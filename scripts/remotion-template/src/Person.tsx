/* ═══ الشخص مقصوص: خلفية بديلة · تصغير · تكبير · تحريك ═══
   البيانات من person.out.json (يبنيه 27_person_layer.py) — لا تكتبها هني.
   • bg "plate"  → غرفته فاضية وراه (من لقطة الغرفة) — الشخص + الغرفة = الفريم الأصلي بالضبط، فالانتقال بلا قفزة.
   • bg "theme"  → خلفية هويته الحيّة (LiveBG تحت) — الفيديو الأصلي يتلاشى وتبقى الطبقة.
   • bg ملف      → صورة أو فيديو من assets/ تحت الشخص.
   ⛔ النوافذ بصيغة FULL فقط وبلا زوم ريموشن (vzoom) — الطبقة ملء الشاشة من المصدر بلا زوم، وزوم كل مقطع يرجع هني. */
import {Img, OffthreadVideo, Sequence, staticFile} from 'remotion';
import P from './project.json';
import {FPS} from './theme';

type PW = {a:number; b:number; bg?:string; scale?:number; x?:number; y?:number; in?:number; out?:number;
  shadow?:boolean; file:string; zs:[number,number][]; plate:string|null};
const PD = ((P as any).person || {}) as {windows?:PW[]; anch?:number};
export const PERSON: PW[] = (PD.windows || []) as PW[];
const ANCH = PD.anch ?? 0.30;

const clamp = (v:number) => Math.max(0, Math.min(1, v));
const ease = (k:number) => k < 0.5 ? 4*k*k*k : 1 - Math.pow(-2*k + 2, 3) / 2;
const isVid = (f:string) => /\.(mp4|webm|mov|m4v)$/i.test(f);

export const personAt = (t:number) => PERSON.find(w => t >= w.a && t < w.b);
/** مرحلتان — عشان ما يطلع «شخصين» فوق بعض:
    bgK: الخلفية تتبدّل والشخص بحجمه الأصلي (أول ٤٥٪ من in) · mvK: بعدها يصغر/يتحرك. والخروج بالعكس. */
const phases = (w:PW, t:number) => {
  const i = w.in ?? 0.4, o = w.out ?? 0.4;
  const e = Math.min(i > 0 ? clamp((t - w.a) / i) : 1, o > 0 ? clamp((w.b - t) / o) : 1);
  return {bgK: ease(clamp(e / 0.45)), mvK: ease(clamp((e - 0.45) / 0.55))};
};
/** شفافية الفيديو الأصلي تحت الطبقة (Ad.tsx يستعملها) */
export const baseVideoOpacity = (t:number) => {
  const w = personAt(t); if (!w) return 1;
  return w.plate ? 0 : 1 - phases(w, t).bgK;
};
/** زوم المقطع الحالي (03_cut_zoom يقصّ كل مقطع بزوم) — الطبقة مبنية بلا زوم، فنرجّعه هني */
const zoomAt = (w:PW, t:number) => ([...w.zs].reverse().find(z => t >= z[0]) || w.zs[0] || [0, 1])[1];

type BP = React.FC<{t:number}> | undefined;
const Win = ({w, t, Behind}:{w:PW; t:number; Behind:BP}) => {
  const {bgK, mvK} = phases(w, t), bg = w.bg ?? 'theme', z = zoomAt(w, t);
  /* النقطة p ← s·p + (tx,ty).  بداية: زوم المقطع حول (540, ANCH·1920) = نفس الفيديو الأصلي بالبكسل.
     نهاية: قاعدة الكادر (540,1920) تروح لـ(x·1080, y·1920) بحجم scale. */
  const S = w.scale ?? 1, cy = ANCH * 1920;
  const s0 = z, tx0 = 540 - z * 540, ty0 = cy - z * cy;
  const tx1 = (w.x ?? 0.5) * 1080 - S * 540, ty1 = (w.y ?? 1) * 1920 - S * 1920;
  const s = s0 + (S - s0) * mvK, tx = tx0 + (tx1 - tx0) * mvK, ty = ty0 + (ty1 - ty0) * mvK;
  const sh = (w.shadow ?? !w.plate) ? mvK : 0;
  const shadow = sh > 0 ? `drop-shadow(0 ${24*sh}px ${36*sh}px rgba(0,0,0,${0.38*sh}))` : 'none';
  const full:React.CSSProperties = {position:'absolute', left:0, top:0, width:1080, height:1920, objectFit:'cover'};
  const zoomed:React.CSSProperties = {...full, transformOrigin:'0 0', transform:`translate(${tx0}px, ${ty0}px) scale(${s0})`};
  return (<>
    {/* الغرفة الفاضية تاخذ نفس زوم المقطع — مثل الفيديو الأصلي بالضبط */}
    {w.plate && <Img src={staticFile(w.plate)} style={zoomed} />}
    {!w.plate && bg !== 'theme' && (isVid(bg)
      ? <OffthreadVideo src={staticFile(bg.split('/').pop()!)} muted style={{...full, opacity:bgK}} />
      : <Img src={staticFile(bg.split('/').pop()!)} style={{...full, opacity:bgK}} />)}
    {/* رسم ورا الشخص وقدّام الخلفية: BehindPerson بـScenes.tsx (اختياري) */}
    {Behind && <div style={{...full, opacity:bgK}}><Behind t={t} /></div>}
    <div style={{...full, transformOrigin:'0 0', filter:shadow, transform:`translate(${tx}px, ${ty}px) scale(${s})`}}>
      <OffthreadVideo src={staticFile(w.file)} transparent muted style={full} />
    </div>
  </>);
};

/** كل نافذة Sequence خاصة فيها — طبقة الشخص تمشي بتوقيت الفيديو بالضبط */
export const PersonStage = ({t, Behind}:{t:number; Behind?:BP}) => (<>
  {PERSON.map((w, i) => (
    <Sequence key={i} from={Math.round(w.a * FPS)} durationInFrames={Math.max(1, Math.round((w.b - w.a) * FPS))} layout="none">
      <Win w={w} t={t} Behind={Behind} />
    </Sequence>
  ))}
</>);
