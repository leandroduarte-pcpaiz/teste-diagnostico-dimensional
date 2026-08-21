#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIZI Engineering AI
Conversor / Diagnóstico DXF

Objetivo:
- Ler DXF ASCII sem depender de ezdxf.
- Extrair LINE, ARC e CIRCLE do MODEL SPACE.
- Reconstruir representação geométrica normalizada.
- Identificar contorno e furos.
- Classificar arcos geométricos do contorno.
- NÃO confundir arco de contorno com dobra tecnológica.
- Produzir JSON utilizável pelos próximos módulos do AIZI.

Regra importante:
O DXF geométrico não informa necessariamente:
- material;
- espessura;
- ângulo tecnológico de dobra;
- K-factor;
- sequência de dobra.

Portanto, essas informações não são inventadas.

Um ARC representa geometria existente no DXF.
Somente a existência de um ARC NÃO significa que exista uma dobra.

As dobras tecnológicas devem ser fornecidas pelo diagnóstico do desenho,
processo, cadastro ou outra fonte de engenharia.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


TOL = 1e-5

# Um arco somente pode ser classificado como pequeno trecho curvo.
# NÃO será transformado automaticamente em dobra.
ARC_CONTORNO_MIN_SWEEP_DEG = 1.0
ARC_CONTORNO_MAX_SWEEP_DEG = 359.999


@dataclass
class Point:
    x: float
    y: float

    def distance(self, other: "Point") -> float:
        return math.hypot(
            self.x - other.x,
            self.y - other.y,
        )


@dataclass
class LineEntity:
    handle: str
    layer: str
    start: Point
    end: Point

    @property
    def length(self) -> float:
        return self.start.distance(self.end)


@dataclass
class ArcEntity:
    handle: str
    layer: str
    center: Point
    radius: float
    start_deg: float
    end_deg: float

    @property
    def start(self) -> Point:
        return polar(
            self.center,
            self.radius,
            self.start_deg,
        )

    @property
    def end(self) -> Point:
        return polar(
            self.center,
            self.radius,
            self.end_deg,
        )

    @property
    def sweep_deg(self) -> float:
        sweep = (
            self.end_deg - self.start_deg
        ) % 360.0

        if sweep <= TOL:
            sweep = 360.0

        return sweep

    @property
    def length(self) -> float:
        return (
            math.radians(self.sweep_deg)
            * self.radius
        )


@dataclass
class CircleEntity:
    handle: str
    layer: str
    center: Point
    radius: float


def polar(
    center: Point,
    radius: float,
    angle_deg: float,
) -> Point:

    angle = math.radians(angle_deg)

    return Point(
        center.x
        + radius * math.cos(angle),
        center.y
        + radius * math.sin(angle),
    )


def angle_deg(
    a: Point,
    b: Point,
) -> float:

    return (
        math.degrees(
            math.atan2(
                b.y - a.y,
                b.x - a.x,
            )
        )
        % 360.0
    )


def normalize_angle(
    value: float,
) -> float:

    return value % 360.0


def fmt(
    value: float,
) -> float:

    if abs(value) < 1e-9:
        return 0.0

    return round(
        float(value),
        6,
    )


def point_dict(
    point: Point,
) -> Dict[str, float]:

    return {
        "x": fmt(point.x),
        "y": fmt(point.y),
    }


def parse_pairs(
    text: str,
) -> List[Tuple[int, str]]:

    raw = text.splitlines()

    pairs: List[
        Tuple[int, str]
    ] = []

    i = 0

    while i + 1 < len(raw):

        code_line = raw[i].strip()
        value_line = (
            raw[i + 1]
            .rstrip("\r\n")
        )

        try:
            code = int(code_line)
        except ValueError:
            i += 1
            continue

        pairs.append(
            (
                code,
                value_line.strip(),
            )
        )

        i += 2

    return pairs


def chunks_until_zero(
    pairs: Sequence[
        Tuple[int, str]
    ],
    section_name: str,
) -> List[
    List[
        Tuple[int, str]
    ]
]:

    in_section = False

    current: List[
        Tuple[int, str]
    ] = []

    entities: List[
        List[
            Tuple[int, str]
        ]
    ] = []

    i = 0

    while i < len(pairs):

        code, value = pairs[i]

        if (
            code == 0
            and value == "SECTION"
        ):

            if (
                i + 1 < len(pairs)
                and pairs[i + 1]
                == (
                    2,
                    section_name,
                )
            ):

                in_section = True
                i += 2
                continue

        if (
            in_section
            and code == 0
            and value == "ENDSEC"
        ):
            break

        if in_section and code == 0:

            if current:
                entities.append(
                    current
                )

            current = [
                (
                    code,
                    value,
                )
            ]

        elif in_section:

            current.append(
                (
                    code,
                    value,
                )
            )

        i += 1

    if current:
        entities.append(
            current
        )

    return entities


def first_value(
    entity: Sequence[
        Tuple[int, str]
    ],
    code: int,
    default: Optional[str] = None,
) -> Optional[str]:

    for current_code, value in entity:

        if current_code == code:
            return value

    return default


def to_float(
    value: Optional[str],
    default: float = 0.0,
) -> float:

    try:
        if value is None:
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def read_dxf(
    path: Path,
) -> Tuple[
    List[LineEntity],
    List[ArcEntity],
    List[CircleEntity],
    Dict[str, object],
]:

    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    pairs = parse_pairs(text)

    lines: List[
        LineEntity
    ] = []

    arcs: List[
        ArcEntity
    ] = []

    circles: List[
        CircleEntity
    ] = []

    entities = chunks_until_zero(
        pairs,
        "ENTITIES",
    )

    for entity in entities:

        kind = first_value(
            entity,
            0,
            "",
        )

        if kind not in {
            "LINE",
            "ARC",
            "CIRCLE",
        }:
            continue

        handle = (
            first_value(
                entity,
                5,
                "",
            )
            or ""
        )

        layer = (
            first_value(
                entity,
                8,
                "0",
            )
            or "0"
        )

        if kind == "LINE":

            start = Point(
                to_float(
                    first_value(
                        entity,
                        10,
                    )
                ),
                to_float(
                    first_value(
                        entity,
                        20,
                    )
                ),
            )

            end = Point(
                to_float(
                    first_value(
                        entity,
                        11,
                    )
                ),
                to_float(
                    first_value(
                        entity,
                        21,
                    )
                ),
            )

            lines.append(
                LineEntity(
                    handle,
                    layer,
                    start,
                    end,
                )
            )

        elif kind == "ARC":

            center = Point(
                to_float(
                    first_value(
                        entity,
                        10,
                    )
                ),
                to_float(
                    first_value(
                        entity,
                        20,
                    )
                ),
            )

            radius = to_float(
                first_value(
                    entity,
                    40,
                )
            )

            start_deg = normalize_angle(
                to_float(
                    first_value(
                        entity,
                        50,
                    )
                )
            )

            end_deg = normalize_angle(
                to_float(
                    first_value(
                        entity,
                        51,
                    )
                )
            )

            arcs.append(
                ArcEntity(
                    handle,
                    layer,
                    center,
                    radius,
                    start_deg,
                    end_deg,
                )
            )

        elif kind == "CIRCLE":

            center = Point(
                to_float(
                    first_value(
                        entity,
                        10,
                    )
                ),
                to_float(
                    first_value(
                        entity,
                        20,
                    )
                ),
            )

            radius = to_float(
                first_value(
                    entity,
                    40,
                )
            )

            circles.append(
                CircleEntity(
                    handle,
                    layer,
                    center,
                    radius,
                )
            )

    header = extract_header_info(
        pairs
    )

    return (
        lines,
        arcs,
        circles,
        header,
    )


def extract_header_info(
    pairs: Sequence[
        Tuple[int, str]
    ],
) -> Dict[str, object]:

    info: Dict[
        str,
        object,
    ] = {}

    current_var: Optional[
        str
    ] = None

    for code, value in pairs:

        if (
            code == 9
            and value
            in {
                "$INSUNITS",
                "$MEASUREMENT",
                "$ACADVER",
            }
        ):

            current_var = value
            continue

        if (
            current_var
            == "$ACADVER"
            and code == 1
        ):

            info[
                "acadver"
            ] = value

            current_var = None

        elif (
            current_var
            == "$INSUNITS"
            and code == 70
        ):

            info[
                "insunits"
            ] = int(
                to_float(value)
            )

            current_var = None

        elif (
            current_var
            == "$MEASUREMENT"
            and code == 70
        ):

            info[
                "measurement"
            ] = int(
                to_float(value)
            )

            current_var = None

    if info.get(
        "insunits"
    ) == 4:

        info[
            "unidade_detectada"
        ] = "mm"

    else:

        info[
            "unidade_detectada"
        ] = None

    return info


def angle_is_on_arc(
    angle: float,
    start: float,
    end: float,
) -> bool:

    angle = normalize_angle(
        angle
    )

    start = normalize_angle(
        start
    )

    end = normalize_angle(
        end
    )

    if abs(
        (end - start)
        % 360.0
    ) < TOL:

        return True

    sweep = (
        end - start
    ) % 360.0

    from_start = (
        angle - start
    ) % 360.0

    return (
        from_start
        <= sweep + TOL
    )


def bbox_from_geometry(
    lines: Sequence[
        LineEntity
    ],
    arcs: Sequence[
        ArcEntity
    ],
    circles: Sequence[
        CircleEntity
    ],
) -> Dict[str, object]:

    xs: List[
        float
    ] = []

    ys: List[
        float
    ] = []

    for line in lines:

        xs.extend(
            [
                line.start.x,
                line.end.x,
            ]
        )

        ys.extend(
            [
                line.start.y,
                line.end.y,
            ]
        )

    for arc in arcs:

        candidates = [
            arc.start,
            arc.end,
        ]

        for angle in (
            0.0,
            90.0,
            180.0,
            270.0,
        ):

            if angle_is_on_arc(
                angle,
                arc.start_deg,
                arc.end_deg,
            ):

                candidates.append(
                    polar(
                        arc.center,
                        arc.radius,
                        angle,
                    )
                )

        xs.extend(
            point.x
            for point in candidates
        )

        ys.extend(
            point.y
            for point in candidates
        )

    for circle in circles:

        xs.extend(
            [
                circle.center.x
                - circle.radius,
                circle.center.x
                + circle.radius,
            ]
        )

        ys.extend(
            [
                circle.center.y
                - circle.radius,
                circle.center.y
                + circle.radius,
            ]
        )

    if not xs:

        return {
            "min_x": None,
            "max_x": None,
            "min_y": None,
            "max_y": None,
            "largura_mm": None,
            "altura_mm": None,
        }

    min_x = min(xs)
    max_x = max(xs)

    min_y = min(ys)
    max_y = max(ys)

    return {
        "min_x": fmt(min_x),
        "max_x": fmt(max_x),
        "min_y": fmt(min_y),
        "max_y": fmt(max_y),
        "largura_mm": fmt(
            max_x - min_x
        ),
        "altura_mm": fmt(
            max_y - min_y
        ),
    }


def classify_arcs(
    arcs: Sequence[
        ArcEntity
    ],
) -> List[
    Dict[str, object]
]:

    resultado: List[
        Dict[str, object]
    ] = []

    for arc in arcs:

        sweep = arc.sweep_deg

        if (
            sweep
            >= 179.0
            and sweep
            <= 181.0
        ):

            tipo = (
                "ARCO_CONTORNO_SEMICIRCULAR"
            )

        elif sweep < 179.0:

            tipo = (
                "ARCO_CONTORNO_PARTE_CURVA"
            )

        else:

            tipo = (
                "ARCO_CONTORNO_CURVA"
            )

        resultado.append(
            {
                "handle": arc.handle,
                "tipo": tipo,
                "layer": arc.layer,
                "centro": point_dict(
                    arc.center
                ),
                "raio_mm": fmt(
                    arc.radius
                ),
                "angulo_inicial_deg": fmt(
                    arc.start_deg
                ),
                "angulo_final_deg": fmt(
                    arc.end_deg
                ),
                "sweep_deg": fmt(
                    sweep
                ),
                "comprimento_mm": fmt(
                    arc.length
                ),
                "funcao": (
                    "GEOMETRIA_DE_CONTORNO"
                ),
                "dobra_tecnologica": False,
            }
        )

    return resultado


def detect_contour(
    lines: Sequence[
        LineEntity
    ],
    arcs: Sequence[
        ArcEntity
    ],
    circles: Sequence[
        CircleEntity
    ],
) -> Dict[str, object]:

    return {
        "linhas_contorno": [
            line.handle
            for line in lines
        ],
        "arcos_contorno": [
            arc.handle
            for arc in arcs
        ],
        "circulos_furos": [
            circle.handle
            for circle in circles
        ],
        "quantidade_linhas": len(
            lines
        ),
        "quantidade_arcos": len(
            arcs
        ),
        "quantidade_circulos": len(
            circles
        ),
        "status": "EXTRAIDO",
    }


def build_bend_diagnosis(
    bends: Optional[
        Sequence[
            Dict[str, object]
        ]
    ] = None,
) -> Dict[str, object]:

    if bends:

        return {
            "status": "INFORMADO",
            "origem": (
                "FONTE_DE_ENGENHARIA"
            ),
            "quantidade": len(
                bends
            ),
            "itens": list(
                bends
            ),
        }

    return {
        "status": "NAO_DETERMINADO",
        "origem": (
            "NAO_INFORMADO_NO_DXF"
        ),
        "quantidade": 0,
        "itens": [],
        "motivo": (
            "O DXF fornece geometria plana, "
            "mas não contém informação suficiente "
            "para afirmar a existência de uma dobra "
            "tecnológica."
        ),
    }


def calculate_bend_allowance(
    radius_mm: float,
    thickness_mm: float,
    angle_deg_value: float,
    k_factor: float,
) -> float:

    theta = math.radians(
        angle_deg_value
    )

    return (
        theta
        * (
            radius_mm
            + k_factor
            * thickness_mm
        )
    )


def calculate_development(
    bends: Sequence[
        Dict[str, object]
    ],
    thickness_mm: Optional[float],
    k_factor: Optional[float],
    angle_deg_value: Optional[float],
) -> Dict[str, object]:

    if not bends:

        return {
            "status": "NAO_CALCULADO",
            "motivo": (
                "DOBRAS_NAO_INFORMADAS"
            ),
            "origem_dobras": (
                "DXF_NAO_DETERMINA_DOBRAS"
            ),
        }

    if (
        thickness_mm is None
        or k_factor is None
        or angle_deg_value is None
    ):

        return {
            "status": "NAO_CALCULADO",
            "motivo": (
                "ESPESSURA_K_FACTOR_ANGULO_NAO_INFORMADOS"
            ),
        }

    total_ba = 0.0

    calculadas: List[
        Dict[str, object]
    ] = []

    for index, bend in enumerate(
        bends,
        1,
    ):

        radius = float(
            bend["raio_mm"]
        )

        angle_value = float(
            bend.get(
                "angulo_deg",
                angle_deg_value,
            )
        )

        ba = calculate_bend_allowance(
            radius,
            thickness_mm,
            angle_value,
            k_factor,
        )

        total_ba += ba

        calculadas.append(
            {
                "numero": index,
                "raio_mm": fmt(
                    radius
                ),
                "angulo_deg": fmt(
                    angle_value
                ),
                "k_factor": fmt(
                    k_factor
                ),
                "espessura_mm": fmt(
                    thickness_mm
                ),
                "bend_allowance_mm": fmt(
                    ba
                ),
            }
        )

    return {
        "status": "CALCULADO",
        "metodo": (
            "BA_DOBRAS_FONTE_ENGENHARIA"
        ),
        "bend_allowance_total_mm": fmt(
            total_ba
        ),
        "dobras": calculadas,
    }


def build_report(
    path: Path,
    lines: Sequence[
        LineEntity
    ],
    arcs: Sequence[
        ArcEntity
    ],
    circles: Sequence[
        CircleEntity
    ],
    header: Dict[str, object],
    thickness_mm: Optional[float],
    k_factor: Optional[float],
    angle_deg_value: Optional[float],
) -> Dict[str, object]:

    dimensional = bbox_from_geometry(
        lines,
        arcs,
        circles,
    )

    arc_classes = classify_arcs(
        arcs
    )

    contour = detect_contour(
        lines,
        arcs,
        circles,
    )

    # IMPORTANTÍSSIMO:
    # O DXF atual NÃO fornece dobras tecnológicas.
    #
    # Os dois ARC encontrados são semicírculos R10
    # do próprio contorno.
    #
    # Portanto NÃO criamos candidatos de dobra aqui.

    bends = []

    bend_diagnosis = (
        build_bend_diagnosis(
            bends
        )
    )

    development = calculate_development(
        bends=bends,
        thickness_mm=thickness_mm,
        k_factor=k_factor,
        angle_deg_value=angle_deg_value,
    )

    holes = [
        {
            "handle": circle.handle,
            "layer": circle.layer,
            "centro": point_dict(
                circle.center
            ),
            "raio_mm": fmt(
                circle.radius
            ),
            "diametro_mm": fmt(
                2.0 * circle.radius
            ),
            "tipo": "FURO_CIRCULAR",
        }
        for circle in circles
    ]

    return {
        "aizi_engineering_ai": {
            "modulo": (
                "conversor_dxf"
            ),
            "versao": "0.3.0",
        },

        "arquivo": path.name,

        "caminho": str(
            path
        ),

        "unidades": (
            header.get(
                "unidade_detectada"
            )
            or "NAO_DETERMINADA"
        ),

        "header": header,

        "geometria": {
            "linhas": [
                {
                    "handle": line.handle,
                    "layer": line.layer,
                    "inicio": point_dict(
                        line.start
                    ),
                    "fim": point_dict(
                        line.end
                    ),
                    "comprimento_mm": fmt(
                        line.length
                    ),
                }
                for line in lines
            ],

            "arcos": [
                {
                    "handle": arc.handle,
                    "layer": arc.layer,
                    "centro": point_dict(
                        arc.center
                    ),
                    "raio_mm": fmt(
                        arc.radius
                    ),
                    "inicio": point_dict(
                        arc.start
                    ),
                    "fim": point_dict(
                        arc.end
                    ),
                    "angulo_inicial_deg": fmt(
                        arc.start_deg
                    ),
                    "angulo_final_deg": fmt(
                        arc.end_deg
                    ),
                    "sweep_deg": fmt(
                        arc.sweep_deg
                    ),
                    "comprimento_mm": fmt(
                        arc.length
                    ),
                }
                for arc in arcs
            ],

            "circulos": holes,
        },

        "arcos_classificados": arc_classes,

        "dimensional": dimensional,

        "contorno": contour,

        "dobras": bend_diagnosis,

        "parametros_tecnologicos": {
            "espessura_mm": (
                thickness_mm
            ),
            "k_factor": (
                k_factor
            ),
            "angulo_deg": (
                angle_deg_value
            ),
        },

        "desenvolvimento": development,

        "status": {
            "geometria_lida": True,

            "contorno_extraido": bool(
                lines or arcs
            ),

            "furos_extraidos": bool(
                circles
            ),

            "arcos_contorno_classificados": bool(
                arc_classes
            ),

            "dobras_determinadas_pelo_dxf": False,

            "dobras_externas_aguardando_integracao": True,

            "material_informado": False,
        },
    }


def print_summary(
    report: Dict[str, object],
) -> None:

    geo = report[
        "geometria"
    ]

    dimensional = report[
        "dimensional"
    ]

    arcs = report[
        "arcos_classificados"
    ]

    bends = report[
        "dobras"
    ]

    development = report[
        "desenvolvimento"
    ]

    print("=" * 80)

    print(
        "AIZI ENGINEERING AI - CONVERSOR DXF"
    )

    print("=" * 80)

    print(
        f"Arquivo: {report['arquivo']}"
    )

    print(
        f"Unidades: {report['unidades']}"
    )

    print()

    print("GEOMETRIA")

    print(
        f"  Linhas : "
        f"{len(geo['linhas'])}"
    )

    print(
        f"  Arcos  : "
        f"{len(geo['arcos'])}"
    )

    print(
        f"  Círculos: "
        f"{len(geo['circulos'])}"
    )

    print()

    print("ENVELOPE")

    print(
        f"  Largura : "
        f"{dimensional['largura_mm']} mm"
    )

    print(
        f"  Altura  : "
        f"{dimensional['altura_mm']} mm"
    )

    print(
        f"  X       : "
        f"{dimensional['min_x']} .. "
        f"{dimensional['max_x']}"
    )

    print(
        f"  Y       : "
        f"{dimensional['min_y']} .. "
        f"{dimensional['max_y']}"
    )

    print()

    print("FUROS")

    if not geo["circulos"]:

        print(
            "  Nenhum furo encontrado."
        )

    else:

        for hole in geo[
            "circulos"
        ]:

            print(
                f"  {hole['handle']}: "
                f"centro=("
                f"{hole['centro']['x']}, "
                f"{hole['centro']['y']}) "
                f"Ø{hole['diametro_mm']} mm"
            )

    print()

    print("ARCOS DO CONTORNO")

    if not arcs:

        print(
            "  Nenhum arco encontrado."
        )

    else:

        for index, arc in enumerate(
            arcs,
            1,
        ):

            print(
                f"  Arco {index}: "
                f"handle={arc['handle']} "
                f"R={arc['raio_mm']} mm "
                f"sweep={arc['sweep_deg']}° "
                f"tipo={arc['tipo']}"
            )

    print()

    print("DOBRAS TECNOLÓGICAS")

    if (
        bends["status"]
        == "NAO_DETERMINADO"
    ):

        print(
            "  Não determinadas pelo DXF."
        )

        print(
            "  Aguardando integração "
            "com diagnóstico de engenharia."
        )

    else:

        print(
            f"  Quantidade: "
            f"{bends['quantidade']}"
        )

    print()

    print("DESENVOLVIMENTO")

    print(
        json.dumps(
            development,
            ensure_ascii=False,
            indent=2,
        )
    )

    print()

    print(
        "STATUS DE INTEGRAÇÃO"
    )

    print(
        "  Geometria DXF        : OK"
    )

    print(
        "  Contorno             : OK"
    )

    print(
        "  Furos                : OK"
    )

    print(
        "  Arcos classificados  : OK"
    )

    print(
        "  Dobras pelo DXF      : NÃO DISPONÍVEIS"
    )

    print(
        "  Integração engenharia: PENDENTE"
    )

    print("=" * 80)


def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "AIZI Engineering AI - "
            "Conversor DXF"
        )
    )

    parser.add_argument(
        "arquivo",
        help=(
            "Caminho do arquivo DXF"
        ),
    )

    parser.add_argument(
        "--espessura",
        type=float,
        default=None,
        help=(
            "Espessura da chapa em mm."
        ),
    )

    parser.add_argument(
        "--k-factor",
        dest="k_factor",
        type=float,
        default=None,
        help=(
            "K-factor para cálculo "
            "de BA."
        ),
    )

    parser.add_argument(
        "--angulo",
        type=float,
        default=None,
        help=(
            "Ângulo tecnológico "
            "da dobra."
        ),
    )

    parser.add_argument(
        "--json",
        dest="json_path",
        default=None,
        help=(
            "Arquivo JSON de saída."
        ),
    )

    args = parser.parse_args()

    path = Path(
        args.arquivo
    )

    if not path.exists():

        print(
            f"ERRO: arquivo não encontrado: "
            f"{path}",
            file=sys.stderr,
        )

        return 2

    try:

        (
            lines,
            arcs,
            circles,
            header,
        ) = read_dxf(
            path
        )

        report = build_report(
            path=path,
            lines=lines,
            arcs=arcs,
            circles=circles,
            header=header,
            thickness_mm=args.espessura,
            k_factor=args.k_factor,
            angle_deg_value=args.angulo,
        )

    except Exception as exc:

        print(
            f"ERRO AO PROCESSAR DXF: "
            f"{exc}",
            file=sys.stderr,
        )

        return 1

    print_summary(
        report
    )

    json_path = (
        Path(args.json_path)
        if args.json_path
        else path.with_name(
            path.stem
            + "_aizi.json"
        )
    )

    json_path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()

    print(
        f"JSON salvo em: "
        f"{json_path}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )