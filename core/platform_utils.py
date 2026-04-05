"""Utilitários cross-platform: som, clipboard, abertura de arquivo."""
import os
import platform
import subprocess

_SYS = platform.system()  # "Windows", "Darwin", "Linux"


def play_beep():
    """Toca um som de notificação no sistema operacional atual."""
    try:
        if _SYS == "Windows":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif _SYS == "Darwin":
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"],
                           check=False, capture_output=True)
        else:
            subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
                           check=False, capture_output=True)
    except Exception:
        pass


def copiar_para_clipboard(texto):
    """Copia texto para a área de transferência."""
    try:
        if _SYS == "Windows":
            subprocess.run(
                ["powershell", "-Command", "Set-Clipboard -Value $input"],
                input=texto.encode("utf-8"),
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        elif _SYS == "Darwin":
            proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            proc.communicate(input=texto.encode("utf-8"))
        else:
            subprocess.run(["xclip", "-selection", "clipboard"],
                           input=texto.encode("utf-8"), check=True)
    except Exception:
        try:
            if _SYS == "Windows":
                subprocess.run(["clip"], input=texto.encode("utf-16-le"), check=True)
        except Exception:
            pass


def abrir_arquivo(path):
    """Abre um arquivo ou URL no aplicativo padrão do sistema."""
    if not path:
        return
    if path.startswith("https://") or path.startswith("http://"):
        import webbrowser
        webbrowser.open(path)
        return
    if not os.path.exists(path):
        return
    if _SYS == "Windows":
        os.startfile(path)
    elif _SYS == "Darwin":
        subprocess.run(["open", path], check=False)
    else:
        subprocess.run(["xdg-open", path], check=False)


def blackhole_instalado():
    """Verifica se o BlackHole está instalado como dispositivo de áudio no macOS."""
    if _SYS != "Darwin":
        return True
    try:
        import soundcard as sc
        devices = sc.all_microphones(include_loopback=True)
        return any("blackhole" in d.name.lower() for d in devices)
    except Exception:
        return False


def instalar_blackhole(on_status=None):
    """Baixa o .pkg mais recente do BlackHole 2ch via GitHub API e abre o instalador nativo."""
    import urllib.request
    import json
    import tempfile

    def status(msg):
        if on_status:
            on_status(msg)

    try:
        status("Buscando versão mais recente...")
        req = urllib.request.Request(
            "https://api.github.com/repos/ExistentialAudio/BlackHole/releases/latest",
            headers={"User-Agent": "SinapseIA/1.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            release = json.loads(resp.read())

        pkg_url = None
        pkg_name = "BlackHole2ch.pkg"
        for asset in release.get("assets", []):
            name = asset["name"].lower()
            if "2ch" in name and name.endswith(".pkg"):
                pkg_url = asset["browser_download_url"]
                pkg_name = asset["name"]
                break

        if not pkg_url:
            return {"ok": False, "erro": "Instalador nao encontrado na release mais recente."}

        tmp_path = os.path.join(tempfile.gettempdir(), pkg_name)
        status(f"Baixando {pkg_name}...")
        urllib.request.urlretrieve(pkg_url, tmp_path)

        status("Abrindo instalador...")
        subprocess.run(["open", tmp_path], check=False)
        return {"ok": True}

    except Exception as e:
        return {"ok": False, "erro": str(e)}


def drives_extras():
    """Retorna drives ou volumes adicionais a escanear, por plataforma."""
    extras = []
    if _SYS == "Windows":
        for letra in "DEFGHIJ":
            drive = f"{letra}:\\"
            if os.path.exists(drive):
                extras.append(drive)
    elif _SYS == "Darwin":
        volumes = "/Volumes"
        if os.path.isdir(volumes):
            try:
                for item in os.listdir(volumes):
                    p = os.path.join(volumes, item)
                    if os.path.isdir(p):
                        extras.append(p)
            except PermissionError:
                pass
    return extras
