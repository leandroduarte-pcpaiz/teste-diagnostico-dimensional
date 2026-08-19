from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


class PlanejadorNecessidades:
    """
    Planejador de Necessidades do AIZI Engineering AI.

    RESPONSABILIDADE
    ----------------
    Recebe a explosão da BOM correspondente a 1 conjunto,
    já enriquecida e classificada pelo Motor de Engenharia.

    O Planejador aplica a quantidade de conjuntos desejada.

    REGRA FUNDAMENTAL
    -----------------
    A explosão da BOM representa SEMPRE 1 conjunto.

        quantidade_conjunto
            = quantidade da explosão para 1 conjunto

        quantidade_necessaria
            = quantidade_conjunto * quantidade_conjuntos

    O Planejador NÃO altera a explosão original.

    NÃO CONSIDERA AINDA:
        - estoque disponível
        - reservas
        - pedidos
        - compras
        - saldo
        - necessidade líquida real

    A preparação para estoque existe somente como estrutura
    para a próxima camada do sistema.
    """

    # ==========================================================
    # INICIALIZAÇÃO
    # ==========================================================

    def __init__(
        self,
        resultado_classificado: Optional[pd.DataFrame] = None,
        quantidade_conjuntos: float = 1,
        explosao: Optional[pd.DataFrame] = None,
        cadastro=None,
    ):
        """
        Parâmetros principais:

        resultado_classificado:
            DataFrame resultante da explosão + cadastro +
            classificação AIZI.

        quantidade_conjuntos:
            Quantidade de produtos acabados desejada.

        explosao / cadastro:
            Mantidos por compatibilidade com versões anteriores.
        """

        self.resultado_classificado = (
            resultado_classificado
        )

        self.quantidade_conjuntos = (
            float(quantidade_conjuntos)
        )

        self.explosao = explosao
        self.cadastro = cadastro

        self.df = pd.DataFrame()

    # ==========================================================
    # PLANEJAMENTO PRINCIPAL
    # ==========================================================

    def planejar(
        self,
        resultado_classificado=None,
        quantidade_conjuntos=None,
    ) -> pd.DataFrame:
        """
        Calcula a necessidade para a quantidade de conjuntos.

        Entrada:

            quantidade_conjunto = quantidade da BOM para 1 conjunto

        Saída:

            quantidade_conjunto
            quantidade_necessaria

        Exemplo:

            G2005887
            quantidade_conjunto = 101156.980 KG
            conjuntos = 10

            quantidade_necessaria = 1011569.800 KG
        """

        # ------------------------------------------------------
        # ATUALIZA PARÂMETROS, SE INFORMADOS
        # ------------------------------------------------------

        if resultado_classificado is not None:

            self.resultado_classificado = (
                resultado_classificado
            )

        if quantidade_conjuntos is not None:

            self.quantidade_conjuntos = float(
                quantidade_conjuntos
            )

        # ------------------------------------------------------
        # VALIDA QUANTIDADE
        # ------------------------------------------------------

        if self.quantidade_conjuntos < 0:

            raise ValueError(
                "A quantidade de conjuntos não pode ser negativa."
            )

        # ------------------------------------------------------
        # OBTÉM DATAFRAME
        # ------------------------------------------------------

        df = self.resultado_classificado

        # ------------------------------------------------------
        # COMPATIBILIDADE COM VERSÃO ANTIGA
        # ------------------------------------------------------

        if df is None:

            df = self.explosao

        if df is None:

            self.df = pd.DataFrame()

            return self.df

        if not isinstance(df, pd.DataFrame):

            raise TypeError(
                "resultado_classificado deve ser um "
                "pandas.DataFrame."
            )

        if df.empty:

            self.df = pd.DataFrame()

            return self.df

        df = df.copy()

        # ------------------------------------------------------
        # NORMALIZA COLUNAS
        # ------------------------------------------------------

        df = self._normalizar_colunas(df)

        # ------------------------------------------------------
        # VALIDA PRODUTO
        # ------------------------------------------------------

        if "componente" not in df.columns:

            if "produto" in df.columns:

                df["componente"] = df["produto"]

            else:

                raise ValueError(
                    "O resultado não possui coluna "
                    "'componente' ou 'produto'."
                )

        # ------------------------------------------------------
        # VALIDA QUANTIDADE
        # ------------------------------------------------------

        if "quantidade_total" not in df.columns:

            if "quantidade" in df.columns:

                df["quantidade_total"] = (
                    df["quantidade"]
                )

            else:

                raise ValueError(
                    "O resultado não possui coluna "
                    "'quantidade_total' ou 'quantidade'."
                )

        # ------------------------------------------------------
        # PADRONIZA COMPONENTE
        # ------------------------------------------------------

        df["componente"] = (
            df["componente"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        # ------------------------------------------------------
        # PADRONIZA QUANTIDADE
        # ------------------------------------------------------

        df["quantidade_total"] = pd.to_numeric(
            df["quantidade_total"],
            errors="coerce",
        ).fillna(0.0)

        # ------------------------------------------------------
        # REMOVE QUANTIDADES ZERO
        # ------------------------------------------------------

        df = df[
            df["quantidade_total"] != 0
        ].copy()

        if df.empty:

            self.df = pd.DataFrame()

            return self.df

        # ======================================================
        # CONSOLIDAÇÃO DA BOM
        # ======================================================
        #
        # IMPORTANTE:
        #
        # A explosão já deveria estar consolidada.
        #
        # Entretanto, caso existam componentes repetidos,
        # consolidamos novamente.
        #
        # A unidade é considerada para não misturar:
        #
        # KG
        # MT
        # PC
        # UN
        # etc.
        #
        # ======================================================

        colunas_grupo = [
            "componente",
        ]

        if "UNIDADE_MEDIDA" in df.columns:

            colunas_grupo.append(
                "UNIDADE_MEDIDA"
            )

        elif "unidade" in df.columns:

            colunas_grupo.append(
                "unidade"
            )

        # ------------------------------------------------------
        # COLUNAS DE CADASTRO
        # ------------------------------------------------------

        colunas_preservar = [
            "DESCRICAO_PRODUTO",
            "descricao",
            "CLASSIFICACAO",
            "classificacao",
            "TIPO",
            "DESCRICAO_TIPO",
            "ITEM_FANTASMA",
            "CLASSIFICACAO_AIZI",
            "TIPO_ENGENHARIA",
            "UNIDADE_MEDIDA",
            "unidade",
        ]

        colunas_preservar = [
            coluna
            for coluna in colunas_preservar
            if coluna in df.columns
            and coluna not in colunas_grupo
        ]

        # ------------------------------------------------------
        # AGRUPAMENTO
        # ------------------------------------------------------

        agregacoes = {
            "quantidade_total": "sum",
        }

        for coluna in colunas_preservar:

            agregacoes[coluna] = "first"

        df = (
            df
            .groupby(
                colunas_grupo,
                as_index=False,
                dropna=False,
            )
            .agg(agregacoes)
        )

        # ======================================================
        # QUANTIDADE POR CONJUNTO
        # ======================================================

        df["quantidade_conjunto"] = (
            df["quantidade_total"]
        )

        # ======================================================
        # NECESSIDADE REAL
        # ======================================================

        df["quantidade_necessaria"] = (
            df["quantidade_conjunto"]
            * self.quantidade_conjuntos
        )

        # ======================================================
        # PADRONIZA CLASSIFICAÇÃO
        # ======================================================

        df = self._padronizar_classificacao(
            df
        )

        # ======================================================
        # PADRONIZA UNIDADE
        # ======================================================

        df = self._padronizar_unidade(
            df
        )

        # ======================================================
        # PADRONIZA DESCRIÇÃO
        # ======================================================

        df = self._padronizar_descricao(
            df
        )

        # ======================================================
        # NOME DA NECESSIDADE TOTAL
        # ======================================================

        df["NECESSIDADE_TOTAL"] = (
            df["quantidade_necessaria"]
        )

        # ======================================================
        # ORDENAÇÃO
        # ======================================================

        colunas_preferenciais = [
            "componente",
            "DESCRICAO_PRODUTO",
            "CLASSIFICACAO",
            "UNIDADE_MEDIDA",
            "quantidade_conjunto",
            "quantidade_necessaria",
            "NECESSIDADE_TOTAL",
        ]

        colunas_existentes = [
            coluna
            for coluna in colunas_preferenciais
            if coluna in df.columns
        ]

        outras = [
            coluna
            for coluna in df.columns
            if coluna not in colunas_existentes
        ]

        df = df[
            colunas_existentes + outras
        ]

        df = (
            df
            .sort_values(
                "componente"
            )
            .reset_index(drop=True)
        )

        self.df = df

        return self.df

    # ==========================================================
    # NORMALIZAÇÃO DE COLUNAS
    # ==========================================================

    @staticmethod
    def _normalizar_colunas(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        mapa = {}

        for coluna in df.columns:

            nome = (
                str(coluna)
                .strip()
                .lower()
            )

            nome = (
                nome
                .replace("ç", "c")
                .replace("ã", "a")
                .replace("á", "a")
                .replace("à", "a")
                .replace("â", "a")
                .replace("é", "e")
                .replace("ê", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ô", "o")
                .replace("ú", "u")
            )

            if nome in (
                "produto",
                "codigo",
                "codigo_produto",
                "cod_produto",
                "componente",
                "item",
            ):

                if (
                    "componente"
                    not in df.columns
                ):

                    mapa[coluna] = (
                        "componente"
                    )

            elif nome in (
                "quantidade",
                "qtd",
                "qtde",
                "quantidade_total",
                "necessidade",
                "necessidade_bruta",
            ):

                if (
                    "quantidade_total"
                    not in df.columns
                ):

                    mapa[coluna] = (
                        "quantidade_total"
                    )

        if mapa:

            df = df.rename(
                columns=mapa
            )

        return df

    # ==========================================================
    # PADRONIZA CLASSIFICAÇÃO
    # ==========================================================

    @staticmethod
    def _padronizar_classificacao(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        # ------------------------------------------------------
        # PRIMEIRA PRIORIDADE:
        # CLASSIFICACAO_AIZI
        # ------------------------------------------------------

        if (
            "CLASSIFICACAO_AIZI"
            in df.columns
        ):

            classificacao = (
                df["CLASSIFICACAO_AIZI"]
                .fillna("")
                .astype(str)
                .str.upper()
                .str.strip()
            )

        elif (
            "CLASSIFICACAO"
            in df.columns
        ):

            classificacao = (
                df["CLASSIFICACAO"]
                .fillna("")
                .astype(str)
                .str.upper()
                .str.strip()
            )

        elif (
            "classificacao"
            in df.columns
        ):

            classificacao = (
                df["classificacao"]
                .fillna("")
                .astype(str)
                .str.upper()
                .str.strip()
            )

        else:

            classificacao = pd.Series(
                "NAO_CLASSIFICADO",
                index=df.index,
            )

        # ------------------------------------------------------
        # NORMALIZA NOMES
        # ------------------------------------------------------

        classificacao = (
            classificacao
            .replace(
                {
                    "ITEM_COMERCIAL":
                        "COMERCIAL",
                    "ITEM COMERCIAL":
                        "COMERCIAL",
                    "MATERIA PRIMA":
                        "MATERIA_PRIMA",
                    "MATÉRIA PRIMA":
                        "MATERIA_PRIMA",
                    "MATERIA-PRIMA":
                        "MATERIA_PRIMA",
                    "MATERIA_PRIMA":
                        "MATERIA_PRIMA",
                    "CONSUMO":
                        "CONSUMO",
                }
            )
        )

        # ------------------------------------------------------
        # CLASSIFICAÇÃO FINAL
        # ------------------------------------------------------

        df["CLASSIFICACAO"] = (
            classificacao
        )

        return df

    # ==========================================================
    # PADRONIZA UNIDADE
    # ==========================================================

    @staticmethod
    def _padronizar_unidade(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        if (
            "UNIDADE_MEDIDA"
            not in df.columns
        ):

            if "unidade" in df.columns:

                df["UNIDADE_MEDIDA"] = (
                    df["unidade"]
                )

            else:

                df["UNIDADE_MEDIDA"] = ""

        df["UNIDADE_MEDIDA"] = (
            df["UNIDADE_MEDIDA"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip()
        )

        return df

    # ==========================================================
    # PADRONIZA DESCRIÇÃO
    # ==========================================================

    @staticmethod
    def _padronizar_descricao(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        if (
            "DESCRICAO_PRODUTO"
            not in df.columns
        ):

            if "descricao" in df.columns:

                df["DESCRICAO_PRODUTO"] = (
                    df["descricao"]
                )

            else:

                df["DESCRICAO_PRODUTO"] = ""

        df["DESCRICAO_PRODUTO"] = (
            df["DESCRICAO_PRODUTO"]
            .fillna("")
            .astype(str)
        )

        return df

    # ==========================================================
    # NECESSIDADE BRUTA
    # ==========================================================

    def necessidade_bruta(
        self,
    ) -> pd.DataFrame:

        if self.df.empty:

            return self.planejar()

        return self.df.copy()

    # ==========================================================
    # MATÉRIA-PRIMA
    # ==========================================================

    def obter_materia_prima(
        self,
        planejamento=None,
    ) -> pd.DataFrame:

        df = self._obter_dataframe(
            planejamento
        )

        if df.empty:

            return df

        return df[
            df["CLASSIFICACAO"]
            .astype(str)
            .str.upper()
            .str.strip()
            == "MATERIA_PRIMA"
        ].copy()

    # ==========================================================
    # COMERCIAL
    # ==========================================================

    def obter_comercial(
        self,
        planejamento=None,
    ) -> pd.DataFrame:

        df = self._obter_dataframe(
            planejamento
        )

        if df.empty:

            return df

        return df[
            df["CLASSIFICACAO"]
            .astype(str)
            .str.upper()
            .str.strip()
            == "COMERCIAL"
        ].copy()

    # ==========================================================
    # CONSUMO
    # ==========================================================

    def obter_consumo(
        self,
        planejamento=None,
    ) -> pd.DataFrame:

        df = self._obter_dataframe(
            planejamento
        )

        if df.empty:

            return df

        return df[
            df["CLASSIFICACAO"]
            .astype(str)
            .str.upper()
            .str.strip()
            == "CONSUMO"
        ].copy()

    # ==========================================================
    # CONSOLIDAÇÃO
    # ==========================================================

    def consolidar_necessidades(
        self,
        planejamento=None,
    ) -> pd.DataFrame:

        df = self._obter_dataframe(
            planejamento
        )

        if df.empty:

            return pd.DataFrame(
                columns=[
                    "componente",
                    "DESCRICAO_PRODUTO",
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                    "quantidade_conjunto",
                    "NECESSIDADE_TOTAL",
                ]
            )

        # ------------------------------------------------------
        # IMPORTANTE:
        #
        # Produto + classificação + unidade.
        #
        # Nunca misturar KG com PC, MT etc.
        # ------------------------------------------------------

        grupo = [
            "componente",
            "CLASSIFICACAO",
            "UNIDADE_MEDIDA",
        ]

        agregacoes = {
            "quantidade_conjunto": "sum",
            "NECESSIDADE_TOTAL": "sum",
        }

        if (
            "DESCRICAO_PRODUTO"
            in df.columns
        ):

            agregacoes[
                "DESCRICAO_PRODUTO"
            ] = "first"

        consolidado = (
            df
            .groupby(
                grupo,
                as_index=False,
                dropna=False,
            )
            .agg(agregacoes)
        )

        return (
            consolidado
            .sort_values(
                "componente"
            )
            .reset_index(drop=True)
        )

    # ==========================================================
    # RESUMO POR CLASSIFICAÇÃO
    # ==========================================================

    def resumo_classificacao(
        self,
        planejamento=None,
    ) -> pd.DataFrame:

        df = self._obter_dataframe(
            planejamento
        )

        if df.empty:

            return pd.DataFrame(
                columns=[
                    "CLASSIFICACAO",
                    "quantidade_itens",
                    "quantidade_total",
                ]
            )

        resumo = (
            df
            .groupby(
                "CLASSIFICACAO",
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

        return (
            resumo
            .sort_values(
                "CLASSIFICACAO"
            )
            .reset_index(drop=True)
        )

    # ==========================================================
    # RESUMO POR CLASSIFICAÇÃO E UNIDADE
    # ==========================================================

    def resumo_classificacao_unidade(
        self,
        planejamento=None,
    ) -> pd.DataFrame:

        df = self._obter_dataframe(
            planejamento
        )

        if df.empty:

            return pd.DataFrame(
                columns=[
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                    "quantidade_itens",
                    "quantidade_total",
                ]
            )

        resumo = (
            df
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

        return (
            resumo
            .sort_values(
                [
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                ]
            )
            .reset_index(drop=True)
        )

    # ==========================================================
    # PREPARAR PARA ESTOQUE
    # ==========================================================

    def preparar_para_estoque(
        self,
        planejamento=None,
    ) -> pd.DataFrame:
        """
        Prepara a necessidade para a futura camada de estoque.

        IMPORTANTE:
        Nenhum estoque é descontado neste momento.

        Portanto:

            NECESSIDADE_LIQUIDA
                = NECESSIDADE_TOTAL

        até que o módulo de estoque seja integrado.
        """

        df = self.consolidar_necessidades(
            planejamento
        )

        if df.empty:

            return pd.DataFrame(
                columns=[
                    "componente",
                    "DESCRICAO_PRODUTO",
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                    "NECESSIDADE_TOTAL",
                    "ARMAZEM",
                    "ENDERECO",
                    "ESTOQUE_DISPONIVEL",
                    "ESTOQUE_RESERVADO",
                    "ESTOQUE_UTILIZAVEL",
                    "NECESSIDADE_LIQUIDA",
                ]
            )

        estoque = df.copy()

        # ------------------------------------------------------
        # CAMPOS DA FUTURA CAMADA DE ESTOQUE
        # ------------------------------------------------------

        estoque["ARMAZEM"] = ""

        estoque["ENDERECO"] = ""

        estoque["ESTOQUE_DISPONIVEL"] = 0.0

        estoque["ESTOQUE_RESERVADO"] = 0.0

        estoque["ESTOQUE_UTILIZAVEL"] = 0.0

        # ------------------------------------------------------
        # NESTA FASE NÃO HÁ ABATIMENTO
        # ------------------------------------------------------

        estoque["NECESSIDADE_LIQUIDA"] = (
            estoque["NECESSIDADE_TOTAL"]
        )

        colunas = [
            "componente",
            "DESCRICAO_PRODUTO",
            "CLASSIFICACAO",
            "UNIDADE_MEDIDA",
            "NECESSIDADE_TOTAL",
            "ARMAZEM",
            "ENDERECO",
            "ESTOQUE_DISPONIVEL",
            "ESTOQUE_RESERVADO",
            "ESTOQUE_UTILIZAVEL",
            "NECESSIDADE_LIQUIDA",
        ]

        return estoque[
            colunas
        ]

    # ==========================================================
    # OBTÉM DATAFRAME
    # ==========================================================

    def _obter_dataframe(
        self,
        planejamento=None,
    ) -> pd.DataFrame:

        if planejamento is not None:

            if not isinstance(
                planejamento,
                pd.DataFrame,
            ):

                raise TypeError(
                    "O planejamento deve ser um "
                    "pandas.DataFrame."
                )

            return planejamento.copy()

        if self.df.empty:

            return self.planejar()

        return self.df.copy()

    # ==========================================================
    # TOTAL DE QUANTIDADE
    # ==========================================================

    def total_quantidade(
        self,
        classificacao: Optional[str] = None,
    ) -> float:

        df = self._obter_dataframe()

        if df.empty:

            return 0.0

        if classificacao is not None:

            classificacao = (
                str(classificacao)
                .strip()
                .upper()
            )

            df = df[
                df["CLASSIFICACAO"]
                .astype(str)
                .str.upper()
                .str.strip()
                == classificacao
            ]

        return float(
            pd.to_numeric(
                df[
                    "quantidade_necessaria"
                ],
                errors="coerce",
            )
            .fillna(0.0)
            .sum()
        )

    # ==========================================================
    # FILTRAR POR CLASSIFICAÇÃO
    # ==========================================================

    def filtrar_classificacao(
        self,
        classificacao: str,
    ) -> pd.DataFrame:

        df = self._obter_dataframe()

        if df.empty:

            return df

        classificacao = (
            str(classificacao)
            .strip()
            .upper()
        )

        return df[
            df["CLASSIFICACAO"]
            .astype(str)
            .str.upper()
            .str.strip()
            == classificacao
        ].copy()

    # ==========================================================
    # OBTER RESULTADO
    # ==========================================================

    def obter(
        self,
    ) -> pd.DataFrame:

        return self.df.copy()

    # ==========================================================
    # RESUMO COMPLETO
    # ==========================================================

    def resumo(
        self,
    ):

        return {
            "necessidades": (
                self.necessidade_bruta()
            ),
            "por_classificacao": (
                self.resumo_classificacao()
            ),
            "por_classificacao_unidade": (
                self.resumo_classificacao_unidade()
            ),
        }

    # ==========================================================
    # EXPORTAÇÃO EXCEL
    # ==========================================================

    def exportar_excel(
        self,
        caminho,
        planejamento=None,
    ):

        df = self._obter_dataframe(
            planejamento
        )

        caminho = Path(caminho)

        caminho.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ------------------------------------------------------
        # DATAFRAMES PARA EXPORTAÇÃO
        # ------------------------------------------------------

        materia_prima = (
            self.obter_materia_prima(df)
        )

        comercial = (
            self.obter_comercial(df)
        )

        consumo = (
            self.obter_consumo(df)
        )

        consolidado = (
            self.consolidar_necessidades(df)
        )

        estoque = (
            self.preparar_para_estoque(df)
        )

        resumo = (
            self.resumo_classificacao(df)
        )

        resumo_unidade = (
            self.resumo_classificacao_unidade(df)
        )

        # ------------------------------------------------------
        # EXPORTA
        # ------------------------------------------------------

        with pd.ExcelWriter(
            caminho,
            engine="openpyxl",
        ) as writer:

            df.to_excel(
                writer,
                sheet_name="Planejamento",
                index=False,
            )

            materia_prima.to_excel(
                writer,
                sheet_name="Materia_Prima",
                index=False,
            )

            comercial.to_excel(
                writer,
                sheet_name="Comercial",
                index=False,
            )

            consumo.to_excel(
                writer,
                sheet_name="Consumo",
                index=False,
            )

            consolidado.to_excel(
                writer,
                sheet_name="Consolidado",
                index=False,
            )

            resumo.to_excel(
                writer,
                sheet_name="Resumo",
                index=False,
            )

            resumo_unidade.to_excel(
                writer,
                sheet_name="Resumo_Unidade",
                index=False,
            )

            estoque.to_excel(
                writer,
                sheet_name="Para_Estoque",
                index=False,
            )

        return caminho