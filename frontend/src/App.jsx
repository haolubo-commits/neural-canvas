import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MetricsBar from './components/MetricsBar';
import CanvasBoard from './components/CanvasBoard';
import AudioVisualizer from './components/AudioVisualizer';
import VoiceActionCockpit from './components/VoiceActionCockpit';
import ActionHistoryDrawer from './components/ActionHistoryDrawer';
import { useNeuralCanvas } from './hooks/useNeuralCanvas';

export default function App() {
  const {
    session,
    nodes,
    edges,
    actions,
    messages,
    wsConnected,
    isRecording,
    vadEnergy,
    selectedNode,
    viewport,
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
  } = useNeuralCanvas();

  const [activeTab, setActiveTab] = useState('canvas'); // 'canvas' | 'actions' | 'topology'

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      backgroundColor: 'var(--bg-primary)',
      overflow: 'hidden'
    }}>
      {/* 1. Top Navigation Bar */}
      <Header
        session={session}
        nodeCount={nodes.length}
        edgeCount={edges.length}
        wsConnected={wsConnected}
        isRecording={isRecording}
        onResetViewport={resetViewport}
        onNewSession={createNewSession}
      />

      {/* 2. Real-Time Telemetry & Metrics Row */}
      <MetricsBar
        nodes={nodes}
        edges={edges}
        actions={actions}
        vadEnergy={vadEnergy}
        isRecording={isRecording}
      />

      {/* 3. Main Workspace Area: Split Canvas + Voice Action Cockpit + Event Drawer */}
      <div style={{
        display: 'flex',
        flex: 1,
        margin: '0 16px 16px 16px',
        gap: '12px',
        overflow: 'hidden',
        position: 'relative'
      }}>
        {/* Left/Center: 2D Spatial Infinite Canvas */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          borderRadius: '12px',
          overflow: 'hidden',
          border: '1px solid var(--border-subtle)'
        }}>
          <CanvasBoard
            nodes={nodes}
            edges={edges}
            viewport={viewport}
            selectedNode={selectedNode}
            onSelectNode={setSelectedNode}
            onViewportChange={setViewport}
            onDeleteNode={deleteNode}
            onConnectNodes={connectNodes}
          />

          {/* Floating Live Audio Waveform Visualizer in Bottom Corner of Canvas */}
          <div style={{
            position: 'absolute',
            bottom: '16px',
            left: '16px',
            zIndex: 20
          }}>
            <AudioVisualizer
              isRecording={isRecording}
              energy={vadEnergy}
              onToggleMic={isRecording ? stopVoiceRecording : startVoiceRecording}
            />
          </div>
        </div>

        {/* Right Sidebar: Voice Action Cockpit & Execution Audit Feed */}
        <div style={{
          width: '380px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          overflow: 'hidden'
        }}>
          {/* Voice Action Cockpit */}
          <VoiceActionCockpit
            isRecording={isRecording}
            onStartRecording={startVoiceRecording}
            onStopRecording={stopVoiceRecording}
            onDispatchIntent={dispatchVoiceIntent}
            selectedNode={selectedNode}
            onAddNode={addNode}
          />

          {/* Action Execution Drawer & Multimodal Chat Stream */}
          <ActionHistoryDrawer
            actions={actions}
            messages={messages}
            nodes={nodes}
          />
        </div>
      </div>
    </div>
  );
}
