from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
import os, time

from .sign_ecdsa import ecdsa_sign
from .sign_pq import pq_sign

router = APIRouter()

API_KEY = os.getenv("API_KEY", "demo")

def require_key(x_api_key: str | None):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

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
    q = pq_sign(payload)

    out = dict(payload)

    # ---- ECDSA (очікувані ключі; пропускаємо, якщо відсутні) ----
    for k in ("v", "r", "s", "msg_hash", "signer_addr", "pq_pubkey_b64", "sig_pq_b64"):
        if k in e:
            out[k] = e[k]

    # ---- PQ (fallback по різних назвам ключів) ----
    sig_pq = q.get("sig_pq_b64") or q.get("pq_sig_b64") or q.get("sig_pq_b64")
    if not sig_pq:
        raise HTTPException(status_code=500, detail="PQ signature missing (sig_pq_b64/pq_sig_b64/sig_b64)")
    out["sig_pq_b64"] = sig_pq

    pk_pq = (
        q.get("pq_pubkey_b64")
        or q.get("pubkey_pq_b64")
        or q.get("pubkey_b64_pq")
        or q.get("pq_pubkey_b64")
    )
    if not pk_pq:
        raise HTTPException(status_code=500, detail="PQ pubkey missing (pq_pubkey_b64/pubkey_pq_b64/pubkey_b64_pq/pubkey_b64)")
    out["pq_pubkey_b64"] = pk_pq

    out["pq_scheme"] = q.get("pq_scheme") or q.get("scheme") or "ML-DSA-65"

    return JSONResponse(out)
