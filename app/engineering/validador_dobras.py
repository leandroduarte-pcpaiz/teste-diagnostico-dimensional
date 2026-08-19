from __future__ import annotations

from typing import Any, Dict, List, Optional
import math


# =============================================================================
# AIZI ENGINEERING AI
# VALIDADOR DE DOBRAS
# =============================================================================
#
# Responsabilidade:
#
# Receber:
#   - geometria interpretada;
#   - resultado produzido pelo AnalisadorDobras;
#   - opcionalmente, resultado do ConsolidadorDobras.
#
# Avaliar a força geométrica das candidatas a dobra.
#
# IMPORTANTE:
# - NÃO altera a geometria original.
# - NÃO calcula BLANK.
# - NÃO calcula desenvolvimento.
# - NÃO calcula K-factor.
# - NÃO inventa raio.
# - NÃO confirma automaticamente uma dobra física.
# - NÃO chama CalculadoraCorte.
#
# O módulo apenas classifica a EVIDÊNCIA geométrica.
#
# Resultado possível:
#
#   EVIDENCIA_FORTE
#   EVIDENCIA_MODERADA
#   EVIDENCIA_FRACA
#   SEM_EVIDENCIA_SUFICIENTE
#
# =============================================================================


class ValidadorDobras:
    """
    Valida geometricamente candidatas a dobra.

    O objetivo é separar:
        - transições geométricas relevantes;
        - candidatas aproximadamente 90°;
        - transições angulares;
        - situações que não possuem evidência suficiente.

    Este módulo NÃO transforma uma candidata em dobra confirmada.
    """

    # -------------------------------------------------------------------------
    # Tolerâncias
    # -------------------------------------------------------------------------

    TOLERANCIA_90_GRAUS = 5.0

    ANGULO_MIN_RELEVANTE = 15.0

    ANGULO_MAX_RELEVANTE = 165.0

    LIMITE_SEGMENTO_CURTO_MM = 10.0

    TOLERANCIA_DIRECAO_GRAUS = 8.0

    # Diferença máxima entre segmentos consecutivos para considerar
    # que a geometria possui mudança direcional relevante.
    TOLERANCIA_COLINEAR_GRAUS = 5.0

    # -------------------------------------------------------------------------
    # Pesos de evidência
    # -------------------------------------------------------------------------

    PONTOS_90_GRAUS = 3

    PONTOS_ARCO = 3

    PONTOS_SEGMENTO_CURTO = 1

    PONTOS_TRANSICAO_GEOMETRICA = 2

    PONTOS_REPETICAO = 1

    PONTOS_RAIO_EXPLICITO = 1

    # -------------------------------------------------------------------------
    # Limiares
    # -------------------------------------------------------------------------

    LIMITE_EVIDENCIA_FORTE = 6

    LIMITE_EVIDENCIA_MODERADA = 4

    LIMITE_EVIDENCIA_FRACA = 2

    def __init__(
        self,
        geometria: Optional[Dict[str, Any]] = None,
        analise_dobras: Optional[Dict[str, Any]] = None,
        consolidacao: Optional[Dict[str, Any]] = None,
    ):
        self.geometria = geometria or {}
        self.analise_dobras = analise_dobras or {}
        self.consolidacao = consolidacao or {}

    # =========================================================================
    # UTILITÁRIOS
    # =========================================================================

    @staticmethod
    def _numero(
        valor: Any,
        padrao: Optional[float] = None,
    ) -> Optional[float]:

        if valor is None:
            return padrao

        try:
            return float(valor)

        except (TypeError, ValueError):
            return padrao

    @staticmethod
    def _normalizar_angulo(
        angulo: Any,
    ) -> Optional[float]:

        valor = ValidadorDobras._numero(angulo)

        if valor is None:
            return None

        valor %= 360.0

        if valor > 180.0:
            valor = 360.0 - valor

        return abs(valor)

    @staticmethod
    def _distancia(
        ponto_a: Dict[str, Any],
        ponto_b: Dict[str, Any],
    ) -> Optional[float]:

        xa = ValidadorDobras._numero(
            ponto_a.get("x")
        )

        ya = ValidadorDobras._numero(
            ponto_a.get("y")
        )

        xb = ValidadorDobras._numero(
            ponto_b.get("x")
        )

        yb = ValidadorDobras._numero(
            ponto_b.get("y")
        )

        if (
            xa is None
            or ya is None
            or xb is None
            or yb is None
        ):
            return None

        return math.hypot(
            xb - xa,
            yb - ya,
        )

    # =========================================================================
    # ACESSO À GEOMETRIA
    # =========================================================================

    def _dados_geometria(
        self,
    ) -> Dict[str, Any]:

        if "geometria" in self.geometria:

            geometria = self.geometria.get(
                "geometria",
                {},
            )

            if isinstance(geometria, dict):
                return geometria

        return self.geometria

    def _segmentos(
        self,
    ) -> List[Dict[str, Any]]:

        geometria = self._dados_geometria()

        segmentos = geometria.get(
            "segmentos",
            [],
        )

        if not isinstance(
            segmentos,
            list,
        ):
            return []

        return segmentos

    def _arcos(
        self,
    ) -> List[Dict[str, Any]]:

        geometria = self._dados_geometria()

        arcos = geometria.get(
            "arcos",
            [],
        )

        if not isinstance(
            arcos,
            list,
        ):
            return []

        return arcos

    # =========================================================================
    # MAPA DE SEGMENTOS
    # =========================================================================

    def _mapa_segmentos(
        self,
    ) -> Dict[int, Dict[str, Any]]:

        resultado: Dict[int, Dict[str, Any]] = {}

        for segmento in self._segmentos():

            try:

                identificador = int(
                    segmento.get("id")
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            resultado[identificador] = segmento

        return resultado

    # =========================================================================
    # TAMANHO DE SEGMENTO
    # =========================================================================

    def _tamanho_segmento(
        self,
        segmento: Optional[Dict[str, Any]],
    ) -> Optional[float]:

        if not segmento:
            return None

        comprimento = self._numero(
            segmento.get(
                "comprimento_mm"
            )
        )

        if comprimento is not None:
            return abs(comprimento)

        x1 = self._numero(
            segmento.get("x1")
        )

        y1 = self._numero(
            segmento.get("y1")
        )

        x2 = self._numero(
            segmento.get("x2")
        )

        y2 = self._numero(
            segmento.get("y2")
        )

        if (
            x1 is None
            or y1 is None
            or x2 is None
            or y2 is None
        ):
            return None

        return math.hypot(
            x2 - x1,
            y2 - y1,
        )

    def _segmento_curto(
        self,
        segmento: Optional[Dict[str, Any]],
    ) -> bool:

        comprimento = self._tamanho_segmento(
            segmento
        )

        if comprimento is None:
            return False

        return (
            comprimento
            <= self.LIMITE_SEGMENTO_CURTO_MM
        )

    # =========================================================================
    # IDS DA CANDIDATA
    # =========================================================================

    @staticmethod
    def _ids_candidata(
        candidata: Dict[str, Any],
    ) -> List[int]:

        resultado: List[int] = []

        # Formato atual
        for chave in (
            "segmento_anterior",
            "segmento_atual",
        ):

            valor = candidata.get(
                chave
            )

            if valor is None:
                continue

            try:

                identificador = int(
                    valor
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if identificador not in resultado:
                resultado.append(
                    identificador
                )

        if resultado:
            return resultado

        # Formatos anteriores
        for chave in (
            "segmento_1",
            "segmento_2",
            "segmento1",
            "segmento2",
        ):

            valor = candidata.get(
                chave
            )

            if valor is None:
                continue

            try:

                identificador = int(
                    valor
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if identificador not in resultado:
                resultado.append(
                    identificador
                )

        if resultado:
            return resultado

        segmentos = candidata.get(
            "segmentos"
        )

        if isinstance(
            segmentos,
            (list, tuple),
        ):

            for valor in segmentos:

                try:

                    identificador = int(
                        valor
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    continue

                if identificador not in resultado:

                    resultado.append(
                        identificador
                    )

        return resultado

    # =========================================================================
    # PONTO DA CANDIDATA
    # =========================================================================

    @staticmethod
    def _ponto_candidata(
        candidata: Dict[str, Any],
    ) -> Dict[str, Optional[float]]:

        ponto = candidata.get(
            "ponto_dobra"
        )

        if isinstance(
            ponto,
            dict,
        ):

            return {
                "x": ValidadorDobras._numero(
                    ponto.get("x_mm")
                ),
                "y": ValidadorDobras._numero(
                    ponto.get("y_mm")
                ),
            }

        ponto = candidata.get(
            "ponto"
        )

        if isinstance(
            ponto,
            dict,
        ):

            return {
                "x": ValidadorDobras._numero(
                    ponto.get("x")
                ),
                "y": ValidadorDobras._numero(
                    ponto.get("y")
                ),
            }

        return {
            "x": ValidadorDobras._numero(
                candidata.get("x")
            ),
            "y": ValidadorDobras._numero(
                candidata.get("y")
            ),
        }

    # =========================================================================
    # ÂNGULO
    # =========================================================================

    @classmethod
    def _angulo_candidata(
        cls,
        candidata: Dict[str, Any],
    ) -> Optional[float]:

        for chave in (
            "angulo_graus",
            "angulo",
            "angulo_deg",
        ):

            if chave in candidata:

                return cls._normalizar_angulo(
                    candidata.get(chave)
                )

        return None

    # =========================================================================
    # RAIO EXPLÍCITO
    # =========================================================================

    @classmethod
    def _raio_candidata(
        cls,
        candidata: Dict[str, Any],
    ) -> Optional[float]:

        for chave in (
            "raio_mm",
            "raio",
            "raio_nominal_mm",
        ):

            if chave not in candidata:
                continue

            raio = cls._numero(
                candidata.get(chave)
            )

            if (
                raio is not None
                and raio > 0
            ):
                return raio

        return None

    # =========================================================================
    # ARCO EXPLÍCITO
    # =========================================================================

    def _arco_proximo(
        self,
        ponto: Dict[str, Optional[float]],
    ) -> Optional[Dict[str, Any]]:

        x = ponto.get("x")
        y = ponto.get("y")

        if x is None or y is None:
            return None

        melhor = None
        menor_distancia = None

        for arco in self._arcos():

            centro_x = self._numero(
                arco.get("centro_x")
            )

            centro_y = self._numero(
                arco.get("centro_y")
            )

            if (
                centro_x is None
                or centro_y is None
            ):
                continue

            distancia = math.hypot(
                x - centro_x,
                y - centro_y,
            )

            if (
                menor_distancia is None
                or distancia < menor_distancia
            ):

                menor_distancia = distancia
                melhor = arco

        return melhor

    # =========================================================================
    # DIREÇÃO DO SEGMENTO
    # =========================================================================

    def _direcao_segmento(
        self,
        segmento: Optional[Dict[str, Any]],
    ) -> Optional[float]:

        if not segmento:
            return None

        x1 = self._numero(
            segmento.get("x1")
        )

        y1 = self._numero(
            segmento.get("y1")
        )

        x2 = self._numero(
            segmento.get("x2")
        )

        y2 = self._numero(
            segmento.get("y2")
        )

        if (
            x1 is None
            or y1 is None
            or x2 is None
            or y2 is None
        ):
            return None

        dx = x2 - x1
        dy = y2 - y1

        if (
            abs(dx) < 1e-12
            and abs(dy) < 1e-12
        ):
            return None

        return math.degrees(
            math.atan2(
                dy,
                dx,
            )
        )

    # =========================================================================
    # DIFERENÇA ENTRE DIREÇÕES
    # =========================================================================

    @staticmethod
    def _diferenca_direcao(
        direcao_a: Optional[float],
        direcao_b: Optional[float],
    ) -> Optional[float]:

        if (
            direcao_a is None
            or direcao_b is None
        ):
            return None

        diferenca = abs(
            direcao_a - direcao_b
        )

        diferenca %= 180.0

        if diferenca > 90.0:
            diferenca = 180.0 - diferenca

        return abs(diferenca)

    # =========================================================================
    # EVIDÊNCIA DE TRANSIÇÃO GEOMÉTRICA
    # =========================================================================

    def _avaliar_transicao(
        self,
        ids: List[int],
        mapa_segmentos: Dict[int, Dict[str, Any]],
    ) -> Dict[str, Any]:

        segmentos = [
            mapa_segmentos[identificador]
            for identificador in ids
            if identificador in mapa_segmentos
        ]

        direcoes = [
            self._direcao_segmento(
                segmento
            )
            for segmento in segmentos
        ]

        direcoes = [
            direcao
            for direcao in direcoes
            if direcao is not None
        ]

        diferencas = []

        for i in range(
            len(direcoes) - 1
        ):

            diferenca = (
                self._diferenca_direcao(
                    direcoes[i],
                    direcoes[i + 1],
                )
            )

            if diferenca is not None:

                diferencas.append(
                    diferenca
                )

        if not diferencas:

            return {
                "transicao_detectada": False,
                "angulo_direcional_graus": None,
            }

        maior = max(
            diferencas
        )

        transicao = (
            maior
            > self.TOLERANCIA_COLINEAR_GRAUS
        )

        return {
            "transicao_detectada":
                transicao,

            "angulo_direcional_graus":
                maior,
        }

    # =========================================================================
    # REPETIÇÃO DE PADRÃO
    # =========================================================================

    def _avaliar_repeticao(
        self,
        candidata: Dict[str, Any],
        candidatas: List[Dict[str, Any]],
    ) -> bool:

        angulo = self._angulo_candidata(
            candidata
        )

        if angulo is None:
            return False

        ids = set(
            self._ids_candidata(
                candidata
            )
        )

        if not ids:
            return False

        for outra in candidatas:

            if outra is candidata:
                continue

            outro_angulo = (
                self._angulo_candidata(
                    outra
                )
            )

            if outro_angulo is None:
                continue

            if abs(
                outro_angulo - angulo
            ) > self.TOLERANCIA_90_GRAUS:

                continue

            outros_ids = set(
                self._ids_candidata(
                    outra
                )
            )

            if ids.intersection(
                outros_ids
            ):

                return True

        return False

    # =========================================================================
    # AVALIAÇÃO INDIVIDUAL
    # =========================================================================

    def _validar_candidata(
        self,
        candidata: Dict[str, Any],
        candidatas: List[Dict[str, Any]],
        mapa_segmentos: Dict[int, Dict[str, Any]],
    ) -> Dict[str, Any]:

        ids = self._ids_candidata(
            candidata
        )

        angulo = self._angulo_candidata(
            candidata
        )

        ponto = self._ponto_candidata(
            candidata
        )

        raio = self._raio_candidata(
            candidata
        )

        segmentos = [
            mapa_segmentos[identificador]
            for identificador in ids
            if identificador in mapa_segmentos
        ]

        segmento_curto = any(
            self._segmento_curto(
                segmento
            )
            for segmento in segmentos
        )

        arco = self._arco_proximo(
            ponto
        )

        possui_arco = arco is not None

        transicao = self._avaliar_transicao(
            ids,
            mapa_segmentos,
        )

        repeticao = self._avaliar_repeticao(
            candidata,
            candidatas,
        )

        eh_90 = (
            angulo is not None
            and abs(
                angulo - 90.0
            )
            <= self.TOLERANCIA_90_GRAUS
        )

        angular_relevante = (
            angulo is not None
            and
            self.ANGULO_MIN_RELEVANTE
            <= angulo
            <= self.ANGULO_MAX_RELEVANTE
        )

        # ---------------------------------------------------------------------
        # PONTUAÇÃO
        # ---------------------------------------------------------------------

        pontos = 0
        evidencias: List[str] = []

        if eh_90:

            pontos += self.PONTOS_90_GRAUS

            evidencias.append(
                "ANGULO_APROXIMADAMENTE_90_GRAUS"
            )

        elif angular_relevante:

            evidencias.append(
                "TRANSICAO_ANGULAR_RELEVANTE"
            )

        if possui_arco:

            pontos += self.PONTOS_ARCO

            evidencias.append(
                "ARCO_EXPLICITO_PROXIMO"
            )

        if segmento_curto:

            pontos += self.PONTOS_SEGMENTO_CURTO

            evidencias.append(
                "SEGMENTO_CURTO_ASSOCIADO"
            )

        if transicao.get(
            "transicao_detectada"
        ):

            pontos += (
                self.PONTOS_TRANSICAO_GEOMETRICA
            )

            evidencias.append(
                "MUDANCA_DIRECIONAL_DETECTADA"
            )

        if repeticao:

            pontos += self.PONTOS_REPETICAO

            evidencias.append(
                "PADRAO_REPETIDO"
            )

        if raio is not None:

            pontos += self.PONTOS_RAIO_EXPLICITO

            evidencias.append(
                "RAIO_EXPLICITO_FORNECIDO"
            )

        # ---------------------------------------------------------------------
        # CLASSIFICAÇÃO DA EVIDÊNCIA
        # ---------------------------------------------------------------------

        if pontos >= self.LIMITE_EVIDENCIA_FORTE:

            nivel = "EVIDENCIA_FORTE"

        elif pontos >= self.LIMITE_EVIDENCIA_MODERADA:

            nivel = "EVIDENCIA_MODERADA"

        elif pontos >= self.LIMITE_EVIDENCIA_FRACA:

            nivel = "EVIDENCIA_FRACA"

        else:

            nivel = "SEM_EVIDENCIA_SUFICIENTE"

        # ---------------------------------------------------------------------
        # DECISÃO CONSERVADORA
        # ---------------------------------------------------------------------

        if eh_90 and possui_arco:

            natureza = (
                "REGIAO_COM_EVIDENCIA_GEOMETRICA_FORTE"
            )

        elif eh_90 and transicao.get(
            "transicao_detectada"
        ):

            natureza = (
                "CANDIDATA_90_COM_TRANSICAO_GEOMETRICA"
            )

        elif eh_90:

            natureza = (
                "CANDIDATA_90_SEM_ARCO"
            )

        elif angular_relevante:

            natureza = (
                "CANDIDATA_ANGULAR"
            )

        else:

            natureza = (
                "TRANSICAO_NAO_CONFIRMADA"
            )

        return {
            "segmentos":
                ids,

            "angulo_graus":
                angulo,

            "ponto":
                ponto,

            "raio_mm":
                raio,

            "possui_arco":
                possui_arco,

            "segmento_curto":
                segmento_curto,

            "transicao_geometrica":
                transicao.get(
                    "transicao_detectada",
                    False,
                ),

            "angulo_direcional_graus":
                transicao.get(
                    "angulo_direcional_graus"
                ),

            "padrao_repetido":
                repeticao,

            "pontos_evidencia":
                pontos,

            "nivel_evidencia":
                nivel,

            "natureza":
                natureza,

            "evidencias":
                evidencias,

            # Segurança:
            # isto NÃO significa que a dobra foi confirmada.
            "dobra_confirmada":
                False,

            "origem":
                candidata,
        }

    # =========================================================================
    # CANDIDATAS OFICIAIS
    # =========================================================================

    def _candidatas(
        self,
    ) -> List[Dict[str, Any]]:

        candidatas = self.analise_dobras.get(
            "dobras"
        )

        if isinstance(
            candidatas,
            list,
        ):
            return candidatas

        # Compatibilidade com versões anteriores
        candidatas = self.analise_dobras.get(
            "candidatas",
            [],
        )

        if isinstance(
            candidatas,
            list,
        ):
            return candidatas

        return []

    # =========================================================================
    # VALIDAÇÃO COMPLETA
    # =========================================================================

    def validar_candidatas(
        self,
    ) -> Dict[str, Any]:

        segmentos = self._segmentos()
        arcos = self._arcos()

        mapa_segmentos = (
            self._mapa_segmentos()
        )

        candidatas = self._candidatas()

        resultados = []

        for candidata in candidatas:

            resultados.append(
                self._validar_candidata(
                    candidata,
                    candidatas,
                    mapa_segmentos,
                )
            )

        fortes = [
            resultado
            for resultado in resultados
            if resultado.get(
                "nivel_evidencia"
            ) == "EVIDENCIA_FORTE"
        ]

        moderadas = [
            resultado
            for resultado in resultados
            if resultado.get(
                "nivel_evidencia"
            ) == "EVIDENCIA_MODERADA"
        ]

        fracas = [
            resultado
            for resultado in resultados
            if resultado.get(
                "nivel_evidencia"
            ) == "EVIDENCIA_FRACA"
        ]

        insuficientes = [
            resultado
            for resultado in resultados
            if resultado.get(
                "nivel_evidencia"
            ) == "SEM_EVIDENCIA_SUFICIENTE"
        ]

        aproximadamente_90 = [
            resultado
            for resultado in resultados
            if (
                resultado.get(
                    "angulo_graus"
                ) is not None
                and
                abs(
                    resultado.get(
                        "angulo_graus"
                    )
                    - 90.0
                )
                <= self.TOLERANCIA_90_GRAUS
            )
        ]

        angulares = [
            resultado
            for resultado in resultados
            if (
                resultado.get(
                    "angulo_graus"
                ) is not None
                and
                self.ANGULO_MIN_RELEVANTE
                <= resultado.get(
                    "angulo_graus"
                )
                <= self.ANGULO_MAX_RELEVANTE
                and
                abs(
                    resultado.get(
                        "angulo_graus"
                    )
                    - 90.0
                )
                > self.TOLERANCIA_90_GRAUS
            )
        ]

        com_arco = [
            resultado
            for resultado in resultados
            if resultado.get(
                "possui_arco"
            )
        ]

        com_transicao = [
            resultado
            for resultado in resultados
            if resultado.get(
                "transicao_geometrica"
            )
        ]

        # ---------------------------------------------------------------------
        # STATUS GERAL
        # ---------------------------------------------------------------------

        if not resultados:

            status = (
                "NENHUMA_CANDIDATA_PARA_VALIDAR"
            )

        elif fortes:

            status = (
                "EVIDENCIA_FORTE_ENCONTRADA"
            )

        elif moderadas:

            status = (
                "EVIDENCIA_MODERADA_ENCONTRADA"
            )

        elif fracas:

            status = (
                "APENAS_EVIDENCIAS_FRACAS"
            )

        else:

            status = (
                "SEM_EVIDENCIA_SUFICIENTE"
            )

        return {
            "tipo":
                "VALIDACAO_DOBRAS",

            "status":
                status,

            "quantidade_segmentos":
                len(segmentos),

            "quantidade_arcos":
                len(arcos),

            "quantidade_candidatas":
                len(candidatas),

            "quantidade_evidencia_forte":
                len(fortes),

            "quantidade_evidencia_moderada":
                len(moderadas),

            "quantidade_evidencia_fraca":
                len(fracas),

            "quantidade_sem_evidencia":
                len(insuficientes),

            "quantidade_aproximadamente_90":
                len(aproximadamente_90),

            "quantidade_angulares":
                len(angulares),

            "quantidade_com_arco":
                len(com_arco),

            "quantidade_com_transicao_geometrica":
                len(com_transicao),

            "candidatas":
                resultados,

            "seguranca": {
                "geometria_alterada":
                    False,

                "blank_calculado":
                    False,

                "desenvolvimento_calculado":
                    False,

                "k_factor_calculado":
                    False,

                "raio_inventado":
                    False,

                "dobra_confirmada":
                    False,

                "calculadora_corte_chamada":
                    False,
            },
        }

    # =========================================================================
    # ALIASES
    # =========================================================================

    def validar(
        self,
    ) -> Dict[str, Any]:

        return self.validar_candidatas()

    def analisar(
        self,
    ) -> Dict[str, Any]:

        return self.validar_candidatas()

    # =========================================================================
    # VALIDAÇÃO ESTRUTURAL
    # =========================================================================

    @staticmethod
    def validar_resultado(
        resultado: Dict[str, Any],
    ) -> Dict[str, Any]:

        erros: List[str] = []

        campos_obrigatorios = [
            "tipo",
            "status",
            "quantidade_candidatas",
            "candidatas",
            "seguranca",
        ]

        for campo in campos_obrigatorios:

            if campo not in resultado:

                erros.append(
                    f"Campo ausente: {campo}"
                )

        candidatas = resultado.get(
            "candidatas",
            []
        )

        if not isinstance(
            candidatas,
            list,
        ):

            erros.append(
                "Campo candidatas não é uma lista."
            )

        seguranca = resultado.get(
            "seguranca",
            {}
        )

        if not isinstance(
            seguranca,
            dict,
        ):

            erros.append(
                "Campo seguranca não é um dicionário."
            )

        else:

            if seguranca.get(
                "geometria_alterada"
            ) is not False:

                erros.append(
                    "A geometria deveria permanecer inalterada."
                )

            if seguranca.get(
                "blank_calculado"
            ) is not False:

                erros.append(
                    "O validador não pode calcular BLANK."
                )

            if seguranca.get(
                "desenvolvimento_calculado"
            ) is not False:

                erros.append(
                    "O validador não pode calcular desenvolvimento."
                )

            if seguranca.get(
                "dobra_confirmada"
            ) is not False:

                erros.append(
                    "O validador não deve confirmar automaticamente uma dobra."
                )

        return {
            "valido":
                len(erros) == 0,

            "erros":
                erros,
        }

    # =========================================================================
    # RESUMO
    # =========================================================================

    @staticmethod
    def gerar_resumo(
        resultado: Dict[str, Any],
    ) -> Dict[str, Any]:

        return {
            "status":
                resultado.get(
                    "status"
                ),

            "candidatas":
                resultado.get(
                    "quantidade_candidatas",
                    0,
                ),

            "evidencia_forte":
                resultado.get(
                    "quantidade_evidencia_forte",
                    0,
                ),

            "evidencia_moderada":
                resultado.get(
                    "quantidade_evidencia_moderada",
                    0,
                ),

            "evidencia_fraca":
                resultado.get(
                    "quantidade_evidencia_fraca",
                    0,
                ),

            "sem_evidencia":
                resultado.get(
                    "quantidade_sem_evidencia",
                    0,
                ),

            "aproximadamente_90":
                resultado.get(
                    "quantidade_aproximadamente_90",
                    0,
                ),

            "angulares":
                resultado.get(
                    "quantidade_angulares",
                    0,
                ),

            "com_arco":
                resultado.get(
                    "quantidade_com_arco",
                    0,
                ),

            "com_transicao_geometrica":
                resultado.get(
                    "quantidade_com_transicao_geometrica",
                    0,
                ),
        }

    # =========================================================================
    # IMPRESSÃO
    # =========================================================================

    @staticmethod
    def imprimir_resumo(
        resultado: Dict[str, Any],
    ) -> None:

        print()
        print("=" * 80)
        print("AIZI ENGINEERING AI")
        print("VALIDAÇÃO DE DOBRAS")
        print("=" * 80)

        print()

        print(
            f"Status: "
            f"{resultado.get('status')}"
        )

        print(
            f"Segmentos: "
            f"{resultado.get('quantidade_segmentos', 0)}"
        )

        print(
            f"Arcos: "
            f"{resultado.get('quantidade_arcos', 0)}"
        )

        print(
            f"Candidatas: "
            f"{resultado.get('quantidade_candidatas', 0)}"
        )

        print(
            f"Evidência forte: "
            f"{resultado.get('quantidade_evidencia_forte', 0)}"
        )

        print(
            f"Evidência moderada: "
            f"{resultado.get('quantidade_evidencia_moderada', 0)}"
        )

        print(
            f"Evidência fraca: "
            f"{resultado.get('quantidade_evidencia_fraca', 0)}"
        )

        print(
            f"Sem evidência suficiente: "
            f"{resultado.get('quantidade_sem_evidencia', 0)}"
        )

        print(
            f"Aproximadamente 90°: "
            f"{resultado.get('quantidade_aproximadamente_90', 0)}"
        )

        print(
            f"Angulares: "
            f"{resultado.get('quantidade_angulares', 0)}"
        )

        print(
            f"Com arco: "
            f"{resultado.get('quantidade_com_arco', 0)}"
        )

        print(
            f"Com transição geométrica: "
            f"{resultado.get('quantidade_com_transicao_geometrica', 0)}"
        )

        print()
        print("=" * 80)
        print("CANDIDATAS VALIDADAS")
        print("=" * 80)

        candidatas = resultado.get(
            "candidatas",
            []
        )

        if not candidatas:

            print()
            print(
                "Nenhuma candidata encontrada."
            )

        for indice, candidata in enumerate(
            candidatas,
            start=1,
        ):

            print()
            print(
                f"Candidata {indice}"
            )

            print(
                f"  Segmentos: "
                f"{candidata.get('segmentos')}"
            )

            print(
                f"  Ângulo: "
                f"{candidata.get('angulo_graus')}°"
            )

            print(
                f"  Ponto: "
                f"{candidata.get('ponto')}"
            )

            print(
                f"  Raio explícito: "
                f"{candidata.get('raio_mm')}"
            )

            print(
                f"  Possui arco: "
                f"{candidata.get('possui_arco')}"
            )

            print(
                f"  Segmento curto: "
                f"{candidata.get('segmento_curto')}"
            )

            print(
                f"  Transição geométrica: "
                f"{candidata.get('transicao_geometrica')}"
            )

            print(
                f"  Ângulo direcional: "
                f"{candidata.get('angulo_direcional_graus')}°"
            )

            print(
                f"  Padrão repetido: "
                f"{candidata.get('padrao_repetido')}"
            )

            print(
                f"  Pontos de evidência: "
                f"{candidata.get('pontos_evidencia')}"
            )

            print(
                f"  Nível: "
                f"{candidata.get('nivel_evidencia')}"
            )

            print(
                f"  Natureza: "
                f"{candidata.get('natureza')}"
            )

            evidencias = candidata.get(
                "evidencias",
                []
            )

            print(
                f"  Evidências: "
                f"{evidencias}"
            )

            print(
                f"  Dobra confirmada: "
                f"{candidata.get('dobra_confirmada')}"
            )

        print()
        print("=" * 80)
        print("VALIDAÇÃO DE SEGURANÇA")
        print("=" * 80)

        seguranca = resultado.get(
            "seguranca",
            {}
        )

        print(
            f"Geometria alterada: "
            f"{seguranca.get('geometria_alterada')}"
        )

        print(
            f"BLANK calculado: "
            f"{seguranca.get('blank_calculado')}"
        )

        print(
            f"Desenvolvimento calculado: "
            f"{seguranca.get('desenvolvimento_calculado')}"
        )

        print(
            f"K-factor calculado: "
            f"{seguranca.get('k_factor_calculado')}"
        )

        print(
            f"Raio inventado: "
            f"{seguranca.get('raio_inventado')}"
        )

        print(
            f"Dobra confirmada: "
            f"{seguranca.get('dobra_confirmada')}"
        )

        print(
            f"CalculadoraCorte chamada: "
            f"{seguranca.get('calculadora_corte_chamada')}"
        )

        print()

        print(
            "OK - Validador permanece conservador."
        )


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def validar_dobras(
    geometria: Dict[str, Any],
    analise_dobras: Dict[str, Any],
    consolidacao: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    validador = ValidadorDobras(
        geometria=geometria,
        analise_dobras=analise_dobras,
        consolidacao=consolidacao,
    )

    return validador.validar_candidatas()


# =============================================================================
# TESTE DIRETO
# =============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("VALIDADOR DE DOBRAS")
    print("=" * 80)

    print()

    print(
        "Este módulo recebe a geometria interpretada"
    )

    print(
        "e o resultado do AnalisadorDobras."
    )

    print()

    print(
        "Avalia a evidência geométrica das candidatas."
    )

    print(
        "Não confirma automaticamente uma dobra."
    )

    print(
        "Não calcula BLANK."
    )

    print(
        "Não calcula desenvolvimento."
    )

    print(
        "Não calcula K-factor."
    )

    print(
        "Não chama CalculadoraCorte."
    )