from app.services.o1_snapshot_service import O1SnapshotService, extract_radio_context
from app.adapters.o1_odl_client import O1ODLClient


class O1EnrichmentService:
    def __init__(self):
        self.client = O1ODLClient()
        self.snapshot_service = O1SnapshotService(self.client)

    def enrich(self, ssd_output: dict) -> dict:
        snapshot = self.snapshot_service.build_snapshot()
        context = extract_radio_context(snapshot)

        return {
            **ssd_output,
            "o1_context": context
        }