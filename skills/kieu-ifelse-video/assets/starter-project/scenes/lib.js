// lib.js — shot templates for EP01 (framing, faces, blueprint art, labels).
import { E, V, S, mood, layer, blurLayer, veil, ease, prog, clamp, lerp, talkAmount, seg, circle, ring, rr, poly, glow, alpha, shade, text, FONTS, rng } from '/engine/core.js';
import { drawFigure, POSES, posesAt, breathe, bigFace } from '/engine/rig2d.js';
import * as UI from '/engine/ui2d.js';

export const drift = (t, dur, z0 = 1, z1 = 1.07, x0 = 0, x1 = -30) => { const k = ease.inOut(clamp(t / dur)); return { z: lerp(z0, z1, k), x: lerp(x0, x1, k), y: 0 }; };
const talking = (i) => talkAmount(i.globalT, i.shot.start, i.shot.end);
export const pose = (p, t) => (typeof p === 'object' ? p : POSES[p] || POSES.stand);

export function figs(g, t, i, M, list, s0 = 1.6, GY) {
  list.forEach((f, n) => {
    const p = Array.isArray(f.p) ? posesAt(t, f.p) : pose(f.p || 'stand', t);
    drawFigure(g, { x: E.W / 2 + (f.x || 0), y: GY + (f.dy || 0), s: f.s || s0, facing: f.f ?? 1, outfit: f.c, pose: f.still ? p : breathe(p, t, 1, n + 1), expr: f.e || 'neutral', talk: f.talk ? talking(i) : 0, look: f.look, prop: f.prop, rot: f.rot, trail: f.trail, blink: (t + n) % 3.1 > 3.0, rim: { color: M.rim, dir: f.dir || [0, -1], w: 4 } });
  });
}
export function scene(g, t, i, set, o) {
  const cam = drift(t, i.dur, o.z0 ?? 1.02, o.z1 ?? 1.09, o.x0 ?? 0, o.x1 ?? -26);
  const { GY, M } = set(g, t, cam, o.set || {});
  layer(g, cam, 1, (g) => { o.back?.(g, GY, M); figs(g, t, i, M, o.figs || [], o.s || 1.6, GY); o.front?.(g, GY, M); });
  o.fx?.(g, t, M, GY);
}
export function face(g, t, i, set, o) {
  let M; blurLayer(g, 14, (g) => { M = set(g, t, { z: 1.4, x: o.bx ?? -100, y: -80 }, o.set || {}).M; }); veil(g, '#0c0810', o.veil ?? 0.42);
  const r = V(300, 330) * (1 + 0.05 * ease.inOut(clamp(t / i.dur)));
  const e = typeof o.e === 'function' ? o.e(t) : o.e;
  bigFace(g, E.W / 2 + (o.x || 0), E.H * V(0.6, 0.55), r, { outfit: o.c, expr: e || 'neutral', talk: o.talk ? talking(i) : 0, look: o.look, rimColor: M.rim, rimSide: o.side || -1, blink: !o.closed && t % 3 > 2.9, tilt: o.tilt });
  o.fx?.(g, t, M);
}
export const T = (g, s, x, y, o = {}) => text(g, s, x, y, { font: FONTS.ui, weight: 900, size: 44, color: S().ui.cream, ...o });
export const gold = () => S().ui.gold, coral = () => S().ui.accent, bpc = () => UI.bpStroke();
export const pop = (t, a = 0, d = 0.35) => ease.outBack(prog(t, a, a + d));
export function card(g, t, str, o = {}) {
  const a = ease.out(prog(t, o.at || 0, (o.at || 0) + 0.3)); if (a <= 0) return;
  const size = o.size || 62, x = o.x ?? E.W / 2, y = o.y ?? E.H * 0.2;
  T(g, str, x, y, { size, color: o.color || gold(), glow: 22, glowColor: alpha(o.color || gold(), 0.65), alpha: a, align: o.align });
}
export function headProfile(g, x, y, s, c, w = 4) {
  g.save(); g.translate(x, y); g.scale(s, s); g.strokeStyle = c; g.lineWidth = w / s; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath();
  g.moveTo(-90, 170); g.lineTo(-96, 96); g.bezierCurveTo(-190, 40, -190, -170, -10, -180); g.bezierCurveTo(120, -186, 170, -80, 150, -20);
  g.lineTo(186, 40); g.lineTo(150, 54); g.lineTo(152, 92); g.lineTo(136, 104); g.bezierCurveTo(140, 140, 110, 140, 66, 132); g.lineTo(60, 172); g.stroke(); g.restore();
}
export function brain(g, x, y, s, c, fill = null) {
  g.save(); g.translate(x, y); g.scale(s, s); g.strokeStyle = c; g.lineWidth = 3.4 / s; g.lineCap = 'round'; g.beginPath();
  g.moveTo(-120, 30); g.bezierCurveTo(-160, -60, -90, -120, -30, -112); g.bezierCurveTo(30, -146, 120, -110, 128, -40); g.bezierCurveTo(166, 0, 130, 60, 80, 56); g.bezierCurveTo(60, 90, 0, 84, -10, 62); g.bezierCurveTo(-50, 86, -110, 76, -120, 30);
  if (fill) { g.fillStyle = fill; g.fill(); } g.stroke();
  for (const q of [[-90, -40, -40, -70, -20, -30], [-60, 20, -10, -20, 40, 10], [10, -90, 40, -50, 90, -60], [50, 30, 90, 0, 110, 20]]) { g.beginPath(); g.moveTo(q[0], q[1]); g.quadraticCurveTo(q[2], q[3], q[4], q[5]); g.stroke(); } g.restore();
}
export function photo(g, x, y, w, h, rot, draw, a = 1) { g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot); rr(g, -w / 2 - 12, -h / 2 - 12, w + 24, h + 44, 4); g.fillStyle = '#e9e2d4'; g.fill(); rr(g, -w / 2, -h / 2, w, h, 2); g.save(); g.clip(); draw(g, w, h); g.restore(); g.restore(); }
export function notes(g, t, x, y, c = '#ffe7b0', n = 7) { const r = rng(9); for (let k = 0; k < n; k++) { const d = r() * 4, ph = (t * 0.5 + r()) % 1, nx = x + (r() - 0.5) * 300 + Math.sin(t * 2 + d) * 18, ny = y - ph * 300; g.save(); g.globalAlpha *= Math.sin(ph * Math.PI); circle(g, nx, ny, 12, c); seg(g, [[nx + 11, ny], [nx + 11, ny - 42], [nx + 30, ny - 32]], 5, c); g.restore(); glow(g, nx, ny, 40, c, 0.18 * Math.sin(ph * Math.PI)); } }
export function hands(g, t, M) {
  const k = ease.out(clamp(t / 1.2)), x = E.W / 2, y = E.H * 0.56;
  seg(g, [[-200, E.H * 0.95], [x - 40 - (1 - k) * 200, y + 10]], 62, '#0e0b12'); seg(g, [[-200, E.H * 0.95], [x - 320, y + 110]], 110, '#2fa7a0');
  seg(g, [[E.W + 200, E.H * 0.9], [x + 56, y - 20]], 54, '#0e0b12'); seg(g, [[E.W + 200, E.H * 0.9], [x + 300, y + 66]], 96, '#8a5ad6');
  circle(g, x + 34, y - 8, 54, '#0e0b12'); circle(g, x - 26 - (1 - k) * 200, y + 8, 60, '#0e0b12'); for (let q = 0; q < 4; q++) circle(g, x - 2 - (1 - k) * 200 + q * 6, y - 34 + q * 22, 18, '#0e0b12');
  seg(g, [[x - 24 - (1 - k) * 200, y - 54], [x + 60, y - 62]], 3, alpha(M.rim, 0.75));
}
export { UI };
