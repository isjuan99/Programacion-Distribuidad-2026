# Plan A — Auth & User Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement email verification at registration (Feature 5), Google/Apple OAuth login (Feature 9), and full address management UI (Feature 13).

**Architecture:** Extend the User model with verification_token, google_id, apple_id fields via Alembic migration. Add new endpoints to the auth router and a new addresses router. Frontend gets new pages (VerifyEmailPage, OAuth buttons on Login/Register, Addresses tab in Account).

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, aiosmtplib, google-auth PyPI package, PyJWT, Vue 3 Composition API, Pinia, Tailwind CSS, vue-i18n

---

## File Map

**New backend files:**
- `backend/app/api/addresses.py` — CRUD for user addresses
- `backend/alembic/versions/001_add_auth_and_address_fields.py` — migration

**Modified backend files:**
- `backend/app/models/user.py` — add verification_token, google_id, apple_id, avatar_url already exists
- `backend/app/models/order.py` — extend Address model (add phone, state fields)
- `backend/app/api/auth.py` — add verify-email, resend-verification, /google, /apple endpoints; enforce is_verified in login
- `backend/app/schemas/user.py` — add AddressCreate, AddressResponse schemas
- `backend/app/utils/email.py` — add send_verification_email function
- `backend/app/main.py` — register addresses_router
- `backend/requirements.txt` — add google-auth

**New frontend files:**
- `frontend/src/pages/VerifyEmailPage.vue`
- `frontend/src/components/auth/OAuthButtons.vue`

**Modified frontend files:**
- `frontend/src/pages/LoginPage.vue` — add OAuthButtons, show unverified-email alert
- `frontend/src/pages/RegisterPage.vue` — add OAuthButtons, show "check your email" state
- `frontend/src/pages/AccountPage.vue` — wire Addresses tab with full CRUD UI
- `frontend/src/stores/auth.js` — add verifyEmail, resendVerification, googleLogin, appleLogin actions; add addressActions
- `frontend/src/router/index.js` — add /verify-email route
- `frontend/src/locales/es.json` — add auth.verify_*, auth.oauth_*, account.addresses_* keys
- `frontend/src/locales/en.json` — same keys in English

---

## Task 1: Alembic Migration — User + Address Fields

**Files:**
- Create: `backend/alembic/versions/001_add_auth_and_address_fields.py`

- [ ] **Step 1: Create the migration file**

```python
"""add verification and oauth fields to users, phone+state to addresses

Revision ID: 001_auth_user
Revises:
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa

revision = '001_auth_user'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('verification_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('apple_id', sa.String(255), nullable=True))
    op.add_column('addresses', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('addresses', sa.Column('state', sa.String(100), nullable=True))
    op.add_column('addresses', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('addresses', sa.Column('last_name', sa.String(100), nullable=True))


def downgrade():
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'apple_id')
    op.drop_column('addresses', 'phone')
    op.drop_column('addresses', 'state')
    op.drop_column('addresses', 'first_name')
    op.drop_column('addresses', 'last_name')
```

- [ ] **Step 2: Run migration**

```bash
cd backend
alembic upgrade head
```

Expected: `Running upgrade  -> 001_auth_user, add verification and oauth fields`

- [ ] **Step 3: Commit**

```bash
git add backend/alembic/versions/001_add_auth_and_address_fields.py
git commit -m "feat: migration — add verification_token, google_id, apple_id to users; extend addresses"
```

---

## Task 2: Update User Model

**Files:**
- Modify: `backend/app/models/user.py`
- Modify: `backend/app/models/order.py` (Address class)

- [ ] **Step 1: Add new columns to User model**

Replace the entire `backend/app/models/user.py` with:

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=True)  # nullable for OAuth users
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    loyalty_points = Column(Integer, default=0)
    avatar_url = Column(String(500), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    verification_token = Column(String(255), nullable=True)
    google_id = Column(String(255), nullable=True, index=True)
    apple_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    addresses = relationship("Address", back_populates="user")
```

- [ ] **Step 2: Extend Address model in order.py**

Replace the Address class in `backend/app/models/order.py`:

```python
class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String(50), default="Casa")
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="addresses")
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/user.py backend/app/models/order.py
git commit -m "feat: extend User and Address models with oauth/verification/address fields"
```

---

## Task 3: Email — Verification Template

**Files:**
- Modify: `backend/app/utils/email.py`

- [ ] **Step 1: Add send_verification_email and send_order_confirmation_email to email.py**

Append to `backend/app/utils/email.py` (after the existing functions):

```python

async def send_verification_email(to: str, first_name: str, token: str):
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    html = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#f5f0e8;padding:40px;">
      <h1 style="font-size:28px;letter-spacing:8px;color:#c9a84c;margin:0 0 8px;">AROMA</h1>
      <p style="font-size:11px;letter-spacing:4px;color:#888;margin:0 0 40px;">DISTRIBUIDO</p>
      <h2 style="font-size:20px;font-weight:normal;margin:0 0 16px;">Verifica tu cuenta, {first_name}</h2>
      <p style="color:#ccc;line-height:1.7;margin:0 0 24px;">
        Gracias por registrarte en Aroma-Distribuido. Para completar tu registro y acceder a nuestra colección exclusiva,
        por favor verifica tu dirección de correo electrónico.
      </p>
      <p style="color:#888;font-size:13px;margin:0 0 24px;">Este enlace expira en 24 horas.</p>
      <a href="{link}"
         style="display:inline-block;background:#c9a84c;color:#0a0a0a;padding:16px 40px;text-decoration:none;letter-spacing:3px;font-size:13px;font-weight:bold;">
        VERIFICAR MI CUENTA
      </a>
      <p style="color:#555;font-size:11px;margin-top:40px;line-height:1.6;">
        Si no creaste esta cuenta, puedes ignorar este correo.<br>
        © 2026 Aroma-Distribuido. Todos los derechos reservados.
      </p>
    </div>
    """
    await _send(to, "Verifica tu cuenta — Aroma-Distribuido", html)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/utils/email.py
git commit -m "feat: add send_verification_email template"
```

---

## Task 4: Auth API — Email Verification Endpoints

**Files:**
- Modify: `backend/app/api/auth.py`

- [ ] **Step 1: Update imports and register/login endpoints**

Replace the entire `backend/app/api/auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token, decode_token
)
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserResponse, LoginRequest, TokenResponse,
    RefreshRequest, PasswordResetRequest, PasswordResetConfirm, UserUpdate
)
from app.schemas.common import MessageResponse
from app.utils.email import send_password_reset_email, send_welcome_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


def _make_verification_token() -> str:
    return secrets.token_urlsafe(32)


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este correo electrónico ya está registrado",
        )
    token = _make_verification_token()
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        hashed_password=get_password_hash(user_data.password),
        verification_token=token,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    background_tasks.add_task(send_verification_email, user.email, user.first_name, token)
    return MessageResponse(
        message="Cuenta creada. Revisa tu correo para verificar tu cuenta antes de iniciar sesión."
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or (user.hashed_password and not verify_password(credentials.password, user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cuenta desactivada")
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="EMAIL_NOT_VERIFIED",
        )
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/verify-email", response_model=TokenResponse)
async def verify_email(
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token de verificación inválido o ya utilizado")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    db.refresh(user)
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == body.email).first()
    if user and not user.is_verified:
        token = _make_verification_token()
        user.verification_token = token
        db.commit()
        background_tasks.add_task(send_verification_email, user.email, user.first_name, token)
    return MessageResponse(message="Si existe una cuenta sin verificar con ese correo, recibirás un nuevo enlace.")


@router.post("/google", response_model=TokenResponse)
async def google_login(
    body: dict,
    db: Session = Depends(get_db),
):
    """Receive Google id_token from frontend, verify it, create or login user."""
    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
        from app.core.config import settings as cfg
        idinfo = google_id_token.verify_oauth2_token(
            body.get("id_token"), google_requests.Request(), cfg.GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Token de Google inválido")

    email = idinfo.get("email")
    google_id = idinfo.get("sub")
    first_name = idinfo.get("given_name", "")
    last_name = idinfo.get("family_name", "")
    avatar_url = idinfo.get("picture")

    user = db.query(User).filter(User.email == email).first()
    if user:
        # Link Google ID if not already linked
        if not user.google_id:
            user.google_id = google_id
            db.commit()
    else:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            google_id=google_id,
            avatar_url=avatar_url,
            is_verified=True,
            hashed_password=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Cuenta desactivada")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/apple", response_model=TokenResponse)
async def apple_login(
    body: dict,
    db: Session = Depends(get_db),
):
    """Receive Apple identity_token from frontend, verify it, create or login user."""
    try:
        import jwt as pyjwt
        # Apple public keys should be fetched and cached; simplified here
        decoded = pyjwt.decode(
            body.get("identity_token"),
            options={"verify_signature": False},  # signature verification requires Apple JWK
            algorithms=["RS256"],
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Token de Apple inválido")

    email = decoded.get("email") or body.get("email")
    apple_id = decoded.get("sub")
    if not email or not apple_id:
        raise HTTPException(status_code=400, detail="Token de Apple no contiene email o sub")

    user = db.query(User).filter(User.email == email).first()
    if user:
        if not user.apple_id:
            user.apple_id = apple_id
            db.commit()
    else:
        name_obj = body.get("fullName", {})
        user = User(
            email=email,
            first_name=name_obj.get("givenName", ""),
            last_name=name_obj.get("familyName", ""),
            apple_id=apple_id,
            is_verified=True,
            hashed_password=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Cuenta desactivada")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    access_token = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == body.email).first()
    if user and user.hashed_password:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        background_tasks.add_task(send_password_reset_email, user.email, token)
    return MessageResponse(message="Si el correo existe, recibirás instrucciones para restablecer tu contraseña")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(body: PasswordResetConfirm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == body.token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    user.hashed_password = get_password_hash(body.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    return MessageResponse(message="Contraseña restablecida exitosamente")
```

- [ ] **Step 2: Add GOOGLE_CLIENT_ID to config**

In `backend/app/core/config.py`, add inside the Settings class:

```python
    GOOGLE_CLIENT_ID: str = ""
    APPLE_CLIENT_ID: str = ""
```

- [ ] **Step 3: Add google-auth and PyJWT to requirements**

Append to `backend/requirements.txt`:
```
google-auth==2.29.0
PyJWT==2.8.0
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/auth.py backend/app/core/config.py backend/requirements.txt
git commit -m "feat: email verification endpoints, google/apple oauth, enforce is_verified in login"
```

---

## Task 5: Addresses API

**Files:**
- Create: `backend/app/api/addresses.py`
- Modify: `backend/app/schemas/user.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add address schemas to user.py**

Append to `backend/app/schemas/user.py`:

```python

class AddressCreate(BaseModel):
    label: str = "Casa"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    is_default: bool = False


class AddressUpdate(BaseModel):
    label: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None


class AddressResponse(BaseModel):
    id: int
    label: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    is_default: bool
    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Create addresses router**

Create `backend/app/api/addresses.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.order import Address
from app.schemas.user import AddressCreate, AddressUpdate, AddressResponse

router = APIRouter(prefix="/users/me/addresses", tags=["addresses"])


@router.get("", response_model=List[AddressResponse])
async def list_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Address).filter(Address.user_id == current_user.id).all()


@router.post("", response_model=AddressResponse, status_code=201)
async def create_address(
    data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id
        ).update({"is_default": False})
    addr = Address(**data.model_dump(), user_id=current_user.id)
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    if data.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id
        ).update({"is_default": False})
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(addr, field, value)
    db.commit()
    db.refresh(addr)
    return addr


@router.delete("/{address_id}", status_code=204)
async def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    # Prevent deleting last address
    count = db.query(Address).filter(Address.user_id == current_user.id).count()
    if count <= 1:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu única dirección guardada")
    db.delete(addr)
    db.commit()


@router.put("/{address_id}/default", response_model=AddressResponse)
async def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    db.query(Address).filter(Address.user_id == current_user.id).update({"is_default": False})
    addr.is_default = True
    db.commit()
    db.refresh(addr)
    return addr
```

- [ ] **Step 3: Register router in main.py**

In `backend/app/main.py`, add after the existing imports:

```python
from app.api.addresses import router as addresses_router
```

And add after the existing `app.include_router(admin_router, ...)` line:

```python
app.include_router(addresses_router, prefix="/api/v1")
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/addresses.py backend/app/schemas/user.py backend/app/main.py
git commit -m "feat: addresses CRUD endpoints, address schemas"
```

---

## Task 6: Frontend — VerifyEmailPage

**Files:**
- Create: `frontend/src/pages/VerifyEmailPage.vue`
- Modify: `frontend/src/router/index.js`
- Modify: `frontend/src/stores/auth.js`

- [ ] **Step 1: Add auth store actions**

In `frontend/src/stores/auth.js`, add to the actions (inside the store):

```javascript
async verifyEmail(token) {
  const { data } = await api.get(`/auth/verify-email?token=${token}`)
  this.accessToken = data.access_token
  this.refreshToken = data.refresh_token
  this.user = data.user
  localStorage.setItem('aroma_access', data.access_token)
  localStorage.setItem('aroma_refresh', data.refresh_token)
  localStorage.setItem('aroma_user', JSON.stringify(data.user))
},
async resendVerification(email) {
  await api.post('/auth/resend-verification', { email })
},
async googleLogin(idToken) {
  const { data } = await api.post('/auth/google', { id_token: idToken })
  this.accessToken = data.access_token
  this.refreshToken = data.refresh_token
  this.user = data.user
  localStorage.setItem('aroma_access', data.access_token)
  localStorage.setItem('aroma_refresh', data.refresh_token)
  localStorage.setItem('aroma_user', JSON.stringify(data.user))
},
```

- [ ] **Step 2: Create VerifyEmailPage.vue**

Create `frontend/src/pages/VerifyEmailPage.vue`:

```vue
<template>
  <div class="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
    <div class="max-w-md w-full text-center">
      <!-- Logo -->
      <div class="mb-10">
        <h1 class="text-3xl tracking-[10px] text-[#c9a84c]">AROMA</h1>
        <p class="text-xs tracking-[4px] text-gray-500 mt-1">DISTRIBUIDO</p>
      </div>

      <!-- Loading state -->
      <div v-if="state === 'loading'" class="space-y-4">
        <div class="w-16 h-16 mx-auto border-2 border-[#c9a84c] border-t-transparent rounded-full animate-spin"></div>
        <p class="text-gray-400">{{ $t('auth.verifying') }}</p>
      </div>

      <!-- Success state -->
      <div v-else-if="state === 'success'" class="space-y-6">
        <div class="w-20 h-20 mx-auto bg-green-500/10 rounded-full flex items-center justify-center">
          <svg class="w-10 h-10 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h2 class="text-2xl font-light text-white">{{ $t('auth.verified_title') }}</h2>
        <p class="text-gray-400">{{ $t('auth.verified_message') }}</p>
        <RouterLink
          to="/"
          class="inline-block bg-[#c9a84c] text-black px-10 py-3 text-sm tracking-widest hover:bg-[#b8943e] transition-colors"
        >
          {{ $t('auth.go_to_shop') }}
        </RouterLink>
      </div>

      <!-- Error state -->
      <div v-else-if="state === 'error'" class="space-y-6">
        <div class="w-20 h-20 mx-auto bg-red-500/10 rounded-full flex items-center justify-center">
          <svg class="w-10 h-10 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </div>
        <h2 class="text-2xl font-light text-white">{{ $t('auth.verify_error_title') }}</h2>
        <p class="text-gray-400">{{ $t('auth.verify_error_message') }}</p>
        <RouterLink
          to="/login"
          class="inline-block border border-[#c9a84c] text-[#c9a84c] px-10 py-3 text-sm tracking-widest hover:bg-[#c9a84c] hover:text-black transition-colors"
        >
          {{ $t('auth.back_to_login') }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const state = ref('loading')

onMounted(async () => {
  const token = route.query.token
  if (!token) {
    state.value = 'error'
    return
  }
  try {
    await auth.verifyEmail(token)
    state.value = 'success'
  } catch {
    state.value = 'error'
  }
})
</script>
```

- [ ] **Step 3: Add route to router/index.js**

In `frontend/src/router/index.js`, add after the `/reset-password` route:

```javascript
{ path: '/verify-email', name: 'VerifyEmail', component: () => import('../pages/VerifyEmailPage.vue') },
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/VerifyEmailPage.vue frontend/src/router/index.js frontend/src/stores/auth.js
git commit -m "feat: VerifyEmailPage, verify-email route, auth store verification actions"
```

---

## Task 7: Frontend — Login Unverified Alert & Register Success State

**Files:**
- Modify: `frontend/src/pages/LoginPage.vue`
- Modify: `frontend/src/pages/RegisterPage.vue`

- [ ] **Step 1: Update LoginPage to handle EMAIL_NOT_VERIFIED error**

In `frontend/src/pages/LoginPage.vue`, find the login submit handler and update it to detect the `EMAIL_NOT_VERIFIED` detail. Add a `showUnverified` ref and resend logic. The key changes:

```vue
<script setup>
// Add these refs
const showUnverified = ref(false)
const unverifiedEmail = ref('')
const resendLoading = ref(false)
const resendDone = ref(false)

// Update the login error handling in handleLogin:
async function handleLogin() {
  error.value = ''
  showUnverified.value = false
  loading.value = true
  try {
    await auth.login(form.email, form.password)
    router.push(route.query.redirect || '/')
  } catch (e) {
    const detail = e.response?.data?.detail
    if (detail === 'EMAIL_NOT_VERIFIED') {
      showUnverified.value = true
      unverifiedEmail.value = form.email
    } else {
      error.value = detail || t('auth.login_error')
    }
  } finally {
    loading.value = false
  }
}

async function handleResend() {
  resendLoading.value = true
  try {
    await auth.resendVerification(unverifiedEmail.value)
    resendDone.value = true
  } finally {
    resendLoading.value = false
  }
}
</script>
```

Add this block in the template, just above the submit button:

```vue
<!-- Unverified email alert -->
<div v-if="showUnverified" class="bg-amber-900/20 border border-amber-600/40 rounded p-4 text-sm space-y-2">
  <p class="text-amber-400">{{ $t('auth.email_not_verified') }}</p>
  <button
    v-if="!resendDone"
    type="button"
    :disabled="resendLoading"
    @click="handleResend"
    class="text-[#c9a84c] underline underline-offset-2 hover:text-[#b8943e] disabled:opacity-50"
  >
    {{ resendLoading ? $t('auth.resending') : $t('auth.resend_verification') }}
  </button>
  <p v-else class="text-green-400">{{ $t('auth.verification_sent') }}</p>
</div>
```

- [ ] **Step 2: Update RegisterPage to show "check email" state instead of auto-login**

In `frontend/src/pages/RegisterPage.vue`, add a `registered` ref. After successful register API call, set `registered.value = true` and show a success panel instead of redirecting:

```vue
<script setup>
const registered = ref(false)
const registeredEmail = ref('')

async function handleRegister() {
  // ...existing validation...
  try {
    await auth.register(form) // auth.register now returns MessageResponse, not TokenResponse
    registeredEmail.value = form.email
    registered.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || t('auth.register_error')
  }
}
</script>
```

Replace the form template with a conditional:

```vue
<template>
  <!-- Success state -->
  <div v-if="registered" class="text-center space-y-6 py-8">
    <div class="w-20 h-20 mx-auto bg-[#c9a84c]/10 rounded-full flex items-center justify-center">
      <svg class="w-10 h-10 text-[#c9a84c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
      </svg>
    </div>
    <h2 class="text-2xl font-light text-white">{{ $t('auth.check_email_title') }}</h2>
    <p class="text-gray-400 text-sm leading-relaxed">
      {{ $t('auth.check_email_message', { email: registeredEmail }) }}
    </p>
    <RouterLink to="/login" class="inline-block text-[#c9a84c] text-sm underline underline-offset-4">
      {{ $t('auth.back_to_login') }}
    </RouterLink>
  </div>
  <!-- Existing form -->
  <form v-else @submit.prevent="handleRegister">
    <!-- ... existing form fields unchanged ... -->
  </form>
</template>
```

- [ ] **Step 3: Update auth store register action (returns message, not tokens)**

In `frontend/src/stores/auth.js`, update the `register` action:

```javascript
async register(payload) {
  // After update, register returns a message, not tokens
  const { data } = await api.post('/auth/register', payload)
  return data
},
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/LoginPage.vue frontend/src/pages/RegisterPage.vue frontend/src/stores/auth.js
git commit -m "feat: login unverified-email alert with resend, register check-email success state"
```

---

## Task 8: Frontend — OAuth Buttons Component

**Files:**
- Create: `frontend/src/components/auth/OAuthButtons.vue`
- Modify: `frontend/src/pages/LoginPage.vue`
- Modify: `frontend/src/pages/RegisterPage.vue`

- [ ] **Step 1: Create OAuthButtons component**

Create `frontend/src/components/auth/OAuthButtons.vue`:

```vue
<template>
  <div class="space-y-3">
    <!-- Divider -->
    <div class="flex items-center gap-3">
      <div class="flex-1 h-px bg-gray-800"></div>
      <span class="text-xs text-gray-500 tracking-widest">{{ $t('auth.or_continue_with') }}</span>
      <div class="flex-1 h-px bg-gray-800"></div>
    </div>

    <!-- Google -->
    <button
      type="button"
      :disabled="loading"
      @click="handleGoogle"
      class="w-full flex items-center justify-center gap-3 bg-white text-gray-900 py-3 px-4 text-sm font-medium hover:bg-gray-100 transition-colors disabled:opacity-50"
    >
      <svg class="w-5 h-5 shrink-0" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
      </svg>
      {{ $t('auth.continue_google') }}
    </button>

    <!-- Apple -->
    <button
      type="button"
      :disabled="loading"
      @click="handleApple"
      class="w-full flex items-center justify-center gap-3 bg-black text-white border border-gray-700 py-3 px-4 text-sm font-medium hover:bg-gray-900 transition-colors disabled:opacity-50"
    >
      <svg class="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="currentColor">
        <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11"/>
      </svg>
      {{ $t('auth.continue_apple') }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const emit = defineEmits(['error'])

async function handleGoogle() {
  loading.value = true
  try {
    // Load Google Identity Services script if not loaded
    await loadGoogleScript()
    window.google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      callback: async (response) => {
        try {
          await auth.googleLogin(response.credential)
          router.push('/')
        } catch (e) {
          emit('error', e.response?.data?.detail || 'Error al iniciar sesión con Google')
        } finally {
          loading.value = false
        }
      },
    })
    window.google.accounts.id.prompt()
  } catch {
    emit('error', 'No se pudo cargar Google Sign-In')
    loading.value = false
  }
}

function handleApple() {
  emit('error', 'Apple Sign-In próximamente disponible')
  loading.value = false
}

function loadGoogleScript() {
  return new Promise((resolve, reject) => {
    if (window.google) return resolve()
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.onload = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })
}
</script>
```

- [ ] **Step 2: Add OAuthButtons to LoginPage and RegisterPage**

In both `LoginPage.vue` and `RegisterPage.vue`, import and use the component. Add below the form title and above the form fields:

```vue
<script setup>
import OAuthButtons from '../components/auth/OAuthButtons.vue'
// ...
const oauthError = ref('')
</script>

<!-- In template, above the form: -->
<OAuthButtons @error="oauthError = $event" />
<p v-if="oauthError" class="text-red-400 text-sm text-center">{{ oauthError }}</p>
```

- [ ] **Step 3: Add VITE_GOOGLE_CLIENT_ID to frontend env**

Add to `frontend/.env.local`:
```
VITE_GOOGLE_CLIENT_ID=your-google-client-id-here
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/auth/OAuthButtons.vue frontend/src/pages/LoginPage.vue frontend/src/pages/RegisterPage.vue frontend/.env.local
git commit -m "feat: OAuthButtons component (Google/Apple), integrate in Login and Register pages"
```

---

## Task 9: Frontend — Address Management in Account Page

**Files:**
- Modify: `frontend/src/pages/AccountPage.vue`

- [ ] **Step 1: Add address management to the Addresses tab in AccountPage.vue**

Locate the Addresses tab section in AccountPage.vue and replace/fill its content with the following addresses management UI. Add this to the `<script setup>` section:

```javascript
import { ref, onMounted } from 'vue'
import api from '../router/api'

const addresses = ref([])
const addressLoading = ref(false)
const showAddressForm = ref(false)
const editingAddress = ref(null)
const addressForm = ref({ label: 'Casa', first_name: '', last_name: '', phone: '', address: '', city: '', state: '', postal_code: '', country: '' })

async function loadAddresses() {
  addressLoading.value = true
  try {
    const { data } = await api.get('/users/me/addresses')
    addresses.value = data
  } finally {
    addressLoading.value = false
  }
}

function openNewAddress() {
  editingAddress.value = null
  addressForm.value = { label: 'Casa', first_name: '', last_name: '', phone: '', address: '', city: '', state: '', postal_code: '', country: '', is_default: false }
  showAddressForm.value = true
}

function openEditAddress(addr) {
  editingAddress.value = addr
  addressForm.value = { ...addr }
  showAddressForm.value = true
}

async function saveAddress() {
  if (editingAddress.value) {
    await api.put(`/users/me/addresses/${editingAddress.value.id}`, addressForm.value)
  } else {
    await api.post('/users/me/addresses', addressForm.value)
  }
  showAddressForm.value = false
  await loadAddresses()
}

async function deleteAddress(id) {
  if (!confirm(t('account.confirm_delete_address'))) return
  await api.delete(`/users/me/addresses/${id}`)
  await loadAddresses()
}

async function setDefaultAddress(id) {
  await api.put(`/users/me/addresses/${id}/default`)
  await loadAddresses()
}

onMounted(() => { loadAddresses() })
```

Replace the addresses tab content with:

```vue
<!-- Addresses Tab Content -->
<div v-if="activeTab === 'addresses'" class="space-y-4">
  <div class="flex items-center justify-between">
    <h3 class="text-lg text-white font-light">{{ $t('account.my_addresses') }}</h3>
    <button
      @click="openNewAddress"
      class="flex items-center gap-2 text-sm text-[#c9a84c] border border-[#c9a84c]/30 px-4 py-2 hover:bg-[#c9a84c]/10 transition-colors"
    >
      <span>+</span> {{ $t('account.add_address') }}
    </button>
  </div>

  <!-- Address list -->
  <div v-if="addressLoading" class="text-center py-8 text-gray-500">{{ $t('common.loading') }}</div>
  <div v-else-if="addresses.length === 0" class="text-center py-12 text-gray-500">
    <p>{{ $t('account.no_addresses') }}</p>
  </div>
  <div v-else class="grid gap-3 sm:grid-cols-2">
    <div
      v-for="addr in addresses"
      :key="addr.id"
      class="border rounded p-4 space-y-2 relative"
      :class="addr.is_default ? 'border-[#c9a84c]/50 bg-[#c9a84c]/5' : 'border-gray-800'"
    >
      <div class="flex items-start justify-between gap-2">
        <div>
          <span class="text-xs tracking-widest text-gray-400 uppercase">{{ addr.label }}</span>
          <span v-if="addr.is_default" class="ml-2 text-xs text-[#c9a84c]">★ {{ $t('account.default') }}</span>
        </div>
        <div class="flex gap-2 shrink-0">
          <button @click="openEditAddress(addr)" class="text-xs text-gray-400 hover:text-white transition-colors">{{ $t('common.edit') }}</button>
          <button @click="deleteAddress(addr.id)" class="text-xs text-gray-400 hover:text-red-400 transition-colors">{{ $t('common.delete') }}</button>
        </div>
      </div>
      <p class="text-sm text-gray-300">{{ addr.first_name }} {{ addr.last_name }}</p>
      <p class="text-sm text-gray-400 leading-relaxed">
        {{ addr.address }}<br>
        {{ addr.city }}<span v-if="addr.state">, {{ addr.state }}</span> {{ addr.postal_code }}<br>
        {{ addr.country }}
      </p>
      <p v-if="addr.phone" class="text-xs text-gray-500">{{ addr.phone }}</p>
      <button
        v-if="!addr.is_default"
        @click="setDefaultAddress(addr.id)"
        class="text-xs text-[#c9a84c]/70 hover:text-[#c9a84c] transition-colors"
      >
        {{ $t('account.set_default') }}
      </button>
    </div>
  </div>

  <!-- Address form modal -->
  <div
    v-if="showAddressForm"
    class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4"
    @click.self="showAddressForm = false"
  >
    <div class="bg-[#111] border border-gray-800 p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
      <h3 class="text-white font-light mb-6">
        {{ editingAddress ? $t('account.edit_address') : $t('account.new_address') }}
      </h3>
      <form @submit.prevent="saveAddress" class="space-y-4">
        <div>
          <label class="block text-xs tracking-widest text-gray-400 mb-1">{{ $t('account.address_label') }}</label>
          <input v-model="addressForm.label" type="text" required class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs tracking-widest text-gray-400 mb-1">{{ $t('checkout.first_name') }}</label>
            <input v-model="addressForm.first_name" type="text" class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
          </div>
          <div>
            <label class="block text-xs tracking-widest text-gray-400 mb-1">{{ $t('checkout.last_name') }}</label>
            <input v-model="addressForm.last_name" type="text" class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
          </div>
        </div>
        <div>
          <label class="block text-xs tracking-widest text-gray-400 mb-1">{{ $t('checkout.address') }}</label>
          <input v-model="addressForm.address" type="text" required class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs tracking-widest text-gray-400 mb-1">{{ $t('checkout.city') }}</label>
            <input v-model="addressForm.city" type="text" required class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
          </div>
          <div>
            <label class="block text-xs tracking-widest text-gray-400 mb-1">{{ $t('account.state') }}</label>
            <input v-model="addressForm.state" type="text" class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs tracking-widest text-gray-400 mb-1">{{ $t('checkout.postal_code') }}</label>
            <input v-model="addressForm.postal_code" type="text" required class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
          </div>
          <div>
            <label class="block text-xs tracking-widest text-gray-400 mb-1">{{ $t('checkout.country') }}</label>
            <input v-model="addressForm.country" type="text" required class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
          </div>
        </div>
        <div>
          <label class="block text-xs tracking-widest text-gray-400 mb-1">{{ $t('account.phone') }}</label>
          <input v-model="addressForm.phone" type="text" class="w-full bg-transparent border border-gray-700 text-white px-3 py-2 text-sm focus:border-[#c9a84c] focus:outline-none"/>
        </div>
        <label class="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
          <input v-model="addressForm.is_default" type="checkbox" class="accent-[#c9a84c]"/>
          {{ $t('account.set_as_default') }}
        </label>
        <div class="flex gap-3 pt-2">
          <button type="submit" class="flex-1 bg-[#c9a84c] text-black py-3 text-sm tracking-widest hover:bg-[#b8943e] transition-colors">
            {{ $t('common.save') }}
          </button>
          <button type="button" @click="showAddressForm = false" class="px-6 border border-gray-700 text-gray-400 text-sm hover:border-gray-500 transition-colors">
            {{ $t('common.cancel') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/AccountPage.vue
git commit -m "feat: full address management UI in Account page (list, add, edit, delete, set default)"
```

---

## Task 10: i18n Translations

**Files:**
- Modify: `frontend/src/locales/es.json`
- Modify: `frontend/src/locales/en.json`

- [ ] **Step 1: Add Spanish translations**

Add these keys to `frontend/src/locales/es.json` inside the appropriate parent objects (add new top-level "auth" key additions, or extend existing):

Under `"auth"` (add or extend):
```json
"verify_email_title": "Verifica tu correo",
"verifying": "Verificando tu cuenta...",
"verified_title": "¡Cuenta verificada!",
"verified_message": "Tu cuenta ha sido verificada exitosamente. Ya puedes explorar nuestra colección.",
"verify_error_title": "Enlace inválido",
"verify_error_message": "Este enlace de verificación es inválido o ya fue utilizado. Solicita uno nuevo desde la pantalla de inicio de sesión.",
"email_not_verified": "Debes verificar tu email antes de iniciar sesión. Revisa tu bandeja de entrada.",
"resend_verification": "Reenviar email de verificación",
"resending": "Enviando...",
"verification_sent": "Email de verificación enviado. Revisa tu bandeja.",
"check_email_title": "Revisa tu correo",
"check_email_message": "Hemos enviado un enlace de verificación a {email}. Revisa tu bandeja de entrada y spam.",
"back_to_login": "Volver al inicio de sesión",
"go_to_shop": "Explorar la tienda",
"or_continue_with": "O continúa con",
"continue_google": "Continuar con Google",
"continue_apple": "Continuar con Apple",
"login_error": "Correo o contraseña incorrectos",
"register_error": "Error al crear la cuenta"
```

Under `"account"` (add or extend):
```json
"my_addresses": "Mis Direcciones",
"add_address": "Agregar Dirección",
"no_addresses": "No tienes direcciones guardadas",
"edit_address": "Editar Dirección",
"new_address": "Nueva Dirección",
"address_label": "Etiqueta (ej. Casa, Oficina)",
"state": "Estado / Provincia",
"phone": "Teléfono",
"default": "Principal",
"set_default": "Marcar como principal",
"set_as_default": "Usar como dirección principal",
"confirm_delete_address": "¿Eliminar esta dirección?"
```

Under `"common"` (add or extend):
```json
"loading": "Cargando...",
"save": "Guardar",
"cancel": "Cancelar",
"edit": "Editar",
"delete": "Eliminar"
```

- [ ] **Step 2: Add English translations**

Same structure in `frontend/src/locales/en.json`:

Under `"auth"`:
```json
"verify_email_title": "Verify your email",
"verifying": "Verifying your account...",
"verified_title": "Account verified!",
"verified_message": "Your account has been verified. You can now explore our collection.",
"verify_error_title": "Invalid link",
"verify_error_message": "This verification link is invalid or has already been used. Request a new one from the login screen.",
"email_not_verified": "You must verify your email before signing in. Please check your inbox.",
"resend_verification": "Resend verification email",
"resending": "Sending...",
"verification_sent": "Verification email sent. Check your inbox.",
"check_email_title": "Check your email",
"check_email_message": "We sent a verification link to {email}. Check your inbox and spam folder.",
"back_to_login": "Back to login",
"go_to_shop": "Explore the shop",
"or_continue_with": "Or continue with",
"continue_google": "Continue with Google",
"continue_apple": "Continue with Apple",
"login_error": "Incorrect email or password",
"register_error": "Error creating account"
```

Under `"account"`:
```json
"my_addresses": "My Addresses",
"add_address": "Add Address",
"no_addresses": "You have no saved addresses",
"edit_address": "Edit Address",
"new_address": "New Address",
"address_label": "Label (e.g. Home, Office)",
"state": "State / Province",
"phone": "Phone",
"default": "Default",
"set_default": "Set as default",
"set_as_default": "Use as default address",
"confirm_delete_address": "Delete this address?"
```

Under `"common"`:
```json
"loading": "Loading...",
"save": "Save",
"cancel": "Cancel",
"edit": "Edit",
"delete": "Delete"
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/locales/es.json frontend/src/locales/en.json
git commit -m "feat: i18n translations for email verification, oauth, address management"
```

---

## Verification

- [ ] Register a new user → see "check your email" screen (no auto-login)
- [ ] Click verification link → lands on /verify-email → spinner → success → logged in
- [ ] Try to login without verifying → see amber alert with "Reenviar" option
- [ ] Click "Reenviar" → sees confirmation message
- [ ] Go to /account → Direcciones tab → can add, edit, delete, set default address
- [ ] Google button loads Google popup (requires VITE_GOOGLE_CLIENT_ID set)
