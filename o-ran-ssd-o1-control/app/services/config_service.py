import json
from app.db.models import RuntimeConfigModel

def get_config(db) -> dict:
    cfg = db.query(RuntimeConfigModel).first()
    return {
        "threshold": cfg.threshold,
        "sigma_floor": cfg.sigma_floor,
        "persistence_windows": cfg.persistence_windows,
        "block_duration_sec": cfg.block_duration_sec,
        "neighbor_ta_span": cfg.neighbor_ta_span,
        "action_ladder": json.loads(cfg.action_ladder),
    }

def update_config(db, payload: dict) -> dict:
    cfg = db.query(RuntimeConfigModel).first()
    for key, value in payload.items():
        if value is None:
            continue
        if key == "action_ladder":
            setattr(cfg, key, json.dumps(value))
        else:
            setattr(cfg, key, value)
    db.commit()
    db.refresh(cfg)
    return get_config(db)
