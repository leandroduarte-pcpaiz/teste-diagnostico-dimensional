#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIZI Engineering AI
Extrator geométrico DXF

Responsabilidades:
- Ler DXF através do ezdxf.
- Extrair LINE, LWPOLYLINE, POLYLINE, ARC, CIRCLE e SPLINE.
- Converter curvas em pontos com tolerância controlada.
- Reconstruir cadeias geométricas.
- Identificar contornos fechados.
- Identificar contorno principal e contornos internos.
- Preservar a origem geométrica de cada trecho.
- Suportar SPLINE através de flattening.
- Calcular dimensões, área bruta, área de furos,
  área líquida e perímetro do flat pattern.

IMPORTANTE:
O DXF é tratado como fonte geométrica.

O extrator NÃO inventa:
- material;
- espessura;
- K-factor;
- ângulo tecnológico;
- sequência de dobra;
- desenvolvimento de dobra.

Se o DXF representa um flat pattern, as dimensões geométricas
do DXF são consideradas dimensões efetivas de corte.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# ======================================================================
# DATACLASSES
# ======================================================================

@dataclass
class PontoDXF:
    x: float
    y: float


@dataclass
class SegmentoDXF:
    tipo: str
    x1: float
    y1: float
    x2: float
    y2: float
    comprimento_mm: float


# ======================================================================
# EXTRATOR
# ======================================================================

class ExtratorDXF:
    """
    Extrator geométrico AIZI para arquivos DXF.

    O DXF é fonte geométrica preferencial para peças de chapa/corte.

    Saída principal:
        - contornos fechados;
        - contorno principal;
        - contornos internos;
        - largura/comprimento do blank;
        - área bruta;
        - área de furos;
        - área líquida;
        - perímetro;
        - segmentos;
        - entidades de origem;
        - diagnóstico de SPLINE.

    Não calcula desenvolvimento de dobra.
    """

    _UNITS_TO_MM = {
        0: 1.0,
        1: 25.4,
        2: 304.8,
        3: 1609344.0,
        4: 1.0,
        5: 10.0,
        6: 1000.0,
        7: 1000000.0,
    }

    def __init__(
        self,
        tolerancia_mm: float = 0.05,
    ) -> None:

        self.tolerancia_mm = float(
            tolerancia_mm
        )

    # ==================================================================
    # UTILIDADES
    # ==================================================================

    @staticmethod
    def _dist(
        a: PontoDXF,
        b: PontoDXF,
    ) -> float:

        return math.hypot(
            b.x - a.x,
            b.y - a.y,
        )

    @staticmethod
    def _angulo_normalizado(
        angulo: float,
    ) -> float:

        return float(angulo) % 360.0

    @staticmethod
    def _fechar_pontos(
        pontos: List[PontoDXF],
    ) -> List[PontoDXF]:

        if not pontos:
            return pontos

        if (
            math.isclose(
                pontos[0].x,
                pontos[-1].x,
                abs_tol=1e-9,
            )
            and
            math.isclose(
                pontos[0].y,
                pontos[-1].y,
                abs_tol=1e-9,
            )
        ):
            return pontos

        return pontos + [
            pontos[0]
        ]

    @staticmethod
    def _area(
        pontos: List[PontoDXF],
    ) -> float:

        if len(pontos) < 3:
            return 0.0

        pts = (
            ExtratorDXF._fechar_pontos(
                pontos
            )
        )

        total = 0.0

        for a, b in zip(
            pts,
            pts[1:],
        ):
            total += (
                a.x * b.y
                -
                b.x * a.y
            )

        return abs(total) / 2.0

    @staticmethod
    def _perimetro(
        pontos: List[PontoDXF],
    ) -> float:

        if len(pontos) < 2:
            return 0.0

        pts = (
            ExtratorDXF._fechar_pontos(
                pontos
            )
        )

        return sum(
            ExtratorDXF._dist(a, b)
            for a, b in zip(
                pts,
                pts[1:],
            )
        )

    @staticmethod
    def _bbox(
        pontos: List[PontoDXF],
    ) -> Tuple[
        float,
        float,
        float,
        float,
    ]:

        if not pontos:
            return (
                0.0,
                0.0,
                0.0,
                0.0,
            )

        xs = [
            p.x
            for p in pontos
        ]

        ys = [
            p.y
            for p in pontos
        ]

        return (
            min(xs),
            min(ys),
            max(xs),
            max(ys),
        )

    def _unidade_mm(
        self,
        doc,
    ) -> float:

        try:
            unidades = int(
                doc.header.get(
                    "$INSUNITS",
                    0,
                )
            )
        except Exception:
            unidades = 0

        return self._UNITS_TO_MM.get(
            unidades,
            1.0,
        )

    # ==================================================================
    # ARC / CIRCLE
    # ==================================================================

    def _pontos_arco(
        self,
        cx: float,
        cy: float,
        raio: float,
        inicio: float,
        fim: float,
        escala: float,
    ) -> List[PontoDXF]:

        inicio_rad = math.radians(
            inicio
        )

        fim_rad = math.radians(
            fim
        )

        while fim_rad <= inicio_rad:
            fim_rad += (
                2.0 * math.pi
            )

        delta = (
            fim_rad
            -
            inicio_rad
        )

        comprimento_estimado = (
            delta
            *
            max(
                raio * escala,
                1.0,
            )
        )

        n = max(
            8,
            int(
                math.ceil(
                    comprimento_estimado
                    / 2.0
                )
            ),
        )

        n = min(
            n,
            720,
        )

        pontos: List[
            PontoDXF
        ] = []

        for i in range(
            n + 1
        ):

            angulo = (
                inicio_rad
                +
                delta
                *
                i
                /
                n
            )

            pontos.append(
                PontoDXF(
                    cx
                    +
                    raio
                    *
                    math.cos(
                        angulo
                    ),
                    cy
                    +
                    raio
                    *
                    math.sin(
                        angulo
                    ),
                )
            )

        return pontos

    # ==================================================================
    # SPLINE
    # ==================================================================

    def _pontos_spline(
        self,
        entidade,
        escala: float,
    ) -> List[PontoDXF]:

        try:

            tolerancia_curva = max(
                self.tolerancia_mm / 5.0,
                0.01,
            )

            pontos: List[
                PontoDXF
            ] = []

            for ponto in entidade.flattening(
                tolerancia_curva
            ):

                pontos.append(
                    PontoDXF(
                        float(
                            ponto[0]
                        )
                        *
                        escala,

                        float(
                            ponto[1]
                        )
                        *
                        escala,
                    )
                )

            if len(pontos) < 2:
                return []

            return pontos

        except Exception:
            return []

    # ==================================================================
    # ENTIDADE -> GEOMETRIA
    # ==================================================================

    def _entidade_para_pontos(
        self,
        entidade,
        escala: float,
    ) -> Tuple[
        List[PontoDXF],
        str,
    ]:

        dxftype = (
            entidade.dxftype()
        )

        if dxftype == "LINE":

            a = entidade.dxf.start
            b = entidade.dxf.end

            return (
                [
                    PontoDXF(
                        float(a.x)
                        *
                        escala,
                        float(a.y)
                        *
                        escala,
                    ),
                    PontoDXF(
                        float(b.x)
                        *
                        escala,
                        float(b.y)
                        *
                        escala,
                    ),
                ],
                "LINE",
            )

        if dxftype == "LWPOLYLINE":

            pontos: List[
                PontoDXF
            ] = []

            for item in entidade.get_points(
                "xy"
            ):

                pontos.append(
                    PontoDXF(
                        float(
                            item[0]
                        )
                        *
                        escala,

                        float(
                            item[1]
                        )
                        *
                        escala,
                    )
                )

            if getattr(
                entidade,
                "closed",
                False,
            ):

                pontos = (
                    self._fechar_pontos(
                        pontos
                    )
                )

            return (
                pontos,
                "LWPOLYLINE",
            )

        if dxftype == "POLYLINE":

            pontos: List[
                PontoDXF
            ] = []

            for vertice in entidade.vertices:

                p = (
                    vertice.dxf.location
                )

                pontos.append(
                    PontoDXF(
                        float(p.x)
                        *
                        escala,

                        float(p.y)
                        *
                        escala,
                    )
                )

            if (
                getattr(
                    entidade,
                    "is_2d_polyline",
                    False,
                )
                and
                getattr(
                    entidade,
                    "is_closed",
                    False,
                )
            ):

                pontos = (
                    self._fechar_pontos(
                        pontos
                    )
                )

            return (
                pontos,
                "POLYLINE",
            )

        if dxftype == "CIRCLE":

            centro = (
                entidade.dxf.center
            )

            raio = float(
                entidade.dxf.radius
            )

            pontos = (
                self._pontos_arco(
                    float(
                        centro.x
                    ),
                    float(
                        centro.y
                    ),
                    raio,
                    0.0,
                    360.0,
                    escala,
                )
            )

            return (
                pontos,
                "CIRCLE",
            )

        if dxftype == "ARC":

            centro = (
                entidade.dxf.center
            )

            pontos = (
                self._pontos_arco(
                    float(
                        centro.x
                    ),
                    float(
                        centro.y
                    ),
                    float(
                        entidade.dxf.radius
                    ),
                    float(
                        entidade.dxf.start_angle
                    ),
                    float(
                        entidade.dxf.end_angle
                    ),
                    escala,
                )
            )

            return (
                pontos,
                "ARC",
            )

        if dxftype == "SPLINE":

            pontos = (
                self._pontos_spline(
                    entidade,
                    escala,
                )
            )

            return (
                pontos,
                "SPLINE",
            )

        return (
            [],
            dxftype,
        )

    # ==================================================================
    # COLETA
    # ==================================================================

    def _coletar_entidades(
        self,
        doc,
    ) -> List[
        Dict[str, Any]
    ]:

        escala = (
            self._unidade_mm(
                doc
            )
        )

        entidades: List[
            Dict[str, Any]
        ] = []

        for entidade in doc.modelspace():

            try:

                pontos, tipo = (
                    self._entidade_para_pontos(
                        entidade,
                        escala,
                    )
                )

            except Exception:
                continue

            if len(pontos) < 2:
                continue

            if (
                self._perimetro(
                    pontos
                )
                <
                self.tolerancia_mm
            ):
                continue

            entidades.append(
                {
                    "pontos": pontos,
                    "tipo": tipo,
                    "handle": getattr(
                        entidade.dxf,
                        "handle",
                        None,
                    ),
                }
            )

        if not entidades:
            return []

        def distancia(
            a: PontoDXF,
            b: PontoDXF,
        ) -> float:

            return self._dist(
                a,
                b,
            )

        restantes = [
            {
                "pontos": list(
                    item["pontos"]
                ),
                "tipo": item[
                    "tipo"
                ],
                "handle": item[
                    "handle"
                ],
            }
            for item in entidades
        ]

        cadeias: List[
            Dict[str, Any]
        ] = []

        while restantes:

            cadeia_item = (
                restantes.pop(0)
            )

            cadeia = list(
                cadeia_item[
                    "pontos"
                ]
            )

            entidades_cadeia = [
                {
                    "tipo": cadeia_item[
                        "tipo"
                    ],
                    "handle": cadeia_item[
                        "handle"
                    ],
                    "quantidade_pontos": len(
                        cadeia_item[
                            "pontos"
                        ]
                    ),
                }
            ]

            mudou = True

            while mudou:

                mudou = False

                inicio_cadeia = (
                    cadeia[0]
                )

                fim_cadeia = (
                    cadeia[-1]
                )

                melhor_indice = -1
                melhor_operacao = None
                melhor_distancia = float(
                    "inf"
                )

                for indice, candidato in enumerate(
                    restantes
                ):

                    pontos_candidato = (
                        candidato[
                            "pontos"
                        ]
                    )

                    if len(
                        pontos_candidato
                    ) < 2:
                        continue

                    c_inicio = (
                        pontos_candidato[
                            0
                        ]
                    )

                    c_fim = (
                        pontos_candidato[
                            -1
                        ]
                    )

                    opcoes = [
                        (
                            distancia(
                                fim_cadeia,
                                c_inicio,
                            ),
                            "FIM_INICIO",
                        ),
                        (
                            distancia(
                                fim_cadeia,
                                c_fim,
                            ),
                            "FIM_FIM",
                        ),
                        (
                            distancia(
                                inicio_cadeia,
                                c_fim,
                            ),
                            "INICIO_FIM",
                        ),
                        (
                            distancia(
                                inicio_cadeia,
                                c_inicio,
                            ),
                            "INICIO_INICIO",
                        ),
                    ]

                    distancia_local, operacao = min(
                        opcoes,
                        key=lambda item: item[0],
                    )

                    if (
                        distancia_local
                        <= self.tolerancia_mm
                        and
                        distancia_local
                        <
                        melhor_distancia
                    ):

                        melhor_distancia = (
                            distancia_local
                        )

                        melhor_indice = (
                            indice
                        )

                        melhor_operacao = (
                            operacao
                        )

                if melhor_indice < 0:
                    break

                candidato = (
                    restantes.pop(
                        melhor_indice
                    )
                )

                pontos_candidato = list(
                    candidato[
                        "pontos"
                    ]
                )

                entidade_info = {
                    "tipo": candidato[
                        "tipo"
                    ],
                    "handle": candidato[
                        "handle"
                    ],
                    "quantidade_pontos": len(
                        pontos_candidato
                    ),
                }

                if (
                    melhor_operacao
                    ==
                    "FIM_INICIO"
                ):

                    cadeia.extend(
                        pontos_candidato[
                            1:
                        ]
                    )

                    entidades_cadeia.append(
                        entidade_info
                    )

                elif (
                    melhor_operacao
                    ==
                    "FIM_FIM"
                ):

                    pontos_candidato.reverse()

                    cadeia.extend(
                        pontos_candidato[
                            1:
                        ]
                    )

                    entidades_cadeia.append(
                        entidade_info
                    )

                elif (
                    melhor_operacao
                    ==
                    "INICIO_FIM"
                ):

                    pontos_candidato = (
                        pontos_candidato[
                            :-1
                        ]
                    )

                    pontos_candidato.reverse()

                    cadeia = (
                        pontos_candidato
                        +
                        cadeia
                    )

                    entidades_cadeia.insert(
                        0,
                        entidade_info,
                    )

                elif (
                    melhor_operacao
                    ==
                    "INICIO_INICIO"
                ):

                    pontos_candidato.reverse()

                    pontos_candidato = (
                        pontos_candidato[
                            :-1
                        ]
                    )

                    cadeia = (
                        pontos_candidato
                        +
                        cadeia
                    )

                    entidades_cadeia.insert(
                        0,
                        entidade_info,
                    )

                mudou = True

            cadeia = (
                self._fechar_pontos(
                    cadeia
                )
            )

            cadeias.append(
                {
                    "pontos": cadeia,
                    "entidades": entidades_cadeia,
                }
            )

        return cadeias

    # ==================================================================
    # CONTORNOS
    # ==================================================================

    def _contorno_fechado(
        self,
        pontos: List[PontoDXF],
    ) -> bool:

        if len(pontos) < 3:
            return False

        return (
            self._dist(
                pontos[0],
                pontos[-1],
            )
            <=
            self.tolerancia_mm
        )

    # ==================================================================
    # SEGMENTOS
    # ==================================================================

    def _segmentos(
        self,
        pontos: List[PontoDXF],
        entidades: Optional[
            List[Dict[str, Any]]
        ] = None,
    ) -> List[SegmentoDXF]:

        pts = list(pontos)

        if len(pts) < 2:
            return []

        segmentos: List[
            SegmentoDXF
        ] = []

        if (
            entidades
            and
            len(entidades) == 1
        ):

            tipo = entidades[0].get(
                "tipo",
                "GEOMETRIA",
            )

            pts = (
                self._fechar_pontos(
                    pts
                )
            )

            for a, b in zip(
                pts,
                pts[1:],
            ):

                comprimento = (
                    self._dist(
                        a,
                        b,
                    )
                )

                if (
                    comprimento
                    <=
                    self.tolerancia_mm
                ):
                    continue

                segmentos.append(
                    SegmentoDXF(
                        tipo=tipo,
                        x1=a.x,
                        y1=a.y,
                        x2=b.x,
                        y2=b.y,
                        comprimento_mm=(
                            comprimento
                        ),
                    )
                )

            return segmentos

        if entidades:

            total_pontos_origem = sum(
                max(
                    int(
                        entidade.get(
                            "quantidade_pontos",
                            2,
                        )
                    ),
                    2,
                )
                for entidade in entidades
            )

            total_segmentos = max(
                len(pts) - 1,
                1,
            )

            acumulado = 0

            indice_entidade = 0

            for a, b in zip(
                pts,
                pts[1:],
            ):

                comprimento = (
                    self._dist(
                        a,
                        b,
                    )
                )

                if (
                    comprimento
                    <=
                    self.tolerancia_mm
                ):
                    continue

                entidade_atual = (
                    entidades[
                        indice_entidade
                    ]
                )

                tipo = entidade_atual.get(
                    "tipo",
                    "GEOMETRIA",
                )

                segmentos.append(
                    SegmentoDXF(
                        tipo=tipo,
                        x1=a.x,
                        y1=a.y,
                        x2=b.x,
                        y2=b.y,
                        comprimento_mm=(
                            comprimento
                        ),
                    )
                )

                acumulado += 1

                if (
                    indice_entidade
                    <
                    len(entidades) - 1
                ):

                    proporcao = (
                        acumulado
                        /
                        total_segmentos
                    )

                    alvo = (
                        sum(
                            max(
                                int(
                                    e.get(
                                        "quantidade_pontos",
                                        2,
                                    )
                                ),
                                2,
                            )
                            for e in entidades[
                                :indice_entidade + 1
                            ]
                        )
                        /
                        max(
                            total_pontos_origem,
                            1,
                        )
                    )

                    if (
                        proporcao
                        >=
                        alvo
                    ):
                        indice_entidade += 1

            return segmentos

        pts = (
            self._fechar_pontos(
                pts
            )
        )

        for a, b in zip(
            pts,
            pts[1:],
        ):

            comprimento = (
                self._dist(
                    a,
                    b,
                )
            )

            if (
                comprimento
                <=
                self.tolerancia_mm
            ):
                continue

            segmentos.append(
                SegmentoDXF(
                    tipo="GEOMETRIA",
                    x1=a.x,
                    y1=a.y,
                    x2=b.x,
                    y2=b.y,
                    comprimento_mm=(
                        comprimento
                    ),
                )
            )

        return segmentos

    # ==================================================================
    # EXTRAÇÃO DOS CONTORNOS
    # ==================================================================

    def _extrair_contornos(
        self,
        geometrias: Iterable[
            Dict[str, Any]
        ],
    ) -> List[
        Dict[str, Any]
    ]:

        contornos: List[
            Dict[str, Any]
        ] = []

        for indice, geometria in enumerate(
            geometrias,
            start=1,
        ):

            pontos = geometria[
                "pontos"
            ]

            entidades = geometria.get(
                "entidades",
                [],
            )

            if not self._contorno_fechado(
                pontos
            ):
                continue

            area = self._area(
                pontos
            )

            if area <= 0.01:
                continue

            (
                xmin,
                ymin,
                xmax,
                ymax,
            ) = self._bbox(
                pontos
            )

            largura = (
                xmax - xmin
            )

            altura = (
                ymax - ymin
            )

            perimetro = (
                self._perimetro(
                    pontos
                )
            )

            segmentos = self._segmentos(
                pontos,
                entidades,
            )

            tipos = []
            handles = []

            for entidade in entidades:

                tipo = entidade.get(
                    "tipo"
                )

                handle = entidade.get(
                    "handle"
                )

                if tipo is not None:
                    tipos.append(
                        tipo
                    )

                if handle is not None:
                    handles.append(
                        handle
                    )

            contornos.append(
                {
                    "indice": indice,

                    "pontos": [
                        asdict(p)
                        for p in pontos
                    ],

                    "segmentos": [
                        asdict(s)
                        for s in segmentos
                    ],

                    "entidades_origem": {
                        "tipos": tipos,
                        "handles": handles,
                        "detalhes": entidades,
                    },

                    "largura_mm": largura,
                    "altura_mm": altura,
                    "area_mm2": area,
                    "perimetro_mm": perimetro,
                    "fechado": True,
                }
            )

        contornos.sort(
            key=lambda c: c[
                "area_mm2"
            ],
            reverse=True,
        )

        return contornos

    # ==================================================================
    # CONTAGEM DE ENTIDADES
    # ==================================================================

    def _contar_entidades(
        self,
        doc,
    ) -> Dict[str, int]:

        contagem: Dict[
            str,
            int,
        ] = {}

        for entidade in doc.modelspace():

            tipo = entidade.dxftype()

            contagem[tipo] = (
                contagem.get(
                    tipo,
                    0,
                )
                + 1
            )

        return dict(
            sorted(
                contagem.items()
            )
        )

    # ==================================================================
    # DIAGNÓSTICO DE SPLINES
    # ==================================================================

    def _diagnostico_splines(
        self,
        doc,
        escala: float,
    ) -> List[
        Dict[str, Any]
    ]:

        resultado: List[
            Dict[str, Any]
        ] = []

        for entidade in doc.modelspace():

            if entidade.dxftype() != "SPLINE":
                continue

            pontos = (
                self._pontos_spline(
                    entidade,
                    escala,
                )
            )

            if not pontos:
                continue

            comprimento_aberto = 0.0

            for a, b in zip(
                pontos,
                pontos[1:],
            ):
                comprimento_aberto += (
                    self._dist(
                        a,
                        b,
                    )
                )

            xmin, ymin, xmax, ymax = (
                self._bbox(
                    pontos
                )
            )

            try:
                quantidade_cp = len(
                    entidade.control_points
                )
            except Exception:
                quantidade_cp = 0

            try:
                grau = (
                    int(
                        entidade.dxf.degree
                    )
                    if entidade.dxf.hasattr(
                        "degree"
                    )
                    else None
                )
            except Exception:
                grau = None

            resultado.append(
                {
                    "handle": getattr(
                        entidade.dxf,
                        "handle",
                        None,
                    ),
                    "closed": bool(
                        getattr(
                            entidade,
                            "closed",
                            False,
                        )
                    ),
                    "degree": grau,
                    "control_points": (
                        quantidade_cp
                    ),
                    "pontos_flattening": (
                        len(pontos)
                    ),
                    "comprimento_aproximado_mm": (
                        comprimento_aberto
                    ),
                    "bbox": {
                        "xmin": xmin,
                        "ymin": ymin,
                        "xmax": xmax,
                        "ymax": ymax,
                    },
                }
            )

        return resultado

    # ==================================================================
    # API PÚBLICA
    # ==================================================================

    def analisar(
        self,
        caminho: str | Path,
    ) -> Dict[str, Any]:

        caminho = Path(
            caminho
        )

        if not caminho.is_file():
            raise FileNotFoundError(
                f"DXF não encontrado: {caminho}"
            )

        try:
            import ezdxf
        except ImportError as exc:

            raise RuntimeError(
                "DEPENDENCIA_DXF_AUSENTE: "
                "instale ezdxf com "
                "'pip install ezdxf' "
                "e execute novamente."
            ) from exc

        try:
            doc = ezdxf.readfile(
                str(caminho)
            )
        except Exception as exc:

            raise RuntimeError(
                f"ERRO_LEITURA_DXF: {exc}"
            ) from exc

        escala = (
            self._unidade_mm(
                doc
            )
        )

        contagem_entidades = (
            self._contar_entidades(
                doc
            )
        )

        diagnostico_splines = (
            self._diagnostico_splines(
                doc,
                escala,
            )
        )

        geometrias = (
            self._coletar_entidades(
                doc
            )
        )

        contornos = (
            self._extrair_contornos(
                geometrias
            )
        )

        if not contornos:

            return {
                "status": "ERRO",

                "erro": (
                    "NENHUM_CONTORNO_"
                    "FECHADO_ENCONTRADO"
                ),

                "arquivo_dxf": str(
                    caminho
                ),

                "unidade_fonte": "MM",

                "contagem_entidades_dxf": (
                    contagem_entidades
                ),

                "spline": {
                    "quantidade_dxf": (
                        contagem_entidades.get(
                            "SPLINE",
                            0,
                        )
                    ),
                    "quantidade_diagnostica": (
                        len(
                            diagnostico_splines
                        )
                    ),
                    "suportado": True,
                    "metodo": (
                        "EZDXF_FLATTENING"
                    ),
                    "tolerancia_mm": max(
                        self.tolerancia_mm / 5.0,
                        0.01,
                    ),
                },

                "contornos": [],

                "contorno_principal": None,

                "area_mm2": 0.0,

                "area_bruta_mm2": 0.0,

                "area_furos_mm2": 0.0,

                "area_liquida_mm2": 0.0,
            }

        principal = (
            contornos[0]
        )

        internos = (
            contornos[1:]
        )

        largura = float(
            principal[
                "largura_mm"
            ]
        )

        altura = float(
            principal[
                "altura_mm"
            ]
        )

        dimensao_a = min(
            largura,
            altura,
        )

        dimensao_b = max(
            largura,
            altura,
        )

        # --------------------------------------------------------------
        # TIPOS REALMENTE PRESENTES
        # NO CONTORNO PRINCIPAL
        # --------------------------------------------------------------

        tipos_contorno: List[
            str
        ] = []

        for tipo in principal[
            "entidades_origem"
        ].get(
            "tipos",
            [],
        ):

            if tipo not in tipos_contorno:
                tipos_contorno.append(
                    tipo
                )

        # --------------------------------------------------------------
        # SPLINES DO CONTORNO PRINCIPAL
        # --------------------------------------------------------------

        quantidade_splines = (
            contagem_entidades.get(
                "SPLINE",
                0,
            )
        )

        quantidade_splines_contorno = (
            sum(
                1
                for tipo in principal[
                    "entidades_origem"
                ].get(
                    "tipos",
                    [],
                )
                if tipo == "SPLINE"
            )
        )

        # --------------------------------------------------------------
        # SEGMENTOS DO TIPO SPLINE
        # --------------------------------------------------------------

        segmentos_spline = 0

        for segmento in principal.get(
            "segmentos",
            [],
        ):

            if segmento.get(
                "tipo"
            ) == "SPLINE":

                segmentos_spline += 1

        # --------------------------------------------------------------
        # ÁREA BRUTA
        # --------------------------------------------------------------

        area_bruta_mm2 = float(
            principal[
                "area_mm2"
            ]
        )

        # --------------------------------------------------------------
        # ÁREA DOS CONTORNOS INTERNOS
        #
        # Todos os contornos após o principal são considerados
        # subtrações geométricas da peça.
        # --------------------------------------------------------------

        area_furos_mm2 = sum(
            float(
                contorno.get(
                    "area_mm2",
                    0.0,
                )
            )
            for contorno in internos
        )

        # --------------------------------------------------------------
        # ÁREA LÍQUIDA
        # --------------------------------------------------------------

        area_liquida_mm2 = (
            area_bruta_mm2
            -
            area_furos_mm2
        )

        # Proteção numérica contra pequeno resíduo negativo.
        if (
            area_liquida_mm2 < 0.0
            and
            abs(area_liquida_mm2) < 1e-6
        ):
            area_liquida_mm2 = 0.0

        # --------------------------------------------------------------
        # RESULTADO
        # --------------------------------------------------------------

        return {
            "status": "OK",

            "arquivo_dxf": str(
                caminho
            ),

            "unidade_fonte": "MM",

            "dimensoes_fonte": "DXF",

            "tipo_geometria": (
                "FLAT_PATTERN"
            ),

            "contagem_entidades_dxf": (
                contagem_entidades
            ),

            "entidades_geometricas_contorno": (
                tipos_contorno
            ),

            "spline": {
                "quantidade_dxf": (
                    quantidade_splines
                ),

                "quantidade_no_contorno": (
                    quantidade_splines_contorno
                ),

                "segmentos_flattening_contorno": (
                    segmentos_spline
                ),

                "suportado": True,

                "metodo": (
                    "EZDXF_FLATTENING"
                ),

                "tolerancia_mm": max(
                    self.tolerancia_mm / 5.0,
                    0.01,
                ),

                "diagnostico": (
                    diagnostico_splines
                ),
            },

            "contornos_encontrados": (
                len(contornos)
            ),

            "furos_contornos_internos": (
                len(internos)
            ),

            "contorno_principal": (
                principal
            ),

            "contornos": (
                contornos
            ),

            "dimensao_x_mm": (
                dimensao_a
            ),

            "dimensao_y_mm": (
                dimensao_b
            ),

            "largura_blank_mm": (
                dimensao_a
            ),

            "comprimento_blank_mm": (
                dimensao_b
            ),

            # ----------------------------------------------------------
            # ÁREAS
            # ----------------------------------------------------------

            "area_mm2": (
                area_bruta_mm2
            ),

            "area_bruta_mm2": (
                area_bruta_mm2
            ),

            "area_furos_mm2": (
                area_furos_mm2
            ),

            "area_liquida_mm2": (
                area_liquida_mm2
            ),

            "perimetro_mm": float(
                principal[
                    "perimetro_mm"
                ]
            ),

            "blank": {
                "largura_mm": (
                    dimensao_a
                ),
                "comprimento_mm": (
                    dimensao_b
                ),
            },

            "blank_status": (
                "CALCULADO_PELO_DXF"
            ),

            "blank_origem": (
                "DXF_GEOMETRIA"
            ),
        }


# ======================================================================
# FUNÇÃO DE CONVENIÊNCIA
# ======================================================================

def extrair_dxf(
    caminho: str | Path,
) -> Dict[str, Any]:

    return ExtratorDXF().analisar(
        caminho
    )


# ======================================================================
# EXECUÇÃO DIRETA
# ======================================================================

if __name__ == "__main__":

    import json
    import sys

    if len(sys.argv) != 2:

        print(
            "Uso: "
            "python -m "
            "app.engineering.extrator_dxf "
            "<arquivo.dxf>"
        )

        raise SystemExit(2)

    resultado = extrair_dxf(
        sys.argv[1]
    )

    print(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        )
    )