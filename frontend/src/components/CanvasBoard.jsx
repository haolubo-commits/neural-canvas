import React, { useState, useRef, useCallback } from 'react';

const NODE_TYPE_COLORS = {
  prompt: { bg: 'rgba(56, 189, 248, 0.15)', border: '#38bdf8', icon: '💬' },
  data_source: { bg: 'rgba(16, 185, 129, 0.15)', border: '#10b981', icon: '🗄️' },
  filter: { bg: 'rgba(245, 158, 11, 0.15)', border: '#f59e0b', icon: '⚡' },
  tool: { bg: 'rgba(168, 85, 247, 0.15)', border: '#a855f7', icon: '🛠️' },
  transform: { bg: 'rgba(59, 130, 246, 0.15)', border: '#3b82f6', icon: '🔄' },
  visualization: { bg: 'rgba(236, 72, 153, 0.15)', border: '#ec4899', icon: '📊' },
  output: { bg: 'rgba(148, 163, 184, 0.15)', border: '#94a3b8', icon: '📤' }
};

export default function CanvasBoard({
  nodes = [],
  edges = [],
  viewport = { x: 0, y: 0, zoom: 1.0 },
  selectedNode = null,
  onSelectNode,
  onViewportChange,
  onDeleteNode,
  onConnectNodes
}) {
  const containerRef = useRef(null);
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });

  // Dragging node state
  const [draggingNodeId, setDraggingNodeId] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [nodePositions, setNodePositions] = useState({});

  // Wiring / Edge creation state
  const [wiringSourceId, setWiringSourceId] = useState(null);

  // Helper to get effective position of node
  const getNodePos = useCallback((node) => {
    if (nodePositions[node.node_id]) {
      return nodePositions[node.node_id];
    }
    return { x: node.position_x, y: node.position_y };
  }, [nodePositions]);

  // Handle Pan start
  const handleMouseDown = (e) => {
    // Only pan if clicking canvas background
    if (e.target === containerRef.current || e.target.tagName === 'svg') {
      setIsPanning(true);
      setPanStart({ x: e.clientX - viewport.x, y: e.clientY - viewport.y });
    }
  };

  const handleMouseMove = (e) => {
    if (isPanning) {
      onViewportChange({
        ...viewport,
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y
      });
    } else if (draggingNodeId) {
      const containerRect = containerRef.current.getBoundingClientRect();
      const newX = (e.clientX - containerRect.left - viewport.x) / viewport.zoom - dragOffset.x;
      const newY = (e.clientY - containerRect.top - viewport.y) / viewport.zoom - dragOffset.y;

      setNodePositions(prev => ({
        ...prev,
        [draggingNodeId]: { x: Math.max(0, Math.round(newX)), y: Math.max(0, Math.round(newY)) }
      }));
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
    setDraggingNodeId(null);
  };

  const handleNodeMouseDown = (e, node) => {
    e.stopPropagation();
    onSelectNode(node);
    setDraggingNodeId(node.node_id);

    const pos = getNodePos(node);
    const containerRect = containerRef.current.getBoundingClientRect();
    const mouseX = (e.clientX - containerRect.left - viewport.x) / viewport.zoom;
    const mouseY = (e.clientY - containerRect.top - viewport.y) / viewport.zoom;

    setDragOffset({
      x: mouseX - pos.x,
      y: mouseY - pos.y
    });
  };

  // Handle Output Handle click for wiring
  const handlePortClick = (e, nodeId, isOutput) => {
    e.stopPropagation();
    if (isOutput) {
      setWiringSourceId(nodeId);
    } else if (wiringSourceId && wiringSourceId !== nodeId) {
      onConnectNodes(wiringSourceId, nodeId);
      setWiringSourceId(null);
    }
  };

  // Compute curved SVG path between nodes
  const renderEdgePath = (edge) => {
    const srcNode = nodes.find(n => n.node_id === edge.source_node_id);
    const tgtNode = nodes.find(n => n.node_id === edge.target_node_id);
    if (!srcNode || !tgtNode) return null;

    const srcPos = getNodePos(srcNode);
    const tgtPos = getNodePos(tgtNode);

    // Source output port is right center
    const x1 = srcPos.x + (srcNode.width || 250);
    const y1 = srcPos.y + (srcNode.height || 140) / 2;

    // Target input port is left center
    const x2 = tgtPos.x;
    const y2 = tgtPos.y + (tgtNode.height || 140) / 2;

    const dx = Math.abs(x2 - x1) * 0.55;
    const pathData = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;

    return (
      <g key={edge.edge_id}>
        {/* Glow backdrop line */}
        <path
          d={pathData}
          fill="none"
          stroke="rgba(56, 189, 248, 0.2)"
          strokeWidth="6"
        />
        {/* Crisp foreground stream line */}
        <path
          d={pathData}
          fill="none"
          stroke="#38bdf8"
          strokeWidth="2.5"
          strokeDasharray={edge.edge_type === 'alert_trigger' ? '6 4' : 'none'}
        />
        {/* Target arrow marker */}
        <circle cx={x2} cy={y2} r="4" fill="#38bdf8" />
      </g>
    );
  };

  return (
    <div
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      className="canvas-grid-bg"
      style={{
        flex: 1,
        width: '100%',
        height: '100%',
        position: 'relative',
        cursor: isPanning ? 'grabbing' : 'default',
        overflow: 'hidden',
        userSelect: 'none'
      }}
    >
      {/* Zoom / Pan Control Widget */}
      <div style={{
        position: 'absolute',
        top: '16px',
        right: '16px',
        zIndex: 25,
        display: 'flex',
        gap: '6px',
        background: 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(8px)',
        padding: '6px',
        borderRadius: '8px',
        border: '1px solid var(--border-subtle)'
      }}>
        <button
          onClick={() => onViewportChange({ ...viewport, zoom: Math.min(2.0, viewport.zoom + 0.1) })}
          className="btn-secondary"
          style={{ padding: '4px 10px', fontSize: '0.85rem' }}
        >
          +
        </button>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', padding: '0 4px', fontFamily: 'var(--font-mono)' }}>
          {Math.round(viewport.zoom * 100)}%
        </span>
        <button
          onClick={() => onViewportChange({ ...viewport, zoom: Math.max(0.4, viewport.zoom - 0.1) })}
          className="btn-secondary"
          style={{ padding: '4px 10px', fontSize: '0.85rem' }}
        >
          -
        </button>
      </div>

      {/* Wiring active mode indicator */}
      {wiringSourceId && (
        <div style={{
          position: 'absolute',
          top: '16px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 30,
          background: 'rgba(245, 158, 11, 0.9)',
          color: '#000',
          padding: '6px 14px',
          borderRadius: '9999px',
          fontSize: '0.8rem',
          fontWeight: 600,
          boxShadow: '0 4px 12px rgba(245, 158, 11, 0.4)'
        }}>
          ⚡ Wiring mode active: Click target node input handle
          <button
            onClick={() => setWiringSourceId(null)}
            style={{ marginLeft: '10px', background: 'transparent', fontWeight: 700 }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Canvas Viewport Transformer */}
      <div style={{
        transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${viewport.zoom})`,
        transformOrigin: '0 0',
        width: '100%',
        height: '100%',
        position: 'absolute',
        top: 0,
        left: 0
      }}>
        {/* SVG Directed Edge Lines Layer */}
        <svg style={{
          width: '5000px',
          height: '5000px',
          position: 'absolute',
          top: 0,
          left: 0,
          pointerEvents: 'none',
          overflow: 'visible'
        }}>
          {edges.map(renderEdgePath)}
        </svg>

        {/* Spatial Node Cards Layer */}
        {nodes.map(node => {
          const pos = getNodePos(node);
          const isSelected = selectedNode?.node_id === node.node_id;
          const typeStyle = NODE_TYPE_COLORS[node.node_type] || NODE_TYPE_COLORS.prompt;

          return (
            <div
              key={node.node_id}
              onMouseDown={(e) => handleNodeMouseDown(e, node)}
              className="glass-panel"
              style={{
                position: 'absolute',
                left: `${pos.x}px`,
                top: `${pos.y}px`,
                width: `${node.width || 250}px`,
                minHeight: `${node.height || 140}px`,
                cursor: draggingNodeId === node.node_id ? 'grabbing' : 'grab',
                border: isSelected ? '2px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                boxShadow: isSelected ? '0 0 24px rgba(56, 189, 248, 0.25)' : '0 4px 20px rgba(0, 0, 0, 0.35)',
                transition: draggingNodeId === node.node_id ? 'none' : 'box-shadow 0.2s ease',
                zIndex: isSelected ? 15 : 10
              }}
            >
              {/* Input Handle (Left) */}
              <div
                onClick={(e) => handlePortClick(e, node.node_id, false)}
                title="Input Handle"
                style={{
                  position: 'absolute',
                  left: '-8px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '14px',
                  height: '14px',
                  borderRadius: '50%',
                  backgroundColor: '#38bdf8',
                  border: '2px solid #0f172a',
                  cursor: 'pointer',
                  zIndex: 20
                }}
              />

              {/* Output Handle (Right) */}
              <div
                onClick={(e) => handlePortClick(e, node.node_id, true)}
                title="Output Handle (Click to Wire)"
                style={{
                  position: 'absolute',
                  right: '-8px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '14px',
                  height: '14px',
                  borderRadius: '50%',
                  backgroundColor: wiringSourceId === node.node_id ? '#f59e0b' : '#10b981',
                  border: '2px solid #0f172a',
                  cursor: 'pointer',
                  zIndex: 20
                }}
              />

              {/* Card Header */}
              <div style={{
                padding: '10px 14px',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'rgba(255, 255, 255, 0.02)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '1rem' }}>{typeStyle.icon}</span>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    color: typeStyle.border
                  }}>
                    {node.node_type}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span
                    title={`Status: ${node.execution_status}`}
                    style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: node.execution_status === 'success' ? '#10b981' :
                                       node.execution_status === 'running' ? '#38bdf8' :
                                       node.execution_status === 'error' ? '#f43f5e' : '#64748b'
                    }}
                  />
                  {isSelected && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteNode(node.node_id);
                      }}
                      title="Delete Node"
                      style={{
                        background: 'transparent',
                        color: 'var(--accent-rose)',
                        fontSize: '0.8rem',
                        padding: '2px'
                      }}
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>

              {/* Card Body */}
              <div style={{ padding: '12px 14px' }}>
                <h4 style={{
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  marginBottom: '8px',
                  color: 'var(--text-main)'
                }}>
                  {node.label}
                </h4>

                {/* Node Metadata Parameters */}
                {node.data && (
                  <div style={{
                    fontSize: '0.75rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-muted)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px'
                  }}>
                    {Object.entries(node.data).slice(0, 3).map(([key, val]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: 'var(--text-dim)' }}>{key}:</span>
                        <span style={{ color: 'var(--text-main)', maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {String(val)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
