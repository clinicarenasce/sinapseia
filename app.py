import eel
import os
import re
import subprocess
from datetime import datetime
from tkinter import filedialog, Tk

from core.config import salvar_groq_key as _salvar_groq_key, tem_groq_key as _tem_groq_key
from core.storage import carregar_historico as _carregar_historico, salvar_historico
from core.transcriber import (
    transcrever as _do_transcrever,
    cancelar_transcricao as _do_cancelar,
    get_nome_inteligente,
    get_audio_path_atual,
    get_idioma_detectado,
)
from core.ai import traduzir_texto as _traduzir_texto
from core.recorder import (
    listar_dispositivos as _listar_dispositivos,
    iniciar_gravacao as _do_iniciar_gravacao,
    pausar_gravacao as _do_pausar,
    parar_gravacao as _do_parar,
    cancelar_gravacao as _do_cancelar_gravacao,
    get_tempo_gravacao as _get_tempo_gravacao,
)
from core.config import is_first_run as _is_first_run, mark_onboarding_done as _mark_onboarding_done, tem_logseq_config as _tem_logseq_config, tem_pro as _tem_pro, ativar_pro as _ativar_pro
from integrations.obsidian import (
    formatar_obsidian as _do_formatar_obsidian,
    salvar_obsidian as _do_salvar_obsidian,
    salvar_obsidian_em as _do_salvar_obsidian_em,
    formatar_texto_direto as _do_formatar_texto_direto,
    escolher_pasta_obsidian as _do_escolher_pasta,
    detectar_vaults as _detectar_vaults,
    selecionar_vault as _selecionar_vault,
)
from integrations.logseq import (
    detectar_logseq_graphs as _detectar_logseq_graphs,
    get_logseq_graph as _get_logseq_graph,
    set_logseq_graph as _set_logseq_graph,
    salvar_logseq as _do_salvar_logseq,
    salvar_logseq_em as _do_salvar_logseq_em,
    escolher_pasta_logseq as _do_escolher_pasta_logseq,
)
from integrations.notion import (
    tem_notion_config as _tem_notion_config,
    salvar_notion_config as _do_salvar_notion_config,
    salvar_notion as _do_salvar_notion,
)
from integrations.roam import tem_roam_config as _tem_roam_config
from core.resumo import gerar_resumo_semanal as _gerar_resumo_semanal

GRAVACAO_DIR = os.path.join(os.path.expanduser("~"), "Desktop")

eel.init("web")


# --- Callback factories ---

def _transcriber_cbs():
    return {
        "on_status": lambda m: eel.on_status(m),
        "on_segmento": lambda t: eel.on_segmento(t),
        "on_progresso": lambda n: eel.on_progresso(n),
        "on_concluido": lambda nome, idioma="": eel.on_concluido(nome, idioma),
        "on_cancelado": lambda: eel.on_cancelado(),
        "on_erro": lambda m: eel.on_erro(m),
    }


def _recorder_cbs():
    return {
        "on_nivel_audio": lambda n: eel.on_nivel_audio(n),
        "on_gravacao_concluida": lambda p, n: eel.on_gravacao_concluida(p, n),
        "on_erro": lambda m: eel.on_erro(m),
    }


def _obsidian_cbs():
    return {
        "on_status_obsidian": lambda m: eel.on_status_obsidian(m),
        "on_obsidian_formatado": lambda md: eel.on_obsidian_formatado(md),
        "on_salvar_obs_concluido": lambda p, n: eel.on_salvar_obs_concluido(p, n),
        "on_texto_direto_concluido": lambda md, path, nome: eel.on_texto_direto_concluido(md, path, nome),
        "on_erro": lambda m: eel.on_erro(m),
    }


def _logseq_cbs():
    return {
        "on_status": lambda m: eel.on_status_obsidian(m),
        "on_formatado": lambda md: eel.on_obsidian_formatado(md),
        "on_salvar_concluido": lambda p, n: eel.on_salvar_obs_concluido(p, n),
        "on_texto_direto_concluido": lambda md, path, nome: eel.on_texto_direto_concluido(md, path, nome),
        "on_erro": lambda m: eel.on_erro(m),
    }


def _notion_cbs():
    return {
        "on_status": lambda m: eel.on_status_obsidian(m),
        "on_formatado": lambda md: eel.on_obsidian_formatado(md),
        "on_salvar_concluido": lambda url, n: eel.on_salvar_notion_concluido(url, n),
        "on_texto_direto_concluido": lambda md, path, nome: eel.on_texto_direto_concluido(md, path, nome),
        "on_erro": lambda m: eel.on_erro(m),
    }


def _resumo_cbs():
    return {
        "on_status": lambda m: eel.on_status_obsidian(m),
        "on_texto_direto_concluido": lambda md, path, nome: eel.on_texto_direto_concluido(md, path, nome),
        "on_erro": lambda m: eel.on_erro(m),
    }


# --- Helpers that stay in app.py (UI-bound) ---

def _copiar_para_clipboard(texto):
    try:
        subprocess.run(["powershell", "-Command", "Set-Clipboard -Value $input"],
                       input=texto.encode("utf-8"), check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception:
        try:
            subprocess.run(["clip"], input=texto.encode("utf-16-le"), check=True)
        except Exception:
            pass


# --- Exposed functions ---

@eel.expose
def selecionar_arquivo():
    try:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            parent=root,
            filetypes=[
                ("Audio, Video e Legendas", "*.mp3 *.mp4 *.m4a *.wav *.ogg *.mkv *.srt *.vtt *.ass *.ssa *.sub *.sbv *.txt"),
                ("Audio e Video", "*.mp3 *.mp4 *.m4a *.wav *.ogg *.mkv"),
                ("Legendas", "*.srt *.vtt *.ass *.ssa *.sub *.sbv"),
                ("Texto", "*.txt"),
            ],
        )
        root.destroy()
        if path:
            return {"path": path, "nome": os.path.basename(path)}
    except Exception:
        pass
    return None


@eel.expose
def salvar_groq_key(key):
    return _salvar_groq_key(key)


@eel.expose
def tem_groq_key():
    return _tem_groq_key()


@eel.expose
def ler_arquivo_texto(path):
    try:
        ext = os.path.splitext(path)[1].lower()
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            conteudo = f.read()

        if ext in (".srt", ".vtt", ".sbv"):
            linhas = []
            for linha in conteudo.split("\n"):
                linha = linha.strip()
                if not linha:
                    continue
                if re.match(r"^\d+$", linha):
                    continue
                if re.match(r"^\d{2}:\d{2}", linha):
                    continue
                if re.match(r"^WEBVTT", linha):
                    continue
                if re.match(r"^NOTE", linha):
                    continue
                linha = re.sub(r"<[^>]+>", "", linha)
                if linha:
                    linhas.append(linha)
            return "\n".join(linhas)

        if ext in (".ass", ".ssa"):
            linhas = []
            for linha in conteudo.split("\n"):
                if linha.startswith("Dialogue:"):
                    partes = linha.split(",", 9)
                    if len(partes) >= 10:
                        texto = partes[9].strip()
                        texto = re.sub(r"\{[^}]+\}", "", texto)
                        texto = texto.replace("\\N", " ").replace("\\n", " ")
                        if texto:
                            linhas.append(texto)
            return "\n".join(linhas)

        return conteudo
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"


@eel.expose
def listar_dispositivos():
    return _listar_dispositivos()


@eel.expose
def transcrever(audio_path):
    _do_transcrever(audio_path, _transcriber_cbs())


@eel.expose
def cancelar_transcricao():
    _do_cancelar()


@eel.expose
def copiar_texto(texto):
    _copiar_para_clipboard(texto)


@eel.expose
def salvar_texto(texto, nome_custom=None):
    import threading
    def _run():
        try:
            nome = (nome_custom or get_nome_inteligente() or f"SinapseIA_{datetime.now().strftime('%Y%m%d_%H%M%S')}").strip()
            nome = "".join(c for c in nome if c not in r'\/:*?"<>|').strip() or "SinapseIA"
            path = os.path.join(GRAVACAO_DIR, f"{nome}.txt")
            if os.path.exists(path):
                ts = datetime.now().strftime("_%H%M%S")
                path = os.path.join(GRAVACAO_DIR, f"{nome}{ts}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(texto)
            salvar_historico(nome, path, "txt")
            eel.on_salvar_concluido(path, os.path.basename(path))
        except Exception as e:
            eel.on_erro(f"Erro ao salvar: {e}")
    threading.Thread(target=_run, daemon=True).start()


@eel.expose
def abrir_arquivo(path):
    if path and (path.startswith("https://") or path.startswith("http://")):
        import webbrowser
        webbrowser.open(path)
    elif path and os.path.exists(path):
        os.startfile(path)


@eel.expose
def ler_conteudo_arquivo(path):
    try:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return {"conteudo": f.read(), "nome": os.path.basename(path), "path": path}
    except Exception:
        pass
    return None


@eel.expose
def atualizar_arquivo(path, conteudo):
    try:
        if path and os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(conteudo)
            return True
    except Exception:
        pass
    return False


@eel.expose
def excluir_arquivo(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            return True
    except Exception:
        pass
    return False


@eel.expose
def carregar_historico():
    return _carregar_historico()


@eel.expose
def formatar_obsidian(texto):
    _do_formatar_obsidian(texto, _obsidian_cbs())


@eel.expose
def salvar_obsidian(conteudo, nome_custom=None):
    _do_salvar_obsidian(conteudo, get_nome_inteligente(), nome_custom, _obsidian_cbs())


@eel.expose
def formatar_texto_direto(texto):
    _do_formatar_texto_direto(texto, _obsidian_cbs())


@eel.expose
def escolher_pasta_obsidian():
    return _do_escolher_pasta()


@eel.expose
def salvar_obsidian_em(conteudo, pasta, nome_custom=None):
    _do_salvar_obsidian_em(conteudo, pasta, get_nome_inteligente(), nome_custom, _obsidian_cbs())


@eel.expose
def iniciar_gravacao(device_id=None):
    _do_iniciar_gravacao(device_id, _recorder_cbs())


@eel.expose
def pausar_gravacao():
    return _do_pausar()


@eel.expose
def parar_gravacao():
    _do_parar()


@eel.expose
def cancelar_gravacao():
    _do_cancelar_gravacao()


@eel.expose
def get_tempo_gravacao():
    return _get_tempo_gravacao()


# --- Logseq ---

@eel.expose
def detectar_logseq_graphs():
    return _detectar_logseq_graphs()


@eel.expose
def selecionar_logseq_graph(path):
    if os.path.isdir(path) and os.path.isdir(os.path.join(path, "logseq")):
        _set_logseq_graph(path)
        return True
    return False


@eel.expose
def tem_logseq_config():
    return _tem_logseq_config()


@eel.expose
def salvar_logseq(conteudo, nome_custom=None):
    _do_salvar_logseq(conteudo, get_nome_inteligente(), nome_custom, _logseq_cbs())


@eel.expose
def salvar_logseq_em(conteudo, pasta, nome_custom=None):
    _do_salvar_logseq_em(conteudo, pasta, get_nome_inteligente(), nome_custom, _logseq_cbs())


@eel.expose
def escolher_pasta_logseq():
    return _do_escolher_pasta_logseq()


# --- Notion ---

@eel.expose
def tem_notion_config():
    return _tem_notion_config()


@eel.expose
def salvar_notion_config(token, parent_id):
    _do_salvar_notion_config(token, parent_id)
    return True


@eel.expose
def salvar_notion(conteudo, nome_custom=None):
    _do_salvar_notion(conteudo, get_nome_inteligente(), nome_custom, _notion_cbs())


# --- Roam ---

@eel.expose
def tem_roam_config():
    return _tem_roam_config()


# --- Freemium ---

@eel.expose
def tem_pro():
    return _tem_pro()


@eel.expose
def ativar_pro(chave):
    return _ativar_pro(chave)


# --- Traducao ---

@eel.expose
def traduzir_para(texto, idioma_alvo):
    """Translates transcript text to the target language. Returns translated string or None."""
    resultado = _traduzir_texto(texto, idioma_alvo)
    return resultado if resultado and resultado not in ("__INVALID_KEY__", "__DAILY_LIMIT__") else None


# --- Resumo Semanal ---

@eel.expose
def gerar_resumo_semanal():
    _gerar_resumo_semanal(_resumo_cbs())


# --- Vault & Onboarding ---

@eel.expose
def detectar_vaults():
    return _detectar_vaults()


@eel.expose
def selecionar_vault(path):
    return _selecionar_vault(path)


@eel.expose
def is_first_run():
    return _is_first_run()


@eel.expose
def mark_onboarding_done():
    _mark_onboarding_done()


# --- Start ---

if __name__ == "__main__":
    eel.start("index.html", size=(750, 780), mode="chrome", port=0)
