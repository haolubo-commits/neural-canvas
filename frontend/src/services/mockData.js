/**
 * Demo and fallback mock datasets for NeuralCanvas.
 * Populates realistic multimodal sessions, nodes, edges, and action logs.
 */

export const INITIAL_DEMO_SESSION = {
  session_id: "sess_demo_alpha",
  title: "AI Customer Intelligence & Churn DAG",
  description: "Multimodal voice-driven pipeline correlating CRM telemetry, sentiment, and automated alerts.",
  status: "active",
  viewport_x: 0,
  viewport_y: 0,
  viewport_zoom: 1.0,
  voice_enabled: true,
  created_at: new Date(Date.now() - 3600000).toISOString(),
  updated_at: new Date().toISOString()
};

export const INITIAL_DEMO_NODES = [
  {
    node_id: "node_prompt_input",
    session_id: "sess_demo_alpha",
    node_type: "prompt",
    label: "Voice Ingestion & Query Parser",
    position_x: 80,
    position_y: 140,
    width: 250,
    height: 140,
    execution_status: "success",
    data: {
      input_source: "Microphone 16kHz PCM",
      vad_threshold: 0.015,
      last_intent: "Filter customers churn > 0.8"
    }
  },
  {
    node_id: "node_data_crm",
    session_id: "sess_demo_alpha",
    node_type: "data_source",
    label: "PostgreSQL Customer DB",
    position_x: 400,
    position_y: 100,
    width: 260,
    height: 150,
    execution_status: "success",
    data: {
      table: "customer_telemetry",
      row_count: 48250,
      query_latency_ms: 14.2
    }
  },
  {
    node_id: "node_churn_filter",
    session_id: "sess_demo_alpha",
    node_type: "filter",
    label: "High Churn Risk Filter",
    position_x: 740,
    position_y: 130,
    width: 260,
    height: 150,
    execution_status: "success",
    data: {
      condition: "churn_probability >= 0.80",
      matched_records: 142,
      reduction_ratio: "99.7%"
    }
  },
  {
    node_id: "node_slack_alert",
    session_id: "sess_demo_alpha",
    node_type: "tool",
    label: "Slack Retention Alert Bot",
    position_x: 1080,
    position_y: 130,
    width: 250,
    height: 140,
    execution_status: "idle",
    data: {
      channel: "#cx-urgent-escalations",
      webhook_status: "connected",
      dispatched_count: 14
    }
  },
  {
    node_id: "node_analytics_viz",
    session_id: "sess_demo_alpha",
    node_type: "visualization",
    label: "Real-Time Risk Distribution",
    position_x: 580,
    position_y: 360,
    width: 280,
    height: 160,
    execution_status: "running",
    data: {
      chart_type: "Density Heatmap",
      refresh_rate_sec: 2
    }
  }
];

export const INITIAL_DEMO_EDGES = [
  {
    edge_id: "edge_01",
    session_id: "sess_demo_alpha",
    source_node_id: "node_prompt_input",
    target_node_id: "node_data_crm",
    source_handle: "output",
    target_handle: "input",
    edge_type: "data_stream"
  },
  {
    edge_id: "edge_02",
    session_id: "sess_demo_alpha",
    source_node_id: "node_data_crm",
    target_node_id: "node_churn_filter",
    source_handle: "output",
    target_handle: "input",
    edge_type: "data_stream"
  },
  {
    edge_id: "edge_03",
    session_id: "sess_demo_alpha",
    source_node_id: "node_churn_filter",
    target_node_id: "node_slack_alert",
    source_handle: "output",
    target_handle: "input",
    edge_type: "alert_trigger"
  },
  {
    edge_id: "edge_04",
    session_id: "sess_demo_alpha",
    source_node_id: "node_churn_filter",
    target_node_id: "node_analytics_viz",
    source_handle: "output",
    target_handle: "input",
    edge_type: "metrics_stream"
  }
];

export const INITIAL_DEMO_MESSAGES = [
  {
    message_id: "msg_001",
    session_id: "sess_demo_alpha",
    sender: "user",
    modality: "voice",
    content: "Create a data transform node that filters customer churn > 0.8 and wire it to the Slack alert node",
    created_at: new Date(Date.now() - 1200000).toISOString()
  },
  {
    message_id: "msg_002",
    session_id: "sess_demo_alpha",
    sender: "assistant",
    modality: "action",
    content: "Created filter node 'High Churn Risk Filter' and connected it to 'Slack Retention Alert Bot'.",
    created_at: new Date(Date.now() - 1198000).toISOString()
  },
  {
    message_id: "msg_003",
    session_id: "sess_demo_alpha",
    sender: "user",
    modality: "voice",
    content: "Add a visualization node showing risk distribution",
    created_at: new Date(Date.now() - 600000).toISOString()
  },
  {
    message_id: "msg_004",
    session_id: "sess_demo_alpha",
    sender: "assistant",
    modality: "action",
    content: "Spawned visualization node 'Real-Time Risk Distribution' at coordinate (580, 360).",
    created_at: new Date(Date.now() - 598000).toISOString()
  }
];

export const INITIAL_DEMO_ACTIONS = [
  {
    action_id: "act_001",
    session_id: "sess_demo_alpha",
    action_type: "CREATE_NODE",
    status: "success",
    parameters: { node_type: "filter", label: "High Churn Risk Filter" },
    execution_result: { created_node_id: "node_churn_filter" },
    latency_ms: 18.4,
    created_at: new Date(Date.now() - 1200000).toISOString()
  },
  {
    action_id: "act_002",
    session_id: "sess_demo_alpha",
    action_type: "CONNECT_NODES",
    status: "success",
    parameters: { source: "node_churn_filter", target: "node_slack_alert" },
    execution_result: { edge_id: "edge_03" },
    latency_ms: 12.1,
    created_at: new Date(Date.now() - 1199000).toISOString()
  },
  {
    action_id: "act_003",
    session_id: "sess_demo_alpha",
    action_type: "CREATE_NODE",
    status: "success",
    parameters: { node_type: "visualization", label: "Real-Time Risk Distribution" },
    execution_result: { created_node_id: "node_analytics_viz" },
    latency_ms: 16.8,
    created_at: new Date(Date.now() - 600000).toISOString()
  }
];
