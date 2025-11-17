from __future__ import annotations
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any
from .recommend import recommend_careers

def build_recommendations_table(
    users: List[Dict[str, Any]],
    df_carreiras: pd.DataFrame,
    top_n: int = 3,
    debug: bool = False,
) -> pd.DataFrame:
    """
    Gera uma tabela LONGA (uma linha por recomendação) com:
    nome, modo, ods, skills, rec_rank, carreira, estado, score, skills_faltantes
    """
    rows = []
    for u in users:
        recs = recommend_careers(u, df_carreiras, top_n=top_n, debug=debug)
        if not recs:
            rows.append({
                "nome": u.get("nome", "-"),
                "modo": u.get("modo", "-"),
                "ods": ",".join(str(x) for x in u.get("ods_interesse", [])),
                "skills": ",".join(u.get("skills", [])),
                "rec_rank": None,
                "carreira": None,
                "estado": None,
                "score": None,
                "skills_faltantes": None,
            })
        else:
            for rank, r in enumerate(recs, start=1):
                rows.append({
                    "nome": u.get("nome", "-"),
                    "modo": u.get("modo", "-"),
                    "ods": ",".join(str(x) for x in u.get("ods_interesse", [])),
                    "skills": ",".join(u.get("skills", [])),
                    "rec_rank": rank,
                    "carreira": r["carreira"],
                    "estado": r["estado"],
                    "score": r["score"],
                    "skills_faltantes": ",".join(r["skills_faltantes"]),
                })
    return pd.DataFrame(rows)

def build_wide_from_long(df_long: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói uma tabela LARGA no formato:
    uma linha por usuário e colunas rec_1, rec_2, rec_3 com os nomes das carreiras.
    """
    if df_long.empty:
        return pd.DataFrame(columns=["nome","modo","ods","skills","rec_1","rec_2","rec_3"])
    wide = (
        df_long
        .pivot_table(
            index=["nome","modo","ods","skills"],
            columns="rec_rank",
            values="carreira",
            aggfunc="first"
        )
        .rename(columns={1:"rec_1", 2:"rec_2", 3:"rec_3"})
        .reset_index()
    )
    # Garante colunas mesmo se faltarem ranks
    for col in ["rec_1","rec_2","rec_3"]:
        if col not in wide.columns:
            wide[col] = None
    return wide

def export_csv(df: pd.DataFrame, path: Path) -> Path:
    """
    Exporta um DataFrame para CSV (UTF-8, sem índice).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    return path