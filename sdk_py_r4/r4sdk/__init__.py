from .client import R4Client
import requests

class R4Client:
    def __init__(self, api_key: str, host: str = "http://localhost:8080"):
        self.api_key = api_key
        self.host = host.rstrip("/")

    def get_random(self, n: int = 32) -> bytes:
        url = f"{self.host}/random?n={n}&fmt=raw"
        headers = {"X-API-Key": self.api_key}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.content
