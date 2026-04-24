from datetime import datetime, timedelta, timezone
import random
from app.core.schemas import RAREvent

def _ensure_start(start_time):
    return start_time or datetime.now(timezone.utc).replace(second=0, microsecond=0)

def generate_synthetic_events(preset: str, cell_id: str, windows: int, window_sec: int, base_ta: int, seed: int = 42, start_time=None):
    rng = random.Random(seed)
    start = _ensure_start(start_time)
    events = []

    for w in range(windows):
        window_start = start + timedelta(seconds=w * window_sec)

        if preset == "testbed_clean":
            count = 3
            tas = [base_ta, base_ta, base_ta + rng.choice([-1, 0, 1])]
            offsets = [5, 20, 40]
        elif preset == "testbed_attack":
            count = 12
            tas = [base_ta] * count
            offsets = [min(i * 2, window_sec - 1) for i in range(count)]
        elif preset == "testbed_mixed":
            count = 3
            tas = [base_ta, base_ta + rng.choice([-1, 0, 1]), base_ta]
            offsets = [5, 20, 40]
            if w % 4 == 0:
                attack_count = 12
                for i in range(attack_count):
                    events.append(RAREvent(
                        timestamp=window_start + timedelta(seconds=min(i * 2, window_sec - 1)),
                        cell_id=cell_id,
                        ta=base_ta,
                        ue_temp_id=f"att_{w}_{i}",
                    ))
        elif preset == "simulation_clean":
            # mimic lighter periodic + daytime randomness
            count = max(1, int(rng.expovariate(1/5)))
            tas = [base_ta + rng.choice([-2, -1, 0, 1, 2]) for _ in range(count)]
            offsets = sorted(rng.randint(0, window_sec - 1) for _ in range(count))
        elif preset == "simulation_attack":
            count = 100
            tas = [base_ta] * count
            offsets = [int(i * (5 / max(count,1))) for i in range(count)]
            offsets = [min(x, window_sec - 1) for x in offsets]
        elif preset == "simulation_mixed":
            clean_count = max(1, int(rng.expovariate(1/5)))
            tas = [base_ta + rng.choice([-2, -1, 0, 1, 2]) for _ in range(clean_count)]
            offsets = sorted(rng.randint(0, window_sec - 1) for _ in range(clean_count))
            if w % 6 == 0:
                for i in range(100):
                    events.append(RAREvent(
                        timestamp=window_start + timedelta(seconds=min(int(i * (5 / 100)), window_sec - 1)),
                        cell_id=cell_id,
                        ta=base_ta,
                        ue_temp_id=f"sim_att_{w}_{i}",
                    ))
        else:
            raise ValueError(f"Unknown preset: {preset}")

        for i in range(count):
            events.append(RAREvent(
                timestamp=window_start + timedelta(seconds=offsets[i]),
                cell_id=cell_id,
                ta=tas[i],
                ue_temp_id=f"ue_{w}_{i}",
            ))

    return sorted(events, key=lambda e: e.timestamp)
