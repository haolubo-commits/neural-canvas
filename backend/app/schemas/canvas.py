"""
Pydantic v2 schemas for NeuralCanvas.
Handles request/response validation, graph serialization, and WebSocket message frames.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.canvas import (
    SessionStatus,
    NodeType,
    NodeExecutionStatus,
    MessageSender,
    ModalityType,
    ActionType,
    ActionStatus,
)


# ==========================================
# Canvas Node Schemas
# ==========================================

class CanvasNodeBase(BaseModel):
    node_type: NodeType = NodeType.PROMPT
    label: str = Field(..., min_length=1, max_length=120)
    position_x: float = Field(default=100.0)
    position_y: float = Field(default=100.0)
    width: float = Field(default=240.0)
    height: float = Field(default=160.0)
    data: Dict[str, Any] = Field(default_factory=dict)
    execution_status: NodeExecutionStatus = NodeExecutionStatus.IDLE


class CanvasNodeCreate(CanvasNodeBase):
    node_id: Optional[str] = None


class CanvasNodeUpdate(BaseModel):
    label: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    data: Optional[Dict[str, Any]] = None
    execution_status: Optional[NodeExecutionStatus] = None


class CanvasNodeResponse(CanvasNodeBase):
    node_id: str
    session_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# Canvas Edge Schemas
# ==========================================

class CanvasEdgeBase(BaseModel):
    source_node_id: str
    target_node_id: str
    source_handle: str = "output"
    target_handle: str = "input"
    edge_type: str = "data_stream"


class CanvasEdgeCreate(CanvasEdgeBase):
    edge_id: Optional[str] = None


class CanvasEdgeResponse(CanvasEdgeBase):
    edge_id: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# Multimodal Message Schemas
# ==========================================

class MultimodalMessageBase(BaseModel):
    sender: MessageSender = MessageSender.USER
    modality: ModalityType = ModalityType.VOICE
    content: str = Field(..., min_length=1)
    audio_metadata: Dict[str, Any] = Field(default_factory=dict)


class MultimodalMessageCreate(MultimodalMessageBase):
    message_id: Optional[str] = None


class MultimodalMessageResponse(MultimodalMessageBase):
    message_id: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# Action Execution Schemas
# ==========================================

class ActionExecutionBase(BaseModel):
    action_type: ActionType
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ActionExecutionCreate(ActionExecutionBase):
    action_id: Optional[str] = None


class ActionExecutionResponse(ActionExecutionBase):
    action_id: str
    session_id: str
    status: ActionStatus
    execution_result: Dict[str, Any]
    error_message: Optional[str]
    latency_ms: float
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# Canvas Session Schemas
# ==========================================

class CanvasSessionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
    viewport_x: float = Field(default=0.0)
    viewport_y: float = Field(default=0.0)
    viewport_zoom: float = Field(default=1.0)
    voice_enabled: bool = True


class CanvasSessionCreate(CanvasSessionBase):
    session_id: Optional[str] = None


class CanvasSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[SessionStatus] = None
    viewport_x: Optional[float] = None
    viewport_y: Optional[float] = None
    viewport_zoom: Optional[float] = None
    voice_enabled: Optional[bool] = None


class CanvasSessionResponse(CanvasSessionBase):
    session_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CanvasSessionDetailResponse(CanvasSessionResponse):
    nodes: List[CanvasNodeResponse] = Field(default_factory=list)
    edges: List[CanvasEdgeResponse] = Field(default_factory=list)
    messages: List[MultimodalMessageResponse] = Field(default_factory=list)
    actions: List[ActionExecutionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ==========================================
# Real-Time WebSocket Message Frames
# ==========================================

class VoiceIntentPacket(BaseModel):
    type: str = "voice_intent"
    session_id: str
    transcription: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())


class ActionDispatchedFrame(BaseModel):
    type: str = "action_dispatched"
    session_id: str
    action: ActionExecutionResponse
    affected_node: Optional[CanvasNodeResponse] = None
    affected_edge: Optional[CanvasEdgeResponse] = None
