import json, sys
from eth_keys import keys
from eth_utils import to_checksum_address
j = json.load(open(sys.argv[1] if len(sys.argv)>1 else "/tmp/vrf.json"))
msg_hash = bytes.fromhex(j["msg_hash"][2:])
v = int(j["v"]); r = int(j["r"],16); s = int(j["s"],16)
if v>=27: v-=27
sig = keys.Signature(vrs=(v,r,s))
recovered = to_checksum_address(sig.recover_public_key_from_msg_hash(msg_hash).to_address())
print({"recovered": recovered, "expected": to_checksum_address(j["signer_addr"]), "ok": recovered==to_checksum_address(j["signer_addr"])})
