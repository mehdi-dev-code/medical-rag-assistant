import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="msg-row msg-row-user">
        <div className="msg-bubble msg-bubble-user">{message.text}</div>
      </div>
    );
  }

  if (message.error) {
    return (
      <div className="msg-row msg-row-assistant">
        <div className="msg-bubble msg-bubble-error">
          <span className="msg-error-label">Request failed</span>
          {message.text}
        </div>
      </div>
    );
  }

  return (
    <div className="msg-row msg-row-assistant">
      <div className="msg-bubble msg-bubble-assistant">
        <div className="msg-text msg-markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
        </div>
        {message.mode === "general" ? (
          <div className="msg-general-badge">
            <span className="msg-general-dot" />
            General medical knowledge — not from your documents
          </div>
        ) : (
          message.sources?.length > 0 && (
            <div className="msg-sources">
              {message.sources.map((s, i) => (
                <span className="msg-source-chip" key={i}>
                  {s.source}
                </span>
              ))}
            </div>
          )
        )}
        {typeof message.latency === "number" && (
          <div className="msg-latency">{message.latency}ms · {message.sources?.length || 0} chunks retrieved</div>
        )}
      </div>
    </div>
  );
}
