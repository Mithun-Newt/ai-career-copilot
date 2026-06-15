# Changelog

All notable changes to **AI Career Copilot** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- OAuth integration (Google / LinkedIn sign-in)
- Live job board integration (LinkedIn Jobs / Indeed API)
- AI resume builder from user profile data
- Interview prep mode with AI-generated mock questions
- Mobile app (React Native)

---

## [1.0.0] — 2026-06-15

### Added

#### Core Features
- JWT-based user authentication (register, login, token refresh)
- PDF resume upload with AI-powered parsing (skills, education, experience extraction)
- AI Career Roadmap Generator using LangChain structured output + DuckDuckGo live web search
- Learning resources integration: each roadmap task includes curated YouTube tutorials and official documentation links
- Skill Intelligence Dashboard: gap analysis comparing resume skills against any target role
- ATS Resume Analyzer: match score, missing skills, and interview preparation suggestions
- AI Career Coach: conversational chat with full user profile, resume, and roadmap context
- Multi-model AI support: Google Gemini, Groq (LLaMA 3.1), OpenAI (auto-selected by available key)
- In-app AI model switcher in Career Coach: users can change AI provider mid-session
- Analytics Dashboard: roadmaps count, task completion %, average ATS score, coach message count

#### Role Support
- Expanded role coverage from 3 hardcoded engineering roles to 50+ roles across:
  - Technology (AI Engineer, Backend Developer, DevOps Engineer, Data Scientist, Cybersecurity Analyst)
  - Business (Product Manager, Business Analyst, Financial Analyst, Marketing Manager, Sales Representative)
  - Creative (UX/UI Designer, Content Writer, Graphic Designer, Video Producer)
  - Healthcare (Nurse, Healthcare Administrator, Medical Coder)
  - Education (Teacher, Instructional Designer, School Counselor)
  - Legal & Finance (Lawyer, Accountant, Compliance Officer)
  - Operations (Supply Chain Manager, Project Manager, HR Manager)
  - Custom: any free-text role processed dynamically via LLM

#### Resume Management
- Upload multiple resumes per account
- Delete individual resumes with account scoping
- Parsed skills and metadata stored as JSONB

#### Roadmap Management
- Generate multiple roadmaps per user
- Delete individual roadmaps
- Task completion toggling with visual progress tracking
- Milestone-grouped task display with progress percentage

### Technical
- FastAPI backend with service/repository pattern
- SQLAlchemy ORM with PostgreSQL (UUID primary keys, cascade deletes)
- LangChain `with_structured_output` for Pydantic schema enforcement
- Resource URL serialization via `||RESOURCES||` suffix in task descriptions (no DB migration required)
- DuckDuckGo HTML search for real-time role requirements
- React 18 + TypeScript + Vite frontend
- Framer Motion animations throughout the UI
- Docker Compose setup for backend + PostgreSQL
- Comprehensive `.env.example` with all required variables documented

---

## [0.1.0] — 2026-06-01 (Initial Development)

### Added
- Project scaffolding: FastAPI backend + React/TypeScript frontend
- Basic JWT authentication flow
- Initial database models (User, Resume, Roadmap, RoadmapTask)
- Hardcoded roadmap for 3 engineering roles (AI Engineer, Data Scientist, Backend Developer)
- Basic resume upload without deletion support
- Initial career coach chat (no model switcher)
- Docker Compose configuration

---

[Unreleased]: https://github.com/Mithun-Newt/career_copilot/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Mithun-Newt/career_copilot/releases/tag/v1.0.0
[0.1.0]: https://github.com/Mithun-Newt/career_copilot/releases/tag/v0.1.0
