import json
import os
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = os.getenv('RAGFORGE_BASE_URL', 'http://127.0.0.1:8000')
PROJECT_ID = os.getenv('RAGFORGE_VALIDATION_PROJECT_ID', 'project_postman_reliability')
EXPECT_REAL_OPENAI = os.getenv('RAGFORGE_EXPECT_REAL_OPENAI', 'true').lower() == 'true'


SOURCE_NUMBER_PATTERN = re.compile(r'\[Sources?\s+([^\]]+)\]')
NUMBER_PATTERN = re.compile(r'\d+')


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        url=url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with urlopen(request, timeout=120) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            return status_code, json.loads(body)
    except HTTPError as error:
        body = error.read().decode('utf-8')
        return error.code, json.loads(body)


def cited_numbers(answer: str) -> set[int]:
    numbers: set[int] = set()

    for match in SOURCE_NUMBER_PATTERN.finditer(answer or ''):
        for number_text in NUMBER_PATTERN.findall(match.group(1)):
            numbers.add(int(number_text))

    return numbers


def assert_no_invalid_citations(payload: dict) -> None:
    valid_numbers = {
        int(source['source_number'])
        for source in payload.get('sources', [])
    }
    answer_numbers = cited_numbers(payload.get('answer') or '')
    invalid = answer_numbers - valid_numbers

    assert not invalid, f'Invalid source citations found: {invalid}'


def validate_answer(payload: dict) -> None:
    assert payload['signal'] in {
        'rag_answer_success',
        'rag_answer_no_context',
    }

    if payload['signal'] == 'rag_answer_success':
        assert payload['answer']
        assert payload['retrieval_count'] > 0
        assert 'sources' in payload
        assert 'evidence' in payload
        assert 'retrieval_diagnostics' in payload
        assert 'citation_validation' in payload
        assert_no_invalid_citations(payload)

        if EXPECT_REAL_OPENAI:
            assert payload['llm_model'] != 'fake-ragforge-model'


def run_case(name: str, question: str) -> dict:
    status_code, payload = post_json(
        url=f'{BASE_URL}/api/v1/answers/{PROJECT_ID}',
        payload={
            'question': question,
            'limit': 5,
            'asset_id': None,
            'min_score': None,
            'include_sources': True,
            'include_evidence': True,
            'include_debug_prompt': False,
        },
    )

    print('\n===', name, '===')
    print('Status code:', status_code)
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    assert status_code == 200
    validate_answer(payload)
    return payload


def main() -> None:
    """
    Validate Branch 19 RAG Core stability through the running FastAPI API.

    Prerequisites:
    - MongoDB and Qdrant are running.
    - FastAPI is running on BASE_URL.
    - PROJECT_ID exists.
    - The project has uploaded, processed, and indexed chunks.
    - For production-oriented validation, .env uses real OpenAI-compatible
      LLM and real OpenAI-compatible embeddings.
    """

    run_case(
        name='numeric separation',
        question='What is the preferred chunk size in Scenario B?',
    )

    run_case(
        name='negative evidence',
        question='What is the salary of the Atlas Scholar director?',
    )

    run_case(
        name='database role separation',
        question='Does MongoDB replace Qdrant?',
    )

    print('\nBranch 19 RAG Core stability validation passed')


if __name__ == '__main__':
    main()
