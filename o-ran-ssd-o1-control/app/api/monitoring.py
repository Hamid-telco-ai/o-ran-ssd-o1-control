from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.db.deps import get_db
from app.db.models import AlarmModel, PolicyModel, KPIProfileModel

router = APIRouter(tags=["monitoring"])

ALARM_COUNT = Counter("ssd_xapp_alarms_total", "Total alarms generated")
POLICY_COUNT = Counter("ssd_xapp_policies_total", "Total policies generated")
PROFILE_COUNT = Gauge("ssd_xapp_profiles", "Profiles stored")

@router.get("/alarms")
def list_alarms(db: Session = Depends(get_db)):
    alarms = db.query(AlarmModel).order_by(AlarmModel.ts.desc()).limit(200).all()
    return [
        {
            "id": a.id,
            "ts": a.ts,
            "cell_id": a.cell_id,
            "ta": a.ta,
            "observed_x": a.observed_x,
            "mu": a.mu,
            "sigma": a.sigma,
            "anomaly_score": a.anomaly_score,
            "threshold": a.threshold,
            "action": a.action,
        }
        for a in alarms
    ]

@router.get("/policies")
def list_policies(db: Session = Depends(get_db)):
    policies = db.query(PolicyModel).order_by(PolicyModel.created_at.desc()).limit(200).all()
    return [
        {
            "id": p.id,
            "created_at": p.created_at,
            "cell_id": p.cell_id,
            "ta": p.ta,
            "policy_type": p.policy_type,
            "duration_sec": p.duration_sec,
            "status": p.status,
        }
        for p in policies
    ]

@router.get("/profiles/{cell_id}/{ta}")
def get_profile(cell_id: str, ta: int, db: Session = Depends(get_db)):
    profiles = db.query(KPIProfileModel).filter(KPIProfileModel.cell_id == cell_id, KPIProfileModel.ta == ta).all()
    return [
        {
            "cell_id": p.cell_id,
            "ta": p.ta,
            "time_bucket": p.time_bucket,
            "window_sec": p.window_sec,
            "mu": p.mu,
            "sigma": p.sigma,
            "samples": p.samples,
        }
        for p in profiles
    ]

@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    PROFILE_COUNT.set(db.query(KPIProfileModel).count())
    ALARM_COUNT._value.set(db.query(AlarmModel).count())
    POLICY_COUNT._value.set(db.query(PolicyModel).count())
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
