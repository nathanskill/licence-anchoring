# Amendment 4 — F1: the 40 % stratum cap cannot bind, and what is done instead

Status: **a pre-registered rule meeting a frame it does not fit.** Recorded
because the rule was declared in advance and cannot be executed as written;
the resolution is stated here rather than improvised in code.

## The rule and the frame

Amendment 2 fixed F1 sampling as "stratified random … allocation proportional
to stratum size, capped so no single stratum exceeds 40 % of the drawn
sample". The realised F1 strata, joining the 96,141 matched domains against
the F2 register frame, are:

| Stratum | Domains |
|---|---|
| no offshore entity | 96,107 |
| Seychelles | 27 |
| Belize | 7 |

The cap was written as a guard against one stratum swamping the draw. Here it
inverts: capping the large stratum at 40 % of a draw of n would require 0.6 n
observations from a combined pool of 34 domains, which is impossible for any
n above 57 and absurd well before that — it would sample the same 34 domains
repeatedly while leaving 96,107 almost untouched.

The cause is not a defect in the frame. F1 is corpus-driven by construction,
so the overwhelming majority of its members have no entry in any offshore
register we were able to enumerate. That is precisely the "no offshore
entity" stratum the frozen protocol §4 names, and precisely the reason F1 was
run: F2 cannot supply that stratum at all.

## What is done instead

1. **The two small strata are taken in full** (34 domains). They are the F1
   members that also appear in an enumerated offshore register, so they are
   both cheap and independently interesting; nothing is gained by sampling
   them.
2. **The remainder of the draw is taken from "no offshore entity"** by seeded
   random sampling, seed 20260723 as fixed in amendment 2.
3. **The realised allocation is published** with every count derived from the
   draw, so no reader has to reconstruct it. It is *not* proportional and
   *not* capped: it is census-of-the-small-strata plus a random sample of the
   large one.

## What this changes and does not change

It changes the allocation rule for F1 only. It does not touch the seed, the
token list, the exclusions, the taxonomy, the operative-entity rule, the
two-step register verification, the language discipline, or the N = 80 target
/ 60 floor. Units already verified under F2 and F3 are unaffected.

**Consequence for claims:** F1-derived counts are not projectable to the F1
frame by simple scaling, because the small strata are censused while the large
one is sampled. Any F1 prevalence statement must either be restricted to the
large stratum, where the sampling is genuinely random, or carry stratum
weights explicitly. This is recorded now so that the constraint is fixed
before any F1 number exists, rather than being discovered when one is wanted.

Recorded 2026-08-02, before the F1 draw.
