from __future__ import annotations

import json
import time

from app.services.o1_snapshot_service import O1SnapshotService


if __name__ == "__main__":
    service = O1SnapshotService()
    while True:
        snapshot = service.build_snapshot()
        print(json.dumps(snapshot, indent=2))
        time.sleep(10)
