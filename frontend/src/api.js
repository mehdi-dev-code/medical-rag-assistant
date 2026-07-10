const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore parse failure */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  health: () => request("/health"),
  documents: () => request("/documents"),
  query: (query) =>
    request("/query", { method: "POST", body: JSON.stringify({ query }) }),
  history: () => request("/history"),
  clearHistory: () => request("/history", { method: "DELETE" }),
  evaluate: (query, response) =>
    request("/eval", { method: "POST", body: JSON.stringify({ query, response }) }),
};
