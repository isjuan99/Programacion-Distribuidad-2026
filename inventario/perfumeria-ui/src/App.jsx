/*import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast, ToastContainer } from "../components/Toast";
import Navbar             from "../components/Navbar";
import CartPanel          from "../components/CartPanel";
import LoginPage          from "../pages/LoginPage";
import RegisterPage       from "../pages/RegisterPage";
import CatalogoPage       from "../pages/CatalogoPage";
import CheckoutPage       from "../pages/CheckoutPage";
import MisOrdenesPage     from "../pages/MisOrdenesPage";
import DashboardPage      from "../pages/admin/DashboardPage";
import AdminPerfumesPage  from "../pages/admin/AdminPerfumesPage";
import AdminOrdenesPage   from "../pages/admin/AdminOrdenesPage";

/*
  REDIRECCIÓN POR ROL
  ───────────────────
  Sin sesión          →  LoginPage / RegisterPage
  rol === "admin"     →  DashboardPage   (panel admin)
  rol === "cliente"   →  CatalogoPage    (tienda)

  El useEffect escucha cambios en user.access_token
  y redirige automáticamente en login y logout.
*

export default function App() {
  const { user } = useAuth();
  const { push, toasts } = useToast();

  const [page, setPage] = useState(() => {
    if (!user)                return "login";
    if (user.rol === "admin") return "dashboard";
    return "catalogo";
  });

  const [cartOpen, setCartOpen] = useState(false);

  useEffect(() => {
    if (!user)                { setPage("login");     return; }
    if (user.rol === "admin") { setPage("dashboard"); return; }
    setPage("dashboard"); // Por simplicidad, admin y cliente comparten dashboard
  }, [user?.access_token]);

  const renderPage = () => {
    if (!user) {
      if (page === "register") return <RegisterPage setPage={setPage} push={push} />;
      return <LoginPage setPage={setPage} push={push} />;
    }

    if (user.rol === "admin") {
      if (page === "adminPerfumes") return <AdminPerfumesPage push={push} />;
      if (page === "adminOrdenes")  return <AdminOrdenesPage />;
      return <DashboardPage user={user} />;
    }

    if (page === "checkout")   return <CheckoutPage push={push} setPage={setPage} />;
    if (page === "misOrdenes") return <MisOrdenesPage />;
    return <CatalogoPage push={push} />;
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Jost:wght@300;400;500;600&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0E0B08; color: #E8E0D5; }
        @keyframes toastIn { from { transform: translateY(8px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
      `}</style>

      <Navbar
        page={page}
        setPage={setPage}
        onOpenCart={() => setCartOpen(true)}
      />

      {renderPage()}

      {cartOpen && (
        <CartPanel
          onClose={() => setCartOpen(false)}
          onCheckout={() => { setCartOpen(false); setPage("checkout"); }}
        />
      )}

      <ToastContainer toasts={toasts} />
    </>
  );
}*/

// src/App.jsx
import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast, ToastContainer } from "../components/Toast";
import Navbar             from "../components/Navbar";
import CartPanel          from "../components/CartPanel";
import LoginPage          from "../pages/LoginPage";
import RegisterPage       from "../pages/RegisterPage";
import CatalogoPage       from "../pages/CatalogoPage";
import CheckoutPage       from "../pages/CheckoutPage";
import MisOrdenesPage     from "../pages/MisOrdenesPage";
import DashboardPage      from "../pages/admin/DashboardPage";
import AdminPerfumesPage  from "../pages/admin/AdminPerfumesPage";
import AdminOrdenesPage   from "../pages/admin/AdminOrdenesPage";
import PerfumeriaApp      from "../pages/admin/PerfumeriaApp";  

export default function App() {
  const { user, token } = useAuth();
  const { push, toasts } = useToast();

  const [page, setPage] = useState(() => {
    if (!user) return "login";
    if (user.rol === "admin") return "PerfumeriaApp";
    return "catalogo";
  });

  const [cartOpen, setCartOpen] = useState(false);

  // Redirigir cuando user cambia (login o logout)
  useEffect(() => {
    if (!user) {
      setPage("login");
    } else if (user.rol === "admin") {
      setPage("PerfumeriaApp");
    } else if (user.rol === "cliente") {
      setPage("catalogo");
    }
  }, [user]);

  const renderPage = () => {
    // Sin sesión
    if (!user) {
      if (page === "register") return <RegisterPage setPage={setPage} push={push} />;
      return <LoginPage setPage={setPage} push={push} />;
    }

    // Administrador
    if (user.rol === "admin") {
      if (page === "PerfumeriaApp") return <PerfumeriaApp push={push} />;
      if (page === "PerfumeriaApp") return <PerfumeriaApp />;
      return <PerfumeriaApp user={user} setPage={setPage} />;
    }

    // Cliente
    if (page === "checkout") return <CheckoutPage push={push} setPage={setPage} />;
    if (page === "misOrdenes") return <MisOrdenesPage />;
    return <CatalogoPage push={push} setPage={setPage} />;
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Jost:wght@300;400;500;600&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0E0B08; color: #E8E0D5; }
        @keyframes toastIn { from { transform: translateY(8px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
      `}</style>

      <Navbar
        page={page}
        setPage={setPage}
        onOpenCart={() => setCartOpen(true)}
      />

      {renderPage()}

      {cartOpen && (
        <CartPanel
          onClose={() => setCartOpen(false)}
          onCheckout={() => { setCartOpen(false); setPage("checkout"); }}
        />
      )}

      <ToastContainer toasts={toasts} />
    </>
  );
}