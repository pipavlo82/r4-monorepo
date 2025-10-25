import os, subprocess, time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI()

API_KEY = os.getenv("API_KEY", "demo")
CORE_BIN = "/app/runtime/bin/re4_dump"

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
        "limits": {
            "max_bytes_per_request": 1000000,
            "rate_limit": "10/sec per IP (enforced in prod by reverse proxy)"
        },
    }

@app.get("/random", response_class=PlainTextResponse)
def random(request: Request, n: int = 32, fmt: str = "hex"):
    # auth
    hdr = request.headers.get("x-api-key")
    if hdr != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")

    if n > 1_000_000:
        raise HTTPException(status_code=400, detail="too many bytes requested")

    # call core binary
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

    data = raw[:n]

    if fmt == "hex":
        return data.hex()
    else:
        return PlainTextResponse(data)
