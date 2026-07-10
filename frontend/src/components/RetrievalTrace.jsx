import React from "react";

function TraceNode({ chunk, index, total }) {
  const delay = `${index * 90}ms`;
  return (
    <div className="trace-node" style={{ animationDelay: delay }}>
      <div className="trace-node-line">
        <span className="trace-node-dot" />
        {index < total - 1 && <span className="trace-node-connector" />}
      </div>
      <div className="trace-node-body">
        <div className="trace-node-source">{chunk.source}</div>
        {chunk.metadata?.medical_specialty && (
          <div className="trace-node-tag">{chunk.metadata.medical_specialty}</div>
        )}
        <div className="trace-node-snippet">{chunk.snippet}…</div>
      </div>
    </div>
  );
}

export default function RetrievalTrace({
  latestMessage,
  onEvaluate,
  evalLoading,
  evalResult,
  evalError,
}) {
  const sources = latestMessage?.sources || [];
  const hasResult = latestMessage && !latestMessage.error;
  const isGeneral = latestMessage?.mode === "general";

  return (
    <aside className="trace-panel">
      <div className="trace-header">
        <div className="trace-title">Retrieval trace</div>
        <div className="trace-subtitle">
          {isGeneral
            ? `No relevant chunks · ${latestMessage.latency}ms`
            : sources.length > 0
              ? `${sources.length} chunk${sources.length > 1 ? "s" : ""} · ${latestMessage.latency}ms`
              : "Waiting for a query"}
        </div>
      </div>

      <div className="trace-body">
        {isGeneral && (
          <div className="trace-general">
            <span className="trace-general-dot" />
            <div>
              <div className="trace-general-title">No relevant documents found</div>
              <div className="trace-general-sub">
                The retrieved chunks weren't relevant to this question, so the
                model answered from its own general medical knowledge instead
                of your indexed documents.
              </div>
            </div>
          </div>
        )}
        {!isGeneral && sources.length === 0 && (
          <div className="trace-empty">
            Send a question and the semantic search path will render here —
            each retrieved chunk lights up in order of relevance.
          </div>
        )}
        {!isGeneral &&
          sources.map((chunk, i) => (
            <TraceNode key={i} chunk={chunk} index={i} total={sources.length} />
          ))}
      </div>

      <div className="trace-footer">
        <button
          className="btn-secondary"
          onClick={onEvaluate}
          disabled={!hasResult || evalLoading}
        >
          {evalLoading ? "Evaluating…" : "Evaluate this response"}
        </button>

        {evalError && <div className="eval-error">{evalError}</div>}

        {evalResult && (
          <div className="eval-result">
            <div className="eval-result-label">Evaluation</div>
            <div className="eval-result-text">{evalResult}</div>
          </div>
        )}
      </div>
    </aside>
  );
}
