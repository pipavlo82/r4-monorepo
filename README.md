# Re4ctor RNG Platform  
**High-Integrity Randomness for Security, Blockchain, and Fair Systems**  
*(Core R4-CS is proprietary — available via enterprise license or audit access)*

---

## 🔍 Overview

Re4ctor is a high-assurance Random Number Generation (RNG) platform built for:
- 🎲 **Provably-fair systems & simulations**
- 🛡️ **Security-critical infrastructure / HSM replacement**
- ⛓️ **Blockchain randomness & future VRF oracle services**

The cryptographic core (**r4-cs**) remains private to protect IP and licensing value.  
This repository provides the **public interface**, **client code**, **specs**, and **tamper-proof CI tests**, proving authenticity without exposing the algorithm internals.

---

## 🧭 Architecture

| Layer | Role | Status |
|-------|------|--------|
| `r4-cs` | Core HKDF → ChaCha20 DRBG (Closed) | 🔒 Proprietary |
| `re4ctor-ipc` | Secure IPC over Unix socket (HMAC-framed) | 🟢 Public Binary |
| `r4cat` / `bindings/python/r4.py` | Public clients (C / Python) | 🟢 Open |
| `tests/tamper.sh` | Tamper-detection integrity test | ✅ CI Verified |

---

## ⚙️ Installation (Linux / WSL / Ubuntu)

git clone https://github.com/pipavlo82/r4-monorepo.git
cd r4-monorepo
make

arduino
Copy code

Run smoke test (requires running IPC server):
./bin/r4cat -n 32 -hex # 32 bytes of verified randomness

yaml
Copy code

---

## 🛡️ Security & Trust Model

| Feature | Status |
|---------|--------|
| HKDF-SHA256 → ChaCha20 DRBG | ✅ Core (Private) |
| HMAC-SHA256 Framed IPC | ✅ Implemented |
| Tamper Detection | ✅ Client rejects fake server |
| CI Integrity Test | ✅ Required for every commit (`tests/tamper.sh`) |
| NIST STS / PractRand / Dieharder | ✅ Passed (reports available) |

🔒 *Core algorithm (r4-cs) is not shipped here to prevent IP theft and allow enterprise licensing.*

---

## 🧪 Tamper Test (CI Proven)

The client **must reject any fake or manipulated data stream**.  
This is enforced in GitHub Actions via `tests/tamper.sh`.

OK: tamper rejected (rc=2), stdout empty

yaml
Copy code

---

## 💻 Developer API (C / Python)

### C Example
```c
uint32_t x = r4_u32();
printf("Random: %08x\n", x);
Python Example
python
Copy code
from bindings.python.r4 import R4
r = R4()
print(r.read(32).hex())
r.close()
🌐 Blockchain & VRF Roadmap
Phase	Feature
✅ Phase 1	Secure IPC & Client Library
🔄 Phase 2	VRF Output Formatting (Ethereum / WASM)
🔲 Phase 3	Oracle / VRF Network Integration

💰 Licensing & Enterprise Access
Core R4-CS is proprietary
Available under Commercial License or Audit Partnership.
Roadmap includes: OEM Integration, Cloud API, Hardware RNG Module.

📧 Contact: [via GitHub Issues or private request]

🧠 Why Re4ctor?
Problem with Traditional RNG	Re4ctor Solution
Open RNG → Easy to forge	HMAC-protected stream
No provenance	Commit/Reveal, Audit logs
No IP moat	Proprietary core with verifiable spec

📚 Reports & Compliance
✅ NIST STS, Dieharder, PractRand (Full logs available offline)

🔒 Core spec: docs/SPEC-R4CS.md

📎 Cryptographic paper (in preparation for IACR / USENIX)

🏁 Final Notes
This repository is not just code — it's a platform for verifiable randomness.
Trusted by design, auditable by spec, protected by IP.

Investors / Partners — Core access via NDA & Licensing.
Developers — Free client API integration.
Auditors — Spec-based verification available.

csharp
Copy code
[CI Status Badge Incoming]
Built by Re4ctor Labs — 2025
