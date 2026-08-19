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
from app.engineering.planejador_dimensional import (
    PlanejadorDimensional,
)
from app.engineering.calculadora_corte import (
    CalculadoraCorte,
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
# FUNÇÕES AUXILIARES
# ============================================================

def imprimir_titulo(texto: str) -> None:
    print()
    print("=" * 80)
    print(texto)
    print("=" * 80)


def localizar_coluna(df: pd.DataFrame, nomes) -> str | None:
    """
    Localiza uma coluna ignorando maiúsculas/minúsculas,
    espaços e acentos básicos.

    IMPORTANTE:
    Se houver nomes duplicados no DataFrame, retorna somente
    a primeira coluna encontrada.
    """

    mapa = {}

    for coluna in df.columns:
        chave = (
            str(coluna)
            .strip()
            .upper()
        )

        if chave not in mapa:
            mapa[chave] = coluna

    for nome in nomes:
        chave = (
            str(nome)
            .strip()
            .upper()
        )

        if chave in mapa:
            return mapa[chave]

    return None


def garantir_coluna(
    df: pd.DataFrame,
    nome: str,
    valor=None,
) -> pd.DataFrame:
    """
    Garante uma coluna única.

    Se o DataFrame possuir colunas duplicadas com o mesmo nome,
    mantém a primeira e elimina as demais.
    """

    duplicadas = [
        coluna
        for coluna in df.columns
        if coluna == nome
    ]

    if len(duplicadas) > 1:
        indices = [
            i
            for i, coluna in enumerate(df.columns)
            if coluna == nome
        ]

        manter = indices[0]
        remover = set(indices[1:])

        df = df.iloc[
            :,
            [
                i
                for i in range(len(df.columns))
                if i not in remover
            ],
        ].copy()

    if nome not in df.columns:
        df[nome] = valor

    return df


def remover_colunas_duplicadas(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove colunas duplicadas mantendo somente a primeira.

    Esta função é fundamental para evitar o erro:

        AttributeError:
        'DataFrame' object has no attribute 'str'

    Esse erro ocorre quando:

        df["CLASSIFICACAO"]

    retorna outro DataFrame porque existem duas ou mais colunas
    chamadas CLASSIFICACAO.
    """

    df = df.copy()

    if not df.columns.duplicated().any():
        return df

    duplicadas = (
        df.columns[
            df.columns.duplicated()
        ]
        .tolist()
    )

    print()
    print(
        "AVISO: colunas duplicadas encontradas:"
    )

    for coluna in duplicadas:
        print(f"  - {coluna}")

    df = df.loc[
        :,
        ~df.columns.duplicated(
            keep="first"
        ),
    ].copy()

    return df


def normalizar_texto(valor) -> str:
    if valor is None:
        return ""

    try:
        if pd.isna(valor):
            return ""
    except (TypeError, ValueError):
        pass

    return (
        str(valor)
        .replace('="', "")
        .replace('"', "")
        .strip()
    )


def garantir_dataframe(
    valor,
    nome: str,
) -> pd.DataFrame:

    if valor is None:
        return pd.DataFrame()

    if isinstance(valor, pd.DataFrame):
        return remover_colunas_duplicadas(valor)

    if isinstance(valor, list):
        return remover_colunas_duplicadas(
            pd.DataFrame(valor)
        )

    if isinstance(valor, dict):
        return remover_colunas_duplicadas(
            pd.DataFrame(valor)
        )

    raise TypeError(
        f"{nome}: formato não reconhecido: "
        f"{type(valor)}"
    )


# ============================================================
# NORMALIZAÇÃO DA EXPLOSÃO
# ============================================================

def normalizar_explosao(
    df_explosao: pd.DataFrame,
) -> pd.DataFrame:

    df = remover_colunas_duplicadas(
        df_explosao
    )

    coluna_componente = localizar_coluna(
        df,
        [
            "componente",
            "filho",
            "produto",
            "codigo",
            "codigo_produto",
        ],
    )

    if coluna_componente is None:
        raise ValueError(
            "A explosão não possui uma coluna de componente."
        )

    if coluna_componente != "componente":
        df = df.rename(
            columns={
                coluna_componente: "componente"
            }
        )

    coluna_quantidade = localizar_coluna(
        df,
        [
            "quantidade_total",
            "quantidade",
            "qtd",
            "qtde",
        ],
    )

    if coluna_quantidade is None:
        raise ValueError(
            "A explosão não possui uma coluna de quantidade."
        )

    if coluna_quantidade != "quantidade_total":
        df = df.rename(
            columns={
                coluna_quantidade:
                "quantidade_total"
            }
        )

    df = remover_colunas_duplicadas(df)

    df = garantir_coluna(
        df,
        "componente",
        "",
    )

    df = garantir_coluna(
        df,
        "quantidade_total",
        0,
    )

    df["componente"] = (
        df["componente"]
        .apply(normalizar_texto)
        .str.upper()
        .str.strip()
    )

    df["quantidade_total"] = pd.to_numeric(
        df["quantidade_total"],
        errors="coerce",
    ).fillna(0.0)

    df = df[
        df["componente"] != ""
    ].copy()

    return df.reset_index(drop=True)


# ============================================================
# MOTOR DE ENGENHARIA
# ============================================================

def executar_motor_engenharia(
    df_explosao: pd.DataFrame,
) -> pd.DataFrame:

    imprimir_titulo(
        "3. MOTOR DE ENGENHARIA"
    )

    motor = MotorEngenharia(
        caminho_cadastro=ARQUIVO_CADASTRO
    )

    # O MotorEngenharia fornecido possui o método:
    #
    #     enriquecer()
    #
    # NÃO usar:
    #
    #     executar()
    #     processar()
    #     enriquecer_explosao()
    #
    # A chamada correta é abaixo.

    resultado = motor.enriquecer(
        df_explosao
    )

    resultado = garantir_dataframe(
        resultado,
        "MotorEngenharia",
    )

    resultado = remover_colunas_duplicadas(
        resultado
    )

    if resultado.empty:
        raise RuntimeError(
            "O Motor de Engenharia retornou "
            "um DataFrame vazio."
        )

    # --------------------------------------------------------
    # GARANTE CAMPOS PRINCIPAIS
    # --------------------------------------------------------

    for coluna, valor in [
        ("componente", ""),
        ("quantidade_total", 0.0),
        ("CLASSIFICACAO_AIZI", "FABRICADO"),
        ("CLASSIFICACAO", "FABRICADO"),
        ("categoria_planejamento", "FABRICADO"),
        ("UNIDADE_MEDIDA", ""),
        ("DESCRICAO_PRODUTO", ""),
    ]:
        resultado = garantir_coluna(
            resultado,
            coluna,
            valor,
        )

    # --------------------------------------------------------
    # NORMALIZA CAMPOS
    # --------------------------------------------------------

    resultado["componente"] = (
        resultado["componente"]
        .apply(normalizar_texto)
        .str.upper()
        .str.strip()
    )

    resultado["quantidade_total"] = pd.to_numeric(
        resultado["quantidade_total"],
        errors="coerce",
    ).fillna(0.0)

    for coluna in [
        "CLASSIFICACAO_AIZI",
        "CLASSIFICACAO",
        "categoria_planejamento",
        "UNIDADE_MEDIDA",
        "DESCRICAO_PRODUTO",
    ]:
        resultado[coluna] = (
            resultado[coluna]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------------
    # VALIDAÇÃO
    # --------------------------------------------------------

    classificados = (
        resultado["CLASSIFICACAO_AIZI"]
        .fillna("")
        .astype(str)
        .str.strip()
        != ""
    )

    nao_classificados = int(
        (~classificados).sum()
    )

    unidades = (
        resultado["UNIDADE_MEDIDA"]
        .fillna("")
        .astype(str)
        .str.strip()
        != ""
    )

    nao_encontradas = int(
        (~unidades).sum()
    )

    cadastro = (
        resultado.get(
            "cadastro_encontrado",
            pd.Series(
                True,
                index=resultado.index,
            ),
        )
    )

    cadastro = (
        cadastro
        .fillna(False)
        .astype(bool)
    )

    print()
    print(
        f"Componentes processados: "
        f"{len(resultado)}"
    )

    print(
        f"Encontrados no cadastro: "
        f"{int(cadastro.sum())}"
    )

    print(
        f"Não encontrados no cadastro: "
        f"{len(resultado) - int(cadastro.sum())}"
    )

    print()
    print("Classificação AIZI:")

    resumo = (
        resultado[
            "CLASSIFICACAO_AIZI"
        ]
        .replace("", "NAO_CLASSIFICADO")
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

    if nao_classificados:
        raise RuntimeError(
            "Existem componentes sem classificação AIZI."
        )

    if nao_encontradas:
        print()
        print(
            "AVISO: existem componentes sem "
            "unidade de medida no cadastro."
        )

    return resultado.reset_index(
        drop=True
    )


# ============================================================
# PREPARAÇÃO DAS NECESSIDADES
# ============================================================

def preparar_necessidades(
    df_explosao,
) -> pd.DataFrame:

    df = remover_colunas_duplicadas(
        df_explosao
    )

    coluna = localizar_coluna(
        df,
        [
            "componente",
            "codigo",
            "produto",
        ],
    )

    if coluna is None:
        raise ValueError(
            "Não foi possível identificar o componente."
        )

    if coluna != "componente":
        df = df.rename(
            columns={
                coluna: "componente"
            }
        )

    coluna = localizar_coluna(
        df,
        [
            "quantidade_total",
            "quantidade",
        ],
    )

    if coluna is None:
        raise ValueError(
            "Não foi possível identificar a quantidade."
        )

    if coluna != "quantidade_total":
        df = df.rename(
            columns={
                coluna:
                "quantidade_total"
            }
        )

    df = remover_colunas_duplicadas(
        df
    )

    df = garantir_coluna(
        df,
        "componente",
        "",
    )

    df = garantir_coluna(
        df,
        "quantidade_total",
        0.0,
    )

    df["componente"] = (
        df["componente"]
        .apply(normalizar_texto)
        .str.upper()
        .str.strip()
    )

    df["quantidade_total"] = pd.to_numeric(
        df["quantidade_total"],
        errors="coerce",
    ).fillna(0.0)

    # IMPORTANTE:
    #
    # NÃO MULTIPLICA AQUI.
    #
    # A multiplicação por QUANTIDADE_PRODUZIR
    # pertence exclusivamente ao PlanejadorNecessidades.

    return df


# ============================================================
# NORMALIZAÇÃO DO RESULTADO DO PLANEJADOR
# ============================================================

def normalizar_resultado_necessidades(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normaliza a saída do PlanejadorNecessidades.

    Esta versão elimina explicitamente o problema que causava:

        AttributeError:
        'DataFrame' object has no attribute 'str'

    A causa era uma coluna duplicada, principalmente
    CLASSIFICACAO.
    """

    df = garantir_dataframe(
        df,
        "PlanejadorNecessidades",
    )

    df = remover_colunas_duplicadas(
        df
    )

    if df.empty:
        return df

    # --------------------------------------------------------
    # COMPONENTE
    # --------------------------------------------------------

    coluna = localizar_coluna(
        df,
        [
            "componente",
            "codigo",
            "produto",
        ],
    )

    if coluna is None:
        raise ValueError(
            "O resultado do Planejador não possui componente."
        )

    if coluna != "componente":
        df = df.rename(
            columns={
                coluna:
                "componente"
            }
        )

    df = remover_colunas_duplicadas(df)

    df = garantir_coluna(
        df,
        "componente",
        "",
    )

    df["componente"] = (
        df["componente"]
        .apply(normalizar_texto)
        .str.upper()
        .str.strip()
    )

    # --------------------------------------------------------
    # QUANTIDADE NECESSÁRIA
    # --------------------------------------------------------

    coluna = localizar_coluna(
        df,
        [
            "quantidade_necessaria",
            "NECESSIDADE_TOTAL",
            "necessidade",
            "quantidade_total",
            "quantidade",
        ],
    )

    if coluna is None:
        raise ValueError(
            "O resultado do Planejador não possui "
            "quantidade_necessaria."
        )

    if coluna != "quantidade_necessaria":
        df = df.rename(
            columns={
                coluna:
                "quantidade_necessaria"
            }
        )

    df = remover_colunas_duplicadas(df)

    df = garantir_coluna(
        df,
        "quantidade_necessaria",
        0.0,
    )

    df["quantidade_necessaria"] = pd.to_numeric(
        df["quantidade_necessaria"],
        errors="coerce",
    ).fillna(0.0)

    # --------------------------------------------------------
    # CLASSIFICAÇÃO
    # --------------------------------------------------------

    # PRIORIDADE:
    #
    # 1. CLASSIFICACAO
    # 2. CLASSIFICACAO_AIZI
    # 3. categoria_planejamento
    #
    # Mas nunca criamos duas colunas com o mesmo nome.

    df = remover_colunas_duplicadas(df)

    coluna_classificacao = localizar_coluna(
        df,
        [
            "CLASSIFICACAO",
            "CLASSIFICACAO_AIZI",
            "categoria_planejamento",
            "classificacao",
        ],
    )

    if coluna_classificacao is None:

        df["CLASSIFICACAO"] = (
            "NAO_CLASSIFICADO"
        )

    elif coluna_classificacao != "CLASSIFICACAO":

        df = df.rename(
            columns={
                coluna_classificacao:
                "CLASSIFICACAO"
            }
        )

    df = remover_colunas_duplicadas(df)

    df = garantir_coluna(
        df,
        "CLASSIFICACAO",
        "NAO_CLASSIFICADO",
    )

    df["CLASSIFICACAO"] = (
        df["CLASSIFICACAO"]
        .fillna("NAO_CLASSIFICADO")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["CLASSIFICACAO"] = (
        df["CLASSIFICACAO"]
        .replace(
            {
                "ITEM_COMERCIAL":
                    "COMERCIAL",
                "ITEM COMERCIAL":
                    "COMERCIAL",
                "MATÉRIA PRIMA":
                    "MATERIA_PRIMA",
                "MATERIA PRIMA":
                    "MATERIA_PRIMA",
                "MATERIA-PRIMA":
                    "MATERIA_PRIMA",
                "MATERIA_PRIMA":
                    "MATERIA_PRIMA",
            }
        )
    )

    # --------------------------------------------------------
    # UNIDADE
    # --------------------------------------------------------

    df = remover_colunas_duplicadas(df)

    coluna = localizar_coluna(
        df,
        [
            "UNIDADE_MEDIDA",
            "unidade_medida",
            "um_componente",
            "um_produto",
            "UM",
            "um",
        ],
    )

    if coluna is None:

        df["UNIDADE_MEDIDA"] = ""

    elif coluna != "UNIDADE_MEDIDA":

        df = df.rename(
            columns={
                coluna:
                "UNIDADE_MEDIDA"
            }
        )

    df = remover_colunas_duplicadas(df)

    df = garantir_coluna(
        df,
        "UNIDADE_MEDIDA",
        "",
    )

    df["UNIDADE_MEDIDA"] = (
        df["UNIDADE_MEDIDA"]
        .fillna("")
        .apply(normalizar_texto)
        .str.upper()
        .str.strip()
    )

    # --------------------------------------------------------
    # DESCRIÇÃO
    # --------------------------------------------------------

    df = remover_colunas_duplicadas(df)

    coluna = localizar_coluna(
        df,
        [
            "DESCRICAO_PRODUTO",
            "descricao",
            "descricao_produto",
            "descricao_componente",
        ],
    )

    if coluna is None:

        df["descricao"] = ""

    elif coluna != "descricao":

        df = df.rename(
            columns={
                coluna:
                "descricao"
            }
        )

    df = remover_colunas_duplicadas(df)

    df = garantir_coluna(
        df,
        "descricao",
        "",
    )

    df["descricao"] = (
        df["descricao"]
        .fillna("")
        .apply(normalizar_texto)
    )

    return df.reset_index(
        drop=True
    )


# ============================================================
# CALCULADORA DE CORTE
# ============================================================

def executar_calculadora_corte(
    df_corte: pd.DataFrame,
) -> pd.DataFrame:

    resultados = []

    if df_corte is None:
        return pd.DataFrame()

    df_corte = garantir_dataframe(
        df_corte,
        "Itens para corte",
    )

    if df_corte.empty:
        return pd.DataFrame()

    for _, item in df_corte.iterrows():

        try:

            codigo = normalizar_texto(
                item.get(
                    "componente",
                    item.get(
                        "codigo_peca",
                        "",
                    ),
                )
            )

            material = normalizar_texto(
                item.get(
                    "material",
                    item.get(
                        "materia_prima",
                        "",
                    ),
                )
            )

            espessura = item.get(
                "espessura_mm",
                None,
            )

            largura_peca = item.get(
                "largura_efetiva_mm",
                item.get(
                    "largura_peca_mm",
                    None,
                ),
            )

            comprimento_peca = item.get(
                "comprimento_efetivo_mm",
                item.get(
                    "comprimento_peca_mm",
                    None,
                ),
            )

            quantidade = item.get(
                "quantidade_necessaria",
                0,
            )

            largura_chapa = item.get(
                "largura_padrao_mm",
                item.get(
                    "largura_chapa_mm",
                    None,
                ),
            )

            comprimento_chapa = item.get(
                "comprimento_padrao_mm",
                item.get(
                    "comprimento_chapa_mm",
                    None,
                ),
            )

            valores = [
                espessura,
                largura_peca,
                comprimento_peca,
                largura_chapa,
                comprimento_chapa,
            ]

            invalido = False

            for valor in valores:

                if valor is None:
                    invalido = True
                    break

                try:
                    if pd.isna(valor):
                        invalido = True
                        break

                    if float(valor) <= 0:
                        invalido = True
                        break

                except (
                    TypeError,
                    ValueError,
                ):
                    invalido = True
                    break

            if invalido:
                continue

            try:
                quantidade = int(
                    float(quantidade)
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            if quantidade <= 0:
                continue

            calculadora = CalculadoraCorte(
                codigo_peca=codigo,
                material=material,
                espessura_mm=espessura,
                largura_peca_mm=largura_peca,
                comprimento_peca_mm=(
                    comprimento_peca
                ),
                quantidade=quantidade,
                largura_chapa_mm=(
                    largura_chapa
                ),
                comprimento_chapa_mm=(
                    comprimento_chapa
                ),
            )

            resultado = calculadora.calcular()

            if resultado:
                resultados.append(
                    resultado
                )

        except Exception as erro:

            print()
            print(
                f"ERRO NO CORTE - "
                f"{item.get('componente', '')}: "
                f"{erro}"
            )

    return pd.DataFrame(
        resultados
    )


# ============================================================
# VALIDAÇÃO DA NECESSIDADE
# ============================================================

def validar_necessidade(
    df_explosao: pd.DataFrame,
    df_necessidades: pd.DataFrame,
) -> None:

    imprimir_titulo(
        "VALIDAÇÃO DA NECESSIDADE"
    )

    df_explosao = remover_colunas_duplicadas(
        df_explosao
    )

    df_necessidades = remover_colunas_duplicadas(
        df_necessidades
    )

    print(
        f"Componentes na explosão: "
        f"{len(df_explosao)}"
    )

    print(
        f"Itens na necessidade: "
        f"{len(df_necessidades)}"
    )

    if len(df_explosao) == len(df_necessidades):

        print(
            "STATUS: OK - quantidade de itens preservada."
        )

    else:

        print(
            "ATENÇÃO: quantidade de itens mudou entre "
            "explosão e necessidade."
        )

    # --------------------------------------------------------
    # VALIDA DUPLICAÇÃO
    # --------------------------------------------------------

    if (
        "componente" in df_necessidades.columns
        and "quantidade_necessaria"
        in df_necessidades.columns
    ):

        duplicados = (
            df_necessidades[
                "componente"
            ]
            .duplicated()
            .sum()
        )

        if duplicados == 0:

            print(
                "STATUS: OK - sem componentes duplicados."
            )

        else:

            print(
                f"ATENÇÃO: {duplicados} "
                f"componentes duplicados."
            )

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    if (
        "quantidade_necessaria"
        in df_necessidades.columns
    ):

        total = pd.to_numeric(
            df_necessidades[
                "quantidade_necessaria"
            ],
            errors="coerce",
        ).fillna(0).sum()

        print(
            f"Quantidade total planejada: "
            f"{total:,.4f}"
        )


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    imprimir_titulo(
        "AIZI ENGINEERING AI\n"
        "PLANEJAMENTO COMPLETO"
    )

    print(
        f"Produto: {PRODUTO}"
    )

    print(
        f"Quantidade a produzir: "
        f"{QUANTIDADE_PRODUZIR}"
    )

    # ========================================================
    # 1. IMPORTAÇÃO BOM
    # ========================================================

    imprimir_titulo(
        "1. IMPORTANDO BOM DO TOTVS"
    )

    df_bom = importar_csv(
        ARQUIVO_BOM
    )

    if df_bom is None or df_bom.empty:

        print(
            "ERRO: BOM não carregada."
        )

        return

    print(
        f"Linhas carregadas: "
        f"{len(df_bom)}"
    )

    # ========================================================
    # 2. EXPLOSÃO
    # ========================================================

    imprimir_titulo(
        "2. EXPLOSÃO DA BOM"
    )

    explosao = ExplosaoBOM(
        df_bom
    )

    resultado_explosao = explosao.explodir(
        PRODUTO,
        quantidade=1,
    )

    df_explosao = garantir_dataframe(
        resultado_explosao,
        "ExplosaoBOM",
    )

    df_explosao = normalizar_explosao(
        df_explosao
    )

    print(
        f"Componentes finais encontrados: "
        f"{len(df_explosao)}"
    )

    # ========================================================
    # 3. MOTOR DE ENGENHARIA
    # ========================================================

    df_classificado = (
        executar_motor_engenharia(
            df_explosao
        )
    )

    # ========================================================
    # 4. PLANEJADOR DE NECESSIDADES
    # ========================================================

    imprimir_titulo(
        "4. PLANEJADOR DE NECESSIDADES"
    )

    df_preparado = preparar_necessidades(
        df_classificado
    )

    planejador = PlanejadorNecessidades(
        resultado_classificado=df_preparado,
        quantidade_conjuntos=(
            QUANTIDADE_PRODUZIR
        ),
    )

    resultado = planejador.planejar()

    df_necessidades = (
        normalizar_resultado_necessidades(
            resultado
        )
    )

    print(
        f"Itens na necessidade: "
        f"{len(df_necessidades)}"
    )

    # ========================================================
    # 5. RESUMO DA NECESSIDADE
    # ========================================================

    imprimir_titulo(
        "5. RESUMO DA NECESSIDADE"
    )

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
    # VALIDAÇÃO
    # ========================================================

    validar_necessidade(
        df_classificado,
        df_necessidades,
    )

    # ========================================================
    # 6. PLANEJAMENTO DIMENSIONAL
    # ========================================================

    imprimir_titulo(
        "6. PLANEJAMENTO DIMENSIONAL"
    )

    dimensional = PlanejadorDimensional(
        df_necessidades
    )

    if hasattr(
        dimensional,
        "analisar",
    ):

        df_dimensional = (
            dimensional.analisar()
        )

    else:

        df_dimensional = (
            df_necessidades.copy()
        )

    df_dimensional = garantir_dataframe(
        df_dimensional,
        "PlanejadorDimensional",
    )

    if "componente" not in df_dimensional.columns:

        df_dimensional = (
            df_necessidades.copy()
        )

    df_dimensional = remover_colunas_duplicadas(
        df_dimensional
    )

    garantir_coluna(
        df_dimensional,
        "tipo_dimensional",
        "NAO_APLICAVEL",
    )

    df_dimensional["tipo_dimensional"] = (
        df_dimensional[
            "tipo_dimensional"
        ]
        .fillna("NAO_APLICAVEL")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    print()
    print(
        "Tipos dimensionais encontrados:"
    )

    tipos = (
        df_dimensional[
            "tipo_dimensional"
        ]
        .value_counts()
        .rename_axis(
            "tipo_dimensional"
        )
        .reset_index(
            name="quantidade_itens"
        )
    )

    print(
        tipos.to_string(
            index=False
        )
    )

    # ========================================================
    # 7. PREPARAR PARA CORTE
    # ========================================================

    imprimir_titulo(
        "7. ITENS PREPARADOS PARA CORTE"
    )

    if hasattr(
        dimensional,
        "preparar_medidas_compra",
    ):

        try:

            df_corte = (
                dimensional
                .preparar_medidas_compra(
                    df_dimensional
                )
            )

            df_corte = garantir_dataframe(
                df_corte,
                "Preparação para corte",
            )

        except Exception as erro:

            print(
                "ERRO AO PREPARAR CORTE:"
            )

            print(erro)

            df_corte = pd.DataFrame()

    else:

        print(
            "PlanejadorDimensional não possui "
            "preparar_medidas_compra()."
        )

        df_corte = pd.DataFrame()

    print(
        f"Itens preparados para corte: "
        f"{len(df_corte)}"
    )

    # ========================================================
    # 8. RESULTADO DIMENSIONAL
    # ========================================================

    imprimir_titulo(
        "8. RESULTADO DIMENSIONAL"
    )

    colunas_dimensional = [
        "componente",
        "descricao",
        "DESCRICAO_PRODUTO",
        "CLASSIFICACAO",
        "UNIDADE_MEDIDA",
        "quantidade_necessaria",
        "tipo_dimensional",
        "espessura_mm",
        "diametro_externo_mm",
        "largura_padrao_mm",
        "comprimento_padrao_mm",
        "largura_efetiva_mm",
        "comprimento_efetivo_mm",
        "status_dimensional",
        "preparado_para_corte",
    ]

    df_dimensional = remover_colunas_duplicadas(
        df_dimensional
    )

    for coluna in colunas_dimensional:

        garantir_coluna(
            df_dimensional,
            coluna,
            None,
        )

    print(
        df_dimensional[
            colunas_dimensional
        ].to_string(
            index=False
        )
    )

    # ========================================================
    # 9. CALCULADORA DE CORTE
    # ========================================================

    imprimir_titulo(
        "9. CALCULADORA DE CORTE"
    )

    df_resultados_corte = (
        executar_calculadora_corte(
            df_corte
        )
    )

    # ========================================================
    # 10. RESULTADO DOS CÁLCULOS
    # ========================================================

    imprimir_titulo(
        "10. RESULTADO DOS CÁLCULOS DE CORTE"
    )

    if df_resultados_corte.empty:

        print(
            "Nenhum cálculo de corte realizado."
        )

    else:

        print(
            df_resultados_corte.to_string(
                index=False
            )
        )

    # ========================================================
    # 11. RESUMO FINAL
    # ========================================================

    imprimir_titulo(
        "11. RESUMO FINAL"
    )

    print(
        f"Produto: "
        f"{PRODUTO}"
    )

    print(
        f"Quantidade produzida: "
        f"{QUANTIDADE_PRODUZIR}"
    )

    print(
        f"Linhas BOM importadas: "
        f"{len(df_bom)}"
    )

    print(
        f"Componentes da explosão: "
        f"{len(df_explosao)}"
    )

    print(
        f"Componentes classificados: "
        f"{len(df_classificado)}"
    )

    print(
        f"Itens da necessidade: "
        f"{len(df_necessidades)}"
    )

    print(
        f"Itens dimensionais: "
        f"{len(df_dimensional)}"
    )

    print(
        f"Itens preparados para corte: "
        f"{len(df_corte)}"
    )

    print(
        f"Cálculos de corte realizados: "
        f"{len(df_resultados_corte)}"
    )

    if (
        "quantidade_necessaria"
        in df_necessidades.columns
    ):

        total_necessidade = pd.to_numeric(
            df_necessidades[
                "quantidade_necessaria"
            ],
            errors="coerce",
        ).fillna(0).sum()

        print(
            f"Quantidade total da necessidade: "
            f"{total_necessidade:,.4f}"
        )

    print()
    print(
        "ESTOQUE NÃO CONSIDERADO."
    )

    print(
        "A necessidade acima é a necessidade bruta "
        "calculada a partir da BOM."
    )

    print()
    print("=" * 80)
    print(
        "FIM DO TESTE"
    )
    print("=" * 80)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()