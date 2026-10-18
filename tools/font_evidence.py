"""Read-only font inspection helpers shared by validation and build checks."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = [ord(c) for c in " HxMWmn0O1Il|gj_()—…→─"] + [0x301, 0x200B, 0xE0B0, 0xE0B2, 0xF0C12, 0xE711, 0xF113, 0x276C]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_digest(value) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def check_validation_runtime() -> None:
    import importlib.metadata
    import platform
    locked_minor = json.loads((ROOT / "tools/toolchain.lock.json").read_text())["python_minor"]
    if not platform.python_version().startswith(locked_minor + "."):
        raise RuntimeError(f"Use Python {locked_minor}.x for the recorded validation contract")
    for line in (ROOT / "tools/requirements.txt").read_text().splitlines():
        if line and not line.startswith("#"):
            name, version = line.split("==")
            if importlib.metadata.version(name) != version:
                raise RuntimeError(f"Install tools/requirements.txt: {name} must be {version}")


def inspect_font(path: Path | bytes) -> dict:
    data = path if isinstance(path, bytes) else path.read_bytes()
    with TTFont(io.BytesIO(data), recalcTimestamp=False) as font:
        cmap = font.getBestCmap()
        os2, post, hhea = font["OS/2"], font["post"], font["hhea"]
        names = {str(i): font["name"].getDebugName(i) for i in [0, 1, 2, 3, 4, 5, 6, 13, 14, 16, 17]}
        tables = {}
        # Exclude only container/checksum and clock fields from semantic evidence.
        # Everything else, including outlines, hint programs and shaping, is retained.
        for tag in sorted(font.keys()):
            if tag == "GlyphOrder":
                continue
            if tag == "head":
                old = font[tag].created, font[tag].modified, font[tag].checkSumAdjustment
                font[tag].created = font[tag].modified = 2082844800
                font[tag].checkSumAdjustment = 0
            tables[tag] = digest(font.getTableData(tag))
            if tag == "head":
                font[tag].created, font[tag].modified, font[tag].checkSumAdjustment = old
        glyphs = font.getGlyphSet()
        samples = {}
        for cp in SAMPLES:
            if cp not in cmap:
                samples[f"U+{cp:04X}"] = None
                continue
            glyph = cmap[cp]
            pen = BoundsPen(glyphs)
            glyphs[glyph].draw(pen)
            advance, lsb = font["hmtx"][glyph]
            bounds = pen.bounds
            samples[f"U+{cp:04X}"] = {
                "advance": advance, "lsb": lsb, "bounds": bounds,
                "occupied_width_ratio": (bounds[2] - bounds[0]) / advance if bounds and advance else None,
                "horizontal_overhang": bool(bounds and (bounds[0] < 0 or bounds[2] > advance)),
                "outside_win_metrics": bool(bounds and (bounds[1] < -os2.usWinDescent or bounds[3] > os2.usWinAscent)),
            }
        features = {}
        for tag in ("GSUB", "GPOS"):
            table = font[tag].table if tag in font else None
            features[tag] = sorted({r.FeatureTag for r in table.FeatureList.FeatureRecord}) if table and table.FeatureList else []
        semantic = {
            "names": names, "upm": font["head"].unitsPerEm,
            "weight": os2.usWeightClass, "width": os2.usWidthClass,
            "fs_selection": os2.fsSelection, "mac_style": font["head"].macStyle,
            "fixed_pitch": post.isFixedPitch, "panose_proportion": os2.panose.bProportion,
            "post_format": post.formatType, "italic_angle": post.italicAngle,
            "font_revision": font["head"].fontRevision,
            "x_height": os2.sxHeight, "cap_height": os2.sCapHeight,
            "typo_metrics": [os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap],
            "win_metrics": [os2.usWinAscent, os2.usWinDescent],
            "hhea_metrics": [hhea.ascent, hhea.descent, hhea.lineGap],
            "glyph_count": len(font.getGlyphOrder()), "cmap_count": len(cmap),
            "cmap_hash": json_digest(sorted(cmap.items())),
            "glyph_order_hash": json_digest(font.getGlyphOrder()),
            "hmtx_hash": json_digest(font["hmtx"].metrics),
            "advance_histogram": {str(a): sum(font["hmtx"][g][0] == a for g in cmap.values()) for a in sorted({font["hmtx"][g][0] for g in cmap.values()})},
            "features": features, "samples": samples, "table_semantic_sha256": tables,
        }
        raw_tables = {tag: digest(font.reader[tag]) for tag in sorted(font.reader.keys())}
        return {"bytes": len(data), "sha256": digest(data),
                "raw_table_sha256": raw_tables,
                "created": font["head"].created, "modified": font["head"].modified,
                "semantic_sha256": json_digest(semantic), "semantic": semantic}
