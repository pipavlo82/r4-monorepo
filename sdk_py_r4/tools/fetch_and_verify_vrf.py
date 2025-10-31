#!/usr/bin/env python3
# sdk_py_r4/tools/fetch_and_verify_vrf.py
import os, requests, json
from r4sdk import client as r4client_mod  # якщо r4sdk встановлений локально, це нормально
# якщо не вдається імпортувати client як модуль, використай R4Client з пакету
try:
    from r4sdk import vrf
except Exception:
    import vrf

API_KEY = os.environ.get("R4_API_KEY", "demo")
HOST = os.environ.get("R4_PQ_HOST", "http://localhost:8084")  # налаштовуваний
SIG = os.environ.get("R4_SIG", "ecdsa")
N = int(os.environ.get("R4_N", "32"))

def fetch():
    url = f"{HOST}/random_pq?sig={SIG}&n={N}"
    print("fetching:", url)
    r = requests.get(url, headers={"X-API-Key": API_KEY}, timeout=10)
    r.raise_for_status()
    return r.json()

def main():
    data = fetch()
    print("\n== response ==\n", json.dumps(data, indent=2))
    ok, reason = vrf.verify_ecdsa_from_response(data)
    print("\n== verification ==\n", ok, reason)

if __name__ == "__main__":
    main()
