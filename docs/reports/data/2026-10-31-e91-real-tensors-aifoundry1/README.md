# E91: the real tensors' energy replicated on aifoundry1 card 1 (GPT-2 small's numbers, 600 MHz)

*Sat 31 Oct 2026 (week 44), Q130's evening round. Pre-registered in `eb72ce5d` (committed 21:09:09, pushed 21:09:11
PDT by GitHub's record, before the claim and the first launch):
[`tools/claims-v3/kinds/E91.md`](../../../../tools/claims-v3/kinds/E91.md), frozen numbers in `predictions-e91.json`
(sha256 `56efe2e7…`). Amendment A1 in `7f007f53` (pushed 21:30:24 PDT, during pass 9113, before any reduction).
aifoundry1 card 1 (`V3_DEVICE=1`, its own lock) at 600 MHz, 498.6 mV mean, TDP 65 W / threshold 65 °C read at both ends
of every block (21:10:19–21:35:07), never set. Nothing was written to the card, and no `--reset-ms` was sent. Claim
1566303302210158713 in #community-lab, posted 21:10:07 PDT, released 21:36 PDT by editing it (held 26.1 min; device
access 24.8 min, 21:10:19–21:35:07; budget 35 card-minutes;
[`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)).*

*Corrected after verification, Sat 31 Oct 2026, at the desk, with no card touched and nothing re-run (§ [Corrections
after verification](#corrections-after-verification-sat-31-oct-2026), C1–C10). Every ratio now names its baseline:
over the type's all-zeros level (D), over idle (S) or of the whole board (p80), for every format (result 1). The A1
account now says the floor that refused pass 9114 was the lane's own choice, and that A1's exact budget held the pass
until 21:36:06.8. The arms are named as sensitivity analyses, and the real tiles' card scale is compared with the six
synthetic kinds rather than with a median that contains them. The path sentence, the dry pass's evidence and one push
time are fixed. No number in `e91*.json`, `runs*.csv`, `scored*.json`, `results*.md` or `reduce*` changed, no frozen
input changed, and every registered verdict stays NOT SCORED.*

## The registered outcome: every rule NOT SCORED

**Four passes ran (9110–9113). E78's zeros-line pass gate set pass 9110 aside in the registered primary reduction:
`int8.zeros` departs −0.288 W from its straight line, against a 0.25 W limit. That leaves three kept passes, below the
registered minimum of four, so all eleven registered verdicts (R1–R5, S1, X1–X4) are NOT SCORED** (`scored.json` ›
`tally`). The fifth pass that amendment A1 added for exactly this risk did not run. The first queue's budget rule
stopped before `p9114` by 11 s (elapsed 1,450 s + the longest pass, 361 s, against 1,800 s). A1's second queue then
refused it by 1 s. A1's budget, 35 − 25.25 − 3 = 6.75 card-minutes (405 s), was floored to 6 whole minutes (360 s)
against the 361 s pass. A1 gives no rounding. The floor was the lane's own choice, written into its helper at 21:30:54,
30 s after A1 was pushed ([`logs/a1-second-queue.sh`](logs/a1-second-queue.sh)), because `queue_e86.sh` counts whole
minutes. On A1's exact arithmetic the pass would have run. It was not started by hand afterwards (§ Departures).

So **by its registered rules E91 replicates nothing.** Everything below comes from the three kept passes or from the
registered arms. It is reported, labelled, and no verdict rests on it. Two registered arms keep all four passes, and
their verdicts differ:
- at 0.1994 W/°C (Q130(n)'s D scope), R1–R5, S1, X1 and X4 pass and X2a / X2b / X3 fail;
- at leakage 0, R4 is INCONCLUSIVE and R5 fails, while R1–R3, S1, X1 and X4 pass and X2a / X2b / X3 fail.

The arms are sensitivity analyses, not a fallback primary ([`corrections-check.txt`](corrections-check.txt) C4).

## What the three kept passes and the arms show (reported, not scored)

**1. Over each format's all-zeros level (D), the real tiles cost on card 1 about what they cost on aifoundry3,
relative to random data in the same pass (int8 only within its noise): fp32 98.5–99.7% of random, fp16 96.6–99.3% and
int8 81–89% (aifoundry3 98.3–99.4%, 97.1–99.6% and 78–89%). Over idle (S) card 1 gives 98.9–99.4%, 96.7–99.0% and
86–91%; of the whole board's power (p80) it gives 99.4–99.8%, 98.7–99.7% and 96.9–98.3%.** D (board
power over the type's own zeros), the primary reduction (dips removed, leakage `auto`), passes 9111–9113; beside it
the registered 0.1994 W/°C arm (Q130(n)'s D scope), where the gate keeps all four passes. ± is 95% over passes
(t(0.975, n−1) × SE). Sources: `scored.json` › `tiles`, `scored-leak0.1994.json` › `tiles` (a re-scoring of the
`e91-leak0.1994.json` arm, reported only), and E86's `scored.json` › `tiles` for aifoundry3:

| tile | D (W), 3 passes | ±95% | D ÷ random, 3 passes | ±95% | D ÷ random, 0.1994 arm, 4 passes | ±95% | E86 (aifoundry3), 4 passes | card 1 − aifoundry3 (3 passes) | E91 interval (W) |
|---|---|---|---|---|---|---|---|---|---|
| fp32 `l0_mlp_up` | 23.318 | 0.223 | 0.9969 | 0.0025 | 0.9946 | 0.0040 | 0.9863 ± 0.0310 | +0.0106 ± 0.0311 | [21.406, 26.092] |
| fp32 `l6_mlp_down` | 23.209 | 0.106 | 0.9922 | 0.0043 | 0.9912 | 0.0031 | 0.9937 ± 0.0012 | −0.0015 ± 0.0045 | [21.32, 26.005] |
| fp32 `l6_attn_qk` | 23.046 | 0.212 | 0.9853 | 0.0101 | 0.9855 | 0.0074 | 0.9833 ± 0.0023 | +0.0020 ± 0.0104 | [21.405, 26.091] |
| fp16 `l0_mlp_up` | 20.823 | 0.113 | 0.9911 | 0.0033 | 0.9868 | 0.0085 | 0.9950 ± 0.0162 | −0.0039 ± 0.0165 | [18.739, 23.292] |
| fp16 `l6_mlp_down` | 20.865 | 0.088 | 0.9931 | 0.0040 | 0.9911 | 0.0081 | 0.9957 ± 0.0175 | −0.0027 ± 0.0179 | [18.394, 22.946] |
| fp16 `l6_attn_qk` | 20.291 | 0.362 | 0.9657 | 0.0115 | 0.9655 | 0.0057 | 0.9710 ± 0.0120 | −0.0053 ± 0.0166 | [18.568, 23.121] |
| int8 `l0_mlp_up` | 5.986 | 0.352 | 0.8935 | 0.0691 | 0.8922 | 0.0208 | 0.8879 ± 0.1022 | +0.0055 ± 0.1234 | [4.451, 7.019] |
| int8 `l6_mlp_down` | 5.522 | 0.393 | 0.8241 | 0.0390 | 0.8121 | 0.0072 | 0.8109 ± 0.0441 | +0.0132 ± 0.0588 | [3.762, 6.331] |
| int8 `l6_attn_qk` | 5.413 | 0.208 | 0.8078 | 0.0407 | 0.8042 | 0.0160 | 0.7820 ± 0.0558 | +0.0258 ± 0.0691 | [4.313, 6.882] |

Averaged over a format's three tiles (R3's ρ), card 1 gives fp32 **0.9915 ± 0.0050**, fp16 **0.9833 ± 0.0015** and
int8 **0.8418 ± 0.0437** (3 passes). The 0.1994 arm gives 0.9904 ± 0.0031, 0.9811 ± 0.0057 and 0.8362 ± 0.0051 (4
passes). aifoundry3 (E86) gave 0.9878 ± 0.0103, 0.9872 ± 0.0142 and 0.8269 ± 0.0501, and the differences are
**+0.0037 ± 0.0115, −0.0040 ± 0.0142 and +0.0148 ± 0.0665** (`scored.json` › `replication_of_e86.rho_by_type`;
intervals added in quadrature). Every tile's paired D(real) − D(random) lies below zero at 95% in all three formats
(`order_vs_ref`). In fp16 the three-tile mean sits clearly below 1 on card 1, where E86's registered reduction could not
separate it from 1 (its upper bound was 1.0014). E86's post-hoc dips-removed view gave 0.9832 ± 0.0039.

The same ratios against the three baselines on card 1, paired per pass in the same way (3 passes;
[`corrections-check.txt`](corrections-check.txt) C1). S is board power over idle, and p80 the window's whole board power
(idle plus S, leakage-corrected):

| tile | D ÷ random (over the type's zeros) | S ÷ random (over idle) | p80 ÷ random (whole board) |
|---|---|---|---|
| fp32 `l0_mlp_up` | 0.9969 ± 0.0025 | 0.9942 ± 0.0100 | 0.9983 ± 0.0005 |
| fp32 `l6_mlp_down` | 0.9922 ± 0.0043 | 0.9886 ± 0.0164 | 0.9970 ± 0.0018 |
| fp32 `l6_attn_qk` | 0.9853 ± 0.0101 | 0.9925 ± 0.0148 | 0.9939 ± 0.0039 |
| fp16 `l0_mlp_up` | 0.9911 ± 0.0033 | 0.9860 ± 0.0105 | 0.9965 ± 0.0014 |
| fp16 `l6_mlp_down` | 0.9931 ± 0.0040 | 0.9900 ± 0.0277 | 0.9970 ± 0.0025 |
| fp16 `l6_attn_qk` | 0.9657 ± 0.0115 | 0.9666 ± 0.0057 | 0.9868 ± 0.0034 |
| int8 `l0_mlp_up` | 0.8935 ± 0.0691 | 0.9123 ± 0.0442 | 0.9829 ± 0.0087 |
| int8 `l6_mlp_down` | 0.8241 ± 0.0390 | 0.8649 ± 0.0280 | 0.9707 ± 0.0041 |
| int8 `l6_attn_qk` | 0.8078 ± 0.0407 | 0.8605 ± 0.0330 | 0.9688 ± 0.0027 |

Three-tile means on both cards (E86's from its `e86.json` › `per_pass`, as its
[`corrections-check.txt`](../2026-10-31-e86-real-tensors-energy/corrections-check.txt) C2 gives them; differences with
the intervals in quadrature):

| three-tile mean | D ÷ random | S ÷ random | p80 ÷ random |
|---|---|---|---|
| fp32, card 1 (3 passes) | 0.9915 ± 0.0050 | 0.9918 ± 0.0094 | 0.9964 ± 0.0019 |
| fp32, aifoundry3 (E86, 4 passes) | 0.9878 ± 0.0103 | 0.9902 ± 0.0090 | 0.9945 ± 0.0040 |
| fp32, card 1 − aifoundry3 | +0.0037 ± 0.0115 | +0.0016 ± 0.0130 | +0.0019 ± 0.0045 |
| fp16, card 1 | 0.9833 ± 0.0015 | 0.9809 ± 0.0047 | 0.9934 ± 0.0004 |
| fp16, aifoundry3 | 0.9872 ± 0.0142 | 0.9875 ± 0.0107 | 0.9942 ± 0.0057 |
| fp16, card 1 − aifoundry3 | −0.0040 ± 0.0142 | −0.0067 ± 0.0117 | −0.0008 ± 0.0057 |
| int8, card 1 | 0.8418 ± 0.0437 | 0.8793 ± 0.0012 | 0.9741 ± 0.0047 |
| int8, aifoundry3 | 0.8269 ± 0.0501 | 0.8787 ± 0.0316 | 0.9657 ± 0.0110 |
| int8, card 1 − aifoundry3 | +0.0148 ± 0.0665 | +0.0006 ± 0.0316 | +0.0085 ± 0.0120 |

So on card 1 the int8 tiles save 11–19% of the power above int8's all-zeros level, 9–14% of the power above idle and
1.7–3.1% of the whole board's (aifoundry3: 11–22%, 8–15% and 2.3–4.2%). The fp32 tiles save 0.3–1.5% over the zeros
level and 0.2–0.6% of the whole board, and the fp16 tiles 0.7–3.4% and 0.3–1.3%. Over the zeros level and over idle,
the fp32 and fp16 three-tile means agree between the cards within about 1 point, with 95% intervals of ±1.2–1.4 points.
The int8 means agree only within their noise, ±6.7 points over the zeros level and ±3.2 over idle. Card 1 idles at
33.0 W and aifoundry3 at 25.9 W, so a whole-board share sits closer to 1 on card 1 for that reason alone. The
whole-board column therefore does not compare the two cards' tiles.

**2. Every tile lies inside its E91 interval (9 of 9), and inside aifoundry3's unscaled intervals too.** Those intervals
are ±1.3–2.3 W wide, 3–26× the measurement's own ±0.09–0.39 W, so this says little (as E86 noted for R1). At the
0.1994 arm, where four passes are kept, the errors against the E91 points are rms 0.195 / 0.549 / 0.433 W (mean +0.165 /
+0.460 / +0.346 W), inside E78-R2's 2.0 / 2.0 / 1.0 W (`scored-leak0.1994.json` › `rules.E91-R2`).

**3. Against E78's synthetic network stand-ins, on card 1:** real fp32 costs 1.87–1.89× `nn_like` and real fp16
1.22–1.25× (above, as predicted). Real int8 `l6_mlp_down` and `l6_attn_qk` cost 0.87× and 0.86× `gauss_q` (below, as
predicted). Real int8 `l0_mlp_up` is −0.34 ± 0.37 W from `gauss_q` (3 passes; −0.27 ± 0.22 W at the 0.1994 arm), so
as on aifoundry3 (−0.17 ± 0.77 W) it is about where E78's quantised-Gaussian stand-in sits.

**4. The session reads lower than E82's on this card at the session's own leakage slope, not at E78's.** The
primary's `auto` slope came out at **0.422 W/°C** (101 runs of the three kept passes, dips removed; 0.277 with the dips
kept). E82 measured 0.241 on this card (313 runs), E86 0.229 and E78 0.1994. A steeper slope subtracts more for each
run's window warming (p80 = P − k·ΔT, with ΔT about 3 °C in fp32 and fp16). So at `auto` the seven tie cells read
−0.17 to −0.60 W below E82's, and fp32 `randn`'s −0.596 W is outside R5's ±0.50 W. At 0.1994 all seven lie within
−0.03 to +0.33 W of E82's (`scored.json` and `scored-leak0.1994.json` › `rules.E91-R5`). A ratio within one format is
nearly unaffected (both runs warm alike): fp32 ρ is 0.9915 at `auto` against 0.9904 at 0.1994. Why the estimator
returns 0.42 on this session is not resolved here.

**5. The card scale on the real tiles depends on the same slope.** D(aifoundry3, E86) / D(card 1, E91) has a median of
**1.054** over the 15 kinds at `auto` against E86's registered reduction, 1.023 with 0.1994 on both cards, 1.018 with
no correction on both, and 1.032 with E91's dips kept. Over the nine real tiles alone the medians are 1.054, 1.025,
1.018 and 1.032. E82 measured 1.031 over its 32 synthetic kinds, those that switch at least 5 W (`scored.json` ›
`cross_card.primary` and `.pairs`). The real tiles' median lies within 0.0025 of the median of the six synthetic kinds
run beside them at every resolved pairing. Those six are E78's random and stand-in kinds: fp32 and fp16 `randn` and
`nn_like`, int8 `full` and `gauss_q`. The gaps are +0.0003, +0.0021, +0.0015 and −0.0023, and −0.0011 with the dips
removed on both cards ([`corrections-check.txt`](corrections-check.txt) C5). So the real tiles scale between the
cards as those kinds do. The scale itself spans 1.018–1.054 with the leakage slope and the dip treatment. September's
band [0.88, 0.99] is missed at every pairing (X2a / X3 would fail, as on E82). X1's ranks are 0.90 / 1.00 / 1.00 (fp32 /
fp16 / int8): in fp32, `l0_mlp_up` and `l6_mlp_down` swap.

**6. Why pass 9110 was set aside, at each arm.** `int8.zeros` departs from its straight line by −0.288 W at `auto`
(0.422), −0.258 W with dips kept (auto 0.277), −0.279 W at 0.3803 and −0.313 W at 0.545 (all past 0.25 W: set aside),
and by less than 0.25 W at 0.1994 and at 0 (kept). At 0.545 the gate also sets 9111 aside (−0.292 W). 9110 was the
session's first pass, started with the die at 54 °C, below the launch band (`e91*.json` › `passes_set_aside`). E88's
first pass on this card was kept, and its fourth (8813) was set aside by the same gate on `fp16.zeros`.

**7. Checks, reported:** idle consistency median |S − S0 − D| 0.074 W (≤ 0.15); rail lag re-fit 0.95 s (in [0.80,
1.15]); duty 0.9956–0.9964 (in [0.990, 1.000]); carry-over −0.0006 W/W, SE 0.0008 (n 93). Every run's cycles per op was
546.0 / 546.0 / 318.0, at 600 MHz. One run was skipped by the protocol: 9110's `int8.gauss_q` (the launch reading went
back to 59 °C inside the quiet wait). The primary removed 7 / 3 / 8 / 8 dip samples from passes 9110–9113
(`scored.json` › `dip_samples_removed`).

**Energy per operation, card 1, 3 passes** (S over idle ÷ the MAC rate; `scored.json` › `tiles.*.pj_mac_S`): fp32
5.46–5.49 pJ/MAC, fp16 2.42–2.48, int8 0.251–0.266. The 2 s die rise is fp32 3.1–3.4 °C, fp16 2.9–3.0 °C and int8
1.0–1.2 °C (whole-degree reading). int8 `l6_mlp_down` and `l6_attn_qk` read exactly 1 °C in every pass; the
reading's resolution is 1 °C, so their zero spread is not a zero uncertainty ([`corrections-check.txt`](corrections-check.txt) C7).

## Registered against what happened

| | registered (E91.md) | what happened |
|---|---|---|
| pre-registration | README, frozen predictions and rules committed and pushed before the claim | `eb72ce5d` pushed 21:09:11 (GitHub's record); claim 21:10:07.755; first launch 21:10:19 |
| setup | `run_e91.sh setup`, no device access | 21:05 and 21:08: every file identical to the freeze; tiles ok. The 21:05 dry pass (21:05:34–21:05:42) planned 32 runs, 9 on real tiles, and 2 burn-ins (34 launch commands), with `ET_DEVICES=1`, and opened no device ([`logs/dry-p9100/`](logs/dry-p9100/), copied read-only from the box after verification; the committed `logs/e91-dry.log` is the 21:08 skip line) |
| smoke | pass 9101, seven 2 s runs | 21:10:19–21:11:03: 7 of 7 ok, cycles/op 546 / 546 / 318, 599.2–599.5 MHz, launch coverage 0.9975–0.9983, config 65 W / 65 °C / 600 MHz / 499 mV at both ends |
| passes | 9110–9115, at least four, by the budget rule (30 card-min of the queue) | 9110 (21:11:12, 351 s), 9111 (361 s), 9112 (331 s), 9113 (347 s, ended 21:35:07); the rule stopped before 9114 |
| A1 | pass 9114 alone if it fits in 35 − used − 3 card-minutes | refused at 21:35:22: the lane's helper floored A1's 6.75 card-minutes (405 s) to 6 min (360 s) against the 361 s pass; A1 gives no rounding (§ Departures) |
| kept passes | ≥ 4 for any verdict | **3** (9111–9113); 9110 set aside by E78's zeros-line gate |
| verdicts | R1–R5, S1, X1–X4 | **all NOT SCORED** |
| arms | dips kept; leakage 0.1994, 0.545, 0.3803, 0 | dips kept: 3 passes, NOT SCORED; 0.545: 2 passes; 0.3803: 3 passes; **0.1994: 4 passes, R1–R5, S1 PASS, X1 PASS, X2a / X2b / X3 FAIL, X4 PASS**; 0: 4 passes, R1–R3 PASS, R4 INCONCLUSIVE, R5 FAIL, S1 PASS, and with no correction on both cards X1 PASS, X2a / X2b / X3 FAIL, X4 PASS (`scored.json` › `rules.*.at_arms`; the 0.1994 X verdicts are the "0.1994 on both" pair's) |
| budget | ≤ 35 card-minutes, claim to release | 26.1 |

## Departures

- **A1 (`7f007f53`, pushed 21:30:24, during 9113, before any reduction):** one pass added inside the registered 35
  card-minutes, because the passes took about 5.8 min, not E88's 5.4. No rule, band, gate or analysis changed. Its
  outcome is the main departure from plan.
  - A1 sets the second queue's budget at 35 − used − 3 card-minutes and gives no rounding.
  - `queue_e86.sh` needs whole minutes (its rule is bash integer arithmetic, `$((BUDGET_MIN * 60))`).
  - The lane's helper chose the floor. It was written at 21:30:54, 30 s after A1 was pushed, and is committed with its
    output after verification ([`logs/a1-second-queue.sh`](logs/a1-second-queue.sh),
    [`logs/a1-second-queue.out`](logs/a1-second-queue.out)).
  - At 21:35:22 the floor gave 6 min (360 s) against the first queue's longest pass, 361 s, so the pass was refused by
    1 s. A1's exact budget was 405 s and would have run it. The floor is the lane's implementation choice, not A1's.
  - A1's exact budget kept room for the pass until 21:36:06.8: 401.8 s when the refusal was read at 21:35:26, and
    371.8 s at the closing `et-who` read at 21:35:56 ([`corrections-check.txt`](corrections-check.txt) C3).
  - The pass was not started by hand afterwards. Starting it after the registered rule had refused it would have been
    a second, unregistered decision.
- **The reductions record repo-relative pass directories.** `collect_e91.sh` ran over a gitignored copy at
  `build/claims-v3/aifoundry1-c1-e91/`, as E86's did, so no Intel path enters the reductions. The raw pass files and the
  queue logs keep the box's own paths, under his public login's home directory on aifoundry1 (1,246 lines, C6). An
  earlier run of the same code over the lane's scratch copy gave identical numbers.
- **Reported views beyond the registered list:** `scored-leak0.1994.json` / `results-leak0.1994.md` and
  `scored-leak0.json` / `results-leak0.md` are `score_e91.py` run with an arm as its input. They give each arm's tables
  in full, and their verdicts are the ones `scored.json` › `rules.*.at_arms` already reports. Their cross-card pairing is
  the arm against E86's registered reduction (median 1.021 at 0.1994), not the registered "0.1994 on both" pair (1.023,
  in `scored.json`).

## What it changes for the blog material and the hub

- **No registered result.** E91 cannot be cited as a passed replication. The hub should list it as run, with 3 of 4
  passes kept and every verdict not scored.
- **What it supports, labelled exploratory:**
  - **On a second card the three real GPT-2 small tiles per format draw about the same fraction of random data's power
    above each format's all-zeros level as on aifoundry3:** fp32 98.5–99.7%, fp16 96.6–99.3% and int8 81–89% (aifoundry3
    98.3–99.4%, 97.1–99.6% and 78–89%).
  - The fp32 and fp16 three-tile means agree within about 1 point (+0.4 ± 1.2 and −0.4 ± 1.4). int8 agrees only within
    its noise (+1.5 ± 6.7 points).
  - Over idle, int8 is 86–91% of random on card 1 (85–92% on aifoundry3). Of the whole board it is 96.9–98.3%
    (95.8–97.7%); the whole-board shares differ partly because card 1 idles at 33.0 W against 25.9 W.
  - The fp16 tiles sit clearly below random on card 1 (0.983 ± 0.002 over 3 passes), matching E86's post-hoc value,
    not its inconclusive registered one.
  - The real tiles scale between the two cards as the six synthetic kinds run beside them do (medians within 0.0025),
    at 1.018–1.054 depending on the leakage slope and the dip treatment.
- **A new open item:** this session's `auto` leakage slope (0.42 W/°C, 0.28 with the dips kept), against 0.20–0.24 on
  E78, E82 and E86. It moves absolute D by up to 0.7 W in fp32 and decides whether the session's first pass survives
  E78's zeros-line gate. Removing the dips moves it by 0.15 W/°C, which is unexplained.
- **For the lab's runbooks:** a queue budget set from another experiment's run time can leave the registered minimum
  of passes with no margin. Register one spare pass inside the budget, register the budget in seconds, and implement
  it as an exact check in seconds, never a floor (A1's spare pass was refused by a whole-minute floor, by 1 s).

## Files

| file | what |
|---|---|
| `e91.json`, `runs.csv`, `reduce.txt` | the primary reduction (`reduce_e78.py` unchanged via `reduce_e91.py`: E86's items, card 1's 65/65 config gate, dips removed, leakage `auto`) |
| `e91-dipskept.json`, `e91-leak{0.1994,0.545,0.3803,0}.json` (+ csv, txt, log) | the registered arms |
| `scored.json`, `results.md` | every registered rule (all NOT SCORED), the arms' verdicts, the cross-card pairs, the replication of E86's ratios |
| `scored-leak0.1994.json`, `results-leak0.1994.md`, `scored-leak0.json`, `results-leak0.md` | reported views: the scorer run on two arms (§ Departures) |
| `aifoundry1-c1/kinds/p9110`–`p9113`, `kinds-smoke-p9101` | raw passes: 10 Hz telemetry, launch records, marks, tile dumps, config reads, manifests |
| `logs/` | the queue logs (`e91-queue-1.log`: the first queue; `e91-queue.log`: A1's second), the dry run's 21:08 skip line, push and claim times. Added after verification: `a1-second-queue.sh` and `.out` (the lane's A1 helper and its output), `dry-p9100/` (the 21:05 dry pass's block, plan, run log, marks and config reads, copied read-only from aifoundry1) and the verification lines in `push-and-claim-times.txt` |
| `code.sha256` | sha256 of every file the collection used |
| `corrections-check.py`, `corrections-check.txt` | the desk check behind Corrections after verification: every number it quotes, from the committed files (standard library only; the same output on Python 3.9 and 3.14) |

Reproduce on the Intel: copy `aifoundry1:nekko/build/claims-v3/aifoundry1-c1/{kinds,kinds-smoke}/p91*` to
`build/claims-v3/aifoundry1-c1-e91/`, then `PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/kinds/collect_e91.sh
'p91[1-9][0-9]' build/claims-v3/aifoundry1-c1-e91` (a few seconds).

## Corrections after verification (Sat 31 Oct 2026)

An independent verifier checked E91 after the data commit (`7c0af0c1`):
- It re-ran `reduce_e91.py` and `score_e91.py` on the committed raw passes. The six reductions, `scored.json` and
  `scored-leak0.1994.json` came back with zero numeric differences.
- It recomputed ρ, the differences from E86, the gate values, the slopes and the queue arithmetic independently.
- It found these sound: the registration order, the frozen inputs, A1's timing (before any reduction), the card conduct
  and the claim and release. Nothing was written to the card, no `--reset-ms` was sent, and the config reads gave
  65 W / 65 °C / 600 MHz / 499 mV at both ends of all five blocks.

It found one major and eight minor faults in how E91 was stated and handed on. Each is corrected above, desk only: no
card was touched, nothing was re-run, and no registered prediction, rule, number or verdict changed (all eleven NOT
SCORED). C10 is a slip the desk found while correcting. Every number below is printed by
[`corrections-check.py`](corrections-check.py) into [`corrections-check.txt`](corrections-check.txt), under the section
named.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **Major: the ratios handed on for the blog did not name their baseline, and "the same fraction" was not shown for int8.** The handed-on blog point said the real tiles "cost the same fraction of random data" (fp32 98.5–99.7%, fp16 96.6–99.3%, int8 81–89%) without saying these are D ratios, power over each format's all-zeros level. A reader takes "int8 costs 81–89% of random" as an 11–19% power saving; of the whole board it is 1.7–3.1%. E86's verification (`65f0ab03`) required every ratio to name its baseline. The int8 difference between the cards, +0.015 ± 0.067, does not show "the same" | Result 1's heading names D and gives the S and p80 ranges. A table gives the D, S and p80 ratios per tile on card 1, and a second gives the three-tile means on both cards with their differences. Over the zeros level int8 costs 81–89% of random, over idle 86–91%, and of the whole board 96.9–98.3%. What it changes and the handed-on blog point name the baseline and say int8 agrees only within its noise. Card 1 idles at 33.0 W against aifoundry3's 25.9 W, which pulls its whole-board shares toward 1, so those shares do not compare the cards. The data commit `7c0af0c1` keeps its subject; its "ratios to random" are over each format's all-zeros level |
| C2 | **The handed-on blog point compared the card scale with "51 synthetic kinds".** E82's 1.031 is the median over 32 kinds, those that switch at least 5 W (E82 `scored.json` › `cross_card.primary.x3`, n 32). E82's own verifier flagged the same wording. The point also stated a NOT SCORED result (X4) as fact, and "the same ratio" hid that the scale spans 1.018–1.054 with the leakage treatment. This README already said 32 | The handed-on blog point is labelled exploratory. It says the real tiles scale like the six synthetic kinds beside them (within 0.0025), gives the scale as 1.018–1.054 by the leakage correction, and cites E82's 1.031 over its 32 kinds |
| C3 | **A1 was carried out with a rounding A1 does not state, and the account of it overstated the case.** A1 sets the budget at 35 − used − 3 card-minutes with no rounding. `queue_e86.sh` takes whole minutes. The lane's helper, written at 21:30:54, 30 s after A1 was pushed, floored the budget, and that floor alone refused pass 9114: 360 s against 361 s, where A1's arithmetic gave 405 s. The README said "by the time the refusal was read (about 21:36), even the exact budget no longer held it". In fact it held until 21:36:06.8 (401.8 s at 21:35:26, 371.8 s at 21:35:56). It also said "A1 does not name a unit", but A1 names card-minutes; what it lacks is a rounding. The handed-on blog point said the spare pass "missed its time budget by one second" | The registered outcome, Registered against what happened and Departures say the floor was the lane's implementation choice, and date it. The helper and its output are committed under `logs/`. The "exact budget no longer held it" sentence is gone. The reason that stands is that starting the pass after the registered rule refused it would have been a second, unregistered decision. The blog point says the spare pass missed a whole-minute rounding of its budget by one second and would have run on the registered arithmetic. The runbook lesson adds: implement a registered budget as an exact check in seconds, never a floor. The NOT SCORED outcome is unchanged |
| C4 | **The handed-on headline gave only the 0.1994 arm's verdicts.** The other arm that keeps all four passes, leakage 0, gives R4 INCONCLUSIVE and R5 FAIL (`scored.json` › `rules.*.at_arms.leak0`). So the four-pass verdicts depend on the arm | The registered outcome lists both four-pass arms' verdicts and says the arms are sensitivity analyses, not a fallback primary. The headline handed on does the same |
| C5 | **The card scale compared the real tiles with a median that contains them.** Result 5 said the real tiles' median lies "within 0.002 of all 15 kinds' median", and nine of the 15 are the real tiles. It also said the scale "moves by ±3%", where it spans 1.018–1.054 | Result 5 compares the real tiles with the six synthetic kinds run beside them: within 0.0025 at every resolved pairing (+0.0003, +0.0021, +0.0015, −0.0023; −0.0011 with the dips removed on both cards). The conclusion stands. The scale is given as spanning 1.018–1.054 |
| C6 | **"No machine path enters the committed files" was false as written.** The raw pass files and the queue logs carry the box's own paths, under his public login's home directory on aifoundry1 (the repo-wide convention for raw files). That was 1,245 lines at verification, and 1,246 with the second queue's output added here. The reductions carry none | Departures says no Intel path enters the reductions, and that the raw pass files and queue logs keep the box's own paths |
| C7 | **Two die-rise values were handed on as "1.00 ± 0.00 (95%)".** int8 `l6_mlp_down` and `l6_attn_qk` read exactly 1 °C in each of the three passes. The interval therefore has zero width, which hides the reading's 1 °C resolution | The energy paragraph says those two read 1 °C in every pass, at a 1 °C resolution. The handed-on table cells say "1 °C in all three passes (whole-degree reading, resolution 1 °C)" and give no ± |
| C8 | **The handed-on text for the records ended with a lane path on the Intel**, inside text meant for the public records and hub | Dropped from the text handed on. It was never in this README |
| C9 | **The 21:05 dry pass had no committed source.** "Planned 34 launches (9 real), all ET_DEVICES=1" came from the dry pass's stdout log. The 21:08 setup run overwrote that log with its skip line (`logs/e91-dry.log`) | The pass directory's block.json, plan.json, run.log, marks.jsonl and config reads were copied read-only from aifoundry1 into `logs/dry-p9100/`; no device was opened. They show 32 runs planned (9 on real tiles), 2 burn-ins (34 launch commands), `ET_DEVICES=1` in the run log's header, and no launch made. Registered against what happened cites them |
| C10 | **One push time.** The header and Registered against what happened gave `eb72ce5d` as pushed at 21:09:12, which is when the lane's command returned. GitHub's activity record reads 21:09:11 (04:09:11Z), and git's commit time is 21:09:09 | The header and the table give 21:09:11, by GitHub's record. `logs/push-and-claim-times.txt` adds the record for all three commits (A1 21:30:24, data 21:41:18) and the claim's time from its message id, 21:10:07.755 |
