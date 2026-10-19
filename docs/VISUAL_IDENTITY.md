# Ioskeley visual identity

Ioskeley is its own typeface identity: a monochrome, typography-led technical
publication, with Proof Red as a single, strictly governed exception.
**Grammar recedes; content remains.** The font—not a brand hue—is the
identifying color. Preserve generous negative space, precise alignment,
large/small type contrast, and only a few deliberate rules. Avoid UI panels,
editor chrome, gradients, glows, decorative grids, and hue-based syntax.

## Color tokens

| Role | Dark | Light |
|---|---|---|
| Canvas | `#101010` | `#F2F0EA` |
| Ink / primary | `#D8D5CE` | `#292826` |
| Secondary | `#B8B5AF` | `#4E4D49` |
| Grammar | `#7E7C77` | `#807D77` |
| Keywords | `#74726E` | `#68655F` |
| Operators | `#74726E` | `#77746E` |
| Punctuation | `#686763` | `#8B8880` |
| Comments | `#5F5D58` italic | `#98958D` italic |
| Proof Red | `#B04A43` | `#913832` |
| Rare emphasis | `#ECE9E2` | `#171614` |
| Rule | `#343330` | `#D3D0C8` |
| Guide | `#4A4843` | `#BDBAB2` |
| Selection | `#302F2B` | `#E2DFD8` |

Keep emphasis rare. Use primary/secondary for identifiers and meaningful values;
use grammar tones for keywords, operators, and punctuation. In light mode grammar
moves toward the paper. Proof Red is the only non-neutral colour in the system and
is governed separately below; no other branding hue is permitted.

Comments use the real italic face in both modes, never a synthesised oblique.
Light-mode punctuation and comments sit closer to primary than in the previous
revision so that a 14–15 px italic comment stays readable on `#F2F0EA`.

`Selection` is a reserved role: no production plate uses it yet, so the artwork
generators do not define it. If a plate ever needs a selection state, use this
token rather than inventing a new one.

## Proof Red

**Monochrome carries the information. Proof Red marks structure.**

Proof Red is an exception, not a second palette. It exists because Ioskeley is a
programming typeface, where delimiter and punctuation forms are part of the
visual character. Keep it scarce enough that it keeps its meaning: if red appears
everywhere, it marks nothing.

### Where it may appear

- Branded code specimens, on structural punctuation only.
- One small technical proof or registration mark per specimen. The approved
  Social Preview uses the baseline registration tick, drawn on the measurement
  canvas; the cap and x-height ticks stay grammar grey so the highlight reads as a
  deliberate reference to the baseline.
- Selected-glyph indicators, and restrained active or interactive state on the
  website where it carries real meaning (current specimen control, current
  selection).

### Where it may not appear

Not a general styling device. Do not use it for headings, large borders, card
backgrounds, paragraph emphasis, filled buttons, generic hover decoration,
ornamental marks, or warnings and errors unless the red is semantically an error.
A dense run of red punctuation, or red applied to commas, colons, or semicolons,
stops reading as structure and becomes a syntax theme.

### Structural punctuation set

Accented: `{ } [ ] ( ) " " ' '`.

Not accented by default: `,` `:` `;`, keywords, operators, identifiers, numbers,
comments, string contents, and member-access periods.

The punctuation itself takes the colour; the content it encloses keeps its normal
monochrome role, so `"!="` shows a red delimiter around monochrome content. Proof
Red is presentation applied in HTML/CSS. It is not a font feature and must never be
described as the typeface colouring punctuation.

### Branded specimens versus analytical plates

Origins-01, Origins-02 and Origins-03 are analytical comparison evidence, not
branded specimen artwork. They stay **monochrome**. Ioskeley punctuation must not
be accented inside the Berkeley/TX-02 comparison plates, because a colour that
carries no evidential meaning would become a variable in a study whose only
purpose is typeface comparison.

## Typography and specimens

- Use Ioskeley itself for titles, code, labels, and measurements.
- On a 1280×640 plate, use a bold 48–52 px product title, regular 14–16 px
  code, and 8–10 px tracked metadata. A large Regular glyph may carry the main
  scale contrast; comments use the real italic face.
- Let weight and italic distinguish roles before adding more tonal levels.
- Show the actual forms: single-storey `g`, figures, punctuation, and programming
  ligatures. Do not overload a specimen with every glyph.
- Keep metadata small and factual; align it to the type, not to decorative UI.

## Composition and measurement

Social previews are fixed 1280×640 artboards. Prefer one typographic plane, open
space, and a few hairline rules over nested frames. Measurement guides should be
limited to useful cap-height, x-height, and baseline references, with restrained
ticks and labels. Keep broad edge margins (about 72–76 px) and leave enough
negative space around both code and display glyphs. Use approved metrics only:
cap height 690, x-height 520, Normal advance 600, SemiCondensed advance 540, and
italic angle 11.8°.

Cap height 690 and x-height 520 are the declared design metrics (OS/2
`sCapHeight` / `sxHeight`), not the maximum ink bounds of the outlines. Artwork
must label them as metrics — `CAP METRIC · 690`, `X METRIC · 520` — and must not
present them as measured ink extremes. The metric is where a guide belongs; no
glyph needs to touch it.

## Font and export requirements

Artwork generators must explicitly load the local Regular, Italic, and Bold
artifacts from `site/fonts/` using `@font-face`. Await `document.fonts.ready` and
verify Regular 400, Italic 400, and Bold 700 before rendering. Verify faces by
membership in `document.fonts` (family, style, weight, status `loaded`), not with
`document.fonts.check()`, which reports `true` for families that do not exist.
Do not depend on installed system fonts or a generic fallback during
export. For historical comparison studies only, resolve TX-02 from the
maintainer's local installation; never copy it into this repository or distribute
it. If TX-02 is absent, stop the export rather than substituting another face.
Pin the HTML-to-PNG renderer — it is vendored at
`artwork/vendor/html2canvas-1.4.1.min.js`; do not load it from a CDN.

Compose on a fixed 1280×640 logical plate and export at 2× physical resolution,
so the delivered PNG is **2560×1280** and stays sharp on HiDPI surfaces. The
generator's size assertion must check the delivered size, not the layout size.
Internal comparison canvases use a 2× backing store over their layout box, which
maps 1:1 into the 2× output.

Type must not be placed in inline `<svg>`. The HTML-to-PNG renderer rasterises SVG
subtrees as standalone images, where page `@font-face` rules cannot load, so live
specimens silently export in a fallback serif. Draw measurement diagrams and glyph
comparisons on a `<canvas>`, which is drawn with the loaded faces and copied at its
backing resolution.

## Specimen boxes and glyph fitting

Size every container from measured ink, never from a guessed box. A sample row's
line box must hold the real ascender and descender of both faces at the rendered
size plus clearance; do not use `overflow: hidden` on a glyph container, and do not
use `line-height: 1` with a fixed-height box — both silently crop descenders. For
overlay studies, draw both faces at one em size, one baseline, and one origin:
allocate the cell margin from the union of the faces' ink bounds, never fit one
glyph individually, and never stretch or squash to fill a cell. Size backing buffers
from the element's layout size, never from a CSS-scaled rectangle, so output does
not depend on the browser viewport. Render at a true multiple of the layout size
(2× is sufficient; 4× changes under 0.3% of output pixels). Let the generators
assert these conditions on load and report the result, rather than relying on
visual inspection.
