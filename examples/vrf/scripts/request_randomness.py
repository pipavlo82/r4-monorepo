#!/usr/bin/env python3
import os, subprocess, hashlib, time, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
r4cat = os.path.join(ROOT, "bin", "r4cat")
if not os.path.exists(r4cat):
    print("r4cat not found. Build first: make -B", file=sys.stderr)
    sys.exit(1)

def get_rand32():
    return subprocess.check_output([r4cat, "-n", "32"])

def fake_proof(rand):
    ts = str(int(time.time())).encode()
    return hashlib.sha256(rand + ts).digest()

if __name__ == "__main__":
    rnd = get_rand32()
    prf = fake_proof(rnd)
    rid = hashlib.sha256(rnd).digest().hex()
    print("roundId    :", rid)
    print("randomness :", rnd.hex())
    print("proof      :", prf.hex())
