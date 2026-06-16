import re
import pathlib
import json
import fitz  # PyMuPDF
from typing import List, Dict, Any
from app.utils.exceptions import DomainException

class ResumeParser:
    """
    Parser utilizing PyMuPDF (fitz) for PDF extraction and LLM structured parsing.
    """

    def extract_text(self, file_path: str) -> str:
        """
        Open a PDF resume using PyMuPDF and extract all readable text pages.
        Raises DomainException if the file is corrupted, unreadable, or empty.
        """
        path = pathlib.Path(file_path)
        if not path.is_file():
            raise DomainException(f"Resume file path '{file_path}' does not exist.")

        try:
            doc = fitz.open(str(path))
        except Exception as e:
            raise DomainException(f"Failed to open PDF document (corrupted file?): {str(e)}")

        if len(doc) == 0:
            doc.close()
            raise DomainException("The uploaded PDF resume contains no pages.")

        extracted_text_list = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text:
                extracted_text_list.append(text)

        doc.close()
        full_text = "\n".join(extracted_text_list).strip()

        if not full_text:
            raise DomainException(
                "PDF is empty or text could not be extracted (e.g. image-only scanned PDF without OCR)."
            )

        return full_text

    def parse_resume(self, raw_text: str) -> Dict[str, Any]:
        """
        AI-first resume parser with raw JSON prompt fallback.
        No heuristic catalogs are used.
        """
        parsed_data = None
        from app.ai.roadmap_generator import get_llm
        llm = get_llm()
        if llm is None:
            raise RuntimeError("LLM Provider is not configured. Resume parsing requires an active LLM.")

        try:
            from pydantic import BaseModel, Field
            from langchain_core.prompts import ChatPromptTemplate

            class ResumeFullExtraction(BaseModel):
                name: str = Field(description="Candidate's full name.")
                email: str = Field(description="Candidate's email address.")
                phone: str = Field(description="Candidate's phone number.")
                title: str = Field(description="Candidate's professional title or role (e.g. Software Engineer, VLSI Design Engineer).")
                bio: str = Field(description="A brief 2-3 sentence biography summary of the candidate's core skills and background.")
                experience_years: int = Field(description="Estimated total years of professional experience as an integer.")
                education: List[str] = Field(description="List of education history entries.")
                projects: List[str] = Field(description="List of projects mentioned in the resume.")
                experience: List[str] = Field(description="List of professional work experience entries.")
                certifications: List[str] = Field(description="List of certifications.")
                technical_skills: List[str] = Field(description="List of technical skills (e.g. Python, Verilog, C++).")
                tools: List[str] = Field(description="List of developer/engineering tools (e.g. Git, Docker, Vivado, Cadence).")
                frameworks: List[str] = Field(description="List of software/modelling frameworks (e.g. FastAPI, React, PyTorch).")
                domain_skills: List[str] = Field(description="List of engineering or conceptual domain skills (e.g. Digital VLSI Design, FPGA Design, Machine Learning).")

            structured_llm = llm.with_structured_output(ResumeFullExtraction)
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are an expert resume parser. Extract a comprehensive, structured representation "
                    "of the candidate's details from the resume text.\n"
                    "Extract details accurately without inventing elements."
                )),
                ("user", "{resume_text}")
            ])
            chain = prompt_template | structured_llm
            result = chain.invoke({"resume_text": raw_text})
            
            skills_flat = list(dict.fromkeys(result.technical_skills + result.tools + result.frameworks + result.domain_skills))
            parsed_data = {
                "name": result.name.strip() if result.name else "Unknown",
                "email": result.email.strip() if result.email else "Unknown",
                "phone": result.phone.strip() if result.phone else "Unknown",
                "title": result.title.strip() if result.title else "Professional Specialist",
                "bio": result.bio.strip() if result.bio else "Passionate specialist in their domain.",
                "experience_years": int(result.experience_years) if result.experience_years is not None else 0,
                "education": [e.strip() for e in result.education if e.strip()],
                "projects": [p.strip() for p in result.projects if p.strip()],
                "experience": [exp.strip() for exp in result.experience if exp.strip()],
                "certifications": [c.strip() for c in result.certifications if c.strip()],
                "technical_skills": [s.strip() for s in result.technical_skills if s.strip()],
                "tools": [t.strip() for t in result.tools if t.strip()],
                "frameworks": [f.strip() for f in result.frameworks if f.strip()],
                "domain_skills": [d.strip() for d in result.domain_skills if d.strip()],
                "skills": skills_flat
            }
        except Exception as e:
            print(f"LLM full resume extraction failed: {e}. Attempting JSON fallback...")
            try:
                from langchain_core.prompts import ChatPromptTemplate
                raw_prompt = ChatPromptTemplate.from_messages([
                    ("system", (
                        "You are an expert resume parser. Extract a comprehensive, structured representation of the candidate's details.\n"
                        "You MUST respond ONLY with a raw JSON block. Do not write any markdown code fences, headers, or text outside the JSON.\n"
                        "The JSON must have the following keys at the root level:\n"
                        "- name: string\n"
                        "- email: string\n"
                        "- phone: string\n"
                        "- title: string\n"
                        "- bio: string\n"
                        "- experience_years: integer\n"
                        "- education: list of strings\n"
                        "- projects: list of strings\n"
                        "- experience: list of strings\n"
                        "- certifications: list of strings\n"
                        "- technical_skills: list of strings\n"
                        "- tools: list of strings\n"
                        "- frameworks: list of strings\n"
                        "- domain_skills: list of strings"
                    )),
                    ("user", "{resume_text}")
                ])
                raw_chain = raw_prompt | llm
                raw_response = raw_chain.invoke({"resume_text": raw_text})
                raw_content = raw_response.content
                json_match = re.search(r"(\{.*\})", raw_content, re.DOTALL)
                if json_match:
                    parsed_json = json.loads(json_match.group(1))
                    tech = [s.strip() for s in parsed_json.get("technical_skills", []) if isinstance(s, str)]
                    tools = [t.strip() for t in parsed_json.get("tools", []) if isinstance(t, str)]
                    framer = [f.strip() for f in parsed_json.get("frameworks", []) if isinstance(f, str)]
                    domain = [d.strip() for d in parsed_json.get("domain_skills", []) if isinstance(d, str)]
                    skills_flat = list(dict.fromkeys(tech + tools + framer + domain))
                    
                    parsed_data = {
                        "name": parsed_json.get("name", "Unknown").strip(),
                        "email": parsed_json.get("email", "Unknown").strip(),
                        "phone": parsed_json.get("phone", "Unknown").strip(),
                        "title": parsed_json.get("title", "Professional Specialist").strip(),
                        "bio": parsed_json.get("bio", "Passionate specialist in their domain.").strip(),
                        "experience_years": int(parsed_json.get("experience_years", 0)),
                        "education": [e.strip() for e in parsed_json.get("education", []) if isinstance(e, str)],
                        "projects": [p.strip() for p in parsed_json.get("projects", []) if isinstance(p, str)],
                        "experience": [exp.strip() for exp in parsed_json.get("experience", []) if isinstance(exp, str)],
                        "certifications": [c.strip() for c in parsed_json.get("certifications", []) if isinstance(c, str)],
                        "technical_skills": tech,
                        "tools": tools,
                        "frameworks": framer,
                        "domain_skills": domain,
                        "skills": skills_flat
                    }
                else:
                    raise ValueError("Could not find a valid JSON object block in LLM response.")
            except Exception as final_err:
                raise RuntimeError(f"AI Resume Parser failed completely: {final_err}")

        return parsed_data


# Expose parser singleton
resume_parser = ResumeParser()
