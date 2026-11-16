"""Own cover art for the folders added in V6: a 16:9 card (PNG) and an animated focus GIF per folder.
Plain name + colour + country badge, no brand logos."""
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = "covers"; os.makedirs(OUT, exist_ok=True)
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

ITEMS = [  # slug, name, sub line, colour, badge
    ("wow", "WOW", "Serien · Filme · Sky Originals", "#7b2ff7", "DE"),
    ("sky-go", "Sky Go", "Serien · Filme · Sport", "#0a6ee6", "DE"),
    ("joyn", "Joyn", "ProSieben · Sat.1 · Originals", "#ff2e7e", "DE"),
    ("rtl-plus", "RTL+", "Serien · Shows · Filme", "#e3001b", "DE"),
    ("magentatv", "MagentaTV", "Serien · Filme · Originals", "#e20074", "DE"),
    ("ard", "ARD Mediathek", "Krimis · Dokus · Filme", "#1f4fb4", "DE"),
    ("zdf", "ZDF Mediathek", "Krimis · Serien · Dokus", "#f47c20", "DE"),
    ("arte", "Arte", "Kino · Dokus · Kultur", "#f05a28", "DE"),
    ("netzkino", "Netzkino", "Filme gratis", "#c4161c", "DE"),
    ("jiohotstar", "JioHotstar", "Hindi · Serien · Filme", "#2541d8", "IN"),
    ("zee5", "Zee5", "Hindi · Serien · Filme", "#8a2be2", "IN"),
    ("sonyliv", "SonyLIV", "Hindi · Serien · Filme", "#c9a227", "IN"),
    ("netflix-india", "Netflix India", "Hindi · Serien · Filme", "#e50914", "IN"),
    ("prime-india", "Prime Video India", "Hindi · Serien · Filme", "#00a8e1", "IN"),
    ("hindi-dubbed", "Hindi Dubbed", "Hollywood · South · Serien", "#ff8a00", "IN"),
    ("demnaechst-digital", "Demnächst digital", "Bald zum Streamen · DE & IN", "#7c4dff", None),
    ("jetzt-im-kino", "Jetzt im Kino", "Was gerade läuft · DE & IN", "#e0a800", None),
    ("zufall", "Zufall", "Jedes Mal etwas Neues", "#16c784", None),
]
FLAGS = {"DE": ["#000000", "#dd0000", "#ffce00"], "IN": ["#ff9933", "#ffffff", "#138808"]}

def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def fit(draw, text, font_path, max_w, start):
    size = start
    while size > 20:
        f = ImageFont.truetype(font_path, size)
        if draw.textlength(text, font=f) <= max_w: return f
        size -= 4
    return ImageFont.truetype(font_path, size)

def card(name, sub, colour, badge, W, H, phase=None):
    c = rgb(colour); base = (12, 12, 18)
    img = Image.new("RGB", (W, H), base)
    px = img.load()
    for y in range(H):  # diagonal gradient: colour top-left, almost black bottom-right
        for x in range(0, W, 2):
            t = min(1, (x / W) * 0.6 + (y / H) * 0.7)
            col = mix(mix(c, (0, 0, 0), 0.25), base, t ** 0.9)
            px[x, y] = col
            if x + 1 < W: px[x + 1, y] = col
    glow = Image.new("L", (W, H), 0); g = ImageDraw.Draw(glow)
    r = int(H * 0.75); cx, cy = int(W * 0.18), int(H * 0.2)
    g.ellipse((cx - r, cy - r, cx + r, cy + r), fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(H // 5))
    img = Image.composite(Image.new("RGB", (W, H), mix(c, (255, 255, 255), 0.15)), img, glow)
    if phase is not None:  # moving light sweep for the focus animation
        sweep = Image.new("L", (W, H), 0); s = ImageDraw.Draw(sweep)
        x0 = int(-W * 0.5 + phase * W * 2.0); bw = W // 6
        s.polygon([(x0, 0), (x0 + bw, 0), (x0 + bw - H // 2, H), (x0 - H // 2, H)], fill=70)
        sweep = sweep.filter(ImageFilter.GaussianBlur(W // 40))
        img = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), img, sweep)
    d = ImageDraw.Draw(img)
    pad = int(W * 0.07)
    title = fit(d, name, BLACK, W - 2 * pad, int(H * 0.2))
    tb = d.textbbox((0, 0), name, font=title)
    ty = int(H * 0.5) - (tb[3] - tb[1]) // 2 - tb[1]
    d.text((pad + 3, ty + 4), name, font=title, fill=(0, 0, 0))
    d.text((pad, ty), name, font=title, fill=(255, 255, 255))
    sf = ImageFont.truetype(BOLD, max(14, int(H * 0.055)))
    d.text((pad, ty + tb[3] + int(H * 0.04)), sub, font=sf, fill=mix(c, (255, 255, 255), 0.7))
    d.rectangle((pad, ty - int(H * 0.06), pad + int(W * 0.08), ty - int(H * 0.06) + max(3, H // 90)), fill=c)
    if badge:  # small flag + country code, top right (drawn, so it looks the same on every device)
        fw, fh = int(W * 0.07), int(W * 0.045); x1, y1 = W - pad - fw, pad
        for i, s in enumerate(FLAGS[badge]):
            d.rectangle((x1, y1 + i * fh // 3, x1 + fw, y1 + (i + 1) * fh // 3), fill=s)
        if badge == "IN":
            rr = fh // 7; d.ellipse((x1 + fw // 2 - rr, y1 + fh // 2 - rr, x1 + fw // 2 + rr, y1 + fh // 2 + rr), outline="#000080", width=max(1, H // 360))
        bf = ImageFont.truetype(BOLD, max(12, int(H * 0.045)))
        d.text((x1 - int(W * 0.012), y1 + fh // 2), badge, font=bf, fill=(255, 255, 255), anchor="rm")
    return img

for slug, name, sub, colour, badge in ITEMS:
    card(name, sub, colour, badge, 1280, 720).save(f"{OUT}/{slug}.png", optimize=True)
    frames = [card(name, sub, colour, badge, 480, 270, phase=i / 15) for i in range(16)]
    frames = [f.convert("P", palette=Image.ADAPTIVE, colors=96) for f in frames]
    frames[0].save(f"{OUT}/{slug}-focus.gif", save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)
print("ok")
