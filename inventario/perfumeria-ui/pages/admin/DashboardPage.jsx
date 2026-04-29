/*import { useState, useEffect } from "react";
import { apiGetInventario } from "../../api/api";

export default function DashboardPage({ user }) {
  const [items, setItems]     = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGetInventario()
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  const totalStock = items.reduce((s, p) => s + (p.stock || 0), 0);
  const valorTotal = items.reduce((s, p) => s + (p.precio || 0) * (p.stock || 0), 0);
  const marcas     = [...new Set(items.map(p => p.marca))];

  const s = {
    page:    { padding: "40px", minHeight: "90vh" },
    h2:      { fontFamily: "'Playfair Display', serif", fontSize: 30, color: "#E8D5A3", marginBottom: 6 },
    sub:     { fontSize: 13, color: "#7A6E64", marginBottom: 32 },
    grid:    { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(210px,1fr))", gap: 18, marginBottom: 32 },
    card:    (accent) => ({ background: "#1E1914", border: "1px solid #3D3428", borderTop: `3px solid ${accent}`, borderRadius: 12, padding: "20px 24px" }),
    cLabel:  { fontSize: 10, fontWeight: 600, color: "#5A504A", letterSpacing: ".12em", textTransform: "uppercase", marginBottom: 10 },
    cVal:    { fontFamily: "'Playfair Display', serif", fontSize: 34, color: "#E8D5A3" },
    marcaCard: { background: "#1E1914", border: "1px solid #3D3428", borderRadius: 12, padding: "22px 26px" },
    marcaTitle:{ fontSize: 10, fontWeight: 600, color: "#5A504A", letterSpacing: ".12em", textTransform: "uppercase", marginBottom: 14 },
    marcaRow:  { display: "flex", flexWrap: "wrap", gap: 8 },
    marcaPill: { background: "rgba(201,168,76,.08)", border: "1px solid rgba(201,168,76,.2)", borderRadius: 20, padding: "4px 14px", fontSize: 12, color: "#C9A84C" },
    spinner:   { width: 28, height: 28, borderRadius: "50%", border: "2px solid #2E2820", borderTopColor: "#C9A84C", animation: "spin .7s linear infinite", margin: "60px auto" },
  };

  return (
    <div style={s.page}>
      <style>{"@keyframes spin{to{transform:rotate(360deg)}}"}</style>
      <h2 style={s.h2}>Hola, {user?.nombre || "Administrador"} 👋</h2>
      <p style={s.sub}>Panel de control · AromaDistribuido</p>

      {loading ? <div style={s.spinner}/> : (<>
        <div style={s.grid}>
          {[
            { label: "Productos",        val: items.length,                                        accent: "#C9A84C" },
            { label: "Stock total",      val: totalStock,                                           accent: "#7A8C6E" },
            { label: "Valor inventario", val: `$${valorTotal.toLocaleString("en-US", { maximumFractionDigits:0 })}`, accent: "#C47B74" },
            { label: "Marcas",           val: marcas.length,                                        accent: "#9A84C4" },
          ].map(({ label, val, accent }) => (
            <div key={label} style={s.card(accent)}>
              <div style={s.cLabel}>{label}</div>
              <div style={s.cVal}>{val}</div>
            </div>
          ))}
        </div>

        <div style={s.marcaCard}>
          <div style={s.marcaTitle}>Marcas disponibles</div>
          <div style={s.marcaRow}>
            {marcas.map(m => <span key={m} style={s.marcaPill}>{m}</span>)}
          </div>
        </div>
      </>)}
    </div>
  );
}
*/


// src/pages/admin/DashboardPage.jsx
import { useAuth } from "../../context/AuthContext";

export default function DashboardPage({ user, setPage }) {
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    // El useEffect en App.jsx redirigirá automáticamente a login
  };

  const styles = {
    container: {
      padding: "40px",
      maxWidth: "1200px",
      margin: "0 auto"
    },
    header: {
      marginBottom: "30px"
    },
    title: {
      fontSize: "28px",
      color: "#C9A84C",
      marginBottom: "10px"
    },
    welcome: {
      fontSize: "16px",
      color: "#7A6E64",
      marginBottom: "20px"
    },
    grid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
      gap: "20px",
      marginTop: "30px"
    },
    card: {
      background: "#1E1914",
      border: "1px solid #3D3428",
      borderRadius: "12px",
      padding: "24px",
      cursor: "pointer",
      transition: "transform 0.2s",
      textAlign: "center"
    },
    cardTitle: {
      fontSize: "18px",
      fontWeight: "600",
      color: "#C9A84C",
      marginBottom: "12px"
    },
    cardDesc: {
      fontSize: "14px",
      color: "#7A6E64"
    },
    logoutBtn: {
      background: "#2E2820",
      color: "#C9A84C",
      border: "1px solid #3D3428",
      padding: "10px 20px",
      borderRadius: "8px",
      cursor: "pointer",
      marginTop: "20px"
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Panel de Administrador</h1>
        <p style={styles.welcome}>Bienvenido, {user?.nombre}</p>
        <button style={styles.logoutBtn} onClick={handleLogout}>
          Cerrar Sesión
        </button>
      </div>

      <div style={styles.grid}>
        <div style={styles.card} onClick={() => setPage("adminPerfumes")}>
          <div style={styles.cardTitle}>📦 Gestionar Perfumes</div>
          <div style={styles.cardDesc}>Agregar, editar o eliminar perfumes del inventario</div>
        </div>
        
        <div style={styles.card} onClick={() => setPage("adminOrdenes")}>
          <div style={styles.cardTitle}>📋 Ver Órdenes</div>
          <div style={styles.cardDesc}>Revisar y gestionar las órdenes de los clientes</div>
        </div>
        
        <div style={styles.card} onClick={() => setPage("catalogo")}>
          <div style={styles.cardTitle}>🛍️ Ver Tienda</div>
          <div style={styles.cardDesc}>Visualizar la tienda como cliente</div>
        </div>
      </div>
    </div>
  );
}