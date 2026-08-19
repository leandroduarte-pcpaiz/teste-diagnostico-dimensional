from pathlib import Path
import pandas as pd


def limpar_codigo(valor):
    if pd.isna(valor):
        return ""

    valor = str(valor)
    valor = valor.replace('="', "")
    valor = valor.replace('"', "")

    return valor.strip()


def importar_csv(caminho_csv):

    print("=" * 50)
    print("AIZI Engineering AI")
    print("Importador TOTVS")
    print("=" * 50)

    arquivo = Path(caminho_csv)

    if not arquivo.exists():
        print("Arquivo não encontrado.")
        return None

    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="latin1"
    )

    df.columns = [
        "nivel",
        "produto",
        "tipo_produto",
        "descricao_produto",
        "um_produto",
        "componente",
        "tipo_componente",
        "descricao_componente",
        "um_componente",
        "quantidade",
        "ipi",
        "ncm",
        "ult_preco",
        "origem",
        "custo_medio"
    ]

    df["produto"] = df["produto"].apply(limpar_codigo)
    df["componente"] = df["componente"].apply(limpar_codigo)

    df["nivel"] = (
        df["nivel"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
        .fillna(0)
        .astype(int)
    )

    df["quantidade"] = (
        df["quantidade"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # Remove linhas completamente vazias
    df = df.dropna(how="all")

    # Remove espaços
    df["produto"] = df["produto"].str.strip()
    df["componente"] = df["componente"].str.strip()

    # Remove registros sem produto ou componente
    df = df[
        (df["produto"] != "") &
        (df["componente"] != "")
    ]

    # Remove linhas duplicadas do CSV
    df = df.drop_duplicates(
        subset=[
            "produto",
            "componente",
            "quantidade"
        ],
        keep="first"
    ).reset_index(drop=True)

    print()
    print(f"Linhas carregadas: {len(df)}")

    return df


if __name__ == "__main__":

    caminho = input("Informe o caminho do CSV: ").strip()

    df = importar_csv(caminho)

    if df is not None:

        from app.engineering.arvore_produto import ArvoreProduto
        from app.engineering.motor_engenharia import MotorEngenharia

        produto = input(
            "Informe o código do produto: "
        ).strip()

        arvore = ArvoreProduto(df)

        estrutura = arvore.montar_arvore(produto)

        print()
        print("=" * 50)
        print("ÁRVORE COMPLETA")
        print("=" * 50)

        for item in estrutura:

            espaco = "   " * item["nivel"]

            print(
                f"{espaco}{item['pai']} -> {item['filho']}"
            )

        # Converte a árvore para DataFrame
        dados_explosao = pd.DataFrame(estrutura)

        # Renomeia as colunas para o formato esperado pelo MotorEngenharia
        dados_explosao = dados_explosao.rename(
            columns={
                "filho": "componente"
            }
        )

        # Soma as quantidades dos componentes
        if "quantidade" in dados_explosao.columns:

            resultado_explosao = (
                dados_explosao
                .groupby("componente", as_index=False)["quantidade"]
                .sum()
                .rename(
                    columns={
                        "quantidade": "quantidade_total"
                    }
                )
            )

        else:

            resultado_explosao = (
                dados_explosao[
                    ["componente"]
                ]
                .drop_duplicates()
            )

            resultado_explosao["quantidade_total"] = 0

        # Enriquecimento com cadastro TOTVS
        motor = MotorEngenharia()

        resultado = motor.gerar_relatorio(
            resultado_explosao
        )