from __future__ import annotations

"""
Validate that Alembic can read the PostgreSQL migration environment.

Run after installing dependencies and starting PostgreSQL:

    python scripts/validation/validate_branch_20_alembic_state.py
"""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_command(command: list[str]) -> None:
    print(f'Running: {" ".join(command)}')
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    run_command(['alembic', '-c', 'alembic.ini', 'current'])
    run_command(['alembic', '-c', 'alembic.ini', 'history'])
    print('Branch 20 Alembic state validation passed.')


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f'Alembic validation failed with exit code {exc.returncode}.')
        sys.exit(exc.returncode)
