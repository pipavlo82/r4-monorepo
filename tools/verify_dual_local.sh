#!/usr/bin/env bash
set -Eeuo pipefail

API_KEY="${API_KEY:-demo}"
VRF_URL="${VRF_URL:-http://127.0.0.1:8083}"
OUT="/tmp/vrf_dual.json"

# 1) Отримати dual-proof
curl -sS -H "X-API-Key: $API_KEY" "$VRF_URL/random_dual" -o "$OUT"
[ -s "$OUT" ] || { echo "❌ $OUT порожній"; exit 1; }
echo "— head $OUT:"; head -c 220 "$OUT"; echo; echo

# 2) Перевірити ECDSA та ML-DSA (якщо присутній)
python3 - <<'PY'
import json, base64, sys
from eth_keys import keys
from eth_utils import to_checksum_address
import oqs

path = "/tmp/vrf_dual.json"
j = json.load(open(path,"r"))

# ------- ECDSA -------
ecdsa = j.get("ecdsa", j)
req = ("v","r","s","msg_hash","signer_addr")
if all(k in ecdsa for k in req):
    v = ecdsa["v"]; r = int(ecdsa["r"],16); s = int(ecdsa["s"],16)
    if v in (27,28): v -= 27
    mh = ecdsa["msg_hash"][2:] if str(ecdsa["msg_hash"]).startswith("0x") else ecdsa["msg_hash"]
    sig = keys.Signature(vrs=(v,r,s))
    rec = sig.recover_public_key_from_msg_hash(bytes.fromhex(mh)).to_checksum_address()
    exp = to_checksum_address(ecdsa["signer_addr"])
    print({"scheme":"ECDSA","expected":exp,"recovered":rec,"ok":rec==exp})
else:
    print({"scheme":"ECDSA","ok":False,"reason":"missing fields"})

# ------- PQ (ML-DSA / Dilithium) -------
# Підтримуємо різні назви полів:
pq = j.get("pq", j)
# можливі ключі:
cand_alg = pq.get("pq_alg") or pq.get("ml_dsa_alg") or pq.get("dilithium_alg") or pq.get("pq_scheme") or ""
cand_pk  = pq.get("pq_pubkey_b64") or pq.get("pq_pk_b64") or pq.get("pubkey_pq_b64") or pq.get("pq_pubkey")
cand_sig = pq.get("pq_sig_b64") or pq.get("signature_pq_b64") or pq.get("pq_signature_b64") or pq.get("pq_sig")

def norm_alg(a:str)->str:
    if not a: return ""
    a=a.strip().lower()
    map = {"dilithium2":"ML-DSA-44","dilithium3":"ML-DSA-65","dilithium5":"ML-DSA-87",
           "ml-dsa-44":"ML-DSA-44","ml-dsa-65":"ML-DSA-65","ml-dsa-87":"ML-DSA-87"}
    return map.get(a, a.upper())

alg = norm_alg(cand_alg) if cand_alg else "ML-DSA-65"  # дефолт — Dilithium3

if cand_pk and cand_sig:
    try:
        pk  = base64.b64decode(cand_pk)
        sig = base64.b64decode(cand_sig)
        with oqs.Signature(alg) as s:
            ok = s.verify(j.get("msg","").encode() if "msg" in j else  # якщо є явне поле msg
                          bytes.fromhex(j["msg_hash"][2:]) if "msg_hash" in j else  # або перевіряли по хешу
                          json.dumps({k:j[k] for k in ("random","timestamp") if k in j}, separators=(',',':')).encode(),  # запасний варіант
                          sig, pk)
        print({"scheme":alg,"ok":ok})
    except Exception as e:
        print({"scheme":alg,"ok":False,"error":str(e)})
else:
    print({"scheme":"PQ","ok":False,"reason":"missing pq_{sig/pk}_b64"})
PY
