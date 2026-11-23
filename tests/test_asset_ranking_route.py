import hashlib
import os
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.models.db_schemes import Asset, DataChunk
from src.ragforge.models.enums.asset_status import AssetStatus
from src.ragforge.routes import search
from src.ragforge.services.semantic_search_service import SemanticSearchService


@pytest.fixture
def ranked_api(tmp_path, monkeypatch):
    secret = 'q' * 48
    path = tmp_path / 'token'
    path.write_text(secret)
    path.chmod(0o400)
    settings = Settings(SERVICE_AUTH_ENABLED=True, SERVICE_AUTH_TOKEN_FILE=str(path),
                        SERVICE_AUTH_TOKEN_EXPECTED_OWNER_UID=os.getuid(), SEARCH_MIN_SCORE=0.99)
    monkeypatch.setattr(search, 'get_settings', lambda: settings)
    project, asset_id = ObjectId(), ObjectId()
    revision = hashlib.sha256(b'original').hexdigest()
    asset = Asset(_id=asset_id, asset_project_id=project, asset_name='policy',
                  asset_status=AssetStatus.PROCESSED, chunk_count=2, updated_at=datetime.now(timezone.utc),
                  asset_metadata={'source_revision': revision})
    original, other = 'REF-RH-07 allocation', 'Calculez le plafond.'
    chunks = []
    for order, text in enumerate((original, other), start=1):
        chunk_id = ObjectId()
        chunks.append(DataChunk(_id=chunk_id, chunk_project_id=project, chunk_asset_id=asset_id,
                               chunk_text=text, chunk_order=order, embedded=True, vector_id=str(chunk_id),
                               chunk_metadata={'source_revision': revision, 'page_number': order,
                                               'char_start': 0, 'char_end': len(text),
                                               'passage_sha256': hashlib.sha256(text.encode()).hexdigest()}))

    async def rows(project_key, asset_key, pinned, cap):
        assert (project_key, asset_key, pinned) == (project, asset_id, revision)
        for item in chunks[:cap]:
            yield item

    assets = SimpleNamespace(get_asset_by_id=AsyncMock(return_value=asset))
    projects = SimpleNamespace(get_project_by_project_id=AsyncMock(return_value=SimpleNamespace(id=project)))
    monkeypatch.setattr(search.ProjectStore, 'create_instance', AsyncMock(return_value=projects))
    monkeypatch.setattr(search, 'AssetStore', lambda **_: assets)
    monkeypatch.setattr(search, 'ChunkStore', lambda **_: SimpleNamespace(indexed_revision_chunks=rows))
    app = FastAPI()
    app.include_router(search.search_router)
    app.db_client = object()
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)
    body = dict(query='REF-RH-07', ranking_method='bm25', source_revision=revision,
                asset_id=str(asset_id), max_corpus_chunks=2, max_corpus_characters=100, limit=2)

    def post(body, auth=True):
        headers = {'Authorization': 'Bearer ' + secret} if auth else {}
        return client.post('/api/v1/search/client', json=body, headers=headers)

    return post, body, asset, chunks, assets


def test_bm25_through_protected_http_route(ranked_api):
    post, body, _, chunks, _ = ranked_api
    assert post(body, auth=False).status_code == 401
    response = post(body)
    assert response.status_code == 200, response.text
    data = response.json()
    hit, = data['results']
    assert data['signal'] == 'asset_bm25_ranked'
    assert hit['chunk_id'] == str(chunks[0].id)
    raw = hit['metadata']['raw_rank_score']
    assert hit['score'] == pytest.approx(raw / (1 + raw))
    redacted, = post(dict(body, include_text=False, include_metadata=False)).json()['results']
    assert redacted['metadata'] == {} and redacted['text'] is None


def test_rrf_adds_full_corpus_lexical_hits_and_excludes_out_of_scope_dense_ids(ranked_api, monkeypatch):
    post, body, asset, chunks, _ = ranked_api
    dense = AsyncMock(return_value=('test-model', [SimpleNamespace(record_id=ObjectId()),
                                                   SimpleNamespace(record_id=chunks[1].id)]))
    monkeypatch.setattr(SemanticSearchService, 'dense_candidates', dense)
    data = post(dict(body, ranking_method='rrf')).json()
    assert data['signal'] == 'asset_rrf_ranked'
    assert {row['chunk_id'] for row in data['results']} == {str(c.id) for c in chunks}
    assert all(row['score'] == pytest.approx(1 / 61) for row in data['results'])
    assert dense.await_args.kwargs == {'limit': 2, 'strict_space': True, 'filters': {
        'project_id': str(asset.asset_project_id), 'asset_id': str(asset.id),
        'source_revision': body['source_revision'],
    }}


def test_ranked_http_rejects_missing_scope_stale_revision_and_over_budget(ranked_api):
    post, body, asset, chunks, _ = ranked_api
    for key in ('asset_id', 'source_revision', 'max_corpus_chunks', 'max_corpus_characters'):
        assert post({k: v for k, v in body.items() if k != key}).status_code == 422
    assert post(dict(body, min_score=0.2)).status_code == 422
    assert post(dict(body, source_revision='0' * 64)).status_code == 409
    assert post(dict(body, max_corpus_chunks=1)).status_code == 413
    assert post(dict(body, max_corpus_characters=10)).status_code == 413
    chunks.pop()
    assert post(body).status_code == 409
    asset.asset_project_id = ObjectId()
    assert post(body).status_code == 404


def test_corrupt_or_withdrawn_asset_emits_no_passages(ranked_api):
    post, body, asset, chunks, assets = ranked_api
    assets.get_asset_by_id.side_effect = [asset, None]
    response = post(body)
    assert response.status_code == 409 and 'results' not in response.json()
    assets.get_asset_by_id.side_effect = None
    chunks[0].chunk_metadata['passage_sha256'] = '0' * 64
    assert post(body).status_code == 409


def test_matching_old_chunks_cannot_establish_missing_owner_revision(ranked_api):
    post, body, asset, chunks, _ = ranked_api
    assert all(c.chunk_metadata['source_revision'] == body['source_revision'] for c in chunks)
    asset.asset_metadata.pop('source_revision')
    for method in ('bm25', 'rrf'):
        result = post(dict(body, ranking_method=method))
        assert result.status_code == 409
        assert 'results' not in result.json()
