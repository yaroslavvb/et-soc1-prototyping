# Dated note 1 beside the README (Fri 6 Nov 2026, week 45): the leak correction moved his pair within its noise and carries no factor of its own; aifoundry3's minion monitor reads 3-4 mV under its set point, not within 2; the board value refreshes with the rails every pass, and the 155 ms pass dates to between 29 Sep and 20 Oct

*This note sits beside [`README.md`](README.md) (`b5ab9d46`) and changes nothing in it; that file stays as committed. It corrects
three of its readings, as Q150's verifier found them, with the check script and output committed beside it. Every figure is POST HOC,
as the README's are: no registered number, rule or verdict of any run changes, E178's included. Desk only: no card and no lab machine
was touched. Its time is its commit's.*

## Builds on

- **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 16:00 PST. Public rows read: P01, P03, L06, L08, L11, L23, H24,
  H28. The ids are opaque pointers into a private inventory.
- **Used:**
  - E178's committed reductions on two footings, `../2026-11-06-e178-one-number-aifoundry3/runs.csv` (registered, leak-corrected) and
    `runs-leak0.csv` (no leak correction), and its kept passes' `telemetry.jsonl.gz`;
  - the kept passes of E171 (aifoundry3) and E172 (aifoundry1's card 1);
  - aifoundry3's committed telemetry with no statistics reset from 29 Sep to 6 Nov: E58
    (`../2026-09-29-tau-aifoundry3/`), the 20 Oct bitflip ladder, the 21 Oct dtf runs, E65, E70, E78, E171 and E178; card 1's E58
    (`../2026-09-29-tau-aifoundry1-c1/`) and E172;
  - E178's dated note 1 (`../2026-11-06-e178-one-number-aifoundry3/README.md.dated-note-1.md`, `f68f0380`) on its pass means;
  - the order term on his pair, first found post hoc by the card day's critic and recomputed here.
- **Not used:** E180's data (another run's); any card time.
- **Tiers:** public only.

## 1. The leak correction on his pair is inside the noise, and is not "a factor 1.4"

The README's answer table and section 4 read the registered leak correction as "the one meter-side term", which "takes 0.021 W
off the pair ... a factor 1.4" of the 3.5, leaving "about 2.5x" to the model; its fault 10 says the correction "carries a factor 1.4".
The README's own interval for that term holds 0 (+0.0214 W [-0.0076, +0.0505]). On E178's committed couples (`q150_note1_checks.json`
› `A_e178_footing`):

| reading | registered footing | leak-0 footing |
|---|---:|---:|
| his pair, int8 5s - 4s, four passes | +0.0532 W [+0.0217, +0.0848] | +0.0746 W [+0.0421, +0.1072] |
| its half-width | 0.0316 W | 0.0326 W |
| couple sd (11 adjacent couples) | 0.1069 W | 0.0845 W |
| order term, first run of a couple less the second | **+0.066 W** | **-0.051 W** |
| the pair, order-adjusted | +0.048 W | +0.079 W |

- **On his pair** the correction takes 0.021 W off in the mean, with a per-couple sd of 0.13 W. The couples' variance ratio is 1.60 on
  10 and 10 degrees of freedom; even read as independent samples, that has a one-sided p of about 0.24. The four-pass half-width does
  not narrow without the correction.
  - The run before each of his 11 couples was an fp16 one-number kind, 6.6 W above the couple's first run.
  - With the correction, the first run of a couple reads 0.066 W above the second; without it, 0.051 W below.
  - E178's alternating order, 6 couples one way and 5 the other, cancels that order term to about +0.006 W in the mean.
- **On the other 7 adjacent same-format pairs within 0.15 W of each other** (42 couples), the correction's leak term averages
  +0.0007 W (sd 0.031) in the pairs' name order and +0.006 ± 0.005 W read first run less second: no order bias there, and its mean
  within 0.006 W of zero either way. It adds 8% to the couple scatter (rms 0.079 against 0.073 W); with his pair included, 13% (0.084
  against 0.075 W, 53 couples).
- **Over every same-format pair within 0.15 W run in one segment** (80 pairs, 379 couples, adjacent or not) the scatter is 0.0765 W
  with the correction and 0.0748 without it, 2% apart. The correction lowers it in 41% of the pairs, raises it in 33%, and leaves 26%
  unchanged.

**So the registered +0.053 W and the leak-0 +0.075 W differ by footing within the pair's noise.** The whole-degree correction carries no
factor of its own on near-equal pairs. M10's frozen +0.186 W stands 2.5x (leak-0) to 3.5x (registered) above the measurement, and is
the model's at either footing. The README's other exclusions (gain, filter, quantization, staleness, missing power, averaging) stand.

**The interval itself is narrower than E178's design predicts.** E178's dated note 1 records that his pair's four pass means agreed
more closely than the couples predict. At the couples' scatter (0.107 W, 2.75 couples a pass) a pass mean scatters about 0.064 W;
at the registered couple noise (0.125 W), about 0.075 W. The four passes read 0.020 W. At the predicted scatter, four passes give
about ±0.10-0.12 W, eight ±0.054-0.063 W and sixteen ±0.034-0.040 W (`F_arithmetic`).

## 2. The minion voltage reads 3-4 mV under its set point on aifoundry3, not within 2 mV

Section 1 says the set point confirms the on-die minion reading "within 2 mV, as the sibling directory also reads", and fault 5 says
the two "agree within 2 mV". The README's own figures for aifoundry3 (525 mV set, 521.2 busy and 522.1 at rest) are 2.9-3.8 mV
apart. On every kept sample of E171 and E178 (`B_die_minus_set_point_by_load`) aifoundry3's minion monitor reads 3 mV under the set
point at idle (90-95% of idle samples) and 3-4 mV under load (-4 in 33-54% of busy samples); its SRAM and NoC rails read -2 and
-1 mV. Card 1 reads -1 at idle and -1 to -2 under load on the minion rail, and +1 on SRAM and NoC. The sibling directory's 2 mV is
September's idle reading (its dated note 1). The conclusion stands: a misreading large enough for card 1's 10% would be about 25 mV,
and using the set points in place of the monitors moves the V squared ratio by 0.75% (1.1025 against 1.0943).

## 3. The board value refreshes with the rails every pass; the 155 ms pass dates to between 29 Sep and 20 Oct

The README's section 3 gives `board_w` a refresh of 163-166 ms on aifoundry3 and adds "repeats lengthen the board's figure". Its
first bullet places the change from 263 ms: "the card has run another service-processor build since 7 October". On samples with no
statistics reset (`C_refresh_by_date`):

| date, session | minion rail: mean time between changes | `board_w` | board changes on the rail's sample (or the next) | board changes when the rail does not |
|---|---:|---:|---:|---:|
| 29 Sep, E58, aifoundry3 | 283 ms | 292 ms | 94.3% (95.9%) | 1.0% |
| 20 Oct, bitflip ladder, aifoundry3 | 155.2 ms | 161.6 ms | 94.6% (97.5%) | 2.7% |
| 21 Oct, 26 Oct (E65), 27 Oct (E70), 31 Oct (E78), aifoundry3 | 154.8-155.1 ms | 161.2-165.2 ms | 92.9-94.9% (96.2-97.6%) | 1.7-2.6% |
| 5 Nov, E171, aifoundry3 | 154.9 ms | 163.2 ms | 93.6% (96.8%) | 2.4% |
| 6 Nov, E178, aifoundry3 | 154.9 ms | 166.2 ms | 91.9% (95.7%) | 2.2% |
| 29 Sep, E58, card 1 | 167.5 ms | 180.7 ms | 91.2% (94.2%) | 1.3% |
| 5 Nov, E172, card 1 | 156.8 ms | 169.5 ms | 91.2% (95.4%) | 2.4% |

- **`board_w` is refreshed in the same service-processor pass as the rails.** It changes on the rail's sample, or the next, at 94-98%
  of the rail's changes, and almost never otherwise. Its longer mean interval comes from passes whose new 10 mW reading equals the old
  one (4-7% of passes on aifoundry3). So the board's refresh is the pass, about 155 ms; 161-166 ms is that pass with its repeats.
- **The pass shortened between 29 Sep and 20 Oct.** No aifoundry3 telemetry between those dates is committed. The thermal build flashed
  on 7 Oct falls inside that bracket, so it is a candidate cause, not an established one. Card 1's pass also shortened, from 167.5 to
  156.8 ms between 29 Sep and 5 Nov.

## Files

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `q150_note1_checks.py` | the checks, standard library only, read-only, every input's sha256 recorded |
| `q150_note1_checks.json` | its output; sections A-C for this note, B and D for the sibling directory's note, E and F for Q150's ranking of methods |
| [`README.md.dated-note-1.sha256`](README.md.dated-note-1.sha256) | the three files above and the README (unchanged) |

From the top of the repository:

    python3 -I docs/reports/data/2026-11-06-q150-sensor-crosscheck/q150_note1_checks.py . \
        > docs/reports/data/2026-11-06-q150-sensor-crosscheck/q150_note1_checks.json

SPDX-License-Identifier: Apache-2.0
