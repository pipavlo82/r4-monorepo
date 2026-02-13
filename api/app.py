from fastapi import FastAPI
from api.dual_router import router as dual_router
from fastapi.responses import JSONResponse
import time

# Узгоджений мінімальний додаток FastAPI
app = FastAPI(
    title="Re4ctoR — Entropy & VRF API",
    description=(
        "ECDSA(secp256k1) і PQ ML-DSA-65 (Dilithium3) підтримка (PQ може бути вимкнена).\n"
        "Endpoints:\n"
        " - GET /health\n"
        " - GET /random_pq?sig=ecdsa|pq\n"
        " - GET /random_dual\n"
    ),
    version="1.0.0",
)

# Підключаємо роутер з /random_pq та /random_dual
app.include_router(dual_router)

@app.get("/health")
def health():
    return {"ok": True, "ts": int(time.time())}

@app.get("/version")
def version():
    return {"name": "re4ctor-api", "version": "1.0.0", "status": "running"}
