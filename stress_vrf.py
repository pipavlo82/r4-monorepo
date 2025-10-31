#!/usr/bin/env python3
import argparse
import concurrent.futures
import json
import os
import statistics
import sys
import time
from typing import Tuple, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_HOST = os.getenv("PQ_HOST", "http://127.0.0.1:8081")
DEFAULT_KEY = os.getenv("PQ_KEY", "demo")

def parse_args():
    ap = argparse.ArgumentParser(description="R4 VRF stress")
    ap.add_argument("--host", default=DEFAULT_HOST, help="VRF host (default env PQ_HOST or http://127.0.0.1:8081)")
    ap.add_argument("--key", default=DEFAULT_KEY, help="API key (default env PQ_KEY or demo)")
    ap.add_argument("-n", "--reqs", type=int, default=60, help="total requests (default: 60)")
    ap.add_argument("-w", "--workers", type=int, default=10, help="concurrency (default: 10)")
    ap.add_argument("-t", "--timeout", type=float, default=5.0, help="per-request timeout seconds (default: 5)")
    return ap.parse_args()

def make_session(timeout: float) -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=0,  # не ретраїмо, бо це stress (можна увімкнути за потреби)
        backoff_factor=0,
        status_forcelist=[],
        allowed_methods=False,
    )
    adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retries)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.request_timeout = timeout  # просто позначка
    return s

def hit_once(session: requests.Session, host: str, key: str, timeout: float) -> Tuple[Union[int,str], float, str]:
    url = f"{host}/random_pq"
    params = {"sig": "ecdsa"}
    headers = {"X-API-Key": key}
    t0 = time.perf_counter()
    try:
        r = session.get(url, params=params, headers=headers, timeout=timeout)
        dt = time.perf_counter() - t0
        return (r.status_code, dt, r.text)
    except Exception as e:
        dt = time.perf_counter() - t0
        return ("ERR", dt, str(e))

def maybe_verify_ecdsa(sample_json: dict) -> Union[bool, None]:
    """
    Спроба локально перевірити ECDSA підпис (EIP-191) якщо є поля.
    Повертає True/False або None, якщо перевірку неможливо виконати.
    """
    try:
        from eth_keys import keys
        from eth_utils import keccak, to_bytes, to_checksum_address

        v = sample_json.get("v")
        r_hex = sample_json.get("r")
        s_hex = sample_json.get("s")
        signer = sample_json.get("signer_addr")
        msg_hash_hex = sample_json.get("msg_hash") or sample_json.get("msg_hash_in_json")
        rnd = sample_json.get("random")

        if None in (v, r_hex, s_hex, signer) or rnd is None:
            return None

        # canonical message: "\x19Ethereum Signed Message:\n32" + keccak(randomness)
        # randomness може бути int; упаковуємо як 32-байтовий big-endian
        rnd_int = int(rnd)
        rnd_bytes = rnd_int.to_bytes(32, "big")
        msg_hash = keccak(rnd_bytes)
        prefix = b"\x19Ethereum Signed Message:\n32"
        eth_hash = keccak(prefix + msg_hash)

        sig = keys.Signature(vrs=(int(v), int(r_hex,16), int(s_hex,16)))
        recovered = sig.recover_public_key_from_msg_hash(eth_hash).to_canonical_address()
        recovered_addr = to_checksum_address("0x" + recovered.hex())
        return recovered_addr.lower() == signer.lower()
    except Exception:
        return None

def main():
    args = parse_args()
    print("=== PQ / VRF STRESS ===")
    print(f"Target    : {args.host}/random_pq?sig=ecdsa")
    print(f"Threads   : {args.workers}")
    print(f"Requests  : {args.reqs}")
    print()

    s = make_session(args.timeout)

    t0 = time.perf_counter()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(hit_once, s, args.host, args.key, args.timeout) for _ in range(args.reqs)]
        for f in concurrent.futures.as_completed(futs):
            results.append(f.result())
    dur = time.perf_counter() - t0

    codes = [c for (c, _, _) in results]
    times = [t for (_, t, _) in results if isinstance(t, float)]
    ok = sum(1 for c in codes if c == 200)
    limited = sum(1 for c in codes if c == 429)
    other = [(c, b) for (c, _, b) in results if c not in (200, 429)]

    rps = int(len(results)/max(dur, 1e-6))
    print(f"Time: {dur:.2f}s  RPS: {rps}  (total: {len(results)})")
    if times:
        print(f"Latency (s): avg={statistics.fmean(times):.4f}  p50={statistics.quantiles(times, n=2)[0]:.4f}  p95={statistics.quantiles(times, n=20)[18]:.4f}  p99={statistics.quantiles(times, n=100)[98]:.4f}")
    print(f"200 OK          : {ok}")
    print(f"429 rate limited: {limited}")
    print(f"Other errors    : {len(other)}")
    if other:
        code, body = other[0]
        print(f"Sample other err: {code} -> {str(body)[:200]}")

    # Save one signed example for audit
    sample_ok_body = next((b for (c, _, b) in results if c == 200), None)
    if sample_ok_body:
        try:
            parsed = json.loads(sample_ok_body)
        except Exception:
            parsed = None

        out_path = "/tmp/vrf_sample.json"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(sample_ok_body)
        print(f"\nSaved sample to {out_path}")

        # Optional local verification (if eth_keys present & fields exist)
        if isinstance(parsed, dict):
            vres = maybe_verify_ecdsa(parsed)
            if vres is True:
                print("Local ECDSA verify: ✅ PASS")
            elif vres is False:
                print("Local ECDSA verify: ❌ FAIL (signature mismatch)")
            else:
                print("Local ECDSA verify: (skipped) fields/lib not available")

        # Pretty print first 800 chars
        try:
            print("\nExample signed response:")
            print(json.dumps(parsed if isinstance(parsed, dict) else sample_ok_body, indent=2)[:800])
        except Exception:
            print(str(sample_ok_body)[:800])

if __name__ == "__main__":
    sys.exit(main() or 0)
