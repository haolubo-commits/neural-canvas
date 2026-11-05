import React, { useState, useEffect } from 'react';

export default function AudioVisualizer({ isRecording, energy = 0.0, onToggleMic }) {
  const [barHeights, setBarHeights] = useState([12, 18, 10, 24, 16, 32, 22, 14, 28, 18, 12, 20]);

  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setBarHeights(prev =>
          prev.map(() => Math.floor(10 + Math.random() * 45))
        );
      }, 100);
    } else {
      setBarHeights([8, 10, 8, 12, 10, 14, 10, 8, 12, 10, 8, 10]);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  return (
    <div className="glass-panel" style={{
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      padding: '10px 18px',
      borderRadius: '9999px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
      border: isRecording ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid var(--border-subtle)',
      background: 'rgba(15, 23, 42, 0.85)'
    }}>
      {/* Mic Action Toggle Button */}
      <button
        onClick={onToggleMic}
        className={`btn-voice ${isRecording ? 'recording' : ''}`}
        style={{ padding: '8px 16px', fontSize: '0.85rem' }}
      >
        <span style={{ fontSize: '1.1rem' }}>{isRecording ? '⏹' : '🎙️'}</span>
        {isRecording ? 'Streaming...' : 'Voice Mic'}
      </button>

      {/* Dynamic Animated Frequency Bars */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        height: '32px'
      }}>
        {barHeights.map((h, i) => (
          <div
            key={i}
            style={{
              width: '4px',
              height: `${h}px`,
              borderRadius: '2px',
              backgroundColor: isRecording ? (i % 2 === 0 ? '#f43f5e' : '#a855f7') : '#64748b',
              transition: 'height 0.1s ease',
              boxShadow: isRecording ? '0 0 6px rgba(244, 63, 94, 0.4)' : 'none'
            }}
          />
        ))}
      </div>

      {/* Audio Metric Readout */}
      <div style={{
        fontSize: '0.75rem',
        color: isRecording ? 'var(--accent-rose)' : 'var(--text-muted)',
        fontFamily: 'var(--font-mono)',
        minWidth: '60px'
      }}>
        {isRecording ? `${(energy * 1000).toFixed(1)} dB` : '16kHz PCM'}
      </div>
    </div>
  );
}
