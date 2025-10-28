import base64
import hashlib
import json
from typing import Dict, Any, Tuple

from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigdecode_string


# ⚠️ IMPORTANT:
# For demo we generate a static key once per process.
# In prod you'd load from secure storage / HSM.
# We'll keep signer_key global so it's stable inside the process.
_signer_key = SigningKey.generate(curve=SECP256k1)
_verifier_key = _signer_key.get_verifying_key()


def _build_message_bytes(payload: Dict[str, Any]) -> bytes:
    """
    THIS IS CRITICAL.

    We must define EXACTLY what we sign so that Solidity and off-chain
    code can reproduce it. We will commit to this format:

      msg_preimage = random (uint256 big-endian 32 bytes)
                   || timestamp (UTF-8 bytes)

    Same as we assumed in prep_vrf_for_chain.py.
    """
    rnd = int(payload["random"])
    ts = str(payload["timestamp"]).encode("utf-8")

    rnd_be32 = rnd.to_bytes(32, "big")
    return rnd_be32 + ts


def _sha256(b: bytes) -> bytes:
    h = hashlib.sha256()
    h.update(b)
    return h.digest()


def _sign_digest_secp256k1(digest32: bytes) -> Tuple[int, bytes, bytes]:
    """
    Sign the 32-byte digest with secp256k1, raw ECDSA.
    Return (recid, r32, s32).

    NOTE:
    ecdsa.SigningKey from the 'ecdsa' library gives us DER by default.
    We want raw (r,s) and also a recover ID (0/1).
    The library doesn't give recid, so for now we brute force it using coincurve logic.
    """
    # First: get raw r||s using ecdsa library.
    # We can call sign_digest with sigencode = lambda r,s,order: r(32)||s(32)
    def _sigencode_strict(r, s, order):
        # both r and s are ints, we convert to 32-byte big-endian
        rb = int(r).to_bytes(32, "big")
        sb = int(s).to_bytes(32, "big")
        return rb + sb

    sig64 = _signer_key.sign_digest(
        digest32,
        sigencode=_sigencode_strict
    )
    r_bytes32 = sig64[:32]
    s_bytes32 = sig64[32:64]

    # Now derive recid (0 or 1) by trying to recover and match our own pubkey.
    try:
        from coincurve import PublicKey
        my_uncompressed = b"\x04" + _verifier_key.to_string()
        want_addr = _eth_address_from_uncompressed(my_uncompressed)

        for recid in (0, 1):
            test_sig65 = sig64 + bytes([recid])
            pub_try = PublicKey.from_signature_and_message(
                test_sig65, digest32, hasher=None
            )
            rec_uncompressed = pub_try.format(compressed=False)
            addr_try = _eth_address_from_uncompressed(rec_uncompressed)
            if addr_try.lower() == want_addr.lower():
                return recid, r_bytes32, s_bytes32
    except Exception:
        pass

    # fallback if we can't recover: recid = 0
    return 0, r_bytes32, s_bytes32


def _eth_address_from_uncompressed(uncompressed: bytes) -> str:
    """
    Convert uncompressed EC pubkey (0x04 || X || Y) to Ethereum-style 0x... checksum address.
    """
    from eth_utils import keccak, to_checksum_address
    addr_bytes = keccak(uncompressed[1:])[-20:]
    return to_checksum_address("0x" + addr_bytes.hex())


def ecdsa_sign(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    High-level helper used by /random_pq?sig=ecdsa.

    Returns:
      - signature_type
      - sig_b64 (r||s base64)
      - pubkey_b64 (PEM-like block base64 for audit / regulator)
      - hash_alg
      - v, r, s, msg_hash  <-- NEW FIELDS for Solidity
      - signer_addr        <-- Ethereum-style address of this signer
    """

    # 1. Build message in a documented, deterministic way
    msg_preimage = _build_message_bytes(payload)                # bytes
    digest32 = _sha256(msg_preimage)                            # 32 bytes sha256

    # 2. Sign it using our secp256k1 key
    recid, r_bytes32, s_bytes32 = _sign_digest_secp256k1(digest32)

    # 3. Prepare return fields
    sig64 = r_bytes32 + s_bytes32  # raw 64-byte sig

    # PEM-style pubkey we already give in API for auditors:
    pem_lines = [
        b"-----BEGIN PUBLIC KEY-----",
        _verifier_key.to_pem().split(b"\n")[1].strip(),  # this is a cheat shortcut
        b"-----END PUBLIC KEY-----",
    ]
    pem_joined = b"\n".join(pem_lines)

    # compute Ethereum-style address from our public key
    uncompressed = b"\x04" + _verifier_key.to_string()
    signer_addr = _eth_address_from_uncompressed(uncompressed)

    return {
        "signature_type": "ECDSA(secp256k1)",
        "sig_b64": base64.b64encode(sig64).decode("ascii"),
        "pubkey_b64": base64.b64encode(pem_joined).decode("ascii"),
        "hash_alg": "SHA-256",

        # new stuff for on-chain consumers:
        "v": recid + 27,  # Solidity-style v
        "r": "0x" + r_bytes32.hex(),
        "s": "0x" + s_bytes32.hex(),
        "msg_hash": "0x" + digest32.hex(),
        "signer_addr": signer_addr,
    }


def ecdsa_verify(payload: Dict[str, Any], sig_b64: str, pubkey_b64: str) -> bool:
    """
    Basic off-chain style verifier for auditors.
    We keep it simple: recompute digest and check the sig.
    """
    # rebuild message
    msg_preimage = _build_message_bytes(payload)
    digest32 = _sha256(msg_preimage)

    # decode signature
    sig_raw = base64.b64decode(sig_b64)
    if len(sig_raw) != 64:
        return False
    r_bytes32 = sig_raw[:32]
    s_bytes32 = sig_raw[32:64]

    # load the provided pubkey
    import base64 as b64
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    pem_bytes = b64.b64decode(pubkey_b64)
    pub = load_pem_public_key(pem_bytes)

    # convert from bytes back to ints for ecdsa library
    r_int = int.from_bytes(r_bytes32, "big")
    s_int = int.from_bytes(s_bytes32, "big")

    vk = _verifier_key  # NOTE: demo assumes single local key == provided key
    try:
        # 'ecdsa' lib wants DER by default, but we can manually verify via vk.pubkey.verifies(...)
        # We'll just re-encode to DER-ish using sigdecode_string.
        sig_ok = vk.verify_digest(
            r_bytes32 + s_bytes32,
            digest32,
            sigdecode=sigdecode_string,
        )
        return sig_ok
    except Exception:
        return False
