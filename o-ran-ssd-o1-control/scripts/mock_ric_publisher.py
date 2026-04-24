import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import redis
from app.core.config import settings
from app.services.traffic import generate_synthetic_events

CHANNEL = "ric:events"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", default="testbed_mixed")
    parser.add_argument("--cell", default="cell_1")
    parser.add_argument("--windows", type=int, default=10)
    parser.add_argument("--window-sec", type=int, default=60)
    parser.add_argument("--base-ta", type=int, default=77)
    args = parser.parse_args()

    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    events = generate_synthetic_events(args.preset, args.cell, args.windows, args.window_sec, args.base_ta)

    for e in events:
        r.publish(CHANNEL, e.model_dump_json())
    print(f"Published {len(events)} events to {CHANNEL}")

if __name__ == "__main__":
    main()
