# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec para macOS."""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Arquivos de dados necessários
datas = [
    ('web', 'web'),
    ('core', 'core'),
    ('integrations', 'integrations'),
]

# Coletar dados do Eel (templates web)
datas += collect_data_files('eel')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'eel',
        'bottle',
        'gevent',
        'geventwebsocket',
        'faster_whisper',
        'soundcard',
        'soundfile',
        'numpy',
        'core.ai',
        'core.config',
        'core.naming',
        'core.recorder',
        'core.resumo',
        'core.storage',
        'core.transcriber',
        'core.wikilinks',
        'core.platform_utils',
        'integrations.obsidian',
        'integrations.logseq',
        'integrations.notion',
        'integrations.roam',
        'integrations.base',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['winsound', 'winreg', 'win32api'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SinapseIA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SinapseIA',
)

app = BUNDLE(
    coll,
    name='SinapseIA.app',
    icon='web/logo.icns',
    bundle_identifier='com.clinicarenasce.sinapseia',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'NSMicrophoneUsageDescription': 'Necessário para gravar áudio do microfone.',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1',
        'LSUIElement': False,
    },
)
