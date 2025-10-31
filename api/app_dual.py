from fastapi import FastAPI
from .dual_router import router as dual_router

app = FastAPI(title="R4 VRF Dual (clean)")
app.include_router(dual_router)
