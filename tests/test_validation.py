"""Exercise guards using real existing fonts and deliberately damaged inputs."""
import io
from contextlib import redirect_stdout
import json
from pathlib import Path
import sys
import tempfile
import unittest
import yaml
import zipfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import build as build_tool
import validate_fonts as validation_tool
from fontTools.ttLib import TTFont
from font_evidence import ROOT
from validate_fonts import (Results, check_font, check_nerd_geometry, compare, expects_bold,
                            check_nerd_advance_profile, expected_members, nerd_variant_from_filename,
                            CONTRACT, validate_run)


class RegressionGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = (ROOT / "site/fonts/IoskeleyMono-Regular.woff2").read_bytes()

    def changed(self, edit, data=None):
        font = TTFont(io.BytesIO(data or self.data))
        edit(font)
        stream = io.BytesIO()
        font.save(stream)
        font.close()
        return stream.getvalue()

    def validate(self, data, plan="IoskeleyMonoWeb"):
        results = Results()
        check_font(data, "test", plan, False, results)
        return results

    def test_current_web_behavior_is_accepted(self):
        result = self.validate(self.data)
        self.assertEqual([], result.errors)
        self.assertIn("name ID 5 retains upstream Iosevka version 34.4.0", result.warnings)

    def test_fixed_pitch_flag_regression_is_rejected(self):
        result = self.validate(self.changed(lambda f: setattr(f["post"], "isFixedPitch", 0)))
        self.assertTrue(any("isFixedPitch" in e for e in result.errors))

    def test_nonmonospace_ascii_is_rejected(self):
        def edit(font):
            glyph = font.getBestCmap()[ord("A")]
            _, lsb = font["hmtx"][glyph]
            font["hmtx"][glyph] = (601, lsb)
        result = self.validate(self.changed(edit))
        self.assertTrue(any("ASCII cell advances" in e for e in result.errors))

    def test_subset_leak_is_rejected(self):
        def edit(font):
            glyph = font.getBestCmap()[ord("A")]
            for table in font["cmap"].tables:
                if table.isUnicode(): table.cmap[0x410] = glyph
        result = self.validate(self.changed(edit))
        self.assertTrue(any("excluded web range" in e for e in result.errors))

    def test_bold_linkage_covers_bold_extrabold_and_black(self):
        for name in ["IoskeleyMono-Regular.woff2", "IoskeleyMono-Bold.woff2",
                     "IoskeleyMono-ExtraBold.woff2", "IoskeleyMono-Black.woff2"]:
            result = self.validate((ROOT / "site/fonts" / name).read_bytes())
            self.assertEqual([], result.errors, name)

    def test_extrabold_without_bold_linkage_is_rejected(self):
        data = (ROOT / "site/fonts/IoskeleyMono-ExtraBold.woff2").read_bytes()

        def edit(font):
            font["OS/2"].fsSelection &= ~32
            font["head"].macStyle &= ~1

        result = self.validate(self.changed(edit, data))
        self.assertTrue(any("bold linkage mismatch" in error for error in result.errors))

    def test_regular_must_not_be_bold_linked(self):
        def edit(font):
            font["OS/2"].fsSelection &= ~64
            font["OS/2"].fsSelection |= 32
            font["head"].macStyle |= 1

        result = self.validate(self.changed(edit))
        self.assertTrue(any("bold linkage mismatch" in error for error in result.errors))

    def test_nerd_patcher_bold_policy_stays_explicit(self):
        self.assertTrue(expects_bold(700, nerd=True))
        self.assertFalse(expects_bold(800, nerd=True))
        self.assertFalse(expects_bold(900, nerd=True))
        self.assertTrue(all(expects_bold(weight, nerd=False) for weight in (700, 800, 900)))

    def test_nerd_archives_contain_distinct_nf_and_nfm_siblings(self):
        expected_modes = {"NF": [], "NFM": ["--mono"]}
        self.assertEqual(set(expected_modes), set(build_tool.LOCK["nerd_fonts"]["flags_by_variant"]))
        self.assertEqual(["--complete", "--careful"], build_tool.LOCK["nerd_fonts"]["flags"])
        nerd_styles = len(CONTRACT["weights"]) * len(CONTRACT["widths"]) * len(CONTRACT["slopes"])
        self.assertEqual(40, nerd_styles)
        self.assertEqual(560, sum(spec["count"] for spec in CONTRACT["packages"].values()))
        for archive in ("IoskeleyMono-NerdFont.zip", "IoskeleyMono-Term-NerdFont.zip",
                        "IoskeleyMono-NL-NerdFont.zip"):
            spec = CONTRACT["packages"][archive]
            self.assertEqual(["NF", "NFM"], spec["variants"])
            self.assertEqual(2 * nerd_styles, spec["count"])
            self.assertIsNone(expected_members(spec))
        self.assertEqual(" Nerd Font", CONTRACT["nerd_variants"]["NF"]["family_suffix"])
        self.assertEqual(" Nerd Font Mono", CONTRACT["nerd_variants"]["NFM"]["family_suffix"])
        self.assertEqual("normal", CONTRACT["nerd_variants"]["NF"]["geometry"])
        self.assertFalse(CONTRACT["nerd_variants"]["NF"]["strict_mono"])
        self.assertTrue(CONTRACT["nerd_variants"]["NFM"]["strict_mono"])
        for variant, extra in expected_modes.items():
            self.assertEqual([*build_tool.LOCK["nerd_fonts"]["flags"], *extra],
                             build_tool.nerd_flags_for_variant(variant))
        self.assertNotIn("--single-width-glyphs", build_tool.nerd_flags_for_variant("NF"))
        self.assertNotIn("--cell", build_tool.nerd_flags_for_variant("NF"))
        with self.assertRaises(ValueError):
            build_tool.nerd_flags_for_variant("Propo")

    def test_nerd_package_member_generation_covers_both_40_face_matrices(self):
        with tempfile.TemporaryDirectory() as folder:
            work = Path(folder)
            for archive_name in ("IoskeleyMono-NerdFont.zip", "IoskeleyMono-Term-NerdFont.zip",
                                 "IoskeleyMono-NL-NerdFont.zip"):
                spec = CONTRACT["packages"][archive_name]
                plan = spec["plan"]
                for width in CONTRACT["widths"]:
                    for weight in CONTRACT["weights"]:
                        for slope in CONTRACT["slopes"]:
                            suffix = ("" if width == "Normal" else width)
                            suffix += "" if weight == "Regular" else weight
                            suffix += "Italic" if slope == "Italic" else ""
                            suffix = suffix or "Regular"
                            for variant in spec["variants"]:
                                mono = "Mono" if variant == "NFM" else ""
                                filename = f"{plan}NerdFont{mono}-{suffix}.ttf"
                                path = work / "patched" / plan / width / filename
                                path.parent.mkdir(parents=True, exist_ok=True)
                                path.touch()
                members = build_tool.package_members(work, spec)
                paths = [archive_path for _, archive_path in members]
                self.assertEqual(80, len(paths), archive_name)
                self.assertEqual(80, len(set(paths)), archive_name)
                self.assertEqual(40, sum("NerdFont-" in path for path in paths))
                self.assertEqual(40, sum("NerdFontMono-" in path for path in paths))
        self.assertEqual("NF", nerd_variant_from_filename("IoskeleyMonoNerdFont-Regular.ttf"))
        self.assertEqual("NFM", nerd_variant_from_filename("IoskeleyMonoNerdFontMono-Regular.ttf"))
        self.assertIsNone(nerd_variant_from_filename("IoskeleyMono-Regular.ttf"))

    def test_nf_preserves_multi_cell_source_advances_but_nfm_does_not(self):
        errors = []
        check_nerd_advance_profile({0, 600, 1200}, 600, False, lambda ok, message: errors.append(message) if not ok else None)
        self.assertEqual([], errors)
        check_nerd_advance_profile({600}, 600, True, lambda ok, message: errors.append(message) if not ok else None)
        self.assertEqual([], errors)
        check_nerd_advance_profile({0, 600, 1200}, 600, True, lambda ok, message: errors.append(message) if not ok else None)
        self.assertTrue(any("NFM encoded glyph advances" in error for error in errors))

    def test_desktop_fontconfig_scan_does_not_require_nerd_variant(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            archive_path = folder / "IoskeleyMono.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("Normal/Hinted/Regular.woff2", self.data)

            def record_font(data, key, plan, nerd, results, nerd_variant=None):
                results.fonts[key] = {
                    "semantic": {"names": {"6": "IoskeleyMono-Regular"}},
                    "coverage_sha256": "test-coverage",
                    "programming_substitutions": [],
                }
                return "Normal", 400, False

            contract = {
                "packages": {"IoskeleyMono.zip": {"plan": "IoskeleyMono", "kind": "desktop", "count": 1}},
                "widths": {},
                "weights": {},
                "nerd_variants": {},
            }
            with patch.object(validation_tool, "CONTRACT", contract), \
                    patch.object(validation_tool, "expected_members", return_value=None), \
                    patch.object(validation_tool, "check_font", side_effect=record_font), \
                    patch.object(validation_tool.shutil, "which", return_value=True), \
                    patch.object(validation_tool.subprocess, "check_output", return_value="100"), \
                    redirect_stdout(io.StringIO()):
                failed = validation_tool.validate_run(folder, folder / "report.json", ("IoskeleyMono.zip",))
            self.assertFalse(failed)

    def test_normal_nerd_geometry_rejects_regressed_icon_sizes(self):
        def glyph(bounds):
            return {"advance": 600, "bounds": bounds, "outside_win_metrics": False}

        samples = {
            "U+E0B0": glyph([-8, -285, 600, 965]),
            "U+E0B2": glyph([0, -285, 608, 965]),
            "U+F0C12": glyph([0, 40, 600, 640]),
            "U+E711": glyph([-1, -30, 600, 710]),
            "U+F113": glyph([0, 100, 600, 580]),
            "U+276C": glyph([115, 17, 485, 663]),
        }
        result = Results()
        check_nerd_geometry(samples, 1000, 600, "normal", lambda condition, message: result.check(condition, message))
        self.assertTrue(any("U+F0C12" in error for error in result.errors))
        self.assertTrue(any("U+E711" in error for error in result.errors))
        self.assertTrue(any("U+F113" in error for error in result.errors))

    def test_normal_nerd_geometry_allows_upstream_overhang(self):
        def glyph(bounds):
            return {"advance": 600, "bounds": bounds, "outside_win_metrics": False}

        samples = {
            "U+E0B0": glyph([-8, -285, 600, 965]),
            "U+E0B2": glyph([0, -285, 608, 965]),
            "U+F0C12": glyph([0, -35, 750, 715]),
            "U+E711": glyph([0, -50, 632, 729]),
            "U+F113": glyph([0, -6, 865, 686]),
            "U+276C": glyph([115, 17, 485, 663]),
        }
        result = Results()
        check_nerd_geometry(samples, 1000, 600, "normal", lambda condition, message: result.check(condition, message))
        self.assertEqual([], result.errors)

    def test_single_width_geometry_rejects_excessive_overhang(self):
        def glyph(bounds):
            return {"advance": 600, "bounds": bounds, "outside_win_metrics": False}

        samples = {
            "U+E0B0": glyph([-8, -285, 600, 965]),
            "U+E0B2": glyph([0, -285, 608, 965]),
            "U+F0C12": glyph([0, 40, 600, 640]),
            "U+E711": glyph([-1, -30, 600, 710]),
            "U+F113": glyph([0, 100, 865, 580]),
            "U+276C": glyph([115, 17, 485, 663]),
        }
        samples["U+E0B0"]["outside_win_metrics"] = True
        result = Results()
        check_nerd_geometry(samples, 1000, 600, "single", lambda condition, message: result.check(condition, message))
        self.assertTrue(any("U+F113" in error and "overhang" in error for error in result.errors))
        self.assertTrue(any("U+E0B0" in error and "clipping" in error for error in result.errors))

    def test_exported_names_are_required_for_terminal_ligatures(self):
        result = self.validate(self.data, "IoskeleyMono")
        self.assertTrue(any("glyph names were lost" in e for e in result.errors))

    def test_ligatured_font_cannot_pass_as_nl(self):
        result = self.validate(self.data, "IoskeleyMonoNL")
        self.assertTrue(any("ligature policy" in e for e in result.errors))

    def test_real_package_filename_edge_cases(self):
        members = expected_members(CONTRACT["packages"]["IoskeleyMono-Web.zip"])
        self.assertIn("WOFF2/IoskeleyMono-SemiCondensed.woff2", members)
        self.assertIn("WOFF2/IoskeleyMono-Italic.woff2", members)
        self.assertNotIn("WOFF2/IoskeleyMono-RegularItalic.woff2", members)
        self.assertEqual(40, len(members))

    def test_empty_reports_do_not_prove_reproducibility(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source = folder / "empty.json"
            source.write_text(json.dumps({"errors": [], "fonts": {}, "archives": {}}))
            with redirect_stdout(io.StringIO()):
                self.assertTrue(compare(source, source, folder / "comparison.json"))

    def test_corrupt_archive_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            target = folder / "IoskeleyMono.zip"
            with zipfile.ZipFile(target, "w", zipfile.ZIP_STORED) as archive:
                archive.writestr("Normal/Hinted/example.ttf", b"control payload")
            data = bytearray(target.read_bytes())
            location = data.index(b"control payload")
            data[location] ^= 1
            target.write_bytes(data)
            report = folder / "validation.json"
            with redirect_stdout(io.StringIO()):
                self.assertTrue(validate_run(folder, report))
            self.assertTrue(any("CRC" in error for error in json.loads(report.read_text())["errors"]))

    def test_current_build_accepts_intentional_design_change(self):
        changed = (ROOT / "private-build-plans.toml").read_text(encoding="utf-8").replace("xHeight = 520", "xHeight = 525", 1)
        self.assertNotEqual((ROOT / "private-build-plans.toml").read_text(encoding="utf-8"), changed)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "private-build-plans.toml").write_text(changed, encoding="utf-8")
            source = root / "work/iosevka-src"
            source.mkdir(parents=True)
            (source / "private-build-plans.toml").write_text(changed, encoding="utf-8")
            with patch.object(build_tool, "ROOT", root), patch.object(
                build_tool, "output", side_effect=[build_tool.LOCK["iosevka"]["commit"], ""]
            ):
                build_tool.source_check(root / "work")

    def test_build_has_no_publish_operation(self):
        import subprocess
        result = subprocess.run([sys.executable, str(ROOT / "tools/build.py"), "publish", "--work-dir", "unused"], capture_output=True)
        self.assertNotEqual(0, result.returncode)
        self.assertIn(b"invalid choice", result.stderr)

    def test_clean_build_refuses_a_reused_directory(self):
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            marker = Path(folder) / "existing-evidence.txt"
            marker.write_text("preserve")
            result = subprocess.run([sys.executable, str(ROOT / "tools/build.py"), "all", "--work-dir", folder], capture_output=True)
            self.assertNotEqual(0, result.returncode)
            self.assertIn(b"unused work directory", result.stderr)
            self.assertEqual("preserve", marker.read_text())

    def test_manual_workflow_cannot_publish_or_upload(self):
        workflow = yaml.load((ROOT / ".github/workflows/build-font.yml").read_text(), Loader=yaml.BaseLoader)
        self.assertIn("workflow_dispatch", workflow["on"])
        gate = "github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')"
        self.assertEqual(gate, workflow["jobs"]["publish"]["if"])
        self.assertEqual("read", workflow["permissions"]["contents"])
        for step in workflow["jobs"]["build"]["steps"]:
            action = step.get("uses", "")
            if "upload" in action:
                self.assertEqual(gate, step.get("if"))
            self.assertNotIn("action-gh-release", action)


if __name__ == "__main__":
    unittest.main()
