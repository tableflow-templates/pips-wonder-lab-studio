import sys, os, math, json, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw
import art
from art import W, H, font
from script import SCENES, timeline

FPS = 30
COL = {"MIA": (230, 120, 30), "LEO": (60, 150, 64), "PIP": (40, 140, 210), "ALL": (170, 80, 200)}
NAME = {"MIA": "MIA", "LEO": "LEO", "PIP": "PIP", "ALL": "ALL"}
POS = {"MIA": (180, 300), "LEO": (1340, 300), "PIP": (1020, 330)}  # sprite top-left
GLASS_X, TABLE_Y = 760, 795

BG = art.lab_bg()
TABLE = BG.crop((0, 785, W, H)).convert("RGBA")
BULB = {False: art.bulb(False), True: art.bulb(True)}
GLASS = art.glass()
ICE = art.ice_cube()
PEB = art.pebble()

def ease(x):
    x = max(0, min(1, x)); return x * x * (3 - 2 * x)

@lru_cache(None)
def caption(who, text):
    f = font(46)
    words = text.split(); lines = []; cur = ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if f.getlength(t) > 1380: lines.append(cur); cur = w_
        else: cur = t
    lines.append(cur)
    bw = int(max(f.getlength(l) for l in lines)) + 120
    bh = 60 * len(lines) + 70
    col = COL[who]
    def fn(d, s, k):
        art.RR(d, s, (4, 40, bw - 4, 40 + bh), 28, (255, 255, 255, 240), 5, col + (255,))
        nw = int(font(34).getlength(NAME[who])) + 50
        art.RR(d, s, (30, 4, 30 + nw, 64), 22, col + (255,), 0, None)
        d.text(s(55, 14), NAME[who], fill=(255, 255, 255, 255), font=font(34 * k))
        for i, l in enumerate(lines):
            d.text(s(60, 80 + i * 60), l, fill=(40, 30, 25, 255), font=font(46 * k))
    return art.sprite(bw, bh + 46, fn)

@lru_cache(None)
def banner(text, size=96, col=(214, 82, 43), sub=None):
    f = font(size)
    bw = int(f.getlength(text)) + 140
    sw = int(font(44).getlength(sub)) + 140 if sub else 0
    bw = max(bw, sw)
    bh = size + 90 + (64 if sub else 0)
    def fn(d, s, k):
        art.RR(d, s, (6, 6, bw - 6, bh - 6), 40, (255, 255, 255, 250), 8, col + (255,))
        tw = font(size).getlength(text)
        d.text(s((bw - tw) / 2, 40), text, fill=col + (255,), font=font(size * k))
        if sub:
            sw_ = font(44).getlength(sub)
            d.text(s((bw - sw_) / 2, size + 60), sub, fill=(60, 50, 45, 255), font=font(44 * k))
    return art.sprite(bw, bh, fn)

def paste_center(img, spr, cx, cy, scale=1.0):
    if scale <= 0.01: return
    if abs(scale - 1) > 0.01:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    img.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)))

def speaking(lines, t):
    for (a, b, who, text, expr) in lines:
        if a <= t < b: return who, text, expr, t - a
    return None, None, None, 0

def draw_chars(img, t, lines, force_expr=None, only=None):
    who, _, expr, lt = speaking(lines, t)
    for i, name in enumerate(["MIA", "PIP", "LEO"]):
        if only and name not in only: continue
        talking = (who == name or who == "ALL")
        ph = i * 1.3
        blink = ((t + ph) % 3.7) < 0.13
        mouth = [1, 2, 1, 0][int(lt * 9) % 4] if talking else 0
        e = force_expr or (expr if talking else None)
        if name == "PIP":
            spr = art.char("PIP", "closed" if blink else "open", 1 if (talking and int(lt * 6) % 2 == 0) else 0, e)
            dy = math.sin(t * 1.7 + ph) * 14
        else:
            spr = art.char(name, "closed" if blink else "open", mouth, e)
            dy = math.sin(t * 2 + ph) * 4 - (abs(math.sin(lt * 7)) * 8 if talking else 0)
        x, y = POS[name]
        img.alpha_composite(spr, (x, int(y + dy)))
    img.alpha_composite(TABLE, (0, 785))

def draw_caption(img, t, lines):
    who, text, expr, lt = speaking(lines, t)
    if not who: return
    c = caption(who, text)
    a = min(1, lt / 0.15)
    y = 1060 - c.height + int((1 - a) * 30)
    img.alpha_composite(c, ((W - c.width) // 2, y))

def lab(t, bulb_on=False):
    img = BG.convert("RGBA")
    img.alpha_composite(BULB[bulb_on], (960 - 160, 50))
    return img

def water_overlay(img, x0, x1, ytop, ybot):
    ov = Image.new("RGBA", (x1 - x0, max(1, ybot - ytop)), (140, 205, 240, 120))
    img.alpha_composite(ov, (x0, ytop))

def glass_with(img, cx, objs):
    """objs: list of (sprite, y_top, submerge) drawn inside glass at center x."""
    gx, gy = cx - GLASS.width // 2, TABLE_Y - GLASS.height + 10
    img.alpha_composite(GLASS, (gx, gy))
    surf = gy + 119
    for spr, ytop in objs:
        img.alpha_composite(spr, (cx - spr.width // 2, int(ytop)))
        if ytop + spr.height > surf:
            water_overlay(img, cx - spr.width // 2, cx + spr.width // 2, int(max(ytop, surf)), int(ytop + spr.height))
    return surf

def floating_ice_y(surf, t_since):
    """ice top y; drops at t_since=0..0.6 then bobs."""
    rest = surf - 22
    if t_since < 0: return None
    if t_since < 0.6:
        return -120 + (rest + 50 + 120) * (t_since / 0.6) ** 2
    u = t_since - 0.6
    return rest + 50 * math.exp(-3 * u) * math.cos(u * 7) + math.sin(t_since * 2) * 2

EVENTS = []

def ev(kind, t):
    EVENTS.append((kind, round(t, 3)))

# ---------------- scenes ----------------
def scene1(t, L, T, D):
    img = lab(t)
    surf = TABLE_Y - GLASS.height + 10 + 119
    y = floating_ice_y(surf, t - T["drop"])
    draw_chars(img, t, L)
    glass_with(img, GLASS_X, [(ICE, y)] if y is not None else [])
    if t >= T["title"]:
        u = t - T["title"]
        sc = ease(u / 0.5) * (1 + 0.08 * math.sin(min(u, 1.5) * 6) * math.exp(-2 * u))
        paste_center(img, banner("Why does ice float?", 110), W / 2, 330, sc)
    draw_caption(img, t, L)
    return img

def scene2(t, L, T, D):
    img = lab(t)
    surf = TABLE_Y - GLASS.height + 10 + 119
    draw_chars(img, t, L)
    glass_with(img, GLASS_X, [(ICE, floating_ice_y(surf, 10 + t))])
    if L[0][0] <= t < L[2][0]:
        a = ease((t - L[0][0]) / 0.4)
        paste_center(img, thought(), 1330, 230, a)
        paste_center(img, BALLOON, 1340, 200, a * 0.9)
    if L[1][0] <= t < L[3][0]:
        a = ease((t - L[1][0]) / 0.4)
        paste_center(img, thought(), 1000, 200, a)
        paste_center(img, SCARED, 1010, 180, a * 0.85)
    draw_caption(img, t, L)
    return img

@lru_cache(None)
def thought(): return art.thought()
BALLOON = art.balloon_icon(); SCARED = art.scared_ice()
GROWNUP = art.badge("Ask a grown-up")

def label(img, text, cx, y, col=(255, 255, 255), stroke=True):
    f = font(40)
    d = ImageDraw.Draw(img)
    tw = f.getlength(text)
    if stroke:
        d.text((cx - tw / 2, y), text, fill=col, font=f, stroke_width=4, stroke_fill=(80, 50, 30))
    else:
        d.text((cx - tw / 2, y), text, fill=col, font=f)

def scene3(t, L, T, D):
    img = lab(t)
    draw_chars(img, t, L)
    surf = TABLE_Y - GLASS.height + 10 + 119
    u = t - T["drop1"]
    iy = floating_ice_y(surf, u) if u >= 0 else None
    glass_with(img, 740, [(ICE, iy)] if iy is not None else [])
    if u >= 0:
        bottom = TABLE_Y - 20 - PEB.height
        if u < 0.6: py = -120 + (surf + 120) * (u / 0.6) ** 2
        else: py = surf + (bottom - surf) * ease((u - 0.6) / 2.0)
        glass_with(img, 1000, [(PEB, py)])
    else:
        glass_with(img, 1000, [])
    label(img, "ICE", 740, 535); label(img, "PEBBLE", 1000, 535)
    img.alpha_composite(GROWNUP, (40, 30))
    draw_caption(img, t, L)
    return img

CUP_W = {}
@lru_cache(None)
def cupspr(level_q, ice): return art.cup(level_q / 100, ice)
FREEZER = art.freezer()

def scene4(t, L, T, D):
    if T["freezer"] <= t < T["back"]:
        img = Image.new("RGBA", (W, H), (200, 230, 250, 255))
        u = t - T["freezer"]
        paste_center(img, FREEZER, 700, 540)
        # clock
        d = ImageDraw.Draw(img)
        cx, cy, r = 1300, 420, 170
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255), outline=(59, 42, 32), width=12)
        for i in range(12):
            a = i * math.pi / 6
            d.line((cx + (r - 30) * math.sin(a), cy - (r - 30) * math.cos(a), cx + (r - 12) * math.sin(a), cy - (r - 12) * math.cos(a)), fill=(59, 42, 32), width=8)
        a1 = u * 2 * math.pi * 1.2; a2 = u * 2 * math.pi / 10
        d.line((cx, cy, cx + 130 * math.sin(a1), cy - 130 * math.cos(a1)), fill=(214, 82, 43), width=10)
        d.line((cx, cy, cx + 85 * math.sin(a2), cy - 85 * math.cos(a2)), fill=(59, 42, 32), width=14)
        d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=(59, 42, 32))
        paste_center(img, banner("Many hours later...", 70, (40, 140, 210)), 1300, 760, ease(u / 0.4))
        img.alpha_composite(GROWNUP, (40, 30))
        draw_caption(img, t, L)
        return img
    img = lab(t)
    draw_chars(img, t, L)
    if t < T["freezer"]:
        lv = 0 if t < T["fill"] else ease((t - T["fill"]) / 1.4) * 62
        c = cupspr(int(lv), False)
    else:
        c = cupspr(62, True)
    img.alpha_composite(c, (GLASS_X - c.width // 2, TABLE_Y - c.height + 10))
    if t >= T["back"] + 0.8 and t < T.get("density", 1e9):
        a = ease((t - T["back"] - 0.8) / 0.4)
        paste_center(img, banner("More space!", 54, (230, 60, 60)), GLASS_X, 400, a)
    if t >= T["density"]:
        a = ease((t - T["density"]) / 0.5)
        paste_center(img, banner("DENSITY", 110, (40, 140, 210), "how tightly stuff is packed"), W / 2, 230, a)
    img.alpha_composite(GROWNUP, (40, 30))
    draw_caption(img, t, L)
    return img

MOL = art.molecule()
import random
random.seed(4)
LIQ = []
for gx in range(6):
    for gy in range(6):
        LIQ.append((250 + gx * 92 + random.uniform(-14, 14), 290 + gy * 88 + random.uniform(-14, 14), random.uniform(0, 6.28)))
RING = []
_r = 118
for row in range(-3, 4):
    for col in range(-3, 4):
        hx = 1440 + col * _r * 3 ** 0.5 + (_r * 3 ** 0.5 / 2 if row % 2 else 0)
        hy = 540 + row * _r * 1.5
        for k in range(6):
            a = k * math.pi / 3 + math.pi / 6
            RING.append((hx + _r * math.cos(a), hy + _r * math.sin(a)))
RING = [(x, y) for (x, y) in RING if 1080 < x < 1800 and 250 < y < 820]
RING = list({(round(x), round(y)) for x, y in RING})

def scene5(t, L, T, D):
    if t < T["lab"]:
        img = Image.new("RGBA", (W, H), (236, 246, 255, 255))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((60, 150, 900, 860), 40, fill=(255, 255, 255), outline=(79, 160, 230), width=8)
        d.rounded_rectangle((1020, 150, 1860, 860), 40, fill=(255, 255, 255), outline=(150, 200, 240), width=8)
        label(img, "LIQUID WATER", 480, 180, (40, 100, 170), False)
        for (x, y, ph) in LIQ:
            paste_center(img, MOL, x + 6 * math.sin(t * 5 + ph), y + 6 * math.cos(t * 4.3 + ph * 1.7))
        if t >= T["ice"]:
            a = ease((t - T["ice"]) / 0.8)
            label(img, "ICE", 1440, 180, (40, 100, 170), False)
            # hand-holding bonds
            for i, (x, y) in enumerate(RING):
                for (x2, y2) in RING[i + 1:]:
                    if abs(math.hypot(x - x2, y - y2) - _r) < 5:
                        d.line((x, y, x2, y2), fill=(110, 170, 225), width=10)
            for (x, y) in RING:
                sw = 2 * math.sin(t * 3 + x)
                paste_center(img, MOL, x, 540 + (y - 540) * a + sw, a)
        draw_caption(img, t, L)
        return img
    on = t >= T["bulb"]
    img = lab(t, on)
    surf = TABLE_Y - GLASS.height + 10 + 119
    draw_chars(img, t, L, "surprised" if T["bulb"] <= t < T["bulb"] + 2.4 else None)
    glass_with(img, GLASS_X, [(ICE, floating_ice_y(surf, 10 + t))])
    if on and t < T["bulb"] + 2.6:
        paste_center(img, banner("AHA!", 120, (230, 150, 20)), W / 2, 420, ease((t - T["bulb"]) / 0.3))
    draw_caption(img, t, L)
    return img

FISH = art.fish(); FISH2 = art.fish((255, 200, 70))

def scene6(t, L, T, D):
    if T["lake"] <= t < T["end"]:
        u = t - T["lake"]
        img = Image.new("RGBA", (W, H), (180, 225, 250, 255))
        d = ImageDraw.Draw(img)
        d.rectangle((0, 330, W, H), fill=(60, 140, 200))
        d.rectangle((0, 300, W, 400), fill=(225, 243, 255), outline=(150, 200, 235), width=6)
        for x in range(60, W, 260):
            d.line((x, 320, x + 60, 340), fill=(255, 255, 255), width=6)
        label(img, "ICE (like a lid)", 360, 230, (30, 80, 140), False)
        label(img, "WATER", 1500, 470, (255, 255, 255))
        for (sp, y0, spd, ph) in [(FISH, 560, 140, 0), (FISH2, 700, 100, 3), (FISH, 820, 170, 7)]:
            x = (u * spd + ph * 250) % (W + 300) - 150
            img.alpha_composite(sp, (int(x), int(y0 + 12 * math.sin(u * 2 + ph))))
        d.rectangle((0, 1000, W, H), fill=(120, 100, 70))
        draw_caption(img, t, L)
        return img
    img = lab(t, t >= T["end"])
    surf = TABLE_Y - GLASS.height + 10 + 119
    draw_chars(img, t, L)
    glass_with(img, GLASS_X, [(ICE, floating_ice_y(surf, 10 + t))])
    if t >= T["end"]:
        last = L[-1]
        if t >= last[0]:
            paste_center(img, banner("Mission complete!", 100, (214, 82, 43), "Pip's Wonder Lab"), W / 2, 300, ease((t - last[0]) / 0.5))
        else:
            paste_center(img, banner("What do you wonder about?", 70, (40, 140, 210)), W / 2, 300, ease((t - T["end"]) / 0.4))
    draw_caption(img, t, L)
    return img

FUNCS = [scene1, scene2, scene3, scene4, scene5, scene6]

def frame(i, t):
    L, T, D = timeline(SCENES[i])
    img = FUNCS[i](t, L, T, D)
    if t < 0.35:
        a = 1 - t / 0.35
        img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), a)
    if i == 5 and t > D - 0.5:
        a = (t - (D - 0.5)) / 0.5
        img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), min(1, a))
    return img.convert("RGB")

def render(i, out):
    L, T, D = timeline(SCENES[i])
    n = int(round(D * FPS))
    tmp = out.replace(".mp4", ".part.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for f in range(n):
        p.stdin.write(frame(i, f / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, out)

if __name__ == "__main__":
    if sys.argv[1] == "still":
        i, t = int(sys.argv[2]), float(sys.argv[3])
        frame(i, t).save(sys.argv[4])
    else:
        for i in map(int, sys.argv[2:]):
            render(i, f"out/scene{i + 1}.mp4")
