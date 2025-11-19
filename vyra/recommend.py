import pandas as pd

# pesos de estado evolutivo no score final
STATE_WEIGHTS = {
    "mutar": 3,
    "crescer": 2,
    "nascer": 1,
    "em_risco": -1,
    "extinta": -3,
}

def recommend_careers(
    dna: dict,
    df_carreiras: pd.DataFrame,
    top_n: int = 3,
    debug: bool = False,
    return_rationale: bool = False,  # novo: devolve explicação detalhada do score
):
    """
    Gera recomendações de carreiras com base no DNA do usuário e no ecossistema (já atualizado).
    Retorna lista de dicts: {'carreira','estado','score','skills_faltantes',('rationale'?)}.
    """

    def score_row(row):
        # normaliza entradas esperadas
        user_sk = set(map(str.lower, dna.get("skills", [])))
        car_sk = set(map(str.lower, row["skills_base"]))
        inter = len(user_sk & car_sk)
        gap = len(car_sk - user_sk)
        s_skills = inter * 2
        s_gap = -gap  # penaliza gaps

        user_ods = dna.get("ods_interesse", [])
        ods_hits = sum(1 for o in user_ods if o in row["ods"]) if user_ods else 0
        s_ods = 2 * ods_hits

        estado = row.get("estado_evolutivo", "nascer")
        s_estado = STATE_WEIGHTS.get(estado, 0)

        modo = dna.get("modo", "hibrido")
        impacto_remoto = row.get("impacto_remoto", 5)
        if modo == "remoto" and impacto_remoto >= 7:
            s_modo = 2
        elif modo == "presencial" and impacto_remoto <= 3:
            s_modo = 2
        elif modo == "hibrido" and 4 <= impacto_remoto <= 6:
            s_modo = 1
        else:
            s_modo = 0

        score = s_skills + s_gap + s_ods + s_estado + s_modo
        faltantes = list(car_sk - user_sk)

        if debug:
            print(
                f"[MATCH] {row['carreira']} -> score={score} "
                f"(skills={s_skills}, gap={s_gap}, ods={s_ods}, estado={s_estado}, modo={s_modo})"
            )

        rationale = {
            "skills": s_skills,
            "gap": s_gap,
            "ods": s_ods,
            "estado": s_estado,
            "modo": s_modo,
            "total": score,
        }
        return score, faltantes, estado, rationale

    resultados = []
    for _, row in df_carreiras.iterrows():
        score, faltantes, estado, rationale = score_row(row)
        if score > 0:
            item = {
                "carreira": row["carreira"],
                "estado": estado,
                "score": score,
                "skills_faltantes": faltantes
            }
            if return_rationale:
                item["rationale"] = rationale
            resultados.append(item)

    resultados.sort(key=lambda r: r["score"], reverse=True)
    return resultados[:top_n]
