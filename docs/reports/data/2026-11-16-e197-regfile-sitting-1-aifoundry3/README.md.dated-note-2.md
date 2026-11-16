# E197 sitting 1's data README, dated note 2 (Mon 16 Nov 2026): step 13's outputs, run on the data commit `ae3c1ee0` at 06:26:11-14 PST, committed beside it byte for byte with both programs' printed lines; the measured, reduced prices; the data verifier's re-derivation agrees

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `ae3c1ee0` (06:25:28 PST Mon 16 Nov
2026), and note 1's two files ([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and [`SHA256SUMS-note1`](SHA256SUMS-note1),
`8aa6185e`, 07:12:37 PST), which stay as committed too. Written on aifoundry2 from about 07:15 PST on Mon 16 Nov 2026 (week 47) by the
clock, desk only (no card, no lab box, no device, no post), by Q191's lane `reduce-e197`, after the card lane `card-e197` (the data
commit), the data verifier `verify-e197d` (holds with fixes: one minor finding and four nits, none of them a fault in a datum, a check or
a verdict) and note 1 (`fix-e197d`). The kit's step 13 ([`rb/s24_reduce_e197.sh`](../../../../tools/claims-v3/e197/rb/s24_reduce_e197.sh))
runs only after the data commit and leaves its outputs to a later commit: "Its outputs go to RB_OUT (the json, its printed table, the
checks); the records lane commits them beside the data in a later commit." README.md's section "Reduced (not here)" says the same: they
"are committed beside it by a later lane in a dated note, which fills this section", and note 1 section 2 names that note: this file.
This note commits the four outputs, states when and on which commit step 13 ran, gives the measured, reduced prices and the checks' words
as printed, sets the data verifier's re-derivation beside them, and answers each finding the verifier named with a dated clause. **No
number, price, rule, verdict, check or gate reading changes, and nothing is scored. The forecast stays sealed (the lab knows it only by
its sha256, `e8e1746e...`, E197.md section 0): no forecast number is here, and nothing here scores E197 against it; the model session
scores it privately against these published prices.** This is sitting 1 alone: sitting 2 did not run (note 1 section 1), so T7 and T14
and the two prices built on them read NOT SCORED, and T1 has 134 of its 364 planned processes. Until a sitting 2 runs, this reduction is
E197's result (E197.md 11). Interpreter: `/usr/bin/python3` 3.12.3 (`-I -B`) on aifoundry2, standard library only, for step 13 and for
this lane's re-run. Labels: **registered** ([`E197.md`](../../../../tools/claims-v3/e197/E197.md) and the kit as committed),
**measured** (the session's committed records, and the registered reducer's and the kit checker's outputs from them), **desk check of
code** (this lane's re-run and comparisons), **post hoc** (desk arithmetic after the data, deciding nothing), **REPORTED**
(verify-e197d's and fix-e197d's figures, not re-run here).*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`regfile-e197-s1.json`](regfile-e197-s1.json) | the registered reducer's output (its `--out`), byte for byte | 42,092 | `6c742a8b546840380d66ff11e014d57274f41d45fb4b6b4ecb31a24aeb857139` |
| [`regfile-e197-s1.txt`](regfile-e197-s1.txt) | the reducer's printed lines (37 lines), the runbook's capture of that call, which step 13 copies here, byte for byte | 3,039 | `e655b38d502b5d7069366a8bed56f1394dc3a8b4b883477e981154a60d7fc54c` |
| [`checks-e197-1.json`](checks-e197-1.json) | the kit checker's output (`check_e197.py checks ... --out`), byte for byte | 27,274 | `ad69afe589821ea0f5c67187e2d15159c1f9189d381cb67f679734a2ded91355` |
| [`checks-e197-1.txt`](checks-e197-1.txt) | the checker's printed lines (110 lines), the runbook's capture of that call, byte for byte | 14,752 | `9cd4cf605cde0b95f9ba2497f8fc3ee7a0ab58535ee7262ff0a8ce113464c893` |
| `README.md.dated-note-2.md` | this note | | in `SHA256SUMS-note2` |
| [`SHA256SUMS-note2`](SHA256SUMS-note2) | the sha256 of the five files above | | |

All four outputs are byte for byte what step 13 wrote, and their sha256 are the ones note 1 section 2 published before this commit.
Step 13 copies the reducer's capture to `regfile-e197-s1.txt` (`cp "$RB_CAP" "${OUTJ%.json}.txt"`) but leaves the checker's capture in
the runbook's folder of call captures: `checks-e197-1.txt` is that capture, unchanged, named after `checks-e197-1.json` (E196's
`checks-e196.txt` is the same kind of file). No output carries a desk path, so nothing is redacted. Nothing else in this directory
changes.

## 2. When, where and on which commit the reducer and the checker ran

- **The step.** Step 13 of card-e197's runbook, `rb/s24_reduce_e197.sh 1` on this directory, run on aifoundry2 inside the round's CPU
  slot. The card lane's record gives 06:25:56 (its slot call) to 06:26:14 PST on Mon 16 Nov 2026, rc 0. The step's seven calls end at
  06:26:11-14, 43 s after the data commit (`ae3c1ee0`, committed at 06:25:28 and pushed at 06:25:33).
- **The runbook's log: its seven lines for the step** (lines 75-81 of the sitting's runbook log, kept with the round's records). Each time
  is the end of its call; the command fields are left out here, and the two programs' calls are given below.

```
06:26:11 read  the data directory committed (a commit names it): docs/reports/data/2026-11-16-e197-regfile-sitting-1-aifoundry3   0.0 s  rc 0
06:26:11 read  the data directory clean                                       0.0 s  rc 0
06:26:11 read  the data's SHA256SUMS, every entry                             0.0 s  rc 0
06:26:11 read  the history check                                              0.2 s  rc 0
06:26:11 read  the registered reducer at its sha256 (f325bd0e...)             0.0 s  rc 0
06:26:14 desk  THE REGISTERED REDUCER, unchanged, on the committed data (reduce_regfile.py sitting-1 --out ...; never --prediction)   2.4 s  rc 0
06:26:14 desk  the kit's checker: E197.md 8's rows (check_e197.py checks)      0.0 s  rc 0
```

  What the five reads printed, from the runbook's captures: the commit naming the directory is `ae3c1ee0` ("E197 data: X02's scalar
  register file, sitting 1 on aifoundry3 card 0, RAN WHOLE ..."); the directory clean (no line); `SHA256SUMS` 23 of 23 entries OK; "HISTORY
  OK: 78 files added since e8a85229 on E197's paths, none changed or removed; the registration ea4b4ad7f7a7; the kit 2c68a6338fb2: nothing
  under tools/claims-v3/e197 changed since; nothing untracked; ..."; and the reducer at `f325bd0e...`. The script stops before the reducer
  unless all five hold.
- **The two calls, as logged** (`<RB_OUT>` stands for the runbook's output folder on the desk):

```
/usr/bin/python3 -I -B tools/claims-v3/e197/proposal/src/reduce_regfile.py <RB_OUT>/e197-reduce-1/sitting-1 --out <RB_OUT>/regfile-e197-s1.json
/usr/bin/python3 -I -B tools/claims-v3/e197/check_e197.py checks <RB_OUT>/regfile-e197-s1.json --out <RB_OUT>/checks-e197-1.json
```

  This is README.md's "Re-make it" form, run on copies of the committed records; the registered reducer never had `--prediction`.
- **The files' times.** `regfile-e197-s1.json` 06:26:14.493, the reducer's capture 06:26:14.536, `regfile-e197-s1.txt` 06:26:14.545,
  `checks-e197-1.json` and the checker's capture 06:26:14.580 PST: each at the end of its call as logged. Their sha256 are note 1's and
  this lane's re-run's, so nothing changed them after the step.
- **The printed lines.** `regfile-e197-s1.txt` is byte-equal to the runbook's capture of the reducer's call, and `checks-e197-1.txt` is
  the capture of the checker's call. Each of their 37 and 110 lines is in the card lane's log of step 13. The runbook's capture takes a
  program's stdout and stderr together, as they come.
- **On which commit.** The lab clone's reflog shows HEAD at `ae3c1ee0` from 06:25:28, then two commits by other lanes before the step:
  `d2f8ac3c` (06:26:01, E199's data directory only) and `9e59ca0d` (06:26:07, E198's tools only); the next, `50795847`, came at 06:26:25.
  So the step ran with HEAD at `9e59ca0d`, a descendant of `ae3c1ee0` whose trees for this directory and for `tools/claims-v3/e197/` are
  `ae3c1ee0`'s, object for object (desk check). The reducer read copies of `run/runs.jsonl` and `run/marks.jsonl`, and
  `run/telemetry.jsonl.gz` unpacked. The step checked each against the session's `session/MANIFEST.sha256` (the box's bytes) before the
  reducer ran ("each sitting's run/ files (the telemetry unpacked) equal the box's manifest's sha256"). This lane compared each copy with
  the data commit's blob: 3 of 3 equal, the telemetry after unpacking (desk check). The session wrote no `run/STOP`.
- **The programs.**
  - The registered reducer [`reduce_regfile.py`](../../../../tools/claims-v3/e197/proposal/src/reduce_regfile.py), sha256
    `f325bd0e3e916b81ee12304db7b47d79ad6daa5172ded19952f0ef1b0565eb87` (E197.md 7), with the train table it reads beside it,
    [`trains.tsv`](../../../../tools/claims-v3/e197/proposal/src/trains.tsv). It has the same bytes at `ea4b4ad7` (the registration),
    `2c68a633` (the kit), `ae3c1ee0`, `8aa6185e` and today's HEAD.
  - The kit's checker [`check_e197.py`](../../../../tools/claims-v3/e197/check_e197.py), sha256
    `b0b3012db6cd3f22b06374af16f1423f6968375881189d17e5b2c2947bbe5fdc`, pinned in
    [`SHA256SUMS-e197-kit`](../../../../tools/claims-v3/e197/SHA256SUMS-e197-kit); the same at `2c68a633`, `ae3c1ee0`, `8aa6185e` and
    HEAD. The step's script, `rb/s24_reduce_e197.sh` (`a38b57af...`), is pinned there too.
  - Both import the standard library only (`argparse`, `bisect`, `json`, `math`, `os`, `re`, `statistics`, `sys`); desk check of code.
    numpy 1.26.4 is on the box, but neither program imports it.

  No commit since the kit touches `tools/claims-v3/e197/`.
- **This lane's re-run** (desk check of code, 07:20:24-07:20:27 PST). Both programs ran in step 13's form on a fresh extract of
  `ae3c1ee0`: the data directory's `run/`, `session/MANIFEST.sha256` and `SHA256SUMS`, the reducer's folder `proposal/src/` and the
  checker, exported from the commit's own tree, with nothing read from the clone's working tree. They ran inside the round's CPU slot
  and its no-device sandbox, each with its stdout and stderr in one file, as the runbook takes them. The extract's nine record lines of
  `SHA256SUMS` read OK and its three run files read "the box's bytes". Both returned rc 0, and all four outputs are byte for byte step
  13's. fix-e197d's re-run of README.md's "Re-make it" lines from the clone's tree at `b4a5f6f2` gave the same four (REPORTED, note 1
  section 2).

## 3. The measured, reduced prices

Every figure in this section is **measured**: the registered reducer's output on the committed records, read from
[`regfile-e197-s1.json`](regfile-e197-s1.json), which holds them in full. Here the trains' D are rounded to 4 decimals, as the reducer
prints them, and the prices to 4 significant figures (its printed lines round them to 4 decimals). D is a train's estimate of board
power, its F kind less its S kind, in W: the mean over its units of the quads' s (L2 + L3 - L1 - L4) / 2, with the t(0.975, n - 1)
interval (E197.md 7). A price is energy per instruction: the train's D, or the registered combination of trains shown, over the
median device rate in instructions a second (the median of those trains' median rates), divided by the bits the trains hold apart
where it is a price per bit. The last two columns of each table are the data verifier's own re-derivation and the largest relative
difference between its numbers and the kit's on that row (section 5).

**3a. The trains (sitting 1).** 13 of 15 scored; every unit pairs an F and an S process; no process was dropped.

| train | F - S (registered kinds) | what it holds apart (trains.tsv, registered) | processes (of the plan) | units | D, F - S (W) | 95 % interval (W) | the reducer's word | F/S rate | verify-e197d: D [interval] | largest relative difference |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 | `rot.x64` - `rot2.x64` | cells: every write changes 64 stored bits (F) or none (S); same source, port and result stream, same field changes | 134 (of 364) | 67 | +0.0153 | [+0.0119, +0.0186] | POSITIVE | 1.00008 | +0.0153 [+0.0119, +0.0186] | < 1e-13 |
| T2 | `rot.x0` - `rot2.x0` | check for T1: the same two forms on an image where no write changes a cell (designed difference 0) | 18 (of 18) | 9 | -0.0033 | [-0.0170, +0.0103] | NOT RESOLVED | 1.00010 | -0.0033 [-0.0170, +0.0103] | < 1e-12 |
| T3 | `res.k64` - `res.k0` | the result path: 64 result bits change per instruction, sources fixed, destinations hold | 18 (of 18) | 9 | +1.9639 | [+1.9558, +1.9720] | POSITIVE | 1.00002 | +1.9639 [+1.9558, +1.9720] | < 1e-15 |
| T4 | `res.k32` - `res.k0` | the same at 32 bits (linearity of T3) | 18 (of 18) | 9 | +0.9957 | [+0.9805, +1.0109] | POSITIVE | 1.00002 | +0.9957 [+0.9805, +1.0109] | < 1e-14 |
| T5 | `resf.k0` - `resz.k0` | one register write (x5, value unchanged) against a write to x0 | 52 (of 52) | 26 | +0.0554 | [+0.0471, +0.0636] | POSITIVE | 0.99997 | +0.0554 [+0.0471, +0.0636] | < 1e-13 |
| T6 | `wn2.z` - `wn1.z` | two destinations in turn (one field bit apart) against one destination | 18 (of 18) | 9 | +0.0739 | [+0.0636, +0.0841] | POSITIVE | 1.00003 | +0.0739 [+0.0636, +0.0841] | < 1e-13 |
| T7 | `wn8.z` - `wn2.z` | eight destinations in turn against two, one field bit per step (bounded) | 0 (of 18) | 0 | - | - | NOT SCORED (not run) | - | NOT SCORED | - |
| T8 | `rd2i.d64` - `rd2i.e0` | bits 24:20 of an immediate instruction name two registers that differ in 64 bits (F) or hold zero (S) | 18 (of 18) | 9 | +0.1436 | [+0.1298, +0.1573] | POSITIVE | 0.99997 | +0.1436 [+0.1298, +0.1573] | < 1e-13 |
| T9 | `rd2i.e64` - `rd2i.e0` | the same two named registers both all ones (F) or both zero (S): no bit changes, ones held | 26 (of 26) | 13 | +0.1910 | [+0.1802, +0.2018] | POSITIVE | 1.00000 | +0.1910 [+0.1802, +0.2018] | < 1e-14 |
| T10 | `rd2r.d64` - `rd2r.e0` | the two registers read as the second operand, result held at zero by and with x0 | 18 (of 18) | 9 | +0.5022 | [+0.4923, +0.5121] | POSITIVE | 1.00000 | +0.5022 [+0.4923, +0.5121] | < 1e-14 |
| T11 | `rd1u.d64` - `rd1u.e0` | bits 19:15 of an upper-immediate instruction name the two registers | 18 (of 18) | 9 | +0.1862 | [+0.1684, +0.2040] | POSITIVE | 1.00000 | +0.1862 [+0.1684, +0.2040] | < 1e-13 |
| T12 | `idx5.z` - `idx1.z` | the second source field changes in 5 bits against 1 (zero contents) | 18 (of 18) | 9 | +0.2370 | [+0.2206, +0.2533] | POSITIVE | 0.99995 | +0.2370 [+0.2206, +0.2533] | < 1e-14 |
| T13 | `idx1.z` - `idx0.z` | the second source field changes in 1 bit against not at all (zero contents) | 26 (of 26) | 13 | +0.0965 | [+0.0858, +0.1072] | POSITIVE | 1.00008 | +0.0965 [+0.0858, +0.1072] | < 1e-13 |
| T14 | `rn8.z` - `idx1.z` | eight source registers in turn against two, one field bit per step (bounded) | 0 (of 18) | 0 | - | - | NOT SCORED (not run) | - | NOT SCORED | - |
| T15 | `idx3.z` - `idx1.z` | the second source field changes in 3 bits against 1 (zero contents): the field ladder 0, 1, 3, 5 | 18 (of 18) | 9 | +0.1140 | [+0.1010, +0.1270] | POSITIVE | 0.99997 | +0.1140 [+0.1010, +0.1270] | < 1e-13 |

**3b. The derived prices, in pJ of board energy per event.** POSITIVE: the whole 95 % interval is above zero. BOUNDED: the registered
reading for a price whose interval holds zero (E197.md 7: `order`, `lin_result` and `lin_field` here); its interval is the bound.

| price | from the trains (registered) | per | board pJ, mean | 95 % interval (pJ) | the reducer's word | verify-e197d: pJ [interval] | largest relative difference |
|---|---|---|---|---|---|---|---|
| `cell` | T1 / 64 | bit | +0.0004548 | [+0.0003539, +0.0005556] | POSITIVE | +0.0004548 [+0.0003539, +0.0005556] | < 1e-13 |
| `cell_ctrl` | (T1 - T2) / 64 | bit | +0.0005546 | [+0.0001418, +0.0009674] | POSITIVE | +0.0005546 [+0.0001418, +0.0009674] | < 1e-12 |
| `order` | T2 | instr | -0.006389 | [-0.032430, +0.019651] | BOUNDED | -0.006389 [-0.032430, +0.019651] | < 1e-12 |
| `result_bit` | T3 / 64 | bit | +0.05855 | [+0.05831, +0.05879] | POSITIVE | +0.05855 [+0.05831, +0.05879] | < 1e-15 |
| `result_bit32` | T4 / 32 | bit | +0.05937 | [+0.05847, +0.06028] | POSITIVE | +0.05937 [+0.05847, +0.06028] | < 1e-14 |
| `lin_result` | T4 - T3 / 2 | instr | +0.02624 | [-0.00321, +0.05568] | BOUNDED | +0.02624 [-0.00321, +0.05568] | < 1e-12 |
| `write` | T5 | instr | +0.1057 | [+0.0899, +0.1214] | POSITIVE | +0.1057 [+0.0899, +0.1214] | < 1e-13 |
| `dest_switch` | T6 | instr | +0.1410 | [+0.1215, +0.1605] | POSITIVE | +0.1410 [+0.1215, +0.1605] | < 1e-13 |
| `dest_n8` | T7 | instr | - | - | NOT SCORED (T7 did not run) | NOT SCORED | - |
| `read2_field` | T8 / 64 | bit | +0.004281 | [+0.003871, +0.004691] | POSITIVE | +0.004281 [+0.003871, +0.004691] | < 1e-13 |
| `read2_net` | (T8 - T9 / 2) / 64 | bit | +0.001434 | [+0.001009, +0.001859] | POSITIVE | +0.001434 [+0.001009, +0.001859] | < 1e-13 |
| `held_one` | T9 / 128 | bit | +0.002847 | [+0.002686, +0.003008] | POSITIVE | +0.002847 [+0.002686, +0.003008] | < 1e-14 |
| `read2_operand` | T10 / 64 | bit | +0.01497 | [+0.01468, +0.01527] | POSITIVE | +0.01497 [+0.01468, +0.01527] | < 1e-14 |
| `operand_path` | (T10 - T8) / 64 | bit | +0.01069 | [+0.01022, +0.01116] | POSITIVE | +0.01069 [+0.01022, +0.01116] | < 1e-14 |
| `read1_field` | T11 / 64 | bit | +0.005552 | [+0.005022, +0.006083] | POSITIVE | +0.005552 [+0.005022, +0.006083] | < 1e-13 |
| `field_bit` | T12 / 4 | bit | +0.1130 | [+0.1052, +0.1208] | POSITIVE | +0.1130 [+0.1052, +0.1208] | < 1e-14 |
| `field_bit3` | T15 / 2 | bit | +0.1088 | [+0.0964, +0.1212] | POSITIVE | +0.1088 [+0.0964, +0.1212] | < 1e-13 |
| `lin_field` | T15 - T12 / 2 | instr | -0.008510 | [-0.035888, +0.018869] | BOUNDED | -0.008510 [-0.035888, +0.018869] | < 1e-12 |
| `field_first` | T13 | instr | +0.1841 | [+0.1637, +0.2045] | POSITIVE | +0.1841 [+0.1637, +0.2045] | < 1e-13 |
| `field_base` | T13 - T12 / 4 | instr | +0.07106 | [+0.04986, +0.09226] | POSITIVE | +0.07106 [+0.04986, +0.09226] | < 1e-13 |
| `read_n8` | T14 | instr | - | - | NOT SCORED (T14 did not run) | NOT SCORED | - |

**3c. The same prices in the other units the reducer writes** (each from the board mean): gain-corrected (divided by the train gain,
3d), electrons through the 12 V input (pJ / (e x 12 V)), the core-rail share of it (x the rail share, 3d) and electrons through the core
rail (/ (e x V_rail)). verify-e197d's values of these four are in section 5's count.

| price | gain-corrected board pJ, mean [interval] | electrons through the 12 V input | core-rail pJ | electrons through the core rail |
|---|---|---|---|---|
| `cell` | +0.0004601 [+0.0003581, +0.0005621] | 237 | +0.0004032 | 4,812 |
| `cell_ctrl` | +0.0005611 [+0.0001435, +0.0009786] | 288 | +0.0004918 | 5,869 |
| `order` | -0.006464 [-0.032807, +0.019879] | -3,323 | -0.005665 | -67,610 |
| `result_bit` | +0.05924 [+0.05899, +0.05948] | 30,456 | +0.05192 | 619,603 |
| `result_bit32` | +0.06006 [+0.05915, +0.06098] | 30,882 | +0.05265 | 628,274 |
| `lin_result` | +0.02654 [-0.00324, +0.05633] | 13,647 | +0.02326 | 277,637 |
| `write` | +0.1069 [+0.0909, +0.1228] | 54,957 | +0.0937 | 1,118,063 |
| `dest_switch` | +0.1426 [+0.1229, +0.1624] | 73,332 | +0.1250 | 1,491,902 |
| `dest_n8` | - | - | - | - |
| `read2_field` | +0.004331 [+0.003916, +0.004745] | 2,227 | +0.003796 | 45,300 |
| `read2_net` | +0.001451 [+0.001021, +0.001880] | 746 | +0.001272 | 15,176 |
| `held_one` | +0.002880 [+0.002717, +0.003043] | 1,481 | +0.002524 | 30,124 |
| `read2_operand` | +0.01515 [+0.01485, +0.01545] | 7,788 | +0.01328 | 158,445 |
| `operand_path` | +0.01082 [+0.01034, +0.01129] | 5,562 | +0.00948 | 113,150 |
| `read1_field` | +0.005617 [+0.005080, +0.006154] | 2,888 | +0.004923 | 58,755 |
| `field_bit` | +0.1144 [+0.1065, +0.1222] | 58,796 | +0.1002 | 1,196,171 |
| `field_bit3` | +0.1100 [+0.0975, +0.1226] | 56,581 | +0.0965 | 1,151,118 |
| `lin_field` | -0.008609 [-0.036305, +0.019088] | -4,426 | -0.007545 | -90,047 |
| `field_first` | +0.1862 [+0.1656, +0.2069] | 95,755 | +0.1632 | 1,948,097 |
| `field_base` | +0.07189 [+0.05044, +0.09333] | 36,960 | +0.06301 | 751,924 |
| `read_n8` | - | - | - | - |

**3d. Beside the prices.**

- **The cell reading:** "cell" ("order (T2) reads BOUNDED"). E197.md 7's reading rule: `cell` (T1 / 64)
  is the stored-bit price when `order` (T2) reads BOUNDED; when T2 reads POSITIVE or NEGATIVE, `cell_ctrl` is read first.
- **The train gain:** 0.9885 (T3's D over the median of the anchors' eight `res.k64` - `res.k0` burst differences,
  1.9867 W; flagged outside 0.95-1.05: no). The eight differences (W):
  2.0386, 1.8700, 2.1934, 2.0554, 1.9068, 1.9485, 1.9138, 2.0250.
- **The rail share:** 0.8867, the median of eight (0.8681, 0.9669, 0.8534, 0.8929, 0.9030, 0.8805, 0.9104, 0.8358);
  **V_rail** 0.523 V.
- **The telemetry:** 25,930 samples, all at 600 MHz; 309 board samples set aside by the two dip rules (E197.md 7);
  the participants gate 1,024; stops seen by the reducer: none (`[{"session": "sitting-1", "t_ms": null, "from": null}]`).
- **The anchors:** 24 bursts, first and last of each block, each of 8 launches; the largest drift between a block's first and last
  burst of one kind is 0.1501 W, against the registered 0.3 W, and none is flagged.

| block | kind | first, board over idle (W) | last (W) | last - first (W) | flagged |
|---|---|---|---|---|---|
| A | `nop.z` | 1.4568 | 1.4657 | +0.0089 | no |
| A | `res.k0` | 1.7725 | 1.7910 | +0.0186 | no |
| A | `res.k64` | 3.8111 | 3.6610 | -0.1501 | no |
| B | `nop.z` | 1.4831 | 1.4808 | -0.0023 | no |
| B | `res.k0` | 1.6460 | 1.7769 | +0.1309 | no |
| B | `res.k64` | 3.8394 | 3.8323 | -0.0071 | no |
| C | `nop.z` | 1.4740 | 1.4786 | +0.0046 | no |
| C | `res.k0` | 1.7841 | 1.8782 | +0.0941 | no |
| C | `res.k64` | 3.6909 | 3.8267 | +0.1357 | no |
| D | `nop.z` | 1.5180 | 1.3755 | -0.1425 | no |
| D | `res.k0` | 1.8761 | 1.8009 | -0.0751 | no |
| D | `res.k64` | 3.7899 | 3.8259 | +0.0361 | no |

## 4. The checks, as the checker printed them (measured)

The checker's last line, as printed: **"CHECKS READ: 109 rows (APPLIED 16, NOT SCORED 2, PASS 13, REPORTED 78)"**. Its rows are E197.md 8's, in [`checks-e197-1.json`](checks-e197-1.json) in
full and in [`checks-e197-1.txt`](checks-e197-1.txt) as printed (each row's name cut to width there). Per train: one gates row
(APPLIED), one gate row (PASS, or NOT SCORED for the two trains that did not run) and five REPORTED rows; then four closing rows. The
table gives each train's rows as the checker wrote them in its JSON (the retired-per-body rows' flag is the checker's "outside 0.5 % of
131/128 plus the entry and exit").

| train | gates (APPLIED): processes of the plan, units, dropped | gate: rates within 0.05 %, 8 units | F/S rate | retired / body, F and S (flagged?) | instruction-cache misses per iteration, F and S | L1 data misses, median per launch, F and S | launches with a slow hart, F and S | rail-voltage samples off, of all in the spans |
|---|---|---|---|---|---|---|---|---|
| T1 | 134 of 364, 67, none | PASS | 1.00008 | 1.023438 (no); 1.023438 (no) | 2.501e-06; 2.424e-06 | 19,349; 19,348 | 245; 375 | 0 of 6,999 |
| T2 | 18 of 18, 9, none | PASS | 1.00010 | 1.023438 (no); 1.023438 (no) | 2.501e-06; 2.424e-06 | 19,349; 19,347 | 29; 56 | 0 of 942 |
| T3 | 18 of 18, 9, none | PASS | 1.00002 | 1.023438 (no); 1.023438 (no) | 2.345e-06; 2.345e-06 | 12,288; 12,288 | 59; 50 | 0 of 944 |
| T4 | 18 of 18, 9, none | PASS | 1.00002 | 1.023438 (no); 1.023438 (no) | 2.345e-06; 2.345e-06 | 12,288; 12,288 | 54; 56 | 0 of 937 |
| T5 | 52 of 52, 26, none | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 2.268e-06; 2.268e-06 | 12,296; 10,254 | 144; 123 | 0 of 2,706 |
| T6 | 18 of 18, 9, none | PASS | 1.00003 | 1.023438 (no); 1.023438 (no) | 2.268e-06; 2.269e-06 | 10,252; 10,256 | 44; 63 | 0 of 936 |
| T7 | 0 of 18, 0, none | NOT SCORED | - | -; - | -; - | -; - | 0; 0 | 0 of 0 |
| T8 | 18 of 18, 9, none | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 2.269e-06; 2.269e-06 | 16,154; 16,134 | 52; 58 | 0 of 942 |
| T9 | 26 of 26, 13, none | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 2.270e-06; 2.270e-06 | 16,159; 16,133 | 82; 81 | 0 of 1,358 |
| T10 | 18 of 18, 9, none | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 2.268e-06; 2.268e-06 | 16,163; 16,142 | 41; 41 | 0 of 938 |
| T11 | 18 of 18, 9, none | PASS | 1.00000 | 1.023438 (no); 1.023438 (no) | 2.268e-06; 2.268e-06 | 16,155; 16,128 | 61; 55 | 0 of 938 |
| T12 | 18 of 18, 9, none | PASS | 0.99995 | 1.023438 (no); 1.023438 (no) | 2.269e-06; 2.268e-06 | 15,352; 14,120 | 41; 42 | 0 of 940 |
| T13 | 26 of 26, 13, none | PASS | 1.00008 | 1.023438 (no); 1.023438 (no) | 2.268e-06; 2.269e-06 | 14,139; 14,100 | 67; 83 | 0 of 1,358 |
| T14 | 0 of 18, 0, none | NOT SCORED | - | -; - | -; - | -; - | 0; 0 | 0 of 0 |
| T15 | 18 of 18, 9, none | PASS | 0.99997 | 1.023438 (no); 1.023438 (no) | 2.269e-06; 2.268e-06 | 16,167; 14,124 | 46; 37 | 0 of 943 |

| row (E197.md 8, as the checker names it) | kind | word | what it printed |
|---|---|---|---|
| the anchors' first and last bursts of a block within 0.3 W | report | REPORTED | `{"flagged": [], "pairs": 12}` |
| the train gain (T3 over the anchors' burst difference) within 0.95-1.05 (outside: the gain-corrected prices first) | report | REPORTED | `{"train_gain": 0.9885050583735298}` |
| the cell reading (order, T2, BOUNDED: cell; else cell_ctrl first) | reading rule | REPORTED | `{"read": "cell", "why": "order (T2) reads BOUNDED"}` |
| the stops seen by the reducer (a process ending after a STOP gives no value) | gate | APPLIED | `{"stops": [{"session": "sitting-1", "t_ms": null, "from": null}]}` |

## 5. Beside verify-e197d's independent re-derivation

verify-e197d wrote its own reducer from E197.md, importing nothing from the kit, and ran it on the committed raw files.

- **Its numbers (REPORTED).** All 13 scored trains, 21 prices and 24 anchors match step 13's outputs, the largest relative difference
  6.9e-13; all 109 checker rows are equal (APPLIED 16, NOT SCORED 2, PASS 13, REPORTED 78); 0 disagreements. Its re-make of README.md's
  lines gave step 13's bytes.
- **This lane's comparison of the two files** (desk check, value by value, standard library, by a fixed map from the kit's field names
  to the verifier's): 541 numeric values compared, 353 exactly equal, the largest relative difference 6.9e-13 (on
  `lin_result pJ lo`). By part:
  - the trains: 121 compared, 88 exactly equal, largest relative difference < 1e-12;
  - the derived prices: 266 compared, 112 exactly equal, largest relative difference < 1e-12;
  - the anchors and their drifts: 132 compared, 132 exactly equal, largest relative difference 0;
  - the rail shares, burst differences, rail share, train gain, V_rail, samples, dips and clock: 22 compared, 21 exactly equal, largest relative difference < 1e-15.

  82 words (signs, verdicts, flags, dropped lists) compared: 82 equal. The kit's file holds more than the verifier's
  (the per-kind counts, the roles, the bounds in fJ); those are read in section 4 and not counted here.
- **In section 3** every train and price agrees with the verifier's at the figures shown, and to better than 1e-12 relative in full.

## 6. The verifier's findings, answered (dated clauses, Mon 16 Nov 2026)

| verify-e197d | what | answered |
|---|---|---|
| F1 (minor) | sitting 2's step 0 (`go_anchors_e197.sh`) has no sitting-2 form, so after sitting 1's own data commit it can only read NOT AS STATED; sitting 2 could not run | Note 1 section 1 (`8aa6185e`) records it as a fail-safe stop and E197.md 11's reading. *Mon 16 Nov 2026:* until a sitting 2 runs, sitting 1's reduction, committed here, is E197's result. If a sitting 2 runs, its step 13 pools both sittings into `regfile-e197.json` (`rb/s24_reduce_e197.sh 2`), and the four files here stay as committed beside it. A sitting-2 form of the anchors is drafted but not committed or verified (fix-e197d, REPORTED). |
| F2 (nit) | README.md says a later dated note "fills this section"; the lab's practice adds the note and the outputs beside the README | Note 1 section 2 names this file. *Mon 16 Nov 2026:* done here: the four outputs and this note are new files beside README.md, which is not edited; sections 1-4 are what its "Reduced (not here)" points to. |
| finding 3 (nit) | the data commit's scans read the subject and body before the commit helper appended the round's two trailer lines | Note 1 section 3. *Mon 16 Nov 2026:* this commit's message was scanned in full, trailer included, before the commit (section 7), and the pushed message is read back after the push. |
| finding 4 (nit) | "nothing set" rests on the command audit and the telemetry; no closing configuration read | Note 1 section 3: E197 registers no closing read; no gap against E197.md. *Mon 16 Nov 2026:* nothing here bears on it: the reduction reads the committed records only. |
| finding 5 (nit) | the box's build record compares the kernel's `.text`, not its 72 B `.rodata` | Note 1 section 3: reported, never a gate. *Mon 16 Nov 2026:* nothing here bears on it: the reduction does not read the kernel. |

This note also closes the card lane's open item: "The step 13 outputs are not committed ... A later lane commits them in a dated note."

## 7. Checks before the commit

- **The sums.** `SHA256SUMS-note2` reads back, 5 of 5. In the lab clone, README.md's `SHA256SUMS` (23 of 23) and `SHA256SUMS-note1`
  (3 of 3) still read back, and nothing in this directory changed since note 1's commit.
- **New files only.** None of the six names was in this directory before this commit.
- **The desk-path gate** (`nopath_q142s.py`, v3.1) over the six files: clean.
- **The login and public-text scans** read the six files and this commit's message: the round's login check, the lab's sanitizer list
  ([`tools/timeline/sanitize_extracts.py`](../../../../tools/timeline/sanitize_extracts.py)) with this box's privacy table, the round's
  word classes, and the two scanners README.md's scan used. They found nothing in the six files. In the message, the only matches are
  the round's two standard trailer lines: the co-author line's address and the session line's link.
- **The seal.** The numbers of the request's withheld lines (redaction R1, E197.md section 0), read on this desk from the received file
  (checked first by its sha256 and the withheld block's, both as E197.md registers them), searched as whole numbers in the six files and
  the message: no withheld number counts. The rule's other matches, each counted with its line in this lane's log, are all of its first
  accepted kind: numbers the received request also states outside its withheld lines (public in the committed copy since the
  registration). Its other two accepted kinds (the digits of a train's or an experiment's name, digits inside a hash) did not occur.
  Nothing of the withheld lines is quoted here, and neither program reads them (the reducer runs without `--prediction`).

## What does not change

README.md, `SHA256SUMS` and note 1's two files stay as committed, and no committed file changes. No number, price, rule, verdict, check or
gate reading changes; nothing is scored, and no forecast number is here.

SPDX-License-Identifier: Apache-2.0
