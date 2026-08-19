from __future__ import annotations

from pathlib import Path

import pandas as pd


class MotorEngenharia:
    """
    Motor de Engenharia da AIZI Engineering AI.

    RESPONSABILIDADES
    -----------------
    1. Carregar o cadastro de produtos do TOTVS.
    2. Receber a explosão da BOM.
    3. Cruzar componentes da BOM com o cadastro TOTVS.
    4. Garantir descrição e unidade de medida do cadastro.
    5. Aplicar a classificação oficial AIZI.
    6. Entregar um DataFrame estável para o PlanejadorNecessidades.

    REGRA OFICIAL AIZI
    ------------------
        G2 -> MATÉRIA_PRIMA

        G1 -> ITEM_COMERCIAL
        G3 -> ITEM_COMERCIAL
        K  -> ITEM_COMERCIAL

        I  -> FABRICADO

        demais -> FABRICADO

    IMPORTANTE
    ----------
    O Motor de Engenharia NÃO:

        - multiplica quantidade;
        - calcula necessidade;
        - considera estoque;
        - calcula saldo;
        - calcula compras;
        - calcula corte.

    A quantidade recebida da explosão permanece inalterada.
    """

    # ==========================================================
    # INICIALIZAÇÃO
    # ==========================================================

    def __init__(self, caminho_cadastro=None):

        if caminho_cadastro is None:

            caminho_cadastro = (
                Path(__file__).resolve().parents[2]
                / "data"
                / "cadastro_produtos.xlsx"
            )

        self.caminho_cadastro = Path(
            caminho_cadastro
        )

        self.cadastro = None

    # ==========================================================
    # CARREGAR CADASTRO
    # ==========================================================

    def carregar_cadastro(self):

        if not self.caminho_cadastro.exists():

            raise FileNotFoundError(
                "\nCadastro de produtos não encontrado:\n"
                f"{self.caminho_cadastro}\n\n"
                "Coloque o arquivo "
                "cadastro_produtos.xlsx "
                "dentro da pasta data."
            )

        print()
        print("=" * 60)
        print("CARREGANDO CADASTRO DE PRODUTOS")
        print("=" * 60)

        self.cadastro = pd.read_excel(
            self.caminho_cadastro,
            sheet_name="Consulta Atual",
            dtype=str,
        )

        # ------------------------------------------------------
        # NORMALIZA NOMES DAS COLUNAS
        # ------------------------------------------------------

        self.cadastro.columns = [
            str(coluna).strip()
            for coluna in self.cadastro.columns
        ]

        # ------------------------------------------------------
        # COLUNAS OBRIGATÓRIAS
        # ------------------------------------------------------

        colunas_necessarias = [
            "CODIGO_PRODUTO",
            "DESCRICAO_PRODUTO",
            "UNIDADE_MEDIDA",
            "TIPO",
            "DESCRICAO_TIPO",
            "ITEM_FANTASMA",
        ]

        faltantes = [
            coluna
            for coluna in colunas_necessarias
            if coluna not in self.cadastro.columns
        ]

        if faltantes:

            raise ValueError(
                "O cadastro TOTVS não possui as "
                "colunas necessárias:\n"
                + "\n".join(
                    f"- {coluna}"
                    for coluna in faltantes
                )
            )

        # ------------------------------------------------------
        # NORMALIZA CAMPOS
        # ------------------------------------------------------

        for coluna in colunas_necessarias:

            self.cadastro[coluna] = (
                self.cadastro[coluna]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        # ------------------------------------------------------
        # NORMALIZA CÓDIGO
        # ------------------------------------------------------

        self.cadastro[
            "CODIGO_PRODUTO"
        ] = (
            self.cadastro[
                "CODIGO_PRODUTO"
            ]
            .str.upper()
            .str.strip()
        )

        # ------------------------------------------------------
        # REMOVE CÓDIGOS VAZIOS
        # ------------------------------------------------------

        self.cadastro = self.cadastro[
            self.cadastro[
                "CODIGO_PRODUTO"
            ] != ""
        ].copy()

        # ------------------------------------------------------
        # UM REGISTRO POR CÓDIGO
        # ------------------------------------------------------

        self.cadastro = (
            self.cadastro
            .drop_duplicates(
                subset=[
                    "CODIGO_PRODUTO"
                ],
                keep="first",
            )
            .reset_index(drop=True)
        )

        print(
            "Produtos carregados: "
            f"{len(self.cadastro):,}".replace(
                ",",
                ".",
            )
        )

        return self.cadastro

    # ==========================================================
    # NORMALIZA VALOR
    # ==========================================================

    @staticmethod
    def _normalizar(valor):

        if valor is None:
            return ""

        try:

            if pd.isna(valor):
                return ""

        except (
            TypeError,
            ValueError,
        ):

            pass

        return (
            str(valor)
            .replace('="', "")
            .replace('"', "")
            .strip()
            .upper()
        )

    # ==========================================================
    # NORMALIZA DATAFRAME
    # ==========================================================

    @staticmethod
    def _normalizar_dataframe(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        if not isinstance(
            df,
            pd.DataFrame,
        ):

            df = pd.DataFrame(df)

        df = df.copy()

        # ------------------------------------------------------
        # REMOVE COLUNAS DUPLICADAS
        # ------------------------------------------------------

        df = df.loc[
            :,
            ~df.columns.duplicated()
        ].copy()

        # ------------------------------------------------------
        # NORMALIZA NOMES
        # ------------------------------------------------------

        df.columns = [
            str(coluna).strip()
            for coluna in df.columns
        ]

        return df

    # ==========================================================
    # CLASSIFICAÇÃO AIZI
    # ==========================================================

    @classmethod
    def classificar_aizi(
        cls,
        codigo,
    ):

        codigo = cls._normalizar(
            codigo
        )

        if not codigo:
            return "FABRICADO"

        # ------------------------------------------------------
        # G2 = MATÉRIA-PRIMA
        # ------------------------------------------------------

        if codigo.startswith("G2"):
            return "MATÉRIA_PRIMA"

        # ------------------------------------------------------
        # G1 / G3 = COMERCIAL
        # ------------------------------------------------------

        if (
            codigo.startswith("G1")
            or codigo.startswith("G3")
        ):

            return "ITEM_COMERCIAL"

        # ------------------------------------------------------
        # K = COMERCIAL
        # ------------------------------------------------------

        if codigo.startswith("K"):
            return "ITEM_COMERCIAL"

        # ------------------------------------------------------
        # I = FABRICADO
        # ------------------------------------------------------

        if codigo.startswith("I"):
            return "FABRICADO"

        # ------------------------------------------------------
        # DEMAIS = FABRICADO
        # ------------------------------------------------------

        return "FABRICADO"

    # ==========================================================
    # COMPATIBILIDADE
    # ==========================================================

    @classmethod
    def classificar_item(
        cls,
        codigo,
        tipo=None,
        descricao_tipo=None,
        item_fantasma=None,
    ):

        return cls.classificar_aizi(
            codigo
        )

    # ==========================================================
    # PREPARA CADASTRO PARA MERGE
    # ==========================================================

    def _preparar_cadastro(self):

        if self.cadastro is None:

            self.carregar_cadastro()

        cadastro = self.cadastro[
            [
                "CODIGO_PRODUTO",
                "DESCRICAO_PRODUTO",
                "UNIDADE_MEDIDA",
                "TIPO",
                "DESCRICAO_TIPO",
                "ITEM_FANTASMA",
            ]
        ].copy()

        cadastro = cadastro.rename(
            columns={
                "CODIGO_PRODUTO":
                    "componente"
            }
        )

        cadastro["componente"] = (
            cadastro["componente"]
            .apply(self._normalizar)
        )

        cadastro = (
            cadastro
            .drop_duplicates(
                subset=[
                    "componente"
                ],
                keep="first",
            )
            .reset_index(drop=True)
        )

        return cadastro

    # ==========================================================
    # ENRIQUECER
    # ==========================================================

    def enriquecer(
        self,
        resultado_explosao,
    ):

        if self.cadastro is None:

            self.carregar_cadastro()

        if resultado_explosao is None:

            raise ValueError(
                "O resultado da explosão "
                "está vazio."
            )

        resultado = (
            self._normalizar_dataframe(
                resultado_explosao
            )
        )

        if resultado.empty:

            raise ValueError(
                "O resultado da explosão "
                "está vazio."
            )

        # ------------------------------------------------------
        # COMPATIBILIDADE COM QUANTIDADE
        # ------------------------------------------------------

        if (
            "quantidade_total"
            not in resultado.columns
        ):

            if (
                "quantidade"
                in resultado.columns
            ):

                resultado[
                    "quantidade_total"
                ] = resultado[
                    "quantidade"
                ]

            else:

                raise ValueError(
                    "A explosão precisa possuir "
                    "'quantidade_total' ou "
                    "'quantidade'."
                )

        # ------------------------------------------------------
        # COMPATIBILIDADE COM COMPONENTE
        # ------------------------------------------------------

        if (
            "componente"
            not in resultado.columns
        ):

            candidatos = [
                "produto",
                "filho",
                "codigo",
                "item",
            ]

            encontrado = None

            for candidato in candidatos:

                if candidato in resultado.columns:

                    encontrado = candidato
                    break

            if encontrado is None:

                raise ValueError(
                    "A explosão precisa possuir "
                    "a coluna 'componente'."
                )

            resultado = resultado.rename(
                columns={
                    encontrado:
                        "componente"
                }
            )

        # ------------------------------------------------------
        # NORMALIZA COMPONENTE
        # ------------------------------------------------------

        resultado[
            "componente"
        ] = (
            resultado[
                "componente"
            ]
            .apply(self._normalizar)
        )

        # ------------------------------------------------------
        # NORMALIZA QUANTIDADE
        # ------------------------------------------------------

        resultado[
            "quantidade_total"
        ] = pd.to_numeric(
            resultado[
                "quantidade_total"
            ],
            errors="coerce",
        ).fillna(0.0)

        # ------------------------------------------------------
        # REMOVE COMPONENTES VAZIOS
        # ------------------------------------------------------

        resultado = resultado[
            resultado[
                "componente"
            ] != ""
        ].copy()

        # ------------------------------------------------------
        # CADASTRO
        # ------------------------------------------------------

        cadastro = (
            self._preparar_cadastro()
        )

        # ------------------------------------------------------
        # REMOVE COLUNAS QUE SERÃO TRAZIDAS
        # PELO CADASTRO
        #
        # ISSO EVITA O PROBLEMA DE COLUNAS
        # DUPLICADAS / SUFIXOS.
        # ------------------------------------------------------

        colunas_cadastro = [
            "DESCRICAO_PRODUTO",
            "UNIDADE_MEDIDA",
            "TIPO",
            "DESCRICAO_TIPO",
            "ITEM_FANTASMA",
        ]

        resultado = resultado.drop(
            columns=[
                coluna
                for coluna in colunas_cadastro
                if coluna in resultado.columns
            ],
            errors="ignore",
        )

        # ------------------------------------------------------
        # MERGE
        # ------------------------------------------------------

        resultado = resultado.merge(
            cadastro,
            on="componente",
            how="left",
            validate="many_to_one",
        )

        # ------------------------------------------------------
        # GARANTE CAMPOS DO CADASTRO
        # ------------------------------------------------------

        for coluna in colunas_cadastro:

            if coluna not in resultado.columns:

                resultado[coluna] = ""

            resultado[coluna] = (
                resultado[coluna]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        # ------------------------------------------------------
        # CADASTRO ENCONTRADO
        # ------------------------------------------------------

        resultado[
            "cadastro_encontrado"
        ] = (
            resultado[
                "DESCRICAO_PRODUTO"
            ]
            .str.strip()
            != ""
        )

        # ------------------------------------------------------
        # CLASSIFICAÇÃO OFICIAL AIZI
        # ------------------------------------------------------

        resultado[
            "CLASSIFICACAO_AIZI"
        ] = (
            resultado[
                "componente"
            ]
            .apply(
                self.classificar_aizi
            )
        )

        # ------------------------------------------------------
        # CLASSIFICAÇÃO PADRÃO
        # ------------------------------------------------------

        resultado[
            "CLASSIFICACAO"
        ] = resultado[
            "CLASSIFICACAO_AIZI"
        ]

        # ------------------------------------------------------
        # TIPO ENGENHARIA
        # ------------------------------------------------------

        resultado[
            "TIPO_ENGENHARIA"
        ] = resultado[
            "CLASSIFICACAO_AIZI"
        ]

        # ------------------------------------------------------
        # CATEGORIA PLANEJAMENTO
        # ------------------------------------------------------

        resultado[
            "categoria_planejamento"
        ] = resultado[
            "CLASSIFICACAO_AIZI"
        ]

        # ------------------------------------------------------
        # UNIDADE
        # ------------------------------------------------------

        resultado[
            "unidade_medida"
        ] = resultado[
            "UNIDADE_MEDIDA"
        ]

        # ------------------------------------------------------
        # DESCRIÇÃO
        # ------------------------------------------------------

        resultado[
            "descricao"
        ] = resultado[
            "DESCRICAO_PRODUTO"
        ]

        # ------------------------------------------------------
        # STATUS CLASSIFICAÇÃO
        # ------------------------------------------------------

        resultado[
            "classificacao_encontrada"
        ] = (
            resultado[
                "CLASSIFICACAO_AIZI"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            != ""
        )

        # ------------------------------------------------------
        # STATUS UNIDADE
        # ------------------------------------------------------

        resultado[
            "unidade_encontrada"
        ] = (
            resultado[
                "UNIDADE_MEDIDA"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            != ""
        )

        # ------------------------------------------------------
        # REMOVE QUALQUER DUPLICIDADE DE COLUNA
        # ------------------------------------------------------

        resultado = resultado.loc[
            :,
            ~resultado.columns.duplicated()
        ].copy()

        # ------------------------------------------------------
        # ORDENA
        # ------------------------------------------------------

        resultado = (
            resultado
            .sort_values(
                "componente"
            )
            .reset_index(
                drop=True
            )
        )

        return resultado

    # ==========================================================
    # MÉTODO PADRÃO PARA APLICAÇÃO
    # ==========================================================

    def enriquecer_explosao(
        self,
        resultado_explosao,
    ):

        return self.enriquecer(
            resultado_explosao
        )

    # ==========================================================
    # COMPATIBILIDADE: PROCESSAR
    # ==========================================================

    def processar(
        self,
        resultado_explosao,
    ):

        return self.enriquecer(
            resultado_explosao
        )

    # ==========================================================
    # COMPATIBILIDADE: EXECUTAR
    # ==========================================================

    def executar(
        self,
        resultado_explosao,
    ):

        return self.enriquecer(
            resultado_explosao
        )

    # ==========================================================
    # RELATÓRIO
    # ==========================================================

    def gerar_relatorio(
        self,
        resultado_explosao,
    ):

        resultado = self.enriquecer(
            resultado_explosao
        )

        print()
        print("=" * 80)
        print(
            "RESULTADO DA EXPLOSÃO + "
            "CADASTRO TOTVS"
        )
        print("=" * 80)

        print()
        print(
            "Primeiros 20 componentes:"
        )
        print()

        colunas = [
            "componente",
            "descricao",
            "unidade_medida",
            "CLASSIFICACAO_AIZI",
            "quantidade_total",
            "cadastro_encontrado",
        ]

        colunas = [
            coluna
            for coluna in colunas
            if coluna in resultado.columns
        ]

        print(
            resultado[
                colunas
            ]
            .head(20)
            .to_string(
                index=False
            )
        )

        # ------------------------------------------------------
        # RESUMO
        # ------------------------------------------------------

        total = len(resultado)

        encontrados = int(
            resultado[
                "cadastro_encontrado"
            ].sum()
        )

        nao_encontrados = (
            total - encontrados
        )

        print()
        print("=" * 80)
        print("RESUMO")
        print("=" * 80)

        print(
            f"Componentes processados: "
            f"{total}"
        )

        print(
            f"Encontrados no cadastro: "
            f"{encontrados}"
        )

        print(
            f"Não encontrados no cadastro: "
            f"{nao_encontrados}"
        )

        # ------------------------------------------------------
        # CLASSIFICAÇÃO
        # ------------------------------------------------------

        print()
        print(
            "CLASSIFICAÇÃO AIZI"
        )
        print("-" * 80)

        resumo = (
            resultado[
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

        return resultado