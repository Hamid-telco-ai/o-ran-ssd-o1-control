import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from collections import defaultdict
import csv
from datetime import datetime, timezone
from app.services.traffic import generate_synthetic_events
from app.services.profile_builder import build_kpi_profiles
from app.services.detector import SSDDetector, bucket_index

def evaluate(thresholds=(0.5, 0.8, 1.0, 1.5, 2.0), out_csv="artifacts/evaluation.csv"):
    Path("artifacts").mkdir(exist_ok=True)

    train_events = generate_synthetic_events("testbed_clean", "cell_1", 60, 60, 77, start_time=datetime.now(timezone.utc))
    profiles = build_kpi_profiles(train_events, 60)
    profiles_map_all = {(p["ta"], p["time_bucket"]): {"mu": p["mu"], "sigma": p["sigma"]} for p in profiles}

    rows = []
    for thr in thresholds:
        detector = SSDDetector(
            threshold=thr,
            sigma_floor=0.5,
            persistence_windows=2,
            block_duration_sec=300,
            neighbor_ta_span=1,
            action_ladder=[thr*0.5, thr*0.8, thr],
        )

        mixed = generate_synthetic_events("testbed_mixed", "cell_1", 30, 60, 77, start_time=datetime.now(timezone.utc))
        grouped = defaultdict(list)
        for e in mixed:
            epoch = int(e.timestamp.timestamp())
            window_start = epoch - (epoch % 60)
            grouped[window_start].append(e)

        alarms = 0
        rejects = 0
        for _, events in grouped.items():
            counts = defaultdict(int)
            for e in events:
                counts[e.ta] += 1
            bucket = bucket_index(events[0].timestamp, 60)
            profiles_map = {(ta, b): v for (ta, b), v in profiles_map_all.items() if b == bucket}
            a, p = detector.detect("cell_1", events[0].timestamp, dict(counts), profiles_map, 60)
            alarms += len(a)
            rejects += sum(1 for x in p if x["policy_type"] == "reject")
        rows.append({"threshold": thr, "alarms": alarms, "rejects": rejects})

    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["threshold", "alarms", "rejects"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out_csv}")

if __name__ == "__main__":
    evaluate()
