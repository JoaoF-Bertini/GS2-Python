def show_title():
    print("=" * 42)
    print("  VYRA — Ecossistema de Carreiras Vivas")
    print("=" * 42)

def print_df(df, columns=None, max_rows=10):
    """
    Saída formatada: imprime recorte do DataFrame.
    """
    if columns:
        to_show = df[columns]
    else:
        to_show = df
    print("\n--- DataFrame (parcial) ---")
    print(to_show.head(max_rows))

def print_state_counts(df):
    """
    Relatório agregado: contagem por estado_evolutivo.
    """
    print("\n--- Contagem por estado evolutivo ---")
    counts = df["estado_evolutivo"].value_counts()
    print(counts)

def print_recommendations(dna: dict, recs: list[dict]):
    """
    Saída: mostra as recomendações de forma amigável.
    """
    print(f"\n=== Recomendações VYRA para {dna['nome']} ===")
    if not recs:
        print("Nenhuma carreira positiva. Sugestão: evoluir skills ou ajustar preferências.")
        return
    for i, r in enumerate(recs, start=1):
        print(f"\n{i}. {r['carreira']}  [{r['estado']}]")
        print(f"   Score: {r['score']}")
        if r["skills_faltantes"]:
            print("   Skills a desenvolver:", ", ".join(r["skills_faltantes"]))
        else:
            print("   Você já cobre as skills-base desta carreira!")

def print_users_table(users: list[dict], max_rows: int = 10):
    """
    Saída simples: lista os DNAs cadastrados (nome, modo, ODS, skills resumidas).
    """
    if not users:
        print("\nNenhum DNA cadastrado ainda.")
        return
    print("\n--- Usuários cadastrados (parcial) ---")
    for i, u in enumerate(users[:max_rows], start=1):
        skills = ", ".join(u.get("skills", [])[:5])
        ods = ",".join(str(x) for x in u.get("ods_interesse", []))
        print(f"{i:02d}. {u['nome']} | modo={u['modo']} | ODS={ods or '-'} | skills={skills or '-'}")
