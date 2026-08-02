from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ResumeBase(BaseModel):
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    parsed_skills: List[str] = []
    parsed_experience_years: float = 0.0
    parsed_education: List[str] = []

class ResumeCreate(ResumeBase):
    raw_text: str
    file_path: Optional[str] = None

class ResumeResponse(ResumeBase):
    id: str
    raw_text: str
    file_path: Optional[str] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
