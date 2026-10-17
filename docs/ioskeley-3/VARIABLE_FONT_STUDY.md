# Variable Font Feasibility Spike

Status: planned. The maintainer's response in [issue #21](https://github.com/ahatem/IoskeleyMono/issues/21) records a GSUB `ShouldBeConstant` failure across ten static weights, involving different helper glyphs in backtrack coverage. The issue was closed as not planned. Reproduce the failure before drawing conclusions about whether a reduced build can avoid it.

## Question
Can Ioskeley produce a maintainable variable font by normalizing or intentionally reducing incompatible generated content, without becoming a permanent Iosevka fork?

## 1. Reproduce
Pin Iosevka and fontTools. Reproduce the previous GSUB `ShouldBeConstant` failure. Record hashes, glyph counts, tables and first failure.

Start from the release workflow's Iosevka v34.4.0 baseline. Record the exact input plans, commands, tool versions and logs with the result. If the reported failure cannot be reproduced, document that difference before testing alternatives.

## 2. Inventory
Start with Thin / Regular / Black:
- glyph-set symmetric differences;
- glyph order;
- cmap;
- GSUB/GPOS/GDEF structure;
- fontTools interpolatability output;
- contour/component compatibility.

Do not delete the first offending glyph and call it solved.

## 3. Taxonomy
Classify incompatibilities as:
1. order-only;
2. helper/ligature glyph;
3. optional OpenType feature;
4. optional Unicode coverage;
5. normalizable generation difference;
6. outline incompatibility;
7. systemic Iosevka behavior.

## 4. Smallest credible VF
Try `wght` first with a serious programming repertoire: ASCII, practical Latin, required combining marks, programming punctuation, useful operators/arrows and compatible box drawing.

Add features/coverage back incrementally. The objective is the largest useful maintainable contract, not merely making varLib stop throwing.

## 5. Width
Only after `wght` succeeds cleanly, test `wdth` using calibrated public width masters.

## Acceptance
Ship only if reproducible, exclusions are understandable, critical coding glyphs remain, shaping is correct, and no recurring manual binary surgery/private generator fork is required.

## Rejection
If success requires large bespoke patches, destroys the useful repertoire, or creates an upstream-update trap, document the evidence and freeze the decision until Iosevka changes.
