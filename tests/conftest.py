"""Pytest bootstrap for deterministic Settings creation.

Production settings stay strict.
Tests define safe placeholder defaults so CI does not depend on a local .env file.
"""

from __future__ import annotations

import os


_TEST_ENV_DEFAULTS = {
    "APP_NAME": "RAGForge",
    "APP_VERSION": "0.1.0",
    "APP_ENV": "test",
    "MONGO_INITDB_ROOT_USERNAME": "ragforge",
    "MONGO_INITDB_ROOT_PASSWORD": "ragforge_password_change_me",
    "MONGODB_DATABASE": "ragforge_test",
    "MONGODB_URL": "mongodb://ragforge:ragforge_password_change_me@localhost:27017/ragforge_test?authSource=admin",
    "EMBEDDING_VECTOR_SIZE": "1536",
}


for key, value in _TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(key, value)
