# E113 — the A side's form: two layouts at fixed Hamming weight (Q133, aifoundry3 card 0, 600 MHz, 2026-11-01)

*Pre-registered in [`tools/claims-v3/e113/README.md`](../../../tools/claims-v3/e113/README.md) — four laws, the frozen predictions
in [`predictions-e113.json`](../../../tools/claims-v3/e113/predictions-e113.json), seven rules P1–P7 and the scorer — committed as
`b05e610d` and **pushed at 16:00:44 PST, 59 s before the card was claimed** in `#community-lab` (16:01:43 PST, message
1566603178164617247), before the first launch (the smoke, from 16:01:59) and 2 min 26 s before the first registered pass's
first launch (16:03:10). The session ran
16:01:54 → 16:28:42 PST on **aifoundry3 card 0** (smoke 16:02:04–16:02:27, then passes 1131–1137): **26.8 card-minutes** of the 35
allowed. 600 MHz pinned by the card's boot-time TDP 0, 521.7 mV. `ettelem config`, read under the card lock with `timeout 10` at the
session's start and end, read TDP 0 W, threshold 65 °C, 600 MHz, 523 mV, `max_power` both times. **Nothing on the card was set.***

**The complaint it answers.** The A side's saturating form, carried since E70 rejected it, and listed as not touched by the final
critic's item 13. On the kinds page's [§ 11, "What is still open"](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)
(as it read at `1fe8377a18af`) it falls under **item 15, "Smaller, and carried"**, and it bears on **item 6**'s clause on the A side
and its ladders (the power model reads them 0.86–0.90 post hoc). It also tests E78's C2, *the broadcast A word's weight is unvalidated*,
for an ungated fp32 lane.

## Results

**1. The layout matters on A, as it does on B (P1 PASS).** At the same number of flipping A bits, spreading them over the mantissa
costs more than keeping them in the low bits, at every k from 2 to 16. At k = 8 the spread layout costs **+2.818 ± 0.051 W** more
(55.7 SE from the zero any "how many" law needs). So A's sub-additivity is set by *which* bit positions flip, not *how many*.

**2. The A side's saturating form in its own summed single-bit prices is rejected again (P2 REJECTED), now with both layouts.** One
curve W (1 − e^(−S_A/W)) in A's own additive sum, refitted on the 15 A rungs (W = 5.90 W), leaves **0.708 W rms** against the
registered 0.40 W to accept and 0.60 W to reject (E70: 1.063 W on the low layout alone). The ladder's top rung, out of every fit,
`alq_h23` = 7.598 ± 0.032 W, sits **1.70 W, 54 SE above the refitted W** (E70: 28 SE above 6.37 W).

**3. What does describe the A side: the mirror. An A mask costs a fixed fraction of the same mask flipped on B (P3 PASS, P4 "which
bits").** With c = 0.643 frozen from E70's low layout, the mirror reads the seven new spread rungs to **0.259 W rms** (out of sample;
registered ≤ 0.50 W) and all 15 A rungs to 0.308 W. Refitted, c = **0.678 ± 0.007** (per-pass) reads the 15 rungs to **0.248 W**,
against 0.708 W for a curve in S_A and 0.877 W for the best any "how many" law can do. The mirror collapses the two A layouts 2.9× better
than a curve in A's own sum. *Post hoc:* through the B side's own law (E70's W = 10.52 W in the B list's additive sum over the same
positions), one scale c = 0.679 reads the 15 A rungs to **0.233 W**, the B side's own 0.232 W ([`posthoc.json`](posthoc.json)
`sb_law`). So the A side does saturate, **in the
same variable as the B side, the B list's sum over the flipping positions, scaled by about 0.68**, and not in its own single-bit sum.
*Caveat, as registered:* on the spread rungs alone the frozen A-side curve reads 0.226 W too, so P3 does not separate the two laws.
The low layout does (the frozen curve over-predicts `alq_h8` by 1.78 W, the mirror by 0.06 W).

**4. The A word's weight against B, at the same mask (P5 PASS).** Per designed bit (A counted per lane slot, 2,048 per multiply-add per
k; B 4,096), A over B is **ρ(8) = 1.366 ± 0.106 in the low layout and 1.350 ± 0.012 in the spread layout**, a difference of
−0.016 ± 0.103. A bit of the broadcast A word, counted once per lane slot as `kinds.json` counts it, costs about 1.35 B bits in either
layout. Counted once per broadcast word it would have to cost about 10.8 B bits. This validates the per-slot count for an **ungated**
fp32 lane only. E78's C2 case, a gated lane (B = 0, A moving), was not run.

**5. The session reproduces E70 (P6 PASS)** and the random pair agrees (P7 PASS). E70's seven A rungs come back within +0.016 to
+0.122 W (bands 0.6 W, 1.0 W at the top). The B tie `ls_h8` − `lq_h8` reads 4.140 ± 0.187 W against E70's 3.860 (+0.28, band 0.6).
`nrd_a` / `nrd_b` (one side random fp32, the other 1.0) reads **0.664 ± 0.006**, against the mirror's c and E70's 0.668. The refitted
S_A curve predicts `nrd_a` at 5.585 W, which is 1.29× too low.

| rule | asked | measured | verdict |
|---|---|---|---|
| **P1** | D1_A(8) > 1.0 W at ≥ 3 SE (H 0; WA 1.19; M 2.48; A 3.96 W) | +2.818 ± 0.051 W | **PASS** |
| **P2** | one curve in S_A, W refitted on 15 A rungs: ACCEPTED ≤ 0.40 W, REJECTED > 0.60 W | 0.708 W (W = 5.90 W) | **REJECTED** |
| **P3** | the mirror, c frozen at 0.643, over the 7 spread rungs: PASS ≤ 0.50 W, FAIL > 0.80 W | 0.259 W (frozen curve 0.226; additive 7.417) | **PASS** |
| **P4** | the form, read off P1 and D2_A | R_k 0.877, R_SA 0.708, R_M 0.248 W | **which bits**: the two A layouts collapse on a one-parameter law, not on k; the mirror better than a curve in S_A |
| **P5** | ρ(8) in [0.7, 2.5] in both layouts, \|spread − low\| ≤ 0.30 | 1.366 / 1.350, −0.016 ± 0.103 | **PASS** |
| **P6** | E70's seven `alq` rungs within 0.6 W (1.0 W at k = 23), `ls_h8` − `lq_h8` within 0.6 W of 3.860 | largest +0.122 W; tie +0.280 W | **PASS** |
| **P7** | `nrd_a` / `nrd_b` in [0.55, 0.75] | 0.664 ± 0.006 | **PASS** |

Every rule is scored as registered by `tools/claims-v3/e113/score_e113.py` over the six passes the gates keep
([`report.md`](report.md), [`scored.json`](scored.json) `rules`). Every arm keeps every verdict: the leakage slope fixed at 0.2, 0.3
or 0.4 W/°C, and all seven passes with E70's D-a gate off (`report.md` § Arms).

## The two ladders

ΔW over the A-side zero `aq_h0` (A constant, B = 1.0), paired per pass, mean ± SE over six passes; the laws' frozen predictions
beside them (`scored.json` `items`, `predictions-e113.json` `rungs`).

| k | low layout `alq` (W) | spread layout `als` (W) | flipping bits, spread | law WA (low / spread) | law M (low / spread) | E70 `alq` |
|---|---|---|---|---|---|---|
| 1 | 0.314 ± 0.058 | — | — | 0.443 / — | 0.390 / — | 0.282 ± 0.070 |
| 2 | 0.951 ± 0.025 | 1.177 ± 0.028 | 0, 12 | 1.414 / 1.280 | 0.597 / 1.342 | 0.829 ± 0.097 |
| 3 | 0.950 ± 0.026 | 2.641 ± 0.095 | 0, 8, 15 | 1.769 / 2.563 | 0.832 / 2.225 | — |
| 4 | 1.594 ± 0.026 | 2.827 ± 0.029 | 0, 6, 12, 17 | 2.485 / 2.930 | 0.968 / 2.848 | 1.578 ± 0.017 |
| 6 | 2.045 ± 0.023 | 3.941 ± 0.169 | 0, 4, 8, 12, 15, 19 | 3.081 / 4.334 | 1.516 / 3.786 | — |
| 8 | 2.026 ± 0.028 | 4.844 ± 0.056 | 0, 3, 6, 9, 12, 14, 17, 20 | 3.801 / 4.991 | 2.089 / 4.573 | 1.957 ± 0.070 |
| 12 | 3.504 ± 0.043 | 6.061 ± 0.062 | 0, 2, 4, …, 21 (12 bits) | 4.826 / 5.832 | 3.539 / 5.719 | 3.482 ± 0.016 |
| 16 | 5.743 ± 0.071 | 6.504 ± 0.049 | 16 of 0–22 | 5.848 / 6.185 | 5.381 / 6.271 | 5.709 ± 0.136 |
| 23 | 7.598 ± 0.032 | = `alq_h23` (same mask) | 0–22 | 6.336 | 7.813 | 7.560 ± 0.042 |

The B rungs run in the same passes: `lq_h8` 3.037 ± 0.189 W and `ls_h8` 7.177 ± 0.048 W over `lq_h0`; `nrd_a` 7.195 ± 0.052 W over
`aq_h0`, `nrd_b` 10.842 ± 0.037 W over `lq_h0`.

**D1_A, spread minus low at the same k** (paired per pass, `scored.json` `D1_A`): +0.226 ± 0.010, +1.692 ± 0.084, +1.233 ± 0.018,
+1.897 ± 0.166, **+2.818 ± 0.051**, +2.556 ± 0.022, +0.761 ± 0.059 W at k = 2, 3, 4, 6, 8, 12, 16 — every one 11–115 SE from zero. It
rises, peaks at k = 8–12 and falls toward the exact zero k = 23 forces, the shape E70 measured on B (+1.158 … +3.860 … +1.385 W),
at 0.20 to 0.78 of B's size (0.73 at k = 8, 0.75 at k = 12, 0.55 at k = 16), where the mirror predicted 0.64 at every k. The mirror predicted +0.745 … +2.483 … +0.891 W;
the A-side curve +1.190 at k = 8; additivity +3.959 at k = 8 and +6.56 at k = 16; "how many" 0.

**D2_A, what collapses the two layouts** (15 rungs, `alq_h23` out of sample; `scored.json` `D2_A`):

| law | free parameters | rms (W) |
|---|---|---|
| a free value per k (the best any "how many" law can do) | one per k | 0.877 (matched k only 0.908) |
| one curve in A's own sum S_A, W refitted (5.90 W; per pass 5.90 ± 0.08) | 1 | 0.708 |
| the same, W frozen at E70's 6.37 W | 0 | 0.732 |
| the mirror, c refitted (0.678; per pass 0.678 ± 0.007) | 1 | **0.248** |
| the mirror, c frozen at 0.643 | 0 | 0.308 |
| additive (S_A) | 0 | 6.011 |
| *post hoc:* c × the B side's law in the B list's sum, W = 10.52 W frozen (c 0.679) | 1 | 0.233 |

The frozen mirror's largest misses are `alq_h4` (+0.63 W), `alq_h6` (+0.53) and `als_h3` (+0.42) (`posthoc.json` `mirror_res`).
E70's `lq_h4` carries an SE of 0.20 W, and the mirror inherits every B rung's noise. Through the B side's law instead, which smooths
them, the same 15 rungs read 0.233 W (the last row, post hoc: `posthoc_e113.py` → `posthoc.json` `sb_law`; with W free too, 0.227 W
at W = 9.83 W, `sb_law_W_free`).

## What it changes

- **E70's "the A side's saturating form is rejected outright … its shape is newly open":** the shape is no longer open for the
  quiet partner on this card. In A's own single-bit sum the form stays rejected, more firmly (0.708 W rms over two layouts; top rung
  54 SE above the curve's W). But the A side follows the B side's law, scaled: an A mask costs about **0.64–0.68** of the same mask
  flipped on B (0.25–0.31 W rms over 15 rungs and two layouts). So E67's A single-bit prices are the wrong axis, and the B list, which
  E70 showed saturates in its own sum, carries the A side too.
- **The carry-over between operands** (E70's ρ, Q128's choice between 1.57 and 1.01): measured at k = 8 in both layouts in one session,
  **1.35 per designed bit, the same in both layouts** (1.366 ± 0.106 and 1.350 ± 0.012). E70's ρ(12) = 1.266 ± 0.011 was a low-layout
  number. At k = 8, ρ does not depend on which positions flip.
- **E78's C2 (the broadcast A word's weight):** for an ungated fp32 lane, counting an A flip once per lane slot is the right footing,
  within 35%. A count per broadcast word is excluded by about 8×. The gated-lane residual C2 was about, 0.616 W with B = 0, is untouched.
- **For the power model (item 6), post hoc:** in the fixed RTL bench (Q132(b) `counts-hl.json`, `unit.nets_hier` over each ladder's
  zero) A's low ladder toggles 0.88–1.38× as many nets as B's at the same k (k = 2 to 23), where on the card it costs 0.62–1.06× the
  watts (E113's A rungs, E70's B rungs; `posthoc.json` `bench_vs_card`). The bench counts an A flip 1.2–1.7× too high against a B
  flip at the same positions, if net toggles stood for watts. That is
  the A-side over-count item 6 lists ("ladders 0.86–0.90 post hoc"). A term that prices an A mask at about 0.68 of the same mask on B
  is what this data supports; nobody has fitted one.
- **For the blog:** which positions flip sets the cost, on either operand. Flip the same bit positions on the broadcast operand A
  instead of B and the card pays about two thirds of the watts, at half the flips; per flipped bit, A costs about 1.35 B bits.

**Still open:** the busy partner (every A rung here has B = 1.0); other A base words (one shared base word, E67's); fp16 and int8 (the
hl runner is fp32 only, so Q130(c) A1's int8 A-side α of 0.491 is untouched); the gated lane; why the A/B ratio sits near 1.0 at k = 2
and 4 in the low layout (0.951 / 0.928 and 1.594 / 1.505 against E70's B rungs) and near 0.63 from k = 8 up; another card.

## What ran

One item list, 24 runs a pass after two unrecorded `anchor_pi` burn-in runs: `anchor_pi` (first and last), `aq_h0`, `alq_h1, 2, 3, 4,
6, 8, 12, 16, 23`, `als_h2, 3, 4, 6, 8, 12, 16`, `lq_h0`, `lq_h8`, `ls_h8`, `nrd_a`, `nrd_b`. Operand set `build/hl-gen6-e113`, written
by `make_e113.py` on the box and `--check`ed. 167 of 167 files of E70's `build/hl-gen5` are byte-identical in it, and the nine new
tiles match `new-tiles.sha256` (`logs/setup.log`). E67's and E70's protocol through `hl/block.sh` unchanged: launch at a 58 °C reading
after 59 °C, 4 s runs on 1,024 minions, the rest shuffled with the pass number. The smoke, pass 1130 (`anchor_pi`, `als_h8`,
`alq_h8`, no preheat), passed its gate (block ok; every launch ok on 1,024 minions at 546 cycles per op).

- **Seven passes, 1131–1137**, 201–235 s each (`logs/queue.out`). **168 of 168 runs passed every per-run gate** (600 MHz in every
  window sample, voltage, launch on protocol at 58.0 °C, cycles per op 546.0–546.016). The die ran 57 → 58 °C in every pass after the
  first (51 → 58). The op rate held at 1.1208–1.1210 Gop/s per minion. Host load1 0.36–1.14 over the session (`logs/load.jsonl`).
- **One pass set aside, by E70's D-a gate as registered:** in pass 1137 `aq_h0` read 35.665 W against 36.32, 36.52 and 36.43 W for
  the pass's other constant-operand runs, a spread of 0.858 W against the gate's 0.45. That one low reading would have lifted every
  A rung of that pass by about 0.8 W. The registered reduction is over **six passes (1131–1136)**. The all-passes arm, with 1137 in,
  keeps every verdict (c 0.695, D1_A(8) 2.837 ± 0.047 W).
- **Leakage:** `reduce_hl.py`'s within-run fit on this session, 0.161 W/°C (153 runs). The arms at 0.2, 0.3 and 0.4 W/°C keep every
  verdict. c moves 0.673 → 0.647 across them and D1_A(8) moves 2.812 → 2.782 W.

**Departures:** none from the registration. Three notes. (a) The mirror law was formed post hoc on E70's published numbers, before
this registration; the registration says so, and P3 scores it only on the spread rungs, which E70 never ran. (b) The refitted c
(0.678) sits 5% above the frozen 0.643. Part of that is the B side's session: the mirror reads E70's B rungs, and E113's own `lq_h8`
reads 3.037 ± 0.189 W against E70's 3.248. With the B rungs from E113's own passes, ρ(8) / 2 gives c = 0.683 (low) and 0.675
(spread). (c) The smoke gate's printout counts launch records ("40 runs" is 4 runs × 10 launches); its checks are per launch, as
written.

## Files

| file | what |
|---|---|
| `posthoc_e113.py`, `posthoc.json` | the post hoc numbers the README labels post hoc: the B-side law on the A rungs, the frozen mirror's residuals, the bench against the card |
| `report.md`, `scored.json` | **the registered result**: `score_e113.py` over the six passes the gates keep, every contrast paired per pass; the arms in `report.md` § Arms and `scored.json` `arms` |
| `hl.json`, `runs.csv`, `reduce.txt` | `hl/reduce_hl.py` over all seven passes (its own pass gate sets aside none); `runs.csv` is the scorer's input |
| `hl-leak0.2/0.3/0.4.json`, `runs-leak*.csv`, `reduce-leak*.txt` | the leakage arms |
| `predictions-e113.json`, `manifest.json` | the frozen predictions as run; the operand set's items and designed flip counts |
| `aifoundry3/e113/p1131…p1137` | per pass: `block.json`, `configs.json`, `gen.sha256`, `manifest.txt` (`et-lab-manifest`), `marks.jsonl`, `run.log`, `runs.jsonl`, `code.sha256`, `telemetry.jsonl.gz`, `tiles/` |
| `aifoundry3/smoke-p1130` | the smoke pass |
| `logs/` | `setup.log` (files only: the operand set, byte-identity, dry run), `session.log`, `queue.out`, `smoke.log`, `load.jsonl`, `config-session-start.json` and `config-session-end.json`, the session's start and end times |

Nothing on the card was changed: no governor, TDP, threshold or clock write, no reset, no `--reset-ms`, no PMIC command. `et-who`
showed no holder before the claim (16:01:41) and after the session (16:28:42). Other lab users' idle logins on the host did not block
(E60's departure D1, as `hl/block.sh` implements it), and none of their names is recorded here.
