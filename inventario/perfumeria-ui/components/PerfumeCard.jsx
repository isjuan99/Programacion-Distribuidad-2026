import { useState } from "react";

const EMOJIS = ["🌹","🌺","🌸","🌼","✨","🪷","💐","🌿","🫧","🕯️","🌙","⭐"];
export const getEmoji = (id) => EMOJIS[Number(id) % EMOJIS.length];
const formatCOP = (value) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(Number(value) || 0);

export default function PerfumeCard({ perfume, onAdd, onSelect }) {
  const { id, nombre, marca, precio, stock, imagen, image, imageUrl, image_url, foto } = perfume;
  const sinStock = stock === 0;
  const imageSrc = imagen || image || imageUrl || image_url || foto;
  const [imageFailed, setImageFailed] = useState(false);

  return (
    <div style={{
      background: "#1E1914", border: "1px solid #2E2820",
      borderRadius: 16, overflow: "hidden",
      display: "flex", flexDirection: "column",
      minHeight: 420,
      transition: "border-color .2s, transform .2s",
    }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = "#3D3428";
        e.currentTarget.style.transform   = "translateY(-3px)";
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = "#2E2820";
        e.currentTarget.style.transform   = "none";
      }}
    >
      {/* Imagen */}
      <div style={{
        height: 210, fontSize: 50,
        background: "linear-gradient(135deg,#1A1614 0%,#2A2118 60%,#1E1914 100%)",
        display: "flex", alignItems: "center", justifyContent: "center",
        borderBottom: "1px solid #2E2820", position: "relative",
      }}>
        {imageSrc && !imageFailed ? (
          <img
            src={imageSrc}
            alt={nombre}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            onError={() => setImageFailed(true)}
          />
        ) : (
          getEmoji(id)
        )}
        {sinStock && (
          <span style={{
            position: "absolute", top: 10, right: 10,
            background: "rgba(196,123,116,.2)",
            border: "1px solid rgba(196,123,116,.4)",
            borderRadius: 20, padding: "2px 10px",
            fontSize: 10, fontWeight: 600, color: "#C47B74",
          }}>Sin stock</span>
        )}
      </div>

      {/* Info */}
      <div style={{ padding: "18px 18px 16px", flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
        <div style={{
          fontSize: 10, fontWeight: 600, color: "#C9A84C",
          letterSpacing: ".15em", textTransform: "uppercase",
        }}>{marca}</div>

        <div style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: 19, color: "#E8E0D5", lineHeight: 1.2, minHeight: 46,
        }}>{nombre}</div>

        <div style={{ fontSize: 11, color: "#5A504A", marginBottom: 12, flex: 1 }}>
          {sinStock ? "Agotado temporalmente" : `${stock} unidades disponibles`}
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{
            fontFamily: "'Playfair Display', serif",
            fontSize: 21, color: "#E8D5A3",
          }}>{formatCOP(precio)}</span>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
            <button
              onClick={() => onSelect && onSelect(perfume)}
              style={{
                background: "transparent",
                color: "#C9A84C",
                border: "1px solid #3D3428",
                borderRadius: 8,
                padding: "7px 10px",
                fontSize: 12,
                fontWeight: 600,
                cursor: "pointer",
                fontFamily: "'Jost', sans-serif",
              }}
            >
              Ver
            </button>
            <button
              disabled={sinStock}
              onClick={() => !sinStock && onAdd && onAdd(perfume)}
              style={{
                background: sinStock ? "transparent" : "#C9A84C",
                color:       sinStock ? "#5A504A" : "#1A1410",
                border:      sinStock ? "1px solid #3D3428" : "none",
                borderRadius: 8, padding: "7px 12px",
                fontSize: 12, fontWeight: 600,
                cursor: sinStock ? "not-allowed" : "pointer",
                fontFamily: "'Jost', sans-serif",
              }}
            >{sinStock ? "Agotado" : "+ Agregar"}</button>
          </div>
        </div>
      </div>
    </div>
  );
}
