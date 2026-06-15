import os
import re
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
        self, parsed_resume: Dict[str, Any], target_role: str
    ) -> Dict[str, Any]:
        """
        Evaluate candidate details and target role to compile a customized career learning pathway.
        Queries live web search first, then uses LLM to synthesize it. Falls back to search-based
        mockup model if API keys are missing.
        """
        # Fetch live career data from web search
        web_requirements = search_role_requirements_on_web(target_role)
        
        llm = get_llm()
        if llm is not None:
            try:
                structured_llm = llm.with_structured_output(RoadmapAIOutput)
                
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", (
                        "You are an expert career transition coach and technical mentor.\n"
                        "Your task is to generate a highly personalized, structured learning roadmap "
                        "for a user trying to transition from their current profile to a target role.\n"
                        "Use the provided real-time Web Search Requirements to align with industry expectations "
                        "for the role, then compare them against their parsed resume data to design a phased learning roadmap.\n"
                        "Create a sequenced milestone path with actionable tasks.\n"
                        "For every task, you MUST populate the 'resources' field with 2-3 high-quality direct URLs to study it "
                        "(e.g., YouTube results: 'https://www.youtube.com/results?search_query=...', official site links, or guides)."
                    )),
                    ("user", (
                        "Target Role: {target_role}\n\n"
                        "Real-time Web Search Requirements:\n{web_requirements}\n\n"
                        "Candidate Resume Data:\n{parsed_resume}\n"
                        "Candidate Extracted Skills: {skills}\n\n"
                        "Generate a personalized learning roadmap matching the structured output schema."
                    ))
                ])
                
                chain = prompt_template | structured_llm
                result = chain.invoke({
                    "target_role": target_role,
                    "web_requirements": web_requirements or "Not available.",
                    "parsed_resume": str(parsed_resume),
                    "skills": ", ".join(parsed_resume.get("skills", [])),
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

        # Fallback dynamically constructed using web requirements
        milestones = []
        if web_requirements:
            lines = [l.strip() for l in web_requirements.split("\n") if len(l.strip()) > 30]
            if len(lines) >= 3:
                milestones = [
                    {
                        "title": f"Phase 1: {target_role} Core Foundations",
                        "description": "Establish core industry-standard definitions, frameworks, and syntax.",
                        "tasks": [
                            {"title": "Foundational Competencies", "description": lines[0][:200], "resources": [f"https://www.youtube.com/results?search_query={target_role.replace(' ', '+')}+fundamentals", "https://en.wikipedia.org/wiki/Special:Search?search=" + target_role.replace(" ", "+")]},
                            {"title": "Essential Tools Integration", "description": lines[1][:200], "resources": [f"https://www.youtube.com/results?search_query={target_role.replace(' ', '+')}+tools"]}
                        ]
                    },
                    {
                        "title": "Phase 2: Operational Applications",
                        "description": "Deep dive into execution practices and intermediate tooling expectations.",
                        "tasks": [
                            {"title": "Core Workflows Mastery", "description": lines[2][:200], "resources": [f"https://www.youtube.com/results?search_query={target_role.replace(' ', '+')}+workflows"]},
                            {"title": "Advanced Methodologies", "description": lines[min(3, len(lines)-1)][:200], "resources": [f"https://www.youtube.com/results?search_query={target_role.replace(' ', '+')}+methodologies"]}
                        ]
                    },
                    {
                        "title": "Phase 3: Industry Synthesis & Capstone",
                        "description": "Apply learning to production workflows, optimizations, and validations.",
                        "tasks": [
                            {"title": "Production Deployment & Delivery", "description": lines[min(4, len(lines)-1)][:200], "resources": [f"https://www.youtube.com/results?search_query={target_role.replace(' ', '+')}+deployment"]},
                            {"title": "Lifecycle Optimization", "description": lines[min(5, len(lines)-1)][:200], "resources": [f"https://www.youtube.com/results?search_query={target_role.replace(' ', '+')}+optimization"]}
                        ]
                    }
                ]
                
        # Safe default if web requirements search returns nothing and no LLM is configured
        if not milestones:
            milestones = [
                {
                    "title": f"Phase 1: {target_role} Fundamentals",
                    "description": "Get started with core syntax, workflows, and version control foundations.",
                    "tasks": [
                        {"title": "Basic Skills Alignment", "description": f"Learn foundational concepts required to work as a {target_role}.", "resources": [f"https://www.youtube.com/results?search_query={target_role.replace(' ', '+')}+basics"]},
                        {"title": "Git & Tool Setup", "description": "Configure your development environment and master collaboration basics.", "resources": ["https://git-scm.com/doc", "https://www.youtube.com/results?search_query=git+github+tutorial"]}
                    ]
                },
                {
                    "title": "Phase 2: Database & Systems Integration",
                    "description": "Build intermediate projects and study storage schemas.",
                    "tasks": [
                        {"title": "Data Management", "description": "Master REST API integrations and structured data stores.", "resources": ["https://www.youtube.com/results?search_query=rest+api+database+basics"]},
                        {"title": "Security & Auth Essentials", "description": "Learn secure communication patterns and access control implementations.", "resources": ["https://www.youtube.com/results?search_query=oauth2+jwt+security+tutorial"]}
                    ]
                },
                {
                    "title": "Phase 3: Production QA & Delivery",
                    "description": "Launch projects into production and run quality checks.",
                    "tasks": [
                        {"title": "Testing & Debugging", "description": "Implement complete automated testing suites and handle error logs.", "resources": ["https://www.youtube.com/results?search_query=unit+testing+mocking+basics"]},
                        {"title": "Deployment Pipeline", "description": "Learn containerization and continuous integration strategies.", "resources": ["https://www.docker.com/", "https://www.youtube.com/results?search_query=ci+cd+docker+deployment"]}
                    ]
                }
            ]

        return {
            "title": f"AI Transition Roadmap to {target_role}",
            "description": f"An AI-aligned training blueprint custom designed to transition your profile skills into a {target_role} specialist position.",
            "milestones": milestones
        }


# Expose generator singleton
roadmap_generator = RoadmapGenerator()
