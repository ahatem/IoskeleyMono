# Ioskeley 3 finalization plan

Status: proposed. This plan defines the work and release criteria for Ioskeley 3; it does not announce a completed release. Font binaries, build settings, package names and the published website are unchanged by this proposal.

Ioskeley began as an Iosevka experiment inspired by Berkeley Mono. The next release should retain that technical character while making readability, terminal correctness and a coherent family the basis for design decisions.

**Distinctive when inspected. Quiet when used.**

## Current baseline

The checked-in build plan defines Normal at shape 600, SemiCondensed at 540, x-height 520, cap height 690 and leading 1250. These are configuration values; compiled metrics still need measurement. An x-height near 530 is an experiment to evaluate, not an approved change.

The release workflow pins Iosevka to v34.4.0 and builds Standard, Term, NL and Web plans, with Nerd Font derivatives and separate Web and Web-Full archives. Other dependencies still need a reproducibility audit: for example, the Nerd Fonts patcher currently comes from its latest release.

The maintainer's response in [issue #21](https://github.com/ahatem/IoskeleyMono/issues/21) records a varLib `ShouldBeConstant` failure in generated GSUB backtrack coverage across the ten static weights. The issue was closed as not planned, with Web subsetting as the workaround. This proposal allows one bounded investigation of that failure; it does not establish that a variable build is feasible. The original artifacts still need reproduction. Earlier width decisions described in the supplied notes also need source-history references during the baseline review.

## Work sequence

| Stage | Work | Required result |
| --- | --- | --- |
| 1. Establish evidence | Review issue history; build the current family; capture metrics and specimens | Baseline tied to source revision, tool versions and artifact hashes |
| 2. Calibrate the family | Audit heights, rhythm, darkness, punctuation, operators and italics | Recorded comparisons and approved design values |
| 3. Settle width and variable-font questions | Run the bounded studies below | Written verdict for each, including a reason if rejected |
| 4. Validate distributions | Add regression checks and audit build inputs | Repeatable builds and explicit package contracts |
| 5. Update presentation | Revise README, website, package chooser and specimens; produce the identity film | Accurate public copy and usable download paths |
| 6. Release | Review all gates and document remaining limitations | Release notes, validated archives and a maintenance handoff |

Typography work and the variable-font study may proceed independently after the baseline is captured. Website copy can be prepared early; final specimens and family claims depend on the design verdicts.

## Design and research

- [Design direction](DESIGN_DIRECTION.md): priorities, calibration and attribution.
- [Decision ledger](DECISION_LEDGER.md): defaults to preserve and evidence needed to reopen them.
- [Width study](WIDTH_STUDY.md): compare 600 / 576 / 560 / 548 / 540 / 525 / 510, plus the historical Condensed value after recovering it from source history. Keep experimental builds outside public packages.
- [Variable-font study](VARIABLE_FONT_STUDY.md): reproduce the reported failure, classify incompatibilities and test weight interpolation before width interpolation.

Static fonts remain the full-capability release family. A variable build is optional and must have a documented coverage and feature contract. A third width ships only if specimens show a useful distinction from SemiCondensed across weights and italics. Neither experiment is a release promise.

## Distribution validation

Preserve Standard, Term, NL, Nerd Font, Web and Web-Full unless new evidence justifies a change. Each package must have a documented use case and checks appropriate to its contract:

- Family, style and PostScript names; weight/width metadata; fixed-pitch flags.
- Term cell geometry, exported glyph names needed by terminal shaping, Powerline and box-drawing continuity.
- Standard ligature shaping and NL's no-ligature behavior.
- Nerd Font family names, icon advance widths, alignment and clipping.
- Coverage and shaping in the Web subset; full-coverage expectations for Web-Full; measured file-size budgets.
- Archive names, directory layout, face counts, CSS references and expected files.
- Clipping, overlap and representative metric snapshots across weights, widths and slopes.

Choose the actual shaping strings, supported environments, numerical tolerances and size budgets from baseline measurements. Record expected results before turning them into regression checks. Pin the generator, patcher and validation tools, and document how to reproduce the release.

## Presentation

- [README proposal](README_PROPOSAL.md): positioning and package guidance. Retain working installation, feature, build and license documentation when applying it.
- [Website direction](WEBSITE.md) and [content wireframe](SITE_WIREFRAME.md): understand the family, inspect specimens, try it and choose a package.
- [Identity film](FILM.md): a 55–70 second concept using the actual fonts in controlled technical scenes.

Credit Iosevka and its contributors as the construction foundation, and Berkeley Mono as design inspiration. Technical scenes must not imply real aircraft deployment or certification.

## Release checklist

These boxes describe future work. They are intentionally unchecked.

- [ ] Baseline artifacts, tool versions, hashes and source references recorded.
- [ ] Typography measurements and visual comparisons reviewed; final values recorded.
- [ ] Width study completed with an explicit verdict.
- [ ] Variable-font study completed with a reproducible build or an evidence-backed rejection.
- [ ] Package validation implemented; known regressions fixed or documented with acceptance reasons.
- [ ] Reproducible build and release instructions verified.
- [ ] README, site, metadata and specimens reflect the approved family.
- [ ] Download chooser, archives, CSS and installation guidance checked together.
- [ ] Identity film completed and checked against the released fonts.
- [ ] Release notes and decision ledger record limitations and conditions for reopening decisions.

After release, focus on compatibility fixes, upstream updates and demonstrated quality defects. Reopen settled design or package decisions when new evidence warrants it.
