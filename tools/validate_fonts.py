"""Validate the current fonts and packages."""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import sys
import shutil
import subprocess
import tempfile
import platform
import importlib.metadata
import unicodedata
import re
import zipfile
from xml.sax.saxutils import escape

from fontTools.ttLib import TTFont
import uharfbuzz as hb

from font_evidence import (ROOT, digest, inspect_font, json_digest, check_validation_runtime,
                           shorten_legacy_family, LEGACY_FAMILY_NAME_LIMIT)

CONTRACT = json.loads((ROOT / "tools/release-contract.json").read_text())
LOCK = json.loads((ROOT / "tools/toolchain.lock.json").read_text())
FONT_COUNT = sum(spec["count"] for spec in CONTRACT["packages"].values())
CORPUS = json.loads((ROOT / "tests/specimens.json").read_text())


def release_version_parts():
    product = CONTRACT["version"]["product"]
    match = re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", product)
    if not match:
        raise RuntimeError(f"Invalid semantic product version in release contract: {product!r}")
    major, minor, _ = map(int, match.groups())
    return product, major, minor


def check_name_record_consistency(font, checks):
    records = font["name"].names
    for name_id in (1, 2, 3, 4, 5, 6, 16, 17):
        values = {record.toUnicode() for record in records if record.nameID == name_id}
        if values:
            checks(len(values) == 1, f"name ID {name_id} platform/language records disagree")

    version_keys = {
        (record.platformID, record.platEncID, record.langID)
        for record in records if record.nameID == 5
    }
    checks((1, 0, 0) in version_keys, "name ID 5 is missing the Macintosh English record")
    checks((3, 1, 0x0409) in version_keys, "name ID 5 is missing the Windows English record")


def expected_typographic_subfamily(width, weight, italic, nerd):
    labels = {
        100: "Thin", 200: "Extralight", 300: "Light", 350: "SemiLight",
        400: "", 500: "Medium", 600: "Semibold", 700: "Bold",
        800: "Extrabold", 900: "Heavy",
    }
    pieces = []
    if nerd and width != "Normal":
        pieces.append("SemiCondensed")
    if labels[weight]:
        pieces.append(labels[weight])
    if not nerd and width != "Normal":
        pieces.append("Semi-Condensed")
    if italic:
        pieces.append("Italic")
    if not pieces:
        pieces.append("Regular")
    return " ".join(pieces)


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


def check_nerd_geometry(samples, upm, cell, mode, checks):
    checks(mode in CONTRACT["nerd_geometry"], f"unknown Nerd geometry mode {mode!r}")
    if mode not in CONTRACT["nerd_geometry"]:
        return
    probes = {f"U+{cp:04X}": samples.get(f"U+{cp:04X}") for cp in CONTRACT["nerd_probes"]}
    checks(all(probes.values()), "missing Nerd geometry regression probe")
    for label, sample in probes.items():
        if not sample:
            continue
        checks(sample["advance"] == cell, f"Nerd probe {label} must advance one cell")
        checks(not sample["outside_win_metrics"], f"Nerd probe {label} exceeds vertical clipping metrics")
        bounds = sample["bounds"]
        checks(bool(bounds), f"Nerd probe {label} has no ink bounds")
        if not bounds:
            continue
        xmin, _, xmax, _ = bounds
        ink_width = xmax - xmin
        overhang = max(0, -xmin, xmax - sample["advance"])
        if mode == "single":
            limits = CONTRACT["nerd_geometry"]["single"]
            checks(ink_width <= cell * limits["maximum_ink_width_cells"],
                   f"single-width Nerd probe {label} exceeds its cell geometry")
            checks(overhang <= cell * limits["maximum_overhang_cells"],
                   f"single-width Nerd probe {label} overhangs too far")
        elif mode == "normal":
            limits = CONTRACT["nerd_geometry"]["normal"]
            checks(ink_width <= cell * limits["maximum_ink_width_cells"],
                   f"normal Nerd probe {label} exceeds its two-cell geometry")
            checks(overhang <= cell * limits["maximum_overhang_cells"],
                   f"normal Nerd probe {label} overhangs too far")

    if mode == "normal":
        minimums = CONTRACT["nerd_geometry"]["normal"]["minimum_ink_em"]
        for cp, limits in minimums.items():
            label = f"U+{int(cp):04X}"
            sample = samples.get(label)
            if not sample or not sample["bounds"]:
                continue
            xmin, ymin, xmax, ymax = sample["bounds"]
            measured = {"width": (xmax - xmin) / upm, "height": (ymax - ymin) / upm}
            for dimension, minimum in limits.items():
                checks(measured[dimension] >= minimum,
                       f"normal Nerd probe {label} {dimension} is below {minimum:.2f} em")


def check_nerd_advance_profile(advances, cell, strict_mono, checks):
    if strict_mono:
        checks(advances == {cell}, "NFM encoded glyph advances must all be one cell")
    else:
        checks(advances <= {0, cell, 2 * cell}, "unexpected NF encoded glyph advance")


def nerd_variant_from_filename(filename):
    name = Path(filename).name
    if "NerdFontMono-" in name:
        return "NFM"
    if "NerdFont-" in name:
        return "NF"
    return None


def check_font(data, key, plan, nerd, results, nerd_variant=None):
    ev = inspect_font(data)
    s = ev["semantic"]
    results.fonts[key] = ev
    checks = lambda condition, message: results.check(condition, f"{key}: {message}")
    variant_contract = CONTRACT["nerd_variants"].get(nerd_variant) if nerd else None
    if nerd:
        checks(variant_contract is not None, f"unknown Nerd Font variant {nerd_variant!r}")
        if variant_contract is None:
            nerd_variant = "NFM"
            variant_contract = CONTRACT["nerd_variants"][nerd_variant]
    strict_mono = bool(variant_contract and variant_contract["strict_mono"])
    checks(set(CONTRACT["required_tables"]) <= set(s["table_semantic_sha256"]), "missing required tables")
    names = s["names"]
    for i in [1, 2, 3, 4, 5, 6] + ([] if nerd else [16, 17]):
        checks(bool(names[str(i)]), f"missing name ID {i}")
    checks(bool(names["13"] or names["14"]), "missing embedded license evidence")
    checks(" " not in (names["6"] or ""), "PostScript name contains spaces")
    checks((names["6"] or "").isascii() and len(names["6"] or "") <= 63,
           "PostScript name is not ASCII or exceeds 63 characters")
    checks(len(names["1"] or "") <= LEGACY_FAMILY_NAME_LIMIT,
           f"legacy family name exceeds {LEGACY_FAMILY_NAME_LIMIT} characters")
    checks(shorten_legacy_family(names["1"] or "") == names["1"],
           "legacy family name is not in deterministic compatibility form")
    checks(len(names["2"] or "") <= LEGACY_FAMILY_NAME_LIMIT,
           f"legacy subfamily name exceeds {LEGACY_FAMILY_NAME_LIMIT} characters")
    family = plan + variant_contract["family_suffix"] if nerd else CONTRACT["plans"][plan]["family"]
    if names["16"] or not nerd:
        checks(names["16"] == family, f"unexpected typographic family {names['16']!r}; expected {family!r}")
    checks(bool(names["16"]) == bool(names["17"]), "incomplete typographic name pair")
    checks((names["4"] or "").startswith(family), "full name ID 4 does not match package")
    checks(s["weight"] in CONTRACT["weights"].values(), "unexpected weight class")
    if nerd and (s["width"] != 5 or s["weight"] not in {400, 700}):
        checks(bool(names["16"]) and bool(names["17"]), "non-RIBBI Nerd style lost its typographic names")
    widths = [name for name, spec in CONTRACT["widths"].items() if spec["class"] == s["width"]]
    checks(len(widths) == 1, "unexpected width class")
    width = widths[0] if widths else "Normal"
    cell = CONTRACT["widths"][width]["advance"]
    italic = bool(s["fs_selection"] & 1)
    if nerd:
        legacy_family = names["1"] or ""
        plan_prefixes = {
            "IoskeleyMono": ("IoskeleyMono", "Ioskeley"),
            "IoskeleyMonoTerm": ("IoskeleyMonoTerm", "IoskeleyTerm"),
            "IoskeleyMonoNL": ("IoskeleyMonoNL", "IoskeleyNL"),
        }
        prefixes = plan_prefixes.get(plan, ())
        if plan == "IoskeleyMono":
            matches_plan = any(legacy_family.startswith(prefix) for prefix in prefixes) and not legacy_family.startswith(
                ("IoskeleyMonoTerm", "IoskeleyMonoNL", "IoskeleyTerm", "IoskeleyNL")
            )
        else:
            matches_plan = any(legacy_family.startswith(prefix) for prefix in prefixes)
        checks(matches_plan, "legacy family name lost its Standard/Term/NL identity")
        if nerd_variant == "NFM":
            checks(" Nerd Font Mono" in legacy_family or re.search(r"(?:^|\s)NFM(?:\s|$)", legacy_family) is not None,
                   "legacy family name lost its NFM identity")
        else:
            checks(re.search(r"(?:^|\s)Nerd Font(?:\s|$)", legacy_family) is not None
                   or re.search(r"(?:^|\s)NF(?:\s|$)", legacy_family) is not None,
                   "legacy family name lost its NF identity")
        if width == "SemiCondensed":
            checks("SemiCondensed" in legacy_family or re.search(r"(?:^|\s)SC(?:\s|$)", legacy_family) is not None,
                   "legacy family name lost its SemiCondensed identity")
    else:
        checks((names["1"] or "").startswith(family), "legacy family ID 1 does not match package")

    checks(italic == bool(s["mac_style"] & 2) == (s["italic_angle"] != 0), "inconsistent italic flags")
    checks(italic == ("Italic" in (names["17"] or names["2"] or "")), "italic naming linkage mismatch")
    expected_legacy_subfamily = (
        ("Bold" if s["weight"] == 700 else "Regular") if not italic else
        ("Bold Italic" if s["weight"] == 700 else "Italic")
    )
    checks(names["2"] == expected_legacy_subfamily, "legacy subfamily weight/style name mismatch")
    if names["17"]:
        expected_subfamily = expected_typographic_subfamily(width, s["weight"], italic, nerd)
        checks(names["17"] == expected_subfamily,
               f"unexpected typographic subfamily {names['17']!r}; expected {expected_subfamily!r}")
    else:
        checks(nerd and width == "Normal" and s["weight"] in {400, 700},
               "typographic subfamily is missing outside the legacy RIBBI group")
        expected_subfamily = expected_typographic_subfamily(width, s["weight"], italic, nerd)
    expected_full_name = family if expected_subfamily == "Regular" else f"{family} {expected_subfamily}"
    checks(names["4"] == expected_full_name,
           f"unexpected full name {names['4']!r}; expected {expected_full_name!r}")
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
    product, version_major, version_minor = release_version_parts()
    upstream = LOCK["iosevka"]["tag"].removeprefix("v")
    version_parts = (names["5"] or "").split("; ")
    checks(len(version_parts) >= 3 and version_parts[0] == f"Version {version_major}.{version_minor}",
           "name ID 5 must begin with the standards-compatible Ioskeley major.minor version")
    checks(len(version_parts) >= 3 and version_parts[1] == f"Ioskeley Mono {product}",
           "name ID 5 does not identify the Ioskeley product version")
    checks(len(version_parts) >= 3 and version_parts[2] == f"Iosevka {upstream}",
           "name ID 5 does not retain locked Iosevka provenance")
    expected_suffix = []
    if "Unhinted" not in key.replace("\\", "/"):
        expected_suffix.append(f"ttfautohint (v{LOCK['ttfautohint']})")
    if nerd:
        expected_suffix.append(f"Nerd Fonts {LOCK['nerd_fonts']['version']}")
    checks(version_parts[3:] == expected_suffix,
           "name ID 5 provenance does not match the hinted/Nerd product pipeline")
    with TTFont(io.BytesIO(data), recalcTimestamp=False) as font:
        check_name_record_consistency(font, checks)
        expected_revision = float(f"{version_major}.{version_minor}")
        actual_revision_bits = int(round(font["head"].fontRevision * 65536))
        expected_revision_bits = int(round(expected_revision * 65536))
        checks(actual_revision_bits == expected_revision_bits,
               f"head.fontRevision is not the Ioskeley {version_major}.{version_minor} numeric revision")
        cm = font.getBestCmap()
        glyph_order = font.getGlyphOrder()
        # ASCII text must occupy one cell. Combining marks and intended wide symbols
        # are checked separately; Term may preserve valid two-cell Unicode glyphs.
        checks(all(c in cm and font["hmtx"][cm[c]][0] == cell for c in range(32, 127)), "ordinary ASCII cell advances changed")
        mark_expected = cell if strict_mono else 0
        checks(0x301 in cm and font["hmtx"][cm[0x301]][0] == mark_expected, "combining acute raw advance changed")
        checks(0x200B in cm and font["hmtx"][cm[0x200B]][0] == mark_expected, "zero-width-space raw advance profile changed")
        marks = [font["hmtx"][g][0] for c, g in cm.items() if unicodedata.category(chr(c)) in {"Mn", "Me"}]
        checks(all(advance == mark_expected for advance in marks), "nonspacing mark raw advance profile changed")
        ev["nonspacing_mark_advances"] = {str(advance): marks.count(advance) for advance in set(marks)}
        advances = {font["hmtx"][g][0] for g in cm.values()}
        # NF keeps valid source zero- and two-cell advances; NFM remains strict.
        if nerd:
            check_nerd_advance_profile(advances, cell, strict_mono, checks)
        else:
            checks(advances <= {0, cell, 2 * cell}, "unexpected encoded glyph advance")
        if plan == "IoskeleyMonoTerm":
            arrow_width = cell if strict_mono else 2 * cell
            checks(0x27F6 in cm and font["hmtx"][cm[0x27F6]][0] == arrow_width,
                   "Term long-arrow width changed for its NF/NFM contract")
            if nerd_variant == "NF":
                arrow = s["samples"].get("U+27F6")
                checks(bool(arrow and arrow["bounds"] and arrow["bounds"][0] >= 0
                            and arrow["bounds"][2] <= 2 * cell),
                       "Term NF long arrow no longer fits its two-cell advance")
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
            check_nerd_geometry(s["samples"], s["upm"], cell, variant_contract["geometry"], checks)
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
        return None  # Upstream patcher naming is validated by the variant/style matrix.
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


def check_nfm_fontconfig(fonts, archive_name, expected_nfm_count, results):
    if not shutil.which("fc-list") or not shutil.which("fc-cache"):
        message = f"{archive_name}: fc-list/fc-cache unavailable; NFM :mono listing was not checked"
        if sys.platform.startswith("linux"):
            results.check(False, message)
        else:
            results.warn(message)
        return

    try:
        with tempfile.TemporaryDirectory(prefix="ioskeley-nfm-fontconfig-") as folder:
            root = Path(folder)
            font_dir, cache_dir = root / "fonts", root / "cache"
            font_dir.mkdir()
            cache_dir.mkdir()
            expected = set()
            nf_probe = None
            for variant, filename, data in fonts:
                include_nf_probe = (variant == "NF" and "/Normal/" in "/" + filename
                                    and Path(filename).name.endswith("NerdFont-Regular.ttf"))
                if variant != "NFM" and not include_nf_probe:
                    continue
                target = font_dir / Path(filename).name
                results.check(not target.exists(), f"{archive_name}: duplicate Fontconfig test filename {target.name}")
                target.write_bytes(data)
                if variant == "NFM":
                    expected.add(str(target.resolve()))
                else:
                    nf_probe = str(target.resolve())
            config = root / "fonts.conf"
            config.write_text(
                '<?xml version="1.0"?>\n'
                '<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">\n'
                '<fontconfig>\n'
                f'  <dir>{escape(str(font_dir))}</dir>\n'
                f'  <cachedir>{escape(str(cache_dir))}</cachedir>\n'
                '</fontconfig>\n'
            )
            env = {**os.environ, "FONTCONFIG_FILE": str(config), "FONTCONFIG_PATH": str(root)}
            subprocess.run(["fc-cache", "-f"], env=env, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            listed = subprocess.check_output(
                ["fc-list", ":mono", "--format", "%{file}\\n"], env=env,
                stderr=subprocess.STDOUT, text=True
            )
            mono_files = {str(Path(line).resolve()) for line in listed.splitlines() if line}
            missing = sorted(expected - mono_files)
            results.check(nf_probe is not None, f"{archive_name}: NF coexistence probe is missing")
            results.check(len(expected) == expected_nfm_count,
                          f"{archive_name}: expected {expected_nfm_count} NFM files for Fontconfig")
            results.check(not missing,
                          f"{archive_name}: NFM files missing from fc-list :mono ({len(missing)})")
            results.archives[archive_name]["fontconfig_mono"] = {
                "expected_nfm_files": len(expected),
                "nfm_files_listed": len(expected & mono_files),
                "nf_geometry_requires_mono": False,
                "nf_probe_file": nf_probe,
                "nf_probe_in_mono_list": nf_probe in mono_files if nf_probe else None,
            }
    except Exception as exc:
        results.check(False, f"{archive_name}: Fontconfig NFM check failed: {type(exc).__name__}: {exc}")


def validate_run(work, report, package_names=None):
    results = Results()
    selected_names = tuple(package_names or CONTRACT["packages"])
    selected = set(selected_names)
    found = {p.name for p in work.glob("IoskeleyMono*.zip")}
    results.check(found == selected, f"archive set mismatch: expected {sorted(selected)}, found {sorted(found)}")
    coverage = {}
    signatures = {}
    ps_names = {}
    unique_id_owners = {}
    legacy_family_owners = {}
    for name in selected_names:
        spec = CONTRACT["packages"][name]
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
                nerd_font_data = []
                for info in fontfiles:
                    key = name + "/" + info.filename
                    try:
                        data = archive.read(info)
                        variant = nerd_variant_from_filename(info.filename) if spec["kind"] == "nerd" else None
                        if spec["kind"] == "nerd":
                            results.check(variant in spec["variants"], f"{key}: unknown or missing NF/NFM filename marker")
                            nerd_font_data.append((variant, info.filename, data))
                        style = check_font(data, key, spec["plan"], spec["kind"] == "nerd", results,
                                           variant)
                        width, weight, italic = style
                        hint = "Unhinted" if "/Unhinted/" in info.filename else "Hinted"
                        slot = ((hint, *style) if spec["kind"] == "desktop"
                                else (variant, *style) if spec["kind"] == "nerd" else style)
                        results.check(slot not in seen, f"{key}: duplicate style slot {slot}")
                        seen.add(slot)
                        if spec["kind"] in {"desktop", "nerd"}:
                            results.check(info.filename.split("/")[0] == width, f"{key}: width directory mismatch")
                        if spec["kind"] == "nerd":
                            results.check(len(info.filename.split("/")) == 2, f"{key}: Nerd package has unexpected directory nesting")
                        ev = results.fonts[key]
                        names = ev["semantic"]["names"]
                        base_plan = spec["plan"].replace("IoskeleyMonoWeb", "IoskeleyMono")
                        unique_owner = (base_plan, variant, style)
                        unique_id = names["3"]
                        results.check(unique_id not in unique_id_owners or unique_id_owners[unique_id] == unique_owner,
                                      f"{key}: name ID 3 collides with a different font face")
                        unique_id_owners[unique_id] = unique_owner
                        legacy_weight_group = "RIBBI" if weight in {400, 700} else weight
                        legacy_owner = (base_plan, variant, width, legacy_weight_group)
                        legacy_name = names["1"]
                        results.check(legacy_name not in legacy_family_owners
                                      or legacy_family_owners[legacy_name] == legacy_owner,
                                      f"{key}: legacy family name collides across product families or widths")
                        legacy_family_owners[legacy_name] = legacy_owner
                        if shutil.which("fc-scan") and spec["kind"] != "web":
                            with tempfile.TemporaryDirectory(prefix="ioskeley-fontconfig-") as folder:
                                scan_path = Path(folder) / "font.ttf"
                                scan_path.write_bytes(data)
                                spacing = subprocess.check_output(["fc-scan", "--format", "%{spacing}", str(scan_path)], text=True).strip()
                            ev["fontconfig_spacing"] = spacing
                            if (spec["kind"] == "nerd"
                                    and CONTRACT["nerd_variants"][variant]["strict_mono"]):
                                results.check(spacing == "100", f"{key}: NFM must have Fontconfig spacing 100, found {spacing!r}")
                        ps = ev["semantic"]["names"]["6"]
                        results.check(ps not in package_ps or package_ps[ps] == style, f"{key}: PostScript collision")
                        package_ps[ps] = style
                        owner = (base_plan, variant, style)
                        results.check(ps not in ps_names or ps_names[ps] == owner, f"{key}: cross-package naming collision")
                        ps_names[ps] = owner
                        coverage[(name, variant, style)] = ev["coverage_sha256"]
                        signatures[(name, variant, style, hint)] = ev
                    except Exception as exc:
                        results.errors.append(f"{key}: {type(exc).__name__}: {exc}")
                results.check(len(seen) == spec["count"], f"{name}: incomplete style matrix")
                if spec["kind"] == "nerd":
                    variant_count = len(spec["variants"])
                    results.check(variant_count > 0 and spec["count"] % variant_count == 0,
                                  f"{name}: Nerd face count must divide evenly across variants")
                    expected_nfm_count = spec["count"] // variant_count if variant_count else 0
                    check_nfm_fontconfig(nerd_font_data, name, expected_nfm_count, results)
        except Exception as exc:
            results.errors.append(f"{name}: {type(exc).__name__}: {exc}")
    styles = [(w, v, i) for w in CONTRACT["widths"] for v in CONTRACT["weights"].values() for i in [False, True]]
    if {"IoskeleyMono.zip", "IoskeleyMono-Web-Full.zip"} <= selected:
        for style in styles:
            results.check(coverage.get(("IoskeleyMono.zip", None, style)) == coverage.get(("IoskeleyMono-Web-Full.zip", None, style)) is not None, f"{style}: full web coverage differs from desktop")
    pairs = [("IoskeleyMono.zip", "IoskeleyMono-NerdFont.zip"), ("IoskeleyMono-Term.zip", "IoskeleyMono-Term-NerdFont.zip"), ("IoskeleyMono-NL.zip", "IoskeleyMono-NL-NerdFont.zip")]
    for base, patched in pairs:
        if base not in selected or patched not in selected:
            continue
        for style in styles:
            a = signatures.get((base, None, style, "Hinted"))
            for variant in CONTRACT["nerd_variants"]:
                b = signatures.get((patched, variant, style, "Hinted"))
                if a and b:
                    results.check(a["programming_substitutions"] == b["programming_substitutions"], f"{style}/{variant}: patching changed substitutions for {base}")
                    if "named_programming_shaping" in a:
                        results.check(a["named_programming_shaping"] == b.get("named_programming_shaping"), f"{style}/{variant}: patching changed named programming glyphs/positions for {base}")
    return results.write(report)


def validate_site(report):
    results = Results()
    spec = CONTRACT["packages"][CONTRACT["site_package"]]
    expected = {Path(member).name for member in expected_members(spec)}
    paths = sorted((ROOT / "site/fonts").glob("*.woff2"))
    results.check({p.name for p in paths} == expected, "checked-in web face set changed")
    ps_owners = {}
    unique_id_owners = {}
    legacy_family_owners = {}
    for path in paths:
        style = check_font(path.read_bytes(), path.name, spec["plan"], spec["kind"] == "nerd", results)
        width, _, _ = style
        ev = results.fonts[path.name]["semantic"]["names"]
        owner = ("IoskeleyMono", None, style)
        results.check(ev["6"] not in ps_owners or ps_owners[ev["6"]] == owner,
                      f"{path.name}: PostScript name collision")
        ps_owners[ev["6"]] = owner
        results.check(ev["3"] not in unique_id_owners or unique_id_owners[ev["3"]] == owner,
                      f"{path.name}: name ID 3 collision")
        unique_id_owners[ev["3"]] = owner
        legacy_weight_group = "RIBBI" if style[1] in {400, 700} else style[1]
        family_owner = ("IoskeleyMono", None, width, legacy_weight_group)
        results.check(ev["1"] not in legacy_family_owners or legacy_family_owners[ev["1"]] == family_owner,
                      f"{path.name}: legacy family name collision")
        legacy_family_owners[ev["1"]] = family_owner
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
