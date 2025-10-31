# 📚 API Usage — RE4CTOR / R4 entropy API

This guide shows how to call the API from:
- curl
- Python (r4sdk)
- JavaScript / Node
- Solidity (Verifier)

It covers both:
- Core entropy node `:8080`
- PQ/VRF signed randomness node `:8081`

---

## 1) Health / Version

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

self-test / integrity info

Archive /version output at startup to prove to an auditor that you ran a legitimate, uncompromised build.

2) Get raw entropy (:8080)
Endpoint

bash
Copy code
GET /random?n=<bytes>&fmt=<hex|base64|raw>
Auth

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
Error example (bad key)

bash
Copy code
curl -i -H "X-API-Key: WRONG" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# HTTP/1.1 401 Unauthorized
# {"detail":"invalid api key"}
3) Python usage (r4sdk)
Install

bash
Copy code
pip install r4sdk
Use

python
Copy code
from r4sdk import R4Client

client = R4Client(
    api_key="demo",
    host="http://localhost:8080",
)
rand_bytes = client.get_random(32)
print("Random hex:", rand_bytes.hex())
Typical integrations

generate wallet keys

draw raffle winners off-chain

seed game matchmaker / brackets

rotate validator committees

4) JavaScript / Node usage
js
Copy code
import fetch from "node-fetch";

const res = await fetch(
  "http://localhost:8080/random?n=8&fmt=hex",
  { headers: { "X-API-Key": "demo" } }
);
const hex = await res.text();

// Example: fair dice roll 1-100
const roll = (parseInt(hex.substring(0, 8), 16) % 100) + 1;
console.log("Rolled:", roll);
5) PQ/VRF signed randomness (:8081)
This node gives you randomness plus a cryptographic proof you can verify in Solidity.

Request

bash
Copy code
curl -s -H "X-API-Key: demo" \
  "http://localhost:8081/random_pq?sig=ecdsa" | jq
Typical response

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
random — the random value (integer)

v,r,s — ECDSA signature parts (EIP-191)

signer_addr — Ethereum address of the oracle signer

timestamp — ISO time of generation

pq_mode — whether PQ / Dilithium path was used

Enterprise builds

bash
Copy code
curl -s -H "X-API-Key: demo" \
  "http://localhost:8081/random_pq?sig=dilithium" | jq
Returns ML-DSA-65 (Dilithium3, FIPS-204) signature instead of secp256k1 ECDSA.

Note: The API returns random as an integer; on-chain you’ll pass it as bytes32.

6) On-chain verification (Solidity)
Contracts live in vrf-spec/contracts/:

R4VRFVerifierCanonical.sol

LotteryR4.sol

High-level flow

solidity
Copy code
// Off-chain: call /random_pq?sig=ecdsa
// On-chain: pass randomness + sig into drawWinner()

require(
    verifier.verify(
        randomness,   // bytes32
        v, r, s,
        trustedSigner // oracle address
    ),
    "Invalid signature"
);

uint256 winnerIndex = uint256(randomness) % players.length;
address winner = players[winnerIndex];
emit WinnerSelected(winner, winnerIndex, randomness);
Passing integer → bytes32 (JS)

js
Copy code
import { ethers } from "ethers";
const randomnessInt = data.random;                 // from API (number)
const randomnessBytes32 = ethers.toBeHex(randomnessInt, 32); // bytes32

const tx = await lottery.drawWinner(randomnessBytes32, v, r, s);
const rc = await tx.wait();
const ev = rc.logs.find(l => l.fragment?.name === 'WinnerSelected');
console.log('Winner:', ev?.args?.winner);
Provable fairness

contract enforces that randomness truly came from your RE4CTOR node (signature)

modulo is deterministic

everything is on-chain for audit / replay

7) Stress / audit tooling
These helper scripts ship in repo root:

stress_core.sh
Load-tests :8080 (/random) to confirm throughput / rate limit.
Expect ~950k req/s sustained, p99 ~1.1 ms on decent hardware.

stress_vrf.py
Hammers :8081/random_pq in parallel, shows:

how many 200 OK

how many 429 (rate-limited)

prep_vrf_for_chain.py
Fetches a live (random, v, r, s, signer_addr) bundle from :8081 and formats it for Hardhat tests and LotteryR4.drawWinner().

run_full_demo.sh
One-shot script that:

boots both services

calls them

runs stress tests

runs Hardhat tests in vrf-spec

prints ✅ summary

If run_full_demo.sh prints “6 passing”, you’ve reproduced the full fairness pipeline locally.

8) What NOT to do in production
❌ Expose :8081 (PQ/VRF signer) to the open internet without auth + rate limiting

❌ Leave API_KEY=demo in prod

❌ Skip reverse proxy / logging — regulators will want an audit trail

❌ Rotate signer_addr silently — announce rotations on-chain / via governance

9) TL;DR
/random → fast raw entropy for internal systems

/random_pq → signed entropy you can prove on-chain

r4sdk → Python client

LotteryR4.sol → reference “provably fair” consumer contract

run_full_demo.sh → end-to-end proof (expect 6 passing)

markdown
Copy code
