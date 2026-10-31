# V3-KSPEED E83: the speed of the 33 kinds E80 did not run, under aifoundry2's own governor (Q130)

*Pre-registered Sat 31 Oct 2026 (week 44), before the `#community-lab` claim and before the first launch. This
commit freezes the design ([`protocol.json`](protocol.json)), the predictions ([`predictions.json`](predictions.json),
sha256 `97f58c89344dc867b66e28c4ea9e969c4c610865700ea91221fed9c8f4f78cec`), the analysis code
([`reduce_e83.py`](reduce_e83.py)) and the decision rules. Any change after it goes in Amendments at the end, dated,
before the data it touches. E83 starts from E80's data (`c244f148`), Q130(c)'s frozen model (`2bbe03dd`) and the kinds
spec (`7d9c0d9e`); each is cited by sha256 in `predict_e83.py`.*

**The ask** (the owner, Sat 31 Oct 2026, about 08:40 PDT): *"… The goal is to collect material for blog follow-up,
fully explain the speed/heat/power issues of multiplying varying kinds of numbers. Run experiments on aifoundry …"*,
and at about 13:15 the same day: *"feel free to use more cards"*. In Q130's plan this is **E83**: E80's speed design on
every kind E80 did not run, on aifoundry2, with **no governor move**.

**The question.** [E80](../../../../docs/reports/data/2026-10-31-e80-kinds-speed/README.md) measured the burst and
sustained clock of 18 of the 51 kinds in [`kinds.json`](../../kinds/README.md). For the other 33 the blog's speed
column is still a prediction. E83 measures them on the same card, with the same runner, kernel, run shapes and gates,
in one session later the same day. It also asks whether what E80 learned predicts them: E80's own measured relation
between a kind's power and its clock, fed Q130(c)'s predicted power, against Q130(c)'s own frozen clocks.

## Design

**Card and instrument, as they are.** aifoundry2, card 0, release 1.4.0 / BL2 0.22.0 (E69's reading). DVFS 600, 700
and 800 MHz at 0.517, 0.568 and 0.618 V; static TDP 65 W; software threshold 65 °C. **Nothing is set on the card.** The
runner reads `ettelem config` after every run, holding the card lock with `timeout 10`, and ends the session unless the
TDP and the threshold both read 65. The session's first and last queries read it too, and a read-only `ettelem config`
under the lock closes the card time.

**The runner is E80's.** [`run_e83.py`](run_e83.py) imports [`../run_kspeed.py`](../run_kspeed.py) (itself E64's
[`run_hpl.py`](../../hpl/run_hpl.py) plus `file:` tiles checked against `kinds.json`) and runs it unchanged. It adds a
dry-run power table for the new kinds and an `e83.json` record of its own sha256. The lock, the other-user checks, the
sampler (10 Hz, no `--reset-ms`), the trace-ring reads, the safety stops (85 °C; 97 W on three samples) and the config
check are E64's code.

**Kernel: E64's and E80's, unchanged.** `sparsity_host --test fma --pattern none --values file:<tile>`, aifoundry2's
`build/sparsity_t2` binaries (host `7adadf4f…`, kernel `990807f4…`, checked by sha256 in `session.json`). Hart 0 of
each of the 1,024 minions repeats one 16×16 TensorFMA on a tile pair in its L1 scratchpad; 546 / 546 / 318 cycles per
op for fp32 / fp16 / int8, for 8,192 / 16,384 / 32,768 operations. A `file:` run checks no arithmetic and prints the
discarded random fill's metadata (kinds README §1.5); every statistic of a kind comes from `kinds.json`.

**The kinds: the 33 of `kinds.json` (sha256 `9586568f…`, revision 2) that E80 did not run.**

| format | kinds (33) |
|---|---|
| fp32 (13) | zeros, ones, neg_ones, pi, randn_small, randn_large, uniform01, sparse50, pow2, fp16grid, a_randn_b_zeros, a_zeros_b_randn, randn_sorted |
| fp16 (10) | neg_ones, randn_small, uniform01, sparse90, wsparse50, wsparse90, a_randn_b_zeros, a_zeros_b_randn, pair_half_zero, randn_sorted |
| int8 (10) | ones, pos, ternary, sparse90, wsparse50, wsparse90, highbit, a_full_b_zeros, a_zeros_b_full, sorted |

**E80's anchors, repeated inside the session** (the brief): fp32 randn, fp16 randn, int8 full, and one zeros per type.
fp16 zeros and int8 zeros are E80 kinds; fp32 zeros is one of the 33 (E80 never ran it), so its tie is to E64's
23 Oct cell only. The five E80 kinds tie the two sessions together (rule E83-R5) and give the heat path's drift since
E80 (arm a-adj). They are not scored with the 33.

**The blocks** ([`protocol.json`](protocol.json), order seed 83; E80's shapes exactly):

| block | runs | start | load | scores |
|---|---|---|---|---|
| `SMOKE` | fp32 a_zeros_b_randn, fp16 pair_half_zero, int8 highbit, 2 s each | none | one 2 s process | not analysed: it checks new `file:` tiles on the card |
| `BURST` | 38 kinds × 2 passes, each pass shuffled | die reading ≤ 55 °C | one 6 s process | burst clock, p800, burst W, die, the burst limit, the kernel's rate, the switching term c |
| `SUS` | 38 kinds, plus fp32 ones, int8 ternary, fp32 sparse50 and fp16 wsparse50 again (42 runs), shuffled | die reading ≤ 57 °C | nine back-to-back 8 s processes, about 76 s | the last 40 s: clock, board W, die, rate, the limit labels |

That is 118 runs. E80 took 12 s per burst and 95 s per sustained run, so the plan is about **82 card-minutes**
(76 × 12 s + 42 × 95 s). The cap is **95** for the main session and **100 in all**, smoke included, and the card work
ends by 19:30 PDT. A session the cap cuts short is reduced as far as it got; a rule below its population is
UNDER-RESOLVED.

**Why these four sustained replicates.** They are the new kinds that the prediction puts on the steep part of the
sustained curve or at the edge of its limit class, where E80 saw the largest run-to-run spread (fp16 ones, 22.6 MHz):
fp32 ones (the fp32 copy of E80's fp16 all-ones cell; share at 800 predicted 0.74), fp32 sparse50 (759 MHz predicted),
fp16 wsparse50 (767), and int8 ternary (share 0.92, one point from the class line).

**Etiquette.** The card is claimed in `#community-lab` with one line, after this commit is pushed and before the
smoke, with the planned time and its end (`for 2 h, until ~HH:MM PDT`); the same post is edited at the release. The
runner refuses when another user is logged in or another process holds the card, and before every launch process;
it caps every device process at `timeout 10` and never signals one. The lab dashboard's collector and keeper are left
alone, as in E64, E69 and E80: the runner holds the card lock, which they honour.

## What E80's 1-of-9 result says about which rules are worth registering

E80 registered nine rules and one passed (E80-R1, the cool-die burst). Read cause by cause
([E80 README](../../../../docs/reports/data/2026-10-31-e80-kinds-speed/README.md) §1 and §3), the failures say four
things about how to register E83:

1. **The burst path works; register it again with the same bar.** Kind → predicted watts → governor held the 18 burst
   clocks to 21.7 MHz rms, and the governor alone on measured power to 2.65 MHz once the idle resets were set aside.
   E83-R1 keeps E69's 25 MHz bar.
2. **A sustained prediction built on another day's heat path tests the room, not the model.** E80's sustained misses
   (S3 35.8 MHz, R2 13 of 18, R3 +36.4 MHz) came from the die line moving 1.38 °C between 23 and 31 Oct; on its own
   day's line the same governor model reached 9.2 MHz. So E83 predicts the sustained clock from **E80's same-day
   relation** (prediction a), scores it against the frozen model that used 23 Oct's line (prediction b), and measures
   the drift since E80 directly on the five anchors (E83-R5, arm a-adj). A sustained rule is worth registering only
   with a heat path measured on the same day.
3. **A rule that mixes the power model with the clock model cannot say which one failed.** E80-S3 needed a post-hoc
   split. E83 registers the split up front: the full chain (R1–R4), the clock relation alone on each kind's measured
   power (S1), and the power model alone (S2, S3).
4. **"Every cell" clauses are hostage to the governor's idle reset.** It fired in 2.2% of E80's work processes (E63's
   rate), and one reset decided R7. With 118 runs E83 should see two or three. So no E83 rule has an "every cell"
   clause on a clock: they are rms and shares. A1's reset detector (`posthoc_idle.flags`, committed at `075b691e`; the
   file's one later change, `c244f148`, touched only its `main`) is applied to every burst and reported beside each
   burst rule, never instead of it.

And one thing worth registering **as a prediction** rather than a check: E80 found that Q130(c) over-charges fp32 data
whose mantissas carry fewer random bits (bf16trunc −27%, smallint −18%, nn_like −18% against its point). E83-S3 predicts
the same direction for the two new fp32 kinds that zero mantissa bits, fp16grid (the low 13 bits) and pow2 (all 23).

## Predictions (frozen)

[`predict_e83.py`](predict_e83.py) builds [`predictions.json`](predictions.json) and
[`predictions.txt`](predictions.txt) from committed inputs only, each refused unless its sha256 is:

- `c5a66cb6…` Q130(c)'s `predictions.json` (prediction b, and every predicted power);
- `9586568f…` `kinds.json`;
- `f8ab6fc0…` E80's `results.json` and `f1f37c5e…` its `posthoc-idle.json` (the fit's points);
- `d430bfab…` E64's `figures.json` (B_f, s_f, the registered governor);
- `69a62b31…` E80's `predictions.json` (E64-T1's build, for one labelled arm only).

**Prediction (a), primary: E80's measured relation, fitted on E80's 18 kinds only.** A kind's power is its switching
term c at 600 MHz and 517 mV, by E64's method (`P_f = B_f + c·s_f`, referred to a 58 °C die). E80 measured c and the
clocks for its 18 kinds. The relation is the clock at which the kind's power curve time-averages an effective cap W,
the governor dithering between neighbouring DVFS points:

- 800 MHz if `W ≥ P_800`; `700 + 100 (W − P_700)/(P_800 − P_700)` if `P_700 ≤ W < P_800`;
  `600 + 100 (W − P_600)/(P_700 − P_600)` if `P_600 ≤ W < P_700`; 600 below that;
- averaged over `W ~ Normal(W*, σ)`, which softens the knee.

Two parameters per regime, least squares on E80's 18 cells (burst: A1's reset-free cells; sustained: the registered
cells). Fitted:

| regime | W* | σ | rms on E80, in sample | leave one kind out | a two-parameter hinge, leave one out |
|---|---|---|---|---|---|
| burst (1.5–6.5 s of a 6 s run from ≤ 55 °C) | **66.15 W** | 2.75 W | 0.94 MHz | **1.4 MHz** (worst 3.8) | 2.3 MHz |
| sustained (last 40 s of ~76 s from ≤ 57 °C) | **49.75 W** | 1.95 W | 8.0 MHz | **9.0 MHz** (worst 14.7) | 10.7 MHz |

The form was chosen before any E83 data by its leave-one-kind-out rms on E80, against the hinge
`clamp(800 − β·max(0, c − c₀), 600, 800)`; the script refuses to freeze a form that loses. In words: a burst behaves
as if the governor held 66 W, and sustained work on today's cooling as if the card could shed 49.75 W of 58 °C-referred
power at the 65 °C trip.

The same average gives the expected time share at 800 MHz. **The predicted sustained limit** is `none` when that share
is ≥ 0.9 (the measured rule's own threshold), otherwise `thermal`: in E80 no sustained sample of any kind carried a
power label. The predicted burst limit is `power` when the burst share is below 0.9, otherwise `none` (tabulated, not a
rule). Each kind's interval is the clock at the two ends of Q130(c)'s 95% c interval, converted to aifoundry2.

**Prediction (b): Q130(c)'s own frozen clocks**, verbatim from its `predictions.json` (sha256 `c5a66cb6…`): the burst
mean over 4–12 s, the sustained mean over 40–80 s from 58 °C, and its two-way limit (`power` for every cell under its
trip, as E80 scored R8). It used E64's 23 Oct die line.

**Labelled arms, tabulated, never a verdict:** E64's registered governor on Q130(c)'s c over 1.5–6.5 s (E80's own
burst prediction); E64-T1 at γ 3 with E80's post-hoc die line `42.233 + 0.4349 °C/W` from 57 °C; and **(a-adj)**,
prediction (a) with its sustained cap moved by the heat path's drift since E80, measured on the anchors: the mean over
E83's anchor sustained runs of `die − (42.233 + 0.4349·W)` is Δ, and `W*_adj = 49.75 − Δ/0.4349`.

**The table** (`predictions.txt` has the same with the arms; "role" anchor = an E80 kind repeated here):

| kind | role | c W (95%) | (a) burst MHz (from c 95%) | (a) burst limit | (a) sustained MHz (from c 95%) | share at 800 | (a) limit | (b) burst 4–12 s | (b) sustained | (b) limit |
|---|---|---|---|---|---|---|---|---|---|---|
| fp32 zeros | e83 | 1.44 (1.44–1.74) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| fp32 ones | e83 | 9.84 (9.28–10.39) | 800.0 (800–800) | none | 773.8 (765–782) | 0.74 | thermal | 800 | 745 | thermal |
| fp32 neg_ones | e83 | 9.84 (9.28–10.39) | 800.0 (800–800) | none | 773.8 (765–782) | 0.74 | thermal | 800 | 745 | thermal |
| fp32 pi | e83 | 9.84 (9.28–10.39) | 800.0 (800–800) | none | 773.8 (765–782) | 0.74 | thermal | 800 | 745 | thermal |
| fp32 randn | anchor | 25.21 (21.41–29.01) | 712.9 (680–748) | power | 603.1 (600–626) | 0.00 | thermal | 700 | 600 | thermal |
| fp32 randn_small | e83 | 25.44 (21.59–29.30) | 710.8 (677–747) | power | 602.5 (600–624) | 0.00 | thermal | 700 | 600 | thermal |
| fp32 randn_large | e83 | 25.48 (21.62–29.34) | 710.5 (677–746) | power | 602.4 (600–624) | 0.00 | thermal | 700 | 600 | thermal |
| fp32 uniform01 | e83 | 21.43 (18.54–24.32) | 748.2 (721–779) | power | 625.3 (606–656) | 0.00 | thermal | 736 | 612 | thermal |
| fp32 sparse50 | e83 | 10.77 (8.88–12.65) | 800.0 (800–800) | none | 759.2 (732–787) | 0.59 | thermal | 800 | 728 | thermal |
| fp32 pow2 | e83 | 14.39 (13.15–15.64) | 799.8 (798–800) | none | 708.8 (693–725) | 0.12 | thermal | 800 | 681 | thermal |
| fp32 fp16grid | e83 | 24.95 (21.21–28.69) | 715.1 (682–750) | power | 603.8 (600–627) | 0.00 | thermal | 700 | 600 | thermal |
| fp32 a_randn_b_zeros | e83 | 1.44 (1.44–1.74) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| fp32 a_zeros_b_randn | e83 | 1.44 (1.44–1.74) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| fp32 randn_sorted | e83 | 23.79 (20.33–27.25) | 725.5 (695–760) | power | 608.4 (600–636) | 0.00 | thermal | 706 | 600 | thermal |
| fp16 zeros | anchor | 1.39 (1.39–1.69) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| fp16 neg_ones | e83 | 9.70 (7.33–12.07) | 800.0 (800–800) | none | 776.0 (740–799) | 0.76 | thermal | 800 | 745 | thermal |
| fp16 randn | anchor | 23.28 (19.96–26.61) | 730.2 (701–764) | power | 611.2 (601–640) | 0.00 | thermal | 715 | 600 | thermal |
| fp16 randn_small | e83 | 23.18 (14.44–31.92) | 731.1 (656–800) | power | 611.9 (600–708) | 0.00 | thermal | 718 | 600 | thermal |
| fp16 uniform01 | e83 | 17.82 (12.23–23.41) | 786.4 (729–800) | power | 664.3 (610–738) | 0.00 | thermal | 776 | 646 | thermal |
| fp16 sparse90 | e83 | 2.56 (1.94–3.19) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| fp16 wsparse50 | e83 | 10.27 (5.91–14.63) | 800.0 (800–800) | none | 767.0 (706–800) | 0.67 | thermal | 800 | 735 | thermal |
| fp16 wsparse90 | e83 | 1.84 (1.47–2.22) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| fp16 a_randn_b_zeros | e83 | 1.39 (1.39–1.69) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| fp16 a_zeros_b_randn | e83 | 1.39 (1.39–1.69) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| fp16 pair_half_zero | e83 | 21.95 (13.95–29.95) | 743.0 (672–800) | power | 620.9 (600–715) | 0.00 | thermal | 727 | 608 | thermal |
| fp16 randn_sorted | e83 | 22.44 (14.15–30.74) | 738.1 (665–800) | power | 616.9 (600–712) | 0.00 | thermal | 715 | 604 | thermal |
| int8 zeros | anchor | 2.12 (2.12–2.42) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| int8 ones | e83 | 2.68 (2.12–5.04) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| int8 full | anchor | 9.10 (5.79–12.41) | 800.0 (800–800) | none | 784.7 (735–800) | 0.85 | thermal | 800 | 758 | thermal |
| int8 pos | e83 | 5.51 (2.43–8.58) | 800.0 (800–800) | none | 800.0 (791–800) | 1.00 | none | 800 | 800 | power |
| int8 ternary | e83 | 8.42 (3.77–13.08) | 800.0 (800–800) | none | 792.4 (726–800) | 0.92 | none | 800 | 768 | thermal |
| int8 sparse90 | e83 | 2.90 (2.20–3.60) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| int8 wsparse50 | e83 | 5.33 (3.04–7.62) | 800.0 (800–800) | none | 800.0 (798–800) | 1.00 | none | 800 | 800 | power |
| int8 wsparse90 | e83 | 2.39 (2.12–2.73) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| int8 highbit | e83 | 6.53 (2.95–10.12) | 800.0 (800–800) | none | 799.8 (770–800) | 1.00 | none | 800 | 800 | power |
| int8 a_full_b_zeros | e83 | 2.12 (2.12–2.42) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| int8 a_zeros_b_full | e83 | 2.12 (2.12–2.42) | 800.0 (800–800) | none | 800.0 (800–800) | 1.00 | none | 800 | 800 | power |
| int8 sorted | e83 | 8.00 (3.59–12.40) | 800.0 (800–800) | none | 795.7 (735–800) | 0.96 | none | 800 | 776 | thermal |

**What the predictions rest on, and what they do not cover.**

- Every predicted power is Q130(c)'s frozen number. E80 measured it too high for low-entropy fp32 data and within
  0.35 W on the calibration kinds; prediction (a) inherits that error, which is why S1 scores the relation on the
  measured power as well.
- **int8 power is provisional** (Q130(c)'s U_int8; E80 read int8 neg_ones 0.86 W above it). Every int8 kind but
  ternary and sorted is predicted far enough below the knee that this cannot move its clock.
- (a) assumes the heat path of E80's session (12:22–13:02 PDT). E83 runs later the same afternoon; the anchors measure
  how far it moved (R5, a-adj).
- 24 of the 33 bursts and 15 of the 33 sustained cells are predicted at 800 MHz. Those cells are easy and dilute an
  rms, so the reduction also reports R1's and R3's rms over the kinds (a) puts below 799 MHz (labelled).
- fp32 zeros has E64's 23 Oct cells beside it (burst and sustained 800), as do fp32 ones (burst 800, sustained 738),
  fp32 pow2 (burst 800) and int8 ones (sustained 800); E64 ran the host's own values with the same bit rules.
  Tabulated, no rule.

## Decision rules (frozen; `reduce_e83.py` implements them)

**Definitions** (E80's, unchanged).

- A run's **burst clock** is the mean sampled clock from 1.5 s after the first launch to the end of the work; a kind's
  **burst cell** is the mean of its two passes, and its interval the two passes.
- A **sustained cell** is the mean clock over the last 40 s of the work, averaged over the kind's runs. A single-run
  cell's interval is the run-to-run spread of the replicated cells (E80's three and E83's four), reported in the data
  README.
- **Board W, die °C, p800, TFLOPS / TOPS, the measured switching term c and the measured sustained limit** are E80's
  (`reduce_kspeed.burst_extra` and `sus_limit`, imported unchanged): `none` if ≥ 90% of the last 40 s reads 800 MHz;
  otherwise `thermal` or `power` by E64 R4's labels at ≥ 50% of the samples below 800; otherwise `unresolved`. A
  kind's c is the mean of its two bursts' c.
- **The 33** are the kinds whose role is `e83`. The anchors are scored only in R5.

**Primary rules.**

- **E83-R1, the burst, kind → watts → clock.** The rms over the 33 of (measured burst cell − (a) burst) is at most
  **25 MHz** (E69's bar, as E80-R1). Beside it: the same on A1's reset-free cells, (b)'s rms, the E64-governor arm's,
  and the rms over the kinds (a) puts below 799 MHz.
- **E83-R2, the sustained limit.** (a)'s limit (`none` / `thermal`) is right for at least **80%** of the 33 (27 or
  more). A kind is right only if every one of its runs carries the predicted label; `power` or `unresolved` is wrong.
- **E83-R3, the sustained clock.** The rms over the 33 of (measured sustained cell − (a) sustained) is at most
  **25 MHz**.
- **E83-R4, what E80 taught beats the frozen model.** Over the 33, the sustained rms of (a) is smaller than the
  sustained rms of (b). The same comparison for the burst is reported beside it.
- **E83-R5, the two sessions tie.** Each of the ten anchor comparisons (fp32 randn, fp16 randn, int8 full, fp16 zeros
  and int8 zeros; burst and sustained cell) lies within **25 MHz** of E80's cell. A failure means the card moved
  between the two sessions, not that a model did.

**Secondary rules: one link of the chain at a time.**

- **E83-S1, the relation alone.** (a)'s relation applied to each kind's **measured** c reproduces the measured clocks
  over the 33: burst rms ≤ **15 MHz** and sustained rms ≤ **15 MHz** (both). This is E80's relation out of sample on
  new kinds, free of Q130(c)'s power error.
- **E83-S2, the power model on aifoundry2.** The measured c lies inside Q130(c)'s converted 95% interval for at least
  **70%** of the 33 that Q130(c) labels out of sample (all but int8 ones).
- **E83-S3, E80's fp32 lesson repeated.** fp32 fp16grid and fp32 pow2 each measure c **below** Q130(c)'s point
  prediction (24.95 and 14.39 W).

A rule with fewer than 24 of the 33 cells (R1–R4, S1), fewer than eight anchor rows (R5), fewer than 18 kinds (S2), or
a missing kind (S3) is UNDER-RESOLVED.

**Labelled, never a verdict:** A1's reset-free view of every burst rule; the two arms and (a-adj); the die line refitted
on E83's own sustained runs (as E80's post hoc) and its shift from E80's line; the measured burst limit against (a)'s;
the count of bursts whose first throttle-down was thermal; the idle resets per process.

## What a result fills

For each of the 33 kinds, the cells of the blog's kinds-of-numbers table that E80 filled for its 18: burst MHz and
sustained MHz, TFLOPS or TOPS at each, board W (p800, burst mean, sustained mean), die °C (burst start and peak,
sustained mean) and the limiting test. With E80 that is all 51 kinds measured on one card on one day. The data goes to
[`docs/reports/data/2026-10-31-e83-kinds-speed-rest/`](../../../../docs/reports/data/2026-10-31-e83-kinds-speed-rest/).

## Files

| file | what |
|---|---|
| `protocol.json` | the blocks, the tiles, the gates, the caps |
| `run_e83.py` | the runner: E80's `run_kspeed.py`, imported unchanged, plus a dry-run power table and `e83.json` |
| `predict_e83.py`, `predictions.json`, `predictions.txt` | the frozen predictions, the fit and its console table |
| `reduce_e83.py` | the registered reduction (per-run metrics from E80's and E64's code, unchanged) |

Run, on aifoundry2, from the lab checkout:

```bash
python3 tools/claims-v3/kspeed/e83/run_e83.py --protocol tools/claims-v3/kspeed/e83/protocol.json --out build/e83/runs/<s> --dry --only SMOKE   # toy card
python3 tools/claims-v3/kspeed/e83/run_e83.py --protocol tools/claims-v3/kspeed/e83/protocol.json --out build/e83/runs/smoke --only SMOKE --max-card-min 5
python3 tools/claims-v3/kspeed/e83/run_e83.py --protocol tools/claims-v3/kspeed/e83/protocol.json --out build/e83/runs/s1
python3 tools/claims-v3/kspeed/e83/reduce_e83.py <data>/s1 --out <data>/results.json > <data>/reduce.txt
```

## Amendments

None yet.
