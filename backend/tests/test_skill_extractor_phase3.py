import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal
from app.models.job import Job
from app.models.resume import Resume
from app.services.skill_extractor import SkillExtractor

client = TestClient(app)
extractor = SkillExtractor()


def test_job_creation_skill_extraction_db_persistence():
    """Verify POST /api/jobs auto-extracts skills from description and persists to DB."""
    job_payload = {
        "title": "Backend Python Lead",
        "description": "We are seeking a Backend Engineer skilled in Python, FastAPI, PostgreSQL, Docker, and AWS. Must have experience with microservices.",
        "required_skills": ["Python"],
        "min_experience_years": 5
    }
    response = client.post("/api/jobs", json=job_payload)
    assert response.status_code == 201
    data = response.json()
    job_id = data["id"]
    
    # Query database directly to confirm DB persistence
    db: Session = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.id == job_id).first()
        assert db_job is not None
        assert "Python" in db_job.required_skills
        assert "FastAPI" in db_job.required_skills
        assert "PostgreSQL" in db_job.required_skills
        assert "Docker" in db_job.required_skills
        assert "AWS" in db_job.required_skills
    finally:
        db.close()


def test_ambiguous_short_token_false_positives():
    """Verify false positives are avoided for C, C++, C#, Go, R."""
    # 1. "Go to the market" vs "Go microservices"
    ambiguous_go_text = "I like to go to the store and buy groceries."
    valid_go_text = "Experienced in building Go microservices and Golang APIs."
    assert "Go" not in extractor.extract_skills(ambiguous_go_text)
    assert "Go" in extractor.extract_skills(valid_go_text)

    # 2. "C++" vs "C" vs "C#"
    cpp_text = "Strong proficiency in C++ programming."
    cs_text = "Built enterprise applications with C# and .NET."
    c_text = "Developed embedded systems using C language."

    cpp_skills = extractor.extract_skills(cpp_text)
    cs_skills = extractor.extract_skills(cs_text)
    c_skills = extractor.extract_skills(c_text)

    assert "C++" in cpp_skills and "C" not in cpp_skills
    assert "C#" in cs_skills and "C" not in cs_skills
    assert "C" in c_skills

    # 3. "R" vs "R&D"
    rd_text = "Worked in R&D department on product strategy."
    r_stats_text = "Statistical modeling using R language and Python."

    assert "R" not in extractor.extract_skills(rd_text)
    assert "R" in extractor.extract_skills(r_stats_text)


def test_taxonomy_coverage_breakdown():
    """Verify skills taxonomy count and categorizations."""
    taxonomy = extractor.taxonomy
    assert len(taxonomy) >= 150
    
    # Verify core SWE categories exist
    languages = {"Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust"}
    frameworks = {"React", "FastAPI", "Django", "Next.js", "Spring Boot"}
    databases = {"PostgreSQL", "MongoDB", "Redis", "MySQL"}
    cloud = {"AWS", "Docker", "Kubernetes", "Azure"}

    assert languages.issubset(set(taxonomy))
    assert frameworks.issubset(set(taxonomy))
    assert databases.issubset(set(taxonomy))
    assert cloud.issubset(set(taxonomy))


def test_resume_upload_skills_db_persistence():
    """Verify POST /api/resumes/upload populates parsed_skills directly in the database."""
    resume_text = """
    Samantha Ray
    samantha.ray@cloud.io

    SUMMARY
    Senior Engineer specializing in Python, React, PostgreSQL, Docker, and Kubernetes.
    """

    response = client.post(
        "/api/resumes/upload",
        files=[("files", ("samantha_resume.txt", resume_text.encode("utf-8"), "text/plain"))]
    )
    assert response.status_code == 201
    resume_id = response.json()[0]["id"]

    db: Session = SessionLocal()
    try:
        db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
        assert db_resume is not None
        assert "Python" in db_resume.parsed_skills
        assert "React" in db_resume.parsed_skills
        assert "PostgreSQL" in db_resume.parsed_skills
        assert "Docker" in db_resume.parsed_skills
        assert "Kubernetes" in db_resume.parsed_skills
    finally:
        db.close()
