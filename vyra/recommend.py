import pandas as pd

STATE_WEIGHTS = {
    "mutar": 3,
    "crescer": 2,
    "nascer": 1,
    "em_risco": -1,
    "extinta": -3,
}

def recommend_careers(dna: dict, df_carreiras: pd.DataFrame, top_n: int = 3, debug: bool = False):
    """
    Gera recomendações de carreiras com base no DNA do usuário e no ecossistema (já atualizado).
    Retorna lista de dicts: {'carreira','estado','score','skills_faltantes'}
    """

    def score_row(row) -> tuple[int, list[str]]:
        """
        Regras:
        - +2 por cada skill que o usuário já tem (interseção)
        - -1 por cada skill faltante (gap)
        - +2 por cada ODS de interesse do usuário que esteja na carreira
        - Ajuste pelo estado evolutivo (mutar=+3, crescer=+2, nascer=+1, em_risco=-1, extinta=-3)
        - Modo de trabalho vs impacto_remoto:
            * remoto & impacto_remoto >= 7 -> +2
            * presencial & impacto_remoto <= 3 -> +2
            * hibrido & 4 <= impacto_remoto <= 6 -> +1
        """
        score = 0
        user_sk = set(dna.get("skills", []))
        car_sk = set(row["skills_base"])

        inter = len(user_sk & car_sk)
        gap = len(car_sk - user_sk)

        score += inter * 2
        score -= gap

        user_ods = dna.get("ods_interesse", [])
        if user_ods:
            ods_hits = sum(1 for o in user_ods if o in row["ods"])
            score += 2 * ods_hits
        else:
            ods_hits = 0

        estado = row.get("estado_evolutivo", "nascer")
        score += STATE_WEIGHTS.get(estado, 0)

        modo = dna.get("modo", "hibrido")
        impacto_remoto = row.get("impacto_remoto", 5)
        if modo == "remoto" and impacto_remoto >= 7:
            score += 2
        elif modo == "presencial" and impacto_remoto <= 3:
            score += 2
        elif modo == "hibrido" and 4 <= impacto_remoto <= 6:
            score += 1

        faltantes = list(car_sk - user_sk)

        if debug:
            print(
                f"[MATCH] {dna.get('nome','(sem nome)')} × {row['carreira']} | "
                f"inter={inter} gap={gap} ods+={ods_hits} "
                f"estado={estado}({STATE_WEIGHTS.get(estado,0)}) modo={modo}/impRem={impacto_remoto} -> score={score}"
            )

        return score, faltantes

    resultados = []
    for _, row in df_carreiras.iterrows():
        score, faltantes = score_row(row)
        if score > 0:
            resultados.append({
                "carreira": row["carreira"],
                "estado": row.get("estado_evolutivo", "nascer"),
                "score": score,
                "skills_faltantes": faltantes
            })

    resultados.sort(key=lambda r: r["score"], reverse=True)
    return resultados[:top_n]
