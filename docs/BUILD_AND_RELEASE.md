# Build, validation, and release

`private-build-plans.toml` is the authoritative font design and build
configuration. `tools/build.py` is the canonical local build and packaging
implementation used by both maintainers and GitHub Actions. It invokes
Iosevka's upstream `npm install` and `npm run build` operations; it does not
generate fonts itself. Each Nerd archive contains two variants patched from
the same hinted TTF inputs: NF uses `--complete --careful`; NFM adds `--mono`.
Both receive the `post.isFixedPitch` repair. NF has larger icons and may
overhang a cell; NFM preserves strict one-cell advances and Fontconfig `:mono`
recognition.

`tools/release-contract.json` records current product and packaging
expectations: package membership, style matrix, metrics, version policy, and
web repertoire limits. `tools/validate_fonts.py` is the validation mechanism.
`tools/font_evidence.py` contains small shared font-inspection helpers.

The release contract's single `version.product` value is authoritative. Final
font metadata is stamped after upstream generation and, for Nerd outputs, after
FontForge patching. Name ID 5 begins with the product's numeric major/minor and
then carries the full Ioskeley semver and locked upstream provenance. The
`head.fontRevision` is the Fixed 16.16 numeric major/minor; the semver patch is
not encoded in that numeric field. Overlong Nerd legacy family ID 1 values use
short compatibility aliases; modern family/subfamily IDs 16/17 retain the full
names. FontForge can report the intermediate overlength during patching; the
post-patch finalizer fixes ID 1 before the font is packaged.

## Prerequisites

Use Linux, including WSL, for the complete pipeline. Install Git, curl, Python
3.14 with venv support, Node 20.20.0, ttfautohint 1.8.4, FontForge 20230101,
and Fontconfig. The orchestrator checks these versions and the Python dependency
pins in `tools/requirements.txt`. Exact source, patcher, Node, npm, and
validation tool versions live in `tools/toolchain.lock.json`.

CI uses `ubuntu-24.04` because the system tool versions are checked exactly.
Native Windows validation is possible with compatible Python/Brotli wheels; the
production build tools are Linux tools.

From the repository root:

```bash
python3.14 -m venv /var/tmp/ioskeley-venv
/var/tmp/ioskeley-venv/bin/python -m pip install -r tools/requirements.txt
PYTHON=/var/tmp/ioskeley-venv/bin/python

$PYTHON tools/validate_fonts.py site
$PYTHON -m unittest discover -s tests -v
$PYTHON tools/build.py all --work-dir /var/tmp/ioskeley-build --jobs 2
```

Node must be on `PATH` at the locked version. Use a new work directory for a
clean repeat; `all` refuses a nonempty directory.

## Build operations

```bash
$PYTHON tools/build.py prepare  --work-dir /var/tmp/ioskeley-build
$PYTHON tools/build.py compile  --work-dir /var/tmp/ioskeley-build --jobs 2
$PYTHON tools/build.py patch    --work-dir /var/tmp/ioskeley-build
$PYTHON tools/build.py package  --work-dir /var/tmp/ioskeley-build
$PYTHON tools/build.py validate --work-dir /var/tmp/ioskeley-build
```

`prepare` clones the locked Iosevka tag, downloads the patcher, verifies the
commit and SHA-256, checks the host tools, and writes `provenance.json`.
`compile` installs upstream npm dependencies and builds all four plans.
`patch` creates the Nerd Font variants, repairs `post.isFixedPitch`, and applies
the final product metadata after FontForge's name/version changes. `package`
re-applies the same idempotent metadata finalizer to every archive member before
writing the eight archives, and refuses to overwrite existing files. `validate`
runs the current-product archive checks. `all` runs the five operations in
order.

An interrupted build can be resumed with the individual operations. Do not
reuse stale `dist`, patch, or package output when checking reproducibility.

## Validation

```bash
# Current checked-in web assets against the current contract.
$PYTHON tools/validate_fonts.py site

# All eight archives from one build directory.
$PYTHON tools/validate_fonts.py run --work-dir /var/tmp/ioskeley-build

# Explicit comparison of two validation reports.
$PYTHON tools/validate_fonts.py compare \
  --left /var/tmp/ioskeley-build-a/validation.json \
  --right /var/tmp/ioskeley-build-b/validation.json \
  --report /var/tmp/ioskeley-comparison.json
```

Each operation writes a JSON report and a short stdout summary. The verdict is
`PASS` or `FAIL`; a failed guard returns a nonzero exit code. Warnings are
non-blocking and are listed in the report. Reports are written to the build
directory unless `--report` is supplied; `site` defaults to a temporary file.

### Automated guards

- Archives open and pass CRC checks. Missing archives, duplicate entries,
  missing or extra font paths, wrong counts, unsafe paths, and incomplete or
  duplicated style slots fail validation.
- Fonts parse; required tables, embedded license notice, and names
  1/2/3/4/5/6/16/17 are checked. ID 5 must identify the product version and
  locked provenance consistently in Macintosh and Windows records; `head`
  revision, legacy family length/grouping collisions, weight, width,
  italic/bold linkage, and PostScript/name-ID-3 uniqueness are checked across
  the installation matrix.
- Fixed-pitch metadata, PANOSE proportion, design metrics, ASCII advances,
  nonspacing-mark advances, and encoded advance limits are checked.
- NFM must use the Nerd Font Mono names, have one-cell encoded advances, report
  Fontconfig spacing 100, and appear in an isolated `fc-list :mono` query. NF
  uses ordinary Nerd Font names, keeps source zero-/two-cell advances, and does
  not promise `:mono`. Its issue probes enforce larger injected-icon sizes,
  bounded overhang, and vertical metrics; Term NF preserves its two-cell arrow.
- Standard and Term must shape programming ligatures. NL must not. Combining
  and format-control sequences are shaped separately and checked for cell
  width. Standard and Term retain `post` format 2 glyph names for terminal
  ligature support.
- Nerd patching must preserve the programming substitution pattern and named
  glyph positions of its base package.
- The Web subset must stay inside its declared ranges and measured closure
  exceptions, must not contain known excluded probes, must include ASCII, and
  must match the current effective repertoire. Web-Full coverage must match the
  base desktop repertoire.
- `compare` refuses incomplete or empty reports. It reports semantic table
  differences, shaping differences, font bytes, archive bytes, and archive
  member differences without modifying either input.

### Current product notes

- Name ID 5 starts `Version 2.2; Ioskeley Mono 2.2.0; Iosevka 34.4.0` and
  retains `ttfautohint (v1.8.4)` on hinted outputs plus `Nerd Fonts 3.5.0` on
  NF/NFM outputs. Unhinted desktop fonts omit only the autohint token.
- `head.fontRevision` stores numeric 2.2 (Fixed 16.16; reported as 2.200).
  Iosevka 34.4.0 is retained as provenance, not used as the product revision.
- Long NF/NFM legacy family ID 1 names are shortened only as needed to the
  FontForge 31-character compatibility limit. IDs 16/17 keep the full NF/NFM
  typographic family names; ID 4 and PostScript names remain face-specific.
- Both NF and NFM are shipped for Standard, Term, and NL. NF uses ordinary
  Nerd Font geometry; NFM keeps the existing `--mono` behavior, including its
  strict advances and one-cell Term long-arrow advance.
- NF preserves source combining/format-control advances; NFM uses `--mono`'s
  strict cell advances. HarfBuzz combining and format-control behavior is
  checked separately.
- Archives do not add standalone license/notice files; embedded notices are
  checked.
- Plain Term and Term NF keep intended wide characters, so Fontconfig may not
  satisfy a strict `:mono` query. Term NFM is the strict-mono terminal variant.

## Testing the validators

```bash
$PYTHON -m unittest discover -s tests -v
```

The tests use the checked-in web fonts and controlled in-memory mutations. They
cover fixed pitch, ASCII advances, subset leakage, glyph names, NL ligature
policy, NF/NFM flags, product version/revision and platform-name records, legacy
family aliases, package-time metadata stamping, naming and geometry, strict NFM
Fontconfig membership, package filename edge cases, bold linkage, empty
comparison reports, corrupt archives, the absence of a publishing CLI operation,
and intentional current-design changes. Tests do not alter font assets.

## Packages

The contract enumerates eight archive names. Standard, Term, and NL each contain
80 TTFs under `Normal|SemiCondensed/Hinted|Unhinted`. Each Nerd archive contains
80 patched TTFs (40 NF and 40 NFM) under the two width directories; their
distinct family prefixes preserve unique filenames. Each Web archive contains
40 WOFF2 files under `WOFF2` with identical public filenames. Web-Full comes
from the base plan, not a separate generator plan.

Packaging preserves font contents and paths. ZIP entries are sorted and
directory entries are omitted, so container bytes need not match another ZIP
implementation. Font timestamps may also differ between runs.

## Reproducibility

Build twice into separate new work directories and compare the two
`validation.json` reports with the explicit `compare` operation. Font semantic
fingerprints normalize only `head.created`, `head.modified`, and
`head.checkSumAdjustment`; outlines, layout, hint programs, naming, and all other
table contents remain compared. Archive directory records, order, and container
metadata are not font semantics.

Exact inputs are the Iosevka commit, patcher archive/hash/flags, Node/npm and
Python tool versions, installed npm lock fingerprint, and the tracked build-plan
text. OS/library revisions, compression implementation, architecture, and
timestamps are environmental inputs. Investigate lockfile differences rather
than silently accepting them.

## Publishing boundary

`tools/build.py` has no tag, release, upload, push, or GitHub API write
operation. Local commands produce local files only. Dependency downloads do not
upload fonts.

`build-font.yml` is the manual-only RC builder. It runs the same `all`
operation, then uploads `ioskeley-rc-<source SHA>` with the eight ZIPs,
`validation.json`, and `provenance.json`. Failed runs preserve whatever exists
under `ioskeley-failed-<source SHA>` instead. Both expire after seven days.
Branch and tag pushes do not trigger a font build.

After inspecting a successful RC, manually dispatch `publish-rc.yml` with
`run_id` set to that successful builder run and `tag` set to `v2.2.0` (or the
source contract's product version). Promotion checks the source run, artifact
identity, PASS verdict, empty errors, provenance SHA, exact package inventory,
font counts and each ZIP's SHA-256 against the report. It checks out the source
SHA's release contract and notes, creates a new tag at that exact SHA, and
publishes those downloaded ZIP bytes without compiling or patching again.
Existing tags are refused. Only this separate workflow has release write access.
The source artifact must still be available; failed runs cannot be promoted.
Human-facing release notes live in `docs/RELEASE_NOTES.md`.

Keep generated fonts, archives, build directories, logs, and temporary
experiments out of Git.
