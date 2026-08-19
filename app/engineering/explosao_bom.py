import pandas as pd

from app.engineering.arvore_produto import ArvoreProduto


class ExplosaoBOM:

    def __init__(self, df):
        self.arvore = ArvoreProduto(df)

    # ==========================================================
    # EXPLOSÃO CONSOLIDADA
    # ==========================================================

    def explodir(self, produto, quantidade=1):

        produto = produto.upper().strip()

        resultado = {}

        self._explodir_recursivo(
            produto,
            quantidade,
            resultado,
            caminho=set()
        )

        return pd.DataFrame(
            [
                {
                    "componente": componente,
                    "quantidade_total": quantidade_total
                }
                for componente, quantidade_total in resultado.items()
            ]
        )

    # ==========================================================
    # EXPLOSÃO RECURSIVA
    # ==========================================================

    def _explodir_recursivo(
        self,
        produto,
        quantidade_pai,
        resultado,
        caminho
    ):

        if produto in caminho:
            return

        novo_caminho = caminho.copy()
        novo_caminho.add(produto)

        filhos = self.arvore.buscar_filhos(produto)

        for componente, quantidade in filhos:

            componente = str(componente).upper().strip()

            qtd = float(quantidade) * quantidade_pai

            possui_estrutura = (
                componente in self.arvore.df["produto"].values
            )

            if possui_estrutura:

                self._explodir_recursivo(
                    componente,
                    qtd,
                    resultado,
                    novo_caminho
                )

            else:

                if componente in resultado:
                    resultado[componente] += qtd
                else:
                    resultado[componente] = qtd

    # ==========================================================
    # ÁRVORE HIERÁRQUICA DA BOM
    # ==========================================================

    def montar_arvore(
        self,
        produto,
        quantidade=1
    ):

        produto = (
            str(produto)
            .upper()
            .strip()
        )

        if not produto:

            raise ValueError(
                "O produto informado para montar a árvore está vazio."
            )

        try:

            quantidade = float(
                quantidade
            )

        except (TypeError, ValueError):

            raise ValueError(
                "A quantidade informada para montar a árvore "
                "precisa ser numérica."
            )

        if quantidade <= 0:

            raise ValueError(
                "A quantidade informada para montar a árvore "
                "precisa ser maior que zero."
            )

        arvore = self.arvore.montar_arvore(
            produto=produto,
            quantidade_acumulada=quantidade
        )

        return pd.DataFrame(
            arvore,
            columns=[
                "nivel",
                "pai",
                "filho",
                "quantidade",
                "quantidade_acumulada"
            ]
        )