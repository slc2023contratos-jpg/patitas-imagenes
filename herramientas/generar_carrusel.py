"""Genera las láminas de un carrusel de Patitas en Casa (1080x1920, JPG: TikTok no acepta PNG).

Uso:
    python3 generar_carrusel.py carrusel.json carpeta_salida

El JSON tiene esta forma:
{
  "portada": {"etiqueta": "PERROS", "titulo": "5 alimentos...", "subtitulo": "Guarda este post"},
  "laminas": [
    {"numero": "1", "titulo": "Chocolate", "texto": "Contiene teobromina..."}
  ],
  "cierre": {"titulo": "¿Comió algo de esto?", "texto": "Llama a tu veterinario...",
             "llamado": "Recetas seguras para tu peludo: link en mi perfil"}
}
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT_DIR = "/usr/share/fonts/opentype/inter"

# Paleta de la marca
CREMA = (250, 243, 232)
TINTA = (43, 33, 26)
CANELA = (196, 106, 43)
SALVIA = (122, 150, 112)
SUAVE = (120, 104, 90)


def fuente(nombre, tam):
    ruta = os.path.join(FONT_DIR, nombre)
    try:
        return ImageFont.truetype(ruta, tam)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", tam)


def partir(draw, texto, fnt, ancho):
    lineas = []
    for parrafo in texto.split("\n"):
        palabras, actual = parrafo.split(), ""
        for p in palabras:
            prueba = (actual + " " + p).strip()
            if draw.textlength(prueba, font=fnt) <= ancho:
                actual = prueba
            else:
                if actual:
                    lineas.append(actual)
                actual = p
        lineas.append(actual)
    return lineas


def bloque(draw, texto, fnt, x, y, ancho, color, interlineado=1.25):
    alto = int(fnt.size * interlineado)
    for linea in partir(draw, texto, fnt, ancho):
        draw.text((x, y), linea, font=fnt, fill=color)
        y += alto
    return y


def huella(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.9], fill=color)
    for ang, dist in ((-60, 1.55), (-20, 1.75), (20, 1.75), (60, 1.55)):
        a = math.radians(ang - 90)
        px, py = cx + math.cos(a) * r * dist, cy + math.sin(a) * r * dist
        rr = r * 0.42
        draw.ellipse([px - rr, py - rr * 1.15, px + rr, py + rr * 1.15], fill=color)


def base(fondo=CREMA):
    img = Image.new("RGB", (W, H), fondo)
    d = ImageDraw.Draw(img)
    return img, d


def marca(d, color=SUAVE):
    f = fuente("Inter-SemiBold.otf", 34)
    huella(d, 108, H - 128, 18, CANELA)
    d.text((150, H - 152), "Patitas en Casa · @patitasencasa2", font=f, fill=color)


def portada(datos):
    img, d = base(CANELA)
    huella(d, W - 220, 360, 120, (214, 134, 78))
    huella(d, W - 190, H - 330, 70, (214, 134, 78))
    y = 640
    d.text((96, y), datos.get("etiqueta", "").upper(), font=fuente("Inter-Bold.otf", 40), fill=CREMA)
    y += 90
    y = bloque(d, datos["titulo"], fuente("InterDisplay-Black.otf", 112), 96, y, W - 192, CREMA, 1.08)
    if datos.get("subtitulo"):
        y += 40
        bloque(d, datos["subtitulo"], fuente("Inter-Medium.otf", 46), 96, y, W - 192, (255, 228, 205))
    d.text((96, H - 160), "Desliza  →", font=fuente("Inter-Bold.otf", 44), fill=CREMA)
    return img


def lamina(datos, total):
    img, d = base()
    d.rounded_rectangle([96, 460, 296, 660], radius=40, fill=CANELA)
    num = str(datos["numero"])
    fn = fuente("InterDisplay-Black.otf", 120)
    tw = d.textlength(num, font=fn)
    d.text((196 - tw / 2, 482), num, font=fn, fill=CREMA)
    y = 770
    y = bloque(d, datos["titulo"], fuente("InterDisplay-ExtraBold.otf", 110), 96, y, W - 192, TINTA, 1.08)
    y += 50
    d.line([96, y, 296, y], fill=SALVIA, width=8)
    y += 60
    bloque(d, datos["texto"], fuente("Inter-Medium.otf", 60), 96, y, W - 192, TINTA, 1.38)
    marca(d)
    return img


def cierre(datos):
    img, d = base(SALVIA)
    huella(d, W // 2, 470, 110, CREMA)
    y = 760
    y = bloque(d, datos["titulo"], fuente("InterDisplay-Black.otf", 96), 96, y, W - 192, CREMA, 1.08)
    y += 50
    y = bloque(d, datos["texto"], fuente("Inter-Medium.otf", 52), 96, y, W - 192, CREMA, 1.35)
    if datos.get("llamado"):
        y += 70
        fl = fuente("Inter-Bold.otf", 50)
        lineas = partir(d, datos["llamado"], fl, W - 272)
        alto = len(lineas) * 64 + 80
        d.rounded_rectangle([96, y, W - 96, y + alto], radius=36, fill=CREMA)
        yy = y + 40
        for ln in lineas:
            d.text((136, yy), ln, font=fl, fill=TINTA)
            yy += 64
    d.text((96, H - 160), "Patitas en Casa · @patitasencasa2", font=fuente("Inter-SemiBold.otf", 34), fill=CREMA)
    return img


def main():
    datos = json.load(open(sys.argv[1], encoding="utf-8"))
    salida = sys.argv[2]
    os.makedirs(salida, exist_ok=True)
    imagenes = [portada(datos["portada"])]
    imagenes += [lamina(l, len(datos["laminas"])) for l in datos["laminas"]]
    imagenes.append(cierre(datos["cierre"]))
    rutas = []
    for i, im in enumerate(imagenes, 1):
        ruta = os.path.join(salida, f"{i:02d}.jpg")
        im.save(ruta, "JPEG", quality=92, optimize=True)
        rutas.append(ruta)
    print("\n".join(rutas))


if __name__ == "__main__":
    main()
