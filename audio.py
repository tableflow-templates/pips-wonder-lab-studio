import numpy as np
from scipy.io import wavfile
from script import SCENES, timeline

SR = 44100
rng = np.random.default_rng(7)

durs, offs, Ls, Ts = [], [], [], []
o = 0
for sc in SCENES:
    L, T, D = timeline(sc)
    n = round(D * 30) / 30
    offs.append(o); durs.append(n); Ls.append(L); Ts.append(T); o += n
TOTAL = o
N = int(TOTAL * SR) + SR
mix = np.zeros(N)

def add(sig, t, gain=1.0):
    i = int(t * SR)
    if i >= N: return
    j = min(N, i + len(sig))
    mix[i:j] += sig[: j - i] * gain

def env(n, a=0.005, r=None):
    e = np.ones(n)
    na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if r: nr = min(n, int(r * SR)); e[-nr:] *= np.linspace(1, 0, nr)
    return e

def tone(f, d, kind="sine", decay=6):
    t = np.arange(int(d * SR)) / SR
    if kind == "sine": s = np.sin(2 * np.pi * f * t)
    else: s = np.sign(np.sin(2 * np.pi * f * t)) * 0.4
    return s * np.exp(-decay * t) * env(len(t), 0.003)

def pluck(f, d=1.2, bright=0.5):
    n = int(d * SR); p = int(SR / f)
    buf = rng.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * (bright * buf[i % p] + (1 - bright) * buf[(i + 1) % p]) if False else 0.4985 * (buf[i % p] + buf[(i + 1) % p])
    return out * env(n, 0.002, 0.05)

# ---- Karplus-Strong vectorised by blocks ----
def ks(f, d=1.4):
    n = int(d * SR); p = max(2, int(round(SR / f)))
    reps = n // p + 2
    buf = rng.uniform(-1, 1, p)
    out = []
    for _ in range(reps):
        out.append(buf.copy())
        buf = 0.497 * (buf + np.roll(buf, -1))
    return np.concatenate(out)[:n] * env(n, 0.002, 0.08)

NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
chords = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]
bass = [48, 43, 45, 41]
bpm = 96; beat = 60 / bpm; bar = 4 * beat
music = np.zeros(N)
cache = {}
def note(m, d):
    k = (m, d)
    if k not in cache: cache[k] = ks(NOTE(m), d)
    return cache[k]
t = 0.0; b = 0
pattern = [0, 1, 2, 3, 2, 1, 2, 3]
mel = [76, 74, 72, 74, 76, 76, 76, None, 74, 74, 74, None, 76, 79, 79, None]
while t < TOTAL:
    c = chords[b % 4]
    for k, idx in enumerate(pattern):
        s = note(c[idx], 1.0)
        i = int((t + k * beat / 2) * SR)
        if i < N: music[i:i + len(s)] += s[: max(0, min(len(s), N - i))] * 0.22
    bs = tone(NOTE(bass[b % 4]), bar, "sine", 1.2) * 0.35
    i = int(t * SR); music[i:i + len(bs)] += bs[: max(0, min(len(bs), N - i))]
    if (b // 8) % 2 == 1:  # light glockenspiel melody every other section
        for k in range(4):
            m = mel[(b * 4 + k) % len(mel)]
            if m:
                s = tone(NOTE(m + 12), 0.8, "sine", 5) * 0.12
                i = int((t + k * beat) * SR); music[i:i + len(s)] += s[: max(0, min(len(s), N - i))]
    t += bar; b += 1
fade = np.ones(N); fe = int((TOTAL - 3) * SR); fade[fe:] = np.linspace(1, 0, N - fe) if N > fe else 1
music *= fade
mix += music * 0.55

# ---- SFX ----
def plop(f0=500, f1=120, d=0.25):
    tt = np.arange(int(d * SR)) / SR
    f = f0 * (f1 / f0) ** (tt / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-12 * tt)

def splash(d=0.5):
    n = int(d * SR); s = rng.normal(0, 1, n)
    s = np.convolve(s, np.ones(8) / 8, "same")
    return s * np.exp(-np.arange(n) / SR * 9) * 0.5

def whoosh(d=0.7):
    n = int(d * SR); s = rng.normal(0, 1, n)
    k = np.convolve(s, np.ones(30) / 30, "same")
    return k * np.sin(np.linspace(0, np.pi, n)) * 1.2

def beep():
    return np.concatenate([tone(880, 0.09, "square", 3), np.zeros(int(0.03 * SR)), tone(1320, 0.11, "square", 3)]) * 0.5

def ding(f=1568):
    return (tone(f, 1.6, "sine", 2.2) + 0.4 * tone(f * 2, 1.6, "sine", 3)) * 0.6

def pop():
    return plop(900, 300, 0.12) * 0.8

def chime(base=72):
    out = np.zeros(int(2.4 * SR))
    for k, m in enumerate([0, 4, 7, 12]):
        s = tone(NOTE(base + m + 12), 1.6, "sine", 2.5) * 0.45
        i = int(k * 0.14 * SR); out[i:i + len(s)] += s
    return out

def pour(d=1.4):
    n = int(d * SR); s = rng.normal(0, 1, n)
    s = np.convolve(s, np.ones(4) / 4, "same") * (0.6 + 0.4 * np.sin(np.arange(n) / SR * 2 * np.pi * 9))
    return s * env(n, 0.1, 0.3) * 0.25

def bubbles():
    out = np.zeros(int(1.5 * SR))
    for k in range(6):
        s = plop(rng.uniform(600, 1100), 300, 0.08) * 0.35
        i = int(rng.uniform(0, 1.3) * SR); out[i:i + len(s)] += s
    return out

for si in range(6):
    o, L, T = offs[si], Ls[si], Ts[si]
    if si > 0: add(whoosh(0.6), o, 0.25)
    for (a, _, who, _, _) in L:
        if who == "PIP": add(beep(), o + a, 0.35)
    if si == 0:
        add(plop(), o + T["drop"] + 0.6, 0.8); add(splash(), o + T["drop"] + 0.6, 0.5)
        add(whoosh(), o + T["title"], 0.6); add(chime(), o + T["title"] + 0.2, 0.7)
    if si == 1:
        add(pop(), o + L[0][0], 0.7); add(pop(), o + L[1][0], 0.7)
    if si == 2:
        add(plop(), o + T["drop1"] + 0.6, 0.8); add(plop(300, 80, 0.35), o + T["drop1"] + 0.62, 0.8)
        add(splash(), o + T["drop1"] + 0.6, 0.5)
    if si == 3:
        add(pour(), o + T["fill"], 1.0); add(whoosh(), o + T["freezer"], 0.6)
        add(ding(1318), o + T["back"], 0.6); add(pop(), o + T["density"], 0.8)
    if si == 4:
        add(chime(79), o + T["ice"], 0.5); add(ding(), o + T["bulb"], 0.9); add(chime(), o + T["bulb"] + 0.1, 0.5)
    if si == 5:
        add(bubbles(), o + T["lake"] + 0.3, 0.8)
        add(chime(72), o + Ls[5][-1][0], 0.8); add(chime(79), o + Ls[5][-1][0] + 0.5, 0.6)

mix = mix[: int(TOTAL * SR)]
mix /= max(1e-9, np.abs(mix).max()) / 0.85
wavfile.write("out/soundtrack.wav", SR, (mix * 32767).astype(np.int16))
print("total", TOTAL)
