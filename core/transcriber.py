import os
import threading
from faster_whisper import WhisperModel
from core.naming import gerar_nome_inteligente, renomear_arquivo
from core.platform_utils import play_beep

_modelo_whisper = None
_cancelar_transcricao = False
_nome_inteligente = ""
_audio_path_atual = ""
_idioma_detectado = ""


def get_nome_inteligente():
    return _nome_inteligente


def get_audio_path_atual():
    return _audio_path_atual


def get_idioma_detectado():
    return _idioma_detectado


def _get_whisper(on_status=None):
    global _modelo_whisper
    if _modelo_whisper is None:
        if on_status:
            on_status("Carregando modelo (primeira vez pode levar alguns minutos)...")
        _modelo_whisper = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    return _modelo_whisper


def transcrever(audio_path, callbacks):
    """Transcreve audio. callbacks: on_status, on_segmento, on_progresso, on_concluido, on_cancelado, on_erro"""
    global _cancelar_transcricao, _nome_inteligente, _audio_path_atual, _idioma_detectado
    _cancelar_transcricao = False
    _nome_inteligente = ""
    _audio_path_atual = audio_path
    _idioma_detectado = ""

    def _run():
        global _cancelar_transcricao, _nome_inteligente, _audio_path_atual, _idioma_detectado
        try:
            if not os.path.exists(audio_path):
                callbacks["on_erro"]("Arquivo nao encontrado.")
                return

            modelo = _get_whisper(callbacks.get("on_status"))
            callbacks["on_status"]("Transcrevendo...")
            segments, info = modelo.transcribe(audio_path)
            linhas = []
            total_seg = 0
            for seg in segments:
                if _cancelar_transcricao:
                    callbacks["on_cancelado"]()
                    return
                linha = seg.text.strip()
                if linha:
                    linhas.append(linha)
                    total_seg += 1
                    callbacks["on_segmento"](linha)
                    callbacks["on_progresso"](total_seg)

            if not linhas:
                callbacks["on_erro"]("Nenhum texto foi detectado no audio.")
                return

            _idioma_detectado = info.language or ""
            callbacks["on_status"]("Gerando nome inteligente...")
            texto_completo = "\n".join(linhas)
            _nome_inteligente = gerar_nome_inteligente(texto_completo)

            novo_audio = renomear_arquivo(audio_path, _nome_inteligente)
            _audio_path_atual = novo_audio

            play_beep()
            callbacks["on_concluido"](_nome_inteligente, _idioma_detectado)
        except Exception as e:
            callbacks["on_erro"](str(e))

    threading.Thread(target=_run, daemon=True).start()


def cancelar_transcricao():
    global _cancelar_transcricao
    _cancelar_transcricao = True
