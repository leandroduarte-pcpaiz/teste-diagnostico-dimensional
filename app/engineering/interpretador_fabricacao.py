from pathlib import Path
import json
import math
import sys


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

ESPESSURA_PADRAO_MM = 6.35
ANGULO_DOBRA_PADRAO = 90.0
TOLERANCIA_RAIO_MM = 0.75

RAIOS_NOMINAIS = [
    5.0,
    8.0,
    10.0,
    12.0,
    15.0,
    20.0,
    25.0,
    30.0,
    35.0,
    40.0,
    50.0,
]

PASTA_DIAGNOSTICO = (
    Path(__file__).resolve().parents[2]
    / "diagnostico"
)


# =============================================================================
# UTILITÁRIOS
# =============================================================================

def distancia(p1, p2):
    return math.hypot(
        p2[0] - p1[0],
        p2[1] - p1[1],
    )


def classificar_raio(raio):
    """
    Identifica o raio nominal mais próximo.
    """

    melhor = None
    menor_erro = float("inf")

    for nominal in RAIOS_NOMINAIS:

        erro = abs(raio - nominal)

        if erro < menor_erro:
            menor_erro = erro
            melhor = nominal

    if melhor is None:
        return {
            "nominal": None,
            "erro": None,
            "classificacao": "NAO_CLASSIFICADO",
        }

    if menor_erro <= TOLERANCIA_RAIO_MM:
        return {
            "nominal": melhor,
            "erro": menor_erro,
            "classificacao": f"R{melhor:g}",
        }

    return {
        "nominal": None,
        "erro": menor_erro,
        "classificacao": "NAO_CLASSIFICADO",
    }


def determinar_orientacao(largura, altura):

    if largura > altura:
        return "HORIZONTAL"

    if altura > largura:
        return "VERTICAL"

    return "QUADRADA"


def calcular_relacao_aspecto(largura, altura):

    if largura <= 0 or altura <= 0:
        return 0.0

    return max(largura, altura) / min(largura, altura)


# =============================================================================
# CARREGAMENTO
# =============================================================================

def carregar_geometria(caminho):

    caminho = Path(caminho)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado:\n{caminho}"
        )

    with open(
        caminho,
        "r",
        encoding="utf-8",
    ) as arquivo:

        return json.load(arquivo)


# =============================================================================
# IDENTIFICAÇÃO DE SEGMENTOS
# =============================================================================

def analisar_segmentos(vertices):

    horizontais = 0
    verticais = 0
    inclinados = 0

    segmentos = []

    tolerancia = 0.05

    if len(vertices) < 2:

        return {
            "horizontais": 0,
            "verticais": 0,
            "inclinados": 0,
            "segmentos": [],
        }

    for i in range(len(vertices) - 1):

        p1 = (
            float(vertices[i]["x_mm"]),
            float(vertices[i]["y_mm"]),
        )

        p2 = (
            float(vertices[i + 1]["x_mm"]),
            float(vertices[i + 1]["y_mm"]),
        )

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        comprimento = math.hypot(dx, dy)

        if comprimento <= 0:
            continue

        if abs(dy) <= tolerancia:

            tipo = "HORIZONTAL"
            horizontais += 1

        elif abs(dx) <= tolerancia:

            tipo = "VERTICAL"
            verticais += 1

        else:

            tipo = "INCLINADO"
            inclinados += 1

        segmentos.append(
            {
                "numero": i + 1,
                "tipo": tipo,
                "comprimento_mm": comprimento,
                "inicio": {
                    "x_mm": p1[0],
                    "y_mm": p1[1],
                },
                "fim": {
                    "x_mm": p2[0],
                    "y_mm": p2[1],
                },
            }
        )

    return {
        "horizontais": horizontais,
        "verticais": verticais,
        "inclinados": inclinados,
        "segmentos": segmentos,
    }


# =============================================================================
# ANÁLISE DOS ARCOS
# =============================================================================

def analisar_arcos(arcos):

    resultado = []

    raios_r10 = []

    for numero, arco in enumerate(arcos, start=1):

        raio = float(
            arco.get("raio", 0.0)
        )

        erro_original = float(
            arco.get("erro_maximo", 0.0)
        )

        classificacao = classificar_raio(
            raio
        )

        item = {
            "numero": numero,
            "inicio": arco.get("inicio"),
            "fim": arco.get("fim"),
            "tipo": arco.get(
                "tipo",
                "arco"
            ),
            "centro_x": float(
                arco.get("centro_x", 0.0)
            ),
            "centro_y": float(
                arco.get("centro_y", 0.0)
            ),
            "raio_mm": raio,
            "erro_geometrico_mm": erro_original,
            "raio_nominal_mm": classificacao[
                "nominal"
            ],
            "classificacao": classificacao[
                "classificacao"
            ],
            "erro_classificacao_mm": classificacao[
                "erro"
            ],
            "pontos": arco.get("pontos"),
        }

        resultado.append(item)

        if classificacao["nominal"] == 10.0:
            raios_r10.append(item)

    return {
        "arcos": resultado,
        "quantidade": len(resultado),
        "quantidade_r10": len(raios_r10),
        "raios_r10": raios_r10,
    }


# =============================================================================
# IDENTIFICAÇÃO DA GEOMETRIA
# =============================================================================

def identificar_geometria(dados):

    largura = float(
        dados.get("largura_mm", 0.0)
    )

    altura = float(
        dados.get("altura_mm", 0.0)
    )

    area = float(
        dados.get("area_mm2", 0.0)
    )

    perimetro = float(
        dados.get("perimetro_mm", 0.0)
    )

    vertices = dados.get(
        "vertices_mm",
        []
    )

    arcos = dados.get(
        "arcos",
        []
    )

    analise_segmentos = analisar_segmentos(
        vertices
    )

    analise_arcos = analisar_arcos(
        arcos
    )

    relacao = calcular_relacao_aspecto(
        largura,
        altura,
    )

    orientacao = determinar_orientacao(
        largura,
        altura,
    )

    indicadores = []

    if relacao >= 3.0:
        indicadores.append(
            "GEOMETRIA_ALONGADA"
        )

    if len(arcos) > 0:
        indicadores.append(
            "PRESENCA_DE_ARCOS"
        )

    if len(arcos) >= 2:
        indicadores.append(
            "MULTIPLOS_ARCOS"
        )

    if len(vertices) >= 20:
        indicadores.append(
            "GEOMETRIA_DETALHADA"
        )

    total_segmentos = (
        analise_segmentos["horizontais"]
        + analise_segmentos["verticais"]
        + analise_segmentos["inclinados"]
    )

    if total_segmentos > 0:

        ortogonais = (
            analise_segmentos["horizontais"]
            + analise_segmentos["verticais"]
        )

        percentual_ortogonal = (
            ortogonais
            / total_segmentos
            * 100.0
        )

        if percentual_ortogonal >= 50.0:
            indicadores.append(
                "CONTORNO_PREDOMINANTEMENTE_ORTOGONAL"
            )

    if analise_arcos["quantidade_r10"] >= 2:
        indicadores.append(
            "DOIS_OU_MAIS_RAIOS_R10"
        )

    return {
        "largura_mm": largura,
        "altura_mm": altura,
        "orientacao": orientacao,
        "relacao_aspecto": relacao,
        "area_mm2": area,
        "perimetro_mm": perimetro,
        "quantidade_vertices": len(vertices),
        "quantidade_segmentos": total_segmentos,
        "segmentos": analise_segmentos,
        "arcos": analise_arcos,
        "indicadores": indicadores,
    }


# =============================================================================
# IDENTIFICAÇÃO DE DOBRAS
# =============================================================================

def identificar_dobras(dados):

    dobras = dados.get(
        "dobras",
        []
    )

    resultado = []

    for numero, dobra in enumerate(
        dobras,
        start=1,
    ):

        angulo = dobra.get(
            "angulo_graus",
            ANGULO_DOBRA_PADRAO,
        )

        raio = dobra.get(
            "raio_mm",
            None,
        )

        resultado.append(
            {
                "numero": numero,
                "angulo_graus": float(
                    angulo
                ),
                "raio_mm": (
                    float(raio)
                    if raio is not None
                    else None
                ),
                "origem": "JSON",
            }
        )

    if resultado:
        status = "IDENTIFICADAS"
    else:
        status = "NAO_IDENTIFICADAS"

    return {
        "quantidade": len(resultado),
        "status": status,
        "dobras": resultado,
    }


# =============================================================================
# CLASSIFICAÇÃO DE FABRICAÇÃO
# =============================================================================

def classificar_fabricacao(
    geometria,
    dobras,
):

    indicadores = geometria["indicadores"]

    possui_arcos = (
        "PRESENCA_DE_ARCOS"
        in indicadores
    )

    possui_r10 = (
        "DOIS_OU_MAIS_RAIOS_R10"
        in indicadores
    )

    if dobras["quantidade"] > 0:

        tipo = "PECA_DOBRADA"

        status = (
            "DESENVOLVIMENTO_NECESSARIO"
        )

    elif possui_arcos:

        tipo = "PECA_CORTE_COM_ARCOS"

        status = (
            "DOBRAS_NAO_CONFIRMADAS"
        )

    else:

        tipo = "PECA_PLANA"

        status = (
            "SEM_DOBRAS_IDENTIFICADAS"
        )

    observacoes = []

    if possui_r10:

        observacoes.append(
            "Foram identificados dois ou mais "
            "raios próximos de R10 no contorno."
        )

    if possui_arcos:

        observacoes.append(
            "Os arcos identificados pertencem "
            "à geometria do contorno e não devem "
            "ser automaticamente tratados como dobras."
        )

    if dobras["quantidade"] == 0:

        observacoes.append(
            "As dobras ainda não foram confirmadas "
            "por dados específicos do desenho."
        )

    return {
        "tipo": tipo,
        "status": status,
        "observacoes": observacoes,
    }


# =============================================================================
# RESULTADO COMPLETO
# =============================================================================

def interpretar(dados):

    geometria = identificar_geometria(
        dados
    )

    dobras = identificar_dobras(
        dados
    )

    fabricacao = classificar_fabricacao(
        geometria,
        dobras,
    )

    resultado = {

        "origem": {
            "componente": dados.get(
                "componente"
            ),
            "score": dados.get(
                "score"
            ),
            "escala": dados.get(
                "escala"
            ),
        },

        "dimensoes": {
            "largura_mm": geometria[
                "largura_mm"
            ],
            "altura_mm": geometria[
                "altura_mm"
            ],
            "orientacao": geometria[
                "orientacao"
            ],
            "relacao_aspecto": geometria[
                "relacao_aspecto"
            ],
        },

        "metricas": {
            "area_mm2": geometria[
                "area_mm2"
            ],
            "perimetro_mm": geometria[
                "perimetro_mm"
            ],
        },

        "geometria": {
            "quantidade_vertices": geometria[
                "quantidade_vertices"
            ],
            "quantidade_segmentos": geometria[
                "quantidade_segmentos"
            ],
            "segmentos": geometria[
                "segmentos"
            ],
            "arcos": geometria[
                "arcos"
            ],
        },

        "fabricacao": {
            "tipo": fabricacao[
                "tipo"
            ],
            "status": fabricacao[
                "status"
            ],
            "dobras": dobras,
            "indicadores": geometria[
                "indicadores"
            ],
            "observacoes": fabricacao[
                "observacoes"
            ],
        },
    }

    return resultado


# =============================================================================
# IMPRESSÃO
# =============================================================================

def imprimir_resultado(resultado):

    origem = resultado["origem"]
    dimensoes = resultado["dimensoes"]
    metricas = resultado["metricas"]
    geometria = resultado["geometria"]
    fabricacao = resultado["fabricacao"]

    print()
    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("INTERPRETADOR DE FABRICAÇÃO")
    print("=" * 80)

    print()
    print("ORIGEM:")

    print(
        f"Componente: "
        f"{origem['componente']}"
    )

    print(
        f"Score: "
        f"{origem['score']}"
    )

    if origem["escala"] is not None:

        print(
            f"Escala: "
            f"{float(origem['escala']):.6f}"
        )

    else:

        print(
            "Escala: não informada"
        )

    print()
    print("DIMENSÕES:")

    print(
        f"Largura: "
        f"{dimensoes['largura_mm']:.4f} mm"
    )

    print(
        f"Altura: "
        f"{dimensoes['altura_mm']:.4f} mm"
    )

    print(
        f"Orientação: "
        f"{dimensoes['orientacao']}"
    )

    print(
        f"Relação de aspecto: "
        f"{dimensoes['relacao_aspecto']:.4f}"
    )

    print()
    print("MÉTRICAS:")

    print(
        f"Área: "
        f"{metricas['area_mm2']:.4f} mm²"
    )

    print(
        f"Perímetro: "
        f"{metricas['perimetro_mm']:.4f} mm"
    )

    print()
    print("GEOMETRIA:")

    print(
        f"Vértices: "
        f"{geometria['quantidade_vertices']}"
    )

    print(
        f"Segmentos: "
        f"{geometria['quantidade_segmentos']}"
    )

    print(
        f"Arcos: "
        f"{len(geometria['arcos']['arcos'])}"
    )

    segmentos = geometria["segmentos"]

    print()
    print("SEGMENTOS:")

    print(
        f"Horizontais: "
        f"{segmentos['horizontais']}"
    )

    print(
        f"Verticais: "
        f"{segmentos['verticais']}"
    )

    print(
        f"Inclinados: "
        f"{segmentos['inclinados']}"
    )

    print()
    print("ARCOS:")

    if not geometria["arcos"]["arcos"]:

        print(
            "Nenhum arco identificado."
        )

    else:

        for arco in geometria[
            "arcos"
        ]["arcos"]:

            print(
                f"Arco {arco['numero']:02d} | "
                f"R={arco['raio_mm']:.4f} mm | "
                f"Erro={arco['erro_geometrico_mm']:.4f} mm | "
                f"{arco['classificacao']}"
            )

    print()
    print("FABRICAÇÃO:")

    print(
        f"Tipo: "
        f"{fabricacao['tipo']}"
    )

    print(
        f"Status: "
        f"{fabricacao['status']}"
    )

    print()
    print("DOBRAS:")

    if not fabricacao["dobras"]["dobras"]:

        print(
            "Nenhuma dobra explicitamente "
            "identificada no JSON."
        )

    else:

        for dobra in fabricacao[
            "dobras"
        ]["dobras"]:

            raio = dobra["raio_mm"]

            if raio is None:
                raio_texto = "não informado"
            else:
                raio_texto = (
                    f"{raio:.3f} mm"
                )

            print(
                f"Dobra {dobra['numero']:02d} | "
                f"Ângulo="
                f"{dobra['angulo_graus']:.2f}° | "
                f"Raio={raio_texto}"
            )

    print()
    print("INDICADORES DE FABRICAÇÃO:")

    if not fabricacao["indicadores"]:

        print(
            "Nenhum indicador."
        )

    else:

        for indicador in fabricacao[
            "indicadores"
        ]:

            print(
                f"- {indicador}"
            )

    print()
    print("OBSERVAÇÕES:")

    for observacao in fabricacao[
        "observacoes"
    ]:

        print(
            f"- {observacao}"
        )

    print()
    print("=" * 80)


# =============================================================================
# LOCALIZAÇÃO DOS JSONS
# =============================================================================

def localizar_geometrias():

    if not PASTA_DIAGNOSTICO.exists():
        return []

    arquivos = sorted(
        PASTA_DIAGNOSTICO.rglob(
            "*geometria.json"
        )
    )

    return [
        arquivo
        for arquivo in arquivos
        if not arquivo.name.endswith(
            "_fabricacao.json"
        )
    ]


def selecionar_geometria():

    arquivos = localizar_geometrias()

    if not arquivos:
        print()
        print(
            "Nenhum arquivo de geometria encontrado."
        )
        print(
            f"Pasta pesquisada:"
        )
        print(
            PASTA_DIAGNOSTICO
        )
        return None

    print()
    print("=" * 80)
    print("GEOMETRIAS DISPONÍVEIS")
    print("=" * 80)

    for numero, arquivo in enumerate(
        arquivos,
        start=1,
    ):

        print(
            f"{numero:02d} - "
            f"{arquivo.parent.name} | "
            f"{arquivo.name}"
        )

    print()

    while True:

        escolha = input(
            "Selecione a geometria: "
        ).strip()

        try:

            indice = int(escolha)

        except ValueError:

            print(
                "Digite o número da peça."
            )
            continue

        if 1 <= indice <= len(arquivos):

            return arquivos[indice - 1]

        print(
            "Opção inválida."
        )


# =============================================================================
# SALVAR RESULTADO
# =============================================================================

def salvar_resultado(
    caminho_entrada,
    resultado,
):

    caminho_entrada = Path(
        caminho_entrada
    )

    pasta = caminho_entrada.parent

    nome = caminho_entrada.stem

    caminho_saida = (
        pasta
        / f"{nome}_fabricacao.json"
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
        "Resultado da interpretação salvo em:"
    )

    print(
        caminho_saida
    )

    return caminho_saida


# =============================================================================
# MAIN
# =============================================================================

def main():

    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("INTERPRETADOR DE FABRICAÇÃO")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # CAMINHO POR ARGUMENTO
    # -------------------------------------------------------------------------

    if len(sys.argv) > 1:

        caminho = Path(
            sys.argv[1]
        )

        print()
        print("Entrada:")
        print(caminho)

    else:

        caminho = selecionar_geometria()

        if caminho is None:
            return

        print()
        print("Entrada:")
        print(caminho)

    # -------------------------------------------------------------------------
    # CARREGAMENTO
    # -------------------------------------------------------------------------

    try:

        dados = carregar_geometria(
            caminho
        )

    except Exception as erro:

        print()
        print(
            "ERRO AO CARREGAR GEOMETRIA:"
        )

        print(
            erro
        )

        return

    # -------------------------------------------------------------------------
    # INTERPRETAÇÃO
    # -------------------------------------------------------------------------

    resultado = interpretar(
        dados
    )

    # -------------------------------------------------------------------------
    # IMPRESSÃO
    # -------------------------------------------------------------------------

    imprimir_resultado(
        resultado
    )

    # -------------------------------------------------------------------------
    # SALVAMENTO
    # -------------------------------------------------------------------------

    salvar_resultado(
        caminho,
        resultado,
    )

    print()
    print("=" * 80)
    print("INTERPRETAÇÃO CONCLUÍDA")
    print("=" * 80)


# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":
    main()