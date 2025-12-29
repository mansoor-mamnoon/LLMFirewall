from __future__ import annotations

import json
import time
import uuid
from pathlib import Path


def new_run_id() -> str:
    # short unique ID that's human-readable
    return uuid.uuid4().hex[:12]


class TranscriptLogger:
    def __init__(self, run_id: str, base_dir: str = "runs") -> None:
        self.run_id = run_id
        self.path = Path(base_dir) / f"{run_id}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: str, payload: dict) -> None:
        """
        New schema:
        {"event": "...", "ts_ms": <int>, "run_id": "...", ...payload fields...}

        Also includes old fields for backward compatibility:
        {"event_type": "...", "payload": {...}}
        """

        ts_ms = int(time.time() * 1000)

        # New flat schema
        rec: dict = {"event": event, "ts_ms": ts_ms, "run_id": self.run_id}
        if isinstance(payload, dict):
            # merge payload at top-level for easy grepping
            rec.update(payload)

        # Back-compat (optional, but helps if other code expects it)
        rec["event_type"] = event
        rec["payload"] = payload

        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
