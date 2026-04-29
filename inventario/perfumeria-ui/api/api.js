/*const BASE = "http://localhost:8000";

function headers(token) {
  const h = { "Content-Type": "application/json" };
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
}

async function handle(res) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Error en el servidor");
  }
  return res.json();
}

// ── Auth ─────────────────────────────────────────────
export const apiLogin    = (data) =>
  handle(fetch(`${BASE}/usuarios/login`,    { method: "POST", headers: headers(), body: JSON.stringify(data) }));

export const apiRegistro = (data) =>
  handle(fetch(`${BASE}/usuarios/registro`, { method: "POST", headers: headers(), body: JSON.stringify(data) }));

// ── Perfumes ─────────────────────────────────────────
export const apiGetPerfumes = () =>
  handle(fetch(`${BASE}/inventario`, { headers: headers() }));

export const apiCrearPerfume = (data, token) =>
  handle(fetch(`${BASE}/perfumes`,   { method: "POST", headers: headers(token), body: JSON.stringify(data) }));

export const apiActualizarPerfume = (id, data, token) =>
  handle(fetch(`${BASE}/perfumes/${id}`, { method: "PUT", headers: headers(token), body: JSON.stringify(data) }));

// ── Inventario ────────────────────────────────────────
export const apiGetInventario = () =>
  handle(fetch(`${BASE}/inventario`, { headers: headers() }));

// ── Órdenes ──────────────────────────────────────────
export const apiCrearOrden = (data, token) =>
  handle(fetch(`${BASE}/ordenes/`,   { method: "POST", headers: headers(token), body: JSON.stringify(data) }));

export const apiMisOrdenes = (token) =>
  handle(fetch(`${BASE}/ordenes/mis-ordenes`, { headers: headers(token) }));
*/



/*const BASE = "http://localhost:8000";

function headers(token) {
  const h = { "Content-Type": "application/json" };
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
}

async function handle(res) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Error en el servidor");
  }
  return res.json();
}

// ── Auth ─────────────────────────────────────────────
// CORREGIDO: Los endpoints correctos
export const apiLogin = (data) =>
  handle(fetch(`${BASE}/login`, { 
    method: "POST", 
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      username: data.email,
      password: data.password
    })
  }));

export const apiRegistro = (data) =>
  handle(fetch(`${BASE}/register`, { 
    method: "POST", 
    headers: headers(), 
    body: JSON.stringify({
      nombre: data.nombre,
      email: data.email,
      password: data.password
    })
  }));

// ── Perfumes ─────────────────────────────────────────
export const apiGetPerfumes = () =>
  handle(fetch(`${BASE}/inventario`, { headers: headers() }));

export const apiCrearPerfume = (data, token) =>
  handle(fetch(`${BASE}/inventario`, { 
    method: "POST", 
    headers: headers(token), 
    body: JSON.stringify(data) 
  }));

export const apiActualizarPerfume = (id, data, token) =>
  handle(fetch(`${BASE}/inventario/${id}`, { 
    method: "PUT", 
    headers: headers(token), 
    body: JSON.stringify(data) 
  }));

export const apiEliminarPerfume = (id, token) =>
  handle(fetch(`${BASE}/inventario/${id}`, { 
    method: "DELETE", 
    headers: headers(token)
  }));

// ── Inventario ────────────────────────────────────────
export const apiGetInventario = () =>
  handle(fetch(`${BASE}/inventario`, { headers: headers() }));

// ── Órdenes ──────────────────────────────────────────
export const apiCrearOrden = (data, token) =>
  handle(fetch(`${BASE}/ordenes`, { 
    method: "POST", 
    headers: headers(token), 
    body: JSON.stringify(data) 
  }));

export const apiMisOrdenes = (token) =>
  handle(fetch(`${BASE}/ordenes`, { 
    headers: headers(token) 
  }));

export const apiOrdenDetalle = (ordenId, token) =>
  handle(fetch(`${BASE}/ordenes/${ordenId}/detalle`, { 
    headers: headers(token) 
  }));*/





  const BASE = "http://localhost:8000";

function headers(token) {
  const h = { "Content-Type": "application/json" };
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
}

// ✅ CORREGIDO: handle debe recibir la promesa y esperarla
async function handle(promise) {
  try {
    const response = await promise;  // Esperar la respuesta de fetch
    
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || "Error en el servidor");
    }
    
    return await response.json();  // Retornar el JSON
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}

// ── Auth ─────────────────────────────────────────────
export const apiLogin = (data) =>
  handle(fetch(`${BASE}/login`, { 
    method: "POST", 
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      username: data.email,
      password: data.password
    })
  }));

export const apiRegistro = (data) =>
  handle(fetch(`${BASE}/register`, { 
    method: "POST", 
    headers: headers(), 
    body: JSON.stringify({
      nombre: data.nombre,
      email: data.email,
      password: data.password
    })
  }));

// ── Perfumes ─────────────────────────────────────────
export const apiGetPerfumes = () =>
  handle(fetch(`${BASE}/inventario`, { headers: headers() }));

export const apiCrearPerfume = (data, token) =>
  handle(fetch(`${BASE}/inventario`, { 
    method: "POST", 
    headers: headers(token), 
    body: JSON.stringify(data) 
  }));

export const apiActualizarPerfume = (id, data, token) =>
  handle(fetch(`${BASE}/inventario/${id}`, { 
    method: "PUT", 
    headers: headers(token), 
    body: JSON.stringify(data) 
  }));

export const apiEliminarPerfume = (id, token) =>
  handle(fetch(`${BASE}/inventario/${id}`, { 
    method: "DELETE", 
    headers: headers(token)
  }));

// ── Inventario ────────────────────────────────────────
export const apiGetInventario = () =>
  handle(fetch(`${BASE}/inventario`, { headers: headers() }));

// ── Órdenes ──────────────────────────────────────────
export const apiCrearOrden = (data, token) =>
  handle(fetch(`${BASE}/ordenes`, { 
    method: "POST", 
    headers: headers(token), 
    body: JSON.stringify(data) 
  }));

export const apiMisOrdenes = (token) =>
  handle(fetch(`${BASE}/ordenes`, { 
    headers: headers(token) 
  }));

export const apiOrdenDetalle = (ordenId, token) =>
  handle(fetch(`${BASE}/ordenes/${ordenId}/detalle`, { 
    headers: headers(token) 
  }));