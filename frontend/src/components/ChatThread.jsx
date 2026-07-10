import React, { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble.jsx";

export default function ChatThread({ messages, loading }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="chat-empty">
        <div className="chat-empty-mark">
          <svg width="40" height="40" viewBox="0 0 22 22" fill="none">
            <path
              d="M11 2v6M11 14v6M2 11h6M14 11h6"
              stroke="var(--teal-dim)"
              strokeWidth="1.6"
              strokeLinecap="round"
            />
            <circle cx="11" cy="11" r="3.2" stroke="var(--teal-dim)" strokeWidth="1.4" />
          </svg>
        </div>
        <div className="chat-empty-title">Ask a medical question</div>
        <div className="chat-empty-sub">
          Answers are grounded in your indexed documents. Retrieved evidence
          appears in the trace panel on the right.
        </div>
        <div className="chat-empty-suggestions">
          {[
            "What are the early symptoms of Type 2 diabetes?",
            "How is hypertension managed long-term?",
            "What precautions reduce COVID-19 transmission?",
          ].map((s) => (
            <div className="chat-suggestion" key={s}>
              {s}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="chat-thread">
      {messages.map((m) => (
        <MessageBubble key={m.id} message={m} />
      ))}
      {loading && (
        <div className="msg-row msg-row-assistant">
          <div className="msg-bubble msg-bubble-assistant msg-bubble-loading">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        </div>
      )}
      <div ref={endRef} />
    </div>
  );
}
