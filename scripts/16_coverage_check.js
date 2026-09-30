/* ═══ الفاحص السابع: لا فراغ طويل ═══
   node 16_coverage_check.js <work> [الحد بالثواني]
   ليش: اشتكى مرتين من مدى طويل بلا شي — «٢٣ ثانية وجه وكابشن بس».
   شلون: يجمع نوافذ كل دوال المشاهد (kN/jN) + مدَيات البي-رول من broll.json،
         ويطلّع أي فجوة أطول من الحد (٤ ثواني افتراضياً)، ويسقط لو التغطية أقل من ٧٠٪.
   ⛔ كان الحد ١٢ ثانية فطلع المقطع «فجوات طويلة والكابشن بس على الشاشة — ممل» (القاعدة ١٣٣).                        */
const fs=require('fs'), path=require('path');
const W=path.resolve(process.argv[2])+path.sep, LIM=Number(process.argv[3]||4), MINCOV=70;
/* المحرّكان: الخفيف يقرأ compose.html، وريموشن يقرأ Scenes.tsx (كل مشهد: const A=…, B=…) — كان الفاحص خفيفاً فقط
   فطلع «ما فيه compose.html» على مشاريع ريموشن */
const REM=fs.existsSync(W+'Scenes.tsx');   // ريموشن هو الافتراضي لو المشاهد موجودة (مجلد الشغل قد يحمل compose.html قديماً)
const src=fs.readFileSync(W+(REM?'Scenes.tsx':'compose.html'),'utf8');
const caps=JSON.parse(fs.readFileSync(W+'caps.json','utf8'));
const DUR=caps.total;
const win=[];
if(REM){
  for(const m of src.matchAll(/const (\w+) = \(\{t[^\n]*\n(?:.*\n){0,6}?\s*const A=([\d.]+), B=([\d.]+);/g))
    if(!['BehindPerson','VideoOverlay','Scenes'].includes(m[1])) win.push([+m[2],+m[3]]);   // طبقات القالب — مو مشاهد
  for(const m of src.matchAll(/<(\w+) t=\{t\} A=\{([\d.]+)\} B=\{([\d.]+)\}/g)) win.push([+m[2],+m[3]]);
} else {
  for(const m of src.matchAll(/function [jk]\d+\(t\)\{[^]*?A=([\d.]+)\s*,\s*B=([\d.]+)/g)) win.push([+m[1],+m[2]]);
}
/* الصورة الخارجية (bleed) والكلام ورا الشخص يحسبان تغطية */
const bk=src.match(/const BK_A=([\d.]+),\s*BK_B=([\d.]+)/); if(bk) win.push([+bk[1],+bk[2]]);
if(fs.existsSync(W+'behind.json'))
  JSON.parse(fs.readFileSync(W+'behind.json','utf8')).lines.forEach(l=>win.push([l.s,l.e]));
/* قصّ الشخص (27_person_layer) — تصغيره أو تغيير خلفيته آلية بحد ذاتها */
if(fs.existsSync(W+'person.json'))
  (JSON.parse(fs.readFileSync(W+'person.json','utf8')).windows||[]).forEach(w=>win.push([w.a,w.b]));
if(fs.existsSync(W+'broll.json'))
  JSON.parse(fs.readFileSync(W+'broll.json','utf8')).ranges.forEach(r=>win.push([r[0],r[1]]));
win.sort((a,b)=>a[0]-b[0]);
const merged=[];
for(const w of win){
  if(merged.length&&w[0]<=merged[merged.length-1][1]+0.01) merged[merged.length-1][1]=Math.max(merged[merged.length-1][1],w[1]);
  else merged.push([...w]);
}
const gaps=[]; let cur=0;
for(const m of merged){ if(m[0]-cur>LIM) gaps.push([+cur.toFixed(2),+m[0].toFixed(2),+(m[0]-cur).toFixed(1)]); cur=Math.max(cur,m[1]); }
if(DUR-cur>LIM) gaps.push([+cur.toFixed(2),+DUR.toFixed(2),+(DUR-cur).toFixed(1)]);
const cov=merged.reduce((a,m)=>a+m[1]-m[0],0)/DUR*100;
console.log(`تغطية: ${cov.toFixed(0)}٪ · ${merged.length} نافذة · الحد ${LIM} ث`);
if(cov<MINCOV){ console.log(`\n❌ التغطية ${cov.toFixed(0)}٪ — أقل من ${MINCOV}٪: وجهه والكابشن بس أغلب المقطع (القاعدة ١٣٣).`); if(!gaps.length) process.exitCode=3; }
if(gaps.length){
  console.log('\n❌ فراغات أطول من الحد:');
  gaps.forEach(g=>console.log(`   ${g[0]} → ${g[1]}   (${g[2]} ث)`));
  console.log('\n⛔ ضِف آلية أو بي-رول (القاعدة ٦٤).'); process.exit(1);
}
console.log('\n✅ ما فيه فراغ أطول من '+LIM+' ثانية.');
