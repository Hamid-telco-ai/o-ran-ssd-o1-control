from datetime import datetime
from sqlalchemy import delete
from app.db.models import RAREventModel, KPIProfileModel, AlarmModel, PolicyModel

def save_events(db, events):
    db.add_all([
        RAREventModel(
            ts=e.timestamp,
            cell_id=e.cell_id,
            ta=e.ta,
            ue_temp_id=e.ue_temp_id,
            request_type=e.request_type,
            result=e.result,
            event_type=e.event_type,
        )
        for e in events
    ])
    db.commit()

def replace_profiles(db, cell_id: str, window_sec: int, profiles: list[dict]):
    db.execute(delete(KPIProfileModel).where(KPIProfileModel.cell_id == cell_id))
    db.add_all([
        KPIProfileModel(
            cell_id=cell_id,
            ta=p["ta"],
            time_bucket=p["time_bucket"],
            window_sec=window_sec,
            mu=p["mu"],
            sigma=p["sigma"],
            samples=p["samples"],
            updated_at=datetime.utcnow(),
        )
        for p in profiles
    ])
    db.commit()

def save_alarms(db, alarms: list[dict]):
    db.add_all([
        AlarmModel(
            ts=a["ts"],
            cell_id=a["cell_id"],
            ta=a["ta"],
            observed_x=a["observed_x"],
            mu=a["mu"],
            sigma=a["sigma"],
            anomaly_score=a["anomaly_score"],
            threshold=a["threshold"],
            action=a["action"],
        )
        for a in alarms
    ])
    db.commit()

def save_policies(db, policies: list[dict]):
    db.add_all([
        PolicyModel(
            created_at=p["created_at"],
            cell_id=p["cell_id"],
            ta=p["ta"],
            policy_type=p["policy_type"],
            duration_sec=p["duration_sec"],
            status=p["status"],
        )
        for p in policies
    ])
    db.commit()
