"""Validate the current fonts and packages."""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import sys
import shutil
import subprocess
import tempfile
import platform
import importlib.metadata
import unicodedata
import zipfile

from fontTools.ttLib import TTFont
import uharfbuzz as hb

from font_evidence import ROOT, digest, inspect_font, json_digest, check_validation_runtime

CONTRACT = json.loads((ROOT / "tools/release-contract.json").read_text())
FONT_COUNT = sum(spec["count"] for spec in CONTRACT["packages"].values())
CORPUS = json.loads((ROOT / "tests/specimens.json").read_text())


class Results:
    def __init__(self):
        self.errors = []
        self.warnings = set()
        self.fonts = {}
        self.archives = {}

    def check(self, condition, message):
        if not condition:
            self.errors.append(message)

    def warn(self, message):
        self.warnings.add(message)

    def write(self, path):
        result = {"errors": self.errors, "warnings": sorted(self.warnings), "fonts": self.fonts, "archives": self.archives,
                  "validation_runtime": {"python": platform.python_version(), "fonttools": importlib.metadata.version("fonttools"), "brotli": importlib.metadata.version("brotli"), "uharfbuzz": importlib.metadata.version("uharfbuzz"), "harfbuzz": hb.version_string()},
                  "verdict": "FAIL" if self.errors else "PASS"}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"report": str(path), "fonts": len(self.fonts), "archives": len(self.archives), "error_count": len(self.errors), "errors": self.errors[:20],
                          "warning_count": len(self.warnings), "warnings": sorted(self.warnings), "verdict": result["verdict"]}, indent=2), flush=True)
        return bool(self.errors)


def sfnt(data):
    with TTFont(io.BytesIO(data), recalcTimestamp=False) as font:
        font.flavor = None
        buf = io.BytesIO()
        font.save(buf, reorderTables=False)
        return buf.getvalue()


def shaping(data):
    font = hb.Font(hb.Face(sfnt(data)))
    font.scale = (font.face.upem, font.face.upem)
    result = {}
    for text in CORPUS["ligatures"] + CORPUS["terminal"] + CORPUS["ambiguity"] + CORPUS["combining"] + CORPUS["zero_width"]:
        modes = {}
        for enabled in (False, True):
            buf = hb.Buffer()
            buf.add_str(text)
            buf.guess_segment_properties()
            buf.language = "en"
            hb.shape(font, buf, {"calt": enabled, "dlig": enabled, "liga": enabled})
            modes[str(enabled)] = [[i.codepoint, i.cluster, p.x_advance, p.y_advance, p.x_offset, p.y_offset]
                                  for i, p in zip(buf.glyph_infos, buf.glyph_positions)]
        result[text] = modes
    return result


def expects_bold(weight, nerd):
    # Iosevka sets the legacy bold linkage for its whole bold class (weight > 650),
    # so ExtraBold and Black are bold-linked even though only Bold is a RIBBI style.
    # Nerd Fonts 3.5.0 patching clears those bits above RIBBI Bold, so Nerd
    # archives are expected to link only weight 700. Both profiles are explicit.
    return weight == 700 if nerd else weight > 650


def check_font(data, key, plan, nerd, results):
    ev = inspect_font(data)
    s = ev["semantic"]
    results.fonts[key] = ev
    checks = lambda condition, message: results.check(condition, f"{key}: {message}")
    checks(set(CONTRACT["required_tables"]) <= set(s["table_semantic_sha256"]), "missing required tables")
    names = s["names"]
    for i in [1, 2, 4, 5, 6] + ([] if nerd else [16, 17]):
        checks(bool(names[str(i)]), f"missing name ID {i}")
    checks(bool(names["13"] or names["14"]), "missing embedded license evidence")
    checks(" " not in (names["6"] or ""), "PostScript name contains spaces")
    family = plan + " Nerd Font Mono" if nerd else CONTRACT["plans"][plan]["family"]
    if names["16"] or not nerd:
        checks(names["16"] == family, f"unexpected typographic family {names['16']!r}; expected {family!r}")
    checks(bool(names["16"]) == bool(names["17"]), "incomplete typographic name pair")
    checks((names["1"] or "").startswith(family), "legacy family ID 1 does not match package")
    checks((names["4"] or "").startswith(family), "full name ID 4 does not match package")
    checks(s["weight"] in CONTRACT["weights"].values(), "unexpected weight class")
    if nerd and (s["width"] != 5 or s["weight"] not in {400, 700}):
        checks(bool(names["16"]) and bool(names["17"]), "non-RIBBI Nerd style lost its typographic names")
    widths = [name for name, spec in CONTRACT["widths"].items() if spec["class"] == s["width"]]
    checks(len(widths) == 1, "unexpected width class")
    width = widths[0] if widths else "Normal"
    cell = CONTRACT["widths"][width]["advance"]
    italic = bool(s["fs_selection"] & 1)
    checks(italic == bool(s["mac_style"] & 2) == (s["italic_angle"] != 0), "inconsistent italic flags")
    checks(italic == ("Italic" in (names["17"] or names["2"] or "")), "italic naming linkage mismatch")
    bold = expects_bold(s["weight"], nerd)
    checks(bool(s["fs_selection"] & 32) == bold, "bold linkage mismatch")
    checks(bool(s["mac_style"] & 1) == bold, "macStyle bold linkage mismatch")
    checks(s["fixed_pitch"] == 1, "post.isFixedPitch must remain set")
    checks(s["panose_proportion"] == 9, "monospace PANOSE proportion changed")
    metrics = CONTRACT["metrics"]
    checks(s["x_height"] == metrics["x_height"] and s["cap_height"] == metrics["cap_height"], "design metrics drifted")
    checks(s["typo_metrics"] == metrics["typo"], "typo metrics drifted")
    checks(s["win_metrics"] == metrics["win"], "Windows metrics drifted")
    checks(s["hhea_metrics"] == (metrics["nerd_hhea"] if nerd else metrics["hhea"]), "hhea metrics drifted")
    version = CONTRACT["version"]
    if version["name_id_5_product"] not in names["5"]:
        if version["name_id_5_upstream"] in names["5"]:
            results.warn(f"name ID 5 retains upstream Iosevka version {version['name_id_5_upstream']}")
        else:
            checks(False, "unexpected version metadata")
    with TTFont(io.BytesIO(data), recalcTimestamp=False) as font:
        cm = font.getBestCmap()
        glyph_order = font.getGlyphOrder()
        # ASCII text must occupy one cell. Combining marks and intended wide symbols
        # are checked separately; plain Term is deliberately not fontconfig-mono.
        checks(all(c in cm and font["hmtx"][cm[c]][0] == cell for c in range(32, 127)), "ordinary ASCII cell advances changed")
        mark_expected = cell if nerd else 0
        checks(0x301 in cm and font["hmtx"][cm[0x301]][0] == mark_expected, "combining acute raw advance changed")
        checks(0x200B in cm and font["hmtx"][cm[0x200B]][0] == mark_expected, "zero-width-space raw advance profile changed")
        marks = [font["hmtx"][g][0] for c, g in cm.items() if unicodedata.category(chr(c)) in {"Mn", "Me"}]
        checks(all(advance == mark_expected for advance in marks), "nonspacing mark raw advance profile changed")
        ev["nonspacing_mark_advances"] = {str(advance): marks.count(advance) for advance in set(marks)}
        allowed = {0, cell} if nerd else {0, cell, 2 * cell}
        checks(all(font["hmtx"][g][0] in allowed for g in cm.values()), "unexpected encoded glyph advance")
        if not nerd and plan == "IoskeleyMonoTerm":
            checks(0x27F6 in cm and font["hmtx"][cm[0x27F6]][0] == 2 * cell, "intended long-arrow coverage/width changed")
        if CONTRACT["plans"][plan]["glyph_names"]:
            checks(s["post_format"] == 2.0, "terminal ligature glyph names were lost")
        for cp in [0x2014, 0x2026, 0x2192, 0x2500]:
            checks(cp in cm, f"missing terminal regression character U+{cp:04X}")
            if plan == "IoskeleyMonoTerm" and cp in cm:
                checks(font["hmtx"][cm[cp]][0] == cell, f"Term character U+{cp:04X} no longer single cell")
        if plan == "IoskeleyMonoWeb":
            ranges = CONTRACT["web_ranges"]
            closure = set(CONTRACT.get("web_closure_exceptions", []))
            checks(all(cp in closure or any(lo <= cp <= hi for lo, hi in ranges) for cp in cm), "subset contains undeclared Unicode codepoints")
            checks(not any(cp in cm for cp in CONTRACT["web_excluded_probes"]), "known excluded web range leaked")
            checks(all(cp in cm for cp in range(32, 127)), "web ASCII coverage incomplete")
            checks(json_digest(sorted(cm)) == CONTRACT.get("web_effective_coverage_sha256"), "effective web repertoire changed")
        if nerd:
            probes = {f"U+{cp:04X}": s["samples"].get(f"U+{cp:04X}") for cp in CONTRACT["nerd_probes"]}
            checks(all(probes.values()), "missing Nerd geometry regression probe")
            checks(all(v and v["advance"] == cell for v in probes.values()), "Nerd icon is not single-cell")
        ev["coverage_sha256"] = json_digest(sorted(cm))
        ev["encoded_advances_sha256"] = json_digest([(c, font["hmtx"][g][0]) for c, g in sorted(cm.items())])
    shapes = shaping(data)
    ev["shaping"] = shapes
    if CONTRACT["plans"][plan]["glyph_names"]:
        ev["named_programming_shaping"] = {
            text: {mode: [[glyph_order[row[0]], *row[1:]] for row in rows] for mode, rows in shapes[text].items()}
            for text in CORPUS["ligatures"]
        }
    changed = [t for t in CORPUS["ligatures"] if shapes[t]["False"] != shapes[t]["True"]]
    ev["programming_substitutions"] = changed
    checks(bool(changed) == CONTRACT["plans"][plan]["ligatures"], "programming ligature policy changed")
    for text in CORPUS["ligatures"]:
        for mode in ["False", "True"]:
            checks(sum(g[2] for g in shapes[text][mode]) == len(text) * cell, f"shaping changed total cell width: {text!r} {mode}")
    for text in CORPUS["combining"]:
        for mode in ["False", "True"]:
            checks(sum(g[2] for g in shapes[text][mode]) == cell, f"combining sequence does not shape to one cell: {text!r}")
    for text in CORPUS["zero_width"]:
        for mode in ["False", "True"]:
            checks(sum(g[2] for g in shapes[text][mode]) == 2 * cell, f"format-control sequence changed total cell width: {text!r}")
    return width, s["weight"], italic


def expected_members(spec):
    members = set()
    plan, kind = spec["plan"], spec["kind"]
    if kind == "nerd":
        return None  # Patcher filenames are checked through the complete metadata matrix.
    for width in CONTRACT["widths"]:
        for weight in CONTRACT["weights"]:
            for slope in CONTRACT["slopes"]:
                suffix = ("" if width == "Normal" else width) + ("" if weight == "Regular" else weight) + ("Italic" if slope == "Italic" else "")
                suffix = suffix or "Regular"
                if kind == "web":
                    members.add(f"WOFF2/IoskeleyMono-{suffix}.woff2")
                else:
                    for hint in ["Hinted", "Unhinted"]:
                        members.add(f"{width}/{hint}/{plan}-{suffix}.ttf")
    return members


def validate_run(work, report):
    results = Results()
    found = {p.name for p in work.glob("IoskeleyMono*.zip")}
    results.check(found == set(CONTRACT["packages"]), f"archive set mismatch: {sorted(found)}")
    coverage = {}
    signatures = {}
    ps_names = {}
    for name, spec in CONTRACT["packages"].items():
        path = work / name
        if not path.exists():
            continue
        print("Validating", name, flush=True)
        try:
            with zipfile.ZipFile(path) as archive:
                results.check(archive.testzip() is None, f"{name}: CRC failure")
                infos = archive.infolist()
                results.check(len({i.filename for i in infos}) == len(infos), f"{name}: duplicate ZIP entries")
                files = [i for i in infos if not i.is_dir()]
                fontfiles = [i for i in files if i.filename.endswith((".ttf", ".woff2"))]
                results.check(len(fontfiles) == spec["count"], f"{name}: wrong font count {len(fontfiles)}")
                results.check(all(not Path(i.filename).is_absolute() and ".." not in Path(i.filename).parts for i in files), f"{name}: unsafe archive path")
                expected = expected_members(spec)
                if expected is not None:
                    results.check({i.filename for i in fontfiles} == expected, f"{name}: missing/unexpected font paths")
                notices = [i.filename for i in files if any(t in Path(i.filename).name.lower() for t in ["license", "notice", "ofl"])]
                results.archives[name] = {"sha256": digest(path.read_bytes()), "bytes": path.stat().st_size,
                                          "font_count": len(fontfiles), "members": {i.filename: digest(archive.read(i)) for i in files}, "standalone_notices": notices}
                seen = set()
                package_ps = {}
                for info in fontfiles:
                    key = name + "/" + info.filename
                    try:
                        data = archive.read(info)
                        style = check_font(data, key, spec["plan"], spec["kind"] == "nerd", results)
                        width, weight, italic = style
                        hint = "Unhinted" if "/Unhinted/" in info.filename else "Hinted"
                        slot = (hint, *style) if spec["kind"] == "desktop" else style
                        results.check(slot not in seen, f"{key}: duplicate style slot {slot}")
                        seen.add(slot)
                        if spec["kind"] in {"desktop", "nerd"}:
                            results.check(info.filename.split("/")[0] == width, f"{key}: width directory mismatch")
                        if spec["kind"] == "nerd":
                            results.check(len(info.filename.split("/")) == 2, f"{key}: Nerd package has unexpected directory nesting")
                        ev = results.fonts[key]
                        if shutil.which("fc-scan") and spec["kind"] != "web":
                            with tempfile.TemporaryDirectory(prefix="ioskeley-fontconfig-") as folder:
                                scan_path = Path(folder) / "font.ttf"
                                scan_path.write_bytes(data)
                                spacing = subprocess.check_output(["fc-scan", "--format", "%{spacing}", str(scan_path)], text=True).strip()
                            ev["fontconfig_spacing"] = spacing
                            if spec["kind"] == "nerd":
                                results.check(spacing == "100", f"{key}: FontConfig no longer recognizes Nerd Mono as mono ({spacing!r})")
                        ps = ev["semantic"]["names"]["6"]
                        results.check(ps not in package_ps or package_ps[ps] == style, f"{key}: PostScript collision")
                        package_ps[ps] = style
                        owner = (spec["plan"].replace("IoskeleyMonoWeb", "IoskeleyMono"), spec["kind"] == "nerd", style)
                        results.check(ps not in ps_names or ps_names[ps] == owner, f"{key}: cross-package naming collision")
                        ps_names[ps] = owner
                        coverage[(name, style)] = ev["coverage_sha256"]
                        signatures[(name, style, hint)] = ev
                    except Exception as exc:
                        results.errors.append(f"{key}: {type(exc).__name__}: {exc}")
                results.check(len(seen) == spec["count"], f"{name}: incomplete style matrix")
        except Exception as exc:
            results.errors.append(f"{name}: {type(exc).__name__}: {exc}")
    for style in [(w, v, i) for w in CONTRACT["widths"] for v in CONTRACT["weights"].values() for i in [False, True]]:
        results.check(coverage.get(("IoskeleyMono.zip", style)) == coverage.get(("IoskeleyMono-Web-Full.zip", style)) is not None, f"{style}: full web coverage differs from desktop")
        for base, patched in [("IoskeleyMono.zip", "IoskeleyMono-NerdFont.zip"), ("IoskeleyMono-Term.zip", "IoskeleyMono-Term-NerdFont.zip"), ("IoskeleyMono-NL.zip", "IoskeleyMono-NL-NerdFont.zip")]:
            a = signatures.get((base, style, "Hinted"))
            b = signatures.get((patched, style, "Hinted"))
            if a and b:
                results.check(a["programming_substitutions"] == b["programming_substitutions"], f"{style}: patching changed substitutions for {base}")
                if "named_programming_shaping" in a:
                    results.check(a["named_programming_shaping"] == b.get("named_programming_shaping"), f"{style}: patching changed named programming glyphs/positions for {base}")
    return results.write(report)


def validate_site(report):
    results = Results()
    spec = CONTRACT["packages"][CONTRACT["site_package"]]
    expected = {Path(member).name for member in expected_members(spec)}
    paths = sorted((ROOT / "site/fonts").glob("*.woff2"))
    results.check({p.name for p in paths} == expected, "checked-in web face set changed")
    for path in paths:
        check_font(path.read_bytes(), path.name, spec["plan"], spec["kind"] == "nerd", results)
    return results.write(report)


def compare(a, b, report):
    left, right = json.loads(a.read_text()), json.loads(b.read_text())
    changes = {"font_set_equal": set(left["fonts"]) == set(right["fonts"]), "font_semantic_differences": [], "font_byte_differences": [], "archive_byte_differences": [], "archive_member_differences": []}
    for key in sorted(set(left["fonts"]) & set(right["fonts"])):
        x, y = left["fonts"][key], right["fonts"][key]
        if x["semantic_sha256"] != y["semantic_sha256"] or json_digest(x.get("shaping")) != json_digest(y.get("shaping")):
            changes["font_semantic_differences"].append({"font": key, "tables": [t for t in set(x["semantic"]["table_semantic_sha256"]) | set(y["semantic"]["table_semantic_sha256"]) if x["semantic"]["table_semantic_sha256"].get(t) != y["semantic"]["table_semantic_sha256"].get(t)]})
        if x["sha256"] != y["sha256"]:
            raw_x, raw_y = x.get("raw_table_sha256", {}), y.get("raw_table_sha256", {})
            changes["font_byte_differences"].append({"font": key, "created": [x["created"], y["created"]], "modified": [x["modified"], y["modified"]], "raw_table_differences": sorted(t for t in raw_x.keys() | raw_y.keys() if raw_x.get(t) != raw_y.get(t))})
    changes["archive_set_equal"] = set(left["archives"]) == set(right["archives"])
    changes["validation_runtime_equal"] = left.get("validation_runtime") == right.get("validation_runtime")
    for key in set(left["archives"]) & set(right["archives"]):
        x, y = left["archives"][key], right["archives"][key]
        if x["sha256"] != y["sha256"]: changes["archive_byte_differences"].append(key)
        if set(x["members"]) != set(y["members"]): changes["archive_member_differences"].append(key)
    changes["input_validation_passed"] = all(not x["errors"] and len(x["fonts"]) == FONT_COUNT and len(x["archives"]) == len(CONTRACT["packages"]) for x in [left, right])
    changes["semantic_equal"] = changes["input_validation_passed"] and changes["font_set_equal"] and changes["archive_set_equal"] and not changes["font_semantic_differences"] and not changes["archive_member_differences"]
    report.write_text(json.dumps(changes, indent=2) + "\n")
    print(json.dumps({k: len(v) if isinstance(v, list) else v for k, v in changes.items()}, indent=2))
    return not changes["semantic_equal"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["site", "run", "compare"])
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--left", type=Path)
    parser.add_argument("--right", type=Path)
    args = parser.parse_args()
    check_validation_runtime()
    if args.operation == "site":
        return validate_site(args.report or Path(tempfile.gettempdir()) / "ioskeley-site-validation.json")
    if args.operation == "run":
        if not args.work_dir: parser.error("run requires --work-dir")
        return validate_run(args.work_dir, args.report or args.work_dir / "validation.json")
    if not (args.left and args.right and args.report): parser.error("compare requires --left, --right, --report")
    return compare(args.left, args.right, args.report)


if __name__ == "__main__":
    sys.exit(main())
