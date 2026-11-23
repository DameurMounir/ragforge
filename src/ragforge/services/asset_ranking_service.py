import hashlib

from bson import ObjectId

from src.ragforge.models.enums.asset_status import AssetStatus
from src.ragforge.schemas.search import SemanticSearchRequest
from src.ragforge.services.passage_ranking import Passage, ScopedPassageIndex
from src.ragforge.services.semantic_search_service import SemanticSearchService


def _error(status: int, message: str):
    return status, {'signal': 'asset_ranking_failed', 'message': message}


async def rank_asset_revision(project_id: str, request: SemanticSearchRequest, *, settings,
                              project_store, asset_store, chunk_store):
    """Use one explicitly scoped, processed revision. Never broaden incomplete reads."""
    limit = request.limit or settings.SEARCH_DEFAULT_LIMIT
    if limit > settings.SEARCH_MAX_LIMIT:
        return _error(400, 'Result limit exceeds server policy.')
    project = await project_store.get_project_by_project_id(project_id=project_id)
    if project is None or project.id is None or not ObjectId.is_valid(request.asset_id):
        return _error(404, 'Asset not found in the requested project.')
    asset = await asset_store.get_asset_by_id(request.asset_id)
    if asset is None or asset.asset_project_id != project.id:
        return _error(404, 'Asset not found in the requested project.')
    if asset.asset_status not in (AssetStatus.PROCESSED, AssetStatus.INDEXED):
        return _error(409, 'Asset is not ready for ranked retrieval.')
    if asset.asset_metadata.get('source_revision') != request.source_revision:
        return _error(409, 'Requested revision is not bound to the current asset.')
    if asset.chunk_count > request.max_corpus_chunks:
        return _error(413, 'Full asset exceeds the requested passage budget.')

    chunks = {}
    characters = 0
    async for chunk in chunk_store.indexed_revision_chunks(
        project.id, asset.id, request.source_revision, request.max_corpus_chunks + 1
    ):
        characters += len(chunk.chunk_text)
        if characters > request.max_corpus_characters or len(chunks) >= request.max_corpus_chunks:
            return _error(413, 'Full asset exceeds the requested corpus budget.')
        metadata = chunk.chunk_metadata
        if (
            chunk.id is None or not chunk.embedded or chunk.chunk_project_id != project.id
            or chunk.chunk_asset_id != asset.id or metadata.get('source_revision') != request.source_revision
        ):
            return _error(409, 'Indexed passage does not match the requested asset revision.')
        start, end, page = (metadata.get(k) for k in ('char_start', 'char_end', 'page_number'))
        if (
            type(start) is not int or type(end) is not int or type(page) is not int
            or min(start, page - 1) < 0 or end - start != len(chunk.chunk_text)
            or metadata.get('passage_sha256') != hashlib.sha256(chunk.chunk_text.encode()).hexdigest()
            or chunk.vector_id != str(chunk.id)
        ):
            return _error(409, 'Indexed passage provenance is incomplete.')
        chunks[str(chunk.id)] = chunk
    if not chunks or len(chunks) != asset.chunk_count:
        return _error(409, 'Pinned revision is incomplete. Process and index the full asset.')

    index = ScopedPassageIndex(
        Passage(passage_id, str(asset.id), chunk.chunk_text) for passage_id, chunk in chunks.items()
    )
    model = 'not-applicable'
    method = request.ranking_method
    if method == 'rrf':
        filters = {
            'project_id': str(project.id), 'asset_id': str(asset.id),
            'source_revision': request.source_revision,
        }
        model, vectors = await SemanticSearchService(settings).dense_candidates(
            request.query, filters=filters, limit=len(chunks), strict_space=True,
        )
        hits = index.hybrid(request.query, (str(v.record_id) for v in vectors), limit=limit)
    else:
        hits = index.lexical(request.query, limit=limit)

    # Reprocessing and failure both change this owner record. Check again after
    # ranking I/O so a withdrawn or changing asset cannot produce a response.
    current = await asset_store.get_asset_by_id(request.asset_id)
    if (current is None or current.asset_project_id != asset.asset_project_id
            or current.updated_at != asset.updated_at or current.asset_status != asset.asset_status
            or current.chunk_count != asset.chunk_count or current.asset_metadata != asset.asset_metadata):
        return _error(409, 'Asset changed during ranking. Acquire its current revision.')
    include_text = settings.SEARCH_INCLUDE_TEXT_DEFAULT if request.include_text is None else request.include_text
    include_metadata = settings.SEARCH_INCLUDE_METADATA_DEFAULT if request.include_metadata is None else request.include_metadata
    results = []
    for rank, hit in enumerate(hits, 1):
        chunk = chunks[hit.passage.passage_id]
        metadata = {}
        if include_metadata:
            metadata = {
                'source_revision': request.source_revision,
                'page_number': chunk.chunk_metadata['page_number'],
                'char_start': chunk.chunk_metadata['char_start'],
                'char_end': chunk.chunk_metadata['char_end'],
                'passage_sha256': chunk.chunk_metadata['passage_sha256'],
                'ranking_method': method, 'raw_rank_score': hit.score,
                'lexical_rank': hit.lexical_rank, 'dense_rank': hit.dense_rank,
            }
        results.append({
            'rank': rank, 'score': hit.score / (1 + hit.score) if method == 'bm25' else hit.score,
            'record_id': str(chunk.id), 'chunk_id': str(chunk.id), 'asset_id': str(asset.id),
            'project_id': str(project.id), 'chunk_order': chunk.chunk_order,
            'text': chunk.chunk_text if include_text else None, 'metadata': metadata,
        })
    score_kind = 'BM25/(1+BM25)' if method == 'bm25' else 'reciprocal rank fusion (k=60)'
    return 200, {
        'signal': f'asset_{method}_ranked',
        'message': f'Ranked one pinned document. Score is {score_kind}.',
        'project_id': project_id, 'query': request.query,
        'collection_name': settings.VECTOR_DB_COLLECTION_NAME, 'embedding_model': model,
        'total_results': len(results), 'results': results,
    }
