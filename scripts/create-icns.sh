#!/bin/bash
# Roda no macOS para criar logo.icns a partir de logo.png
# Executar a partir da raiz do projeto: bash scripts/create-icns.sh

set -e
ICONSET="web/SinapseIA.iconset"
mkdir -p "$ICONSET"

sips -z 16   16   web/logo.png --out "$ICONSET/icon_16x16.png"
sips -z 32   32   web/logo.png --out "$ICONSET/icon_16x16@2x.png"
sips -z 32   32   web/logo.png --out "$ICONSET/icon_32x32.png"
sips -z 64   64   web/logo.png --out "$ICONSET/icon_32x32@2x.png"
sips -z 128  128  web/logo.png --out "$ICONSET/icon_128x128.png"
sips -z 256  256  web/logo.png --out "$ICONSET/icon_128x128@2x.png"
sips -z 256  256  web/logo.png --out "$ICONSET/icon_256x256.png"
sips -z 512  512  web/logo.png --out "$ICONSET/icon_256x256@2x.png"
sips -z 512  512  web/logo.png --out "$ICONSET/icon_512x512.png"
sips -z 1024 1024 web/logo.png --out "$ICONSET/icon_512x512@2x.png"

iconutil -c icns "$ICONSET" -o web/logo.icns
rm -rf "$ICONSET"
echo "web/logo.icns criado com sucesso"
