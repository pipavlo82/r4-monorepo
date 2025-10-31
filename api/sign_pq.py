import base64, json

# --- optional import of liboqs-python ---
try:
    import oqs  # noqa: F401
    _OQS_OK = True
except Exception as e:
    oqs = None
    _OQS_OK = False
    _OQS_ERR = e

ALG = "ML-DSA-65"

_SIGNER = None
_PK = None  # public key bytes

def _msg_bytes(payload: dict) -> bytes:
    m = {
        "random": int(payload["random"]),
        "timestamp": payload["timestamp"],
        "hash_alg": payload.get("hash_alg", "SHA-256"),
    }
    return json.dumps(m, separators=(",", ":")).encode()

def _ensure_keys():
    global _SIGNER, _PK
    if not _OQS_OK:
        return
    if _SIGNER is None:
        s = oqs.Signature(ALG)
        _PK = s.generate_keypair()     # returns public key bytes
        _SIGNER = s                    # keep signer with secret in memory

def pq_sign(payload: dict) -> dict:
    """
    Повертає PQ-підпис, якщо liboqs доступний.
    Якщо НІ — не падаємо: віддаємо pq_available=False (для CI).
    """
    if not _OQS_OK:
        return {
            "pq_available": False,
            "pq_error": str(_OQS_ERR),
            "pq_scheme": ALG,
        }

    _ensure_keys()
    msg = _msg_bytes(payload)
    sig = _SIGNER.sign(msg)  # liboqs не вимагає явно передавати секретний ключ

    return {
        "pq_available": True,
        "pq_scheme": ALG,
        "sig_pq_b64": base64.b64encode(sig).decode(),
        "pq_pubkey_b64": base64.b64encode(_PK).decode(),
    }
