<div align="center">

<h1>🚀 AI Career Copilot</h1>

<p><strong>Your personalized AI-powered career intelligence platform.</strong><br/>
Resume parsing · Skill gap analysis · Dynamic roadmaps · ATS scoring · AI career coaching</p>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org)
[![LangChain](https://img.shields.io/badge/LangChain-Enabled-1C3C3C?style=flat-square)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Environment Variables](#environment-variables)
  - [Database Setup](#database-setup)
- [Running Locally](#-running-locally)
- [Docker Setup](#-docker-setup)
- [API Documentation](#-api-documentation)
- [Future Improvements](#-future-improvements)
- [Learning Outcomes](#-learning-outcomes)
- [Author](#-author)

---

## 🌟 Overview

**AI Career Copilot** is a full-stack, production-grade career intelligence platform that leverages Generative AI, LangChain, and LLMs to help users of **any profession** accelerate their career growth.

Whether you're a nurse transitioning to healthcare management, a teacher moving into EdTech, a developer aiming for an AI role, or a fresh graduate planning your first career path — AI Career Copilot provides deeply personalized, AI-generated guidance every step of the way.

> Built for **everyone** — not just engineers.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **JWT Authentication** | Secure registration, login, and token-based session management |
| 📄 **Resume Upload & Parsing** | Upload PDF resumes; AI extracts skills, experience, and education |
| 🗺️ **AI Roadmap Generator** | LLM generates a fully personalized, phased learning roadmap for any target role |
| 📚 **Learning Resources** | Each roadmap task includes curated YouTube tutorials, official docs, and guides |
| 🧠 **Skill Intelligence** | Matches your resume skills against industry requirements for any career role |
| 🎯 **ATS Resume Analyzer** | Compares resume against job descriptions for match score and missing skills |
| 💬 **AI Career Coach** | Conversational chat assistant with full resume, roadmap, and profile context |
| 🤖 **Multi-Model AI Support** | Choose between Google Gemini, Groq (LLaMA), or OpenAI for AI-powered features |
| 📊 **Dashboard Analytics** | At-a-glance stats: roadmaps created, task completion %, ATS scores, coach messages |
| 🔍 **Dynamic Role Support** | Supports hundreds of career roles — technical, creative, business, healthcare, and more |
| 🗑️ **Resume & Roadmap Management** | Upload multiple resumes per account, delete individually, manage multiple roadmaps |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + TS)                     │
│  Vite · Framer Motion · Lucide Icons · TailwindCSS · Axios  │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP REST API
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + Python)                   │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Auth &  │  │ Resume   │  │ Roadmap  │  │  Career    │  │
│  │  JWT     │  │ Service  │  │ Service  │  │  Coach     │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│                         │                                    │
│              ┌──────────┴──────────┐                        │
│              │   AI Engine Layer   │                        │
│              │  LangChain · LLMs   │                        │
│              │  Web Search (DDG)   │                        │
│              └─────────────────────┘                        │
└────────────────────────────┬────────────────────────────────┘
                             │ SQLAlchemy ORM
                             ▼
                  ┌──────────────────────┐
                  │  PostgreSQL Database  │
                  └──────────────────────┘
```

See [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) for an in-depth breakdown of component design, data models, and request/response flows.

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.11+** | Core backend language |
| **FastAPI** | High-performance async REST API framework |
| **SQLAlchemy** | ORM for database models and queries |
| **Alembic** | Database migration management |
| **PostgreSQL** | Relational database |
| **LangChain** | LLM orchestration, prompt chaining, structured output |
| **Pydantic v2** | Data validation and schema definitions |
| **PyJWT / Passlib** | JWT token auth and bcrypt password hashing |
| **httpx** | Async HTTP client for live web search |
| **PyMuPDF / pdfplumber** | PDF text extraction for resume parsing |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** | UI component library |
| **TypeScript** | Type-safe JavaScript |
| **Vite** | Blazing-fast build tooling and dev server |
| **Framer Motion** | Production-quality animations and transitions |
| **Lucide React** | Consistent icon system |
| **Axios** | HTTP API communication client |
| **TailwindCSS** | Utility-first CSS framework |

### AI / LLM Providers (any one required)
| Provider | Model | Environment Key |
|---|---|---|
| **Google Gemini** | `gemini-1.5-flash` | `GEMINI_API_KEY` |
| **Groq** | `llama-3.1-8b-instant` | `GROQ_API_KEY` |
| **OpenAI** | `gpt-4o-mini` | `OPENAI_API_KEY` |

---

## 📁 Project Structure

```
career_copilot/
├── backend/
│   ├── app/
│   │   ├── ai/                     # AI engine: roadmap generator, skill mapper
│   │   │   ├── roadmap_generator.py
│   │   │   ├── role_skill_mapper.py
│   │   │   └── chat_engine.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/      # Route handlers (auth, resumes, roadmaps, skills, coach)
│   │   │       └── router.py
│   │   ├── core/                   # App config, database engine, security utilities
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── repositories/           # Database query abstraction layer
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── services/               # Business logic services
│   │   ├── utils/                  # Helper utilities and custom exceptions
│   │   └── main.py                 # FastAPI application entry point
│   ├── alembic/                    # Database migration scripts
│   ├── uploads/                    # User-uploaded resume files (gitignored)
│   ├── .env.example                # Environment variable template
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/                    # Axios client and API helpers
│   │   ├── components/             # Reusable UI components (Navbar, etc.)
│   │   ├── layouts/                # Page layout wrappers
│   │   ├── pages/                  # Full page components
│   │   │   ├── Landing.tsx         # Public landing page
│   │   │   ├── Dashboard.tsx       # Analytics dashboard
│   │   │   ├── ResumeUpload.tsx    # Resume management hub
│   │   │   ├── RoadmapDashboard.tsx# AI roadmap viewer/generator
│   │   │   ├── SkillsDashboard.tsx # Skill intelligence analysis
│   │   │   ├── ATSAnalyzer.tsx     # ATS resume scorer
│   │   │   ├── CareerCoach.tsx     # AI coach chat interface
│   │   │   └── Profile.tsx         # User profile settings
│   │   ├── types/                  # Shared TypeScript type definitions
│   │   └── App.tsx                 # Root router with protected routes
│   ├── index.html
│   └── vite.config.ts
│
├── docker-compose.yml              # Docker Compose for backend + DB
├── .gitignore
├── README.md
├── PROJECT_ARCHITECTURE.md         # Deep-dive technical architecture docs
├── CONTRIBUTING.md                 # Contribution guidelines
└── CHANGELOG.md                    # Version history and release notes
```

---

## 📸 Screenshots

> Live demo screenshots will be added here post-deployment.

| Feature | Preview |
|---|---|
| 🏠 Landing Page | *Coming soon* |
| 📊 Dashboard | *Coming soon* |
| 🗺️ AI Roadmap | *Coming soon* |
| 🎯 ATS Analyzer | *Coming soon* |
| 💬 Career Coach | *Coming soon* |

---

## ⚙️ Installation

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and **npm**
- **PostgreSQL 15+** (local or via Docker)
- At least **one** AI API key:
  - 🆓 [Groq (free tier)](https://console.groq.com)
  - 🆓 [Google Gemini (free tier)](https://makersuite.google.com/app/apikey)
  - 💳 [OpenAI](https://platform.openai.com/api-keys)

---

### Backend Setup

```bash
# 1. Navigate into the backend directory
cd backend

# 2. Create a Python virtual environment
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — macOS / Linux
source venv/bin/activate

# 3. Install all Python dependencies
pip install -r requirements.txt

# 4. Copy the environment template
cp .env.example .env
# Then open .env and fill in your values
```

---

### Frontend Setup

```bash
# 1. Navigate into the frontend directory
cd frontend

# 2. Install Node.js dependencies
npm install
```

---

### Environment Variables

Edit `backend/.env` with the following variables:

```env
# Application
PROJECT_NAME="AI Career Copilot"
API_V1_STR="/api/v1"
DEBUG=true

# CORS — update with your frontend URL in production
BACKEND_CORS_ORIGINS=["http://localhost:5173"]

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/career_copilot
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=career_copilot
POSTGRES_PORT=5432

# Security — CHANGE THIS IN PRODUCTION to a cryptographically random string
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# AI Provider — add at least ONE:
GROQ_API_KEY=gsk_...            # Free at console.groq.com
GEMINI_API_KEY=AIza...          # Free at makersuite.google.com
OPENAI_API_KEY=sk-...           # Paid at platform.openai.com
```

> **Priority:** The system auto-selects: Gemini → OpenAI → Groq. Add any one.

---

### Database Setup

Ensure PostgreSQL is running and create the database:

```sql
CREATE DATABASE career_copilot;
```

All tables are automatically created on first backend startup — no manual migration required.

---

## 🏃 Running Locally

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate          # Windows
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

| Service | URL |
|---|---|
| 🌐 Frontend App | http://localhost:5173 |
| ⚡ Backend API | http://localhost:8000 |
| 📖 Swagger Docs | http://localhost:8000/api/v1/docs |
| 📗 ReDoc | http://localhost:8000/api/v1/redoc |

---

## 🐳 Docker Setup

Run the full backend + PostgreSQL stack:

```bash
# From the project root directory
docker-compose up --build
```

This will:
1. Start a **PostgreSQL 15** container with persistent volume storage
2. Build and launch the **FastAPI backend** container
3. Expose the API at `http://localhost:8000`

> **Note:** Run the React frontend locally using `npm run dev` pointing to `http://localhost:8000`.

```bash
# Stop containers
docker-compose down

# Stop and remove all data volumes
docker-compose down -v
```

---

## 📖 API Documentation

Interactive Swagger UI available at `http://localhost:8000/api/v1/docs` (when `DEBUG=true`).

### Endpoint Groups

| Route Prefix | Description |
|---|---|
| `/api/v1/auth` | Registration, login, JWT tokens |
| `/api/v1/users` | User profile management |
| `/api/v1/resumes` | Upload, list, parse, delete resumes |
| `/api/v1/roadmaps` | AI generate, list, delete roadmaps; update tasks |
| `/api/v1/skills` | Skill intelligence and role gap matching |
| `/api/v1/career-coach` | AI chat and conversation history |
| `/api/v1/ats` | ATS resume vs job description analysis |

### Key Endpoints

```
POST   /api/v1/auth/register           — Create a new account
POST   /api/v1/auth/login              — Get JWT access token

POST   /api/v1/resumes/upload          — Upload and parse a PDF resume
GET    /api/v1/resumes/my-resumes      — List user's uploaded resumes
DELETE /api/v1/resumes/{id}            — Delete a resume

POST   /api/v1/roadmaps/generate       — AI-generate a new career roadmap
GET    /api/v1/roadmaps                — List all saved roadmaps
DELETE /api/v1/roadmaps/{id}           — Delete a roadmap
PATCH  /api/v1/roadmaps/tasks/{id}     — Toggle task completion status

POST   /api/v1/career-coach/chat       — Send a message to the AI coach
GET    /api/v1/career-coach/history    — Retrieve conversation history

POST   /api/v1/ats/analyze             — Analyze resume vs job description
GET    /api/v1/skills/intelligence     — Get skill gap analysis for a role
```

---

## 🔮 Future Improvements

- [ ] **OAuth Integration** — Google / LinkedIn sign-in
- [ ] **Live Job Board Integration** — LinkedIn Jobs or Indeed API for live postings
- [ ] **AI Resume Builder** — Generate optimized resumes from your profile
- [ ] **Interview Prep Mode** — AI-generated mock questions per target role
- [ ] **Progress Notifications** — Email alerts for roadmap milestone completion
- [ ] **Team / Cohort Mode** — Group career tracking for bootcamps or teams
- [ ] **Mobile App** — React Native version of the platform
- [ ] **Multimodal Resume Support** — Word document (.docx) parsing
- [ ] **Analytics Dashboard** — Track learning velocity and skill evolution over time
- [ ] **Alembic Migrations** — Full migration pipeline for production deployments

---

## 🎓 Learning Outcomes

This project demonstrates practical, production-level full-stack engineering:

- **Full-Stack Architecture** — REST API design, service/repository layering, React SPA routing
- **LLM Integration** — Structured output prompting, multi-provider fallback, context injection
- **LangChain Patterns** — `ChatPromptTemplate`, Pydantic schema output, prompt engineering
- **Auth Systems** — Stateless JWT authentication with bcrypt password hashing
- **Database Design** — SQLAlchemy ORM, relational modeling, UUID PKs, cascade deletes
- **AI Product Design** — UX around LLM latency, error states, streaming responses
- **Docker & DevOps** — Multi-service Compose, environment management, health checks
- **TypeScript + React** — Strongly-typed component design, custom hooks, protected routing

---

## 👤 Author

**Mithun** — Full-Stack AI Developer

> Built from scratch with a passion for AI, great UX, and clean architecture.

- 🌐 GitHub: [@Mithun-Newt](https://github.com/Mithun-Newt)
- 💼 LinkedIn: [linkedin.com/in/mithun-venaktesan](https://www.linkedin.com/in/mithun-venkatesan-78346528b/)

---

<div align="center">
  <sub>⭐ If this project helped or inspired you, please star it on GitHub — it means the world!</sub>
</div>
