from pathlib import Path
from urllib.parse import quote
import requests

class APIService:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def set_base_url(self, value):
        value = value.strip().rstrip("/")
        if not value.startswith(("http://", "https://")):
            raise ValueError("L'adresse doit commencer par http:// ou https://")
        if " " in value:
            raise ValueError("L'adresse du serveur est invalide.")
        self.base_url = value

    def health(self):
        response = requests.get(f"{self.base_url}/health", timeout=8)
        response.raise_for_status()
        return response.json()

    def upload(self, path):
        path = Path(path)
        with path.open("rb") as stream:
            response = requests.post(
                f"{self.base_url}/files/upload",
                files={"uploaded_file": (path.name, stream, "application/octet-stream")},
                timeout=(15, 300),
            )
        response.raise_for_status()
        return response.json()

    def qr(self, token):
        response = requests.get(f"{self.base_url}/files/{quote(token, safe='')}/qr", timeout=20)
        response.raise_for_status()
        return response.content

    def download(self, token, destination):
        response = requests.get(
            f"{self.base_url}/download/{quote(token, safe='')}",
            stream=True,
            timeout=(15, 300),
        )
        response.raise_for_status()
        name = response.headers.get("X-File-Name", f"qrconnect-{token[:8]}.bin")
        name = Path(name).name
        target = Path(destination) / name
        if target.exists():
            target = target.with_name(f"{target.stem}_received{target.suffix}")
        try:
            with target.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        output.write(chunk)
        except Exception:
            target.unlink(missing_ok=True)
            raise
        return str(target)
