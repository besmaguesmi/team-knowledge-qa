# Team Knowledge Base Q&A
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![CI](https://github.com/YOUR_USERNAME/team-knowledge-qa/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/team-knowledge-qa/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://www.docker.com/)

A production‑ready RAG (Retrieval‑Augmented Generation) system that answers questions **only from your uploaded documents** – no hallucinations.
Built with FastAPI, ChromaDB, Groq, and Streamlit.

## Features

- Upload PDF or TXT documents
- Ask natural language questions
- Answers are grounded **only** in your documents – the LLM refuses if the answer isn't there
- Shows which source documents were used
- Full containerisation with Docker Compose
- REST API (FastAPI) + clean UI (Streamlit)
- CI pipeline with GitHub Actions

## Quick Start

### Project structure
```
.
├── .github/workflows/ci.yml # CI pipeline
├── backend/
│ ├── Dockerfile
│ ├── requirements.txt
│ └── app/
│ ├── config.py # Environment variables
│ ├── main.py # FastAPI endpoints (/upload, /ask)
│ ├── models.py # Pydantic schemas
│ └── rag_engine.py # Chunking, embeddings, vector DB, LLM call
├── frontend/
│ ├── Dockerfile
│ ├── requirements.txt
│ └── streamlit_app.py # Streamlit UI
├── docker-compose.yml
├── .env.example
├── README.md
└── doc.md # Detailed learning guide
```

### Prerequisites
- Docker and Docker Compose (recommended) **or** Python 3.10+
- A [Groq API key](https://console.groq.com) (free tier – 30 requests/min)

### Setup (using Docker Compose)

```
git clone https://github.com/YOUR_USERNAME/team-knowledge-qa.git
cd team-knowledge-qa
# Edit .env and add your GROQ_API_KEY
docker-compose up --build
```
Open http://localhost:8501 in your browser.

### Manual setup (without Docker)
#### Backend
```
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env   # add GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

#### Frontend (in a new terminal)
```
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BACKEND_URL=http://localhost:8000   # or set in .env
streamlit run streamlit_app.py
```

#### Run tests
```
pip install pytest
pytest tests/
``` 
