import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiLogin } from "../api/api";

/*export default function LoginPage({ setPage, push }) {
  const { login } = useAuth();
  const [form, setForm]       = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const h = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));
*/

export default function LoginPage({ setPage, push }) {
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const h = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));


   const submit = async () => {
    if (!form.email || !form.password) { 
      push("Completa todos los campos", "err"); 
      return; 
    }
    
    setLoading(true);
    try {
      const data = await apiLogin(form);
      // data = { access_token, token_type, usuario: { id, nombre, email, rol } }
      login(data.usuario, data.access_token);
      push(`¡Bienvenido, ${data.usuario.nombre}!`);
      // La redirección la maneja App.jsx con el useEffect
    } catch (e) {
      push(e.message || "Credenciales incorrectas", "err");
    } finally {
      setLoading(false);
    }
  };

  const s = {
    page: {
      minHeight: "100vh", display: "flex",
      alignItems: "center", justifyContent: "center",
      padding: "40px 20px",
      background: "radial-gradient(ellipse at 30% 50%, rgba(201,168,76,.06) 0%, transparent 60%)",
    },
    card: {
      width: "100%", maxWidth: 400,
      background: "#1E1914", border: "1px solid #3D3428",
      borderRadius: 20, overflow: "hidden",
    },
    head: {
      padding: "32px 36px 22px",
      borderBottom: "1px solid #2E2820", textAlign: "center",
    },
    brand: {
      display: "block", marginBottom: 18,
      fontFamily: "'Playfair Display', serif",
      fontSize: 12, color: "#C9A84C",
      letterSpacing: ".18em", textTransform: "uppercase",
    },
    h2:  { fontFamily: "'Playfair Display', serif", fontSize: 27, color: "#E8D5A3" },
    sub: { fontSize: 13, color: "#7A6E64", marginTop: 6 },
    body: { padding: "26px 36px" },
    field: { display: "flex", flexDirection: "column", gap: 6, marginBottom: 16 },
    label: { fontSize: 11, fontWeight: 600, color: "#5A504A", letterSpacing: ".12em", textTransform: "uppercase" },
    input: {
      padding: "12px 14px",
      background: "#0E0B08", border: "1px solid #3D3428",
      borderRadius: 9, color: "#E8E0D5", fontSize: 14, outline: "none",
      fontFamily: "'Jost', sans-serif",
    },
    btn: {
      width: "100%", background: "#C9A84C", color: "#1A1410",
      border: "none", borderRadius: 10, padding: "13px",
      fontSize: 14, fontWeight: 600, cursor: "pointer",
      fontFamily: "'Jost', sans-serif",
    },
    hint: {
      marginTop: 14, padding: "11px 14px",
      background: "rgba(201,168,76,.07)",
      border: "1px solid rgba(201,168,76,.18)",
      borderRadius: 8, fontSize: 12, color: "#9A8E84", lineHeight: 1.7,
    },
    foot: {
      padding: "16px 36px", borderTop: "1px solid #2E2820",
      textAlign: "center", fontSize: 13, color: "#7A6E64",
    },
    link: {
      background: "none", border: "none", color: "#C9A84C",
      cursor: "pointer", fontSize: 13, fontWeight: 500,
      textDecoration: "underline", textUnderlineOffset: 3,
    },
  };

  return (
    <div style={s.page}>
      <div style={s.card}>
        <div style={s.head}>
          <span style={s.brand}>Aroma Distribuido</span>
          <h2 style={s.h2}>Bienvenido</h2>
          <p style={s.sub}>Inicia sesión para continuar</p>
        </div>
        <div style={s.body}>
          <div style={s.field}>
            <label style={s.label}>Correo electrónico</label>
            <input style={s.input} name="email" type="email"
              placeholder="tu@email.com" value={form.email} onChange={h}
              onKeyDown={e => e.key === "Enter" && submit()}/>
          </div>
          <div style={s.field}>
            <label style={s.label}>Contraseña</label>
            <input style={s.input} name="password" type="password"
              placeholder="••••••••" value={form.password} onChange={h}
              onKeyDown={e => e.key === "Enter" && submit()}/>
          </div>
          <button style={{ ...s.btn, opacity: loading ? .6 : 1 }}
            onClick={submit} disabled={loading}>
            {loading ? "Ingresando…" : "Iniciar sesión"}
          </button>
          {/* <div style={s.hint}>
            <strong style={{ color: "#C9A84C" }}>Admin:</strong> admin@aroma.com · admin123<br/>
            <strong style={{ color: "#C9A84C" }}>Cliente:</strong> cliente@aroma.com · admin123
          </div> */}
        </div>
        <div style={s.foot}>
          ¿No tienes cuenta?{" "}
          <button style={s.link} onClick={() => setPage("register")}>Regístrate</button>
        </div>
      </div>
    </div>
  );
}
