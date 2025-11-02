#!/usr/bin/env python3
import base64, json, struct, requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

HOST = "http://localhost:8084"
API_KEY = "demo"

def load_pubkey_from_double_b64(b64txt: str):
    pem = base64.b64decode(b64txt)
    return serialization.load_pem_public_key(pem)

def try_verify(pub, message, sig_raw):
    # 1) DER
    try:
        pub.verify(sig_raw, message, ec.ECDSA(hashes.SHA256()))
        return True, "DER", "msg-len=%d" % len(message)
    except InvalidSignature:
        pass
    # 2) raw r||s (64)
    if len(sig_raw) == 64:
        r = int.from_bytes(sig_raw[:32], "big")
        s = int.from_bytes(sig_raw[32:], "big")
        der = utils.encode_dss_signature(r, s)
        try:
            pub.verify(der, message, ec.ECDSA(hashes.SHA256()))
            return True, "raw(r||s)", "msg-len=%d" % len(message)
        except InvalidSignature:
            pass
    # 3) raw r||s||v (65) -> відкинути v
    if len(sig_raw) == 65:
        r = int.from_bytes(sig_raw[:32], "big")
        s = int.from_bytes(sig_raw[32:64], "big")
        der = utils.encode_dss_signature(r, s)
        try:
            pub.verify(der, message, ec.ECDSA(hashes.SHA256()))
            return True, "raw(r||s||v→drop v)", "msg-len=%d" % len(message)
        except InvalidSignature:
            pass
    return False, None, None

def main():
    url = f"{HOST}/random_pq?sig=ecdsa&n=32"
    r = requests.get(url, headers={"X-API-Key": API_KEY}, timeout=10)
    data = r.json()
    print("== /random_pq?sig=ecdsa ==")
    print(json.dumps(data, indent=2))
    r.raise_for_status()

    rnd = data["random"]
    ts  = data.get("timestamp","")
    sig_raw = base64.b64decode(data["sig_b64"])
    pub = load_pubkey_from_double_b64(data["pubkey_b64"])

    print(f"\n[info] sig_len={len(sig_raw)} bytes")

    # Кандидати повідомлень (список (name, bytes))
    candidates = []
    # 1) ASCII числа
    candidates.append(("ascii(str(random))", str(rnd).encode()))
    # 2) big-endian 4 байти
    candidates.append(("int32_be", struct.pack(">I", rnd & 0xffffffff)))
    # 3) big-endian 8 байт
    candidates.append(("int64_be", struct.pack(">Q", rnd & 0xffffffffffffffff)))
    # 4) hex без 0x
    candidates.append(("ascii(hex(random)[2:])", format(rnd, "x").encode()))
    # 5) "random|timestamp" у різних варіантах
    candidates.append(("ascii(str(random)+timestamp)", (str(rnd)+ts).encode()))
    candidates.append(("ascii(str(random)+'|'+timestamp)", (str(rnd)+"|"+ts).encode()))
    # 6) JSON стабільний
    payload = {"random": rnd, "timestamp": ts}
    candidates.append(("json_compact", json.dumps(payload, separators=(",",":"), sort_keys=True).encode()))
    # 7) тільки timestamp
    candidates.append(("ascii(timestamp)", ts.encode()))

    for name, msg in candidates:
        ok, mode, extra = try_verify(pub, msg, sig_raw)
        if ok:
            print(f"✅ VERIFIED [{name}] using {mode} ({extra})")
            return
        else:
            print(f"… no [{name}]")

    print("❌ No candidate message/format matched. Need server signing spec.")

if __name__ == "__main__":
    main()
