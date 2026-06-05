from src.ragforge.services.retrieval_postprocessor import (
    RetrievalPostprocessingConfig,
    RetrievalPostprocessor,
)


def make_item(record_id, asset_id, score, text='evidence', chunk_order=1):
    return {
        'rank': 1,
        'score': score,
        'record_id': record_id,
        'chunk_id': record_id,
        'asset_id': asset_id,
        'project_id': 'project-1',
        'chunk_order': chunk_order,
        'text': text,
        'metadata': {
            'asset_id': asset_id,
            'chunk_id': record_id,
            'chunk_order': chunk_order,
            'source': f'{asset_id}.pdf',
        },
    }


def test_postprocessor_filters_weak_scores_and_limits_final_results():
    processor = RetrievalPostprocessor()

    result = processor.process(
        evidence_results=[
            make_item('c1', 'asset-a', 0.72),
            make_item('c2', 'asset-a', 0.52, chunk_order=2),
            make_item('c3', 'asset-b', 0.18),
        ],
        config=RetrievalPostprocessingConfig(
            final_limit=5,
            min_score=0.25,
            max_chunks_per_asset=3,
            enable_source_dedup=True,
            enable_dominant_asset=False,
            dominant_asset_score_gap=0.08,
            dominant_asset_min_chunks=2,
        ),
    )

    assert len(result['results']) == 2
    assert result['diagnostics']['removed_below_min_score'] == 1
    assert all(item['score'] >= 0.25 for item in result['results'])


def test_postprocessor_prefers_dominant_asset_when_clear():
    processor = RetrievalPostprocessor()

    result = processor.process(
        evidence_results=[
            make_item('a1', 'asset-td', 0.62),
            make_item('a2', 'asset-td', 0.55, chunk_order=2),
            make_item('b1', 'asset-other', 0.41),
        ],
        config=RetrievalPostprocessingConfig(
            final_limit=5,
            min_score=0.20,
            max_chunks_per_asset=3,
            enable_source_dedup=True,
            enable_dominant_asset=True,
            dominant_asset_score_gap=0.08,
            dominant_asset_min_chunks=2,
        ),
    )

    assert result['diagnostics']['dominant_asset_applied'] is True
    assert result['diagnostics']['dominant_asset_id'] == 'asset-td'
    assert {item['asset_id'] for item in result['results']} == {'asset-td'}


def test_postprocessor_preserves_multi_document_context_when_no_clear_winner():
    processor = RetrievalPostprocessor()

    result = processor.process(
        evidence_results=[
            make_item('a1', 'asset-a', 0.62),
            make_item('b1', 'asset-b', 0.59),
            make_item('a2', 'asset-a', 0.55, chunk_order=2),
        ],
        config=RetrievalPostprocessingConfig(
            final_limit=5,
            min_score=0.20,
            max_chunks_per_asset=3,
            enable_source_dedup=True,
            enable_dominant_asset=True,
            dominant_asset_score_gap=0.08,
            dominant_asset_min_chunks=2,
        ),
    )

    assert result['diagnostics']['dominant_asset_applied'] is False
    assert {item['asset_id'] for item in result['results']} == {'asset-a', 'asset-b'}
