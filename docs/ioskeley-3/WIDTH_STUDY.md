# Condensed Width Study

Status: planned. Current configuration anchors are Normal at shape 600 and SemiCondensed at 540. Candidate values below are Iosevka shape settings, not measured advances or approved public widths.

The previous Condensed was useful to a small group but looked excessively narrow/crushed to the maintainer.

The study asks:

> **Can Ioskeley have a readable, distinct condensed design?**

## Private candidates
600 / 576 / 560 / 548 / 540 / 525 / 510 plus the old narrow point as historical control.

Recover the historical narrow value and its source revision before building the control. Keep height, weight, slope, hinting and specimen settings consistent across candidates; record each build's inputs and hashes. Save a comparison sheet and a written verdict, including reasons for rejecting candidates.

## Measure
For each candidate:
- advance;
- ink bbox / cell;
- sidebearings;
- counter widths;
- apparent darkness;
- H M W m n x;
- 0 O 8 / a g e;
- () [] {};
- <> +- = != => ->;
- underscore/dots;
- real code texture.

## Human tests
12/13/14/16px, standard DPI/HiDPI, editor, diff, terminal, logs/data, long identifiers and comments.

## Berkeley reference
If a legitimate local reference is available, compare normalized relationships between its widths. Width names do not imply equivalent Iosevka numeric values. Do not copy outlines.

## Ship a third width only if
1. clearly distinct from SemiCondensed;
2. preserves counters/forms rather than looking squeezed;
3. improves a real dense-use scenario;
4. remains coherent across weights/italic;
5. justifies its package/maintenance cost.

Otherwise Normal + SemiCondensed become the explicitly final public width system.
