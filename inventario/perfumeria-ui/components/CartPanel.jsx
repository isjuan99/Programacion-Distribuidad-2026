import { useCart } from "../context/CartContext";
import { getEmoji } from "./PerfumeCard";

const formatCOP = (value) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(Number(value) || 0);

export default function CartPanel({ onClose, onCheckout }) {
  const { items, removeItem, setQty, total, totalQty } = useCart();

  const s = {
    overlay: {
      position: "fixed", inset: 0,
      background: "rgba(0,0,0,.72)", zIndex: 200,
      display: "flex", justifyContent: "flex-end",
    },
    panel: {
      width: "100%", maxWidth: 420,
      background: "#161210",
      borderLeft: "1px solid #2E2820",
      display: "flex", flexDirection: "column",
      fontFamily: "'Jost', sans-serif",
    },
    head: {
      padding: "20px 26px",
      borderBottom: "1px solid #2E2820",
      display: "flex", alignItems: "center", justifyContent: "space-between",
    },
    title: { fontFamily: "'Playfair Display', serif", fontSize: 21, color: "#E8D5A3" },
    closeBtn: {
      background: "none", border: "none", cursor: "pointer",
      color: "#5A504A", fontSize: 20, lineHeight: 1,
    },
    body: {
      flex: 1, overflowY: "auto",
      padding: "18px 26px",
      display: "flex", flexDirection: "column", gap: 12,
    },
    item: {
      display: "flex", alignItems: "center", gap: 12,
      background: "#1E1914", border: "1px solid #2E2820",
      borderRadius: 12, padding: 12,
    },
    emoji: {
      fontSize: 26, width: 48, height: 48,
      background: "#0E0B08", borderRadius: 8,
      display: "flex", alignItems: "center", justifyContent: "center",
      flexShrink: 0,
      overflow: "hidden",
    },
    info: { flex: 1 },
    itemName:  { fontFamily: "'Playfair Display', serif", fontSize: 14, color: "#E8E0D5" },
    itemMarca: { fontSize: 11, color: "#5A504A", marginTop: 2 },
    itemPrice: { fontSize: 12, color: "#C9A84C", fontWeight: 500, marginTop: 2 },
    qtyRow:    { display: "flex", alignItems: "center", gap: 8, marginTop: 8 },
    qtyBtn: {
      width: 24, height: 24, borderRadius: 6,
      border: "1px solid #3D3428", background: "#161210",
      color: "#E8E0D5", cursor: "pointer", fontSize: 14,
      display: "flex", alignItems: "center", justifyContent: "center",
    },
    qtyNum: { fontSize: 14, fontWeight: 500, minWidth: 20, textAlign: "center" },
    removeBtn: {
      background: "none", border: "none", cursor: "pointer",
      color: "#5A504A", fontSize: 16, flexShrink: 0,
    },
    foot: {
      padding: "18px 26px",
      borderTop: "1px solid #2E2820",
      display: "flex", flexDirection: "column", gap: 10,
    },
    totalRow: { display: "flex", justifyContent: "space-between", alignItems: "center" },
    totalLabel: { fontSize: 13, color: "#7A6E64" },
    totalVal:   { fontFamily: "'Playfair Display', serif", fontSize: 26, color: "#E8D5A3" },
    btnGold: {
      background: "#C9A84C", color: "#1A1410", border: "none",
      borderRadius: 10, padding: "13px", fontSize: 14, fontWeight: 600,
      cursor: "pointer", fontFamily: "'Jost', sans-serif",
    },
    btnGhost: {
      background: "transparent", color: "#7A6E64",
      border: "1px solid #2E2820", borderRadius: 10,
      padding: "11px", fontSize: 13,
      cursor: "pointer", fontFamily: "'Jost', sans-serif",
    },
    empty: {
      flex: 1, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      gap: 14, color: "#5A504A", fontSize: 13,
    },
  };

  return (
    <div style={s.overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={s.panel}>
        <div style={s.head}>
          <h3 style={s.title}>Carrito · {totalQty}</h3>
          <button style={s.closeBtn} onClick={onClose}>✕</button>
        </div>

        {items.length === 0 ? (
          <div style={s.empty}>
            <span style={{ fontSize: 44 }}>🛍️</span>
            <span>Tu carrito está vacío</span>
          </div>
        ) : (
          <div style={s.body}>
            {items.map(item => (
              <div key={item.id} style={s.item}>
                <div style={s.emoji}>
                  {item.imagen ? (
                    <img
                      src={item.imagen}
                      alt={item.nombre}
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  ) : (
                    getEmoji(item.id)
                  )}
                </div>
                <div style={s.info}>
                  <div style={s.itemName}>{item.nombre}</div>
                  <div style={s.itemMarca}>{item.marca}</div>
                  <div style={s.itemPrice}>{formatCOP(item.precio * item.qty)}</div>
                  <div style={s.qtyRow}>
                    <button style={s.qtyBtn} onClick={() => setQty(item.id, item.qty - 1)}>−</button>
                    <span style={s.qtyNum}>{item.qty}</span>
                    <button style={s.qtyBtn} onClick={() => setQty(item.id, item.qty + 1)}>+</button>
                  </div>
                </div>
                <button style={s.removeBtn} onClick={() => removeItem(item.id)}>🗑</button>
              </div>
            ))}
          </div>
        )}

        {items.length > 0 && (
          <div style={s.foot}>
            <div style={s.totalRow}>
              <span style={s.totalLabel}>{totalQty} artículo{totalQty !== 1 ? "s" : ""}</span>
              <span style={s.totalVal}>{formatCOP(total)}</span>
            </div>
            <button style={s.btnGold} onClick={() => { onClose(); onCheckout(); }}>
              Proceder al pago
            </button>
            <button style={s.btnGhost} onClick={onClose}>Seguir comprando</button>
          </div>
        )}
      </div>
    </div>
  );
}
