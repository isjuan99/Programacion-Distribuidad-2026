import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";

const API_URL = "http://localhost:8000";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --cream: #F5F0E8;
    --ink: #1A1410;
    --gold: #C9A84C;
    --gold-light: #E8D5A3;
    --rose: #B5716A;
    --rose-light: #F0DDD9;
    --sage: #7A8C6E;
    --sage-light: #E4EAE0;
    --surface: #FDFAF5;
    --border: #E2D9CC;
    --muted: #8A7F72;
    --shadow: 0 2px 20px rgba(26,20,16,0.08);
    --shadow-lg: 0 8px 40px rgba(26,20,16,0.12);
  }

  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--cream);
    color: var(--ink);
    min-height: 100vh;
  }

  .app { display: flex; min-height: 100vh; }

  /* ── SIDEBAR ── */
  .sidebar {
    width: 240px;
    min-height: 100vh;
    background: var(--ink);
    display: flex;
    flex-direction: column;
    padding: 0;
    position: fixed;
    left: 0; top: 0; bottom: 0;
    z-index: 100;
  }
  .sidebar-logo {
    padding: 36px 28px 28px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }
  .sidebar-logo h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 22px;
    font-weight: 300;
    color: var(--gold-light);
    letter-spacing: 0.05em;
    line-height: 1.3;
  }
  .sidebar-logo span {
    display: block;
    font-size: 10px;
    font-weight: 500;
    color: var(--muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 4px;
  }
  .sidebar-nav {
    padding: 24px 16px;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .nav-label {
    font-size: 10px;
    font-weight: 500;
    color: #4A4540;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0 12px;
    margin: 16px 0 8px;
  }
  .nav-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 16px;
    border-radius: 8px;
    border: none;
    background: transparent;
    color: #9A9188;
    font-family: 'DM Sans', sans-serif;
    font-size: 13.5px;
    font-weight: 400;
    cursor: pointer;
    transition: all 0.15s;
    text-align: left;
    width: 100%;
  }
  .nav-btn:hover { background: rgba(255,255,255,0.05); color: #E8E0D5; }
  .nav-btn.active { background: rgba(201,168,76,0.15); color: var(--gold-light); }
  .nav-btn .icon {
    width: 18px; height: 18px;
    opacity: 0.7;
    flex-shrink: 0;
  }
  .nav-btn.active .icon { opacity: 1; }
  .sidebar-footer {
    padding: 20px 28px;
    border-top: 1px solid rgba(255,255,255,0.06);
  }
  .sidebar-footer p {
    font-size: 11px;
    color: #4A4540;
    line-height: 1.6;
  }

  /* ── MAIN CONTENT ── */
  .main {
    margin-left: 240px;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  /* ── TOPBAR ── */
  .topbar {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 36px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky; top: 0; z-index: 50;
  }
  .topbar-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 20px;
    font-weight: 400;
    color: var(--ink);
  }
  .topbar-right { display: flex; align-items: center; gap: 12px; }
  .badge {
    display: inline-flex; align-items: center; justify-content: center;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.05em;
  }
  .badge-gold { background: var(--gold-light); color: #7A5C10; }
  .badge-sage { background: var(--sage-light); color: #3D5230; }
  .badge-rose { background: var(--rose-light); color: #7A3830; }

  /* ── PAGE CONTENT ── */
  .page { padding: 36px; }
  .page-header {
    margin-bottom: 32px;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
  }
  .page-header h2 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 32px;
    font-weight: 300;
    color: var(--ink);
    line-height: 1;
  }
  .page-header p {
    font-size: 13px;
    color: var(--muted);
    margin-top: 6px;
  }

  /* ── STATS GRID ── */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 36px;
  }
  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px 28px;
    position: relative;
    overflow: hidden;
  }
  .stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
  }
  .stat-card.gold::before { background: var(--gold); }
  .stat-card.rose::before { background: var(--rose); }
  .stat-card.sage::before { background: var(--sage); }
  .stat-label {
    font-size: 11px;
    font-weight: 500;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 12px;
  }
  .stat-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 38px;
    font-weight: 300;
    color: var(--ink);
    line-height: 1;
  }
  .stat-sub {
    font-size: 12px;
    color: var(--muted);
    margin-top: 8px;
  }

  /* ── TABLE ── */
  .table-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
  }
  .table-header {
    padding: 20px 24px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
  }
  .table-header h3 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 18px;
    font-weight: 400;
  }
  .search-box {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--cream);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 14px;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: var(--ink);
    min-width: 220px;
  }
  .search-box input {
    border: none; background: transparent;
    font-family: inherit; font-size: inherit; color: inherit;
    outline: none; width: 100%;
  }
  .search-box input::placeholder { color: var(--muted); }
  table { width: 100%; border-collapse: collapse; }
  thead tr { background: #F8F4EE; }
  th {
    padding: 12px 20px;
    text-align: left;
    font-size: 11px;
    font-weight: 500;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
  }
  td {
    padding: 16px 20px;
    font-size: 13.5px;
    border-bottom: 1px solid var(--border);
    color: var(--ink);
    vertical-align: middle;
  }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: #FDFAF0; }
  .perfume-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 16px;
    font-weight: 400;
  }
  .marca-pill {
    display: inline-flex;
    padding: 3px 10px;
    background: var(--cream);
    border: 1px solid var(--border);
    border-radius: 20px;
    font-size: 11px;
    color: var(--muted);
    font-weight: 500;
  }
  .precio {
    font-family: 'Cormorant Garamond', serif;
    font-size: 17px;
    font-weight: 600;
    color: #7A5C10;
  }
  .stock-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .stock-dot {
    width: 7px; height: 7px; border-radius: 50%;
    flex-shrink: 0;
  }
  .stock-dot.high { background: var(--sage); }
  .stock-dot.mid  { background: var(--gold); }
  .stock-dot.low  { background: var(--rose); }

  /* ── BUTTONS ── */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
    border: none;
  }
  .btn-primary {
    background: var(--ink);
    color: var(--gold-light);
  }
  .btn-primary:hover { background: #2E2520; }
  .btn-secondary {
    background: var(--cream);
    color: var(--ink);
    border: 1px solid var(--border);
  }
  .btn-secondary:hover { background: #EDE8DF; }
  .btn-gold {
    background: var(--gold);
    color: #3A2800;
  }
  .btn-gold:hover { background: #B89640; }
  .btn-icon {
    padding: 8px;
    border-radius: 6px;
    background: var(--cream);
    border: 1px solid var(--border);
    color: var(--muted);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
  }
  .btn-icon:hover { background: var(--gold-light); color: #7A5C10; border-color: var(--gold); }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }

  /* ── MODAL ── */
  .modal-overlay {
    position: fixed; inset: 0;
    background: rgba(26,20,16,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 200;
    padding: 20px;
    animation: fadeIn 0.15s ease;
  }
  @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
  .modal {
    background: var(--surface);
    border-radius: 16px;
    width: 100%;
    max-width: 480px;
    box-shadow: var(--shadow-lg);
    animation: slideUp 0.2s ease;
    overflow: hidden;
  }
  @keyframes slideUp { from { transform:translateY(16px); opacity:0; } to { transform:translateY(0); opacity:1; } }
  .modal-head {
    padding: 28px 32px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
  }
  .modal-head h3 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 24px;
    font-weight: 300;
  }
  .modal-head p { font-size: 13px; color: var(--muted); margin-top: 4px; }
  .modal-body { padding: 24px 32px; display: flex; flex-direction: column; gap: 18px; }
  .modal-footer {
    padding: 20px 32px;
    border-top: 1px solid var(--border);
    display: flex; gap: 12px; justify-content: flex-end;
  }
  .close-btn {
    background: none; border: none; cursor: pointer;
    color: var(--muted); padding: 4px;
    display: flex; align-items: center;
    transition: color 0.15s;
  }
  .close-btn:hover { color: var(--ink); }

  /* ── FORM FIELDS ── */
  .field { display: flex; flex-direction: column; gap: 6px; }
  .field label {
    font-size: 11px;
    font-weight: 500;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }
  .field input {
    padding: 11px 14px;
    border: 1px solid var(--border);
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    color: var(--ink);
    background: var(--cream);
    outline: none;
    transition: border-color 0.15s;
  }
  .field input:focus { border-color: var(--gold); background: #fff; }
  .field input::placeholder { color: #B8AFA4; }
  .fields-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

  /* ── TOAST ── */
  .toast-container {
    position: fixed;
    bottom: 28px; right: 28px;
    display: flex; flex-direction: column; gap: 10px;
    z-index: 300;
  }
  .toast {
    padding: 14px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    max-width: 320px;
    box-shadow: var(--shadow-lg);
    animation: slideUp 0.2s ease;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .toast.success { background: var(--ink); color: var(--gold-light); }
  .toast.error { background: var(--rose); color: #fff; }

  /* ── LOADING ── */
  .loading {
    display: flex; align-items: center; justify-content: center;
    padding: 60px; color: var(--muted);
    flex-direction: column; gap: 14px;
  }
  .spinner {
    width: 28px; height: 28px;
    border: 2px solid var(--border);
    border-top-color: var(--gold);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── EMPTY STATE ── */
  .empty {
    padding: 64px 32px;
    text-align: center;
    color: var(--muted);
  }
  .empty p { font-size: 14px; margin-top: 8px; }

  /* ── RESPONSIVE ── */
  @media (max-width: 900px) {
    .sidebar { width: 200px; }
    .main { margin-left: 200px; }
    .stats-grid { grid-template-columns: 1fr 1fr; }
    .page { padding: 24px; }
  }
`;

function Icon({ name, size = 18 }) {
  const icons = {
    inventory: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>,
    add: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8v8"/></svg>,
    edit: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4Z"/></svg>,
    close: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>,
    search: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>,
    refresh: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>,
    chart: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>,
    check: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>,
    alert: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
    orders: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7 4h10l3 4v12H4V8Z"/><path d="M4 8h16"/><path d="M9 12h6"/><path d="M9 16h6"/></svg>,
  };
  return icons[name] || null;
}

function Toast({ toasts }) {
  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast ${t.type}`}>
          <Icon name={t.type === "success" ? "check" : "alert"} size={16} />
          {t.msg}
        </div>
      ))}
    </div>
  );
}

function ModalCrear({ onClose, onCreado }) {
  const [form, setForm] = useState({ nombre: "", marca: "", precio: "", stock: "", imagen: null });
  const [loading, setLoading] = useState(false);

  const handle = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  const handleImage = e => {
    const file = e.target.files?.[0] || null;
    setForm(f => ({ ...f, imagen: file }));
  };

  const submit = async () => {
    if (!form.nombre || !form.marca || !form.precio || !form.stock) return;
    setLoading(true);
    try {
      const payload = new FormData();
      payload.append("nombre", form.nombre);
      payload.append("marca", form.marca);
      payload.append("precio", form.precio);
      payload.append("stock", form.stock);
      if (form.imagen) {
        payload.append("imagen", form.imagen);
      }
      const res = await fetch(`${API_URL}/perfumes`, { method: "POST", body: payload });
      if (!res.ok) throw new Error();
      onCreado("Perfume registrado exitosamente");
      onClose();
    } catch {
      onCreado("Error al registrar el perfume", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-head">
          <div>
            <h3>Nuevo perfume</h3>
            <p>Registrar producto en el inventario</p>
          </div>
          <button className="close-btn" onClick={onClose}><Icon name="close" size={20} /></button>
        </div>
        <div className="modal-body">
          <div className="fields-row">
            <div className="field">
              <label>Nombre</label>
              <input name="nombre" placeholder="Ej: Sauvage" value={form.nombre} onChange={handle} />
            </div>
            <div className="field">
              <label>Marca</label>
              <input name="marca" placeholder="Ej: Dior" value={form.marca} onChange={handle} />
            </div>
          </div>
          <div className="fields-row">
            <div className="field">
              <label>Precio (USD)</label>
              <input name="precio" type="number" placeholder="120.00" value={form.precio} onChange={handle} />
            </div>
            <div className="field">
              <label>Stock (unidades)</label>
              <input name="stock" type="number" placeholder="15" value={form.stock} onChange={handle} />
            </div>
          </div>
          <div className="field">
            <label>Foto del perfume (opcional)</label>
            <input type="file" accept="image/*" onChange={handleImage} />
            {form.imagen && (
              <small style={{ color: "var(--muted)", fontSize: 12 }}>
                Archivo seleccionado: {form.imagen.name}
              </small>
            )}
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
          <button className="btn btn-gold" onClick={submit} disabled={loading}>
            {loading ? "Guardando…" : "Registrar perfume"}
          </button>
        </div>
      </div>
    </div>
  );
}

function ModalEditar({ perfume, onClose, onActualizado }) {
  const [form, setForm] = useState({ precio: perfume.precio, stock: perfume.stock });
  const [imagen, setImagen] = useState(null);
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(false);

  const handle = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  const handleImagen = (e) => setImagen(e.target.files?.[0] || null);

  useEffect(() => {
    if (!imagen) {
      setPreview("");
      return;
    }
    const nextPreview = URL.createObjectURL(imagen);
    setPreview(nextPreview);
    return () => URL.revokeObjectURL(nextPreview);
  }, [imagen]);

  const submit = async () => {
    setLoading(true);
    try {
      const payload = new FormData();
      payload.append("precio", form.precio);
      payload.append("stock", form.stock);
      if (imagen) payload.append("imagen", imagen);
      const res = await fetch(`${API_URL}/perfumes/${perfume.id}`, { method: "PUT", body: payload });
      if (!res.ok) throw new Error();
      onActualizado("Inventario actualizado correctamente");
      onClose();
    } catch {
      onActualizado("Error al actualizar el inventario", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-head">
          <div>
            <h3>Editar perfume</h3>
            <p style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: 16, marginTop: 2 }}>
              {perfume.nombre} · <span style={{ color: "var(--muted)", fontSize: 13, fontFamily: "inherit" }}>{perfume.marca}</span>
            </p>
          </div>
          <button className="close-btn" onClick={onClose}><Icon name="close" size={20} /></button>
        </div>
        <div className="modal-body">
          <div className="fields-row">
            <div className="field">
              <label>Precio (USD)</label>
              <input name="precio" type="number" value={form.precio} onChange={handle} />
            </div>
            <div className="field">
              <label>Stock (unidades)</label>
              <input name="stock" type="number" value={form.stock} onChange={handle} />
            </div>
          </div>
          <div className="field">
            <label>Cambiar foto (opcional)</label>
            <input type="file" accept="image/*" onChange={handleImagen} />
            {imagen && (
              <small style={{ color: "var(--muted)", fontSize: 12 }}>
                Nueva imagen: {imagen.name}
              </small>
            )}
            {preview && (
              <img
                src={preview}
                alt="Vista previa"
                style={{
                  marginTop: 8,
                  width: "100%",
                  maxHeight: 180,
                  objectFit: "cover",
                  borderRadius: 8,
                  border: "1px solid var(--border)"
                }}
              />
            )}
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
          <button className="btn btn-primary" onClick={submit} disabled={loading}>
            {loading ? "Guardando…" : "Actualizar"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const { token } = useAuth();
  const [vista, setVista] = useState("inventario");
  const [inventario, setInventario] = useState([]);
  const [ordenes, setOrdenes] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [cargandoOrdenes, setCargandoOrdenes] = useState(false);
  const [actualizandoOrden, setActualizandoOrden] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [modalCrear, setModalCrear] = useState(false);
  const [editando, setEditando] = useState(null);
  const [toasts, setToasts] = useState([]);

  const toast = (msg, type = "success") => {
    const id = Date.now();
    setToasts(t => [...t, { id, msg, type }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3500);
  };

  const cargarInventario = async () => {
    setCargando(true);
    try {
      const res = await fetch(`${API_URL}/inventario`);
      const data = await res.json();
      setInventario(data);
    } catch {
      toast("No se pudo conectar con la API", "error");
      setInventario([]);
    } finally {
      setCargando(false);
    }
  };

  const cargarOrdenes = async () => {
    setCargandoOrdenes(true);
    try {
      const res = await fetch(`${API_URL}/admin/ordenes`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error();
      setOrdenes(await res.json());
    } catch {
      toast("No se pudieron cargar las órdenes", "error");
      setOrdenes([]);
    } finally {
      setCargandoOrdenes(false);
    }
  };

  const cambiarEstadoOrden = async (ordenId, estado) => {
    setActualizandoOrden(ordenId);
    try {
      const res = await fetch(`${API_URL}/admin/ordenes/${ordenId}/estado`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ estado }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      toast(data.mensaje || "Orden actualizada");
      cargarOrdenes();
    } catch {
      toast("No se pudo actualizar la orden", "error");
    } finally {
      setActualizandoOrden(null);
    }
  };

  useEffect(() => { cargarInventario(); }, []);
  useEffect(() => {
    if (vista === "ordenes") {
      cargarOrdenes();
    }
  }, [vista]);

  const filtrado = inventario.filter(p =>
    p.nombre?.toLowerCase().includes(busqueda.toLowerCase()) ||
    p.marca?.toLowerCase().includes(busqueda.toLowerCase())
  );

  const totalItems = inventario.length;
  const totalStock = inventario.reduce((s, p) => s + (p.stock || 0), 0);
  const valorTotal = inventario.reduce((s, p) => s + (p.precio || 0) * (p.stock || 0), 0);
  const stockBajo = inventario.filter(p => p.stock <= 5).length;

  const stockClass = s => s > 10 ? "high" : s > 5 ? "mid" : "low";
  const estadoMeta = (estado) => ({
    pendiente: { bg: "var(--rose-light)", color: "#7A3830", border: "var(--rose)" },
    confirmada: { bg: "var(--gold-light)", color: "#7A5C10", border: "var(--gold)" },
    rechazada: { bg: "#F0E5DD", color: "#6C4A3F", border: "#B99A8A" },
  }[estado] || { bg: "var(--cream)", color: "var(--muted)", border: "var(--border)" });

  return (
    <>
      <style>{styles}</style>
      <div className="app">

        {/* SIDEBAR */}
        <aside className="sidebar">
          <div className="sidebar-logo">
            <h1>Aroma<br/>Distribuido</h1>
            <span>E-commerce </span>
          </div>
          <nav className="sidebar-nav">
            <span className="nav-label">Módulos</span>
            <button className={`nav-btn ${vista === "inventario" ? "active" : ""}`} onClick={() => setVista("inventario")}>
              <span className="icon"><Icon name="inventory" /></span>
              Inventario
            </button>
            <button className={`nav-btn ${vista === "ordenes" ? "active" : ""}`} onClick={() => setVista("ordenes")}>
              <span className="icon"><Icon name="orders" /></span>
              Órdenes
            </button>
            <button className={`nav-btn ${vista === "estadisticas" ? "active" : ""}`} onClick={() => setVista("estadisticas")}>
              <span className="icon"><Icon name="chart" /></span>
              Estadísticas
            </button>
          </nav>
          <div className="sidebar-footer">
            <p>API: localhost:8000<br />MySQL · FastAPI</p>
          </div>
        </aside>

        {/* MAIN */}
        <main className="main">

          {/* TOPBAR */}
          <div className="topbar">
            <span className="topbar-title">
              {vista === "inventario" ? "Gestión de inventario" : vista === "ordenes" ? "Gestión de órdenes" : "Estadísticas"}
            </span>
            <div className="topbar-right">
              {vista === "ordenes" ? (
                <span className="badge badge-rose">
                  {ordenes.filter(o => o.estado === "pendiente").length} pendientes
                </span>
              ) : stockBajo > 0 && (
                <span className="badge badge-rose">
                  {stockBajo} con stock bajo
                </span>
              )}
              <span className="badge badge-sage">{totalItems} productos</span>
            </div>
          </div>

          {/* INVENTARIO */}
          {vista === "inventario" && (
            <div className="page">
              <div className="page-header">
                <div>
                  <h2>Inventario</h2>
                  <p>Catálogo completo de perfumes registrados en la base de datos</p>
                </div>
                <div style={{ display: "flex", gap: 10 }}>
                  <button className="btn btn-secondary" onClick={cargarInventario}>
                    <Icon name="refresh" size={15} /> Actualizar
                  </button>
                  <button className="btn btn-gold" onClick={() => setModalCrear(true)}>
                    <Icon name="add" size={15} /> Nuevo perfume
                  </button>
                </div>
              </div>

              {/* STATS */}
              <div className="stats-grid">
                <div className="stat-card gold">
                  <div className="stat-label">Productos registrados</div>
                  <div className="stat-value">{totalItems}</div>
                  <div className="stat-sub">En base de datos</div>
                </div>
                <div className="stat-card rose">
                  <div className="stat-label">Unidades en stock</div>
                  <div className="stat-value">{totalStock}</div>
                  <div className="stat-sub">{stockBajo > 0 ? `${stockBajo} productos con stock ≤ 5` : "Stock saludable"}</div>
                </div>
                <div className="stat-card sage">
                  <div className="stat-label">Valor del inventario</div>
                  <div className="stat-value">${valorTotal.toLocaleString("en-US", { maximumFractionDigits: 0 })}</div>
                  <div className="stat-sub">Precio × stock total</div>
                </div>
              </div>

              {/* TABLE */}
              <div className="table-container">
                <div className="table-header">
                  <h3>Catálogo de perfumes</h3>
                  <div className="search-box">
                    <Icon name="search" size={15} />
                    <input
                      placeholder="Buscar por nombre o marca…"
                      value={busqueda}
                      onChange={e => setBusqueda(e.target.value)}
                    />
                  </div>
                </div>

                {cargando ? (
                  <div className="loading">
                    <div className="spinner" />
                    <span style={{ fontSize: 13, color: "var(--muted)" }}>Cargando inventario…</span>
                  </div>
                ) : filtrado.length === 0 ? (
                  <div className="empty">
                    <Icon name="inventory" size={36} />
                    <p>{busqueda ? "Sin resultados para tu búsqueda" : "No hay perfumes registrados"}</p>
                  </div>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Marca</th>
                        <th>Precio</th>
                        <th>Stock</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filtrado.map(p => (
                        <tr key={p.id}>
                          <td style={{ color: "var(--muted)", fontSize: 12 }}>#{p.id}</td>
                          <td><span className="perfume-name">{p.nombre}</span></td>
                          <td><span className="marca-pill">{p.marca}</span></td>
                          <td><span className="precio">${Number(p.precio).toFixed(2)}</span></td>
                          <td>
                            <div className="stock-indicator">
                              <span className={`stock-dot ${stockClass(p.stock)}`} />
                              <span>{p.stock} uds.</span>
                            </div>
                          </td>
                          <td>
                            <button className="btn-icon" onClick={() => setEditando(p)} title="Editar">
                              <Icon name="edit" size={15} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {vista === "ordenes" && (
            <div className="page">
              <div className="page-header">
                <div>
                  <h2>Órdenes</h2>
                  <p>Gestiona los pedidos de clientes y cambia su estado manualmente</p>
                </div>
                <div style={{ display: "flex", gap: 10 }}>
                  <button className="btn btn-secondary" onClick={cargarOrdenes}>
                    <Icon name="refresh" size={15} /> Actualizar
                  </button>
                </div>
              </div>

              <div className="stats-grid">
                <div className="stat-card gold">
                  <div className="stat-label">Total órdenes</div>
                  <div className="stat-value">{ordenes.length}</div>
                  <div className="stat-sub">Pedidos registrados</div>
                </div>
                <div className="stat-card rose">
                  <div className="stat-label">Pendientes</div>
                  <div className="stat-value">{ordenes.filter(o => o.estado === "pendiente").length}</div>
                  <div className="stat-sub">Esperando revisión</div>
                </div>
                <div className="stat-card sage">
                  <div className="stat-label">Confirmadas</div>
                  <div className="stat-value">{ordenes.filter(o => o.estado === "confirmada").length}</div>
                  <div className="stat-sub">Listas o despachadas</div>
                </div>
              </div>

              <div className="table-container">
                <div className="table-header">
                  <h3>Listado de órdenes</h3>
                </div>

                {cargandoOrdenes ? (
                  <div className="loading">
                    <div className="spinner" />
                    <span style={{ fontSize: 13, color: "var(--muted)" }}>Cargando órdenes…</span>
                  </div>
                ) : ordenes.length === 0 ? (
                  <div className="empty">
                    <Icon name="orders" size={36} />
                    <p>No hay órdenes registradas</p>
                  </div>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th>Orden</th>
                        <th>Cliente</th>
                        <th>Fecha</th>
                        <th>Total</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ordenes.map(o => {
                        const meta = estadoMeta(o.estado);
                        return (
                          <tr key={o.orden_id}>
                            <td style={{ color: "var(--muted)", fontSize: 12 }}>#{o.orden_id}</td>
                            <td>
                              <div className="perfume-name">{o.usuario_nombre || `Usuario #${o.usuario_id}`}</div>
                              <div style={{ color: "var(--muted)", fontSize: 12 }}>{o.usuario_email || "Sin email"}</div>
                            </td>
                            <td style={{ color: "var(--muted)", fontSize: 13 }}>
                              {new Date(o.creado_en).toLocaleDateString("es-CO", { year: "numeric", month: "short", day: "numeric" })}
                            </td>
                            <td><span className="precio">${Number(o.total).toLocaleString("en-US", { maximumFractionDigits: 0 })}</span></td>
                            <td>
                              <span style={{
                                display: "inline-flex",
                                alignItems: "center",
                                padding: "4px 12px",
                                borderRadius: 20,
                                border: `1px solid ${meta.border}`,
                                background: meta.bg,
                                color: meta.color,
                                fontSize: 11,
                                fontWeight: 600,
                                letterSpacing: ".08em",
                                textTransform: "uppercase",
                              }}>
                                {o.estado}
                              </span>
                            </td>
                            <td>
                              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                                <button className="btn btn-secondary" onClick={() => cambiarEstadoOrden(o.orden_id, "pendiente")} disabled={actualizandoOrden === o.orden_id || o.estado === "pendiente"}>
                                  Pendiente
                                </button>
                                <button className="btn btn-gold" onClick={() => cambiarEstadoOrden(o.orden_id, "confirmada")} disabled={actualizandoOrden === o.orden_id || o.estado === "confirmada"}>
                                  Confirmar
                                </button>
                                <button className="btn btn-secondary" onClick={() => cambiarEstadoOrden(o.orden_id, "rechazada")} disabled={actualizandoOrden === o.orden_id || o.estado === "rechazada"}>
                                  Rechazar
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {/* ESTADÍSTICAS */}
          {vista === "estadisticas" && (
            <div className="page">
              <div className="page-header">
                <div>
                  <h2>Estadísticas</h2>
                  <p>Resumen analítico del inventario</p>
                </div>
              </div>
              <div className="stats-grid">
                <div className="stat-card gold">
                  <div className="stat-label">Total productos</div>
                  <div className="stat-value">{totalItems}</div>
                </div>
                <div className="stat-card rose">
                  <div className="stat-label">Stock total</div>
                  <div className="stat-value">{totalStock}</div>
                </div>
                <div className="stat-card sage">
                  <div className="stat-label">Valor inventario</div>
                  <div className="stat-value">${valorTotal.toLocaleString("en-US", { maximumFractionDigits: 0 })}</div>
                </div>
              </div>

              <div className="table-container">
                <div className="table-header">
                  <h3>Distribución por marca</h3>
                </div>
                {inventario.length === 0 ? (
                  <div className="loading"><div className="spinner" /></div>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th>Marca</th>
                        <th>Productos</th>
                        <th>Stock total</th>
                        <th>Valor total</th>
                        <th>Precio promedio</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(
                        inventario.reduce((acc, p) => {
                          if (!acc[p.marca]) acc[p.marca] = { count: 0, stock: 0, valor: 0, precios: [] };
                          acc[p.marca].count++;
                          acc[p.marca].stock += p.stock || 0;
                          acc[p.marca].valor += (p.precio || 0) * (p.stock || 0);
                          acc[p.marca].precios.push(p.precio || 0);
                          return acc;
                        }, {})
                      )
                        .sort((a, b) => b[1].valor - a[1].valor)
                        .map(([marca, d]) => (
                          <tr key={marca}>
                            <td><span className="perfume-name">{marca}</span></td>
                            <td>{d.count}</td>
                            <td>
                              <div className="stock-indicator">
                                <span className={`stock-dot ${stockClass(d.stock / d.count)}`} />
                                {d.stock}
                              </div>
                            </td>
                            <td><span className="precio">${d.valor.toLocaleString("en-US", { maximumFractionDigits: 0 })}</span></td>
                            <td style={{ color: "var(--muted)", fontSize: 13 }}>
                              ${(d.precios.reduce((a, b) => a + b, 0) / d.precios.length).toFixed(2)}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* MODALS */}
      {modalCrear && (
        <ModalCrear
          onClose={() => setModalCrear(false)}
          onCreado={(msg, type) => { toast(msg, type); cargarInventario(); }}
        />
      )}
      {editando && (
        <ModalEditar
          perfume={editando}
          onClose={() => setEditando(null)}
          onActualizado={(msg, type) => { toast(msg, type); cargarInventario(); }}
        />
      )}

      <Toast toasts={toasts} />
    </>
  );
}
