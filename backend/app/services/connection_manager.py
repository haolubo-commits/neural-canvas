"""
WebSocket Connection Manager for NeuralCanvas.
Manages concurrent active client connections, per-session routing, and broadcasting.
"""

from typing import Dict, List, Set
import logging
from fastapi import WebSocket

logger = logging.getLogger("neural_canvas.connection_manager")


class ConnectionManager:
    def __init__(self):
        # Maps session_id to set of active WebSocket client connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        """Accepts and registers a new WebSocket client for a canvas session."""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        logger.info(
            f"Client connected to session '{session_id}'. "
            f"Total active clients for session: {len(self.active_connections[session_id])}"
        )

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        """Unregisters a WebSocket client upon disconnection."""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"Client disconnected from session '{session_id}'.")

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """Sends a JSON frame to a specific client socket."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Error sending personal message: {e}")

    async def broadcast_to_session(self, session_id: str, message: dict) -> None:
        """Broadcasts a JSON message frame to all clients viewing the given session."""
        if session_id not in self.active_connections:
            return

        dead_connections = []
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to broadcast to client in session '{session_id}': {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(session_id, dead)

    def get_session_client_count(self, session_id: str) -> int:
        """Returns the number of active clients in a session."""
        return len(self.active_connections.get(session_id, set()))

    def get_total_active_sessions(self) -> int:
        """Returns the total number of sessions with live client connections."""
        return len(self.active_connections)


connection_manager = ConnectionManager()
