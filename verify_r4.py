#!/usr/bin/env python3
import base64, json, sys
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from pathlib import Path

print("DEBUG: verify_r4 starting...")

resp_path = Path("response.json")
if resp_path.exists():
    print("DEBUG: loading response.json")
    RESP = json.loads(resp_path.read_text())
else:
    print("DEBUG: using embedded RESP")
    RESP = {
      "random": 3727920637,
      "timestamp": "2025-10-29T21:47:30Z",
      "signature_type": "ECDSA(secp256k1)",
      "sig_b64": "zHpyDw2wDv2ioz0LZv3eX/cIjkt5de6+r/OvjNPrOdkbhAV8RBcaIZGw+Lu7GsasB7dql6zxmAic7Mu7ylRZAg==",
      "pubkey_b64": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZZd0VBWUhLb1pJemowQ0FRWUZLNEVFQUFvRFFnQUVqVDE4ZzVIQ05la3FsSklUdXNUUmtOMml1R0NBdFg3Vy80eThKR0d3b3NNTQpENWJxMGhBOUN4Zy80ZThRN0x2TzNJNHVqc0ZPK1hDYkcyM3lKc3lGbWc9PQotLS0tLUVORCBQVUJMSUMgS0VZLS0tLS0K",
      "hash_alg": "SHA-256",
      "pq_mode": False
    }

def b64d(s): return base64.b64decode(s)

try:
    pub_pem = b64d(RESP["pubkey_b64"])
    pubkey = serialization.load_pem_public_key(pub_pem)
    print("DEBUG: public key loaded (PEM).")
except Exception as e:
    print("ERROR loading public key:", e)
    sys.exit(1)

try:
    sig_raw = b64d(RESP["sig_b64"])
    print(f"DEBUG: signature length = {len(sig_raw)} bytes")
except Exception as e:
    print("ERROR decoding signature:", e)
    sys.exit(1)

def raw_to_der(sig):
    if len(sig) == 64:
        r = int.from_bytes(sig[:32], 'big')
        s = int.from_bytes(sig[32:], 'big')
        return utils.encode_dss_signature(r, s)
    return sig

r = int(RESP["random"])
ts = str(RESP["timestamp"])

cand_msgs = []

# common textual/binary candidates
cand_msgs += [
    ("str", str(r).encode()),
    ("hex_no0x", hex(r)[2:].encode()),
    ("hex_0x", ("0x"+hex(r)[2:]).encode()),
    ("r_pipe_ts", f"{r}|{ts}".encode()),
    ("r_concat_ts", f"{r}{ts}".encode()),
    ("ts", ts.encode()),
    ("json_r_ts", json.dumps({"random": r, "timestamp": ts}, separators=(',', ':'), sort_keys=True).encode()),
    ("json_r", json.dumps({"random": r}, separators=(',', ':'), sort_keys=True).encode()),
]

r_be = r.to_bytes(4, "big")
r_le = r.to_bytes(4, "little")
cand_msgs += [
    ("uint32_be", r_be),
    ("uint32_le", r_le),
    ("be+ts", r_be + ts.encode()),
    ("le+ts", r_le + ts.encode()),
    ("ts+be", ts.encode() + r_be),
    ("ts+le", ts.encode() + r_le),
    ("be_nl", r_be + b"\n"),
    ("be_rn", r_be + b"\r\n"),
]

# add variants with small prefixes that services sometimes use
prefixes = [b"", b"R4|", b"r4|", b"random:", b"Random:", b"MSG:"]
expanded = []
for lab, m in cand_msgs:
    for p in prefixes:
        expanded.append((f"{lab}+pref({p.decode(errors='ignore')})", p + m))
cand_msgs = expanded

# Ethereum personal_sign prefix helper
def eth_prefixed(m):
    pre = b"\x19Ethereum Signed Message:\n" + str(len(m)).encode()
    return pre + m

sig_der = raw_to_der(sig_raw)

def try_verify_bytes(msg, sig, prehashed=False):
    try:
        if prehashed:
            digest = sha256(msg).digest()
            pubkey.verify(sig, digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        else:
            pubkey.verify(sig, msg, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        print("ERROR during verify:", e)
        return False

ok = False
tried = 0
print("DEBUG: trying candidates (this may take a few seconds)...")

for label, m in cand_msgs:
    tried += 1
    # normal verify (DER and raw)
    if try_verify_bytes(m, sig_der, prehashed=False):
        print(f"[OK] {label} (DER) sha256={sha256(m).hexdigest()}")
        ok = True
    if try_verify_bytes(m, sig_raw, prehashed=False):
        print(f"[OK] {label} (RAW-64) sha256={sha256(m).hexdigest()}")
        ok = True
    # try prehashed mode
    if try_verify_bytes(m, sig_der, prehashed=True):
        print(f"[OK] {label} (DER, Prehashed SHA256) sha256={sha256(m).hexdigest()}")
        ok = True
    if try_verify_bytes(m, sig_raw, prehashed=True):
        print(f"[OK] {label} (RAW-64, Prehashed SHA256) sha256={sha256(m).hexdigest()}")
        ok = True
    # try ethereum prefixed
    ethm = eth_prefixed(m)
    if try_verify_bytes(ethm, sig_der, prehashed=False):
        print(f"[OK] eth_prefixed {label} (DER) sha256={sha256(ethm).hexdigest()}")
        ok = True
    if try_verify_bytes(ethm, sig_raw, prehashed=False):
        print(f"[OK] eth_prefixed {label} (RAW-64) sha256={sha256(ethm).hexdigest()}")
        ok = True

print(f"DEBUG: tried {tried} base candidates with prefixes + eth variants.")
if not ok:
    print("❌ None matched. Next actions:")
    print("  1) поклади справжній response JSON у response.json і запусти знову")
    print("  2) або додай у відповідь поле message_b64 з точними байтами, які підписували")
    print("  3) якщо сервіс підписує тільки хеш (тобто передавався не msg а digest), то нам треба точний digest (hex)")
else:
    print("✅ At least one candidate matched.")
