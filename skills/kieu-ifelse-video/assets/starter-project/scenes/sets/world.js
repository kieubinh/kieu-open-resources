// sets/world.js — all locations of EP01, each anchored to GY/CX with walls and floors past the frame.
import { E, V, mood, layer, backdrop, rr, seg, circle, poly, linGrad, glow, alpha, shade, mix, rng, text, FONTS } from '/engine/core.js';
import * as FX from '/engine/fx2d.js';

const G = () => E.H * V(0.8, 0.68), floor = (g, M, GY, a = -0.1) => { g.fillStyle = linGrad(g, 0, GY, 0, GY + 420, [shade(M.floor, a), shade(M.dark, -0.2)]); g.fillRect(-E.W, GY, E.W * 3, E.H * 2); };

export function street(g, t, cam, o = {}) {
  const M = mood(o.mood || 'golden'), GY = G(), CX = E.W / 2;
  layer(g, cam, 0.15, (g) => { backdrop(g, M.sky); FX.sun(g, CX + 520, GY - 520, 60, '#fff3dc', M.key, 5); FX.clouds(g, { y: GY - 860, h: 180, color: '#ffe7c7', a: 0.14, seed: 3 }); FX.skyline(g, { x: -E.W, y: GY - 420, w: E.W * 3, minH: 80, maxH: 260, color: mix(M.sky[1], M.dark, 0.72), windowColor: alpha(M.practical, 0.5), lit: 0.15, seed: 8 }); });
  layer(g, cam, 0.55, (g) => { let x = -1400; for (let i = 0; i < 12; i++) { const w = 240 + (i * 53) % 120, h = 330 + (i * 97) % 240; FX.facade(g, { x, y: GY, w, h, color: shade(M.wall, -0.32 - (i % 3) * 0.08), win: M.practical, dark: M.dark, cols: 3, rows: 3 + i % 2, lit: 0.45, seed: 20 + i }); x += w + 8; } });
  layer(g, cam, 0.85, (g) => { floor(g, M, GY); g.fillStyle = shade(M.dark, -0.1); g.fillRect(-E.W, GY + 70, E.W * 3, 300); for (let x = -E.W; x < E.W * 2; x += 180) { g.fillStyle = alpha(M.key, 0.35); g.fillRect(x, GY + 170, 90, 6); } FX.lampPost(g, CX - 560, GY, 340, { light: M.practical }); FX.tree(g, CX + 620, GY, 1.4, shade(M.dark, -0.2)); });
  return { GY, CX, M };
}
export function home(g, t, cam, o = {}) {
  const M = mood(o.mood || 'interiorWarm'), GY = G(), CX = E.W / 2, wall = shade(M.wall, -0.3);
  layer(g, cam, 0.2, (g) => backdrop(g, o.mood === 'night' ? M.sky : mood('dusk').sky));
  layer(g, cam, 0.6, (g) => {
    const wx = CX - 330, wy = GY - 610, ww = 660, wh = 430;
    g.fillStyle = linGrad(g, 0, 0, 0, GY, [shade(wall, 0.08), wall, shade(wall, -0.3)]);
    g.fillRect(-E.W, -E.H, wx + E.W, E.H * 3); g.fillRect(wx + ww, -E.H, E.W * 3, E.H * 3); g.fillRect(wx, -E.H, ww, wy + E.H); g.fillRect(wx, wy + wh, ww, E.H * 2);
    FX.windowFrame(g, { x: wx, y: wy, w: ww, h: wh, cols: 3, rows: 2, frame: shade(wall, -0.5), bar: 10 }, (g, x, y, w, h) => { if (o.mood === 'night') FX.moon(g, x + w * 0.7, y + h * 0.3, 34); else FX.sun(g, x + w * 0.65, y + h * 0.72, 46, '#fff3dc', M.key, 4); });
    glow(g, CX, wy + wh / 2, 620, M.key, o.mood === 'night' ? 0.12 : 0.28);
    rr(g, CX - 860, GY - 520, 150, 190, 8); g.fillStyle = shade(wall, -0.45); g.fill(); rr(g, CX - 848, GY - 508, 126, 166, 4); g.fillStyle = alpha(M.practical, 0.28); g.fill(); circle(g, CX - 785, GY - 440, 34, shade(wall, -0.55));
    FX.counter(g, { x: CX + 480, y: GY, w: 900, h: 120, color: shade(wall, -0.5), top: shade(wall, -0.25) });
  });
  layer(g, cam, 0.9, (g) => { floor(g, M, GY); FX.floorLines(g, GY, GY + 500, 'rgba(0,0,0,.22)', 0.08); FX.pool(g, CX, GY + 40, 420, 60, M.key, 0.22); });
  return { GY, CX, M };
}
export function bedroom(g, t, cam, o = {}) {
  const M = mood('night'), GY = G(), CX = E.W / 2;
  layer(g, cam, 0.2, (g) => backdrop(g, M.sky));
  layer(g, cam, 0.6, (g) => {
    const wx = CX + 120, wy = GY - 640, ww = 420, wh = 400, wall = shade(M.wall, -0.2);
    g.fillStyle = linGrad(g, 0, 0, 0, GY, [wall, shade(wall, -0.3)]); g.fillRect(-E.W, -E.H, wx + E.W, E.H * 3); g.fillRect(wx + ww, -E.H, E.W * 3, E.H * 3); g.fillRect(wx, -E.H, ww, wy + E.H); g.fillRect(wx, wy + wh, ww, E.H * 2);
    FX.windowFrame(g, { x: wx, y: wy, w: ww, h: wh, cols: 2, rows: 2, frame: shade(wall, -0.5), bar: 9 }, (g, x, y, w, h) => { FX.stars(g, t, { area: [x, y, w, h], count: 40 }); FX.moon(g, x + w * 0.6, y + h * 0.35, 38); });
    FX.godRays(g, wx + ww / 2, wy + wh / 2, { angle: 2.2, color: M.key, a: 0.05, t, len: 900 });
  });
  layer(g, cam, 0.9, (g) => { floor(g, M, GY); FX.bed(g, { x: CX - 420, y: GY, w: 520, color: '#3a3a70', frame: shade(M.wall, -0.5), pillow: '#a9a8c8' }); FX.pool(g, CX - 80, GY + 40, 380, 50, M.key, 0.16); });
  return { GY, CX, M };
}
export function classroom(g, t, cam, o = {}) {
  const M = mood('interiorCool'), GY = G(), CX = E.W / 2, wall = shade(M.wall, 0.04);
  layer(g, cam, 0.6, (g) => {
    g.fillStyle = linGrad(g, 0, 0, 0, GY, [wall, shade(wall, -0.3)]); g.fillRect(-E.W, -E.H, E.W * 3, E.H * 3);
    rr(g, CX - 560, GY - 610, 1120, 380, 8); g.fillStyle = '#1d3a34'; g.fill(); g.strokeStyle = shade(M.wall, -0.5); g.lineWidth = 12; g.stroke(); glow(g, CX, GY - 420, 600, M.key, 0.08);
    for (const x of [CX - 1040, CX + 720]) FX.windowFrame(g, { x, y: GY - 610, w: 300, h: 380, cols: 2, rows: 2, frame: shade(M.wall, -0.5), bar: 8 }, (g, a, b, w, h) => { g.fillStyle = linGrad(g, 0, b, 0, b + h, [M.sky[1], M.key]); g.fillRect(a, b, w, h); });
    o.board?.(g, CX, GY - 420);
  });
  layer(g, cam, 0.9, (g) => { floor(g, M, GY); FX.floorLines(g, GY, GY + 500, 'rgba(0,0,0,.25)', 0.08); FX.pool(g, CX, GY + 40, 500, 60, M.key, 0.14); });
  return { GY, CX, M };
}
export function market(g, t, cam, o = {}) {
  const M = mood('golden'), GY = G(), CX = E.W / 2;
  layer(g, cam, 0.15, (g) => { backdrop(g, M.sky); FX.skyline(g, { x: -E.W, y: GY - 500, w: E.W * 3, minH: 90, maxH: 280, color: mix(M.sky[1], M.dark, 0.7), windowColor: alpha(M.practical, 0.5), lit: 0.2, seed: 11 }); });
  layer(g, cam, 0.65, (g) => {
    for (let i = -3; i <= 3; i++) { const x = CX + i * 520; rr(g, x - 240, GY - 170, 480, 170, 6); g.fillStyle = shade(M.wall, -0.5); g.fill();
      for (let k = 0; k < 8; k++) { g.fillStyle = k % 2 ? (i % 2 ? '#c9b8a4' : '#d9c26a') : (i % 2 ? '#8f3328' : '#3a6a5a'); g.fillRect(x - 260 + k * 65, GY - 400, 65, 56); g.beginPath(); g.arc(x - 228 + k * 65, GY - 344, 32, 0, Math.PI); g.fill(); }
      for (const q of [-120, 0, 120]) { seg(g, [[x + q, GY - 340], [x + q, GY - 290]], 2, '#111'); circle(g, x + q, GY - 280, 12, '#fff0c8'); glow(g, x + q, GY - 280, 110, M.practical, 0.42); }
      for (let k = 0; k < 9; k++) { const fx = x - 200 + k * 50, fy = GY - 186 - (k % 2) * 10; g.fillStyle = k % 3 ? '#b9c6c8' : '#e3b23c'; g.beginPath(); g.ellipse(fx, fy, 22, 9, 0, 0, 7); g.fill(); } }
  });
  layer(g, cam, 0.9, (g) => { floor(g, M, GY); FX.pool(g, CX, GY + 30, 640, 60, M.practical, 0.2); });
  return { GY, CX, M };
}
export function stage(g, t, cam, o = {}) {
  const M = mood('night'), GY = G(), CX = E.W / 2;
  layer(g, cam, 0.3, (g) => { backdrop(g, ['#05060f', '#0c1030', '#141a44']); });
  layer(g, cam, 0.65, (g) => {
    FX.screen(g, { x: CX - 520, y: GY - 640, w: 1040, h: 380, bg: '#0c1a3a', glowC: '#5fb7ff', a: 0.3 }, (g, x, y, w, h) => { text(g, o.screen || 'CHUNG KẾT', x + w / 2, y + h / 2, { size: 84, color: '#e8f2ff', glow: 24, glowColor: '#5fb7ff' }); });
    for (const k of [-3, -2, -1, 1, 2, 3]) FX.lightCone(g, CX + k * 300, GY - 900, { angle: Math.PI / 2 - k * 0.1, spread: 0.2, len: 1000, color: k % 2 ? '#7fb8ff' : '#ffd59a', a: 0.13 });
  });
  layer(g, cam, 0.9, (g) => { g.fillStyle = linGrad(g, 0, GY, 0, GY + 300, ['#2a2f58', '#0b0d1e']); g.fillRect(-E.W, GY, E.W * 3, E.H * 2); FX.pool(g, CX + (o.spot || 0), GY + 34, 300, 46, '#fff0d0', 0.5); });
  if (o.crowd !== false) layer(g, cam, 1.4, (g) => FX.crowd(g, t, { y: E.H + 60, w: E.W * 1.4, x: -E.W * 0.2, rows: 3, rowH: 34, size: 1.6, color: '#080a18', flags: 0, wave: 0.2 }));
  return { GY, CX, M };
}
export function backstage(g, t, cam, o = {}) {
  const M = mood('interiorCool'), GY = G(), CX = E.W / 2;
  layer(g, cam, 0.6, (g) => { for (let x = -E.W, k = 0; x < E.W * 2; x += 70, k++) { g.fillStyle = k % 2 ? '#3a1420' : '#2a0e18'; g.fillRect(x, -E.H, 70, E.H * 3); } FX.lightCone(g, CX + 420, GY - 700, { angle: 1.9, spread: 0.3, len: 900, color: '#7fb8ff', a: 0.16 }); });
  layer(g, cam, 0.9, (g) => { g.fillStyle = linGrad(g, 0, GY, 0, GY + 300, ['#1a1420', '#0a0810']); g.fillRect(-E.W, GY, E.W * 3, E.H * 2); });
  return { GY, CX, M };
}
export function clinic(g, t, cam, o = {}) {
  const M = mood('interiorCool'), GY = G(), CX = E.W / 2, wall = shade(M.wall, 0.1);
  layer(g, cam, 0.6, (g) => { g.fillStyle = linGrad(g, 0, 0, 0, GY, [wall, shade(wall, -0.25)]); g.fillRect(-E.W, -E.H, E.W * 3, E.H * 3); FX.screen(g, { x: CX - 200, y: GY - 600, w: 400, h: 300, bg: '#16283a', glowC: '#a8d8ff', a: 0.35 }, (g, x, y, w, h) => { g.strokeStyle = '#cfe6ff'; g.lineWidth = 4; g.beginPath(); g.ellipse(x + w / 2, y + h / 2, 110, 90, 0, 0, 7); g.stroke(); circle(g, x + w / 2 + 16, y + h / 2 + 30, 18, 'rgba(255,190,90,.8)'); }); });
  layer(g, cam, 0.9, (g) => { floor(g, M, GY); FX.floorLines(g, GY, GY + 500, 'rgba(0,0,0,.2)', 0.08); });
  return { GY, CX, M };
}
export function bridge(g, t, cam, o = {}) {
  const M = mood('storm'), GY = G(), CX = E.W / 2;
  layer(g, cam, 0.12, (g) => { backdrop(g, M.sky); FX.skyline(g, { x: -E.W, y: GY - 300, w: E.W * 3, minH: 70, maxH: 210, color: shade(M.dark, 0.1), windowColor: alpha(M.practical, 0.45), lit: 0.18, seed: 15 }); });
  layer(g, cam, 0.5, (g) => { g.fillStyle = linGrad(g, 0, GY - 90, 0, GY + 200, [shade(M.dark, 0.15), shade(M.dark, -0.3)]); g.fillRect(-E.W, GY - 90, E.W * 3, 400); for (let k = 0; k < 9; k++) FX.pool(g, CX - 800 + k * 200, GY - 40, 90, 12, M.practical, 0.12); });
  layer(g, cam, 0.9, (g) => {
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 300, ['#3a4068', '#10142a']); g.fillRect(-E.W, GY, E.W * 3, E.H * 2);
    seg(g, [[-E.W, GY - 120], [E.W * 2, GY - 120]], 12, '#c8d0e8'); for (let x = -E.W; x < E.W * 2; x += 90) seg(g, [[x, GY - 120], [x, GY]], 6, '#7c86a8');
    for (const x of [CX - 620, CX + 240]) { FX.lampPost(g, x, GY, 400, { light: M.practical, a: 0.3 }); FX.lightCone(g, x + 34, GY - 410, { angle: Math.PI / 2, spread: 0.4, len: 480, color: M.practical, a: 0.2 }); FX.pool(g, x + 34, GY + 36, 280, 40, M.practical, 0.35); }
  });
  return { GY, CX, M };
}
export function oldBridge(g, t, cam, o = {}) {
  const M = mood('golden'), GY = G(), CX = E.W / 2, c = '#3b2a22';
  layer(g, cam, 0.15, (g) => { backdrop(g, ['#6a4a5e', '#d98a5a', '#f6cf92']); FX.sun(g, CX - 300, GY - 360, 70, '#fff3dc', M.key, 6); FX.hills(g, { y: GY - 220, amp: 50, color: '#6a4a48', seed: 4 }); });
  layer(g, cam, 0.5, (g) => { g.fillStyle = linGrad(g, 0, GY - 60, 0, GY + 300, ['#d99a68', '#5a4050']); g.fillRect(-E.W, GY - 60, E.W * 3, 500); FX.lensStreak(g, CX - 300, GY - 10, 900, '#ffe0b0', 0.3, 4); });
  layer(g, cam, 0.9, (g) => { const pts = []; for (let x = -E.W; x <= E.W * 2; x += 40) pts.push([x, GY + 20 + Math.sin(x * 0.0035) * 22]); seg(g, pts, 13, c); seg(g, pts.map(([x, y]) => [x, y - 100]), 6, c); for (const [x, y] of pts.filter((_, i) => i % 4 === 0)) { seg(g, [[x, y - 100], [x, y + 240]], 7, c); seg(g, [[x - 30, y + 150], [x + 30, y + 60]], 5, c); } FX.tree(g, CX + 700, GY + 120, 2, '#2f2030'); });
  return { GY: GY + 14, CX, M };
}
