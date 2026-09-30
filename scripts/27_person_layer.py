#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""27_person_layer.py — قصّ الشخص من الفيديو: خلفية بديلة · تصغير · تكبير · تحريك.

    python3 27_person_layer.py <work> plate <فيديو الغرفة الفاضية>   # يجهّز لقطة الغرفة ويفحص ثبات الكاميرا
    python3 27_person_layer.py <work> build [--fast]                  # يبني طبقة الشخص لكل نافذة بـperson.json
    python3 27_person_layer.py <work> off                             # يلغي كل شي

<work>/person.json (تكتبه أنت):
{
  "windows": [
    {"a": 3.2, "b": 7.5,                 ← من-إلى بثواني الفيديو المقصوص (نفس caps.json)
     "bg": "plate",                      ← plate (غرفته فاضية) · theme (خلفية هويته الحيّة) · <ملف بـassets/> صورة أو فيديو
     "scale": 0.6, "x": 0.72, "y": 1.0,  ← حجم الشخص (1 = كما صُوّر) · x مركزه أفقياً (0 يسار · 1 يمين) · y مكان قاعدته (1 = أسفل الكادر)
     "in": 0.4, "out": 0.4,              ← مدة الانتقال من/إلى لقطته الأصلية (0 = قطع حاد)
     "shadow": true}                     ← ظل تحت الشخص (للخلفيات البديلة)
  ]
}

⛔ **ليش لقطة الغرفة الفاضية؟** لما يصغر الشخص أو يتحرك، المكان اللي كان فيه لازم يبان وراه.
   بدونها: ما نقدر نخلّي غرفته الحقيقية وراه — بس خلفية بديلة (هويته · صورة · فيديو).
   وكمان تحسّن القص: الفرق بين الفريم والغرفة الفاضية يلقط الشعر والأغراض اللي بيده والكرسي.
   الشرط: **نفس مكان الكاميرا بالضبط (حامل ثابت)، نفس الزوم والإضاءة، ٥ ثواني بلا ما أحد يمر.**

الناتج: <work>/person/ (w<N>.webm طبقة شفافة · plate_w.png) + person.out.json — ينسخها 04b_remotion.sh.
الانتقال: الخلفية تتبدّل والشخص بحجمه (أول ٤٥٪ من in) ← ثم يصغر ويتحرك. والخروج بالعكس.
"""
import sys, os, json, subprocess, shutil, platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths

if len(sys.argv) < 3: print(__doc__); sys.exit(2)
W = os.path.abspath(sys.argv[1]); CMD = sys.argv[2]
P = lambda *n: os.path.join(W, *n)
K = os.path.dirname(os.path.abspath(__file__))
OUT = P("person"); FPS = 30
FW, FH = 1080, 1920

def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
def probe(f, what):
    return subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries",what,"-of","csv=p=0:s=x",f],
                          capture_output=True, text=True).stdout.strip()

try:
    import numpy as np, cv2
except ImportError:
    sys.exit("⛔ ناقص numpy أو opencv — ثبّتها: python3 -m pip install numpy opencv-python")

# ── نفس قصّ الزوم اللي يسويه 03_cut_zoom.py (عشان الطبقة والغرفة تنطبق على الفيديو بالبكسل) ──
def zoom_plan():
    th = json.load(open(P("theme.json"))) if os.path.exists(P("theme.json")) else {}
    Z = [1.00,1.08,1.00,1.06,1.00,1.12,1.04,1.14,1.00,1.08,1.00,1.05,1.10,1.00]
    anch = float(th.get("zoomAnchor", 0.30)) if isinstance(th.get("zoomAnchor"), (int, float)) else 0.30
    if th.get("noZoom"): Z = [1.00]
    keep = json.load(open(P("cut.json")))["keep"]
    off, acc = [], 0.0
    for a, b in keep: off.append(acc); acc += b - a
    return Z, anch, keep, off

def seg_at(t, off):
    i = 0
    while i + 1 < len(off) and off[i + 1] <= t + 1e-6: i += 1
    return i

def crop_like_cut(img, z, anch):
    H, Wd = img.shape[:2]
    cw, ch = int(Wd / z) // 2 * 2, int(H / z) // 2 * 2
    x, y = (Wd - cw) // 2, int((H - ch) * anch)
    return cv2.resize(img[y:y+ch, x:x+cw], (FW, FH), interpolation=cv2.INTER_LANCZOS4)

# ── قاصّ الشخص: مكتبة أبل بالماك · mediapipe بغيره (نفس اللي يستعمله 11 و12) ──
def personmask_cmd():
    if platform.system() == "Darwin":
        b = _paths.data("tools", "personmask")
        if not os.path.exists(b):
            _paths.ensure()
            r = subprocess.run(["swiftc", "-O", "-o", b, os.path.join(K, "personmask.swift")], capture_output=True)
            if r.returncode: sys.exit("⛔ أدوات Xcode ناقصة — شغّل 00_setup.sh --install")
        return [b]
    return [sys.executable, os.path.join(K, "personmask.py")]

# ══════════════════════════════════════════════════════════════════════════
if CMD == "off":
    for f in ("person.json", "person.out.json"):
        if os.path.exists(P(f)): os.remove(P(f))
    shutil.rmtree(OUT, ignore_errors=True); print("انلغى قصّ الشخص."); sys.exit(0)

# ══════════════════════════════════════════════════════════════════════════
if CMD == "plate":
    if len(sys.argv) < 4: sys.exit("الاستعمال: plate <فيديو الغرفة الفاضية>")
    src = os.path.abspath(sys.argv[3]); os.makedirs(OUT, exist_ok=True)
    dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",src],
                               capture_output=True, text=True).stdout.strip() or 0)
    if dur < 1.0: sys.exit("⛔ لقطة الغرفة أقصر من ثانية — نحتاج ٣-٥ ثواني")
    tmp = os.path.join(OUT, "_plate"); os.makedirs(tmp, exist_ok=True)
    # ١٥ فريم موزّعة ← الوسيط: يشيل التشويش وأي حركة عابرة
    ff("-i", src, "-vf", f"fps={15/dur:.4f},format=rgb24", "-frames:v", "15", os.path.join(tmp, "%02d.png"))
    fr = [cv2.imread(os.path.join(tmp, f)) for f in sorted(os.listdir(tmp))]
    med = np.median(np.stack(fr), axis=0).astype(np.uint8)
    spread = float(np.mean(np.std(np.stack(fr).astype(np.float32), axis=0)))
    shutil.rmtree(tmp)
    sw, sh = [int(v) for v in probe(P("src.mov"), "stream=width,height").split("x")[:2]]
    if (med.shape[1], med.shape[0]) != (sw, sh):
        print(f"⚠️ مقاس لقطة الغرفة {med.shape[1]}×{med.shape[0]} غير الفيديو {sw}×{sh} — كبّرتها لنفس المقاس، بس الأفضل نفس الإعدادات")
        med = cv2.resize(med, (sw, sh), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(os.path.join(OUT, "plate_src.png"), med)
    # فحص ثبات الكاميرا: قارن الغرفة بأول فريم من الفيديو بالمنطقة البعيدة عن الشخص (الحواف)
    ff("-ss", "0.5", "-i", P("src.mov"), "-frames:v", "1", "-vf", "format=rgb24", os.path.join(OUT, "_f.png"))
    f0 = cv2.imread(os.path.join(OUT, "_f.png")); os.remove(os.path.join(OUT, "_f.png"))
    m = np.zeros(f0.shape[:2], bool); bw = f0.shape[1] // 6
    m[:, :bw] = True; m[:, -bw:] = True; m[: f0.shape[0] // 8] = True
    g1, g2 = cv2.cvtColor(med, cv2.COLOR_BGR2GRAY), cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)
    shift, _ = cv2.phaseCorrelate(np.float32(g1), np.float32(g2))
    diff = float(np.mean(np.abs(g1[m].astype(float) * (np.median(g2[m]) / max(1, np.median(g1[m]))) - g2[m])))
    moved = abs(shift[0]) > 3 or abs(shift[1]) > 3
    print(f"✅ لقطة الغرفة جاهزة ({dur:.1f} ث) · اهتزاز داخلها {spread:.1f} · إزاحة عن الفيديو {shift[0]:+.1f},{shift[1]:+.1f} بكسل · فرق الحواف {diff:.1f}")
    if moved: print("⛔ الكاميرا تحرّكت بين اللقطتين — القص بالفرق راح يطلع هالة. قل له يعيد تصوير الغرفة بدون ما يلمس الكاميرا،"
                    " أو كمّل بخلفية بديلة (theme / صورة) بدل غرفته.")
    elif diff > 18: print("⚠️ الإضاءة أو الأغراض تغيّرت بين اللقطتين — أعرض عليه لقطة قبل ما نعتمدها.")
    if spread > 6: print("⚠️ فيه حركة داخل لقطة الغرفة (أحد مرّ؟ ستارة؟) — الوسيط يخففها، بس افحص plate_src.png")
    json.dump({"moved": moved, "shift": shift, "edgeDiff": diff}, open(os.path.join(OUT, "plate.json"), "w"))
    sys.exit(3 if moved else 0)

# ══════════════════════════════════════════════════════════════════════════
if CMD == "build":
    if not os.path.exists(P("person.json")): sys.exit("⛔ اكتب person.json أول (الصيغة بأعلى الملف)")
    if not os.path.exists(P("cutz.mp4")): sys.exit("⛔ ما فيه cutz.mp4 — شغّل 03_cut_zoom.py أول")
    cfg = json.load(open(P("person.json"), encoding="utf-8"))
    Z, anch, keep, off = zoom_plan()
    plate_src = cv2.imread(os.path.join(OUT, "plate_src.png")) if os.path.exists(os.path.join(OUT, "plate_src.png")) else None
    if plate_src is not None and json.load(open(os.path.join(OUT, "plate.json"))).get("moved"):
        print("⚠️ لقطة الغرفة ما تنطبق على الفيديو (الكاميرا تحرّكت) — ما راح أستعملها: القص بالشخص وحده")
        plate_src = None
    PM = personmask_cmd(); quality = "balanced" if "--fast" in sys.argv else "accurate"
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):                         # بقايا بناء سابق
        if f.startswith(("w", "plate_w", "preview_w")): os.remove(os.path.join(OUT, f))
    out = {"windows": [], "anch": anch}
    sw, sh = [int(v) for v in probe(P("src.mov"), "stream=width,height").split("x")[:2]]
    plate1 = crop_like_cut(plate_src, 1.0, anch) if plate_src is not None else None      # الغرفة بلا زوم
    if plate1 is not None and any(w.get("bg") == "plate" for w in cfg.get("windows", [])):
        cv2.imwrite(os.path.join(OUT, "plate_w.png"), plate1)
    for n, w in enumerate(cfg.get("windows", []), 1):
        a, b = float(w["a"]), float(w["b"])
        if w.get("bg", "theme") == "plate" and plate_src is None:
            sys.exit(f"⛔ النافذة {n} تبي غرفته خلفها بس ما فيه لقطة غرفة فاضية — شغّل plate أول، أو غيّر bg لـtheme/صورة")
        fd, md = os.path.join(OUT, f"_w{n}"), os.path.join(OUT, f"_w{n}m")
        shutil.rmtree(fd, ignore_errors=True); shutil.rmtree(md, ignore_errors=True); os.makedirs(fd)
        # ⛔ الطبقة تُبنى من المصدر **بلا زوم** (نفس القصّات): لو بنيناها من cutz.mp4 يدخل فيها زوم كل مقطع،
        #    فالشخص المصغّر «ينطّ» حجمه عند كل قطعة. الزوم يرجع بـPerson.tsx (zs) لحظة الانتقال بس.
        fc, lab, zs = [], [], []
        for i, (ka, kb) in enumerate(keep):
            lo, hi = max(a, off[i]), min(b, off[i] + (kb - ka))
            if hi - lo < 1e-3: continue
            zs.append([round(lo, 3), Z[i % len(Z)]])
            fc.append(f"[0:v]trim=start={ka + lo - off[i]:.4f}:end={ka + hi - off[i]:.4f},setpts=PTS-STARTPTS,"
                      f"scale={FW}:{FH}:flags=lanczos,setsar=1[v{len(lab)}]"); lab.append(f"[v{len(lab)}]")
        fc.append("".join(lab) + f"concat=n={len(lab)}:v=1:a=0,fps={FPS},"
                  "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709[vo]")
        ff("-i", P("src.mov"), "-filter_complex", ";".join(fc), "-map", "[vo]", "-q:v", "2", os.path.join(fd, "%05d.jpg"))
        frames = sorted(os.listdir(fd))
        print(f"✂️ النافذة {n}: {a:.2f}→{b:.2f} · {len(frames)} فريم · أقصّ الشخص…")
        subprocess.run(PM + [fd, md, quality, "0"], check=True, capture_output=True)
        rgba = os.path.join(OUT, f"_w{n}a"); shutil.rmtree(rgba, ignore_errors=True); os.makedirs(rgba)
        for k, f in enumerate(frames):
            img = cv2.imread(os.path.join(fd, f))
            seg = cv2.imread(os.path.join(md, f[:-4] + ".png"), cv2.IMREAD_GRAYSCALE)
            seg = cv2.resize(seg, (img.shape[1], img.shape[0])).astype(np.float32) / 255
            alpha = seg
            if plate1 is not None:
                pl = plate1.astype(np.float32); bgm = seg < 0.05
                # تعويض تعريض الكاميرا التلقائي: نسبة كل قناة بالخلفية
                gain = np.array([np.median(img[..., c][bgm]) / max(1.0, np.median(pl[..., c][bgm])) for c in range(3)]) if bgm.sum() > 1000 else np.ones(3)
                d = np.max(np.abs(img.astype(np.float32) - pl * gain), axis=2)
                d = np.clip((d - 16) / (42 - 16), 0, 1)                       # فرق واضح = جزء من الشخص
                near = cv2.dilate((seg > 0.3).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))) > 0
                d = cv2.morphologyEx((d * near).astype(np.float32), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
                alpha = np.maximum(seg, d)                                    # الشعر والأغراض بيده والكرسي
            alpha = cv2.GaussianBlur(alpha, (0, 0), 1.2)
            out_img = np.dstack([img, np.clip(alpha * 255, 0, 255).astype(np.uint8)])
            cv2.imwrite(os.path.join(rgba, f[:-4] + ".png"), out_img)
        vid = f"w{n}.webm"
        # VP9 بقناة شفافية — ريموشن يقرأها بـ<OffthreadVideo transparent>
        ff("-framerate", str(FPS), "-i", os.path.join(rgba, "%05d.png"), "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
           "-crf", "14", "-b:v", "0", "-row-mt", "1", "-auto-alt-ref", "0", os.path.join(OUT, vid))
        # لقطة معاينة من النص: الشخص فوق رقعة شطرنج — تشوف القص بعينك قبل الرندر
        mid = cv2.imread(os.path.join(rgba, frames[len(frames)//2][:-4] + ".png"), cv2.IMREAD_UNCHANGED)
        yy, xx = np.indices(mid.shape[:2]); cb = (((yy // 40) + (xx // 40)) % 2 * 60 + 120).astype(np.uint8)
        al = mid[..., 3:4].astype(np.float32) / 255
        prev = (mid[..., :3] * al + np.dstack([cb] * 3) * (1 - al)).astype(np.uint8)
        cv2.imwrite(os.path.join(OUT, f"preview_w{n}.jpg"), cv2.resize(prev, (540, 960)))
        for x in (fd, md, rgba): shutil.rmtree(x, ignore_errors=True)
        ow = {k: w[k] for k in ("a", "b", "bg", "scale", "x", "y", "in", "out", "shadow") if k in w}
        ow.update({"file": vid, "zs": zs, "plate": "plate_w.png" if w.get("bg") == "plate" else None})
        out["windows"].append(ow)
        print(f"   ✅ {vid} · معاينة القص: person/preview_w{n}.jpg ← افتحها وتأكد إن الشعر والأطراف سليمة")
    json.dump(out, open(P("person.out.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nالتالي: 04b_remotion.sh <work> sync (ينسخ الطبقات) ثم render-test على نافذة وحدة قبل الرندر الكامل.")
    sys.exit(0)

sys.exit("الأوامر: plate · build · off")
