import React from 'react';
import {Composition, Still} from 'remotion';
import {Episode} from './Episode';
import {Thumbnail} from './Thumbnail';
import {timeline} from './timeline';

export const Root: React.FC = () => (
  <>
    <Composition id="EP03-WildcardMatching" component={Episode} durationInFrames={timeline.totalFrames} fps={30} width={1920} height={1080} />
    <Still id="EP03-Thumbnail" component={Thumbnail} width={1280} height={720} />
  </>
);
