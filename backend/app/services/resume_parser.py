import re
import io
from typing import Dict, List, Any, Optional
import pdfplumber
import docx
import spacy

# Load spaCy small English pipeline
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


class ResumeParser:
    """
    Structured Resume Parsing service using pdfplumber, python-docx,
    regex patterns, and spaCy Named Entity Recognition (NER).
    """

    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """Extract raw text from PDF document using pdfplumber with error handling."""
        if not file_bytes or len(file_bytes.strip()) == 0:
            raise ValueError("Empty file provided")
        try:
            text_content = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                if len(pdf.pages) == 0:
                    raise ValueError("PDF file contains no pages")
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content.append(extracted)
            result = "\n".join(text_content).strip()
            if not result:
                raise ValueError("PDF contains no extractable text (scanned or blank PDF)")
            return result
        except Exception as e:
            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                raise ValueError("PDF file is password-protected or encrypted")
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Failed to parse PDF document: {str(e)}")

    @staticmethod
    def extract_text_from_docx(file_bytes: bytes) -> str:
        """Extract raw text from DOCX document using python-docx with error handling."""
        if not file_bytes or len(file_bytes.strip()) == 0:
            raise ValueError("Empty file provided")
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            result = "\n".join(paragraphs).strip()
            if not result:
                raise ValueError("DOCX document contains no text")
            return result
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Failed to parse DOCX document: {str(e)}")

    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email address using regex."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Extract phone number using regex."""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def extract_name(text: str) -> str:
        """
        Extract candidate name prioritizing document top-line header,
        with spaCy PERSON NER validation to prevent extracting manager/reference names.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return "Unknown Candidate"

        # Examine top 3 lines for candidate header
        for i, line in enumerate(lines[:3]):
            # Skip contact header lines containing email, URL, phone, or section keywords
            if re.search(r'@|http|phone|\+?\d{7,}|resume|curriculum|vitae|profile|experience|skills', line, re.I):
                continue

            words = line.split()
            if 1 <= len(words) <= 4 and all(w[0].isupper() or w.lower() in ['de', 'van', 'der', 'jr', 'sr', 'iii'] for w in words if w.isalpha()):
                # Confirm with spaCy or top line heuristic
                doc = nlp(line)
                person_ents = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
                if person_ents:
                    return person_ents[0].strip()
                # Top header fallback
                if i == 0:
                    return line.strip()

        # Secondary pass: check top 5 lines for any spaCy PERSON entity
        top_text = "\n".join(lines[:5])
        doc = nlp(top_text)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) <= 4:
                return ent.text.strip()

        return "Unknown Candidate"

    @staticmethod
    def extract_experience_years(text: str) -> float:
        """Estimate total experience years based on explicit cues and date ranges."""
        if not text or not text.strip():
            return 0.0

        # Pattern 1: Explicit mentions like "5+ years of experience", "4 yrs experience"
        pattern = r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:work\s+)?experience'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

        # Pattern 2: Date ranges (e.g. 2018 - 2023 or 2019 - Present)
        year_ranges = re.findall(r'(20\d{2}|19\d{2})\s*(?:-|to|\u2013)\s*(20\d{2}|Present|Current|now)', text, re.IGNORECASE)
        total_years = 0.0
        current_year = 2026

        for start_str, end_str in year_ranges:
            try:
                start_year = int(start_str)
                if end_str.lower() in ['present', 'current', 'now']:
                    end_year = current_year
                else:
                    end_year = int(end_str)
                diff = max(0, end_year - start_year)
                total_years += diff
            except ValueError:
                continue

        if total_years > 0:
            return round(total_years, 1)

        # Pattern 3: Lone duration mentions e.g. "Over 4 years"
        lone_match = re.search(r'(?:over|approx\.?|around)?\s*(\d+)\s*(?:years?|yrs?)', text, re.IGNORECASE)
        if lone_match:
            return float(lone_match.group(1))

        return 0.0

    @staticmethod
    def extract_education(text: str) -> List[str]:
        """Extract degree qualifications and education sections."""
        education_keywords = [
            "Bachelor", "Master", "Ph.D", "PhD", "B.S.", "B.A.", "M.S.", "M.A.", "B.Tech", "M.Tech",
            "Bachelor of Science", "Bachelor of Arts", "Master of Science", "Computer Science",
            "Information Technology", "Engineering", "Degree", "University", "College"
        ]
        found_education = []
        lines = text.split('\n')
        for line in lines:
            for kw in education_keywords:
                if kw.lower() in line.lower():
                    clean_line = line.strip()
                    if clean_line and clean_line not in found_education and len(clean_line) < 120:
                        found_education.append(clean_line)
                    break
        return found_education[:4]

    def parse_resume(self, text: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Parse raw resume text into structured candidate profile."""
        name = self.extract_name(text)
        if name == "Unknown Candidate" and filename:
            clean_filename = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
            name = clean_filename

        return {
            "candidate_name": name,
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "parsed_experience_years": self.extract_experience_years(text),
            "parsed_education": self.extract_education(text),
            "raw_text": text
        }
