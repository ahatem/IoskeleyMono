// Multi-Theme Prism definitions
const themesCSS = `
code[class*="language-"], pre[class*="language-"] {
  font-family: inherit; font-size: inherit; background: none; text-shadow: none;
}
pre[class*="language-"]::-moz-selection, pre[class*="language-"] ::-moz-selection,
code[class*="language-"]::-moz-selection, code[class*="language-"] ::-moz-selection,
pre[class*="language-"]::selection, pre[class*="language-"] ::selection,
code[class*="language-"]::selection, code[class*="language-"] ::selection {
  text-shadow: none; background: #6c7a8a30;
}

/* 1. Kintsugi Dark */
.theme-kintsugi .token.comment, .theme-kintsugi .token.prolog, .theme-kintsugi .token.doctype, .theme-kintsugi .token.cdata { color: #5f5f5f; }
.theme-kintsugi .token.punctuation { color: #7f7b66; }
.theme-kintsugi .token.property, .theme-kintsugi .token.tag, .theme-kintsugi .token.boolean, .theme-kintsugi .token.number, .theme-kintsugi .token.constant, .theme-kintsugi .token.symbol, .theme-kintsugi .token.deleted { color: #DB9833; }
.theme-kintsugi .token.selector, .theme-kintsugi .token.attr-name, .theme-kintsugi .token.string, .theme-kintsugi .token.char, .theme-kintsugi .token.builtin, .theme-kintsugi .token.inserted { color: #cc7f66; }
.theme-kintsugi .token.operator, .theme-kintsugi .token.entity, .theme-kintsugi .token.url, .theme-kintsugi .language-css .token.string, .theme-kintsugi .style .token.string { color: #E08542; }
.theme-kintsugi .token.atrule, .theme-kintsugi .token.attr-value, .theme-kintsugi .token.keyword { color: #D66848; font-weight: bold; }
.theme-kintsugi .token.function, .theme-kintsugi .token.class-name { color: #798283; }
.theme-kintsugi .token.regex, .theme-kintsugi .token.important, .theme-kintsugi .token.variable { color: #DBAD49; }

/* 1b. Kintsugi Light Flared */
.theme-kintsugi-light .token.comment, .theme-kintsugi-light .token.prolog, .theme-kintsugi-light .token.doctype, .theme-kintsugi-light .token.cdata { color: #8f8b83; }
.theme-kintsugi-light .token.punctuation { color: #726e65; }
.theme-kintsugi-light .token.property, .theme-kintsugi-light .token.tag, .theme-kintsugi-light .token.boolean, .theme-kintsugi-light .token.number, .theme-kintsugi-light .token.constant, .theme-kintsugi-light .token.symbol, .theme-kintsugi-light .token.deleted { color: #90671c; }
.theme-kintsugi-light .token.selector, .theme-kintsugi-light .token.attr-name, .theme-kintsugi-light .token.string, .theme-kintsugi-light .token.char, .theme-kintsugi-light .token.builtin, .theme-kintsugi-light .token.inserted { color: #a85030; }
.theme-kintsugi-light .token.operator, .theme-kintsugi-light .token.entity, .theme-kintsugi-light .token.url, .theme-kintsugi-light .language-css .token.string, .theme-kintsugi-light .style .token.string { color: #a45d1d; }
.theme-kintsugi-light .token.atrule, .theme-kintsugi-light .token.attr-value, .theme-kintsugi-light .token.keyword { color: #b84020; font-weight: bold; }
.theme-kintsugi-light .token.function, .theme-kintsugi-light .token.class-name { color: #506870; }
.theme-kintsugi-light .token.regex, .theme-kintsugi-light .token.important, .theme-kintsugi-light .token.variable { color: #87691c; }

/* 2. Tokyo Night */
.theme-tokyonight .token.comment, .theme-tokyonight .token.prolog { color: #565f89; }
.theme-tokyonight .token.punctuation { color: #89ddff; }
.theme-tokyonight .token.property, .theme-tokyonight .token.boolean, .theme-tokyonight .token.number, .theme-tokyonight .token.constant { color: #ff9e64; }
.theme-tokyonight .token.string, .theme-tokyonight .token.char, .theme-tokyonight .token.builtin { color: #9ece6a; }
.theme-tokyonight .token.operator { color: #89ddff; }
.theme-tokyonight .token.keyword, .theme-tokyonight .token.atrule { color: #bb9af7; font-weight: bold; }
.theme-tokyonight .token.function, .theme-tokyonight .token.class-name { color: #7aa2f7; }
.theme-tokyonight .token.variable, .theme-tokyonight .token.regex { color: #e0af68; }

/* 3. Kanagawa Dragon */
.theme-kanagawa .token.comment { color: #737c73; }
.theme-kanagawa .token.punctuation { color: #9e9b93; }
.theme-kanagawa .token.number, .theme-kanagawa .token.boolean, .theme-kanagawa .token.constant { color: #e46876; }
.theme-kanagawa .token.string, .theme-kanagawa .token.char { color: #87a987; }
.theme-kanagawa .token.operator { color: #c4b28a; }
.theme-kanagawa .token.keyword { color: #8ba4b0; font-weight: bold; }
.theme-kanagawa .token.function, .theme-kanagawa .token.class-name { color: #a292a3; }
.theme-kanagawa .token.variable { color: #e6c384; }

/* 4. Catppuccin Mocha */
.theme-catppuccin .token.comment { color: #6c7086; }
.theme-catppuccin .token.punctuation { color: #94e2d5; }
.theme-catppuccin .token.number, .theme-catppuccin .token.boolean, .theme-catppuccin .token.constant { color: #fab387; }
.theme-catppuccin .token.string, .theme-catppuccin .token.char { color: #a6e3a1; }
.theme-catppuccin .token.operator { color: #89dceb; }
.theme-catppuccin .token.keyword { color: #cba6f7; font-weight: bold; }
.theme-catppuccin .token.function, .theme-catppuccin .token.class-name { color: #89b4fa; }
.theme-catppuccin .token.variable { color: #f9e2af; }

/* 5. Solarized Light */
.theme-solarized-light .token.comment { color: #93a1a1; }
.theme-solarized-light .token.punctuation { color: #586e75; }
.theme-solarized-light .token.number, .theme-solarized-light .token.boolean, .theme-solarized-light .token.constant { color: #d33682; }
.theme-solarized-light .token.string, .theme-solarized-light .token.char { color: #2aa198; }
.theme-solarized-light .token.operator { color: #859900; }
.theme-solarized-light .token.keyword { color: #b58900; font-weight: bold; }
.theme-solarized-light .token.function, .theme-solarized-light .token.class-name { color: #268bd2; }
.theme-solarized-light .token.variable { color: #cb4b16; }

/* 6. Gruvbox Dark */
.theme-gruvbox .token.comment { color: #928374; }
.theme-gruvbox .token.punctuation { color: #d5c4a1; }
.theme-gruvbox .token.number, .theme-gruvbox .token.boolean, .theme-gruvbox .token.constant { color: #d3869b; }
.theme-gruvbox .token.string, .theme-gruvbox .token.char { color: #b8bb26; }
.theme-gruvbox .token.operator { color: #83a598; }
.theme-gruvbox .token.keyword { color: #fb4934; font-weight: bold; }
.theme-gruvbox .token.function, .theme-gruvbox .token.class-name { color: #fabd2f; }
.theme-gruvbox .token.variable { color: #fe8019; }

/* 7. Nord */
.theme-nord .token.comment { color: #616e88; }
.theme-nord .token.punctuation { color: #81a1c1; }
.theme-nord .token.number, .theme-nord .token.boolean, .theme-nord .token.constant { color: #b48ead; }
.theme-nord .token.string, .theme-nord .token.char { color: #a3be8c; }
.theme-nord .token.operator { color: #88c0d0; }
.theme-nord .token.keyword { color: #81a1c1; font-weight: bold; }
.theme-nord .token.function, .theme-nord .token.class-name { color: #88c0d0; }
.theme-nord .token.variable { color: #d08770; }

/* 8. Dracula */
.theme-dracula .token.comment { color: #6272a4; }
.theme-dracula .token.punctuation { color: #f8f8f2; }
.theme-dracula .token.number, .theme-dracula .token.boolean, .theme-dracula .token.constant { color: #bd93f9; }
.theme-dracula .token.string, .theme-dracula .token.char { color: #f1fa8c; }
.theme-dracula .token.operator { color: #ff79c6; }
.theme-dracula .token.keyword { color: #ff79c6; font-weight: bold; }
.theme-dracula .token.function, .theme-dracula .token.class-name { color: #50fa7b; }
.theme-dracula .token.variable { color: #8be9fd; }

/* 9. One Dark */
.theme-onedark .token.comment { color: #5c6370; }
.theme-onedark .token.punctuation { color: #abb2bf; }
.theme-onedark .token.number, .theme-onedark .token.boolean, .theme-onedark .token.constant { color: #d19a66; }
.theme-onedark .token.string, .theme-onedark .token.char { color: #98c379; }
.theme-onedark .token.operator { color: #56b6c2; }
.theme-onedark .token.keyword { color: #c678dd; font-weight: bold; }
.theme-onedark .token.function, .theme-onedark .token.class-name { color: #61afef; }
.theme-onedark .token.variable { color: #e06c75; }

/* 10. Solarized Dark */
.theme-solarized-dark .token.comment { color: #586e75; }
.theme-solarized-dark .token.punctuation { color: #839496; }
.theme-solarized-dark .token.number, .theme-solarized-dark .token.boolean, .theme-solarized-dark .token.constant { color: #d33682; }
.theme-solarized-dark .token.string, .theme-solarized-dark .token.char { color: #2aa198; }
.theme-solarized-dark .token.operator { color: #859900; }
.theme-solarized-dark .token.keyword { color: #b58900; font-weight: bold; }
.theme-solarized-dark .token.function, .theme-solarized-dark .token.class-name { color: #268bd2; }
.theme-solarized-dark .token.variable { color: #cb4b16; }

/* 11. GitHub Dark */
.theme-github-dark .token.comment { color: #8b949e; }
.theme-github-dark .token.punctuation { color: #c9d1d9; }
.theme-github-dark .token.number, .theme-github-dark .token.boolean, .theme-github-dark .token.constant { color: #79c0ff; }
.theme-github-dark .token.string, .theme-github-dark .token.char { color: #a5d6ff; }
.theme-github-dark .token.operator { color: #ff7b72; }
.theme-github-dark .token.keyword { color: #ff7b72; font-weight: bold; }
.theme-github-dark .token.function, .theme-github-dark .token.class-name { color: #d2a8ff; }
.theme-github-dark .token.variable { color: #ffa657; }

/* 12. Monokai Pro */
.theme-monokai .token.comment { color: #75715e; }
.theme-monokai .token.punctuation { color: #f8f8f2; }
.theme-monokai .token.number, .theme-monokai .token.boolean, .theme-monokai .token.constant { color: #ae81ff; }
.theme-monokai .token.string, .theme-monokai .token.char { color: #e6db74; }
.theme-monokai .token.operator { color: #f92672; }
.theme-monokai .token.keyword { color: #f92672; font-weight: bold; }
.theme-monokai .token.function, .theme-monokai .token.class-name { color: #a6e22e; }
.theme-monokai .token.variable { color: #66d9e8; }
`.trim();

(function() {
  const s = document.createElement('style');
  s.textContent = themesCSS;
  document.head.appendChild(s);
  document.getElementById('prism-theme')?.remove();
})();

// ── Width switcher ────────────────────────────────────────────────────

const widthOpts = document.querySelectorAll('#header-width-switcher .header-w-btn');
const WIDTH_KEY = 'ioskeley-width';

function applyWidth(width) {
  document.documentElement.classList.remove('sc');
  if (width === 'sc') document.documentElement.classList.add('sc');
}

function selectWidth(width, animate = false) {
  widthOpts.forEach(btn => {
    const active = btn.dataset.width === width;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  });
  if (animate) document.body.classList.add('switching');
  applyWidth(width);
  if (animate) {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => document.body.classList.remove('switching'));
    });
  }
}

widthOpts.forEach(btn => {
  btn.addEventListener('click', () => {
    try { localStorage.setItem(WIDTH_KEY, btn.dataset.width); } catch (_) {}
    selectWidth(btn.dataset.width, true);
  });
});

(function initWidth() {
  let saved = null;
  try { saved = localStorage.getItem(WIDTH_KEY); } catch (_) {}
  selectWidth(saved === 'sc' ? 'sc' : 'normal');
})();

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
  tryInput.value = samples[index].code;
  updateEditor();
  syncScroll();
}

// Load languages once, not on every keystroke, so re-highlighting stays sync.
const loadedLangs = new Set();
function ensureLang(lang, done) {
  if (loadedLangs.has(lang) || Prism.languages[lang]) { loadedLangs.add(lang); done(); return; }
  Prism.plugins.autoloader.loadLanguages([lang], () => { loadedLangs.add(lang); done(); });
}

function renderGutter(lineCount) {
  // Typing inside a line shouldn't touch the gutter.
  if (tryGutter.childElementCount === lineCount) return;
  let s = '';
  for (let i = 1; i <= lineCount; i++) s += i + '\n';
  tryGutter.textContent = s;
}

function updateEditor() {
  const text = tryInput.value;
  renderGutter(text.split('\n').length);
  // Trailing newline needs a placeholder or the layer ends up a row short.
  tryHighlight.textContent = text.endsWith('\n') ? text + ' ' : text;
  tryHighlight.className = `language-${tryLang}`;
  ensureLang(tryLang, () => Prism.highlightElement(tryHighlight));
}

function syncScroll() {
  const wrap = tryHighlight.parentElement;   // the <pre class="try-highlight">
  wrap.scrollTop = tryInput.scrollTop;
  wrap.scrollLeft = tryInput.scrollLeft;
  tryGutter.scrollTop = tryInput.scrollTop;

  // A scrollbar shrinks the textarea's viewport but not the highlight layer,
  // so match it or the colored text bleeds under the scrollbar.
  const h = tryInput.clientHeight, w = tryInput.clientWidth;
  if (h && wrap.style.height !== h + 'px') wrap.style.height = h + 'px';
  if (w && wrap.style.width !== w + 'px') wrap.style.width = w + 'px';
}

tryInput.addEventListener('scroll', syncScroll, { passive: true });
tryInput.addEventListener('input', () => { updateEditor(); syncScroll(); });

tryInput.addEventListener('keydown', (e) => {
  if (e.key !== 'Tab') return;
  e.preventDefault();
  const { selectionStart: a, selectionEnd: b, value } = tryInput;

  if (a === b && !e.shiftKey) {
    // setRangeText keeps native undo working; execCommand doesn't.
    tryInput.setRangeText('\t', a, b, 'end');
  } else {
    // Indent or outdent every line the selection touches.
    const start = value.lastIndexOf('\n', a - 1) + 1;
    const end = value.indexOf('\n', b) === -1 ? value.length : value.indexOf('\n', b);
    const block = value.slice(start, end);
    const shifted = e.shiftKey
      ? block.replace(/^(\t| {1,4})/gm, '')
      : block.replace(/^/gm, '\t');
    tryInput.setRangeText(shifted, start, end, 'select');
  }
  updateEditor();
  syncScroll();
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
tryInput.value = trySamplesData.js[0].code;
tryStatusLang.textContent = 'JavaScript';
Prism.plugins.autoloader.loadLanguages(
  ['javascript', 'python', 'rust', 'cpp', 'haskell', 'java', 'markup'],
  () => {
    updateEditor();
  }
);

// ── Playground Interactive Controls ───────────────────────────────────

const tryEditorBox = document.getElementById('try-editor-box');
const sizeSlider = document.getElementById('try-size-slider');
const sizeVal = document.getElementById('try-size-val');
const weightSel = document.getElementById('try-weight-sel');
const themeSel = document.getElementById('try-theme-sel');
const ligaturesBtn = document.getElementById('try-ligatures-btn');

if (sizeSlider && sizeVal && tryEditorBox) {
  sizeSlider.addEventListener('input', () => {
    const val = sizeSlider.value;
    sizeVal.textContent = `${val}px`;
    // Drive ALL layers via CSS variables — no per-element style mutations
    // This prevents the highlight/input font-size desync (jaggedness bug)
    tryEditorBox.style.setProperty('--try-fz', `${val}px`);
    updateEditor();
  });
}

if (weightSel) {
  weightSel.addEventListener('change', () => {
    const w = weightSel.value;
    tryEditorBox.style.setProperty('--try-fw', w);
    tryInput.style.fontWeight = w;
    tryHighlight.style.fontWeight = w;
  });
}

const ALL_THEMES = [
  'theme-kintsugi', 'theme-kintsugi-light', 'theme-kanagawa', 'theme-tokyonight',
  'theme-catppuccin', 'theme-gruvbox', 'theme-nord', 'theme-dracula', 'theme-onedark',
  'theme-solarized-dark', 'theme-solarized-light', 'theme-github-dark', 'theme-monokai'
];

if (themeSel && tryEditorBox) {
  themeSel.addEventListener('change', () => {
    tryEditorBox.classList.remove(...ALL_THEMES);
    tryEditorBox.classList.add(themeSel.value);
  });
}

if (ligaturesBtn) {
  let ligaturesOn = true;
  ligaturesBtn.addEventListener('click', () => {
    ligaturesOn = !ligaturesOn;
    ligaturesBtn.classList.toggle('active', ligaturesOn);
    const val = ligaturesOn ? 'normal' : 'none';
    tryInput.style.fontVariantLigatures = val;
    tryHighlight.style.fontVariantLigatures = val;
  });
}

// ── 1-Click Editor Setup Tabs ─────────────────────────────────────────

const configSnippets = {
  vscode: `// VS Code / Cursor: settings.json
{
  "editor.fontFamily": "'Ioskeley Mono', monospace",
  "editor.fontLigatures": true,
  "editor.fontWeight": "400",
  "editor.fontSize": 14.5,
  "editor.lineHeight": 1.55
}`,
  zed: `// Zed: settings.json
{
  "buffer_font_family": "Ioskeley Mono",
  "buffer_font_size": 15,
  "buffer_line_height": "comfortable"
}`,
  ghostty: `# Ghostty: config
font-family = Ioskeley Mono
font-size = 14`,
  kitty: `# Kitty: kitty.conf
font_family      Ioskeley Mono Term
bold_font        auto
italic_font      auto
bold_italic_font auto
font_size        14.0`,
  alacritty: `# Alacritty: alacritty.toml
[font.normal]
family = "Ioskeley Mono"
style = "Regular"`,
  wezterm: `-- WezTerm: wezterm.lua
local wezterm = require 'wezterm'
local config = wezterm.config_builder()
config.font = wezterm.font('Ioskeley Mono')
config.font_size = 14.0
return config`,
  neovim: `-- Neovim GUI (Neovide / Goneovim)
vim.opt.guifont = "IoskeleyMono Nerd Font:h14"`
};

(function initConfigTabs() {
  const tabs = document.querySelectorAll('.config-tab');
  const codeEl = document.getElementById('config-code');
  const copyBtn = document.getElementById('copy-cfg-btn');
  const copyText = document.getElementById('copy-cfg-text');
  let currentKey = 'vscode';

  if (!codeEl) return;

  function renderConfig(key) {
    currentKey = key;
    const raw = configSnippets[key] || '';
    // Highlighter is registered further down, so the first render is plain.
    if (window.__cfgHighlight) codeEl.innerHTML = window.__cfgHighlight(raw);
    else codeEl.textContent = raw;
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      renderConfig(tab.dataset.cfg);
    });
  });

  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(configSnippets[currentKey]);
        copyBtn.classList.add('copied');
        if (copyText) copyText.textContent = '✓ Copied';
        setTimeout(() => {
          copyBtn.classList.remove('copied');
          if (copyText) copyText.textContent = 'Copy';
        }, 2000);
      } catch (_) {}
    });
  }

  renderConfig('vscode');
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

  // Hold the <img>, not its src — the art swaps on theme change and a cached
  // src would reopen the old one.
  const galleryItems = cards.map(card => {
    const img = card.querySelector('img');
    return {
      img,
      alt: img ? img.getAttribute('alt') : '',
      title: card.dataset.title || (img ? img.getAttribute('alt') : 'Comparison Specimen'),
    };
  });

  function showImage(index) {
    if (index < 0) index = galleryItems.length - 1;
    if (index >= galleryItems.length) index = 0;
    currentIndex = index;

    const item = galleryItems[currentIndex];
    const src = item.img ? item.img.getAttribute('src') : '';
    imgEl.src = src;
    imgEl.alt = item.alt;
    titleEl.textContent = item.title;
    if (rawLink) rawLink.href = src;

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

// ── Split Diff Slider ─────────────────────────────────────────────────

(function initSplitDiff() {
  const container = document.querySelector('.split-diff-container');
  if (!container) return;

  const beforeLayer = container.querySelector('.split-diff-layer--before');
  const handle = container.querySelector('.split-diff-handle');
  if (!beforeLayer || !handle) return;

  let dragging = false;

  function setPosition(clientX) {
    const rect = container.getBoundingClientRect();
    let pct = ((clientX - rect.left) / rect.width) * 100;
    pct = Math.max(5, Math.min(95, pct));
    beforeLayer.style.width = pct + '%';
    handle.style.left = pct + '%';
  }

  handle.addEventListener('mousedown', (e) => {
    e.preventDefault();
    dragging = true;
    document.body.style.cursor = 'ew-resize';
    document.body.style.userSelect = 'none';
  });

  document.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    setPosition(e.clientX);
  });

  document.addEventListener('mouseup', () => {
    if (!dragging) return;
    dragging = false;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  });

  // Touch support
  handle.addEventListener('touchstart', (e) => {
    e.preventDefault();
    dragging = true;
  }, { passive: false });

  document.addEventListener('touchmove', (e) => {
    if (!dragging) return;
    setPosition(e.touches[0].clientX);
  }, { passive: true });

  document.addEventListener('touchend', () => { dragging = false; });
})();

// ── Header Width Switcher Sync ────────────────────────────────────────

(function initHeaderWidth() {
  const headerBtns = document.querySelectorAll('.header-w-btn');
  const tryWidthSel = document.getElementById('try-width-sel');

  function applyWidthClass(w) {
    document.documentElement.classList.remove('sc');
    if (w === 'sc') document.documentElement.classList.add('sc');
    localStorage.setItem('ioskeley-width', w);
  }

  function syncAll(w) {
    // sync header buttons
    headerBtns.forEach(b => b.classList.toggle('active', b.dataset.width === w));
    // sync Try It dropdown
    if (tryWidthSel) tryWidthSel.value = w;
    applyWidthClass(w);
  }

  headerBtns.forEach(btn => {
    btn.addEventListener('click', () => syncAll(btn.dataset.width));
  });

  if (tryWidthSel) {
    tryWidthSel.addEventListener('change', () => syncAll(tryWidthSel.value));
  }

  // Restore saved width
  const saved = localStorage.getItem('ioskeley-width');
  if (saved) syncAll(saved);
})();

// ── Light / dark toggle ───────────────────────────────────────────────

(function initThemeToggle() {
  const btn = document.getElementById('theme-toggle');
  if (!btn) return;
  const root = document.documentElement;

  // Baked art can't inherit CSS vars, so swap the file. data-* keeps the
  // light renders lazy for anyone who never leaves dark mode.
  function syncArtwork() {
    const light = root.getAttribute('data-theme') === 'light';
    document.querySelectorAll('img[data-light]').forEach(img => {
      const next = light ? img.dataset.light : img.dataset.dark;
      if (next && img.getAttribute('src') !== next) img.setAttribute('src', next);
    });

    // Only follow the site between the two Kintsugi variants. If they've
    // picked Dracula to preview, leave it alone.
    const box = document.getElementById('try-editor-box');
    const sel = document.getElementById('try-theme-sel');
    if (!box || !sel) return;
    const want = light ? 'theme-kintsugi-light' : 'theme-kintsugi';
    const other = light ? 'theme-kintsugi' : 'theme-kintsugi-light';
    if (box.classList.contains(other)) {
      box.classList.remove(other);
      box.classList.add(want);
      sel.value = want;
    }
  }
  syncArtwork();

  btn.addEventListener('click', () => {
    const light = root.getAttribute('data-theme') === 'light';
    if (light) root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', 'light');
    try { localStorage.setItem('ioskeley-theme', light ? 'dark' : 'light'); } catch (_) {}
    syncArtwork();
  });

  // Follow the OS until they pick a side.
  const mq = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)');
  if (mq && mq.addEventListener) {
    mq.addEventListener('change', e => {
      let saved = null;
      try { saved = localStorage.getItem('ioskeley-theme'); } catch (_) {}
      if (saved) return;
      if (e.matches) root.setAttribute('data-theme', 'light');
      else root.removeAttribute('data-theme');
      syncArtwork();
    });
  }
})();

// ── Comparison font picker (lazy-loaded web fonts) ────────────────────

(function initSplitFontPicker() {
  const sel = document.getElementById('split-font-sel');
  const layer = document.querySelector('.split-diff-layer--after');
  const badge = document.getElementById('split-badge-right');
  if (!sel || !layer || !badge) return;

  // Fetched on first pick, so the page costs nothing if this is never used.
  const loaded = new Set();

  function loadWebFont(spec, family) {
    if (loaded.has(spec)) return Promise.resolve();
    loaded.add(spec);

    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = `https://fonts.googleapis.com/css2?family=${spec}&display=swap`;
    document.head.appendChild(link);

    // Resolve once the face is usable, not just when the CSS lands.
    return new Promise(resolve => {
      link.addEventListener('load', () => {
        if (document.fonts && document.fonts.load) {
          document.fonts.load(`400 1em "${family}"`).then(resolve, resolve);
        } else resolve();
      });
      link.addEventListener('error', resolve);
    });
  }

  async function apply() {
    const opt = sel.selectedOptions[0];
    const value = sel.value;
    const spec = opt.dataset.webfont;
    badge.textContent = opt.textContent.trim();

    if (spec) {
      layer.classList.add('is-loading-font');
      await loadWebFont(spec, value);
      layer.classList.remove('is-loading-font');
      // Quoted, with a fallback for the load window.
      layer.style.fontFamily = `"${value}", monospace`;
    } else {
      layer.style.fontFamily = value;
    }
  }

  sel.addEventListener('change', apply);
  apply();
})();

// ── Syntax highlight the comparison slider ────────────────────────────

(function highlightSplitDiff() {
  const blocks = document.querySelectorAll('.split-diff-content code.language-js');
  if (!blocks.length || typeof Prism === 'undefined') return;
  // Identical markup both sides, so the colors line up across the divider.
  blocks.forEach(b => Prism.highlightElement(b));
})();

// ── Installation Tabs ─────────────────────────────────────────────────

(function initInstallTabs() {
  const tabs = document.querySelectorAll('.install-tab');
  const panels = document.querySelectorAll('.install-tab-content');
  if (!tabs.length) return;

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const target = document.querySelector(`.install-tab-content[data-os-content="${tab.dataset.os}"]`);
      if (target) target.classList.add('active');
    });
  });

  // Activate first tab
  if (tabs[0]) tabs[0].click();
})();

// ── Kintsugi Config Syntax Highlight ─────────────────────────────────
// Color the config code blocks (not Prism, uses custom span classes)

(function highlightConfigs() {
  // Single pass, so emitted markup never gets re-scanned. Chained .replace()
  // breaks here: once the colon is wrapped in a span the string and number
  // patterns stop matching, and class="..." reads as a string.
  function highlight(raw) {
    const esc = t => t
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    const token = new RegExp([
      '(\\/\\/[^\\n]*|#[^\\n]*)',              // 1 comment
      '("(?:[^"\\\\]|\\\\.)*")(\\s*:)?',       // 2 string, 3 trailing colon => JSON key
      '\\b(true|false)\\b',                    // 4 boolean
      '\\b(require|local|return)\\b',          // 5 keyword
      '\\b(\\d+(?:\\.\\d+)?)\\b',              // 6 number
      '^([ \\t]*)([A-Za-z_][\\w.]*)(?=\\s*=)'  // 7 indent, 8 TOML/Lua key
    ].join('|'), 'gm');

    let out = '', last = 0, m;
    while ((m = token.exec(raw)) !== null) {
      out += esc(raw.slice(last, m.index));
      last = m.index + m[0].length;

      if (m[1]) {
        out += `<span class="cfg-cmt">${esc(m[1])}</span>`;
      } else if (m[2]) {
        // A string followed by ":" is a key; otherwise it's a value.
        out += m[3]
          ? `<span class="cfg-key">${esc(m[2])}</span><span class="cfg-punc">${esc(m[3])}</span>`
          : `<span class="cfg-str">${esc(m[2])}</span>`;
      } else if (m[4]) {
        out += `<span class="cfg-bool">${m[4]}</span>`;
      } else if (m[5]) {
        out += `<span class="cfg-kw">${m[5]}</span>`;
      } else if (m[6]) {
        out += `<span class="cfg-num">${m[6]}</span>`;
      } else if (m[8]) {
        out += esc(m[7]) + `<span class="cfg-key">${esc(m[8])}</span>`;
      }
    }
    out += esc(raw.slice(last));
    return out;
  }

  const codeEl = document.getElementById('config-code');
  if (!codeEl) return;

  // renderConfig calls this directly. The old version hooked tab clicks and
  // re-highlighted in rAF, which raced it and never fired in a background tab.
  window.__cfgHighlight = highlight;

  // renderConfig already painted the default as plain text; redo it.
  codeEl.innerHTML = highlight(codeEl.textContent);
})();
