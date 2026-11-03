# Q139(c): Q138's final critic's three desk checks, re-derived, and what they correct (post hoc, desk only)

*Tue 3 Nov 2026 (week 45), about 04:00–05:00 PST, on the Intel. Desk only: no card, no ssh to a lab host, no Modal, nothing set.
**Everything here is post hoc**: every number it reads was committed before this lane began, and none of its arms was registered.
It answers the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 1
(a large GEMM; ranks 3 and 7 of Q138's final critic) and items 9 and 8 (heat over minutes, the critic's rank 4) for check (a), and
item 6 (the power model: the card term, rank 5, and the blind scores, ranks 1–2) for checks (b) and (c). Q138's final critic ran
these three checks in its own scratch, unverified; this lane wrote its own code from the committed data and compared with the
critic's outputs only at the end. The corrections they support are in the lab records, on the kinds page and on the hubs (below).*

## Results first

**(a) A large GEMM's sustained die is predicted from its board watts.** Q138(t)'s frozen aifoundry2 chain (`model-q138t.json` a2,
frozen at `f5473428` before E146 was registered, amended at `c2f9920d` with no number changed; fitted on the kinds loop's E111 and
E133 only) was run open loop on each large-GEMM session's measured board trace. It was scored on the window die of all 56 sustained
runs: the registered reducers' last 40 s of work inside dispatch windows. Errors are measured − predicted, °C rms (mean):

| Session | Runs | Chain, rest anchor (Q138(t)'s A1.3) | Chain, first gate | Chain, each run's start | E136's frozen law, same watts |
|---|---|---|---|---|---|
| E119 | 20 | 0.72 (+0.62) | 0.45 (−0.26) | 0.49 (+0.03) | 2.95 (+2.89) |
| E126 | 22 | 0.61 (+0.53) | 0.50 (−0.39) | 0.51 (+0.04) | 0.97 (+0.86) |
| E136 | 12 | 0.46 (+0.41) | 0.49 (−0.43) | 0.46 (+0.02) | 2.16 (+2.05) |
| E146 | 2 | 0.62 (+0.62) | 0.23 (+0.21) | 0.40 (+0.27) | 2.76 (+2.74) |
| **All 56** | 56 | **0.63** (+0.54) | **0.47** (−0.33) | **0.49** (+0.04) | **2.18** (+1.91) |

- **F6, the shape never run, given the watts.** fp32 random measured 65.25 °C at 56.15 W, and the chain reads +0.55 / +0.12 / +0.56 °C
  by the three anchors. int8 full measured 61.71 °C at 45.48 W: +0.69 / +0.30 / −0.02 °C. E136's law on the same watts reads
  +3.05 / +2.43 °C (+3.10 with the registered die rounded to 65.3).
- **F6 end to end, through the prediction's power.** Fed G2's frozen sustained power (52.5 / 42.72 W) instead of the trace, the chain
  reads fp32 random **+2.0 to +3.2 °C** low and int8 full **+1.2 to +1.7 °C** low (by anchor, and by whether only in-dispatch samples or the
  whole run span carry the frozen watts). E136's law on G2's power gives +4.57 / +3.58 °C (registered: +4.62 / +3.57, R5 die FAIL ×2).
  Fed P0's 800 MHz power (57.98 / 44.71 W), the chain reads −0.40 to +0.99 °C.
- **So R5's die FAIL is E136's two-parameter law and the power it was fed, not the heat path.** G2 read F6's sustained board 3.65 / 2.76 W
  low and its clock 800 MHz where the governor held fp32 random at 745.1. For a sustained large GEMM the next gain is its sustained power
  and governed clock (the critic's rank 3, Q139(q)), not heat.
- **Checks on this file's own reader.** Its window die and watts equal every session's registered `results.json` cells to 0.05 °C and
  0.005 W, and its die_start equals theirs in 56 of 56. Its chain, on the first-gate anchor, equals Q138(t)'s own
  `heat_q138t.load_tel/grid/states` to 0.0005 °C in every window (`--frozen-check`). A trapezoid integration on the telemetry's own
  sample times moves the pooled rms by at most 0.02 °C (`chain_gemm-trap.*`).

**(b) The card term (E142's registered X1 / X2) on E141's committed reduction.** The registered scorer itself
(`score_e142.py --e141`, written to `x-registered-*` here) and this file's own reader agree:

| | Median D(card 1) / D(aifoundry3) | Bootstrap 95% | Order-statistic interval | Tiles | M7's card-1 scale | Verdict |
|---|---|---|---|---|---|---|
| X1, floats (D ≥ 5 W) | **0.9821** | [0.9796, 0.9955] | [0.9789, 0.9967] (97.3%) | 21 | 0.9711 | **FAIL** |
| X2, int8 (D ≥ 1 W) | **0.9809** | [0.9688, 1.0050] | [0.9688, 1.0050] (96.1%) | 9 | 0.9735 | **PASS** |

- **The ratio moves with the reduction footing.** Over every scorable pair of the two cards' committed reduction arms (E141's 12,
  including the six post hoc training-footing arms of its corrections C1, by E142's 7; 77 pairs, 7 not scorable), the float median runs
  **0.931–1.015** (X1 PASS in 10) and int8's 0.928–1.038 (X2 PASS in 60). Over the 31 pairs with the same rule for the meter's dips on
  both cards, the float median runs 0.953–1.015.
- **At M7's own training footing**, with the dips removed on both cards (E141 at 0.2104 / 0.2163 / 0.2217 W/°C against card 1's frozen
  0.2414), the float ratio is **0.9730–0.9744**, 0.20–0.34% over M7's 0.9711. That still FAILS X1, because the intervals are narrow
  ([0.9722, 0.9765] at 0.2104). With each card's slope fitted on its own session (E141 `nodips` × E142 `auto`) it is 0.9604, 1.1% under.
  The registered verdict is at mismatched footings: aifoundry3's session slope with the dips kept, against card 1's frozen slope with
  the dips removed. So M7's card term is about right on its own footing, and its error at 1% is set by the footing, not measured.
- No frozen number, band, prediction or verdict is changed. X1 / X2 stay as registered; this is their first scoring, post hoc and labelled.

**(c) How wide the blind power scores are** (M7 on pool 5, W). The chi-square interval is exact for an rms of zero-mean normal errors;
the percentile bootstrap over tiles assumes neither but runs short at n ≤ 9:

| Card | Set | n | rms | χ² 95% | Bootstrap 95% | Bias [t 95%] | rms about the bias |
|---|---|---|---|---|---|---|---|
| aifoundry3 (E141) | all 30 | 30 | **0.365** | [0.292, 0.488] | [0.284, 0.437] | −0.233 [−0.340, −0.126] | 0.281 |
| | fp32 priority-1 | 9 | 0.325 | [0.224, 0.594] | [0.188, 0.436] | −0.233 | 0.227 |
| | fp16 priority-1 | 8 | 0.317 | [0.214, 0.607] | [0.139, 0.447] | −0.227 | 0.221 |
| | int8 priority-1 | 7 | 0.356 | [0.235, 0.724] | [0.208, 0.476] | −0.110 | 0.338 |
| aifoundry1 card 1 (E142) | all 30 | 30 | **0.211** | [0.168, 0.282] | [0.135, 0.279] | +0.001 [−0.080, +0.081] | 0.211 |
| | fp32 priority-1 | 9 | 0.169 | [0.116, 0.308] | [0.072, 0.265] | +0.067 | 0.155 |
| | fp16 priority-1 | 8 | 0.149 | [0.101, 0.286] | [0.098, 0.192] | +0.030 | 0.146 |
| | int8 priority-1 | 7 | 0.251 | [0.166, 0.511] | [0.106, 0.390] | −0.038 | 0.248 |

- The per-format readings rest on 7–9 tiles, so their χ² intervals run from 0.66–0.69 to 1.83–2.04 times the reading. Every format's
  set of all its non-anchor tiles (12 / 9 / 9) is in `blind_rms_ci.txt`. M6 over all 30 reads 0.367 [0.293, 0.491] on aifoundry3 and
  0.211 [0.169, 0.282] on card 1, so M7 against M6 (−0.009 and −0.003 W over the 30, registered as NOT RESOLVED) sits deep inside both.
- The recomputed errors equal the committed `scored.json` `power_rows` to 1e-14 W.

## Where this differs from Q138's final critic (the data rule)

- **The rest-anchored chain reads F6 +0.55 / +0.69 °C, not +0.95 / +1.13.** This lane anchors on Q138(t)'s own definition (A1.3: the mean
  die over the last 120 s of rest before the first launch, here 46.50 °C on E146, with the smoke's heat simulated). The critic used a
  46.0 °C rest reading, and for E119 and E126 a generic 22.0 W / 46.0 °C anchor. E126 rested at 43.0 °C and 21.22 W, so the critic's rest
  arm there read 2.04 °C rms over the whole session; on its own rest it reads 0.61 °C over the sustained windows. The critic's
  first-gate figures reproduce: 0.45 / 0.50 / 0.49 / 0.23 °C against its 0.45 / 0.51 / 0.49 / 0.22, and F6 +0.12 / +0.30 against +0.11 / +0.29.
- **Through G2's power the chain reads F6 +1.2 to +3.2 °C low, not "+1.5 to +2.9"**: the range depends on the anchor and on which samples
  carry the frozen watts.
- **The card ratio's spread is wider, and its sign flips.** It is 0.931–1.015 over the 77 committed pairs, against the critic's
  0.953–0.989 over 24. "M7 about 1.1% low on card 1" holds at the registered inputs only. At M7's training footing M7 is within 0.2–0.34%,
  and on the session-fitted slopes it is 1.1% high.
- **The governed clock's second "before"**, 13.9 MHz and 2.35 W, is M7's end-to-end score from the tile's bytes on the 21 training bursts the
  governor acts on, with the cap fitted on those bursts (Q138(m) C1, `posthoc-m7.json` `aifoundry2_split`). It is not a leave-one-kind-out
  score, so the records quote it under that name.
- **The fault list has eight minor faults**, not seven: 1 major, 1 moderate, 8 minor and 1 carried privacy item.

## What it does to predicting power and heat

- **Heat, the term tested: Q138(t)'s frozen board-watts-to-die chain, carried from the kinds loop to a large GEMM** (out of sample for the
  chain's fit; post hoc for this scoring). Before, E136's frozen sustained law on the measured watts: 2.18 °C rms over 56 sustained runs
  (0.97–2.95 by session), and F6 +3.05 / +2.43 °C. After, the frozen chain on the same watts: **0.47–0.63 °C rms** (by anchor; 0.49 °C
  anchored like the law on each run's start), and **F6 within +0.7 °C**. End to end through the frozen power, F6 still reads 1.2–3.2 °C low,
  so the term to correct is a large GEMM's sustained power and governed clock (Q139(q), the critic's rank 3).
- **Power, the term tested: M7's card-1 scale.** Registered X1 FAILS at 0.982 against 0.9711, M7 about 1.1% low on card 1 at the
  registered inputs (about 0.2 W on a 20 W float kind). The ratio moves 0.931–1.015 with the reduction footing, and on M7's own footing it
  is within 0.3%. So the card term's out-of-sample error cannot be put below the footing's few percent until one footing exists (Q139(u),
  rank 1). int8's scale passes.
- **The blind scores' own uncertainty.** aifoundry3 0.365 W [0.29, 0.49], card 1 0.211 W [0.17, 0.28]; per format about 0.7 to 2 times
  the reading. A refit must beat M6 or M7 by more than about 0.05–0.1 W over 30 tiles, per card, to resolve, which is why pool 6 pairs the
  models tile by tile (Q139(b)).
- No frozen number, band, prediction or verdict changes. What changes is which term the records say is open: for a large GEMM the
  sustained power and clock, not heat; for the card term the footing, not M7's scale.

## The corrections this supports (made by this lane)

Q138's final critic listed one major fault, one moderate, eight minor and one carried. All ten that are not the carried privacy item are
corrected in the lab records (`docs/findings/05-claims.md`, `02-requests.md`), on the kinds page and on the Horace hub, each as a dated
correction that keeps what was written. The carried item (the private archive's host named in four public lab files, and in git
history) is the owner's call and is left as it stands.
1. **Major, the sustained-die miss.** R5's die FAIL stays E136's law's. Given the watts, the frozen chain reads that die to within 0.7 °C
   (post hoc), and the open part moves to the sustained power and governed clock.
2. **Moderate.** "E141 measures no float offset in M7" now reads: about half (the slope) to all (the slope and the dip rule) of the −0.23 W
   is the reduction's footing. On the dips-kept footing that 154 of M7's 247 aifoundry3 float training rows used, −0.11 to −0.13 W remains at B1's line
   (`fault_support.txt`), so an offset of about −0.1 W is neither shown nor excluded.
3. **The card term** is scored, by (b).
4. **Heat over 4.5 s.** The skill is the floats': a constant per format would err 0.37–0.55 °C on aifoundry3. int8's rises there are
   whole-degree readings of 0.667 or 1.000 °C, whose 0.117 °C spread is below M7's 0.135 °C error (on card 1 int8 does have skill,
   0.139 against 0.220).
5. **A hold's plateau** is predicted "from E78's measured watts for these kinds", not "from the planned work alone".
6. **A large GEMM's rows** carry R5's two registered FAILs: the store-energy model's burst power on fp32 random (+5.61 W) and the time per
   op on F6 (−8.9 to −9.2% against a 5% line, all three formats).
7. **The governed clock** gives both befores: in sample 7.59 MHz / 1.94 W, and M7's end-to-end 13.9 MHz / 2.35 W where the governor acts.
8. **The GPU tile** reads "a toggle model of the ET-SoC-1's form, fitted on A100 ladders and frozen".
9. **No launch's C was checked on pool 5.** Every fma launch reads `unchecked`: 2,274 on aifoundry3, 2,854 on card 1, 2,004 on aifoundry2
   (`fault_support.txt`; E78's README line 231).
10. **"E448's reads"** becomes "the 448-toggle image reads".

## Files

- `chain_gemm.py` → `chain_gemm.json`, `chain_gemm.txt` (check (a); `--frozen-check` needs numpy for Q138(t)'s own code, the rest is
  standard library); `chain_gemm-trap.*` (the trapezoid sensitivity, `--mode trap`).
- `xterm_check.py` → `xterm_check.json`, `xterm_check.txt` (check (b), all pairs); `x-registered-scored.json`, `x-registered-results.md`,
  `x-registered-score.log`: the registered `tools/claims-v3/e142/score_e142.py --e142 e142.json --runs runs.csv --e141 e141.json`, run into
  this folder; its 12 other verdicts equal the committed `scored.json`.
- `blind_rms_ci.py` → `blind_rms_ci.json`, `blind_rms_ci.txt` (check (c)).
- `fault_support.py` → `fault_support.txt`: the committed numbers behind corrections 2, 4, 6, 7 and 9.
- Reproduce from the repository root: `python3 docs/reports/data/2026-11-03-q139c-critic-checks/<script>.py --json … --txt …`.

## Published (Tue 3 Nov 2026, 04:2x–04:3x PST)

- This folder and the records' corrections: lab `22f8d1f9` (04:20:57 PST).
- The kinds page, [Multiplying different numbers](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers): `2ed9794277c1`
  (04:24:30 PST) over `8ec9ead107aa`, public and unlisted. Read back signed out: `<main>` identical to the deploy copy, 32 of 32 phrase
  checks, Chrome at 390 and 1280 px in light and dark with no sideways scroll and no errors (the before/after table now 18 rows).
- The [Horace Hub](https://spacesheep.dev/@yaroslavvb/horace-hub): `2abafc9e57ca` (04:31:15 PST) over `cb5b58d682b7`, public and
  unlisted: a new Fix entry at the top of week 45 (no older Log entry touched), Status (Q138's paragraph, section 11 re-quoted from the
  corrected page, the verification bullet), Levels stop 3 and the Library line. The AI Foundry hub (private) carried one faulty
  sentence, E144's row, and has its own Fix entry. Read back signed out: `<main>` identical to the deploy copy, public-text counts unchanged.
- Not changed: the carried privacy item (the owner's call), and the projects tracker, whose Horace row carries no fault from the list.
