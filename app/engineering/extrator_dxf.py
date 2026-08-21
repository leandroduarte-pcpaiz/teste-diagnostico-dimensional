# -*- coding: utf-8 -*-

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


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


class ExtratorDXF:
    """
    Extrator geométrico AIZI para arquivos DXF.

    O DXF é tratado como fonte geométrica preferencial para peças de
    chapa/corte. O PDF continua sendo fonte complementar para textos,
    material, espessura e informações de fabricação.

    Saída principal:
        - contornos fechados;
        - contorno principal;
        - largura/comprimento do blank;
        - área e perímetro aproximados;
        - segmentos;
        - quantidade de furos/contornos internos;
        - dimensões_fonte = DXF.

    Não calcula desenvolvimento de dobra. Se o DXF já for um flat pattern,
    suas dimensões geométricas são tratadas como dimensões efetivas de corte.
    """

    _UNITS_TO_MM = {
        0: 1.0,       # sem unidade definida: preserva coordenadas
        1: 25.4,      # polegada
        2: 304.8,     # pé
        3: 1609344.0, # milha
        4: 1.0,       # mm
        5: 10.0,      # cm
        6: 1000.0,    # m
        7: 1000000.0, # km
    }

    def __init__(self, tolerancia_mm: float = 0.05) -> None:
        self.tolerancia_mm = float(tolerancia_mm)

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    @staticmethod
    def _dist(a: PontoDXF, b: PontoDXF) -> float:
        return math.hypot(b.x - a.x, b.y - a.y)

    @staticmethod
    def _angulo_normalizado(angulo: float) -> float:
        return float(angulo) % 360.0

    def _pontos_arco(
        self,
        cx: float,
        cy: float,
        raio: float,
        inicio: float,
        fim: float,
        escala: float,
    ) -> List[PontoDXF]:
        inicio = math.radians(inicio)
        fim = math.radians(fim)
        while fim <= inicio:
            fim += 2.0 * math.pi

        delta = fim - inicio
        # Aproximação suficientemente fina para diagnóstico dimensional.
        n = max(8, int(math.ceil(delta * max(raio * escala, 1.0) / 2.0)))
        n = min(n, 720)

        pontos: List[PontoDXF] = []
        for i in range(n + 1):
            a = inicio + delta * i / n
            pontos.append(
                PontoDXF(
                    cx + raio * math.cos(a),
                    cy + raio * math.sin(a),
                )
            )
        return pontos

    @staticmethod
    def _fechar_pontos(pontos: List[PontoDXF]) -> List[PontoDXF]:
        if not pontos:
            return pontos
        if math.isclose(pontos[0].x, pontos[-1].x, abs_tol=1e-9) and math.isclose(
            pontos[0].y, pontos[-1].y, abs_tol=1e-9
        ):
            return pontos
        return pontos + [pontos[0]]

    @staticmethod
    def _area(pontos: List[PontoDXF]) -> float:
        if len(pontos) < 3:
            return 0.0
        pts = ExtratorDXF._fechar_pontos(pontos)
        total = 0.0
        for a, b in zip(pts, pts[1:]):
            total += a.x * b.y - b.x * a.y
        return abs(total) / 2.0

    @staticmethod
    def _perimetro(pontos: List[PontoDXF]) -> float:
        if len(pontos) < 2:
            return 0.0
        pts = ExtratorDXF._fechar_pontos(pontos)
        return sum(ExtratorDXF._dist(a, b) for a, b in zip(pts, pts[1:]))

    @staticmethod
    def _bbox(pontos: List[PontoDXF]) -> Tuple[float, float, float, float]:
        xs = [p.x for p in pontos]
        ys = [p.y for p in pontos]
        return min(xs), min(ys), max(xs), max(ys)

    def _unidade_mm(self, doc) -> float:
        try:
            unidades = int(doc.header.get("$INSUNITS", 0))
        except Exception:
            unidades = 0
        return self._UNITS_TO_MM.get(unidades, 1.0)

    # ------------------------------------------------------------------
    # Entidades
    # ------------------------------------------------------------------

    def _entidade_para_pontos(self, entidade, escala: float) -> List[PontoDXF]:
        dxftype = entidade.dxftype()

        if dxftype == "LINE":
            a = entidade.dxf.start
            b = entidade.dxf.end
            return [
                PontoDXF(float(a.x) * escala, float(a.y) * escala),
                PontoDXF(float(b.x) * escala, float(b.y) * escala),
            ]

        if dxftype == "LWPOLYLINE":
            pontos = []
            for item in entidade.get_points("xy"):
                pontos.append(
                    PontoDXF(float(item[0]) * escala, float(item[1]) * escala)
                )
            if getattr(entidade, "closed", False):
                pontos = self._fechar_pontos(pontos)
            return pontos

        if dxftype == "POLYLINE":
            pontos = []
            for vertice in entidade.vertices:
                p = vertice.dxf.location
                pontos.append(
                    PontoDXF(float(p.x) * escala, float(p.y) * escala)
                )
            if getattr(entidade, "is_2d_polyline", False) and getattr(entidade, "is_closed", False):
                pontos = self._fechar_pontos(pontos)
            return pontos

        if dxftype == "CIRCLE":
            centro = entidade.dxf.center
            raio = float(entidade.dxf.radius)
            return self._pontos_arco(
                float(centro.x), float(centro.y), raio,
                0.0, 360.0, escala,
            )

        if dxftype == "ARC":
            centro = entidade.dxf.center
            return self._pontos_arco(
                float(centro.x), float(centro.y), float(entidade.dxf.radius),
                float(entidade.dxf.start_angle), float(entidade.dxf.end_angle),
                escala,
            )

        return []

    def _coletar_entidades(self, doc) -> List[List[PontoDXF]]:
        escala = self._unidade_mm(doc)
        resultado: List[List[PontoDXF]] = []

        for entidade in doc.modelspace():
            try:
                pontos = self._entidade_para_pontos(entidade, escala)
            except Exception:
                continue

            if len(pontos) < 2:
                continue

            # Ignora geometrias microscópicas.
            if self._perimetro(pontos) < self.tolerancia_mm:
                continue

            resultado.append(pontos)

        return resultado

    # ------------------------------------------------------------------
    # Contornos
    # ------------------------------------------------------------------

    def _contorno_fechado(self, pontos: List[PontoDXF]) -> bool:
        if len(pontos) < 3:
            return False
        a = pontos[0]
        b = pontos[-1]
        return self._dist(a, b) <= self.tolerancia_mm

    def _segmentos(self, pontos: List[PontoDXF]) -> List[SegmentoDXF]:
        pts = self._fechar_pontos(pontos)
        segmentos: List[SegmentoDXF] = []
        for a, b in zip(pts, pts[1:]):
            comprimento = self._dist(a, b)
            if comprimento <= self.tolerancia_mm:
                continue
            segmentos.append(
                SegmentoDXF(
                    tipo="GEOMETRIA",
                    x1=a.x,
                    y1=a.y,
                    x2=b.x,
                    y2=b.y,
                    comprimento_mm=comprimento,
                )
            )
        return segmentos

    def _extrair_contornos(self, geometrias: Iterable[List[PontoDXF]]) -> List[Dict[str, Any]]:
        contornos: List[Dict[str, Any]] = []

        for indice, pontos in enumerate(geometrias, start=1):
            if not self._contorno_fechado(pontos):
                continue

            area = self._area(pontos)
            if area <= 0.01:
                continue

            xmin, ymin, xmax, ymax = self._bbox(pontos)
            largura = xmax - xmin
            altura = ymax - ymin
            perimetro = self._perimetro(pontos)

            contornos.append(
                {
                    "indice": indice,
                    "pontos": [asdict(p) for p in pontos],
                    "segmentos": [asdict(s) for s in self._segmentos(pontos)],
                    "largura_mm": largura,
                    "altura_mm": altura,
                    "area_mm2": area,
                    "perimetro_mm": perimetro,
                    "fechado": True,
                }
            )

        contornos.sort(key=lambda c: c["area_mm2"], reverse=True)
        return contornos

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def analisar(self, caminho: str | Path) -> Dict[str, Any]:
        caminho = Path(caminho)
        if not caminho.is_file():
            raise FileNotFoundError(f"DXF não encontrado: {caminho}")

        try:
            import ezdxf
        except ImportError as exc:
            raise RuntimeError(
                "DEPENDENCIA_DXF_AUSENTE: instale ezdxf com "
                "'pip install ezdxf' e execute novamente."
            ) from exc

        try:
            doc = ezdxf.readfile(str(caminho))
        except Exception as exc:
            raise RuntimeError(f"ERRO_LEITURA_DXF: {exc}") from exc

        geometrias = self._coletar_entidades(doc)
        contornos = self._extrair_contornos(geometrias)

        if not contornos:
            return {
                "status": "ERRO",
                "erro": "NENHUM_CONTORNO_FECHADO_ENCONTRADO",
                "arquivo_dxf": str(caminho),
                "contornos": [],
                "contorno_principal": None,
            }

        principal = contornos[0]
        internos = contornos[1:]

        largura = float(principal["largura_mm"])
        altura = float(principal["altura_mm"])

        # O flat pattern pode estar rotacionado. A saída mantém as duas
        # dimensões, sempre como menor x maior para facilitar compra/corte.
        dimensao_a = min(largura, altura)
        dimensao_b = max(largura, altura)

        return {
            "status": "OK",
            "arquivo_dxf": str(caminho),
            "unidade_fonte": "MM",
            "dimensoes_fonte": "DXF",
            "tipo_geometria": "FLAT_PATTERN",
            "contornos_encontrados": len(contornos),
            "furos_contornos_internos": len(internos),
            "contorno_principal": principal,
            "contornos": contornos,
            "dimensao_x_mm": dimensao_a,
            "dimensao_y_mm": dimensao_b,
            "largura_blank_mm": dimensao_a,
            "comprimento_blank_mm": dimensao_b,
            "area_mm2": float(principal["area_mm2"]),
            "perimetro_mm": float(principal["perimetro_mm"]),
            "blank": {
                "largura_mm": dimensao_a,
                "comprimento_mm": dimensao_b,
            },
            "blank_status": "CALCULADO_PELO_DXF",
            "blank_origem": "DXF_GEOMETRIA",
        }


def extrair_dxf(caminho: str | Path) -> Dict[str, Any]:
    """Função de conveniência do extrator DXF."""
    return ExtratorDXF().analisar(caminho)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print("Uso: python -m app.engineering.extrator_dxf <arquivo.dxf>")
        raise SystemExit(2)

    resultado = extrair_dxf(sys.argv[1])
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
