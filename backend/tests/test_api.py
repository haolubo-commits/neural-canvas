"""
Integration tests for NeuralCanvas FastAPI REST endpoints.
"""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "NeuralCanvas" in data["message"]
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"
    assert "ws_v1" in data


def test_health_check_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["service"] == "NeuralCanvas"
    assert data["audio_sample_rate_hz"] == 16000


def test_session_lifecycle(client: TestClient):
    # 1. Create Session
    create_res = client.post(
        "/api/v1/sessions",
        json={"title": "Marketing Retention Canvas", "description": "Q4 Campaigns"},
    )
    assert create_res.status_code == 201
    sess_data = create_res.json()
    session_id = sess_data["session_id"]
    assert sess_data["title"] == "Marketing Retention Canvas"

    # 2. Get Session Details
    get_res = client.get(f"/api/v1/sessions/{session_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["session_id"] == session_id
    assert isinstance(detail["nodes"], list)

    # 3. Patch Session Viewport
    patch_res = client.patch(
        f"/api/v1/sessions/{session_id}",
        json={"viewport_x": 150.0, "viewport_zoom": 1.25},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["viewport_x"] == 150.0
    assert patch_res.json()["viewport_zoom"] == 1.25

    # 4. Topology Check
    topo_res = client.get(f"/api/v1/sessions/{session_id}/topology")
    assert topo_res.status_code == 200
    assert topo_res.json()["node_count"] == 0

    # 5. Delete Session
    del_res = client.delete(f"/api/v1/sessions/{session_id}")
    assert del_res.status_code == 200

    # Confirm 404 after deletion
    assert client.get(f"/api/v1/sessions/{session_id}").status_code == 404


def test_node_and_edge_api(client: TestClient, sample_session):
    session_id = sample_session.session_id

    # 1. Create Node
    node_res = client.post(
        f"/api/v1/sessions/{session_id}/nodes",
        json={
            "node_type": "visualization",
            "label": "Live Stream Chart",
            "position_x": 600.0,
            "position_y": 200.0,
        },
    )
    assert node_res.status_code == 201
    node_id = node_res.json()["node_id"]

    # 2. List Nodes
    list_res = client.get(f"/api/v1/sessions/{session_id}/nodes")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 3

    # 3. Connect Nodes (Edge)
    edge_res = client.post(
        f"/api/v1/sessions/{session_id}/edges",
        json={
            "source_node_id": "node_tgt_02",
            "target_node_id": node_id,
            "edge_type": "chart_feed",
        },
    )
    assert edge_res.status_code == 201
    edge_id = edge_res.json()["edge_id"]

    # 4. Delete Edge
    del_edge = client.delete(f"/api/v1/sessions/{session_id}/edges/{edge_id}")
    assert del_edge.status_code == 200


def test_voice_intent_action_api(client: TestClient, sample_session):
    session_id = sample_session.session_id

    # Dispatch Voice Intent
    intent_res = client.post(
        f"/api/v1/sessions/{session_id}/actions/voice-intent",
        json={
            "transcription": "Create a filter node named high_risk_filter",
            "confidence": 0.99,
        },
    )
    assert intent_res.status_code == 200
    data = intent_res.json()
    assert data["session_id"] == session_id
    assert data["action_type"] == "CREATE_NODE"
    assert data["status"] == "success"
    assert "high_risk_filter" in data["summary"]

    # Query Actions
    act_res = client.get(f"/api/v1/sessions/{session_id}/actions")
    assert act_res.status_code == 200
    assert len(act_res.json()) >= 1


def test_vad_check_api(client: TestClient, sample_session):
    import base64
    import struct
    session_id = sample_session.session_id

    # 100 samples of 16-bit silence
    silence = struct.pack("<100h", *[0] * 100)
    b64_payload = base64.b64encode(silence).decode("utf-8")

    res = client.post(
        f"/api/v1/sessions/{session_id}/actions/vad-check",
        json={"pcm_base64": b64_payload},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_active_speech"] is False
    assert data["rms_energy"] == 0.0
