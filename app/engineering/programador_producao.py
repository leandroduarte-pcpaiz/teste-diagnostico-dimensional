from __future__ import annotations

import pandas as pd


class ProgramadorProducao:
    """
    Prepara a necessidade calculada pelo PlanejadorNecessidades
    para programação da produção.

    NÃO considera:
    - estoque
    - compras
    - saldo
    - reservas
    - disponibilidade

    RESPONSABILIDADE:
    - receber a necessidade dos conjuntos;
    - consolidar os componentes;
    - identificar o que será FABRICADO;
    - identificar MATÉRIA-PRIMA;
    - identificar ITEM_COMERCIAL;
    - identificar CONSUMO;
    - gerar uma estrutura única para programação.

    REGRA:
        quantidade_necessaria
        = quantidade necessária para produzir os conjuntos informados.

    Este módulo NÃO recalcula a BOM.
    Este módulo NÃO multiplica novamente a quantidade.
    Este módulo NÃO faz abatimento de estoque.
    """

    COLUNAS_BASE = [
        "CODIGO",
        "DESCRICAO",
        "CLASSIFICACAO",
        "UNIDADE_MEDIDA",
        "quantidade_por_conjunto",
        "quantidade_necessaria",
    ]

    COLUNAS_SAIDA = [
        "CODIGO",
        "DESCRICAO",
        "CLASSIFICACAO",
        "UNIDADE_MEDIDA",
        "quantidade_por_conjunto",
        "quantidade_necessaria",
        "STATUS_PROGRAMACAO",
    ]

    def __init__(self, df_necessidades: pd.DataFrame):
        if not isinstance(df_necessidades, pd.DataFrame):
            raise TypeError(
                "df_necessidades deve ser um pandas.DataFrame."
            )

        self.df = df_necessidades.copy()

    # ==========================================================
    # NORMALIZAÇÃO
    # ==========================================================

    @staticmethod
    def _numero(valor) -> float:
        try:
            if pd.isna(valor):
                return 0.0

            return float(valor)

        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _texto(valor) -> str:
        if pd.isna(valor):
            return ""

        return str(valor).strip()

    def _preparar(self) -> pd.DataFrame:

        df = self.df.copy()

        if df.empty:
            return pd.DataFrame(columns=self.COLUNAS_BASE)

        # ------------------------------------------------------
        # NORMALIZAÇÃO DE NOMES
        # ------------------------------------------------------

        mapa = {
            "codigo": "CODIGO",
            "Codigo": "CODIGO",
            "Código": "CODIGO",
            "codigo_produto": "CODIGO",
            "CODIGO_PRODUTO": "CODIGO",
            "CODIGO": "CODIGO",

            "descricao": "DESCRICAO",
            "Descricao": "DESCRICAO",
            "Descrição": "DESCRICAO",
            "DESCRICAO_PRODUTO": "DESCRICAO",
            "DESCRICAO": "DESCRICAO",

            "classificacao": "CLASSIFICACAO",
            "CLASSIFICACAO_PLANEJAMENTO": "CLASSIFICACAO",
            "CLASSIFICACAO": "CLASSIFICACAO",

            "unidade": "UNIDADE_MEDIDA",
            "UNIDADE": "UNIDADE_MEDIDA",
            "unidade_medida": "UNIDADE_MEDIDA",
            "UNIDADE_MEDIDA": "UNIDADE_MEDIDA",

            "quantidade": "quantidade_necessaria",
            "QUANTIDADE": "quantidade_necessaria",
            "necessidade": "quantidade_necessaria",
            "NECESSIDADE": "quantidade_necessaria",
            "quantidade_necessaria": "quantidade_necessaria",

            "quantidade_por_conjunto": "quantidade_por_conjunto",
        }

        df = df.rename(columns=mapa)

        # ------------------------------------------------------
        # COLUNAS OBRIGATÓRIAS
        # ------------------------------------------------------

        obrigatorias = [
            "CODIGO",
            "CLASSIFICACAO",
            "UNIDADE_MEDIDA",
            "quantidade_necessaria",
        ]

        for coluna in obrigatorias:

            if coluna not in df.columns:

                raise ValueError(
                    f"Coluna obrigatória não encontrada: {coluna}"
                )

        # ------------------------------------------------------
        # COLUNAS OPCIONAIS
        # ------------------------------------------------------

        if "DESCRICAO" not in df.columns:
            df["DESCRICAO"] = ""

        if "quantidade_por_conjunto" not in df.columns:
            df["quantidade_por_conjunto"] = 0.0

        # ------------------------------------------------------
        # TEXTOS
        # ------------------------------------------------------

        df["CODIGO"] = df["CODIGO"].apply(
            lambda x: self._texto(x).upper()
        )

        df["DESCRICAO"] = df["DESCRICAO"].apply(
            self._texto
        )

        df["CLASSIFICACAO"] = df["CLASSIFICACAO"].apply(
            lambda x: self._texto(x).upper()
        )

        df["UNIDADE_MEDIDA"] = df["UNIDADE_MEDIDA"].apply(
            lambda x: self._texto(x).upper()
        )

        # ------------------------------------------------------
        # NÚMEROS
        # ------------------------------------------------------

        df["quantidade_por_conjunto"] = pd.to_numeric(
            df["quantidade_por_conjunto"],
            errors="coerce",
        ).fillna(0.0)

        df["quantidade_necessaria"] = pd.to_numeric(
            df["quantidade_necessaria"],
            errors="coerce",
        ).fillna(0.0)

        # Não existe necessidade negativa.
        df["quantidade_necessaria"] = (
            df["quantidade_necessaria"].clip(lower=0)
        )

        # ------------------------------------------------------
        # REMOVE LINHAS SEM CÓDIGO
        # ------------------------------------------------------

        df = df[
            df["CODIGO"].str.strip() != ""
        ].copy()

        return df

    # ==========================================================
    # PROGRAMAÇÃO COMPLETA
    # ==========================================================

    def gerar_programacao(self) -> pd.DataFrame:

        df = self._preparar()

        if df.empty:
            return pd.DataFrame(
                columns=self.COLUNAS_SAIDA
            )

        # ------------------------------------------------------
        # CONSOLIDA POR:
        #
        # código
        # descrição
        # classificação
        # unidade
        #
        # IMPORTANTE:
        # KG não é misturado com PC,
        # MT não é misturado com UN etc.
        # ------------------------------------------------------

        resultado = (
            df.groupby(
                [
                    "CODIGO",
                    "DESCRICAO",
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                ],
                as_index=False,
                dropna=False,
            )
            .agg(
                quantidade_por_conjunto=(
                    "quantidade_por_conjunto",
                    "sum",
                ),
                quantidade_necessaria=(
                    "quantidade_necessaria",
                    "sum",
                ),
            )
        )

        # ------------------------------------------------------
        # STATUS
        # ------------------------------------------------------

        resultado["STATUS_PROGRAMACAO"] = resultado[
            "quantidade_necessaria"
        ].apply(
            lambda x:
                "PROGRAMAR"
                if x > 0
                else "SEM NECESSIDADE"
        )

        return resultado[
            self.COLUNAS_SAIDA
        ].reset_index(drop=True)

    # ==========================================================
    # FABRICAÇÃO
    # ==========================================================

    def fabricar(self) -> pd.DataFrame:

        df = self.gerar_programacao()

        if df.empty:
            return df

        return df[
            (df["CLASSIFICACAO"] == "FABRICADO")
            & (df["quantidade_necessaria"] > 0)
        ].reset_index(drop=True)

    # ==========================================================
    # MATÉRIA-PRIMA
    # ==========================================================

    def materia_prima(self) -> pd.DataFrame:

        df = self.gerar_programacao()

        if df.empty:
            return df

        return df[
            (df["CLASSIFICACAO"] == "MATERIA_PRIMA")
            & (df["quantidade_necessaria"] > 0)
        ].reset_index(drop=True)

    # ==========================================================
    # COMERCIAL
    # ==========================================================

    def comercial(self) -> pd.DataFrame:

        df = self.gerar_programacao()

        if df.empty:
            return df

        return df[
            (df["CLASSIFICACAO"] == "ITEM_COMERCIAL")
            & (df["quantidade_necessaria"] > 0)
        ].reset_index(drop=True)

    # ==========================================================
    # CONSUMO
    # ==========================================================

    def consumo(self) -> pd.DataFrame:

        df = self.gerar_programacao()

        if df.empty:
            return df

        return df[
            (df["CLASSIFICACAO"] == "CONSUMO")
            & (df["quantidade_necessaria"] > 0)
        ].reset_index(drop=True)

    # ==========================================================
    # RESUMO
    # ==========================================================

    def resumo(self) -> pd.DataFrame:

        df = self.gerar_programacao()

        if df.empty:

            return pd.DataFrame(
                columns=[
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                    "quantidade_itens",
                    "quantidade_total",
                ]
            )

        resultado = (
            df.groupby(
                [
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                ],
                as_index=False,
            )
            .agg(
                quantidade_itens=(
                    "CODIGO",
                    "nunique",
                ),
                quantidade_total=(
                    "quantidade_necessaria",
                    "sum",
                ),
            )
            .sort_values(
                [
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                ]
            )
            .reset_index(drop=True)
        )

        return resultado

    # ==========================================================
    # RESUMO DE PRODUÇÃO
    # ==========================================================

    def resumo_producao(self) -> pd.DataFrame:

        df = self.fabricar()

        if df.empty:

            return pd.DataFrame(
                columns=[
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                    "quantidade_itens",
                    "quantidade_total",
                ]
            )

        return (
            df.groupby(
                [
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                ],
                as_index=False,
            )
            .agg(
                quantidade_itens=(
                    "CODIGO",
                    "nunique",
                ),
                quantidade_total=(
                    "quantidade_necessaria",
                    "sum",
                ),
            )
            .sort_values(
                [
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                ]
            )
            .reset_index(drop=True)
        )

    # ==========================================================
    # ESTRUTURA PARA PROGRAMAÇÃO
    # ==========================================================

    def estrutura_programacao(self) -> dict:

        return {
            "PROGRAMAR_FABRICACAO": self.fabricar(),
            "NECESSIDADE_MATERIA_PRIMA": self.materia_prima(),
            "NECESSIDADE_ITEM_COMERCIAL": self.comercial(),
            "NECESSIDADE_CONSUMO": self.consumo(),
            "PROGRAMACAO_COMPLETA": self.gerar_programacao(),
            "RESUMO": self.resumo(),
        }

    # ==========================================================
    # EXPORTAÇÃO
    # ==========================================================

    def salvar(
        self,
        caminho: str,
    ) -> None:

        df = self.gerar_programacao()

        df.to_csv(
            caminho,
            index=False,
            sep=";",
            encoding="utf-8-sig",
        )

    # ==========================================================
    # EXPORTAÇÃO COMPLETA
    # ==========================================================

    def salvar_completa(
        self,
        caminho: str,
    ) -> None:

        programacao = self.gerar_programacao()
        resumo = self.resumo()
        fabricacao = self.fabricar()
        materia_prima = self.materia_prima()
        comercial = self.comercial()
        consumo = self.consumo()

        with open(
            caminho,
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as arquivo:

            arquivo.write(
                "AIZI ENGINEERING AI\n"
            )

            arquivo.write(
                "PROGRAMACAO DA PRODUCAO\n"
            )

            arquivo.write(
                "=" * 100 + "\n\n"
            )

            # --------------------------------------------------
            # FABRICAÇÃO
            # --------------------------------------------------

            arquivo.write(
                "PROGRAMAR FABRICACAO\n"
            )

            arquivo.write(
                "-" * 100 + "\n"
            )

            fabricacao.to_csv(
                arquivo,
                index=False,
                sep=";",
            )

            arquivo.write("\n\n")

            # --------------------------------------------------
            # MATÉRIA-PRIMA
            # --------------------------------------------------

            arquivo.write(
                "NECESSIDADE DE MATERIA-PRIMA\n"
            )

            arquivo.write(
                "-" * 100 + "\n"
            )

            materia_prima.to_csv(
                arquivo,
                index=False,
                sep=";",
            )

            arquivo.write("\n\n")

            # --------------------------------------------------
            # COMERCIAL
            # --------------------------------------------------

            arquivo.write(
                "NECESSIDADE DE ITENS COMERCIAIS\n"
            )

            arquivo.write(
                "-" * 100 + "\n"
            )

            comercial.to_csv(
                arquivo,
                index=False,
                sep=";",
            )

            arquivo.write("\n\n")

            # --------------------------------------------------
            # CONSUMO
            # --------------------------------------------------

            arquivo.write(
                "NECESSIDADE DE CONSUMO\n"
            )

            arquivo.write(
                "-" * 100 + "\n"
            )

            consumo.to_csv(
                arquivo,
                index=False,
                sep=";",
            )

            arquivo.write("\n\n")

            # --------------------------------------------------
            # PROGRAMAÇÃO COMPLETA
            # --------------------------------------------------

            arquivo.write(
                "PROGRAMACAO COMPLETA\n"
            )

            arquivo.write(
                "-" * 100 + "\n"
            )

            programacao.to_csv(
                arquivo,
                index=False,
                sep=";",
            )

            arquivo.write("\n\n")

            # --------------------------------------------------
            # RESUMO
            # --------------------------------------------------

            arquivo.write(
                "RESUMO\n"
            )

            arquivo.write(
                "-" * 100 + "\n"
            )

            resumo.to_csv(
                arquivo,
                index=False,
                sep=";",
            )