import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    skill_match_score: Mapped[float] = mapped_column(Float, nullable=False)
    experience_match_score: Mapped[float] = mapped_column(Float, nullable=False)
    semantic_similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    matched_skills: Mapped[list] = mapped_column(JSON, default=list)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    job = relationship("Job", back_populates="match_results")
    resume = relationship("Resume", back_populates="match_results")
