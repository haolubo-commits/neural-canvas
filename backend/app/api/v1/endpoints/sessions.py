"""
Session REST API endpoints for NeuralCanvas.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.canvas import (
    CanvasSessionCreate,
    CanvasSessionUpdate,
    CanvasSessionResponse,
    CanvasSessionDetailResponse,
)
from app.services.session_service import SessionService
from app.services.canvas_service import CanvasService

router = APIRouter(prefix="/sessions", tags=["Canvas Sessions"])


@router.post("", response_model=CanvasSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_in: CanvasSessionCreate, db: Session = Depends(get_db)):
    """Creates a new interactive canvas workspace session."""
    return SessionService.create_session(db, session_in)


@router.get("", response_model=List[CanvasSessionResponse])
def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lists canvas sessions ordered by most recently modified."""
    return SessionService.list_sessions(db, skip=skip, limit=limit)


@router.get("/{session_id}", response_model=CanvasSessionDetailResponse)
def get_session_details(session_id: str, db: Session = Depends(get_db)):
    """Retrieves full canvas session details including nodes, edges, messages, and action logs."""
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return session


@router.patch("/{session_id}", response_model=CanvasSessionResponse)
def update_session(
    session_id: str,
    session_in: CanvasSessionUpdate,
    db: Session = Depends(get_db),
):
    """Updates session metadata, title, viewport coordinates, or active status."""
    session = SessionService.update_session(db, session_id, session_in)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return session


@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Deletes a session and cascaded graph elements."""
    deleted = SessionService.delete_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return {"message": f"Session '{session_id}' successfully deleted."}


@router.get("/{session_id}/topology", response_model=Dict[str, Any])
def get_session_topology(session_id: str, db: Session = Depends(get_db)):
    """Calculates graph topology metrics, root nodes, leaf sinks, and detects cycles."""
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return CanvasService.analyze_graph_topology(db, session_id)
