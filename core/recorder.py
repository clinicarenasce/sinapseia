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
    vistos = set()
    dispositivos = []
    for m in sc.all_microphones(include_loopback=True):
        if m.name not in vistos:
            vistos.add(m.name)
            dispositivos.append({"id": m.id, "nome": m.name})
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
            # device_id chega como string do JS; IDs do soundcard sao int ou str
            def _match(s):
                try:
                    return s.id == device_id or str(s.id) == str(device_id) or int(s.id) == int(device_id)
                except Exception:
                    return False

            if device_id:
                # Tenta encontrar como microfone primeiro (BlackHole aparece como mic no Mac)
                mic = next((m for m in sc.all_microphones(include_loopback=True) if _match(m)), None)
                if mic:
                    device = mic
                else:
                    speaker = next((s for s in sc.all_speakers() if _match(s)), None)
                    if not speaker:
                        callbacks["on_erro"]("Dispositivo de audio nao encontrado.")
                        _gravando = False
                        return
                    device = sc.get_microphone(speaker.id, include_loopback=True)
            else:
                device = sc.default_microphone()
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
    global _gravando, _gravacao_inicio
    _gravando = False
    _gravacao_inicio = 0.0


def cancelar_gravacao():
    global _gravando, _gravacao_inicio
    _gravando = False
    _gravacao_inicio = 0.0
