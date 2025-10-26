#!/usr/bin/env python3
# 🧩 Known-Answer-Tests / Integrity check
import hashlib, json, sys, os
MANIFEST=os.path.join(os.path.dirname(__file__),"manifest.json")

def verify():
    try:
        man=json.load(open(MANIFEST))
        for f,h in man.items():
            with open(f,"rb") as fh: data=fh.read()
            if hashlib.sha256(data).hexdigest()!=h:
                raise ValueError(f"Hash mismatch for {f}")
        print("FIPS-SELFTEST: PASS")
        return True
    except Exception as e:
        print(f"FIPS-SELFTEST: FAIL → {e}")
        return False

if __name__=="__main__":
    sys.exit(0 if verify() else 1)
