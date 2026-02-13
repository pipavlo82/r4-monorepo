import os
import json
import hashlib
from typing import Any, Dict, Union

from eth_keys import keys
from eth_utils import to_checksum_address

# Demo key (НЕ production). Можеш перевизначити через ECDSA_PRIVKEY=0x...
_DEFAULT_DEMO_PRIV = "0x59c6995e998f97a5a0044966f094538b292a2e2b0f1b9b7a0f6f4b9b9b2e8d4a"


def _get_privkey() -> keys.PrivateKey:
    k = os.getenv("ECDSA_PRIVKEY", _DEFAULT_DEMO_PRIV).strip()
    if not k.startswith("0x"):
        k = "0x" + k
    raw = bytes.fromhex(k[2:])
    if len(raw) != 32:
        raise ValueError("ECDSA_PRIVKEY must be 32 bytes hex (64 hex chars)")
    return keys.PrivateKey(raw)


def _hash_payload(payload: Dict[str, Any]) -> bytes:
    # deterministic: sha256(canonical_json(payload))
    b = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(b).digest()


def ecdsa_sign(msg: Union[str, Dict[str, Any]]) -> dict:
    """
    Sign either:
      - 32-byte hash hex string (with or without 0x), OR
      - payload dict (we will hash it deterministically).
    Returns {v,r,s,msg_hash,signer_addr}.
    """
    if isinstance(msg, dict):
        digest = _hash_payload(msg)
    else:
        h = msg.strip()
        if h.startswith("0x"):
            h = h[2:]
        digest = bytes.fromhex(h)
        if len(digest) != 32:
            raise ValueError("msg_hash_hex must be 32 bytes (64 hex chars)")

    pk = _get_privkey()
    sig = pk.sign_msg_hash(digest)

    v = int(sig.v) + 27  # eth_keys gives 0/1
    r = "0x" + int(sig.r).to_bytes(32, "big").hex()
    s = "0x" + int(sig.s).to_bytes(32, "big").hex()

    signer_addr = to_checksum_address(pk.public_key.to_address())
    msg_hash = "0x" + digest.hex()

    return {
        "v": v,
        "r": r,
        "s": s,
        "msg_hash": msg_hash,
        "signer_addr": signer_addr,
    }
