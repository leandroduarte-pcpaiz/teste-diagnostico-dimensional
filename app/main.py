from app.database.database import Base, engine
from app.database import models


def iniciar_banco():
    Base.metadata.create_all(bind=engine)
    print("======================================")
    print(" AIZI Engineering AI")
    print(" Banco de dados criado com sucesso!")
    print("======================================")


if __name__ == "__main__":
    iniciar_banco()