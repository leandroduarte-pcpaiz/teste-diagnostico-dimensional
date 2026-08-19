from math import ceil


class CalculadoraCorte:
    """
    Calcula o aproveitamento de peças retangulares
    em uma chapa de matéria-prima.

    Todas as dimensões são informadas em milímetros.
    """

    def __init__(
        self,
        codigo_peca,
        material,
        espessura_mm,
        largura_peca_mm,
        comprimento_peca_mm,
        quantidade,
        largura_chapa_mm,
        comprimento_chapa_mm,
    ):
        self.codigo_peca = codigo_peca
        self.material = material
        self.espessura_mm = float(espessura_mm)

        self.largura_peca_mm = float(largura_peca_mm)
        self.comprimento_peca_mm = float(comprimento_peca_mm)

        self.quantidade = int(quantidade)

        self.largura_chapa_mm = float(largura_chapa_mm)
        self.comprimento_chapa_mm = float(comprimento_chapa_mm)

    def calcular_por_orientacao(
        self,
        largura_peca_mm,
        comprimento_peca_mm,
    ):
        """
        Calcula quantas peças cabem na chapa
        considerando uma determinada orientação.
        """

        pecas_largura = int(
            self.largura_chapa_mm // largura_peca_mm
        )

        pecas_comprimento = int(
            self.comprimento_chapa_mm // comprimento_peca_mm
        )

        quantidade_por_chapa = (
            pecas_largura * pecas_comprimento
        )

        return {
            "pecas_largura": pecas_largura,
            "pecas_comprimento": pecas_comprimento,
            "quantidade_por_chapa": quantidade_por_chapa,
        }

    def calcular(self):
        """
        Testa as duas orientações possíveis da peça
        e escolhe aquela que permite maior quantidade
        de peças por chapa.
        """

        orientacao_1 = self.calcular_por_orientacao(
            self.largura_peca_mm,
            self.comprimento_peca_mm,
        )

        orientacao_2 = self.calcular_por_orientacao(
            self.comprimento_peca_mm,
            self.largura_peca_mm,
        )

        if (
            orientacao_2["quantidade_por_chapa"]
            > orientacao_1["quantidade_por_chapa"]
        ):
            melhor_orientacao = orientacao_2
            orientacao = "90 graus"

        else:
            melhor_orientacao = orientacao_1
            orientacao = "0 graus"

        pecas_por_chapa = melhor_orientacao[
            "quantidade_por_chapa"
        ]

        # A peça não cabe na chapa
        if pecas_por_chapa <= 0:
            return {
                "codigo_peca": self.codigo_peca,
                "material": self.material,
                "espessura_mm": self.espessura_mm,
                "largura_peca_mm": self.largura_peca_mm,
                "comprimento_peca_mm": self.comprimento_peca_mm,
                "quantidade_necessaria": self.quantidade,
                "pecas_por_chapa": 0,
                "chapas_necessarias": None,
                "pecas_produzidas": 0,
                "pecas_sobrando": None,
                "orientacao": None,
                "aproveitamento_necessidade_percentual": 0,
                "aproveitamento_chapa_percentual": 0,
                "erro": "A peça não cabe na chapa.",
            }

        # Quantidade de chapas necessárias
        chapas_necessarias = ceil(
            self.quantidade / pecas_por_chapa
        )

        # Quantidade total de peças que serão produzidas
        pecas_produzidas = (
            chapas_necessarias * pecas_por_chapa
        )

        # Quantidade de posições que ficarão sem peça
        pecas_sobrando = (
            pecas_produzidas - self.quantidade
        )

        # Áreas
        area_chapa = (
            self.largura_chapa_mm
            * self.comprimento_chapa_mm
        )

        area_peca = (
            self.largura_peca_mm
            * self.comprimento_peca_mm
        )

        # Aproveitamento considerando TODAS as posições
        # ocupadas na chapa pelo padrão de corte
        area_ocupada_corte = (
            area_peca * pecas_por_chapa
        )

        aproveitamento_chapa = (
            area_ocupada_corte / area_chapa
        ) * 100

        # Aproveitamento considerando somente
        # a quantidade realmente necessária
        area_necessaria = (
            area_peca * self.quantidade
        )

        area_total_chapas = (
            area_chapa * chapas_necessarias
        )

        aproveitamento_necessidade = (
            area_necessaria / area_total_chapas
        ) * 100

        return {
            "codigo_peca": self.codigo_peca,
            "material": self.material,
            "espessura_mm": self.espessura_mm,
            "largura_peca_mm": self.largura_peca_mm,
            "comprimento_peca_mm": self.comprimento_peca_mm,
            "quantidade_necessaria": self.quantidade,
            "largura_chapa_mm": self.largura_chapa_mm,
            "comprimento_chapa_mm": self.comprimento_chapa_mm,
            "pecas_por_chapa": pecas_por_chapa,
            "chapas_necessarias": chapas_necessarias,
            "pecas_produzidas": pecas_produzidas,
            "pecas_sobrando": pecas_sobrando,
            "orientacao": orientacao,
            "pecas_largura": melhor_orientacao[
                "pecas_largura"
            ],
            "pecas_comprimento": melhor_orientacao[
                "pecas_comprimento"
            ],
            "aproveitamento_necessidade_percentual": round(
                aproveitamento_necessidade,
                2,
            ),
            "aproveitamento_chapa_percentual": round(
                aproveitamento_chapa,
                2,
            ),
            "erro": None,
        }


if __name__ == "__main__":

    calculadora = CalculadoraCorte(
        codigo_peca="G2005887",
        material="ACO_A36",
        espessura_mm=6.35,
        largura_peca_mm=500,
        comprimento_peca_mm=1000,
        quantidade=20,
        largura_chapa_mm=2000,
        comprimento_chapa_mm=6000,
    )

    resultado = calculadora.calcular()

    print("=" * 60)
    print("AIZI Engineering AI")
    print("Calculadora de Corte")
    print("=" * 60)

    for chave, valor in resultado.items():
        print(f"{chave}: {valor}")

    print("=" * 60)