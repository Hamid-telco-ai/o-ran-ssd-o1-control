from collections import defaultdict
from datetime import datetime
import math

def bucket_index(ts: datetime, window_sec: int) -> int:
    sec_of_hour = ts.minute * 60 + ts.second
    return sec_of_hour // window_sec

def build_kpi_profiles(events, window_sec: int) -> list[dict]:
    # counts[(ta, bucket, window_start_ts)] = count
    window_counts = defaultdict(int)
    window_seen = set()

    for e in events:
        bucket = bucket_index(e.timestamp, window_sec)
        epoch = int(e.timestamp.timestamp())
        window_start = epoch - (epoch % window_sec)
        key = (e.ta, bucket, window_start)
        window_counts[key] += 1
        window_seen.add((e.ta, bucket, window_start))

    grouped = defaultdict(list)
    for (ta, bucket, _window_start), count in window_counts.items():
        grouped[(ta, bucket)].append(count)

    profiles = []
    for (ta, bucket), counts in grouped.items():
        n = len(counts)
        mu = sum(counts) / n
        if n > 1:
            var = sum((x - mu) ** 2 for x in counts) / (n - 1)
            sigma = math.sqrt(var)
        else:
            sigma = 0.0
        profiles.append({
            "ta": ta,
            "time_bucket": bucket,
            "mu": round(mu, 6),
            "sigma": round(sigma, 6),
            "samples": n,
        })
    return profiles
