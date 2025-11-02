#!/usr/bin/env python3
# sdk_py_r4/tools/vrf_bruteforce_verify.py
# Робить багато варіантів перевірки ECDSA(sig) відповіді /random_pq?sig=ecdsa
import os, json, base64, hashlib, requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

# Налаштування через ENV (або змінити тут)
API_KEY = os.environ.get("R4_API_KEY", "demo")
HOST = os.environ.get("R4_PQ_HOST", "http://localhost:8084")
SIG = os.environ.get("R4_SIG", "ecdsa")
N = int(os.environ.get("R4_N", "32"))

def fetch():
    url = f"{HOST}/random_pq?sig={SIG}&n={N}"
    r = requests.get(url, headers={"X-API-Key": API_KEY}, timeout=10)
    r.raise_for_status()
    return r.json()

def load_pubkey_from_b64(pub_b64):
    """
    Сервер може повертати base64-PEM або base64-raw-SEC1.
    Спробуємо декодувати й розпізнати.
    """
    raw = base64.b64decode(pub_b64)
    # Якщо це вже PEM text
    try:
        pub = serialization.load_pem_public_key(raw)
        return pub, "pem(decoded b64)"
    except Exception:
        pass
    # Спробуємо завантажити як DER (SPKI)
    try:
        pub = serialization.load_der_public_key(raw)
        return pub, "der(decoded b64)"
    except Exception:
        pass
    # Спробуємо розпізнати SEC1 uncompressed (0x04 || X || Y)
    if raw and raw[0] == 0x04 and (len(raw) == 65 or len(raw) == 1 + 32 + 32):
        x = int.from_bytes(raw[1:33], "big")
        y = int.from_bytes(raw[33:65], "big")
        numbers = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256K1())
        pub = numbers.public_key()
        return pub, "sec1_uncompressed"
    # Якщо не вдалося
    raise ValueError("Cannot parse public key (unknown encoding)")

def msg_variants(random_val, timestamp):
    s = str(random_val)
    ts = str(timestamp)
    variants = []
    # 1) compact sorted JSON with timestamp (canonical we tried before)
    variants.append(("json_sorted_r_t", json.dumps({"random": int(random_val), "timestamp": ts}, separators=(",",":"), sort_keys=True).encode()))
    # 2) compact JSON without sort_keys (same order)
    variants.append(("json_nosort_r_t", json.dumps({"random": int(random_val), "timestamp": ts}, separators=(",",":")).encode()))
    # 3) JSON only random
    variants.append(("json_r_only", json.dumps({"random": int(random_val)}, separators=(",",":"), sort_keys=True).encode()))
    # 4) ascii number
    variants.append(("ascii_decimal", s.encode()))
    # 5) ascii hex without 0x
    variants.append(("ascii_hex_no0x", format(int(random_val), "x").encode()))
    # 6) ascii hex with 0x
    variants.append(("ascii_hex_0x", ("0x"+format(int(random_val),"x")).encode()))
    # 7) ascii random + timestamp concatenated
    variants.append(("ascii_r_plus_ts", (s+ts).encode()))
    variants.append(("ascii_r_pipe_ts", (s+"|"+ts).encode()))
    variants.append(("ascii_ts", ts.encode()))
    # 8) compact JSON with random as hex string
    variants.append(("json_r_hex_string", json.dumps({"random": hex(int(random_val)), "timestamp": ts}, separators=(",",":"), sort_keys=True).encode()))
    # 9) json compact with timestamp trimmed to seconds (if ms present)
    ts_short = ts.split(".")[0]
    variants.append(("json_sorted_r_t_shortts", json.dumps({"random": int(random_val), "timestamp": ts_short}, separators=(",",":"), sort_keys=True).encode()))
    # unique by content
    seen = set(); out=[]
    for name,b in variants:
        if b not in seen:
            out.append((name,b)); seen.add(b)
    return out

def try_verify(pubkey, msg, sig):
    """Спроби верифікації різними способами. Повертає (True,desc) або (False,reason)."""
    # 1) try as DER signature directly (common)
    try:
        pubkey.verify(sig, msg, ec.ECDSA(hashes.SHA256()))
        return True, "DER signature on msg (sha256)"
    except InvalidSignature:
        pass
    except Exception as e:
        # пропустити інші помилки, будемо пробувати інше
        pass
    # 2) try raw r||s (64 bytes) -> DER
    if len(sig) >= 64:
        rs = sig[:64]
        r = int.from_bytes(rs[:32], "big")
        s = int.from_bytes(rs[32:64], "big")
        der = utils.encode_dss_signature(r, s)
        try:
            pubkey.verify(der, msg, ec.ECDSA(hashes.SHA256()))
            return True, "raw r||s -> DER on msg (sha256)"
        except InvalidSignature:
            pass
        # try prehashed
        try:
            digest = hashlib.sha256(msg).digest()
            pubkey.verify(der, digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
            return True, "raw r||s -> DER on prehashed(SHA256(msg))"
        except InvalidSignature:
            pass
        # try swapped r/s (some libs produce s||r)
        r2 = int.from_bytes(rs[32:64], "big")
        s2 = int.from_bytes(rs[:32], "big")
        der2 = utils.encode_dss_signature(r2, s2)
        try:
            pubkey.verify(der2, msg, ec.ECDSA(hashes.SHA256()))
            return True, "raw s||r -> DER on msg (sha256)"
        except InvalidSignature:
            pass
    # 3) try signature as DER on prehashed(msg)
    try:
        digest = hashlib.sha256(msg).digest()
        pubkey.verify(sig, digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        return True, "DER on prehashed(SHA256(msg))"
    except InvalidSignature:
        pass
    except Exception:
        pass

    return False, "no-match"

def main():
    data = fetch()
    print("== response ==\n", json.dumps(data, indent=2))
    sig_b64 = data.get("sig_b64")
    pub_b64 = data.get("pubkey_b64")
    if not sig_b64 or not pub_b64:
        print("Missing sig_b64 or pubkey_b64 in response")
        return
    sig = base64.b64decode(sig_b64)
    pub_raw_b64 = pub_b64

    # load public key
    try:
        pubkey, pk_info = load_pubkey_from_b64(pub_raw_b64)
    except Exception as e:
        print("Cannot parse public key:", e)
        return
    print("Loaded public key format:", pk_info)

    # build msg candidates
    random_val = data.get("random")
    timestamp = data.get("timestamp","")
    candidates = msg_variants(random_val, timestamp)

    # try all candidates
    for name,msg in candidates:
        ok, reason = try_verify(pubkey, msg, sig)
        digest = hashlib.sha256(msg).hexdigest()
        print(f"[{name}] sha256(msg)={digest} -> {ok} ; {reason}")
        if ok:
            print("SUCCESS: matched candidate:", name)
            print("message bytes:", msg)
            return

    # summary: print signature lengths and sample bytes
    print("=== Summary / debug ===")
    print("sig len:", len(sig))
    print("sig hex (first 128):", sig.hex()[:128])
    print("pub_raw_b64 len:", len(pub_raw_b64))
    try:
        decoded_pub = base64.b64decode(pub_raw_b64)
        print("decoded pub first bytes:", decoded_pub[:80])
    except Exception:
        pass

if __name__ == '__main__':
    main()

