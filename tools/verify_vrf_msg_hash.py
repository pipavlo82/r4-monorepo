#!/usr/bin/env python3
"""
verify_vrf_msg_hash.py — перевіряє, що:
  1) msg_hash у JSON відповідає keccak256 від payload
  2) ECDSA(v,r,s) відновлює signer_addr
JSON очікується у форматі відповіді API (/random_pq або /random_dual).
"""

import sys, json, base64
from eth_keys import keys
from eth_utils import to_checksum_address
from web3 import Web3

def _payload_bytes(j: dict) -> bytes:
    # Узгоджений payload, як на бекенді:
    m = {"random": j["random"], "timestamp": j["timestamp"], "hash_alg": j["hash_alg"]}
    return json.dumps(m, separators=(",",":")).encode()

def main(path: str|None):
    data = sys.stdin.read() if path in (None, "-", "") else open(path,"r").read()
    j = json.loads(data)

    # 1) Перерахувати keccak(payload) і звірити з msg_hash
    msg = _payload_bytes(j)
    digest = Web3.keccak(msg)  # bytes32
    msg_hash_hex = j.get("msg_hash") or j.get("message_hash") or ""
    if msg_hash_hex.startswith("0x"):
        msg_hash_hex = msg_hash_hex[2:]
    msg_hash_bytes = bytes.fromhex(msg_hash_hex) if msg_hash_hex else b""
    hash_ok = (msg_hash_bytes == digest)

    # 2) Перевірити ECDSA підпис
    v = j["v"]
    r = int(j["r"], 16) if isinstance(j["r"], str) else j["r"]
    s = int(j["s"], 16) if isinstance(j["s"], str) else j["s"]
    v_adj = v - 27 if v in (27, 28) else v
    signer = keys.Signature(vrs=(v_adj, r, s)).recover_public_key_from_msg_hash(digest)
    recovered = signer.to_checksum_address()
    expected  = to_checksum_address(j["signer_addr"])
    ecdsa_ok = (recovered == expected)

    out = {
        "hash_ok": hash_ok,
        "ecdsa_ok": ecdsa_ok,
        "expected": expected,
        "recovered": recovered,
        "msg_hash": "0x"+digest.hex(),
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
