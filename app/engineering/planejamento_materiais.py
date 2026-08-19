import pandas as pd
from pathlib import Path


class PlanejamentoMateriais:

    def __init__(self, resultado_final):
        self.df = resultado_final.copy()

    def gerar(self, produto):

        produto = produto.upper().strip()

        colunas = [
            "componente",
            "DESCRICAO_PRODUTO",
            "UNIDADE_MEDIDA",
            "TIPO",
            "DESCRICAO_TIPO",
            "ITEM_FANTASMA",
            "quantidade_total",
            "cadastro_encontrado"
        ]

        colunas_existentes = [
            coluna
            for coluna in colunas
            if coluna in self.df.columns
        ]

        resultado = self.df[colunas_existentes].copy()

        # --------------------------------------------------
        # CLASSIFICAÇÃO INICIAL
        # --------------------------------------------------

        if "TIPO" in resultado.columns:

            resultado["categoria_planejamento"] = (
                resultado["TIPO"]
                .fillna("")
                .astype(str)
                .str.upper()
                .str.strip()
            )

        else:

            resultado["categoria_planejamento"] = "NAO_CLASSIFICADO"

        # --------------------------------------------------
        # QUANTIDADE
        # --------------------------------------------------

        if "quantidade_total" in resultado.columns:

            resultado["quantidade_total"] = pd.to_numeric(
                resultado["quantidade_total"],
                errors="coerce"
            ).fillna(0)

        # --------------------------------------------------
        # ORDENAÇÃO
        # --------------------------------------------------

        resultado = resultado.sort_values(
            by=["categoria_planejamento", "componente"]
        ).reset_index(drop=True)

        # --------------------------------------------------
        # RESUMO
        # --------------------------------------------------

        resumo = (
            resultado
            .groupby("categoria_planejamento", dropna=False)
            .agg(
                quantidade_itens=("componente", "count")
            )
            .reset_index()
        )

        # --------------------------------------------------
        # SALVA RESULTADOS
        # --------------------------------------------------

        pasta = Path("resultado_final")
        pasta.mkdir(exist_ok=True)

        caminho_detalhado = (
            pasta /
            f"planejamento_materiais_{produto}.csv"
        )

        caminho_resumo = (
            pasta /
            f"resumo_planejamento_{produto}.csv"
        )

        resultado.to_csv(
            caminho_detalhado,
            index=False,
            encoding="utf-8-sig"
        )

        resumo.to_csv(
            caminho_resumo,
            index=False,
            encoding="utf-8-sig"
        )

        return resultado, resumo