# 📊 r4 Benchmarks – November 2025

| Source | Avg Latency (ms) | p99 (ms) | Req/s | Notes |
|--------|------------------|-----------|-------|-------|
| r4 (local Docker) | 0.8 | 1.1 | 950 000 | FastAPI + i7-13700K |
| /dev/urandom | 3.2 | 5.5 | 250 000 | system RNG |
| drand HTTP | 150 | 200 | 6 | network latency |
