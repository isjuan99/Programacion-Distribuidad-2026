import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { apiGetInventario, apiCrearPerfume, apiActualizarPerfume } from "../../api/api";

function Modal({ title, sub, onClose, children, footer }) {
  return (
    <div style={{ position:"fixed",inset:0,background:"rgba(0,0,0,.72)",zIndex:300,display:"flex",alignItems:"center",justifyContent:"center",padding:20 }}
      onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={{ width:"100%",maxWidth:450,background:"#1E1914",border:"1px solid #3D3428",borderRadius:18,overflow:"hidden" }}>
        <div style={{ padding:"24px 30px 18px",borderBottom:"1px solid #2E2820",display:"flex",justifyContent:"space-between",alignItems:"flex-start" }}>
          <div>
            <h3 style={{ fontFamily:"'Playfair Display',serif",fontSize:21,color:"#E8D5A3" }}>{title}</h3>
            {sub && <p style={{ fontSize:13,color:"#7A6E64",marginTop:4 }}>{sub}</p>}
          </div>
          <button onClick={onClose} style={{ background:"none",border:"none",cursor:"pointer",color:"#5A504A",fontSize:20 }}>✕</button>
        </div>
        <div style={{ padding:"20px 30px",display:"flex",flexDirection:"column",gap:14 }}>{children}</div>
        <div style={{ padding:"16px 30px",borderTop:"1px solid #2E2820",display:"flex",gap:10,justifyContent:"flex-end" }}>{footer}</div>
      </div>
    </div>
  );
}

export default function AdminPerfumesPage({ push }) {
  const { user }                        = useAuth();
  const [perfumes, setPerfumes]         = useState([]);
  const [loading, setLoading]           = useState(true);
  const [showCreate, setShowCreate]     = useState(false);
  const [editItem, setEditItem]         = useState(null);
  const [form, setForm]                 = useState({ nombre:"", marca:"", precio:"", stock:"" });
  const [editForm, setEditForm]         = useState({ precio:"", stock:"" });
  const [saving, setSaving]             = useState(false);

  const load = () => {
    apiGetInventario()
      .then(setPerfumes)
      .catch(() => setPerfumes([]))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  const hf = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  const he = e => setEditForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const crear = async () => {
    if (!form.nombre || !form.marca || !form.precio || !form.stock) { push("Completa todos los campos", "err"); return; }
    setSaving(true);
    try {
      // POST /perfumes con query params (según tu API actual)
      const params = new URLSearchParams({ nombre:form.nombre, marca:form.marca, precio:form.precio, stock:form.stock });
      const res = await fetch(`http://localhost:8000/perfumes?${params}`, { method:"POST" });
      if (!res.ok) throw new Error();
      push("Perfume creado exitosamente");
      setShowCreate(false);
      setForm({ nombre:"", marca:"", precio:"", stock:"" });
      load();
    } catch { push("Error al crear perfume", "err"); }
    finally { setSaving(false); }
  };

  const actualizar = async () => {
    if (!editForm.precio && editForm.stock === "") { push("Ingresa precio o stock", "err"); return; }
    setSaving(true);
    try {
      // PUT /perfumes/{id} con query params (según tu API actual)
      const params = new URLSearchParams({ precio: editForm.precio, stock: editForm.stock });
      const res = await fetch(`http://localhost:8000/perfumes/${editItem.id}?${params}`, { method:"PUT" });
      if (!res.ok) throw new Error();
      push("Perfume actualizado");
      setEditItem(null);
      load();
    } catch { push("Error al actualizar", "err"); }
    finally { setSaving(false); }
  };

  const sColor = (s) => s > 10 ? "#7A8C6E" : s > 5 ? "#C9A84C" : "#C47B74";

  const inputStyle = { padding:"11px 14px", background:"#0E0B08", border:"1px solid #3D3428", borderRadius:9, color:"#E8E0D5", fontSize:14, outline:"none", fontFamily:"'Jost',sans-serif" };
  const labelStyle = { fontSize:11, fontWeight:600, color:"#5A504A", letterSpacing:".12em", textTransform:"uppercase" };
  const field = (lbl, name, type="text", val, onChange, ph="") => (
    <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
      <label style={labelStyle}>{lbl}</label>
      <input style={inputStyle} name={name} type={type} placeholder={ph} value={val} onChange={onChange}/>
    </div>
  );
  const btnGold  = { background:"#C9A84C", color:"#1A1410", border:"none", borderRadius:9, padding:"10px 20px", fontSize:13, fontWeight:600, cursor:"pointer", fontFamily:"'Jost',sans-serif" };
  const btnGhost = { background:"transparent", color:"#7A6E64", border:"1px solid #3D3428", borderRadius:9, padding:"10px 20px", fontSize:13, cursor:"pointer", fontFamily:"'Jost',sans-serif" };

  const s = {
    page:   { padding:"40px", minHeight:"90vh" },
    header: { marginBottom:32, display:"flex", alignItems:"flex-end", justifyContent:"space-between", flexWrap:"wrap", gap:12 },
    h2:     { fontFamily:"'Playfair Display',serif", fontSize:30, color:"#E8D5A3" },
    sub:    { fontSize:13, color:"#7A6E64", marginTop:6 },
    table:  { width:"100%", borderCollapse:"collapse", background:"#1E1914", border:"1px solid #3D3428", borderRadius:14, overflow:"hidden" },
    th:     { padding:"11px 18px", textAlign:"left", fontSize:10, fontWeight:600, color:"#5A504A", letterSpacing:".1em", textTransform:"uppercase", borderBottom:"1px solid #2E2820", background:"#181410" },
    td:     { padding:"14px 18px", borderBottom:"1px solid #1A1714", color:"#E8E0D5", verticalAlign:"middle" },
    spinner:{ width:28, height:28, borderRadius:"50%", border:"2px solid #2E2820", borderTopColor:"#C9A84C", animation:"spin .7s linear infinite", margin:"60px auto" },
  };

  return (
    <div style={s.page}>
      <style>{"@keyframes spin{to{transform:rotate(360deg)}}"}</style>
      <div style={s.header}>
        <div>
          <h2 style={s.h2}>Gestión de perfumes</h2>
          <p style={s.sub}>Administra el catálogo completo</p>
        </div>
        <button style={btnGold} onClick={() => setShowCreate(true)}>+ Nuevo perfume</button>
      </div>

      {loading ? <div style={s.spinner}/> : (
        <table style={s.table}>
          <thead>
            <tr>{["ID","Nombre","Marca","Precio","Stock","Acción"].map(c =>
              <th key={c} style={s.th}>{c}</th>
            )}</tr>
          </thead>
          <tbody>
            {perfumes.map(p => (
              <tr key={p.id}>
                <td style={{ ...s.td, fontSize:12, color:"#5A504A" }}>#{p.id}</td>
                <td style={s.td}><span style={{ fontFamily:"'Playfair Display',serif", fontSize:15 }}>{p.nombre}</span></td>
                <td style={s.td}><span style={{ display:"inline-block", padding:"2px 10px", background:"#0E0B08", border:"1px solid #3D3428", borderRadius:20, fontSize:11, color:"#7A6E64" }}>{p.marca}</span></td>
                <td style={s.td}><span style={{ fontFamily:"'Playfair Display',serif", fontSize:16, color:"#C9A84C" }}>${Number(p.precio).toFixed(2)}</span></td>
                <td style={s.td}>
                  <span style={{ display:"flex", alignItems:"center", gap:8 }}>
                    <span style={{ width:7, height:7, borderRadius:"50%", background:sColor(p.stock), flexShrink:0 }}/>
                    {p.stock} uds.
                  </span>
                </td>
                <td style={s.td}>
                  <button style={{ ...btnGhost, padding:"6px 14px", fontSize:12 }}
                    onClick={() => { setEditItem(p); setEditForm({ precio:p.precio, stock:p.stock }); }}>
                    Editar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showCreate && (
        <Modal title="Nuevo perfume" onClose={() => setShowCreate(false)}
          footer={<>
            <button style={btnGhost} onClick={() => setShowCreate(false)}>Cancelar</button>
            <button style={{ ...btnGold, opacity: saving ? 0.6 : 1 }} onClick={crear} disabled={saving}>{saving ? "Guardando…" : "Crear perfume"}</button>
          </>}>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:14 }}>
            {field("Nombre","nombre","text",form.nombre,hf,"Sauvage")}
            {field("Marca","marca","text",form.marca,hf,"Dior")}
          </div>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:14 }}>
            {field("Precio (USD)","precio","number",form.precio,hf,"120.00")}
            {field("Stock","stock","number",form.stock,hf,"15")}
          </div>
        </Modal>
      )}

      {editItem && (
        <Modal title={`Editar — ${editItem.nombre}`} sub={editItem.marca} onClose={() => setEditItem(null)}
          footer={<>
            <button style={btnGhost} onClick={() => setEditItem(null)}>Cancelar</button>
            <button style={{ ...btnGold, opacity: saving ? 0.6 : 1 }} onClick={actualizar} disabled={saving}>{saving ? "Guardando…" : "Actualizar"}</button>
          </>}>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:14 }}>
            {field("Precio (USD)","precio","number",editForm.precio,he)}
            {field("Stock","stock","number",editForm.stock,he)}
          </div>
        </Modal>
      )}
    </div>
  );
}
