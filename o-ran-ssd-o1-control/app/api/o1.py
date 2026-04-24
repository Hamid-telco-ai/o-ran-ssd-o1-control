from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.adapters.o1_odl_client import O1ODLClient
from app.services.o1_snapshot_service import O1SnapshotService

router = APIRouter()
client = O1ODLClient()
service = O1SnapshotService(client)


@router.get("/topology")
def get_topology():
    try:
        return client.get_topology_nonconfig()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"O1 topology read failed: {exc}") from exc


@router.get("/system")
def get_system():
    try:
        return client.get_system()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"O1 system read failed: {exc}") from exc


@router.get("/netconf-state")
def get_netconf_state():
    try:
        return client.get_netconf_state()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"O1 netconf-state read failed: {exc}") from exc


@router.get("/du-model")
def get_du_model():
    try:
        return client.get_du_network_function()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"O1 DU model read failed: {exc}") from exc


@router.get("/snapshot")
def get_snapshot():
    try:
        return service.build_snapshot()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"O1 snapshot build failed: {exc}") from exc


# REAL O1 CONTROL ENDPOINT
@router.post("/control/user-label")
def update_user_label(user_label: str = "nf1-controlled-by-ssd-xapp"):
    try:
        return client.update_network_function_user_label(user_label)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"O1 control failed: {exc}") from exc