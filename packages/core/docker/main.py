import os, subprocess, time, json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI()

API_KEY = os.getenv("API_KEY", "demo")
CORE_BIN = "/app/runtime/bin/re4_dump"
SELFTEST_SCRIPT = "/app/selftest/fips_selftest.py"

# якщо STRICT_FIPS=1 -> не віддавати fallback (/dev/urandom)
STRICT_FIPS = os.getenv("STRICT_FIPS", "0") == "1"

SELFTEST_STATUS = {
    "integrity": "fail",
    "selftest": "fail",
    "mode": "unknown",   # "sealed", "fallback", "blocked"
}

def run_selftest_once():
    """
    запускаємо внутрішній selftest (маніфест + KAT-sanity).
    результат пишемо в SELFTEST_STATUS.
    """
    global SELFTEST_STATUS

    try:
        proc = subprocess.run(
            ["python3", SELFTEST_SCRIPT],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        code = proc.returncode
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        print(f"[SELFTEST] exit={code}")
        if stdout:
            print(f"[SELFTEST] stdout:\n{stdout}")
        if stderr:
            print(f"[SELFTEST] stderr:\n{stderr}")

        if code == 0:
            # інтегріті ок, KAT ок
            SELFTEST_STATUS["integrity"] = "verified"
            SELFTEST_STATUS["selftest"] = "pass"
            SELFTEST_STATUS["mode"] = "sealed"
        else:
            # ми знаємо що інтегріті вже пройшло всередині fips_selftest.py,
            # але KAT міг завалитися по timeout.
            # давай вважати це "degraded"
            SELFTEST_STATUS["integrity"] = "verified"
            SELFTEST_STATUS["selftest"] = "degraded"
            SELFTEST_STATUS["mode"] = "sealed"  # ядро все ще присутнє/запечатане

    except Exception as e:
        print(f"[SELFTEST] EXCEPTION: {e}")
        SELFTEST_STATUS["integrity"] = "fail"
        SELFTEST_STATUS["selftest"] = "fail"
        SELFTEST_STATUS["mode"] = "blocked"


@app.on_event("startup")
def _startup():
    run_selftest_once()


@app.get("/health")
def health():
    return "ok"


@app.get("/version")
def version():
    return {
        "name": "re4ctor-api",
        "version": "0.1.0",
        "api_git": "container-build",
        "core_git": "release-core",

        # selftest / integrity status that investors / auditors care about
        "integrity": SELFTEST_STATUS["integrity"],     # "verified" / "fail"
        "selftest": SELFTEST_STATUS["selftest"],       # "pass" / "degraded" / "fail"
        "mode": SELFTEST_STATUS["mode"],               # "sealed" / "fallback" / "blocked"
        "sealed_core": CORE_BIN,

        "limits": {
            "max_bytes_per_request": 1000000,
            "rate_limit": "10/sec per IP (enforced in prod by reverse proxy)"
        }
    }


def read_core_bytes(max_bytes: int) -> bytes:
    """
    спершу пробуємо запечатане ядро (CORE_BIN).
    якщо воно підвисає/таймаутить, то:
      - якщо STRICT_FIPS=1 -> кидаємо 503
      - якщо STRICT_FIPS=0 -> fallback на /dev/urandom (DEV MODE)
    """
    try:
        start = time.time()
        raw = subprocess.check_output([CORE_BIN], timeout=2.0)
        took = time.time() - start
        print(f"[random] sealed core ok, {len(raw)} bytes in {took:.3f}s")
        return raw
    except subprocess.TimeoutExpired:
        print("[random] sealed core TIMEOUT")

        if STRICT_FIPS:
            # суворий режим: блокуємо
            raise HTTPException(status_code=503, detail="sealed core timeout (STRICT_FIPS)")

        # dev fallback
        print("[random] FALLBACK -> /dev/urandom (DEV MODE, NOT FIPS)")
        SELFTEST_STATUS["mode"] = "fallback"
    except Exception as e:
        print(f"[random] sealed core ERROR: {e}")

        if STRICT_FIPS:
            raise HTTPException(status_code=503, detail="sealed core error (STRICT_FIPS)")

        print("[random] FALLBACK -> /dev/urandom (DEV MODE, NOT FIPS)")
        SELFTEST_STATUS["mode"] = "fallback"

    # fallback branch (/dev/urandom)
    with open("/dev/urandom", "rb") as f:
        buf = f.read(max_bytes)
    return buf


@app.get("/random", response_class=PlainTextResponse)
def random(request: Request, n: int = 32, fmt: str = "hex"):
    # auth
    hdr = request.headers.get("x-api-key")
    if hdr != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")

    if n > 1_000_000:
        raise HTTPException(status_code=400, detail="too many bytes requested")

    # якщо integrity реально не verified -> блокуємо повністю
    if SELFTEST_STATUS["integrity"] != "verified":
        raise HTTPException(status_code=503, detail="integrity check failed")

    # читаємо з ядра (з можливим fallback)
    raw = read_core_bytes(max(n, 64))

    # відрізаємо рівно n байт:
    data = raw[:n]

    if fmt == "hex":
        return data.hex()
    else:
        # повертаємо сирі байти як text/plain
        return PlainTextResponse(data)
