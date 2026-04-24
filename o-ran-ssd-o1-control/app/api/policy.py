from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import RuntimeConfigModel
import json

router = APIRouter()

# -------------------------------
# GET /config
# -------------------------------
@router.get("/config")
def read_config(db: Session = Depends(get_db)):
    config = db.query(RuntimeConfigModel).first()

    if not config:
        return {"error": "No config found"}

    # Convert action_ladder string → list
    try:
        action_ladder = json.loads(config.action_ladder)
    except:
        action_ladder = config.action_ladder

    return {
        "threshold": config.threshold,
        "sigma_floor": config.sigma_floor,
        "persistence_windows": config.persistence_windows,
        "block_duration_sec": config.block_duration_sec,
        "neighbor_ta_span": config.neighbor_ta_span,
        "action_ladder": action_ladder,
    }

# -------------------------------
# POST /config
# -------------------------------
@router.post("/config")
def update_config(payload: dict, db: Session = Depends(get_db)):
    config = db.query(RuntimeConfigModel).first()

    if not config:
        config = RuntimeConfigModel(
            threshold=1.0,
            sigma_floor=0.5,
            persistence_windows=2,
            block_duration_sec=300,
            neighbor_ta_span=1,
            action_ladder=json.dumps([0.5, 0.8, 1.0])
        )
        db.add(config)
        db.commit()
        db.refresh(config)

    # Update only provided fields
    if "threshold" in payload:
        config.threshold = payload["threshold"]

    if "sigma_floor" in payload:
        config.sigma_floor = payload["sigma_floor"]

    if "persistence_windows" in payload:
        config.persistence_windows = payload["persistence_windows"]

    if "block_duration_sec" in payload:
        config.block_duration_sec = payload["block_duration_sec"]

    if "neighbor_ta_span" in payload:
        config.neighbor_ta_span = payload["neighbor_ta_span"]

    if "action_ladder" in payload:
        config.action_ladder = json.dumps(payload["action_ladder"])

    db.commit()

    return {
        "status": "updated",
        "config": {
            "threshold": config.threshold,
            "sigma_floor": config.sigma_floor,
            "persistence_windows": config.persistence_windows,
            "block_duration_sec": config.block_duration_sec,
            "neighbor_ta_span": config.neighbor_ta_span,
            "action_ladder": payload.get("action_ladder", [])
        }
    }