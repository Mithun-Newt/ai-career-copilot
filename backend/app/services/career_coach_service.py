import uuid
import logging
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
                    "Answer queries by heavily aligning your advice with the candidate's profile and active roadmap below.\n\n"
                    "=== Candidate Profile Context ===\n"
                    "{context}\n"
                    "=================================\n\n"
                    "Provide a professional, clear, and actionable mentoring response. Do not repeat a canned or generic advice response. Address user queries directly."
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
        Gathers profile, resume, skills, and roadmap details to build coaching context.
        """
        # Fetch profile
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        profile_info = "No profile set up."
        if profile:
            profile_info = f"Title: {profile.title or 'N/A'}\nExperience: {profile.experience_years or 0} years\nBio: {profile.bio or 'N/A'}"

        # Fetch latest resume
        resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).first()
        resume_info = "No resume uploaded."
        if resume and resume.parsed_data:
            data = resume.parsed_data
            skills = ", ".join(data.get("skills", []))
            resume_info = f"Current Skills: {skills}\nExperience Snippet: {', '.join(data.get('experience', []))[:300]}"

        # Fetch active roadmap
        roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id).order_by(Roadmap.created_at.desc()).first()
        roadmap_info = "No active roadmap."
        if roadmap:
            tasks_list = [f"Step {t.sequence}: {t.title} ({t.status})" for t in roadmap.tasks[:6]]
            roadmap_info = f"Target Role: {roadmap.target_role}\nActive Path title: {roadmap.title}\nKey tasks:\n" + "\n".join(tasks_list)

        return (
            f"--- Candidate Profile ---\n{profile_info}\n\n"
            f"--- Resume Details ---\n{resume_info}\n\n"
            f"--- Career Roadmap ---\n{roadmap_info}"
        )


# Expose singleton service
career_coach_service = CareerCoachService()
