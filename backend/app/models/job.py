import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[list] = mapped_column(JSON, default=list)
    min_experience_years: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    match_results = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")
