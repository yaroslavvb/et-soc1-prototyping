# E200 sitting 1's data README, dated note 2 (Mon 16 Nov 2026): step 13's outputs on this sitting alone, run on the data commit `548d736e` at 09:02:50-52 PST, committed beside it byte for byte with both programs' printed lines; this sitting's measured, reduced prices at 800 MHz; the data verifier's re-derivation agrees

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `548d736e` (09:02:36 PST Mon 16 Nov 2026),
and note 1's two files ([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and [`SHA256SUMS-note1`](SHA256SUMS-note1), `839151a2`,
10:58:42 PST), which stay as committed too. Written on aifoundry2 from about 11:15 PST on Mon 16 Nov 2026 (week 47) by the clock, desk
only (no card, no lab box, no device, no post), by Q192's lane `reduce-e200`, after the card lane `card-e200`, the data verifier
`verify-e200d` (holds with fixes, the fixes documentation only) and note 1 (`fix-e200d`). The kit's step 13
([`rb/s24_reduce_e200.sh`](../../../../tools/claims-v3/e200/rb/s24_reduce_e200.sh)) leaves its outputs to "the records lane", which
"commits them beside the data in a later commit"; README.md's section "Reduced (not here)" says they "are committed beside it by a later
lane in a dated note, which fills this section", and note 1 section 5 names that note: this file. This note commits this sitting's four
outputs, states when and on which commit step 13 ran, gives this sitting's measured, reduced prices, THE CLOCK RULE's counts and the
checks' words as printed, sets the data verifier's re-derivation beside them and answers each finding the verifier named with a dated
clause. **This is sitting 1 alone, not E200's result:** sitting 2 ran, so the pooled reduction of both sittings, committed in the same
commit in sitting 2's directory by its note 2
([`../2026-11-16-e200-regfile-sitting-2-aifoundry2/README.md.dated-note-2.md`](../2026-11-16-e200-regfile-sitting-2-aifoundry2/README.md.dated-note-2.md)),
is E200's registered result (E200.md 6), with THE REPORTED COMPARISON with E197 there. Here T7 and T14 (block E's, sitting 2's) did not
run, so they and the two prices built on them read NOT SCORED, and T1 has 134 of its 364 planned processes. **No number, price, rule, verdict, check or gate reading changes, and nothing is scored. The forecast stays sealed (the lab knows it
only by its sha256, `2eba6ef4b60241674628dde125273db4547b0ba17dd6d5a3e30935c7c6e89733`, E200.md section 0): no forecast number is
here, and nothing here scores E200 against it; the model session scores it privately against these published prices.** Interpreter:
`/usr/bin/python3` 3.12.3 (`-I -B`) on aifoundry2, standard library only, for step 13 and for this lane's re-run. Labels: **registered** ([`E200.md`](../../../../tools/claims-v3/e200/E200.md), E197.md by reference, the kit as committed),
**measured** (the sessions' committed records, and the registered reduction's and the kit checker's outputs from them), **desk check
of code** (this lane's re-run and comparisons), **post hoc** (desk arithmetic after the data, deciding nothing), **REPORTED**
(verify-e200d's and fix-e200d's figures, not re-run here, and the registered comparison with E197, which decides nothing).*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`regfile-e200-s1.json`](regfile-e200-s1.json) | the registered reduction's output (its `--out`) on this sitting alone, byte for byte | 43,232 | `aa18f2d8c6fac8a0dc2838a2610a006e4c58615864ced7bbf6ac75dd16ffdf24` |
| [`regfile-e200-s1.txt`](regfile-e200-s1.txt) | the reduction's printed lines (38 lines), the runbook's capture of that call, which step 13 copies here, byte for byte | 3,455 | `9e0702013f9f86951d3fbd6ccb6b514b4e21ad68effeea89d33adf55464c035f` |
| [`checks-e200-1.json`](checks-e200-1.json) | the kit checker's output (`check_e200.py checks ... --out`), byte for byte | 29,443 | `eaae1105046de09406f69632395bd7321ef72a30c5b27d8321a9725dba0c3099` |
| [`checks-e200-1.txt`](checks-e200-1.txt) | the checker's printed lines (111 lines), the runbook's capture of that call, byte for byte | 15,414 | `462aa153bc700e93b6a4a6062f90a0d509994b6e6dd6010a35d6a0154133540d` |
| `README.md.dated-note-2.md` | this note | | in `SHA256SUMS-note2` |
| [`SHA256SUMS-note2`](SHA256SUMS-note2) | the sha256 of the 5 files above | | |

All four outputs are byte for byte what step 13 wrote, and the two JSON files' sha256 are the ones note 1 section 5 published before this
commit. Step 13 copies the reduction's capture to `regfile-e200-s1.txt` (`cp "$RB_CAP" "${OUTJ%.json}.txt"`) but leaves the checker's
capture in the runbook's folder of call captures: `checks-e200-1.txt` is that capture, unchanged, named after `checks-e200-1.json`. No
output carries a desk path, so nothing is redacted. Nothing else in this directory changes.

## 2. When, where and on which commit the reduction and the checker ran

- **The step.** Step 13 of card-e200's runbook for sitting 1, `rb/s24_reduce_e200.sh 1` on this directory, run on aifoundry2 inside the
  round's CPU slot at 09:02:50 PST on Mon 16 Nov 2026. Its seven calls end at 09:02:50-52, rc 0, 14-16 s after the data commit
  (`548d736e`, committed at 09:02:36 and pushed by 09:02:42).
- **The runbook's log: its seven lines for the step** (lines 93-99 of sitting 1's runbook log, kept with the round's records). Each time
  is the end of its call; the command fields are left out here, and the two programs' calls are given below.

```
09:02:50 read  the data directory committed (a commit names it): docs/reports/data/2026-11-16-e200-regfile-sitting-1-aifoundry2   0.0 s  rc 0
09:02:50 read  the data directory clean                                          0.0 s  rc 0
09:02:50 read  the data's SHA256SUMS, every entry                                0.0 s  rc 0
09:02:50 read  the history check                                                 0.2 s  rc 0
09:02:50 read  E200's registered reduction at its sha256 (10a44034...) and E197's reducer it loads (f325bd0e...)   0.0 s  rc 0
09:02:52 desk  E200'S REGISTERED REDUCTION, unchanged, on the committed data (reduce_e200.py sitting-1 --out ...; never --prediction)   1.2 s  rc 0
09:02:52 desk  the kit's checker: E197.md 8's rows, the clock row by C1 with its tallies (check_e200.py checks)   0.0 s  rc 0
```

  What the five reads printed, from the runbook's captures: the commit naming the directory is `548d736e` ("E200 data: X02's scalar
  register file on aifoundry2 card 0 under its governor, sitting 1, RAN WHOLE ..."); the directory clean (no line); `SHA256SUMS` 36 of 36
  entries OK; "HISTORY OK: 141 files added since 72514ce5 on E200's paths, none changed or removed; ... nothing under tools/claims-v3/e200
  or tools/claims-v3/e197 changed since; nothing untracked; ..."; and the two programs at `10a44034...` and `f325bd0e...`. The script
  stops before the reduction unless all five hold. It then copied `run/runs.jsonl` and `run/marks.jsonl` and unpacked
  `run/telemetry.jsonl.gz`, checked each copy against `session/MANIFEST.sha256` (the box's bytes) and printed "each sitting's run/ files
  (the telemetry unpacked) equal the box's manifest's sha256".
- **The two calls, as logged** (`<RB_OUT>` stands for the runbook's output folder on the desk):

```
/usr/bin/python3 -I -B tools/claims-v3/e200/reduce_e200.py <RB_OUT>/e200-reduce-1/sitting-1 --out <RB_OUT>/regfile-e200-s1.json
/usr/bin/python3 -I -B tools/claims-v3/e200/check_e200.py checks <RB_OUT>/regfile-e200-s1.json --out <RB_OUT>/checks-e200-1.json
```

  This is README.md's "Re-make it" form, run on copies of the committed records; the registered reduction never had `--prediction`.
- **The files' times.** `regfile-e200-s1.json` and the reduction's capture 09:02:52.009, `regfile-e200-s1.txt` 09:02:52.156,
  `checks-e200-1.json` and the checker's capture 09:02:52.193 PST: each at the end of its call as logged. Their sha256 are note 1's (the
  two JSON files) and this lane's re-run's, so nothing changed them after the step.
- **The printed lines.** `regfile-e200-s1.txt` is byte-equal to the runbook's capture of the reduction's call, and `checks-e200-1.txt` is
  the capture of the checker's call. Each of their 38 and 111 lines is in the card lane's log of step 13.
- **On which commit.** The lab clone's reflog shows HEAD at `548d736e` from 09:02:36 to 09:19:44, so the step ran on the data commit
  itself. This lane compared each copy with the data commit's blob: 3 of 3 equal, the telemetry after unpacking, and each at its line in
  the session's manifest (desk check). The session wrote no `run/STOP`.
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
  `548d736e`'s own tree (this directory's `run/`, `session/MANIFEST.sha256` and `SHA256SUMS`, `reduce_e200.py`, `check_e200.py` and
  E197's `proposal/src/`; nothing read from the clone's working tree), inside the round's CPU slot and its no-device sandbox. The
  export's record lines of `SHA256SUMS` read OK and its three run files read "the box's bytes". Both returned rc 0, and all four outputs
  are byte for byte step 13's. verify-e200d's re-run of the committed programs and of README.md's "Re-make it" lines gave the same bytes
  (REPORTED).

## 3. This sitting's measured, reduced prices (sitting 1 alone)

Every figure in this section is **measured**: the registered reduction's output on this sitting's committed records, read from
[`regfile-e200-s1.json`](regfile-e200-s1.json), which holds them in full. The trains' D are rounded to 4 decimals and the prices to 4
significant figures. D is a train's estimate of board power, its F kind less its S kind, in W: the mean over its units of the quads' s (L2 + L3 - L1 -
L4) / 2, with the t(0.975, n - 1) interval (E197.md 7), each process read on its quads 2 and 3 only (C2, E200.md 4). A price is
energy per instruction: the train's D, or the registered combination of trains shown, over the median device rate in instructions a
second (the median of those trains' median rates, all at 800 MHz), divided by the bits the trains hold apart where it is a price per
bit. POSITIVE or NEGATIVE: the whole 95 % interval on one side of zero. BOUNDED: the registered reading for one of the five prices
zero by design or by a linear law (`order`, `lin_result`, `lin_field`, `dest_n8`, `read_n8`) whose interval holds zero; its interval
is the bound (E197.md 7). The last two columns of each table are the data verifier's own re-derivation and the largest relative
difference between its numbers and the kit's on that row (section 6). Prices at 800 MHz only (E200.md 0).

**3a. The trains (sitting 1).** 13 of 15 scored (T7 and T14 belong to block E, sitting 2's); every unit pairs an F and an S process. The
clock set aside T1 3, T3 1, T5 1, T12 1 processes (section 4); no process was dropped for another reason. Every train but T1 ran whole in
this sitting, so T2-T6, T8-T13 and T15 read the same here as in the pooled reduction; T1 pools 176 units there against 64 here.

| train | F - S (registered kinds) | what it holds apart (trains.tsv, registered) | processes (of the plan) | set aside by the clock | units | D, F - S (W) | 95 % interval (W) | the reducer's word | F/S rate | verify-e200d: D [interval] | largest relative difference |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | `rot.x64` - `rot2.x64` | cells: every write changes 64 stored bits (F) or none (S); same source, port and result stream, same field changes | 134 (of 364) | 3 | 64 | +0.0370 | [+0.0311, +0.0429] | POSITIVE | 1.00003 | +0.0370 [+0.0311, +0.0429] | < 1e-13 |
| T2 | `rot.x0` - `rot2.x0` | check for T1: the same two forms on an image where no write changes a cell (designed difference 0) | 18 (of 18) | 0 | 9 | -0.0166 | [-0.0323, -0.0009] | NEGATIVE | 1.00005 | -0.0166 [-0.0323, -0.0009] | < 1e-13 |
| T3 | `res.k64` - `res.k0` | the result path: 64 result bits change per instruction, sources fixed, destinations hold | 18 (of 18) | 1 | 8 | +3.8020 | [+3.7842, +3.8197] | POSITIVE | 0.99997 | +3.8020 [+3.7842, +3.8197] | < 1e-14 |
| T4 | `res.k32` - `res.k0` | the same at 32 bits (linearity of T3) | 18 (of 18) | 0 | 9 | +1.9166 | [+1.9014, +1.9319] | POSITIVE | 1.00000 | +1.9166 [+1.9014, +1.9319] | < 1e-14 |
| T5 | `resf.k0` - `resz.k0` | one register write (x5, value unchanged) against a write to x0 | 52 (of 52) | 1 | 25 | +0.0869 | [+0.0771, +0.0968] | POSITIVE | 1.00000 | +0.0869 [+0.0771, +0.0968] | < 1e-14 |
| T6 | `wn2.z` - `wn1.z` | two destinations in turn (one field bit apart) against one destination | 18 (of 18) | 0 | 9 | +0.1333 | [+0.1110, +0.1557] | POSITIVE | 1.00000 | +0.1333 [+0.1110, +0.1557] | < 1e-15 |
| T7 | `wn8.z` - `wn2.z` | eight destinations in turn against two, one field bit per step (bounded) | 0 (of 18) | - | 0 | - | - | NOT SCORED (not run in this sitting) | - | NOT SCORED | - |
| T8 | `rd2i.d64` - `rd2i.e0` | bits 24:20 of an immediate instruction name two registers that differ in 64 bits (F) or hold zero (S) | 18 (of 18) | 0 | 9 | +0.2793 | [+0.2624, +0.2962] | POSITIVE | 0.99997 | +0.2793 [+0.2624, +0.2962] | < 1e-14 |
| T9 | `rd2i.e64` - `rd2i.e0` | the same two named registers both all ones (F) or both zero (S): no bit changes, ones held | 26 (of 26) | 0 | 13 | +0.3554 | [+0.3424, +0.3683] | POSITIVE | 1.00003 | +0.3554 [+0.3424, +0.3683] | < 1e-13 |
| T10 | `rd2r.d64` - `rd2r.e0` | the two registers read as the second operand, result held at zero by and with x0 | 18 (of 18) | 0 | 9 | +0.9480 | [+0.9249, +0.9711] | POSITIVE | 0.99997 | +0.9480 [+0.9249, +0.9711] | < 1e-15 |
| T11 | `rd1u.d64` - `rd1u.e0` | bits 19:15 of an upper-immediate instruction name the two registers | 18 (of 18) | 0 | 9 | +0.3224 | [+0.3031, +0.3417] | POSITIVE | 1.00000 | +0.3224 [+0.3031, +0.3417] | < 1e-15 |
| T12 | `idx5.z` - `idx1.z` | the second source field changes in 5 bits against 1 (zero contents) | 18 (of 18) | 1 | 8 | +0.4254 | [+0.4012, +0.4496] | POSITIVE | 0.99995 | +0.4254 [+0.4012, +0.4496] | < 1e-14 |
| T13 | `idx1.z` - `idx0.z` | the second source field changes in 1 bit against not at all (zero contents) | 26 (of 26) | 0 | 13 | +0.1837 | [+0.1657, +0.2018] | POSITIVE | 1.00010 | +0.1837 [+0.1657, +0.2018] | < 1e-13 |
| T14 | `rn8.z` - `idx1.z` | eight source registers in turn against two, one field bit per step (bounded) | 0 (of 18) | - | 0 | - | - | NOT SCORED (not run in this sitting) | - | NOT SCORED | - |
| T15 | `idx3.z` - `idx1.z` | the second source field changes in 3 bits against 1 (zero contents): the field ladder 0, 1, 3, 5 | 18 (of 18) | 0 | 9 | +0.1963 | [+0.1800, +0.2127] | POSITIVE | 0.99997 | +0.1963 [+0.1800, +0.2127] | < 1e-14 |

**3b. The derived prices, in pJ of board energy per event.**

| price | from the trains (registered) | per | board pJ, mean | 95 % interval (pJ) | the reducer's word | verify-e200d: pJ [interval] | largest relative difference |
|---|---|---|---|---|---|---|---|
| `cell` | T1 / 64 | bit | +0.0008273 | [+0.0006947, +0.0009600] | POSITIVE | +0.0008273 [+0.0006947, +0.0009600] | < 1e-13 |
| `cell_ctrl` | (T1 - T2) / 64 | bit | +0.001199 | [+0.000834, +0.001564] | POSITIVE | +0.001199 [+0.000834, +0.001564] | < 1e-14 |
| `order` | T2 | instr | -0.02378 | [-0.04628, -0.00129] | NEGATIVE | -0.02378 [-0.04628, -0.00129] | < 1e-13 |
| `result_bit` | T3 / 64 | bit | +0.08502 | [+0.08462, +0.08542] | POSITIVE | +0.08502 [+0.08462, +0.08542] | < 1e-14 |
| `result_bit32` | T4 / 32 | bit | +0.08572 | [+0.08504, +0.08640] | POSITIVE | +0.08572 [+0.08504, +0.08640] | < 1e-14 |
| `lin_result` | T4 - T3 / 2 | instr | +0.02242 | [-0.00119, +0.04603] | BOUNDED | +0.02242 [-0.00119, +0.04603] | < 1e-13 |
| `write` | T5 | instr | +0.1244 | [+0.1103, +0.1385] | POSITIVE | +0.1244 [+0.1103, +0.1385] | < 1e-14 |
| `dest_switch` | T6 | instr | +0.1908 | [+0.1588, +0.2228] | POSITIVE | +0.1908 [+0.1588, +0.2228] | < 1e-15 |
| `dest_n8` | T7 | instr | - | - | NOT SCORED (T7 did not run in this sitting) | NOT SCORED | - |
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
| `read_n8` | T14 | instr | - | - | NOT SCORED (T14 did not run in this sitting) | NOT SCORED | - |

**3c. The same prices in the other units the reduction writes** (gain-corrected, electrons through the 12 V input, the core-rail share and
electrons through the core rail; the rail's figures REPORTED with E200.md 15's caveat, as in sitting 2's note 2, section 3c):

| price | gain-corrected board pJ, mean [interval] | electrons through the 12 V input | core-rail pJ (REPORTED, the climb's caveat) | electrons through the core rail (the same caveat) |
|---|---|---|---|---|
| `cell` | +0.0008514 [+0.0007149, +0.0009879] | 430 | +0.0006901 | 6,958 |
| `cell_ctrl` | +0.001234 [+0.000858, +0.001609] | 624 | +0.001000 | 10,084 |
| `order` | -0.02448 [-0.04763, -0.00133] | -12,371 | -0.01984 | -200,033 |
| `result_bit` | +0.08749 [+0.08709, +0.08790] | 44,220 | +0.07091 | 715,042 |
| `result_bit32` | +0.08822 [+0.08751, +0.08892] | 44,585 | +0.07150 | 720,936 |
| `lin_result` | +0.02307 [-0.00122, +0.04737] | 11,662 | +0.01870 | 188,577 |
| `write` | +0.1280 [+0.1135, +0.1425] | 64,690 | +0.1037 | 1,046,031 |
| `dest_switch` | +0.1963 [+0.1634, +0.2292] | 99,229 | +0.1591 | 1,604,525 |
| `dest_n8` | - | - | - | - |
| `read2_field` | +0.006428 [+0.006039, +0.006817] | 3,249 | +0.005210 | 52,529 |
| `read2_net` | +0.002338 [+0.001936, +0.002741] | 1,182 | +0.001895 | 19,111 |
| `held_one` | +0.004089 [+0.003940, +0.004238] | 2,067 | +0.003314 | 33,418 |
| `read2_operand` | +0.02182 [+0.02129, +0.02235] | 11,026 | +0.01768 | 178,294 |
| `operand_path` | +0.01539 [+0.01478, +0.01600] | 7,778 | +0.01247 | 125,777 |
| `read1_field` | +0.007419 [+0.006975, +0.007864] | 3,750 | +0.006013 | 60,632 |
| `field_bit` | +0.1566 [+0.1477, +0.1655] | 79,157 | +0.1269 | 1,279,971 |
| `field_bit3` | +0.1446 [+0.1325, +0.1566] | 73,072 | +0.1172 | 1,181,563 |
| `lin_field` | -0.02408 [-0.05169, +0.00352] | -12,172 | -0.01952 | -196,817 |
| `field_first` | +0.2706 [+0.2440, +0.2972] | 136,750 | +0.2193 | 2,211,233 |
| `field_base` | +0.1139 [+0.0866, +0.1413] | 57,590 | +0.0924 | 931,219 |
| `read_n8` | - | - | - | - |

**3d. Beside the prices.**

- **The cell reading:** "cell_ctrl" ("order (T2) reads NEGATIVE"): T2 reads NEGATIVE, so `cell_ctrl` is read first (E197.md 7).
- **The train gain:** 0.9717 (T3's D over the median of the anchors' 8 burst differences, 3.9126 W; flagged: no). The
  differences (W): 3.9412, 4.0276, 3.8809, 3.9965, 3.9173, 3.9080, 3.7267, 3.8435.
- **The rail share:** 0.8341, the median of 8 (0.8268, 0.5603, 1.1647, 0.5974, 0.7932, 0.8414, 0.8812, 0.8522); **V_rail** 0.619 V
  (REPORTED, the caveat of 3c).
- **The telemetry:** 26,113 samples, the session clock's median 800 MHz; 232 board samples set aside by the two dip rules; the
  participants gate 1,024; stops seen by the reduction: none (`[{"session": "sitting-1", "t_ms": null, "from": null}]`).
- **The anchors:** 24 bursts, each of 7 or 8 launches; the largest drift between a block's first and last burst of one kind is
  0.4085 W, against the registered 0.3 W; 2 of 12 pairs are flagged (section 5).

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

## 4. THE CLOCK RULE's counts (C1 and C2, applied by the reduction after the data commit)

The reduction's `e200` line, as printed (in [`regfile-e200-s1.txt`](regfile-e200-s1.txt), line 38):

```
e200 sitting-1: median clock 800.0 MHz (ok); train processes judged 400, kept by the clock 394, set aside: median 0, samples after 1.5 s 6, no last launch 0, own count 0; launches asked 5122, before 2.0 s not read 1970, read 3152, unmatched 0; anchor groups 24, board windows moved 24, off 800 MHz after 1.5 s 0; samples 26113 (0 without a clock, 4754 off 800 MHz)
```

| THE CLOCK RULE's count (the reduction's `e200` tallies) | sitting 1 |
|---|---|
| the session's median clock (MHz); within 1 MHz of 800 | 800.0; yes |
| train processes judged | 400 |
| kept by the clock (counted) | 394 |
| set aside: the session's median clock | 0 |
| set aside: a sample off 800 MHz after the first launch's start + 1.5 s | 6 |
| set aside: no last launch | 0 |
| set aside: the last launch's own count outside 780-810 MHz | 0 |
| launches asked of the kept processes | 5,122 |
| not read: started before the first launch's start + 2.0 s (C2) | 1,970 |
| read as E197 reads them | 3,152 |
| unmatched | 0 |
| anchor bursts; board windows moved to + 2.0 s (C2); off 800 MHz after 1.5 s | 24; 24; 0 |
| telemetry samples; without a clock; off 800 MHz | 26,113; 0; 4,754 |

These fill README.md's row "C1, THE CLOCK RULE (the reduction's), C2 (nothing read before 2.0 s): applied after the data commit". **Kept
by the clock: 394 of 400 train processes** (measured), the 6 set aside all by the clause on samples after the 1.5 s allowance
(T1 3, T3 1, T5 1, T12 1): the six C3 judged OFF live, never two in a row (README.md; the same six: verify-e200d, REPORTED). C2 left 1,970 launches unread (launches 0-4 of every kept
process, the settling launch and quad 1) and moved all 24 anchor bursts' board windows to + 2.0 s.

## 5. The checks, as the checker printed them (measured)

The checker's last line, as printed: **"CHECKS READ: 110 rows (APPLIED 17, FLAGGED 1, NOT SCORED 2, PASS 13, REPORTED 77)"**. Its rows are in [`checks-e200-1.json`](checks-e200-1.json) in full
and in [`checks-e200-1.txt`](checks-e200-1.txt) as printed: one row of THE CLOCK RULE (APPLIED); per train one gates row (APPLIED), one
gate row (PASS, or NOT SCORED for T7 and T14, which did not run in this sitting) and five REPORTED rows; then four closing rows.

| train | gates (APPLIED): processes of the plan, units, dropped | gate: rates within 0.05 %, 8 units | F/S rate | retired / body, F and S (flagged?) | instruction-cache misses per iteration, F and S; F over S | L1 data misses, median per launch, F and S | launches with a slow hart, F and S | rail-voltage samples off, of all in the spans |
|---|---|---|---|---|---|---|---|---|
| T1 | 134 of 364, 64, clock 3 | PASS | 1.00003 | 1.023438 (no); 1.023438 (no) | 1.876e-06; 1.817e-06; 1.032 | 19,303; 19,281 | 187; 208 | 512 of 6,954 |
| T2 | 18 of 18, 9, none | PASS | 1.00005 | 1.023438 (no); 1.023438 (no) | 1.876e-06; 1.817e-06; 1.032 | 19,304; 19,281 | 25; 26 | 66 of 952 |
| T3 | 18 of 18, 8, clock 1 | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 1.759e-06; 1.759e-06; 1.000 | 12,288; 12,288 | 45; 35 | 51 of 897 |
| T4 | 18 of 18, 9, none | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 1.759e-06; 1.759e-06; 1.000 | 12,288; 12,288 | 44; 53 | 75 of 955 |
| T5 | 52 of 52, 25, clock 1 | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 1.700e-06; 1.701e-06; 1.000 | 12,292; 10,246 | 99; 109 | 202 of 2,703 |
| T6 | 18 of 18, 9, none | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 1.701e-06; 1.701e-06; 1.000 | 10,248; 10,248 | 36; 39 | 64 of 953 |
| T7 | 0 of 18, 0, none | NOT SCORED | - | -; - | -; -; - | -; - | 0; 0 | 0 of 0 |
| T8 | 18 of 18, 9, none | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 1.701e-06; 1.701e-06; 1.000 | 16,104; 16,080 | 69; 74 | 62 of 958 |
| T9 | 26 of 26, 13, none | PASS | 1.00003 | 1.023438 (no); 1.023438 (no) | 1.701e-06; 1.701e-06; 1.000 | 16,108; 16,076 | 86; 79 | 101 of 1,380 |
| T10 | 18 of 18, 9, none | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 1.700e-06; 1.700e-06; 1.000 | 16,086; 16,051 | 41; 38 | 62 of 954 |
| T11 | 18 of 18, 9, none | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 1.700e-06; 1.700e-06; 1.000 | 16,080; 16,044 | 46; 50 | 76 of 958 |
| T12 | 18 of 18, 8, clock 1 | PASS | 0.99995 | 1.023438 (no); 1.023438 (no) | 1.702e-06; 1.700e-06; 1.001 | 15,356; 14,084 | 39; 28 | 52 of 899 |
| T13 | 26 of 26, 13, none | PASS | 1.00010 | 1.023438 (no); 1.023438 (no) | 1.700e-06; 1.701e-06; 1.000 | 14,108; 13,988 | 40; 61 | 89 of 1,378 |
| T14 | 0 of 18, 0, none | NOT SCORED | - | -; - | -; -; - | -; - | 0; 0 | 0 of 0 |
| T15 | 18 of 18, 9, none | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 1.701e-06; 1.700e-06; 1.000 | 16,128; 14,081 | 40; 36 | 78 of 957 |

| row (E197.md 8, as the checker names it) | kind | word | what it printed |
|---|---|---|---|
| the anchors' first and last bursts of a block within 0.3 W | report | FLAGGED | `{"flagged": [["sitting-1", "A", "res.k0", 0.32211188811188407], ["sitting-1", "A", "res.k64", 0.40848717948717805]], "pairs": 12}` |
| the train gain (T3 over the anchors' burst difference) within 0.95-1.05 (outside: the gain-corrected prices first) | report | REPORTED | `{"train_gain": 0.9717081356303519}` |
| the cell reading (order, T2, BOUNDED: cell; else cell_ctrl first) | reading rule | REPORTED | `{"read": "cell_ctrl", "why": "order (T2) reads NEGATIVE"}` |
| the stops seen by the reducer (a process ending after a STOP gives no value) | gate | APPLIED | `{"stops": [{"session": "sitting-1", "t_ms": null, "from": null}]}` |

- **The FLAGGED row** is a report, not a gate (E197.md 8: "flagged per block and kind"): 2 of 12 pairs drifted more than 0.3 W
  (block A, `res.k0`, +0.3221 W; block A, `res.k64`, +0.4085 W). It removes no datum.
- **The rail row** reads high by design on this card (README.md, "Reading the checker's rail row"; KIT.md 7): the spans include each
  process's climb at the 600 MHz point's lower voltage. Never a gate.

## 6. Beside verify-e200d's independent re-derivation

- **Its numbers (REPORTED).** This sitting's reduction: 1,114 values compared, 0 mismatches, largest relative difference 5.5e-14 among
  them (1.2e-13 over both of its comparisons); the checker's 110 rows, every verdict and 307 detail values equal; its re-run of the kit's
  programs and of README.md's "Re-make it" lines gave step 13's bytes.
- **This lane's comparison** (desk check, leaf by leaf over the keys both hold): 783 numeric values compared, 637 exactly equal,
  the largest relative difference 5.5e-14. By part:
  - trains: 277 compared, 246 exactly equal, largest relative difference < 1e-13;
  - derived: 335 compared, 220 exactly equal, largest relative difference < 1e-13;
  - anchors and drifts: 132 compared, 132 exactly equal, largest relative difference 0;
  - THE CLOCK RULE's tallies: 17 compared, 17 exactly equal, largest relative difference 0;
  - the rest (shares, bursts, gain, V_rail, clocks, samples, dips, stops, cell reading): 22 compared, 22 exactly equal, largest relative difference 0;

  307 words compared: 307 equal. The checker's 110 rows: every verdict word equal; 195 detail values compared, 195 exactly
  equal.

## 7. The verifier's findings, answered (dated clauses, Mon 16 Nov 2026)

| verify-e200d | what | answered |
|---|---|---|
| F1 (low, documentation) | in each sitting one collected file, fwgate's read record, differs from its line in the box's manifest (`session/MANIFEST.sha256`): the registered scrub wrote the box's home as "~" in its ledger path | Note 1 section 1 (`839151a2`) gives the dated sentence. *Mon 16 Nov 2026:* that record is not an input of the reduction. Step 13 read `run/runs.jsonl`, `run/marks.jsonl` and `run/telemetry.jsonl.gz` unpacked, each at its manifest line (the box's bytes), as step 13 checked before the reducer ran and this lane's re-run checked again (section 2); the scrub touched none of them, so the outputs committed here stand on the box's bytes. |
| F2 (nit) | "the sitting's first holder check" (E197.md 6) read two ways: step 7's first command or step 4's look | Note 1 section 2 (with fix-e200d's extension: under the other reading sitting 2's card time would read 45.2 minutes against its cap of 35). *Mon 16 Nov 2026:* KIT.md 4, stated before any datum, decides: the look sends nothing to the card, so sitting 2's rest (40.2 minutes) and cap (26.45 of 35) held and the pooled reduction, committed in sitting 2's note 2, is E200's registered result. This sitting's own reduction, committed here, would be E200's result under the other reading; both are committed, and nothing is re-scored. |
| F3 (information; post hoc) | the processes THE CLOCK RULE set aside were not slow climbs (each reached 800 MHz, then left it once for about 1.1-1.2 s) | Note 1 section 3. *Mon 16 Nov 2026:* the reduction committed here set aside the same six processes, by C1's clause "a sample off 800 MHz after the first launch's start + 1.5 s" and by no other clause (section 4), the processes C3 judged OFF live. |
| F4 (information; REPORTED) | instruction-cache misses per iteration, F over S: T7 1.103 and T14 1.069 (T1 and T2 1.032) | Note 1 section 4 (sitting 2's). *Mon 16 Nov 2026:* T7 and T14 did not run in this sitting; the pooled checks in sitting 2's note 2 carry the two ratios. |
| F5 (information) | sitting 2 sent the firmware read a second time on this boot, as E200.md 8 registers it per sitting; it read EQUAL | Sitting 2's note 1, section 5 (it concerns sitting 2 alone). *Mon 16 Nov 2026:* nothing here bears on it: the reduction reads no firmware record. |
| F6 (nit) | four pinned E200 files write "Mon 16 Nov 2026 (week 46)"; the ISO week is 47 | Note 1 section 4. *Mon 16 Nov 2026:* this note writes week 47; the pinned files stay as committed. |

## 8. Checks before the commit

- **The sums.** `SHA256SUMS-note2` reads back, 5 of 5. In the lab clone, README.md's `SHA256SUMS` (36 of 36) and
  `SHA256SUMS-note1` still read back, and nothing in this directory changed since note 1's commit. The same holds in sitting 2's directory,
  which this commit fills with its own note 2.
- **New files only.** None of the 6 names was in this directory before this commit.
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

README.md, `SHA256SUMS` and note 1's two files stay as committed, and no committed file changes. No number, price, rule, verdict, check or
gate reading changes; nothing is scored, and no forecast number is here.

SPDX-License-Identifier: Apache-2.0
