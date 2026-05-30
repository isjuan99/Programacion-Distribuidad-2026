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
      <h2 style="font-size:20px;font-weight:normal;color:#fff;margin:0 0 8px;">&#161;Gracias por tu pedido, {first_name}!</h2>
      <p style="color:#888;margin:0 0 32px;">Hemos recibido tu pedido y est&#225; siendo procesado.</p>
      <div style="background:#111;border:1px solid #222;padding:20px;margin-bottom:24px;">
        <p style="color:#888;font-size:12px;letter-spacing:3px;margin:0 0 4px;">N&#218;MERO DE PEDIDO</p>
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
        <p style="color:#888;font-size:11px;letter-spacing:3px;margin:0 0 8px;">DIRECCI&#211;N DE ENV&#205;O</p>
        <p style="color:#ccc;font-size:14px;margin:0;white-space:pre-line;">{shipping_address}</p>
      </div>
      <a href="{track_link}"
         style="display:inline-block;background:#c9a84c;color:#0a0a0a;padding:16px 40px;text-decoration:none;letter-spacing:3px;font-size:13px;font-weight:bold;">
        SEGUIR MI PEDIDO
      </a>
      <p style="color:#555;font-size:11px;margin-top:40px;">&#169; 2026 Aroma-Distribuido.</p>
    </div>
    """
    await _send(to, f"Confirmaci&#243;n de pedido #{order_number} — Aroma-Distribuido", html)


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
      <h2 style="font-size:20px;font-weight:normal;color:#fff;text-align:center;margin:0 0 8px;">&#161;Tu pedido ha sido enviado, {first_name}!</h2>
      <p style="color:#888;text-align:center;margin:0 0 32px;">Tu pedido #{order_number} est&#225; en camino.</p>
      <div style="background:#111;border:1px solid #222;padding:20px;margin-bottom:24px;">
        <div style="margin-bottom:12px;">
          <p style="color:#888;font-size:11px;letter-spacing:3px;margin:0 0 4px;">EMPRESA DE ENV&#205;O</p>
          <p style="color:#fff;font-size:16px;margin:0;">{tracking_company}</p>
        </div>
        <div>
          <p style="color:#888;font-size:11px;letter-spacing:3px;margin:0 0 4px;">N&#218;MERO DE TRACKING</p>
          <p style="color:#c9a84c;font-size:18px;letter-spacing:2px;margin:0;">{tracking_number}</p>
        </div>
      </div>
      {track_section}
      <p style="color:#555;font-size:11px;margin-top:40px;">&#169; 2026 Aroma-Distribuido.</p>
    </div>
    """
    await _send(to, f"Tu pedido #{order_number} ha sido enviado — Aroma-Distribuido", html)


async def send_return_status_email(to: str, first_name: str, order_number: str, return_status: str, admin_notes: str = None):
    status_messages = {
        "approved": ("Tu solicitud ha sido aprobada", "Hemos aprobado tu solicitud de devoluci&#243;n. Te contactaremos con las instrucciones de env&#237;o.", "#22c55e"),
        "rejected": ("Solicitud no aprobada", "Despu&#233;s de revisar tu solicitud, no podemos procesarla en este momento.", "#ef4444"),
        "refunded": ("Reembolso procesado", "Hemos procesado tu reembolso. Deber&#237;a reflejarse en tu cuenta en 3-5 d&#237;as h&#225;biles.", "#c9a84c"),
    }
    title, message, color = status_messages.get(return_status, ("Actualizaci&#243;n de devoluci&#243;n", "Hay una actualizaci&#243;n en tu solicitud.", "#c9a84c"))
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
      <p style="color:#555;font-size:11px;margin-top:40px;">&#169; 2026 Aroma-Distribuido.</p>
    </div>
    """
    await _send(to, "Actualizaci&#243;n de devoluci&#243;n — Aroma-Distribuido", html)
