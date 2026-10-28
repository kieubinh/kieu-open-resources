#!/usr/bin/env python3
"""Offline lower-fidelity REVIEW ONLY MP4, NOT a substitute for Remotion release."""
from __future__ import annotations
import json, re, subprocess, math, wave, shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from config import ROOT,OUT_PREFIX,REVIEW_MP4,find_font
OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
STILLS=OUT/'review_frames';STILLS.mkdir(exist_ok=True)
S=json.loads((ROOT/'src/timeline.json').read_text())
TR=json.loads((ROOT/'src/traces.json').read_text())
WIDTH,HEIGHT=1280,720
BG='#09172b';PANEL='#132c46';BORDER='#315675';TEAL='#57ecd0';AMBER='#ffcc73';WHITE='#f8fbff';MUTED='#bdd0e2';BLUE='#76aaff';RED='#ff8c9e';GREEN='#92eabb'
FONT=find_font('REGULAR');BOLD=find_font('BOLD');MONO=find_font('MONO')
F={n:ImageFont.truetype(BOLD if b else FONT,n) for n,b in [(15,False),(18,False),(20,False),(21,False),(23,True),(25,False),(28,True),(30,True),(32,True),(40,True),(44,True),(48,True)]}

def wrap(d,text,font,width):
 words=str(text).split();lines=[];current=''
 for word in words:
    test=current+' '+word if current else word
    if d.textbbox((0,0),test,font=font)[2]<=width: current=test
    else:
        if current:lines.append(current)
        current=word
 if current:lines.append(current)
 return lines

def text_lines(d,txt,xy,font,color,width,maxlines=3,step=None):
 x,y=xy;lines=wrap(d,txt,font,width)
 if len(lines)>maxlines:raise ValueError(f'Text clipped: {txt[:100]} / {len(lines)} lines > {maxlines}')
 for line in lines:
    d.text((x,y),line,font=font,fill=color,stroke_width=0)
    y+=step or font.size+9
 return y

def pill(d,num,x,y,color,left=False):
 d.rounded_rectangle((x,y,x+90,y+75),radius=12,fill=('#1b4f5c' if left else PANEL),outline=color,width=3)
 s=str(num);bb=d.textbbox((0,0),s,font=F[32]);d.text((x+45-(bb[2]-bb[0])/2,y+15),s,font=F[32],fill=WHITE)

def draw_trace(d,s,frac):
 steps=TR.get(s['trace'] or ('official_1' if s['mode']=='ex1' else 'official_2')) or TR['official_2']
 ix=min(len(steps)-1,int(frac*len(steps))); st=steps[ix]
 y=215
 d.rounded_rectangle((40,215,1240,563),radius=18,fill=PANEL,outline=BORDER,width=2)
 d.text((75,230),f"i = {st['i']}   j = {st['j']}   left_size = {st['leftSize']}   bước {ix+1}/{len(steps)}",font=F[25],fill=AMBER)
 for row,(name,arr,cut,color) in enumerate([('A',st['a'],st['i'],BLUE),('B',st['b'],st['j'],TEAL)]):
   yy=300+row*105;d.text((78,yy+20),name,font=F[40],fill=color)
   x=156
   for k,v in enumerate(arr):
      if k==cut:d.line((x-7,yy-10,x-7,yy+85),fill=AMBER,width=6)
      pill(d,v,x,yy,color,k<cut);x+=104
   if cut==len(arr):d.line((x-7,yy-10,x-7,yy+85),fill=AMBER,width=6)
   if not arr:d.text((x,yy+22),'∅',font=F[32],fill=MUTED)
 d.text((80,526),f"AL={st['AL']}  AR={st['AR']}     BL={st['BL']}  BR={st['BR']}",font=F[25],fill=WHITE)
 verdict={'valid':f"HỢP LỆ · median = {st['median']}",'move_left':'AL > BR · cắt A sang trái','move_right':'BL > AR · cắt A sang phải'}[st['decision']]
 d.text((82,575),verdict,font=F[28],fill=GREEN if st['decision']=='valid' else AMBER)

def draw_scene(s,frac=0,caption='',count=None):
 im=Image.new('RGB',(WIDTH,HEIGHT),BG);d=ImageDraw.Draw(im)
 d.text((40,26),'KIEU STUDIO',font=F[23],fill=TEAL)
 d.text((250,28),'/  THE ART OF CODING',font=F[20],fill=MUTED)
 d.text((1016,28),'LEETCODE #4',font=F[23],fill=AMBER)
 d.line((40,78,1240,78),fill=BORDER,width=2)
 d.text((42,99),s['phase'],font=F[20],fill=TEAL)
 titlefont=F[40] if len(s['title'])>55 else F[44]
 text_lines(d,s['title'],(40,135),titlefont,WHITE,1180,2,titlefont.size+4)
 if s['mode']=='think':
    d.ellipse((526,265,756,495),outline=TEAL,width=12)
    val=f'{count:02}'
    bb=d.textbbox((0,0),val,font=F[48]);d.text(((1280-(bb[2]-bb[0]))/2,345),val,font=F[48],fill=AMBER)
    text_lines(d,'Tự vẽ hai đường cắt và xác định điều kiện hợp lệ.',(260,560),F[25],WHITE,820,2)
 elif s['mode'] in ('ex1','ex2','trace','code_trace','move_left','move_right','edge','partition','bounds','valid'):
    draw_trace(d,s,frac)
 elif s['mode'] in ('code1','code2'):
    code=[
     'a, b = nums1, nums2',
     'if len(a) > len(b): a, b = b, a',
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
     '        if (m+n)%2: return float(max(a_left,b_left))',
     '        return (max(a_left,b_left)+min(a_right,b_right))/2.0',
     '    if a_left > b_right: hi = i - 1',
     '    else: lo = i + 1',
    ]
    source=code[:8] if s['mode']=='code1' else code[7:]
    for i,line in enumerate(source):
        y=230+i*43
        if i==min(len(source)-1,int(frac*len(source))):d.rounded_rectangle((70,y-4,1195,y+36),radius=7,fill='#20516b')
        d.text((100,y),line,font=ImageFont.truetype(MONO,19),fill=WHITE)
 else:
    n=len(s['lines']);space=min(91, int(355/max(1,n)))
    top=233
    for i,line in enumerate(s['lines']):
       y=top+i*space
       d.rounded_rectangle((54,y,1226,y+space-7),radius=12,fill=PANEL,outline=BORDER,width=1)
       d.ellipse((75,y+25,91,y+41),fill=TEAL if i%2==0 else AMBER)
       text_lines(d,line,(112,y+13),F[21],WHITE,1075,2,26)
 if caption:
    d.rounded_rectangle((90,627,1190,686),radius=12,fill='#06101e')
    text_lines(d,caption,(108,633),F[18],WHITE,1060,2,23)
 d.rectangle((40,700,1240,705),fill=BORDER)
 d.rectangle((40,700,40+int(1200*frac),705),fill=TEAL)
 return im

def subs():
 path=OUT/f'{OUT_PREFIX}_REVIEW_ESTIMATED.srt'
 raw=path.read_text(encoding='utf8')
 blocks=re.split(r'\n\s*\n',raw.strip())
 def parse(t):
    a=t.replace(',','').split(':');return int(a[0])*3600+int(a[1])*60+int(a[2])/1000
 parsed=[]
 for block in blocks:
    lines=block.strip().splitlines()
    if len(lines)<3:continue
    start,end=lines[1].split(' --> ')
    parsed.append((parse(start),parse(end),' '.join(lines[2:])))
 return parsed

def render():
 cues=json.loads((ROOT/'src/captions.json').read_text())
 total_frames=S[-1]['fromFrame']+S[-1]['frames']
 records=[]
 image_index=0
 for s in S:
    start=s['fromFrame']; end=start+s['frames']
    if s['silent']:
       for n in range(10):
           path=STILLS/f'frame_{image_index:04d}.png';image_index+=1
           draw_scene(s,n/10,'',10-n).save(path,optimize=True)
           records.append((path,30/30.0,start+n*30,start+(n+1)*30))
       continue
    matches=[c for c in cues if c['sceneId']==s['id']]
    if not matches:raise ValueError('Missing captions for '+s['id'])
    points=[start]+[c['fromFrame'] for c in matches if c['fromFrame']>start]+[end]
    points=sorted(set(points))
    for k,(st,et) in enumerate(zip(points,points[1:])):
       cue=next((c for c in matches if c['fromFrame']<=st<c['toFrame']),None)
       if cue is None: cue=matches[0] if st< matches[0]['fromFrame'] else matches[-1]
       path=STILLS/f'frame_{image_index:04d}.png';image_index+=1
       draw_scene(s,(st-start)/s['frames'],cue['text'],None).save(path,optimize=True)
       records.append((path,(et-st)/30.0,st,et))
 assert records[0][2]==0 and records[-1][3]==total_frames
 for one,two in zip(records,records[1:]):
    assert one[3]==two[2], f'Visual review scene gap/overlap: {one[3]} != {two[2]}'
 assert abs(sum(dur for _,dur,_,_ in records)-total_frames/30)<1e-5
 concat=OUT/'review_frames.ffconcat'
 with concat.open('w') as w:
    w.write('ffconcat version 1.0\n')
    for path,duration,_,_ in records:
        w.write(f"file '{path.resolve()}'\nduration {duration:.8f}\n")
    w.write(f"file '{records[-1][0].resolve()}'\n")
 outfile=OUT/REVIEW_MP4
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-safe','0','-f','concat','-i',str(concat),
    '-vf','fps=2,format=yuv420p','-t',f'{total_frames/30:.4f}',
    '-c:v','libx264','-preset','ultrafast','-crf','26','-movflags','+faststart',str(outfile)]
 subprocess.run(cmd,check=True,timeout=220)
 print(json.dumps({'path':str(outfile),'images':len(records),'duration':total_frames/30,'fps':2},ensure_ascii=False))

def thumbnail():
 s=dict(phase='KIEU STUDIO / THE ART OF CODING',title='LeetCode #4 — MEDIAN',mode='valid',trace='official_2',lines=[],id='thumb')
 im=draw_scene(s,.7,'Hai mảng có thứ tự. Một đường cắt đúng.',None)
 im.save(OUT/f'{OUT_PREFIX}_THUMBNAIL.png',optimize=True)
 print('thumbnail',OUT/f'{OUT_PREFIX}_THUMBNAIL.png')

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--thumb-only',action='store_true');args=p.parse_args()
 SUBS=subs()
 thumbnail()
 if not args.thumb_only:render()
