"""Canonical local build/package operations. This program has no publish operation."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile
import zlib
from font_evidence import check_validation_runtime

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "tools/toolchain.lock.json").read_text())
CONTRACT = json.loads((ROOT / "tools/release-contract.json").read_text())
STYLE_COUNT = len(CONTRACT["weights"]) * len(CONTRACT["widths"]) * len(CONTRACT["slopes"])


def run(command, cwd=None):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=cwd, check=True)


def output(command):
    return subprocess.check_output(command, stderr=subprocess.STDOUT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_tools():
    import uharfbuzz
    check_validation_runtime()
    versions = {"node": output(["node", "--version"]), "npm": output(["npm", "--version"]),
                "python": platform.python_version(), "ttfautohint": output(["ttfautohint", "--version"]),
                "fontforge": output(["fontforge", "-version"]), "platform": platform.platform(), "harfbuzz": uharfbuzz.version_string(),
                "zlib": {"build": zlib.ZLIB_VERSION, "runtime": zlib.ZLIB_RUNTIME_VERSION},
                "dependencies": {p: importlib.metadata.version(p) for p in ["fonttools", "brotli", "uharfbuzz", "PyYAML"]}}
    if versions["node"] != "v" + LOCK["node"]:
        raise RuntimeError(f"Expected Node {LOCK['node']}, found {versions['node']}")
    if versions["npm"] != LOCK["npm"]:
        raise RuntimeError(f"Expected npm {LOCK['npm']}, found {versions['npm']}")
    if not versions["python"].startswith(LOCK["python_minor"] + "."):
        raise RuntimeError(f"Expected Python {LOCK['python_minor']}.x")
    if versions["ttfautohint"].splitlines()[0] != "ttfautohint " + LOCK["ttfautohint"]:
        raise RuntimeError("Unexpected ttfautohint version")
    if "fontforge " + LOCK["fontforge"] not in versions["fontforge"]:
        raise RuntimeError("Unexpected FontForge version")
    return versions


def source_check(work):
    source = work / "iosevka-src"
    if output(["git", "-C", str(source), "rev-parse", "HEAD"]) != LOCK["iosevka"]["commit"]:
        raise RuntimeError("Iosevka checkout does not match lock")
    changed = output(["git", "-C", str(source), "diff", "HEAD", "--name-only"]).splitlines()
    if set(changed) - {"package-lock.json"}:
        raise RuntimeError(f"Iosevka source was modified: {changed}")
    # The tracked design plan is authoritative; a reused checkout must match it.
    plan_text = (ROOT / "private-build-plans.toml").read_text(encoding="utf-8")
    if (source / "private-build-plans.toml").exists() and (source / "private-build-plans.toml").read_text(encoding="utf-8") != plan_text:
        raise RuntimeError("Build source contains a different design plan")
    return source


def prepare(work):
    work.mkdir(parents=True, exist_ok=True)
    source = work / "iosevka-src"
    if not source.exists():
        run(["git", "clone", "--depth", "1", "--branch", LOCK["iosevka"]["tag"], LOCK["iosevka"]["repository"], source])
    source_check(work)
    patcher = work / "FontPatcher.zip"
    if not patcher.exists():
        urllib.request.urlretrieve(LOCK["nerd_fonts"]["url"], patcher)
    if sha(patcher) != LOCK["nerd_fonts"]["sha256"]:
        raise RuntimeError("Nerd Fonts patcher checksum mismatch")
    with zipfile.ZipFile(patcher) as archive:
        target = (work / "nerd-fonts-patcher").resolve()
        for name in archive.namelist():
            if not (target / name).resolve().is_relative_to(target):
                raise RuntimeError("Unsafe patcher archive member")
        archive.extractall(target)
    versions = check_tools()
    versions.update({"iosevka_commit": LOCK["iosevka"]["commit"], "patcher_sha256": sha(patcher),
                     "build_plan_sha256": sha(ROOT / "private-build-plans.toml"),
                     "build_plan_text_sha256": hashlib.sha256((ROOT / "private-build-plans.toml").read_text(encoding="utf-8").encode()).hexdigest(),
                     "source_date_epoch": os.environ.get("SOURCE_DATE_EPOCH"),
                     "repository_head": output(["git", "-C", str(ROOT), "rev-parse", "HEAD"])})
    if shutil.which("dpkg-query"):
        versions["system_packages"] = output(["dpkg-query", "-W", "ttfautohint", "fontforge", "libfontforge4", "libfreetype6", "fontconfig", "python3"])
    (work / "provenance.json").write_text(json.dumps(versions, indent=2) + "\n")


def compile_fonts(work, jobs):
    check_tools()
    source = source_check(work)
    shutil.copyfile(ROOT / "private-build-plans.toml", source / "private-build-plans.toml")
    # Use Iosevka's upstream entry point and the locked dependency set.
    run(["npm", "install"], source)
    if sha(source / "package-lock.json") != LOCK["installed_npm_lock_sha256"]:
        raise RuntimeError("npm installation lock fingerprint changed; investigate before rebuilding")
    run(["npm", "run", "build", "--", *["contents::" + p for p in CONTRACT["plans"]], f"--jCmd={jobs}"], source)
    provenance = json.loads((work / "provenance.json").read_text())
    provenance["npm_package_lock_sha256"] = sha(source / "package-lock.json")
    (work / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")


def patch_fonts(work):
    from fontTools.ttLib import TTFont
    check_tools()
    source = source_check(work)
    for plan in (p for p in CONTRACT["plans"] if p != "IoskeleyMonoWeb"):
        fonts = sorted((source / "dist" / plan / "TTF").glob("*.ttf"))
        if len(fonts) != STYLE_COUNT:
            raise RuntimeError(f"Expected {STYLE_COUNT} input faces for {plan}, got {len(fonts)}")
        for font in fonts:
            width = "SemiCondensed" if "-SemiCondensed" in font.name else "Normal"
            dest = work / "patched" / plan / width
            dest.mkdir(parents=True, exist_ok=True)
            # Keep production flags and hinted TTF inputs exactly.
            run(["fontforge", "-script", work / "nerd-fonts-patcher/font-patcher", font,
                 *LOCK["nerd_fonts"]["flags"], "--outputdir", dest])
        for path in sorted((work / "patched" / plan).rglob("*.ttf")):
            font = TTFont(path)
            if "post" in font and font["post"].isFixedPitch != 1:
                font["post"].isFixedPitch = 1
                font.save(path)
            font.close()


def package(work):
    source = source_check(work)
    for name, spec in CONTRACT["packages"].items():
        members = []
        plan, kind = spec["plan"], spec["kind"]
        dist = source / "dist" / plan
        if kind == "desktop":
            for folder, hint in [("TTF", "Hinted"), ("TTF-Unhinted", "Unhinted")]:
                for path in sorted((dist / folder).glob("*.ttf")):
                    width = "SemiCondensed" if "-SemiCondensed" in path.name else "Normal"
                    members.append((path, f"{width}/{hint}/{path.name}"))
        elif kind == "nerd":
            for width in CONTRACT["widths"]:
                members.extend((p, f"{width}/{p.name}") for p in sorted((work / "patched" / plan / width).glob("*.ttf")))
        else:
            members.extend((p, "WOFF2/" + p.name.replace("IoskeleyMonoWeb-", "IoskeleyMono-", 1)) for p in sorted((dist / "WOFF2").glob("*.woff2")))
        if len(members) != spec["count"] or len({n for _, n in members}) != spec["count"]:
            raise RuntimeError(f"Wrong or duplicate package members: {name}: {len(members)}")
        target = work / name
        if target.exists():
            raise RuntimeError(f"Refusing to overwrite existing archive: {target}")
        # Preserve current contents/paths. Ordering is explicit; source mtimes remain evidence.
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            for path, member in sorted(members, key=lambda x: x[1]):
                archive.write(path, member)
        print(f"Packaged {name}: {len(members)} font files", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["prepare", "compile", "patch", "package", "validate", "all"])
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    work = args.work_dir.resolve()
    if work == ROOT or ROOT.is_relative_to(work) or args.jobs < 1:
        parser.error("Use a dedicated work directory and positive concurrency")
    if args.operation == "all" and work.exists() and any(work.iterdir()):
        parser.error("all requires an unused work directory; use individual operations to resume")
    for op in (["prepare", "compile", "patch", "package", "validate"] if args.operation == "all" else [args.operation]):
        if op == "prepare": prepare(work)
        elif op == "compile": compile_fonts(work, args.jobs)
        elif op == "patch": patch_fonts(work)
        elif op == "package": package(work)
        else: run([sys.executable, ROOT / "tools/validate_fonts.py", "run", "--work-dir", work])


if __name__ == "__main__":
    main()
