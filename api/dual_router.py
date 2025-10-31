# api/dual_router.py
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
import os, time
from typing import Optional

from .sign_ecdsa import ecdsa_sign
from .sign_pq import pq_sign

router = APIRouter()

API_KEY = os.getenv("API_KEY", "demo")


def require_key(x_api_key: Optional[str]):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.get("/random_pq")
def random_pq(sig: str = "ecdsa", x_api_key: Optional[str] = Header(None)):
    """Окремий ендпойнт: або ECDSA, або PQ-підпис (для швидкої перевірки)."""
    require_key(x_api_key)

    rnd = int.from_bytes(os.urandom(4), "big")
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    payload = {
        "random": rnd,
        "timestamp": ts_iso,
        "hash_alg": "SHA-256",
    }

    s = sig.lower()
    if s == "ecdsa":
        proof = ecdsa_sign(payload)
    elif s in ("pq", "mldsa", "ml-dsa-65", "dilithium3"):
        proof = pq_sign(payload)
    else:
        raise HTTPException(status_code=400, detail="sig must be 'ecdsa' or 'pq'")

    return JSONResponse({**payload, **proof})


@router.get("/random_dual")
def random_dual(x_api_key: Optional[str] = Header(None)):
    """Подвійний доказ: ECDSA + ML-DSA-65 (коли доступний liboqs)."""
    require_key(x_api_key)

    rnd = int.from_bytes(os.urandom(4), "big")
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    payload = {
        "random": rnd,
        "timestamp": ts_iso,
        "hash_alg": "SHA-256",
        "signature_type": "ECDSA(secp256k1) + ML-DSA-65",
    }

    out = dict(payload)

    # ---- ECDSA ----
    e = ecdsa_sign(payload)
    for k in ("v", "r", "s", "msg_hash", "signer_addr", "sig_b64", "pubkey_b64", "signature_type"):
        if k in e:
            out[k] = e[k]

    # ---- PQ (ML-DSA-65) ----
    q = pq_sign(payload)
    pq_available = q.get("pq_available", True)
    out["pq_available"] = pq_available

    if pq_available:
        # підпис (допускаємо різні назви полів)
        sig_pq = q.get("sig_pq_b64") or q.get("pq_sig_b64") or q.get("sig_b64")
        if not sig_pq:
            raise HTTPException(
                status_code=500,
                detail="PQ signature missing (sig_pq_b64/pq_sig_b64/sig_b64)",
            )
        out["sig_pq_b64"] = sig_pq

        # публічний ключ (без дублю)
        pk_pq = q.get("pq_pubkey_b64") or q.get("pubkey_pq_b64") or q.get("pubkey_b64_pq")
        if pk_pq:
            out["pq_pubkey_b64"] = pk_pq

        out["pq_scheme"] = q.get("pq_scheme", "ML-DSA-65")
    else:
        # у CI без liboqs не падаємо — відмічаємо причину
        out["pq_error"] = q.get("pq_error", "liboqs not available")

    return JSONResponse(out)
