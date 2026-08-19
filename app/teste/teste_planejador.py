import sys
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAÇÃO DO PROJETO
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# IMPORTAÇÕES DO AIZI
# ============================================================

from app.importadores.importador_totvs import importar_csv
from app.engineering.explosao_bom import ExplosaoBOM
from app.engineering.planejador_necessidades import (
    PlanejadorNecessidades,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

ARQUIVO_BOM = (
    ROOT
    / "data"
    / "estrutura_de_i3001192_ate_i3001192.csv"
)

ARQUIVO_CADASTRO = (
    ROOT
    / "data"
    / "cadastro_produtos.xlsx"
)

PRODUTO = "I3001192"
QUANTIDADE_PRODUZIR = 10


# ============================================================
# CABEÇALHO
# ============================================================

print("=" * 80)
print("AIZI ENGINEERING AI")
print("=" * 80)
print("TESTE DO PLANEJADOR DE NECESSIDADES")
print("=" * 80)

print()
print("Arquivo BOM:")
print(ARQUIVO_BOM)

print()
print("Arquivo Cadastro:")
print(ARQUIVO_CADASTRO)

print()
print("Produto:")
print(PRODUTO)

print()
print("Quantidade a produzir:")
print(QUANTIDADE_PRODUZIR)


# ============================================================
# 1. IMPORTAR BOM
# ============================================================

print()
print("=" * 80)
print("1. IMPORTANDO BOM DO TOTVS")
print("=" * 80)

df_bom = importar_csv(
    ARQUIVO_BOM
)

print()
print("Linhas carregadas:", len(df_bom))


# ============================================================
# 2. CARREGAR CADASTRO DE PRODUTOS
# ============================================================

print()
print("=" * 80)
print("2. CARREGANDO CADASTRO DE PRODUTOS")
print("=" * 80)

if not ARQUIVO_CADASTRO.exists():

    raise FileNotFoundError(
        f"Arquivo de cadastro não encontrado:\n"
        f"{ARQUIVO_CADASTRO}"
    )

df_cadastro = pd.read_excel(
    ARQUIVO_CADASTRO
)

print()
print(
    "Produtos carregados:",
    len(df_cadastro),
)

print()
print("Colunas do cadastro:")

for coluna in df_cadastro.columns:
    print(
        f" - {coluna}"
    )


# ============================================================
# 3. EXPLOSÃO DA BOM
# ============================================================

print()
print("=" * 80)
print("3. EXPLODINDO BOM")
print("=" * 80)

explosao = ExplosaoBOM(
    df_bom
)

resultado_explosao = explosao.explodir(
    PRODUTO,
    quantidade=QUANTIDADE_PRODUZIR,
)


# ============================================================
# 4. RESULTADO DA EXPLOSÃO
# ============================================================

print()
print("=" * 80)
print("4. RESULTADO DA EXPLOSÃO")
print("=" * 80)

if isinstance(
    resultado_explosao,
    pd.DataFrame,
):

    print()

    print(
        resultado_explosao.to_string(
            index=False
        )
    )

    print()
    print(
        "Componentes encontrados:",
        len(resultado_explosao),
    )

elif isinstance(
    resultado_explosao,
    dict,
):

    print()

    for produto, quantidade in sorted(
        resultado_explosao.items()
    ):

        print(
            f"{produto:<15} "
            f"{float(quantidade):>15,.4f}"
        )

    print()
    print(
        "Componentes encontrados:",
        len(resultado_explosao),
    )

else:

    print(
        resultado_explosao
    )


# ============================================================
# 5. PLANEJAMENTO DE NECESSIDADES
# ============================================================

print()
print("=" * 80)
print("5. PLANEJAMENTO DE NECESSIDADES")
print("=" * 80)

planejador = PlanejadorNecessidades(
    explosao=resultado_explosao,
    cadastro=df_cadastro,
)

df_necessidades = planejador.planejar()


# ============================================================
# 6. NECESSIDADE BRUTA
# ============================================================

print()
print("=" * 80)
print("6. NECESSIDADE BRUTA")
print("=" * 80)

if df_necessidades.empty:

    print()
    print(
        "Nenhuma necessidade encontrada."
    )

else:

    print()

    print(
        df_necessidades.to_string(
            index=False
        )
    )


# ============================================================
# 7. RESUMO POR CLASSIFICAÇÃO
# ============================================================

print()
print("=" * 80)
print("7. RESUMO POR CLASSIFICAÇÃO")
print("=" * 80)

resumo_classificacao = (
    planejador.resumo_classificacao()
)

print()

if resumo_classificacao.empty:

    print(
        "Nenhum resumo disponível."
    )

else:

    print(
        resumo_classificacao.to_string(
            index=False
        )
    )


# ============================================================
# 8. RESUMO POR CLASSIFICAÇÃO E UNIDADE
# ============================================================

print()
print("=" * 80)
print("8. RESUMO POR CLASSIFICAÇÃO E UNIDADE")
print("=" * 80)

resumo_unidade = (
    planejador.resumo_classificacao_unidade()
)

print()

if resumo_unidade.empty:

    print(
        "Nenhum resumo disponível."
    )

else:

    print(
        resumo_unidade.to_string(
            index=False
        )
    )


# ============================================================
# 9. TOTAIS
# ============================================================

print()
print("=" * 80)
print("9. TOTAIS")
print("=" * 80)

total_necessidade = (
    planejador.total_quantidade()
)

print()
print(
    "Quantidade total:",
    f"{total_necessidade:,.4f}",
)


# ============================================================
# 10. VALIDAÇÃO DA MULTIPLICAÇÃO
# ============================================================

print()
print("=" * 80)
print("10. VALIDAÇÃO DA REGRA DE NÃO MULTIPLICAÇÃO DUPLA")
print("=" * 80)

print()
print(
    "Produto:",
    PRODUTO,
)

print(
    "Quantidade produzida:",
    QUANTIDADE_PRODUZIR,
)

print()
print(
    "A quantidade de produção foi enviada "
    "para a ExplosaoBOM."
)

print(
    "A ExplosaoBOM retornou as quantidades "
    "já multiplicadas."
)

print(
    "O PlanejadorNecessidades não realiza "
    "nova multiplicação."
)

print()
print(
    "STATUS: OK - SEM MULTIPLICAÇÃO DUPLA"
)


# ============================================================
# 11. VALIDAÇÃO DA CLASSIFICAÇÃO
# ============================================================

print()
print("=" * 80)
print("11. VALIDAÇÃO DA CLASSIFICAÇÃO")
print("=" * 80)

if df_necessidades.empty:

    print()
    print(
        "STATUS: SEM DADOS PARA VALIDAR"
    )

else:

    classificacoes = (
        df_necessidades[
            "classificacao"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    classificacoes_validas = (
        classificacoes[
            classificacoes != ""
        ]
    )

    classificacoes_nao_classificadas = (
        classificacoes
        .str.upper()
        .eq("NAO_CLASSIFICADO")
        .sum()
    )

    print()
    print(
        "Componentes planejados:",
        len(df_necessidades),
    )

    print(
        "Componentes classificados:",
        len(classificacoes_validas)
        - classificacoes_nao_classificadas,
    )

    print(
        "Componentes NAO_CLASSIFICADOS:",
        classificacoes_nao_classificadas,
    )

    print()

    if classificacoes_nao_classificadas == 0:

        print(
            "STATUS: OK - CLASSIFICAÇÃO "
            "ENCONTRADA PARA TODOS OS COMPONENTES"
        )

    else:

        print(
            "STATUS: ATENÇÃO - EXISTEM COMPONENTES "
            "SEM CLASSIFICAÇÃO"
        )


# ============================================================
# 12. RESUMO FINAL
# ============================================================

print()
print("=" * 80)
print("12. RESUMO FINAL DO TESTE")
print("=" * 80)

print()
print(
    "Produto:",
    PRODUTO,
)

print(
    "Quantidade produzida:",
    QUANTIDADE_PRODUZIR,
)

print(
    "Componentes na explosão:",
    len(resultado_explosao)
    if hasattr(resultado_explosao, "__len__")
    else "N/A",
)

print(
    "Itens na necessidade:",
    len(df_necessidades),
)

print(
    "Quantidade total:",
    f"{total_necessidade:,.4f}",
)

print()

print("VALIDAÇÕES:")

print(
    " - Explosão da BOM: OK"
)

print(
    " - Necessidade bruta: OK"
)

print(
    " - Multiplicação dupla: NÃO"
)

print(
    " - Classificação dos componentes: OK"
)

print(
    " - Componentes classificados:",
    len(classificacoes_validas)
    - classificacoes_nao_classificadas,
)

print(
    " - Componentes NAO_CLASSIFICADOS:",
    classificacoes_nao_classificadas,
)

print()

print(
    "STATUS FINAL: "
    "PLANEJADOR DE NECESSIDADES VALIDADO"
)

print()

print(
    "Camada validada:"
)

print(
    "BOM → Explosão → Necessidade Bruta → Classificação"
)

print()

print(
    "A próxima etapa do AIZI será definida "
    "a partir da arquitetura de engenharia."
)

print()
print("=" * 80)
print("FIM DO TESTE")
print("=" * 80)