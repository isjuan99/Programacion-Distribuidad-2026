# Sistema de Devoluciones — Especificación
**Fecha:** 2026-06-03  
**Proyecto:** Aroma Distribuido  
**Estado:** Aprobado por el usuario

---

## Contexto

Aroma Distribuido es una tienda de perfumería de lujo con e-commerce. El sistema de devoluciones ya tiene una estructura base (modelo, endpoints, UI básica), pero necesita completarse con:
- Flujo de estados completo (6 estados)
- Subida de fotos en la solicitud del cliente
- Instrucciones de envío del admin al cliente (dirección o etiqueta prepagada)
- Campo de número de guía por parte del cliente
- Estado `received` para que el admin confirme recepción
- Tipo de reembolso flexible (tarjeta / puntos / cambio de producto)
- Emails en cada transición de estado
- UI de seguimiento visual (timeline) para el cliente
- Panel de admin mejorado

---

## Política de Devoluciones

- **Plazo:** 30 días desde la entrega del pedido
- **Productos sin abrir:** Aceptados por cualquier motivo
- **Productos abiertos/usados:** Solo aceptados si llegaron dañados o incorrectos
- **Validación en frontend:** Si el cliente selecciona condición "Abierto" + motivo "Cambio de opinión", se bloquea el formulario con mensaje explicativo
- **Generación de guía:** El admin decide caso a caso — puede dar dirección de devolución O subir URL de etiqueta prepagada

---

## Flujo de Estados

```
PENDING ──► APPROVED ──► SHIPPED ──► RECEIVED ──► REFUNDED
   └──────► REJECTED
```

| Estado | Quién lo activa | Descripción |
|--------|-----------------|-------------|
| `pending` | Cliente | Solicitud creada, pendiente de revisión |
| `approved` | Admin | Aprobada; admin provee dirección o etiqueta |
| `rejected` | Admin | Rechazada; admin explica el motivo |
| `shipped` | Cliente | Cliente ingresó número de guía |
| `received` | Admin | Admin confirmó recepción e inspección del paquete |
| `refunded` | Admin | Reembolso procesado (tipo + monto definidos por admin) |

---

## Cambios en Base de Datos

### Tabla `returns` — campos nuevos

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `tracking_number` | String(100) | Sí | Número de guía que ingresa el cliente |
| `return_address` | String(500) | Sí | Dirección de devolución que provee el admin |
| `refund_type` | String(20) | Sí | `'card'` / `'points'` / `'exchange'` |

### Enum `ReturnStatus` — estado nuevo

Agregar `received` entre `shipped` y `refunded`.

### Migración

Nueva migración Alembic: `005_add_return_fields.py`

---

## Backend

### Endpoints existentes (se modifican)

#### `POST /returns`
- Sin cambios en firma
- El campo `images` ya existe en el modelo — el frontend ahora lo usa

#### `PUT /returns/{return_id}/status` (admin)
Agrega campos opcionales al body:
- `return_address`: String — dirección de devolución (al aprobar)
- `return_label_url`: String — URL de etiqueta (ya existe en modelo, ahora se acepta en este endpoint)
- `refund_type`: `'card' | 'points' | 'exchange'` (al reembolsar)
- Estado `received` ahora es válido

### Endpoint nuevo

#### `PUT /returns/{return_id}/tracking`
- **Auth:** Usuario autenticado (dueño de la devolución)
- **Precondición:** El return debe estar en estado `approved`
- **Body:** `{ "tracking_number": string }`
- **Efecto:** Cambia estado a `shipped`, guarda tracking_number
- **Respuesta:** `ReturnResponse` actualizado
- **Email:** Dispara "Recibimos tu número de guía" al cliente

### Emails (todos los estados)

| Trigger | Asunto | Destinatario |
|---------|--------|--------------|
| `approved` | "Devolución aprobada — instrucciones de envío" | Cliente |
| `rejected` | "Sobre tu solicitud de devolución #ORDER" | Cliente |
| `shipped` (cliente agrega guía) | "Recibimos tu número de guía" | Cliente |
| `received` | "Paquete recibido — procesando tu reembolso" | Cliente |
| `refunded` | "Reembolso procesado" | Cliente |

El email de `approved` incluye:
- Si hay `return_label_url`: botón "Descargar etiqueta"
- Si hay `return_address`: dirección formateada
- Si hay ambas: muestra las dos

---

## Frontend — Cliente (AccountPage.vue)

### Formulario de creación (mejoras)

Campo nuevo: **Condición del producto**
```
○ Sin abrir   ○ Abierto / Usado
```
Validación: si `condición = abierto` Y `motivo ∈ ['Cambio de opinión']` → mostrar:
> "Solo aceptamos devoluciones de productos abiertos si llegaron dañados o incorrectos."
y deshabilitar el botón de envío.

Campo nuevo: **Fotos** (hasta 3 imágenes, usando el endpoint `/upload/review-image` existente)

### Vista de seguimiento — Timeline por tarjeta

Cada devolución se muestra como una tarjeta expandible con:

```
[● Solicitada] ──── [○ Aprobada] ──── [○ Enviada] ──── [○ Recibida] ──── [○ Reembolsada]
```

Paso activo resaltado en dorado. Pasos completados con check verde.

**Acciones contextuales según estado:**

| Estado actual | Lo que ve el cliente |
|---------------|---------------------|
| `pending` | "Tu solicitud está siendo revisada" |
| `approved` | Dirección de envío y/o botón "Descargar etiqueta" + campo para ingresar número de guía |
| `shipped` | Número de guía ingresado + "Esperando confirmación de recepción" |
| `received` | "Paquete recibido, procesando reembolso" |
| `refunded` | Tipo de reembolso + monto + "3-5 días hábiles" |
| `rejected` | Motivo del rechazo (admin_notes) en banner rojo |

### Acción: ingresar número de guía

Cuando estado = `approved`, mostrar formulario inline:
```
[ Número de guía: _________________ ] [ Confirmar envío ]
```
Al confirmar → `PUT /returns/{id}/tracking` → tarjeta actualiza a `shipped`.

---

## Frontend — Admin (AdminReturns.vue)

### Lista mejorada

Columnas:
- ID · Pedido (con enlace) · Motivo · **Condición** · Estado · Fecha · **Guía** · Acciones

Fotos del cliente: miniaturas de 48x48px en la fila (máx 3), con lightbox al hacer clic.

### Modal de gestión (mejoras)

**Sección de fotos:** grid de imágenes 80x80px con lightbox.

**Al seleccionar estado `approved`:** aparece sección "Instrucciones de envío":
```
○ Proporcionar dirección de envío
○ Subir URL de etiqueta prepagada
○ Ambas
```
Campos condicionales según selección.

**Al seleccionar estado `received`:** campo de notas de inspección.

**Al seleccionar estado `refunded`:** aparece sección "Tipo de reembolso":
```
[ Tipo: ○ Tarjeta  ○ Puntos de lealtad  ○ Cambio de producto ]
[ Monto: ___________ COP ]
```

Si tipo = `points`: el backend debe sumar puntos al usuario automáticamente (1 punto = $10 COP de reembolso).

---

## Lógica especial: Reembolso en puntos

Cuando `refund_type = 'points'`:
1. Backend calcula puntos: `puntos = int(refund_amount / 10)`
2. Suma puntos a `user.loyalty_points`
3. Crea `LoyaltyTransaction` con `type='earned'`, `description='Reembolso por devolución #ORDER'`

---

## Archivos a crear/modificar

### Backend
| Archivo | Acción |
|---------|--------|
| `backend/alembic/versions/005_add_return_fields.py` | Crear — migración nuevos campos |
| `backend/app/models/returns.py` | Modificar — nuevos campos + estado `received` |
| `backend/app/api/returns.py` | Modificar — nuevo endpoint tracking, campos en update |
| `backend/app/schemas/returns.py` o `common.py` | Modificar — schemas actualizados |
| `backend/app/utils/email.py` | Modificar — nuevos templates de email |

### Frontend
| Archivo | Acción |
|---------|--------|
| `frontend/src/pages/AccountPage.vue` | Modificar — formulario, timeline, tracking input |
| `frontend/src/pages/admin/AdminReturns.vue` | Modificar — lista mejorada, modal mejorado |

---

## Secuencia de implementación recomendada

1. Migración de BD + modelo actualizado
2. Backend: schemas + endpoints actualizados + nuevo endpoint tracking
3. Backend: emails nuevos/modificados
4. Frontend: AccountPage — formulario mejorado + timeline + tracking
5. Frontend: AdminReturns — lista + modal mejorado
