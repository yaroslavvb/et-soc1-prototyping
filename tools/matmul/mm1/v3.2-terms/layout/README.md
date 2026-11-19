# A layout term for MM1-v3.1: 'MM1-v3.1 + contention', frozen for E215 before any E215 datum

Round Q225, lane lay-contention, Thu 19 Nov 2026, Pacific time. Desk only: nothing here measured anything. Every number is **post
hoc** (computed after its data existed) and **held out** where it says so; nothing is blind. E215, MM1-v3.1's blind matmul day,
is the first blind test of this term: its 28 subset-mask points (family L: 20 on arm A, aifoundry3 card 0; 8 on arm B, aifoundry1
card 1) are the only E215 points the term changes. No E215 data file or folder was opened by this lane; E215's registered point list
(`tools/claims-v3/e215/points-e215.csv`, registration 4cb2c2ad) was read for its shapes and masks only.

The owner's words that put the matmul first (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you
to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches
and clock cycles. From based on what I know about the size of a matrix and which operations are contained."

**The question.** MM1-v3 and MM1-v3.1 miss subset layouts: at an equal shire count, the placement moves the wall time by up to 15%
(E212's layout pairs), E213 arm A's time failures are subset points (gemmL1x3x12 fp32 at 0x1010101 and 0x11; gemmL2x8x8 at 0x3,
0xf0000, 0xf0f), and E212's re-run S3 has spread-mask misses of +9.1 to +9.7%. MM1-v3.1's level map is keyed by the arm, never the
mask (`engine_v3.ShapeBank`), so every subset is priced at the full chip's footprint and the mask enters only through n / 32
(`chi3`, `chiF`) and the row-imbalance term (`eta`). The masked walk (`../../v3.1/walk/`, 5a75e212, trace check PASS) gives each
shire's exact request stream; as T7 inside v3.1's fit it read a leave-one-layout-out error of 14.40% against n/32's declared 89.78%
(a figure an unidentified `eta` dominates; n/32's re-read with that `eta` at 0 is 6.32%, below T7's) and raised the pooled LOEO to
6.20%, so v3.1's declared rule kept it out.

## What was done, in order (times from the lane's log)

| when (PST) | step | file |
|---|---|---|
| 09:09-09:12 | a desk look at MM1-v3.1's committed residuals by mask (not blind: it saw the points the folds score) | `look_residuals_layout.py`, `look_pairs_layout.py` |
| 09:14-09:18 | the walk and mesh features of every subset configuration of the fit set and of E215 (187 walks, 254 s) | `features_layout.py` -> `out/features_layout.json` |
| 09:19:44 | **the forms and the keep rule declared** (before any form was fitted or scored) | `DECLARED-layout.md` (sha256 `df336d74...`) |
| 09:21:27 | the seven declared forms scored, two-stage, on MM1-v3.1's fold records | `eval_layout.py` -> `out/eval_layout.json` |
| 09:22-09:24 | a post hoc look: which feature orders the measured layout pairs | `look_features_layout.py`, `order_pairs_layout.py` |
| 09:24:29 | **addendum 1** (post hoc, after the scores): a placebo check for the rule's winner and two more forms | `DECLARED-layout-addendum-1.md` (sha256 `55570842...`) |
| 09:25:39 | the placebo check and the added forms scored | `placebo_layout.py` -> `out/placebo_layout.json` |
| 09:28:14 | the winner's E215 forecasts made and checked against MM1-v3.1's frozen files | `freeze_layout.py` -> `forecast-e215-v31-layout.csv`, `.json` |

Interpreter `/usr/bin/python3` 3.12.3, numpy 1.26.4, scipy 1.11.4, `-I -B`, single-threaded, in the round's CPU slots. Run from a
checkout holding MM1-v3.1 (`tools/matmul/mm1/v3.1/`, 2c971828) and this folder; `features_layout.py` imports the walk unchanged.

## The chip's placement: what is known and what is assumed

Known (the lab's measured notes, `docs/et-soc1-notes.md`, and its public sources):

- **Mesh positions:** the 32 compute shires on a 6 x 6 grid (4 stops for the master, spare, I/O and PCIe shires), in the public
  logical map from marty1885's NoC topology scanner (`MARTY` in `workloads/nocbench/analyze.py`); every inter-shire latency is
  a + b x Manhattan distance on that map; a hop costs 20 ns round trip (12 cycles at 600 MHz).
- **The L3's distribution and interleave:** each compute shire's SRAM holds an L3 slice; a line's home shire is PA[10:6] (the lab's
  memory-anatomy probe: L3 hit = 110 + 12 x hops(requester, home)).
- **The memory shires and their controllers:** eight memory shires, a line's memory shire PA[8:6] (the probe and the read counters):
  the DRAM leg past the L3 is 91 + 12 x hops(home, memory shire); memory shires 0-3 sit one step off one edge of the map at x = 1-4,
  4-7 off the opposite edge.
- **The kernels' streams:** the masked walk (no fitted constant, read from the kernels' sources, checked against traced simulator
  runs): which active shires ask which A and B tile at each lock step; an A tile is asked by the active shires of its row group
  (shire >> 2), a B tile by those of its column group (shire & 3).

Assumed (not measured or not stated in the lab's notes): memory shire m at x = 1 + (m mod 4) along its edge; dimension-ordered
(x, then y) routing for the link loads; the four non-compute stops carry no matmul traffic; the L3 slices of shires outside the launch
mask still serve their homes (PA[10:6] is a fixed address function; the probe measured it with every shire); the walk's lock-step,
strict-LRU (32 MB) levels.

**Where each run's requests are served** (from the walk and the interleave, for every run of the data; `out/features_layout.json`
holds each configuration's numbers): every A and B tile is 1 KiB aligned, and at one step every tile has the parity of k, so a step's
requests go to one half of the 32 homes (the halves alternate with k), each home receiving exactly one line of every requested tile;
every fresh (DRAM) tile sends exactly two lines to each memory shire. **So the per-slice and per-controller loads are uniform for
these kernels at every mask** (the maximum over slices equals the mean: n x 12 lines per home per step with cooperative loads): no
slice or controller is hot, and the placement can act only through (a) the footprint and sharing pattern (which shires ask which tiles,
hence what the L3 holds and how many lines reach DRAM) and (b) the mesh paths (hops; link loads). The features below measure both.

## The forms (declared 09:19:44, before any score)

T = T_v31 x (1 + sum a_i Phi_i), on the subset points of the walk's loops; every Phi_i = 0 at the full mask by construction, so the
term is exactly zero at the full chip. At most two constants.

| feature | what it is |
|---|---|
| Phi_fresh (per-controller load) | the walk's DRAM lines a step over the line requests a step, minus the full chip's |
| Phi_link (mesh contention) | the busiest directed link's L3-return load over the full chip's, minus n / 32 |
| Phi_hop (hop distance) | the slowest active shire's mean L3 latency over the 32 homes over the full chip's slowest, minus 1 |
| Phi_fan (shared-operand fan-out) | the request-weighted mean number of active shires asking each tile, per active shire, minus the full chip's |
| G1 Phi_hopmean (addendum 1) | the active shires' mean L3 latency over the 32 homes over the full chip's mean, minus 1 |
| G2 Phi_share (addendum 1) | n_A / 4 - n_B / 8: the A tiles' sharers against the B tiles' (zero at the full mask) |

Forms F1 Phi_fresh, F2 Phi_link, F3 Phi_hop, F4 Phi_fan, F5 Phi_fresh + Phi_fan, F6 Phi_fresh + Phi_link, F7 Phi_fresh + Phi_hop; G1,
G2. "T7's own levels with one of these" as a joint refit is **NOT RUN** (T7's fits took 170-740 s a fold in Q222).

**How scored (two-stage, held out):** each fold's base is that fold's own stored MM1-v3.1 constants (`../../v3.1/out/fits/
time_T5r+G0+n32.json`), re-predicted with `time_v31.Engine31` (equal to the stored held-out predictions: 0 difference in every
fold); the term's constants are the linear least-squares solution of the fold's training residuals (E146's store rungs out); the
base's constants are **not** refitted with the term. LOEO: the 18 experiment folds, pooled over the 1,299 no-twin points. LOLO: item
4's three layout classes, every subset point (212: E212 122, E206 28, E208 23, E213 22, E209 9, E207 8; all rgm136 gemmL), read (a)
as declared (the compact fold's `eta` sits at its bound 2.0, an unidentified constant: v3.1 reads 89.78%) and (b) with that fold's
`eta` at its neutral 0 (v3.1's README's own post hoc re-read). Pairs: the 37 equal-count layout pairs of E212 and E213 (same card,
kernel, arm, format, clock and shire count; measured more than 1% apart).

**The keep rule (declared):** LOLO (b) below v3.1's, LOLO (a) not above v3.1's, pooled LOEO (no twins) at most 4.72%; the lowest LOLO
(b) wins, within 0.10 points the fewer constants. **Addendum 1 (post hoc):** the winner must also beat 95 of 100 permutation placebos
of its own feature (seeded 20261119 + i) and both layout-class indicators.

## The result (post hoc, held out)

| form | constants (all-data) | LOEO no twins | LOEO subsets | LOLO (a) | LOLO (b) | (b) compact / spread / other | LOCO | pairs ordered (in sample / LOEO) | rule |
|---|---|---|---|---|---|---|---|---|---|
| MM1-v3.1 | - | 4.723% | 6.470% | 89.78% | 6.319% | 6.17 / 6.55 / 6.47 | 4.150% | 12 / 12 of 37 | - |
| **F1** | a_fresh -0.0832 | **4.710%** | 6.408% | 89.32% | **6.248%** | 6.07 / 6.46 / 6.51 | 4.148% | 17 / 17 | **kept; winner** |
| F2 | a_link +0.015 | 4.720% | 6.457% | 89.44% | 6.319% | 6.13 / 6.82 / 6.15 | 4.149% | 20 / 20 | out (LOLO b not lower) |
| F3 | a_hop +0.497 | 4.754% | 6.622% | 89.44% | 6.279% | 6.09 / 6.56 / 6.47 | 4.177% | 15 / 15 | out (LOEO) |
| F4 | a_fan +0.021 | 4.704% | 6.378% | 89.92% | 6.274% | 6.18 / 6.82 / 5.66 | 4.142% | 20 / 20 | out (LOLO a) |
| F5 | a_fresh -0.092, a_fan +0.024 | 4.688% | 6.296% | 89.50% | 6.190% | 6.09 / 6.81 / 5.47 | 4.139% | 20 / 20 | kept (the lowest LOLO (b) of the kept forms; F1, within 0.10 points with one constant, wins) |
| F6 | a_fresh -0.090, a_link +0.022 | 4.704% | 6.375% | 88.94% | 6.288% | 6.03 / 6.97 / 6.04 | 4.146% | 19 / 17 | kept |
| F7 | a_fresh -0.074, a_hop +0.341 | 4.736% | 6.535% | 88.93% | 6.205% | 5.99 / 6.46 / 6.50 | 4.169% | 18 / 18 | out (LOEO) |
| G1 | a_hopmean +0.303 | 4.703% | - | 90.27% | 6.172% | 6.22 / 6.58 / 5.28 | - | - | out (LOLO a) |
| G2 | - | 4.729% | - | 93.16% | 6.871% | 7.05 / 6.65 / 6.58 | - | - | out |

Kept by the declared rule: F1, F5, F6. The rule's winner: **F1** (the lowest LOLO (b) among kept forms is F5's 6.190%; F1 at 6.248%
and F6 at 6.288% are within 0.10 points, and F1 has one constant). Addendum 1's check: F1's LOLO (b) is below that of **98 of 100**
permutation placebos (median 6.327%, range 6.197-6.578%), so F1 passes; the class-indicator half of the check is degenerate (a
held-out class's indicator is zero on every training point of its LOLO fold, so it reads as MM1-v3.1 itself) and is passed trivially.
G1 had the lowest LOLO (b) (6.172%; 100 of 100 placebos above) but its LOLO (a) is higher than v3.1's, so the declared rule leaves it
out; it is REPORTED beside the frozen forecasts.

**What F1 is, read honestly.** It earns its place by the declared rule and the placebo check, but its held-out gain is small (LOLO (b)
6.319% -> 6.248%, pooled LOEO 4.723% -> 4.710%), and its sign is the opposite of a per-controller load: a subset whose active footprint
sends more DRAM lines per request than the full chip runs *faster* than MM1-v3.1 says (the subset's DRAM relief exceeds what `chiF`'s
n / 32 gives). It orders 17 of the 37 measured layout pairs (MM1-v3.1: 12), so it does not explain the up-to-15% layout spread. The
layout effect's sign flips with the shape (the layout whose shared operand is A is faster at gemmL1x1x16, 4x8x4 and 1x3x12; the one
sharing B is faster at 1x16x4, 2x4x16 and 2x8x8, where its active footprint is the smaller), and no single walk or mesh feature orders
more than 22 of the 37 pairs (`order_pairs_layout.py`: hop_mean 22/15; fan-out 20/17; fresh 18/15 with 4 ties; R and C 20/17).

## The frozen forecasts (`forecast-e215-v31-layout.csv`, `.json`)

'MM1-v3.1 + contention' = MM1-v3.1's wall op time at its frozen all-data constants x (1 - 0.0832 x Phi_fresh), for every E215 point
and reference of the registered list (94 rows: arm A's 60 points and 2 references, arm B's 30 points and 2 references):
wall cycles an op (`v31c_cycles_per_op_wall`), the op time and seconds a GEMM (`v31c_seconds_per_gemm` = op time x the registered
ops a minion a GEMM). MM1-v3.1's own forecast, re-made here at its frozen constants, equals the frozen files to their 4-decimal
rounding (worst 5.1e-8 relative), and sits beside each row with its source file.

**The term at the full mask is exactly zero:** all 66 full-mask rows have factor 1 and keep MM1-v3.1's forecast to the last digit
(checked by `freeze_layout.py`). At the 28 subset rows the factor runs 0.9942-1.0139: the 12 rows of 28 shires with one row
group off (0xf0ffffff ... 0xfffffff0) read 0.9995; the two 24-shire spread masks (0xbbbbbbbb, 0xdddddddd) 1.0000; the other 14 rows
(2-15 shires) 0.9942-1.0139 (the largest, 0xcc000 at gemmL2x1x16 and 0xee000e at gemmL1x1x16 on arm B, both +1.39%; the only one
below 1, 0xd000dd0 at gemmL1x8x6, -0.58%). Beside them, REPORTED and never the frozen form:
F5's and G1's cycles for the same rows.

## After the freeze (REPORTED; no frozen file changed)

The freeze was final at **09:31:34 PST** (the lane's FROZEN.txt: `forecast-e215-v31-layout.csv` sha256 `50949ba3...`, `.json`
`f09f9e1a...`). Everything in this section was run after it and changes none of its bytes.

- **Reproduction** (09:32-09:34): the landed scripts, re-run from a copy of this folder inside a read-only tree of the lab checkout,
  give the forecast CSV byte for byte and every JSON equal but for its run-time field (`eval_layout.py` also writes
  `out/phi_layout.npy`, not kept here).
- **A joint refit** (09:36-09:51, `joint_layout.py` -> `out/joint_layout.json`): the layout constant fitted together with every
  MM1-v3.1 time constant by `fit_v31.fit_time` unchanged (18 declared starts, phase 2, the pin rule; the constant free in [-3, 3]
  from 0), on the same LOEO and LOLO folds:

  | form, joint | all-data constant | LOEO no twins | LOEO subsets | LOLO (a) | LOLO (b) | (b) compact / spread / other | constant in every fold |
  |---|---|---|---|---|---|---|---|
  | F1 (frozen form) | a_fresh -0.0999 | 4.691% | 6.394% | 89.25% | 6.269% | 6.05 / 6.59 / 6.47 | negative in all 21 (-0.032 to -0.160) |
  | G1 (REPORTED) | a_hopmean +0.454 | 4.697% | 6.419% | 89.29% | **5.976%** | 5.95 / 6.51 / 5.13 | positive in all 21 (+0.230 to +0.581) |

  So F1 keeps its sign and passes the declared rule when fitted jointly too; and **G1, which the two-stage scoring left out by 0.5
  points of the degenerate LOLO (a), passes every condition jointly and has the lowest LOLO (b) of anything tried**: its constant has
  the sign of the measured L3 law (active shires farther from the 32 homes on average run slower). The freeze stays F1 (the declared
  procedure chose it); G1's two-stage forecasts are frozen beside it in the same files (column `REPORTED_G1_cycles_per_op_wall`, made
  before any E215 datum), so E215's family L scores both blind.
- **How the committed fit records order the 37 pairs** (`pairs_fitrecords_layout.py` -> `out/pairs_fitrecords.json`; cycles basis):
  MM1-v3.1's n/32 form orders 13 in sample and 13 held out (13 exact ties: n/32 cannot tell equal-count layouts apart); the T7 form
  20 in sample and **22 held out** (it failed v3.1's LOEO condition, 6.20%).
- **Where each configuration's requests are served** (`placement_layout.py` -> `out/placement_by_config.csv`; 187 configurations,
  151 used by a run of the data or an E215 row): lines each L3 home receives a step, fresh lines each memory shire receives a step,
  the fresh share of requests against the full chip's, the active shires' mean and largest mean hop to the homes, the busiest
  link's load, the fan-out, and which runs use it. The link column counts 192 lines a shire-step (cooperative loads): for gemmLnc's
  rows (full-chip only here) it is low by 1024 / 192; the features' ratios to their own full chip are unaffected.

File names in the scripts' docstrings are the lane's working names (`work/s04_eval.json` is `out/eval_layout.json`, and so on).

## Gaps

- Two-stage for the freeze: the base constants were not refitted with the term (the joint refit above is REPORTED). T7 plus a
  term as a joint T7 refit: NOT RUN.
- The selection is post hoc on the data it scores; only E215 can say whether F1 (or G1, REPORTED) helps blind.
- The memory shires' order along their edges and the routing are assumed; no lab measurement shows the L3 under a subset mask.
- E214 (the model session's third sweep) was not read: it is not in MM1-v3.1's fit and track A scores it UNREAD.
- run_gemm points carry no term (the walk does not cover them); MM1-v3.1's fit holds no run_gemm subset point.

SPDX-License-Identifier: Apache-2.0
