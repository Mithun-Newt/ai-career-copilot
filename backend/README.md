# AI Career Copilot - Backend Architecture Skeleton

This is a production-grade FastAPI backend template structured with clean architecture principles, leveraging modern components like SQLAlchemy 2.0, Alembic, Pydantic V2, and clean dependency injection.

## Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # API Route controllers / handlers
│   │       └── router.py       # API V1 router aggregation
│   │
│   ├── core/
│   │   ├── config.py           # Application Settings (Pydantic Settings)
│   │   └── database.py         # SQLAlchemy Engine, Session, and Dependency helpers
│   │
│   ├── models/                 # SQLAlchemy 2.0 Database Models
│   ├── schemas/                # Pydantic Schemas / DTOs
│   ├── services/               # Pure business logic services
│   ├── repositories/           # Database access layer (Repository Pattern)
│   ├── ai/                     # LLM / LangChain / LangGraph components (future)
│   ├── utils/                  # Miscellaneous helpers / common utils
│   └── main.py                 # FastAPI app configuration, Lifespans, and Middleware
│
├── alembic/                    # DB Migrations folder
├── requirements.txt            # Package dependencies
├── .env.example                # Sample environment configuration
└── README.md                   # This file
```

## Getting Started

### Prerequisites
- Python 3.12
- PostgreSQL database

### Local Setup

1. **Clone & Navigate:**
   ```bash
   cd backend
   ```

2. **Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   ```bash
   copy .env.example .env
   # Update variables in .env as needed
   ```

5. **Run Database Migrations (Once DB is running):**
   ```bash
   alembic upgrade head
   ```

6. **Start the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend API will be available at `http://127.0.0.1:8000`.
   Interactive API documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.
