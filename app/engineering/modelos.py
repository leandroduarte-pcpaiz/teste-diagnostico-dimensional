from dataclasses import dataclass, field


@dataclass
class ItemEngenharia:

    codigo: str
    descricao: str
    tipo: str
    quantidade: float
    nivel: int

    filhos: list = field(default_factory=list)

    def adicionar_filho(self, filho):
        self.filhos.append(filho)