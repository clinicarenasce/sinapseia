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


def multi_output_configurado():
    """Verifica se já existe um Multi-Output Device com BlackHole como saída do sistema."""
    if _SYS != "Darwin":
        return True
    try:
        result = subprocess.run(
            ["system_profiler", "SPAudioDataType"],
            capture_output=True, text=True, timeout=5
        )
        output = result.stdout.lower()
        tem_multi = "multi-output" in output
        tem_bh_output = False
        for bloco in output.split("\n\n"):
            if "default output device: yes" in bloco and "blackhole" in bloco:
                tem_bh_output = True
        return tem_multi or tem_bh_output
    except Exception:
        return False


def criar_multi_output(on_status=None):
    """Cria Multi-Output Device (BlackHole + saída atual) e define como saída do sistema."""
    def status(msg):
        if on_status:
            on_status(msg)

    if _SYS != "Darwin":
        return {"ok": False, "erro": "Apenas macOS."}

    script = r"""
tell application "Audio MIDI Setup"
    activate
end tell
delay 1
tell application "System Events"
    tell process "Audio MIDI Setup"
        -- Clica no botao "+"
        click button 1 of splitter group 1 of window 1
        delay 0.5
        -- Seleciona "Criar Dispositivo de Multiplas Saidas"
        click menu item 1 of menu 1 of button 1 of splitter group 1 of window 1
        delay 0.5
    end tell
end tell
"""
    try:
        status("Abrindo Audio MIDI Setup...")
        subprocess.run(["osascript", "-e", script], timeout=10, capture_output=True)
        return {"ok": True, "manual": True}
    except Exception as e:
        return {"ok": False, "erro": str(e)}


def instalar_blackhole(on_status=None):
    """Baixa o .pkg do BlackHole 2ch diretamente e abre o instalador nativo."""
    import urllib.request
    import json
    import tempfile

    FALLBACK_VERSION = "0.6.1"

    def status(msg):
        if on_status:
            on_status(msg)

    def url_para_versao(versao):
        v = versao.lstrip("v")
        return f"https://existential.audio/downloads/BlackHole2ch-{v}.pkg"

    try:
        status("Buscando versão mais recente...")
        versao = FALLBACK_VERSION
        try:
            req = urllib.request.Request(
                "https://api.github.com/repos/ExistentialAudio/BlackHole/releases/latest",
                headers={"User-Agent": "SinapseIA/1.0"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                release = json.loads(resp.read())
            versao = release.get("tag_name", FALLBACK_VERSION).lstrip("v")
        except Exception:
            versao = FALLBACK_VERSION

        pkg_url = url_para_versao(versao)
        pkg_name = f"BlackHole2ch-{versao}.pkg"
        tmp_path = os.path.join(tempfile.gettempdir(), pkg_name)

        status(f"Baixando BlackHole {versao}...")
        req_pkg = urllib.request.Request(
            pkg_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/octet-stream, */*",
            },
        )
        with urllib.request.urlopen(req_pkg, timeout=60) as resp:
            with open(tmp_path, "wb") as f:
                f.write(resp.read())

        status("Abrindo instalador...")
        subprocess.run(["open", tmp_path], check=False)
        return {"ok": True}

    except Exception as e:
        return {"ok": False, "erro": str(e)}


def escolher_pasta_nativa(titulo="Escolha uma pasta", initial_dir=None):
    """Abre dialogo nativo de escolha de pasta. Usa AppleScript no Mac, tkinter nos outros."""
    if _SYS == "Darwin":
        script = f'POSIX path of (choose folder with prompt "{titulo}"'
        if initial_dir and os.path.isdir(initial_dir):
            script += f' default location POSIX file "{initial_dir}"'
        script += ")"
        try:
            r = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=120,
            )
            path = r.stdout.strip().rstrip("/")
            return path if path and os.path.isdir(path) else None
        except Exception:
            return None
    # Fallback: tkinter
    from tkinter import Tk, filedialog
    try:
        root = Tk(); root.withdraw(); root.attributes("-topmost", True)
        pasta = filedialog.askdirectory(parent=root, initialdir=initial_dir or "", title=titulo)
        root.destroy()
        return pasta if pasta else None
    except Exception:
        return None


def escolher_arquivo_nativo(titulo="Escolha um arquivo", tipos=None):
    """Abre dialogo nativo de escolha de arquivo. Usa AppleScript no Mac."""
    if _SYS == "Darwin":
        ext_list = []
        if tipos:
            for desc, exts in tipos:
                for e in exts.replace("*.", "").split():
                    if e not in ext_list:
                        ext_list.append(e)
        script = f'POSIX path of (choose file with prompt "{titulo}"'
        if ext_list:
            tipo_str = ", ".join(f'"{e}"' for e in ext_list)
            script += f" of type {{{tipo_str}}}"
        script += ")"
        try:
            r = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=120,
            )
            path = r.stdout.strip()
            return path if path and os.path.exists(path) else None
        except Exception:
            return None
    # Fallback: tkinter
    from tkinter import Tk, filedialog
    try:
        root = Tk(); root.withdraw(); root.attributes("-topmost", True)
        ft = [(d, e) for d, e in (tipos or [])]
        path = filedialog.askopenfilename(parent=root, filetypes=ft, title=titulo)
        root.destroy()
        return path if path else None
    except Exception:
        return None


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
