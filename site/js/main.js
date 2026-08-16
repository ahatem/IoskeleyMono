// Kintsugi Dark Flared Prism theme
const kintsugiTheme = `
code[class*="language-"], pre[class*="language-"] {
  color: #BCAC8F; background: none; text-shadow: none;
  font-family: inherit; font-size: inherit;
}
pre[class*="language-"]::-moz-selection, pre[class*="language-"] ::-moz-selection,
code[class*="language-"]::-moz-selection, code[class*="language-"] ::-moz-selection {
  text-shadow: none; background: #6c7a8a30;
}
pre[class*="language-"]::selection, pre[class*="language-"] ::selection,
code[class*="language-"]::selection, code[class*="language-"] ::selection {
  text-shadow: none; background: #6c7a8a30;
}
.token.comment, .token.prolog, .token.doctype, .token.cdata { color: #5f5f5f; }
.token.punctuation { color: #7f7b66; }
.token.property, .token.tag, .token.boolean, .token.number,
.token.constant, .token.symbol, .token.deleted { color: #DB9833; }
.token.selector, .token.attr-name, .token.string, .token.char,
.token.builtin, .token.inserted { color: #cc7f66; }
.token.operator, .token.entity, .token.url,
.language-css .token.string, .style .token.string { color: #E08542; }
.token.atrule, .token.attr-value, .token.keyword { color: #D66848; font-weight: bold; }
.token.function, .token.class-name { color: #798283; }
.token.regex, .token.important, .token.variable { color: #DBAD49; }
.token.important, .token.bold { font-weight: bold; }
.token.italic { font-style: italic; }
.token.entity { cursor: help; }
`.trim();

(function() {
  const s = document.createElement('style');
  s.textContent = kintsugiTheme;
  document.head.appendChild(s);
  document.getElementById('prism-theme')?.remove();
})();

// ── Width switcher ────────────────────────────────────────────────────

const widthOpts = document.querySelectorAll('#width-switcher .seg-opt');
const WIDTH_KEY = 'ioskeley-width';

(function initWidth() {
  const saved = localStorage.getItem(WIDTH_KEY);
  if (saved) {
    const btn = document.querySelector(`.seg-opt[data-width="${saved}"]`);
    if (btn) btn.click();
  }
})();

function applyWidth(width) {
  document.documentElement.classList.remove('sc', 'condensed');
  if (width === 'sc') document.documentElement.classList.add('sc');
  if (width === 'cond') document.documentElement.classList.add('condensed');
}

widthOpts.forEach(btn => {
  btn.addEventListener('click', () => {
    widthOpts.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    localStorage.setItem(WIDTH_KEY, btn.dataset.width);
    document.body.classList.add('switching');
    applyWidth(btn.dataset.width);
    requestAnimationFrame(() => {
      requestAnimationFrame(() => document.body.classList.remove('switching'));
    });
  });
});

// ── Try It editor ─────────────────────────────────────────────────────

const tryInput = document.getElementById('try-input');
const tryHighlight = document.getElementById('try-highlight');
const tryGutter = document.getElementById('try-gutter');
const tryLangBtns = document.querySelectorAll('.try-lang-opt');
const trySamples = document.getElementById('try-samples');
const tryStatusLang = document.getElementById('try-status-lang');
let tryLang = 'js';
const langNames = { js: 'JavaScript', py: 'Python', rust: 'Rust', cpp: 'C++', haskell: 'Haskell', java: 'Java', html: 'HTML' };

const trySamplesData = {
  js: [
    {
      label: 'Fibonacci',
      code: [
        'const fibonacci = (n) => {',
        '    if (n < 2) return n;',
        '    return fibonacci(n - 1) + fibonacci(n - 2);',
        '};',
        '',
        'const seq = Array.from({ length: 15 }, (_, i) => fibonacci(i));',
        'console.log("Fibonacci:", seq.join(", "));',
      ].join('\n'),
    },
    {
      label: 'Filter',
      code: [
        'const users = [',
        '    { name: "Alice", role: "admin" },',
        '    { name: "Bob", role: "user" },',
        '    { name: "Charlie", role: "user" },',
        '];',
        '',
        'const admins = users',
        '    .filter(u => u.role === "admin")',
        '    .map(u => u.name);',
        '',
        'console.log(`Admins: ${admins.join(", ")}`);',
      ].join('\n'),
    },
    {
      label: 'Async',
      code: [
        'async function fetchData(url) {',
        '    try {',
        '        const res = await fetch(url);',
        '        if (!res.ok) throw new Error(`HTTP ${res.status}`);',
        '        return await res.json();',
        '    } catch (err) {',
        '        console.error("Failed:", err.message);',
        '        return null;',
        '    }',
        '}',
      ].join('\n'),
    },
  ],
  py: [
    {
      label: 'Data',
      code: [
        'from dataclasses import dataclass',
        '',
        '@dataclass',
        'class Item:',
        '    name: str',
        '    price: float',
        '',
        '    @property',
        '    def taxed(self) -> float:',
        '        return self.price * 1.15',
        '',
        'items = [Item("widget", 9.99), Item("gadget", 14.50)]',
        'for item in items:',
        '    print(f"{item.name}: ${item.taxed:.2f}")',
      ].join('\n'),
    },
    {
      label: 'Comprehension',
      code: [
        'nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]',
        '',
        'evens = [x for x in nums if x % 2 == 0]',
        'odds  = [x for x in nums if x % 2 != 0]',
        'squares = {x: x**2 for x in nums}',
        '',
        'print(f"Evens: {evens}")',
        'print(f"Odds:  {odds}")',
        'print(f"Map:   {squares}")',
      ].join('\n'),
    },
    {
      label: 'Decorator',
      code: [
        'import time',
        '',
        'def timer(fn):',
        '    def wrapper(*args, **kwargs):',
        '        start = time.perf_counter()',
        '        result = fn(*args, **kwargs)',
        '        elapsed = time.perf_counter() - start',
        '        print(f"{fn.__name__} took {elapsed:.4f}s")',
        '        return result',
        '    return wrapper',
        '',
        '@timer',
        'def slow_add(a, b):',
        '    time.sleep(0.1)',
        '    return a + b',
      ].join('\n'),
    },
  ],
  rust: [
    {
      label: 'Enum',
      code: [
        '#[derive(Debug)]',
        'enum Status {',
        '    Active,',
        '    Inactive,',
        '    Pending(String),',
        '}',
        '',
        'fn describe(s: &Status) -> &str {',
        '    match s {',
        '        Status::Active => "running",',
        '        Status::Inactive => "stopped",',
        '        Status::Pending(r) => r,',
        '    }',
        '}',
      ].join('\n'),
    },
    {
      label: 'Generics',
      code: [
        'fn identity<T: std::fmt::Display>(x: T) -> String {',
        '    format!("value: {}", x)',
        '}',
        '',
        'fn main() {',
        '    let s = identity(42);',
        '    let t = identity("hello");',
        '    println!("{s}");',
        '    println!("{t}");',
        '}',
      ].join('\n'),
    },
    {
      label: 'Iterator',
      code: [
        'fn process(nums: &[i32]) -> Vec<i32> {',
        '    nums.iter()',
        '        .filter(|&&n| n > 0)',
        '        .map(|&n| n * 2)',
        '        .collect()',
        '}',
        '',
        'let data = [-3, 0, 5, -1, 8, 2];',
        'let result = process(&data);',
        'println!("{:?}", result);',
      ].join('\n'),
    },
  ],
  html: [
    {
      label: 'Article',
      code: [
        '<article class="post">',
        '    <header>',
        '        <h1>Hello, <span class="hl">World</span></h1>',
        '        <time datetime="2026-05-26">May 26</time>',
        '    </header>',
        '    <section class="content">',
        '        <p>Styled with <strong>Ioskeley Mono</strong>.</p>',
        '        <pre><code>npm run build</code></pre>',
        '    </section>',
        '</article>',
      ].join('\n'),
    },
    {
      label: 'Form',
      code: [
        '<form action="/submit" method="POST">',
        '    <label for="email">Email:</label>',
        '    <input type="email" id="email" name="email" required>',
        '',
        '    <label for="role">Role:</label>',
        '    <select id="role" name="role">',
        '        <option value="user">User</option>',
        '        <option value="admin">Admin</option>',
        '    </select>',
        '',
        '    <button type="submit">Submit</button>',
        '</form>',
      ].join('\n'),
    },
    {
      label: 'Table',
      code: [
        '<table>',
        '    <caption>Font Weights</caption>',
        '    <thead>',
        '        <tr><th>Name</th><th>Value</th></tr>',
        '    </thead>',
        '    <tbody>',
        '        <tr><td>Regular</td><td>400</td></tr>',
        '        <tr><td>Medium</td><td>500</td></tr>',
        '        <tr><td>Bold</td><td>700</td></tr>',
        '    </tbody>',
        '</table>',
      ].join('\n'),
    },
  ],
  cpp: [
    {
      label: 'Template',
      code: [
        'template <typename T>',
        'concept Numeric = std::is_arithmetic_v<T>;',
        '',
        'template <Numeric T>',
        'T max(T a, T b) {',
        '    return (a > b) ? a : b;',
        '}',
        '',
        'auto result = max(3.14, 2.72);',
        'auto r2 = max<int>(42, 7);',
      ].join('\n'),
    },
    {
      label: 'Lambda',
      code: [
        '#include <vector>',
        '#include <algorithm>',
        '',
        'auto main() -> int {',
        '    std::vector<int> nums = {1, 2, 3, 4, 5};',
        '',
        '    auto even = std::count_if(',
        '        nums.begin(), nums.end(),',
        '        [](int n) { return n % 2 == 0; }',
        '    );',
        '',
        '    return even;',
        '}',
      ].join('\n'),
    },
    {
      label: 'RAII',
      code: [
        'class Buffer {',
        '    int* data;',
        'public:',
        '    explicit Buffer(size_t sz)',
        '        : data(new int[sz]) {}',
        '',
        '    ~Buffer() { delete[] data; }',
        '',
        '    Buffer(const Buffer&) = delete;',
        '    auto operator=(const Buffer&) = delete;',
        '};',
      ].join('\n'),
    },
  ],
  haskell: [
    {
      label: 'Quicksort',
      code: [
        'quicksort :: Ord a => [a] -> [a]',
        'quicksort [] = []',
        'quicksort (p:xs) =',
        '    quicksort smaller ++ [p] ++ quicksort larger',
        '  where',
        '    smaller = filter (< p) xs',
        '    larger  = filter (>= p) xs',
      ].join('\n'),
    },
    {
      label: 'Functor',
      code: [
        'data Maybe\' a = Nothing\' | Just\' a',
        '    deriving (Show, Eq)',
        '',
        'instance Functor Maybe\' where',
        '    fmap _ Nothing\'  = Nothing\'',
        '    fmap f (Just\' x) = Just\' (f x)',
      ].join('\n'),
    },
    {
      label: 'Eval',
      code: [
        'data Expr = Val Int',
        '          | Add Expr Expr',
        '          | Mul Expr Expr',
        '',
        'eval :: Expr -> Maybe Int',
        'eval (Val n)   = Just n',
        'eval (Add x y) = do',
        '    a <- eval x',
        '    b <- eval y',
        '    return (a + b)',
        'eval (Mul x y) = do',
        '    a <- eval x',
        '    b <- eval y',
        '    return (a * b)',
      ].join('\n'),
    },
  ],
  java: [
    {
      label: 'Records',
      code: [
        'public sealed interface Shape',
        '    permits Circle, Rectangle {}',
        '',
        'record Circle(double radius) implements Shape {',
        '    public double area() {',
        '        return Math.PI * radius * radius;',
        '    }',
        '}',
        '',
        'record Rectangle(double w, double h) implements Shape {',
        '    public double area() {',
        '        return w * h;',
        '    }',
        '}',
      ].join('\n'),
    },
    {
      label: 'Streams',
      code: [
        'var result = IntStream.rangeClosed(1, 20)',
        '    .filter(n -> n % 2 == 0)',
        '    .mapToObj(n -> "%d:%d".formatted(n, n * n))',
        '    .collect(Collectors.joining(", "));',
        '',
        'System.out.println(result);',
      ].join('\n'),
    },
    {
      label: 'Generics',
      code: [
        'public class Pair<A, B> {',
        '    private final A first;',
        '    private final B second;',
        '',
        '    public Pair(A first, B second) {',
        '        this.first = first;',
        '        this.second = second;',
        '    }',
        '',
        '    public A first()  { return first; }',
        '    public B second() { return second; }',
        '',
        '    public static <A, B> Pair<A, B> of(A a, B b) {',
        '        return new Pair<>(a, b);',
        '    }',
        '}',
      ].join('\n'),
    },
  ],
};

function renderSamples() {
  const samples = trySamplesData[tryLang] || [];
  trySamples.innerHTML = samples.map((s, i) =>
    `<button class="try-sample-btn" data-sample="${i}">${s.label}</button>`
  ).join('');
}

function loadSample(index) {
  const samples = trySamplesData[tryLang];
  if (!samples || !samples[index]) return;
  tryInput.textContent = samples[index].code;
  updateEditor();
}

function updateEditor() {
  const text = tryInput.innerText;
  const lines = text.split('\n');
  tryGutter.textContent = lines.map((_, i) => i + 1).join('\n');
  tryHighlight.textContent = text || ' ';
  tryHighlight.className = `language-${tryLang}`;
  Prism.plugins.autoloader.loadLanguages([tryLang], () => {
    Prism.highlightElement(tryHighlight);
  });
}

tryInput.addEventListener('scroll', () => {
  tryHighlight.scrollTop = tryInput.scrollTop;
  tryHighlight.scrollLeft = tryInput.scrollLeft;
  tryGutter.scrollTop = tryInput.scrollTop;
});

tryInput.addEventListener('input', updateEditor);

tryInput.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    e.preventDefault();
    document.execCommand('insertText', false, '\t');
    updateEditor();
  }
});

tryInput.addEventListener('paste', (e) => {
  e.preventDefault();
  const text = e.clipboardData.getData('text/plain');
  document.execCommand('insertText', false, text);
  updateEditor();
});

tryLangBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    tryLangBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    tryLang = btn.dataset.tryLang;
    tryStatusLang.textContent = langNames[tryLang] || tryLang;
    renderSamples();
    loadSample(0);
  });
});

trySamples.addEventListener('click', (e) => {
  const btn = e.target.closest('.try-sample-btn');
  if (!btn) return;
  loadSample(parseInt(btn.dataset.sample));
});

// Init — load first sample, pre-highlight
renderSamples();
tryInput.textContent = trySamplesData.js[0].code;
tryStatusLang.textContent = 'JavaScript';
Prism.plugins.autoloader.loadLanguages(
  ['javascript', 'python', 'rust', 'cpp', 'haskell', 'java', 'markup'],
  () => {
    updateEditor();
  }
);

// ── Download counts ──────────────────────────────────────────────────

(async function loadDownloads() {
  try {
    const res = await fetch('https://api.github.com/repos/ahatem/IoskeleyMono/releases/latest');
    if (!res.ok) return;
    const release = await res.json();
    const assetMap = {};
    release.assets.forEach(a => { assetMap[a.name] = a.download_count; });

    const rows = document.querySelectorAll('.dl-cell[data-zip]');
    let maxCount = 0;
    const counts = [];
    rows.forEach(el => {
      const c = assetMap[el.dataset.zip] || 0;
      counts.push(c);
      if (c > maxCount) maxCount = c;
    });
    if (maxCount === 0) return;

    rows.forEach((el, i) => {
      const pct = (counts[i] / maxCount) * 100;
      el.querySelector('.dl-fill').style.width = pct + '%';
      el.querySelector('.dl-num').textContent = counts[i].toLocaleString();
    });
  } catch (_) {}
})();

// ── Hover Loupe Magnifier ─────────────────────────────────────────────

(function initLoupe() {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

  const cards = document.querySelectorAll('.comp-card');
  const ZOOM_LEVEL = 2.4;

  cards.forEach(card => {
    const img = card.querySelector('img');
    if (!img) return;

    const loupe = document.createElement('div');
    loupe.className = 'comp-loupe';
    card.appendChild(loupe);

    let rect = null;

    function updateRect() {
      rect = card.getBoundingClientRect();
      loupe.style.backgroundImage = `url("${img.currentSrc || img.src}")`;
      loupe.style.backgroundSize = `${rect.width * ZOOM_LEVEL}px ${rect.height * ZOOM_LEVEL}px`;
    }

    card.addEventListener('mouseenter', (e) => {
      updateRect();
      loupe.classList.add('is-active');
      moveLoupe(e);
    });

    card.addEventListener('mouseleave', () => {
      loupe.classList.remove('is-active');
    });

    function moveLoupe(e) {
      if (!rect) updateRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      loupe.style.left = `${x}px`;
      loupe.style.top = `${y}px`;

      const bgX = (x / rect.width) * 100;
      const bgY = (y / rect.height) * 100;
      loupe.style.backgroundPosition = `${bgX}% ${bgY}%`;
    }

    card.addEventListener('mousemove', moveLoupe);
  });
})();

// ── Lightbox & Image Zoom ─────────────────────────────────────────────

(function initLightbox() {
  const lightbox = document.getElementById('lightbox');
  if (!lightbox) return;

  const backdrop = document.getElementById('lightbox-backdrop');
  const closeBtn = document.getElementById('lightbox-close');
  const prevBtn = document.getElementById('lightbox-prev');
  const nextBtn = document.getElementById('lightbox-next');
  const zoomBtn = document.getElementById('lightbox-zoom');
  const zoomLabel = document.getElementById('lightbox-zoom-label');
  const rawLink = document.getElementById('lightbox-raw');
  const titleEl = document.getElementById('lightbox-title');
  const viewport = document.getElementById('lightbox-viewport');
  const imgEl = document.getElementById('lightbox-img');
  const cards = Array.from(document.querySelectorAll('.comp-card'));

  if (!cards.length) return;

  let currentIndex = 0;
  let isZoomed = false;

  const galleryItems = cards.map(card => {
    const img = card.querySelector('img');
    return {
      src: img ? img.getAttribute('src') : '',
      alt: img ? img.getAttribute('alt') : '',
      title: card.dataset.title || (img ? img.getAttribute('alt') : 'Comparison Specimen'),
    };
  });

  function showImage(index) {
    if (index < 0) index = galleryItems.length - 1;
    if (index >= galleryItems.length) index = 0;
    currentIndex = index;

    const item = galleryItems[currentIndex];
    imgEl.src = item.src;
    imgEl.alt = item.alt;
    titleEl.textContent = item.title;
    if (rawLink) rawLink.href = item.src;

    setZoom(false);
  }

  function setZoom(zoomed) {
    isZoomed = zoomed;
    if (isZoomed) {
      viewport.classList.add('is-zoomed');
      if (zoomLabel) zoomLabel.textContent = 'Fit Screen';
    } else {
      viewport.classList.remove('is-zoomed');
      if (zoomLabel) zoomLabel.textContent = '1:1 Zoom';
      viewport.scrollTop = 0;
      viewport.scrollLeft = 0;
    }
  }

  function toggleZoom() {
    setZoom(!isZoomed);
  }

  function openLightbox(index) {
    showImage(index);
    lightbox.classList.add('active');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    lightbox.classList.remove('active');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    setZoom(false);
  }

  cards.forEach((card, i) => {
    card.addEventListener('click', () => openLightbox(i));
  });

  if (backdrop) backdrop.addEventListener('click', closeLightbox);
  if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
  if (zoomBtn) zoomBtn.addEventListener('click', toggleZoom);
  if (viewport) viewport.addEventListener('click', (e) => {
    if (e.target === viewport || e.target === imgEl) {
      toggleZoom();
    }
  });

  if (prevBtn) prevBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    showImage(currentIndex - 1);
  });

  if (nextBtn) nextBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    showImage(currentIndex + 1);
  });

  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('active')) return;

    if (e.key === 'Escape') {
      closeLightbox();
    } else if (e.key === 'ArrowLeft') {
      showImage(currentIndex - 1);
    } else if (e.key === 'ArrowRight') {
      showImage(currentIndex + 1);
    } else if (e.key === 'z' || e.key === 'Z') {
      toggleZoom();
    }
  });
})();
