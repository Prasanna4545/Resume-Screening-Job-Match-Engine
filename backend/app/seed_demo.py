import os
import sys

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.job import Job
from app.models.resume import Resume
from app.models.match_result import MatchResult
from app.services.resume_parser import ResumeParser
from app.services.skill_extractor import SkillExtractor
from app.services.matching_engine import MatchingEngine

Base.metadata.create_all(bind=engine)

def seed_demo_data():
    db = SessionLocal()
    parser = ResumeParser()
    skill_extractor = SkillExtractor()
    matching_engine = MatchingEngine()

    print("Clearing old demo data...")
    db.query(MatchResult).delete()
    db.query(Resume).delete()
    db.query(Job).delete()
    db.commit()

    print("Seeding sample Job Descriptions...")
    job1 = Job(
        title="Senior Full-Stack Python & React Engineer",
        description="Seeking a Senior Full-Stack Engineer skilled in Python, FastAPI, React, PostgreSQL, Docker, and AWS. Minimum 4 years experience building cloud web applications.",
        required_skills=["Python", "FastAPI", "React", "PostgreSQL", "Docker", "AWS"],
        min_experience_years=4
    )
    job2 = Job(
        title="Machine Learning & NLP Specialist",
        description="Looking for an ML Engineer to build NLP models. Must know Python, PyTorch, scikit-learn, spaCy, sentence-transformers, and HuggingFace. Minimum 3 years experience.",
        required_skills=["Python", "PyTorch", "scikit-learn", "spaCy", "sentence-transformers", "NLP"],
        min_experience_years=3
    )
    job3 = Job(
        title="DevOps & Site Reliability Engineer (SRE)",
        description="Seeking DevOps Engineer with expertise in AWS, Kubernetes, Docker, Terraform, CI/CD, Linux, and Prometheus. Minimum 5 years experience.",
        required_skills=["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Linux"],
        min_experience_years=5
    )

    db.add_all([job1, job2, job3])
    db.commit()
    db.refresh(job1)
    db.refresh(job2)
    db.refresh(job3)

    print("Seeding 15 Sample Resumes...")
    sample_resumes_raw = [
        ("Alice Johnson", "alice.johnson@dev.com", "Senior Full-Stack Engineer with 6 years experience. Expert in Python, FastAPI, React, PostgreSQL, Docker, AWS, and TypeScript.", 6.0, ["B.S. Computer Science, Stanford"]),
        ("Bob Smith", "bob.smith@ai.io", "Senior Machine Learning Engineer with 5 years experience. Built NLP systems using PyTorch, scikit-learn, spaCy, and sentence-transformers.", 5.0, ["M.S. Artificial Intelligence, MIT"]),
        ("Carol Martinez", "carol.m@cloudops.com", "DevOps & SRE Specialist with 7 years experience in AWS, Kubernetes, Docker, Terraform, CI/CD, and Linux administration.", 7.0, ["B.Tech Information Technology"]),
        ("David Lee", "david.lee@frontend.org", "Frontend Developer with 3 years experience crafting web interfaces in React, TypeScript, TailwindCSS, and HTML5.", 3.0, ["Bachelor of Design"]),
        ("Eve Taylor", "eve.t@backend.net", "Python Developer with 4 years experience creating REST APIs using FastAPI, Django, PostgreSQL, and Redis.", 4.0, ["B.S. Computer Engineering"]),
        ("Frank Miller", "frank.m@mlops.io", "Data Scientist with 3 years experience in Python, PyTorch, pandas, numpy, scikit-learn, and SQL.", 3.0, ["M.S. Data Science"]),
        ("Grace Hopper", "grace.h@devops.com", "Infrastructure Engineer with 6 years experience in Docker, Kubernetes, Terraform, AWS, Bash, and Linux.", 6.0, ["B.S. Electrical Engineering"]),
        ("Hank Schrader", "hank.s@security.net", "Cybersecurity Specialist with 8 years experience in Penetration Testing, SSL/TLS, Linux, and Network Security.", 8.0, ["B.S. Cybersecurity"]),
        ("Irene Adler", "irene.a@fullstack.dev", "Full-Stack Software Engineer with 5 years experience in Python, Django, React, MySQL, and Docker.", 5.0, ["B.S. Computer Science"]),
        ("Jack Reacher", "jack.r@cloud.org", "Cloud Engineer with 4 years experience in AWS, GCP, Terraform, Python, and Linux.", 4.0, ["B.S. Information Systems"]),
        ("Kevin Space", "kevin.s@frontend.io", "Junior Frontend Engineer with 1 year experience in React, JavaScript, HTML, and CSS.", 1.0, ["Self-Taught Bootcamp"]),
        ("Laura Croft", "laura.c@gamedev.com", "C++ Graphics Engineer with 6 years experience in C++, OpenGL, DirectX, and Computer Vision.", 6.0, ["B.S. Game Development"]),
        ("Michael Scott", "michael.s@sales.com", "Regional Sales Manager with 10 years experience in team management, client relations, and public speaking.", 10.0, ["B.A. Business Administration"]),
        ("Nancy Drew", "nancy.d@qa.org", "QA Automation Engineer with 4 years experience in Python, PyTest, Selenium, and CI/CD pipelines.", 4.0, ["B.S. Software Engineering"]),
        ("Oscar Martinez", "oscar.m@finance.com", "Corporate Accountant with 8 years experience in Excel, QuickBooks, Financial Analysis, and Tax Audit.", 8.0, ["B.S. Accounting"])
    ]

    resumes_db = []
    for name, email, text, exp, edu in sample_resumes_raw:
        skills = skill_extractor.extract_skills(text)
        res = Resume(
            candidate_name=name,
            email=email,
            raw_text=text,
            parsed_skills=skills,
            parsed_experience_years=exp,
            parsed_education=edu,
            file_path=f"{name.lower().replace(' ', '_')}.txt"
        )
        db.add(res)
        resumes_db.append(res)

    db.commit()
    for r in resumes_db:
        db.refresh(r)

    print("Running initial matching engine for Job #1...")
    job1_data = {"title": job1.title, "description": job1.description, "required_skills": job1.required_skills, "min_experience_years": job1.min_experience_years}
    for r in resumes_db:
        r_data = {"candidate_name": r.candidate_name, "raw_text": r.raw_text, "parsed_skills": r.parsed_skills, "parsed_experience_years": r.parsed_experience_years}
        eval_res = matching_engine.evaluate_match(job1_data, r_data)
        match = MatchResult(
            job_id=job1.id,
            resume_id=r.id,
            overall_score=eval_res["overall_score"],
            skill_match_score=eval_res["skill_match_score"],
            experience_match_score=eval_res["experience_match_score"],
            semantic_similarity_score=eval_res["semantic_similarity_score"],
            matched_skills=eval_res["matched_skills"],
            missing_skills=eval_res["missing_skills"],
            explanation=eval_res["explanation"]
        )
        db.add(match)

    db.commit()
    print("Demo dataset seeded successfully! (3 Jobs, 15 Resumes, Match Results)")

if __name__ == "__main__":
    seed_demo_data()
