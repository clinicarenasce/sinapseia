import os
import time
import threading
import numpy as np
import soundcard as sc
import soundfile as sf
from datetime import datetime

GRAVACAO_DIR = os.path.join(os.path.expanduser("~"), "Desktop")

_gravando = False
_pausado = False
_gravacao_thread = None
_gravacao_inicio = 0.0


def _gerar_nome_gravacao():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(GRAVACAO_DIR, f"sinapseia_{ts}.wav")


def listar_dispositivos():
    dispositivos = []
    for s in sc.all_speakers():
        dispositivos.append({"id": s.id, "nome": s.name})
    return dispositivos


def get_tempo_gravacao():
    """Retorna segundos desde o inicio da gravacao (0 se nao estiver gravando)."""
    if not _gravando or _gravacao_inicio == 0.0:
        return 0
    return int(time.time() - _gravacao_inicio)


def iniciar_gravacao(device_id, callbacks):
    """Inicia gravacao loopback. callbacks: on_nivel_audio, on_gravacao_concluida, on_erro"""
    global _gravando, _pausado, _gravacao_thread, _gravacao_inicio
    if _gravando:
        return
    _gravando = True
    _pausado = False
    _gravacao_inicio = time.time()

    def _gravar():
        global _gravando, _pausado, _gravacao_inicio
        try:
            samplerate = 16000
            frames = []
            if device_id:
                speaker = next((s for s in sc.all_speakers() if s.id == device_id), None)
            else:
                speaker = sc.default_speaker()
            if not speaker:
                callbacks["on_erro"]("Dispositivo de audio nao encontrado.")
                _gravando = False
                return
            device = sc.get_microphone(speaker.id, include_loopback=True)
            with device.recorder(samplerate=samplerate, channels=1) as rec:
                while _gravando:
                    if _pausado:
                        time.sleep(0.1)
                        callbacks["on_nivel_audio"](0.0)
                        continue
                    chunk = rec.record(numframes=samplerate // 4)
                    frames.append(chunk)
                    rms = float(np.sqrt(np.mean(chunk ** 2)))
                    nivel = min(1.0, rms * 10)
                    callbacks["on_nivel_audio"](nivel)
            if not frames:
                callbacks["on_erro"]("Nenhum audio foi capturado.")
                return
            audio = np.concatenate(frames, axis=0)
            wav_path = _gerar_nome_gravacao()
            sf.write(wav_path, audio, samplerate)
            callbacks["on_gravacao_concluida"](wav_path, os.path.basename(wav_path))
        except Exception as e:
            _gravando = False
            callbacks["on_erro"](f"Erro na gravacao: {e}")

    _gravacao_thread = threading.Thread(target=_gravar, daemon=True)
    _gravacao_thread.start()


def pausar_gravacao():
    global _pausado
    _pausado = not _pausado
    return _pausado


def parar_gravacao():
    global _gravando
    _gravando = False


def cancelar_gravacao():
    global _gravando
    _gravando = False
