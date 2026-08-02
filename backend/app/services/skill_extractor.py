import os
import json
import re
from typing import List, Set
from rapidfuzz import fuzz, process
from app.config import get_settings

settings = get_settings()

TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "skills_taxonomy.json")


class SkillExtractor:
    """
    Skill Extraction engine combining exact regex taxonomy matching
    with fuzzy string matching via rapidfuzz, incorporating strict rules for
    ambiguous short tokens (C, C++, C#, R, Go).
    """

    def __init__(self, taxonomy_path: str = TAXONOMY_PATH):
        self.taxonomy_path = taxonomy_path
        self.taxonomy: List[str] = self._load_taxonomy()
        self.taxonomy_lower_map = {skill.lower(): skill for skill in self.taxonomy}

    def _load_taxonomy(self) -> List[str]:
        if os.path.exists(self.taxonomy_path):
            with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return [
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI", "Django",
            "PostgreSQL", "Docker", "Kubernetes", "AWS", "PyTorch", "TensorFlow", "SQL",
            "C", "C++", "C#", "Go", "R"
        ]

    def extract_skills(self, text: str, fuzzy_threshold: int = 90) -> List[str]:
        """
        Extract matching skills from text using exact regex matching
        and rapidfuzz token similarity matching.
        """
        if not text or not text.strip():
            return []

        matched_skills: Set[str] = set()

        # 1. Special Handling for Ambiguous Short Tech Tokens: C++, C#, C, Go, R
        # C++ / C#
        if re.search(r'(?:^|\W)C\+\+(?:$|\W)', text):
            matched_skills.add("C++")
        if re.search(r'(?:^|\W)C\#(?:$|\W)', text):
            matched_skills.add("C#")

        # C (Standalone C programming, avoiding C++ or C# prefix)
        if re.search(r'(?:^|\W)C(?:$|\W)', text) and not re.search(r'C\+\+|C\#', text):
            # Check context to ensure it's C programming language
            if re.search(r'\b(?:C\s*(?:language|programming|code|developer)|C/C\+\+|C,)\b', text, re.I):
                matched_skills.add("C")

        # Go (programming language vs English verb "go to")
        if re.search(r'\b(?:Golang|Go\s+(?:language|programming|microservices|developer|backend))\b', text, re.I) or \
           re.search(r'\b(?:Python|Java|C\+\+|Rust|Docker|Kubernetes|TypeScript)[,\s]+Go\b', text):
            matched_skills.add("Go")

        # R (programming language vs R&D or single letter)
        if re.search(r'\b(?:R\s*(?:language|programming|studio|stats|data)|R,)\b', text, re.I) or \
           re.search(r'\b(?:Python|SQL|Julia)[,\s]+R\b', text):
            matched_skills.add("R")

        # 2. Exact Taxonomy Word-Boundary Search for all other skills
        for skill in self.taxonomy:
            if skill in ["C", "C++", "C#", "Go", "R"]:
                continue  # Handled above via strict contextual rules

            escaped_skill = re.escape(skill)
            if skill.isalnum():
                pattern = rf'\b{escaped_skill}\b'
            else:
                pattern = rf'(?:^|\s|\W){escaped_skill}(?:$|\s|\W)'

            if re.search(pattern, text, re.IGNORECASE):
                matched_skills.add(skill)

        # 3. Fuzzy Matching for Skill Variations (skipping short < 4 char skills)
        words_and_phrases = re.findall(r'\b[a-zA-Z0-9+#.-]{4,20}\b', text)
        aliases = {
            "reactjs": "React",
            "nodejs": "Node.js",
            "fastapi": "FastAPI",
            "postgres": "PostgreSQL",
            "postgresql": "PostgreSQL",
            "tailwindcss": "TailwindCSS",
            "spacy": "spaCy",
            "scikit": "scikit-learn",
            "sklearn": "scikit-learn",
            "pyspark": "PySpark",
            "typescript": "TypeScript",
            "javascript": "JavaScript",
            "golang": "Go",
        }

        for chunk in words_and_phrases:
            chunk_lower = chunk.lower()

            if chunk_lower in aliases and aliases[chunk_lower] in self.taxonomy:
                matched_skills.add(aliases[chunk_lower])
                continue

            # Skip fuzzy search if token is too short or is a pure number
            if len(chunk_lower) < 4 or chunk_lower.isdigit():
                continue

            match = process.extractOne(
                chunk_lower,
                [s.lower() for s in self.taxonomy if len(s) >= 4],
                scorer=fuzz.ratio,
                score_cutoff=fuzzy_threshold
            )
            if match:
                matched_skill_lower = match[0]
                canonical_skill = self.taxonomy_lower_map.get(matched_skill_lower)
                if canonical_skill:
                    matched_skills.add(canonical_skill)

        return sorted(list(matched_skills))
