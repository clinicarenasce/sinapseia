# Build — Sinapse&IA

## Pré-requisitos

```bash
pip install pyinstaller
pip install Pillow          # opcional — apenas para gerar logo.ico
# UPX (opcional, reduz ~30% o tamanho): https://upx.github.io/
# Inno Setup 6 (para gerar o instalador .exe): https://jrsoftware.org/isinfo.php
```

## 1. Gerar logo.ico (opcional)

Se `web/logo.png` existir e `web/logo.ico` ainda não:

```bash
python -c "
from PIL import Image
img = Image.open('web/logo.png')
img.save('web/logo.ico', format='ICO', sizes=[(256,256),(128,128),(64,64),(32,32),(16,16)])
print('logo.ico gerado')
"
```

## 2. Build PyInstaller

```bash
pyinstaller sinapseia.spec
```

Saída em `dist/SinapseIA/SinapseIA.exe`

## Sobre o modelo Whisper

O modelo `large-v3-turbo` (~1.6 GB) **não está embutido** no instalador.
Na primeira execução, o app baixa automaticamente para:
```
C:\Users\<usuario>\.cache\huggingface\hub\
```
Execuções seguintes usam o cache local — sem internet necessária.

## 3. Zipar para distribuição direta

```powershell
Compress-Archive -Path dist\SinapseIA\* -DestinationPath SinapseIA_v1.0_Windows.zip
```

## 4. Gerar instalador com Inno Setup (recomendado)

### Pré-condição: configurar Stripe

Antes de compilar o instalador, substitua o placeholder no script `.iss`:

```
installer\sinapseia_setup.iss  →  linha: #define StripeURL  "STRIPE_PAYMENT_LINK_URL"
```

Substitua `STRIPE_PAYMENT_LINK_URL` pela URL real do seu Payment Link no Stripe
(ex: `https://buy.stripe.com/XXXXXXXXXXXXXXXX`).

Para criar o Payment Link:
1. Stripe Dashboard → Products → Criar produto "Sinapse&IA Pro" (R$19/mês)
2. Payment Links → Criar link → ativar **Free trial: 30 dias**
3. Copiar a URL gerada

### Compilar o instalador

```bash
# Via linha de comando (após instalar Inno Setup 6):
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\sinapseia_setup.iss

# Ou abrir installer\sinapseia_setup.iss no Inno Setup IDE e pressionar F9
```

Saída: `dist\installer\SinapseIA_Setup_1.0.exe`

### O que o instalador faz

- Instala o app em `%ProgramFiles%\SinapseIA\`
- Exibe tela de trial Pro (card dourado pré-selecionado vs card cinza "Gratuito")
- Se o usuário aceitar o trial → abre `buy.stripe.com/...` no browser após a instalação
- Se recusar → instala normalmente sem abrir nenhuma URL

## Reduzir tamanho (opcional)

```bash
# Instalar UPX e adicionar ao PATH
# O spec já tem upx=True — rode o build normalmente
```

## Distribuir

- **Simples**: zipar `dist/SinapseIA/` e hospedar no GitHub Releases
- **Instalador**: usar `dist/installer/SinapseIA_Setup_1.0.exe` gerado pelo Inno Setup

### GitHub Releases

```bash
gh release create v1.0 SinapseIA_v1.0_Windows.zip \
  --title "Sinapse&IA v1.0" \
  --notes "Primeira versão pública."
```
