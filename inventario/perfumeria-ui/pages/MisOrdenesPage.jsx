import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { apiMisOrdenes, apiOrdenDetalle } from "../api/api";

const formatCOP = (value) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(Number(value) || 0);

export default function MisOrdenesPage() {
  const { token }                     = useAuth();
  const [ordenes, setOrdenes]         = useState([]);
  const [loading, setLoading]         = useState(true);
  const [detalle, setDetalle]         = useState(null);
  const [detalleLoading, setDetalleLoading] = useState(false);
  const [detalleError, setDetalleError] = useState("");

  useEffect(() => {
    if (!token) {
      setOrdenes([]);
      setLoading(false);
      return;
    }
    apiMisOrdenes(token)
      .then(setOrdenes)
      .catch(() => setOrdenes([]))
      .finally(() => setLoading(false));
  }, [token]);

  const estadoStyle = (e) => ({
    confirmada: { bg: "rgba(201,168,76,.12)",  color: "#C9A84C", border: "rgba(201,168,76,.3)"  },
    entregada:  { bg: "rgba(122,140,110,.12)", color: "#7A8C6E", border: "rgba(122,140,110,.3)" },
    pendiente:  { bg: "rgba(196,123,116,.12)", color: "#C47B74", border: "rgba(196,123,116,.3)" },
  }[e] || { bg: "#1E1914", color: "#7A6E64", border: "#3D3428" });

  const s = {
    page:   { padding: "40px", minHeight: "90vh" },
    h2:     { fontFamily: "'Playfair Display', serif", fontSize: 30, color: "#E8D5A3", marginBottom: 6 },
    sub:    { fontSize: 13, color: "#7A6E64", marginBottom: 32 },
    list:   { display: "flex", flexDirection: "column", gap: 14, maxWidth: 640 },
    card:   { background: "#1E1914", border: "1px solid #3D3428", borderRadius: 13, padding: "18px 22px", display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer" },
    num:    { fontFamily: "'Playfair Display', serif", fontSize: 17, color: "#E8D5A3" },
    date:   { fontSize: 12, color: "#5A504A", marginTop: 4 },
    total:  { fontFamily: "'Playfair Display', serif", fontSize: 22, color: "#C9A84C" },
    empty:  { textAlign: "center", padding: "80px 20px", color: "#5A504A" },
    spinner:{ width: 28, height: 28, borderRadius: "50%", border: "2px solid #2E2820", borderTopColor: "#C9A84C", animation: "spin .7s linear infinite", margin: "80px auto" },
    overlay: { position: "fixed", inset: 0, background: "rgba(0,0,0,.72)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 200, padding: 20 },
    modal: { width: "min(760px, 100%)", maxHeight: "86vh", overflowY: "auto", background: "#1A1512", border: "1px solid #3D3428", borderRadius: 16 },
    modalHead: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "18px 22px", borderBottom: "1px solid #2E2820" },
    closeBtn: { background: "none", border: "none", color: "#7A6E64", cursor: "pointer", fontSize: 18 },
    modalBody: { padding: "18px 22px" },
    detailGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 },
    detailItem: { background: "#14100D", border: "1px solid #2E2820", borderRadius: 10, padding: "10px 12px" },
    detailLabel: { fontSize: 10, color: "#7A6E64", textTransform: "uppercase", letterSpacing: ".08em" },
    detailVal: { fontSize: 13, color: "#E8E0D5", marginTop: 4 },
    itemRow: { display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, padding: "12px 0", borderBottom: "1px solid #2E2820" },
    itemTitle: { color: "#E8D5A3", fontFamily: "'Playfair Display', serif", fontSize: 16 },
    itemSub: { color: "#7A6E64", fontSize: 12, marginTop: 2 },
  };

  const abrirDetalle = async (ordenId) => {
    if (!token) return;
    setDetalle(null);
    setDetalleError("");
    setDetalleLoading(true);
    try {
      const data = await apiOrdenDetalle(ordenId, token);
      setDetalle(data);
    } catch (error) {
      setDetalleError(error?.message || "No se pudo cargar el detalle");
    } finally {
      setDetalleLoading(false);
    }
  };

  const pill = (estado) => {
    const c = estadoStyle(estado);
    return { display: "inline-block", padding: "3px 12px", borderRadius: 20, fontSize: 10, fontWeight: 600, letterSpacing: ".08em", textTransform: "uppercase", background: c.bg, color: c.color, border: `1px solid ${c.border}`, marginTop: 8 };
  };

  return (
    <div style={s.page}>
      <style>{"@keyframes spin{to{transform:rotate(360deg)}}"}</style>
      <h2 style={s.h2}>Mis órdenes</h2>
      <p style={s.sub}>Historial de compras realizadas</p>

      {loading ? <div style={s.spinner}/> :
       ordenes.length === 0 ? (
        <div style={s.empty}>
          <div style={{ fontSize: 44, marginBottom: 14 }}>📦</div>
          <p style={{ fontSize: 14 }}>Aún no has realizado ninguna orden.</p>
        </div>
       ) : (
        <div style={s.list}>
          {ordenes.map(o => (
            <div key={o.orden_id} style={s.card} onClick={() => abrirDetalle(o.orden_id)}>
              <div>
                <div style={s.num}>Orden #{o.orden_id}</div>
                <div style={s.date}>
                  {new Date(o.creado_en).toLocaleDateString("es-CO", { year: "numeric", month: "long", day: "numeric" })}
                </div>
                <div><span style={pill(o.estado)}>{o.estado}</span></div>
              </div>
              <div style={s.total}>{formatCOP(o.total)}</div>
            </div>
          ))}
        </div>
       )}

      {(detalleLoading || detalle || detalleError) && (
        <div style={s.overlay} onClick={(e) => e.target === e.currentTarget && (setDetalle(null), setDetalleError(""), setDetalleLoading(false))}>
          <div style={s.modal}>
            <div style={s.modalHead}>
              <h3 style={{ ...s.num, margin: 0 }}>Detalle de orden</h3>
              <button style={s.closeBtn} onClick={() => { setDetalle(null); setDetalleError(""); setDetalleLoading(false); }}>✕</button>
            </div>
            <div style={s.modalBody}>
              {detalleLoading && <div style={s.spinner} />}
              {detalleError && <p style={{ color: "#C47B74" }}>{detalleError}</p>}
              {detalle && (
                <>
                  <div style={s.detailGrid}>
                    <div style={s.detailItem}>
                      <div style={s.detailLabel}>Orden</div>
                      <div style={s.detailVal}>#{detalle.orden?.orden_id}</div>
                    </div>
                    <div style={s.detailItem}>
                      <div style={s.detailLabel}>Estado</div>
                      <div style={s.detailVal}>{detalle.orden?.estado}</div>
                    </div>
                    <div style={s.detailItem}>
                      <div style={s.detailLabel}>Fecha</div>
                      <div style={s.detailVal}>{new Date(detalle.orden?.creado_en).toLocaleString("es-CO")}</div>
                    </div>
                    <div style={s.detailItem}>
                      <div style={s.detailLabel}>Total</div>
                      <div style={s.detailVal}>{formatCOP(detalle.orden?.total)}</div>
                    </div>
                    <div style={s.detailItem}>
                      <div style={s.detailLabel}>Pago</div>
                      <div style={s.detailVal}>{detalle.orden?.metodo_pago || "No especificado"}</div>
                    </div>
                    <div style={s.detailItem}>
                      <div style={s.detailLabel}>Teléfono</div>
                      <div style={s.detailVal}>{detalle.orden?.telefono || "No especificado"}</div>
                    </div>
                  </div>
                  <div style={{ ...s.detailItem, marginBottom: 14 }}>
                    <div style={s.detailLabel}>Dirección</div>
                    <div style={s.detailVal}>{detalle.orden?.direccion || "No especificada"}</div>
                  </div>
                  <div style={{ ...s.detailItem, marginBottom: 14 }}>
                    <div style={s.detailLabel}>Notas</div>
                    <div style={s.detailVal}>{detalle.orden?.notas || "Sin notas"}</div>
                  </div>
                  {(detalle.items || []).map((item) => (
                    <div key={item.item_id} style={s.itemRow}>
                      <div>
                        <div style={s.itemTitle}>{item.perfume_nombre || `Perfume #${item.perfume_id}`}</div>
                        <div style={s.itemSub}>
                          {item.perfume_marca || "Sin marca"} · {item.cantidad} x {formatCOP(item.precio_unit)}
                        </div>
                      </div>
                      <div style={s.total}>{formatCOP(item.subtotal)}</div>
                    </div>
                  ))}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
