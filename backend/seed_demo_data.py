"""
seed_demo_data.py — Rich Dataset Seeder for NeuralCanvas.
Populates realistic enterprise canvas DAG workspaces, spatial nodes,
directed connection edges, voice message streams, and action audit logs.
"""

import uuid
from datetime import datetime, timedelta
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.canvas import (
    CanvasSession,
    CanvasNode,
    CanvasEdge,
    MultimodalMessage,
    ActionExecution,
    SessionStatus,
    NodeType,
    NodeExecutionStatus,
    MessageSender,
    ModalityType,
    ActionType,
    ActionStatus,
)


DEMO_SESSIONS = [
    {
        "session_id": "sess_churn_intel_01",
        "title": "Customer Intelligence & Churn Prevention DAG",
        "description": "Streaming voice pipeline extracting CRM customer retention risk scores, sending automated Slack alerts, and plotting heatmaps.",
        "nodes": [
            {
                "node_id": "node_voice_ingest",
                "node_type": NodeType.PROMPT,
                "label": "Voice Ingestion Stream",
                "position_x": 80.0,
                "position_y": 140.0,
                "width": 250.0,
                "height: 140.0": None,
                "status": NodeExecutionStatus.SUCCESS,
                "data": {"sample_rate_hz": 16000, "vad_threshold": 0.015, "format": "16-bit PCM"},
            },
            {
                "node_id": "node_crm_pg",
                "node_type": NodeType.DATA_SOURCE,
                "label": "PostgreSQL Customer DB",
                "position_x": 400.0,
                "position_y": 100.0,
                "status": NodeExecutionStatus.SUCCESS,
                "data": {"table": "customer_telemetry", "records": 48250, "query_time_ms": 14.2},
            },
            {
                "node_id": "node_churn_filter",
                "node_type": NodeType.FILTER,
                "label": "High Churn Risk Filter",
                "position_x": 740.0,
                "position_y": 130.0,
                "status": NodeExecutionStatus.SUCCESS,
                "data": {"condition": "churn_prob >= 0.80", "matched_records": 142},
            },
            {
                "node_id": "node_slack_bot",
                "node_type": NodeType.TOOL,
                "label": "Slack Retention Bot",
                "position_x": 1080.0,
                "position_y": 130.0,
                "status": NodeExecutionStatus.IDLE,
                "data": {"channel": "#cx-retention-war-room", "bot_id": "U0847BOT"},
            },
            {
                "node_id": "node_risk_heatmap",
                "node_type": NodeType.VISUALIZATION,
                "label": "Risk Distribution Heatmap",
                "position_x": 580.0,
                "position_y": 360.0,
                "status": NodeExecutionStatus.RUNNING,
                "data": {"chart": "density_heatmap", "refresh_sec": 2},
            },
        ],
        "edges": [
            ("node_voice_ingest", "node_crm_pg", "data_stream"),
            ("node_crm_pg", "node_churn_filter", "data_stream"),
            ("node_churn_filter", "node_slack_bot", "alert_trigger"),
            ("node_churn_filter", "node_risk_heatmap", "metrics_stream"),
        ],
    },
    {
        "session_id": "sess_fraud_telemetry_02",
        "title": "Financial Transaction Fraud Telemetry",
        "description": "Real-time payment transaction monitoring, anomaly scoring via Isolation Forest, and account freeze actions.",
        "nodes": [
            {
                "node_id": "node_kafka_stream",
                "node_type": NodeType.DATA_SOURCE,
                "label": "Kafka Payment Feed",
                "position_x": 100.0,
                "position_y": 180.0,
                "status": NodeExecutionStatus.SUCCESS,
                "data": {"topic": "transactions.global", "throughput_msg_sec": 4200},
            },
            {
                "node_id": "node_iso_forest",
                "node_type": NodeType.TRANSFORM,
                "label": "Anomaly Detection Scorer",
                "position_x": 460.0,
                "position_y": 180.0,
                "status": NodeExecutionStatus.SUCCESS,
                "data": {"model": "IsolationForest_v3", "latency_ms": 3.8},
            },
            {
                "node_id": "node_card_freeze",
                "node_type": NodeType.TOOL,
                "label": "Account Freeze Gateway",
                "position_x": 820.0,
                "position_y": 180.0,
                "status": NodeExecutionStatus.IDLE,
                "data": {"provider": "Stripe/Visa", "auto_freeze_threshold": 0.95},
            },
        ],
        "edges": [
            ("node_kafka_stream", "node_iso_forest", "data_stream"),
            ("node_iso_forest", "node_card_freeze", "action_trigger"),
        ],
    },
]


def seed():
    print(f"Connecting to database and initializing schemas...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear previous seed data
    print("Clearing previous seed data...")
    db.query(ActionExecution).delete()
    db.query(MultimodalMessage).delete()
    db.query(CanvasEdge).delete()
    db.query(CanvasNode).delete()
    db.query(CanvasSession).delete()
    db.commit()

    print("Seeding demo canvas workspaces, nodes, and edges...")
    for s_info in DEMO_SESSIONS:
        sess = CanvasSession(
            session_id=s_info["session_id"],
            title=s_info["title"],
            description=s_info["description"],
            status=SessionStatus.ACTIVE.value,
            viewport_x=0.0,
            viewport_y=0.0,
            viewport_zoom=1.0,
            voice_enabled=True,
            created_at=datetime.utcnow() - timedelta(hours=4),
            updated_at=datetime.utcnow(),
        )
        db.add(sess)

        # Seed nodes
        for n in s_info["nodes"]:
            node = CanvasNode(
                node_id=n["node_id"],
                session_id=sess.session_id,
                node_type=n["node_type"].value,
                label=n["label"],
                position_x=n["position_x"],
                position_y=n["position_y"],
                width=260.0,
                height=150.0,
                data=n["data"],
                execution_status=n["status"].value,
                created_at=datetime.utcnow() - timedelta(hours=4),
                updated_at=datetime.utcnow(),
            )
            db.add(node)

        # Seed edges
        for src, tgt, edge_type in s_info["edges"]:
            edge = CanvasEdge(
                edge_id=f"edge_{uuid.uuid4().hex[:10]}",
                session_id=sess.session_id,
                source_node_id=src,
                target_node_id=tgt,
                edge_type=edge_type,
                created_at=datetime.utcnow() - timedelta(hours=3, minutes=55),
            )
            db.add(edge)

        # Seed sample voice message
        user_msg = MultimodalMessage(
            message_id=f"msg_voice_{uuid.uuid4().hex[:8]}",
            session_id=sess.session_id,
            sender=MessageSender.USER.value,
            modality=ModalityType.VOICE.value,
            content="Create a filter node that isolates customer churn probability > 0.8",
            audio_metadata={"confidence": 0.98, "sample_rate": 16000},
            created_at=datetime.utcnow() - timedelta(hours=2),
        )
        asst_msg = MultimodalMessage(
            message_id=f"msg_reply_{uuid.uuid4().hex[:8]}",
            session_id=sess.session_id,
            sender=MessageSender.ASSISTANT.value,
            modality=ModalityType.ACTION.value,
            content="Created filter node 'High Churn Risk Filter' and connected it to downstream actions.",
            created_at=datetime.utcnow() - timedelta(hours=1, minutes=59),
        )
        db.add(user_msg)
        db.add(asst_msg)

        # Seed action execution log
        action = ActionExecution(
            action_id=f"act_{uuid.uuid4().hex[:8]}",
            session_id=sess.session_id,
            action_type=ActionType.CREATE_NODE.value,
            status=ActionStatus.SUCCESS.value,
            parameters={"label": "High Churn Risk Filter", "node_type": "filter"},
            execution_result={"node_id": "node_churn_filter", "status": "deployed"},
            latency_ms=14.8,
            created_at=datetime.utcnow() - timedelta(hours=2),
        )
        db.add(action)

    db.commit()
    db.close()
    print("✅ Successfully seeded enterprise demo workspaces, nodes, edges, and voice messages!")


if __name__ == "__main__":
    seed()
