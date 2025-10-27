import os, base64, json, hashlib
from ecdsa import SigningKey, SECP256k1, VerifyingKey, BadSignatureError

ECDSA_PRIV_PATH = "keys/ecdsa_priv.pem"
ECDSA_PUB_PATH  = "keys/ecdsa_pub.pem"

def _load_or_create_ecdsa_keys():
    os.makedirs("keys", exist_ok=True)
    if not os.path.exists(ECDSA_PRIV_PATH):
        sk = SigningKey.generate(curve=SECP256k1)
        vk = sk.get_verifying_key()
        with open(ECDSA_PRIV_PATH, "wb") as f:
            f.write(sk.to_pem())
        with open(ECDSA_PUB_PATH, "wb") as f:
            f.write(vk.to_pem())
    with open(ECDSA_PRIV_PATH, "rb") as f:
        sk = SigningKey.from_pem(f.read())
    with open(ECDSA_PUB_PATH, "rb") as f:
        vk_pem = f.read()
    return sk, vk_pem

_sk_ecdsa, _vk_pem = _load_or_create_ecdsa_keys()

def ecdsa_sign(payload: dict) -> dict:
    """
    payload -> {"random": int, "timestamp": str}
    """
    msg_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(msg_bytes).digest()
    sig_raw = _sk_ecdsa.sign_digest(digest)
    return {
        "signature_type": "ECDSA(secp256k1)",
        "sig_b64": base64.b64encode(sig_raw).decode("ascii"),
        "pubkey_b64": base64.b64encode(_vk_pem).decode("ascii"),
        "hash_alg": "SHA-256"
    }

def ecdsa_verify(payload: dict, sig_b64: str, pubkey_b64: str) -> bool:
    msg_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(msg_bytes).digest()
    vk_pem = base64.b64decode(pubkey_b64.encode("ascii"))
    sig_raw = base64.b64decode(sig_b64.encode("ascii"))
    vk = VerifyingKey.from_pem(vk_pem)
    try:
        vk.verify_digest(sig_raw, digest, curve=SECP256k1)
        return True
    except BadSignatureError:
        return False
