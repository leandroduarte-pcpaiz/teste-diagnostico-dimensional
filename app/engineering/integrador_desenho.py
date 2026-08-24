# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.scanner.scanner import (
    localizar_pares_desenho,
)

from app.engineering.extrator_desenho import ExtratorDesenho
from app.engineering.extrator_dxf import ExtratorDXF


class IntegradorDesenho:
    """
    Integra PDF + DXF pertencentes ao mesmo desenho.

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
       RESULTADO UNIFICADO

    Regras de autoridade:

        GEOMETRIA:
            DXF > PDF

        INFORMAÇÕES TEXTUAIS / FABRICAÇÃO:
            PDF

    O integrador NÃO recalcula:
        - desenvolvimento de dobra;
        - bend allowance;
        - K-factor;
        - blank geométrico;
        - áreas;
        - perímetros.

    Quando existe DXF válido, a geometria efetiva do flat pattern
    vem diretamente do ExtratorDXF.

    O resultado mantém:
        - dados unificados em nível superior;
        - resultado completo do PDF;
        - resultado completo do DXF.

    Dessa forma, os módulos seguintes não precisam conhecer a
    implementação interna dos extratores.
    """

    def __init__(self) -> None:
        self.extrator_dxf = ExtratorDXF()

    # ==================================================================
    # UTILITÁRIOS
    # ==================================================================

    @staticmethod
    def _valor_positivo(valor: Any) -> bool:
        """Retorna True quando valor é numérico e maior que zero."""
        try:
            return float(valor) > 0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _extrair_primeiro(
        dados: Dict[str, Any],
        *chaves: str,
    ) -> Any:
        """Retorna o primeiro valor existente e não nulo."""
        for chave in chaves:
            valor = dados.get(chave)
            if valor is not None:
                return valor
        return None

    # ==================================================================
    # PDF
    # ==================================================================

    def _extrair_pdf(
        self,
        caminho_pdf: Optional[Path],
    ) -> Dict[str, Any]:

        if caminho_pdf is None:
            return {
                "status": "NAO_DISPONIVEL",
                "arquivo_pdf": None,
            }

        try:
            caminho_pdf = Path(caminho_pdf)

            extrator = ExtratorDesenho(caminho_pdf)
            dados = extrator.extrair()

            if not isinstance(dados, dict):
                raise TypeError(
                    "ExtratorDesenho.extrair() não retornou um dicionário."
                )

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

    # ==================================================================
    # DXF
    # ==================================================================

    def _extrair_dxf(
        self,
        caminho_dxf: Optional[Path],
    ) -> Dict[str, Any]:

        if caminho_dxf is None:
            return {
                "status": "NAO_DISPONIVEL",
                "arquivo_dxf": None,
            }

        try:
            caminho_dxf = Path(caminho_dxf)

            dados = self.extrator_dxf.analisar(caminho_dxf)

            if not isinstance(dados, dict):
                raise TypeError(
                    "ExtratorDXF.analisar() não retornou um dicionário."
                )

            # Garante que o caminho do arquivo exista no resultado,
            # mesmo que o extrator não o tenha incluído.
            dados.setdefault(
                "arquivo_dxf",
                str(caminho_dxf),
            )

            return dados

        except Exception as exc:
            return {
                "status": "ERRO",
                "arquivo_dxf": str(caminho_dxf),
                "erro": str(exc),
            }

    # ==================================================================
    # GEOMETRIA DXF
    # ==================================================================

    def _geometria_dxf(
        self,
        dados_dxf: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extrai somente informações geométricas já calculadas pelo DXF.

        Nenhum cálculo geométrico novo é realizado aqui.
        """

        return {
            "largura_blank_mm": self._extrair_primeiro(
                dados_dxf,
                "largura_blank_mm",
            ),
            "comprimento_blank_mm": self._extrair_primeiro(
                dados_dxf,
                "comprimento_blank_mm",
            ),
            "dimensao_x_mm": self._extrair_primeiro(
                dados_dxf,
                "dimensao_x_mm",
            ),
            "dimensao_y_mm": self._extrair_primeiro(
                dados_dxf,
                "dimensao_y_mm",
            ),
            "area_mm2": self._extrair_primeiro(
                dados_dxf,
                "area_mm2",
            ),
            "area_bruta_mm2": self._extrair_primeiro(
                dados_dxf,
                "area_bruta_mm2",
                "area_mm2",
            ),
            "area_furos_mm2": self._extrair_primeiro(
                dados_dxf,
                "area_furos_mm2",
            ),
            "area_liquida_mm2": self._extrair_primeiro(
                dados_dxf,
                "area_liquida_mm2",
            ),
            "perimetro_mm": self._extrair_primeiro(
                dados_dxf,
                "perimetro_mm",
            ),
            "blank_status": self._extrair_primeiro(
                dados_dxf,
                "blank_status",
            ),
            "blank_origem": self._extrair_primeiro(
                dados_dxf,
                "blank_origem",
            ),
            "blank_dxf": self._extrair_primeiro(
                dados_dxf,
                "blank",
            ),
            "contornos": self._extrair_primeiro(
                dados_dxf,
                "contornos",
            ),
            "furos": self._extrair_primeiro(
                dados_dxf,
                "furos",
            ),
            "geometrias": self._extrair_primeiro(
                dados_dxf,
                "geometrias",
            ),
            "entidades": self._extrair_primeiro(
                dados_dxf,
                "entidades",
            ),
        }

    # ==================================================================
    # GEOMETRIA PDF
    # ==================================================================

    def _geometria_pdf(
        self,
        dados_pdf: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Obtém as dimensões geométricas fornecidas pelo PDF.

        O PDF somente é utilizado como fallback quando não existe
        geometria DXF válida.
        """

        dimensoes = dados_pdf.get(
            "dimensoes_geometricas_mm",
            [],
        )

        if not isinstance(dimensoes, (list, tuple)):
            dimensoes = []

        valores: List[float] = []

        for valor in dimensoes:
            try:
                numero = float(valor)
            except (TypeError, ValueError):
                continue

            if numero > 0:
                valores.append(numero)

        if len(valores) < 2:
            return {
                "largura_blank_mm": None,
                "comprimento_blank_mm": None,
                "area_mm2": None,
                "perimetro_mm": None,
            }

        largura = min(valores[0], valores[1])
        comprimento = max(valores[0], valores[1])

        return {
            "largura_blank_mm": largura,
            "comprimento_blank_mm": comprimento,
            "area_mm2": None,
            "perimetro_mm": None,
        }

    # ==================================================================
    # INTEGRAÇÃO
    # ==================================================================

    def integrar_par(
        self,
        par: Dict[str, Optional[Path]],
    ) -> Dict[str, Any]:

        caminho_pdf = par.get("pdf")
        caminho_dxf = par.get("dxf")

        dados_pdf = self._extrair_pdf(caminho_pdf)
        dados_dxf = self._extrair_dxf(caminho_dxf)

        # --------------------------------------------------------------
        # IDENTIFICAÇÃO
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

        if not isinstance(dobras, list):
            dobras = []

        # --------------------------------------------------------------
        # VALIDADE DAS FONTES
        # --------------------------------------------------------------

        dxf_ok = dados_dxf.get("status") == "OK"
        pdf_ok = dados_pdf.get("status") == "OK"

        # --------------------------------------------------------------
        # GEOMETRIA DXF
        # --------------------------------------------------------------

        geometria_dxf = self._geometria_dxf(
            dados_dxf
        )

        largura_blank_mm = geometria_dxf[
            "largura_blank_mm"
        ]

        comprimento_blank_mm = geometria_dxf[
            "comprimento_blank_mm"
        ]

        area_mm2 = geometria_dxf[
            "area_mm2"
        ]

        area_bruta_mm2 = geometria_dxf[
            "area_bruta_mm2"
        ]

        area_furos_mm2 = geometria_dxf[
            "area_furos_mm2"
        ]

        area_liquida_mm2 = geometria_dxf[
            "area_liquida_mm2"
        ]

        perimetro_mm = geometria_dxf[
            "perimetro_mm"
        ]

        blank_status = geometria_dxf[
            "blank_status"
        ]

        blank_origem = geometria_dxf[
            "blank_origem"
        ]

        # --------------------------------------------------------------
        # VALIDAÇÃO GEOMÉTRICA DXF
        # --------------------------------------------------------------

        dxf_geometria_valida = (
            dxf_ok
            and self._valor_positivo(largura_blank_mm)
            and self._valor_positivo(comprimento_blank_mm)
        )

        # --------------------------------------------------------------
        # FALLBACK PDF
        # --------------------------------------------------------------

        if not dxf_geometria_valida:

            geometria_pdf = self._geometria_pdf(
                dados_pdf
            )

            largura_blank_mm = geometria_pdf[
                "largura_blank_mm"
            ]

            comprimento_blank_mm = geometria_pdf[
                "comprimento_blank_mm"
            ]

            # O PDF não fornece automaticamente as mesmas grandezas
            # geométricas do DXF.
            area_mm2 = None
            area_bruta_mm2 = None
            area_furos_mm2 = None
            area_liquida_mm2 = None
            perimetro_mm = None

            blank_status = (
                "CALCULADO_PELO_PDF"
                if (
                    self._valor_positivo(
                        largura_blank_mm
                    )
                    and self._valor_positivo(
                        comprimento_blank_mm
                    )
                )
                else None
            )

            blank_origem = (
                "PDF_GEOMETRIA"
                if blank_status is not None
                else None
            )

            geometria_fonte = (
                "PDF"
                if blank_status is not None
                else None
            )

        else:

            geometria_fonte = "DXF"

        # --------------------------------------------------------------
        # STATUS DA GEOMETRIA
        # --------------------------------------------------------------

        if dxf_geometria_valida:
            status_geometria = "OK_DXF"

        elif (
            pdf_ok
            and self._valor_positivo(largura_blank_mm)
            and self._valor_positivo(comprimento_blank_mm)
        ):
            status_geometria = "OK_PDF"

        elif dxf_ok:
            status_geometria = "DXF_SEM_BLANK_VALIDO"

        elif pdf_ok:
            status_geometria = "PDF_SEM_GEOMETRIA_VALIDO"

        else:
            status_geometria = "ERRO"

        # --------------------------------------------------------------
        # BLANK UNIFICADO
        # --------------------------------------------------------------

        blank_valido = (
            self._valor_positivo(largura_blank_mm)
            and self._valor_positivo(comprimento_blank_mm)
        )

        blank = {
            "largura_mm": largura_blank_mm,
            "comprimento_mm": comprimento_blank_mm,
            "origem": blank_origem,
            "status": blank_status,
            "valido": blank_valido,
        }

        # --------------------------------------------------------------
        # GEOMETRIA UNIFICADA
        # --------------------------------------------------------------

        geometria = {
            "fonte": geometria_fonte,
            "status": status_geometria,

            "dimensao_x_mm": geometria_dxf.get(
                "dimensao_x_mm"
            )
            if dxf_geometria_valida
            else None,

            "dimensao_y_mm": geometria_dxf.get(
                "dimensao_y_mm"
            )
            if dxf_geometria_valida
            else None,

            "largura_blank_mm": largura_blank_mm,

            "comprimento_blank_mm": comprimento_blank_mm,

            "area_mm2": area_mm2,

            "area_bruta_mm2": area_bruta_mm2,

            "area_furos_mm2": area_furos_mm2,

            "area_liquida_mm2": area_liquida_mm2,

            "perimetro_mm": perimetro_mm,

            "blank_status": blank_status,

            "blank_origem": blank_origem,

            "blank": blank,

            "contornos": (
                geometria_dxf.get("contornos")
                if dxf_geometria_valida
                else None
            ),

            "furos": (
                geometria_dxf.get("furos")
                if dxf_geometria_valida
                else None
            ),

            "geometrias": (
                geometria_dxf.get("geometrias")
                if dxf_geometria_valida
                else None
            ),

            "entidades": (
                geometria_dxf.get("entidades")
                if dxf_geometria_valida
                else None
            ),
        }

        # --------------------------------------------------------------
        # STATUS GERAL
        # --------------------------------------------------------------

        if dxf_ok or pdf_ok:
            status = "OK"
        else:
            status = "ERRO"

        # --------------------------------------------------------------
        # RESULTADO UNIFICADO
        # --------------------------------------------------------------

        resultado: Dict[str, Any] = {

            "status": status,

            "arquivo_base": (
                str(par.get("base"))
                if par.get("base") is not None
                else None
            ),

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

            "area_bruta_mm2": area_bruta_mm2,

            "area_furos_mm2": area_furos_mm2,

            "area_liquida_mm2": area_liquida_mm2,

            "perimetro_mm": perimetro_mm,

            "blank_status": blank_status,

            "blank_origem": blank_origem,

            "blank": blank,

            "geometria": geometria,

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
        }

        return resultado

    # ==================================================================
    # ENTRADA POR ARQUIVO / PASTA
    # ==================================================================

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
        # PASTA
        # --------------------------------------------------------------

        if caminho.is_dir():

            pares = localizar_pares_desenho(
                caminho
            )

            resultados: List[Dict[str, Any]] = []

            for par in pares:
                resultados.append(
                    self.integrar_par(par)
                )

            return resultados

        # --------------------------------------------------------------
        # ARQUIVO INDIVIDUAL
        # --------------------------------------------------------------

        extensao = caminho.suffix.lower()

        if extensao not in {".pdf", ".dxf"}:
            raise ValueError(
                "Formato não suportado. "
                "Use PDF, DXF ou uma pasta."
            )

        # --------------------------------------------------------------
        # PROCURA PAR
        # --------------------------------------------------------------

        pares = localizar_pares_desenho(
            caminho.parent
        )

        base = caminho.with_suffix("").resolve()

        par_encontrado: Optional[
            Dict[str, Optional[Path]]
        ] = None

        for par in pares:

            base_par = par.get("base")

            if base_par is None:
                continue

            try:
                base_par_resolvida = Path(
                    base_par
                ).resolve()
            except Exception:
                continue

            if base_par_resolvida == base:

                par_encontrado = par
                break

        # --------------------------------------------------------------
        # PAR NÃO LOCALIZADO
        # --------------------------------------------------------------

        if par_encontrado is None:

            par_encontrado = {
                "base": base,

                "pdf": (
                    caminho
                    if extensao == ".pdf"
                    else None
                ),

                "dxf": (
                    caminho
                    if extensao == ".dxf"
                    else None
                ),
            }

        return [
            self.integrar_par(
                par_encontrado
            )
        ]


# ======================================================================
# RESUMO DE TERMINAL
# ======================================================================

def _imprimir_resumo(
    resultado: Dict[str, Any],
) -> None:

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
        ("Área bruta (mm²)", "area_bruta_mm2"),
        ("Área furos (mm²)", "area_furos_mm2"),
        ("Área líquida (mm²)", "area_liquida_mm2"),
        ("Perímetro (mm)", "perimetro_mm"),
        ("Arquivo PDF", "arquivo_pdf"),
        ("Arquivo DXF", "arquivo_dxf"),
    ]

    for titulo, chave in campos:

        print(
            f"{titulo:<28}: "
            f"{resultado.get(chave)}"
        )

    dobras = resultado.get("dobras") or []

    furos = resultado.get("furos")

    if furos is None:
        dxf = resultado.get("dxf") or {}
        furos = dxf.get("furos")

    quantidade_furos = (
        len(furos)
        if isinstance(furos, list)
        else 0
    )

    print(
        f"{'Dobras encontradas':<28}: "
        f"{len(dobras)}"
    )

    print(
        f"{'Furos/recortes identificados':<28}: "
        f"{quantidade_furos}"
    )

    blank = resultado.get("blank") or {}

    print(
        f"{'Blank válido':<28}: "
        f"{blank.get('valido')}"
    )

    print("=" * 80)


# ======================================================================
# JSON RESUMIDO
# ======================================================================

def _gerar_saida_json(
    resultado: Dict[str, Any],
) -> str:
    """
    Mantém o JSON completo disponível quando solicitado pelo programa,
    mas o resumo do terminal não precisa despejar toda a geometria.
    """

    return json.dumps(
        resultado,
        ensure_ascii=False,
        indent=2,
    )


# ======================================================================
# MAIN
# ======================================================================

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

    caminho = Path(
        sys.argv[1]
    )

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
            print(
                "JSON COMPLETO:"
            )

            print(
                _gerar_saida_json(
                    resultado
                )
            )

        return 0

    except Exception as exc:

        print()
        print(
            "ERRO NA INTEGRAÇÃO:"
        )
        print(
            str(exc)
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())