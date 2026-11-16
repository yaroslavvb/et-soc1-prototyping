# E200 sitting 2's data README, dated note 2 (Mon 16 Nov 2026): step 13's pooled outputs, run on the data commits `548d736e` and `ca53ed29` at 10:06:48-51 PST, committed beside them byte for byte with both programs' printed lines; E200's measured, reduced prices at 800 MHz (its registered result); the data verifier's re-derivation agrees; THE REPORTED COMPARISON with E197

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `ca53ed29` (10:06:26 PST Mon 16 Nov
2026), and note 1's four files ([`README.md.dated-note-1.md`](README.md.dated-note-1.md), [`posthoc_note1_e200.py`](posthoc_note1_e200.py),
[`posthoc-note1-e200.txt`](posthoc-note1-e200.txt) and [`SHA256SUMS-note1`](SHA256SUMS-note1), `839151a2`, 10:58:42 PST), which stay
as committed too. Written on aifoundry2 from about 11:15 PST on Mon 16 Nov 2026 (week 47) by the clock, desk only (no card, no lab box,
no device, no post), by Q192's lane `reduce-e200`, after the card lane `card-e200` (both data commits and step 13), the data verifier
`verify-e200d` (holds with fixes, the fixes documentation only: none of its findings is a fault in a datum, the reduction, a check, the
clock rule, the seal, a gate or a release) and note 1 (`fix-e200d`). The kit's step 13
([`rb/s24_reduce_e200.sh`](../../../../tools/claims-v3/e200/rb/s24_reduce_e200.sh)) runs only after the data commits and leaves its
outputs to a later commit: "Its outputs go to RB_OUT (the json, its printed table, the checks); the records lane commits them beside the
data in a later commit." README.md's section "Reduced (not here)" says the same ("a later lane commits them beside the data in a dated
note, which fills this section"), and note 1 section 7 names that note: this file. This note commits the pooled run's four outputs,
states when and on which commits step 13 ran, gives E200's measured, reduced prices (the pooled reduction is E200's registered result,
E200.md 6), THE CLOCK RULE's counts and the checks' words as printed, sets the data verifier's re-derivation beside them, gives THE
REPORTED COMPARISON with E197 (E200.md 14) with its two files, and answers each finding the verifier named with a dated clause. Sitting 1's
own reduction is committed in sitting 1's directory by its note 2
([`../2026-11-16-e200-regfile-sitting-1-aifoundry2/README.md.dated-note-2.md`](../2026-11-16-e200-regfile-sitting-1-aifoundry2/README.md.dated-note-2.md)),
in the same commit. **No number, price, rule, verdict, check or gate reading changes, and nothing is scored. The forecast stays sealed (the lab knows it
only by its sha256, `2eba6ef4b60241674628dde125273db4547b0ba17dd6d5a3e30935c7c6e89733`, E200.md section 0): no forecast number is
here, and nothing here scores E200 against it; the model session scores it privately against these published prices.** Interpreter: `/usr/bin/python3` 3.12.3 (`-I -B`) on aifoundry2, standard library only, for step 13 and for
this lane's re-run and comparison. Labels: **registered** ([`E200.md`](../../../../tools/claims-v3/e200/E200.md), E197.md by reference, the kit as committed),
**measured** (the sessions' committed records, and the registered reduction's and the kit checker's outputs from them), **desk check
of code** (this lane's re-run and comparisons), **post hoc** (desk arithmetic after the data, deciding nothing), **REPORTED**
(verify-e200d's and fix-e200d's figures, not re-run here, and the registered comparison with E197, which decides nothing).*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`regfile-e200.json`](regfile-e200.json) | the registered reduction's output (its `--out`), the pooled run of both sittings: E200's registered result, byte for byte | 47,615 | `9e70c813a1e140f867bdc6434a354ded9bbc3b8d8379d07df03f91d97983cfde` |
| [`regfile-e200.txt`](regfile-e200.txt) | the reduction's printed lines (39 lines), the runbook's capture of that call, which step 13 copies here, byte for byte | 3,856 | `73f4409fb6e78232236790d011438ab8bb8a91a99148b123e76104fbdc0bae89` |
| [`checks-e200-2.json`](checks-e200-2.json) | the kit checker's output (`check_e200.py checks ... --out`), byte for byte | 30,792 | `9e72317aceb4cda82fb1f34ec5dd13ed440dc56c99f41260527f1d2c7e5d891b` |
| [`checks-e200-2.txt`](checks-e200-2.txt) | the checker's printed lines (112 lines), the runbook's capture of that call, byte for byte | 16,187 | `e3e498954242699088d7a3b278b00aa03b45bf1762aeffcacba3e889b42e4d25` |
| [`compare-e200.json`](compare-e200.json) | THE REPORTED COMPARISON with E197 (E200.md 14): `compare_e200.py`'s `--out`, run by this lane in its registered form (section 7) | 11,285 | `f2f44f45747bf02d8c0fc2bdfe0da3d3f010a7eff7c10f6bcaed891c8658f3fb` |
| [`compare-e200.txt`](compare-e200.txt) | its printed lines (25 lines), stdout and stderr together | 3,583 | `8192fab86c983d28f0e96562c1b65dcd696b10b331ef8a266a063525bf1a88a2` |
| `README.md.dated-note-2.md` | this note | | in `SHA256SUMS-note2` |
| [`SHA256SUMS-note2`](SHA256SUMS-note2) | the sha256 of the 7 files above | | |

All four step-13 outputs are byte for byte what step 13 wrote, and the two JSON files' sha256 are the ones note 1 section 7 published
before this commit. Step 13 copies the reduction's capture to `regfile-e200.txt` (`cp "$RB_CAP" "${OUTJ%.json}.txt"`) but leaves the
checker's capture in the runbook's folder of call captures: `checks-e200-2.txt` is that capture, unchanged, named after
`checks-e200-2.json` (E197's `checks-e197-1.txt` is the same kind of file). No output carries a desk path, so nothing is redacted.
Nothing else in this directory changes.

## 2. When, where and on which commits the reduction and the checker ran

- **The step.** Step 13 of card-e200's runbook for sitting 2, `rb/s24_reduce_e200.sh 2`, run on aifoundry2 inside the round's CPU slot
  at 10:06:48 PST on Mon 16 Nov 2026. Its ten calls end at 10:06:48-51, rc 0, 22-25 s after sitting 2's data commit (`ca53ed29`,
  committed at 10:06:26 and pushed by 10:06:31); sitting 1's (`548d736e`) had been committed at 09:02:36.
- **The runbook's log: its ten lines for the step** (lines 86-95 of sitting 2's runbook log, kept with the round's records). Each time is
  the end of its call; the command fields are left out here, and the two programs' calls are given below.

```
10:06:48 read  the data directory committed (a commit names it): docs/reports/data/2026-11-16-e200-regfile-sitting-1-aifoundry2   0.0 s  rc 0
10:06:48 read  the data directory clean                                          0.0 s  rc 0
10:06:48 read  the data's SHA256SUMS, every entry                                0.0 s  rc 0
10:06:48 read  the data directory committed (a commit names it): docs/reports/data/2026-11-16-e200-regfile-sitting-2-aifoundry2   0.0 s  rc 0
10:06:48 read  the data directory clean                                          0.0 s  rc 0
10:06:48 read  the data's SHA256SUMS, every entry                                0.0 s  rc 0
10:06:48 read  the history check                                                 0.2 s  rc 0
10:06:48 read  E200's registered reduction at its sha256 (10a44034...) and E197's reducer it loads (f325bd0e...)   0.0 s  rc 0
10:06:50 desk  E200'S REGISTERED REDUCTION, unchanged, on the committed data (reduce_e200.py sitting-1 sitting-2: the pooled reduction --out ...; never --prediction)   2.1 s  rc 0
10:06:51 desk  the kit's checker: E197.md 8's rows, the clock row by C1 with its tallies (check_e200.py checks)   0.0 s  rc 0
```

  What the eight reads printed, from the runbook's captures: the commits naming the two directories, `548d736e` ("E200 data: X02's scalar
  register file on aifoundry2 card 0 under its governor, sitting 1, RAN WHOLE ...") and `ca53ed29` ("... sitting 2, RAN WHOLE ..."); both
  directories clean (no line); `SHA256SUMS` 36 of 36 entries OK in each; "HISTORY OK: 141 files added since 72514ce5 on E200's paths, none
  changed or removed; E197's registration ea4b4ad7f7a7; E197's kit 2c68a6338fb2; the registration 7361cc243ecd; the kit b4a5f6f2bbe1:
  nothing under tools/claims-v3/e200 or tools/claims-v3/e197 changed since; nothing untracked; ..."; and the two programs at
  `10a44034...` and `f325bd0e...`. The script stops before the reduction unless all eight hold. It then copied each sitting's
  `run/runs.jsonl` and `run/marks.jsonl` and unpacked `run/telemetry.jsonl.gz`, checked each copy against its session's
  `session/MANIFEST.sha256` (the box's bytes) and printed "each sitting's run/ files (the telemetry unpacked) equal the box's manifest's
  sha256".
- **The two calls, as logged** (`<RB_OUT>` stands for the runbook's output folder on the desk):

```
/usr/bin/python3 -I -B tools/claims-v3/e200/reduce_e200.py <RB_OUT>/e200-reduce-2/sitting-1 <RB_OUT>/e200-reduce-2/sitting-2 --out <RB_OUT>/regfile-e200.json
/usr/bin/python3 -I -B tools/claims-v3/e200/check_e200.py checks <RB_OUT>/regfile-e200.json --out <RB_OUT>/checks-e200-2.json
```

  This is README.md's "Re-make it" form, run on copies of the committed records; the registered reduction never had `--prediction`
  (it refuses it).
- **The files' times.** `regfile-e200.json` and the reduction's capture 10:06:50.685, `regfile-e200.txt` 10:06:50.972,
  `checks-e200-2.json` and the checker's capture 10:06:51.008 PST: each at the end of its call as logged. Their sha256 are note 1's (the
  two JSON files) and this lane's re-run's, so nothing changed them after the step.
- **The printed lines.** `regfile-e200.txt` is byte-equal to the runbook's capture of the reduction's call, and `checks-e200-2.txt` is the
  capture of the checker's call. Each of their 39 and 112 lines is in the card lane's log of step 13. The runbook's capture
  takes a program's stdout and stderr together, as they come.
- **On which commits.** The lab clone's reflog shows HEAD at `ca53ed29` from 10:06:26 and at `4a59c4ec` from 10:06:50 (another lane's
  commit, E197's data directory only). The step's copies were made at 10:06:48, from HEAD `ca53ed29`; the trees of both E200 data
  directories, of `tools/claims-v3/e200/` and of `tools/claims-v3/e197/` are the same at `ca53ed29` and `4a59c4ec`, object for object,
  and those of sitting 1's directory and of both tool folders are the same at `548d736e` (desk check). This lane compared each copy with
  the data commits' blobs: 6 of 6 equal, the telemetry after unpacking, and each at its line in its session's manifest (desk check).
  Neither session wrote a `run/STOP`.
- **The programs.**
  - E200's registered reduction [`reduce_e200.py`](../../../../tools/claims-v3/e200/reduce_e200.py), sha256
    `10a4403430b20686050ccfc7ae1af3db2107f6ccc56511bfc00a6c8056c147ef` (E200.md 6), which loads E197's registered reducer
    [`reduce_regfile.py`](../../../../tools/claims-v3/e197/proposal/src/reduce_regfile.py) by its path and checks its sha256,
    `f325bd0e3e916b81ee12304db7b47d79ad6daa5172ded19952f0ef1b0565eb87`, before it reads anything, and runs it with THE CLOCK RULE's three
    functions in place (C1 and C2); E197's train table beside it, [`trains.tsv`](../../../../tools/claims-v3/e197/proposal/src/trains.tsv),
    `6c6d723177ad8046c476fd0a02a27134a7141118efcac6e0af44f8ff8742e6d8`. All three have the same bytes at `7361cc24` (the registration),
    `b4a5f6f2` (the kit), both data commits, `839151a2` (note 1) and today's HEAD.
  - The kit's checker [`check_e200.py`](../../../../tools/claims-v3/e200/check_e200.py), sha256
    `9fa7c9d6233fb19957d0f45a09d6235ec2b9f8a62e92ffba1927ecbbf7005e65`, pinned in
    [`SHA256SUMS-e200-kit`](../../../../tools/claims-v3/e200/SHA256SUMS-e200-kit) with the step's script, `rb/s24_reduce_e200.sh`
    (`7b9e3d96...`); both the same at `b4a5f6f2`, both data commits, `839151a2` and HEAD. No commit since the kit touches
    `tools/claims-v3/e200/` or `tools/claims-v3/e197/`.
  - All import the standard library only (`argparse`, `bisect`, `hashlib`, `json`, `math`, `os`, `re`, `statistics`, `sys`, `types`);
    desk check of code.
- **This lane's re-run** (desk check of code, 11:08:28-11:08:32 PST). Both programs ran in step 13's form on a fresh export of
  `ca53ed29`'s own tree: both data directories' `run/`, `session/MANIFEST.sha256` and `SHA256SUMS`, `reduce_e200.py`, `check_e200.py`,
  `compare_e200.py` and E197's `proposal/src/`, with nothing read from the clone's working tree. They ran inside the round's CPU slot
  and its no-device sandbox, each with its stdout and stderr in one file, as the runbook takes them. The export's record lines of each
  `SHA256SUMS` read OK and its six run files read "the box's bytes". Both returned rc 0, and all four outputs are byte for byte step 13's.
  verify-e200d's re-run of the committed reduction and checker, and of both READMEs' "Re-make it" lines, gave the same bytes (REPORTED).

## 3. E200's measured, reduced prices (the pooled reduction: its registered result)

Every figure in this section is **measured**: the registered reduction's output on the committed records of both sittings, read from
[`regfile-e200.json`](regfile-e200.json), which holds them in full. Here the trains' D are rounded to 4 decimals, as the reduction prints
them, and the prices to 4 significant figures (its printed lines round them to 4 decimals). D is a train's estimate of board power, its F kind less its S kind, in W: the mean over its units of the quads' s (L2 + L3 - L1 -
L4) / 2, with the t(0.975, n - 1) interval (E197.md 7), each process read on its quads 2 and 3 only (C2, E200.md 4). A price is
energy per instruction: the train's D, or the registered combination of trains shown, over the median device rate in instructions a
second (the median of those trains' median rates, all at 800 MHz), divided by the bits the trains hold apart where it is a price per
bit. POSITIVE or NEGATIVE: the whole 95 % interval on one side of zero. BOUNDED: the registered reading for one of the five prices
zero by design or by a linear law (`order`, `lin_result`, `lin_field`, `dest_n8`, `read_n8`) whose interval holds zero; its interval
is the bound (E197.md 7). The last two columns of each
table are the data verifier's own re-derivation and the largest relative difference between its numbers and the kit's on that row
(section 6). The prices are at the governor's 800 MHz only (E200.md 0: THE CLOCK RULE prints no price at 700 or 600 MHz).

**3a. The trains (both sittings pooled).** 15 of 15 scored; every unit pairs an F and an S process. The clock set aside
T1 6, T3 1, T5 1, T12 1 processes (section 4); no process was dropped for another reason.

| train | F - S (registered kinds) | what it holds apart (trains.tsv, registered) | processes (of the plan) | set aside by the clock | units | D, F - S (W) | 95 % interval (W) | the reducer's word | F/S rate | verify-e200d: D [interval] | largest relative difference |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | `rot.x64` - `rot2.x64` | cells: every write changes 64 stored bits (F) or none (S); same source, port and result stream, same field changes | 364 (of 364) | 6 | 176 | +0.0356 | [+0.0322, +0.0390] | POSITIVE | 1.00003 | +0.0356 [+0.0322, +0.0390] | < 1e-12 |
| T2 | `rot.x0` - `rot2.x0` | check for T1: the same two forms on an image where no write changes a cell (designed difference 0) | 18 (of 18) | 0 | 9 | -0.0166 | [-0.0323, -0.0009] | NEGATIVE | 1.00005 | -0.0166 [-0.0323, -0.0009] | < 1e-13 |
| T3 | `res.k64` - `res.k0` | the result path: 64 result bits change per instruction, sources fixed, destinations hold | 18 (of 18) | 1 | 8 | +3.8020 | [+3.7842, +3.8197] | POSITIVE | 0.99997 | +3.8020 [+3.7842, +3.8197] | < 1e-14 |
| T4 | `res.k32` - `res.k0` | the same at 32 bits (linearity of T3) | 18 (of 18) | 0 | 9 | +1.9166 | [+1.9014, +1.9319] | POSITIVE | 1.00000 | +1.9166 [+1.9014, +1.9319] | < 1e-14 |
| T5 | `resf.k0` - `resz.k0` | one register write (x5, value unchanged) against a write to x0 | 52 (of 52) | 1 | 25 | +0.0869 | [+0.0771, +0.0968] | POSITIVE | 1.00000 | +0.0869 [+0.0771, +0.0968] | < 1e-14 |
| T6 | `wn2.z` - `wn1.z` | two destinations in turn (one field bit apart) against one destination | 18 (of 18) | 0 | 9 | +0.1333 | [+0.1110, +0.1557] | POSITIVE | 1.00000 | +0.1333 [+0.1110, +0.1557] | < 1e-15 |
| T7 | `wn8.z` - `wn2.z` | eight destinations in turn against two, one field bit per step (bounded) | 18 (of 18) | 0 | 9 | +0.0167 | [+0.0083, +0.0251] | POSITIVE | 0.99995 | +0.0167 [+0.0083, +0.0251] | < 1e-14 |
| T8 | `rd2i.d64` - `rd2i.e0` | bits 24:20 of an immediate instruction name two registers that differ in 64 bits (F) or hold zero (S) | 18 (of 18) | 0 | 9 | +0.2793 | [+0.2624, +0.2962] | POSITIVE | 0.99997 | +0.2793 [+0.2624, +0.2962] | < 1e-14 |
| T9 | `rd2i.e64` - `rd2i.e0` | the same two named registers both all ones (F) or both zero (S): no bit changes, ones held | 26 (of 26) | 0 | 13 | +0.3554 | [+0.3424, +0.3683] | POSITIVE | 1.00003 | +0.3554 [+0.3424, +0.3683] | < 1e-13 |
| T10 | `rd2r.d64` - `rd2r.e0` | the two registers read as the second operand, result held at zero by and with x0 | 18 (of 18) | 0 | 9 | +0.9480 | [+0.9249, +0.9711] | POSITIVE | 0.99997 | +0.9480 [+0.9249, +0.9711] | < 1e-15 |
| T11 | `rd1u.d64` - `rd1u.e0` | bits 19:15 of an upper-immediate instruction name the two registers | 18 (of 18) | 0 | 9 | +0.3224 | [+0.3031, +0.3417] | POSITIVE | 1.00000 | +0.3224 [+0.3031, +0.3417] | < 1e-15 |
| T12 | `idx5.z` - `idx1.z` | the second source field changes in 5 bits against 1 (zero contents) | 18 (of 18) | 1 | 8 | +0.4254 | [+0.4012, +0.4496] | POSITIVE | 0.99995 | +0.4254 [+0.4012, +0.4496] | < 1e-14 |
| T13 | `idx1.z` - `idx0.z` | the second source field changes in 1 bit against not at all (zero contents) | 26 (of 26) | 0 | 13 | +0.1837 | [+0.1657, +0.2018] | POSITIVE | 1.00010 | +0.1837 [+0.1657, +0.2018] | < 1e-13 |
| T14 | `rn8.z` - `idx1.z` | eight source registers in turn against two, one field bit per step (bounded) | 18 (of 18) | 0 | 9 | -0.0203 | [-0.0316, -0.0091] | NEGATIVE | 0.99995 | -0.0203 [-0.0316, -0.0091] | < 1e-14 |
| T15 | `idx3.z` - `idx1.z` | the second source field changes in 3 bits against 1 (zero contents): the field ladder 0, 1, 3, 5 | 18 (of 18) | 0 | 9 | +0.1963 | [+0.1800, +0.2127] | POSITIVE | 0.99997 | +0.1963 [+0.1800, +0.2127] | < 1e-14 |

**3b. The derived prices, in pJ of board energy per event.**

| price | from the trains (registered) | per | board pJ, mean | 95 % interval (pJ) | the reducer's word | verify-e200d: pJ [interval] | largest relative difference |
|---|---|---|---|---|---|---|---|
| `cell` | T1 / 64 | bit | +0.0007960 | [+0.0007191, +0.0008729] | POSITIVE | +0.0007960 [+0.0007191, +0.0008729] | < 1e-12 |
| `cell_ctrl` | (T1 - T2) / 64 | bit | +0.001168 | [+0.000812, +0.001523] | POSITIVE | +0.001168 [+0.000812, +0.001523] | < 1e-14 |
| `order` | T2 | instr | -0.02378 | [-0.04628, -0.00129] | NEGATIVE | -0.02378 [-0.04628, -0.00129] | < 1e-13 |
| `result_bit` | T3 / 64 | bit | +0.08502 | [+0.08462, +0.08542] | POSITIVE | +0.08502 [+0.08462, +0.08542] | < 1e-14 |
| `result_bit32` | T4 / 32 | bit | +0.08572 | [+0.08504, +0.08640] | POSITIVE | +0.08572 [+0.08504, +0.08640] | < 1e-14 |
| `lin_result` | T4 - T3 / 2 | instr | +0.02242 | [-0.00119, +0.04603] | BOUNDED | +0.02242 [-0.00119, +0.04603] | < 1e-13 |
| `write` | T5 | instr | +0.1244 | [+0.1103, +0.1385] | POSITIVE | +0.1244 [+0.1103, +0.1385] | < 1e-14 |
| `dest_switch` | T6 | instr | +0.1908 | [+0.1588, +0.2228] | POSITIVE | +0.1908 [+0.1588, +0.2228] | < 1e-15 |
| `dest_n8` | T7 | instr | +0.02392 | [+0.01187, +0.03596] | POSITIVE | +0.02392 [+0.01187, +0.03596] | < 1e-14 |
| `read2_field` | T8 / 64 | bit | +0.006246 | [+0.005868, +0.006624] | POSITIVE | +0.006246 [+0.005868, +0.006624] | < 1e-14 |
| `read2_net` | (T8 - T9 / 2) / 64 | bit | +0.002272 | [+0.001881, +0.002663] | POSITIVE | +0.002272 [+0.001881, +0.002663] | 0 |
| `held_one` | T9 / 128 | bit | +0.003973 | [+0.003829, +0.004118] | POSITIVE | +0.003973 [+0.003829, +0.004118] | < 1e-13 |
| `read2_operand` | T10 / 64 | bit | +0.02120 | [+0.02068, +0.02172] | POSITIVE | +0.02120 [+0.02068, +0.02172] | < 1e-15 |
| `operand_path` | (T10 - T8) / 64 | bit | +0.01495 | [+0.01436, +0.01555] | POSITIVE | +0.01495 [+0.01436, +0.01555] | < 1e-13 |
| `read1_field` | T11 / 64 | bit | +0.007209 | [+0.006777, +0.007641] | POSITIVE | +0.007209 [+0.006777, +0.007641] | < 1e-15 |
| `field_bit` | T12 / 4 | bit | +0.1522 | [+0.1435, +0.1608] | POSITIVE | +0.1522 [+0.1435, +0.1608] | < 1e-14 |
| `field_bit3` | T15 / 2 | bit | +0.1405 | [+0.1288, +0.1522] | POSITIVE | +0.1405 [+0.1288, +0.1522] | < 1e-14 |
| `lin_field` | T15 - T12 / 2 | instr | -0.02340 | [-0.05023, +0.00342] | BOUNDED | -0.02340 [-0.05023, +0.00342] | < 1e-13 |
| `field_first` | T13 | instr | +0.2629 | [+0.2371, +0.2887] | POSITIVE | +0.2629 [+0.2371, +0.2887] | < 1e-13 |
| `field_base` | T13 - T12 / 4 | instr | +0.1107 | [+0.0841, +0.1373] | POSITIVE | +0.1107 [+0.0841, +0.1373] | < 1e-14 |
| `read_n8` | T14 | instr | -0.02908 | [-0.04517, -0.01300] | NEGATIVE | -0.02908 [-0.04517, -0.01300] | < 1e-14 |

**3c. The same prices in the other units the reduction writes** (each from the board mean): gain-corrected (divided by the train gain,
3d), electrons through the 12 V input (pJ / (e x 12 V)), the core-rail share of it (x the rail share, 3d) and electrons through the core
rail (/ (e x V_rail)). The core rail's figures are REPORTED with E200.md 15's caveat: the rail share is read over each anchor burst's last
1.5 s against a filter's step from its first launch, and under the governor the clock's step comes up to 1.5 s later, so the per-block
shares scatter (3d). The board prices, which carry every word, are not touched by it. verify-e200d's values of these four are in section
6's count.

| price | gain-corrected board pJ, mean [interval] | electrons through the 12 V input | core-rail pJ (REPORTED, the climb's caveat) | electrons through the core rail (the same caveat) |
|---|---|---|---|---|
| `cell` | +0.0008191 [+0.0007400, +0.0008983] | 414 | +0.0006639 | 6,700 |
| `cell_ctrl` | +0.001202 [+0.000836, +0.001567] | 607 | +0.000974 | 9,828 |
| `order` | -0.02448 [-0.04763, -0.00133] | -12,371 | -0.01984 | -200,195 |
| `result_bit` | +0.08749 [+0.08709, +0.08790] | 44,220 | +0.07091 | 715,620 |
| `result_bit32` | +0.08822 [+0.08751, +0.08892] | 44,585 | +0.07150 | 721,519 |
| `lin_result` | +0.02307 [-0.00122, +0.04737] | 11,662 | +0.01870 | 188,730 |
| `write` | +0.1280 [+0.1135, +0.1425] | 64,690 | +0.1037 | 1,046,877 |
| `dest_switch` | +0.1963 [+0.1634, +0.2292] | 99,229 | +0.1591 | 1,605,822 |
| `dest_n8` | +0.02461 [+0.01222, +0.03701] | 12,440 | +0.01995 | 201,321 |
| `read2_field` | +0.006428 [+0.006039, +0.006817] | 3,249 | +0.005210 | 52,572 |
| `read2_net` | +0.002338 [+0.001936, +0.002741] | 1,182 | +0.001895 | 19,126 |
| `held_one` | +0.004089 [+0.003940, +0.004238] | 2,067 | +0.003314 | 33,445 |
| `read2_operand` | +0.02182 [+0.02129, +0.02235] | 11,026 | +0.01768 | 178,438 |
| `operand_path` | +0.01539 [+0.01478, +0.01600] | 7,778 | +0.01247 | 125,878 |
| `read1_field` | +0.007419 [+0.006975, +0.007864] | 3,750 | +0.006013 | 60,681 |
| `field_bit` | +0.1566 [+0.1477, +0.1655] | 79,157 | +0.1269 | 1,281,006 |
| `field_bit3` | +0.1446 [+0.1325, +0.1566] | 73,072 | +0.1172 | 1,182,518 |
| `lin_field` | -0.02408 [-0.05169, +0.00352] | -12,172 | -0.01952 | -196,976 |
| `field_first` | +0.2706 [+0.2440, +0.2972] | 136,750 | +0.2193 | 2,213,020 |
| `field_base` | +0.1139 [+0.0866, +0.1413] | 57,590 | +0.0924 | 931,972 |
| `read_n8` | -0.02993 [-0.04649, -0.01338] | -15,128 | -0.02426 | -244,813 |

**3d. Beside the prices.**

- **The cell reading:** "cell_ctrl" ("order (T2) reads NEGATIVE"). E197.md 7's reading rule: `cell` (T1 / 64) is the stored-bit price when
  `order` (T2) reads BOUNDED; when T2 reads POSITIVE or NEGATIVE, `cell_ctrl` is read first. T2, the designed-zero check for T1, reads
  NEGATIVE here (section 3a), so `cell_ctrl` is read first.
- **The train gain:** 0.9717 (T3's D over the median of the anchors' 10 `res.k64` - `res.k0` burst differences,
  3.9126 W; flagged outside 0.95-1.05: no), so the board prices are read first. The differences (W), in the anchors'
  order: 3.9412, 4.0276, 3.8809, 3.9965, 3.9173, 3.9080, 3.7267, 3.8435, 3.8505, 3.9802.
- **The rail share:** 0.8341, the median of 10 (0.8268, 0.5603, 1.1647, 0.5974, 0.7932, 0.8414, 0.8812, 0.8522, 0.8613, 0.8130); **V_rail** 0.6185 V.
  REPORTED with the caveat in 3c: the per-block shares scatter as E200.md 15 foresaw on a synthetic session.
- **The telemetry:** 26,113, 15,816 samples (sittings 1 and 2), the session clocks' medians 800, 800 MHz;
  232, 342 board samples set aside by the two dip rules (E197.md 7); the participants gate 1,024;
  stops seen by the reduction: none (`[{"session": "sitting-1", "t_ms": null, "from": null}, {"session": "sitting-2", "t_ms": null, "from": null}]`).
- **The anchors:** 30 bursts, the first and last of each block and kind, each of 7 or 8 launches. The largest drift between
  a block's first and last burst of one kind is 0.4085 W, against the registered 0.3 W; 3 of 15 pairs are flagged (the
  checker's row reads FLAGGED: section 5).

| sitting | block | kind | first, board over idle (W) | last (W) | last - first (W) | flagged (over 0.3 W) |
|---|---|---|---|---|---|---|
| 1 | A | `nop.z` | 9.1289 | 9.4089 | +0.2800 | no |
| 1 | A | `res.k0` | 9.6819 | 10.0041 | +0.3221 | yes |
| 1 | A | `res.k64` | 13.6232 | 14.0317 | +0.4085 | yes |
| 1 | B | `nop.z` | 9.1792 | 9.3525 | +0.1734 | no |
| 1 | B | `res.k0` | 9.8718 | 9.9365 | +0.0647 | no |
| 1 | B | `res.k64` | 13.7528 | 13.9330 | +0.1802 | no |
| 1 | C | `nop.z` | 9.2746 | 9.2997 | +0.0251 | no |
| 1 | C | `res.k0` | 9.8155 | 9.9730 | +0.1575 | no |
| 1 | C | `res.k64` | 13.7328 | 13.8810 | +0.1481 | no |
| 1 | D | `nop.z` | 9.1907 | 9.3209 | +0.1302 | no |
| 1 | D | `res.k0` | 9.7602 | 9.9330 | +0.1728 | no |
| 1 | D | `res.k64` | 13.4869 | 13.7765 | +0.2896 | no |
| 2 | E | `nop.z` | 9.1397 | 9.3330 | +0.1932 | no |
| 2 | E | `res.k0` | 9.7509 | 9.9490 | +0.1981 | no |
| 2 | E | `res.k64` | 13.6015 | 13.9292 | +0.3277 | yes |

## 4. THE CLOCK RULE's counts (C1 and C2, applied by the reduction after the data commits)

The reduction's two `e200` lines, as printed (in [`regfile-e200.txt`](regfile-e200.txt), lines 38-39):

```
e200 sitting-1: median clock 800.0 MHz (ok); train processes judged 400, kept by the clock 394, set aside: median 0, samples after 1.5 s 6, no last launch 0, own count 0; launches asked 5122, before 2.0 s not read 1970, read 3152, unmatched 0; anchor groups 24, board windows moved 24, off 800 MHz after 1.5 s 0; samples 26113 (0 without a clock, 4754 off 800 MHz)
e200 sitting-2: median clock 800.0 MHz (ok); train processes judged 266, kept by the clock 263, set aside: median 0, samples after 1.5 s 3, no last launch 0, own count 0; launches asked 3419, before 2.0 s not read 1315, read 2104, unmatched 0; anchor groups 6, board windows moved 6, off 800 MHz after 1.5 s 0; samples 15816 (0 without a clock, 1844 off 800 MHz)
```

| THE CLOCK RULE's count (the reduction's `e200` tallies) | sitting 1 | sitting 2 |
|---|---|---|
| the session's median clock (MHz); within 1 MHz of 800 | 800.0; yes | 800.0; yes |
| train processes judged | 400 | 266 |
| kept by the clock (counted) | 394 | 263 |
| set aside: the session's median clock | 0 | 0 |
| set aside: a sample off 800 MHz after the first launch's start + 1.5 s | 6 | 3 |
| set aside: no last launch | 0 | 0 |
| set aside: the last launch's own count outside 780-810 MHz | 0 | 0 |
| launches asked of the kept processes | 5,122 | 3,419 |
| not read: started before the first launch's start + 2.0 s (C2) | 1,970 | 1,315 |
| read as E197 reads them | 3,152 | 2,104 |
| unmatched | 0 | 0 |
| anchor bursts; board windows moved to + 2.0 s (C2); off 800 MHz after 1.5 s | 24; 24; 0 | 6; 6; 0 |
| telemetry samples; without a clock; off 800 MHz | 26,113; 0; 4,754 | 15,816; 0; 1,844 |

These fill README.md's row "C1, THE CLOCK RULE (the reduction's), C2 (nothing read before 2.0 s): applied after the data commit". **Kept
by the clock: 394 of 400 train processes in sitting 1 and 263 of 266 in sitting 2** (measured), every one set aside by the
clause on samples after the 1.5 s allowance and none by another clause. By train (3a): T1 6, T3 1, T5 1, T12 1. C3, the kit's live
judgment, read the same processes OFF during the sittings (6 and 3, never two in a row: the data READMEs; the same processes:
verify-e200d, REPORTED), and THE CLOCK RULE's checker rows read APPLIED for both sittings (section 5). C2 left the launches that started before 2.0 s into their process unread (launches 0-4
of every kept process, the settling launch and quad 1: 1,970 and 1,315) and moved every anchor burst's board window to its first launch's start + 2.0 s
(24 and 6). No session was set aside by its median clock.

## 5. The checks, as the checker printed them (measured)

The checker's last line, as printed: **"CHECKS READ: 111 rows (APPLIED 18, FLAGGED 1, PASS 15, REPORTED 77)"**. Its rows are E197.md 8's with the clock row read by C1, in
[`checks-e200-2.json`](checks-e200-2.json) in full and in [`checks-e200-2.txt`](checks-e200-2.txt) as printed (each row's name cut to
width there). Two rows of THE CLOCK RULE (APPLIED, one a sitting, with the tallies of section 4); per train, one gates row (APPLIED),
one gate row (PASS) and five REPORTED rows; then four closing rows. The table gives each train's rows as the checker wrote them in its
JSON (the retired-per-body rows' flag is the checker's "outside 0.5 % of 131/128 plus the entry and exit").

| train | gates (APPLIED): processes of the plan, units, dropped | gate: rates within 0.05 %, 8 units | F/S rate | retired / body, F and S (flagged?) | instruction-cache misses per iteration, F and S; F over S | L1 data misses, median per launch, F and S | launches with a slow hart, F and S | rail-voltage samples off, of all in the spans |
|---|---|---|---|---|---|---|---|---|
| T1 | 364 of 364, 176, clock 6 | PASS | 1.00003 | 1.023438 (no); 1.023438 (no) | 1.876e-06; 1.817e-06; 1.032 | 19,302; 19,281 | 512; 602 | 1,377 of 18,980 |
| T2 | 18 of 18, 9, none | PASS | 1.00005 | 1.023438 (no); 1.023438 (no) | 1.876e-06; 1.817e-06; 1.032 | 19,304; 19,281 | 25; 26 | 66 of 952 |
| T3 | 18 of 18, 8, clock 1 | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 1.759e-06; 1.759e-06; 1.000 | 12,288; 12,288 | 45; 35 | 51 of 897 |
| T4 | 18 of 18, 9, none | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 1.759e-06; 1.759e-06; 1.000 | 12,288; 12,288 | 44; 53 | 75 of 955 |
| T5 | 52 of 52, 25, clock 1 | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 1.700e-06; 1.701e-06; 1.000 | 12,292; 10,246 | 99; 109 | 202 of 2,703 |
| T6 | 18 of 18, 9, none | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 1.701e-06; 1.701e-06; 1.000 | 10,248; 10,248 | 36; 39 | 64 of 953 |
| T7 | 18 of 18, 9, none | PASS | 0.99995 | 1.023438 (no); 1.023438 (no) | 1.876e-06; 1.701e-06; 1.103 | 13,312; 10,247 | 56; 34 | 64 of 958 |
| T8 | 18 of 18, 9, none | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 1.701e-06; 1.701e-06; 1.000 | 16,104; 16,080 | 69; 74 | 62 of 958 |
| T9 | 26 of 26, 13, none | PASS | 1.00003 | 1.023438 (no); 1.023438 (no) | 1.701e-06; 1.701e-06; 1.000 | 16,108; 16,076 | 86; 79 | 101 of 1,380 |
| T10 | 18 of 18, 9, none | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 1.700e-06; 1.700e-06; 1.000 | 16,086; 16,051 | 41; 38 | 62 of 954 |
| T11 | 18 of 18, 9, none | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 1.700e-06; 1.700e-06; 1.000 | 16,080; 16,044 | 46; 50 | 76 of 958 |
| T12 | 18 of 18, 8, clock 1 | PASS | 0.99995 | 1.023438 (no); 1.023438 (no) | 1.702e-06; 1.700e-06; 1.001 | 15,356; 14,084 | 39; 28 | 52 of 899 |
| T13 | 26 of 26, 13, none | PASS | 1.00010 | 1.023438 (no); 1.023438 (no) | 1.700e-06; 1.701e-06; 1.000 | 14,108; 13,988 | 40; 61 | 89 of 1,378 |
| T14 | 18 of 18, 9, none | PASS | 0.99995 | 1.023438 (no); 1.023438 (no) | 1.818e-06; 1.700e-06; 1.069 | 16,188; 14,080 | 40; 21 | 79 of 953 |
| T15 | 18 of 18, 9, none | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 1.701e-06; 1.700e-06; 1.000 | 16,128; 14,081 | 40; 36 | 78 of 957 |

| row (E197.md 8, as the checker names it) | kind | word | what it printed |
|---|---|---|---|
| the anchors' first and last bursts of a block within 0.3 W | report | FLAGGED | `{"flagged": [["sitting-1", "A", "res.k0", 0.32211188811188407], ["sitting-1", "A", "res.k64", 0.40848717948717805], ["sitting-2", "E", "res.k64", 0.32770329670329446]], "pairs": 15}` |
| the train gain (T3 over the anchors' burst difference) within 0.95-1.05 (outside: the gain-corrected prices first) | report | REPORTED | `{"train_gain": 0.9717081356303519}` |
| the cell reading (order, T2, BOUNDED: cell; else cell_ctrl first) | reading rule | REPORTED | `{"read": "cell_ctrl", "why": "order (T2) reads NEGATIVE"}` |
| the stops seen by the reducer (a process ending after a STOP gives no value) | gate | APPLIED | `{"stops": [{"session": "sitting-1", "t_ms": null, "from": null}, {"session": "sitting-2", "t_ms": null, "from": null}]}` |

- **The FLAGGED row** is a report, not a gate (E197.md 8: "flagged per block and kind"): 3 of 15 anchor pairs drifted more than 0.3 W
  between a block's first and last burst (sitting 1, block A, `res.k0`, +0.3221 W; sitting 1, block A, `res.k64`, +0.4085 W; sitting 2, block E, `res.k64`, +0.3277 W). It removes no datum; the
  trains' quads, in A B B A order, cancel a linear drift within a block (E197.md 7), and the anchors enter only the train gain and the
  rail share (3d).
- **The rail row** ("rail voltage samples beyond +-3 mV of the session median in the train's spans") reads high by design on this card:
  every train process's span includes its climb, run at the 600 MHz point's lower voltage, so the count is no rail fault and never a gate
  (README.md, "Reading the checker's rail row"; KIT.md 7).
- **The front-end ratios** (instruction-cache misses per iteration, F over S): T7 1.103 and T14 1.069, T1 1.032 and T2 1.032, the
  other eleven 0.9996-1.0008: REPORTED, no word (E197.md 8's reading (a)); note 1 section 4 sets them beside
  E197.md 14's front-end caveat for `dest_n8` and `read_n8`.

## 6. Beside verify-e200d's independent re-derivation

verify-e200d wrote its own reducer and checks from E197.md and E200.md, importing nothing from the kit or E197's reducer, and ran them
on the committed raw files.

- **Its numbers (REPORTED).** The pooled reduction: 1,240 values compared, 0 mismatches, largest relative difference 1.2e-13; sitting
  1's: 1,114, 0 mismatches. The checker's rows: 111 and 110, every verdict equal, 332 and 307 detail values equal. Its re-run of the
  committed reduction and checker, and of both READMEs' "Re-make it" lines, gave step 13's bytes.
- **This lane's comparison of the two files** (desk check, leaf by leaf over the keys both hold; the kit-only keys, the trains' role
  texts and S kinds, and verify-e200d's own working keys are left out): 904 numeric values compared, 730 exactly equal, the
  largest relative difference 1.2e-13 (on a train's interval half-width). By part:
  - trains: 299 compared, 262 exactly equal, largest relative difference < 1e-12;
  - derived: 377 compared, 240 exactly equal, largest relative difference < 1e-12;
  - anchors and drifts: 165 compared, 165 exactly equal, largest relative difference 0;
  - THE CLOCK RULE's tallies: 34 compared, 34 exactly equal, largest relative difference 0;
  - the rest (shares, bursts, gain, V_rail, clocks, samples, dips, stops, cell reading): 29 compared, 29 exactly equal, largest relative difference 0;

  306 words (signs, verdicts, flags, kinds, dropped lists, sessions) compared: 306 equal. The checker's 111 rows against
  verify-e200d's 111: every verdict word equal; 223 detail values compared, 223 exactly equal. The two counts differ from
  verify-e200d's because each lane counts its own leaves.
- **In section 3** every train and price agrees with the verifier's at the figures shown, and to better than 1e-12 relative in full.

## 7. THE REPORTED COMPARISON with E197 (E200.md 14: registered before any datum; it decides nothing)

E200.md 14 registers it for when "E200's result and E197's (each its pooled form if its sitting 2 ran) are committed". Both are now:
E200's is the pooled reduction committed here; E197's is its sitting 1's reduction, `regfile-e197-s1.json`, committed in E197's data note
2 (`4a59c4ec`, sha256 `6c742a8b546840380d66ff11e014d57274f41d45fb4b6b4ecb31a24aeb857139`), because E197's sitting 2 did not run (E197's data
note 1). E197 ran on aifoundry3 card 0 at 600 MHz, E200 on aifoundry2 card 0 at its governor's 800 MHz. This lane ran
[`compare_e200.py`](../../../../tools/claims-v3/e200/compare_e200.py) (sha256 `02289c31757f7f55b4a1c3dd9eee86ecb7ea14d82c2ff3fe6680a3b088bc479f`,
pinned in `SHA256SUMS-e200-registration`, unchanged since `7361cc24`) in its registered form between 11:08:28 and 11:08:32 PST, inside
the CPU slot and the no-device sandbox, twice (the same bytes both times), on the bytes committed here and E197's committed file:

    /usr/bin/python3 -I -B tools/claims-v3/e200/compare_e200.py docs/reports/data/2026-11-16-e200-regfile-sitting-2-aifoundry2/regfile-e200.json docs/reports/data/2026-11-16-e197-regfile-sitting-1-aifoundry3/regfile-e197-s1.json --out compare-e200.json > compare-e200.txt

Its printed lines, as in [`compare-e200.txt`](compare-e200.txt) (REPORTED):

```
E200 / E197, REPORTED (no verdict): v2(800) = 1.423953; E190 arm A / arm B, J over idle a GEMM: bursts fp32 1.677, fp16 1.689, int8 1.796; sustained fp32 1.535, fp16 1.562, int8 1.684
E200: device rate (median over the trains) 6.9877e+11 instr/s; train gain 0.9717; session clocks [800.0, 800.0] MHz
E197: device rate (median over the trains) 5.2408e+11 instr/s; train gain 0.9885; session clocks [600.0] MHz
rate ratio E200 / E197: 1.33334
cell           E197 +0.00045 pJ [+0.00035, +0.00056] POSITIVE     E200 +0.00080 pJ [+0.00072, +0.00087] POSITIVE      ratio 1.7502 [1.2941, 2.4661]
cell_ctrl      E197 +0.00055 pJ [+0.00014, +0.00097] POSITIVE     E200 +0.00117 pJ [+0.00081, +0.00152] POSITIVE      ratio 2.1052 [0.8395, 10.7369]
order          E197 -0.00639 pJ [-0.03243, +0.01965] BOUNDED      E200 -0.02378 pJ [-0.04628, -0.00129] NEGATIVE      no ratio (not the same sign in both)
result_bit     E197 +0.05855 pJ [+0.05831, +0.05879] POSITIVE     E200 +0.08502 pJ [+0.08462, +0.08542] POSITIVE      ratio 1.4520 [1.4393, 1.4648]
result_bit32   E197 +0.05937 pJ [+0.05847, +0.06028] POSITIVE     E200 +0.08572 pJ [+0.08504, +0.08640] POSITIVE      ratio 1.4437 [1.4107, 1.4778]
lin_result     E197 +0.02624 pJ [-0.00321, +0.05568] BOUNDED      E200 +0.02242 pJ [-0.00119, +0.04603] BOUNDED       no ratio (not the same sign in both)
write          E197 +0.10566 pJ [+0.08990, +0.12142] POSITIVE     E200 +0.12437 pJ [+0.11028, +0.13846] POSITIVE      ratio 1.1771 [0.9083, 1.5402]
dest_switch    E197 +0.14099 pJ [+0.12145, +0.16053] POSITIVE     E200 +0.19078 pJ [+0.15880, +0.22276] POSITIVE      ratio 1.3531 [0.9892, 1.8341]
dest_n8        E197 -                               NOT SCORED   E200 +0.02392 pJ [+0.01187, +0.03596] POSITIVE      no ratio (not the same sign in both)
read2_field    E197 +0.00428 pJ [+0.00387, +0.00469] POSITIVE     E200 +0.00625 pJ [+0.00587, +0.00662] POSITIVE      ratio 1.4590 [1.2509, 1.7111]
read2_net      E197 +0.00143 pJ [+0.00101, +0.00186] POSITIVE     E200 +0.00227 pJ [+0.00188, +0.00266] POSITIVE      ratio 1.5844 [1.0122, 2.6381]
held_one       E197 +0.00285 pJ [+0.00269, +0.00301] POSITIVE     E200 +0.00397 pJ [+0.00383, +0.00412] POSITIVE      ratio 1.3957 [1.2730, 1.5332]
read2_operand  E197 +0.01497 pJ [+0.01468, +0.01527] POSITIVE     E200 +0.02120 pJ [+0.02068, +0.02172] POSITIVE      ratio 1.4158 [1.3545, 1.4795]
operand_path   E197 +0.01069 pJ [+0.01022, +0.01116] POSITIVE     E200 +0.01495 pJ [+0.01436, +0.01555] POSITIVE      ratio 1.3986 [1.2868, 1.5206]
read1_field    E197 +0.00555 pJ [+0.00502, +0.00608] POSITIVE     E200 +0.00721 pJ [+0.00678, +0.00764] POSITIVE      ratio 1.2984 [1.1141, 1.5216]
field_bit      E197 +0.11304 pJ [+0.10525, +0.12083] POSITIVE     E200 +0.15219 pJ [+0.14354, +0.16083] POSITIVE      ratio 1.3463 [1.1879, 1.5281]
field_bit3     E197 +0.10878 pJ [+0.09636, +0.12120] POSITIVE     E200 +0.14049 pJ [+0.12877, +0.15220] POSITIVE      ratio 1.2914 [1.0625, 1.5794]
lin_field      E197 -0.00851 pJ [-0.03589, +0.01887] BOUNDED      E200 -0.02340 pJ [-0.05023, +0.00342] BOUNDED       no ratio (not the same sign in both)
field_first    E197 +0.18410 pJ [+0.16373, +0.20447] POSITIVE     E200 +0.26292 pJ [+0.23709, +0.28875] POSITIVE      ratio 1.4281 [1.1595, 1.7636]
field_base     E197 +0.07106 pJ [+0.04986, +0.09226] POSITIVE     E200 +0.11072 pJ [+0.08414, +0.13730] POSITIVE      ratio 1.5582 [0.9121, 2.7536]
read_n8        E197 -                               NOT SCORED   E200 -0.02908 pJ [-0.04517, -0.01300] NEGATIVE      no ratio (not the same sign in both)
```

How to read it (the program's own rules, E200.md 14): every derived price both experiments read with the same sign gets the two board
prices with their 95 % intervals and the ratio, E200 over E197, with the range the two intervals' ends allow; a price NOT SCORED, BOUNDED
or NOT RESOLVED in either gets no ratio, which the program prints as "no ratio (not the same sign in both)". Here 16 of
21 prices have a ratio; `order` (BOUNDED in E197, NEGATIVE here), `lin_result` and `lin_field` (BOUNDED in both), and `dest_n8` and
`read_n8` (NOT SCORED in E197: its T7 and T14 did not run) have none. The rate ratio, 1.33334, is the two device rates'
medians over the trains, at 800 and 600 MHz. Beside the ratios, as fixed references and never thresholds: the frozen ledger's
v2(800) = 1.423953 for aifoundry2 (its per-instruction scaling from 600 to 800 MHz, by the square of the voltages), and E190's
card-to-card reading of one 8,192^3 GEMM's J over idle (another card pair and another load: a reference of scale only). **E200.md 15's
limit stands beside every ratio:** E200 against E197 changes the card, the clock (with its voltage) and the die at once, so a ratio says
how far a price moved, not which of the three moved it. No verdict word is printed, and neither experiment's sealed forecast is read: the
model session scores both privately. If E197's sitting 2 ever runs, its pooled result replaces its sitting 1's here by a later dated note
(the comparison re-run), and these two files stay as committed.

## 8. The verifier's findings, answered (dated clauses, Mon 16 Nov 2026)

| verify-e200d | what | answered |
|---|---|---|
| F1 (low, documentation) | in each sitting one collected file, fwgate's read record, differs from its line in the box's manifest (`session/MANIFEST.sha256`): the registered scrub wrote the box's home as "~" in its ledger path | Note 1 section 1 (`839151a2`) gives the dated sentence. *Mon 16 Nov 2026:* that record is not an input of the reduction. Step 13 read `run/runs.jsonl`, `run/marks.jsonl` and `run/telemetry.jsonl.gz` unpacked, each at its manifest line (the box's bytes), as step 13 checked before the reducer ran and this lane's re-run checked again (section 2); the scrub touched none of them, so the outputs committed here stand on the box's bytes. |
| F2 (nit) | "the sitting's first holder check" (E197.md 6) read two ways: step 7's first command or step 4's look | Note 1 section 2 (with fix-e200d's extension: under the other reading sitting 2's card time would read 45.2 minutes against its cap of 35). *Mon 16 Nov 2026:* KIT.md 4, stated before any datum, decides: the look sends nothing to the card, so sitting 2's rest (40.2 minutes) and cap (26.45 of 35) held and the pooled reduction committed here is E200's registered result. Sitting 1's own reduction, committed in sitting 1's note 2, would be E200's result under the other reading; both are committed beside the data, and nothing is re-scored. |
| F3 (information; post hoc) | the processes THE CLOCK RULE set aside were not slow climbs (each reached 800 MHz, then left it once for about 1.1-1.2 s) | Note 1 section 3. *Mon 16 Nov 2026:* the reduction committed here set aside the same nine (six in sitting 1, three in sitting 2) processes, by C1's clause "a sample off 800 MHz after the first launch's start + 1.5 s" and by no other clause (section 4), the processes C3 judged OFF live. |
| F4 (information; REPORTED) | instruction-cache misses per iteration, F over S: T7 1.103 and T14 1.069 (T1 and T2 1.032) | Note 1 section 4 (sitting 2's). *Mon 16 Nov 2026:* those ratios are rows of `checks-e200-2.json`, committed here (section 5: T7 1.103, T14 1.069); `dest_n8` (POSITIVE) and `read_n8` (NEGATIVE), built on T7 and T14 alone, carry E197.md 14's front-end caveat beside their words. |
| F5 (information) | sitting 2 sent the firmware read a second time on this boot, as E200.md 8 registers it per sitting; it read EQUAL | Note 1 section 5. *Mon 16 Nov 2026:* nothing here bears on it: the reduction reads no firmware record. |
| F6 (nit) | four pinned E200 files write "Mon 16 Nov 2026 (week 46)"; the ISO week is 47 | Note 1 section 6. *Mon 16 Nov 2026:* this note writes week 47; the pinned files stay as committed. |

This note also closes the card lane's open item: "The reductions' outputs are not committed ... A records lane commits them beside the
data in a dated note."

## 9. Checks before the commit

- **The sums.** `SHA256SUMS-note2` reads back, 7 of 7. In the lab clone, README.md's `SHA256SUMS` (36 of 36) and
  `SHA256SUMS-note1` still read back, and nothing in this directory changed since note 1's commit. The same holds in sitting 1's directory,
  which this commit fills with its own note 2.
- **New files only.** None of the 8 names was in this directory before this commit.
- **The desk-path gate** (`nopath_q142s.py`, v3.1) over the new files of both directories: clean.
- **The login and public-text scans** read the new files of both directories and this commit's message: the round's login check, the
  lab's sanitizer list ([`tools/timeline/sanitize_extracts.py`](../../../../tools/timeline/sanitize_extracts.py)) with this box's privacy
  table, the round's word classes, and the two scanners README.md's scan used. They found nothing in the new files. In the message, the
  only matches are the round's two standard trailer lines: the co-author line's address and the session line's link.
- **The seal.** The numbers of E197's request's withheld lines (redaction R1, E197.md section 0, which E200.md section 0 keeps), read on
  this desk from the received file (checked first by its sha256 and the withheld block's, both as E197.md registers them), searched as
  whole numbers in the new files and the message: no withheld number counts. The rule's other matches are all of its first accepted kind:
  numbers the received request also states outside its withheld lines (public in E197's committed copy since its registration). Neither
  program was given a forecast (the reduction ran without `--prediction`, which it refuses), no file here holds a word that scores one,
  and nothing here reads the sealed forecast.

## What does not change

README.md, `SHA256SUMS` and note 1's four files stay as committed, and no committed file changes. No number, price, rule, verdict, check or
gate reading changes; nothing is scored, and no forecast number is here.

SPDX-License-Identifier: Apache-2.0
