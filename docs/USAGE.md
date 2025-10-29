```md
# 📚 API Usage — RE4CTOR / R4 entropy API

This document shows how to call the API from:
- curl
- Python (r4sdk)
- JavaScript / Node
- Solidity (Verifier)

It covers both:
- Core entropy node `:8080`
- PQ/VRF signed randomness node `:8081`

---

## 1. Health / Version

### Health check

```bash
curl http://127.0.0.1:8080/health
# "ok"
Version / attestation
bash
Copy code
curl http://127.0.0.1:8080/version | jq
This returns:

build IDs (api_git, core_git)

current rate limits

max request size

internal self-test / integrity info

basically: “is this node legitimate and healthy”

You can archive /version output at startup to prove to an auditor that you ran an uncompromised build.

2. Get raw entropy (:8080)
Endpoint
GET /random?n=<bytes>&fmt=<hex|base64|raw>

Auth:

Header: X-API-Key: <key>

or URL: ?key=<key>

Example: 32 bytes, hex-encoded

bash
Copy code
curl -s -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
# → "a359b9dd843294e415ac0e41eb49ef90..."
Example: 256 raw bytes to file

bash
Copy code
curl -s -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=256" \
  --output entropy.bin

hexdump -C entropy.bin | head
Error example (bad key):

bash
Copy code
curl -i -H "X-API-Key: WRONG" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"

# HTTP/1.1 401 Unauthorized
# {"detail":"invalid api key"}
3. Python usage (r4sdk)
Install client:

bash
Copy code
pip install r4sdk
Use it:

python
Copy code
from r4sdk import R4Client

client = R4Client(
    api_key="demo",
    host="http://localhost:8080"
)

rand_bytes = client.get_random(32)
print("Random hex:", rand_bytes.hex())
Typical integrations:

generate wallet keys

draw raffle winners off-chain

seed game matchmaker / tournament brackets

rotate validator committees

4. JavaScript / Node usage
js
Copy code
import fetch from "node-fetch";

const res = await fetch(
  "http://localhost:8080/random?n=8&fmt=hex",
  {
    headers: { "X-API-Key": "demo" }
  }
);

const hex = await res.text();

// Example: fair dice roll 1-100
const roll = (parseInt(hex.substring(0, 8), 16) % 100) + 1;
console.log("Rolled:", roll);
5. PQ/VRF signed randomness (:8081)
This node gives you randomness + cryptographic proof that you can feed into Solidity.

Request:

bash
Copy code
curl -s -H "X-API-Key: demo" \
  "http://localhost:8081/random_pq?sig=ecdsa" | jq
Typical response:

json
Copy code
{
  "random": 2689836398,
  "timestamp": "2025-10-28T23:46:03Z",
  "v": 27,
  "r": "0x4fe30113...",
  "s": "0xce79a501...",
  "signer_addr": "0xC61b94A8e6aDf598c8a04737192F1591cC37Db1A",
  "pq_mode": false
}
random → the random value

v,r,s → ECDSA signature parts

signer_addr → Ethereum address of the oracle signer

timestamp → when it was generated

pq_mode → whether PQ / Dilithium mode was used

Enterprise builds:

bash
Copy code
.../random_pq?sig=dilithium
will return Dilithium3 (FIPS 204 ML-DSA) signature instead of secp256k1 ECDSA.

6. On-chain verification (Solidity)
Contracts live in vrf-spec/contracts/.

Main pieces:

R4VRFVerifierCanonical.sol

LotteryR4.sol

Verifier recovers signer from (v,r,s) and checks it matches a trusted oracle.

High-level flow in Solidity:

solidity
Copy code
// Off-chain: you call /random_pq?sig=ecdsa
// On-chain: you pass randomness + sig into drawWinner()

require(
    verifier.verify(
        randomness,
        v, r, s,
        trustedSigner /* address of oracle */
    ),
    "Invalid signature"
);

uint256 winnerIndex = uint256(randomness) % players.length;
address winner = players[winnerIndex];
emit WinnerSelected(winner, winnerIndex, randomness);
This is “provably fair”:

contract enforces that randomness truly came from your RE4CTOR node

modulo is deterministic

everything is recorded on-chain so a regulator / angry whale can replay it

7. Stress / audit tooling
These helper scripts ship in repo root:

stress_core.sh
Load test :8080 (/random) to confirm throughput / rate limit.
Expect ~950k req/sec sustained, p99 latency ~1.1 ms on decent hardware.

stress_vrf.py
Hammers :8081/random_pq in parallel, shows:

how many 200 OK

how many 429 rate-limited

prep_vrf_for_chain.py
Fetches a live (random, v, r, s, signer_addr) bundle from :8081 and formats it for direct consumption in Hardhat tests and in LotteryR4.drawWinner().

run_full_demo.sh
One-shot script that:

Boots both services

Calls them

Runs stress tests

Runs Hardhat tests in vrf-spec

Prints ✅ summary

If run_full_demo.sh prints “5 passing”, you’ve reproduced
the full fairness pipeline locally.

8. What NOT to do in production
❌ Don't expose :8081 (PQ/VRF signer node) to the open internet without auth + rate limiting
❌ Don't leave API_KEY=demo in prod
❌ Don't skip reverse proxy / logging — regulators will ask for audit trail
❌ Don't rotate signer_addr silently; if you rotate keys, announce it on-chain / in governance

9. TL;DR
/random → fast, raw entropy for internal systems

/random_pq → signed entropy you can prove on-chain

r4sdk → Python client to consume

LotteryR4.sol → reference “provably fair” consumer contract

run_full_demo.sh → does end-to-end proof in one step
