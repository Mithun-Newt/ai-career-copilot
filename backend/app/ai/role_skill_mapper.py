import os
import re
from typing import List, Dict
from pydantic import BaseModel, Field
import httpx

# Master static map for roles.
ROLE_SKILLS_CATALOG: Dict[str, List[str]] = {
    "AI Engineer": [
        "Python", "FastAPI", "LangChain", "Vector Databases",
        "Prompt Engineering", "RAG", "LLMs", "PyTorch", "Docker", "Kubernetes"
    ],
    "Data Scientist": [
        "Python", "Pandas", "Numpy", "Machine Learning", "Statistics",
        "SQL", "Matplotlib", "Scikit-Learn", "Deep Learning"
    ],
    "Backend Developer": [
        "Python", "FastAPI", "PostgreSQL", "Docker", "REST APIs",
        "Redis", "Git", "SQLAlchemy", "Unit Testing", "CI/CD"
    ],
    "Product Manager": [
        "Product Strategy", "Roadmapping", "Agile Methodologies", "User Research", "Wireframing",
        "A/B Testing", "Data Analytics", "Market Analysis", "Jira", "SQL"
    ],
    "Digital Marketing Specialist": [
        "SEO", "SEM", "Google Analytics", "Content Strategy", "Social Media Marketing",
        "Email Campaigns", "Copywriting", "A/B Testing", "PPC Advertising", "Customer Segmentation"
    ],
    "UX/UI Designer": [
        "Figma", "User Research", "Wireframing", "Prototyping", "Information Architecture",
        "Interaction Design", "Visual Design", "Design Systems", "User Testing"
    ],
    "HR Manager": [
        "Talent Acquisition", "Employee Relations", "Performance Management", "HRIS", "Onboarding",
        "Conflict Resolution", "Labor Laws", "Organizational Development"
    ],
    "Financial Analyst": [
        "Financial Modeling", "Excel VBA", "Data Analysis", "Forecasting", "SQL",
        "Valuation", "Power BI", "Tableau", "Budgeting"
    ],
    "Sales Representative": [
        "Salesforce", "Lead Generation", "Negotiation", "Client Relationship Management", "Cold Calling",
        "Product Demos", "Sales Pipeline Management", "Account Management"
    ],
    "Content Writer": [
        "SEO Copywriting", "Content Marketing", "Editing", "Research", "WordPress",
        "Social Media Management", "Proofreading", "Creative Writing"
    ],
    "Project Manager": [
        "Agile Scrum", "Project Planning", "Risk Management", "Jira", "MS Project",
        "Resource Allocation", "Stakeholder Communication", "Budget Tracking"
    ]
}


class RoleSkillsModel(BaseModel):
    skills: List[str] = Field(description="List of 8 to 12 core professional skills required for this role.")


class RoleSkillMapper:
    """
    Resolves required skill catalogs for targeted career roles.
    """

    def get_skills_for_role(self, target_role: str) -> List[str]:
        """
        Query target skills matching a role. Employs case-insensitive matching fallback logic.
        If role is not in database, dynamically queries LLM or web search.
        """
        role_key = target_role.strip().lower()
        
        # Standardize matching in static catalog
        for catalog_role, skills in ROLE_SKILLS_CATALOG.items():
            if catalog_role.lower() in role_key or role_key in catalog_role.lower():
                return skills

        # If not found in catalog, try LLM dynamic lookup
        try:
            from app.ai.roadmap_generator import get_llm
            llm = get_llm()
            if llm is not None:
                structured_llm = llm.with_structured_output(RoleSkillsModel)
                from langchain_core.prompts import ChatPromptTemplate
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an expert career coach. Identify the top 8 to 12 key skills or tools required for the target job role."),
                    ("user", "Target Role: {target_role}\nGenerate the list of key skills.")
                ])
                chain = prompt | structured_llm
                result = chain.invoke({"target_role": target_role})
                if result and result.skills:
                    return [s.strip() for s in result.skills if s.strip()]
        except Exception as e:
            print(f"Failed to query LLM for skills: {e}")

        # Web search fallback
        try:
            from app.ai.roadmap_generator import search_role_requirements_on_web
            web_requirements = search_role_requirements_on_web(target_role)
            if web_requirements:
                # Use simple regex or splits to find possible skill words from snippets
                words = re.findall(r'[a-zA-Z\s\-\#\+\.]+', web_requirements)
                # Filter useful skill terms/nouns (heuristic)
                candidate_skills = []
                for w in words:
                    cleaned = w.strip()
                    if 2 < len(cleaned) < 25 and cleaned.istitle() and cleaned not in candidate_skills:
                        candidate_skills.append(cleaned)
                if len(candidate_skills) >= 5:
                    return candidate_skills[:10]
        except Exception as e:
            print(f"Failed web-search skills fallback: {e}")
                
        # If target role is not mapped, provide a basic standard technical and soft skill baseline
        return ["Communication", "Problem Solving", "Project Management", "Time Management", "Collaboration"]


# Expose mapper singleton
role_skill_mapper = RoleSkillMapper()
