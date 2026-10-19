# Vendored build dependencies

Files here are exact, unmodified copies so artwork can be regenerated offline and
so a build is reproducible without depending on a remote host.

| File | Version | Source | SHA-256 |
|---|---|---|---|
| `html2canvas-1.4.1.min.js` | 1.4.1 | `https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js` | `e87e550794322e574a1fda0c1549a3c70dae5a93d9113417a429016838eab8cb` |

html2canvas is MIT licensed. Do not edit these files; replace them wholesale and
update the table above, the generator error messages, and `docs/VISUAL_IDENTITY.md`
together.

Why it is vendored: the generators must rasterise identically on any machine, with
no network access. html2canvas also converts inline `<svg>` into standalone images,
where page `@font-face` rules cannot load — so specimen type must be drawn on a
`<canvas>`, not as SVG `<text>`. See `docs/VISUAL_IDENTITY.md`.