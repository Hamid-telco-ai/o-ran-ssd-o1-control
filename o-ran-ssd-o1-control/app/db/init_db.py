from app.db.session import engine, SessionLocal
from app.db.models import Base, RuntimeConfigModel
from app.core.config import settings
import json

def init():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        cfg = db.query(RuntimeConfigModel).first()
        if not cfg:
            cfg = RuntimeConfigModel(
                threshold=settings.default_threshold,
                sigma_floor=settings.default_sigma_floor,
                persistence_windows=settings.default_persistence_windows,
                block_duration_sec=settings.default_block_duration_sec,
                neighbor_ta_span=settings.default_neighbor_ta_span,
                action_ladder=json.dumps([0.5, 0.8, settings.default_threshold]),
            )
            db.add(cfg)
            db.commit()

if __name__ == "__main__":
    init()
