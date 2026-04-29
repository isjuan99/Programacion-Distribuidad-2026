import { useMemo, useState } from "react";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { apiCrearOrden } from "../api/api";
import { getEmoji } from "../components/PerfumeCard";

const formatCOP = (value) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(Number(value) || 0);

export default function CheckoutPage({ push, setPage }) {
  const { items, total, clearCart } = useCart();
  const { token } = useAuth();
  const [done, setDone] = useState(false);
  const [orderNum, setOrderNum] = useState("");
  const [loading, setLoading] = useState(false);
  const [processStep, setProcessStep] = useState(0);
  const [direccion, setDireccion] = useState("Bogotá · Calle 80 #10-20");
  const [metodoPago, setMetodoPago] = useState("PSE");
  const [telefono, setTelefono] = useState("3001234567");
  const [notas, setNotas] = useState("");

  const subtotal = total;
  const envio = useMemo(() => (subtotal >= 200000 ? 0 : 12000), [subtotal]);
  const servicio = useMemo(() => Math.round(subtotal * 0.02), [subtotal]);
  const totalFinal = subtotal + envio + servicio;

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const confirmar = async () => {
    if (!items.length || !direccion.trim() || !telefono.trim()) return;
    setLoading(true);
    setProcessStep(1);
    await sleep(600);
    setProcessStep(2);
    await sleep(700);
    setProcessStep(3);
    await sleep(700);
    try {
      const payload = {
        items: items.map(i => ({ perfume_id: i.id, cantidad: i.qty, precio_unit: i.precio })),
        total: totalFinal,
        direccion,
        metodo_pago: metodoPago,
        telefono,
        notas,
      };
      const data = await apiCrearOrden(payload, token);
      setOrderNum(`ORD-${data.orden_id}`);
    } catch (error) {
      setLoading(false);
      setProcessStep(0);
      push(error?.message || "No se pudo registrar la orden", "err");
      return;
    }
    setProcessStep(4);
    await sleep(450);
    clearCart();
    setDone(true);
    setLoading(false);
    push("¡Orden confirmada exitosamente!");
  };

  const s = {
    page: { padding: "44px 32px 64px", maxWidth: 1120, margin: "0 auto", minHeight: "90vh" },
    layout: { display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 24, alignItems: "start" },
    h2:   { fontFamily: "'Playfair Display', serif", fontSize: 38, color: "#E8D5A3" },
    sub:  { fontSize: 14, color: "#7A6E64", marginTop: 8, marginBottom: 28 },
    card: { background: "#1A1512", border: "1px solid #3D3428", borderRadius: 16, overflow: "hidden" },
    sectionPad: { padding: "18px 22px" },
    summary: { background: "#1E1914", border: "1px solid #3D3428", borderRadius: 16, overflow: "hidden", marginBottom: 18 },
    sHead: { padding: "14px 22px", borderBottom: "1px solid #2E2820", fontSize: 10, fontWeight: 600, color: "#5A504A", letterSpacing: ".12em", textTransform: "uppercase" },
    row:  { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "13px 22px", borderBottom: "1px solid #2E2820" },
    name: { fontFamily: "'Playfair Display', serif", fontSize: 14, color: "#E8E0D5" },
    rsub: { fontSize: 11, color: "#5A504A", marginTop: 2 },
    rval: { fontFamily: "'Playfair Display', serif", fontSize: 15, color: "#E8D5A3" },
    totalRow: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "18px 22px", background: "rgba(201,168,76,.05)", borderBottom: "1px solid #2E2820" },
    totalLabel: { fontSize: 13, color: "#7A6E64" },
    totalVal:   { fontFamily: "'Playfair Display', serif", fontSize: 26, color: "#C9A84C" },
    btnGold: { width: "100%", background: "#C9A84C", color: "#1A1410", border: "none", borderRadius: 10, padding: 14, fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: "'Jost', sans-serif", marginBottom: 10 },
    btnGhost: { width: "100%", background: "transparent", color: "#7A6E64", border: "1px solid #2E2820", borderRadius: 10, padding: 12, fontSize: 13, cursor: "pointer", fontFamily: "'Jost', sans-serif" },
    success: { minHeight: "80vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 20, textAlign: "center", padding: 40 },
    checkCircle: { width: 78, height: 78, borderRadius: "50%", background: "rgba(201,168,76,.12)", border: "2px solid #C9A84C", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 30 },
    ordNum: { background: "#1E1914", border: "1px solid #3D3428", borderRadius: 10, padding: "10px 24px", fontSize: 12, color: "#7A6E64" },
    fieldWrap: { display: "flex", flexDirection: "column", gap: 6, marginBottom: 14 },
    label: { fontSize: 11, fontWeight: 600, color: "#7A6E64", letterSpacing: ".1em", textTransform: "uppercase" },
    input: { width: "100%", border: "1px solid #3D3428", borderRadius: 8, background: "#120F0D", color: "#E8E0D5", padding: "11px 12px", fontSize: 13, fontFamily: "'Jost', sans-serif" },
    processRow: { display: "flex", alignItems: "center", gap: 10, padding: "8px 0", fontSize: 13 },
    dot: (active) => ({ width: 9, height: 9, borderRadius: "50%", background: active ? "#C9A84C" : "#3D3428" }),
  };

  if (done) return (
    <div style={{ ...s.page, maxWidth: "100%" }}>
      <div style={s.success}>
        <div style={s.checkCircle}>✓</div>
        <h2 style={s.h2}>¡Orden confirmada!</h2>
        <p style={{ fontSize: 14, color: "#7A6E64", maxWidth: 460 }}>
          Tu pedido fue registrado y quedó en proceso logístico. Te notificaremos cuando pase a despacho.
        </p>
        <div style={s.ordNum}>Número de orden: <strong style={{ color: "#C9A84C" }}>{orderNum}</strong></div>
        <div style={{ width: 280 }}>
          <button style={{ ...s.btnGold, marginTop: 8 }} onClick={() => setPage("misOrdenes")}>Ver seguimiento</button>
          <button style={s.btnGhost} onClick={() => setPage("catalogo")}>Seguir comprando</button>
        </div>
      </div>
    </div>
  );

  if (!items.length) return (
    <div style={{ ...s.page, maxWidth: "100%" }}>
      <div style={s.success}>
        <span style={{ fontSize: 48 }}>🛍️</span>
        <h2 style={s.h2}>Carrito vacío</h2>
        <p style={{ fontSize: 14, color: "#7A6E64" }}>Agrega productos antes de continuar.</p>
        <button style={{ ...s.btnGold, width: 220 }} onClick={() => setPage("catalogo")}>Ver catálogo</button>
      </div>
    </div>
  );

  return (
    <div style={s.page}>
      <h2 style={s.h2}>Resumen de orden</h2>
      <p style={s.sub}>Confirma datos de entrega y revisa el total antes de procesar tu compra.</p>

      <div style={s.layout}>
        <div>
          <div style={s.card}>
            <div style={s.sHead}>Datos de entrega y pago</div>
            <div style={s.sectionPad}>
              <div style={s.fieldWrap}>
                <label style={s.label}>Dirección de entrega</label>
                <input style={s.input} value={direccion} onChange={(e) => setDireccion(e.target.value)} />
              </div>
              <div style={s.fieldWrap}>
                <label style={s.label}>Teléfono de contacto</label>
                <input style={s.input} value={telefono} onChange={(e) => setTelefono(e.target.value)} />
              </div>
              <div style={s.fieldWrap}>
                <label style={s.label}>Método de pago</label>
                <select style={s.input} value={metodoPago} onChange={(e) => setMetodoPago(e.target.value)}>
                  <option value="PSE">PSE</option>
                  <option value="Tarjeta débito/crédito">Tarjeta débito/crédito</option>
                  <option value="Contraentrega">Contraentrega</option>
                </select>
              </div>
              <div style={s.fieldWrap}>
                <label style={s.label}>Notas para el envío (opcional)</label>
                <textarea style={{ ...s.input, minHeight: 86, resize: "vertical" }} value={notas} onChange={(e) => setNotas(e.target.value)} />
              </div>
            </div>
          </div>

          {loading && (
            <div style={{ ...s.card, marginTop: 14 }}>
              <div style={s.sHead}>Procesando orden</div>
              <div style={s.sectionPad}>
                {[
                  "Validando inventario",
                  "Autorizando pago",
                  "Creando orden",
                  "Confirmación final",
                ].map((label, idx) => (
                  <div key={label} style={s.processRow}>
                    <span style={s.dot(processStep > idx)} />
                    <span style={{ color: processStep > idx ? "#E8E0D5" : "#7A6E64" }}>{label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div style={s.summary}>
          <div style={s.sHead}>Productos ({items.length})</div>
          {items.map(item => (
            <div key={item.id} style={s.row}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span style={{ fontSize: 22, width: 42, height: 42, display: "inline-flex", alignItems: "center", justifyContent: "center", borderRadius: 8, overflow: "hidden", background: "#0E0B08" }}>
                  {item.imagen ? (
                    <img src={item.imagen} alt={item.nombre} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  ) : (
                    getEmoji(item.id)
                  )}
                </span>
                <div>
                  <div style={s.name}>{item.nombre}</div>
                  <div style={s.rsub}>{item.marca} · {item.qty} × {formatCOP(item.precio)}</div>
                </div>
              </div>
              <div style={s.rval}>{formatCOP(item.precio * item.qty)}</div>
            </div>
          ))}
          <div style={s.row}>
            <span style={s.totalLabel}>Subtotal</span>
            <span style={s.rval}>{formatCOP(subtotal)}</span>
          </div>
          <div style={s.row}>
            <span style={s.totalLabel}>Envío</span>
            <span style={s.rval}>{envio === 0 ? "Gratis" : formatCOP(envio)}</span>
          </div>
          <div style={s.row}>
            <span style={s.totalLabel}>Servicio</span>
            <span style={s.rval}>{formatCOP(servicio)}</span>
          </div>
          <div style={s.totalRow}>
            <span style={s.totalLabel}>Total a pagar</span>
            <span style={s.totalVal}>{formatCOP(totalFinal)}</span>
          </div>
          <div style={s.sectionPad}>
            <button style={{ ...s.btnGold, opacity: loading ? .6 : 1 }} onClick={confirmar} disabled={loading}>
              {loading ? "Procesando…" : `Confirmar orden · ${formatCOP(totalFinal)}`}
            </button>
            <button style={s.btnGhost} onClick={() => setPage("catalogo")}>Volver al catálogo</button>
          </div>
        </div>
      </div>
    </div>
  );
}
