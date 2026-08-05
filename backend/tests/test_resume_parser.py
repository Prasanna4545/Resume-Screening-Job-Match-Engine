import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal, engine
from app.models.resume import Resume
from app.services.resume_parser import ResumeParser

client = TestClient(app)
parser = ResumeParser()

# Sample 1: Standard layout
SAMPLE_RESUME_1 = """
Alice Johnson
Email: alice.johnson@example.com
Phone: (555) 234-5678

PROFESSIONAL SUMMARY
Senior Software Engineer with 5+ years of experience building web applications in Python, React, and PostgreSQL.

WORK EXPERIENCE
Senior Full-Stack Developer (2021 - Present)
- Developed REST APIs with FastAPI and PostgreSQL.
- Built reactive frontends with React and TypeScript.

Software Engineer (2019 - 2021)
- Built microservices in Python and Docker.

EDUCATION
Bachelor of Science in Computer Science, Stanford University (2015 - 2019)
"""

# Sample 2: Standard layout with contact pipe
SAMPLE_RESUME_2 = """
Bob Smith
Contact: bob.smith@techcorp.io | +1-800-555-0199

EXPERIENCE
Lead Data Scientist | 2018 - 2024
- Implemented NLP models using spaCy and PyTorch.

EDUCATION
Master of Science in Data Science, MIT
"""

# Sample 3 (a): Messy / Non-standard layout with references and manager names
SAMPLE_RESUME_3_MESSY = """
Carol Martinez
Email: carol.martinez@devstudio.com | Phone: 415-555-9012

BACKGROUND & CAREER HISTORY
Staff Platform Engineer managing AWS cloud infrastructure.
Manager Reference: David Miller (VP of Engineering at Tech Corp)
Team Lead Reference: Sarah Connor

EDUCATION & CREDENTIALS
B.Tech in Information Technology
AWS Certified Solutions Architect

WORK HISTORY
2020 - Present: Staff Engineer at CloudSystems
2016 - 2020: Infrastructure Engineer at DataNode
"""

# Sample 4 (b): No explicit date ranges (e.g. "Over 4 years of experience")
SAMPLE_RESUME_4_NO_DATES = """
David Lee
david.lee@frontend.dev

SUMMARY
Frontend Specialist with over 4 years of experience crafting modern user interfaces using React, Vue, and TailwindCSS.

TECHNICAL SKILLS
JavaScript, TypeScript, HTML, CSS

EDUCATION
Bachelor of Arts in Design
"""

# Sample 5 (c): Minimal / Sparse Resume
SAMPLE_RESUME_5_SPARSE = """
Eve Taylor
eve.taylor@startup.io
Software Developer seeking backend role.
"""


def test_extract_email():
    assert parser.extract_email(SAMPLE_RESUME_1) == "alice.johnson@example.com"
    assert parser.extract_email(SAMPLE_RESUME_2) == "bob.smith@techcorp.io"
    assert parser.extract_email(SAMPLE_RESUME_3_MESSY) == "carol.martinez@devstudio.com"


def test_extract_phone():
    assert parser.extract_phone(SAMPLE_RESUME_1) is not None
    assert parser.extract_phone(SAMPLE_RESUME_3_MESSY) == "415-555-9012"


def test_name_extraction_reliability_and_fallback():
    # Ensures manager names (David Miller) in body are not mistaken for candidate name (Carol Martinez)
    name_messy = parser.extract_name(SAMPLE_RESUME_3_MESSY)
    assert name_messy == "Carol Martinez"

    name_sparse = parser.extract_name(SAMPLE_RESUME_5_SPARSE)
    assert name_sparse == "Eve Taylor"


def test_diverse_experience_parsing():
    exp_standard = parser.extract_experience_years(SAMPLE_RESUME_1)
    exp_no_dates = parser.extract_experience_years(SAMPLE_RESUME_4_NO_DATES)
    exp_sparse = parser.extract_experience_years(SAMPLE_RESUME_5_SPARSE)

    assert exp_standard >= 5.0
    assert exp_no_dates == 4.0
    assert exp_sparse == 0.0


def test_diverse_education_parsing():
    edu_messy = parser.extract_education(SAMPLE_RESUME_3_MESSY)
    edu_no_dates = parser.extract_education(SAMPLE_RESUME_4_NO_DATES)

    assert any("B.Tech" in e or "Information Technology" in e for e in edu_messy)
    assert any("Bachelor" in e or "Design" in e for e in edu_no_dates)


def test_end_to_end_db_persistence():
    """Verify that uploading a file via POST /api/resumes/upload persists all fields to DB."""
    file_content = SAMPLE_RESUME_3_MESSY.encode("utf-8")
    response = client.post(
        "/api/resumes/upload",
        files=[("files", ("carol_martinez.txt", file_content, "text/plain"))]
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    resume_id = data[0]["id"]

    # Query DB directly to verify persistence
    db: Session = SessionLocal()
    try:
        db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
        assert db_resume is not None
        assert db_resume.candidate_name == "Carol Martinez"
        assert db_resume.email == "carol.martinez@devstudio.com"
        assert db_resume.parsed_experience_years >= 8.0
        assert len(db_resume.parsed_education) > 0
        assert "carol_martinez.txt" in db_resume.file_path
        assert "Staff Platform Engineer" in db_resume.raw_text
    finally:
        db.close()


def test_error_handling_corrupt_empty_files():
    """Test upload endpoint with empty file and corrupted content."""
    # 1. Empty file (0 bytes)
    res_empty = client.post(
        "/api/resumes/upload",
        files=[("files", ("empty.pdf", b"", "application/pdf"))]
    )
    assert res_empty.status_code == 400
    assert "empty" in res_empty.json()["detail"].lower()

    # 2. Corrupted PDF content
    res_corrupt = client.post(
        "/api/resumes/upload",
        files=[("files", ("bad.pdf", b"NOT_A_VALID_PDF_HEADER", "application/pdf"))]
    )
    assert res_corrupt.status_code == 400
    assert "failed to process file" in res_corrupt.json()["detail"].lower() or "pdf" in res_corrupt.json()["detail"].lower()
