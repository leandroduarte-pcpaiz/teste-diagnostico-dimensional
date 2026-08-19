import pandas as pd


class CalculadoraMateriaPrima:

    COMPRIMENTO_PADRAO_TUBO_MM = 6000.0
    COMPRIMENTO_PADRAO_BARRA_MM = 6000.0

    # ==========================================================
    # INICIALIZAÇÃO
    # ==========================================================

    def __init__(self, df):
        self.df = df.copy()

    # ==========================================================
    # PADRÃO DE CHAPAS
    # ==========================================================

    @staticmethod
    def definir_padrao_chapa(material, espessura):

        if pd.isna(material):
            return None

        material = str(material).upper().strip()

        if pd.isna(espessura):
            return None

        espessura = float(espessura)

        # ------------------------------------------------------
        # AÇO
        #
        # Até 12,70 mm:
        # 1500 x 6000
        #
        # Acima de 12,70 mm:
        # 2500 x 6000
        # ------------------------------------------------------

        if material == "ACO":

            if espessura <= 12.7:
                return {
                    "largura_mm": 1500.0,
                    "comprimento_mm": 6000.0,
                }

            return {
                "largura_mm": 2500.0,
                "comprimento_mm": 6000.0,
            }

        # ------------------------------------------------------
        # AÇO INOX
        #
        # Por enquanto não assumimos padrão.
        # Será cadastrado posteriormente conforme padrão real.
        # ------------------------------------------------------

        if material == "ACO_INOX":

            return None

        # ------------------------------------------------------
        # AÇO XADREZ
        #
        # 1500 x 6000
        # ------------------------------------------------------

        if material == "ACO_XADREZ":

            return {
                "largura_mm": 1500.0,
                "comprimento_mm": 6000.0,
            }

        # ------------------------------------------------------
        # AÇO EXPANDIDA
        #
        # 1200 x 3000
        # ------------------------------------------------------

        if material == "ACO_EXPANDIDA":

            return {
                "largura_mm": 1200.0,
                "comprimento_mm": 3000.0,
            }

        # ------------------------------------------------------
        # GALVANIZADA
        #
        # 1200 x 3000
        # ------------------------------------------------------

        if material == "GALVANIZADA":

            return {
                "largura_mm": 1200.0,
                "comprimento_mm": 3000.0,
            }

        # ------------------------------------------------------
        # ALUMÍNIO
        #
        # 1250 x 3000
        # ------------------------------------------------------

        if material == "ALUMINIO":

            return {
                "largura_mm": 1250.0,
                "comprimento_mm": 3000.0,
            }

        return None

    # ==========================================================
    # IDENTIFICAR PADRÃO DA MATÉRIA-PRIMA
    # ==========================================================

    def identificar_padrao(self, linha):

        categoria = str(
            linha.get(
                "categoria_material",
                ""
            )
        ).upper().strip()

        # ------------------------------------------------------
        # CHAPA
        # ------------------------------------------------------

        if categoria == "CHAPA":

            material = linha.get(
                "material_chapa"
            )

            espessura = linha.get(
                "espessura_mm"
            )

            padrao = self.definir_padrao_chapa(
                material,
                espessura
            )

            resultado = {
                "tipo_materia_prima": "CHAPA",

                "material_materia_prima": material,

                "espessura_materia_prima_mm": espessura,

                "largura_padrao_mm": None,

                "comprimento_padrao_mm": None,
            }

            if padrao:

                resultado[
                    "largura_padrao_mm"
                ] = padrao["largura_mm"]

                resultado[
                    "comprimento_padrao_mm"
                ] = padrao["comprimento_mm"]

            return resultado

        # ------------------------------------------------------
        # TUBO
        # ------------------------------------------------------

        if categoria == "TUBO":

            return {
                "tipo_materia_prima": "TUBO",

                "material_materia_prima": None,

                "espessura_materia_prima_mm":
                    linha.get(
                        "espessura_mm"
                    ),

                "largura_padrao_mm": None,

                "comprimento_padrao_mm":
                    self.COMPRIMENTO_PADRAO_TUBO_MM,
            }

        # ------------------------------------------------------
        # BARRA
        # ------------------------------------------------------

        if categoria == "BARRA":

            return {
                "tipo_materia_prima": "BARRA",

                "material_materia_prima": None,

                "espessura_materia_prima_mm": None,

                "largura_padrao_mm": None,

                "comprimento_padrao_mm":
                    self.COMPRIMENTO_PADRAO_BARRA_MM,
            }

        # ------------------------------------------------------
        # PERFIL
        # ------------------------------------------------------

        if categoria == "PERFIL":

            return {
                "tipo_materia_prima": "PERFIL",

                "material_materia_prima": None,

                "espessura_materia_prima_mm": None,

                "largura_padrao_mm": None,

                "comprimento_padrao_mm":
                    linha.get(
                        "comprimento_perfil_mm"
                    ),
            }

        # ------------------------------------------------------
        # OUTROS
        # ------------------------------------------------------

        return {
            "tipo_materia_prima": None,

            "material_materia_prima": None,

            "espessura_materia_prima_mm": None,

            "largura_padrao_mm": None,

            "comprimento_padrao_mm": None,
        }

    # ==========================================================
    # PROCESSAR
    # ==========================================================

    def processar(self):

        resultado = self.df.copy()

        dados = resultado.apply(
            self.identificar_padrao,
            axis=1,
            result_type="expand"
        )

        # ------------------------------------------------------
        # Remove as colunas que serão recalculadas aqui.
        #
        # Isso evita duplicação caso o PlanejadorDimensional
        # já tenha criado alguma delas.
        # ------------------------------------------------------

        colunas_recalculadas = [
            "tipo_materia_prima",
            "material_materia_prima",
            "espessura_materia_prima_mm",
            "largura_padrao_mm",
            "comprimento_padrao_mm",
        ]

        resultado = resultado.drop(
            columns=[
                coluna
                for coluna in colunas_recalculadas
                if coluna in resultado.columns
            ],
            errors="ignore"
        )

        resultado = pd.concat(
            [
                resultado.reset_index(drop=True),

                dados.reset_index(drop=True),
            ],
            axis=1
        )

        return resultado

    # ==========================================================
    # RESUMO DE MATÉRIA-PRIMA
    # ==========================================================

    def gerar_resumo(self, df):

        if df.empty:

            return pd.DataFrame(
                columns=[
                    "tipo_materia_prima",
                    "material_materia_prima",
                    "espessura_materia_prima_mm",
                    "largura_padrao_mm",
                    "comprimento_padrao_mm",
                    "quantidade_itens",
                ]
            )

        # ------------------------------------------------------
        # Considera somente chapas
        # ------------------------------------------------------

        chapas = df[
            df["tipo_materia_prima"].eq("CHAPA")
        ].copy()

        if chapas.empty:

            return pd.DataFrame(
                columns=[
                    "tipo_materia_prima",
                    "material_materia_prima",
                    "espessura_materia_prima_mm",
                    "largura_padrao_mm",
                    "comprimento_padrao_mm",
                    "quantidade_itens",
                ]
            )

        # ------------------------------------------------------
        # Agrupamento
        # ------------------------------------------------------

        resumo = (
            chapas
            .groupby(
                [
                    "tipo_materia_prima",
                    "material_materia_prima",
                    "espessura_materia_prima_mm",
                    "largura_padrao_mm",
                    "comprimento_padrao_mm",
                ],
                dropna=False
            )
            .agg(
                quantidade_itens=(
                    "componente",
                    "count"
                )
            )
            .reset_index()
        )

        return resumo