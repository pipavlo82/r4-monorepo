import os
import time
import json
import hashlib

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse

from .sign_ecdsa import ecdsa_sign

# PQ signer is optional in public repo
try:
    from .sign_pq import pq_sign  # type: ignore
except Exception:
    pq_sign = None  # type: ignore

router = APIRouter()


def require_key(x_api_key: str | None):
    want = os.getenv("VRF_KEY", "demo")
    if not x_api_key or x_api_key != want:
        raise HTTPException(status_code=401, detail="unauthorized")


@router.get("/version")
def version():
    return {
        "name": "re4ctor-vrf",
        "version": "0.1.0-public",
        "paths": ["/random_dual", "/random_dual_full"],
    }


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

    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    msg_hash = hashlib.sha256(payload_bytes).hexdigest()
    payload["msg_hash"] = "0x" + msg_hash

    e = ecdsa_sign(msg_hash)

    q = {}
    if pq_sign is not None:
        try:
            q = pq_sign(payload) or {}
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

    out["pq_scheme"] = q.get("pq_scheme") or q.get("scheme") or "ML-DSA-65(stub)"
    out["mode"] = "dual"
    out["version"] = "1.0"

    return JSONResponse(out)


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

    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    msg_hash = hashlib.sha256(payload_bytes).hexdigest()
    payload["msg_hash"] = "0x" + msg_hash

    e = ecdsa_sign(msg_hash)

    q = {"pq_scheme": "ML-DSA-65(stub)", "sig_pq_b64": "", "pq_pubkey_b64": ""}
    if pq_sign is not None:
        try:
            q = pq_sign(payload) or q
        except Exception:
            pass

    out = {
        "payload": payload,
        "ecdsa": {
            "v": e.get("v"),
            "r": e.get("r"),
            "s": e.get("s"),
            "msg_hash": payload["msg_hash"],
            "signer_addr": e.get("signer_addr"),
        },
        "pq": {
            "sig_pq_b64": q.get("sig_pq_b64") or q.get("pq_sig_b64") or q.get("sig_b64") or "",
            "pq_pubkey_b64": q.get("pq_pubkey_b64") or q.get("pubkey_pq_b64") or q.get("pubkey_b64_pq") or q.get("pubkey_b64") or "",
            "pq_scheme": q.get("pq_scheme") or q.get("scheme") or "ML-DSA-65(stub)",
        },
        "mode": "full",
        "version": "1.0",
    }

    return JSONResponse(out)
