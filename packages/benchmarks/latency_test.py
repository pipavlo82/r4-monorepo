#!/usr/bin/env python3
# ⚙️ r4 latency probe
import requests,statistics,time
URL="http://127.0.0.1:8080/random?n=32&fmt=hex"
API_KEY="demo"

times=[]
for _ in range(1000):
    t0=time.perf_counter()
    requests.get(URL,headers={"x-api-key":API_KEY})
    times.append((time.perf_counter()-t0)*1000)

print(f"p50={statistics.median(times):.3f}ms, p95={statistics.quantiles(times,[.95])[0]:.3f}ms, p99={statistics.quantiles(times,[.99])[0]:.3f}ms")
