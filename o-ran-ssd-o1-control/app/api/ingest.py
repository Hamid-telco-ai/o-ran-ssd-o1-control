from datetime import datetime
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import RAREventModel
from app.db.session import get_db

router = APIRouter()


class IngestEvent(BaseModel):
    timestamp: datetime
    cell_id: str = "cell_1"
    event_type: Literal[
        "cell_selected",
        "initial_registration",
        "rrc_setup_request",
        "rrc_connected",
        "registration_failed",
        "registration_rejected",
        "registration_success",
    ]
    ta: int
    ue_temp_id: Optional[str] = None
    request_type: Optional[str] = None
    result: Optional[str] = None


class IngestBatch(BaseModel):
    events: List[IngestEvent]


@router.post("/events/ingest")
def ingest_events(payload: IngestBatch, db: Session = Depends(get_db)):
    written = 0

    for ev in payload.events:
        row = RAREventModel(
            ts=ev.timestamp,
            cell_id=ev.cell_id,
            ta=ev.ta,
            ue_temp_id=ev.ue_temp_id,
            request_type=ev.request_type,
            result=ev.result,
            event_type=ev.event_type,
        )
        db.add(row)
        written += 1

    db.commit()
    return {"status": "ok", "events_written": written}