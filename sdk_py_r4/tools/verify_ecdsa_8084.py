#!/usr/bin/env python3
import base64, json, requests, sys
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

HOST = "http://localhost:8084"
API_KEY = "demo"

def load_pubkey_from_double_b64(b64txt: str):
    # 1) base64-decode -> отримуємо рядок PEM
    pem_bytes = base64.b64decode(b64txt)
    # інколи це байти; зробимо завантаження напряму
    pub = serialization.load_pem_public_key(pem_bytes)
    return pub

def verify_sig(pubkey, message_bytes, sig_raw):
    # Спочатку пробуємо як DER
    try:
        pubkey.verify(sig_raw, message_bytes, ec.ECDSA(hashes.SHA256()))
        return True, "DER"
    except InvalidSignature:
        pass
    # Якщо не DER: може бути r||s (64 байти)
    if len(sig_raw) == 64:
        r = int.from_bytes(sig_raw[:32], "big")
        s = int.from_bytes(sig_raw[32:], "big")
        der = utils.encode_dss_signature(r, s)
        try:
            pubkey.verify(der, message_bytes, ec.ECDSA(hashes.SHA256()))
            return True, "raw(r||s)"
        except InvalidSignature:
            return False, "raw(r||s)"
    return False, f"unknown_len={len(sig_raw)}"

def main():
    url = f"{HOST}/random_pq?sig=ecdsa&n=32"
    r = requests.get(url, headers={"X-API-Key": API_KEY}, timeout=10)
    print("== /random_pq?sig=ecdsa ==")
    print(json.dumps(r.json(), indent=2))
    r.raise_for_status()
    data = r.json()

    # повідомлення: серіалізуємо random як текст (узгоджено з msg_hash=SHA-256(random))
    msg = str(data["random"]).encode("utf-8")

    sig_raw = base64.b64decode(data["sig_b64"])
    pub = load_pubkey_from_double_b64(data["pubkey_b64"])

    ok, mode = verify_sig(pub, msg, sig_raw)
    if ok:
        print(f"✅ ECDSA signature verified ({mode}), SHA-256 over text(random).")
    else:
        print(f"❌ Verification failed (tried as DER and r||s).")

if __name__ == "__main__":
    main()
