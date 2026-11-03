"""
Canvas Node REST API endpoints for NeuralCanvas.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.canvas import CanvasNodeCreate, CanvasNodeUpdate, CanvasNodeResponse
from app.services.canvas_service import CanvasService
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions/{session_id}/nodes", tags=["Canvas Nodes"])


@router.post("", response_model=CanvasNodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(
    session_id: str,
    node_in: CanvasNodeCreate,
    db: Session = Depends(get_db),
):
    """Spawns a new node onto the canvas in the specified session."""
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return CanvasService.create_node(db, session_id, node_in)


@router.get("", response_model=List[CanvasNodeResponse])
def list_nodes(session_id: str, db: Session = Depends(get_db)):
    """Lists all nodes currently deployed in a session."""
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return CanvasService.list_nodes(db, session_id)


@router.get("/{node_id}", response_model=CanvasNodeResponse)
def get_node(session_id: str, node_id: str, db: Session = Depends(get_db)):
    """Retrieves properties and state of a single canvas node."""
    node = CanvasService.get_node(db, session_id, node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in session '{session_id}'.")
    return node


@router.patch("/{node_id}", response_model=CanvasNodeResponse)
def update_node(
    session_id: str,
    node_id: str,
    node_in: CanvasNodeUpdate,
    db: Session = Depends(get_db),
):
    """Updates position coordinates, dimensions, label, or execution data of a node."""
    updated = CanvasService.update_node(db, session_id, node_id, node_in)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in session '{session_id}'.")
    return updated


@router.delete("/{node_id}", status_code=status.HTTP_200_OK)
def delete_node(session_id: str, node_id: str, db: Session = Depends(get_db)):
    """Removes a node and its attached connections from the canvas."""
    deleted = CanvasService.delete_node(db, session_id, node_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in session '{session_id}'.")
    return {"message": f"Node '{node_id}' successfully removed."}
