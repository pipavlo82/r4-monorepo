import os
import time
import secrets
import hashlib
import json

from fastapi import FastAPI, Request, Query
from pydantic import BaseModel

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from dotenv import load_dotenv

# локальні модулі підпису
from api.sign_ecdsa import ecdsa_sign, ecdsa_verify
from api.sign_dilithium import dilithium_sign, dilithium_verify, PQ_AVAILABLE


# -------------------------------------------------
# ENV / CONFIG
# -------------------------------------------------
load_dotenv()

API_KEY    = os.getenv("API_KEY", "demo")
RATE_LIMIT = os.getenv("RATE_LIMIT", "30/minute")  # напр. "30/minute"
PORT       = int(os.getenv("PORT", "8081"))        # інформативно, uvicorn задає порт при запуску

# -------------------------------------------------
# Rate Limiter + FastAPI app
# -------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="re4ctor / R4PQ API",
    description=(
        "High-throughput entropy API with optional provable fairness.\n"
        "Supports classic ECDSA(secp256k1) and post-quantum Dilithium3 (FIPS 204 ML-DSA).\n"
        "Use /random for raw entropy; /random_pq for signed entropy."
    ),
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

START_TIME = time.time()


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _now_timestamp_utc():
    """UTC timestamp у форматі YYYY-MM-DD HH:MM:SS (для /version, /random)."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

def _now_iso_utc():
    """UTC ISO timestamp (Z-секундами) для підписаних раундів."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _random_hex_256_bits():
    """256 біт криптографічно сильного рандому у hex (32 байти -> 64 hex chars)."""
    return secrets.token_hex(32)

def _random_u32():
    """32-бітне криптографічно сильне число як int. Зручно для ігор/лотерей."""
    return int.from_bytes(secrets.token_bytes(4), "little")


# -------------------------------------------------
# Legacy / public endpoints (твоя поточна поведінка)
# -------------------------------------------------

@app.get("/version")
@limiter.limit("10/minute")
def version(request: Request):
    """
    Healthcheck endpoint.
    Це те, що клієнти/інвестори вже можуть викликати, щоб побачити що нода жива.
    Ми не ламаємо існуючий формат.
    """
    return {
        "version":    "v1.0.0",
        "build":      "r4-demo",
        "rate_limit": RATE_LIMIT,
        "api_key":    API_KEY,
        "timestamp":  _now_timestamp_utc()
    }


@app.get("/random")
@limiter.limit(RATE_LIMIT)
def random_hex(request: Request):
    """
    Основний endpoint (історичний/простий).
    Повертає 256 біт випадковості + timestamp.
    Без криптопідпису.
    """
    rnd_hex = _random_hex_256_bits()
    ts     = _now_timestamp_utc()
    return {
        "random_hex": rnd_hex,
        "timestamp":  ts
    }


@app.get("/metrics")
@limiter.limit("60/minute")
def metrics(request: Request):
    """
    Легка метрика для старого режиму.
    """
    uptime_s = int(time.time() - START_TIME)
    return {
        "service": "re4ctor-api",
        "uptime_seconds": uptime_s,
        "requests_per_minute_allowed": RATE_LIMIT,
    }


# -------------------------------------------------
# PQ / Provably Fair endpoints
# -------------------------------------------------

@app.get("/random_pq")
@limiter.limit(RATE_LIMIT)
def random_pq(
    request: Request,
    sig: str = Query("dilithium", enum=["ecdsa", "dilithium"])
):
    """
    НОВИЙ endpoint для гемблінгу / аудиторів / інвесторів.

    Повертає випадкове число + криптографічний підпис:
    - sig=ecdsa       -> класичний підпис ECDSA(secp256k1)
    - sig=dilithium   -> пост-квантовий підпис Dilithium3 (FIPS 204 ML-DSA)
                         якщо PQ_AVAILABLE == True

    Якщо Dilithium не зібраний на цій машині, повернемо статус 501 у JSON,
    замість того щоб падати.
    """

    rnd_int = _random_u32()
    ts_iso  = _now_iso_utc()

    payload = {
        "random":    rnd_int,
        "timestamp": ts_iso
    }

    if sig == "ecdsa":
        proof = ecdsa_sign(payload)
        return {
            "random":          payload["random"],
            "timestamp":       payload["timestamp"],
            "signature_type":  proof["signature_type"],          # "ECDSA(secp256k1)"
            "sig_b64":         proof["sig_b64"],
            "pubkey_b64":      proof["pubkey_b64"],
            "hash_alg":        proof["hash_alg"],                # "SHA-256"
            "pq_mode":         False
        }

    # sig == "dilithium"
    if not PQ_AVAILABLE:
        # graceful fallback: PQ оголошена як фіча, але не зібрана тут
        return {
            "error": "Dilithium3 signature not available on this build",
            "pq_required": True,
            "status": 501,
            "hint": "Enterprise / FIPS 204 build required"
        }

    # Якщо PQ_AVAILABLE = True, генеруємо пост-квантовий підпис
    proof = dilithium_sign(payload)
    return {
        "random":          payload["random"],
        "timestamp":       payload["timestamp"],
        "signature_type":  proof["signature_type"],              # "Dilithium3 (FIPS 204 ML-DSA)"
        "sig_b64":         proof["sig_b64"],
        "pubkey_b64":      proof["pubkey_b64"],
        "hash_alg":        proof["hash_alg"],                    # "SHA-256"
        "pq_mode":         True
    }


class VerifyRequest(BaseModel):
    random: int
    timestamp: str
    signature_type: str
    sig_b64: str
    pubkey_b64: str


@app.post("/verify_pq")
@limiter.limit("30/minute")
def verify_pq(request: Request, body: VerifyRequest):
    """
    Аудитор / гравець / регулятор надсилає:
      - random
      - timestamp
      - signature_type
      - sig_b64
      - pubkey_b64

    Ми відповідаємо valid: true/false.
    Підтримуємо обидва типи: ECDSA та Dilithium3.
    """

    payload = {
        "random":    body.random,
        "timestamp": body.timestamp
    }

    if body.signature_type.startswith("ECDSA"):
        ok = ecdsa_verify(payload, body.sig_b64, body.pubkey_b64)
    elif "Dilithium" in body.signature_type:
        # Якщо Dilithium недоступний у цій збірці, вважаймо невалідним,
        # бо верифайер не може перевірити підпис.
        if not PQ_AVAILABLE:
            ok = False
        else:
            ok = dilithium_verify(payload, body.sig_b64, body.pubkey_b64)
    else:
        ok = False

    return {
        "valid": ok,
        "checked_at": _now_iso_utc()
    }


@app.get("/metrics_pq")
@limiter.limit("60/minute")
def metrics_pq(request: Request):
    """
    PQ-facing метрики / маркетинг для ліцензіара казино.
    Показуємо стан PQ-режиму чесно.
    """
    uptime_s = int(time.time() - START_TIME)
    return {
        "service": "re4ctor-pq-api",
        "uptime_seconds": uptime_s,
        "modes_supported": [
            "ecdsa",
            "dilithium" if PQ_AVAILABLE else "dilithium(unavailable)"
        ],
        "fips_status": {
            # rng_core - це твоя історія про те що ядро готується під FIPS 140-3
            "rng_core": "FIPS 140-3 ready",
            # pq_signature - це наша маркетингова правда:
            # якщо PQ_AVAILABLE == False -> ця конкретна збірка без liboqs
            "pq_signature": (
                "FIPS 204 (Dilithium3 class)"
                if PQ_AVAILABLE else
                "Not enabled in this build"
            ),
        },
        "note": (
            "Use /random_pq for signed randomness and /verify_pq for round audit. "
            "sig=dilithium requires enterprise PQ build."
        ),
    }
