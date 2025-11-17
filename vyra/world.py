def _read_int_0_10(prompt: str) -> int:
    """
    Lê e valida um inteiro entre 0 e 10 (inclusive).
    """
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            val = int(raw)
            if 0 <= val <= 10:
                return val
        print("Valor inválido. Digite um número inteiro de 0 a 10.")

def collect_world_trends() -> dict:
    """
    Estrutura de entrada: coleta tendências do mundo (0..10).
    Retorna dict: {'ia': int, 'clima': int, 'remoto': int}
    """
    print("\n=== Estado do mundo (0 a 10) ===")
    ia = _read_int_0_10("Nível de avanço de IA (0-10): ")
    clima = _read_int_0_10("Força da crise climática (0-10): ")
    remoto = _read_int_0_10("Intensidade do trabalho remoto/híbrido (0-10): ")
    return {"ia": ia, "clima": clima, "remoto": remoto}
