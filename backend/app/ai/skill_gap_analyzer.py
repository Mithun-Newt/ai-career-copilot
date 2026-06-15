from typing import List, Dict, Any

# Map missing skill names to categorical focus areas for customized recommendations
FOCUS_AREA_CATEGORIZATION = {
    "FastAPI": "API Frameworks",
    "REST APIs": "API Frameworks",
    "PostgreSQL": "Database Systems",
    "SQL": "Database Systems",
    "Vector Databases": "AI & Vector Storage",
    "RAG": "AI & Vector Storage",
    "LLMs": "Generative AI Foundations",
    "Prompt Engineering": "Generative AI Foundations",
    "LangChain": "AI Orchestration",
    "LangGraph": "AI Orchestration",
    "Docker": "DevOps & Containers",
    "Kubernetes": "DevOps & Containers",
    "Redis": "Caching & Queues",
    "Pandas": "Data Manipulation",
    "Numpy": "Data Manipulation",
    "Machine Learning": "Core ML",
    "Deep Learning": "Deep Learning / PyTorch",
    "PyTorch": "Deep Learning / PyTorch",
    "Statistics": "Mathematics",
    "CI/CD": "DevOps & Containers",
    "Unit Testing": "Quality Assurance"
}


class SkillGapAnalyzer:
    """
    Analyzes gaps between user profile skills and target career path requirements.
    Calculates coverage ratios and outputs categorizations.
    """

    def analyze_gap(self, user_skills: List[str], target_skills: List[str]) -> Dict[str, Any]:
        """
        Performs set-based gap analysis and groups missing elements into focus areas.
        """
        if not target_skills:
            return {
                "matched_skills": [],
                "missing_skills": [],
                "match_percentage": 0,
                "user_skills_count": len(user_skills),
                "target_skills_count": 0,
                "focus_areas": {}
            }

        # Normalize casings for comparing
        user_skills_normalized = {skill.lower().strip() for skill in user_skills}
        
        matched_skills = []
        missing_skills = []

        for skill in target_skills:
            if skill.lower().strip() in user_skills_normalized:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        # Calculate coverage score
        match_percentage = int((len(matched_skills) / len(target_skills)) * 100)

        # Formulate focus areas categories
        focus_areas: Dict[str, List[str]] = {}
        for skill in missing_skills:
            category = FOCUS_AREA_CATEGORIZATION.get(skill, "General Engineering")
            if category not in focus_areas:
                focus_areas[category] = []
            focus_areas[category].append(skill)

        return {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_percentage": match_percentage,
            "user_skills_count": len(user_skills),
            "target_skills_count": len(target_skills),
            "focus_areas": focus_areas
        }


# Expose analyzer singleton
skill_gap_analyzer = SkillGapAnalyzer()
