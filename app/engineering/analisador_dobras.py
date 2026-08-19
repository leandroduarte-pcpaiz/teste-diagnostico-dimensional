from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# AIZI ENGINEERING AI
# ANALISADOR DE DOBRAS
# =============================================================================
#
# Responsabilidade:
# ----------------
# Analisar a geometria interpretada de uma peça de chapa e identificar
# possíveis regiões/linhas associadas a dobras.
#
# IMPORTANTE:
# -----------
# Este módulo:
#
# - NÃO calcula BLANK.
# - NÃO calcula desenvolvimento.
# - NÃO altera a geometria original.
# - NÃO inventa raio.
# - NÃO confirma automaticamente uma dobra.
#
# REGRA IMPORTANTE:
# -----------------
# Mudanças angulares envolvendo segmentos muito curtos NÃO são consideradas
# candidatas a dobra.
#
# Isso evita interpretar pequenos segmentos de fechamento, retornos ou
# detalhes do contorno como dobras de fabricação.
#
# CONTRATO PRINCIPAL:
#
#     resultado["transicoes"]
#     resultado["transicoes_analisadas"]
#     resultado["dobras"]
#     resultado["candidatas"]
#     resultado["quantidade_candidatas"]
#
# O ConsolidadorDobras consome:
#
#     resultado["dobras"]
#
# =============================================================================


# =============================================================================
# TOLERÂNCIAS
# =============================================================================

TOLERANCIA_ANGULO_GRAUS = 5.0

TOLERANCIA_CONEXAO_MM = 1.0

TOLERANCIA_COLINEARIDADE_MM = 0.5

ANGULO_DOBRA_MINIMO = 10.0

ANGULO_DOBRA_MAXIMO = 170.0

ANGULO_DOBRA_90 = 90.0

# Segmento abaixo deste valor não pode participar de uma candidata de dobra.
COMPRIMENTO_MINIMO_SEGMENTO_DOBRA_MM = 10.0

# Segmentos abaixo deste valor são registrados como segmentos curtos.
LIMITE_SEGMENTO_CURTO_MM = 10.0


# =============================================================================
# FUNÇÕES BÁSICAS
# =============================================================================

def _numero(
    valor: Any,
) -> Optional[float]:

    if valor is None:
        return None

    try:
        return float(valor)

    except (TypeError, ValueError):
        return None


def _ponto(
    segmento: Dict[str, Any],
    inicio: bool,
) -> Optional[Dict[str, float]]:

    try:

        if inicio:

            return {
                "x": float(segmento["x1"]),
                "y": float(segmento["y1"]),
            }

        return {
            "x": float(segmento["x2"]),
            "y": float(segmento["y2"]),
        }

    except (
        KeyError,
        TypeError,
        ValueError,
    ):

        return None


def _distancia_pontos(
    ponto_a: Dict[str, float],
    ponto_b: Dict[str, float],
) -> float:

    return math.hypot(
        ponto_a["x"] - ponto_b["x"],
        ponto_a["y"] - ponto_b["y"],
    )


def _vetor(
    p1: Dict[str, float],
    p2: Dict[str, float],
) -> Tuple[float, float]:

    return (
        p2["x"] - p1["x"],
        p2["y"] - p1["y"],
    )


def _comprimento_vetor(
    vetor: Tuple[float, float],
) -> float:

    return math.hypot(
        vetor[0],
        vetor[1],
    )


def _angulo_vetor(
    vetor: Tuple[float, float],
) -> float:

    return math.degrees(
        math.atan2(
            vetor[1],
            vetor[0],
        )
    )


def _normalizar_angulo(
    angulo: float,
) -> float:

    return angulo % 360.0


def _diferenca_angular(
    angulo1: float,
    angulo2: float,
) -> float:

    diferenca = abs(
        _normalizar_angulo(angulo1)
        - _normalizar_angulo(angulo2)
    )

    if diferenca > 180.0:

        diferenca = 360.0 - diferenca

    return diferenca


# =============================================================================
# SEGMENTOS
# =============================================================================

def _tipo_segmento(
    segmento: Dict[str, Any],
) -> str:

    tipo = segmento.get("tipo")

    if tipo:

        return str(
            tipo
        ).upper()

    return "DESCONHECIDO"


def _comprimento_segmento(
    segmento: Dict[str, Any],
) -> Optional[float]:

    comprimento = _numero(
        segmento.get(
            "comprimento_mm"
        )
    )

    if comprimento is not None:

        return comprimento

    p1 = _ponto(
        segmento,
        True,
    )

    p2 = _ponto(
        segmento,
        False,
    )

    if p1 is None or p2 is None:

        return None

    return _distancia_pontos(
        p1,
        p2,
    )


def _segmento_e_relevante(
    segmento: Dict[str, Any],
) -> bool:

    comprimento = _comprimento_segmento(
        segmento
    )

    if comprimento is None:

        return False

    return (
        comprimento
        >= COMPRIMENTO_MINIMO_SEGMENTO_DOBRA_MM
    )


def identificar_segmentos_curto(
    segmentos: List[Dict[str, Any]],
) -> List[int]:

    resultado = []

    for segmento in segmentos:

        comprimento = _comprimento_segmento(
            segmento
        )

        if (
            comprimento is not None
            and comprimento < LIMITE_SEGMENTO_CURTO_MM
        ):

            try:

                resultado.append(
                    int(
                        segmento.get(
                            "id"
                        )
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

    return resultado


# =============================================================================
# CONEXÕES GEOMÉTRICAS
# =============================================================================

def _conexoes_segmentos(
    segmento_a: Dict[str, Any],
    segmento_b: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Identifica todas as formas possíveis de conexão entre dois segmentos.

    São testadas as quatro combinações:

        A1 -> B1
        A1 -> B2
        A2 -> B1
        A2 -> B2

    Isso permite trabalhar mesmo quando a orientação dos segmentos
    no JSON está invertida.
    """

    a1 = _ponto(
        segmento_a,
        True,
    )

    a2 = _ponto(
        segmento_a,
        False,
    )

    b1 = _ponto(
        segmento_b,
        True,
    )

    b2 = _ponto(
        segmento_b,
        False,
    )

    if (
        a1 is None
        or a2 is None
        or b1 is None
        or b2 is None
    ):

        return []

    possibilidades = [
        (
            "A1_B1",
            a1,
            b1,
            a2,
            b2,
        ),
        (
            "A1_B2",
            a1,
            b2,
            a2,
            b1,
        ),
        (
            "A2_B1",
            a2,
            b1,
            a1,
            b2,
        ),
        (
            "A2_B2",
            a2,
            b2,
            a1,
            b1,
        ),
    ]

    resultado = []

    for (
        orientacao,
        ponto_a,
        ponto_b,
        outro_a,
        outro_b,
    ) in possibilidades:

        distancia = _distancia_pontos(
            ponto_a,
            ponto_b,
        )

        resultado.append(
            {
                "orientacao": orientacao,
                "distancia_mm": distancia,
                "ponto_conexao": {
                    "x": (
                        ponto_a["x"]
                        + ponto_b["x"]
                    )
                    / 2.0,
                    "y": (
                        ponto_a["y"]
                        + ponto_b["y"]
                    )
                    / 2.0,
                },
                "ponto_a": ponto_a,
                "ponto_b": ponto_b,
                "outro_a": outro_a,
                "outro_b": outro_b,
            }
        )

    resultado.sort(
        key=lambda item:
            item["distancia_mm"]
    )

    return resultado


def _melhor_conexao(
    segmento_a: Dict[str, Any],
    segmento_b: Dict[str, Any],
) -> Optional[Dict[str, Any]]:

    conexoes = _conexoes_segmentos(
        segmento_a,
        segmento_b,
    )

    if not conexoes:

        return None

    melhor = conexoes[0]

    if (
        melhor["distancia_mm"]
        > TOLERANCIA_CONEXAO_MM
    ):

        return None

    return melhor


# =============================================================================
# ÂNGULO ENTRE SEGMENTOS CONECTADOS
# =============================================================================

def _angulo_conexao(
    segmento_a: Dict[str, Any],
    segmento_b: Dict[str, Any],
    conexao: Dict[str, Any],
) -> Optional[float]:
    """
    Calcula a mudança angular na conexão real entre dois segmentos.

    O vetor de entrada de A aponta até a conexão.

    O vetor de saída de B aponta a partir da conexão.

    O resultado é a menor diferença angular entre os dois vetores.
    """

    try:

        orientacao = conexao.get(
            "orientacao"
        )

        if orientacao == "A1_B1":

            ponto_conexao = _ponto(
                segmento_a,
                True,
            )

            outro_a = _ponto(
                segmento_a,
                False,
            )

            outro_b = _ponto(
                segmento_b,
                False,
            )

        elif orientacao == "A1_B2":

            ponto_conexao = _ponto(
                segmento_a,
                True,
            )

            outro_a = _ponto(
                segmento_a,
                False,
            )

            outro_b = _ponto(
                segmento_b,
                True,
            )

        elif orientacao == "A2_B1":

            ponto_conexao = _ponto(
                segmento_a,
                False,
            )

            outro_a = _ponto(
                segmento_a,
                True,
            )

            outro_b = _ponto(
                segmento_b,
                False,
            )

        elif orientacao == "A2_B2":

            ponto_conexao = _ponto(
                segmento_a,
                False,
            )

            outro_a = _ponto(
                segmento_a,
                True,
            )

            outro_b = _ponto(
                segmento_b,
                True,
            )

        else:

            return None

        if (
            ponto_conexao is None
            or outro_a is None
            or outro_b is None
        ):

            return None

        vetor_entrada = _vetor(
            outro_a,
            ponto_conexao,
        )

        vetor_saida = _vetor(
            ponto_conexao,
            outro_b,
        )

        comprimento_entrada = (
            _comprimento_vetor(
                vetor_entrada
            )
        )

        comprimento_saida = (
            _comprimento_vetor(
                vetor_saida
            )
        )

        if (
            comprimento_entrada <= 0.0001
            or comprimento_saida <= 0.0001
        ):

            return None

        angulo_entrada = _angulo_vetor(
            vetor_entrada
        )

        angulo_saida = _angulo_vetor(
            vetor_saida
        )

        return _diferenca_angular(
            angulo_entrada,
            angulo_saida,
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):

        return None


# =============================================================================
# CLASSIFICAÇÃO ANGULAR
# =============================================================================

def classificar_angulo(
    angulo: Optional[float],
) -> str:

    if angulo is None:

        return "NAO_DETERMINADO"

    if angulo < ANGULO_DOBRA_MINIMO:

        return "SEM_DOBRA_RELEVANTE"

    if (
        abs(
            angulo
            - ANGULO_DOBRA_90
        )
        <= TOLERANCIA_ANGULO_GRAUS
    ):

        return (
            "DOBRA_APROXIMADAMENTE_90_GRAUS"
        )

    if (
        ANGULO_DOBRA_MINIMO
        <= angulo
        <= ANGULO_DOBRA_MAXIMO
    ):

        return "MUDANCA_ANGULAR"

    return "NAO_CLASSIFICADO"


# =============================================================================
# ANÁLISE DE TRANSIÇÕES
# =============================================================================

def analisar_transicoes(
    segmentos: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Analisa conexões geométricas reais entre os segmentos.

    IMPORTANTE:
    -----------
    Não assume que a ordem dos segmentos no JSON representa
    a ordem geométrica da peça.

    Cada par de segmentos é comparado e somente conexões
    geometricamente válidas são registradas.

    SEGMENTOS CURTOS:
    -----------------
    Transições envolvendo segmentos abaixo do comprimento mínimo
    continuam sendo registradas para diagnóstico, porém são marcadas
    como não relevantes para dobra.
    """

    transicoes = []

    if len(segmentos) < 2:

        return transicoes

    pares_analisados = set()

    for indice_a in range(
        len(segmentos)
    ):

        segmento_a = segmentos[
            indice_a
        ]

        id_a = segmento_a.get(
            "id",
            indice_a,
        )

        for indice_b in range(
            indice_a + 1,
            len(segmentos),
        ):

            segmento_b = segmentos[
                indice_b
            ]

            id_b = segmento_b.get(
                "id",
                indice_b,
            )

            chave_par = (
                str(id_a),
                str(id_b),
            )

            if chave_par in pares_analisados:

                continue

            pares_analisados.add(
                chave_par
            )

            conexao = _melhor_conexao(
                segmento_a,
                segmento_b,
            )

            if conexao is None:

                continue

            angulo = _angulo_conexao(
                segmento_a,
                segmento_b,
                conexao,
            )

            comprimento_a = (
                _comprimento_segmento(
                    segmento_a
                )
            )

            comprimento_b = (
                _comprimento_segmento(
                    segmento_b
                )
            )

            segmentos_relevantes = (
                _segmento_e_relevante(
                    segmento_a
                )
                and
                _segmento_e_relevante(
                    segmento_b
                )
            )

            classificacao = classificar_angulo(
                angulo
            )

            # -------------------------------------------------------------
            # REGRA DE SEGURANÇA:
            #
            # Se um dos segmentos for curto, a transição não pode ser
            # considerada uma transição de dobra.
            #
            # A transição continua no diagnóstico, mas sua classificação
            # deixa explícito que ela não deve gerar candidata.
            # -------------------------------------------------------------

            if not segmentos_relevantes:

                classificacao = (
                    "SEGMENTO_CURTO_SEM_DOBRA"
                )

            transicoes.append(
                {
                    "indice":
                        len(transicoes) + 1,

                    "segmento_anterior":
                        id_a,

                    "segmento_atual":
                        id_b,

                    "tipo_anterior":
                        _tipo_segmento(
                            segmento_a
                        ),

                    "tipo_atual":
                        _tipo_segmento(
                            segmento_b
                        ),

                    "comprimento_anterior_mm":
                        comprimento_a,

                    "comprimento_atual_mm":
                        comprimento_b,

                    "distancia_conexao_mm":
                        round(
                            conexao[
                                "distancia_mm"
                            ],
                            6,
                        ),

                    "orientacao_conexao":
                        conexao[
                            "orientacao"
                        ],

                    "ponto_conexao":
                        conexao[
                            "ponto_conexao"
                        ],

                    "angulo_mudanca_graus":
                        (
                            round(
                                angulo,
                                4,
                            )
                            if angulo is not None
                            else None
                        ),

                    "classificacao":
                        classificacao,

                    "segmentos_relevantes":
                        segmentos_relevantes,
                }
            )

    return transicoes


# =============================================================================
# DETECÇÃO DE CANDIDATAS
# =============================================================================

def detectar_candidatas_dobra(
    segmentos: List[Dict[str, Any]],
    transicoes: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    candidatas = []

    mapa_segmentos = {}

    for segmento in segmentos:

        try:

            identificador = int(
                segmento.get(
                    "id"
                )
            )

            mapa_segmentos[
                identificador
            ] = segmento

        except (
            TypeError,
            ValueError,
        ):

            continue

    for transicao in transicoes:

        # -----------------------------------------------------------------
        # PRIMEIRA BARREIRA DE SEGURANÇA
        #
        # Somente transições em que os dois segmentos são relevantes
        # podem gerar candidata de dobra.
        # -----------------------------------------------------------------

        if not transicao.get(
            "segmentos_relevantes",
            False,
        ):

            continue

        angulo = transicao.get(
            "angulo_mudanca_graus"
        )

        if angulo is None:

            continue

        if angulo < ANGULO_DOBRA_MINIMO:

            continue

        if angulo > ANGULO_DOBRA_MAXIMO:

            continue

        try:

            id_anterior = int(
                transicao.get(
                    "segmento_anterior"
                )
            )

            id_atual = int(
                transicao.get(
                    "segmento_atual"
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

        segmento_anterior = mapa_segmentos.get(
            id_anterior
        )

        segmento_atual = mapa_segmentos.get(
            id_atual
        )

        if (
            segmento_anterior is None
            or segmento_atual is None
        ):

            continue

        comprimento_anterior = (
            _comprimento_segmento(
                segmento_anterior
            )
        )

        comprimento_atual = (
            _comprimento_segmento(
                segmento_atual
            )
        )

        if (
            comprimento_anterior is None
            or comprimento_atual is None
        ):

            continue

        # -----------------------------------------------------------------
        # SEGUNDA BARREIRA DE SEGURANÇA
        #
        # Mesmo que a transição tenha sido marcada anteriormente,
        # validamos novamente os comprimentos aqui.
        # -----------------------------------------------------------------

        if (
            comprimento_anterior
            < COMPRIMENTO_MINIMO_SEGMENTO_DOBRA_MM
        ):

            continue

        if (
            comprimento_atual
            < COMPRIMENTO_MINIMO_SEGMENTO_DOBRA_MM
        ):

            continue

        if (
            abs(
                angulo
                - ANGULO_DOBRA_90
            )
            <= TOLERANCIA_ANGULO_GRAUS
        ):

            classificacao = (
                "CANDIDATA_DOBRA_90_GRAUS"
            )

            confianca = "ALTA"

        else:

            classificacao = (
                "CANDIDATA_DOBRA_ANGULAR"
            )

            confianca = "MEDIA"

        ponto = transicao.get(
            "ponto_conexao"
        )

        if not isinstance(
            ponto,
            dict,
        ):

            ponto = {
                "x": None,
                "y": None,
            }

        x = _numero(
            ponto.get("x")
        )

        y = _numero(
            ponto.get("y")
        )

        candidatas.append(
            {
                "segmento_anterior":
                    id_anterior,

                "segmento_atual":
                    id_atual,

                "segmentos": [
                    id_anterior,
                    id_atual,
                ],

                "ponto": {
                    "x": x,
                    "y": y,
                },

                "ponto_dobra": {
                    "x_mm": x,
                    "y_mm": y,
                },

                "angulo_graus":
                    round(
                        angulo,
                        4,
                    ),

                "classificacao":
                    classificacao,

                "confianca":
                    confianca,

                "tipo_segmento_anterior":
                    _tipo_segmento(
                        segmento_anterior
                    ),

                "tipo_segmento_atual":
                    _tipo_segmento(
                        segmento_atual
                    ),

                "comprimento_segmento_anterior_mm":
                    round(
                        comprimento_anterior,
                        4,
                    ),

                "comprimento_segmento_atual_mm":
                    round(
                        comprimento_atual,
                        4,
                    ),

                "distancia_conexao_mm":
                    transicao.get(
                        "distancia_conexao_mm"
                    ),

                "raio_mm":
                    None,

                "origem_raio":
                    "NAO_DETERMINADO",
            }
        )

    return candidatas


# =============================================================================
# ASSOCIAÇÃO COM ARCOS
# =============================================================================

def associar_arcos(
    candidatas: List[Dict[str, Any]],
    arcos: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not candidatas:

        return []

    if not arcos:

        return candidatas

    resultado = []

    for candidata in candidatas:

        nova = dict(
            candidata
        )

        nova[
            "raios_disponiveis"
        ] = [
            arco.get(
                "raio_mm"
            )
            for arco in arcos
        ]

        resultado.append(
            nova
        )

    return resultado


# =============================================================================
# AGRUPAMENTO / REMOÇÃO DE DUPLICIDADES
# =============================================================================

def agrupar_candidatas(
    candidatas: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    if not candidatas:

        return []

    resultado = []

    for candidata in candidatas:

        ponto = candidata.get(
            "ponto_dobra",
            {}
        )

        x = _numero(
            ponto.get(
                "x_mm"
            )
        )

        y = _numero(
            ponto.get(
                "y_mm"
            )
        )

        segmentos_candidata = set(
            candidata.get(
                "segmentos",
                []
            )
        )

        duplicada = False

        for existente in resultado:

            ponto_existente = existente.get(
                "ponto_dobra",
                {}
            )

            xe = _numero(
                ponto_existente.get(
                    "x_mm"
                )
            )

            ye = _numero(
                ponto_existente.get(
                    "y_mm"
                )
            )

            segmentos_existente = set(
                existente.get(
                    "segmentos",
                    []
                )
            )

            mesmos_segmentos = (
                segmentos_candidata
                == segmentos_existente
            )

            mesma_posicao = False

            if (
                x is not None
                and y is not None
                and xe is not None
                and ye is not None
            ):

                distancia = math.hypot(
                    x - xe,
                    y - ye,
                )

                mesma_posicao = (
                    distancia
                    <= TOLERANCIA_COLINEARIDADE_MM
                )

            if (
                mesmos_segmentos
                or mesma_posicao
            ):

                duplicada = True
                break

        if not duplicada:

            resultado.append(
                candidata
            )

    return resultado


# =============================================================================
# STATUS
# =============================================================================

def classificar_resultado(
    segmentos: List[Dict[str, Any]],
    arcos: List[Dict[str, Any]],
    candidatas: List[Dict[str, Any]],
) -> str:

    if not segmentos:

        return "GEOMETRIA_SEM_SEGMENTOS"

    if candidatas:

        if arcos:

            return (
                "DOBRAS_CANDIDATAS_COM_GEOMETRIA_DE_ARCO"
            )

        return (
            "DOBRAS_CANDIDATAS_SEM_ARCOS_EXPLICITOS"
        )

    return (
        "NENHUMA_DOBRA_GEOMETRICA_IDENTIFICADA"
    )


# =============================================================================
# EXTRAÇÃO ROBUSTA DA GEOMETRIA
# =============================================================================

def _extrair_geometria(
    estrutura: Dict[str, Any],
) -> Tuple[
    Dict[str, Any],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
]:
    """
    Aceita:

        {
            "geometria": {
                "segmentos": [...],
                "arcos": [...]
            }
        }

    ou:

        {
            "segmentos": [...],
            "arcos": [...]
        }

    ou estruturas em que a geometria esteja dentro de
    campos auxiliares conhecidos.
    """

    if not isinstance(
        estrutura,
        dict,
    ):

        return {}, [], []

    # -------------------------------------------------------------------------
    # Caso 1 - estrutura["geometria"]
    # -------------------------------------------------------------------------

    geometria = estrutura.get(
        "geometria"
    )

    if isinstance(
        geometria,
        dict,
    ):

        segmentos = geometria.get(
            "segmentos",
            []
        )

        arcos = geometria.get(
            "arcos",
            []
        )

        if (
            isinstance(segmentos, list)
            or isinstance(arcos, list)
        ):

            if not isinstance(
                segmentos,
                list,
            ):

                segmentos = []

            if not isinstance(
                arcos,
                list,
            ):

                arcos = []

            return (
                geometria,
                segmentos,
                arcos,
            )

    # -------------------------------------------------------------------------
    # Caso 2 - estrutura já é a geometria
    # -------------------------------------------------------------------------

    segmentos = estrutura.get(
        "segmentos",
        []
    )

    arcos = estrutura.get(
        "arcos",
        []
    )

    if (
        isinstance(segmentos, list)
        or isinstance(arcos, list)
    ):

        if not isinstance(
            segmentos,
            list,
        ):

            segmentos = []

        if not isinstance(
            arcos,
            list,
        ):

            arcos = []

        return (
            estrutura,
            segmentos,
            arcos,
        )

    # -------------------------------------------------------------------------
    # Caso 3 - campos auxiliares
    # -------------------------------------------------------------------------

    for chave in (
        "geometria_interpretada",
        "resultado_geometria",
        "dados_geometria",
    ):

        candidata = estrutura.get(
            chave
        )

        if not isinstance(
            candidata,
            dict,
        ):

            continue

        segmentos = candidata.get(
            "segmentos",
            []
        )

        arcos = candidata.get(
            "arcos",
            []
        )

        if (
            isinstance(segmentos, list)
            or isinstance(arcos, list)
        ):

            if not isinstance(
                segmentos,
                list,
            ):

                segmentos = []

            if not isinstance(
                arcos,
                list,
            ):

                arcos = []

            return (
                candidata,
                segmentos,
                arcos,
            )

    return {}, [], []


# =============================================================================
# ANÁLISE PRINCIPAL
# =============================================================================

def analisar_dobras(
    estrutura: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Executa a análise completa da geometria.

    Não altera a geometria original.

    REGRA:
    -------
    Segmentos menores que COMPRIMENTO_MINIMO_SEGMENTO_DOBRA_MM
    não podem gerar candidatas de dobra.
    """

    if not estrutura:

        return {
            "tipo":
                "ANALISE_DOBRAS",

            "status":
                "DADOS_AUSENTES",

            "quantidade_segmentos":
                0,

            "quantidade_arcos":
                0,

            "quantidade_segmentos_curtos":
                0,

            "quantidade_transicoes":
                0,

            "transicoes_analisadas":
                0,

            "quantidade_candidatas":
                0,

            "quantidade_dobras":
                0,

            "segmentos_curtos":
                [],

            "transicoes":
                [],

            "dobras":
                [],

            "candidatas":
                [],
        }

    (
        geometria,
        segmentos,
        arcos,
    ) = _extrair_geometria(
        estrutura
    )

    # -------------------------------------------------------------------------
    # Segmentos curtos
    # -------------------------------------------------------------------------

    segmentos_curtos = (
        identificar_segmentos_curto(
            segmentos
        )
    )

    # -------------------------------------------------------------------------
    # Transições
    #
    # As transições continuam sendo analisadas para diagnóstico.
    # Porém, transições com segmentos curtos são marcadas como
    # SEGMENTO_CURTO_SEM_DOBRA e não geram candidatas.
    # -------------------------------------------------------------------------

    transicoes = analisar_transicoes(
        segmentos
    )

    # -------------------------------------------------------------------------
    # Candidatas
    # -------------------------------------------------------------------------

    candidatas = detectar_candidatas_dobra(
        segmentos,
        transicoes,
    )

    # -------------------------------------------------------------------------
    # Arcos
    # -------------------------------------------------------------------------

    candidatas = associar_arcos(
        candidatas,
        arcos,
    )

    # -------------------------------------------------------------------------
    # Remover duplicidades
    # -------------------------------------------------------------------------

    candidatas = agrupar_candidatas(
        candidatas
    )

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    status = classificar_resultado(
        segmentos,
        arcos,
        candidatas,
    )

    return {
        "tipo":
            "ANALISE_DOBRAS",

        "status":
            status,

        "quantidade_segmentos":
            len(
                segmentos
            ),

        "quantidade_arcos":
            len(
                arcos
            ),

        "quantidade_segmentos_curtos":
            len(
                segmentos_curtos
            ),

        "segmentos_curtos":
            segmentos_curtos,

        "quantidade_transicoes":
            len(
                transicoes
            ),

        # Compatibilidade com testes que usam
        # "transicoes_analisadas".
        "transicoes_analisadas":
            len(
                transicoes
            ),

        "transicoes":
            transicoes,

        "quantidade_candidatas":
            len(
                candidatas
            ),

        "quantidade_dobras":
            len(
                candidatas
            ),

        # Contrato oficial com ConsolidadorDobras
        "dobras":
            candidatas,

        # Compatibilidade
        "candidatas":
            candidatas,

        "observacoes": [
            (
                "As conexões são determinadas geometricamente "
                "e não dependem da ordem dos segmentos no JSON."
            ),
            (
                "Segmentos curtos não geram candidatas de dobra."
            ),
            (
                "Candidatas geométricas não representam "
                "automaticamente dobras confirmadas."
            ),
            (
                "A ausência de arcos não impede a identificação "
                "de uma candidata angular."
            ),
            (
                "O cálculo do BLANK depende da interpretação "
                "posterior da geometria de fabricação."
            ),
            (
                "Este módulo não calcula BLANK nem desenvolvimento."
            ),
        ],
    }


# =============================================================================
# VALIDAÇÃO
# =============================================================================

def validar_analise(
    resultado: Dict[str, Any],
) -> Dict[str, Any]:

    erros = []

    if not isinstance(
        resultado,
        dict,
    ):

        return {
            "valido":
                False,

            "erros": [
                "Resultado não é um dicionário."
            ],
        }

    campos_obrigatorios = [
        "status",
        "quantidade_candidatas",
        "dobras",
        "transicoes",
    ]

    for campo in campos_obrigatorios:

        if campo not in resultado:

            erros.append(
                f"Campo ausente: {campo}"
            )

    dobras = resultado.get(
        "dobras",
        []
    )

    if not isinstance(
        dobras,
        list,
    ):

        erros.append(
            "Campo 'dobras' não é uma lista."
        )

    quantidade = resultado.get(
        "quantidade_candidatas"
    )

    if isinstance(
        quantidade,
        int,
    ):

        if quantidade != len(
            dobras
        ):

            erros.append(
                "Quantidade de candidatas "
                "não corresponde à lista de dobras."
            )

    else:

        erros.append(
            "Quantidade de candidatas inválida."
        )

    transicoes = resultado.get(
        "transicoes",
        []
    )

    if not isinstance(
        transicoes,
        list,
    ):

        erros.append(
            "Campo 'transicoes' não é uma lista."
        )

    return {
        "valido":
            len(erros) == 0,

        "erros":
            erros,
    }


# =============================================================================
# RESUMO
# =============================================================================

def gerar_resumo(
    resultado: Dict[str, Any],
) -> Dict[str, Any]:

    if not resultado:

        return {
            "status":
                "SEM_RESULTADO",

            "dobras":
                0,
        }

    dobras = resultado.get(
        "dobras",
        []
    )

    quantidade_90 = 0

    quantidade_angulares = 0

    for dobra in dobras:

        classificacao = str(
            dobra.get(
                "classificacao",
                ""
            )
        )

        if (
            classificacao
            == "CANDIDATA_DOBRA_90_GRAUS"
        ):

            quantidade_90 += 1

        elif (
            classificacao
            == "CANDIDATA_DOBRA_ANGULAR"
        ):

            quantidade_angulares += 1

    return {
        "status":
            resultado.get(
                "status"
            ),

        "dobras_candidatas":
            len(
                dobras
            ),

        "dobras_90_graus":
            quantidade_90,

        "dobras_angulares":
            quantidade_angulares,

        "transicoes":
            resultado.get(
                "quantidade_transicoes",
                0,
            ),

        "arcos_disponiveis":
            resultado.get(
                "quantidade_arcos",
                0,
            ),

        "segmentos_curtos":
            resultado.get(
                "quantidade_segmentos_curtos",
                0,
            ),
    }


# =============================================================================
# IMPRESSÃO
# =============================================================================

def imprimir_resumo(
    resultado: Dict[str, Any],
) -> None:

    print()
    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("ANÁLISE DE DOBRAS")
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
        f"Transições analisadas: "
        f"{resultado.get('quantidade_transicoes', 0)}"
    )

    print(
        f"Candidatas a dobra: "
        f"{resultado.get('quantidade_candidatas', 0)}"
    )

    print()

    print("=" * 80)
    print("TRANSIÇÕES GEOMÉTRICAS")
    print("=" * 80)

    transicoes = resultado.get(
        "transicoes",
        []
    )

    if not transicoes:

        print()
        print(
            "Nenhuma conexão geométrica encontrada."
        )

    else:

        for transicao in transicoes:

            print()

            print(
                f"Transição "
                f"{transicao.get('indice')}"
            )

            print(
                f"  Segmentos: "
                f"{transicao.get('segmento_anterior')} "
                f"-> "
                f"{transicao.get('segmento_atual')}"
            )

            print(
                f"  Conexão: "
                f"{transicao.get('distancia_conexao_mm')} mm"
            )

            print(
                f"  Ângulo: "
                f"{transicao.get('angulo_mudanca_graus')}°"
            )

            print(
                f"  Classificação: "
                f"{transicao.get('classificacao')}"
            )

            print(
                f"  Segmentos relevantes: "
                f"{transicao.get('segmentos_relevantes')}"
            )

    print()

    print("=" * 80)
    print("CANDIDATAS A DOBRA")
    print("=" * 80)

    dobras = resultado.get(
        "dobras",
        []
    )

    if not dobras:

        print()
        print(
            "Nenhuma candidata geométrica "
            "a dobra foi identificada."
        )

    else:

        for indice, dobra in enumerate(
            dobras,
            start=1,
        ):

            ponto = dobra.get(
                "ponto_dobra",
                {}
            )

            print()

            print(
                f"Dobra candidata {indice}"
            )

            print(
                f"  Segmentos: "
                f"{dobra.get('segmento_anterior')} "
                f"-> "
                f"{dobra.get('segmento_atual')}"
            )

            print(
                f"  Ângulo: "
                f"{dobra.get('angulo_graus')}°"
            )

            print(
                f"  Classificação: "
                f"{dobra.get('classificacao')}"
            )

            print(
                f"  Confiança: "
                f"{dobra.get('confianca')}"
            )

            print(
                f"  Ponto: "
                f"({ponto.get('x_mm')}, "
                f"{ponto.get('y_mm')}) mm"
            )

            print(
                f"  Raio: "
                f"{dobra.get('raio_mm')}"
            )

    print()

    print("=" * 80)
    print("VALIDAÇÃO DE SEGURANÇA")
    print("=" * 80)

    print(
        "BLANK calculado: False"
    )

    print(
        "Desenvolvimento calculado: False"
    )

    print(
        "Raio inventado: False"
    )

    print(
        "Dobra confirmada automaticamente: False"
    )

    print(
        "CalculadoraCorte chamada: False"
    )

    print()

    print(
        "OK - Analisador permanece conservador."
    )


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("ANALISADOR DE DOBRAS")
    print("=" * 80)

    print()

    print(
        "Este módulo recebe a estrutura produzida pelo"
    )

    print(
        "interpretador_geometria.interpretar_geometria()."
    )

    print()

    print(
        "Não foi executada uma análise automática porque"
    )

    print(
        "nenhuma geometria foi fornecida diretamente."
    )