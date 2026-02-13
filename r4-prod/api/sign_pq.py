import os
import base64

# Public stub: no real PQ signing here.
# Enterprise profile will replace this module with real ML-DSA-65 signer.
_STUB_PQ_PUBKEY_B64 = os.getenv("PQ_PUBKEY_B64", "")
_STUB_PQ_SIG_B64    = os.getenv("PQ_SIG_B64", "")

def pq_sign(msg_hash_hex: str) -> dict:
    # Return empty placeholders by default (still valid JSON fields)
    # You can set PQ_PUBKEY_B64 / PQ_SIG_B64 if you want non-empty demo blobs.
    return {
        "sig_pq_b64": _STUB_PQ_SIG_B64,
        "pq_pubkey_b64": _STUB_PQ_PUBKEY_B64,
        "pq_scheme": os.getenv("PQ_SCHEME", "ML-DSA-65(stub)"),
    }
