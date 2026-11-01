# E91: the real tensors' energy replicated on aifoundry1 card 1 (GPT-2 small's numbers, 600 MHz)

*Sat 31 Oct 2026 (week 44), Q130's evening round. Pre-registered in `eb72ce5d` (pushed 21:09:12 PDT, before the claim
and the first launch): [`tools/claims-v3/kinds/E91.md`](../../../../tools/claims-v3/kinds/E91.md), frozen numbers in
`predictions-e91.json` (sha256 `56efe2e7…`). Amendment A1 in `7f007f53` (pushed 21:30:24 PDT, during pass 9113, before
any reduction). aifoundry1 card 1 (`V3_DEVICE=1`, its own lock) at 600 MHz, 498.6 mV mean, TDP 65 W / threshold 65 °C
read at both ends of every block (21:10:19–21:35:07), never set. Nothing was written to the card, and no `--reset-ms`
was sent. Claim 1566303302210158713 in #community-lab, posted 21:10:07 PDT, released 21:36 PDT by editing it (held
26.1 min; device access 24.8 min, 21:10:19–21:35:07; budget 35 card-minutes;
[`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)).*

## The registered outcome: every rule NOT SCORED

**Four passes ran (9110–9113). E78's zeros-line pass gate set pass 9110 aside in the registered primary reduction:
`int8.zeros` departs −0.288 W from its straight line, against a 0.25 W limit. That leaves three kept passes, below the
registered minimum of four, so all eleven registered verdicts (R1–R5, S1, X1–X4) are NOT SCORED** (`scored.json` ›
`tally`). The fifth pass that amendment A1 added for exactly this risk did not run. The first queue's budget rule
stopped before `p9114` by 11 s (elapsed 1,450 s + the longest pass, 361 s, against 1,800 s). A1's second queue then
refused it by 1 s: A1's budget, 35 − 25.25 − 3 = 6.75 card-minutes, was floored to the queue's whole minute (6, i.e.
360 s) against the 361 s pass. On A1's exact arithmetic the pass would have fit. The floor came from the
implementation, and the pass was not started by hand afterwards (§ Departures).

So **by its registered rules E91 replicates nothing.** Everything below comes from the three kept passes or from the
registered arms. It is reported, labelled, and no verdict rests on it.

## What the three kept passes and the arms show (reported, not scored)

**1. On card 1 the real tiles cost what they cost on aifoundry3, relative to random data in the same pass.** D (board
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
1.018 and 1.032. E82 measured 1.031 over its 32 synthetic kinds (`scored.json` › `cross_card.primary` and `.pairs`).
At every pairing the real tiles' median lies within 0.002 of all 15 kinds' median, so the real tiles scale between the
cards as E78's kinds do. The scale itself moves by ±3% with the leakage slope and the dip treatment. September's band
[0.88, 0.99] is missed at every pairing (X2a / X3 would fail, as on E82). X1's ranks are 0.90 / 1.00 / 1.00 (fp32 /
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
1.0–1.2 °C (whole-degree reading).

## Registered against what happened

| | registered (E91.md) | what happened |
|---|---|---|
| pre-registration | README, frozen predictions and rules committed and pushed before the claim | `eb72ce5d` pushed 21:09:12; claim 21:10:07; first launch 21:10:19 |
| setup | `run_e91.sh setup`, no device access | 21:05 and 21:08: every file identical to the freeze; tiles ok; the 21:05 dry pass planned 34 launches (9 real), all `ET_DEVICES=1` |
| smoke | pass 9101, seven 2 s runs | 21:10:19–21:11:03: 7 of 7 ok, cycles/op 546 / 546 / 318, 599.2–599.5 MHz, launch coverage 0.9975–0.9983, config 65 W / 65 °C / 600 MHz / 499 mV at both ends |
| passes | 9110–9115, at least four, by the budget rule (30 card-min of the queue) | 9110 (21:11:12, 351 s), 9111 (361 s), 9112 (331 s), 9113 (347 s, ended 21:35:07); the rule stopped before 9114 |
| A1 | pass 9114 alone if it fits in 35 − used − 3 card-minutes | refused at 21:35:22: budget floored to 6 min against 361 s (§ Departures) |
| kept passes | ≥ 4 for any verdict | **3** (9111–9113); 9110 set aside by E78's zeros-line gate |
| verdicts | R1–R5, S1, X1–X4 | **all NOT SCORED** |
| arms | dips kept; leakage 0.1994, 0.545, 0.3803, 0 | dips kept: 3 passes, NOT SCORED; 0.545: 2 passes; 0.3803: 3 passes; **0.1994: 4 passes, R1–R5, S1 PASS, X1 PASS, X2a / X2b / X3 FAIL, X4 PASS**; 0: 4 passes, R1–R3 PASS, R4 INCONCLUSIVE, R5 FAIL, S1 PASS, and with no correction on both cards X1 PASS, X2a / X2b / X3 FAIL, X4 PASS (`scored.json` › `rules.*.at_arms`; the 0.1994 X verdicts are the "0.1994 on both" pair's) |
| budget | ≤ 35 card-minutes, claim to release | 26.1 |

## Departures

- **A1 (`7f007f53`, 21:30:24, during 9113, before any reduction):** one pass added inside the registered 35
  card-minutes, because the passes took about 5.8 min, not E88's 5.4. No rule, band, gate or analysis changed. Its
  outcome is the main departure from plan. A1 sets the second queue's budget at 35 − used − 3 card-minutes, and the
  script floored that to an integer because `queue_e86.sh` counts whole minutes. At 21:35:22 that gave 6 min against the
  first queue's longest pass, 361 s, so the pass was refused by 1 s; unfloored (6.75 min) it would have run. A1 does not
  name a unit. The pass was not started by hand afterwards. By the time the refusal was read (about 21:36), even the
  exact budget no longer held it, and starting it after a refusal would have been a second, unregistered decision.
- **The reductions record repo-relative pass directories.** `collect_e91.sh` ran over a gitignored copy at
  `build/claims-v3/aifoundry1-c1-e91/`, as E86's did, so no machine path enters the committed files. An earlier run of
  the same code over the lane's scratch copy gave identical numbers.
- **Reported views beyond the registered list:** `scored-leak0.1994.json` / `results-leak0.1994.md` and
  `scored-leak0.json` / `results-leak0.md` are `score_e91.py` run with an arm as its input. They give each arm's tables
  in full, and their verdicts are the ones `scored.json` › `rules.*.at_arms` already reports. Their cross-card pairing is
  the arm against E86's registered reduction (median 1.021 at 0.1994), not the registered "0.1994 on both" pair (1.023,
  in `scored.json`).

## What it changes for the blog material and the hub

- **No registered result.** E91 cannot be cited as a passed replication. The hub should list it as run, with 3 of 4
  passes kept and every verdict not scored.
- **What it supports, labelled exploratory:** on a second card, real GPT-2 tiles cost the same fraction of random data
  as on aifoundry3. The fp32 and fp16 fractions agree within about 1%, the int8 ones within the noise. The fp16 tiles
  sit clearly below random on card 1 (0.983 ± 0.002 over 3 passes), matching E86's post-hoc value, not its
  inconclusive registered one. The real tiles scale between the two cards with E78's kinds, at 1.02–1.05 depending on
  the leakage slope.
- **A new open item:** this session's `auto` leakage slope (0.42 W/°C, 0.28 with the dips kept), against 0.20–0.24 on
  E78, E82 and E86. It moves absolute D by up to 0.7 W in fp32 and decides whether the session's first pass survives
  E78's zeros-line gate. Removing the dips moves it by 0.15 W/°C, which is unexplained.
- **For the lab's runbooks:** a queue budget set from another experiment's run time can leave the registered minimum
  of passes with no margin. Register one spare pass inside the budget, and a budget in seconds.

## Files

| file | what |
|---|---|
| `e91.json`, `runs.csv`, `reduce.txt` | the primary reduction (`reduce_e78.py` unchanged via `reduce_e91.py`: E86's items, card 1's 65/65 config gate, dips removed, leakage `auto`) |
| `e91-dipskept.json`, `e91-leak{0.1994,0.545,0.3803,0}.json` (+ csv, txt, log) | the registered arms |
| `scored.json`, `results.md` | every registered rule (all NOT SCORED), the arms' verdicts, the cross-card pairs, the replication of E86's ratios |
| `scored-leak0.1994.json`, `results-leak0.1994.md`, `scored-leak0.json`, `results-leak0.md` | reported views: the scorer run on two arms (§ Departures) |
| `aifoundry1-c1/kinds/p9110`–`p9113`, `kinds-smoke-p9101` | raw passes: 10 Hz telemetry, launch records, marks, tile dumps, config reads, manifests |
| `logs/` | the queue logs (`e91-queue-1.log`: the first queue; `e91-queue.log`: A1's second), the dry run, push and claim times |
| `code.sha256` | sha256 of every file the collection used |

Reproduce on the Intel: copy `aifoundry1:nekko/build/claims-v3/aifoundry1-c1/{kinds,kinds-smoke}/p91*` to
`build/claims-v3/aifoundry1-c1-e91/`, then `PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/kinds/collect_e91.sh
'p91[1-9][0-9]' build/claims-v3/aifoundry1-c1-e91` (a few seconds).
