from pydantic import BaseModel

class DashboardAnalyticsResponse(BaseModel):
    total_roadmaps: int
    completed_tasks_percentage: int
    average_ats_score: int
    total_career_messages: int
