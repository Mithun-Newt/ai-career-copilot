from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, users, profiles, resumes, skills, roadmaps, career, ats, analytics

api_router = APIRouter()

# Include version 1 API endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(skills.router, prefix="/skills", tags=["skills"])
api_router.include_router(roadmaps.router, prefix="/roadmaps", tags=["roadmaps"])
api_router.include_router(career.router, prefix="/career", tags=["career"])
api_router.include_router(ats.router, prefix="/ats", tags=["ats"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
