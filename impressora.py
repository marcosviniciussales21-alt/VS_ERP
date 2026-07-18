import win32print
import win32ui


def listar_impressoras():
    flags = (
        win32print.PRINTER_ENUM_LOCAL
        | win32print.PRINTER_ENUM_CONNECTIONS
    )

    impressoras = win32print.EnumPrinters(
        flags
    )

    return [
        item[2]
        for item in impressoras
    ]


def imprimir_texto(
    nome_impressora,
    texto
):
    hprinter = win32print.OpenPrinter(
        nome_impressora
    )

    try:
        hdc = win32ui.CreateDC()

        hdc.CreatePrinterDC(
            nome_impressora
        )

        hdc.StartDoc(
            "VS ERP - Impressão"
        )

        hdc.StartPage()

        fonte = win32ui.CreateFont({
            "name": "Consolas",
            "height": 28,
        })

        hdc.SelectObject(
            fonte
        )

        x = 100
        y = 100

        for linha in texto.splitlines():
            hdc.TextOut(
                x,
                y,
                linha
            )

            y += 35

        hdc.EndPage()
        hdc.EndDoc()

        hdc.DeleteDC()

    finally:
        win32print.ClosePrinter(
            hprinter
        )


def imprimir_teste(
    nome_impressora
):
    texto = """
VS ERP
==============================
IMPRESSAO DE TESTE
==============================

Impressora configurada
com sucesso.

Obrigado!
"""

    imprimir_texto(
        nome_impressora,
        texto
    )


if __name__ == "__main__":
    impressoras = listar_impressoras()

    print(
        "Impressoras encontradas:"
    )

    for indice, nome in enumerate(
        impressoras,
        start=1
    ):
        print(
            f"{indice} - {nome}"
        )