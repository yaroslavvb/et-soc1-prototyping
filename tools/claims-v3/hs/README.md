# V3-HS: E70 — the saturation ladder and the A-side multi-bit ladder (Q129)

*Pre-registered Tue 27 Oct 2026 (week 44) on aifoundry3, before the first measured pass; any change after this
commit goes in the Amendments section at the end, dated, before the data it touches. Request Q129, which is
Q128 §5 item 2 (the saturation ladder) and §5 item 4's third point (no A-side multi-bit ladder). Card:
**aifoundry3 only**, whose governor is latched at 600 MHz by its boot-time TDP 0
(`docs/findings/14-card-behaviour.md`) — the same card, clock and voltage as E65's B-side scan and E67's A-side
scan, so every price here is addable to theirs without a conversion. Every number below is a 600 MHz, ~0.522 V
number. **The governor is not touched: E70 changes no card setting of any kind.***

## Why

The per-bit price list E65 (B side, 32 positions) and E67 (A side, 32 positions) built **over-predicts a whole
random word by about 2×**. E67's own closure test: summing the measured per-position prices over the designed
flip histogram of `nrd_a` (A random fp32, B = 1.0) predicts 17.30 W against a measured 7.48 ± 0.23 W, a ratio of
**0.43**; for `nrd_b` (B random) 21.85 W against 10.89 ± 0.02 W, ratio **0.50**. That is the single largest
remaining error in the Q128 chain's use of the price list, and Q128 §5 names its two candidate causes:

- **shared wires** — the sub-additivity is set by **which** bits flip. Each flipped position wakes a set of nets
  in the Booth recoder, the partial-product array and the carry-save tree; two positions whose sets overlap are
  charged twice for the same wires when their prices are added. The deficit then tracks the *size of the union*,
  so it is large exactly where the single-bit prices are large.
- **interaction** — the sub-additivity is set by **how many** bits flip. A fixed cost of making the operand move
  at all (E67's A13 "turn-on" `T`) is charged once per position by a per-bit price list, so summing h prices
  charges it h times instead of once; beyond that, flips add.

**One knob separates them: the layout of the flipping bits at fixed Hamming weight.** `lq_h<h>` flips B's **low
h** mantissa bits together; `ls_h<h>` flips **h bits spread evenly** over the 23 mantissa positions. At h = 8
their additive sums are 3.886 W and 12.628 W — a factor of 3.2 — while h is identical. `ls` has never run on
this card (E60 ran it only on aifoundry2 at 800 MHz, where amendment A3 had to exclude `ls_h8` because the
governor dipped the clock). At **h = 23 the spread mask is the low mask**, so the two layouts coincide there by
construction: the ladder's top rung is a built-in tie as well as the ceiling anchor.

The second half closes Q128 §5 item 4's third point. Every multi-bit measurement so far is on **B**. The
carry-over from a B-side price to an A-side one is a *choice* between two defensible numbers — the raw
single-bit per-bit ratio (median **1.57** over the 23 mantissa positions) and the turn-on-corrected marginal one
(median **1.01**) — and Q128 records that the choice moves the prediction by 6%. `alq_h<k>` is the analogue of
`lq_h<k>` on the A operand: A's low k mantissa bits flip together, B held at the quiet partner 1.0, k = 1, 2, 4,
8, 12, 16, 23. With it the carry-over is **measured at the Hamming weights a real word actually has**, not
chosen at h = 1.

## The three candidate laws, and what each predicts

Write `S(mask)` for the **additive sum**: the sum of E65's (B) or E67's (A) registered single-bit prices over
the flipping positions, each measured against its own constant-operand zero on this card.

| | Law | Form | Fitted on |
|---|---|---|---|
| **A** | additive (the price list's own null) | `dW = S(mask)` | nothing — no free parameter |
| **H-strong** | "how many": the Hamming weight alone | `dW = f(h)`, one curve in h for **both** layouts | nothing at matched h: `dW_ls(h) − dW_lq(h) = 0` |
| **H-offset** | "how many": one shared turn-on charged once | `dW = S(mask) − (h−1)·T` | `T` = 1.351 ± 0.281 W, E67's grid |
| **W** | "which bits": shared wires / coverage | `dW = W∞·(1 − exp(−S/W∞))` | `W∞` = **12.58 W**, fitted on E60's lq ladder **alone** |

`predict_e70.py` writes every number below into `predictions-e70.json` beside the data, from already-published
aifoundry3 numbers only: E65's `bits`, E67's `a_bits` and grid excess, and E60's `lq` rungs on this card. **Law W
has one free parameter and it is fitted on E60's existing lq ladder before any E70 data exists**, so its
predictions for every `ls` and every `alq` rung are frozen with no freedom left.

**H-offset is already dead and is registered as such, not as a discovery.** With `T` = 1.351 W from E67's grid it
predicts a *negative* step for six of the nine lq rungs (lq_h4: −2.03 W), and the per-rung `T` implied by E60's
own lq ladder runs **0.10 → 1.28 W**, a 13× spread, instead of one constant. Its only live form is a free-`T` fit,
which D3 scores. The live contest is **H-strong against W**.

### The registered predictions

| item | h | flipping bits | S (W) | law A | law H-offset | **law W** | E60 on this card |
|---|---|---|---|---|---|---|---|
| `lq_h1` | 1 | 0 | 0.625 | 0.625 | 0.625 | **0.610** | 0.594 ± 0.011 |
| `lq_h2` | 2 | 0–1 | 1.138 | 1.138 | −0.213 | **1.088** | 0.841 ± 0.131 |
| `lq_h3` | 3 | 0–2 | 1.543 | 1.543 | −1.159 | **1.453** | — (new rung) |
| `lq_h4` | 4 | 0–3 | 2.026 | 2.026 | −2.028 | **1.871** | 1.712 ± 0.012 |
| `lq_h6` | 6 | 0–5 | 2.970 | 2.970 | −3.785 | **2.646** | — (new rung) |
| `lq_h8` | 8 | 0–7 | 3.886 | 3.886 | −5.572 | **3.343** | 3.206 ± 0.054 |
| `lq_h12` | 12 | 0–11 | 7.078 | 7.078 | −7.784 | **5.414** | 5.536 ± 0.027 |
| `lq_h16` | 16 | 0–15 | 15.122 | 15.122 | −5.144 | **8.799** | 8.299 ± 0.025 |
| `lq_h23` | 23 | 0–22 | 40.384 | 40.384 | 10.659 | **12.073** | 12.261 ± 0.021 |
| `ls_h2` | 2 | 0, 12 | 2.192 | 2.192 | 0.840 | **2.011** | never run here |
| `ls_h3` | 3 | 0, 8, 15 | 3.693 | 3.693 | 0.991 | **3.200** | never run anywhere |
| `ls_h4` | 4 | 0, 6, 12, 17 | 5.410 | 5.410 | 1.357 | **4.397** | never run here |
| `ls_h6` | 6 | 0, 4, 8, 12, 15, 19 | 9.460 | 9.460 | 2.704 | **6.649** | never run anywhere |
| `ls_h8` | 8 | 0, 3, 6, 9, 12, 14, 17, 20 | 12.628 | 12.628 | 3.170 | **7.970** | never run here |
| `ls_h12` | 12 | 0, 2, 4, 6, 8, 10, 12, 13, 15, 17, 19, 21 | 19.987 | 19.987 | 5.125 | **10.012** | never run here |
| `ls_h16` | 16 | 0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 14, 16, 17, 19, 20, 22 | 28.039 | 28.039 | 7.772 | **11.226** | never run here |
| `alq_h1` | 1 | A 0 | 0.459 | 0.459 | 0.459 | **0.451** | = `abit_0`, E67: 0.459 ± 0.241 |
| `alq_h2` | 2 | A 0–1 | 1.599 | 1.599 | 0.248 | **1.502** | — |
| `alq_h4` | 4 | A 0–3 | 3.150 | 3.150 | −0.903 | **2.787** | — |
| `alq_h8` | 8 | A 0–7 | 5.784 | 5.784 | −3.674 | **4.637** | — |
| `alq_h12` | 12 | A 0–11 | 9.025 | 9.025 | −5.838 | **6.441** | — |
| `alq_h16` | 16 | A 0–15 | 15.913 | 15.913 | −4.354 | **9.030** | — |
| `alq_h23` | 23 | A 0–22 | 32.852 | 32.852 | 3.127 | **11.657** | — |

`alq_h1` is **byte-identical** to E67's `abit_0` (same shared A base word, same single flipped bit), checked in
setup: a free tie between the two experiments' A-side numbers.

Law W's `alq` column above uses the **same** ceiling as the B side (12.58 W) — the registered prediction that the
ceiling is a property of the multiplier tree, not of the operand side. The alternative, a ceiling that scales with
the operand's designed flip rate (`W∞/2` = 6.29 W, since A flips 2,048 bits per multiply-add against B's 4,096),
is written to `predictions-e70.json` as `alq_half_ceiling` and reported beside it.

## The discriminators, pre-registered

**D1 — the matched-h layout contrast.** The experiment's sharpest test, and parameter-free for two of the three
laws:

| h | `S_ls − S_lq` | law A and law H-offset predict | law H-strong predicts | **law W predicts** |
|---|---|---|---|---|
| 2 | 1.054 W | 1.054 W | 0 | **0.923 W** |
| 3 | 2.150 W | 2.150 W | 0 | **1.748 W** |
| 4 | 3.384 W | 3.384 W | 0 | **2.526 W** |
| 6 | 6.489 W | 6.489 W | 0 | **4.004 W** |
| 8 | 8.742 W | 8.742 W | 0 | **4.627 W** |
| 12 | 12.909 W | 12.909 W | 0 | **4.598 W** |
| 16 | 12.916 W | 12.916 W | 0 | **2.427 W** |
| 23 | 0 (same mask) | 0 | 0 | **0** |

The `−(h−1)T` offset cancels in a matched-h difference, so **A and H-offset make the same D1 prediction** and D1
alone cannot separate those two; D2 and D3 do that. D1's job is H-strong against the rest, and then law W's
specific curve against pure additivity.

**D2 — which variable the two layouts collapse on.** Fit the 15 B-side rungs (9 lq + 6 ls, excluding the shared
h = 23 point, which both layouts own) twice:
- `R_h`: residual rms about the best monotone curve in **h** (a free value per h, i.e. the pooled within-h scatter
  between the layouts — the best any "how many" law can do);
- `R_S`: residual rms about the one-parameter coverage curve in **S** with `W∞` **re-fitted on E70's own 15 rungs**
  (reported beside the frozen `W∞` = 12.58 W version).

**D3 — is a single turn-on enough?** Per rung, `T_implied = (S − dW)/(h − 1)`. H-offset requires one constant `T`
across both layouts and every h.

**D4 — the carry-over between operands, measured.** Per flipped bit at matched h,
`rho(h) = [dW_alq(h)/(2048·h)] / [dW_lq(h)/(4096·h)]`, over h = 1, 2, 4, 8, 12, 16, 23 — against the two numbers
Q128 had to choose between (raw single-bit median 1.57, turn-on-corrected median 1.01) and against law A's own
prediction of `rho(h)` (1.47, 2.81, 3.11, 2.98, 2.55, 2.10 at h = 1, 2, 4, 8, 12, 16).

**D5 — the closure, re-run with the saturation law.** Take E67's `nrd_a` and `nrd_b` (re-measured in E70's own
passes, so the comparison is within-pass): price their designed flip histograms with the price lists as E67 did,
then pass the summed `S` through whichever law D2 selects, and report the ratio measured/predicted beside E67's
0.43 and 0.50.

## Predictions, frozen with this commit

- **P1 (the layouts do not collapse on h).** At h = 8, `dW_ls − dW_lq` > 2.0 W at ≥ 3 SE. *H-strong requires 0;
  law A requires 8.74 W; law W requires 4.63 W.* A value under 2.0 W at h = 8 is a **PASS for "how many"** and the
  headline would be that the sub-additivity is set by the number of flips, not by which ones.
- **P2 (the deficit is set by which bits, and law W's frozen curve holds).** Over the 6 `ls` rungs (h = 2..16) the
  rms of (measured − law W's frozen prediction) is **≤ 2.0 W**, and smaller than the rms against law A by at least
  a factor of 3. *Law A's own rms over those rungs would be ≥ 7 W if law W is right.*
- **P3 (the price-per-bit falls with the additive sum, not with h).** Spearman ρ between `dW/S` and `S` over all
  15 B-side rungs is < −0.7; the partial relation of `dW/S` with h at fixed S is weaker than with S at fixed h
  (reported as the two Spearman ρ of the residuals of a single-variable fit).
- **P4 (one turn-on is not enough).** D3's `T_implied` spans more than a factor of 4 over the 15 B-side rungs, and
  at least one rung's `T_implied` lies more than 3 SE from the grid's 1.351 W.
- **P5 (the A side saturates too, with a shared ceiling).** The `alq` ladder bends: `dW_alq(23)/23` is below
  `dW_alq(1)` by at least a factor of 2. The fitted A-side ceiling is within a factor of 1.5 of the B-side
  ceiling — i.e. nearer 12.58 W than 6.29 W. *A ceiling near `W∞/2` instead means the ceiling scales with the
  operand's flip rate and the two sides do not share one saturating resource.*
- **P6 (the carry-over at a real Hamming weight).** `rho(h)` at h = 12 and h = 16 (near a random fp32 word's
  13.9 average Hamming distance) lies in **[0.7, 2.5]**, and `rho(16) < rho(2)` — the single-bit carry-over
  over-states the multi-bit one. The measured `rho(12..16)` is the number Q128's chain should use, and it is
  reported with its interval whatever it is.
- **P7 (the closure improves).** With the law D2 selects, D5's ratios for `nrd_a` and `nrd_b` both lie in
  **[0.7, 1.4]** — against E67's 0.43 and 0.50 from the raw additive sum. This is the prediction that matters for
  the Q128 waterfall: it is what moves pJ from "unaccounted" to "accounted".
- **P8 (the replicate).** The 7 `lq` rungs E60 measured on this card reproduce within **0.6 W** of E60's values,
  and `lq_h23` within 1.0 W. E60 ran 7 days earlier with a different operand set directory and a different pass
  set; a failure here is a card-stability result and is reported as one, and would qualify every other number.

## Decision rules

Each prediction is scored PASS / FAIL / UNDECIDED against its own stated band, in the results section of the data
README and in E70 of `docs/findings/03-experiments.md`. UNDECIDED is used when the measurement's SE cannot
separate the bands. **The verdict on the Q128 §5 question is read off D1 and D2 together**, and is one of:
- *shared wires (which bits)* — P1 PASS in the "does not collapse on h" direction and `R_S` < `R_h`/2;
- *interaction (how many)* — P1 in the under-2.0 W direction and `R_h` < `R_S`/2;
- *both, with weights* — neither collapse wins by 2×: the two residuals are reported with the fitted law that
  carries both terms, and the verdict says so rather than picking one.
A block whose passes do not survive the gates is reported as not run, never re-registered.

## Protocol

E67's protocol, unchanged, through `hl/block.sh`: `flock -n /run/lock/etsoc-shire0.lock` held for the pass, every
device process under `timeout 10` with `--stop-file`, the pass stops at a 78 °C reading, on telemetry older than
3 s, or when another user appears **on this card** (E60's departure D1: another user's idle shell login does not
block, and aifoundry3 has several; failing closed when `et-holders` is unreadable). Launch reading **58 °C after
59 °C**, exactly E65's and E67's, so every run in the three experiments is launched identically. 4 s runs; two
unrecorded `anchor_pi` burn-in runs start every pass; `anchor_pi` runs first and last; everything else shuffled
with the pass number as seed. Before the first launch: `et-boot-check --status`, `et-who`, `who`, `uptime`,
`make_hl.py --check`, the byte-identity check below, and a `V3_DRY=1` dry run. The card is claimed in
`#community-lab` before the first launch and released after — **by appending to the claim, never replacing it**
(E67's A17). Card time at most **75 minutes**.

**One item list, one pass** (29 runs a pass), so the two ladders, their zeros and the random anchors all share
each pass's offset:

```
anchor_pi, lq_h0, lq_h1, lq_h2, lq_h3, lq_h4, lq_h6, lq_h8, lq_h12, lq_h16, lq_h23,
ls_h2, ls_h3, ls_h4, ls_h6, ls_h8, ls_h12, ls_h16,
aq_h0, alq_h1, alq_h2, alq_h4, alq_h8, alq_h12, alq_h16, alq_h23, nrd_a, nrd_b
```

Passes **790** upward, target 7, minimum 4 for a reported result. Operand set `build/hl-gen5`; **every operand
file E60, E65 and E67 ran must be byte-identical in it** (checked against `build/hl-gen4` and `build/hl-gen3` on
the box before the first launch, as `run_e67.sh setup` does), or the experiment does not launch.

**Power.** Law W puts the dearest rung (`ls_h16`) at 11.2 W above a 36.5 W base, about 48 W — below
`anchor_randn`'s 52.5 W measured on this card. If law A were right, `ls_h16` would draw about 64.5 W. Registered
abort: a rung whose board power reads **≥ 70 W**, or a die reading ≥ 72 °C, is dropped from later passes and
reported by name; `block.sh`'s 78 °C stop stands above that. No card setting is changed, no clock is set, the
governor is not touched.

## Departures from E67's protocol, and why

- **D-a, the pass gate is the spread of every constant-operand run,** not `anchor_pi`'s first-versus-last drift.
  E67's amendment A15 found the registered drift gate fired on one of four degraded passes and missed three. E70
  carries three constant-operand items (`lq_h0`, `aq_h0`, `anchor_pi` twice — four runs, one physical state by
  three routes, which E67 measured as agreeing to 0.42 W). **Registered gate: a pass whose four constant-operand
  runs span more than 0.45 W is set aside**, alongside E67's own two gates (more than one failed run; `anchor_pi`
  drift above 0.3 W), and every gate's verdict is reported per pass.
- **D-b, the host's CPU load is recorded.** E67's amendment A16 found another lab user's CPU work on the host
  changed the measured op rate 1.121 → 1.085 Gop/s mid-session and was invisible to every registered gate.
  `run_e70.sh` samples `/proc/loadavg` and `/proc/stat` every 2 s for the whole session into
  `build/e70-load.jsonl`, and the reduction reports the load average and the op rate per pass. **Registered rule:
  a pass whose mean 1-minute load average exceeds 4.0, or whose mean op rate differs from pass 790's by more than
  1%, is reported as load-disturbed; it is kept in the registered reduction and a labelled sensitivity over the
  undisturbed passes is reported beside it.** (Kept, not dropped, because E67's A16 showed the correlation is not
  monotone.)
- **D-c, no RTL predictions for the new rungs.** `predict_hl.py` needs Verilator, absent on this host (E65's D3).
  `lq_h3`, `lq_h6`, every `ls` rung and every `alq` rung are registered against the three measured laws above, not
  against an RTL replay; `reduce_hl.py` reports `pred_dW: null` for an item with no prediction, and amendment A19
  below keeps the bus/nets regressors from reading one that does not exist.
- **D-d, the leakage correction.** The registered slope is the one `reduce_hl.py` fits within-run on this card's
  own passes (E67 read 0.175 W/°C over 547 runs; E65 0.17–0.18). **Registered sensitivity: the whole reduction is
  re-run at 0.2, 0.3 and 0.4 W/°C** — the band that brackets E66's measured aifoundry2 idle slope of 0.294 W/°C —
  and every headline number is quoted with the spread those three give. aifoundry3's own idle slope is measured by
  E71, not here; until it exists this is a labelled sensitivity, not a correction.

## Files

`predict_e70.py` (the predictions above, from published data only), `run_e70.sh` (setup, the load sampler and the
pass queue on the box), `collect_e70.sh` (reduce every finished pass and assemble the data directory),
`report_e70.py` (the law fits, D1–D5 and the scored rules). The ladder itself runs `tools/claims-v3/hl/`
unchanged apart from amendments A18 and A19.

## Amendments

**A18 to `tools/claims-v3/hl/make_hl.py` (Tue 27 Oct 2026, with this commit, before any E70 data).**
`LADDER_H` gains h = 3 and 6 (so `lq_h3`, `lq_h6` and, as a by-product of the shared loop, `lb_h3`, `lb_h6`),
`SPREAD_H` gains h = 3 and 6, and a new family `alq_h<k>` for k ∈ {1, 2, 4, 8, 12, 16, 23} flips A's low k
mantissa bits on E67's shared A base word with B = 1.0 and carries `zero: aq_h0`. No RNG draw order changes, so
**every file E60, E65 and E67 ran is byte-identical in `build/hl-gen5`** — 154 of 154, checked on the Intel
against the committed generator before this commit and re-checked on the box against `build/hl-gen4` before the
first launch. *Why:* the saturation ladder needs h = 3 and 6 to see the low-h bend, the spread layout needs the
same rungs as the low one, and the A side has no multi-bit ladder at all.

**A19 to `tools/claims-v3/hl/reduce_hl.py` (Tue 27 Oct 2026, with this commit, before any E70 data).**
`ZERO["alq"] = "aq_h0"`; the `bus` and `nets` regressors of the lq/lb slope fit skip a rung with no entry in
`predictions.json` (`lq_h3`, `lq_h6` have no RTL replay — without the guard the fit raises); `ls_vs_lq` reports
h = 3 and 6 beside 2, 4, 8, 12, 16, writing no key for a rung that did not run. Every E60, E65 and E67 item has an
RTL prediction and an unchanged zero, so **their reductions are unchanged** (verified by re-reducing E67's
committed passes with the amended code before the first launch).
