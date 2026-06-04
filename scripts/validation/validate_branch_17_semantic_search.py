import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = 'http://127.0.0.1:8000'
PROJECT_ID = 'project16test'


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    """
    Minimal JSON POST helper.

    urllib is used to avoid adding a new dependency just for validation.
    """
    request = Request(
        url=url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with urlopen(request, timeout=30) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            return status_code, json.loads(body)
    except HTTPError as error:
        body = error.read().decode('utf-8')
        return error.code, json.loads(body)


def main() -> None:
    """
    Validate Branch 17 semantic search through the running FastAPI API.

    Prerequisites:
    - MongoDB and Qdrant are running.
    - FastAPI is running on http://127.0.0.1:8000.
    - The project `project16test` exists.
    - The project has already been uploaded, processed, and indexed
      through Branch 16.
    """

    status_code, payload = post_json(
        url=f'{BASE_URL}/api/v1/search/{PROJECT_ID}',
        payload={
            'query': 'indexing pipeline fake embedding Qdrant',
            'limit': 5,
            'asset_id': None,
            'min_score': None,
            'include_text': True,
            'include_metadata': True,
        },
    )

    print('Status code:', status_code)
    print(payload)

    assert status_code == 200
    assert payload['signal'] in {
        'semantic_search_success',
        'semantic_search_no_results',
    }

    if payload['signal'] == 'semantic_search_success':
        assert payload['total_results'] > 0
        assert payload['results']
        first_result = payload['results'][0]
        assert 'rank' in first_result
        assert 'score' in first_result
        assert 'record_id' in first_result
        assert 'text' in first_result
        assert 'metadata' in first_result

    print('Branch 17 semantic search validation passed')


if __name__ == '__main__':
    main()
