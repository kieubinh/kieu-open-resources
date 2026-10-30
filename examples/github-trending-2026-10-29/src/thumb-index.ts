import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {Thumb, defaultThumb} from './thumb';
registerRoot(() => React.createElement(Composition, {id: 'Thumb', component: Thumb, width: 1280, height: 720, fps: 30, durationInFrames: 1, defaultProps: defaultThumb}));
