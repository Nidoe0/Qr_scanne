from io import BytesIO
from urllib.parse import urlencode
import qrcode
from app.config import QR_CONNECT_BASE_URL

def make_qr(token: str) -> BytesIO:
    payload = f"qrconnect://receive?{urlencode({'server': QR_CONNECT_BASE_URL, 'token': token})}"
    image = qrcode.make(payload)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
