import React from 'react';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import timeline from './timeline.json';

type Scene={id:string;phase:string;title:string;lines:string[];mode:string;silent:boolean;fromFrame:number;frames:number;audio:string};
const COLORS={bg:'#08172b',panel:'#152e48',cyan:'#46d7c1',muted:'#b4c8dd',gold:'#ffc56a',white:'#f5f8ff',line:'#31516e',red:'#ff8194',green:'#7ce0a1',blue:'#69aefc'};
const font='"Noto Sans","Arial Unicode MS","Arial",sans-serif';
const mono='"SFMono-Regular",Consolas,monospace';
const box:React.CSSProperties={background:COLORS.panel,border:'2px solid '+COLORS.line,borderRadius:22,padding:'20px 30px'};
const panel=(text:string,k:number,active:boolean)=><div key={k} style={{...box,fontSize:35,opacity:active?1:.35,transition:'none'}}>{text}</div>;
const tokens=(value:string,border:string,limit:number)=><div style={{display:'flex',gap:16}}>{Array.from(value).map((ch,i)=>
    <div key={i} style={{width:112,height:112,border:'3px solid '+border,background:i<limit?'#20526b':COLORS.panel,borderRadius:18,display:'grid',placeItems:'center',fontFamily:mono,fontSize:68,fontWeight:800}}>{ch}</div>)}</div>;
function Visual({s,frame}:{s:Scene;frame:number}){
 const prog=Math.min(1,frame/Math.max(1,s.frames));
 if(s.mode==='mission')return <div style={{marginTop:50,...box,padding:44}}>
   <div style={{color:COLORS.gold,fontSize:30}}>OUR MISSION</div>
   <div style={{fontSize:48,fontWeight:800,color:COLORS.cyan,margin:'22px 0 42px'}}>PRACTISING PROBLEM-SOLVING SKILLS</div>
   <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:24}}>
   {['01 / HIỂU VẤN ĐỀ','02 / ĐẶT GIẢ THUYẾT','03 / KIỂM CHỨNG','04 / RÚT KINH NGHIỆM'].map((s,i)=>panel(s,i,prog>i*.17))}
   </div></div>;
 if(['ex1','ex2','ex3'].includes(s.mode)){
   const n=Number(s.mode.slice(-1)),input=n===3?'ab':'aa',pattern=n===1?'a':n===2?'a*':'.*';
   return <div style={{display:'flex',flexDirection:'column',gap:48,marginTop:75}}>
     <div style={{display:'flex',gap:60,alignItems:'center'}}><div style={{width:230,color:COLORS.muted,fontSize:34}}>STRING s</div>{tokens(input,COLORS.blue,Math.ceil(prog*input.length))}</div>
     <div style={{display:'flex',gap:60,alignItems:'center'}}><div style={{width:230,color:COLORS.muted,fontSize:34}}>PATTERN p</div>{tokens(pattern,COLORS.cyan,Math.ceil(prog*pattern.length))}</div>
     <div style={{fontSize:52,color:n===1?COLORS.red:COLORS.green,fontWeight:850}}>Output: {n===1?'false':'true'}</div>
     <div style={{fontSize:31,color:COLORS.muted}}>{n===1?'Còn một chữ a chưa khớp — phải khớp TOÀN BỘ.':n===2?'a* có thể dùng chữ a hai lần.':'. khớp một ký tự, * cho phép lặp quy tắc.'}</div>
   </div>;
 }
 if(s.mode==='stats')return <div style={{marginTop:50}}>
   <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:25}}>
   {[['HARD','Difficulty'],['~1.52M','Accepted submissions'],['~4.8M','Submissions'],['32.0%','Acceptance rate']].map(([v,t],i)=>
   <div key={i} style={{...box,padding:35}}><div style={{fontSize:75,fontWeight:800,color:i===0?COLORS.gold:COLORS.cyan}}>{v}</div><div style={{fontSize:27,color:COLORS.muted}}>{t}</div></div>)}</div>
   <div style={{color:COLORS.muted,fontSize:25,marginTop:22}}>Snapshot: 28 Oct 2026 · Submission attempts, not unique people · Source: LeetCode</div></div>;
 if(s.mode==='think'){
   const sec=Math.max(0,10-Math.floor(frame/30));
   return <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',height:570}}>
     <div style={{border:'12px solid '+COLORS.cyan,borderRadius:'50%',width:300,height:300,display:'grid',placeItems:'center',fontSize:158,fontWeight:900,color:COLORS.gold}}>{String(sec).padStart(2,'0')}</div>
     <div style={{fontSize:36,marginTop:46}}>Bạn sẽ bỏ qua a* hay dùng thêm một ký tự?</div>
   </div>;
 }
 if(s.mode==='branch')return <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:38,marginTop:100}}>
     {[['A / BỎ QUA','dfs(i, j+2)'],['B / DÙNG THÊM','dfs(i+1, j)']].map(([t,v],i)=>
     <div key={i} style={{...box,padding:45,borderColor:i?COLORS.cyan:COLORS.gold}}>
     <div style={{color:i?COLORS.cyan:COLORS.gold,fontSize:44,fontWeight:800}}>{t}</div>
     <div style={{fontFamily:mono,fontSize:40,marginTop:50}}>{v}</div></div>)}</div>;
 if(['cache','grid','dp_demo'].includes(s.mode)){
     const states=[[true,false],[true,false],[true,true]];
     return <div style={{marginTop:58}}>
       <div style={{fontSize:30,color:COLORS.muted,marginBottom:20}}>s = "aa", p = "a*" — chỉ những vị trí mẫu hợp lệ j = 0, 2</div>
       <div style={{display:'grid',gridTemplateColumns:'230px 270px 270px',gap:18}}>
         {['','j=0 (a*)','j=2 (end)'].map((v,i)=><div key={i} style={{fontSize:30,color:COLORS.gold}}>{v}</div>)}
         {states.flatMap((row,i)=>[<div key={'l'+i} style={{fontSize:33,color:COLORS.muted}}>i = {i}</div>,...row.map((v,j)=><div key={i+'-'+j} style={{...box,height:98,display:'grid',placeItems:'center',fontSize:31,color:v?COLORS.green:COLORS.red}}>{v?'TRUE':'FALSE'}</div>)])}
       </div><div style={{fontSize:27,color:COLORS.muted,marginTop:22}}>Không có cột j=1: dấu * không phải một mẫu độc lập.</div></div>;
 }
 if(s.mode==='code1'||s.mode==='code2'){
   const code=s.mode==='code1'?['from functools import cache','','@cache','def dfs(i, j):','    if j == len(p):','        return i == len(s)']:['first = i < len(s) and (s[i] == p[j] or p[j] == ".")','if j + 1 < len(p) and p[j + 1] == "*":','    return dfs(i,j+2) or (first and dfs(i+1,j))','return first and dfs(i+1,j+1)'];
   return <div style={{...box,marginTop:60,padding:35,fontFamily:mono}}>
     {code.map((l,i)=><div key={i} style={{fontSize:32,padding:15,background:i===Math.floor(prog*code.length)?'#245366':'transparent',color:i===Math.floor(prog*code.length)?COLORS.cyan:COLORS.white,whiteSpace:'pre'}}>{l}</div>)}
     <div style={{marginTop:28,fontSize:23,color:COLORS.muted,fontFamily:font}}>Lời giải Python 3 hoàn chỉnh: scripts/solution.py</div></div>;
 }
 return <div style={{display:'flex',flexDirection:'column',gap:22,marginTop:48}}>
   {s.lines.map((line,k)=>panel(line,k,frame>=k*9))}
 </div>;
}
function SceneCard({s}:{s:Scene}){
 const frame=useCurrentFrame(),{fps}=useVideoConfig();
 const progress=Math.min(1,frame/Math.max(1,s.frames));
 const offset=interpolate(progress,[0,.12],[24,0],{extrapolateRight:'clamp'});
 return <AbsoluteFill style={{background:COLORS.bg,color:COLORS.white,fontFamily:font,padding:'48px 78px'}}>
   <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
     <div style={{fontSize:29}}><b style={{color:COLORS.cyan}}>KIEU STUDIO</b><span style={{color:COLORS.muted}}> / THE ART OF CODING</span></div>
     <b style={{color:COLORS.gold,fontSize:27}}>LEETCODE #10 · HARD</b>
   </div><div style={{height:2,background:COLORS.line,margin:'28px 0 36px'}}/>
   <div style={{fontSize:30,color:COLORS.cyan}}>{s.phase}</div>
   <h1 style={{fontSize:65,lineHeight:1.13,margin:'20px 0 35px',transform:'translateY('+offset+'px)'}}>{s.title}</h1>
   <Visual s={s} frame={frame}/>
   <div style={{position:'absolute',bottom:40,left:78,right:78,height:4,background:COLORS.line}}>
     <div style={{width:(progress*100)+'%',height:4,background:COLORS.cyan}}/></div>
 </AbsoluteFill>;
}
export function Episode02(){
 const scenes=timeline as Scene[];
 return <AbsoluteFill>{scenes.map(s=><Sequence key={s.id} from={s.fromFrame} durationInFrames={s.frames}>
   <SceneCard s={s}/>
   {s.audio && <Audio src={staticFile(s.audio)}/>}
 </Sequence>)}</AbsoluteFill>;
}
