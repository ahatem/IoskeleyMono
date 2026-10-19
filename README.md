# Ioskeley Mono

[![Latest release](https://img.shields.io/github/v/release/ahatem/IoskeleyMono?style=flat-square)](https://github.com/ahatem/IoskeleyMono/releases/latest)
[![SIL Open Font License 1.1](https://img.shields.io/badge/license-SIL%20OFL%201.1-blue?style=flat-square)](./LICENSE)

An open programming typeface built on Iosevka — compact, geometric, and tuned for editors and terminals.

> Technical character without visual noise. Compact without feeling crushed.

## Why Ioskeley

Ioskeley brings a distinctive, geometric voice to Iosevka’s compact proportions, with clear forms for code and long sessions in editors and terminals. Berkeley Mono (TX-02) was an early inspiration; Ioskeley has since evolved into its own typeface, not a clone or specification match.

## Choose a family

| Family | Programming ligatures | Choose it for |
|---|:---:|---|
| **Standard** — `Ioskeley Mono` | Yes | General editor use. |
| **Term** — `Ioskeley Mono Term` | Yes | Terminal-oriented spacing and arrow/box-drawing forms. |
| **NL** — `Ioskeley Mono NL` | No | Apps where ligatures cannot be disabled, or when you prefer none. |

All three families include ten static weights from Thin through Black, each in upright and italic styles.

## Choose a width

| Width | Choose it when |
|---|---|
| **Normal** | You want the standard width and spacing. |
| **SemiCondensed** | You want to fit more code on a line; its advances are 90% of Normal. |

Both widths are included in the desktop and Nerd Font packages. Choose a width folder when installing.

## Nerd Font variants

Each Nerd Font archive includes both variants:

- **Nerd Font (NF):** ordinary Nerd Fonts geometry with larger icons. The usual choice when you want icons; some icons may extend beyond one cell.
- **Nerd Font Mono (NFM):** strict one-cell advances for software or font pickers that require true monospace behavior.

Neither is universally better: choose based on what the application needs. NF and NFM are included in the Standard, Term, and NL Nerd Font archives.

## Downloads and installation

Choose an archive for the family you want. Each Nerd Font archive contains the NF and NFM variants described above.

| Build | Desktop archive | With Nerd Font variants |
|---|---|---|
| Standard | [`IoskeleyMono.zip`](https://github.com/ahatem/IoskeleyMono/releases/latest/download/IoskeleyMono.zip) | [`IoskeleyMono-NerdFont.zip`](https://github.com/ahatem/IoskeleyMono/releases/latest/download/IoskeleyMono-NerdFont.zip) |
| Term | [`IoskeleyMono-Term.zip`](https://github.com/ahatem/IoskeleyMono/releases/latest/download/IoskeleyMono-Term.zip) | [`IoskeleyMono-Term-NerdFont.zip`](https://github.com/ahatem/IoskeleyMono/releases/latest/download/IoskeleyMono-Term-NerdFont.zip) |
| NL | [`IoskeleyMono-NL.zip`](https://github.com/ahatem/IoskeleyMono/releases/latest/download/IoskeleyMono-NL.zip) | [`IoskeleyMono-NL-NerdFont.zip`](https://github.com/ahatem/IoskeleyMono/releases/latest/download/IoskeleyMono-NL-NerdFont.zip) |
| Web | [Subset](https://github.com/ahatem/IoskeleyMono/releases/latest/download/IoskeleyMono-Web.zip) · [Full](https://github.com/ahatem/IoskeleyMono/releases/latest/download/IoskeleyMono-Web-Full.zip) | — |

The **Web** archive is a smaller WOFF2 subset for common Latin text, punctuation, arrows, math, and box drawing. **Web Full** contains the desktop glyph repertoire, including Greek, Cyrillic, and less common symbols. Both use the same public filenames inside the archive.

Product details on this page describe **v2.2.0**. Download links target the latest published release, not version-specific URLs. Before v2.2.0 is published, they serve **v2.1.0**, whose Nerd Font archives predate the NF/NFM split described above. After publication, the same links resolve to v2.2.0 assets. No unreleased 2.2.0 URLs are used here.

For desktop fonts, install the `.ttf` files from the chosen width and rendering folders. Use **Hinted** for standard-density Windows/Linux displays and **Unhinted** for macOS or HiDPI displays. Nerd Font archives do not have separate hinted/unhinted sets.

- **Windows:** right-click the selected fonts and choose **Install**.
- **macOS:** open the fonts in Font Book and choose **Install**.
- **Linux:** copy them to `~/.local/share/fonts/IoskeleyMono/`, then run `fc-cache -fv`.

Restart open applications after installation. In VS Code, for example:

```json
{
  "editor.fontFamily": "'Ioskeley Mono', monospace",
  "editor.fontLigatures": true
}
```

Use the installed family name for Term, NL, or a Nerd Font variant instead. The slashed-zero `zero` feature can be enabled in applications that support it.

## Build from source

Contributors: see [Build, validation, and release](./docs/BUILD_AND_RELEASE.md) for prerequisites, the reproducible build and validation process, package details, and publishing boundaries. The [build plan](./private-build-plans.toml) is the source for glyph and metric configuration.

## Credits and license

Ioskeley began as an Iosevka configuration inspired by the technical character of Berkeley Mono (TX-02). It has since evolved into its own open programming typeface. Berkeley Mono is a commercial typeface by Neil Panchal / [Berkeley Graphics](https://berkeleygraphics.com/typefaces/berkeley-mono/); its font files are not distributed here. Ioskeley is independent and is not affiliated with or endorsed by Berkeley Graphics.

Ioskeley Mono is built with [Iosevka](https://github.com/be5invis/Iosevka), created by Belleve Invis and its contributors. The icon variants use [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts). Ioskeley Mono is licensed under the [SIL Open Font License 1.1](./LICENSE); upstream projects and assets remain subject to their own licenses.

**Author:** Ahmed Hatem <ahatem925@gmail.com>
