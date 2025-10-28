import os
import time
import secrets
import hashlib
import json

from fastapi import FastAPI, Request, Query, HTTPException
from pydantic import BaseModel

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from dotenv import load_dotenv

from api.sign_ecdsa import ecdsa_sign, ecdsa_verify
from api.sign_dilithium import dilithium_sign, dilithium_verify, PQ_AVAILABLE

# -------------------------------------------------
# ENV / CONFIG
# -------------------------------------------------
load_dotenv()
API_KEY    = os.getenv("API_KEY", "demo")
RATE_LIMIT = os.getenv("RATE_LIMIT", "30/minute")
PORT       = int(os.getenv("PORT", "8081"))

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
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

def _now_iso_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _random_hex_256_bits():
    return secrets.token_hex(32)

def _random_u32():
    return int.from_bytes(secrets.token_bytes(4), "little")

# -------------------------------------------------
# Public/basic endpoints
# -------------------------------------------------

@app.get("/version")
@limiter.limit("10/minute")
def version(request: Request):
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
    rnd_hex = _random_hex_256_bits()
    ts     = _now_timestamp_utc()
    return {
        "random_hex": rnd_hex,
        "timestamp":  ts
    }

@app.get("/metrics")
@limiter.limit("60/minute")
def metrics(request: Request):
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
    /random_pq:
    - sig=ecdsa     -> classic ECDSA(secp256k1)
    - sig=dilithium -> post-quantum Dilithium3 (if available)

    We now also expose on-chain fields (v,r,s,msg_hash,signer_addr)
    for sig=ecdsa so Solidity can verify with ecrecover.
    """

    # --- auth (basic API key gate like your 8080 node does) ---
    header_key = request.headers.get("x-api-key")
    if header_key not in (API_KEY,):
        # still allow demo mode if you want public? if no -> uncomment below
        # raise HTTPException(status_code=401, detail="invalid key")
        pass

    rnd_int = _random_u32()
    ts_iso  = _now_iso_utc()

    payload = {
        "random":    rnd_int,
        "timestamp": ts_iso
    }

    # ECDSA path (with on-chain fields)
    if sig == "ecdsa":
        proof = ecdsa_sign(payload)
        return {
            # core randomness data
            "random":          payload["random"],
            "timestamp":       payload["timestamp"],

            # signing metadata (human / audit)
            "signature_type":  proof["signature_type"],
            "sig_b64":         proof["sig_b64"],
            "pubkey_b64":      proof["pubkey_b64"],
            "hash_alg":        proof["hash_alg"],

            # on-chain verification data
            "msg_hash":        proof["msg_hash"],      # sha256(message_preimage)
            "v":               proof["v"],             # uint8 (27 or 28)
            "r":               proof["r"],             # 0x...
            "s":               proof["s"],             # 0x...
            "signer_addr":     proof["signer_addr"],   # 0x... Ethereum-style

            "pq_mode":         False
        }

    # Dilithium (post-quantum) path
    if sig == "dilithium":
        if not PQ_AVAILABLE:
            return {
                "error": "Dilithium3 signature not available on this build",
                "pq_required": True,
                "status": 501,
                "hint": "Enterprise / FIPS 204 build required"
            }

        proof = dilithium_sign(payload)
        return {
            "random":          payload["random"],
            "timestamp":       payload["timestamp"],
            "signature_type":  proof["signature_type"],
            "sig_b64":         proof["sig_b64"],
            "pubkey_b64":      proof["pubkey_b64"],
            "hash_alg":        proof["hash_alg"],
            "pq_mode":         True
        }

    # should never hit here
    raise HTTPException(status_code=400, detail="unsupported sig type")


class VerifyRequest(BaseModel):
    random: int
    timestamp: str
    signature_type: str
    sig_b64: str
    pubkey_b64: str

@app.post("/verify_pq")
@limiter.limit("30/minute")
def verify_pq(request: Request, body: VerifyRequest):
    payload = {
        "random":    body.random,
        "timestamp": body.timestamp
    }

    if body.signature_type.startswith("ECDSA"):
        ok = ecdsa_verify(payload, body.sig_b64, body.pubkey_b64)
    elif "Dilithium" in body.signature_type:
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
    uptime_s = int(time.time() - START_TIME)
    return {
        "service": "re4ctor-pq-api",
        "uptime_seconds": uptime_s,
        "modes_supported": [
            "ecdsa",
            "dilithium" if PQ_AVAILABLE else "dilithium(unavailable)"
        ],
        "fips_status": {
            "rng_core": "FIPS 140-3 ready",
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

