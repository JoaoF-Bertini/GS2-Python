# vyra/analytics.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import matplotlib.pyplot as plt

def state_counts(df_carreiras: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna uma tabela com contagem por estado_evolutivo.
    """
    counts = df_carreiras["estado_evolutivo"].value_counts().rename_axis("estado").reset_index(name="qtd")
    return counts

def ods_distribution_by_state(df_carreiras: pd.DataFrame) -> pd.DataFrame:
    """
    Explode ODS e faz contagem por (estado, ODS).
    """
    df = df_carreiras.explode("ods").dropna(subset=["ods"])
    tbl = (
        df.groupby(["estado_evolutivo", "ods"])
          .size()
          .reset_index(name="qtd")
          .sort_values(["estado_evolutivo", "ods"])
    )
    return tbl

def plot_state_counts(df_counts: pd.DataFrame, out_png: Path) -> Path:
    """
    Gera um gráfico de barras simples de estados (sem definir cores).
    """
    fig, ax = plt.subplots()
    ax.bar(df_counts["estado"], df_counts["qtd"])
    ax.set_title("Contagem por estado evolutivo")
    ax.set_xlabel("Estado")
    ax.set_ylabel("Quantidade")
    plt.xticks(rotation=15)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)
    return out_png

def plot_ods_by_state(df_ods: pd.DataFrame, out_png: Path) -> Path:
    """
    Gera um gráfico de barras agrupadas: para cada estado, barras por ODS.
    """
    if df_ods.empty:
        out_png.parent.mkdir(parents=True, exist_ok=True)
        # cria um PNG vazio com uma mensagem
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Sem ODS para exibir", ha="center", va="center")
        fig.savefig(out_png)
        plt.close(fig)
        return out_png

    # pivot para estados nas categorias e ODS como colunas
    pivot = df_ods.pivot_table(index="estado_evolutivo", columns="ods", values="qtd", aggfunc="sum").fillna(0)

    fig, ax = plt.subplots()
    pivot.plot(kind="bar", ax=ax)  # não definir cores
    ax.set_title("ODS por estado evolutivo")
    ax.set_xlabel("Estado")
    ax.set_ylabel("Quantidade")
    plt.xticks(rotation=15)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)
    return out_png
