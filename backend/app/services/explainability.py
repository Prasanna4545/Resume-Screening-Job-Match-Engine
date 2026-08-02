from typing import List, Dict, Any


class ExplainabilityEngine:
    """
    Generates human-readable explanations and skill gap analysis
    for candidate-job match evaluations.
    """

    def generate_explanation(
        self,
        overall_score: float,
        semantic_score: float,
        skill_score: float,
        experience_score: float,
        matched_skills: List[str],
        missing_skills: List[str],
        parsed_exp: float,
        min_exp: int
    ) -> str:
        """
        Generate a clear natural-language explanation string.
        Example: "Strong match: 8/10 required skills found, 5.0 years experience meets the 3-year minimum."
        """
        total_req = len(matched_skills) + len(missing_skills)
        match_level = "Excellent match" if overall_score >= 80 else \
                      "Strong match" if overall_score >= 65 else \
                      "Moderate match" if overall_score >= 50 else \
                      "Low match"

        skills_str = f"{len(matched_skills)}/{total_req} required skills found" if total_req > 0 else "skills evaluated"
        
        if min_exp > 0:
            if parsed_exp >= min_exp:
                exp_str = f"{parsed_exp:.1f} years experience meets the {min_exp}-year minimum"
            else:
                exp_str = f"{parsed_exp:.1f} years experience falls below the {min_exp}-year requirement"
        else:
            exp_str = f"{parsed_exp:.1f} years experience"

        explanation = f"{match_level}: {skills_str}, {exp_str}."
        if missing_skills:
            explanation += f" Top missing skills: {', '.join(missing_skills[:3])}."

        return explanation

    def get_top_matched_and_missing(
        self,
        candidate_skills: List[str],
        job_skills: List[str]
    ) -> Dict[str, List[str]]:
        """Identify Top 5 matched skills and Top 5 missing required skills."""
        cand_set = {s.lower(): s for s in candidate_skills}
        matched = []
        missing = []

        for req_skill in job_skills:
            if req_skill.lower() in cand_set:
                matched.append(req_skill)
            else:
                missing.append(req_skill)

        # Include additional candidate skills as matched if relevant
        for s in candidate_skills:
            if s not in matched and len(matched) < 5:
                matched.append(s)

        return {
            "matched_skills": matched[:5],
            "missing_skills": missing[:5]
        }
