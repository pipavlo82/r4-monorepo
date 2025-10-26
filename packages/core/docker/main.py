import os, subprocess, time, json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI()

API_KEY = os.getenv("API_KEY", "demo")
CORE_BIN = "/app/runtime/bin/re4_dump"

# ------------------------------------------------------------------
# FIPS-style startup self-test
# - перевіряє SHA-256 core/bin/re4_dump проти зафіксованого manifest.json
# - якщо хтось підмінив бінарник -> SELFTEST_OK = False
# - /random тоді не віддає випадковість
# ------------------------------------------------------------------
def run_selftest():
    """
    запускаємо внутрішній selftest всередині контейнера.
    очікуємо, що Dockerfile скопіював packages/core/selftest -> /app/selftest
    """
    try:
        result = subprocess.run(
            ["python3", "/app/selftest/fips_selftest.py"],
            capture_output=True,
            text=True,
            timeout=3
        )
        # друкуємо результат в stdout контейнера, щоб було видно в логах
        print(result.stdout.strip())
        return result.returncode == 0
    except Exception as e:
        print(f"SELFTEST EXCEPTION: {e}")
        return False

SELFTEST_OK = run_selftest()
# ------------------------------------------------------------------


@app.get("/health")
def health():
    # ПРОСТИЙ лівнес-чек
    return "ok"


@app.get("/version")
def version():
    # це те, що бачить аудитор / інфраструктурник / інвестор
    return {
        "name": "re4ctor-api",
        "version": "0.1.0",
        "api_git": "container-build",
        "core_git": "release-core",

        # нові поля для довіри
        "integrity": "verified" if SELFTEST_OK else "fail",
        "selftest": "pass" if SELFTEST_OK else "fail",
        "sealed_core": CORE_BIN,

        "limits": {
            "max_bytes_per_request": 1_000_000,
            "rate_limit": "10/sec per IP (enforced in prod by reverse proxy)"
        },
    }


@app.get("/random", response_class=PlainTextResponse)
def random(request: Request, n: int = 32, fmt: str = "hex"):
    # -------------------------------------------------
    # 1. integrity gate: якщо self-test не пройшов — стоп
    # -------------------------------------------------
    if not SELFTEST_OK:
        raise HTTPException(
            status_code=503,
            detail="entropy core integrity check failed"
        )

    # -------------------------------------------------
    # 2. auth: x-api-key має збігатися з API_KEY
    # -------------------------------------------------
    hdr = request.headers.get("x-api-key")
    if hdr != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")

    # -------------------------------------------------
    # 3. валідація параметрів
    # -------------------------------------------------
    if n < 1:
        raise HTTPException(status_code=400, detail="too few bytes requested")

    if n > 1_000_000:
        raise HTTPException(status_code=400, detail="too many bytes requested")

    # -------------------------------------------------
    # 4. викликаємо core binary
    #    NOTE: зараз core просто повертає великий буфер байтів
    #    ми його не тримаємо довше ніж треба
    # -------------------------------------------------
    try:
        start = time.time()
        raw = subprocess.check_output([CORE_BIN], timeout=5.0)
        took = time.time() - start
        print(f"[re4/random] core ok, {len(raw)} bytes in {took:.3f}s")
    except subprocess.TimeoutExpired:
        print("[re4/random] core TIMEOUT")
        raise HTTPException(status_code=500, detail="core timeout")
    except Exception as e:
        print(f"[re4/random] core ERROR: {e}")
        raise HTTPException(status_code=500, detail="core error")

    # беремо рівно n байт з буфера
    data = raw[:n]

    # -------------------------------------------------
    # 5. формат відповіді
    # -------------------------------------------------
    if fmt == "hex":
        # віддаємо рядок з hex
        return data.hex()
    else:
        # віддаємо як text/plain (але це будуть raw байти)
        # важливо: fastapi.responses.PlainTextResponse очікує str,
        # тому якщо просили не-hex, краще вернути hex fallback
        # щоб не намагатися кинути binary прямо в текстовий респонс
        return data.hex()
