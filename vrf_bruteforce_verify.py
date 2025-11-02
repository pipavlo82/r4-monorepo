# --- QUICK EXACT VERIFICATION (added) ---
# Якщо поруч є response.json і pubkey.pem — спробуємо швидко верифікувати canonical JSON,
# щоб уникнути довгого брутфорсу.
try:
    import json, base64
    from pathlib import Path
    from hashlib import sha256
    from cryptography.hazmat.primitives.asymmetric import ec, utils
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.exceptions import InvalidSignature

    resp_path = Path("response.json")
    pem_path = Path("pubkey.pem")
    quick_verified = False

    if resp_path.exists() and pem_path.exists():
        try:
            resp = json.loads(resp_path.read_text())
            # canonical message: default json separators (with spaces), sort_keys=True
            msg = json.dumps({"random": resp["random"], "timestamp": resp["timestamp"]}, sort_keys=True).encode()
            sig_raw = base64.b64decode(resp["sig_b64"])
            if len(sig_raw) == 64:
                r = int.from_bytes(sig_raw[:32], "big")
                s = int.from_bytes(sig_raw[32:], "big")
                sig = utils.encode_dss_signature(r, s)
            else:
                sig = sig_raw
            pub = serialization.load_pem_public_key(pem_path.read_bytes())
            pub.verify(sig, msg, ec.ECDSA(hashes.SHA256()))
            print("quick-verify: VERIFIED (exact canonical JSON). Exiting — no brute force needed.")
            quick_verified = True
        except InvalidSignature:
            # not matched — continue to brute force below
            pass
        except Exception as _e:
            # fallback silently to normal flow (print minimal debug)
            print("quick-verify: skipped (error or missing fields).", str(_e))
    # If quick_verified is True, exit early
    if quick_verified:
        import sys; sys.exit(0)
except Exception:
    # if cryptography missing or import fails — continue with original script
    pass
# --- end quick block ---
