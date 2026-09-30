/* ═══ الإضاءة الانتقائية: شي يضوي ثانية أو ثنتين والباقي يغمق ═══
   البيانات من spotlight.out.json (يبنيه 29_spotlight.py) — لا تكتبها هني.
   كل شي يُرسم **داخل نافذة الفيديو** (Ad.tsx) بنفس زوم الفيديو، فيشتغل بـFULL وCARD وSIDE.
   • target "person" → الشخص مقصوص (طبقة شفافة) يضوي ويتوهّج، والباقي يغمق
   • target "object" → شي بالكادر (Vision، ماك بس) بنفس الطريقة
   • target "area"   → بقعة ضوء بيضاوية بمكان تحدده (بلا قص) — تقدر تتحرك من area إلى to
   • target "frame"  → تدرّج لوني مؤقت للكادر كله (تغميق · تشبّع · تباين) بلا هدف
   ⛔ طلب صريح منه بس (القاعدة ٤) — الباقي من الفيديو ما يُلمس. */
import {OffthreadVideo, Sequence, staticFile} from 'remotion';
import P from './project.json';
import {FPS, T} from './theme';
import {rgba} from './util';

type Area = {x:number; y:number; rx:number; ry:number};
type SW = {a:number; b:number; target:'person'|'object'|'area'|'frame'; file?:string;
  area?:Area; to?:Area; dim?:number; desat?:number; contrast?:number; lift?:number;
  glow?:string|null; glowSize?:number; glowAlpha?:number; pulse?:boolean; in?:number; out?:number};
export const SPOTS: SW[] = (((P as any).spotlight || {}).windows || []) as SW[];

const clamp = (v:number) => Math.max(0, Math.min(1, v));
const sm = (k:number) => k * k * (3 - 2 * k);
export const spotAt = (t:number) => SPOTS.find(w => t >= w.a && t < w.b);
/** شدّة النافذة 0…1 — دخول وخروج ناعمين */
const amt = (w:SW, t:number) => {
  const i = w.in ?? 0.25, o = w.out ?? 0.35;
  return sm(Math.min(i > 0 ? clamp((t - w.a) / i) : 1, o > 0 ? clamp((w.b - t) / o) : 1));
};
/** لون التوهّج: مفتاح من ثيمه (acc · sky · warm…) أو hex — الافتراضي لون تمييزه */
const glowCol = (g:string|null|undefined) =>
  g === null ? null : (g && g.startsWith('#') ? g : ((T as any)[g || 'acc'] || T.acc));

/** فلتر «الباقي» — يُطبّق على الفيديو الأصلي نفسه (Ad.tsx) */
export const restFilter = (t:number) => {
  const w = spotAt(t); if (!w) return undefined;
  const k = amt(w, t);
  const br = 1 - (w.dim ?? (w.target === 'frame' ? 0.25 : 0.55)) * k;
  const sa = 1 - (w.desat ?? (w.target === 'frame' ? 0.6 : 0.3)) * k;
  const co = 1 + ((w.contrast ?? 1) - 1) * k;
  return `brightness(${br.toFixed(3)}) saturate(${sa.toFixed(3)}) contrast(${co.toFixed(3)})`;
};

const glowFilter = (w:SW, t:number, k:number) => {
  const c = glowCol(w.glow);
  const lift = `brightness(${(1 + (w.lift ?? 0.12) * k).toFixed(3)})`;
  if (!c) return lift;
  /* نبضة وحدة بالنص لو pulse — التوهّج يكبر ويرجع */
  const pl = w.pulse ? 1 + 0.45 * Math.sin(Math.PI * clamp((t - w.a) / Math.max(0.01, w.b - w.a))) : 1;
  const G = (w.glowSize ?? 26) * k * pl, A = (w.glowAlpha ?? 0.85) * k;
  return `${lift} drop-shadow(0 0 ${(G * 0.35).toFixed(1)}px ${rgba(c, A)}) drop-shadow(0 0 ${G.toFixed(1)}px ${rgba(c, A * 0.7)})`;
};

type VS = React.CSSProperties;
const AreaSpot = ({w, t, src, vstyle}:{w:SW; t:number; src:string; vstyle:VS}) => {
  const k = amt(w, t), A = w.area!, B = w.to || A;
  const m = sm(clamp((t - w.a) / Math.max(0.01, w.b - w.a)));
  const x = A.x + (B.x - A.x) * m, y = A.y + (B.y - A.y) * m;
  const rx = A.rx + (B.rx - A.rx) * m, ry = A.ry + (B.ry - A.ry) * m;
    /* نسب مئوية لا بكسل — عشان البقعة تنطبق داخل كرت مصغّر (CARD/SIDE) كما بملء الشاشة */
  const ell = `radial-gradient(ellipse ${(rx * 100).toFixed(2)}% ${(ry * 100).toFixed(2)}% at ${(x * 100).toFixed(2)}% ${(y * 100).toFixed(2)}%, #000 62%, transparent 100%)`;
  const c = glowCol(w.glow);
  return (<>
    {/* نسخة ثانية من نفس الفيديو بلا تغميق، مقصوصة ببقعة ناعمة الحواف */}
    <div style={{position:'absolute', inset:0, WebkitMaskImage:ell, maskImage:ell}}>
      <OffthreadVideo src={src} muted style={{...vstyle, filter:`brightness(${(1 + (w.lift ?? 0.12) * k).toFixed(3)})`}} />
    </div>
    {c && <div style={{position:'absolute', left:`${(x - rx * 1.15) * 100}%`, top:`${(y - ry * 1.15) * 100}%`,
      width:`${rx * 230}%`, height:`${ry * 230}%`, borderRadius:'50%', mixBlendMode:'screen',
      background:`radial-gradient(ellipse at center, transparent 50%, ${rgba(c, 0.22 * k)} 70%, transparent 88%)`}} />}
  </>);
};

/** داخل نافذة الفيديو، بعد الفيديو الأصلي. vstyle = نفس ستايل الفيديو (الزوم والمرساة) */
export const SpotLayer = ({t, src, vstyle}:{t:number; src:string; vstyle:VS}) => (<>
  {SPOTS.map((w, i) => {
    if (w.target === 'frame') return null;
    if (w.target === 'area') return t >= w.a && t < w.b ? <AreaSpot key={i} w={w} t={t} src={src} vstyle={vstyle} /> : null;
    if (!w.file) return null;
    /* كل نافذة Sequence خاصة فيها — الطبقة مبنية من cutz.mp4 فتنطبق على الفيديو فريم بفريم */
    return (
      <Sequence key={i} from={Math.round(w.a * FPS)} durationInFrames={Math.max(1, Math.round((w.b - w.a) * FPS))} layout="none">
        <div style={{position:'absolute', inset:0, filter:glowFilter(w, t, amt(w, t))}}>
          <OffthreadVideo src={staticFile(w.file)} transparent muted style={vstyle} />
        </div>
      </Sequence>
    );
  })}
</>);
