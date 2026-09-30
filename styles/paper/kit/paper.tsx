/* ═══════ عُدّة الورق المقصوص — Stop-motion paper-cut ═══════
   import {Piece, PaperWord, PaperBG, PaperClip, assemble, stepT, muted} from './paper';
   الدليل: styles/paper/STYLE.md
   كل قطعة = ورقة مسطّحة مقصوصة: حافة ممزّقة · شريحة بيضاء تحتها · ملمس ألياف · ظل قاسي.
   تدخل من برّا الكادر **بحركة متقطّعة ١٢ إطاراً** (stop-motion)، وترتجف رجفة خفيفة بعد ما تستقر (boil).
   ⛔ ممنوع: تحوّل (morph) · طيّ · رسم يتكوّن بمكانه · حركة ناعمة رقمية — القطعة تنزلق أو تدور أو تسقط بس.
   ⛔ الألوان من الثيم (القاعدة ٣) — `muted()` يطفيها شوي عشان تحس ورق، ما يبدّلها. */
import React from 'react';
import {OffthreadVideo, Sequence} from 'remotion';
import {staticFile} from 'remotion';
import {T, FPS} from './theme';
import {mix, lum} from './util';

export const PFPS = 12;                                          // إيقاع الورق — «on twos» تقريباً
/** الوقت مقطّع على ١٢ إطاراً — كل حركة ورق تمر من هنا */
export const stepT = (t:number, fps = PFPS) => Math.floor(t * fps) / fps;
const clamp = (v:number) => Math.max(0, Math.min(1, v));
const rng = (s:number) => { const x = Math.sin(s * 9301.7 + 49297.3) * 233280; return x - Math.floor(x); };
const backOut = (k:number) => { const c = 1.35; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
const easeOut = (k:number) => 1 - Math.pow(1 - k, 3);
/** لون الثيم بطابع ورق (أقل تشبّع وأدفى) */
export const muted = (c:string, k = 0.22) => mix(c, '#D8CCB8', k);
/** لون الكتابة فوق الورقة — يقرأ hex و rgb() (muted يرجّع rgb) */
const toHex = (c:string) => { const m = c.match(/\d+/g); return c.startsWith('#') || !m ? c :
  '#' + m.slice(0, 3).map(v => (+v).toString(16).padStart(2, '0')).join(''); };
const inkOn = (bg:string) => (lum(toHex(bg)) > 0.42 ? '#1A1A1A' : '#FAF6EE');

type Dir = 'left' | 'right' | 'top' | 'bottom' | 'drop';
/** إزاحة البداية من برّا الكادر حسب الاتجاه */
const offFrom = (d:Dir, x:number, y:number, w:number, h:number) =>
  d === 'left' ? [-(x + w + 60), 0] : d === 'right' ? [1080 - x + 60, 0] :
  d === 'top' ? [0, -(y + h + 60)] : d === 'bottom' ? [0, 1920 - y + 60] : [0, -140];

/** شكل الورقة (قبل التمزيق): مستطيل · دائرة · مسار SVG حر بإحداثيات 0..w × 0..h */
export type Shape = 'rect' | 'circle' | 'pill' | string;

/**
 * قطعة ورق وحدة.
 *  at = وقت الدخول (خذه من caps.json — مع الكلمة) · dur = مدة الانزلاق · out = وقت الخروج (اختياري)
 *  from = من وين تدخل · rot = ميلانها النهائي · seed = يغيّر شكل التمزيق والرجفة
 */
export const Piece = ({t, x, y, w, h, color = T.cream, at, dur = 0.5, out, outDur = 0.35, from = 'bottom',
  rot = 0, seed = 1, shape = 'rect', torn = 1, sliver = true, boil = true, shadow = true, z, children}:
  {t:number; x:number; y:number; w:number; h:number; color?:string; at:number; dur?:number; out?:number; outDur?:number;
   from?:Dir; rot?:number; seed?:number; shape?:Shape; torn?:number; sliver?:boolean; boil?:boolean; shadow?:boolean;
   z?:number; children?:React.ReactNode}) => {
  const ts = stepT(t);
  if (ts < at) return null;
  if (out !== undefined && ts > out + outDur) return null;
  const kIn = backOut(clamp((ts - at) / dur));
  const kOut = out !== undefined ? easeOut(clamp((ts - out) / outDur)) : 0;
  const [ox, oy] = offFrom(from, x, y, w, h);
  const k = kIn * (1 - kOut);
  const settled = kIn >= 0.999 && kOut === 0;
  const n = Math.floor(ts * PFPS);                                  // رقم الخطوة — للرجفة
  const jx = boil && settled ? (rng(seed * 131 + n) - 0.5) * 2.2 : 0;
  const jy = boil && settled ? (rng(seed * 173 + n) - 0.5) * 2.2 : 0;
  const jr = boil && settled ? (rng(seed * 197 + n) - 0.5) * 0.7 : 0;
  const dx = ox * (1 - k) + jx, dy = oy * (1 - k) + jy;
  const r = rot + (1 - k) * (rng(seed) > 0.5 ? 9 : -9) + jr;
  const pad = 18, id = `pp${seed}`;
  const sc = 14 * torn;                                             // قوة التمزيق
  const body = (fill:string, grow:number, fid:string) =>
    shape === 'circle' ? <ellipse cx={pad + w/2} cy={pad + h/2} rx={w/2 + grow} ry={h/2 + grow} fill={fill} filter={`url(#${fid})`}/> :
    shape === 'pill'   ? <rect x={pad - grow} y={pad - grow} width={w + 2*grow} height={h + 2*grow} rx={(h + 2*grow)/2} fill={fill} filter={`url(#${fid})`}/> :
    shape === 'rect'   ? <rect x={pad - grow} y={pad - grow} width={w + 2*grow} height={h + 2*grow} fill={fill} filter={`url(#${fid})`}/> :
    <path d={shape} transform={`translate(${pad},${pad})`} fill={fill} stroke={fill} strokeWidth={grow * 2} filter={`url(#${fid})`}/>;
  return (
    <div style={{position:'absolute', left:x, top:y, width:w, height:h, zIndex:z,
      transform:`translate(${dx}px, ${dy}px) rotate(${r}deg)`,
      filter: shadow ? 'drop-shadow(6px 9px 0 rgba(0,0,0,0.30)) drop-shadow(0 14px 18px rgba(0,0,0,0.16))' : undefined}}>
      <svg width={w + 2*pad} height={h + 2*pad} style={{position:'absolute', left:-pad, top:-pad, overflow:'visible'}}>
        <defs>
          {/* حافة ممزّقة: ضجيج يزحزح حدود الشكل */}
          <filter id={`${id}e`} x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="3" seed={seed} result="n"/>
            <feDisplacementMap in="SourceGraphic" in2="n" scale={sc} xChannelSelector="R" yChannelSelector="G"/>
          </filter>
          {/* نفس التمزيق + ألياف الورق (ضجيج ناعم مضروب بلون الورقة) */}
          <filter id={`${id}p`} x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="3" seed={seed + 7} result="n"/>
            <feDisplacementMap in="SourceGraphic" in2="n" scale={sc * 0.8} xChannelSelector="R" yChannelSelector="G" result="torn"/>
            <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={seed + 3} result="g"/>
            <feColorMatrix in="g" type="saturate" values="0" result="gg"/>
            <feComponentTransfer in="gg" result="gl">
              <feFuncR type="linear" slope="0.34" intercept="0.74"/><feFuncG type="linear" slope="0.34" intercept="0.74"/>
              <feFuncB type="linear" slope="0.34" intercept="0.74"/><feFuncA type="linear" slope="0" intercept="1"/>
            </feComponentTransfer>
            <feComposite in="gl" in2="torn" operator="in" result="gc"/>
            <feBlend in="torn" in2="gc" mode="multiply"/>
          </filter>
        </defs>
        {sliver && body('#F7F3EA', 5, `${id}e`)}
        {body(color, 0, `${id}p`)}
      </svg>
      <div style={{position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center',
        color:inkOn(color), fontFamily:T.font}}>{children}</div>
    </div>
  );
};

/**
 * كلمات كلامه تنقص ورق وتدخل كلمة كلمة مع نطقها.
 *  words = من caps.json (W(i) بـScenes.tsx) — ⛔ كلامه بالحرف بس (القاعدة ٦)
 *  يبني أسطر من اليمين لليسار، وكل كلمة ورقة بلون من الألوان المعطاة.
 */
export const PaperWord = ({t, words, x = 90, y = 360, maxW = 900, size = 92, colors, out, seed = 11, lead = 0.04}:
  {t:number; words:{t:string; s:number; e:number}[]; x?:number; y?:number; maxW?:number; size?:number;
   colors?:string[]; out?:number; seed?:number; lead?:number}) => {
  const cs = colors && colors.length ? colors : [muted(T.acc), T.cream, muted(T.sky || T.bg)];
  const est = (s:string) => s.length * size * 0.56 + size * 0.9;   // تقدير عرض الكلمة (يكفي لتوزيع الأسطر)
  const lines:{w:typeof words[0]; W:number}[][] = [[]]; let used = 0;
  const clean = (s:string) => s.replace(/[،,.:؛;!؟?"«»]/g, '');       // الترقيم يبقى بالكابشن، مو على الورق
  words = words.map(w => ({...w, t: clean(w.t)})).filter(w => w.t);
  words.forEach(w => { const W = est(w.t); if (used + W > maxW && lines[lines.length-1].length) { lines.push([]); used = 0; }
    lines[lines.length-1].push({w, W}); used += W + 18; });
  let idx = 0;
  return (<>{lines.map((ln, li) => { let cx = x + maxW;                // عربي: من اليمين
    return ln.map(({w, W}) => { cx -= W; const i = idx++; const px = cx; cx -= 18;
      return (
        <Piece key={i} t={t} x={px} y={y + li * (size * 1.55)} w={W} h={size * 1.3} at={w.s - lead} dur={0.35}
          from={i % 2 ? 'right' : 'top'} rot={(rng(seed + i) - 0.5) * 6} seed={seed + i * 5} color={cs[i % cs.length]}
          out={out}>
          <span style={{fontWeight:900, fontSize:size, lineHeight:1, marginTop:-size * 0.08}}>{w.t}</span>
        </Piece>);
    }); })}</>);
};

/**
 * ترتيب التجميع (من الخلف للأمام): أعطه عناصر بطبقاتها، يرجّع وقت دخول كل وحدة.
 *  layers: 0 سماء/حائط · 1 أرض · 2 مكان وأغراض · 3 ناس بالخلفية · 4 البطل (آخر شي، جزء جزء)
 *  يوزّعهم على [a, b] بتأخير متدرّج ولمسة عشوائية (توقيت غير منتظم = يدوي).
 */
export const assemble = (layers:number[], a:number, b:number, seed = 5) => {
  const order = layers.map((l, i) => ({l, i})).sort((p, q) => p.l - q.l || p.i - q.i);
  const span = Math.max(0.2, b - a), stepS = span / Math.max(1, order.length);
  const out = new Array(layers.length).fill(a);
  order.forEach((o, k) => { out[o.i] = a + k * stepS + (rng(seed + k) - 0.5) * stepS * 0.35; });
  return out as number[];
};

/** خلفية ورق كاملة: شرائح سماء من فوق وأرض من تحت — بألوان هويته مطفية */
export const PaperBG = ({t, at, out, top = [T.bg, T.sky], ground = [T.sand, T.cream], horizon = 1250, seed = 40}:
  {t:number; at:number; out?:number; top?:string[]; ground?:string[]; horizon?:number; seed?:number}) => {
  const sky = [0, 1, 2].map(i => ({y: -60 + i * (horizon / 3), h: horizon / 3 + 90, c: muted(top[i % top.length], 0.15 + i * 0.08)}));
  const gr = [0, 1, 2].map(i => ({y: horizon - 40 + i * ((1920 - horizon) / 3), h: (1920 - horizon) / 3 + 120,
    c: muted(ground[i % ground.length], 0.12 + i * 0.1)}));
  return (<>
    {sky.map((s, i) => <Piece key={'s'+i} t={t} x={-40} y={s.y} w={1160} h={s.h} color={s.c} at={at + i * 0.12}
      from="top" rot={(rng(seed+i)-0.5)*1.6} seed={seed + i} sliver={i > 0} boil={false} out={out}/>)}
    {gr.map((g, i) => <Piece key={'g'+i} t={t} x={-40} y={g.y} w={1160} h={g.h} color={g.c} at={at + 0.36 + i * 0.12}
      from="bottom" rot={(rng(seed+9+i)-0.5)*1.6} seed={seed + 10 + i} boil={false} out={out}/>)}
  </>);
};

/**
 * مقطع ورق مولّد (من طريق البرومبتات — references/paper-motion.md) يتركّب بنافذة [a, b].
 *  dur = مدته الفعلية (ffprobe) · from/to = الجزء المستعمل منه بالثواني (غالباً نبدأ بعد الإطارات الفاضية)
 *  يتسرّع ليخلص عند b بالضبط (١× إلى ٣× — الورق يتحمّل السرعة). الصوت مكتوم: الفولي يمر عبر مكتبة الأصوات.
 */
export const PaperClip = ({src, a, b, from = 0, to, x = 0, y = 0, w = 1080, h = 1920, fit = 'cover', radius = 0}:
  {src:string; a:number; b:number; from?:number; to:number; x?:number; y?:number; w?:number; h?:number;
   fit?:'cover'|'contain'; radius?:number}) => {
  const rate = Math.min(3, Math.max(1, (to - from) / Math.max(0.1, b - a)));
  return (
    <Sequence from={Math.round(a * FPS)} durationInFrames={Math.max(1, Math.round((b - a) * FPS))} layout="none">
      <div style={{position:'absolute', left:x, top:y, width:w, height:h, overflow:'hidden', borderRadius:radius}}>
        <OffthreadVideo src={staticFile(src)} muted playbackRate={rate} startFrom={Math.round(from * FPS)}
          style={{width:'100%', height:'100%', objectFit:fit}}/>
      </div>
    </Sequence>);
};
