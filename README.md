# 🛠️ RAGForge

**RAGForge** is a production-oriented **Retrieval-Augmented Generation** platform designed to build, test, and evolve modular RAG systems step by step.

This project is not a simple notebook or a small demo. It is a long-term AI engineering project focused on building a clean, scalable, and professional RAG backend architecture using real engineering practices: **milestones, issues, branches, pull requests, documentation, testing, and deployment**.

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
Branch: setup/initial-ragforge-environment
```

This first milestone focuses on preparing the repository, defining the project vision, setting up the development environment, and creating the first professional project structure.

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

- `libpq-dev` is needed later for PostgreSQL-related Python packages.
- `gcc` is needed to compile some Python dependencies.
- `python3-dev` provides Python development headers needed by some packages.

---

## 📦 Install Python using Miniconda

### 1. Download and install Miniconda

Download and install Miniconda from the official website.

After installation, restart your terminal or open a new WSL Ubuntu terminal.

---

### 2. Create a new Conda environment

Create a dedicated environment for this project:

```bash
conda create -n ragforge python=3.11
```

---

### 3. Activate the environment

```bash
conda activate ragforge
```

After activation, you should see something like this in your terminal:

```text
(ragforge) dameurmounir@DESKTOP-XXXX:~/development/tech/ai-engineering/projects/rag/ragforge$
```

---

### 4. Verify Python version

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

Example:

```text
dameurmounir@DESKTOP-XXXX:~/development/tech/ai-engineering/projects/rag/ragforge
$
```

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

If the repository is already cloned, only enter the folder:

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
```

### Why these packages?

- `fastapi` is the backend web framework.
- `uvicorn[standard]` is the ASGI server used to run the FastAPI application.
- `python-multipart` will be used later for file upload support.

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
OPENAI_API_KEY=""
```

For now, you can leave `OPENAI_API_KEY` empty.

Later, when LLM integration is added, you can add your real API key inside `.env`.

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

## 🗂️ Initial Project Structure

The current repository structure is:

```text
ragforge/
├── resources/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

### Why `resources/`?

The `resources/` folder is reserved for small project support files such as:

- 🖼️ screenshots
- 📊 diagrams
- 📄 small sample files
- 🧾 documentation resources

The `.gitkeep` file is used because Git does not track empty folders.

---

## ▶️ How to Use the Project Now

At the current stage, the project is still in the environment setup phase.

There is no FastAPI application to run yet.

For now, the correct usage is:

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

### 5. Check Git status

```bash
git status
```

The project is now ready for the next milestone: building the first FastAPI backend.

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

```bash
git checkout -b setup/initial-ragforge-environment
```

### 4. Make changes

Edit files such as:

```text
README.md
requirements.txt
.env.example
.gitignore
resources/.gitkeep
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

```bash
git commit -m "chore: add initial RAGForge environment setup"
```

### 8. Push the branch

```bash
git push -u origin setup/initial-ragforge-environment
```

### 9. Open a Pull Request

Open a Pull Request on GitHub and link it to the issue:

```text
Closes #1
```

---

## 🧩 Current Work Completed

The current branch includes the first project setup work:

- ✅ Created the initial `README.md`
- ✅ Defined the RAGForge project vision
- ✅ Added requirements and installation instructions
- ✅ Created the Conda environment with Python 3.11
- ✅ Added `requirements.txt`
- ✅ Installed FastAPI, Uvicorn, and python-multipart
- ✅ Created `.env.example`
- ✅ Prepared local `.env` usage
- ✅ Protected `.env` using `.gitignore`
- ✅ Created the `resources/` folder
- ✅ Added `.gitkeep` to keep the empty folder in Git
- ✅ Customized the WSL terminal prompt for better readability
- ✅ Prepared the repository for milestone-based development

---

## 🗺️ Milestone Roadmap

RAGForge will be developed step by step through professional milestones.

| Milestone | Focus | Expected Result |
|---|---|---|
| M1 | 🧱 Project Bootstrap & Environment | README, environment, Git workflow, initial structure |
| M2 | ⚙️ FastAPI Backend Foundation | Running FastAPI app with basic routes |
| M3 | 📄 File Upload & Processing | Upload and process documents |
| M4 | 🗄️ Database & Document Models | Store metadata, documents, and chunks |
| M5 | 🔁 Data Pipeline Checkpoint | Stable ingestion pipeline |
| M6 | 🔎 RAG Core | Embeddings, vector search, retrieval, answer generation |
| M7 | 🐳 Deployment & Workers | Docker, PostgreSQL, PgVector, Celery, Flower |

---

## 🧱 Current Milestone: M1

### Goal

Prepare the repository and development environment before writing the main backend code.

### Current focus

- project vision
- requirements
- environment setup
- GitHub workflow
- first branch
- first issue
- first pull request

### Definition of Done

Milestone 1 will be considered complete when the project contains:

- ✅ professional `README.md`
- ✅ `requirements.txt`
- ✅ `.env.example`
- ✅ `.gitignore`
- ✅ `resources/.gitkeep`
- ✅ Conda environment
- ✅ GitHub issue
- ✅ GitHub branch
- ✅ Pull Request merged into `main`

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
```

---

## 👤 Author

**Dameur Mounir**

AI engineer, teacher, and system builder focused on production-grade RAG, agentic AI systems, LangGraph architectures, vector databases, observability, and real-world AI deployment.

This project is part of my long-term roadmap to master, design, and build robust AI systems capable of powering future autonomous agents, educational platforms, and enterprise-ready AI products.
