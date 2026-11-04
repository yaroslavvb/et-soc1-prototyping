# Q141(t2): the convergence rule's 243-point step, and cal_third_b21's fallback, registered before any 243-point count

*Wed 4 Nov 2026 (week 45), about 13:30 PST, desk only: no card is claimed, no device command is sent, no lab box, Discord, Modal or
archive is touched. Written and committed **before any count at the 243-point level exists**. It answers the Q141 final critic's
`desk_next` 4 (Q141(t)'s 243-point step for the 8 calibration tiles above the bound, all bit 20 or 21, checked first against one
Intel point, **with cal_third_b21's fallback registered first**), under the Q140 final critic's open **rank 4** (the bench's
counting against a missing single-bit price), for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6** (a new kind's power,
predicted blind).*

**What it does not touch.** No frozen prediction, price, card term, band, rule or verdict changes. M9 (`1f244140`) stays as
frozen, with its three-point predictions primary; Q141(t)'s arm stays at 27 points (`67d5e44f`, amended by A1 in `c31e7ae3`);
RECOUNT-RULE.md (`b4444dd4`) and its code stay as registered. Everything here is reported only.

## 0. What it descends from, and what exists now

- **The convergence rule:** Q140(m)'s [RECOUNT-RULE.md](../2026-11-04-q140m-m9/recount-rule/RECOUNT-RULE.md) (`b4444dd4`,
  01:53:26 PST) and its code `recount_rule.py`: the launch points (section 1), e(N) at M9's frozen float prices (section 2), the
  bound e(N) ≤ 0.10 W (section 3), the stepping, the cap N = 243 and N\* (section 4). Its 27-point pilot is `b85ca0f9`.
- **Q141(t)'s step 3**, registered in [`REGISTRATION.md`](REGISTRATION.md) section 4 (`0830f65b`) and committed as
  [`step81/`](step81/README.md) (`9c7ae1f2`, 11:23:07 PST): at 81 points **8 of the 16 calibration tiles are above the bound**,
  all bit 20 or 21. N\* is not yet determined. e(27)/e(81) has median 1.75, against the 1/√N law's 1.73
  ([`step81/README.md.dated-note.md`](step81/README.md.dated-note.md), `c31e7ae3`).
- **No 243-point count exists.** Checked at about 13:25 PST:
  - `git log origin/main` shows no `step243/` directory and no `counts-cal243-*` file;
  - this lane's only bench counts so far are the build checks of section 2, at points already committed (the nine- and 81-point
    sets).

## 1. The step

**Tiles (8)**, the ones above the bound at 81 points. They are counted in this order: cal_third_b21 first, then by e(81),
largest first.

| order | tile | base word | bit | e(81), W |
|---:|---|---|---:|---:|
| 1 | `fp32.cal_third_b21` | 0x3EAAAAAB (1/3) | 21 | 0.221 |
| 2 | `fp32.cal_pi_b21` | 0x40490FDB (π) | 21 | 0.154 |
| 3 | `fp32.cal_third_b20` | 0x3EAAAAAB | 20 | 0.147 |
| 4 | `fp32.cal_w67_b21` | 0x3FBBC9E4 | 21 | 0.140 |
| 5 | `fp32.cal_w79_b21` | 0x3FBD207C | 21 | 0.120 |
| 6 | `fp32.cal_w67_b20` | 0x3FBBC9E4 | 20 | 0.115 |
| 7 | `fp32.cal_w79_b20` | 0x3FBD207C | 20 | 0.108 |
| 8 | `fp32.cal_pi_b20` | 0x40490FDB | 20 | 0.1004 |

**Points.** Each tile gets the 162 points of N = 243 that N = 81 does not hold, 1,296 points in all.
- RECOUNT-RULE.md section 1 gives n_j = int(ops (2j + 1) / 486), j = 0-242, with ops = 0.5 × 600e6 / 546.
- N = 81's points are exactly the points with j ≡ 1 (mod 3). The driver stops if that nesting fails.
- The new points come in two parts of 81 each: part 1 is j ≡ 0 (mod 3), part 2 is j ≡ 2 (mod 3). Both parts span the whole
  launch.
- That makes 16 chunks, one part of one tile each, in the order above, part 1 before part 2.

**The bench.** It is Q133(b)'s bench, `rtl-sim/fma_toggle_v2` (`vpu_top`), the build behind every count since Q140(m).
- **Sources.** Its four inputs that are not built hash as Q140(m)'s `bench-check/bench-sha256.txt`: the three `maps/*.map` and
  `run_kinds.py`. `run_kinds.py` is unchanged.
- **The build.** It is made on the mini from the same open RTL: core-et `b38a1a31`, unmodified, its `rtl/` and `dv/inc/`. The
  compiler is Verilator 5.052, as on the Intel, with the Makefile's `-fno-dfg` kept.
- **The driver** is [`step243/bench_243.py`](step243/bench_243.py), committed with this file. `bench_s7.py` stays as committed: its
  build check pins the Intel's x86_64 binaries, which an arm64 build cannot match. So `bench_243.py` checks the four inputs
  against `bench-sha256.txt` and the binaries against the build record of section 2 (B1). It checks each tile's bytes against
  `cal-tiles.json`, and C at every point (`check_mismatch`). A mismatch stops the rule's code (`main()`).
- **Where.** It runs on the mini (arm64 macOS), at 4 jobs, each chunk under a memory cap (6 GB) and a time cap, under the owner's
  rule of 4 November 2026 that batch work runs off the Intel. The Intel runs one check point (B3) on one core at nice 10.
- **If the step cannot finish** (the mini lost, or no time), the chunks not counted are named. Their tiles read "not counted to
  243" (section 3), and nothing is extrapolated in their place.

## 2. The build checks: a count from the mini is quoted only after all three pass

- **B1, done before this file (13:16-13:17 PST).** The two builds read the same files, byte for byte.
  - Verilator records every file a build reads, with a content hash (`obj_vpu/Vtb__verFiles.dat`).
  - 156 of 156 files are identical across the two builds: the 153 RTL and bench files and Verilator's own three
    ([`step243/build-record-mini.json`](step243/build-record-mini.json),
    [`step243/build-record-intel.json`](step243/build-record-intel.json)).
  - The four inputs hash as `bench-sha256.txt`, and both builds carry `-fno-dfg`.
  - The command lines differ only in the Intel's `-MAKEFLAGS CXX=… LINK=…` override, which its conda-forge Verilator needs.
  - The binaries differ (arm64 against x86_64), as they must.
- **B2, done before this file (13:17:47-13:18:20 PST).** The mini's build re-counted 16 points already committed: the standard
  point n0 457875 and the 81-point step's n0 403608, for each of the 8 tiles. **16 of 16 are identical in every field** to the
  Intel-built committed counts ([`step243/check-b2-mini.json`](step243/check-b2-mini.json), by
  [`step243/compare_points.py`](step243/compare_points.py); counts in `step243/counts-b2-mini.json`). That took 31.9 s at 4 jobs,
  about 8 s a point per worker.
- **B3, after this file and before any chunk.** One new point of N = 243 is counted on both builds: `fp32.cal_third_b21` at
  n0 272464 (j = 120, in part 1).
  - The Intel's hashed build counts it on one core at nice 10, and the mini's build counts it too.
  - The two must be identical in every field. Otherwise no count from the mini is quoted, and the step stops, reported as partial.
  - Part 1 of cal_third_b21 counts the same point again on the mini, and that count must equal B3's: the bench is deterministic.

## 3. What the 243-point counts decide, and by what rule

**The rule** is `recount_rule.py`'s `main()`, unchanged (RECOUNT-RULE.md sections 2-4).
- It runs through [`step243/run_recount_rule_243.py`](step243/run_recount_rule_243.py) on the committed counts at 9, 27 and 81
  points and this step's 16 chunk files. Its output directory is pointed at `step243/`.
- e(N) = max(se_sample, se_interleaved) at M9's frozen float prices, and the bound is e(N) ≤ 0.10 W.
- The wrapper adds nothing to the rule. Its self-check (T0 of [`step243/selftest-step243.txt`](step243/selftest-step243.txt))
  runs `main()` on the committed counts alone, and that rewrites `step81/recount-rule.json` and `.txt` byte for byte.

**Each of the 8 tiles** gets exactly one of three outcomes:

| outcome | when | what it means |
|---|---|---|
| **met at 243** | e(243) ≤ 0.10 W | its first N meeting the bound is 243 |
| **above the bound at the cap** | e(243) > 0.10 W | section 4's fallback applies to it |
| **not counted to 243** | the step was cut short | it keeps its 81-point figures and is named |

**N\*:**
- **If all 8 meet the bound at 243**, then N\* = 243, which `main()` prints.
- **If any tile is above the bound at the cap**, `main()` prints "not yet determined". At the cap that means **N\* is not reached by
  uniform points**.
  - There is no N = 729 step, because 243 is the rule's cap.
  - `main()`'s next-step line ("count the k tiles not yet meeting the bound at 3 x their N") does not apply to such a tile.
  - `summary243.json` writes "not reached by uniform points at the cap (243)".
- **If any tile is not counted to 243**, N\* stays "not yet determined: the step is incomplete".

**The projections, written before the data.**
- By the 1/√N law, cal_third_b21's e(243) is about 0.221 / √3 = 0.128 W, above the bound; the law's N for it is 395.
- The other seven project at 82-192 points, under the cap.
- The rule decides, never the projection. A tile under the bound at 243 has met it even if it was projected above, and the reverse
  holds too.

**The self-test** ([`step243/selftest_step243.py`](step243/selftest_step243.py), PASS) runs the summary on three synthetic worlds
built from step81's committed output, never from counts: all 8 met; cal_third_b21 above the bound at the cap; and one tile
counted only to 81. Each gives the outcome and N\* above.

## 4. What follows if they do not settle it: the fallback

RECOUNT-RULE.md section 4 reads: *"If a tile does not meet the bound at 243, uniform launch points cannot give its launch average to
0.10 W at an affordable cost. The next model then either carries that tile's e(N) as a known error on rows like it, or registers
another estimator before using one, for instance points stratified by C's state computed in software (`accum.c` gives C at any op
index for free)."*

This file chooses now, before any 243-point count, for cal_third_b21 and for any other tile above the bound at the cap. **F1
applies at once. F2 is the only way past F1, and only by its own registration.**

### 4.1 F1, the known error: applied at once, mechanically

- **The launch average.** It is the tile's 243-point mean, carried with **e(243) as its known 1-s.e. counting error**, at M9's
  frozen prices. `summary243.json` writes both, as `F1_known_counting_error`.
- **No uniform count beyond 243** is made for it. The cap holds.
- **The recount's cap.** RECOUNT-RULE.md section 6 counts each recount tile "never beyond N\*".
  - With N\* not reached, the recount's cap is the rule's own cap, N = 243.
  - A recount tile still above the bound there is reported with its e(243), as section 6 already says for e(N\*).
  - If N\* = 243, the cap is the same 243.
- **"Rows like it"** (section 4's words). A row whose own tile is above the bound at its last counted N carries that tile's own
  e(N) as a known counting error, in quadrature with the row's other errors.
  - The next model's registration says how it uses that error (weights, bands) before its fit.
  - This file binds only that the error is carried. It is never dropped, and never replaced by a smaller figure.
- **What F1 leaves alone.** The arm stays at 27 points. M9's three-point predictions stay primary. No band, card term or price
  moves.

### 4.2 F2, a stratified estimator: the only way past F1, not run here

A stratified estimate replaces F1's figure on a tile only through **its own registration**. That registration must be committed
before any count it adds and before it is applied to any tile, and it must hold all four of these points.

1. **Strata from C's state alone.** They are computed in software, by `accum.c` from the tile's bytes and the op index, never from
   a bench count, and fixed in that file. A stratum's weight W_h is its exact share of the launch's op indices 0 … ops − 1, also
   computed in software.
   - C's binade alone is too coarse. A look at the committed 81 points, with no new count, shows the spread inside one binade
     (sd 1.2-1.9 W) about as large as over the whole launch.
   - On cal_third_b21 the points sit near 4 W or near 7.8 W, so a useful stratum must separate those two levels, from C's bits.
2. **The estimate and its error.** The estimate is Σ_h W_h ȳ_h over bench points inside each stratum: this step's points, the
   earlier uniform points, and points that registration names. Its error rule is written there, at least the stratified standard
   error √(Σ_h W_h² s_h² / n_h), with n_h ≥ 2 in every stratum. The bound stays 0.10 W.
3. **Validation before use, on all 16 calibration tiles.** On each tile, F2's estimate must agree with the uniform launch average at
   the tile's last counted N within **3 σ_d**. σ_d is the difference's standard error, computed by that registration with shared
   points counted. One miss means F2 is not used.
   - 3 σ_d, not 2: with 16 tiles, a 2σ test would fail a correct estimator about half the time (1 − 0.954^16 ≈ 0.53). At 3σ the
     rate is about 4%.
4. **The choice goes by errors, never by values.** F2's figure replaces F1's on a tile only if the validation passes and F2's own
   error on that tile is at most 0.10 W. Otherwise F1 stays.

Until such a registration is committed and its count has run, F1 holds.

## 5. The reported readings (registered here; no verdict)

[`step243/readings_243.py`](step243/readings_243.py) writes `readings-243.json` and `.txt`.

| reading | what it reports |
|---|---|
| **G1** | The 81-to-243 move on each tile: d = mean(81) − mean(243), against its expected spread under the rule's own model. z = d / √(e(81)² − e(243)²), since the 81 points are nested in the 243. If e(81) is a fair 1-s.e. error, z has rms about 1. |
| **G2** | e(81)/e(243) per tile against √3 = 1.73, with its range and median. |
| **G3** | The three-point count's error at 243 points (3pt − 243) per tile, at M9's frozen prices. |
| **G4** | The arm's one tile with a calibration twin, pool 7's `fp32.b_onebit_b20_pi` (byte for byte `fp32.cal_pi_b20`). It gives k243 = s × (3pt − 243) ± s × e(243) beside the arm's frozen k at 27 points and step81's reading at 81, with s = 1 on aifoundry3 and M9's card-1 scale on card 1. The arm stays as frozen. |
| **G5** | Pool 6's twin `fp32.b_onebit_b20_third` (twin `cal_third_b20`): M9's error with the 243-point average, `main()`'s own post hoc lines, copied. |

The summary also reports the bench time per point on the mini, and B3's result.

## 6. What it does to predicting power and heat

- **The term:** the bench's single-bit counting, which is the input of the next model's single-bit price, now at 243 points.
- **What it leaves alone:** no frozen prediction, price, card term, band or rule changes. M9 and the arm stay as frozen, and every
  hash list still passes.
- **What it makes known:**
  - how many uniform points a single-bit refit needs (N\*);
  - or which calibration tiles carry a known counting error, and how large it is.
  - Either way, a refit cannot fit the bench's quadrature as a price.
- **Heat:** through M7's law (dT = g × S, with g = 0.11855 °C/W on aifoundry3), a counting error of e moves the 4.5 s rise by
  g × e. That is about 0.015 °C for 0.128 W, too small to matter for these tiles' heat prediction.

## 7. Files

**Committed with this registration** (all new, in `step243/`):
- `bench_243.py`, the driver;
- `compare_points.py`, the field-by-field comparison;
- `run_recount_rule_243.py`, the rule's `main()` unchanged, plus the summary;
- `readings_243.py`, section 5's readings;
- `selftest_step243.py` with its output `selftest-step243.txt` (PASS);
- B1's records: `build-record-intel.json` and `build-record-mini.json`;
- B2's counts and comparison: `counts-b2-mini.json`, `counts-b2-mini-run.json` and `check-b2-mini.json`.

**Committed with the counts, afterwards:**
- B3's files;
- `counts-cal243-<tile>-p<k>.json` with each one's `-run.json` and log (16 chunks);
- `recount-rule.json` and `.txt`, `summary243.json` and `.txt`, `readings-243.json` and `.txt`;
- a README, results first.

The chunk names use tile = `third_b21`, `pi_b21`, `third_b20`, `w67_b21`, `w79_b21`, `w67_b20`, `w79_b20` and `pi_b20`, and
k = 1 or 2.
