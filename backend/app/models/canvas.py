"""
SQLAlchemy 2.0 ORM models for NeuralCanvas.
Defines sessions, 2D canvas nodes, directed graph edges, multimodal messages, and action audit logs.
"""

from enum import Enum
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class NodeType(str, Enum):
    PROMPT = "prompt"
    TOOL = "tool"
    DATA_SOURCE = "data_source"
    FILTER = "filter"
    TRANSFORM = "transform"
    VISUALIZATION = "visualization"
    OUTPUT = "output"


class NodeExecutionStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class MessageSender(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ModalityType(str, Enum):
    VOICE = "voice"
    TEXT = "text"
    ACTION = "action"


class ActionType(str, Enum):
    CREATE_NODE = "CREATE_NODE"
    UPDATE_NODE = "UPDATE_NODE"
    DELETE_NODE = "DELETE_NODE"
    CONNECT_NODES = "CONNECT_NODES"
    DISCONNECT_NODES = "DISCONNECT_NODES"
    EXECUTE_TOOL = "EXECUTE_TOOL"
    TRANSFORM_DATA = "TRANSFORM_DATA"
    VOICE_SYNTHESIS = "VOICE_SYNTHESIS"


class ActionStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"


class CanvasSession(Base):
    __tablename__ = "canvas_sessions"

    session_id = Column(String(36), primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=SessionStatus.ACTIVE.value)
    viewport_x = Column(Float, nullable=False, default=0.0)
    viewport_y = Column(Float, nullable=False, default=0.0)
    viewport_zoom = Column(Float, nullable=False, default=1.0)
    voice_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    nodes = relationship("CanvasNode", back_populates="session", cascade="all, delete-orphan")
    edges = relationship("CanvasEdge", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("MultimodalMessage", back_populates="session", cascade="all, delete-orphan")
    actions = relationship("ActionExecution", back_populates="session", cascade="all, delete-orphan")


class CanvasNode(Base):
    __tablename__ = "canvas_nodes"

    node_id = Column(String(36), primary_key=True, index=True)
    session_id = Column(
        String(36),
        ForeignKey("canvas_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    node_type = Column(String(30), nullable=False, default=NodeType.PROMPT.value)
    label = Column(String(120), nullable=False)
    position_x = Column(Float, nullable=False, default=100.0)
    position_y = Column(Float, nullable=False, default=100.0)
    width = Column(Float, nullable=False, default=240.0)
    height = Column(Float, nullable=False, default=160.0)
    data = Column(JSON, nullable=False, default=dict)
    execution_status = Column(String(20), nullable=False, default=NodeExecutionStatus.IDLE.value)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("CanvasSession", back_populates="nodes")


class CanvasEdge(Base):
    __tablename__ = "canvas_edges"

    edge_id = Column(String(36), primary_key=True, index=True)
    session_id = Column(
        String(36),
        ForeignKey("canvas_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    source_node_id = Column(
        String(36),
        ForeignKey("canvas_nodes.node_id", ondelete="CASCADE"),
        nullable=False
    )
    target_node_id = Column(
        String(36),
        ForeignKey("canvas_nodes.node_id", ondelete="CASCADE"),
        nullable=False
    )
    source_handle = Column(String(50), nullable=False, default="output")
    target_handle = Column(String(50), nullable=False, default="input")
    edge_type = Column(String(30), nullable=False, default="data_stream")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("CanvasSession", back_populates="edges")

    __table_args__ = (
        Index("ix_canvas_edges_source_target", "source_node_id", "target_node_id"),
    )


class MultimodalMessage(Base):
    __tablename__ = "multimodal_messages"

    message_id = Column(String(36), primary_key=True, index=True)
    session_id = Column(
        String(36),
        ForeignKey("canvas_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sender = Column(String(20), nullable=False, default=MessageSender.USER.value)
    modality = Column(String(20), nullable=False, default=ModalityType.VOICE.value)
    content = Column(Text, nullable=False)
    audio_metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("CanvasSession", back_populates="messages")


class ActionExecution(Base):
    __tablename__ = "action_executions"

    action_id = Column(String(36), primary_key=True, index=True)
    session_id = Column(
        String(36),
        ForeignKey("canvas_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    action_type = Column(String(40), nullable=False)
    status = Column(String(20), nullable=False, default=ActionStatus.PENDING.value)
    parameters = Column(JSON, nullable=False, default=dict)
    execution_result = Column(JSON, nullable=False, default=dict)
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("CanvasSession", back_populates="actions")
