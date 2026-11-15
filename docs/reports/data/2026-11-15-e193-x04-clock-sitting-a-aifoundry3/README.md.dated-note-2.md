# E193 sitting A's data README, dated note 2 (Sun 15 Nov 2026): the registered reducer's and the kit's checker's outputs, run by step 13 on the data commit `fe08ed67` at 11:13:49-51 PST, committed into this directory byte for byte with their printed lines; the measured, reduced prices; the data verifier's own re-derivation agrees; no reading changes

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `fe08ed67`, and note 1's five files
([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and the four beside it, `3a4a53b8`), which stay as committed too. Written on
aifoundry2 from 13:28 PST on Sun 15 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no post), by Q182's lane
`reduce-e193`, after E193's data verifier `verify-e193d` (12:24-12:52 PST: holds with fixes; one minor finding and three nits, all records
lines, none in a datum, a price or a check) and note 1 (`fix-e193d`, git 13:11:55 PST), which answers those findings; this note does not
repeat them. The kit's step 13 runs only after the data commit and leaves its outputs to a later commit: KIT.md's table of steps (line 92)
gives "its outputs to RB_OUT, committed by the records lane", and its script
([`rb/s24_reduce_e193.sh`](../../../../tools/claims-v3/e193/rb/s24_reduce_e193.sh), lines 8-10) says "the records lane commits them beside
the data in a later commit". README.md says the same (lines 26-27, and its "Next", lines 185-188: "a later lane commits them beside this
directory, with this README's reduced prices in a dated note"), and note 1 names `x04-e193-A.json` and `checks-e193-A.json` as the files
the records lane commits into this directory after it. This lane is that later lane. This note commits both outputs byte for byte, with
the two programs' printed lines, states the measured, reduced prices and the checks' words as printed, and sets the data verifier's
figures beside them; E193.md 7 (line 233) lists these prices, per arm, per fit and per train, with their SEs and the checks of section 8,
as what E193 publishes. **No number, price, check, verdict or gate reading changes, and nothing is scored. The forecasts stay sealed: no
forecast number is here, and nothing here scores E193 against them; the model session scores them privately against these published
prices.** Interpreter: `/usr/bin/python3` 3.12.3 with the system's numpy 1.26.4, on aifoundry2. Labels: **registered** (E193.md and the
kit as committed), **measured** (the session's committed records, and the registered reducer's prices from them), **desk check of code**
(this lane's re-run and the verifier's figures).*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`x04-e193-A.json`](x04-e193-A.json) | the registered reducer's output ([`reduce_x04.py`](../../../../tools/claims-v3/e193/proposal/src/reduce_x04.py), registered in `b17d58a4` at `98bbc174...`, run unchanged; E193.md 7's `x04.json`, named `x04-e193-A.json` by step 13): 180 run records (passes 0-8, 20 a pass; pass 0, the registered warm-up, is in the file and in no mean) and 54 train records (6 a pass); the 16 arms' watts over idle on the board and the three rails with their denominators, the 6 trains' contrasts, the 4 fits, the rails' leakage slopes and the reducer's own check fields | 332,704 | `e1e536e8...` |
| [`checks-e193-A.json`](checks-e193-A.json) | the kit's checker's output ([`check_e193.py`](../../../../tools/claims-v3/e193/check_e193.py) `checks`, kitted in `45d45c12` at `1351df2d...`): E193.md 8's nine checks (check 2 has two items), each with its verdict and numbers | 2,336 | `095f8a8e...` |
| [`x04-e193-A.txt`](x04-e193-A.txt) | the reducer's printed lines (27): step 13's copy of the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 1,714 | `4dd28738...` |
| [`checks-e193-A.txt`](checks-e193-A.txt) | the checker's printed lines (11), copied byte for byte from the runbook's capture of that call | 399 | `26a0bb99...` |
| `README.md.dated-note-2.md` | this note | | |

[`SHA256SUMS-note2`](SHA256SUMS-note2) pins these five and `SHA256SUMS-note1`. `SHA256SUMS-note1` pins `README.md`, `SHA256SUMS` and note
1's four files, and `SHA256SUMS` the 28 collected files, so every file here is pinned but `SHA256SUMS-note2` itself.

## 2. When, where and on which commit the reducer and the checker ran

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder
RB_OUT for this sitting, and from the lab clone's own log of its HEAD:

- **Step 13** ([`rb/s24_reduce_e193.sh`](../../../../tools/claims-v3/e193/rb/s24_reduce_e193.sh) `A`, the kit's, `35afddd7...` in
  `SHA256SUMS-e193-kit`): Sun 15 Nov 2026, **11:13:49-11:13:51 PST**, on aifoundry2, in the lab clone with its HEAD at **`fe08ed67`**,
  this sitting's data commit (git 11:13:37 PST; pushed by 11:13:40 PST, when the lab's remote main read `fe08ed67`), which stayed the
  clone's HEAD until the next commit, `96ef447c`, at 12:20:41 PST.
- **Its gates**, the log's lines 69-73, 11:13:49-11:13:50, each rc 0: the data directory committed (the call names `fe08ed67` as the last
  commit touching it); the directory clean (no line); its `SHA256SUMS`, every entry (28 of 28 OK); the history check ("HISTORY OK": the
  registration `b17d58a4`, the kit `45d45c12`, nothing under `tools/claims-v3/e193` changed since); the reducer at its registered sha256
  (`98bbc174...`). The step then copied `x04/runs.jsonl` and unpacked `x04/telemetry.jsonl.gz` into RB_OUT and checked both against
  `session/MANIFEST.sha256` (the box's bytes); it stops with a gate exit otherwise, and its own line reads "x04/runs.jsonl and the
  unpacked x04/telemetry.jsonl equal the box's manifest's sha256".
- **The reducer**, line 74: `/usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py RB_OUT/e193-reduce-A/x04 --out
  RB_OUT/x04-e193-A.json`, rc 0 in 0.8 s, logged at 11:13:51 (the runner writes each line at the call's end). `x04-e193-A.json` was last
  written at 11:13:51.155, the runbook's capture of the reducer's printed lines at 11:13:51.192, and the step's copy of it,
  `x04-e193-A.txt`, at 11:13:51.208.
- **The checker**, line 75: `/usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks RB_OUT/x04-e193-A.json
  RB_OUT/e193-reduce-A/x04 --out RB_OUT/checks-e193-A.json`, rc 0 in 0.6 s, logged at 11:13:51; `checks-e193-A.json` was last written at
  11:13:51.833, its capture at 11:13:51.833. Line 75 is the log's last line (75 lines): nothing ran through the runbook in that folder
  after the checker.
- **The step's own last line**, which the card lane's log of the step holds after the captures: `[s24_reduce_e193] reduced sitting A:
  RB_OUT/x04-e193-A.json and checks-e193-A.json (CHECKS READ: 1 PASS, 2 NOT COMPUTED, 2 NOT COMPUTED, 3 FLAGGED, 4 REPORTED, 5 REPORTED, 6
  FAIL, 7 REPORTED, 8 REPORTED, 9 REPORTED); the records lane commits them beside the data`. `runbook.log` holds each call's line, not its
  output; the runbook's bounded runner (v3.1's `rb_run.py`, through the k6 runbook's `rb_common.sh`) writes each call's stdout and stderr,
  as they come, to that call's capture file, and the two printed-line files here are the step's sixth and seventh captures (the sixth
  through step 13's copy).
- **The inputs it read** (re-checked by this lane): the two files in RB_OUT are, byte for byte, this directory's `x04/runs.jsonl` (2,808
  launch records) and `x04/telemetry.jsonl.gz` unpacked (24,771 samples), as committed in `fe08ed67`, and each equals its entry in
  `session/MANIFEST.sha256`.
- **The code as registered and kitted:** `reduce_x04.py` (`98bbc174...`, in `SHA256SUMS-e193-registration`), `check_e193.py`
  (`1351df2d...`), `rb/s24_reduce_e193.sh` (`35afddd7...`) and `rb/rb_e193.sh` (`0ca8b83f...`, all three in `SHA256SUMS-e193-kit`) are the
  same at the kit `45d45c12`, at both data commits and at LAB's HEAD as this note was written (`2d0fe517`): `tools/claims-v3/e193` is the
  tree `431bee42...` at all of them, and no commit since the kit touches it.
- **The interpreter:** `/usr/bin/python3` 3.12.3 on aifoundry2, isolated (`-I -B`), with the system's numpy 1.26.4 (the reducer imports
  numpy; the checker is standard library but for check 8, where it loads the registered reducer by path). E193.md 7 (line 231) and KIT.md
  (line 17) name the same interpreter and numpy for the desk, and README.md records the interpreter.
- **Re-run since, at the desk, on the committed bytes** (a desk check of code): by this lane at 13:20:53-13:20:55 PST (both sittings),
  from a fresh extract of `fe08ed67`'s own tree (`tools/claims-v3/e193` and this directory, from git's objects), the input built as step
  13 builds it (2 of 2 against the manifest), run with the runbook's interpreter and flags, from the tree's top with the same paths and
  output names, in the round's CPU slot with no device node reachable: reducer rc 0 in 0.8 s, checker rc 0 in 0.6 s; `x04-e193-A.json` and
  `checks-e193-A.json` byte-equal, and each program's printed lines byte-equal to its capture. The runs wrote nothing into the extract.

## 3. The measured, reduced prices

From [`x04-e193-A.json`](x04-e193-A.json), generated from the file, not typed. **Measured:** the registered reducer's prices from the
session's committed records; watts over idle on the board meter (12 V input) with the lab's idle law taking out the warmer burst's extra
leakage, and the minion rail's fitted level over idle; mean ± SE over the 8 measured passes (1-8; pass 0, the registered warm-up, is in
the file and in no mean). The reducer's printed lines (`x04-e193-A.txt`) give the same figures to three places; the SRAM and NoC rails,
the electrons, the wakes a second and each run's own record are in the file.

**Records:** 180 runs (20 a pass) and 54 train records (6 a pass), none dropped by a launch or by the clock (checks 4 and 5: 0 and 0;
trains not ok 0); the dip rule dropped 1 board reading (check 8). Rails' leakage slopes, fitted to this session's idle windows: minion
0.0748, SRAM 0.0205, NoC 0.0299 W per C.

**The arms** (`x04-e193-A.json` > `arms`; pJ per worker minion-cycle = W over idle / worker minion-cycles a second):

| arm | n | board: W over idle | board: anchor-detrended | minion rail: W over idle | pJ per worker minion-cycle, board / minion rail | slots a hart-cycle | awake fraction |
|---|---|---|---|---|---|---|---|
| `spin2` | 40 | 2.451 ± 0.019 | 2.451 | 2.160 ± 0.005 | 4.133 / 3.643 | 0.3474 | - |
| `tk_s2` | 8 | -0.006 ± 0.009 | -0.017 | 0.007 ± 0.003 | - (no worker minion-cycles) | 0.0000 | - |
| `tk_s11` | 8 | 0.013 ± 0.010 | 0.016 | 0.028 ± 0.003 | - (no worker minion-cycles) | 0.0000 | - |
| `tk_s21` | 8 | 0.075 ± 0.010 | 0.028 | 0.049 ± 0.005 | - (no worker minion-cycles) | 0.0000 | - |
| `tk` | 8 | 0.091 ± 0.017 | 0.085 | 0.074 ± 0.003 | - (no worker minion-cycles) | 0.0000 | - |
| `tk_l100` | 8 | 0.100 ± 0.011 | 0.095 | 0.080 ± 0.004 | - (no worker minion-cycles) | 0.0000 | - |
| `tk_l200` | 8 | 0.091 ± 0.010 | 0.096 | 0.079 ± 0.005 | - (no worker minion-cycles) | 0.0000 | - |
| `wait2` | 8 | 0.092 ± 0.012 | 0.087 | 0.078 ± 0.002 | 0.156 / 0.132 | 0.0000 | - |
| `duty33` | 8 | 0.890 ± 0.012 | 0.889 | 0.793 ± 0.005 | 1.501 / 1.338 | 0.1271 | 0.3308 |
| `duty67` | 8 | 1.690 ± 0.035 | 1.715 | 1.551 ± 0.012 | 2.850 / 2.615 | 0.2580 | 0.6709 |
| `duty100` | 8 | 2.618 ± 0.048 | 2.638 | 2.407 ± 0.012 | 4.416 / 4.061 | 0.3848 | 0.9990 |
| `duty33f` | 8 | 0.995 ± 0.016 | 1.014 | 0.878 ± 0.003 | 1.678 / 1.480 | 0.1405 | 0.3562 |
| `duty33k` | 8 | 1.295 ± 0.037 | 1.318 | 1.146 ± 0.007 | 2.184 / 1.933 | 0.1860 | 0.4421 |
| `w7` | 8 | 0.603 ± 0.030 | 0.645 | 0.536 ± 0.007 | 4.501 / 4.000 | 0.3460 | - |
| `w15` | 8 | 1.233 ± 0.034 | 1.259 | 1.058 ± 0.011 | 4.297 / 3.689 | 0.3460 | - |
| `w23` | 8 | 1.822 ± 0.041 | 1.863 | 1.623 ± 0.009 | 4.141 / 3.689 | 0.3460 | - |

**The trains** (`x04-e193-A.json` > `trains`; segments 0 and 3 are A, 1 and 2 are B; the contrast is mean(B) - mean(A), leakage-corrected per segment, no idle subtraction):

| train | n | board: B - A, W | minion rail: B - A, W | slots a hart-cycle by segment, 0 / 1 / 2 / 3 |
|---|---|---|---|---|
| `tr_tk_spin1` | 8 | +1.501 ± 0.035 | +1.295 ± 0.009 | 0.0000 / 0.3884 / 0.3884 / 0.0000 |
| `tr_spin1_spin2` | 8 | +0.830 ± 0.028 | +0.808 ± 0.007 | 0.3884 / 0.3466 / 0.3474 / 0.3884 |
| `tr_tk_stall2` | 8 | +0.283 ± 0.013 | +0.255 ± 0.003 | 0.0000 / 0.0071 / 0.0071 / 0.0000 |
| `tr_packed_spread` | 8 | +0.059 ± 0.005 | +0.045 ± 0.004 | 0.3460 / 0.3480 / 0.3478 / 0.3456 |
| `tr_faddps_fadds` | 8 | -0.014 ± 0.028 | +0.054 ± 0.015 | 0.3471 / 0.3472 / 0.3473 / 0.3470 |
| `tr_spread_cluster` | 8 | -0.506 ± 0.025 | -0.402 ± 0.006 | 0.3468 / 0.3472 / 0.3472 / 0.3468 |

**The fits** (`x04-e193-A.json` > `fits`; board W over idle; each a straight line by least squares through its points):

| fit | through | x | slope | intercept | residuals, W |
|---|---|---|---|---|---|
| `tk_shires` | `tk_s2`, `tk_s11`, `tk_s21`, `tk` | launched shires 2, 11, 21, 32 | 3.4938 mW a shire | -0.01442 W | +0.0019, -0.0111, +0.0161, -0.0068 |
| `tk_launches` | `tk_l100`, `tk_l200`, `tk` | launches a second 9.855, 4.963, 2.491 | 1.4085 mW per launch a second | +0.08573 W | +0.0007, -0.0020, +0.0013 |
| `duty` | `wait2`, `duty33`, `duty67`, `duty100` | awake fraction 0.0000, 0.3308, 0.6709, 0.9990 | 2.5096 W per unit of awake fraction | +0.06748 W | +0.0249, -0.0073, -0.0608, +0.0432 |
| `workers` | `w7`, `w15`, `w23`, `spin2` | workers a shire 7, 15, 23, 31 | 76.687 mW per worker a shire | +0.07012 W | -0.0042, +0.0121, -0.0118, +0.0038 |

Off the duty line: `duty33f` +0.0335 W, **115.64 pJ a wake**; `duty33k` +0.1179 W, **101.77 pJ a wake** (the residual over the arm's wakes
a second).

## 4. E193.md 8's checks, as the checker printed them

[`checks-e193-A.txt`](checks-e193-A.txt), verbatim:

```
check 1 spin2: PASS
check 2 faddps_p1: NOT COMPUTED
check 2 fsgnjs_p1: NOT COMPUTED
check 3 anchor drift: FLAGGED
check 4 device ok: REPORTED
check 5 clock: REPORTED
check 6 duty linear: FAIL
check 7 nulls: REPORTED
check 8 dip rule: REPORTED
check 9 stall2: REPORTED
CHECKS READ: 1 PASS, 2 NOT COMPUTED, 2 NOT COMPUTED, 3 FLAGGED, 4 REPORTED, 5 REPORTED, 6 FAIL, 7 REPORTED, 8 REPORTED, 9 REPORTED
```

Each check's numbers (`checks-e193-A.json` > `checks`):

| check | the numbers | verdict |
|---|---|---|
| 1 | `spin2` 2.4512 W against the catalogue's two-hart no-op row, 2.496 W scaled by 992/1024 = 2.418 W (+1.4 %, inside the registered 15 %) | PASS |
| 2 | `faddps_p1` and `fsgnjs_p1` are sitting B's arms (block C); the checker: "faddps_p1 has no measured value", "fsgnjs_p1 has no measured value". Sitting B's note 2 gives both | NOT COMPUTED (x2) |
| 3 | 16 of 32 pass/block boundaries above 0.1 W: 1/T, 2/T, 3/S, 3/D, 3/T, 4/T, 5/S, 5/T, 6/S, 6/D, 7/S, 7/D, 7/W, 7/T, 8/S, 8/T (note 1 § 5 reads them by the block crossed, post hoc) | FLAGGED |
| 4 | runs 180, trains 54; dropped by a launch not ok 0, trains not ok 0 | REPORTED |
| 5 | dropped by the clock 0 | REPORTED |
| 6 | the duty line's residuals +0.0249, -0.0073, -0.0608, +0.0432 W (each under 0.05 W passes) | FAIL |
| 7 | `wait2 - tk` +0.0018 W, 95 % interval [-0.0381, +0.0417] W; `duty33f` off the duty line +0.0335 W, `duty33k` +0.1179 W | REPORTED |
| 8 | 1 reading dropped (pass 5: 1; a train segment) of 16,818 window readings (busy 6,328, idle before 4,469, idle after 4,497, train segments 1,524) | REPORTED |
| 9 | `stall2`'s divides a hart-cycle 0.0071 against `spin2`'s slots a hart-cycle 0.3474: "a stalled pipeline"; the threshold, "less than half of the session's spin2 rate (E193.md 8, the lab's reading)" | REPORTED |

E193.md 8 (line 259): "Each check is reported PASS or FAIL (the nulls with their values and intervals) beside the prices; a failed check
removes no datum beyond the reducer's own run gates (4, 5, 8)." **Registered verdicts, unchanged.** The checker's line, as the step's last
line repeats it: `CHECKS READ: 1 PASS, 2 NOT COMPUTED, 2 NOT COMPUTED, 3 FLAGGED, 4 REPORTED, 5 REPORTED, 6 FAIL, 7 REPORTED, 8 REPORTED,
9 REPORTED`.

## 5. Beside verify-e193d's independent re-derivation

`verify-e193d` (Sun 15 Nov 2026, 12:24-12:52 PST) re-derived the reduction from this directory's committed raw files, taken from
`fe08ed67`, with its own code, written from E193.md 7 and the reducer's stated rules, importing nothing from the kit's reducer, runner or
checker (`/usr/bin/python3` 3.12.3, numpy 1.26.4), and checks 8 and 9 with its own code too. Its figures are a desk check of code. It
compared its output with the same bytes as `x04-e193-A.json` (sha256 `e1e536e8...`) field by field: **6,619 fields** (every run record,
every train record, every arm, train and fit, the rails' leakage slopes and the reducer's checks), **largest relative difference 8.6e-8**,
every difference traced to the reducer holding epoch seconds as float64 in each run's `wall_s`, and every check verdict the same. It also
ran README.md's own re-make commands from git's objects: `x04.json` and the printed lines came out byte-equal to step 13's. Each pair
below is **the reducer / verify-e193d**, generated from `x04-e193-A.json` and from the verifier's own output file (`mine-A-float.json`,
sha256 `445adc11...`, kept outside the repository), not typed. Over the 400 numeric fields of the arms, the trains, the fits and the
rails' leakage slopes that both files carry (this lane's comparison), the largest relative difference is 8.6e-08
(`fits.tk_launches.residuals_w[0]`).

| arm or train | board: the reducer | board: verify-e193d | minion rail: the reducer | minion rail: verify-e193d |
|---|---|---|---|---|
| `spin2` | 2.451216 ± 0.018717 | 2.451216 ± 0.018717 | 2.160157 ± 0.005103 | 2.160157 ± 0.005103 |
| `tk_s2` | -0.005524 ± 0.008817 | -0.005524 ± 0.008817 | 0.007176 ± 0.003071 | 0.007176 ± 0.003071 |
| `tk_s11` | 0.012868 ± 0.009712 | 0.012868 ± 0.009712 | 0.028476 ± 0.002751 | 0.028476 ± 0.002751 |
| `tk_s21` | 0.075025 ± 0.010151 | 0.075025 ± 0.010151 | 0.049209 ± 0.004908 | 0.049209 ± 0.004908 |
| `tk` | 0.090545 ± 0.016712 | 0.090545 ± 0.016712 | 0.073592 ± 0.002603 | 0.073592 ± 0.002603 |
| `tk_l100` | 0.100272 ± 0.011385 | 0.100272 ± 0.011385 | 0.079826 ± 0.003950 | 0.079826 ± 0.003950 |
| `tk_l200` | 0.090761 ± 0.009727 | 0.090761 ± 0.009727 | 0.078872 ± 0.004836 | 0.078872 ± 0.004836 |
| `wait2` | 0.092351 ± 0.011610 | 0.092351 ± 0.011610 | 0.078142 ± 0.001885 | 0.078142 ± 0.001885 |
| `duty33` | 0.890256 ± 0.012037 | 0.890256 ± 0.012037 | 0.793221 ± 0.004968 | 0.793221 ± 0.004968 |
| `duty67` | 1.690414 ± 0.034535 | 1.690414 ± 0.034535 | 1.550593 ± 0.011634 | 1.550593 ± 0.011634 |
| `duty100` | 2.617757 ± 0.048138 | 2.617757 ± 0.048138 | 2.407298 ± 0.011850 | 2.407298 ± 0.011850 |
| `duty33f` | 0.994867 ± 0.016088 | 0.994867 ± 0.016088 | 0.877625 ± 0.003247 | 0.877625 ± 0.003247 |
| `duty33k` | 1.294889 ± 0.036675 | 1.294889 ± 0.036675 | 1.146389 ± 0.006971 | 1.146389 ± 0.006971 |
| `w7` | 0.602756 ± 0.030191 | 0.602756 ± 0.030191 | 0.535697 ± 0.007483 | 0.535697 ± 0.007483 |
| `w15` | 1.232567 ± 0.034107 | 1.232567 ± 0.034107 | 1.058094 ± 0.011185 | 1.058094 ± 0.011185 |
| `w23` | 1.822129 ± 0.040971 | 1.822129 ± 0.040971 | 1.623060 ± 0.009255 | 1.623060 ± 0.009255 |
| `tr_tk_spin1` (B - A) | 1.501298 ± 0.034650 | 1.501298 ± 0.034650 | 1.295384 ± 0.009279 | 1.295384 ± 0.009279 |
| `tr_spin1_spin2` (B - A) | 0.830322 ± 0.027890 | 0.830322 ± 0.027890 | 0.807542 ± 0.006896 | 0.807542 ± 0.006896 |
| `tr_tk_stall2` (B - A) | 0.282768 ± 0.013159 | 0.282768 ± 0.013159 | 0.255002 ± 0.003190 | 0.255002 ± 0.003190 |
| `tr_packed_spread` (B - A) | 0.059107 ± 0.005047 | 0.059107 ± 0.005047 | 0.044723 ± 0.003986 | 0.044723 ± 0.003986 |
| `tr_faddps_fadds` (B - A) | -0.013981 ± 0.028089 | -0.013981 ± 0.028089 | 0.053691 ± 0.014995 | 0.053691 ± 0.014995 |
| `tr_spread_cluster` (B - A) | -0.505585 ± 0.025184 | -0.505585 ± 0.025184 | -0.401731 ± 0.005814 | -0.401731 ± 0.005814 |

| fit | the reducer: slope, intercept | verify-e193d: slope, intercept |
|---|---|---|
| `tk_shires` | 0.0034938 W, -0.0144193 W | 0.0034938 W, -0.0144193 W |
| `tk_launches` | 0.00140849 W, 0.0857334 W | 0.00140849 W, 0.0857334 W |
| `duty` | 2.50963 W, 0.0674805 W | 2.50963 W, 0.0674805 W |
| `workers` | 0.0766868 W, 0.0701177 W | 0.0766868 W, 0.0701177 W |
| `duty`: pJ a wake, `duty33f` / `duty33k` | 115.6391 / 101.7736 | 115.6391 / 101.7736 |

The verifier's own checks, from its file: check 1 PASS (2.451216 W against 2.418); check 3 16 of 32 boundaries flagged; check 4 runs 180,
trains 54, dropped 0 and 0; check 6 FAIL; check 7 `wait2 - tk` +0.001806 W, [-0.038079, +0.041690]; check 8 1 reading dropped; check 9
0.0071 against 0.347374, "a stalled pipeline". **Agree or differ: they agree.** Every figure above is the same to the places shown, and
the verdicts are the same: `CHECKS READ: 1 PASS, 2 NOT COMPUTED, 2 NOT COMPUTED, 3 FLAGGED, 4 REPORTED, 5 REPORTED, 6 FAIL, 7 REPORTED, 8
REPORTED, 9 REPORTED`.

## 6. Checks before the commit

- The four copied files as staged are byte-equal (`cmp`) to the card lane's RB_OUT files and to the runbook's captures of the two calls,
  and to this lane's re-run (§ 2).
- In a copy of this directory with the six new files: `SHA256SUMS` 28 of 28, `SHA256SUMS-note1` 6 of 6 and `SHA256SUMS-note2` 6 of 6
  entries OK; 41 files, every one in a list but `SHA256SUMS-note2`.
- The desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the round's folders forbidden) read the six new files with 0 hits,
  and a login check found no home path, no login, no e-mail address and no holder line in them or in this commit's subject and body.
- The public-text scan (the lab's `sanitize_extracts.py`, its fixed list and the box's local table, and the round's lists of private,
  vendor, process, access and mechanism words) found nothing in the six new files or in this commit's subject and body, but four digits
  that one of the round's patterns lists, inside a longer number in `x04-e193-A.json` (a run's worker minion-cycles a second, kept byte
  for byte), read as no hit.

## Re-make it

From the top of the repository, nothing here opens a device; set R to an empty folder outside the repository (the first line), then run
the rest as they stand. They build step 13's input from this directory, run the registered reducer and the kit's checker with step 13's
output names, and compare the four copied files byte for byte (a re-run under `/usr/bin/python3` 3.12.3 with numpy 1.26.4 gives the same
bytes):

    D=docs/reports/data/2026-11-15-e193-x04-clock-sitting-a-aifoundry3; R=<an empty folder outside the repository>
    mkdir -p "$R/x04" && cp "$D/x04/runs.jsonl" "$R/x04/" && gzip -dc "$D/x04/telemetry.jsonl.gz" > "$R/x04/telemetry.jsonl"
    /usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py "$R/x04" --out "$R/x04-e193-A.json" > "$R/x04-e193-A.txt" 2>&1
    /usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks "$R/x04-e193-A.json" "$R/x04" --out "$R/checks-e193-A.json" > "$R/checks-e193-A.txt" 2>&1
    for f in x04-e193-A.json x04-e193-A.txt checks-e193-A.json checks-e193-A.txt; do cmp "$R/$f" "$D/$f" && echo "$f: the same bytes"; done
    (cd "$D" && sha256sum -c SHA256SUMS-note2 && sha256sum -c SHA256SUMS-note1 && sha256sum -c SHA256SUMS)

## Departure (dated Sun 15 Nov 2026)

No post in the lab's channel for this commit: the owner's standing waiver of the post, his words at 10:22:36 PST (note 1 of sitting A, §
1), stands, and this lane made none.

## What does not change

Every reading, verdict, gate, stop and figure of `README.md`, note 1 and their files stands; this note adds the reducer's and the
checker's outputs beside them and reads them, and changes nothing. The reducer and the checker read none of this note's files. This lane
reached no box, opened no device and changed no committed file. Sitting B's note 2 commits that sitting's outputs into its own directory
in the same commit.

SPDX-License-Identifier: Apache-2.0
