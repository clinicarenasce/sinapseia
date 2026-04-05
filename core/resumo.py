import os
import threading
from datetime import datetime
from core.config import carregar_config
from core.ai import groq_gerar, PROMPT_RESUMO_SEMANAL
from core.storage import carregar_historico


def gerar_resumo_semanal(callbacks):
    """Generates a weekly review note from recent history entries.

    Uses up to the 8 most recent notes. Delivers via callbacks:
    on_status(msg), on_texto_direto_concluido(md, '', nome), on_erro(msg).
    """
    def _run():
        try:
            config = carregar_config()
            if not config.get("groq_api_key"):
                callbacks["on_erro"]("Configure sua API key do Groq primeiro.")
                return

            callbacks["on_status"]("Carregando notas recentes...")
            historico = carregar_historico()

            if not historico:
                callbacks["on_erro"]("Nenhuma nota no historico ainda.")
                return

            # Load note contents — use up to 8 most recent notes
            partes = []
            for item in historico[:8]:
                path = item.get("path", "")
                nome = item.get("nome", "Sem titulo")
                if not path:
                    continue
                # Notion entries have a URL, not a local path
                if path.startswith("http"):
                    partes.append(f"### {nome}\n(nota no Notion — sem conteudo local)")
                    continue
                if os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            conteudo = f.read(2500)
                        partes.append(f"### {nome}\n{conteudo}")
                    except Exception:
                        pass

            if not partes:
                callbacks["on_erro"]("Nao foi possivel ler as notas recentes.")
                return

            semana = datetime.now().isocalendar()[1]
            ano = datetime.now().year
            contexto = f"Semana {semana} de {ano}\n\n" + "\n\n---\n\n".join(partes)

            callbacks["on_status"]("Gerando revisao com IA...")
            resultado = groq_gerar(contexto, max_tokens=4096, system=PROMPT_RESUMO_SEMANAL)
            if resultado == "__INVALID_KEY__":
                callbacks["on_erro"]("API key do Groq invalida.")
                return
            if resultado == "__DAILY_LIMIT__":
                callbacks["on_erro"]("Limite diario de tokens do Groq atingido. O limite reseta em algumas horas.")
                return
            if not resultado or not resultado.strip():
                callbacks["on_erro"]("O modelo nao retornou texto.")
                return

            nome_nota = f"Revisao Semanal - Semana {semana} {ano}"
            callbacks["on_texto_direto_concluido"](resultado.strip(), "", nome_nota)
        except Exception as e:
            callbacks["on_erro"](f"Erro ao gerar resumo: {e}")
    threading.Thread(target=_run, daemon=True).start()
