# -*- coding: utf-8 -*-

from __future__ import annotations

from math import ceil
from pathlib import Path
from typing import Any, Dict, Optional


class CalculadoraCorte:
    """
    AIZI Engineering AI - CALCULADORA DE CORTE

    Calcula o aproveitamento de uma peça sobre uma chapa comercial.

    Para peças de chapa, o DXF e a fonte geometrica preferencial quando
    disponivel. O PDF pode fornecer material, espessura e demais dados de
    fabricacao, mas nao substitui a geometria do DXF.

    Se o DXF for um FLAT PATTERN, largura_blank_mm e
    comprimento_blank_mm sao usados diretamente como dimensoes efetivas
    de corte. Esta classe nao calcula desenvolvimento de dobra.
    """

    def __init__(
        self,
        codigo_peca: str,
        material: str,
        espessura_mm: float,
        largura_peca_mm: float,
        comprimento_peca_mm: float,
        quantidade: int,
        largura_chapa_mm: float,
        comprimento_chapa_mm: float,
        dimensoes_fonte: Optional[str] = None,
        dados_dxf: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.codigo_peca = str(codigo_peca)
        self.material = str(material)
        self.espessura_mm = float(espessura_mm)
        self.largura_peca_mm = float(largura_peca_mm)
        self.comprimento_peca_mm = float(comprimento_peca_mm)
        self.quantidade = int(quantidade)
        self.largura_chapa_mm = float(largura_chapa_mm)
        self.comprimento_chapa_mm = float(comprimento_chapa_mm)
        self.dimensoes_fonte = (
            str(dimensoes_fonte) if dimensoes_fonte is not None else None
        )
        self.dados_dxf = dict(dados_dxf) if isinstance(dados_dxf, dict) else None
        self._validar_dados()

    @classmethod
    def from_dxf(
        cls,
        codigo_peca: str,
        material: str,
        espessura_mm: float,
        quantidade: int,
        largura_chapa_mm: float,
        comprimento_chapa_mm: float,
        caminho_dxf: str | Path | None = None,
        dados_dxf: Optional[Dict[str, Any]] = None,
    ) -> "CalculadoraCorte":
        """Cria a calculadora usando o DXF como fonte das dimensoes do blank."""
        if dados_dxf is None:
            if caminho_dxf is None:
                raise ValueError("Informe caminho_dxf ou dados_dxf.")
            from app.engineering.extrator_dxf import extrair_dxf
            dados_dxf = extrair_dxf(caminho_dxf)

        if not isinstance(dados_dxf, dict):
            raise ValueError("dados_dxf deve ser um dicionario.")

        if dados_dxf.get("status") != "OK":
            raise ValueError(
                "DXF invalido para calculo de corte: "
                f"{dados_dxf.get('erro', 'erro desconhecido')}"
            )

        largura = dados_dxf.get("largura_blank_mm")
        comprimento = dados_dxf.get("comprimento_blank_mm")

        if largura is None or comprimento is None:
            blank = dados_dxf.get("blank")
            if isinstance(blank, dict):
                largura = blank.get("largura_mm")
                comprimento = blank.get("comprimento_mm")

        if largura is None or comprimento is None:
            raise ValueError(
                "O resultado do DXF nao contem largura_blank_mm e comprimento_blank_mm."
            )

        return cls(
            codigo_peca=codigo_peca,
            material=material,
            espessura_mm=espessura_mm,
            largura_peca_mm=float(largura),
            comprimento_peca_mm=float(comprimento),
            quantidade=quantidade,
            largura_chapa_mm=largura_chapa_mm,
            comprimento_chapa_mm=comprimento_chapa_mm,
            dimensoes_fonte="DXF_GEOMETRIA",
            dados_dxf=dados_dxf,
        )

    def _validar_dados(self) -> None:
        if self.quantidade < 0:
            raise ValueError("A quantidade da peca nao pode ser negativa.")
        if self.espessura_mm <= 0:
            raise ValueError("A espessura da peca deve ser maior que zero.")
        if self.largura_peca_mm <= 0:
            raise ValueError("A largura efetiva da peca deve ser maior que zero.")
        if self.comprimento_peca_mm <= 0:
            raise ValueError("O comprimento efetivo da peca deve ser maior que zero.")
        if self.largura_chapa_mm <= 0:
            raise ValueError("A largura da chapa deve ser maior que zero.")
        if self.comprimento_chapa_mm <= 0:
            raise ValueError("O comprimento da chapa deve ser maior que zero.")

    def calcular_por_orientacao(
        self,
        largura_peca_mm: float,
        comprimento_peca_mm: float,
    ) -> Dict[str, Any]:
        largura_peca_mm = float(largura_peca_mm)
        comprimento_peca_mm = float(comprimento_peca_mm)
        pecas_largura = int(self.largura_chapa_mm // largura_peca_mm)
        pecas_comprimento = int(self.comprimento_chapa_mm // comprimento_peca_mm)
        return {
            "largura_peca_mm": largura_peca_mm,
            "comprimento_peca_mm": comprimento_peca_mm,
            "pecas_largura": pecas_largura,
            "pecas_comprimento": pecas_comprimento,
            "quantidade_por_chapa": pecas_largura * pecas_comprimento,
        }

    def determinar_melhor_orientacao(self) -> Dict[str, Any]:
        orientacao_0 = self.calcular_por_orientacao(
            self.largura_peca_mm, self.comprimento_peca_mm
        )
        orientacao_90 = self.calcular_por_orientacao(
            self.comprimento_peca_mm, self.largura_peca_mm
        )
        if orientacao_90["quantidade_por_chapa"] > orientacao_0["quantidade_por_chapa"]:
            return {"orientacao": "90 graus", "dados": orientacao_90}
        return {"orientacao": "0 graus", "dados": orientacao_0}

    def calcular(self) -> Dict[str, Any]:
        melhor = self.determinar_melhor_orientacao()
        orientacao = melhor["orientacao"]
        dados = melhor["dados"]
        pecas_por_chapa = dados["quantidade_por_chapa"]

        if pecas_por_chapa <= 0:
            return self._resultado_erro("A peca nao cabe na chapa.")

        if self.quantidade == 0:
            chapas_necessarias = 0
            pecas_produzidas = 0
            pecas_sobrando = 0
        else:
            chapas_necessarias = ceil(self.quantidade / pecas_por_chapa)
            pecas_produzidas = chapas_necessarias * pecas_por_chapa
            pecas_sobrando = pecas_produzidas - self.quantidade

        area_peca_mm2 = self.largura_peca_mm * self.comprimento_peca_mm
        area_chapa_mm2 = self.largura_chapa_mm * self.comprimento_chapa_mm
        area_necessaria_mm2 = area_peca_mm2 * self.quantidade
        area_ocupada_corte_mm2 = area_peca_mm2 * pecas_por_chapa
        aproveitamento_chapa = (area_ocupada_corte_mm2 / area_chapa_mm2) * 100.0
        if chapas_necessarias > 0:
            aproveitamento_necessidade = (
                area_necessaria_mm2 / (area_chapa_mm2 * chapas_necessarias)
            ) * 100.0
        else:
            aproveitamento_necessidade = 0.0

        resultado = {
            "codigo_peca": self.codigo_peca,
            "material": self.material,
            "espessura_mm": self.espessura_mm,
            "largura_peca_mm": self.largura_peca_mm,
            "comprimento_peca_mm": self.comprimento_peca_mm,
            "dimensoes_fonte": self.dimensoes_fonte,
            "quantidade_necessaria": self.quantidade,
            "largura_chapa_mm": self.largura_chapa_mm,
            "comprimento_chapa_mm": self.comprimento_chapa_mm,
            "pecas_por_chapa": pecas_por_chapa,
            "chapas_necessarias": chapas_necessarias,
            "pecas_produzidas": pecas_produzidas,
            "pecas_sobrando": pecas_sobrando,
            "orientacao": orientacao,
            "pecas_largura": dados["pecas_largura"],
            "pecas_comprimento": dados["pecas_comprimento"],
            "area_peca_mm2": round(area_peca_mm2, 4),
            "area_chapa_mm2": round(area_chapa_mm2, 4),
            "area_necessaria_mm2": round(area_necessaria_mm2, 4),
            "area_ocupada_corte_mm2": round(area_ocupada_corte_mm2, 4),
            "aproveitamento_necessidade_percentual": round(aproveitamento_necessidade, 2),
            "aproveitamento_chapa_percentual": round(aproveitamento_chapa, 2),
            "erro": None,
        }

        if self.dados_dxf is not None:
            resultado.update({
                "geometria_fonte": "DXF",
                "blank_origem": self.dados_dxf.get("blank_origem", "DXF_GEOMETRIA"),
                "blank_status": self.dados_dxf.get("blank_status", "CALCULADO_PELO_DXF"),
                "arquivo_dxf": self.dados_dxf.get("arquivo_dxf"),
                "area_dxf_mm2": self.dados_dxf.get("area_mm2"),
                "perimetro_dxf_mm": self.dados_dxf.get("perimetro_mm"),
                "contornos_dxf": self.dados_dxf.get("contornos_encontrados"),
                "furos_contornos_internos_dxf": self.dados_dxf.get("furos_contornos_internos"),
            })
        else:
            resultado.update({
                "geometria_fonte": None,
                "blank_origem": None,
                "blank_status": None,
                "arquivo_dxf": None,
                "area_dxf_mm2": None,
                "perimetro_dxf_mm": None,
                "contornos_dxf": None,
                "furos_contornos_internos_dxf": None,
            })
        return resultado

    def _resultado_erro(self, mensagem: str) -> Dict[str, Any]:
        area_peca_mm2 = self.largura_peca_mm * self.comprimento_peca_mm
        area_chapa_mm2 = self.largura_chapa_mm * self.comprimento_chapa_mm
        area_necessaria_mm2 = area_peca_mm2 * self.quantidade
        return {
            "codigo_peca": self.codigo_peca,
            "material": self.material,
            "espessura_mm": self.espessura_mm,
            "largura_peca_mm": self.largura_peca_mm,
            "comprimento_peca_mm": self.comprimento_peca_mm,
            "dimensoes_fonte": self.dimensoes_fonte,
            "quantidade_necessaria": self.quantidade,
            "largura_chapa_mm": self.largura_chapa_mm,
            "comprimento_chapa_mm": self.comprimento_chapa_mm,
            "pecas_por_chapa": 0,
            "chapas_necessarias": None,
            "pecas_produzidas": 0,
            "pecas_sobrando": None,
            "orientacao": None,
            "pecas_largura": 0,
            "pecas_comprimento": 0,
            "area_peca_mm2": round(area_peca_mm2, 4),
            "area_chapa_mm2": round(area_chapa_mm2, 4),
            "area_necessaria_mm2": round(area_necessaria_mm2, 4),
            "area_ocupada_corte_mm2": 0,
            "aproveitamento_necessidade_percentual": 0.0,
            "aproveitamento_chapa_percentual": 0.0,
            "geometria_fonte": "DXF" if self.dados_dxf is not None else None,
            "blank_origem": self.dados_dxf.get("blank_origem") if self.dados_dxf else None,
            "blank_status": self.dados_dxf.get("blank_status") if self.dados_dxf else None,
            "arquivo_dxf": self.dados_dxf.get("arquivo_dxf") if self.dados_dxf else None,
            "area_dxf_mm2": self.dados_dxf.get("area_mm2") if self.dados_dxf else None,
            "perimetro_dxf_mm": self.dados_dxf.get("perimetro_mm") if self.dados_dxf else None,
            "contornos_dxf": self.dados_dxf.get("contornos_encontrados") if self.dados_dxf else None,
            "furos_contornos_internos_dxf": self.dados_dxf.get("furos_contornos_internos") if self.dados_dxf else None,
            "erro": mensagem,
        }


if __name__ == "__main__":
    import sys

    print("=" * 80)
    print("AIZI ENGINEERING AI")
    print("CALCULADORA DE CORTE")
    print("=" * 80)

    if len(sys.argv) != 2:
        print("Uso: python -m app.engineering.calculadora_corte <arquivo.dxf>")
        raise SystemExit(2)

    calculadora = CalculadoraCorte.from_dxf(
        codigo_peca="046",
        material="ACO_A36",
        espessura_mm=6.35,
        quantidade=1,
        largura_chapa_mm=2000.0,
        comprimento_chapa_mm=6000.0,
        caminho_dxf=sys.argv[1],
    )

    for chave, valor in calculadora.calcular().items():
        print(f"{chave:<45}: {valor}")

    print("=" * 80)
