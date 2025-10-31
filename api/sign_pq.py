import base64, json
import oqs

ALG = "ML-DSA-65"
SIGNER = oqs.Signature(ALG)          # 1 раз на процес
PK = SIGNER.generate_keypair()       # генеруємо публічний; секретний залишається в SIGNER

def _msg_bytes(p: dict) -> bytes:
    # Строго та стабільно серіалізуємо рівно ці три поля
    m = {
        "random": int(p["random"]),
        "timestamp": p["timestamp"],
        "hash_alg": p.get("hash_alg", "SHA-256"),
    }
    return json.dumps(m, separators=(",", ":")).encode()

def pq_sign(payload: dict) -> dict:
    msg = _msg_bytes(payload)
    sig = SIGNER.sign(msg)  # секретний ключ всередині SIGNER
    return {
        "pq_scheme": ALG,
        "sig_pq_b64": base64.b64encode(sig).decode(),
        "pq_pubkey_b64": base64.b64encode(PK).decode(),
    }
