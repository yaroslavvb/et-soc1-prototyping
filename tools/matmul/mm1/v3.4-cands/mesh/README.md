# 'MM1-v3.2 + mesh': a placement term for core-group masks from the L3's set map and the mesh (a v3.4 candidate), frozen

*Round Q238, lane mask-mesh (track M), Sat 21 Nov 2026 (week 47), Pacific time, 01:05-02:04 PST (frozen 02:03:37), at aifoundry2's desk. Desk only: no card,
no simulator, no ssh, no booking. Interpreter for every number: `/usr/bin/python3` 3.12.3, numpy 1.26.4, scipy 1.11.4, `-I -B`,
single-threaded (OMP / OPENBLAS / MKL / NUMEXPR_NUM_THREADS = 1), every numerical job inside the round's CPU slots, one at a time.*

The owner's words that put the matmul first (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you to
focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock
cycles. From based on what I know about the size of a matrix and which operations are contained."

**Labels.** *Known*: a committed measurement or a documented fact, cited. *Assumed*: named as such. *Post hoc*: every constant and the
form's choice (made after the looks disclosed in `DECLARED-mesh.md` section 0). *Held out*: left out of the fit that scores it (not blind).
*Blind*: only data that did not exist when a forecast was frozen (here: E221's MM1-v3.2 and posimb errors, read from their committed score).
*REPORTED*: printed beside a rule, never deciding it. *NOT RUN*: not run. Error = forecast / measured - 1 of the wall op time; rms and bias in %.

## 0. On one screen

| item | value |
|---|---|
| the lead | E221's MASK class (core-group mask placements): MM1-v3.2 BLIND 12.41% wall rms on 363 no-twin cases, 152 of its 175 T1 misses |
| the mechanism | the L3 is 4-way set associative with an 8 MiB aliasing period (its documented decode); MM1-v3.2's place map is mask-blind |
| the form | MM1-v3.2's own engine with its L3 / DRAM place map moved by the walk's set-associative miss shares and its L3 / DRAM latency constants moved by the mesh hop, both at the laggard shire against the full chip's: **two constants** |
| the constants (all data) | **a_set 0.738, a_hop 0.827** (1 = the mechanism's own size; both positive in all 144 folds) |
| THE KEY HELD-OUT NUMBER | **leave one mask out: the lead 12.41% -> 5.97%** (bias +5.23 -> -1.30) |
| the declared rule | K1 (margin 1 point) PASS, K2 (LOSO 5.98%, LOEO 7.38%, LOCO 6.06%) PASS, K3 (non-MASK guard +0.0006 points) PASS, K4 (placebo 100 / 100) PASS: **KEPT** |
| declaration | `DECLARED-mesh.md` sha256 `f9e5a8681b87db6d43ef32948490be948026c1fdc57d3e54a34b5f7e866af134`, hashed 01:39:07 PST before any fit |
| with AF4 | 'MM1-v3.2 + AF4 + mesh' by construction (disjoint domains), checked against AF4's frozen E220 forecasts: 46 gemmLnc rows to 2.7e-10 |

## 1. The lead

E221 (the model session's sixth sweep, 847 runs, three cards) failed the lab's declared blind test on MM1-v3.2's time bands; blind-e221
(5eb23fd4) put 152 of the 175 T1 misses on the MASK class: one shape placed on many shire groups, each with its whole-chip twin. MM1-v3.2
reads 12.41% there (n 363, no twin), single-shire placements +10.3% bias (the card faster), 16-31-shire ones -4.7% (the card slower). Its
place map Q (the share of ops whose A and B come from the L2, the L3 or DRAM) is keyed by the arm only, so every mask of a shape gets the
full chip's; its subset terms are n / 32 contention (chi3 0.055, chiF 0.097) and a row term at 1e-9.

## 2. The mechanism: known and assumed

- **The L3's set map (known; the lab's memory-levels report of 2026-09-28, from the shire cache specification it cites; default swizzle0):**
  home slice PA[10:6], bank PA[12:11], sub-bank PA[14:13], set PA[22:15] (256 sets a sub-bank in Mode 0), 4 ways. So the 32 MiB L3 is
  4-way set associative over 131,072 sets: a 1 KiB tile lands in 16 homes at one set index, and two tiles compete iff their tile index
  agrees mod 8,192 (8 MiB). *Assumed:* the cards run that decode, LRU replacement.
- **The tiles (known; MM1-v3.1's masked walk, trace check PASS):** rgm136 gemmL's A tile (mb, kb, row, k) at (mb KB + kb) 2 MiB + (row 32 + k)
  1 KiB of its pool, B (kb, nb, col, k) at (kb NB + nb) 1 MiB + (col 32 + k) 1 KiB; a shire's rows are 8 (s >> 2) + 0..7, its columns
  8 (s & 3) + 0..7. **The pools (known for the simulator, assumed for the card):** C, then A, then B, back to back (every traced sys_emu run).
  So **A's tile at (row, k) and B's at (col, k) share 4 ways exactly when row ≡ col (mod 32)**: a shire whose row group equals its column
  group mod 4 (shires 0, 5, 10, 15, 16, 21, 26, 31) evicts its own A with its own B. `scripts/test_mesh_l3.py`: this lane's stream equals
  `walk_v31.chip_steps` request for request (7 of 7 shapes and masks).
- **The mesh (known; docs/et-soc1-notes.md, three cards):** an L3 hit costs 110 + 12 x hops(requester, home), the DRAM leg 91 + 12 x
  hops(home, memory shire); lines interleave uniformly over the homes and memory shires (no hot slice or controller at any mask). *Assumed,
  REPORTED only:* X-then-Y routes for per-link loads.
- **Assumed (the walk's convention):** the second pass is the steady state; a tile asked by w shires is one request; every distinct tile
  request of a step enters the L3 (no L2 filter); C's stores allocate.

The mechanism alone (no constant) at E221's gemmL2x6x10 single shires: the eight collision shires miss 0.61-0.62 of their A requests and
0.565 of B, the other 24 miss 0.167 and 0.500, the full chip's laggard 0.66 and 0.65; the walk's fully associative LRU reads 0 at every
single shire. On the card (E221, 26 single-shire masks of that shape on three cards; held out by leave one mask out):

| gemmL2x6x10 fp32 zeros, one shire | cases | MM1-v3.2 rms (bias) | + mesh rms (bias) |
|---|---|---|---|
| the collision set (row group = column group mod 4) | 24 | 3.87 (-1.12) | 4.97 (-3.98) |
| the other shires | 54 | 15.52 (+15.17) | 2.97 (+1.94) |

## 3. The form (declared before any fit: `DECLARED-mesh.md`)

At a subset point of rgm136's gemmL loop, MM1-v3.2's op time is re-made by its own engine (`mesh_term.Base`, equal to `Engine31.predict`
at zero term in all 34 constant sets, max relative difference 0.0) with: (1) **the place map moved**: a_set dA of A's ops between MM1-v3.2's
L3 and DRAM places (dA > 0 to DRAM, < 0 from it; never more than the place holds), then a_set dB of B's; (2) **the latencies moved**:
c3 -> c3 (1 + a_hop g3), cF -> cF (1 + a_hop gF). dA, dB = the laggard shire's set-associative A and B miss shares less the full chip
laggard's; g3, gF = the laggard's L3 / DRAM latency from the latency laws less the full chip laggard's, relative (section 2). All exactly 0
at the full chip; every other point keeps MM1-v3.2 to the last bit. Bounds a_set [-1, 4], a_hop [-2, 4]; starts (1, 1) and (0, 0); least
squares of ln T over the fold's training points in the scope. MM1-v3.2's 19 time constants unchanged (two-stage).

## 4. The fit and the held-out record (post hoc; held out where it says so; `out/holdout-mesh.json`)

Data: every committed matmul time point through E224 (`out/points-mesh.json`, 4,311 points; 1,193 in the term's scope at 160 masks;
MASK class by this lane's rule, 1,013 points, equal to decl-e221's column at all 733 of E221's cases); excluded: every run whose check of
C failed and E224's p3a, p3b.

| the declared rule | MM1-v3.2 | + mesh | threshold | verdict |
|---|---|---|---|---|
| K1 the lead, leave one mask out (115 folds) | 12.409% | **5.975%** | <= 11.409% (1-point margin) | PASS |
| K2 the lead, leave one E221 session out (9) | 12.409% | 5.979% | below MM1-v3.2 | PASS |
| K2 the lead, leave one experiment out (E221's fold) | 12.409% | 7.378% | below | PASS |
| K2 the lead, leave one card out (4) | 12.305% | 6.060% | below | PASS |
| K3 non-MASK points without a twin, LOEO (n 2,341) | 5.4192% | 5.4199% | <= 5.4692% | PASS |
| K4 placebo (mask features permuted within each shape), 100 draws | - | beaten in 100 | >= 95 | PASS |

**Verdict: KEPT by its declared rule.** Placebo K1 rms min / median / max: 9.93 / 11.14 / 11.90%.

| fold | MASK, every point without a twin | MASK subset points without a twin | non-MASK scope points without a twin |
|---|---|---|---|
| leave one mask out (points at a fold mask) | 10.00 -> **6.40** (n 732) | 10.22 -> 6.48 (692) | 0.92 -> 0.97 (182) |
| leave one E221 session out | 9.39 -> 6.59 (903) | 9.56 -> 6.66 (863) | 1.15 -> 1.15 (193) |
| leave one experiment out | 9.47 -> 7.08 (903) | 9.63 -> 7.17 (863) | 1.51 -> 1.54 (193) |
| leave one experiment out, E215-E224 folds | 10.55 -> 7.01 (598) | | |
| leave one card out | 9.39 -> 6.48 (903) | 9.55 -> 6.55 (863) | 1.40 -> 1.43 (193) |

Constants by fold: leave one mask out a_set 0.722-0.771, a_hop 0.616-0.902; LOSO 0.716-0.738, 0.677-0.990; LOEO 0.428-0.767,
0.672-1.058; LOCO 0.598-0.754, 0.594-1.247: **positive in every fold, the expected sign**, a_set below 1 (the walk's L3 model over-states
the card's miss changes by about a quarter). The lead by card (LOMO): aifoundry1 card 1 11.21 -> 5.65%, card 0 13.00 -> 6.15%, aifoundry2
card 0 12.93 -> 6.11%.

## 5. REPORTED beside (never deciding)

**Controls**, fitted and held out (leave one mask out) by the same procedure (the lead's rms; all MASK points without a twin at the fold
masks):

| control | constants (all data) | the lead | all MASK |
|---|---|---|---|
| **the form** | a_set 0.738, a_hop 0.827 | **5.97** | 6.40 |
| the sets alone (a_hop = 0) | 0.853 | 6.15 | 6.52 |
| the hop alone (a_set = 0) | a_hop 2.57 | 9.75 | 8.44 |
| the walk's fully associative LRU instead of the sets (lay-contention F1's kind) | a_set 0.00002, a_hop 2.97 | 9.39 | 8.18 |
| the chip's request-weighted set shares, the active mean's hop | 0.481, 3.81 | 7.30 | 7.26 |
| the form with the active mean's hop (post hoc, better than the form) | 0.816, 3.30 | 5.52 | 5.98 |

So the sets do the work (the fully associative model fits a_set = 0: capacity alone explains nothing here), the hop adds about 0.2 points.

**posimb beside** on the lead's 351 subset cases (posimb's frozen, BLIND errors from blind-e221's case table against this term's LOMO
ones, post hoc): which placements each explains (cases brought closer to the measured wall than MM1-v3.2 by more than 1 point):

| family or shire count | cases | MM1-v3.2 | + posimb (blind) | + mesh (LOMO) | posimb closer | mesh closer |
|---|---|---|---|---|---|---|
| all subset cases | 351 | 12.60 | 12.33 | **6.04** | 44 | 201 |
| PLM gemmL3x4x6 | 24 | 28.19 | 27.75 | 5.34 | 3 | 23 |
| PLX gemmL2x6x10 (single shires) | 46 | 13.47 | 13.36 | 3.39 | 2 | 37 |
| PLH gemmL4x6x2 | 21 | 14.61 | 14.09 | 5.67 | 3 | 21 |
| PLK / PLK3 gemmL2x6x10 random, ones, int8 | 18 / 12 | 13.41 / 13.11 | 12.95 / 12.64 | 6.31 / 6.50 | 5 / 4 | 10 / 6 |
| PLA gemmL2x6x10 | 74 | 11.52 | 11.29 | 7.63 | 7 | 31 |
| PLB gemmL1x12x8 | 24 | 10.55 | 10.22 | 5.88 | 6 | 12 |
| PLL gemmL1x3x4 | 21 | 6.91 | 6.38 | 3.82 | 3 | 18 |
| PLC / PLD / PLE (no collision effect) | 24 / 21 / 42 | 2.52 / 2.31 / 3.14 | 2.52 / 1.79 / 2.77 | 3.31 / 1.84 / 3.40 | 1 / 4 / 3 | 6 / 11 / 21 |
| PLN gemmL2x6x10 at 24 shires | 18 | 13.39 | 13.38 | 13.64 | 0 | 0 |
| one shire / 2-3 / 4-7 / 8-15 / 16-31 | 160 / 91 / 41 / 3 / 56 | 14.19 / 12.96 / 5.59 / 12.46 / 10.78 | 13.74 / 12.85 / 5.54 / 11.69 / 10.75 | 3.90 / 5.15 / 4.76 / 14.57 / 10.69 | 27 / 3 / 14 / 0 / 0 | 127 / 50 / 12 / 0 / 12 |

posimb's features (the hop mean and the private share of the DRAM stream) explain a few 4-7-shire and single-shire cases by small amounts;
this term explains the single-shire and 2-3-shire placements (the collision set and the footprint the mask-blind map misses); **neither
explains the 8-31-shire masks with fewer than four column groups (PLN; PLA's 0x88888888, 0x66666666, 0x99999999, 0xaaaaaaaa), where the
card is 10-19% slower than MM1-v3.2**: this form can only make a subset faster (every feature is at most 0: the full chip's laggard has the
most set misses and the farthest homes), so those stay as they were.

**By experiment** (MASK points without a twin; leave one mask out where the mask is a fold, else leave one experiment out; post hoc):
E221 12.34 -> 5.95 (n 347), E224 7.46 -> 6.03 (20), E222 6.81 -> 6.06 (20), E217 8.04 -> 7.22 (104), E215 8.84 -> 6.11 (28), E214 7.27
-> 6.75 (126), E216 8.71 -> 8.06 (16), E209 8.14 -> 6.66 (10), E207 8.18 -> 6.61 (8), E220 4.73 -> 4.58 (50), E218 4.62 -> 4.59 (13), E208
4.06 -> 4.06 (7); **worse: E206 5.88 -> 9.91 (24), E212 6.45 -> 7.13 (106), E213 5.43 -> 5.98 (24)**. The named miss: **gemmL4x8x4 at
small masks** (E206 and E212: 0x1, 0xf, 0x1111, 0xff, 0xffff) where the walk's sets put B's miss share 0.38-0.41 below the full chip's and
the term speeds the op by 13-16% while the card reads MM1-v3.2 about right at 0x1, 0xf and 0x1111 (MM1-v3.2 -1.1 to -3.5%, the term -15.3 to -17.9%) and 6-10% faster than it at 0xff and 0xffff (MM1-v3.2 +5.9 to +10.2%, the term -3.7 to -7.2%); and
gemmL1x16x4 at 0x1 (-4.5 -> -10.9%). The guard (K3) does not see them: they are MASK points.

## 6. How to call it on new points, and with AF4

```
import json, mesh_term as MT                     # with MASK_MESH_REPO = a lab checkout (tools/matmul/mm1 at 4e386f75 or later, unchanged)
M = MT.Model(json.load(open('out/params-mesh.json')), 'out/features-mesh.json')
T_us, factor, X = M.time_many([{'arm': 'gemmL2x6x10', 'kernel': 'rgm136', 'fmt': 'fp32', 'mask': '0x4000', 'f': 600.0}])
```
`time_many` returns the wall op time (us), its factor over MM1-v3.2's and the four features; a configuration (arm, mask) missing from the
features cache is made by `mesh_l3.simulate` (no constant; seconds to a minute) and its full-chip reference with it. Cycles an op =
T x f; the counter's mean = cycles / MM1-v3.2's rho; seconds a GEMM = ops x T; W over idle at a measured t = MM1-v3.2's A + B / t; with t
forecast at this T. **With AF4** (MM1-v3.3 = MM1-v3.2 + AF4 as E222's selection rule chose it): `scripts/compose_af4.py composed(specs,
mesh)` gives 'MM1-v3.2 + AF4 + mesh': AF4's own equation and constants at gemmLnc points (this term out of scope there: factor 1, asserted),
this term's op time at cooperative gemmL subset points (AF4's dW = 0 there, asserted), MM1-v3.2 elsewhere; no refit. Checked against AF4's
frozen E220 forecasts (`out/compose-af4-check.json`): 46 gemmLnc rows re-made to 2.7e-10 relative (the CSV's printed digits), 160
full-chip rows to 3.1e-10, AF4 equal to MM1-v3.2 at all 100 cooperative subset rows; this term's factor there 0.966-1.000.

## 7. Files

- `DECLARED-mesh.md` (the declaration), `DECLARED.sha256.json` / `DECLARED.sha256` (it, the code and the inputs, hashed 01:39:07 PST), `FROZEN.txt`.
- `scripts/mesh_l3.py` (the mechanism: the walk's stream, the set-associative and fully associative L3, the map), `scripts/mesh_term.py`
  (the term, the engine re-made, the fit, the Model), `scripts/m01_points.py` (the points), `scripts/m02_features.py` (the features),
  `scripts/m03_fit.py` (the declared procedure), `scripts/m03b_rerun.py` and `m03c_compare.py` (section 8), `scripts/compose_af4.py`,
  `scripts/r01_report.py` (the post hoc summaries), the tests `test_mesh_l3.py`, `t02_smoke.py`, the looks `x01_e221_look.py`,
  `x02_single_look.py`, the snapshot and reduction scripts `s00*.sh`, `s01_reduce_e224b.sh`, `run.sh`, `h01_hash_declaration.py`, `m04_freeze.py`.
- `out/params-mesh.json` (the frozen constants), `out/fit-mesh.json`, `out/holdout-mesh.json` (every table above, the fold constants, the
  placebo scores, the controls), `out/points-scored-mesh.json` (per point: measured, MM1-v3.2 and the term in every fold, the features),
  `out/features-mesh.json` (the mechanism's numbers at 600 configurations), `out/points-mesh.json`, `out/compose-af4-check.json`,
  `out/report-mesh.json`, `out/inputs/` (E224 arm B by E208's registered reducer; the snapshot record).
- `logs/` (every run's output), `SCRUB.json` (the box's paths written as placeholders in the landed text), `SHA256SUMS`.

## 8. Departures, gaps and NOT RUN

- **m03's first run** (01:39:15-01:46 PST) computed every number above and then stopped writing `holdout-mesh.json` at a numpy integer the
  json module cannot encode. `m03_fit.py` was NOT edited: `m03b_rerun.py` re-ran it unchanged under a json encoder that writes numpy numbers
  as Python ones; `m03c_compare.py`: the re-run's 68 log lines equal the first run's but for their times, `fit-mesh.json` equal but for its
  stamps, the first run's partial file a prefix of the re-run's.
- **The snapshot after the declaration:** `s00c_snapshot_e214src.sh` added E214's registered source (arms.json and tiles, the same commit)
  to the read-only snapshot at about 01:59 PST, after the declaration's hash, because MM1-v3.2's energy code opens it at import and
  `compose_af4.py` imports that code; the time fit does not read it. So `work/lab-SNAPSHOT.txt` (the snapshot's record) gained that one
  line after its declared hash; every other declared input and all 13 declared code files read SAME at the freeze.
- **E224 arm B** had no committed reduction: this lane ran E208's registered reducer (b9e32618 / c3fc7883, the one E224's runbook step 13
  names) on the committed session (087f9baa), output in `out/inputs/` only, route c read as E220's frozen scorer reads arm B.
- **E222 and E224 read by this lane's copy of E220's frozen reader** with one change the lane's text binds: a run whose check of C failed is
  dropped (the frozen reader keeps it and flags R0). E222's and E224's verifiers ran beside this lane; no run of theirs was named faulty in a
  file this lane read.
- **Gaps:** two-stage only (MM1-v3.2's constants not refitted with the term: NOT RUN); the L2 is not filtered from the L3 stream (the walk's
  convention); the card's pool bases and L3 replacement are assumed; the per-link loads are REPORTED features only (assumed routes), no
  per-link term was fitted; the form cannot slow a subset (section 5); gemmL4x8x4's small masks are a named miss; the energy given t is
  MM1-v3.2's (the term moves no watt); no E226 point or file was chosen or read.
- **NOT RUN:** a joint refit; the counter's mean scored (the wall only); any blind test of this term (E226, registered after this freeze).

SPDX-License-Identifier: Apache-2.0
