from app.engineering.motor_engenharia import MotorEngenharia


def main():
    print("=" * 60)
    print("AIZI ENGINEERING AI")
    print("TESTE DO CADASTRO DE PRODUTOS")
    print("=" * 60)

    motor = MotorEngenharia()

    cadastro = motor.carregar_cadastro()

    print()
    print("Primeiros produtos do cadastro:")
    print()

    print(
        cadastro[
            [
                "CODIGO_PRODUTO",
                "DESCRICAO_PRODUTO",
                "UNIDADE_MEDIDA",
                "TIPO",
                "DESCRICAO_TIPO",
            ]
        ].head(20).to_string(index=False)
    )

    print()
    print("=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)


if __name__ == "__main__":
    main()