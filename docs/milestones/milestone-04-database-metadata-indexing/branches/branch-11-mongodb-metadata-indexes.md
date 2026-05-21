# Branch 11 — MongoDB Metadata Indexes

## 🎯 Objective

Add MongoDB metadata indexes for the RAGForge asset metadata layer.

This branch defines and initializes indexes for projects, assets, and data chunks to prepare the database layer for efficient metadata querying before upload and processing endpoints start writing metadata records automatically.

---

## 🧭 Implementation Context

Branch 10 introduced the asset metadata schemes and MongoDB store classes.

Branch 11 builds on that layer by adding index definitions and index initialization logic.

The goal is to make metadata queries efficient, predictable, and ready for larger datasets before endpoint-level persistence is introduced.

This branch keeps the architecture focused on the database metadata layer only.

---

## 🧱 Core Indexed Relationship

The indexed metadata relationship is:

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
DataChunk = extracted text unit linked to both project and asset
```

Indexes are added to support fast access patterns such as:

```text
find project by project_id
list assets by project
find asset by project and name
filter assets by status or type
list chunks by project
list chunks by asset
reconstruct chunks in original order
track embedding/vector indexing state
```

---

## 🧱 Scope

This branch includes:

- Add project index definitions
- Add asset index definitions
- Add data chunk index definitions
- Add collection initialization methods to MongoDB stores
- Add `create_instance()` helpers to MongoDB stores
- Validate MongoDB indexes manually
- Update Milestone 4 documentation
- Update README current focus

---

## 📁 Expected Files

```text
src/ragforge/models/db_schemes/project.py
src/ragforge/models/db_schemes/asset.py
src/ragforge/models/db_schemes/data_chunk.py

src/ragforge/stores/mongodb/project_store.py
src/ragforge/stores/mongodb/asset_store.py
src/ragforge/stores/mongodb/chunk_store.py

docs/milestones/milestone-04-database-metadata-indexing/branches/branch-11-mongodb-metadata-indexes.md
docs/milestones/milestone-04-database-metadata-indexing/milestone-04-database-metadata-indexing.md
README.md
```

---

## 🧩 Project Indexes

Expected project indexes:

```text
_id_
project_id_unique_idx
```

Purpose:

```text
Prevent duplicate public project identifiers.
Support fast lookup by project_id.
```

Expected definition:

```text
project_id → unique
```

---

## 🧩 Asset Indexes

Expected asset indexes:

```text
_id_
asset_project_id_idx
asset_project_name_unique_idx
asset_status_idx
asset_type_idx
asset_source_uri_idx
```

Purpose:

```text
Support project asset listing.
Prevent duplicate asset names inside the same project.
Support filtering assets by lifecycle status.
Support filtering assets by source type.
Prepare future lookup of external sources such as URLs.
```

Expected definitions:

```text
asset_project_id → non-unique
asset_project_id + asset_name → unique
asset_status → non-unique
asset_type → non-unique
source_uri → non-unique
```

---

## 🧩 DataChunk Indexes

Expected data chunk indexes:

```text
_id_
chunk_project_id_idx
chunk_asset_id_idx
chunk_project_asset_idx
chunk_project_asset_order_unique_idx
chunk_embedded_idx
chunk_vector_id_idx
```

Purpose:

```text
Support chunk retrieval by project.
Support chunk retrieval by asset.
Support ordered chunk reconstruction.
Prevent duplicate chunk order inside the same asset.
Support future embedding-status filtering.
Support future vector mapping.
```

Expected definitions:

```text
chunk_project_id → non-unique
chunk_asset_id → non-unique
chunk_project_id + chunk_asset_id → non-unique
chunk_project_id + chunk_asset_id + chunk_order → unique
embedded → non-unique
vector_id → non-unique
```

---

## 🧩 Store Initialization

This branch adds collection initialization to MongoDB stores.

Expected store helpers:

```text
ProjectStore.create_instance()
AssetStore.create_instance()
ChunkStore.create_instance()
```

Each helper should:

```text
create the store instance
call init_collection()
return the initialized store
```

Each store should expose:

```text
init_collection()
```

This method creates the indexes defined by the corresponding database scheme.

---

## 🧪 Manual Validation

Manual validation was performed using a temporary local validation script and Studio 3T.

The validation confirmed that MongoDB created the expected custom metadata indexes for:

```text
projects
assets
data_chunks
```

Expected MongoDB structure after validation:

```text
ragforge
├── projects
│   ├── _id_
│   └── project_id_unique_idx
│
├── assets
│   ├── _id_
│   ├── asset_project_id_idx
│   ├── asset_project_name_unique_idx
│   ├── asset_status_idx
│   ├── asset_type_idx
│   └── asset_source_uri_idx
│
└── data_chunks
    ├── _id_
    ├── chunk_project_id_idx
    ├── chunk_asset_id_idx
    ├── chunk_project_asset_idx
    ├── chunk_project_asset_order_unique_idx
    ├── chunk_embedded_idx
    └── chunk_vector_id_idx
```

The temporary validation script is not committed because it was only used for local manual testing.

---

## ✅ Validation Commands

The following commands should work before committing the branch:

```bash
python -c "from src.ragforge.models.db_schemes import Project, Asset, DataChunk; print('db schemes ok')"
```

```bash
python -c "from src.ragforge.stores.mongodb import ProjectStore, AssetStore, ChunkStore; print('stores ok')"
```

```bash
python -m pytest
```

Manual MongoDB validation can also be performed with:

```bash
PYTHONPATH=. python scripts/test_mongodb_indexes.py
```

The temporary script should be removed before commit unless it is intentionally kept as a development utility.

---

## 🚫 Out of Scope

This branch does not include:

- upload endpoint metadata persistence
- processing endpoint metadata persistence
- embedding generation
- vector database integration
- semantic search
- augmented answer generation
- citation-aware responses

Endpoint integration is intentionally reserved for Branch 12.

---

## ✅ Definition of Done

This branch is complete when:

- project index definitions are added
- asset index definitions are added
- data chunk index definitions are added
- project store can initialize indexes
- asset store can initialize indexes
- chunk store can initialize indexes
- `create_instance()` helpers exist for metadata stores
- custom indexes are visible in MongoDB
- import validation commands pass
- pytest runs without collection errors
- no upload/process endpoint persistence is added in this branch
- documentation is updated

---

## 🔜 Next Branch

The next branch is:

```text
Branch 12 — Upload and Processing Metadata Persistence
```

Expected next work:

```text
Connect upload and processing endpoints to the metadata stores.
```

Branch 12 will make the existing upload and processing workflow create and update real MongoDB metadata records automatically.
