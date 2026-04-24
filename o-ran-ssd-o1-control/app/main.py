from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.db.init_db import init
from app.api.train import router as train_router
from app.api.infer import router as infer_router
from app.api.policy import router as config_router
from app.api.monitoring import router as monitoring_router
from app.api.live import router as live_router
from app.api.o1 import router as o1_router

init()

app = FastAPI(title="SSD-xApp for srsRAN + Open5GS + Mocked RIC Adapter")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(train_router)
app.include_router(infer_router)
app.include_router(config_router)
app.include_router(monitoring_router)
app.include_router(live_router)
app.include_router(ingest_router)
app.include_router(o1_router, prefix="/o1", tags=["o1"])
