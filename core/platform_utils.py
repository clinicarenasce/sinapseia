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
