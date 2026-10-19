"""Canonical local build/package operations. This program has no publish operation."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile
import zlib
from font_evidence import check_validation_runtime, shorten_legacy_family

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


def nerd_flags_for_variant(variant):
    spec = LOCK["nerd_fonts"]
    variants = spec.get("flags_by_variant", {})
    if variant not in variants:
        raise ValueError(f"Unknown Nerd Font variant: {variant}")
    return [*spec["flags"], *variants[variant]]


def product_version_parts():
    value = CONTRACT["version"]["product"]
    match = re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", value)
    if not match:
        raise RuntimeError(f"Invalid semantic product version in release contract: {value!r}")
    major, minor, patch = map(int, match.groups())
    if major >= 32768 or minor >= 65535 or patch >= 65535:
        raise RuntimeError(f"Product version cannot be represented in OpenType metadata: {value}")
    return value, major, minor, patch


def product_font_revision():
    """Use the semantic major/minor as a Fixed 16.16 decimal; patch stays textual."""
    _, major, minor, _ = product_version_parts()
    revision = float(f"{major}.{minor}")
    if revision >= 32768:
        raise RuntimeError("Product version exceeds the signed Fixed 16.16 fontRevision range")
    return revision


def set_name_records(name_table, name_id, value):
    keys = {(r.platformID, r.platEncID, r.langID) for r in name_table.names if r.nameID == name_id}
    if not keys:
        keys = {(1, 0, 0), (3, 1, 0x0409)}
    for platform_id, encoding_id, language_id in sorted(keys):
        name_table.setName(value, name_id, platform_id, encoding_id, language_id)


def finalize_font_metadata(path, *, nerd=False, repair_fixed_pitch=False):
    """Apply Ioskeley's release version after upstream, hinting, or patcher edits."""
    from fontTools.ttLib import TTFont

    product, major, minor, _ = product_version_parts()
    upstream = LOCK["iosevka"]["tag"].removeprefix("v")
    autohint_token = f"ttfautohint (v{LOCK['ttfautohint']})"
    nerd_token = f"Nerd Fonts {LOCK['nerd_fonts']['version']}"
    expected_upstream = f"Iosevka {upstream}"
    expected_nerd = nerd_token if nerd else None

    with TTFont(path, recalcTimestamp=False) as font:
        name_table = font["name"]
        source_versions = [r.toUnicode() for r in name_table.names if r.nameID == 5]
        source_text = "; ".join(source_versions)
        if expected_upstream not in source_text and upstream not in source_text:
            raise RuntimeError(f"{path}: source name ID 5 does not retain locked Iosevka {upstream}")

        has_autohint = "ttfautohint" in source_text.lower()
        autohint_tokens = set(re.findall(r"ttfautohint\s*\([^;)]*\)", source_text))
        if has_autohint and autohint_tokens != {autohint_token}:
            raise RuntimeError(f"{path}: unexpected ttfautohint provenance in name ID 5")
        nerd_tokens = set(re.findall(r"Nerd Fonts [0-9]+(?:\.[0-9]+)*", source_text))
        if nerd:
            if nerd_tokens != {nerd_token}:
                raise RuntimeError(f"{path}: Nerd Fonts provenance does not match the toolchain lock")
        elif nerd_tokens:
            raise RuntimeError(f"{path}: Nerd Fonts font was passed as an unpatched product font")

        parts = [
            f"Version {major}.{minor}",
            f"Ioskeley Mono {product}",
            expected_upstream,
        ]
        if has_autohint:
            parts.append(autohint_token)
        if expected_nerd:
            parts.append(expected_nerd)
        final_version = "; ".join(parts)

        set_name_records(name_table, 5, final_version)
        for record in list(name_table.names):
            if record.nameID != 1:
                continue
            legacy_name = shorten_legacy_family(record.toUnicode())
            if legacy_name != record.toUnicode():
                name_table.setName(legacy_name, 1, record.platformID, record.platEncID, record.langID)

        font["head"].fontRevision = product_font_revision()
        if repair_fixed_pitch and "post" in font:
            font["post"].isFixedPitch = 1

        output = io.BytesIO()
        font.save(output, reorderTables=False)
    path.write_bytes(output.getvalue())


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


def patch_fonts(work, face_names_by_plan=None):
    check_tools()
    source = source_check(work)
    for plan in (p for p in CONTRACT["plans"] if p != "IoskeleyMonoWeb"):
        fonts = sorted((source / "dist" / plan / "TTF").glob("*.ttf"))
        if face_names_by_plan is None:
            expected_count = STYLE_COUNT
        else:
            requested = set(face_names_by_plan.get(plan, ()))
            available = {font.name for font in fonts}
            missing = requested - available
            if missing:
                raise RuntimeError(f"Missing selected {plan} input faces: {sorted(missing)}")
            fonts = [font for font in fonts if font.name in requested]
            expected_count = len(requested)
        if len(fonts) != expected_count:
            raise RuntimeError(f"Expected {expected_count} input faces for {plan}, got {len(fonts)}")
        for font in fonts:
            width = "SemiCondensed" if "-SemiCondensed" in font.name else "Normal"
            dest = work / "patched" / plan / width
            dest.mkdir(parents=True, exist_ok=True)
            # Ship both upstream geometry contracts from the same hinted input.
            for variant in CONTRACT["nerd_variants"]:
                run(["fontforge", "-script", work / "nerd-fonts-patcher/font-patcher", font,
                     *nerd_flags_for_variant(variant), "--outputdir", dest])
        for path in sorted((work / "patched" / plan).rglob("*.ttf")):
            finalize_font_metadata(path, nerd=True, repair_fixed_pitch=True)


def package_members(work, spec):
    members = []
    plan, kind = spec["plan"], spec["kind"]
    dist = work / "iosevka-src" / "dist" / plan
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
    return members


def package(work, package_names=None):
    source_check(work)
    selected = tuple(package_names or CONTRACT["packages"])
    unknown = set(selected) - set(CONTRACT["packages"])
    if unknown:
        raise ValueError(f"Unknown packages: {sorted(unknown)}")
    for name in selected:
        spec = CONTRACT["packages"][name]
        members = package_members(work, spec)
        if len(members) != spec["count"] or len({n for _, n in members}) != spec["count"]:
            raise RuntimeError(f"Wrong or duplicate package members: {name}: {len(members)}")
        target = work / name
        if target.exists():
            raise RuntimeError(f"Refusing to overwrite existing archive: {target}")
        for path in sorted({path for path, _ in members}):
            finalize_font_metadata(path, nerd=spec["kind"] == "nerd",
                                   repair_fixed_pitch=spec["kind"] == "nerd")
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
