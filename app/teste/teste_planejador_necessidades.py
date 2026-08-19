from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


# ============================================================
# RAIZ DO PROJETO
# ============================================================

RAIZ_PROJETO = Path(__file__).resolve().parents[2]

if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


# ============================================================
# IMPORTAÇÕES
# ============================================================

from app.importadores.importador_totvs import importar_csv
from app.engineering.explosao_bom import ExplosaoBOM
from app.engineering.motor_engenharia import MotorEngenharia
from app.engineering.planejador_necessidades import (
    PlanejadorNecessidades,
)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ARQUIVO_BOM = (
    RAIZ_PROJETO
    / "data"
    / "estrutura_de_i3001192_ate_i3001192.csv"
)

ARQUIVO_CADASTRO = (
    RAIZ_PROJETO
    / "data"
    / "cadastro_produtos.xlsx"
)

PRODUTO = "I3001192"

QUANTIDADE_PRODUZIR = 10


# ============================================================
# TESTE
# ============================================================

def main():

    print("=" * 80)
    print("TESTE ISOLADO - PLANEJADOR DE NECESSIDADES")
    print("=" * 80)

    print()
    print(f"Produto: {PRODUTO}")
    print(f"Quantidade a produzir: {QUANTIDADE_PRODUZIR}")

    # ========================================================
    # 1. BOM
    # ========================================================

    print()
    print("=" * 80)
    print("1. IMPORTANDO BOM")
    print("=" * 80)

    df_bom = importar_csv(
        ARQUIVO_BOM
    )

    if df_bom is None or df_bom.empty:
        raise RuntimeError(
            "BOM não carregada."
        )

    print(
        f"Linhas da BOM: {len(df_bom)}"
    )

    # ========================================================
    # 2. EXPLOSÃO
    # ========================================================

    print()
    print("=" * 80)
    print("2. EXPLOSÃO")
    print("=" * 80)

    explosao = ExplosaoBOM(
        df_bom
    )

    df_explosao = explosao.explodir(
        PRODUTO,
        quantidade=1,
    )

    if not isinstance(
        df_explosao,
        pd.DataFrame,
    ):
        df_explosao = pd.DataFrame(
            df_explosao
        )

    print(
        f"Componentes: {len(df_explosao)}"
    )

    # ========================================================
    # 3. MOTOR DE ENGENHARIA
    # ========================================================

    print()
    print("=" * 80)
    print("3. MOTOR DE ENGENHARIA")
    print("=" * 80)

    motor = MotorEngenharia(
        caminho_cadastro=ARQUIVO_CADASTRO
    )

    df_classificado = motor.enriquecer(
        df_explosao
    )

    print(
        f"Componentes classificados: "
        f"{len(df_classificado)}"
    )

    # ========================================================
    # 4. PLANEJADOR
    # ========================================================

    print()
    print("=" * 80)
    print("4. PLANEJADOR DE NECESSIDADES")
    print("=" * 80)

    planejador = PlanejadorNecessidades(
        resultado_classificado=df_classificado,
        quantidade_conjuntos=QUANTIDADE_PRODUZIR,
    )

    df_necessidades = planejador.planejar()

    if not isinstance(
        df_necessidades,
        pd.DataFrame,
    ):
        df_necessidades = pd.DataFrame(
            df_necessidades
        )

    print()
    print(
        f"Itens na necessidade: "
        f"{len(df_necessidades)}"
    )

    # ========================================================
    # 5. VALIDAR COLUNAS
    # ========================================================

    print()
    print("=" * 80)
    print("5. VALIDANDO COLUNAS")
    print("=" * 80)

    obrigatorias = [
        "componente",
        "DESCRICAO_PRODUTO",
        "CLASSIFICACAO",
        "UNIDADE_MEDIDA",
        "quantidade_conjunto",
        "quantidade_necessaria",
        "NECESSIDADE_TOTAL",
    ]

    faltantes = [
        coluna
        for coluna in obrigatorias
        if coluna not in df_necessidades.columns
    ]

    if faltantes:

        raise ValueError(
            "Colunas obrigatórias ausentes:\n"
            + "\n".join(
                f"- {coluna}"
                for coluna in faltantes
            )
        )

    print(
        "OK - todas as colunas obrigatórias existem."
    )

    # ========================================================
    # 6. TESTE DE MULTIPLICAÇÃO
    # ========================================================

    print()
    print("=" * 80)
    print("6. VALIDANDO MULTIPLICAÇÃO")
    print("=" * 80)

    df_necessidades["esperado"] = (
        df_necessidades[
            "quantidade_conjunto"
        ]
        * QUANTIDADE_PRODUZIR
    )

    diferencas = (
        (
            df_necessidades[
                "quantidade_necessaria"
            ]
            - df_necessidades["esperado"]
        )
        .abs()
        > 0.000001
    )

    quantidade_erros = int(
        diferencas.sum()
    )

    if quantidade_erros:

        print(
            f"ERRO: {quantidade_erros} "
            "itens possuem multiplicação incorreta."
        )

        print()

        print(
            df_necessidades.loc[
                diferencas,
                [
                    "componente",
                    "quantidade_conjunto",
                    "quantidade_necessaria",
                    "esperado",
                ],
            ]
            .head(20)
            .to_string(index=False)
        )

        raise ValueError(
            "Falha na validação da multiplicação."
        )

    print(
        "OK - multiplicação correta."
    )

    # ========================================================
    # 7. TESTE ESPECÍFICO G2005887
    # ========================================================

    print()
    print("=" * 80)
    print("7. VALIDANDO G2005887")
    print("=" * 80)

    alvo = df_necessidades[
        df_necessidades[
            "componente"
        ]
        == "G2005887"
    ]

    if alvo.empty:

        print(
            "ATENÇÃO: G2005887 não encontrado."
        )

    else:

        linha = alvo.iloc[0]

        quantidade_conjunto = float(
            linha[
                "quantidade_conjunto"
            ]
        )

        quantidade_necessaria = float(
            linha[
                "quantidade_necessaria"
            ]
        )

        esperado = (
            quantidade_conjunto
            * QUANTIDADE_PRODUZIR
        )

        print(
            f"Componente: G2005887"
        )

        print(
            f"Quantidade por conjunto: "
            f"{quantidade_conjunto:.3f}"
        )

        print(
            f"Quantidade necessária: "
            f"{quantidade_necessaria:.3f}"
        )

        print(
            f"Esperado: "
            f"{esperado:.3f}"
        )

        if abs(
            quantidade_necessaria - esperado
        ) > 0.000001:

            raise ValueError(
                "G2005887 possui quantidade incorreta."
            )

        print(
            "OK - G2005887 calculado corretamente."
        )

    # ========================================================
    # 8. RESUMO
    # ========================================================

    print()
    print("=" * 80)
    print("8. RESUMO POR CLASSIFICAÇÃO")
    print("=" * 80)

    resumo = (
        df_necessidades
        .groupby(
            [
                "CLASSIFICACAO",
                "UNIDADE_MEDIDA",
            ],
            dropna=False,
        )
        .agg(
            quantidade_itens=(
                "componente",
                "nunique",
            ),
            quantidade_total=(
                "quantidade_necessaria",
                "sum",
            ),
        )
        .reset_index()
    )

    print(
        resumo.to_string(
            index=False
        )
    )

    # ========================================================
    # 9. TOTAL
    # ========================================================

    total = float(
        df_necessidades[
            "quantidade_necessaria"
        ]
        .sum()
    )

    print()
    print("=" * 80)
    print("9. TOTAL DA NECESSIDADE")
    print("=" * 80)

    print(
        f"Quantidade total: {total:.4f}"
    )

    # ========================================================
    # 10. AMOSTRA
    # ========================================================

    print()
    print("=" * 80)
    print("10. AMOSTRA DA NECESSIDADE")
    print("=" * 80)

    colunas = [
        "componente",
        "DESCRICAO_PRODUTO",
        "CLASSIFICACAO",
        "UNIDADE_MEDIDA",
        "quantidade_conjunto",
        "quantidade_necessaria",
    ]

    print(
        df_necessidades[
            colunas
        ]
        .head(20)
        .to_string(index=False)
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()
    print("=" * 80)
    print("TESTE DO PLANEJADOR CONCLUÍDO COM SUCESSO")
    print("=" * 80)


if __name__ == "__main__":
    main()