from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional

import pandas as pd


class PlanejadorDimensional:
    """
    Planejador dimensional do AIZI Engineering AI.

    Responsabilidade:
    -----------------
    Identificar características dimensionais de materiais
    e preparar itens para a Calculadora de Corte.

    Também possui a etapa de desenvolvimento geométrico de
    peças de chapa dobrada extraídas de desenho técnico.

    NÃO calcula:
        - estoque;
        - necessidade líquida;
        - compras;
        - saldo;
        - reservas.

    Categorias:
        CHAPA
        TUBO
        BARRA
        PERFIL
        NAO_APLICAVEL

    Fluxo principal:

        PlanejadorDimensional(df)
                    |
                    v
                analisar()
                    |
                    v
        DataFrame dimensional
                    |
                    v
        preparar_medidas_compra()

    Fluxo para desenho técnico:

        ExtratorDesenho
              |
              v
        dados estruturados
              |
              v
        analisar_peca_extraida()
              |
              v
        calcular_desenvolvimento_chapa()
              |
              v
        determinar_blank()
              |
              v
        BLANK
    """

    CATEGORIAS_DIMENSIONAIS = {
        "CHAPA",
        "TUBO",
        "BARRA",
        "PERFIL",
    }

    COMPRIMENTO_PADRAO_TUBO_MM = 6000.0

    COMPRIMENTO_PADRAO_BARRA_MM = 6000.0

    PADROES_COMERCIAIS_CHAPA = [
        (1000.0, 2000.0),
        (1200.0, 2000.0),
        (1200.0, 3000.0),
        (1500.0, 3000.0),
        (1500.0, 6000.0),
        (2000.0, 6000.0),
    ]

    # ----------------------------------------------------------
    # PARÂMETROS PADRÃO DE DESENVOLVIMENTO
    # ----------------------------------------------------------

    # Valor operacional inicial.
    #
    # K representa a posição da linha neutra dentro da
    # espessura da chapa:
    #
    # linha neutra = K * espessura
    #
    # O valor 0.34 é mantido como padrão inicial para chapas
    # metálicas dobradas.
    #
    # Este parâmetro poderá futuramente ser substituído por
    # uma tabela por material / espessura / raio.
    K_FACTOR_PADRAO = 0.34

    ANGULO_DOBRA_PADRAO_GRAUS = 90.0

    # ----------------------------------------------------------
    # TOLERÂNCIAS
    # ----------------------------------------------------------

    TOLERANCIA_NUMERICA = 0.0001

    def __init__(self, df: Optional[pd.DataFrame] = None):
        """
        Inicializa o PlanejadorDimensional.

        O DataFrame recebido é preservado internamente.
        """

        self.df = (
            df.copy()
            if isinstance(df, pd.DataFrame)
            else pd.DataFrame()
        )

    # ==========================================================
    # ANÁLISE PRINCIPAL
    # ==========================================================

    def analisar(self) -> pd.DataFrame:
        """
        Executa a análise dimensional do DataFrame recebido
        na inicialização do objeto.

        Importante:
        ----------
        - preserva todos os itens recebidos;
        - preserva as quantidades;
        - preserva as colunas originais;
        - adiciona/enriquece as informações dimensionais;
        - não faz qualquer cálculo de estoque;
        - não altera a quantidade necessária.
        """

        if self.df is None:
            self.df = pd.DataFrame()

        if self.df.empty:
            return self.df.copy()

        self.df = self.preparar_medidas_compra(
            self.df
        )

        return self.df.copy()

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _texto(valor: Any) -> str:
        """
        Converte valor para texto e remove resíduos comuns
        vindos do Excel/CSV.
        """

        if valor is None:
            return ""

        try:
            if pd.isna(valor):
                return ""
        except (TypeError, ValueError):
            pass

        texto = str(valor).strip()

        if texto.startswith('="') and texto.endswith('"'):
            texto = texto[2:-1]

        texto = texto.strip('"').strip()

        return texto.upper()

    @staticmethod
    def _numero(texto: Any) -> Optional[float]:
        """
        Converte números nos formatos:

            6,35       -> 6.35
            6.35       -> 6.35
            1.000,50   -> 1000.50
        """

        if texto is None:
            return None

        try:
            if pd.isna(texto):
                return None
        except (TypeError, ValueError):
            pass

        texto = str(texto).strip()

        if not texto:
            return None

        try:

            if "," in texto and "." in texto:

                texto = (
                    texto
                    .replace(".", "")
                    .replace(",", ".")
                )

            elif "," in texto:

                texto = texto.replace(",", ".")

            return float(texto)

        except (ValueError, TypeError):

            return None

    @classmethod
    def _extrair_numeros_mm(
        cls,
        texto: str,
    ):
        """
        Extrai números associados a MM.

        Exemplos:

            6,35MM
            33,40 X 26,64 X 3,38MM
            6000MM
        """

        texto = cls._texto(texto)

        padrao = (
            r"(\d+(?:[.,]\d+)?)"
            r"\s*MM"
        )

        encontrados = re.findall(
            padrao,
            texto,
        )

        return [
            cls._numero(x)
            for x in encontrados
        ]

    @classmethod
    def _extrair_tres_medidas(
        cls,
        texto: str,
    ):
        """
        Procura sequências do tipo:

            33,40 X 26,64 X 3,38MM

        Retorna:

            [33.40, 26.64, 3.38]
        """

        texto = cls._texto(texto)

        padrao = (
            r"(\d+(?:[.,]\d+)?)"
            r"\s*[Xx×]\s*"
            r"(\d+(?:[.,]\d+)?)"
            r"\s*[Xx×]\s*"
            r"(\d+(?:[.,]\d+)?)"
            r"\s*MM"
        )

        match = re.search(
            padrao,
            texto,
        )

        if not match:
            return None

        return [
            cls._numero(match.group(1)),
            cls._numero(match.group(2)),
            cls._numero(match.group(3)),
        ]

    @classmethod
    def _contem_codigo_produto(
        cls,
        texto: Any,
        prefixos=("G",),
    ) -> bool:
        """
        Verifica se um texto contém código de produto
        no padrão TOTVS.

        Exemplo:

            G2005887
        """

        texto = cls._texto(texto)

        if not texto:
            return False

        for prefixo in prefixos:

            padrao = (
                rf"\b{re.escape(prefixo)}\d{{7}}\b"
            )

            if re.search(
                padrao,
                texto,
                re.IGNORECASE,
            ):
                return True

        return False

    # ==========================================================
    # UTILITÁRIOS DE DESENVOLVIMENTO
    # ==========================================================

    @classmethod
    def _valor_angulo(
        cls,
        dobra: Any,
    ) -> Optional[float]:
        """
        Obtém o ângulo de uma dobra em graus.

        Aceita formatos como:

            {"angulo": 90}
            {"angulo_graus": 90}
            {"angle": 90}

        Também aceita diretamente um número.
        """

        if isinstance(dobra, (int, float)):

            return float(dobra)

        if not isinstance(dobra, dict):

            return None

        for chave in (
            "angulo",
            "angulo_graus",
            "angulo_deg",
            "angle",
            "graus",
        ):

            if chave in dobra:

                valor = cls._numero(
                    dobra.get(chave)
                )

                if valor is not None:
                    return valor

        return None

    @classmethod
    def _valor_raio(
        cls,
        dobra: Any,
    ) -> Optional[float]:
        """
        Obtém o raio interno da dobra.

        Aceita:

            raio
            raio_mm
            raio_interno
            raio_interno_mm
            r
        """

        if not isinstance(dobra, dict):

            return None

        for chave in (
            "raio",
            "raio_mm",
            "raio_interno",
            "raio_interno_mm",
            "r",
        ):

            if chave in dobra:

                valor = cls._numero(
                    dobra.get(chave)
                )

                if valor is not None:
                    return valor

        return None

    @classmethod
    def _valor_k(
        cls,
        dobra: Any,
        k_factor: Optional[float] = None,
    ) -> float:
        """
        Obtém o fator K.

        Prioridade:

            1. valor explícito da dobra;
            2. valor fornecido ao método;
            3. K_FACTOR_PADRAO.
        """

        if isinstance(dobra, dict):

            for chave in (
                "k_factor",
                "fator_k",
                "k",
            ):

                if chave in dobra:

                    valor = cls._numero(
                        dobra.get(chave)
                    )

                    if (
                        valor is not None
                        and 0.0 <= valor <= 1.0
                    ):

                        return valor

        if k_factor is not None:

            valor = cls._numero(
                k_factor
            )

            if (
                valor is not None
                and 0.0 <= valor <= 1.0
            ):

                return valor

        return cls.K_FACTOR_PADRAO

    @classmethod
    def _extrair_dimensoes_geometricas(
        cls,
        dados: Dict[str, Any],
    ) -> List[float]:
        """
        Normaliza dimensões geométricas extraídas do desenho.

        Exemplos:

            [672, 163]
            ["672", "163"]
            (672, 163)

        Também tenta localizar dimensões em campos alternativos.
        """

        if not dados:
            return []

        candidatos = [
            dados.get(
                "dimensoes_geometricas_mm"
            ),
            dados.get(
                "dimensoes_mm"
            ),
            dados.get(
                "dimensoes"
            ),
        ]

        for candidato in candidatos:

            if isinstance(
                candidato,
                (list, tuple),
            ):

                valores = []

                for item in candidato:

                    numero = cls._numero(
                        item
                    )

                    if numero is not None:
                        valores.append(
                            float(numero)
                        )

                if valores:
                    return valores

        return []

    # ==========================================================
    # IDENTIFICAÇÃO DO TIPO
    # ==========================================================

    @classmethod
    def identificar_tipo_dimensional(
        cls,
        descricao: Any,
        classificacao: Any = None,
        unidade_medida: Any = None,
    ) -> str:
        """
        Identifica o tipo dimensional através das informações
        disponíveis no cadastro/BOM.
        """

        descricao = cls._texto(descricao)
        classificacao = cls._texto(classificacao)
        unidade_medida = cls._texto(unidade_medida)

        texto = (
            f"{descricao} "
            f"{classificacao} "
            f"{unidade_medida}"
        )

        # CHAPA
        if (
            "CHAPA" in texto
            or re.search(
                r"\bCH\s+A[CÇ]O\b",
                texto,
                re.IGNORECASE,
            )
        ):
            return "CHAPA"

        # TUBO
        if "TUBO" in texto:
            return "TUBO"

        # BARRA
        if "BARRA" in texto:
            return "BARRA"

        # PERFIL
        if "PERFIL" in texto:
            return "PERFIL"

        return "NAO_APLICAVEL"

    # ==========================================================
    # IDENTIFICAÇÃO A PARTIR DE DESENHO
    # ==========================================================

    @classmethod
    def identificar_tipo_peca_extraida(
        cls,
        dados: Dict[str, Any],
    ) -> str:
        """
        Identifica o tipo dimensional de uma peça extraída
        de desenho técnico.
        """

        if not dados:
            return "NAO_APLICAVEL"

        descricao = cls._texto(
            dados.get("descricao")
            or dados.get("descricao_produto")
        )

        material = cls._texto(
            dados.get("material")
        )

        materia_prima = cls._texto(
            dados.get("materia_prima")
        )

        classificacao = cls._texto(
            dados.get("classificacao")
        )

        unidade = cls._texto(
            dados.get("unidade")
            or dados.get("unidade_medida")
        )

        texto = " ".join(
            [
                descricao,
                material,
                materia_prima,
                classificacao,
                unidade,
            ]
        )

        # ------------------------------------------------------
        # PRIMEIRO: REGRAS EXPLÍCITAS
        # ------------------------------------------------------

        tipo = cls.identificar_tipo_dimensional(
            descricao=descricao,
            classificacao=classificacao,
            unidade_medida=unidade,
        )

        if tipo != "NAO_APLICAVEL":
            return tipo

        # ------------------------------------------------------
        # MATERIAL DE CHAPA
        # ------------------------------------------------------

        padroes_chapa = [
            r"\bCH\s+A[CÇ]O\b",
            r"\bCHAPA\b",
            r"\bCH\s+INOX\b",
            r"\bCH\s+ALUMINIO\b",
            r"\bCH\s+ALUM[IÍ]NIO\b",
        ]

        for padrao in padroes_chapa:

            if re.search(
                padrao,
                texto,
                re.IGNORECASE,
            ):
                return "CHAPA"

        # ------------------------------------------------------
        # ESPESSURA + MATERIAL METÁLICO
        # ------------------------------------------------------

        espessura = dados.get(
            "espessura_mm"
        )

        tem_espessura = (
            cls._numero(espessura)
            is not None
        )

        material_chapa = (
            "AÇO" in texto
            or "ACO" in texto
            or "INOX" in texto
            or "ALUMINIO" in texto
            or "ALUMÍNIO" in texto
        )

        if (
            tem_espessura
            and material_chapa
        ):
            return "CHAPA"

        # ------------------------------------------------------
        # DOBRAS
        # ------------------------------------------------------

        dobras = dados.get(
            "dobras"
        )

        if isinstance(
            dobras,
            (list, tuple),
        ):

            if (
                len(dobras) > 0
                and tem_espessura
            ):

                return "CHAPA"

        # ------------------------------------------------------
        # TUBO
        # ------------------------------------------------------

        if "TUBO" in texto:
            return "TUBO"

        # ------------------------------------------------------
        # BARRA
        # ------------------------------------------------------

        if "BARRA" in texto:
            return "BARRA"

        # ------------------------------------------------------
        # PERFIL
        # ------------------------------------------------------

        if "PERFIL" in texto:
            return "PERFIL"

        return "NAO_APLICAVEL"

    # ==========================================================
    # CHAPA
    # ==========================================================

    @classmethod
    def analisar_chapa(
        cls,
        descricao: Any,
        espessura_fornecida: Any = None,
        material_fornecido: Any = None,
    ) -> Dict[str, Any]:
        """
        Analisa uma matéria-prima de chapa.

        As dimensões comerciais da chapa são dimensões
        da matéria-prima, e NÃO são automaticamente o BLANK
        da peça.
        """

        descricao = cls._texto(descricao)

        resultado = {
            "tipo_dimensional": "CHAPA",
            "material": None,
            "espessura_mm": None,
            "largura_padrao_mm": None,
            "comprimento_padrao_mm": None,
            "largura_efetiva_mm": None,
            "comprimento_efetivo_mm": None,
            "status_dimensional": "CHAPA SEM ESPESSURA",
        }

        # ------------------------------------------------------
        # MATERIAL
        # ------------------------------------------------------

        material_texto = cls._texto(
            material_fornecido
        )

        texto_material = (
            f"{descricao} {material_texto}"
        )

        if "A36" in texto_material:

            resultado["material"] = "ACO A36"

        elif "INOX" in texto_material:

            resultado["material"] = "ACO INOX"

        elif (
            "ALUMINIO" in texto_material
            or "ALUMÍNIO" in texto_material
        ):

            resultado["material"] = "ALUMINIO"

        elif material_texto:

            resultado["material"] = (
                material_texto
            )

        # ------------------------------------------------------
        # ESPESSURA
        # ------------------------------------------------------

        espessura = cls._numero(
            espessura_fornecida
        )

        if espessura is None:

            medidas = cls._extrair_numeros_mm(
                descricao
            )

            if medidas:

                espessura = medidas[-1]

        resultado["espessura_mm"] = (
            espessura
        )

        if (
            resultado["espessura_mm"]
            is None
        ):

            return resultado

        # ------------------------------------------------------
        # PADRÃO COMERCIAL
        # ------------------------------------------------------

        if cls.PADROES_COMERCIAIS_CHAPA:

            largura, comprimento = (
                cls.PADROES_COMERCIAIS_CHAPA[0]
            )

            resultado[
                "largura_padrao_mm"
            ] = largura

            resultado[
                "comprimento_padrao_mm"
            ] = comprimento

        resultado[
            "largura_efetiva_mm"
        ] = resultado[
            "largura_padrao_mm"
        ]

        resultado[
            "comprimento_efetivo_mm"
        ] = resultado[
            "comprimento_padrao_mm"
        ]

        resultado[
            "status_dimensional"
        ] = "CHAPA IDENTIFICADA"

        return resultado

    # ==========================================================
    # TUBO
    # ==========================================================

    @classmethod
    def analisar_tubo(
        cls,
        descricao: Any,
    ) -> Dict[str, Any]:

        descricao = cls._texto(
            descricao
        )

        resultado = {
            "tipo_dimensional": "TUBO",
            "diametro_externo_mm": None,
            "diametro_interno_mm": None,
            "espessura_mm": None,
            "comprimento_padrao_mm": (
                cls.COMPRIMENTO_PADRAO_TUBO_MM
            ),
            "largura_efetiva_mm": None,
            "comprimento_efetivo_mm": None,
            "status_dimensional": (
                "TUBO SEM DIMENSÕES"
            ),
        }

        # ------------------------------------------------------
        # 33,40 X 26,64 X 3,38MM
        # ------------------------------------------------------

        medidas = cls._extrair_tres_medidas(
            descricao
        )

        if medidas:

            resultado[
                "diametro_externo_mm"
            ] = medidas[0]

            resultado[
                "diametro_interno_mm"
            ] = medidas[1]

            resultado[
                "espessura_mm"
            ] = medidas[2]

            resultado[
                "comprimento_efetivo_mm"
            ] = (
                cls.COMPRIMENTO_PADRAO_TUBO_MM
            )

            resultado[
                "status_dimensional"
            ] = "TUBO IDENTIFICADO"

            return resultado

        # ------------------------------------------------------
        # DIAM EXT 10 X DIAM INT 07MM
        # ------------------------------------------------------

        padrao = (
            r"DIAM\s*EXT\s*"
            r"(\d+(?:[.,]\d+)?)"
            r"\s*X\s*"
            r"DIAM\s*INT\s*"
            r"(\d+(?:[.,]\d+)?)"
            r"\s*MM"
        )

        match = re.search(
            padrao,
            descricao,
        )

        if match:

            resultado[
                "diametro_externo_mm"
            ] = cls._numero(
                match.group(1)
            )

            resultado[
                "diametro_interno_mm"
            ] = cls._numero(
                match.group(2)
            )

            externo = resultado[
                "diametro_externo_mm"
            ]

            interno = resultado[
                "diametro_interno_mm"
            ]

            if (
                externo is not None
                and interno is not None
            ):

                resultado[
                    "espessura_mm"
                ] = round(
                    (externo - interno)
                    / 2.0,
                    4,
                )

            resultado[
                "comprimento_efetivo_mm"
            ] = (
                cls.COMPRIMENTO_PADRAO_TUBO_MM
            )

            resultado[
                "status_dimensional"
            ] = "TUBO IDENTIFICADO"

            return resultado

        # ------------------------------------------------------
        # 22,22 X 2,65 PAREDE
        # ------------------------------------------------------

        padrao = (
            r"(\d+(?:[.,]\d+)?)"
            r"\s*[Xx×]\s*"
            r"(\d+(?:[.,]\d+)?)"
            r"\s*(?:MM)?"
            r"\s*PAREDE"
        )

        match = re.search(
            padrao,
            descricao,
        )

        if match:

            resultado[
                "diametro_externo_mm"
            ] = cls._numero(
                match.group(1)
            )

            resultado[
                "espessura_mm"
            ] = cls._numero(
                match.group(2)
            )

            externo = resultado[
                "diametro_externo_mm"
            ]

            espessura = resultado[
                "espessura_mm"
            ]

            if (
                externo is not None
                and espessura is not None
            ):

                resultado[
                    "diametro_interno_mm"
                ] = round(
                    externo
                    - (2 * espessura),
                    4,
                )

            resultado[
                "comprimento_efetivo_mm"
            ] = (
                cls.COMPRIMENTO_PADRAO_TUBO_MM
            )

            resultado[
                "status_dimensional"
            ] = "TUBO IDENTIFICADO"

            return resultado

        return resultado

    # ==========================================================
    # BARRA
    # ==========================================================

    @classmethod
    def analisar_barra(
        cls,
        descricao: Any,
    ) -> Dict[str, Any]:

        descricao = cls._texto(
            descricao
        )

        resultado = {
            "tipo_dimensional": "BARRA",
            "bitola_mm": None,
            "comprimento_padrao_mm": (
                cls.COMPRIMENTO_PADRAO_BARRA_MM
            ),
            "largura_efetiva_mm": None,
            "comprimento_efetivo_mm": (
                cls.COMPRIMENTO_PADRAO_BARRA_MM
            ),
            "status_dimensional": (
                "BARRA SEM BITOLA"
            ),
        }

        medidas = cls._extrair_numeros_mm(
            descricao
        )

        if medidas:

            resultado[
                "bitola_mm"
            ] = medidas[-1]

            resultado[
                "status_dimensional"
            ] = "BARRA IDENTIFICADA"

        return resultado

    # ==========================================================
    # PERFIL
    # ==========================================================

    @classmethod
    def analisar_perfil(
        cls,
        descricao: Any,
    ) -> Dict[str, Any]:

        descricao = cls._texto(
            descricao
        )

        resultado = {
            "tipo_dimensional": "PERFIL",
            "comprimento_padrao_mm": None,
            "largura_efetiva_mm": None,
            "comprimento_efetivo_mm": None,
            "status_dimensional": (
                "PERFIL SEM COMPRIMENTO"
            ),
        }

        medidas = cls._extrair_numeros_mm(
            descricao
        )

        if medidas:

            comprimento = medidas[-1]

            resultado[
                "comprimento_padrao_mm"
            ] = comprimento

            resultado[
                "comprimento_efetivo_mm"
            ] = comprimento

            resultado[
                "status_dimensional"
            ] = "PERFIL IDENTIFICADO"

        return resultado

    # ==========================================================
    # ANÁLISE DE ITEM
    # ==========================================================

    @classmethod
    def analisar_item(
        cls,
        descricao: Any,
        classificacao: Any = None,
        unidade_medida: Any = None,
    ) -> Dict[str, Any]:

        tipo = cls.identificar_tipo_dimensional(
            descricao,
            classificacao,
            unidade_medida,
        )

        resultado = {
            "tipo_dimensional": tipo,
            "espessura_mm": None,
            "diametro_externo_mm": None,
            "diametro_interno_mm": None,
            "bitola_mm": None,
            "largura_padrao_mm": None,
            "comprimento_padrao_mm": None,
            "largura_efetiva_mm": None,
            "comprimento_efetivo_mm": None,
            "material": None,
            "status_dimensional": None,
            "preparado_para_corte": False,
        }

        if tipo == "CHAPA":

            dados = cls.analisar_chapa(
                descricao
            )

        elif tipo == "TUBO":

            dados = cls.analisar_tubo(
                descricao
            )

        elif tipo == "BARRA":

            dados = cls.analisar_barra(
                descricao
            )

        elif tipo == "PERFIL":

            dados = cls.analisar_perfil(
                descricao
            )

        else:

            resultado[
                "status_dimensional"
            ] = "ITEM COMERCIAL SEM CORTE"

            return resultado

        resultado.update(
            dados
        )

        resultado[
            "preparado_para_corte"
        ] = cls._pode_preparar_para_corte(
            resultado
        )

        return resultado

    # ==========================================================
    # ANÁLISE DE PEÇA EXTRAÍDA DO DESENHO
    # ==========================================================

    @classmethod
    def analisar_peca_extraida(
        cls,
        dados: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analisa uma peça proveniente do ExtratorDesenho.

        Agora também prepara os dados necessários para o
        desenvolvimento da peça dobrada.
        """

        if not dados:
            return {}

        descricao = (
            dados.get("descricao")
            or dados.get(
                "descricao_produto"
            )
            or ""
        )

        material = (
            dados.get("material")
            or ""
        )

        espessura = dados.get(
            "espessura_mm"
        )

        classificacao = (
            dados.get("classificacao")
        )

        unidade = (
            dados.get("unidade")
            or dados.get(
                "unidade_medida"
            )
        )

        tipo = cls.identificar_tipo_peca_extraida(
            dados
        )

        resultado = {
            "tipo_dimensional": tipo,
            "espessura_mm": None,
            "diametro_externo_mm": None,
            "diametro_interno_mm": None,
            "bitola_mm": None,
            "largura_padrao_mm": None,
            "comprimento_padrao_mm": None,
            "largura_efetiva_mm": None,
            "comprimento_efetivo_mm": None,
            "material": None,
            "status_dimensional": None,
            "preparado_para_corte": False,

            # Dados específicos do desenho
            "codigo_peca": dados.get(
                "codigo_peca"
            ),
            "materia_prima": dados.get(
                "materia_prima"
            ),
            "dimensoes_geometricas_mm": dados.get(
                "dimensoes_geometricas_mm"
            ),
            "dobras": dados.get(
                "dobras"
            ),

            # Controle explícito do BLANK
            "blank_determinado": False,
            "blank": None,

            # Dados de desenvolvimento
            "k_factor": None,
            "desenvolvimento_mm": None,
            "largura_blank_mm": None,
            "comprimento_blank_mm": None,
            "metodo_desenvolvimento": None,
            "bend_allowance_total_mm": None,
            "bend_deduction_total_mm": None,
            "quantidade_dobras": 0,
        }

        # ------------------------------------------------------
        # CHAPA
        # ------------------------------------------------------

        if tipo == "CHAPA":

            dados_chapa = cls.analisar_chapa(
                descricao=material,
                espessura_fornecida=espessura,
                material_fornecido=material,
            )

            resultado.update(
                dados_chapa
            )

            if material:

                resultado[
                    "material"
                ] = cls._normalizar_material_desenho(
                    material
                )

            if espessura is not None:

                resultado[
                    "espessura_mm"
                ] = cls._numero(
                    espessura
                )

        elif tipo == "TUBO":

            dados_tubo = cls.analisar_tubo(
                descricao
            )

            resultado.update(
                dados_tubo
            )

        elif tipo == "BARRA":

            dados_barra = cls.analisar_barra(
                descricao
            )

            resultado.update(
                dados_barra
            )

        elif tipo == "PERFIL":

            dados_perfil = cls.analisar_perfil(
                descricao
            )

            resultado.update(
                dados_perfil
            )

        else:

            resultado[
                "status_dimensional"
            ] = "PEÇA SEM TIPO DIMENSIONAL"

        # ------------------------------------------------------
        # DOBRAS
        # ------------------------------------------------------

        dobras = dados.get(
            "dobras"
        )

        if isinstance(
            dobras,
            (list, tuple),
        ):

            resultado[
                "quantidade_dobras"
            ] = len(dobras)

        else:

            resultado[
                "quantidade_dobras"
            ] = 0

        # ------------------------------------------------------
        # DIMENSÕES DO DESENHO
        # ------------------------------------------------------

        resultado[
            "dimensoes_geometricas_mm"
        ] = cls._extrair_dimensoes_geometricas(
            dados
        )

        # ------------------------------------------------------
        # PREPARAÇÃO PARA CORTE
        # ------------------------------------------------------

        resultado[
            "preparado_para_corte"
        ] = cls._pode_preparar_para_corte(
            resultado
        )

        # ------------------------------------------------------
        # DESENVOLVIMENTO AUTOMÁTICO DA CHAPA
        # ------------------------------------------------------

        if tipo == "CHAPA":

            desenvolvimento = (
                cls.calcular_desenvolvimento_chapa(
                    resultado
                )
            )

            if desenvolvimento:

                resultado.update(
                    desenvolvimento
                )

                resultado[
                    "blank"
                ] = {
                    "largura_mm": desenvolvimento[
                        "largura_blank_mm"
                    ],
                    "comprimento_mm": desenvolvimento[
                        "comprimento_blank_mm"
                    ],
                }

                resultado[
                    "blank_determinado"
                ] = True

                resultado[
                    "status_dimensional"
                ] = "CHAPA COM BLANK CALCULADO"

        # ------------------------------------------------------
        # CONTEXTO DA EXTRAÇÃO
        # ------------------------------------------------------

        resultado[
            "dados_extracao"
        ] = dados

        return resultado

    # ==========================================================
    # NORMALIZAÇÃO DE MATERIAL
    # ==========================================================

    @staticmethod
    def _normalizar_material_desenho(
        material: Any,
    ) -> Optional[str]:

        if material is None:
            return None

        texto = str(
            material
        ).strip().upper()

        if not texto:
            return None

        if "A36" in texto:
            return "ACO A36"

        if "INOX" in texto:
            return "ACO INOX"

        if (
            "ALUMINIO" in texto
            or "ALUMÍNIO" in texto
        ):
            return "ALUMINIO"

        return texto

    # ==========================================================
    # CÁLCULO DE BEND ALLOWANCE
    # ==========================================================

    @classmethod
    def calcular_bend_allowance(
        cls,
        espessura_mm: float,
        raio_interno_mm: float,
        angulo_graus: float,
        k_factor: Optional[float] = None,
    ) -> float:
        """
        Calcula o Bend Allowance (BA).

        Fórmula:

            BA = PI / 180 × A × (R + K × T)

        Onde:

            A = ângulo da dobra em graus
            R = raio interno
            T = espessura
            K = fator K

        O resultado representa o comprimento da linha neutra
        utilizado no desenvolvimento da dobra.
        """

        t = cls._numero(
            espessura_mm
        )

        r = cls._numero(
            raio_interno_mm
        )

        a = cls._numero(
            angulo_graus
        )

        k = cls._numero(
            k_factor
        )

        if t is None or t <= 0:
            raise ValueError(
                "Espessura da chapa inválida."
            )

        if r is None or r < 0:
            raise ValueError(
                "Raio interno da dobra inválido."
            )

        if a is None or a <= 0:
            raise ValueError(
                "Ângulo da dobra inválido."
            )

        if k is None:
            k = cls.K_FACTOR_PADRAO

        if not 0.0 <= k <= 1.0:
            raise ValueError(
                "Fator K deve estar entre 0 e 1."
            )

        angulo_rad = math.radians(
            a
        )

        ba = (
            angulo_rad
            * (
                r
                + (k * t)
            )
        )

        return round(
            ba,
            4,
        )

    # ==========================================================
    # CÁLCULO DE BEND DEDUCTION
    # ==========================================================

    @classmethod
    def calcular_bend_deduction(
        cls,
        espessura_mm: float,
        raio_interno_mm: float,
        angulo_graus: float,
        k_factor: Optional[float] = None,
    ) -> float:
        """
        Calcula o Bend Deduction (BD).

        Fórmula:

            BD =
                2 × (R + T) × tan(A / 2)
                - BA

        Onde BA é o Bend Allowance.

        Esta fórmula é utilizada quando as dimensões da peça
        extraída representam dimensões externas totais.

        Para o caso de uma dimensão externa contendo duas
        dobras, o desenvolvimento pode ser obtido por:

            Desenvolvimento =
                Dimensão externa
                - soma(BD)
        """

        t = cls._numero(
            espessura_mm
        )

        r = cls._numero(
            raio_interno_mm
        )

        a = cls._numero(
            angulo_graus
        )

        if t is None or t <= 0:
            raise ValueError(
                "Espessura da chapa inválida."
            )

        if r is None or r < 0:
            raise ValueError(
                "Raio interno da dobra inválido."
            )

        if a is None or a <= 0:
            raise ValueError(
                "Ângulo da dobra inválido."
            )

        ba = cls.calcular_bend_allowance(
            espessura_mm=t,
            raio_interno_mm=r,
            angulo_graus=a,
            k_factor=k_factor,
        )

        angulo_meio_rad = math.radians(
            a / 2.0
        )

        bd = (
            2.0
            * (r + t)
            * math.tan(
                angulo_meio_rad
            )
            - ba
        )

        return round(
            bd,
            4,
        )

    # ==========================================================
    # DESENVOLVIMENTO DE CHAPA
    # ==========================================================

    @classmethod
    def calcular_desenvolvimento_chapa(
        cls,
        dados: Dict[str, Any],
        k_factor: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Calcula o desenvolvimento de uma peça de chapa dobrada.

        Estratégia atual:
        -----------------

        1. Obtém a espessura.
        2. Obtém as dimensões geométricas.
        3. Obtém as dobras.
        4. Obtém raio e ângulo de cada dobra.
        5. Calcula BA e BD de cada dobra.
        6. Quando a geometria representa uma dimensão externa
           total, calcula:

                BLANK =
                    dimensão externa
                    - soma(Bend Deduction)

        Para peças como:

            672 x 163 mm
            2 dobras de 90°
            R10
            T6,35

        o método calcula aproximadamente:

            672 - BD1 - BD2

        produzindo um desenvolvimento próximo de 645~646 mm,
        dependendo do K.

        IMPORTANTE:
        -----------
        O algoritmo não assume que toda dimensão extraída
        seja desenvolvimento.

        A dimensão maior é tratada como o comprimento externo
        de desenvolvimento somente quando existem dobras e
        dados suficientes para calcular a compensação.

        A menor dimensão é preservada como largura do blank.
        """

        if not dados:
            return None

        if (
            dados.get("tipo_dimensional")
            != "CHAPA"
        ):
            return None

        espessura = cls._numero(
            dados.get("espessura_mm")
        )

        if (
            espessura is None
            or espessura <= 0
        ):
            return None

        dimensoes = (
            cls._extrair_dimensoes_geometricas(
                dados
            )
        )

        if len(dimensoes) < 2:
            return None

        dobras = dados.get(
            "dobras"
        )

        if not isinstance(
            dobras,
            (list, tuple),
        ):
            return None

        if not dobras:
            return None

        # ------------------------------------------------------
        # ORGANIZA DIMENSÕES
        # ------------------------------------------------------

        dimensoes_validas = [
            float(x)
            for x in dimensoes
            if (
                x is not None
                and x > 0
            )
        ]

        if len(dimensoes_validas) < 2:
            return None

        dimensao_maior = max(
            dimensoes_validas
        )

        dimensao_menor = min(
            dimensoes_validas
        )

        # ------------------------------------------------------
        # CALCULA CADA DOBRA
        # ------------------------------------------------------

        detalhes_dobras = []

        total_ba = 0.0
        total_bd = 0.0

        for indice, dobra in enumerate(
            dobras,
            start=1,
        ):

            angulo = (
                cls._valor_angulo(
                    dobra
                )
                if dobra is not None
                else None
            )

            if angulo is None:
                angulo = (
                    cls.ANGULO_DOBRA_PADRAO_GRAUS
                )

            raio = (
                cls._valor_raio(
                    dobra
                )
                if dobra is not None
                else None
            )

            if raio is None:
                return None

            k = cls._valor_k(
                dobra,
                k_factor,
            )

            try:

                ba = cls.calcular_bend_allowance(
                    espessura_mm=espessura,
                    raio_interno_mm=raio,
                    angulo_graus=angulo,
                    k_factor=k,
                )

                bd = cls.calcular_bend_deduction(
                    espessura_mm=espessura,
                    raio_interno_mm=raio,
                    angulo_graus=angulo,
                    k_factor=k,
                )

            except ValueError:

                return None

            total_ba += ba
            total_bd += bd

            detalhes_dobras.append(
                {
                    "numero": indice,
                    "angulo_graus": round(
                        angulo,
                        4,
                    ),
                    "raio_interno_mm": round(
                        raio,
                        4,
                    ),
                    "espessura_mm": round(
                        espessura,
                        4,
                    ),
                    "k_factor": round(
                        k,
                        4,
                    ),
                    "bend_allowance_mm": round(
                        ba,
                        4,
                    ),
                    "bend_deduction_mm": round(
                        bd,
                        4,
                    ),
                }
            )

        # ------------------------------------------------------
        # DESENVOLVIMENTO
        # ------------------------------------------------------
        #
        # A dimensão maior é tratada como dimensão externa
        # total no eixo das dobras.
        #
        # BLANK = dimensão externa - soma BD
        #
        # Isso é exatamente o que corrige o erro anterior:
        #
        #     672
        #
        # não é simplesmente usado como BLANK.
        # ------------------------------------------------------

        desenvolvimento = (
            dimensao_maior
            - total_bd
        )

        if desenvolvimento <= 0:
            return None

        largura_blank = (
            dimensao_menor
        )

        return {
            "desenvolvimento_mm": round(
                desenvolvimento,
                4,
            ),
            "largura_blank_mm": round(
                largura_blank,
                4,
            ),
            "comprimento_blank_mm": round(
                desenvolvimento,
                4,
            ),
            "k_factor": round(
                (
                    detalhes_dobras[0][
                        "k_factor"
                    ]
                    if detalhes_dobras
                    else (
                        k_factor
                        if k_factor is not None
                        else cls.K_FACTOR_PADRAO
                    )
                ),
                4,
            ),
            "bend_allowance_total_mm": round(
                total_ba,
                4,
            ),
            "bend_deduction_total_mm": round(
                total_bd,
                4,
            ),
            "quantidade_dobras": len(
                detalhes_dobras
            ),
            "dobras_calculadas": (
                detalhes_dobras
            ),
            "dimensao_externa_utilizada_mm": round(
                dimensao_maior,
                4,
            ),
            "dimensao_transversal_utilizada_mm": round(
                dimensao_menor,
                4,
            ),
            "metodo_desenvolvimento": (
                "DIMENSAO_EXTERNA_MENOS_BEND_DEDUCTION"
            ),
            "status_desenvolvimento": (
                "DESENVOLVIMENTO CALCULADO"
            ),
        }

    # ==========================================================
    # VALIDAÇÃO PARA CORTE
    # ==========================================================

    @staticmethod
    def _pode_preparar_para_corte(
        dados: Dict[str, Any],
    ) -> bool:

        tipo = dados.get(
            "tipo_dimensional"
        )

        if tipo == "CHAPA":

            return (
                dados.get(
                    "espessura_mm"
                ) is not None
                and (
                    (
                        dados.get(
                            "largura_efetiva_mm"
                        )
                        is not None
                        and dados.get(
                            "comprimento_efetivo_mm"
                        )
                        is not None
                    )
                    or (
                        dados.get(
                            "blank"
                        )
                        is not None
                    )
                )
            )

        if tipo == "TUBO":

            return (
                dados.get(
                    "diametro_externo_mm"
                ) is not None
                and dados.get(
                    "espessura_mm"
                ) is not None
                and dados.get(
                    "comprimento_efetivo_mm"
                ) is not None
            )

        if tipo == "BARRA":

            return (
                dados.get(
                    "bitola_mm"
                ) is not None
                and dados.get(
                    "comprimento_efetivo_mm"
                ) is not None
            )

        if tipo == "PERFIL":

            return (
                dados.get(
                    "comprimento_efetivo_mm"
                ) is not None
            )

        return False

    # ==========================================================
    # PREPARAR MEDIDAS DE COMPRA
    # ==========================================================

    @classmethod
    def preparar_medidas_compra(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        if df is None:
            return pd.DataFrame()

        if df.empty:
            return df.copy()

        resultado = df.copy()

        # ------------------------------------------------------
        # LOCALIZAR COLUNAS
        # ------------------------------------------------------

        def encontrar_coluna(
            *nomes,
        ):

            for nome in nomes:

                if nome in resultado.columns:
                    return nome

            return None

        col_descricao = encontrar_coluna(
            "DESCRICAO_PRODUTO",
            "descricao_produto",
            "descricao",
            "DESCRICAO",
        )

        col_classificacao = encontrar_coluna(
            "CLASSIFICACAO",
            "classificacao",
            "categoria_planejamento",
        )

        col_unidade = encontrar_coluna(
            "UNIDADE_MEDIDA",
            "unidade_medida",
            "UM",
        )

        if col_descricao is None:

            raise ValueError(
                "Coluna de descrição não encontrada."
            )

        # ------------------------------------------------------
        # ANALISAR LINHA POR LINHA
        # ------------------------------------------------------

        registros = []

        for _, linha in resultado.iterrows():

            descricao = linha.get(
                col_descricao
            )

            classificacao = (
                linha.get(
                    col_classificacao
                )
                if col_classificacao
                else None
            )

            unidade = (
                linha.get(
                    col_unidade
                )
                if col_unidade
                else None
            )

            dados = cls.analisar_item(
                descricao,
                classificacao,
                unidade,
            )

            registros.append(
                dados
            )

        df_dimensional = pd.DataFrame(
            registros
        )

        # ------------------------------------------------------
        # GARANTIR ÍNDICE
        # ------------------------------------------------------

        resultado = resultado.reset_index(
            drop=True
        )

        df_dimensional = (
            df_dimensional.reset_index(
                drop=True
            )
        )

        # ------------------------------------------------------
        # REMOVER COLUNAS DIMENSIONAIS ANTIGAS
        # ------------------------------------------------------

        for coluna in df_dimensional.columns:

            if coluna in resultado.columns:

                resultado.drop(
                    columns=[coluna],
                    inplace=True,
                )

        # ------------------------------------------------------
        # JUNTAR
        # ------------------------------------------------------

        resultado = pd.concat(
            [
                resultado,
                df_dimensional,
            ],
            axis=1,
        )

        return resultado

    # ==========================================================
    # RESUMO
    # ==========================================================

    @staticmethod
    def gerar_resumo(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        if df is None or df.empty:
            return pd.DataFrame()

        if (
            "tipo_dimensional"
            not in df.columns
        ):
            return pd.DataFrame()

        resumo = (
            df.groupby(
                "tipo_dimensional",
                dropna=False,
            )
            .size()
            .reset_index(
                name="quantidade_itens"
            )
        )

        return resumo

    # ==========================================================
    # BLANK
    # ==========================================================

    @classmethod
    def determinar_blank(
        cls,
        dados: Dict[str, Any],
    ) -> Optional[Dict[str, float]]:
        """
        Determina o BLANK da peça.

        Prioridade:

            1. BLANK explicitamente fornecido;
            2. BLANK calculado pelo desenvolvimento;
            3. peça de chapa sem dobras usando medidas efetivas;
            4. comprimento efetivo de tubo/barra/perfil.

        Para chapa dobrada, o método NÃO utiliza mais
        diretamente a dimensão geométrica como BLANK.

        Primeiro tenta o desenvolvimento por Bend Deduction.
        """

        if not dados:
            return None

        tipo = dados.get(
            "tipo_dimensional"
        )

        # ------------------------------------------------------
        # BLANK EXPLÍCITO
        # ------------------------------------------------------

        blank_existente = dados.get(
            "blank"
        )

        if isinstance(
            blank_existente,
            dict,
        ):

            largura = cls._numero(
                blank_existente.get(
                    "largura_mm"
                )
            )

            comprimento = cls._numero(
                blank_existente.get(
                    "comprimento_mm"
                )
            )

            if (
                largura is not None
                and comprimento is not None
            ):

                return {
                    "largura_mm": round(
                        largura,
                        4,
                    ),
                    "comprimento_mm": round(
                        comprimento,
                        4,
                    ),
                }

        # ------------------------------------------------------
        # CHAPA
        # ------------------------------------------------------

        if tipo == "CHAPA":

            dobras = dados.get(
                "dobras"
            )

            # --------------------------------------------------
            # PEÇA DOBRADA
            # --------------------------------------------------

            if isinstance(
                dobras,
                (list, tuple),
            ) and len(dobras) > 0:

                desenvolvimento = (
                    dados.get(
                        "desenvolvimento_mm"
                    )
                )

                largura_blank = (
                    dados.get(
                        "largura_blank_mm"
                    )
                )

                comprimento_blank = (
                    dados.get(
                        "comprimento_blank_mm"
                    )
                )

                if desenvolvimento is not None:

                    desenvolvimento = cls._numero(
                        desenvolvimento
                    )

                if largura_blank is not None:

                    largura_blank = cls._numero(
                        largura_blank
                    )

                if comprimento_blank is not None:

                    comprimento_blank = cls._numero(
                        comprimento_blank
                    )

                if (
                    desenvolvimento is not None
                    and desenvolvimento > 0
                ):

                    if (
                        largura_blank is None
                        or largura_blank <= 0
                    ):

                        dimensoes = (
                            cls._extrair_dimensoes_geometricas(
                                dados
                            )
                        )

                        if len(dimensoes) >= 2:

                            largura_blank = min(
                                dimensoes
                            )

                    if (
                        comprimento_blank is None
                        or comprimento_blank <= 0
                    ):

                        comprimento_blank = (
                            desenvolvimento
                        )

                    if (
                        largura_blank is not None
                        and largura_blank > 0
                    ):

                        return {
                            "largura_mm": round(
                                largura_blank,
                                4,
                            ),
                            "comprimento_mm": round(
                                comprimento_blank,
                                4,
                            ),
                        }

                # Se há dobras mas não foi possível calcular
                # desenvolvimento, NÃO inventar BLANK.
                return None

            # --------------------------------------------------
            # CHAPA SEM DOBRA
            # --------------------------------------------------

            largura = cls._numero(
                dados.get(
                    "largura_efetiva_mm"
                )
            )

            comprimento = cls._numero(
                dados.get(
                    "comprimento_efetivo_mm"
                )
            )

            if (
                largura is not None
                and comprimento is not None
            ):

                return {
                    "largura_mm": round(
                        largura,
                        4,
                    ),
                    "comprimento_mm": round(
                        comprimento,
                        4,
                    ),
                }

        # ------------------------------------------------------
        # TUBO
        # ------------------------------------------------------

        elif tipo == "TUBO":

            comprimento = cls._numero(
                dados.get(
                    "comprimento_efetivo_mm"
                )
            )

            if (
                comprimento is not None
                and comprimento > 0
            ):

                return {
                    "comprimento_mm": round(
                        comprimento,
                        4,
                    ),
                }

        # ------------------------------------------------------
        # BARRA
        # ------------------------------------------------------

        elif tipo == "BARRA":

            comprimento = cls._numero(
                dados.get(
                    "comprimento_efetivo_mm"
                )
            )

            if (
                comprimento is not None
                and comprimento > 0
            ):

                return {
                    "comprimento_mm": round(
                        comprimento,
                        4,
                    ),
                }

        # ------------------------------------------------------
        # PERFIL
        # ------------------------------------------------------

        elif tipo == "PERFIL":

            comprimento = cls._numero(
                dados.get(
                    "comprimento_efetivo_mm"
                )
            )

            if (
                comprimento is not None
                and comprimento > 0
            ):

                return {
                    "comprimento_mm": round(
                        comprimento,
                        4,
                    ),
                }

        return None