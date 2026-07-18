import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config_impressora.json"


CONFIG_PADRAO = {
    "impressora": "Microsoft Print to PDF",
    "papel": "80mm",
    "impressao_automatica": False
}


def carregar_configuracao():
    if not CONFIG_PATH.exists():
        salvar_configuracao(CONFIG_PADRAO)
        return CONFIG_PADRAO.copy()

    try:
        with open(
            CONFIG_PATH,
            "r",
            encoding="utf-8"
        ) as arquivo:
            config = json.load(arquivo)

        return config

    except Exception:
        return CONFIG_PADRAO.copy()


def salvar_configuracao(config):
    with open(
        CONFIG_PATH,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            config,
            arquivo,
            ensure_ascii=False,
            indent=4
        )