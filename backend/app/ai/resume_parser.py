import re
import pathlib
import fitz  # PyMuPDF
from typing import List, Dict, Any
from app.utils.exceptions import DomainException

# Common skill catalog for heuristic matching
COMMON_SKILLS = [
    "python", "javascript", "typescript", "golang", "java", "c++", "ruby", "rust",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "fastapi", "django", "flask", "express", "react", "next.js", "vue", "angular",
    "html", "css", "tailwind", "bootstrap",
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ansible", "jenkins", "git",
    "machine learning", "deep learning", "nlp", "pytorch", "tensorflow", "langchain", "openai"
]


class ResumeParser:
    """
    Parser utilizing PyMuPDF (fitz) for PDF extraction and heuristics/regular expressions
    to structure resume data.
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
        Heuristic-based parser using regex matching and section splitting.
        """
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        # 1. Heuristic for Name: First non-empty line that doesn't contain common resume noise
        name = "Unknown"
        for line in lines[:5]:
            # Ensure it is not an email, phone number, website link or contains typical section headers
            lower_line = line.lower()
            if (
                "@" not in line 
                and not re.search(r'\d{4,}', line) 
                and not any(hdr in lower_line for hdr in ["education", "experience", "skills", "summary", "contact"])
                and len(line.split()) <= 4
            ):
                name = line
                break

        # 2. Regex for Email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, raw_text)
        email = email_match.group(0) if email_match else "Unknown"

        # 3. Regex for Phone Number (matches standard variations)
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, raw_text)
        phone = phone_match.group(0) if phone_match else "Unknown"

        # 4. Keyword Match for Skills
        matched_skills = []
        lower_raw_text = raw_text.lower()
        for skill in COMMON_SKILLS:
            # Word boundary check to avoid partial matching (e.g. "git" matching "digital")
            pattern = rf"\b{re.escape(skill)}\b"
            if re.search(pattern, lower_raw_text):
                matched_skills.append(skill.title() if len(skill) > 3 or skill in ["git", "sql", "aws", "gcp", "nlp"] else skill.upper())

        # 5. Heuristic Section Splitting for Education and Experience
        education_items = self._extract_section_items(lines, ["education", "academic history", "academics"])
        experience_items = self._extract_section_items(lines, ["experience", "work history", "employment", "professional experience"])

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": matched_skills,
            "education": education_items,
            "experience": experience_items,
        }

    def _extract_section_items(self, lines: List[str], headers: List[str]) -> List[str]:
        """
        Extract bullet list or paragraph items from a section identified by header tags.
        """
        section_items = []
        in_section = False
        
        # Other potential headers to signal the end of this section
        all_other_stop_headers = ["education", "experience", "work history", "employment", "skills", "projects", "certifications", "languages", "summary", "contact", "about me"]
        
        for line in lines:
            lower_line = line.lower()
            
            # Check if entering the targeted section
            if any(lower_line.startswith(hdr) or lower_line == hdr for hdr in headers):
                in_section = True
                continue
            
            if in_section:
                # If we encounter a line matching another section header, we stop parsing the current one
                if any(lower_line.startswith(stop_hdr) or lower_line == stop_hdr for stop_hdr in all_other_stop_headers):
                    break
                
                # Append line if it's descriptive
                if len(line) > 5:
                    # Strip bullet point markers (-, *, •)
                    clean_line = re.sub(r'^[\-\*•\s\d\.\)]+', '', line).strip()
                    if clean_line:
                        section_items.append(clean_line)
                        
            # Limit the size of parsed lines per section to avoid spilling
            if len(section_items) >= 15:
                break
                
        return section_items


# Expose parser singleton
resume_parser = ResumeParser()
