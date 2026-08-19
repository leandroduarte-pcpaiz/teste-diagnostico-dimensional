from __future__ import annotations

import pandas as pd


class ApuradorFabricacao:
    """
    Apurador de fabricação do AIZI Engineering AI.

    REGRA DE NEGÓCIO
    ----------------

    G2...
        -> MATÉRIA_PRIMA

    G... diferente de G2
        -> ITEM_COMERCIAL

    K...
        -> ITEM_COMERCIAL

    Qualquer outro código
        -> FABRICADO

    IMPORTANTE
    ----------
    ITEM_FANTASMA NÃO participa da classificação.

    O item fantasma continua sendo um item real da estrutura:

        - continua na explosão;
        - continua na quantidade;
        - continua no planejamento;
        - continua sendo classificado normalmente.

    O campo ITEM_FANTASMA existe apenas para o comportamento
    de abertura de OP no TOTVS e não deve interferir no AIZI.
    """

    COLUNA_CODIGO = "componente"

    CLASSIFICACAO_FABRICADO = "FABRICADO"
    CLASSIFICACAO_MATERIA_PRIMA = "MATERIA_PRIMA"
    CLASSIFICACAO_ITEM_COMERCIAL = "ITEM_COMERCIAL"

    def __init__(self):
        pass

    # =========================================================
    # NORMALIZAÇÃO
    # =========================================================

    @staticmethod
    def normalizar_codigo(valor) -> str:
        """
        Normaliza o código utilizado na classificação.

        O valor original da coluna não é alterado.
        """

        if pd.isna(valor):
            return ""

        return (
            str(valor)
            .strip()
            .upper()
        )

    # =========================================================
    # CLASSIFICAÇÃO
    # =========================================================

    def classificar_codigo(self, codigo: str) -> str:
        """
        Classifica um componente segundo a regra AIZI.

        Regras:

            G2...       -> MATÉRIA_PRIMA
            G...        -> ITEM_COMERCIAL
            K...        -> ITEM_COMERCIAL
            demais      -> FABRICADO
        """

        codigo = self.normalizar_codigo(
            codigo
        )

        if not codigo:
            return "NAO_CLASSIFICADO"

        # -----------------------------------------------------
        # MATÉRIA-PRIMA
        # -----------------------------------------------------

        if codigo.startswith("G2"):
            return self.CLASSIFICACAO_MATERIA_PRIMA

        # -----------------------------------------------------
        # ITEM COMERCIAL
        # -----------------------------------------------------

        if codigo.startswith("G"):
            return self.CLASSIFICACAO_ITEM_COMERCIAL

        if codigo.startswith("K"):
            return self.CLASSIFICACAO_ITEM_COMERCIAL

        # -----------------------------------------------------
        # FABRICADO
        # -----------------------------------------------------

        return self.CLASSIFICACAO_FABRICADO

    # =========================================================
    # CLASSIFICAR DATAFRAME
    # =========================================================

    def classificar(self, resultado_enriquecido):
        """
        Recebe o resultado enriquecido pelo MotorEngenharia.

        Acrescenta:

            CLASSIFICACAO_AIZI
            FABRICAR
            COMPRAR
            MATERIA_PRIMA
            ITEM_COMERCIAL

        Não remove componentes.

        Não altera:

            componente
            quantidade_total
            TIPO
            DESCRICAO_TIPO
            ITEM_FANTASMA
        """

        if resultado_enriquecido is None:
            raise ValueError(
                "O resultado enriquecido está vazio."
            )

        if not isinstance(
            resultado_enriquecido,
            pd.DataFrame
        ):
            resultado_enriquecido = pd.DataFrame(
                resultado_enriquecido
            )

        if resultado_enriquecido.empty:
            raise ValueError(
                "O resultado enriquecido está vazio."
            )

        resultado = (
            resultado_enriquecido.copy()
        )

        # -----------------------------------------------------
        # Padronização dos nomes
        # -----------------------------------------------------

        resultado.columns = (
            resultado.columns
            .astype(str)
            .str.strip()
        )

        if self.COLUNA_CODIGO not in (
            resultado.columns
        ):
            raise ValueError(
                "O resultado enriquecido precisa possuir "
                "a coluna 'componente'."
            )

        # -----------------------------------------------------
        # Classificação
        # -----------------------------------------------------

        resultado["CLASSIFICACAO_AIZI"] = (
            resultado[
                self.COLUNA_CODIGO
            ]
            .apply(
                self.classificar_codigo
            )
        )

        # -----------------------------------------------------
        # Indicadores
        # -----------------------------------------------------

        resultado["FABRICAR"] = (
            resultado["CLASSIFICACAO_AIZI"]
            == self.CLASSIFICACAO_FABRICADO
        )

        resultado["COMPRAR"] = (
            resultado["CLASSIFICACAO_AIZI"]
            == self.CLASSIFICACAO_ITEM_COMERCIAL
        )

        resultado["MATERIA_PRIMA"] = (
            resultado["CLASSIFICACAO_AIZI"]
            == self.CLASSIFICACAO_MATERIA_PRIMA
        )

        resultado["ITEM_COMERCIAL"] = (
            resultado["CLASSIFICACAO_AIZI"]
            == self.CLASSIFICACAO_ITEM_COMERCIAL
        )

        # -----------------------------------------------------
        # IMPORTANTE:
        # ITEM_FANTASMA não é utilizado aqui.
        #
        # Se existir, permanece exatamente como veio.
        # -----------------------------------------------------

        return resultado

    # =========================================================
    # RESUMO
    # =========================================================

    def gerar_resumo(
        self,
        resultado_classificado
    ):
        """
        Gera resumo quantitativo das classificações.
        """

        if resultado_classificado is None:
            raise ValueError(
                "O resultado classificado está vazio."
            )

        if not isinstance(
            resultado_classificado,
            pd.DataFrame
        ):
            resultado_classificado = (
                pd.DataFrame(
                    resultado_classificado
                )
            )

        if (
            "CLASSIFICACAO_AIZI"
            not in resultado_classificado.columns
        ):
            raise ValueError(
                "O resultado ainda não foi classificado."
            )

        resumo = (
            resultado_classificado[
                "CLASSIFICACAO_AIZI"
            ]
            .value_counts()
            .rename_axis(
                "CLASSIFICACAO_AIZI"
            )
            .reset_index(
                name="QUANTIDADE_ITENS"
            )
        )

        return resumo

    # =========================================================
    # RESUMO POR CLASSIFICAÇÃO
    # =========================================================

    def gerar_resumo_detalhado(
        self,
        resultado_classificado
    ):
        """
        Gera um resumo adicional mostrando:

            classificação
            quantidade de componentes
            quantidade total

        A quantidade_total da BOM não é alterada.
        """

        if (
            "CLASSIFICACAO_AIZI"
            not in resultado_classificado.columns
        ):
            raise ValueError(
                "O resultado ainda não foi classificado."
            )

        if (
            "quantidade_total"
            not in resultado_classificado.columns
        ):
            raise ValueError(
                "O resultado precisa possuir "
                "a coluna 'quantidade_total'."
            )

        dados = (
            resultado_classificado.copy()
        )

        dados["quantidade_total"] = (
            pd.to_numeric(
                dados["quantidade_total"],
                errors="coerce"
            )
            .fillna(0)
        )

        resumo = (
            dados
            .groupby(
                "CLASSIFICACAO_AIZI",
                dropna=False
            )
            .agg(
                quantidade_itens=(
                    "componente",
                    "count"
                ),
                quantidade_total=(
                    "quantidade_total",
                    "sum"
                )
            )
            .reset_index()
        )

        return resumo

    # =========================================================
    # EXECUÇÃO COMPLETA
    # =========================================================

    def executar(
        self,
        resultado_enriquecido
    ):
        """
        Executa a classificação e gera os resumos.

        Retorna:

            resultado_classificado
            resumo
        """

        resultado_classificado = (
            self.classificar(
                resultado_enriquecido
            )
        )

        resumo = (
            self.gerar_resumo(
                resultado_classificado
            )
        )

        return (
            resultado_classificado,
            resumo
        )

    # =========================================================
    # MOSTRAR RESUMO
    # =========================================================

    def mostrar_resumo(
        self,
        resultado_classificado
    ):
        """
        Mostra o resumo no terminal.
        """

        resumo = (
            self.gerar_resumo_detalhado(
                resultado_classificado
            )
        )

        print()
        print("=" * 80)
        print("APURAÇÃO DE FABRICAÇÃO")
        print("=" * 80)
        print()

        for _, linha in resumo.iterrows():

            classificacao = (
                linha[
                    "CLASSIFICACAO_AIZI"
                ]
            )

            quantidade_itens = int(
                linha[
                    "quantidade_itens"
                ]
            )

            quantidade_total = (
                linha[
                    "quantidade_total"
                ]
            )

            print(
                f"{classificacao:<25}"
                f"Itens: {quantidade_itens:>6}"
                f" | Quantidade: "
                f"{quantidade_total:,.3f}"
            )

        print()

        print(
            f"Total de componentes: "
            f"{len(resultado_classificado)}"
        )

        # -----------------------------------------------------
        # Informação sobre fantasmas
        # -----------------------------------------------------

        if (
            "ITEM_FANTASMA"
            in resultado_classificado.columns
        ):

            fantasmas = (
                resultado_classificado[
                    resultado_classificado[
                        "ITEM_FANTASMA"
                    ]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    == "S"
                ]
            )

            print(
                f"Itens fantasma presentes: "
                f"{len(fantasmas)}"
            )

            print(
                "ITEM_FANTASMA não altera "
                "a classificação nem a quantidade."
            )

        print()

        return resumo