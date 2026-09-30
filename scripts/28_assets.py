#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""28_assets.py — يجيب صوراً ومقاطع وأيقونات مجانية من النت، بورقة اختيار وحدة، ويسجّل رخصتها.

    python3 28_assets.py <work> search "<كلمات بالإنجليزي>" [--kind photo|video|icon] [--n 12] [--src …] [--any-orient]
    python3 28_assets.py <work> pick <slug> <رقم> [--name <اسم>] [--cut]
    python3 28_assets.py <work> icon twemoji:flag-egypt noto:trophy  # أيقونات بأسمائها بالضبط
    python3 28_assets.py <work> credits                      # قائمة الإسناد (لكابشن البوست لو الرخصة تطلبه)
    python3 28_assets.py <work> clean                        # يمسح المرشّحين (_cand) بعد الاختيار

search: يدوّر بكل المصادر المتاحة، ينزّل مصغّرات، ويبني **ورقة وحدة مرقّمة** assets/_cand/<slug>.jpg
        ← اقرأها بعينك (صورة وحدة بدل ١٢)، واختر الأوضح والأقرب للكلام والملتزم بقيوده.
pick:   ينزّل الأصل بدقته الكاملة لـassets/<اسم>، ويسجّله بـassets/SOURCES.json (المصدر · الصاحب · الرخصة).
        --cut: يشيل الخلفية (قص الموضوع). والمقطع: يطلّع ورقة فريمات assets/<اسم>.check.jpg تفحص فيها **كل** لقطة (القاعدة ٨٥②).

المصادر (بلا مفاتيح): أرشيف ويكيميديا (أماكن · أشخاص معروفين · أشياء حقيقية · شعارات) · أوبن‌فيرس (صور بترخيص حر) ·
أيقونات Iconify (رموز SVG). وبمفتاح مجاني (اختياري — keys.json بمجلد بياناته أو متغيرات PEXELS_API_KEY / PIXABAY_API_KEY):
بيكسلز وبيكساباي (صور ومقاطع فيديو ستوك عمودية — أغنى مصدر للمقاطع).
⛔ لا تذكر أسماء المصادر للمستخدم — «مصادر مجانية موثوقة».
"""
import sys, os, json, re, time, urllib.request, urllib.parse, subprocess, shutil, platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths

if len(sys.argv) < 3: print(__doc__); sys.exit(2)
W = os.path.abspath(sys.argv[1]); CMD = sys.argv[2]
A = os.path.join(W, "assets"); CAND = os.path.join(A, "_cand")
ARG = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
K = os.path.dirname(os.path.abspath(__file__))
UA = "khalid-editing-creatives/1.0 (video editing skill; local use)"

def get(url, headers=None, timeout=25, raw=False):
    """⛔ التنزيل بـcurl لا بـurllib: بايثون الماك (من python.org) كثير ما يلقى شهادات HTTPS،
    فيفشل كل تنزيل بصمت (CERTIFICATE_VERIFY_FAILED) — وهذا كان سبب «ما يجيب صور من النت».
    curl يستعمل شهادات النظام، وموجود بالماك وويندوز ١٠+."""
    cmd = ["curl", "-sSL", "--fail", "--retry", "2", "--max-time", str(timeout), "-A", UA]
    for k, v in (headers or {}).items(): cmd += ["-H", f"{k}: {v}"]
    r = subprocess.run(cmd + [url], capture_output=True)
    if r.returncode:
        raise RuntimeError(f"curl {r.returncode}: {r.stderr.decode('utf-8', 'ignore')[:120]}")
    return r.stdout if raw else json.loads(r.stdout.decode("utf-8"))

def keys():
    k = _paths.load("keys.json", {})
    return {"pexels": os.environ.get("PEXELS_API_KEY") or k.get("pexels"),
            "pixabay": os.environ.get("PIXABAY_API_KEY") or k.get("pixabay")}

def slugify(q): return re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")[:40] or "q"

# ── المصادر: كل وحدة ترجّع [{src, thumb, full, w, h, title, author, license, page, kind}] ──
def s_commons(q, kind, n, portrait):
    if kind == "icon": return []                                  # الأيقونات من Iconify (SVG نظيف)
    ft = {"photo": "filetype:bitmap", "video": "filetype:video", "icon": "filetype:drawing"}.get(kind, "")
    u = ("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "generator": "search", "gsrsearch": f"{ft} {q}".strip(), "gsrnamespace": 6, "gsrlimit": n * 2,
        "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 480, "format": "json"}))
    out = []
    for pg in (get(u).get("query", {}).get("pages", {}) or {}).values():
        ii = (pg.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata", {})
        lic = md.get("LicenseShortName", {}).get("value", "?")
        if re.search(r"NC|ND|fair use|non-free", lic, re.I): continue
        au = re.sub(r"<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip()[:80]
        out.append({"src": "commons", "thumb": ii.get("thumburl"), "full": ii.get("url"), "w": ii.get("width"),
                    "h": ii.get("height"), "title": pg.get("title", "")[5:], "author": au, "license": lic,
                    "page": ii.get("descriptionurl"), "kind": "video" if "video" in ii.get("mime", "") else kind})
    return out

def s_openverse(q, kind, n, portrait):
    if kind not in ("photo", "any"): return []
    p = {"q": q, "page_size": n, "license_type": "commercial", "mature": "false"}
    if portrait: p["aspect_ratio"] = "tall"
    r = get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(p))
    return [{"src": "openverse", "thumb": x.get("thumbnail"), "full": x.get("url"), "w": x.get("width"), "h": x.get("height"),
             "title": x.get("title", ""), "author": x.get("creator", ""), "license": ("CC0" if x.get("license") in ("cc0", "pdm") else f"CC {x.get('license','').upper()}"),
             "page": x.get("foreign_landing_url"), "kind": "photo"} for x in r.get("results", [])]

def s_pexels(q, kind, n, portrait):
    k = keys()["pexels"]
    if not k or kind == "icon": return []
    vid = kind == "video"
    p = {"query": q, "per_page": n, **({"orientation": "portrait"} if portrait else {})}
    r = get(("https://api.pexels.com/videos/search?" if vid else "https://api.pexels.com/v1/search?") + urllib.parse.urlencode(p),
            headers={"Authorization": k})
    out = []
    for x in r.get("videos" if vid else "photos", []):
        if vid:
            fs = sorted([f for f in x.get("video_files", []) if f.get("width")], key=lambda f: -(f["width"] * f["height"]))
            fs = [f for f in fs if max(f["width"], f["height"]) <= 2160] or fs
            if not fs: continue
            out.append({"src": "pexels", "thumb": x.get("image"), "full": fs[0]["link"], "w": fs[0]["width"], "h": fs[0]["height"],
                        "title": q, "author": x.get("user", {}).get("name", ""), "license": "Pexels License",
                        "page": x.get("url"), "kind": "video", "dur": x.get("duration")})
        else:
            out.append({"src": "pexels", "thumb": x["src"]["medium"], "full": x["src"]["original"], "w": x.get("width"),
                        "h": x.get("height"), "title": x.get("alt", q), "author": x.get("photographer", ""),
                        "license": "Pexels License", "page": x.get("url"), "kind": "photo"})
    return out

def s_pixabay(q, kind, n, portrait):
    k = keys()["pixabay"]
    if not k or kind == "icon": return []
    vid = kind == "video"
    p = {"key": k, "q": q, "per_page": max(3, n), "safesearch": "true", **({} if vid else {"image_type": "photo"}),
         **({"orientation": "vertical"} if portrait and not vid else {})}
    r = get(("https://pixabay.com/api/videos/?" if vid else "https://pixabay.com/api/?") + urllib.parse.urlencode(p))
    out = []
    for x in r.get("hits", []):
        if vid:
            v = x["videos"].get("large") or x["videos"].get("medium") or {}
            if not v.get("url"): continue
            out.append({"src": "pixabay", "thumb": v.get("thumbnail") or x["videos"].get("tiny", {}).get("thumbnail"),
                        "full": v["url"], "w": v.get("width"), "h": v.get("height"), "title": x.get("tags", q),
                        "author": x.get("user", ""), "license": "Pixabay License", "page": x.get("pageURL"),
                        "kind": "video", "dur": x.get("duration")})
        else:
            out.append({"src": "pixabay", "thumb": x.get("webformatURL"), "full": x.get("largeImageURL"), "w": x.get("imageWidth"),
                        "h": x.get("imageHeight"), "title": x.get("tags", q), "author": x.get("user", ""),
                        "license": "Pixabay License", "page": x.get("pageURL"), "kind": "photo"})
    return out

def s_iconify(q, kind, n, portrait):
    if kind != "icon": return []
    # البحث العام يطلّع الخطية بس — المجموعات الملوّنة تنطلب بالاسم (prefixes)، ثم نكمّل بالعام
    color = "fluent-emoji-flat,noto,twemoji,openmoji,streamline-emojis,flat-color-icons,fxemoji,emojione,logos,skill-icons"
    r = {"icons": get("https://api.iconify.design/search?" + urllib.parse.urlencode({"query": q, "limit": 48, "prefixes": color})).get("icons", [])
                  + get("https://api.iconify.design/search?" + urllib.parse.urlencode({"query": q, "limit": 64})).get("icons", [])}
    # الملوّنة أول (تنفع للموشن قرافيكس) ثم الخطية النظيفة — ومجموعة وحدة ما تاخذ الورقة كلها
    pref = ["fluent-emoji-flat", "noto", "twemoji", "openmoji", "streamline-emojis", "fxemoji", "flat-color-icons",
            "logos", "skill-icons", "twemoji", "emojione", "icon-park", "ph", "tabler", "lucide", "mdi", "material-symbols"]
    rank = lambda ic: (pref.index(ic.split(":")[0]) if ic.split(":")[0] in pref else len(pref))
    seen, pick = {}, []
    for ic in sorted(r.get("icons", []), key=rank):
        pre = ic.split(":")[0]
        if seen.get(pre, 0) >= 2: continue
        seen[pre] = seen.get(pre, 0) + 1; pick.append(ic)
    out = []
    for ic in pick[: n]:
        pre, name = ic.split(":", 1)
        svg = f"https://api.iconify.design/{pre}/{name}.svg?height=512"
        out.append({"src": "iconify", "thumb": svg, "full": svg, "w": 512, "h": 512, "title": ic, "author": pre,
                    "license": "see iconify set " + pre, "page": f"https://icon-sets.iconify.design/{pre}/{name}/", "kind": "icon"})
    return out

SOURCES = {"pexels": s_pexels, "pixabay": s_pixabay, "commons": s_commons, "openverse": s_openverse, "iconify": s_iconify}

# ── ورقة الاختيار: مصغّرات مرقّمة بصورة وحدة ──
def svg_png(svg_path, out_png):
    if platform.system() == "Darwin":
        d = os.path.dirname(svg_path)
        subprocess.run(["qlmanage", "-t", "-s", "300", "-o", d, svg_path], capture_output=True)
        q = svg_path + ".png"
        if os.path.exists(q): os.replace(q, out_png); return True
    return False

def sheet(items, folder, out):
    from PIL import Image, ImageDraw, ImageFont
    cell, cols = 300, 4
    rows = (len(items) + cols - 1) // cols
    S = Image.new("RGB", (cols * cell, rows * (cell + 34)), (245, 243, 238))
    dr = ImageDraw.Draw(S)
    try: font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
    except Exception: font = ImageFont.load_default()
    for i, it in enumerate(items):
        x, y = (i % cols) * cell, (i // cols) * (cell + 34)
        p = os.path.join(folder, f"{i+1:02d}.jpg")
        if os.path.exists(p):
            try:
                im = Image.open(p).convert("RGB"); im.thumbnail((cell - 8, cell - 8))
                S.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
            except Exception: pass
        o = "V" if (it.get("h") or 0) > (it.get("w") or 1) else "H"      # عمودي / أفقي
        tag = f"{i+1}  {it['kind'][0].upper()} {o} {it.get('w') or '?'}x{it.get('h') or '?'}" + (f" {int(it['dur'])}s" if it.get("dur") else "")
        dr.rectangle([x, y + cell, x + cell, y + cell + 34], fill=(30, 30, 30))
        dr.text((x + 8, y + cell + 6), tag, fill=(255, 255, 255), font=font)
    S.save(out, quality=86)

# ══════════════════════════════════════════════════════════════════════════
if CMD == "search":
    if len(sys.argv) < 4: sys.exit('search "<كلمات بالإنجليزي>"')
    q = sys.argv[3]; kind = ARG("--kind", "photo"); n = int(ARG("--n", "12"))
    portrait = "--any-orient" not in sys.argv and kind != "icon"
    srcs = ARG("--src", "all"); srcs = list(SOURCES) if srcs == "all" else srcs.split(",")
    per = n if kind == "icon" else max(3, n // 2)
    got, notes = [], []
    for s in srcs:
        try:
            r = SOURCES[s](q, kind, per, portrait); got += r
            if r: notes.append(f"{s}:{len(r)}")
        except Exception as e: notes.append(f"{s}:✗")
    # ترتيب: المقاطع/الصور العمودية الكبيرة أول، وتنويع بين المصادر
    def rank(it):
        w, h = it.get("w") or 0, it.get("h") or 0
        return (-(h >= w) if portrait else 0, -min(w, h))
    by = {}
    for it in sorted(got, key=rank): by.setdefault(it["src"], []).append(it)
    items = []
    while len(items) < n and any(by.values()):
        for s in list(by):
            if by[s] and len(items) < n: items.append(by[s].pop(0))
    if not items:
        k = keys()
        sys.exit("❌ ما لقيت شي. جرّب كلمات إنجليزية أبسط أو أعم" +
                 ("" if kind != "video" or k["pexels"] or k["pixabay"] else
                  "\n   ⚠️ المقاطع تحتاج مفتاح مجاني (keys.json) — بدونه المصدر الوحيد للفيديو أرشيف ويكيميديا وهو محدود."))
    slug = slugify(q) + ("-" + kind if kind != "photo" else "")
    d = os.path.join(CAND, slug); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for i, it in enumerate(items):
        try:
            b = get(it["thumb"], raw=True)
            if it["kind"] == "icon":
                sp = os.path.join(d, f"{i+1:02d}.svg"); open(sp, "wb").write(b)
                if not svg_png(sp, os.path.join(d, f"{i+1:02d}.jpg")): pass
            else:
                open(os.path.join(d, f"{i+1:02d}.jpg"), "wb").write(b)
        except Exception:
            # خدمة المصغّرات أحياناً تطيح (أوبن‌فيرس يرجّع 424) — نجيب الأصل للصور بدلها
            if it["kind"] == "photo":
                try: open(os.path.join(d, f"{i+1:02d}.jpg"), "wb").write(get(it["full"], raw=True, timeout=40))
                except Exception: pass
    json.dump({"query": q, "kind": kind, "items": items}, open(os.path.join(d, "cand.json"), "w"), ensure_ascii=False, indent=1)
    out = os.path.join(CAND, slug + ".jpg"); sheet(items, d, out)
    print(f"🔎 «{q}» · {len(items)} مرشّح ({' · '.join(notes)})")
    print(f"   الورقة: {out}")
    print(f"   اختر: python3 scripts/28_assets.py {W} pick {slug} <رقم> --name <اسم>" + (" --cut" if kind == "photo" else ""))
    for i, it in enumerate(items):
        print(f"   {i+1:>2}  {it['kind']:<5} {it.get('w')}x{it.get('h')}  {it['license'][:22]:<22} {it['title'][:60]}")
    sys.exit(0)

# ══════════════════════════════════════════════════════════════════════════
def cutout(img, out):
    """قص الموضوع بلا خلفية: مكتبة أبل بالماك (subjectcut.swift) · rembg بغيره"""
    if platform.system() == "Darwin":
        b = _paths.data("tools", "subjectcut")
        if not os.path.exists(b):
            _paths.ensure(); subprocess.run(["swiftc", "-O", "-o", b, os.path.join(K, "subjectcut.swift")], capture_output=True)
        if os.path.exists(b):
            r = subprocess.run([b, img, out], capture_output=True, text=True)
            if r.returncode == 0 and os.path.exists(out): return True
    try:
        from rembg import remove
        open(out, "wb").write(remove(open(img, "rb").read())); return True
    except Exception:
        return False

if CMD == "pick":
    if len(sys.argv) < 5: sys.exit("pick <slug> <رقم> [--name اسم] [--cut]")
    slug, n = sys.argv[3], int(sys.argv[4])
    c = json.load(open(os.path.join(CAND, slug, "cand.json"), encoding="utf-8"))
    it = c["items"][n - 1]
    ext = {"icon": ".svg", "video": ".mp4"}.get(it["kind"]) or os.path.splitext(urllib.parse.urlparse(it["full"]).path)[1].lower() or ".jpg"
    if it["kind"] == "video" and it["src"] == "commons": ext = os.path.splitext(urllib.parse.urlparse(it["full"]).path)[1].lower()
    name = ARG("--name", f"{slug}-{n}")
    name = re.sub(r"[^\w\-]+", "_", name)
    dst = os.path.join(A, name + ext); os.makedirs(A, exist_ok=True)
    print(f"⏬ {it['title'][:60]} …")
    open(dst, "wb").write(get(it["full"], raw=True, timeout=120))
    final = dst
    if it["kind"] == "video" and ext != ".mp4":                          # webm/ogv → mp4 عشان ريموشن والمتصفح
        mp = os.path.join(A, name + ".mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", dst, "-an", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", mp], check=True)
        os.remove(dst); final = mp
    if it["kind"] == "video":
        # ⛔ القاعدة ٨٥②: قيوده على **كل** فريم — ورقة فريمات كل نص ثانية تشوفها كاملة
        dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",final],
                                   capture_output=True, text=True).stdout.strip() or 1)
        ck = os.path.join(A, name + ".check.jpg")
        nfr = min(48, max(6, int(dur * 2))); cols = 6
        subprocess.run(["ffmpeg","-v","error","-y","-i",final,"-vf",f"fps={nfr/dur:.4f},scale=240:-2,tile={cols}x{(nfr+cols-1)//cols}",
                        "-frames:v","1",ck], check=True)
        print(f"   🎞️ {dur:.1f} ث · افحص كل لقطة: {ck}")
    if "--cut" in sys.argv and it["kind"] == "photo":
        cp = os.path.join(A, name + "_cut.png")
        print("   ✂️ " + (f"قصّيت الموضوع: {cp}" if cutout(final, cp) else "القص ما اشتغل — استعمل الصورة كاملة"))
    src_log = os.path.join(A, "SOURCES.json")
    log = json.load(open(src_log, encoding="utf-8")) if os.path.exists(src_log) else []
    log.append({"file": os.path.basename(final), "title": it["title"], "author": it["author"], "license": it["license"],
                "page": it["page"], "source": it["src"]})
    json.dump(log, open(src_log, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    need = re.search(r"\bBY\b", it["license"] or "", re.I)
    print(f"✅ {final}  ·  {it['license']}" + ("  ← تحتاج إسناد: credits يطلع لك السطر لكابشن البوست" if need else ""))
    sys.exit(0)

if CMD == "icon":
    # أيقونة باسمها بالضبط (من نتيجة search أو معروفة): twemoji:flag-egypt · noto:trophy
    for spec in [a for a in sys.argv[3:] if ":" in a]:
        pre, nm = spec.split(":", 1); os.makedirs(A, exist_ok=True)
        dst = os.path.join(A, re.sub(r"[^\w\-]+", "_", nm) + ".svg")
        try:
            b = get(f"https://api.iconify.design/{pre}/{nm}.svg?height=512", raw=True)
            if b.strip() == b"404" or not b.lstrip().startswith(b"<svg"): raise RuntimeError("غير موجودة")
            open(dst, "wb").write(b); print(f"✅ {dst}")
        except Exception as e: print(f"❌ {spec}: {e}")
    sys.exit(0)

if CMD == "credits":
    p = os.path.join(A, "SOURCES.json")
    if not os.path.exists(p): sys.exit("ما فيه أصول مسجّلة.")
    for x in json.load(open(p, encoding="utf-8")):
        if re.search(r"\bBY\b", x["license"] or "", re.I):
            print(f"• {x['title'][:50]} — {x['author'] or 'unknown'} ({x['license']}) {x['page']}")
    sys.exit(0)

if CMD == "clean":
    shutil.rmtree(CAND, ignore_errors=True); print("انمسحت المرشّحات."); sys.exit(0)

sys.exit("الأوامر: search · pick · icon · credits · clean")
