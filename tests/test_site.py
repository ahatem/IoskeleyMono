"""Static guards for the showcase site: readable-text contrast and the faces
the Live Lab can request."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "site/css/main.css").read_text(encoding="utf-8")
HTML = (ROOT / "site/index.html").read_text(encoding="utf-8")

# Semantic roles include code glyphs and location references, not just prose.
READABLE = ("primary", "secondary", "grammar", "keyword", "operator",
            "punctuation", "comment", "line-number", "title")


def declarations(body):
    return dict(re.findall(r"(--[a-z-]+|color|background):\s*([^;]+);", body))


def rule(selector):
    clean = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
    result = {}
    for header, body in re.findall(r"([^{}]+)\{([^{}]*)\}", clean):
        # Split selector lists without splitting :is(.code, .diff).
        if selector in re.split(r",\s*(?![^()]*\))", header.strip()):
            result.update(declarations(body))
    return result


def resolve(value, theme):
    while value.startswith("var("):
        value = theme[value[4:-1]]
    return value


def theme_tokens(selector):
    return {**rule(":root"), **rule(selector)}


def effective_background(value, theme):
    value = resolve(value, theme)
    if value.startswith("#"):
        return value
    mix = re.fullmatch(r"color-mix\(in srgb, var\((--[a-z-]+)\) ([\d.]+)%, transparent\)", value)
    if not mix:
        raise AssertionError(f"Unmodelled background: {value}")
    ink = resolve(theme[mix[1]], theme)
    canvas = resolve(theme["--canvas"], theme)
    alpha = float(mix[2]) / 100
    # Preserve fractional channels: do not round a near-threshold failure away.
    return tuple(int(ink[i:i + 2], 16) * alpha + int(canvas[i:i + 2], 16) * (1 - alpha)
                 for i in (1, 3, 5))


def tokens(selector):
    block = re.search(re.escape(selector) + r"\s*\{(.*?)\n\}", CSS, re.S).group(1)
    return dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})\s*;", block))


def luminance(hex_color):
    channels = ([int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
                if isinstance(hex_color, str) else [c / 255 for c in hex_color])
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


class SiteContrast(unittest.TestCase):
    def test_readable_tokens_meet_text_contrast_on_canvas(self):
        for name, selector in (("dark", ":root"), ("light", ':root[data-theme="light"]')):
            theme = theme_tokens(selector)
            for token in READABLE:
                with self.subTest(theme=name, token=token):
                    self.assertGreaterEqual(contrast(resolve(theme["--" + token], theme), theme["--canvas"]), 4.5)

    def test_rendered_semantic_roles_on_canvas_and_filled_rows(self):
        roles = (":is(.code, .diff) .t-keyword", ":is(.code, .diff) .t-operator",
                 ":is(.code, .diff) .t-punct", ":is(.code, .diff) .t-mark",
                 ":is(.code, .diff) .t-comment", ".wb__code .ln::before",
                 ".dr__n", ".dr__s", ".lg-l--error", ".seg__btn",
                 ".seg--quiet .seg__btn")
        surfaces = (None, ".wb__code .ln.is-current", ".dr--add", ".dr--hunk", ".dr--del")
        for selector in (":root", ':root[data-theme="light"]'):
            base = theme_tokens(selector)
            for surface in surfaces:
                overrides = rule(surface) if surface else {}
                theme = {**base, **{k: v for k, v in overrides.items() if k.startswith("--")}}
                background = effective_background(overrides.get("background", "var(--canvas)"), theme)
                # Current Workbench and Review rows contain syntax/gutters only.
                actual_roles = roles if surface is None else roles[:8]
                for role in actual_roles:
                    foreground = rule(role)["color"]
                    if surface == ".dr--del" and role.startswith(":is"):
                        foreground = rule(".dr--del .dr__c *")["color"]
                    if surface == ".dr--add" and role in (".dr__n", ".dr__s"):
                        foreground = rule(".dr--add " + role)["color"]
                    if surface == ".wb__code .ln.is-current" and role == ".wb__code .ln::before":
                        foreground = rule(".wb__code .ln.is-current::before")["color"]
                    with self.subTest(theme=selector, surface=surface, role=role):
                        self.assertGreaterEqual(contrast(resolve(foreground, theme), background), 4.5)
                if surface == ".dr--hunk":
                    self.assertGreaterEqual(contrast(resolve(overrides["color"], theme), background), 4.5)

    def test_scrollbars_preserve_native_access_and_system_colours(self):
        self.assertNotRegex(CSS, r"scrollbar-width:\s*none")
        self.assertIn("@media (forced-colors: none)", CSS)
        self.assertIn("::-webkit-scrollbar-thumb:hover", CSS)
        self.assertIn("::-webkit-scrollbar-thumb:active", CSS)

    def test_identity_colours_are_unchanged(self):
        dark, light = tokens(":root"), tokens(':root[data-theme="light"]')
        self.assertEqual((dark["canvas"], dark["proof-red"]), ("#101010", "#b04a43"))
        self.assertEqual((light["canvas"], light["proof-red"]), ("#f2f0ea", "#913832"))

    def test_comments_still_recede_from_content(self):
        for selector in (":root", ':root[data-theme="light"]'):
            theme = {**tokens(":root"), **tokens(selector)}
            self.assertGreater(contrast(theme["secondary"], theme["canvas"]),
                               contrast(theme["comment"], theme["canvas"]))


class LiveLabFaces(unittest.TestCase):
    def test_bold_italic_faces_exist_for_both_widths(self):
        for name in ("IoskeleyMono-BoldItalic", "IoskeleyMono-SemiCondensedBoldItalic"):
            self.assertTrue((ROOT / "site/fonts" / f"{name}.woff2").is_file(), name)

    def test_editor_layers_share_one_scroller(self):
        # The textarea scrolls; the highlight layer is clipped and follows it.
        rule = re.search(r"\.editor__scroll\s*\{(.*?)\}", CSS, re.S).group(1)
        self.assertIn("overflow: hidden", rule)
        rule = re.search(r"\}\n\.editor__input\s*\{(.*?)\}", CSS, re.S).group(1)
        self.assertIn("overflow: auto", rule)


class NerdTimingNote(unittest.TestCase):
    def test_v210_is_not_said_to_ship_neither_variant(self):
        self.assertNotIn("ship neither variant", HTML)
        self.assertIn("predates the NF / NFM split", HTML)


if __name__ == "__main__":
    unittest.main()
