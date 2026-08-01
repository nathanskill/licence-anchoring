# Amendment 3 — F1: tokens in the public-suffix position

Status: **made after observing the composition of the F1 match set, and
disclosed as such.** This is the honest sequence and it is stated first
because the reader is entitled to weigh it: amendment 2 froze the token list
before execution, the scan ran, and this clarification was written after
seeing what the frozen pattern matched. The token list itself is **not**
changed by this amendment, and no token is added or removed.

## What was observed

The frozen pattern matched **166,825 of 117,963,409 domains** (0.14 %).
Decomposing the matches by the position in which the token occurs:

| Where the token occurs | Domains | Share |
|---|---|---|
| Public-suffix position only | 70,684 | 42.4 % |
| Registrable-name position (retained) | 96,141 | 57.6 % |

The suffix-only matches are carried almost entirely by six generic top-level
domains that happen to be spelled as vertical vocabulary: `.cfd` (47,892),
`.capital` (6,619), `.market` (5,846), `.exchange` (4,239), `.gold` (3,669),
`.markets` (905). Inspection of a seeded random sample shows these to be
ordinary registrations under a cheap generic TLD — `50-tow-truck-near-me.cfd`
is a representative example.

## The clarification

**A token occurring only in the public-suffix position does not place a domain
in frame F1.**

The justification is structural rather than empirical, and would hold whatever
the counts had turned out to be: the public suffix is a string chosen by the
registry, not by the registrant. Amendment 2 defines F1 by whether a domain
"carries a vertical token", which is a statement about the registrant's naming
choice — the same reasoning that put Hanyu Pinyin transliterations into the
token list, and the same reasoning behind matching at label boundaries so that
substrings inside unrelated words do not count. Counting `.cfd` as a vertical
token measures the TLD registry's marketing, not the site's.

It remains true that this reasoning was written down only after the scan. A
reader who discounts post-hoc clarifications should use the unrestricted
figure; both are published, and every downstream count states which frame
definition it uses.

## What is NOT claimed

This clarification does not make F1 precise. The registrable-name matches
still include large numbers of domains that have nothing to do with retail
FX/CFD — `shilajit-gold.com`, `prime47carmel.com`, `f50capital.com` are all in
the retained set. F1 remains a **recall-oriented name-pattern frame** whose
precision is supplied downstream by the Chinese-language presence probe and
then by the claim extractor, not by the pattern. The frame's precision is
therefore an empirical property to be measured and reported at each stage, and
the yield rates are published for exactly that reason.

## Effect on figures

- F1 frame size: **166,825** unrestricted / **96,141** under this
  clarification. Both appear in `frame_f1_summary.json`
  (`matched_unrestricted` and `matched`).
- No unit verified under frames F2 or F3 is affected; their claim ids,
  codings and counts are unchanged.
- No token, exclusion, seed or stratum rule from amendment 2 changes.

## Correction of this file's own figures

The counts first written into this amendment (166,817 / 96,037 / 70,676) came
from an ad-hoc recomputation whose end-of-token anchor was corrupted by shell
escaping. They are superseded by the figures above, which are those the
committed `frame_f1_summary.json` reports. The discrepancy is at the fourth
significant figure and changes no share and no conclusion; it is recorded
rather than quietly overwritten because a number in an amendment that does not
match the artifact it describes is exactly the kind of drift these amendments
exist to prevent.

Recorded 2026-08-02, after the scan of 2026-08-02; figures corrected the same
day against the committed artifact.
