# Ioskeley Mono

<p align="center">
  <img src="assets/SocialPreview.png" alt="Ioskeley Mono — Free Open Source Monospace Font" width="100%">
</p>

<p align="center">
  <a href="https://github.com/ahatem/IoskeleyMono/releases/latest"><img src="https://img.shields.io/github/v/release/ahatem/IoskeleyMono?style=flat-square&color=b8943a" alt="Latest Release"></a>
  <a href="https://github.com/ahatem/IoskeleyMono/releases"><img src="https://img.shields.io/github/downloads/ahatem/IoskeleyMono/total?style=flat-square&color=333" alt="Downloads"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-SIL%20OFL%201.1-b8943a?style=flat-square" alt="License"></a>
  <a href="https://ahatem.github.io/IoskeleyMono/"><img src="https://img.shields.io/badge/showcase-interactive%20demo-b8943a?style=flat-square" alt="Showcase"></a>
</p>

<p align="center">
  <strong>A free, open-source monospace font engineered to deliver the aesthetic, geometry, and metric parity of <a href="https://berkeleygraphics.com/typefaces/berkeley-mono/">Berkeley Mono</a>.</strong><br>
  Built by configuring <a href="https://github.com/be5invis/Iosevka">Iosevka</a> with custom glyph variants, metrics, and weight distributions.
</p>

<p align="center">
  <a href="https://ahatem.github.io/IoskeleyMono/"><strong>Explore Live Showcase →</strong></a> &nbsp;|&nbsp; 
  <a href="https://github.com/ahatem/IoskeleyMono/releases/latest"><strong>Download Latest Release →</strong></a>
</p>

---

## ⚡ Highlights

- **📐 Metric & Geometric Parity**: Custom line height, letter spacing, and character bounds tuned to Berkeley Mono's compact density.
- **🎨 10 Weights & 2 Widths**: Full weight spectrum (Thin `100` → Black `900`) across Normal and SemiCondensed, each with matching true italics (40 styles total).
- **🔤 Distinctive Glyph Engineering**: Dotted `0`, single-storey `g`, flat-arc parentheses `()`, open-contour `6` and `9`, two-circle `8`, raised underscore, and square punctuation.
- **💻 Tailored Variants**: Out-of-the-box support for Nerd Font icons, strict terminal grid alignment (`Term`), and ligature-free environments (`NL`).
- **🌐 Web Ready**: Pre-packaged WOFF2 web fonts with optimized `@font-face` definitions.

---

## 🔍 Comparison with Berkeley Mono

Ioskeley Mono is calibrated across character shapes, pixel overlays, and real-world code density.

### 01. Character Forms
> Exact identity glyphs, ambiguity-free numeral forms, compact punctuation bounds, and programming operators.

![Ioskeley Mono vs Berkeley Mono - Character Forms](assets/01-Ioskeley-vs-Berkeley-Character-Forms.png)

### 02. Pixel Overlay
> 1:1 origin and baseline overlay showing shared shape agreement (ivory) and minimal edge variances (colored).

![Ioskeley Mono vs Berkeley Mono - Pixel Overlay](assets/02-Ioskeley-vs-Berkeley-Pixel-Overlay.png)

### 03. Real-World Code Specimen
> Identical rhythm, line spacing, tracking, and visual weight in typical editor themes.

![Ioskeley Mono vs Berkeley Mono - Real Code](assets/03-Ioskeley-vs-Berkeley-Real-Code.png)

---

## 📦 Downloads & Variants

Grab pre-built packages from the [Releases page](https://github.com/ahatem/IoskeleyMono/releases/latest).

| Package | Use Case | Ligatures | Nerd Icons |
|---|---|:---:|:---:|
| **`IoskeleyMono.zip`** *(Recommended)* | VS Code, JetBrains, Zed, Sublime Text, Cursor | ✅ | — |
| **`IoskeleyMono-NerdFont.zip`** | Editors that show Nerd Font icons in file trees and status bars | ✅ | ✅ |
| **`IoskeleyMono-Term.zip`** *(terminals)* | Kitty, Ghostty, WezTerm, Alacritty | ✅ | — |
| **`IoskeleyMono-Term-NerdFont.zip`** *(terminals + icons)* | Kitty, Ghostty, WezTerm with Neovim, Starship, zsh | ✅ | ✅ |
| **`IoskeleyMono-NL.zip`** | Environments with forced ligatures (e.g. Xcode) | ❌ | — |
| **`IoskeleyMono-NL-NerdFont.zip`** | No ligatures + Nerd Font icons | ❌ | ✅ |
| **`IoskeleyMono-Web.zip`** | Web / CSS `@font-face` — small subset (Latin, punctuation, arrows, box drawing, ≈94 KB/face) | ✅ | — |
| **`IoskeleyMono-Web-Full.zip`** | Web / CSS `@font-face` — full coverage (Greek, Cyrillic, long arrows, rare math) | ✅ | — |

> **On the web, prefer `IoskeleyMono-Web.zip`.** The `-Full` zip is for sites
> that display characters outside the subset — Greek and Cyrillic text, long
> arrows, or the rarer math operators. Both zips use the same filenames
> (`IoskeleyMono-*.woff2`), so swapping one for the other works without editing
> a single `@font-face` rule.

> **In a terminal, take a `Term` build.** They redraw arrows and box-drawing to sit inside the cell, and they're the ones detected as monospace by fontconfig and macOS Font Book.

<details>
<summary><strong>📁 Package Internal Structure (Widths & Hinting)</strong></summary>

Every TTF package contains both widths, organized by screen rendering target:

```
Normal/
  Hinted/    ← ClearType / standard-DPI screens (Windows)
  Unhinted/  ← High-DPI / Retina screens (macOS, Linux HiDPI)
SemiCondensed/
  Hinted/
  Unhinted/
```
> *Recommendation:* If using macOS or high-DPI displays, install `Unhinted/`. For Windows standard-DPI monitors, install `Hinted/`.
</details>

---

## 🚀 Quick Setup & Editor Configuration

### Installation

**macOS (Homebrew)** — thanks to [@zhimoe](https://github.com/zhimoe), [@ForsakenHarmony](https://github.com/ForsakenHarmony) and [@frovere](https://github.com/frovere), Ioskeley is in the official casks:

```bash
brew install --cask font-ioskeley-mono
```

Or install manually:

- **macOS**: Unzip → Select all `.ttf` files in your chosen folder → Double click & click **Install Font** (or drag into Font Book).
- **Windows**: Unzip → Select all `.ttf` files → Right click → **Install for all users**.
- **Linux**: Unzip → Copy `.ttf` files to `~/.local/share/fonts/` (or `~/.fonts/`) → Run `fc-cache -fv`.

### Editor Configuration

#### VS Code / Cursor
```json
{
  "editor.fontFamily": "'Ioskeley Mono', monospace",
  "editor.fontLigatures": true,
  "editor.fontWeight": "400",
  "editor.fontSize": 14.5,
  "editor.lineHeight": 1.55
}
```
*(If using the Nerd Font variant, set `"editor.fontFamily": "'IoskeleyMono Nerd Font', monospace"`)*

#### Zed
```json
{
  "buffer_font_family": "Ioskeley Mono",
  "buffer_font_size": 15,
  "buffer_line_height": "comfortable"
}
```

#### Ghostty
```ini
font-family = Ioskeley Mono
font-size = 14
```

#### Alacritty
```toml
[font.normal]
family = "Ioskeley Mono"
style = "Regular"
```

#### Kitty
```conf
font_family      Ioskeley Mono Term
bold_font        auto
italic_font      auto
bold_italic_font auto
font_size        14.0
```
*(With the Nerd Font package, use `IoskeleyMonoTerm Nerd Font Mono`.)*

---

## 🔡 Font Features

Ioskeley ships several OpenType features you can switch on per-app. The most
asked-for is `zero`, which swaps the dotted zero for a slashed one.

| Feature | Effect |
|---|:---|
| `zero` | Slashed zero instead of dotted |
| `calt` | Programming ligatures (on by default) |
| `dlig` | Discretionary ligatures |
| `onum` | Old-style figures |
| `frac` | Fractions |

```jsonc
// VS Code / Cursor
"editor.fontLigatures": "'calt', 'zero'"
```
```ini
# Ghostty
font-feature = zero
```
```conf
# Kitty
font_features IoskeleyMono +zero
```
```css
/* CSS */
font-feature-settings: "zero";
```

---

## 📊 Weight Spectrum

Ioskeley Mono provides a full continuous weight spectrum across both widths:

| Weight Name | CSS `font-weight` | Upright | Italic |
|---|---|:---:|:---:|
| **Thin** | `100` | Included | Included |
| **ExtraLight** | `200` | Included | Included |
| **Light** | `300` | Included | Included |
| **SemiLight** | `350` | Included | Included |
| **Regular** | `400` | Included | Included |
| **Medium** | `500` | Included | Included |
| **SemiBold** | `600` | Included | Included |
| **Bold** | `700` | Included | Included |
| **ExtraBold** | `800` | Included | Included |
| **Black** | `900` | Included | Included |

---

## 🛠️ Build from Source

Builds are executed via GitHub Actions on tagged releases. To reproduce locally:

```bash
# 1. Clone repositories
git clone https://github.com/ahatem/IoskeleyMono.git
git clone --depth 1 https://github.com/be5invis/Iosevka.git

# 2. Copy the customized build plan
cp IoskeleyMono/private-build-plans.toml Iosevka/

# 3. Install dependencies and compile
cd Iosevka
npm install
npm run build -- contents::IoskeleyMono contents::IoskeleyMonoTerm contents::IoskeleyMonoNL contents::IoskeleyMonoWeb
```
Compiled binaries land in `Iosevka/dist/<PlanName>/`. The workflow pins Iosevka to a known-good tag; check [`build-font.yml`](.github/workflows/build-font.yml) for the current one.

---

## 🤝 Contributing

Contributions, glyph refinement proposals, and build plan tweaks are welcome!
- For proposed character adjustments, check [`private-build-plans.toml`](./private-build-plans.toml).
- Submit bug reports, ligature suggestions, or PRs via GitHub Issues.

---

## ☕ Support

If Ioskeley Mono enhances your daily coding workflow or saves you font licensing fees, consider supporting ongoing development:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ahmedhatem-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/ahmedhatem)

---

## 📜 License & Acknowledgments

- **Ioskeley Mono** is released under the [SIL Open Font License 1.1](./LICENSE).
- Built on top of the [Iosevka](https://github.com/be5invis/Iosevka) font generation engine by [Belleve Invis](https://github.com/be5invis) and contributors.
- Design aesthetic inspired by [Berkeley Mono](https://berkeleygraphics.com/typefaces/berkeley-mono/) by Berkeley Graphics.
