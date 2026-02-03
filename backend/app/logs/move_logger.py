import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "game_moves.log"


def log_move(data: dict):
    """
    Append a fully structured move log as JSONL.
    One line = one move.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
