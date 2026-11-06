"""
Unit tests for CanvasService.
Tests spatial node placement, edge wiring, search, deletion, and graph topology.
"""

from app.services.canvas_service import CanvasService
from app.schemas.canvas import CanvasNodeCreate, CanvasNodeUpdate, CanvasEdgeCreate
from app.models.canvas import NodeType, NodeExecutionStatus


def test_create_and_get_node(db_session, sample_session):
    node_in = CanvasNodeCreate(
        node_type=NodeType.FILTER,
        label="Threshold Filter",
        position_x=220.0,
        position_y=180.0,
        data={"threshold": 0.75},
        execution_status=NodeExecutionStatus.IDLE,
    )
    node = CanvasService.create_node(db_session, sample_session.session_id, node_in)

    assert node.node_id is not None
    assert node.label == "Threshold Filter"
    assert node.node_type == NodeType.FILTER.value
    assert node.position_x == 220.0

    retrieved = CanvasService.get_node(db_session, sample_session.session_id, node.node_id)
    assert retrieved is not None
    assert retrieved.label == "Threshold Filter"


def test_find_node_by_label_or_id(db_session, sample_session):
    node = CanvasService.find_node_by_label_or_id(db_session, sample_session.session_id, "Prompt Ingest")
    assert node is not None
    assert node.node_id == "node_src_01"

    node_by_id = CanvasService.find_node_by_label_or_id(db_session, sample_session.session_id, "node_tgt_02")
    assert node_by_id is not None
    assert node_by_id.label == "Tool Executor"


def test_update_node(db_session, sample_session):
    update_in = CanvasNodeUpdate(
        label="Updated Ingest Node",
        position_x=120.0,
        position_y=160.0,
        execution_status=NodeExecutionStatus.RUNNING,
    )
    updated = CanvasService.update_node(
        db_session, sample_session.session_id, "node_src_01", update_in
    )
    assert updated is not None
    assert updated.label == "Updated Ingest Node"
    assert updated.position_x == 120.0
    assert updated.execution_status == NodeExecutionStatus.RUNNING.value


def test_create_and_delete_edge(db_session, sample_session):
    edge_in = CanvasEdgeCreate(
        source_node_id="node_src_01",
        target_node_id="node_tgt_02",
        edge_type="telemetry_stream",
    )
    edge = CanvasService.create_edge(db_session, sample_session.session_id, edge_in)
    assert edge.edge_id is not None
    assert edge.edge_type == "telemetry_stream"

    deleted = CanvasService.delete_edge(db_session, sample_session.session_id, edge.edge_id)
    assert deleted is True

    edges = CanvasService.list_edges(db_session, sample_session.session_id)
    assert not any(e.edge_id == edge.edge_id for e in edges)


def test_analyze_graph_topology(db_session, sample_session):
    topology = CanvasService.analyze_graph_topology(db_session, sample_session.session_id)
    assert topology["node_count"] == 2
    assert topology["edge_count"] == 1
    assert "node_src_01" in topology["root_nodes"]
    assert "node_tgt_02" in topology["leaf_nodes"]
    assert topology["has_cycles"] is False
