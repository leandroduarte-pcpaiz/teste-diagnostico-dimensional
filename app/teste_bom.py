import sys
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAÇÃO DO PROJETO
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# IMPORTAÇÕES DO AIZI
# ============================================================

from app.importadores.importador_totvs import importar_csv
from app.engineering.explosao_bom import ExplosaoBOM
from app.engineering.motor_engenharia import MotorEngenharia
from app.engineering.classificador_materiais import (
    ClassificadorMateriais,
)
from app.engineering.planejador_necessidades import (
    PlanejadorNecessidades,
)
from app.engineering.planejador_dimensional import (
    PlanejadorDimensional,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CAMINHO_BOM = (
    ROOT
    / "data"
    / "estrutura_de_i3001192_ate_i3001192.csv"
)

PRODUTO = "I3001192"


# ============================================================
# QUANTIDADE DE PRODUTO ACABADO
# ============================================================

QUANTIDADE = 10


# ============================================================
# CAMINHO DO RESULTADO
# ============================================================

CAMINHO_RESULTADO = (
    ROOT
    / "resultado_final"
    / "planejamento_necessidades.xlsx"
)

CAMINHO_DIMENSIONAL = (
    ROOT
    / "resultado_final"
    / "planejamento_dimensional.xlsx"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def imprimir_titulo(texto):

    print()
    print("=" * 80)
    print(texto)
    print("=" * 80)


def imprimir_tabela(
    dataframe,
    colunas=None,
):

    if dataframe is None or dataframe.empty:

        print("Nenhum registro encontrado.")

        return

    tabela = dataframe.copy()

    if colunas is not None:

        colunas_existentes = [
            coluna
            for coluna in colunas
            if coluna in tabela.columns
        ]

        tabela = tabela[
            colunas_existentes
        ]

    print()

    print(
        tabela.to_string(
            index=False
        )
    )


# ============================================================
# PRINCIPAL
# ============================================================

def main():

    imprimir_titulo(
        "AIZI ENGINEERING AI"
    )

    print(
        "TESTE COMPLETO DA BOM + CADASTRO + "
        "CLASSIFICAÇÃO + PLANEJAMENTO + DIMENSIONAL"
    )

    # ========================================================
    # 1. IMPORTAR BOM
    # ========================================================

    imprimir_titulo(
        "1. IMPORTANDO BOM DO TOTVS"
    )

    if not CAMINHO_BOM.exists():

        raise FileNotFoundError(
            f"\nArquivo BOM não encontrado:\n"
            f"{CAMINHO_BOM}\n\n"
            f"Verifique se o CSV está dentro da pasta data."
        )

    print()
    print("Arquivo BOM:")
    print(CAMINHO_BOM)

    df_bom = importar_csv(
        CAMINHO_BOM
    )

    print()

    print(
        f"Linhas carregadas: "
        f"{len(df_bom):,}".replace(",", ".")
    )

    # ========================================================
    # 2. CRIAR ESTRUTURA DA BOM
    # ========================================================

    imprimir_titulo(
        "2. CRIANDO ESTRUTURA DA BOM"
    )

    explosao = ExplosaoBOM(
        df_bom
    )

    # ========================================================
    # 3. EXPLOSÃO CONSOLIDADA
    # ========================================================

    imprimir_titulo(
        "3. EXPLOSÃO CONSOLIDADA - 1 CONJUNTO"
    )

    resultado_explosao = explosao.explodir(
        produto=PRODUTO,
        quantidade=1,
    )

    if resultado_explosao.empty:

        print()
        print(
            "NENHUM COMPONENTE ENCONTRADO."
        )

        return

    print()

    print(
        f"Componentes consolidados: "
        f"{len(resultado_explosao)}"
    )

    print()

    print(
        resultado_explosao.head(30).to_string(
            index=False
        )
    )

    # ========================================================
    # 4. MOTOR DE ENGENHARIA
    # ========================================================

    imprimir_titulo(
        "4. CARREGANDO MOTOR DE ENGENHARIA"
    )

    motor = MotorEngenharia()

    # ========================================================
    # 5. ENRIQUECER COM CADASTRO TOTVS
    # ========================================================

    imprimir_titulo(
        "5. ENRIQUECENDO EXPLOSÃO COM CADASTRO TOTVS"
    )

    resultado = motor.enriquecer(
        resultado_explosao
    )

    # ========================================================
    # 6. RESULTADO ENRIQUECIDO
    # ========================================================

    imprimir_titulo(
        "6. RESULTADO ENRIQUECIDO"
    )

    imprimir_tabela(
        resultado.head(50)
    )

    # ========================================================
    # 7. RESUMO DA EXPLOSÃO
    # ========================================================

    imprimir_titulo(
        "7. RESUMO DA EXPLOSÃO"
    )

    total = len(resultado)

    encontrados = int(
        resultado[
            "cadastro_encontrado"
        ].sum()
    )

    nao_encontrados = (
        total - encontrados
    )

    print(
        f"Componentes consolidados:       {total}"
    )

    print(
        f"Encontrados no cadastro TOTVS:  "
        f"{encontrados}"
    )

    print(
        f"Não encontrados:                "
        f"{nao_encontrados}"
    )

    # ========================================================
    # 8. DISTRIBUIÇÃO POR TIPO TOTVS
    # ========================================================

    imprimir_titulo(
        "8. DISTRIBUIÇÃO POR TIPO TOTVS"
    )

    if "TIPO" in resultado.columns:

        tipos = (
            resultado
            .copy()
            .fillna("")
            .groupby(
                [
                    "TIPO",
                    "DESCRICAO_TIPO",
                ],
                dropna=False,
            )
            .agg(
                componentes=(
                    "componente",
                    "count",
                ),
                quantidade_total=(
                    "quantidade_total",
                    "sum",
                ),
            )
            .reset_index()
            .sort_values(
                by="componentes",
                ascending=False,
            )
        )

        imprimir_tabela(
            tipos
        )

    # ========================================================
    # 9. CLASSIFICAÇÃO DOS MATERIAIS
    # ========================================================

    imprimir_titulo(
        "9. CLASSIFICAÇÃO DOS MATERIAIS"
    )

    classificador = ClassificadorMateriais(
        resultado
    )

    resultado_classificado = (
        classificador.classificar()
    )

    resumo_categorias = (
        classificador.gerar_resumo(
            resultado_classificado
        )
    )

    imprimir_tabela(
        resumo_categorias
    )

    # ========================================================
    # 10. COMPONENTES NÃO ENCONTRADOS
    # ========================================================

    if nao_encontrados > 0:

        imprimir_titulo(
            "10. COMPONENTES NÃO ENCONTRADOS NO CADASTRO"
        )

        nao_cadastrados = resultado[
            ~resultado[
                "cadastro_encontrado"
            ]
        ]

        imprimir_tabela(
            nao_cadastrados,
            [
                "componente",
                "quantidade_total",
            ],
        )

    # ========================================================
    # 11. ÁRVORE HIERÁRQUICA
    # ========================================================

    imprimir_titulo(
        "11. ÁRVORE HIERÁRQUICA DA BOM"
    )

    arvore = explosao.montar_arvore(
        produto=PRODUTO,
        quantidade=1,
    )

    if arvore.empty:

        print()
        print(
            "Nenhuma estrutura encontrada."
        )

    else:

        imprimir_tabela(
            arvore.head(100)
        )

        print()

        print(
            f"Linhas da árvore: "
            f"{len(arvore)}"
        )

    # ========================================================
    # 12. PLANEJADOR DE NECESSIDADES
    # ========================================================

    imprimir_titulo(
        "12. PLANEJADOR DE NECESSIDADES"
    )

    planejador = PlanejadorNecessidades(
        resultado_classificado=resultado_classificado,
        quantidade_conjuntos=QUANTIDADE,
    )

    planejamento = planejador.planejar()

    print()

    print(
        f"Produto acabado: {PRODUTO}"
    )

    print(
        f"Quantidade desejada: "
        f"{QUANTIDADE:g} conjuntos"
    )

    print()

    print(
        "Necessidades calculadas por componente."
    )

    # ========================================================
    # 13. NECESSIDADES DE MATÉRIA-PRIMA
    # ========================================================

    imprimir_titulo(
        "13. NECESSIDADE DE MATÉRIA-PRIMA"
    )

    materia_prima = (
        planejador.obter_materia_prima(
            planejamento
        )
    )

    imprimir_tabela(
        materia_prima,
        [
            "componente",
            "DESCRICAO_PRODUTO",
            "UNIDADE_MEDIDA",
            "quantidade_conjunto",
            "quantidade_necessaria",
        ],
    )

    # ========================================================
    # 14. NECESSIDADES COMERCIAIS
    # ========================================================

    imprimir_titulo(
        "14. NECESSIDADE DE ITENS COMERCIAIS"
    )

    comercial = (
        planejador.obter_comercial(
            planejamento
        )
    )

    imprimir_tabela(
        comercial,
        [
            "componente",
            "DESCRICAO_PRODUTO",
            "UNIDADE_MEDIDA",
            "quantidade_conjunto",
            "quantidade_necessaria",
        ],
    )

    # ========================================================
    # 15. NECESSIDADES DE CONSUMO
    # ========================================================

    imprimir_titulo(
        "15. NECESSIDADE DE CONSUMO"
    )

    consumo = (
        planejador.obter_consumo(
            planejamento
        )
    )

    imprimir_tabela(
        consumo,
        [
            "componente",
            "DESCRICAO_PRODUTO",
            "UNIDADE_MEDIDA",
            "quantidade_conjunto",
            "quantidade_necessaria",
        ],
    )

    # ========================================================
    # 16. NECESSIDADES CONSOLIDADAS
    # ========================================================

    imprimir_titulo(
        "16. NECESSIDADES CONSOLIDADAS"
    )

    necessidades = (
        planejador.consolidar_necessidades(
            planejamento
        )
    )

    imprimir_tabela(
        necessidades,
        [
            "componente",
            "DESCRICAO_PRODUTO",
            "CLASSIFICACAO",
            "UNIDADE_MEDIDA",
            "quantidade_conjunto",
            "NECESSIDADE_TOTAL",
        ],
    )

    # ========================================================
    # 17. RESUMO POR CLASSIFICAÇÃO
    # ========================================================

    imprimir_titulo(
        "17. RESUMO DAS NECESSIDADES"
    )

    resumo = (
        planejador.resumo_classificacao(
            planejamento
        )
    )

    imprimir_tabela(
        resumo
    )

    # ========================================================
    # 18. RESUMO POR CLASSIFICAÇÃO E UNIDADE
    # ========================================================

    imprimir_titulo(
        "18. RESUMO POR CLASSIFICAÇÃO E UNIDADE"
    )

    if planejamento is None or planejamento.empty:

        print(
            "Nenhum planejamento disponível para gerar resumo."
        )

    else:

        resumo_unidade = (
            planejamento
            .groupby(
                [
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                ],
                dropna=False,
            )
            .agg(
                quantidade_itens=(
                    "componente",
                    "nunique",
                ),
                quantidade_total=(
                    "quantidade_necessaria",
                    "sum",
                ),
            )
            .reset_index()
            .sort_values(
                [
                    "CLASSIFICACAO",
                    "UNIDADE_MEDIDA",
                ]
            )
        )

        imprimir_tabela(
            resumo_unidade
        )

    # ========================================================
    # 19. PREPARAÇÃO PARA ESTOQUE
    # ========================================================

    imprimir_titulo(
        "19. NECESSIDADES PREPARADAS PARA ESTOQUE"
    )

    estoque = (
        planejador.preparar_para_estoque(
            planejamento
        )
    )

    imprimir_tabela(
        estoque,
        [
            "componente",
            "DESCRICAO_PRODUTO",
            "CLASSIFICACAO",
            "UNIDADE_MEDIDA",
            "NECESSIDADE_TOTAL",
            "ARMAZEM",
            "ENDERECO",
            "ESTOQUE_DISPONIVEL",
            "ESTOQUE_RESERVADO",
            "ESTOQUE_UTILIZAVEL",
            "NECESSIDADE_LIQUIDA",
        ],
    )

    # ========================================================
    # 20. EXPORTAR PLANEJAMENTO DE NECESSIDADES
    # ========================================================

    imprimir_titulo(
        "20. EXPORTANDO PLANEJAMENTO"
    )

    caminho_exportado = (
        planejador.exportar_excel(
            CAMINHO_RESULTADO,
            planejamento,
        )
    )

    # ========================================================
    # 21. PREPARAÇÃO DIMENSIONAL
    # ========================================================
    #
    # A partir daqui NÃO voltamos para a BOM.
    #
    # O dimensional recebe diretamente o resultado do
    # PlanejadorNecessidades.
    #
    # Isso garante que:
    #
    # BOM = 1 conjunto
    #
    # Planejamento = quantidade real desejada
    #
    # Dimensional = necessidade real para corte
    #
    # ========================================================

    imprimir_titulo(
        "21. PLANEJADOR DIMENSIONAL"
    )

    planejador_dimensional = (
        PlanejadorDimensional(
            planejamento
        )
    )

    planejamento_dimensional = (
        planejador_dimensional.processar_dimensionais()
    )

    # ========================================================
    # 22. RESULTADO DIMENSIONAL
    # ========================================================

    imprimir_titulo(
        "22. RESULTADO DO PLANEJAMENTO DIMENSIONAL"
    )

    if (
        planejamento_dimensional is None
        or planejamento_dimensional.empty
    ):

        print()
        print(
            "Nenhum item dimensional identificado."
        )

    else:

        colunas_dimensional = [

            "componente",

            "DESCRICAO_PRODUTO",

            "CLASSIFICACAO",

            "UNIDADE_MEDIDA",

            "quantidade_conjunto",

            "quantidade_necessaria",

            "tipo_dimensional",

            "espessura_mm",

            "diametro_externo_mm",

            "diametro_interno_mm",

            "bitola_mm",

            "largura_padrao_mm",

            "comprimento_padrao_mm",

            "largura_efetiva_mm",

            "comprimento_efetivo_mm",

            "status_dimensional",

        ]

        imprimir_tabela(
            planejamento_dimensional,
            colunas_dimensional,
        )

    # ========================================================
    # 23. RESUMO DIMENSIONAL
    # ========================================================

    imprimir_titulo(
        "23. RESUMO POR TIPO DIMENSIONAL"
    )

    if (
        planejamento_dimensional is None
        or planejamento_dimensional.empty
    ):

        print(
            "Nenhum item dimensional para resumir."
        )

    else:

        resumo_dimensional = (
            planejamento_dimensional
            .groupby(
                "tipo_dimensional",
                dropna=False,
            )
            .agg(
                quantidade_itens=(
                    "componente",
                    "nunique",
                ),
                quantidade_total=(
                    "quantidade_necessaria",
                    "sum",
                ),
            )
            .reset_index()
            .sort_values(
                "tipo_dimensional"
            )
        )

        imprimir_tabela(
            resumo_dimensional
        )

    # ========================================================
    # 24. PREPARAÇÃO PARA CALCULADORA DE CORTE
    # ========================================================
    #
    # IMPORTANTE:
    #
    # Aqui ainda NÃO calculamos cortes.
    #
    # Apenas criamos os dados que serão entregues
    # posteriormente à CalculadoraCorte.
    #
    # ========================================================

    imprimir_titulo(
        "24. PREPARAÇÃO PARA CALCULADORA DE CORTE"
    )

    if (
        planejamento_dimensional is None
        or planejamento_dimensional.empty
    ):

        dados_para_corte = pd.DataFrame()

        print(
            "Nenhum item dimensional disponível para corte."
        )

    else:

        dados_para_corte = (
            planejador_dimensional
            .preparar_para_corte(
                planejamento_dimensional
            )
        )

        colunas_corte = [

            "componente",

            "DESCRICAO_PRODUTO",

            "CLASSIFICACAO",

            "UNIDADE_MEDIDA",

            "quantidade_para_corte",

            "tipo_dimensional",

            "espessura_mm",

            "diametro_externo_mm",

            "diametro_interno_mm",

            "bitola_mm",

            "largura_efetiva_mm",

            "comprimento_efetivo_mm",

            "status_dimensional",

        ]

        imprimir_tabela(
            dados_para_corte,
            colunas_corte,
        )

    # ========================================================
    # 25. EXPORTAR PLANEJAMENTO DIMENSIONAL
    # ========================================================

    imprimir_titulo(
        "25. EXPORTANDO PLANEJAMENTO DIMENSIONAL"
    )

    CAMINHO_DIMENSIONAL.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        CAMINHO_DIMENSIONAL,
        engine="openpyxl",
    ) as writer:

        if planejamento_dimensional is not None:

            planejamento_dimensional.to_excel(
                writer,
                sheet_name="DIMENSIONAL",
                index=False,
            )

        if dados_para_corte is not None:

            dados_para_corte.to_excel(
                writer,
                sheet_name="PREPARADO_CORTE",
                index=False,
            )

        if (
            planejamento_dimensional is not None
            and not planejamento_dimensional.empty
        ):

            resumo_dimensional.to_excel(
                writer,
                sheet_name="RESUMO",
                index=False,
            )

    print()
    print(
        "Arquivo dimensional:"
    )

    print(
        CAMINHO_DIMENSIONAL
    )

    # ========================================================
    # 26. RESUMO FINAL
    # ========================================================

    imprimir_titulo(
        "26. RESUMO FINAL"
    )

    print(
        f"Produto analisado:              "
        f"{PRODUTO}"
    )

    print(
        f"Quantidade de conjuntos:        "
        f"{QUANTIDADE:g}"
    )

    print(
        f"Componentes finais:             "
        f"{total}"
    )

    print(
        f"Componentes cadastrados:        "
        f"{encontrados}"
    )

    print(
        f"Componentes não cadastrados:    "
        f"{nao_encontrados}"
    )

    print(
        f"Necessidades planejadas:        "
        f"{len(planejamento)}"
    )

    print(
        f"Matéria-prima:                  "
        f"{len(materia_prima)}"
    )

    print(
        f"Comercial:                      "
        f"{len(comercial)}"
    )

    print(
        f"Consumo:                        "
        f"{len(consumo)}"
    )

    if planejamento_dimensional is not None:

        print(
            f"Itens dimensionais:             "
            f"{len(planejamento_dimensional)}"
        )

    else:

        print(
            "Itens dimensionais:             0"
        )

    if dados_para_corte is not None:

        print(
            f"Itens preparados para corte:    "
            f"{len(dados_para_corte)}"
        )

    else:

        print(
            "Itens preparados para corte:    0"
        )

    print()

    print(
        "Arquivo de necessidades:"
    )

    print(
        caminho_exportado
    )

    print()

    print(
        "Arquivo dimensional:"
    )

    print(
        CAMINHO_DIMENSIONAL
    )

    # ========================================================
    # FIM
    # ========================================================

    imprimir_titulo(
        "TESTE FINALIZADO COM SUCESSO"
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    main()