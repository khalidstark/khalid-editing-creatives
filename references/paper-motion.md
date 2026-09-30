# مقاطع الورق المولّدة (Paper-cut stop-motion) — ٣ برومبتات، هو يولّد

> مأخوذ من مهارة motion-design ومكيّف للمونتاج: المقطع الناتج يتركّب كمشهد داخل الفيديو (`PaperClip` بعُدّة `paper`).
> **أنت تكتب البرومبتات — هو يشغّلها** بأدواته (نموذج صور ثم نموذج فيديو) ويرجّع الملفات. أنت ما تولّد شي.
> ⛔ كلّمه بلغته، والبرومبتات **بالإنجليزي كاملة داخل مربع كود** يقدر ينسخه بضغطة. لا تسمّ له برامج إلا لو سأل
> (لو سأل: للصور GPT Image 2.0، وللفيديو Seedance 2.0 — أثبت شي جرّبناه، وأي بديل يشتغل).

## متى
- لحظة أو ثنتين بالمقطع يستاهلون «واو»: الهوك · الذروة · مشهد يصعب يترسم بالكود (مكان، شخص، حدث).
- **اعرض الفكرة عليه أول** بجملة: «عند ‹الكلمة› أبي مشهد ورق يتبنى: ‹وصف› — تبي نسويه؟ ياخذ منك ٣ توليدات.»
- الباقي بالكود (`styles/paper/STYLE.md`) — لا تطلب منه ١٠ توليدات.

## التجهيز
```bash
mkdir -p <work>/assets/paper/<المشهد>
```
قل له المسار الكامل على سطر لحاله، وكل ملف يولّده يحطه فيه ويقول «تم». (أو يرسله بالمحادثة — عادي.)
الأحدث بـ`ls -t` هو نتيجة آخر برومبت — لا تخلط الأصل بالورق بالورقة.

**صورة البداية:** وحدة من (أ) صورة جبتها من النت (`28_assets.py`) · (ب) صورة أرسلها · (ج) ولا شي — اكتب البرومبت الأول من وصف المشهد نفسه.

---

## ١) برومبت الصورة الورقية
فقرة وحدة بالإنجليزي:
- وصف مختصر لما بالصورة (أو بالمشهد لو ما فيه صورة): الموضوع · الوضعية · الألوان الأساسية · التكوين. **عمودي 9:16.**
- ثم **كتلة الستايل حرفياً:**
  *"Built entirely from layered cut-and-torn paper pieces: every shape is a separate flat paper cutout with rough torn edges, visible paper grain and fibre texture, and a hard drop shadow beneath it. Small rough white negative-space slivers show between the pieces. Muted, tactile, slightly desaturated color treatment. A mosaic of overlapping paper facets, like a real handmade paper artwork photographed under soft directional light. No smooth gradients, no digital flatness, no glossy 3D — it must look like real cut paper."*
- ثم: `Vertical 9:16. No text, letters, numbers or logos anywhere.` + قيوده من ملفه (القاعدة ١١).
- لو ألوان هويته تناسب: `Palette leaning toward <لونين من ثيمه بالكلمات>`.

قدّمها له:
> هذا برومبت **الصورة الورقية** — يحوّل ‹وصف› لكولاج ورق ممزّق:
> ```
> [البرومبت]
> ```
> - 🤖 **نموذج صور** (اللي تستعمله)
> - 📎 **أرفق:** الصورة الأصلية (لو فيه) + (اختياري) أي صورة ورق مقصوص تعجبك كمرجع ستايل لو أداتك تقبل
> - 💾 **احفظ النتيجة** بـ`<المسار>` وقل **تم**

افحصها بالدقة الكاملة: قيوده · ما فيها كتابة مخربطة · شكل ورق فعلاً.

## ٢) الحركة الإضافية؟
المشهد يبني نفسه دائماً. **بعد التجميع** ممكن حركة وحدة تخدم كلامه (السيارة تمشي · الشخص يطير مع البالون · الكرة تدخل والقصاصات تتطاير).
اختر أنت الحركة من **معنى الجملة** واقترحها عليه بجملة — أو «تجميع بس».

## ٣) برومبت الورقة (٣×٣ = ٩ لقطات)
فقرة وحدة بالإنجليزي:
- `A clean 3×3 storyboard sheet of 9 panels showing the scene assembling piece by piece.` **بلا أي نص أو أرقام أو عناوين بالشبكة.**
- من البعيد للقريب: اللوحة ١ كادر شبه فاضي وأول قطع الخلفية تنزلق · الأرض تطلع · المكان والأغراض · الناس بالخلفية · الأغراض تستقر ·
  البطل يتجمّع جزء جزء · (لو فيه حركة: اللوحة ٨ لحظتها) · اللوحة ٩ = التكوين الكامل مطابق للصورة الورقية.
- نفس شكل الورق بكل لوحة (حواف ممزّقة · ألياف · ظلال قاسية · شرائح بيضاء · نفس الألوان). واختم: `No text or writing in any panel.`

> - 🤖 **نموذج صور** · 📐 **المقاس: 9:16** · 📎 **أرفق:** الصورة الورقية اللي ولّدها · 💾 احفظ وقل **تم**

## ٤) برومبت الحركة
فقرة وحدة بالإنجليزي **بهالترتيب الثابت** — الافتتاح والكتل الثلاث الأخيرة **حرفياً بلا تغيير**:
1. **الافتتاح:** *"Animate this as a handcrafted stop-motion paper collage assembly. Every element must enter the frame as a flat pre-cut torn paper piece pushed in from outside the frame."*
2. **جسم التجميع** — رتّب من الخلف للأمام ووصف الدخول: الخلفية من فوق والجوانب · الأرض من تحت بشرائح · المكان والأغراض من الجوانب وفوق ·
   الناس بالخلفية صف صف · الأغراض تستقر · **البطل آخر شي جزء جزء** (من تحت لفوق: الأرجل ← الملابس ← الجذع ← الذراعين ← اليدين ← الرأس ← الملامح ← الشعر آخر شي؛
   للوجه: الفك ← الخدود ← الأنف ← الجبهة ← العيون بلمعة بيضاء صغيرة ← الحواجب ← الشعر). كل قطعة بظل ورق قاسي تحتها، والتفاصيل قصاصات صغيرة منفصلة.
3. **الحركة الإضافية (لو فيه):** تبدأ بـ*"As the final beat…"* — حركة وحدة واضحة بأفعال الورق بس (slide · drop · rotate · tumble · lift · plant · scatter · tip · swing · snap forward · drive off)؛
   المشي = *"flat cutout limbs sliding and swapping mid-stride in choppy stop-motion steps."* ⛔ لا morph ولا fold ولا bend ولا smooth. سلسلة سبب ← نتيجة، والختام *"tiny scattered paper flecks."*
   بلا حركة: اختم بـ*"all pieces settle and lock into place with tiny staggered adjustments."*
4. **الستايل (حرفياً):** *"Motion should feel tactile, slightly imperfect, editorial, and stop-motion realistic, with tiny misalignments, staggered timing, hard shadows, rough white torn edges, overlapping paper layers, and visible paper texture."*
5. **الممنوع (حرفياً):** *"No folding, no morphing, no in-place drawing, no smooth digital animation. Every piece is a pre-made flat cutout sliding, rotating, or dropping into place."*
6. **الصوت (حرفياً):** *"Sound design: ASMR paper-only foley, including soft paper slides, taps, shuffles, drops, and friction. No music, no voice, no ambient sound, no extra effects."*

> - 🎬 **نموذج فيديو** (اللي تستعمله) · 📎 **أرفق:** الورقة (٩ لقطات) كإطار بداية/مرجع · ⚙️ **10 ثواني · 720p أو أعلى · 9:16 · الصوت شغّال**
> - 💾 احفظ المقطع بـ`<المسار>` وقل **تم**

## ٥) تركيبه بالمونتاج
```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 <المقطع>      # مدته (لـto)
ffmpeg -v error -i <المقطع> -vf "fps=2,scale=180:-2,tile=5x4" -frames:v 1 <work>/assets/paper/<المشهد>/check.jpg   # افحص كل لقطة (القاعدة ٨٥②)
cp <المقطع> <work>/assets/paper_<المشهد>.mp4
```
بـ`Scenes.tsx`:
```tsx
<PaperClip src="paper_<المشهد>.mp4" a={A} b={B} from={1.2} to={10} />   // FULL — من أول كلمة الجملة لآخرها
```
- **`from`**: أول ثانية غالباً فاضية — ابدأ من لما يطلع شي بالكادر. المقطع يتسرّع ليخلص عند `B` (حتى ٣×، والورق يتحمّل السرعة).
- الصيغة: `FULL` للهوك · `CARD` لو يبي وجهه باين معه. والقطع للمشهد وعنه **حاد** مع الكلمة (القاعدة ٢٣).
- الصوت مكتوم بالرندر — فولي الورق عبر مكتبة أصواته (`styles/paper/STYLE.md` ← الصوت).

## حرّاس
- ⛔ **لا أسماء أشخاص حقيقيين ولا أعمال فنية مشهورة ولا علامات تجارية** بأي برومبت — وصف عام («لاعب بقميص أصفر»).
- كل برومبت فقرة وحدة بلا أسطر، والثوابت الأربع حرفية.
- لو النتيجة فيها كتابة مخربطة أو يد مشوّهة أو يكسر قيوده: قل له بجملة وش تغيّر، وأعطه البرومبت معدّلاً كاملاً (لا «نفس اللي قبل بس…»).
