import React from 'react';
import {Composition,Folder} from 'remotion';
import {Episode02} from './Episode02';
import timeline from './timeline.json';

export const Root:React.FC=()=>{
  const rows=timeline as {fromFrame:number;frames:number}[];
  const end=rows.length ? rows[rows.length-1].fromFrame+rows[rows.length-1].frames : 1;
  return <Folder name="Kieu Studio — Problem Solving">
    <Composition id="EP02-RegularExpression" component={Episode02}
      width={1920} height={1080} fps={30} durationInFrames={Math.max(1,end)}/>
  </Folder>;
};
