# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation** platform designed to build, test, and evolve modular RAG systems step by step.

This project is not a simple notebook or a small demo. It is a long-term AI engineering project focused on building a clean, scalable, and professional RAG backend architecture using real engineering practices: milestones, issues, branches, pull requests, testing, documentation, and deployment.

---

## 🎯 Project Vision

RAGForge aims to become a complete RAG backend foundation that can be progressively extended from a simple document-processing system into a production-ready Retrieval-Augmented Generation platform.

The project will evolve through structured milestones covering:

- 🧱 project setup and architecture
- ⚙️ FastAPI backend development
- 📄 document upload and processing
- 🗄️ database integration
- 🧾 document metadata management
- 🔎 vector search
- 🧬 embeddings
- 🤖 LLM integration
- 🔁 retrieval pipelines
- 💬 augmented answer generation
- 📊 evaluation and observability
- 🐳 Docker deployment
- ⏱️ background workers

The objective is to master the full RAG engineering path before moving later to more advanced agentic systems.

---

## 🚦 Current Status

The project is currently in:

```text
Milestone 1: Project Bootstrap & Environment
Issue #1: Define RAGForge Core vision and learning strategy
Branch: docs/1-ragforge-core-vision
```

---

## ✅ Requirements

- 🐍 Python 3.11 or later
- 📦 Miniconda or Anaconda
- 🌿 Git
- 🧑‍💻 Visual Studio Code
- 🐧 WSL Ubuntu

### 📦 Install Python using Miniconda

1. Download and install Miniconda from the official website.

2. Create a new Conda environment:

```bash
conda create -n ragforge python=3.11
```

3. Activate the environment:

```bash
conda activate ragforge
```

4. Verify Python version:

```bash
python --version
```

Expected result:

```text
Python 3.11.x
```

---

## 🔀 Development Workflow

This project follows a professional GitHub workflow:

- 🎯 one milestone for each major phase
- 🧩 one issue for each task
- 🌿 one branch for each issue
- 🔁 one pull request for each branch

For the current issue, the working branch is:

```text
docs/1-ragforge-core-vision
```

Typical workflow:

```bash
git checkout main
git pull origin main
git checkout -b docs/1-ragforge-core-vision
git status
git add .
git commit -m "docs: define RAGForge core vision"
git push -u origin docs/1-ragforge-core-vision
```

---

## 👤 Author

**Dameur Mounir**