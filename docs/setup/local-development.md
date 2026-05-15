# 💻 Local Development Setup

This document explains how to set up **RAGForge** locally for development.

RAGForge currently uses a **FastAPI backend** with a professional `src/` package layout:

```text
uvicorn src.ragforge.main:app --reload --host 127.0.0.1 --port 8000
```

The recommended environment is **WSL Ubuntu + Conda + VS Code**.

---

## 🎯 Goal

The goal of this setup is to create a clean local development environment for:

- running the FastAPI backend
- testing API endpoints
- managing environment variables
- preparing future document upload features
- preparing future RAG, Qdrant, PostgreSQL, Redis, and worker integrations

---

## ✅ Requirements

Before running the project, install:

- 🐧 WSL Ubuntu
- 🐍 Python 3.11
- 📦 Miniconda or Anaconda
- 🌿 Git
- 🧑‍💻 Visual Studio Code
- 🔌 VS Code Remote WSL extension

---

## 🧰 System Dependencies

Some Python packages may require Linux system dependencies during installation.

Run inside **WSL Ubuntu**:

```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

---

## 🧠 Why These Packages?

| Package | Purpose |
|---|---|
| `libpq-dev` | Required later for PostgreSQL Python drivers |
| `gcc` | Required to compile some Python packages |
| `python3-dev` | Provides Python development headers |

These dependencies prepare the environment for future production features such as PostgreSQL integration and background workers.

---

## 🐍 Create Conda Environment

Create a dedicated Conda environment for RAGForge:

```bash
conda create -n ragforge python=3.11
```

Activate it:

```bash
conda activate ragforge
```

Verify Python version:

```bash
python --version
```

Expected result:

```text
Python 3.11.x
```

---

## 📥 Clone the Repository

Clone the project from GitHub:

```bash
git clone https://github.com/DameurMounir/ragforge.git
```

Enter the project folder:

```bash
cd ragforge
```

If the repository already exists locally, enter your existing folder:

```bash
cd ~/development/tech/ai-engineering/projects/rag/ragforge
```

---

## 📦 Install Python Dependencies

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Current important packages include:

```text
fastapi
uvicorn[standard]
python-multipart
python-dotenv
pydantic-settings
aiofiles
```

---

## ⚙️ Environment Variables

RAGForge uses environment variables to separate configuration from source code.

Create a local `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Open it in VS Code:

```bash
code .env
```

Example `.env` content:

```env
APP_NAME=RAGForge
APP_VERSION=0.1.0
APP_ENV=development

FILE_ALLOWED_TYPES=application/pdf,text/plain,text/markdown
FILE_MAX_SIZE_MB=10
FILE_DEFAULT_CHUNK_SIZE=524288
```

---

## 🔐 Environment Security Rule

The real `.env` file must never be committed to GitHub.

The public file is:

```text
.env.example
```

The private local file is:

```text
.env
```

Make sure `.gitignore` contains:

```gitignore
.env
.env.*
!.env.example
```

---

## 🧱 Current Project Structure

RAGForge uses a professional `src/` package architecture.

```text
ragforge/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
│
├── docs/
├── resources/
├── storage/
├── tests/
│
└── src/
    └── ragforge/
        ├── __init__.py
        ├── main.py
        ├── core/
        ├── routes/
        ├── services/
        ├── models/
        ├── schemas/
        ├── utils/
        └── exceptions/
```

The real FastAPI application lives in:

```text
src/ragforge/main.py
```

---

## 🚀 Run the API

From the project root, run:

```bash
uvicorn src.ragforge.main:app --reload --host 127.0.0.1 --port 8000
```

You should see output similar to:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

---

## 🌐 Open API Documentation

FastAPI automatically generates Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

Alternative documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## 🧪 Test Current Endpoints

### Base Route

```bash
curl http://127.0.0.1:8000/api/v1/
```

Expected response:

```json
{
  "message": "Hello and goodbye!",
  "app_name": "RAGForge",
  "app_version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-05-15T10:00:00+00:00"
}
```

---

### Health Route

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

Expected response:

```json
{
  "status": "healthy",
  "app_name": "RAGForge",
  "app_version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-05-15T10:00:00+00:00"
}
```

---

## 📤 Test Future Upload Route

After the document upload endpoint is implemented, test it with:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload/default" \
  -F "file=@README.md"
```

This route is planned for Milestone 3.

---

## 🧪 Run Tests

Install testing dependencies if needed:

```bash
pip install pytest httpx
```

Run all tests:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest tests/test_health.py -v
```

---

## 🌿 Git Workflow

Before starting a new branch, always update `main`:

```bash
git checkout main
git pull origin main
```

Create a feature branch:

```bash
git checkout -b feature/4-service-architecture-and-settings
```

Check status:

```bash
git status
```

Stage changes:

```bash
git add .
```

Commit changes:

```bash
git commit -m "refactor: move backend to src package architecture"
```

Push branch:

```bash
git push -u origin feature/4-service-architecture-and-settings
```

---

## 🔁 Current Branch Example

For Milestone 3 Branch 1:

```text
feature/4-service-architecture-and-settings
```

Purpose:

```text
Move backend into src/ragforge package layout
Add service-oriented architecture
Prepare settings, docs, models, services, schemas, utils, and exceptions folders
```

---

## 🧹 Gitignore Rules for Local Development

Make sure `.gitignore` includes:

```gitignore
# Private environment files
.env
.env.*
!.env.example

# Python cache
__pycache__/
*.pyc

# Uploaded documents and runtime storage
storage/uploads/*
!storage/uploads/.gitkeep

# Local runtime logs
*.log

# Temporary local files
tmp/
temp/
```

---

## 📁 Storage Folder

Uploaded files should be stored outside source code:

```text
storage/uploads/
```

The folder should contain a `.gitkeep` file so Git keeps the folder structure:

```text
storage/uploads/.gitkeep
```

Real uploaded files must not be committed.

---

## 🛠️ Common Problems

### Problem: Uvicorn cannot import the app

If you moved the app into `src/ragforge/main.py`, do not run:

```bash
uvicorn main:app --reload
```

Use:

```bash
uvicorn src.ragforge.main:app --reload --host 127.0.0.1 --port 8000
```

---

### Problem: Environment variables are not loaded

Check that `.env` exists:

```bash
ls -la
```

If not, create it:

```bash
cp .env.example .env
```

---

### Problem: `.env` appears in `git status`

If `.env` was accidentally tracked before, remove it from Git tracking:

```bash
git rm --cached .env
```

Then commit the `.gitignore` fix.

If Git says:

```text
fatal: pathspec '.env' did not match any files
```

that means `.env` was not tracked. This is good.

---

### Problem: Uploaded files appear in Git status

Check `.gitignore`:

```gitignore
storage/uploads/*
!storage/uploads/.gitkeep
```

Then run:

```bash
git status
```

Only `.gitkeep` should be tracked.

---

## 🧑‍💻 Optional Terminal Prompt Improvement

To make the WSL Ubuntu terminal easier to read:

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

To make it permanent:

```bash
echo 'export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "' >> ~/.bashrc
source ~/.bashrc
```

This displays the current folder clearly and puts the command input on a new line.

---

## 🧭 Future Local Services

Later, local development will include:

```text
PostgreSQL
Qdrant
Redis
Celery workers
Flower dashboard
Docker Compose
```

The future local stack may look like:

```text
FastAPI
PostgreSQL
Qdrant
Redis
Celery
Flower
```

These services will be added progressively in future milestones.

---

## ✅ Local Development Checklist

Before working on RAGForge, make sure:

- Conda environment is activated
- dependencies are installed
- `.env` exists
- API runs with Uvicorn
- `/docs` opens correctly
- `/api/v1/` works
- `/api/v1/health/` works
- Git branch is correct
- `.env` is not tracked
- uploaded files are ignored

---

## 📌 Quick Commands Summary

```bash
conda activate ragforge
pip install -r requirements.txt
cp .env.example .env
uvicorn src.ragforge.main:app --reload --host 127.0.0.1 --port 8000
```

Test:

```bash
curl http://127.0.0.1:8000/api/v1/
curl http://127.0.0.1:8000/api/v1/health/
```
