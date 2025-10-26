import os
import requests

class Client:
    """
    Легкий клієнт для Re4ctoR API.

    Використання:
        from re4ctor_client.api import Client
        c = Client()  # за замовчуванням http://localhost:8081
        print(c.get_status())
        print(c.get_random())

        # або вказати публічну ноду
        c = Client(base_url="https://demo.re4ctor.net")
    """

    def __init__(self, base_url=None):
        # Пріоритет:
        # 1) параметр конструктора
        # 2) env var R4_BASE_URL
        # 3) локальний дев-сервер (8081)
        self.base_url = (
            base_url
            or os.getenv("R4_BASE_URL")
            or "http://localhost:8081"
        )

    def get_status(self):
        """Отримати /version."""
        r = requests.get(f"{self.base_url}/version", timeout=5)
        r.raise_for_status()
        return r.json()

    def get_random(self):
        """Отримати /random."""
        r = requests.get(f"{self.base_url}/random", timeout=5)
        r.raise_for_status()
        return r.json()

    def get_metrics(self):
        """Отримати /metrics (можна для health dashboards)."""
        r = requests.get(f"{self.base_url}/metrics", timeout=5)
        r.raise_for_status()
        return r.json()
