# 🤖 AI Resume Screening & Job Matching System

A portfolio-grade, full-stack application for automated candidate resume screening and semantic job matching built with **FastAPI**, **React 18 + TypeScript**, **PostgreSQL**, **spaCy**, **sentence-transformers**, and **Alembic**, fully containerized with **Docker**.

---

## 🌟 Architecture & System Overview

```
┌────────────────────────────────────────────────────────┐
│                   React 18 + Vite UI                    │
│   (Upload Job, Upload Resumes, Ranking, Candidate Detail) │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP (Axios/Fetch)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI Backend API                   │
│   ├── REST Routes (/jobs, /resumes, /matching)          │
│   ├── Services (ResumeParser, SkillExtractor, Matcher)  │
│   └── Database Layer (SQLAlchemy 2.0 ORM + Alembic)     │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
              ▼                            ▼
┌───────────────────────────┐  ┌─────────────────────────┐
│ PostgreSQL 16 DB          │  │ ML / NLP Engine         │
│ (jobs, resumes, results)  │  │ (all-MiniLM-L6-v2 +     │
│                           │  │  spaCy + Skill Taxonomy)│
└───────────────────────────┘  └─────────────────────────┘
```

---

## 📐 Scoring Formula & Explainability

Matching scores ($0–100$) are calculated using a weighted 3-component engine:

$$\text{overall\_score} = 0.4 \times \text{semantic\_similarity} + 0.4 \times \text{skill\_match\_score} + 0.2 \times \text{experience\_match\_score}$$

- **Semantic Similarity (40%)**: Cosine similarity between `all-MiniLM-L6-v2` embeddings of job description & resume text.
- **Skill Match Score (40%)**: Ratio of required job skills matched (exact & fuzzy matching via `rapidfuzz`) against a curated 200+ item skill taxonomy.
- **Experience Match Score (20%)**: Domain-relevance gated scaling comparing candidate experience years against job minimum requirements.

Each sub-score is persisted separately in the `match_results` table along with Top Matched Skills, Top Missing Skills, and a Natural Language Diagnosis.

---

## 🚀 Quick Start (Docker)

```bash
# 1. Clone & set up environment
cp .env.example .env

# 2. Build & launch containers
docker-compose up --build
```

- **Frontend Application**: [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠 Local Development Setup

### Backend (Python 3.11+)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Seed demo dataset (3 jobs, 15 resumes, match results)
python app/seed_demo.py

# Run FastAPI dev server
uvicorn app.main:app --reload --port 8000
```

### Frontend (Node.js 18+)
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing

Run the full automated test suite (24 unit & integration tests):
```bash
cd backend
pytest -v tests
```

---

## 📊 Evaluation Report

For full accuracy benchmarks and manually-labeled ground truth pair evaluations, see [evaluation.md](file:///c:/Users/Prasanna/OneDrive/Desktop/AI%20Resume%20Screening%20&%20Job%20Matching%20System/evaluation.md).
