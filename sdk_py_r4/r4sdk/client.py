import requests
from typing import Optional, Literal


class R4Client:
    """
    Легкий клієнт до локального/дистанційного R4 API.

    Приклад:
        c = R4Client(api_key="demo", host="http://localhost:8080")

        # 1) сирі байти ентропії
        raw32 = c.get_random(32)

        # 2) версія / білд ноди
        info = c.get_version()

        # 3) PQ-VRF вихід з підписом (dilithium/kyber/etc)
        vrf = c.get_vrf(length=32, sig_type="dilithium")
    """

    def __init__(self, api_key: str, host: str = "http://localhost:8080"):
        # ключ доступу до API
        self.api_key = api_key
        # базова адреса (прибираємо фінальний "/")
        self.host = host.rstrip("/")

    def _headers(self):
        # стандартні заголовки для кожного запиту
        return {"X-API-Key": self.api_key}

    # -------------------------------
    # 1. /random → сирі байти
    # -------------------------------
    def get_random(self, n: int = 32) -> bytes:
        """
        Отримати n байт високоякісної ентропії як raw bytes.

        Це просто прямий стрім твого ядра.
        """
        url = f"{self.host}/random"
        params = {
            "n": n,
            "fmt": "raw",
        }
        r = requests.get(url, params=params, headers=self._headers(), timeout=10)
        r.raise_for_status()
        return r.content  # bytes

    # -------------------------------
    # 2. /version → метадані ноди
    # -------------------------------
    def get_version(self) -> dict:
        """
        Дізнатись версію/білд/uptime ноди R4.

        Очікуємо, що бекенд повертає JSON.
        Повертаємо dict як є.
        """
        url = f"{self.host}/version"
        r = requests.get(url, headers=self._headers(), timeout=5)
        r.raise_for_status()
        return r.json()

    # -------------------------------
    # 3. /random_pq → підписана випадковість
    # -------------------------------
    def get_vrf(
        self,
        length: int = 32,
        sig_type: Literal["dilithium", "kyber", "kyber512", "dilithium2", "ecdsa"] = "dilithium",
        context: Optional[str] = None,
    ) -> dict:
        """
        Отримати верифіковану випадковість (типу VRF) з PQ-підписом.

        Параметри:
            length   - бажана довжина випадкових байтів (наприклад 32)
            sig_type - схема підпису, яку хочеш ("dilithium" і т.д.)
            context  - (необов'язково) довільний стрінг, який сервер включає в payload
                       щоб ти міг довести "це було саме для цього запиту".

        Очікуваний формат відповіді від бекенда (приклад):
        {
            "random": "<hex або base64>",
            "sig": "<hex або base64>",
            "sig_type": "dilithium",
            "pubkey": "<hex або base64>",
            "timestamp": 1699999999
        }

        Ми повертаємо dict, бо там не тільки байти, а й доказ.
        """
        url = f"{self.host}/random_pq"
        params = {
            "n": length,
            "sig_type": sig_type,
        }
        if context is not None:
            params["context"] = context

        r = requests.get(url, params=params, headers=self._headers(), timeout=10)
        r.raise_for_status()
        return r.json()
