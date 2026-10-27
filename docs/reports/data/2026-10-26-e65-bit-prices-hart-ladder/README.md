# E65 — every bit position, the flow-M case, and the hart ladder (Q126, aifoundry3, 2026-10-26)

*Pre-registered in [`tools/claims-v3/hb/README.md`](../../../tools/claims-v3/hb/README.md) (design, departures
D1–D4, predictions A1–A3, B1–B2, C1–C4, D1, decision rules, amendments A4–A7), committed as `6da964d2` before the
first measured pass. Card runs 2026-10-26 from 16:45 PDT on **aifoundry3 only**, whose governor is latched at
600 MHz, so every number here is a 600 MHz, ~0.522 V number. Claimed in `#community-lab` at 16:45 and released
after the last pass.*

## What it measures

| Block | Question it closes | Items |
|---|---|---|
| **A** | gap 6: a flip's price by bit position, with no law for it (E60 built 13 positions and ran 6) | `bit_0` … `bit_31`, A = 1.0, each against `lq_h0` |
| **B** | the price list's **flow-M row**: `b` bit 11 with `a` = π, priced at the gate level by Q124 and never run on a card | `bpi_0, bpi_8, bpi_11, bpi_16, bpi_22`, A = π, against `lb_h0` |
| **C** | gap 5: E62's 5.80 W offset — the kernel's, the clock's or the card's? | an idle-bracketed hart ladder, 64 … 1,024 harts, one session per operand set |
| **D** | gap 4: the switching drift with temperature (+0.3–0.5 %/°C, cause unknown) | `lq_h0, lq_h2, lq_h8, bit_22` at the duty cycle's own plateau (A7) |

Blocks A, B and D ran through E60's `tools/claims-v3/hl/block.sh` unchanged; block C ran E62's
`tools/claims-v3/hm/run_hm.py` on a new protocol, `--no-cam`. Both hold `flock -n
/run/lock/etsoc-shire0.lock` for their pass or session, put every device process under `timeout 10` with an
explicit `--stop-file`, check for another user on the card before and between launches, and stop at 78 °C.

## Amendments, all committed before the data they touch

| | What | Commit |
|---|---|---|
| **A4** | `make_hl.py` builds all 32 bit positions and the new `bpi` family (A = π); `reduce_hl.py` gains `ZERO["bpi"]`, reports the scan for both partners, and tolerates an item with no RTL replay. Every operand file E60 ran is byte-identical in the new set — checked, 63 of 63, before the first launch. | `6da964d2` |
| **A5** | `run_hm.py`'s other-user test on aifoundry3 and aifoundry1 becomes E60's departure D1 (another user on **this card**, from `sudo -n /usr/local/sbin/et-holders`, failing closed). Two lab users keep idle tmux logins on aifoundry3, so the `who`-based test would have refused every block-C session. | `b27d323c` |
| **A6** | the ladder protocols' `cooldown_gate` keys corrected to `run_hm.py`'s schema. Inert either way: the gate is called only between blocks and each session has one. | `e53c9945` |
| **A7** | block D's registered 65 °C launch is unreachable on this card (E60's probe: a 64 °C plateau; every approach today reached 60–61 °C), so it runs with **no approach** at the duty cycle's own plateau, 8 passes, and D1 is fitted on each run's own recorded launch reading. | `0adf4a3d` |

## Files

| File | What |
|---|---|
| `hl.json`, `runs.csv`, `reduce.txt` | blocks A and B: `reduce_hl.py` over the 58 °C passes |
| `hl-blockD.json`, `runs-blockD.csv`, `reduce-blockD.txt` | block D: the same reducer over the no-approach passes |
| `ladder.json`, `rungs.csv`, `reduce-ladder.txt` | block C: `hb/reduce_ladder.py` over both ladder sessions |
| `manifest.json` | the operand set `build/hl-gen3`: every item, its designed flip counts, re-derived from the files |
| `aifoundry3/hl/p65*`, `aifoundry3/hl/p67*` | per pass: `block.json`, `configs.json`, `gen.sha256` (the operand files that ran), `manifest.txt` (`et-lab-manifest`), `marks.jsonl`, `run.log`, `runs.jsonl`, `code.sha256`, `telemetry.jsonl.gz` |
| `logs/` | the queue and session logs as they stand. `run_e65.sh ab` and `d` truncate their queue log when a later group starts, so `queue-ab.log` holds only passes 655–657 and `queue-d-a9.log` only the 61 °C regime; `queue-d-a7.log` is the copy taken before that truncation. Nothing is lost by it: each pass's own `run.log` and `block.json` (start and end epoch, die temperatures, status) are the record, and they are complete for every pass |
| `aifoundry3/e65/{randn,zeros}` | each ladder session: `session.json`, the protocol verbatim, `launches.jsonl`, `phases.jsonl`, `blocks.jsonl`, `marks.jsonl`, `run.log`, `tel.jsonl.gz` |

## Results

Blocks A and B: passes [651, 652, 653, 655, 657] after the gates, 205 runs kept. Clock 600 MHz on every sample, rail 521.9 mV. Every value below is the item minus its family's constant-operand zero (`lq_h0` for A = 1.0, `lb_h0` for A = π), averaged over passes, with the SE from the between-pass scatter; the energy is that difference divided by 4,096 designed flipped bits per multiply-add times the measured multiply-add rate.

### Block A — the price of a flipped bit at all 32 positions (A = 1.0)

| bit | field | ΔW above `lq_h0` | SE (W) | fJ per flipped bit | SE (fJ) |
|---|---|---|---|---|---|
| 0 | mantissa | 0.625 | 0.021 | 136 | 5 |
| 1 | mantissa | 0.512 | 0.018 | 112 | 4 |
| 2 | mantissa | 0.406 | 0.021 | 88 | 5 |
| 3 | mantissa | 0.482 | 0.026 | 105 | 6 |
| 4 | mantissa | 0.484 | 0.019 | 105 | 4 |
| 5 | mantissa | 0.461 | 0.021 | 100 | 5 |
| 6 | mantissa | 0.381 | 0.095 | 83 | 21 |
| 7 | mantissa | 0.535 | 0.023 | 116 | 5 |
| 8 | mantissa | 0.524 | 0.017 | 114 | 4 |
| 9 | mantissa | 0.606 | 0.038 | 132 | 8 |
| 10 | mantissa | 0.965 | 0.046 | 210 | 10 |
| 11 | mantissa | 1.098 | 0.082 | 239 | 18 |
| 12 | mantissa | 1.566 | 0.034 | 341 | 7 |
| 13 | mantissa | 1.777 | 0.031 | 387 | 7 |
| 14 | mantissa | 2.157 | 0.034 | 470 | 7 |
| 15 | mantissa | 2.544 | 0.028 | 554 | 6 |
| 16 | mantissa | 2.794 | 0.028 | 609 | 6 |
| 17 | mantissa | 2.838 | 0.107 | 618 | 23 |
| 18 | mantissa | 3.152 | 0.162 | 687 | 35 |
| 19 | mantissa | 3.717 | 0.029 | 809 | 6 |
| 20 | mantissa | 3.973 | 0.030 | 865 | 7 |
| 21 | mantissa | 4.161 | 0.078 | 906 | 17 |
| 22 | mantissa | 4.627 | 0.098 | 1008 | 21 |
| 23 | exponent | 0.796 | 0.023 | 173 | 5 |
| 24 | exponent | 0.794 | 0.021 | 173 | 5 |
| 25 | exponent | 0.684 | 0.022 | 149 | 5 |
| 26 | exponent | 0.867 | 0.036 | 189 | 8 |
| 27 | exponent | 0.509 | 0.013 | 111 | 3 |
| 28 | exponent | 0.952 | 0.103 | 207 | 22 |
| 29 | exponent | 1.061 | 0.024 | 231 | 5 |
| 30 | exponent | 0.737 | 0.056 | 161 | 12 |
| 31 | sign | 0.563 | 0.024 | 123 | 5 |

**The shape.** The mantissa is two regimes, not one slope. Bits 0–9 are flat at 83–136 fJ (mean 109 fJ); from bit 10 the price climbs monotonically to 1008 fJ at bit 22, 9.2× the flat floor. The eight exponent bits (23–30) average 174 fJ — dearer than the low mantissa bits but **cheaper than every mantissa bit above 10** — and the sign bit costs 123 fJ. Across all 32 positions the span is 12.2× (83 fJ at bit 6, 1008 fJ at bit 22).

### Block B — the flow-M case and the busy partner (A = π)

| bit | ΔW above `lb_h0` | SE (W) | fJ per flipped bit | A = π ÷ A = 1.0 | difference (SE) |
|---|---|---|---|---|---|
| 0 | 2.043 | 0.063 | 445 | 3.27× | +1.417 W (0.067, 21.2 SE) |
| 8 | 2.480 | 0.258 | 540 | 4.73× | +1.956 W (0.258, 7.6 SE) |
| 11 | 3.421 | 0.258 | 745 | 3.12× | +2.324 W (0.271, 8.6 SE) |
| 16 | 5.713 | 0.069 | 1244 | 2.04× | +2.919 W (0.074, 39.5 SE) |
| 22 | 7.362 | 0.085 | 1604 | 1.59× | +2.735 W (0.130, 21.1 SE) |

**The flow-M row.** `b` bit 11 alternating with `a` = π — the stimulus the chip diagram priced at the gate level and no card had run — costs **3.421 ± 0.258 W**, i.e. **745 ± 56 fJ per flipped bit** at the board, all-in. The gate-level price is 0.11–0.13 pJ in the multiplier alone at zero delay (`tfma.flip.energy`), about 0.15–0.18 pJ once that page's ×1.4 for glitches is applied. So the board number is **6.2× the zero-delay multiplier price and 4.4× the glitched one**: on this card the Booth rows, the Wallace tree and the product adder account for roughly **23% of what a flipped operand bit costs**, and the rest is the operand bus, the register file's read ports, the result path, the accumulator and the clocked bits. The two agree in direction (board ≥ gate) and the board is the larger, as it must be.

Against a position-0 flip with the same partner the position-11 premium is +1.379 W (300 fJ) with A = π and +0.472 W (103 fJ) with A = 1.0.

### Block C — the hart ladder, and what E62's 5.80 W offset was

| harts | randn board (W) | randn de-leaked (W) | randn mW/hart | zeros board (W) | zeros de-leaked (W) | zeros mW/hart |
|---|---|---|---|---|---|---|
| 64 | 26.40 | 1.56 | 24.4 | 24.25 | 0.14 | 2.3 |
| 128 | 27.93 | 3.07 | 24.0 | 24.37 | 0.28 | 2.2 |
| 256 | 31.27 | 6.36 | 24.8 | 24.64 | 0.56 | 2.2 |
| 384 | 34.61 | 9.64 | 25.1 | 24.88 | 0.81 | 2.1 |
| 512 | 38.23 | 13.15 | 25.7 | 25.11 | 1.06 | 2.1 |
| 768 | 45.23 | 20.04 | 26.1 | 25.66 | 1.61 | 2.1 |
| 1024 | 52.99 | 27.69 | 27.0 | 26.19 | 2.15 | 2.1 |

| session | line | intercept (W) | slope (mW/hart) | residual rms (W) | laps |
|---|---|---|---|---|---|
| randn | raw | -0.454 ± 0.293 | 27.64 ± 0.144 | 0.273 | 3 |
| randn | de-leaked | -0.511 ± 0.026 | 27.13 ± 0.005 | 0.271 | 3 |
| zeros | raw | -0.358 ± 0.104 | 2.02 ± 0.092 | 0.027 | 3 |
| zeros | de-leaked | 0.013 ± 0.016 | 2.08 ± 0.012 | 0.014 | 3 |

**There is no 5.80 W fixed cost on this card at this clock.** With an IDLE bracket on both sides of every rung, the de-leaked randn line is **-0.51 ± 0.03 W + 27.1 mW per hart** over 64–1,024 harts, residual rms 0.271 W. E62 measured 5.80 W + 55.8 mW/hart at 800 MHz on aifoundry2; scaled to this card by f·V² = (600/800)(0.523/0.618)² = 0.537 that is 3.12 W + 30.0 mW/hart. **The slope lands (27.1 against 30.0 mW/hart) and the intercept does not.** A small negative intercept is what a mildly convex ladder gives a straight line: the per-hart price rises across the rungs (see the table), so the fit lands just below zero at harts = 0. The reading is that the offset belongs to E62's baseline — one pre-session idle at a 49 °C die while its rungs ran at 52–61 °C — and not to the kernel, the clock or the card. An idle bracket per rung removes it.

**And it is not the data's switching either.** The zeros line is +0.01 ± 0.02 W + 2.1 mW per hart: the slope falls to 8% of randn's while the intercepts differ by -0.52 W (SE 0.03). Whatever a kernel costs before its first flipped bit, it is under a watt here, and it is the same for a stream that switches hard and one that barely switches at all.

### Block D — the switching drift with temperature, and a gate that ruled out its own protocol

Block D ran in two regimes: **A7**, eight passes (671–678) with no approach at all, and **A9**, six passes
(681–686) launched at a 61 °C reading after 62 °C. Its items are `lq_h0`, `lq_h2`, `lq_h8` and `bit_22`; the
contrast shared with blocks A and B, which measure it at 58 °C, is **`bit_22` − `lq_h0`**.

**The A7 regime produced no admissible pass.** All eight were set aside by the registered pass-level gate that
rejects a pass whose `anchor_pi` drifts more than 0.3 W from its first run to its last: the drifts were **+0.57 to
+0.74 W**, every one the same sign. That is not noise and not a fault — it is what A7's design guarantees. A pass
with no approach never idles back down, so the die climbs monotonically through the pass and the closing anchor
sits above the opening one by the leakage slope times the climb. **A7 changed the protocol and left in place the
gate that assumes the protocol.** A8 caught the sibling problem (the launch-reading gate) and not this one. The
lesson for the recipe: a no-approach regime needs its drift gate restated as a *rate* — watts per degree of the
pass's own climb — or replaced by a within-pass control, and that restatement has to be registered, not made
after the data.

**The A9 regime worked exactly as registered.** Every run reached its setpoint: 61.0 °C after a 62–63 °C preheat,
**zero skipped runs** in 36. Five of its six passes passed the drift gate (686 drifted +0.77 W and was set aside),
so D1 is scored on **five passes at 58 °C against five at 61 °C**, a gated 3.00 °C contrast.

| launch reading | passes | `bit_22` − `lq_h0` | sd |
|---|---|---|---|
| 58.00 °C (blocks A and B) | 5 | 4.627 W | 0.219 |
| 61.00 °C (block D, A9) | 5 | 4.693 W | 0.104 |

**D1: the coefficient is +0.47 ± 0.78 %/°C — the registered band's own value, and not resolved from zero.**
The fit of the difference on the launch reading gives **+22.0 ± 36.1 mW/°C**, i.e. +0.47 ± 0.78 %/°C of the
contrast's 4.66 W mean, 95% CI **−1.05 to +1.99 %/°C**. The registered band, +0.3 to +0.5 %/°C, sits inside that
interval; so does zero, and so does +1.9 %/°C. **Verdict: CONSISTENT, UNDECIDED** — the point estimate is the
registered value almost exactly, and 3 °C of leverage cannot separate it from nothing. A7 said in advance that a
span this short might only bound the coefficient, and it does. `lq_h2` and `lq_h8` ran only in block D, so they
have no temperature spread and no fit.

**Block C saw the same term from the other side, with far better leverage.** The randn hart ladder's per-hart
price rises 24.4 → 27.0 mW/hart, +11%, while its die goes 55.0 → 60.7 °C — about +1.9 %/°C — where the zeros
ladder is flat (2.3 → 2.1 mW/hart) at a die that barely moves (52.3 → 53.0 °C). That is the stronger signal in
this data set, and it is **confounded with hart count**, so it is reported as a co-variation and not as a
coefficient. Taken together the two say the term is real, positive, and somewhere between a few tenths and about
two percent per degree; separating it properly needs a block that varies the launch reading over 10 °C or more at
one hart count, which this card's duty cycle cannot reach without a hotter heater.

### The registered predictions, scored

| | Registered | Measured | Verdict |
|---|---|---|---|
| **A1** | the price rises with j over the mantissa (Spearman ρ > 0.5); the span over all 32 exceeds 5× | ρ = 0.927; span 12.2× | **PASS** |
| **A2** | E60's six positions reproduce within a factor of 1.5 | worst ratio 1.12× over the six | **PASS** |
| **A3** | the sign bit is among the four cheapest; the exponent bits are dearer than the mantissa bits below 16 | sign is rank 10 of 32 (the four cheapest are bits [6, 2, 5, 3]); mantissa bits [11, 12, 13, 14, 15] are dearer than every exponent bit | **FAIL**, both halves |
| **B1** | `bpi_11` costs 100–250 fJ per flipped bit all-in, and at least the gate-level 0.11–0.13 pJ | 745 ± 56 fJ | **FAIL** on the band (it is 3.0× its top), **PASS** on board ≥ gate |
| **B2** | the busy partner is dearer at ≥ 2 SE at 3 of the 5 shared positions | 5 of 5 positions | **PASS** |
| **C1** | the two intercepts within 0.5 W ⇒ not the data's switching; apart by more than 0.5 W and 3 SE ⇒ partly the kernel's | a₀(randn) − a₀(zeros) = -0.52 W (SE 0.03) | **UNDECIDED** by the registered rule (A10) |
| **C2** | a₀(randn) in [2.5, 3.8] W ⇒ scales with f·V²; in [5.0, 6.6] W ⇒ fixed | -0.51 ± 0.03 W | **neither band**: no fixed offset at all |
| **C3** | the randn slope is 30.0 ± 6 mW/hart; the zeros slope is 10–40% of it | 27.1 mW/hart; zeros 8% of randn | **PASS** on randn, **FAIL** on zeros |
| **C4** | residual rms ≤ 0.4 W, or ≤ 3% of the span | worst 0.271 W | **PASS** |

**A note on A2.** The registered wording said E60's six positions ran on aifoundry1's card 0 at 800 MHz and would need rescaling. They did not: E60's amendment A1 moved the bit scan to **aifoundry3**, passes 5–8, and the E60 ledger entry reports it there. So A2 was scored as what it actually is — a direct, same-card, same-clock replication six days later with no rescaling, which is the harder test.

*Every verdict above is the registered rule applied to the committed reduction; nothing was re-registered after the data.*
