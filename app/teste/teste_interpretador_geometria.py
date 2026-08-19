from __future__ import annotations

import json
import sys
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO DO PROJETO
# =============================================================================

RAIZ_PROJETO = Path(
    r"C:\Projetos\AIZI Engineering AI"
)

if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(
        0,
        str(RAIZ_PROJETO),
    )


from app.engineering.interpretador_geometria import (
    interpretar_geometria,
)


# =============================================================================
# CONFIGURAÇÃO DO TESTE
# =============================================================================

PASTA_DIAGNOSTICO = (
    RAIZ_PROJETO / "diagnostico"
)

NOME_ARQUIVO_PREFERENCIAL = (
    "_I1044988_geometria.json"
)


# =============================================================================
# LOCALIZAR ARQUIVO
# =============================================================================

def localizar_arquivo_geometria():

    caminho_preferencial = (
        PASTA_DIAGNOSTICO
        / NOME_ARQUIVO_PREFERENCIAL
    )

    if caminho_preferencial.exists():
        return caminho_preferencial

    arquivos = sorted(
        PASTA_DIAGNOSTICO.glob(
            "*I1044988*geometria.json"
        )
    )

    if arquivos:
        return arquivos[0]

    return None


# =============================================================================
# CARREGAR JSON
# =============================================================================

def carregar_json(caminho):

    with open(
        caminho,
        "r",
        encoding="utf-8",
    ) as arquivo:

        return json.load(arquivo)


# =============================================================================
# SEGMENTOS
# =============================================================================

def imprimir_segmentos(estrutura):

    segmentos = (
        estrutura
        .get("geometria", {})
        .get("segmentos", [])
    )

    print()
    print("=" * 80)
    print("SEGMENTOS IDENTIFICADOS")
    print("=" * 80)

    print(
        f"Quantidade: {len(segmentos)}"
    )

    for segmento in segmentos:

        print(
            f"  Segmento {segmento['id']:02d}: "
            f"{segmento['tipo']:<10} "
            f"{segmento['comprimento_mm']:.4f} mm "
            f"({segmento['inicio']} -> "
            f"{segmento['fim']})"
        )


# =============================================================================
# ARCOS
# =============================================================================

def imprimir_arcos(estrutura):

    arcos = (
        estrutura
        .get("geometria", {})
        .get("arcos", [])
    )

    print()
    print("=" * 80)
    print("ARCOS IDENTIFICADOS")
    print("=" * 80)

    print(
        f"Quantidade: {len(arcos)}"
    )

    for arco in arcos:

        print(
            f"  Arco {arco['id']:02d}: "
            f"R={arco['raio_mm']:.4f} mm | "
            f"erro={arco['erro_mm']:.4f} mm | "
            f"{arco['inicio']} -> {arco['fim']}"
        )


# =============================================================================
# INDICADORES
# =============================================================================

def imprimir_indicadores(estrutura):

    indicadores = estrutura.get(
        "indicadores_fabricacao",
        [],
    )

    print()
    print("=" * 80)
    print("INDICADORES DE FABRICAÇÃO")
    print("=" * 80)

    if not indicadores:

        print(
            "Nenhum indicador identificado."
        )

        return

    for indicador in indicadores:

        print(
            f"  - {indicador}"
        )


# =============================================================================
# MAIN
# =============================================================================

def main():

    print("=" * 80)
    print("TESTE ISOLADO - INTERPRETADOR DE GEOMETRIA")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. ARQUIVO
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("1. ARQUIVO DE GEOMETRIA")
    print("=" * 80)

    caminho = localizar_arquivo_geometria()

    if caminho is None:

        print()
        print(
            "ERRO - arquivo de geometria não encontrado."
        )

        print()
        print("Arquivos disponíveis:")

        arquivos = sorted(
            PASTA_DIAGNOSTICO.glob(
                "*geometria.json"
            )
        )

        if arquivos:

            for arquivo in arquivos:

                print(
                    f"  - {arquivo.name}"
                )

        else:

            print(
                "  Nenhum arquivo *_geometria.json encontrado."
            )

        return

    print()
    print("Arquivo:")
    print(caminho)

    # -------------------------------------------------------------------------
    # 2. CARREGAR
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("2. CARREGAMENTO")
    print("=" * 80)

    try:

        dados = carregar_json(
            caminho
        )

    except Exception as erro:

        print()
        print(
            "ERRO AO CARREGAR JSON:"
        )

        print(erro)

        return

    print()
    print(
        "OK - arquivo JSON carregado."
    )

    # -------------------------------------------------------------------------
    # 3. ORIGEM
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("3. DADOS DE ORIGEM")
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
    # 4. INTERPRETAR
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("4. INTERPRETAÇÃO DA GEOMETRIA")
    print("=" * 80)

    try:

        estrutura = interpretar_geometria(
            dados
        )

    except Exception as erro:

        print()
        print(
            "ERRO AO INTERPRETAR GEOMETRIA:"
        )

        print(erro)

        return

    print()
    print(
        "OK - geometria interpretada."
    )

    # -------------------------------------------------------------------------
    # 5. DIMENSÕES
    # -------------------------------------------------------------------------

    dimensoes = estrutura.get(
        "dimensoes",
        {}
    )

    print()
    print("=" * 80)
    print("5. DIMENSÕES")
    print("=" * 80)

    print()
    print(
        f"Largura: "
        f"{dimensoes.get('largura_mm', 0.0):.4f} mm"
    )

    print(
        f"Altura: "
        f"{dimensoes.get('altura_mm', 0.0):.4f} mm"
    )

    print(
        f"Orientação: "
        f"{dimensoes.get('orientacao')}"
    )

    print(
        f"Relação de aspecto: "
        f"{dimensoes.get('relacao_aspecto', 0.0):.4f}"
    )

    # -------------------------------------------------------------------------
    # 6. MÉTRICAS
    # -------------------------------------------------------------------------

    metricas = estrutura.get(
        "metricas",
        {}
    )

    print()
    print("=" * 80)
    print("6. MÉTRICAS")
    print("=" * 80)

    print()
    print(
        f"Área: "
        f"{metricas.get('area_mm2', 0.0):.4f} mm²"
    )

    print(
        f"Perímetro: "
        f"{metricas.get('perimetro_mm', 0.0):.4f} mm"
    )

    # -------------------------------------------------------------------------
    # 7. ESTATÍSTICAS
    # -------------------------------------------------------------------------

    estatisticas = estrutura.get(
        "estatisticas",
        {}
    )

    estatisticas_segmentos = (
        estatisticas.get(
            "segmentos",
            {}
        )
    )

    estatisticas_arcos = (
        estatisticas.get(
            "arcos",
            {}
        )
    )

    print()
    print("=" * 80)
    print("7. ESTATÍSTICAS DA GEOMETRIA")
    print("=" * 80)

    print()
    print(
        f"Vértices: "
        f"{estatisticas.get('quantidade_vertices', 0)}"
    )

    print(
        f"Segmentos: "
        f"{estatisticas_segmentos.get('quantidade_total', 0)}"
    )

    print(
        f"  Horizontais: "
        f"{estatisticas_segmentos.get('horizontais', 0)}"
    )

    print(
        f"  Verticais: "
        f"{estatisticas_segmentos.get('verticais', 0)}"
    )

    print(
        f"  Inclinados: "
        f"{estatisticas_segmentos.get('inclinados', 0)}"
    )

    print(
        f"Arcos: "
        f"{estatisticas_arcos.get('quantidade', 0)}"
    )

    # -------------------------------------------------------------------------
    # 8. SEGMENTOS
    # -------------------------------------------------------------------------

    imprimir_segmentos(
        estrutura
    )

    # -------------------------------------------------------------------------
    # 9. ARCOS
    # -------------------------------------------------------------------------

    imprimir_arcos(
        estrutura
    )

    # -------------------------------------------------------------------------
    # 10. RAIOS
    # -------------------------------------------------------------------------

    analise_raios = estrutura.get(
        "analise_raios",
        []
    )

    print()
    print("=" * 80)
    print("10. ANÁLISE DOS RAIOS")
    print("=" * 80)

    if not analise_raios:

        print(
            "Nenhum arco identificado."
        )

    else:

        for arco in analise_raios:

            print(
                f"Arco {arco['arco']:02d}: "
                f"R={arco['raio_mm']:.4f} mm | "
                f"{arco['classificacao']} | "
                f"erro={arco['erro_mm']:.4f} mm"
            )

    # -------------------------------------------------------------------------
    # 11. INDICADORES
    # -------------------------------------------------------------------------

    imprimir_indicadores(
        estrutura
    )

    # -------------------------------------------------------------------------
    # 12. VALIDAÇÃO
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("11. VALIDAÇÃO")
    print("=" * 80)

    vertices = (
        estrutura
        .get("geometria", {})
        .get("vertices", [])
    )

    segmentos = (
        estrutura
        .get("geometria", {})
        .get("segmentos", [])
    )

    arcos = (
        estrutura
        .get("geometria", {})
        .get("arcos", [])
    )

    if vertices:

        print(
            "OK - vértices normalizados."
        )

    else:

        print(
            "ATENÇÃO - nenhum vértice encontrado."
        )

    if segmentos:

        print(
            "OK - segmentos construídos."
        )

    else:

        print(
            "ATENÇÃO - nenhum segmento construído."
        )

    if arcos:

        print(
            "OK - arcos identificados."
        )

    else:

        print(
            "INFO - nenhum arco identificado."
        )

    # -------------------------------------------------------------------------
    # 13. RESULTADO FINAL
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("12. RESULTADO FINAL")
    print("=" * 80)

    print()
    print(
        f"Arquivo: {caminho.name}"
    )

    print(
        f"Componente: "
        f"{estrutura['origem']['componente']}"
    )

    print(
        f"Vértices: "
        f"{len(vertices)}"
    )

    print(
        f"Segmentos: "
        f"{len(segmentos)}"
    )

    print(
        f"Arcos: "
        f"{len(arcos)}"
    )

    print(
        f"Largura: "
        f"{dimensoes.get('largura_mm', 0.0):.4f} mm"
    )

    print(
        f"Altura: "
        f"{dimensoes.get('altura_mm', 0.0):.4f} mm"
    )

    print(
        f"Relação de aspecto: "
        f"{dimensoes.get('relacao_aspecto', 0.0):.4f}"
    )

    print()
    print(
        "TESTE ISOLADO DO INTERPRETADOR "
        "DE GEOMETRIA CONCLUÍDO."
    )

    print("=" * 80)


if __name__ == "__main__":
    main()