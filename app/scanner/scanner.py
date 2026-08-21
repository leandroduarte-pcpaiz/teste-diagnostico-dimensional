from __future__ import annotations

from pathlib import Path
from typing import Dict, List


EXTENSOES = {
    ".pdf",
    ".dxf",
    ".sldprt",
    ".slddrw",
}


def localizar_arquivos(pasta):
    """Localiza arquivos de desenho suportados recursivamente."""
    pasta = Path(pasta)
    arquivos = []

    for arquivo in pasta.rglob("*"):
        if arquivo.is_file() and arquivo.suffix.lower() in EXTENSOES:
            arquivos.append(arquivo)

    return sorted(arquivos)


def localizar_pares_desenho(pasta) -> List[Dict[str, Path | None]]:
    """
    Localiza PDF e DXF do mesmo desenho na mesma pasta.

    Regra de pareamento:
        mesmo nome-base -> par PDF/DXF.

    Se existir somente um dos formatos, o registro continua existindo.
    Isso permite usar DXF como fonte geométrica preferencial e PDF como
    complemento, sem obrigar os dois arquivos a existirem.
    """
    arquivos = localizar_arquivos(pasta)
    grupos: Dict[Path, Dict[str, Path | None]] = {}

    for arquivo in arquivos:
        if arquivo.suffix.lower() not in {".pdf", ".dxf"}:
            continue

        chave = arquivo.with_suffix("").resolve()
        registro = grupos.setdefault(
            chave,
            {
                "base": chave,
                "pdf": None,
                "dxf": None,
            },
        )

        if arquivo.suffix.lower() == ".pdf":
            registro["pdf"] = arquivo
        else:
            registro["dxf"] = arquivo

    return [
        grupos[chave]
        for chave in sorted(grupos, key=lambda p: str(p).lower())
    ]


def selecionar_fonte_geometrica(par: Dict[str, Path | None]) -> Path | None:
    """
    Seleciona a fonte geométrica.

    Prioridade AIZI:
        1. DXF
        2. PDF
    """
    if par.get("dxf") is not None:
        return par["dxf"]
    return par.get("pdf")
