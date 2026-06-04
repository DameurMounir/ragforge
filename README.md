# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation (RAG)** backend platform built step by step with real software engineering practices.

The project starts from a clean FastAPI backend and progressively evolves toward document ingestion, project-based storage, metadata management, text extraction, chunking, LLM integration, vector databases, embeddings, indexing, semantic search, grounded answer generation, background workers, observability, security, and production deployment.

RAGForge is not a notebook demo. It is designed as a long-term AI engineering project focused on building a clean, scalable, and professional backend architecture.

---

## 🎯 Project Vision

RAGForge aims to become a modular foundation for building production-ready RAG systems.

The objective is to master the full engineering path from a basic backend service to a production-ready AI platform that can later be reused by applications, websites, internal tools, or agent systems as a reliable knowledge backend.

RAGForge is also designed as one infrastructure brick inside a broader agentic systems architecture. It is not limited to naive RAG. It prepares the foundation for retrieval tools, answer-generation tools, source-grounded knowledge access, orchestration layers, observability, and future AI system components.

---

## 🧠 Knowledge-Oriented RAG Direction

RAGForge is built with the understanding that **RAG is not dead**.

What is becoming obsolete is **naive RAG**: systems that only split documents into chunks, retrieve a few similar passages, and pass them directly to an LLM without strong metadata, structure, provenance, indexing, source control, or workflow discipline.

RAGForge follows a more modern **knowledge-oriented RAG direction**.

The goal is to evolve from simple document retrieval toward a production-grade knowledge backend where every source is tracked as an asset, every extracted chunk is linked to its origin, metadata is persisted, vectors are indexed, semantic search returns source-ready evidence, and grounded answers can be generated with structured sources.

The current architectural direction is:

```text
Project
  ↓
Asset
  ↓
DataChunk
  ↓
Embedding
  ↓
Vector Indexing
  ↓
Semantic Search
  ↓
Grounded / Augmented Answer with Sources
```

This makes RAGForge more than a basic RAG demo. It is designed as a foundation for structured knowledge systems that can later support applications, websites, internal tools, and agentic AI workflows.

---

## 🧭 7-Milestone Roadmap

| Milestone | Focus | Expected Result |
|---|---|---|
| M1 | 🧱 Project Bootstrap & Environment | Repository, environment, Git workflow, README, and initial project structure |
| M2 | ⚙️ FastAPI Backend Foundation | Running FastAPI app with structured routes, environment configuration, and health check |
| M3 | 📄 Document Upload & Processing Foundation | Upload endpoint, file validation, project-based storage, and document processing foundation |
| M4 | 🗄️ Database Metadata, Indexing & Ingestion Pipeline | MongoDB metadata layer, asset schemas, stores, indexes, upload metadata persistence, processing metadata persistence, and stable ingestion pipeline |
| M5 | 🔎 RAG Core: LLM, Vector Store & Retrieval | LLM factory, vector database factory, embeddings, indexing, semantic search, retrieval, and grounded answer generation |
| M6 | 🐳 Production Deployment & Workers | Docker deployment, PostgreSQL/PgVector evolution, Redis, Celery workers, schedulers, and production runtime setup |
| M7 | 🛡️ Observability, Security & Agent-Ready Evolution | Monitoring, structured logs, evaluation, security hardening, and preparation for agentic system integration |

---

## 🚦 Current Development Focus

### Current Milestone

Milestone 5 — RAG Core: LLM, Vector Store & Retrieval

### Latest Completed Branch

Branch 18 — Augmented Answers with Sources

Git branch:

```text
feature/18-augmented-answers-with-sources
```

Branch 18 completes the first functional end-to-end RAG Core flow.

It connects semantic search evidence to grounded answer generation:

```text
Question
  ↓
SemanticSearchService
  ↓
Ranked evidence chunks
  ↓
RAGContextBuilder
  ↓
RAG prompt builder
  ↓
LLMService
  ↓
Grounded answer with sources
```

It adds:

- answer request schema,
- answer response schema,
- source schema,
- evidence schema,
- `RAGAnswerService`,
- `RAGContextBuilder`,
- isolated RAG answer prompt builder,
- answer route,
- Branch 18 validation script,
- answer schema tests,
- context builder tests,
- answer service tests,
- source-aware response structure,
- debug prompt control,
- complete answer endpoint validation.

Branch 18 validates that RAGForge can:

```text
Upload document
  ↓
Process document
  ↓
Persist chunks in MongoDB
  ↓
Index chunk embeddings into Qdrant
  ↓
Search indexed vectors
  ↓
Build source-numbered context
  ↓
Generate a grounded answer
  ↓
Return answer + sources + evidence
```

### Next Branch

Branch 19 — RAG Core Stabilization

Branch 19 will stabilize the full RAG Core v1 by improving:

- end-to-end validation,
- error handling,
- local/demo readiness,
- documentation consistency,
- regression testing,
- API examples,
- local LLM readiness,
- professional cleanup before moving toward production deployment.

---

## Documentation Map Entries

| Document | Purpose |
|---|---|
| [`docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md`](docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md) | Milestone 5 RAG Core overview |
| [`docs/milestones/milestone-05-rag-core/branches/branch-14-llm-factory.md`](docs/milestones/milestone-05-rag-core/branches/branch-14-llm-factory.md) | Branch 14 LLM Factory implementation notes |
| [`docs/milestones/milestone-05-rag-core/branches/branch-15-vector-db-factory-qdrant.md`](docs/milestones/milestone-05-rag-core/branches/branch-15-vector-db-factory-qdrant.md) | Branch 15 Vector DB Factory with Qdrant implementation notes |
| [`docs/milestones/milestone-05-rag-core/branches/branch-16-embeddings-indexing.md`](docs/milestones/milestone-05-rag-core/branches/branch-16-embeddings-indexing.md) | Branch 16 Embeddings & Indexing Foundation implementation notes |
| [`docs/milestones/milestone-05-rag-core/branches/branch-17-semantic-search.md`](docs/milestones/milestone-05-rag-core/branches/branch-17-semantic-search.md) | Branch 17 Semantic Search implementation notes |
| [`docs/milestones/milestone-05-rag-core/branches/branch-18-augmented-answers-with-sources.md`](docs/milestones/milestone-05-rag-core/branches/branch-18-augmented-answers-with-sources.md) | Branch 18 Augmented Answers with Sources implementation notes |

---

## 🧱 Architecture Overview

RAGForge follows a production-oriented FastAPI `src/` architecture with a service-based backend structure.

The stable architecture principle is:

```text
Route → Service → Infrastructure
```

More specifically:

```text
HTTP Request
    ↓
FastAPI Route
    ↓
Service Layer
    ↓
Storage / Database / Vector Database / LLM / Embedding Provider
    ↓
API Response
```

After Branch 13, the document processing flow follows this structure:

```text
documents.py
  ↓
PipelineService
  ↓
DocumentProcessingService
  ↓
ProjectStore / AssetStore / ChunkStore
  ↓
MongoDB
```

After Branch 14 and Branch 15, the RAG Core foundation adds provider-based AI infrastructure:

```text
Application / Route Layer
  ↓
Service Layer
  ├── LLMService
  └── VectorDBService
      ↓
Provider Factories
  ├── LLMProviderFactory
  └── VectorDBProviderFactory
      ↓
Provider Interfaces
  ├── BaseLLMProvider
  └── BaseVectorDBProvider
      ↓
Provider Implementations
  ├── FakeLLMProvider
  ├── OpenAICompatibleLLMProvider
  └── QdrantProvider
```

After Branch 16, the indexing foundation adds the embedding and indexing path:

```text
Indexing Route
  ↓
IndexingService
  ↓
ProjectStore / ChunkStore
  ↓
EmbeddingProviderFactory
  ↓
EmbeddingProvider
  ↓
VectorDBService
  ↓
VectorDBProviderFactory
  ↓
Vector DB Provider
```

After Branch 17, the semantic search path is:

```text
Search Route
  ↓
SemanticSearchService
  ↓
ProjectStore
  ↓
EmbeddingProviderFactory
  ↓
EmbeddingProvider
  ↓
VectorDBService
  ↓
VectorDBProviderFactory
  ↓
Vector DB Provider
  ↓
Ranked Evidence
```

After Branch 18, the grounded answer path is:

```text
Answers Route
  ↓
RAGAnswerService
  ↓
SemanticSearchService
  ↓
RAGContextBuilder
  ↓
RAG Prompt Builder
  ↓
LLMService
  ↓
Answer + Sources + Evidence
```

The route stays thin. The orchestration lives in the service layer. Provider-specific implementation details stay behind interfaces.

Full architecture reference:

[`docs/architecture/backend-architecture.md`](docs/architecture/backend-architecture.md)

---

## 🧩 No-Hardcode Architecture Rule

RAGForge follows a strict configuration rule:

```text
.env
  ↓
core/config.py
  ↓
settings
  ↓
factory/service
  ↓
provider
```

Runtime operational values must not be hidden inside services, routes, or provider factories.

Allowed places for defaults:

```text
.env.example
src/ragforge/core/config.py
tests
validation scripts
documentation
```

Not allowed:

```text
services
routes
provider factories
provider-neutral orchestration code
```

Examples of values that must come from configuration:

```text
embedding model
embedding provider
vector collection name
vector size
distance metric
provider URL
provider name
LLM model
temperature
timeouts
token limits
answer default limit
answer max context size
debug prompt behavior
```

Generic services must not reference provider-specific configuration names such as `QDRANT_COLLECTION_NAME`, `QDRANT_VECTOR_SIZE`, or `QDRANT_DISTANCE`.

Provider-specific settings are allowed only at provider boundaries, such as the provider factory and provider implementation.

This keeps RAGForge provider-neutral, testable, and ready for future backends such as Qdrant, pgvector, Weaviate, Milvus, Pinecone, or another vector database.

---

## 📦 Project Structure

```text
ragforge/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .gitignore
│
├── docker/
│   └── docker-compose.yml
│
├── docs/
│   ├── architecture/
│   │   └── backend-architecture.md
│   ├── milestones/
│   │   ├── milestone-03-document-upload/
│   │   ├── milestone-04-database-metadata-indexing/
│   │   └── milestone-05-rag-core/
│   │       ├── milestone-05-rag-core.md
│   │       └── branches/
│   │           ├── branch-14-llm-factory.md
│   │           ├── branch-15-vector-db-factory-qdrant.md
│   │           ├── branch-16-embeddings-indexing.md
│   │           ├── branch-17-semantic-search.md
│   │           └── branch-18-augmented-answers-with-sources.md
│   ├── setup/
│   │   └── local-development.md
│   └── api/
│       └── endpoints.md
│
├── resources/
├── scripts/
│   └── validation/
│       ├── validate_branch_15_vector_db.py
│       ├── validate_branch_16_indexing.py
│       ├── validate_branch_17_semantic_search.py
│       └── validate_branch_18_answers.py
│
├── storage/
│   └── uploads/
│       └── {project_id}/
│           └── documents/
│
├── tests/
│   ├── test_answer_schemas.py
│   ├── test_embedding_provider_factory.py
│   ├── test_indexing_schemas.py
│   ├── test_llm_factory.py
│   ├── test_llm_service.py
│   ├── test_rag_answer_service.py
│   ├── test_rag_context_builder.py
│   ├── test_search_schemas.py
│   ├── test_semantic_search_service.py
│   └── test_vector_db_factory.py
│
└── src/
    └── ragforge/
        ├── main.py
        ├── core/
        ├── exceptions/
        ├── models/
        │   ├── enums/
        │   └── db_schemes/
        ├── prompts/
        │   └── rag_answer_prompt.py
        ├── providers/
        │   ├── embedding/
        │   ├── llm/
        │   └── vector_db/
        ├── routes/
        │   ├── answers.py
        │   ├── documents.py
        │   ├── indexing.py
        │   ├── llm.py
        │   └── search.py
        ├── schemas/
        │   ├── answers.py
        │   ├── document_processing.py
        │   ├── indexing.py
        │   └── search.py
        ├── services/
        │   ├── document_service.py
        │   ├── document_processing_service.py
        │   ├── indexing_service.py
        │   ├── llm_service.py
        │   ├── pipeline_service.py
        │   ├── rag_answer_service.py
        │   ├── rag_context_builder.py
        │   ├── semantic_search_service.py
        │   └── vector_db_service.py
        ├── stores/
        │   └── mongodb/
        └── utils/
```

Detailed branch-level file changes belong in the relevant branch document, not in this README.

---

## 🌐 API Documentation

Current API endpoints, request examples, response examples, and testing notes are documented here:

[`docs/api/endpoints.md`](docs/api/endpoints.md)

Swagger UI is available when the server is running:

```text
http://127.0.0.1:8000/docs
```

---

## 🚀 Local Development

Local setup, environment preparation, installation commands, and run instructions are documented here:

[`docs/setup/local-development.md`](docs/setup/local-development.md)

Quick run command:

```bash
uvicorn src.ragforge.main:app --reload --reload-dir src --host 127.0.0.1 --port 8000
```

MongoDB and Qdrant are launched through the Docker Compose file inside the `docker/` directory:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up -d
```

Check container status:

```bash
docker compose --env-file .env -f docker/docker-compose.yml ps
```

Check Qdrant health:

```bash
curl http://localhost:6333/healthz
```

Run validation scripts:

```bash
python scripts/validation/validate_branch_15_vector_db.py
python scripts/validation/validate_branch_16_indexing.py
python scripts/validation/validate_branch_17_semantic_search.py
python scripts/validation/validate_branch_18_answers.py
```

Run tests:

```bash
pytest
```

---

## 🔎 Branch 16 Indexing Endpoint

Branch 16 adds the indexing endpoint:

```http
POST /api/v1/indexing/{project_id}
```

Example request:

```json
{
  "asset_id": null,
  "do_reset": true,
  "batch_size": 32,
  "limit": null,
  "strategy": "simple_chunk",
  "granularity": "chunk",
  "include_results": true
}
```

Example response:

```json
{
  "signal": "indexing_success",
  "message": "Indexing completed.",
  "project_id": "project16test",
  "asset_id": null,
  "strategy": "simple_chunk",
  "granularity": "chunk",
  "collection_name": "ragforge_chunks",
  "embedding_model": "fake-embedding-model",
  "indexed_chunks": 1,
  "failed_chunks": 0,
  "skipped_chunks": 0
}
```

---

## 🔍 Branch 17 Semantic Search Endpoint

Branch 17 adds the semantic search endpoint:

```http
POST /api/v1/search/{project_id}
```

Example request:

```json
{
  "query": "indexing pipeline fake embedding Qdrant",
  "limit": 5,
  "asset_id": null,
  "min_score": null,
  "include_text": true,
  "include_metadata": true
}
```

Example response:

```json
{
  "signal": "semantic_search_success",
  "message": "Semantic search completed.",
  "project_id": "project16test",
  "query": "indexing pipeline fake embedding Qdrant",
  "collection_name": "ragforge_chunks",
  "embedding_model": "fake-embedding-model",
  "total_results": 1,
  "results": [
    {
      "rank": 1,
      "score": -0.045289338,
      "record_id": "6a2053a1c374e1d233e0e76b",
      "chunk_id": "6a2053a1c374e1d233e0e76b",
      "asset_id": "6a20538ec374e1d233e0e76a",
      "project_id": "6a20538ec374e1d233e0e769",
      "chunk_order": 1,
      "text": "RAGForge Branch 16 validates the indexing pipeline...",
      "metadata": {
        "index_level": "chunk",
        "indexing_strategy": "simple_chunk",
        "source_type": "data_chunk",
        "embedding_model": "fake-embedding-model"
      }
    }
  ]
}
```

The fake embedding provider uses deterministic pseudo-vectors, so the score is not expected to behave like a real semantic embedding score. With real embedding providers, the score becomes semantically meaningful.

---

## 🧠 Branch 18 Augmented Answer Endpoint

Branch 18 adds the grounded answer endpoint:

```http
POST /api/v1/answers/{project_id}
```

Example request:

```json
{
  "question": "What is RAGForge?",
  "limit": 5,
  "asset_id": null,
  "min_score": null,
  "include_sources": true,
  "include_evidence": true,
  "include_debug_prompt": false
}
```

Example response:

```json
{
  "signal": "rag_answer_success",
  "message": "Answer generated from retrieved evidence.",
  "project_id": "project18test",
  "question": "What is RAGForge?",
  "answer": "Fake RAGForge response generated successfully. Input preview: Question:\nWhat is RAGForge?\n\nRetrieved sources:\n[Source 1] rank=1...",
  "sources": [
    {
      "source_number": 1,
      "rank": 1,
      "score": 0.021401197,
      "record_id": "6a21d739b5d8264b4c0feeda",
      "chunk_id": "6a21d739b5d8264b4c0feeda",
      "asset_id": "6a21d720b5d8264b4c0feed9",
      "project_id": "6a21d720b5d8264b4c0feed8",
      "chunk_order": 1,
      "metadata": {
        "index_level": "chunk",
        "indexing_strategy": "simple_chunk",
        "source_type": "data_chunk",
        "embedding_model": "fake-embedding-model"
      }
    }
  ],
  "evidence": [
    {
      "source_number": 1,
      "text": "RAGForge is a modular RAG backend...",
      "score": 0.021401197,
      "chunk_id": "6a21d739b5d8264b4c0feeda",
      "asset_id": "6a21d720b5d8264b4c0feed9",
      "chunk_order": 1,
      "metadata": {
        "index_level": "chunk",
        "indexing_strategy": "simple_chunk",
        "source_type": "data_chunk",
        "embedding_model": "fake-embedding-model"
      }
    }
  ],
  "llm_model": "fake-ragforge-model",
  "retrieval_count": 1,
  "debug_prompt": null
}
```

The fake LLM provider returns a deterministic fake response for local validation. With a real LLM provider, the same endpoint generates a real grounded answer from retrieved evidence.

---

## ⚙️ RAG Core Configuration

Generic vector indexing configuration:

```env
VECTOR_DB_COLLECTION_NAME="ragforge_chunks"
VECTOR_DB_VECTOR_SIZE=1536
VECTOR_DB_DISTANCE="cosine"
```

Vector DB provider configuration:

```env
VECTOR_DB_PROVIDER="qdrant"
QDRANT_MODE="server"
QDRANT_URL="http://localhost:6333"
QDRANT_API_KEY=""
QDRANT_LOCAL_PATH="storage/vector_db/qdrant"
QDRANT_PREFER_GRPC=false
```

Embedding configuration:

```env
EMBEDDING_PROVIDER="fake"
EMBEDDING_MODEL="text-embedding-3-small"
EMBEDDING_VECTOR_SIZE=1536
EMBEDDING_BATCH_SIZE=32
FAKE_EMBEDDING_MODEL="fake-embedding-model"

EMBEDDING_OPENAI_API_KEY=""
EMBEDDING_OPENAI_BASE_URL=""
```

Semantic search configuration:

```env
SEARCH_DEFAULT_LIMIT=5
SEARCH_MAX_LIMIT=20
# SEARCH_MIN_SCORE=
SEARCH_INCLUDE_TEXT_DEFAULT=true
SEARCH_INCLUDE_METADATA_DEFAULT=true
```

RAG answer configuration:

```env
RAG_ANSWER_DEFAULT_LIMIT=5
RAG_ANSWER_MAX_CONTEXT_CHARS=8000
RAG_ANSWER_INCLUDE_SOURCES_DEFAULT=true
RAG_ANSWER_INCLUDE_EVIDENCE_DEFAULT=true
RAG_ANSWER_DEBUG_PROMPT_DEFAULT=false
```

LLM configuration:

```env
LLM_PROVIDER="fake"
LLM_DEFAULT_MODEL="fake-ragforge-model"
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=512
LLM_TIMEOUT_SECONDS=60

OPENAI_API_KEY=""
OPENAI_BASE_URL=""
```

---

## 📚 Documentation Map

| Document | Purpose |
|---|---|
| [`docs/architecture/backend-architecture.md`](docs/architecture/backend-architecture.md) | Stable backend architecture and long-term design principles |
| [`docs/milestones/`](docs/milestones/) | All milestone overviews, branch plans, and implementation history |
| [`docs/milestones/milestone-04-database-metadata-indexing/milestone-04-database-metadata-indexing.md`](docs/milestones/milestone-04-database-metadata-indexing/milestone-04-database-metadata-indexing.md) | Milestone 4 metadata and ingestion pipeline overview |
| [`docs/milestones/milestone-04-database-metadata-indexing/branches/branch-13-data-pipeline-enhancements.md`](docs/milestones/milestone-04-database-metadata-indexing/branches/branch-13-data-pipeline-enhancements.md) | Branch 13 implementation details and validation |
| [`docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md`](docs/milestones/milestone-05-rag-core/milestone-05-rag-core.md) | Milestone 5 RAG Core overview |
| [`docs/milestones/milestone-05-rag-core/branches/branch-14-llm-factory.md`](docs/milestones/milestone-05-rag-core/branches/branch-14-llm-factory.md) | Branch 14 LLM Factory implementation details |
| [`docs/milestones/milestone-05-rag-core/branches/branch-15-vector-db-factory-qdrant.md`](docs/milestones/milestone-05-rag-core/branches/branch-15-vector-db-factory-qdrant.md) | Branch 15 Vector DB Factory with Qdrant implementation details |
| [`docs/milestones/milestone-05-rag-core/branches/branch-16-embeddings-indexing.md`](docs/milestones/milestone-05-rag-core/branches/branch-16-embeddings-indexing.md) | Branch 16 Embeddings & Indexing Foundation implementation details |
| [`docs/milestones/milestone-05-rag-core/branches/branch-17-semantic-search.md`](docs/milestones/milestone-05-rag-core/branches/branch-17-semantic-search.md) | Branch 17 Semantic Search implementation details |
| [`docs/milestones/milestone-05-rag-core/branches/branch-18-augmented-answers-with-sources.md`](docs/milestones/milestone-05-rag-core/branches/branch-18-augmented-answers-with-sources.md) | Branch 18 Augmented Answers with Sources implementation details |
| [`docs/api/endpoints.md`](docs/api/endpoints.md) | API endpoints, request examples, and response examples |
| [`docs/setup/local-development.md`](docs/setup/local-development.md) | Local setup, installation, running commands, and common problems |

---

## 🌿 Development Workflow

RAGForge follows a professional GitHub workflow:

```text
Milestone → Issue → Branch → Pull Request → Merge
```

Each branch should focus on one clear responsibility.

Branch numbering is global across the project.

Examples:

```text
Branch 9  → Docker MongoDB Motor Infrastructure
Branch 10 → Asset Metadata Schemes & Stores
Branch 11 → MongoDB Metadata Indexes & Auth
Branch 12 → Upload and Processing Metadata Persistence
Branch 13 → Data Pipeline Enhancements
Branch 14 → LLM Factory
Branch 15 → Vector DB Factory with Qdrant
Branch 16 → Embeddings & Indexing Foundation
Branch 17 → Semantic Search
Branch 18 → Augmented Answers with Sources
Branch 19 → RAG Core Stabilization
```

Documentation rule:

```text
README.md
= stable public landing page

docs/architecture/
= stable architecture

docs/milestones/
= milestone and branch implementation history

docs/api/
= endpoint details

docs/setup/
= setup and run instructions
```

The README should stay stable.

Branch-specific implementation details should be added to the relevant branch `.md` file.

---

## 🧠 Engineering Principles

RAGForge follows these principles:

- keep routes thin
- move business logic to services
- centralize configuration in `core/config.py`
- use controlled response signals
- use provider interfaces for replaceable external systems
- avoid hidden hardcoded operational values in services and factories
- keep generic services provider-neutral
- keep provider-specific settings at provider boundaries
- keep runtime data outside source code
- keep uploaded files out of Git
- do not commit private `.env` files
- do not expose internal absolute paths
- keep each branch focused on one responsibility
- use one branch identifier everywhere: Git branch, issue, PR, and documentation
- document implementation details in milestone branch files
- treat metadata as a first-class part of modern RAG architecture
- link every chunk to its source asset for traceability and future citations
- return source-ready evidence before answer generation
- generate grounded answers only from retrieved evidence
- keep answer generation separate from retrieval
- keep prompt construction separate from orchestration
- hide debug prompts by default
- keep pipeline orchestration reusable for future workers and agentic layers

---

## ✅ Current Stable Backend Capability

At the end of Branch 18, RAGForge can:

```text
Upload document
  ↓
Persist project and asset metadata
  ↓
Process one asset or all project assets
  ↓
Extract and split document content
  ↓
Persist DataChunk records
  ↓
Update asset processing status
  ↓
Generate embeddings for stored chunks
  ↓
Index vectors into Qdrant
  ↓
Mark chunks as embedded
  ↓
Search indexed vectors by user query
  ↓
Return ranked evidence chunks with source metadata
  ↓
Build source-numbered context
  ↓
Generate a grounded answer through LLMService
  ↓
Return answer, sources, evidence, model, and retrieval count
```

RAGForge also has:

```text
LLM provider layer
  ↓
Fake and OpenAI-compatible providers
  ↓
LLM service
  ↓
LLM generation endpoint
```

And:

```text
VectorDBService
  ↓
VectorDBProviderFactory
  ↓
BaseVectorDBProvider
  ↓
QdrantProvider
  ↓
Qdrant Docker service
```

And:

```text
EmbeddingProviderFactory
  ↓
BaseEmbeddingProvider
  ↓
FakeEmbeddingProvider / OpenAICompatibleEmbeddingProvider
  ↓
IndexingService
  ↓
Qdrant vector indexing
```

And now:

```text
RAGAnswerService
  ↓
SemanticSearchService
  ↓
RAGContextBuilder
  ↓
RAG prompt builder
  ↓
LLMService
  ↓
Grounded answer with structured sources
```

Supported `/process/{project_id}` modes from the ingestion pipeline:

```text
all_project_file_assets
single_asset_by_id
single_asset_by_filename
```

Supported RAG Core endpoints now include:

```text
POST /api/v1/llm/generate
POST /api/v1/indexing/{project_id}
POST /api/v1/search/{project_id}
POST /api/v1/answers/{project_id}
```

---

## ✅ Branch 18 Validation Result

Branch 18 validation confirms:

```text
30 passed
Branch 18 answer validation passed
```

The validated end-to-end test flow was:

```text
Upload
  ↓
Process
  ↓
Index
  ↓
Answer
```

The answer response includes:

```text
rag_answer_success
answer
sources
evidence
llm_model
retrieval_count
debug_prompt = null by default
```

Architecture audit:

```text
No controller pattern added.
No direct vector database coupling in the answer route/service.
No direct concrete LLM provider coupling in the answer route/service.
No hidden settings fallback in the new Branch 18 service path.
```

---

## 👤 Author

**Dameur Mounir**

AI engineer and system builder focused on production-grade RAG, agentic AI systems, vector databases, observability, and deployable AI architectures.

My objective is to build practical, robust, and scalable AI systems that can evolve from learning projects into real products, client solutions, and future agentic platforms.