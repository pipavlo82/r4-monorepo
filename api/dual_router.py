# api/dual_router.py
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
import os, time

from .sign_ecdsa import ecdsa_sign
from .sign_pq import pq_sign  # optional

router = APIRouter()
API_KEY = os.getenv("API_KEY", "demo")


def require_key(x_api_key: str | None):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ============================================================
#               SIMPLE DUAL ENDPOINT
# ============================================================
@router.get("/random_dual")
def random_dual(x_api_key: str | None = Header(None)):
    require_key(x_api_key)

    rnd = int.from_bytes(os.urandom(4), "big")
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    payload = {
        "random": rnd,
        "timestamp": ts_iso,
        "hash_alg": "SHA-256",
        "signature_type": "ECDSA(secp256k1) + ML-DSA-65",
    }

    e = ecdsa_sign(payload)

    try:
        q = pq_sign(payload)
    except Exception:
        q = {}

    out = dict(payload)

    # ECDSA mandatory fields
    for k in ("v", "r", "s", "msg_hash", "signer_addr"):
        if k in e:
            out[k] = e[k]

    # PQ flexible fields
    sig_pq = q.get("sig_pq_b64") or q.get("pq_sig_b64") or q.get("sig_b64")
    if sig_pq:
        out["sig_pq_b64"] = sig_pq

    pk_pq = (
        q.get("pq_pubkey_b64")
        or q.get("pubkey_pq_b64")
        or q.get("pubkey_b64_pq")
        or q.get("pubkey_b64")
    )
    if pk_pq:
        out["pq_pubkey_b64"] = pk_pq

    if "pq_scheme" in q or "scheme" in q:
        out["pq_scheme"] = q.get("pq_scheme") or q.get("scheme")

    out["mode"] = "dual"
    out["version"] = "1.0"

    return JSONResponse(out)


# ============================================================
#               FULL DEBUG ENDPOINT
# ============================================================
@router.get("/random_dual_full")
def random_dual_full(x_api_key: str | None = Header(None)):
    require_key(x_api_key)

    rnd = int.from_bytes(os.urandom(4), "big")
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    payload = {
        "random": rnd,
        "timestamp": ts_iso,
        "hash_alg": "SHA-256",
        "signature_type": "ECDSA(secp256k1) + ML-DSA-65",
    }

    e = ecdsa_sign(payload)

    try:
        q = pq_sign(payload)
    except Exception:
        q = {"pq_available": False, "pq_error": "Cannot sign"}

    return JSONResponse({
        "payload": payload,
        "ecdsa": e,
        "pq": q,
        "mode": "full",
        "version": "1.0"
    })
