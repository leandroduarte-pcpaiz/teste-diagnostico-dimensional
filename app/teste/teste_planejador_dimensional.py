from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


RAIZ_PROJETO = Path(__file__).resolve().parents[2]

if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


from app.importadores.importador_totvs import importar_csv
from app.engineering.explosao_bom import ExplosaoBOM
from app.engineering.motor_engenharia import MotorEngenharia
from app.engineering.planejador_necessidades import (
    PlanejadorNecessidades,
)
from app.engineering.planejador_dimensional import (
    PlanejadorDimensional,
)


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


def main():

    print("=" * 80)
    print("TESTE ISOLADO - PLANEJADOR DIMENSIONAL")
    print("=" * 80)

    # ========================================================
    # 1. IMPORTAÇÃO
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
    # 3. MOTOR
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
    # 4. NECESSIDADES
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

    print(
        f"Itens na necessidade: "
        f"{len(df_necessidades)}"
    )

    # ========================================================
    # 5. PLANEJADOR DIMENSIONAL
    # ========================================================

    print()
    print("=" * 80)
    print("5. PLANEJADOR DIMENSIONAL")
    print("=" * 80)

    dimensional = PlanejadorDimensional(
        df_necessidades
    )

    print(
        "Objeto PlanejadorDimensional criado."
    )

    # --------------------------------------------------------
    # VERIFICA MÉTODO ANALISAR
    # --------------------------------------------------------

    if not hasattr(
        dimensional,
        "analisar",
    ):

        raise AttributeError(
            "PlanejadorDimensional não possui "
            "o método analisar()."
        )

    print(
        "Método analisar(): encontrado."
    )

    # --------------------------------------------------------
    # EXECUTA ANÁLISE
    # --------------------------------------------------------

    df_dimensional = (
        dimensional.analisar()
    )

    if not isinstance(
        df_dimensional,
        pd.DataFrame,
    ):

        df_dimensional = pd.DataFrame(
            df_dimensional
        )

    print(
        f"Itens analisados: "
        f"{len(df_dimensional)}"
    )

    # ========================================================
    # 6. VALIDAR PRESERVAÇÃO
    # ========================================================

    print()
    print("=" * 80)
    print("6. VALIDANDO PRESERVAÇÃO DOS ITENS")
    print("=" * 80)

    if len(df_dimensional) != len(
        df_necessidades
    ):

        raise ValueError(
            "O Planejador Dimensional alterou "
            "a quantidade de itens.\n"
            f"Necessidades: {len(df_necessidades)}\n"
            f"Dimensional: {len(df_dimensional)}"
        )

    print(
        "OK - os 230 itens foram preservados."
    )

    # ========================================================
    # 7. VALIDAR COMPONENTE
    # ========================================================

    print()
    print("=" * 80)
    print("7. VALIDANDO COMPONENTES")
    print("=" * 80)

    if "componente" not in df_dimensional.columns:

        raise ValueError(
            "Planejador Dimensional removeu "
            "a coluna 'componente'."
        )

    print(
        "OK - coluna componente preservada."
    )

    # ========================================================
    # 8. VALIDAR QUANTIDADE
    # ========================================================

    print()
    print("=" * 80)
    print("8. VALIDANDO NECESSIDADE")
    print("=" * 80)

    if (
        "quantidade_necessaria"
        not in df_dimensional.columns
    ):

        raise ValueError(
            "Planejador Dimensional não preservou "
            "quantidade_necessaria."
        )

    total_dimensional = float(
        pd.to_numeric(
            df_dimensional[
                "quantidade_necessaria"
            ],
            errors="coerce",
        )
        .fillna(0)
        .sum()
    )

    total_necessidades = float(
        df_necessidades[
            "quantidade_necessaria"
        ]
        .sum()
    )

    print(
        f"Total necessidades: "
        f"{total_necessidades:.4f}"
    )

    print(
        f"Total dimensional: "
        f"{total_dimensional:.4f}"
    )

    if abs(
        total_dimensional
        - total_necessidades
    ) > 0.000001:

        raise ValueError(
            "Planejador Dimensional alterou "
            "as quantidades."
        )

    print(
        "OK - quantidades preservadas."
    )

    # ========================================================
    # 9. TIPOS DIMENSIONAIS
    # ========================================================

    print()
    print("=" * 80)
    print("9. TIPOS DIMENSIONAIS")
    print("=" * 80)

    if "tipo_dimensional" not in df_dimensional.columns:

        raise ValueError(
            "Planejador Dimensional não produziu "
            "tipo_dimensional."
        )

    resumo_tipos = (
        df_dimensional[
            "tipo_dimensional"
        ]
        .fillna("NAO_INFORMADO")
        .astype(str)
        .str.upper()
        .str.strip()
        .value_counts()
        .rename_axis(
            "tipo_dimensional"
        )
        .reset_index(
            name="quantidade_itens"
        )
    )

    print(
        resumo_tipos.to_string(
            index=False
        )
    )

    # ========================================================
    # 10. COLUNAS DIMENSIONAIS
    # ========================================================

    print()
    print("=" * 80)
    print("10. COLUNAS DIMENSIONAIS")
    print("=" * 80)

    colunas = [
        "componente",
        "DESCRICAO_PRODUTO",
        "CLASSIFICACAO",
        "UNIDADE_MEDIDA",
        "quantidade_necessaria",
        "tipo_dimensional",
        "espessura_mm",
        "diametro_externo_mm",
        "largura_padrao_mm",
        "comprimento_padrao_mm",
    ]

    for coluna in colunas:

        if coluna not in df_dimensional.columns:

            print(
                f"ATENÇÃO - coluna ausente: "
                f"{coluna}"
            )

    colunas_existentes = [
        coluna
        for coluna in colunas
        if coluna in df_dimensional.columns
    ]

    print()

    print(
        df_dimensional[
            colunas_existentes
        ]
        .head(30)
        .to_string(index=False)
    )

    # ========================================================
    # 11. PREPARAR MEDIDAS DE COMPRA
    # ========================================================

    print()
    print("=" * 80)
    print("11. PREPARAR MEDIDAS DE COMPRA")
    print("=" * 80)

    if not hasattr(
        dimensional,
        "preparar_medidas_compra",
    ):

        raise AttributeError(
            "PlanejadorDimensional não possui "
            "preparar_medidas_compra()."
        )

    print(
        "Método preparar_medidas_compra(): encontrado."
    )

    df_corte = (
        dimensional.preparar_medidas_compra(
            df_dimensional
        )
    )

    if not isinstance(
        df_corte,
        pd.DataFrame,
    ):

        df_corte = pd.DataFrame(
            df_corte
        )

    print(
        f"Itens preparados para compra/corte: "
        f"{len(df_corte)}"
    )

    # ========================================================
    # 12. RESULTADO
    # ========================================================

    print()
    print("=" * 80)
    print("12. RESULTADO FINAL DO TESTE DIMENSIONAL")
    print("=" * 80)

    print(
        f"Necessidades:              "
        f"{len(df_necessidades)}"
    )

    print(
        f"Dimensional:               "
        f"{len(df_dimensional)}"
    )

    print(
        f"Preparados para compra:    "
        f"{len(df_corte)}"
    )

    print(
        f"Quantidade total:          "
        f"{total_dimensional:.4f}"
    )

    print()
    print("=" * 80)
    print("TESTE DO PLANEJADOR DIMENSIONAL CONCLUÍDO")
    print("=" * 80)


if __name__ == "__main__":
    main()