from pathlib import Path

EXTENSOES = {
    ".pdf",
    ".dxf",
    ".sldprt",
    ".slddrw"
}


def localizar_arquivos(pasta):

    pasta = Path(pasta)

    arquivos = []

    for arquivo in pasta.rglob("*"):

        if arquivo.is_file():

            if arquivo.suffix.lower() in EXTENSOES:

                arquivos.append(arquivo)

    return arquivos