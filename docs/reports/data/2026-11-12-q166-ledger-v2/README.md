# Q166 step 1: the load ledger v2 - the joined load model revived by its own recipe, frozen first, then held out on E39, E37 and E59: 0.69 / 1.17 / 0.75 W rms against v1's 1.10 / 2.14 / 3.02, and sparse parity's joules a solve within 1.7-3.3% given its seconds (2.5-4.9% with them forecast)

*Thu 12 Nov 2026 (week 46), PST, on the Intel, desk only: no card, no lab box, no device command, no post. Q166's lane calc-a,
step 1 of the November checkpoint's plan, on the owner's ask of about 15:15 PST: "Please take into account the following
suggestions and start filling in the gaps". The checkpoint (a private page) read his question of Wed 11 Nov, "Can I answer how
many joules a particular computation takes?", and recommended reviving this model first; the model's retirement note asks for
"a whole-workload question from the owner", and his message is read as that question.*

**Dated corrections (Thu 12 Nov 2026, fix-q166, on Q166's verifier; every figure post hoc, in
[`posthoc-v2.json`](posthoc-v2.json), from `tools/ledger/posthoc_ledger_v2.py`; nothing frozen changed):**
- **E37 is post hoc for the awake rule** (a hart's time priced once). The rule was set during the build after arithmetic
  that put v2 beside E101's DRAM arm, which is the same benchmark streaming from DRAM. Without it, E37 reads +27.3 to +28.0%
  an op and 2.40 W rms, worse than v1's 2.14. So E37's gain over v1 rests on that rule.
- **E101's two DRAM-arm cells are post hoc for the same rule:** +18.6% and +5.7% with it, +36.0% and +16.4% without it.
  E101's held-out-by-price score is the 7 loop cells only, **3.2% rms**. The first figure, 7.1% over 9 cells, is superseded.
- **Sparse parity's op cycles are priced twice:** about 447 cycles an op sit inside both the tensor price and the
  scratchpad-load price. That is 3.3-4.9% of each solve's forecast. Priced once, J a solve over idle given its seconds
  reads **-5.9 / -7.2 / -7.8 / -6.1%**, not -1.7 / -2.5 / -3.3 / -2.9%.
- **E136's L3 row was not zero in the difference,** as its frozen label said. It added -0.12 W to each format, because its
  zeros column is aifoundry3's and its random column aifoundry2's. Without it: fp32 -2.6%, fp16 +2.4%, int8 -9.6%
  (frozen: -3.3%, +1.7%, -11.5%).
- **FREEZE.md's "no constant was fitted to any of the seven loads" is false:** E101 is in sample for `w_set` and the L2
  stream price, and M10 was fitted on E86's and E95's rows. See [`FREEZE.md.dated-note-1.md`](FREEZE.md.dated-note-1.md).

**Held out, not blind.** The form, every constant and every prediction were frozen in [`frozen-v2.json`](frozen-v2.json) and
[`predictions-v2.json`](predictions-v2.json) and committed with their hashes ([`SHA256SUMS-freeze`](SHA256SUMS-freeze),
[`FREEZE.md`](FREEZE.md)) before any score was computed. `score_ledger_v2.py` refuses to run if those bytes change. But all three
held-out loads were measured in September, and their measured values were known before the freeze. FREEZE.md names the two
rules set during the build.

## Results

**1. The three held-out loads, beside v1's committed scores** ([`scores-v2.json`](scores-v2.json) › `summary`; v1's figures
recomputed from [`../2026-10-26-load-model/scores.json`](../2026-10-26-load-model/scores.json) to the last digit):

| load | what is scored | v1 (26 Oct) | **v2** | v2's bias | v2 inside its own band |
|---|---|---:|---:|---:|---|
| E39, the gemv sparsity ladder, three cards | three slopes and three intercepts, W | 1.10 W rms | **0.69 W rms** | +0.26 W | 4 of 6 (1 of 3 slopes inside the measurement's 99% interval) |
| E37, mmbench fp32 from DRAM, three cards | W over the pre-launch idle | 2.14 W rms (+23-27%) | **1.17 W rms** (+13-14%); post hoc for the awake rule: 2.40 W rms without it | +1.17 W | 3 of 3 |
| E59, sparse parity, four runs on aifoundry3 | W over idle, leak-corrected | 3.02 W rms (13-39% low) | **0.75 W rms** (3.7-7.4% low) | -0.72 W | 4 of 4 |

**2. Joules, scored twice: given the measured seconds (tests prices and counts) and with the seconds forecast (the whole
ledger), each over idle and with the card at rest** (error, forecast over measured):

| load | J over idle, given seconds | J over idle, seconds forecast | J with the card at rest, given | J with the card at rest, forecast |
|---|---|---|---|---|
| E59, a solve (L1, L2, (256,5) halves) | -1.7, -2.5, -3.3, -2.9% | -4.9, -2.5, -4.6, -4.5% | -2.1, -1.7, -0.9, -0.7% | **-14.4**, -1.8, -6.0, -6.0% |
| E37, an op (aifoundry2, aifoundry3, card 1) | +14.0, +13.0, +13.5% | the same | +3.4, +3.7, +1.3% | +10.1, +9.4, +7.5% |

- E59's seconds are the host's own cycle model (`plan.json` › `model_s`, fitted on the same kernel's runs of the same day): on L1 it
  is 16.6% short, and that carries straight into the joules with the card at rest.
- E37's forecast seconds are the DRAM's: 2,048 B an op over 1,024 minions at the catalogue's 76 GB/s, 16,556 cycles an op against
  15,267-15,404 measured.
- E37's joules over idle do not depend on the seconds, because v2 prices that load wholly per op and per byte.
- E37's T0 is the run's mean die (`die_c_mean`), which the run itself raised, and the ledger adds the forecast rise on top.
  So J with the card at rest counts the rise twice. With the run's starting die (`die_c_start`) as T0, given its seconds, it
  reads +2.4 / +3.3 / +1.4% (post hoc), against +3.4 / +3.7 / +1.3% as frozen.
- E59's watts are scored against each record's catalogue cross-check (`board.catalogue.over_idle_w`), and its joules
  against the record's headline (`board.j_per_solve`). For one run the two reductions differ by 1.3-4.8%, which is why the
  W and J errors of one forecast differ. v1 was scored the same way.
- E59's joules carry a double count. Each op's cycles are inside both the tensor price and the scratchpad-load price, about
  447 hart-0 cycles an op more than the hart spends: 0.07 / 0.29 / 0.57 / 0.50 J a solve, 3.3-4.9% of each forecast.
  Priced once (post hoc), J a solve over idle given its seconds reads -5.9 / -7.2 / -7.8 / -6.1%. A later ledger should
  subtract one price's awake share wherever an op overlaps its own loads.
- E39 runs the resident loop at its fixed 546 cycles an op, so it has no second score.

**3. Where sparse parity's joules go, by the ledger** (given seconds; `predictions-v2.json`):

| run | J a solve | tensor ops | scratchpad bytes | hart 1's generation | epilogue and set-up | awake, waiting | other bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| L1 | 1.63 | 21% | 48% | 9% | 10% | 10% | 1% |
| L2 | 6.04 | 24% | 54% | 10% | 3% | 9% | 1% |
| (256,5) first half | 12.19 | 23% | 53% | 11% | 3% | 10% | 1% |
| (256,5) second half | 15.36 | 16% | 45% | 22% | 3% | 13% | 1% |

- The terms v1 lacked (hart 1's generation, the epilogue and set-up, and the awake time) carry 21-37% of each run
  (29.6 / 21.2 / 23.7 / 37.4%; desk arithmetic of the frozen ledger, `posthoc-v2.json` › `e59_terms_v1_lacked`).
- The second half carries the most, 37%, and it is where v1 missed by 39%.
- *Post hoc, a cross-check only:* the scratchpad term, 0.79 / 3.28 / 6.44 / 6.98 J, sits beside each run's own SRAM-rail reading
  over idle, 0.79 / 2.89 / 5.80 / 6.94 J a solve (`energy.json` › `rails.sram_w.j_per_solve`).

**4. Beside them, on one chart** ([`chart-v2.html`](chart-v2.html), drawn by `chart_ledger_v2.py` from
[`chart-data-v2.json`](chart-data-v2.json), which carries every number's source and label):

| load | label | v2 |
|---|---|---|
| E101, the resident loop on aifoundry3 | held out by price: M10's kernel term on a session M10 never saw (6 cells and the e37 loop cell) | **7 cells, 3.2% rms** |
| E101, the DRAM arm (`mmp64`) | **post hoc for the awake rule** (set after arithmetic beside this arm); the catalogue's DRAM row held out | zeros **+18.6%**, random +5.7%; without the rule +36.0%, +16.4% |
| E101, the L2-streamed benchmark arm | **in sample**: v2's L2 streaming price is E101's own post hoc path cost | 7 cells, 3.4% rms; e37's kind -8.2% |
| E136, the 4,096³ GEMM on aifoundry2 at 800 MHz | held out, not blind; **random minus zeros only** (the card at rest and the clock's static part cancel). *Dated correction, post hoc:* the L3 row's share is not zero (-0.12 W) | fp32 -3.3%, fp16 +1.7%, int8 -11.5% as frozen; corrected post hoc -2.6%, +2.4%, -9.6% |
| E86, real tensors, aifoundry3 | M10 held out by kind (its float scale reads each session's own random anchors) | 12 kinds, 0.18 W rms |
| E95, real tensors, aifoundry3 | the same | 33 kinds, 0.14 W rms |

**In plain words.** The ledger now gets sparse parity close: 1.7-3.3% low on joules over idle given its seconds, against v1's
13-39% low on watts. Part of that closeness is a double count: priced once, the op cycles leave it 6-8% low (post hoc).
- What fixed it is the checkpoint's gap 5: the second hart's row generation, each output tile's 1,606-cycle epilogue and the
  time a running hart waits. The instruction catalogue prices all three from counts.
- The other change: the bytes are priced at the scratchpad's measured prices, with a counted 2 KB an op where v1 assumed an
  unbracketed 4 KB.

E37 halves its miss, from +23-27% to +13-14%, but stays high on all three cards. *(Corrected account, fix-q166:)*
- The halving comes from the awake rule. It prices none of a hart's wait inside its own DRAM loads as awake. The rule was
  set during the build after arithmetic beside E101's DRAM arm, the same benchmark streaming from DRAM, so E37 is post
  hoc for it. Without the rule, E37 reads +27.3 to +28.0% an op, no better than v1.
- The data change (mmbench fills its tiles with {-2, -1, 1, 2}, not random numbers) and the counted bytes move it little
  on their own.
- What remains, +13-14% with the rule, is **the DRAM row's price or the byte count (2,048 B assumed, bracket 1,024-2,048)**.
  E37's measured 15,267-15,404 cycles an op move about 1,888-1,905 B at 76 GB/s, or 2,048 B at about 82 GB/s. With every
  other input frozen, 1,773-1,790 B an op would zero v2's miss on each card. E101's DRAM arm, the same benchmark on a
  later day, misses the same way, worst on zeros (+18.6%).

E39's slopes land within 6%, and the intercepts move from v1's hard zero gate to the zeros anchor.
- Its aifoundry3 intercept reads 1.15 W high.
- E39's own record says its reduction reads that card 0.81-1.34 W low at its launch temperature
  ([`03-experiments.md`](../../../findings/03-experiments.md), E39, caveats), so read that row with the caveat; the score
  keeps it.

## The ledger

[`tools/ledger/ledger_v2.py`](../../../../tools/ledger/ledger_v2.py), standard library only:

```
J_total     = P_idle(card, T0) t  +  k_leak(card, T0) dT t  +  J_over_idle
J_over_idle = sum_ops (Z_f + D_kind) / R_f v2              M10's kernel term: the zeros anchor and M10's D, per op
            + sum_class hart-cycles x r_issue x e_class v2  instruction-bound hart time (an epilogue, a generator)
            + awake hart-cycles x e_awake v2                a running hart that waits on another
            + sum_paths bytes x (z + (r - z) phi)           phi = w_set rho/0.5 + (1 - w_set) tau/0.5 (E101's set bits)
            + bytes x hops x p_hop                          the mesh
dT = k_rise x P_over_idle;  v2 = (V / V_600)^2;  every term carries a band [lo, hi]
```

| term | from | label |
|---|---|---|
| Z_f, the zeros anchor a format's loop pays per op | E78 (aifoundry3), E82 (card 1), the 21 Sep session (aifoundry2, fp32) | measured |
| D, the data's price per op | M10's leave-one-kind-out predictions (`rows-m10.json` › `err_w`); card 1 its own rows; aifoundry2 = aifoundry3 / 0.963 (E38) | M10, held out by kind |
| small-integer operands (E39's [-3, 3], E37's {-2, -1, 1, 2}) | the mean of M10's predictions for its three nearest kinds, their spread in the band | a hand choice, stated |
| bytes | energy manual §4.1 per card, zeros and random; §4.2's L3; E101's post hoc L2 stream cost | measured; the L2 stream post hoc |
| phi, the set-bit form | E101's R5 and R5b: a constant costs the path 0.21-0.31 of random's increment, so w_set 0.55-0.83 (0.70) | post hoc (E101) |
| instructions | the vector-integer class median of §3.1 per card, at its measured issue rate 0.37 a hart-cycle | measured; their use for busy cycles a hand choice |
| awake | the stalled-minion figure, 1.19 W per 1,024 harts [1.01, 1.92] (§2, §7.3) | measured; its use a hand choice |
| the card at rest | the footing law per card (FL1-FL6, c14e5f35) inside its band; E66's split (aifoundry2) and the manual's per-card laws outside | registered law; measured |
| the run's own heating | M10's 4.5 s window law, 0.12 °C a W [0.09, 0.20] | registered law, carried to aifoundry2 by hand |
| a hart's time is priced once | the catalogue measured each byte and op with its issuing hart awake, so only waits on another hart are priced as awake | a rule (FREEZE.md), set after arithmetic beside E101's DRAM arm: E37 and E101's DRAM arm are post hoc for it; sparse parity's op cycles still sit inside two prices (dated note above) |

**What a counter (step 2) would replace.** Every count here was written down by hand or by the planner:
- E59's op, output-tile and row-tile counts are exact: the planner's geometry, ported, reproduces `plan.json`.
- E59's hart cycles by activity are the cycle model's fitted constants times those counts; a counter's instructions by class
  would replace them, and the issue-rate assumption with them.
- E59's bytes (2 KB of tensor loads an op, S KB staged a row tile) are counted from the kernel's description; the card's own
  shire-cache counters would confirm them.
- E37's 2,048 B an op from DRAM is bracketed to 1,024; the DRAM side's read counters would settle it.
- E136's 384 B a minion-op beyond the L2 is E136's own desk count, frozen before E136 ran.

## What this does to predicting power and heat

| quantity | before (v1, 26 Oct) | after (v2, held out, not blind) |
|---|---|---|
| a whole program that is not a matmul (sparse parity), W over idle | 3.02 W rms, 13-39% low | **0.75 W rms**, 3.7-7.4% low |
| the same, J a solve over idle, given its seconds | 13-39% low | **1.7-3.3% low** (6-8% low with its op cycles priced once, post hoc) |
| the same, with its seconds forecast | not scored | 2.5-4.9% low (with the card at rest: 0.7-2.1% given; 1.8-14.4% forecast) |
| a matmul streamed from DRAM (E37), W over idle | 2.14 W rms, 23-27% high | **1.17 W rms, 13-14% high**, post hoc for the awake rule (2.40 W rms without it) |
| a resident ladder (E39), six line parameters | 1.10 W rms | **0.69 W rms** |

**Not touched:** M10 (used as frozen), the heat laws, the governor. v2 has no model of a governed clock. At 800 MHz it scores
only differences.

## What this cannot say

- **Not blind.** The scored measurements predate the freeze. The blind test is the checkpoint's step 4: four programs, forecast
  in the lab repo before a card runs, and that needs the owner's go.
- **Seconds are the weak half.** E59's cycle model is 16.6% short on L1, and the tensor unit alone, at 318 cycles an op, would
  run sparse parity 2.4-5.2 times faster than it does. v2 forecasts no program's time from its counts; the counter's cycles are step 2's.
- **The awake and issue prices are hand choices**, each bracketed: a waiting hart at the stalled-minion figure, and a busy one at
  0.37 issues a cycle. The bands are boxes, the sum of each term's band, and they are wide: L1's is [1.31, 2.88] J.
- **The DRAM row reads high** at E37's and E101's stream rates, and v2 does not correct it. Doing that with E37's or E101's
  numbers would make those scores in sample.
- **aifoundry2 has no M10 family.** Its D is aifoundry3's over E38's 0.963, and its fp16 and int8 zeros anchors are placeholders
  used only where they cancel.
- **The awake rule is post hoc for E37 and E101's DRAM arm** (dated corrections above). The blind day is its first fair test.
- **E37's residual is the DRAM row's price or the byte count.** The two are not separated: the DRAM side's read counters
  (system call 10) would count the bytes. E37's count bracket (1,024-2,048 B) is not in its band.
- **E37's T0 is the run's mean die,** so its J with the card at rest counts the run's rise twice (above).
- **Smaller points, none of which moves a headline:**
  - L1 and L2 start at 51 C, 1 C below aifoundry3's footing band (52-66 C), so their rest law is the exponential one: 0.29 W
    below the footing law extended to 51 C.
  - E39's rungs carry no J total.
  - E136's J total, which is not scored, uses the 600 MHz idle law at 800 MHz.
  - E136 prices no L2-side path: about +0.70 W in each format if its 384 B a minion-op were priced at the L2 stream price.

## Builds on

Under the stock-take's rule for lanes (CONTEXT § 45, MAP § 3).
- **(1) Checked:** the stock-take's inventory was read on Thu 12 Nov 2026. Public rows read: L06 (the energy manual), L10 (the idle
  slopes), H04 (Q126(c)'s joined model), H07 and H08 (E78-E125, E95 and E101 among them), H15 (Q139(u)'s footing), H19 (E136) and
  H21 (M10).
- **(2) Used:**
  - L06: §1-§4.2 and §3.1.
  - H21: `m10.json` and `rows-m10.json`.
  - Every piece was read at `726a6b64`, the freeze's `repo_head_at_freeze`.
  - H07: E78's and E82's zeros anchors.
  - The footing law: `c14e5f35`.
  - L10: E66's split.
  - H08: E101's R5/R5b and its post hoc path cost (labelled).
  - E136's desk count.
  - The sparse-parity planner and cycle model: `workloads/sparseparity/tools/cycle_model.py`.
  - Each check against an earlier measurement of the same quantity is the score above.
- **(3) Not used:**
  - the 21 Sep flip prices (replaced, as the recipe asks);
  - v1's per-kernel offset c0 (disputed in v1's own README);
  - E43's hop slope;
  - E39's own rail voltage;
  - E37's measured int8 cycles for E59;
  - the archive.
- **(4) Tiers:** public pieces only. No NDA-tier check was made for this file.
- **(5) Readiness:** not a registration. Nothing here gates a card.

## Files

| file | what |
|---|---|
| `frozen-v2.json` | the form and every constant, each with its source path and its label (frozen) |
| `predictions-v2.json` | every load's inputs, counts, ledger terms and bands (frozen) |
| `FREEZE.md`, `SHA256SUMS-freeze` | the freeze and its hashes, committed before any score |
| `scores-v2.json` | every scored number: measured, its source, forecast, band, error, label, v1 beside; frozen labels kept as `label_frozen` where a dated correction replaced them |
| `posthoc-v2.json`, `FREEZE.md.dated-note-1.md` | the dated corrections of fix-q166, every figure post hoc, from the frozen model (`tools/ledger/posthoc_ledger_v2.py`) |
| `chart-data-v2.json`, `chart-v2.html` | the one chart's data (every number's source) and the chart, self-contained |
| `tools/ledger/` | `ledger_v2.py` (the model), `freeze_ledger_v2.py`, `loads_ledger_v2.py`, `score_ledger_v2.py`, `posthoc_ledger_v2.py`, `chart_ledger_v2.py` |

Re-run from the top of the tree:

```
/usr/bin/python3 -I -B tools/ledger/score_ledger_v2.py
/usr/bin/python3 -I -B tools/ledger/posthoc_ledger_v2.py
/usr/bin/python3 -I -B tools/ledger/chart_ledger_v2.py
```

The score refuses to run unless the frozen files match `SHA256SUMS-freeze`. All six scripts need only the standard library.
The files here were written by Python 3.9 (the lab's `/usr/bin/python3`). From Python 3.12, `sum()` rounds differently in
the last digit, so a few floats differ there.

SPDX-License-Identifier: Apache-2.0
