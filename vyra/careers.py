import pandas as pd

def create_careers_df():
    """
    Cria o DataFrame base do ecossistema VYRA com 'espécies de carreira'.
    Já retorna uma coluna 'estado_evolutivo' inicial (crescer).
    Demonstra: DataFrame + função dentro de função (nested).
    """

    def L(*args):
        """Atalho para criar listas de forma legível nas colunas do DF."""
        return [*args]

    data = {
        "carreira": [
            "Engenheiro(a) de Ecossistemas de IA",
            "Curador(a) de Aprendizagem Contínua",
            "Designer de Ambientes Imersivos (VR/AR)",
            "Gestor(a) de Bem-estar Digital",
            "Analista de Impacto Socioambiental de Dados"
        ],
        "skills_base": [
            L("python", "ia", "dados"),
            L("educacao", "facilitacao", "ia"),
            L("vr", "ux", "colaboracao"),
            L("psicologia", "bem-estar", "dados"),
            L("sustentabilidade", "dados", "esg")
        ],
        "ods": [
            L(4, 8, 9),
            L(4, 8),
            L(8, 9),
            L(3, 8, 10),
            L(8, 9, 10, 12)
        ],
        # pesos de sensibilidade (0..10) a cada tendência
        "impacto_ia":     [9, 8, 6, 5, 7],
        "impacto_clima":  [4, 3, 2, 5, 9],
        "impacto_remoto": [7, 8, 9, 8, 6],
    }

    df = pd.DataFrame(data)
    df["estado_evolutivo"] = "crescer"  # valor inicial
    return df


def update_ecosystem_state(df: pd.DataFrame, trends: dict, debug: bool = False) -> pd.DataFrame:
    """
    Aplica as tendências do mundo ao ecossistema e reclassifica o estado evolutivo.
    trends = {'ia': int, 'clima': int, 'remoto': int} (0..10)
    Retorna o DF atualizado.
    """

    def classify_row(row) -> str:
        # parcelas do score
        s_ia = row["impacto_ia"] * trends.get("ia", 0)
        s_cl = row["impacto_clima"] * trends.get("clima", 0)
        s_re = row["impacto_remoto"] * trends.get("remoto", 0)
        score = s_ia + s_cl + s_re

        if debug:
            print(
                f"[DEBUG] {row['carreira']}\n"
                f"        ia={row['impacto_ia']}*{trends.get('ia',0)} -> {s_ia}, "
                f"clima={row['impacto_clima']}*{trends.get('clima',0)} -> {s_cl}, "
                f"remoto={row['impacto_remoto']}*{trends.get('remoto',0)} -> {s_re} | "
                f"score={score}"
            )

        # Faixas de corte ajustadas (máx teórico = 300)
        if score >= 230:
            estado = "mutar"
        elif score >= 170:
            estado = "crescer"
        elif score >= 110:
            estado = "nascer"
        elif score >= 60:
            estado = "em_risco"
        else:
            estado = "extinta"

        if debug:
            print(f"        => estado: {estado}\n")

        return estado

    df["estado_evolutivo"] = df.apply(classify_row, axis=1)
    return df
