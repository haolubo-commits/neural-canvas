"""
Pytest configuration, in-memory SQLite database fixtures, and TestClient setup.
"""

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.canvas import CanvasSession, CanvasNode, CanvasEdge, NodeType

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initializes tables for test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provides isolated transaction session for each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_session(db_session: Session) -> CanvasSession:
    """Pre-populates a test session with nodes and an edge."""
    sess = CanvasSession(
        session_id="sess_test_101",
        title="Automated Test DAG Workspace",
        description="Integration testing session",
        viewport_x=10.0,
        viewport_y=20.0,
        viewport_zoom=1.0,
    )
    db_session.add(sess)

    node1 = CanvasNode(
        node_id="node_src_01",
        session_id=sess.session_id,
        node_type=NodeType.PROMPT.value,
        label="Prompt Ingest",
        position_x=100.0,
        position_y=150.0,
        data={"query": "test query"},
    )
    node2 = CanvasNode(
        node_id="node_tgt_02",
        session_id=sess.session_id,
        node_type=NodeType.TOOL.value,
        label="Tool Executor",
        position_x=450.0,
        position_y=150.0,
        data={"tool": "search"},
    )
    db_session.add(node1)
    db_session.add(node2)

    edge = CanvasEdge(
        edge_id="edge_test_01",
        session_id=sess.session_id,
        source_node_id=node1.node_id,
        target_node_id=node2.node_id,
        edge_type="data_stream",
    )
    db_session.add(edge)
    db_session.commit()
    db_session.refresh(sess)
    return sess
