from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services.live_service import live_processor

router = APIRouter(prefix="/live", tags=["live"])

@router.post("/start")
def start_live(db: Session = Depends(get_db)):
    started = live_processor.start(db)
    return {"started": started}
