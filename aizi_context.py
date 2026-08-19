from pathlib import Path
from datetime import datetime


# ============================================================
# AIZI ENGINEERING AI
# GERENCIADOR DE CONTEXTO DO PROJETO
# ============================================================

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

# Documentos principais do AIZI
ARQUIVOS_CONTEXTO = [
    ("_CONTEXT.md", DOCS / "AIZI" / "_CONTEXT.md"),
    ("ARQUITETURA.md", DOCS / "ARQUITETURA.md"),
    ("DECISOES.md", DOCS / "DECISOES.md"),
    ("ROADMAP.md", DOCS / "ROADMAP.md"),
]


def ler_arquivo(caminho: Path) -> str:
    """
    Lê um arquivo de texto usando UTF-8.
    Se necessário, tenta latin1.
    """

    if not caminho.exists():
        return ""

    try:
        return caminho.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        return caminho.read_text(encoding="latin1")


def carregar_contexto() -> dict:
    """
    Carrega todos os documentos principais do projeto.
    """

    contexto = {
        "projeto": "AIZI Engineering AI",
        "raiz": str(ROOT),
        "data_leitura": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "documentos": {},
    }

    for nome_arquivo, caminho in ARQUIVOS_CONTEXTO:

        contexto["documentos"][nome_arquivo] = {
            "caminho": str(caminho),
            "existe": caminho.exists(),
            "conteudo": ler_arquivo(caminho),
        }

    return contexto


def exibir_contexto(contexto: dict):
    """
    Exibe o contexto completo no terminal.
    """

    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("GERENCIADOR DE CONTEXTO")
    print("=" * 80)

    print()
    print(f"Projeto : {contexto['projeto']}")
    print(f"Raiz    : {contexto['raiz']}")
    print(f"Leitura : {contexto['data_leitura']}")

    print()
    print("=" * 80)
    print("DOCUMENTOS DO PROJETO")
    print("=" * 80)

    for nome, documento in contexto["documentos"].items():

        print()
        print("-" * 80)
        print(nome)
        print("-" * 80)

        if not documento["existe"]:
            print("ARQUIVO NAO ENCONTRADO")
            print(f"Caminho: {documento['caminho']}")
            continue

        conteudo = documento["conteudo"].strip()

        if not conteudo:
            print("ARQUIVO VAZIO")
            print(f"Caminho: {documento['caminho']}")
            continue

        print(conteudo)

    print()
    print("=" * 80)
    print("FIM DO CONTEXTO")
    print("=" * 80)


def salvar_contexto_consolidado(contexto: dict):
    """
    Gera um único arquivo contendo todo o contexto.

    O arquivo consolidado fica em:

        docs/AIZI/_CONTEXT/_COMPLETO.md
    """

    pasta_saida = DOCS / "AIZI" / "_CONTEXT"
    pasta_saida.mkdir(parents=True, exist_ok=True)

    caminho_saida = pasta_saida / "_COMPLETO.md"

    linhas = []

    linhas.append("# AIZI ENGINEERING AI")
    linhas.append("")
    linhas.append("# CONTEXTO COMPLETO")
    linhas.append("")
    linhas.append(
        f"Gerado em: {contexto['data_leitura']}"
    )
    linhas.append("")

    for nome, documento in contexto["documentos"].items():

        linhas.append("")
        linhas.append("=" * 80)
        linhas.append(f"# {nome}")
        linhas.append("=" * 80)
        linhas.append("")

        if documento["existe"]:

            conteudo = documento["conteudo"].strip()

            if conteudo:
                linhas.append(conteudo)
            else:
                linhas.append("ARQUIVO VAZIO")

        else:

            linhas.append("ARQUIVO NAO ENCONTRADO")
            linhas.append(
                f"Caminho esperado: {documento['caminho']}"
            )

        linhas.append("")

    caminho_saida.write_text(
        "\n".join(linhas),
        encoding="utf-8",
    )

    return caminho_saida


def main():

    contexto = carregar_contexto()

    exibir_contexto(contexto)

    caminho = salvar_contexto_consolidado(
        contexto
    )

    print()
    print(
        "Contexto consolidado salvo em:"
    )
    print(caminho)


if __name__ == "__main__":
    main()