import pytest
from app.services.skill_extractor import SkillExtractor

extractor = SkillExtractor()

TEST_RESUME_TEXT = """
Alex Rivera
Senior Software Engineer

SKILLS
Programming Languages: Python, TypeScript, C++
Web Frameworks: FastAPI, ReactJS, Node.js, TailwindCSS
Databases & Cloud: Postgres, Redis, AWS, Docker, Kubernetes
ML & NLP: PyTorch, scikit-learn, spaCy, HuggingFace
"""

def test_exact_and_fuzzy_skill_extraction():
    skills = extractor.extract_skills(TEST_RESUME_TEXT)
    
    # Assert exact match skills
    assert "Python" in skills
    assert "TypeScript" in skills
    assert "C++" in skills
    assert "FastAPI" in skills
    assert "AWS" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "PyTorch" in skills
    assert "spaCy" in skills
    assert "scikit-learn" in skills

    # Assert fuzzy / alias matched skills
    assert "React" in skills  # ReactJS -> React
    assert "PostgreSQL" in skills  # Postgres -> PostgreSQL
    assert "Node.js" in skills


def test_empty_or_no_skill_text():
    assert extractor.extract_skills("") == []
    assert extractor.extract_skills("Nothing related to technology here.") == []
