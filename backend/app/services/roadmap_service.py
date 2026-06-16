import uuid
from typing import List
from sqlalchemy.orm import Session
from app.models.roadmap import Roadmap
from app.models.roadmap_task import RoadmapTask
from app.schemas.roadmap import RoadmapCreate
from app.schemas.roadmap_task import RoadmapTaskCreate, RoadmapTaskUpdate
from app.repositories.roadmap_repository import roadmap_repository
from app.repositories.roadmap_task_repository import roadmap_task_repository
from app.repositories.user_repository import user_repository
from app.utils.exceptions import EntityNotFoundError


from app.repositories.resume_repository import resume_repository
from app.ai.roadmap_generator import roadmap_generator
from app.utils.exceptions import EntityNotFoundError, ForbiddenError


class RoadmapService:
    """
    Business service coordinating actions for generated Career Roadmaps and Tasks.
    """

    def generate_roadmap_for_user(
        self, db: Session, *, user_id: uuid.UUID, resume_id: uuid.UUID, target_role: str
    ) -> Roadmap:
        """
        Loads the specified resume, verifies user ownership, triggers the roadmap generator,
        and persists the generated roadmap along with its sequenced task milestones.
        """
        # 1. Fetch resume and verify existence
        resume = resume_repository.get_by_id(db, id=resume_id)
        if not resume:
            raise EntityNotFoundError("Resume", resume_id)

        # 2. Validate ownership of the resume
        if resume.user_id != user_id:
            raise ForbiddenError("You do not have permission to use this resume for roadmap generation")

        # 3. Retrieve parsed metadata content and compute missing skills
        parsed_resume = resume.parsed_data or {}
        user_skills = parsed_resume.get("skills", [])
        
        from app.ai.skill_gap_analyzer import skill_gap_analyzer
        try:
            gap_analysis = skill_gap_analyzer.analyze_gap(
                user_skills=user_skills,
                target_role=target_role,
                user_id=user_id,
                resume_id=resume.id,
                parsed_resume=parsed_resume,
                raw_resume_text=resume.raw_text
            )
            missing_skills = gap_analysis.get("missing_skills", [])
        except Exception as gap_err:
            print(f"RoadmapService: failed to compute skill gap: {gap_err}. Defaulting to empty missing skills.")
            missing_skills = []

        # 4. Invoke the AI RoadmapGenerator
        roadmap_payload = roadmap_generator.generate_roadmap(parsed_resume, target_role, missing_skills)

        # 5. Persist parent Roadmap record
        db_roadmap = Roadmap(
            user_id=user_id,
            title=roadmap_payload["title"],
            description=roadmap_payload["description"],
            target_role=target_role,
        )
        db.add(db_roadmap)
        db.commit()
        db.refresh(db_roadmap)

        # 6. Persist individual RoadmapTask records
        import json
        sequence = 1
        for milestone in roadmap_payload["milestones"]:
            m_title = milestone["title"]
            for task in milestone["tasks"]:
                resources_list = task.get("resources", [])
                serialized_resources = f"\n\n||RESOURCES||{json.dumps(resources_list)}"
                db_task = RoadmapTask(
                    roadmap_id=db_roadmap.id,
                    title=task["title"],
                    description=f"Milestone: {m_title}\n\n{task['description']}{serialized_resources}",
                    sequence=sequence,
                    status="pending",
                )
                db.add(db_task)
                sequence += 1
            
        db.commit()
        db.refresh(db_roadmap)

        return db_roadmap

    def get_roadmaps_for_user(self, db: Session, *, user_id: uuid.UUID) -> List[Roadmap]:
        """
        Query all career roadmaps belonging to a user.
        """
        return roadmap_repository.get_roadmaps_by_user(db, user_id=user_id)



    def create_roadmap(
        self, db: Session, *, user_id: uuid.UUID, roadmap_in: RoadmapCreate
    ) -> Roadmap:
        """
        Initialize a career roadmap track.
        Placeholder for future LLM generative roadmap configurations.
        """
        # Ensure user exists
        user = user_repository.get_by_id(db, id=user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        roadmap_data = roadmap_in.model_dump()
        roadmap_data["user_id"] = user_id

        # Save record
        db_roadmap = Roadmap(**roadmap_data)
        db.add(db_roadmap)
        db.commit()
        db.refresh(db_roadmap)

        # Placeholder: Trigger generative task parsing or populate mock milestones
        self._populate_mock_tasks(db, roadmap_id=db_roadmap.id)

        return db_roadmap

    def get_roadmap(self, db: Session, *, roadmap_id: uuid.UUID) -> Roadmap:
        """
        Query a roadmap along with its nested tasks.
        Raises EntityNotFoundError if missing.
        """
        roadmap = roadmap_repository.get_by_id(db, id=roadmap_id)
        if not roadmap:
            raise EntityNotFoundError("Roadmap", roadmap_id)
        return roadmap

    def create_task(
        self, db: Session, *, roadmap_id: uuid.UUID, task_in: RoadmapTaskCreate
    ) -> RoadmapTask:
        """
        Create a new milestone task directly within an existing roadmap.
        """
        # Verify roadmap exists
        roadmap = roadmap_repository.get_by_id(db, id=roadmap_id)
        if not roadmap:
            raise EntityNotFoundError("Roadmap", roadmap_id)

        task_data = task_in.model_dump()
        # Verify matching roadmap reference
        task_data["roadmap_id"] = roadmap_id

        db_task = RoadmapTask(**task_data)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    def update_task_status(
        self, db: Session, *, task_id: uuid.UUID, status: str
    ) -> RoadmapTask:
        """
        Modify the completion state of a specific learning milestone task.
        """
        db_task = roadmap_task_repository.get_by_id(db, id=task_id)
        if not db_task:
            raise EntityNotFoundError("RoadmapTask", task_id)

        return roadmap_task_repository.update(db, db_obj=db_task, obj_in={"status": status})

    def delete_roadmap(self, db: Session, *, roadmap_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """
        Delete a career roadmap after verifying user ownership.
        """
        roadmap = roadmap_repository.get_by_id(db, id=roadmap_id)
        if not roadmap:
            raise EntityNotFoundError("Roadmap", roadmap_id)
        
        if roadmap.user_id != user_id:
            raise ForbiddenError("You do not have permission to delete this roadmap")
            
        roadmap_repository.delete(db, id=roadmap_id)

    def _populate_mock_tasks(self, db: Session, roadmap_id: uuid.UUID) -> None:
        """
        Populate mock tasks for initial verification.
        Will be replaced by LangChain / Groq structured JSON outputs.
        """
        mock_tasks = [
            {"title": "Research Foundations", "description": "Gather basic documentations and industry standard practices.", "sequence": 1, "status": "pending"},
            {"title": "Core Syntax & Frameworks", "description": "Build minor prototype projects using primary tools.", "sequence": 2, "status": "pending"},
            {"title": "Deploy & Optimize", "description": "Launch projects onto cloud infrastructure and optimize performance.", "sequence": 3, "status": "pending"}
        ]
        
        for task_dict in mock_tasks:
            task = RoadmapTask(roadmap_id=roadmap_id, **task_dict)
            db.add(task)
            
        db.commit()


# Expose service singleton
roadmap_service = RoadmapService()
