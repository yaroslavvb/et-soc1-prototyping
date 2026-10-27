# V3-RF: what one bit stored in a register's own cell costs (E74, Q129)

*Pre-registered Tue 27 Oct 2026 (week 44), 14:0x–15:3x PDT, on aifoundry1 (build and dry run only — no card was
opened anywhere for this file). Every prediction and every decision rule below is frozen at the commit that adds
this file, before the first measured pass on aifoundry3. Any change after that goes in Amendments at the end,
dated, before the data it touches.*

## The question

Stop 4 of the Horace Hub's Levels tab asks **what the register file's own cells cost**. Every ladder before this
one held the sources still — `gen_ops.py`'s rotating block is built so that "sources are never overwritten and
sinks never read" — so the only bits that moved were on the read ports and the result path, and the stored bit's
own price was never in the design. E60 priced the read-port bit (20.83 ± 0.10 fJ) and the result bit (30.00–31.17
fJ) that way. E61 reached the cell once, and the reach was the problem:

| | E61 (family V, 21 Oct) | E74 (this) |
|---|---|---|
| rungs | `d1b_h0/h16/h32`: cell bits 0/128/256 per op — **and port bits 0/128/256**, perfectly correlated | `rf_k32 … rf_k192`: cell bits 32/64/96/128/160/192 per op, **port bits 96 on every rung** |
| estimator | the difference of two kernels' slopes (`df.un1b.fnot` − `df.un1a.fnot`), each against its own zero | the slope **inside one mode**, one `.text`, one build |
| what it carries | α(mode), 0.125 address bits/op, and a 3% issue-rate difference (0.7574 vs 0.7356 ops/cycle/hart) that is ~100× the signal | nothing: the instruction stream is byte-identical across rungs and only the 256 B operand image changes |
| result | aifoundry3 **1.267 fJ ± 0.151** (12 passes, t = 8.4); **not identified** on aifoundry2 or aifoundry1 card 0 | — |

E61's number is real but rests on a cross-kernel subtraction on one card. E74 asks the same question with the
confound removed by construction, and with the cell moved over a 6× range while the ports do not move at all.

## The design

`df.un1b.fnot` (gen_df.py, mode 305, in a build configured `-DENERCAT_DF=ON`) is 16 ops per loop iteration:

    phase 1:  fnot.pi f(8+i), f(i)            i = 0..7
    phase 2:  fnot.pi f(8+((i+3)%8)), f(i)    i = 0..7

`load_vsrc(src)` puts the eight 256-bit sources S0..S7 in f0..f7 once, before the loop; they are never written.
Per iteration, with all arithmetic over 256-bit `.pi` registers:

| what moves | count per iteration | per op |
|---|---|---|
| read port (one source per op): S0,S1,…,S7,S0,…,S7 | 2 · Σ_j popcount(S_j ^ S_{j+1}) | **C** |
| result bus: ~S0,…,~S7,~S0,…,~S7 (same deltas) | the same | **C** |
| the **cell** of sink f(8+m): ~S_m after phase 1, ~S_{(m−3) mod 8} after phase 2, ~S_m again next iteration | 2 · Σ_m popcount(S_m ^ S_{(m−3) mod 8}) | **k** |
| read index, sink index, op count, opcode | fixed by the kernel | fixed |

So an operand set with **popcount(S_j ^ S_{j+1}) = C for every j** and **popcount(S_m ^ S_{(m−3) mod 8}) = k for
every m** moves the register file's cells, and nothing else, by k bits per op. `make_rf.py` builds such sets with
C = 96 and k = 32, 64, 96, 128, 160, 192, and holds **popcount(S_j) = W = 128 for every j and every rung** as
well, so no rung carries more ones than another (a bitline-precharge or static term cannot masquerade as a
slope). The construction is exact — whole cyclic orbits of 8-bit indicator vectors over the 256 bit positions —
and `--check` re-derives C, k and W from the bytes on disk; nothing is trusted from the algebra.

k = 0 is **not** a rung and cannot be: 3 generates Z8, so k = 0 forces every S_j equal and C = 0 too. The
ladder's zero is the intercept of the fit, which is what makes this a ladder and not a pair.

### The null test, and why it is not the estimator

`df.un1a.fnot` (mode 304) is the same 16 ops with the second phase's sinks **not** rotated, so every sink is
rewritten with the value it already holds: ports and result path identical, cells still. `rfz_k32`, `rfz_k96` and
`rfz_k192` run the three extreme operand images through it. Their power must **not** depend on k. They are a
falsification test, not the estimator: a different `.text` brings back α(mode) and E61's loop-address issue-rate
trap (docs/findings/14-card-behaviour.md, "Traps": a kernel's issue rate is set by where its loop sits).

## Frozen predictions

Anchors, all aifoundry3, 600 MHz, `--harts 1`, board energy above idle: E60's read-port bit 20.83 ± 0.10 fJ and
result bit 30.00–31.17 fJ; E61's e_cell 1.267 ± 0.151 fJ; the ½CV² prior 0.3–3 fJ at 0.52 V; `df.un1b.fnot` runs
0.7574 ops per cycle per hart, so 1,024 harts at 600 MHz issue 4.6535 × 10¹¹ ops/s and **1 fJ per cell bit is
4.6535 × 10⁻⁴ W per (bit per op)**.

| # | prediction | number |
|---|---|---|
| P1 | e_cell, the slope ÷ cell bits per op | **0.8–1.8 fJ** per flipped cell bit (point prior 1.27, E61's aifoundry3 value) |
| P2 | board power, rung 192 − rung 32 (160 bits/op) | **+60 to +134 mW** (94 mW at 1.27 fJ) |
| P3 | the ladder is **linear** in k | residual rms of the straight-line fit ≤ 20 mW, and no monotone curvature ≥ 3 SE (unlike the single-bit arithmetic price list, which over-predicts a random word ~2×, a cell write has no shared wire to saturate) |
| P4 | the `rfz` null | board power across `rfz_k32`, `rfz_k96`, `rfz_k192` flat within ±2 SE: |slope| < 0.3 × the `rf` slope |
| P5 | issue rate | `ops_per_cycle_per_hart` = 0.7574 ± 0.0020 on every `rf_` rung (one mode, one build: the data must not move it) and 0.7356 ± 0.0020 on every `rfz_` rung |
| P6 | implied cell capacitance | 2 e_cell / V² at V = 0.5218 → **5.9–13.2 fF** per cell bit (E61: 9.3 fF) |

## Decision rules (registered)

1. **The estimator** is the least-squares slope of board power on cell bits per op over the six `rf_` rungs,
   fitted **within each pass** and then averaged over passes; the quoted interval is the two-sided t interval on
   the between-pass scatter (df = passes − 1), as E60, E65 and E61 all did. The rail estimate is the same fit on
   the minion-rail reduction, reported beside it, never instead of it.
2. **The rate gate** (dtf's 0.2% gate): a run whose `ops_per_cycle_per_hart` departs from its item's median by
   more than 0.2% is dropped, and a rung that loses more than one run in a pass voids that pass.
3. **The null gate**: if P4 fails, e_cell is reported as **not identified** by this design and the slope is
   published as a bound only, with the failure named. A failed null is not rounded into a result.
4. **Temperature**: every run launches from the hl/E67 protocol (preheat to 59 °C, launch at the first reading
   ≤ 58 °C, cap 78 °C). The pass is voided if three runs in a row cannot reach the launch reading (run_hl.py's
   own rule, exit 5). Die temperature at launch is recorded per run; the reduction reports the slope with and
   without a temperature covariate, and E66's measured idle slope (0.294 W/°C, aifoundry2) is used only as a
   labelled sensitivity — aifoundry3's own idle slope is E71's job, not this one.
5. **Resolution, stated in advance**: with E60's residual rms (0.032 W per point) the slope's SE is
   0.032/√(Σ(k−k̄)²) ≈ 1.1 × 10⁻⁴ W per bit/op per pass-set of 5, i.e. **±0.23 fJ at 5 passes and ±0.16 fJ at
   10**. So 5 passes separate P1 from zero and from 3 fJ, and do **not** separate 1.27 from 0.8. If the pass
   scatter is worse than E60's, the result is reported as a bound. **Target: 6 passes, extend to 10 if the lane
   is free.**
6. **What it changes.** A cell bit at 1.27 fJ with 256 bits of register content per `.pi` op puts the whole
   register file's cell energy at ~0.3 pJ per 256-bit op — against the 5.783 pJ board cost of one fp32
   multiply-add (Q128), a share of **about 0.08 pJ per MAC** at the MAC's 64-bit-per-operand scale, which is
   where it enters the waterfall: it is part of the "register-file read ports, operand bus, result path and
   pipeline registers" that Q128 §2 lists as unpriced in the 1.946 pJ bottom-up ledger. The experiment's output
   is that number with an interval, plus the first same-kernel confirmation of E61's cross-kernel value.

## How to run it (aifoundry3, after E70 and E71)

    ssh aifoundry3
    cd ~/aifoundry                                  # the tree that holds the binaries
    bash tools/claims-v3/rf/run_e74.sh setup        # operand set + --check, .text hashes, dry run. No card.
    bash tools/claims-v3/rf/run_e74.sh go 7410 6    # six passes, detached; log build/e74-rf.log

**On aifoundry1 the dry run needs a card named** — `lib.sh` refuses to guess between its two cards —
so prefix it with `V3_DEVICE=0`. Under `V3_DRY=1` that opens nothing: it only names the data directory.

`setup` writes `build/rf-gen` (or `$RF_GEN`) and prints the `.text` hashes of the host binary and the device
kernel; they must equal aifoundry1's, recorded in this experiment's data directory, before any number from the
two boxes is compared. Watch it with `ssh aifoundry3 'tail -3 ~/aifoundry/build/e74-rf.log'`; stop it between
passes with `touch ~/aifoundry/build/rf-STOP`.

Data lands in `build/claims-v3/aifoundry3/rf/p<pass>/`. Collect it into
`docs/reports/data/2026-10-27-e74-register-file-cells/` (date of the run), with `hl.json`-style per-item means,
`runs.csv`, the `.text` hashes, `gen.sha256`, and a README in the repo's style: results first, registered vs
happened, departures dated.

## Risks, and what each one does to the result

- **Resolution.** The whole span is ~94 mW on a board that idles near 20 W. This is the same regime E60 and E61
  worked in and the same protocol, but it is the first risk, not the last. Mitigation: 6 passes, shuffled order,
  the `anchor_pi` drift anchor at the start and end of every block (run_hl.py's own), and rule 5's bound.
- **The construction could be wrong.** Mitigation: `--check` recomputes C, k and W from the files; the `rfz`
  null (P4) catches a leak into the ports; the rate gate (P5) catches a leak into the issue rate.
- **A second hart.** `--harts 1` keeps the comparison on E60's and E61's basis. `--harts 2` would double the op
  rate and the signal; it is **not** in this registration (run_hl.py passes `--harts 1`), and if it is wanted it
  is a separate experiment with its own number, not an amendment.
- **The two kernels differ in issue rate by 3%** (0.7574 vs 0.7356). This design never subtracts them, which is
  the point; the `rfz` arm is only read against itself.
- **Another user, or the demo service on aifoundry3** (14-card-behaviour.md): `block.sh` stops on another user's
  device process or lock, holds `/run/lock/etsoc-shire0.lock`, and caps every device process at `timeout 10`.
- **No card is opened on aifoundry1.** `setup` and `dry` run under `V3_DRY=1`; the build and the operand set are
  all that happens there.

## Files

| file | what it is |
|---|---|
| `make_rf.py` | the operand sets and their designed counts; `--check` re-derives them from the bytes; `--grid` prints the reachable k at the registered C and W |
| `block.sh` | one pass as a `lib.sh` block: card lock, sampler, `timeout 10` per device process, stop on another user; the runner is `hl/run_hl.py` unchanged |
| `queue_rf.sh` | passes back to back, detached, stopping on `build/rf-STOP` |
| `run_e74.sh` | `setup` / `dry` / `go <first> <n>` |
| `predictions.json` | P1–P6 and the decision rules, machine-readable, frozen with this commit |
| `../text_hash.sh` | the `.text` hashes of the host binary and the device kernel, so two boxes' builds can be compared before their numbers are |

## Amendments

*(none yet)*
