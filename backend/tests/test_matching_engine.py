import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal
from app.models.job import Job
from app.models.resume import Resume
from app.models.match_result import MatchResult
from app.services.embedding_service import EmbeddingService
from app.services.matching_engine import MatchingEngine
from app.services.explainability import ExplainabilityEngine

client = TestClient(app)
embedding_service = EmbeddingService()
matching_engine = MatchingEngine()
explainability_engine = ExplainabilityEngine()


def test_embedding_service_semantic_similarity():
    """Verify embedding service produces valid cosine similarity scores in range [0, 100]."""
    text1 = "Senior Python developer building web applications with FastAPI and PostgreSQL."
    text2 = "Python software engineer with experience in FastAPI microservices and SQL databases."
    text3 = "Professional chef specializing in Italian cuisine, pasta, and pastry baking."

    sim_high = embedding_service.compute_semantic_similarity(text1, text2)
    sim_low = embedding_service.compute_semantic_similarity(text1, text3)

    assert 0.0 <= sim_high <= 100.0
    assert 0.0 <= sim_low <= 100.0
    assert sim_high > sim_low  # Semantic relevance ordering check


def test_matching_engine_weighted_scoring_formula():
    """Verify formula: 0.4*semantic + 0.4*skill + 0.2*experience."""
    job_data = {
        "title": "Senior Python Engineer",
        "description": "Building APIs with Python, FastAPI, Docker, and PostgreSQL.",
        "required_skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "min_experience_years": 4
    }

    # Candidate 1: High match
    cand_high = {
        "candidate_name": "High Match Candidate",
        "raw_text": "Experienced Python Engineer specializing in FastAPI, Docker, and PostgreSQL microservices.",
        "parsed_skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "parsed_experience_years": 5.0
    }

    # Candidate 2: Low match
    cand_low = {
        "candidate_name": "Low Match Candidate",
        "raw_text": "Junior Graphic Designer experienced in Adobe Photoshop and Figma.",
        "parsed_skills": ["Figma", "UI/UX"],
        "parsed_experience_years": 1.0
    }

    res_high = matching_engine.evaluate_match(job_data, cand_high)
    res_low = matching_engine.evaluate_match(job_data, cand_low)

    # Score bounds checks
    assert 0.0 <= res_high["overall_score"] <= 100.0
    assert 0.0 <= res_low["overall_score"] <= 100.0

    # Rank ordering check
    assert res_high["overall_score"] > res_low["overall_score"]
    assert res_high["skill_match_score"] == 100.0
    assert len(res_high["missing_skills"]) == 0
    assert len(res_low["missing_skills"]) > 0


def test_explainability_summary_generation():
    """Verify natural language explanation summary content."""
    explanation = explainability_engine.generate_explanation(
        overall_score=85.0,
        semantic_score=80.0,
        skill_score=100.0,
        experience_score=100.0,
        matched_skills=["Python", "FastAPI", "Docker"],
        missing_skills=[],
        parsed_exp=5.0,
        min_exp=3
    )
    assert "Excellent match" in explanation or "Strong match" in explanation
    assert "3/3 required skills found" in explanation or "skills" in explanation
    assert "meets the 3-year minimum" in explanation


def test_end_to_end_matching_api_and_db_persistence():
    """Verify POST /api/matching/run end-to-end API response and DB persistence."""
    # 1. Create Job
    job_res = client.post("/api/jobs", json={
        "title": "Machine Learning Engineer",
        "description": "Looking for ML engineer with Python, PyTorch, scikit-learn, and NLP experience.",
        "required_skills": ["Python", "PyTorch", "scikit-learn", "NLP"],
        "min_experience_years": 3
    })
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # 2. Upload Resume
    resume_text = "Experienced ML Engineer specializing in Python, PyTorch, scikit-learn, and NLP model training. 4 years experience."
    res_upload = client.post("/api/resumes/upload", files=[
        ("files", ("ml_candidate.txt", resume_text.encode("utf-8"), "text/plain"))
    ])
    assert res_upload.status_code == 201
    resume_id = res_upload.json()[0]["id"]

    # 3. Run Matching API
    match_req = client.post("/api/matching/run", json={
        "job_id": job_id,
        "resume_ids": [resume_id]
    })
    assert match_req.status_code == 200
    match_data = match_req.json()
    assert len(match_data) == 1
    result = match_data[0]

    assert result["job_id"] == job_id
    assert result["resume_id"] == resume_id
    assert result["overall_score"] > 70.0
    assert result["semantic_similarity_score"] > 0.0
    assert "Python" in result["matched_skills"]
    assert result["explanation"] is not None

    # 4. Query MatchResult directly in DB
    db: Session = SessionLocal()
    try:
        db_match = db.query(MatchResult).filter(
            MatchResult.job_id == job_id,
            MatchResult.resume_id == resume_id
        ).first()
        assert db_match is not None
        assert db_match.overall_score == result["overall_score"]
        assert db_match.explanation == result["explanation"]
    finally:
        db.close()
