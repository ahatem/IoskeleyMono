"""Verify a successful Actions RC and publish its existing ZIP bytes; never build."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def require(condition, message):
    if not condition:
        raise ValueError(message)


def api(repo, endpoint):
    return json.loads(subprocess.check_output(
        ["gh", "api", f"repos/{repo}/{endpoint}"], text=True))


def source_identity(run, artifacts):
    require(run["status"] == "completed" and run["conclusion"] == "success",
            "Source RC run must have completed successfully")
    require(run["event"] == "workflow_dispatch" and
            run["path"] == ".github/workflows/build-font.yml",
            "Source must be the canonical manual RC builder")
    sha = run["head_sha"]
    require(re.fullmatch(r"[0-9a-f]{40}", sha), "Invalid source SHA")
    matches = [a for a in artifacts if a["name"] == f"ioskeley-rc-{sha}"]
    require(len(matches) == 1 and not matches[0]["expired"],
            "Exactly one unexpired successful RC artifact is required")
    artifact = matches[0]
    require(artifact["workflow_run"]["id"] == run["id"] and
            artifact["workflow_run"]["head_sha"] == sha,
            "Artifact does not belong to the source run/SHA")
    return sha, artifact["id"]


def verify_bundle(directory, source_root, sha, tag):
    contract = json.loads((source_root / "tools/release-contract.json").read_text())
    require(tag == "v" + contract["version"]["product"], "Tag differs from source product version")
    report = json.loads((directory / "validation.json").read_text())
    provenance = json.loads((directory / "provenance.json").read_text())
    require(report["verdict"] == "PASS" and report["errors"] == [], "RC validation did not pass")
    require(provenance["repository_head"] == sha, "Provenance SHA differs from source")
    packages = contract["packages"]
    require(len(packages) == 8, "Expected eight release packages")
    require({p.name for p in directory.iterdir()} == set(packages) | {"validation.json", "provenance.json"},
            "Unexpected or missing RC deliverables")
    require(set(report["archives"]) == set(packages), "Report archive inventory differs")
    require(len(report["fonts"]) == sum(s["count"] for s in packages.values()),
            "Report font count differs")
    for name, spec in packages.items():
        path = directory / name
        require(path.is_file() and not path.is_symlink(), "Invalid package file")
        evidence = report["archives"][name]
        require(evidence["font_count"] == spec["count"], f"Wrong count: {name}")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"],
                f"ZIP checksum differs from validated bytes: {name}")
    return sorted(packages)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["inspect", "publish"])
    parser.add_argument("--repo", required=True)
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--tag")
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--notes-root", type=Path, default=Path("."))
    args = parser.parse_args()
    run = api(args.repo, f"actions/runs/{args.run_id}")
    artifacts = api(args.repo, f"actions/runs/{args.run_id}/artifacts?per_page=100")
    sha, artifact_id = source_identity(run, artifacts["artifacts"])
    if args.operation == "inspect":
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write(f"sha={sha}\nartifact_id={artifact_id}\n")
        return
    require(args.directory and args.source_root and args.tag, "Missing promotion arguments")
    require(subprocess.check_output(["git", "-C", str(args.source_root), "rev-parse", "HEAD"],
                                    text=True).strip() == sha, "Checkout differs from RC SHA")
    names = verify_bundle(args.directory, args.source_root, sha, args.tag)
    notes = (args.notes_root / "docs/RELEASE_NOTES.md").read_text()
    notes_path = args.directory.parent / "release-notes.md"
    notes_path.write_text(notes.replace("{{tag}}", args.tag))
    # Create a new ref at the validated SHA. GitHub rejects an existing tag,
    # preventing an existing tag at another commit from being silently reused.
    subprocess.run(["gh", "api", "--method", "POST", f"repos/{args.repo}/git/refs",
                    "-f", f"ref=refs/tags/{args.tag}", "-f", f"sha={sha}"], check=True)
    subprocess.run(["gh", "release", "create", args.tag, "--repo", args.repo,
                    "--verify-tag", "--title", f"Ioskeley Mono {args.tag}",
                    "--notes-file", str(notes_path),
                    *[str(args.directory / name) for name in names]], check=True)


if __name__ == "__main__":
    main()
