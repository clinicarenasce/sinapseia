import os
import json
from datetime import datetime

HISTORICO_PATH = os.path.join(os.path.expanduser("~"), ".transcritor_historico.json")


def carregar_historico():
    try:
        with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def salvar_historico(nome, path, tipo):
    historico = carregar_historico()
    entry = {"nome": nome, "path": path, "tipo": tipo, "data": datetime.now().strftime("%d/%m %H:%M")}
    historico.insert(0, entry)
    historico = historico[:50]
    with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False)
