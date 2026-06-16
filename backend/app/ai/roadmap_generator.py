import os
import re
import json
from typing import Dict, Any, List
import httpx
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Pydantic schemas for LangChain Structured Output
class TaskModel(BaseModel):
    title: str = Field(description="The specific action item or learning topic title.")
    description: str = Field(description="Actionable guidance, resources, or criteria to master this topic.")
    resources: List[str] = Field(default=[], description="List of 2-3 direct URL links (e.g., YouTube searches like 'https://www.youtube.com/results?search_query=...', official documentation, or tutorials) to study this topic.")

class MilestoneModel(BaseModel):
    title: str = Field(description="The milestone or phase title (e.g., Phase 1: Python & API Foundations).")
    description: str = Field(description="An overview of what this milestone covers and its learning objectives.")
    tasks: List[TaskModel] = Field(description="The list of individual tasks to complete in this milestone.")

class RoadmapAIOutput(BaseModel):
    title: str = Field(description="Clear and concise title for the career roadmap pathway.")
    description: str = Field(description="General roadmap overview, summarizing the transition strategy.")
    milestones: List[MilestoneModel] = Field(description="The structured milestones defining the path.")


def search_role_requirements_on_web(target_role: str) -> str:
    """
    Search the web for target role requirements and skills using DuckDuckGo.
    This fetches real job details dynamically.
    """
    try:
        query = f"{target_role} job description requirements key skills"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # Fetch search results securely
        response = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=headers,
            timeout=10.0
        )
        if response.status_code == 200:
            text = response.text
            # Extract DuckDuckGo result snippets using regular expression
            snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL)
            if snippets:
                cleaned = []
                for s in snippets[:8]:
                    clean = re.sub(r'<[^>]+>', '', s).strip()
                    cleaned.append(clean)
                return "\n".join(cleaned)
    except Exception as e:
        print(f"Web search failed: {e}")
    return ""


def get_llm():
    """
    Utility helper to initialize the LLM from available provider environments.
    """
    from app.core.config import settings
    # 1. Attempt Google Gemini Setup
    gemini_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=gemini_key
        )
    # 2. Attempt OpenAI Setup
    openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if openai_key:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=openai_key
        )
    # 3. Attempt Groq Setup
    groq_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if groq_key:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            groq_api_key=groq_key
        )
    return None


class RoadmapGenerator:
    """
    AI Generator using Web Search, LangChain, and Pydantic structured output
    to build personalized transition pathways.
    """

    def generate_roadmap(
        self, parsed_resume: Dict[str, Any], target_role: str, missing_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate candidate details, target role, and missing skills to compile a customized career learning pathway.
        Does not generate generic pathways.
        """
        llm = get_llm()
        if llm is not None:
            try:
                structured_llm = llm.with_structured_output(RoadmapAIOutput)
                
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", (
                        "You are an expert career transition coach and technical mentor.\n"
                        "Your task is to generate a highly personalized, structured learning roadmap "
                        "designed to help a candidate transition into a target role.\n"
                        "You MUST generate the roadmap ONLY from: the candidate's Resume JSON, the Target Role, and their specific Missing Skills.\n"
                        "Focus entirely on teaching the missing skills and closing the gap. Do NOT generate generic roadmaps.\n"
                        "Create a sequenced milestone path with actionable tasks tailored specifically to their background.\n"
                        "For every task, you MUST populate the 'resources' field with 2-3 high-quality direct URLs to study it "
                        "(e.g., YouTube results: 'https://www.youtube.com/results?search_query=...', official site links, or guides)."
                    )),
                    ("user", (
                        "Target Role: {target_role}\n\n"
                        "Candidate Specific Missing Skills: {missing_skills}\n\n"
                        "Candidate Resume JSON:\n{parsed_resume}\n\n"
                        "Generate a personalized learning roadmap matching the structured output schema."
                    ))
                ])
                
                chain = prompt_template | structured_llm
                result = chain.invoke({
                    "target_role": target_role,
                    "missing_skills": ", ".join(missing_skills) if missing_skills else "None (Fully matched). Focus on advanced specialization.",
                    "parsed_resume": json.dumps(parsed_resume, indent=2, ensure_ascii=False) if isinstance(parsed_resume, dict) else str(parsed_resume),
                })
                
                return {
                    "title": result.title,
                    "description": result.description,
                    "milestones": [
                        {
                            "title": m.title,
                            "description": m.description,
                            "tasks": [
                                {
                                    "title": t.title,
                                    "description": t.description,
                                    "resources": t.resources if hasattr(t, "resources") else []
                                } for t in m.tasks
                            ]
                        } for m in result.milestones
                    ]
                }
            except Exception as e:
                print(f"Error calling LLM: {e}. Falling back to default pathway.")

        # Fallback dynamically constructed using missing skills
        milestones = []
        if missing_skills:
            # Group missing skills into 2 phases
            half = len(missing_skills) // 2 if len(missing_skills) > 1 else 1
            skills_p1 = missing_skills[:half]
            skills_p2 = missing_skills[half:]
            
            milestones = [
                {
                    "title": f"Phase 1: Core Skill Acquisition",
                    "description": f"Master initial core gaps: {', '.join(skills_p1)}",
                    "tasks": [
                        {
                            "title": f"Study {s}",
                            "description": f"Learn foundational concepts and theory behind {s}.",
                            "resources": [f"https://www.youtube.com/results?search_query={s.replace(' ', '+')}+tutorial"]
                        } for s in skills_p1
                    ]
                }
            ]
            if skills_p2:
                milestones.append({
                    "title": f"Phase 2: Advanced Integration & Application",
                    "description": f"Master remaining gaps and build projects: {', '.join(skills_p2)}",
                    "tasks": [
                        {
                            "title": f"Implement {s}",
                            "description": f"Build practical hands-on application demonstrating proficiency in {s}.",
                            "resources": [f"https://www.youtube.com/results?search_query={s.replace(' ', '+')}+practice+project"]
                        } for s in skills_p2
                    ]
                })
        else:
            # 100% matched, focus on advanced specialization project
            milestones = [
                {
                    "title": f"Phase 1: Advanced Specialization in {target_role}",
                    "description": "Candidate already possesses required skills. Focus on deep-dive optimization and engineering benchmarks.",
                    "tasks": [
                        {
                            "title": "System-Level Architecture Analysis",
                            "description": "Evaluate bottlenecks in existing setups and research next-generation standards.",
                            "resources": [f"https://www.youtube.com/results?search_query={target_role.replace(' ', '+')}+advanced+architecture"]
                        }
                    ]
                }
            ]

        return {
            "title": f"AI Transition Roadmap to {target_role}",
            "description": f"An AI-aligned training blueprint custom designed to transition your profile skills into a {target_role} specialist position by targeting specific gaps.",
            "milestones": milestones
        }


# Expose generator singleton
roadmap_generator = RoadmapGenerator()
