# Benchmarks Summary – r4 v0.1.1-perf-fips
Results validated on commodity hardware (Docker on consumer CPU).

| Metric              | r4           | /dev/urandom   | drand HTTP      |
|--------------------|--------------|----------------|-----------------|
| Throughput (req/s) | 950 000      | 250 000        | ~6              |
| p99 Latency (ms)   | ~1.1         | ~5.5           | ~200 (network)  |
| Entropy bits/byte  | ~7.999       | ~7.998         | ~7.99           |

Notes:
- r4 served randomness over HTTP with API key gating.
- drand measured as remote HTTPS beacon → network-bound, not local.
- `/dev/urandom` is local but not remotely consumable / auditable.
