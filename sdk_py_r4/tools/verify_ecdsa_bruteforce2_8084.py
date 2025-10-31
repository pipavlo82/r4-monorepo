#!/usr/bin/env python3
# verify_ecdsa_bruteforce2_8084.py
import base64, json, struct, requests, hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

HOST = "http://localhost:8084"
API_KEY = "demo"
URL = f"{HOST}/random_pq?sig=ecdsa&n=32"

def load_pubkey_from_double_b64(b64txt: str):
    pem = base64.b64decode(b64txt)
    return serialization.load_pem_public_key(pem)

def verify_der(pub, msg, sig):
    try:
        pub.verify(sig, msg, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False

def verify_raw_rs(pub, msg, sig):
    # sig is raw r||s (64) or r||s||v (65 -> drop v)
    if len(sig) == 65:
        sig = sig[:64]
    if len(sig) != 64:
        return False
    r = int.from_bytes(sig[:32], "big")
    s = int.from_bytes(sig[32:], "big")
    der = utils.encode_dss_signature(r, s)
    return verify_der(pub, msg, der)

def verify_prehashed(pub, digest_bytes, sig):
    # digest_bytes is raw SHA256 digest (32 bytes)
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
        # also try if given DER already:
        pub.verify(sig, digest_bytes, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        return True
    except InvalidSignature:
        return False

def eth_prefixed(msg_bytes):
    # Ethereum Signed Message prefix variant
    prefix = b"\x19Ethereum Signed Message:\n" + str(len(msg_bytes)).encode()
    return prefix + msg_bytes

def run():
    r = requests.get(URL, headers={"X-API-Key": API_KEY}, timeout=10)
    r.raise_for_status()
    data = r.json()
    print("== response ==")
    print(json.dumps(data, indent=2))
    sig_raw = base64.b64decode(data["sig_b64"])
    pub = load_pubkey_from_double_b64(data["pubkey_b64"])
    rnd = data["random"]
    ts = data.get("timestamp", "")

    print(f"\n[info] sig_len={len(sig_raw)} bytes")

    # candidate messages (name, bytes)
    cands = []

    # raw variations:
    cands.append(("ascii(random)", str(rnd).encode()))
    cands.append(("hex(random)", format(rnd, "x").encode()))
    cands.append(("int32_be", struct.pack(">I", rnd & 0xffffffff)))
    cands.append(("int64_be", struct.pack(">Q", rnd & 0xffffffffffffffff)))
    cands.append(("ascii(random)+timestamp", (str(rnd)+ts).encode()))
    cands.append(("ascii(random)+'|'+timestamp", (str(rnd)+"|"+ts).encode()))
    cands.append(("timestamp", ts.encode()))
    cands.append(("json_compact", json.dumps({"random": rnd, "timestamp": ts}, separators=(",",":"), sort_keys=True).encode()))

    # ethereum-prefixed forms (message and hex message)
    for name, m in list(cands):
        cands.append((f"eth_prefixed::{name}", eth_prefixed(m)))

    # hashed forms: sha256(message) as raw digest AND ascii hex of digest
    more = []
    for name, m in list(cands):
        h = hashlib.sha256(m).digest()
        more.append((f"sha256_digest::{name}", h))
        more.append((f"sha256_hexascii::{name}", hashlib.sha256(m).hexdigest().encode()))
    cands.extend(more)

    # also try sha256 of ascii(random) specifically and of hex(random)
    cands.append(("sha256_ascii_random_digest", hashlib.sha256(str(rnd).encode()).digest()))
    cands.append(("sha256_hexrandom_digest", hashlib.sha256(format(rnd,"x").encode()).digest()))

    # try verifying
    for name, msg in cands:
        # 1) try raw r||s verification (server maybe signed raw msg but used ECDSA over msg)
        try:
            ok = verify_raw_rs(pub, msg, sig_raw)
            if ok:
                print(f"✅ VERIFIED raw-r||s on message: {name}")
                return
        except Exception as e:
            pass

        # 2) try DER verify (server might have provided DER already)
        try:
            ok = verify_der(pub, msg, sig_raw)
            if ok:
                print(f"✅ VERIFIED DER on message: {name}")
                return
        except Exception:
            pass

        # 3) try prehashed (server signs SHA256(msg) directly)
        try:
            digest = hashlib.sha256(msg).digest()
            ok = verify_prehashed(pub, digest, sig_raw)
            if ok:
                print(f"✅ VERIFIED prehashed(SHA256(msg)) for: {name}")
                return
        except Exception:
            pass

    print("❌ No candidate matched. Next: try other prehash (e.g., double-hash), different encodings, or ask for server signing spec.")

if __name__ == "__main__":
    run()
