import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_endpoints_workflow():
    """Verify all 7 REST endpoints specified in section 7 of prompt."""
    # 1. POST /api/jobs
    job_res = client.post("/api/jobs", json={
        "title": "Lead DevOps & Cloud Engineer",
        "description": "Building AWS cloud infrastructure with Terraform, Docker, and Kubernetes.",
        "required_skills": ["AWS", "Terraform", "Docker", "Kubernetes"],
        "min_experience_years": 5
    })
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # 2. GET /api/jobs/{id}
    get_job = client.get(f"/api/jobs/{job_id}")
    assert get_job.status_code == 200
    assert get_job.json()["title"] == "Lead DevOps & Cloud Engineer"

    # 3. POST /api/resumes/upload
    resume_text = "DevOps Engineer with 6 years experience in AWS, Terraform, Docker, and Kubernetes."
    up_res = client.post("/api/resumes/upload", files=[
        ("files", ("devops_resume.txt", resume_text.encode("utf-8"), "text/plain"))
    ])
    assert up_res.status_code == 201
    resume_id = up_res.json()[0]["id"]

    # 4. GET /api/resumes/{id}
    get_res = client.get(f"/api/resumes/{resume_id}")
    assert get_res.status_code == 200
    assert get_res.json()["candidate_name"] is not None

    # 5. POST /api/matching/run
    match_run = client.post("/api/matching/run", json={
        "job_id": job_id,
        "resume_ids": [resume_id]
    })
    assert match_run.status_code == 200
    assert len(match_run.json()) == 1

    # 6. GET /api/matching/results/{job_id}
    results_list = client.get(f"/api/matching/results/{job_id}")
    assert results_list.status_code == 200
    assert len(results_list.json()) == 1

    # 7. GET /api/matching/results/{job_id}/{resume_id}
    detail = client.get(f"/api/matching/results/{job_id}/{resume_id}")
    assert detail.status_code == 200
    assert detail.json()["overall_score"] > 0.0
