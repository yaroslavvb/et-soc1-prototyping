# E178: one-number matrices on aifoundry3 card 0 - int8 5s cost more than 4s (E178-H-int8 POSITIVE, +0.053 W [+0.022, +0.085]), at about 0.29 of M10's frozen price (SIZE FAIL HIGH; E178-W-int8 FAIL HIGH, 2.78 fJ a flip against 7.48); the int8 kinds order as P orders them (E178-R-int8 PASS, rho +0.643); equal-flip kinds read equal in all three formats; the float 4s-5s pairs, E178-U and E178-S-int8 NOT RESOLVED; every launch's C bit-exact

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds". It answers the owner's ask of Thu 5 Nov 2026, about 19:30 PST ("here's a matrix filled with one
number, and here's a matrix filled with another number, and they require different number of transistor flips, therefore they will use
different power, and I have a model which actually tracks it down"), as registered in [`tools/claims-v3/e178/E178.md`](../../../../tools/claims-v3/e178/E178.md)
with its dated notes A1-A4 and M1 and kitted by [`KIT.md`](../../../../tools/claims-v3/e178/KIT.md) with its
[dated note 1](../../../../tools/claims-v3/e178/KIT.md.dated-note-1.md). Fri 6 Nov 2026 (week 45), the card day Q149, on the owner's go of that
morning (about 09:20 PST), aifoundry3 card 0 at 600 MHz pinned, after E181 (M11's session 2) had ended and its step 22 had copied back.
**Blind:** every forecast and rule below was committed before the session's opening config read on the card (A2-4's first datum).*

- **Card:** aifoundry3 card 0, **600 MHz in all 26,541 samples**; `ettelem config` through E128's guard at the session's start (11:33:24
  PST) and end (12:18:36): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV both times. **Nothing was set.** `since_reset_ms` −1 in
  every sample: no statistics reset.
- **Card session** 11:33:24-12:18:36 PST, **45.2 card-minutes** (T0 + 2,712 s), inside FULL's cap of 60: the stop-path test 17802, the smoke
  17801 and its gate (PASS at 11:34:21), then **FULL as registered**: kinds passes 17810 (689 s), 17811 (647 s), 17812 (640 s) and 17813
  (639 s), the fourth admitted by the budget rule (it started at T0 + 2,063 s, projected 689 s, against the last end T0 + 3,540 s). **All four
  passes kept** on the registered primary; nothing set aside; no kind left out by E178-C.
- **Every launch's C is bit-exact:** 3,130 of 3,130 PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`, `--jobs 2`; fp32 1,284, fp16
  912, int8 934; no ROUNDING, UNMODELLED or FAIL): 60 in the smoke and 770, 780, 760 and 760 in the four passes. The five sessions that must
  carry a C log each carried one, checked to its end (`ccsessions_e178.py`: FINISHED); the stop-path test carried none. **E178-C PASS: 2,190
  of 2,190 launches of E178's 40 kinds PASS.** The smoke's C, reported: `fp32.e178_uf` (whose accumulator must read +0 throughout),
  `int8.e178_v85` and `int8.e178_v127` (whose int32 accumulators wrap within a launch) each 6 of 6 launches PASS against the reference
  arithmetic, as every other smoke item.
- **No stop fired** in any pass: the highest live readings were **54.06 W board** and **62 °C `minshire[0]`** (the stops 65 W / 70 °C), 50.03
  W and 53 °C in the smoke. The stop-path test fired all three stops on live samples with no launch.
- **Every device-management command sent was a read** (§ Device commands sent).
- **Five runs were skipped by E78's own rule**, each "launch reading not reached" (its approach ended at 59 °C, above the 58 °C launch line)
  and not retried: pass 17810 #11 `int8.e178_v4`, 17812 #32 `fp32.e178_v5` and #73 `fp32.e178_a4_b5`, 17813 #34 `fp16.e178_v4` and #43
  `fp16.e178_a5_b4` (`aifoundry3/e178/p178NN/run.log`). So 299 of 304 runs are kept; three couple-rule passes read two couples instead of
  three (H-int8 in 17810, H-fp32 in 17812, H-fp16 in 17813), as the registered statistic reads them; `fp32.e178_a4_b5` and
  `fp16.e178_a5_b4` are measured in three passes, every other kind in four.

## The answer (the registered rules, blind)

The scorer's words govern (A2-1): **FAIL HIGH = the forecast is above the measured interval: the model prices more than the card reads.**
Each interval is m ± t(0.975, n − 1) sd/√n over the kept passes; dP and dF are the scored forecasts (frozen P and F × s × the kind's measured
rate / E171's rate; s = 1.00590 for the floats from `fp32.randn` and `fp16.randn`, 1 for int8).

| rule | what | measured, W (95%) | forecast P / F, W | verdict |
|---|---|---|---|---|
| **E178-C** | every launch of every E178 kind C-checked | 2,190 of 2,190 PASS | all | **PASS** |
| **E178-H-int8**, his pair | int8 5s − 4s, three adjacent couples a pass | **+0.0532 [+0.0217, +0.0848]**; per pass +0.045, +0.082, +0.050, +0.036 | +0.1857 / +0.1871 (frozen +0.1862 / +0.1877) | **POSITIVE**, SIZE **FAIL HIGH** (P and F) |
| **E178-H-fp32** | fp32 5s − 4s | +0.0523 [−0.0459, +0.1505] | +0.0087 / +0.0303 | **NOT RESOLVED**, SIZE PASS / PASS |
| **E178-H-fp16** | fp16 5s − 4s | +0.0558 [−0.0038, +0.1154] | +0.0173 / +0.0389 | **NOT RESOLVED**, SIZE PASS / PASS |
| **E178-U** | fp32 ones − 1.5 × 2^−64 (equal popcount; the second's accumulator never moves) | +0.0452 [−0.0314, +0.1217] | +0.0743 / +0.1303 | **NOT RESOLVED**, SIZE PASS / FAIL HIGH |
| **E178-S-int8** (A1-1) | int8 85 − neg_ones, one run each a pass | +0.0582 [−0.0770, +0.1935] | +0.3555 / +0.3580 (a held-1-bit model: negative) | **NOT RESOLVED**, SIZE FAIL HIGH / FAIL HIGH |
| beside it, never a verdict (A1-1) | int8 127 − neg_ones | +0.0271 [−0.0828, +0.1371] | +0.2420 / +0.2439 | reads across 0 |
| **E178-R-int8** | Spearman rho of the scored P against measured D, 13 int8 kinds | **rho +0.643** | ≥ 0.56 | **PASS** |
| **E178-W-int8** | OLS slope of D on (i)'s launch-mean flips, 13 int8 kinds | **2.78 fJ a flip [1.51, 4.05]** | P's 7.48 | **FAIL HIGH** |
| **E178-E-int8** | equal flips read equal: int8 ones, 2, 4, 8 | spread 0.0669 | 95% point 0.2460 | **PASS** (read equal) |
| **E178-E-fp32** | fp32 0.5, 1, −1, 2, 4, 8 | spread 0.1048 | 0.1958 | **PASS** (read equal) |
| **E178-E-fp16** | fp16 0.5, 1, −1, 2, 4, 8 | spread 0.1749 | 0.1811 | **PASS** (read equal) |

**The owner's sentence (A1-1, with A2-2's limit): not measured.** It needs four rules to read together: E178-H-int8 POSITIVE with SIZE PASS,
E178-S-int8 POSITIVE, E178-R-int8 PASS and E178-W-int8 PASS. Here E178-H-int8 is POSITIVE but its SIZE FAILS HIGH, E178-S-int8 does not
resolve and E178-W-int8 FAILS HIGH; only E178-R-int8 passes.

**What the card says, in plain words.** In int8, a matrix of 5s does draw more power than a matrix of 4s: +0.053 W at the board, resolved in
all four passes, the direction the flip model gives. But it is about 0.29 of what M10's frozen price says (+0.186 W), and the card's price
per flip (by (i)'s count) over the 13 int8 kinds is 2.78 fJ [1.51, 4.05], about 0.37 of M10's 7.48 fJ. The thirteen int8 numbers order as P
orders them (rho +0.643), and the numbers whose accumulators count alike (1, 2, 4, 8) read alike. Whether the held operands' 1-bits rather
than the flips set the order (E178-S-int8) is not resolved at this resolution. In the floats, 4s against 5s stays below what the card
resolves (as registered: power 0.05-0.13), and so does E178-U.

Sources: [`results.md`](results.md) and [`scored.json`](scored.json) (`score_e178.py`, run by step 22 v2 after its C-session gate), the
primary reduction [`e178.json`](e178.json) and [`runs.csv`](runs.csv) (`reduce_e178.py`, E78's reduction unchanged, on E171's registered
footing: `--leak 0.20563713796102187 --no-refit --drop-dips`, E78's gates), [`ccheck/ccheck-all.json`](ccheck/ccheck-all.json),
[`logs/session.log`](logs/session.log).

## Reported beside, never a verdict

All from `scored.json` › `primary` › `reported` (the scorer's per-pass difference of the two kinds' D, t interval over the kept passes), the
measured value against the scored dP:

| pair | measured, W (95%) | dP, W | reading |
|---|---|---|---|
| int8 his pair in pass form, 5s − 4s | +0.0724 [+0.0117, +0.1331] | +0.1857 | positive; dP above |
| int8 crossed (A 4, B 5) − 4s | +0.0937 [+0.0282, +0.1591] | +0.1241 | positive; dP inside |
| int8 crossed (A 4, B 5) − (A 5, B 4) | +0.0028 [−0.1231, +0.1286] | +0.0154 | across 0; dP inside |
| the bridge, int8 neg_ones − ones | +0.1227 [−0.2126, +0.4579] | +0.1094 | across 0; dP inside; the same sign as E78's +0.069 ± 0.045 and E82's +0.116 ± 0.049 (± 1 se, post hoc) |
| the bridge, fp32 / fp16 neg_ones − ones | −0.0543 [−0.1166, +0.0081] / +0.1001 [−0.0115, +0.2118] | −0.0008 / +0.0019 | across 0 |
| int8's largest, 85 − ones | +0.1809 [−0.0297, +0.3915] | +0.4649 | across 0; dP above |
| int8's smallest, 2 − 4 (P equal) | +0.0586 [−0.0119, +0.1291] | 0.0000 | across 0; dP inside |
| fp32's largest, (A 5, B 4) − 1.5 × 2^−64 | −0.0200 [−0.1165, +0.0766] | +0.0904 | across 0; dP above |
| fp32's smallest, (A 4, B 5) − (A 5, B 4) (3 passes) | +0.0595 [−0.2502, +0.3692] | −0.0003 | across 0; dP inside |
| fp16's largest, 6 − 0.5 | +0.0251 [−0.1284, +0.1787] | +0.0219 | across 0; dP inside |
| fp16's smallest, (A 4, B 5) − (A 5, B 4) (3 passes) | +0.0930 [−0.0543, +0.2403] | −0.0022 | across 0; dP inside |
| A2-2's 85 − 127 (read by the rail arm's board column) | +0.0311 [−0.1188, +0.1810] | +0.1127 (A2-2's second account about −0.044) | across 0; not expected to resolve (A2-2) |
| equal flips, different values: 21 pairs | 18 read across 0; three read below 0: fp16 2 − neg_ones −0.1749 [−0.2496, −0.1001], fp16 4 − neg_ones −0.1458 [−0.1661, −0.1255], int8 4 − 8 −0.0669 [−0.1241, −0.0097] | each at most 0.0045 in size | P inside in 18 of 21 |
| equal popcount, different flips: 6 pairs | all across 0 (int8 5 − 3 −0.0100 [−0.0615, +0.0415] against dP +0.0542) | +0.017 to +0.074 | P inside in 5 of 6 (not int8 5 − 3) |
| the floats' ranking and slope, reported | fp32: Spearman against P −0.046 (14 kinds), slope 0.35 fJ a flip (se 1.15); fp16: +0.280 (13), 3.44 fJ (se 6.45) | | |

Every kind's measured D sits against its scored P in `scored.json` › `primary` › `reported` › `kinds`: **every int8 kind reads below P**, by
0.048 W (int8 8) to 0.354 W (int8 85), the misses larger where P gives more flips (E178-W-int8's reading); the float kinds read from 0.039 W
below P (fp16 (A 5, B 4)) to 0.154 W above it (fp32 1.5 × 2^−64), 23 of the 27 above.

**The seven reduction arms** (`results.md`, reported): the arms with the dips removed (auto), the gates off, and the leak slopes 0 and 0.1994
read every verdict as the primary does; the leak slope 0.3803 reads E178-H-int8 NOT RESOLVED and E178-R-int8 FAIL; the session's own
footing (two passes kept, 17812-17813) reads E178-H-int8 NOT RESOLVED; the frozen slope with the dips kept keeps one pass (E78's gates set
17810-17812 aside on anchor spans and drift with the dips in) and scores nothing. No arm was dropped (`arms-dropped.txt` absent).

### The minion-rail arm (dated note A3, read by A4's reader v2), reported, never a verdict

Read at the desk after step 22 v2 and before this commit, by A4-5's three lines exactly (12:32:03 PST): `SHA256SUMS-e178-a3` 34 of 34 OK,
`SHA256SUMS-e178-a4` 44 of 44 OK, then `python3 -B tools/claims-v3/e178/rail_e178_v2.py read` on this session's `runs.csv`, `e178.json` and
`scored.json`, exit 0: 52 contrasts (48 distinct readings), 299 kept runs, every one with a Drail, none flagged; the board column reproduces
the scorer's own reading of every rule contrast and reported pair (`cross_check_with_scored_json` ok). Its forecasts are the frozen board
forecast times E171's median Drail/D (fp32 0.8096, fp16 0.8080, int8 0.8379) on the rail, and times one less it off the rail.

| contrast | board D, W | minion rail Drail, W | off the minion rail, D − Drail, W |
|---|---|---|---|
| E178-H-int8, int8 5s − 4s | +0.0532 [+0.0217, +0.0848] | **+0.0261 [−0.0281, +0.0804]**, spans 0; forecast +0.1560 (P) **above** | +0.0271 [−0.0189, +0.0731], spans 0; forecast +0.0302 (P) inside |
| E178-H-fp32 | +0.0523 [−0.0459, +0.1505] | +0.0422 [−0.0887, +0.1731]; +0.0080 inside | +0.0101 [−0.1610, +0.1812]; +0.0019 inside |
| E178-H-fp16 | +0.0558 [−0.0038, +0.1154] | +0.0292 [−0.0251, +0.0835]; +0.0135 inside | +0.0266 [−0.0646, +0.1177]; +0.0032 inside |
| E178-U | +0.0452 [−0.0314, +0.1217] | +0.0328 [−0.1174, +0.1829]; +0.0606 inside | +0.0124 [−0.1461, +0.1709]; +0.0143 inside |
| E178-S-int8, 85 − neg_ones | +0.0582 [−0.0770, +0.1935] | +0.0688 [−0.0436, +0.1812]; +0.2974 above | −0.0106 [−0.1177, +0.0965]; +0.0575 inside |
| 127 − neg_ones | +0.0271 [−0.0828, +0.1371] | +0.0177 [−0.0856, +0.1210]; +0.2029 above | +0.0095 [−0.1296, +0.1485]; +0.0393 inside |
| 85 − 127 (A2-2) | +0.0311 [−0.1188, +0.1810] | +0.0512 [−0.0243, +0.1266]; +0.0944 inside | −0.0201 [−0.1015, +0.0614]; +0.0183 inside |
| the bridge, int8 neg_ones − ones | +0.1227 [−0.2126, +0.4579] | +0.0630 [−0.1142, +0.2401]; +0.0921 inside | +0.0597 [−0.1166, +0.2360]; +0.0178 inside |
| int8's largest, 85 − ones | +0.1809 [−0.0297, +0.3915] | +0.1318 [−0.0001, +0.2637]; +0.3894 above | +0.0491 [−0.0355, +0.1338]; +0.0754 inside |

Over all 52: the rail's P forecast is inside its interval in 42, above it in 7 (E178-H-int8 and its pass form, E178-S-int8, 127 − neg_ones,
85 − ones, int8 5 − 3, and fp32 (A 5, B 4) − 1.5 × 2^−64) and below it in 3 (the fp32 crosses, three passes); the rail intervals read above 0 in 3
(the fp32 crosses), below 0 in 1 (int8 5 − 3, −0.0632 [−0.1174, −0.0090]) and span 0 in 48. For his pair the board resolved what the rail
did not: here the rail was not the finer line (A3-3 claimed nothing for its resolution). Full table: [`rail-arm-e178.md`](rail-arm-e178.md),
every pass and column in [`rail-arm-e178.json`](rail-arm-e178.json).

### Not read here

E178's two other reported arms are read after this commit, by their own registered readings, at the desk (the card day's arms-e178 lane):
Q148(c)'s constant-lane term (`tools/claims-v3/m10-c/`, its 27 float forecasts frozen in `6b5ad913`) and october-forecast-model (dated note
M1, `97a5e16b`, by M1-4). Neither is a rule of E178, and no verdict above depends on them.

## The readings, labelled

Everything here is measured on the card in this session.

| what | reading | source |
|---|---|---|
| card-minutes | **45.2** of a 60 cap (3,600 s from T0, 60 s reserve): config reads at 11:33:24 and 12:18:36 PST; T0 11:33:24 | `logs/config-session-start.json.time`, `logs/config-session-end.json.time`, `logs/queue.out` |
| the timeline | the stop-path test 11:33:24-11:33:38; the smoke 11:33:38-11:34:21 and its gate PASS; 17810 11:34:21-11:45:50, 17811 11:46:00-11:56:47, 17812 11:56:57-12:07:37, 17813 12:07:47-12:18:26 (each rc 0); the queue done at T0 + 2,712 s (12:18:36), the session end 12:18:36 | `logs/session.log`, `logs/queue.out` |
| the stop-path test (17802, no launch) | the die stop at 1 °C fired on `minshire[0]` 50.0 °C, the board stop at 1 W on 23.4 W, the in-run watcher's board stop at 1 W on 23.26 W, each read from the live sampler file within 0.12 s of its sample; each run ended with exit 6 | `aifoundry3/e178-stoptest/p17802/` (`STOP.die`, `STOP.board`, `STOP.watch`, `stoptest.rc`) |
| the smoke (17801, 10 items, 2 s each) | 5 launch records each; median cycles per op 546.001 (floats) and 318.0 (int8); 0.5994-0.5997 GHz; every dumped tile equal to its registered sha256; 403 samples, board 23.02-50.03 W, `since_reset_ms` −1; the C log's launch gaps median 3.0 ms (max 5); **SMOKE-GATE PASS** | `logs/session.log`, `aifoundry3/e178-smoke/p17801/` |
| peaks, the four passes | board 53.82, 53.81, 53.87 and **54.06 W**; `minshire[0]` 62 °C in each; the stops 65 W / 70 °C (`run_e78.py --max-c 70`), none reached | `aifoundry3/e178/p178NN/telemetry.jsonl.gz` |
| clock and statistics | 600 MHz in 26,541 of 26,541 samples (the stop-path test, the smoke and the four passes); `since_reset_ms` −1 in every one | the six `telemetry.jsonl.gz` |
| config at both ends | TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV at the session's start and end, and at the runbook's step-9 read (11:32:03) | `logs/config-session-start.json`, `logs/config-session-end.json` |
| the order | every kept pass ran `plan-e178.json`'s registered order (`order_as_registered` true for 17810-17813) | `scored.json` |
| the reduction | 4 passes kept, 299 runs; idle consistency median \|S − S0 − D\| 0.048 W; carry-over slope −0.00014 ± 0.00062 W/W (295 runs) | `reduce.txt` |
| the noise, for the record | the int8 couple's per-pass sd was about 0.020 W (half-width 0.032 W at four passes), against the registered noise model's 0.125/√3 W a pass for a core couple | `scored.json` › `primary` › `rules` › `E178-H-int8` › `per_pass` |

## Registered before any data, and what the box ran

Every E178 text below was committed before the session's opening config read on the card (A2-4's first datum), one ancestry chain in the
lab repository (PST): the registration `48171930` (Thu 5 Nov 20:51:01), dated note A1 `f421c67a` (22:12:30), the kit `a4aafc6f` (23:06:28),
A2 `c212a345` (Fri 6 Nov 00:05:00), the kit's dated note 1 `763307e7` (01:56:48), A3 `77768027` (05:17:12, the reported minion-rail arm),
A4 `d48135dd` (06:40:23, its reader v2) and M1 `97a5e16b` (10:01:16, october-forecast-model's frozen forecasts, a reported arm). Q148(c)'s
constant-lane term was registered `c71fbc7f` (05:27:58) and fitted with its E178 forecasts frozen `6b5ad913` (05:39:33), fixed `d62d0c8f`
(06:37:59). The readiness critic (Q146(f)) read E178 READY WITH GAPS at about 04:50 PST; its one owed note was A3. `git log --all` showed no
`docs/reports/data/*e178*` before this commit.

The owner's go came at about 09:20 PST with the lab boxes' fresh network approvals; the window, recorded by step 1 at 09:33:05: no session
starts after 15:30 PST and every run ends by 17:00 PST. E178 ran after E181's step 22 (11:09:23) and E181's data commit (`d4e5119d`,
11:21:42), by the kit's dated note 1 runbook (`KIT.md.dated-note-1.md` section 6, with box steps 2, 5 and 11 as v2), never KIT.md's v1
steps 2, 5 or 11, each step with the card day's one runbook output directory and lock file:

| box step | when (PST) | what it read |
|---|---|---|
| 2, `rb/s03_desk_e178_v2.sh` | 11:30:48-11:30:51 | pulled (`d4e5119d`); HEAD descends from `c212a345`, and from A3, A4 and M1; E178's paths clean; the five lists 76/27/72/17/47 OK, and A3's 34, A4's 44 and M1's 13; the kit and harness rebuilt; the orders verified; HARNESS OK 80; dated note M1 present; 0 E178 data commits |
| 3, the post | 11:31:18-11:31:24 | the day's one post already carried E178's clause, set at E181's end: read back, not edited |
| 4, `s05_look_k6.sh aifoundry3` | 11:31:33 and again 11:33:17 | FREE: et-who's "No process holds an ET-SoC-1 device node or card lock" (0 holder lines), no device process of ours or of another account; 12 terminals logged in (an idle login does not block, the owner's ruling of 1 November 2026); up 10 days 21 h |
| 5, `rb/s07_a3_sync_e178_v2.sh` | 11:31:45-11:31:46 | the 80 non-binary harness files in 30 paths, after `check_e178.py --desk` read them at the harness's sha256 |
| 6, `rb/s08_a3_preflight_e178.sh` | 11:31:52-11:31:53 | HARNESS OK: 84 files (the box binaries among them); `preflight_e178.sh` GO (32 send sites, 0 disallowed); `e178_common --verify` 0 problems |
| 7, `s09_a3_reads_k6.sh` | 11:32:02-11:32:03 | `et-lab-manifest`; the config through the guard: TDP 0 W / 65 °C / max_power / 600 MHz / 523 mV; et-who clean |
| 8, `rb/s10_a3_dry_e178.sh` start, wait | 11:32:18-11:32:37 | the dry job rc 0: 17810's 78 launches through the C wrapper, the smoke's 10, the start gate refusing with 8 (its two lines open `logs/session.log`, 11:32:35: "no device opened") |
| 9, `rb/s11_a3_session_e178.sh FULL` | 11:33:23-11:33:29 | launched detached (the dry job ended rc 0 today, no session or dry pass of ours running) |
| 10, `rb/s20_wait_e178.sh` | 11:33:37-12:18:44, six bounded calls | five said "call again", the sixth read the session end |
| 11, the handover, then `rb/s22_collect_e178_v2.sh` | 12:19:00-12:20:56; 12:21:03-12:31:22 | the post rewritten to the next run's clause; then the copies back (12:21:03-12:21:08), the collector v2 at nice 10, the gates (below) |

## Who checked it

Step 22 v2 ran its gates in order, each passing: the copies back; `collect_e178_v2.sh` (the check of C over every listed session, the
primary and its seven arms, `score_e178.py`; no arm failed, so none was dropped); the C-session gate (`ccsessions: 5 of 5 listed sessions
checked to the end: FINISHED`; the stop-path test with no launch or C record); the desk-path gate (`nopath: 343 files read ... 0 hit(s):
CLEAN`); and last the login check over every directory (`scrub_tree_e178.py --check`: `OK (131 files in 9 directories read, 0 left)`). Then
A4-5's three lines (above), and nothing else in `tools/claims-v3/e178/` ran before this commit (A4-1). No data verifier has read this
directory yet: the card day's verifier and fix pass for E178 follow its data commit.

## Device commands sent

As registered (E178.md section 7, "Device commands"): E171's harness and E78's card code unchanged, every telemetry call through E128's
guard (`ettelem config` with no argument, `ettelem sample --seconds --every-ms` and nothing else): `ettelem config` at the session's start and
end and at both ends of the stop-path test, the smoke and every pass, `ettelem sample` at 10 Hz in every block; and once before the session,
the runbook's step-9 read (`ettelem config` through the same guard, under card 0's lock). Sent: GET_MODULE_STATIC_TDP_LEVEL,
GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS,
GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all READs**, the two in bold PMIC voltage-register reads, which the owner's rule of
2 November 2026 allows. **Never sent**: the statistics reset (`since_reset_ms` −1 in every sample), any SET_*, the firmware-revisions query,
any residency read, any governor, TDP, threshold or clock set, any reset, and `dev_mngt_service` (the block's drain is a refusal). The
checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened: **GO**, 32 send sites, 0 disallowed
([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)); the same at step 6. No power cycle, and nothing near card 0's 75 W alarm (the
board's highest live reading 54.06 W).

## Card and post

`et-who` at the looks (11:31:33 and 11:33:17 PST), at the step-9 read (11:32:03) and at the session's start (11:33:24) and end (12:18:36):
no process held a device node or card lock, and no other account ran a device process. 12 terminals were logged in, as at the card day's
claim, whose finer look (09:33:58 PST) read them as 7 of ours and 5 of another account's, all idle; an idle login does not block, and no
login is named in any file. One session of ours ran on aifoundry3 at a time: E181's ended at 11:04
and its copy-back at 11:09, before this run's look; the day's next run, E180, follows this run's step 22. Nothing ran on aifoundry1 or
aifoundry2.

Fri 6 Nov's one `#community-lab` post is message `1568318213618540726`, created by the card day's claim at 09:36:40 PST. Before this run it
read `<ai> **Claude says:** using aifoundry3 for 1.5 h, until ~12:36 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`
(E178's clause, set at E181's end, 11:06:55), read back at 11:31:24 with no edit. **At this run's end, 12:19:16 PST**, under the Discord
lock and `EXPECT_TEXT`, dry-run, saved and read back (from the edit box, and from a fresh plan at 12:20:56: one post that day, its text equal
to the intended one), the clause became the next run's, every other word kept:
`<ai> **Claude says:** using aifoundry3 for 1.5 h, until ~13:49 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
Thu 5 Nov's post and every earlier day's were not touched.

## Privacy and the public-text scan (before the commit)

- **Logins.** Step 22 v2's last gate read every directory of the collection with `scrub_tree_e178.py --check` (0 left). Before this commit
  the final bytes were read again with files outside `tools/claims-v3/e178/` (A4-1): E164's `scrub_etwho_e164.py --check` (unchanged;
  `--owner` the box login of this repository's owner) in every directory of this one and of a scratch copy of the text inside its 16 `.gz`
  files (31 directories, every one rc 0), and a search of both for run_e78's "another user on this card" stop line and lib.sh's "others
  present" line (0 lines). The session log's et-who readings say "No process holds an ET-SoC-1 device node or card lock".
- **The public-text scan** (`tools/timeline/sanitize_extracts.py`'s fixed list, plus the private-network, Mac-home, scratch and e-mail
  patterns) over every text file and the text inside every `.gz` of this directory: 262 text files and 16 `.gz` files, 14,720 matches,
  14,714 of them the owner's own box home path and 6 the configs' tree key that names it, the reviewed class E166's, E171's, E176's and
  E181's committed data carry; no other match. The runbook's desk-path gate (`nopath_q142s.py`) read the final directory too: 347 files
  (this README and `SHA256SUMS` among them), 0 hits. This README and `SHA256SUMS` were scanned on their own afterwards (0 matches). The lab's private name table is absent on the Intel,
  so names were checked against the fixed list only (a stated coverage limit).

## Files

All files of step 22 v2's collection and score are here as step 22 left them (`diff -r` against `build/e178-out/`: equal), with the rail
arm's two files beside `scored.json` as A4-5 wrote them, plus this README and [`SHA256SUMS`](SHA256SUMS), which pins every file but this
README and itself.

| file | what |
|---|---|
| `scored.json`, `results.md`, `score.log` | the registered scorer's output on the registered primary, every arm beside |
| `e178.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the registered primary reduction of the four kinds passes |
| `e178-session.json`, `e178-auto-nodips.json`, `e178-kfrozen-dips.json`, `e178-leak*.json`, `e178-gatesoff.json` (with their `runs-*.csv`, `reduce-*.txt`, `reduce-*.log`) | the arms |
| `rail-arm-e178.json`, `rail-arm-e178.md` | the minion-rail arm (A3), read by A4's reader v2 |
| `ccheck/` | the C logs (`c-log-p178*.jsonl.gz`) and `ccheck.py`'s output (`ccheck-all.json`, `ccheck.txt`) |
| `aifoundry3/e178/p17810`-`p17813` | the passes as the box wrote them (`telemetry.jsonl.gz`, `runs.jsonl`, `run.log`, `marks.jsonl`, `block.json`, `plan.json`, the config reads, `c-log.jsonl.gz`, the tiles' and code's hashes, `manifest.txt`) |
| `aifoundry3/e178-smoke/p17801`, `aifoundry3/e178-stoptest/p17802` | the smoke and the stop-path test (its `STOP.die`, `STOP.board`, `STOP.watch`, `stoptest.rc`) |
| `logs/` | the session's own logs: `session.log` (with et-who's readings and step 8's two dry start-gate lines at its top), `queue.out`, `session.out`, the session config reads with their times and stderr, `dmcmd-preflight.txt`, `binaries.sha256` |
| `code.sha256` | the sha256 of every registered file the collection read |

## What it does to predicting power

- **The flips' direction holds blind in int8, the price does not.** M10's frozen forecast put int8 5s − 4s at +0.186 W, 96% of it its bus
  term at M10's price for those flips (A1-3). The card reads +0.053 W [+0.022, +0.085]: the sign as forecast, the size about 0.29 of it, and
  a price per flip of 2.78 fJ [1.51, 4.05] against M10's 7.48 fJ. Every int8 kind reads below its P, by more where P gives more flips. So A1-3's
  post hoc reading (M10 reads the int8 one-number kinds high) holds blind, and it is the price, not only a level: the pair's difference and
  the slope both read low. M10 prices what the int8 accumulator does (its flips by (i)'s count; A2-2's limit stands: the four rules cannot
  tell flips from 1-bits held at each read) at about 2.7 times what the card reads by the slope over the 13 kinds, and 3.5 times by his
  pair.
- **What holds for a model:** the int8 ranking (rho +0.643, PASS), the equal-flip groups in all three formats (PASS), and P's int8 order
  through its flips. **What does not:** M10's int8 bus price (E178-H-int8 SIZE and E178-W-int8 FAIL HIGH), and the four-rule reading of the
  owner's sentence. **Still open:** flips against held 1-bits (E178-S-int8 NOT RESOLVED, its interval across 0 and below P), the float
  one-number pairs (resolution about ±0.06-0.10 W here), and P against F in fp32 (E178-U).
- **For the next model:** a blind int8 one-number price near 2.8 fJ a flip on aifoundry3 at 600 MHz (its 95% interval 1.5-4.1 fJ), one
  session. The two reported arms read after this commit (Q148(c)'s constant-lane term and october-forecast-model) say whether a model that
  priced the int8 flips lower, or a level term for the floats, reads these kinds better.
- **Heat:** nothing is read or scored here (each run launched at E78's 58 °C line after heating to 59 °C, so heat is held out of the
  comparison by the protocol, and the die's live reading peaked at 62 °C).

SPDX-License-Identifier: Apache-2.0
