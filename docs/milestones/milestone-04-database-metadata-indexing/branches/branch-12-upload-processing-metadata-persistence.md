# Branch 12 — Upload and Processing Metadata Persistence

## 🎯 Objective

Connect the upload and processing metadata flow to MongoDB.

This branch makes the metadata stores active by validating that project, asset, and chunk metadata can be persisted, updated, and retrieved through the MongoDB store layer.

The goal is to move RAGForge from a metadata schema/store foundation toward a real metadata-driven ingestion backend.

---

## 🧭 Implementation Context

Previous branches introduced:

```text
Branch 9  → MongoDB infrastructure
Branch 10 → Asset metadata schemes and stores
Branch 11 → MongoDB indexes and authentication
```

Branch 12 builds on that foundation by validating metadata persistence across the core relationship:

```text
Project
  ↓
Asset
  ↓
DataChunk
```

---

## 🧱 Scope

This branch includes:

- Add project metadata persistence validation
- Add asset metadata persistence validation
- Add chunk metadata persistence validation
- Validate project creation and reuse
- Validate asset creation and reuse
- Validate uploaded asset retrieval
- Validate chunk insertion
- Validate chunk retrieval by asset
- Validate asset status update after processing
- Validate asset chunk count update
- Support project identifiers with letters, numbers, underscores, and hyphens
- Add validation utility script
- Add validation script documentation
- Update README current focus
- Update Milestone 4 documentation

---

## 📁 Expected Files

```text
src/ragforge/models/db_schemes/project.py
src/ragforge/stores/mongodb/project_store.py
src/ragforge/stores/mongodb/asset_store.py
src/ragforge/stores/mongodb/chunk_store.py

scripts/validation/test_branch12_metadata_persistence.py
scripts/validation/README.md

docs/milestones/milestone-04-database-metadata-indexing/branches/branch-12-upload-processing-metadata-persistence.md
docs/milestones/milestone-04-database-metadata-indexing/milestone-04-database-metadata-indexing.md
README.md
```

---

## 🧩 Project Identifier Validation

This branch confirms that project identifiers support practical URL-safe names.

Allowed characters:

```text
letters
numbers
underscore _
hyphen -
```

Examples:

```text
project0020
project00_21
project00-21
```

This keeps project identifiers readable and compatible with API paths.

---

## 🧪 Validation Utility

This branch keeps a manual validation script under:

```text
scripts/validation/test_branch12_metadata_persistence.py
```

This script validates:

```text
ProjectStore → AssetStore → ChunkStore
```

It confirms that:

- a project can be created or reused
- an asset can be created or reused
- uploaded assets can be retrieved
- chunks can be inserted
- chunks can be retrieved by asset
- asset processing status can be updated
- asset chunk count can be updated

These scripts are development validation utilities, not production runtime code.

---

## ▶️ Validation Command

Run from the project root:

```bash
PYTHONPATH=. python scripts/validation/test_branch12_metadata_persistence.py
```

Expected result:

```text
Project OK: ...
Asset created: ... or Asset already exists: ...
Uploaded assets found: 1
Chunks inserted: 2
Asset status: AssetStatus.PROCESSED
Asset chunk count: 2
Chunks found for asset: 2
Branch 12 metadata persistence test OK.
```

---

## 🧪 Studio 3T Validation

Manual validation was confirmed in Studio 3T.

Expected MongoDB records:

```text
ragforge
├── projects
│   └── project_id records
│
├── assets
│   └── asset metadata records
│
└── data_chunks
    └── persisted chunk records
```

Validated examples:

```text
projects    → project0020, project0021, project00_21, project00-21
assets      → processed asset metadata
data_chunks → persisted chunk records
```

The validation confirms that the metadata store layer can persist and link records across:

```text
Project → Asset → DataChunk
```

---

## 🚫 Out of Scope

This branch does not include:

- embedding generation
- vector database integration
- semantic search
- augmented answer generation
- background workers
- application user authentication
- JWT authentication
- role-based access control

---

## ✅ Definition of Done

This branch is complete when:

- project metadata can be created or reused
- asset metadata can be created or reused
- uploaded assets can be retrieved
- chunks can be inserted
- chunks can be retrieved by asset
- asset status can be updated to processed
- asset chunk count can be updated
- project IDs support letters, numbers, underscores, and hyphens
- validation script runs successfully
- MongoDB records are visible in Studio 3T
- pytest runs without errors
- documentation is updated

---

## 🔜 Next Branch

The next branch should connect this persistence logic directly to the API workflow.

Expected next work:

```text
Upload endpoint → create project + asset metadata
Processing endpoint → create chunks + update asset metadata
```
