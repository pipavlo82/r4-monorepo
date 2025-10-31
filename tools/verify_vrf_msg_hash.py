#!/usr/bin/env python3
import json, sys
from eth_keys import keys
from eth_utils import to_checksum_address

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/vrf.json"
with open(path, "r", encoding="utf-8") as f:
    j = json.load(f)

v = int(j["v"]); r = int(j["r"], 16); s = int(j["s"], 16)
mh = j["msg_hash"]; msg_hash = bytes.fromhex(mh[2:] if mh.startswith("0x") else mh)

# eth_keys очікує 0/1, а вузол віддає 27/28 (канонічно для EVM)
v = v - 27 if v >= 27 else v

sig = keys.Signature(vrs=(v, r, s))
recovered = sig.recover_public_key_from_msg_hash(msg_hash).to_checksum_address()
expected = to_checksum_address(j["signer_addr"])
print({"expected": expected, "recovered": recovered, "ok": recovered == expected})
