"""Cheap release-boundary checks; no font builds or optional font dependencies."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from promote_rc import source_identity, verify_bundle
import promote_rc


class ReleasePipeline(unittest.TestCase):
    def test_nerd_and_upstream_weight_names(self):
        module = ast.parse((ROOT / "tools/validate_fonts.py").read_text())
        function = next(n for n in module.body if isinstance(n, ast.FunctionDef)
                        and n.name == "expected_typographic_subfamily")
        namespace = {}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "naming", "exec"), namespace)
        naming = namespace[function.name]
        for weight, plain, nerd in [(200, "Extralight", "ExtraLight"),
                                    (600, "Semibold", "SemiBold"),
                                    (800, "Extrabold", "ExtraBold")]:
            for italic in [False, True]:
                suffix = " Italic" if italic else ""
                self.assertEqual(plain + suffix, naming("Normal", weight, italic, False))
                self.assertEqual(nerd + suffix, naming("Normal", weight, italic, True))
                self.assertEqual("SemiCondensed " + nerd + suffix,
                                 naming("SemiCondensed", weight, italic, True))
                self.assertEqual(plain + " Semi-Condensed" + suffix,
                                 naming("SemiCondensed", weight, italic, False))

    def test_rc_workflow_guards(self):
        module = ast.parse((ROOT / "tests/test_validation.py").read_text())
        cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == "RegressionGuards")
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                      and n.name == "test_manual_workflow_preserves_rc_artifacts_without_publishing")
        namespace = {"ROOT": ROOT, "yaml": yaml}
        exec(compile(ast.Module(body=[method], type_ignores=[]), "workflow_guard", "exec"), namespace)
        namespace[method.name](self)

    def test_source_run_and_artifact_are_bound(self):
        sha = "a" * 40
        run = {"status": "completed", "conclusion": "success", "event": "workflow_dispatch",
               "path": ".github/workflows/build-font.yml", "head_sha": sha, "id": 123}
        artifact = {"name": f"ioskeley-rc-{sha}", "expired": False, "id": 456,
                    "workflow_run": {"id": 123, "head_sha": sha}}
        self.assertEqual((sha, 456), source_identity(run, [artifact]))
        for field, value in [("conclusion", "failure"), ("status", "in_progress"),
                             ("event", "push"), ("path", ".github/workflows/other.yml")]:
            changed = dict(run, **{field: value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                source_identity(changed, [artifact])
        for edit in [lambda a: a.update(expired=True),
                     lambda a: a.update(name=f"ioskeley-failed-{sha}"),
                     lambda a: a["workflow_run"].update(head_sha="b" * 40),
                     lambda a: a["workflow_run"].update(id=999)]:
            changed = copy.deepcopy(artifact)
            edit(changed)
            with self.assertRaises(ValueError):
                source_identity(run, [changed])

    def test_only_complete_validated_identical_zip_bytes_can_be_promoted(self):
        contract = json.loads((ROOT / "tools/release-contract.json").read_text())
        sha = "a" * 40
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            report = {"verdict": "PASS", "errors": [], "fonts": {}, "archives": {}}
            for name, spec in contract["packages"].items():
                data = name.encode()
                (directory / name).write_bytes(data)
                report["archives"][name] = {"font_count": spec["count"],
                                             "sha256": hashlib.sha256(data).hexdigest()}
                report["fonts"].update({f"{name}/{i}": {} for i in range(spec["count"])})
            (directory / "provenance.json").write_text(json.dumps({"repository_head": sha}))
            def save():
                (directory / "validation.json").write_text(json.dumps(report))
            save()
            tag = "v" + contract["version"]["product"]
            self.assertEqual(sorted(contract["packages"]), verify_bundle(directory, ROOT, sha, tag))
            for field, value in [("verdict", "FAIL"), ("errors", ["bad font"]), ("fonts", {})]:
                original = report[field]
                report[field] = value
                save()
                with self.subTest(field=field), self.assertRaises(ValueError):
                    verify_bundle(directory, ROOT, sha, tag)
                report[field] = original
            save()
            with self.assertRaises(ValueError):
                verify_bundle(directory, ROOT, sha, "v0.0.0")
            with self.assertRaises(ValueError):
                verify_bundle(directory, ROOT, "b" * 40, tag)
            (directory / next(iter(contract["packages"]))).write_bytes(b"changed ZIP")
            with self.assertRaises(ValueError):
                verify_bundle(directory, ROOT, sha, tag)

    def test_publishing_creates_tag_at_rc_sha_and_attaches_only_verified_files(self):
        sha = "a" * 40
        run = {"status": "completed", "conclusion": "success", "event": "workflow_dispatch",
               "path": ".github/workflows/build-font.yml", "head_sha": sha, "id": 123}
        artifact = {"name": f"ioskeley-rc-{sha}", "expired": False, "id": 456,
                    "workflow_run": {"id": 123, "head_sha": sha}}
        names = sorted(json.loads((ROOT / "tools/release-contract.json").read_text())["packages"])
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "rc"
            args = ["promote_rc.py", "publish", "--repo", "owner/repo", "--run-id", "123",
                    "--tag", "v2.2.0", "--directory", str(directory), "--source-root", str(ROOT)]
            with patch.object(sys, "argv", args), patch.object(promote_rc, "api", side_effect=[run, {"artifacts": [artifact]}]), \
                    patch.object(promote_rc.subprocess, "check_output", return_value=sha), \
                    patch.object(promote_rc, "verify_bundle", return_value=names) as verify, \
                    patch.object(promote_rc.subprocess, "run") as commands:
                promote_rc.main()
                verify.assert_called_once_with(directory, ROOT, sha, "v2.2.0")
                self.assertEqual(2, commands.call_count)
                tag_command = commands.call_args_list[0].args[0]
                self.assertIn(f"sha={sha}", tag_command)
                self.assertIn("ref=refs/tags/v2.2.0", tag_command)
                release_command = commands.call_args_list[1].args[0]
                self.assertIn("--verify-tag", release_command)
                self.assertEqual([str(directory / n) for n in names], release_command[-8:])
            run["conclusion"] = "failure"
            with patch.object(sys, "argv", args), patch.object(promote_rc, "api", side_effect=[run, {"artifacts": [artifact]}]), \
                    patch.object(promote_rc.subprocess, "run") as commands:
                with self.assertRaises(ValueError):
                    promote_rc.main()
                commands.assert_not_called()

    def test_publish_workflow_never_builds_and_uses_source_identity(self):
        text = (ROOT / ".github/workflows/publish-rc.yml").read_text()
        workflow = yaml.load(text, Loader=yaml.BaseLoader)
        self.assertEqual({"workflow_dispatch"}, set(workflow["on"]))
        self.assertEqual({"publish"}, set(workflow["jobs"]))
        self.assertNotIn("build.py", text)
        self.assertNotIn("npm", text)
        steps = workflow["jobs"]["publish"]["steps"]
        self.assertEqual("${{ steps.source.outputs.sha }}", steps[2]["with"]["ref"])
        self.assertEqual("${{ steps.source.outputs.artifact_id }}", steps[3]["with"]["artifact-ids"])
        self.assertEqual("${{ inputs.run_id }}", steps[3]["with"]["run-id"])
        self.assertIn("promote_rc.py publish", steps[-1]["run"])


if __name__ == "__main__":
    unittest.main()
