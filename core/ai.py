import json
import time
import urllib.request
import urllib.error
from core.config import carregar_config

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MODEL_FAST = "llama-3.1-8b-instant"

PROMPT_OBSIDIAN = """Voce e um assistente que formata transcricoes e textos para notas no Obsidian.

Primeiro, identifique o tipo de conteudo:
- AULA: conteudo educacional, curso, modulo
- REUNIAO: discussao, decisoes, action items
- PALESTRA: apresentacao, talk, keynote
- PODCAST: conversa, entrevista
- TEXTO: artigo, anotacao, conteudo geral

Estrutura da nota:
1. YAML frontmatter:
---
date: {data de hoje no formato YYYY-MM-DD}
type: {tipo identificado acima em minusculo}
tags: [tag1, tag2, tag3]
---

2. Titulo: # Titulo claro baseado no conteudo

3. Secao ## Resumo com 2-3 frases

4. Conteudo estruturado:
   - Use ## e ### para headers
   - Use bullet points para conceitos
   - Destaque termos com **negrito**
   - Crie [[wikilinks]] para conceitos importantes que merecem nota propria
   - Para REUNIAO: adicione secao "## Decisoes" e "## Proximos passos"
   - Para AULA: adicione secao "## Exemplos" se houver

5. Secao ## Conceitos-chave no final com lista de [[wikilinks]]

Regras importantes:
- Mantenha fidelidade ao conteudo original, NAO invente informacoes
- [[wikilinks]] devem ser para conceitos reais mencionados, nao genericos
- Tags devem ser especificas: #marketing-digital em vez de #marketing
- Se o conteudo incluir uma lista de [Tags existentes no vault: ...], PRIORIZE reutilizar essas tags antes de criar novas
- Responda APENAS com o markdown formatado, sem explicacoes

Conteudo:
"""

PROMPT_RESUMO_SEMANAL = """Voce e um assistente que cria revisoes semanais para o segundo cerebro no Obsidian.

IDIOMA: Use o idioma predominante nas notas recebidas.

Receberá notas recentes com seus titulos e conteudos. Crie uma nota de revisao semanal com:

1. YAML frontmatter:
---
date: {data de hoje no formato YYYY-MM-DD}
type: revisao-semanal
tags: [revisao-semanal]
---

2. Titulo: # Revisao Semanal — Semana {numero}

3. ## Resumo
2-3 frases sobre os principais temas da semana

4. ## Notas da Semana
Lista com [[wikilinks]] para cada nota e uma frase descritiva do que ela cobre

5. ## Conexoes
Conexoes e padroes tematicos entre as notas

6. ## Insights
Principais aprendizados e ideias emergentes desta semana

Regras:
- Use [[Nome da Nota]] para referenciar cada nota pelo titulo exato
- Identifique conexoes reais entre os conteudos
- NAO invente informacoes que nao estejam nas notas
- Responda APENAS com o markdown, sem explicacoes

Notas recentes:
"""


IDIOMAS_NOMES = {
    "pt": "Português", "en": "English", "es": "Español",
    "zh": "Mandarim (Chinês)", "hi": "Hindi", "ar": "Árabe", "fr": "Français",
    "de": "Deutsch", "ja": "Japonês", "ko": "Coreano", "it": "Italiano", "ru": "Russo",
}


def traduzir_texto(texto, idioma_alvo):
    """Translates text to the target language using Groq. Returns translated string or None."""
    nome = IDIOMAS_NOMES.get(idioma_alvo, idioma_alvo)
    system = (
        f"You are a professional translator. Translate the following text into {nome}. "
        "Preserve the original meaning, tone, and any formatting. "
        "Reply ONLY with the translated text, no explanations."
    )
    return groq_gerar(texto, max_tokens=4096, system=system)


def groq_gerar(prompt, max_tokens=100, system=None, _tentativa=0, _modelo=None):
    if _modelo is None:
        _modelo = GROQ_MODEL
    config = carregar_config()
    api_key = config.get("groq_api_key", "")
    if not api_key:
        return None
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = json.dumps({
        "model": _modelo, "messages": messages,
        "temperature": 0.2, "max_tokens": max_tokens,
    }).encode("utf-8")
    req = urllib.request.Request(GROQ_URL, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "SinapseIA/1.0",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resultado = json.loads(resp.read().decode("utf-8"))
        content = resultado["choices"][0]["message"]["content"].strip()
        if not content and _tentativa < 1:
            time.sleep(2)
            return groq_gerar(prompt, max_tokens, system, _tentativa + 1, _modelo)
        return content if content else None
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return "__INVALID_KEY__"
        if e.code == 429:
            try:
                err_body = json.loads(e.read().decode("utf-8", "replace"))
                err_msg = err_body.get("error", {}).get("message", "")
            except Exception:
                err_msg = ""
            # Limite diario de tokens: tenta modelo menor antes de desistir
            if "tokens per day" in err_msg or "TPD" in err_msg:
                if _modelo == GROQ_MODEL:
                    return groq_gerar(prompt, max_tokens, system, 0, GROQ_MODEL_FAST)
                return "__DAILY_LIMIT__"
            # Rate limit por minuto: retry com backoff
            if _tentativa < 2:
                time.sleep(2 ** _tentativa * 2)
                return groq_gerar(prompt, max_tokens, system, _tentativa + 1, _modelo)
            raise
        if e.code in (500, 502, 503) and _tentativa < 2:
            time.sleep(2 ** _tentativa * 2)
            return groq_gerar(prompt, max_tokens, system, _tentativa + 1, _modelo)
        raise
    except Exception:
        if _tentativa < 2:
            time.sleep(2 ** _tentativa * 2)
            return groq_gerar(prompt, max_tokens, system, _tentativa + 1, _modelo)
        raise
