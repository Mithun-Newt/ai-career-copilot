import uuid
import logging
import json
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.career_chat import CareerChat
from app.models.career_message import CareerMessage
from app.models.resume import Resume
from app.models.profile import Profile
from app.models.roadmap import Roadmap
from app.ai.roadmap_generator import get_llm
from app.core.config import settings
from app.utils.exceptions import EntityNotFoundError, ForbiddenError
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Configure logging
logger = logging.getLogger("career_coach")
logger.setLevel(logging.INFO)


class CareerCoachService:
    """
    Business service orchestrating AI career coach session chats, memory, and context.
    """

    def get_user_chats(self, db: Session, *, user_id: uuid.UUID) -> List[CareerChat]:
        """
        List all career coaching chat sessions belonging to a user.
        """
        try:
            return db.query(CareerChat).filter(CareerChat.user_id == user_id).order_by(CareerChat.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Database failure listing chats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database failure listing chat sessions: {str(e)}"
            )

    def get_chat_session(self, db: Session, *, user_id: uuid.UUID, chat_id: uuid.UUID) -> CareerChat:
        """
        Retrieve a single chat session with its nested messages, checking user ownership.
        """
        try:
            chat = db.query(CareerChat).filter(CareerChat.id == chat_id).first()
        except Exception as e:
            logger.error(f"Database failure fetching chat session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database failure fetching chat session: {str(e)}"
            )
            
        if not chat:
            raise EntityNotFoundError("CareerChat", chat_id)
        if chat.user_id != user_id:
            raise ForbiddenError("You do not have access to this chat session")
        return chat

    def delete_chat_session(self, db: Session, *, user_id: uuid.UUID, chat_id: uuid.UUID) -> None:
        """
        Delete a career chat session.
        """
        chat = self.get_chat_session(db, user_id=user_id, chat_id=chat_id)
        try:
            db.delete(chat)
            db.commit()
        except Exception as e:
            logger.error(f"Database failure deleting chat: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database failure deleting chat session: {str(e)}"
            )

    def chat_with_coach(
        self, db: Session, *, user_id: uuid.UUID, message: str, chat_id: Optional[uuid.UUID] = None
    ) -> dict:
        """
        Interact with the career coach. Builds dynamic profile context,
        manages database-persisted chat memory, and invokes LangChain.
        """
        # Log: Request Received
        logger.info(f"Career Coach Request Received - User: {user_id}, Message: '{message}', Session ID: {chat_id}")
        print(f"Career Coach Request Received - User: {user_id}, Message: '{message}', Session ID: {chat_id}")

        # 1. Resolve or initialize the Chat Session
        try:
            if chat_id:
                chat = db.query(CareerChat).filter(CareerChat.id == chat_id).first()
                if not chat:
                    logger.error(f"Chat thread not found: {chat_id}")
                    raise HTTPException(status_code=404, detail=f"CareerChat with ID {chat_id} not found.")
                if chat.user_id != user_id:
                    logger.error(f"Access denied to chat session: {chat_id} for user {user_id}")
                    raise HTTPException(status_code=403, detail="Access denied to this chat session.")
            else:
                title = message[:40] + "..." if len(message) > 40 else message
                chat = CareerChat(user_id=user_id, title=title)
                db.add(chat)
                db.commit()
                db.refresh(chat)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Database failure resolving chat session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database failure resolving chat session: {str(e)}"
            )

        # 2. Persist User's Current Message
        try:
            user_msg = CareerMessage(chat_id=chat.id, role="user", content=message)
            db.add(user_msg)
            db.commit()
        except Exception as e:
            logger.error(f"Database failure persisting user message: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database failure persisting message: {str(e)}"
            )

        # 3. Compile Dynamic Profile Context
        logger.info("Building Context")
        print("Building Context")
        context_str = self._build_dynamic_context(db, user_id)
        logger.info(f"Context Built:\n{context_str}")

        # 4. Construct Conversation Memory from Database History
        try:
            history = []
            past_messages = (
                db.query(CareerMessage)
                .filter(CareerMessage.chat_id == chat.id, CareerMessage.id != user_msg.id)
                .order_by(CareerMessage.created_at.asc())
                .all()
            )
            for msg in past_messages:
                if msg.role == "user":
                    history.append(HumanMessage(content=msg.content))
                else:
                    history.append(AIMessage(content=msg.content))
        except Exception as e:
            logger.error(f"Database failure loading conversation history: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database failure loading chat history: {str(e)}"
            )

        # 5. LLM Initialization and Verification
        llm = get_llm()
        if llm is None:
            # Check which API key is missing
            has_gemini = bool(settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY)
            has_openai = bool(settings.OPENAI_API_KEY)
            has_groq = bool(settings.GROQ_API_KEY)
            
            error_detail = "Missing API key: No LLM provider api key found. Please configure GEMINI_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY in your .env file."
            logger.error(error_detail)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )

        # 6. Call LLM using LangChain
        logger.info("Calling LLM")
        print("Calling LLM")
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are an expert, highly encouraging AI Career Coach. Your goal is to guide the candidate "
                    "on transitions, learning strategies, and timeline analysis.\n"
                    "Answer queries by heavily aligning your advice with the candidate's profile, parsed resume, skill gap analysis, ATS analysis, and active roadmap below.\n\n"
                    "=== Candidate Profile Context ===\n"
                    "{context}\n"
                    "=================================\n\n"
                    "CRITICAL REQUIREMENT: You must NEVER answer from generic prompts or give canned, generic advice if the candidate's profile context is populated. "
                    "If candidate data exists in the context above, you MUST base your response entirely on their specific details (their skills, experience, projects, education, roadmap, skill gap analysis, and ATS evaluation). "
                    "Cite their specific skills and steps from their roadmap, and refer to their actual strengths and weaknesses. Generic, non-contextualized advice is strictly prohibited and unacceptable."
                )),
                MessagesPlaceholder(variable_name="history"),
                ("user", "{message}")
            ])
            
            chain = prompt | llm
            response_obj = chain.invoke({
                "context": context_str,
                "history": history,
                "message": message
            })
            ai_response = response_obj.content
            logger.info("LLM Response Received")
            print("LLM Response Received")
        except Exception as e:
            error_detail = f"LangChain invocation failure: {str(e)}"
            logger.error(error_detail)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )

        # 7. Persist and commit the Coach's Message
        try:
            coach_msg = CareerMessage(chat_id=chat.id, role="assistant", content=ai_response)
            db.add(coach_msg)
            db.commit()
        except Exception as e:
            logger.error(f"Database failure saving coach response: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database failure saving AI response: {str(e)}"
            )

        logger.info("Returning Response")
        print("Returning Response")
        return {
            "response": ai_response,
            "chat_id": chat.id
        }

    def _build_dynamic_context(self, db: Session, user_id: uuid.UUID) -> str:
        """
        Gathers profile, parsed resume, skill gap analysis, ATS analysis, and roadmap details to build coaching context.
        """
        # 1. Fetch Profile Info
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        profile_info = "No profile set up."
        if profile:
            profile_info = (
                f"Title: {profile.title or 'N/A'}\n"
                f"Experience: {profile.experience_years or 0} years\n"
                f"Bio: {profile.bio or 'N/A'}"
            )

        # 2. Fetch Active/Latest Resume & Full Parsed Resume JSON
        resume = db.query(Resume).filter(Resume.user_id == user_id, Resume.is_active == True).first()
        if not resume:
            resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).first()
        
        resume_info = "No resume uploaded."
        parsed_resume_json = "No parsed resume data available."
        resume_skills = []
        
        if resume and resume.parsed_data:
            resume_skills = resume.parsed_data.get("skills", [])
            parsed_resume_json = json.dumps(resume.parsed_data, indent=2, ensure_ascii=False)
            resume_info = (
                f"Filename: {resume.filename}\n"
                f"Candidate Name: {resume.parsed_data.get('name', 'N/A')}\n"
                f"Title: {resume.parsed_data.get('title', 'N/A')}\n"
                f"Bio: {resume.parsed_data.get('bio', 'N/A')}\n"
                f"Extracted Skills: {', '.join(resume_skills)}"
            )

        # 3. Fetch Active Roadmap
        roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id).order_by(Roadmap.created_at.desc()).first()
        roadmap_info = "No active roadmap."
        target_role = None
        if roadmap:
            target_role = roadmap.target_role
            tasks_list = [
                f"Step {t.sequence}: {t.title} - {t.description or 'No description'} (Status: {t.status})"
                for t in roadmap.tasks
            ]
            roadmap_info = (
                f"Target Role: {target_role}\n"
                f"Roadmap Title: {roadmap.title}\n"
                f"Roadmap Description: {roadmap.description or 'N/A'}\n"
                f"Steps:\n" + "\n".join(tasks_list)
            )

        # 4. Perform Dynamic Skill Gap Analysis
        skill_gap_info = "No skill gap analysis available (requires an active resume and target role)."
        if resume and target_role:
            try:
                from app.ai.skill_gap_analyzer import skill_gap_analyzer
                gap_analysis = skill_gap_analyzer.analyze_gap(
                    user_skills=resume_skills,
                    target_role=target_role,
                    user_id=user_id,
                    resume_id=resume.id,
                    parsed_resume=resume.parsed_data,
                    raw_resume_text=resume.raw_text
                )
                skill_gap_info = (
                    f"Match Percentage Score: {gap_analysis.get('match_percentage', 0)}%\n"
                    f"Core Required Skills: {', '.join(gap_analysis.get('core_required', []))}\n"
                    f"Core Matched Skills: {', '.join(gap_analysis.get('core_matched', []))}\n"
                    f"Supporting Required Skills: {', '.join(gap_analysis.get('supporting_required', []))}\n"
                    f"Supporting Matched Skills: {', '.join(gap_analysis.get('supporting_matched', []))}\n"
                    f"Transferable Required Skills: {', '.join(gap_analysis.get('transferable_required', []))}\n"
                    f"Transferable Matched Skills: {', '.join(gap_analysis.get('transferable_matched', []))}\n"
                    f"Missing Skills: {', '.join(gap_analysis.get('missing_skills', []))}\n"
                    f"Strengths Identified: {', '.join(gap_analysis.get('strengths', []))}\n"
                    f"Weaknesses/Gaps Identified: {', '.join(gap_analysis.get('weaknesses', []))}\n"
                    f"Immediate Learning Priorities: {', '.join(gap_analysis.get('learning_priorities', []))}\n"
                    f"Scoring Breakdown & Match Reasoning:\n{gap_analysis.get('reasoning', 'N/A')}"
                )
            except Exception as e:
                skill_gap_info = f"Failed to perform dynamic skill gap analysis: {str(e)}"

        # 5. Fetch Latest ATS Analysis
        from app.models.ats_analysis import ATSAnalysis
        ats_record = db.query(ATSAnalysis).filter(ATSAnalysis.user_id == user_id).order_by(ATSAnalysis.created_at.desc()).first()
        ats_info = "No ATS analysis results found."
        if ats_record:
            ats_info = (
                f"ATS Score: {ats_record.ats_score}/100\n"
                f"Match Percentage: {ats_record.match_percentage}%\n"
                f"Missing Skills: {', '.join(ats_record.missing_skills)}\n"
                f"Missing Keywords: {', '.join(ats_record.missing_keywords)}\n"
                f"Strengths: {', '.join(ats_record.strengths)}\n"
                f"Weaknesses: {', '.join(ats_record.weaknesses)}\n"
                f"Recommendations: {json.dumps(ats_record.recommendations, indent=2, ensure_ascii=False)}"
            )

        return (
            f"--- Candidate Profile Info ---\n{profile_info}\n\n"
            f"--- Full Parsed Resume JSON ---\n{parsed_resume_json}\n\n"
            f"--- Live Skill Gap Analysis ---\n{skill_gap_info}\n\n"
            f"--- Latest ATS Analysis ---\n{ats_info}\n\n"
            f"--- Active Career Roadmap ---\n{roadmap_info}"
        )


# Expose singleton service
career_coach_service = CareerCoachService()
