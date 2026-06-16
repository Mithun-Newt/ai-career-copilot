import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.ai.roadmap_generator import get_llm

class SkillIntelligenceRebuildModel(BaseModel):
    core_required: List[str] = Field(description="Direct core domain/technical skills required for the target role.")
    core_matched: List[str] = Field(description="Sublist of core_required that the candidate has semantically demonstrated in their resume. MUST be a subset of core_required.")
    supporting_required: List[str] = Field(description="Supporting technologies, programming languages, databases, tools, or frameworks expected for this role.")
    supporting_matched: List[str] = Field(description="Sublist of supporting_required that the candidate has semantically demonstrated in their resume. MUST be a subset of supporting_required.")
    transferable_required: List[str] = Field(description="General engineering concepts, soft skills, collaboration, or mathematics expected for this role.")
    transferable_matched: List[str] = Field(description="Sublist of transferable_required that the candidate has semantically demonstrated in their resume. MUST be a subset of transferable_required.")
    strengths: List[str] = Field(description="Key strengths aligned to target role requirements.")
    weaknesses: List[str] = Field(description="Key gaps relative to target role requirements.")
    learning_priorities: List[str] = Field(description="Immediate learning priority recommendations.")
    focus_areas: Dict[str, List[str]] = Field(description="Only the missing required skills grouped by dynamic domain categories (e.g. 'API Frameworks': ['FastAPI']). Do NOT include matched skills here.")
    semantic_match_reasoning: str = Field(description="Detailed qualitative explanation of how candidate skills matched semantically (e.g. mapping synonyms or equivalent concepts).")


class SkillGapAnalyzer:
    """
    Rebuilt Skill Intelligence Analyzer using dynamic LLM-only extraction and semantic matching.
    Never uses hardcoded skill catalogs, static matching tables, or exact string matching logic.
    Shows the step-by-step reasoning used for match score calculation.
    """

    def __init__(self):
        # In-memory cache to save token costs and speed up Dashboard requests
        # Mapped by: (user_id_str, resume_id_str, target_role_str) -> gap_analysis_result_dict
        self._cache: Dict[tuple, Dict[str, Any]] = {}

    def analyze_gap(
        self,
        user_skills: List[str],
        target_role: str,
        user_id: Optional[str] = None,
        resume_id: Optional[str] = None,
        parsed_resume: Optional[Dict[str, Any]] = None,
        raw_resume_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Performs AI-driven gap analysis matching candidate details against dynamically extracted target role requirements.
        """
        # 1. Attempt Cache Resolution
        cache_key = (
            str(user_id) if user_id else "anonymous",
            str(resume_id) if resume_id else "profile",
            target_role.strip().lower()
        )
        if cache_key in self._cache:
            print(f"SkillGapAnalyzer: serving cached results for {cache_key}")
            return self._cache[cache_key]

        llm = get_llm()
        if llm is None:
            raise RuntimeError(
                "LLM Provider is not configured. Please set GEMINI_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY."
            )

        # Prepare candidate resume context for the LLM
        # Use parsed_resume (Resume JSON) if available, otherwise construct one from user_skills
        if not parsed_resume:
            parsed_resume = {
                "skills": user_skills,
                "technical_skills": user_skills,
                "tools": [],
                "frameworks": [],
                "domain_skills": []
            }
        
        resume_json_str = json.dumps(parsed_resume, indent=2)
        raw_text_content = raw_resume_text if raw_resume_text else "No raw resume text available."

        result_model = None

        try:
            # Try structured LLM call first
            structured_llm = llm.with_structured_output(SkillIntelligenceRebuildModel)
            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are an advanced AI Career Matcher.\n"
                    "Given a candidate's resume (in structured JSON format), their raw resume text, and a Target Role:\n"
                    "1. Extract the required skills for the target role and categorize them into:\n"
                    "   - core_required (Direct domain requirements, most important factor)\n"
                    "   - supporting_required (Complementary technologies, programming languages, databases, tools, or frameworks)\n"
                    "   - transferable_required (General engineering concepts, soft skills, collaboration, mathematics)\n"
                    "   Extract 5-8 skills for each category.\n"
                    "2. Perform semantic matching: Evaluate the candidate's resume JSON and raw resume text to see if they possess these required skills. "
                    "You must check ALL fields of the resume JSON (skills, experience, projects, education) and the raw resume text.\n"
                    "Match semantically (e.g., if the resume has 'Vivado' and 'RTL coding', match 'Xilinx Vivado' and 'RTL Design' if those are required).\n"
                    "Be thorough but STRICT: if a required skill is listed or demonstrated in the resume, include it in the matched list. "
                    "CRITICAL: Do NOT hallucinate matches. A required skill MUST NOT be in the matched list if the candidate's resume or skills do not contain that skill or a direct semantic equivalent. "
                    "For example, a candidate with only VLSI design engineering experience does NOT match digital marketing skills like 'SEO', 'Facebook Ads', or 'Google Analytics'—these must be left out of the matched lists.\n"
                    "3. The lists of matched skills (core_matched, supporting_matched, transferable_matched) MUST contain only items that are present in the corresponding required lists (core_required, supporting_required, transferable_required), using the exact same spelling as the required items. Do not invent new skills or include unmatched skills.\n"
                    "4. Identify strengths, weaknesses, and immediate learning priorities.\n"
                    "5. Dynamically group only the missing skills (skills in the required lists that are NOT in the matched lists) into focus areas based on their domains. Do not use any hardcoded categories. Do not include any matched skills here.\n"
                    "6. Provide a qualitative explanation of the semantic matching results in semantic_match_reasoning."
                )),
                ("user", "Target Role: {target_role}\n\nCandidate Resume JSON:\n{resume_json}\n\nCandidate Raw Resume Text:\n{raw_resume_text}")
            ])
            chain = prompt | structured_llm
            result_model = chain.invoke({
                "target_role": target_role,
                "resume_json": resume_json_str,
                "raw_resume_text": raw_text_content
            })
        except Exception as e:
            print(f"Skill Intelligence structured output failed: {e}. Attempting JSON fallback...")
            try:
                raw_prompt = ChatPromptTemplate.from_messages([
                    ("system", (
                        "You are an advanced AI Career Matcher.\n"
                        "Given a candidate's resume (in structured JSON format), their raw resume text, and a Target Role, extract and analyze skill gaps.\n"
                        "You MUST respond ONLY with a raw JSON block. Do not write any markdown code fences, headers, or text outside the JSON.\n"
                        "The JSON must have the following keys at the root level:\n"
                        "- core_required: list of strings\n"
                        "- core_matched: list of strings (must be a subset of core_required and strictly demonstrated in the resume)\n"
                        "- supporting_required: list of strings\n"
                        "- supporting_matched: list of strings (must be a subset of supporting_required and strictly demonstrated in the resume)\n"
                        "- transferable_required: list of strings\n"
                        "- transferable_matched: list of strings (must be a subset of transferable_required and strictly demonstrated in the resume)\n"
                        "- strengths: list of strings\n"
                        "- weaknesses: list of strings\n"
                        "- learning_priorities: list of strings\n"
                        "- focus_areas: dictionary where keys are dynamic category names and values are lists of missing skills only\n"
                        "- semantic_match_reasoning: string explaining the semantic match results"
                    )),
                    ("user", "Target Role: {target_role}\n\nCandidate Resume JSON:\n{resume_json}\n\nCandidate Raw Resume Text:\n{raw_resume_text}\n\nGenerate the raw JSON response block.")
                ])
                raw_chain = raw_prompt | llm
                raw_response = raw_chain.invoke({
                    "target_role": target_role,
                    "resume_json": resume_json_str,
                    "raw_resume_text": raw_text_content
                })
                raw_content = raw_response.content
                json_match = re.search(r"(\{.*\})", raw_content, re.DOTALL)
                if json_match:
                    parsed_json = json.loads(json_match.group(1))
                    
                    class DummyResult:
                        pass
                    
                    result_model = DummyResult()
                    result_model.core_required = parsed_json.get("core_required", [])
                    result_model.core_matched = parsed_json.get("core_matched", [])
                    result_model.supporting_required = parsed_json.get("supporting_required", [])
                    result_model.supporting_matched = parsed_json.get("supporting_matched", [])
                    result_model.transferable_required = parsed_json.get("transferable_required", [])
                    result_model.transferable_matched = parsed_json.get("transferable_matched", [])
                    result_model.strengths = parsed_json.get("strengths", [])
                    result_model.weaknesses = parsed_json.get("weaknesses", [])
                    result_model.learning_priorities = parsed_json.get("learning_priorities", [])
                    result_model.focus_areas = parsed_json.get("focus_areas", {})
                    result_model.semantic_match_reasoning = parsed_json.get("semantic_match_reasoning", "Analysis complete.")
                else:
                    raise ValueError("Could not find a valid JSON object block in LLM fallback response.")
            except Exception as final_err:
                raise RuntimeError(f"Skill Intelligence Analyzer failed completely: {final_err}")

        # Post-process lists to ensure strict subset validity and strip whitespace
        core_req = [s.strip() for s in result_model.core_required if isinstance(s, str) and s.strip()]
        core_mat = [s.strip() for s in result_model.core_matched if isinstance(s, str) and s.strip() and s.strip() in core_req]
        
        supp_req = [s.strip() for s in result_model.supporting_required if isinstance(s, str) and s.strip()]
        supp_mat = [s.strip() for s in result_model.supporting_matched if isinstance(s, str) and s.strip() and s.strip() in supp_req]
        
        trans_req = [s.strip() for s in result_model.transferable_required if isinstance(s, str) and s.strip()]
        trans_mat = [s.strip() for s in result_model.transferable_matched if isinstance(s, str) and s.strip() and s.strip() in trans_req]

        # Calculate exact weighted score in Python to prevent LLM mathematical hallucinations
        core_ratio = len(core_mat) / len(core_req) if core_req else 0.0
        supp_ratio = len(supp_mat) / len(supp_req) if supp_req else 0.0
        trans_ratio = len(trans_mat) / len(trans_req) if trans_req else 0.0
        
        weighted_score = (0.70 * core_ratio + 0.20 * supp_ratio + 0.10 * trans_ratio) * 100
        match_percentage = min(max(round(weighted_score), 0), 100)

        # Flat lists for UI compatibility
        matched_all = list(dict.fromkeys(core_mat + supp_mat + trans_mat))
        
        missing_core = [s for s in core_req if s not in core_mat]
        missing_supp = [s for s in supp_req if s not in supp_mat]
        missing_trans = [s for s in trans_req if s not in trans_mat]
        missing_all = list(dict.fromkeys(missing_core + missing_supp + missing_trans))

        # Dynamic, filtered focus areas mapping only actual missing skills
        clean_focus_areas = {}
        if isinstance(result_model.focus_areas, dict):
            for category, skills in result_model.focus_areas.items():
                if isinstance(skills, list):
                    filtered = [s.strip() for s in skills if isinstance(s, str) and s.strip() in missing_all]
                    if filtered:
                        clean_focus_areas[category] = filtered

        # Construct step-by-step scoring rationale breakdown
        reasoning_str = (
            f"### Score Calculation Reasoning Breakdown ({match_percentage}% Match)\n\n"
            f"The overall readiness score is computed using a weighted domain model:\n"
            f"- **Core Skills** (70% weight): {len(core_mat)}/{len(core_req)} matched "
            f"({core_ratio*100:.1f}% ratio) -> Contribution: {0.70 * core_ratio * 100:.1f}%\n"
            f"- **Supporting Skills** (20% weight): {len(supp_mat)}/{len(supp_req)} matched "
            f"({supp_ratio*100:.1f}% ratio) -> Contribution: {0.20 * supp_ratio * 100:.1f}%\n"
            f"- **Transferable Skills** (10% weight): {len(trans_mat)}/{len(trans_req)} matched "
            f"({trans_ratio*100:.1f}% ratio) -> Contribution: {0.10 * trans_ratio * 100:.1f}%\n\n"
            f"**Mathematical Scoring Calculation:**\n"
            f"({0.70 * core_ratio * 100:.1f}%) + ({0.20 * supp_ratio * 100:.1f}%) + ({0.10 * trans_ratio * 100:.1f}%) = **{weighted_score:.1f}%** (rounded to **{match_percentage}%**).\n\n"
            f"**AI Semantic Analysis:**\n"
            f"{result_model.semantic_match_reasoning.strip()}"
        )

        result_dict = {
            "core_required": core_req,
            "core_matched": core_mat,
            "supporting_required": supp_req,
            "supporting_matched": supp_mat,
            "transferable_required": trans_req,
            "transferable_matched": trans_mat,
            "matched_skills": matched_all,
            "missing_skills": missing_all,
            "match_percentage": match_percentage,
            "user_skills_count": len(user_skills),
            "target_skills_count": len(core_req) + len(supp_req) + len(trans_req),
            "focus_areas": clean_focus_areas,
            "strengths": [s.strip() for s in result_model.strengths if isinstance(s, str) and s.strip()],
            "weaknesses": [w.strip() for w in result_model.weaknesses if isinstance(w, str) and w.strip()],
            "learning_priorities": [lp.strip() for lp in result_model.learning_priorities if isinstance(lp, str) and lp.strip()],
            "reasoning": reasoning_str
        }

        # Cache the result before returning
        self._cache[cache_key] = result_dict
        return result_dict


# Expose analyzer singleton
skill_gap_analyzer = SkillGapAnalyzer()
