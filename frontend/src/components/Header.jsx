import React from 'react';

export default function Header({
  session,
  nodeCount,
  edgeCount,
  wsConnected,
  isRecording,
  onResetViewport,
  onNewSession
}) {
  return (
    <header className="glass-panel" style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 24px',
      margin: '12px 16px',
      borderBottom: '1px solid var(--border-subtle)'
    }}>
      {/* Brand & Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '1.25rem',
          boxShadow: '0 0 16px rgba(14, 165, 233, 0.4)'
        }}>
          🎙️
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontSize: '1.15rem', fontWeight: 600, letterSpacing: '-0.02em' }}>
              NeuralCanvas
            </h1>
            <span style={{
              fontSize: '0.7rem',
              fontWeight: 600,
              padding: '2px 8px',
              borderRadius: '9999px',
              background: 'rgba(56, 189, 248, 0.15)',
              color: 'var(--accent-cyan)',
              border: '1px solid rgba(56, 189, 248, 0.3)'
            }}>
              v0.1.0 • Cockpit
            </span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {session ? session.title : "Multimodal Voice & Real-Time Action Cockpit"}
          </p>
        </div>
      </div>

      {/* Real-time Status Badges */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* WebSocket Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '0.8rem',
          padding: '6px 12px',
          borderRadius: '8px',
          background: wsConnected ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
          border: `1px solid ${wsConnected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
          color: wsConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: wsConnected ? '#10b981' : '#f43f5e',
            display: 'inline-block',
            boxShadow: wsConnected ? '0 0 8px #10b981' : 'none'
          }} />
          {wsConnected ? 'WebSocket Live' : 'Disconnected'}
        </div>

        {/* Voice Stream Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '0.8rem',
          padding: '6px 12px',
          borderRadius: '8px',
          background: isRecording ? 'rgba(239, 68, 68, 0.15)' : 'rgba(255, 255, 255, 0.05)',
          border: `1px solid ${isRecording ? 'rgba(239, 68, 68, 0.4)' : 'var(--border-subtle)'}`,
          color: isRecording ? '#f87171' : 'var(--text-muted)'
        }}>
          <span>{isRecording ? '● Voice Stream Active' : '○ Mic Standby'}</span>
        </div>

        {/* Graph Stats */}
        <div style={{
          fontSize: '0.8rem',
          color: 'var(--text-muted)',
          padding: '6px 10px',
          background: 'rgba(255, 255, 255, 0.03)',
          borderRadius: '8px',
          border: '1px solid var(--border-subtle)',
          fontFamily: 'var(--font-mono)'
        }}>
          {nodeCount} Nodes • {edgeCount} Edges
        </div>

        {/* Controls */}
        <button
          onClick={onResetViewport}
          className="btn-secondary"
          title="Reset Viewport to Origin (0,0)"
        >
          🎯 Reset Pan
        </button>

        <button
          onClick={onNewSession}
          className="btn-primary"
        >
          + New Session
        </button>
      </div>
    </header>
  );
}
