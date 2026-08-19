from __future__ import annotations

from typing import Any, Dict, List, Optional
import math


# =============================================================================
# AIZI ENGINEERING AI
# CONSOLIDADOR DE DOBRAS
# =============================================================================
#
# Responsabilidade:
#
# Receber:
#   - geometria interpretada;
#   - resultado produzido pelo AnalisadorDobras.
#
# Consolidar as candidatas geométricas em regiões de possível dobra.
#
# IMPORTANTE:
# - NÃO calcula BLANK.
# - NÃO calcula desenvolvimento.
# - NÃO chama CalculadoraCorte.
# - NÃO inventa raio.
# - NÃO confirma automaticamente uma dobra.
# - NÃO altera a geometria original.
#
# =============================================================================


class ConsolidadorDobras:
    """
    Consolida as candidatas produzidas pelo AnalisadorDobras.

    O módulo mantém dois níveis de saída:

    1. Estrutura principal:
        regioes
        regioes_dobra

    2. Compatibilidade:
        dobras
        quantidade_dobras_consolidadas
        quantidade_90_graus
        quantidade_angulares
        arcos_disponiveis

    Isso permite que os testes e módulos anteriores continuem funcionando
    sem perder a estrutura nova de regiões geométricas.
    """

    LIMITE_SEGMENTO_CURTO_MM = 10.0

    TOLERANCIA_90_GRAUS = 5.0

    TOLERANCIA_ANGULAR_MIN = 15.0

    TOLERANCIA_ANGULAR_MAX = 165.0

    DISTANCIA_AGRUPAMENTO_MM = 15.0

    def __init__(
        self,
        geometria: Optional[Dict[str, Any]] = None,
        analise_dobras: Optional[Dict[str, Any]] = None,
    ):
        self.geometria = geometria or {}
        self.analise_dobras = analise_dobras or {}

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

        valor = ConsolidadorDobras._numero(
            angulo
        )

        if valor is None:
            return None

        valor %= 360.0

        if valor > 180.0:
            valor = 360.0 - valor

        return abs(valor)

    # =========================================================================
    # GEOMETRIA
    # =========================================================================

    def _dados_geometria(
        self,
    ) -> Dict[str, Any]:

        if "geometria" in self.geometria:

            geometria = self.geometria.get(
                "geometria",
                {},
            )

            if isinstance(
                geometria,
                dict,
            ):
                return geometria

            return {}

        return self.geometria

    def _segmentos(
        self,
    ) -> List[Dict[str, Any]]:

        segmentos = self._dados_geometria().get(
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

        arcos = self._dados_geometria().get(
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

        resultado = {}

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
    # TAMANHO DO SEGMENTO
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
            return comprimento

        x1 = self._numero(
            segmento.get("x1"),
            0.0,
        )

        y1 = self._numero(
            segmento.get("y1"),
            0.0,
        )

        x2 = self._numero(
            segmento.get("x2"),
            0.0,
        )

        y2 = self._numero(
            segmento.get("y2"),
            0.0,
        )

        return math.hypot(
            x2 - x1,
            y2 - y1,
        )

    def _eh_segmento_curto(
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
    # SEGMENTOS CURTOS
    # =========================================================================

    def _ids_segmentos_curtos(
        self,
    ) -> List[int]:

        resultado = []

        for segmento in self._segmentos():

            if not self._eh_segmento_curto(
                segmento
            ):
                continue

            try:
                resultado.append(
                    int(
                        segmento.get("id")
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

        return resultado

    # =========================================================================
    # CANDIDATAS
    # =========================================================================

    def _candidatas(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Obtém as candidatas do AnalisadorDobras.

        Contrato principal:
            analise_dobras["dobras"]

        Compatibilidade:
            analise_dobras["candidatas"]
        """

        candidatas = self.analise_dobras.get(
            "dobras"
        )

        if isinstance(
            candidatas,
            list,
        ):
            return candidatas

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
    # IDS DOS SEGMENTOS
    # =========================================================================

    @staticmethod
    def _ids_da_candidata(
        candidata: Dict[str, Any],
    ) -> List[int]:

        resultado = []

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
                resultado.append(
                    int(valor)
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

        if resultado:
            return resultado

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
                resultado.append(
                    int(valor)
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

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
                    resultado.append(
                        int(valor)
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    continue

        return resultado

    # =========================================================================
    # PONTO
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
                "x": ConsolidadorDobras._numero(
                    ponto.get("x_mm")
                ),
                "y": ConsolidadorDobras._numero(
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
                "x": ConsolidadorDobras._numero(
                    ponto.get("x")
                ),
                "y": ConsolidadorDobras._numero(
                    ponto.get("y")
                ),
            }

        return {
            "x": ConsolidadorDobras._numero(
                candidata.get("x")
            ),
            "y": ConsolidadorDobras._numero(
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
    # RAIO
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
    # ARCO PRÓXIMO
    # =========================================================================

    def _encontrar_arco_proximo(
        self,
        ponto: Dict[str, Optional[float]],
    ) -> Optional[Dict[str, Any]]:

        arcos = self._arcos()

        if not arcos:
            return None

        x = ponto.get("x")
        y = ponto.get("y")

        if x is None or y is None:
            return None

        melhor = None
        menor_distancia = None

        for arco in arcos:

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
    # CLASSIFICAÇÃO
    # =========================================================================

    def _classificar_candidata(
        self,
        candidata: Dict[str, Any],
        mapa_segmentos: Dict[int, Dict[str, Any]],
    ) -> Dict[str, Any]:

        ids = self._ids_da_candidata(
            candidata
        )

        segmentos = [
            mapa_segmentos[x]
            for x in ids
            if x in mapa_segmentos
        ]

        angulo = self._angulo_candidata(
            candidata
        )

        ponto = self._ponto_candidata(
            candidata
        )

        raio = self._raio_candidata(
            candidata
        )

        segmento_curto = any(
            self._eh_segmento_curto(
                segmento
            )
            for segmento in segmentos
        )

        arco_proximo = (
            self._encontrar_arco_proximo(
                ponto
            )
        )

        possui_arco = False

        if arco_proximo is not None:

            raio_arco = self._numero(
                arco_proximo.get(
                    "raio_mm",
                    arco_proximo.get("raio")
                )
            )

            # IMPORTANTE:
            # O raio do arco é evidência geométrica.
            # Não é um raio inventado pelo consolidador.
            if (
                raio is None
                and raio_arco is not None
                and raio_arco > 0
            ):
                raio = raio_arco

            possui_arco = True

        eh_90 = (
            angulo is not None
            and abs(
                angulo - 90.0
            )
            <= self.TOLERANCIA_90_GRAUS
        )

        if eh_90 and possui_arco:

            classificacao = (
                "REGIAO_DOBRA_COM_ARCO"
            )

            confianca = "ALTA"

        elif eh_90:

            classificacao = (
                "CANDIDATA_DOBRA_90_SEM_ARCO"
            )

            confianca = "MEDIA"

        elif (
            angulo is not None
            and
            self.TOLERANCIA_ANGULAR_MIN
            <= angulo
            <= self.TOLERANCIA_ANGULAR_MAX
        ):

            classificacao = (
                "TRANSICAO_ANGULAR"
            )

            confianca = "BAIXA"

        else:

            classificacao = (
                "TRANSICAO_NAO_RELEVANTE"
            )

            confianca = "BAIXA"

        return {
            "segmentos": ids,
            "angulo_graus": angulo,
            "ponto": ponto,
            "raio_mm": raio,
            "possui_arco": possui_arco,
            "segmento_curto": segmento_curto,
            "classificacao": classificacao,
            "confianca": confianca,
        }

    # =========================================================================
    # DISTÂNCIA ENTRE CANDIDATAS
    # =========================================================================

    @staticmethod
    def _distancia_candidatas(
        candidata_a: Dict[str, Any],
        candidata_b: Dict[str, Any],
    ) -> float:

        ponto_a = candidata_a.get(
            "ponto",
            {}
        )

        ponto_b = candidata_b.get(
            "ponto",
            {}
        )

        xa = ConsolidadorDobras._numero(
            ponto_a.get("x")
        )

        ya = ConsolidadorDobras._numero(
            ponto_a.get("y")
        )

        xb = ConsolidadorDobras._numero(
            ponto_b.get("x")
        )

        yb = ConsolidadorDobras._numero(
            ponto_b.get("y")
        )

        if (
            xa is None
            or ya is None
            or xb is None
            or yb is None
        ):
            return float("inf")

        return math.hypot(
            xb - xa,
            yb - ya,
        )

    # =========================================================================
    # AGRUPAMENTO
    # =========================================================================

    def agrupar_candidatas(
        self,
        candidatas: List[Dict[str, Any]],
    ) -> List[List[Dict[str, Any]]]:

        if not candidatas:
            return []

        grupos = []
        usadas = set()

        for i, candidata in enumerate(
            candidatas
        ):

            if i in usadas:
                continue

            grupo = [candidata]
            usadas.add(i)

            alterou = True

            while alterou:

                alterou = False

                for j, outra in enumerate(
                    candidatas
                ):

                    if j in usadas:
                        continue

                    for existente in grupo:

                        if (
                            self._distancia_candidatas(
                                existente,
                                outra,
                            )
                            <= self.DISTANCIA_AGRUPAMENTO_MM
                        ):

                            grupo.append(
                                outra
                            )

                            usadas.add(j)

                            alterou = True

                            break

            grupos.append(grupo)

        return grupos

    # =========================================================================
    # REPRESENTANTE
    # =========================================================================

    def _representante_grupo(
        self,
        grupo: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        if not grupo:
            return {}

        com_arco = [
            x
            for x in grupo
            if x.get("possui_arco")
        ]

        if com_arco:

            return max(
                com_arco,
                key=lambda x:
                    x.get("raio_mm") or 0.0,
            )

        candidatos_90 = [
            x
            for x in grupo
            if (
                x.get("angulo_graus") is not None
                and
                abs(
                    x.get("angulo_graus")
                    - 90.0
                )
                <= self.TOLERANCIA_90_GRAUS
            )
        ]

        if candidatos_90:
            return candidatos_90[0]

        return grupo[0]

    # =========================================================================
    # CONSOLIDAÇÃO
    # =========================================================================

    def consolidar(
        self,
    ) -> Dict[str, Any]:

        segmentos = self._segmentos()
        arcos = self._arcos()
        candidatas = self._candidatas()

        mapa_segmentos = (
            self._mapa_segmentos()
        )

        analisadas = []

        for candidata in candidatas:

            dados = self._classificar_candidata(
                candidata,
                mapa_segmentos,
            )

            dados["origem"] = candidata

            analisadas.append(
                dados
            )

        # ---------------------------------------------------------------------
        # Somente transições relevantes seguem para agrupamento
        # ---------------------------------------------------------------------

        relevantes = [
            candidata
            for candidata in analisadas
            if candidata.get(
                "classificacao"
            )
            != "TRANSICAO_NAO_RELEVANTE"
        ]

        grupos = self.agrupar_candidatas(
            relevantes
        )

        regioes = []

        for numero, grupo in enumerate(
            grupos,
            start=1,
        ):

            representante = (
                self._representante_grupo(
                    grupo
                )
            )

            possui_arco = any(
                candidata.get(
                    "possui_arco"
                )
                for candidata in grupo
            )

            tem_90 = any(
                candidata.get(
                    "angulo_graus"
                ) is not None
                and
                abs(
                    candidata.get(
                        "angulo_graus"
                    )
                    - 90.0
                )
                <= self.TOLERANCIA_90_GRAUS
                for candidata in grupo
            )

            if possui_arco:

                status = (
                    "REGIAO_DOBRA_COM_EVIDENCIA_DE_ARCO"
                )

                confianca = "ALTA"

            elif tem_90:

                status = (
                    "REGIAO_DOBRA_CANDIDATA"
                )

                confianca = "MEDIA"

            else:

                status = (
                    "REGIAO_GEOMETRICA_NAO_CONFIRMADA"
                )

                confianca = "BAIXA"

            segmentos_regiao = sorted(
                {
                    segmento
                    for candidata in grupo
                    for segmento in candidata.get(
                        "segmentos",
                        []
                    )
                }
            )

            # -----------------------------------------------------------------
            # Compatibilidade com o formato antigo
            # -----------------------------------------------------------------

            classificacao = (
                representante.get(
                    "classificacao"
                )
            )

            origem = (
                representante.get(
                    "origem"
                )
            )

            regiao = {
                "id": numero,

                "segmentos":
                    segmentos_regiao,

                "quantidade_candidatas":
                    len(grupo),

                "angulo_representativo_graus":
                    representante.get(
                        "angulo_graus"
                    ),

                # Campo compatível com o teste antigo
                "angulo_graus":
                    representante.get(
                        "angulo_graus"
                    ),

                "raio_mm":
                    representante.get(
                        "raio_mm"
                    ),

                "possui_arco":
                    possui_arco,

                "status":
                    status,

                # Campo compatível com o teste antigo
                "classificacao":
                    classificacao,

                "confianca":
                    confianca,

                "ponto":
                    representante.get(
                        "ponto"
                    ),

                "origem":
                    origem,

                "candidatas":
                    grupo,
            }

            regioes.append(
                regiao
            )

        regioes_dobra = [
            regiao
            for regiao in regioes
            if regiao.get("status")
            in (
                "REGIAO_DOBRA_COM_EVIDENCIA_DE_ARCO",
                "REGIAO_DOBRA_CANDIDATA",
            )
        ]

        # ---------------------------------------------------------------------
        # STATUS
        # ---------------------------------------------------------------------

        if not candidatas:

            status = (
                "NENHUMA_DOBRA_CANDIDATA"
            )

        elif not regioes_dobra:

            status = (
                "NENHUMA_REGIAO_DE_DOBRA_CONFIRMAVEL"
            )

        elif arcos:

            status = (
                "REGIOES_DE_DOBRA_COM_ARCOS"
            )

        else:

            status = (
                "REGIOES_DE_DOBRA_CANDIDATAS_SEM_ARCOS"
            )

        # ---------------------------------------------------------------------
        # CONTAGENS
        # ---------------------------------------------------------------------

        quantidade_90 = sum(
            1
            for candidata in analisadas
            if (
                candidata.get(
                    "angulo_graus"
                ) is not None
                and
                abs(
                    candidata.get(
                        "angulo_graus"
                    )
                    - 90.0
                )
                <= self.TOLERANCIA_90_GRAUS
            )
        )

        quantidade_angular = sum(
            1
            for candidata in analisadas
            if (
                candidata.get(
                    "angulo_graus"
                ) is not None
                and
                self.TOLERANCIA_ANGULAR_MIN
                <= candidata.get(
                    "angulo_graus"
                )
                <= self.TOLERANCIA_ANGULAR_MAX
                and
                abs(
                    candidata.get(
                        "angulo_graus"
                    )
                    - 90.0
                )
                > self.TOLERANCIA_90_GRAUS
            )
        )

        # ---------------------------------------------------------------------
        # SEGURANÇA
        # ---------------------------------------------------------------------

        seguranca = {
            "blank_calculado":
                False,

            "desenvolvimento_calculado":
                False,

            "raio_inventado":
                False,

            "dobra_confirmada_automaticamente":
                False,

            "calculadora_corte_chamada":
                False,
        }

        # ---------------------------------------------------------------------
        # RETORNO
        # ---------------------------------------------------------------------
        #
        # "regioes" e "regioes_dobra" são a estrutura principal atual.
        #
        # "dobras" é um alias deliberado para compatibilidade com:
        #
        #   teste_consolidador_dobras.py
        #
        # Assim, a saída:
        #
        #   Dobras consolidadas: 6
        #
        # continua correta.
        # ---------------------------------------------------------------------

        return {
            "tipo":
                "CONSOLIDACAO_DOBRAS",

            "status":
                status,

            "quantidade_segmentos":
                len(segmentos),

            "quantidade_arcos":
                len(arcos),

            "arcos_disponiveis":
                len(arcos),

            "quantidade_segmentos_curtos":
                len(
                    self._ids_segmentos_curtos()
                ),

            "segmentos_curtos":
                self._ids_segmentos_curtos(),

            "quantidade_candidatas_original":
                len(candidatas),

            "quantidade_candidatas_originais":
                len(candidatas),

            "quantidade_candidatas_analisadas":
                len(analisadas),

            "quantidade_candidatas_90_graus":
                quantidade_90,

            "quantidade_90_graus":
                quantidade_90,

            "quantidade_candidatas_angulares":
                quantidade_angular,

            "quantidade_angulares":
                quantidade_angular,

            "quantidade_regioes":
                len(regioes),

            "quantidade_regioes_dobra":
                len(regioes_dobra),

            "quantidade_dobras_consolidadas":
                len(regioes_dobra),

            # -------------------------------------------------------------
            # Estrutura nova
            # -------------------------------------------------------------

            "regioes":
                regioes,

            "regioes_dobra":
                regioes_dobra,

            # -------------------------------------------------------------
            # Compatibilidade com o teste/módulos anteriores
            # -------------------------------------------------------------

            "dobras":
                regioes_dobra,

            "seguranca":
                seguranca,
        }

    # =========================================================================
    # ALIAS
    # =========================================================================

    def analisar(
        self,
    ) -> Dict[str, Any]:

        return self.consolidar()

    # =========================================================================
    # VALIDAÇÃO
    # =========================================================================

    @staticmethod
    def validar(
        resultado: Dict[str, Any],
    ) -> Dict[str, Any]:

        erros = []

        campos = [
            "status",
            "quantidade_candidatas_original",
            "quantidade_regioes",
            "regioes",
            "regioes_dobra",
            "dobras",
            "seguranca",
        ]

        for campo in campos:

            if campo not in resultado:

                erros.append(
                    f"Campo ausente: {campo}"
                )

        regioes = resultado.get(
            "regioes",
            [],
        )

        regioes_dobra = resultado.get(
            "regioes_dobra",
            [],
        )

        dobras = resultado.get(
            "dobras",
            [],
        )

        if not isinstance(
            regioes,
            list,
        ):

            erros.append(
                "Campo regioes não é uma lista."
            )

        if not isinstance(
            regioes_dobra,
            list,
        ):

            erros.append(
                "Campo regioes_dobra não é uma lista."
            )

        if not isinstance(
            dobras,
            list,
        ):

            erros.append(
                "Campo dobras não é uma lista."
            )

        quantidade_original = resultado.get(
            "quantidade_candidatas_original"
        )

        if (
            isinstance(
                quantidade_original,
                int,
            )
            and quantidade_original < 0
        ):

            erros.append(
                "Quantidade original inválida."
            )

        quantidade_dobras = resultado.get(
            "quantidade_dobras_consolidadas"
        )

        if (
            isinstance(
                quantidade_dobras,
                int,
            )
            and quantidade_dobras < 0
        ):

            erros.append(
                "Quantidade de dobras consolidadas inválida."
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

            "candidatas_originais":
                resultado.get(
                    "quantidade_candidatas_original",
                    0,
                ),

            "candidatas_90_graus":
                resultado.get(
                    "quantidade_candidatas_90_graus",
                    0,
                ),

            "candidatas_angulares":
                resultado.get(
                    "quantidade_candidatas_angulares",
                    0,
                ),

            "regioes_consolidadas":
                resultado.get(
                    "quantidade_regioes",
                    0,
                ),

            "regioes_dobra":
                resultado.get(
                    "quantidade_regioes_dobra",
                    0,
                ),

            "dobras_consolidadas":
                resultado.get(
                    "quantidade_dobras_consolidadas",
                    0,
                ),

            "arcos_disponiveis":
                resultado.get(
                    "quantidade_arcos",
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
        print("CONSOLIDAÇÃO DE DOBRAS")
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
            f"Segmentos curtos: "
            f"{resultado.get('quantidade_segmentos_curtos', 0)}"
        )

        print(
            f"Candidatas originais: "
            f"{resultado.get('quantidade_candidatas_original', 0)}"
        )

        print(
            f"Candidatas analisadas: "
            f"{resultado.get('quantidade_candidatas_analisadas', 0)}"
        )

        print(
            f"Candidatas aproximadamente 90°: "
            f"{resultado.get('quantidade_candidatas_90_graus', 0)}"
        )

        print(
            f"Candidatas angulares: "
            f"{resultado.get('quantidade_candidatas_angulares', 0)}"
        )

        print(
            f"Regiões consolidadas: "
            f"{resultado.get('quantidade_regioes', 0)}"
        )

        print(
            f"Regiões candidatas a dobra: "
            f"{resultado.get('quantidade_regioes_dobra', 0)}"
        )

        print(
            f"Dobras consolidadas: "
            f"{resultado.get('quantidade_dobras_consolidadas', 0)}"
        )

        print()

        print("=" * 80)
        print("REGIÕES CONSOLIDADAS")
        print("=" * 80)

        regioes = resultado.get(
            "regioes",
            [],
        )

        if not regioes:

            print()
            print(
                "Nenhuma região consolidada."
            )

        for regiao in regioes:

            print()
            print(
                f"Região {regiao.get('id')}"
            )

            print(
                f"  Segmentos: "
                f"{regiao.get('segmentos')}"
            )

            print(
                f"  Candidatas agrupadas: "
                f"{regiao.get('quantidade_candidatas')}"
            )

            print(
                f"  Ângulo representativo: "
                f"{regiao.get('angulo_representativo_graus')}°"
            )

            print(
                f"  Raio: "
                f"{regiao.get('raio_mm')}"
            )

            print(
                f"  Possui arco: "
                f"{regiao.get('possui_arco')}"
            )

            print(
                f"  Classificação: "
                f"{regiao.get('classificacao')}"
            )

            print(
                f"  Status: "
                f"{regiao.get('status')}"
            )

            print(
                f"  Confiança: "
                f"{regiao.get('confianca')}"
            )

            ponto = regiao.get(
                "ponto"
            )

            if ponto:

                print(
                    f"  Ponto: "
                    f"X={ponto.get('x')} | "
                    f"Y={ponto.get('y')} mm"
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
            f"BLANK calculado: "
            f"{seguranca.get('blank_calculado')}"
        )

        print(
            f"Desenvolvimento calculado: "
            f"{seguranca.get('desenvolvimento_calculado')}"
        )

        print(
            f"Raio inventado: "
            f"{seguranca.get('raio_inventado')}"
        )

        print(
            f"Dobra confirmada automaticamente: "
            f"{seguranca.get('dobra_confirmada_automaticamente')}"
        )

        print(
            f"CalculadoraCorte chamada: "
            f"{seguranca.get('calculadora_corte_chamada')}"
        )

        print()

        print(
            "OK - Consolidador permanece conservador."
        )


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def consolidar_dobras(
    geometria: Dict[str, Any],
    analise_dobras: Dict[str, Any],
) -> Dict[str, Any]:

    consolidador = ConsolidadorDobras(
        geometria=geometria,
        analise_dobras=analise_dobras,
    )

    return consolidador.consolidar()


# =============================================================================
# TESTE DIRETO
# =============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("CONSOLIDADOR DE DOBRAS")
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
        "Não calcula BLANK."
    )

    print(
        "Não calcula desenvolvimento."
    )

    print(
        "Não chama CalculadoraCorte."
    )