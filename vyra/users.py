def _parse_list(raw: str) -> list[str]:
    """
    'python, dados, ia' -> ['python','dados','ia'] normalizado.
    """
    return [p.strip().lower() for p in raw.split(",") if p.strip()]

def _parse_ods(raw: str) -> list[int]:
    """
    '4,8,9' -> [4,8,9] (ignora o que não for número).
    """
    out = []
    for p in raw.split(","):
        p = p.strip()
        if p.isdigit():
            out.append(int(p))
    return out

def collect_user_dna() -> dict | None:
    """
    Estrutura de entrada: coleta o DNA profissional digital do usuário.
    Retorna None se o usuário der ENTER no nome (para sair do cadastro).
    """
    print("\n--- Cadastro de DNA profissional digital ---")
    nome = input("Nome (ENTER para cancelar): ").strip()
    if not nome:
        return None

    area = input("Área atual (ex: TI, RH, Marketing): ").strip()

    skills_raw = input("Habilidades (ex: python, dados, ia): ").lower()
    skills = _parse_list(skills_raw)

    valores_raw = input("Valores (ex: impacto social, inovação): ").lower()
    valores = _parse_list(valores_raw)

    modo = input("Modo de trabalho preferido (remoto / hibrido / presencial): ").strip().lower()
    if modo not in ("remoto", "hibrido", "presencial"):
        print("Modo inválido. Usando 'hibrido' como padrão.")
        modo = "hibrido"

    ods_raw = input("ODS de interesse (ex: 4,8,9,10 – opcional): ").strip()
    ods = _parse_ods(ods_raw) if ods_raw else []

    return {
        "nome": nome,
        "area": area,
        "skills": skills,
        "valores": valores,
        "modo": modo,
        "ods_interesse": ods,
    }
