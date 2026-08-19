# =============================================================================
# AIZI ENGINEERING AI
# TESTE DO INTERPRETADOR DE FABRICAÇÃO
# =============================================================================

from pathlib import Path
import json
import sys


# =============================================================================
# CAMINHOS
# =============================================================================

PASTA_PROJETO = Path(__file__).resolve().parents[2]

PASTA_DIAGNOSTICO = (
    PASTA_PROJETO / "diagnostico"
)


# =============================================================================
# IMPORTAÇÃO
# =============================================================================

try:

    from app.engineering.interpretador_fabricacao import (
        carregar_geometria,
        interpretar,
        imprimir_resultado,
        salvar_resultado,
    )

except ImportError as erro:

    print()
    print("=" * 80)
    print("ERRO AO IMPORTAR O INTERPRETADOR")
    print("=" * 80)
    print()
    print(erro)
    print()
    print(
        "Verifique se o arquivo existe em:"
    )
    print(
        "app/engineering/interpretador_fabricacao.py"
    )
    print()

    sys.exit(1)


# =============================================================================
# LOCALIZAR GEOMETRIAS
# =============================================================================

def localizar_geometrias():

    if not PASTA_DIAGNOSTICO.exists():

        return []

    arquivos = sorted(
        PASTA_DIAGNOSTICO.rglob(
            "*_geometria.json"
        )
    )

    return [
        arquivo
        for arquivo in arquivos
        if not arquivo.name.endswith(
            "_fabricacao.json"
        )
    ]


# =============================================================================
# SELECIONAR GEOMETRIA
# =============================================================================

def selecionar_geometria():

    arquivos = localizar_geometrias()

    if not arquivos:

        print()
        print("=" * 80)
        print("NENHUMA GEOMETRIA ENCONTRADA")
        print("=" * 80)
        print()
        print(
            "Nenhum arquivo *_geometria.json foi encontrado."
        )
        print()
        print(
            "Pasta pesquisada:"
        )
        print(
            PASTA_DIAGNOSTICO
        )
        print()

        return None

    print()
    print("=" * 80)
    print("GEOMETRIAS DISPONÍVEIS")
    print("=" * 80)
    print()

    for numero, arquivo in enumerate(
        arquivos,
        start=1,
    ):

        print(
            f"{numero:02d} - {arquivo.name}"
        )

    print()

    while True:

        escolha = input(
            "Selecione a geometria: "
        ).strip()

        try:

            indice = int(escolha)

        except ValueError:

            print(
                "Digite o número da peça."
            )

            continue

        if 1 <= indice <= len(arquivos):

            return arquivos[
                indice - 1
            ]

        print(
            "Opção inválida."
        )


# =============================================================================
# MOSTRAR RESUMO DO JSON ORIGINAL
# =============================================================================

def mostrar_entrada(dados):

    print()
    print("=" * 80)
    print("DADOS DA GEOMETRIA")
    print("=" * 80)

    print()

    print(
        f"Componente: "
        f"{dados.get('componente')}"
    )

    print(
        f"Score: "
        f"{dados.get('score')}"
    )

    print(
        f"Escala: "
        f"{dados.get('escala')}"
    )

    print(
        f"Largura: "
        f"{dados.get('largura_mm')}"
    )

    print(
        f"Altura: "
        f"{dados.get('altura_mm')}"
    )

    print(
        f"Área: "
        f"{dados.get('area_mm2')}"
    )

    print(
        f"Perímetro: "
        f"{dados.get('perimetro_mm')}"
    )

    print(
        f"Vértices: "
        f"{len(dados.get('vertices_mm', []))}"
    )

    print(
        f"Arcos: "
        f"{len(dados.get('arcos', []))}"
    )

    print(
        f"Dobras: "
        f"{len(dados.get('dobras', []))}"
    )


# =============================================================================
# VALIDAR RESULTADO
# =============================================================================

def validar_resultado(resultado):

    erros = []

    if "origem" not in resultado:

        erros.append(
            "Resultado sem seção 'origem'."
        )

    if "dimensoes" not in resultado:

        erros.append(
            "Resultado sem seção 'dimensoes'."
        )

    if "metricas" not in resultado:

        erros.append(
            "Resultado sem seção 'metricas'."
        )

    if "geometria" not in resultado:

        erros.append(
            "Resultado sem seção 'geometria'."
        )

    if "fabricacao" not in resultado:

        erros.append(
            "Resultado sem seção 'fabricacao'."
        )

    if erros:

        return False, erros

    return True, []


# =============================================================================
# MOSTRAR RESULTADO FINAL
# =============================================================================

def mostrar_resumo_final(resultado):

    fabricacao = resultado[
        "fabricacao"
    ]

    dimensoes = resultado[
        "dimensoes"
    ]

    geometria = resultado[
        "geometria"
    ]

    print()
    print("=" * 80)
    print("RESUMO DA INTERPRETAÇÃO")
    print("=" * 80)

    print()

    print(
        f"Tipo de fabricação: "
        f"{fabricacao['tipo']}"
    )

    print(
        f"Status: "
        f"{fabricacao['status']}"
    )

    print()

    print(
        f"Dimensão: "
        f"{dimensoes['largura_mm']:.3f} "
        f"x "
        f"{dimensoes['altura_mm']:.3f} mm"
    )

    print(
        f"Orientação: "
        f"{dimensoes['orientacao']}"
    )

    print(
        f"Relação de aspecto: "
        f"{dimensoes['relacao_aspecto']:.4f}"
    )

    print()

    print(
        f"Vértices: "
        f"{geometria['quantidade_vertices']}"
    )

    print(
        f"Segmentos: "
        f"{geometria['quantidade_segmentos']}"
    )

    print(
        f"Arcos: "
        f"{len(geometria['arcos']['arcos'])}"
    )

    print(
        f"Dobras: "
        f"{fabricacao['dobras']['quantidade']}"
    )

    print()

    print("INDICADORES:")

    if not fabricacao["indicadores"]:

        print(
            "Nenhum."
        )

    else:

        for indicador in fabricacao[
            "indicadores"
        ]:

            print(
                f"- {indicador}"
            )


# =============================================================================
# MAIN
# =============================================================================

def main():

    print()
    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("TESTE DO INTERPRETADOR DE FABRICAÇÃO")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # LOCALIZAR ARQUIVO
    # -------------------------------------------------------------------------

    caminho = selecionar_geometria()

    if caminho is None:

        return

    print()
    print("Arquivo selecionado:")
    print(caminho)

    # -------------------------------------------------------------------------
    # CARREGAR
    # -------------------------------------------------------------------------

    try:

        dados = carregar_geometria(
            caminho
        )

    except Exception as erro:

        print()
        print("=" * 80)
        print("ERRO AO CARREGAR GEOMETRIA")
        print("=" * 80)
        print()
        print(erro)

        return

    # -------------------------------------------------------------------------
    # MOSTRAR ENTRADA
    # -------------------------------------------------------------------------

    mostrar_entrada(
        dados
    )

    # -------------------------------------------------------------------------
    # INTERPRETAR
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("EXECUTANDO INTERPRETADOR")
    print("=" * 80)
    print()

    try:

        resultado = interpretar(
            dados
        )

    except Exception as erro:

        print()
        print("=" * 80)
        print("ERRO DURANTE A INTERPRETAÇÃO")
        print("=" * 80)
        print()

        print(
            type(erro).__name__
        )

        print(
            str(erro)
        )

        print()

        raise

    # -------------------------------------------------------------------------
    # VALIDAR
    # -------------------------------------------------------------------------

    valido, erros = validar_resultado(
        resultado
    )

    if not valido:

        print()
        print("=" * 80)
        print("RESULTADO INVÁLIDO")
        print("=" * 80)

        for erro in erros:

            print(
                f"- {erro}"
            )

        return

    # -------------------------------------------------------------------------
    # IMPRESSÃO COMPLETA
    # -------------------------------------------------------------------------

    imprimir_resultado(
        resultado
    )

    # -------------------------------------------------------------------------
    # RESUMO
    # -------------------------------------------------------------------------

    mostrar_resumo_final(
        resultado
    )

    # -------------------------------------------------------------------------
    # SALVAR
    # -------------------------------------------------------------------------

    try:

        caminho_saida = salvar_resultado(
            caminho,
            resultado,
        )

    except Exception as erro:

        print()
        print("=" * 80)
        print("ERRO AO SALVAR RESULTADO")
        print("=" * 80)
        print()
        print(erro)

        return

    # -------------------------------------------------------------------------
    # CONFIRMAR JSON
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("VALIDANDO ARQUIVO GERADO")
    print("=" * 80)

    try:

        with open(
            caminho_saida,
            "r",
            encoding="utf-8",
        ) as arquivo:

            json_gerado = json.load(
                arquivo
            )

        print()
        print(
            "JSON de fabricação válido."
        )

        print(
            f"Arquivo: {caminho_saida}"
        )

        print(
            f"Tamanho: "
            f"{caminho_saida.stat().st_size} bytes"
        )

        print(
            f"Seções: "
            f"{', '.join(json_gerado.keys())}"
        )

    except Exception as erro:

        print()
        print(
            "ERRO ao validar JSON gerado:"
        )

        print(
            erro
        )

        return

    # -------------------------------------------------------------------------
    # FINAL
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("TESTE CONCLUÍDO COM SUCESSO")
    print("=" * 80)
    print()


# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":

    main()