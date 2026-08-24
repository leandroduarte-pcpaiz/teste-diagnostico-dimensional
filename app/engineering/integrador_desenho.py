# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.scanner.scanner import (
    localizar_pares_desenho,
    selecionar_fonte_geometrica,
)

from app.engineering.extrator_desenho import ExtratorDesenho
from app.engineering.extrator_dxf import ExtratorDXF


class IntegradorDesenho:
    """
    Integra PDF + DXF de um mesmo desenho.

    Arquitetura:

        SCANNER
           |
           +---- PDF ----> ExtratorDesenho
           |
           +---- DXF ----> ExtratorDXF
           |
           v
       INTEGRADOR
           |
           v
       resultado unificado

    Prioridade:

        GEOMETRIA:
            DXF > PDF

        INFORMAÇÕES TEXTUAIS/FABRICAÇÃO:
            PDF

    O integrador não recalcula desenvolvimento de dobra.
    Se existir DXF, suas dimensões são tratadas como geometria
    efetiva do flat pattern.
    """

    def __init__(self) -> None:
        self.extrator_dxf = ExtratorDXF()

    # ------------------------------------------------------------------
    # PDF
    # ------------------------------------------------------------------

    def _extrair_pdf(self, caminho_pdf: Optional[Path]) -> Dict[str, Any]:
        if caminho_pdf is None:
            return {
                "status": "NAO_DISPONIVEL",
                "arquivo_pdf": None,
            }

        try:
            extrator = ExtratorDesenho(caminho_pdf)
            dados = extrator.extrair()

            return {
                "status": "OK",
                "arquivo_pdf": str(caminho_pdf),
                **dados,
            }

        except Exception as exc:
            return {
                "status": "ERRO",
                "arquivo_pdf": str(caminho_pdf),
                "erro": str(exc),
            }

    # ------------------------------------------------------------------
    # DXF
    # ------------------------------------------------------------------

    def _extrair_dxf(self, caminho_dxf: Optional[Path]) -> Dict[str, Any]:
        if caminho_dxf is None:
            return {
                "status": "NAO_DISPONIVEL",
                "arquivo_dxf": None,
            }

        try:
            dados = self.extrator_dxf.analisar(caminho_dxf)
            return dados

        except Exception as exc:
            return {
                "status": "ERRO",
                "arquivo_dxf": str(caminho_dxf),
                "erro": str(exc),
            }

    # ------------------------------------------------------------------
    # Integração
    # ------------------------------------------------------------------

    def integrar_par(
        self,
        par: Dict[str, Optional[Path]],
    ) -> Dict[str, Any]:

        caminho_pdf = par.get("pdf")
        caminho_dxf = par.get("dxf")

        dados_pdf = self._extrair_pdf(caminho_pdf)
        dados_dxf = self._extrair_dxf(caminho_dxf)

        # --------------------------------------------------------------
        # Identificação
        # --------------------------------------------------------------

        codigo_peca = dados_pdf.get("codigo_peca")

        if not codigo_peca:
            codigo_peca = (
                caminho_dxf.stem
                if caminho_dxf is not None
                else (
                    caminho_pdf.stem
                    if caminho_pdf is not None
                    else None
                )
            )

        descricao = dados_pdf.get("descricao")
        materia_prima = dados_pdf.get("materia_prima")
        material = dados_pdf.get("material")
        espessura_mm = dados_pdf.get("espessura_mm")
        peso_kg = dados_pdf.get("peso_kg")
        unidade = dados_pdf.get("unidade")
        dobras = dados_pdf.get("dobras", [])

        # --------------------------------------------------------------
        # Geometria
        # --------------------------------------------------------------

        geometria_fonte = None
        largura_blank_mm = None
        comprimento_blank_mm = None
        area_mm2 = None
        perimetro_mm = None

        if dados_dxf.get("status") == "OK":

            geometria_fonte = "DXF"

            largura_blank_mm = dados_dxf.get(
                "largura_blank_mm"
            )

            comprimento_blank_mm = dados_dxf.get(
                "comprimento_blank_mm"
            )

            area_mm2 = dados_dxf.get(
                "area_mm2"
            )

            perimetro_mm = dados_dxf.get(
                "perimetro_mm"
            )

        elif dados_pdf.get("status") == "OK":

            geometria_fonte = "PDF"

            dimensoes = dados_pdf.get(
                "dimensoes_geometricas_mm",
                [],
            )

            if len(dimensoes) >= 2:
                largura_blank_mm = min(
                    dimensoes[0],
                    dimensoes[1],
                )

                comprimento_blank_mm = max(
                    dimensoes[0],
                    dimensoes[1],
                )

        # --------------------------------------------------------------
        # Status geral
        # --------------------------------------------------------------

        if dados_dxf.get("status") == "OK":
            status_geometria = "OK_DXF"

        elif dados_pdf.get("status") == "OK":
            status_geometria = "OK_PDF"

        else:
            status_geometria = "ERRO"

        # --------------------------------------------------------------
        # Resultado unificado
        # --------------------------------------------------------------

        resultado = {
            "status": "OK",

            "arquivo_base": str(par.get("base"))
            if par.get("base") is not None
            else None,

            "codigo_peca": codigo_peca,

            "descricao": descricao,

            "materia_prima": materia_prima,

            "material": material,

            "espessura_mm": espessura_mm,

            "peso_kg": peso_kg,

            "unidade": unidade,

            "dobras": dobras,

            # ----------------------------------------------------------
            # GEOMETRIA
            # ----------------------------------------------------------

            "geometria_fonte": geometria_fonte,

            "status_geometria": status_geometria,

            "largura_blank_mm": largura_blank_mm,

            "comprimento_blank_mm": comprimento_blank_mm,

            "area_mm2": area_mm2,

            "perimetro_mm": perimetro_mm,

            # ----------------------------------------------------------
            # ARQUIVOS
            # ----------------------------------------------------------

            "arquivo_pdf": dados_pdf.get(
                "arquivo_pdf"
            ),

            "arquivo_dxf": dados_dxf.get(
                "arquivo_dxf"
            ),

            # ----------------------------------------------------------
            # FONTES COMPLETAS
            # ----------------------------------------------------------

            "pdf": dados_pdf,

            "dxf": dados_dxf,

            # ----------------------------------------------------------
            # BLANK
            # ----------------------------------------------------------

            "blank": {
                "largura_mm": largura_blank_mm,
                "comprimento_mm": comprimento_blank_mm,
                "origem": (
                    "DXF_GEOMETRIA"
                    if geometria_fonte == "DXF"
                    else "PDF_GEOMETRIA"
                    if geometria_fonte == "PDF"
                    else None
                ),
                "valido": (
                    largura_blank_mm is not None
                    and comprimento_blank_mm is not None
                    and largura_blank_mm > 0
                    and comprimento_blank_mm > 0
                ),
            },
        }

        return resultado

    # ------------------------------------------------------------------
    # Entrada por arquivo
    # ------------------------------------------------------------------

    def integrar_arquivo(
        self,
        caminho: str | Path,
    ) -> List[Dict[str, Any]]:

        caminho = Path(caminho)

        if not caminho.exists():
            raise FileNotFoundError(
                f"Arquivo ou pasta não encontrado: {caminho}"
            )

        # --------------------------------------------------------------
        # Pasta
        # --------------------------------------------------------------

        if caminho.is_dir():

            pares = localizar_pares_desenho(caminho)

            resultados = []

            for par in pares:
                resultados.append(
                    self.integrar_par(par)
                )

            return resultados

        # --------------------------------------------------------------
        # Arquivo individual
        # --------------------------------------------------------------

        extensao = caminho.suffix.lower()

        if extensao not in {".pdf", ".dxf"}:
            raise ValueError(
                "Formato não suportado. "
                "Use PDF, DXF ou uma pasta."
            )

        # Localiza o par através da pasta do arquivo.
        pares = localizar_pares_desenho(
            caminho.parent
        )

        base = caminho.with_suffix("").resolve()

        par_encontrado = None

        for par in pares:

            if par.get("base") == base:

                par_encontrado = par
                break

        if par_encontrado is None:

            par_encontrado = {
                "base": base,
                "pdf": caminho
                if extensao == ".pdf"
                else None,
                "dxf": caminho
                if extensao == ".dxf"
                else None,
            }

        return [
            self.integrar_par(
                par_encontrado
            )
        ]


def _imprimir_resumo(resultado: Dict[str, Any]) -> None:

    print()
    print("=" * 80)
    print("RESULTADO DA INTEGRAÇÃO")
    print("=" * 80)

    campos = [
        ("Código da peça", "codigo_peca"),
        ("Descrição", "descricao"),
        ("Matéria-prima", "materia_prima"),
        ("Material", "material"),
        ("Espessura (mm)", "espessura_mm"),
        ("Peso (kg)", "peso_kg"),
        ("Unidade", "unidade"),
        ("Geometria fonte", "geometria_fonte"),
        ("Status geometria", "status_geometria"),
        ("Largura blank (mm)", "largura_blank_mm"),
        ("Comprimento blank (mm)", "comprimento_blank_mm"),
        ("Área (mm²)", "area_mm2"),
        ("Perímetro (mm)", "perimetro_mm"),
        ("Arquivo PDF", "arquivo_pdf"),
        ("Arquivo DXF", "arquivo_dxf"),
    ]

    for titulo, chave in campos:
        print(
            f"{titulo:<28}: "
            f"{resultado.get(chave)}"
        )

    print(
        f"Dobras encontradas{'':<9}: "
        f"{len(resultado.get('dobras') or [])}"
    )

    print("=" * 80)


def main() -> int:

    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("INTEGRADOR DE DESENHO PDF + DXF")
    print("=" * 80)

    if len(sys.argv) != 2:

        print()
        print("Uso:")
        print(
            "python -m app.engineering.integrador_desenho "
            "<arquivo.pdf|arquivo.dxf|pasta>"
        )

        return 2

    caminho = Path(sys.argv[1])

    try:

        integrador = IntegradorDesenho()

        resultados = integrador.integrar_arquivo(
            caminho
        )

        if not resultados:

            print()
            print(
                "Nenhum desenho PDF/DXF encontrado."
            )

            return 1

        for resultado in resultados:

            _imprimir_resumo(
                resultado
            )

            print()
            print("JSON COMPLETO:")
            print(
                json.dumps(
                    resultado,
                    ensure_ascii=False,
                    indent=2,
                )
            )

        return 0

    except Exception as exc:

        print()
        print(
            "ERRO NA INTEGRAÇÃO:"
        )
        print(exc)

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
