# E155: int8's no-issue floor by shape - three A rows against one, with K = 8 partners in both formats (Q139, aifoundry1 card 1)

Tue 3 Nov 2026 (week 45), Q139, lane a1c1-e155-int8-floor. **Registered before the claim and the first launch.** It answers
[section 11 of the kinds page](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 11, int8's no-issue
floor** ("int8 zeros' extra 0.61 W"), and **rank 10 of Q138's final critic**: "int8's no-issue floor by shape: which count the per-row part follows
(address-bit toggles against new-address reads), the per-op premise, and what stays at one row", whose next test is "a registered three-row arm
with K = 8 partners in both formats (avoid four rows, errata type D), both counts' predictions frozen. Rule: the rise from one row to three within
the frozen count's band, and the per-op difference between the formats bounded below 30 pJ." It builds on
[E148](../../../docs/reports/data/2026-11-02-e148-int8-excess/README.md) (this card, Mon 2 Nov 22:11-22:46 PST, ten passes: with nothing issued
int8's sixteen-row loop costs N = 1.631 ± 0.049 W more than fp32's, one A row N1 = 0.884 ± 0.077 W, two rows put back D21 = 0.159 ± 0.096 W; W1
WALK on E129's wide range, but at E148's own scale the walk counted in new-address reads over-predicts D21 twofold and the walk counted in
address-bit toggles fits, post hoc), on [E129](../../../docs/reports/data/2026-11-02-e129-int8-noissue/README.md) and
[E109](../../../docs/reports/data/2026-11-01-e109-int8-zeros/README.md) (the K = 8 construction of per-op work) and on
[Q136(c)](../../../docs/reports/data/2026-11-02-q136c-tima-bench/README.md) (the TIMA bench).

## The question, and the arms that answer it

E148 left two things open. **Which count the per-row part follows:** the walk counted in TenC reads at a new address (the registered count) or in
TenC read-address bits that change (chosen after E148's data). **The per-op premise:** every reading assumes equal per-op work in the two formats;
at two rows the formats ran within 2.1 % of each other's op rate, so the premise barely mattered. Three rows separate the two counts by 0.16 of the
walk's sixteen-row share (0.542 against 0.385), and at three rows int8 runs 16 % more ops a second than fp32 (110 against 128 cycles an op), so the
premise matters and must be measured. Four rows would separate the counts further but fall in errata 1.29 type D for the float ops (A of 4 rows
with B in the L1 scratchpad); three rows do not. **The K = 8 partner** of the three-row arm measures each format's per-op work there (E109's
construction: the same rows, half the K, so the op rate nearly doubles while every cycle stays busy).

The bench ([`desk/bench-e155.json`](desk/bench-e155.json), Q136(c)'s binary run by [`desk/bench_e155.py`](desk/bench_e155.py); its m0 and m0r1
streams are identical to Q136(c)'s committed `counts.json` and m0r3's to E148's post hoc ladder) says, per op on one minion with the row mask 0x0000:

| an op, nothing issued | `m0r1` int8 (1 row, K 16) | **`m0r3` int8 (3 rows, K 16)** | **`m0r3k8` int8 (3 rows, K 8)** | `m0r3` fp32 | `m0r3k8` fp32 |
|---|---:|---:|---:|---:|---:|
| bench cycles (card: + 7.75, E109's rule) | 54.25 → 62 | **102.25 → 110** | **54.25 → 62** | 120.25 → **128** | 64.25 → **72** |
| TenC reads; at a new address; address-bit toggles | 996; 0; 0 | 1,764; **768; 1,024** | 996; **384; 512** | 0 (2,052 in the card's order, one address) | 0 (1,156) |
| TenTMP writes = 64-bit A reads | 8 | 16 | 8 | 0 | 0 |
| TIMA control bits clocked (int8 enables) | 5,775 | 10,911 | 5,775 | 0 | 0 |
| TenB writes (B) | 256 | 256 | 128 | 256 | 128 |

**`m0r3k8` int8 runs one row's schedule exactly** (62 cycles, the same TenC read count, TIMA control bits and TenTMP staging an op as `m0r1`) **with
the walk on.** Against `m0r3`, int8's walk and TenTMP staging a second fall by 11.3 % and its TIMA control bits by 6.1 %, so the raw per-op
difference between the formats reads low by the cost of those changes; F3 carries a frozen allowance for it.

**N3 = S(`m0r3.int8.zeros`) − S(`m0r3.fp32.zeros`)** and the registered statistic **D31 = N3 − N1**, paired inside each pass beside N1 (E148's D21
construction at three rows). Each format's per-op energy at three rows, **e(f) = [D(`m0r3k8`.f) − D(`m0r3`.f)] / [rate(`m0r3k8`.f) − rate(`m0r3`.f)]**,
and **Δe₃ = e(int8) − e(fp32)**.

## The frozen readings of D31 ([`predictions-e155.json`](predictions-e155.json) › `readings`, printed in [`predictions-e155.txt`](predictions-e155.txt))

Each reading is a **count term**, E148's measured part put where the reading says it goes and scaled by the bench's counts a second (int8 − fp32 in
the card's order, at E148's measured duty 0.99577 for short ops), plus the **shared per-op term**: with equal per-op energy in the two formats, N3
carries E_op × (rate(int8) − rate(fp32)) = E_op × 0.782 × 10⁹ a second, where E_op = **108.7 pJ an op [90.6, 126.8]** is fp32's per-op energy at K
= 16 (its per-op work and its B traffic), frozen from E148's fp32 [S(`m0r1`) − S(`m0r2`)] / [rate(`m0r1`) − rate(`m0r2`)] over ten passes; that
term is **+0.085 W [0.071, 0.099]**. Each band is the count term's range from E148's ten-pass 95% interval (N − N1 0.664–0.831 W, N1 0.807–0.960
W) plus the shared term's range. Nothing is fitted to E155's data.

| reading | what it says | factor | count term, W | **D31, W** | band (95%) |
|---|---|---:|---:|---:|---|
| **Wn** the walk in new-address reads | all of E148's N − N1 is TenC's walk, priced a read at a new address (E148's registered count) | 0.5418 of N − N1 | +0.405 | **+0.490** | +0.430 to +0.549 |
| **Wt** the walk in address-bit toggles | all of it is the walk, priced a read-address bit that changes (E148's post hoc count, registered here) | 0.3853 of N − N1 | +0.288 | **+0.373** | +0.327 to +0.419 |
| **T** the A path | all of it is TenTMP's staging, a 64-bit A read (excluded as the sole carrier by E148's W2) | 0.2271 of N − N1 | +0.170 | **+0.255** | +0.222 to +0.288 |
| **C** per cycle | none of the rise is per-row: N1 is per-cycle work, scaled by the TIMA controls' clocked bits a second | 0.0649 of N1 | +0.057 | **+0.142** | +0.123 to +0.162 |
| reported: E148's two-term solve | 75.5 fJ a new-address read and 3.43 pJ a 64-bit A read (E148 `scored.json` › `reported.two_term`) | | +0.357 | +0.442 | — |
| reported: the null | a third row changes nothing | | 0 | 0 (or +0.085 with the shared term) | — |

The four bands do not overlap: C's top (0.162) lies below T's bottom (0.222), T's top (0.288) below Wt's (0.327), Wt's top (0.419) below Wn's
(0.430).

## Rules (frozen in `predictions-e155.json` › `rules`; scored by [`score_e155.py`](score_e155.py))

Every statistic is computed per kept pass, paired inside the pass, then its mean and 95% t interval over passes. S is over the run's idle bracket and
D over the format's zeros (E78's reduction, E148's primary: leakage 0.2414 W/°C, card 1's launch-gap dips removed).

| rule | statistic | line | verdicts |
|---|---|---|---|
| **F1** (primary) | D31 = N3 − N1 | each reading X ∈ {Wn, Wt, T, C}: CONSISTENT if D31's 95% interval overlaps X's frozen band, else EXCLUDED | **F1a, the walk against the per-cycle reading:** WALK (Wn or Wt consistent, C excluded) / PER-CYCLE (C consistent, Wn and Wt excluded) / NEITHER / INCONCLUSIVE. **F1b, address-bit toggles against new-address reads:** TOGGLES (Wt consistent, Wn excluded) / NEW-ADDRESS (Wn consistent, Wt excluded) / NEITHER / INCONCLUSIVE (both). The consistent set, T included, beside them |
| **F3** | Δe₃c = Δe₃ − b_mid, b the frozen allowance for int8's count changes between the partner and the arm | H = √(h² + b_half²), h the 95% t half-width of Δe₃; **BOUNDED** if [Δe₃c − H, Δe₃c + H] lies inside (−30, +30) pJ; EXCEEDS if it lies wholly outside; else INCONCLUSIVE | BOUNDED / EXCEEDS / INCONCLUSIVE; the raw Δe₃ reported beside it |
| R6 | median cycles per op, six arms | \|measured − predicted\| ≤ 2.0: `m0r1` 62 / 62, **`m0r3` 128 / 110 (new)**, **`m0r3k8` 72 / 62 (new)** (fp32 / int8) | PASS / FAIL per arm |
| T1 | N1 against E148's 0.884 W | \|difference\| ≤ 0.5 W | PASS / FAIL; labels, removes nothing |

**F3's allowance** (`predictions-e155.json` › `f3_allowance`): int8's walk and TenTMP a second fall by 11.3 % and its TIMA control bits by 6.1 % from
`m0r3` to `m0r3k8`, which E109's construction books as per-op work. Priced under each frozen reading and divided by int8's rate change (4.306 × 10⁹
a second), it makes the raw Δe₃ read low by **10.6 pJ (Wn), 7.5 (Wt), 13.3 (C) and 16.5 (E148's two-term solve)**: b_mid = −12.0 pJ, b_half = 4.5
pJ. Under T alone (excluded as the sole carrier by E148) it would be −39.4 pJ. B's TenB writes a second fall in both formats (int8 −1.61 × 10¹¹,
fp32 −1.36 × 10¹¹); at 0.10-0.16 pJ a write that moves Δe₃ by 0.1 pJ, so no allowance is made for it.

**At least 3 kept passes** for every rule, else NOT-SCORED. **The set-aside rule** (`set_aside_rule`, E148's): the primary reduction carries every
verdict if it keeps at least 3 passes; if it keeps fewer, the relaxed reduction (`reduce_e155.py --relax-tie`, π's drift gate lifted) carries them if
it keeps more, labelled; the relaxed one is always reported; no pass is added after any reduction is read, and none is chosen after the fact.

**Reported with no verdict:** N3, N3k8 = S(`m0r3k8.int8`) − S(`m0r3k8.fp32`); **D31 less the shared term measured in this session** (E_op from this
session's fp32 `m0r1` against `m0r3`) and each count's one-term price fitted on it; each format's e at three rows and the raw Δe₃; **Q31k =
S(`m0r3k8.int8`) − S(`m0r1.int8`)**, int8 at one row's schedule with the walk on, against the walk parts of Wn (+0.359 W [0.319, 0.399]) and Wt
(+0.255 [0.227, 0.284]) (C and T put nothing there; B's TenB writes a second are halved in it, −1.26 × 10¹² a second, which no frozen number
prices); N3's out-of-sample prediction by each reading (E148's N1 + the reading's D31, and this session's N1 + it); every arm's D, S, rate and
cycles; the leakage-`auto`, dips-kept and relaxed arms.

**Expectations, not lines.** R6 PASS ×6 (the bench matched E129's one row and E148's two to the cycle; three rows and K = 8 there are new). T1 PASS.
F1's precision is set by the number of passes: E148's per-pass spread of D21 (0.134 W) gives D31 a 95% half-width of **0.096 W at ten passes, 0.141
at six, 0.214 at four and 0.335 at three**. So F1a (the walk bands against C's, at least 0.17 W apart) is decidable at six or more passes, while F1b
(Wt's and Wn's bands, 0.011 W apart at their facing ends and 0.117 W between their points) resolves only if D31 lands near or beyond one count's
point; INCONCLUSIVE is a likely outcome of F1b. **On a cool morning this card's passes took 522-650 s** (E129, a median of 5-8 heats a launch from a
47 °C die) against **170-206 s on a warm evening** (E148, 1-2 heats), so the number of passes, and with it every interval, depends on the morning.
F3's h is expected near 20 pJ at ten passes (E148's spread of two-arm differences, 0.088 W a pass, over the rate changes of 3.7 and 4.3 × 10⁹ a
second), so BOUNDED needs |Δe₃c| below about 10 pJ.

## What is reused unchanged, and what changes

E148's harness, every change marked E155 in each file: E78's runner `run_e78.py`, `e78_common.py`, reducer `reduce_e78.py`, `kinds.json` and its
fp32 and int8 zeros tiles; `lib.sh`; E109's binary `sp109/` (built on aifoundry1 into `build/e109` for E124, run by E129 and E148); E128's telemetry
allow-list `e128/ettelem_guard.sh`; Q136(w)'s checker `dmcmd_audit.py` and its table. Their sha256 (E148's 20 files, unchanged since E148's freeze,
and the 5 box binaries) are frozen in `predictions-e155.json` › `harness` and checked by [`check_e155.py`](check_e155.py) before any device opens and
before any reduction.

1. **The arms.** E148's `m0` and `m0r2` are replaced by **`m0r3`** (three A rows, K = 16) and **`m0r3k8`** (three A rows, K = 8), each with mask 0x0000
   ([`e155_common.py`](e155_common.py) › `ARMS`); `m0r1` stays. The six items: `m0r1`, `m0r3` and `m0r3k8` on each format's zeros. **The pass is
   E148's**: π burn-ins ×2, π first and last, each format's zeros once in each of three segments, the six arms dealt round-robin with seed
   `E155|aifoundry1-c1|<pass>`: 14 runs. Launch at 58 °C after a 59 °C preheat, 2 s quiet, 4 s runs on all 1,024 minions (E78's frame). B stays in the
   L1 scratchpad (`--b-stream` is never passed), at one or three A rows: outside errata 1.29 type D. Nothing issues, so power is low.
2. **Live-sample stops** (E148's, from E142, in [`run_e155.py`](run_e155.py)): the newest line of the running sampler's file is read before every
   launch and every 0.1 s while waiting, and by an in-run watcher every 0.1 s that writes the STOP file the host program checks before every launch;
   **board_w ≥ 66 W** or **any minion-shire reading ≥ 72 °C** ends the pass (E148's session peaked at 59.79 W), plus run_e78's die cap `--max-c 72`.
   **NEW, from E148's verifier (C7): a line 1.5 s old or older when read is itself a stop**, in the guard and the watcher (the sampler writes every
   0.1 s; E148's largest gap was 101 ms), so a sampler that dies mid-run ends the pass within one launch. **The stop path is tested before the
   smoke** (`block_e155.sh 15502 --stoptest`, no launch: the die stop at 1.0 °C, the board stop at 1.0 W, the watcher at 1.0 W and the stale limit at
   0.0 s must each end with exit 6 and a STOP line read from a live sample); anything else and no smoke or pass runs.
3. **Passes and the budget.** Passes **15510-15519** in order, smoke **15501**, stop test **15502**. **At most 40 card-minutes**, counted from the
   session's first config read to its last: [`queue_e155.sh`](queue_e155.sh) starts a pass only if now + projected ≤ T0 + 2,400 − 150 s and its end
   is before **11:20 PST**; projected is 600 s (E129's cool-morning passes) until a pass ends, then the longest measured. **No session starts after
   10:30 PST** ([`session_e155.sh`](session_e155.sh) refuses); every run ends by 11:30 PST (Q139's gates).
4. **The scorer** ([`score_e155.py`](score_e155.py)) and the predictions ([`make_predictions_e155.py`](make_predictions_e155.py)) are new;
   [`selftest.txt`](selftest.txt): A, the bench's m0/m0r1 counts identical to Q136(c)'s and m0r3's to E148's ladder; B, the scorer on E148's
   reduction with synthetic m0r3/m0r3k8 items at each reading's point returns that reading's F1a/F1b verdicts (WALK + NEW-ADDRESS, WALK + TOGGLES,
   PER-CYCLE + NEITHER, NEITHER + NEITHER) and F3 BOUNDED, and Δe₃ = mid + 60 pJ returns EXCEEDS; C, the line test (stale at 1.5 s, the stop test's
   0.0 s, the board and die lines). The reducer ([`reduce_e155.py`](reduce_e155.py), E148's wrapper) ran mechanically at the desk on a renamed copy
   of E148's pass 14810.

## Device commands sent

Every command the run sends to card 1, classified from the source of its running build: release 1.4.0, **BL2 0.22.0**, et-platform **`836a4ab`**
(the version-matched revision of Q136(w)'s table, E129's dated note C1 and E148's audit of the same command set). Q136(w)'s checker on every file
the session runs reads **GO: 32 send sites, 0 disallowed, no WRITE allowed** ([`dmcmd-audit.txt`](dmcmd-audit.txt), from
[`preflight_e155.sh`](preflight_e155.sh)); the session runs it again on the box and opens no device unless it reads GO.

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
| — | `lib.sh:154`'s forwarded arguments (a possible `--reset-ms` = `DM_CMD_SET_STATS_RUN_CONTROL`, 62) | WRITE, conditional: **never sent** (the reviewed exception: `block_e155.sh:103` passes the file and the duration only, and `ettelem_guard.sh` refuses `--reset-ms`) |
| — | `lib.sh`'s `drain_mgmt` (`dev_mngt_service`) | **never sent**: replaced by a refusal in `block_e155.sh` |
| — | `sparsity_host` (E109's `build/e109`; E78's heater `build/sparsity`) | the Master Minion's device-ops: DMA writes and reads of device DRAM, kernel launches, an abort on a 6 s overrun: the workload, not a device-management command |
| — | `et-lab-manifest`, `et-holders`, `et-who` | sysfs and `fuser` reads; they open no device node |

**The run sends no WRITE.** Not sent: the statistics reset, the SP log level (67), `sptrace`, `dev_mngt_service`, the firmware-revisions query (14),
a residency read, any governor, TDP, threshold, clock or voltage set, any reset.

## Protocol

1. **Desk, before this commit:** the bench run and its identity checks; `make_predictions_e155.py`; `selftest_e155.py` (PASS); the preflight (GO);
   `bash -n` of every script; the reducer's mechanical run. **On the box, before the claim:** the files synced into `~/nekko`, `check_e155.py`,
   `preflight_e155.sh` GO, `bash -n`, a stub run of `queue_e155.sh`, `V3_DRY=1` of the stop test, the smoke and pass 15510.
2. This registration committed and pushed; then the claim: Tue 3 Nov's one card post in `#community-lab` (the first lane to reserve that day posts
   it; every later change rewrites it under the discord lock with `EXPECT_TEXT`) gains `using aifoundry1 card 1 for 1 h, until ~HH:MM PST [doc](…)`;
   never while another of our clauses holds aifoundry1; Mon 2 Nov's post is never edited again.
3. [`session_e155.sh`](session_e155.sh), detached on aifoundry1 (`setsid nohup`, `E155_T0` = the launch): the 10:30 gate; `check_e155.py`; the
   preflight; `et-who`; the opening `ettelem config` under card 1's lock (`ET_DEVICES=1`, `timeout 10`, through the guard); the stop test (15502)
   and its gate; the smoke (15501: eight items, 2 s runs, no preheat) and its gate ([`smoke_gate_e155.py`](smoke_gate_e155.py), E109's rule); the
   queue; the closing config read; `et-who`.
4. The release by rewriting the day's post; the data collected to the Intel ([`collect_e155.sh`](collect_e155.sh)), reduced and scored with
   [`pipeline_e155.sh`](pipeline_e155.sh), data in `docs/reports/data/2026-11-03-e155-int8-floor-rows/`.

**Stops:** `build/e155/STOP`; the live board, die and stale-line stops above; another user's device process, a device node or this card's lock held
by anyone else (exit 3, no retry; another user's idle login does not block, D1 for `aifoundry1-c*`); a failed pass. **No power cycle and nothing that
risks one:** nothing issues in the arms, no random anchor runs, E78's heater (2 s fp32 random launches, about 59 W at the board in E148) is the
hottest run. **Nothing is set.**

## What a result does to predicting power and heat

The term under test is int8's no-issue floor, the part of an int8 matmul's power that is there whatever the data and whether or not anything issues:
1.63 W over fp32's on this card at sixteen rows, 0.88 W of it at one row. E148 gave it the form **N(shape) ≈ N1 + (a per-row part) + (the shared
per-op work at the formats' rate difference)** but left the per-row part's count open. E155 predicts a shape no model has seen, three rows, from
counts and prices frozen before the run: **the out-of-sample error of D31 (and of N3 = N1 + D31) is scored for each count** against the null (no
change, error = D31 itself), and the count that holds becomes the model's per-row term for any int8 shape (a price per address-bit toggle or per
new-address read, times the bench's count). F3 measures the premise the shared term rests on. Heat follows power through card 1's die rise per board
watt (M7's H2, 0.1151 °C/W): a 0.1-0.5 W difference is 0.01-0.06 °C, below what the 4.5 s readout resolves, so E155 scores power only.

## Amendments

None yet. Any departure is a dated amendment written before the data it touches.
