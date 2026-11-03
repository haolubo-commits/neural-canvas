"""
Canvas Edge / Directed Connection REST API endpoints for NeuralCanvas.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.canvas import CanvasEdgeCreate, CanvasEdgeResponse
from app.services.canvas_service import CanvasService
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions/{session_id}/edges", tags=["Canvas Edges"])


@router.post("", response_model=CanvasEdgeResponse, status_code=status.HTTP_201_CREATED)
def create_edge(
    session_id: str,
    edge_in: CanvasEdgeCreate,
    db: Session = Depends(get_db),
):
    """Wires together a source node handle to a target node handle."""
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    # Validate source and target nodes exist in the session
    src = CanvasService.get_node(db, session_id, edge_in.source_node_id)
    tgt = CanvasService.get_node(db, session_id, edge_in.target_node_id)
    if not src or not tgt:
        raise HTTPException(
            status_code=400,
            detail=f"Both source node '{edge_in.source_node_id}' and target node '{edge_in.target_node_id}' must exist.",
        )

    return CanvasService.create_edge(db, session_id, edge_in)


@router.get("", response_model=List[CanvasEdgeResponse])
def list_edges(session_id: str, db: Session = Depends(get_db)):
    """Lists all directed connections in a canvas session."""
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return CanvasService.list_edges(db, session_id)


@router.delete("/{edge_id}", status_code=status.HTTP_200_OK)
def delete_edge(session_id: str, edge_id: str, db: Session = Depends(get_db)):
    """Removes a directed connection between canvas nodes."""
    deleted = CanvasService.delete_edge(db, session_id, edge_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Edge '{edge_id}' not found in session '{session_id}'.")
    return {"message": f"Edge '{edge_id}' successfully removed."}
