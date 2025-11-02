#!/usr/bin/env python3
# sdk_py_r4/r4sdk/vrf.py
# Простий verifier для відповіді /random_pq?sig=ecdsa (compact JSON sign)
import json
import base64
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

def build_signed_message(random_int, timestamp):
    """
    Формує байт-стрічку, яку підписує сервер:
    JSON compact, сортування ключів, без пробілів.
    """
    return json.dumps({"random": int(random_int), "timestamp": str(timestamp)}, separators=(",",":"), sort_keys=True).encode()

def verify_ecdsa_from_response(resp):
    """
    Перевіряє sig_b64 / pubkey_b64 в відповіді сервера.
    Повертає (True/False, reason_str).
    Підтримує:
      - raw r||s (64 байти) -> DER -> verify(msg, SHA-256)
      - DER signature (try direct)
      - prehashed SHA256(msg)
    """
    try:
        sig_b64 = resp["sig_b64"]
        pub_b64 = resp["pubkey_b64"]
    except KeyError as e:
        return False, f"missing field: {e}"

    sig = base64.b64decode(sig_b64)
    pem = base64.b64decode(pub_b64)
    pubkey = serialization.load_pem_public_key(pem)

    msg = build_signed_message(resp["random"], resp.get("timestamp", ""))

    # try: raw r||s (64 bytes) -> DER
    if len(sig) >= 64:
        rs = sig[:64]
        r = int.from_bytes(rs[:32], "big")
        s = int.from_bytes(rs[32:64], "big")
        der = utils.encode_dss_signature(r, s)
        try:
            pubkey.verify(der, msg, ec.ECDSA(hashes.SHA256()))
            return True, "verified: raw r||s -> DER on message (sha256 over msg)"
        except InvalidSignature:
            pass
        # try pre-hashed verification (sha256(msg))
        try:
            digest = hashlib.sha256(msg).digest()
            pubkey.verify(der, digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
            return True, "verified: raw r||s -> DER on prehashed(SHA256(msg))"
        except InvalidSignature:
            pass

    # try signature as DER directly (server might return DER b64)
    try:
        pubkey.verify(sig, msg, ec.ECDSA(hashes.SHA256()))
        return True, "verified: signature as DER on msg (sha256)"
    except InvalidSignature:
        pass
    except Exception as e:
        # other errors from crypto lib
        return False, f"crypto error: {e}"

    # fallback failed
    return False, "no verification method matched"
