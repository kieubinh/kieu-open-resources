import React from 'react';
import {AbsoluteFill,Audio,Sequence,interpolate,staticFile,useCurrentFrame} from 'remotion';
import timeline from './timeline.json';
import traces from './traces.json';
import captions from './captions.json';

type Scene = {id:string;phase:string;title:string;lines:string[];script:string;fromFrame:number;frames:number;mode:string;silent:boolean;trace:string;audio:string};
type Step = {a:number[];b:number[];lo:number;hi:number;i:number;j:number;AL:number|string;AR:number|string;BL:number|string;BR:number|string;decision:string;median:number|null};
const C={bg:'#09172b',deep:'#0c2039',panel:'#132c46',border:'#315675',teal:'#57ecd0',amber:'#ffcc73',white:'#f8fbff',muted:'#bdd0e2',blue:'#76aaff',red:'#ff8c9e',green:'#92eabb'};
const sans='"DejaVu Sans","FreeSans","Segoe UI",Arial,sans-serif';
const mono='"DejaVu Sans Mono","SFMono-Regular",Consolas,monospace';
const box:React.CSSProperties={background:C.panel,border:`2px solid ${C.border}`,borderRadius:24,padding:'20px 28px'};
const getTrace=(s:Scene):Step[]=>((traces as Record<string,Step[]>)[s.trace]||[]);
const clamp=(v:number,a=0,b=1)=>Math.max(a,Math.min(b,v));

function Pills({values,cut,color,reveal}:{values:number[];cut:number;color:string;reveal:number}){
 return <div style={{display:'flex',gap:12,minHeight:104,alignItems:'center'}}>
 {values.length===0&&<div style={{color:C.muted,fontSize:34}}>∅ (mảng rỗng)</div>}
 {values.map((v,k)=><React.Fragment key={k}>
   {k===cut&&<div style={{height:110,width:7,background:C.amber,borderRadius:6,boxShadow:`0 0 26px ${C.amber}`}}/>}
   <div style={{width:105,height:94,display:'grid',placeItems:'center',background:k<cut?`${color}44`:C.deep,
     border:`3px solid ${color}`,borderRadius:15,fontSize:47,fontWeight:800,
     transform:`translateY(${Math.round((1-clamp(reveal-k*.14))*21)}px)`,opacity:clamp(reveal-k*.14)}}>{v}</div>
  </React.Fragment>)}
 {cut===values.length&&<div style={{height:110,width:7,background:C.amber,borderRadius:6,boxShadow:`0 0 26px ${C.amber}`}}/>}
 </div>;
}
function Boundary({s,frame}:{s:Scene;frame:number}){
 const all=getTrace(s);const choice=all.length?Math.min(all.length-1,Math.floor(frame/(s.frames/Math.max(all.length,1)))):0;
 const step=all[choice] || {a:[2],b:[1,3],i:1,j:1,lo:0,hi:1,AL:2,AR:'+∞',BL:1,BR:3,decision:'valid',median:2};
 const p=clamp(frame/Math.max(s.frames,1)*2);
 const main=step as Step;
 return <div style={{...box,padding:42,marginTop:14}}>
  <div style={{display:'flex',justifyContent:'space-between',fontSize:31,color:C.muted,marginBottom:32}}>
    <span>Khoảng tìm i: [{main.lo}, {main.hi}]</span><b style={{color:C.amber}}>i={main.i} · j={main.j} · bước {choice+1}/{all.length||1}</b>
  </div>
  <div style={{display:'grid',gridTemplateColumns:'170px 1fr',rowGap:30,alignItems:'center'}}>
   <b style={{fontSize:39,color:C.blue}}>A (ngắn)</b><Pills values={main.a} cut={main.i} color={C.blue} reveal={p}/>
   <b style={{fontSize:39,color:C.teal}}>B (dài)</b><Pills values={main.b} cut={main.j} color={C.teal} reveal={p}/>
  </div>
  <div style={{marginTop:42,display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:16}}>
   {([['AL',main.AL],['AR',main.AR],['BL',main.BL],['BR',main.BR]] as Array<[string,number|string]>).map(([name,v],i)=><div key={name} style={{background:C.deep,border:`2px solid ${C.border}`,borderRadius:16,padding:20,textAlign:'center'}}>
     <div style={{fontSize:24,color:C.muted}}>{name}</div><div style={{fontSize:45,fontWeight:800,color:i%2?C.amber:C.white}}>{v}</div>
   </div>)}
  </div>
  <div style={{marginTop:24,fontSize:32,color:main.decision==='valid'?C.green:main.decision==='move_left'?C.red:C.amber,fontWeight:800}}>
    {main.decision==='valid'?`✓ CẮT HỢP LỆ  ·  MEDIAN ${main.median}`:main.decision==='move_left'?'AL > BR  →  DỊCH i SANG TRÁI':'BL > AR  →  DỊCH i SANG PHẢI'}
  </div>
 </div>;
}
const codeLines=[
 'a, b = nums1, nums2',
 'if len(a) > len(b): a, b = b, a',
 'm, n = len(a), len(b)',
 'left_size = (m + n + 1) // 2',
 'lo, hi = 0, m',
 'while lo <= hi:',
 '    i = (lo + hi) // 2',
 '    j = left_size - i',
 '    a_left = a[i-1] if i else float("-inf")',
 '    a_right = a[i] if i < m else float("inf")',
 '    b_left = b[j-1] if j else float("-inf")',
 '    b_right = b[j] if j < n else float("inf")',
 '    if a_left <= b_right and b_left <= a_right:',
 '        if (m+n) % 2:',
 '            return float(max(a_left, b_left))',
 '        return (max(a_left,b_left)+min(a_right,b_right))/2.0',
 '    if a_left > b_right: hi = i - 1',
 '    else: lo = i + 1',
];
function CodeVisual({s,frame}:{s:Scene;frame:number}){
 const start=s.mode==='code1'?0:9;
 const shown=codeLines.slice(start,start+(s.mode==='code1'?9:9));
 const active=Math.min(shown.length-1,Math.floor(frame/Math.max(1,s.frames)*shown.length));
 return <div style={{...box,marginTop:15,padding:'26px 38px',fontFamily:mono}}>
  {shown.map((line,i)=><div key={i} style={{display:'flex',alignItems:'center',gap:28,fontSize:28,minHeight:66,
    padding:'9px 15px',borderRadius:11,background:active===i?'#1d5871':'transparent',color:active===i?C.teal:C.white,whiteSpace:'pre'}}>
     <span style={{color:C.muted,fontSize:23,width:30}}>{start+i+1}</span>{line}
  </div>)}
  <div style={{color:C.muted,fontFamily:sans,fontSize:22,marginTop:16}}>Mã Python 3 đầy đủ: code/solution.py · ký hiệu inf tương ứng float('inf')</div>
 </div>;
}
function GenericVisual({s,frame}:{s:Scene;frame:number}){
 const progress=frame/Math.max(1,s.frames);
 if(s.mode==='stats')return <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:22,marginTop:25}}>
    {(['HARD','46,4%','04/09/2026','Chưa xác minh'] as const).map((n,k)=><div key={n} style={{...box,padding:36}}>
      <div style={{fontSize:k===3?39:62,fontWeight:850,color:k===0?C.amber:C.teal}}>{n}</div>
      <div style={{fontSize:27,color:C.muted}}>{['Difficulty / LeetCode','Acceptance / Leetbot','Ngày cập nhật snapshot','Accepted & total submissions'][k]}</div>
    </div>)}
   </div>;
 if(s.mode==='ex1'||s.mode==='ex2'||s.mode==='trace'||s.mode==='code_trace'||s.mode==='move_left'||s.mode==='move_right'||s.mode==='edge'||s.mode==='partition'||s.mode==='bounds'||s.mode==='valid'){
   if(['edge','partition','bounds','valid'].includes(s.mode)&&!s.trace){
     const key=s.mode==='edge'?'empty':'official_2';return <Boundary s={{...s,trace:key}} frame={frame}/>;
   }
   return <Boundary s={s} frame={frame}/>;
 }
 if(s.mode==='code1'||s.mode==='code2')return <CodeVisual s={s} frame={frame}/>;
 if(s.mode==='think'){
   // 300 exact silent frames, 10.000 seconds, no <Audio/> or background music.
   const remaining=Math.max(0,10-Math.floor(frame/30));
   return <div style={{height:600,display:'flex',justifyContent:'center',alignItems:'center',flexDirection:'column',gap:40}}>
     <div style={{width:315,height:315,borderRadius:'50%',border:`15px solid ${C.teal}`,
       display:'grid',placeItems:'center',fontSize:148,fontWeight:900,color:C.amber}}>{String(remaining).padStart(2,'0')}</div>
     <div style={{fontSize:36,color:C.white,textAlign:'center'}}>Tự vẽ hai đường cắt. Bạn sẽ so sánh bốn số nào?</div>
   </div>;
 }
 if(s.mode==='median')return <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:34,marginTop:45}}>
  {[{t:'TỔNG LẺ',arr:[1,2,3],res:'2.0'},{t:'TỔNG CHẴN',arr:[1,2,3,4],res:'2.5'}].map(item=><div key={item.t} style={{...box,padding:35}}>
      <div style={{fontSize:37,color:C.amber}}>{item.t}</div><div style={{display:'flex',gap:10,margin:'45px 0'}}>{item.arr.map((v,i)=><div key={i} style={{padding:19,background: i===1||item.arr.length===4&&i===2 ? C.teal:C.deep,color:i===1||item.arr.length===4&&i===2?C.bg:C.white,borderRadius:15,fontSize:55,fontWeight:900,flex:1,textAlign:'center'}}>{v}</div>)}</div>
      <div style={{fontSize:57,color:C.teal,fontWeight:900}}>Median = {item.res}</div>
  </div>)}</div>;
 if(s.mode==='practice')return <div style={{display:'flex',gap:30,marginTop:40}}>{s.lines.map((txt,k)=><div key={txt} style={{...box,flex:1,padding:38,display:'flex',flexDirection:'column',gap:45}}>
   <div style={{fontSize:70,fontWeight:900,color:C.amber}}>0{k+1}</div><div style={{fontSize:33,lineHeight:1.35}}>{txt}</div><div style={{color:C.teal,fontSize:26}}>Tự xác định điều kiện trước khi code</div></div>)}</div>;
 return <div style={{display:'flex',flexDirection:'column',gap:22,marginTop:30}}>{s.lines.map((line,k)=><div key={k} style={{...box,opacity:clamp(progress*7-k*.7),transform:`translateX(${(1-clamp(progress*7-k*.7))*25}px)`,fontSize:35,lineHeight:1.35,display:'flex',alignItems:'center',gap:22,padding:'25px 34px'}}>
   <div style={{width:16,height:16,borderRadius:'50%',background:k%2?C.amber:C.teal,flexShrink:0}}/>{line}</div>)}</div>;
}
function Subtitle({s,frame}:{s:Scene;frame:number}){
 if(s.silent||!s.script)return null;
 const absolute=s.fromFrame+frame;
 const cue=(captions as Array<{sceneId:string;fromFrame:number;toFrame:number;text:string}>).find(
   c=>c.sceneId===s.id&&c.fromFrame<=absolute&&c.toFrame>absolute);
 if(!cue)return null;
 return <div style={{position:'absolute',left:270,right:270,bottom:57,background:'#050e1bdc',borderRadius:12,
   textAlign:'center',minHeight:54,padding:'14px 22px',fontSize:29,fontWeight:650,lineHeight:1.34}}>{cue.text}</div>;
}
function SceneCard({s}:{s:Scene}){
 const frame=useCurrentFrame();
 const progress=clamp(frame/Math.max(1,s.frames));
 const entrance=interpolate(progress,[0,.06],[22,0],{extrapolateRight:'clamp'});
 return <AbsoluteFill style={{background:C.bg,color:C.white,fontFamily:sans,padding:'42px 76px'}}>
  <div style={{display:'flex',justifyContent:'space-between',fontSize:27,alignItems:'center'}}>
    <div><b style={{color:C.teal}}>KIEU STUDIO</b><span style={{color:C.muted}}> / THE ART OF CODING</span></div>
    <div style={{color:C.amber,fontWeight:850}}>LEETCODE #4 · HARD</div>
  </div>
  <div style={{background:C.border,height:2,margin:'23px 0 27px'}}/>
  <div style={{fontSize:27,color:C.teal,letterSpacing:.8,fontWeight:700}}>{s.phase}</div>
  <h1 style={{fontSize:61,lineHeight:1.18,letterSpacing:-1,margin:'13px 0 22px',transform:`translateY(${entrance}px)`,maxWidth:1770}}>{s.title}</h1>
  <GenericVisual s={s} frame={frame}/>
  <Subtitle s={s} frame={frame}/>
  <div style={{position:'absolute',bottom:23,left:76,right:76,height:5,background:C.border}}><div style={{width:`${progress*100}%`,background:C.teal,height:5}}/></div>
 </AbsoluteFill>;
}
export function Episode04(){
 const scenes=timeline as Scene[];
 return <AbsoluteFill>{scenes.map(s=><Sequence key={s.id} from={s.fromFrame} durationInFrames={s.frames}>
  <SceneCard s={s}/>{s.audio&&!s.silent&&<Audio src={staticFile(s.audio)}/>}
 </Sequence>)}</AbsoluteFill>;
}
