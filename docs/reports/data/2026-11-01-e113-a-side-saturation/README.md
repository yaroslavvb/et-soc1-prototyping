# E113 — the A side's form: two layouts at fixed Hamming weight (Q133, aifoundry3 card 0, 600 MHz, 2026-11-01)

*Pre-registered in [`tools/claims-v3/e113/README.md`](../../../../tools/claims-v3/e113/README.md) — four laws, the frozen predictions
in [`predictions-e113.json`](../../../../tools/claims-v3/e113/predictions-e113.json), seven rules P1–P7 and the scorer — committed as
`b05e610d` and **pushed at 16:00:44 PST, 59 s before the card was claimed** in `#community-lab` (16:01:43 PST, message
1566603178164617247), before the first launch (the smoke's, at 16:02:04) and 2 min 26 s before the first registered pass's
first launch (16:03:10). The session ran
16:01:54 → 16:28:42 PST on **aifoundry3 card 0** (smoke 16:02:04–16:02:27, then passes 1131–1137): **26.8 card-minutes** of the 35
allowed. 600 MHz pinned by the card's boot-time TDP 0, 521.7 mV. `ettelem config`, read under the card lock with `timeout 10` at the
session's start and end, read TDP 0 W, threshold 65 °C, 600 MHz, 523 mV, `max_power` both times. **Nothing on the card was set.**
Corrected after verification the same day, desk only: no data file, frozen file or registered verdict changed, and the wrong sentences
are replaced below ([Corrections after verification](#corrections-after-verification)).*

**The complaint it answers.** The A side's saturating form, carried since E70 rejected it, and listed as not touched by the final
critic's item 13. On the kinds page's [§ 11, "What is still open"](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)
(as it read at `1fe8377a18af`) it falls under **item 15, "Smaller, and carried"**, and it bears on **item 6**'s clause on the A side
and its ladders (the power model reads them 0.86–0.90 post hoc). It also tests E78's C2, *the broadcast A word's weight is unvalidated*,
for an ungated fp32 lane.

## Results

**1. The layout matters on A, as it does on B (P1 PASS).** At the same number of flipping A bits, spreading them over the mantissa
costs more than keeping them in the low bits, at every k from 2 to 16. At k = 8 the spread layout costs **+2.818 ± 0.051 W** more
(55.7 SE from the zero any "how many" law needs). So A's sub-additivity is set by *which* bit positions flip, not by *how many*
alone (the cost still rises with k in each layout).

**2. The A side's saturating form in its own summed single-bit prices is rejected again (P2 REJECTED), now with both layouts.** One
curve W (1 − e^(−S_A/W)) in A's own additive sum, refitted on the 15 A rungs (W = 5.90 W), leaves **0.708 W rms** against the
registered 0.40 W to accept and 0.60 W to reject (E70: 1.063 W on the low layout alone). The ladder's top rung, out of every fit,
`alq_h23` = 7.598 ± 0.032 W, sits **1.70 W, 54 SE above the refitted W** (E70: 28 SE above 6.37 W). P2 tests E70's one-parameter
curve only. Why no curve in S_A does much better is in the data: in 7 pairs of rungs the smaller sum costs more, at ≥ 3 SE paired per
pass. The clearest is `als_h4` (S_A 3.92 W) at 2.827 ± 0.029 W against `alq_h8` (S_A 5.78 W) at 2.026 ± 0.028 W, 0.80 W apart (34 SE).
Any rising function of S_A misses one of those two rungs by at least 0.40 W. *Post hoc*, two-parameter saturating curves in S_A reach
0.46 W (inside P2's INCONCLUSIVE band), and the best non-decreasing function of S_A, with 8 free levels, 0.21 W
([`corrections-check.txt`](corrections-check.txt) C2).

**3. What describes the A side better: the mirror. An A mask costs about two thirds of the same mask flipped on B (P3 PASS, P4 "which
bits"), though not a fixed fraction rung by rung.** With c = 0.643 frozen from E70's low layout, the mirror reads the seven new spread
rungs to **0.259 W rms** (out of sample; registered ≤ 0.50 W) and all 15 A rungs to 0.308 W. Refitted, c = **0.678 ± 0.007** (per-pass)
reads the 15 rungs to **0.248 W**, against 0.708 W for a curve in S_A and 0.877 W for the best any "how many" law can do. The mirror
collapses the two A layouts 2.9× better than a curve in A's own sum. Rung by rung, E113's A step over E70's B step of the same mask
runs 0.56–0.76 for every spread mask and for 8 or more low bits, but 0.52–1.06 for 1–6 low bits (0.52, 1.02, 0.73, 1.06, 0.87 at
k = 1, 2, 3, 4, 6). **Out of every fit, the top rung `alq_h23` reads 7.598 ± 0.032 W. The refitted mirror predicts 8.233 W (−0.635 W:
−20 SE on the A rung alone, about −4.6 SE once E70's `lq_h23` error of 0.158 W and c's are counted). The frozen mirror predicts 7.813 W
(−0.215 W, about −2.0 SE with E70's error; its c was fitted on E70's seven `alq` rungs, k = 23 among them, so for it this rung is a
replicate, not out of sample). The refitted S_A curve predicts 5.877 W (+1.721 W, 54.5 SE).** ([`report.md`](report.md) § D2_A,
[`corrections-check.txt`](corrections-check.txt) C1.) So the mirror is the better one-parameter law, not an exact one. *Post hoc:*
through the B side's own law (E70's W = 10.52 W in the B list's additive sum over the same positions), one scale c = 0.679 reads the
15 A rungs to **0.233 W**, the B side's own 0.232 W ([`posthoc.json`](posthoc.json) `sb_law`). So the A side does saturate, **in the
same variable as the B side, the B list's sum over the flipping positions, scaled by about 0.64–0.68**, and not in its own single-bit
sum.
*Caveat, as registered:* on the spread rungs alone the frozen A-side curve reads 0.226 W too, so P3 does not separate the two laws.
The low layout does (the frozen curve over-predicts `alq_h8` by 1.78 W, the mirror by 0.06 W), but that is the layout both frozen
constants were fitted on (E70's), so it is no out-of-sample test; the fair comparison is P4's, each law refitted on both layouts
(0.708 against 0.248 W).

**4. The A word's weight against B, at the same mask (P5 PASS).** Per designed bit (A counted per lane slot, 2,048 per multiply-add per
k; B 4,096), A over B is **ρ(8) = 1.366 ± 0.106 in the low layout and 1.350 ± 0.012 in the spread layout**, a difference of
−0.016 ± 0.103. A bit of the broadcast A word, counted once per lane slot as `kinds.json` counts it, costs about 1.35 B bits in either
layout. Counted once per broadcast word it would have to cost about 10.8 B bits. This validates the per-slot count for an **ungated**
fp32 lane only. E78's C2 case, a gated lane (B = 0, A moving), was not run. Between sessions ρ is less settled than within one: E70's
low layout read ρ(8) = 1.205 ± 0.041 (1.266 and 1.365 at k = 12 and 16), so at k = 8–16 the two sessions span 1.2–1.4. The gap at k = 8
sits mostly in the B rung: E113's `lq_h8` reads 3.037 ± 0.189 W (two of its six passes at 2.74 and 2.23 W) against E70's
3.248 ± 0.028, while the A rungs agree (2.026 against 1.957; [`corrections-check.txt`](corrections-check.txt) C4).

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
rises, with a dip at k = 4 (+1.233, below k = 3's +1.692; B's contrast has none), peaks at k = 8–12 and falls toward the exact zero
k = 23 forces, the shape E70 measured on B (+1.158 … +3.860 … +1.385 W),
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

- **E70's "the A side's saturating form is rejected outright … its shape is newly open":** the shape is answered in outline for
  the quiet partner on this card, with residuals left. In A's own single-bit sum the form stays rejected, more firmly (0.708 W rms
  over two layouts; top rung 54 SE above the curve's W). But the A side follows the B side's law, scaled: an A mask costs about
  **0.64–0.68** of the same mask flipped on B (0.25–0.31 W rms over 15 rungs and two layouts). It is not that fraction rung by rung
  (0.52–1.06 for 1–6 low bits), and the refitted mirror over-predicts the top rung by 0.64 W (about 4.6 SE with E70's B-rung error
  and c's).
  So E67's A single-bit prices are the wrong axis: a larger A sum sometimes costs less (`als_h4` against `alq_h8`), which no rising
  curve of it can follow. The B list, which E70 showed saturates in its own sum, carries most of the A side. A likely reason the A sum
  over-counts (a reading, not tested here): E102 (Q132, on aifoundry1 card 1) found E67's all-in A prices are composites at high
  bits, all-in over balanced 7.1× at bit 16, 3.2× at bit 20 and 2.2× at bit 22, but 1.07–1.29× at bits 0 and 6
  ([E102's README](../2026-11-01-e102-balanced-bit-prices/README.md) result 1).
- **The carry-over between operands** (E70's ρ, Q128's choice between 1.57 and 1.01): measured at k = 8 in both layouts in one session,
  **1.35 per designed bit, the same in both layouts** (1.366 ± 0.106 and 1.350 ± 0.012). Within a session, at k = 8, ρ does not depend
  on which positions flip. Between sessions it moves: E70's low layout read ρ(8) = 1.205 ± 0.041 and ρ(12) = 1.266 ± 0.011, so ρ sits
  at 1.2–1.4 at k = 8–16 over the two. The gap at k = 8 is session scatter, mostly in the B rung (E113's `lq_h8` 3.037 ± 0.189 W
  against E70's 3.248 ± 0.028), not the layout. E70's ρ(12) stands as measured.
- **E78's C2 (the broadcast A word's weight):** for an ungated fp32 lane, counting an A flip once per lane slot is the right footing,
  within 20–40% (ρ 1.2–1.4 over the two sessions). A count per broadcast word is excluded by about 8×. The gated-lane residual C2 was
  about (0.616 W with B = 0) is untouched.
- **For the power model (item 6), post hoc:** in the fixed RTL bench (Q132(b) `counts-hl.json`, `unit.nets_hier` over each ladder's
  zero) A's low ladder toggles 0.88–1.38× as many nets as B's at the same k (k = 2 to 23), where on the card it costs 0.62–1.06× the
  watts (E113's A rungs over E70's B rungs, two sessions five days apart; `posthoc.json` `bench_vs_card`). The bench counts an A flip
  1.2–1.7× too high against a B flip at the same positions, if net toggles stood for watts; at k = 8 within E113 alone (its own
  `lq_h8`) the factor is 1.41 ([`corrections-check.txt`](corrections-check.txt) C9). That is the A-side over-count item 6 lists
  ("ladders 0.86–0.90 post hoc"). A term that prices an A mask at about 0.64–0.68 of the same mask on B is what this data supports;
  nobody has fitted one.
- **For the blog:** which positions flip sets the cost, on either operand. Flip the same bit positions on the broadcast operand A
  instead of B and the card pays about two thirds of the watts for spread masks and for 8 or more low bits (nearer all of them at 2
  and 4 low bits), at half the flips; per flipped bit, A costs about 1.35 B bits in one session (1.2–1.4 over two).

**Still open:** the busy partner (every A rung here has B = 1.0); other A base words (one shared base word, E67's); fp16 and int8 (the
hl runner is fp32 only, so Q130(c) A1's int8 A-side α of 0.491 is untouched); the gated lane; why the A/B ratio sits near 1.0 at k = 2
and 4 in the low layout (0.951 / 0.928 and 1.594 / 1.505 against E70's B rungs) and near 0.63 from k = 8 up; why the refitted mirror
over-predicts the top rung by 0.64 W; another card.

## What ran

One item list, 24 runs a pass after two unrecorded `anchor_pi` burn-in runs: `anchor_pi` (first and last), `aq_h0`, `alq_h1, 2, 3, 4,
6, 8, 12, 16, 23`, `als_h2, 3, 4, 6, 8, 12, 16`, `lq_h0`, `lq_h8`, `ls_h8`, `nrd_a`, `nrd_b`. Operand set `build/hl-gen6-e113`, written
by `make_e113.py` on the box and `--check`ed. 167 of 167 files of E70's `build/hl-gen5` are byte-identical in it, and the nine new
tiles match `new-tiles.sha256` (`logs/setup.log`). E67's and E70's protocol through `hl/block.sh` unchanged: launch at a 58 °C reading
after 59 °C, 4 s runs on 1,024 minions, the rest shuffled with the pass number. The smoke, pass 1130 (`anchor_pi`, `als_h8`,
`alq_h8`, no preheat), passed its gate (block ok; every launch ok on 1,024 minions at 546 cycles per op).

- **Seven passes, 1131–1137**, 201–235 s each (`logs/queue.out`). **168 of 168 runs passed every per-run gate** (600 MHz in every
  window sample, voltage, launch on protocol at 58.0 °C, cycles per op 546.0–546.016). The die ran 57 → 58 °C in every pass after the
  first (51 → 58). The op rate held at 1.1208–1.1210 G minion-ops/s summed over the card's 1,024 minions, about 1.09 M per minion
  (`report.md`'s "op rate (Gop/s)" column is the same card-wide figure). Host load1 0.36–1.14 over the session (`logs/load.jsonl`).
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

## Corrections after verification

*Sun 1 Nov 2026, against `64e69cc3`, from an independent verifier's read (holds with fixes: one major fault, nine minor). Desk only: no
card touched, nothing re-run. **No data file, frozen file or registered verdict changed**: the registration stands as committed in
`b05e610d`, and every other file has the content it had at `64e69cc3` ([`corrections-check.txt`](corrections-check.txt) F). Wrong
sentences are replaced above. Every number here is recomputed by [`corrections-check.py`](corrections-check.py) from committed files,
and every one of them is post hoc.*

- **C1, major: the top rung was reported against one law only, and the mirror was called "a fixed fraction".** Result 2 cited
  `alq_h23` only against the curve in S_A. Result 3 now gives it under all three laws: the refitted mirror predicts 8.233 W (−0.635 W;
  −20.1 SE on the A rung alone, −4.6 SE with E70's `lq_h23` SE of 0.158 W and c's per-pass SE of 0.0067), the frozen mirror 7.813 W
  (−0.215 W, −2.0 SE; its c was fitted on E70's `alq` rungs at k = 1, 2, 4, 8, 12, 16 and 23, so for it the rung is a replicate),
  and the refitted S_A curve 5.877 W (+1.721 W, 54.5 SE). `report.md` printed these in its D2_A section. Result 3's heading now says "about two thirds …
  though not a fixed fraction rung by rung". Per rung, A over E70's B runs 0.56–0.76 for every spread mask and for 8 or more low bits
  (the top rung 0.626), and 0.52–1.06 for 1–6 low bits. "The shape is no longer open" is now "answered in outline, with residuals
  left".
- **C2: P2 tests one curve, and the reason a curve in S_A fails is now given.** P2 scores E70's one-parameter W (1 − e^(−S_A/W)).
  Post hoc, two-parameter saturating curves reach 0.459 W (W (1 − e^(−S/K)), W 7.83, K 11.90 W) and 0.462 W (W S / (S + K)), inside
  P2's INCONCLUSIVE band. The best non-decreasing function of S_A reaches 0.214 W with 8 free levels. What rules out S_A as the axis
  is that in 7 pairs a smaller sum costs more, at ≥ 3 SE paired per pass. The clearest is `als_h4` − `alq_h8`, +0.801 ± 0.024 W
  (34 SE paired; about 20 SE if the two rungs' SEs are added as if independent). Any rising function of S_A misses one of the two by
  at least 0.40 W, 14 SE of either rung.
- **C3: the spread layout did not pick the mirror over the curve on its own.** On the seven spread rungs, out of sample for both, the
  frozen curve in S_A reads 0.226 W and the frozen mirror 0.259 W (`scored.json` `rules.P3`). The README's registered caveat said so;
  the plain-language line handed to the integration lanes did not, and is corrected there. The mirror wins with both layouts
  together, each law refitted: 0.248 W against 0.708 W.
- **C4: ρ between sessions.** "E70's ρ(12) = 1.266 was a low-layout number" implied the layout explained the difference. Within E113
  the layout does not matter (1.366 ± 0.106 low, 1.350 ± 0.012 spread). E70's own low-layout ρ(8) was 1.205 ± 0.041, a value this
  README had left out. Over the two sessions ρ sits at 1.2–1.4 at k = 8–16. The gap at k = 8 is in the B rung: E113's `lq_h8` per pass
  reads 3.324, 3.407, 2.742, 2.226, 3.260 and 3.264 W against E70's 3.248 ± 0.028, while `alq_h8` agrees (2.026 against 1.957).
  E70's ρ(12) stands. The per-slot footing for E78's C2 now reads "within 20–40%", not "within 35%".
- **C5: the PMIC voltage-register reads are now stated.** The two `ettelem config` reads send `GET_ASIC_VOLTAGE`
  (`tools/ettelem/ettelem.cpp:121`). Every sampler reading sends `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE` (`:166–167`): the 14,820
  saved readings each carry `die_mv` and `reg_mv`, which the sampler prints only when those two answer, and the `die_c` reads at each
  pass's start and end (`tools/claims-v3/lib.sh:103`, `:188`, `:196`) make the same calls. These are reads, with no write. The
  statistics reset (`resetStats`, `:96`) was never sent (`since_reset_ms` −1 throughout). E114's corrected README and E118's change
  record say the same of their runs.
- **C6: the op rate's unit.** It is iters × minions per second summed over the card (`tools/claims-v3/hl/reduce_hl.py:141`, `:148`,
  "fma: minion-ops/s"): 1.1208–1.1210 G minion-ops/s over the card, 1.094–1.095 M per minion (600 MHz / 546 cycles gives 1.099 M). It
  said "Gop/s per minion", wording inherited from E70.
- **C7: what the two sides share.** The registration's question 3 says "everything after the multiplier sees the same bit pattern
  whichever side flips". The registration is frozen and is not edited. The two sides share the **flipping positions**, not the
  words, as pass 1133's dumped tiles show. In `alq_h8`, one A base word alternates with base ⊕ `0xff` down the rows, and B is 1.0
  (`0x3f800000`) everywhere. In `lq_h8`, A is 1.0 and B holds eight per-lane base words, lane l against lane 8 + l differing by
  `0xff`. `als_h8` and `ls_h8` are the same with mask `0x125249`. So with the partner at 1.0 the product is the flipping operand: one
  shared word on A, eight per-lane words on B.
- **C8: the et-who citation.** The README cited an `et-who` read "before the claim (16:01:41)" that no committed log holds. It now
  cites `logs/setup.log` (16:00:03) and `logs/session.log` (16:01:54, 10 s before the first launch at 16:02:04, `logs/smoke.log`).
- **C9: the bench line keeps its caveat, and E102 is cited.** The bench-against-card factor (1.2–1.7×) compares E113's A rungs with
  E70's B rungs, two sessions five days apart. The README now says so and gives the one-session value at k = 8 (1.41, E113's own
  `lq_h8`). It holds only if net toggles stood for watts. E102's finding that E67-style all-in A prices are composites at high bits
  (7.1×, 3.2× and 2.2× all-in over balanced at bits 16, 20 and 22; 1.07–1.29× at bits 0 and 6) is cited as a likely reason the A sum
  over-counts. That is a reading: E102 ran on another card. In the text handed to the integration lanes, "about 0.68" beside the
  frozen constant's 0.26 W now reads 0.64–0.68.
- **C10: small wording.** "Not *how many*" is now "not by *how many* alone", because the cost rises with k in each layout. The smoke
  is dated by its first launch, 16:02:04; 16:01:59 is its plan line. D1_A's dip at k = 4 (+1.233 W, below k = 3's +1.692) is named;
  B's contrast has none. In the text handed to the integration lanes, "last week's ladder" is now "E70's ladder of 27 Oct": E70 ran
  in the same ISO week.
- **C11, found while correcting (not a verifier fault):** the header's two links into `tools/claims-v3/e113/` were one directory short
  (`../../../` resolves under `docs/`). They now use `../../../../`.

## Files

| file | what |
|---|---|
| `corrections-check.py`, `corrections-check.txt` | the corrections' numbers, recomputed from committed files (standard library only); F checks the data and frozen files against `64e69cc3` |
| `posthoc_e113.py`, `posthoc.json` | the post hoc numbers the README labels post hoc: the B-side law on the A rungs, the frozen mirror's residuals, the bench against the card |
| `report.md`, `scored.json` | **the registered result**: `score_e113.py` over the six passes the gates keep, every contrast paired per pass; the arms in `report.md` § Arms and `scored.json` `arms` |
| `hl.json`, `runs.csv`, `reduce.txt` | `hl/reduce_hl.py` over all seven passes (its own pass gate sets aside none); `runs.csv` is the scorer's input |
| `hl-leak0.2/0.3/0.4.json`, `runs-leak*.csv`, `reduce-leak*.txt` | the leakage arms |
| `predictions-e113.json`, `manifest.json` | the frozen predictions as run; the operand set's items and designed flip counts |
| `aifoundry3/e113/p1131…p1137` | per pass: `block.json`, `configs.json`, `gen.sha256`, `manifest.txt` (`et-lab-manifest`), `marks.jsonl`, `run.log`, `runs.jsonl`, `code.sha256`, `telemetry.jsonl.gz`, `tiles/` |
| `aifoundry3/smoke-p1130` | the smoke pass |
| `logs/` | `setup.log` (files only: the operand set, byte-identity, dry run), `session.log`, `queue.out`, `smoke.log`, `load.jsonl`, `config-session-start.json` and `config-session-end.json`, the session's start and end times |

Nothing on the card was changed: no governor, TDP, threshold or clock write, no reset, no `--reset-ms`, no PMIC command (no PMIC
write, no firmware-revisions query). As in every lab run with the stock sampler, the two `ettelem config` reads sent
`GET_ASIC_VOLTAGE`, and each sampler reading sent `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE`: the 14,820 readings saved in the
passes' and the smoke's `telemetry.jsonl.gz`, and the short `die_c` reads at each pass's start and end. These read PMIC voltage
registers, with no write (`tools/ettelem/ettelem.cpp:121`, `:166–167`; E118's
[change record](../../../../tools/claims-v3/e118/CHANGE-RECORD.md) lists the handlers). No statistics reset was sent
(`since_reset_ms` −1 in every saved reading). `et-who` showed no holder at setup (16:00:03, `logs/setup.log`), at the session's start
(16:01:54, 11 s after the claim and 10 s before the first launch, `logs/session.log`) and after the session (16:28:42). A read just
before the claim (16:01:41) was not saved, so it is not cited. Other lab users' idle logins on the host did not block (E60's departure
D1, as `hl/block.sh` implements it), and none of their names is recorded here.
