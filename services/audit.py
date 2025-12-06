# services/audit.py
import json
from pathlib import Path
import pandas as pd
from io import BytesIO

DECISION_PATH = Path("outputs/decision_traces.jsonl")
MANUAL_PATH = Path("outputs/manual_review.jsonl")

def _read_jsonl(path: Path):
    if not path.exists():
        return []
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                # skip malformed lines
                continue
    return items

def _append_jsonl(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def read_traces(limit=None):
    items = _read_jsonl(DECISION_PATH)
    if limit:
        return items[-limit:]
    return items

def read_manual_queue(limit=None):
    items = _read_jsonl(MANUAL_PATH)
    if limit:
        return items[-limit:]
    return items

def append_trace(trace_obj):
    """Append to main decision traces audit log."""
    _append_jsonl(DECISION_PATH, trace_obj)

def queue_manual_review(trace_obj):
    """Append a trace to manual review queue."""
    _append_jsonl(MANUAL_PATH, trace_obj)

def remove_manual_item(match_fn):
    """
    Remove manual review items matching predicate match_fn(trace) -> True.
    match_fn must accept a trace dict and return boolean.
    """
    items = _read_jsonl(MANUAL_PATH)
    kept = [t for t in items if not match_fn(t)]
    # overwrite file
    MANUAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANUAL_PATH.open("w", encoding="utf-8") as f:
        for t in kept:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

def traces_to_csv_bytes(traces):
    """Convert list of trace dicts to CSV bytes for download."""
    rows = []
    for t in traces:
        d = t.get("decision_details", {})
        a = t.get("applicant", {})
        rows.append({
            "timestamp": d.get("timestamp"),
            "applicant_id": a.get("id"),
            "applicant_name": a.get("name"),
            "decision": d.get("final_decision"),
            "requested_amount": d.get("requested_amount"),
            "EMI": d.get("EMI"),
            "EMI_pct_salary": d.get("EMI_pct_salary"),
            "rules_fired": " | ".join(d.get("rules_fired", []))
        })
    if not rows:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(rows)
    bio = BytesIO()
    df.to_csv(bio, index=False)
    bio.seek(0)
    return bio.getvalue()
