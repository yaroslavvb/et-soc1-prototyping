# Dated note 1 beside NOTE-2026-11-05-fmadd-ps-public-facts.md, Fri 6 Nov 2026 (week 45), about 00:00-00:10 PST: the minion-rail figure and the board-over-minion ratio on one footing, and the virus loop's structure (post hoc)

*This note sits beside [`NOTE-2026-11-05-fmadd-ps-public-facts.md`](NOTE-2026-11-05-fmadd-ps-public-facts.md), which stays as committed
in `538c98ce` (Thu 5 Nov 2026, 22:54:13 PST). It answers the adversarial verifier of the anatomy lane (`verify-anat-q145a`, Thu 5 Nov
2026, about 23:00-23:35 PST): its major fault as it touches the NOTE's section 2, and its first nit. It holds public facts only, post
hoc: nothing here is a prediction or a verdict. Every figure is printed by [`posthoc_note1_q145a.py`](posthoc_note1_q145a.py) in
[`posthoc-note1-q145a.txt`](posthoc-note1-q145a.txt) (F1, "the NOTE's random rows on one footing", and F7 (a)). What it builds on, and
the rules A, Au and B, are in the README's [dated note 1](README.md.dated-note-1.md) (its Builds-on block and section 1).*

## 1. Section 2's minion-rail figure and ratio, on one footing

Section 2's table puts the board's figure, which is **net** of the catalogue's leakage correction (the 21 Sep law's slope times the
busy die's rise), beside the minion rail's, which is the catalogue's `rails_over`: a **raw** rise over the burst's last 0.6 s against an
idle read before the burst, with the rail's own heating in it (`workloads/enercat/analyze_catalogue.py`, lines 82-100). So its "board
over minion rail, one convention" row (1.218 / 1.166 / 1.208) mixes two footings, the same kind of mix its first bullet corrects for
wall against device time (0.4%), but about ten times larger. On one footing, `fmadd.ps/random/h2`, pJ an instruction above each burst's
idle (the catalogue's wall-rate convention unless marked):

| | aifoundry3 | aifoundry1 card 1 | aifoundry2 | the three cards |
|---|---:|---:|---:|---:|
| board, net of its heating (as committed) | 56.25 | 55.44 | 55.59 | **55.76** |
| minion rail net of its own heating, rule A (the registered reduction's 0.81 of the same law, the rise through the rail's filter) | 44.52 | 45.55 | 43.25 | **44.44** |
| the same at the device-time rate | 44.35 | 45.35 | 43.09 | 44.26 |
| the minion rail net, across the rules: B (the rail ledger's drift) to Au (the unfiltered rise) | 45.53-43.62 | - to 44.86 | 44.32-42.21 | - |
| **board over minion rail, both net (footing A)** | **1.264** | **1.217** | **1.285** | 1.255 |
| board, no heating removed | 58.01 | 57.36 | 58.34 | 57.91 |
| minion rail, raw (as committed) | 46.16 | 47.54 | 46.00 | 46.57 |
| **board over minion rail, both raw** | **1.257** | **1.207** | **1.268** | 1.244 |
| the committed mix (net board over raw minion rail), for reference | 1.219 | 1.166 | 1.208 | 1.198 |

(The three-card column is the mean of the card columns; card 1 has no rule-B figure, because the rail ledger holds no card-1 drift.)

- **So a like-for-like pair is 55.8 pJ at the board with 44.4 pJ on the minion rail, both net of their heating** (board over minion
  rail 1.22-1.29 by card; across the rules the minion rail reads 43.6-45.5 pJ on aifoundry3 and 42.2-44.3 pJ on aifoundry2), **or 57.9
  with 46.6 pJ, both raw**
  (1.21-1.27). The pair "55.76 pJ at the board, 46.57 (or 46.38) pJ on the minion rail" is not on one footing and should not be quoted as
  one.
- The same holds for the other random rows: `fadd.ps` random 41.14 pJ at the board with 33.32 pJ on the minion rail on footing A (1.19-1.28
  by card), and `fadd.pi` random 19.83 with 15.85 pJ (1.19-1.32).
- Card 1's minion rail, after each card's own V² (0.499 and 0.523 V), reads 1.124 times aifoundry3's for `fmadd.ps` random on footing A
  (1.131 raw).

## 2. The virus loop's structure (section 1, "What it runs")

Not "alternating, 20 pairs a loop". In `vpu_power_virus()` (et-platform `836a4ab60`,
`test-compute-kernels/src/vpu_txfma_power_virus/kernel.h`, lines 162-190), the loop's inner block is **24 `fmadd.ps`: 12 pairs, written
to f4-f27**, alternating `fmadd.ps f(even), f1, f2, f3` and `fmadd.ps f(odd), f28, f29, f30`; the block runs **20 times (240 pairs, 480
instructions) before each gold check** against `gold_ref_0` and `gold_ref_1`. The two triples alternate across the blocks' boundaries
too (24 is even), so every instruction's sources still differ from the previous one's on that hart, and the flip counts of section 1
stand.

## 3. What does not change

Section 1's operand-port flips (334 on hart 0 and 348 on hart 1 as each hart alternates its triples; 318, 348, 352 and 322 if the
harts' instructions alternate one for one), the random rotation's 286.7 expected and the constant column's 0; section 2's board row
(56.25 / 55.44 / 55.59, 55.76 for the three cards), its issue rates (0.3649 / 0.3651 / 0.3648 a hart-cycle with two harts, 0.730 a
minion-cycle; 0.5814 with one hart), and the rate ceiling (`nop` 0.390 a hart-cycle; 102 of the 150 random-data two-hart instruction rows
at 0.30-0.45, the median 0.369). The virus's own rate and power on these cards are still not measured.
