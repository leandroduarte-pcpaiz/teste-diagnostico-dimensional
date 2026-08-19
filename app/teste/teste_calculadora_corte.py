from __future__ import annotations

from pathlib import Path
import sys


RAIZ_PROJETO = Path(__file__).resolve().parents[2]

if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


from app.engineering.calculadora_corte import CalculadoraCorte


def main():

    print("=" * 80)
    print("TESTE ISOLADO - CALCULADORA DE CORTE")
    print("=" * 80)

    # ========================================================
    # 1. TESTE DE CORTE NORMAL
    # ========================================================

    print()
    print("=" * 80)
    print("1. TESTE DE CORTE NORMAL")
    print("=" * 80)

    calculadora = CalculadoraCorte(
        codigo_peca="G2005887",
        material="ACO_A36",
        espessura_mm=6.35,
        largura_peca_mm=500,
        comprimento_peca_mm=1000,
        quantidade=20,
        largura_chapa_mm=2000,
        comprimento_chapa_mm=6000,
    )

    resultado = calculadora.calcular()

    print()

    for chave, valor in resultado.items():
        print(f"{chave}: {valor}")

    # ========================================================
    # 2. VALIDAR QUANTIDADE POR CHAPA
    # ========================================================

    print()
    print("=" * 80)
    print("2. VALIDANDO QUANTIDADE POR CHAPA")
    print("=" * 80)

    if resultado["pecas_por_chapa"] != 24:
        raise ValueError(
            "Quantidade por chapa incorreta. "
            f"Esperado: 24 | "
            f"Obtido: {resultado['pecas_por_chapa']}"
        )

    print("OK - 24 peças por chapa.")

    # ========================================================
    # 3. VALIDAR CHAPAS NECESSÁRIAS
    # ========================================================

    print()
    print("=" * 80)
    print("3. VALIDANDO CHAPAS NECESSÁRIAS")
    print("=" * 80)

    if resultado["chapas_necessarias"] != 1:
        raise ValueError(
            "Quantidade de chapas incorreta. "
            f"Esperado: 1 | "
            f"Obtido: {resultado['chapas_necessarias']}"
        )

    print("OK - 1 chapa necessária.")

    # ========================================================
    # 4. VALIDAR PEÇAS PRODUZIDAS
    # ========================================================

    print()
    print("=" * 80)
    print("4. VALIDANDO PEÇAS PRODUZIDAS")
    print("=" * 80)

    if resultado["pecas_produzidas"] != 24:
        raise ValueError(
            "Quantidade produzida incorreta. "
            f"Esperado: 24 | "
            f"Obtido: {resultado['pecas_produzidas']}"
        )

    print("OK - 24 posições de corte.")

    # ========================================================
    # 5. VALIDAR SOBRA
    # ========================================================

    print()
    print("=" * 80)
    print("5. VALIDANDO SOBRA")
    print("=" * 80)

    if resultado["pecas_sobrando"] != 4:
        raise ValueError(
            "Quantidade sobrando incorreta. "
            f"Esperado: 4 | "
            f"Obtido: {resultado['pecas_sobrando']}"
        )

    print("OK - 4 posições sobrando.")

    # ========================================================
    # 6. VALIDAR ORIENTAÇÃO
    # ========================================================

    print()
    print("=" * 80)
    print("6. VALIDANDO ORIENTAÇÃO")
    print("=" * 80)

    if resultado["orientacao"] not in {
        "0 graus",
        "90 graus",
    }:
        raise ValueError(
            "Orientação inválida: "
            f"{resultado['orientacao']}"
        )

    print(
        f"OK - orientação selecionada: "
        f"{resultado['orientacao']}"
    )

    # ========================================================
    # 7. VALIDAR APROVEITAMENTO
    # ========================================================

    print()
    print("=" * 80)
    print("7. VALIDANDO APROVEITAMENTO")
    print("=" * 80)

    aproveitamento_necessidade = resultado[
        "aproveitamento_necessidade_percentual"
    ]

    aproveitamento_chapa = resultado[
        "aproveitamento_chapa_percentual"
    ]

    print(
        "Aproveitamento da necessidade: "
        f"{aproveitamento_necessidade:.2f}%"
    )

    print(
        "Aproveitamento geométrico da chapa: "
        f"{aproveitamento_chapa:.2f}%"
    )

    if aproveitamento_necessidade <= 0:
        raise ValueError(
            "Aproveitamento da necessidade inválido."
        )

    if aproveitamento_chapa <= 0:
        raise ValueError(
            "Aproveitamento da chapa inválido."
        )

    print("OK - aproveitamentos calculados.")

    # ========================================================
    # 8. TESTE DE PEÇA QUE NÃO CABE
    # ========================================================

    print()
    print("=" * 80)
    print("8. TESTE DE PEÇA QUE NÃO CABE")
    print("=" * 80)

    calculadora_invalida = CalculadoraCorte(
        codigo_peca="TESTE_NAO_CABE",
        material="ACO_A36",
        espessura_mm=6.35,
        largura_peca_mm=2500,
        comprimento_peca_mm=7000,
        quantidade=1,
        largura_chapa_mm=2000,
        comprimento_chapa_mm=6000,
    )

    resultado_invalido = (
        calculadora_invalida.calcular()
    )

    print()

    for chave, valor in resultado_invalido.items():
        print(f"{chave}: {valor}")

    if resultado_invalido["pecas_por_chapa"] != 0:
        raise ValueError(
            "A calculadora deveria identificar "
            "que a peça não cabe na chapa."
        )

    if resultado_invalido["erro"] is None:
        raise ValueError(
            "A calculadora não informou erro "
            "para peça que não cabe."
        )

    print(
        "OK - peça maior que a chapa foi "
        "identificada corretamente."
    )

    # ========================================================
    # 9. RESULTADO FINAL
    # ========================================================

    print()
    print("=" * 80)
    print("RESULTADO FINAL DO TESTE")
    print("=" * 80)

    print("Teste normal:              OK")
    print("Quantidade por chapa:      OK")
    print("Chapas necessárias:        OK")
    print("Peças produzidas:          OK")
    print("Sobra:                      OK")
    print("Orientação:                OK")
    print("Aproveitamento:            OK")
    print("Peça que não cabe:         OK")

    print()
    print("=" * 80)
    print("TESTE DA CALCULADORA DE CORTE CONCLUÍDO")
    print("=" * 80)


if __name__ == "__main__":
    main()