from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str
    description: str
    required_skills: List[str] = []
    min_experience_years: int = 0

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
