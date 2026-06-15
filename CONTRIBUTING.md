# Contributing to AI Career Copilot

Thank you for your interest in contributing! This guide will help you get started.

---

## 🏁 Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/career_copilot.git
   cd career_copilot
   ```
3. Set up the project following the [Installation guide in README.md](README.md#-installation)
4. Create a new feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 🌿 Branch Naming Convention

| Type | Format | Example |
|---|---|---|
| Feature | `feature/description` | `feature/linkedin-oauth` |
| Bug Fix | `fix/description` | `fix/resume-delete-cascade` |
| Docs | `docs/description` | `docs/api-reference` |
| Refactor | `refactor/description` | `refactor/skill-mapper` |

---

## 📝 Commit Message Style

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]
```

**Examples:**
```
feat(roadmaps): add learning resource links to each task
fix(auth): handle expired JWT tokens gracefully
docs(readme): add Docker setup section
refactor(services): extract resume parser into utility module
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## 🧪 Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend type check
cd frontend
npx tsc --noEmit

# Frontend build verification
npm run build
```

---

## 🔍 Code Standards

### Python (Backend)
- Follow **PEP 8** style guidelines
- Use **type hints** for all function signatures
- Add **docstrings** to all service and repository methods
- Keep endpoint handlers thin — move logic to services

### TypeScript (Frontend)
- Use **strict TypeScript** — avoid `any` types
- Prefer **functional components** with hooks
- Define **interfaces/types** in `src/types/` for shared data
- Keep page components focused — extract reusable UI into `src/components/`

---

## 🚀 Submitting a Pull Request

1. Ensure all tests pass and the build is clean
2. Update documentation if you changed any public APIs
3. Add an entry to [CHANGELOG.md](CHANGELOG.md) under `[Unreleased]`
4. Open a PR with:
   - A clear **title** describing the change
   - A **description** of what was changed and why
   - References to any related issues: `Closes #123`

---

## 💡 Ideas for Contributions

Check the [Future Improvements](README.md#-future-improvements) section in the README for a list of planned features. Issues labeled `good first issue` are great starting points.

---

## 📋 Code of Conduct

Be kind, collaborative, and constructive. We welcome contributors of all experience levels.
