# Q129 — every aifoundry3 reduction re-priced at the card's measured idle leakage slope

**Desk-only, Wed 28 Oct 2026 (week 44). No card was touched: no `ssh` to a lab box, no run, no governor read or
write, no device opened.** Labelled sensitivities beside the registered scoring. **Nothing published is replaced
and not one verdict moves.**

E66 measured aifoundry2's idle leakage slope and E71 measured aifoundry3's. Four aifoundry3 experiments — E60, E65,
E67, E70 — were reduced with a slope none of them had measured: `reduce_hl.py`'s own within-run estimator, fitted
inside each 2 s kernel window. This directory re-runs each of them, with **each experiment's own reduce and scoring
code**, at aifoundry3's measured idle slope, and rebuilds Q128's data block from the result.

E71 already published the per-position **price** shifts for E65 and E67 (its `sensitivity-e65-ab.json`,
`sensitivity-e65-blockD.json`, `sensitivity-e67.json`, `sensitivity-e67-clean.json`). What is added here is what
E71 left: **E60's aifoundry3 rows**, **E65's flow-M row**, **E67's interaction grid**, **E70's saturation ladder and
A-side multi-bit ladder**, and the pass from the re-reduced price lists all the way through `chain.py` and
`build_data.py` into Q128's `perbit` block.

## The slope, by card and by band

| slope, W/°C | card | band | how it was got |
|---|---|---|---|
| **1.508** | aifoundry2 | the kernel's own 2 s window | the registered estimator on a **busy transient** (E68's A1). It is **4.0–5.1× every measured idle slope** and is not an idle leakage slope at all |
| 0.168–0.203 | aifoundry3 | each run's own 2 s window | the same estimator, as E60 (0.2026), E65 A+B (0.1824), E67 (0.1755), E67 clean (0.1683) and E70 (0.1975) actually ran it. E65 block D took 0.0692 |
| **0.2936** | aifoundry2 | 51–58 °C | E66, 18 cycles, sd 0.0012 (E71 reproduces it exactly) |
| **0.3452**, sd 0.0112 | aifoundry2 | **58–62 °C** | E71's re-fit of E66's own 18 passes. The 18 per-pass fits run 0.3183–0.3613: sd 0.0112, SEM 0.0026, MAD 0.0074. E71's own README writes "± 0.0056", which is exactly half that sd and matches no spread of these 18 values; it was inherited unchecked and is superseded by the sd quoted here (corrected 2026-10-28) |
| 0.3200 | aifoundry3 | 52–58 °C | E71 |
| **0.3803 ± 0.0036** | **aifoundry3** | **58–62 °C** | **E71**, 6 cycles, sd 0.0036 — the band every reduction here launched in, and the slope used throughout this directory |
| 0.3957 | aifoundry3 | 58–65 °C | E71 (the better k for E65's block D, whose kept arm launches at 61.0 °C) |

Two things follow and both matter more than the card-to-card difference. **A leakage slope is not a card constant**:
it rises about 0.009 W/°C per °C of die temperature on aifoundry2 and about 0.011 on aifoundry3, so E66's 0.294 is
only 77% of the slope these aifoundry3 reductions needed, and about three fifths of the E66-to-E71 gap is the band
rather than the card. And **the registered 1.508 W/°C was never a leakage slope**, which is why re-pricing at the
measured one moves prices by only a few per cent: every auto k these reductions actually used was already 0.17–0.20,
not 1.508.

## What moves, in one table

Group means at 0.3803 W/°C against each reduction's own auto k. Individual items spread wider than their group
(E71: +4.0% to −9.0% across the 166 price items), so **never quote a group mean of a single number**.

| Experiment | what was re-done here | the headline shift | verdicts |
|---|---|---|---|
| **E60** (bitflip ladder) | the **aifoundry3 rows only**, re-reduced (aifoundry1's and aifoundry2's keep their own slopes) | `lq` per designed bit **116.746 → 115.049 fJ** (−1.45%), `lb` **129.918 → 127.687 fJ** (−1.72%); the 6 priced B positions −1.8% to −3.3%; the marginal slope 0.5362 → 0.5284 W per h | — (E60 has no prediction re-scored here) |
| **E65** blocks A+B | full re-reduction; the **flow-M row** | **flow-M 745 ± 56 → 722 ± 61 fJ** (−3.07%); 32 B positions: low-mantissa mean 109.3 → 103.6 fJ (−5.17%), bit 22 1008 → 985, span 12.15× → 12.81× | B1 still FAILS its 100–250 fJ band (2.9× its top, was 3.0×) and still PASSES board ≥ gate |
| **E67** | full re-reduction, `closure.py` and `report_e67.py`; the **interaction grid** | grid mean excess **−1.351 ± 0.281 → −1.310 ± 0.278 W**, largest cell 4.051 → 3.975 W, 8/16 → 9/16 cells within 20%; the implied turn-on T 1.351 → 1.310 W, so A14's marginal correction becomes **579** fJ per A bit and **289** per B bit (published 597 and 298) | **P1–P8 all unchanged**, P6 still FAIL (sub-additive), P8 still FAIL |
| **E70** | `report_e70.py`'s registered six-pass scoring; the **saturation ladder** and the **A-side ladder** | every rung falls — over the 22 rungs more than 7 SE from zero the fall is **1.8% to 8.6%** (`lq` −2.1% to −6.8%, `ls` −1.8% to −3.0%, `alq` −2.2% to −8.6%), while the 23rd, `alq_h1`, falls 11.3% at only 4.0 SE from zero (0.282 ± 0.070 → 0.250 ± 0.066 W), inside its own interval; W∞ refit 10.52 → 10.16 W; residual rms 0.232 → 0.236 W refit, **0.595 → 0.696 W frozen**; ρ(12) 1.266 ± 0.011 → 1.246 ± 0.014 | **P1–P8 all unchanged**, P5 still FAIL |
| **E67 closure** | a **second route** to E71's `closure_refit.py`: full re-reduce + E67's own `closure.py` over the rebuilt tiles | A side predicted −3.86% vs measured −2.07%: **0.4326 → 0.4406**; B side −3.22% vs −2.15%: **0.4985 → 0.5040** — identical to E71's corrected figures to four digits, which is near-structural rather than independent (both routes take the same re-reduced powers and the same re-priced lists, and the ratio is linear in both). What the second route **does** establish: the committed per-pass `tiles/<item>.b<pass>.bin` copies are the files the published closure used | the 2.0–2.3× over-prediction stands |

The one figure that degrades materially is E70's **frozen**-ceiling residual, 0.595 → 0.696 W (+16.9%), and it is an
artefact of mixing slopes: the 12.581 W ceiling was frozen from E60's ladder at E60's *own* auto k. Re-de-leaking
E70's rungs while leaving that constant alone is apples to oranges — E60's ladder at 0.3803 gives a marginal
0.5284 W per h instead of 0.5362, so a consistently re-frozen ceiling falls with it. D2's verdict is untouched: the
refit still beats the best possible law in Hamming weight alone by 5.7× (was 5.8×) and pure additivity by 26×.

## Exactly how Q128's `perbit` block should change

Q128's `perbit` block (`docs/reports/data/2026-10-27-matmul-to-transistor/data.json`) has two kinds of entry, and
they need different treatment.

**(a) Computed — they follow automatically.** Re-running `chain.py` over the three re-reduced `hl.json` files and
then `build_data.py` produces all of these; `q128-data-at-0.3803.json` here *is* that rebuild, and
`q128-data-diff.txt` is every number in the whole data block that moves. Nothing is hand-edited.

| key | published | at 0.3803 W/°C |
|---|---|---|
| `B_fJ` (32), `B_se_fJ` | low-mantissa mean 109.25, bit 22 1007.8, exponent 174.27, sign 122.60 fJ | 103.61, 985.4, 166.35, 121.73 fJ (−5.17 / −2.22 / −4.55 / −0.70%) |
| `A_fJ` (32), `A_se_fJ` | low-mantissa mean 305.05, bit 22 1440.4, exponent 265.17, sign 247.35 fJ | 290.28, 1396.4, 254.83, 238.32 fJ (−4.84 / −3.05 / −3.90 / −3.65%) |
| `B_min` / `B_max` / `B_span` | 82.94 / 1007.8 / 12.152× | 76.90 / 985.4 / **12.814×** |
| `A_min` / `A_max` / `A_span` | 152.52 / 1440.4 / 9.443× | 140.92 / 1396.4 / **9.909×** |
| `shape` (both sides, 4 regimes each) | — | as the two rows above |
| `ladder_rows` (7 E60 `lq` rungs) | dW 0.594 … 12.261 W | −1.7% to −7.9%; the *naive* sum falls less (−1.9% to −4.9%), so **`ratio` rises** at every h ≥ 2 (h = 23: 0.3036 → 0.3085) |
| `flat_fJ_per_bit` | 107.092 | **104.835** (−2.11%) |
| `flat_marginal_fJ` | 116.801 | **115.100** (−1.46%) |
| `beta` | 0.99348 | **1.01058** (+1.72%); `alpha` 0.7747 → 0.7834, `c_pow_W` 0.4807 → 0.4510 |
| `laws` | flat rms 14.383 / worst 22.66; free_power 13.307 / 19.05; price_list_compressed 28.480 / 62.50 | 14.302 / 23.32; **12.497** / 18.13; **29.482** / 64.35 — the free power law improves 6.1% and the price-list law worsens 3.5% |

**(b) Hard-coded in `build_data.py` — they must be edited by hand.**

| key | published | should become | why |
|---|---|---|---|
| `flowM_fJ`, `flowM_se` | 745.0, 56.0 | **722.2, 60.8** | E65's `bpi_11` re-reduced: 3.4211 ± 0.2579 → 3.3162 ± 0.2791 W. The shift (23 fJ) is a third of the SE, so the *claim* is unchanged; the gate-level comparison moves from 6.2×/4.4× to **6.0×/4.3×** — the published convention is zero-delay 120 fJ (midpoint of 0.11–0.13 pJ) and glitched 1.4 × 120 = 168 fJ, which reproduces E65's own 6.2× and 4.4× — and the multiplier's share of a flipped operand bit is **unchanged at about 23%** (22.6% → 23.3%). The −3.07% is against E65's own 745.1; against Q128's rounded 745.0 it is −3.06% |
| `flowM_A_side_fJ` | 856.0 | **827.4** | E67's `abp_11`, −3.32% |
| `e60_lq_fJ`, `e60_lq_se` | 116.746, 0.613 | **115.049, 0.538** | E60's aifoundry3 `lq` per designed bit. These reach `data.json` through `transistor-ledger.json`, so `ledger.py` has to re-run over the re-reduced E60 `hl.json` as well |
| `e60_lb_fJ`, `e60_lb_se` | 129.918, 0.480 | **127.687, 0.424** | the same, busy partner |
| `e60_cards` | aifoundry3 quiet 116.746, busy 129.918; aifoundry2 121.3; aifoundry1 c0 102.490 | aifoundry3 quiet **115.049**, busy **127.687**; **aifoundry2 and aifoundry1 unchanged** | this slope is aifoundry3's. Re-pricing another card's rows with it is exactly the mistake the Levels caution warns about |
| `e68_band_fJ` | [117.5, 135.9] | **135.2 ± 0.2 fJ — a point value, not a band** | **both published ends are mis-banded for E68.** 117.5 came from the registered 1.508 W/°C, a busy-transient fit 4.0–5.1× every measured idle slope; 135.9 came from E66's 0.2936, fitted over **51–58 °C**. All 574 E68 runs launch at exactly 58.0 °C with windows 57.8–60.8 °C, so by this file's own criterion — a slope belongs to the band it was fitted in — the slope to use is aifoundry2's measured **58–62 °C** value, 0.3452. E68's own committed table is linear in k (`sm_lo12` = 140.4 − 15.19 k fJ), so 0.3452 → **135.2 fJ**, and the 18-pass spread (sd 0.0112) moves that by only ±0.2. `sm_hi12` → 193.5 and `sm_sp12` → 215.2 fJ at the same slope. Keeping [135.2, 135.9] would quote a band spanning **two bands on one card**, not two defensible slopes (corrected 2026-10-28: this row first recommended that band) |
| `e68_vs_e60_same_card` | [133.7, 121.3] | **open — do not patch from here** | 133.7 is E68 at E60's aifoundry2 auto k 0.442, itself a busy-transient fit. The E68 side becomes 135.2 at aifoundry2's measured 58–62 °C slope, but the E60 side (121.3 fJ, aifoundry2, 800 MHz) needs aifoundry2's rows re-reduced, which **this lane did not do** |
| `e66_leak_W_per_C`, `a1_leak_W_per_C` | 0.294, 1.508 | a per-card, per-band block, not a pair of constants | **a slope quoted without its band is ambiguous at the 20–30% level** — larger than the 10% card-to-card difference it is usually invoked for. The seven measured values are in the table at the top of this file |

**What does NOT change.** `waterfall` is byte-identical: not one pJ moves from "unaccounted" to "accounted", because
Q128's waterfall rests on E38's registered random-MAC means (board 5.783 pJ, rail 4.337 pJ), which no leakage slope
touches. `transistor`, `floor`, `gates`, `rail` and `toggles` are byte-identical too — the whole bottom-up ledger
(1.946 pJ) is untouched. What moves is the **measured** side of the comparison, and it moves **toward** the
open-netlist figure by a few per cent, cheap positions most.

Also moved, as a consequence and worth carrying: `board.step_W` 24.659 → 24.131 W, `board.data_W` 16.442 → 16.067 W,
`board.clocking_W` 8.217 → 8.064 W, `permac.this_work_data_pJ` 3.627 → 3.545, `permac.this_work_clocking_pJ` 1.813 →
1.779, `permac.data_per_changed_bit_fJ` 132.56 → 129.54, and the governor/closure blocks' extrapolated TFLOPS by
+0.7% to +1.0% (all 30 closure entries and 8 governor entries are in `q128-data-diff.txt`).

## Reproduction, which is the integrity check

Every reduction was also run at **its own published auto k**, and each had to reproduce the committed file. All five
did:

| re-run at the published slope | reproduces |
|---|---|
| E60 aifoundry3 | **every price number** in `hl.json` exactly (`lq` 116.746 ± 0.613, `lb` 129.918 ± 0.480 fJ, `lq` per bus 74.6579 to 1e−9; 220/220 runs kept, same set-aside list). Not byte-for-byte: the re-run's `cards/aifoundry3` loses the `xnz` family — 13 leaves, the `xnz_h*` rungs without their `xin_h0` zero and `ec/xnz` with `n_passes` 0 and its `se_J` nulled |
| E65 blocks A+B | **every price number** in `hl.json` exactly (205/287 kept, passes 654 and 656 set aside). Not byte-for-byte: the re-run carries 33 `anchors/*` keys the committed file does not |
| E67 | **every price number** in `hl.json` exactly (424/554 kept, passes 754, 771–773 set aside), and `closure.json` to **worst absolute difference 0.0** |
| E67 scoring | `scored.json`: grid mean excess −1.351 ± 0.281 W, largest cell 4.051 W, 8/16 within 20% — every published digit |
| E70 scoring | `scored.json` to **worst relative difference 0.0**, every key |
| `chain.py`, `build_data.py` on the unmodified repo | the committed `chain.json` and `data.json` to **worst relative difference 0.0** |

No kept-pass set changes anywhere at the measured slope, and no pass moves in or out of a set-aside list.

The two "not byte-for-byte" notes above cost no number. `xnz` is read by no downstream script — not `chain.py`,
not `build_data.py`, not `ledger.py` — and the `anchors/*` keys are not prices. Every re-run also differs from
its committed file in the `runs[i]/dir` path strings (554 of them in E65's) and in `gates/*/leak_runs`, neither of
which enters a number; the splice of a re-reduced
`aifoundry3` block into the Q128 shadow is lossless, which the published-k arm proves by reproducing the
committed `data.json` to worst relative 0.0. (Both notes added 2026-10-28 after review: the table had said
"`hl.json` exactly".)

`closure.py` reads the operand tiles from the generator directory, which is not committed; `refit.sh` rebuilds it
from the per-pass `tiles/<item>.b<pass>.bin` copies that *are* committed. That the rebuilt `closure.json` matches the
published one to 0.0 W is also the check that those copies are the files the published closure used.

## Departures and limits

1. **E70's `grid_T_W` and `turn_on_T_W` stay at E67's published 1.351 W** in both E70 runs, because `report_e70.py`
   is given E67's committed `closure.json`. At the measured slope E67's own grid gives 1.310 W, which moves D3's
   comparison value by 3% and no verdict.
2. **E65's block D is not re-done here** — E71 re-priced it, and its kept arm launches at 61.0 °C with windows
   61.9–62.4 °C, so a 58–65 °C slope (0.3957) is the better k for that arm. **E65's block C is unaffected**:
   `reduce_ladder` de-leaks with IDLE brackets, not a slope.
3. **aifoundry2's and aifoundry1's rows are not re-reduced.** E60's aifoundry2 rows, E68, E69, E72 and E73 all sit on
   aifoundry2, whose measured slope at its own launch band is **0.3452**, not E66's 0.294. That is a separate lane.
4. The slope itself is fitted on a **transient cooling** on both cards, so the die sensor's lag and the board parts
   the `minshire` sensor cannot see are a shared systematic that neither E66 nor E71 bounds.
5. `report_e70.py`, `report_e67.py`, `chain.py` and `build_data.py` need Python ≥ 3.12 (nested same-quote f-strings);
   `reduce_hl.py` needs numpy. `refit.sh` takes both as `PY312` and `PY_NP`.

## Files

| File | What |
|---|---|
| `refit.sh` | every command, in order: the eight reductions, the rebuilt tile directory, `closure.py`, `report_e67.py`, `report_e70.py`, and `chain.py` + `build_data.py` over a shadow repo root that is symlinks plus four substituted files |
| `sensitivity.py`, `sensitivity.txt`, `sensitivity.json` | the comparison: every number at both slopes, printed and machine-readable |
| `q128-data-at-0.3803.json` | the **computed** half of Q128's data block at the measured slope — the 11 hand-coded `perbit` entries in it are still the published values (section **(b)** above): `flowM_fJ` 745.0, `flowM_se` 56.0, `flowM_A_side_fJ` 856.0, `e60_lq_fJ`/`_se`, `e60_lb_fJ`/`_se`, `e68_band_fJ`, `e68_vs_e60_same_card`, `e66_leak_W_per_C`, `a1_leak_W_per_C`. Renamed in description, not on disk, 2026-10-28: it was called "Q128's whole data block" |
| `q128-data-diff.txt` | every one of the 275 numbers in that block that moves, by block |
| `../2026-10-20-bitflip-ladder/leak-sensitivity-e71.{txt,json}` | E60, aifoundry3 rows |
| `../2026-10-26-e65-bit-prices-hart-ladder/leak-sensitivity-e71.{txt,json}` | E65 blocks A+B and the flow-M row |
| `../2026-10-27-e67-a-side-bit-prices/leak-sensitivity-e71.{txt,json}` | E67's 32 A positions, the interaction grid, the closure |
| `../2026-10-27-e70-saturation-ladder/leak-sensitivity-e71.{txt,json}` | E70's three ladders and its registered scoring |

The slope itself: `../2026-10-27-e71-idle-slope-aifoundry3/` (`slopes.json`, and E71's own four price sensitivities).
E68's aifoundry2 ladder of slopes: `../2026-10-27-e68-stage-map/leak-sensitivity.txt`.

## Corrections after review, 2026-10-28

An adversarial review of this directory found nine faults, all in **text, labels and recommendations**: not one
number in `sensitivity.json`, `sensitivity.txt`, `q128-data-at-0.3803.json` or the four
`leak-sensitivity-e71.json` files changed, and no reduction or scoring code was touched. The review re-ran
`refit.sh` end to end from a clean tree and got a byte-identical `sensitivity.txt` and an identical
`q128-data-at-0.3803.json`, and re-scored E67's and E70's sixteen registered verdicts at both slopes with the
registered code: still identical. Corrected here:

| # | was | is |
|---|---|---|
| 1 | A14's marginal correction "582 fJ per A bit" (E67's `.txt`), and "581 / 288" in the lane's hand-off | **579** and **289** fJ, which is what the committed JSON holds (596.847 → 578.804, 298.424 → 289.402) |
| 2 | the flow-M gate-level comparison "6.2×/4.4× → 6.0×/4.2×, share rises 23% → 24%" | **6.0×/4.3×**, share **unchanged at about 23%**. A −3.07% shift cannot move a ratio by 4.5% |
| 3 | "reproduces `hl.json` exactly" for E60 and E65 | "every **price number** exactly", with the dropped `xnz` family and the 33 extra `anchors/*` keys named |
| 4 | aifoundry2's 58–62 °C slope "0.3452 ± 0.0056", inherited from E71 | **0.3452, sd 0.0112** (SEM 0.0026, MAD 0.0074 over the 18 passes); ± 0.0056 is half the sd and matches nothing |
| 5 | `e68_band_fJ` → [135.2, 135.9] | **135.2 ± 0.2 fJ**, a point value: the upper end is E66's 51–58 °C slope, the wrong band for E68 by this file's own criterion |
| 6 | D1 "74 → 109 SE from zero", read as the verdict getting sharper | verdict **confirmed, unchanged**; the SE change is a property of the de-leaking constant and goes both ways (E65's `bpi_11` SE **grows** 8%) |
| 7 | "every rung falls 1.8–11.3%" | **1.8–8.6%** over the 22 rungs more than 7 SE from zero; `alq_h1`'s 11.3% is 4.0 SE from zero |
| 8 | the closure as "an independent confirmation of E71's correction" | a **second route** that agrees near-structurally; its real finding is that the committed per-pass tile copies are the files the published closure used |
| 9 | `q128-data-at-0.3803.json` as "Q128's whole data block" | the **computed half**; its 11 hand-coded `perbit` entries are still published values |
