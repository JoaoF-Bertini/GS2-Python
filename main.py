from pathlib import Path
from vyra.careers import create_careers_df, update_ecosystem_state
from vyra.world import collect_world_trends
from vyra.users import collect_user_dna
from vyra.recommend import recommend_careers
from vyra.reports import build_recommendations_table, build_wide_from_long, export_csv
from vyra.storage import (
    ensure_dirs, save_users, load_users, REPORTS_DIR,
    save_careers_df, load_careers_df, save_trends, load_trends
)
from vyra.io import (
    show_title, print_df, print_state_counts, print_recommendations,
    print_users_table, print_table
)
from vyra.analytics import (
    state_counts, ods_distribution_by_state,
    plot_state_counts, plot_ods_by_state
)

def main():
    show_title()
    ensure_dirs()

    # Carrega ecossistema se existir, senão cria novo
    df_loaded = load_careers_df()
    df_carreiras = df_loaded if df_loaded is not None else create_careers_df()

    trends_loaded = load_trends()
    world_trends = trends_loaded if trends_loaded else None

    users: list[dict] = []  # DNAs em memória

    while True:
        print("\nMenu")
        print("[1] Listar carreiras (relatório básico)")
        print("[2] Atualizar ecossistema (aplicar tendências do mundo)")
        print("[3] Ver contagem por estado evolutivo")
        print("[4] Cadastrar DNA profissional (usuário)")
        print("[5] Recomendar para o último DNA cadastrado")
        print("[6] Listar DNAs cadastrados")
        print("[7] Salvar DNAs em data/users.json")
        print("[8] Carregar DNAs de data/users.json")
        print("[9] Gerar relatório pandas (users × recomendações)")
        print("[10] Salvar ecossistema (carreiras + estado) em data/careers.json")
        print("[11] Carregar ecossistema de data/careers.json")
        print("[12] Analytics & Gráficos (estados/ODS)")
        print("[0] Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            print_df(df_carreiras, columns=["carreira", "ods", "estado_evolutivo"])

        elif opcao == "2":
            world_trends = collect_world_trends()
            dbg = input("Ativar debug detalhado da atualização? (s/N): ").strip().lower() in ("s","sim","y","yes")
            df_carreiras = update_ecosystem_state(df_carreiras, world_trends, debug=dbg)
            # salvar tendências para reuso futuro
            save_trends(world_trends)
            print("\nEcossistema atualizado com sucesso!")

        elif opcao == "3":
            print_state_counts(df_carreiras)

        elif opcao == "4":
            dna = collect_user_dna()
            if dna:
                users.append(dna)
                print(f"DNA de {dna['nome']} cadastrado.")
            else:
                print("Cadastro cancelado.")

        elif opcao == "5":
            if not users:
                print("Cadastre um DNA primeiro (opção [4]).")
                continue
            dna = users[-1]
            dbg = input("Ativar debug do match? (s/N): ").strip().lower() in ("s","sim","y","yes")
            recs = recommend_careers(dna, df_carreiras, top_n=3, debug=dbg)
            print_recommendations(dna, recs)

        elif opcao == "6":
            print_users_table(users)

        elif opcao == "7":
            path = save_users(users)
            print(f"DNAs salvos em: {path.resolve()}")

        elif opcao == "8":
            users = load_users()
            print(f"DNAs carregados: {len(users)}")

        elif opcao == "9":
            if not users:
                print("Não há DNAs cadastrados. Use a opção [4] ou carregue com [8].")
                continue
            df_long = build_recommendations_table(users, df_carreiras, top_n=3, debug=False)
            print_df(df_long, max_rows=20)

            want_wide = input("Gerar também tabela LARGA (rec_1..rec_3)? (s/N): ").strip().lower() in ("s","sim","y","yes")
            if want_wide:
                df_wide = build_wide_from_long(df_long)
                print_df(df_wide, max_rows=20)

            want_csv = input("Exportar CSV do relatório? (s/N): ").strip().lower() in ("s","sim","y","yes")
            if want_csv:
                if want_wide:
                    from vyra.storage import REPORTS_DIR
                    path_long = REPORTS_DIR / "recomendacoes_long.csv"
                    path_wide = REPORTS_DIR / "recomendacoes_wide.csv"
                    export_csv(df_long, path_long)
                    export_csv(df_wide, path_wide)
                    print(f"CSV salvo: {path_long.resolve()}")
                    print(f"CSV salvo: {path_wide.resolve()}")
                else:
                    filename = "recomendacoes_long.csv"
                    export_csv(df_long, Path("data/reports") / filename)
                    print(f"CSV salvo: {(Path('data/reports')/filename).resolve()}")

        elif opcao == "10":
            path = save_careers_df(df_carreiras)
            print(f"Ecossistema salvo em: {path.resolve()}")

        elif opcao == "11":
            df_loaded = load_careers_df()
            if df_loaded is None:
                print("Arquivo data/careers.json não encontrado.")
            else:
                df_carreiras = df_loaded
                print("Ecossistema carregado com sucesso.")

            # tenta carregar tendências salvas
            trends = load_trends()
            if trends:
                print(f"Tendências carregadas: {trends}")
                world_trends = trends

        elif opcao == "12":
            # Tabelas
            df_counts = state_counts(df_carreiras)
            print_table(df_counts, title="Contagem por estado evolutivo")

            df_ods = ods_distribution_by_state(df_carreiras)
            print_table(df_ods, title="ODS por estado (long)")

            # Gráficos
            png1 = plot_state_counts(df_counts, Path("data/reports/estado_counts.png"))
            png2 = plot_ods_by_state(df_ods, Path("data/reports/ods_por_estado.png"))
            print(f"Gráficos gerados:\n - {png1.resolve()}\n - {png2.resolve()}")

        elif opcao == "0":
            print("Saindo... até a próxima! 👋")
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
