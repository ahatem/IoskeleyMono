"""Static guards for the showcase site: readable-text contrast and the faces
the Live Lab can request."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "site/css/main.css").read_text(encoding="utf-8")
HTML = (ROOT / "site/index.html").read_text(encoding="utf-8")

# Tokens that carry readable text (comments, labels, unselected controls).
READABLE = ("primary", "secondary", "grammar", "comment")


def tokens(selector):
    block = re.search(re.escape(selector) + r"\s*\{(.*?)\n\}", CSS, re.S).group(1)
    return dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})\s*;", block))


def luminance(hex_color):
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


class SiteContrast(unittest.TestCase):
    def test_readable_tokens_meet_text_contrast_on_canvas(self):
        for name, selector in (("dark", ":root"), ("light", ':root[data-theme="light"]')):
            theme = {**tokens(":root"), **tokens(selector)}
            for token in READABLE:
                with self.subTest(theme=name, token=token):
                    self.assertGreaterEqual(contrast(theme[token], theme["canvas"]), 4.5)

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
