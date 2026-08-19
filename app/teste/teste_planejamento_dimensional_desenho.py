from __future__ import annotations

import os
import sys


# ==============================================================
# GARANTE QUE A RAIZ DO PROJETO ESTEJA NO PYTHONPATH
# ==============================================================

RAIZ_PROJETO = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

if RAIZ_PROJETO not in sys.path:
    sys.path.insert(
        0,
        RAIZ_PROJETO,
    )


from app.engineering.extrator_desenho import ExtratorDesenho
from app.engineering.planejador_dimensional import (
    PlanejadorDimensional,
)


# ==============================================================
# CONFIGURAÇÃO
# ==============================================================

CAMINHO_PDF_PADRAO = (
    r"U:\I1 PC PRODUZIDAS\I1044\I1044988.pdf"
)


# ==============================================================
# FUNÇÕES AUXILIARES
# ==============================================================


def imprimir_linha():
    print("=" * 80)


def imprimir_cabecalho(titulo):
    print()
    imprimir_linha()
    print(titulo)
    imprimir_linha()


def selecionar_pdf():
    """
    Permite selecionar outro PDF caso o arquivo padrão
    não exista.
    """

    try:
        import tkinter as tk

        from tkinter import filedialog

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

    except Exception as erro:

        print()
        print(
            "Não foi possível abrir a seleção "
            f"de arquivo: {erro}"
        )

        return ""


# ==============================================================
# TESTE PRINCIPAL
# ==============================================================


def main():

    print()
    imprimir_linha()
    print(
        "TESTE INTEGRADO - "
        "DESENHO + PLANEJADOR DIMENSIONAL"
    )
    imprimir_linha()

    # ----------------------------------------------------------
    # LOCALIZAÇÃO DO PDF
    # ----------------------------------------------------------

    caminho_pdf = CAMINHO_PDF_PADRAO

    if not os.path.isfile(caminho_pdf):

        print()
        print(
            "Arquivo PDF padrão não encontrado:"
        )

        print(
            caminho_pdf
        )

        print()
        print(
            "Selecione o desenho técnico manualmente."
        )

        caminho_pdf = selecionar_pdf()

    if not caminho_pdf:

        print()
        print(
            "Nenhum PDF selecionado."
        )

        print(
            "Teste cancelado."
        )

        return

    # ----------------------------------------------------------
    # 1. PDF
    # ----------------------------------------------------------

    imprimir_cabecalho(
        "1. DESENHO TÉCNICO"
    )

    print(
        "Arquivo:"
    )

    print(
        caminho_pdf
    )

    # ----------------------------------------------------------
    # 2. EXTRATOR
    # ----------------------------------------------------------

    imprimir_cabecalho(
        "2. EXTRATOR DE DESENHO"
    )

    extrator = ExtratorDesenho(
        caminho_pdf
    )

    dados = extrator.extrair()

    print(
        "Código da peça:"
    )

    print(
        dados.get("codigo_peca")
    )

    print()

    print(
        "Descrição:"
    )

    print(
        dados.get("descricao")
    )

    print()

    print(
        "Matéria-prima:"
    )

    print(
        dados.get("materia_prima")
    )

    print()

    print(
        "Material:"
    )

    print(
        dados.get("material")
    )

    print()

    print(
        "Espessura:"
    )

    print(
        f"{dados.get('espessura_mm')} mm"
    )

    print()

    print(
        "Peso:"
    )

    print(
        f"{dados.get('peso_kg')} kg"
    )

    print()

    print(
        "Unidade:"
    )

    print(
        dados.get("unidade")
    )

    print()

    print(
        "Dimensões geométricas:"
    )

    print(
        dados.get(
            "dimensoes_geometricas_mm"
        )
    )

    print()

    print(
        "Dobras:"
    )

    dobras = dados.get(
        "dobras"
    )

    if dobras:

        for numero, dobra in enumerate(
            dobras,
            start=1,
        ):

            print(
                f"  Dobra {numero}: "
                f"{dobra.get('angulo_graus')}° "
                f"{dobra.get('direcao')} "
                f"R{dobra.get('raio_mm')} mm"
            )

    else:

        print(
            "  Nenhuma dobra identificada."
        )

    # ----------------------------------------------------------
    # 3. VALIDAÇÃO DA EXTRAÇÃO
    # ----------------------------------------------------------

    imprimir_cabecalho(
        "3. VALIDAÇÃO DA EXTRAÇÃO"
    )

    campos_obrigatorios = {
        "codigo_peca": dados.get(
            "codigo_peca"
        ),
        "materia_prima": dados.get(
            "materia_prima"
        ),
        "espessura_mm": dados.get(
            "espessura_mm"
        ),
        "dimensoes_geometricas_mm": dados.get(
            "dimensoes_geometricas_mm"
        ),
    }

    extracao_ok = True

    for campo, valor in campos_obrigatorios.items():

        if valor is None or valor == []:

            print(
                f"ATENÇÃO - "
                f"{campo}: NÃO ENCONTRADO"
            )

            extracao_ok = False

        else:

            print(
                f"OK - "
                f"{campo}: {valor}"
            )

    print()

    if extracao_ok:

        print(
            "OK - informações principais "
            "do desenho extraídas."
        )

    else:

        print(
            "ATENÇÃO - existem informações "
            "que precisam de tratamento."
        )

    # ----------------------------------------------------------
    # 4. PLANEJADOR DIMENSIONAL
    # ----------------------------------------------------------

    imprimir_cabecalho(
        "4. PLANEJADOR DIMENSIONAL"
    )

    planejador = PlanejadorDimensional()

    print(
        "Objeto PlanejadorDimensional criado."
    )

    resultado_dimensional = (
        planejador.analisar_peca_extraida(
            dados
        )
    )

    print()

    print(
        "Tipo dimensional:"
    )

    print(
        resultado_dimensional.get(
            "tipo_dimensional"
        )
    )

    print()

    print(
        "Status dimensional:"
    )

    print(
        resultado_dimensional.get(
            "status_dimensional"
        )
    )

    print()

    print(
        "Material identificado:"
    )

    print(
        resultado_dimensional.get(
            "material"
        )
    )

    print()

    print(
        "Espessura:"
    )

    print(
        resultado_dimensional.get(
            "espessura_mm"
        )
    )

    print()

    print(
        "Largura padrão:"
    )

    print(
        resultado_dimensional.get(
            "largura_padrao_mm"
        )
    )

    print()

    print(
        "Comprimento padrão:"
    )

    print(
        resultado_dimensional.get(
            "comprimento_padrao_mm"
        )
    )

    print()

    print(
        "Largura efetiva:"
    )

    print(
        resultado_dimensional.get(
            "largura_efetiva_mm"
        )
    )

    print()

    print(
        "Comprimento efetivo:"
    )

    print(
        resultado_dimensional.get(
            "comprimento_efetivo_mm"
        )
    )

    print()

    print(
        "Preparado para corte:"
    )

    print(
        resultado_dimensional.get(
            "preparado_para_corte"
        )
    )

    # ----------------------------------------------------------
    # 5. DETERMINAÇÃO DO BLANK
    # ----------------------------------------------------------

    imprimir_cabecalho(
        "5. DETERMINAÇÃO DO BLANK"
    )

    blank = (
        PlanejadorDimensional.determinar_blank(
            resultado_dimensional
        )
    )

    if blank is None:

        print(
            "BLANK: não determinado."
        )

    else:

        print(
            "BLANK determinado pelo "
            "PlanejadorDimensional:"
        )

        for chave, valor in blank.items():

            print(
                f"{chave}: {valor} mm"
            )

    # ----------------------------------------------------------
    # 6. DIMENSÕES DO DESENHO
    # ----------------------------------------------------------

    imprimir_cabecalho(
        "6. DIMENSÕES EXTRAÍDAS DO DESENHO"
    )

    dimensoes = dados.get(
        "dimensoes_geometricas_mm",
        [],
    )

    if dimensoes:

        for numero, dimensao in enumerate(
            dimensoes,
            start=1,
        ):

            print(
                f"Dimensão {numero}: "
                f"{dimensao} mm"
            )

    else:

        print(
            "Nenhuma dimensão geométrica "
            "encontrada."
        )

    # ----------------------------------------------------------
    # 7. DOBRAS
    # ----------------------------------------------------------

    imprimir_cabecalho(
        "7. DOBRAS IDENTIFICADAS"
    )

    if dobras:

        print(
            f"Quantidade de dobras: "
            f"{len(dobras)}"
        )

        for numero, dobra in enumerate(
            dobras,
            start=1,
        ):

            print()

            print(
                f"Dobra {numero}"
            )

            print(
                f"  Ângulo: "
                f"{dobra.get('angulo_graus')}°"
            )

            print(
                f"  Direção: "
                f"{dobra.get('direcao')}"
            )

            print(
                f"  Raio: "
                f"{dobra.get('raio_mm')} mm"
            )

    else:

        print(
            "Nenhuma dobra identificada."
        )

    # ----------------------------------------------------------
    # 8. MATÉRIA-PRIMA x BLANK
    # ----------------------------------------------------------

    imprimir_cabecalho(
        "8. MATÉRIA-PRIMA x BLANK"
    )

    print(
        "MATÉRIA-PRIMA COMERCIAL:"
    )

    print(
        f"  Largura: "
        f"{resultado_dimensional.get('largura_efetiva_mm')} mm"
    )

    print(
        f"  Comprimento: "
        f"{resultado_dimensional.get('comprimento_efetivo_mm')} mm"
    )

    print()

    print(
        "IMPORTANTE:"
    )

    print(
        "As dimensões acima representam "
        "a matéria-prima comercial."
    )

    print(
        "Elas NÃO devem ser consideradas "
        "automaticamente como o blank da peça."
    )

    print()

    print(
        "BLANK DA PEÇA:"
    )

    if blank:

        for chave, valor in blank.items():

            print(
                f"  {chave}: {valor} mm"
            )

    else:

        print(
            "  Ainda não determinado."
        )

    # ----------------------------------------------------------
    # 9. PREPARAÇÃO PARA CALCULADORA DE CORTE
    # ----------------------------------------------------------

    imprimir_cabecalho(
        "9. PREPARAÇÃO PARA CALCULADORA DE CORTE"
    )

    tipo = resultado_dimensional.get(
        "tipo_dimensional"
    )

    tem_dobras = bool(
        dados.get("dobras")
    )

    dimensoes_validas = (
        len(dimensoes) >= 2
    )

    print(
        f"Tipo dimensional: {tipo}"
    )

    print(
        "Possui dobras: "
        f"{'SIM' if tem_dobras else 'NÃO'}"
    )

    print(
        "Possui pelo menos duas dimensões: "
        f"{'SIM' if dimensoes_validas else 'NÃO'}"
    )

    print()

    if tipo == "CHAPA" and tem_dobras:

        print(
            "ATENÇÃO:"
        )

        print(
            "Peça de CHAPA com DOBRAS detectada."
        )

        print(
            "A CalculadoraCorte não será chamada "
            "diretamente neste teste."
        )

        print()

        print(
            "Motivo:"
        )

        print(
            "é necessário determinar corretamente "
            "o desenvolvimento da peça antes de "
            "transformar a geometria final em BLANK."
        )

    elif tipo == "CHAPA" and dimensoes_validas:

        print(
            "CHAPA sem dobras identificadas."
        )

        print(
            "Pode futuramente ser encaminhada "
            "diretamente para a CalculadoraCorte."
        )

    else:

        print(
            "Peça ainda não está pronta para "
            "ser enviada à CalculadoraCorte."
        )

    # ----------------------------------------------------------
    # 10. RESULTADO FINAL
    # ----------------------------------------------------------

    imprimir_cabecalho(
        "10. RESULTADO FINAL DO TESTE"
    )

    print(
        f"Código: "
        f"{dados.get('codigo_peca')}"
    )

    print(
        f"Matéria-prima: "
        f"{dados.get('materia_prima')}"
    )

    print(
        f"Tipo dimensional: "
        f"{tipo}"
    )

    print(
        f"Espessura: "
        f"{dados.get('espessura_mm')} mm"
    )

    print(
        f"Dimensões extraídas: "
        f"{dimensoes}"
    )

    print(
        f"Dobras identificadas: "
        f"{len(dobras) if dobras else 0}"
    )

    print(
        f"BLANK atual: "
        f"{blank}"
    )

    print()

    print(
        "TESTE DE INTEGRAÇÃO "
        "DESENHO + PLANEJADOR DIMENSIONAL "
        "CONCLUÍDO."
    )

    imprimir_linha()


# ==============================================================
# EXECUÇÃO
# ==============================================================


if __name__ == "__main__":
    main()