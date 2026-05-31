from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import asyncio
import logging

from app.utils.email import send_contact_email, send_contact_confirmation_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["contact"])


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str = "Consulta general"
    message: str


@router.post("")
async def send_contact(data: ContactRequest):
    if len(data.message.strip()) < 10:
        raise HTTPException(status_code=422, detail="El mensaje es demasiado corto.")
    if len(data.name.strip()) < 2:
        raise HTTPException(status_code=422, detail="Por favor ingresa tu nombre.")

    try:
        await asyncio.gather(
            send_contact_email(
                name=data.name.strip(),
                email=data.email,
                message=data.message.strip(),
            ),
            send_contact_confirmation_email(
                to=data.email,
                name=data.name.strip(),
            ),
        )
    except Exception as e:
        logger.error("Error enviando correo de contacto: %s", e)
        raise HTTPException(
            status_code=503,
            detail="No se pudo enviar el mensaje. Verifica la configuración SMTP o escríbenos directamente a aromadistribuido@gmail.com.",
        )
    return {"message": "Mensaje enviado correctamente"}
