import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";

export default function AdminOrdenesPage() {
  const { user }                  = useAuth();
  const [ordenes, setOrdenes]     = useState([]);
  const [loading, setLoading]     = useState(true);
  const [filtro, setFiltro]       = useState("todas");

  useEffect(() => {
    fetch("http://localhost:8000/ordenes/todas", {
      headers: { Authorization: `Bearer ${user?.access_token}` },
    })
      .then(r => r.json())
      .then(setOrdenes)
      .catch(() => setOrdenes([
        { orden_id:1, usuario_nombre:"Juan Camilo", total:265, estado:"confirmada", creado_en:"2025-03-20T10:30:00" },
        { orden_id:2, usuario_nombre:"María López",  total:150, estado:"entregada",  creado_en:"2025-03-19T14:15:00" },
        { orden_id:3, usuario_nombre:"Carlos Ríos",  total:95,  estado:"pendiente",  creado_en:"2025-03-18T09:00:00" },
      ]))
      .finally(() => setLoading(false));
  }, []);

  const estadoStyle = (e) => ({
    confirmada: { bg:"rgba(201,168,76,.12)",  color:"#C9A84C", border:"rgba(201,168,76,.3)"  },
    entregada:  { bg:"rgba(122,140,110,.12)", color:"#7A8C6E", border:"rgba(122,140,110,.3)" },
    pendiente:  { bg:"rgba(196,123,116,.12)", color:"#C47B74", border:"rgba(196,123,116,.3)" },
  }[e] || { bg:"#1E1914", color:"#7A6E64", border:"#3D3428" });

  const filtrados = filtro === "todas" ? ordenes : ordenes.filter(o => o.estado === filtro);

  const totalIngresos = ordenes.filter(o => o.estado !== "pendiente").reduce((s,o) => s + Number(o.total), 0);

  const s = {
    page:    { padding:"40px", minHeight:"90vh" },
    h2:      { fontFamily:"'Playfair Display',serif", fontSize:30, color:"#E8D5A3", marginBottom:6 },
    sub:     { fontSize:13, color:"#7A6E64", marginBottom:30 },
    statsRow:{ display:"flex", gap:14, marginBottom:28, flexWrap:"wrap" },
    statBox: (a) => ({ background:"#1E1914", border:"1px solid #3D3428", borderTop:`3px solid ${a}`, borderRadius:12, padding:"16px 22px", flex:1, minWidth:140 }),
    sLabel:  { fontSize:9, fontWeight:600, color:"#5A504A", letterSpacing:".12em", textTransform:"uppercase", marginBottom:8 },
    sVal:    { fontFamily:"'Playfair Display',serif", fontSize:28, color:"#E8D5A3" },
    filterRow:{ display:"flex", gap:8, marginBottom:18 },
    fBtn: (a) => ({
      background: a ? "rgba(201,168,76,.12)" : "transparent",
      border:     a ? "1px solid rgba(201,168,76,.3)" : "1px solid #3D3428",
      color:      a ? "#C9A84C" : "#7A6E64",
      borderRadius:8, padding:"7px 16px", fontSize:12, fontWeight:500,
      cursor:"pointer", fontFamily:"'Jost',sans-serif",
    }),
    table:   { width:"100%", borderCollapse:"collapse", background:"#1E1914", border:"1px solid #3D3428", borderRadius:14, overflow:"hidden" },
    th:      { padding:"11px 18px", textAlign:"left", fontSize:10, fontWeight:600, color:"#5A504A", letterSpacing:".1em", textTransform:"uppercase", borderBottom:"1px solid #2E2820", background:"#181410" },
    td:      { padding:"15px 18px", borderBottom:"1px solid #1A1714", color:"#E8E0D5", verticalAlign:"middle" },
    spinner: { width:28, height:28, borderRadius:"50%", border:"2px solid #2E2820", borderTopColor:"#C9A84C", animation:"spin .7s linear infinite", margin:"60px auto" },
  };

  const pill = (estado) => {
    const c = estadoStyle(estado);
    return { display:"inline-block", padding:"3px 12px", borderRadius:20, fontSize:10, fontWeight:600, letterSpacing:".08em", textTransform:"uppercase", background:c.bg, color:c.color, border:`1px solid ${c.border}` };
  };

  return (
    <div style={s.page}>
      <style>{"@keyframes spin{to{transform:rotate(360deg)}}"}</style>
      <h2 style={s.h2}>Órdenes</h2>
      <p style={s.sub}>Gestión de pedidos de clientes</p>

      <div style={s.statsRow}>
        {[
          { l:"Total órdenes",   v:ordenes.length,                                                    a:"#C9A84C" },
          { l:"Entregadas",      v:ordenes.filter(o=>o.estado==="entregada").length,                   a:"#7A8C6E" },
          { l:"Pendientes",      v:ordenes.filter(o=>o.estado==="pendiente").length,                   a:"#C47B74" },
          { l:"Ingresos",        v:`$${totalIngresos.toLocaleString("en-US",{maximumFractionDigits:0})}`, a:"#9A84C4" },
        ].map(({ l, v, a }) => (
          <div key={l} style={s.statBox(a)}>
            <div style={s.sLabel}>{l}</div>
            <div style={s.sVal}>{v}</div>
          </div>
        ))}
      </div>

      <div style={s.filterRow}>
        {["todas","confirmada","entregada","pendiente"].map(f => (
          <button key={f} style={s.fBtn(filtro===f)} onClick={() => setFiltro(f)}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading ? <div style={s.spinner}/> : (
        <table style={s.table}>
          <thead>
            <tr>{["Orden","Cliente","Fecha","Total","Estado"].map(c => <th key={c} style={s.th}>{c}</th>)}</tr>
          </thead>
          <tbody>
            {filtrados.map(o => (
              <tr key={o.orden_id}>
                <td style={{ ...s.td, fontSize:12, color:"#5A504A" }}>#{o.orden_id}</td>
                <td style={s.td}><span style={{ fontFamily:"'Playfair Display',serif", fontSize:15 }}>{o.usuario_nombre || `Usuario #${o.usuario_id}`}</span></td>
                <td style={{ ...s.td, fontSize:12, color:"#7A6E64" }}>
                  {new Date(o.creado_en).toLocaleDateString("es-CO",{ year:"numeric", month:"short", day:"numeric" })}
                </td>
                <td style={s.td}><span style={{ fontFamily:"'Playfair Display',serif", fontSize:17, color:"#C9A84C" }}>${Number(o.total).toFixed(2)}</span></td>
                <td style={s.td}><span style={pill(o.estado)}>{o.estado}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!loading && filtrados.length === 0 && (
        <div style={{ textAlign:"center", padding:"50px 20px", color:"#5A504A", fontSize:14 }}>
          No hay órdenes con estado "{filtro}".
        </div>
      )}
    </div>
  );
}
