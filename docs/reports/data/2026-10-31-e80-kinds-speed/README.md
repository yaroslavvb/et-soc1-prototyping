# E80 data: the speed of each kind of number under aifoundry2's own governor (Q130, Sat 31 Oct 2026)

Eighteen kinds of numbers on aifoundry2 card 0, under the card's own governor:

- fp16: zeros, ones, randn, sparse50, smallint, fp8grid, nn_like;
- int8: zeros, neg_ones, full, smallint, gauss_q, sparse50;
- fp32: randn, bf16trunc, sparse90, smallint, nn_like.

Each kind got a **burst on a cool die**, run twice, and a **sustained run** of about 76 s. **Nothing was set on the
card**: the TDP and the threshold read 65 W and 65 °C at all 57 per-run reads of `ettelem config` (and the smoke's
three), at the session's start and end, and once more at the close under the card lock, just before the release.

The pre-registration is [`tools/claims-v3/kspeed/`](../../../../tools/claims-v3/kspeed/README.md) (`10f58581`,
pushed 12:20:43 PDT). Its frozen predictions are
[`predictions.json`](../../../../tools/claims-v3/kspeed/predictions.json), sha256 `69a62b31…`, built from Q130(c)'s
freeze (`2bbe03dd`) and amendment A1 (`320f3fdd`) and the kinds spec (`7d9c0d9e`). E80's own amendment A1 (`075b691e`,
12:34:36) was written during the sustained block. The card was claimed in `#community-lab` at 12:21:13 and released by
editing the same post at 13:03.

| session | PDT | what |
|---|---|---|
| `smoke/` | 12:21:30–12:21:51 | three 2 s `file:` launches (fp16 ones, int8 full, fp32 randn): cycles per op 546.0 / 318.0 / 546.0, config 65 W / 65 °C; not analysed |
| `s1/` | 12:22:12–13:02:42 | the registered session, 57 runs, exit 0, **40.5 card-minutes** (40.8 with the smoke, of the 90 allowed): `BURST` 36 runs (12:22–12:29), `SUS` 21 runs (12:29–13:02) |

## Results first

### 1. One registered rule of nine passes

**What passes.** The cool-die burst prediction (E80-R1): kind → predicted watts → E64's governor holds within E69's
25 MHz bar.

**What fails.** Every sustained rule, the power check on aifoundry2 (S1), and the two that hang on the governor's
idle-reset glitch (R7's 800 MHz clause, and S2).

- **The card's heat path moved** since E64's 23 Oct session. This matters most: it moved the cells that sit near the
  thermal trip.
- The **power model over-predicts the low-entropy fp32 kinds**.
- The governor's **idle reset fired inside two bursts**.

Each failure is scored exactly as registered ([`results.json`](results.json) `rules`, [`reduce.txt`](reduce.txt)).

| rule | verdict | what the data say |
|---|---|---|
| **E80-R1** burst rms ≤ 25 MHz, against E64's registered governor fed Q130(c)'s predicted watts | **PASS** | **21.7 MHz** over 18 kinds. Against E64-T1's burst it is 28.1, and against Q130(c)'s own 4–12 s numbers 27.0 |
| **E80-R2** the sustained limit (none / thermal / power) called right for ≥ 80% of kinds | **FAIL** | 13 of 18 (72%). Four int8 kinds (full, smallint, gauss_q, sparse50) were predicted thermal and held 789–797 MHz, `none`. fp16 ones was predicted thermal: one run read `none`, one `thermal`. All 13 others were right |
| **E80-R3** fp16 ones sustained within 15 MHz of E64-T1 | **FAIL** | **781.6 MHz** (792.9 and 770.3), against **745.2** predicted: **+36.4 MHz**. E64 measured 737.1 on 23 Oct; E64-T1's out-of-sample number was 754.5 |
| **E80-R4** E64's own cells within 25 MHz (the drift check) | **FAIL** | the fp32 randn burst +2.1 MHz; sustained fp32 randn +4.3, fp16 zeros −4.6, fp16 randn +9.0, int8 zeros 0.0. But **fp16 ones +44.5** and **int8 full +30.2**: the two cells inside the clamp window |
| **R7** (Q130(c)) burst within 25 MHz for ≥ 70%, and every predicted-800 cell ≥ 790 | **FAIL** | 13 of 18 within 25 MHz (72%, passes), but int8 neg_ones read 777.5 (755.1 and 800). The 755.1 pass was an idle reset (§3d) |
| **R8** (Q130(c)) sustained thermal-vs-power right for every cell, and within 40 MHz for ≥ 70% | **FAIL** | 13 of 18 limits right (the five R2 misses); 13 of 18 within 40 MHz (72%, passes) |
| **E80-S1** measured switching term c inside the converted 95% interval for ≥ 70% of out-of-sample kinds | **FAIL** | 8 of 12. **All four fp32 kinds fell outside**: bf16trunc 19.11 W (predicted 24.27, interval 20.70–27.85), smallint 15.18 (18.52, 16.07–20.96), nn_like 14.04 (17.15, 14.24–20.06), sparse90 2.23 (1.89, 1.57–2.20). All eight fp16 and int8 kinds were inside their wider intervals |
| **E80-S2** E64's governor on each burst run's own measured powers, rms ≤ 10 MHz | **FAIL** | 15.7 MHz over 34 runs. It is **2.65 MHz** without the two idle-reset bursts (post hoc, §3d) |
| **E80-S3** sustained rms against E64-T1 at γ 3 ≤ 15 MHz | **FAIL** | **35.8 MHz** over 18 cells. Sixteen of 18 cells read at or above the prediction; the two below are fp16 zeros (−10.2 MHz) and int8 neg_ones (−3.1), both predicted at 800 |

### 2. The speeds: what each kind of number gets on this card

The burst is the mean clock from 1.5 to 6.5 s of a 6 s run from a die reading ≤ 55 °C; both passes are given. The
sustained figure is the last 40 s of nine back-to-back 8 s processes, about 76 s in all; where a kind ran twice, both
runs are given. Rates are the kernel's own operations over its own wall time. p800 is the board's power at 800 MHz in
the first second after reaching it. The sustained W and die are the means over the last 40 s.

The last column is **derived**, not measured on its own: board pJ/op is the sustained board W over the sustained
kernel rate. It is whole-board energy, idle and lane power included. From [`tables.md`](tables.md):

| format | kind | burst MHz | burst rate | p800 W | burst limit | sustained MHz | sustained rate | board W | die °C | limit | board pJ/op |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 | randn | 711.9 (715.7 / 708.0) | 10.69 TFLOPS | 82.7 | power | 604.3 (608.4 / 600.3) | 9.27 TFLOPS | 54.2 | 66.0 | thermal | 5.85 |
| fp32 | bf16trunc | 774.0 (776.5 / 771.4) | 11.71 | 69.5 | power | 639.1 | 9.70 | 51.7 | 65.7 | thermal | 5.33 |
| fp32 | nn_like | 760.8 (721.6 / 800.0) | 11.65 | 59.8 | none | 700.0 | 10.56 | 52.5 | 65.5 | thermal | 4.97 |
| fp32 | smallint | 800.0 (800 / 800) | 12.28 | 61.3 | none | 690.8 | 10.44 | 52.5 | 65.5 | thermal | 5.03 |
| fp32 | sparse90 | 800.0 (800 / 800) | 12.28 | 35.5 | none | 800.0 | 12.28 | 36.8 | 58.0 | none | 3.00 |
| fp16 | randn | 730.6 (746.9 / 714.3) | 21.95 TFLOPS | 76.1 | power | 609.5 | 18.68 TFLOPS | 52.3 | 66.0 | thermal | 2.80 |
| fp16 | fp8grid | 773.2 (776.5 / 770.0) | 23.37 | 69.8 | power | 661.5 | 19.98 | 54.2 | 65.6 | thermal | 2.71 |
| fp16 | smallint | 782.7 (787.8 / 777.6) | 23.82 | 66.9 | power | 650.6 | 19.71 | 51.9 | 65.6 | thermal | 2.63 |
| fp16 | nn_like | 780.0 (784.0 / 776.0) | 23.70 | 68.0 | power | 665.2 | 20.12 | 54.7 | 65.6 | thermal | 2.72 |
| fp16 | sparse50 | 800.0 (800 / 800) | 24.55 | 59.9 | none | 717.1 | 21.62 | 54.9 | 65.5 | thermal | 2.54 |
| fp16 | ones | 800.0 (800 / 800) | 24.55 | 50.7 | none | 781.6 (792.9 / 770.3) | 23.83 | 53.2 | 64.8 | none / thermal | 2.23 |
| fp16 | zeros | 800.0 (800 / 800) | 24.55 | 34.6 | none | 789.8 | 24.23 | 35.1 | 57.7 | none | 1.45 |
| int8 | full | 800.0 (800 / 800) | 84.30 TOPS | 48.9 | none | 793.4 (796.7 / 790.0) | 83.54 TOPS | 53.2 | 64.9 | none | 0.64 |
| int8 | gauss_q | 800.0 (800 / 800) | 84.31 | 48.0 | none | 794.4 | 83.70 | 52.1 | 64.6 | none | 0.62 |
| int8 | smallint | 798.0 (800 / 796) | 84.31 | 46.2 | none | 795.4 | 83.80 | 51.0 | 64.4 | none | 0.61 |
| int8 | sparse50 | 800.0 (800 / 800) | 84.30 | 46.8 | none | 789.3 | 83.15 | 49.0 | 63.6 | none | 0.59 |
| int8 | neg_ones | 777.5 (755.1 / 800.0) | 81.68 | 39.4 | none | 796.9 | 83.98 | 41.0 | 60.0 | none | 0.49 |
| int8 | zeros | 800.0 (800 / 800) | 84.30 | 34.8 | none | 800.0 | 84.33 | 37.0 | 58.0 | none | 0.44 |

How to read it:

- **On a cool die only the power test acts.** Every kind that stepped down in a burst logged a *power* throttle-down
  first, and no burst logged a thermal one. Those kinds are fp32 randn and bf16trunc and fp16 randn, fp8grid,
  smallint and nn_like. Their p800 is 66.9–82.7 W, against the 65 W level.
- **In sustained work only the thermal test acts.** No sustained run's last 40 s carries a single power label. Every
  kind that settles below 800 does so on the thermal test, at a die mean of 65.2–66.0 °C.
- **Speed by kind.** On the same matmul and clock table:
  - fp32 sustains 604 MHz on random normals, 639 on bf16-truncated mantissas, 691–700 on small integers and NN-like
    data, and 800 on 90%-sparse data.
  - fp16 sustains 610 on random, 651–665 on small-integer, fp8-grid and NN-like data, 717 on 50%-sparse, and 782–790
    on constants.
  - int8 holds 789–800 MHz on **every** kind. Even its random data draws only about 53 W sustained, and on today's
    cooling its die stays at 63.6–64.9 °C, under the trip.
- **The interval.** A burst cell is two independent passes; those agree to 0–33 MHz except where an idle reset fell
  in one (§3d). A sustained cell is one run except fp16 ones, fp32 randn and int8 full. Those three replicated to
  22.6, 8.1 and 6.7 MHz. fp16 ones sits right at the trip, so a small change in the die decides how much of the 40 s
  is spent at 800.

### 3. What the misses are made of (post hoc, labelled; no verdict changes)

**(a) The card's heat path moved since 23 October.** The post-hoc die line over E80's 21 sustained runs is
**die = 42.23 + 0.4349 °C per W** (rms 0.56 °C). It reaches 65.5 °C at **53.5 W**, against E64's 50.3 W. At E64's
own slope the line sits **1.38 °C lower** (`results.json` `posthoc.die_line_e80`). The idle die read 45–47 °C at about
22 W this session, against 49–51 °C on 23 Oct. That is why the cells inside the clamp window moved, while the
clamped cells and the burst did not:

- fp16 ones moved +44.5 MHz and int8 full +30.2;
- fp32 randn's burst moved +2.1 MHz;
- the sustained clamps (fp32 and fp16 random at 600, the zeros at 800) moved by −4.6 to +9.0 MHz.

**This is E69's failed drift check showing up again**, and Q130(c) flagged it (its README, item 7).

**(b) The power model over-charges low-entropy fp32 data.** E80 measures the switching term c on aifoundry2 with
E64's own method, and for the fp32 kinds Q130(c) predicted it too high:

| kind | measured c | predicted c | measured share of random's switching over zeros |
|---|---|---|---|
| fp32 bf16trunc | 19.11 W | 24.27 W | 0.733 |
| fp32 smallint | 15.18 | 18.52 | 0.570 |
| fp32 nn_like | 14.04 | 17.15 | 0.523 |

For bf16trunc, Q130(c)'s model saved 4% against randn (A1's E70 arm saved 7%). E80 measures **27%**. fp16
smallint, fp8grid, nn_like and sparse50, and int8 smallint, gauss_q and sparse50, are also all below their point
predictions, by 0.7–3.4 W, but inside their wider intervals. On the calibration kinds the model is right to within 0.35 W:

- fp16 randn 23.07 W against 23.28;
- fp16 ones 9.70 against 9.70;
- int8 full 8.98 against 9.10;
- fp32 randn 25.55 against 25.21.

int8 neg_ones (a constant) reads 3.54 W against the frozen 2.68: the int8 lanes-on cost is higher than frozen, in
E79's direction.

One caveat on every kind that holds 800 MHz in its burst, which includes all six int8 kinds: its c rests on the
800 MHz point plus one or two ramp samples at 600 and 700. So its two passes disagree by up to 1.4 W (int8 gauss_q
8.48 and 7.09; int8 zeros 2.82 and 2.16). The power-limited fp16 and fp32 kinds dither through all three points, and
their passes agree to 0.2 W. The sustained board power corroborates the int8 ordering at a common clock and die
(about 795 MHz, 64.4–64.9 °C): smallint 51.0 W and gauss_q 52.1 W against full's 53.2 W. So int4-range data draws
about 2 W less than full-range int8 here, although the kinds spec counts as many operand-bit flips for it (kinds.json
`kinds.int8.smallint`). That is two passes and one sustained run; E78 measures it at a pinned clock.

**(c) Splitting the sustained miss.** E64-T1 at γ 3, re-run post hoc (`results.json` `posthoc`):

| E64-T1 run on | sustained rms over 18 cells |
|---|---|
| the frozen inputs (E80-S3) | 35.8 MHz |
| the measured c | 19.8 MHz |
| E80's own die line | 16.7 MHz |
| **both** | **9.2 MHz** |

E64-T1's out-of-sample figure on E64's own cells was 6.2 MHz. With both fixes it puts **fp16 ones at 779.6 MHz
against 781.6 measured (−2.0)**. That is the cell E64-T1 was said never to close. It closes once the session's own
thermal path is used. The int8 kinds come out at 793–800 MHz, against 789–800 measured.

So the governor-and-heat model itself holds up. What failed is its inputs: Q130(c)'s fp32 power for low-entropy
data, and a die line measured on another day. One caution on the 9.2 MHz: E80's die line is fitted on these same 21
sustained runs, so the thermal path in that row is in sample, and only the governor and the leakage law are being
tested out of sample there.

**(d) The governor's idle reset, inside a launch** (amendment A1, [`posthoc-idle.txt`](posthoc-idle.txt),
[`posthoc-idle.json`](posthoc-idle.json)). Five times in 225 work processes (2.2%), the clock fell from 800 MHz
straight to 600 MHz while the work ran on. There was no power or thermal line, but a POWER_IDLE power-status record
in the ring. The clock climbed back about 1 s later. That is E63's rate: 8 in 360,
[`14-card-behaviour.md`](../../../findings/14-card-behaviour.md) "A one-second idle reset inside a launch". It fell
twice in bursts (int8 neg_ones and fp32 nn_like, pass 1 each) and three times in sustained runs. One burst, fp32
nn_like pass 1, also waited 2.2 s at 600 MHz before its first climb.

With those samples set aside (post hoc):

- the burst rms is 19.5 MHz;
- no predicted-800 cell reads below 790, so R7's second clause would hold;
- the governor-only rms (S2) is **2.65 MHz** over 34 runs. That is better than E64's in-sample 3.3 MHz, on kinds it
  never saw.

R2 is unchanged at 13 of 18 by this view: the limit misses are the heat path, not the glitch.

### 4. Predicted against measured

The full table, with E64-T1's burst, Q130(c)'s own numbers and c against its interval, is in [`tables.md`](tables.md)
("Predicted against measured"). Each kind's prediction and its sources are under `kinds.<type>/<kind>` in
[`predictions.json`](../../../../tools/claims-v3/kspeed/predictions.json).

## What it changes

**For the blog's kinds table:**

- every cell of burst MHz, sustained MHz, TFLOPS/TOPS, board W, die °C and the limiting test for these 18 kinds, on
  one card in one session (`cells.json`);
- the two-limits story, confirmed across formats: on a cool die, the power test acts; in sustained work on this
  card's cooling, the thermal test acts;
- int8's whole range of kinds bursts at 800 MHz and sustains 789–800 MHz.

**Three new findings for the explanation:**

1. **Narrower precision buys real power.** fp32 with bf16-truncated mantissas draws 27% less switching power than
   random fp32, and gets 62 MHz more burst clock and 35 MHz more sustained.
2. **The sustained speed of a borderline kind depends on the room.** fp16 ones read 737 MHz on 23 Oct and 782 MHz on
   31 Oct, while the power-limited burst anchor (fp32 randn) moved 2 MHz.
3. **The governor occasionally resets mid-launch** (2.2% of processes), costing a 6 s burst up to ~80 MHz of mean
   clock.

**For the Horace hub:**

- Status item 9 ("fp16 and int8, and the fp16 all-ones sustained cell"): **measured.** The speeds of seven fp16 and
  six int8 kinds now exist, burst and sustained.
- The fp16 all-ones cell: E64-T1's frozen prediction missed by +36.4 MHz. Post hoc, the model closes the cell to −2.0 MHz on
  the measured power and the session's own die line (that line fitted on the same runs), so the open part is the
  drifting heat path, not the governor model.
- Levels stop 1 ("a temperature term that closes"): the same post-hoc reading, 9.2 MHz rms over 18 new cells. To
  make it a prediction, a future run must measure the die line in the same session, before scoring. E80 shows that
  23 Oct's line is 3 W off today.

## Card state and etiquette

- aifoundry2 card 0, release 1.4.0 / BL2 0.22.0 (E69's reading).
- At the start, `et-who` read *"No process holds an ET-SoC-1 device node or card lock"*, and `who` showed no
  logins.
- The runner held the card lock for each session. The lab dashboard's collector and keeper kept to it, as with
  E64 and E69: nothing of theirs was stopped.
- The final read-only `ettelem config` under the lock, at about 13:03, gave `tdp_w 65`, `temp_threshold_c 65`,
  `low_power`, 600 MHz, 519 mV. `et-who` was free afterwards.
- Safety stops: none. The hottest die-mean sample read 67 °C (hottest sensor 69 °C), and the highest board sample
  was 88.1 W, in the first seconds of a sustained fp32 randn run on a cool die. The stops are 85 °C and 97 W.

## Departures, dated

- **Registered at `10f58581`:** every kind's burst ran twice, not only the anchors'. The sustained replicates were
  fp16 ones, fp32 randn and int8 full.
- **A1 (`075b691e`, during the SUS block):** the idle-reset view of §3d, post hoc.
  [`posthoc_idle.py`](../../../../tools/claims-v3/kspeed/posthoc_idle.py) as committed at A1 lacked the S2 view that
  A1's text names. That view was added after the data were in; nothing else in the script changed. It is post hoc
  either way.
- **The box's checkout.** aifoundry2's lab checkout was at `20c4249f`. E73 had left untracked copies of
  `tools/claims-v3/hlf/` there, which blocked a fast-forward. They were **moved, not deleted**, into an ignored
  backup folder under `build/`. Six are byte-identical to the tracked files; `lockin_hlf.py` differs and is kept.
  The checkout was then pulled to `10f58581`, and the runner, tiles, binaries and predictions were verified by sha256
  there before the claim.

## Files

| path | what |
|---|---|
| `s1/`, `smoke/` | the sessions as run (E64's layout): `session.json` and `kspeed.json` (the code's and every tile's sha256), `runs.jsonl`, `launches.jsonl.gz`, `tel/<run>.jsonl.gz` (10 Hz, no `--reset-ms`), `sp/<run>.bin` (the trace ring, read with `tools/claims-v3/hpl/sptrace_full.py`), `queries.jsonl`, `marks.jsonl`, `manifest.txt`, `run.log`, `run.out`, `end.json` |
| `results.json`, `reduce.txt` | `reduce_kspeed.py`: per-run metrics (E64's `reduce_hpl.run_metrics`), per-kind cells, every rule, the post-hoc arms |
| `posthoc-idle.json`, `posthoc-idle.txt` | `posthoc_idle.py` (amendment A1) |
| `tables.py`, `tables.md`, `cells.json` | formatting only: the README's tables and the blog's kinds-table cells, read from `results.json` and `predictions.json` |

Rebuild (any machine with Python 3; no third-party modules):

```bash
cd docs/reports/data/2026-10-31-e80-kinds-speed
python3 ../../../../tools/claims-v3/kspeed/reduce_kspeed.py s1 --out results.json > reduce.txt
python3 ../../../../tools/claims-v3/kspeed/posthoc_idle.py results.json s1 --out posthoc-idle.json > posthoc-idle.txt
python3 tables.py results.json ../../../../tools/claims-v3/kspeed/predictions.json --cells cells.json > tables.md
```
