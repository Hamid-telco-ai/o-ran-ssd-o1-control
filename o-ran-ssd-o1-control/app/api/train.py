from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.schemas import SyntheticRequest, TrainResponse
from app.db.deps import get_db
from app.services.traffic import generate_synthetic_events
from app.services.storage import save_events, replace_profiles
from app.services.profile_builder import build_kpi_profiles

router = APIRouter(prefix="/train", tags=["train"])

@router.post("/synthetic", response_model=TrainResponse)
def train_synthetic(req: SyntheticRequest, db: Session = Depends(get_db)):
    events = generate_synthetic_events(
        preset=req.preset,
        cell_id=req.cell_id,
        windows=req.windows,
        window_sec=req.window_sec,
        base_ta=req.base_ta,
        seed=req.seed,
        start_time=req.start_time,
    )
    save_events(db, events)
    profiles = build_kpi_profiles(events, req.window_sec)
    replace_profiles(db, req.cell_id, req.window_sec, profiles)
    return TrainResponse(windows_processed=req.windows, profiles_written=len(profiles))
