# Ioskeley Product Decision Ledger

Status: proposed defaults for the Ioskeley 3 work. Confirm the historical rationale against issue discussions and build artifacts during the baseline review; these entries are not completed study results. See the [finalization plan](README.md) for release gates.

| Area | Verdict | Why / reopen condition |
|---|---|---|
| Normal | KEEP | Primary readability anchor; recalibrate only with strong evidence |
| SemiCondensed | KEEP; recalibration allowed | Useful density mode |
| Old Condensed | DO NOT RESTORE AS-IS | Previously looked too narrow/crushed |
| New Condensed | ONE BOUNDED DESIGN SPIKE | Must prove a distinct, attractive use case |
| 10 static weights | KEEP; optical audit | Mature family/API; avoid churn without evidence |
| Upright + Italic | KEEP; recalibrate italic | Core family structure |
| Standard ligatures | KEEP | Established behavior |
| NL | KEEP | Needed where apps cannot reliably disable ligatures |
| Term | KEEP | Real terminal-cell/shaping history justifies it |
| Nerd Font | KEEP | Repeated user demand; current icon sizing is a quality issue |
| Web subset | KEEP | Oversized webfonts already solved through subsetting |
| Web Full | KEEP | Full-coverage escape hatch |
| Variable font | REOPEN ONCE AS SPIKE | Direct varLib attempt failed; quantify whether incompatibility is local or systemic |
| Reduced VF subset | EXPERIMENT | Only if exclusions are small, explicit and maintainable |
| Slashed zero | KEEP AS OPENTYPE FEATURE | No extra family required |
| More public widths | DEFAULT NO | Must earn a distinct use case |
| Quasi-proportional | OUT OF SCOPE | Different product question; not a VF substitute |
| Berkeley fidelity | REFERENCE | Never override correctness/readability/identity |
| Iosevka pin | KEEP | Reproducible releases |
| Rename | NO | Compatibility/distribution cost |

## Durable lessons
The issue history is part of the architecture. Record the evidence behind each decision so future maintainers can build on it.

A closed decision means: **bring new evidence before reopening it.**
