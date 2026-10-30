import React from 'react';
import {Composition,Folder} from 'remotion';
import timeline from './timeline.json';
import {Episode04} from './Episode04';
export const Root:React.FC=()=>{
  const rows=timeline as Array<{fromFrame:number;frames:number}>;
  const duration=rows.length?rows[rows.length-1].fromFrame+rows[rows.length-1].frames:1;
  return <Folder name="Kieu-Studio-Problem-Solving">
    <Composition id="EP04-Median" component={Episode04} width={1920} height={1080} fps={30} durationInFrames={duration}/>
  </Folder>;
};
