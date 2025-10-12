# Re4ctor RNG Platform (Technical Overview)

This repository hosts the unified Re4ctor RNG components:
- `r4-cs` — core RNG based on HKDF + ChaCha20 (internal)
- `re4ctor-ipc` — secure IPC server with HMAC integrity
- `r4cat` — minimal CLI and C/Python client interface

**Note:** Core generator source is closed. Only client API and IPC protocol are public.

---

## Features

- Deterministic seeding (reproducible output)
- AF_UNIX socket IPC interface (`/run/r4sock/r4.sock`)
- HMAC-SHA256 frame protection (integrity required)
- C and Python API available
- Tested with PractRand / TestU01 / Dieharder / NIST

---

## Directory Layout

.
├─ include/ # Public C headers (r4.h)
├─ src/ # Client CLI (r4cat) and IPC adapter
├─ bindings/python/ # Python wrapper (simple subprocess or socket)
├─ deploy/ # systemd units (server deployment)
├─ tests/ # tamper tests / PractRand harness
└─ docs/ # (optional) protocol and architecture notes

yaml
Copy code

---

## Build (Client Components Only)

```bash
make clean
make
This builds:

bin/r4cat — CLI tool

lib/libr4.a — static client library

Dependencies: gcc, make, libssl-dev (for HMAC)

Usage (CLI - Local/IPC)
bash
Copy code
# 64 bytes, hex output
./bin/r4cat -n 64 -hex

# From IPC socket (if server running)
./bin/r4cat -n 1024 -sock /run/r4sock/r4.sock | hexdump -C
Exit codes:

pgsql
Copy code
0 - success
2 - HMAC/protocol error
3 - cannot connect (server missing or perms)
C API (Minimal)
c
Copy code
int r4_open(const char *path, const char *seed);
long long r4_read(void *out, size_t n);
uint32_t r4_u32(void);
void r4_close(void);
Example:

c
Copy code
#include "r4.h"
#include <stdio.h>

int main() {
    if (r4_open(NULL, "1") != 0) return 1;
    printf("%08x\n", r4_u32());
    r4_close();
}
Python Example
python
Copy code
from bindings.python.r4 import R4

r = R4()
print(r.read(32).hex())
r.close()
IPC Security (Server Required)
Socket: /run/r4sock/r4.sock

Key: /etc/r4/secret.key (32 bytes, root:r4users, mode 0640)

Each frame: MAGIC + LEN + NONCE + DATA + HMAC

If HMAC invalid → client rejects, no output.

Server Deployment (systemd)
bash
Copy code
sudo groupadd -f r4users
sudo mkdir -p /etc/r4
sudo dd if=/dev/urandom of=/etc/r4/secret.key bs=32 count=1 status=none
sudo chown root:r4users /etc/r4/secret.key
sudo chmod 640 /etc/r4/secret.key
Enable service (in deploy/):

bash
Copy code
sudo systemctl enable --now r4-server.socket r4-server.service
Tamper Test
Fake server without HMAC = must fail:

bash
Copy code
./bin/r4cat -n 32 -sock /run/r4sock/bad.sock
# -> "r4_read error (HMAC/protocol)" and exit 2
Status
RNG engine: internal, closed

IPC + API: public

Tested: PractRand 1TB+, Dieharder, NIST, TestU01

Next: VRF support, external proofs, Rust SDK
