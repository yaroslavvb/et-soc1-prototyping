# E180: one-number vector adds on aifoundry3 card 0 - a matrix of 5s does not read above a matrix of 4s (E180-H NOT RESOLVED, +0.027 W [-0.050, +0.104]; the registered +0.165 W is above the interval, SIZE FAIL HIGH); the result's 1-bits cost about 0.0097 W a bit (E180-L [+0.0027, +0.0167]), about 1/17 of P's price and below every arm's; the kinds order as P orders them (E180-R PASS, rho +0.800); the operand's bits cost nothing (E180-O NULL); the integer add is flat (E180-I NULL); a running sum costs more (E180-A POSITIVE, +0.36 W), about 0.12 of its forecast

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds". It answers the owner's ask of Thu 5 Nov 2026, about 19:30 PST ("maybe even adding, like adding a
matrix filled with 4s is a different than adding a matrix filled with 5s ... Ideally it's one number, and then be able to forecast the number
of flips and then be able to test this experimentally"), as registered in [`tools/claims-v3/e180/E180.md`](../../../../tools/claims-v3/e180/E180.md)
with its dated notes [A1](../../../../tools/claims-v3/e180/E180.md.dated-note-A1.md), [M1](../../../../tools/claims-v3/e180/E180.md.dated-note-M1.md)
and [M2](../../../../tools/claims-v3/e180/E180.md.dated-note-M2.md), and kitted by [`KIT.md`](../../../../tools/claims-v3/e180/KIT.md) with its
dated notes [1](../../../../tools/claims-v3/e180/KIT.md.dated-note-1.md) (kit v2) and [2](../../../../tools/claims-v3/e180/KIT.md.dated-note-2.md).
Fri 6 Nov 2026 (week 45), the card day Q149, on the owner's go of that morning (about 09:20 PST), aifoundry3 card 0 at 600 MHz pinned, after
E178 had ended and its step 22 had copied back. **Blind:** every forecast and rule below was committed before the session's opening config
read on the card.*

- **Card:** aifoundry3 card 0, **600 MHz in all 24,301 samples**; `ettelem config` through E128's guard at the session's start (12:54:50 PST)
  and end (13:36:52): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV both times. **Nothing was set.** `since_reset_ms` −1 in every
  sample: no statistics reset.
- **Card session** 12:54:50-13:36:52 PST, **42.0 card-minutes** (T0 + 2,522 s), inside FULL's cap of 50: the stop-path test 18002, the smoke
  18001 and its gate (passed at 12:55:33), then **FULL as registered, all six passes**: 18010 (403 s), 18011 (403 s), 18012 (403 s), 18013
  (404 s), 18014 (403 s) and 18015 (403 s), the sixth admitted by the budget rule (it started at T0 + 2,109 s, projected 404 s, against the
  last end T0 + 2,940 s). Each pass ran its 47 configurations in `plan-e180.json`'s order and read **47 of 47 bursts** ok. **All six passes
  kept**; nothing set aside, nothing unreadable (`reduce_e180_v3.py`). Each pass's order equals `plan-e180.json`'s, run for run
  (`configs.json`; the runner refuses before any device opens otherwise), and so does the smoke's.
- **The build's first compile on a box** was this day's box step 6 (12:53:49-12:53:53): `BUILD OK`, `BUILD-E180.json` written 12:53:53,
  the kernel `b4b8ae32…` and the host `656fb80f…` ([`logs/build-e180.json`](logs/build-e180.json)); every session check compared them before
  any device opened (HARNESS OK, 88 files with the binaries).
- **The accumulating sums walk** (A1-7, read at the desk by `check_elf_e180_v2.py` on the box's own kernel listing, as dated note 2 binds):
  **261 PASS, 262 PASS**, the control mode 160 PASS ([`logs/elfcheck-e180-v2.txt`](logs/elfcheck-e180-v2.txt)). The box's own v1 line at
  step 6, kept beside and never read for a verdict, read 261 UNREAD ("the zeroing block found 2 time(s)") and 262 PASS: the case note 2
  section 1 expected and fixed ([`logs/elfcheck-e180.txt`](logs/elfcheck-e180.txt)).
- **No stop fired**: the highest live readings were **44.70 W board** and **57 °C `minshire[0]`** (the stops 65 W / 70 °C), 34.80 W and
  51 °C in the smoke. The stop-path test fired both stops on live samples with no launch.
- **Every device-management command sent was a read** (§ Device commands sent).

## The answer (the registered rules, blind)

The scorer's words govern (E178's dated note A2, which E180.md section 5 takes): **FAIL HIGH = the forecast is above the measured interval:
the model prices more than the card reads.** Each interval is m ± t(0.975, n − 1) sd/√n over the 6 kept passes. The forecasts are the
registered ones for aifoundry3 (`forecast-e180.json`); P is the primary, C, E, F and A its arms (E180.md section 4).

| rule | what | measured (95%) | forecast P (C / E / F / A) | verdict |
|---|---|---|---|---|
| **E180-H** | his pair: mean D(5s) − mean D(4s), three runs each a pass | **+0.0270 W [−0.0503, +0.1043]**; per pass +0.171, −0.012, +0.027, −0.036, +0.004, +0.008 | +0.1649 (+0.2197 / +0.0687 / +0.0352 / +0.0192) | **NOT RESOLVED**; SIZE **FAIL HIGH** for P and C, PASS for E, F and A |
| **E180-L** | the ladder: the OLS slope of D(kind) − D(zeros) on the result's 1-bits over the 21 fadd.ps one-number kinds | **+0.0097 W a bit [+0.0027, +0.0167]** | 0.1649 (0.2197 / 0.0687 / 0.0352 / 0.0192) | SIZE **FAIL HIGH for every arm; inside: none**; not footing-limited (A1-1) |
| **E180-O** | the operand's bits: c in D = a + b pop(result) + c pop(operand), same 21 kinds | +0.0046 W a bit [−0.0071, +0.0163] | NULL inside ±0.02 | **NULL** |
| **E180-R** | Spearman rho of P against the 21 kinds' mean D | **rho +0.800** | line 0.433 | **PASS** |
| **E180-E** | equal results read equal: the spread of the kinds' mean D | result popcount 2 (1.5, 2, 4, −1): 0.1255 W; popcount 3 (3, 5, 6, 8, −4): 0.0444 W | its 95% point under equality: 0.3386 / 0.1561 W | **PASS; PASS** |
| **E180-I** | the integer path: mean D over the 8 fadd.pi R4 kinds − D(fadd.pi zeros) | +0.1022 W [+0.0385, +0.1659] | NULL inside ±0.30 (P 0; F +0.041, A +0.046) | **NULL** |
| **E180-X** | float against integer: [D(fadd.ps 5s) − D(fadd.ps zeros)] − [D(fadd.pi 5s) − D(fadd.pi zeros)] | −0.0176 W [−0.1892, +0.1541] | +0.4947 (+0.6590 / +0.2062 / +0.0829 / +0.0321) | **NOT RESOLVED**; SIZE FAIL HIGH for P, C and E, PASS for F and A |
| **E180-A** | accumulating against plain: [D(fadd.ps.acc 4s) − D(fadd.ps.acc zeros)] − [D(fadd.ps 4s) − D(fadd.ps zeros)] | **+0.3596 W [+0.0683, +0.6510]**; per pass +0.562, +0.718, −0.087, +0.347, +0.235, +0.383 | +2.9631 (+3.9467 / +1.2350 / +1.5583 / +1.3850) | **POSITIVE**; SIZE FAIL HIGH for every arm; **outside P's offset band** (+0.752 to +4.261 W, A1-5: the band test "meets" binds, and this interval does not meet it); its arm reading is not a price test (A1 section 5); **walk verified by disassembly** (A1-7) |

**The owner's sentence for the add** (E180-H POSITIVE with SIZE PASS, P's slope inside E180-L, E180-O NULL): **not measured**. E180-H is
not resolved, and E180-L reads every arm's price above the card's.

In plain words: the result's 1-bits do cost power here, as the write-back's return to zero says they should (E180-L's interval lies above
0, and P's ranking of the 21 kinds holds, rho +0.800), but **about 0.0097 W per 1-bit of v + v, one seventeenth of P's 0.1649 W**, and below
even the lowest arm (A's 0.0192, the uniform price per RTL toggle). At that price his pair, one result bit apart, would differ by about
0.01 W, and this session resolves his pair to about ±0.08 W. So a matrix of 5s and a matrix of 4s read alike here, and the registered +0.165
W is too high. The operand's held bits cost nothing that the ladder can see (±0.012 W a bit), and the integer add reads flat inside its
margin. A running sum costs more than a fixed result, by +0.36 W on 4s, about 0.12 of P's +2.96 W and below the whole band the harts' start
offset allows.

The price, as arithmetic on E180-L's slope (post hoc, at the registered fadd.ps rate 4.5836 × 10^11 instructions a second): **about 21 fJ
per result 1-bit per instruction** ([6, 36] fJ; eight lanes, so about 2.6 fJ a lane), against P's 360 fJ; or, by the bench's 24.995 named
flips per result bit, **about 0.85 fJ per named flip** ([0.24, 1.45] fJ), against P's 14.395 fJ.

## Reported beside, never a verdict

From the scorer v3's reported arms (dated note A1 section 4; [`scored-e180.md`](scored-e180.md) and [`scored-e180.json`](scored-e180.json)
`reported_v2`, `reported_v3`). Words: the forecast reads **inside**, **above** or **below** the measured interval.

| reading | on | measured (95%) | forecast(s) |
|---|---|---|---|
| RA1, fadd.ps const − zeros | the board, D | +0.0675 W [−0.0393, +0.1742] | P +0.1649 inside; C +0.2197 above; E, F, A inside |
| | the net minion rail, R | +0.1110 W [−0.0275, +0.2495] | P +0.1277 inside; every arm inside |
| | D on FL1; on E60's slope | +0.0677 [−0.0375, +0.1729]; +0.0617 [−0.0356, +0.1590] | P +0.1649 inside; P +0.1672 above |
| RA2, his pair | R | −0.0160 W [−0.0773, +0.0452] | P +0.1277 above; C, E above; F +0.0272 and A +0.0148 inside |
| | D on FL1; on E60's slope | +0.0267 [−0.0506, +0.1041]; +0.0261 [−0.0459, +0.0982] | P +0.1649 above; P +0.1672 above |
| RA3, the ladder slope | R | **+0.0093 W a bit [+0.0060, +0.0125]** | P 0.1277 above; every arm above |
| | D on FL1; on E60's slope | +0.0097 [+0.0028, +0.0166]; +0.0101 [+0.0032, +0.0169] | P above on each |
| RA4, E180-A's statistic | R | +0.3586 W [+0.1333, +0.5838] | P +2.2938 above; every arm above |
| RA5, the anchors against the catalogue's 26 Sep rows | D: const − zeros; random − zeros | +0.0675 [−0.0393, +0.1742]; +8.4546 W [+8.3417, +8.5675] | the catalogue +0.2029 above; +8.6953 above |
| | R: const − zeros; random − zeros | +0.1110 [−0.0275, +0.2495]; +6.8767 W [+6.7323, +7.0212] | +0.0297 inside; +6.7552 inside |

- **The die rise per burst** (A1 section 4.3): median 0.870 °C; more than 0.5 °C off it, only `fadd.ps/random` (the heaviest kind).
- **Each burst's rate** (the timing must not depend on the number, E180.md section 5): the 22 fadd.ps kinds 4.5871-4.5930 × 10^11
  instructions a second (0.13% apart), fadd.pi 4.563-4.568, fadd.ps.acc 4.509-4.515, fadd.pi.acc 4.586 × 10^11. The smoke's gate read the
  four smoke configurations' rates within 3% (4.5252-4.6282 × 10^11).
- **Each kind's D above its mode's zeros, against P** (`scored-e180.json` `reported.kinds`; the mean over 6 passes, W): the ladder's top,
  R3max (thirty result 1-bits) +0.326 (P +4.947); R3 k = 24 / 20 / 16 / 12 / 8 / 4: +0.189 / +0.254 / +0.209 / +0.206 / +0.158 / +0.125;
  0.5s +0.096 (P +1.154); 1.5s +0.102 (P +0.330); const +0.068 (P +0.165); 2s −0.024; 3s +0.094; 4s +0.022; 5s +0.049; 6s +0.064; 7s +0.060;
  8s +0.084 (P +0.495); −1 −0.001; −4 +0.060; −5 +0.059; fadd.ps random +8.455 (P +8.726). fadd.pi: random +3.171 (P +9.639, F +3.186), the
  eight R4 kinds −0.102 to +0.373. fadd.ps.acc: 4s +0.382, 5s +0.696, const +0.383 (P +3.293, +3.281, +3.293). fadd.pi.acc: int 1 / 4 / 5: +0.239 /
  +0.269 / +0.348 (P +1.199 / +1.199 / +1.816).
- **The pairs of E180.md section 4** (differences of the kinds' means above): 0.5s − 1.5s −0.006 (P +0.825); const − 2s +0.091 (P −0.165);
  fadd.ps 5s − fadd.pi 5s (each above its zeros) −0.018 (P +0.495; E180-X's statistic); fadd.ps.acc 5s − 4s +0.314 (P −0.012, F +0.132);
  fadd.pi.acc 5 − 4 +0.080. None is a verdict.
- **Every accumulating kind's reading is marked "walk verified by disassembly"** (A1-7's per-kind mark, note 2 section 4).

### Not read here

- **october-forecast-model's arm** (dated notes M1 and M2): REPORTED, never a verdict. M2's reader, `arm_m1_e180.py read`, runs after this
  commit on this directory's `reduced-e180-v3.json` and `scored-e180.json`, and its table goes in a dated note beside this README.
- **A data verifier** of this directory and its verdicts, then a fix pass, follow this commit.

## The readings, labelled

- **Blind, registered:** every verdict of § The answer, the owner's sentence, A1-1's footing flag, A1-5's band reading and A1-7's walk
  labels; each forecast was committed before the session's opening config read (12:54:50 PST).
- **Reported, registered before the data:** RA1-RA5, the die rise, each kind's D against its forecasts, the rates, the pairs (A1 section 4,
  E180.md section 5).
- **Post hoc** (written after the data, deciding nothing): the price conversions in fJ above, the ratios to P (1/17 on the ladder; 0.16 on his
  pair; 0.12 on E180-A), and the per-pass spreads (his pair's sd over passes 0.074 W, half-width 0.077 W, against A1's registered-level
  0.103 W; the first pass's +0.171 W is the one far from the others).

## Registered before any data, and what the box ran

Every E180 text below was committed before the session's opening config read on the card, one ancestry chain in the lab repository
(Fri 6 Nov 2026, PST): the registration `4dc5035f` (01:22:09), the kit `c92f627b` (01:40:21), dated note A1 `879197e3` (03:34:44), the kit's
dated note 1 with kit v2 `90a1312f` (03:54:42), the kit's dated note 2 `1e19a451` (06:16:32: the desk walk v2, the build record collected,
reduce v3 and score v3, box steps 2 and 11 as v3; no box file changed), dated note M1 `b38d09e3` (09:49:37: october-forecast-model's fadd.ps
one-number arm, reported) and dated note M2 `2b32db9d` (10:42:13: its reader `arm_m1_e180.py`). The readiness critic (Q146(f)) read E180
READY WITH GAPS at about 04:50 PST; the kit verifier of A1 and kit v2 (Q146(g)) held it with fixes, all answered by note 2. No verifier read
note 2 before the session (it changed no box file). `git log --all` showed no `docs/reports/data/*e180*` before this commit.

The owner's go came at about 09:20 PST with the lab boxes' fresh network approvals; the window, recorded by each of the day's kits' step 1
(`rb/s02_window_e180.sh` first) at 09:33:05: no session starts after 15:30 PST and every run ends by 17:00 PST. E180 ran after E178's step 22 (12:31:22) and E178's data commit (`f7820e70`,
12:42:52), by the kit's dated note 2 runbook (`KIT.md.dated-note-2.md` section 6: box step 2 as v3, steps 5, 6 and 8-10 as note 1's v2, step
11 as v3), never KIT.md's v1 steps, each step with the card day's one runbook output directory and lock file:

| box step | when (PST) | what it read |
|---|---|---|
| 2, `rb/s03_desk_e180_v3.sh` | 12:52:57-12:53:01 | pulled (`f7820e70` = origin/main); HEAD descends from `879197e3` (A1), and from `1e19a451`, M1 and M2; E180's paths clean; the five lists 71/55/41/90/96 OK, and M1's 6 and M2's 30; harness v2 rebuilt; the plan and the forecasts re-made; HARNESS OK 86 (v2); october-forecast-model's freeze present; 0 E180 data commits |
| 3, the post | 12:53:22-12:53:29 | the day's one post already carried E180's clause, set at E178's end: read back, not edited |
| 4, `s05_look_k6.sh aifoundry3` | 12:53:36-12:53:37, and again 12:54:48-12:54:49 | FREE: et-who's "No process holds an ET-SoC-1 device node or card lock" (0 holder lines), no device process of ours or of another account; 12 terminals logged in (an idle login does not block, the owner's ruling of 1 November 2026); up 10 days 22 h |
| 5, `rb/s07_a3_sync_e180_v2.sh` | 12:53:42-12:53:43 | every file of `harness-e180-v2.json`, 61 files in 6 paths, after `check_e180_v2.py harness` read them at the harness's sha256 (HARNESS OK 86) |
| 6, `rb/s08_a3_build_e180_v2.sh` start, wait | 12:53:48-12:53:51; 12:53:56-12:53:57 | the job 12:53:49-12:53:53, rc 0: `build_e180.sh` BUILD OK (the first compile of modes 261 and 262 on a box); the walk's v1 line (above); HARNESS OK 88 with the binaries; `preflight_e180_v2.sh` GO (32 send sites, 0 disallowed) |
| 7, `s09_a3_reads_k6.sh` | 12:54:18-12:54:19 | `et-lab-manifest`; the config through the guard: TDP 0 W / 65 °C / max_power / 600 MHz / 523 mV; et-who clean |
| 8, `rb/s10_a3_dry_e180_v2.sh` start, wait | 12:54:24-12:54:26; 12:54:33-12:54:34 | the dry job rc 0: pass 18010's 47 runs, the smoke's 4, the stop-path test (both stops fired, no launch), the start gate refusing with 8 ([`logs/session-dry.log`](logs/session-dry.log)) |
| 9, `rb/s11_a3_session_e180_v2.sh FULL` | 12:54:49-12:54:55 | launched detached at 12:54:55 (both v2 jobs ended rc 0 today; no session or dry pass of ours running) |
| 10, `rb/s20_wait_e180_v2.sh` | 12:55:05-13:36:57, five bounded calls | four said "call again", the fifth read the session end |
| 11, the release, then `rb/s22_collect_e180_v3.sh` | 13:37:12-13:39:07; 13:39:14-13:39:21 | the post's release; then the three copies back (13:39:15-13:39:16), `collect_e180_v3.sh` at nice 10, the gates (below) |

The session ([`logs/session.log`](logs/session.log), [`logs/queue.out`](logs/queue.out)): T0 and the opening config read 12:54:50; the
harness check with the binaries and the device-command preflight (GO) first; the stop-path test 18002 12:54:51-12:54:54; the smoke 18001
12:54:55-12:55:33 (4 of 4 bursts) and its gate; the six passes 12:55:34-13:36:42, each 47 of 47 bursts, 10 s apart; the queue done at T0 +
2,522 s; the closing config read and the session end 13:36:52.

## Who checked it

Step 22 v3 ran its gates in order, each passing: the three copies back (the passes, smoke and stop-path test; the session logs with the
box's walk line; the build record and the box's kernel listing); the stop-path test checked to have recorded no launch; `collect_e180_v3.sh`
(`build_record_e180.py`, `check_elf_e180_v2.py` 3 PASS of 3, `reduce_e180_v3.py` 6 kept passes and none unreadable, `score_e180_v3.py`); the
desk-path gate (`nopath: 89 files read ... 0 hit(s): CLEAN`); and last the login check over every directory (`scrub_tree_e178.py --check`:
`OK (74 files in 12 directories read, 0 left)`). No data verifier has read this directory yet: the card day's verifier and fix pass for
E180 follow its data commit.

## Device commands sent

As registered (E180.md section 7, "Device commands"; kit v2's block): every telemetry call through E128's guard (`ettelem config` with no
argument, `ettelem sample --seconds --every-ms` and nothing else): `ettelem config` at the session's start and end; `ettelem sample` at 10 Hz
in every block, and for the block's 1 s clock and die reads; and once before the session, box step 7's read (`s09_a3_reads_k6.sh`:
`ettelem config` through the same guard, under card 0's lock). Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all
READs**, the two in bold PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows. **Never sent**: the statistics reset
(`since_reset_ms` −1 in every sample), any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or clock
set, any reset, and `dev_mngt_service` (the block's drain is a refusal). The enercat host opens the card through the runtime only (kernel
load, copies, launches). The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened: **GO**, 32 send
sites, 0 disallowed ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)); the same at step 6. No power cycle, and nothing near card 0's
75 W alarm (the board's highest live reading 44.70 W).

## Card and post

`et-who` at the looks (12:53:37 and 12:54:49 PST), at box step 7's read (12:54:19) and at the session's start (12:54:50) and end (13:36:52):
no process held a device node or card lock, and no other account ran a device process. D1's check before every run (kit v2) let all 286
runs go (282 in the passes and 4 in the smoke, every one rc 0), and no others-present line was written. 12 terminals were logged in, as at the card day's claim; an idle login does not block, and no login is
named in any file. One session of ours ran on aifoundry3 at a time: E178's ended at 12:18:36 and its copy-back at 12:21:08, before this
run's look; E180 was the day's last run. Nothing ran on aifoundry1 or aifoundry2.

Fri 6 Nov's one `#community-lab` post is message `1568318213618540726`, created by the card day's claim at 09:36:40 PST. Before this run it
read `<ai> **Claude says:** using aifoundry3 for 1.5 h, until ~13:49 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`
(E180's clause, set at E178's end, 12:19:16), read back at 12:53:29 with no edit. **At this run's end, 13:37:28 PST**, under the Discord
lock and `EXPECT_TEXT`, dry-run, saved and read back (from the edit box, and from a fresh plan at 13:39:07: one post that day, its text
equal to the intended one, released), ` — released` was appended, every other word kept:
`<ai> **Claude says:** using aifoundry3 for 1.5 h, until ~13:49 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released`.
Thu 5 Nov's post and every earlier day's were not touched.

## Privacy and the public-text scan (before the commit)

- **Logins.** Step 22 v3's last gate read every directory of the collection with `scrub_tree_e178.py --check` (0 left). Before this commit
  the final bytes were read again: `scrub_tree_e178.py --check` over this directory (74 files in 12 directories, 0 left); E164's
  `scrub_etwho_e164.py --check` (unchanged; `--owner` the box login of this repository's owner) in every directory of this one and of a
  scratch copy of the text inside its 15 `.gz` files (29 directories, every one rc 0); and a search of both for lib.sh's and D1's "others
  present" line and run_e78's "another user on this card" stop line (0 lines). The session log's et-who readings say "No process holds an
  ET-SoC-1 device node or card lock". `logs/build-e180.json` withholds the toolchain listing's owner and group (note 2 section 2).
- **The public-text scan** (`tools/timeline/sanitize_extracts.py`'s fixed list, plus the private-network, Mac-home, scratch and e-mail
  patterns) over every text file and the text inside every `.gz` of this directory: 74 text files and 15 `.gz` files, 8 matches, every one
  the owner's own box home path, the reviewed class E166's, E171's, E176's, E178's and E181's committed data carry; no other match. The
  runbook's desk-path gate (`nopath_q142s.py`) read the final directory too (this README and `SHA256SUMS` among its files), 0 hits. This README
  and `SHA256SUMS` were scanned on their own afterwards. The lab's private name table is absent on the Intel, so names were checked against
  the fixed list only (a stated coverage limit).

## Files

All files of step 22 v3's collection and score are here as step 22 left them (`diff -r` against `build/e180-out/`: equal), plus this README
and [`SHA256SUMS`](SHA256SUMS), which pins every file but this README and itself.

| file | what |
|---|---|
| `scored-e180.json`, `scored-e180.md` | the scorer v3's output: every registered rule (v1's code on v1's D), A1's rules and reported arms, A1-7's walk from the desk, the per-kind marks |
| `reduced-e180-v3.json` | the reduction v3 (v1's D per kind and pass, v2's per-burst readings, the v3 record: nothing set aside) |
| `raw/e180/p18010`-`p18015` | the passes as the box wrote them (`telemetry.jsonl.gz`, `runs.jsonl.gz`, `run.log`, `runner.out`, `configs.json`, `pass.json`, `check.json`, `block.json`, `code.sha256`) |
| `raw/e180-smoke/p18001`, `raw/e180-stoptest/p18002` | the smoke and the stop-path test (its board and die `stoptest.json` and outputs) |
| `logs/` | the session's own logs: `session.log`, `queue.out`, `session.out`, the two session config reads with their times and stderr, `dmcmd-preflight.txt`, `session-dry.log` (step 8's dry start gate); the box's walk line `elfcheck-e180.txt`; the desk walk `elfcheck-e180-v2.txt`; the build record `build-e180.json`; the box's kernel listing `e180-kernel-dis.txt` (19,185 instructions, sha256 `6310b355…`) |

## What it does to predicting power

- **The mechanism's direction holds blind, its price does not.** The result's 1-bits cost power (E180-L's interval above 0) and P orders
  the 21 one-number kinds right (E180-R, rho +0.800), but at about 0.0097 W a bit, 1/17 of P's 0.1649 and half of the lowest arm's (A,
  0.0192). Every arm prices the write-back's bit above the card. P was calibrated on the catalogue's random row, which this session
  reproduces to 3% (+8.45 W against +8.70); what fails is carrying the random row's price per flip to a one-number kind. E178 found the same
  direction for the int8 TensorFMA (M10 about 2.7-3.5 times high); the vector add's write-back is overpriced far more.
- **His pair, 5s against 4s, is below this card's resolution at the measured price** (about 0.01 W against ±0.08 W). The question needs the
  ladder's form: it is the ladder, read to ±0.007 W a bit, that answers "do the result's bits cost power" (yes, about 21 fJ a bit an
  instruction). The net minion rail, where the write-back is, reads a positive slope too, and more finely (+0.0093 W a bit [+0.0060,
  +0.0125], reported).
- **What holds for a model:** the operand's held bits cost nothing (E180-O NULL, ±0.012 W a bit), the integer add's held write-back is flat
  within ±0.30 W (E180-I NULL), equal results read equal (E180-E PASS twice), and a running sum costs more (E180-A POSITIVE) though at 0.12 of
  P and below the harts' offset band. **What does not:** every per-flip price for the one-number write-back (E180-L), P's +0.165 W for his
  pair (E180-H SIZE FAIL HIGH), the float add's +0.5 W over the integer add (E180-X NOT RESOLVED, P above), and P's +2.96 W for the running
  sum (E180-A SIZE FAIL HIGH).
- **For the next model:** a blind one-number fadd.ps price near 0.0097 W per result bit on aifoundry3 at 600 MHz (95% 0.0027-0.0167; about
  0.85 fJ a named flip), one session; the next E180-type test reads a ladder, not a pair.
- **Heat:** nothing is read or scored here. The die's live reading stayed at 50-57 °C, and a burst's mean rise was 0.87 °C.
