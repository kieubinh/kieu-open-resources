export const C = {bg: '#09172b', deep: '#0c2039', panel: '#132c46', border: '#315675', teal: '#57ecd0', amber: '#ffcc73', white: '#f8fbff',
  muted: '#bdd0e2', blue: '#76aaff', red: '#ff8c9e', green: '#92eabb', cyan: '#72dce0', dim: '#1b3a58'};
export const accent = (name?: string) => ({teal: C.teal, amber: C.amber, blue: C.blue} as Record<string, string>)[name || 'teal'] || C.teal;
export const sans = '"Noto Sans","DejaVu Sans","Segoe UI","Arial Unicode MS",Arial,sans-serif';
export const mono = '"DejaVu Sans Mono","SFMono-Regular",Menlo,Consolas,monospace';
export const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const ease = (t: number) => 1 - Math.pow(1 - clamp(t), 3);
/** Staged progress: 0 before `a`, 1 after `b`, eased in between. */
export const seg = (p: number, a: number, b: number) => ease((p - a) / (b - a));
export const stagger = (p: number, i: number, step = 0.09, len = 0.18) => ease((p - 0.04 - i * step) / len);
export const fmt = (n: number) => Math.round(n).toLocaleString('de-DE'); // 52.530 — Vietnamese thousands separator
export const box = {background: C.panel, border: `2px solid ${C.border}`, borderRadius: 24} as const;
