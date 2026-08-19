class ArvoreProduto:

    def __init__(self, df):
        self.df = df.copy()

        self.df["produto"] = (
            self.df["produto"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip()
        )

        self.df["componente"] = (
            self.df["componente"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip()
        )

    def buscar_filhos(self, produto):

        produto = produto.upper().strip()

        filhos = self.df[
            self.df["produto"] == produto
        ]

        return filhos[
            [
                "componente",
                "quantidade"
            ]
        ].values.tolist()

    def montar_arvore(
        self,
        produto,
        nivel=0,
        caminho=None,
        quantidade_acumulada=1
    ):

        produto = produto.upper().strip()

        if caminho is None:
            caminho = set()

        if produto in caminho:
            return []

        novo_caminho = caminho.copy()
        novo_caminho.add(produto)

        arvore = []

        filhos = self.buscar_filhos(produto)

        for filho, quantidade in filhos:

            filho = str(filho).upper().strip()
            quantidade = float(quantidade)

            quantidade_total = (
                quantidade_acumulada * quantidade
            )

            arvore.append(
                {
                    "nivel": nivel + 1,
                    "pai": produto,
                    "filho": filho,
                    "quantidade": quantidade,
                    "quantidade_acumulada": quantidade_total
                }
            )

            if filho in self.df["produto"].values:

                arvore.extend(
                    self.montar_arvore(
                        filho,
                        nivel + 1,
                        novo_caminho,
                        quantidade_total
                    )
                )

        return arvore
