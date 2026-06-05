from src.ragforge.services.citation_validator import CitationValidator


def test_citation_validator_detects_invalid_source_number():
    validator = CitationValidator()

    result = validator.validate_and_sanitize(
        answer='MongoDB does not replace Qdrant [Sources 1, 2, 13].',
        valid_source_numbers=[1, 2, 3, 4, 5],
    )

    assert result['invalid_source_numbers'] == [13]
    assert result['was_modified'] is True
    assert '13' not in result['answer']
    assert '[Sources 1, 2]' in result['answer']


def test_citation_validator_removes_fully_invalid_citation():
    validator = CitationValidator()

    result = validator.validate_and_sanitize(
        answer='The answer is unsupported [Source 99].',
        valid_source_numbers=[1, 2],
    )

    assert result['invalid_source_numbers'] == [99]
    assert '[Source 99]' not in result['answer']


def test_citation_validator_keeps_valid_citations():
    validator = CitationValidator()

    result = validator.validate_and_sanitize(
        answer='The chunk size is 900 characters [Source 1].',
        valid_source_numbers=[1, 2],
    )

    assert result['invalid_source_numbers'] == []
    assert result['was_modified'] is False
    assert result['answer'] == 'The chunk size is 900 characters [Source 1].'
