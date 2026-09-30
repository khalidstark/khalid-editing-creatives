#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""29_spotlight.py — إضاءة انتقائية: شي يضوي ثانية أو ثنتين والباقي يغمق (+ تدرّج لوني مؤقت).

    python3 29_spotlight.py <work> build [--fast]    # يبني طبقات القص لكل نافذة بـspotlight.json + معاينة
    python3 29_spotlight.py <work> off               # يلغي كل شي

⛔ **بطلبه الصريح بس** (القاعدة ٤) — ما نلمس صورته من نفسنا.

<work>/spotlight.json (تكتبه أنت):
{"windows": [
  {"a": 12.3, "b": 14.1,                 ← من-إلى بثواني الفيديو المقصوص (نفس caps.json) — ١–٣ ثواني أقوى
   "target": "person",                   ← person (هو) · object (شي بالكادر — ماك) · area (بقعة تحددها) · frame (الكادر كله)
   "point": [0.62, 0.71],                ← object بس: نقطة على الشي بأول فريم (0…1 من العرض/الطول بالفيديو المقصوص)
   "area": {"x":0.5,"y":0.42,"rx":0.22,"ry":0.14},  ← area بس: مركز البقعة ونصف قطريها (نسب)
   "to":   {"x":0.5,"y":0.60,"rx":0.18,"ry":0.12},  ← area اختياري: البقعة تمشي لهنا خلال النافذة
   "dim": 0.55,                          ← كم يغمق الباقي (0 = ولا شي · 1 = أسود) — frame: 0.25
   "desat": 0.3,                         ← كم يبهت لون الباقي (1 = أبيض وأسود) — frame: 0.6
   "contrast": 1.0,                      ← تباين الباقي (1 = كما هو)
   "lift": 0.12,                         ← كم يضوي الهدف نفسه
   "glow": "acc",                        ← لون التوهّج: مفتاح من ثيمه (acc · sky · warm…) أو "#hex" · null = بلا توهّج
   "glowSize": 26, "glowAlpha": 0.85,    ← حجم التوهّج وقوته
   "pulse": false,                       ← التوهّج ينبض مرة بالنص
   "in": 0.25, "out": 0.35}              ← دخول وخروج ناعم (0 = قطع حاد، مثل ضربة ضوء)
]}

الناتج: <work>/spot/ (s<N>.webm طبقة شفافة · preview_s<N>.jpg) + spotlight.out.json — ينسخها 04b_remotion.sh.
الطبقة تُبنى من cutz.mp4 نفسه فتنطبق على الفيديو فريم بفريم، وتُرسم داخل نافذة الفيديو بنفس زومه.
"""
import sys, os, json, subprocess, shutil, platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths

if len(sys.argv) < 3: print(__doc__); sys.exit(2)
W = os.path.abspath(sys.argv[1]); CMD = sys.argv[2]
P = lambda *n: os.path.join(W, *n)
K = os.path.dirname(os.path.abspath(__file__))
OUT = P("spot"); FPS = 30
TARGETS = ("person", "object", "area", "frame")

def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)

if CMD == "off":
    for f in ("spotlight.json", "spotlight.out.json"):
        if os.path.exists(P(f)): os.remove(P(f))
    shutil.rmtree(OUT, ignore_errors=True); print("انلغت الإضاءة الانتقائية."); sys.exit(0)
if CMD != "build": sys.exit("الأوامر: build · off")

try:
    import numpy as np, cv2
except ImportError:
    sys.exit("⛔ ناقص numpy أو opencv — ثبّتها: python3 -m pip install numpy opencv-python")

if not os.path.exists(P("spotlight.json")): sys.exit("⛔ اكتب spotlight.json أول (الصيغة بأعلى الملف)")
if not os.path.exists(P("cutz.mp4")): sys.exit("⛔ ما فيه cutz.mp4 — شغّل 03_cut_zoom.py أول")
cfg = json.load(open(P("spotlight.json"), encoding="utf-8"))
WINS = cfg.get("windows", [])

# ── تحقّق قبل أي شغل ثقيل ──
errs = []
for n, w in enumerate(WINS, 1):
    tg = w.get("target", "person")
    if tg not in TARGETS: errs.append(f"النافذة {n}: target «{tg}» غير معروف — {' · '.join(TARGETS)}")
    if float(w["b"]) - float(w["a"]) < 0.3: errs.append(f"النافذة {n}: أقصر من ٠٫٣ ث")
    if tg == "object" and not (isinstance(w.get("point"), list) and len(w["point"]) == 2):
        errs.append(f"النافذة {n}: object يحتاج \"point\": [x, y]")
    if tg == "object" and platform.system() != "Darwin":
        errs.append(f"النافذة {n}: object يشتغل بالماك بس (Vision) — استعمل area بدله")
    if tg == "area" and not all(k in (w.get("area") or {}) for k in ("x", "y", "rx", "ry")):
        errs.append(f"النافذة {n}: area يحتاج \"area\": {{x, y, rx, ry}}")
s = sorted((float(w["a"]), float(w["b"]), n) for n, w in enumerate(WINS, 1))
for (a1, b1, n1), (a2, b2, n2) in zip(s, s[1:]):
    if a2 < b1: errs.append(f"النافذتان {n1} و{n2} متداخلتان — نافذة وحدة بكل لحظة")
if errs: print("⛔ spotlight.json:"); [print("  ", e) for e in errs]; sys.exit(2)
# نوافذ قصّ الشخص (27) تخفي الفيديو الأصلي — الإضاءة ما تنرسم فوقها
if os.path.exists(P("person.out.json")):
    for pw in json.load(open(P("person.out.json"))).get("windows", []):
        for n, w in enumerate(WINS, 1):
            if float(w["a"]) < pw["b"] and pw["a"] < float(w["b"]):
                print(f"⚠️ النافذة {n} تتداخل مع نافذة قصّ الشخص {pw['a']:.2f}→{pw['b']:.2f} — ما راح تبان هناك")

def tool(name, swift):
    b = _paths.data("tools", name)
    if not os.path.exists(b) or os.path.getmtime(b) < os.path.getmtime(os.path.join(K, swift)):
        _paths.ensure()
        r = subprocess.run(["swiftc", "-O", "-o", b, os.path.join(K, swift)], capture_output=True)
        if r.returncode: sys.exit("⛔ أدوات Xcode ناقصة — شغّل 00_setup.sh --install\n" + r.stderr.decode()[-400:])
    return [b]
def personmask_cmd():
    return tool("personmask", "personmask.swift") if platform.system() == "Darwin" \
        else [sys.executable, os.path.join(K, "personmask.py")]

def hexcol(g, th):
    g = th.get(g or "acc", th.get("acc", "#FFD400")) if not (g or "").startswith("#") else g
    g = (g or "#FFD400").lstrip("#"); return np.array([int(g[4:6], 16), int(g[2:4], 16), int(g[0:2], 16)], np.float32)

def preview(img, alpha, w, th):
    """تقريب للناتج بالبايثون: الباقي مغمّق ومبهّت، الهدف مضوّي، والتوهّج حوله — تشوفه قبل الرندر"""
    f = img.astype(np.float32)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
    ds = w.get("desat", 0.3); rest = (f * (1 - ds) + gray * ds) * (1 - w.get("dim", 0.55))
    tgt = np.clip(f * (1 + w.get("lift", 0.12)), 0, 255)
    a = alpha[..., None]; o = rest * (1 - a) + tgt * a
    if w.get("glow", "acc") is not None:
        G = w.get("glowSize", 26)
        halo = np.clip(cv2.GaussianBlur(alpha, (0, 0), max(1, G * 0.6)) * 1.8 - alpha, 0, 1)[..., None] * w.get("glowAlpha", 0.85)
        o = o + (255 - o) * halo * (hexcol(w.get("glow"), th) / 255)
    return np.clip(o, 0, 255).astype(np.uint8)

th = json.load(open(P("theme.json"))) if os.path.exists(P("theme.json")) else {}
quality = "balanced" if "--fast" in sys.argv else "accurate"
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.startswith(("s", "preview_s", "_")): shutil.rmtree(os.path.join(OUT, f), ignore_errors=True) \
        if os.path.isdir(os.path.join(OUT, f)) else os.remove(os.path.join(OUT, f))
out = {"windows": []}
KEYS = ("a", "b", "target", "area", "to", "dim", "desat", "contrast", "lift", "glow", "glowSize", "glowAlpha", "pulse", "in", "out")

for n, w in enumerate(WINS, 1):
    a, b, tg = float(w["a"]), float(w["b"]), w.get("target", "person")
    ow = {k: w[k] for k in KEYS if k in w}; ow["target"] = tg
    if tg in ("area", "frame"):                       # بلا قص — كله بريموشن
        out["windows"].append(ow); print(f"✅ النافذة {n}: {tg} {a:.2f}→{b:.2f} (بلا قص)"); continue
    fd, md, rg = (os.path.join(OUT, f"_s{n}{x}") for x in ("", "m", "a"))
    for d in (fd, md, rg): shutil.rmtree(d, ignore_errors=True)
    os.makedirs(fd)
    # نفس فريمات video.mp4 بالضبط: cutz.mp4 ثابت ٣٠ فريم، والنافذة تبدأ بـround(a·30) مثل Sequence بريموشن
    f0, nf = round(a * FPS), max(1, round((b - a) * FPS))
    ff("-i", P("cutz.mp4"), "-vf", f"trim=start_frame={f0}:end_frame={f0 + nf},setpts=PTS-STARTPTS",
       "-q:v", "2", os.path.join(fd, "%05d.jpg"))
    frames = sorted(os.listdir(fd))
    if not frames: sys.exit(f"⛔ النافذة {n}: ما طلع ولا فريم — {a:.2f} بعد نهاية الفيديو؟")
    print(f"✂️ النافذة {n}: {tg} {a:.2f}→{b:.2f} · {len(frames)} فريم · أقصّ…")
    if tg == "person":
        subprocess.run(personmask_cmd() + [fd, md, quality, "2.0"], check=True, capture_output=True)
    else:
        r = subprocess.run(tool("objectmask", "objectmask.swift") + [fd, md, str(w["point"][0]), str(w["point"][1])],
                           capture_output=True, text=True)
        print("   ", r.stdout.strip())
        if r.returncode: sys.exit(f"⛔ النافذة {n}: ما لقيت شي عند النقطة {w['point']} — افتح spot/_s{n}/00001.jpg وحدّد النقطة من جديد، أو استعمل area")
    os.makedirs(rg); cover = []
    for f in frames:
        img = cv2.imread(os.path.join(fd, f))
        m = cv2.imread(os.path.join(md, f[:-4] + ".png"), cv2.IMREAD_GRAYSCALE)
        m = np.zeros(img.shape[:2], np.uint8) if m is None else cv2.resize(m, (img.shape[1], img.shape[0]))
        cover.append(float((m > 127).mean()))
        cv2.imwrite(os.path.join(rg, f[:-4] + ".png"), np.dstack([img, m]))
    # VP9 بقناة شفافية — ريموشن يقرأها بـ<OffthreadVideo transparent>
    vid = f"s{n}.webm"
    ff("-framerate", str(FPS), "-i", os.path.join(rg, "%05d.png"), "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
       "-crf", "14", "-b:v", "0", "-row-mt", "1", "-auto-alt-ref", "0", os.path.join(OUT, vid))
    mid = frames[len(frames) // 2]
    al = cv2.imread(os.path.join(rg, mid[:-4] + ".png"), cv2.IMREAD_UNCHANGED)[..., 3].astype(np.float32) / 255
    pv = preview(cv2.imread(os.path.join(fd, mid)), al, w, th)
    cv2.imwrite(os.path.join(OUT, f"preview_s{n}.jpg"), cv2.resize(pv, (pv.shape[1] // 2, pv.shape[0] // 2)))
    for d in (fd, md, rg): shutil.rmtree(d, ignore_errors=True)
    c = float(np.median(cover))
    if c < 0.002: print(f"   ⚠️ الهدف شبه فاضي ({c:.1%} من الكادر) — افحص المعاينة")
    if c > 0.6: print(f"   ⚠️ الهدف ماخذ {c:.0%} من الكادر — ما راح يبان فرق؛ جرّب area أو frame")
    ow["file"] = vid; out["windows"].append(ow)
    print(f"   ✅ {vid} · المعاينة: spot/preview_s{n}.jpg ← افتحها: الحواف · الأصابع · التوهّج")

json.dump(out, open(P("spotlight.out.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nالتالي: 04b_remotion.sh <work> render-test <out> <فريمات النافذة> قبل الرندر الكامل.")
