from src.ragforge.services.rag_context_builder import RAGContextBuilder


def test_context_builder_creates_source_numbered_context():
    builder = RAGContextBuilder()

    result = builder.build_context(
        evidence_results=[
            {
                'rank': 1,
                'score': 0.91,
                'record_id': 'record-1',
                'chunk_id': 'chunk-1',
                'asset_id': 'asset-1',
                'project_id': 'project-1',
                'chunk_order': 3,
                'text': 'This is relevant evidence.',
                'metadata': {'file_name': 'demo.txt'},
            }
        ],
        max_context_chars=1000,
    )

    assert '[Source 1]' in result['context']
    assert 'This is relevant evidence.' in result['context']
    assert len(result['sources']) == 1
    assert result['sources'][0].source_number == 1
    assert len(result['evidence']) == 1


def test_context_builder_skips_empty_text():
    builder = RAGContextBuilder()

    result = builder.build_context(
        evidence_results=[
            {
                'rank': 1,
                'score': 0.91,
                'record_id': 'record-1',
                'text': '   ',
                'metadata': {},
            }
        ],
        max_context_chars=1000,
    )

    assert result['context'] == ''
    assert result['sources'] == []
    assert result['evidence'] == []


def test_context_builder_respects_max_context_chars():
    builder = RAGContextBuilder()

    result = builder.build_context(
        evidence_results=[
            {
                'rank': 1,
                'score': 0.91,
                'record_id': 'record-1',
                'chunk_id': 'chunk-1',
                'asset_id': 'asset-1',
                'project_id': 'project-1',
                'chunk_order': 1,
                'text': 'A' * 1000,
                'metadata': {},
            }
        ],
        max_context_chars=200,
    )

    assert len(result['context']) <= 220
    assert len(result['sources']) == 1
