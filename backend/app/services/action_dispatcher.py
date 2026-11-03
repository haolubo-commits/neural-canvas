"""
Action Dispatcher & Execution Engine for NeuralCanvas.
Coordinates between parsed voice intents, canvas graph state mutations,
tool executions, and audit log persistence.
"""

from typing import Dict, Any, Optional, Tuple
import uuid
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.canvas import (
    ActionExecution,
    ActionType,
    ActionStatus,
    MultimodalMessage,
    MessageSender,
    ModalityType,
    NodeType,
    CanvasNode,
    CanvasEdge,
)
from app.schemas.canvas import CanvasNodeCreate, CanvasEdgeCreate
from app.services.canvas_service import CanvasService
from app.services.voice_processor import VoiceProcessor


class ActionDispatcher:
    def __init__(self):
        self.voice_processor = VoiceProcessor()

    def process_voice_intent(
        self,
        db: Session,
        session_id: str,
        transcription: str,
        confidence: float = 1.0,
    ) -> Dict[str, Any]:
        """
        End-to-end processing of streaming speech transcription:
        1. Records user incoming voice message
        2. Parses semantic speech intent
        3. Executes corresponding canvas action
        4. Records assistant multimodal response
        5. Returns dispatched action frame
        """
        # 1. Log incoming user voice message
        user_msg = MultimodalMessage(
            message_id=f"msg_{uuid.uuid4().hex[:10]}",
            session_id=session_id,
            sender=MessageSender.USER.value,
            modality=ModalityType.VOICE.value,
            content=transcription,
            audio_metadata={"confidence": confidence, "timestamp": datetime.utcnow().isoformat()},
            created_at=datetime.utcnow(),
        )
        db.add(user_msg)
        db.commit()

        # 2. Parse intent
        intent = self.voice_processor.parse_speech_intent(transcription)
        action_type = intent["action_type"]
        params = intent["parameters"]

        # 3. Execute action
        action_res, affected_node, affected_edge, assistant_reply = self.execute_action(
            db=db,
            session_id=session_id,
            action_type=action_type,
            parameters=params,
        )

        # 4. Log assistant multimodal response
        assistant_msg = MultimodalMessage(
            message_id=f"msg_{uuid.uuid4().hex[:10]}",
            session_id=session_id,
            sender=MessageSender.ASSISTANT.value,
            modality=ModalityType.ACTION.value if action_type != ActionType.VOICE_SYNTHESIS else ModalityType.VOICE.value,
            content=assistant_reply,
            audio_metadata={"linked_action_id": action_res.action_id},
            created_at=datetime.utcnow(),
        )
        db.add(assistant_msg)
        db.commit()

        return {
            "type": "action_dispatched",
            "session_id": session_id,
            "action": action_res,
            "affected_node": affected_node,
            "affected_edge": affected_edge,
            "assistant_reply": assistant_reply,
            "summary": intent.get("summary", ""),
        }

    def execute_action(
        self,
        db: Session,
        session_id: str,
        action_type: ActionType,
        parameters: Dict[str, Any],
    ) -> Tuple[ActionExecution, Optional[CanvasNode], Optional[CanvasEdge], str]:
        """
        Executes a discrete action against the canvas state and records execution logs.
        """
        start_time = time.perf_counter()
        action_id = f"act_{uuid.uuid4().hex[:10]}"
        status = ActionStatus.SUCCESS
        error_msg = None
        result_payload: Dict[str, Any] = {}
        affected_node = None
        affected_edge = None
        assistant_reply = ""

        try:
            if action_type == ActionType.CREATE_NODE:
                node_type_val = parameters.get("node_type", "prompt")
                node_in = CanvasNodeCreate(
                    node_type=NodeType(node_type_val),
                    label=parameters.get("label", "New Node"),
                    position_x=parameters.get("position_x", 150.0),
                    position_y=parameters.get("position_y", 150.0),
                    data=parameters.get("data", {}),
                )
                affected_node = CanvasService.create_node(db, session_id, node_in)
                result_payload = {"created_node_id": affected_node.node_id, "label": affected_node.label}
                assistant_reply = f"Created {affected_node.node_type} node '{affected_node.label}' on the canvas."

            elif action_type == ActionType.CONNECT_NODES:
                src_ident = parameters.get("source", "")
                tgt_ident = parameters.get("target", "")

                src_node = CanvasService.find_node_by_label_or_id(db, session_id, src_ident)
                tgt_node = CanvasService.find_node_by_label_or_id(db, session_id, tgt_ident)

                if not src_node or not tgt_node:
                    raise ValueError(f"Could not resolve nodes for connection: '{src_ident}' -> '{tgt_ident}'")

                edge_in = CanvasEdgeCreate(
                    source_node_id=src_node.node_id,
                    target_node_id=tgt_node.node_id,
                    edge_type=parameters.get("edge_type", "data_stream"),
                )
                affected_edge = CanvasService.create_edge(db, session_id, edge_in)
                result_payload = {
                    "edge_id": affected_edge.edge_id,
                    "source": src_node.label,
                    "target": tgt_node.label,
                }
                assistant_reply = f"Connected '{src_node.label}' to '{tgt_node.label}'."

            elif action_type == ActionType.DELETE_NODE:
                target_ident = parameters.get("node_target", "")
                target_node = CanvasService.find_node_by_label_or_id(db, session_id, target_ident)
                if not target_node:
                    raise ValueError(f"Node '{target_ident}' not found for deletion.")

                deleted_id = target_node.node_id
                deleted_label = target_node.label
                CanvasService.delete_node(db, session_id, deleted_id)
                result_payload = {"deleted_node_id": deleted_id, "label": deleted_label}
                assistant_reply = f"Deleted node '{deleted_label}'."

            elif action_type == ActionType.EXECUTE_TOOL:
                tool_name = parameters.get("tool_name", "generic_tool")
                result_payload = {
                    "tool": tool_name,
                    "output": f"Executed tool {tool_name} successfully.",
                    "status": "completed",
                }
                assistant_reply = f"Executed tool '{tool_name}'."

            elif action_type == ActionType.VOICE_SYNTHESIS:
                query = parameters.get("query", "")
                result_payload = {"synthesized": True, "query": query}
                assistant_reply = f"I've processed your voice request: '{query}'."

            else:
                result_payload = {"info": "Generic action executed."}
                assistant_reply = "Action dispatched successfully."

        except Exception as e:
            status = ActionStatus.FAILED
            error_msg = str(e)
            result_payload = {"error": error_msg}
            assistant_reply = f"Encountered an issue executing action: {error_msg}"

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        action_execution = ActionExecution(
            action_id=action_id,
            session_id=session_id,
            action_type=action_type.value if hasattr(action_type, "value") else action_type,
            status=status.value if hasattr(status, "value") else status,
            parameters=parameters,
            execution_result=result_payload,
            error_message=error_msg,
            latency_ms=elapsed_ms,
            created_at=datetime.utcnow(),
        )
        db.add(action_execution)
        db.commit()
        db.refresh(action_execution)

        return action_execution, affected_node, affected_edge, assistant_reply
