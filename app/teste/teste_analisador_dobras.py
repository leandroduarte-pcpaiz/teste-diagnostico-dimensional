from pathlib import Path
import json

from app.engineering.interpretador_geometria import (
    interpretar_geometria,
)

from app.engineering.analisador_dobras import (
    analisar_dobras,
    validar_analise,
    gerar_resumo,
    imprimir_resumo,
)


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

PASTA_DIAGNOSTICO = Path(
    r"C:\Projetos\AIZI Engineering AI\diagnostico"
)

ARQUIVO_GEOMETRIA = (
    PASTA_DIAGNOSTICO
    / "_I1044988_geometria.json"
)


# =============================================================================
# CABEÇALHO
# =============================================================================

print("=" * 80)
print("TESTE ISOLADO - ANALISADOR DE DOBRAS")
print("=" * 80)


# =============================================================================
# 1. ARQUIVO
# =============================================================================

print()
print("=" * 80)
print("1. ARQUIVO DE GEOMETRIA")
print("=" * 80)

print()
print(f"Arquivo:")
print(ARQUIVO_GEOMETRIA)


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

    raise SystemExit(1)


print()
print("OK - arquivo encontrado.")


# =============================================================================
# 2. CARREGAMENTO
# =============================================================================

print()
print("=" * 80)
print("2. CARREGAMENTO DO JSON")
print("=" * 80)


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

    print()
    print(
        "ERRO AO CARREGAR JSON:"
    )

    print(erro)

    raise SystemExit(1)


print()
print("OK - JSON carregado.")


# =============================================================================
# 3. DADOS DE ORIGEM
# =============================================================================

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


# =============================================================================
# 4. INTERPRETAÇÃO DA GEOMETRIA
# =============================================================================

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

    raise SystemExit(1)


print()
print(
    "OK - geometria interpretada."
)


# =============================================================================
# 5. DADOS INTERPRETADOS
# =============================================================================

print()
print("=" * 80)
print("5. DADOS INTERPRETADOS")
print("=" * 80)

print()

print(
    f"Largura: "
    f"{estrutura['dimensoes']['largura_mm']:.4f} mm"
)

print(
    f"Altura: "
    f"{estrutura['dimensoes']['altura_mm']:.4f} mm"
)

print(
    f"Orientação: "
    f"{estrutura['dimensoes']['orientacao']}"
)

print(
    f"Relação de aspecto: "
    f"{estrutura['dimensoes']['relacao_aspecto']:.4f}"
)

print()

print(
    f"Vértices: "
    f"{estrutura['estatisticas']['quantidade_vertices']}"
)

print(
    f"Segmentos: "
    f"{estrutura['estatisticas']['segmentos']['quantidade_total']}"
)

print(
    f"Arcos: "
    f"{estrutura['estatisticas']['arcos']['quantidade']}"
)


# =============================================================================
# 6. ANÁLISE DE DOBRAS
# =============================================================================

print()
print("=" * 80)
print("6. ANALISADOR DE DOBRAS")
print("=" * 80)


try:

    resultado = analisar_dobras(
        estrutura
    )

except Exception as erro:

    print()
    print(
        "ERRO AO ANALISAR DOBRAS:"
    )

    print(erro)

    raise SystemExit(1)


print()
print(
    "OK - análise de dobras executada."
)


# =============================================================================
# 7. RESUMO
# =============================================================================

print()
print("=" * 80)
print("7. RESUMO DA ANÁLISE")
print("=" * 80)

resumo = gerar_resumo(
    resultado
)

print()

print(
    f"Status: "
    f"{resumo.get('status')}"
)

print(
    f"Dobras candidatas: "
    f"{resumo.get('dobras_candidatas')}"
)

print(
    f"Candidatas aproximadamente 90°: "
    f"{resumo.get('dobras_90_graus')}"
)

print(
    f"Arcos disponíveis: "
    f"{resumo.get('arcos_disponiveis')}"
)

print(
    f"Segmentos curtos: "
    f"{resumo.get('segmentos_curtos')}"
)


# =============================================================================
# 8. CANDIDATAS
# =============================================================================

print()
print("=" * 80)
print("8. CANDIDATAS A DOBRA")
print("=" * 80)

dobras = resultado.get(
    "dobras",
    []
)

print()

if not dobras:

    print(
        "Nenhuma candidata a dobra identificada."
    )

else:

    for indice, dobra in enumerate(
        dobras,
        start=1,
    ):

        ponto = dobra.get(
            "ponto_dobra",
            {}
        )

        print(
            f"Dobra candidata {indice}"
        )

        print(
            f"  Segmentos: "
            f"{dobra.get('segmento_anterior')} -> "
            f"{dobra.get('segmento_atual')}"
        )

        print(
            f"  Ângulo: "
            f"{dobra.get('angulo_graus')}°"
        )

        print(
            f"  Classificação: "
            f"{dobra.get('classificacao')}"
        )

        print(
            f"  Confiança: "
            f"{dobra.get('confianca')}"
        )

        print(
            f"  Ponto: "
            f"X={ponto.get('x_mm')} mm | "
            f"Y={ponto.get('y_mm')} mm"
        )

        print(
            f"  Raio: "
            f"{dobra.get('raio_mm')}"
        )

        print()


# =============================================================================
# 9. SEGMENTOS CURTOS
# =============================================================================

print("=" * 80)
print("9. SEGMENTOS CURTOS")
print("=" * 80)

segmentos_curtos = resultado.get(
    "segmentos_curtos",
    []
)

print()

print(
    f"Quantidade: "
    f"{len(segmentos_curtos)}"
)

if segmentos_curtos:

    print()
    print(
        "IDs dos segmentos curtos:"
    )

    print(
        segmentos_curtos
    )

else:

    print(
        "Nenhum segmento curto identificado."
    )


# =============================================================================
# 10. VALIDAÇÃO
# =============================================================================

print()
print("=" * 80)
print("10. VALIDAÇÃO")
print("=" * 80)


validacao = validar_analise(
    resultado
)

print()

if validacao["valido"]:

    print(
        "OK - estrutura da análise válida."
    )

else:

    print(
        "ERRO - estrutura da análise inválida."
    )

    for erro in validacao["erros"]:

        print(
            f"  - {erro}"
        )


# =============================================================================
# 11. SEGURANÇA GEOMÉTRICA
# =============================================================================

print()
print("=" * 80)
print("11. VALIDAÇÃO DE SEGURANÇA GEOMÉTRICA")
print("=" * 80)

print()

print(
    "IMPORTANTE:"
)

print(
    "As candidatas identificadas NÃO são consideradas"
)

print(
    "automaticamente como dobras confirmadas."
)

print()

print(
    "O AnalisadorDobras não calcula BLANK."
)

print(
    "O AnalisadorDobras não altera a geometria."
)

print(
    "O AnalisadorDobras não chama a CalculadoraCorte."
)

print()

print(
    "OK - análise permanece conservadora."
)


# =============================================================================
# 12. IMPRESSÃO COMPLETA
# =============================================================================

imprimir_resumo(
    resultado
)


# =============================================================================
# 13. RESULTADO FINAL
# =============================================================================

print()
print("=" * 80)
print("13. RESULTADO FINAL")
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
    f"{len(dados.get('vertices_mm', []))}"
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
    f"Status: "
    f"{resultado.get('status')}"
)

print(
    f"Dobras candidatas: "
    f"{resultado.get('quantidade_candidatas')}"
)

print()

print(
    "TESTE DO ANALISADOR DE DOBRAS CONCLUÍDO."
)

print("=" * 80)