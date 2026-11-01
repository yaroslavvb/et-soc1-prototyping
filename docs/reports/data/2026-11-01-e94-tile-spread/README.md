# E94: tile-to-tile spread — what a kind of number costs (aifoundry1 card 1, 600 MHz)

*Sun 1 Nov 2026 (week 44), Q132 (lane `a1c1-e94-spread`). Pre-registered in `f45f0b34` (pushed 00:59:38 PDT, before the claim and
the first launch): [`tools/claims-v3/kinds/E94.md`](../../../../tools/claims-v3/kinds/E94.md), frozen numbers in
`predictions-e94.json` (sha256 `7810782d…`), the scorer `score_e94.py` (sha256 `3baa1190…`) and its self-test in the same commit.
aifoundry1 card 1 (`V3_DEVICE=1`, its own lock) at 600 MHz in every sample, 498.6 mV mean, TDP 65 W / threshold 65 °C read under the
card lock at both ends of every block (01:00:43–01:39:25 PDT), never set. Nothing was written to the card, and no `--reset-ms` was
sent. Claim 1566361297262616617 in #community-lab, posted 01:00:34 PDT, released by editing it at 01:45 PDT.*

**What ran.** Forty-two fresh draws of eight kinds (seeds `sha256("E94/<type>/<kind>/draw<r>")`, none rejected), E90's nine draws byte
for byte as a bridge to aifoundry3, E78's committed tile of each kind, and E78's six anchors three times a pass: 76 runs a pass, three
passes (9410–9412), E78's runner and reduction unchanged and sha256-checked. **All three passes were kept; 227 of 227 attempted runs
passed every gate** (one anchor run was skipped by the launch rule). The unit of replication is **the draw**: every interval on a kind is
over draws, the correction E90 C2 asked for. D is a tile's board power over its own type's zeros; S is over the idle bracket.

## Results

**1. What a kind costs, on card 1, with the draw as the unit** (`scored.json` › `primary.rules_of_number`):

| kind (the page's row) | k | D: kind's mean ± 95% over draws, W | between-draw SD τ [95%], W | one tile's between-pass SD, W | τ ÷ that | S: kind's mean ±, W | pJ/MAC, kind (S) | committed tile D, W | committed − kind ± 95%, W | inside the draws' spread (R1) | the row (R2) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 50% zeros † (`fp32.sparse50`) | 9 | **7.645** ± 0.382 | **0.49** [0.33, 0.95] | 0.11 | 4.3 | 9.48 ± 0.37 | 2.066 | 7.022 | **−0.623** ± 0.397 | inside | **CORRECTION** |
| fp16 ReLU × small weights † (`fp16.nn_like`) | 9 | **15.914** ± 0.435 | **0.57** [0.38, 1.08] | 0.06 | 10.1 | 17.77 ± 0.43 | 1.935 | 17.055 | **+1.141** ± 0.442 | inside | **CORRECTION** |
| fp16 uniform in [0, 1) (`fp16.uniform01`) | 9 | **18.722** ± 0.058 | **0.06** [0.02, 0.14] | 0.08 | 0.8 | 20.55 ± 0.07 | 2.239 | 18.910 | **+0.188** ± 0.106 | inconclusive | **NO CORRECTION** |
| fp32 ReLU × small weights † (`fp32.nn_like`) | 6 | **12.351** ± 0.582 | **0.55** [0.34, 1.36] | 0.11 | 5.2 | 14.16 ± 0.58 | 3.084 | 12.804 | **+0.452** ± 0.603 | inside | **UNRESOLVED** |
| int8 50% zero bytes † (`int8.sparse50`) | 6 | **5.434** ± 0.093 | **0.07** [0.00, 0.21] | 0.10 | 0.7 | 7.77 ± 0.09 | 0.246 | 5.348 | **−0.087** ± 0.146 | inside | **NO CORRECTION** |
| fp32 random (normal) (`fp32.randn`) | 4 | **24.180** ± 0.130 | **0.06** [0.00, 0.30] | 0.10 | 0.6 | 26.01 ± 0.18 | 5.665 | 24.099 | **−0.081** ± 0.155 | inside | **NO CORRECTION** |
| fp16 random (normal) (`fp16.randn`) | 4 | **21.431** ± 0.093 | **0.03** [0.00, 0.21] | 0.09 | 0.3 | 23.29 ± 0.12 | 2.536 | 21.559 | **+0.128** ± 0.130 | inconclusive | **NO CORRECTION** |
| int8 random −128…127 (`int8.full`) | 4 | **6.962** ± 0.019 | **0.00** [0.00, 0.04] | 0.04 | 0.0 | 9.29 ± 0.09 | 0.295 | 6.928 | **−0.034** ± 0.057 | inconclusive | **NO CORRECTION** |

**2. E78's table needs a correction in 2 of these eight rows, and one more row is unresolved as registered.** The tile E78 ran for fp16 "ReLU × small weights" reads **+1.14 ± 0.44 W** above its kind's mean, and its CORRECTION holds at every arm (+0.89 to +1.19 W). The tile for fp32 "50% zeros" reads **−0.62 ± 0.40 W** below. That row keeps its sign at every arm and is marginal in size against the ±0.50 W band: its verdict is UNRESOLVED at the 0.545 W/°C arm (−0.478 ± 0.394 W) and on the six fresh draws alone (−0.629 ± 0.643 W). fp32 "ReLU × small weights" is UNRESOLVED (+0.45 ± 0.60 W), as registered in advance: six draws know that kind's mean to ±0.58 W; result 7 resolves it post hoc. The other five rows need none. **Translated to aifoundry3 for the three rules with a bridge, because E94-R8 passes (result 5)**, by the registered statement, E78's cell minus (offset × E82's card scale); rows with no draw read on both cards keep card 1's numbers (`check_e94.txt` [B]):

| row, aifoundry3 | R2 | D, W: E78 → kind | S, W | nJ per op | pJ per MAC | E78 − kind ± 95%, W | E90's own draws there, W |
|---|---|---|---|---|---|---|---|
| fp16 ReLU × small weights † | **CORRECTION** | 17.60 → **16.42** | 19.48 → **18.30** | 17.38 → **16.33** | 2.122 → **1.993** | +1.18 ± 0.46 | 16.69 (3 draws) |
| fp32 50% zeros † | **CORRECTION** | 7.30 → **7.94** | 9.24 → **9.88** | 8.24 → **8.82** | 2.013 → **2.153** | −0.64 ± 0.41 | 8.00 (3 draws) |
| fp16 uniform in [0, 1) | **NO CORRECTION** | 19.43 → **19.23** | 21.37 → **21.18** | 19.06 → **18.89** | 2.327 → **2.306** | +0.19 ± 0.11 | 19.16 (3 draws) |

`fp16.uniform01` needs no correction by the registered band, but its tile is above all nine draws, +0.19 ± 0.11 W on card 1. The page's other columns on these rows (burst and sustained clock, the limit) are E80's and E83's readings of the committed tile and are not corrected here.

**3. A kind with no zeros barely moves with the draw; a kind with random zeros moves about half a watt.** Pooled over fp32 and fp16 random and fp16 uniform (19–24 W of D), the tile component is **0.055 W [0.022, 0.105]**, about 0.3% of their power, under the registered 0.30 W (R4a PASS, 14 degrees of freedom), and smaller than one tile's own between-pass SD (0.08–0.10 W). Int8's two rules pool to **0.052 W [0.000, 0.127]** against 0.25 W (R4b PASS). The three float kinds with random zeros have **0.49, 0.57 and 0.55 W**, 4–10 times one tile's between-pass SD; each interval holds the SD the gate law expected from kinds.json's gate-share spread alone, 0.69, 0.60 and 0.85 W (R3 PASS in all four gated rules). So **a † cell of these kinds is one draw from a spread with an SD of about 0.5 W, so about ±1 W at 95%**, not "good to about ±0.5 W".

**4. One line computed from the tile says where a draw lands.** The gate law, `D(draw) = D(committed) × (1 − g_draw)/(1 − g_committed)`, frozen before the card ran and with no fitted number, tracks the 24 fresh draws of the gated rules to **0.140 W rms**, against 0.894 W for predicting no move and 0.285 W for Q130(n)'s predictor on the same draws (R6 PASS; its hindsight figure on E90's draws was 0.108 W). Inside a kind, centred on the kind's mean, both explain most of what moves: residual 0.109 W (gate law) and 0.103 W (Q130(n)) of a centred SD of 0.585 W over the float gated rules (R7 PASS twice). Q130(n)'s deltas pass over all 42 fresh draws (R5 PASS, rms 0.243 W, 0.682 W for no move, none resolved opposite); its loss to the gate law is one rule, `fp16.nn_like`, where it misses by 0.527 W rms against 0.202 W. Among dense draws nothing computed from the tile beats predicting no move, because they do not move: bus bits taken proportionally make it worse, and the frozen bus-bits reading of a sparse draw is poor as well (`scored.json` › `primary.reported_laws_on_fresh_draws`; rms in W, then centred residual with its ratio to the centred SD):

| frozen delta, on the fresh draws | gated rules (24), rms | centred | dense rules (18), rms | centred |
|---|---|---|---|---|
| no move at all | 0.894 | 0.509 (1.00) | 0.146 | 0.066 (1.00) |
| the gate law, D(committed) × (1 − g)/(1 − g_c) | **0.140** | 0.102 (0.20) | same as no move (g = 0) | same |
| Q130(n)'s predictor | **0.285** | 0.097 (0.19) | 0.172 | 0.076 (1.15) |
| bus bits, D(committed) × bus/bus_c (reported) | **0.618** | 0.403 (0.79) | 0.311 | 0.226 (3.40) |

**5. The same draw moves alike on both cards.** E90's nine draws, read on aifoundry3 on 31 Oct and on card 1 here: rms of offset(card 1) × scale − offset(aifoundry3) is **0.131 W** (R8 PASS), where noise alone gives 0.113 W and predicting no move 0.703 W. One draw carries most of it (`fp16.uniform01 d1`, +0.345 W, whose aifoundry3 reading has an SE of 0.21 W); without it 0.066 W (`check_e94.txt` [I]).

| draw | D(draw) − D(committed), aifoundry3, W | card 1, W | card 1 × scale, W | difference, W |
|---|---|---|---|---|
| `fp32.sparse50 d1` | +0.898 | +0.745 | +0.768 | −0.130 |
| `fp32.sparse50 d2` | +0.884 | +0.840 | +0.865 | −0.018 |
| `fp32.sparse50 d3` | +0.328 | +0.246 | +0.253 | −0.075 |
| `fp16.nn_like d1` | −0.601 | −0.525 | −0.542 | +0.058 |
| `fp16.nn_like d2` | −0.823 | −0.709 | −0.733 | +0.090 |
| `fp16.nn_like d3` | −1.189 | −1.157 | −1.195 | −0.007 |
| `fp16.uniform01 d1` | −0.459 | −0.110 | −0.114 | +0.345 |
| `fp16.uniform01 d2` | −0.257 | −0.272 | −0.281 | −0.024 |
| `fp16.uniform01 d3` | −0.161 | −0.152 | −0.157 | +0.003 |

**6. No committed tile is shown to be outside its kind's spread (R1: 5 inside, 3 inconclusive, 0 outside), and that does not excuse the rows.** A prediction interval with six to nine draws is ±2.4–2.8 SD wide, so a real draw can sit 1.9 SD off its kind's mean, as `fp16.nn_like`'s does (p = 0.09), and still cost a watt more than the kind. The two tiles kinds.json had flagged before any card ran (E78 C5) read above all nine draws of their rule: `fp16.nn_like` (gate share below its band) and `fp16.uniform01` (bus bits above its band, p = 0.046; Holm over eight tests does not resolve it). `check_e94.txt` [G].

**7. Post hoc, labelled: the gate share as a control variate tightens the float kinds' means four- to eightfold (int8's barely), and resolves `fp32.nn_like`.** R6 and R7 having passed, each draw can be moved by the frozen law to its rule's mean gate share, which kinds.json knows from 400 draws, before averaging. This uses no data beyond the registered run's, but it was not registered, and it changes no verdict (`check_e94.txt` [C]):

| rule | draws' mean gate share vs the rule's | registered kind's mean, W | law-adjusted, W | committed − kind, post hoc, W | verdict by R2's thresholds, post hoc |
|---|---|---|---|---|---|
| `fp32.sparse50` | 0.7517 vs 0.7505 | 7.645 ± 0.382 | 7.684 ± 0.099 | −0.662 ± 0.164 | CORRECTION |
| `fp16.nn_like` | 0.2574 vs 0.2487 | 15.914 ± 0.435 | 16.096 ± 0.057 | +0.959 ± 0.085 | CORRECTION |
| `fp32.nn_like` | 0.5234 vs 0.5009 | 12.351 ± 0.582 | 12.933 ± 0.129 | −0.130 ± 0.168 | NO CORRECTION |
| `int8.sparse50` | 0.0559 vs 0.0672 | 5.434 ± 0.093 | 5.371 ± 0.082 | −0.023 ± 0.142 | NO CORRECTION |

The six `fp32.nn_like` draws happened to gate more than the rule does on average, which pulled their plain mean down and made the committed tile look high; with that removed its row needs no correction (with the rule's own fitted slope, 12.847 ± 0.137 W, the same call). The fp16 "ReLU" correction is +0.96 W by this view against the registered +1.14 W, the same call.

**8. The price of a gated lane (post hoc).** Inside a rule, D falls by 25.2 ± 2.6, 20.3 ± 2.3 and 22.0 ± 4.3 W per unit of gate share (`fp32.sparse50`, `fp16.nn_like`, `fp32.nn_like`), so **1% more of the lane-cycles gated saves 0.20–0.25 W, about 1% of random data's power**. Each interval holds D(random) (24.1 and 21.6 W). The frozen law's slope, D(committed)/(1 − g_c), is too steep in `fp32.sparse50` (31.1 W per unit, outside −25.2 ± 2.6), and a slope of D(random) per unit tracks the same 24 draws to 0.148 W against the frozen law's 0.140 W, having seen them (`check_e94.txt` [D]). In int8 the slope is unresolved (−3.6 ± 7.0 W per unit; only 7% of its lane-cycles gate).

**9. Why the dense kinds barely move (post hoc).** Inside the three dense float rules, D rises 50.8 ± 30.2 µW per operand-bus bit an op (20 tiles): about twice E88's frozen operand-bus price (21.7 and 27.7 µW, both inside the interval), and 5 times below a plain share of the total, about 264 µW. A draw's bus-bit spread is about 1,100 bits, so its power moves by only 0.03–0.06 W (`check_e94.txt` [E]).

## The desk table may speak, and what it says

R6 and R9's gate-law verdict both PASS (rms 0.322 W on the committed tiles' offsets, Q130(n) 0.382 W), so the frozen `predictions-e94.json` › `desk_table` may be quoted for rows no card ran, **labelled as predicted**. It names one more row at its band: **fp16 "50% zeros" (`fp16.sparse50`), offset +0.52 W by the gate law and +0.50 W by Q130(n), with a between-draw SD of 0.66 and 0.64 W, so E78's 13.20 W would be about 12.7 W at its kind's mean. Not measured here.** Every other random row is inside its band by both laws (largest: `fp16.wsparse50` −0.32 / −0.02 W; `int8.wsparse50` −0.17 / −0.11 W). The † rows' predicted SDs are in `check_e94.txt` [H], gate law then Q130(n): fp32 integers 0.32 / 0.31 W, fp16 50% zero words 0.69 / 0.51 W, int8 50% zero words 0.26 / 0.21 W; the others are 0.26 W or less.

## Registered against happened

| rule | registered | happened | verdict |
|---|---|---|---|
| E94-R1 (8) | committed tile inside the 95% prediction interval of one more draw | offsets above; none wholly outside | **5 PASS, 3 INCONCLUSIVE** (`fp16.uniform01`, `fp16.randn`, `int8.full`), 0 FAIL |
| E94-R2 (8) | NO CORRECTION / CORRECTION / UNRESOLVED against ±0.50 W (float), ±0.25 W (int8) | each a likely outcome in its power table (`fp16.nn_like` CORRECTION 1.00, `fp32.sparse50` CORRECTION 0.72, `fp32.nn_like` UNRESOLVED 0.93, `int8.sparse50` NO CORRECTION 0.38, the other four NO CORRECTION at least 0.83) | **2 CORRECTION, 5 NO CORRECTION, 1 UNRESOLVED** |
| E94-R3 (4) | the gate law's expected SD inside τ's 95% interval | 0.69 in [0.33, 0.95]; 0.60 in [0.38, 1.09]; 0.85 in [0.34, 1.36]; 0.09 in [0.00, 0.21] | **PASS ×4** |
| E94-R4a | dense float kinds, pooled τ's upper bound ≤ 0.30 W | 0.055 [0.022, 0.105] W | **PASS** |
| E94-R4b | int8's two rules, pooled τ's upper bound ≤ 0.25 W | 0.052 [0.000, 0.127] W | **PASS** |
| E94-R5 | Q130(n), 42 fresh draws: rms ≤ 0.50 W, below no move, none opposite | 0.243 W, no move 0.682 W, none opposite | **PASS** |
| E94-R6 | gate law, 24 fresh draws: rms ≤ 0.30 W and below no move | 0.140 W, no move 0.894 W | **PASS** |
| E94-R7 (2) | centred residual ≤ 0.6 × centred SD, 18 fresh draws | gate law 0.19, Q130(n) 0.18 | **PASS ×2** |
| E94-R8 | E90's nine draws: rms ≤ 0.30 W across the cards | 0.131 W | **PASS** |
| E94-R9 (2) | each law's committed-tile offset: rms ≤ 0.50 W over the gated rules | gate law 0.322 W, Q130(n) 0.382 W | **PASS ×2** |
| E94-S1 | nine cells within ±0.50 / ±0.25 W of E82's dips-removed D | all inside, largest +0.112 W: fp32.randn +0.10, fp16.randn +0.07, anchor_pi −0.02, int8.full +0.09, fp32.sparse50 −0.01, fp16.nn_like +0.05, fp16.uniform01 +0.06, fp32.nn_like +0.08, int8.sparse50 +0.11 | **PASS** |

**Frozen expectations against the measured offsets of the committed tile:** `fp16.nn_like` gate law +1.13 W, Q130(n) +1.50 W, measured +1.14 W; `fp32.sparse50` −0.74, −0.61, measured −0.62 W; `fp32.nn_like` −0.18, −0.21, measured +0.45 ± 0.60 W (post hoc −0.13 W, result 7); `int8.sparse50` −0.02, +0.04, measured −0.09 W. **The arms** (dips kept, E78's pass gates opened, leakage `auto`, 0.1994, 0.3803, 0.545, 0): no pass was set aside at any arm, so the gates-opened arm equals the primary. These verdicts move: `E94-R2:fp32.sparse50` CORRECTION → UNRESOLVED at 0.545; `E94-R1:fp16.nn_like` PASS → INCONCLUSIVE at dips kept; `E94-R2:fp16.uniform01` NO CORRECTION → UNRESOLVED at dips kept; `E94-R1:int8.sparse50` PASS → INCONCLUSIVE at no correction; `E94-R2:int8.sparse50` NO CORRECTION → UNRESOLVED at 0.545, UNRESOLVED at no correction; `E94-R1:fp16.randn` INCONCLUSIVE → PASS at dips kept, PASS at no correction; `E94-R2:int8.full` NO CORRECTION → UNRESOLVED at 0.545; `E94-R9:q130n` PASS → INCONCLUSIVE at dips kept; `E94-S1` PASS → FAIL at 0.545, FAIL at no correction. S1's two moves are that arm's D against E82's reference at its own slope, as in E86 and E90: a frame change, not the session. No rule on spread, the laws or the bridge moves, except R9's Q130(n) at dips kept. **Checks:** clock 600 MHz in every sample; cycles per op 546.001 / 546.001 / 318.000; duty 0.9957–0.9967; idle consistency median |S − S0 − D| 0.073 W; carry-over 0.0017 ± 0.0008 W/W; rail lag 1.00 s; tie drift 0.07–0.32 W a pass; dip samples removed 13 / 15 / 17; every dumped tile equal to its registered sha256; TDP 65 / threshold 65 / 600 MHz / 499 mV at both ends of the smoke and all three passes (`e94.json` › `reducer.config_reads_raw`).

**Departures from E94.md.**

1. **The claim was held 45 minutes, not about 40.** Device access ended at 01:39:25 PDT, 38.9 minutes after the claim, inside the budget (queue 2,278 s of 2,400 s). The lane had handed off and was woken after the queue ended, so the card sat idle and claimed until the release edit at about 01:45:33 PDT. The post's own hold (1 h) was not exceeded.
2. **The collection ran on another desk machine, not the Intel,** which was overloaded (load above 100): Python 3.13, numpy 2.5.4, over a copy of the raw passes inside an ignored `build/` tree, so the recorded directories are relative. The freeze (`make_predictions_e94.py`, the self-test) ran there too; the tiles were built on the Intel and `make_e94.py --check` passed on the other machine. Code hashes are in `code.sha256`.
3. **Pass 9410's anchor `fp16.randn` #47 was skipped by the launch rule** (the reading went back to 59 °C inside the quiet wait), so that anchor has two runs in that pass, as E82 saw. It is a random anchor, not a zeros anchor, and no gate moved.

Two read-only looks during the run (01:04 and 01:14 PDT: return codes, the clock, the board's power range) computed no D. E93's data commit came about 11 minutes before this freeze; nothing of it was read or used until after E94's data (`check_e94.txt` [F] quotes E93's reading of the committed `fp32.sparse50` tile, 6.933 ± 0.216 W, against 7.022 W here). No amendment was needed.

## Interpretation (labelled: not measured by E94)

A gated lane-cycle costs almost nothing and a live one costs about what a random-data lane-cycle costs, so a sparse tile's cost is mostly its live share. That fits results 3, 4 and 8, and it is why a one-line law on a number from kinds.json does as well as a five-term predictor inside a kind. It does not say which stage saves the power, and it is a statement about offsets from a measured tile: E90 C1 stands, absolute prices need a measured neighbour. The dense kinds' small spread fits operand bits being priced at about the operand bus's own cost, with the multiplier and result path set by the distribution, which every draw of a rule shares; E94 does not separate those stages.

## What it changes

**Section 11, item 11: closed for these eight rows on this card**, and for the aifoundry3 table on three rows by R8. The rows no card ran have a frozen, tested prediction, not a measurement.

**The kinds table, section 2.**
- Change the † note: "Read a † cell as one draw, good to about ±0.5 W" should say that the between-draw SD is about 0.5 W for float kinds with random zeros (E94: 0.49, 0.57, 0.55 W), so one draw lies within about ±1 W of its kind's mean, and 0.07 W for int8's 50% zero bytes.
- Correct or annotate two rows on aifoundry3: fp16 "ReLU × small weights" S 19.48 → 18.30 W (nJ per op 17.38 → 16.33, pJ per MAC 2.122 → 1.993); fp32 "50% zeros" S 9.24 → 9.88 W (8.24 → 8.82, 2.013 → 2.153), the second marked arm-sensitive. Both ± about 0.4–0.5 W at kind level (post hoc 0.1–0.2 W).
- The dense rows measured need no † and no change: the draw moves them about 0.05 W. The desk table says the same of the dense rows no card ran here (predicted).
- fp32 "ReLU × small weights" stays as is: UNRESOLVED as registered, no correction post hoc.
- A predicted note for fp16 "50% zeros" (about 12.7 W at its kind's mean, against 13.20), labelled predicted. Not a measurement.

**Blog-ready sentences** (each with its source):
- Re-drawing the random numbers of a kind with no zeros moves its power by about 0.05 W in 19–24 W: 0.3% (E94 R4a).
- Re-drawing a kind with random zeros moves it by about 0.5 W, a standard deviation, because each draw gates a slightly different share of the lanes (E94 R3).
- Each extra 1% of lane-cycles gated saves about 0.2–0.25 W, about 1% of random data's power (E94 result 8, post hoc).
- One line, the tile's live share times the cost of its live lanes, said where 24 new draws would land to 0.14 W; predicting no change misses by 0.89 W (E94 R6).
- Two of the eight table rows we re-drew had been one unlucky tile: one a watt high, one 0.6 W low. The other measured rows held (E94 R2).
- The same draws moved the same way on two cards, to 0.13 W, where the noise alone is 0.11 W (E94 R8).

## Caveats

One card, one clock, one session, three passes. Nine draws know an SD to a factor of 0.68–1.92, six to 0.62–2.45, four to 0.57–3.69: that is why the dense claim is pooled. R8 tests the translation on three rules only; the rule's kind means on aifoundry3 are translated, not measured there, and the card scale (E82: 1.031, sd 1.2%) is a median over kinds. The rule is synthetic: nothing here says what a real tensor's "kind" is, and the speed columns were not re-drawn. The gate law was noticed on E90's draws before this freeze; R6 and R7 are its first test, on new draws, but it was chosen with E90 in view, and its slope is too steep in `fp32.sparse50` (result 8). Results 7, 8 and 9 are post hoc. The registered intervals over draws leave out the leakage arms, which here move offsets by up to about 0.15 W (`fp32.sparse50`, −0.48 to −0.74 W). int8's bus counts are provisional (kinds README), so its bus readings are reported only. Pass noise for a tile is pooled over its rule, while a single tile can scatter more: the committed `fp32.sparse50` read 6.742, 7.140, 7.183 W, an SD of 0.243 W against the pooled 0.114 W; with its own SD its offset's interval is ±0.514 W, which still excludes 0 (`check_e94.txt` [F]).

## Files

`e94.json` (the registered reduction), `runs.csv`, `reduce.txt`, `reduce.log`; the arms `e94-dipskept`, `e94-gatesoff`, `e94-auto`, `e94-leak0.1994`, `e94-leak0.3803`, `e94-leak0.545`, `e94-leak0` (`.json`, with `runs-*.csv`, `reduce-*.txt`, `reduce-*.log`); `scored.json` and `results.md` (`score_e94.py`: every rule, every draw, each verdict at every arm); `check_e94.py` and its output `check_e94.txt` (desk checks and the post-hoc views: A re-derives the table from `runs.csv`, B the rows on aifoundry3, C control variate, D gate-share slopes, E bus bits, F how firm the corrections are, G R1's p values, H the desk table, I the bridge; standard library only; it changes nothing); `code.sha256`; `logs/` (`e94-queue.log`, `e94-dry.log`, `e94-list.err`); `aifoundry1-c1/kinds/p9410`–`p9412` (raw telemetry, marks, launch records, tile dumps, configs, manifests) and `kinds-smoke-p9401`. Code and the registration: `tools/claims-v3/kinds/` — `E94.md`, `predictions-e94.json`, `make_predictions_e94.py`, `make_e94.py`, `e94/` (the tiles and `e94.json`), `e94_common.py`, `run_e94.py`, `block_e94.sh`, `queue_e94.sh`, `run_e94.sh`, `reduce_e94.py`, `score_e94.py`, `collect_e94.sh`, `selftest_e94.py`/`.txt`. Reproduce: copy `aifoundry1-c1/` to `build/claims-v3/aifoundry1-c1/`, then `PY=python3 bash tools/claims-v3/kinds/collect_e94.sh 'p94[1-9][0-9]' build/claims-v3/aifoundry1-c1`.
