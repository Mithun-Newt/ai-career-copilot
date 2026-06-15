from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.roadmap import Roadmap
from app.models.roadmap_task import RoadmapTask
from app.models.ats_analysis import ATSAnalysis
from app.models.career_chat import CareerChat
from app.models.career_message import CareerMessage
from app.schemas.analytics import DashboardAnalyticsResponse

router = APIRouter()

@router.get(
    "/dashboard",
    response_model=DashboardAnalyticsResponse,
    summary="Get user dashboard analytics"
)
def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> DashboardAnalyticsResponse:
    # 1. Total roadmaps
    total_roadmaps = db.query(Roadmap).filter(Roadmap.user_id == current_user.id).count()

    # 2. Completed tasks percentage
    # Find all tasks for the user's roadmaps
    roadmaps_query = db.query(Roadmap.id).filter(Roadmap.user_id == current_user.id).subquery()
    total_tasks = db.query(RoadmapTask).filter(RoadmapTask.roadmap_id.in_(roadmaps_query)).count()
    completed_tasks = db.query(RoadmapTask).filter(
        RoadmapTask.roadmap_id.in_(roadmaps_query),
        RoadmapTask.status == "completed"
    ).count()
    
    completed_tasks_percentage = 0
    if total_tasks > 0:
        completed_tasks_percentage = int((completed_tasks / total_tasks) * 100)

    # 3. Average ATS score
    avg_ats_score_result = db.query(func.avg(ATSAnalysis.ats_score)).filter(ATSAnalysis.user_id == current_user.id).scalar()
    average_ats_score = int(avg_ats_score_result) if avg_ats_score_result else 0

    # 4. Total career messages (from the user)
    chats_query = db.query(CareerChat.id).filter(CareerChat.user_id == current_user.id).subquery()
    total_career_messages = db.query(CareerMessage).filter(
        CareerMessage.chat_id.in_(chats_query),
        CareerMessage.role == "user"
    ).count()

    return DashboardAnalyticsResponse(
        total_roadmaps=total_roadmaps,
        completed_tasks_percentage=completed_tasks_percentage,
        average_ats_score=average_ats_score,
        total_career_messages=total_career_messages
    )
