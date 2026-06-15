import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()


@router.get("", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def check_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Check the health of the application and its core dependencies (Database connection).
    """
    start_time = time.time()
    
    # Check Database connection viability
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )
        
    duration = time.time() - start_time
    
    return {
        "status": "healthy",
        "database": "connected",
        "latency_seconds": round(duration, 4)
    }
