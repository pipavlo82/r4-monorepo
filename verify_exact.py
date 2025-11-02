#!/usr/bin/env python3
import json, base64, sys
from hashlib import sha256
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives import serialization, hashes

# Читає response.json поруч (або можна передати файл як аргумент)
resp_path = Path("response.json")
if not resp_path.exists():
    print("response.json not found"); sys.exit(2)
resp = json.loads(resp_path.read_text())

# Побудова точного повідомлення — дефолтний json (з пробілами), sort_keys=True
msg = json.dumps({"random": resp["random"], "timestamp": resp["timestamp"]}, sort_keys=True).encode()
print("MESSAGE:", msg.decode())
print("sha256:", sha256(msg).hexdigest())

# Підпис (base64) → raw 64 → DER
sig_raw = base64.b64decode(resp["sig_b64"])
if len(sig_raw) == 64:
    r = int.from_bytes(sig_raw[:32], "big")
    s = int.from_bytes(sig_raw[32:], "big")
    sig = utils.encode_dss_signature(r, s)
else:
    sig = sig_raw

# Публічний ключ беремо з pubkey.pem поруч
pem_path = Path("pubkey.pem")
if not pem_path.exists():
    print("pubkey.pem not found"); sys.exit(3)
pub = serialization.load_pem_public_key(pem_path.read_bytes())

# Верифікація
try:
    pub.verify(sig, msg, ec.ECDSA(hashes.SHA256()))
    print("VERIFIED ✅")
    sys.exit(0)
except Exception as e:
    print("VERIFY FAILED ❌", e)
    sys.exit(1)
