# E121: E93's zero-gate tests on a second card — negative zero, denormals, int8's eight-byte rule, its column pairing and the A word (Q134, aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): the closed list's entry "The zero gate on silicon" (old item 4), "closed at power resolution on one card" by [E93](../2026-11-01-e93-zero-gate-silicon/README.md); and item 15's two E93 leftovers (why a live zero on A costs more than priced; the extra watts of a half-gated int8 tile).*

*Sun 1 Nov 2026 (week 44), Q134. Pre-registered in `b66434a8` (pushed 19:21:26 PST by origin/main's reflog, before the claim and the first launch):
[`tools/claims-v3/e121/E121.md`](../../../../tools/claims-v3/e121/E121.md), frozen numbers in
[`predictions-e121.json`](../../../../tools/claims-v3/e121/predictions-e121.json) (sha256 `dd7bcb69…`), scorer `score_e121.py` (sha256 `b7accbef…`) committed
with them. No amendment was written. aifoundry3 card 0 (no `V3_DEVICE`, `/run/lock/etsoc-shire0.lock`) at 600 MHz in every sample, 521.7 mV mean, TDP 0 /
threshold 65 °C read at both ends of every block and at the session's start and end, never set; no governor move, no reset, no `--reset-ms`, no PMIC
command (the stock telemetry's PMIC register reads are disclosed under § Registered against what happened, C2). The claim was a clause added to the day's one `#community-lab` post (message 1566603178164617247) at 19:23:25 PST and erased from it at 19:51:59
PST (aifoundry2 was still held, so the clause was dropped rather than marked released): held 28.6 min of the 35 registered; device access 27.9 min,
19:23:35–19:51:28, the first launch at 19:23:41 ([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt); C4).*

*Corrected after verification, Sun 1 Nov 2026, at the desk, with no card touched and nothing re-run on a card (§ [Corrections after verification](#corrections-after-verification-sun-1-nov-2026), C1–C6). The reductions' raw-root paths are now repo-relative (re-reduced by the registered collector, every number byte-identical); the stock telemetry's PMIC reads are disclosed; item 15's first leftover is stated as what replicates (R5's failure), not as the 1.72 W A-side excess, which was not recomputed here; device access is dated from the die reading; two card-1 numbers are re-rounded; the blog text names the cards. No registered prediction, rule, number or verdict changed (24 of 24 as E93: 23 PASS, 1 FAIL).*

> **What this is.** E93 tested the public RTL's zero gate where "the word is zero" and "the value is zero" disagree, on aifoundry1 card 1, and the page
> closed the item at power resolution on one card. E121 runs **the same seventeen tiles, E93's card code and E78's runner unchanged, and E93's 24 rules
> with their lines unchanged on a second card**, aifoundry3 (the card of E78's kinds matrix), and adds cross-card rules at E82's card scale. **Every number
> here is board switching power over the type's own all-zeros level (D), 1,024 minions, on aifoundry3, unless it says otherwise.**

## Results

**Four passes of four run, all four kept (12110–12113), 158 of 160 runs, none failing a run gate (two skipped before launch by E78's launch-reading rule);
the 22 gate rules PASS; E93's 24 verdicts replicate one for one (23 PASS, 1 FAIL: R5 fails again, as on card 1); the int8 pairing reading is `rtl`; 23 of
24 cross-card rules PASS at E82's card scale and one is INCONCLUSIVE (aggregate PASS); the session tie to E78 passes, its largest difference 0.089 W.** The
zero gate's closed entry now stands **at power resolution on two cards** (aifoundry1 card 1 and aifoundry3 card 0), in agreement with the RTL. The
micro-op counters were still not read, so gated lanes are inferred from power, not counted. [`scored.json` › `primary`; [`results.md`](results.md)]

1. **`-0.0` leaves the lane on, on the second card too.** `-0.0 × -0.0` costs **8.23 ± 0.19 W** in fp32 and **8.18 ± 0.19 W** in fp16 (card 1: 7.94 ± 0.07 and
   8.02 ± 0.26 W), about a constant's cost: against `anchor_pi` (π × π) in the same pass −0.19 ± 0.16 W (R2-fp32), and against E78's fp16 constant on this card
   −0.20 ± 0.19 W (R2-fp16), both inside the registered ±1 W. With random numbers on the other side, a live `-0` costs **12.44 ± 0.05 W** (A = `-0`) and
   **12.83 ± 0.04 W** (B = `-0`) for a product that is exactly zero, and A's sign bits read **11.72 ± 0.12 W** over the `+0` mirror in the same pass (card 1:
   11.37 ± 0.13 W). [R1 (six), R2 (two); `e121.json` › `items`]
2. **Denormal words pass the gate; power agrees with the manual and the RTL that the fraction never reaches the multiplier.** `0x00000001 × 0x00000001` costs
   **8.39 ± 0.10 W**, random denormals on both sides **9.74 ± 0.05 W** (fp16 9.52 ± 0.06 W), on A alone 13.22 ± 0.06 W (fp16 13.27 ± 0.11), on B alone
   13.70 ± 0.12 W. Random fractions over a constant denormal add **1.35 ± 0.08 W** (card 1: 1.40 ± 0.08), far below R4's 4.98 W midpoint toward the unflushed
   reading: **16.9 ± 1.0 fJ a raw bit** (card 1: 17.6 ± 1.0), about the operand-bus price. Cycles per op are 546.001 on every denormal tile: no stall. As in E93
   no run reads a result, so the flush itself is still the documents' statement (PRM §3.4, the VPU specification §2.2.3.9, `txfma_f0.v:375-377`). [R3 (six),
   R4 (four); [`readme-numbers.txt`](readme-numbers.txt)]
3. **int8's B gate wants eight bytes and pairs columns `(l, l+8)`, on the second card too.** The same A, the same eight nonzero B words a line and the same bus
   bits, only the zero columns differing: `(l, l+8)` pairs **4.27 ± 0.15 W**, `(2l, 2l+1)` pairs **5.69 ± 0.13 W**, one zero word in every pair **5.71 ± 0.12 W**.
   R6a **1.44 ± 0.12 W**, R6b **1.42 ± 0.21 W**, R6c the control **0.02 ± 0.24 W** (card 1: 1.25 ± 0.30, 1.33 ± 0.20, −0.08 ± 0.18). The scorer names the
   RTL's reading again, so `(2l, 2l+1)` is rejected on two cards. E93's limits stand: 16 of the 2,027,025 perfect pairings of sixteen columns give these
   tiles' pattern, and power cannot tell the RTL's AND from a per-unit gate plus lane-shared logic. [R6a–c; `scored.json` › `primary.pairing_reading`]
4. **int8's A test is the whole word.** One nonzero byte in every A word costs **5.88 ± 0.20 W**, all four zero **0.24 ± 0.15 W**: R7 **5.68 ± 0.38 W** (card 1:
   5.40 ± 0.22). R7 rests on three passes: its zero reference `int8.a_zeros_b_full` was skipped in 12110 by the launch-reading rule. [R7]
5. **The masked sparse tile pays the same watts for its negative zeros.** E78's `sparse50` reads 7.33 ± 0.05 W; the same tile with 46% of its zero words made
   `-0.0`, as `x * mask` leaves them, reads **13.15 ± 0.18 W**: **5.82 ± 0.15 W** more (card 1: 5.82 ± 0.15 W), 1.79× in D, 1.62× in S (9.34 → 15.11 W). The
   tile is synthetic. [R8]
6. **R5 fails again: E93's Booth-recoder side prediction is wrong on two cards.** A live zero on B against one on A, fp32: **+0.39 ± 0.09 W** against a line of
   +1 W (card 1: +0.31 ± 0.16); fp16's twin −0.67 ± 0.12 W (card 1: −0.75 ± 0.16; reported, no verdict). So R5's failure is not a card-1 artifact. Item 15's
   "why a live zero on A costs 1.72 W more than priced" rests on E93's split of card 1's shortfall (C3 there: 2.793 W = 1.718 W of `a_nz_b_randn` above its
   priced point + 1.075 W of `a_randn_b_nz` below its point). That split needs priced points on this card and was not recomputed here, so E121 shows R5's
   failure again, not the A-side excess itself, and does not explain either (C3). [R5-fp32; `reported.e93_reported_block.booth_asymmetry_w`]
7. **The watts carry across by the card scale.** 23 of the 24 cross-card rules PASS (|d| + h ≤ w); X-R7 is INCONCLUSIVE (d +0.14 W, h 0.44 W against w 0.50 W,
   R7's three-pass interval). Post hoc: over the 22 cells E93 read at 4 W or more, D here over D on card 1 has a **median of 1.030** (E82's 32-kind median:
   1.031), range 1.004 (`int8.b_pairs_rtl`) to 1.057 (fp32 `sparse50`, also E82's widest cell), 18 of 22 within 1.5%. The half-gated int8 tile's extra over
   the gate law, `b_pairs_rtl` − (½ `full` + ½ `a_zeros_b_full`) in the same pass, is **+0.55 ± 0.15 W** (three passes; card 1: +0.65 W), post hoc: item 15's
   other leftover is not a card-1 artifact either. [`scored.json` › `primary.cross_card`; [`readme-numbers.txt`](readme-numbers.txt)]
8. **The arms.** At three of the six registered arms (leakage `auto`, 0.155 W/°C over 103 runs; 0.2414, E93's own frame; 0) all 24 verdicts equal E93's and the
   cross-card aggregate PASSes. At 0.3803 E78's int8 zeros-line gate sets 12112 aside and R7 becomes UNRESOLVED (its zero reference then has two passes); every
   other gate verdict holds. **At dips kept (E78's own frame on this card) and at 0.545 nothing scores**: E78's range gate sets 12110 and 12111 aside on the
   meter's launch-gap dips (`fp16.randn` spans 1.155 W, `int8.full` 1.027 W, against 1.0 W), as it set aside E95's 9513 and E92's 9211 on this card, and the
   zeros-line gate sets 12112 and 12113 aside at 0.545; two passes are left, so every rule is NOT SCORED there, as registered. The scorer therefore marks every
   rule arm-sensitive. The session tie fails at 0.3803, 0.545 and 0, where the slope moves the random cells against E78's frame, as E93's did against E82's.

**What it means for the blog.** E93's statements about the zero gate now hold on two ET-SoC-1 cards, with aifoundry3's watts about 3% above aifoundry1 card 1's,
the same scale E82 found across 32 kinds: a zero the gate can see is almost free; `-0.0` and denormal words keep the lane on and cost about what two constants
cost (≈ 8 W over exact zeros on either card); int8's B side needs all eight bytes of an `(l, l+8)` column pair and its A side all four bytes of the word.
Each blog sentence at the end carries its baseline, its cards and its source.

## The table

D over the type's zeros, S over the idle bracket, pJ/MAC from S at the measured op rate, all ± 95% over the kept passes (four; `int8.a_zeros_b_full` three) at the
primary slope, statistical only; ΔT is the die reading's rise over the window and is limited by its 1 °C steps below about 12 W of switching (E82 C1, E89);
the rail is deconvolved and reported, never scored. "Gated" is `kinds.json` or `tile_stats`' `gated_lane_frac` under the RTL's reading. "Card 1" is E93's
D (`e93.json` › `items`). Source: `e121.json` › `items`; [`readme-numbers.txt`](readme-numbers.txt).

| tile | gated | D (W) | S (W) | pJ/MAC (S) | ΔT (°C) | Drail (W) | card 1, D (W) | here / card 1 |
|---|---|---|---|---|---|---|---|---|
| `fp32.nz_both` | 0.000 | 8.23 ± 0.19 | 10.11 ± 0.20 | 2.201 ± 0.044 | 1.00 | 6.97 | 7.94 | 1.037 |
| `fp32.dn1_both` | 0.000 | 8.39 ± 0.10 | 10.31 ± 0.15 | 2.245 ± 0.033 | 1.01 | 7.05 | 8.01 | 1.047 |
| `fp32.dnr_both` | 0.000 | 9.74 ± 0.05 | 11.70 ± 0.09 | 2.550 ± 0.019 | 1.55 | 8.19 | 9.42 | 1.034 |
| `fp32.a_nz_b_randn` | 0.000 | 12.44 ± 0.05 | 14.44 ± 0.09 | 3.145 ± 0.018 | 1.61 | 10.49 | 12.11 | 1.027 |
| `fp32.a_dnr_b_randn` | 0.000 | 13.22 ± 0.06 | 15.19 ± 0.04 | 3.309 ± 0.007 | 1.78 | 10.85 | 12.79 | 1.034 |
| `fp32.a_randn_b_nz` | 0.000 | 12.83 ± 0.04 | 14.80 ± 0.11 | 3.223 ± 0.025 | 1.99 | 10.59 | 12.42 | 1.033 |
| `fp32.a_randn_b_dnr` | 0.000 | 13.70 ± 0.12 | 15.69 ± 0.11 | 3.417 ± 0.025 | 1.50 | 11.35 | 13.32 | 1.028 |
| `fp32.sparse50_mask` | 0.485 | 13.15 ± 0.18 | 15.11 ± 0.19 | 3.290 ± 0.042 | 1.84 | 10.92 | 12.75 | 1.031 |
| `fp32.sparse50` | 0.774 | 7.33 ± 0.05 | 9.34 ± 0.11 | 2.034 ± 0.023 | 1.04 | 6.16 | 6.93 | 1.057 |
| `fp32.a_zeros_b_randn` | 1.000 | 0.72 ± 0.15 | 2.64 ± 0.06 | 0.574 ± 0.012 | 0.40 | 0.64 | 0.75 | 0.967 |
| `anchor_pi` | 0.000 | 8.42 ± 0.09 | 10.45 ± 0.04 | 2.276 ± 0.009 | 0.84 | 7.16 | 8.08 | 1.042 |
| `fp32.randn` | 0.000 | 24.74 ± 0.04 | 26.67 ± 0.06 | 5.809 ± 0.011 | 3.09 | 19.78 | 24.01 | 1.031 |
| `fp32.zeros` | 1.000 | 0.00 ± 0.00 | 1.98 ± 0.15 | 0.431 ± 0.032 | 0.03 | 0.00 | 0.00 | — |
| `fp16.nz_both` | 0.000 | 8.18 ± 0.19 | 10.11 ± 0.08 | 1.101 ± 0.009 | 1.07 | 6.94 | 8.02 | 1.020 |
| `fp16.dnr_both` | 0.000 | 9.52 ± 0.06 | 11.50 ± 0.07 | 1.252 ± 0.007 | 1.55 | 7.93 | 9.25 | 1.030 |
| `fp16.a_nz_b_randn` | 0.000 | 12.79 ± 0.06 | 14.83 ± 0.14 | 1.614 ± 0.015 | 1.97 | 10.62 | 12.48 | 1.024 |
| `fp16.a_dnr_b_randn` | 0.000 | 13.27 ± 0.11 | 15.26 ± 0.23 | 1.662 ± 0.026 | 1.85 | 11.03 | 12.96 | 1.024 |
| `fp16.a_randn_b_nz` | 0.000 | 12.12 ± 0.07 | 14.11 ± 0.18 | 1.537 ± 0.020 | 1.86 | 10.05 | 11.73 | 1.033 |
| `fp16.randn` | 0.000 | 22.14 ± 0.10 | 24.13 ± 0.03 | 2.628 ± 0.003 | 2.78 | 17.89 | 21.59 | 1.026 |
| `fp16.zeros` | 1.000 | 0.00 ± 0.00 | 1.98 ± 0.10 | 0.216 ± 0.011 | 0.02 | 0.00 | 0.00 | — |
| `int8.b_pairs_rtl` | 0.500 | 4.27 ± 0.15 | 6.86 ± 0.11 | 0.217 ± 0.003 | 0.75 | 3.66 | 4.26 | 1.004 |
| `int8.b_pairs_alt` | 0.000 | 5.69 ± 0.13 | 8.20 ± 0.08 | 0.260 ± 0.003 | 1.00 | 4.84 | 5.58 | 1.020 |
| `int8.b_unpaired` | 0.000 | 5.71 ± 0.12 | 8.30 ± 0.10 | 0.263 ± 0.003 | 0.75 | 4.85 | 5.50 | 1.037 |
| `int8.a_3of4_b_full` | 0.000 | 5.88 ± 0.20 | 8.45 ± 0.28 | 0.268 ± 0.009 | 1.00 | 5.02 | 5.80 | 1.013 |
| `int8.a_zeros_b_full` | 1.000 | 0.24 ± 0.15 | 2.76 ± 0.08 | 0.088 ± 0.003 | 0.22 | 0.32 | 0.40 | 0.601 |
| `int8.full` | 0.000 | 7.12 ± 0.05 | 9.72 ± 0.04 | 0.308 ± 0.001 | 0.98 | 5.91 | 6.96 | 1.023 |
| `int8.zeros` | 1.000 | 0.00 ± 0.00 | 2.52 ± 0.09 | 0.080 ± 0.003 | 0.37 | 0.00 | 0.00 | — |

The gated cells' ratios (0.97 and 0.60) are ratios of numbers near 0 W, within their intervals of each other: `int8.a_zeros_b_full` reads 0.24 ± 0.15 W here
and 0.40 ± 0.25 W on card 1.

## The registered rules

At the primary reduction (dips removed, leakage frozen at E78's 0.1994 W/°C), in pass units, four kept passes (three for R7) (`scored.json` › `primary.rules`):

| rule | contrast | W, ± 95% | line | verdict | card 1 (E93) |
|---|---|---|---|---|---|
| R1-fp32-both | `fp32.nz_both` | 8.232 ± 0.190 | low > 5.0; high < 2.0 fails | **PASS** | 7.936 ± 0.068, PASS |
| R1-fp32-a | `fp32.a_nz_b_randn` − `fp32.a_zeros_b_randn` | 11.717 ± 0.119 | low > 5.0; high < 2.0 fails | **PASS** | 11.367 ± 0.133, PASS |
| R1-fp32-b | `fp32.a_randn_b_nz` − 0.616 (E78) | 12.216 ± 0.040 | low > 5.0; high < 2.0 fails | **PASS** | 11.791 ± 0.127, PASS |
| R1-fp16-both | `fp16.nz_both` | 8.183 ± 0.188 | low > 5.0; high < 2.0 fails | **PASS** | 8.022 ± 0.255, PASS |
| R1-fp16-a | `fp16.a_nz_b_randn` − 0.782 (E78) | 12.002 ± 0.059 | low > 5.0; high < 2.0 fails | **PASS** | 11.719 ± 0.231, PASS |
| R1-fp16-b | `fp16.a_randn_b_nz` − 0.659 (E78) | 11.458 ± 0.067 | low > 5.0; high < 2.0 fails | **PASS** | 11.101 ± 0.177, PASS |
| R2-fp32 | `fp32.nz_both` − `anchor_pi` | −0.190 ± 0.156 | inside ±1.0 | **PASS** | −0.147 ± 0.138, PASS |
| R2-fp16 | `fp16.nz_both` − 8.382 (E78) | −0.198 ± 0.188 | inside ±1.0 | **PASS** | −0.063 ± 0.255, PASS |
| R3-fp32-one | `fp32.dn1_both` | 8.389 ± 0.100 | low > 5.0; high < 2.0 fails | **PASS** | 8.013 ± 0.080, PASS |
| R3-fp32-both | `fp32.dnr_both` | 9.739 ± 0.052 | low > 5.0; high < 2.0 fails | **PASS** | 9.418 ± 0.073, PASS |
| R3-fp32-a | `fp32.a_dnr_b_randn` − `fp32.a_zeros_b_randn` | 12.501 ± 0.162 | low > 5.0; high < 2.0 fails | **PASS** | 12.041 ± 0.209, PASS |
| R3-fp32-b | `fp32.a_randn_b_dnr` − 0.616 (E78) | 13.083 ± 0.117 | low > 5.0; high < 2.0 fails | **PASS** | 12.694 ± 0.127, PASS |
| R3-fp16-both | `fp16.dnr_both` | 9.524 ± 0.058 | low > 5.0; high < 2.0 fails | **PASS** | 9.249 ± 0.274, PASS |
| R3-fp16-a | `fp16.a_dnr_b_randn` − 0.782 (E78) | 12.486 ± 0.109 | low > 5.0; high < 2.0 fails | **PASS** | 12.202 ± 0.111, PASS |
| R4-fp32-both | `fp32.dnr_both` − `fp32.dn1_both` | 1.351 ± 0.080 | high < 4.98 | **PASS** | 1.405 ± 0.083, PASS |
| R4-fp32-a | `fp32.a_dnr_b_randn` − `fp32.a_nz_b_randn` | 0.784 ± 0.104 | high < 3.94 | **PASS** | 0.674 ± 0.191, PASS |
| R4-fp16-both | `fp16.dnr_both` − `fp16.nz_both` | 1.341 ± 0.143 | high < 3.58 | **PASS** | 1.227 ± 0.286, PASS |
| R4-fp16-a | `fp16.a_dnr_b_randn` − `fp16.a_nz_b_randn` | 0.484 ± 0.144 | high < 2.48 | **PASS** | 0.483 ± 0.215, PASS |
| R5-fp32 | `fp32.a_randn_b_nz` − `fp32.a_nz_b_randn` | 0.393 ± 0.089 | low > 1.0; high < 1.0 fails | **FAIL** | 0.308 ± 0.158, FAIL |
| R6a | `int8.b_unpaired` − `int8.b_pairs_rtl` | 1.437 ± 0.118 | low > 0.3; high < 0.3 fails | **PASS** | 1.249 ± 0.301, PASS |
| R6b | `int8.b_pairs_alt` − `int8.b_pairs_rtl` | 1.419 ± 0.214 | low > 0.3; high < 0.3 fails | **PASS** | 1.326 ± 0.196, PASS |
| R6c | `int8.b_unpaired` − `int8.b_pairs_alt` | 0.018 ± 0.242 | inside ±0.6 | **PASS** | −0.078 ± 0.177, PASS |
| R7 | `int8.a_3of4_b_full` − `int8.a_zeros_b_full` | 5.682 ± 0.379 (n 3) | low > 1.0; high < 1.0 fails | **PASS** | 5.398 ± 0.217, PASS |
| R8 | `fp32.sparse50_mask` − `fp32.sparse50` | 5.815 ± 0.148 | low > 1.0; high < 1.0 fails | **PASS** | 5.821 ± 0.149, PASS |

**The gate summary** (the 22 gate rules, R1–R4, R6a–c and R7): **PASS**, as predicted. **R5 FAIL and R8 PASS, as predicted.** **Pairing reading `rtl`, as
predicted.** 24 of 24 verdicts equal E93's.

**The cross-card rules** (`scored.json` › `primary.cross_card`): d = C here − s · C on card 1, s = E82's per-type scale (fp32 1.0300, fp16 1.0332, int8 1.0271),
h the two sessions' half-widths in quadrature; PASS if |d| + h ≤ w.

| X rule | here, W | card 1 × s, W | d | h | w | verdict |
|---|---|---|---|---|---|---|
| X-R1-fp32-both | 8.232 ± 0.190 | 8.174 | +0.058 | 0.203 | 0.75 | PASS |
| X-R1-fp32-a | 11.717 ± 0.119 | 11.708 | +0.009 | 0.181 | 0.75 | PASS |
| X-R1-fp32-b | 12.216 ± 0.040 | 12.145 | +0.071 | 0.137 | 0.75 | PASS |
| X-R1-fp16-both | 8.183 ± 0.188 | 8.288 | −0.105 | 0.324 | 0.75 | PASS |
| X-R1-fp16-a | 12.002 ± 0.059 | 12.108 | −0.106 | 0.246 | 0.75 | PASS |
| X-R1-fp16-b | 11.458 ± 0.067 | 11.470 | −0.012 | 0.195 | 0.75 | PASS |
| X-R2-fp32 | −0.190 ± 0.156 | −0.151 | −0.039 | 0.211 | 0.75 | PASS |
| X-R2-fp16 | −0.198 ± 0.188 | −0.065 | −0.133 | 0.324 | 0.75 | PASS |
| X-R3-fp32-one | 8.389 ± 0.100 | 8.254 | +0.135 | 0.129 | 0.75 | PASS |
| X-R3-fp32-both | 9.739 ± 0.052 | 9.701 | +0.038 | 0.092 | 0.75 | PASS |
| X-R3-fp32-a | 12.501 ± 0.162 | 12.403 | +0.098 | 0.269 | 0.75 | PASS |
| X-R3-fp32-b | 13.083 ± 0.117 | 13.075 | +0.008 | 0.175 | 0.75 | PASS |
| X-R3-fp16-both | 9.524 ± 0.058 | 9.556 | −0.032 | 0.289 | 0.75 | PASS |
| X-R3-fp16-a | 12.486 ± 0.109 | 12.607 | −0.121 | 0.158 | 0.75 | PASS |
| X-R4-fp32-both | 1.351 ± 0.080 | 1.447 | −0.096 | 0.117 | 0.75 | PASS |
| X-R4-fp32-a | 0.784 ± 0.104 | 0.695 | +0.089 | 0.223 | 0.75 | PASS |
| X-R4-fp16-both | 1.341 ± 0.143 | 1.268 | +0.073 | 0.328 | 0.75 | PASS |
| X-R4-fp16-a | 0.484 ± 0.144 | 0.499 | −0.015 | 0.265 | 0.75 | PASS |
| X-R5-fp32 | 0.393 ± 0.089 | 0.317 | +0.076 | 0.186 | 0.75 | PASS |
| X-R6a | 1.437 ± 0.118 | 1.283 | +0.155 | 0.331 | 0.50 | PASS |
| X-R6b | 1.419 ± 0.214 | 1.362 | +0.057 | 0.294 | 0.50 | PASS |
| X-R6c | 0.018 ± 0.242 | −0.080 | +0.098 | 0.302 | 0.50 | PASS |
| X-R7 | 5.682 ± 0.379 | 5.544 | +0.138 | 0.440 | 0.50 | **INCONCLUSIVE** |
| X-R8 | 5.815 ± 0.148 | 5.995 | −0.180 | 0.213 | 0.75 | PASS |

**Aggregate: PASS** (no FAIL, 23 of 24 PASS; the registered line is no FAIL and at least 12 PASS).

**The arms** (`scored.json` › `arms`; passes kept, the gate summary, E93's 24 rules, the cross-card aggregate, the tie):

| arm | slope (W/°C) | kept passes | gate summary | tally | cross-card | tie E78 |
|---|---|---|---|---|---|---|
| primary | 0.1994 | 4 | PASS | 23 / 1 / 0 | PASS (23, 1 INC) | PASS |
| dips_kept | 0.1994 | 2 (12110, 12111 set aside: `fp16.randn` spans 1.155 W, `int8.full` 1.027 W) | NOT SCORED | — | NOT SCORED | PASS |
| auto | 0.1553 (103 runs) | 4 | PASS | 23 / 1 / 0 | PASS (23, 1 INC) | PASS |
| leak0.2414 (E93's frame) | 0.2414 | 4 | PASS | 23 / 1 / 0 | PASS (23, 1 INC) | PASS |
| leak0.3803 | 0.3803 | 3 (12112 set aside: `int8.zeros` departs −0.270 W from its straight line) | INCONCLUSIVE (R7 UNRESOLVED) | 22 / 1 / 0, 1 UNRESOLVED | PASS (20, 3 INC, 1 UNRES) | FAIL |
| leak0.545 | 0.5450 | 2 (12112, 12113 set aside: `int8.zeros` departs −0.396 and −0.277 W) | NOT SCORED | — | NOT SCORED | FAIL |
| leak0 | 0 | 4 | PASS | 23 / 1 / 0 | PASS (23, 1 INC) | FAIL |

**The session tie** (`scored.json` › `primary.tie_e78`): every cell inside its band of E78's on this card.

| cell | D (W) | E78 (W) | difference | band | verdict |
|---|---|---|---|---|---|
| `anchor_pi` | 8.423 | 8.360 | +0.063 | ±0.5 | PASS |
| `fp32.randn` | 24.741 | 24.725 | +0.016 | ±0.5 | PASS |
| `fp16.randn` | 22.139 | 22.162 | −0.024 | ±0.5 | PASS |
| `int8.full` | 7.120 | 7.056 | +0.064 | ±0.25 | PASS |
| `fp32.a_zeros_b_randn` | 0.722 | 0.810 | −0.089 | ±0.25 | PASS |
| `int8.a_zeros_b_full` | 0.243 | 0.305 | −0.063 | ±0.25 | PASS |
| `fp32.sparse50` | 7.331 | 7.302 | +0.029 | ±0.75 | PASS |

**Reported, beside the rules** (`scored.json` › `reported`, `checks`): denormal − `-0` per side, fp32 both 1.51 ± 0.14, constant 0.16 ± 0.15, A 0.78 ± 0.10,
B 0.87 ± 0.14 W; fp16 both 1.34 ± 0.14, A 0.48 ± 0.14 W. int8's units, on E93's assumption that half of `full` is the data units' (`int8_unit_costs_w`):
gated 1.42 ± 0.33 W, live on a zero B word 4.30 ± 0.24 W for all 16 (card 1: 1.55 ± 0.31 and 4.05 ± 0.30). This session's own scale over card 1: `fp32.randn`
1.031, `fp16.randn` 1.026, `int8.full` 1.023, `anchor_pi` 1.042. E78-R5's checks: idle consistency median 0.068 W (≤ 0.15), rail lag re-fitted 0.95 s,
carry-over 0.0011 ± 0.0006 W/W, cycles per op 546.001 / 546.001 / 318.0, idle 25.91 ± 0.02 W at the launch reading, 521.7 mV. Dip samples removed per pass:
17, 12, 10, 5. E95's dips-removed anchors on this card (at its own auto slope, 0.299 W/°C) are printed beside the tie, with no verdict.

## Registered against what happened

| | registered | happened |
|---|---|---|
| freeze | before the claim and the first launch | `b66434a8` pushed 19:21:26; claim edit 19:23:25; first device access 19:23:35 (the smoke block's die reading, its t0 19:23:34.8); first launch 19:23:41 |
| setup | no device access; every card and E121 file identical to the freeze; a dry pass | 19:17:39, 19:19:56 and 19:20:31 on aifoundry3; the last ran dry pass 12100 (42 launches, 17 on E93 tiles, no `ET_DEVICES`) with every hash identical (`logs/setup.log`, `logs/e121-dry.log`) |
| smoke and gate | 12101, eight 2 s runs; ok, 1,024 minions, cycles per op 546 / 318, all eight items, both reads 0 / 65 at 600 MHz | block 19:23:35–19:24:23, launches from 19:23:41: 48 launches ok, 546.0 and 318.0, 0 / 65 / 600 MHz / 523 mV at both ends: **SMOKE GATE PASS** (`logs/smoke.log`) |
| passes | 12110–12114 planned, the budget rule decides, at least 3 kept | 12110–12113 ran (404, 384, 398, 378 s); 12114 was not started, its projected end past T0 + 1,980 s (`logs/e121-queue.log`) |
| kept | at least 3 kept to score | **4 of 4**; none set aside by the registered gates at the primary |
| skipped runs | a run whose launch reading is not reached is skipped, never launched off protocol | 2 of 160: 12110 `int8.a_zeros_b_full` (position 17) and `fp16.zeros` (19), the die still reading 59 °C after the quiet wait. The pass is kept by the registered code; R7 and that cell have three passes |
| budget | at most 35 card-minutes, claim to release, in seconds from the claim edit | 28.6 min (19:23:25–19:51:59); queue end at T0 + 1,683 s |
| config | read at both ends of every block and at the session's start and end, never set | TDP 0, threshold 65, `max_power`, 600 MHz, 522–523 mV in all eleven reads (the smoke's two, the passes' eight, the session-end one) |
| claim | a clause in the day's one post, added and later erased or marked released by editing it | added at 19:23:25 beside aifoundry1 card 1's clause; erased at 19:51:59 with aifoundry2's clause still held. Both edits first met another session's rewrite (`edit_replace.mjs` exit 7) and were rebuilt from the post's live text, as the protocol says |

**Departures:** none from the registration.

**PMIC reads (disclosed after verification, Sun 1 Nov 2026; C2).** The stock `ettelem` reads two PMIC voltage registers per `config` call and eleven per
`sample` (reads, no write), as in every run since September. This session made eleven `config` reads; its committed telemetry holds 16,004 samples (the
smoke and four passes, 10 Hz); each block's die readings are short `ettelem sample` calls too. Whether "no PMIC command" covers such reads is the owner's
open question of 1 Nov; it is disclosed here, not settled.

*Dated note, Mon 2 Nov 2026 (Q136's records): the open question is answered. The owner's ruling of 2 November 2026 allows
read-only PMIC voltage-register reads, so these reads are allowed ([AGENT.md](../../../../AGENT.md) §5, "Device commands").*

## What it closes and what it leaves open

- **The zero gate's closed entry (old item 4) now stands on two cards**: negative zero and denormal words against exact zeros (R1–R4), int8's eight-byte B
  rule (R6a) and its `(l, l+8)` pairing (R6b, R6c), and the A word (R7), at power resolution on aifoundry1 card 1 (E93) and aifoundry3 card 0 (E121), in
  agreement with the RTL. The page's "on one card" can become "on two cards"; "the micro-op counters were not read" stays.
- **The magnitudes carry across by the card scale** (23 of 24 cross-card rules; median per-cell ratio 1.030 against E82's 1.031): E93's watts for these tiles
  are not a card-1 quirk.
- **Item 15's two E93 leftovers: what replicates, and neither is explained.** R5's failure replicates: a live zero on B costs only +0.39 ± 0.09 W more than
  on A in fp32 here (card 1: +0.31 ± 0.16 W), not the +3.1 W the Booth generator predicted. The 1.72 W A-side excess behind item 15's "costs 1.72 W more than
  priced" is E93 C3's split of card 1's shortfall and was not recomputed on this card; aifoundry3 prices such as
  [E116](../2026-11-01-e116-split-replicate/README.md)'s (E88's split on this card) could supply it later. The half-gated int8 tile again reads more than the
  gate law (+0.55 ± 0.15 W, three passes, post hoc; card 1: +0.65 W). Two cards, one fixed set of tiles; power is the only reading (C3).

## Blog sentences, each with its baseline, its cards and its source

- The zero gate compares raw bits, on two ET-SoC-1 cards (aifoundry1 card 1 and aifoundry3; 1,024 minions, 600 MHz): `-0.0 × -0.0` costs 7.9–8.2 W of board power over `+0.0 × +0.0` in fp32
  and 8.0–8.2 W in fp16, about what multiplying two constants costs. [E93 and E121 R1-fp32-both, R1-fp16-both, R2-fp32]
- On both cards, `0x00000001 × 0x00000001` costs 8.0–8.4 W over exact zeros in fp32, and random denormal fractions add only 1.35–1.40 W, about what their raw
  bits cost on the operand bus (16.9–17.6 fJ a bit), consistent with the manual's flush to zero. [E93 and E121 R3-fp32-one, R4-fp32-both]
- In int8, the same words with the same operand bus bits read 4.3 W over int8's zeros when the eight zero words a line fill columns `(l, l+8)`, and 5.5–5.7 W
  otherwise, on both cards; `(2l, 2l+1)` is rejected, in agreement with the RTL. [E93 and E121 R6a–c]
- An int8 A word with one nonzero byte reads 5.8–5.9 W over int8's zeros, against 0.2–0.4 W when all four bytes are zero, on both cards. [E93 and E121 R7]
- aifoundry3's watts for these tiles are about 3% above aifoundry1 card 1's (median 1.030 over 22 cells), the same card-to-card scale measured across 32
  kinds of numbers. [E121 `readme-numbers.txt`; E82]

## Files

`e121.json` the primary reduction (dips removed, 0.1994 W/°C), `e121-dipskept.json`, `e121-auto.json`, `e121-leak<k>.json` the arms, with their
`reduce*.txt/.log` and `runs*.csv`; `scored.json` every verdict, arm and reported number; `results.md` the same in tables; `readme-numbers.py` and
`readme-numbers.txt` the derived and post hoc numbers this README quotes; `code.sha256`; `logs/` the setup, the dry pass, the smoke, the queue, the
session-start and session-end config reads, the push and claim times; `aifoundry3/kinds/p121<nn>/` each pass's raw data (telemetry, marks, runs, tile dumps,
config reads, manifest), `kinds-smoke-p12101` the smoke. Reproduce from the raw passes:
`PY=/usr/bin/python3 bash tools/claims-v3/e121/collect_e121.sh 'p121[1-9][0-9]' <raw root>`. The committed reductions were made from the repo root with
the relative raw root `build/claims-v3/aifoundry3` (the passes' path under the box's tree, holding `kinds/`, `kinds-smoke/` and `logs/` copied from this
directory), so `dirs` and the `dir` column read `build/claims-v3/aifoundry3/kinds/p121<nn>` (C1).

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier (Q134's) checked E121 the same evening, after the data commit (`dd9e8466`). Its verdict: holds with fixes, one major fault (public
text) and six minor ones in how the results were stated. It re-ran the registered collector over the committed raw passes (`scored.json`, `results.md`,
`reduce*`, `score.log` and `code.sha256` byte-identical), matched 35 raw-file hashes on aifoundry3 (read only) against the committed copies, recomputed
five rule intervals and X-R7's verdict by hand, and found the registration timing, the frozen rules, the tiles, the card's safety and the posting protocol
sound. Each fault is corrected above, at the desk: no card was touched, and no registered prediction, rule, number or verdict changed (24 of 24 as E93,
23 PASS, 1 FAIL; cross-card aggregate PASS). `scored.json`, `results.md`, `reduce*`, `score.log`, `code.sha256`, `readme-numbers.txt`, `logs/` and the raw
passes are byte-identical to `dd9e8466`.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **Desk paths in public files.** The seven reductions (`e121*.json`, `dirs`) and their seven `runs*.csv` (`dir` column, 158 rows each) named the raw root as the lane's scratch folder on the desk machine, an absolute home path: 1,134 lines, the only such paths under `docs/reports/data` | The registered collector (code at `dd9e8466`) was re-run over the committed raw passes from a repo copy's root with the relative raw root `build/claims-v3/aifoundry3`, as E93's was. The 14 files now read `build/claims-v3/aifoundry3/kinds/p121<nn>`, and each equals its first version with only that prefix replaced (`git diff dd9e8466` on them shows only those lines); every other output of the collector is byte-identical to `dd9e8466`, and `readme-numbers.py` prints `readme-numbers.txt` unchanged. Git history keeps the old text |
| C2 | **PMIC reads undisclosed.** The opening said "no PMIC command" and nothing of the stock telemetry's PMIC register reads | A paragraph under § Registered against what happened: two register reads per `config` call, eleven per `sample`, reads with no write; eleven `config` reads and 16,004 samples here; whether such reads count is the owner's open question of 1 Nov, disclosed, not settled, as E124's README says it. The opening points to it |
| C3 | **Item 15's first leftover was over-claimed.** Result 6 said item 15's "why a live zero on A costs more than priced" is "not a card-1 artifact", and § What it closes called both leftovers "confirmed". What replicates is R5's failure (+0.39 ± 0.09 W here, +0.31 ± 0.16 W on card 1). The page's 1.72 W is E93 C3's split of card 1's shortfall (2.793 W = 1.718 W of `a_nz_b_randn` above its priced point + 1.075 W of `a_randn_b_nz` below it), and E121 did not recompute it | Result 6 and § What it closes say R5's failure replicates and the A-side split was not recomputed on this card, naming E116's prices as a way to supply it. The half-gated int8 tile's excess (+0.55 ± 0.15 W, post hoc) is the leftover that replicates as measured |
| C4 | **Device access was dated from the first launch**: 19:23:41, 27.8 min, in the opening and the table. The smoke block began at 19:23:34.8 and read the die at 19:23:35 (`logs/smoke.log`), which is device access | Device access 19:23:35–19:51:28, 27.9 min; the first launch stays 19:23:41. The order holds: push 19:21:26, claim edit 19:23:25, device access 19:23:35. `logs/push-and-claim-times.txt` keeps the lane's command-output times as written |
| C5 | **Small things, found in this pass, not by the verifier.** Two card-1 numbers were rounded twice: R4-fp32-both is 1.4047 W on card 1, printed 1.41 in result 2 and in the second blog sentence, and fp16's Booth twin is −0.7545 W, printed −0.76 in result 6. Result 6 cited `reported.booth_asymmetry_w`, which in this `scored.json` sits under `reported.e93_reported_block` | 1.40 and −0.75, as E93's README prints them; the citation names the full key |
| C6 | **"The second card" and "the first card" in the blog text** reverse the kinds page's convention, where aifoundry3 is the main card and aifoundry1 card 1 the second card | The blog sentences and § What it means for the blog name the cards |

Three more of the verifier's faults were in the lane's report to the integration lanes, not in this page (its blog points, one table cell's pass count,
and the arms' wording, where what holds is that no verdict flips between PASS and FAIL at any arm that scores); they were corrected there.
