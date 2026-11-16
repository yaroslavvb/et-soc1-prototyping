# E199's data README, dated note 2 (Mon 16 Nov 2026): step 13's outputs committed beside the data - the rail filter's census, the reduction (filtered and unfiltered), E192's checks on card 1 and the transport scorer's eight verdicts, each with its printed lines; the measured prices beside aifoundry3's; the data verifier's re-derivation agrees

*Written on aifoundry2 from about 06:43 PST on Mon 16 Nov 2026 (week 47) by the clock, desk only (no card, no lab box, no device, no post), by the lane `reduce-e199` of Q191: the records lane that E199's card-lane brief names for step 13 ("a records lane commits them with intbits-e199.json, checks-e199.json and the unfiltered reduction"). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `6d1f3a5a`, the data commit) and [note 1](README.md.dated-note-1.md) with [`SHA256SUMS-note1`](SHA256SUMS-note1) (lab `d2f8ac3c`) stay as committed. **No number, rule, verdict or check reading changes and nothing is re-scored:** the files below are step 13's own outputs, byte for byte, but for the scores file, which is the registered scorer's output on the same bytes with the reduction's repository path in place of the scratch path step 13 gave it (section 6). **No number of the sealed card-1 forecast is here** (the lab knows it only as E199.md's freeze line 2; the model session scores it privately). Interpreter: `/usr/bin/python3` 3.12.3 with numpy 1.26.4 (`-I -B`) on aifoundry2, for step 13 and for this lane's re-run. Labels: **registered** (E199.md, E192.md, the kit), **measured** (the session's records, and the registered pipeline's outputs from them), **desk check of code** (this lane's re-run and comparisons), **REPORTED** (verify-e199d's own code, not re-run here; and what E199.md itself labels REPORTED).*

## 1. The new files

| file | what | from | sha256 |
|---|---|---|---|
| [`intbits-e199.json`](intbits-e199.json) | E192's registered reducer (`reduce_intbits.py`, `715fddaa...`) on the filtered run: card 1's measured prices, the reduction the scorer reads | step 13's output, byte for byte | `5033f861...` |
| [`intbits-e199.txt`](intbits-e199.txt) | the reducer's printed lines | the runbook's capture of that call (capture 5), byte for byte | `575fb034...` |
| [`checks-e199.json`](checks-e199.json) | E192's section 7 checker (`check_e192.py`, `ceb99e7c...`) on card 1's raw run and that reduction: REPORTED beside E192's, never a transport verdict | step 13's output, byte for byte | `905586f8...` |
| [`checks-e199.txt`](checks-e199.txt) | the checker's printed lines | capture 6, byte for byte | `45192e48...` |
| [`scores-e199.json`](scores-e199.json) | THE TRANSPORT SCORER (`score_e199.py`, `e578bf74...`): the eight registered verdicts, every price's pair, z and ratio, each family's scale, R1 and R2, E192's checks beside card 1's | the registered scorer on the byte-identical reduction, given it by its repository path; step 13's file (`64d3b218...`, not committed) differs in that one value (section 6) | `69a55603...` |
| [`scores-e199.txt`](scores-e199.txt) | the scorer's printed lines | capture 7, byte for byte (the re-run printed the same bytes) | `ae512c8e...` |
| [`intbits-e199-unfiltered.json`](intbits-e199-unfiltered.json) | the same reducer on the unfiltered telemetry: REPORTED beside (E199.md 6.5) | step 13's output, byte for byte | `066d5f6c...` |
| [`intbits-e199-unfiltered.txt`](intbits-e199-unfiltered.txt) | its printed lines | capture 8, byte for byte | `f9860615...` |
| [`railfilter-e199.json`](railfilter-e199.json) | E151's rail filter's census (`prefilter_e199.py`, `79c699ec...`, which imports `railfilter_e151.py` at `87bffb5f...`): the 22 samples removed, each with its rail, running-maximum and board readings (E199.md 6.8 reports the census) | step 13's output (its filtered directory), byte for byte | `518aee91...` |
| [`railfilter-e199.txt`](railfilter-e199.txt) | the filter's printed line | capture 4, byte for byte | `f1871a91...` |
| `README.md.dated-note-2.md` | this note | written by this lane | in `SHA256SUMS-note2` |
| `SHA256SUMS-note2` | the sums of the eleven files above and of `SHA256SUMS-note1` (12 entries) | written by this lane | - |

The filtered telemetry itself is not committed: it is the committed `run/telemetry.jsonl.gz` unpacked, less the census's 22 sample lines (each removed whole), with `run/runs.jsonl` and `run/marks.jsonl` passed through byte for byte (desk check of code: this lane's re-run made the same filtered telemetry bytes as step 13).

## 2. When, where and on which commit step 13 ran

From card-e199's runbook log (lines 82-89 are step 13, `rb/s24_score_e199.sh` at its kit pin `e8c0bf9e...`), the captures' times and the lab clone's own HEAD log (a desk check of code):

| log line | logged (PST) | the call | rc | secs | its output (mtime) | its capture (mtime) |
|---|---|---|---:|---:|---|---|
| 82-84 | 05:18:56 | the gates: the data directory tracked at HEAD (3 of 3 paths) and clean (0 lines); the five programs' sha256 | 0 | 0.0 | - | 05:18:56.279-.353 |
| 85 | 05:18:57 | E151's rail filter (`prefilter_e199.py`) | 0 | 0.8 | `railfilter-e199.json` 05:18:57.276 | 05:18:57.278 |
| 86 | 05:18:58 | E192's reducer on the filtered run | 0 | 1.3 | `intbits-e199.json` 05:18:58.576 | 05:18:58.577 |
| 87 | 05:19:01 | E192's section 7 checker | 0 | 3.2 | `checks-e199.json` 05:19:01.763 | 05:19:01.825 |
| 88 | 05:19:01 | THE TRANSPORT SCORER | 0 | 0.0 | `scores-e199.json` 05:19:01.882 | 05:19:01.883 |
| 89 | 05:19:03 | the reducer on the unfiltered run | 0 | 1.4 | `intbits-e199-unfiltered.json` 05:19:03.286 | 05:19:03.287 |

- **Nothing after it:** line 89 is the log's last line; the log has no stop line; no step-13 output was written after it.
- **The programs** (capture 3): `reduce_intbits.py` `715fddaa...` (E192's registered reducer), `check_e192.py` `ceb99e7c...` (E192's kit pin), `prefilter_e199.py` `79c699ec...` and `score_e199.py` `e578bf74...` (E199's registration list, 17 of 17 in this lane's extract), `railfilter_e151.py` `87bffb5f...`.
- **The commit it ran on.** The lab clone's HEAD log: `6d1f3a5a` (E199's data commit) at 05:12:10, then `4bc7a07a` at 05:13:21 (E196's data commit: its parent is `6d1f3a5a` and it touches only E196's own data directory, 42 paths), until 06:25:28. Step 13 therefore ran at HEAD `4bc7a07a`, where this directory (tree `8a0e3c93`) and `tools/claims-v3/e199` (`0afcd4f4`), `e192` (`84ae5466`) and `e151` (`e0ae09b9`) are the same trees as at `6d1f3a5a`, and its gates read this directory committed and clean: it read the data commit's bytes.
- **The inputs.** Step 13's `run/telemetry.jsonl` (unpacked), `runs.jsonl` and `marks.jsonl` are byte-equal to the files committed at `6d1f3a5a` and to their lines in `session/MANIFEST.sha256` (`f0f726e1...`, `d89caf26...`, `e25b8275...`).
- **The re-run (desk check of code), 06:34:18-24 PST.** E199's step-13 pipeline, from this lane's own extract of `6d1f3a5a`'s tree (not the working tree), in one of the round's CPU slots with no device node reachable and a 4 GB cap, `/usr/bin/python3 -I -B` 3.12.3: the filter, the reducer, the checker, the scorer and the unfiltered reduction each exited 0; the census, the filtered telemetry, `intbits-e199.json`, `checks-e199.json` and `intbits-e199-unfiltered.json` came out byte-equal to step 13's, and the five printed outputs byte-equal to captures 4-8; `scores-e199.json` equals step 13's in 2,747 of its 2,748 values (section 6) and note 1's re-run byte for byte.

## 3. The rules' words

As the registered scorer printed them (capture 7, [`scores-e199.txt`](scores-e199.txt)):

```
E199-T1 (family A, board, per-arm contrasts (THE HEADLINE)): FAIL - 29 of 31 decided, 21 hold, 8 miss (PASS at 27, FAIL at 5 misses)
E199-T2 (family A): FAIL - 23 hold, 6 miss at the best scale s* 1.03393; s_hat 1.0408 +- 0.02368, the scale meets [0.943145, 1.03707]
E199-T1L (family B, board ladders): FAIL - 22 of 24 decided, 14 hold, 8 miss (PASS at 21, FAIL at 4 misses)
E199-T2L (family B): FAIL - 14 hold, 8 miss at the best scale s* 1.03493; s_hat 1.05713 +- 0.04524, the scale meets [0.943145, 1.03707]
E199-T1R (family C, core rail, per-arm contrasts): FAIL - 31 of 31 decided, 24 hold, 7 miss (PASS at 27, FAIL at 5 misses)
E199-T2R (family C): PASS - 29 hold, 2 miss at the best scale s* 1.03707; s_hat 1.04404 +- 0.005808, the scale meets [0.943145, 1.03707]
E199-T1RL (family D, core rail ladders): FAIL - 24 of 24 decided, 18 hold, 6 miss (PASS at 21, FAIL at 4 misses)
E199-T2RL (family D): PASS - 21 hold, 3 miss at the best scale s* 1.03707; s_hat 1.0459 +- 0.008585, the scale meets [0.943145, 1.03707]
R1 (REPORTED, board energies over idle): 32 of 32 decided, T1 0 hold, T2 0 hold, s_hat 1.27836
R2 (REPORTED, rail energies over idle): 32 of 32 decided, T1 1 hold, T2 6 hold, s_hat 1.10286
SCORES-E199: E199-T1 FAIL; E199-T2 FAIL; E199-T1L FAIL; E199-T2L FAIL; E199-T1R FAIL; E199-T2R PASS; E199-T1RL FAIL; E199-T2RL PASS
```

The same, with the counts from [`scores-e199.json`](scores-e199.json) and, **beside each FAIL, the null rate at its number of passes** (E199.md 6.8, registered before any datum; REPORTED there, a desk check of code: the share of draws with no card difference that read FAIL). Every decided price in all four families rests on 8 measured passes on card 1 (`families` > `card1_passes` [8, 8] in A, B, C and D), so the row is E199.md 6.8's row for 8 passes. A FAIL is reported as FAIL.

| rule | family | decided of N | T1: hold / miss (PASS at K hold, FAIL at F miss) | T2: hold / miss at s* | s_hat ± SE (meets [0.943145, 1.03707]?) | the word | null rate at 8 passes |
|---|---|---:|---|---|---|---|---:|
| **E199-T1** | A: the 31 per-arm contrasts against their controls, board (THE HEADLINE) | 29 of 31 | 21 / 8 (27, 5) | - | - | **FAIL** | 1.5% |
| **E199-T2** | A | 29 of 31 | - | 23 / 6 at s* 1.03393 | 1.0408 ± 0.02368 (yes) | **FAIL** | 0.3% |
| E199-T1L | B: the 24 ladder quantities, board | 22 of 24 | 14 / 8 (21, 4) | - | - | **FAIL** | 6.3% |
| E199-T2L | B | 22 of 24 | - | 14 / 8 at s* 1.03493 | 1.05713 ± 0.04524 (yes) | **FAIL** | 1.5% |
| E199-T1R | C: the 31 per-arm contrasts against their controls, core rail | 31 of 31 | 24 / 7 (27, 5) | - | - | **FAIL** | 2.3% |
| E199-T2R | C | 31 of 31 | - | 29 / 2 at s* 1.03707 | 1.04404 ± 0.005808 (yes) | **PASS** | (0.5%; a PASS needs none) |
| E199-T1RL | D: the 24 ladder quantities, core rail | 24 of 24 | 18 / 6 (21, 4) | - | - | **FAIL** | 4.3% |
| E199-T2RL | D | 24 of 24 | - | 21 / 3 at s* 1.03707 | 1.0459 ± 0.008585 (yes) | **PASS** | (1.2%; a PASS needs none) |

**Not decided** (E199.md 6.2: card 1's SE above 3 times aifoundry3's): A `add.crb.l8` (card 1's SE 0.111996 above 3 x aifoundry3's 0.0352399); A `add.ripple` (card 1's SE 0.134965 above 3 x aifoundry3's 0.0415422); B `and_f2_minus_f3_fJ_per_bit` (card 1's SE 8.87275 above 3 x aifoundry3's 2.40385); B `ripple_minus_add_z_pJ` (card 1's SE 0.134965 above 3 x aifoundry3's 0.0415422). Families C and D decide every price.

**R1 and R2** (REPORTED, no verdict: the energies over idle carry one shared bias and each card's own idle footing): R1, board, 32 of 32 decided, T1 0 hold, T2 0 hold, s_hat 1.27836 ± 0.0109; R2, core rail, 32 of 32 decided, T1 1 hold, T2 6 hold, s_hat 1.10286 ± 0.00559.

**E192's section 7 checks on card 1** ([`checks-e199.txt`](checks-e199.txt); REPORTED beside E192's, never a transport verdict): `CHECKS-E192: 1 PASS; 2 FAIL; 3 NOT EQUAL; 4 PASS; 5 FAIL; 6 FAIL; 7 REPORTED; 8 REPORTED`. Each is the same word as aifoundry3's (`scores-e199.json` > `checks_beside`: 8 of 8 the same).

## 4. The measured prices beside aifoundry3's

Each pair as the scorer read it (`scores-e199.json` > `families` > `prices`; measured): aifoundry3's m3 ± se3 is E192's measured price (`intbits-e192.json` in E192's data directory, copied exactly into the frozen `forecast-e199.json`, E199.md's freeze line 1); card 1's m1 ± se1 is this directory's `intbits-e199.json`; both temperature-corrected (E192.md section 6's primary), mean ± SE over the 8 measured passes (pass 0, the registered warm-up, out). **Desk check of code:** every m3 and se3 below equals `intbits-e192.json`'s and `forecast-e199.json`'s value at the price's path, and every m1 and se1 equals `intbits-e199.json`'s: 174 of 174 pairs (the four families and R1 and R2). z = (m1 - m3) / sqrt(se1² + se3²); T1 holds at |z| <= 2; T2 holds at the family's s* (E199.md 6.3-6.4); ND = not decided.

**Family A: the 31 per-arm contrasts against their controls, board (THE HEADLINE)** (pJ an instruction; s* 1.03393):

| price | control | aifoundry3 (E192) | card 1 (E199) | m1 / m3 | z | T1 | T2 |
|---|---|---:|---:|---:|---:|---|---|
| `add.a.all` | `add.z` | 4.951 ± 0.065 | 5.340 ± 0.096 | 1.079 | +3.37 | **miss** | hold |
| `add.a.f0` | `add.z` | 1.799 ± 0.051 | 1.869 ± 0.075 | 1.039 | +0.77 | hold | hold |
| `add.a.f1` | `add.z` | 1.221 ± 0.058 | 1.492 ± 0.081 | 1.222 | +2.71 | **miss** | **miss** |
| `add.a.f12` | `add.z` | 2.441 ± 0.058 | 2.579 ± 0.100 | 1.057 | +1.20 | hold | hold |
| `add.a.f2` | `add.z` | 1.004 ± 0.036 | 1.413 ± 0.104 | 1.408 | +3.72 | **miss** | **miss** |
| `add.a.f2.k4` | `add.z` | 0.249 ± 0.046 | 0.384 ± 0.106 | 1.540 | +1.17 | hold | hold |
| `add.a.f2.k8` | `add.z` | 0.489 ± 0.079 | 0.721 ± 0.110 | 1.474 | +1.71 | hold | hold |
| `add.a.f3` | `add.z` | 0.902 ± 0.067 | 0.997 ± 0.106 | 1.105 | +0.76 | hold | hold |
| `add.b.f0` | `add.z` | 1.743 ± 0.070 | 1.773 ± 0.058 | 1.017 | +0.33 | hold | hold |
| `add.b.f2` | `add.z` | 1.038 ± 0.054 | 1.069 ± 0.097 | 1.029 | +0.27 | hold | hold |
| `add.cr.l0` | `add.z` | -0.009 ± 0.049 | 0.153 ± 0.113 | -17.040 | +1.32 | hold | hold |
| `add.cr.l16` | `add.cr.l0` | 0.351 ± 0.069 | 0.315 ± 0.153 | 0.899 | -0.21 | hold | hold |
| `add.cr.l24` | `add.cr.l0` | 0.386 ± 0.071 | 0.430 ± 0.107 | 1.113 | +0.34 | hold | hold |
| `add.cr.l31` | `add.cr.l0` | 0.597 ± 0.059 | 0.523 ± 0.082 | 0.877 | -0.73 | hold | hold |
| `add.cr.l8` | `add.cr.l0` | 0.144 ± 0.079 | 0.111 ± 0.094 | 0.773 | -0.27 | hold | hold |
| `add.crb.l0` | `add.z` | -0.023 ± 0.034 | 0.235 ± 0.074 | -10.204 | +3.16 | **miss** | **miss** |
| `add.crb.l16` | `add.crb.l0` | 1.154 ± 0.051 | 0.952 ± 0.087 | 0.825 | -2.01 | **miss** | **miss** |
| `add.crb.l24` | `add.crb.l0` | 1.671 ± 0.040 | 1.472 ± 0.086 | 0.881 | -2.10 | **miss** | **miss** |
| `add.crb.l31` | `add.crb.l0` | 1.972 ± 0.070 | 1.849 ± 0.062 | 0.938 | -1.32 | hold | hold |
| `add.crb.l8` | `add.crb.l0` | 0.649 ± 0.035 | 0.431 ± 0.112 | 0.663 | - | ND | ND |
| `add.ripple` | `add.z` | 4.059 ± 0.042 | 4.248 ± 0.135 | 1.047 | - | ND | ND |
| `add.s.f0` | `add.z` | 0.867 ± 0.088 | 1.139 ± 0.099 | 1.313 | +2.05 | **miss** | hold |
| `add.s.f2` | `add.z` | 0.346 ± 0.075 | 0.491 ± 0.124 | 1.417 | +1.00 | hold | hold |
| `add.same` | `nop` | 0.312 ± 0.041 | 0.247 ± 0.087 | 0.791 | -0.68 | hold | hold |
| `add.z` | `add.same` | 1.073 ± 0.073 | 0.990 ± 0.096 | 0.923 | -0.69 | hold | hold |
| `and.a.f1` | `and.z` | 0.201 ± 0.062 | 0.424 ± 0.086 | 2.116 | +2.12 | **miss** | **miss** |
| `and.a.f2` | `and.z` | 0.152 ± 0.061 | 0.341 ± 0.095 | 2.241 | +1.68 | hold | hold |
| `and.a.f3` | `and.z` | 0.102 ± 0.054 | 0.270 ± 0.111 | 2.655 | +1.36 | hold | hold |
| `and.z` | `add.z` | 0.075 ± 0.058 | 0.067 ± 0.103 | 0.894 | -0.07 | hold | hold |
| `xor.a.f2` | `xor.z` | 1.226 ± 0.068 | 1.147 ± 0.096 | 0.936 | -0.67 | hold | hold |
| `xor.z` | `add.z` | -0.082 ± 0.069 | 0.115 ± 0.109 | -1.406 | +1.52 | hold | hold |

**Family B: the 24 ladder quantities, board** (units as each name carries them: fJ per bit or per position, pJ where named; s* 1.03493):

| price | aifoundry3 (E192) | card 1 (E199) | m1 / m3 | z | T1 | T2 |
|---|---:|---:|---:|---:|---|---|
| `hamming_f2_slope_fJ` | 62.683 ± 2.242 | 87.768 ± 6.324 | 1.400 | +3.74 | **miss** | **miss** |
| `hamming_f2_quad_fJ` | 0.152 ± 0.952 | -0.340 ± 1.433 | -2.239 | -0.29 | hold | hold |
| `add_f0_fJ_per_bit` | 112.440 ± 3.210 | 116.809 ± 4.718 | 1.039 | +0.77 | hold | hold |
| `add_f1_fJ_per_bit` | 76.313 ± 3.627 | 93.266 ± 5.093 | 1.222 | +2.71 | **miss** | **miss** |
| `add_f2_fJ_per_bit` | 62.736 ± 2.239 | 88.321 ± 6.504 | 1.408 | +3.72 | **miss** | **miss** |
| `add_f3_fJ_per_bit` | 56.393 ± 4.159 | 62.310 ± 6.623 | 1.105 | +0.76 | hold | hold |
| `add_f12_fJ_per_bit` | 76.276 ± 1.812 | 80.601 ± 3.117 | 1.057 | +1.20 | hold | hold |
| `additivity_all_minus_fields_pJ` | 0.025 ± 0.123 | -0.432 ± 0.224 | -17.388 | -1.79 | hold | hold |
| `f12_minus_f1_f2_pJ` | 0.216 ± 0.068 | -0.326 ± 0.135 | -1.510 | -3.59 | **miss** | **miss** |
| `and_f1_fJ_per_bit` | 12.534 ± 3.861 | 26.519 ± 5.346 | 2.116 | +2.12 | **miss** | **miss** |
| `and_f2_fJ_per_bit` | 9.520 ± 3.787 | 21.331 ± 5.907 | 2.241 | +1.68 | hold | hold |
| `and_f3_fJ_per_bit` | 6.363 ± 3.389 | 16.897 ± 6.941 | 2.655 | +1.36 | hold | hold |
| `and12_fJ_per_bit` | 11.027 ± 3.567 | 23.925 ± 4.069 | 2.170 | +2.38 | **miss** | **miss** |
| `d12_a12_minus_and12_fJ_per_bit` | 65.249 ± 4.602 | 56.676 ± 5.933 | 0.869 | -1.14 | hold | hold |
| `add_f2_minus_f3_fJ_per_bit` | 6.343 ± 4.245 | 26.011 ± 5.603 | 4.100 | +2.80 | **miss** | **miss** |
| `and_f2_minus_f3_fJ_per_bit` | 3.157 ± 2.404 | 4.434 ± 8.873 | 1.405 | - | ND | ND |
| `S_cr_fJ_per_position` | 18.376 ± 1.198 | 17.530 ± 2.418 | 0.954 | -0.31 | hold | hold |
| `S_crb_fJ_per_position` | 63.793 ± 2.092 | 60.774 ± 1.482 | 0.953 | -1.18 | hold | hold |
| `S_cr_quad_fJ` | -0.015 ± 0.245 | -0.104 ± 0.408 | 7.037 | -0.19 | hold | hold |
| `S_crb_quad_fJ` | -0.666 ± 0.113 | 0.026 ± 0.265 | -0.039 | +2.40 | **miss** | **miss** |
| `C1_carry_fJ_per_position` | 2.946 ± 1.458 | -1.148 ± 1.721 | -0.390 | -1.82 | hold | hold |
| `C2_fJ_per_bit` | -4.403 ± 4.503 | 5.246 ± 3.886 | -1.191 | +1.62 | hold | hold |
| `C3_fJ_per_bit` | 15.430 ± 1.423 | 18.679 ± 2.120 | 1.211 | +1.27 | hold | hold |
| `ripple_minus_add_z_pJ` | 4.059 ± 0.042 | 4.248 ± 0.135 | 1.047 | - | ND | ND |

**Family C: the 31 per-arm contrasts against their controls, core rail** (pJ an instruction; s* 1.03707):

| price | control | aifoundry3 (E192) | card 1 (E199) | m1 / m3 | z | T1 | T2 |
|---|---|---:|---:|---:|---:|---|---|
| `add.a.all` | `add.z` | 4.612 ± 0.021 | 4.812 ± 0.035 | 1.043 | +4.90 | **miss** | hold |
| `add.a.f0` | `add.z` | 1.574 ± 0.029 | 1.670 ± 0.035 | 1.061 | +2.11 | **miss** | hold |
| `add.a.f1` | `add.z` | 1.136 ± 0.039 | 1.173 ± 0.057 | 1.032 | +0.54 | hold | hold |
| `add.a.f12` | `add.z` | 2.207 ± 0.017 | 2.303 ± 0.024 | 1.044 | +3.30 | **miss** | hold |
| `add.a.f2` | `add.z` | 0.976 ± 0.025 | 1.124 ± 0.034 | 1.152 | +3.55 | **miss** | **miss** |
| `add.a.f2.k4` | `add.z` | 0.251 ± 0.018 | 0.272 ± 0.028 | 1.085 | +0.64 | hold | hold |
| `add.a.f2.k8` | `add.z` | 0.532 ± 0.030 | 0.556 ± 0.042 | 1.045 | +0.46 | hold | hold |
| `add.a.f3` | `add.z` | 0.817 ± 0.022 | 0.809 ± 0.029 | 0.990 | -0.22 | hold | hold |
| `add.b.f0` | `add.z` | 1.553 ± 0.040 | 1.649 ± 0.039 | 1.062 | +1.72 | hold | hold |
| `add.b.f2` | `add.z` | 0.956 ± 0.020 | 0.973 ± 0.026 | 1.018 | +0.52 | hold | hold |
| `add.cr.l0` | `add.z` | 0.039 ± 0.023 | 0.060 ± 0.027 | 1.562 | +0.61 | hold | hold |
| `add.cr.l16` | `add.cr.l0` | 0.255 ± 0.028 | 0.268 ± 0.052 | 1.051 | +0.22 | hold | hold |
| `add.cr.l24` | `add.cr.l0` | 0.352 ± 0.035 | 0.365 ± 0.030 | 1.036 | +0.27 | hold | hold |
| `add.cr.l31` | `add.cr.l0` | 0.497 ± 0.037 | 0.490 ± 0.032 | 0.985 | -0.16 | hold | hold |
| `add.cr.l8` | `add.cr.l0` | 0.121 ± 0.031 | 0.053 ± 0.022 | 0.442 | -1.76 | hold | hold |
| `add.crb.l0` | `add.z` | 0.045 ± 0.030 | 0.066 ± 0.033 | 1.465 | +0.47 | hold | hold |
| `add.crb.l16` | `add.crb.l0` | 1.009 ± 0.030 | 0.984 ± 0.047 | 0.975 | -0.45 | hold | hold |
| `add.crb.l24` | `add.crb.l0` | 1.378 ± 0.018 | 1.472 ± 0.030 | 1.068 | +2.73 | **miss** | hold |
| `add.crb.l31` | `add.crb.l0` | 1.806 ± 0.036 | 1.800 ± 0.037 | 0.996 | -0.13 | hold | hold |
| `add.crb.l8` | `add.crb.l0` | 0.513 ± 0.039 | 0.530 ± 0.044 | 1.032 | +0.28 | hold | hold |
| `add.ripple` | `add.z` | 3.851 ± 0.030 | 4.032 ± 0.029 | 1.047 | +4.33 | **miss** | hold |
| `add.s.f0` | `add.z` | 0.829 ± 0.017 | 0.880 ± 0.028 | 1.061 | +1.54 | hold | hold |
| `add.s.f2` | `add.z` | 0.300 ± 0.020 | 0.335 ± 0.041 | 1.117 | +0.77 | hold | hold |
| `add.same` | `nop` | 0.248 ± 0.016 | 0.340 ± 0.020 | 1.373 | +3.64 | **miss** | **miss** |
| `add.z` | `add.same` | 0.810 ± 0.012 | 0.813 ± 0.027 | 1.003 | +0.08 | hold | hold |
| `and.a.f1` | `and.z` | 0.181 ± 0.051 | 0.221 ± 0.017 | 1.220 | +0.74 | hold | hold |
| `and.a.f2` | `and.z` | 0.173 ± 0.032 | 0.231 ± 0.029 | 1.336 | +1.35 | hold | hold |
| `and.a.f3` | `and.z` | 0.121 ± 0.033 | 0.186 ± 0.026 | 1.545 | +1.58 | hold | hold |
| `and.z` | `add.z` | 0.041 ± 0.028 | 0.028 ± 0.015 | 0.675 | -0.42 | hold | hold |
| `xor.a.f2` | `xor.z` | 1.081 ± 0.019 | 1.078 ± 0.041 | 0.998 | -0.05 | hold | hold |
| `xor.z` | `add.z` | 0.024 ± 0.028 | 0.068 ± 0.030 | 2.850 | +1.08 | hold | hold |

**Family D: the 24 ladder quantities, core rail** (units as each name carries them: fJ per bit or per position, pJ where named; s* 1.03707):

| price | aifoundry3 (E192) | card 1 (E199) | m1 / m3 | z | T1 | T2 |
|---|---:|---:|---:|---:|---|---|
| `hamming_f2_slope_fJ` | 61.152 ± 1.633 | 70.411 ± 2.206 | 1.151 | +3.37 | **miss** | **miss** |
| `hamming_f2_quad_fJ` | -0.545 ± 0.342 | 0.117 ± 0.605 | -0.214 | +0.95 | hold | hold |
| `add_f0_fJ_per_bit` | 98.370 ± 1.826 | 104.348 ± 2.158 | 1.061 | +2.11 | **miss** | hold |
| `add_f1_fJ_per_bit` | 71.028 ± 2.407 | 73.326 ± 3.543 | 1.032 | +0.54 | hold | hold |
| `add_f2_fJ_per_bit` | 60.977 ± 1.557 | 70.255 ± 2.096 | 1.152 | +3.55 | **miss** | **miss** |
| `add_f3_fJ_per_bit` | 51.045 ± 1.393 | 50.554 ± 1.804 | 0.990 | -0.22 | hold | hold |
| `add_f12_fJ_per_bit` | 68.954 ± 0.532 | 71.975 ± 0.746 | 1.044 | +3.30 | **miss** | hold |
| `additivity_all_minus_fields_pJ` | 0.110 ± 0.050 | 0.036 ± 0.100 | 0.329 | -0.66 | hold | hold |
| `f12_minus_f1_f2_pJ` | 0.094 ± 0.044 | 0.006 ± 0.078 | 0.063 | -0.98 | hold | hold |
| `and_f1_fJ_per_bit` | 11.328 ± 3.200 | 13.825 ± 1.060 | 1.220 | +0.74 | hold | hold |
| `and_f2_fJ_per_bit` | 10.807 ± 2.009 | 14.443 ± 1.793 | 1.336 | +1.35 | hold | hold |
| `and_f3_fJ_per_bit` | 7.542 ± 2.060 | 11.654 ± 1.602 | 1.545 | +1.58 | hold | hold |
| `and12_fJ_per_bit` | 11.067 ± 2.306 | 14.134 ± 1.279 | 1.277 | +1.16 | hold | hold |
| `d12_a12_minus_and12_fJ_per_bit` | 57.887 ± 2.370 | 57.841 ± 1.165 | 0.999 | -0.02 | hold | hold |
| `add_f2_minus_f3_fJ_per_bit` | 9.932 ± 2.558 | 19.700 ± 1.738 | 1.984 | +3.16 | **miss** | **miss** |
| `and_f2_minus_f3_fJ_per_bit` | 3.265 ± 2.570 | 2.789 ± 2.358 | 0.854 | -0.14 | hold | hold |
| `S_cr_fJ_per_position` | 15.700 ± 0.783 | 16.546 ± 1.032 | 1.054 | +0.65 | hold | hold |
| `S_crb_fJ_per_position` | 57.414 ± 0.519 | 58.294 ± 0.864 | 1.015 | +0.87 | hold | hold |
| `S_cr_quad_fJ` | 0.047 ± 0.112 | 0.073 ± 0.125 | 1.549 | +0.15 | hold | hold |
| `S_crb_quad_fJ` | -0.230 ± 0.103 | -0.301 ± 0.116 | 1.310 | -0.46 | hold | hold |
| `C1_carry_fJ_per_position` | 2.080 ± 0.514 | 1.432 ± 0.519 | 0.689 | -0.89 | hold | hold |
| `C2_fJ_per_bit` | -2.553 ± 2.351 | -0.980 ± 1.540 | 0.384 | +0.56 | hold | hold |
| `C3_fJ_per_bit` | 13.620 ± 0.579 | 15.114 ± 1.040 | 1.110 | +1.25 | hold | hold |
| `ripple_minus_add_z_pJ` | 3.851 ± 0.030 | 4.032 ± 0.029 | 1.047 | +4.33 | **miss** | hold |

**The pooled temperature slope** the correction used (`beta_W_per_C`, measured): card 1 board 0.1372 W per °C, core rail -0.0562 W per °C (sum dT² 0.938 °C²); aifoundry3 0.0552 and 0.0496 W per °C (17.377 °C²). Note 1 section 4 says what that spread means for the corrected prices (REPORTED and post hoc); the registered reading decides (E199.md 6.5 and 6.6).

**E151's rail filter** ([`railfilter-e199.json`](railfilter-e199.json), measured): 22 of 36,150 samples removed (F1 22, F2 22, union 22); in every one the rail read 33.625 W, the running maximum the same sample reports. The unfiltered reduction beside it ([`intbits-e199-unfiltered.json`](intbits-e199-unfiltered.json)) is REPORTED and decides nothing.

## 5. Beside verify-e199d's independent re-derivation

verify-e199d (Q191) re-derived the filter, the reduction and the scores on this directory's committed raw files with its own code, importing nothing from the kit (REPORTED: its outputs were read here, not re-run, and compared with the files above by a desk check of code):

- **The filter:** the same 22 of 36,150 samples removed, their times and values equal (its `filter` block: F1 22, F2 22, union 22).
- **The reduction:** 10,572 fields compared, filtered and unfiltered (arms, ladders, uncorrected ladders, beta and the 324 runs), 0 mismatches; the largest relative difference 3.8e-13.
- **The scorer:** 818 fields compared, 0 mismatches; its eight words are the committed eight.
- **Price by price (computed here from its rows):** over the 110 prices of families A-D, the decided flag and the T1 and T2 outcomes are the same in 110 of 110; across the decided prices the largest absolute difference in m1 is 9.9e-13, in se1 1.0e-12, in d 9.9e-13, in its SE 8.3e-13 and in the ratio 8.5e-12 (the largest relative difference 2.5e-12).

| family | verify-e199d: decided; T1 hold / miss; T2 hold / miss at s*; s_hat ± SE | committed (`scores-e199.json`) | the same |
|---|---|---|---|
| A | 29; FAIL 21 / 8; FAIL 23 / 6 at 1.033935; 1.040798 ± 0.023685 | 29; FAIL 21 / 8; FAIL 23 / 6 at 1.033935; 1.040798 ± 0.023685 | yes |
| B | 22; FAIL 14 / 8; FAIL 14 / 8 at 1.034930; 1.057128 ± 0.045241 | 22; FAIL 14 / 8; FAIL 14 / 8 at 1.034930; 1.057128 ± 0.045241 | yes |
| C | 31; FAIL 24 / 7; PASS 29 / 2 at 1.037070; 1.044037 ± 0.005808 | 31; FAIL 24 / 7; PASS 29 / 2 at 1.037070; 1.044037 ± 0.005808 | yes |
| D | 24; FAIL 18 / 6; PASS 21 / 3 at 1.037070; 1.045896 ± 0.008585 | 24; FAIL 18 / 6; PASS 21 / 3 at 1.037070; 1.045896 ± 0.008585 | yes |

R1 and R2 (REPORTED, no verdict): its T1 and T2 hold counts (0 and 0; 1 and 6) and s_hat (1.278361; 1.102861) are the committed ones. **They agree.**

## 6. verify-e199d's findings, answered

verify-e199d read the data commit `6d1f3a5a` and step 13's outputs: HOLDS WITH FIXES, two low findings and five nits, none of them a fault in a datum or a verdict. Each, with a dated clause:

1. **Finding 1 (low): step 13's `scores-e199.json` holds the scratch home path its command line gave the scorer (`card1_file` > `path`), which names a login.** *Answered (Mon 16 Nov 2026, lane reduce-e199):* the committed `scores-e199.json` is the registered scorer's output on the byte-identical reduction, given the reduction by its repository path (`docs/reports/data/2026-11-16-e199-intbits-aifoundry1-c1/intbits-e199.json`). Against step 13's file (`64d3b218...`) it differs in 1 of its 2,748 values, that path, and in 1 of its 3,200 lines; its `card1_file` > `sha256` (`5033f861...`), every verdict, count, scale, z and ratio are equal. This lane made it from its own extract of `6d1f3a5a` (section 2), and it is byte for byte the file note 1 section 1 made from the lab clone (`69a55603...`). No lab file holds the home path.
2. **Finding 2 (low): no null rate beside the six FAILs (E199.md 6.8).** *Answered (Mon 16 Nov 2026):* note 1 section 2 gave them, and section 3 above sets each beside its FAIL from E199.md 6.8's 8-pass row: E199-T1 1.5%, E199-T2 0.3%, T1L 6.3%, T2L 1.5%, T1R 2.3%, T1RL 4.3%.
3. **Nit 3: step 12's delay of about 19 minutes and the card lane's change to its own scripts are not in the README.** *Answered in note 1 section 3; nothing more here.*
4. **Nit 4: `window.env`'s label on the recording time.** *Answered in note 1 section 5: no change needed (nothing reads it; the bounds are G's).*
5. **Nit 5: card 1's pooled slopes rest on a small temperature spread.** *Answered in note 1 section 4 (with verify-e199d's post hoc readings without the slope and without the filter, REPORTED); section 4 above sets the slopes beside the prices. The registered reading decides.*
6. **Nit 6: the box manifest's launch output is not committed.** *Answered in note 1 section 5: it is byte for byte `session/session.log`; no change.*
7. **Nit 7: the checker's checks 1 and 2 count all 9 passes while its used passes are 1-8.** *Answered in note 1 section 5: the verdicts are the same either way; `checks-e199.json` is committed as the registered checker wrote it.*

Its open items: the sealed card-1 forecast's numbers were NOT CHECKED against lab files by verify-e199d; none is in any file this note adds (the public-text scan below, which also looks for its sha256). The card lane's own scratch on aifoundry2 is not a lab file.

## 7. Checks before the commit

This note was committed only after each of these read clean (this lane's scripts; desk checks of code):

- the lists in an assembled copy of this directory as it will be: `SHA256SUMS` 35 of 35, `SHA256SUMS-note1` 3 of 3, `SHA256SUMS-note2` 12 of 12, and only `SHA256SUMS-note2` itself in no list;
- the lab's desk-path gate (`nopath_q142s.py` v3.1), the login check, the lab's sanitizer and the round's tier classes: 0 hits over the twelve new files and the commit message;
- new files only: no committed file changes; the commit made under the round's desk-commit rule (the quiet hold absent and no card lane in its desk span, both read just before the commit).

## What does not change

`README.md`, `SHA256SUMS`, note 1 and `SHA256SUMS-note1`; E199's registration and kit; every word step 13 printed. The eight verdicts stand as printed: E199-T1 FAIL and E199-T2 FAIL (the headline), E199-T1L FAIL, E199-T2L FAIL, E199-T1R FAIL, E199-T2R PASS, E199-T1RL FAIL, E199-T2RL PASS.
