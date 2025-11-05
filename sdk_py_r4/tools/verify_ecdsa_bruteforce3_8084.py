#!/usr/bin/env python3
# verify_ecdsa_bruteforce3_8084.py
# Розширений brute-force для верифікації ECDSA(sig_b64) з сервера R4 (порт 8084)
import base64, json, struct, requests, hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

# optional keccak
try:
    import sha3
    has_keccak = True
except Exception:
    has_keccak = False

HOST = "http://localhost:8084"
API_KEY = "demo"
URL = f"{HOST}/random_pq?sig=ecdsa&n=32"
TIMEOUT = 10

def load_pubkey_from_b64pem(b64txt: str):
    pem = base64.b64decode(b64txt)
    return serialization.load_pem_public_key(pem)

def verify_der(pub, msg, sig):
    try:
        pub.verify(sig, msg, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False

def verify_raw_rs(pub, msg, sig):
    if len(sig) == 65:
        sig = sig[:64]
    if len(sig) != 64:
        return False
    r = int.from_bytes(sig[:32], "big")
    s = int.from_bytes(sig[32:], "big")
    der = utils.encode_dss_signature(r, s)
    return verify_der(pub, msg, der)

def verify_prehashed(pub, digest_bytes, sig):
    try:
        if len(sig) == 65:
            sig2 = sig[:64]
        else:
            sig2 = sig
        if len(sig2) == 64:
            r = int.from_bytes(sig2[:32], "big")
            s = int.from_bytes(sig2[32:], "big")
            der = utils.encode_dss_signature(r, s)
            pub.verify(der, digest_bytes, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
            return True
        pub.verify(sig, digest_bytes, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        return True
    except InvalidSignature:
        return False

def keccak256(b: bytes):
    if not has_keccak:
        raise RuntimeError("pysha3 not installed")
    k = sha3.keccak_256()
    k.update(b)
    return k.digest()

def eth_prefixed(msg_bytes):
    prefix = b"\x19Ethereum Signed Message:\n" + str(len(msg_bytes)).encode()
    return prefix + msg_bytes

def pad32_be_int(n):
    return n.to_bytes(32, "big")

def pad32_le_int(n):
    return n.to_bytes(32, "little")

def candidates(random_int, ts):
    c = []
    r = random_int
    s_ts = ts or ""
    # basic ascii/hex/int forms
    c.append(("ascii_random", str(r).encode()))
    c.append(("hex_random", format(r, "x").encode()))
    c.append(("hex0x_random", ("0x"+format(r,"x")).encode()))
    c.append(("int32_be", struct.pack(">I", r & 0xffffffff)))
    c.append(("int64_be", struct.pack(">Q", r & 0xffffffffffffffff)))
    c.append(("int32_le", struct.pack("<I", r & 0xffffffff)))
    c.append(("int64_le", struct.pack("<Q", r & 0xffffffffffffffff)))
    c.append(("padded32_be", pad32_be_int(r)))
    c.append(("padded32_le", pad32_le_int(r)))

    # combos with timestamp
    c.append(("ascii_random|ts", (str(r)+"|"+s_ts).encode()))
    c.append(("ascii_random+ts", (str(r)+s_ts).encode()))
    c.append(("timestamp", s_ts.encode()))
    # json compact / pretty
    c.append(("json_compact_r_t", json.dumps({"random": r, "timestamp": s_ts}, separators=(",",":"), sort_keys=True).encode()))
    c.append(("json_r_t", json.dumps({"random": r, "timestamp": s_ts}, sort_keys=True).encode()))
    c.append(("json_random_only", json.dumps({"random": r}, separators=(",",":"), sort_keys=True).encode()))
    c.append(("ascii_hex_random", bytes(format(r,"x").encode())))

    # ethereum prefixed variants (for both message and hex)
    base_list = list(c)
    for name, m in base_list:
        c.append((f"eth_prefixed::{name}", eth_prefixed(m)))
        # keccak of prefixed if keccak available
        if has_keccak:
            c.append((f"keccak_prefixed::{name}", keccak256(eth_prefixed(m))))
    # add direct sha256 digest and double-sha256
    more = []
    for name, m in list(c):
        h = hashlib.sha256(m).digest()
        more.append((f"sha256_digest::{name}", h))
        more.append((f"sha256_hexascii::{name}", hashlib.sha256(m).hexdigest().encode()))
        # double sha256
        more.append((f"double_sha256::{name}", hashlib.sha256(h).digest()))
    c.extend(more)

    # keccak raw options (if available)
    if has_keccak:
        extra = []
        for name, m in list(c):
            extra.append((f"keccak::{name}", keccak256(m)))
        c.extend(extra)

    # common prefixes/labels
    c.append(("label_random_colon", f"random:{r}".encode()))
    c.append(("label_Random_colon", f"Random:{r}".encode()))
    c.append(("label_rand_json", json.dumps({"r": r}).encode()))
    return c

def run():
    r = requests.get(URL, headers={"X-API-Key": API_KEY}, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    print("== response ==")
    print(json.dumps(data, indent=2))
    sig_raw = base64.b64decode(data["sig_b64"])
    pub = load_pubkey_from_b64pem(data["pubkey_b64"])
    rnd = data["random"]
    ts = data.get("timestamp", "")
    print(f"\n[info] sig_len={len(sig_raw)} bytes")

    cand_list = candidates(rnd, ts)
    tried = 0
    for name, msg in cand_list:
        tried += 1
        # 1) try raw r||s
        try:
            if verify_raw_rs(pub, msg, sig_raw):
                print(f"✅ VERIFIED raw-r||s on message: {name}")
                return
        except Exception:
            pass
        # 2) try DER
        try:
            if verify_der(pub, msg, sig_raw):
                print(f"✅ VERIFIED DER style on message: {name}")
                return
        except Exception:
            pass
        # 3) try prehashed (sha256(msg))
        try:
            digest = hashlib.sha256(msg).digest()
            if verify_prehashed(pub, digest, sig_raw):
                print(f"✅ VERIFIED prehashed(SHA256(msg)) for: {name}")
                return
        except Exception:
            pass

    print(f"❌ No candidate matched after trying {tried} formats.")
    print("Suggestions: inspect server code for exact sign(data) call, or provide server signing spec.")

if __name__ == "__main__":
    run()
