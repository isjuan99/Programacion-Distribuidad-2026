import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings


async def _send(to: str, subject: str, html: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM}>"
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=False,
            start_tls=True,
        )
    except Exception as e:
        print(f"[Email Error] {e}")


async def send_welcome_email(to: str, first_name: str):
    html = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#f5f0e8;padding:40px;">
      <h1 style="font-size:28px;letter-spacing:8px;color:#c9a84c;">AROMA</h1>
      <p style="font-size:18px;margin-top:24px;">Bienvenido, {first_name}.</p>
      <p>Tu cuenta en Aroma-Distribuido ha sido creada exitosamente.</p>
      <a href="{settings.FRONTEND_URL}/shop"
         style="display:inline-block;background:#c9a84c;color:#0a0a0a;padding:14px 32px;text-decoration:none;margin-top:24px;letter-spacing:2px;">
        EXPLORAR CATÁLOGO
      </a>
    </div>
    """
    await _send(to, "Bienvenido a Aroma-Distribuido", html)


async def send_password_reset_email(to: str, token: str):
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    html = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#f5f0e8;padding:40px;">
      <h1 style="font-size:28px;letter-spacing:8px;color:#c9a84c;">AROMA</h1>
      <p style="font-size:16px;margin-top:24px;">Recibimos una solicitud para restablecer tu contraseña.</p>
      <p>Este enlace es válido por 1 hora.</p>
      <a href="{link}"
         style="display:inline-block;background:#c9a84c;color:#0a0a0a;padding:14px 32px;text-decoration:none;margin-top:24px;letter-spacing:2px;">
        RESTABLECER CONTRASEÑA
      </a>
      <p style="color:#666;font-size:12px;margin-top:32px;">Si no solicitaste esto, ignora este correo.</p>
    </div>
    """
    await _send(to, "Restablecer contraseña — Aroma-Distribuido", html)


async def send_verification_email(to: str, first_name: str, token: str):
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    html = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#f5f0e8;padding:40px;">
      <h1 style="font-size:28px;letter-spacing:8px;color:#c9a84c;margin:0 0 8px;">AROMA</h1>
      <p style="font-size:11px;letter-spacing:4px;color:#888;margin:0 0 40px;">DISTRIBUIDO</p>
      <h2 style="font-size:20px;font-weight:normal;margin:0 0 16px;">Verifica tu cuenta, {first_name}.</h2>
      <p style="color:#ccc;line-height:1.7;margin:0 0 24px;">
        Gracias por registrarte en Aroma-Distribuido. Para completar tu registro y acceder a nuestra colecci&#243;n exclusiva,
        por favor verifica tu direcci&#243;n de correo electr&#243;nico.
      </p>
      <p style="color:#888;font-size:13px;margin:0 0 24px;">Este enlace expira en 24 horas.</p>
      <a href="{link}"
         style="display:inline-block;background:#c9a84c;color:#0a0a0a;padding:16px 40px;text-decoration:none;letter-spacing:3px;font-size:13px;font-weight:bold;">
        VERIFICAR MI CUENTA
      </a>
      <p style="color:#555;font-size:11px;margin-top:40px;line-height:1.6;">
        Si no creaste esta cuenta, puedes ignorar este correo.<br>
        &#169; 2026 Aroma-Distribuido. Todos los derechos reservados.
      </p>
    </div>
    """
    await _send(to, "Verifica tu cuenta — Aroma-Distribuido", html)
