import argparse
import json
import os
import re
import time
from datetime import datetime
from typing import Optional

import requests


TIMESTAMP_RE = re.compile(r"^\[(?P<ts>[\d\-:\.\s]+)\]")
TAC_RE = re.compile(r"tac\[(?P<tac>\d+)\]")
CAUSE_RE = re.compile(r"Initial Registration failed \[(?P<cause>[A-Z0-9_]+)\]")


def parse_ts(line: str) -> Optional[datetime]:
    m = TIMESTAMP_RE.search(line)
    if not m:
        return None
    raw = m.group("ts")
    return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S.%f")


def build_event(line: str, pseudo_ta: int, ue_id: str, cell_id: str):
    ts = parse_ts(line)
    if ts is None:
        return None

    base = {
        "timestamp": ts.isoformat(),
        "cell_id": cell_id,
        "ta": pseudo_ta,
        "ue_temp_id": ue_id,
        "request_type": "initial_registration",
        "result": "observed",
    }

    if "Selected cell" in line:
        tac_match = TAC_RE.search(line)
        tac = tac_match.group("tac") if tac_match else "unknown"
        return {
            **base,
            "event_type": "cell_selected",
            "result": f"tac_{tac}",
        }

    if "Sending Initial Registration" in line:
        return {
            **base,
            "event_type": "initial_registration",
        }

    if "Sending RRC Setup Request" in line:
        return {
            **base,
            "event_type": "rrc_setup_request",
        }

    if "RRC connection established" in line:
        return {
            **base,
            "event_type": "rrc_connected",
        }

    if "Initial Registration failed" in line:
        cause_match = CAUSE_RE.search(line)
        cause = cause_match.group("cause") if cause_match else "unknown"
        return {
            **base,
            "event_type": "registration_failed",
            "result": cause,
        }

    if "Registration accept" in line or "Registration completed" in line:
        return {
            **base,
            "event_type": "registration_success",
            "result": "success",
        }

    return None


def post_event(api_url: str, event: dict, timeout: float = 5.0):
    payload = {"events": [event]}
    r = requests.post(api_url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def follow_file(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            yield line.rstrip("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-file", required=True, help="Path to ue.log")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000/events/ingest")
    parser.add_argument("--pseudo-ta", type=int, default=77)
    parser.add_argument("--ue-id", default="imsi-001010000000001")
    parser.add_argument("--cell-id", default="cell_1")
    parser.add_argument("--print-only", action="store_true")
    args = parser.parse_args()

    print(f"Watching {args.log_file}")
    print(f"Pseudo-TA={args.pseudo_ta}, UE-ID={args.ue_id}")

    for line in follow_file(args.log_file):
        event = build_event(line, args.pseudo_ta, args.ue_id, args.cell_id)
        if event is None:
            continue

        print(json.dumps(event, indent=2))

        if args.print_only:
            continue

        try:
            resp = post_event(args.api_url, event)
            print(f"Ingested: {resp}")
        except Exception as exc:
            print(f"POST failed: {exc}")


if __name__ == "__main__":
    main()