from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models.job import Job
from app.models.resume import Resume
from app.models.match_result import MatchResult
from app.schemas.matching import MatchRequest, MatchResultResponse
from app.services.matching_engine import MatchingEngine

router = APIRouter(prefix="/matching", tags=["Matching Engine"])
matching_engine = MatchingEngine()

@router.post("/run", response_model=List[MatchResultResponse])
def run_matching(request: MatchRequest, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    if request.resume_ids:
        resumes = db.query(Resume).filter(Resume.id.in_(request.resume_ids)).all()
    else:
        resumes = db.query(Resume).all()

    if not resumes:
        return []

    job_data = {
        "title": job.title,
        "description": job.description,
        "required_skills": job.required_skills or [],
        "min_experience_years": job.min_experience_years
    }

    results = []
    for resume in resumes:
        resume_data = {
            "candidate_name": resume.candidate_name,
            "raw_text": resume.raw_text,
            "parsed_skills": resume.parsed_skills or [],
            "parsed_experience_years": resume.parsed_experience_years,
            "parsed_education": resume.parsed_education or []
        }

        eval_res = matching_engine.evaluate_match(job_data, resume_data)

        # Check if existing match result exists
        match = db.query(MatchResult).filter(
            MatchResult.job_id == job.id,
            MatchResult.resume_id == resume.id
        ).first()

        if not match:
            match = MatchResult(
                job_id=job.id,
                resume_id=resume.id
            )
            db.add(match)

        match.overall_score = eval_res["overall_score"]
        match.skill_match_score = eval_res["skill_match_score"]
        match.experience_match_score = eval_res["experience_match_score"]
        match.semantic_similarity_score = eval_res["semantic_similarity_score"]
        match.matched_skills = eval_res["matched_skills"]
        match.missing_skills = eval_res["missing_skills"]
        match.explanation = eval_res["explanation"]

        results.append(match)

    db.commit()
    for r in results:
        db.refresh(r)

    # Fetch with resume relationship populated for response schema
    results = (
        db.query(MatchResult)
        .options(joinedload(MatchResult.resume))
        .filter(MatchResult.job_id == job.id)
        .order_by(MatchResult.overall_score.desc())
        .all()
    )
    return results

@router.get("/results/{job_id}", response_model=List[MatchResultResponse])
def get_job_match_results(job_id: str, db: Session = Depends(get_db)):
    results = (
        db.query(MatchResult)
        .options(joinedload(MatchResult.resume))
        .filter(MatchResult.job_id == job_id)
        .order_by(MatchResult.overall_score.desc())
        .all()
    )
    return results

@router.get("/results/{job_id}/{resume_id}", response_model=MatchResultResponse)
def get_candidate_match_detail(job_id: str, resume_id: str, db: Session = Depends(get_db)):
    result = (
        db.query(MatchResult)
        .options(joinedload(MatchResult.resume))
        .filter(MatchResult.job_id == job_id, MatchResult.resume_id == resume_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Match result not found for candidate")
    return result
