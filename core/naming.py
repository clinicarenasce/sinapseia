import os
from datetime import datetime
from core.ai import groq_gerar
from core.storage import carregar_historico


def gerar_nome_inteligente(texto):
    historico = carregar_historico()
    hist_nomes = [h["nome"] for h in historico[:5]] if historico else []
    hist_context = ""
    if hist_nomes:
        hist_context = f"""

Nomes dos ultimos arquivos salvos (do mais recente ao mais antigo):
{chr(10).join(f'- {n}' for n in hist_nomes)}

IMPORTANTE: Se os nomes acima indicam uma sequencia (ex: "Aula 1", "Aula 2"), continue com o proximo numero."""

    prompt = f"""Tarefa: gerar UM nome de arquivo curto baseado no conteudo.

Exemplos de bons nomes:
- Marketing Digital - Modulo 2 - Aula 5 - Funis de Venda
- Aula 3 - Introducao ao Python
- Direito Constitucional - Aula 12 - Direitos Fundamentais
- Reuniao de Planejamento Q2
- Palestra sobre Inteligencia Artificial

Regras:
1. Responda com UMA UNICA LINHA contendo apenas o nome
2. Sem aspas, sem extensao de arquivo, sem explicacao
3. Se o conteudo mencionar curso, modulo ou aula, inclua no nome
4. Maximo 10 palavras
5. Use hifen (-) para separar secoes{hist_context}

Conteudo:
{texto[:2000]}

Nome:"""

    nome = groq_gerar(prompt, max_tokens=40)
    if nome and nome not in ("__INVALID_KEY__", "__DAILY_LIMIT__"):
        nome = nome.split("\n")[0].strip()
        nome = nome.strip('"').strip("'").strip("`").strip("*")
        for prefixo in ["Nome:", "nome:", "Nome do arquivo:", "Arquivo:", "- "]:
            if nome.startswith(prefixo):
                nome = nome[len(prefixo):].strip()
        nome = "".join(c for c in nome if c not in r'\/:*?"<>|').strip()
        for ext in [".txt", ".md", ".wav", ".mp3"]:
            if nome.lower().endswith(ext):
                nome = nome[:-len(ext)].strip()
        if nome and len(nome) > 3:
            return nome[:80]
    return f"SinapseIA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def renomear_arquivo(path_antigo, nome_novo):
    if not path_antigo or not os.path.exists(path_antigo):
        return path_antigo
    pasta = os.path.dirname(path_antigo)
    ext = os.path.splitext(path_antigo)[1]
    novo_path = os.path.join(pasta, f"{nome_novo}{ext}")
    if os.path.exists(novo_path):
        ts = datetime.now().strftime("_%H%M%S")
        novo_path = os.path.join(pasta, f"{nome_novo}{ts}{ext}")
    try:
        os.rename(path_antigo, novo_path)
        return novo_path
    except Exception:
        return path_antigo
