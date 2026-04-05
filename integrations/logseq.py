import os
import threading
from datetime import datetime
from tkinter import filedialog, Tk
from core.config import carregar_config, salvar_config
from core.ai import groq_gerar, PROMPT_OBSIDIAN
from core.naming import gerar_nome_inteligente
from core.storage import salvar_historico
from core.wikilinks import ler_tags_vault, criar_stubs_wikilinks
from integrations.base import NoteApp


def detectar_logseq_graphs():
    """Scans common directories for Logseq graphs (folders with logseq/ subfolder)."""
    home = os.path.expanduser("~")
    candidatos = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Documents"),
        os.path.join(home, "OneDrive"),
        os.path.join(home, "Documentos"),
        home,
    ]
    for letra in "DEF":
        drive = f"{letra}:\\"
        if os.path.exists(drive):
            candidatos.append(drive)

    graphs = []
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
                if os.path.isdir(pasta) and os.path.isdir(os.path.join(pasta, "logseq")):
                    graphs.append({"name": item, "path": pasta})
        except PermissionError:
            continue
    return graphs


def get_logseq_graph():
    return carregar_config().get("logseq_graph", "")


def set_logseq_graph(path):
    salvar_config("logseq_graph", path)


def _get_pages_dir(graph_path=None):
    """Returns the pages/ dir for the active (or provided) Logseq graph."""
    graph = graph_path or get_logseq_graph()
    if graph and os.path.isdir(graph):
        pages = os.path.join(graph, "pages")
        os.makedirs(pages, exist_ok=True)
        return pages
    return None


def _nome_seguro(nome):
    nome = "".join(c for c in nome if c not in r'\/:*?"<>|').strip() or "SinapseIA"
    return nome


def _texto_com_tags(texto, graph_path):
    pages = _get_pages_dir(graph_path) or graph_path
    tags = ler_tags_vault(pages)
    if tags:
        return texto + f"\n\n[Tags existentes no graph: {', '.join(tags)}]"
    return texto


def formatar_logseq(texto, callbacks):
    """Formats text for Logseq (same Obsidian markdown prompt)."""
    def _run():
        try:
            config = carregar_config()
            if not config.get("groq_api_key"):
                callbacks["on_erro"]("Configure sua API key do Groq primeiro.")
                return
            callbacks["on_status"]("Formatando com IA...")
            texto_enriquecido = _texto_com_tags(texto, get_logseq_graph())
            resultado = groq_gerar(texto_enriquecido, max_tokens=4096, system=PROMPT_OBSIDIAN)
            if resultado == "__INVALID_KEY__":
                callbacks["on_erro"]("API key do Groq invalida.")
                return
            if resultado == "__DAILY_LIMIT__":
                callbacks["on_erro"]("Limite diario de tokens do Groq atingido. O limite reseta em algumas horas.")
                return
            if resultado and resultado.strip():
                callbacks["on_formatado"](resultado.strip())
            else:
                callbacks["on_erro"]("O modelo nao retornou texto. Tente novamente.")
        except Exception as e:
            callbacks["on_erro"](f"Erro: {e}")
    threading.Thread(target=_run, daemon=True).start()


def salvar_logseq(conteudo, nome_inteligente, nome_custom, callbacks):
    """Saves .md to the active Logseq graph pages/ directory."""
    def _run():
        try:
            pages = _get_pages_dir()
            if not pages:
                callbacks["on_erro"]("Nenhum graph Logseq configurado. Selecione um graph primeiro.")
                return
            nome = _nome_seguro((nome_custom or nome_inteligente or
                                 f"SinapseIA_{datetime.now().strftime('%Y%m%d_%H%M%S')}").strip())
            path = os.path.join(pages, f"{nome}.md")
            if os.path.exists(path):
                ts = datetime.now().strftime("_%H%M%S")
                path = os.path.join(pages, f"{nome}{ts}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(conteudo)
            criar_stubs_wikilinks(conteudo, pages)
            salvar_historico(nome, path, "logseq")
            callbacks["on_salvar_concluido"](path, os.path.basename(path))
        except Exception as e:
            callbacks["on_erro"](f"Erro ao salvar: {e}")
    threading.Thread(target=_run, daemon=True).start()


def salvar_logseq_em(conteudo, pasta, nome_inteligente, nome_custom, callbacks):
    """Saves .md to a specific folder inside a Logseq graph."""
    def _run():
        try:
            nome = _nome_seguro((nome_custom or nome_inteligente or
                                 f"SinapseIA_{datetime.now().strftime('%Y%m%d_%H%M%S')}").strip())
            os.makedirs(pasta, exist_ok=True)
            path = os.path.join(pasta, f"{nome}.md")
            if os.path.exists(path):
                ts = datetime.now().strftime("_%H%M%S")
                path = os.path.join(pasta, f"{nome}{ts}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(conteudo)
            criar_stubs_wikilinks(conteudo, pasta)
            salvar_historico(nome, path, "logseq")
            callbacks["on_salvar_concluido"](path, os.path.basename(path))
        except Exception as e:
            callbacks["on_erro"](f"Erro ao salvar: {e}")
    threading.Thread(target=_run, daemon=True).start()


def formatar_texto_direto_logseq(texto, callbacks):
    """Formats free text and delivers result for Logseq save."""
    def _run():
        try:
            config = carregar_config()
            if not config.get("groq_api_key"):
                callbacks["on_erro"]("Configure sua API key do Groq primeiro.")
                return
            callbacks["on_status"]("Gerando nome...")
            nome = gerar_nome_inteligente(texto)
            callbacks["on_status"]("Formatando com IA...")
            resultado = groq_gerar(texto, max_tokens=4096, system=PROMPT_OBSIDIAN)
            if resultado == "__INVALID_KEY__":
                callbacks["on_erro"]("API key do Groq invalida.")
                return
            if resultado == "__DAILY_LIMIT__":
                callbacks["on_erro"]("Limite diario de tokens do Groq atingido. O limite reseta em algumas horas.")
                return
            if not resultado or not resultado.strip():
                callbacks["on_erro"]("O modelo nao retornou texto.")
                return
            callbacks["on_texto_direto_concluido"](resultado.strip(), "", nome)
        except Exception as e:
            callbacks["on_erro"](f"Erro: {e}")
    threading.Thread(target=_run, daemon=True).start()


def escolher_pasta_logseq():
    """Opens folder picker starting from active Logseq graph."""
    try:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        initial = get_logseq_graph() or os.path.expanduser("~")
        pasta = filedialog.askdirectory(
            parent=root,
            initialdir=initial,
            title="Escolha a pasta dentro do Logseq",
        )
        root.destroy()
        if pasta:
            return pasta
    except Exception:
        pass
    return None
