# The gemmLnc term: why MM1-v3.1 underprices rgm136's non-cooperative loads, the price, and E215's frozen forecasts

*Thu 19 Nov 2026, Pacific time. Round Q225, lane lnc-energy (track B). Desk only: no card was used. Interpreter `/usr/bin/python3` 3.12.3,
numpy 1.26.4. Every fit here is **post hoc**: the 9 points existed before it. The rail split is **measured**, read post hoc from committed
telemetry. The walk numbers are **desk**: exact streams, with no fitted constant. The forecasts for E215 are **frozen before any E215 datum**,
so they are blind for E215.*

## The answer in five lines

1. **What the branch changes.** rgm136's gemmLnc runs gemmL's loop with every TensorLoad non-cooperative. Each shire then issues 32 A and
   32 B tile reads an op step (1,024 lines) where gemmL issues 4 and 8 (192 lines). That is **832 duplicate line reads a shire-op**
   (26 a minion-op). The chip's distinct-tile stream, and so the walk's L3 and DRAM lines, are the same for both kernels.
2. **Where the energy goes (measured, by rail).** Against its gemmL twin, gemmLnc's extra W over idle is on the **SRAM rail** at every point
   (+2.2 to +8.3 W; 3.6-7.0 nJ a minion-op). It is on the **NoC rail** at the shapes with NB ≤ 3 that are served beyond the L2 (+1.9 to
   +4.5 W; 3.2-6.4 nJ a minion-op). The NoC part almost vanishes at NB 5-6 (+0.5 W) and at the L2-resident 1x1x1 (+0.3 W). The minion rail
   carries little: under 0.15 of the board excess at 7 of 9 points.
3. **The cause.** Every duplicate is an extra L2 read. In addition, at some shapes the duplicates of lines from beyond the L2 are fetched
   again over the NoC instead of merging in the L2. The walk's desk L2 model has no time, so it counts every duplicate as an L2 hit. The NoC
   rail shows this is not so on the card. Ruled out: the instruction census (fewer instructions, the wrong sign), the op time, the FMA and
   core logic, and more chip-level L3 or DRAM lines.
4. **The term (form F3, two constants).** It adds **254.4 pJ for each duplicate L2 read**, plus **552.1 pJ for each duplicate of a
   beyond-L2 line on the A panel's first C block** (one in NB). The NB dependence is described here, not derived.
   - In sample: W over idle rms **7.99%**, against MM1-v3.1's **32.56%** (mean -30.7%).
   - Held out: leave one point out 9.81%, leave one run out 9.63%, E211 out 10.05%, E213 arm A out 12.82%, card 1 out 9.86%.
   - On E213's two gemmLnc smokes, never fitted: -2.1% and -6.3% (MM1-v3.1: -29.4% and -31.9%).
   - The term is identically 0 on every cooperative loop.
5. **E215's frozen forecasts** (`forecasts-gemmlnc-e215.csv`, sha256 `00fcaf5d...`):
   - a024 23.53 W, a026 23.57 W, a031 25.90 W and a032 25.75 W on aifoundry3. b013 25.04 W on card 1.
   - Planning peaks are 50.3-58.8 W, 13-20 W under the stops: **no registered point comes within 3 W**.
   - **Safety flag, a smoke rather than a point.** Arm B's gemmLnc smoke s14 (gemmLnc2x2x2, now right before the gemmLnc block) has a
     planning peak of 68.56 W with the term. That is 3.44 W under the 72 W x3 stop, and 2.46 W under it by form F2. E213's measured s14 on
     the rest law gives 70.42 W, 1.58 W under.

## 1. The data: every committed gemmLnc energy point and its twins

These are 9 points, one a configuration (12 runs). Their W over idle comes from MM1-v3.1's own records
(`tools/matmul/mm1/v3.1/out/points_energy_v31.csv`, landed 2c971828, sha256 `7c73966c...`). The op times come from `points_time_v31.csv`
(sha256 `d5faf0b1...`), and MM1-v3.1's in-sample W is given the measured op time. The runs:

- E211 (aifoundry3 card 0, data 38aaf004): c01c, c02c.
- E213 arm A (aifoundry3 card 0, c69a12aa): a075, a079, a082, a086, a087.
- E213 arm B (aifoundry1 card 1, b0c727c5): k37, k40.

E213 arm B's k38 and k39 never ran (the board stop at run 079): NO DATA. **E212 and E214 hold no gemmLnc arm.** E214's registration names
gemmLnc only in its never-run scan's list of earlier configurations (E211's and E213's), and **no E214 data file was read** by this lane.
Nothing of E215 was read but its registration's point list (`tools/claims-v3/e215/points-e215.csv`, the tokens) and MM1-v3.1's frozen E215
forecasts.

### Table 1. The 9 committed gemmLnc points and their rgm136 gemmL twins

Measured, with MM1-v3.1 in sample, given the measured op time.

| point | shape, format, card | measured W over idle: gemmLnc / twin | MM1-v3.1: gemmLnc / twin | measured / MM1-v3.1: gemmLnc / twin | wall cycles an op: gemmLnc / twin | excess over MM1-v3.1, nJ a minion-op |
|---|---|---|---|---|---|---|
| c01c (w01m) | gemmLnc2x3x2 fp32, aifoundry3 card 0 | 36.09 / 25.07 | 24.95 / 24.23 | 1.446 / 1.034 | 876.6 / 904.7 | 15.89 |
| c02c (w06m) | gemmLnc3x5x7 fp32, aifoundry3 card 0 | 25.15 / 19.14 | 22.22 / 19.65 | 1.132 / 0.974 | 1030.5 / 1173.6 | 4.91 |
| a087 (a088) | gemmLnc1x1x1 int8, aifoundry3 card 0 | 26.27 / 14.65 | 16.05 / 14.88 | 1.637 / 0.985 | 358.7 / 389.8 | 5.97 |
| a086 (a083) | gemmLnc1x1x44 fp32, aifoundry3 card 0 | 21.72 / 14.58 | 14.78 / 15.00 | 1.470 / 0.972 | 1666.7 / 1633.8 | 18.83 |
| a079 (a076) | gemmLnc1x6x5 fp32, aifoundry3 card 0 | 26.23 / 20.14 | 22.78 / 20.60 | 1.151 / 0.978 | 982.5 / 1092.6 | 5.51 |
| a075 (a006) | gemmLnc3x1x3 fp32, aifoundry3 card 0 | 39.18 / 24.77 | 24.70 / 23.93 | 1.586 / 1.035 | 880.3 / 910.6 | 20.75 |
| a082 (a030) | gemmLnc4x1x6 fp32, aifoundry3 card 0 | 23.08 / 15.97 | 16.77 / 16.31 | 1.376 / 0.979 | 1375.9 / 1416.0 | 14.12 |
| k40 (k41) | gemmLnc1x1x1 int8, aifoundry1 card 1 | 29.31 / 15.15 | 16.28 / 15.02 | 1.801 / 1.009 | 358.8 / 389.8 | 7.61 |
| k37 (k06) | gemmLnc3x1x3 fp32, aifoundry1 card 1 | 41.96 / 24.93 | 24.90 / 24.11 | 1.685 / 1.034 | 880.2 / 910.3 | 24.44 |

What the table shows:

- MM1-v3.1 prices gemmLnc at about its twins. Its census charges gemmLnc **-39.64 pJ a minion-op** for the two tensor_coop issue slots it
  drops (`census-v3.1.json`: gemmL 46, gemmLnc 39 instructions an op). At these rates that is about -0.03 W.
- MM1-v3.1's chosen energy form (E1t) prices an L2 line at 0 (b2 = d2 = 0), so nothing in it can see a duplicate L2 read.
- gemmLnc runs 3-8% faster than gemmL at NB ≤ 3, 10-12% faster at NB 5-6, and 2% slower at 1x1x44.
- The per-op excess varies about 4x across shapes (4.9-24.4 nJ a minion-op).

## 2. The mechanism

**From the kernels' sources** (`tools/claims-v3/e136/rgm136/kernel/sparsity.c`, `run_gemm_large`):

- In gemmL, a TensorLoad with the cooperative bit (62) and a `tensor_coop` group serves all the minions of the group with one read. A is
  shared by the 8 minions of a neighbourhood, and B by the 4 minions at one position across the shire's 4 neighbourhoods.
- gemmLnc issues the same two loads with no cooperation: every minion reads its own 16 lines for A and for B.
- Each minion does the same 64 MB NB KB ops in the same order in both kernels. The only other change is the two `csrw tensor_coop` issue
  slots an op, which the census prices.

**From the masked walk** (`../../v3.1/walk/walk/walk_v31.py`, landed 5a75e212, sha256 `87736da2...`; Table 3, `s03_walk.py`):

- At every shape a shire-op reads 192 lines (gemmL) or 1,024 (gemmLnc): **832 duplicates**, 448 of A and 384 of B.
- The chip's stream of distinct tiles is identical for both kernels: `chip_steps` reads no coop flag, and both kernels hash equal at the
  four small shapes (2x3x2, 1x1x1, 3x1x3, 2x2x2). So the walk's L3 and DRAM line counts and its sharing are the same.
- The lab's desk L2 model (2,048 sets x 4 ways, the shire's own line stream, second pass) has **every duplicate hit the L2** (share 1.000 at
  all 13 shapes). By that model the duplicates add L2 reads only.

### Table 3. The walk (desk, exact streams; full mask): what the branch changes a shire-op

| shape | what | footprint MB | reads a shire-op, gemmL / gemmLnc (lines) | duplicates (lines) | desk L2 hits, gemmL / gemmLnc (lines) | duplicates hitting the desk L2 | chip L3 strict 32 MB, A / B in-L3 share (both kernels) |
|---|---|---|---|---|---|---|---|
| 2x3x2 | E211 c01c | 26 | 192 / 1,024 | 832 (A 448, B 384) | 16 / 848 | 1.000 | 1.000 / 1.000 |
| 3x5x7 | E211 c02c | 107 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.800 / 0.500 |
| 1x1x1 | E213 a087/k40 | 5 | 192 / 1,024 | 832 (A 448, B 384) | 192 / 1024 | 1.000 | 1.000 / 1.000 |
| 1x1x44 | E213 a086 | 134 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.000 / 0.000 |
| 1x6x5 | E213 a079 | 52 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 1.000 / 0.500 |
| 3x1x3 | E213 a075/k37 | 27 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 1.000 / 1.000 |
| 4x1x6 | E213 a082 | 62 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.000 / 1.000 |
| 2x2x2 | E213/E215 smoke s03/s14 | 20 | 192 / 1,024 | 832 (A 448, B 384) | 16 / 848 | 1.000 | 1.000 / 1.000 |
| 1x15x3 | E215 a024 (shape only) | 81 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 1.000 / 0.500 |
| 1x12x4 | E215 a026 (shape only) | 80 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 1.000 / 0.500 |
| 8x1x5 | E215 a031 (shape only) | 101 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.000 / 1.000 |
| 5x1x10 | E215 a032 (shape only) | 120 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.000 / 1.000 |
| 2x1x37 | E215 b013 (shape only) | 189 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.000 / 0.000 |

**From the card's rails** (measured, post hoc; `s02_rails.py`):

- The source is the committed sessions' 10 Hz telemetry: `sp.minion_w`, `sp.sram_w` and `sp.noc_w`, each sample's mean, beside `board_w`.
- The windows are the reducers' own: work is the samples inside a counted launch (each experiment's own `host_records` and `counted`), and
  rest is the 5 s before the run's first process. Each run takes the median, and each point the mean over its runs.

### Table 2. Where the excess goes: W over idle by rail, gemmLnc minus its twin

The per-op columns take each kernel at its own op rate.

| point | shape | board | minion rail | SRAM rail | NoC rail | NoC rail, nJ a minion-op | SRAM rail, nJ a minion-op |
|---|---|---|---|---|---|---|---|
| c01c | 2x3x2 | +11.03 | +0.53 | +3.75 | +2.28 | +3.15 | +5.23 |
| c02c | 3x5x7 | +6.01 | +1.77 | +2.42 | +0.56 | +0.50 | +3.57 |
| a087 | 1x1x1 | +11.61 | +1.53 | +8.25 | +0.29 | +0.14 | +4.65 |
| a086 | 1x1x44 | +7.14 | -0.15 | +2.24 | +1.88 | +5.18 | +6.17 |
| a079 | 1x6x5 | +6.08 | +1.51 | +2.51 | +0.53 | +0.49 | +3.61 |
| a075 | 3x1x3 | +14.41 | +0.76 | +4.97 | +3.80 | +5.33 | +6.99 |
| a082 | 4x1x6 | +7.11 | +0.35 | +2.70 | +2.04 | +4.47 | +5.93 |
| k40 | 1x1x1 | +14.16 | +1.63 | +6.55 | +0.38 | +0.18 | +3.69 |
| k37 | 3x1x3 | +17.03 | +0.84 | +3.96 | +4.53 | +6.37 | +5.58 |

The three rails carry 0.55-0.87 of the board's excess; the rest lies outside them (other rails and conversion). Reading the tables
together:

- **The duplicate L2 reads** show on the SRAM rail at every shape, at a roughly constant 3.6-7.0 nJ a minion-op. That is 140-270 pJ a
  duplicate line on the rail.
- **The re-fetch over the NoC** shows at the beyond-L2 shapes with NB ≤ 3 (3x1x3, 4x1x6, 1x1x44, 2x3x2): +3.2 to +6.4 nJ a minion-op on the
  NoC rail. gemmLnc's NoC-rail energy an op is then 2.0-2.7x its twin's (the twins spend 3.1-3.9 nJ a minion-op on their 6 beyond-L2
  lines). So the duplicates of lines in flight from the L3 or DRAM are not merged, at least in part. The walk's desk L2 model, with no time,
  cannot show this.
- **At NB 5-6** (1x6x5, 3x5x7) the NoC part nearly vanishes (+0.5 nJ), and gemmLnc runs 10-12% faster than gemmL there. That reads as the
  early minion's fetch filling the L2 for the late ones: the duplicates hit, and nothing waits for the group.
- **At the L2-resident 1x1x1** there is nothing to re-fetch (+0.15 nJ).
- The walk's chip view gives a second description of the same split. The two low-NoC shapes are the only ones whose B tiles alternate
  between fresh and L3 within a C block (B in-L3 share 0.5), and E215's a024 and a026 share that signature. Either description puts a024
  and a026 with the low group and a031, a032 and b013 with the high one.

**Ruled out, and why:**

- **The instruction census.** gemmLnc has 39 instructions an op against gemmL's 46. Item 6 prices that at -39.64 pJ a minion-op, about
  -0.03 W: the wrong sign, and 0.2% of the excess.
- **The op time.** The excess is taken given the measured op time, and gemmLnc is the faster kernel at 8 of 9 points.
- **The FMA and core logic.** The minion rail carries under 0.15 of the board excess at 7 of 9 points. Its 0.25-0.29 share at a079 and
  c02c matches their 10-12% higher op rate.
- **More chip-level L3 or DRAM lines.** The walk's chip stream is identical for both kernels.
- **"Every duplicate hits the L2" alone.** The NoC rail rises +1.9 to +4.5 W at NB ≤ 3.
- **"Every duplicate of a beyond-L2 line is re-fetched" (F2).** It overprices NB 5-6 by +24% and +25% in sample, and its E213-out fold is
  not identified.
- **One price for every duplicate (F1).** It leaves ±20% errors, because the per-op excess varies 4x.

## 3. The term

**Form F3**, two constants, fitted post hoc on the 9 points' residuals from MM1-v3.1's frozen predictor (`s04_fit.py`, `term-gemmlnc.json`):

    dW = D * sL * (minions / t_op) * 1e-12 * (c1 * dup + c2 * first)      [W]
    dup   = 26 duplicate line reads a minion-op (gemmLnc; 0 for every cooperative loop)
    first = (14 qA_b + 12 qB_b) / NB: the duplicates of the lines MM1-v3.1's map serves beyond the L2 (qA_b, qB_b = 1 - the L2 marginals of
            its Q), on the A panel's first C block of its row of C blocks
    c1 = 254.4 pJ a duplicate L2 read;  c2 = 552.1 pJ a re-fetched duplicate line
    D = 1 + 0.0048 (die - 50 C), sL = 1 + xi (s_V - 1): MM1-v3.1's own die and line-voltage factors (as it applies them to its line energies)

The scorer's `given()` form is W = A + B / t_op. The term is proportional to 1 / t_op, so it adds dW t_op to MM1-v3.1's B and leaves A
unchanged. For scale: c1 is 0.20 of MM1-v3.1's fitted L3 line price for random data (b3 + d3 = 1,256 pJ), and c2 is 0.44 of it.

**The declared selection** (in `s04_fit.py`, written before the fits ran; post hoc, as the forms were designed after the data were seen):
the lowest leave-one-point-out (LOPO) rms of W over idle, a two-constant form only if it beats the best one-constant form by 1 point.
F3 9.81% against F1 19.37%: **F3**.

### Table 4. The candidate terms

W over idle errors in %, on the 9 points. MM1-v3.1 alone: rms 32.56%, mean -30.66%.

| form | x | constants, pJ a line | in sample | LOPO | LORO (12 runs) | LOEO E211 out | LOEO E213 out | E213 arm A out | card 1 out | aifoundry3 out |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | dup | 360.3 | 16.16 | 19.37 | 17.56 | 11.67 | 19.67 | 17.82 | 19.01 | 16.10 |
| F2 | dup + beyond | 261.4, 324.2 | 13.45 | 16.51 | 16.29 | 21.37 | 961.80 (NOT IDENTIFIED) | 13.34 | 15.40 | 27.95 |
| **F3** | **dup + first** | **254.4, 552.1** | **7.99** | **9.81** | **9.63** | **10.05** | 100.71 (NOT IDENTIFIED) | **12.82** | **9.86** | **12.76** |
| F4 | beyond | 587.5 | 23.72 | 25.17 | 23.17 | 21.35 | 25.79 | 21.31 | 34.21 | 31.22 |

F3's per-point errors in sample, in %:

| c01c | c02c | a087 | a086 | a079 | a075 | a082 | k40 | k37 |
|---|---|---|---|---|---|---|---|---|
| -8.6 | +11.3 | +4.6 | +3.6 | +8.5 | +0.7 | +13.6 | -6.4 | -6.1 |

How to read the folds:

- **LORO** leaves out one committed run: 12 runs, where a point with two runs keeps the mean of the other.
- **LOEO with E213 out** trains on E211's two points alone. Neither is L2-resident, so the two constants cannot be told apart there, and the
  fold is **NOT IDENTIFIED** (two points, two near-collinear columns).
- **E213 arm A out** trains on E211 plus card 1: four points, one of them L2-resident.
- **The cards.** Card 1 out (trained on aifoundry3) reads card 1 low by 10.6% and 9.0%. Card 1 runs about 6-10% above the term (LOCO), and
  with two constants there is no card factor.

**On cooperative gemmL the term is 0 by construction** (dup = first = 0: one read a coop group), and the twins need none. Their measured /
MM1-v3.1 ratios are 1.034, 0.974, 0.985, 0.972, 0.978, 1.035, 0.979, 1.009 and 1.034.

**The held-out check.** E213's two gemmLnc smokes (gemmLnc2x2x2 fp32, NB 2; committed, never fitted) are REPORTED, with their rest
estimated (the reducer's p_rest there is the previous process's tail). The estimate is the session's opening rest moved to the smoke's
start die by the frozen rest law.

| smoke | W over idle | MM1-v3.1 | F3 | F2 | F1 |
|---|---|---|---|---|---|
| s03 (arm A) | 34.90 W | -29.4% | **-2.1%** | +0.7% | -10.5% |
| s14 (arm B) | 36.66 W | -31.9% | **-6.3%** | -3.7% | -14.2% |

## 4. The frozen forecasts for E215's gemmLnc points

**The method:**

- **The base.** MM1-v3.1's frozen predictor in its registered call: `mm1_v31.Model(out/mm1_v31_params.json).predict_many([{card, arm, fmt,
  kind, mask, f: 600.0, kernel}])`, params sha256 `d01009a0...`, at a 50 C die (its default) and the card's default volts.
- **Reproduction.** It reproduces MM1-v3.1's frozen E215 forecasts: a024-a032 to the CSV's printed precision, and b013 exactly against
  `forecast-e215b-v31.json`.
- **The term.** F3 is added at MM1-v3.1's own op time.
- **J over idle** = W x MM1-v3.1's seconds a GEMM.
- **J at rest** = (the rest law at the card's T0 forecast + W) x seconds.
- **The planning peak** = W + the rest law + 2 W, the registration's form.
- **The stops.** Arm A 70 W x3, arm B 72 W x3.

### Table 5. The frozen forecasts (MM1-v3.1 + gemmLnc term, form F3)

| id | arm, card | shape | NB | MM1-v3.1 W over idle | term W | **W over idle** | A, B (W, W us) for given() | J over idle a GEMM | J at rest a GEMM (rest law, T0) | planning peak W | stop | margin W | within 3 W |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a024 | A, aifoundry3 card 0 | gemmLnc1x15x3 | 15 | 19.554 | 3.978 | **23.531** | 0.9293, 44.2701 | 0.13274 | 0.27230 (24.74 W, 54.4 C) | 50.27 | 70 W x3 | 19.73 | no |
| a026 | A, aifoundry3 card 0 | gemmLnc1x12x4 | 12 | 19.456 | 4.112 | **23.568** | 0.9293, 44.2470 | 0.14151 | 0.29006 (24.74 W, 54.4 C) | 50.31 | 70 W x3 | 19.69 | no |
| a031 | A, aifoundry3 card 0 | gemmLnc8x1x5 | 1 | 16.582 | 9.314 | **25.896** | 0.9293, 57.8332 | 0.15356 | 0.30028 (24.74 W, 54.4 C) | 52.64 | 70 W x3 | 17.36 | no |
| a032 | A, aifoundry3 card 0 | gemmLnc5x1x10 | 1 | 16.446 | 9.308 | **25.754** | 0.9293, 57.5436 | 0.19103 | 0.37455 (24.74 W, 54.4 C) | 52.49 | 70 W x3 | 17.51 | no |
| b013 | B, aifoundry1 card 1 | gemmLnc2x1x37 | 1 | 16.577 | 8.461 | **25.038** | 1.4067, 59.9726 | 0.30094 | 0.68262 (31.76 W, 55.0 C) | 58.80 | 72 W x3 | 13.20 | no |
| s03 (smoke) | A, aifoundry3 card 0 | gemmLnc2x2x2 | 2 | 24.700 | 9.569 | **34.269** | 0.9118, 48.5198 | 0.02552 | 0.04395 (24.74 W, 54.4 C) | 61.01 | 70 W x3 | 8.99 | no |
| s14 (smoke) | B, aifoundry1 card 1 | gemmLnc2x2x2 | 2 | 25.278 | 9.523 | **34.802** | 1.3892, 48.5996 | 0.02592 | 0.04957 (31.76 W, 55.0 C) | 68.56 | 72 W x3 | 3.44 | no |

The other forms beside, REPORTED (W over idle):

| id | F1 | F2 | F4 | max-form peak |
|---|---|---|---|---|
| a024 | 24.48 W | 27.55 W | 27.58 W | 54.32 W |
| a026 | 24.39 W | 27.47 W | 27.50 W | 54.24 W |
| a031 | 20.74 W | 23.35 W | 23.37 W | 52.64 W |
| a032 | 20.60 W | 23.20 W | 23.23 W | 52.49 W |
| b013 | 20.36 W | 22.72 W | 22.74 W | 58.80 W |
| s14 | 31.87 W | 35.78 W | 35.64 W | 69.54 W, **within 3 W** |

**Safety, for the orchestrator.** A trip is the registered stop; nothing is changed by this lane.

- **No registered E215 gemmLnc point comes within 3 W of its stop** by any form. The closest is b013: 58.80 W against 72 W.
- **Arm B's smoke s14 comes close.** It is gemmLnc2x2x2, which E215 runs right before the gemmLnc block at the session's end, and it is
  E213 arm B's 66.1 W peak smoke.
  - With the term its planning peak is **68.56 W (3.44 W margin)**, and 69.54 W (2.46 W) by F2.
  - E213's own measured s14 (W over idle 36.66 W) on the frozen rest law at 55 C reads **70.42 W planning peak (1.58 W margin)**.
  - On E213's measured card-1 rest (28.49 W) its board mean was 65.15 W.
  - Card 1 runs 6-10% above the term (Section 3), so a warm card at the session's end makes a 72 W x3 trip at s14 possible: it would end
    the session before b013.
- Arm A's s03 reads 61.0 W (term) and 61.6 W (analog), under the 70 W stop.

### Frozen: sha256 and times

The files were written at **2026-11-19 09:29:59 PST** by `s05_freeze.py`, run from this folder, and were final at **09:30:36 PST**
(`OUT/lnc-energy/FROZEN.txt`). At the freeze there was no booking on any box (`book.sh show` empty), no E215 card folder, and the lab main
stood at 8bde0182. No E215 data file was opened by this lane at any time.

    00fcaf5dd05e7af5a95ce1b783b68588a416dde91d0434f4f82ba6bdee6f5a7c  forecasts-gemmlnc-e215.csv
    feba7e5e70829854169bb3671947767c56c2303c20a74b83c7949bcd6b024e7c  forecasts-gemmlnc-e215.json
    2ee478f80aa1182aeb5d00e07fc302cffa668e66964ca7ebc2e61362128f3ee4  term-gemmlnc.json

The forecasts are blind for E215 once these hashes are in a pushed commit, or posted, before E215's first card command.

## 5. Gaps and NOT RUN

- **The NB dependence** of the NoC re-fetch is described (1 / NB, the A panel's first C block), not derived. No simulator here has caches
  with time, so the merging of in-flight duplicates in the L2 cannot be checked at the desk.
- **NB 3** (c01c) is under by 8.6%, and **NB 5-6** are over by 8.5-11.3%. The forecasts sit at NB 1 and NB 12-15, where the form is pinned
  by 4 and 2 points respectively.
- **Data kind.** Every point is random data (phi 1), so the term's data dependence is not identified. E215's points are random too.
- **Format.** The two int8 points are both the L2-resident 1x1x1, so a format effect cannot be told from the L2 regime. E215's points are
  fp32.
- **Card 1** reads 6-10% above the term, with no card factor at two constants.
- **Time.** MM1-v3.1's op time overprices gemmLnc's cycles at NB 5-6 (c02c +16.4%, a079 +9.6% in sample), so a024 and a026 may run faster
  than forecast. That affects J with the time forecast, not W given t. No time term is frozen here.
- **The smokes' rest** is estimated (REPORTED): their W over idle is not the reducer's.
- **NOT RUN:** any card, any simulator run, any fit of MM1-v3.1's own constants (the term sits on its frozen predictor), and any E214 read.

## Files

| file | what |
|---|---|
| `forecasts-gemmlnc-e215.csv`, `.json` | **the frozen forecasts** (rows, all four forms, the reproduction check, the held-out smokes, the safety analog) |
| `term-gemmlnc.json` | **the frozen term**: form, constants, equation, fits and folds, the selection |
| `s01_points.py` | step 1: the 9 points and twins, MM1-v3.1 given t, its line map by operand -> `work/s01_points.json` |
| `s02_rails.py` | step 2a: the rail split of every E211 and E213 run in the reducers' windows -> `work/s02_rails_runs.json`, `work/s02_rails_points.json` |
| `s03_walk.py` | step 2b: the walk's traffic per shape -> `work/s03_walk.json` |
| `s04_fit.py` | step 3: the forms, the folds, the declared selection -> `work/s04_fit.json` |
| `s05_freeze.py` | step 4: the forecasts (writes the three frozen files) |
| `s08_tables.py` | this README's tables, from the work files -> `logs/s08_tables.md` |
| `logs/` | the run log and each step's output |
| `SHA256SUMS` | every file here |

To re-run from a checkout of the lab: from this folder, run each of `s01_points.py`, `s02_rails.py`, `s03_walk.py`, `s04_fit.py` and
`s05_freeze.py` in turn with `/usr/bin/python3 -B` and single-threaded maths (OMP_NUM_THREADS=1 and the like). The lab is found from this
folder's place in it, or from `ET_LAB`. The work files re-make byte for byte, except `work/s03_walk.json`'s per-shape seconds and the
forecasts JSON's `made` time.
