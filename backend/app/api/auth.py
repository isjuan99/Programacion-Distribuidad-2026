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
    try:
        import jwt as pyjwt
        decoded = pyjwt.decode(
            body.get("identity_token"),
            options={"verify_signature": False},
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
