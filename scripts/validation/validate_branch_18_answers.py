import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = 'http://127.0.0.1:8000'
PROJECT_ID = 'project18test'


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        url=url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with urlopen(request, timeout=60) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            return status_code, json.loads(body)
    except HTTPError as error:
        body = error.read().decode('utf-8')
        return error.code, json.loads(body)


def main() -> None:
    """
    Validate Branch 18 answer generation through the running FastAPI API.

    Prerequisites:
    - MongoDB and Qdrant are running.
    - FastAPI is running on http://127.0.0.1:8000.
    - PROJECT_ID exists.
    - The project has uploaded, processed, and indexed chunks.
    """

    status_code, payload = post_json(
        url=f'{BASE_URL}/api/v1/answers/{PROJECT_ID}',
        payload={
            'question': 'What does this project say about RAGForge indexing?',
            'limit': 5,
            'asset_id': None,
            'min_score': None,
            'include_sources': True,
            'include_evidence': True,
            'include_debug_prompt': False,
        },
    )

    print('Status code:', status_code)
    print(payload)

    assert status_code == 200
    assert payload['signal'] in {
        'rag_answer_success',
        'rag_answer_no_context',
    }

    if payload['signal'] == 'rag_answer_success':
        assert payload['answer']
        assert payload['retrieval_count'] > 0
        assert 'sources' in payload
        assert 'evidence' in payload
        assert payload['llm_model']

    print('Branch 18 answer validation passed')


if __name__ == '__main__':
    main()
