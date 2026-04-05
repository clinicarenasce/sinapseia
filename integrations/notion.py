import json
import os
import re
import time
import threading
import urllib.request
import urllib.error
from datetime import datetime
from core.config import carregar_config, salvar_config, CONFIG_PATH
from core.ai import groq_gerar, PROMPT_OBSIDIAN
from core.naming import gerar_nome_inteligente
from core.storage import salvar_historico

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


# --- Config helpers ---

def get_notion_token():
    return carregar_config().get("notion_token", "")


def get_notion_parent_id():
    return carregar_config().get("notion_parent_id", "")


def salvar_notion_config(token, parent_id):
    config = carregar_config()
    config["notion_token"] = token.strip()
    config["notion_parent_id"] = parent_id.strip()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False)


def tem_notion_config():
    config = carregar_config()
    return bool(config.get("notion_token") and config.get("notion_parent_id"))


# --- Notion API helpers ---

def _notion_headers(token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
    }


def _notion_post(endpoint, data, token, _tentativa=0):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{NOTION_API}/{endpoint}",
        data=body,
        headers=_notion_headers(token),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (500, 502, 503) and _tentativa < 2:
            time.sleep(2 ** _tentativa * 2)
            return _notion_post(endpoint, data, token, _tentativa + 1)
        raise
    except Exception:
        if _tentativa < 2:
            time.sleep(2 ** _tentativa * 2)
            return _notion_post(endpoint, data, token, _tentativa + 1)
        raise


def _notion_append(page_id, blocks, token, _tentativa=0):
    """Appends blocks to an existing Notion page (PATCH /blocks/{id}/children)."""
    body = json.dumps({"children": blocks}).encode("utf-8")
    req = urllib.request.Request(
        f"{NOTION_API}/blocks/{page_id}/children",
        data=body,
        headers=_notion_headers(token),
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (500, 502, 503) and _tentativa < 2:
            time.sleep(2 ** _tentativa * 2)
            return _notion_append(page_id, blocks, token, _tentativa + 1)
        raise
    except Exception:
        if _tentativa < 2:
            time.sleep(2 ** _tentativa * 2)
            return _notion_append(page_id, blocks, token, _tentativa + 1)
        raise


def _rt(text):
    """Create a single rich_text element, respecting Notion's 2000-char limit."""
    return [{"type": "text", "text": {"content": text[:2000]}}]


def _md_to_blocks(texto):
    """Convert markdown text to Notion API block objects (sem limite de 99 — paginação feita no caller)."""
    blocks = []
    in_frontmatter = False
    frontmatter_done = False
    frontmatter_line_count = 0
    in_code_block = False
    code_lang = "plain text"
    code_lines = []

    linhas = texto.split("\n")

    for linha in linhas:
        s = linha.strip()

        # --- Frontmatter robusto ---
        if not frontmatter_done:
            if s == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    frontmatter_line_count = 0
                    continue
                else:
                    # fechamento normal
                    in_frontmatter = False
                    frontmatter_done = True
                    continue
            if in_frontmatter:
                frontmatter_line_count += 1
                if frontmatter_line_count > 20:
                    # frontmatter sem fechamento — desistir e tratar como corpo
                    in_frontmatter = False
                    frontmatter_done = True
                    # não pular esta linha — cai no parsing abaixo
                else:
                    continue

        # --- Code blocks (triple backticks) ---
        if s.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_lang = s[3:].strip() or "plain text"
                code_lines = []
            else:
                in_code_block = False
                code_content = "\n".join(code_lines)
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": _rt(code_content[:2000]),
                        "language": code_lang,
                    },
                })
            continue

        if in_code_block:
            code_lines.append(linha)  # preservar indentação original
            continue

        if not s:
            continue

        if s.startswith("### "):
            blocks.append({"object": "block", "type": "heading_3",
                           "heading_3": {"rich_text": _rt(s[4:])}})
        elif s.startswith("## "):
            blocks.append({"object": "block", "type": "heading_2",
                           "heading_2": {"rich_text": _rt(s[3:])}})
        elif s.startswith("# "):
            blocks.append({"object": "block", "type": "heading_1",
                           "heading_1": {"rich_text": _rt(s[2:])}})
        elif s.startswith("- ") or s.startswith("* "):
            blocks.append({"object": "block", "type": "bulleted_list_item",
                           "bulleted_list_item": {"rich_text": _rt(s[2:])}})
        elif re.match(r"^\d+\.\s", s):
            text = re.sub(r"^\d+\.\s", "", s)
            blocks.append({"object": "block", "type": "numbered_list_item",
                           "numbered_list_item": {"rich_text": _rt(text)}})
        elif s.startswith("> "):
            blocks.append({"object": "block", "type": "quote",
                           "quote": {"rich_text": _rt(s[2:])}})
        else:
            blocks.append({"object": "block", "type": "paragraph",
                           "paragraph": {"rich_text": _rt(s)}})

    # Fechar code block não terminado
    if in_code_block and code_lines:
        blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": _rt("\n".join(code_lines)[:2000]),
                "language": code_lang,
            },
        })

    return blocks


def _criar_pagina(nome, blocks, token, parent_id):
    """Creates a Notion page with up to 99 initial blocks. Returns (url, page_id)."""
    data = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": nome[:2000]}}]
            }
        },
        "children": blocks[:99],
    }
    resultado = _notion_post("pages", data, token)
    return resultado.get("url", ""), resultado.get("id", "")


# --- Public integration functions ---

def formatar_notion(texto, callbacks):
    """Formats text for Notion (same AI prompt as Obsidian — markdown)."""
    def _run():
        try:
            config = carregar_config()
            if not config.get("groq_api_key"):
                callbacks["on_erro"]("Configure sua API key do Groq primeiro.")
                return
            callbacks["on_status"]("Formatando com IA...")
            resultado = groq_gerar(texto, max_tokens=4096, system=PROMPT_OBSIDIAN)
            if resultado == "__INVALID_KEY__":
                callbacks["on_erro"]("API key do Groq invalida.")
                return
            if resultado == "__DAILY_LIMIT__":
                callbacks["on_erro"]("Limite diario de tokens do Groq atingido. O limite reseta em algumas horas.")
                return
            if resultado and resultado.strip():
                callbacks["on_formatado"](resultado.strip())
            else:
                callbacks["on_erro"]("O modelo nao retornou texto.")
        except Exception as e:
            callbacks["on_erro"](f"Erro: {e}")
    threading.Thread(target=_run, daemon=True).start()


def salvar_notion(conteudo, nome_inteligente, nome_custom, callbacks):
    """Creates a Notion page from markdown content, with full pagination for long notes."""
    def _run():
        try:
            token = get_notion_token()
            parent_id = get_notion_parent_id()
            if not token or not parent_id:
                callbacks["on_erro"]("Notion nao configurado. Insira o token e o ID da pagina pai.")
                return

            nome = (nome_custom or nome_inteligente or
                    f"SinapseIA {datetime.now().strftime('%Y-%m-%d %H:%M')}").strip()
            nome = "".join(c for c in nome if c not in r'*?"<>|').strip() or "SinapseIA"

            callbacks["on_status"]("Criando pagina no Notion...")
            blocks = _md_to_blocks(conteudo)

            # Criar página com os primeiros 99 blocos
            url, page_id = _criar_pagina(nome, blocks, token, parent_id)
            if not url:
                url = f"https://notion.so/{page_id.replace('-', '')}" if page_id else ""

            # Enviar blocos restantes em batches de 99
            if page_id and len(blocks) > 99:
                restantes = blocks[99:]
                batch_num = 1
                while restantes:
                    batch = restantes[:99]
                    restantes = restantes[99:]
                    callbacks["on_status"](f"Enviando conteudo adicional ({batch_num})...")
                    _notion_append(page_id, batch, token)
                    batch_num += 1

            salvar_historico(nome, url, "notion")
            callbacks["on_salvar_concluido"](url, nome)
        except urllib.error.HTTPError as e:
            msg = {
                401: "Token Notion invalido ou sem permissao na pagina pai.",
                404: "Pagina pai nao encontrada. Verifique o ID e se a integracao foi adicionada.",
                400: "Requisicao invalida. Verifique o ID da pagina pai.",
            }.get(e.code, f"Erro HTTP {e.code} na API Notion.")
            callbacks["on_erro"](msg)
        except Exception as e:
            callbacks["on_erro"](f"Erro ao salvar no Notion: {e}")
    threading.Thread(target=_run, daemon=True).start()


def formatar_texto_direto_notion(texto, callbacks):
    """Formats free text and delivers result ready for Notion save."""
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
