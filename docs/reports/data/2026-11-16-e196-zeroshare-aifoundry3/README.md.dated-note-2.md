# E196's data README, dated note 2 (Mon 16 Nov 2026): the registered reducer's and the kit checker's outputs, run on the data commit `4bc7a07a` at 05:19:08-09 PST, committed beside it with their printed lines (one desk folder withheld); the measured, reduced prices; the data verifier's re-derivation agrees

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `4bc7a07a` (05:13:21 PST Mon 16 Nov 2026),
and note 1's two files ([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and [`SHA256SUMS-note1`](SHA256SUMS-note1), `985554c6`,
06:26:27 PST), which stay as committed too. Written on aifoundry2 from 06:28 PST on Mon 16 Nov 2026 (week 47) by the clock, desk only (no
card, no lab box, no device, no post), by Q191's lane `reduce-e196`, after the card lane `card-e196` (the data commit), the data verifier
`verify-e196d` (holds with fixes: one low finding and three nits, none of them a fault in a datum, a check or a verdict) and note 1
(`fix-e196d`). The kit's step 13 ([`rb/s24_reduce_e196.sh`](../../../../tools/claims-v3/e196/rb/s24_reduce_e196.sh)) runs only after
the data commit and leaves its outputs to a later commit: "Outputs: RB_OUT/x14-e196.json (the reduction's) and its printed lines,
RB_OUT/checks-e196.json (the checker's) and its lines, with the interpreter named; the records lane commits them beside the data."
README.md's "Next" says the same ("its outputs in a dated note by a later lane"). This lane is that later lane. This note commits the
four outputs, states when and on which commit step 13 ran, gives the measured, reduced prices and the checks' words as printed, sets
the data verifier's re-derivation beside them, and answers each finding the verifier named with a dated clause. **No number, price,
rule, verdict, check or gate reading changes, and nothing is scored. The forecast stays sealed (the lab knows it only by its sha256,
E196.md section 0): no forecast number is here, and nothing here scores E196 against it; the model session scores it privately against
these published prices.** Interpreter: `/usr/bin/python3` 3.12.3 (`-I -B`) on aifoundry2, standard library only, for step 13 and for
this lane's re-run. Labels: **registered** ([`E196.md`](../../../../tools/claims-v3/e196/E196.md) and the kit as committed),
**measured** (the session's committed records, and the registered reducer's and the kit checker's outputs from them), **desk check of
code** (this lane's re-run and comparisons), **post hoc** (desk arithmetic after the data, deciding nothing), **REPORTED**
(verify-e196d's and fix-e196d's figures, not re-run here).*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`x14-e196.json`](x14-e196.json) | the registered reducer's output (its `--json`), byte for byte | 130,194 | `3a020dc8b43fd1402c825cc8fc63f0069bfe9dabaa5c262ec6a5237b6dae3bad` |
| [`x14-e196.txt`](x14-e196.txt) | the reducer's printed lines, the runbook's capture of that call, with one marked redaction in line 1 (below) | 5,753 | `eed77848a11938d18abf538227b215daf9c949a9dad1d109d919f735d759ed3d` |
| [`checks-e196.json`](checks-e196.json) | the kit checker's output (`check_e196.py ... --out`), byte for byte | 5,445 | `1c1db76b7090efa801f3931ebf8558d69cccbfbb20eb228c622193e7f215f0d8` |
| [`checks-e196.txt`](checks-e196.txt) | the checker's printed lines, the runbook's capture of that call, byte for byte | 845 | `222342b55930f4979f9eb2b84ec5507a0fafbdd8f240815372fa908f0d58498f` |
| `README.md.dated-note-2.md` | this note | | in `SHA256SUMS-note2` |
| [`SHA256SUMS-note2`](SHA256SUMS-note2) | the sha256 of the five files above | | |

Three of the four outputs are byte for byte the files step 13 wrote; their sha256 are the ones note 1 section 5 published before this
commit. Nothing else in this directory changes.

**The one redaction (`x14-e196.txt`, line 1).** The reducer's first printed line ends with the path it wrote its JSON to. On the desk
that is an absolute folder of 78 characters: this box's home folder, then the round's private working folders. A public file
carries no desk path, so the committed copy replaces that folder, and only it, by the marker
`[withheld: the desk folder, see README.md.dated-note-2.md]`; the line now ends
`-> [withheld: the desk folder, see README.md.dated-note-2.md]/x14-e196.json`.
Lines 2-57 are the capture's bytes: their sha256 is
`b947711b4ca69f683009d8c55dd33c0928e91d7c3044631752a65a03c2fb5348` in both files. The capture as step 13 wrote it, 5,773 bytes, has sha256
`39e6571460cbebaaca5ab4b3712b4348ff62bcf03bf8a39a90d6f3f37b9191d8` (note 1 section 5): put the folder back in place of the marker and
that sha256 returns. The folder carries no measured value; every number of the line is
kept ("passes kept [0, 1, 2, 3, 4, 5, 6]; runs 213 kept, 1 set aside; 68 dips dropped").

## 2. When, where and on which commit the reducer and the checker ran

- **The step.** Step 13 of card-e196's runbook, `rb/s24_reduce_e196.sh` on this directory, run on aifoundry2 inside the round's CPU slot:
  the card lane's record gives 05:13:38 to 05:19:09 PST on Mon 16 Nov 2026, rc 0, and its seven calls all end at 05:19:08-09, 5 min
  47 s after the data commit (`4bc7a07a`, committed at 05:13:21 and pushed by 05:13:25).
- **The runbook's log: its seven lines for the step**, kept with the round's records. Each time is the end of its call; the command
  fields are left out here and the two programs' calls are given below.

```
05:19:08 read  the data directory tracked at HEAD                                       rc 0
05:19:08 read  the data directory clean                                                 rc 0
05:19:08 read  the data directory's SHA256SUMS, every entry                             rc 0
05:19:08 read  the reduction at its registered sha256                                   rc 0
05:19:08 read  the session's arms.json is the registered one (proposal/src/arms.json), byte for byte   rc 0
05:19:09 desk  the registered reduction, unchanged (/usr/bin/python3 -I -B): reduce_e196.py OUT --readback-none-ok --json x14-e196.json   0.6 s   rc 0
05:19:09 desk  the section 8 checker (check_e196.py)                                    0.6 s   rc 0
```

  The script stops before the reducer unless the data directory is tracked at HEAD and clean, its `SHA256SUMS` holds, the reducer is at
  `c58c6690...` and the session's `run/gen/arms.json` is the registered table.
- **The two calls, as logged** (`<RB_OUT>` stands for the runbook's output folder on the desk):

```
/usr/bin/python3 -I -B tools/claims-v3/e196/reduce_e196.py <RB_OUT>/reduce-e196/run --readback-none-ok --json <RB_OUT>/x14-e196.json
/usr/bin/python3 -I -B tools/claims-v3/e196/check_e196.py <RB_OUT>/reduce-e196/run <RB_OUT>/x14-e196.json --out <RB_OUT>/checks-e196.json
```

  This is README.md section 5's form, run on copies of the committed records.
- **The files' times.** `x14-e196.json` 05:19:09.192, `x14-e196.txt` 05:19:09.244, `checks-e196.json` 05:19:09.797 and
  `checks-e196.txt` 05:19:09.848 PST: each at the end of its call as logged. Their sha256 are note 1's and this lane's re-run's (with
  the swap below), so nothing changed them after the step.
- **The printed lines.** The step copies the runbook's capture of each program's call to its `.txt` (`rb/s24_reduce_e196.sh`:
  `cp "$RB_CAP" "$RB_OUT/x14-e196.txt"`, and the same for `checks-e196.txt`). The two `.txt` files are byte-equal to the runbook's own
  captures of those two calls (written 05:19:09.235 and 05:19:09.838), and each of their 57 and 7 lines is in the card lane's log of
  step 13 (line 1 there with the home folder masked).
- **On which commit.** The lab clone's reflog shows HEAD at `4bc7a07a` from 05:13:21 until the next commit at 06:25:28 (E197's data,
  `ae3c1ee0`), so the step read the data commit itself. The reducer read copies of `run/runs.jsonl`, `run/train.jsonl`,
  `run/checks.jsonl`, `run/marks.jsonl` and `run/gen/arms.json`, and `run/telemetry.jsonl.gz` unpacked. The step checked each record
  against the session's `session/MANIFEST.sha256` (the box's bytes) before the reducer ran, and this lane compared each copy with the
  data commit's blob: 6 of 6 equal, the telemetry after unpacking (desk check). The session wrote no `run/STOP`.
- **The programs.**
  - The registered reducer [`reduce_e196.py`](../../../../tools/claims-v3/e196/reduce_e196.py), sha256
    `c58c6690016f18e5dac62ba620086f3cefda812cab9e93d2a929cb1aa207f3f7` (E196.md section 7). It has the same bytes at `2cf02aae` (the
    registration), `99bc9a38` (the kit), `4bc7a07a`, `985554c6` and today's HEAD.
  - The kit's checker [`check_e196.py`](../../../../tools/claims-v3/e196/check_e196.py), sha256
    `e1038e4449214bd8137b71c585bb13f4e5d4420680b7b9a0a3809d0853c15477`, pinned in
    [`SHA256SUMS-e196-kit`](../../../../tools/claims-v3/e196/SHA256SUMS-e196-kit); the same at `99bc9a38`, `4bc7a07a`, `985554c6` and
    HEAD. The step's script, `rb/s24_reduce_e196.sh` (`3bac19c6...`), is pinned there too.
  - Both import the standard library only (`argparse`, `bisect`, `json`, `math`, `os`, `statistics`), as E196.md 7 registers ("standard
    library only"); desk check of code.

  No commit since the kit touches `tools/claims-v3/e196/`.
- **This lane's re-run** (desk check of code, 06:34:45-06:34:46 PST). Both programs ran in README.md section 5's form on a fresh extract
  of `4bc7a07a`: the data directory's `run/` and `session/MANIFEST.sha256`, the two programs and the registered `arms.json`, exported
  from the commit's own tree, with nothing read from the clone's working tree. They ran inside the round's CPU slot and its no-device
  sandbox. Both returned rc 0 with nothing on stderr. `x14-e196.json`, `checks-e196.json` and `checks-e196.txt` are byte for byte step
  13's; the re-run's `x14-e196.txt` is byte for byte step 13's once line 1's folder (where each run writes its JSON) is swapped.
  fix-e196d's re-run from the clone's tree at `4bc7a07a` gave the same (REPORTED, note 1 section 5).

## 3. The measured, reduced prices

Every figure in this section is **measured**: the registered reducer's output on the committed records, read from
[`x14-e196.json`](x14-e196.json) and rounded here to 4 significant figures (the file holds them in full). The last column of each table
of derived prices is the data verifier's own re-derivation, set beside the kit's (section 5): "equal" means its mean, standard error
and 95 % interval are the kit's exactly, in full.

**3.1 The reduction's registered inputs (not measured).** E196.md 7 runs the reducer "its defaults otherwise", and
`reduce_e196.py` (lines 79 and 133-138) fixes them:

- the leakage slope **0.1994 W/°C** (E78's fitted slope; `--leak`, written to the output as `leak_W_per_C`), with every result also at
  the sensitivity slopes **0** and **0.3803 W/°C** (`LEAK_ARMS`, the output's `sensitivity` block, section 3.6). The slope is an input:
  it is not among the measured prices below (note 1 section 1);
- the rail filter's time constant 1.05 s and its delay 0.26 s; `--min-passes 5`; no `--drop-pass0`;
- `--readback-none-ok`, given: the output's `readback_gate` lists the 214 runs of the unchanged host (the 210 pass runs and the trains'
  4 anchors), which carry no read-back of C and are not set aside for it (E196.md 7).

**3.2 What the reduction kept.** All 7 passes (0-6): each pass's two `K.pi` anchors agree within the registered 0.3 W.

| pass | kept | the two `K.pi` anchors' drift (W) |
|---|---|---|
| 0 | yes | +0.171 |
| 1 | yes | -0.122 |
| 2 | yes | -0.078 |
| 3 | yes | -0.151 |
| 4 | yes | -0.196 |
| 5 | yes | +0.260 |
| 6 | yes | -0.227 |

213 runs kept (the 209 kept pass runs and the trains' 4 anchors) and 1 set aside: pass 5 seq 22, `I.Z.m0FFF`, "approach off
protocol" (it closed at 59 °C; note 1 section 2). 68 dips dropped by E82's A2 rule; 28,783 telemetry samples, none off 600 MHz.

**3.3 Per arm** (W over idle; D over the arm's registered reference in the primary form, the leak-corrected busy means; mean over the
kept passes, standard error over passes; the file adds the bracketed D, the rail, the electrons per op and the 95 % intervals):

| arm | S over idle (W) | se | its reference (`arms.json`) | D over it, the primary form (W) | se | D per op, board (pJ) | n passes |
|---|---|---|---|---|---|---|---|
| `I.Z.m0000` | 0.3222 | 0.041 | - | - | - | - | 7 |
| `I.Z.m000F` | 0.9184 | 0.023 | `I.Z.m0000` | 0.5571 | 0.028 | 529.9 | 7 |
| `I.Z.m00FF` | 1.306 | 0.054 | `I.Z.m0000` | 0.9890 | 0.025 | 874.1 | 7 |
| `I.Z.m0FFF` | 1.699 | 0.020 | `I.Z.m0000` | 1.334 | 0.016 | 1225 | 6 |
| `I.Z.full` | 1.914 | 0.016 | `I.Z.m0000` | 1.518 | 0.032 | 1422 | 7 |
| `I.H.m0000` | 0.4910 | 0.014 | `I.Z.m0000` | 0.06177 | 0.022 | 150.0 | 7 |
| `I.H.m000F` | 3.250 | 0.033 | `I.H.m0000` | 2.766 | 0.052 | 2453 | 7 |
| `I.H.m00FF` | 5.644 | 0.036 | `I.H.m0000` | 5.205 | 0.025 | 4581 | 7 |
| `I.H.m0FFF` | 8.038 | 0.031 | `I.H.m0000` | 7.617 | 0.030 | 6710 | 7 |
| `I.H.full` | 10.26 | 0.025 | `I.H.m0000` | 9.823 | 0.026 | 8718 | 7 |
| `I.H.mFFFF` | 10.24 | 0.026 | `I.H.full` | -0.03072 | 0.038 | -18.97 | 7 |
| `I.H.m5555` | 6.857 | 0.028 | `I.H.m00FF` | 1.225 | 0.029 | 1078 | 7 |
| `I.H.m3333` | 6.211 | 0.018 | `I.H.m00FF` | 0.6087 | 0.034 | 503.0 | 7 |
| `I.H.m0F0F` | 5.934 | 0.041 | `I.H.m00FF` | 0.2844 | 0.023 | 257.4 | 7 |
| `I.R.m0000` | 0.7481 | 0.038 | `I.Z.m0000` | 0.3951 | 0.022 | 378.7 | 7 |
| `I.R.m00FF` | 13.67 | 0.031 | `I.R.m0000` | 12.88 | 0.022 | 1.149 x 10^4 | 7 |
| `I.R.full` | 26.58 | 0.037 | `I.R.m0000` | 25.82 | 0.026 | 2.304 x 10^4 | 7 |
| `F.B0` | 10.39 | 0.025 | `I.Z.full` | 8.523 | 0.040 | 7563 | 7 |
| `F.Bs` | 10.99 | 0.047 | `F.B0` | 0.5851 | 0.039 | 528.7 | 7 |
| `F.Be` | 12.11 | 0.021 | `F.B0` | 1.709 | 0.016 | 1538 | 7 |
| `F.A0` | 10.39 | 0.050 | `I.Z.full` | 8.476 | 0.037 | 7563 | 7 |
| `F.Ae` | 11.35 | 0.035 | `F.A0` | 0.9907 | 0.026 | 851.8 | 7 |
| `Z.a50` | 15.17 | 0.031 | `I.R.full` | -11.45 | 0.015 | -1.017 x 10^4 | 7 |
| `Z.b50` | 15.97 | 0.039 | `I.R.full` | -10.66 | 0.026 | -9460 | 7 |
| `Z.ab50` | 9.142 | 0.038 | `I.R.full` | -17.42 | 0.022 | -1.555 x 10^4 | 7 |
| `Z.a0` | 2.723 | 0.044 | `I.Z.full` | 0.8252 | 0.027 | 721.2 | 7 |
| `Z.a0.m0000` | 0.6751 | 0.044 | `I.Z.m0000` | 0.2781 | 0.037 | 313.6 | 7 |
| `K.ones` | 10.27 | 0.027 | `I.Z.full` | 8.375 | 0.048 | 7458 | 7 |
| `K.pi` | 10.40 | 0.034 | - | - | - | - | 7 |

**3.4 The derived prices** (the reducer's own names, as it prints them in [`x14-e196.txt`](x14-e196.txt); each name carries its
unit, and a value is the board's unless its name says rail). The three ladder tables of S (`ladder_H_S_W`, `ladder_Z_S_W` and `ladder_R_S_W`, of
5, 5 and 3 rungs) repeat the arms' S in section 3.3 and are not listed again (desk check: equal).

**The ladders: each step (W) and the slopes**

| price (the reducer's name) | mean | se | 95 % interval | n | verify-e196d |
|---|---|---|---|---|---|
| `ladder_H_step_I.H.m0000_to_I.H.m000F_W` | 2.766 | 0.0524 | [2.638, 2.894] | 7 | equal |
| `ladder_H_step_I.H.m000F_to_I.H.m00FF_W` | 2.439 | 0.0450 | [2.329, 2.549] | 7 | equal |
| `ladder_H_step_I.H.m00FF_to_I.H.m0FFF_W` | 2.412 | 0.0229 | [2.356, 2.468] | 7 | equal |
| `ladder_H_step_I.H.m0FFF_to_I.H.full_W` | 2.206 | 0.0208 | [2.155, 2.257] | 7 | equal |
| `ladder_H_slope_pJ_per_issued_uop` | 16.63 | 0.198 | [16.15, 17.12] | 7 | equal |
| `ladder_H_slope_W_per_row` | 0.6064 | 0.00629 | [0.5910, 0.6218] | 7 | equal |
| `ladder_Z_step_I.Z.m0000_to_I.Z.m000F_W` | 0.5571 | 0.0281 | [0.4882, 0.6259] | 7 | equal |
| `ladder_Z_step_I.Z.m000F_to_I.Z.m00FF_W` | 0.4319 | 0.0422 | [0.3287, 0.5352] | 7 | equal |
| `ladder_Z_step_I.Z.m00FF_to_I.Z.m0FFF_W` | 0.3304 | 0.0160 | [0.2894, 0.3714] | 6 | equal |
| `ladder_Z_step_I.Z.m0FFF_to_I.Z.full_W` | 0.1723 | 0.0424 | [0.06314, 0.2814] | 6 | equal |
| `ladder_Z_slope_pJ_per_issued_uop` | 2.726 | 0.0987 | [2.473, 2.980] | 6 | equal |
| `ladder_Z_slope_W_per_row` | 0.09848 | 0.00434 | [0.08731, 0.1096] | 6 | equal |
| `ladder_R_step_I.R.m0000_to_I.R.m00FF_W` | 12.88 | 0.0219 | [12.83, 12.93] | 7 | equal |
| `ladder_R_step_I.R.m00FF_to_I.R.full_W` | 12.94 | 0.0301 | [12.87, 13.01] | 7 | equal |
| `ladder_R_slope_pJ_per_issued_uop` | 45.00 | 0.0759 | [44.81, 45.19] | 7 | equal |
| `ladder_R_slope_W_per_row` | 1.614 | 0.00160 | [1.610, 1.618] | 7 | equal |

**The held line and the two ratios**

| price (the reducer's name) | mean | se | 95 % interval | n | verify-e196d |
|---|---|---|---|---|---|
| `held_line_at_0_minus_mask0_pJ_per_op` | 323.5 | 48.0 | [206.1, 440.8] | 7 | equal |
| `held_full_minus_line_at_512_pJ_per_op` | -120.4 | 53.8 | [-252.0, 11.29] | 7 | equal |
| `held_ladder_middle_step_ratio` | 0.9909 | 0.0207 | [0.9403, 1.042] | 7 | equal |
| `zero_ladder_first_step_ratio` | 1.402 | 0.197 | [0.9210, 1.884] | 7 | equal |

**Per multiply-add**

| price (the reducer's name) | mean | se | 95 % interval | n | verify-e196d |
|---|---|---|---|---|---|
| `lanes_clock_plus_accumulator_writes_per_mac_board_pJ` | 1.818 | 0.00582 | [1.804, 1.832] | 7 | equal |
| `lanes_clock_plus_accumulator_writes_per_mac_rail_pJ` | 1.565 | 0.0173 | [1.523, 1.607] | 7 | equal |
| `data_part_per_issued_mac_random_board_pJ` | 3.552 | 0.00839 | [3.532, 3.573] | 7 | equal |

**Spread, the MSK bit alone, mask 0, B through gated micro-ops**

| price (the reducer's name) | mean | se | 95 % interval | n | verify-e196d |
|---|---|---|---|---|---|
| `spread_I.H.m0F0F_minus_I.H.m00FF_W` | 0.2844 | 0.0228 | [0.2285, 0.3402] | 7 | equal |
| `spread_I.H.m3333_minus_I.H.m00FF_W` | 0.6087 | 0.0341 | [0.5252, 0.6923] | 7 | equal |
| `spread_I.H.m5555_minus_I.H.m00FF_W` | 1.225 | 0.0291 | [1.153, 1.296] | 7 | equal |
| `msk_null_I.H.mFFFF_minus_I.H.full_pJ_per_op` | -18.97 | 34.8 | [-104.0, 66.07] | 7 | equal |
| `mask0_I.H.m0000_minus_zero_W` | 0.06177 | 0.0220 | [0.007839, 0.1157] | 7 | equal |
| `mask0_I.R.m0000_minus_zero_W` | 0.3951 | 0.0218 | [0.3417, 0.4484] | 7 | equal |
| `mask0_Z.a0.m0000_minus_zero_W` | 0.2781 | 0.0375 | [0.1864, 0.3699] | 7 | equal |
| `b_through_gated_micro_ops_W` | 0.5471 | 0.0301 | [0.4734, 0.6208] | 7 | equal |

**The fields**

| price (the reducer's name) | mean | se | 95 % interval | n | verify-e196d |
|---|---|---|---|---|---|
| `field_F.Bs_fJ_per_operand_flip_board` | 129.1 | 12.3 | [98.87, 159.3] | 7 | equal |
| `field_F.Bs_fJ_per_flip_all_board` | 43.02 | 4.11 | [32.96, 53.09] | 7 | equal |
| `field_F.Bs_electrons_per_operand_flip_rail` | 1.632 x 10^6 | 1.69 x 10^5 | [1.218 x 10^6, 2.045 x 10^6] | 7 | equal |
| `field_F.Be_fJ_per_operand_flip_board` | 46.92 | 0.432 | [45.86, 47.98] | 7 | equal |
| `field_F.Be_fJ_per_flip_all_board` | 31.28 | 0.288 | [30.58, 31.99] | 7 | equal |
| `field_F.Be_electrons_per_operand_flip_rail` | 4.263 x 10^5 | 2.13 x 10^4 | [3.742 x 10^5, 4.784 x 10^5] | 7 | equal |
| `field_F.Ae_fJ_per_operand_flip_board` | 51.99 | 2.11 | [46.83, 57.15] | 7 | equal |
| `field_F.Ae_fJ_per_flip_all_board` | 34.66 | 1.41 | [31.22, 38.10] | 7 | equal |
| `field_F.Ae_electrons_per_operand_flip_rail` | 4.596 x 10^5 | 7.13 x 10^4 | [2.853 x 10^5, 6.340 x 10^5] | 7 | equal |

**The zero shares**

| price (the reducer's name) | mean | se | 95 % interval | n | verify-e196d |
|---|---|---|---|---|---|
| `share_Z.a50` | 0.5374 | 0.00109 | [0.5348, 0.5401] | 7 | equal |
| `r_from_Z.a50` | 0.07485 | 0.00218 | [0.06951, 0.08019] | 7 | equal |
| `share_Z.b50` | 0.5700 | 0.00180 | [0.5656, 0.5744] | 7 | equal |
| `r_from_Z.b50` | 0.1400 | 0.00360 | [0.1312, 0.1488] | 7 | equal |
| `share_Z.ab50` | 0.2931 | 0.00195 | [0.2883, 0.2979] | 7 | equal |
| `r_from_Z.ab50` | 0.08689 | 0.00251 | [0.08073, 0.09304] | 7 | equal |

**The ties**

| price (the reducer's name) | mean | se | 95 % interval | n | verify-e196d |
|---|---|---|---|---|---|
| `tie_random_pJ_per_mac_board` | 5.787 | 0.00771 | [5.769, 5.806] | 7 | equal |
| `tie_zeros_S_W` | 1.914 | 0.0164 | [1.874, 1.954] | 7 | equal |
| `tie_pi_S_W` | 10.40 | 0.0340 | [10.32, 10.48] | 7 | equal |
| `tie_ones_D_W` | 8.375 | 0.0481 | [8.257, 8.493] | 7 | equal |
| `tie_random_D_W` | 24.70 | 0.0383 | [24.60, 24.79] | 7 | equal |
| `tie_a_zero_D_W` | 0.8252 | 0.0272 | [0.7587, 0.8918] | 7 | equal |
| `tie_sparse50_D_W` | 7.275 | 0.0399 | [7.177, 7.372] | 7 | equal |
| `tie_b_sign_D_W` | 0.5851 | 0.0389 | [0.4900, 0.6802] | 7 | equal |

**3.5 The trains** (E182's statistic; raw board watts; a unit is one SFFS and one FSSF process):

| train | F against S | processes with a value | units | D = F - S (W) | se | 95 % interval | D per op, board (pJ) [95 %] | anchors' drift (W) | verify-e196d |
|---|---|---|---|---|---|---|---|---|---|
| T1 | `T.Z.m1111` against `I.Z.m000F` | 24 of 24 | 12 | 0.4591 | 0.00566 | [0.4466, 0.4715] | 406.8 [395.8, 417.9] | -0.1235 | equal |
| T2 | `T.Z.m5555` against `I.Z.m00FF` | 24 of 24 | 12 | 0.6042 | 0.00480 | [0.5936, 0.6148] | 535.4 [526.1, 544.8] | +0.0735 | equal |

The trains ran on the request's `x14_host`; the anchors and the passes on the lab's unchanged sparsity host (E196.md section 3).

**3.6 At the two sensitivity slopes** (the registered sensitivity arms, `sensitivity` in the file; headline prices only, every derived
price and every arm's D is in the file):

| price | at 0 W/°C | at 0.1994 W/°C (registered; the primary) | at 0.3803 W/°C |
|---|---|---|---|
| `ladder_H_slope_pJ_per_issued_uop` | 17.23 | 16.63 | 16.09 |
| `ladder_Z_slope_pJ_per_issued_uop` | 2.709 | 2.726 | 2.742 |
| `ladder_R_slope_pJ_per_issued_uop` | 46.13 | 45.00 | 43.98 |
| `lanes_clock_plus_accumulator_writes_per_mac_board_pJ` | 1.866 | 1.818 | 1.774 |
| `data_part_per_issued_mac_random_board_pJ` | 3.633 | 3.552 | 3.479 |
| `field_F.Bs_fJ_per_operand_flip_board` | 118.8 | 129.1 | 138.4 |
| `field_F.Be_fJ_per_operand_flip_board` | 46.15 | 46.92 | 47.63 |
| `field_F.Ae_fJ_per_operand_flip_board` | 50.05 | 51.99 | 53.75 |
| `share_Z.a50` | 0.5379 | 0.5374 | 0.5370 |
| `share_Z.b50` | 0.5704 | 0.5700 | 0.5696 |
| `share_Z.ab50` | 0.2944 | 0.2931 | 0.2918 |
| `tie_random_pJ_per_mac_board` | 5.894 | 5.787 | 5.691 |

## 4. The checks, as the checker printed them (measured)

[`checks-e196.txt`](checks-e196.txt), whole:

```
check 1 (the ties): derived.tie_zeros_S_W REPRODUCES, derived.tie_random_D_W REPRODUCES, derived.tie_ones_D_W REPRODUCES, derived.tie_sparse50_D_W REPRODUCES, derived.tie_a_zero_D_W REPRODUCES, derived.tie_pi_S_W REPRODUCES, derived.tie_b_sign_D_W REPRODUCES, arms.I.Z.m0000.S_W REPRODUCES
check 2 (the MSK bit alone): EQUAL
check 3 (the held ladder's middle steps): STRAIGHT
check 4 (the read-backs): PASS
check 5 (cycles per op): PASS
check 6 (the trains' anchors and carry-over): T1 AGREE, T2 AGREE
CHECKS-E196: 1 8 of 8 REPRODUCE (0 not computed); 2 EQUAL; 3 STRAIGHT; 4 PASS (108 of 108 ok; 108 at the full plan); 5 PASS (209 kept runs, 672 train launches, 0 deviations); 6 T1 AGREE T2 AGREE; reported: 7 passes kept; 1 runs set aside; 68 dips; 0 samples off 600 MHz; readback_gate 214 of 214 unchanged-host runs; 0 unreadable host outputs
```

**Check 1, the ties** (E196.md 8.1's rule: REPRODUCES when |E196's mean - the reference| is at most E196's 95 % half-width plus the
reference's published half-width; the references are the lab's own published figures, registered in E196.md 8.1 and in
`check_e196.py`):

| tie | E196, mean (95 % half-width) | the reference (95 % half-width), E196.md 8.1 | its source | difference | reading |
|---|---|---|---|---|---|
| `derived.tie_zeros_S_W` | 1.914 (0.040) | 1.986 (0.059) | E78 fp32 zeros S over idle | -0.0719 | REPRODUCES |
| `derived.tie_random_D_W` | 24.70 (0.094) | 24.725 (0.082) | E78 randn D | -0.0266 | REPRODUCES |
| `derived.tie_ones_D_W` | 8.375 (0.12) | 8.257 (0.221) | E78 ones D | +0.1182 | REPRODUCES |
| `derived.tie_sparse50_D_W` | 7.275 (0.098) | 7.302 (0.063) | E78 sparse50 D | -0.0274 | REPRODUCES |
| `derived.tie_a_zero_D_W` | 0.8252 (0.067) | 0.810 (0.065) | E78 a_zeros_b_randn D | +0.0152 | REPRODUCES |
| `derived.tie_pi_S_W` | 10.40 (0.083) | 10.398 (0.080) | E78 built-in pi S over idle | +0.0017 | REPRODUCES |
| `derived.tie_b_sign_D_W` | 0.5851 (0.095) | 0.563 (0.024) | E65 bit 31 (a DIFFERS is the transfer's size, never a failure) | +0.0221 | REPRODUCES |
| `arms.I.Z.m0000.S_W` | 0.3222 (0.099) | 0.376 (0.089) | E109 fp32 loop, no micro-op issued (three passes, labelled there) | -0.0538 | REPRODUCES |

- **Check 2, the MSK bit alone:** EQUAL. `msk_null_I.H.mFFFF_minus_I.H.full_pJ_per_op` -18.97 pJ per op, 95 % interval
  [-104.0, 66.07], which contains 0; `I.H.mFFFF`'s D -0.03072 W [-0.1233, 0.06189]; both arms at 546.001 cycles per op (equal rates).
- **Check 3, the held ladder's middle steps:** STRAIGHT. `held_ladder_middle_step_ratio` (the 8-to-12-row step over the 4-to-8-row
  step, per pass) is 0.9909, 95 % interval [0.9403, 1.042], which contains 1.0; the two steps' means are 2.439 W and 2.412 W.
- **Check 4, the read-backs:** PASS. 108 of 108 `X14CHECK` records ok, 108 at the full plan; the pass runs' read-backs are "not made
  (the lab's unchanged host reads no C back on file tiles)", never counted as ok.
- **Check 5, cycles per op:** PASS. 209 kept runs and 672 train launches, 0 deviations from 546.0 or 544.0.
- **Check 6, the trains' anchors and carry-over:** T1's anchors drift -0.1235 W and T2's +0.0735 W: both AGREE (within 0.3 W). The
  carry-over (L2 - L3, SFFS against FSSF, 12 units each), REPORTED with no verdict as registered: T1 -0.0069 W [-0.0296, +0.0158], T2
  +0.0118 W [-0.0093, +0.0330].
- **Also reported:** 28,783 samples, 0 off 600 MHz; 1 run set aside (approach off protocol), the one run off protocol; passes 0-6
  kept (7, not provisional); 68 dips; `readback_gate` 214 of the plan's 214 unchanged-host runs; 0 unreadable host outputs; 0 runtime
  lines dropped.

## 5. Beside verify-e196d's independent re-derivation

verify-e196d wrote its own reduction from E196.md, importing nothing from the kit, and ran it on the committed raw files.

- **Its numbers (REPORTED).** It compared 4,211 numeric values with step 13's `x14-e196.json`: all exactly equal. It re-ran the committed
  reducer on its own copy and got a byte-equal file. Its section 8 readings are the checker's: 8 of 8 REPRODUCE, EQUAL, STRAIGHT, PASS
  (108 of 108), PASS, T1 AGREE and T2 AGREE, and its carry-over values equal the checker's.
- **This lane's comparison of the two files** (desk check, leaf by leaf, standard library). Of the 3,403 numeric values in the kit's
  `x14-e196.json`, 3,390 are numeric values in the verifier's file at the same place, and all 3,390 are exactly equal (largest relative
  difference 0): 1,680 in the arms, 335 in the derived prices, 28 in the trains, 900 in the sensitivity arms, and 447 in the passes,
  `readback_gate` and the top-level values. The other 13 are the set-aside run's own readings, which the verifier's file records in another
  form (the same pass, seq, arm and reason). Its file adds, per train, the unit-order flags and the carry-over, whose values equal the
  checker's check 6 exactly. The two files count values differently, so its 4,211 and this lane's 3,403 are not the same count.
- **In section 3** every derived price and both trains read "equal": mean, standard error and 95 % interval, in full.

## 6. The verifier's findings, answered (dated clauses, Mon 16 Nov 2026)

| verify-e196d | what | answered |
|---|---|---|
| low 1 | the leakage slope, 0.1994 W/°C, was labelled a measured price in the card lane's report | Note 1 section 1 (`985554c6`) labels it registered: an input, beside the sensitivity slopes 0 and 0.3803. *Mon 16 Nov 2026:* this note lists it under section 3.1's registered inputs, and no measured table here names it; the committed output's `leak_W_per_C` is that input. |
| nit 2 | the approach as it ran (the 2 s counted from the last device process's end; the band at the close) | Note 1 section 2 gives the runner's logic, the recount and both readings; the registered code decides. *Mon 16 Nov 2026:* the prices here are at that reading: the reducer's one run set aside (pass 5 seq 22) is the rule's one run off protocol, and nothing is re-read or re-scored. |
| nit 3 | the round's commit helper adds two trailer lines after the scans | Note 1 section 3, item 1: a round convention, the orchestrator's call. *Mon 16 Nov 2026:* this note's commit carries the same two lines, and its scans read the full message and name them (section 7). |
| nit 4 | RAN WHOLE and RAN FULL, two words for one outcome | Note 1 section 3, item 2: RAN WHOLE is the registered word. *Mon 16 Nov 2026:* this note uses no other. |

This note also answers two open items. The card lane's: the reduction's outputs were not committed, and a later lane was to commit them in
a dated note. fix-e196d's: line 1 of `x14-e196.txt` holds a desk path, so it could not be committed byte for byte; section 1 gives the
marked redaction and the original's sha256. *A precision on note 1's interpreter line (Mon 16 Nov 2026):* note 1 names numpy 1.26.4
beside `/usr/bin/python3` 3.12.3. The box has it, but neither the reducer nor the checker imports it (section 2), so step 13's
interpreter is Python 3.12.3 with its standard library.

## 7. Checks before the commit

- **The sums.** `SHA256SUMS-note2` reads back, 5 of 5. In the lab clone, README.md's `SHA256SUMS` and `SHA256SUMS-note1` still read
  back, and neither README.md nor note 1's files changed since their commits.
- **New files only.** None of the six names was in this directory before this commit.
- **The desk-path gate** (`nopath_q142s.py`, v3.1) over the six files: clean.
- **The login and public-text scans** read the six files and this commit's message: the round's login check, the lab's sanitizer list
  ([`tools/timeline/sanitize_extracts.py`](../../../../tools/timeline/sanitize_extracts.py)) with this box's privacy table, the round's
  word classes, and the two scanners README.md's scan used. They found nothing in the six files. In the message, the only matches are the round's two standard trailer lines: the co-author line's address and the session line's link.
- **The seal.** The numbers of the request's withheld lines (redaction R1, E196.md section 0), searched as whole numbers in the six files
  and the message: no withheld number counts. The rule's other matches, each named with its line in this lane's log, are of three accepted kinds: E196.md 8.1's registered references and their half-widths, public in `check_e196.py` since the kit (in `checks-e196.json` and section 4's table); the digits of an experiment's name in a source string, which R1 keeps; and digits inside a sha256.

## What does not change

README.md, `SHA256SUMS` and note 1's two files stay as committed, and no committed file changes. No number, price, rule, verdict, check or
gate reading changes; nothing is scored, and no forecast number is here.

SPDX-License-Identifier: Apache-2.0
