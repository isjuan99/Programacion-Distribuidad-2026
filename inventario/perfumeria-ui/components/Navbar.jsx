import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function Navbar({ page, setPage, onOpenCart }) {
  const { user, logout } = useAuth();
  const { totalQty }     = useCart();
  const isAdmin          = user?.rol === "admin";

  const s = {
    nav: {
      position: "sticky", top: 0, zIndex: 100,
      background: "rgba(14,11,8,.93)",
      backdropFilter: "blur(14px)",
      borderBottom: "1px solid #2E2820",
      display: "flex", alignItems: "center",
      justifyContent: "space-between",
      padding: "0 32px", height: 62,
      fontFamily: "'Jost', sans-serif",
    },
    logo: {
      fontFamily: "'Playfair Display', serif",
      fontSize: 19, color: "#E8D5A3",
      letterSpacing: ".04em", cursor: "pointer",
    },
    em: { fontStyle: "italic", color: "#C9A84C" },
    links: { display: "flex", alignItems: "center", gap: 4 },
    navBtn: (active) => ({
      background: "none", border: "none", cursor: "pointer",
      color: active ? "#C9A84C" : "#5A504A",
      fontSize: 13, fontWeight: 500,
      padding: "8px 14px", borderRadius: 6,
      fontFamily: "'Jost', sans-serif",
      transition: "color .15s",
    }),
    pill: {
      display: "flex", alignItems: "center", gap: 8,
      background: "rgba(201,168,76,.1)",
      border: "1px solid rgba(201,168,76,.2)",
      borderRadius: 20, padding: "5px 14px",
      fontSize: 12, color: "#E8D5A3",
    },
    adminBadge: {
      background: "rgba(201,168,76,.2)",
      border: "1px solid rgba(201,168,76,.4)",
      color: "#C9A84C", fontSize: 10, fontWeight: 600,
      letterSpacing: ".12em", textTransform: "uppercase",
      padding: "2px 8px", borderRadius: 20,
    },
    cartBtn: {
      display: "flex", alignItems: "center", gap: 8,
      background: "#1E1914", border: "1px solid #3D3428",
      borderRadius: 8, padding: "8px 16px", cursor: "pointer",
      color: "#E8E0D5", fontSize: 13, fontWeight: 500,
      fontFamily: "'Jost', sans-serif",
    },
    badge: {
      background: "#C9A84C", color: "#1A1410",
      borderRadius: "50%", width: 18, height: 18,
      fontSize: 10, fontWeight: 700,
      display: "flex", alignItems: "center", justifyContent: "center",
    },
    logoutBtn: {
      background: "none", border: "none", cursor: "pointer",
      color: "#5A504A", padding: "8px 12px",
      borderRadius: 6, fontSize: 13,
      fontFamily: "'Jost', sans-serif",
    },
    registerBtn: {
      background: "#C9A84C", color: "#1A1410",
      border: "none", borderRadius: 8,
      padding: "8px 18px", fontSize: 13, fontWeight: 600,
      cursor: "pointer", fontFamily: "'Jost', sans-serif",
    },
  };

  return (
    <nav style={s.nav}>
      {/* Logo */}
      <span style={s.logo}
        onClick={() => setPage(isAdmin ? "dashboard" : "catalogo")}>
        Aroma <em style={s.em}>Distribuido</em>
      </span>

      {/* Links centro */}
      <div style={s.links}>
        {isAdmin && <>
          <button style={s.navBtn(page === "dashboard")}     onClick={() => setPage("dashboard")}>Dashboard</button>
          <button style={s.navBtn(page === "adminPerfumes")} onClick={() => setPage("adminPerfumes")}>Perfumes</button>
          <button style={s.navBtn(page === "adminOrdenes")}  onClick={() => setPage("adminOrdenes")}>Órdenes</button>
        </>}
        {!isAdmin && user && <>
          <button style={s.navBtn(page === "catalogo")}   onClick={() => setPage("catalogo")}>Catálogo</button>
          <button style={s.navBtn(page === "misOrdenes")} onClick={() => setPage("misOrdenes")}>Mis órdenes</button>
        </>}
      </div>

      {/* Derecha */}
      <div style={s.links}>
        {user ? <>
          <div style={s.pill}>
            {isAdmin && <span style={s.adminBadge}>Admin</span>}
            {user.nombre}
          </div>
          {!isAdmin && (
            <button style={s.cartBtn} onClick={onOpenCart}>
              🛍 Carrito
              {totalQty > 0 && <span style={s.badge}>{totalQty}</span>}
            </button>
          )}
          <button style={s.logoutBtn} onClick={logout}>Salir</button>
        </> : <>
          <button style={s.navBtn(page === "login")}
            onClick={() => setPage("login")}>Iniciar sesión</button>
          <button style={s.registerBtn}
            onClick={() => setPage("register")}>Registrarse</button>
        </>}
      </div>
    </nav>
  );
}
