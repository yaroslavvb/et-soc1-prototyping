# E192's data README, dated note 2 (Sat 14 Nov 2026): the registered reducer's and the section 7 checker's outputs, run on the data commit `a6e17e83` at 22:16:53-57 PST, committed beside it byte for byte with their printed lines; the measured, reduced prices; the data verifier's own re-derivation agrees

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `a6e17e83`, and note 1's five files
([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and the four beside it, `4e964246`), which stay as committed too. Written on
aifoundry2 from 23:11 PST on Sat 14 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no post), by Q179's lane
`reduce-e192`, after E192's data verifier `verify-e192d` (22:20-22:48 PST: holds with fixes, none of them in a datum, a price or a check)
and note 1 (`fix-e192d`, 23:09 PST). The kit's step 13 ([`KIT.md`](../../../../tools/claims-v3/e192/KIT.md), its table of steps: "the
registered reducer at `715fddaa...`, unchanged, on the committed bytes (the telemetry unpacked and checked against the session's manifest),
then `check_e192.py` (E192.md section 7, its thresholds and no other); no scoring") runs only after the data commit, and its script
([`rb/s24_reduce_e192.sh`](../../../../tools/claims-v3/e192/rb/s24_reduce_e192.sh)) leaves the two outputs to a later commit: "the records
lane commits them". README.md's "Next" says the same, and KIT.md section 9 puts the reducer's prices and the checks "after step 13 only
(its own commit)". E192.md section 6 lists the reducer's output and the checks' outcomes among what E192 publishes "in E192's data
commit"; the kit, committed before any datum, runs the reducer only on the committed bytes, after the data commit, and gives the prices
and the checks a commit of their own, so they come here, into E192's data directory, by a later commit: the kit's reading, stated before
any datum, recorded here. This lane is that later lane. This note commits both outputs byte for byte, with the two programs' printed lines,
states the measured, reduced prices and the checks' words as printed, and sets the data verifier's figures beside them. **No number,
price, check, verdict or gate reading changes, and nothing is scored. The forecasts stay sealed: no forecast number is here, and nothing
here scores E192 against them; the model session scores them privately against these published prices.** Interpreter: `/usr/bin/python3`
3.12.3 with the system's numpy 1.26.4, on aifoundry2. Labels: **registered** (E192.md and the kit as committed), **measured** (the
session's committed records, and the registered reducer's prices from them), **desk check of code** (this lane's re-run and the
verifier's figures).*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`intbits-e192.json`](intbits-e192.json) | the registered reducer's output ([`reduce_intbits.py`](../../../../tools/claims-v3/e192/proposal/src/reduce_intbits.py), registered in `a282aad6` at `715fddaa...`, unchanged; E192.md section 6's `intbits.json`, named `intbits-e192.json` by the kit's step 13): 324 run records (passes 0-8; the smoke's three runs are not among them), the 32 arms' energies over idle and contrasts on both meters, temperature-corrected and uncorrected, with their electrons, beta, and every ladder, corrected and uncorrected | 289,103 | `0a675627...` |
| [`checks-e192.json`](checks-e192.json) | the kit's checker's output ([`check_e192.py`](../../../../tools/claims-v3/e192/check_e192.py), kitted in `a6fe5c20` at `ceb99e7c...`): E192.md section 7's eight checks, each with its verdict and numbers, the passes used (1, 2, 3, 4, 5, 6, 7, 8) and the Python (`3.12.3`) | 4,223 | `bfe123cf...` |
| [`intbits-e192.txt`](intbits-e192.txt) | the reducer's printed lines (57), copied byte for byte from the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 4,259 | `d18f40e6...` |
| [`checks-e192.txt`](checks-e192.txt) | the checker's printed lines (9), copied the same way; the checker itself cuts each check's line at 300 characters (`check_e192.py` line 165), so check 7's line ends inside a number, as printed | 1,195 | `4ee4ca1b...` |
| `README.md.dated-note-2.md` | this note | | |

[`SHA256SUMS-note2`](SHA256SUMS-note2) pins these five. With `SHA256SUMS` (27 entries, unchanged) and `SHA256SUMS-note1` (6 entries),
every file here is pinned but `SHA256SUMS-note1` and `SHA256SUMS-note2` themselves.

## 2. When, where and on which commit the reducer and the checker ran

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder
RB_OUT, and from the lab clone's own log of its HEAD:

- **Step 13** ([`rb/s24_reduce_e192.sh`](../../../../tools/claims-v3/e192/rb/s24_reduce_e192.sh), the kit's, `d9168e61...` in
  `SHA256SUMS-e192-kit`): Sat 14 Nov 2026, **22:16:53-22:16:57 PST**, on aifoundry2, in the lab clone with its HEAD at **`a6e17e83`**, the
  data commit (made at 22:16:26 PST and pushed by 22:16:31), which stayed the clone's HEAD until the next commit (E193's registration,
  `b17d58a4`) at 22:17:08 PST.
- **Its gates**, the log's lines 77-79, each at 22:16:53 with rc 0: this directory's `run/runs.jsonl`, `run/telemetry.jsonl.gz` and
  `session/MANIFEST.sha256` tracked at HEAD (three lines); the directory clean (no line); the reducer at its registered sha256
  (`715fddaa...`). The step then unpacked `run/telemetry.jsonl.gz` and copied `run/runs.jsonl` and `run/marks.jsonl` into RB_OUT, and
  checked each of the three against `session/MANIFEST.sha256` (the box's bytes); it stops with a gate exit otherwise, and the log holds no
  stop line for the step.
- **The reducer**, line 80: `/usr/bin/python3 -I -B tools/claims-v3/e192/proposal/src/reduce_intbits.py RB_OUT/reduce-e192/run --out
  RB_OUT/intbits-e192.json`, rc 0 in 1.2 s, logged at 22:16:54 (the runner writes each line at the call's end). `intbits-e192.json` was last
  written at 22:16:54.508, beside the runbook's capture of the reducer's printed lines at 22:16:54.509.
- **The checker**, line 81: `/usr/bin/python3 -I -B tools/claims-v3/e192/check_e192.py RB_OUT/reduce-e192/run RB_OUT/intbits-e192.json
  --out RB_OUT/checks-e192.json`, rc 0 in 2.7 s, logged at 22:16:57; `checks-e192.json` was last written at 22:16:57.202, its capture at
  22:16:57.251. Line 81 is the log's last line: nothing ran through the runbook in that folder after the checker.
- **The step's own last line**, which the card lane's log of the step holds after the five captures: `[s24_reduce_e192] reduced (the
  registered reducer, Python 3.12.3): RB_OUT/intbits-e192.json; the section 7 checks: 1 PASS; 2 FAIL; 3 NOT EQUAL; 4 PASS; 5 FAIL; 6 FAIL;
  7 REPORTED; 8 REPORTED; commit both with the records, no score`. `runbook.log` itself holds each call's line, not its output; the
  runbook's bounded runner (v3.1's `rb_run.py`, through the k6 runbook's `rb_common.sh`) writes each call's stdout and stderr, as they
  come, to that call's capture file (masking only holder lines and other users' login marks, of which these two printed none), and
  `intbits-e192.txt` and `checks-e192.txt` are the step's fourth and fifth.
- **The inputs it read** (re-checked by this lane): the three files in RB_OUT are, byte for byte, this directory's `run/runs.jsonl`,
  `run/marks.jsonl` and `run/telemetry.jsonl.gz` unpacked, as committed in `a6e17e83`, and each equals its entry in `session/MANIFEST.sha256`.
- **The code as registered and kitted:** `reduce_intbits.py` (`715fddaa...`, in `SHA256SUMS-e192-registration`), `check_e192.py`
  (`ceb99e7c...`) and `rb/s24_reduce_e192.sh` (`d9168e61...`, both in `SHA256SUMS-e192-kit`) are the same at the kit `a6fe5c20`, the data
  commit and this note's parent: `tools/claims-v3/e192` is the tree `84ae5466...` at all three, and no commit since the kit touches it.
- **The interpreter:** `/usr/bin/python3` 3.12.3 on aifoundry2, isolated (`-I -B`), with the system's numpy 1.26.4 (the reducer imports
  numpy; the checker uses the standard library only). The step's last line names the Python, and `checks-e192.json` carries `"python":
  "3.12.3"`. E192.md section 16 (its desk checks) and KIT.md name the same interpreter and numpy for the desk.
- **Re-run since, at the desk, on the committed bytes** (a desk check of code): by this lane at 23:18:55-59 PST, from a fresh extract of
  `a6e17e83`'s own tree (`tools/claims-v3/e192` and this directory), the input built as step 13 builds it (3 of 3 against the manifest), run
  with the runbook's interpreter and flags, in the round's CPU slot with no device node reachable: `intbits-e192.json` and `checks-e192.json` byte-equal, and
  each program's printed lines byte-equal to its capture. The runs wrote nothing into the extract.

## 3. The measured, reduced prices

From [`intbits-e192.json`](intbits-e192.json), generated from the file, not typed. **Measured:** the registered reducer's prices from
the session's committed records; temperature-corrected (E192.md section 6's primary: each arm's power corrected to its control chain's
temperature by the pooled slope beta), mean ± SE over the 8 measured passes (1-8; pass 0, the registered warm-up,
is in the file and in no mean). The reducer's printed lines (`intbits-e192.txt`) give the board meter; the core rail's figures are the
file's. A reading the reducer gives as a bound (its 95% interval, mean ± 2 SE, holds zero) is shown with it. The uncorrected values and
the electrons per instruction are in the file.

- **Run records:** 324 (anchor_first 9, anchor_last 9, arm 288, burnin 18), every one passing the reducer's run gates (`ok` true in all 324: every launch ok with
  `check_bad` 0, one participant count, the clock within 1 MHz, at least 5 board samples);
  dips (board samples more than 2 W below the window's median) 0 in every arm; runs off protocol
  in the measured passes: `add.a.f0` 1 (pass 5's, flagged and kept: README.md, Results).
- **beta**, the pooled temperature slope: board **0.0552 W per °C**, core rail **0.0496 W per °C** (the reducer's
  `sum_dT2`, 17.38).
- **The headline prices (board):** C1, one carry position, **2.946 ± 1.458 fJ** (core rail 2.080 ± 0.514); the f2 count ladder's slope
  (Hamming), **62.683 ± 2.242 fJ per bit**.

**The ladders** (fJ per bit or per position, pJ where named; `intbits-e192.json` > `ladders`):

| the reducer's name | what (E192.md section 6) | board | core rail |
|---|---|---|---|
| `hamming_f2_slope_fJ` | the f2 count ladder's slope (Hamming), fJ per bit | 62.683 ± 2.242 | 61.152 ± 1.633 |
| `hamming_f2_quad_fJ` | its quadratic term, fJ | 0.152 ± 0.952 (bound \|x\| < 2.055) | -0.545 ± 0.342 (bound \|x\| < 1.228) |
| `add_f0_fJ_per_bit` | add, field 0, fJ per bit | 112.440 ± 3.210 | 98.370 ± 1.826 |
| `add_f1_fJ_per_bit` | add, field 1, fJ per bit | 76.313 ± 3.627 | 71.028 ± 2.407 |
| `add_f2_fJ_per_bit` | add, field 2, fJ per bit | 62.736 ± 2.239 | 60.977 ± 1.557 |
| `add_f3_fJ_per_bit` | add, field 3, fJ per bit | 56.393 ± 4.159 | 51.045 ± 1.393 |
| `add_f12_fJ_per_bit` | add, fields 1-2 (a12), fJ per bit | 76.276 ± 1.812 | 68.954 ± 0.532 |
| `additivity_all_minus_fields_pJ` | additivity: add.a.all - add.z - the four fields, pJ | 0.025 ± 0.123 (bound \|x\| < 0.2706) | 0.110 ± 0.050 |
| `f12_minus_f1_f2_pJ` | additivity: add.a.f12 - add.z - (f1 + f2), pJ | 0.216 ± 0.068 | 0.094 ± 0.044 |
| `and_f1_fJ_per_bit` | and, field 1, fJ per bit | 12.534 ± 3.861 | 11.328 ± 3.200 |
| `and_f2_fJ_per_bit` | and, field 2, fJ per bit | 9.520 ± 3.787 | 10.807 ± 2.009 |
| `and_f3_fJ_per_bit` | and, field 3, fJ per bit | 6.363 ± 3.389 (bound \|x\| < 13.14) | 7.542 ± 2.060 |
| `and12_fJ_per_bit` | and12 (the mean of fields 1 and 2), fJ per bit | 11.027 ± 3.567 | 11.067 ± 2.306 |
| `d12_a12_minus_and12_fJ_per_bit` | d12 = a12 - and12, fJ per bit | 65.249 ± 4.602 | 57.887 ± 2.370 |
| `add_f2_minus_f3_fJ_per_bit` | add, f2 - f3, fJ per bit | 6.343 ± 4.245 (bound \|x\| < 14.83) | 9.932 ± 2.558 |
| `and_f2_minus_f3_fJ_per_bit` | and, f2 - f3, fJ per bit | 3.157 ± 2.404 (bound \|x\| < 7.964) | 3.265 ± 2.570 (bound \|x\| < 8.404) |
| `S_cr_fJ_per_position` | S_cr, the slope of the carry ladder with the result held, fJ per position | 18.376 ± 1.198 | 15.700 ± 0.783 |
| `S_crb_fJ_per_position` | S_crb, the slope of the carry ladder with port A held, fJ per position | 63.793 ± 2.092 | 57.414 ± 0.519 |
| `S_cr_quad_fJ` | S_cr's quadratic term, fJ | -0.015 ± 0.245 (bound \|x\| < 0.5052) | 0.047 ± 0.112 (bound \|x\| < 0.2722) |
| `S_crb_quad_fJ` | S_crb's quadratic term, fJ | -0.666 ± 0.113 | -0.230 ± 0.103 |
| `C1_carry_fJ_per_position` | **C1 = (S_cr + S_crb - a12) / 2, one carry position, fJ per position** | 2.946 ± 1.458 | 2.080 ± 0.514 |
| `C2_fJ_per_bit` | C2, fJ per bit | -4.403 ± 4.503 (bound \|x\| < 13.41) | -2.553 ± 2.351 (bound \|x\| < 7.256) |
| `C3_fJ_per_bit` | C3 = and12 - C2, fJ per bit | 15.430 ± 1.423 | 13.620 ± 0.579 |
| `ripple_minus_add_z_pJ` | add.ripple - add.z (reported alone), pJ | 4.059 ± 0.042 | 3.851 ± 0.030 |

**The arms** (pJ per instruction; `intbits-e192.json` > `arms`): the energy over idle, and the contrast against the arm's control in the
same pass. E192.md section 14: the absolute energies over idle share one bias, the contrasts do not; read each arm's "over idle" with it,
the contrasts and the ladders without.

| arm | control | board: pJ over idle | board: contrast, pJ | core rail: pJ over idle | core rail: contrast, pJ | runs off protocol |
|---|---|---|---|---|---|---|
| `add.a.all` | `add.z` | 8.912 ± 0.092 | 4.951 ± 0.065 | 7.319 ± 0.074 | 4.612 ± 0.021 | 0 |
| `add.a.f0` | `add.z` | 5.851 ± 0.137 | 1.799 ± 0.051 | 4.350 ± 0.108 | 1.574 ± 0.029 | 1 |
| `add.a.f1` | `add.z` | 5.272 ± 0.109 | 1.221 ± 0.058 | 3.912 ± 0.071 | 1.136 ± 0.039 | 0 |
| `add.a.f12` | `add.z` | 6.329 ± 0.173 | 2.441 ± 0.058 | 4.857 ± 0.091 | 2.207 ± 0.017 | 0 |
| `add.a.f2` | `add.z` | 5.094 ± 0.156 | 1.004 ± 0.036 | 3.782 ± 0.124 | 0.976 ± 0.025 | 0 |
| `add.a.f2.k4` | `add.z` | 4.213 ± 0.106 | 0.249 ± 0.046 | 2.959 ± 0.060 | 0.251 ± 0.018 | 0 |
| `add.a.f2.k8` | `add.z` | 4.649 ± 0.146 | 0.489 ± 0.079 | 3.392 ± 0.100 | 0.532 ± 0.030 | 0 |
| `add.a.f3` | `add.z` | 5.026 ± 0.149 | 0.902 ± 0.067 | 3.649 ± 0.093 | 0.817 ± 0.022 | 0 |
| `add.b.f0` | `add.z` | 5.641 ± 0.135 | 1.743 ± 0.070 | 4.211 ± 0.093 | 1.553 ± 0.040 | 0 |
| `add.b.f2` | `add.z` | 5.226 ± 0.161 | 1.038 ± 0.054 | 3.837 ± 0.107 | 0.956 ± 0.020 | 0 |
| `add.cr.l0` | `add.z` | 4.365 ± 0.121 | -0.009 ± 0.049 (bound \|x\| < 0.1069) | 3.064 ± 0.064 | 0.039 ± 0.023 (bound \|x\| < 0.08534) | 0 |
| `add.cr.l16` | `add.cr.l0` | 4.499 ± 0.143 | 0.351 ± 0.069 | 3.152 ± 0.098 | 0.255 ± 0.028 | 0 |
| `add.cr.l24` | `add.cr.l0` | 4.468 ± 0.180 | 0.386 ± 0.071 | 3.198 ± 0.130 | 0.352 ± 0.035 | 0 |
| `add.cr.l31` | `add.cr.l0` | 4.851 ± 0.128 | 0.597 ± 0.059 | 3.476 ± 0.089 | 0.497 ± 0.037 | 0 |
| `add.cr.l8` | `add.cr.l0` | 4.221 ± 0.104 | 0.144 ± 0.079 (bound \|x\| < 0.3017) | 2.962 ± 0.080 | 0.121 ± 0.031 | 0 |
| `add.crb.l0` | `add.z` | 4.137 ± 0.174 | -0.023 ± 0.034 (bound \|x\| < 0.09193) | 2.905 ± 0.116 | 0.045 ± 0.030 (bound \|x\| < 0.1051) | 0 |
| `add.crb.l16` | `add.crb.l0` | 5.258 ± 0.161 | 1.154 ± 0.051 | 3.889 ± 0.120 | 1.009 ± 0.030 | 0 |
| `add.crb.l24` | `add.crb.l0` | 5.761 ± 0.093 | 1.671 ± 0.040 | 4.247 ± 0.089 | 1.378 ± 0.018 | 0 |
| `add.crb.l31` | `add.crb.l0` | 5.830 ± 0.152 | 1.972 ± 0.070 | 4.497 ± 0.077 | 1.806 ± 0.036 | 0 |
| `add.crb.l8` | `add.crb.l0` | 4.851 ± 0.075 | 0.649 ± 0.035 | 3.469 ± 0.070 | 0.513 ± 0.039 | 0 |
| `add.ripple` | `add.z` | 7.914 ± 0.087 | 4.059 ± 0.042 | 6.477 ± 0.056 | 3.851 ± 0.030 | 0 |
| `add.s.f0` | `add.z` | 4.935 ± 0.171 | 0.867 ± 0.088 | 3.618 ± 0.138 | 0.829 ± 0.017 | 0 |
| `add.s.f2` | `add.z` | 4.672 ± 0.068 | 0.346 ± 0.075 | 3.288 ± 0.065 | 0.300 ± 0.020 | 0 |
| `add.same` | `nop` | 3.318 ± 0.103 | 0.312 ± 0.041 | 2.228 ± 0.070 | 0.248 ± 0.016 | 0 |
| `add.z` | `add.same` | 4.254 ± 0.079 | 1.073 ± 0.073 | 2.933 ± 0.044 | 0.810 ± 0.012 | 0 |
| `and.a.f1` | `and.z` | 4.353 ± 0.149 | 0.201 ± 0.062 | 3.019 ± 0.100 | 0.181 ± 0.051 | 0 |
| `and.a.f2` | `and.z` | 4.362 ± 0.096 | 0.152 ± 0.061 | 3.054 ± 0.087 | 0.173 ± 0.032 | 0 |
| `and.a.f3` | `and.z` | 4.175 ± 0.180 | 0.102 ± 0.054 (bound \|x\| < 0.2103) | 2.897 ± 0.115 | 0.121 ± 0.033 | 0 |
| `and.z` | `add.z` | 4.182 ± 0.117 | 0.075 ± 0.058 (bound \|x\| < 0.1916) | 2.860 ± 0.076 | 0.041 ± 0.028 (bound \|x\| < 0.09704) | 0 |
| `nop` | - | 2.934 ± 0.088 | - | 1.925 ± 0.072 | - | 0 |
| `xor.a.f2` | `xor.z` | 5.512 ± 0.140 | 1.226 ± 0.068 | 4.126 ± 0.090 | 1.081 ± 0.019 | 0 |
| `xor.z` | `add.z` | 4.065 ± 0.144 | -0.082 ± 0.069 (bound \|x\| < 0.2191) | 2.874 ± 0.088 | 0.024 ± 0.028 (bound \|x\| < 0.07968) | 0 |

## 4. The section 7 checks, as the checker printed them

[`checks-e192.txt`](checks-e192.txt), verbatim (each line cut at 300 characters by the checker itself):

```
check 1: PASS {"launches": 3240, "check_bad_launches": 0, "participants_not_1024": 0, "runs": 324, "runs_ret_over_body_outside_0.1pct": 0, "ret_over_body_range": [1.0117191827558676, 1.011719328608284]}
check 2: FAIL {"board_window_samples": 6481, "off_600_MHz": 0, "rail_mv_samples": 4907, "rail_mv_beyond_3mV": 0, "runs_with_l1d_misses": 324}
check 3: NOT EQUAL {"min": 1.2197065648103055e-05, "max": 1.2579761665735282e-05, "spread": 3.826960176322271e-07, "note": "no threshold is registered: EQUAL means identical"}
check 4: PASS {"median_rate": 234246892505.71695, "slower_arms": [], "faster_arms": [], "max_abs_dev": 9.338203609998708e-05, "runs_off_protocol": 1}
check 5: FAIL {}
check 6: FAIL {}
check 7: REPORTED {"xor.z_vs_add.z_pJ_board": {"mean": -0.08160820853832673, "se": 0.06873073398746758, "n": 8, "reading": "bound |x| < 0.2191"}, "and.z_vs_add.z_pJ_board": {"mean": 0.07505187498409704, "se": 0.058257817403622604, "n": 8, "reading": "bound |x| < 0.1916"}, "xor.z_vs_add.z_pJ_rail": {"mean": 0.02400095
check 8: REPORTED {"arms_with_electrons_rail": 31, "arms_with_electrons_12V": 31}
CHECKS-E192: 1 PASS; 2 FAIL; 3 NOT EQUAL; 4 PASS; 5 FAIL; 6 FAIL; 7 REPORTED; 8 REPORTED
```

The items behind checks 5 and 6 (`checks-e192.json` > `checks` > `5`, `6` > `items`; within 2 SE of zero is a PASS, E192.md section 7):

| check | item | as the checker wrote it | verdict |
|---|---|---|---|
| 5 | `board.additivity_all_minus_fields_pJ` | 0.02482 +- 0.1229 (2 SE 0.2458) | PASS |
| 5 | `board.f12_minus_f1_f2_pJ` | 0.216 +- 0.06788 (2 SE 0.1358) | FAIL |
| 5 | `rail.additivity_all_minus_fields_pJ` | 0.1097 +- 0.04997 (2 SE 0.09995) | FAIL |
| 5 | `rail.f12_minus_f1_f2_pJ` | 0.09445 +- 0.04391 (2 SE 0.08781) | FAIL |
| 6 | `board.hamming_f2_quad_fJ` | 0.1517 +- 0.9519 (2 SE 1.904) | PASS |
| 6 | `board.S_cr_quad_fJ` | -0.01474 +- 0.2452 (2 SE 0.4905) | PASS |
| 6 | `board.S_crb_quad_fJ` | -0.6658 +- 0.1128 (2 SE 0.2256) | FAIL |
| 6 | `rail.hamming_f2_quad_fJ` | -0.5449 +- 0.3416 (2 SE 0.6833) | PASS |
| 6 | `rail.S_cr_quad_fJ` | 0.04734 +- 0.1124 (2 SE 0.2248) | PASS |
| 6 | `rail.S_crb_quad_fJ` | -0.23 +- 0.1029 (2 SE 0.2058) | FAIL |

Each FAIL is reported beside the prices it qualifies and removes no datum (E192.md section 7: "a failed check is reported as failed,
beside the prices it qualifies"). Note 1 § 4 gives the sizes behind checks 2 and 3, post hoc. **Registered verdicts, unchanged.**

## 5. Beside verify-e192d's independent re-derivation

`verify-e192d` (Sat 14 Nov 2026, 22:20-22:48 PST) re-derived the reduction from this directory's committed raw files, taken from
`a6e17e83`, with its own code, written from E192.md section 6 and a reading of the reducer's semantics, importing nothing from the kit,
the reducer or the runner (the standard library and numpy 1.26.4; `/usr/bin/python3` 3.12.3), and the section 7 checks with its own code
too. Its figures are a desk check of code. It compared its output with the same bytes as `intbits-e192.json` (sha256 `0a675627...`),
field by field: **8,233 fields** (every run record, every arm's energies and contrasts on both meters, corrected and
uncorrected, the electrons, beta and every ladder), **0 beyond the tolerance** (an absolute 1e-12 or a relative 1e-9).
The largest relative difference is 1.68e-12 (`ladders.board`); the largest absolute difference is
4.47e-08 (`arms.contrast_electrons_rail`, electron counts per instruction of 2.9e+05 to 5.5e+07; that field's
largest relative difference is 1.5e-13). Each pair below is **the
reducer / verify-e192d**, generated from `intbits-e192.json` and from the verifier's own output file (`vreduce-e192.json`), not typed:

| the reducer's name | board: the reducer | board: verify-e192d | core rail: the reducer | core rail: verify-e192d |
|---|---|---|---|---|
| `hamming_f2_slope_fJ` | 62.682606 ± 2.242268 | 62.682606 ± 2.242268 | 61.152168 ± 1.633340 | 61.152168 ± 1.633340 |
| `hamming_f2_quad_fJ` | 0.151655 ± 0.951885 | 0.151655 ± 0.951885 | -0.544860 ± 0.341626 | -0.544860 ± 0.341626 |
| `add_f0_fJ_per_bit` | 112.439631 ± 3.209739 | 112.439631 ± 3.209739 | 98.370446 ± 1.826155 | 98.370446 ± 1.826155 |
| `add_f1_fJ_per_bit` | 76.313349 ± 3.627034 | 76.313349 ± 3.627034 | 71.028305 ± 2.407293 | 71.028305 ± 2.407293 |
| `add_f2_fJ_per_bit` | 62.736374 ± 2.239473 | 62.736374 ± 2.239473 | 60.976966 ± 1.556881 | 60.976966 ± 1.556881 |
| `add_f3_fJ_per_bit` | 56.392927 ± 4.159478 | 56.392927 ± 4.159478 | 51.045398 ± 1.392651 | 51.045398 ± 1.392651 |
| `add_f12_fJ_per_bit` | 76.276061 ± 1.812008 | 76.276061 ± 1.812008 | 68.954264 ± 0.531570 | 68.954264 ± 0.531570 |
| `additivity_all_minus_fields_pJ` | 0.024820 ± 0.122911 | 0.024820 ± 0.122911 | 0.109734 ± 0.049973 | 0.109734 ± 0.049973 |
| `f12_minus_f1_f2_pJ` | 0.216038 ± 0.067880 | 0.216038 ± 0.067880 | 0.094452 ± 0.043907 | 0.094452 ± 0.043907 |
| `and_f1_fJ_per_bit` | 12.533588 ± 3.861092 | 12.533588 ± 3.861092 | 11.328016 ± 3.200452 | 11.328016 ± 3.200452 |
| `and_f2_fJ_per_bit` | 9.519674 ± 3.787448 | 9.519674 ± 3.787448 | 10.806771 ± 2.009328 | 10.806771 ± 2.009328 |
| `and_f3_fJ_per_bit` | 6.363046 ± 3.389475 | 6.363046 ± 3.389475 | 7.542162 ± 2.059854 | 7.542162 ± 2.059854 |
| `and12_fJ_per_bit` | 11.026631 ± 3.567357 | 11.026631 ± 3.567357 | 11.067394 ± 2.306122 | 11.067394 ± 2.306122 |
| `d12_a12_minus_and12_fJ_per_bit` | 65.249430 ± 4.601582 | 65.249430 ± 4.601582 | 57.886870 ± 2.370107 | 57.886870 ± 2.370107 |
| `add_f2_minus_f3_fJ_per_bit` | 6.343447 ± 4.244868 | 6.343447 ± 4.244868 | 9.931568 ± 2.557655 | 9.931568 ± 2.557655 |
| `and_f2_minus_f3_fJ_per_bit` | 3.156628 ± 2.403853 | 3.156628 ± 2.403853 | 3.264610 ± 2.569685 | 3.264610 ± 2.569685 |
| `S_cr_fJ_per_position` | 18.376227 ± 1.197716 | 18.376227 ± 1.197716 | 15.700281 ± 0.783319 | 15.700281 ± 0.783319 |
| `S_crb_fJ_per_position` | 63.792534 ± 2.092085 | 63.792534 ± 2.092085 | 57.413908 ± 0.518975 | 57.413908 ± 0.518975 |
| `S_cr_quad_fJ` | -0.014741 ± 0.245229 | -0.014741 ± 0.245229 | 0.047342 ± 0.112415 | 0.047342 ± 0.112415 |
| `S_crb_quad_fJ` | -0.665756 ± 0.112785 | -0.665756 ± 0.112785 | -0.229955 ± 0.102913 | -0.229955 ± 0.102913 |
| `C1_carry_fJ_per_position` | 2.946350 ± 1.457705 | 2.946350 ± 1.457705 | 2.079962 ± 0.513792 | 2.079962 ± 0.513792 |
| `C2_fJ_per_bit` | -4.403246 ± 4.502518 | -4.403246 ± 4.502518 | -2.552925 ± 2.351339 | -2.552925 ± 2.351339 |
| `C3_fJ_per_bit` | 15.429877 ± 1.422843 | 15.429877 ± 1.422843 | 13.620319 ± 0.578866 | 13.620319 ± 0.578866 |
| `ripple_minus_add_z_pJ` | 4.058935 ± 0.041542 | 4.058935 ± 0.041542 | 3.851462 ± 0.029819 | 3.851462 ± 0.029819 |
| beta, W per °C | 0.055206193 | 0.055206193 | 0.049568775 | 0.049568775 |

The checks, the checker / verify-e192d (from `checks-e192.json` and the verifier's `vchecks-e192.json`):

| check | the checker (`checks-e192.json`) | verify-e192d (`vchecks-e192.json`) |
|---|---|---|
| 1 | PASS: 3240 launches (passes 0-8), check_bad 0, participants not 1,024 0; retired / body 1.0117192-1.0117193 | PASS: 3240, 0, 0; 1.0117192-1.0117193 |
| 2 | FAIL: board window samples 6481, off 600 MHz 0; rail samples 4907, beyond 3 mV 0; runs with L1 data misses 324 | FAIL: 6481, 0; 4907, 0; 324 |
| 3 | NOT EQUAL: misses per iteration 1.21971e-05 to 1.25798e-05 | NOT EQUAL: 1.21971e-05 to 1.25798e-05 |
| 4 | PASS: median rate 2.342469e+11 instructions a second, largest deviation 9.3382e-05, slower arms 0, runs off protocol 1 | PASS: 2.342469e+11, 9.3382e-05, 0, 1 |
| 5 | FAIL: board additivity_all_minus_fields_pJ PASS; board f12_minus_f1_f2_pJ FAIL; rail additivity_all_minus_fields_pJ FAIL; rail f12_minus_f1_f2_pJ FAIL | FAIL: board additivity_all_minus_fields_pJ PASS; board f12_minus_f1_f2_pJ FAIL; rail additivity_all_minus_fields_pJ FAIL; rail f12_minus_f1_f2_pJ FAIL |
| 6 | FAIL: board hamming_f2_quad_fJ PASS; board S_cr_quad_fJ PASS; board S_crb_quad_fJ FAIL; rail hamming_f2_quad_fJ PASS; rail S_cr_quad_fJ PASS; rail S_crb_quad_fJ FAIL | FAIL: board hamming_f2_quad_fJ PASS; board S_cr_quad_fJ PASS; board S_crb_quad_fJ FAIL; rail hamming_f2_quad_fJ PASS; rail S_cr_quad_fJ PASS; rail S_crb_quad_fJ FAIL |
| 7 | REPORTED: xor.z_vs_add.z_pJ_board -0.081608 ± 0.068731; and.z_vs_add.z_pJ_board 0.075052 ± 0.058258; xor.z_vs_add.z_pJ_rail 0.024001 ± 0.027837; and.z_vs_add.z_pJ_rail 0.041181 ± 0.027928 | REPORTED: -0.081608 ± 0.068731; 0.075052 ± 0.058258; 0.024001 ± 0.027837; 0.041181 ± 0.027928 |
| 8 | REPORTED: arms with electrons, rail 31, 12 V 31 | REPORTED: 31, 31 |

**Agree or differ: they agree.** Every ladder and beta above, on both meters, is the same to the six decimals shown (the largest
difference in any shown mean or SE is 4.8e-13), every field beneath them agrees within the tolerance, the eight verdicts are the same,
and the verifier's own comparison of the two checks' numbers lists 55 items, every one the same.

## 6. Checks before the commit

- The four copied files as staged are byte-equal (`cmp`) to the card lane's RB_OUT files and to the runbook's captures of the two calls,
  and to this lane's re-run (§ 2).
- In a copy of this directory with the six new files: `SHA256SUMS` 27 of 27, `SHA256SUMS-note1` 6 of 6 and `SHA256SUMS-note2` 5 of 5
  entries OK; 40 files, every one in a list but `SHA256SUMS-note1` and `SHA256SUMS-note2`.
- The desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the round's folders forbidden) read the six new files with 0 hits,
  and a login check found no home path, no login and no holder line in them or in this commit's subject and body.
- The public-text scan (the lab's `sanitize_extracts.py`, its fixed list and the box's local table, and the round's lists of private,
  vendor, process, access and mechanism words) found nothing in the six new files or in this commit's subject and body.

## What does not change

Every reading, verdict, gate, stop and figure of `README.md`, note 1 and their files stands; this note adds the reducer's and the checker's
outputs beside them and reads them, and changes nothing. The reducer and the checker read none of this note's files. This lane reached no
box, opened no device and changed no committed file.

SPDX-License-Identifier: Apache-2.0
