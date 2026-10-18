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
from fontTools.ttLib import TTFont
from font_evidence import ROOT
from validate_fonts import Results, check_font, compare, expects_bold, expected_members, CONTRACT, validate_run


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
