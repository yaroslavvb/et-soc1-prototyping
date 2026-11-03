# E155: from one A row to three, int8's no-issue floor rises 0.31 ± 0.10 W, inside the frozen band of the walk counted in address-bit toggles and outside the new-address count's (by 0.017 W) and per cycle's (F1a WALK, F1b TOGGLES); the toggle count predicted the three-row floor to 0.012 W; the per-op difference between the formats is 8 ± 27 pJ, not bounded below 30 pJ (F3 INCONCLUSIVE) (Q139, aifoundry1 card 1, 600 MHz, nine passes)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 11, int8's
no-issue floor** ("int8 zeros' extra 0.61 W"), and **rank 10 of Q138's final critic**, the complaint this answers: "int8's no-issue floor by shape: which
count the per-row part follows (address-bit toggles against new-address reads), the per-op premise, and what stays at one row", with its next test "a
registered three-row arm with K = 8 partners in both formats (avoid four rows, errata type D), both counts' predictions frozen. Rule: the rise from one
row to three within the frozen count's band, and the per-op difference between the formats bounded below 30 pJ." It builds on
[E148](../2026-11-02-e148-int8-excess/README.md) (this card, the night before: two rows put back 0.16 ± 0.10 W; at that session's own scale the walk
counted in new-address reads over-predicted it twofold and the walk counted in address-bit toggles fitted, a count chosen after the data),
[E129](../2026-11-02-e129-int8-noissue/README.md) and [E109](../2026-11-01-e109-int8-zeros/README.md) (the K = 8 construction of per-op work) and
[Q136(c)](../2026-11-02-q136c-tima-bench/README.md) (the TIMA bench).*

*Tue 3 Nov 2026 (week 45), Q139, lane a1c1-e155-int8-floor. Pre-registered in [`tools/claims-v3/e155/README.md`](../../../../tools/claims-v3/e155/README.md)
with [`predictions-e155.json`](../../../../tools/claims-v3/e155/predictions-e155.json), committed as **`82b5af8d`** and pushed by `commit_lab.sh` at
04:28:26 PST, before the claim (04:30:0x) and before any device opened (04:30:48). **aifoundry1 card 1** (`V3_DEVICE=1`, its own lock), release 1.4.0
(BL1 and BL2 0.22.0), the first session on the card that day (it had idled since E148 ended at 22:45:56). `ettelem config` was read 24 times under
card 1's lock with `timeout 10`, through E128's allow-list (the session's start, 04:30:48, and end, 05:07:01, and both ends of the stop-path test, the
smoke and every pass): **TDP 65 W, threshold 65 °C, 600 MHz, 499 mV in every read** (power state `low_power` 6 times, `managed_power` 18). **Nothing
was set and no WRITE was sent** (§ Device commands sent; `since_reset_ms` −1 in all 20,534 samples). **Card session 04:30:48–05:07:01 PST, 36.2
card-minutes of the 40 allowed**: the stop-path test 15502, the smoke 15501 and **nine passes, 15510–15518 (215–239 s each), all kept**. The card was
claimed at 04:30 by rewriting the day's one card post in `#community-lab` (message `1567153765390487573`) and released at 05:07 by rewriting it again
(§ How it ran).*

**In plain words.** With nothing to multiply, an int8 matmul loop on this chip still draws more than the same loop in fp32, and how much depends on
the shape of the operation: 0.93 W more at one row of A, 1.24 W at three rows, 1.63 W at sixteen (E148). Last night's two-row run left open what the
part that grows with rows follows: how often the accumulator memory's read address changes, or how many of its address bits flip. At three rows the
two counts predict different rises, and both predictions were frozen before the run. **The rise was 0.31 W: inside the band the bit-flip count
predicted (0.33–0.42 W) and below the address-change count's (0.43–0.55 W), and the bit-flip count, with last night's one-row level, predicted the
three-row floor to 0.012 W.** That reading rests on the two formats spending the same energy on each operation's fixed work. At three rows they do
not run equally many operations a second, so it was measured: about 90 pJ an operation in each, the same to within −19 to +35 pJ, not the ±30 pJ
the test asked for, and a difference at those limits could move the rise by −0.15 to +0.08 W. A check that needs no such assumption, int8 run at one
row's exact schedule with the walk switched on, agrees (post hoc).

## Results

**All nine passes kept on the registered primary** (E78's `reduce_e78.py` unchanged through `reduce_e155.py`: leakage frozen at 0.2414 W/°C, card 1's
launch-gap dips removed, E78's run and pass gates, card 1's 65/65 config gate): 126 runs, none failing a gate, a median of two heats a launch. The
relaxed reduction keeps the same nine. ([`scored.json`](scored.json) › `n_passes`, `which_reduction_scores` = "primary"; [`e155.json`](e155.json) ›
`passes_set_aside` = [])

1. **Three A rows put back D31 = N3 − N1 = +0.311 ± 0.102 W** (95% +0.208 to +0.413; nine passes, paired inside each). **F1a reads WALK and F1b
   TOGGLES**: D31's interval overlaps the frozen band of the walk counted in address-bit toggles (Wt, +0.327 to +0.419) and of the A path (T, +0.222 to
   +0.288), and excludes the walk counted in new-address reads (Wn, +0.430 to +0.549) and per cycle (C, +0.123 to +0.162). **Wn's exclusion is by
   0.017 W** (D31's upper end 0.413 against 0.430); in the dips-kept arm by 0.002 W, in the leakage-`auto` arm by 0.023 W; C's by 0.046 W. Every arm
   reads the same verdicts. (`scored.json` › `rules.F1`)
2. **The frozen predictions against the three-row shape, which no model had seen** (`posthoc/posthoc.txt` section 4 prints these from `scored.json`):

   | predictor, frozen before the run | D31 predicted | D31 error | N3 from E148's N1 (0.884 W) | **N3 error** |
   |---|---:|---:|---:|---:|
   | null: a third row changes nothing | 0 | +0.311 W | 0.884 | +0.361 W |
   | null plus the shared per-op term | +0.085 | +0.226 | 0.969 | +0.276 |
   | per cycle (C) | +0.142 | +0.168 | 1.026 | +0.218 |
   | the A path (T; excluded as the sole carrier by E148's W2) | +0.255 | +0.056 | 1.138 | +0.106 |
   | **the walk in address-bit toggles (Wt)** | **+0.373** | **−0.062** | **1.256** | **−0.012** |
   | E148's two-term solve (75.5 fJ a new-address read, 3.43 pJ a 64-bit A read) | +0.442 | −0.131 | 1.326 | −0.081 |
   | the walk in new-address reads (Wn; E148's registered count) | +0.490 | −0.179 | 1.373 | −0.129 |

   Measured: N3 = **1.244 ± 0.083 W**, D31 = +0.311 ± 0.102 W; each error carries the measurement's interval. (`scored.json` ›
   `reported.N3_out_of_sample`)
3. **The per-op premise, measured at three rows for the first time** (F3 INCONCLUSIVE). E109's construction with the K = 8 partners gives **e = 90.2 ±
   15.0 pJ an op in fp32 and 86.4 ± 15.6 pJ in int8** (E129 at sixteen rows: 81 ± 43 and 77 ± 92), a raw difference **Δe₃ = −3.9 ± 26.6 pJ**. With the
   frozen allowance for int8's count changes between the partner and the arm (−12.0 ± 4.5 pJ) it is **Δe₃c = +8.2 pJ, interval −18.8 to +35.1 pJ**:
   inside ±35 but not inside ±30 pJ, so the premise is not bounded at the registered line. Entering D31 as −4.30 × 10⁹ × Δe (int8's op-rate change
   from one row to three), that interval allows **−0.151 to +0.081 W** of D31: at its upper end the new-address count's band would be reached, at its
   centre (−0.035 W) the reading moves toward the toggle count's point. (`scored.json` › `rules.F3`; § What this cannot say)
4. **The silicon keeps the RTL's schedule at three rows and at K = 8 there** (R6 PASS ×6). Every arm's cycles per op equal the frozen prediction, the
   bench's plus E109's 7.75: **`m0r3` 128.0 (fp32) and 110.0 (int8)**, **`m0r3k8` 72.0 and 62.0**, `m0r1` 62.0 and 62.0, schedules no card had run but
   one row's. The smoke read the same. (`scored.json` › `rules.R6`; [`logs/session.log`](logs/session.log), the smoke lines)
5. **What stays at one row replicates** (T1 PASS): **N1 = 0.934 ± 0.077 W** against E148's 0.884 ± 0.077 and E129's 0.865 ± 0.357 on this card.
   (`scored.json` › `rules.T1`, `stats.N1`)
6. **Post hoc, deciding nothing** ([`posthoc/posthoc.txt`](posthoc/posthoc.txt)). (a) int8's K = 8 arm runs one row's exact schedule (62 cycles, the
   same TIMA control bits, TenTMP staging and TenC read count an op) with the walk on, so **Q31k = S(`m0r3k8.int8`) − S(`m0r1.int8`)** needs no per-op
   premise: raw +0.036 ± 0.065 W, and **+0.220 ± 0.118 W once B's halved traffic is added back** at this session's price, 0.146 ± 0.077 pJ a TenB write
   (fp32's three arms solved per pass for e and that price). The frozen walk parts are Wt +0.255 [0.227, 0.284] and Wn +0.359 [0.319, 0.399]: the
   toggle count's residual is −0.035 W, the new-address count's −0.139 W. (b) Priced on D31 less this session's shared term (0.100 ± 0.008 W), the
   rise is **36.9 ± 17.0 fJ an address-bit toggle** against E148's sixteen-row 50.5 (consistent) or **49.3 ± 22.7 fJ a new-address read** against
   94.8 (excluded). (c) D31 / D21 = 1.95 against the counts' 1.71 (toggles) and 1.28 (new-address), before the shared terms.

**What it changes.** Item 11 narrows again. **The per-row part follows the walk counted in address-bit toggles** on two shapes now: E148's two rows
(post hoc, −0.009 W) and E155's three rows (registered: F1b TOGGLES, the new-address count excluded by 0.017 W, under the per-op premise; post hoc
by Q31k without it). The A path's band also holds D31 at three rows, but E148's W2 excluded it as the sole carrier at two rows, and no single count
other than the toggle count fits both shapes. **The premise** is measured at three rows (−19 to +35 pJ), 2.4 times tighter than E129's ±63 pJ, but
not inside the ±30 pJ the critic asked for. **What stays at one row** (0.93 W) is replicated a third time; what it is (per-cycle work or one row's A
staging) no arm here separates.

## What it does to predicting power and heat

**The term measured and tested:** int8's no-issue floor as a function of shape, N(R) ≈ N1 + p_tog × (TenC read-address bits that change a second) +
E_op × (the formats' op-rate difference). Before E155 the per-row count was open (E148: the registered new-address count failed at its own scale,
the toggle count fitted post hoc). **Out of sample, on a shape no model was fitted on (three A rows, both predictions frozen first): the toggle count
predicts N3 to −0.012 W from E148's N1 (1 % of 1.24 W) and the rise D31 to −0.062 W, against +0.311 W (D31) and +0.361 W (N3) for the null "a third
row changes nothing", −0.179 / −0.129 W for E148's registered count and −0.131 / −0.081 W for E148's two-term solve.** So the rise's error falls from
0.31 W (the null) or 0.18 W (the registered count) to 0.06 W, inside the measurement's ±0.10 W. Its price, 50.5 fJ an address-bit toggle at sixteen
rows (E148) and 36.9 ± 17.0 fJ at three (post hoc), lets a model carry the floor to any int8 shape from the bench's toggle count. The shared per-op
term (fp32's 108.7 pJ an op frozen, 127.9 ± 10.7 measured here) is a correction of 0.085–0.100 W at three rows; the per-op difference between the
formats is not yet bounded below 30 pJ. **Heat** follows power through card 1's die rise per board watt (M7's H2, 0.1151 °C/W): the 0.06 W error is
0.007 °C and the whole rise 0.04 °C, below the 4.5 s readout, so no heat term changes.

## The arms (primary reduction)

D is over the format's zeros (interpolated between the pass's three zeros anchors) and S over the idle bracket, ± 95% over 9 passes (t 2.306).
"Cycles" is the median over the kept runs. Source: `e155.json` › `items`, `per_pass`; [`readme-numbers.txt`](readme-numbers.txt).

| item | cycles | ops/s (10⁹) | D, W | S, W |
|---|---|---|---|---|
| `fp32.zeros` | 546.001 | 1.1208 | 0 | +1.598 ± 0.028 |
| `int8.zeros` | 318.001 | 1.9249 | 0 | +2.200 ± 0.033 |
| `anchor_pi` | 546.001 | 1.1208 | +8.215 ± 0.029 | +9.794 ± 0.026 |
| `m0r1.fp32.zeros` | 62.0 | 9.8656 | −0.404 ± 0.051 | +1.220 ± 0.049 |
| `m0r1.int8.zeros` | 62.0 | 9.8660 | −0.052 ± 0.028 | +2.153 ± 0.058 |
| **`m0r3.fp32.zeros`** | **128.0** | 4.7811 | −1.044 ± 0.041 | **+0.569 ± 0.046** |
| **`m0r3.int8.zeros`** | **110.0** | 5.5644 | −0.372 ± 0.056 | **+1.814 ± 0.058** |
| **`m0r3k8.fp32.zeros`** | **72.0** | 8.4966 | −0.709 ± 0.055 | +0.886 ± 0.052 |
| **`m0r3k8.int8.zeros`** | **62.0** | 9.8652 | −0.000 ± 0.045 | +2.189 ± 0.069 |

Idle 33.03 W. From one row to three both formats' levels fall with the op rate and B's traffic, fp32's by 0.651 ± 0.054 W and int8's by only 0.340 ±
0.078 W; int8 alone adds the walk back. Halving K at three rows raises both again (fp32 +0.316 ± 0.081, int8 +0.376 ± 0.099 W). (`scored.json` ›
`stats.r3_over_r1_*`, `stats.r3k8_over_r3_*`)

## The registered rules against the data

`scored.json` is `score_e155.py`'s output with `predictions-e155.json` on the primary, chosen by the set-aside rule over the relaxed reduction.

| rule | registered line | **E155 (primary, 9 passes)** | dips kept (8 passes) | leakage `auto` (fitted) | relaxed |
|---|---|---|---|---|---|
| **F1** (primary) | D31's 95% interval against the frozen bands Wn, Wt, T, C | **F1a WALK; F1b TOGGLES** (+0.311 ± 0.102; Wt and T consistent, Wn and C excluded) | WALK; TOGGLES (+0.309 ± 0.119) | WALK; TOGGLES (+0.311 ± 0.096) | WALK; TOGGLES |
| **F3** | Δe₃c's interval (H = √(h² + 4.5²)) inside ±30 pJ | **INCONCLUSIVE** (+8.2; −18.8 to +35.1) | INCONCLUSIVE (+5.7; −24.8 to +36.2) | INCONCLUSIVE (+6.3; −20.0 to +32.7) | INCONCLUSIVE |
| R6 | \|measured − predicted\| ≤ 2 cycles | **PASS ×6** (every difference 0) | PASS ×6 | PASS ×6 | PASS ×6 |
| T1 | N1 within 0.5 W of E148's 0.884 | **PASS** (0.934) | PASS | PASS | PASS |

**No verdict moves with an arm.** The dips-kept reduction sets aside pass 15518 (π drifts +0.694 W against its 0.60 W gate with the meter's dips
kept); the primary and the relaxed keep all nine.

## Registered against what happened

| | registered | happened |
|---|---|---|
| freeze | committed and pushed before the claim and the first launch | `82b5af8d` pushed 04:28:26 PST; claim 04:30; first device process 04:30:48 (the opening config read) |
| desk | the bench and its identity checks; the predictions; the self-test; the preflight; `bash -n`; the reducer's mechanical run. On the box: `check_e155.py`, the preflight, `bash -n`, a stub queue, `V3_DRY` of the stop test, smoke and pass 15510 | [`selftest.txt`](../../../../tools/claims-v3/e155/selftest.txt) PASS (A–C); [`dmcmd-audit.txt`](../../../../tools/claims-v3/e155/dmcmd-audit.txt) GO; the box's checks 04:26:06–04:27:29 PST ([`logs/desk/`](logs/desk/)) |
| stop test | before the smoke: the die, board, watcher and stale-line stops each exit 6 on a live sample, no launch | 04:30:49–04:31:03: die stop on a sample read 0.044 s after it was taken, board 0.044 s, watcher 0.079 s, stale 0.077 s; rc 6 four times ([`aifoundry1-c1/e155-stoptest/p15502/`](aifoundry1-c1/e155-stoptest/p15502/)) |
| smoke | eight items, 2 s runs; E109's gate | 04:31:04–04:31:51; every item 6 launch records, all `ok`: SMOKE-GATE PASS; `m0r3` 128.0 / 110.0 and `m0r3k8` 72.0 / 62.0 cycles |
| passes | 15510–15519 as the budget allows | **nine**, 215–239 s each (rc 0); the budget rule stopped before 15519 (05:07:01, T0 + 2,174 s; it would have ended at T0 + 2,413 s against T0 + 2,250 s) |
| kept | the primary carries if ≥ 3; else the relaxed one | **9 of 9** by E78's gates; the relaxed reduction keeps the same 9 |
| runs | 14 a pass | 126 of 126 ran and all are kept; a median of 2 heats a launch (31–39 heater launches a pass) |
| stops | `build/e155/STOP`; board ≥ 66 W, a minion-shire reading ≥ 72 °C or a line ≥ 1.5 s old on a live sample (before every launch, every 0.1 s while waiting, and by the in-run watcher); run_e78's `--max-c 72`; another user's device process or this card's lock | none fired. In all 20,534 samples: board at most **59.48 W** (stop 66), the hottest-shire field 65 °C throughout (its latch; stop 72), the shires' mean 49–61 °C, 600 MHz, `since_reset_ms` −1 ([`telemetry-max.json`](telemetry-max.json)); no line was read 1.5 s stale |
| budget | at most 40 card-minutes, first config read to last; no session after 10:30 PST; passes end by 11:20 PST | **36.2** (04:30:48–05:07:01); claim to release about 37 min (04:30–05:07) |
| config | read at both ends, never set | TDP 65 W, 65 °C, 600 MHz, 499 mV in all 24 reads |

## Departures (dated)

- **Tue 3 Nov 2026, the passes ran 2.5 times faster than the queue's first estimate.** The registration projected 600 s a pass from E129's cool
  morning (522–650 s). This card's die started at 49 °C and settled at 53–61 °C with a median of two heats a launch, and the passes took 215–239 s;
  the queue's budget rule, unchanged, started nine. Recorded, not amended: no rule depended on the number of passes beyond the minimum of three.
- **The day's post's plan read lagged at the release**, as in E148: `delete_msg.mjs --plan` still showed the aifoundry3 lane's clause after that lane
  had dropped it, so `edit_replace.mjs` with `EXPECT_TEXT` refused (exit 7) as its rule says; the release text was rebuilt from what the edit box held
  (this card's clause alone), ` — released` appended, and saved (§ How it ran).

## How it ran

04:26:06–04:27:29 PST, before the commit, on the box with no device opened: Python 3.12.3; `check_e155.py` HARNESS OK (25 files: E148's 20 reused files
and the 5 binaries); the preflight GO; every script parsed; the queue's budget rule on a 1 s stub; `V3_DRY` of the stop test, the smoke and pass 15510
([`logs/desk/`](logs/desk/)). `et-who`: no process held a device node or card lock. 04:28:26 the registration was pushed (`82b5af8d`). 04:30 the claim,
under the discord lock, after a fresh `et-who`: the day's one card post, which the aifoundry3 lane had posted at 04:29 as
`<ai> **Claude says:** using aifoundry3 for 1 h, until ~05:29 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, was rewritten to
`<ai> **Claude says:** using aifoundry3 for 1 h, until ~05:29 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>); using aifoundry1 card 1 for 1 h, until ~05:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`
(`edit_replace.mjs` with `EXPECT_TEXT`, dry run, save, read back). 04:30:47 `session_e155.sh` started detached on the box (`setsid nohup`, T0 = the
launch): the 10:30 gate; `check_e155.py` (HARNESS OK); the preflight (GO); `et-who` (no holder); the opening config read; the stop-path test 15502;
the smoke 15501 and its gate; `queue_e155.sh`; the closing config read at 05:07:01; `et-who` (no holder). The other lab user's idle logins were
present throughout; no other user's process, device node or card lock was seen (E78's departure D1 for `aifoundry1-c*`).

Each pass ran E78's two burn-in runs of π, then 14 registered runs: π first and last, each format's zeros once in each of three segments, and E155's six
arms dealt round-robin with seed `E155|aifoundry1-c1|<pass>`. Each run launched at a 58 °C die reading after a 59 °C preheat, with 2 s quiet and 4 s
FMA runs on all 1,024 minions. The waits were bounded `ssh … 'bash -s'` calls that read the session's and the queue's log lines only; nothing was
copied off the box until the session had ended.

05:07 the release: the post then read (in its edit box) `<ai> **Claude says:** using aifoundry1 card 1 for 1 h, until ~05:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`,
the aifoundry3 clause already dropped by its lane; this card was the last held, so it was rewritten to
`<ai> **Claude says:** using aifoundry1 card 1 for 1 h, until ~05:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released`
and read back. The data were then collected to the Intel ([`collect_e155.sh`](../../../../tools/claims-v3/e155/collect_e155.sh), the box's desk checks
into [`logs/desk/`](logs/desk/)), reduced and scored with [`pipeline_e155.sh`](../../../../tools/claims-v3/e155/pipeline_e155.sh).

## Device commands sent

Every command the run sent to card 1, classified at registration from the source of its running build: release 1.4.0, BL1 and BL2 0.22.0,
et-platform **`836a4ab`** (the version-matched revision of Q136(w)'s table and of E148's audit of the same command set). Q136(w)'s checker on every file
the session runs read **GO: 32 send sites, 0 disallowed, no WRITE allowed**, at the desk
([`dmcmd-audit.txt`](../../../../tools/claims-v3/e155/dmcmd-audit.txt)) and on the box before the first device opened
([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt), 04:30:48 PST). **The run sent no WRITE** (`since_reset_ms` −1 in every sample).

| # | sent by | command (id) | class (BL2 0.22.0, `836a4ab`, under `device-bootloaders/src/ServiceProcessorBL2/`) |
|---|---|---|---|
| 1 | `ettelem config` (session start and end, each block's start and end) | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25) | READ: `thermal_power_monitor.c:339` → `thermal_pwr_mgmt.c:613`, a copy from SP RAM |
| 2 | `ettelem config` | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` (21) | READ: `:438` → `:665`, SP RAM |
| 3 | `ettelem config` | `DM_CMD_GET_MODULE_POWER_STATE` (23) | READ: `:48` → `:551`, SP RAM |
| 4 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_FREQUENCIES` (53) | READ: `performance.c:41` → `io_pll.c:907-960`, PLL register reads |
| 5 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_VOLTAGE` (32) | READ: `thermal_pwr_mgmt.c:1142`, PVT reads and two `pmic_get_voltage` I2C register reads (allowed by the owner's rule of 2 November 2026) |
| 6 | `ettelem sample` (the 10 Hz sampler; `lib.sh`'s 1 s die reads) | `DM_CMD_GET_MODULE_POWER` (33) | READ: `:984`, SP RAM |
| 7 | `ettelem sample` | `DM_CMD_GET_SP_STATS` (60) | READ: `performance.c:404` → `thermal_pwr_mgmt.c:2780`, SP RAM, no reset |
| 8 | `ettelem sample` | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | READ: `:732`, PVT sensor reads |
| 9 | `ettelem sample` | `DM_CMD_GET_MODULE_VOLTAGE` (31) | READ: `:1010`, nine `pmic_get_voltage` register reads (allowed) |
| — | `lib.sh:154`'s forwarded arguments (a possible `--reset-ms` = `DM_CMD_SET_STATS_RUN_CONTROL`, 62) | WRITE, conditional: **never sent** (the reviewed exception: `block_e155.sh:103` passes the file and the duration only, and `ettelem_guard.sh` refuses `--reset-ms`) | |
| — | `lib.sh`'s `drain_mgmt` (`dev_mngt_service`) | **never sent**: replaced by a refusal in `block_e155.sh` | |
| — | `sparsity_host` (E109's `build/e109`; E78's heater `build/sparsity`) | the Master Minion's device-ops: DMA writes and reads of device DRAM, kernel launches, an abort on a 6 s overrun: the workload, not a device-management command | |
| — | `et-lab-manifest`, `et-holders`, `et-who` | sysfs and `fuser` reads; they open no device node | |

Not sent: the statistics reset, the SP log level (67), `sptrace`, `dev_mngt_service`, the firmware-revisions query (14), a residency read, any
governor, TDP, threshold, clock or voltage set, any reset.

## What this cannot say

- **F1b rests on the per-op premise, which F3 does not bound at ±30 pJ.** Every reading of D31 assumes equal per-op work in the two formats. F3's
  interval (−18.8 to +35.1 pJ, after the frozen allowance) lets a per-op difference move D31 by −0.151 to +0.081 W, enough at its upper end to
  reach the new-address count's band. The premise-free check (Q31k) is post hoc and leans on B's price from fp32's three arms (0.146 ± 0.077 pJ a
  TenB write), itself an effective number that absorbs fp32's TenA, scratchpad and register changes between the arms.
- **Wn's exclusion is narrow**: 0.017 W on the primary, 0.002 W with the meter's dips kept.
- **The A path is not excluded at three rows**: its band holds D31. Its exclusion as the sole per-row carrier is E148's (W2, two rows), and at three
  rows it rises with the walk, so this shape cannot separate them; the two-term mixture of E148 over-predicts D31 by 0.13 W.
- **RTL, not silicon, and a later revision.** The counts come from core-et's later revision (Erbium), not the ET-SoC-1's own RTL; R6 shows the
  schedule carries over, not the energy of each event.
- **One card, one morning.** The toggle count now fits two shapes in two sessions on aifoundry1 card 1; no other card has run these arms.
- **The per-cycle candidates stay together.** What stays at one row (0.93 W) may be per-cycle work or one row's A staging; no arm here separates
  them, or TenC's reads as such, the TIMA controls and the core.

## Files

`e155.json`, `runs.csv`, `reduce.txt`, `reduce.log` (the primary reduction); `scored.json`, `results.md`, `score.log` (`score_e155.py`; the set-aside rule
chose the primary); `e155-relaxed.json`, `scored-relaxed.json`, `results-relaxed.md` and logs (always run, not needed); `e155-dipskept.json`,
`e155-auto.json` with their `scored-*`, `results-*`, `runs-*`, `reduce-*` (the two arms); `readme-numbers.txt` (every number above, printed by
[`numbers_e155.py`](../../../../tools/claims-v3/e155/numbers_e155.py), written while the passes ran); `telemetry-max.json`
([`telemetry_max_e155.py`](../../../../tools/claims-v3/e155/telemetry_max_e155.py), E148's); `posthoc/` (post hoc, deciding nothing: `posthoc_e155.py`,
written while the passes ran, and its `posthoc.txt`/`posthoc.json`); `aifoundry1-c1/e155/p1551[0-8]/` (every pass's raw data: `runs.jsonl`,
`marks.jsonl`, `telemetry.jsonl.gz`, `tiles/`, `config_start.json`, `config_end.json`, `manifest.txt`, `binaries.sha256`, `code.sha256`, `gen.sha256`,
`configs.json`, `plan.json`, `run.log`, `block.json`); `aifoundry1-c1/e155-smoke/p15501/`; `aifoundry1-c1/e155-stoptest/p15502/` (with `STOP.die`,
`STOP.board`, `STOP.watch`, `STOP.stale`, `stoptest.rc`); `logs/` (the session, its two config reads with their times, the queue, the preflight,
`binaries.sha256`, `T0`; `logs/desk/`, the box's checks before the claim). The registration and code are in
[`tools/claims-v3/e155/`](../../../../tools/claims-v3/e155/README.md).

Rerun from the repo root: `bash tools/claims-v3/e155/pipeline_e155.sh <out dir> docs/reports/data/2026-11-03-e155-int8-floor-rows/aifoundry1-c1/e155/p1551[0-8]`
(needs `uv` for numpy). Post hoc: `python3 docs/reports/data/2026-11-03-e155-int8-floor-rows/posthoc/posthoc_e155.py`.

## Blog sentences, each with its baseline, its card and its source

*Any line about the RTL is about its later revision (Erbium, core-et), not the ET-SoC-1's own.*

- With nothing to multiply, an int8 matmul loop on this chip still draws more than the same loop in fp32, and the excess depends on the shape: 0.93 W
  with one row of A, 1.24 W with three, 1.63 W with sixteen. [aifoundry1 card 1, 600 MHz, nine passes; `scored.json` › `stats.N1`, `stats.N3`; E148
  `scored.json` › `stats.N`]
- The part that grows with rows follows how many bits of the accumulator memory's read address flip, not how often that address changes: frozen
  before the run, the bit-flip count predicted the three-row excess to within 0.012 W from the one-row level measured the night before, where counting
  address changes missed by 0.13 W and assuming no change by 0.36 W. [aifoundry1 card 1; `scored.json` › `rules.F1`,
  `reported.N3_out_of_sample`]
- That reading assumes the two formats spend the same energy on each operation's fixed work. Measured at three rows it is about 90 pJ an operation in
  each, equal to within −19 to +35 pJ, not yet inside the ±30 pJ the test asked for. [aifoundry1 card 1; `scored.json` › `rules.F3`,
  `stats.e3_fp32_pJ`, `stats.e3_int8_pJ`]
- The open RTL predicted two new schedules on silicon to the cycle: 128 and 110 cycles an op in fp32 and int8 at three rows, 72 and 62 with half the K.
  [aifoundry1 card 1; `scored.json` › `rules.R6`]
- Run with half the K at three rows, int8 keeps one row's exact schedule but its accumulator walks, and that alone costs about 0.22 W once the halved B
  traffic is added back, near the bit-flip count's 0.26 W (post hoc). [aifoundry1 card 1; `posthoc/posthoc.txt` section 2]
