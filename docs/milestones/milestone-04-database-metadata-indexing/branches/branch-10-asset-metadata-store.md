# Branch 10 — Asset Metadata Schemes & Stores

## 🎯 Objective

Introduce the asset metadata scheme and MongoDB store layer for RAGForge.

This branch defines the database document shapes and store classes required to manage projects, assets, and data chunks.

An asset represents any knowledge source that can later be processed into chunks, such as files, URLs, images, videos, audio files, web pages, or transcripts.

---

## 🧭 Implementation Context

Branch 9 introduced MongoDB infrastructure.

Branch 10 builds on that foundation by adding the first metadata storage layer.

This branch follows the existing RAGForge structure:

```text
models/db_schemes → database document shapes
stores/mongodb    → MongoDB operations
```

The goal is not to implement semantic search yet.

The goal is to prepare the database layer that semantic search and augmented generation will later depend on.

This branch also adds basic local validation support for the new metadata layer by updating Python requirements, configuring pytest collection, and excluding MongoDB runtime data from Git and test discovery.

---

## 🧱 Core Data Relationship

The core relationship introduced in this branch is:

```text
Project
  ↓
Asset
  ↓
DataChunk
```

Where:

```text
Project   = logical workspace
Asset     = knowledge source attached to a project
DataChunk = text unit extracted from an asset
```

This keeps RAGForge flexible because an asset can later represent:

```text
file
URL
image
video
audio
web page
transcript
API source
```

---

## 🧱 Scope

This branch includes:

- Add asset type enum
- Add asset status enum
- Keep/update project database scheme
- Add asset database scheme
- Update data chunk database scheme
- Add MongoDB collection enum
- Add base MongoDB store
- Add project store
- Add asset store
- Add chunk store
- Add pytest configuration
- Update requirements for MongoDB and test dependencies
- Update `.gitignore` to exclude MongoDB runtime data
- Update README current focus and knowledge-oriented RAG direction
- Update backend architecture documentation

---

## 📁 Expected Files

```text
src/ragforge/models/enums/asset_type.py
src/ragforge/models/enums/asset_status.py

src/ragforge/models/db_schemes/project.py
src/ragforge/models/db_schemes/asset.py
src/ragforge/models/db_schemes/data_chunk.py
src/ragforge/models/db_schemes/__init__.py

src/ragforge/stores/mongodb/collections.py
src/ragforge/stores/mongodb/base_store.py
src/ragforge/stores/mongodb/project_store.py
src/ragforge/stores/mongodb/asset_store.py
src/ragforge/stores/mongodb/chunk_store.py
src/ragforge/stores/mongodb/__init__.py

pytest.ini
requirements.txt
.gitignore
README.md
docs/architecture/backend-architecture.md
docs/milestones/milestone-04-database-metadata-indexing/milestone-04-database-metadata-indexing.md
docs/milestones/milestone-04-database-metadata-indexing/branches/branch-10-asset-metadata-store.md
```

---

## 🧩 Asset Type Enum

The asset type enum defines supported knowledge source types.

Initial supported values:

```text
file
url
image
video
audio
web_page
```

Only file assets are expected to be used immediately.

Other values prepare the architecture for future ingestion sources.

---

## 🧩 Asset Status Enum

The asset status enum defines the lifecycle of an asset.

Expected values:

```text
uploaded
registered
processing
processed
failed
indexed
```

Meaning:

```text
uploaded    → local file uploaded
registered  → external source registered
processing  → extraction or chunking started
processed   → content was processed successfully
failed      → processing failed
indexed     → vector indexing completed later
```

---

## 🧩 Project Scheme

The project scheme represents a logical workspace.

Expected fields:

```text
_id
project_id
```

The project scheme should remain simple in this branch.

---

## 🧩 Asset Scheme

The asset scheme represents any knowledge source attached to a project.

Expected fields include:

```text
_id
asset_project_id
asset_type
asset_status
asset_name
source_uri
file_name
file_extension
mime_type
asset_size
storage_path
chunk_count
extraction_method
extraction_error
asset_config
asset_metadata
asset_pushed_at
updated_at
```

This gives RAGForge a flexible asset model that can support files now and other knowledge sources later.

---

## 🧩 Data Chunk Scheme

The data chunk scheme represents text extracted from an asset.

Expected fields include:

```text
_id
chunk_text
chunk_metadata
chunk_order
chunk_project_id
chunk_asset_id
embedded
embedding_model
vector_id
```

The fields `embedded`, `embedding_model`, and `vector_id` prepare the system for future semantic search without implementing embeddings in this branch.

---

## 🧩 MongoDB Stores

This branch introduces store classes for MongoDB operations.

Expected stores:

```text
BaseMongoStore
ProjectStore
AssetStore
ChunkStore
```

Store classes should contain database operations only.

They should not contain route logic.

They should not contain upload workflow logic.

---

## 🧭 Store Responsibilities

### BaseMongoStore

Responsible for shared MongoDB store setup.

Expected responsibility:

```text
hold db_client
load application settings
provide common base for MongoDB stores
```

### ProjectStore

Responsible for project records.

Expected methods:

```text
create_project
get_project_by_id
get_project_or_create_one
get_all_projects
```

### AssetStore

Responsible for asset records.

Expected methods:

```text
create_asset
get_asset_by_id
get_project_assets
get_asset_record
```

### ChunkStore

Responsible for data chunk records.

Expected methods:

```text
create_chunk
get_chunk
insert_many_chunks
get_asset_chunks
delete_chunks_by_project_id
delete_chunks_by_asset_id
```

---

## 🧪 Validation and Local Testing

This branch adds `pytest.ini` so pytest only collects tests from the `tests/` folder and does not scan runtime folders such as Docker volume data.

Expected `pytest.ini` behavior:

```text
testpaths = tests
norecursedirs = .git, .venv, venv, __pycache__, docker, storage, resources
```

This prevents pytest from trying to read MongoDB runtime files such as local database journal or diagnostic files.

This branch also updates `requirements.txt` to include the dependencies required by the new metadata layer and validation workflow.

Important dependencies include:

```text
motor
pymongo
pydantic-mongo
pytest
```

`pymongo` is required because it provides the `bson` package used by `ObjectId`.

---

## ✅ Validation Commands

The following commands should work before committing the branch:

```bash
python -c "from bson.objectid import ObjectId; print('bson ok')"
```

```bash
python -c "from src.ragforge.models.db_schemes import Project, Asset, DataChunk; print('db schemes ok')"
```

```bash
python -c "from src.ragforge.stores.mongodb import ProjectStore, AssetStore, ChunkStore; print('stores ok')"
```

```bash
python -m pytest
```

If there are no test files yet, pytest may return:

```text
collected 0 items
no tests ran
```

That is acceptable for this branch as long as pytest runs successfully and does not fail during collection.

---

## 🚫 Out of Scope

This branch does not include:

- MongoDB index initialization
- upload endpoint metadata persistence
- processing endpoint metadata persistence
- embedding generation
- vector database integration
- semantic search
- augmented answer generation
- citation-aware responses

MongoDB indexing is intentionally kept for Branch 11.

---

## ✅ Definition of Done

This branch is complete when:

- asset type enum is added
- asset status enum is added
- project database scheme is available
- asset database scheme is added
- data chunk scheme supports project and asset relations
- MongoDB collection enum is added
- base MongoDB store is added
- project store is implemented
- asset store is implemented
- chunk store is implemented
- store classes are independent from route logic
- requirements include MongoDB and test dependencies
- `.gitignore` excludes MongoDB runtime data
- `pytest.ini` limits test discovery to project tests
- import validation commands pass
- pytest runs without collection errors
- no MongoDB index initialization is added in this branch
- branch documentation is updated

---

## 🔜 Next Branch

The next branch is:

```text
Branch 11 — MongoDB Metadata Indexes
```

Expected next work:

```text
Add  MongoDB index definitions and index initialization for projects, assets, and chunks.
```

Branch 11 will prepare the metadata layer for efficient querying before upload and processing endpoints start writing metadata records.

