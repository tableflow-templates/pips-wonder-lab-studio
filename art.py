"""Character rig, backgrounds and props for The Curiosity Crew (original designs)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from functools import lru_cache
import math

W, H = 1920, 1080
SS = 2  # supersampling factor for sprites
INK = (59, 42, 32, 255)
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

@lru_cache(None)
def font(size):
    return ImageFont.truetype(FONT_B, size)

def sprite(w, h, fn):
    """Draw at SS scale with fn(draw, s) where s scales coordinates; return downsampled RGBA."""
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fn(d, lambda *v: [x * SS for x in v], SS)
    return im.resize((w, h), Image.LANCZOS)

def E(d, s, box, fill, ow=6, outline=INK):
    d.ellipse(s(*box), fill=fill, outline=outline, width=int(ow * SS) if outline else 0)

def RR(d, s, box, r, fill, ow=6, outline=INK):
    d.rounded_rectangle(s(*box), radius=r * SS, fill=fill, outline=outline, width=int(ow * SS) if outline else 0)

# ---------------- characters ----------------
CW, CH = 440, 640

def _eyes_glasses(d, s, eyes, expr):
    for cx in (168, 262):
        E(d, s, (cx - 36, 186, cx + 36, 258), (255, 255, 255, 255), 7)
        if eyes == "closed":
            d.arc(s(cx - 16, 208, cx + 16, 236), 200, 340, fill=INK, width=5 * SS)
        else:
            r = 13 if expr == "surprised" else 11
            E(d, s, (cx - r, 222 - r, cx + r, 222 + r), INK, 0, None)
            E(d, s, (cx - 4, 214, cx + 2, 220), (255, 255, 255, 255), 0, None)
    d.line(s(204, 222, 226, 222), fill=INK, width=6 * SS)

def _mouth(d, s, cx, cy, mouth, expr):
    if mouth == 0 and expr != "surprised":
        d.arc(s(cx - 28, cy - 22, cx + 28, cy + 18), 20, 160, fill=INK, width=6 * SS)
    elif mouth == 1:
        E(d, s, (cx - 20, cy - 6, cx + 20, cy + 22), (170, 50, 60, 255), 5)
    else:
        E(d, s, (cx - 18, cy - 12, cx + 18, cy + 26), (170, 50, 60, 255), 5)

def draw_mia(eyes="open", mouth=0, expr=None):
    def fn(d, s, k):
        # hair back
        for (x, y, r) in [(120, 150, 70), (300, 150, 70), (105, 240, 62), (315, 240, 62), (130, 320, 52), (290, 320, 52), (215, 90, 85)]:
            E(d, s, (x - r, y - r, x + r, y + r), (214, 82, 43, 255), 6)
        # body: raincoat
        d.polygon(s(130, 360, 310, 360, 360, 640, 80, 640), fill=(255, 205, 60, 255), outline=INK, width=6 * k)
        RR(d, s, (150, 340, 290, 390), 20, (255, 205, 60, 255))
        for y in (430, 490, 550):
            E(d, s, (212, y, 228, y + 16), (230, 150, 40, 255), 4)
        # arms
        RR(d, s, (70, 390, 130, 560), 28, (255, 205, 60, 255))
        RR(d, s, (310, 390, 370, 560), 28, (255, 205, 60, 255))
        E(d, s, (72, 540, 128, 596), (246, 201, 164, 255), 5)
        E(d, s, (312, 540, 368, 596), (246, 201, 164, 255), 5)
        # head
        E(d, s, (95, 95, 335, 335), (246, 201, 164, 255), 7)
        # bangs
        for (x, y, r) in [(150, 118, 46), (215, 100, 50), (280, 118, 46)]:
            E(d, s, (x - r, y - r, x + r, y + r), (214, 82, 43, 255), 0, None)
        E(d, s, (128, 270, 158, 290), (245, 150, 140, 200), 0, None)
        E(d, s, (272, 270, 302, 290), (245, 150, 140, 200), 0, None)
        _eyes_glasses(d, s, eyes, expr)
        _mouth(d, s, 215, 292, mouth, expr)
    return sprite(CW, CH, fn)

def draw_leo(eyes="open", mouth=0, expr=None):
    def fn(d, s, k):
        # hood behind head
        E(d, s, (80, 200, 360, 420), (76, 175, 80, 255), 6)
        # body hoodie
        d.polygon(s(120, 370, 320, 370, 370, 640, 70, 640), fill=(76, 175, 80, 255), outline=INK, width=6 * k)
        # backpack straps
        RR(d, s, (128, 372, 156, 620), 10, (140, 90, 50, 255), 4)
        RR(d, s, (284, 372, 312, 620), 10, (140, 90, 50, 255), 4)
        d.line(s(200, 380, 196, 450), fill=(240, 240, 240, 255), width=5 * k)
        d.line(s(240, 380, 244, 450), fill=(240, 240, 240, 255), width=5 * k)
        RR(d, s, (170, 520, 270, 580), 18, (60, 150, 64, 255), 5)
        # arms
        RR(d, s, (62, 395, 124, 565), 28, (76, 175, 80, 255))
        RR(d, s, (316, 395, 378, 565), 28, (76, 175, 80, 255))
        E(d, s, (64, 545, 122, 603), (141, 90, 59, 255), 5)
        E(d, s, (318, 545, 376, 603), (141, 90, 59, 255), 5)
        # head
        E(d, s, (100, 110, 340, 350), (141, 90, 59, 255), 7)
        # hair cap
        d.chord(s(104, 100, 336, 270), 180, 360, fill=(30, 25, 25, 255), outline=INK, width=6 * k)
        E(d, s, (92, 205, 122, 255), (141, 90, 59, 255), 5)  # ears
        E(d, s, (318, 205, 348, 255), (141, 90, 59, 255), 5)
        for cx in (175, 265):
            if eyes == "closed":
                d.arc(s(cx - 18, 212, cx + 18, 242), 200, 340, fill=INK, width=6 * k)
            else:
                ry = 26 if expr == "surprised" else 22
                E(d, s, (cx - 20, 228 - ry, cx + 20, 228 + ry), (255, 255, 255, 255), 5)
                E(d, s, (cx - 9, 222, cx + 9, 240), INK, 0, None)
                E(d, s, (cx - 4, 224, cx + 1, 229), (255, 255, 255, 255), 0, None)
        if expr == "surprised":
            d.arc(s(150, 172, 200, 196), 200, 340, fill=INK, width=5 * k)
            d.arc(s(240, 172, 290, 196), 200, 340, fill=INK, width=5 * k)
        _mouth(d, s, 220, 296, mouth, expr)
    return sprite(CW, CH, fn)

def draw_pip(eyes="open", talk=0, expr=None):
    def fn(d, s, k):
        d.line(s(220, 150, 220, 90), fill=INK, width=7 * k)
        E(d, s, (200, 62, 240, 102), (255, 90, 90, 255) if talk else (255, 200, 80, 255), 5)
        # side arms
        E(d, s, (70, 300, 120, 370), (225, 230, 236, 255), 6)
        E(d, s, (320, 300, 370, 370), (225, 230, 236, 255), 6)
        E(d, s, (95, 145, 345, 395), (244, 246, 248, 255), 7)
        RR(d, s, (138, 205, 302, 320), 40, (31, 42, 68, 255), 6)
        for cx in (185, 255):
            if eyes == "closed":
                RR(d, s, (cx - 24, 258, cx + 24, 268), 5, (79, 195, 247, 255), 0, None)
            else:
                h = 46 if expr == "surprised" else (34 if talk else 40)
                RR(d, s, (cx - 18, 262 - h // 2, cx + 18, 262 + h // 2), 14, (79, 195, 247, 255), 0, None)
        if talk:
            RR(d, s, (200, 296, 240, 306), 4, (79, 195, 247, 255), 0, None)
        E(d, s, (150, 340, 175, 360), (255, 170, 170, 255), 0, None)
        E(d, s, (265, 340, 290, 360), (255, 170, 170, 255), 0, None)
    return sprite(CW, 460, fn)

@lru_cache(None)
def char(name, eyes, mouth, expr):
    if name == "MIA": return draw_mia(eyes, mouth, expr)
    if name == "LEO": return draw_leo(eyes, mouth, expr)
    return draw_pip(eyes, mouth, expr)

# ---------------- backgrounds ----------------
def lab_bg():
    def fn(d, s, k):
        # wall planks
        for i in range(0, 1920, 120):
            c = (232, 201, 160, 255) if (i // 120) % 2 == 0 else (226, 194, 152, 255)
            d.rectangle(s(i, 0, i + 120, 1080), fill=c)
            d.line(s(i, 0, i, 1080), fill=(205, 168, 122, 255), width=3 * k)
        # window
        E(d, s, (150, 120, 610, 580), (150, 210, 245, 255), 22, (120, 78, 45, 255))
        for (x, y, r) in [(230, 200, 70), (330, 160, 60), (520, 230, 80), (260, 470, 90), (470, 480, 85), (380, 330, 50)]:
            E(d, s, (x - r, y - r, x + r, y + r), (110, 185, 90, 255), 0, None)
        d.line(s(380, 130, 380, 570), fill=(120, 78, 45, 255), width=12 * k)
        d.line(s(160, 350, 600, 350), fill=(120, 78, 45, 255), width=12 * k)
        E(d, s, (150, 120, 610, 580), None, 22, (120, 78, 45, 255))
        # shelves right
        for y in (230, 430):
            RR(d, s, (1280, y, 1800, y + 24), 6, (150, 98, 58, 255), 4)
        jars = [(1320, 230, (120, 200, 230)), (1420, 230, (250, 170, 90)), (1520, 230, (190, 140, 220)), (1640, 230, (140, 210, 140)),
                (1340, 430, (250, 220, 100)), (1470, 430, (240, 130, 130)), (1600, 430, (130, 180, 240)), (1700, 430, (200, 200, 200))]
        for (x, y, c) in jars:
            RR(d, s, (x, y - 110, x + 70, y), 16, c + (255,), 5)
            RR(d, s, (x + 8, y - 128, x + 62, y - 106), 6, (150, 98, 58, 255), 4)
        # gear poster
        RR(d, s, (760, 300, 1160, 560), 18, (250, 245, 230, 255), 6)
        d.text(s(800, 330), "SCIENCE!", fill=(214, 82, 43, 255), font=font(60 * k))
        for i, c in enumerate([(79, 195, 247), (255, 205, 60), (76, 175, 80)]):
            E(d, s, (810 + i * 110, 430, 900 + i * 110, 520), c + (255,), 5)
        # lamp cord
        d.line(s(960, 0, 960, 120), fill=INK, width=6 * k)
        # table
        RR(d, s, (120, 790, 1800, 850), 14, (176, 112, 64, 255), 6)
        d.rectangle(s(160, 846, 1760, 1080), fill=(150, 92, 50, 255), outline=INK, width=6 * k)
        for x in (560, 960, 1360):
            d.line(s(x, 850, x, 1080), fill=(125, 76, 40, 255), width=5 * k)
    return sprite(W, H, fn).convert("RGB")

def bulb(on):
    def fn(d, s, k):
        if on:
            for r, a in ((150, 50), (115, 90), (85, 140)):
                E(d, s, (160 - r, 150 - r, 160 + r, 150 + r), (255, 230, 90, a), 0, None)
            for i in range(10):
                a = i * math.pi / 5
                d.line(s(160 + 95 * math.cos(a), 150 + 95 * math.sin(a), 160 + 135 * math.cos(a), 150 + 135 * math.sin(a)), fill=(255, 190, 40, 255), width=8 * k)
        RR(d, s, (140, 70, 180, 110), 6, (150, 150, 160, 255), 5)
        E(d, s, (110, 100, 210, 200), (255, 236, 120, 255) if on else (238, 236, 220, 255), 6)
    return sprite(320, 300, fn)

# ---------------- props ----------------
def glass(w=220, h=300, level=0.62, tint=(140, 205, 240)):
    def fn(d, s, k):
        top = h - 20 - int((h - 40) * level)
        d.rectangle(s(18, top, w - 18, h - 22), fill=tint + (170,))
        d.line(s(18, top, w - 18, top), fill=(90, 160, 210, 255), width=4 * k)
        RR(d, s, (12, 10, w - 12, h - 10), 18, None, 6, (90, 120, 140, 255))
        d.line(s(36, 40, 36, h - 60), fill=(255, 255, 255, 200), width=6 * k)
    return sprite(w, h, fn)

def ice_cube(sz=90):
    def fn(d, s, k):
        RR(d, s, (6, 6, sz - 6, sz - 6), 14, (215, 240, 255, 235), 5, (110, 160, 200, 255))
        d.line(s(20, 22, 44, 22), fill=(255, 255, 255, 255), width=6 * k)
        d.line(s(20, 22, 20, 44), fill=(255, 255, 255, 255), width=6 * k)
    return sprite(sz, sz, fn)

def pebble():
    def fn(d, s, k):
        E(d, s, (6, 10, 84, 64), (130, 130, 140, 255), 5)
        E(d, s, (22, 18, 40, 30), (180, 180, 190, 255), 0, None)
    return sprite(90, 72, fn)

def scared_ice():
    def fn(d, s, k):
        RR(d, s, (10, 10, 130, 130), 20, (215, 240, 255, 255), 6, (110, 160, 200, 255))
        E(d, s, (38, 50, 58, 74), INK, 0, None); E(d, s, (82, 50, 102, 74), INK, 0, None)
        d.arc(s(45, 92, 95, 122), 200, 340, fill=INK, width=5 * k)
        for x in (24, 112):
            d.line(s(x, 30, x + 4, 46), fill=(79, 160, 230, 255), width=4 * k)
    return sprite(140, 140, fn)

def balloon_icon():
    def fn(d, s, k):
        E(d, s, (20, 10, 120, 130), (240, 90, 90, 255), 6)
        d.line(s(70, 130, 60, 175), fill=INK, width=4 * k)
        E(d, s, (40, 30, 62, 58), (255, 200, 200, 255), 0, None)
    return sprite(140, 180, fn)

def thought(w=300, h=230):
    def fn(d, s, k):
        for (x, y, r) in [(90, 100, 75), (160, 80, 85), (225, 110, 70), (150, 140, 75)]:
            E(d, s, (x - r, y - r, x + r, y + r), (255, 255, 255, 255), 6)
        for (x, y, r) in [(90, 100, 69), (160, 80, 79), (225, 110, 64), (150, 140, 69)]:
            E(d, s, (x - r, y - r, x + r, y + r), (255, 255, 255, 255), 0, None)
        E(d, s, (60, 200, 84, 224), (255, 255, 255, 255), 5)
    return sprite(w, h, fn)

def badge(text, color=(255, 140, 50)):
    f = font(40)
    tw = int(f.getlength(text))
    w = tw + 90
    def fn(d, s, k):
        RR(d, s, (4, 4, w - 4, 76), 36, color + (255,), 5)
        d.text(s(64, 18), text, fill=(255, 255, 255, 255), font=font(40 * k))
        E(d, s, (18, 22, 52, 56), (255, 255, 255, 255), 0, None)
        d.text(s(29, 20), "!", fill=color + (255,), font=font(30 * k))
    return sprite(w, 80, fn)

def cup(level, ice=False, line_y=0.62):
    w, h = 200, 280
    def fn(d, s, k):
        lt = h - 20 - int((h - 40) * line_y)
        if ice:
            # ice bulging above the line
            d.rectangle(s(20, lt + 6, w - 20, h - 22), fill=(220, 240, 255, 255))
            d.chord(s(20, lt - 40, w - 20, lt + 40), 180, 360, fill=(220, 240, 255, 255), outline=(110, 160, 200, 255), width=5 * k)
            d.line(s(40, lt - 6, 70, lt - 16), fill=(255, 255, 255, 255), width=6 * k)
        elif level > 0:
            top = h - 20 - int((h - 40) * level)
            d.rectangle(s(20, top, w - 20, h - 22), fill=(140, 205, 240, 200))
        # dashed line
        for x in range(20, w - 20, 26):
            d.line(s(x, lt, x + 14, lt), fill=(230, 60, 60, 255), width=5 * k)
        d.polygon(s(10, 10, w - 10, 10, w - 22, h - 10, 22, h - 10), outline=(90, 120, 140, 255), width=6 * k)
    return sprite(w, h, fn)

def freezer():
    def fn(d, s, k):
        RR(d, s, (10, 10, 520, 760), 30, (235, 245, 252, 255), 8)
        d.line(s(10, 300, 520, 300), fill=INK, width=8 * k)
        RR(d, s, (440, 120, 470, 230), 10, (170, 180, 190, 255), 5)
        RR(d, s, (440, 360, 470, 520), 10, (170, 180, 190, 255), 5)
        for (x, y) in [(120, 120), (220, 190), (320, 110)]:
            for a in range(3):
                ang = a * math.pi / 3
                d.line(s(x - 30 * math.cos(ang), y - 30 * math.sin(ang), x + 30 * math.cos(ang), y + 30 * math.sin(ang)), fill=(110, 180, 230, 255), width=6 * k)
    return sprite(530, 770, fn)

def molecule(r=34):
    def fn(d, s, k):
        E(d, s, (4, 4, 4 + 2 * r, 4 + 2 * r), (79, 160, 230, 255), 4)
        E(d, s, (2 * r - 6, -2 + 6, 2 * r + 18, 22 + 6), (255, 255, 255, 255), 4)
        E(d, s, (-2 + 6, -2 + 6, 22 + 6, 22 + 6), (255, 255, 255, 255), 4)
    return sprite(2 * r + 24, 2 * r + 24, fn)

def fish(color=(255, 150, 60)):
    def fn(d, s, k):
        d.polygon(s(10, 20, 10, 80, 50, 50), fill=color + (255,), outline=INK, width=5 * k)
        E(d, s, (36, 14, 150, 86), color + (255,), 5)
        E(d, s, (112, 34, 128, 50), INK, 0, None)
    return sprite(160, 100, fn)
