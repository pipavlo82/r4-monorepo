from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from dotenv import load_dotenv
import os
import secrets
import time

# ----------------------------------------
# Завантажуємо змінні з .env (API_KEY, RATE_LIMIT, PORT)
# ----------------------------------------
load_dotenv()

# ----------------------------------------
# Rate limiter + FastAPI app
# ----------------------------------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# ----------------------------------------
# Конфіг (можна буде винести в окремий config.py)
# ----------------------------------------
API_KEY = os.getenv("API_KEY", "demo")
RATE_LIMIT = os.getenv("RATE_LIMIT", "30/minute")  # скільки запитів дозволяємо
PORT = int(os.getenv("PORT", "8081"))             # не обов'язково, але зручно

# ----------------------------------------
# Службові хелпери (якщо захочемо в майбутньому робити auth)
# ----------------------------------------
def _now_timestamp_utc():
    """UTC timestamp у форматі YYYY-MM-DD HH:MM:SS (для audit / logs)."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

def _random_hex_256_bits():
    """Генерує 256 біт криптографічно безпечної випадковості у hex."""
    return secrets.token_hex(32)  # 32 bytes => 256 bits

# ----------------------------------------
# Маршрути (ендпоїнти API)
# ----------------------------------------

@app.get("/version")
@limiter.limit("10/minute")
def version(request: Request):
    """
    Healthcheck endpoint.
    Використовується інвесторами/клієнтами щоб перевірити що нода жива.
    """
    return {
        "version": "v1.0.0",
        "build": "r4-demo",
        "rate_limit": RATE_LIMIT,
        "api_key": API_KEY,
        "timestamp": _now_timestamp_utc()
    }


@app.get("/random")
@limiter.limit(RATE_LIMIT)
def random_hex(request: Request):
    """
    Основний endpoint.
    Повертає 256 біт випадковості + timestamp.
    TODO (далі): підписувати значення і додавати signature для VRF.
    """
    rnd = _random_hex_256_bits()
    ts = _now_timestamp_utc()
    return {
        "random_hex": rnd,
        "timestamp": ts
    }


# (плейсхолдер для майбутнього Prometheus /metrics)
@app.get("/metrics")
@limiter.limit("60/minute")
def metrics(request: Request):
    """
    Проста заглушка для майбутнього моніторингу.
    Потім тут будуть Prometheus метрики:
      - total_requests
      - avg_latency
      - bytes_served
    Зараз просто віддаємо статичну структуру.
    """
    return {
        "service": "re4ctor-api",
        "uptime_stub": "ok",
        "requests_per_minute_allowed": RATE_LIMIT,
    }
