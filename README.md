# O-RAN SSD Closed-Loop xApp

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![O-RAN](https://img.shields.io/badge/O--RAN-O1%20Interface-orange)
![Status](https://img.shields.io/badge/Status-Closed--Loop%20Working-success)

Signaling Storm Detection (SSD) xApp with O-RAN O1-based closed-loop control using OpenDaylight (SMO), NETCONF, and a simulated O-DU.

<img width="1342" height="782" alt="Screenshot 2026-04-24 132401" src="https://github.com/user-attachments/assets/355540fc-2976-4fd8-b4da-0c57d3a2918a" />


---

## Overview

This project implements a closed-loop control system:

Traffic Events → SSD Detection → Alarm → O1 Control → DU Update

It demonstrates how O-RAN SMO (OpenDaylight) can be used to:

- Monitor network state via O1 (NETCONF/YANG)
- Detect signaling storms using statistical modeling
- Trigger automated control actions via edit-config

---

## Procedure

- Signaling Storm Detection (SSD)
  - Z-score anomaly detection using (μ, σ)
  - Time-bucketed KPI modeling
  - TA-level granularity

- Closed-loop Control
  - Alarm-triggered O1 actions
  - Real NETCONF edit-config via OpenDaylight

- O-RAN O1 Integration
  - Topology discovery
  - DU system + NETCONF state
  - O-RAN DU YANG model parsing

- FastAPI Backend
  - Modular services (detector, O1 client, enrichment)
  - REST APIs for inference, monitoring, and control

---

 ## Algorithm
1. Events generated (simulated traffic)

2. FastAPI:
   → SSD detects anomaly

3. Decision:
   → Alarm triggered

4. FastAPI:
   → RESTCONF request to ODL (OpenDaylight)

5. OpenDaylight:
   → converts to NETCONF edit-config

6. O-DU:
   → applies configuration change

7. FastAPI:
   → reads updated state via O1

8. System confirms action

---

## High-Level Architecture

            +----------------------+
            |   FastAPI xApp       |
            |----------------------|
            | SSD Detector         |
            | O1 Enrichment        |
            | Control Logic        |
            +----------+-----------+
                       |
                       | RESTCONF
                       ▼
            +----------------------+
            | OpenDaylight (SMO)   |
            +----------+-----------+
                       |
                       | NETCONF (O1)
                       ▼
            +----------------------+
            | O-DU Simulator       |
            +----------------------+  
---

## Detection Logic

score = (observed - μ) / σ

Action determined by:

action_ladder = [alert, rate_limit, reject]

---

## Example

Observed = 20  
μ = 2  
σ = 1  

score = 18 → reject  

---

## Setup

### 1. Start O-DU Simulator

```bash
docker compose up -d ntsim-ng ntsim-ng-o-du
```

### 2. Start OpenDaylight (SMO)

```bash
Ensure RESTCONF is accessible:
```
http://<ODL_IP>:8181


---

### 3. Configure `.env`

```env
O1_ODL_BASE_URL=http://<ODL_IP>:8181
O1_ODL_USERNAME=admin
O1_ODL_PASSWORD=admin
O1_NODE_ID=o-du1
```

### 4. Start FastAPI

```bash
python -m uvicorn app.main:app --reload
```

---

## APIs

### O1 Data

```bash
GET /o1/topology
GET /o1/system
GET /o1/netconf-state
GET /o1/du-model
GET /o1/snapshot
```
### SSD Inference

```bash
POST /infer/ingested
```
### O1 Control

```bash
POST /o1/control/user-label
```

## Example Output

```bash
{
  "windows_processed": 1,
  "alarms": 1,
  "closed_loop_control": {
    "triggered": true,
    "mode": "real_o1_edit_config"
  },
  "o1_context": {
    "du_id": "O-DU-1211",
    "pci": 1,
    "tac": 10
  }
}
```

## How to Run

### Local

```bash
- python -m venv .venv
- .venv\Scripts\activate
- pip install -r requirements.txt
- python -m uvicorn app.main:app --reload
```

### Docker

```bash
- docker build -t o-ran-ssd-xapp .
- docker run -p 8000:8000 -e O1_ODL_BASE_URL=http://<ODL_IP>:8181 o-ran-ssd-xapp

```
## References

  - **O-RAN SC O1 Interface Simulator**  
  Used to emulate a NETCONF-enabled O-DU and validate O1 interactions.  
  https://docs.o-ran-sc.org/projects/o-ran-sc-sim-o1-interface/en/latest/overview.html

- **OpenDaylight (ODL)**  
  Open-source SDN controller used as a lightweight SMO-like platform to expose RESTCONF APIs and perform NETCONF-based O1 control.  
  https://github.com/opendaylight



