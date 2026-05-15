# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation (RAG)** platform designed to build, test, and evolve modular RAG systems step by step.

This project is not a simple notebook or a small demo. It is a long-term AI engineering project focused on building a clean, scalable, and professional RAG backend architecture using real engineering practices: **milestones, issues, branches, pull requests, documentation, testing, and deployment**.

---

## 🎯 Project Vision

RAGForge aims to become a complete RAG backend foundation that can progressively evolve from a basic document-processing system into a production-ready Retrieval-Augmented Generation and agentic AI platform.

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
- 🧠 future agentic extensions

The objective is to master the full RAG engineering path before moving later to more advanced agentic systems.

---

## 🚦 Current Status

The project is currently in:

```text
Milestone 2: FastAPI Backend Foundation
Issue #6: Add nested routes and environment configuration
Branch: feature/3-routes-env-config
```

This branch improves the initial FastAPI foundation by introducing:

- a dedicated `routes/` package
- a versioned API router using the `/api/v1` prefix
- environment-based configuration using `.env`
- application metadata returned from API responses
- a dedicated health check endpoint
- `python-dotenv` support
- a cleaner structure ready for future backend modules

Current active endpoints:

```text
GET /api/v1/
GET /api/v1/health/
GET /docs
```

---

## ✅ Requirements

Before using this project, make sure you have the following tools installed:

- 🐧 WSL Ubuntu
- 🐍 Python 3.11
- 📦 Miniconda or Anaconda
- 🌿 Git
- 🧑‍💻 Visual Studio Code
- 🐙 GitHub account

---

## 🧰 Install System Dependencies

Some Python packages may need Linux system dependencies during installation.

Run the following commands inside **WSL Ubuntu**:

```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

### Why these dependencies?

- `libpq-dev` will be useful later for PostgreSQL-related Python packages.
- `gcc` is needed to compile some Python dependencies.
- `python3-dev` provides Python development headers required by some packages.

---

## 📦 Install Python Using Miniconda

### 1. Create a new Conda environment

Create a dedicated environment for this project:

```bash
conda create -n ragforge python=3.11
```

### 2. Activate the environment

```bash
conda activate ragforge
```

After activation, you should see something like this:

```text
(ragforge) dameurmounir@DESKTOP-XXXX:~/development/tech/ai-engineering/projects/rag/ragforge$
```

### 3. Verify Python version

```bash
python --version
```

Expected result:

```text
Python 3.11.x
```

---

## 💻 Optional: Improve Command Line Readability

To make the WSL Ubuntu terminal easier to read, you can customize the shell prompt:

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

This displays the username, hostname, and current directory on one line, then places the command input on a new line.

To make this change permanent:

```bash
echo 'export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "' >> ~/.bashrc
source ~/.bashrc
```

---

## 📥 Clone the Repository

Clone the project from GitHub:

```bash
git clone https://github.com/YOUR_USERNAME/ragforge.git
```

Enter the project folder:

```bash
cd ragforge
```

If the repository is already cloned, enter the existing folder:

```bash
cd ~/development/tech/ai-engineering/projects/rag/ragforge
```

---

## 📚 Install Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The current `requirements.txt` contains:

```txt
fastapi==0.136.1
uvicorn[standard]==0.46.0
python-multipart==0.0.28
python-dotenv==1.2.2
```

### Why these packages?

- `fastapi` is the backend web framework.
- `uvicorn[standard]` is the ASGI server used to run the FastAPI application.
- `python-multipart` will be used later for file upload support.
- `python-dotenv` loads environment variables from the local `.env` file.

---

## ⚙️ Setup Environment Variables

The project uses environment variables to separate configuration from source code.

### 1. Copy the example environment file

```bash
cp .env.example .env
```

### 2. Open `.env`

```bash
code .env
```

### 3. Example `.env` content

```env
APP_NAME="RAGForge"
APP_VERSION="0.1.0"
APP_ENV="development"
OPENAI_API_KEY=""
```

For now, `OPENAI_API_KEY` can stay empty.

Later, when LLM integration is added, the real API key can be stored locally inside `.env`.

---

## 🔐 Important Security Rule

Never commit the real `.env` file to GitHub.

The `.gitignore` file must contain:

```gitignore
.env
```

The public file is:

```text
.env.example
```

The private local file is:

```text
.env
```

---

## 🗂️ Current Project Structure

The current repository structure is:

```text
ragforge/
├── resources/
│   ├── .gitkeep
│   └── ragforge.postman_collection.json
├── routes/
│   ├── __init__.py
│   ├── base.py
│   └── health.py
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── main.py
└── requirements.txt
```

### Why `resources/`?

The `resources/` folder is reserved for small project support files such as:

- 🖼️ screenshots
- 📊 diagrams
- 📄 small sample files
- 🧾 documentation resources
- 🧪 Postman collections

The current Postman collection can be used to test the first API endpoints.

### Why `routes/`?

The `routes/` folder separates API route definitions from the main FastAPI application file.

This prepares the backend for a cleaner and more scalable architecture. Instead of putting every endpoint directly inside `main.py`, each group of routes can later be organized into its own module.

Current route modules:

| File | Responsibility |
|---|---|
| `routes/base.py` | Defines the base `/api/v1/` endpoint |
| `routes/health.py` | Defines the `/api/v1/health/` health check endpoint |
| `routes/__init__.py` | Marks `routes/` as a Python package |

---

## ▶️ How to Run the FastAPI Application

The project now contains a minimal FastAPI backend with structured routing and environment configuration.

### 1. Activate the environment

```bash
conda activate ragforge
```

### 2. Enter the project folder

```bash
cd ~/development/tech/ai-engineering/projects/rag/ragforge
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare environment variables

```bash
cp .env.example .env
```

### 5. Run the API

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

You can also use `0.0.0.0` if you want the server to listen on all interfaces:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌐 Current API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/` | Returns a base message with application metadata loaded from `.env` |
| GET | `/api/v1/health/` | Returns the API health status with application metadata and UTC timestamp |
| GET | `/docs` | Opens the automatic Swagger UI generated by FastAPI |
| GET | `/redoc` | Opens the automatic ReDoc documentation generated by FastAPI |

---

## 🧪 Testing the Current Branch

### 1. Run the server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Test the base API route

Open:

```text
http://127.0.0.1:8000/api/v1/
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

### 3. Test the health check route

Open:

```text
http://127.0.0.1:8000/api/v1/health/
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

### 4. Test using `curl`

```bash
curl http://127.0.0.1:8000/api/v1/
curl http://127.0.0.1:8000/api/v1/health/
```

### 5. Open the automatic API documentation

Open:

```text
http://127.0.0.1:8000/docs
```

Expected result:

```text
FastAPI Swagger documentation opens successfully.
```

---

## ⚙️ Milestone 2 — FastAPI Backend Foundation

Milestone 2 introduces the first backend layer of RAGForge Core.

The milestone is divided into three parts:

1. Minimal FastAPI foundation
2. Routes and environment configuration
3. Health check endpoint

---

### Part 1 — FastAPI Foundation

Implemented in the previous branch:

```text
feature/2-fastapi-foundation
```

Completed work:

- ✅ Created a minimal FastAPI application
- ✅ Added a first test endpoint
- ✅ Verified that the application runs with Uvicorn
- ✅ Verified that FastAPI documentation is available through `/docs`
- ✅ Added a Postman collection inside the `resources/` folder

---

### Part 2 — Routes and Environment Configuration

Implemented in the current branch:

```text
feature/3-routes-env-config
```

Completed work:

- ✅ Created a `routes/` folder
- ✅ Added `routes/__init__.py`
- ✅ Added `routes/base.py`
- ✅ Added an API router with the `/api/v1` prefix
- ✅ Loaded environment variables from `.env`
- ✅ Added `python-dotenv` to `requirements.txt`
- ✅ Returned `APP_NAME`, `APP_VERSION`, and `APP_ENV` from the API response
- ✅ Added a UTC timestamp to the base API response
- ✅ Updated `main.py` to include the base router

---

### Part 3 — Health Check Endpoint

Implemented in the current branch:

```text
feature/3-routes-env-config
```

Completed work:

- ✅ Added `routes/health.py`
- ✅ Added a dedicated health router with the `/api/v1/health` prefix
- ✅ Added a health check endpoint at `/api/v1/health/`
- ✅ Returned `status`, `APP_NAME`, `APP_VERSION`, `APP_ENV`, and UTC timestamp
- ✅ Updated `main.py` to include the health router
- ✅ Verified that the endpoint works with Uvicorn
- ✅ Verified that the route appears in FastAPI Swagger documentation

---

## 🧱 Architecture Notes

The project is now moving from a simple single-file FastAPI application toward a structured backend architecture.

Current architecture:

```text
main.py
  ├── includes routes/base.py
  │     └── exposes /api/v1/
  │
  └── includes routes/health.py
        └── exposes /api/v1/health/
```

Current responsibility of each file:

| File | Responsibility |
|---|---|
| `main.py` | Creates the FastAPI application, loads `.env`, and includes routers |
| `routes/base.py` | Defines the `/api/v1/` router and base endpoint |
| `routes/health.py` | Defines the `/api/v1/health/` router and health check endpoint |
| `routes/__init__.py` | Marks `routes/` as a Python package |
| `.env.example` | Shows required environment variables |
| `requirements.txt` | Lists Python dependencies |
| `resources/ragforge.postman_collection.json` | Provides API testing resources |

This structure will make it easier to add future route groups such as:

- document upload routes
- processing routes
- search routes
- RAG answer routes
- database health routes
- admin or monitoring routes

---

## 🩺 Why a Health Check Endpoint Matters

The health check endpoint is a small but important production feature.

It is commonly used by:

- Docker health checks
- Kubernetes readiness and liveness probes
- monitoring systems
- load balancers
- CI/CD pipelines
- uptime checkers
- deployment scripts

In the future, the health route can be extended into several checks:

```text
GET /api/v1/health/
GET /api/v1/health/db
GET /api/v1/health/qdrant
GET /api/v1/health/redis
GET /api/v1/health/workers
```

Future checks may verify:

- PostgreSQL connection
- Qdrant vector database status
- Redis availability
- Celery or ARQ worker status
- file storage availability
- model provider availability
- system uptime and readiness

---

## 🔀 Development Workflow

This project follows a professional GitHub workflow:

- 🎯 one milestone for each major phase
- 🧩 one issue for each task
- 🌿 one branch for each issue
- 🔁 one pull request for each branch

The goal is not only to write code, but to build the project like a real professional software engineering project.

---

## 🌿 Branch Workflow

Before starting a task, always create a branch from `main`.

### 1. Go to main

```bash
git checkout main
```

### 2. Pull latest changes

```bash
git pull origin main
```

### 3. Create a branch for the issue

For the current branch:

```bash
git checkout -b feature/3-routes-env-config
```

### 4. Make changes

For this branch, the main files are:

```text
main.py
README.md
requirements.txt
routes/base.py
routes/health.py
routes/__init__.py
.env.example
```

### 5. Check status

```bash
git status
```

### 6. Stage files

```bash
git add .
```

### 7. Commit changes

Recommended commit message:

```bash
git commit -m "feat: add routes, env config and health check"
```

### 8. Push the branch

```bash
git push -u origin feature/3-routes-env-config
```

### 9. Open a Pull Request

Open a Pull Request on GitHub and link it to the issue:

```text
Closes #6
```

Recommended PR title:

```text
Add routes, environment config and health check
```

---

## 🧩 Current Work Completed

The project already includes:

- ✅ Initial `README.md`
- ✅ RAGForge project vision
- ✅ Conda environment with Python 3.11
- ✅ `requirements.txt`
- ✅ FastAPI, Uvicorn, python-multipart, and python-dotenv
- ✅ `.env.example`
- ✅ Protected `.env` using `.gitignore`
- ✅ `resources/` folder
- ✅ Postman collection for API testing
- ✅ Minimal FastAPI application
- ✅ Structured `routes/` package
- ✅ `/api/v1/` endpoint
- ✅ `/api/v1/health/` endpoint
- ✅ Environment variable loading from `.env`
- ✅ Application name, version, and environment returned by the API
- ✅ UTC timestamp returned by API responses
- ✅ Successful Uvicorn execution
- ✅ FastAPI Swagger documentation through `/docs`

---

## 🗺️ Milestone Roadmap

RAGForge will be developed step by step through professional milestones.

| Milestone | Focus | Expected Result |
|---|---|---|
| M1 | 🧱 Project Bootstrap & Environment | README, environment, Git workflow, initial structure |
| M2 | ⚙️ FastAPI Backend Foundation | Running FastAPI app with structured routes, env config, and health check |
| M3 | 📄 File Upload & Processing | Upload and process documents |
| M4 | 🗄️ Database & Document Models | Store metadata, documents, and chunks |
| M5 | 🔁 Data Pipeline Checkpoint | Stable ingestion pipeline |
| M6 | 🔎 RAG Core | Embeddings, vector search, retrieval, answer generation |
| M7 | 🐳 Deployment & Workers | Docker, PostgreSQL, Qdrant/PgVector, Redis, Celery/ARQ, monitoring |

---

## ⚙️ Current Milestone: M2

### Goal

Create the first running backend service using FastAPI, structured routes, API versioning, environment-based configuration, and a production-style health check endpoint.

### Current focus

- FastAPI application setup
- Uvicorn execution
- structured routes
- API version prefix
- `.env` loading
- application metadata
- health check endpoint
- API documentation
- Postman testing resources

### Definition of Done

Milestone 2 will be considered complete when the project contains:

- ✅ running FastAPI application
- ✅ `/docs` available
- ✅ first API route working
- ✅ structured API routes
- ✅ `/api/v1/` route working
- ✅ environment variables loaded from `.env`
- ✅ `APP_NAME`, `APP_VERSION`, and `APP_ENV` returned from API responses
- ✅ dedicated `/api/v1/health/` endpoint
- ✅ health check returns `healthy` status
- ✅ Swagger documentation shows all current endpoints

---

## ⏭️ Next Step

The next improvement should be to add the first **document upload route**.

Planned future route:

```text
POST /api/v1/documents/upload
```

Expected future responsibility:

- receive uploaded PDF or text files
- validate file type
- store files temporarily or permanently
- create document metadata
- prepare the file for text extraction and chunking
- later connect the upload process to background jobs

This will move RAGForge from a basic backend foundation toward the real RAG ingestion pipeline.

---

## 🧠 Project Philosophy

RAGForge follows one core principle:

```text
Do not only copy a tutorial.
Transform every step into a professional engineering project.
```

This means every important change should be:

- documented
- connected to an issue
- developed in a dedicated branch
- committed with a clear message
- reviewed through a pull request
- merged cleanly into `main`

---

## 📌 Commit Message Examples

Recommended commit messages:

```text
docs: define RAGForge project vision
chore: add initial backend requirements
chore: add environment example file
chore: add resources folder
setup: configure initial development environment
feat: add FastAPI foundation
docs: update README with FastAPI run instructions
feat: add routes and environment config
feat: add health check route
docs: update README for routes, env config and health check
```

---

## 👤 Author

**Dameur Mounir**

AI engineer and system builder focused on production-grade RAG, agentic AI systems, LangGraph workflows, vector databases, observability, and deployable AI architectures.

My objective is to build practical, robust, and scalable AI systems that can evolve from learning projects into real products, client solutions, and future agentic platforms.
