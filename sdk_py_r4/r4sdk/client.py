import requests


class R4Client:
    def __init__(self, api_key, host="http://localhost:8080"):
        self.api_key = api_key
        self.host = host
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": self.api_key})

    def get_random(self, length=32, fmt="hex"):
        """
        Get random bytes from /random endpoint.
        Supports both raw and hex output.
        """
        # 🔧 важливо: бекенд очікує параметр 'n', не 'length'
        r = self.session.get(f"{self.host}/random", params={"n": length, "fmt": fmt})
        r.raise_for_status()

        # Якщо сервер повертає JSON (fmt=hex) — парсимо
        if fmt == "hex":
            return bytes.fromhex(r.text.strip())
        else:
            return r.content


if __name__ == "__main__":
    client = R4Client(api_key="demo", host="http://localhost:8082")
    try:
        rand = client.get_random(16)
        print("🔐 Random bytes:", rand.hex())
    except Exception as e:
        print("❌ Error:", e)
