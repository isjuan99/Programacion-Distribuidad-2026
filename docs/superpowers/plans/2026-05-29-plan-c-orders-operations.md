# Plan C — Orders & Operations Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement order success/confirmation page with email (Feature 6), shipping tracking with email notification (Feature 7), returns/RMA workflow (Feature 8), stock reservation during checkout (Feature 18), and export orders to CSV/Excel from admin (Feature 23).

**Architecture:** New models: `Return` (RMA), `StockReservation`. New email templates in `email.py`. New API routers: `returns.py`. Extended `orders.py` for tracking, export. New frontend pages: `OrderSuccessPage.vue`, `AdminReturns.vue`. Extended `AccountPage.vue` for returns/tracking. Extended `AdminOrders.vue` for tracking input and export.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, aiosmtplib (email), openpyxl (Excel export), Python `csv` module, Vue 3 Composition API, Pinia, Tailwind CSS

---

## File Map

**New backend files:**
- `backend/alembic/versions/003_orders_operations.py` — migration
- `backend/app/models/returns.py` — Return/RMA model, StockReservation model
- `backend/app/api/returns.py` — Returns CRUD endpoints

**Modified backend files:**
- `backend/app/models/order.py` — add tracking_number, tracking_company, tracking_url to Order
- `backend/app/api/orders.py` — add tracking endpoint, export endpoint
- `backend/app/utils/email.py` — add order confirmation, tracking, return status email templates
- `backend/app/main.py` — register returns_router
- `backend/requirements.txt` — add openpyxl

**New frontend files:**
- `frontend/src/pages/OrderSuccessPage.vue`
- `frontend/src/pages/admin/AdminReturns.vue`

**Modified frontend files:**
- `frontend/src/pages/CheckoutPage.vue` — after order created, redirect to /order/success/{id}
- `frontend/src/pages/AccountPage.vue` — add Returns tab, add tracking display in order detail
- `frontend/src/pages/admin/AdminOrders.vue` — add tracking form, export button
- `frontend/src/router/index.js` — add /order/success/:id route, /admin/returns route
- `frontend/src/locales/es.json` — new keys
- `frontend/src/locales/en.json` — new keys

---

## Task 1: Migration — Tracking, Returns, Stock Reservation

**Files:**
- Create: `backend/alembic/versions/003_orders_operations.py`

- [ ] **Step 1: Create migration**

```python
"""add tracking fields to orders, returns table, stock_reservations table

Revision ID: 003_orders_operations
Revises: 002_product_features
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa

revision = '003_orders_operations'
down_revision = '002_product_features'
branch_labels = None
depends_on = None


def upgrade():
    # Tracking fields on orders
    op.add_column('orders', sa.Column('tracking_number', sa.String(100), nullable=True))
    op.add_column('orders', sa.Column('tracking_company', sa.String(100), nullable=True))
    op.add_column('orders', sa.Column('tracking_url', sa.String(500), nullable=True))

    # Returns table
    op.create_table(
        'returns',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reason', sa.String(100), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('refund_amount', sa.Float(), nullable=True),
        sa.Column('return_label_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Stock reservations table
    op.create_table(
        'stock_reservations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('variant_id', sa.Integer(), sa.ForeignKey('product_variants.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(255), nullable=False, index=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('stock_reservations')
    op.drop_table('returns')
    op.drop_column('orders', 'tracking_url')
    op.drop_column('orders', 'tracking_company')
    op.drop_column('orders', 'tracking_number')
```

- [ ] **Step 2: Run migration**

```bash
cd backend
alembic upgrade head
```

Expected: `Running upgrade 002_product_features -> 003_orders_operations`

- [ ] **Step 3: Commit**

```bash
git add backend/alembic/versions/003_orders_operations.py
git commit -m "feat: migration — tracking fields on orders, returns table, stock_reservations table"
```

---

## Task 2: Update Order Model with Tracking Fields

**Files:**
- Modify: `backend/app/models/order.py`

- [ ] **Step 1: Add tracking columns to Order class**

In `backend/app/models/order.py`, inside the `Order` class add after `notes`:

```python
    tracking_number = Column(String(100), nullable=True)
    tracking_company = Column(String(100), nullable=True)
    tracking_url = Column(String(500), nullable=True)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/order.py
git commit -m "feat: add tracking_number, tracking_company, tracking_url to Order model"
```

---

## Task 3: New Models — Returns & StockReservation

**Files:**
- Create: `backend/app/models/returns.py`

- [ ] **Step 1: Create returns.py**

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ReturnStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    shipped = "shipped"
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

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/returns.py
git commit -m "feat: Return (RMA) and StockReservation models"
```

---

## Task 4: Email Templates — Order Confirmation, Tracking, Return Status

**Files:**
- Modify: `backend/app/utils/email.py`

- [ ] **Step 1: Add three new email functions**

Append to `backend/app/utils/email.py`:

```python

async def send_order_confirmation_email(to: str, first_name: str, order_number: str, items: list, total: float, shipping_address: str):
    items_html = "".join([
        f"""<tr>
          <td style="padding:8px 0;border-bottom:1px solid #1a1a1a;color:#ccc;font-size:14px;">{item['product_name']} — {item['size_ml']}ml</td>
          <td style="padding:8px 0;border-bottom:1px solid #1a1a1a;color:#ccc;font-size:14px;text-align:center;">{item['quantity']}</td>
          <td style="padding:8px 0;border-bottom:1px solid #1a1a1a;color:#c9a84c;font-size:14px;text-align:right;">${item['total_price']:.2f}</td>
        </tr>"""
        for item in items
    ])
    track_link = f"{settings.FRONTEND_URL}/account"
    html = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#f5f0e8;padding:40px;">
      <h1 style="font-size:28px;letter-spacing:8px;color:#c9a84c;margin:0 0 4px;">AROMA</h1>
      <p style="font-size:11px;letter-spacing:4px;color:#888;margin:0 0 40px;">DISTRIBUIDO</p>
      <h2 style="font-size:20px;font-weight:normal;color:#fff;margin:0 0 8px;">¡Gracias por tu pedido, {first_name}!</h2>
      <p style="color:#888;margin:0 0 32px;">Hemos recibido tu pedido y está siendo procesado.</p>
      <div style="background:#111;border:1px solid #222;padding:20px;margin-bottom:24px;">
        <p style="color:#888;font-size:12px;letter-spacing:3px;margin:0 0 4px;">NÚMERO DE PEDIDO</p>
        <p style="color:#c9a84c;font-size:20px;letter-spacing:2px;margin:0;">#{order_number}</p>
      </div>
      <table style="width:100%;border-collapse:collapse;margin-bottom:24px;">
        <thead>
          <tr>
            <th style="text-align:left;font-size:11px;letter-spacing:3px;color:#666;padding-bottom:12px;">PRODUCTO</th>
            <th style="text-align:center;font-size:11px;letter-spacing:3px;color:#666;padding-bottom:12px;">CANT.</th>
            <th style="text-align:right;font-size:11px;letter-spacing:3px;color:#666;padding-bottom:12px;">PRECIO</th>
          </tr>
        </thead>
        <tbody>{items_html}</tbody>
        <tfoot>
          <tr>
            <td colspan="2" style="padding-top:16px;color:#fff;font-size:16px;letter-spacing:2px;">TOTAL</td>
            <td style="padding-top:16px;color:#c9a84c;font-size:16px;text-align:right;">${total:.2f}</td>
          </tr>
        </tfoot>
      </table>
      <div style="background:#111;border:1px solid #222;padding:16px;margin-bottom:32px;">
        <p style="color:#888;font-size:11px;letter-spacing:3px;margin:0 0 8px;">DIRECCIÓN DE ENVÍO</p>
        <p style="color:#ccc;font-size:14px;margin:0;white-space:pre-line;">{shipping_address}</p>
      </div>
      <a href="{track_link}"
         style="display:inline-block;background:#c9a84c;color:#0a0a0a;padding:16px 40px;text-decoration:none;letter-spacing:3px;font-size:13px;font-weight:bold;">
        SEGUIR MI PEDIDO
      </a>
      <p style="color:#555;font-size:11px;margin-top:40px;">© 2026 Aroma-Distribuido.</p>
    </div>
    """
    await _send(to, f"Confirmación de pedido #{order_number} — Aroma-Distribuido", html)


async def send_tracking_email(to: str, first_name: str, order_number: str, tracking_number: str, tracking_company: str, tracking_url: str = None):
    track_section = ""
    if tracking_url:
        track_section = f"""
        <a href="{tracking_url}"
           style="display:inline-block;background:#c9a84c;color:#0a0a0a;padding:14px 36px;text-decoration:none;letter-spacing:3px;font-size:13px;font-weight:bold;margin-top:16px;">
          RASTREAR MI PAQUETE
        </a>"""
    html = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#f5f0e8;padding:40px;">
      <h1 style="font-size:28px;letter-spacing:8px;color:#c9a84c;margin:0 0 4px;">AROMA</h1>
      <p style="font-size:11px;letter-spacing:4px;color:#888;margin:0 0 40px;">DISTRIBUIDO</p>
      <div style="text-align:center;margin-bottom:32px;">
        <div style="width:64px;height:64px;background:#c9a84c20;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:28px;">📦</div>
      </div>
      <h2 style="font-size:20px;font-weight:normal;color:#fff;text-align:center;margin:0 0 8px;">¡Tu pedido ha sido enviado, {first_name}!</h2>
      <p style="color:#888;text-align:center;margin:0 0 32px;">Tu pedido #{order_number} está en camino.</p>
      <div style="background:#111;border:1px solid #222;padding:20px;margin-bottom:24px;">
        <div style="margin-bottom:12px;">
          <p style="color:#888;font-size:11px;letter-spacing:3px;margin:0 0 4px;">EMPRESA DE ENVÍO</p>
          <p style="color:#fff;font-size:16px;margin:0;">{tracking_company}</p>
        </div>
        <div>
          <p style="color:#888;font-size:11px;letter-spacing:3px;margin:0 0 4px;">NÚMERO DE TRACKING</p>
          <p style="color:#c9a84c;font-size:18px;letter-spacing:2px;margin:0;">{tracking_number}</p>
        </div>
      </div>
      {track_section}
      <p style="color:#555;font-size:11px;margin-top:40px;">© 2026 Aroma-Distribuido.</p>
    </div>
    """
    await _send(to, f"Tu pedido #{order_number} ha sido enviado — Aroma-Distribuido", html)


async def send_return_status_email(to: str, first_name: str, order_number: str, return_status: str, admin_notes: str = None):
    status_messages = {
        "approved": ("Tu solicitud ha sido aprobada", "Hemos aprobado tu solicitud de devolución. Te contactaremos con las instrucciones de envío.", "#22c55e"),
        "rejected": ("Solicitud no aprobada", "Después de revisar tu solicitud, no podemos procesarla en este momento.", "#ef4444"),
        "refunded": ("Reembolso procesado", "Hemos procesado tu reembolso. Debería reflejarse en tu cuenta en 3-5 días hábiles.", "#c9a84c"),
    }
    title, message, color = status_messages.get(return_status, ("Actualización de devolución", "Hay una actualización en tu solicitud.", "#c9a84c"))
    notes_section = f"<p style='color:#888;font-size:14px;border-left:2px solid #333;padding-left:16px;margin-top:16px;'>{admin_notes}</p>" if admin_notes else ""
    html = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#f5f0e8;padding:40px;">
      <h1 style="font-size:28px;letter-spacing:8px;color:#c9a84c;margin:0 0 4px;">AROMA</h1>
      <p style="font-size:11px;letter-spacing:4px;color:#888;margin:0 0 40px;">DISTRIBUIDO</p>
      <h2 style="font-size:20px;font-weight:normal;color:{color};margin:0 0 8px;">{title}</h2>
      <p style="color:#888;margin:0 0 16px;">Pedido #{order_number}</p>
      <p style="color:#ccc;line-height:1.7;margin:0 0 16px;">{message}</p>
      {notes_section}
      <a href="{settings.FRONTEND_URL}/account"
         style="display:inline-block;background:#c9a84c;color:#0a0a0a;padding:14px 36px;text-decoration:none;letter-spacing:3px;font-size:13px;font-weight:bold;margin-top:24px;">
        VER MI CUENTA
      </a>
      <p style="color:#555;font-size:11px;margin-top:40px;">© 2026 Aroma-Distribuido.</p>
    </div>
    """
    await _send(to, f"Actualización de devolución — Aroma-Distribuido", html)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/utils/email.py
git commit -m "feat: order confirmation, tracking notification, return status email templates"
```

---

## Task 5: Update Orders API — Tracking, Export, Confirmation Endpoint

**Files:**
- Modify: `backend/app/api/orders.py`
- Modify: `backend/app/schemas/order.py`
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Update OrderResponse schema to include tracking**

In `backend/app/schemas/order.py`, add to `OrderResponse`:

```python
    tracking_number: Optional[str] = None
    tracking_company: Optional[str] = None
    tracking_url: Optional[str] = None
```

Also add a new schema:

```python
class TrackingUpdate(BaseModel):
    tracking_number: str
    tracking_company: str
    tracking_url: Optional[str] = None
```

- [ ] **Step 2: Add tracking endpoint and export endpoint to orders.py**

Add these imports to `backend/app/api/orders.py`:

```python
from fastapi.responses import StreamingResponse
import io, csv
from app.schemas.order import TrackingUpdate
from app.utils.email import send_order_confirmation_email, send_tracking_email
```

Add these new endpoints to `backend/app/api/orders.py`:

```python

@router.put("/{order_id}/tracking", response_model=OrderResponse)
async def update_tracking(
    order_id: int,
    data: TrackingUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    order.tracking_number = data.tracking_number
    order.tracking_company = data.tracking_company
    order.tracking_url = data.tracking_url
    order.status = OrderStatus.shipped
    db.commit()
    db.refresh(order)
    # Send tracking email to customer
    if order.shipping_email:
        background_tasks.add_task(
            send_tracking_email,
            order.shipping_email,
            order.shipping_first_name,
            order.order_number,
            data.tracking_number,
            data.tracking_company,
            data.tracking_url,
        )
    return OrderResponse.model_validate(order)


@router.get("/{order_id}/confirmation", response_model=OrderResponse)
async def get_order_confirmation(
    order_id: int,
    db: Session = Depends(get_db),
):
    """Public endpoint for order success page — no auth required, uses order ID."""
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return OrderResponse.model_validate(order)


@router.get("/export")
async def export_orders(
    format: str = Query("csv", regex="^(csv|excel)$"),
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    from datetime import datetime as dt
    query = db.query(Order).options(joinedload(Order.items)).order_by(Order.created_at.desc())
    if status:
        query = query.filter(Order.status == status)
    if date_from:
        try:
            query = query.filter(Order.created_at >= dt.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Order.created_at <= dt.fromisoformat(date_to))
        except ValueError:
            pass
    orders = query.all()

    rows = []
    for o in orders:
        products_str = "; ".join([f"{i.product_name} ({i.size_ml}ml) x{i.quantity}" for i in o.items])
        rows.append([
            o.order_number,
            o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "",
            f"{o.shipping_first_name} {o.shipping_last_name}",
            o.shipping_email,
            products_str,
            o.subtotal,
            o.tax,
            o.shipping_cost,
            o.discount,
            o.total,
            o.payment_method or "",
            o.status.value if o.status else "",
            o.tracking_number or "",
            o.tracking_company or "",
            f"{o.shipping_address}, {o.shipping_city}, {o.shipping_postal_code}, {o.shipping_country}",
        ])

    headers = [
        "Orden", "Fecha", "Cliente", "Email", "Productos",
        "Subtotal", "Impuestos", "Envío", "Descuento", "Total",
        "Método Pago", "Estado", "Tracking", "Empresa Envío", "Dirección"
    ]
    from datetime import date
    filename = f"ordenes_aroma_{date.today().strftime('%Y%m%d')}"

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8-sig")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
        )
    else:
        # Excel
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Órdenes"
        gold_fill = PatternFill(start_color="C9A84C", end_color="C9A84C", fill_type="solid")
        bold_font = Font(bold=True, color="000000")
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.fill = gold_fill
            cell.font = bold_font
            cell.alignment = Alignment(horizontal="center")
        for row_idx, row in enumerate(rows, 2):
            for col_idx, value in enumerate(row, 1):
                ws.cell(row=row_idx, column=col_idx, value=value)
        # Auto-width
        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"},
        )
```

Also update `create_order` in `orders.py` to send confirmation email after creating the order. Add inside `create_order`, after `db.refresh(order)`:

```python
    # Send order confirmation email
    items_for_email = [
        {"product_name": i.product_name, "size_ml": i.size_ml, "quantity": i.quantity, "total_price": i.total_price}
        for i in order.items
    ]
    shipping_addr = f"{order.shipping_address}\n{order.shipping_city}, {order.shipping_postal_code}\n{order.shipping_country}"
    background_tasks.add_task(
        send_order_confirmation_email,
        order.shipping_email,
        order.shipping_first_name,
        order.order_number,
        items_for_email,
        order.total,
        shipping_addr,
    )
```

Update the `create_order` signature to include `BackgroundTasks`:

```python
async def create_order(
    data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
```

- [ ] **Step 3: Add openpyxl to requirements**

Add to `backend/requirements.txt`:
```
openpyxl==3.1.2
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/orders.py backend/app/schemas/order.py backend/requirements.txt
git commit -m "feat: tracking endpoint, order confirmation endpoint, CSV/Excel export, confirmation email on order create"
```

---

## Task 6: Returns API

**Files:**
- Create: `backend/app/api/returns.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Create returns router**

Create `backend/app/api/returns.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form, UploadFile, File, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.returns import Return, ReturnStatus
from app.models.order import Order, OrderStatus
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

    # Check 30-day window
    from datetime import datetime, timedelta
    if order.updated_at and (datetime.utcnow() - order.updated_at.replace(tzinfo=None)) > timedelta(days=30):
        raise HTTPException(status_code=400, detail="El periodo de devolución de 30 días ha expirado")

    # Check no existing pending/approved return
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
    return db.query(Return).filter(Return.user_id == current_user.id).order_by(Return.created_at.desc()).all()


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


@router.put("/{return_id}/status", response_model=ReturnResponse)
async def update_return_status(
    return_id: int,
    data: ReturnStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    ret = db.query(Return).options(joinedload(Return.order), joinedload(Return.user)).filter(
        Return.id == return_id
    ).first()
    if not ret:
        raise HTTPException(status_code=404, detail="Devolución no encontrada")

    valid_statuses = [s.value for s in ReturnStatus]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Válidos: {valid_statuses}")

    ret.status = data.status
    if data.admin_notes:
        ret.admin_notes = data.admin_notes
    if data.refund_amount is not None:
        ret.refund_amount = data.refund_amount
    if data.return_label_url:
        ret.return_label_url = data.return_label_url

    db.commit()
    db.refresh(ret)

    # Send email notification to customer
    if data.status in ("approved", "rejected", "refunded"):
        background_tasks.add_task(
            send_return_status_email,
            ret.user.email,
            ret.user.first_name,
            ret.order.order_number,
            data.status,
            data.admin_notes,
        )

    return ret
```

- [ ] **Step 2: Register in main.py**

In `backend/app/main.py`, add:

```python
from app.api.returns import router as returns_router
# ...
app.include_router(returns_router, prefix="/api/v1")
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/returns.py backend/app/main.py
git commit -m "feat: returns/RMA API — create, list, admin status update with email notifications"
```

---

## Task 7: Frontend — OrderSuccessPage

**Files:**
- Create: `frontend/src/pages/OrderSuccessPage.vue`
- Modify: `frontend/src/router/index.js`
- Modify: `frontend/src/pages/CheckoutPage.vue`

- [ ] **Step 1: Create OrderSuccessPage.vue**

Create `frontend/src/pages/OrderSuccessPage.vue`:

```vue
<template>
  <div class="min-h-screen bg-[#0a0a0a] py-20 px-4">
    <div class="max-w-2xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-20">
        <div class="w-12 h-12 mx-auto border-2 border-[#c9a84c] border-t-transparent rounded-full animate-spin"></div>
      </div>

      <template v-else-if="order">
        <!-- Success animation -->
        <div class="text-center mb-12">
          <div class="w-24 h-24 mx-auto bg-[#c9a84c]/10 rounded-full flex items-center justify-center mb-6 animate-bounce-once">
            <svg class="w-12 h-12 text-[#c9a84c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <h1 class="text-3xl font-light text-white tracking-widest mb-3">{{ $t('order_success.title') }}</h1>
          <p class="text-gray-400">{{ $t('order_success.subtitle') }}</p>
        </div>

        <!-- Order number card -->
        <div class="border border-[#c9a84c]/30 bg-[#c9a84c]/5 p-6 text-center mb-8">
          <p class="text-xs tracking-[4px] text-gray-400 mb-2">{{ $t('order_success.order_number') }}</p>
          <p class="text-2xl tracking-widest text-[#c9a84c] font-light">#{{ order.order_number }}</p>
          <p class="text-sm text-gray-500 mt-2">{{ $t('order_success.email_sent', { email: order.shipping_email }) }}</p>
        </div>

        <!-- Order items -->
        <div class="border border-gray-800 mb-6">
          <div class="border-b border-gray-800 px-6 py-4">
            <h2 class="text-sm tracking-widest text-white uppercase">{{ $t('order_success.your_order') }}</h2>
          </div>
          <div class="divide-y divide-gray-800">
            <div
              v-for="item in order.items"
              :key="item.id"
              class="flex items-center justify-between px-6 py-4 gap-4"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm text-white truncate">{{ item.product_name }}</p>
                <p class="text-xs text-gray-500">{{ item.size_ml }}ml · {{ $t('common.qty') }}: {{ item.quantity }}</p>
              </div>
              <p class="text-sm text-[#c9a84c] shrink-0">${{ item.total_price.toFixed(2) }}</p>
            </div>
          </div>
          <!-- Totals -->
          <div class="border-t border-gray-800 px-6 py-4 space-y-2">
            <div class="flex justify-between text-sm text-gray-400">
              <span>{{ $t('cart.subtotal') }}</span>
              <span>${{ order.subtotal.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-sm text-gray-400">
              <span>{{ $t('cart.shipping') }}</span>
              <span>{{ order.shipping_cost === 0 ? $t('common.free') : `$${order.shipping_cost.toFixed(2)}` }}</span>
            </div>
            <div class="flex justify-between text-sm text-gray-400">
              <span>{{ $t('cart.tax') }}</span>
              <span>${{ order.tax.toFixed(2) }}</span>
            </div>
            <div v-if="order.discount > 0" class="flex justify-between text-sm text-green-400">
              <span>{{ $t('cart.discount') }}</span>
              <span>-${{ order.discount.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-base text-white border-t border-gray-800 pt-3 mt-2">
              <span class="tracking-widest">{{ $t('cart.total') }}</span>
              <span class="text-[#c9a84c]">${{ order.total.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <!-- Shipping address -->
        <div class="border border-gray-800 px-6 py-5 mb-8">
          <h2 class="text-xs tracking-widest text-gray-400 uppercase mb-3">{{ $t('order_success.shipping_to') }}</h2>
          <p class="text-sm text-gray-300">{{ order.shipping_first_name }} {{ order.shipping_last_name }}</p>
          <p class="text-sm text-gray-500 mt-1 leading-relaxed">
            {{ order.shipping_address }}<br>
            {{ order.shipping_city }}, {{ order.shipping_postal_code }}<br>
            {{ order.shipping_country }}
          </p>
        </div>

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row gap-4">
          <RouterLink
            to="/account"
            class="flex-1 text-center bg-[#c9a84c] text-black py-4 text-sm tracking-widest hover:bg-[#b8943e] transition-colors"
          >
            {{ $t('order_success.track_order') }}
          </RouterLink>
          <RouterLink
            to="/shop"
            class="flex-1 text-center border border-gray-700 text-gray-300 py-4 text-sm tracking-widest hover:border-gray-500 transition-colors"
          >
            {{ $t('order_success.continue_shopping') }}
          </RouterLink>
        </div>
      </template>

      <!-- Error -->
      <div v-else class="text-center py-20">
        <p class="text-gray-400">{{ $t('order_success.not_found') }}</p>
        <RouterLink to="/" class="text-[#c9a84c] mt-4 inline-block">{{ $t('common.go_home') }}</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCartStore } from '../stores/cart'
import api from '../router/api'

const route = useRoute()
const cart = useCartStore()
const order = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get(`/orders/${route.params.orderId}/confirmation`)
    order.value = data
    cart.clearCart()
  } catch {
    order.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
@keyframes bounce-once {
  0%, 100% { transform: translateY(0); }
  40% { transform: translateY(-12px); }
  60% { transform: translateY(-6px); }
}
.animate-bounce-once {
  animation: bounce-once 0.8s ease-out;
}
</style>
```

- [ ] **Step 2: Add route to router/index.js**

In `frontend/src/router/index.js`, add to public routes:

```javascript
{ path: '/order/success/:orderId', name: 'OrderSuccess', component: () => import('../pages/OrderSuccessPage.vue') },
```

- [ ] **Step 3: Update CheckoutPage to redirect to success page**

In `frontend/src/pages/CheckoutPage.vue`, find the successful order creation handler and replace the redirect:

```javascript
// After order is created successfully:
const orderId = response.data.id
// DO NOT clear cart here — OrderSuccessPage does it
router.push(`/order/success/${orderId}`)
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/OrderSuccessPage.vue frontend/src/router/index.js frontend/src/pages/CheckoutPage.vue
git commit -m "feat: OrderSuccessPage with animated check, order summary, shipping address, redirects from checkout"
```

---

## Task 8: Frontend — Tracking Display in Account & Admin

**Files:**
- Modify: `frontend/src/pages/AccountPage.vue`
- Modify: `frontend/src/pages/admin/AdminOrders.vue`

- [ ] **Step 1: Add tracking display in Account orders tab**

In `frontend/src/pages/AccountPage.vue`, in the order detail view (or order list), add tracking info display. Find where orders are displayed and add:

```vue
<!-- Tracking info (shown when tracking is available) -->
<div
  v-if="order.tracking_number"
  class="mt-3 bg-blue-900/10 border border-blue-500/20 rounded p-3"
>
  <p class="text-xs tracking-widest text-gray-400 mb-2">{{ $t('account.tracking') }}</p>
  <p class="text-sm text-white">{{ order.tracking_company }} · <span class="text-[#c9a84c]">{{ order.tracking_number }}</span></p>
  <a
    v-if="order.tracking_url"
    :href="order.tracking_url"
    target="_blank"
    rel="noopener"
    class="inline-block mt-2 text-xs text-[#c9a84c] border border-[#c9a84c]/30 px-3 py-1 hover:bg-[#c9a84c]/10 transition-colors"
  >
    {{ $t('account.track_package') }} →
  </a>
</div>
```

- [ ] **Step 2: Add tracking form and export button in AdminOrders.vue**

In `frontend/src/pages/admin/AdminOrders.vue`, add:

**Export button** (in the page header area):

```vue
<div class="flex items-center gap-3">
  <!-- Existing filters -->
  <!-- Export dropdown -->
  <div class="relative" ref="exportMenuRef">
    <button
      @click="showExportMenu = !showExportMenu"
      class="flex items-center gap-2 border border-gray-700 text-gray-300 px-4 py-2 text-sm hover:border-gray-500 transition-colors"
    >
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
      </svg>
      {{ $t('admin.export') }}
    </button>
    <div v-if="showExportMenu" class="absolute right-0 top-full mt-1 bg-[#111] border border-gray-800 w-44 z-20 shadow-xl">
      <button @click="exportOrders('csv')" class="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors">CSV</button>
      <button @click="exportOrders('excel')" class="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors">Excel (.xlsx)</button>
    </div>
  </div>
</div>
```

**Export function** in `<script setup>`:

```javascript
import api from '../../router/api'
const showExportMenu = ref(false)
const exportLoading = ref(false)

async function exportOrders(format) {
  showExportMenu.value = false
  exportLoading.value = true
  try {
    const response = await api.get(`/orders/export?format=${format}`, { responseType: 'blob' })
    const today = new Date().toISOString().split('T')[0].replace(/-/g, '')
    const filename = `ordenes_aroma_${today}.${format === 'excel' ? 'xlsx' : 'csv'}`
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch {
    alert(t('admin.export_error'))
  } finally {
    exportLoading.value = false
  }
}
```

**Tracking form** in the order detail/row actions:

```vue
<!-- Tracking form (shown in order detail modal/row) -->
<div v-if="selectedOrder" class="mt-4 border-t border-gray-800 pt-4">
  <h4 class="text-xs tracking-widest text-gray-400 mb-3">{{ $t('admin.tracking_info') }}</h4>
  <div class="grid grid-cols-2 gap-3 mb-3">
    <div>
      <label class="block text-xs text-gray-500 mb-1">{{ $t('admin.tracking_company') }}</label>
      <select v-model="trackingForm.tracking_company" class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none">
        <option value="">Seleccionar...</option>
        <option>FedEx</option>
        <option>UPS</option>
        <option>DHL</option>
        <option>USPS</option>
        <option>Correos de Colombia</option>
        <option>Servientrega</option>
      </select>
    </div>
    <div>
      <label class="block text-xs text-gray-500 mb-1">{{ $t('admin.tracking_number') }}</label>
      <input v-model="trackingForm.tracking_number" type="text" placeholder="Ej: 1Z9999999999999999" class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
    </div>
  </div>
  <div class="mb-3">
    <label class="block text-xs text-gray-500 mb-1">{{ $t('admin.tracking_url') }} (opcional)</label>
    <input v-model="trackingForm.tracking_url" type="url" placeholder="https://..." class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
  </div>
  <button
    @click="saveTracking"
    :disabled="!trackingForm.tracking_number || !trackingForm.tracking_company"
    class="bg-[#c9a84c] text-black px-6 py-2 text-sm tracking-widest hover:bg-[#b8943e] transition-colors disabled:opacity-50"
  >
    {{ $t('admin.save_tracking') }}
  </button>
</div>
```

**Tracking save function**:

```javascript
const trackingForm = ref({ tracking_number: '', tracking_company: '', tracking_url: '' })

async function saveTracking() {
  try {
    await api.put(`/orders/${selectedOrder.value.id}/tracking`, trackingForm.value)
    // Refresh order list
    await loadOrders()
    // Show success toast
  } catch (e) {
    alert(e.response?.data?.detail || t('common.error'))
  }
}
```

- [ ] **Step 3: Add admin/returns route**

In `frontend/src/router/index.js`, add to admin children:

```javascript
{ path: 'returns', name: 'AdminReturns', component: () => import('../pages/admin/AdminReturns.vue') },
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/AccountPage.vue frontend/src/pages/admin/AdminOrders.vue frontend/src/router/index.js
git commit -m "feat: tracking display in account, tracking form + export button in admin orders"
```

---

## Task 9: Frontend — AdminReturns Page

**Files:**
- Create: `frontend/src/pages/admin/AdminReturns.vue`

- [ ] **Step 1: Create AdminReturns.vue**

```vue
<template>
  <div class="p-6 lg:p-8 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-light tracking-widest text-white">{{ $t('admin.returns') }}</h1>
        <p class="text-gray-500 text-sm mt-1">{{ $t('admin.returns_subtitle') }}</p>
      </div>
    </div>

    <!-- Status filter tabs -->
    <div class="flex gap-1 mb-6 border-b border-gray-800">
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        @click="activeStatus = tab.value; loadReturns()"
        class="px-4 py-2 text-sm transition-colors"
        :class="activeStatus === tab.value
          ? 'text-[#c9a84c] border-b-2 border-[#c9a84c]'
          : 'text-gray-500 hover:text-gray-300'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-16 text-gray-500">{{ $t('common.loading') }}</div>

    <!-- Returns table -->
    <div v-else-if="returns.length" class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-800">
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">ID</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">{{ $t('admin.order') }}</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">{{ $t('admin.reason') }}</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">{{ $t('admin.status') }}</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">{{ $t('common.date') }}</th>
            <th class="text-left py-3 px-4 text-xs tracking-widest text-gray-400 font-normal">{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800">
          <tr v-for="ret in returns" :key="ret.id" class="hover:bg-white/2 transition-colors">
            <td class="py-3 px-4 text-gray-400">#{{ ret.id }}</td>
            <td class="py-3 px-4 text-gray-300">{{ $t('admin.order') }} #{{ ret.order_id }}</td>
            <td class="py-3 px-4 text-gray-300 max-w-xs truncate">{{ ret.reason }}</td>
            <td class="py-3 px-4">
              <span
                class="text-xs px-2 py-1 rounded-sm"
                :class="{
                  'bg-yellow-500/20 text-yellow-400': ret.status === 'pending',
                  'bg-green-500/20 text-green-400': ret.status === 'approved' || ret.status === 'refunded',
                  'bg-red-500/20 text-red-400': ret.status === 'rejected',
                  'bg-blue-500/20 text-blue-400': ret.status === 'shipped',
                }"
              >
                {{ $t(`returns.status_${ret.status}`) }}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-500 text-xs">{{ formatDate(ret.created_at) }}</td>
            <td class="py-3 px-4">
              <button
                @click="openReturn(ret)"
                class="text-xs text-[#c9a84c] border border-[#c9a84c]/30 px-3 py-1 hover:bg-[#c9a84c]/10 transition-colors"
              >
                {{ $t('common.review') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center py-16 text-gray-500">{{ $t('admin.no_returns') }}</div>

    <!-- Review modal -->
    <div v-if="selectedReturn" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 px-4" @click.self="selectedReturn = null">
      <div class="bg-[#111] border border-gray-800 p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-white font-light">{{ $t('returns.return_details') }} #{{ selectedReturn.id }}</h3>
          <button @click="selectedReturn = null" class="text-gray-500 hover:text-white">✕</button>
        </div>

        <div class="space-y-4 mb-6">
          <div>
            <p class="text-xs text-gray-500 mb-1">{{ $t('returns.reason') }}</p>
            <p class="text-sm text-gray-200">{{ selectedReturn.reason }}</p>
          </div>
          <div v-if="selectedReturn.comments">
            <p class="text-xs text-gray-500 mb-1">{{ $t('returns.comments') }}</p>
            <p class="text-sm text-gray-400 leading-relaxed">{{ selectedReturn.comments }}</p>
          </div>
          <!-- Return images -->
          <div v-if="selectedReturn.images?.length" class="flex gap-2 flex-wrap">
            <img
              v-for="(img, i) in selectedReturn.images"
              :key="i"
              :src="img"
              class="w-20 h-20 object-cover border border-gray-700"
            />
          </div>
        </div>

        <form @submit.prevent="updateReturnStatus" class="space-y-4 border-t border-gray-800 pt-4">
          <div>
            <label class="block text-xs text-gray-400 mb-1">{{ $t('admin.update_status') }}</label>
            <select v-model="statusForm.status" class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none">
              <option value="pending">{{ $t('returns.status_pending') }}</option>
              <option value="approved">{{ $t('returns.status_approved') }}</option>
              <option value="rejected">{{ $t('returns.status_rejected') }}</option>
              <option value="shipped">{{ $t('returns.status_shipped') }}</option>
              <option value="refunded">{{ $t('returns.status_refunded') }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs text-gray-400 mb-1">{{ $t('admin.admin_notes') }}</label>
            <textarea v-model="statusForm.admin_notes" rows="3" class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none resize-none" :placeholder="$t('admin.notes_placeholder')"></textarea>
          </div>
          <div v-if="statusForm.status === 'refunded'">
            <label class="block text-xs text-gray-400 mb-1">{{ $t('returns.refund_amount') }}</label>
            <input v-model="statusForm.refund_amount" type="number" step="0.01" class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
          </div>
          <button type="submit" class="w-full bg-[#c9a84c] text-black py-3 text-sm tracking-widest hover:bg-[#b8943e] transition-colors">
            {{ $t('admin.save_status') }}
          </button>
        </form>
      </div>
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
const statusForm = ref({ status: 'pending', admin_notes: '', refund_amount: null })

const statusTabs = [
  { label: t('common.all'), value: '' },
  { label: t('returns.status_pending'), value: 'pending' },
  { label: t('returns.status_approved'), value: 'approved' },
  { label: t('returns.status_rejected'), value: 'rejected' },
  { label: t('returns.status_refunded'), value: 'refunded' },
]

async function loadReturns() {
  loading.value = true
  try {
    const params = activeStatus.value ? `?status=${activeStatus.value}` : ''
    const { data } = await api.get(`/returns${params}`)
    returns.value = data
  } finally {
    loading.value = false
  }
}

function openReturn(ret) {
  selectedReturn.value = ret
  statusForm.value = { status: ret.status, admin_notes: ret.admin_notes || '', refund_amount: ret.refund_amount }
}

async function updateReturnStatus() {
  try {
    await api.put(`/returns/${selectedReturn.value.id}/status`, statusForm.value)
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

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/admin/AdminReturns.vue
git commit -m "feat: AdminReturns page with status filter tabs, detail modal, status update form"
```

---

## Task 10: Frontend — Returns Tab in Account Page

**Files:**
- Modify: `frontend/src/pages/AccountPage.vue`

- [ ] **Step 1: Add "Mis Devoluciones" tab to AccountPage**

In AccountPage.vue, add to the sidebar navigation tabs:

```vue
<button
  @click="activeTab = 'returns'"
  class="w-full text-left px-4 py-3 text-sm transition-colors"
  :class="activeTab === 'returns' ? 'text-[#c9a84c] bg-white/5' : 'text-gray-400 hover:text-white'"
>
  {{ $t('account.my_returns') }}
</button>
```

Add to `<script setup>`:

```javascript
const returns = ref([])
const showReturnForm = ref(false)
const returnOrderId = ref(null)
const returnReasons = [
  'Producto dañado',
  'No coincide con la descripción',
  'Cambio de opinión',
  'Producto incorrecto recibido',
  'Calidad insatisfactoria',
]
const returnForm = ref({ reason: '', comments: '' })

async function loadReturns() {
  try {
    const { data } = await api.get('/returns/my-returns')
    returns.value = data
  } catch { /* ignore */ }
}

function openReturnForm(orderId) {
  returnOrderId.value = orderId
  returnForm.value = { reason: '', comments: '' }
  showReturnForm.value = true
}

async function submitReturn() {
  try {
    await api.post('/returns', {
      order_id: returnOrderId.value,
      reason: returnForm.value.reason,
      comments: returnForm.value.comments,
    })
    showReturnForm.value = false
    await loadReturns()
    alert(t('account.return_submitted'))
  } catch (e) {
    alert(e.response?.data?.detail || t('common.error'))
  }
}

// In onMounted, also call loadReturns()
```

Add the Returns tab content:

```vue
<!-- Returns tab -->
<div v-if="activeTab === 'returns'" class="space-y-4">
  <h3 class="text-lg text-white font-light">{{ $t('account.my_returns') }}</h3>

  <!-- Returns list -->
  <div v-if="returns.length === 0" class="text-center py-12 text-gray-500">
    <p>{{ $t('account.no_returns') }}</p>
  </div>
  <div v-else class="space-y-3">
    <div
      v-for="ret in returns"
      :key="ret.id"
      class="border border-gray-800 p-4 flex items-center justify-between gap-4"
    >
      <div class="min-w-0">
        <p class="text-sm text-gray-300">{{ $t('admin.order') }} #{{ ret.order_id }} · {{ ret.reason }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ formatDate(ret.created_at) }}</p>
      </div>
      <span
        class="text-xs px-2 py-1 shrink-0 rounded-sm"
        :class="{
          'bg-yellow-500/20 text-yellow-400': ret.status === 'pending',
          'bg-green-500/20 text-green-400': ret.status === 'approved' || ret.status === 'refunded',
          'bg-red-500/20 text-red-400': ret.status === 'rejected',
        }"
      >
        {{ $t(`returns.status_${ret.status}`) }}
      </span>
    </div>
  </div>

  <!-- Return request form modal -->
  <div v-if="showReturnForm" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 px-4" @click.self="showReturnForm = false">
    <div class="bg-[#111] border border-gray-800 p-6 w-full max-w-md">
      <h3 class="text-white font-light mb-6">{{ $t('account.request_return') }}</h3>
      <form @submit.prevent="submitReturn" class="space-y-4">
        <div>
          <label class="block text-xs text-gray-400 mb-1">{{ $t('returns.reason') }}</label>
          <select v-model="returnForm.reason" required class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none">
            <option value="" disabled>{{ $t('returns.select_reason') }}</option>
            <option v-for="r in returnReasons" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-gray-400 mb-1">{{ $t('returns.comments') }} ({{ $t('common.optional') }})</label>
          <textarea v-model="returnForm.comments" rows="3" class="w-full bg-[#0a0a0a] border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none resize-none"></textarea>
        </div>
        <div class="flex gap-3">
          <button type="submit" class="flex-1 bg-[#c9a84c] text-black py-3 text-sm tracking-widest">{{ $t('account.submit_return') }}</button>
          <button type="button" @click="showReturnForm = false" class="px-5 border border-gray-700 text-gray-400 text-sm">{{ $t('common.cancel') }}</button>
        </div>
      </form>
    </div>
  </div>
</div>
```

Also add a "Solicitar devolución" button in the Orders tab when order status is `delivered`:

```vue
<button
  v-if="order.status === 'delivered'"
  @click="openReturnForm(order.id)"
  class="text-xs text-gray-400 border border-gray-700 px-3 py-1 hover:border-gray-500 hover:text-white transition-colors mt-2 inline-block"
>
  {{ $t('account.request_return') }}
</button>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/AccountPage.vue
git commit -m "feat: returns tab in account (list returns, request form linked from delivered orders)"
```

---

## Task 11: i18n Translations — Orders & Operations

**Files:**
- Modify: `frontend/src/locales/es.json`
- Modify: `frontend/src/locales/en.json`

- [ ] **Step 1: Add Spanish translations**

Add new `"order_success"` section:
```json
"order_success": {
  "title": "¡Pedido Confirmado!",
  "subtitle": "Gracias por tu compra en Aroma-Distribuido",
  "order_number": "NÚMERO DE PEDIDO",
  "email_sent": "Hemos enviado una confirmación a {email}",
  "your_order": "Tu Pedido",
  "shipping_to": "Dirección de Envío",
  "track_order": "Seguir mi Pedido",
  "continue_shopping": "Seguir Comprando",
  "not_found": "Pedido no encontrado"
}
```

Add new `"returns"` section:
```json
"returns": {
  "status_pending": "Pendiente",
  "status_approved": "Aprobada",
  "status_rejected": "Rechazada",
  "status_shipped": "Enviada",
  "status_refunded": "Reembolsada",
  "return_details": "Detalle de Devolución",
  "reason": "Motivo",
  "comments": "Comentarios adicionales",
  "select_reason": "Selecciona un motivo",
  "refund_amount": "Monto de reembolso"
}
```

Add to `"account"`:
```json
"my_returns": "Mis Devoluciones",
"no_returns": "No tienes solicitudes de devolución",
"request_return": "Solicitar Devolución",
"return_submitted": "Tu solicitud ha sido enviada",
"submit_return": "Enviar Solicitud",
"tracking": "Información de Envío",
"track_package": "Rastrear paquete"
```

Add to `"admin"`:
```json
"returns": "Devoluciones",
"returns_subtitle": "Gestiona las solicitudes de devolución de los clientes",
"no_returns": "No hay solicitudes de devolución",
"order": "Pedido",
"reason": "Motivo",
"status": "Estado",
"update_status": "Actualizar estado",
"admin_notes": "Notas internas",
"notes_placeholder": "Mensaje para el cliente (opcional)...",
"save_status": "Guardar Cambios",
"export": "Exportar",
"export_error": "Error al exportar",
"tracking_info": "Información de Tracking",
"tracking_company": "Empresa de Envío",
"tracking_number": "Número de Tracking",
"tracking_url": "URL de seguimiento",
"save_tracking": "Guardar y Notificar Cliente"
```

Add to `"common"`:
```json
"qty": "Cant.",
"free": "Gratis",
"go_home": "Ir al inicio",
"all": "Todos",
"review": "Revisar",
"date": "Fecha",
"actions": "Acciones",
"optional": "opcional",
"error": "Ocurrió un error inesperado"
```

Add to `"cart"`:
```json
"discount": "Descuento"
```

- [ ] **Step 2: Add English translations** (same structure)

`"order_success"`:
```json
"title": "Order Confirmed!",
"subtitle": "Thank you for shopping at Aroma-Distribuido",
"order_number": "ORDER NUMBER",
"email_sent": "We sent a confirmation to {email}",
"your_order": "Your Order",
"shipping_to": "Shipping Address",
"track_order": "Track My Order",
"continue_shopping": "Continue Shopping",
"not_found": "Order not found"
```

`"returns"`:
```json
"status_pending": "Pending",
"status_approved": "Approved",
"status_rejected": "Rejected",
"status_shipped": "Shipped",
"status_refunded": "Refunded",
"return_details": "Return Details",
"reason": "Reason",
"comments": "Additional comments",
"select_reason": "Select a reason",
"refund_amount": "Refund amount"
```

Account additions:
```json
"my_returns": "My Returns",
"no_returns": "No return requests",
"request_return": "Request Return",
"return_submitted": "Your request has been submitted",
"submit_return": "Submit Request",
"tracking": "Shipping Info",
"track_package": "Track package"
```

Common additions:
```json
"qty": "Qty.",
"free": "Free",
"go_home": "Go to home",
"all": "All",
"review": "Review",
"date": "Date",
"actions": "Actions",
"optional": "optional",
"error": "An unexpected error occurred"
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/locales/es.json frontend/src/locales/en.json
git commit -m "feat: i18n translations for order success, returns, tracking, export"
```

---

## Verification

- [ ] Complete a checkout → redirected to /order/success/{id} → see check animation, order number, items, address
- [ ] Check email inbox → order confirmation email received with order details
- [ ] Admin: open an order → fill tracking form → click "Guardar y Notificar" → customer receives tracking email
- [ ] Admin: Órdenes page → click Exportar → CSV downloads correctly with all columns
- [ ] Admin: Exportar → Excel → `.xlsx` file downloads with gold header row
- [ ] Account: My Returns tab visible
- [ ] Delivered order → "Solicitar Devolución" button appears
- [ ] Submit return form → appears in /admin/returns with "Pendiente" status
- [ ] Admin: AdminReturns → change status to "Aprobada" → customer receives email
- [ ] /admin/returns route accessible
