import re
import fitz
import tkinter as tk

from tkinter import filedialog


class ExtratorDesenho:
    """
    Extrator de informações de desenhos técnicos em PDF.

    Estrutura:

    PDF
      ↓
    Dados do desenho
      ↓
    Informações estruturadas
    """

    def __init__(self, caminho_pdf):
        self.caminho_pdf = caminho_pdf
        self.texto = ""
        self.documento = None

    def carregar_pdf(self):
        """
        Abre o PDF e extrai o texto.
        """

        self.documento = fitz.open(
            self.caminho_pdf
        )

        textos = []

        for pagina in self.documento:

            textos.append(
                pagina.get_text()
            )

        self.texto = "\n".join(
            textos
        )

        return self.texto

    def fechar_pdf(self):
        """
        Fecha o documento PDF.
        """

        if self.documento is not None:

            self.documento.close()

            self.documento = None

    def extrair_codigo(self):
        """
        Procura o código da peça.

        Exemplo:

        I1044988
        """

        padrao = r"\bI\d{7}\b"

        resultado = re.search(
            padrao,
            self.texto,
            re.IGNORECASE,
        )

        if resultado:

            return resultado.group(
                0
            ).upper()

        return None

    def extrair_materia_prima(self):
        """
        Procura o código da matéria-prima.

        Exemplo:

        G2005887
        """

        padrao = r"\bG\d{7}\b"

        resultado = re.search(
            padrao,
            self.texto,
            re.IGNORECASE,
        )

        if resultado:

            return resultado.group(
                0
            ).upper()

        return None

    def extrair_descricao(self):
        """
        Extrai a descrição diretamente da
        região visual do campo DESCRIÇÃO.

        Estratégia:

        1. Localiza o texto DESCRIÇÃO.
        2. Identifica sua posição na página.
        3. Procura a linha imediatamente abaixo.
        4. Pega somente as palavras pertencentes
           à região do campo.
        """

        if self.documento is None:

            self.carregar_pdf()

        for pagina in self.documento:

            palavras = pagina.get_text(
                "words"
            )

            campo_descricao = None

            # -------------------------------------------------
            # LOCALIZA O CAMPO "DESCRIÇÃO"
            # -------------------------------------------------

            for palavra in palavras:

                texto = palavra[4].strip()

                if texto.upper() == "DESCRIÇÃO":

                    campo_descricao = palavra

                    break

            if campo_descricao is None:

                continue

            label_x0 = campo_descricao[0]
            label_y0 = campo_descricao[1]
            label_x1 = campo_descricao[2]
            label_y1 = campo_descricao[3]

            label_centro_y = (
                label_y0 + label_y1
            ) / 2

            # -------------------------------------------------
            # PROCURA A LINHA ABAIXO
            # -------------------------------------------------

            candidatos = []

            for palavra in palavras:

                texto = palavra[4].strip()

                x0 = palavra[0]
                y0 = palavra[1]
                x1 = palavra[2]
                y1 = palavra[3]

                if not texto:

                    continue

                # Não considera o próprio campo
                if texto.upper() == "DESCRIÇÃO":

                    continue

                centro_y = (
                    y0 + y1
                ) / 2

                # -------------------------------------------------
                # A palavra deve estar abaixo do campo DESCRIÇÃO.
                #
                # Usamos o centro da palavra porque no PDF
                # o texto REFORÇO 4 começa alguns pixels antes
                # do final da caixa do título.
                # -------------------------------------------------

                if centro_y <= label_centro_y:

                    continue

                diferenca_y = (
                    centro_y
                    - label_centro_y
                )

                # A descrição está logo abaixo.
                #
                # Valores maiores pertencem a outros campos.
                if diferenca_y > 25:

                    continue

                # -------------------------------------------------
                # LIMITAÇÃO HORIZONTAL
                #
                # A descrição começa praticamente no mesmo
                # X do campo DESCRIÇÃO.
                # -------------------------------------------------

                if x1 < label_x0:

                    continue

                # Não deixa alcançar campos vizinhos.
                if x0 > label_x0 + 250:

                    continue

                # -------------------------------------------------
                # IGNORA CÓDIGOS
                # -------------------------------------------------

                if re.fullmatch(
                    r"I\d{7}",
                    texto,
                    re.IGNORECASE,
                ):

                    continue

                if re.fullmatch(
                    r"G\d{7}",
                    texto,
                    re.IGNORECASE,
                ):

                    continue

                # -------------------------------------------------
                # IGNORA DATAS
                # -------------------------------------------------

                if re.fullmatch(
                    r"\d{2}/\d{2}/\d{4}",
                    texto,
                ):

                    continue

                # -------------------------------------------------
                # IGNORA CAMPOS ADMINISTRATIVOS
                # -------------------------------------------------

                palavras_ignoradas = {
                    "MATERIAL",
                    "CÓDIGO",
                    "ESCALA",
                    "PROJETISTA",
                    "DESENHISTA",
                    "DATA",
                    "PESO",
                    "LÍQUIDO",
                    "UNIDADE",
                    "LINHA",
                    "FOLHA",
                    "1ºDIEDRO",
                }

                if texto.upper() in palavras_ignoradas:

                    continue

                candidatos.append(
                    (
                        x0,
                        texto,
                    )
                )

            # -------------------------------------------------
            # MONTA A DESCRIÇÃO
            # -------------------------------------------------

            if candidatos:

                candidatos.sort(
                    key=lambda item: item[0]
                )

                descricao = " ".join(
                    item[1]
                    for item in candidatos
                )

                descricao = descricao.strip()

                if descricao:

                    return descricao

        return None

    def extrair_material(self):
        """
        Extrai a descrição do material.

        Exemplo:

        CH AÇO ASTM A36
        """

        padrao = (
            r"\b"
            r"(CH\s+AÇO.*?)"
            r"\s+\d+[,.]\d+\s*mm"
        )

        resultado = re.search(
            padrao,
            self.texto,
            re.IGNORECASE,
        )

        if resultado:

            return resultado.group(
                1
            ).strip()

        return None

    def extrair_espessura(self):
        """
        Extrai a espessura da matéria-prima.
        """

        padrao = (
            r"\bG\d{7}\b"
            r"\s+"
            r"CH\s+AÇO.*?"
            r"(\d+[,.]\d+)\s*mm"
        )

        resultado = re.search(
            padrao,
            self.texto,
            re.IGNORECASE,
        )

        if resultado:

            return float(
                resultado.group(1)
                .replace(",", ".")
            )

        return None

    def extrair_peso(self):
        """
        Extrai o peso líquido.
        """

        padrao = (
            r"PESO\s+LÍQUIDO\s*"
            r"\n\s*"
            r"(\d+[,.]\d+)\s*Kg"
        )

        resultado = re.search(
            padrao,
            self.texto,
            re.IGNORECASE,
        )

        if resultado:

            return float(
                resultado.group(1)
                .replace(",", ".")
            )

        return None

    def extrair_unidade(self):
        """
        Extrai a unidade do desenho.
        """

        padrao = (
            r"UNIDADE\s*"
            r"\n\s*"
            r"(mm)"
        )

        resultado = re.search(
            padrao,
            self.texto,
            re.IGNORECASE,
        )

        if resultado:

            return resultado.group(1)

        return None

    def extrair_dobras(self):
        """
        Extrai indicações de dobra.

        Exemplo:

        PARA CIMA 90° R 10
        """

        padrao = (
            r"PARA\s+CIMA\s+"
            r"90[°º]\s+"
            r"R\s*(\d+(?:[,.]\d+)?)"
        )

        resultados = re.findall(
            padrao,
            self.texto,
            re.IGNORECASE,
        )

        dobras = []

        for raio in resultados:

            dobras.append(
                {
                    "angulo_graus": 90,
                    "direcao": "PARA CIMA",
                    "raio_mm": float(
                        raio.replace(",", ".")
                    ),
                }
            )

        return dobras

    def extrair_dimensoes_geometricas(self):
        """
        Extrai dimensões localizadas na área
        principal do desenho.

        Não considera:

        - códigos
        - datas
        - informações administrativas
        - ângulos
        - raios pequenos
        """

        if self.documento is None:

            self.carregar_pdf()

        dimensoes = []

        for pagina in self.documento:

            largura = pagina.rect.width
            altura = pagina.rect.height

            palavras = pagina.get_text(
                "words"
            )

            for palavra in palavras:

                texto = palavra[4].strip()

                x0 = palavra[0]
                y0 = palavra[1]
                x1 = palavra[2]
                y1 = palavra[3]

                # Precisa ser número
                if not re.fullmatch(
                    r"\d+(?:[,.]\d+)?",
                    texto,
                ):

                    continue

                valor = float(
                    texto.replace(",", ".")
                )

                # Código da peça
                if re.fullmatch(
                    r"I\d{7}",
                    texto,
                    re.IGNORECASE,
                ):

                    continue

                # Código da matéria-prima
                if re.fullmatch(
                    r"G\d{7}",
                    texto,
                    re.IGNORECASE,
                ):

                    continue

                # Datas
                if re.fullmatch(
                    r"\d{2}/\d{2}/\d{4}",
                    texto,
                ):

                    continue

                # Borda da folha
                if (
                    y0 < altura * 0.05
                    or y1 > altura * 0.98
                ):

                    continue

                # Quadro administrativo inferior direito
                #
                # Mantemos a parte inferior esquerda
                # porque pode conter dimensões válidas.
                if (
                    x0 > largura * 0.50
                    and y0 > altura * 0.82
                ):

                    continue

                # 90° = ângulo de dobra
                if valor == 90:

                    continue

                # R10 fica na informação de dobra
                if valor < 15:

                    continue

                dimensoes.append(
                    valor
                )

        return sorted(
            set(dimensoes),
            reverse=True,
        )

    def extrair(self):
        """
        Executa a extração completa.
        """

        self.carregar_pdf()

        try:

            resultado = {
                "codigo_peca":
                    self.extrair_codigo(),

                "descricao":
                    self.extrair_descricao(),

                "materia_prima":
                    self.extrair_materia_prima(),

                "material":
                    self.extrair_material(),

                "espessura_mm":
                    self.extrair_espessura(),

                "peso_kg":
                    self.extrair_peso(),

                "unidade":
                    self.extrair_unidade(),

                "dimensoes_geometricas_mm":
                    self.extrair_dimensoes_geometricas(),

                "dobras":
                    self.extrair_dobras(),
            }

            return resultado

        finally:

            self.fechar_pdf()


def selecionar_pdf():
    """
    Abre a caixa de seleção de arquivos do Windows.
    """

    janela = tk.Tk()

    janela.withdraw()

    caminho = filedialog.askopenfilename(
        title="Selecionar desenho técnico",
        filetypes=[
            (
                "Arquivos PDF",
                "*.pdf",
            ),
            (
                "Todos os arquivos",
                "*.*",
            ),
        ],
    )

    janela.destroy()

    return caminho


if __name__ == "__main__":

    print("=" * 60)
    print("AIZI Engineering AI")
    print("Extrator de Desenho Técnico")
    print("=" * 60)

    print()
    print("Selecione o desenho técnico...")
    print()

    caminho_pdf = selecionar_pdf()

    if not caminho_pdf:

        print()
        print("Nenhum arquivo selecionado.")
        print("Operação cancelada.")

    else:

        print()
        print("Arquivo selecionado:")
        print(caminho_pdf)
        print()

        extrator = ExtratorDesenho(
            caminho_pdf
        )

        resultado = extrator.extrair()

        print("=" * 60)
        print("INFORMAÇÕES EXTRAÍDAS")
        print("=" * 60)

        for chave, valor in resultado.items():

            print(
                f"{chave}: {valor}"
            )

        print("=" * 60)