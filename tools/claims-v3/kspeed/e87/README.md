# V3-KSPEED E87: the speed of real GPT-2 tensors under aifoundry2's own governor (Q130)

*Pre-registered Sat 31 Oct 2026 (week 44), in the evening, before the `#community-lab` claim and before the first
launch. This commit freezes the design ([`protocol.json`](protocol.json)), the predictions
([`predictions.json`](predictions.json), sha256 `025f4e15950e75c3b21ea405ea15f04487cd1e56db4a7b308b19aa2ab7565ae8`),
the analysis code ([`reduce_e87.py`](reduce_e87.py)) and the decision rules. Any change after it goes in Amendments at
the end, dated, before the data it touches. E87 starts from Q130(n)'s real tiles and frozen predictions (`7d5b99af`)
and its Amendment 1 (`99620cc2`), and from E83's design, relation and data (`c253bd1c`, `6f02f1bc`, `734e997f`); each
input is cited by sha256 in [`predict_e87.py`](predict_e87.py).*

**The ask** (the owner, Sat 31 Oct 2026, about 08:40 PDT): *"… The goal is to collect material for blog follow-up,
fully explain the speed/heat/power issues of multiplying varying kinds of numbers. Run experiments on aifoundry …"*;
in the evening, *"feel free to keep using the lab"*. In Q130's plan this is **E87**: the real tensors' speed under
aifoundry2's own governor, with **no governor move**, in E80's and E83's frame.

**The question.** E80 and E83 measured the burst and sustained clock of all 51 synthetic kinds of numbers on aifoundry2.
A critic asked the obvious next thing: what do *real* numbers do? Q130(n) cut nine tiles from GPT-2 small (three
products, each in fp32, fp16 and int8) and froze, before any card ran them, their power and the clocks E83's
power-to-clock relation gives for that power. E87 measures those clocks, on the same card, with the same runner,
kernel, run shapes and gates, with E80's anchors repeated in the session.

## Design

**Card and instrument, as they are.** aifoundry2, card 0, release 1.4.0 / BL2 0.22.0. DVFS 600, 700 and 800 MHz at
0.517, 0.568 and 0.618 V; static TDP 65 W; software threshold 65 °C. **Nothing is set on the card.** The runner reads
`ettelem config` after every run, holding the card lock with `timeout 10`, and ends the session unless the TDP and the
threshold both read 65. The session's first and last queries read it too, and a read-only `ettelem config` under the
lock closes the card time. **No `--reset-ms`**: the sampler never sends the statistics reset (E85 C1), as in E80 and
E83.

**The runner is E80's.** [`run_e87.py`](run_e87.py) imports [`../run_kspeed.py`](../run_kspeed.py) (itself E64's
[`run_hpl.py`](../../hpl/run_hpl.py) plus `file:` tiles) and runs it unchanged, with one extension: a `file:` value may
also name a tile of Q130(n)'s real-tile folder, `tools/claims-v3/kinds/real/tiles/<type>/`, checked before the session
against the sha256 frozen in Q130(n)'s `predictions-real.json` and `real.json` (both themselves sha256-checked). Every
anchor tile is checked by `run_kspeed.py`'s own code against `kinds.json`. The lock, the other-user checks, the sampler
(10 Hz), the trace-ring reads, the safety stops (85 °C; 97 W on three samples) and the config check are E64's code.

**Kernel: E64's, E80's and E83's, unchanged.** `sparsity_host --test fma --pattern none --values file:<tile>`,
aifoundry2's `build/sparsity_t2` binaries (host `7adadf4f…`, kernel `990807f4…`, checked by sha256 in
`session.json`). Hart 0 of each of the 1,024 minions repeats one 16×16 TensorFMA on the tile pair in its L1
scratchpad; 546 / 546 / 318 cycles per op for fp32 / fp16 / int8. A `file:` run checks no arithmetic.

**The tiles: Q130(n)'s nine, and E80's six anchors.**

| format | real tiles (Q130(n), sha256) | anchors (`kinds.json` revision 2) |
|---|---|---|
| fp32 | `l0_mlp_up` `6d592ffe…`, `l6_mlp_down` `fa0270cb…`, `l6_attn_qk` `3bfdf870…` | randn, zeros |
| fp16 | `l0_mlp_up` `52199639…`, `l6_mlp_down` `193c36e9…`, `l6_attn_qk` `b3b46443…` | randn, zeros |
| int8 | `l0_mlp_up` `2734a6f4…`, `l6_mlp_down` `3af027ef…`, `l6_attn_qk` `50879e49…` | full, zeros |

`l0_mlp_up` is layer 0's MLP up-projection (A = the `ln_2` output, B = `c_fc`'s weight), `l6_mlp_down` layer 6's MLP
down-projection, `l6_attn_qk` layer 6's attention QKᵀ (real q and k). The anchors are the ones the brief names "E80's":
fp32 randn, fp16 randn, int8 full and one zeros per type. Five are E80 kinds and tie to E80's cells; fp32 zeros was
first run by E83 and ties to E83's cell. They tie the session to E80 and E83 (E87-R5), give the like-with-like
references (randn, int8 full and the zeros, S2–S4) and give the heat path's drift (arm a-adj E87). They are not scored
with the nine.

**The blocks** ([`protocol.json`](protocol.json), order seed 87; E80's and E83's shapes exactly):

| block | runs | start | load | scores |
|---|---|---|---|---|
| `SMOKE` | fp32 `l6_attn_qk`, fp16 `l0_mlp_up`, int8 `l6_mlp_down`, 2 s each | none | one 2 s process | not analysed: it checks the real tiles on the card |
| `BURST` | 15 tiles × 2 passes, each pass shuffled | die reading ≤ 55 °C | one 6 s process | burst clock, p800, burst W, die, the burst limit, the kernel's rate, the switching term c |
| `SUS` | 15 tiles, plus fp32 randn and fp16 randn again (17 runs), shuffled | die reading ≤ 57 °C | nine back-to-back 8 s processes, about 76 s | the last 40 s: clock, board W, die, rate, the limit labels |

That is 47 runs. E83 took 12.3 s per burst and 93 s per sustained run, and E87's mix runs hotter (most of its 15
sustained tiles are thermal-held), so the plan is about **34 card-minutes** (30 × ~13 s + 17 × ~100 s). The cap is
**38** for the main session (`caps.max_card_min`) and **40 in all**, the smoke included (`--max-card-min 2`). The
session starts by 21:45 PDT and ends by 22:30 PDT, or it is not started. A session the cap cuts short is reduced as far
as it got; a rule below its population is UNDER-RESOLVED.

**Why fp32 randn and fp16 randn twice.** They are the same-session references the real fp32 and fp16 tiles are
compared with (S2's sustained difference, labelled; the like-with-like ratios of S3 and S4 use the bursts), and two of
the sustained anchors of arm a-adj E87. One sustained run's 1 σ is ±15.6 MHz on the slope and ±5.6 MHz at a clamp
(E83's corrections-check C3), so a reference run twice halves the reference's share of a difference's variance.

**Etiquette.** The card is claimed in `#community-lab` with one line, after this commit is pushed and before the
smoke, with the planned time and its end (`for 1 h, until ~HH:MM PDT`); the same post is edited at the release. The
runner refuses when another user is logged in or another process holds the card, and before every launch process; it
caps every launch and config read at `timeout 10`, and stops its sampler with SIGTERM at each run's end (E83's
correction C8). The lab dashboard's collector and keeper are left alone, as in E64, E69, E80 and E83: the runner holds
the card lock, which they honour.

## Predictions (frozen)

[`predict_e87.py`](predict_e87.py) builds [`predictions.json`](predictions.json) and
[`predictions.txt`](predictions.txt) from committed inputs only, each refused unless its sha256 is:

- `bab33bee…` Q130(n)'s `predictions-real.json` (the frozen points: c, burst and sustained clocks, shares, limits);
- `f32e8a90…` Q130(n)'s `amendment-1.json` (the scoring intervals, the D intervals, the like-with-like references);
- `eb36f4cd…` Q130(n)'s `real.json` (the tiles' sha256);
- `97f58c89…` E83's `predictions.json` (E64's B_f and s_f, E83's relation, E80's die line and anchor cells);
- `3717f176…` E83's `results.json` (E83's anchor cells and its same-day heat-path view, W*_adj 49.724 W);
- `9586568f…` `kinds.json` (the anchor tiles).

**There is no new model in E87.** Every predicted clock is Q130(n)'s: E83's registered relation (burst W* 66.15 W,
σ 2.75; sustained W* 49.75 W, σ 1.95; the governor dithering between DVFS points at an effective cap) applied to
Q130(n)'s predicted switching term c for each tile, converted to aifoundry2 as E83 converted (c = c_zeros + D / 1.0187).
The script checks that E83's relation (`predict_e83.Rel`, imported unchanged) on each frozen c reproduces Q130(n)'s
frozen burst and sustained points to 0.05 MHz, and refuses otherwise. **E87 scores against Amendment 1's intervals**
(each D interval propagated through the relation, plus 1.96 × E83's relation rms in quadrature: 10.6 MHz burst,
8.4 MHz sustained, clamped to [600, 800]) and reports the frozen D-propagated ranges beside them.

| tile | c W (amended interval) | burst MHz | scoring | frozen range | sus MHz | scoring | frozen range | share at 800 | limit |
|---|---|---|---|---|---|---|---|---|---|
| fp32 l0_mlp_up | 25.454 (23.09–27.82) | 710.7 | 681.3–740.5 | 691.8–730.0 | 602.5 | 600.0–621.7 | 600.2–611.1 | 0.00 | thermal |
| fp32 l6_mlp_down | 25.367 (23.00–27.74) | 711.5 | 682.1–741.3 | 692.6–730.8 | 602.7 | 600.0–622.1 | 600.3–611.7 | 0.00 | thermal |
| fp32 l6_attn_qk | 25.453 (23.08–27.82) | 710.7 | 681.3–740.5 | 691.8–730.0 | 602.5 | 600.0–621.7 | 600.2–611.1 | 0.00 | thermal |
| fp16 l0_mlp_up | 22.710 (20.40–25.02) | 735.6 | 706.0–767.0 | 719.3–753.4 | 615.0 | 600.0–641.0 | 605.3–629.9 | 0.00 | thermal |
| fp16 l6_mlp_down | 22.360 (20.05–24.67) | 738.9 | 709.2–770.7 | 722.4–757.1 | 617.6 | 600.0–644.4 | 606.8–633.3 | 0.00 | thermal |
| fp16 l6_attn_qk | 22.537 (20.23–24.85) | 737.2 | 707.6–768.8 | 720.8–755.2 | 616.2 | 600.0–642.7 | 606.0–631.5 | 0.00 | thermal |
| int8 l0_mlp_up | 7.905 (6.61–9.20) | 800.0 | 800.0–800.0 | 800.0–800.0 | 796.2 | 775.3–800.0 | 788.7–799.2 | 0.96 | none |
| int8 l6_mlp_down | 7.211 (5.92–8.51) | 800.0 | 800.0–800.0 | 800.0–800.0 | 798.9 | 780.9–800.0 | 795.1–799.9 | 0.99 | none |
| int8 l6_attn_qk | 7.767 (6.47–9.06) | 800.0 | 800.0–800.0 | 800.0–800.0 | 797.0 | 776.7–800.0 | 790.3–799.4 | 0.97 | none |

The burst limit is `power` for the six fp32 and fp16 tiles and `none` for int8 (tabulated, not a rule). **int8's burst
scoring interval is the single point 800 MHz:** a burst cell whose two passes do not both read 800 lies outside it. In
E80 and E83, 27 of 32 int8 burst passes read 800, two read 796 without a reset and three read 751–758 after the
governor's idle reset (E83 C9). A1's reset-free count is reported beside R4.

**The like-with-like predictions** (S3, S4): Q130(n) predicts each tile's switching above its type's zeros as a ratio
of the reference kind's measured on E78 (`amendment-1.json` `like_with_like.ratio_to_ref_measured`): fp32
0.986–0.989 of randn, fp16 0.964–0.980 of randn, int8 0.735–0.835 of full. E87 measures the same ratio on aifoundry2
in one session, (c_tile − c_zeros) / (c_ref − c_zeros), every c from the bursts by E64's method, which cancels the
card's scale and the session's drift. The S3 interval for a tile is Amendment 1's D scoring interval divided by the
reference's E78 D (`like_with_like.S3_ratio_interval` in `predictions.json`; the frozen interval beside it).

**Labelled arm, tabulated, never a verdict: (a-adj E83)**, the sustained relation with W* moved to E83's same-day value
49.724 W (E83 `results.json` `posthoc.a_adj.W_star_adj_w`), on Q130(n)'s c. Q130(n) named it ("E87 may add that as a
labelled arm"); it moves no prediction by more than 0.2 MHz.

**What the predictions rest on, and what they do not cover.** Every predicted power is Q130(n)'s post-hoc predictor,
fitted on E78's 51 kinds only (its open issues 1–3); its terms are not mechanisms. The step from aifoundry3's D to
aifoundry2's c is E83's conversion, whose error is outside the intervals (Q130(n) open issue 4); E83-S2 found the
converted power model wrong for gated kinds, and none of the nine is gated (no zero word in any tile). int8 power is
provisional, as for every int8 kind. The relation assumes E80's heat path; E83 measured it 0.15 °C away later the same
afternoon, and E87's anchors measure it again (R5, arm a-adj E87).

## Decision rules (frozen; `reduce_e87.py` implements them)

**Definitions** (E80's and E83's, unchanged).

- A run's **burst clock** is the mean sampled clock from 1.5 s after the first launch to the end of the work; a tile's
  **burst cell** is the mean of its two passes, and its interval the two passes.
- A **sustained cell** is the mean clock over the last 40 s of the work, averaged over the tile's runs.
- **Board W, die °C, p800, TFLOPS / TOPS, the measured switching term c and the measured sustained limit** are E80's
  (`reduce_kspeed.burst_extra` and `sus_limit`, imported unchanged): `none` if ≥ 90% of the last 40 s reads 800 MHz;
  otherwise `thermal` or `power` by E64 R4's labels at ≥ 50% of the samples below 800; otherwise `unresolved`. A
  tile's c is the mean of its two bursts' c.
- **The nine** are Q130(n)'s real tiles. The anchors are scored only in R5 and used as references in S2–S4.

**Primary rules: Q130(n)'s frozen predictions.**

- **E87-R1, the burst.** The rms over the nine of (measured burst cell − Q130(n)'s frozen burst point) is at most
  **25 MHz** (E69's bar, as E80-R1 and E83-R1). Beside it: the same on A1's reset-free cells, and over the six fp32 and
  fp16 tiles (the ones below the 800 MHz cap).
- **E87-R2, the sustained limit.** Q130(n)'s limit (`none` / `thermal`) is right for at least **7 of the nine**. A tile
  is right only if every one of its runs carries the predicted label; `power` or `unresolved` is wrong.
- **E87-R3, the sustained clock.** The rms over the nine of (measured sustained cell − Q130(n)'s frozen sustained
  point) is at most **25 MHz**. Beside it: the arms, and the rms over the six fp32 and fp16 tiles.
- **E87-R4, Amendment 1's intervals.** At least **7 of the nine** burst cells lie inside their burst scoring interval
  **and** at least 7 of the nine sustained cells inside their sustained scoring interval. Beside it: the counts inside
  the frozen D-propagated ranges, and A1's reset-free burst count.
- **E87-R5, the sessions tie.** Each of the twelve anchor comparisons (six anchors; burst and sustained cell) lies
  within **25 MHz** of its tie cell (E80's for fp32 randn, fp16 randn, int8 full, fp16 zeros, int8 zeros; E83's for
  fp32 zeros). E83's cell is reported beside every row. A failure means the card moved, not that a model did.

**Secondary rules: one link at a time, and the blog's claims.**

- **E87-S1, the relation alone.** E83's relation applied to each tile's **measured** c reproduces the measured clocks
  over the nine: burst rms ≤ **15 MHz** and sustained rms ≤ **15 MHz** (both). It is E83-S1's bar, out of sample on
  real data.
- **E87-S2, real numbers run at random numbers' speed.** In fp32 and in fp16, the mean of the three real tiles' burst
  cells lies within **±15 MHz** of the same-session randn burst cell (both formats). On E83's relation, Q130(n)'s c puts
  the real tiles +1 MHz (fp32) and +5 MHz (fp16) above randn at randn's E80/E83 c; a burst cell's random part is about
  5.3 MHz (E83 C6), so a 95% band for the difference is about ±12 MHz around that.
  The sustained difference and A1's view are reported beside it.
- **E87-S3, the power predictor like with like.** For each of the nine, the measured ratio (c_tile − c_zeros) /
  (c_ref − c_zeros) (ref = randn for fp32 and fp16, int8 full for int8; every c from this session) lies inside its S3
  interval; at least **7 of the nine**. Beside it: the counts inside the frozen ratio intervals, and the measured c
  against Q130(n)'s converted c intervals (frozen and amended), which carry the card-to-card step.
- **E87-S4, Q130(n)'s direction.** The mean of that ratio over a format's three tiles is **below 1** in fp32, **below 1**
  in fp16 and **below 0.9** in int8 (all three). This is Q130(n)'s headline claim: real fp32 and fp16 tensors draw a
  little less switching power than random data, and real int8 clearly less than uniform random int8.

A rule with fewer than 7 of the nine cells (R1–R4, S1, S3), fewer than 9 anchor rows (R5), or without a format's
reference (and, for S4, its zeros) or with fewer than 2 of its real tiles (S2, S4) is UNDER-RESOLVED.

**Labelled, never a verdict:** A1's reset-free view of every burst rule; the frozen D-propagated ranges beside R4;
(a-adj E83); **(a-adj E87)**, the sustained relation with W* moved by the anchors' mean residual from E80's die line,
`W*_adj = 49.75 − Δ / 0.4349` with Δ the mean over E87's anchor sustained runs of `die − (42.233 + 0.4349·W)` (E83's
a-adj, on E87's anchors); the die line refitted on E87's own sustained runs and its shift from E80's; the measured
burst limit against Q130(n)'s; the count of bursts whose first throttle-down was thermal; the idle resets per process;
the sustained replicates' spread.

## What a result fills

For each of the nine real tiles, the cells of the blog's kinds-of-numbers table that E80 and E83 filled for the 51
synthetic kinds: burst MHz and sustained MHz, TFLOPS or TOPS at each, board W (p800, burst mean, sustained mean), die °C
(burst start and peak, sustained mean), the limiting test and the switching term c, with the like-with-like ratios to
random data measured in the same session. The data goes to
[`docs/reports/data/2026-10-31-e87-real-tensors-speed/`](../../../../docs/reports/data/2026-10-31-e87-real-tensors-speed/).

## Files

| file | what |
|---|---|
| `protocol.json` | the blocks, the tiles, the gates, the caps |
| `run_e87.py` | the runner: E80's `run_kspeed.py`, imported unchanged, plus the real-tile check and a dry-run power table |
| `predict_e87.py`, `predictions.json`, `predictions.txt` | the frozen predictions (Q130(n)'s, gathered and checked) |
| `reduce_e87.py` | the registered reduction (per-run metrics from E64's, E80's and E83's code, unchanged) |

Run, on aifoundry2, from the lab checkout:

```bash
python3 tools/claims-v3/kspeed/e87/run_e87.py --protocol tools/claims-v3/kspeed/e87/protocol.json --out build/e87/runs/<s> --dry --only SMOKE   # toy card
python3 tools/claims-v3/kspeed/e87/run_e87.py --protocol tools/claims-v3/kspeed/e87/protocol.json --out build/e87/runs/smoke --only SMOKE --max-card-min 2
python3 tools/claims-v3/kspeed/e87/run_e87.py --protocol tools/claims-v3/kspeed/e87/protocol.json --out build/e87/runs/s1
python3 tools/claims-v3/kspeed/e87/reduce_e87.py <data>/s1 --out <data>/results.json > <data>/reduce.txt
```

The dry run on the Intel's toy card (no device) exercised the smoke, all 30 bursts and the first sustained run before
it was stopped, and `reduce_e87.py` reduced it; the toy card's clocks are not a prediction.

## Amendments

None yet.
