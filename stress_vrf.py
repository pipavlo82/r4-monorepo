#!/usr/bin/env python3
import concurrent.futures
import time
import requests
import json

PQ_HOST = "http://localhost:8081"
API_KEY = "demo"

REQS = 60       # total requests we'll send
WORKERS = 10    # how many threads in parallel

def hit_once(i):
    try:
        r = requests.get(
            f"{PQ_HOST}/random_pq",
            params={"sig": "ecdsa"},
            headers={"X-API-Key": API_KEY},
            timeout=5,
        )
        return (r.status_code, r.text)
    except Exception as e:
        return ("ERR", str(e))

def main():
    print("=== PQ / VRF STRESS ===")
    print(f"Target: {PQ_HOST}/random_pq?sig=ecdsa")
    print(f"Threads: {WORKERS}")
    print(f"Total requests: {REQS}")
    print()

    t0 = time.time()

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(hit_once, i) for i in range(REQS)]
        for f in concurrent.futures.as_completed(futs):
            results.append(f.result())

    t1 = time.time()
    dur = t1 - t0

    ok = sum(1 for code, _ in results if code == 200)
    limited = sum(1 for code, _ in results if code == 429)
    other_errs = [(code, body) for code, body in results if code not in (200, 429)]

    print(f"Time: {dur:.2f}s for {REQS} requests")
    print(f"200 OK:          {ok}")
    print(f"429 rate limited:{limited}")
    print(f"Other errors:    {len(other_errs)}")
    if other_errs:
        code, body = other_errs[0]
        print(f"Sample other err: {code} -> {body[:200]}")

    # Show one signed sample for investor / audit evidence
    sample_ok = next((body for code, body in results if code == 200), None)
    if sample_ok:
        print("\nExample signed response:")
        try:
            parsed = json.loads(sample_ok)
            print(json.dumps(parsed, indent=2)[:800])
        except Exception:
            print(sample_ok[:800])

if __name__ == "__main__":
    main()
