# Build, validation, and release

`private-build-plans.toml` is the authoritative font design and build
configuration. `tools/build.py` is the canonical local build and packaging
implementation used by both maintainers and GitHub Actions. It invokes
Iosevka's upstream `npm install` and `npm run build` operations; it does not
generate fonts itself. Nerd Font patches use the locked patcher with
`--complete --careful --mono`, hinted TTF inputs, and the documented
`post.isFixedPitch` repair.

`tools/release-contract.json` records current product and packaging
expectations: package membership, style matrix, metrics, version policy, and
web repertoire limits. `tools/validate_fonts.py` is the validation mechanism.
`tools/font_evidence.py` contains small shared font-inspection helpers.

## Prerequisites

Use Linux, including WSL, for the complete pipeline. Install Git, curl, Python
3.14 with venv support, Node 20.20.0, ttfautohint 1.8.4, and FontForge
20230101. The orchestrator checks these versions and the Python dependency pins
in `tools/requirements.txt`. Exact source, patcher, Node, npm, and validation
tool versions live in `tools/toolchain.lock.json`.

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
`patch` creates the Nerd Font variants. `package` creates the eight archives
and refuses to overwrite existing files. `validate` runs the current-product
archive checks. `all` runs the five operations in order.

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
  1/2/4/5/6/16/17 are checked. Family, weight, width, italic/bold linkage, and
  PostScript uniqueness are checked across the installation matrix.
- Fixed-pitch metadata, PANOSE proportion, design metrics, ordinary ASCII cell
  advances, nonspacing-mark advances, and encoded advance limits are checked.
- Nerd samples must remain single-cell. When `fc-scan` is installed, Nerd Mono
  must also report FontConfig spacing 100. Plain Term is not forced through a
  strict `:mono` filter.
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

- Name ID 5 and the font revision still identify upstream Iosevka. Validation
  emits one non-blocking warning for this condition.
- Nerd icon geometry remains issue #29; `--mono` remains the supported build.
- The existing patcher gives nonspacing marks and the sampled zero-width space
  a cell advance in `hmtx`. HarfBuzz combining and format-control behavior is
  checked separately.
- Archives do not add standalone license/notice files; embedded notices are
  checked.
- Plain Term keeps intended wide characters, so it is not expected to satisfy a
  strict FontConfig `:mono` query. Nerd Mono has its own single-cell contract.

## Testing the validators

```bash
$PYTHON -m unittest discover -s tests -v
```

The tests use the checked-in web fonts and controlled in-memory mutations. They
cover fixed pitch, ASCII advances, subset leakage, glyph names, NL ligature
policy, package filename edge cases, bold linkage, empty comparison reports,
corrupt archives, the absence of a publishing CLI operation, intentional
current-design changes. Tests do not alter font assets.

## Packages

The contract enumerates eight archive names. Standard, Term, and NL each contain
80 TTFs under `Normal|SemiCondensed/Hinted|Unhinted`. Their Nerd derivatives
contain 40 patched TTFs under the two width directories. Each Web archive
contains 40 WOFF2 files under `WOFF2` with identical public filenames. Web-Full
comes from the base plan, not a separate generator plan.

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

GitHub Actions calls the same `all` operation. Manual dispatch runs checks and
builds without uploading an artifact or creating a draft release. A separate
publishing job requires a pushed version tag and a successful build/validation
job. Only that tag path transfers archives and invokes release creation.

Keep generated fonts, archives, build directories, logs, and temporary
experiments out of Git.
