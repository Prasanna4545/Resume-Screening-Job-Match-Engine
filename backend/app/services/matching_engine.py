from typing import Dict, Any, List
from app.services.embedding_service import EmbeddingService
from app.services.skill_extractor import SkillExtractor
from app.services.explainability import ExplainabilityEngine


class MatchingEngine:
    """
    Hybrid Resume-Job Matching Engine implementing weighted multi-signal scoring:
    overall_score = 0.4 * semantic_similarity + 0.4 * skill_match_score + 0.2 * experience_match_score
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.skill_extractor = SkillExtractor()
        self.explainability_engine = ExplainabilityEngine()

    def calculate_experience_score(self, candidate_exp: float, min_required_exp: int) -> float:
        """
        Calculate experience match score (0-100).
        Full score if candidate meets/exceeds requirement, tapered if below.
        """
        if min_required_exp <= 0:
            return 100.0
        if candidate_exp >= min_required_exp:
            return 100.0
        ratio = max(0.0, candidate_exp / float(min_required_exp))
        return round(ratio * 100.0, 2)

    def calculate_skill_score(
        self, candidate_skills: List[str], required_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate skill match score (0-100) and identify matched/missing skills.
        """
        if not required_skills:
            return {
                "score": 100.0,
                "matched_skills": candidate_skills[:5],
                "missing_skills": []
            }

        cand_set = {s.lower() for s in candidate_skills}
        matched = [s for s in required_skills if s.lower() in cand_set]
        missing = [s for s in required_skills if s.lower() not in cand_set]

        ratio = len(matched) / len(required_skills)
        score = round(ratio * 100.0, 2)

        return {
            "score": score,
            "matched_skills": matched,
            "missing_skills": missing
        }

    def evaluate_match(self, job_data: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate full candidate resume against job requirement.
        """
        job_text = f"{job_data.get('title', '')}\n{job_data.get('description', '')}"
        resume_text = resume_data.get('raw_text', '')

        # 1. Semantic Embedding Cosine Similarity (Weight: 0.4)
        semantic_score = self.embedding_service.compute_semantic_similarity(job_text, resume_text)

        # 2. Skill Match Score (Weight: 0.4)
        required_skills = job_data.get("required_skills", [])
        candidate_skills = resume_data.get("parsed_skills", [])
        if not candidate_skills and resume_text:
            candidate_skills = self.skill_extractor.extract_skills(resume_text)

        skill_res = self.calculate_skill_score(candidate_skills, required_skills)
        skill_score = skill_res["score"]

        # 3. Experience Match Score (Weight: 0.2)
        parsed_exp = resume_data.get("parsed_experience_years", 0.0)
        min_exp = job_data.get("min_experience_years", 0)
        raw_exp_score = self.calculate_experience_score(parsed_exp, min_exp)

        # Domain Relevance Gating for Experience Score:
        # If candidate has 0 matching skills AND low semantic similarity (< 35%),
        # non-relevant industry experience (e.g. Executive Chef) is scaled by semantic similarity.
        if len(skill_res["matched_skills"]) == 0 and semantic_score < 35.0:
            exp_score = round(raw_exp_score * (semantic_score / 100.0), 2)
        else:
            exp_score = raw_exp_score

        # Weighted Overall Score Formula
        overall_score = round(
            0.4 * semantic_score +
            0.4 * skill_score +
            0.2 * exp_score,
            2
        )


        # Generate Explainability Summary
        explanation = self.explainability_engine.generate_explanation(
            overall_score=overall_score,
            semantic_score=semantic_score,
            skill_score=skill_score,
            experience_score=exp_score,
            matched_skills=skill_res["matched_skills"],
            missing_skills=skill_res["missing_skills"],
            parsed_exp=parsed_exp,
            min_exp=min_exp
        )

        return {
            "overall_score": overall_score,
            "semantic_similarity_score": semantic_score,
            "skill_match_score": skill_score,
            "experience_match_score": exp_score,
            "matched_skills": skill_res["matched_skills"],
            "missing_skills": skill_res["missing_skills"],
            "explanation": explanation
        }
