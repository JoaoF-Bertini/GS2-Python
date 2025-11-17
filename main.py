from pathlib import Path
from vyra.careers import create_careers_df, update_ecosystem_state
from vyra.world import collect_world_trends
from vyra.users import collect_user_dna
from vyra.recommend import recommend_careers
from vyra.reports import build_recommendations_table, build_wide_from_long, export_csv
from vyra.storage import ensure_dirs, save_users, load_users, REPORTS_DIR
from vyra.io import (
    show_title, print_df, print_state_counts,
    print_recommendations, print_users_table
)

def main():
    show_title()
    ensure_dirs()
    df_carreiras = create_careers_df()
    world_trends = None
    users: list[dict] = []  # DNAs cadastrados em memória

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
        print("[0] Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            print_df(df_carreiras, columns=["carreira", "ods", "estado_evolutivo"])

        elif opcao == "2":
            world_trends = collect_world_trends()
            dbg = input("Ativar debug detalhado da atualização? (s/N): ").strip().lower() in ("s","sim","y","yes")
            df_carreiras = update_ecosystem_state(df_carreiras, world_trends, debug=dbg)
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
            dna = users[-1]  # último cadastrado
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
            # monta a tabela longa
            df_long = build_recommendations_table(users, df_carreiras, top_n=3, debug=False)
            print_df(df_long, max_rows=20)

            # opcional: gerar tabela larga (wide)
            want_wide = input("Gerar também tabela LARGA (rec_1..rec_3)? (s/N): ").strip().lower() in ("s","sim","y","yes")
            if want_wide:
                df_wide = build_wide_from_long(df_long)
                print_df(df_wide, max_rows=20)

            # exportar CSV?
            want_csv = input("Exportar CSV do relatório? (s/N): ").strip().lower() in ("s","sim","y","yes")
            if want_csv:
                default_name = "recomendacoes_long.csv" if not want_wide else "recomendacoes_long_e_wide.csv"
                filename = input(f"Nome do arquivo (ENTER para {default_name}): ").strip() or default_name

                if want_wide:
                    # salvamos dois arquivos: long e wide
                    path_long = REPORTS_DIR / "recomendacoes_long.csv"
                    path_wide = REPORTS_DIR / "recomendacoes_wide.csv"
                    export_csv(df_long, path_long)
                    export_csv(df_wide, path_wide)
                    print(f"CSV salvo: {path_long.resolve()}")
                    print(f"CSV salvo: {path_wide.resolve()}")
                else:
                    path = REPORTS_DIR / filename
                    export_csv(df_long, path)
                    print(f"CSV salvo: {path.resolve()}")

        elif opcao == "0":
            print("Saindo... até a próxima! 👋")
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
