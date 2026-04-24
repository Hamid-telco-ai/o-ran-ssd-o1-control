from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy import select
from app.adapters.mock_ric import MockRICAdapter
from app.db.models import KPIProfileModel
from app.services.detector import SSDDetector, bucket_index
from app.services.storage import save_alarms, save_policies
from app.services.config_service import get_config

class LiveProcessor:
    def __init__(self):
        self.started = False
        self.buffer = []
        self.adapter = MockRICAdapter()

    def start(self, db):
        if self.started:
            return False

        def handle_event(event):
            self.buffer.append(event)
            self.process(db)

        self.adapter.start_listener(handle_event)
        self.started = True
        return True

    def process(self, db):
        if not self.buffer:
            return

        by_window = defaultdict(list)
        for e in self.buffer:
            epoch = int(e.timestamp.timestamp())
            window_start = epoch - (epoch % 60)
            by_window[(e.cell_id, window_start)].append(e)

        remaining = []
        now_epoch = int(datetime.now(timezone.utc).timestamp())
        for (cell_id, window_start), events in by_window.items():
            if now_epoch - window_start < 60:
                remaining.extend(events)
                continue

            counts = defaultdict(int)
            for e in events:
                counts[e.ta] += 1

            cfg = get_config(db)
            detector = SSDDetector(
                threshold=cfg["threshold"],
                sigma_floor=cfg["sigma_floor"],
                persistence_windows=cfg["persistence_windows"],
                block_duration_sec=cfg["block_duration_sec"],
                neighbor_ta_span=cfg["neighbor_ta_span"],
                action_ladder=cfg["action_ladder"],
            )

            bucket = bucket_index(events[0].timestamp, 60)
            q = db.execute(
                select(KPIProfileModel).where(KPIProfileModel.cell_id == cell_id, KPIProfileModel.time_bucket == bucket)
            )
            profiles = q.scalars().all()
            profiles_map = {(p.ta, p.time_bucket): {"mu": p.mu, "sigma": p.sigma} for p in profiles}

            alarms, policies = detector.detect(cell_id, events[0].timestamp, dict(counts), profiles_map, 60)
            if alarms:
                save_alarms(db, alarms)
            if policies:
                save_policies(db, policies)
                for p in policies:
                    self.adapter.publish_policy(p)

        self.buffer = remaining

live_processor = LiveProcessor()
