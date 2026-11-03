"""
Action Execution & Voice Processing REST API endpoints for NeuralCanvas.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.canvas import ActionExecution
from app.schemas.canvas import ActionExecutionResponse, VoiceIntentPacket
from app.services.action_dispatcher import ActionDispatcher
from app.services.session_service import SessionService
from app.services.voice_processor import VoiceProcessor
from app.services.connection_manager import connection_manager

router = APIRouter(prefix="/sessions/{session_id}/actions", tags=["Action Dispatch & Voice"])
action_dispatcher = ActionDispatcher()
voice_processor = VoiceProcessor()


class VoiceIntentRequest(BaseModel):
    transcription: str = Field(..., min_length=1, description="Transcribed voice query / intent string")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class VADCheckRequest(BaseModel):
    pcm_base64: str = Field(..., description="Base64 encoded 16-bit linear PCM audio chunk")


@router.post("/voice-intent", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def dispatch_voice_intent(
    session_id: str,
    req: VoiceIntentRequest,
    db: Session = Depends(get_db),
):
    """
    Simulates or executes speech-to-action intent:
    Parses natural language, mutates canvas state, logs multimodal history,
    and broadcasts updates to all active WebSocket clients.
    """
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    result = action_dispatcher.process_voice_intent(
        db=db,
        session_id=session_id,
        transcription=req.transcription,
        confidence=req.confidence,
    )

    # Broadcast action update to active WebSocket clients for this session
    broadcast_payload = {
        "type": "action_dispatched",
        "session_id": session_id,
        "action_id": result["action"].action_id,
        "action_type": result["action"].action_type,
        "status": result["action"].status,
        "summary": result["summary"],
        "assistant_reply": result["assistant_reply"],
    }
    await connection_manager.broadcast_to_session(session_id, broadcast_payload)

    return {
        "session_id": session_id,
        "action_id": result["action"].action_id,
        "action_type": result["action"].action_type,
        "status": result["action"].status,
        "summary": result["summary"],
        "assistant_reply": result["assistant_reply"],
        "latency_ms": result["action"].latency_ms,
        "affected_node_id": result["affected_node"].node_id if result["affected_node"] else None,
        "affected_edge_id": result["affected_edge"].edge_id if result["affected_edge"] else None,
    }


@router.get("", response_model=List[ActionExecutionResponse])
def list_action_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieves chronological audit trail of dispatched agent actions in a session."""
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    return (
        db.query(ActionExecution)
        .filter(ActionExecution.session_id == session_id)
        .order_by(ActionExecution.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/vad-check", response_model=Dict[str, Any])
def vad_energy_check(session_id: str, req: VADCheckRequest):
    """Evaluates RMS energy and Voice Activity Detection (VAD) on a PCM audio chunk."""
    import base64
    try:
        pcm_bytes = base64.b64decode(req.pcm_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 payload.")

    is_speech, energy = voice_processor.detect_voice_activity(pcm_bytes)
    return {
        "session_id": session_id,
        "is_active_speech": is_speech,
        "rms_energy": energy,
        "threshold": voice_processor.energy_threshold,
    }
