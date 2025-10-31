#!/usr/bin/env python3
import json, sys
from eth_keys import keys
from eth_utils import to_checksum_address

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/vrf.json"

with open(path, "r") as f:
    j = json.load(f)

for k in ["v","r","s","msg_hash","signer_addr"]:
    if k not in j:
        print({"error": f"missing field: {k}"})
        sys.exit(2)

v = j["v"]
if v in (27, 28):  # normalize for eth_keys
    v -= 27
r = int(j["r"], 16)
s = int(j["s"], 16)

h = j["msg_hash"]
if h.startswith("0x"): h = h[2:]
msg_hash = bytes.fromhex(h)

expected = to_checksum_address(j["signer_addr"])
sig = keys.Signature(vrs=(v, r, s))
recovered = sig.recover_public_key_from_msg_hash(msg_hash).to_checksum_address()

print({"expected": expected, "recovered": recovered, "ok": recovered == expected})
