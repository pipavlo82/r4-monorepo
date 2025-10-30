# Lazy/optional Dilithium3 wrapper: не валить застосунок, якщо бібліотеки нема.
import base64

def _load_mod():
    try:
        import importlib
        return importlib.import_module("pqcrypto.sign.dilithium3")
    except Exception:
        return None

# Теґ доступності для /random_pq?sig=dilithium
PQ_AVAILABLE = _load_mod() is not None

def dilithium_sign(message: bytes):
    """
    Повертає dict з полями як у ECDSA-відповіді, але з Dilithium3.
    Якщо бібліотеки нема — піднімає RuntimeError (обробляється у роутері).
    """
    m = _load_mod()
    if m is None:
        raise RuntimeError("Dilithium3 not available in this build")

    # Проста демонстраційна реалізація: генеруємо пару на льоту
    # (для продакшн — заведи й збережи ключі, або завантажуй із KMS/HSM)
    sk, pk = m.generate_keypair()
    sig = m.sign(message, sk)

    return {
        "signature_type": "Dilithium3",
        "sig_b64": base64.b64encode(sig).decode("ascii"),
        "pubkey_b64": base64.b64encode(pk).decode("ascii"),
        "pq_mode": True,
    }

def dilithium_verify(message: bytes, sig: bytes, pk: bytes) -> bool:
    m = _load_mod()
    if m is None:
        return False
    try:
        m.verify(message, sig, pk)
        return True
    except Exception:
        return False
