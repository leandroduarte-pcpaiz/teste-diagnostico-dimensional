# -*- coding: utf-8 -*-

from __future__ import annotations

import tempfile
from pathlib import Path

import ezdxf

from app.engineering.extrator_dxf import extrair_dxf


def main() -> None:
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "teste_046.dxf"

        doc = ezdxf.new("R2010")
        doc.header["$INSUNITS"] = 4  # mm
        msp = doc.modelspace()

        pontos = [
            (0.0, 0.0),
            (163.0, 0.0),
            (163.0, 645.5988),
            (0.0, 645.5988),
        ]
        msp.add_lwpolyline(pontos, close=True)
        doc.saveas(caminho)

        resultado = extrair_dxf(caminho)

        assert resultado["status"] == "OK"
        assert resultado["blank_status"] == "CALCULADO_PELO_DXF"
        assert abs(resultado["largura_blank_mm"] - 163.0) < 0.01
        assert abs(resultado["comprimento_blank_mm"] - 645.5988) < 0.01
        assert abs(resultado["area_mm2"] - (163.0 * 645.5988)) < 1.0
        assert resultado["contornos_encontrados"] == 1

        print("TESTE DXF: OK")
        print(f"Blank: {resultado['largura_blank_mm']:.4f} x {resultado['comprimento_blank_mm']:.4f} mm")
        print(f"Área: {resultado['area_mm2']:.4f} mm²")
        print(f"Perímetro: {resultado['perimetro_mm']:.4f} mm")


if __name__ == "__main__":
    main()
