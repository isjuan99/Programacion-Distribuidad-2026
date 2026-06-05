# Sistema de Devoluciones — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completar el sistema de devoluciones con flujo de 6 estados, fotos, instrucciones de envío (dirección o etiqueta), número de guía, tipo de reembolso flexible y UI de timeline visual para el cliente.

**Architecture:** Backend FastAPI + SQLAlchemy con 3 nuevos campos en tabla `returns` y estado `received`. Frontend Vue 3 con timeline visual en AccountPage y panel de admin mejorado en AdminReturns.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Vue 3, Tailwind CSS, Pinia

---

## Mapa de archivos

| Archivo | Acción |
|---------|--------|
| `backend/alembic/versions/005_add_return_fields.py` | CREAR — migración |
| `backend/app/models/returns.py` | MODIFICAR — 3 campos + estado `received` |
| `backend/app/api/returns.py` | MODIFICAR — schemas, endpoint tracking, loyalty points |
| `backend/app/utils/email.py` | MODIFICAR — función reescrita para 5 estados |
| `frontend/src/pages/AccountPage.vue` | MODIFICAR — formulario + timeline + tracking |
| `frontend/src/pages/admin/AdminReturns.vue` | MODIFICAR — tabla + modal mejorado |

---

## Task 1: Migración de base de datos

**Files:**
- Create: `backend/alembic/versions/005_add_return_fields.py`

- [ ] **Paso 1: Crear el archivo de migración**

```python
# backend/alembic/versions/005_add_return_fields.py
"""add tracking_number, return_address, refund_type to returns

Revision ID: 005_add_return_fields
Revises: 004_offers_compare_price
Create Date: 2026-06-03
"""
from alembic import op
import sqlalchemy as sa

revision = '005_add_return_fields'
down_revision = '004_offers_compare_price'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('returns', sa.Column('tracking_number', sa.String(100), nullable=True))
    op.add_column('returns', sa.Column('return_address', sa.String(500), nullable=True))
    op.add_column('returns', sa.Column('refund_type', sa.String(20), nullable=True))


def downgrade():
    op.drop_column('returns', 'refund_type')
    op.drop_column('returns', 'return_address')
    op.drop_column('returns', 'tracking_number')
```

- [ ] **Paso 2: Ejecutar la migración**

```bash
cd backend
docker compose exec backend alembic upgrade head
```

Salida esperada:
```
INFO  [alembic.runtime.migration] Running upgrade 004_offers_compare_price -> 005_add_return_fields, add tracking_number, return_address, refund_type to returns
```

- [ ] **Paso 3: Commit**

```bash
git add backend/alembic/versions/005_add_return_fields.py
git commit -m "feat(db): add tracking_number, return_address, refund_type to returns table"
```

---

## Task 2: Actualizar modelo Return

**Files:**
- Modify: `backend/app/models/returns.py`

- [ ] **Paso 1: Reemplazar el contenido del modelo**

Reemplaza el archivo completo con:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ReturnStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    shipped = "shipped"
    received = "received"
    refunded = "refunded"


class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(String(100), nullable=False)
    comments = Column(Text, nullable=True)
    images = Column(JSON, default=list)
    status = Column(String(20), default=ReturnStatus.pending.value, nullable=False)
    admin_notes = Column(Text, nullable=True)
    refund_amount = Column(Float, nullable=True)
    return_label_url = Column(String(500), nullable=True)
    tracking_number = Column(String(100), nullable=True)
    return_address = Column(String(500), nullable=True)
    refund_type = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    order = relationship("Order")
    user = relationship("User")


class StockReservation(Base):
    __tablename__ = "stock_reservations"

    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    variant = relationship("ProductVariant")
```

- [ ] **Paso 2: Commit**

```bash
git add backend/app/models/returns.py
git commit -m "feat(model): add received status and new fields to Return model"
```

---

## Task 3: Actualizar returns.py — schemas, endpoint tracking y loyalty points

**Files:**
- Modify: `backend/app/api/returns.py`

- [ ] **Paso 1: Reemplazar el archivo completo**

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.returns import Return, ReturnStatus
from app.models.order import Order, OrderStatus
from app.models.wishlist import LoyaltyTransaction
from app.utils.email import send_return_status_email

router = APIRouter(prefix="/returns", tags=["returns"])


class ReturnCreate(BaseModel):
    order_id: int
    reason: str
    comments: Optional[str] = None
    images: Optional[List[str]] = None


class ReturnStatusUpdate(BaseModel):
    status: str
    admin_notes: Optional[str] = None
    refund_amount: Optional[float] = None
    return_label_url: Optional[str] = None
    return_address: Optional[str] = None
    refund_type: Optional[str] = None  # 'card', 'points', 'exchange'


class TrackingUpdate(BaseModel):
    tracking_number: str


class ReturnResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    reason: str
    comments: Optional[str] = None
    images: Optional[List[str]] = None
    status: str
    admin_notes: Optional[str] = None
    refund_amount: Optional[float] = None
    return_label_url: Optional[str] = None
    return_address: Optional[str] = None
    tracking_number: Optional[str] = None
    refund_type: Optional[str] = None
    created_at: object
    model_config = {"from_attributes": True}


@router.post("", response_model=ReturnResponse, status_code=201)
async def create_return(
    data: ReturnCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(
        Order.id == data.order_id,
        Order.user_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order.status != OrderStatus.delivered:
        raise HTTPException(status_code=400, detail="Solo puedes solicitar devolución de pedidos entregados")

    if order.updated_at:
        deadline = order.updated_at.replace(tzinfo=None) + timedelta(days=30)
        if datetime.utcnow() > deadline:
            raise HTTPException(status_code=400, detail="El periodo de devolución de 30 días ha expirado")

    existing = db.query(Return).filter(
        Return.order_id == data.order_id,
        Return.status.in_(['pending', 'approved']),
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya tienes una solicitud de devolución activa para este pedido")

    ret = Return(
        order_id=data.order_id,
        user_id=current_user.id,
        reason=data.reason,
        comments=data.comments,
        images=data.images or [],
    )
    db.add(ret)
    db.commit()
    db.refresh(ret)
    return ret


@router.get("/my-returns", response_model=List[ReturnResponse])
async def my_returns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Return).filter(
        Return.user_id == current_user.id
    ).order_by(Return.created_at.desc()).all()


@router.get("", response_model=List[ReturnResponse])
async def admin_list_returns(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    query = db.query(Return).order_by(Return.created_at.desc())
    if status:
        query = query.filter(Return.status == status)
    return query.offset((page - 1) * per_page).limit(per_page).all()


@router.put("/{return_id}/tracking", response_model=ReturnResponse)
async def add_tracking_number(
    return_id: int,
    data: TrackingUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ret = db.query(Return).options(
        joinedload(Return.order), joinedload(Return.user)
    ).filter(
        Return.id == return_id,
        Return.user_id == current_user.id,
    ).first()
    if not ret:
        raise HTTPException(status_code=404, detail="Devolución no encontrada")
    if ret.status != ReturnStatus.approved.value:
        raise HTTPException(status_code=400, detail="Solo puedes agregar guía a devoluciones aprobadas")

    ret.tracking_number = data.tracking_number
    ret.status = ReturnStatus.shipped.value
    db.commit()
    db.refresh(ret)

    background_tasks.add_task(
        send_return_status_email,
        ret.user.email,
        ret.user.first_name,
        ret.order.order_number,
        "shipped",
        tracking_number=data.tracking_number,
    )
    return ret


@router.put("/{return_id}/status", response_model=ReturnResponse)
async def update_return_status(
    return_id: int,
    data: ReturnStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    ret = db.query(Return).options(
        joinedload(Return.order), joinedload(Return.user)
    ).filter(Return.id == return_id).first()
    if not ret:
        raise HTTPException(status_code=404, detail="Devolución no encontrada")

    valid_statuses = [s.value for s in ReturnStatus]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Válidos: {valid_statuses}")

    ret.status = data.status
    if data.admin_notes is not None:
        ret.admin_notes = data.admin_notes
    if data.refund_amount is not None:
        ret.refund_amount = data.refund_amount
    if data.return_label_url is not None:
        ret.return_label_url = data.return_label_url
    if data.return_address is not None:
        ret.return_address = data.return_address
    if data.refund_type is not None:
        ret.refund_type = data.refund_type

    # Award loyalty points when refund type is 'points'
    if data.status == ReturnStatus.refunded.value and data.refund_type == "points" and data.refund_amount:
        points_earned = int(data.refund_amount / 10)
        if points_earned > 0:
            ret.user.loyalty_points = (ret.user.loyalty_points or 0) + points_earned
            tx = LoyaltyTransaction(
                user_id=ret.user_id,
                points=points_earned,
                type="earned",
                description=f"Reembolso por devolución — Pedido #{ret.order.order_number}",
            )
            db.add(tx)

    db.commit()
    db.refresh(ret)

    if data.status in ("approved", "rejected", "received", "refunded"):
        background_tasks.add_task(
            send_return_status_email,
            ret.user.email,
            ret.user.first_name,
            ret.order.order_number,
            data.status,
            data.admin_notes,
            return_address=data.return_address,
            return_label_url=data.return_label_url,
            refund_type=data.refund_type,
            refund_amount=data.refund_amount,
        )

    return ret
```

- [ ] **Paso 2: Commit**

```bash
git add backend/app/api/returns.py
git commit -m "feat(api): add tracking endpoint, received state, loyalty refund, new fields"
```

---

## Task 4: Actualizar templates de email

**Files:**
- Modify: `backend/app/utils/email.py` — función `send_return_status_email`

- [ ] **Paso 1: Reemplazar la función `send_return_status_email`**

Localiza la función `send_return_status_email` al final del archivo y reemplázala por completo:

```python
async def send_return_status_email(
    to: str,
    first_name: str,
    order_number: str,
    return_status: str,
    admin_notes: str = None,
    tracking_number: str = None,
    return_address: str = None,
    return_label_url: str = None,
    refund_type: str = None,
    refund_amount: float = None,
):
    def _notes_block(notes):
        if not notes:
            return ""
        return f"<p style='color:#888;font-size:13px;border-left:2px solid #333;padding-left:16px;margin-top:16px;'>{notes}</p>"

    if return_status == "approved":
        title = "Devoluci&#243;n aprobada"
        color = "#22c55e"
        body = "<p style='color:#ccc;line-height:1.7;'>Tu solicitud de devoluci&#243;n ha sido aprobada. Por favor env&#237;a el producto siguiendo las instrucciones a continuaci&#243;n.</p>"
        shipping_block = ""
        if return_label_url:
            shipping_block += f"""
            <div style='background:#111;border:1px solid #333;padding:16px;margin-top:16px;'>
              <p style='color:#aaa;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin:0 0 10px;'>Etiqueta prepagada</p>
              <a href='{return_label_url}' style='display:inline-block;background:#22c55e;color:#fff;padding:10px 24px;text-decoration:none;font-size:12px;letter-spacing:2px;text-transform:uppercase;font-weight:bold;'>
                DESCARGAR ETIQUETA
              </a>
            </div>"""
        if return_address:
            shipping_block += f"""
            <div style='background:#111;border:1px solid #333;padding:16px;margin-top:12px;'>
              <p style='color:#aaa;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin:0 0 10px;'>Direcci&#243;n de env&#237;o</p>
              <p style='color:#f5f0e8;font-family:monospace;font-size:13px;white-space:pre-wrap;margin:0;'>{return_address}</p>
            </div>"""
        body += shipping_block
        body += "<p style='color:#888;font-size:13px;margin-top:20px;'>Una vez enviado, ingresa tu n&#250;mero de gu&#237;a en tu cuenta para que podamos rastrear el paquete.</p>"

    elif return_status == "rejected":
        title = "Solicitud no aprobada"
        color = "#ef4444"
        body = "<p style='color:#ccc;line-height:1.7;'>Despu&#233;s de revisar tu solicitud para el pedido #{order_number}, no podemos procesarla en este momento.</p>"

    elif return_status == "shipped":
        title = "Gu&#237;a registrada — En camino"
        color = "#3b82f6"
        body = "<p style='color:#ccc;line-height:1.7;'>Hemos registrado tu n&#250;mero de gu&#237;a. Cuando recibamos el paquete te notificaremos.</p>"
        if tracking_number:
            body += f"<div style='background:#111;border:1px solid #333;padding:16px;margin-top:16px;'><p style='color:#aaa;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin:0 0 6px;'>N&#250;mero de gu&#237;a</p><p style='color:#f5f0e8;font-family:monospace;font-size:16px;margin:0;'>{tracking_number}</p></div>"

    elif return_status == "received":
        title = "Paquete recibido"
        color = "#f59e0b"
        body = "<p style='color:#ccc;line-height:1.7;'>Hemos recibido e inspeccionado tu paquete. Estamos procesando tu reembolso.</p>"

    elif return_status == "refunded":
        title = "Reembolso procesado"
        color = "#c9a84c"
        refund_labels = {"card": "Tarjeta original", "points": "Puntos de lealtad", "exchange": "Cambio de producto"}
        refund_label = refund_labels.get(refund_type, refund_type or "")
        amount_str = f"${refund_amount:,.0f} COP" if refund_amount else ""
        body = f"<p style='color:#ccc;line-height:1.7;'>Hemos procesado tu reembolso.</p>"
        if refund_label or amount_str:
            body += f"""<div style='background:#111;border:1px solid #333;padding:16px;margin-top:16px;display:flex;gap:32px;'>"""
            if refund_label:
                body += f"<div><p style='color:#aaa;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 4px;'>Tipo</p><p style='color:#f5f0e8;font-size:14px;margin:0;'>{refund_label}</p></div>"
            if amount_str:
                body += f"<div><p style='color:#aaa;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 4px;'>Monto</p><p style='color:#c9a84c;font-size:14px;font-weight:bold;margin:0;'>{amount_str}</p></div>"
            body += "</div>"
        if refund_type != "points":
            body += "<p style='color:#888;font-size:13px;margin-top:16px;'>Puede tardar 3-5 d&#237;as h&#225;biles en reflejarse en tu cuenta.</p>"
    else:
        title = "Actualizaci&#243;n de devoluci&#243;n"
        color = "#c9a84c"
        body = "<p style='color:#ccc;line-height:1.7;'>Hay una actualizaci&#243;n en tu solicitud de devoluci&#243;n.</p>"

    html = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#f5f0e8;padding:40px;">
      <h1 style="font-size:28px;letter-spacing:8px;color:#c9a84c;margin:0 0 4px;">AROMA</h1>
      <p style="font-size:11px;letter-spacing:4px;color:#888;margin:0 0 40px;">DISTRIBUIDO</p>
      <h2 style="font-size:20px;font-weight:normal;color:{color};margin:0 0 8px;">{title}</h2>
      <p style="color:#888;margin:0 0 16px;">Pedido #{order_number}</p>
      {body}
      {_notes_block(admin_notes)}
      <a href="{settings.FRONTEND_URL}/account"
         style="display:inline-block;background:#c9a84c;color:#0a0a0a;padding:14px 36px;text-decoration:none;letter-spacing:3px;font-size:13px;font-weight:bold;margin-top:24px;">
        VER MI CUENTA
      </a>
      <p style="color:#555;font-size:11px;margin-top:40px;">&#169; 2026 Aroma-Distribuido.</p>
    </div>
    """
    await _send(to, f"Devoluci&#243;n #{order_number} — {title} | Aroma-Distribuido", html)
```

- [ ] **Paso 2: Commit**

```bash
git add backend/app/utils/email.py
git commit -m "feat(email): rewrite return emails for all 6 states with rich content"
```

---

## Task 5: AccountPage — modal de devolución mejorado

**Files:**
- Modify: `frontend/src/pages/AccountPage.vue`

- [ ] **Paso 1: Actualizar el estado JS de devoluciones**

Localiza el bloque `// Devoluciones` en el `<script setup>` (alrededor de la línea 637) y reemplázalo:

```js
// Devoluciones
const returns = ref([])
const showReturnForm = ref(false)
const returnOrderId = ref(null)
const returnForm = ref({ reason: '', comments: '', condition: 'unopened' })
const returnImages = ref([])
const returnReasons = ['Producto dañado', 'No coincide con la descripción', 'Cambio de opinión', 'Producto incorrecto recibido', 'Calidad insatisfactoria']

const RETURN_STEPS = [
  { value: 'pending',  label: 'Solicitada'  },
  { value: 'approved', label: 'Aprobada'    },
  { value: 'shipped',  label: 'Enviada'     },
  { value: 'received', label: 'Recibida'    },
  { value: 'refunded', label: 'Reembolsada' },
]

const trackingNumbers = ref({})
const trackingLoading = ref({})
```

- [ ] **Paso 2: Agregar computed `returnBlocked` después del bloque anterior**

Añade justo después de las constantes de devolución (antes de `const menuItems`):

```js
const returnBlocked = computed(() =>
  returnForm.value.condition === 'opened' &&
  returnForm.value.reason === 'Cambio de opinión'
)
```

- [ ] **Paso 3: Actualizar `returnStatusLabel` para incluir `received`**

Localiza la función `returnStatusLabel` y reemplázala:

```js
function returnStatusLabel(s) {
  return {
    pending:  'Pendiente',
    approved: 'Aprobada',
    rejected: 'Rechazada',
    shipped:  'En camino',
    received: 'Recibida',
    refunded: 'Reembolsada',
  }[s] || s
}
```

- [ ] **Paso 4: Agregar funciones helper de timeline y tracking**

Añade estas funciones junto a las demás funciones de devolución (después de `returnStatusLabel`):

```js
function returnStatusBadgeClass(s) {
  return {
    pending:  'bg-yellow-100 text-yellow-700',
    approved: 'bg-emerald-100 text-emerald-700',
    rejected: 'bg-red-100 text-red-700',
    shipped:  'bg-blue-100 text-blue-700',
    received: 'bg-amber-100 text-amber-700',
    refunded: 'bg-gray-100 text-gray-700',
  }[s] || 'bg-gray-100 text-gray-500'
}

function getStepIndex(status) {
  return RETURN_STEPS.findIndex(s => s.value === status)
}

function isStepDone(status, idx) {
  return idx < getStepIndex(status)
}

function isStepActive(status, idx) {
  return idx === getStepIndex(status)
}

function getStepClass(status, idx) {
  if (isStepDone(status, idx))  return 'bg-gold border-gold'
  if (isStepActive(status, idx)) return 'border-gold bg-white'
  return 'border-gray-300 bg-white'
}

async function handleReturnImageUpload(event) {
  const files = Array.from(event.target.files || [])
  for (const file of files) {
    if (returnImages.value.length >= 3) break
    const formData = new FormData()
    formData.append('file', file)
    try {
      const { data } = await api.post('/upload/review-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      returnImages.value.push({ preview: URL.createObjectURL(file), url: data.url })
    } catch {}
    event.target.value = ''
  }
}

function removeReturnImage(idx) {
  URL.revokeObjectURL(returnImages.value[idx].preview)
  returnImages.value.splice(idx, 1)
}

async function submitTracking(returnId) {
  const tracking = trackingNumbers.value[returnId]
  if (!tracking) return
  trackingLoading.value[returnId] = true
  try {
    await api.put(`/returns/${returnId}/tracking`, { tracking_number: tracking })
    await loadReturns()
    trackingNumbers.value[returnId] = ''
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al confirmar el envío')
  } finally {
    trackingLoading.value[returnId] = false
  }
}
```

- [ ] **Paso 5: Actualizar `submitReturn` para enviar imágenes**

Localiza la función `submitReturn` y reemplázala:

```js
async function submitReturn() {
  try {
    await api.post('/returns', {
      order_id: returnOrderId.value,
      reason: returnForm.value.reason,
      comments: returnForm.value.comments,
      images: returnImages.value.map(i => i.url),
    })
    showReturnForm.value = false
    returnForm.value = { reason: '', comments: '', condition: 'unopened' }
    returnImages.value = []
    await loadReturns()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error')
  }
}
```

- [ ] **Paso 6: Commit parcial**

```bash
git add frontend/src/pages/AccountPage.vue
git commit -m "feat(account): add return timeline helpers, tracking submit, image upload"
```

---

## Task 6: AccountPage — reemplazar tab de devoluciones y modal

**Files:**
- Modify: `frontend/src/pages/AccountPage.vue`

- [ ] **Paso 1: Reemplazar el tab `<!-- ── TAB: DEVOLUCIONES ──── -->`**

Localiza el bloque completo desde `<!-- ── TAB: DEVOLUCIONES ──────────────────────────────── -->` hasta su `</div>` de cierre (líneas ~522-546) y reemplázalo:

```html
<!-- ── TAB: DEVOLUCIONES ──────────────────────────────── -->
<div v-if="activeTab === 'returns'">
  <h2 class="font-display text-2xl text-[#111010] mb-6">Mis Devoluciones</h2>

  <div v-if="returns.length === 0" class="text-center py-16 border border-dashed border-gray-200 rounded-sm">
    <p class="text-4xl mb-4">↩️</p>
    <p class="text-gray-400 text-sm mb-1">No tienes solicitudes de devolución.</p>
    <p class="text-gray-300 text-xs">Puedes solicitarla desde un pedido entregado en la sección Pedidos.</p>
  </div>

  <div v-else class="space-y-5">
    <div v-for="ret in returns" :key="ret.id"
      class="bg-white border border-gray-200 rounded-sm shadow-sm overflow-hidden">

      <!-- Header de la tarjeta -->
      <div class="px-6 py-4 border-b border-gray-100 flex items-start justify-between gap-4">
        <div>
          <p class="text-[10px] tracking-widest uppercase text-gray-400 mb-1">
            Devolución #{{ ret.id }} · Pedido #{{ ret.order_id }}
          </p>
          <p class="text-sm font-medium text-[#111010]">{{ ret.reason }}</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(ret.created_at) }}</p>
        </div>
        <span class="text-xs px-3 py-1 rounded-full font-medium shrink-0"
          :class="returnStatusBadgeClass(ret.status)">
          {{ returnStatusLabel(ret.status) }}
        </span>
      </div>

      <!-- Timeline (solo si no está rechazada) -->
      <div v-if="ret.status !== 'rejected'" class="px-6 pt-5 pb-2">
        <div class="flex items-start">
          <template v-for="(step, idx) in RETURN_STEPS" :key="step.value">
            <div class="flex flex-col items-center shrink-0">
              <div class="w-7 h-7 rounded-full flex items-center justify-center border-2 transition-all"
                :class="getStepClass(ret.status, idx)">
                <svg v-if="isStepDone(ret.status, idx)" class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                </svg>
                <div v-else-if="isStepActive(ret.status, idx)" class="w-2 h-2 rounded-full bg-gold"></div>
              </div>
              <p class="text-[9px] mt-1.5 text-center w-14 leading-tight"
                :class="isStepActive(ret.status, idx) || isStepDone(ret.status, idx) ? 'text-gold font-medium' : 'text-gray-400'">
                {{ step.label }}
              </p>
            </div>
            <div v-if="idx < RETURN_STEPS.length - 1"
              class="flex-1 h-px mx-1 mt-3.5 transition-all"
              :class="isStepDone(ret.status, idx) ? 'bg-gold' : 'bg-gray-200'">
            </div>
          </template>
        </div>
      </div>

      <!-- Banner de rechazo -->
      <div v-if="ret.status === 'rejected'" class="mx-6 my-4 bg-red-50 border border-red-200 rounded-sm p-4">
        <p class="text-sm font-semibold text-red-700 mb-1">Solicitud rechazada</p>
        <p class="text-xs text-red-600">{{ ret.admin_notes || 'Sin motivo adicional proporcionado.' }}</p>
      </div>

      <!-- Acciones contextuales -->
      <div v-if="ret.status !== 'rejected'" class="px-6 pb-5">

        <!-- APPROVED -->
        <div v-if="ret.status === 'approved'" class="bg-emerald-50 border border-emerald-200 rounded-sm p-4 space-y-3">
          <p class="text-xs font-semibold text-emerald-800 tracking-wide uppercase">Tu devolución fue aprobada</p>
          <div v-if="ret.return_label_url">
            <p class="text-xs text-emerald-700 mb-2">Se te ha proporcionado una etiqueta de envío prepagada:</p>
            <a :href="ret.return_label_url" target="_blank"
              class="inline-flex items-center gap-1.5 text-xs bg-emerald-700 text-white px-3 py-2 rounded-sm hover:bg-emerald-800 transition-colors">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
              </svg>
              Descargar etiqueta de envío
            </a>
          </div>
          <div v-if="ret.return_address">
            <p class="text-xs text-emerald-700 mb-1">Envía el producto a esta dirección:</p>
            <p class="text-sm text-emerald-900 font-mono bg-white border border-emerald-200 px-3 py-2 rounded-sm whitespace-pre-wrap">{{ ret.return_address }}</p>
          </div>
          <div class="pt-3 border-t border-emerald-200">
            <p class="text-xs text-emerald-700 mb-2">Una vez enviado, ingresa tu número de guía:</p>
            <div class="flex gap-2">
              <input v-model="trackingNumbers[ret.id]" type="text"
                placeholder="Ej: 9400111899223379390000"
                class="flex-1 border border-emerald-300 bg-white text-[#111010] text-sm px-3 py-2 focus:outline-none focus:border-gold rounded-sm" />
              <button @click="submitTracking(ret.id)"
                :disabled="!trackingNumbers[ret.id] || trackingLoading[ret.id]"
                class="bg-gold text-white text-xs px-4 py-2 hover:bg-gold-dark transition-colors rounded-sm disabled:opacity-40">
                {{ trackingLoading[ret.id] ? '...' : 'Confirmar' }}
              </button>
            </div>
          </div>
        </div>

        <!-- SHIPPED -->
        <div v-else-if="ret.status === 'shipped'" class="bg-blue-50 border border-blue-200 rounded-sm p-4">
          <p class="text-xs font-semibold text-blue-800 tracking-wide uppercase mb-2">Producto en camino</p>
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1.5 10h11L20 8"/>
            </svg>
            <p class="text-sm text-blue-700">Guía: <span class="font-mono font-semibold">{{ ret.tracking_number }}</span></p>
          </div>
          <p class="text-xs text-blue-600 mt-2">Esperando confirmación de recepción.</p>
        </div>

        <!-- RECEIVED -->
        <div v-else-if="ret.status === 'received'" class="bg-amber-50 border border-amber-200 rounded-sm p-4">
          <p class="text-xs font-semibold text-amber-800 tracking-wide uppercase mb-1">Paquete recibido</p>
          <p class="text-xs text-amber-700">Hemos recibido tu paquete. Estamos procesando tu reembolso.</p>
        </div>

        <!-- REFUNDED -->
        <div v-else-if="ret.status === 'refunded'" class="bg-gray-50 border border-gray-200 rounded-sm p-4">
          <p class="text-xs font-semibold text-gray-700 tracking-wide uppercase mb-3">Reembolso procesado</p>
          <div class="flex items-center gap-6 flex-wrap">
            <div v-if="ret.refund_type">
              <p class="text-[10px] text-gray-400 uppercase tracking-widest mb-0.5">Tipo</p>
              <p class="text-sm font-medium text-[#111010]">
                {{ { card: 'Tarjeta original', points: 'Puntos de lealtad', exchange: 'Cambio de producto' }[ret.refund_type] || ret.refund_type }}
              </p>
            </div>
            <div v-if="ret.refund_amount">
              <p class="text-[10px] text-gray-400 uppercase tracking-widest mb-0.5">Monto</p>
              <p class="text-sm font-medium text-gold">{{ formatCOP(ret.refund_amount) }}</p>
            </div>
          </div>
          <p v-if="ret.refund_type !== 'points'" class="text-xs text-gray-400 mt-2">Puede tardar 3-5 días hábiles en reflejarse.</p>
          <p v-if="ret.admin_notes" class="text-xs text-gray-500 mt-2 italic">{{ ret.admin_notes }}</p>
        </div>

        <!-- PENDING -->
        <div v-else-if="ret.status === 'pending'" class="mt-3 text-xs text-gray-400 italic">
          Tu solicitud está siendo revisada. Te notificaremos por email en 24-48h.
        </div>
      </div>
    </div>
  </div>
</div>
```

- [ ] **Paso 2: Reemplazar el modal de devolución**

Localiza el bloque `<!-- Modal devolución -->` (líneas ~552-581) y reemplázalo:

```html
<!-- Modal devolución -->
<div v-if="showReturnForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showReturnForm = false">
  <div class="bg-white rounded-sm p-6 w-full max-w-md shadow-xl max-h-[90vh] overflow-y-auto">
    <h3 class="font-display text-xl text-[#111010] mb-5">Solicitar Devolución</h3>
    <form @submit.prevent="submitReturn" class="space-y-4">

      <!-- Condición -->
      <div>
        <label class="block text-xs text-gray-500 mb-2 uppercase tracking-widest">Condición del producto</label>
        <div class="flex gap-4">
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="radio" v-model="returnForm.condition" value="unopened" class="accent-gold" />
            <span class="text-sm text-[#111010]">Sin abrir</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="radio" v-model="returnForm.condition" value="opened" class="accent-gold" />
            <span class="text-sm text-[#111010]">Abierto / Usado</span>
          </label>
        </div>
      </div>

      <!-- Motivo -->
      <div>
        <label class="block text-xs text-gray-500 mb-1 uppercase tracking-widest">Motivo</label>
        <select v-model="returnForm.reason" required
          class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm bg-white">
          <option value="" disabled>Selecciona un motivo</option>
          <option v-for="r in returnReasons" :key="r" :value="r">{{ r }}</option>
        </select>
      </div>

      <!-- Alerta bloqueo -->
      <div v-if="returnBlocked" class="bg-amber-50 border border-amber-200 rounded-sm p-3">
        <p class="text-xs text-amber-700 font-medium">Solo aceptamos devoluciones de productos abiertos si llegaron dañados o incorrectos.</p>
      </div>

      <!-- Comentarios -->
      <div>
        <label class="block text-xs text-gray-500 mb-1 uppercase tracking-widest">Comentarios (opcional)</label>
        <textarea v-model="returnForm.comments" rows="3"
          class="w-full border border-gray-300 text-[#111010] px-3 py-2.5 text-sm focus:border-gold focus:outline-none rounded-sm resize-none"
          placeholder="Describe el problema con más detalle"/>
      </div>

      <!-- Fotos -->
      <div>
        <label class="block text-xs text-gray-500 mb-2 uppercase tracking-widest">Fotos del producto (opcional, máx. 3)</label>
        <div class="flex gap-2 flex-wrap">
          <div v-for="(img, i) in returnImages" :key="i" class="relative w-16 h-16 group shrink-0">
            <img :src="img.preview" class="w-full h-full object-cover rounded-sm border border-gray-200"/>
            <button type="button" @click="removeReturnImage(i)"
              class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity leading-none">×</button>
          </div>
          <label v-if="returnImages.length < 3"
            class="w-16 h-16 border border-dashed border-gray-300 hover:border-gold bg-gray-50 hover:bg-gold/5 flex flex-col items-center justify-center text-gray-400 hover:text-gold cursor-pointer transition-all rounded-sm shrink-0">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4"/>
            </svg>
            <span class="text-[10px] mt-0.5">Foto</span>
            <input type="file" accept="image/jpeg,image/png,image/webp" multiple class="hidden" @change="handleReturnImageUpload"/>
          </label>
        </div>
      </div>

      <div class="flex gap-3 pt-2">
        <button type="submit" :disabled="returnBlocked"
          class="flex-1 bg-gold text-white py-3 text-sm hover:bg-gold-dark transition-colors rounded-sm disabled:opacity-40">
          Enviar solicitud
        </button>
        <button type="button" @click="showReturnForm = false"
          class="px-5 border border-gray-300 text-gray-600 text-sm hover:border-gray-400 transition-colors rounded-sm">
          Cancelar
        </button>
      </div>
    </form>
  </div>
</div>
```

- [ ] **Paso 3: Commit**

```bash
git add frontend/src/pages/AccountPage.vue
git commit -m "feat(account): returns timeline cards, tracking input, photo upload in modal"
```

---

## Task 7: AdminReturns — tabla y modal mejorado

**Files:**
- Modify: `frontend/src/pages/admin/AdminReturns.vue`

- [ ] **Paso 1: Reemplazar el archivo completo**

```html
<template>
  <div class="p-6 lg:p-8 max-w-7xl mx-auto">
    <div class="mb-8">
      <h1 class="text-2xl font-light tracking-widest text-white">{{ $t('admin.returns') }}</h1>
      <p class="text-gray-500 text-sm mt-1">{{ $t('admin.returns_subtitle') }}</p>
    </div>

    <!-- Filtros de estado -->
    <div class="flex gap-1 mb-6 border-b border-gray-800 overflow-x-auto">
      <button v-for="tab in statusTabs" :key="tab.value"
        @click="activeStatus = tab.value; loadReturns()"
        class="px-4 py-2 text-sm transition-colors shrink-0"
        :class="activeStatus === tab.value
          ? 'text-[#c9a84c] border-b-2 border-[#c9a84c]'
          : 'text-gray-500 hover:text-gray-300'">
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-16 text-gray-500 text-sm">{{ $t('common.loading') }}</div>

    <!-- Tabla -->
    <div v-else-if="returns.length" class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-800">
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">ID</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">Pedido</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">Motivo</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">Fotos</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">Guía</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">Estado</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">Fecha</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">Acción</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800">
          <tr v-for="ret in returns" :key="ret.id" class="hover:bg-white/2 transition-colors">
            <td class="py-3 px-4 text-gray-400">#{{ ret.id }}</td>
            <td class="py-3 px-4 text-gray-300">#{{ ret.order_id }}</td>
            <td class="py-3 px-4 text-gray-300 max-w-[160px] truncate">{{ ret.reason }}</td>
            <td class="py-3 px-4">
              <div v-if="ret.images?.length" class="flex gap-1">
                <img v-for="(img, i) in ret.images.slice(0, 3)" :key="i"
                  :src="img" class="w-10 h-10 object-cover border border-gray-700 rounded-sm cursor-pointer hover:border-[#c9a84c] transition-colors"
                  @click="lightboxImg = img" />
              </div>
              <span v-else class="text-gray-600 text-xs">—</span>
            </td>
            <td class="py-3 px-4">
              <span v-if="ret.tracking_number" class="font-mono text-xs text-blue-400">{{ ret.tracking_number }}</span>
              <span v-else class="text-gray-600 text-xs">—</span>
            </td>
            <td class="py-3 px-4">
              <span class="text-xs px-2 py-1 rounded-sm"
                :class="{
                  'bg-yellow-500/20 text-yellow-400': ret.status === 'pending',
                  'bg-green-500/20 text-green-400':  ret.status === 'approved',
                  'bg-red-500/20 text-red-400':      ret.status === 'rejected',
                  'bg-blue-500/20 text-blue-400':    ret.status === 'shipped',
                  'bg-amber-500/20 text-amber-400':  ret.status === 'received',
                  'bg-[#c9a84c]/20 text-[#c9a84c]':  ret.status === 'refunded',
                }">
                {{ statusLabel(ret.status) }}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-500 text-xs">{{ formatDate(ret.created_at) }}</td>
            <td class="py-3 px-4">
              <button @click="openReturn(ret)"
                class="text-xs text-[#c9a84c] border border-[#c9a84c]/30 px-3 py-1 hover:bg-[#c9a84c]/10 transition-colors">
                Gestionar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center py-16 text-gray-500 text-sm">{{ $t('admin.no_returns') }}</div>

    <!-- Modal de gestión -->
    <div v-if="selectedReturn" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 px-4"
      @click.self="selectedReturn = null">
      <div class="bg-[#111] border border-gray-800 p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-white font-light text-lg">Devolución #{{ selectedReturn.id }}</h3>
          <button @click="selectedReturn = null" class="text-gray-500 hover:text-white text-xl leading-none">×</button>
        </div>

        <!-- Info del cliente -->
        <div class="space-y-4 mb-6">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-gray-500 mb-1 uppercase tracking-widest">Motivo</p>
              <p class="text-sm text-gray-200">{{ selectedReturn.reason }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 mb-1 uppercase tracking-widest">Pedido</p>
              <p class="text-sm text-gray-200">#{{ selectedReturn.order_id }}</p>
            </div>
          </div>
          <div v-if="selectedReturn.comments">
            <p class="text-xs text-gray-500 mb-1 uppercase tracking-widest">Comentarios</p>
            <p class="text-sm text-gray-400 leading-relaxed">{{ selectedReturn.comments }}</p>
          </div>
          <div v-if="selectedReturn.tracking_number">
            <p class="text-xs text-gray-500 mb-1 uppercase tracking-widest">Número de guía</p>
            <p class="text-sm font-mono text-blue-400">{{ selectedReturn.tracking_number }}</p>
          </div>
          <!-- Fotos -->
          <div v-if="selectedReturn.images?.length">
            <p class="text-xs text-gray-500 mb-2 uppercase tracking-widest">Fotos del cliente</p>
            <div class="flex gap-2 flex-wrap">
              <img v-for="(img, i) in selectedReturn.images" :key="i"
                :src="img" class="w-20 h-20 object-cover border border-gray-700 rounded-sm cursor-pointer hover:border-[#c9a84c] transition-colors"
                @click="lightboxImg = img" />
            </div>
          </div>
        </div>

        <!-- Formulario de actualización -->
        <form @submit.prevent="updateReturnStatus" class="space-y-4 border-t border-gray-800 pt-5">
          <!-- Estado -->
          <div>
            <label class="block text-xs text-gray-400 mb-1 uppercase tracking-widest">Actualizar estado</label>
            <select v-model="statusForm.status"
              class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none">
              <option value="pending">Pendiente</option>
              <option value="approved">Aprobada</option>
              <option value="rejected">Rechazada</option>
              <option value="shipped">Enviada por cliente</option>
              <option value="received">Recibida</option>
              <option value="refunded">Reembolsada</option>
            </select>
          </div>

          <!-- Notas del admin -->
          <div>
            <label class="block text-xs text-gray-400 mb-1 uppercase tracking-widest">Notas para el cliente</label>
            <textarea v-model="statusForm.admin_notes" rows="2"
              class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none resize-none"
              placeholder="Mensaje que verá el cliente..."></textarea>
          </div>

          <!-- Instrucciones de envío (cuando se aprueba) -->
          <div v-if="statusForm.status === 'approved'" class="border border-[#c9a84c]/20 bg-[#c9a84c]/5 p-4 space-y-3">
            <p class="text-xs text-[#c9a84c] uppercase tracking-widest font-medium">Instrucciones de envío</p>
            <div class="flex gap-3">
              <label class="flex items-center gap-1.5 cursor-pointer text-xs text-gray-300">
                <input type="checkbox" v-model="statusForm.include_address" class="accent-[#c9a84c]" />
                Dar dirección
              </label>
              <label class="flex items-center gap-1.5 cursor-pointer text-xs text-gray-300">
                <input type="checkbox" v-model="statusForm.include_label" class="accent-[#c9a84c]" />
                Subir etiqueta
              </label>
            </div>
            <div v-if="statusForm.include_address">
              <label class="block text-xs text-gray-400 mb-1">Dirección de devolución</label>
              <textarea v-model="statusForm.return_address" rows="3"
                class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none resize-none"
                placeholder="Calle 123 #45-67&#10;Bogotá, Colombia&#10;CP: 110111"/>
            </div>
            <div v-if="statusForm.include_label">
              <label class="block text-xs text-gray-400 mb-1">URL de la etiqueta prepagada</label>
              <input v-model="statusForm.return_label_url" type="url"
                class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"
                placeholder="https://..." />
            </div>
          </div>

          <!-- Tipo de reembolso (cuando se reembolsa) -->
          <div v-if="statusForm.status === 'refunded'" class="border border-[#c9a84c]/20 bg-[#c9a84c]/5 p-4 space-y-3">
            <p class="text-xs text-[#c9a84c] uppercase tracking-widest font-medium">Tipo de reembolso</p>
            <div class="flex gap-4">
              <label v-for="opt in refundTypes" :key="opt.value"
                class="flex items-center gap-1.5 cursor-pointer text-xs text-gray-300">
                <input type="radio" :value="opt.value" v-model="statusForm.refund_type" class="accent-[#c9a84c]" />
                {{ opt.label }}
              </label>
            </div>
            <div>
              <label class="block text-xs text-gray-400 mb-1">Monto a reembolsar (COP)</label>
              <input v-model="statusForm.refund_amount" type="number" step="1000"
                class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"
                placeholder="0" />
            </div>
            <p v-if="statusForm.refund_type === 'points' && statusForm.refund_amount"
              class="text-xs text-[#c9a84c]">
              = {{ Math.floor(statusForm.refund_amount / 10) }} puntos de lealtad
            </p>
          </div>

          <button type="submit"
            class="w-full bg-[#c9a84c] text-black py-3 text-sm tracking-widest hover:bg-[#b8943e] transition-colors font-medium">
            Guardar cambios
          </button>
        </form>
      </div>
    </div>

    <!-- Lightbox fotos -->
    <div v-if="lightboxImg" class="fixed inset-0 bg-black/90 flex items-center justify-center z-[60]"
      @click="lightboxImg = null">
      <img :src="lightboxImg" class="max-w-full max-h-[90vh] object-contain" @click.stop />
      <button @click="lightboxImg = null" class="absolute top-4 right-4 text-white hover:text-[#c9a84c] text-2xl">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../../router/api'

const { t } = useI18n()
const returns = ref([])
const loading = ref(false)
const selectedReturn = ref(null)
const activeStatus = ref('')
const lightboxImg = ref(null)

const statusForm = ref({
  status: 'pending',
  admin_notes: '',
  refund_amount: null,
  return_label_url: '',
  return_address: '',
  refund_type: 'card',
  include_address: false,
  include_label: false,
})

const refundTypes = [
  { value: 'card',     label: 'Tarjeta' },
  { value: 'points',   label: 'Puntos' },
  { value: 'exchange', label: 'Cambio' },
]

const statusTabs = [
  { label: 'Todos',        value: '' },
  { label: 'Pendientes',   value: 'pending' },
  { label: 'Aprobadas',    value: 'approved' },
  { label: 'Rechazadas',   value: 'rejected' },
  { label: 'En camino',    value: 'shipped' },
  { label: 'Recibidas',    value: 'received' },
  { label: 'Reembolsadas', value: 'refunded' },
]

function statusLabel(status) {
  return {
    pending:  'Pendiente',
    approved: 'Aprobada',
    rejected: 'Rechazada',
    shipped:  'En camino',
    received: 'Recibida',
    refunded: 'Reembolsada',
  }[status] || status
}

async function loadReturns() {
  loading.value = true
  try {
    const params = activeStatus.value ? `?status=${activeStatus.value}` : ''
    const { data } = await api.get(`/returns${params}`)
    returns.value = data
  } catch {
    returns.value = []
  } finally {
    loading.value = false
  }
}

function openReturn(ret) {
  selectedReturn.value = ret
  statusForm.value = {
    status:         ret.status,
    admin_notes:    ret.admin_notes || '',
    refund_amount:  ret.refund_amount || null,
    return_label_url: ret.return_label_url || '',
    return_address: ret.return_address || '',
    refund_type:    ret.refund_type || 'card',
    include_address: !!ret.return_address,
    include_label:   !!ret.return_label_url,
  }
}

async function updateReturnStatus() {
  try {
    const payload = {
      status:      statusForm.value.status,
      admin_notes: statusForm.value.admin_notes || null,
      refund_amount:    statusForm.value.refund_amount || null,
      refund_type:      statusForm.value.status === 'refunded' ? statusForm.value.refund_type : null,
      return_address:   statusForm.value.include_address ? statusForm.value.return_address : null,
      return_label_url: statusForm.value.include_label   ? statusForm.value.return_label_url : null,
    }
    await api.put(`/returns/${selectedReturn.value.id}/status`, payload)
    selectedReturn.value = null
    await loadReturns()
  } catch (e) {
    alert(e.response?.data?.detail || t('common.error'))
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(loadReturns)
</script>
```

- [ ] **Paso 2: Commit**

```bash
git add frontend/src/pages/admin/AdminReturns.vue
git commit -m "feat(admin): returns table with photos/tracking, modal with shipping + refund type"
```

---

## Verificación final

- [ ] **Verificar flujo completo como cliente:**
  1. Ir a `/account` → Pedidos → seleccionar un pedido entregado → "Solicitar Devolución"
  2. Seleccionar condición "Abierto" + motivo "Cambio de opinión" → confirmar que el botón queda bloqueado
  3. Cambiar a motivo "Producto dañado" → verificar que el formulario se habilita
  4. Subir una foto → confirmar que aparece la miniatura
  5. Enviar solicitud → ir al tab "Devoluciones" → confirmar que aparece con timeline en paso "Solicitada"

- [ ] **Verificar flujo como admin:**
  1. Ir a `/admin/returns`
  2. Abrir la devolución → cambiar estado a "Aprobada" → activar "Dar dirección" → escribir dirección → guardar
  3. Volver al cliente en `/account` → confirmar que el paso "Aprobada" está activo y aparece la dirección
  4. Ingresar número de guía → confirmar cambio a "Enviada"
  5. Admin: cambiar a "Recibida" → guardar
  6. Admin: cambiar a "Reembolsada" → tipo "Puntos" → monto 50000 → confirmar que muestra "= 5000 puntos"
  7. Cliente: verificar tab "Puntos de Lealtad" → confirmar que aparecen los puntos

- [ ] **Commit final**

```bash
git add -A
git commit -m "feat: complete returns system — 6-state flow, tracking, photos, refund types"
```
