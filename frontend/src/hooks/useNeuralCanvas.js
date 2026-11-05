import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../services/api';
import {
  INITIAL_DEMO_SESSION,
  INITIAL_DEMO_NODES,
  INITIAL_DEMO_EDGES,
  INITIAL_DEMO_ACTIONS,
  INITIAL_DEMO_MESSAGES
} from '../services/mockData';

export function useNeuralCanvas() {
  const [session, setSession] = useState(INITIAL_DEMO_SESSION);
  const [nodes, setNodes] = useState(INITIAL_DEMO_NODES);
  const [edges, setEdges] = useState(INITIAL_DEMO_EDGES);
  const [actions, setActions] = useState(INITIAL_DEMO_ACTIONS);
  const [messages, setMessages] = useState(INITIAL_DEMO_MESSAGES);
  const [selectedNode, setSelectedNode] = useState(null);
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1.0 });

  // Voice stream state
  const [isRecording, setIsRecording] = useState(false);
  const [vadEnergy, setVadEnergy] = useState(0.0);
  const [wsConnected, setWsConnected] = useState(false);

  const wsRef = useRef(null);
  const audioIntervalRef = useRef(null);

  // 1. Initialize session & Fetch data
  useEffect(() => {
    async function loadSession() {
      const data = await api.getSession(INITIAL_DEMO_SESSION.session_id);
      if (data) {
        setSession(data);
        if (data.nodes) setNodes(data.nodes);
        if (data.edges) setEdges(data.edges);
        if (data.actions) setActions(data.actions);
        if (data.messages) setMessages(data.messages);
      }
    }
    loadSession();
  }, []);

  // 2. Setup WebSocket Connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/v1/sessions/${session.session_id}`;
    
    let socket;
    try {
      socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        setWsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'action_dispatched') {
            // Append action to local state
            setActions(prev => [payload.action || {
              action_id: payload.action_id,
              action_type: payload.action_type,
              status: payload.status,
              latency_ms: 14.5,
              created_at: new Date().toISOString()
            }, ...prev]);

            // Append assistant reply to messages
            if (payload.assistant_reply) {
              setMessages(prev => [...prev, {
                message_id: `msg_${Date.now()}`,
                session_id: session.session_id,
                sender: 'assistant',
                modality: 'action',
                content: payload.assistant_reply,
                created_at: new Date().toISOString()
              }]);
            }
          }
        } catch (e) {
          console.warn("WebSocket frame parse caveat:", e);
        }
      };

      socket.onclose = () => {
        setWsConnected(false);
      };

      socket.onerror = () => {
        setWsConnected(false);
      };
    } catch {
      setWsConnected(false);
    }

    return () => {
      if (socket) socket.close();
    };
  }, [session.session_id]);

  // 3. Audio & Voice Recording Simulation
  const startVoiceRecording = useCallback(() => {
    setIsRecording(true);
    // Simulate real-time VAD energy modulation
    audioIntervalRef.current = setInterval(() => {
      // Fluctuates between 0.02 and 0.09 energy (above 0.015 threshold)
      const simulatedEnergy = +(0.02 + Math.random() * 0.07).toFixed(4);
      setVadEnergy(simulatedEnergy);
    }, 120);
  }, []);

  const stopVoiceRecording = useCallback((transcription = "Create a data transform node that filters customer churn > 0.8") => {
    setIsRecording(false);
    setVadEnergy(0.0);
    if (audioIntervalRef.current) {
      clearInterval(audioIntervalRef.current);
      audioIntervalRef.current = null;
    }

    if (transcription) {
      dispatchVoiceIntent(transcription);
    }
  }, []);

  // 4. Dispatch Voice Intent
  const dispatchVoiceIntent = useCallback(async (transcription) => {
    // Optimistically record user voice message
    const userMsg = {
      message_id: `msg_${Date.now()}`,
      session_id: session.session_id,
      sender: 'user',
      modality: 'voice',
      content: transcription,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);

    // Send frame through WebSocket if connected
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "voice_intent",
        session_id: session.session_id,
        transcription: transcription,
        confidence: 0.98
      }));
    }

    // Call REST endpoint
    const res = await api.dispatchVoiceIntent(session.session_id, transcription);
    if (res) {
      setActions(prev => [{
        action_id: res.action_id || `act_${Date.now()}`,
        session_id: session.session_id,
        action_type: res.action_type,
        status: res.status || "success",
        parameters: { transcription },
        execution_result: { summary: res.summary },
        latency_ms: res.latency_ms || 16.2,
        created_at: new Date().toISOString()
      }, ...prev]);

      if (res.assistant_reply) {
        setMessages(prev => [...prev, {
          message_id: `msg_resp_${Date.now()}`,
          session_id: session.session_id,
          sender: 'assistant',
          modality: 'action',
          content: res.assistant_reply,
          created_at: new Date().toISOString()
        }]);
      }

      // If intent created a node, synthesize it onto canvas
      if (res.action_type === 'CREATE_NODE' || transcription.toLowerCase().includes('create')) {
        const newNode = {
          node_id: res.affected_node_id || `node_syn_${Date.now()}`,
          session_id: session.session_id,
          node_type: 'filter',
          label: 'Voice Generated Filter Node',
          position_x: 480 + Math.random() * 80,
          position_y: 220 + Math.random() * 80,
          width: 250,
          height: 140,
          execution_status: 'success',
          data: { generated_from: transcription, condition: 'churn > 0.8' }
        };
        setNodes(prev => [...prev, newNode]);
      }
    }
  }, [session.session_id]);

  // 5. Node & Edge CRUD
  const addNode = useCallback(async (nodeData) => {
    const created = await api.createNode(session.session_id, nodeData);
    setNodes(prev => [...prev, created]);
    return created;
  }, [session.session_id]);

  const deleteNode = useCallback(async (nodeId) => {
    await api.deleteNode(session.session_id, nodeId);
    setNodes(prev => prev.filter(n => n.node_id !== nodeId));
    setEdges(prev => prev.filter(e => e.source_node_id !== nodeId && e.target_node_id !== nodeId));
    if (selectedNode?.node_id === nodeId) {
      setSelectedNode(null);
    }
  }, [session.session_id, selectedNode]);

  const connectNodes = useCallback(async (sourceId, targetId, edgeType = 'data_stream') => {
    const newEdge = await api.createEdge(session.session_id, {
      source_node_id: sourceId,
      target_node_id: targetId,
      edge_type: edgeType
    });
    setEdges(prev => [...prev, newEdge]);
  }, [session.session_id]);

  const resetViewport = useCallback(() => {
    setViewport({ x: 0, y: 0, zoom: 1.0 });
  }, []);

  const createNewSession = useCallback(async () => {
    const newSess = await api.createSession({
      title: `Canvas Session #${Date.now().toString().slice(-4)}`,
      description: "Interactive voice-driven canvas DAG session"
    });
    setSession(newSess);
    setNodes([]);
    setEdges([]);
    setActions([]);
    setMessages([]);
    setSelectedNode(null);
    resetViewport();
  }, [resetViewport]);

  return {
    session,
    nodes,
    edges,
    actions,
    messages,
    selectedNode,
    viewport,
    wsConnected,
    isRecording,
    vadEnergy,
    setSelectedNode,
    setViewport,
    startVoiceRecording,
    stopVoiceRecording,
    dispatchVoiceIntent,
    addNode,
    deleteNode,
    connectNodes,
    resetViewport,
    createNewSession
  };
}
