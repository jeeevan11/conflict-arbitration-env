"""
Save before/after episodes to disk for comparison.
"""
import json
import os
from datetime import datetime


def log_transcript(
    episode: dict,
    decision: dict,
    result: dict,
    label: str,
    out_dir: str = "./transcripts"
) -> str:
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{label}_{timestamp}.json"
    path = os.path.join(out_dir, filename)
    payload = {
        "label": label,
        "timestamp": timestamp,
        "episode": episode,
        "decision": decision,
        "result": result,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    return path


def load_transcript(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)
