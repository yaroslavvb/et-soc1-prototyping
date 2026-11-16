# MM1-v0: the lab's matmul model, as frozen (Mon 16 Nov 2026)

MM1-v0 predicts a matmul's clock cycles, seconds, joules over idle and transistor switches on the ET-SoC-1 cards from the
matrix size, the format, the data kind and the card. It was built by the round's matmul lanes (Horace round Q198) and frozen
before any datum of E206, the lab's matmul sweep, so **E206's arm A is its first blind test**. This folder holds the model
exactly as frozen: the predictor, its parameters, every input file it reads (vendored), and its forecasts for E206's 119
points. Desk only: this commit measured nothing, and nothing in the folder is E206 data.

The owner's words that started it (Mon 16 Nov 2026, at or before 09:48:24 PST; a voice transcription, where "matte mold" is
the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy
and number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which
operations are contained. See check how well the timing simulation for the matte mold matches reality and the energy."

**Labels.** *Measured*: a card's committed reading. *Desk*: arithmetic or a fit made at a desk. *Post hoc*: fitted after its
data existed (every constant of MM1-v0 is). *Held out*: left out of that fit (one experiment or one card at a time); held out
is not blind. *Blind*: scored on data that did not exist when the model was frozen. A check not run is NOT RUN.

## 1. The freeze line

Posted before any E206 datum, as post #1.16 in the owner's private coordination thread, at **13:04:57 PST Mon 16 Nov 2026**:

| file | sha256 | in this folder |
|---|---|---|
| `mm1_v0_e206.csv` (the forecasts) | `5759fb7b34fd21101930e4b128931effbf03d839cd5350d2bfbc490a64d90733` | byte for byte |
| `mm1_v0.py` (the predictor) | `ab2e43b53d066873334b5663f9c7a926eb75dc879b69eb4e8a91f525970d83c2` | its path lines changed (section 8); here `7dabaeac53c67ed52815aa7e11d356e550058085f6f5a83469be38430d5f7971` |
| `mm1_v0_params.json` (the parameters) | `370f780cceada134aa3451ed46f5d8cc22a520665e92caf1d92ae532dfc8cde6` | byte for byte |

- The frozen predictor read its inputs from scratch folders on the lab box. The file itself names those folders, so it is not
  committed. The committed `mm1_v0.py` reads the same inputs, vendored in `inputs/`. Section 8 lists every changed line.
- **The committed predictor computes what the frozen one computed.** Re-run on aifoundry2 at 13:21 PST Mon 16 Nov 2026, and
  again just before this commit, it reproduced all four outputs byte for byte: the forecasts, the parameters, the forecasts' JSON twin and the blind-day planning
  file. The run used `/usr/bin/python3` 3.12.3 with numpy 1.26.4, run `-I -B`, the interpreter the frozen outputs were written
  with.
- **Nothing in this folder is E206 data.**
  - No E206 datum existed at the freeze. GitHub main was then `ec9c9fe8`, which holds no E206 commit at all, not even E206's
    registration.
  - Every file here but this README and `SHA256SUMS` comes from a file written before the freeze: the outputs at
    12:05:56 PST, the inputs between 10:07 and 12:03 PST. All are byte for byte copies except `mm1_v0.py` and
    `inputs/linemap.py`, which carry the changes listed in sections 7 and 8.
  - The point list in `inputs/points.csv` is E206's design: its points, plus planning columns made at the desk.
  - Every measured row behind the model comes from 11 earlier experiments, E105 to E190, whose data folders are dated 1 to
    13 Nov 2026.

## 2. What MM1-v0 predicts, and from what

**Inputs.**
- A grid point of the lab's GEMM kernel, rgm136 (`tools/claims-v3/e136/rgm136/`), as `gemmL<MB>x<NB>x<KB>`:
  - M = 1,024·MB, N = 512·NB, K = 512·KB·w, with w = 1 / 2 / 4 for fp32 / fp16 / int8.
  - Each minion does 64·MB·NB·KB ops a GEMM.
- Or one of the calibrating arms of `run_gemm`: gemmc1, c4s, c8s, c16, c16s or c8. The energy refit also reads c16r\<R\>
  points.
- The format: fp32, fp16 or int8.
- The data kind. Energy is forecast for zeros and random only.
- The shire mask (32 minions a shire).
- The card, its clock f and its voltage V. E206's arm A: aifoundry3 card 0 at its pinned 600 MHz, 0.522 V.

**Outputs.** One row a point in `mm1_v0_e206.csv`:
- cycles an op, two ways:
  - the wall basis, the slowest minion;
  - the counter's mean over minions, which is the wall cycles / ρ;
- ρ, and the compute floor;
- seconds a GEMM;
- W over idle, and J over idle a GEMM;
- lines a shire-op by the place that serves them (L2, L3, fresh from DRAM), and the footprint in MB;
- the timing simulation's instruction count a minion a GEMM;
- a note.

The predictor's `predict()` also returns transistor switches (section 5). The E206 file carries no switch column.

**Time** (per-op maximum over op classes):
- `T_op = Σ P(a, b) · max(Tc(fmt, f), kA·τ(a, f), τ(b, f))`, the sum over the places a (A's tile) and b (B's tile) in
  {L2, L3, F}.
- τ, the time of one operand's tile stream in µs (f in MHz): τ(L2) = 0, τ(L3) = c3/f + m3, τ(F) = cF/f + mF.
- `Tc = max(c1/f + m1, floor/f)`. This is E119's law:
  - fp32 and fp16: 527.48/f + 0.0176 µs;
  - int8: 283.03/f + 0.0146 µs;
  - floor: 529 / 270 cycles.
- P(a, b) comes from rgm136's walk, through four parts:
  - closed-form LRU stack distances (`inputs/linemap.py`);
  - the lab's desk L2 model for KB ≤ 2 (`inputs/l2_lab.json`);
  - a logistic L3 retention, r(d) = 1/(1 + exp((d − x50)/s));
  - a stride rule: the far B group's retention × 0.15 when MB = 1, NB ∈ {4, 8}, KB ≥ 4 and the footprint is over 32 MB.
- The constants are c3 446.49, m3 0.812 µs, cF 219.50, mF 2.359 µs, kA 0.840, x50 50.72 MB and s 8.75 MB.
  - They were fitted on 769 GEMM points (`inputs/harness_time-MAXAB_M3-RSW_M3.json`).
- ρ by regime:
  - 1.006 when every line comes from the L2;
  - 1.126 for gemmL inside 32 MB, and 1.011 past it;
  - 1.143 for c4s and c8s, and 1.001 for c16, c16s and c8.
- Seconds a GEMM = ops a minion × T_op. v0 adds no launch time.

**Energy:**
- `W over idle = P_aw(card)·n/1,024 + g·[B(f) − B(600)] + rate·s_V·[e_res(card, fmt, kind) + Σ_l n_l/32·(b_l + d_l·φ)]`.
- rate = n / T_op, where n is the active minions.
- s_V = (V / 0.517 V)².
- φ = 0 for zeros and 1 for random.
- n_l is the lines a shire-op that place l serves.
- e_res is ledger v2's frozen resident price of an op (`inputs/tables.json`). It is not refitted.
- The rest is refitted by least squares on 682 GEMM points (`inputs/gemm_table.json`) each time the predictor runs. The fit is
  deterministic, and its result is `mm1_v0_params.json`'s `theta`:
  - P_aw: aifoundry3 card 0 1.390 W, aifoundry2 card 0 2.026 W, aifoundry1 card 1 3.660 W, each at 1,024 minions;
  - g: 0.817;
  - b and d for each place: L2 49.4 and 496.7, L3 244.5 and 962.6, fresh 890.6 and 1,339.0 pJ a line a shire-op;
  - in sample: 4.91% rms.
- On a pinned card the governed term is zero.
- J over idle a GEMM = W over idle × seconds a GEMM.
- v0 has no leakage term, no launch term and no contention term.
- J with the card at rest is not in the file. It takes the run's measured rest.

## 3. Scope

- **The lab's rgm136 GEMM on its grid, and the run_gemm arms. Nothing else.** An off-grid size must be padded to the next
  grid point. mm-critic's scope finding:
  - "from the sizes and operations" holds for rgm136 on its grid only;
  - the stack-distance groups are a hand derivation of rgm136's loop order;
  - the arms' classes are assigned by name;
  - the stride rule's × 0.15 was read from four rungs (E158, E169);
  - the shire mask never enters the map (section 6);
  - C's stores and any epilogue are not priced.
  - Another kernel needs its own map. Today's route, a counted simulator run, gives instructions and bytes, never the level
    that served a line.
- **The cards.** v0 covers aifoundry3 card 0, aifoundry2 card 0 and aifoundry1 card 1. Card 1's awake power comes from 18 points
  of one shape. The awake power does not carry across cards (section 4), so each card needs its own GEMM anchor.
- **The forecasts.** `mm1_v0_e206.csv` covers E206's arm A only: aifoundry3 card 0, 600 MHz.
  - Its 119 points by family: star 28, K ladder 15, square 14, extreme 13, zeros 14, subset 16, kinds 10, anchor 9.
  - 109 carry energy. The 10 others (6 real, 4 sparse50) have no frozen resident price for their kind.
  - Arm B, on aifoundry1 card 1, is not forecast.
- `blind_day_plan.csv` is v0's planning output for the blind matmul day's 54 candidate points. It is **planning only**. It is not
  a forecast of record: the day is forecast by MM1-v1, frozen before it.

## 4. How well, on the lab's existing data: desk, post hoc model selection

The figures below are post hoc model selection. Every constant was fitted after its data existed, and MM1-v0's form and map were
chosen after 16 form × map combinations had been scored on these same folds. They are held out by experiment (LOEO) or card
(LOCO), and **never blind**. They are mm-synth's and mm-critic's desk numbers, reported here, not re-run by this commit.

| what | points | MM1-v0, held out |
|---|---:|---|
| cycles an op (wall), LOEO | 769 | **5.54% rms** (bias +0.36%) |
| ... the gemmL shapes | 363 | 6.75% (−0.72%) |
| ... the calibrating arms | 406 | 4.16% |
| ... E190's 8,192³ cells, E190 left out | 36 | −7.1% to +4.5% by cell |
| cycles, LOCO: aifoundry3 / card 1 | 266 / 18 | 3.9% / 5.4% |
| cycles, LOCO: aifoundry2 (unidentified; see 2 below) | 485 | 11.8% from a warm start, **18.4% from a cold start** |
| W over idle given the measured seconds, LOEO | 682 | **6.35%** |
| J over idle with seconds forecast, LOEO | 682 | 7.89%; **7.93% with the retention refitted in each fold** |
| J with the card at rest, given / forecast seconds | 682 | 2.05% / 5.80% (5.82% refitted) |
| W over idle, LOCO: aifoundry3 / card 1 | 203 / 18 | 30.1% (+24.5%) / 16.5% (−14.6%): the awake power does not carry |
| transistor switches | 0 | not scorable: no switch count is measured anywhere |

**mm-critic's rewording of three claims** (its findings F10 and question 2):
1. **"Every constant refitted in each fold" holds for time, not for energy.**
   - In time, c3, m3, cF, mF, kA and the retention are refitted in each fold. Cold-started folds reproduce the held-out numbers
     exactly (5.54 / 6.75 / 4.16%). The c1 law, the stride rule and ρ are fixed; they are in sample (below).
   - The energy folds kept the L3 retention fitted on all the data. Refitting it in each fold leaves W over idle given seconds at
     6.35%, and moves J over idle with seconds forecast from 7.89% to 7.93%.
2. **LOCO aifoundry2's 11.8% depends on the warm start.** From a cold start it reads 18.4%, so both are given. The fold is not a
   card test anyway. aifoundry2 is the only card with more than one clock (its governor), so holding it out leaves only 600 MHz
   data, and the clock split of every stream goes unidentified.
3. **The headline is post hoc model selection.** MAXAB on map M3 was picked among 16 form × map combinations on the same folds,
   so its held-out error is not an unbiased estimate of a new point's error. The blind tests are E206 for v0 and the blind matmul
   day for MM1-v1.

**Also in sample.** These are named by mm-synth and confirmed by mm-critic:
- the c1 law is E119's own fit;
- the stride rule was read from E158's and E169's rungs;
- ρ is the scorecard's median over all points.

## 5. Transistor switches: the definition and its public constants

**The definition.** One transistor switch is one transistor gate, one fin, charged or discharged by a net transition: a "fin
edge". `predict()` returns the count in two parts. Both are voltage-free.
- **Counted, the tensor unit:** `N_op × MACs an op × fin edges a MAC (format, kind)`, low to high. The fin edges a MAC are in
  `inputs/switch_table.json`:

| format and kind | fin edges a MAC (zero delay to timed) | how it was counted |
|---|---|---|
| fp32 random | 71,092 to 107,508 | the fp32 unit at gate level (the public RTL through an open flow); the rest of the vector unit by RTL toggles × the fp32 gate/RTL ratio (an assumption) |
| fp32 zeros | 4,559 to 4,827 | the same |
| fp16 random | 30,238 to 45,411 | RTL toggles × the fp32 gate/RTL ratio (an assumption: no fp16 gate-level run) |
| fp16 zeros | 2,280 to 2,414 | the same |
| int8 full (random) | 1,927 to 2,783 | the vector unit around the arithmetic only: **the int8 arithmetic is missing** (behavioural RTL, no nets in the multiply, product sum and add) |
| int8 zeros | 469 to 490 | the same |

- **Estimated, every class with no public netlist:** `(J over idle − N_op·s_V·e_res) / s_V × κ`. The classes are the awake clock
  tree, the memory path, issue, any epilogue and the governed base.
  - κ is the fin edges a joule at 0.517 V. It has three values:
    - low 1.23·10¹⁶: 71,000 / 5.783 pJ;
    - central 1.87·10¹⁶: 108,000 / 5.783 pJ;
    - high 4.86·10¹⁶: 14.5 fins / 0.2985 fJ.
  - The spec's charge-route ceiling, J over idle / (s_V × 8.94 aJ), is not computed by v0's code.

**Its public constants.** Every one is in the lab's public files: `docs/reports/data/2026-10-27-transistor-ledger/README.md`,
`docs/reports/data/2026-10-27-q129-glitch/` and the findings. They come from the lab's open-netlist chain (the open stand-in
library, the public RTL's fp32 multiply-add unit through an open flow, and SPICE at 0.517 V and 25 °C).
- **Fins a toggle:** 14.5 on a signal net, 39.8 on a clock net.
- **One fin's rise:** 8.94 aJ, 108 electrons; C_gg 0.0335 fF.
- **A net toggle:** 0.2985 fJ (2.233 fF) on a signal net, 1.0416 fJ (7.794 fF) on a clock net.
- **A random fp32 multiply-add:** 4,132.5 gate-level toggles at zero delay and 6,494.8 timed (× 1.572).
- **The board's price:** 5.783 pJ a random fp32 multiply-add (E38's registered figure).

**What the count is not.** These are mm-critic's scope caveats (its finding F3). They apply to v0 as frozen.
- **The estimated part counts energy that switches nothing.**
  - In-run leakage is 7-21% of the estimated class, by the spec's own leakage slope (mm-critic's desk check).
  - On a governed card, the governed base is 43% of the class at 800 MHz, and part of its rise with voltage is leakage.
  - J over idle is the board's reading, so the part also includes the DRAM devices and the regulators' delivery loss. The rail
    ledger's 0.875 pJ row of the 5.783 pJ a MAC is "the regulators' delivery loss plus logic in step with the rails".
  - All of it is scaled as if it were fin edges. A die-only count would subtract it or report it apart.
- **The int8 arithmetic is in neither part.** It is subtracted with e_res, but the counted table has no int8 arithmetic nets.
  The int8 resident op × κ is 2-3 times the counted int8 part.
- **It is not scorable.** Nothing on a card measures switches. The only check is the energy closure, between the open flow's
  bottom-up figure and the board's 5.78 pJ a random fp32 multiply-add.

## 6. The known fault: shire subsets are mapped at the full chip's footprint

This is mm-critic's major finding. It was recorded before any E206 datum.
- **What v0 does.** MM1-v0 gives every shire mask of a shape the same lines and the same cycles.
  - E206's gemmL4x8x4 reads 1,244.42 cycles an op (wall) at all six of its masks. The masks are 0x1, 0xf, 0xff, 0x11111111, 0xffff
    and 0xffffffff, rows p094-p105 of `mm1_v0_e206.csv`.
  - Each of those rows has the same lines a shire-op: 0 from the L2, 133.14 from the L3 and 58.86 fresh. Each has the same 128 MB
    footprint.
  - gemmL1x1x1 likewise reads the same at both of its masks (p106-p109).
- **Why that is wrong.** A shire subset runs each minion's full-chip work, so the GEMM it computes is smaller. Its footprint, and
  with it the L3's retention, is smaller too.
  - A mask-aware line map (the lab's E136 line model with a subset function) moves 0x1 to 192 L3 lines and 0 fresh, and 0x11111111
    to 184 and 8. This is mm-critic's desk reading.
- **What this means for E206.** The 16 points of E206's subset family (14 at a shire subset and the ladder's two full-chip ends)
  stay as frozen. This is their named cause.
  - The rows' own note says "v0 has no contention term". That is a second, separate gap.
- **For v1.** v1 gives the map the mask, tied to the lab's subset line counts, before fitting any contention term. A contention
  term fitted on E206's subset ladder without it would absorb the footprint effect and be mis-identified.

**Other gaps, stated before any E206 datum:**
- no contention term;
- no energy for the 10 real and sparse50 points;
- arm B not forecast;
- no launch, leakage or epilogue term.

mm-critic also relabels the 529 / 270-cycle floor. "The RTL floor with B through TenB" is a closed form read from the card's
TenB loop (measured, E101; a post hoc closed form). The RTL bench's own reach is resident B, at 546 / 318 cycles, exact.

## 7. The files

| file | what | source in the round's lane folders (not public) |
|---|---|---|
| `mm1_v0.py` | the predictor (vendored; section 8) | `orch/frozen-mm1-v0/mm1_v0.py` = `mm-synth/scripts/mm1_v0.py`, sha256 `ab2e43b5...` |
| `mm1_v0_params.json` | its parameters: the form, every constant, the held-out summaries | frozen, byte for byte |
| `mm1_v0_e206.csv` | **the forecasts for E206's 119 points** (arm A) | frozen, byte for byte |
| `mm1_v0_e206.json` | the same rows as JSON, with the interpreter's version | frozen, byte for byte (sha256 `8b39287e...`) |
| `blind_day_plan.csv` | v0's planning numbers for the blind day's 54 candidate points (planning only) | frozen, byte for byte (sha256 `0d14b52f...`) |
| `inputs/linemap.py` | design B's closed-form line map (`groups()`) | `mm-design-b/scripts/linemap.py`, sha256 `3e89d32530d90d8d4b1154478b968b81c4d4e294756c607fd18c147e7799d6b3`; this copy cuts its unused self-check block, and every line before it is byte for byte |
| `inputs/harness_time-MAXAB_M3-RSW_M3.json` | the time harness's fit: c3, m3, cF, mF, kA, the retention and the held-out summaries | `mm-synth/work/`, byte for byte |
| `inputs/l2_lab.json` | the lab's desk L2 model's hits by operand (KB ≤ 2 shapes) | `mm-synth/work/`, byte for byte |
| `inputs/inventory.json` | the GEMM shapes measured, and E206's design | `mm-synth/work/`, byte for byte |
| `inputs/gemm_table.json` | 769 measured GEMM points with their lines, resident price and governed base: the energy refit's data | `mm-design-c/work/`, byte for byte |
| `inputs/switch_table.json` | fin edges a MAC by format and kind | `mm-design-c/work/`, byte for byte |
| `inputs/tables.json` | ledger v2's resident prices (e_res) and other desk tables | `mm-models/work/`, byte for byte |
| `inputs/points.csv` | E206's point list (its design) | `sweep-design/work/`, byte for byte |
| `SHA256SUMS` | every file of this folder but itself | |

## 8. What changed from the frozen predictor (the complete list)

`mm1_v0.py` is the frozen file (sha256 `ab2e43b5...`) with 19 counted replacements, each found exactly once, and a six-line
header. Nothing else changed:
- **The scratch folder's path (two lines) is replaced.** `HERE` is now this file's folder, `IN` is `HERE/inputs`, and `--out
  <folder>` names where the outputs go. The script refuses this folder as `--out`.
- **`os` is imported.**
- **Two comment lines** name the new paths.
- **Each of the eight input reads** now opens `IN/<name>`.
- **Each of the five writes, and the output hashes,** now use the `--out` folder.
- **`mm1_v0.sha256`'s fifth line** is the hash of the script that ran, `mm1_v0.py`. The frozen file's fifth line was
  `../scripts/mm1_v0.py`. The first four lines, the outputs' hashes, are unchanged.

## 9. Reproduce

From the repository's top, into any empty folder:

```
/usr/bin/python3 -I -B tools/matmul/mm1/v0/mm1_v0.py --out /tmp/mm1v0
for f in mm1_v0_e206.csv mm1_v0_params.json mm1_v0_e206.json blind_day_plan.csv; do cmp /tmp/mm1v0/$f tools/matmul/mm1/v0/$f && echo "SAME $f"; done
(cd tools/matmul/mm1/v0 && sha256sum -c SHA256SUMS)
```

It needs Python 3 and numpy. All four outputs were reproduced byte for byte under `/usr/bin/python3` 3.12.3 with numpy 1.26.4 on
aifoundry2 (Ubuntu 24.04). Another numpy or BLAS may move the last digits of the energy refit.

SPDX-License-Identifier: Apache-2.0
