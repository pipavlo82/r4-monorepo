#!/usr/bin/env python3
import os, json, requests
from r4sdk.client import R4Client

API_KEY      = os.getenv("R4_API_KEY", "demo")
PQ_HOST      = os.getenv("R4PQ_HOST", "http://localhost:8081")   # нодка з ECDSA/Dilithium
CLASSIC_HOST = os.getenv("R4_HOST",   "http://localhost:8080")   # класичний /random

sess = requests.Session()
sess.headers.update({"X-API-Key": API_KEY})

def pretty(obj):
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        return str(obj)

def get_json_or_text(resp):
    try:
        return resp.json()
    except Exception:
        return resp.text

def main():
    print(f"== /version on {PQ_HOST} ==")
    try:
        r = sess.get(f"{PQ_HOST}/version", timeout=5)
        print("status:", r.status_code)
        print(pretty(get_json_or_text(r)))
    except Exception as e:
        print("⚠ /version failed:", e)

    print(f"\n== /random_pq?sig=dilithium on {PQ_HOST} ==")
    try:
        r = sess.get(f"{PQ_HOST}/random_pq", params={"sig": "dilithium", "n": 32}, timeout=10)
        print("status:", r.status_code)
        print(pretty(get_json_or_text(r)))
    except Exception as e:
        print("⚠ /random_pq dilithium failed:", e)

    print(f"\n== /random_pq?sig=ecdsa on {PQ_HOST} ==")
    try:
        r = sess.get(f"{PQ_HOST}/random_pq", params={"sig": "ecdsa", "n": 32}, timeout=10)
        print("status:", r.status_code)
        print(pretty(get_json_or_text(r)))
    except Exception as e:
        print("⚠ /random_pq ecdsa failed:", e)

    print(f"\n== classic /random via R4Client on {CLASSIC_HOST} ==")
    try:
        c = R4Client(api_key=API_KEY, host=CLASSIC_HOST)
        rnd = c.get_random(16)  # існуючий метод з client.py
        print("random (hex):", rnd.hex())
    except Exception as e:
        print("⚠ classic /random failed:", e)

if __name__ == "__main__":
    main()
