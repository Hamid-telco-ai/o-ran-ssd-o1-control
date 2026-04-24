from __future__ import annotations

import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class O1ODLClient:
    def __init__(self) -> None:
        # --- REQUIRED CONFIG ---
        self.base_url = os.getenv("O1_ODL_BASE_URL")
        if not self.base_url:
            raise RuntimeError("O1_ODL_BASE_URL is not set in .env")

        self.base_url = self.base_url.rstrip("/")

        self.username = os.getenv("O1_ODL_USERNAME", "admin")
        self.password = os.getenv("O1_ODL_PASSWORD", "admin")

        self.topology_id = os.getenv("O1_TOPOLOGY_ID", "topology-netconf")
        self.node_id = os.getenv("O1_NODE_ID", "o-du1")

        self.timeout = int(os.getenv("O1_POLL_TIMEOUT_SEC", "20"))

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"

        resp = requests.get(
            url,
            auth=(self.username, self.password),
            headers={"Accept": "application/json"},
            timeout=self.timeout,
        )

        resp.raise_for_status()
        return resp.json()

    # --- TOPOLOGY ---
    def get_topology_nonconfig(self) -> Dict[str, Any]:
        return self._get(
            f"/rests/data/network-topology:network-topology/"
            f"topology={self.topology_id}?content=nonconfig"
        )

    # --- SYSTEM ---
    def get_system(self) -> Dict[str, Any]:
        return self._get(
            f"/rests/data/network-topology:network-topology/"
            f"topology={self.topology_id}/node={self.node_id}/"
            f"yang-ext:mount/ietf-system:system?content=nonconfig"
        )

    # --- NETCONF STATE ---
    def get_netconf_state(self) -> Dict[str, Any]:
        return self._get(
            f"/rests/data/network-topology:network-topology/"
            f"topology={self.topology_id}/node={self.node_id}/"
            f"yang-ext:mount/ietf-netconf-monitoring:netconf-state?content=nonconfig"
        )

    # --- O-RAN DU MODEL ---
    def get_du_network_function(self) -> Dict[str, Any]:
        return self._get(
            f"/rests/data/network-topology:network-topology/"
            f"topology={self.topology_id}/node={self.node_id}/"
            f"yang-ext:mount/o-ran-sc-du-hello-world:network-function?content=nonconfig"
        )

    # --- WRITE (EDIT-CONFIG via RESTCONF → NETCONF) ---
    def update_network_function_user_label(self, user_label: str) -> Dict[str, Any]:
        path = (
            f"/rests/data/network-topology:network-topology/"
            f"topology={self.topology_id}/node={self.node_id}/"
            f"yang-ext:mount/o-ran-sc-du-hello-world:network-function/user-label"
        )

        url = f"{self.base_url}{path}"

        payload = {
            "o-ran-sc-du-hello-world:user-label": user_label
        }

        resp = requests.put(
            url,
            auth=(self.username, self.password),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.timeout,
        )

        resp.raise_for_status()

        return {
            "status": "success",
            "updated_field": "network-function/user-label",
            "new_value": user_label,
            "odl_url": url,
        }