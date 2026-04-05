import os
import threading
from datetime import datetime
from tkinter import filedialog, Tk
from core.config import carregar_config, get_vault_ativo, set_vault_ativo
from core.ai import groq_gerar, PROMPT_OBSIDIAN
from core.naming import gerar_nome_inteligente
from core.storage import salvar_historico
from core.wikilinks import ler_tags_vault, criar_stubs_wikilinks
from core.platform_utils import play_beep, drives_extras

_DEFAULT_VAULT = os.path.join(os.path.expanduser("~"), "Desktop")


def _get_vault():
    """Retorna vault ativo do config ou fallback."""
    vault = get_vault_ativo()
    return vault if vault and os.path.isdir(vault) else _DEFAULT_VAULT


def detectar_vaults():
    """Escaneia diretorios comuns por pastas .obsidian/. Retorna lista de {name, path}."""
    home = os.path.expanduser("~")
    candidatos = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Documents"),
        os.path.join(home, "Documentos"),
        os.path.join(home, "OneDrive"),
        # Mac: iCloud Drive (Obsidian sync nativo)
        os.path.join(home, "Library", "Mobile Documents", "iCloud~md~obsidian", "Documents"),
        # Mac: iCloud Drive geral
        os.path.join(home, "Library", "Mobile Documents", "com~apple~CloudDocs"),
        # Mac: Google Drive
        os.path.join(home, "Library", "CloudStorage"),
        home,
    ]
    # Expandir subpastas do Google Drive / iCloud CloudStorage (até 2 níveis)
    cloudStorage = os.path.join(home, "Library", "CloudStorage")
    if os.path.isdir(cloudStorage):
        try:
            for drive in os.listdir(cloudStorage):
                drive_path = os.path.join(cloudStorage, drive)
                candidatos.append(drive_path)
                if os.path.isdir(drive_path):
                    try:
                        for sub in os.listdir(drive_path):
                            sub_path = os.path.join(drive_path, sub)
                            if os.path.isdir(sub_path):
                                candidatos.append(sub_path)
                    except PermissionError:
                        pass
        except PermissionError:
            pass
    candidatos.extend(drives_extras())

    vaults = []
    visitados = set()
    for base in candidatos:
        if not os.path.isdir(base):
            continue
        try:
            for item in os.listdir(base):
                pasta = os.path.join(base, item)
                if pasta in visitados:
                    continue
                visitados.add(pasta)
                if os.path.isdir(pasta) and os.path.isdir(os.path.join(pasta, ".obsidian")):
                    vaults.append({"name": item, "path": pasta})
        except PermissionError:
            continue
    return vaults


def selecionar_vault(path):
    """Define o vault ativo no config. Requer pasta com .obsidian/ dentro."""
    if os.path.isdir(path) and os.path.isdir(os.path.join(path, ".obsidian")):
        set_vault_ativo(path)
        return True
    return False


def _texto_com_tags(texto, vault_path):
    """Appends existing vault tags as context to the user message."""
    tags = ler_tags_vault(vault_path)
    if tags:
        return texto + f"\n\n[Tags existentes no vault: {', '.join(tags)}]"
    return texto


def formatar_obsidian(texto, callbacks):
    """Formata texto para Obsidian. callbacks: on_status_obsidian, on_obsidian_formatado, on_erro"""
    def _run():
        try:
            config = carregar_config()
            if not config.get("groq_api_key"):
                callbacks["on_erro"]("Configure sua API key do Groq primeiro.")
                return
            callbacks["on_status_obsidian"]("Formatando com IA...")
            texto_enriquecido = _texto_com_tags(texto, _get_vault())
            resultado = groq_gerar(texto_enriquecido, max_tokens=4096, system=PROMPT_OBSIDIAN)
            if resultado == "__INVALID_KEY__":
                callbacks["on_erro"]("API key do Groq invalida.")
                return
            if resultado == "__DAILY_LIMIT__":
                callbacks["on_erro"]("Limite diario de tokens do Groq atingido. O limite reseta em algumas horas.")
                return
            if resultado and resultado.strip():
                callbacks["on_obsidian_formatado"](resultado.strip())
            else:
                callbacks["on_erro"]("O modelo nao retornou texto. Tente novamente.")
        except Exception as e:
            callbacks["on_erro"](f"Erro: {e}")
    threading.Thread(target=_run, daemon=True).start()


def salvar_obsidian(conteudo, nome_inteligente, nome_custom, callbacks):
    """Salva .md no vault. callbacks: on_salvar_obs_concluido, on_erro"""
    def _run():
        try:
            nome = (nome_custom or nome_inteligente or f"SinapseIA_{datetime.now().strftime('%Y%m%d_%H%M%S')}").strip()
            nome = "".join(c for c in nome if c not in r'\/:*?"<>|').strip() or "SinapseIA"
            vault = get_vault_ativo()
            if not vault or not os.path.isdir(vault):
                callbacks["on_erro"]("Nenhum vault Obsidian configurado. Acesse Configuracoes e selecione seu vault.")
                return
            os.makedirs(vault, exist_ok=True)
            path = os.path.join(vault, f"{nome}.md")
            if os.path.exists(path):
                ts = datetime.now().strftime("_%H%M%S")
                path = os.path.join(vault, f"{nome}{ts}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(conteudo)
            criar_stubs_wikilinks(conteudo, vault)
            salvar_historico(nome, path, "obsidian")
            callbacks["on_salvar_obs_concluido"](path, os.path.basename(path))
        except Exception as e:
            callbacks["on_erro"](f"Erro ao salvar: {e}")
    threading.Thread(target=_run, daemon=True).start()


def salvar_obsidian_em(conteudo, pasta, nome_inteligente, nome_custom, callbacks):
    """Salva .md em pasta especifica. callbacks: on_salvar_obs_concluido, on_erro"""
    def _run():
        try:
            nome = (nome_custom or nome_inteligente or f"SinapseIA_{datetime.now().strftime('%Y%m%d_%H%M%S')}").strip()
            nome = "".join(c for c in nome if c not in r'\/:*?"<>|').strip() or "SinapseIA"
            os.makedirs(pasta, exist_ok=True)
            path = os.path.join(pasta, f"{nome}.md")
            if os.path.exists(path):
                ts = datetime.now().strftime("_%H%M%S")
                path = os.path.join(pasta, f"{nome}{ts}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(conteudo)
            criar_stubs_wikilinks(conteudo, pasta)
            salvar_historico(nome, path, "obsidian")
            callbacks["on_salvar_obs_concluido"](path, os.path.basename(path))
        except Exception as e:
            callbacks["on_erro"](f"Erro ao salvar: {e}")
    threading.Thread(target=_run, daemon=True).start()


def formatar_texto_direto(texto, callbacks):
    """Formata texto livre para Obsidian. callbacks: on_status_obsidian, on_texto_direto_concluido, on_erro"""
    def _run():
        try:
            config = carregar_config()
            if not config.get("groq_api_key"):
                callbacks["on_erro"]("Configure sua API key do Groq primeiro.")
                return

            callbacks["on_status_obsidian"]("Gerando nome...")
            nome = gerar_nome_inteligente(texto)

            callbacks["on_status_obsidian"]("Formatando com IA...")
            texto_enriquecido = _texto_com_tags(texto, _get_vault())
            resultado = groq_gerar(texto_enriquecido, max_tokens=4096, system=PROMPT_OBSIDIAN)
            if resultado == "__INVALID_KEY__":
                callbacks["on_erro"]("API key do Groq invalida.")
                return
            if resultado == "__DAILY_LIMIT__":
                callbacks["on_erro"]("Limite diario de tokens do Groq atingido. O limite reseta em algumas horas.")
                return
            if not resultado or not resultado.strip():
                callbacks["on_erro"]("O modelo nao retornou texto.")
                return

            play_beep()
            callbacks["on_texto_direto_concluido"](resultado.strip(), "", nome)
        except Exception as e:
            callbacks["on_erro"](f"Erro: {e}")
    threading.Thread(target=_run, daemon=True).start()


def escolher_pasta_obsidian():
    from core.platform_utils import escolher_pasta_nativa
    return escolher_pasta_nativa("Escolha a pasta dentro do Obsidian", _get_vault())
