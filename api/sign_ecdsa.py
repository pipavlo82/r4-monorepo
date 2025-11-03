# api/sign_ecdsa.py
import os, json
from eth_utils import keccak, to_checksum_address
from eth_keys import keys

# приватний ключ або дефолт
PRIV_HEX = os.getenv(
    "R4_ECDSA_PRIV",
    "0x59c6995e998f97a5a0044976f6e5b5d1b1a1a999a84c27f8b3d5a22b6d3a8d7a",  # demo
).lower()

_SK = keys.PrivateKey(bytes.fromhex(PRIV_HEX[2:] if PRIV_HEX.startswith("0x") else PRIV_HEX))
_PUB = _SK.public_key
_SIGNER = _PUB.to_checksum_address()

def _msg_bytes(payload: dict) -> bytes:
    # Фіксований порядок і назви ключів
    m = {
        "random": payload["random"],
        "timestamp": payload["timestamp"],
        "hash_alg": payload.get("hash_alg", "SHA-256"),
    }
    return json.dumps(m, separators=(",", ":")).encode()

def _eip191_hash32(digest32: bytes) -> bytes:
    assert len(digest32) == 32
    prefix = b"\x19Ethereum Signed Message:\n32"
    return keccak(prefix + digest32)

def ecdsa_sign(payload: dict) -> dict:
    """
    Повертає: v,r,s (hex), msg_hash (EIP-191 над keccak(msg)), signer_addr
    """
    msg = _msg_bytes(payload)
    digest_raw = keccak(msg)
    eth_digest = _eip191_hash32(digest_raw)

    sig = _SK.sign_msg_hash(eth_digest)
    v = 27 + sig.v  # 27/28 як у Ethereum
    r = "0x" + sig.r.to_bytes(32, "big").hex()
    s = "0x" + sig.s.to_bytes(32, "big").hex()

    return {
        "v": v,
        "r": r,
        "s": s,
        "msg_hash": "0x" + eth_digest.hex(),  # КЛАДЕМО САМЕ EIP-191 ХЕШ
        "signer_addr": _SIGNER,
    }
