from fastapi import FastAPI
from api.dual_router import router as dual_router

app = FastAPI(title="Re4ctoR VRF (temp)")
app.include_router(dual_router)

@app.get("/healthz")
def healthz():
    return {"ok": True}
