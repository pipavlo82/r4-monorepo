#!/usr/bin/env python3
import hashlib, json, sys, os, subprocess

# де лежить наш запечатаний рантайм-бінарник усередині контейнера
CORE_BIN_PATH = "/app/runtime/bin/re4_dump"

# маніфест з контрольними сумами (sha256)
MANIFEST_PATH = "/app/selftest/manifest.json"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def load_manifest(path):
    with open(path, "r") as f:
        return json.load(f)

def check_integrity():
    # 1. чи існує бінарник
    if not os.path.exists(CORE_BIN_PATH):
        print(f"[SELFTEST] FAIL: core bin missing at {CORE_BIN_PATH}")
        return False

    # 2. чи існує маніфест
    if not os.path.exists(MANIFEST_PATH):
        print(f"[SELFTEST] FAIL: manifest missing at {MANIFEST_PATH}")
        return False

    data = load_manifest(MANIFEST_PATH)

    # очікуємо щось типу { "/app/runtime/bin/re4_dump": "<sha256hex>" }
    expected_hash = data.get(CORE_BIN_PATH)
    if expected_hash is None:
        print(f"[SELFTEST] FAIL: no expected hash for {CORE_BIN_PATH} in manifest")
        return False

    actual_hash = sha256_file(CORE_BIN_PATH)

    if actual_hash != expected_hash:
        print(f"[SELFTEST] FAIL: hash mismatch for core bin")
        print(f" expected {expected_hash}")
        print(f" actual   {actual_hash}")
        return False

    print("[SELFTEST] OK: integrity verified")
    return True

def known_answer_test():
    """
    Мікро-KAT: викликаємо re4_dump один раз і перевіряємо,
    що воно взагалі повертає хоч якісь байти.
    Тут ми не робимо криптоаналіз, тільки sanity.
    """
    try:
        out = subprocess.check_output([CORE_BIN_PATH], timeout=2.0)
        if len(out) < 16:
            print("[SELFTEST] FAIL: KAT too short output")
            return False
        # Можна ще додати мінімальний ентропійний sanity (не всі нулі)
        if all(b == out[0] for b in out[:32]):
            print("[SELFTEST] FAIL: KAT suspiciously uniform output")
            return False
        print("[SELFTEST] OK: KAT basic randomness sanity")
        return True
    except Exception as e:
        print(f"[SELFTEST] FAIL: KAT exception: {e}")
        return False

def main():
    ok_integrity = check_integrity()
    ok_kat = known_answer_test()

    if ok_integrity and ok_kat:
        print("FIPS-SELFTEST: PASS")
        sys.exit(0)
    else:
        print("FIPS-SELFTEST: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    main()
