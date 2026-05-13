import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import httpx
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailNotifier:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = None
        self.sender_password = None
        self._load_config()

    def _load_config(self):
        try:
            from backend.config import settings
            self.sender_email = settings.smtp_email
            self.sender_password = settings.smtp_password
        except Exception:
            self.sender_email = None
            self.sender_password = None

    def is_configured(self) -> bool:
        return bool(self.sender_email and self.sender_password)

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        if not self.is_configured():
            logger.warning("Email not configured. Skipping.")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.sender_email
            msg["To"] = to_email
            msg["Subject"] = subject

            part = MIMEText(html_content, "html")
            msg.attach(part)

            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, msg.as_string())

            logger.info("Email sent to %s: %s", to_email, subject)
            return True
        except Exception as e:
            logger.error("Failed to send email: %s", e)
            return False

    def send_daily_reading(self, to_email: str, book_title: str, chapter_num: int,
                           chapter_title: Optional[str], summary: str,
                           key_points: List[str]) -> bool:
        subject = f"📚 Daily Reading: {book_title} - Chapter {chapter_num}"
        if chapter_title:
            subject += f": {chapter_title}"

        points_html = "".join(
            f'<li style="margin-bottom:8px;color:#374151;font-size:15px;line-height:1.5">{p}</li>'
            for p in key_points
        )

        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin:0; padding:0; background:#f3f4f6; }}
  .container {{ max-width:600px; margin:20px auto; background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.1); }}
  .header {{ background:linear-gradient(135deg,#1e40af,#3b82f6); color:#fff; padding:24px 30px; }}
  .header h1 {{ margin:0; font-size:22px; font-weight:700; }}
  .header p {{ margin:6px 0 0; opacity:0.9; font-size:14px; }}
  .body {{ padding:24px 30px; }}
  .summary {{ color:#1f2937; font-size:15px; line-height:1.7; white-space:pre-wrap; }}
  .points {{ background:#eff6ff; border-radius:8px; padding:20px 24px; margin:20px 0; }}
  .points h3 {{ margin:0 0 12px; color:#1e40af; font-size:16px; }}
  .points ul {{ margin:0; padding-left:20px; }}
  .footer {{ text-align:center; padding:16px 30px; color:#6b7280; font-size:12px; border-top:1px solid #e5e7eb; }}
</style></head>
<body>
<div class="container">
  <div class="header">
    <h1>{subject}</h1>
    <p>Your daily reading summary — read in 5 minutes</p>
  </div>
  <div class="body">
    <div class="summary">{summary}</div>
    <div class="points">
      <h3>Key Takeaways</h3>
      <ul>{points_html}</ul>
    </div>
  </div>
  <div class="footer">
    <p>Books Daily Updates — Read smarter, not harder</p>
    <p>To change notification settings, visit your dashboard.</p>
  </div>
</div>
</body>
</html>"""

        return self.send_email(to_email, subject, html)


class TelegramNotifier:
    def __init__(self):
        self.bot_token = None
        self._load_config()

    def _load_config(self):
        try:
            from backend.config import settings
            self.bot_token = settings.telegram_bot_token
        except Exception:
            self.bot_token = None

    def is_configured(self) -> bool:
        return bool(self.bot_token)

    def send_message(self, chat_id: str, text: str) -> bool:
        if not self.is_configured():
            logger.warning("Telegram not configured. Skipping.")
            return False
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            with httpx.Client(timeout=15) as client:
                resp = client.post(url, json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                })
                if resp.status_code == 200:
                    logger.info("Telegram message sent to %s", chat_id)
                    return True
                logger.warning("Telegram API error: %s", resp.text)
                return False
        except Exception as e:
            logger.error("Telegram send failed: %s", e)
            return False

    def send_daily_reading(self, chat_id: str, book_title: str, chapter_num: int,
                            chapter_title: Optional[str], summary: str,
                            key_points: List[str]) -> bool:
        text = f"<b>📚 {book_title}</b>\n"
        text += f"<b>Chapter {chapter_num}</b>"
        if chapter_title:
            text += f": {chapter_title}"
        text += "\n\n"
        text += f"{summary[:800]}..."
        if key_points:
            text += "\n\n<b>Key Takeaways:</b>\n"
            for p in key_points:
                text += f"• {p}\n"
        text += "\n\n#DailyReading #BookSummary"
        return self.send_message(chat_id, text)


class WhatsAppNotifier:
    def __init__(self):
        self.account_sid = None
        self.auth_token = None
        self.from_number = None
        self._load_config()

    def _load_config(self):
        try:
            from backend.config import settings
            self.account_sid = settings.twilio_account_sid
            self.auth_token = settings.twilio_auth_token
            self.from_number = settings.twilio_whatsapp_number
        except Exception:
            pass

    def is_configured(self) -> bool:
        return bool(self.account_sid and self.auth_token and self.from_number)

    def send_whatsapp(self, to_number: str, message: str) -> bool:
        if not self.is_configured():
            logger.warning("WhatsApp not configured. Skipping.")
            return False
        try:
            from twilio.rest import Client
            client = Client(self.account_sid, self.auth_token)
            msg = client.messages.create(
                body=message,
                from_=f"whatsapp:{self.from_number}",
                to=f"whatsapp:{to_number}",
            )
            logger.info("WhatsApp sent to %s: SID %s", to_number, msg.sid)
            return True
        except Exception as e:
            logger.error("WhatsApp send failed: %s", e)
            return False


email_notifier = EmailNotifier()
telegram_notifier = TelegramNotifier()
whatsapp_notifier = WhatsAppNotifier()
