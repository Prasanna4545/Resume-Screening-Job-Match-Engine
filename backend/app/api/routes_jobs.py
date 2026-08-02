from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse
from app.services.skill_extractor import SkillExtractor

router = APIRouter(prefix="/jobs", tags=["Jobs"])
skill_extractor = SkillExtractor()

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    # Automatically extract skills from job description
    extracted_skills = skill_extractor.extract_skills(job_in.description)
    
    # Merge user-provided skills with extracted skills while preserving order and uniqueness
    combined_skills = list(dict.fromkeys(job_in.required_skills + extracted_skills))

    job = Job(
        title=job_in.title,
        description=job_in.description,
        required_skills=combined_skills,
        min_experience_years=job_in.min_experience_years,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.created_at.desc()).all()

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job
