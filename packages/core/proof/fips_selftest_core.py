#!/usr/bin/env python3
#
# fips_selftest_core.py
#
# Minimal FIPS-style startup self-test for RE4CTOR entropy core.
# 1. Supply-chain integrity: verify SHA-256 of sealed core binary.
# 2. Known Answer Test (KAT): run core to emit N bytes and sanity check output.
#
# Exit code:
#   0 -> OK to serve randomness
#   1 -> FAIL (service must refuse to start / go STRICT_FIPS=1 fail-closed)

import hashlib
import os
import subprocess
import sys
from pathlib import Path

# --- CONFIG -------------------------------------------------------

# absolute path to sealed core binary in this repo layout
CORE_BIN = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../../core/bin/re4_dump"
    )
)

# expected sha256 of that binary
EXPECTED_SHA256 = "17b498bb3a373e8d8114e0e212efddb922c1f98e36d4b74134d196ce2733c995"

# how many bytes we ask core to produce for the self-test
KAT_NBYTES = 32

# how long we're willing to wait for the core to answer
KAT_TIMEOUT = 2.0  # seconds

# -----------------------------------------------------------------

def fail(msg: str):
    print(f"[SELFTEST:FAIL] {msg}")
    sys.exit(1)

def ok(msg: str):
    print(f"[SELFTEST:OK] {msg}")

def info(msg: str):
    print(f"[SELFTEST] {msg}")

def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    # 1. make sure binary exists and is executable
    if not os.path.isfile(CORE_BIN):
        fail(f"core binary not found at {CORE_BIN}")
    if not os.access(CORE_BIN, os.X_OK):
        fail(f"core binary not executable at {CORE_BIN} (chmod +x ?)")

    # 2. verify supply-chain integrity (hash match)
    actual_hash = sha256_of_file(CORE_BIN)
    if actual_hash != EXPECTED_SHA256:
        fail(f"sha256 mismatch: got {actual_hash}, expected {EXPECTED_SHA256}")
    ok("core binary sha256 matches expected")

    # 3. run Known Answer Test (sanity output)
    try:
        out = subprocess.check_output(
            [CORE_BIN, str(KAT_NBYTES)],
            timeout=KAT_TIMEOUT
        )
    except subprocess.TimeoutExpired:
        fail(f"core timeout after {KAT_TIMEOUT}s (hung startup?)")
    except Exception as e:
        fail(f"core error: {e}")

    # 4. basic sanity checks on output
    if len(out) != KAT_NBYTES:
        fail(f"core returned {len(out)} bytes, expected {KAT_NBYTES}")

    if all(b == 0x00 for b in out):
        fail("core output all-zero (suspicious)")

    ok(f"core emitted {len(out)} bytes non-zero entropy")

    # if we got here, we pass
    sys.exit(0)

if __name__ == "__main__":
    main()

