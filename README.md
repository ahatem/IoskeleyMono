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

> Theme: [Kanagawa Dragon Theme](https://plugins.jetbrains.com/plugin/27101-kanagawa-dragon-theme)
---

## Installation

Download the latest release from the [Releases page](https://github.com/ahatem/IoskeleyMono/releases).

### Which file do I need?

| Situation | Download |
|---|---|
| Editor or IDE (VS Code, JetBrains, Zed…) | `IoskeleyMono.zip` |
| Terminal with icons (Neovim, Starship…) | `IoskeleyMono-NerdFont.zip` |
| Arrows or box-drawing look wrong in my terminal | `IoskeleyMono-Term.zip` |
| Terminal with icons _and_ rendering issues | `IoskeleyMono-Term-NerdFont.zip` |
| App that can't disable ligatures (Xcode…) | `IoskeleyMono-NL.zip` |
| Same, but also need Nerd Font icons | `IoskeleyMono-NL-NerdFont.zip` |
| Web / CSS (`@font-face`) | `IoskeleyMono-Web.zip` |

> **Not sure?** Start with `IoskeleyMono.zip`.

### What's inside each TTF zip?

Every TTF zip contains all three widths, each with hinted and unhinted variants:

```
Normal/
  Hinted/    ← standard-DPI screens (most Windows setups)
  Unhinted/  ← high-DPI / Retina (macOS, Linux HiDPI)
SemiCondensed/
  Hinted/
  Unhinted/
Condensed/
  Hinted/
  Unhinted/
```

Install all fonts in your chosen folder — your OS will expose the full weight axis (Thin → Black) automatically. Start with `Normal/` if you're unsure which width you prefer.

### Installing the fonts

1. Download and unzip your chosen file
2. Open the width and hint folder that matches your setup
3. Select all `.ttf` files and install:
   - **macOS** — double-click any font → Install Font, or drag all into Font Book
   - **Windows** — select all → right-click → Install for all users
   - **Linux** — copy to `~/.local/share/fonts/` then run `fc-cache -fv`

### About the Term variant

`Ioskeley Mono Term` uses `spacing = "term"`, which constrains every glyph to its cell boundary. Use it if arrows (`→ ← ↑ ↓`), box-drawing characters, or ligatures render incorrectly in your terminal (known affected: kitty, Ghostty). The glyph design is identical to the standard variant — it's purely a spacing change.

### About the NL variant

`Ioskeley Mono NL` has all ligature substitutions disabled. Use it in apps that can't toggle ligatures off themselves (e.g. Xcode). Everything else — weights, widths, glyph shapes, metrics — is identical to the standard variant.

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

Every weight is available in all three widths, both Upright and Italic.

---

## Design Choices

Ioskeley Mono uses specific character variants and custom metrics to closely match Berkeley Mono's aesthetic.

**Custom metrics** — vertical proportions, letter spacing, and parenthesis size are tuned to capture Berkeley's compact, geometric feel.

**Distinctive glyphs** — single-storey `g`, flat-arc parentheses `()`, two-circle `8`, dotted `0`, open-contour `6` and `9`, square punctuation dots, and a raised underscore.

For the full list of configuration choices, see [`private-build-plans.toml`](./private-build-plans.toml).

---

## Building from Source

The font is built automatically via GitHub Actions on every version tag push. To build locally:

```bash
git clone https://github.com/ahatem/IoskeleyMono.git
git clone --depth 1 https://github.com/be5invis/Iosevka.git

cp IoskeleyMono/private-build-plans.toml Iosevka/
cd Iosevka
npm install
npm run build -- contents::IoskeleyMono contents::IoskeleyMonoTerm
```

Output will be in `Iosevka/dist/IoskeleyMono/` and `Iosevka/dist/IoskeleyMonoTerm/`.

---

## Contributing

This project is just a build configuration on top of Iosevka — changes are often just a few lines in `private-build-plans.toml`. If you spot something off or have an idea, open an issue or send a PR. All contributions are welcome!

---

## Support

If Ioskeley Mono saves you money on a font license, consider buying me a coffee — it keeps the project going!

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ahmedhatem-FFDD00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/ahmedhatem)

---

## License & Credits

Ioskeley Mono is a custom configuration of [Iosevka](https://github.com/be5invis/Iosevka). All credit for the original design and build system goes to [Belleve Invis](https://github.com/be5invis) and the Iosevka contributors.

Licensed under the [SIL Open Font License 1.1](./LICENSE).
