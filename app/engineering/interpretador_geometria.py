from pathlib import Path
import json
import math


# =============================================================================
# AIZI ENGINEERING AI
# INTERPRETADOR DE GEOMETRIA
# =============================================================================

PASTA_DIAGNOSTICO = Path(
    r"C:\Projetos\AIZI Engineering AI\diagnostico"
)

TOLERANCIA_HORIZONTAL_MM = 0.5
TOLERANCIA_VERTICAL_MM = 0.5


# =============================================================================
# FUNÇÕES BÁSICAS
# =============================================================================

def distancia(p1, p2):
    return math.hypot(
        p2["x"] - p1["x"],
        p2["y"] - p1["y"],
    )


def classificar_segmento(p1, p2):
    dx = p2["x"] - p1["x"]
    dy = p2["y"] - p1["y"]

    if abs(dx) <= TOLERANCIA_HORIZONTAL_MM:
        return "VERTICAL"

    if abs(dy) <= TOLERANCIA_VERTICAL_MM:
        return "HORIZONTAL"

    return "INCLINADO"


def comprimento_segmento(p1, p2):
    return distancia(p1, p2)


# =============================================================================
# LOCALIZAÇÃO DO JSON
# =============================================================================

def localizar_json():

    arquivos = sorted(
        PASTA_DIAGNOSTICO.glob(
            "*_geometria.json"
        )
    )

    if not arquivos:
        raise FileNotFoundError(
            "Nenhum arquivo *_geometria.json encontrado em:\n"
            f"{PASTA_DIAGNOSTICO}"
        )

    if len(arquivos) == 1:
        return arquivos[0]

    print()
    print("=" * 80)
    print("GEOMETRIAS DISPONÍVEIS")
    print("=" * 80)

    for i, arquivo in enumerate(
        arquivos,
        start=1,
    ):
        print(
            f"{i:02d} - {arquivo.name}"
        )

    print()

    while True:

        entrada = input(
            "Selecione o número da geometria: "
        ).strip()

        try:
            numero = int(entrada)

            if 1 <= numero <= len(arquivos):
                return arquivos[numero - 1]

        except ValueError:
            pass

        print(
            "Seleção inválida."
        )


# =============================================================================
# CARREGAR JSON
# =============================================================================

def carregar_json(caminho):

    with open(
        caminho,
        "r",
        encoding="utf-8",
    ) as arquivo:

        return json.load(arquivo)


# =============================================================================
# VÉRTICES
# =============================================================================

def normalizar_vertices(dados):

    vertices = []

    vertices_origem = dados.get(
        "vertices_mm",
        []
    )

    for ponto in vertices_origem:

        numero = ponto.get(
            "numero",
            len(vertices) + 1
        )

        x = ponto.get("x_mm")
        y = ponto.get("y_mm")

        if x is None or y is None:
            continue

        vertices.append(
            {
                "id": int(numero),
                "x": float(x),
                "y": float(y),
            }
        )

    return vertices


# =============================================================================
# ARCOS
# =============================================================================

def normalizar_arcos(dados):

    arcos = []

    arcos_origem = dados.get(
        "arcos",
        []
    )

    for i, arco in enumerate(
        arcos_origem,
        start=1,
    ):

        arcos.append(
            {
                "id": i,

                "inicio": int(
                    arco.get(
                        "inicio",
                        0
                    )
                ),

                "fim": int(
                    arco.get(
                        "fim",
                        0
                    )
                ),

                "tipo": arco.get(
                    "tipo",
                    "arco"
                ),

                "centro_x": float(
                    arco.get(
                        "centro_x",
                        0.0
                    )
                ),

                "centro_y": float(
                    arco.get(
                        "centro_y",
                        0.0
                    )
                ),

                "raio_mm": float(
                    arco.get(
                        "raio",
                        0.0
                    )
                ),

                "erro_mm": float(
                    arco.get(
                        "erro_maximo",
                        0.0
                    )
                ),

                "pontos": int(
                    arco.get(
                        "pontos",
                        0
                    )
                ),
            }
        )

    return arcos


# =============================================================================
# SEGMENTOS
# =============================================================================

def construir_segmentos(vertices):

    segmentos = []

    if len(vertices) < 2:
        return segmentos

    for i in range(
        len(vertices) - 1
    ):

        p1 = vertices[i]
        p2 = vertices[i + 1]

        comprimento = comprimento_segmento(
            p1,
            p2,
        )

        if comprimento <= 0.001:
            continue

        segmentos.append(
            {
                "id": len(segmentos) + 1,

                "inicio": p1["id"],
                "fim": p2["id"],

                "x1": p1["x"],
                "y1": p1["y"],

                "x2": p2["x"],
                "y2": p2["y"],

                "comprimento_mm": comprimento,

                "tipo": classificar_segmento(
                    p1,
                    p2,
                ),
            }
        )

    return segmentos


# =============================================================================
# EXTREMOS
# =============================================================================

def calcular_extremos(vertices):

    if not vertices:
        return None

    xs = [
        p["x"]
        for p in vertices
    ]

    ys = [
        p["y"]
        for p in vertices
    ]

    return {
        "x_min": min(xs),
        "x_max": max(xs),
        "y_min": min(ys),
        "y_max": max(ys),

        "largura_mm":
            max(xs) - min(xs),

        "altura_mm":
            max(ys) - min(ys),
    }


# =============================================================================
# ESTATÍSTICAS DOS SEGMENTOS
# =============================================================================

def estatisticas_segmentos(segmentos):

    horizontais = []
    verticais = []
    inclinados = []

    for segmento in segmentos:

        if segmento["tipo"] == "HORIZONTAL":

            horizontais.append(segmento)

        elif segmento["tipo"] == "VERTICAL":

            verticais.append(segmento)

        else:

            inclinados.append(segmento)

    return {
        "quantidade_total": len(segmentos),

        "horizontais": len(
            horizontais
        ),

        "verticais": len(
            verticais
        ),

        "inclinados": len(
            inclinados
        ),

        "comprimento_horizontal_mm":
            sum(
                x["comprimento_mm"]
                for x in horizontais
            ),

        "comprimento_vertical_mm":
            sum(
                x["comprimento_mm"]
                for x in verticais
            ),

        "comprimento_inclinado_mm":
            sum(
                x["comprimento_mm"]
                for x in inclinados
            ),
    }


# =============================================================================
# ESTATÍSTICAS DOS ARCOS
# =============================================================================

def estatisticas_arcos(arcos):

    pequenos = []
    medios = []
    grandes = []

    for arco in arcos:

        raio = arco["raio_mm"]

        if raio <= 15:

            pequenos.append(arco)

        elif raio <= 50:

            medios.append(arco)

        else:

            grandes.append(arco)

    return {
        "quantidade": len(arcos),

        "pequenos_R_ate_15mm":
            len(pequenos),

        "medios_R_15_a_50mm":
            len(medios),

        "grandes_R_acima_50mm":
            len(grandes),

        "raios_mm": [
            arco["raio_mm"]
            for arco in arcos
        ],
    }


# =============================================================================
# RELAÇÃO DE ASPECTO
# =============================================================================

def calcular_relacao_aspecto(extremos):

    if not extremos:
        return 0.0

    largura = extremos[
        "largura_mm"
    ]

    altura = extremos[
        "altura_mm"
    ]

    menor = min(
        largura,
        altura,
    )

    if menor <= 0:
        return 0.0

    return max(
        largura,
        altura,
    ) / menor


# =============================================================================
# ORIENTAÇÃO
# =============================================================================

def determinar_orientacao(extremos):

    if not extremos:
        return "DESCONHECIDA"

    largura = extremos[
        "largura_mm"
    ]

    altura = extremos[
        "altura_mm"
    ]

    if largura > altura:
        return "HORIZONTAL"

    if altura > largura:
        return "VERTICAL"

    return "QUADRADA"


# =============================================================================
# DETECÇÃO DOS ARCOS DE RAIO NOMINAL
# =============================================================================

def analisar_raios(arcos):

    resultado = []

    for arco in arcos:

        raio = arco["raio_mm"]

        if abs(raio - 10.0) <= 0.5:

            classificacao = (
                "RAIO_NOMINAL_R10"
            )

        elif abs(raio - 40.0) <= 2.0:

            classificacao = (
                "RAIO_APROXIMADO_R40"
            )

        else:

            classificacao = (
                "RAIO_NAO_CLASSIFICADO"
            )

        resultado.append(
            {
                "arco": arco["id"],
                "raio_mm": raio,
                "classificacao":
                    classificacao,
                "erro_mm":
                    arco["erro_mm"],
            }
        )

    return resultado


# =============================================================================
# INDICADORES DE FABRICAÇÃO
# =============================================================================

def detectar_indicadores(
    vertices,
    segmentos,
    arcos,
    relacao_aspecto,
):

    indicadores = []

    if relacao_aspecto >= 3.0:

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

    if len(segmentos) >= 20:

        indicadores.append(
            "GEOMETRIA_DETALHADA"
        )

    horizontais = sum(
        1
        for s in segmentos
        if s["tipo"] == "HORIZONTAL"
    )

    verticais = sum(
        1
        for s in segmentos
        if s["tipo"] == "VERTICAL"
    )

    if horizontais >= 2 and verticais >= 2:

        indicadores.append(
            "CONTORNO_PREDOMINANTEMENTE_ORTOGONAL"
        )

    raios_r10 = sum(
        1
        for arco in arcos
        if abs(
            arco["raio_mm"] - 10.0
        ) <= 0.5
    )

    if raios_r10 >= 2:

        indicadores.append(
            "DOIS_OU_MAIS_RAIOS_R10"
        )

    return indicadores


# =============================================================================
# CONSTRUIR ESTRUTURA
# =============================================================================

def interpretar_geometria(dados):

    vertices = normalizar_vertices(
        dados
    )

    arcos = normalizar_arcos(
        dados
    )

    segmentos = construir_segmentos(
        vertices
    )

    extremos = calcular_extremos(
        vertices
    )

    estatisticas_seg = (
        estatisticas_segmentos(
            segmentos
        )
    )

    estatisticas_arc = (
        estatisticas_arcos(
            arcos
        )
    )

    relacao_aspecto = (
        calcular_relacao_aspecto(
            extremos
        )
    )

    orientacao = (
        determinar_orientacao(
            extremos
        )
    )

    indicadores = (
        detectar_indicadores(
            vertices,
            segmentos,
            arcos,
            relacao_aspecto,
        )
    )

    analise_raios = (
        analisar_raios(arcos)
    )

    estrutura = {

        "tipo":
            "PECA_MANUFATURADA",

        "origem": {

            "componente":
                dados.get(
                    "componente"
                ),

            "score":
                dados.get(
                    "score"
                ),

            "escala":
                dados.get(
                    "escala"
                ),

            "orientacao_original":
                dados.get(
                    "orientacao"
                ),

            "dimensao_alvo_mm":
                dados.get(
                    "dimensao_alvo_mm"
                ),
        },

        "dimensoes": {

            "largura_mm":
                dados.get(
                    "largura_mm",
                    0.0
                ),

            "altura_mm":
                dados.get(
                    "altura_mm",
                    0.0
                ),

            "orientacao":
                orientacao,

            "relacao_aspecto":
                relacao_aspecto,
        },

        "metricas": {

            "area_mm2":
                dados.get(
                    "area_mm2",
                    0.0
                ),

            "perimetro_mm":
                dados.get(
                    "perimetro_mm",
                    0.0
                ),
        },

        "geometria": {

            "vertices":
                vertices,

            "segmentos":
                segmentos,

            "arcos":
                arcos,
        },

        "estatisticas": {

            "quantidade_vertices":
                len(vertices),

            "segmentos":
                estatisticas_seg,

            "arcos":
                estatisticas_arc,
        },

        "analise_raios":
            analise_raios,

        "indicadores_fabricacao":
            indicadores,
    }

    return estrutura


# =============================================================================
# IMPRESSÃO
# =============================================================================

def imprimir_resumo(estrutura):

    print()
    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("INTERPRETAÇÃO DA GEOMETRIA")
    print("=" * 80)

    print()

    print("ORIGEM:")

    print(
        f"  Componente: "
        f"{estrutura['origem']['componente']}"
    )

    print(
        f"  Score: "
        f"{estrutura['origem']['score']}"
    )

    print(
        f"  Escala: "
        f"{estrutura['origem']['escala']:.6f}"
    )

    print()

    print("DIMENSÕES:")

    print(
        f"  Largura: "
        f"{estrutura['dimensoes']['largura_mm']:.4f} mm"
    )

    print(
        f"  Altura: "
        f"{estrutura['dimensoes']['altura_mm']:.4f} mm"
    )

    print(
        f"  Orientação: "
        f"{estrutura['dimensoes']['orientacao']}"
    )

    print(
        f"  Relação de aspecto: "
        f"{estrutura['dimensoes']['relacao_aspecto']:.4f}"
    )

    print()

    print("MÉTRICAS:")

    print(
        f"  Área: "
        f"{estrutura['metricas']['area_mm2']:.4f} mm²"
    )

    print(
        f"  Perímetro: "
        f"{estrutura['metricas']['perimetro_mm']:.4f} mm"
    )

    print()

    print("GEOMETRIA:")

    print(
        f"  Vértices: "
        f"{estrutura['estatisticas']['quantidade_vertices']}"
    )

    print(
        f"  Segmentos: "
        f"{estrutura['estatisticas']['segmentos']['quantidade_total']}"
    )

    print(
        f"  Arcos: "
        f"{estrutura['estatisticas']['arcos']['quantidade']}"
    )

    print()

    print("SEGMENTOS:")

    print(
        f"  Horizontais: "
        f"{estrutura['estatisticas']['segmentos']['horizontais']}"
    )

    print(
        f"  Verticais: "
        f"{estrutura['estatisticas']['segmentos']['verticais']}"
    )

    print(
        f"  Inclinados: "
        f"{estrutura['estatisticas']['segmentos']['inclinados']}"
    )

    print()

    print("ARCOS:")

    for arco in estrutura[
        "analise_raios"
    ]:

        print(
            f"  Arco {arco['arco']:02d} | "
            f"R={arco['raio_mm']:.4f} mm | "
            f"Erro={arco['erro_mm']:.4f} mm | "
            f"{arco['classificacao']}"
        )

    print()

    print(
        "INDICADORES DE FABRICAÇÃO:"
    )

    for indicador in estrutura[
        "indicadores_fabricacao"
    ]:

        print(
            f"  - {indicador}"
        )


# =============================================================================
# SALVAR
# =============================================================================

def salvar_estrutura(
    estrutura,
    caminho_origem,
):

    caminho_origem = Path(
        caminho_origem
    )

    caminho_saida = (
        caminho_origem.parent
        / (
            caminho_origem.stem
            + "_interpretada.json"
        )
    )

    with open(
        caminho_saida,
        "w",
        encoding="utf-8",
    ) as arquivo:

        json.dump(
            estrutura,
            arquivo,
            ensure_ascii=False,
            indent=4,
        )

    return caminho_saida


# =============================================================================
# MAIN
# =============================================================================

def main():

    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("INTERPRETADOR DE GEOMETRIA")
    print("=" * 80)

    try:

        caminho_json = localizar_json()

    except Exception as erro:

        print()
        print(
            f"ERRO: {erro}"
        )

        return

    print()
    print(
        f"Entrada:"
    )

    print(
        caminho_json
    )

    try:

        dados = carregar_json(
            caminho_json
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

    try:

        estrutura = interpretar_geometria(
            dados
        )

    except Exception as erro:

        print()
        print(
            "ERRO AO INTERPRETAR GEOMETRIA:"
        )

        print(
            erro
        )

        return

    imprimir_resumo(
        estrutura
    )

    try:

        caminho_saida = salvar_estrutura(
            estrutura,
            caminho_json,
        )

    except Exception as erro:

        print()
        print(
            "ERRO AO SALVAR ESTRUTURA:"
        )

        print(
            erro
        )

        return

    print()
    print("=" * 80)
    print(
        "ESTRUTURA DE ENGENHARIA SALVA EM:"
    )
    print("=" * 80)

    print(
        caminho_saida
    )


if __name__ == "__main__":
    main()