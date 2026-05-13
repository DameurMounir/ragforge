# RAGForge

**RAGForge** is a production-oriented RAG platform designed to build, test, and evolve modular Retrieval-Augmented Generation systems.

The goal of this project is to progressively develop a complete RAG architecture with clean code, professional engineering practices, and scalable components.

---


## Project Vision

RAGForge is not just a minimal RAG demo.  
It is a long-term AI engineering project focused on building a solid foundation for real-world RAG and agentic applications.

The project will evolve step by step from a simple RAG system into a modular platform that includes:

- document ingestion
- text processing and chunking
- embeddings generation
- vector search
- retrieval pipelines
- answer generation
- FastAPI endpoints
- background workers
- database integration
- Docker-based deployment
- evaluation and observability
- agentic workflows

---

## Main Objectives

The main objectives of RAGForge are:

- Build a clean and modular RAG system
- Apply professional GitHub workflow using issues, milestones, branches, and pull requests
- Use production-oriented backend architecture
- Integrate vector databases such as Qdrant, FAISS, or pgvector
- Expose RAG features through FastAPI
- Add asynchronous processing using Celery and Redis
- Store metadata using PostgreSQL
- Add evaluation tools for retrieval and answer quality
- Prepare the system for future agentic workflows using LangGraph

---

## Planned Architecture

```text
ragforge/
├── app/
│   ├── api/
│   ├── core/
│   ├── ingestion/
│   ├── embeddings/
│   ├── retrieval/
│   ├── vectorstores/
│   ├── generation/
│   └── utils/
├── tests/
├── docs/
├── scripts/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── LICENSE