# Ioskeley Mono

![Ioskeley Mono Cover](assets/SocialPreview.png)

A free, open-source alternative to [Berkeley Mono](https://berkeleygraphics.com/typefaces/berkeley-mono/) — built by configuring [Iosevka](https://github.com/be5invis/Iosevka) to match its look and feel as closely as possible.

The name is a mashup: **Iosevka** + **Berkeley** = **Ioskeley**.

---

## Preview

| Ioskeley Mono | Berkeley Mono |
| --- | --- |
| ![Ioskeley Mono Sample](assets/IoskeleyMono.png) | ![Berkeley Mono Sample](assets/BerkeleyMono.png) |

> Theme: [Kintsugi Dark Flared](https://marketplace.visualstudio.com/items?itemName=ahmedhatem.kintsugi)

![Ioskeley Mono in Action](assets/InAction.png)

---

## Installation

Download the latest release from the [Releases page](https://github.com/ahatem/IoskeleyMono/releases).

### Which file should I download?

**Step 1 — Pick your use case:**

| I want to…                       | Download                              |
|----------------------------------|---------------------------------------|
| Use it in my editor / IDE        | A TTF zip                             |
| Use it in my terminal with icons | A Nerd Font zip of Ioskeley Mono Term |
| Use it on the web                | `IoskeleyMono-Web.zip`                |

**Step 2 — Pick your width:**

| Width | Best for |
|---|---|
| `Normal` | Default — works everywhere |
| `SemiCondensed` | More columns without sacrificing readability |
| `Condensed` | Maximum density |

> Not sure? Start with **Normal**.

### Installing the fonts

1. Download and unzip your chosen file
2. Select all `.ttf` files inside
3. Install on your system:
   - **macOS** — double-click any font → Install Font, or drag all into Font Book
   - **Windows** — select all → right-click → Install
   - **Linux** — copy to `~/.local/share/fonts/` then run `fc-cache -fv`

---

## Weights

Ioskeley Mono matches Berkeley Mono's full weight axis across all widths:

| Weight | CSS value |
|---|---|
| Thin | 100 |
| ExtraLight | 200 |
| Light | 300 |
| SemiLight | 350 |
| Regular | 400 |
| Medium | 500 |
| SemiBold | 600 |
| Bold | 700 |
| ExtraBold | 800 |
| Black | 900 |

Every weight is available in both **Upright** and **Italic**.

---

## Design Choices

Ioskeley Mono uses specific character variants and custom metrics to closely match Berkeley Mono's aesthetic.

**Custom metrics** — vertical proportions, letter spacing, and parenthesis size are tuned to capture Berkeley's compact, geometric feel.

**Distinctive glyphs** — single-storey `g`, flat-arc parentheses `()`, two-circle `8`, dotted `0`, open-contour `6` and `9`, square punctuation dots, and a raised underscore.

For the full list of configuration choices, see [`private-build-plans.toml`](./private-build-plans.toml).

---

## Ioskeley Mono Term

This is a variant of Ioskeley Mono tuned for terminal emulators. It has narrower arrows and geometric symbols.

---

## Building from Source

The font is built automatically via GitHub Actions on every version tag push. To build locally:

```bash
git clone https://github.com/ahatem/IoskeleyMono.git
git clone --depth 1 https://github.com/be5invis/Iosevka.git

cp IoskeleyMono/private-build-plans.toml Iosevka/
cd Iosevka
npm install
npm run build -- contents::IoskeleyMono
```

Output will be in `Iosevka/dist/IoskeleyMono/`.

To build the terminal variant afterward:

```bash
npm run build -- contents::IoskeleyMonoTerm
```

Output will be in `Iosevka/dist/IoskeleyMonoTerm/`.

---

## Contributing

This project is just a build configuration on top of Iosevka — changes are often just a few lines in `private-build-plans.toml`. If you spot something off or have an idea, open an issue or send a PR. All contributions are welcome!

---

## License & Credits

Ioskeley Mono and Ioskeley Mono Term are a custom configuration of [Iosevka](https://github.com/be5invis/Iosevka). All credit for the original design and build system goes to [Belleve Invis](https://github.com/be5invis) and the Iosevka contributors.

Licensed under the [SIL Open Font License 1.1](./LICENSE).
