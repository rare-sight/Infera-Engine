import json
import os
from datetime import datetime
from typing import Optional

MEMORY_DIR = "memory"
os.makedirs(MEMORY_DIR, exist_ok=True)


def _path(topic: str) -> str:
    safe = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in topic).strip()[:80]
    return os.path.join(MEMORY_DIR, f"{safe}.json")


def save_run(topic: str, result: dict) -> str:
    data = {
        "topic": topic,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "analysis": result.get("analysis", ""),
        "research": result.get("research", ""),
        "uncertainties": result.get("uncertainties", ""),
        "scenarios_text": result.get("scenarios_text", ""),
        "structured_scenarios": result.get("structured_scenarios"),
    }
    path = _path(topic)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def load_run(topic: str) -> Optional[dict]:
    path = _path(topic)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_saved_topics() -> list[str]:
    files = [f for f in os.listdir(MEMORY_DIR) if f.endswith(".json")]
    topics = []
    for f in files:
        try:
            with open(os.path.join(MEMORY_DIR, f), "r", encoding="utf-8") as fh:
                data = json.load(fh)
                topics.append(data.get("topic", f.replace(".json", "")))
        except Exception:
            continue
    return sorted(set(topics))