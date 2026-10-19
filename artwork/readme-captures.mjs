// README captures: crops of the live showcase scenes, dark and light, at 2x.
//
//   python -m http.server 8951 --directory site
//   node artwork/readme-captures.mjs [path/to/chrome-or-edge]
//
// Drives a headless Chromium over the DevTools protocol (Node 22+, no
// dependencies). Reduced motion is emulated, so every scene is already in its
// final static state; LCD text is disabled so edges are grey, not coloured.
// The run stops if any rendered text in a crop lacks a loaded Ioskeley face.
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const SITE = process.env.SITE_URL || 'http://localhost:8951/';
const OUT = new URL('../assets/readme/', import.meta.url);
const SCALE = 2;
const PAD = 40; // canvas margin around each scene, CSS px

// name, viewport width, element to crop
const SCENES = [
  ['Workbench', 1360, '#wb'],
  ['Terminal', 1440, '#tmux'],
];

const BROWSERS = [
  process.argv[2], process.env.CHROME,
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/chromium', '/usr/bin/google-chrome',
].filter(Boolean);
const browser = BROWSERS.find((p) => existsSync(p));
if (!browser) throw new Error('No Chromium found; pass its path as the first argument.');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const port = 9400 + Math.floor(Math.random() * 400);
const profile = mkdtempSync(join(tmpdir(), 'ioskeley-capture-'));
const proc = spawn(browser, ['--headless=new', `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, '--no-first-run', '--hide-scrollbars',
  '--disable-lcd-text', '--force-color-profile=srgb', 'about:blank'], { stdio: 'ignore' });

let target;
for (let i = 0; i < 100 && !target; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    target = list.find((t) => t.type === 'page');
  } catch {}
  if (!target) await sleep(150);
}
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r));
let seq = 0;
const pending = new Map();
ws.addEventListener('message', (m) => {
  const d = JSON.parse(m.data);
  if (pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); }
});
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++seq;
  pending.set(id, (d) => (d.error ? reject(new Error(`${method}: ${d.error.message}`)) : resolve(d.result)));
  ws.send(JSON.stringify({ id, method, params }));
});
const run = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
  return r.result.value;
};

// Every visible text run in the crop must map to a loaded face of the family
// it asks for; document.fonts.check() is not trusted (it passes for missing
// families).
const VERIFY = (sel) => `(async () => {
  await document.fonts.ready;
  const root = document.querySelector(${JSON.stringify(sel)});
  const loaded = new Set([...document.fonts].filter((f) => f.status === 'loaded')
    .map((f) => [f.family.replace(/"/g, ''), f.style, String(f.weight)].join('|')));
  const need = new Set();
  const walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while (walk.nextNode()) {
    const el = walk.currentNode.parentElement;
    if (!walk.currentNode.data.trim() || !el.getClientRects().length) continue;
    const cs = getComputedStyle(el);
    const fam = cs.fontFamily.split(',')[0].trim().replace(/"/g, '');
    need.add([fam, cs.fontStyle === 'normal' ? 'normal' : 'italic', cs.fontWeight].join('|'));
  }
  return [...need].filter((k) => !loaded.has(k));
})()`;

// Bring the scene into view and return its rectangle in page coordinates.
const PLACE = (sel) => `(() => {
  document.documentElement.style.scrollBehavior = 'auto';
  const header = document.querySelector('.site-header');
  if (header) header.style.visibility = 'hidden';
  const el = document.querySelector(${JSON.stringify(sel)});
  el.scrollIntoView({ block: 'center' });
  const b = el.getBoundingClientRect();
  return { x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height };
})()`;

// Settle each editor on a whole line, after the page's own reveal has run, so
// no clipped glyph tails show along its top edge. scrollTop is whole pixels
// and lines are not, so round up past the seam.
const SNAP = `document.querySelectorAll('.wb__scroll').forEach((s) => {
  const first = s.querySelector('.ln');
  if (!first) return;
  const lh = first.getBoundingClientRect().height;
  const pad = first.offsetTop;
  // At the end of a file the reveal is clamped short of a line boundary; one
  // more line of empty padding below the last line gives the snap room.
  const code = s.querySelector('.wb__code');
  code.style.paddingBottom = parseFloat(getComputedStyle(code).paddingBottom) + lh + 'px';
  s.scrollTop = Math.ceil(Math.round((s.scrollTop - pad) / lh) * lh + pad);
})`;

await send('Page.enable');
await send('Runtime.enable');
mkdirSync(OUT, { recursive: true });
try {
  for (const scheme of ['dark', 'light']) {
    for (const [name, width, sel] of SCENES) {
      await send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: SCALE, mobile: false });
      await send('Emulation.setEmulatedMedia', { features: [
        { name: 'prefers-color-scheme', value: scheme },
        { name: 'prefers-reduced-motion', value: 'reduce' }] });
      await send('Page.navigate', { url: SITE });
      await sleep(1500);
      // Walk the page once so lazily loaded faces arrive for every scene.
      const total = await run('document.documentElement.scrollHeight');
      for (let y = 0; y < total; y += 600) { await run(`scrollTo(0, ${y})`); await sleep(60); }
      await sleep(800);
      const r = await run(PLACE(sel));
      await sleep(800);
      await run(SNAP);
      await sleep(200);
      const missing = await run(VERIFY(sel));
      if (missing.length) throw new Error(`${name} (${scheme}): no loaded face for ${missing.join(', ')}`);
      const clip = { x: r.x - PAD, y: r.y - PAD, width: Math.ceil(r.w) + 2 * PAD, height: Math.ceil(r.h) + 2 * PAD, scale: 1 };
      const shot = await send('Page.captureScreenshot', { format: 'png', clip, captureBeyondViewport: true });
      const file = `${name}${scheme === 'light' ? '-Light' : ''}.png`;
      writeFileSync(new URL(file, OUT), Buffer.from(shot.data, 'base64'));
      console.log(`${file}  ${clip.width * SCALE}x${clip.height * SCALE}`);
    }
  }
} finally {
  ws.close();
  // Close through the protocol: on Windows, killing the launcher process
  // leaves its renderer and GPU children running.
  try {
    const { webSocketDebuggerUrl } = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
    const b = new WebSocket(webSocketDebuggerUrl);
    await new Promise((r) => b.addEventListener('open', r));
    const closed = new Promise((r) => b.addEventListener('close', r));
    b.send(JSON.stringify({ id: 1, method: 'Browser.close' }));
    await Promise.race([closed, sleep(5000)]);
  } catch {}
  proc.kill();
  await sleep(500);
  // The browser can hold its profile briefly after exit.
  try { rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); } catch {}
}
