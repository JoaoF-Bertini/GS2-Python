from __future__ import annotations
from pathlib import Path
import json
from typing import List, Dict, Any

DATA_DIR = Path("data")
USERS_JSON = DATA_DIR / "users.json"
REPORTS_DIR = DATA_DIR / "reports"

def ensure_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def save_users(users: List[Dict[str, Any]], path: Path = USERS_JSON) -> Path:
    """
    Salva a lista de DNAs (users) em JSON com UTF-8 e indentado.
    """
    ensure_dirs()
    with path.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    return path

def load_users(path: Path = USERS_JSON) -> List[Dict[str, Any]]:
    """
    Carrega os DNAs do JSON. Se não existir, retorna lista vazia.
    """
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        # Em caso de erro de parsing, devolve lista vazia
        return []