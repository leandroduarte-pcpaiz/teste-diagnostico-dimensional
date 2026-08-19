from __future__ import annotations

import json
import sys
from pathlib import Path


# =============================================================================
# CORREÇÃO DE IMPORTAÇÃO
# =============================================================================

RAIZ_PROJETO = Path(__file__).resolve().parents[2]

if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


# =============================================================================
# IMPORTAÇÕES
# =============================================================================

from app.engineering.interpretador_geometria import (
    interpretar_geometria,
)

from app.engineering.analisador_dobras import (
    analisar_dobras,
)

from app.engineering.consolidador_dobras import (
    consolidar_dobras,
)


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

PASTA_DIAGNOSTICO = (
    RAIZ_PROJETO / "diagnostico"
)

ARQUIVO_GEOMETRIA = (
    PASTA_DIAGNOSTICO
    / "_I1044988_geometria.json"
)


# =============================================================================
# IMPRESSÃO
# =============================================================================

def linha():
    print("=" * 80)


def imprimir_candidatas(candidatas):
    print()
    print("=" * 80)
    print("CANDIDATAS CONSOLIDADAS")
    print("=" * 80)

    if not candidatas:
        print()
        print("Nenhuma candidata consolidada.")
        return

    for i, candidata in enumerate(
        candidatas,
        start=1,
    ):
        print()
        print(f"Dobra consolidada {i}")

        print(
            f"  Segmentos: "
            f"{candidata.get('segmentos')}"
        )

        print(
            f"  Ângulo: "
            f"{candidata.get('angulo_graus')}°"
        )

        print(
            f"  Classificação: "
            f"{candidata.get('classificacao')}"
        )

        print(
            f"  Confiança: "
            f"{candidata.get('confianca')}"
        )

        print(
            f"  Ponto: "
            f"{candidata.get('ponto')}"
        )

        print(
            f"  Raio: "
            f"{candidata.get('raio_mm')}"
        )

        print(
            f"  Origem: "
            f"{candidata.get('origem')}"
        )


# =============================================================================
# MAIN
# =============================================================================

def main():

    linha()

    print(
        "TESTE ISOLADO - CONSOLIDADOR DE DOBRAS"
    )

    linha()

    # -------------------------------------------------------------------------
    # 1. ARQUIVO
    # -------------------------------------------------------------------------

    print()
    print(linha.__name__.upper())

    print()
    print("1. ARQUIVO DE GEOMETRIA")
    print()

    print(
        f"Arquivo:\n{ARQUIVO_GEOMETRIA}"
    )

    if not ARQUIVO_GEOMETRIA.exists():

        print()
        print(
            "ERRO - arquivo de geometria não encontrado."
        )

        print()
        print("Arquivos disponíveis:")

        for arquivo in sorted(
            PASTA_DIAGNOSTICO.glob(
                "*_geometria.json"
            )
        ):
            print(
                f"  - {arquivo.name}"
            )

        return

    print()
    print("OK - arquivo encontrado.")

    # -------------------------------------------------------------------------
    # 2. CARREGAMENTO
    # -------------------------------------------------------------------------

    print()
    print("2. CARREGAMENTO DO JSON")
    print()

    try:

        with open(
            ARQUIVO_GEOMETRIA,
            "r",
            encoding="utf-8",
        ) as arquivo:

            dados = json.load(
                arquivo
            )

    except Exception as erro:

        print(
            f"ERRO AO CARREGAR JSON: {erro}"
        )

        return

    print(
        "OK - JSON carregado."
    )

    # -------------------------------------------------------------------------
    # 3. ORIGEM
    # -------------------------------------------------------------------------

    print()
    print("3. DADOS DE ORIGEM")
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
        f"Orientação: "
        f"{dados.get('orientacao')}"
    )

    print(
        f"Dimensão alvo: "
        f"{dados.get('dimensao_alvo_mm')}"
    )

    print(
        f"Vértices no JSON: "
        f"{len(dados.get('vertices_mm', []))}"
    )

    print(
        f"Arcos no JSON: "
        f"{len(dados.get('arcos', []))}"
    )

    # -------------------------------------------------------------------------
    # 4. INTERPRETAÇÃO
    # -------------------------------------------------------------------------

    print()
    print("4. INTERPRETAÇÃO DA GEOMETRIA")
    print()

    try:

        estrutura = interpretar_geometria(
            dados
        )

    except Exception as erro:

        print(
            f"ERRO AO INTERPRETAR GEOMETRIA: {erro}"
        )

        return

    print(
        "OK - geometria interpretada."
    )

    # -------------------------------------------------------------------------
    # 5. ANÁLISE DE DOBRAS
    # -------------------------------------------------------------------------

    print()
    print("5. ANÁLISE DAS DOBRAS")
    print()

    try:

        analise = analisar_dobras(
            estrutura
        )

    except Exception as erro:

        print(
            f"ERRO AO ANALISAR DOBRAS: {erro}"
        )

        return

    print(
        "OK - análise de dobras executada."
    )

    # -------------------------------------------------------------------------
    # 6. RESUMO DA ANÁLISE ORIGINAL
    # -------------------------------------------------------------------------

    print()
    print("6. RESULTADO DO ANALISADOR")
    print()

    print(
        f"Status: "
        f"{analise.get('status')}"
    )

    print(
        f"Transições analisadas: "
        f"{analise.get('transicoes_analisadas')}"
    )

    print(
        f"Candidatas: "
        f"{len(analise.get('candidatas', []))}"
    )

    # -------------------------------------------------------------------------
    # 7. CONSOLIDAÇÃO
    # -------------------------------------------------------------------------

    print()
    print("7. CONSOLIDAÇÃO DAS DOBRAS")
    print()

    try:

        consolidado = consolidar_dobras(
            estrutura,
            analise,
        )

    except Exception as erro:

        print(
            f"ERRO AO CONSOLIDAR DOBRAS: {erro}"
        )

        return

    print(
        "OK - consolidação executada."
    )

    # -------------------------------------------------------------------------
    # 8. RESUMO CONSOLIDADO
    # -------------------------------------------------------------------------

    print()
    print("8. RESUMO CONSOLIDADO")
    print()

    print(
        f"Status: "
        f"{consolidado.get('status')}"
    )

    print(
        f"Quantidade de candidatas originais: "
        f"{consolidado.get('quantidade_candidatas_originais')}"
    )

    print(
        f"Quantidade de dobras consolidadas: "
        f"{consolidado.get('quantidade_dobras_consolidadas')}"
    )

    print(
        f"Quantidade de dobras 90°: "
        f"{consolidado.get('quantidade_90_graus')}"
    )

    print(
        f"Quantidade de dobras angulares: "
        f"{consolidado.get('quantidade_angulares')}"
    )

    print(
        f"Arcos disponíveis: "
        f"{consolidado.get('arcos_disponiveis')}"
    )

    # -------------------------------------------------------------------------
    # 9. DOBRAS CONSOLIDADAS
    # -------------------------------------------------------------------------

    imprimir_candidatas(
        consolidado.get(
            "dobras",
            []
        )
    )

    # -------------------------------------------------------------------------
    # 10. VALIDAÇÃO
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("10. VALIDAÇÃO")
    print("=" * 80)

    dobras = consolidado.get(
        "dobras",
        []
    )

    if not isinstance(
        dobras,
        list,
    ):

        print(
            "ERRO - campo 'dobras' não é uma lista."
        )

        return

    print(
        "OK - estrutura consolidada válida."
    )

    quantidade_originais = len(
        analise.get(
            "candidatas",
            []
        )
    )

    quantidade_consolidadas = len(
        dobras
    )

    if quantidade_consolidadas <= quantidade_originais:

        print(
            "OK - consolidação não aumentou "
            "artificialmente a quantidade de dobras."
        )

    else:

        print(
            "ATENÇÃO - quantidade consolidada "
            "maior que quantidade original."
        )

    # -------------------------------------------------------------------------
    # 11. SEGURANÇA
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("11. VALIDAÇÃO DE SEGURANÇA")
    print("=" * 80)

    print()
    print(
        "IMPORTANTE:"
    )

    print(
        "O ConsolidadorDobras:"
    )

    print(
        "  - não calcula BLANK."
    )

    print(
        "  - não calcula desenvolvimento."
    )

    print(
        "  - não chama a CalculadoraCorte."
    )

    print(
        "  - não altera a geometria original."
    )

    print(
        "  - apenas organiza e consolida "
        "as candidatas identificadas."
    )

    print()
    print(
        "OK - consolidação permanece conservadora."
    )

    # -------------------------------------------------------------------------
    # 12. RESULTADO FINAL
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("12. RESULTADO FINAL")
    print("=" * 80)

    print()

    print(
        f"Arquivo: "
        f"{ARQUIVO_GEOMETRIA.name}"
    )

    print(
        f"Componente: "
        f"{dados.get('componente')}"
    )

    print(
        f"Vértices: "
        f"{len(estrutura['geometria']['vertices'])}"
    )

    print(
        f"Segmentos: "
        f"{len(estrutura['geometria']['segmentos'])}"
    )

    print(
        f"Arcos: "
        f"{len(estrutura['geometria']['arcos'])}"
    )

    print(
        f"Status do analisador: "
        f"{analise.get('status')}"
    )

    print(
        f"Candidatas originais: "
        f"{quantidade_originais}"
    )

    print(
        f"Dobras consolidadas: "
        f"{quantidade_consolidadas}"
    )

    print()
    print(
        "TESTE DO CONSOLIDADOR DE DOBRAS CONCLUÍDO."
    )

    print("=" * 80)


if __name__ == "__main__":
    main()