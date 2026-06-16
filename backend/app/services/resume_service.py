import os
import uuid
import pathlib
from typing import List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.repositories.resume_repository import resume_repository
from app.repositories.user_repository import user_repository
from app.utils.exceptions import EntityNotFoundError, ForbiddenError, DomainException

# Configure local file storage location
UPLOAD_DIR = pathlib.Path("uploads/resumes")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class ResumeService:
    """
    Business service coordinating operations for uploaded Resumes including local file storage and validation.
    """

    def upload_resume(
        self, db: Session, *, user_id: uuid.UUID, file: UploadFile
    ) -> Resume:
        """
        Validates file metadata, writes payload contents to disk, and saves records to database.
        """
        # 1. Enforce user existence constraint
        user = user_repository.get_by_id(db, id=user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        # 2. Validate file extension/suffix
        filename = file.filename or "resume"
        extension = pathlib.Path(filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise DomainException(
                f"Unsupported file type. Only PDF and DOCX files are allowed."
            )

        # 3. Read file contents and validate size
        try:
            file_data = file.file.read()
            file_size = len(file_data)
        except Exception as e:
            raise DomainException(f"Failed to read file payload: {str(e)}")
        finally:
            file.file.seek(0)  # Reset stream position

        if file_size > MAX_FILE_SIZE:
            raise DomainException(
                f"File size exceeds the limit of 10 MB."
            )

        # 4. Generate secure UUID filename and ensure storage directory exists
        secure_filename = f"{uuid.uuid4().hex}_resume{extension}"
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        destination_path = UPLOAD_DIR / secure_filename

        # 5. Write file to disk storage
        try:
            with open(destination_path, "wb") as f:
                f.write(file_data)
        except Exception as e:
            raise DomainException(f"Failed to persist file on disk: {str(e)}")

        # 6. Extract text and parse if PDF format
        from app.ai.resume_parser import resume_parser
        
        raw_text = None
        parsed_data = None
        
        if extension == ".pdf":
            raw_text = resume_parser.extract_text(str(destination_path))
            parsed_data = resume_parser.parse_resume(raw_text)
        else:
            # Fallback placeholder for DOCX uploads
            raw_text = "DOCX file content placeholder"
            parsed_data = {
                "name": "Unknown",
                "email": "Unknown",
                "phone": "Unknown",
                "skills": [],
                "education": [],
                "experience": []
            }

        # Deactivate all other user resumes so this newly uploaded one becomes the active one
        db.query(Resume).filter(Resume.user_id == user_id).update({"is_active": False})

        # 7. Save metadata record and parsed structures to database
        db_resume = Resume(
            user_id=user_id,
            filename=filename,
            file_path=str(destination_path),
            file_size=file_size,
            raw_text=raw_text,
            parsed_data=parsed_data,
            is_active=True,
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        # Update user profile with latest resume info
        if parsed_data:
            from app.models.profile import Profile
            profile = db.query(Profile).filter(Profile.user_id == user_id).first()
            if not profile:
                profile = Profile(user_id=user_id)
                db.add(profile)
            profile.title = parsed_data.get("title", profile.title)
            profile.bio = parsed_data.get("bio", profile.bio)
            profile.experience_years = parsed_data.get("experience_years", profile.experience_years)
            db.commit()

        # 8. Synchronize extracted skills dynamically with User profile
        if parsed_data and "skills" in parsed_data and parsed_data["skills"]:
            from app.services.skill_service import skill_service
            skill_service.sync_user_skills_from_resume(
                db, user_id=user_id, resume_skills=parsed_data["skills"]
            )

        return db_resume

    def get_resume(self, db: Session, *, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        """
        Retrieve a single resume document by ID, checking ownership credentials.
        Raises EntityNotFoundError if missing, or ForbiddenError if owned by another user.
        """
        resume = resume_repository.get_by_id(db, id=resume_id)
        if not resume:
            raise EntityNotFoundError("Resume", resume_id)
        
        # Enforce resource ownership checks
        if resume.user_id != user_id:
            raise ForbiddenError("You do not have permission to access this resume")
            
        return resume

    def get_user_resumes(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Resume]:
        """
        Retrieve all resume records belonging to a User ID.
        """
        user = user_repository.get_by_id(db, id=user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        return resume_repository.get_resumes_by_user(db, user_id=user_id, skip=skip, limit=limit)

    def activate_resume(self, db: Session, *, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        """
        Sets a specific resume as active, marking all others for the user as inactive,
        and updates the user's Profile & skills dynamically.
        """
        # Enforce resource ownership checks
        resume = self.get_resume(db, resume_id=resume_id, user_id=user_id)
        
        # Deactivate all others
        db.query(Resume).filter(Resume.user_id == user_id).update({"is_active": False})
        
        # Activate this one
        resume.is_active = True
        db.commit()
        db.refresh(resume)
        
        # Sync profile details
        if resume.parsed_data:
            from app.models.profile import Profile
            profile = db.query(Profile).filter(Profile.user_id == user_id).first()
            if not profile:
                profile = Profile(user_id=user_id)
                db.add(profile)
            profile.title = resume.parsed_data.get("title", profile.title)
            profile.bio = resume.parsed_data.get("bio", profile.bio)
            profile.experience_years = resume.parsed_data.get("experience_years", profile.experience_years)
            db.commit()
            
            # Sync skills
            if "skills" in resume.parsed_data and resume.parsed_data["skills"]:
                from app.services.skill_service import skill_service
                skill_service.sync_user_skills_from_resume(
                    db, user_id=user_id, resume_skills=resume.parsed_data["skills"]
                )
                
        return resume

    def delete_resume(self, db: Session, *, resume_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """
        Deletes a resume record from database metadata and removes the physical file from disk storage.
        """
        # Fetches resume while enforcing ownership constraints
        resume = self.get_resume(db, resume_id=resume_id, user_id=user_id)
        was_active = resume.is_active
        
        # Delete from local file system
        file_path = pathlib.Path(resume.file_path)
        try:
            if file_path.is_file():
                file_path.unlink()
        except Exception as e:
            # Log issue but proceed to clear DB entry to maintain system consistency
            pass

        # Clear database entry
        resume_repository.delete(db, id=resume_id)
        db.commit()

        # Cascade cleanups
        # 1. Delete all generated roadmaps linked to this user
        from app.models.roadmap import Roadmap
        db.query(Roadmap).filter(Roadmap.user_id == user_id).delete()
        
        # 1.5. Delete all ATS evaluations linked to this user or this resume
        from app.models.ats_analysis import ATSAnalysis
        db.query(ATSAnalysis).filter((ATSAnalysis.user_id == user_id) | (ATSAnalysis.resume_id == resume_id)).delete()
        
        # 2. Reset Profile details derived from the resume
        from app.models.profile import Profile
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if profile:
            profile.title = None
            profile.bio = None
            profile.experience_years = None
            
        # 3. Clear user profile skills database relations
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.skills = []
            
        # 4. Clear Skill Intelligence gap analysis cache
        from app.ai.skill_gap_analyzer import skill_gap_analyzer
        skill_gap_analyzer._cache.clear()
        
        db.commit()

        # If deleted resume was the active one, activate the latest remaining one if any
        if was_active:
            latest = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).first()
            if latest:
                self.activate_resume(db, resume_id=latest.id, user_id=user_id)


# Expose service singleton
resume_service = ResumeService()
