import json
from typing import Dict, Any

SEMANTIC_FILE = r"c9hack\v1\src\v1\nrg_team_strategy_semantic.json"

def load_semantic_state() -> Dict[str, Any]:
    with open(SEMANTIC_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
