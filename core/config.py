import os
import json

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".sinapseia_config.json")
VALIDAR_URL = "https://validar-sinapseia.clinicarenasce.workers.dev"
_OLD_CONFIG = os.path.join(os.path.expanduser("~"), ".spongi_config.json")
if os.path.exists(_OLD_CONFIG) and not os.path.exists(CONFIG_PATH):
    os.rename(_OLD_CONFIG, CONFIG_PATH)


def carregar_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def salvar_config(chave, valor):
    config = carregar_config()
    config[chave] = valor
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False)


def salvar_groq_key(key):
    salvar_config("groq_api_key", key.strip())
    return True


def tem_groq_key():
    config = carregar_config()
    return bool(config.get("groq_api_key", ""))


def get_vault_ativo():
    config = carregar_config()
    return config.get("obsidian_vault", "")


def set_vault_ativo(path):
    salvar_config("obsidian_vault", path)


def is_first_run():
    config = carregar_config()
    return not config.get("onboarding_done", False)


def mark_onboarding_done():
    salvar_config("onboarding_done", True)


def tem_logseq_config():
    config = carregar_config()
    return bool(config.get("logseq_graph", ""))


def tem_pro():
    config = carregar_config()
    return bool(config.get("pro_ativo", False))


def ativar_pro(chave):
    """Validates and activates a Pro license key. Returns dict {ok, erro?, aviso?}."""
    import re
    import urllib.request
    chave = chave.strip().upper()
    if not re.match(r'^SINAPSE-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$', chave):
        return {"ok": False, "erro": "Formato invalido. Use SINAPSE-XXXX-XXXX-XXXX"}

    try:
        payload = json.dumps({"chave": chave}).encode()
        req = urllib.request.Request(
            VALIDAR_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        if data.get("valid"):
            salvar_config("pro_ativo", True)
            salvar_config("pro_chave", chave)
            return {"ok": True}
        return {"ok": False, "erro": "Assinatura inativa ou nao encontrada"}
    except Exception:
        return {"ok": False, "erro": "Sem conexao com o servidor. Verifique sua internet e tente novamente."}
