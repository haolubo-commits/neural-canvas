import React, { useState } from 'react';

export default function ActionHistoryDrawer({
  actions = [],
  messages = [],
  nodes = []
}) {
  const [tab, setTab] = useState('actions'); // 'actions' | 'dialogue'

  return (
    <div className="glass-panel" style={{
      flex: 1,
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Tabs */}
      <div style={{
        display: 'flex',
        gap: '8px',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '10px',
        marginBottom: '12px'
      }}>
        <button
          onClick={() => setTab('actions')}
          style={{
            background: 'transparent',
            color: tab === 'actions' ? 'var(--accent-cyan)' : 'var(--text-muted)',
            fontWeight: tab === 'actions' ? 600 : 400,
            fontSize: '0.82rem',
            borderBottom: tab === 'actions' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
            paddingBottom: '4px'
          }}
        >
          Dispatched Actions ({actions.length})
        </button>
        <button
          onClick={() => setTab('dialogue')}
          style={{
            background: 'transparent',
            color: tab === 'dialogue' ? 'var(--accent-purple)' : 'var(--text-muted)',
            fontWeight: tab === 'dialogue' ? 600 : 400,
            fontSize: '0.82rem',
            borderBottom: tab === 'dialogue' ? '2px solid var(--accent-purple)' : '2px solid transparent',
            paddingBottom: '4px'
          }}
        >
          Multimodal Feed ({messages.length})
        </button>
      </div>

      {/* Content Container */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {tab === 'actions' ? (
          actions.length === 0 ? (
            <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textAlign: 'center', marginTop: '24px' }}>
              No actions dispatched yet.
            </div>
          ) : (
            actions.map((act) => (
              <div
                key={act.action_id}
                style={{
                  backgroundColor: 'rgba(0, 0, 0, 0.25)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '8px 12px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    fontFamily: 'var(--font-mono)',
                    color: act.status === 'success' ? 'var(--accent-emerald)' : 'var(--accent-rose)'
                  }}>
                    {act.action_type}
                  </span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    {act.latency_ms ? `${act.latency_ms}ms` : '<20ms'}
                  </span>
                </div>
                {act.parameters && (
                  <div style={{
                    fontSize: '0.72rem',
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-mono)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {JSON.stringify(act.parameters)}
                  </div>
                )}
              </div>
            ))
          )
        ) : (
          messages.length === 0 ? (
            <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textAlign: 'center', marginTop: '24px' }}>
              No voice or text messages recorded.
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.message_id}
                style={{
                  alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                  backgroundColor: msg.sender === 'user' ? 'rgba(56, 189, 248, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${msg.sender === 'user' ? 'rgba(56, 189, 248, 0.3)' : 'var(--border-subtle)'}`,
                  borderRadius: '10px',
                  padding: '8px 12px',
                  fontSize: '0.8rem',
                  lineHeight: '1.4'
                }}
              >
                <div style={{
                  fontSize: '0.68rem',
                  fontWeight: 600,
                  marginBottom: '2px',
                  color: msg.sender === 'user' ? 'var(--accent-cyan)' : 'var(--accent-purple)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  {msg.sender === 'user' ? '🎙️ User' : '🤖 Assistant'}
                </div>
                <div>{msg.content}</div>
              </div>
            ))
          )
        )}
      </div>
    </div>
  );
}
