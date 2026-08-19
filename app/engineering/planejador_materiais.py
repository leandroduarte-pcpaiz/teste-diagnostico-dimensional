import pandas as pd


class PlanejadorMateriais:

    # Materiais que precisam de cálculo de aproveitamento,
    # comprimento, área ou quantidade comercial.
    MATERIAIS_DIMENSIONAIS = [
        "CHAPA",
        "TUBO",
        "BARRA",
        "PERFIL",
    ]

    # Materiais normalmente comprados como item acabado.
    MATERIAIS_PRONTOS = [
        "FIXACAO",
        "CONEXAO",
        "VALVULA",
        "VEDACAO",
        "MANGUEIRA",
        "HIDRAULICO",
        "ELETRICO",
        "FILTRO",
        "FIO",
        "BUCHA",
        "CORREIA",
        "ESTRUTURAL",
        "ACESSORIO",
    ]

    def __init__(self, df):
        self.df = df.copy()

    def classificar_planejamento(self, categoria):

        if pd.isna(categoria):
            return "NAO_CLASSIFICADO"

        categoria = str(categoria).upper().strip()

        if categoria in self.MATERIAIS_DIMENSIONAIS:
            return "DIMENSIONAL"

        if categoria in self.MATERIAIS_PRONTOS:
            return "ITEM_PRONTO"

        return "VERIFICAR"

    def gerar_planejamento(self):

        resultado = self.df.copy()

        resultado["tipo_planejamento"] = (
            resultado["categoria_material"]
            .apply(self.classificar_planejamento)
        )

        return resultado

    def gerar_resumo(self, df):

        resumo = (
            df.groupby(
                [
                    "tipo_planejamento",
                    "categoria_material"
                ]
            )
            .agg(
                quantidade_itens=("componente", "count"),
                quantidade_total=("quantidade_total", "sum")
            )
            .reset_index()
            .sort_values(
                [
                    "tipo_planejamento",
                    "quantidade_itens"
                ],
                ascending=[True, False]
            )
        )

        return resumo

    def gerar_dimensional(self, df):

        return (
            df[
                df["tipo_planejamento"]
                .eq("DIMENSIONAL")
            ]
            .copy()
        )

    def gerar_itens_prontos(self, df):

        return (
            df[
                df["tipo_planejamento"]
                .eq("ITEM_PRONTO")
            ]
            .copy()
        )
