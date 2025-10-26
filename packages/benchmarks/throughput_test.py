#!/usr/bin/env python3
# 💀 r4 throughput benchmark
import time, requests, concurrent.futures
URL="http://127.0.0.1:8080/random?n=32&fmt=hex"
API_KEY="demo"

def one_call():
    r=requests.get(URL,headers={"x-api-key":API_KEY},timeout=2)
    return r.status_code

def main(n=10000,workers=100):
    t0=time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(lambda _:one_call(),range(n)))
    dt=time.time()-t0
    print(f"🔥 {n/dt:.0f} req/s over {n} calls ({dt:.2f}s total)")

if __name__=="__main__":
    main()
