/* ==========================================================================
   Ioskeley Mono — showcase site
   No framework, no syntax-highlighting library. The frozen hierarchy is
   implemented here so the page keeps exact control over which punctuation
   takes Proof Red, and so a visitor pays for no third-party script.

   Every scene is complete static HTML. Scripts only enhance it: tokenising,
   laying out the diff, and the few one-time motions, which are skipped
   entirely under prefers-reduced-motion.
   ========================================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* Set in <head> only when motion is allowed and IntersectionObserver
     exists, so every animated scene can assume both. */
  var motionOK = root.classList.contains('motion');

  /* ------------------------------------------------------------- fonts -- */

  var WEIGHT_FILE = {
    100: 'Thin', 200: 'ExtraLight', 300: 'Light', 350: 'SemiLight', 400: 'Regular',
    500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold', 900: 'Black'
  };
  var WEIGHT_NAME = WEIGHT_FILE;
  var ALL_WEIGHTS = [100, 200, 300, 350, 400, 500, 600, 700, 800, 900];

  /* Regular, Bold and Italic are declared in the stylesheet and preloaded.
     Everything else is declared on demand so a visitor who never scrolls to a
     section never downloads its faces. */
  var declared = { '400|0|0': true, '700|0|0': true, '400|1|0': true };
  function ensureFace(weight, italic, semiCondensed) {
    var key = weight + '|' + (italic ? 1 : 0) + '|' + (semiCondensed ? 1 : 0);
    if (declared[key]) return;
    declared[key] = true;

    var name = WEIGHT_FILE[weight];
    if (!name) return;
    /* Regular is spelled out only for the Normal upright face; the other
       Regulars are IoskeleyMono-Italic and IoskeleyMono-SemiCondensed[Italic]. */
    if (weight === 400 && (italic || semiCondensed)) name = '';
    var family = semiCondensed ? 'IoskeleySC' : 'Ioskeley';
    var file = 'IoskeleyMono-' + (semiCondensed ? 'SemiCondensed' : '') + name + (italic ? 'Italic' : '') + '.woff2';
    var style = document.createElement('style');
    /* Injected into the document, so the path is relative to index.html,
       not to the stylesheet. */
    style.textContent = '@font-face{font-family:' + family +
      ';src:url("fonts/' + file + '") format("woff2");font-weight:' + weight +
      ';font-style:' + (italic ? 'italic' : 'normal') + ';font-display:swap;}';
    document.head.appendChild(style);

    if (document.fonts && document.fonts.load) {
      document.fonts.load((italic ? 'italic ' : '') + weight + ' 16px "' + family + '"').catch(function () {});
    }
  }

  /* Run fn once, when el comes within `margin` of the viewport. */
  function whenNear(el, fn, margin) {
    if (!el) return;
    if (!('IntersectionObserver' in window)) { fn(); return; }
    var io = new IntersectionObserver(function (entries) {
      if (!entries.some(function (e) { return e.isIntersecting; })) return;
      io.disconnect();
      fn();
    }, { rootMargin: margin || '800px 0px' });
    io.observe(el);
  }

  /* Run fn once, when `share` of el is actually on screen. */
  function whenSeen(el, fn, share) {
    if (!el) return;
    if (!('IntersectionObserver' in window)) { fn(); return; }
    var io = new IntersectionObserver(function (entries) {
      if (!entries.some(function (e) { return e.isIntersecting; })) return;
      io.disconnect();
      fn();
    }, { threshold: share || 0.3 });
    io.observe(el);
  }

  /* ------------------------------------------------------------- theme -- */

  var themeLabel = $('#theme-label');
  var themeButton = $('#theme-toggle');

  function isLight() { return root.getAttribute('data-theme') === 'light'; }

  function syncArtwork() {
    var light = isLight();
    $$('img[data-dark][data-light]').forEach(function (img) {
      var next = light ? img.dataset.light : img.dataset.dark;
      if (next && img.getAttribute('src') !== next) img.setAttribute('src', next);
    });
    if (themeLabel) themeLabel.textContent = light ? 'Light' : 'Dark';
    if (themeButton) themeButton.setAttribute('aria-label', 'Switch to ' + (light ? 'dark' : 'light') + ' theme');
  }

  if (themeButton) {
    themeButton.addEventListener('click', function () {
      if (isLight()) root.removeAttribute('data-theme');
      else root.setAttribute('data-theme', 'light');
      try { localStorage.setItem('ioskeley-theme', isLight() ? 'light' : 'dark'); } catch (e) {}
      syncArtwork();
    });
  }

  // Follow the system until the visitor picks a side.
  var mq = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)');
  if (mq && mq.addEventListener) {
    mq.addEventListener('change', function (e) {
      var saved = null;
      try { saved = localStorage.getItem('ioskeley-theme'); } catch (err) {}
      if (saved) return;
      if (e.matches) root.setAttribute('data-theme', 'light');
      else root.removeAttribute('data-theme');
      syncArtwork();
    });
  }

  /* ------------------------------------------------------- tokenizing -- */

  /* Structural punctuation takes Proof Red. Everything else stays neutral. */
  var STRUCTURAL = '{ } [ ] ( ) " \''.split(' ');

  var LANGS = {
    js: {
      line: ['//'], block: [['/*', '*/']], quotes: ['"', "'", '`'],
      keywords: 'const let var function return if else for while do switch case break continue new class extends super this typeof instanceof in of delete void try catch finally throw import export from default async await yield static',
      literals: 'true false null undefined NaN Infinity'
    },
    py: {
      line: ['#'], block: [], quotes: ['"', "'"],
      keywords: 'def class return if elif else for while import from as pass break continue with lambda yield global nonlocal assert del raise try except finally in is not and or async await match case',
      literals: 'True False None self'
    },
    rust: {
      line: ['//'], block: [['/*', '*/']], quotes: ['"'],
      keywords: 'fn let mut const struct enum impl trait pub use mod match if else for while loop return where as in ref self crate super type static move unsafe async await break continue',
      literals: 'true false None Some Ok Err'
    },
    c: {
      line: ['//'], block: [['/*', '*/']], quotes: ['"', "'"],
      keywords: 'int char long short unsigned signed float double void struct union enum typedef static const volatile extern inline return if else for while do switch case break continue sizeof goto register restrict',
      literals: 'NULL true false'
    },
    /* Scene-only languages: the workbench, review and docs use TypeScript,
       the query scene uses SQL. */
    ts: {
      line: ['//'], block: [['/*', '*/']], quotes: ['"', "'", '`'],
      keywords: 'const let var function return if else for while do switch case break continue new class extends super this typeof instanceof in of delete void try catch finally throw import export from default async await yield static type interface implements readonly declare namespace enum keyof as satisfies private public protected',
      literals: 'true false null undefined NaN Infinity'
    },
    sql: {
      line: ['--'], block: [['/*', '*/']], quotes: ["'"],
      keywords: 'SELECT FROM WHERE LEFT RIGHT INNER OUTER JOIN ON AND OR NOT AS GROUP BY ORDER HAVING LIMIT ASC DESC NULLS FIRST LAST interval',
      literals: 'NULL TRUE FALSE'
    }
  };
  var LANG_LABEL = { js: 'JavaScript', py: 'Python', rust: 'Rust', c: 'C' };

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function words(list) {
    var set = {};
    list.split(/\s+/).forEach(function (w) { if (w) set[w] = true; });
    return set;
  }

  var OP_CHARS = '+-*/%=<>!&|^~?';
  var PUNCT_CHARS = '{}()[];,:.';

  /* One pass, longest match first. A delimiter is punctuation and the content
     it encloses keeps its own role — the same split the production artwork
     uses. */
  function tokenize(src, langName) {
    var L = LANGS[langName] || LANGS.js;
    var kw = L._kw || (L._kw = words(L.keywords));
    var lit = L._lit || (L._lit = words(L.literals));
    var out = '';
    var n = src.length;
    var i = 0;

    function span(cls, text) { return '<span class="' + cls + '">' + esc(text) + '</span>'; }
    function mark(ch) {
      return STRUCTURAL.indexOf(ch) > -1 ? span('t-mark', ch) : span('t-punct', ch);
    }

    while (i < n) {
      var c = src.charAt(i);
      var hit = null;

      // line comment
      for (var li = 0; li < L.line.length && !hit; li++) {
        if (src.indexOf(L.line[li], i) === i) {
          var nl = src.indexOf('\n', i);
          hit = ['t-comment', i, nl < 0 ? n : nl];
        }
      }
      // block comment
      for (var bi = 0; bi < L.block.length && !hit; bi++) {
        if (src.indexOf(L.block[bi][0], i) === i) {
          var end = src.indexOf(L.block[bi][1], i + L.block[bi][0].length);
          hit = ['t-comment', i, end < 0 ? n : end + L.block[bi][1].length];
        }
      }
      if (hit) { out += span(hit[0], src.slice(hit[1], hit[2])); i = hit[2]; continue; }

      // string literal, delimiters split from content
      if (L.quotes.indexOf(c) > -1) {
        var j = i + 1;
        var closed = -1;
        while (j < n) {
          if (src.charAt(j) === '\\') { j += 2; continue; }
          if (src.charAt(j) === c) { closed = j; break; }
          if (src.charAt(j) === '\n' && c !== '`') break;   // unterminated
          j++;
        }
        if (closed > -1) {
          out += mark(c) + span('t-string', src.slice(i + 1, closed)) + mark(c);
          i = closed + 1;
        } else {
          out += span('t-string', src.slice(i, j));
          i = j;
        }
        continue;
      }

      // number
      var num = /^(?:0[xX][0-9a-fA-F_]+|\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(src.slice(i));
      if (num && !/[\w]/.test(src.charAt(i - 1) || '')) {
        out += span('t-number', num[0]);
        i += num[0].length;
        continue;
      }

      // word
      var word = /^[A-Za-z_][A-Za-z0-9_]*/.exec(src.slice(i));
      if (word) {
        var w = word[0];
        out += kw[w] ? span('t-keyword', w) : (lit[w] ? span('t-number', w) : esc(w));
        i += w.length;
        continue;
      }

      // operator, then single-character punctuation
      if (OP_CHARS.indexOf(c) > -1) {
        var op = '';
        while (i < n && OP_CHARS.indexOf(src.charAt(i)) > -1) op += src.charAt(i++);
        out += span('t-operator', op);
        continue;
      }
      if (PUNCT_CHARS.indexOf(c) > -1) { out += mark(c); i++; continue; }

      out += esc(c);
      i++;
    }
    return out;
  }

  /* ---------------------------------------------------------- samples -- */

  var SAMPLES = {
    js: [
      {
        label: 'Config',
        code: [
          '// Ioskeley Mono — programming specimen',
          'import { readFile } from "node:fs/promises";',
          '',
          'const CONFIG = {',
          '  family: "Ioskeley Mono",',
          '  widths: ["Normal", "SemiCondensed"],',
          '  metrics: { cap: 690, xHeight: 520, advance: 600 },',
          '};',
          '',
          'export async function resolve(path) {',
          '  if (path === \'\') {',
          '    throw new TypeError("empty path");',
          '  }',
          '  const raw = await readFile(path, "utf8");',
          '  return Object.keys(CONFIG.metrics).map((key) => [key, raw]);',
          '}'
        ].join('\n')
      },
      {
        label: 'Parse',
        code: [
          'export function tokenize(line) {',
          '  const out = [];',
          '  let depth = 0;',
          '',
          '  for (const ch of line) {',
          '    if (ch === "{" || ch === "(" || ch === "[") depth += 1;',
          '    if (ch === "}" || ch === ")" || ch === "]") depth -= 1;',
          '    if (ch === "/" && depth === 0) break;',
          '    out.push(ch);',
          '  }',
          '  return out.join("");',
          '}'
        ].join('\n')
      }
    ],
    py: [
      {
        label: 'Metrics',
        code: [
          '# Ioskeley Mono — programming specimen',
          'from dataclasses import dataclass',
          '',
          '@dataclass',
          'class Metrics:',
          '    cap: int = 690',
          '    x_height: int = 520',
          '    advance: int = 600',
          '',
          'def ratio(m: Metrics) -> float:',
          "    if m.cap == '' or m.cap == 0:",
          '        return 0.0',
          '    return m.x_height / m.cap',
          '',
          'print(f"ratio: {ratio(Metrics()):.3f}")'
        ].join('\n')
      },
      {
        label: 'Tables',
        code: [
          'WEIGHTS = [100, 200, 300, 350, 400, 500, 600, 700, 800, 900]',
          '',
          '',
          'def table(rows: dict) -> list:',
          '    out = []',
          '    for name, value in rows.items():',
          '        if value <= 0:',
          '            continue',
          '        out.append((name, value, f"{value / 1000:.2f}"))',
          '    return sorted(out, key=lambda row: row[1])'
        ].join('\n')
      }
    ],
    rust: [
      {
        label: 'Struct',
        code: [
          '// Ioskeley Mono — programming specimen',
          'use std::collections::HashMap;',
          '',
          'pub struct Metrics {',
          '    pub cap: u16,',
          '    pub x_height: u16,',
          '    pub advance: u16,',
          '}',
          '',
          'impl Metrics {',
          '    pub fn ratio(&self) -> f32 {',
          '        if self.cap == 0 {',
          '            return 0.0;',
          '        }',
          '        self.x_height as f32 / self.cap as f32',
          '    }',
          '}',
          '',
          'pub fn build(rows: &[(&str, u16)]) -> HashMap<String, Metrics> {',
          '    rows.iter().map(|(k, v)| (k.to_string(), *v)).collect()',
          '}'
        ].join('\n')
      },
      {
        label: 'Iter',
        code: [
          "fn longest<'a>(items: &[&'a str]) -> Option<&'a str> {",
          "    let mut best: Option<(&'a str, usize)> = None;",
          '',
          '    for item in items {',
          '        let len = item.chars().count();',
          '        if len == 0 {',
          '            continue;',
          '        }',
          '        match best {',
          '            Some((_, prev)) if prev >= len => {}',
          '            _ => best = Some((item, len)),',
          '        }',
          '    }',
          '',
          '    best.map(|(item, _)| item)',
          '}'
        ].join('\n')
      }
    ],
    c: [
      {
        label: 'Header',
        code: [
          '/* Ioskeley Mono — programming specimen */',
          '#include <stdint.h>',
          '',
          'typedef struct {',
          '    uint16_t cap;      /* declared metric, not ink bounds */',
          '    uint16_t x_height;',
          '    uint16_t advance;',
          '} ioskeley_metrics_t;',
          '',
          'int32_t ioskeley_ratio(ioskeley_metrics_t m) {',
          '    if (m.cap == 0) {',
          '        return 0;',
          '    }',
          '    return (int32_t)((m.x_height * 1000) / m.cap);',
          '}'
        ].join('\n')
      },
      {
        label: 'Buffer',
        code: [
          '#include <stdlib.h>',
          '#include <string.h>',
          '',
          'char *duplicate(const char *src) {',
          '    size_t len;',
          '    char *out;',
          '',
          '    if (src == NULL || src[0] == \'\\0\') {',
          '        return NULL;',
          '    }',
          '    len = strlen(src);',
          '    out = (char *)malloc(len + 1);',
          '    if (out == NULL) {',
          '        return NULL;',
          '    }',
          '    memcpy(out, src, len + 1);',
          '    return out;',
          '}'
        ].join('\n')
      }
    ]
  };


  /* ----------------------------------------------------------- editor -- */

  var editor = $('#editor');
  var input = $('#editor-input');
  var highlight = $('#editor-hl');
  var sampleBar = $('#samples');
  var metaLine = $('#editor-meta');
  var advLine = $('#editor-adv');

  var state = { lang: 'js', weight: 400, style: 'normal', width: 'normal', size: 14.5, liga: 'common-ligatures contextual' };

  function renderSamples() {
    if (!sampleBar) return;
    sampleBar.innerHTML = SAMPLES[state.lang].map(function (s, i) {
      return '<button class="seg__btn" type="button" data-sample="' + i + '" aria-pressed="' + (i === 0) + '">' + esc(s.label) + '</button>';
    }).join('');
  }

  /* The textarea is the only scroller: wheel, scrollbars, caret movement and
     find-in-page all move it. The highlight layer is clipped by the editor box
     and follows by the same offset, applied in the scroll event, which runs in
     the frame that scrolled. */
  var hlLayer = highlight && highlight.parentNode;
  function syncHighlight() {
    if (!input || !hlLayer) return;
    hlLayer.style.transform = 'translate(' + -input.scrollLeft + 'px,' + -input.scrollTop + 'px)';
  }

  function paint() {
    if (!input || !highlight) return;
    highlight.innerHTML = tokenize(input.value, state.lang);
    syncHighlight();
  }

  function loadSample(i) {
    var s = SAMPLES[state.lang][i];
    if (!s || !input) return;
    input.value = s.code;
    input.scrollTop = 0;
    input.scrollLeft = 0;
    paint();
  }

  if (editor) {
    renderSamples();
    loadSample(0);

    input.addEventListener('input', paint);
    input.addEventListener('scroll', syncHighlight, { passive: true });
    if ('ResizeObserver' in window) new ResizeObserver(syncHighlight).observe(input);
    /* Tab is left to the browser so the keyboard never gets stuck here;
       Escape simply drops focus. */
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') input.blur();
    });

    if (sampleBar) {
      sampleBar.addEventListener('click', function (e) {
        var btn = e.target.closest('[data-sample]');
        if (!btn) return;
        $$('[data-sample]', sampleBar).forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
        loadSample(parseInt(btn.dataset.sample, 10));
      });
    }
  }

  /* ------------------------------------------------------- controls -- */

  var WEIGHT_LABEL = { 300: 'Light', 400: 'Regular', 500: 'Medium', 700: 'Bold' };

  function applyEditor() {
    if (!editor) return;
    var sc = state.width === 'sc';
    var italic = state.style === 'italic';
    /* Keywords are always Bold in the chosen style, and comments always
       Italic at the chosen weight, so those faces follow the width, weight
       and style: Regular + Italic needs Bold Italic for its keywords, and
       Bold needs Bold Italic for its comments. Nothing is synthesised. */
    ensureFace(state.weight, italic, sc);
    ensureFace(700, italic, sc);
    ensureFace(state.weight, true, sc);
    editor.style.setProperty('--editor-family', (sc ? 'IoskeleySC, ' : '') + 'Ioskeley, ui-monospace, monospace');
    editor.style.setProperty('--editor-size', state.size + 'px');
    /* Inline layout rounds every highlight span up to 1/64 px, which adds up
       over a long line while the textarea lays its text out as one run. Snap
       the cell advance (0.6 em Normal, 0.54 em SemiCondensed) and the line
       height to that grid so both layers step identically. */
    var adv = state.size * (sc ? 0.54 : 0.6);
    editor.style.setProperty('--editor-ls', (Math.round(adv * 64) / 64 - adv).toFixed(6) + 'px');
    editor.style.setProperty('--editor-lh', (Math.round(state.size * 1.7 * 64) / 64) + 'px');
    editor.style.setProperty('--editor-weight', String(state.weight));
    editor.style.setProperty('--editor-style', state.style);
    editor.style.setProperty('--editor-liga', state.liga);
    if (metaLine) {
      metaLine.textContent = 'Ioskeley Mono · ' + (sc ? 'SemiCondensed' : 'Normal') + ' · ' +
        WEIGHT_LABEL[state.weight] + ' ' + state.weight + ' · ' + LANG_LABEL[state.lang];
    }
    if (advLine) advLine.textContent = (sc ? '540' : '600') + ' units/char';
    /* Metrics changed, so the scroll range did too. */
    syncHighlight();
  }

  /* One handler for every segmented control on the page. */
  function wireSeg(name, onPick) {
    $$('[data-control="' + name + '"]').forEach(function (group) {
      group.addEventListener('click', function (e) {
        var btn = e.target.closest('.seg__btn');
        if (!btn || !group.contains(btn)) return;
        $$('.seg__btn', group).forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
        onPick(btn.dataset.value, btn, group);
      });
    });
  }

  wireSeg('width', function (v) { state.width = v; applyEditor(); });
  wireSeg('weight', function (v) { state.weight = parseInt(v, 10); applyEditor(); });
  wireSeg('style', function (v) { state.style = v; applyEditor(); });
  wireSeg('ligatures', function (v) {
    state.liga = v === 'on' ? 'common-ligatures contextual' : 'none';
    applyEditor();
  });
  wireSeg('language', function (v) {
    state.lang = v;
    renderSamples();
    loadSample(0);
    applyEditor();
  });

  var sizeInput = $('#ctl-size');
  var sizeValue = $('#size-value');
  if (sizeInput) {
    sizeInput.addEventListener('input', function () {
      state.size = parseFloat(sizeInput.value);
      if (sizeValue) sizeValue.textContent = state.size + 'px';
      applyEditor();
    });
  }

  /* The lab's own faces are only fetched once the visitor gets near it. */
  whenNear(editor, applyEditor, '600px 0px');

  /* ------------------------------------------------- scene code blocks -- */

  /* Static code in the scenes is tokenised in place. Workbench editors also
     get line numbers, the current line, one diagnostic and the caret. */
  function enhanceCode(pre) {
    var lang = pre.getAttribute('data-code');
    var src = pre.textContent;
    if (!pre.classList.contains('wb__code')) {
      pre.innerHTML = tokenize(src, lang);
      return;
    }
    var current = parseInt(pre.dataset.current || '0', 10);
    var caret = parseInt(pre.dataset.caret || '0', 10);
    var diag = (pre.dataset.diag || '').split(':');
    var diagLine = parseInt(diag[0] || '0', 10);
    var diagWord = diag[1] || '';
    var diagMsg = diag.slice(2).join(':');

    pre.innerHTML = src.split('\n').map(function (line, i) {
      var n = i + 1;
      var html = tokenize(line, lang);
      if (n === diagLine && diagWord) {
        html = html.replace(new RegExp('\\b' + diagWord + '\\b'), '<span class="diag">' + diagWord + '</span>') +
          '<span class="ghost">   ' + esc(diagMsg) + '</span>';
      }
      if (n === caret) html += '<span class="caret"></span>';
      return '<span class="ln' + (n === current ? ' is-current' : '') + '" data-n="' + n + '">' + (html || ' ') + '</span>';
    }).join('');
  }
  $$('pre[data-code]').forEach(enhanceCode);

  /* ---------------------------------------------------------- workbench -- */

  var wb = $('#wb');
  var wbFace = $('#wb-face');
  var wbState = { width: 'normal', weight: 400 };

  /* Editors scroll like real viewports: keep the current line in view,
     snapped to whole lines so none is cut at the top edge. Lines are a
     fractional 13 × 1.6 px, so the snap uses the measured height (not the
     rounded offsetHeight) from the first line's top, and never asks for more
     than the scroller can reach. scrollTop is whole pixels: rounding up lands
     in the next line's blank half-leading, never in a glyph. */
  function revealCurrentLine() {
    $$('.wb__scroll').forEach(function (s) {
      var lines = $$('.ln', s);
      var idx = lines.indexOf($('.ln.is-current', s));
      var lh = lines.length ? lines[0].getBoundingClientRect().height : 0;
      if (idx < 0 || !lh) { s.scrollTop = 0; return; }
      var origin = lines[0].offsetTop;
      var max = s.scrollHeight - s.clientHeight;
      var last = Math.floor((max - origin) / lh);
      if (Math.ceil(origin + last * lh) > max) last--;
      var k = Math.min(last, Math.round(idx - s.clientHeight * 0.6 / lh));
      s.scrollTop = k > 0 ? Math.ceil(origin + k * lh) : 0;
    });
  }

  function applyWorkbench() {
    if (!wb) return;
    var sc = wbState.width === 'sc';
    var w = wbState.weight;
    ensureFace(w, false, sc);
    ensureFace(w, true, sc);
    ensureFace(400, false, sc);
    ensureFace(700, false, sc);
    wb.style.setProperty('--wb-family', (sc ? 'IoskeleySC, ' : '') + 'Ioskeley, ui-monospace, monospace');
    wb.style.setProperty('--wb-weight', String(w));
    if (wbFace) wbFace.textContent = 'Ioskeley Mono · ' + (sc ? 'SemiCondensed' : 'Normal') + ' · ' + WEIGHT_NAME[w] + ' ' + w;
  }

  if (wb) {
    wireSeg('wb-width', function (v) { wbState.width = v; applyWorkbench(); });
    wireSeg('wb-weight', function (v) { wbState.weight = parseInt(v, 10); applyWorkbench(); });
    revealCurrentLine();
    whenSeen(wb, function () { wb.classList.add('is-live'); }, 0.25);

    /* Split divider: pointer drag, plus arrows / Home / End from the
       keyboard. Double-click restores the default. */
    var editors = $('#wb-editors');
    var divider = $('#wb-divider');
    var setSplit = function (p) {
      p = Math.max(35, Math.min(75, p));
      wb.style.setProperty('--split', p + '%');
      divider.setAttribute('aria-valuenow', String(Math.round(p)));
    };
    if (editors && divider) {
      divider.addEventListener('pointerdown', function (e) {
        divider.setPointerCapture(e.pointerId);
        divider.classList.add('is-dragging');
        e.preventDefault();
      });
      divider.addEventListener('pointermove', function (e) {
        if (!divider.classList.contains('is-dragging')) return;
        var r = editors.getBoundingClientRect();
        setSplit((e.clientX - r.left) / r.width * 100);
      });
      ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (ev) {
        divider.addEventListener(ev, function () { divider.classList.remove('is-dragging'); });
      });
      divider.addEventListener('dblclick', function () { setSplit(58); });
      divider.addEventListener('keydown', function (e) {
        var v = parseFloat(divider.getAttribute('aria-valuenow'));
        var step = e.shiftKey ? 10 : 2;
        if (e.key === 'ArrowLeft') setSplit(v - step);
        else if (e.key === 'ArrowRight') setSplit(v + step);
        else if (e.key === 'Home') setSplit(35);
        else if (e.key === 'End') setSplit(75);
        else return;
        e.preventDefault();
      });
    }
  }

  /* ----------------------------------------------------------- terminal -- */

  /* One command types, its output resolves, the replay bar fills: once. */
  var tmux = $('#tmux');
  /* Markup, not text: the run of full blocks sits in .bar__fill (see CSS). */
  function barText(f, total) {
    var cells = 30;
    var whole = Math.floor(f * cells);
    var rem = f * cells - whole;
    var s = (rem ? ' ▏▎▍▌▋▊▉'.charAt(Math.min(7, Math.round(rem * 8))) : '');
    while (whole + s.length < cells) s += ' ';
    var pct = String(Math.round(f * 100));
    var done = String(Math.round(f * total));
    return '[<span class="bar__fill">' + new Array(whole + 1).join('█') + '</span>' + s + ']  ' +
      ('  ' + pct).slice(-Math.max(2, pct.length)) + '%  ' + ('    ' + done).slice(-4) + '/' + total;
  }

  if (motionOK && tmux) {
    var typed = $('.type', tmux);
    var output = $('.type-out', tmux);
    var bar = $('.bar', tmux);
    var command = typed ? typed.dataset.type : '';
    var barFinal = bar ? bar.innerHTML : '';
    var barTo = bar ? parseFloat(bar.dataset.bar) : 0;
    var barTotal = bar ? parseInt(bar.dataset.total, 10) : 0;

    whenNear(tmux, function () {
      if (typed) typed.textContent = '';
      if (output) output.style.visibility = 'hidden';
      if (bar) bar.innerHTML = barText(0, barTotal);
      tmux.classList.add('is-typing');

      whenSeen(tmux, function () {
        var i = 0;
        (function typeNext() {
          if (!typed || i >= command.length) {
            setTimeout(function () {
              if (output) output.style.visibility = '';
              tmux.classList.remove('is-typing');
            }, 220);
            return;
          }
          typed.textContent = command.slice(0, ++i);
          setTimeout(typeNext, 42 + Math.random() * 40);
        })();

        if (bar) {
          var t0 = null;
          var run = function (t) {
            if (t0 === null) t0 = t;
            var k = Math.min(1, (t - t0) / 1600);
            var eased = 1 - Math.pow(1 - k, 2);
            bar.innerHTML = k < 1 ? barText(barTo * eased, barTotal) : barFinal;
            if (k < 1) requestAnimationFrame(run);
          };
          setTimeout(function () { requestAnimationFrame(run); }, 300);
        }
      }, 0.35);
    }, '300px 0px');
  }

  /* ------------------------------------------------------------- review -- */

  /* Lay the unified diff out as rows with old/new line numbers. The raw diff
     stays in the HTML for anyone without scripts. */
  var diffPre = $('#diff');
  var thread = $('#thread');
  if (diffPre) {
    var lines = diffPre.textContent.split('\n');
    var oldN = 0, newN = 0;
    var rows = [];
    var row = function (kind, o, n, sign, code, tokens) {
      return '<div class="dr dr--' + kind + '"' + (n !== '' ? ' data-new="' + n + '"' : '') + '>' +
        '<span class="dr__n">' + o + '</span><span class="dr__n">' + n + '</span>' +
        '<span class="dr__s">' + sign + '</span>' +
        '<span class="dr__c">' + (tokens ? tokenize(code, 'ts') : esc(code)) + '</span></div>';
    };
    lines.forEach(function (l) {
      var m = /^@@ -(\d+),\d+ \+(\d+),\d+ @@/.exec(l);
      if (m) {
        oldN = parseInt(m[1], 10);
        newN = parseInt(m[2], 10);
        rows.push(row('hunk', '', '', '', l, false));
        return;
      }
      if (/^index /.test(l)) { rows.push(row('meta', '', '', '', l, false)); return; }
      if (/^(diff |--- |\+\+\+ )/.test(l)) return;
      var sign = l.charAt(0);
      var code = l.slice(1);
      if (sign === '+') rows.push(row('add', '', newN++, '+', code, true));
      else if (sign === '-') rows.push(row('del', oldN++, '', '−', code, true));
      else rows.push(row('ctx', oldN++, newN++, '', code, true));
    });
    diffPre.innerHTML = rows.join('');
    diffPre.classList.add('is-rows');

    if (thread) {
      var anchor = $('.dr[data-new="' + thread.dataset.afterNew + '"]', diffPre);
      if (anchor) {
        anchor.classList.add('is-commented');
        anchor.insertAdjacentElement('afterend', thread);
      }
    }
  }

  /* -------------------------------------------------------------- proof -- */

  /* The receipt feeds out from under the printer line once. */
  var receipt = $('#receipt');
  if (motionOK && receipt) {
    whenNear(receipt, function () {
      receipt.classList.add('is-loaded');
      whenSeen(receipt.parentNode, function () {
        requestAnimationFrame(function () { receipt.classList.add('is-printed'); });
      }, 0.3);
    }, '400px 0px');
  }

  /* ------------------------------------------------- faces on approach -- */

  whenNear($('#logs'), function () { ensureFace(400, false, true); ensureFace(700, false, true); });
  whenNear($('#docs'), function () { ensureFace(300, false, false); });
  whenNear($('#width'), function () { ensureFace(400, false, true); });

  /* ---------------------------------------------------------- weights -- */

  var weightsList = $('#weights-list');
  var weightStyle = 'normal';
  var weightWidth = 'normal';
  var WEIGHT_TEXT = 'Handgloves 0123 {glyphs} =&gt;';

  function renderWeights() {
    if (!weightsList) return;
    var sc = weightWidth === 'sc';
    weightsList.innerHTML = ALL_WEIGHTS.map(function (w) {
      return '<div class="weight-row">' +
        '<span class="weight-row__name">' + WEIGHT_NAME[w] + '</span>' +
        '<span class="weight-row__css">' + w + '</span>' +
        '<span class="weight-row__demo" style="font-weight:' + w + ';' +
        (weightStyle === 'italic' ? 'font-style:italic;' : '') +
        (sc ? 'font-family:var(--sc);' : '') + '">' + WEIGHT_TEXT + '</span>' +
        '</div>';
    }).join('');
    ALL_WEIGHTS.forEach(function (w) { ensureFace(w, weightStyle === 'italic', sc); });
  }

  wireSeg('weight-style', function (v) { weightStyle = v; renderWeights(); });
  wireSeg('weight-width', function (v) { weightWidth = v; renderWeights(); });

  whenNear($('#weights'), renderWeights, '1200px 0px');

  /* ---------------------------------------------------------- origins -- */

  var ORIGINS = [
    { file: 'Origins-01-Character-Forms', title: '01 · Character forms', alt: 'Character forms of Ioskeley Mono and TX-02 set beside one another for study' },
    { file: 'Origins-02-Overlay-Study', title: '02 · Overlay study', alt: 'Overlay plot of Ioskeley Mono and TX-02 outlines showing where the forms agree and diverge' },
    { file: 'Origins-03-Code-Texture', title: '03 · Code texture', alt: 'The same code sample set in Ioskeley Mono and TX-02 for comparison of colour and rhythm' }
  ];

  var originsGrid = $('#origins-grid');
  var originsDetails = $('#origins-details');
  var originsBuilt = false;

  function buildOrigins() {
    if (originsBuilt || !originsGrid) return;
    originsBuilt = true;
    var light = isLight();
    originsGrid.innerHTML = ORIGINS.map(function (o, i) {
      return '<figure class="plate">' +
        '<img src="imgs/' + o.file + (light ? '-Light' : '') + '.png" ' +
        'data-dark="imgs/' + o.file + '.png" ' +
        'data-light="imgs/' + o.file + '-Light.png" ' +
        'alt="' + esc(o.alt) + '" loading="lazy" decoding="async" width="1280" height="640">' +
        '<figcaption class="plate__cap"><span>' + esc(o.title) + '</span>' +
        '<button class="plate__open" type="button" data-plate="' + i + '">Enlarge</button></figcaption>' +
        '</figure>';
    }).join('');
    syncArtwork();
  }

  if (originsDetails) {
    originsDetails.addEventListener('toggle', function () {
      if (originsDetails.open) buildOrigins();
    });
  }

  /* --------------------------------------------------------- lightbox -- */

  var lightbox = $('#lightbox');
  var lbImg = $('#lightbox-img');
  var lbTitle = $('#lightbox-title');
  var lbRaw = $('#lightbox-raw');
  var lbZoom = $('#lightbox-zoom');
  var lastFocus = null;

  function openPlate(index) {
    if (!lightbox || !originsGrid) return;
    var img = $$('img[data-dark][data-light]', originsGrid)[index];
    if (!img) return;
    lastFocus = document.activeElement;
    lbImg.src = isLight() ? img.dataset.light : img.dataset.dark;
    lbImg.alt = img.alt;
    lbTitle.textContent = img.closest('.plate').querySelector('.plate__cap span').textContent;
    if (lbRaw) lbRaw.href = lbImg.src;
    lightbox.setAttribute('data-open', 'true');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    $('#lightbox-close').focus();
  }

  function closePlate() {
    if (!lightbox) return;
    lightbox.setAttribute('data-open', 'false');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  if (lightbox) {
    if (originsGrid) {
      originsGrid.addEventListener('click', function (e) {
        var btn = e.target.closest('[data-plate]');
        if (btn) { openPlate(parseInt(btn.dataset.plate, 10)); return; }
        if (e.target.tagName === 'IMG') {
          var fig = e.target.closest('.plate');
          var b = fig && fig.querySelector('[data-plate]');
          if (b) openPlate(parseInt(b.dataset.plate, 10));
        }
      });
    }

    $('#lightbox-backdrop').addEventListener('click', closePlate);
    $('#lightbox-close').addEventListener('click', closePlate);
    lbZoom.addEventListener('click', function () {
      var on = lightbox.getAttribute('data-zoom') === 'true';
      lightbox.setAttribute('data-zoom', on ? 'false' : 'true');
      lbZoom.setAttribute('aria-pressed', String(!on));
      lbZoom.textContent = on ? '1:1' : 'Fit';
    });

    document.addEventListener('keydown', function (e) {
      if (lightbox.getAttribute('data-open') !== 'true') return;
      if (e.key === 'Escape') { closePlate(); return; }
      if (e.key === 'Tab') {
        // Keep focus inside the dialog while it is open.
        var focusable = $$('button, a[href]', lightbox);
        if (!focusable.length) return;
        var first = focusable[0];
        var last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }

  /* ------------------------------------------------------------ copy -- */

  $$('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var cell = btn.closest('.install__cell');
      var pre = cell && cell.querySelector('pre');
      if (!pre) return;
      var done = function () {
        var original = btn.textContent;
        btn.textContent = 'Copied';
        setTimeout(function () { btn.textContent = original; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(pre.textContent).then(done, function () {});
      }
    });
  });

  /* ------------------------------------------------- scrolling regions -- */

  /* Scenes that overflow on narrow screens become focusable,
     labelled regions so the keyboard can scroll them. Scenes that fit take
     no tab stop. */
  function syncScrollables() {
    $$('[data-scroll-label]').forEach(function (el) {
      if (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1) {
        el.setAttribute('tabindex', '0');
        el.setAttribute('role', 'region');
        el.setAttribute('aria-label', el.dataset.scrollLabel);
      } else {
        el.removeAttribute('tabindex');
        el.removeAttribute('role');
        el.removeAttribute('aria-label');
      }
    });
  }

  var resizeTimer = 0;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () { syncScrollables(); revealCurrentLine(); }, 150);
  });
  syncScrollables();
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function () { syncScrollables(); revealCurrentLine(); });
  }

  /* Keep the artwork and the label in step on first paint. */
  syncArtwork();
})();
