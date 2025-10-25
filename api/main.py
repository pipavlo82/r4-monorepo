import os
import subprocess
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse, Response, JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

#
# -----------------------------------------------------------------------------
# config / env
# -----------------------------------------------------------------------------
#

API_KEY = os.getenv("API_KEY", "change-me")

# максимум скільки байтів за один запит можна витягнути
MAX_BYTES = int(os.getenv("MAX_BYTES", "1000000"))

# шлях до нашого RNG-бінарника з re4ctor-core
RNG_BIN = os.getenv("RNG_BIN", "/home/pavlo/re4ctor-core/build/re4_dump")

# рейт-ліміт slowapi (наприклад "10/second")
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/second")

# git info: API_GIT ми задаємо через systemd Environment / .env
API_GIT = os.getenv("API_GIT", None)


def get_core_git() -> Optional[str]:
    """
    беремо короткий git hash з репо re4ctor-core.
    якщо не вийшло (наприклад, нема git або нема репо) -> None
    """
    try:
        out = subprocess.check_output(
            [
                "git",
                "-C",
                "/home/pavlo/re4ctor-core",
                "rev-parse",
                "--short",
                "HEAD",
            ],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8").strip()
    except Exception:
        return None


CORE_GIT = get_core_git()

#
# -----------------------------------------------------------------------------
# FastAPI app + SlowAPI limiter
# -----------------------------------------------------------------------------
#

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="re4ctor-api",
    version="0.1.0",
)

# глобальний handler для 429
@app.exception_handler(RateLimitExceeded)
def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "rate limit exceeded"},
    )

#
# -----------------------------------------------------------------------------
# helpers
# -----------------------------------------------------------------------------
#

def check_key(header_key: Optional[str], query_key: Optional[str]) -> None:
    """
    Аутентифікація.
    Даємо доступ, якщо або x-api-key у заголовку,
    або ?key= у query збігається з API_KEY.
    Інакше -> 401.
    """
    supplied = header_key or query_key
    if supplied != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")


def get_re4_bytes(n: int) -> bytes:
    """
    Викликає зовнішній генератор (/home/pavlo/re4ctor-core/build/re4_dump),
    читає n байтів зі stdout і кидає помилку, якщо не вдалося.
    """
    try:
        proc = subprocess.Popen(
            [RNG_BIN],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="rng backend not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"rng spawn error: {e}")

    try:
        raw = proc.stdout.read(n)
    finally:
        # гарантуємо, що не лишаємо процес висіти
        proc.kill()

    if raw is None or len(raw) != n:
        raise HTTPException(status_code=500, detail="rng backend short read")

    return raw

#
# -----------------------------------------------------------------------------
# PUBLIC ENDPOINTS (no auth)
# -----------------------------------------------------------------------------
#

@app.get("/health", response_class=PlainTextResponse)
def health() -> str:
    return "ok"


@app.get("/version", response_class=JSONResponse)
def version():
    """
    Метадані сервісу для моніторингу / дебагу.
    """
    return {
        "name": "re4ctor-api",
        "version": "0.1.0",
        "api_git": API_GIT,
        "core_git": CORE_GIT,
        "limits": {
            "max_bytes_per_request": MAX_BYTES,
            "rate_limit": RATE_LIMIT,
        },
    }


@app.get("/info", response_class=PlainTextResponse)
def info() -> str:
    """
    Людське пояснення API, можна юзерам кидати.
    """
    return (
        "re4ctor entropy API\n"
        "\n"
        "Public:\n"
        "  GET /health                  -> 200 OK, 'ok'\n"
        "  GET /version                 -> { name, version }\n"
        "  GET /info                    -> this help\n"
        "\n"
        "Protected (API key required):\n"
        "  GET /random?n=<bytes>[&fmt=hex]\n"
        "\n"
        "Auth options:\n"
        "  Header:  x-api-key: <KEY>\n"
        "  or\n"
        "  Query :  ?key=<KEY>\n"
        "\n"
        "Response:\n"
        "  fmt=hex  -> hex text (len = 2*n chars)\n"
        "  no fmt   -> raw bytes (application/octet-stream)\n"
        "\n"
        "Limits:\n"
        f"  n <= {MAX_BYTES} bytes/request\n"
        f"  rate: {RATE_LIMIT} per client IP\n"
    )

#
# -----------------------------------------------------------------------------
# PROTECTED ENDPOINT
# -----------------------------------------------------------------------------
#

@app.get("/random")
@limiter.limit(RATE_LIMIT)
def random_bytes(
    request: Request,
    n: int = Query(..., gt=0),
    fmt: Optional[str] = Query(default=None),
    key: Optional[str] = Query(default=None),
):
    """
    Основний endpoint:
      - auth по ключу
      - rate limit
      - віддаємо ентропію з re4_dump
    """

    # 1. auth
    header_key = request.headers.get("x-api-key")
    check_key(header_key, key)

    # 2. validate size
    if n > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"requested {n} bytes > limit {MAX_BYTES}",
        )

    # 3. отримуємо байти
    raw = get_re4_bytes(n)

    # 4. audit log -> попадає в journald через stdout сервісу
    client_ip = request.client.host if request.client else "?"
    head4 = raw[:4].hex() if raw else ""
    print(
        f"[re4/random] ip={client_ip} n={n} fmt={fmt} head4={head4}",
        flush=True,
    )

    # 5. формат відповіді
    if fmt == "hex":
        return PlainTextResponse(raw.hex(), status_code=200)

    return Response(
        content=raw,
        media_type="application/octet-stream",
        status_code=200,
    )
