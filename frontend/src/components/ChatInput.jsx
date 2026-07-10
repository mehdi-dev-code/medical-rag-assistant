import React, { useState, useRef } from "react";

export default function ChatInput({ onSend, disabled, notReady }) {
  const [value, setValue] = useState("");
  const taRef = useRef(null);

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    if (taRef.current) taRef.current.style.height = "auto";
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const autoGrow = (e) => {
    setValue(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
  };

  return (
    <div className="chat-input-bar">
      <div className="chat-input-shell">
        <textarea
          ref={taRef}
          className="chat-input"
          placeholder={
            notReady ? "Waiting for pipeline to finish initializing…" : "Ask a medical question…"
          }
          rows={1}
          value={value}
          onChange={autoGrow}
          onKeyDown={onKeyDown}
          disabled={disabled}
        />
        <button
          className="btn-send"
          onClick={submit}
          disabled={disabled || !value.trim()}
          aria-label="Send question"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M2 8h11M8 2l6 6-6 6"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
      <div className="chat-input-hint">
        Not a substitute for professional medical advice.
      </div>
    </div>
  );
}
