# E112: replicates on aifoundry1 card 1 — E91 re-run so that it scores, and E95's real tiles on a second card (600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) as of `1fe8377a18af`: item 7, "More real tensors" ("Still open: another card"), and the final critic's replicates (its item 8: "E91 ... not re-run").*

*Sun 1 Nov 2026 (week 44), Q133. Pre-registered in `0623b052` (git commit time 12:51:58, pushed 12:52:02 PST, before the
claim and the first launch): [`tools/claims-v3/e112/E112.md`](../../../../tools/claims-v3/e112/E112.md), frozen numbers in
`predictions-e112.json` (sha256 `4c940b53…`) and `predictions-real2-card1.json`. No amendment. aifoundry1 card 1
(`V3_DEVICE=1`, its own lock) at 600 MHz, 498.6 mV mean, TDP 65 W / threshold 65 °C / 600 MHz / 499 mV read at the session's
start (12:54:09, the smoke's block) and end (13:49:02, the queue's read under the lock with `timeout 10`), and at both ends of
every block, never set: no governor move, no reset, no PMIC command, no `--reset-ms`. Claim 1566555908283302061 in
#community-lab, posted 12:53:53.736 PST, released by editing the same post at about 13:49:24 PST: **55.5 card-minutes of the
registered 60** ([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)).*

**What ran.** One session, two designs, in the registered order. (a) E91's registration, unchanged: E86's 32-run pass
(Q130(n)'s nine real GPT-2 small tiles, E78's three comparison kinds, E78's six anchors three times, the tie twice), E86's card
code, `reduce_e91.py`, `score_e91.py` and `predictions-e91.json` byte for byte, on five passes (11210–11213 and the registered
spare 11214). (b) E95's 53-run pass, unchanged (Q132(r)'s thirty real2 tiles and three of E86's), on three passes
(11250–11252). The budget was kept in exact seconds from the claim: an entry started only if its projected end fell inside the
claim + 3,480 s. **D** is a tile's board power over its own type's all-zeros level, **S** over idle, **whole board** (p80) the
window's leakage-corrected power; a ratio "÷ random" is over the same pass's random kind of that format (`fp32.randn`,
`fp16.randn`, `int8.full`). Intervals are 95% over kept passes, t(0.975, n − 1) × SE.

## Results

**(a) E91's registration now scores: five of five passes kept, 7 PASS and 4 FAIL of its 11 rules. The failures are the three
cross-card rules E91 registered as expected to fail (E82's September band) and the session tie R5, which fails at the session's
own leakage slope and passes at 0.1994 W/°C. (b) E95's pass on card 1 scores nothing: the registered zeros-line gate set its
third pass aside, by 0.003 W, at every leakage arm; the spare did not fit the budget; two kept passes are below E95's minimum of
three, so all 13 claims and the three cross-card rules read NOT SCORED.**

| rule | says | threshold | happened | verdict | at the arms |
|---|---|---|---|---|---|
| **E91-R1** | each real tile's D inside its E91 interval | ≥ 7 of 9 | 9 of 9 | **PASS** | PASS at all four leakage arms; dips kept NOT SCORED (2 passes) |
| **E91-R2** | rms per format of D − the E91 point | 2.0 / 2.0 / 1.0 W | fp32 0.483, fp16 0.386, int8 0.349 W | **PASS** | PASS at all four |
| **E91-R3** | ρ = mean D(real)/D(random) over the three tiles, below the threshold | < 1, < 1, < 0.9 | fp32 0.9905 ± 0.0032, fp16 0.9818 ± 0.0039, int8 0.8265 ± 0.0206 | **PASS** | PASS at 0.1994, 0.545, 0.3803; INCONCLUSIVE at 0 |
| **E91-R4** | each tile on its predicted side of `nn_like` / `gauss_q` | the sign | all nine; int8 `l0_mlp_up` −0.214 ± 0.147 W below `gauss_q` | **PASS** | PASS at 0.1994, 0.3803; INCONCLUSIVE at 0.545, 0 |
| **E91-R5** | E82's seven card-1 cells within their bands | ±0.50 / ±0.25 W | `fp32.randn` −0.502 W, `int8.gauss_q` −0.276 W outside; the other five inside | **FAIL** | PASS at 0.1994, 0.3803; FAIL at 0.545, 0 |
| **E91-S1** | each tile's D÷random inside its ratio interval | ≥ 7 of 9 | 9 of 9 | **PASS** | PASS at all four |
| **E91-X1** | Spearman ρ, card 1 against aifoundry3 (E86), per type | ≥ 0.90 | fp32 0.900, fp16 1.000, int8 1.000; fp32 sits exactly on the threshold (five kinds, one adjacent swap: `l0_mlp_up` and `l6_mlp_down`) | **PASS** | PASS at 0.1994 on both and none on both |
| **E91-X2a / X2b / X3** | E82's one-scale rules, band [0.88, 0.99] | ≥ 80% of point ratios inside / ≥ 80% of intervals overlapping / the median inside | 0 of 15 inside; 0.133 overlapping; median D(aifoundry3)/D(card 1) 1.0520 (IQR 1.0492–1.0587) over 15 kinds | **FAIL** ×3 (expected) | FAIL at both resolved pairings |
| **E91-X4** | median over the nine real tiles of D(aifoundry3)/D(card 1) | [1.0008, 1.0608] | 1.0542 (fp32 1.0519, fp16 1.0576, int8 1.0791) | **PASS** | PASS at both resolved pairings |

Source: [`a-e91-rerun/scored.json`](a-e91-rerun/scored.json) › `rules`, `cross_card` and `tally` (PASS 7, FAIL 4), written by
`score_e91.py` unchanged (its file headers still say "E91": that is the unchanged code speaking). The cross-card pairings at
card 1's own idle slope and at 0.3803 on both read NOT SCORED because E86's 0.3803 arm keeps two passes.

**1. On a second card, Q130(n)'s nine GPT-2 tiles cost the same share of random data as on aifoundry3, now on a registered
reading.** Over each format's all-zeros level (D) the three-tile means are **fp32 0.9905 ± 0.0032, fp16 0.9818 ± 0.0039 and
int8 0.8265 ± 0.0206** on card 1, against E86's 0.9878 ± 0.0103, 0.9872 ± 0.0142 and 0.8269 ± 0.0501 on aifoundry3: differences
**+0.0027 ± 0.0108, −0.0054 ± 0.0147 and −0.0005 ± 0.0542** (`a-e91-rerun/scored.json` › `replication_of_e86.rho_by_type`).
E91's three kept passes on 31 Oct read 0.9915 ± 0.0050, 0.9833 ± 0.0015 and 0.8418 ± 0.0437, the same within their noise. Over
idle (S) card 1 gives 0.9906 ± 0.0057, 0.9823 ± 0.0036 and 0.8687 ± 0.0092; of the whole board 0.9959 ± 0.0012, 0.9929 ± 0.0009
and 0.9722 ± 0.0023 ([`readme-numbers.txt`](readme-numbers.txt) § A1). So the int8 tiles save 9.5–23% of the power above int8's
zeros, 8–17% of the power above idle and 1.6–3.6% of the whole board; the fp16 tiles 0.7–3.5% over the zeros level, and the fp32
tiles 0.7–1.7% (`l6_mlp_down`, `l6_attn_qk`). fp32 `l0_mlp_up`'s 0.45% is not resolved: 0.9955 ± 0.0047 reaches 1.0002, and R3
reads it INCONCLUSIVE per tile ([`corrections-check.txt`](corrections-check.txt) C7). Card 1 idles at 33.0 W against
aifoundry3's 25.9 W, which pulls its whole-board shares toward 1, so that column does not compare the cards.

| tile | D (W) | ±95% | E91 point | in | D ÷ random | S ÷ random | whole board ÷ random | E86 D ÷ random (aifoundry3) | card 1 − aifoundry3 |
|---|---|---|---|---|---|---|---|---|---|
| fp32 `l0_mlp_up` | 23.379 | 0.097 | 23.749 | yes | 0.9955 ± 0.0047 | 0.9962 ± 0.0068 | 0.9982 ± 0.0015 | 0.9863 | +0.0092 ± 0.0314 |
| fp32 `l6_mlp_down` | 23.326 | 0.108 | 23.663 | yes | 0.9933 ± 0.0046 | 0.9928 ± 0.0078 | 0.9969 ± 0.0016 | 0.9937 | −0.0005 ± 0.0048 |
| fp32 `l6_attn_qk` | 23.077 | 0.062 | 23.748 | yes | 0.9827 ± 0.0028 | 0.9826 ± 0.0055 | 0.9928 ± 0.0014 | 0.9833 | −0.0006 ± 0.0036 |
| fp16 `l0_mlp_up` | 20.726 | 0.069 | 21.016 | yes | 0.9871 ± 0.0044 | 0.9865 ± 0.0025 | 0.9951 ± 0.0016 | 0.9950 | −0.0079 ± 0.0168 |
| fp16 `l6_mlp_down` | 20.851 | 0.056 | 20.670 | yes | 0.9930 ± 0.0037 | 0.9929 ± 0.0069 | 0.9971 ± 0.0007 | 0.9957 | −0.0027 ± 0.0179 |
| fp16 `l6_attn_qk` | 20.270 | 0.060 | 20.844 | yes | 0.9654 ± 0.0040 | 0.9674 ± 0.0051 | 0.9866 ± 0.0013 | 0.9710 | −0.0057 ± 0.0127 |
| int8 `l0_mlp_up` | 6.009 | 0.080 | 5.735 | yes | 0.9047 ± 0.0202 | 0.9228 ± 0.0096 | 0.9845 ± 0.0030 | 0.8879 | +0.0167 ± 0.1041 |
| int8 `l6_mlp_down` | 5.325 | 0.229 | 5.046 | yes | 0.8016 ± 0.0328 | 0.8520 ± 0.0263 | 0.9680 ± 0.0037 | 0.8109 | −0.0093 ± 0.0549 |
| int8 `l6_attn_qk` | 5.137 | 0.180 | 5.598 | yes | 0.7732 ± 0.0237 | 0.8313 ± 0.0216 | 0.9642 ± 0.0033 | 0.7820 | −0.0088 ± 0.0607 |

Sources: D, the E91 point and the last two columns from [`a-e91-rerun/results.md`](a-e91-rerun/results.md) (the nine real
tiles' table); S and whole board from `readme-numbers.txt` § A1. Energy per operation over idle (S ÷ the MAC rate), ± 95%,
in the table's tile order: fp32 5.488 ± 0.039, 5.468 ± 0.021 and 5.413 ± 0.031 pJ/MAC; fp16 2.454 ± 0.007, 2.470 ± 0.011 and
2.407 ± 0.012; int8 0.264 ± 0.003, 0.244 ± 0.007 and 0.238 ± 0.006 (`a-e91-rerun/scored.json` › `tiles.*.pj_mac_S`). The 2 s
die rise, read by the firmware in whole degrees (1 °C resolution): fp32 2.86 ± 0.49, 2.77 ± 0.34 and 2.72 ± 0.37 °C; fp16
2.33 ± 0.37, 2.30 ± 0.46 and 2.50 ± 0.48 °C; int8 0.53 ± 0.63, 1.00 and 0.98 ± 0.06 °C. int8 `l6_mlp_down` read 1 °C in all
five passes, so its interval has no width at that resolution (`tiles.*.dT_win`; per pass in
[`corrections-check.txt`](corrections-check.txt) C6).

**2. The card scale on the real tiles is the six synthetic kinds' again, and about half of the gap between the cards comes
from the leakage slope.**
The scale is D(aifoundry3, E86) / D(card 1): switching power over each format's zeros, not absolute watts. In absolute watts
card 1's board draws more, since it idles at 33.0 W against aifoundry3's 25.9 W. At the registered pairing, card 1's `auto`
slope (0.414 W/°C) against E86's (0.229), X4's median over the nine real tiles is 1.0542: card 1 reads them 5.1% lower, 4.0–7.4%
per tile (ratios 1.0416–1.0794). The six synthetic kinds run beside them (fp32 and fp16 `randn` and `nn_like`, int8 `full` and
`gauss_q`) give 1.0514, and the two medians stay within 0.003 at every resolved pairing (+0.0028, +0.0012, −0.0016, and +0.0011
with the dips removed on both cards). X3's 1.0520 is not that comparison, since nine of its 15 kinds are the real tiles. At one
slope on both cards the gap is about half as large: 1.028 at 0.1994 W/°C and 1.023 with no correction (card 1 2.7% and 2.3%
lower, against 5.1%). That is close to E82's 1.031 over its 32 synthetic kinds, measured at nearly one slope (its own 0.241
against E78's 0.1994) ([`corrections-check.txt`](corrections-check.txt) C1, C2; `a-e91-rerun/scored.json` › `cross_card.primary`,
`.pairs`).
This session's `auto` slope is **0.414 W/°C** (97 runs; E91's was 0.422 on 31 Oct, E86's 0.229 on aifoundry3;
`readme-numbers.txt` § A1): with card 1's dips removed the estimator has now returned about 0.42 in two sessions, and a steeper
slope subtracts more for each run's window warming. That is also why R5 fails: at `auto` `fp32.randn` reads 0.502 W below E82's
cell, and at 0.1994 W/°C R5 passes (`rules.E91-R5.at_arms`). D is linear in the slope: the line through the 0.1994 and 0.3803
arms gives the `auto` and 0.545 reductions to 0.000 W. So read at E82's 0.2414 W/°C, every R5 cell would lie inside its band
(`fp32.randn` +0.02 W, `int8.gauss_q` −0.11 W) and R5 would pass; the registered R5, at `auto`, stays FAIL
(`corrections-check.txt` C5). A ratio inside one pass is nearly unaffected: at 0.1994 W/°C the three-tile means are 0.9905 ±
0.0062, 0.9817 ± 0.0061 and 0.8352 ± 0.0194 (`readme-numbers.txt` § A1, the arms' own reductions), and R3 passes there too.

**3. (b), registered: NOT SCORED.** Pass 11252 departs from its `fp32.zeros` straight line by −0.253 W against E78's 0.25 W
limit, and the departure is the same at `auto` (0.417), 0.1994 and 0.3803 W/°C. The dips-kept arm keeps no pass (`fp16.randn`
spans 1.283 and 1.611 W in 11250 and 11251, against the 1.0 W random-range gate), and the 0.545 and 0 arms keep one each
(`readme-numbers.txt` § B3). The registered spare b:11253 was skipped by the budget rule at 13:49:02 (claim + 3,309 s, projected
502 s, end claim + 3,811 s > claim + 3,480 s), after (a)'s spare a:11214 ran, the list's order. So every frozen claim (C1–C12),
every arm and X1, X4, X5 read NOT SCORED ([`b-e95-card1/scored.json`](b-e95-card1/scored.json) › `tally`, `tally_cross_card`).
**By its registered rules E112 (b) replicates nothing.** No launch-rule skip and no run-gate failure occurred: 159 of 159 runs
passed the run gates, and 106 sit in the two kept passes.

**4. What (b)'s data show, reported and never a verdict.** On the two kept passes of the registered reduction, every one of the
33 tiles' ratio to random sits within **0.009 (fp32), 0.006 (fp16) and 0.016 (int8)** of its ratio on aifoundry3 (E95's
dips-removed arm; median differences 0.002, 0.003 and 0.009), and the median D(aifoundry3)/D(card 1) over the 24 tiles above
5 W is 1.045 (`readme-numbers.txt` § B1, B2). Those are point differences on two passes, and two passes' own intervals are far
wider: card 1's per-tile 95% half-widths have medians of ±0.025, ±0.038 and ±0.122 and reach ±0.105, ±0.098 and ±0.222 (t = 12.7
at two passes), wider than X5's registered bands of 0.03, 0.03 and 0.06 ([`corrections-check.txt`](corrections-check.txt) C3).
So they do not bound how far the cards differ, and they stay out of the blog and the kinds page until a scored session
replicates E95's pass. A **post-hoc view**, written after the data, raises that one gate limit from
0.25 to 0.26 W and changes nothing else ([`tools/claims-v3/e112/posthoc_gate_e112b.py`](../../../../tools/claims-v3/e112/posthoc_gate_e112b.py),
output in [`b-e95-card1/posthoc-gate026/`](b-e95-card1/posthoc-gate026/)). With pass 11252 back, E95's claims would read 10 PASS,
1 FAIL (C1), 2 INCONCLUSIVE (C7, C8), and X1, X4 and X5 would PASS (ρ 0.993 / 0.973 / 0.967; median 1.0432; 33 of 33 tiles within
the band, the largest gap 0.010 in fp32, 0.006 in fp16, 0.023 in int8). Those verdicts are not results. They say how the third
pass would read if a 0.003 W excess on one zeros line were ignored. Against E95 on aifoundry3 (9 PASS, 1 FAIL, 2 INCONCLUSIVE,
1 UNDER-RESOLVED), the post-hoc view moves four claims:
- C2 reads PASS. E95's fp32 cell was widened by a dip-hit run, and E95's own dips-removed arm reads PASS.
- C5 reads PASS. VGG's int8 tile sits at the midpoint of (a) and (c) on both cards: 3.640 W against the view's 2.634 and
  4.694 W, nearer (a) by 0.05 W; aifoundry3's 3.912 W was nearer (c).
- C7 reads INCONCLUSIVE, against UNDER-RESOLVED.
- C8 reads INCONCLUSIVE, at +0.738 ± 0.451 W against the view's 0.487 W. E95 read +0.820 ± 0.119 W.

C1 FAILS on the same cell as on aifoundry3: GPT-2's fp16 attention tile reads 0.9554 ± 0.0115 of random
(`posthoc-gate026/scored-posthoc-gate026.json` › `claims`).

| tile (post-hoc three-pass view) | D card 1 (W) | D ÷ random, card 1 | D ÷ random, aifoundry3 (E95, dips removed) | difference |
|---|---|---|---|---|
| fp32 GPT-2 layer 9, queries × keys | 22.968 ± 0.246 | 0.9799 ± 0.0090 | 0.9799 ± 0.0030 | 0.0000 |
| fp32 ViT layer 11 (64% −0.0) | 19.486 ± 0.443 | 0.8314 ± 0.0174 | 0.8259 ± 0.0042 | +0.0055 |
| fp32 T5 bf16-grid weights | 20.742 ± 0.228 | 0.8849 ± 0.0127 | 0.8857 ± 0.0066 | −0.0008 |
| fp32 ResNet-18 layer3.0.conv1 (ReLU) | 13.477 ± 0.085 | 0.5750 ± 0.0050 | 0.5750 ± 0.0027 | −0.0000 |
| fp32 VGG-16 fc2 (ReLU) | 7.552 ± 0.396 | 0.3222 ± 0.0185 | 0.3222 ± 0.0024 | −0.0000 |
| fp16 GPT-2 layer 9, queries × keys | 20.073 ± 0.162 | 0.9554 ± 0.0115 | 0.9562 ± 0.0060 | −0.0008 |
| fp16 VGG-16 fc2 (ReLU) | 9.812 ± 0.495 | 0.4670 ± 0.0247 | 0.4614 ± 0.0073 | +0.0057 |
| int8 GPT-2 layer 11, max-abs | 2.297 ± 0.229 | 0.3414 ± 0.0351 | 0.3356 ± 0.0210 | +0.0057 |
| int8 GPT-2 layer 11, p99.9 clip | 5.350 ± 0.490 | 0.7949 ± 0.0686 | 0.7764 ± 0.0181 | +0.0185 |
| int8 T5 block 0 (ReLU) | 2.200 ± 0.487 | 0.3267 ± 0.0666 | 0.3034 ± 0.0136 | +0.0233 |

All 33 rows are in `posthoc-gate026/results-posthoc-gate026.md` (the cross-card table) and the registered two-pass rows in
`b-e95-card1/results.md`. In the same session, E86's three tiles in (b) read 0.000, +0.162 and −0.052 W from (a)'s readings of
the same tiles (`fp16.real_l6_mlp_down`, `int8.real_l6_mlp_down`, `fp16.real_l6_attn_qk`) on the registered reduction's two kept
passes (NOT SCORED with two; `b-e95-card1/scored.json` › `same_session_tie_reported`), and +0.048, +0.170 and +0.025 W in the
post-hoc three-pass view: all inside the reported ±0.50 W (`corrections-check.txt` C7).

**5. Checks (reported).** (a): idle consistency median |S − S0 − D| 0.068 W (≤ 0.15); rail lag re-fit 1.00 s (in [0.80, 1.15]);
duty 0.9958–0.9964; carry-over 0.0029 W/W, standard error 0.0007 (one SE, not a 95% interval; n 155; ≤ 0.01); 160 of 160 runs
kept; cycles per op 546 / 546 / 318 at 600 MHz; dips removed 10, 9, 14, 5, 13 per pass (`a-e91-rerun/scored.json` › `checks`,
`dip_samples_removed`). (b): 0.074 W; 0.975 s; 0.9955–0.9967; carry-over 0.0038 W/W, SE 0.0008 (n 104); dips removed 26, 30,
27 (`b-e95-card1/scored.json` › `checks`; `e112b.json` › `reducer.dip_samples_removed`). The smoke (11201): 7 of 7 runs ok, cycles per op 546 / 546 / 318, 599.2–599.5
MHz ([`logs/smoke.txt`](logs/smoke.txt)).

## Registered against what happened

| | registered (E112.md) | what happened |
|---|---|---|
| pre-registration | committed and pushed before the claim | `0623b052`, 12:51:58 / pushed 12:52:02; claim 12:53:53.736 |
| setup | `run_e112.sh setup`, no device access | 12:50:19 (on the same files before the commit) and 12:52:13 (after): every hash identical to the freeze; dry passes 11200 (34 launches, 9 on real tiles) and 11240 (55, 30 on real2 tiles), `ET_DEVICES=1`; the queue's stub test started seven stub passes and skipped two ([`logs/box-setup.txt`](logs/box-setup.txt), [`logs/dry-p11200/`](logs/dry-p11200/), [`logs/dry-p11240/`](logs/dry-p11240/)) |
| before the claim | `#community-lab` and `et-who` | 12:53: every claim released (the last, E108's on card 1, at 12:12); "No process holds an ET-SoC-1 device node or card lock" |
| smoke | 11201, E86's seven 2 s runs | 12:54:09–12:54:53, 7 of 7 ok; config 65 / 65 / 600 MHz / 499 mV at both ends |
| queue | a:11210–11213, b:11250–11252, then a:11214, b:11253 if they fit | a: 328, 320, 321, 334 s; b: 502, 491, 501 s; **a:11214 ran** (started claim + 2,980 s, projected end + 3,314 s, ran 314 s); **b:11253 skipped** (projected end + 3,811 s > + 3,480 s) ([`logs/e112-queue.log`](logs/e112-queue.log)) |
| session-end read | after the last pass, under the lock | 13:49:02, et-who clean, 65 / 65 / 600 / 499 ([`logs/config-session-end.json`](logs/config-session-end.json)) |
| kept passes | (a) ≥ 4; (b) ≥ 3 | (a) **5** (none set aside at the primary); (b) **2** (11252 set aside by the zeros-line gate) |
| verdicts | (a) R1–R5, S1, X1–X4; (b) C1–C12, X1, X4, X5 | (a) 7 PASS, 4 FAIL; (b) all NOT SCORED |
| budget | ≤ 60 card-minutes, claim to release | 55.5 |

## Departures

- **None from the registered procedure.** Every pass ran in the registered order under the registered rule; no pass was
  started, stopped or chosen by hand; nothing was reduced or looked at before the session ended.
- **Beyond the registration, labelled:** the post-hoc view of (b) (`posthoc_gate_e112b.py`, written at about 13:55 PST, after
  the release and after the registered reduction had set 11252 aside); `readme-numbers.py` (derived numbers, every one printed
  into `readme-numbers.txt`).
- **One log was edited for the public repo:** `a-e91-rerun/collect.log`, the output of `collect_e91.sh`, named its output
  directory by the Intel's absolute path; the prefix was cut to the repo-relative path. No number changed. The reductions record
  repo-relative pass directories; the raw passes and the queue log keep the box's own paths, as every raw directory here does.
- `code.sha256` was written by `collect_e112.sh` before the post-hoc script existed, so it does not list it.

## What it changes for the blog material and the hub

- **Item 7, "another card":** answered for Q130(n)'s nine GPT-2 tiles on a registered reading (7 of E91's 11 rules pass; R5's
  tie to E82's watts fails at the session's own leakage slope and passes at 0.1994; X2a / X2b / X3 fail as registered). On
  card 1 they cost 0.98–0.996 (fp32), 0.965–0.993 (fp16) and 0.77–0.90 (int8) of random data over each format's zeros. Their
  three-tile means differ from aifoundry3's by +0.3 ± 1.1, −0.5 ± 1.5 and −0.0 ± 5.4 points (95%). It is **not answered** for
  E95's thirty tiles, which are run and described but not scored. Their ratios to random lie within 0.009–0.016 of
  aifoundry3's on two passes whose own 95% intervals are about ±0.025–0.12 (medians), so that is no replication either; it
  stays out of the blog and section 11 until a scored session replicates E95's pass.
- **The final critic's replicates:** "E91 not re-run" is done, and E91's registration scores (7 PASS, 4 FAIL; the three
  one-scale rules fail as registered).
- **For the instrument record:** card 1's leakage estimator with the dips removed returned 0.414 and 0.417 W/°C in this
  session's two halves, after E91's 0.422. That moves absolute D by about 0.5 W in fp32, makes about half of the gap between
  the cards (result 2) and decides R5. Ratios inside a pass are not affected. These numbers extend the bullet Q132 added to
  [`14-card-behaviour.md`](../../../findings/14-card-behaviour.md) that morning ("A session's automatic leakage slope wanders,
  so register one", `578e09d9`, 08:56 PST); they belong in it, not in a new line. E112's registration (12:51) did not cite that
  bullet. (a) re-ran E91's registration unchanged, and its primary is `auto`; (b) chose `auto` to pair like with like with
  E95's dips-removed arm; no arm froze E82's 0.2414. The registered verdicts stand. Read at 0.2414, R5 would pass, as at
  0.1994 and 0.3803 on either side (result 2), and (b) would keep the same two passes and stay NOT SCORED: its third pass is set
  aside by the same −0.253 W at 0.1994, 0.3803 and `auto` (`corrections-check.txt` C5). The zeros-line gate's margin is thin:
  it set aside 11252 by 0.003 W, as it set aside E91's first pass by 0.038 W.
- **For the runbooks:** the exact-seconds budget anchored on the claim did its job: (a)'s spare started with its projected end
  166 s inside the limit. (b)'s spare could not have run in its place: at claim + 2,980 s its projected end was claim + 3,482 s,
  2 s past the limit (`readme-numbers.txt` § B4). A second-card replicate of E95's 53-run pass needs a session of its own, about
  40 card-minutes for four passes at this card's 491–502 s a pass.

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier checked E112 after the data commit (`a5e587bd`). It re-ran `collect_e112.sh` on the committed raw
passes: both `scored.json` files and both `results.md` files came back byte-identical, and 55 of 56 outputs matched after path
normalisation (only `du`'s size line in `collect.log` differs). It re-derived the headline numbers from `e91.json`'s per-pass data
without the scorer. It found these sound: the registration before the claim, the frozen inputs (all 47 harness hashes), the gates
at every arm, the queue's budget arithmetic and the card conduct (nothing set, no `--reset-ms`, the lock and timeouts held, one
session on aifoundry1, the claim and its release). Verdict: holds with fixes. It found one major and six minor faults in how E112
was stated and handed on. Each is corrected above, desk only: no card was touched, nothing was re-run, and no registered
prediction, rule, reduction, measured number or verdict changed ((a) 7 PASS, 4 FAIL; (b) NOT SCORED). One summary range was
restated: result 1's fp32 saving now leaves out the unresolved tile (C7). Every new number is printed by
[`corrections-check.py`](corrections-check.py) into [`corrections-check.txt`](corrections-check.txt) (standard library, post hoc,
deciding nothing), under the section named.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **Major: the blog point handed on said the second card reads "every real tile about 5% lower in absolute watts (median ratio 1.054)".** The ratio is of D, power over each format's zeros, not absolute watts; in absolute watts card 1 draws more (idle 33.0 W against 25.9 W). It is 4.0–7.4% per tile (ratios 1.0416–1.0794), not about 5% for every tile. About half of the gap comes from the leakage estimator: the registered pairing sets card 1's `auto` slope, 0.414 W/°C, against aifoundry3's 0.229 | Result 2 says what the scale is and gives it at one slope on both cards: 1.028 at 0.1994 W/°C and 1.023 uncorrected (card 1 2.7% and 2.3% lower), close to E82's 1.031 on synthetic kinds; 1.054 (5.1% lower, 4.0–7.4% per tile) with each session's own slope. The blog point handed on is rewritten the same way, and the card-scale table cell carries 1.028 and 1.023 beside 1.0542 (C1) |
| C2 | **Result 2 compared the real tiles with X3's 15-kind median, 1.0520, which contains them** (nine of the 15), the point E91's verifier made of E91 (its C5). It also did not say how much the slope moves the scale | Result 2 compares them with the six synthetic kinds run beside them: 1.0514 at the registered pairing, within 0.003 of the real tiles' median at every resolved pairing (+0.0028, +0.0012, −0.0016, +0.0011). It gives the common-slope X4 values (C2) |
| C3 | **(b)'s two-pass agreement, "within 0.009 / 0.006 / 0.016", was quoted without the two passes' uncertainty**, in result 4, in What it changes, and in the blog point, kinds-page line and table cells handed on | Result 4 and What it changes give card 1's per-tile 95% half-widths at two passes (medians ±0.025, ±0.038, ±0.122; up to ±0.105, ±0.098, ±0.222; t = 12.7), wider than X5's bands. They keep the figure out of the blog and section 11 until a scored session replicates E95's pass; the handed-on blog point and kinds-page line drop it (C3) |
| C4 | **The handed-on kinds-page line said "within +0.3 ± 1.1, −0.5 ± 1.5 and −0.0 ± 5.4 points"**, which reads as a bound where these are differences with 95% intervals; and "registered" with no tally reads as if every registered rule passed | The line says "differ from aifoundry3's by … (95%)" and carries the tally: 7 of E91's 11 rules pass, R5's tie to E82's watts fails at the session's own slope and passes at 0.1994, and X2a / X2b / X3 fail as registered. What it changes carries the same (C4) |
| C5 | **Q132's lesson on the slope was not engaged.** `14-card-behaviour.md`'s bullet "A session's automatic leakage slope wanders, so register one" (`578e09d9`, 08:56 PST, four hours before E112's registration) was not cited; (b) registered `auto` without it, and no arm froze E82's 0.2414. The records note handed on proposed a new line rather than extending that bullet | What it changes cites the bullet and asks the records to extend it with 0.414 and 0.417 W/°C. No verdict moves: D is linear in the slope (the line through the 0.1994 and 0.3803 arms gives the `auto` and 0.545 reductions to 0.000 W), so read at 0.2414 R5 would pass and (b) would keep the same two passes and stay NOT SCORED. The registered verdicts, at `auto`, stand (C5) |
| C6 | **The handed-on table cells gave pJ/MAC with no interval and the die rise with only a phrase**, though `scored.json` holds both | The paragraph under the tile table gives each tile's pJ/MAC and die rise with its 95% interval. It says int8 `l6_mlp_down` read 1 °C in all five passes, so its interval has no width at the reading's 1 °C resolution; the table cells handed on carry the same (C6) |
| C7 | **Four labels.** The carry-over figures (0.0029 ± 0.0007 and 0.0038 ± 0.0008 W/W) are standard errors, though the header calls the intervals 95%. X1's fp32 ρ of 0.900 sits exactly on its threshold (five kinds, one adjacent swap), unremarked. "fp32 tiles 0.4–1.7%" included `l0_mlp_up`, whose 0.9955 ± 0.0047 is not resolved below 1. The same-session tie was quoted only from the post-hoc view | Check 5 labels the SEs. The rule table notes X1's fp32 edge. Result 1 says fp32 0.7–1.7% and marks `l0_mlp_up`'s 0.45% unresolved (R3 per tile INCONCLUSIVE). Result 4 quotes the registered two-pass tie first (0.000, +0.162, −0.052 W, NOT SCORED with two passes) and the post-hoc one beside it (C7) |

## Files

| path | what |
|---|---|
| `a-e91-rerun/` | (a): `collect_e91.sh`'s output on passes 11210–11214, unchanged code: `e91.json` (primary: dips removed, leakage auto), `e91-dipskept.json`, `e91-leak{0.1994,0.545,0.3803,0}.json` (+ csv, txt, log), `scored.json`, `results.md`, `score.log`, `collect.log`, `code.sha256` |
| `b-e95-card1/` | (b): `e112b.json` (primary), `e112b-dipskept.json`, `e112b-leak{0.1994,0.545,0.3803,0}.json` (+ csv, txt, log), `scored.json`, `results.md` (`reduce_e112b.py`, `score_e112b.py`) |
| `b-e95-card1/posthoc-gate026/` | the post-hoc view (labelled; never a verdict) |
| `aifoundry1-c1/kinds/p11210`–`p11214`, `p11250`–`p11252`, `kinds-smoke-p11201` | raw passes as the box wrote them: 10 Hz telemetry, launch records, marks, dumped tiles, config reads, manifests |
| `logs/` | the queue log, the box's setup, the smoke, the session's config reads, the two dry passes, push and claim times |
| `readme-numbers.py`, `readme-numbers.txt` | every derived number above that `results.md` does not print (standard library only) |
| `corrections-check.py`, `corrections-check.txt` | added with the corrections after verification: every number they quote, from committed files (standard library, post hoc, deciding nothing) |
| `code.sha256` | the code and frozen files as reduced |

Reproduce on the Intel: copy `aifoundry1:nekko/build/claims-v3/aifoundry1-c1/{kinds,kinds-smoke}/p112*` to
`build/e112-raw/{kinds,kinds-smoke}/`, then `PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e112/collect_e112.sh
build/e112-raw` (about 20 s), and for the post-hoc view `E112A=<out>/a-e91-rerun/e91.json python3
tools/claims-v3/e112/posthoc_gate_e112b.py <out>/b-e95-card1/posthoc-gate026 build/e112-raw/kinds/p1125{0,1,2}`; the
corrections' numbers, `python3 docs/reports/data/2026-11-01-e112-real-replicates/corrections-check.py`.
