# 📄 Milestone 3 — File Upload & Document Processing

## 🎯 Objective

Milestone 3 introduces the first real **document ingestion capability** in RAGForge.

The goal is to move from a basic FastAPI backend foundation to a backend that can:

- receive user documents
- validate uploaded files
- organize documents by project
- prepare files for future text extraction
- prepare the system for chunking, embeddings, and vector search

This milestone is intentionally divided into **small professional branches** instead of one large implementation branch.

---

## 🚀 Why This Milestone Matters

RAG systems start with documents.

Before adding embeddings, vector databases, retrieval, or LLM generation, the platform must first support a reliable document upload pipeline.

This milestone prepares the foundation for:

- 📥 document ingestion
- ✅ file validation
- 🗂️ project-based storage
- 📄 text extraction
- ✂️ chunking
- 🧾 metadata tracking
- ⏱️ background processing
- 🔎 vector indexing

---

## 🌿 Branch Plan

Milestone 3 is divided into four focused branches.

| Branch | Name | Purpose |
|---|---|---|
| 🧱 Branch 1 | `feature/4-service-architecture-and-settings` | Add service-oriented structure and Pydantic settings |
| 🧩 Branch 2 | `feature/5-response-signals-and-api-standards` | Add controlled API response signals using enums |
| 🗂️ Branch 3 | `feature/6-project-storage-service` | Add dynamic project-based storage service |
| 📤 Branch 4 | `feature/7-document-upload-endpoint` | Add document upload endpoint with validation and chunked saving |

---

# 🧱 Branch 1 — Service Architecture and Settings

## 🌿 Branch Name

```text
feature/4-service-architecture-and-settings