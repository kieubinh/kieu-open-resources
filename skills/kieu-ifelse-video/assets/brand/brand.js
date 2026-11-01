// shots/brand.js — channel banner, avatar and EP01 thumbnail (stills).
import { E, S, registerShot as RS, mood, backdrop, blurLayer, veil, glow, alpha, seg, circle, rr, FONTS, rng } from '/engine/core.js';
import { drawFigure, POSES, bigFace } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import { T, gold, brain } from '../lib.js';
import { bridge } from '../sets/world.js';
import { MINH, BA } from '../cast.js';

const sky = ['#0a1024', '#1a1f4a', '#4a3468', '#c26a5e'];
RS('banner', { draw(g, t) {
  // YouTube keeps only the middle 1546x423 on phones: title and figure stay inside x 507-2053, y 508-932.
  backdrop(g, sky); FX.stars(g, 3, { count: 200, area: [0, 0, E.W, E.H * 0.6] }); glow(g, E.W / 2, E.H * 0.6, 640, '#ffb070', 0.42); FX.hills(g, { y: E.H * 0.635, amp: 16, color: '#141228', seed: 3 });
  drawFigure(g, { x: E.W / 2 + 470, y: E.H * 0.632, s: 0.92, facing: -1, outfit: MINH, pose: POSES.think, expr: 'thinking', rim: { color: '#ffc68a', dir: [0, -1], w: 4 } });
  T(g, 'NẾU NHƯ', E.W / 2 - 80, E.H * 0.452, { size: 128, font: FONTS.title, color: gold(), glow: 34, glowColor: 'rgba(255,140,60,.8)', spacing: 6 });
  T(g, 'Nếu cơ thể bạn hoạt động khác đi thì sao?', E.W / 2 - 80, E.H * 0.55, { size: 36 });
} });
RS('avatar', { draw(g, t) {
  backdrop(g, ['#0a1024', '#1a1f4a', '#3a2c5a']); glow(g, E.W / 2, E.H / 2, 500, '#ffb070', 0.32);
  // YouTube crops the logo to a circle of radius 720 here, so everything sits well inside it.
  bigFace(g, E.W / 2 - 90, E.H * 0.54, 320, { outfit: { top: 'none' }, expr: 'thinking', rimColor: '#ffd59a', rimSide: 1 });
  T(g, '?', E.W / 2 + 265, E.H * 0.285, { size: 250, font: FONTS.title, color: gold(), glow: 34, glowColor: 'rgba(255,140,60,.8)' });
} });
RS('thumb', { draw(g, t) {
  let M; blurLayer(g, 10, (g) => { M = bridge(g, 1, { z: 1.3, x: 0, y: -60 }).M; }); veil(g, '#0a0a18', 0.25); FX.rain(g, 1, { count: 240, a: 0.3 });
  const r = rng(6); for (let k = 0; k < 16; k++) { circle(g, 200 + r() * 620, 120 + r() * 700, 3 + r() * 8, alpha(gold(), 0.6)); }
  bigFace(g, E.W * 0.28, E.H * 0.6, 380, { outfit: MINH, expr: 'cry', rimColor: '#ffd59a', rimSide: 1 });
  bigFace(g, E.W * 0.74, E.H * 0.68, 300, { outfit: BA, expr: 'confused', rimColor: M.rim, rimSide: -1, look: [-0.6, 0] });
  rr(g, E.W * 0.57, 140, 700, 170, 85); g.fillStyle = '#f4efe6'; g.fill(); T(g, 'Cháu là ai?', E.W * 0.57 + 350, 226, { size: 96, color: '#14111a' });
  T(g, 'NHỚ MỌI THỨ', E.W * 0.28, E.H * 0.13, { size: 112, font: FONTS.title, color: gold(), glow: 26, glowColor: 'rgba(255,140,60,.9)' });
} });
