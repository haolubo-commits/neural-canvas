"""
Unit tests for ActionDispatcher.
Tests end-to-end voice intent dispatch, graph mutations, and execution logs.
"""

from app.services.action_dispatcher import ActionDispatcher
from app.models.canvas import ActionType, ActionStatus, MultimodalMessage, ActionExecution


def test_process_voice_intent_create_node(db_session, sample_session):
    dispatcher = ActionDispatcher()
    transcription = "Create a filter node named Risk_Evaluator at 300, 300"

    result = dispatcher.process_voice_intent(
        db=db_session,
        session_id=sample_session.session_id,
        transcription=transcription,
        confidence=0.98,
    )

    assert result["type"] == "action_dispatched"
    assert result["action"].status == ActionStatus.SUCCESS.value
    assert result["action"].action_type == ActionType.CREATE_NODE.value
    assert result["affected_node"] is not None
    assert result["affected_node"].label == "Risk_Evaluator"
    assert "Risk_Evaluator" in result["assistant_reply"]

    # Verify message logged
    messages = (
        db_session.query(MultimodalMessage)
        .filter(MultimodalMessage.session_id == sample_session.session_id)
        .all()
    )
    assert len(messages) >= 2


def test_process_voice_intent_connect_nodes(db_session, sample_session):
    dispatcher = ActionDispatcher()
    transcription = "Connect node Prompt Ingest to node Tool Executor"

    result = dispatcher.process_voice_intent(
        db=db_session,
        session_id=sample_session.session_id,
        transcription=transcription,
        confidence=0.95,
    )

    assert result["action"].status == ActionStatus.SUCCESS.value
    assert result["affected_edge"] is not None
    assert result["affected_edge"].source_node_id == "node_src_01"
    assert result["affected_edge"].target_node_id == "node_tgt_02"


def test_process_voice_intent_missing_node_error(db_session, sample_session):
    dispatcher = ActionDispatcher()
    transcription = "Connect node nonexistent_A to node nonexistent_B"

    result = dispatcher.process_voice_intent(
        db=db_session,
        session_id=sample_session.session_id,
        transcription=transcription,
        confidence=0.95,
    )

    assert result["action"].status == ActionStatus.FAILED.value
    assert "error" in result["assistant_reply"].lower()
