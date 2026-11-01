# V3-KSPEED E96: the speed of more real tensors under aifoundry2's own governor, and whether real int8 sustains differently (Q132)

*Pre-registered Sun 1 Nov 2026 (week 44), before the first launch. This commit freezes the design ([`protocol.json`](protocol.json), order from
[`make_protocol_e96.py`](make_protocol_e96.py)), the predictions ([`predictions.json`](predictions.json), sha256 `fd01c53203ede4eb49be45bf775e284a6ff9ba3913d466204dbc387e788e9f25`), the analysis
code ([`reduce_e96.py`](reduce_e96.py), self-test [`selftest.txt`](selftest.txt)) and the decision rules. Any change after it goes in Amendments at the end, dated, before the data it touches. E96 starts from
Q132(r)'s real2 tiles and frozen predictions ([`predictions-real2.json`](../../kinds/real2/predictions-real2.json), sha256 `0957e0c295990ac95cded56430697fb0683c9cf451d90f6943c8ff8d6a0b021a`, commit `6ae4c3d5`), and from E87's
design, anchors and data; each input is cited by sha256 in [`predict_e96.py`](predict_e96.py). Every time in this experiment is epoch ms: the box's clock goes back at 02:00 PDT tonight.*

**The ask** (the owner, Sat 31 Oct 2026, about 23:30 PDT): *"Continue closing issues which are still open in https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers … and run proper experiments on aifoundry."*
This is the speed half of item 3 of that page's section 11: more real tensors, a layer with exact zeros, other int8 calibrations, an fp16 forward pass, and several sustained runs per kind for real int8.

**The questions.**

1. **Does the ReLU tiles' lower power buy clock, as E83's relation says, in the burst and sustained?** Q132(r) predicts about 800 MHz in the burst against random data's 708–731, and 703–800 MHz sustained against 602–612 ([`claims.E96`](../../kinds/real2/predictions-real2.json) S2, S2b).
2. **Do real tensors with no exact zeros still run at random data's speed, beyond GPT-2?** E87 had three GPT-2 tiles. Here GPT-2's layers 3 and 9, BERT and ViT (S3). ResNet-18, VGG-16 and T5-small's ReLU tiles carry zero words, so they are question 1's; T5's `l0_up` has no zero word but its weights sit on the bf16 grid, and ViT's last block is 55% −0.0; each is reported apart.
3. **Does real int8 sustain any differently from random int8?** E87 left it open: its three real int8 tiles sustained 793.6–800 MHz and int8 full 774.7, one run each, and E80 and E83 show single int8 full runs land on either side of the 65 °C trip whatever the data. The kinds page asks for several sustained runs per kind. The new tiles do not test this, so E96 adds its own arm, frozen below before any data.

## Design

**Card and instrument, as they are.** aifoundry2, card 0, release 1.4.0 / BL2 0.22.0 as read on 27 October, the same card, binaries and kernel as E80, E83 and E87. DVFS 600, 700 and 800 MHz; static TDP 65 W; software threshold 65 °C. **Nothing is set on the card.** No governor, TDP, threshold or clock set. No `--reset-ms`: this run tests the governor's power loop, and the statistics reset restarts the running average that loop acts on. Read-only `ettelem config` at the two ends of the card time under the lock with `timeout 10`, and, because the runner is E87's unchanged, after every run, ending the session unless TDP and threshold both read 65. The service processor's trace ring and residencies after every run, as E80 and E87 keep them.

**The runner is E87's.** [`run_e96.py`](run_e96.py) imports [`../run_kspeed.py`](../run_kspeed.py) (itself E64's [`run_hpl.py`](../../hpl/run_hpl.py) plus `file:` tiles) and runs it unchanged, with E87's one extension: a `file:` value may also name a tile of `tools/claims-v3/kinds/real2/tiles/` or `tools/claims-v3/kinds/real/tiles/`, checked before the session against the sha256 frozen in that folder's predictions file and tiles file, each itself sha256-checked. The lock, the other-user checks, the sampler (10 Hz), the safety stops (85 °C; 97 W on three samples) and the config check are E64's code. The kernel is E64's, E80's, E83's and E87's: `sparsity_host --test fma --pattern none --values file:<tile>`, aifoundry2's `build/sparsity_t2`, not rebuilt. As for every kind, a `file:` run checks no arithmetic.

**The tiles.** Q132(r)'s 25 tier-1 tiles (burst all; sustained 11 of them), E87's six anchors (fp32 randn, fp32 zeros, fp16 randn, fp16 zeros, int8 full, int8 zeros), and E87's three real int8 tiles (`l0_mlp_up`, `l6_mlp_down`, `l6_attn_qk`, Q130(n)'s, sustained only). Tier 2's five tiles and E86's fp16 and int8 `l6_mlp_down` reruns do not run here: `e96_suggested` leaves them out, and E87 ran those two.

**The blocks** ([`protocol.json`](protocol.json), `order_seed` 96; E80's, E83's and E87's shapes exactly):

| block | runs | start | load | scores |
|---|---|---|---|---|
| `SMOKE` | 75 s of the idle card with no launch (its last 60 s are the rest reading), then one 2 s launch each of fp32 `vgg16_fc2`, fp16 `t5small_l0_down`, int8 `gpt2_l11_down_maxabs`, the three gating levels | none | | not analysed: it checks the tiles on the card |
| `BURST` | 31 tiles × 2 passes, each pass shuffled: 62 runs | die reading ≤ 55 °C | one 6 s process | burst clock, p800, burst W, die, the burst limit, the kernel's rate, the switching term c |
| `SUS` | 34 runs in the fixed order below | die reading ≤ 57 °C | nine back-to-back 8 s processes, about 76 s | the last 40 s: clock, board W, die, rate, the limit labels |

**The sustained order**, fixed by [`make_protocol_e96.py`](make_protocol_e96.py) from its own seed, shuffled inside each group except G3, written out in `protocol.json`:

| group | runs |
|---|---|
| R1 | the arm's round 1: `l6_mlp_down`, `l6_attn_qk`, `l0_mlp_up`, int8 full |
| Ga | fp32 `resnet18_l3c1`, fp16 randn, fp16 `t5small_l0_down`, fp32 randn |
| R2 | round 2: `l0_mlp_up`, `l6_mlp_down`, `l6_attn_qk`, int8 full |
| Gb | fp16 `vgg16_fc2`, fp16 zeros, fp32 `resnet18_l2c1`, fp32 `t5small_l0_down`, int8 zeros |
| R3 | round 3: `l6_attn_qk`, `l0_mlp_up`, int8 full, `l6_mlp_down` |
| Gc | fp32 `vgg16_fc2`, fp32 randn again, fp16 `resnet18_l3c1`, fp16 randn again |
| R4 | round 4: `l6_mlp_down`, int8 full, `l0_mlp_up`, `l6_attn_qk` |
| G3, if the clock allows | fp32 `t5small_l0_up`, fp32 `vit_l11_down`, fp32 `bert_l6_up`, fp16 `vit_l5_down`, fp32 zeros, in that order |

*Why this order.* A round stays whole and contiguous, so its pairing removes the session's slow drift, and the shuffle inside it removes the order. The rounds are spread through the block so they replicate over the session rather than over five minutes. S2b's gated tiles are spread over Ga, Gb and Gc, and each format's two randn runs sit in Ga and Gc, so the references span them. G3 comes last because no frozen rule names its runs, and in `sustained_first`'s own order, so a time cut takes that list's tail first.

**The budget, and what was cut, before any data.** The slot is 75 minutes and the plan may be about 65 card-minutes. At E87's rates (14.5 s a burst, 99.7 s a sustained run, gates included), the smoke takes 1.7 min, the bursts 15.0, and each sustained run 1.66. `e96_suggested`'s 23 sustained runs and the arm's 15 more would be 38 runs and 80 card-minutes.

- **`sustained_first` is cut from its tail: its last four, `int8/vgg16_fc2`, `int8/vgg16_fc2_asym`, `int8/gpt2_l11_down_maxabs` and `int8/gpt2_l11_down_p999`, get no sustained run.** They burst like every tier-1 tile. So S1's sustained half, S4 and S5's sustained half hold no int8 tile. They are all predicted at 799–800 MHz with the limit `none`, so they would have said little, and the arm covers int8 sustained.
- **The arm gets four rounds, not three.** The power table below says why: with 2 degrees of freedom t is 4.30 and a true +21 MHz at σ 9.2 MHz reads `DIFFERENT` 26% of the time; with 3 it is 3.18 and 47%.
- **The plan is 29 sustained runs: the four rounds (16), the seven gated tiles (S2b's six and fp32 `resnet18_l2c1`) and six anchor runs (each randn twice, fp16 and int8 zeros), about 65 card-minutes in all. G3's five come after it and run only if the clock allows**, about 8 more minutes at E87's rates, and the gated tiles' shorter gates should give some of that back.
- If the card comes free late, the time cut takes G3 first. Nothing else is decided by the clock.

**The slot, the queue, the claim.** E96 is one of three experiments on this card tonight under one `#community-lab` claim, E98's lane's message `1566355908076765257`. E96 makes no post and no release. E98's lane wrote the slot to `~/claude/work/q132-a2-slots.txt` on the box: **start 1793527500 (10:05 UTC = 02:05 PST), end 1793532000 (11:20 UTC = 03:20 PST)**, 20 min before E98's next rest reading. [`queue_e96.py`](queue_e96.py) runs detached on the box and needs no ssh:

- it launches nothing before the slot's start; it then waits, taking no lock, until E98's `status.json` says no probe is running, the card lock is free, `et-who` names no holder and nobody else is logged in, and gives up at the slot's end minus 25 min;
- it records `sensors -j`, `uptime`, `ettelem config` and the last 40 min of the box's own 5 s history before anything of ours touches the card;
- it runs the smoke and checks it: exit 0, every launch rc 0 and ok, 546 / 546 / 318 cycles per op, 65 W / 65 °C. A failed check ends the queue with no session;
- it runs the session with `--max-card-min` set so the runner ends by itself 3 min before the slot's end (exit 0, the end queries run). As a last resort at the slot's end minus 120 s it touches the session's stop-file, and at minus 30 s it sends SIGTERM; a device process is never signalled. Then it records the same snapshot again;
- a session cut short is reduced as far as it got, and a rule below its population is UNDER-RESOLVED. A session that ends for another user's login is not resumed.

**The rest readings and the die line**, because E98 is testing tonight whether the line follows the room, and E96's session sits between its probes P2 and P3:

- **The last 60 s of the smoke's no-launch run**, 10 Hz, just before the first launch. **It is not a true rest.** P2's hold ends about 09:54–10:05 UTC, so the card is minutes from a five-minute hold. The queue does not delay the first launch for it: 15 minutes of rest would cost nine sustained runs, and P2's and P3's own rest readings bracket E96's session, 35 and 20 minutes either side.
- **E98's rest rule on the box's own history** at three moments, the first launch, P2's and P3's, labelled: the board W over the 20 min before the moment, a row within 10 min after a busy one left out, the raw die, the NIC and the NVMe beside it. Before the first launch it will have few rows or none, and that is the point of the rule. A rest die's changes are W / 0.2315, E98's way: only differences mean anything there.
- **The session's die line**: OLS of die against board W over all sustained runs (E87's form), its shift at E80's slope, and **E98's line**, `die − 0.4573 W`, per run, over the four kinds E96 shares with E98's gated line (fp16 zeros, int8 zeros, int8 full, fp32 randn) and over all runs, with its trend through the session. E87's same-kinds value is frozen at 41.665 °C. All labelled: E96 scores no rule on them, and E98's own rules are E98's.

**Etiquette.** The lab repo's `AGENT.md` §4–§7. No build or heavy host load during any probe: this tree's `git pull` happens outside E98's probes and E100's slot, and nothing under `build/sparsity_t2`, `build/ettelem-hpl` or `tools/claims-v3/kspeed/e98` is touched. The lab dashboard's collector and keeper are left alone, as in E64 and E87: the runner holds the card lock, which they honour.

## Predictions (frozen)

[`predict_e96.py`](predict_e96.py) builds [`predictions.json`](predictions.json) and [`predictions.txt`](predictions.txt) from committed inputs only, each refused unless its sha256 is the one frozen in the script. **There is no new model in E96.** Every predicted clock is Q132(r)'s: E83's registered relation (burst W* 66.15 W, σ 2.75; sustained W* 49.75 W, σ 1.95) on Q132(r)'s predicted switching term, with the intervals Amendment 1's rule built. The script checks that the relation on each frozen c reproduces the frozen burst and sustained points to 0.05 MHz, and refuses otherwise. The tile-by-tile table is [`predictions.txt`](predictions.txt) and the [real2 README](../../kinds/real2/README.md) §5.

**What the predictions rest on, and what they do not cover.** Each predicted power is Q130(n)'s post-hoc predictor, whose terms are not mechanisms. The step from aifoundry3's D to aifoundry2's c is E83's conversion; E83-S2 found measured c above its narrow intervals on eight gated synthetic kinds and below on two, so question 1's tiles are exactly where it is least tried. The relation assumes E80's heat path, and E87's session ran 0.5 °C warmer than that, while tonight's room is cooling, so a sustained cell can move for that alone; arm (a-adj E96) reads it. **The clock rules on no-zero tiles do not test the power predictor**, as E87's correction C1 found: their clocks sit within a few MHz of random data's, and a baseline with no model scores as well. It is tabulated beside them. S2 and S2b do test a large predicted effect.

**The arm's expectations, labelled, not rules** (`arm.expected`). E83's relation on E87's measured c gives real tiles 796.6 MHz and int8 full 787.5, **+9.1 MHz**, or **+14.0 MHz** at E87's warmer W*. At a fixed 800 MHz the c difference gives board W **−2.11 W** and die **−0.96 °C**. A colder room moves the whole int8 row toward the cap, and the clock difference toward 0.

## Decision rules (frozen; `reduce_e96.py` implements them)

**Definitions** (E80's, E83's and E87's, unchanged). A run's **burst clock** is the mean sampled clock from 1.5 s after the first launch to the end of the work; a **burst cell** is the mean of its two passes. A **sustained cell** is the mean clock over the last 40 s of the work, averaged over the kind's runs. **Board W, die °C, p800, TFLOPS / TOPS, the measured switching term c and the measured sustained limit** are E80's (`reduce_kspeed.burst_extra`, `sus_limit`, imported unchanged). A tile's c is the mean of its two bursts' c. Idle-reset dips are kept in the registered numbers; A1's reset-free view sits beside them.

**Q132(r)'s claims, as frozen** (`claims.E96`; the quoted rule is the frozen text; each is scored on this session's cells):

| rule | frozen text | population here |
|---|---|---|
| **E96-S1** | "bursts: count inside `burst_scoring_interval_mhz`, sustained: count inside `sus_scoring_interval_mhz`; each PASS if >= 80% of the tiles run, FAIL if < 60%, else INCONCLUSIVE" | 25 bursts, 11 sustained |
| **E96-S2** | "per tile, burst minus the same session's randn burst of its format: PASS if every tile >= +40 MHz, FAIL if any tile < +15 MHz, else INCONCLUSIVE" | fp32 and fp16 `resnet18_l3c1`, `vgg16_fc2`, `t5small_l0_down` |
| **E96-S2b** | "per tile, sustained minus the same session's randn sustained of its format: PASS if every tile >= +50 MHz, FAIL if any tile < +15 MHz, else INCONCLUSIVE" | the same six |
| **E96-S3** | "per format, the tiles' mean burst minus randn's: PASS if \|difference\| <= 15 MHz in both formats, FAIL otherwise" | fp32 `gpt2_l3_mlp_down`, `gpt2_l9_attn_qk`, `bert_l6_up`, `vit_l5_down`; fp16 `gpt2_l9_attn_qk`, `bert_l6_up`, `vit_l5_down` |
| **E96-S4** | "count of sus_limit right: PASS if >= 80% of the tiles run, FAIL if < 60%, else INCONCLUSIVE" | the 11 sustained tiles; right only if every run carries the predicted label, as E87-R2 |
| **E96-S5** | "burst and sustained rms each <= 15 MHz: PASS; either > 25 MHz: FAIL; else INCONCLUSIVE" (E83's relation on each tile's measured c) | 25 bursts, 11 sustained |

**How the frozen text is read, stated before the data.**
- S1 reads PASS when both halves pass, FAIL when either fails, else INCONCLUSIVE, as the real2 README's table says (≥ 80% "of bursts and of sustained").
- `claims.conventions` says "Fewer than 3 kept passes: NOT SCORED", but it opens "All energy claims…", and `e96_suggested` gives two burst passes and one sustained run. E96's claims name no interval over passes, so they are scored on the cells as E87's were. The arm's rules below do use intervals, and they keep the three-pass floor.
- "A lane that drops a tile says so, and a claim short of its population is UNDER-RESOLVED, never PASS": the four int8 tiles dropped from sustained are named above. The minimum populations are frozen here (`minimum_population`): S1 and S5, 20 bursts and 7 sustained; S4, 7 sustained, which is the plan's 7 without G3. S2, S2b and S3 need every named tile and its randn, but a FAIL the measured tiles already force stands. S5's rms below its population is UNDER-RESOLVED.
- int8's burst scoring interval is the single point 800 MHz, so a cell with a pass the idle reset hit lies outside it, as in E87; A1's reset-free count sits beside S1.

**This lane's own rules, citing `predictions-real2.json` by sha256 and moving none of its claims.**

- **E96-T, the sessions tie.** Each anchor's burst and sustained cell lies within **25 MHz** of the mean of the earlier sessions' cells (E80 where it ran, E83, E87; each beside it; 12 rows, at least 9). The mean, because single sustained runs land either side of the trip whatever the data: E87's single int8 full run read 774.7, and a cool night's 800 would sit 25.3 from it. A failure means the card or the room moved, not that a model did.
- **E96-I1, real int8 against random int8, the clock: the rule the kinds page asks for.** A **round** is one sustained run each of int8 full and the three real tiles. It counts when all four runs finished with nine processes back rc 0. With F_r int8 full's sustained clock in round r and T_r the mean of the three real tiles', **d_r = T_r − F_r**. The statistic is the mean of d_r, its interval **t(0.975, n − 1) × sd(d_r) / √n** over whole rounds, with n the whole rounds: fewer than 3 is NOT SCORED. **A difference that counts is ±15 MHz**: E87-S2's and S3's bar, about 2% of 800 MHz, and smaller than E87's single-run +21 MHz, the thing at issue. The verdict is the interval's place against 0 and ±15:

  | the 95% interval | verdict | says |
  |---|---|---|
  | wholly above +15 or wholly below −15 | `DIFFERENT_BEYOND_BAR` | real int8 sustains differently, by more than counts |
  | excludes 0, reaches past ±15 | `DIFFERENT` | a difference is shown, its size not resolved against the bar |
  | excludes 0, inside ±15 | `DIFFERENT_SMALL` | a difference is shown, smaller than counts |
  | holds 0, inside ±15 | `SAME_WITHIN_BAR` | no difference that counts |
  | holds 0, reaches past ±15 | `INCONCLUSIVE` | **one card's run-to-run spread cannot say** |

  If every run of every kind reads limit `none`, the result also carries **`at_the_cap`**: nothing tripped, so a `SAME_WITHIN_BAR` says nothing about the trip's edge, only that on this night's heat path neither reached it.
- **E96-I2, the board W**, the same pairing on the last 40 s: `BELOW` (interval wholly under 0), `ABOVE`, or `INCONCLUSIVE`. **E96-I3, the die**, the same. I2 and I3 say whether real int8 runs cheaper and cooler in the sustained state; a thermal hold on int8 full lowers its watts, so they can read smaller than the fixed-clock expectations above.

**What the rule can do at one card's spread** (simulation in `predict_e96.py`, seed 96, `arm.power`; one run's σ from E83 C3's clamp and slope classes and from the int8 full runs of E80, E83 and E87; the true difference 0, the relation's +12 or E87's +21; full's mean 785 MHz, clamped at 800):

| σ of one run | rounds | median half-width at true 0 | true 0: SAME / INCONCLUSIVE | true +12: DIFFERENT / INCONCLUSIVE | true +21: DIFFERENT / INCONCLUSIVE |
|---|---|---|---|---|---|
| 5.6 MHz | 3 | 13 MHz | 39% / 57% | 33% / 56% | 60% / 35% |
| 5.6 MHz | **4** | 9 MHz | 71% / 24% | 57% / 28% | 86% / 9% |
| 9.2 MHz | 3 | 21 MHz | 12% / 83% | 14% / 77% | 26% / 68% |
| 9.2 MHz | **4** | 15 MHz | 26% / 69% | 24% / 64% | 47% / 47% |
| 15.6 MHz | 3 | 32 MHz | 4% / 90% | 7% / 87% | 10% / 84% |
| 15.6 MHz | **4** | 22 MHz | 7% / 88% | 9% / 82% | 15% / 77% |

**So `INCONCLUSIVE` is the most likely verdict unless the card sits near the clamp.** That is a statement about the spread. If it comes back inconclusive, that will be reported as it stands, with the interval. The planning σ is an estimate; if it is wrong, so is this table, and the verdicts stand as scored.

**Labelled, never a verdict:** A1's reset-free view of every clock rule; the frozen D-propagated ranges beside S1; the gate law's clocks and c beside (a)'s, tile by tile; a **no-model baseline** (each tile = same-session random data of its format) beside the rms of the frozen points and of the relation on measured c, by group; the like-with-like ratios, (c − c_zeros) / (c_ref − c_zeros), against E78's measured ratio and the gate law's; the sustained differences of the no-zero tiles from randn; the burst limits. For the arm: each real tile alone against full; the clock with dips left out; **E98's fine W** at 800 MHz, the mean of the 800 MHz samples with each dip and the 3 s after it left out, since at a fixed clock W is a thermometer with 0.01 W steps (a run the trip holds gets no such reading: the board W is a running average that lags the clock, so its 800 MHz samples read low, as E87's int8 full did at 51.35 W against E80's 53.17); the share at 800; a **pooled two-way interval** (clock = kind + round + error, the contrast on (kinds − 1)(rounds − 1) df, which is narrower and assumes equal spread on and off the clamp); the limit labels; the run-to-run sd. For the heat path: the die line, E98's line and its trend, **(a-adj E96)** (E87's a-adj on E96's anchor runs: W*_adj = 49.75 − Δ / 0.4349, on the frozen c and on the measured c), the rest readings, the idle resets per process, the gates' holds.

## What a result fills

For each real2 tile, the cells of the blog's kinds-of-numbers table that E80, E83 and E87 filled: burst and sustained MHz, TFLOPS or TOPS, board W, die °C, the limit and the switching term. It answers the three questions above in plain words, or says it could not. The data goes to [`docs/reports/data/2026-11-01-e96-real-tensors-speed/`](../../../../docs/reports/data/2026-11-01-e96-real-tensors-speed/). It narrows item 3 of the kinds page's section 11 (E95 is the energy half) and gives E98's item 9 one more line reading at a known place in the night.

## Files

| file | what |
|---|---|
| `make_protocol_e96.py`, `protocol.json`, `protocol-dry.json` | the blocks, the tiles, the gates, the caps, the sustained order; the dry run's short shape, the same order |
| `run_e96.py` | the runner: E80's `run_kspeed.py`, imported unchanged, plus the real-tile check and a dry-run power table |
| `queue_e96.py` | the detached queue: the slot, the look before launching, the smoke and its check, the session, the stops |
| `predict_e96.py`, `predictions.json`, `predictions.txt` | the frozen predictions (Q132(r)'s, gathered and checked), `claims.E96` verbatim, the arm's numbers and power table |
| `reduce_e96.py`, `selftest_e96.py`, `selftest.txt` | the registered reduction, and its test on hand-made cells and rounds |
| `tables_e96.py` | formats `results.json` into the data folder's `tables.md` and `cells.json`; it decides nothing |

Run, on aifoundry2, from the lab checkout, once the slots file exists:

```bash
setsid nohup python3 tools/claims-v3/kspeed/e96/queue_e96.py --slots ~/claude/work/q132-a2-slots.txt --runs build/e96/runs > build/e96/queue.out 2>&1 < /dev/null &
python3 tools/claims-v3/kspeed/e96/reduce_e96.py <data>/s1 --smoke <data>/smoke --history <data>/history.jsonl.gz --rest-at first_launch=<ms> p2=1793525400000 p3=1793533200000 --out <data>/results.json > <data>/reduce.txt
python3 tools/claims-v3/kspeed/e96/tables_e96.py <data>/results.json --cells <data>/cells.json > <data>/tables.md
```

The dry runs on a toy card (no device, on the mini, `protocol-dry.json`) exercised the queue from the slot's start to its end, the smoke's check, all 62 bursts and 34 sustained runs in their short shape, the time cut, the hard stop, the refusal of a slot too near the next rest reading, and `reduce_e96.py` and `tables_e96.py` on the result; the toy card's clocks are not a prediction. `reduce_e96.py` also ran on E87's committed session, where it reproduces E87's cells and die line: the rules read UNDER-RESOLVED there, as they should.

## Amendments

None.

## Results (added after the data, Sun 1 Nov 2026; nothing above changed)

[`docs/reports/data/2026-11-01-e96-real-tensors-speed/`](../../../../docs/reports/data/2026-11-01-e96-real-tensors-speed/README.md). The session ran 02:05–03:15 PST, all 96 runs in 70.3 card-minutes with the smoke, G3 included. S1, S2, S2b, S3, S4, S5 and T all PASS. I1 reads `SAME_WITHIN_BAR` (+6.1 MHz, 95% [−0.8, +13.1], four rounds), I2 and I3 `BELOW`. One expectation above was wrong: the 60 s rest reading was a true rest, because E98's P2 ended early, and the data README says so.
