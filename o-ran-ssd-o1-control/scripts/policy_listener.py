import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import redis
from app.core.config import settings

CHANNEL = "ric:policy"

def main():
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe(CHANNEL)
    print(f"Listening on {CHANNEL} ...")
    for msg in pubsub.listen():
        if msg["type"] == "message":
            print(msg["data"])

if __name__ == "__main__":
    main()
