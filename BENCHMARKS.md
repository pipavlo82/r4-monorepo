# ⚡ Re4ctoR Performance & Quality Benchmarks

This document captures throughput, latency and statistical quality of the shipped binary and API layer.

---

## Runtime Throughput

All numbers below are single-node, local network or localhost tests unless noted.

| Platform                | Mode                        | Throughput        | Latency      | Notes                                  |
|------------------------|----------------------------|-------------------|--------------|----------------------------------------|
| AMD Ryzen 7 5800X      | C CLI (`re4_dump`)         | ~280 MB/s         | ~3.8 ms req  | direct byte stream                     |
| Intel i7-13700K        | HTTP `/random?n=1MB`       | ~190 MB/s         | ~6 ms req    | FastAPI+uvicorn (2 workers)            |
| Raspberry Pi 5 (ARM64) | C CLI (`re4_dump`)         | ~45 MB/s          | ~18 ms req   | thermals begin throttling after ~30s   |

Interpretation:
- Output is fast enough to act as a local entropy service / beacon.
- API wrapper overhead is acceptable for validator / orchestration tasks.
- ARM64 performance is lower but usable for edge devices / oracles.

---

## Statistical Quality

### PractRand
Input: multi-gigabyte stream from the shipped `re4_dump` binary.  
Result: PASS (no catastrophic bias reported).

### Dieharder
Input: ~1GB stream.
Result: All tests PASS or WEAK.  
Note: "WEAK" is normal even for `/dev/urandom` and does not imply exploitability by itself.

### TestU01 BigCrush
Input: 10^9+ bits.
Result: PASS.  
All p-values observed were within acceptable uniform range.

Summaries live in:
- `packages/core/proof/practrand_summary.txt`
- `packages/core/proof/dieharder_summary.txt`
- `packages/core/proof/bigcrush_summary.txt`

Full raw logs (several GB) are stored offline and available for audit under NDA.

---

## Example Usage

### Shell (direct core binary)
```bash
./re4_dump | head -c 32 | hexdump -C
This should output different non-zero, non-repeating bytes each run.

HTTP API (keyed access)
curl -s -H "x-api-key: local-demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
Returns 32 bytes of entropy as lowercase hex.

Why This Matters
These numbers go into investor material and security reviews.

This is what exchanges, rollups, staking validators, and HSM vendors will look at.

This also defines the early SLO for the /random service when deployed under systemd with rate limits (10 req/sec/IP, 1MB max per request).

TL;DR:

High throughput.

Clean statistical profile.

Ready to act as an internal entropy appliance today, VRF oracle tomorrow.

