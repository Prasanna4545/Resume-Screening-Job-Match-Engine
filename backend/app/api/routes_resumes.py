from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import os
from app.database import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse
from app.services.resume_parser import ResumeParser
from app.services.skill_extractor import SkillExtractor
from app.services.storage_service import StorageService

router = APIRouter(prefix="/resumes", tags=["Resumes"])
parser = ResumeParser()
skill_extractor = SkillExtractor()
storage_service = StorageService()

@router.get("", response_model=List[ResumeResponse])
def list_resumes(db: Session = Depends(get_db)):
    return db.query(Resume).order_by(Resume.uploaded_at.desc()).all()

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: str, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@router.post("/upload", response_model=List[ResumeResponse], status_code=status.HTTP_201_CREATED)
async def upload_resumes(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    uploaded_resumes = []
    
    for file in files:
        filename = file.filename or "resume.txt"
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{filename}' is empty."
            )

        ext = filename.rsplit(".", 1)[-1].lower()

        try:
            if ext == "pdf":
                raw_text = parser.extract_text_from_pdf(content)
            elif ext in ["docx", "doc"]:
                raw_text = parser.extract_text_from_docx(content)
            else:
                raw_text = content.decode("utf-8", errors="ignore")
                if not raw_text.strip():
                    raise ValueError("File contains no readable text content.")
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process file '{filename}': {str(ve)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unexpected error parsing '{filename}': {str(e)}"
            )

        parsed = parser.parse_resume(raw_text, filename=filename)
        extracted_skills = skill_extractor.extract_skills(raw_text)

        # Upload file bytes directly to Cloudflare R2 (or return storage key)
        r2_file_key = storage_service.upload_file(
            content,
            filename,
            content_type=file.content_type or "application/octet-stream"
        )

        resume = Resume(
            candidate_name=parsed["candidate_name"],
            email=parsed["email"],
            raw_text=raw_text,
            parsed_skills=extracted_skills,
            parsed_experience_years=parsed["parsed_experience_years"],
            parsed_education=parsed["parsed_education"],
            file_path=r2_file_key
        )
        db.add(resume)
        uploaded_resumes.append(resume)

    db.commit()
    for r in uploaded_resumes:
        db.refresh(r)
    return uploaded_resumes

