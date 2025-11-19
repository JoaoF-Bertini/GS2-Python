# vyra/storage.py
from __future__ import annotations
from pathlib import Path
import json
from typing import List, Dict, Any
import pandas as pd

DATA_DIR = Path("data")
REPORTS_DIR = DATA_DIR / "reports"
USERS_JSON = DATA_DIR / "users.json"
CAREERS_JSON = DATA_DIR / "careers.json"
TRENDS_JSON = DATA_DIR / "trends.json"

def ensure_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------
# USERS (DNAs) JSON
# ------------------------
def save_users(users: List[Dict[str, Any]], path: Path = USERS_JSON) -> Path:
    ensure_dirs()
    with path.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    return path

def load_users(path: Path = USERS_JSON) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

# ------------------------
# CAREERS (DataFrame) JSON
# ------------------------
def save_careers_df(df: pd.DataFrame, path: Path = CAREERS_JSON) -> Path:
    """
    Salva o DataFrame de carreiras como JSON (records) preservando listas.
    """
    ensure_dirs()
    records = df.to_dict(orient="records")
    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return path

def load_careers_df(path: Path = CAREERS_JSON) -> pd.DataFrame | None:
    """
    Carrega o DataFrame de carreiras a partir do JSON (records). Retorna None se não existir.
    """
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        records = json.load(f)
    if not isinstance(records, list):
        return None
    return pd.DataFrame(records)

# ------------------------
# TRENDS (dict) JSON
# ------------------------
def save_trends(trends: Dict[str, Any] | None, path: Path = TRENDS_JSON) -> Path:
    ensure_dirs()
    with path.open("w", encoding="utf-8") as f:
        json.dump(trends or {}, f, ensure_ascii=False, indent=2)
    return path

def load_trends(path: Path = TRENDS_JSON) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
