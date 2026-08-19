from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql import func

from app.database.database import Base


class ArquivoTecnico(Base):
    __tablename__ = "arquivos_tecnicos"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nome = Column(String(255), nullable=False)

    caminho = Column(String(1000), nullable=False, unique=True)

    extensao = Column(String(20), nullable=False)

    tamanho = Column(Integer, nullable=False)

    data_modificacao = Column(DateTime)

    criado_em = Column(
        DateTime,
        server_default=func.now()
    )