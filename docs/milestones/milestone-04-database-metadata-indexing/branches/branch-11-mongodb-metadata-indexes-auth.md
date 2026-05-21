# Branch 11 — MongoDB Metadata Indexes & Auth

## 🎯 Objective

Add MongoDB metadata indexes and authenticated MongoDB access for the RAGForge asset metadata layer.

This branch defines and initializes indexes for projects, assets, and data chunks. It also improves the local MongoDB setup by adding Docker Compose authentication through environment variables.

The goal is to make the MongoDB metadata layer indexed, authenticated, and ready before upload and processing endpoints start writing metadata records automatically.

---

## 🧭 Implementation Context

Branch 10 introduced the asset metadata schemes and MongoDB store classes.

Branch 11 builds on that layer by adding:

- index definitions
- index initialization logic
- authenticated MongoDB connection support
- Docker Compose MongoDB credentials
- MongoDB environment examples

This branch keeps the architecture focused on database readiness.

Endpoint-level metadata persistence is intentionally reserved for Branch 12.

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

## 🔐 MongoDB Authentication

This branch adds MongoDB authentication at the database infrastructure level.

This means:

```text
MongoDB now requires username/password access.
```

This does **not** mean application user authentication.

Out of scope:

```text
user login
JWT
API authentication
role-based access control
```

Those belong to a future authentication/security milestone.

---

## 🧱 Scope

This branch includes:

- Add project index definitions
- Add asset index definitions
- Add data chunk index definitions
- Add collection initialization methods to MongoDB stores
- Add `create_instance()` helpers to MongoDB stores
- Add MongoDB authentication through Docker Compose environment variables
- Add Docker MongoDB credential placeholders to `docker/.env.example`
- Update root `.env.example` with authenticated MongoDB connection values
- Update application settings for MongoDB auth values
- Use authenticated MongoDB connection string
- Validate MongoDB indexes manually
- Validate authenticated MongoDB connection
- Update Milestone 4 documentation
- Update README current focus

---

## 📁 Expected Files

```text
docker/docker-compose.yml
docker/.env.example
.env.example
.gitignore

src/ragforge/core/config.py

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

## 🧩 Docker Compose Authentication

MongoDB should be configured using Docker Compose environment variables:

```yaml
environment:
  MONGO_INITDB_ROOT_USERNAME: ${MONGO_INITDB_ROOT_USERNAME}
  MONGO_INITDB_ROOT_PASSWORD: ${MONGO_INITDB_ROOT_PASSWORD}
```

The local Docker environment file should define:

```env
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=admin

MONGODB_DATABASE=ragforge
MONGODB_URL=mongodb://admin:admin@localhost:27007/ragforge?authSource=admin
```

The connection string must include:

```text
authSource=admin
```

because MongoDB root users are created inside the `admin` authentication database.

---

## 🧩 Environment Files

Private environment files must not be committed:

```text
.env
docker/.env
```

Example files should be committed:

```text
.env.example
docker/.env.example
```

Expected root `.env.example` MongoDB section:

```env
MONGO_INITDB_ROOT_USERNAME=
MONGO_INITDB_ROOT_PASSWORD=

MONGODB_DATABASE=ragforge
MONGODB_URL=mongodb://USERNAME:PASSWORD@localhost:27007/ragforge?authSource=admin
```

Expected `docker/.env.example`:

```env
MONGO_INITDB_ROOT_USERNAME=
MONGO_INITDB_ROOT_PASSWORD=

MONGODB_DATABASE=ragforge
MONGODB_URL=mongodb://USERNAME:PASSWORD@localhost:27007/ragforge?authSource=admin
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

The validation confirmed:

```text
MongoDB authenticated connection OK.
MongoDB metadata indexes initialized successfully.
```

The validation also confirmed that MongoDB created the expected custom metadata indexes for:

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
python -c "from src.ragforge.core.config import get_settings; s=get_settings(); print(s.MONGODB_URL)"
```

Expected MongoDB URL:

```text
mongodb://admin:admin@localhost:27007/ragforge?authSource=admin
```

Run tests:

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
- application user authentication
- JWT authentication
- role-based access control

Endpoint integration is intentionally reserved for Branch 12.

---

## ✅ Definition of Done

This branch is complete when:

- MongoDB authentication is configured in Docker Compose
- MongoDB credentials are read from environment variables
- private `.env` files are ignored by Git
- example environment files are committed
- authenticated MongoDB connection works
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
