#!/usr/bin/env python3
import json, sys, base64
from eth_utils import keccak, to_checksum_address
from eth_keys import keys

def eip191_hash32(digest32: bytes) -> bytes:
    assert len(digest32) == 32
    prefix = b"\x19Ethereum Signed Message:\n32"
    return keccak(prefix + digest32)

def msg_bytes(j: dict) -> bytes:
    # ВАЖЛИВО: порядок і точні назви ключів
    m = {
        "random": j["random"],
        "timestamp": j["timestamp"],
        "hash_alg": j.get("hash_alg", "SHA-256"),
    }
    return json.dumps(m, separators=(",",":")).encode()

def to_bytes32(hex_or_bytes):
    if isinstance(hex_or_bytes, (bytes, bytearray)):
        b = bytes(hex_or_bytes)
    else:
        h = hex_or_bytes[2:] if str(hex_or_bytes).startswith("0x") else str(hex_or_bytes)
        b = bytes.fromhex(h)
    if len(b) != 32:
        raise ValueError(f"expected 32 bytes, got {len(b)}")
    return b

def main(path):
    j = json.load(open(path, "r"))

    # 1) будуємо повідомлення в тому ж форматі
    m = msg_bytes(j)

    # 2) два варіанти хешів
    digest_raw = keccak(m)
    digest_eip191 = eip191_hash32(digest_raw)

    # 3) що поклав сервер у msg_hash
    jhash = bytes.fromhex(j["msg_hash"][2:] if j["msg_hash"].startswith("0x") else j["msg_hash"])

    # 4) вибираємо який збігається з msg_hash
    which = None
    if jhash == digest_eip191:
        which = "eip191"
        digest = digest_eip191
    elif jhash == digest_raw:
        which = "raw"
        digest = digest_raw
    else:
        # навіть якщо не збігся, все одно спробуємо EIP-191 для підпису
        which = "unknown"
        digest = digest_eip191

    # 5) відновлюємо адресу з v,r,s
    v = j["v"]
    if v in (27, 28):
        v_adj = v - 27
    else:
        v_adj = v
    r = int(j["r"], 16)
    s = int(j["s"], 16)
    sig = keys.Signature(vrs=(v_adj, r, s))

    recovered = sig.recover_public_key_from_msg_hash(digest).to_checksum_address()
    expected = to_checksum_address(j["signer_addr"])
    out = {
        "which_hash": which,
        "hash_ok": (jhash == digest),
        "ecdsa_ok": (recovered == expected),
        "expected": expected,
        "recovered": recovered,
        "msg_hash": "0x" + digest.hex(),
        "msg_hash_in_json": j["msg_hash"],
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: verify_vrf_msg_hash.py /path/to/vrf_dual.json", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
