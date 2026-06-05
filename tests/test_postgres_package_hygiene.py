from __future__ import annotations

import subprocess
from pathlib import Path


def test_no_generated_python_cache_files_are_tracked_by_git() -> None:
    """Generated cache artifacts must never be committed.

    This test intentionally checks Git-tracked files, not the live filesystem,
    because `python -m compileall ...` legitimately creates __pycache__
    directories during validation before pytest runs.
    """

    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ['git', 'ls-files'],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked_paths = result.stdout.splitlines()

    forbidden_markers = ('__pycache__', '.pytest_cache')
    forbidden_suffixes = ('.pyc', '.pyo')

    bad_paths = [
        path
        for path in tracked_paths
        if any(marker in path.split('/') for marker in forbidden_markers)
        or path.endswith(forbidden_suffixes)
    ]

    assert not bad_paths, f'Generated cache artifacts must not be tracked: {bad_paths}'
