from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import subprocess, os, binascii

app = FastAPI(
    title="re4ctor API",
    version="0.1.0",
)

API_KEY = os.getenv("API_KEY", "demo")
CORE_BIN = "/app/runtime/bin/re4_dump"

MAX_BYTES = 1_000_000  # hard cap

@app.get("/health")
def health():
    return "ok"

@app.get("/version")
def version():
    return {
        "name": "re4ctor-api",
        "version": "0.1.0",
        "api_git": os.getenv("API_GIT", "container-build"),
        "core_git": os.getenv("CORE_GIT", "release-core"),
        "limits": {
            "max_bytes_per_request": MAX_BYTES,
            "rate_limit": "10/sec per IP (enforced in prod by reverse proxy)",
        },
    }

def _read_core(n_bytes: int) -> bytes:
    # run core binary and read n_bytes from stdout
    p = subprocess.Popen(
        [CORE_BIN],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        close_fds=True,
    )
    out = p.stdout.read(n_bytes)
    p.kill()
    return out

@app.get("/random")
def get_random(request: Request, n: int, fmt: str = None):
    # auth check
    key = request.headers.get("x-api-key") or request.query_params.get("key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")

    # basic limits
    if n <= 0 or n > MAX_BYTES:
        raise HTTPException(status_code=400, detail="invalid n")

    # pull bytes from core
    raw = _read_core(n)
    if len(raw) != n:
        raise HTTPException(status_code=500, detail="core short read")

    # hex mode
    if fmt == "hex":
        return PlainTextResponse(binascii.hexlify(raw).decode("ascii"))

    # raw mode (bytes)
    return PlainTextResponse(raw, media_type="application/octet-stream")
