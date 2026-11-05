import React, { useState } from 'react';

const PRESET_VOICE_COMMANDS = [
  "Create a filter node named Churn_Filter",
  "Connect Churn_Filter to Slack_Alert",
  "Add visualization node for risk distribution",
  "Execute tool retention_bot",
  "Create prompt node named Customer_Ingest"
];

export default function VoiceActionCockpit({
  isRecording,
  onStartRecording,
  onStopRecording,
  onDispatchIntent,
  selectedNode,
  onAddNode
}) {
  const [inputText, setInputText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onDispatchIntent(inputText.trim());
    setInputText("");
  };

  const handlePresetClick = (cmd) => {
    onDispatchIntent(cmd);
  };

  const handleQuickAdd = (type, label) => {
    onAddNode({
      node_type: type,
      label: label,
      position_x: 200 + Math.random() * 200,
      position_y: 180 + Math.random() * 200,
      data: { created_via: "quick_action" }
    });
  };

  return (
    <div className="glass-panel" style={{
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '14px'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ fontSize: '0.95rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>⚡</span> Voice Action Cockpit
        </h3>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Speech-to-Action Parser
        </span>
      </div>

      {/* Voice Intent Prompt Input Bar */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px' }}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Speak or type command (e.g. 'Create filter node')..."
          style={{
            flex: 1,
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '8px',
            padding: '10px 14px',
            color: 'var(--text-main)',
            fontSize: '0.85rem',
            outline: 'none',
            fontFamily: 'var(--font-sans)'
          }}
        />
        <button
          type="submit"
          className="btn-primary"
          style={{ padding: '0 16px', fontSize: '0.85rem' }}
        >
          Send
        </button>
      </form>

      {/* Preset Voice Command Shortcuts */}
      <div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Suggested Voice Intent Commands
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {PRESET_VOICE_COMMANDS.map((cmd, idx) => (
            <button
              key={idx}
              onClick={() => handlePresetClick(cmd)}
              className="btn-secondary"
              style={{
                textAlign: 'left',
                fontSize: '0.78rem',
                padding: '6px 10px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <span style={{ color: 'var(--accent-cyan)' }}>🎙️</span>
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                "{cmd}"
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Quick Node Creation Buttons */}
      <div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Quick Canvas Nodes
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
          <button
            onClick={() => handleQuickAdd('prompt', 'Prompt Ingest')}
            className="btn-secondary"
            style={{ fontSize: '0.75rem', padding: '6px 8px' }}
          >
            + Prompt
          </button>
          <button
            onClick={() => handleQuickAdd('filter', 'Data Filter')}
            className="btn-secondary"
            style={{ fontSize: '0.75rem', padding: '6px 8px' }}
          >
            + Filter
          </button>
          <button
            onClick={() => handleQuickAdd('tool', 'Agent Tool')}
            className="btn-secondary"
            style={{ fontSize: '0.75rem', padding: '6px 8px' }}
          >
            + Tool
          </button>
        </div>
      </div>
    </div>
  );
}
