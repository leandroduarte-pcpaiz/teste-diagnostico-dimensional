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


# ============================================================
# TESTE
# ============================================================

def main():

    print("=" * 80)
    print("TESTE ISOLADO - MOTOR DE ENGENHARIA")
    print("=" * 80)

    print()
    print(f"Produto: {PRODUTO}")
    print(f"BOM: {ARQUIVO_BOM}")
    print(f"Cadastro: {ARQUIVO_CADASTRO}")

    # --------------------------------------------------------
    # 1. IMPORTAÇÃO
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("1. IMPORTANDO BOM")
    print("=" * 80)

    df_bom = importar_csv(ARQUIVO_BOM)

    if df_bom is None or df_bom.empty:
        raise RuntimeError(
            "ERRO: BOM não foi carregada."
        )

    print(
        f"Linhas da BOM: {len(df_bom)}"
    )

    # --------------------------------------------------------
    # 2. EXPLOSÃO
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("2. EXPLODINDO BOM")
    print("=" * 80)

    explosao = ExplosaoBOM(df_bom)

    resultado = explosao.explodir(
        PRODUTO,
        quantidade=1,
    )

    if isinstance(resultado, pd.DataFrame):

        df_explosao = resultado.copy()

    elif isinstance(resultado, list):

        df_explosao = pd.DataFrame(resultado)

    elif isinstance(resultado, dict):

        df_explosao = pd.DataFrame(
            list(resultado.items()),
            columns=[
                "componente",
                "quantidade_total",
            ],
        )

    else:

        raise TypeError(
            "Formato inesperado retornado por "
            f"ExplosaoBOM.explodir(): {type(resultado)}"
        )

    print(
        f"Componentes da explosão: "
        f"{len(df_explosao)}"
    )

    print()
    print("Colunas retornadas:")
    print(
        list(df_explosao.columns)
    )

    # --------------------------------------------------------
    # 3. NORMALIZA QUANTIDADE
    # --------------------------------------------------------

    if "quantidade_total" not in df_explosao.columns:

        if "quantidade" in df_explosao.columns:

            df_explosao["quantidade_total"] = (
                df_explosao["quantidade"]
            )

        else:

            raise ValueError(
                "Explosão não possui "
                "'quantidade_total' nem 'quantidade'."
            )

    # --------------------------------------------------------
    # 4. NORMALIZA COMPONENTE
    # --------------------------------------------------------

    if "componente" not in df_explosao.columns:

        raise ValueError(
            "Explosão não possui a coluna 'componente'."
        )

    df_explosao["componente"] = (
        df_explosao["componente"]
        .fillna("")
        .astype(str)
        .str.replace('="', "", regex=False)
        .str.replace('"', "", regex=False)
        .str.strip()
        .str.upper()
    )

    df_explosao["quantidade_total"] = pd.to_numeric(
        df_explosao["quantidade_total"],
        errors="coerce",
    ).fillna(0)

    # --------------------------------------------------------
    # 5. MOTOR
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("3. MOTOR DE ENGENHARIA")
    print("=" * 80)

    motor = MotorEngenharia(
        caminho_cadastro=ARQUIVO_CADASTRO
    )

    df_enriquecido = motor.enriquecer(
        df_explosao
    )

    if not isinstance(
        df_enriquecido,
        pd.DataFrame,
    ):
        raise TypeError(
            "MotorEngenharia.enriquecer() "
            "não retornou DataFrame."
        )

    # --------------------------------------------------------
    # 6. RESULTADOS
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("4. RESULTADO DO MOTOR")
    print("=" * 80)

    print()
    print(
        f"Componentes processados: "
        f"{len(df_enriquecido)}"
    )

    if "cadastro_encontrado" in df_enriquecido.columns:

        encontrados = int(
            df_enriquecido[
                "cadastro_encontrado"
            ].sum()
        )

        print(
            f"Encontrados no cadastro: "
            f"{encontrados}"
        )

        print(
            f"Não encontrados: "
            f"{len(df_enriquecido) - encontrados}"
        )

    # --------------------------------------------------------
    # 7. CLASSIFICAÇÃO
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("5. CLASSIFICAÇÃO AIZI")
    print("=" * 80)

    if "CLASSIFICACAO_AIZI" not in df_enriquecido.columns:

        raise ValueError(
            "Motor não produziu "
            "'CLASSIFICACAO_AIZI'."
        )

    resumo = (
        df_enriquecido[
            "CLASSIFICACAO_AIZI"
        ]
        .value_counts()
        .rename_axis(
            "CLASSIFICACAO_AIZI"
        )
        .reset_index(
            name="quantidade_itens"
        )
    )

    print(
        resumo.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # 8. CAMPOS OBRIGATÓRIOS
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("6. VALIDANDO CAMPOS")
    print("=" * 80)

    obrigatorios = [
        "componente",
        "quantidade_total",
        "DESCRICAO_PRODUTO",
        "UNIDADE_MEDIDA",
        "CLASSIFICACAO_AIZI",
        "CLASSIFICACAO",
        "categoria_planejamento",
    ]

    erros = []

    for coluna in obrigatorios:

        if coluna not in df_enriquecido.columns:

            erros.append(coluna)

    if erros:

        raise ValueError(
            "Campos obrigatórios ausentes:\n"
            + "\n".join(
                f"- {x}"
                for x in erros
            )
        )

    print(
        "OK - todos os campos obrigatórios existem."
    )

    # --------------------------------------------------------
    # 9. AMOSTRA
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("7. AMOSTRA")
    print("=" * 80)

    colunas = [
        "componente",
        "DESCRICAO_PRODUTO",
        "UNIDADE_MEDIDA",
        "CLASSIFICACAO_AIZI",
        "quantidade_total",
    ]

    print(
        df_enriquecido[
            colunas
        ]
        .head(20)
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # 10. RESULTADO FINAL
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("TESTE DO MOTOR CONCLUÍDO COM SUCESSO")
    print("=" * 80)


if __name__ == "__main__":
    main()