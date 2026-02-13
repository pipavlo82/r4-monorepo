import urllib.request
import urllib.error
import logging
import os
import binascii
from typing import Optional

logger = logging.getLogger(__name__)
from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Depends,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
import httpx

from eth_keys import keys
from eth_account import Account


# -------------------------------------------------------------------
# Config from environment
# -------------------------------------------------------------------

def _clean_env(name: str, default: str) -> str:
    raw = os.getenv(name, default)
    if raw is None:
        return default
    return raw.strip()


# За замовчуванням — локалка; у проді все одно переїде в ENV з r4-prod
CORE_URL = _clean_env("CORE_URL", "http://localhost:8080").rstrip("/")
VRF_URL = _clean_env("VRF_URL", "http://localhost:8081").rstrip("/")

# Публічний ключ для клієнтів (X-API-Key / ?api_key=)
PUBLIC_API_KEY = _clean_env("PUBLIC_API_KEY", _clean_env("API_KEY", "demo"))
# Внутрішній ключ для звернення з gateway до core/vrf
INTERNAL_R4_API_KEY = _clean_env("INTERNAL_R4_API_KEY", PUBLIC_API_KEY)

GATEWAY_VERSION = _clean_env("GATEWAY_VERSION", "v0.1.7")
LOG_LEVEL = _clean_env("LOG_LEVEL", "info")


# -------------------------------------------------------------------
# FastAPI app + CORS
# -------------------------------------------------------------------

app = FastAPI(
    title="RE4CTOR SaaS API Gateway",
    version=GATEWAY_VERSION,
)

CORS_ORIGINS = [
    "https://re4ctor.com",
    "https://www.re4ctor.com",
    "https://api.re4ctor.com",
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8082",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Middleware: service headers
# -------------------------------------------------------------------

@app.middleware("http")
async def add_svc_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-R4-Gateway-Version"] = GATEWAY_VERSION
    resp.headers["X-R4-Core-URL"] = CORE_URL
    resp.headers["X-R4-VRF-URL"] = VRF_URL
    return resp


# -------------------------------------------------------------------
# Simple API-key auth
# -------------------------------------------------------------------

async def require_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
):
    """
    Проста dev-авторизація:
    - API key може прийти або з заголовка X-API-Key,
    - або як query параметр ?api_key=...
    """
    query_key = request.query_params.get("api_key")
    api_key = x_api_key or query_key

    # allow local demo key and paid keys (r4_*) to reach billing middleware
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if (api_key != PUBLIC_API_KEY) and (not str(api_key).startswith("r4_")):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


# -------------------------------------------------------------------
# Models
# -------------------------------------------------------------------

class VerifyRequest(BaseModel):
    msg_hash: str
    r: str
    s: str
    v: int
    expected_signer: str


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

HEX_CHARS = set("0123456789abcdef")


def _clean_hex_64(s: str, field: str) -> str:
    if s is None:
        raise HTTPException(status_code=400, detail=f"{field} is required")

    raw = s.strip().lower()
    if raw.startswith("0x"):
        raw = raw[2:]

    if len(raw) != 64 or any(c not in HEX_CHARS for c in raw):
        raise HTTPException(
            status_code=400,
            detail="msg_hash/r/s must be 64-hex (no 0x)",
        )
    return raw


def _normalize_v(v: int) -> int:
    if v in (27, 28):
        return v - 27
    if v in (0, 1):
        return v
    raise HTTPException(
        status_code=400,
        detail="v must be 0/1 or 27/28",
    )


def _normalize_address(addr: str) -> str:
    if not addr:
        return ""
    a = addr.strip()
    if not a.startswith("0x"):
        a = "0x" + a
    return a.lower()


# -------------------------------------------------------------------
# HTML landing page (розширена, «товста» версія)
# -------------------------------------------------------------------

HOMEPAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>RE4CTOR SaaS API Gateway</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {
      --bg: #020817;
      --bg-2: #020617;
      --card: #020617;
      --accent1: #22c55e;
      --accent2: #06b6d4;
      --accent3: #facc15;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --border: #1f2937;
      --error: #f97373;
      --ok: #22c55e;
      --font: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      --mono: "SF Mono", ui-monospace, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    }
    * {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      padding: 0;
      font-family: var(--font);
      background:
        radial-gradient(circle at 0% 0%, #1d283a 0%, rgba(15,23,42,0.05) 40%, transparent 60%),
        radial-gradient(circle at 100% 0%, #0f766e 0%, rgba(15,23,42,0.15) 35%, transparent 60%),
        radial-gradient(circle at 50% 100%, #1d283a 0%, rgba(2,6,23,0.9) 55%, #020617 100%);
      color: var(--text);
      min-height: 100vh;
    }
    a {
      color: inherit;
      text-decoration: none;
    }
    .page {
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 16px 72px;
    }
    .top-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 18px;
    }
    .logo-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .logo-mark {
      width: 32px;
      height: 32px;
      border-radius: 10px;
      background:
        radial-gradient(circle at 30% 0%, #22c55e 0%, transparent 55%),
        radial-gradient(circle at 70% 90%, #06b6d4 0%, transparent 55%),
        #020617;
      border: 1px solid rgba(148,163,184,0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 700;
      color: #e5e7eb;
      box-shadow: 0 0 18px rgba(34,197,94,0.25);
    }
    .logo-text-main {
      font-size: 15px;
      font-weight: 600;
    }
    .logo-text-sub {
      font-size: 11px;
      color: var(--muted);
    }
    .top-badge {
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(15,23,42,0.9);
      border: 1px solid rgba(148,163,184,0.3);
      font-size: 11px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
    }
    .pill-ok {
      padding: 2px 8px;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--accent1), var(--accent2));
      color: #020617;
      font-weight: 600;
      font-size: 11px;
    }
    .chip-row {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(15,23,42,0.9);
      border: 1px solid rgba(148,163,184,0.3);
      font-size: 12px;
      margin-bottom: 18px;
    }
    .chip-pill {
      padding: 2px 8px;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--accent1), var(--accent2));
      color: #020617;
      font-weight: 600;
    }
    .chip-sub {
      color: var(--muted);
    }
    h1 {
      font-size: 34px;
      line-height: 1.1;
      margin: 0 0 8px;
    }
    .hero-sub {
      max-width: 620px;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.55;
      margin-bottom: 18px;
    }
    .hero-kpi-row {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 20px;
    }
    .hero-kpi {
      font-size: 12px;
      color: var(--muted);
    }
    .hero-kpi span {
      font-weight: 600;
      color: var(--text);
    }
    .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 28px;
    }
    .btn-primary {
      border: none;
      outline: none;
      padding: 10px 20px;
      border-radius: 999px;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      background: linear-gradient(90deg, var(--accent1), var(--accent2));
      color: #020617;
      box-shadow: 0 10px 30px rgba(34,197,94,0.25);
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
    .btn-primary span.icon {
      font-size: 16px;
    }
    .btn-ghost {
      padding: 9px 18px;
      border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.5);
      background: rgba(15,23,42,0.6);
      color: var(--text);
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 22px;
      font-size: 11px;
      color: var(--muted);
    }
    .badge-pill {
      padding: 3px 8px;
      border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.4);
      background: rgba(15,23,42,0.9);
    }
    .badge-pill strong {
      color: var(--text);
      font-weight: 600;
    }
    .layout-main {
      display: grid;
      grid-template-columns: minmax(0, 3.1fr) minmax(0, 2.3fr);
      gap: 26px;
      align-items: flex-start;
    }
    @media (max-width: 960px) {
      .layout-main {
        grid-template-columns: minmax(0,1fr);
      }
    }
    .section-title {
      font-size: 16px;
      font-weight: 600;
      margin: 22px 0 6px;
    }
    .section-sub {
      font-size: 13px;
      color: var(--muted);
      max-width: 640px;
      margin-bottom: 12px;
    }
    .playground-panel {
      border-radius: 18px;
      background: rgba(15,23,42,0.92);
      border: 1px solid rgba(31,41,55,0.9);
      padding: 14px 14px 16px;
      box-shadow:
        0 18px 40px rgba(15,23,42,0.9),
        0 0 0 1px rgba(15,23,42,0.5) inset;
      position: relative;
    }
    .playground-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
    }
    .playground-title {
      font-size: 14px;
      font-weight: 600;
    }
    .playground-pill {
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.5);
      color: var(--muted);
    }
    .playground-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 10px;
    }
    .playground-input {
      flex: 1 1 220px;
      min-width: 0;
      padding: 8px 10px;
      border-radius: 999px;
      border: 1px solid rgba(31,41,55,1);
      background: rgba(2,6,23,0.95);
      color: var(--text);
      font-size: 13px;
      font-family: var(--mono);
    }
    .playground-input::placeholder {
      color: rgba(148,163,184,0.7);
    }
    .playground-btn {
      border-radius: 999px;
      padding: 8px 16px;
      border: none;
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
      background: linear-gradient(90deg, var(--accent1), var(--accent2));
      color: #020617;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .playground-btn.secondary {
      background: rgba(15,23,42,0.95);
      border: 1px solid rgba(148,163,184,0.6);
      color: var(--text);
    }
    .playground-btn span.icon {
      font-size: 15px;
    }
    .playground-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 11px;
      color: var(--muted);
      margin-bottom: 4px;
    }
    .playground-meta span.code {
      font-family: var(--mono);
      font-size: 11px;
      color: #e5e7eb;
    }
    .log-box {
      margin-top: 8px;
      border-radius: 12px;
      background: rgba(2,6,23,0.98);
      border: 1px solid rgba(31,41,55,1);
      padding: 8px;
      font-family: var(--mono);
      font-size: 11px;
      color: #e5e7eb;
      max-height: 230px;
      overflow: auto;
      white-space: pre;
    }
    .log-line-ok {
      color: var(--ok);
    }
    .log-line-err {
      color: var(--error);
    }
    .log-line-muted {
      color: var(--muted);
    }
    .snapshot-card {
      background:
        radial-gradient(circle at top left, rgba(34,197,94,0.18), transparent 52%),
        radial-gradient(circle at top right, rgba(56,189,248,0.14), transparent 55%),
        #020617;
      border-radius: 18px;
      padding: 14px 14px 16px;
      border: 1px solid rgba(148,163,184,0.35);
      box-shadow:
        0 16px 38px rgba(15,23,42,0.85),
        0 0 0 1px rgba(15,23,42,0.6) inset;
    }
    .snapshot-header {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .snapshot-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent1);
      box-shadow: 0 0 8px rgba(34,197,94,0.9);
    }
    .snapshot-sub {
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 10px;
    }
    .snapshot-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 10px;
    }
    .tag-pill {
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.5);
      color: var(--muted);
      background: rgba(15,23,42,0.9);
    }
    .tag-pill--accent {
      border: none;
      background: rgba(34,197,94,0.12);
      color: var(--accent1);
    }
    .tag-pill--pq {
      border: none;
      background: rgba(6,182,212,0.12);
      color: var(--accent2);
    }
    .snapshot-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 6px;
    }
    @media (max-width: 520px) {
      .snapshot-grid {
        grid-template-columns: repeat(2, minmax(0,1fr));
      }
    }
    .snapshot-box {
      border-radius: 14px;
      padding: 9px 9px 10px;
      background: rgba(15,23,42,0.96);
      border: 1px solid rgba(31,41,55,1);
    }
    .snapshot-label {
      font-size: 11px;
      color: var(--muted);
      margin-bottom: 2px;
    }
    .snapshot-value {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 1px;
    }
    .snapshot-meta {
      font-size: 11px;
      color: var(--muted);
    }
    .curl-card {
      background: rgba(15,23,42,0.98);
      border: 1px solid rgba(31,41,55,1);
      border-radius: 18px;
      padding: 12px 14px 14px;
      box-shadow:
        0 18px 30px rgba(15,23,42,0.9),
        0 0 0 1px rgba(15,23,42,0.7) inset;
      font-family: var(--mono);
      font-size: 11px;
      color: #e5e7eb;
      margin-top: 16px;
    }
    .curl-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
      font-size: 11px;
      color: var(--muted);
    }
    .curl-badge {
      padding: 3px 8px;
      border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.7);
    }
    .curl-pre {
      white-space: pre;
      overflow-x: auto;
    }
    .curl-pre span.url {
      color: #93c5fd;
    }
    .muted {
      color: var(--muted);
    }
    .footer {
      margin-top: 26px;
      font-size: 11px;
      color: var(--muted);
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: space-between;
    }
    .footer span.code {
      font-family: var(--mono);
    }
  </style>
</head>
<body>
  <div class="page">
    <div class="top-row">
      <div class="logo-row">
        <div class="logo-mark">R4</div>
        <div>
          <div class="logo-text-main">RE4CTOR Gateway</div>
          <div class="logo-text-sub">Entropy → VRF → Proofs</div>
        </div>
      </div>
      <div class="top-badge">
        <span class="pill-ok">dev mode</span>
        <span>Public demo key: <span class="code">demo</span></span>
      </div>
    </div>

    <div class="chip-row">
      <span class="chip-pill">RE4CTOR SaaS API</span>
      <span class="chip-sub">30–50ms latency • 600× faster than on-chain oracles • dual-signed entropy</span>
    </div>

    <h1>FIPS-ready randomness API with verifiable proofs.</h1>
    <p class="hero-sub">
      RE4CTOR SaaS API is a hardened HTTP gateway in front of RE4CTOR Core RNG
      and dual-signature VRF (ECDSA + ML-DSA-65). One endpoint for crypto, gaming,
      and defense workloads that demand auditable entropy.
    </p>

    <div class="hero-kpi-row">
      <div class="hero-kpi"><span>20–30 ms</span> end-to-end in dev</div>
      <div class="hero-kpi"><span>NIST SP800-22</span> tested core streams</div>
      <div class="hero-kpi"><span>ML-DSA-65</span> post-quantum VRF proofs</div>
    </div>

    <div class="hero-actions">
      <button id="btn-try-api" class="btn-primary">
        <span class="icon">▶</span>
        <span>Try live API</span>
      </button>
      <button id="btn-open-docs" class="btn-ghost">
        <span class="icon">☰</span>
        <span>Open Swagger <span class="code">/docs</span></span>
      </button>
    </div>

    <div class="badge-row">
      <div class="badge-pill"><strong>Core:</strong> 256-bit entropy, mixed &amp; whitened</div>
      <div class="badge-pill"><strong>VRF:</strong> ECDSA(secp256k1) + ML-DSA-65</div>
      <div class="badge-pill"><strong>Headers:</strong> <span class="code">X-R4-*</span> expose runtime</div>
    </div>

    <div class="layout-main">
      <div>
        <div class="section-title">Live API playground</div>
        <p class="section-sub">
          Use this gateway directly from your browser. Calls go to
          <span class="muted" id="runtime-base-label">your gateway</span> and show live responses.
          Public dev key: <span class="code">demo</span>.
        </p>

        <div class="playground-panel">
          <div class="playground-header-row">
            <div class="playground-title">Gateway configuration</div>
            <div class="playground-pill">
              Base URL &middot; X-API-Key &middot; Latency
            </div>
          </div>

          <div class="playground-row">
            <input
              id="base-url-input"
              type="text"
              class="playground-input"
              value=""
              placeholder="https://api.re4ctor.com"
            />
            <input
              id="api-key-input"
              type="text"
              class="playground-input"
              style="max-width: 200px"
              value="demo"
              placeholder="API key (X-API-Key)"
            />
          </div>

          <div class="playground-row">
            <button id="btn-call-random" class="playground-btn">
              <span class="icon">🎲</span>
              <span>Call /v1/random</span>
            </button>
            <button id="btn-call-vrf" class="playground-btn secondary">
              <span class="icon">🔐</span>
              <span>Call /v1/vrf?sig=ecdsa</span>
            </button>
            <button id="btn-call-dual-full" class="playground-btn secondary">
              <span class="icon">🧬</span>
            </button>
          </div>

          <div class="playground-meta">
            <span>Latency: <span id="latency-value" class="code">—</span></span>
            <span>Core: <span class="code">/random</span></span>
            <span>VRF: <span class="code">/random_dual</span></span>
          </div>

          <div id="log-box" class="log-box">
          </div>
        </div>
      </div>

      <div>
        <div class="snapshot-card">
          <div class="snapshot-header">
            <div class="snapshot-dot"></div>
            <span>Runtime snapshot</span>
          </div>
          <div class="snapshot-sub">
            Live view into your RE4CTOR gateway. Values are returned via HTTP and <span class="code">X-R4-*</span> headers.
          </div>

          <div class="snapshot-tags">
            <div class="tag-pill tag-pill--accent">FIPS 204-ready 🔐</div>
            <div class="tag-pill tag-pill--pq">Post-quantum combo (ML-DSA-65)</div>
            <div class="tag-pill">On-chain proof friendly</div>
          </div>

          <div class="snapshot-grid">
            <div class="snapshot-box">
              <div class="snapshot-label">Latency (dev)</div>
              <div id="latency-value-2" class="snapshot-value">—</div>
              <div class="snapshot-meta">Gateway → Core</div>
            </div>
            <div class="snapshot-box">
              <div class="snapshot-label">VRF mode</div>
              <div class="snapshot-value">ECDSA + ML-DSA-65</div>
              <div class="snapshot-meta">Dual-signed</div>
            </div>
            <div class="snapshot-box">
              <div class="snapshot-label">Plan</div>
              <div class="snapshot-value">dev</div>
              <div class="snapshot-meta">X-API-Key: demo</div>
            </div>
          </div>
        </div>

        <div class="curl-card">
          <div class="curl-header">
            <span>curl examples</span>
            <span class="curl-badge">copy &amp; paste into terminal</span>
          </div>
          <div class="curl-pre">
curl -s -H "X-API-Key: demo" \\
  "<span id="curl-base-url-1" class="url">https://api.re4ctor.com</span>/v1/random?n=16&fmt=hex"

curl -s -H "X-API-Key: demo" \\
  "<span id="curl-base-url-2" class="url">https://api.re4ctor.com</span>/v1/vrf?sig=ecdsa" | jq .

curl -s -H "X-API-Key: demo" \\
          </div>
        </div>
      </div>
    </div>

    <div class="footer">
      <span>Gateway: <span class="code">FastAPI</span> • Core / VRF: <span class="code">RE4CTOR</span></span>
      <span>Check <span class="code">/v1/meta</span> and <span class="code">/v1/env_debug</span> for introspection.</span>
    </div>
  </div>

  <script>
    (function() {
      function byId(id) { return document.getElementById(id); }

      var baseInput      = byId("base-url-input");
      var apiKeyInput    = byId("api-key-input");
      var logBox         = byId("log-box");
      var latencyValue   = byId("latency-value");
      var latencyValue2  = byId("latency-value-2");
      var runtimeLabel   = byId("runtime-base-label");
      var curlBase1      = byId("curl-base-url-1");
      var curlBase2      = byId("curl-base-url-2");
      var curlBase3      = byId("curl-base-url-3");

      var origin = window.location.origin || "";

      if (baseInput && !baseInput.value) {
        baseInput.value = origin || "https://api.re4ctor.com";
      }
      if (runtimeLabel) {
        runtimeLabel.textContent = origin || "your gateway";
      }
      if (curlBase1 && origin) curlBase1.textContent = origin;
      if (curlBase2 && origin) curlBase2.textContent = origin;
      if (curlBase3 && origin) curlBase3.textContent = origin;

      function appendLog(line, cls) {
        if (!logBox) return;
        var span = document.createElement("span");
        if (cls) span.className = cls;
        span.textContent = line + "\\n";
        logBox.appendChild(span);
        logBox.scrollTop = logBox.scrollHeight;
      }

      function setLatency(ms) {
        var txt = ms + " ms";
        if (latencyValue) latencyValue.textContent = txt;
        if (latencyValue2) latencyValue2.textContent = txt;
      }

      async function callEndpoint(path) {
        var base = (baseInput && baseInput.value.trim()) || origin || "https://api.re4ctor.com";
        var key  = (apiKeyInput && apiKeyInput.value.trim()) || "demo";

        if (!base) {
          appendLog("ERROR: base URL is empty", "log-line-err");
          return;
        }
        if (!base.startsWith("http")) {
          base = "https://" + base;
        }
        var url = base.replace(/\\/$/, "") + path;

        var t0 = performance.now();
        appendLog("→ GET " + url, "log-line-muted");
        try {
          var res = await fetch(url, {
            method: "GET",
            headers: { "X-API-Key": key }
          });
          var dt = Math.round(performance.now() - t0);
          setLatency(dt);

          var text = await res.text();
          if (res.ok) {
            appendLog("← " + res.status + " OK (" + dt + " ms)", "log-line-ok");
            appendLog(text, "log-line-muted");
          } else {
            appendLog("← " + res.status + " ERROR (" + dt + " ms)", "log-line-err");
            appendLog(text, "log-line-err");
          }
        } catch (e) {
          appendLog("ERROR: " + (e && e.message ? e.message : e), "log-line-err");
        }
      }

      var btnRandom    = byId("btn-call-random");
      var btnVrf       = byId("btn-call-vrf");
      var btnDualFull  = byId("btn-call-dual-full");
      var btnTry       = byId("btn-try-api");
      var btnDocs      = byId("btn-open-docs");

      if (btnRandom) {
        btnRandom.addEventListener("click", function() {
          callEndpoint("/v1/random?n=16&fmt=hex");
        });
      }
      if (btnVrf) {
        btnVrf.addEventListener("click", function() {
          callEndpoint("/v1/vrf?sig=ecdsa");
        });
      }
      if (btnDualFull) {
        btnDualFull.addEventListener("click", function() {
        });
      }
      if (btnTry) {
        btnTry.addEventListener("click", function() {
          callEndpoint("/v1/random?n=16&fmt=hex");
        });
      }
      if (btnDocs) {
        btnDocs.addEventListener("click", function() {
          var base = (baseInput && baseInput.value.trim()) || origin || "https://api.re4ctor.com";
          if (!base.startsWith("http")) base = "https://" + base;
          window.open(base.replace(/\\/$/, "") + "/docs", "_blank");
        });
      }
    })();
  </script>
</body>
</html>
"""


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    return HTMLResponse(content=HOMEPAGE_HTML)


@app.get("/v1/health")
async def health():
    return {"ok": True}


@app.get("/v1/meta")
async def meta():
    return {
        "gateway_version": GATEWAY_VERSION,
        "core_url": CORE_URL,
        "vrf_url": VRF_URL,
    }


@app.get("/v1/env_debug")
async def env_debug():
    return {
        "CORE_URL": CORE_URL,
        "VRF_URL": VRF_URL,
        "PUBLIC_API_KEY": PUBLIC_API_KEY,
        "INTERNAL_R4_API_KEY": INTERNAL_R4_API_KEY,
        "GATEWAY_VERSION": GATEWAY_VERSION,
    }


@app.get("/v1/random")
async def random_proxy(
    n: int,
    fmt: str = "hex",
    api_key: str = Depends(require_api_key),
):
    logger.info("random_proxy_enter key_prefix=%s", str(api_key)[:6] if api_key else "none")
    upstream = f"{CORE_URL}/random_dual"
    params = {"sig": "ecdsa"}
    headers = {}
    if INTERNAL_R4_API_KEY:
        headers["X-API-Key"] = INTERNAL_R4_API_KEY
        params["key"] = INTERNAL_R4_API_KEY

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(upstream, params=params, headers=headers)
            if r.status_code >= 400:
                raise HTTPException(status_code=502, detail=f"core_upstream_status_{r.status_code}")
            return r.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"core_unreachable: {e}")
@app.get("/v1/vrf")
async def vrf_proxy(
    sig: str,
    api_key: str = Depends(require_api_key),
):
    upstream = f"{VRF_URL}/random_dual"
    params = {"sig": sig}
    headers = {"X-API-Key": INTERNAL_R4_API_KEY}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(upstream, params=params, headers=headers)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"vrf_unreachable: {e!s}")

    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type=r.headers.get("content-type", "application/json"),
    )


@app.get("/v1/random_dual")
async def random_dual_proxy(
    sig: str,
    api_key: str = Depends(require_api_key),
):
    """
    Alias до того ж бекенду, що й /v1/vrf – короткий шлях для dual-sig VRF.
    """
    upstream = f"{VRF_URL}/random_dual"
    params = {"sig": sig}
    headers = {"X-API-Key": INTERNAL_R4_API_KEY}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(upstream, params=params, headers=headers)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"vrf_unreachable: {e!s}")

    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type=r.headers.get("content-type", "application/json"),
    )

@app.post("/v1/verify")
async def verify_signature(req: VerifyRequest):
    """
    Перевірка ECDSA підпису (secp256k1) по вже готовому msg_hash (32 байти).
    msg_hash, r, s – у hex (з 0x або без), v – 0/1 або 27/28.
    expected_signer – очікувана адреса "0x..." (чутлива до checksum / ні – не важливо).
    """
    msg_hex = _clean_hex_64(req.msg_hash, "msg_hash")
    r_hex = _clean_hex_64(req.r, "r")
    s_hex = _clean_hex_64(req.s, "s")
    v_norm = _normalize_v(req.v)

    try:
        msg_bytes = binascii.unhexlify(msg_hex)
    except binascii.Error as e:
        raise HTTPException(
            status_code=400,
            detail=f"invalid msg_hash hex: {e}",
        )

    r_int = int(r_hex, 16)
    s_int = int(s_hex, 16)

    try:
        sig = keys.Signature(vrs=(v_norm, r_int, s_int))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"signature_init_failed: {type(e).__name__}: {e}",
        )

    try:
        recovered = Account.recover_hash(msg_bytes, signature=sig.to_bytes())
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"recover_failed: {type(e).__name__}: {e}",
        )

    recovered_norm = _normalize_address(recovered)
    expected_norm = _normalize_address(req.expected_signer)
    match = recovered_norm == expected_norm

    return {
        "ok": True,
        "match": match,
        "recovered": recovered,
        "expected": req.expected_signer,
        "v_used": v_norm,
    }


logger.warning("OVERRIDE_LOADED_MARKER_20260212")


# RANDOM_UPSTREAM_FALLBACK_20260212
def _try_core_random(n:int, fmt:str, api_key:str|None):
    import os, json, urllib.parse, urllib.request, urllib.error
    base_env = os.getenv("R4_CORE_URL") or os.getenv("CORE_URL") or "http://r4-core:8080"
    bases = [base_env]
    if "8080" in base_env: bases.append(base_env.replace("8080","8081"))
    if "8081" in base_env: bases.append(base_env.replace("8081","8080"))
    # unique preserve order
    seen=set(); ubases=[]
    for b in bases:
        if b not in seen:
            seen.add(b); ubases.append(b)

    paths = ["/random", "/random_dual"]
    last_err = None
    for b in ubases:
        for path in paths:
            q = urllib.parse.urlencode({"n": n, "fmt": fmt})
            u = f"{b}{path}?{q}"
            if api_key:
                u += "&" + urllib.parse.urlencode({"key": api_key})
            try:
                with urllib.request.urlopen(u, timeout=8) as r:
                    raw = r.read().decode("utf-8", "replace")
                    try:
                        return r.status, json.loads(raw)
                    except Exception:
                        return r.status, {"raw": raw}
            except Exception as e:
                last_err = f"{u} -> {e}"
                continue
    raise RuntimeError(last_err or "core upstream failed")
