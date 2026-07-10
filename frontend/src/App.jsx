import React, { useEffect, useRef, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import ChatThread from "./components/ChatThread.jsx";
import ChatInput from "./components/ChatInput.jsx";
import RetrievalTrace from "./components/RetrievalTrace.jsx";
import { api } from "./api.js";

let idCounter = 0;
const nextId = () => `m-${++idCounter}-${Date.now()}`;

export default function App() {
  const [health, setHealth] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [evalLoading, setEvalLoading] = useState(false);
  const [evalResult, setEvalResult] = useState(null);
  const [evalError, setEvalError] = useState(null);
  const pollRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    const check = async () => {
      try {
        const h = await api.health();
        if (cancelled) return;
        setHealth(h);
        if (h.ready && pollRef.current) {
          clearInterval(pollRef.current);
          pollRef.current = null;
        }
      } catch {
        if (!cancelled) {
          setHealth({ ready: false, error: "Cannot reach backend at :8000", source_files: [] });
        }
      }
    };

    check();
    pollRef.current = setInterval(check, 3000);
    return () => {
      cancelled = true;
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const latestAssistant = [...messages].reverse().find((m) => m.role === "assistant");

  const handleSend = async (text) => {
    const userMsg = { id: nextId(), role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setEvalResult(null);
    setEvalError(null);

    try {
      const result = await api.query(text);
      const assistantMsg = {
        id: nextId(),
        role: "assistant",
        text: result.response,
        sources: result.sources,
        latency: result.latency_ms,
        mode: result.mode,
        query: text,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: "assistant", error: true, text: e.message },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    setMessages([]);
    setEvalResult(null);
    setEvalError(null);
    try {
      await api.clearHistory();
    } catch {
      /* non-fatal */
    }
  };

  const handleEvaluate = async () => {
    if (!latestAssistant) return;
    setEvalLoading(true);
    setEvalError(null);
    setEvalResult(null);
    try {
      const res = await api.evaluate(latestAssistant.query, latestAssistant.text);
      setEvalResult(res.evaluation);
    } catch (e) {
      setEvalError(e.message);
    } finally {
      setEvalLoading(false);
    }
  };

  const notReady = !health?.ready;

  return (
    <div className="app-shell">
      <Sidebar health={health} onClear={handleClear} messageCount={messages.length} />

      <main className="chat-panel">
        <ChatThread messages={messages} loading={loading} />
        <ChatInput onSend={handleSend} disabled={loading || notReady} notReady={notReady} />
      </main>

      <RetrievalTrace
        latestMessage={latestAssistant}
        onEvaluate={handleEvaluate}
        evalLoading={evalLoading}
        evalResult={evalResult}
        evalError={evalError}
      />
    </div>
  );
}
