import React from "react";

function StatusDot({ ready, error }) {
  const color = ready ? "var(--teal)" : error ? "var(--coral)" : "var(--amber)";
  return (
    <span
      className="status-dot"
      style={{ background: color, boxShadow: `0 0 8px ${color}` }}
    />
  );
}

export default function Sidebar({ health, onClear, messageCount }) {
  const ready = health?.ready;
  const sources = health?.source_files || [];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">
          <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
            <path
              d="M11 2v6M11 14v6M2 11h6M14 11h6"
              stroke="var(--teal)"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <circle cx="11" cy="11" r="3.2" stroke="var(--teal)" strokeWidth="1.6" />
          </svg>
        </div>
        <div>
          <div className="brand-title">Medical RAG</div>
          <div className="brand-subtitle">Clinical retrieval assistant</div>
        </div>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-label">System status</div>
        <div className="status-row">
          <StatusDot ready={ready} error={health?.error && !ready} />
          <span className="status-text">
            {ready
              ? "Pipeline ready"
              : health?.error
                ? "Attention needed"
                : "Initializing…"}
          </span>
        </div>
        {health?.error && <div className="status-detail">{health.error}</div>}
      </div>

      <div className="sidebar-section grow">
        <div className="sidebar-label">
          Knowledge base
          <span className="sidebar-count">{sources.length}</span>
        </div>
        <ul className="source-list">
          {sources.map((s) => (
            <li key={s} className="source-item" title={s}>
              <span className="source-dot" />
              <span className="source-name">{s}</span>
            </li>
          ))}
          {sources.length === 0 && (
            <li className="source-item source-item-empty">No documents loaded</li>
          )}
        </ul>
      </div>

      <div className="sidebar-section">
        <button
          className="btn-ghost"
          onClick={onClear}
          disabled={messageCount === 0}
        >
          Clear conversation
        </button>
      </div>
    </aside>
  );
}
