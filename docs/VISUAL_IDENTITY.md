# Ioskeley visual identity

Ioskeley is its own typeface identity: a monochrome, typography-led technical
publication. **Grammar recedes; content remains.** The font—not a brand hue—is
the identifying color. Preserve generous negative space, precise alignment,
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
| Punctuation | `#686763` | `#918E87` |
| Comments | `#5F5D58` italic | `#A09D95` italic |
| Rare emphasis | `#ECE9E2` | `#171614` |
| Rule | `#343330` | `#D3D0C8` |
| Guide | `#4A4843` | `#BDBAB2` |
| Selection | `#302F2B` | `#E2DFD8` |

Keep emphasis rare. Use primary/secondary for identifiers and meaningful values;
use grammar tones for keywords, operators, and punctuation. In light mode grammar
moves toward the paper. Do not add a branding hue by default.

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

## Font and export requirements

Artwork generators must explicitly load the local Regular, Italic, and Bold
artifacts from `site/fonts/` using `@font-face`. Await `document.fonts.ready` and
verify Regular 400, Italic 400, and Bold 700 with `document.fonts.check()` before
rendering. Do not depend on installed system fonts or a generic fallback during
export. For historical comparison studies only, resolve TX-02 from the
maintainer's local installation; never copy it into this repository or distribute
it. Pin the HTML-to-PNG renderer and export at exactly 1280×640.
