# Rank 4's paired-anchor rule, registered before any pool-7 claim (Q140(x))

*Q140(x), Wed 4 Nov 2026 (PST), desk only. Committed in the same commit as blind pool 7 and the frozen predictions, before any
pool-7 claim. It answers Q139's final critic, open rank 4 ("A card nobody has measured"), on the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6. The machine-readable form
is [`rank4_rule.json`](rank4_rule.json), and [`score_rank4.py`](score_rank4.py) applies it.*

## Why

No cheap read predicts a card's scale to within 1% held out (E153: −1.7% at best on aifoundry3), and V² at 600 MHz misses card 1
by 5.2%. So an unmeasured card carries a 2–5% systematic error, about 0.3–0.7 W on a 14 W float kind, which is more than the model's
own error. Post hoc, on pool 6, random anchors run on both 600 MHz cards gave card 1's float scale to −0.15% of the pool's median and
int8's to −1.04% (Q139's final critic, re-derived in Q140(c)'s check 3,
[`check3-anchor-card-scale.json`](../../../../docs/reports/data/2026-11-04-q140c-critic-checks/check3-anchor-card-scale.json)). This rule
tests that route blind: does a short run of random anchors give a second card's scale?

## The rule

**A card's scale is the median of its anchors' ratios to aifoundry3's. It must land within 1% of the pool's median ratio for
floats, and within 2% for int8, in each session pair.**

- **The cards.** The reference is aifoundry3 card 0 (600 MHz pinned). The scaled card is aifoundry1 card 1 (600 MHz).
- **Session pairs.** E163 (pool 7 on aifoundry3) pairs with E164 (pool 7 on card 1) first. A later pool-7 session on either card
  pairs with the most recent pool-7 session on the other card before it. Each pair is scored from its own two sessions only.
- **D.** A tile's measured switching watts over its format's zeros at 600 MHz. It is each session's registered primary reduction on
  Q139(u)'s footing (`reduce_footing.K_FROZEN`: 0.2056 W/C on aifoundry3 and 0.3134 W/C on card 1; E82 A2's dip rule, once), the
  mean over the session's kept passes. This is the D its power rules score (E153's and E157's `power_rows` `measured` and
  `pool_anchors` `measured_D`).
- **The anchors.** Pool 7's random anchors. Floats: `fp32.anchor7_randn_a`, `fp32.anchor7_randn_b`, `fp16.anchor7_randn_a` and
  `fp16.anchor7_randn_b`. int8: `int8.anchor7_full_a` and `int8.anchor7_full_b`. The three zeros anchors are the footing, not part
  of the scale. Each session must run all nine anchors. They are priority 2 in the MANIFEST, but they are not among the four
  priority-2 tests a session may drop first.
- **The card's scale.** For each anchor, r = D(card 1) / D(aifoundry3). Then s_anchor is the median of the family's r: the mean of
  the middle two of the four float ratios, and the mean of the two int8 ones.
- **The pool's median ratio.** s_pool is the median of D(card 1) / D(aifoundry3) over pool 7's non-anchor tiles of the family, of
  any priority, measured in both sessions. A float tile (fp32 or fp16) must read D ≥ 5 W on both cards, and an int8 tile D ≥ 1 W.
  This is E157's X1 / X2 selection, applied to pool 7.
- **Verdict, per family.** PASS if |s_anchor / s_pool − 1| ≤ 0.01 (floats) or ≤ 0.02 (int8), and FAIL if not. The verdict is NOT
  SCORED (never PASS) if fewer than 3 of the 4 float anchors, fewer than 2 of the 2 int8 anchors, or fewer than 5 pool tiles of the
  family were measured on both cards. A family passes if it passes in every scored pair. Rank 4 passes in a pair if both families
  do.

## Reported beside it (no verdict)

- Each anchor's ratio, with its standard error from the passes: each card's sd over its passes / √n, combined in quadrature on the
  ratio.
- The mean of the anchors' ratios beside their median.
- **The E78 arm:** s_anchor with E78's `fp32.randn` and `fp16.randn` (floats) and `int8.full` (int8) joined, if both sessions ran
  them.
- **Per format:** fp32's two anchors against fp32's own pool median, and the same for fp16.
- s_anchor and s_pool against the card-1 terms the frozen models apply. M9 and M8 apply 0.9616 to every format; M7 and M6 apply
  0.9711 to floats and 0.9735 to int8.
- **The per-tile transfer:** the relative rms of the pool tiles' ratios about s_anchor and about s_pool. This is how well one scale
  carries a measured kind between the cards.

## Forecast (registered)

The basis is pool 6, post hoc (the critic's check, re-derived by Q140(c)).

- **Floats: PASS**, at about −0.15% against a 1% line. The difference's standard error is about 0.16%: the four anchors' 0.10% from
  their passes, and the pool median's 0.12% (95% interval [0.9613, 0.9659] over 25 tiles).
- **int8: PASS more likely than not, but not secure.** The offset is about −1%. Card 1's int8 anchor read 3.6% sd over its three
  passes in E157. So two anchors carry a standard error of 1.2–1.5%, and the pool median carries 0.66%. The difference's standard
  error is then 1.35–1.64%. The chance of landing inside ±2% is 69–75% with pool 6's −1.04% offset, and 78–86% with none (normal
  approximation). More card-1 passes would narrow it.

## Checked before the commit

`python3 -B score_rank4.py --selftest <repo>` runs the scorer unchanged but for the anchor names on pool 6's committed sessions (E153,
E157), using the anchors the critic used there (E78's and pool 6's, per format). It reproduces Q140(c)'s check 3 and E157's
registered X1 / X2: the same 25 float and 16 int8 tiles, s_pool equal to X1's 0.9632 and X2's 0.9681, s_anchor 0.9618 and 0.9580,
offsets −0.15% and −1.04%, both PASS, and the per-tile spread 0.72% and 2.07%. That is 16 checks with 0 differing, in
[`selftest-rank4.txt`](selftest-rank4.txt).

## What it cannot say

- **One card pair.** A card nobody has measured still needs its own paired run. aifoundry1 card 0 is excluded by its alarm, and a
  third card needs his word. Passing here shows the protocol works between these two cards, not that every card scales alike.
- **The anchors are random kinds only.** If the card ratio depends on the kind (card 1 repeats an int8 tile's D only to 0.1–0.2 W
  between sessions, E157 K1), the anchors' scale can sit off a pool whose mix differs. The per-tile spread says how much.
- **Session-wide factors cancel.** A factor common to a session's tiles cancels in s_anchor / s_pool, such as the duty a C log
  lowers (Q140(m) D1: 0.9932 against 0.9963). So the rule tests the scale's consistency across kinds, not the session's absolute
  level.

SPDX-License-Identifier: Apache-2.0
