import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_price_alert(
    product_name: str,
    current_price: float,
    target_price: float,
    product_url: str,
    recipient_email: str,
) -> bool:
    settings = get_settings()

    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning(
            "Credenciais SMTP não configuradas. Alerta de e-mail não enviado."
        )
        return False

    remetente = settings.SMTP_FROM or settings.SMTP_USER

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Price Monitor] Alerta de Preço — {product_name}"
    msg["From"] = remetente
    msg["To"] = recipient_email

    texto_simples = (
        f"Boas notícias! O produto que você está monitorando atingiu o preço alvo.\n\n"
        f"Produto    : {product_name}\n"
        f"Preço atual: R$ {current_price:.2f}\n"
        f"Preço alvo : R$ {target_price:.2f}\n"
        f"Link       : {product_url}\n\n"
        "Aproveite a oportunidade!"
    )

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:40px 0;">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:8px;overflow:hidden;
                      box-shadow:0 2px 8px rgba(0,0,0,.12);">
          <tr>
            <td style="background:#16a34a;padding:28px 32px;">
              <h1 style="margin:0;color:#ffffff;font-size:22px;">
                Preco Alvo Atingido!
              </h1>
            </td>
          </tr>
          <tr>
            <td style="padding:32px;">
              <p style="color:#374151;font-size:16px;margin:0 0 24px;">
                O produto <strong>{product_name}</strong> chegou ao preco que voce definiu.
              </p>
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="border:1px solid #e5e7eb;border-radius:6px;overflow:hidden;">
                <tr style="background:#f9fafb;">
                  <td style="padding:14px 20px;color:#6b7280;font-size:14px;
                             border-bottom:1px solid #e5e7eb;">Preco Atual</td>
                  <td style="padding:14px 20px;font-size:24px;font-weight:700;
                             color:#16a34a;border-bottom:1px solid #e5e7eb;">
                    R$ {current_price:.2f}
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 20px;color:#6b7280;font-size:14px;">
                    Preco Alvo
                  </td>
                  <td style="padding:14px 20px;font-size:16px;color:#374151;">
                    R$ {target_price:.2f}
                  </td>
                </tr>
              </table>
              <div style="text-align:center;margin-top:32px;">
                <a href="{product_url}"
                   style="background:#16a34a;color:#ffffff;padding:14px 36px;
                          text-decoration:none;border-radius:6px;font-size:16px;
                          font-weight:600;display:inline-block;">
                  Ver Produto
                </a>
              </div>
            </td>
          </tr>
          <tr>
            <td style="background:#f9fafb;padding:16px 32px;
                       border-top:1px solid #e5e7eb;">
              <p style="margin:0;color:#9ca3af;font-size:12px;text-align:center;">
                Price Monitor &mdash; monitoramento automatico de precos
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    msg.attach(MIMEText(texto_simples, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.sendmail(remetente, recipient_email, msg.as_string())

        logger.info(
            "Alerta de preço enviado para %s (produto: %s)", recipient_email, product_name
        )
        return True

    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Falha ao enviar e-mail de alerta: %s", exc)
        return False
