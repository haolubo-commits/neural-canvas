"""
Real-Time WebSocket Router for NeuralCanvas.
Handles full-duplex streaming audio frames, voice intents, and canvas state diff broadcasting.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.connection_manager import connection_manager
from app.services.action_dispatcher import ActionDispatcher

logger = logging.getLogger("neural_canvas.websocket")
router = APIRouter(tags=["WebSocket Real-Time Gateway"])
action_dispatcher = ActionDispatcher()


@router.websocket("/ws/v1/sessions/{session_id}")
async def websocket_session_endpoint(websocket: WebSocket, session_id: str):
    """
    Bidirectional WebSocket connection for a canvas session.
    Receives voice intent frames, audio chunks, and broadcasts action updates in real-time.
    """
    await connection_manager.connect(session_id, websocket)

    # Send initial connection confirmation
    await connection_manager.send_personal_message(
        {
            "type": "connection_established",
            "session_id": session_id,
            "connected_at": datetime.utcnow().isoformat(),
            "active_clients": connection_manager.get_session_client_count(session_id),
        },
        websocket,
    )

    db: Session = SessionLocal()
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "ping":
                await connection_manager.send_personal_message({"type": "pong"}, websocket)

            elif msg_type == "voice_intent":
                transcription = data.get("transcription", "")
                confidence = float(data.get("confidence", 1.0))

                if transcription:
                    result = action_dispatcher.process_voice_intent(
                        db=db,
                        session_id=session_id,
                        transcription=transcription,
                        confidence=confidence,
                    )
                    # Broadcast action event to all connected clients in the session
                    await connection_manager.broadcast_to_session(
                        session_id,
                        {
                            "type": "action_dispatched",
                            "session_id": session_id,
                            "action_id": result["action"].action_id,
                            "action_type": result["action"].action_type,
                            "status": result["action"].status,
                            "summary": result["summary"],
                            "assistant_reply": result["assistant_reply"],
                            "affected_node_id": result["affected_node"].node_id if result["affected_node"] else None,
                            "affected_edge_id": result["affected_edge"].edge_id if result["affected_edge"] else None,
                        },
                    )

            elif msg_type == "cursor_move":
                # Collaborative spatial presence
                await connection_manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "peer_cursor",
                        "session_id": session_id,
                        "client_id": data.get("client_id", "peer"),
                        "x": data.get("x", 0),
                        "y": data.get("y", 0),
                    },
                )

            else:
                logger.debug(f"Received unhandled message type '{msg_type}' in session '{session_id}'")

    except WebSocketDisconnect:
        connection_manager.disconnect(session_id, websocket)
        logger.info(f"WebSocket client disconnected cleanly from session '{session_id}'")
    except Exception as e:
        logger.warning(f"WebSocket session error in '{session_id}': {e}")
        connection_manager.disconnect(session_id, websocket)
    finally:
        db.close()
