import React from 'react';
import {Composition, Folder} from 'remotion';
import timeline from './timeline.json';
import {GitHubRadar} from './GitHubRadar';
import {GitHubRadarShort} from './GitHubRadarShort';
export const Root: React.FC = () => {
  const rows = timeline as Array<{fromFrame: number; frames: number}>;
  const duration = rows.length ? rows[rows.length - 1].fromFrame + rows[rows.length - 1].frames : 1;
  return <Folder name="Kieu-Studio-GitHub-Radar">
    <Composition id="GitHubRadarShort" component={GitHubRadarShort} defaultProps={{faceVideo: null}} width={1080} height={1920} fps={30} durationInFrames={duration} />
    <Composition id="GitHubRadar" component={GitHubRadar} defaultProps={{faceVideo: null}} width={1920} height={1080} fps={30} durationInFrames={duration} />
  </Folder>;
};
