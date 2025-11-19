# api/app.py
from __future__ import annotations
from typing import List, Optional, Dict, Any
import threading
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd

from vyra.careers import create_careers_df, update_ecosystem_state
from vyra.recommend import recommend_careers
from vyra.storage import (
    ensure_dirs, load_users, save_users,
    load_careers_df, save_careers_df,
    load_trends, save_trends, REPORTS_DIR
)
from vyra.reports import build_recommendations_table, build_wide_from_long, export_csv

# =========================
# Helpers (normalização)
# =========================
def _norm_list_str(xs: List[str] | None) -> List[str]:
    out: List[str] = []
    for x in xs or []:
        x = (x or "").strip().lower()
        if x and x not in out:
            out.append(x)
    return out

def _norm_ods(xs: List[int] | None) -> List[int]:
    out: List[int] = []
    for n in xs or []:
        try:
            n = int(n)
            if 1 <= n <= 17 and n not in out:
                out.append(n)
        except Exception:
            pass
    return out

# =========================
# Schemas (Pydantic)
# =========================
class TrendInput(BaseModel):
    ia: int = Field(ge=0, le=10)
    clima: int = Field(ge=0, le=10)
    remoto: int = Field(ge=0, le=10)

class UserDNA(BaseModel):
    nome: str
    area: Optional[str] = ""
    skills: List[str] = []
    valores: List[str] = []
    modo: str = Field(default="hibrido", pattern="^(remoto|hibrido|presencial)$")
    ods_interesse: List[int] = []

class Recommendation(BaseModel):
    carreira: str
    estado: str
    score: int
    skills_faltantes: List[str]
    rationale: Optional[Dict[str, Any]] = None  # explicação opcional

class RecommendRequest(BaseModel):
    dna: Optional[UserDNA] = None
    top_n: int = Field(default=3, ge=1, le=10)
    use_last_user: bool = False
    debug: bool = False
    explain: bool = True  # ativa 'rationale' no retorno

class RecommendResponse(BaseModel):
    nome: str
    top_n: int
    items: List[Recommendation]

# =========================
# App, CORS e Logging
# =========================
app = FastAPI(title="VYRA API", version="1.1.0")

# Para DEV (liberado). Em produção, troque pelo domínio do front:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ex.: ["http://localhost:5173","https://seu-front.vercel.app"]
    allow_credentials=True,
    allow_methods=["GET","POST","PUT"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    resp = await call_next(request)
    dur_ms = (time.time() - start) * 1000.0
    print(f"[{request.method}] {request.url.path} -> {resp.status_code} ({dur_ms:.1f} ms)")
    return resp

# =========================
# Estado em memória + Lock
# =========================
ensure_dirs()
_lock = threading.Lock()

_df: pd.DataFrame = load_careers_df() or create_careers_df()
_trends: Optional[dict] = load_trends() or None
_users: List[dict] = load_users()

if _trends:
    _df = update_ecosystem_state(_df, _trends, debug=False)

# =========================
# Endpoints
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/v1/careers")
def get_careers(
    state: Optional[str] = None,
    order_by: str = "carreira",
    offset: int = 0,
    limit: int = 50,
):
    """
    Lista carreiras com paginação e filtro por estado.
    """
    df = _df
    if state:
        df = df[df["estado_evolutivo"] == state]

    cols = ["carreira", "ods", "estado_evolutivo", "impacto_ia", "impacto_clima", "impacto_remoto"]
    if order_by in cols:
        df = df.sort_values(order_by, kind="stable")

    total = len(df)
    start = max(offset, 0)
    end = start + max(limit, 1)
    page = df.iloc[start:end]
    return {"total": total, "items": page[cols].to_dict(orient="records")}

@app.put("/v1/trends")
def put_trends(body: TrendInput):
    """
    Aplica tendências ao ecossistema e persiste (trends + careers).
    Retorna contagem por estado.
    """
    global _df, _trends
    with _lock:
        _trends = body.model_dump()
        _df = update_ecosystem_state(_df, _trends, debug=False)
        save_trends(_trends)
        save_careers_df(_df)
        counts = _df["estado_evolutivo"].value_counts().to_dict()
    return {"trends": _trends, "state_counts": counts}

@app.get("/v1/users")
def list_users():
    return _users

@app.post("/v1/users")
def create_user(dna: UserDNA):
    """
    Cadastra um DNA com normalização básica (lowercase, dedupe).
    """
    with _lock:
        data = dna.model_dump()
        data["skills"] = _norm_list_str(data.get("skills"))
        data["valores"] = _norm_list_str(data.get("valores"))
        data["ods_interesse"] = _norm_ods(data.get("ods_interesse"))
        _users.append(data)
        save_users(_users)
        count = len(_users)
    return {"ok": True, "count": count}

@app.post("/v1/recommend", response_model=RecommendResponse)
def post_recommend(req: RecommendRequest):
    """
    Gera recomendações para o último usuário cadastrado (use_last_user=true)
    ou para um DNA enviado inline no body.
    """
    # seleciona DNA
    if req.use_last_user:
        if not _users:
            raise HTTPException(status_code=400, detail="Nenhum usuário cadastrado.")
        dna = _users[-1]
    elif req.dna:
        dna = req.dna.model_dump()
        dna["skills"] = _norm_list_str(dna.get("skills"))
        dna["valores"] = _norm_list_str(dna.get("valores"))
        dna["ods_interesse"] = _norm_ods(dna.get("ods_interesse"))
    else:
        raise HTTPException(status_code=400, detail="Forneça 'dna' ou 'use_last_user=true'.")

    recs = recommend_careers(
        dna, _df,
        top_n=req.top_n,
        debug=req.debug,
        return_rationale=req.explain,
    )
    # validação leve para casar com o schema de resposta
    items = [Recommendation(**r) for r in recs]
    return RecommendResponse(nome=dna.get("nome", "(sem nome)"), top_n=req.top_n, items=items)

@app.post("/v1/persist")
def persist_all():
    """
    Força salvar usuários, tendências e carreiras.
    """
    with _lock:
        save_users(_users)
        save_trends(_trends or {})
        save_careers_df(_df)
    return {"ok": True}

@app.get("/v1/reports/recommendations")
def report_recommendations(top_n: int = 3, wide: bool = False, export: bool = False):
    """
    Relatório em JSON (long ou wide). Se export=true, salva CSV em data/reports/.
    """
    if not _users:
        return {"items": [], "shape": [0, 0]}
    df_long = build_recommendations_table(_users, _df, top_n=top_n, debug=False)
    if wide:
        df_wide = build_wide_from_long(df_long)
        if export:
            export_csv(df_wide, REPORTS_DIR / "recomendacoes_wide.csv")
        return {"items": df_wide.to_dict(orient="records"), "shape": list(df_wide.shape)}
    else:
        if export:
            export_csv(df_long, REPORTS_DIR / "recomendacoes_long.csv")
        return {"items": df_long.to_dict(orient="records"), "shape": list(df_long.shape)}
