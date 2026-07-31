# Amendment 1 to Locked Protocol v1.0

Date: 2026-07-31.
Applies to: `protocol/locked_protocol_v1.0.md` (frozen at tag
`v1.0-protocol-freeze`; that file is not modified). Per the protocol's
amendment rule, this amendment records corrections and pins choices; it does
not alter the taxonomy, the sampling frames, the coding rules, or the
operative-entity rule.

## 1. Register size: 193 → 231 securities-dealer entries

The frozen protocol states (sections 4 and 6) that the Seychelles FSA
capital-markets register contains 193 securities-dealer entries. That figure
came from access testing. The register snapshot archived three days after
the freeze (`data/registers/seychelles_securities_dealers_20260727T044232Z.html`,
sha256 `52d319f3653dd58abcd23ac6d9509f06d7c5780765063cb88838dbdf76b468b4`)
contains **231 securities-dealer entries** (434 records across 7 categories;
the parse is independently reproducible byte-for-byte from the archived
HTML). The register grew between access testing and the archived fetch; the
**archived snapshot is authoritative** for frame F2. Counts are reported as
"231 securities dealers (+203 other records)", not "434 registrants": the
203 include 195 representative entries (named natural persons) that are
excluded from the committed artifact under section 7 rule 4 and kept
derivable locally only.

## 2. Common Crawl crawl ID pinned: CC-MAIN-2026-25

The frozen protocol names no specific crawl for the F1×F2 Chinese-language
presence probe. The crawl actually queried is **CC-MAIN-2026-25**, pinned at
the first probe run (post-freeze). This amendment fixes that choice so it
cannot drift. A code comment in `src/frame_chinese.py` previously claimed
the crawl ID was "frozen at protocol freeze"; that claim was false and has
been corrected in the source.

## 3. Wording: register-listed domains are not (yet) "onboarding entities"

The message of the frozen commit `330bbbe` describes certain probe results
as "the Seychelles onboarding entities of major ASIC-licensed brands". That
phrasing pre-asserts what the frozen operative-entity rule (section 5,
OE-1..3) has not yet determined — no OE determination has run. The commit
message is immutable; this note supersedes it. The correct description of
rows such as pepperstone.com and icmarkets.sc, in all outputs, is:

> Seychelles-registered group entities whose register-listed domains carry
> Chinese-language pages.

## 4. Author affiliation line

The frozen protocol's author line reads "independent researcher", which sits
poorly beside the section 10 disclosure of full-time brokerage employment.
In all future outputs the author line is the neutral form:

> Zhennan (Nathan) Yu, Sydney; see section 10 for conflicts.

The frozen file itself stays untouched; section 10's conflict-of-interest
disclosure is unchanged and continues to apply in full.
