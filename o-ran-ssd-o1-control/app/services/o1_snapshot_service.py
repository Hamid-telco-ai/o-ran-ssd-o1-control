from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.adapters.o1_odl_client import O1ODLClient


class O1SnapshotService:
    def __init__(self, client: Optional[O1ODLClient] = None) -> None:
        self.client = client or O1ODLClient()

    def build_snapshot(self) -> Dict[str, Any]:
        topology = self.client.get_topology_nonconfig()
        system = self.client.get_system().get("ietf-system:system", {})
        netconf_state = self.client.get_netconf_state().get(
            "ietf-netconf-monitoring:netconf-state", {}
        )
        du_model = self.client.get_du_network_function().get(
            "o-ran-sc-du-hello-world:network-function", {}
        )

        du_context = extract_radio_context_from_du_model(du_model)

        return {
            "snapshot_ts": datetime.now(timezone.utc).isoformat(),
            "topology": topology,
            "system": system,
            "netconf_state": {
                "session_count": netconf_state.get("statistics", {}).get("in-sessions"),
                "rpc_count": netconf_state.get("statistics", {}).get("in-rpcs"),
                "capability_count": len(
                    netconf_state.get("capabilities", {}).get("capability", [])
                ),
            },
            "du_context": du_context,
        }


def extract_radio_context(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract normalized DU/cell context from a full O1 snapshot.
    Use this for enriching SSD outputs.
    """
    return snapshot.get("du_context", {"o1_context": "unavailable"})


def extract_radio_context_from_du_model(du_model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract normalized DU/cell context from the O-RAN DU model.
    """
    try:
        du_list = du_model.get("distributed-unit-functions", [])
        du = du_list[0] if du_list else {}

        cells = du.get("cell", [])
        cell = cells[0] if cells else {}

        arfcn = cell.get("absolute-radio-frequency-channel-number", {})
        bw = cell.get("base-station-channel-bandwidth", {})

        return {
            "network_function_id": du_model.get("id"),
            "du_id": du.get("id"),
            "du_user_label": du.get("user-label"),
            "cell_id": cell.get("id"),
            "pci": cell.get("physical-cell-id"),
            "tac": cell.get("tracking-area-code"),
            "dl_arfcn": arfcn.get("downlink"),
            "ul_arfcn": arfcn.get("uplink"),
            "sul_arfcn": arfcn.get("supplementary-uplink"),
            "dl_bw": bw.get("downlink"),
            "ul_bw": bw.get("uplink"),
            "sul_bw": bw.get("supplementary-uplink"),
            "traffic_state": cell.get("traffic-state"),
            "operational_state": cell.get("operational-state"),
        }

    except Exception:
        return {"o1_context": "unavailable"}