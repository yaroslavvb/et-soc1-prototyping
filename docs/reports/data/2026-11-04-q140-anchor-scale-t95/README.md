# The paired-anchor card scale's 95% interval, with t quantiles (dated note, Wed 4 Nov 2026, week 45)

*Post hoc and desk only, written after the second verifier of Q140's records, the one that read their corrections. Nothing
registered, frozen or measured changes. It corrects one inference in those corrections' dated clauses: Q140's "How to read ±" in
[`05-claims.md`](../../../findings/05-claims.md) and the Q140 row of [`02-requests.md`](../../../findings/02-requests.md) say,
rightly, that the paired-anchor card scale's ± is one standard error, and then that "a 95% interval is about twice as wide, so
int8's scale is about ±3% at 95%". Doubling a standard error gives a 95% interval when the error rests on many kinds, as M8's and
M9's fitted prices do. The anchor scale's rests on a few passes. This answers rank 4 of Q139's final critic (the paired-anchor card
scale), under the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)
item 6 (a power model across kinds). It changes no prediction of power or heat: it says how wide one card pair's measured scale
is.*

## Results

| Scale, card 1 over aifoundry3 | Point against pool 6's median | Standard error | Degrees of freedom | 95% half-width with t | Doubled, as the clause had it |
|---|---|---|---|---|---|
| int8, the mean of 2 random anchors | −1.04% | 1.50% | 2.14–4.28 | **4.07–6.08%** | 3.00% |
| floats, the mean of 4 | −0.15% | 0.10% | 5.38–10.76 | **0.23–0.26%** | 0.21% |

- **int8.** E78's int8 anchor ran 4 passes on aifoundry3 (0.78% sd) and 3 on card 1 (3.62% sd). Card 1's three passes carry almost
  all of the ratio's 2.12% standard error, so its Welch–Satterthwaite degrees of freedom are 2.14. Pool 6's anchor carries pass means
  only, so check 3 took its error as equal to E78's. If that error is a copy of E78's, it adds no information (2.14 degrees of
  freedom, the low end). If pool 6's anchor had passes of its own with the same spread, the information would double (4.28, the
  high end). With t quantiles, as the lab's own pass intervals take them (`one_sample`, `welch` and `ratio` in
  [`ablcore.py`](../../../../tools/claims-v3/abla/ablcore.py)), the 95% half-width is **4.1–6.1%**, not 3%. At whole degrees of
  freedom it is 6.46%, 4.78% and 4.17% at 2, 3 and 4. E78's int8 anchor alone, by the lab's ratio interval (Welch on the logs of
  the passes, 2.14 degrees of freedom), reads −8.2% / +9.0%.
- **Floats.** Their scale rests on four anchors, with 5.38–10.76 degrees of freedom. Doubling gives 0.21%, and t gives 0.23–0.26%.
  The floats' −0.15% stays far inside rank 4's 1% line either way.
- **M8's and M9's fitted prices** are a jackknife by kind over 66–370 kinds a family (`families.*.n_kinds` in
  [`m8.json`](../2026-11-03-q139m-model/m8.json) and [`m9.json`](../2026-11-04-q140m-m9/m9.json)). There t(0.975) is 1.97–2.00,
  so doubling their ± one standard error does give a 95% interval, as the clause said.

**What it changes.** No registered figure, rule or prediction. Rank 4's rule for pool 7, frozen in Q140(x), is untouched. For
reading: on this one card pair and session pair, int8's scale is −1.0% with a 95% interval of about ±4–6%, not ±3%. Check 3's own
reading stands: int8's two anchors carry about ±1.5% of their own, and rank 4's 2% line for int8 is about 1.3 of those standard
errors.

## How it was made

[`anchor_scale_t95.py`](anchor_scale_t95.py) writes [`anchor-scale-t95.txt`](anchor-scale-t95.txt) and
[`anchor-scale-t95.json`](anchor-scale-t95.json). It uses the standard library only:

    python3 -I -B anchor_scale_t95.py <lab clone> --out anchor-scale-t95.json > anchor-scale-t95.txt

It reads Q140(c)'s [`check3-anchor-card-scale.json`](../2026-11-04-q140c-critic-checks/check3-anchor-card-scale.json)
(`anchors`, `scale`) and the passes in E153's and E157's `scored.json` (`e78_anchors_D`). Check 3's per-pass figures agree with
those passes, and its standard errors are reproduced to 1e-12. It also reads M8's and M9's `n_kinds`. The t quantile is a verbatim
copy of `ablcore.py`'s pure-Python Student t (lines 314–359, unchanged since `f7aea65b`), because `ablcore.py` imports numpy.

## Sources

- Q140(c) check 3: its [`README.md`](../2026-11-04-q140c-critic-checks/README.md) section 3, and
  [`check3-anchor-card-scale.txt`](../2026-11-04-q140c-critic-checks/check3-anchor-card-scale.txt) lines 4 and 7 (the per-pass sd,
  the passes, pool 6's assumed error, and the anchors' mean ± 0.0144, or 1.50%).
- E153's [`scored.json`](../2026-11-03-e153-blind6-aifoundry3/scored.json) › `primary.primary.e78_anchors_D`, and E157's
  [`scored.json`](../2026-11-03-e157-blind6-card1/scored.json) › `primary.e78_anchors_D`.
- Q140(m)'s [`README.md`](../2026-11-04-q140m-m9/README.md) section 3 (± one standard error, the jackknife by kind).
