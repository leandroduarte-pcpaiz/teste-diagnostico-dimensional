from __future__ import annotations

import sys
from pathlib import Path


# ==============================================================
# GARANTE QUE O PROJETO SEJA ENCONTRADO PELO PYTHON
# ==============================================================

RAIZ_PROJETO = Path(__file__).resolve().parents[2]

if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


from app.engineering.calculadora_desenvolvimento import (
    CalculadoraDesenvolvimento,
)


def imprimir_linha():
    print("=" * 80)


def validar(condicao, mensagem_ok, mensagem_erro):
    if condicao:
        print(f"OK - {mensagem_ok}")
        return True

    print(f"ERRO - {mensagem_erro}")
    return False


def main():

    imprimir_linha()
    print(
        "TESTE ISOLADO - CALCULADORA DE DESENVOLVIMENTO"
    )
    imprimir_linha()

    # ==========================================================
    # DADOS REAIS DO DESENHO I1044988
    # ==========================================================

    codigo_peca = "I1044988"
    materia_prima = "G2005887"
    material = "CH AÇO ASTM A36"

    espessura_mm = 6.35

    dimensoes_geometricas = [
        672.0,
        163.0,
        80.0,
        55.0,
        48.25,
    ]

    dobras = [
        {
            "angulo_graus": 90,
            "direcao": "PARA CIMA",
            "raio_mm": 10.0,
        },
        {
            "angulo_graus": 90,
            "direcao": "PARA CIMA",
            "raio_mm": 10.0,
        },
    ]

    k_factor = 0.33

    # ==========================================================
    # 1. DADOS DO TESTE
    # ==========================================================

    print()
    print("1. DADOS DO DESENHO")
    print()

    print(f"Código da peça: {codigo_peca}")
    print(f"Matéria-prima: {materia_prima}")
    print(f"Material: {material}")
    print(f"Espessura: {espessura_mm} mm")

    print()
    print("Dimensões geométricas:")
    print(dimensoes_geometricas)

    print()
    print("Dobras:")

    for indice, dobra in enumerate(
        dobras,
        start=1,
    ):
        print(
            f"  Dobra {indice}: "
            f"{dobra['angulo_graus']}° "
            f"{dobra['direcao']} "
            f"R{dobra['raio_mm']} mm"
        )

    # ==========================================================
    # 2. CRIAR CALCULADORA
    # ==========================================================

    print()
    print("2. CRIANDO CALCULADORA")
    print()

    calculadora = CalculadoraDesenvolvimento(
        espessura_mm=espessura_mm,
        dobras=dobras,
        k_factor=k_factor,
    )

    print("Objeto CalculadoraDesenvolvimento criado.")

    # ==========================================================
    # 3. VALIDAR DADOS
    # ==========================================================

    print()
    print("3. VALIDAÇÃO DOS DADOS")
    print()

    validacao = calculadora.validar()

    print(
        f"Dados válidos: "
        f"{validacao['valido']}"
    )

    if validacao["erros"]:

        print()
        print("Erros encontrados:")

        for erro in validacao["erros"]:
            print(f"  - {erro}")

    validar(
        validacao["valido"],
        "dados do cálculo são válidos.",
        "dados do cálculo são inválidos.",
    )

    # ==========================================================
    # 4. TESTAR BEND ALLOWANCE
    # ==========================================================

    print()
    print("4. TESTE DE BEND ALLOWANCE")
    print()

    ba_1 = calculadora.calcular_bend_allowance(
        angulo_graus=90,
        raio_mm=10,
    )

    print(
        f"BA para 90° R10: "
        f"{ba_1:.4f} mm"
    )

    esperado_ba = (
        3.141592653589793 / 2
    ) * (
        10
        + (
            0.33
            * 6.35
        )
    )

    validar(
        abs(ba_1 - esperado_ba) < 0.0001,
        "Bend Allowance calculado corretamente.",
        "Bend Allowance diferente do esperado.",
    )

    # ==========================================================
    # 5. TESTAR BEND DEDUCTION
    # ==========================================================

    print()
    print("5. TESTE DE BEND DEDUCTION")
    print()

    bd_1 = calculadora.calcular_bend_deduction(
        angulo_graus=90,
        raio_mm=10,
    )

    print(
        f"BD para 90° R10: "
        f"{bd_1:.4f} mm"
    )

    validar(
        bd_1 > 0,
        "Bend Deduction calculado.",
        "Bend Deduction não foi calculado.",
    )

    # ==========================================================
    # 6. ANALISAR AS DOBRAS
    # ==========================================================

    print()
    print("6. ANÁLISE DAS DOBRAS")
    print()

    analise_dobras = (
        calculadora.analisar_dobras()
    )

    print(
        f"Quantidade de dobras analisadas: "
        f"{len(analise_dobras)}"
    )

    for dobra in analise_dobras:

        print()

        print(
            f"Dobra {dobra['numero_dobra']}"
        )

        print(
            f"  Ângulo: "
            f"{dobra['angulo_graus']}°"
        )

        print(
            f"  Direção: "
            f"{dobra['direcao']}"
        )

        print(
            f"  Raio: "
            f"{dobra['raio_mm']} mm"
        )

        print(
            f"  Bend Allowance: "
            f"{dobra['bend_allowance_mm']} mm"
        )

        print(
            f"  Bend Deduction: "
            f"{dobra['bend_deduction_mm']} mm"
        )

    validar(
        len(analise_dobras) == 2,
        "as 2 dobras foram analisadas.",
        "a quantidade de dobras analisadas está incorreta.",
    )

    # ==========================================================
    # 7. SOMA DAS DOBRAS
    # ==========================================================

    print()
    print("7. TOTAIS DAS DOBRAS")
    print()

    ba_total = sum(
        dobra["bend_allowance_mm"]
        for dobra in analise_dobras
    )

    bd_total = sum(
        dobra["bend_deduction_mm"]
        for dobra in analise_dobras
    )

    print(
        f"Bend Allowance total: "
        f"{ba_total:.4f} mm"
    )

    print(
        f"Bend Deduction total: "
        f"{bd_total:.4f} mm"
    )

    validar(
        ba_total > 0,
        "BA total calculado.",
        "BA total inválido.",
    )

    validar(
        bd_total > 0,
        "BD total calculado.",
        "BD total inválido.",
    )

    # ==========================================================
    # 8. TESTE COM SEGMENTOS EXPLÍCITOS
    # ==========================================================

    print()
    print("8. TESTE DE DESENVOLVIMENTO COM SEGMENTOS")
    print()

    segmentos_teste = [
        500.0,
        100.0,
        50.0,
    ]

    resultado_segmentos = (
        calculadora.calcular_desenvolvimento_linear(
            segmentos_teste
        )
    )

    print(
        f"Segmentos: "
        f"{segmentos_teste}"
    )

    print(
        f"Comprimento dos segmentos: "
        f"{resultado_segmentos.get('comprimento_segmentos_mm')} mm"
    )

    print(
        f"BA total: "
        f"{resultado_segmentos.get('bend_allowance_total_mm')} mm"
    )

    print(
        f"Desenvolvimento: "
        f"{resultado_segmentos.get('desenvolvimento_mm')} mm"
    )

    esperado_desenvolvimento = (
        sum(segmentos_teste)
        + ba_total
    )

    validar(
        abs(
            resultado_segmentos.get(
                "desenvolvimento_mm"
            )
            - esperado_desenvolvimento
        ) < 0.001,
        "desenvolvimento com segmentos calculado corretamente.",
        "desenvolvimento com segmentos incorreto.",
    )

    # ==========================================================
    # 9. TESTE COM DIMENSÃO TOTAL
    # ==========================================================

    print()
    print("9. TESTE COM DIMENSÃO TOTAL")
    print()

    resultado_total = (
        calculadora.calcular_a_partir_de_comprimento_total(
            672.0
        )
    )

    print(
        f"Comprimento informado: "
        f"{resultado_total.get('comprimento_total_mm')} mm"
    )

    print(
        f"BA total: "
        f"{resultado_total.get('bend_allowance_total_mm')} mm"
    )

    print(
        f"BD total: "
        f"{resultado_total.get('bend_deduction_total_mm')} mm"
    )

    print(
        f"Status: "
        f"{resultado_total.get('status')}"
    )

    validar(
        resultado_total.get("status")
        == "ANALISE",
        "dimensão total analisada sem alterar a geometria.",
        "análise da dimensão total falhou.",
    )

    # ==========================================================
    # 10. TESTE REAL DO DESENHO
    # ==========================================================

    print()
    print("10. TESTE REAL - I1044988")
    print()

    dados_desenho = {
        "codigo_peca": codigo_peca,
        "materia_prima": materia_prima,
        "material": material,
        "espessura_mm": espessura_mm,
        "dimensoes_geometricas_mm": (
            dimensoes_geometricas
        ),
        "dobras": dobras,
    }

    resultado_desenho = (
        CalculadoraDesenvolvimento.analisar_desenho(
            dados_desenho,
            k_factor=k_factor,
        )
    )

    print(
        f"Código: "
        f"{resultado_desenho.get('codigo_peca')}"
    )

    print(
        f"Matéria-prima: "
        f"{resultado_desenho.get('materia_prima')}"
    )

    print(
        f"Espessura: "
        f"{resultado_desenho.get('espessura_mm')} mm"
    )

    print(
        f"K-factor: "
        f"{resultado_desenho.get('k_factor')}"
    )

    print(
        f"Quantidade de dobras: "
        f"{resultado_desenho.get('quantidade_dobras')}"
    )

    print(
        f"Dimensões extraídas: "
        f"{resultado_desenho.get('dimensoes_geometricas_mm')}"
    )

    print(
        f"Status: "
        f"{resultado_desenho.get('status')}"
    )

    print(
        f"BLANK: "
        f"{resultado_desenho.get('blank')}"
    )

    # ==========================================================
    # 11. VALIDAÇÃO MAIS IMPORTANTE
    # ==========================================================

    print()
    print("11. VALIDAÇÃO DE SEGURANÇA GEOMÉTRICA")
    print()

    status = resultado_desenho.get(
        "status"
    )

    blank = resultado_desenho.get(
        "blank"
    )

    # O desenho possui dimensões, mas ainda não
    # informamos quais são os segmentos do desenvolvimento.
    #
    # Portanto o sistema NÃO pode inventar um blank.

    validar(
        status == "GEOMETRIA_INSUFICIENTE",
        "o sistema não inventou um BLANK a partir das dimensões extraídas.",
        "o sistema gerou um BLANK sem geometria suficiente.",
    )

    validar(
        blank is None,
        "BLANK permanece indefinido até a geometria ser interpretada.",
        "BLANK foi definido indevidamente.",
    )

    # ==========================================================
    # 12. RESULTADO FINAL
    # ==========================================================

    print()
    imprimir_linha()
    print(
        "RESULTADO FINAL DO TESTE"
    )
    imprimir_linha()

    print(
        f"Código da peça:          {codigo_peca}"
    )

    print(
        f"Matéria-prima:           {materia_prima}"
    )

    print(
        f"Espessura:               {espessura_mm} mm"
    )

    print(
        f"K-factor:                {k_factor}"
    )

    print(
        f"Dobras:                  {len(dobras)}"
    )

    print(
        f"BA total:                {ba_total:.4f} mm"
    )

    print(
        f"BD total:                {bd_total:.4f} mm"
    )

    print(
        f"Status do desenho:       {status}"
    )

    print(
        f"BLANK:                   {blank}"
    )

    print()

    print(
        "IMPORTANTE:"
    )

    print(
        "O BLANK NÃO foi calculado automaticamente "
        "a partir de 672 x 163 x 80 x 55 x 48,25 mm."
    )

    print(
        "Isso é intencional."
    )

    print(
        "A próxima etapa será interpretar a geometria "
        "das abas e linhas de dobra para determinar "
        "o desenvolvimento real."
    )

    imprimir_linha()

    print(
        "TESTE DA CALCULADORA DE DESENVOLVIMENTO CONCLUÍDO."
    )

    imprimir_linha()


if __name__ == "__main__":
    main()