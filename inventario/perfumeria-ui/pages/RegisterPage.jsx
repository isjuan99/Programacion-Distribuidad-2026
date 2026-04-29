import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiRegistro } from "../api/api";

export default function RegisterPage({ setPage, push }) {
  const { login } = useAuth();
  const [form, setForm]       = useState({ nombre: "", email: "", password: "", confirm: "" });
  const [loading, setLoading] = useState(false);
  const h = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const submit = async () => {
    if (!form.nombre || !form.email || !form.password) { push("Completa todos los campos", "err"); return; }
    if (form.password !== form.confirm)               { push("Las contraseñas no coinciden", "err"); return; }
    if (form.password.length < 4)                     { push("Contraseña mínimo 4 caracteres", "err"); return; }
    setLoading(true);
    try {
      const data = await apiRegistro({ nombre: form.nombre, email: form.email, password: form.password });
      login(data);
      push(`¡Bienvenido, ${data.nombre}!`);
    } catch (e) {
      push(e.message || "Error al registrarse", "err");
    } finally {
      setLoading(false);
    }
  };

  const s = {
    page: {
      minHeight: "100vh", display: "flex",
      alignItems: "center", justifyContent: "center", padding: "40px 20px",
      background: "radial-gradient(ellipse at 70% 50%, rgba(201,168,76,.06) 0%, transparent 60%)",
    },
    card: {
      width: "100%", maxWidth: 430,
      background: "#1E1914", border: "1px solid #3D3428",
      borderRadius: 20, overflow: "hidden",
    },
    head: { padding: "32px 36px 22px", borderBottom: "1px solid #2E2820", textAlign: "center" },
    brand: { display: "block", marginBottom: 18, fontFamily: "'Playfair Display', serif", fontSize: 12, color: "#C9A84C", letterSpacing: ".18em", textTransform: "uppercase" },
    h2:    { fontFamily: "'Playfair Display', serif", fontSize: 27, color: "#E8D5A3" },
    sub:   { fontSize: 13, color: "#7A6E64", marginTop: 6 },
    body:  { padding: "26px 36px" },
    field: { display: "flex", flexDirection: "column", gap: 6, marginBottom: 16 },
    row:   { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 16 },
    label: { fontSize: 11, fontWeight: 600, color: "#5A504A", letterSpacing: ".12em", textTransform: "uppercase" },
    input: { padding: "12px 14px", background: "#0E0B08", border: "1px solid #3D3428", borderRadius: 9, color: "#E8E0D5", fontSize: 14, outline: "none", fontFamily: "'Jost', sans-serif" },
    btn:   { width: "100%", background: "#C9A84C", color: "#1A1410", border: "none", borderRadius: 10, padding: "13px", fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: "'Jost', sans-serif" },
    foot:  { padding: "16px 36px", borderTop: "1px solid #2E2820", textAlign: "center", fontSize: 13, color: "#7A6E64" },
    link:  { background: "none", border: "none", color: "#C9A84C", cursor: "pointer", fontSize: 13, fontWeight: 500, textDecoration: "underline", textUnderlineOffset: 3 },
  };

  return (
    <div style={s.page}>
      <div style={s.card}>
        <div style={s.head}>
          <span style={s.brand}>Aroma Distribuido</span>
          <h2 style={s.h2}>Crear cuenta</h2>
          <p style={s.sub}>Únete y descubre nuestra colección</p>
        </div>
        <div style={s.body}>
          <div style={s.field}>
            <label style={s.label}>Nombre completo</label>
            <input style={s.input} name="nombre" placeholder="Juan Camilo González" value={form.nombre} onChange={h}/>
          </div>
          <div style={s.field}>
            <label style={s.label}>Correo electrónico</label>
            <input style={s.input} name="email" type="email" placeholder="tu@email.com" value={form.email} onChange={h}/>
          </div>
          <div style={s.row}>
            <div style={s.field}>
              <label style={s.label}>Contraseña</label>
              <input style={s.input} name="password" type="password" placeholder="••••••••" value={form.password} onChange={h}/>
            </div>
            <div style={s.field}>
              <label style={s.label}>Confirmar</label>
              <input style={s.input} name="confirm" type="password" placeholder="••••••••" value={form.confirm} onChange={h} onKeyDown={e => e.key === "Enter" && submit()}/>
            </div>
          </div>
          <button style={{ ...s.btn, opacity: loading ? .6 : 1 }} onClick={submit} disabled={loading}>
            {loading ? "Creando cuenta…" : "Crear cuenta"}
          </button>
        </div>
        <div style={s.foot}>
          ¿Ya tienes cuenta?{" "}
          <button style={s.link} onClick={() => setPage("login")}>Inicia sesión</button>
        </div>
      </div>
    </div>
  );
}
