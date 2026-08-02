from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.schemas.resume import ResumeResponse

class MatchRequest(BaseModel):
    job_id: str
    resume_ids: Optional[List[str]] = None  # If None, match against all resumes

class MatchResultResponse(BaseModel):
    id: str
    job_id: str
    resume_id: str
    overall_score: float
    skill_match_score: float
    experience_match_score: float
    semantic_similarity_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: Optional[str] = None
    created_at: datetime
    resume: Optional[ResumeResponse] = None

    model_config = ConfigDict(from_attributes=True)
