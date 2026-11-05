/**
 * API client and WebSocket gateway utilities for NeuralCanvas.
 */

import {
  INITIAL_DEMO_SESSION,
  INITIAL_DEMO_NODES,
  INITIAL_DEMO_EDGES,
  INITIAL_DEMO_ACTIONS,
  INITIAL_DEMO_MESSAGES
} from './mockData';

const BASE_URL = '/api/v1';

export const api = {
  // Session Endpoints
  async getSession(sessionId) {
    try {
      const res = await fetch(`${BASE_URL}/sessions/${sessionId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn("Backend offline, utilizing initial mock session data:", err.message);
      return {
        ...INITIAL_DEMO_SESSION,
        nodes: INITIAL_DEMO_NODES,
        edges: INITIAL_DEMO_EDGES,
        actions: INITIAL_DEMO_ACTIONS,
        messages: INITIAL_DEMO_MESSAGES
      };
    }
  },

  async listSessions() {
    try {
      const res = await fetch(`${BASE_URL}/sessions`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch {
      return [INITIAL_DEMO_SESSION];
    }
  },

  async createSession(payload) {
    try {
      const res = await fetch(`${BASE_URL}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      return await res.json();
    } catch {
      return { ...INITIAL_DEMO_SESSION, ...payload };
    }
  },

  // Node Endpoints
  async createNode(sessionId, nodePayload) {
    try {
      const res = await fetch(`${BASE_URL}/sessions/${sessionId}/nodes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nodePayload)
      });
      return await res.json();
    } catch {
      return {
        node_id: `node_${Date.now()}`,
        session_id: sessionId,
        ...nodePayload,
        created_at: new Date().toISOString()
      };
    }
  },

  async updateNode(sessionId, nodeId, updatePayload) {
    try {
      const res = await fetch(`${BASE_URL}/sessions/${sessionId}/nodes/${nodeId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatePayload)
      });
      return await res.json();
    } catch {
      return { node_id: nodeId, ...updatePayload };
    }
  },

  async deleteNode(sessionId, nodeId) {
    try {
      const res = await fetch(`${BASE_URL}/sessions/${sessionId}/nodes/${nodeId}`, {
        method: 'DELETE'
      });
      return await res.json();
    } catch {
      return { message: "Node deleted (mock)" };
    }
  },

  // Edge Endpoints
  async createEdge(sessionId, edgePayload) {
    try {
      const res = await fetch(`${BASE_URL}/sessions/${sessionId}/edges`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(edgePayload)
      });
      return await res.json();
    } catch {
      return {
        edge_id: `edge_${Date.now()}`,
        session_id: sessionId,
        ...edgePayload,
        created_at: new Date().toISOString()
      };
    }
  },

  async deleteEdge(sessionId, edgeId) {
    try {
      const res = await fetch(`${BASE_URL}/sessions/${sessionId}/edges/${edgeId}`, {
        method: 'DELETE'
      });
      return await res.json();
    } catch {
      return { message: "Edge deleted (mock)" };
    }
  },

  // Voice Intent & Actions
  async dispatchVoiceIntent(sessionId, transcription, confidence = 1.0) {
    try {
      const res = await fetch(`${BASE_URL}/sessions/${sessionId}/actions/voice-intent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcription, confidence })
      });
      return await res.json();
    } catch {
      // Local fallback parsing
      return {
        session_id: sessionId,
        action_id: `act_${Date.now()}`,
        action_type: "VOICE_SYNTHESIS",
        status: "success",
        summary: `Processed: ${transcription}`,
        assistant_reply: `Processed voice query: "${transcription}"`,
        latency_ms: 15.4
      };
    }
  },

  // Health
  async checkHealth() {
    try {
      const res = await fetch('/health');
      return await res.json();
    } catch {
      return { status: "offline", service: "NeuralCanvas" };
    }
  }
};
