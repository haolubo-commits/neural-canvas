"""
Session Management Service for NeuralCanvas.
Handles canvas session lifecycle, viewport persistence, and cascaded data queries.
"""

from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.canvas import CanvasSession, SessionStatus
from app.schemas.canvas import CanvasSessionCreate, CanvasSessionUpdate


class SessionService:
    @staticmethod
    def create_session(db: Session, session_in: CanvasSessionCreate) -> CanvasSession:
        """Creates and persists a new canvas workspace session."""
        session_id = session_in.session_id or f"sess_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow()

        db_session = CanvasSession(
            session_id=session_id,
            title=session_in.title,
            description=session_in.description,
            status=session_in.status.value if hasattr(session_in.status, "value") else session_in.status,
            viewport_x=session_in.viewport_x,
            viewport_y=session_in.viewport_y,
            viewport_zoom=session_in.viewport_zoom,
            voice_enabled=session_in.voice_enabled,
            created_at=now,
            updated_at=now,
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[CanvasSession]:
        """Retrieves a single session by its unique ID."""
        return db.query(CanvasSession).filter(CanvasSession.session_id == session_id).first()

    @staticmethod
    def list_sessions(db: Session, skip: int = 0, limit: int = 50) -> List[CanvasSession]:
        """Lists active and archived sessions with pagination."""
        return (
            db.query(CanvasSession)
            .order_by(CanvasSession.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_session(
        db: Session, session_id: str, session_in: CanvasSessionUpdate
    ) -> Optional[CanvasSession]:
        """Updates session attributes such as viewport position, title, or status."""
        session = SessionService.get_session(db, session_id)
        if not session:
            return None

        update_data = session_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value:
                setattr(session, field, value.value if hasattr(value, "value") else value)
            elif value is not None:
                setattr(session, field, value)

        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        """Deletes a session and cascades delete to all nodes, edges, messages, and actions."""
        session = SessionService.get_session(db, session_id)
        if not session:
            return False

        db.delete(session)
        db.commit()
        return True
