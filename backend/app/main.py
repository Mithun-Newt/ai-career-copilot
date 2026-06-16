import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks (e.g. database pool validation, initializing services)
    from app.core.database import engine, Base
    import app.models
    from sqlalchemy import text
    
    # Automatic database migrations for added columns (ensures existing local DB does not break)
    with engine.begin() as conn:
        try:
            # PostgreSQL syntax
            conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;"))
        except Exception:
            try:
                # SQLite fallback
                conn.execute(text("ALTER TABLE resumes ADD COLUMN is_active BOOLEAN DEFAULT TRUE;"))
            except Exception:
                pass
                
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown tasks (e.g. closing connections, cleaning up background workers)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend architecture skeleton for production-grade AI Career Copilot.",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
)

# CORS middleware configurations
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register central routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    """
    Root endpoint for system index check.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API. Access API docs at {settings.API_V1_STR}/docs."
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please try again later."}
    )
