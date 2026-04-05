"""Gera icone original: esponja divertida absorvendo conhecimento."""
from PIL import Image, ImageDraw, ImageFont
import math

SIZE = 256
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# --- Ondas de conhecimento sendo absorvidas (linhas azuis ao redor) ---
for i, r in enumerate([125, 118, 111]):
    alpha = 180 - i * 50
    color = (0, 120, 212, alpha)
    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    cx, cy = 128, 125
    od.arc((cx-r, cy-r, cx+r, cy+r), start=200, end=260, fill=color, width=3)
    od.arc((cx-r, cy-r, cx+r, cy+r), start=280, end=340, fill=color, width=3)
    od.arc((cx-r, cy-r, cx+r, cy+r), start=30, end=70, fill=color, width=3)
    od.arc((cx-r, cy-r, cx+r, cy+r), start=110, end=160, fill=color, width=3)
    img = Image.alpha_composite(img, overlay)
d = ImageDraw.Draw(img)

# --- Corpo da esponja (retangulo amarelo arredondado, levemente inclinado pra dar vida) ---
corpo = (48, 38, 208, 210)
d.rounded_rectangle(corpo, radius=24, fill="#FFD93D", outline="#D4A800", width=3)

# --- Buracos da esponja ---
buracos = [(75, 65, 13), (165, 58, 11), (105, 120, 14), (175, 125, 10),
           (70, 155, 12), (145, 168, 13), (125, 65, 9), (185, 165, 8)]
for hx, hy, hr in buracos:
    d.ellipse((hx-hr, hy-hr, hx+hr, hy+hr), fill="#E8B800", outline="#C8A200", width=2)

# --- Olhos grandes e animados (olhando pra cima, curiosos) ---
# Esquerdo
d.ellipse((76, 68, 122, 114), fill="white", outline="#2D2D2D", width=3)
d.ellipse((90, 74, 110, 94), fill="#1A1A1A")
d.ellipse((96, 76, 104, 84), fill="white")
# Sobrancelha esquerda (levantada = curiosidade)
d.arc((72, 52, 126, 80), start=200, end=340, fill="#2D2D2D", width=3)

# Direito
d.ellipse((134, 68, 180, 114), fill="white", outline="#2D2D2D", width=3)
d.ellipse((148, 74, 168, 94), fill="#1A1A1A")
d.ellipse((154, 76, 162, 84), fill="white")
# Sobrancelha direita
d.arc((130, 52, 184, 80), start=200, end=340, fill="#2D2D2D", width=3)

# --- Sorriso grande e feliz ---
d.arc((82, 98, 174, 168), start=5, end=175, fill="#2D2D2D", width=4)
# Bochechas rosadas
d.ellipse((68, 112, 88, 130), fill="#FFB6C1")
d.ellipse((168, 112, 188, 130), fill="#FFB6C1")
# Dentes simpaticos
d.rectangle((118, 134, 138, 152), fill="white", outline="#2D2D2D", width=2)

# --- Bracinhos segurando um fone de ouvido (representando absorver audio) ---
# Braco esquerdo
d.line([(48, 140), (28, 120), (35, 100)], fill="#D4A800", width=6)
d.ellipse((25, 85, 48, 108), fill="#0078D4", outline="#005A9E", width=2)  # fone esquerdo

# Braco direito
d.line([(208, 140), (228, 120), (221, 100)], fill="#D4A800", width=6)
d.ellipse((208, 85, 231, 108), fill="#0078D4", outline="#005A9E", width=2)  # fone direito

# Arco do fone de ouvido
d.arc((35, 35, 221, 105), start=190, end=350, fill="#0078D4", width=4)

# --- Letras/simbolos flutuando (conhecimento) ---
try:
    font = ImageFont.truetype("arial.ttf", 18)
    font_sm = ImageFont.truetype("arial.ttf", 14)
except:
    font = ImageFont.load_default()
    font_sm = font

# Letras flutuando ao redor representando conhecimento
letras = [("A", 18, 20), ("B", 220, 15), ("?", 10, 170),
          ("+", 235, 155), ("1", 25, 50), ("0", 225, 45)]
for letra, lx, ly in letras:
    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.text((lx, ly), letra, fill=(0, 120, 212, 140), font=font_sm)
    img = Image.alpha_composite(img, overlay)
d = ImageDraw.Draw(img)

# --- Parte inferior: calca/base ---
d.rectangle((48, 192, 208, 214), fill="#8B5E3C", outline="#5C3A1E", width=2)
d.rectangle((48, 186, 208, 196), fill="#2D2D2D")
# Fivela
d.rounded_rectangle((114, 183, 142, 199), radius=3, fill="#FFD93D", outline="#2D2D2D", width=2)

# --- Perninhas ---
d.rectangle((88, 214, 108, 240), fill="#FFD93D", outline="#D4A800", width=2)
d.rectangle((148, 214, 168, 240), fill="#FFD93D", outline="#D4A800", width=2)
# Sapatos
d.ellipse((78, 234, 118, 252), fill="#2D2D2D")
d.ellipse((138, 234, 178, 252), fill="#2D2D2D")

# --- Salvar ---
ico_path = r"C:\Users\conta\transcritor.ico"
sizes = [(256, 256), (64, 64), (48, 48), (32, 32), (16, 16)]
imgs = [img.resize(s, Image.LANCZOS) for s in sizes]
imgs[0].save(ico_path, format="ICO", sizes=sizes, append_images=imgs[1:])

# PNG preview
img.save(r"C:\Users\conta\transcritor_preview.png")
print(f"Icone salvo em: {ico_path}")
