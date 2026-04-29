import { useState, useCallback } from "react";

export function useToast() {
  const [toasts, setToasts] = useState([]);

  const push = useCallback((msg, type = "ok") => {
    const id = Date.now();
    setToasts(t => [...t, { id, msg, type }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3200);
  }, []);

  return { push, toasts };
}

export function ToastContainer({ toasts }) {
  return (
    <div style={{
      position: "fixed", bottom: 28, right: 28,
      display: "flex", flexDirection: "column", gap: 10, zIndex: 9999,
    }}>
      {toasts.map(t => (
        <div key={t.id} style={{
          padding: "12px 18px", borderRadius: 10,
          fontSize: 13, fontWeight: 500,
          display: "flex", alignItems: "center", gap: 10,
          maxWidth: 320,
          background: t.type === "ok" ? "#1E1914" : "rgba(196,123,116,.22)",
          border:     t.type === "ok" ? "1px solid #3D3428" : "1px solid rgba(196,123,116,.45)",
          color:      t.type === "ok" ? "#E8D5A3" : "#F0DDD9",
          boxShadow: "0 4px 20px rgba(0,0,0,.45)",
          animation: "toastIn .2s ease",
        }}>
          <span>{t.type === "ok" ? "✓" : "✕"}</span>
          {t.msg}
        </div>
      ))}
    </div>
  );
}
