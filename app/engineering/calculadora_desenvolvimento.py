from __future__ import annotations

from math import radians, tan
from typing import Any, Dict, List, Optional


class CalculadoraDesenvolvimento:
    """
    Calculadora de desenvolvimento de peças de chapa dobrada.

    Responsabilidade
    ----------------
    Transformar informações geométricas de uma peça dobrada
    em uma estimativa do desenvolvimento plano (BLANK).

    IMPORTANTE
    ----------
    Este módulo NÃO calcula:

    - estoque;
    - necessidade líquida;
    - compras;
    - aproveitamento da chapa comercial;
    - quantidade de chapas.

    Essas responsabilidades pertencem a outras camadas.

    Fluxo:

        Desenho técnico
              |
              v
        dimensões + dobras
              |
              v
        CalculadoraDesenvolvimento
              |
              v
        BLANK
              |
              v
        CalculadoraCorte

    Método utilizado
    -----------------
    Para cada dobra de 90 graus é calculada a
    Bend Allowance (BA):

        BA = theta_rad * (R + K * T)

    onde:

        theta = ângulo da dobra em radianos
        R     = raio interno
        K     = K-factor
        T     = espessura

    Para uma dobra de 90 graus:

        BA = pi / 2 * (R + K * T)

    O desenvolvimento é calculado a partir das dimensões
    fornecidas e das compensações de dobra.

    ATENÇÃO
    -------
    Esta primeira versão trabalha de forma conservadora
    e NÃO tenta inventar a geometria do blank quando o
    desenho não fornece informações suficientes.

    Quando a geometria não puder ser determinada com
    segurança, o resultado terá status:

        "GEOMETRIA_INSUFICIENTE"
    """

    K_FACTOR_PADRAO = 0.33

    def __init__(
        self,
        espessura_mm: float,
        dobras: Optional[List[Dict[str, Any]]] = None,
        k_factor: float = K_FACTOR_PADRAO,
    ):
        """
        Inicializa a calculadora.

        Parâmetros
        ----------
        espessura_mm:
            Espessura da chapa.

        dobras:
            Lista de dobras extraídas do desenho.

            Exemplo:

            [
                {
                    "angulo_graus": 90,
                    "direcao": "PARA CIMA",
                    "raio_mm": 10,
                },
                ...
            ]

        k_factor:
            Fator K utilizado no cálculo da dobra.
        """

        self.espessura_mm = float(
            espessura_mm
        )

        self.dobras = (
            dobras.copy()
            if dobras
            else []
        )

        self.k_factor = float(
            k_factor
        )

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _numero(
        valor: Any,
    ) -> Optional[float]:
        """
        Converte um valor para float.

        Aceita:

            10
            10.5
            "10,5"
            "10.5"
        """

        if valor is None:
            return None

        try:

            if isinstance(
                valor,
                str,
            ):
                valor = (
                    valor
                    .strip()
                    .replace(",", ".")
                )

            return float(valor)

        except (
            ValueError,
            TypeError,
        ):
            return None

    # ==========================================================
    # VALIDAÇÃO
    # ==========================================================

    def validar(self) -> Dict[str, Any]:
        """
        Valida os dados mínimos necessários para o cálculo.
        """

        erros = []

        if self.espessura_mm <= 0:

            erros.append(
                "Espessura inválida."
            )

        if self.k_factor <= 0:

            erros.append(
                "K-factor inválido."
            )

        if self.k_factor >= 1:

            erros.append(
                "K-factor deve ser menor que 1."
            )

        if not self.dobras:

            erros.append(
                "Nenhuma dobra informada."
            )

        for indice, dobra in enumerate(
            self.dobras,
            start=1,
        ):

            angulo = self._numero(
                dobra.get(
                    "angulo_graus"
                )
            )

            raio = self._numero(
                dobra.get(
                    "raio_mm"
                )
            )

            if angulo is None:

                erros.append(
                    f"Dobra {indice}: "
                    "ângulo não informado."
                )

            elif angulo <= 0:

                erros.append(
                    f"Dobra {indice}: "
                    "ângulo inválido."
                )

            if raio is None:

                erros.append(
                    f"Dobra {indice}: "
                    "raio não informado."
                )

            elif raio < 0:

                erros.append(
                    f"Dobra {indice}: "
                    "raio inválido."
                )

        return {
            "valido": not erros,
            "erros": erros,
        }

    # ==========================================================
    # BEND ALLOWANCE
    # ==========================================================

    def calcular_bend_allowance(
        self,
        angulo_graus: float,
        raio_mm: float,
    ) -> float:
        """
        Calcula a Bend Allowance (BA).

        Fórmula:

            BA = theta * (R + K*T)

        theta em radianos.
        """

        angulo = float(
            angulo_graus
        )

        raio = float(
            raio_mm
        )

        theta_rad = radians(
            angulo
        )

        ba = (
            theta_rad
            * (
                raio
                + (
                    self.k_factor
                    * self.espessura_mm
                )
            )
        )

        return round(
            ba,
            4,
        )

    # ==========================================================
    # BEND DEDUCTION
    # ==========================================================

    def calcular_bend_deduction(
        self,
        angulo_graus: float,
        raio_mm: float,
    ) -> float:
        """
        Calcula a Bend Deduction (BD).

        Para uma dobra:

            BD = 2 * OSSB - BA

        onde:

            OSSB = (R + T) * tan(theta / 2)

        Esta grandeza é útil quando o desenho fornece
        dimensões externas das abas.

        Retorna o valor em milímetros.
        """

        angulo = float(
            angulo_graus
        )

        raio = float(
            raio_mm
        )

        theta_rad = radians(
            angulo
        )

        ossb = (
            raio
            + self.espessura_mm
        ) * tan(
            theta_rad / 2.0
        )

        ba = self.calcular_bend_allowance(
            angulo,
            raio,
        )

        bd = (
            2.0 * ossb
        ) - ba

        return round(
            bd,
            4,
        )

    # ==========================================================
    # ANÁLISE DAS DOBRAS
    # ==========================================================

    def analisar_dobras(self) -> List[Dict[str, Any]]:
        """
        Calcula BA e BD individualmente para cada dobra.
        """

        resultado = []

        for indice, dobra in enumerate(
            self.dobras,
            start=1,
        ):

            angulo = self._numero(
                dobra.get(
                    "angulo_graus"
                )
            )

            raio = self._numero(
                dobra.get(
                    "raio_mm"
                )
            )

            if (
                angulo is None
                or raio is None
            ):
                continue

            bend_allowance = (
                self.calcular_bend_allowance(
                    angulo,
                    raio,
                )
            )

            bend_deduction = (
                self.calcular_bend_deduction(
                    angulo,
                    raio,
                )
            )

            resultado.append(
                {
                    "numero_dobra": indice,
                    "angulo_graus": angulo,
                    "direcao": dobra.get(
                        "direcao"
                    ),
                    "raio_mm": raio,
                    "bend_allowance_mm": (
                        bend_allowance
                    ),
                    "bend_deduction_mm": (
                        bend_deduction
                    ),
                }
            )

        return resultado

    # ==========================================================
    # DESENVOLVIMENTO POR DIMENSÕES
    # ==========================================================

    def calcular_desenvolvimento_linear(
        self,
        dimensoes_segmentos_mm: List[float],
    ) -> Dict[str, Any]:
        """
        Calcula o desenvolvimento a partir dos comprimentos
        dos segmentos da peça.

        Exemplo conceitual:

            aba 1 + aba 2 + BA

        Para múltiplas dobras:

            soma dos segmentos + BA1 + BA2 + ...

        IMPORTANTE:
        -----------
        Os segmentos devem representar comprimentos
        físicos das regiões retas entre as dobras.

        O método NÃO interpreta automaticamente todas
        as dimensões extraídas de um desenho.
        """

        if not dimensoes_segmentos_mm:

            return {
                "status": "GEOMETRIA_INSUFICIENTE",
                "desenvolvimento_mm": None,
                "motivo": (
                    "Nenhum segmento linear informado."
                ),
            }

        segmentos = []

        for valor in dimensoes_segmentos_mm:

            numero = self._numero(
                valor
            )

            if (
                numero is None
                or numero <= 0
            ):
                continue

            segmentos.append(
                numero
            )

        if not segmentos:

            return {
                "status": "GEOMETRIA_INSUFICIENTE",
                "desenvolvimento_mm": None,
                "motivo": (
                    "Nenhuma dimensão linear válida."
                ),
            }

        dados_dobras = (
            self.analisar_dobras()
        )

        if len(dados_dobras) != len(
            self.dobras
        ):

            return {
                "status": "GEOMETRIA_INSUFICIENTE",
                "desenvolvimento_mm": None,
                "motivo": (
                    "Existem dobras sem "
                    "ângulo ou raio válido."
                ),
            }

        comprimento_segmentos = sum(
            segmentos
        )

        soma_ba = sum(
            dobra[
                "bend_allowance_mm"
            ]
            for dobra in dados_dobras
        )

        desenvolvimento = (
            comprimento_segmentos
            + soma_ba
        )

        return {
            "status": "CALCULADO",
            "segmentos_mm": segmentos,
            "comprimento_segmentos_mm": round(
                comprimento_segmentos,
                4,
            ),
            "bend_allowance_total_mm": round(
                soma_ba,
                4,
            ),
            "desenvolvimento_mm": round(
                desenvolvimento,
                4,
            ),
            "dobras": dados_dobras,
        }

    # ==========================================================
    # DESENVOLVIMENTO A PARTIR DE DIMENSÃO TOTAL
    # ==========================================================

    def calcular_a_partir_de_comprimento_total(
        self,
        comprimento_total_mm: float,
    ) -> Dict[str, Any]:
        """
        Calcula uma estimativa quando existe uma dimensão
        total conhecida da peça.

        Esta função NÃO altera a dimensão do desenho.

        Ela apenas calcula as informações de dobra associadas
        ao comprimento informado.

        O objetivo é permitir comparação entre:

            dimensão do desenho
            +
            BA/BD

        antes de determinar definitivamente o blank.
        """

        comprimento = self._numero(
            comprimento_total_mm
        )

        if (
            comprimento is None
            or comprimento <= 0
        ):

            return {
                "status": "GEOMETRIA_INSUFICIENTE",
                "comprimento_total_mm": None,
                "desenvolvimento_mm": None,
                "motivo": (
                    "Comprimento total inválido."
                ),
            }

        dados_dobras = (
            self.analisar_dobras()
        )

        if len(dados_dobras) != len(
            self.dobras
        ):

            return {
                "status": "GEOMETRIA_INSUFICIENTE",
                "comprimento_total_mm": comprimento,
                "desenvolvimento_mm": None,
                "motivo": (
                    "Existem dobras sem "
                    "ângulo ou raio válido."
                ),
            }

        soma_ba = sum(
            dobra[
                "bend_allowance_mm"
            ]
            for dobra in dados_dobras
        )

        soma_bd = sum(
            dobra[
                "bend_deduction_mm"
            ]
            for dobra in dados_dobras
        )

        return {
            "status": "ANALISE",
            "comprimento_total_mm": round(
                comprimento,
                4,
            ),
            "bend_allowance_total_mm": round(
                soma_ba,
                4,
            ),
            "bend_deduction_total_mm": round(
                soma_bd,
                4,
            ),
            "dobras": dados_dobras,
            "observacao": (
                "A dimensão total foi preservada. "
                "O BLANK definitivo depende da "
                "interpretação geométrica das abas "
                "e linhas de dobra."
            ),
        }

    # ==========================================================
    # CÁLCULO COMPLETO
    # ==========================================================

    def calcular(
        self,
        dimensoes_geometricas_mm: Optional[
            List[float]
        ] = None,
        comprimento_principal_mm: Optional[
            float
        ] = None,
        largura_principal_mm: Optional[
            float
        ] = None,
        segmentos_mm: Optional[
            List[float]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Executa a análise completa.

        Regras
        -----

        1. Sem dimensões:
           não calcula blank.

        2. Com segmentos explícitos:
           calcula o desenvolvimento.

        3. Com comprimento principal:
           calcula BA/BD e mantém a dimensão original
           para análise.

        4. Com apenas dimensões geométricas extraídas:
           NÃO assume automaticamente que a maior dimensão
           seja o comprimento do blank.

        Isso evita reproduzir o erro anterior em que uma
        dimensão final do desenho foi transformada
        diretamente em desenvolvimento.
        """

        validacao = self.validar()

        if not validacao["valido"]:

            return {
                "status": "DADOS_INVALIDOS",
                "espessura_mm": self.espessura_mm,
                "k_factor": self.k_factor,
                "dobras": self.dobras,
                "erros": validacao["erros"],
            }

        dados_dobras = (
            self.analisar_dobras()
        )

        resultado = {
            "status": "ANALISE",
            "espessura_mm": self.espessura_mm,
            "k_factor": self.k_factor,
            "dobras": dados_dobras,
            "quantidade_dobras": len(
                dados_dobras
            ),
            "dimensoes_geometricas_mm": (
                dimensoes_geometricas_mm
                if dimensoes_geometricas_mm
                else []
            ),
            "comprimento_principal_mm": (
                comprimento_principal_mm
            ),
            "largura_principal_mm": (
                largura_principal_mm
            ),
            "blank": None,
        }

        # ------------------------------------------------------
        # CASO COM SEGMENTOS EXPLÍCITOS
        # ------------------------------------------------------

        if segmentos_mm:

            desenvolvimento = (
                self.calcular_desenvolvimento_linear(
                    segmentos_mm
                )
            )

            if (
                desenvolvimento.get(
                    "status"
                )
                == "CALCULADO"
            ):

                resultado.update(
                    desenvolvimento
                )

                resultado["blank"] = {
                    "largura_mm": (
                        largura_principal_mm
                    ),
                    "comprimento_mm": (
                        desenvolvimento[
                            "desenvolvimento_mm"
                        ]
                    ),
                }

                resultado["status"] = (
                    "CALCULADO"
                )

            return resultado

        # ------------------------------------------------------
        # CASO COM COMPRIMENTO PRINCIPAL
        # ------------------------------------------------------

        if comprimento_principal_mm:

            analise = (
                self.calcular_a_partir_de_comprimento_total(
                    comprimento_principal_mm
                )
            )

            resultado.update(
                analise
            )

            return resultado

        # ------------------------------------------------------
        # SOMENTE DIMENSÕES EXTRAÍDAS
        # ------------------------------------------------------

        if dimensoes_geometricas_mm:

            resultado["status"] = (
                "GEOMETRIA_INSUFICIENTE"
            )

            resultado["motivo"] = (
                "As dimensões extraídas do desenho "
                "não foram interpretadas automaticamente "
                "como segmentos do desenvolvimento."
            )

            resultado["observacao"] = (
                "É necessário identificar quais dimensões "
                "representam as abas e a direção do "
                "desenvolvimento antes de gerar o BLANK."
            )

            return resultado

        resultado["status"] = (
            "GEOMETRIA_INSUFICIENTE"
        )

        resultado["motivo"] = (
            "Nenhuma dimensão geométrica fornecida."
        )

        return resultado

    # ==========================================================
    # INTEGRAÇÃO COM EXTRATOR
    # ==========================================================

    @classmethod
    def analisar_desenho(
        cls,
        dados_extracao: Dict[str, Any],
        k_factor: float = K_FACTOR_PADRAO,
    ) -> Dict[str, Any]:
        """
        Recebe diretamente o resultado do ExtratorDesenho.

        Exemplo:

            dados = extrator.extrair()

        resultado = (
            CalculadoraDesenvolvimento
            .analisar_desenho(dados)
        )

        IMPORTANTE:
        -----------
        Esta função NÃO inventa o blank.

        Se o desenho possui apenas as dimensões
        extraídas e as dobras, retorna uma análise
        com status GEOMETRIA_INSUFICIENTE.
        """

        if not dados_extracao:

            return {
                "status": "DADOS_INVALIDOS",
                "motivo": (
                    "Dados de extração não informados."
                ),
            }

        espessura = dados_extracao.get(
            "espessura_mm"
        )

        dobras = dados_extracao.get(
            "dobras",
            [],
        )

        dimensoes = dados_extracao.get(
            "dimensoes_geometricas_mm",
            [],
        )

        if espessura is None:

            return {
                "status": "DADOS_INVALIDOS",
                "motivo": (
                    "Espessura não encontrada "
                    "no desenho."
                ),
            }

        calculadora = cls(
            espessura_mm=espessura,
            dobras=dobras,
            k_factor=k_factor,
        )

        resultado = calculadora.calcular(
            dimensoes_geometricas_mm=dimensoes,
        )

        resultado[
            "codigo_peca"
        ] = dados_extracao.get(
            "codigo_peca"
        )

        resultado[
            "materia_prima"
        ] = dados_extracao.get(
            "materia_prima"
        )

        resultado[
            "material"
        ] = dados_extracao.get(
            "material"
        )

        resultado[
            "dados_extracao"
        ] = dados_extracao

        return resultado


if __name__ == "__main__":

    print("=" * 80)
    print(
        "AIZI Engineering AI"
    )
    print(
        "Calculadora de Desenvolvimento"
    )
    print("=" * 80)

    dobras = [
        {
            "angulo_graus": 90,
            "direcao": "PARA CIMA",
            "raio_mm": 10,
        },
        {
            "angulo_graus": 90,
            "direcao": "PARA CIMA",
            "raio_mm": 10,
        },
    ]

    calculadora = CalculadoraDesenvolvimento(
        espessura_mm=6.35,
        dobras=dobras,
        k_factor=0.33,
    )

    resultado = calculadora.calcular(
        dimensoes_geometricas_mm=[
            672.0,
            163.0,
            80.0,
            55.0,
            48.25,
        ]
    )

    print()
    print(
        "ESPESSURA:"
    )
    print(
        resultado.get(
            "espessura_mm"
        )
    )

    print()
    print(
        "K-FACTOR:"
    )
    print(
        resultado.get(
            "k_factor"
        )
    )

    print()
    print(
        "DOBRAS:"
    )

    for dobra in resultado.get(
        "dobras",
        [],
    ):

        print(
            f"Dobra {dobra['numero_dobra']}: "
            f"{dobra['angulo_graus']}° "
            f"R{dobra['raio_mm']} mm | "
            f"BA={dobra['bend_allowance_mm']} mm | "
            f"BD={dobra['bend_deduction_mm']} mm"
        )

    print()
    print(
        "STATUS:"
    )

    print(
        resultado.get(
            "status"
        )
    )

    print()
    print(
        "BLANK:"
    )

    print(
        resultado.get(
            "blank"
        )
    )

    print()
    print(
        "OBSERVAÇÃO:"
    )

    print(
        resultado.get(
            "observacao"
        )
    )

    print("=" * 80)