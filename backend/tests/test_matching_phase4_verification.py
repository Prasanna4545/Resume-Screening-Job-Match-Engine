import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal
from app.models.job import Job
from app.models.resume import Resume
from app.models.match_result import MatchResult
from app.services.matching_engine import MatchingEngine

client = TestClient(app)
matching_engine = MatchingEngine()

# 1. Job Requirement: Senior Full-Stack Python & React Engineer
JOB_DESCRIPTION = """
Senior Full-Stack Engineer
We are seeking an experienced Senior Full-Stack Engineer to build scalable microservices and web applications.
Required Skills: Python, FastAPI, React, PostgreSQL, Docker, AWS
Minimum Experience: 4 years
"""

# 2. Resumes of varying relevance
RESUME_STRONG_MATCH = """
Alex Mercer
alex.mercer@dev.io | (555) 019-2831

SUMMARY
Senior Full-Stack Engineer with 6+ years of experience building cloud microservices and web applications.

SKILLS
Python, FastAPI, React, PostgreSQL, Docker, AWS, TypeScript, Git

WORK EXPERIENCE
Senior Backend Engineer (2020 - Present)
- Designed and built RESTful microservices in Python and FastAPI.
- Deployed containerized applications to AWS using Docker and Kubernetes.

Frontend Developer (2018 - 2020)
- Developed responsive web interfaces using React and TypeScript.

EDUCATION
Bachelor of Science in Computer Science, UC Berkeley (2014 - 2018)
"""

RESUME_PARTIAL_MATCH = """
Brenda Chen
brenda.chen@frontend.org

SUMMARY
Frontend Specialist with 3 years of experience crafting interactive web applications in React and JavaScript.

SKILLS
React, JavaScript, HTML5, CSS3, TailwindCSS, Git

WORK EXPERIENCE
Frontend Engineer (2021 - Present)
- Developed web dashboards with React and Redux.

EDUCATION
Bachelor of Arts in Design
"""

RESUME_IRRELEVANT_MATCH = """
Carlos Rossi
carlos.rossi@gourmet.com

SUMMARY
Head Executive Chef with 10+ years managing high-end restaurant kitchens and culinary staff.

EXPERIENCE
Executive Chef at Bistro Paris (2016 - Present)
- Menu design, kitchen inventory, and team management.

EDUCATION
Culinary Arts Diploma, Le Cordon Bleu
"""

RESUME_ZERO_EXP = """
David Kim
david.kim@freshgrad.edu

SUMMARY
Recent Computer Science Graduate passionate about backend software development.

SKILLS
Python, Java, SQL

EDUCATION
Bachelor of Science in Computer Science (2025)
"""


def test_matching_edge_cases_and_robustness():
    """Test zero skills, zero experience, and zero overlapping skills without crashing."""
    # (a) Job with zero required skills
    job_no_skills = {"title": "General Developer", "description": "Need software dev.", "required_skills": [], "min_experience_years": 0}
    res_no_skills = {"raw_text": "Developer text", "parsed_skills": ["Python"], "parsed_experience_years": 2.0}
    eval_a = matching_engine.evaluate_match(job_no_skills, res_no_skills)
    assert 0.0 <= eval_a["overall_score"] <= 100.0
    assert eval_a["skill_match_score"] == 100.0

    # (b) Resume with 0 experience
    job_exp = {"title": "Dev", "description": "Dev job", "required_skills": ["Python"], "min_experience_years": 3}
    res_zero_exp = {"raw_text": "Python dev", "parsed_skills": ["Python"], "parsed_experience_years": 0.0}
    eval_b = matching_engine.evaluate_match(job_exp, res_zero_exp)
    assert eval_b["experience_match_score"] == 0.0
    assert eval_b["overall_score"] > 0.0  # Still gets credit for skills and semantic embedding

    # (c) Zero overlapping skills
    res_zero_overlap = {"raw_text": "Chef text", "parsed_skills": ["Cooking"], "parsed_experience_years": 5.0}
    eval_c = matching_engine.evaluate_match(job_exp, res_zero_overlap)
    assert eval_c["skill_match_score"] == 0.0
    assert eval_c["overall_score"] < 50.0


def test_end_to_end_rank_ordering_and_db_persistence():
    """Run full matching on 4 distinct candidates and verify sub-scores, explanations, and DB persistence."""
    # 1. Create Job
    job_res = client.post("/api/jobs", json={
        "title": "Senior Full-Stack Python & React Engineer",
        "description": JOB_DESCRIPTION,
        "required_skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "AWS"],
        "min_experience_years": 4
    })
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # 2. Upload 4 Resumes
    resumes = [
        ("alex_mercer.txt", RESUME_STRONG_MATCH),
        ("brenda_chen.txt", RESUME_PARTIAL_MATCH),
        ("carlos_rossi.txt", RESUME_IRRELEVANT_MATCH),
        ("david_kim.txt", RESUME_ZERO_EXP),
    ]
    resume_ids = []
    for filename, text in resumes:
        up_res = client.post("/api/resumes/upload", files=[("files", (filename, text.encode("utf-8"), "text/plain"))])
        assert up_res.status_code == 201
        resume_ids.append(up_res.json()[0]["id"])

    # 3. Execute Matching API
    match_res = client.post("/api/matching/run", json={"job_id": job_id, "resume_ids": resume_ids})
    assert match_res.status_code == 200
    ranked_results = match_res.json()
    assert len(ranked_results) == 4

    print("\n================ RANKED CANDIDATES LEADERBOARD ================")
    for rank, res in enumerate(ranked_results, 1):
        cand_name = res["resume"]["candidate_name"] if res.get("resume") else "Candidate"
        print(f"Rank #{rank}: {cand_name}")
        print(f"  Overall Score:             {res['overall_score']}%")
        print(f"  Semantic Similarity Score: {res['semantic_similarity_score']}%")
        print(f"  Skill Match Score:         {res['skill_match_score']}%")
        print(f"  Experience Match Score:    {res['experience_match_score']}%")
        print(f"  Matched Skills:            {res['matched_skills']}")
        print(f"  Missing Skills:            {res['missing_skills']}")
        print(f"  Explanation:               {res['explanation']}\n")

    # Sanity Check 1: Alex Mercer (Strong Match) should be Rank #1
    top_candidate = ranked_results[0]["resume"]["candidate_name"]
    assert top_candidate == "Alex Mercer"

    # Sanity Check 2: Carlos Rossi (Chef) should be lowest ranked candidate
    lowest_candidate = ranked_results[-1]["resume"]["candidate_name"]
    assert lowest_candidate == "Carlos Rossi"

    # 4. Direct Database Persistence Verification for Sub-Scores
    db: Session = SessionLocal()
    try:
        db_match_results = db.query(MatchResult).filter(MatchResult.job_id == job_id).all()
        assert len(db_match_results) == 4
        sample_db_row = db_match_results[0]
        
        print("================ DIRECT DB ROW QUERY VERIFICATION ================")
        print("Match ID:", sample_db_row.id)
        print("Job ID:", sample_db_row.job_id)
        print("Resume ID:", sample_db_row.resume_id)
        print("overall_score:", sample_db_row.overall_score)
        print("skill_match_score:", sample_db_row.skill_match_score)
        print("experience_match_score:", sample_db_row.experience_match_score)
        print("semantic_similarity_score:", sample_db_row.semantic_similarity_score)
        print("matched_skills (JSON):", sample_db_row.matched_skills)
        print("missing_skills (JSON):", sample_db_row.missing_skills)
        print("explanation (Text):", sample_db_row.explanation)
        print("=================================================================\n")

        assert sample_db_row.overall_score is not None
        assert sample_db_row.skill_match_score is not None
        assert sample_db_row.experience_match_score is not None
        assert sample_db_row.semantic_similarity_score is not None
        assert sample_db_row.explanation is not None
    finally:
        db.close()
