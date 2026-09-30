import {AbsoluteFill, Audio, OffthreadVideo, getRemotionEnvironment, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {T, VEND, OUTRO, HAS_SFX, GUIDES, FACE_ANCHOR} from './theme';
import {rgba} from './util';
import {vrect, vzoom} from './stage';
import {Badge, LiveBG} from './Chrome';
import {Captions} from './Captions';
import {Scenes, VideoOverlay} from './Scenes';
import * as SC from './Scenes';   /* BehindPerson اختياري — Scenes.tsx القديمة بدونه تشتغل عادي */
import {Outro} from './Outro';
import {Guides} from './Guides';
import {PersonStage, baseVideoOpacity} from './Person';
import {SpotLayer, restFilter} from './Spotlight';

export const Ad: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const R = vrect(t);
  const Z = vzoom(t);
  const vOp = baseVideoOpacity(t);                  /* نوافذ قصّ الشخص (Person.tsx) تخفي الفيديو الأصلي تحتها */
  const showVideo = t < VEND + OUTRO && R.w > 2 && vOp > 0;   /* وجهه يبقى بالخاتمة داخل نافذة */
  /* ⛔ الصوت يُعرض بالاستوديو فقط — القاعدة ١٩: صوته يخرج كما دخل.
     بالرندر نطلّع صورة صامتة، ثم ffmpeg يلصق voice.wav الأصلي بلا إعادة ترميز. */
  const preview = !getRemotionEnvironment().isRendering;
  const vsrc = staticFile(preview ? 'video.mp4' : 'video444.mp4');
  const vstyle:React.CSSProperties = {position:'absolute', left:0, top:0, width:'100%', height:'100%', objectFit:'cover',
    objectPosition:`50% ${FACE_ANCHOR*100}%`, transform:`scale(${Z})`, transformOrigin:`50% ${FACE_ANCHOR*100}%`};

  return (
    <AbsoluteFill style={{background:T.bg, fontFamily:T.font}}>
      <LiveBG t={t} />
      {/* ⛔ لا تحط zIndex على نافذة الفيديو. حطّيتها 2 عشان تعلو خلفية الخاتمة،
          فصارت تعلو **كل** المكوّنات (z-index:2 يسبق z-index:auto مهما كان ترتيب DOM)
          وأخفت الكابشن والشارة وكل الرسومات بلحظات ملء الشاشة — سطر واحد عطّل نصف الفيديو.
          الترتيب وحده يكفي: الخاتمة قبل الفيديو بـDOM، والباقي بعده. */}
      {showVideo && (
        <div style={{position:'absolute', left:R.x, top:R.y, width:R.w, height:R.h,
          borderRadius:R.r, overflow:'hidden', opacity:vOp,
          boxShadow: R.r > 0.5 ? `0 26px 64px ${rgba(T.ink,0.26)}` : 'none'}}>
          {/* القاعدة ٩٠: الرندر من الوسيط 4:4:4 (لون مطابق) — والمعاينة من 4:2:0 لأن المتصفح يشغّله */}
          <OffthreadVideo src={vsrc} muted style={{...vstyle, filter:restFilter(t)}} />
          {/* الإضاءة الانتقائية (Spotlight.tsx): الهدف يضوي فوق الفيديو المغمّق — بنفس الزوم */}
          <SpotLayer t={t} src={vsrc} vstyle={vstyle} />
          <VideoOverlay t={t} />
        </div>
      )}
      <PersonStage t={t} Behind={(SC as any).BehindPerson} />
      {preview && <Audio src={staticFile('voice.wav')} />}
      {preview && HAS_SFX && <Audio src={staticFile('sfx.wav')} />}
      <Outro t={t} />
      <Badge t={t} />
      <Scenes t={t} />
      <Captions t={t} />
      {GUIDES && <Guides />}
    </AbsoluteFill>
  );
};
