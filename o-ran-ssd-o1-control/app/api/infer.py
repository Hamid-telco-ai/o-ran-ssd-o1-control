from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.models import KPIProfileModel, RAREventModel
from app.services.config_service import get_config
from app.services.detector import SSDDetector, bucket_index
from app.services.o1_enrichment_service import O1EnrichmentService
from app.services.storage import save_alarms, save_policies

router = APIRouter(prefix="/infer", tags=["infer"])

o1_service = O1EnrichmentService()


@router.post("/ingested")
def infer_ingested(
    cell_id: str = "cell_1",
    window_sec: int = 60,
    lookback_minutes: int = 10,
    db: Session = Depends(get_db),
):
    q = db.execute(
        select(RAREventModel)
        .where(RAREventModel.cell_id == cell_id)
        .order_by(RAREventModel.ts.desc())
        .limit(200)
    )
    rows = list(reversed(q.scalars().all()))

    if not rows:
        base_result = {
            "windows_processed": 0,
            "alarms": 0,
            "policies": 0,
            "closed_loop_control": {
                "triggered": False,
                "reason": "no ingested events",
            },
        }
        return o1_service.enrich(base_result)

    cfg = get_config(db)
    detector = SSDDetector(
        threshold=cfg["threshold"],
        sigma_floor=cfg["sigma_floor"],
        persistence_windows=cfg["persistence_windows"],
        block_duration_sec=cfg["block_duration_sec"],
        neighbor_ta_span=cfg["neighbor_ta_span"],
        action_ladder=cfg["action_ladder"],
    )

    grouped = defaultdict(list)
    for e in rows:
        epoch = int(e.ts.timestamp())
        window_start = epoch - (epoch % window_sec)
        grouped[window_start].append(e)

    total_alarms = 0
    total_policies = 0
    alarm_actions = []

    for _, w_events in grouped.items():
        counts = defaultdict(int)

        for e in w_events:
            if e.event_type in {
                "initial_registration",
                "rrc_setup_request",
                "registration_failed",
                "registration_rejected",
            }:
                counts[e.ta] += 1

        if not counts:
            continue

        bucket = bucket_index(w_events[0].ts, window_sec)
        q = db.execute(
            select(KPIProfileModel).where(
                KPIProfileModel.cell_id == cell_id,
                KPIProfileModel.time_bucket == bucket,
            )
        )
        profiles = q.scalars().all()
        profiles_map = {
            (p.ta, p.time_bucket): {"mu": p.mu, "sigma": p.sigma}
            for p in profiles
        }

        alarms, policies = detector.detect(
            cell_id,
            w_events[0].ts,
            dict(counts),
            profiles_map,
            window_sec,
        )

        if alarms:
            save_alarms(db, alarms)
            total_alarms += len(alarms)
            alarm_actions.extend(
                {
                    "ta": alarm.get("ta"),
                    "action": alarm.get("action"),
                    "anomaly_score": alarm.get("anomaly_score"),
                    "observed_x": alarm.get("observed_x"),
                    "mu": alarm.get("mu"),
                    "sigma": alarm.get("sigma"),
                }
                for alarm in alarms
            )

        if policies:
            save_policies(db, policies)
            total_policies += len(policies)

    closed_loop_control = {
        "triggered": False,
        "reason": "no alarms detected",
    }

    if total_alarms > 0:
        control_label = (
            "ssd-alarm-controlled-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        )

        try:
            control_result = o1_service.client.update_network_function_user_label(
                control_label
            )

            closed_loop_control = {
                "triggered": True,
                "mode": "real_o1_edit_config",
                "control_action": "update_network_function_user_label",
                "new_user_label": control_label,
                "alarm_actions": alarm_actions,
                "result": control_result,
            }

        except Exception as exc:
            closed_loop_control = {
                "triggered": True,
                "mode": "real_o1_edit_config",
                "control_action": "update_network_function_user_label",
                "status": "failed",
                "error": str(exc),
                "alarm_actions": alarm_actions,
            }

    base_result = {
        "windows_processed": len(grouped),
        "alarms": total_alarms,
        "policies": total_policies,
        "closed_loop_control": closed_loop_control,
    }

    return o1_service.enrich(base_result)