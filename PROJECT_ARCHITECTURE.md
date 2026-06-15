# AI Career Copilot — Project Architecture

A comprehensive technical reference for developers, contributors, and reviewers.

---

## Table of Contents

- [High-Level Overview](#high-level-overview)
- [Frontend Architecture](#frontend-architecture)
- [Backend Architecture](#backend-architecture)
- [Database Design](#database-design)
- [AI Engine Design](#ai-engine-design)
- [Authentication Flow](#authentication-flow)
- [Request/Response Flows](#requestresponse-flows)
- [Environment and Configuration](#environment-and-configuration)
- [Docker Architecture](#docker-architecture)

---

## High-Level Overview

AI Career Copilot follows a **three-tier architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│  PRESENTATION TIER                                           │
│  React 18 + TypeScript + Vite SPA                           │
│  Framer Motion · Lucide Icons · TailwindCSS                  │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP/JSON REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  APPLICATION TIER                                            │
│  FastAPI (Python 3.11+)                                      │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────────┐  │
│  │  Auth   │  │ Resumes  │  │Roadmaps │  │ Career Coach │  │
│  │ Router  │  │  Router  │  │  Router │  │    Router    │  │
│  └────┬────┘  └────┬─────┘  └────┬────┘  └──────┬───────┘  │
│       │            │             │               │          │
│  ┌────▼────────────▼─────────────▼───────────────▼───────┐  │
│  │              Service Layer (Business Logic)            │  │
│  └──────────────────────┬─────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼─────────────────────────────────┐  │
│  │             Repository Layer (Data Access)             │  │
│  └──────────────────────┬─────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼─────────────────────────────────┐  │
│  │                  AI Engine Layer                       │  │
│  │  LangChain · LLM Providers · Web Search (DuckDuckGo)  │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │ SQLAlchemy ORM
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  DATA TIER                                                   │
│  PostgreSQL 15                                               │
│  Tables: users, resumes, roadmaps, roadmap_tasks,           │
│          career_messages, skill_analyses                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture

### Technology Decisions

| Decision | Rationale |
|---|---|
| **React + TypeScript** | Type safety reduces runtime bugs; strong ecosystem |
| **Vite** | ~10x faster HMR vs Create React App |
| **Framer Motion** | Production-quality animation primitives |
| **TailwindCSS** | Utility-first makes responsive design fast |
| **Axios** | Interceptor support for JWT token injection |

### Routing Strategy

The app uses **React Router v6** with a protected route pattern:

```
/                   → Landing (public)
/login              → Login (public)
/register           → Register (public)
/dashboard          → Dashboard (protected)
/resumes            → Resume Upload Hub (protected)
/roadmaps           → Career Roadmaps (protected)
/skills             → Skill Intelligence (protected)
/ats                → ATS Analyzer (protected)
/coach              → Career Coach (protected)
/profile            → User Profile (protected)
```

Protected routes check for a valid JWT in `localStorage`. If absent, they redirect to `/login`.

### State Management

State is managed **locally within components** using React's `useState` and `useEffect` hooks. No global state library (Redux/Zustand) is used — each page fetches its own data from the API on mount.

### API Client Pattern

```typescript
// src/api/client.ts
const apiClient = axios.create({ baseURL: 'http://localhost:8000/api/v1' });

// JWT injection interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

### Component Design Principles

- **Page components** own data fetching and state
- **UI components** are purely presentational
- **Framer Motion** `<motion.div>` wrappers add enter/exit animations to key elements
- **Error states** are inline — no global toast/modal system

---

## Backend Architecture

### Layer Responsibilities

```
Endpoint Layer  →  validates HTTP input, calls Service, returns HTTP response
Service Layer   →  orchestrates business logic, calls Repository and AI
Repository Layer→  executes database queries via SQLAlchemy sessions
AI Engine       →  orchestrates LLMs, prompt chains, web search
```

### Directory Map

```
app/
├── api/v1/endpoints/
│   ├── auth.py           # /auth/register, /auth/login
│   ├── users.py          # /users/me, /users/{id}
│   ├── resumes.py        # /resumes/upload, /resumes/my-resumes, /resumes/{id}
│   ├── roadmaps.py       # /roadmaps/generate, /roadmaps, /roadmaps/{id}, /roadmaps/tasks/{id}
│   ├── skills.py         # /skills/intelligence
│   ├── career_coach.py   # /career-coach/chat, /career-coach/history
│   └── ats.py            # /ats/analyze
│
├── services/
│   ├── auth_service.py       # Token creation, credential validation
│   ├── resume_service.py     # Upload handling, PDF parsing, deletion
│   ├── roadmap_service.py    # Roadmap generation, task management
│   ├── skill_service.py      # Skill gap analysis
│   ├── career_coach_service.py # Chat history, LLM context building
│   └── ats_service.py        # Resume vs JD comparison
│
├── repositories/
│   ├── user_repository.py
│   ├── resume_repository.py
│   ├── roadmap_repository.py
│   ├── roadmap_task_repository.py
│   └── base_repository.py    # Generic CRUD operations
│
├── ai/
│   ├── roadmap_generator.py  # LangChain roadmap generation with web search
│   ├── role_skill_mapper.py  # Dynamic role → required skills mapping
│   └── chat_engine.py        # Career coach chat with context injection
│
├── core/
│   ├── config.py             # Pydantic settings loaded from .env
│   ├── database.py           # SQLAlchemy engine and session factory
│   └── security.py           # JWT encoding/decoding, password hashing
│
├── models/                   # SQLAlchemy ORM table definitions
├── schemas/                  # Pydantic v2 request/response schemas
└── utils/
    ├── exceptions.py         # Custom exception types (EntityNotFoundError, ForbiddenError)
    └── file_utils.py         # File storage helpers
```

### Error Handling

Custom exception classes are raised in services and caught by FastAPI exception handlers:

```python
class EntityNotFoundError(Exception):    # → HTTP 404
class ForbiddenError(Exception):         # → HTTP 403
class ValidationError(Exception):        # → HTTP 422
```

A global fallback handler in `main.py` catches any unhandled exceptions and returns HTTP 500.

---

## Database Design

### Entity Relationship

```
users
  ├── id (UUID, PK)
  ├── email (unique)
  ├── hashed_password
  ├── full_name
  ├── current_role
  ├── target_role
  └── created_at

resumes
  ├── id (UUID, PK)
  ├── user_id (FK → users.id, CASCADE DELETE)
  ├── filename
  ├── file_path
  ├── file_size
  ├── parsed_data (JSONB — extracted skills, education, experience)
  └── uploaded_at

roadmaps
  ├── id (UUID, PK)
  ├── user_id (FK → users.id)
  ├── title
  ├── description
  ├── target_role
  └── created_at

roadmap_tasks
  ├── id (UUID, PK)
  ├── roadmap_id (FK → roadmaps.id, CASCADE DELETE)
  ├── title
  ├── description (contains serialized ||RESOURCES|| JSON suffix)
  ├── sequence (integer ordering)
  └── status ("pending" | "completed")

career_messages
  ├── id (UUID, PK)
  ├── user_id (FK → users.id)
  ├── role ("user" | "assistant")
  ├── content
  └── created_at
```

### Design Decisions

- **UUID primary keys** — avoids sequential ID enumeration attacks
- **CASCADE DELETE** — deleting a user cleans up all their resumes and roadmaps
- **JSONB for parsed_data** — flexible schema for AI-extracted resume metadata
- **No migrations enforced** — `Base.metadata.create_all()` runs on startup for simplicity

### Resource Serialization Pattern

To avoid a database schema migration for learning resources, resource URLs are embedded within the task `description` column using a structured separator:

```
{description text}

||RESOURCES||["https://youtube.com/...", "https://docs.python.org/..."]
```

The frontend parses this suffix client-side to render interactive resource links.

---

## AI Engine Design

### LLM Provider Fallback Chain

The system supports three LLM providers with automatic fallback:

```python
def get_llm():
    if GEMINI_API_KEY:   return ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    if OPENAI_API_KEY:   return ChatOpenAI(model="gpt-4o-mini")
    if GROQ_API_KEY:     return ChatGroq(model="llama-3.1-8b-instant")
    return None  # Falls back to web-search-only mode
```

### Roadmap Generation Pipeline

```
1. Web Search (DuckDuckGo HTML)
   └── Query: "{target_role} job description requirements key skills"
   └── Extract up to 8 result snippets

2. LLM Prompt Construction (ChatPromptTemplate)
   └── System: Expert career coach persona
   └── User: target_role + web_requirements + parsed_resume + skills

3. Structured Output (Pydantic Schema)
   └── RoadmapAIOutput → milestones → tasks → resources[]

4. Persistence
   └── Roadmap record → DB
   └── RoadmapTask records (with serialized resource URLs) → DB
```

### Role-Skill Intelligence

The `RoleSkillMapper` uses a broad static catalog covering 50+ career roles across:
- **Technology**: AI Engineer, Backend/Frontend Developer, DevOps, Data Scientist, Cybersecurity
- **Business**: Product Manager, Business Analyst, Financial Analyst, Marketing Manager
- **Creative**: UX/UI Designer, Content Writer, Graphic Designer, Video Producer
- **Healthcare**: Nurse, Healthcare Administrator, Medical Coder
- **Education**: Teacher, Instructional Designer, School Counselor
- **Legal & Finance**: Lawyer, Accountant, Compliance Officer
- **Operations**: Supply Chain Manager, Project Manager, Operations Analyst
- **Custom**: Any free-text role processed dynamically via LLM

For roles not in the catalog, the mapper queries the LLM with a structured prompt to generate a skill list dynamically.

### Career Coach Context Injection

The chat engine builds a rich context block for every conversation:

```python
context = f"""
User Profile: {user.full_name}, Current: {user.current_role}, Target: {user.target_role}
Resume Skills: {resume.parsed_data.get('skills', [])}
Active Roadmap: {roadmap.title} — {completed}/{total} tasks done
Conversation History: {last_10_messages}
"""
```

This context is injected as a system message before each LLM call, giving the AI full awareness of the user's situation.

---

## Authentication Flow

```
1. User submits email + password to POST /api/v1/auth/login
2. AuthService verifies password hash (bcrypt via Passlib)
3. JWT access token generated with 8-day expiry (configurable)
4. Token returned to frontend, stored in localStorage
5. All subsequent requests include: Authorization: Bearer {token}
6. FastAPI Depends(get_current_user) decodes token and injects user object
```

---

## Request/Response Flows

### Resume Upload Flow

```
Frontend: FormData (PDF file) → POST /api/v1/resumes/upload
Backend:
  1. ResumesEndpoint receives file
  2. ResumeService.upload_resume():
     a. Saves file to /uploads/{user_id}/{filename}
     b. Extracts text via PyMuPDF/pdfplumber
     c. Calls LLM to parse skills, education, experience into JSON
     d. Creates Resume record with parsed_data
  3. Returns resume schema with parsed metadata
```

### Roadmap Generation Flow

```
Frontend: {resume_id, target_role} → POST /api/v1/roadmaps/generate
Backend:
  1. RoadmapEndpoint validates request
  2. RoadmapService.generate_roadmap_for_user():
     a. Verifies resume ownership
     b. RoadmapGenerator.generate_roadmap():
        i.  Web search for target role requirements
        ii. LLM generates structured RoadmapAIOutput
        iii. Fallback to web-search-based template if LLM fails
     c. Persists Roadmap + RoadmapTask records
     d. Serializes resource URLs into task descriptions
  3. Returns roadmap with tasks populated
```

### ATS Analysis Flow

```
Frontend: {resume_id, job_description} → POST /api/v1/ats/analyze
Backend:
  1. ATSEndpoint validates inputs
  2. ATSService:
     a. Fetches resume parsed_data
     b. Constructs LLM prompt comparing skills vs JD requirements
     c. Returns match_score (%), matched_skills[], missing_skills[],
        suggestions[], and interview_prep questions
```

---

## Environment and Configuration

All configuration is loaded via a Pydantic `Settings` model from `backend/.env`:

```python
class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    BACKEND_CORS_ORIGINS: List[str]
    GEMINI_API_KEY: Optional[str]
    OPENAI_API_KEY: Optional[str]
    GROQ_API_KEY: Optional[str]
    DEBUG: bool
```

Settings are accessed as a singleton `settings` object injected via FastAPI's dependency system.

---

## Docker Architecture

```yaml
services:
  db:          # PostgreSQL 15 Alpine
    image: postgres:15-alpine
    volumes:   # Persistent data storage
      - postgres_data:/var/lib/postgresql/data
    healthcheck: pg_isready

  backend:     # FastAPI application
    build: ./backend
    depends_on: db (service_healthy)
    environment:
      - DATABASE_URL (connects to db service)
      - SECRET_KEY, ALGORITHM
      - AI API keys
```

The `depends_on` with `condition: service_healthy` ensures the backend only starts after PostgreSQL is ready to accept connections.

---

*Documentation maintained alongside the codebase. For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).*
