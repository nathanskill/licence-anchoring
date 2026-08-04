# Amendment 6 — F1 precision measured; the probe's missingness is not at random; and a caveat in the frozen text is false as written

**Date:** 2026-08-04
**Status:** post-hoc. The F1 presence probe had already been executed when this amendment was written. Nothing here retunes frame F1 — amendment 3 forbids that, and the prohibition is honoured: the frame, its `VERTICAL_TOKENS`, its `SHORT_TOKENS` and its draw are untouched.
**Sequence, stated first so a reader does not have to reconstruct it:** the probe ran to completion over the full 1,000-domain draw; the summary was written; the analysis below was then performed on the resulting artifact; this amendment records what it found.

---

## 1. The measurement F1 was built to produce

`probe_f1.py`'s header states the commitment being discharged here:

> F1 is recall-oriented by construction (amendment 3), so its precision is unknown until measured. The yield here IS that measurement. It is published whatever it turns out to be; the frame is not retuned in response to it.

It has now been measured.

| Stratum | In draw | Probed | Chinese-present | Rate |
|---|---|---|---|---|
| Belize | 7 | 7 (censused) | 2 | — |
| Seychelles | 27 | 27 (censused) | 1 | — |
| no offshore entity | 966 | 777 | 7 | 0.90% |
| **Total** | **1000** | **810** | **10** | **1.23%** |

Per-stratum rates are not comparable without care (amendment 4): the two small strata are censused, the large one sampled. Both small strata are now complete.

The ten domains with Chinese-language captures in CC-MAIN-2026-25:

`3h-trading.com`, `capital.com`, `gold-money.cn`, `m4markets.com`, `markets.com`,
`wh-hw.com`, `wh-sinobest.com`, `wh10176.cn`, `wing-fx.com`, `world-trader.com`

**Nine of the ten are new to the claim corpus** (only `m4markets.com` was already carrying claim units). The corpus domain base goes from 15 to 24, a 60% expansion. Two — `gold-money.cn` and `wh10176.cn` — are `.cn` domains, which a register-anchored frame such as F2 structurally cannot reach; reaching them is the entire reason F1 exists.

Two of the hits (`wh-hw.com`, `wh-sinobest.com`) were drawn by the `wh` token in the frozen `SHORT_TOKENS`, i.e. the Pinyin initials of 外汇. The frozen vocabulary paid out on live data.

**Two of the ten (`capital.com`, `markets.com`) are large mainstream regulated brands** that a register-based frame would reach anyway. The distinctive, F2-unreachable contribution is therefore smaller than nine, and should be described that way rather than as nine.

---

## 2. The missing 190 are not missing at random, and the direction of the bias is identifiable

810 of 1,000 domains were probed. The remaining 190 (all in the sampled "no offshore entity" stratum) are service failures. Per the frozen design, a failed query is never written, so these are correctly "not yet probed" rather than false negatives. A retry pass recovered 39 of them and added **no** new Chinese-present domains.

A live diagnostic on six of the persistent failures returned, in every case, **HTTP 504 Gateway Time-out** from the Common Crawl CDX index. The failures spread across TLDs roughly in proportion to the draw (`.com` 79/389, `.ru` 18/57, `.de` 6/40), so this is not a TLD artifact.

A 504 on a CDX index is a server-side timeout on an expensive query, and query cost rises with the number of captures held for the domain. Capture count is in turn a strong predictor of Chinese presence in the data we do have:

| Capped total captures | n | Chinese-present | Rate |
|---|---|---|---|
| 0 | 519 | 0 | 0.00% |
| 1–9 | 144 | 1 | 0.69% |
| **10–99** | **61** | **5** | **8.20%** |
| 100–999 | 17 | 1 | 5.88% |
| 1000+ | 2 | 0 | 0.00% |

**Therefore the 190 unprobed domains are plausibly enriched for high capture counts, and hence enriched for Chinese presence. 1.23% is a lower bound, not a point estimate.**

Bounding it explicitly:

| Assumption about the 190 | Implied overall rate |
|---|---|
| None has Chinese content (hard floor) | 10/1000 = **1.00%** |
| They behave like the probed stratum (0.90%) | 11.7/1000 = **1.17%** |
| They behave like the 10–99 capture band (8.20%) | 25.5/1000 = **2.55%** |

The defensible statement is that F1's precision on this draw lies **between roughly 1.0% and 2.6%**, with the lower end assuming the timeouts are uninformative and the upper end assuming they are maximally informative. This range is reported instead of the bare 1.23%.

This bias is a property of the instrument (the keyless CDX index), not of the frame, and no change to F1 would remove it.

---

## 3. Defect: a caveat in the frozen summary is false as written

`f1_presence_summary.json` carries this caveat, which is emitted by frozen code:

> Service failures are not recorded, so absence in the file means not-yet-probed, never a silent failure.

**This is false for the total-capture field.** The probe issues two queries per domain — Chinese-only, then any-language. The write path is:

```python
n_any, _ = cc_query(d, False, ANY_CAP)
if n_any < 0:
    n_any = ""
out.write(json.dumps({... "n_captures_capped": n_any ...}))
```

When the Chinese-only query succeeds and the any-language query fails, the row **is** written, with the service failure silently downgraded to an empty string. **34 rows in the sampled stratum (4.4%) carry `n_captures_capped: ""`.**

Scope of the damage:

- **The primary endpoint is unaffected.** Presence is defined on `n_zho_captures_capped > 0` alone (caveat 3: "only presence (n > 0) is used analytically"), and that field is never downgraded — a failed Chinese-only query skips the row entirely. The 1.23% figure and the ten domains stand.
- **The secondary analysis in §2 loses those 34 rows**, which is why the capture-count table above is computed on 743 rather than 777 domains. It is reported on that basis.
- **The caveat's guarantee does not hold for `n_captures_capped`** and must not be relied on for it.

Corrected caveat text, to be used wherever the summary's caveats are quoted:

> Service failures on the Chinese-only query are not recorded, so absence of a domain from the file means not-yet-probed, never a silent failure. Service failures on the any-language query **are** recorded, as an empty `n_captures_capped`; that field is therefore missing-not-at-random and must not be read as a count of zero.

The frozen file is not edited. Consistent with the discipline of this project, the correction lives here and the code fix — writing an explicit `null` with a `capture_query_failed: true` flag rather than `""` — is deferred to a future run rather than applied retroactively to existing rows.

---

## 4. Consequence for the study, stated without softening

F1's precision is of order one per cent. Reaching the 60-unit floor through F1 alone would require a draw an order of magnitude larger than the present one, at roughly 2.2 seconds of politeness-bounded querying per domain.

**F1 is a reach instrument, not a volume instrument.** It was never designed to be efficient; it was designed to reach a stratum that a register-anchored frame structurally cannot see, and on this evidence it does exactly that and little else — nine new domains, two of them `.cn`.

The 60-unit floor therefore needs a route other than enlarging F1. Enlarging F1 in response to a disappointing yield is precisely the retuning that amendment 3 prohibits, and it is not done here.

---

## 5. Artifacts

- `artifacts/frames/f1_presence_probe.jsonl` — 810 rows, append-only, resumable
- `artifacts/frames/f1_presence_summary.json` — regenerated after the retry pass
- `artifacts/frames/frame_f1_draw.csv` — 1,000 domains, unchanged

---

# Revision 1 — 2026-08-04, later the same day

**Sequence, stated first.** Everything above was written and committed (`913aba1`) against a probe file of 810 rows. A further retry pass then completed, taking the file to **979 of 1,000**. The revision is recorded here rather than by editing the text above, so that what was claimed at 810 rows and what survives at 979 are both visible. Two of the three conclusions above are **superseded**, and one new finding is more serious than anything in the original.

## R1.1 Superseded: the bounded range

| | at 810 rows | at 979 rows |
|---|---|---|
| Probed | 810 | 979 |
| Chinese-present | 10 | **14** |
| Rate | 1.23% | **1.43%** |
| Unprobed | 190 | **21** |
| Bounded range | 1.0% – 2.6% | **1.40% – 1.57%** |

The original's headline — that 1.23% was a lower bound with real uncertainty attached — was an artifact of an incomplete run. With 21 domains outstanding the bound is tight and the point estimate is usable. **The wide range in §2 above should not be quoted.**

## R1.2 Strengthened: the missingness gradient

The capture-count gradient is now steeper and rests on more data (n = 901 usable of 945 in the sampled stratum):

| Capped captures | n | Chinese-present | Rate |
|---|---|---|---|
| 0 | 642 | 0 | 0.00% |
| 1–9 | 162 | 2 | 1.23% |
| 10–99 | 72 | 6 | 8.33% |
| 100–999 | 23 | 3 | **13.04%** |
| 1000+ | 2 | 0 | 0.00% |

The mechanism argued in §2 (CDX 504s fall on expensive, high-capture queries; capture count predicts Chinese presence) is better supported than before. Its *practical* consequence has evaporated, because only 21 domains remain unprobed. **The methodological point stands; the uncertainty it implied does not.**

## R1.3 New, and worse: the probe measures Chinese presence, not relevance

This was not asked in the original and it should have been. The probe answers "does this domain have Chinese-primary captures?" It does **not** answer "is this a retail FX operator making regulatory claims?" Reading the stored sample URLs domain by domain:

| Domain | Provisional read | Evidence (stored sample URLs only) |
|---|---|---|
| capital.com | FX/CFD broker | `/zh-hans/analysis/` — F2-reachable |
| markets.com | FX/CFD broker | `/zh/`, `/zh-tw/` — F2-reachable |
| m4markets.com | FX/CFD broker | already in the claim corpus |
| 3h-trading.com | plausible, unconfirmed | path `/fudengwangpeizi/` contains a transliteration of 配资 (margin financing) |
| gold-money.cn | plausible, unconfirmed | `/wp/` only; topic not determinable from path |
| wh10176.cn | plausible, unconfirmed | `/article_cat_12.html`; generic CMS |
| world-trader.com | plausible, unconfirmed | root only, 2 captures |
| **wing-fx.com** | **not FX** | `/channel-fx/even-channel-strip`, `/master-channel-strip` — audio channel strips. The `fx` here is audio effects. |
| **canine-prime.com** | **not FX** | canine |
| **gold-skin.co.kr** | **not FX** | `cn.` subdomain of a Korean `.co.kr` cosmetics domain |
| wh-hw.com | likely not FX | `wh-` reads as Wuhan (武汉), not waihui |
| wh-sinobest.com | likely not FX | "wh-sinobest" reads as Wuhan Sinobest |
| ks-wh.com.cn | likely not FX | `.com.cn`, `wh-` reads as Wuhan |
| wh-lz.com | likely not FX | `wh-` reads as Wuhan |

**Correction to a claim made in the original text of this amendment.** §1 above states that `wh-hw.com` and `wh-sinobest.com` "were drawn by the `wh` token in the frozen `SHORT_TOKENS`, i.e. the Pinyin initials of 外汇 — the frozen vocabulary paid out on live data." **That inference was unsupported and is probably backwards.** `wh-` is a common prefix for Wuhan-based companies. The token fired; nothing was shown to have been paid out. The same applies to `fx`, which fires on audio effects.

The consequence, stated as an upper bound because the four "plausible" domains have not had their content checked:

| Measure | Count | Rate |
|---|---|---|
| Chinese-presence hits | 14 / 979 | 1.43% |
| Relevant at best case (broker + all four plausible) | 7 / 979 | 0.72% |
| **Distinctive — relevant AND not F2-reachable** | **≤ 4 / 979** | **≤ 0.41%** |

The four plausible domains require a content check before any of this is final. That check is the immediate next step and its result goes in a further revision, whatever it is.

## R1.4 What this does to §4

§4 above concluded that F1 is "a reach instrument, not a volume instrument". That was too kind. On the completed run, **F1's distinctive usable yield is at most four domains in a thousand, and the two short tokens `wh` and `fx` are producing systematic false positives** — `wh` on Wuhan, `fx` on audio.

Amendment 3 committed to publishing the yield "whatever it turns out to be". This is what it turned out to be, and the frame is still not retuned: the short tokens stay, because removing them now, after seeing which domains they caught, is exactly the retuning that was prohibited. The finding is reported as a property of the frozen instrument.

The route to the 60-unit floor is not F1, and it is now not a close question.
