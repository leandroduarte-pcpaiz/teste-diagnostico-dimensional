from pathlib import Path
import json
import math


# =============================================================================
# AIZI ENGINEERING AI
# EXTRATOR DIMENSIONAL
#
# Entrada:
#     *_geometria.json
#
# SaÃ­da:
#     *_geometria_dimensional.json
#
# OBJETIVO
# =============================================================================
#
# Transformar a geometria identificada pelo diagnÃ³stico em informaÃ§Ãµes
# dimensionais Ãºteis para engenharia e fabricaÃ§Ã£o.
#
# IMPORTANTE:
#
#     DIMENSÃƒO GEOMÃ‰TRICA != DIMENSÃƒO DE CORTE
#
# Este mÃ³dulo NÃƒO calcula o blank definitivo.
#
# Ele prepara os dados para:
#
#     calculadora_desenvolvimento.py
#
# e posteriormente:
#
#     calculadora_corte.py
#
# =============================================================================


# =============================================================================
# CONFIGURAÃ‡ÃƒO
# =============================================================================

PASTA_DIAGNOSTICO = Path(
    r"C:\Projetos\AIZI Engineering AI\diagnostico"
)

TOLERANCIA_PONTO = 0.01
TOLERANCIA_ANGULO = 2.0
TOLERANCIA_RAIO = 1.50


# =============================================================================
# FUNÃ‡Ã•ES BÃSICAS
# =============================================================================

def numero(valor, padrao=None):
    """
    Converte um valor para float com seguranÃ§a.
    """

    if valor is None:
        return padrao

    if isinstance(valor, (int, float)):
        return float(valor)

    try:
        texto = str(valor).strip()

        if not texto:
            return padrao

        texto = texto.replace(",", ".")

        return float(texto)

    except (TypeError, ValueError):
        return padrao


def texto(valor, padrao=None):
    """
    Converte valor para texto.
    """

    if valor is None:
        return padrao

    valor = str(valor).strip()

    if not valor:
        return padrao

    return valor


def distancia(p1, p2):
    """
    DistÃ¢ncia entre dois pontos.
    """

    return math.hypot(
        p2[0] - p1[0],
        p2[1] - p1[1],
    )


def ponto_quase_igual(
    p1,
    p2,
    tolerancia=TOLERANCIA_PONTO,
):
    return distancia(p1, p2) <= tolerancia


# =============================================================================
# Ã‚NGULOS
# =============================================================================

def calcular_angulo(p1, p2, p3):
    """
    Calcula o Ã¢ngulo interno formado por:

        p1 -> p2 -> p3
    """

    v1 = (
        p1[0] - p2[0],
        p1[1] - p2[1],
    )

    v2 = (
        p3[0] - p2[0],
        p3[1] - p2[1],
    )

    norma1 = math.hypot(
        v1[0],
        v1[1],
    )

    norma2 = math.hypot(
        v2[0],
        v2[1],
    )

    if norma1 <= 1e-9 or norma2 <= 1e-9:
        return None

    produto = (
        v1[0] * v2[0]
        + v1[1] * v2[1]
    )

    coseno = produto / (
        norma1 * norma2
    )

    coseno = max(
        -1.0,
        min(
            1.0,
            coseno,
        ),
    )

    return math.degrees(
        math.acos(coseno)
    )


def normalizar_angulo(angulo):
    """
    Normaliza Ã¢ngulos conhecidos.
    """

    if angulo is None:
        return None

    if abs(angulo - 90.0) <= TOLERANCIA_ANGULO:
        return 90.0

    if abs(angulo - 45.0) <= TOLERANCIA_ANGULO:
        return 45.0

    if abs(angulo - 30.0) <= TOLERANCIA_ANGULO:
        return 30.0

    if abs(angulo - 60.0) <= TOLERANCIA_ANGULO:
        return 60.0

    if abs(angulo - 180.0) <= TOLERANCIA_ANGULO:
        return 180.0

    return round(
        angulo,
        4,
    )


# =============================================================================
# LOCALIZAÃ‡ÃƒO DO JSON
# =============================================================================

def localizar_json():
    """
    Localiza o *_geometria.json mais recente.

    Importante:
    NÃ£o pega *_geometria_dimensional.json.
    """

    arquivos = []

    for arquivo in PASTA_DIAGNOSTICO.glob(
        "*_geometria.json"
    ):

        if arquivo.name.endswith(
            "_geometria_dimensional.json"
        ):
            continue

        arquivos.append(
            arquivo
        )

    arquivos = sorted(
        arquivos,
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not arquivos:
        return None

    return arquivos[0]


# =============================================================================
# CARREGAMENTO
# =============================================================================

def carregar_geometria(caminho):

    with open(
        caminho,
        "r",
        encoding="utf-8",
    ) as arquivo:

        return json.load(
            arquivo
        )


# =============================================================================
# VÃ‰RTICES
# =============================================================================

def extrair_vertices(geometria):

    vertices = []

    lista = geometria.get(
        "vertices_mm",
        []
    )

    if not lista:

        lista = geometria.get(
            "vertices",
            []
        )

    for item in lista:

        if isinstance(
            item,
            dict,
        ):

            x = numero(
                item.get(
                    "x_mm",
                    item.get("x")
                )
            )

            y = numero(
                item.get(
                    "y_mm",
                    item.get("y")
                )
            )

        elif isinstance(
            item,
            (list, tuple),
        ):

            if len(item) < 2:
                continue

            x = numero(
                item[0]
            )

            y = numero(
                item[1]
            )

        else:

            continue

        if x is None or y is None:
            continue

        vertices.append(
            (
                x,
                y,
            )
        )

    return vertices


# =============================================================================
# DIMENSÃ•ES EXTREMAS
# =============================================================================

def calcular_dimensoes(vertices):

    if not vertices:
        return None

    xs = [
        p[0]
        for p in vertices
    ]

    ys = [
        p[1]
        for p in vertices
    ]

    x_min = min(xs)
    x_max = max(xs)

    y_min = min(ys)
    y_max = max(ys)

    largura = x_max - x_min
    altura = y_max - y_min

    proporcao = None

    if (
        largura > 0
        and altura > 0
    ):

        proporcao = (
            max(
                largura,
                altura,
            )
            /
            min(
                largura,
                altura,
            )
        )

    return {
        "x_min_mm": round(
            x_min,
            4,
        ),
        "x_max_mm": round(
            x_max,
            4,
        ),
        "y_min_mm": round(
            y_min,
            4,
        ),
        "y_max_mm": round(
            y_max,
            4,
        ),
        "largura_mm": round(
            largura,
            4,
        ),
        "altura_mm": round(
            altura,
            4,
        ),
        "proporcao": round(
            proporcao,
            4,
        )
        if proporcao is not None
        else None,
    }


# =============================================================================
# SEGMENTOS
# =============================================================================

def extrair_segmentos(vertices):

    segmentos = []

    if len(vertices) < 2:
        return segmentos

    for i in range(
        len(vertices) - 1
    ):

        p1 = vertices[i]
        p2 = vertices[i + 1]

        comprimento = distancia(
            p1,
            p2,
        )

        if comprimento <= TOLERANCIA_PONTO:
            continue

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        angulo = math.degrees(
            math.atan2(
                dy,
                dx,
            )
        )

        if angulo < 0:
            angulo += 180.0

        horizontal = (
            abs(dy)
            <= TOLERANCIA_PONTO
        )

        vertical = (
            abs(dx)
            <= TOLERANCIA_PONTO
        )

        if horizontal:

            orientacao = "horizontal"

        elif vertical:

            orientacao = "vertical"

        else:

            orientacao = "inclinada"

        segmentos.append(
            {
                "numero": i + 1,

                "inicio": {
                    "x_mm": round(
                        p1[0],
                        4,
                    ),
                    "y_mm": round(
                        p1[1],
                        4,
                    ),
                },

                "fim": {
                    "x_mm": round(
                        p2[0],
                        4,
                    ),
                    "y_mm": round(
                        p2[1],
                        4,
                    ),
                },

                "comprimento_mm": round(
                    comprimento,
                    4,
                ),

                "angulo_graus": round(
                    angulo,
                    4,
                ),

                "orientacao": orientacao,
            }
        )

    return segmentos


# =============================================================================
# RESUMO DOS SEGMENTOS
# =============================================================================

def resumir_segmentos(segmentos):

    horizontais = []
    verticais = []
    inclinados = []

    for segmento in segmentos:

        orientacao = segmento[
            "orientacao"
        ]

        if orientacao == "horizontal":

            horizontais.append(
                segmento
            )

        elif orientacao == "vertical":

            verticais.append(
                segmento
            )

        else:

            inclinados.append(
                segmento
            )

    comprimentos = [
        s["comprimento_mm"]
        for s in segmentos
    ]

    return {
        "quantidade_total": len(
            segmentos
        ),

        "horizontais": len(
            horizontais
        ),

        "verticais": len(
            verticais
        ),

        "inclinados": len(
            inclinados
        ),

        "comprimento_total_mm": round(
            sum(comprimentos),
            4,
        ),

        "maior_segmento_mm": round(
            max(
                comprimentos,
                default=0.0,
            ),
            4,
        ),

        "menor_segmento_mm": round(
            min(
                comprimentos,
                default=0.0,
            ),
            4,
        ),
    }


# =============================================================================
# Ã‚NGULOS DOS VÃ‰RTICES
# =============================================================================

def extrair_angulos(vertices):

    angulos = []

    if len(vertices) < 3:
        return angulos

    quantidade = len(vertices) - 1

    for i in range(
        1,
        quantidade,
    ):

        p1 = vertices[i - 1]
        p2 = vertices[i]
        p3 = vertices[i + 1]

        angulo = calcular_angulo(
            p1,
            p2,
            p3,
        )

        if angulo is None:
            continue

        angulo_normalizado = (
            normalizar_angulo(
                angulo
            )
        )

        angulos.append(
            {
                "vertice": i + 1,

                "x_mm": round(
                    p2[0],
                    4,
                ),

                "y_mm": round(
                    p2[1],
                    4,
                ),

                "angulo_graus": round(
                    angulo,
                    4,
                ),

                "angulo_normalizado_graus":
                    angulo_normalizado,
            }
        )

    return angulos


# =============================================================================
# RESUMO DOS Ã‚NGULOS
# =============================================================================

def resumir_angulos(angulos):

    contador_90 = 0
    contador_45 = 0
    contador_30 = 0
    contador_60 = 0
    contador_outros = 0

    for item in angulos:

        valor = item[
            "angulo_normalizado_graus"
        ]

        if valor == 90.0:

            contador_90 += 1

        elif valor == 45.0:

            contador_45 += 1

        elif valor == 30.0:

            contador_30 += 1

        elif valor == 60.0:

            contador_60 += 1

        else:

            contador_outros += 1

    return {
        "quantidade_vertices_analisados":
            len(angulos),

        "angulos_90_graus":
            contador_90,

        "angulos_45_graus":
            contador_45,

        "angulos_30_graus":
            contador_30,

        "angulos_60_graus":
            contador_60,

        "outros_angulos":
            contador_outros,
    }


# =============================================================================
# CURVAS
# =============================================================================

def extrair_curvas(geometria):

    curvas = []

    lista = geometria.get(
        "curvas_reais",
        []
    )

    if not lista:

        lista = geometria.get(
            "curvas",
            []
        )

    for curva in lista:

        if not isinstance(
            curva,
            dict,
        ):
            continue

        raio = numero(
            curva.get(
                "raio_mm",
                curva.get(
                    "raio"
                )
            )
        )

        erro = numero(
            curva.get(
                "erro_maximo_mm",
                curva.get(
                    "erro_maximo"
                )
            )
        )

        curvas.append(
            {
                "indice_geometria":
                    curva.get(
                        "indice_geometria"
                    ),

                "classificacao":
                    curva.get(
                        "classificacao"
                    ),

                "raio_mm":
                    raio,

                "erro_maximo_mm":
                    erro,

                "quantidade_pontos":
                    curva.get(
                        "pontos"
                    ),

                "inicio":
                    curva.get(
                        "ponto_inicio"
                    ),

                "fim":
                    curva.get(
                        "ponto_fim"
                    ),
            }
        )

    return curvas


# =============================================================================
# EXTRAÃ‡ÃƒO DO MATERIAL
# =============================================================================

def extrair_material(geometria):
    """
    Procura material em vÃ¡rios locais possÃ­veis do diagnÃ³stico.

    NÃ£o cria material por inferÃªncia.
    """

    candidatos = [

        geometria.get(
            "material"
        ),

        geometria.get(
            "material_descricao"
        ),

        geometria.get(
            "descricao_material"
        ),

        geometria.get(
            "materia_prima"
        ),

        geometria.get(
            "material_materia_prima"
        ),
    ]

    fabricacao = geometria.get(
        "fabricacao",
        {}
    )

    if isinstance(
        fabricacao,
        dict,
    ):

        candidatos.extend(
            [
                fabricacao.get(
                    "material"
                ),
                fabricacao.get(
                    "material_descricao"
                ),
                fabricacao.get(
                    "materia_prima"
                ),
            ]
        )

    identificacao = geometria.get(
        "identificacao",
        {}
    )

    if isinstance(
        identificacao,
        dict,
    ):

        candidatos.extend(
            [
                identificacao.get(
                    "material"
                ),
                identificacao.get(
                    "material_descricao"
                ),
            ]
        )

    for candidato in candidatos:

        valor = texto(
            candidato
        )

        if valor:
            return valor

    return None


# =============================================================================
# EXTRAÃ‡ÃƒO DA ESPESSURA
# =============================================================================

def extrair_espessura(geometria):
    """
    Procura espessura em vÃ¡rios locais possÃ­veis.
    """

    candidatos = [

        geometria.get(
            "espessura_mm"
        ),

        geometria.get(
            "espessura"
        ),

        geometria.get(
            "thickness_mm"
        ),

        geometria.get(
            "thickness"
        ),
    ]

    fabricacao = geometria.get(
        "fabricacao",
        {}
    )

    if isinstance(
        fabricacao,
        dict,
    ):

        candidatos.extend(
            [
                fabricacao.get(
                    "espessura_mm"
                ),

                fabricacao.get(
                    "espessura"
                ),

                fabricacao.get(
                    "thickness_mm"
                ),

                fabricacao.get(
                    "thickness"
                ),
            ]
        )

    identificacao = geometria.get(
        "identificacao",
        {}
    )

    if isinstance(
        identificacao,
        dict,
    ):

        candidatos.extend(
            [
                identificacao.get(
                    "espessura_mm"
                ),

                identificacao.get(
                    "espessura"
                ),
            ]
        )

    for candidato in candidatos:

        valor = numero(
            candidato
        )

        if valor is not None:

            if valor > 0:

                return valor

    return None


# =============================================================================
# EXTRAÃ‡ÃƒO DO RAIO
# =============================================================================

def extrair_raio(geometria, curvas):
    """
    Procura o raio interno jÃ¡ identificado.

    Se houver uma curva real com raio compatÃ­vel, ela pode ser usada
    como evidÃªncia de raio.

    NÃƒO assume R10 apenas porque a peÃ§a possui dobra.
    """

    candidatos = [

        geometria.get(
            "raio_interno_mm"
        ),

        geometria.get(
            "raio_mm"
        ),

        geometria.get(
            "raio_interno"
        ),

        geometria.get(
            "raio"
        ),
    ]

    fabricacao = geometria.get(
        "fabricacao",
        {}
    )

    if isinstance(
        fabricacao,
        dict,
    ):

        candidatos.extend(
            [
                fabricacao.get(
                    "raio_interno_mm"
                ),

                fabricacao.get(
                    "raio_mm"
                ),

                fabricacao.get(
                    "raio_interno"
                ),

                fabricacao.get(
                    "raio"
                ),
            ]
        )

    for candidato in candidatos:

        valor = numero(
            candidato
        )

        if valor is not None:

            if valor > 0:

                return valor

    # -------------------------------------------------------------------------
    # Caso nÃ£o exista raio declarado, procura nas curvas reais.
    # -------------------------------------------------------------------------

    raios = []

    for curva in curvas:

        raio = numero(
            curva.get(
                "raio_mm"
            )
        )

        if raio is not None:

            if raio > 0:

                raios.append(
                    raio
                )

    if raios:

        # Se houver vÃ¡rios raios reais, nÃ£o escolhemos arbitrariamente.
        # Utilizamos o menor apenas como referÃªncia detectada.
        return min(
            raios
        )

    return None


# =============================================================================
# IDENTIFICAÃ‡ÃƒO DE CARACTERÃSTICAS
# =============================================================================

def detectar_caracteristicas(
    dimensoes,
    segmentos,
    curvas,
    angulos,
):

    caracteristicas = []

    if not dimensoes:
        return caracteristicas

    largura = dimensoes[
        "largura_mm"
    ]

    altura = dimensoes[
        "altura_mm"
    ]

    if (
        largura > 0
        and altura > 0
    ):

        proporcao = (
            max(
                largura,
                altura,
            )
            /
            min(
                largura,
                altura,
            )
        )

        if proporcao >= 3.0:

            caracteristicas.append(
                "GEOMETRIA_ALONGADA"
            )

    if segmentos:

        if any(
            s["orientacao"]
            == "inclinada"
            for s in segmentos
        ):

            caracteristicas.append(
                "SEGMENTOS_INCLINADOS"
            )

    if curvas:

        caracteristicas.append(
            "POSSUI_CURVAS"
        )

        raios = [
            c["raio_mm"]
            for c in curvas
            if c["raio_mm"] is not None
        ]

        if raios:

            if any(
                abs(
                    r - 10.0
                )
                <= TOLERANCIA_RAIO
                for r in raios
            ):

                caracteristicas.append(
                    "POSSUI_R10"
                )

    if angulos:

        if any(
            a[
                "angulo_normalizado_graus"
            ] == 90.0
            for a in angulos
        ):

            caracteristicas.append(
                "ANGULOS_90_GRAUS"
            )

    return caracteristicas


# =============================================================================
# CLASSIFICAÃ‡ÃƒO
# =============================================================================

def classificar_geometria(
    dimensoes,
    segmentos_resumo,
    angulos_resumo,
    curvas,
):

    if not dimensoes:
        return "SEM_GEOMETRIA"

    largura = dimensoes[
        "largura_mm"
    ]

    altura = dimensoes[
        "altura_mm"
    ]

    if (
        len(curvas) > 0
        and segmentos_resumo[
            "inclinados"
        ] > 0
    ):

        return (
            "PERFIL_COM_CURVAS_E_INCLINACOES"
        )

    if len(curvas) > 0:

        return (
            "PERFIL_COM_CURVAS"
        )

    if (
        angulos_resumo[
            "angulos_90_graus"
        ] >= 2
        and segmentos_resumo[
            "quantidade_total"
        ] >= 4
    ):

        return "PERFIL_POLIGONAL"

    if (
        largura > 3 * max(
            altura,
            0.001,
        )
    ):

        return "PERFIL_ALONGADO"

    if (
        altura > 3 * max(
            largura,
            0.001,
        )
    ):

        return "PERFIL_ALONGADO"

    return "PERFIL_GERAL"



# =============================================================================
# POSSÃVEIS DOBRAS
# =============================================================================

def identificar_possiveis_dobras(
    angulos,
    segmentos=None,
    geometria=None,
):
    """
    Identifica possÃ­veis linhas de dobra.

    REGRA DE ENGENHARIA
    -------------------
    Um Ã¢ngulo de 90Â° NÃƒO Ã© suficiente para afirmar que existe uma dobra.

    O contorno de uma peÃ§a pode possuir diversos vÃ©rtices de 90Â° que sÃ£o
    simplesmente cantos geomÃ©tricos.

    Portanto:

    1. Procura primeiro evidÃªncias explÃ­citas de dobra no diagnÃ³stico;
    2. Caso existam linhas de dobra explÃ­citas, utiliza essas informaÃ§Ãµes;
    3. Caso nÃ£o existam, NÃƒO promove automaticamente todos os 90Â° a dobras;
    4. MantÃ©m a informaÃ§Ã£o dos 90Â° como evidÃªncia geomÃ©trica.

    A confirmaÃ§Ã£o definitiva continua sendo responsabilidade da etapa
    de validaÃ§Ã£o da geometria.
    """

    dobras = []

    geometria = (
        geometria
        if isinstance(geometria, dict)
        else {}
    )

    # -------------------------------------------------------------------------
    # 1. EVIDÃŠNCIAS EXPLÃCITAS DE DOBRA
    # -------------------------------------------------------------------------

    candidatos = [
        geometria.get(
            "linhas_dobra"
        ),

        geometria.get(
            "linhas_de_dobra"
        ),

        geometria.get(
            "dobras"
        ),

        geometria.get(
            "dobras_identificadas"
        ),

        geometria.get(
            "linhas_dobra_identificadas"
        ),
    ]

    evidencias = []

    for candidato in candidatos:

        if not isinstance(
            candidato,
            list,
        ):
            continue

        for item in candidato:

            if isinstance(
                item,
                dict,
            ):

                evidencias.append(
                    item
                )

    # -------------------------------------------------------------------------
    # 2. SE EXISTIR LINHA DE DOBRA EXPLÃCITA
    # -------------------------------------------------------------------------

    if evidencias:

        for indice, evidencia in enumerate(
            evidencias,
            start=1,
        ):

            x = numero(
                evidencia.get(
                    "x_mm"
                )
            )

            y = numero(
                evidencia.get(
                    "y_mm"
                )
            )

            angulo = numero(
                evidencia.get(
                    "angulo_graus",
                    evidencia.get(
                        "angulo"
                    )
                )
            )

            raio = numero(
                evidencia.get(
                    "raio_mm",
                    evidencia.get(
                        "raio"
                    )
                )
            )

            dobras.append(
                {
                    "indice": indice,

                    "vertice":
                        evidencia.get(
                            "vertice"
                        ),

                    "x_mm": x,

                    "y_mm": y,

                    "angulo_graus":
                        angulo,

                    "raio_mm":
                        raio,

                    "status":
                        "POSSIVEL_DOBRA",

                    "origem":
                        "DIAGNOSTICO_EXPLICITO",
                }
            )

        return dobras

    # -------------------------------------------------------------------------
    # 3. SEM EVIDÃŠNCIA EXPLÃCITA
    # -------------------------------------------------------------------------
    #
    # NÃƒO transformar automaticamente todos os 90Â° em dobras.
    #
    # Os Ã¢ngulos continuam disponÃ­veis em:
    #
    #     resultado["angulos"]
    #
    # e podem ser utilizados posteriormente pelo mÃ³dulo de desenvolvimento.
    #
    # -------------------------------------------------------------------------

    return []
    """
    NÃƒO promove automaticamente uma possÃ­vel dobra para confirmada.

    SÃ³ considera confirmadas se o diagnÃ³stico original possuir explicitamente
    uma lista de linhas/dobras confirmadas.
    """

    candidatos = [

        geometria.get(
            "dobras_confirmadas"
        ),

        geometria.get(
            "linhas_dobra_confirmadas"
        ),

        geometria.get(
            "linhas_de_dobra_confirmadas"
        ),
    ]

    for candidato in candidatos:

        if not isinstance(
            candidato,
            list,
        ):
            continue

        resultado = []

        for item in candidato:

            if not isinstance(
                item,
                dict,
            ):
                continue

            resultado.append(
                item
            )

        if resultado:

            return resultado

    return []

# =============================================================================
# DOBRAS CONFIRMADAS
# =============================================================================

def identificar_dobras_confirmadas(
    geometria,
    possiveis_dobras,
):
    """
    Retorna somente as dobras explicitamente confirmadas
    pelo diagnóstico original.

    Uma dobra apenas possível NÃO é promovida automaticamente
    para confirmada.
    """

    candidatos = [

        geometria.get(
            "dobras_confirmadas"
        ),

        geometria.get(
            "linhas_dobra_confirmadas"
        ),

        geometria.get(
            "linhas_de_dobra_confirmadas"
        ),
    ]

    for candidato in candidatos:

        if not isinstance(
            candidato,
            list,
        ):
            continue

        resultado = []

        for item in candidato:

            if not isinstance(
                item,
                dict,
            ):
                continue

            resultado.append(
                item
            )

        if resultado:

            return resultado

    return []

# =============================================================================
# STATUS DAS DOBRAS
# =============================================================================

def avaliar_status_dobras(
    possiveis,
    confirmadas,
):

    if confirmadas:

        return "CONFIRMADAS"

    if possiveis:

        return "NAO_CONFIRMADAS"

    return "NAO_IDENTIFICADAS"


# =============================================================================
# INFORMAÃ‡Ã•ES DE FABRICAÃ‡ÃƒO
# =============================================================================

def construir_fabricacao(
    geometria,
    curvas,
):

    material = extrair_material(
        geometria
    )

    espessura = extrair_espessura(
        geometria
    )

    raio = extrair_raio(
        geometria,
        curvas,
    )

    fabricacao_original = geometria.get(
        "fabricacao",
        {}
    )

    metodo = None
    fator_k = None
    fator_dobra = None

    if isinstance(
        fabricacao_original,
        dict,
    ):

        metodo = texto(
            fabricacao_original.get(
                "metodo_fabricacao",
                fabricacao_original.get(
                    "metodo"
                )
            )
        )

        fator_k = numero(
            fabricacao_original.get(
                "fator_k"
            )
        )

        fator_dobra = numero(
            fabricacao_original.get(
                "fator_dobra"
            )
        )

    if metodo is None:

        metodo = texto(
            geometria.get(
                "metodo_fabricacao"
            )
        )

    if fator_k is None:

        fator_k = numero(
            geometria.get(
                "fator_k"
            )
        )

    if fator_dobra is None:

        fator_dobra = numero(
            geometria.get(
                "fator_dobra"
            )
        )

    return {
        "material": material,

        "espessura_mm":
            round(
                espessura,
                4,
            )
            if espessura is not None
            else None,

        "raio_interno_mm":
            round(
                raio,
                4,
            )
            if raio is not None
            else None,

        "metodo_fabricacao":
            metodo,

        "fator_k":
            fator_k,

        "fator_dobra":
            fator_dobra,
    }


# =============================================================================
# AVALIAÃ‡ÃƒO DO DESENVOLVIMENTO
# =============================================================================

def avaliar_desenvolvimento(
    dimensoes,
    fabricacao,
    possiveis_dobras,
    confirmadas,
):

    pendencias = []

    if not dimensoes:

        pendencias.append(
            "DIMENSOES_NAO_IDENTIFICADAS"
        )

    if not possiveis_dobras:

        pendencias.append(
            "LINHAS_DE_DOBRA_NAO_IDENTIFICADAS"
        )

    elif not confirmadas:

        pendencias.append(
            "LINHAS_DE_DOBRA_NAO_CONFIRMADAS"
        )

    if fabricacao[
        "espessura_mm"
    ] is None:

        pendencias.append(
            "ESPESSURA_NAO_VALIDADA_NESTA_ETAPA"
        )

    if fabricacao[
        "raio_interno_mm"
    ] is None:

        pendencias.append(
            "RAIO_INTERNO_NAO_CONFIRMADO"
        )

    if possiveis_dobras and not confirmadas:

        pendencias.append(
            "ANGULOS_DE_DOBRA_NAO_CONFIRMADOS"
        )

    if fabricacao[
        "fator_k"
    ] is None:

        pendencias.append(
            "FATOR_K_NAO_DEFINIDO"
        )

    if fabricacao[
        "fator_dobra"
    ] is None:

        pendencias.append(
            "FATOR_DE_DOBRA_NAO_DEFINIDO"
        )

    if fabricacao[
        "metodo_fabricacao"
    ] is None:

        pendencias.append(
            "METODO_DE_FABRICACAO_NAO_DEFINIDO"
        )

    # -------------------------------------------------------------------------
    # O extrator nÃ£o calcula blank.
    # -------------------------------------------------------------------------

    return {
        "status": (
            "SUFICIENTE_PARA_PROXIMA_ETAPA"
            if not pendencias
            else "INSUFICIENTE"
        ),

        "blank_calculado": "NAO",

        "desenvolvimento_calculado": "NAO",

        "pendencias": pendencias,

        "observacao": (
            "A dimensÃ£o geomÃ©trica nÃ£o Ã© a dimensÃ£o de corte. "
            "O blank definitivo serÃ¡ calculado pelo mÃ³dulo "
            "calculadora_desenvolvimento apÃ³s a validaÃ§Ã£o dos "
            "parÃ¢metros de fabricaÃ§Ã£o."
        ),
    }


# =============================================================================
# CONSTRUÃ‡ÃƒO DO RESULTADO
# =============================================================================

def construir_resultado(
    geometria,
    caminho_entrada,
):

    vertices = extrair_vertices(
        geometria
    )

    dimensoes = calcular_dimensoes(
        vertices
    )

    segmentos = extrair_segmentos(
        vertices
    )

    segmentos_resumo = (
        resumir_segmentos(
            segmentos
        )
    )

    angulos = extrair_angulos(
        vertices
    )

    angulos_resumo = (
        resumir_angulos(
            angulos
        )
    )

    curvas = extrair_curvas(
        geometria
    )

    classificacao = (
        classificar_geometria(
            dimensoes,
            segmentos_resumo,
            angulos_resumo,
            curvas,
        )
    )

    caracteristicas = (
        detectar_caracteristicas(
            dimensoes,
            segmentos,
            curvas,
            angulos,
        )
    )

    possiveis_dobras = (
        identificar_possiveis_dobras(
            angulos
        )
    )

    dobras_confirmadas = (
        identificar_dobras_confirmadas(
            geometria,
            possiveis_dobras,
        )
    )

    status_dobras = (
        avaliar_status_dobras(
            possiveis_dobras,
            dobras_confirmadas,
        )
    )

    fabricacao = (
        construir_fabricacao(
            geometria,
            curvas,
        )
    )

    desenvolvimento = (
        avaliar_desenvolvimento(
            dimensoes,
            fabricacao,
            possiveis_dobras,
            dobras_confirmadas,
        )
    )

    return {

        "aizi": {
            "modulo":
                "extrator_dimensional",

            "versao":
                "2.0",
        },

        "arquivo_origem":
            str(caminho_entrada),

        "componente":
            geometria.get(
                "componente"
            ),

        "score_identificacao":
            numero(
                geometria.get(
                    "score",
                    geometria.get(
                        "score_identificacao"
                    )
                )
            ),

        "escala":
            numero(
                geometria.get(
                    "escala"
                )
            ),

        "orientacao":
            geometria.get(
                "orientacao"
            ),

        "dimensao_alvo_mm":
            geometria.get(
                "dimensao_alvo_mm"
            ),

        "dimensao_estimada_mm":
            geometria.get(
                "dimensao_estimada_mm"
            ),

        "dimensoes_geometricas":
            dimensoes,

        "classificacao":
            classificacao,

        "caracteristicas":
            caracteristicas,

        "segmentos":
            segmentos,

        "resumo_segmentos":
            segmentos_resumo,

        "angulos":
            angulos,

        "resumo_angulos":
            angulos_resumo,

        "curvas":
            curvas,

        # ---------------------------------------------------------------------
        # FABRICAÃ‡ÃƒO
        # ---------------------------------------------------------------------

        "fabricacao":
            fabricacao,

        # ---------------------------------------------------------------------
        # DOBRAS
        # ---------------------------------------------------------------------

        "dobras": {

            "quantidade_possiveis":
                len(
                    possiveis_dobras
                ),

            "quantidade_confirmadas":
                len(
                    dobras_confirmadas
                ),

            "status":
                status_dobras,

            "possiveis":
                possiveis_dobras,

            "confirmadas":
                dobras_confirmadas,
        },

        # ---------------------------------------------------------------------
        # VÃ‰RTICES
        # ---------------------------------------------------------------------

        "vertices": [
            {
                "x_mm": round(
                    p[0],
                    4,
                ),

                "y_mm": round(
                    p[1],
                    4,
                ),
            }

            for p in vertices
        ],

        # ---------------------------------------------------------------------
        # DESENVOLVIMENTO
        # ---------------------------------------------------------------------

        "desenvolvimento":
            desenvolvimento,
    }


# =============================================================================
# IMPRESSÃƒO
# =============================================================================

def imprimir_resultado(
    resultado,
):

    print()
    print("=" * 80)
    print(
        "AIZI ENGINEERING AI"
    )
    print(
        "EXTRATOR DIMENSIONAL"
    )
    print("=" * 80)

    print()

    print(
        f"Componente: "
        f"{resultado['componente']}"
    )

    print(
        f"Score identificaÃ§Ã£o: "
        f"{resultado['score_identificacao']:.2f}"
    )

    print(
        f"Escala: "
        f"{resultado['escala']:.6f}"
    )

    print()

    print(
        "CLASSIFICAÃ‡ÃƒO"
    )

    print(
        f"    {resultado['classificacao']}"
    )

    print()

    print(
        "DIMENSÃ•ES GEOMÃ‰TRICAS"
    )

    dimensoes = (
        resultado[
            "dimensoes_geometricas"
        ]
    )

    if dimensoes:

        print(
            f"    Largura: "
            f"{dimensoes['largura_mm']:.4f} mm"
        )

        print(
            f"    Altura: "
            f"{dimensoes['altura_mm']:.4f} mm"
        )

        print(
            f"    X: "
            f"{dimensoes['x_min_mm']:.4f} â†’ "
            f"{dimensoes['x_max_mm']:.4f}"
        )

        print(
            f"    Y: "
            f"{dimensoes['y_min_mm']:.4f} â†’ "
            f"{dimensoes['y_max_mm']:.4f}"
        )

        print(
            f"    ProporÃ§Ã£o: "
            f"{dimensoes['proporcao']:.4f}"
        )

    print()

    resumo = (
        resultado[
            "resumo_segmentos"
        ]
    )

    print(
        "SEGMENTOS"
    )

    print(
        f"    Total: "
        f"{resumo['quantidade_total']}"
    )

    print(
        f"    Horizontais: "
        f"{resumo['horizontais']}"
    )

    print(
        f"    Verticais: "
        f"{resumo['verticais']}"
    )

    print(
        f"    Inclinados: "
        f"{resumo['inclinados']}"
    )

    print(
        f"    Comprimento total: "
        f"{resumo['comprimento_total_mm']:.4f} mm"
    )

    print()

    angulos = (
        resultado[
            "resumo_angulos"
        ]
    )

    print(
        "Ã‚NGULOS"
    )

    print(
        f"    Analisados: "
        f"{angulos['quantidade_vertices_analisados']}"
    )

    print(
        f"    90Â°: "
        f"{angulos['angulos_90_graus']}"
    )

    print(
        f"    45Â°: "
        f"{angulos['angulos_45_graus']}"
    )

    print(
        f"    30Â°: "
        f"{angulos['angulos_30_graus']}"
    )

    print(
        f"    60Â°: "
        f"{angulos['angulos_60_graus']}"
    )

    print(
        f"    Outros: "
        f"{angulos['outros_angulos']}"
    )

    print()

    print(
        "CURVAS"
    )

    curvas = resultado[
        "curvas"
    ]

    if not curvas:

        print(
            "    Nenhuma curva identificada."
        )

    else:

        for i, curva in enumerate(
            curvas,
            start=1,
        ):

            print(
                f"    Curva {i:02d} | "
                f"{curva['classificacao']} | "
                f"Raio="
                f"{curva['raio_mm']} mm | "
                f"Erro="
                f"{curva['erro_maximo_mm']} mm"
            )

    print()

    # -------------------------------------------------------------------------
    # FABRICAÃ‡ÃƒO
    # -------------------------------------------------------------------------

    print(
        "INFORMAÃ‡Ã•ES DE FABRICAÃ‡ÃƒO"
    )

    fabricacao = resultado[
        "fabricacao"
    ]

    print(
        "    Material: "
        + (
            str(
                fabricacao[
                    "material"
                ]
            )
            if fabricacao[
                "material"
            ]
            else "NÃƒO IDENTIFICADO"
        )
    )

    print(
        "    Espessura: "
        + (
            f"{fabricacao['espessura_mm']:.4f} mm"
            if fabricacao[
                "espessura_mm"
            ] is not None
            else "NÃƒO IDENTIFICADA"
        )
    )

    print(
        "    Raio interno: "
        + (
            f"R{fabricacao['raio_interno_mm']:.4f} mm"
            if fabricacao[
                "raio_interno_mm"
            ] is not None
            else "NÃƒO IDENTIFICADO"
        )
    )

    print(
        "    MÃ©todo de fabricaÃ§Ã£o: "
        + (
            str(
                fabricacao[
                    "metodo_fabricacao"
                ]
            )
            if fabricacao[
                "metodo_fabricacao"
            ]
            else "NÃƒO DEFINIDO"
        )
    )

    print(
        "    Fator K: "
        + (
            f"{fabricacao['fator_k']:.4f}"
            if fabricacao[
                "fator_k"
            ] is not None
            else "NÃƒO DEFINIDO"
        )
    )

    print(
        "    Fator de dobra: "
        + (
            f"{fabricacao['fator_dobra']:.4f}"
            if fabricacao[
                "fator_dobra"
            ] is not None
            else "NÃƒO DEFINIDO"
        )
    )

    print()

    # -------------------------------------------------------------------------
    # DOBRAS
    # -------------------------------------------------------------------------

    dobras = resultado[
        "dobras"
    ]

    print(
        "DOBRAS"
    )

    print(
        f"    PossÃ­veis: "
        f"{dobras['quantidade_possiveis']}"
    )

    print(
        f"    Confirmadas: "
        f"{dobras['quantidade_confirmadas']}"
    )

    print(
        f"    Status: "
        f"{dobras['status']}"
    )

    if dobras[
        "possiveis"
    ]:

        print()

        print(
            "POSSÃVEIS DOBRAS"
        )

        for dobra in dobras[
            "possiveis"
        ]:

            print(
                f"    VÃ©rtice "
                f"{dobra['vertice']} | "
                f"X={dobra['x_mm']:.4f} | "
                f"Y={dobra['y_mm']:.4f} | "
                f"Ã‚ngulo="
                f"{dobra['angulo_graus']:.2f}Â° | "
                f"{dobra['status']}"
            )

    print()

    # -------------------------------------------------------------------------
    # DESENVOLVIMENTO
    # -------------------------------------------------------------------------

    desenvolvimento = resultado[
        "desenvolvimento"
    ]

    print(
        "DESENVOLVIMENTO"
    )

    print(
        f"    Status: "
        f"{desenvolvimento['status']}"
    )

    print(
        f"    Blank calculado: "
        f"{desenvolvimento['blank_calculado']}"
    )

    print(
        f"    Desenvolvimento calculado: "
        f"{desenvolvimento['desenvolvimento_calculado']}"
    )

    if desenvolvimento[
        "pendencias"
    ]:

        print()

        print(
            "PendÃªncias:"
        )

        for pendencia in desenvolvimento[
            "pendencias"
        ]:

            print(
                f"    - {pendencia}"
            )

    print()

    print(
        "REGRA DE ENGENHARIA"
    )

    print(
        "    DimensÃ£o geomÃ©trica â‰  dimensÃ£o de corte."
    )

    print(
        "    O blank definitivo NÃƒO foi calculado nesta etapa."
    )

    print()

    print(
        "PRÃ“XIMO MÃ“DULO"
    )

    print(
        "    calculadora_desenvolvimento"
    )


# =============================================================================
# SALVAR JSON
# =============================================================================

def salvar_json(
    resultado,
    caminho_entrada,
):

    pasta = Path(
        caminho_entrada
    ).parent

    nome = Path(
        caminho_entrada
    ).stem

    caminho_saida = (
        pasta
        / f"{nome}_dimensional.json"
    )

    with open(
        caminho_saida,
        "w",
        encoding="utf-8",
    ) as arquivo:

        json.dump(
            resultado,
            arquivo,
            ensure_ascii=False,
            indent=4,
        )

    print()

    print(
        "DiagnÃ³stico dimensional salvo em:"
    )

    print(
        caminho_saida
    )

    return caminho_saida


# =============================================================================
# MAIN
# =============================================================================

def main():

    print(
        "=" * 80
    )

    print(
        "AIZI ENGINEERING AI"
    )

    print(
        "EXTRATOR DIMENSIONAL"
    )

    print(
        "=" * 80
    )

    print()

    caminho = localizar_json()

    if caminho is None:

        print(
            "Nenhum arquivo *_geometria.json encontrado."
        )

        print()

        print(
            "Pasta pesquisada:"
        )

        print(
            PASTA_DIAGNOSTICO
        )

        return

    print(
        "Arquivo de geometria:"
    )

    print(
        caminho
    )

    try:

        geometria = carregar_geometria(
            caminho
        )

    except Exception as erro:

        print()

        print(
            "ERRO AO LER JSON:"
        )

        print(
            erro
        )

        return

    resultado = construir_resultado(
        geometria,
        caminho,
    )

    imprimir_resultado(
        resultado
    )

    salvar_json(
        resultado,
        caminho
    )

    print()

    print(
        "=" * 80
    )

    print(
        "EXTRAÃ‡ÃƒO DIMENSIONAL CONCLUÃDA"
    )

    print(
        "=" * 80
    )


# =============================================================================
# EXECUÃ‡ÃƒO
# =============================================================================

if __name__ == "__main__":
    main()
