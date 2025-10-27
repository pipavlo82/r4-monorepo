import os, base64, json, hashlib

# --------------------------------------------------
# Спробувати імпортувати пост-квантову бібліотеку.
# Якщо не вийшло — ми просто виставимо PQ_AVAILABLE = False.
# --------------------------------------------------
PQ_AVAILABLE = False
oqs = None

try:
    import pyoqs as oqs  # офіційні Python-біндінги до liboqs
    PQ_AVAILABLE = True
except Exception:
    try:
        import oqs as oqs  # іноді пакет називається oqs
        # перевіримо, чи там реально є Signature
        if hasattr(oqs, "Signature"):
            PQ_AVAILABLE = True
    except Exception:
        PQ_AVAILABLE = False
        oqs = None


DILITHIUM_PRIV_PATH = "keys/dilithium_priv.bin"
DILITHIUM_PUB_PATH  = "keys/dilithium_pub.bin"

_dilithium_priv = None
_dilithium_pub  = None


def _ensure_keys():
    """
    Якщо PQ недоступний — просто нічого не робимо.
    Якщо доступний — ледача генерація/завантаження ключа.
    """
    global _dilithium_priv, _dilithium_pub

    if not PQ_AVAILABLE:
        return

    if _dilithium_priv is not None and _dilithium_pub is not None:
        return

    os.makedirs("keys", exist_ok=True)

    # пробуємо завантажити
    if os.path.exists(DILITHIUM_PRIV_PATH) and os.path.exists(DILITHIUM_PUB_PATH):
        with open(DILITHIUM_PRIV_PATH, "rb") as fpriv:
            _dilithium_priv = fpriv.read()
        with open(DILITHIUM_PUB_PATH, "rb") as fpub:
            _dilithium_pub = fpub.read()
        return

    # генеруємо нові
    with oqs.Signature("Dilithium3") as signer:
        pub = signer.generate_keypair()
        priv = signer.export_secret_key()

    with open(DILITHIUM_PRIV_PATH, "wb") as fpriv:
        fpriv.write(priv)
    with open(DILITHIUM_PUB_PATH, "wb") as fpub:
        fpub.write(pub)

    _dilithium_priv = priv
    _dilithium_pub  = pub


def dilithium_sign(payload: dict) -> dict:
    """
    Якщо PQ_AVAILABLE == False -> піднімаємо RuntimeError,
    щоб апка знала що Dilithium недоступний на цій збірці.
    """
    if not PQ_AVAILABLE:
        raise RuntimeError("Dilithium not available on this build")

    _ensure_keys()

    msg_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")

    with oqs.Signature("Dilithium3") as signer:
        signer.import_secret_key(_dilithium_priv)
        sig_raw = signer.sign(msg_bytes)

    digest = hashlib.sha256(msg_bytes).digest()

    return {
        "signature_type": "Dilithium3 (FIPS 204 ML-DSA)",
        "sig_b64": base64.b64encode(sig_raw).decode("ascii"),
        "pubkey_b64": base64.b64encode(_dilithium_pub).decode("ascii"),
        "hash_alg": "SHA-256",
    }


def dilithium_verify(payload: dict, sig_b64: str, pubkey_b64: str) -> bool:
    if not PQ_AVAILABLE:
        # Якщо нема PQ, валідація Dilithium неможлива => False
        return False

    msg_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    sig_raw   = base64.b64decode(sig_b64.encode("ascii"))
    pub_raw   = base64.b64decode(pubkey_b64.encode("ascii"))

    with oqs.Signature("Dilithium3") as verifier:
        try:
            return verifier.verify(msg_bytes, sig_raw, pub_raw)
        except Exception:
            return False
