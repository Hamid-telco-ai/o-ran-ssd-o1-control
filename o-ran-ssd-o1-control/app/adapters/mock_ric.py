import json
import threading
import redis
from app.core.config import settings
from app.core.schemas import RAREvent

EVENT_CHANNEL = "ric:events"
POLICY_CHANNEL = "ric:policy"

class MockRICAdapter:
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    def publish_policy(self, policy: dict):
        self.redis.publish(POLICY_CHANNEL, json.dumps(policy))

    def start_listener(self, handler):
        def _run():
            pubsub = self.redis.pubsub()
            pubsub.subscribe(EVENT_CHANNEL)
            for msg in pubsub.listen():
                if msg["type"] != "message":
                    continue
                payload = json.loads(msg["data"])
                event = RAREvent(**payload)
                handler(event)
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return t
