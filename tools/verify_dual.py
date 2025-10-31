#!/usr/bin/env python3
import argparse, base64, json, sys
from eth_keys import keys
from eth_utils import to_checksum_address

try:
    import oqs
    HAS_OQS = True
except Exception:
    HAS_OQS = False


def _load_json(path: str) -> dict:
    data = sys.stdin.read() if path == "-" else open(path, "r", encoding="utf-8").read()
    return json.loads(data)


def verify_ecdsa(j: dict):
    try:
        v = j["v"]
        r = int(j["r"], 16)
        s = int(j["s"], 16)
        mh = j["msg_hash"]
        if mh.startswith("0x"):
            mh = mh[2:]
        msg_hash = bytes.fromhex(mh)
        v_adj = v - 27 if v in (27, 28) else v
        addr = keys.Signature(vrs=(v_adj, r, s)).recover_public_key_from_msg_hash(msg_hash).to_checksum_address()
        exp = to_checksum_address(j["signer_addr"])
        return {"ok": addr == exp, "expected": exp, "recovered": addr}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def verify_pq(j: dict):
    if not HAS_OQS:
        return {"ok": None, "error": "liboqs-python not installed"}
    try:
        sig = base64.b64decode(j["sig_pq_b64"])
        pk = base64.b64decode(j["pq_pubkey_b64"])
        msg = json.dumps({
            "random": j["random"],
            "timestamp": j["timestamp"],
            "hash_alg": j.get("hash_alg", "SHA-256")
        }, separators=(",", ":")).encode()
        with oqs.Signature(j.get("pq_scheme", "ML-DSA-65")) as s:
            ok = s.verify(msg, sig, pk)
        return {"ok": bool(ok), "scheme": j.get("pq_scheme", "ML-DSA-65")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main():
    ap = argparse.ArgumentParser(description="Verify dual-proof JSON (ECDSA + PQ)")
    ap.add_argument("path", help="Path to vrf_dual.json")
    args = ap.parse_args()
    j = _load_json(args.path)
    e = verify_ecdsa(j)
    q = verify_pq(j)
    print(json.dumps({"ECDSA": e, "PQ": q}, indent=2))
    if not e["ok"] or (q["ok"] is False):
        sys.exit(1)


if __name__ == "__main__":
    main()
