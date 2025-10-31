#!/usr/bin/env python3
import base64, json, sys, datetime
from hashlib import sha256
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature

def b64d(s): return base64.b64decode(s)

# load inputs
resp = json.loads(Path("response.json").read_text())
pub_pem = Path("pubkey.pem").read_bytes()
pubkey = serialization.load_pem_public_key(pub_pem)

sig_raw = b64d(resp["sig_b64"])
def raw_to_der(sig):
    if len(sig)==64:
        r=int.from_bytes(sig[:32],"big"); s=int.from_bytes(sig[32:],"big")
        return utils.encode_dss_signature(r,s)
    return sig
sig_der = raw_to_der(sig_raw)

r = int(resp["random"])
ts = str(resp["timestamp"])

# timestamp → unix
def parse_iso8601_z(s):
    if s.endswith("Z"): s=s[:-1]+"+00:00"
    return datetime.datetime.fromisoformat(s)
try:
    dt = parse_iso8601_z(ts)
    unix  = int(dt.timestamp())
    unix_ms = int(dt.timestamp()*1000)
except Exception:
    unix = unix_ms = None

cands = []
# text
cands += [
    ("str", str(r).encode()),
    ("hex", hex(r)[2:].encode()),
    ("0xhex", ("0x"+hex(r)[2:]).encode()),
    ("r|ts", f"{r}|{ts}".encode()),
    ("r ts", f"{r} {ts}".encode()),
    ("r,ts", f"{r},{ts}".encode()),
    ("r\\tts", f"{r}\t{ts}".encode()),
    ("ts", ts.encode()),
]
# json
cands += [
    ("json_min", json.dumps({"random": r, "timestamp": ts}, separators=(',',':'), sort_keys=True).encode()),
    ("json_def", json.dumps({"random": r, "timestamp": ts}, sort_keys=True).encode()),
]
# binary uint32
r_be = r.to_bytes(4,"big"); r_le = r.to_bytes(4,"little")
cands += [("r_be", r_be), ("r_le", r_le), ("r_be\\n", r_be+b"\n"), ("r_le\\n", r_le+b"\n")]
# unix combos
if unix is not None:
    u4be = unix.to_bytes(4,"big"); u4le = unix.to_bytes(4,"little")
    cands += [
        ("unix", str(unix).encode()),
        ("r|unix", f"{r}|{unix}".encode()),
        ("r_be+u4be", r_be+u4be),
        ("u4be+r_be", u4be+r_be),
    ]

# small prefixes
prefixes = [b"", b"R4|", b"random:", b"MSG:"]
exp = []
for lab,m in cands:
    for p in prefixes:
        exp.append((f"{lab}+pref({p.decode(errors='ignore')})", p+m))
cands = exp

def vfy(m, sig, prehashed=False):
    try:
        if prehashed:
            pubkey.verify(sig, sha256(m).digest(), ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        else:
            pubkey.verify(sig, m, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False

ok=False
for lab,m in cands:
    h=sha256(m).hexdigest()
    if vfy(m, sig_der) or vfy(m, sig_raw) or vfy(m, sig_der, True) or vfy(m, sig_raw, True):
        print(f"[OK] {lab} sha256={h}")
        ok=True
        break
if not ok:
    # try Ethereum prefix once for each
    def eth(m): 
        p=b"\x19Ethereum Signed Message:\n"+str(len(m)).encode()
        return p+m
    for lab,m in cands:
        em=eth(m); h=sha256(em).hexdigest()
        if vfy(em, sig_der) or vfy(em, sig_raw):
            print(f"[OK] eth {lab} sha256={h}")
            ok=True
            break
# === EXTRA: друк точного повідомлення й хеша ===
if ok:
    # відтворюємо canonical JSON (def separators, sort_keys=True)
    msg = json.dumps(
        {"random": r, "timestamp": ts},
        sort_keys=True  # дає порядок "random", "timestamp"
    ).encode()         # дефолтні separators: ", " і ": "
    print("\n--- EXACT MESSAGE ---")
    print(msg.decode())
    print("sha256:", sha256(msg).hexdigest())

print("✅ MATCHED" if ok else "❌ NO MATCH")
