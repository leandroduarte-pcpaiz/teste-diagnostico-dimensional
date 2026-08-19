import pandas as pd


class ClassificadorMateriais:
    """
    Classificador central de materiais do AIZI Engineering AI.

    O classificador possui DUAS camadas:

    1. CLASSIFICACAO
       Define o comportamento do item no planejamento:
           - MATERIA_PRIMA
           - FABRICADO
           - COMERCIAL
           - CONSUMO
           - NAO_CLASSIFICADO

    2. TIPO_ENGENHARIA
       Define a categoria técnica do item:
           - CHAPA
           - TUBO
           - BARRA
           - PERFIL
           - FIXACAO
           - CONEXAO
           - HIDRAULICO
           - etc.

    REGRA PRINCIPAL DO AIZI:

        G2 -> MATÉRIA-PRIMA

        G1/G3 -> podem representar matéria-prima/processo
                 interno, mas NÃO são classificados como
                 matéria-prima de planejamento automaticamente.

        G/K -> itens ligados à fabricação interna conforme
               estrutura da BOM.

        Não G/K -> FABRICADO, quando o item possui estrutura
                   própria na BOM.

        MP do TOTVS sem estrutura -> COMERCIAL,
        EXCETO G2 -> MATÉRIA-PRIMA.

        MC -> CONSUMO.

    ITEM_FANTASMA NÃO altera quantidade nem classificação.
    """


    # ==========================================================
    # CATEGORIAS DE ENGENHARIA
    # ==========================================================

    REGRAS = {

        "CHAPA": [
            "CHAPA",
        ],

        "TUBO": [
            "TUBO REDONDO",
            "TUBO INDUSTRIAL",
            "TUBO MECANICO",
            "TUBO DIN",
            "TUBO NBR",
            "TUBO SAE",
            "TUBO NYLON",
            "TUBO",
        ],

        "BARRA": [
            "BARRA REDONDA",
            "BARRA CHATA",
            "BARRA QUADRADA",
            "BARRA SEXTAVADA",
            "BARRA",
        ],

        "PERFIL": [
            "PERFIL",
            "CANTONEIRA",
            "VIGA",
            "UNP",
            "U PERFIL",
            "I PERFIL",
        ],

        "FIO": [
            "FIO",
            "CABO",
            "CHICOTE",
        ],

        "PINTURA": [
            "TINTA",
            "PRIMER",
            "ESMALTE",
            "VERNIZ",
            "THINNER",
            "SOLVENTE",
        ],

        "FIXACAO": [
            "PARAFUSO",
            "PF SX",
            "PF MAQ",
            "PO SX",
            "PORCA",
            "ARRUELA",
            "REBITE",
            "PRISIONEIRO",
        ],

        "CONEXAO": [
            "ADAP",
            "ADAPTADOR",
            "NIPLE",
            "COTOVELO",
            "LUVA",
            "TEE",
            "CONEXAO",
            "CONEXÃO",
            "BUJAO",
            "BUJÃO",
            "REDUCAO",
            "REDUÇÃO",
            "CONECTOR",
        ],

        "VALVULA": [
            "VALVULA",
            "VÁLVULA",
            "REGISTRO",
        ],

        "VEDACAO": [
            "VEDACAO",
            "VEDAÇÃO",
            "ANEL ORING",
            "ORING",
            "JUNTA",
            "BORRACHA",
            "LENCOL DE BORRACHA",
            "LENÇOL DE BORRACHA",
        ],

        "MANGUEIRA": [
            "MANGUEIRA",
            "MANG ",
            "MANG.",
        ],

        "HIDRAULICO": [
            "BOMBA HID",
            "BOMBA HIDRAULICA",
            "BOMBA HIDRÁULICA",
            "MOTOR HID",
            "MOTOR HIDRAULICO",
            "MOTOR HIDRÁULICO",
            "COMPRESSOR",
            "PROPULSORA",
        ],

        "ELETRICO": [
            "LANTERNA",
            "FAROL",
            "SINALIZADOR",
            "CHICOTE",
            "CONECTOR ELETRICO",
            "CONECTOR ELÉTRICO",
            "TOMADA",
            "BOTAO",
            "BOTÃO",
            "ATERRAMENTO",
        ],

        "FILTRO": [
            "FILTRO",
        ],

        "CORREIA": [
            "CORREIA",
        ],

        "BUCHA": [
            "BUCHA",
        ],

        "ESTRUTURAL": [
            "GONZO",
            "SUPORTE",
            "CALCO",
            "CALÇO",
            "TAMPA",
            "DOBRADICA",
            "DOBRADIÇA",
            "ACOPLAMENTO",
        ],

        "ACESSORIO": [
            "EXTINTOR",
            "PLAQUETA",
            "ADESIVO",
            "FAIXA REFLETIVA",
            "PARA BARRO",
            "ABRACADEIRA",
            "ABRAÇADEIRA",
            "FECHO",
            "ESGUICHO",
            "BOCAL",
            "VISOR",
            "CARRETEL",
        ],
    }


    # ==========================================================
    # INICIALIZAÇÃO
    # ==========================================================

    def __init__(self, df):

        if df is None:
            raise ValueError(
                "O DataFrame informado ao ClassificadorMateriais "
                "não pode ser None."
            )

        self.df = df.copy()


    # ==========================================================
    # CLASSIFICAÇÃO DE ENGENHARIA
    # ==========================================================

    def classificar_descricao(self, descricao):

        if pd.isna(descricao):
            return "NAO_CLASSIFICADO"

        descricao = (
            str(descricao)
            .upper()
            .strip()
        )

        if not descricao:
            return "NAO_CLASSIFICADO"

        for categoria, palavras in self.REGRAS.items():

            for palavra in palavras:

                if palavra in descricao:
                    return categoria

        return "OUTROS"


    # ==========================================================
    # CLASSIFICAÇÃO DE PLANEJAMENTO
    # ==========================================================

    def classificar_planejamento(
        self,
        tipo,
        componente,
        possui_estrutura=False
    ):
        """
        Define a classificação utilizada pelo planejamento.

        Parâmetros:

            tipo:
                TIPO do cadastro TOTVS.

            componente:
                Código do componente.

            possui_estrutura:
                True quando o componente possui filhos na BOM.

        Retorno:

            MATERIA_PRIMA
            FABRICADO
            COMERCIAL
            CONSUMO
            NAO_CLASSIFICADO
        """

        tipo = (
            ""
            if pd.isna(tipo)
            else str(tipo).upper().strip()
        )

        componente = (
            ""
            if pd.isna(componente)
            else str(componente).upper().strip()
        )

        # ------------------------------------------------------
        # MATERIAL DE USO E CONSUMO
        # ------------------------------------------------------

        if tipo == "MC":
            return "CONSUMO"

        # ------------------------------------------------------
        # G2 = MATÉRIA-PRIMA
        # ------------------------------------------------------

        if componente.startswith("G2"):
            return "MATERIA_PRIMA"

        # ------------------------------------------------------
        # ITENS COM ESTRUTURA
        #
        # Se possui estrutura própria na BOM, trata-se de um
        # componente fabricado/intermediário.
        # ------------------------------------------------------

        if possui_estrutura:
            return "FABRICADO"

        # ------------------------------------------------------
        # G1 / G3
        #
        # Podem ser materiais utilizados em processos internos,
        # mas não entram automaticamente como matéria-prima
        # principal do planejamento.
        # ------------------------------------------------------

        if componente.startswith("G1"):
            return "COMERCIAL"

        if componente.startswith("G3"):
            return "COMERCIAL"

        # ------------------------------------------------------
        # K
        #
        # K sem estrutura é tratado como comercial.
        # K com estrutura já teria retornado FABRICADO acima.
        # ------------------------------------------------------

        if componente.startswith("K"):
            return "COMERCIAL"

        # ------------------------------------------------------
        # MP sem estrutura
        #
        # No planejamento simplificado, apenas G2 é matéria-prima.
        # Os demais MP sem estrutura entram como comercial.
        # ------------------------------------------------------

        if tipo == "MP":
            return "COMERCIAL"

        # ------------------------------------------------------
        # DEMAIS TIPOS
        # ------------------------------------------------------

        if tipo in {
            "MR",
            "PA",
            "PI",
            "PP",
            "BN",
        }:
            return "COMERCIAL"

        # ------------------------------------------------------
        # TIPO NÃO RECONHECIDO
        # ------------------------------------------------------

        if tipo:
            return "COMERCIAL"

        return "NAO_CLASSIFICADO"


    # ==========================================================
    # APLICA CLASSIFICAÇÃO COMPLETA
    # ==========================================================

    def classificar(
        self,
        estruturas=None
    ):
        """
        Classifica o DataFrame completo.

        estruturas:
            Conjunto/lista de códigos que possuem estrutura
            própria na BOM.

        Retorna DataFrame enriquecido com:

            CLASSIFICACAO
            TIPO_ENGENHARIA
            POSSUI_ESTRUTURA
        """

        resultado = self.df.copy()

        # ------------------------------------------------------
        # Validação das colunas
        # ------------------------------------------------------

        if "componente" not in resultado.columns:
            raise ValueError(
                "O DataFrame precisa possuir a coluna "
                "'componente'."
            )

        if "TIPO" not in resultado.columns:
            raise ValueError(
                "O DataFrame precisa possuir a coluna "
                "'TIPO'."
            )

        if "DESCRICAO_PRODUTO" not in resultado.columns:
            resultado["DESCRICAO_PRODUTO"] = ""

        # ------------------------------------------------------
        # Normaliza estruturas
        # ------------------------------------------------------

        if estruturas is None:
            estruturas = set()

        estruturas = {
            str(codigo)
            .upper()
            .strip()
            for codigo in estruturas
        }

        resultado["componente"] = (
            resultado["componente"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip()
        )

        # ------------------------------------------------------
        # Possui estrutura
        # ------------------------------------------------------

        resultado["POSSUI_ESTRUTURA"] = (
            resultado["componente"]
            .isin(estruturas)
        )

        # ------------------------------------------------------
        # Classificação de planejamento
        # ------------------------------------------------------

        resultado["CLASSIFICACAO"] = resultado.apply(
            lambda linha: self.classificar_planejamento(
                tipo=linha.get("TIPO", ""),
                componente=linha.get("componente", ""),
                possui_estrutura=linha.get(
                    "POSSUI_ESTRUTURA",
                    False
                )
            ),
            axis=1
        )

        # ------------------------------------------------------
        # Categoria técnica
        # ------------------------------------------------------

        resultado["TIPO_ENGENHARIA"] = (
            resultado["DESCRICAO_PRODUTO"]
            .apply(self.classificar_descricao)
        )

        return resultado


    # ==========================================================
    # RESUMO
    # ==========================================================

    def gerar_resumo(self, df):

        if df is None or df.empty:
            return pd.DataFrame(
                columns=[
                    "CLASSIFICACAO",
                    "quantidade_itens",
                    "quantidade_total",
                ]
            )

        agregacoes = {
            "componente": "count",
        }

        if "quantidade_total" in df.columns:
            agregacoes["quantidade_total"] = "sum"

        resumo = (
            df.groupby(
                "CLASSIFICACAO",
                dropna=False
            )
            .agg(
                quantidade_itens=(
                    "componente",
                    "count"
                ),
                quantidade_total=(
                    "quantidade_total",
                    "sum"
                )
                if "quantidade_total" in df.columns
                else (
                    "componente",
                    "count"
                )
            )
            .reset_index()
            .sort_values(
                "quantidade_itens",
                ascending=False
            )
        )

        return resumo.reset_index(drop=True)


    # ==========================================================
    # RESUMO POR TIPO DE ENGENHARIA
    # ==========================================================

    def gerar_resumo_engenharia(self, df):

        if df is None or df.empty:
            return pd.DataFrame()

        return (
            df.groupby(
                "TIPO_ENGENHARIA",
                dropna=False
            )
            .agg(
                quantidade_itens=(
                    "componente",
                    "count"
                ),
                quantidade_total=(
                    "quantidade_total",
                    "sum"
                )
            )
            .reset_index()
            .sort_values(
                "quantidade_itens",
                ascending=False
            )
            .reset_index(drop=True)
        )