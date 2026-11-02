# E129: one A row splits int8 zeros' no-issue excess about in half, and per-op work is bounded below half the gap when pooled with E124 (Q136, aifoundry1 card 1, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 11, "int8 zeros' extra 0.61 W"** (the complaint this answers, as the Horace hub's Status quotes it: "per-op work is excluded at the 770 pJ its reading needs, but not bounded below half the gap (R1 INCONCLUSIVE). Left: where the 1.7 W goes."). It is item 5 of Q134's final critic: "one card arm, and per-op work bounded with six or more passes". It builds on [E109](../2026-11-01-e109-int8-zeros/README.md) (aifoundry3), [E124](../2026-11-01-e124-int8-zeros-replicate/README.md) (this card) and [Q136(c)](../2026-11-02-q136c-tima-bench/README.md) (the TIMA bench, whose section 6 proposed this arm).*

*Mon 2 Nov 2026 (week 45), Q136, lane a1c1-e129-int8-noissue. Pre-registered in [`tools/claims-v3/e129/E129.md`](../../../../tools/claims-v3/e129/E129.md) with [`predictions-e129.json`](../../../../tools/claims-v3/e129/predictions-e129.json), committed and pushed as **`f4a4af74`** (10:07:21 PST), before the claim (10:07:52 PST) and before any device opened (10:08:00). Amendment **A1** (`7b0fa202`, 10:19:14 PST) was written while the first pass ran and before any E129 power data was read (§ Departures). **aifoundry1 card 1** (`V3_DEVICE=1`, its own lock), firmware 1.2.0 (BL2 0.18.0), at **600 MHz, 499–500 mV**. `ettelem config` was read under card 1's lock with `timeout 10`, through E128's allow-list, at 10:08:00 and 10:38:33 PST: TDP 65 W, threshold 65 °C, 600 MHz both times (power state `low_power`, then `managed_power`, as E124 and E128 saw). **Nothing was set and no WRITE was sent** (§ Device commands sent). **Card session 10:08:00–10:38:33 PST, 30.5 card-minutes of the 35 allowed.** The card was claimed at 10:07:52 by rewriting the day's one card post in `#community-lab` (message `1566837317765963987`) and released at 10:39:06 by rewriting it again (§ How it ran).*

## Results

**Three passes ran and all three are kept** (12910–12912; E78's gates as they apply to E129's pass, card 1's frame; the set-aside rule was not needed). Six were registered as R1's minimum, and the budget allowed three: this morning's cool die needed a median of 5–8 heats a launch, and the cut pass had no hot anchor to keep it warm (§ Departures). So E129's own R1 reads NOT-SCORED, as registered, and the pooled R1p of amendment A1 carries the per-op question. Every other registered rule scores at three passes. ([`scored.json`](scored.json) › `n_passes`, `which_reduction_scores` = "primary"; [`e129.json`](e129.json) › `passes_set_aside` = [])

1. **One A row removes about half of int8's no-issue excess** (V1 INCONCLUSIVE at its N/2 line; V2 excludes both extremes). With nothing issued, int8's 16-row loop costs **N = 1.566 ± 0.125 W** more than fp32's (Y1 PASS; E124 read 1.567 on this card). With one A row, the two formats at the same 62.0 cycles an op (V0 EQUAL-RATE, 9.86 × 10⁹ ops a second each), the excess is **N1 = 0.865 ± 0.357 W** (per pass 1.022, 0.739, 0.836). So **0.701 ± 0.421 W** (95% 0.28–1.12) goes with something int8 does for each row of A, its TenC read-address walk or its A path, and about 0.87 W stays with work it does every cycle at the same op rate. N1's interval [0.51, 1.22] straddles the line N/2 = 0.78, so V1 is INCONCLUSIVE. (`scored.json` › `one_row`, `rules.V0_equal_rate`, `rules.V1_one_row`)
2. **Two readings are excluded, two remain** (V2). N1 lies **above** the bench's price at its own constants in the card's order (0.070–0.140 W), and **below** "all of N is work done every cycle" (1.40–1.57 W, the r1/m0 ratio of the TIMA controls' and TenC's reads a second). It is consistent with the bench's price from reset (0.40–0.79 W) and with the TIMA controls alone at the cards' issue price (0.49–1.46 W, Q136(c) result 5b). (`scored.json` › `rules.V2_readings`)
3. **Per-op work is bounded below half the gap, pooled with E124** (R1p FAIL, amendment A1). Over E124's four passes and E129's three, seven passes on this card, **G_op = +0.059 ± 0.155 W** (95% −0.10 to +0.21) against the line at half the pooled gap, 0.307 W. E129 alone gives +0.058 ± 0.142 W at three passes, with e_op **81 ± 43 pJ (fp32) and 77 ± 92 pJ (int8)** an op; E124 gave +0.060 ± 0.370 W at four. E129's own R1 reads NOT-SCORED (three of the six passes it needs). (`r1p.json` › `G_op`, `line_w`, `verdict`, `by_session`; `scored.json` › `rules.R1_ops`, `rules.Y2_per_op_ceiling`)
4. **E109's answer holds again on this card** (R0 PER-TIME, R2 LANES-OPPOSE, R3 PASS, Y1 PASS, Y2 PASS). The zeros gap is **G = 0.702 ± 0.102 W** (E124: 0.548). The lanes favour int8 by **G_lane = −0.985 ± 0.099 W**, issuing on zeros costing **fp32 1.431 ± 0.106 W, int8 0.446 ± 0.160 W**, and what neither the op rate nor the lanes move carries **G_rest = +1.629 ± 0.233 W**, 95% lower bound 1.40 W against G/2 = 0.35 W. Both e_op upper bounds (124 and 169 pJ) are far below the 770 pJ the ops reading needs. (`scored.json` › `gap`, `rules.R0_answer`, `rules.R2_lanes`, `rules.R3_per_time`)
5. **The silicon keeps the RTL's schedule at one A row** (R6 PASS ×6). Every arm's cycles per op equal the frozen prediction (the bench's plus E109's 7.75): `m0` 544.001 / 318.001, `m0k8` 280.001 / 166.0, and **`m0r1` 62.0 in both formats**, the bench's 54.25 + 7.75 to the cycle. The smoke read the same. (`scored.json` › `rules.R6_cycles`; [`logs/session.log`](logs/session.log), the smoke lines)
6. **The session ties to E124 on this card in all seven cells** (R10 PASS ×7): D of `m0` −1.431 / −0.446 W (E124 −1.457 / −0.401), of `m0k8` −1.345 / −0.310 (−1.360 / −0.253), π 8.185 (8.121), G 0.702 (0.548, inside its ±0.2 W band) and N 1.566 (1.567). (`scored.json` › `rules.R10_tie`)

**What it changes.** Item 11 narrows on both of its open parts. **Per-op work:** registered, pooled over seven passes on one card, it is bounded below half the gap (R1p FAIL), so "the gap is not per-op work" is no longer only E109's labelled reading; E129's own three passes alone did not reach the six that R1 itself needs. **Where the 1.7 W goes:** with one A row, int8's no-issue excess falls from 1.57 to 0.87 W. About 0.7 W goes with int8's per-row work (its TenC read-address walk or its A path), about 0.9 W with work it does every cycle at an equal op rate. Neither half can be zero at 95%, so the bench's price at its own constants in the card's order (0.07–0.14 W) is excluded, and so is "all of it every cycle". Left open: which per-row event (the walk or the A path) and which per-cycle one (TenC's reads as such, the TIMA controls, or the core) carry each half. *Post hoc, deciding nothing ([`posthoc/posthoc.txt`](posthoc/posthoc.txt)): if all of the per-row half were the walk, a TenC read at a new address would cost 89 fJ (95% 35–142); if it were the A path's 64-bit reads into TenTMP, 5.7 pJ a read, far above the 0.61 pJ that fp32's own no-issue level allows any scratchpad read on this card (E124), so the walk is the likelier carrier of that half.*

## The arms (primary reduction)

D is over the format's zeros (interpolated between the pass's zeros anchors) and S over the idle bracket, ± 95% over 3 passes (t 4.303). "Cycles" is the median over the kept runs. Source: `e129.json` › `items`, `per_pass`.

| item | cycles | ops/s (10⁹) | D | S |
|---|---|---|---|---|
| `fp32.zeros` | 546.001 | 1.1209 | 0 | +1.497 ± 0.113 |
| `int8.zeros` | 318.001 | 1.9246 | 0 | +2.199 ± 0.022 |
| `anchor_pi` | 546.001 | 1.1209 | +8.185 ± 0.044 | +9.742 ± 0.081 |
| `m0.fp32.zeros` | 544.001 | 1.1251 | −1.431 ± 0.106 | +0.134 ± 0.174 |
| `m0.int8.zeros` | 318.001 | 1.9248 | −0.446 ± 0.160 | +1.700 ± 0.069 |
| `m0k8.fp32.zeros` | 280.001 | 2.1857 | −1.345 ± 0.061 | +0.188 ± 0.205 |
| `m0k8.int8.zeros` | 166.0 | 3.6869 | −0.310 ± 0.019 | +1.854 ± 0.069 |
| `m0r1.fp32.zeros` | 62.0 | 9.8644 | −0.400 ± 0.109 | +1.188 ± 0.112 |
| `m0r1.int8.zeros` | 62.0 | 9.8647 | −0.137 ± 0.294 | +2.053 ± 0.389 |

`m0` = the row mask 0x0000 (no micro-op issued), `k8` = K of 8, `r1` = one A row. Idle 32.93 W; leakage slope frozen at 0.2414 W/°C (E82's on this card); 40 of 40 runs kept; 600 MHz in every run; duty 0.9954–0.9962; card 1's launch-gap dips removed, 12, 18 and 22 samples a pass. One row's 5–9 times faster op and B traffic raise each format's level over its 16-row loop: S(m0r1) − S(m0) = +1.054 ± 0.063 W in fp32, +0.353 ± 0.412 W in int8 (reported, no verdict; `scored.json` › `one_row`).

## The registered rules against the data

`scored.json` is `score_e129.py`'s output with `predictions-e129.json` on the primary, chosen by the set-aside rule over the relaxed reduction; `r1p.json` is `pool_r1_e129.py`'s (A1). The arms: dips kept and leakage `auto`.

| rule | registered line | **E129 (primary, 3 passes)** | dips kept | leakage `auto` | expected (E124 carries) |
|---|---|---|---|---|---|
| R0 the answer | a share with 95% lower bound ≥ G/2 | **PER-TIME** | PER-TIME | PER-TIME | PER-TIME |
| R1 per-op work | G_op ≥ G/2; at least 6 kept passes | **NOT-SCORED** (3 passes; +0.058 ± 0.142) | NOT-SCORED | NOT-SCORED | INCONCLUSIVE at 6, FAIL at 8+ |
| **R1p** (A1) pooled with E124 | G_op ≥ pooled G/2; at least 6 passes | **FAIL** (7 passes; +0.059 ± 0.155 < 0.307) | — | — | — |
| R2 the lanes | OPPOSE if upper < 0 | **LANES-OPPOSE** (−0.985 ± 0.099) | LANES-OPPOSE | LANES-OPPOSE | LANES-OPPOSE |
| R3 per-time | G_rest ≥ G/2 | **PASS** (+1.629 ± 0.233) | PASS | PASS | PASS |
| Y1 the no-issue gap | lower ≥ 0.84 W | **PASS** (+1.566 ± 0.125) | PASS | PASS | PASS |
| Y2 per-op ceiling | both upper < 769.7 pJ | **PASS** (124, 169 pJ) | PASS | PASS | PASS |
| V0 one row's premise | \|Δcycles\| ≤ 2 | **EQUAL-RATE** (62.0, 62.0) | EQUAL-RATE | EQUAL-RATE | EQUAL-RATE |
| V1 one A row | N1 upper < N/2: PER-ROW; lower ≥ N/2: PER-CYCLE | **INCONCLUSIVE** (+0.865 ± 0.357 against 0.783) | INCONCLUSIVE | INCONCLUSIVE | no single expectation |
| V2 the readings | overlap with each range | **ABOVE** 0.07–0.14; **CONSISTENT** 0.40–0.79 and 0.49–1.46; **BELOW** 1.40–1.57 | the same | the same | — |
| R6 the RTL's cycles | \|measured − predicted\| ≤ 2 | **PASS ×6** (every difference ≤ 0.001) | PASS ×6 | PASS ×6 | PASS ×6 |
| R10 the tie | seven cells (E124, this card) | **PASS ×7** | PASS ×7 | PASS ×7 | PASS ×7 |

**No verdict moves with an arm.** The dips-kept arm reproduces the primary exactly: the removed samples fell outside every run's power window and idle bracket (all 40 runs' P, idle, p80, idle80, S and D are equal in `runs.csv` and `runs-dipskept.csv`). Leakage `auto` moves N to 1.576 W and leaves N1 at 0.865 W. The relaxed reduction (π's drift gate lifted) keeps the same three passes.

## Registered against what happened

| | registered | happened |
|---|---|---|
| freeze | committed and pushed before the claim and the first launch | `f4a4af74`, 10:07:21 PST; claim 10:07:52; first device process 10:08:00 (the opening config read); A1 `7b0fa202` 10:19:14, during pass 12910, before any power data was read |
| desk | self-test A–F; on the box: `check_e129.py`, the preflight, `bash -n`, a stub queue, `V3_DRY` of the smoke and pass 12910 | [`selftest.txt`](../../../../tools/claims-v3/e129/selftest.txt) PASS; [`logs/desk-check.log`](logs/desk-check.log) (25 of 25), [`logs/desk-preflight.txt`](logs/desk-preflight.txt) (GO), [`logs/desk-stub-queue.log`](logs/desk-stub-queue.log), [`logs/desk-dry-smoke.log`](logs/desk-dry-smoke.log), [`logs/desk-dry-12910.log`](logs/desk-dry-12910.log), all 10:05–10:06 PST |
| smoke | seven items; E109's gate | 10:08:01–10:08:44; every item 6 launch records, all `ok`, `tensor_errors` 0: SMOKE-GATE PASS; `m0r1` at 62.0 cycles in both formats |
| passes | 12910–12919, as many as fit 35 card-minutes; about 175–290 s each expected | 12910 (536 s), 12911 (663 s), 12912 (560 s), rc 0; the queue's rule stopped before 12913 (10:38:33 + 663 s > 10:40:29); A1's extra pass did not fit (10:38:42 + 560 + 30 s > 10:40:29) |
| kept | the primary carries if ≥ 6; else the relaxed one; R1 needs 6, the rest 3 | **3 of 3** by E78's gates; the relaxed reduction keeps the same 3; R1 NOT-SCORED, every other rule scored |
| runs | 14 a pass | 40 of 42 ran and all 40 are kept; 2 were skipped by run_e78's launch rule after 15 heats each (12911's third `fp32.zeros` anchor, 12912's opening π) |
| budget | at most 35 card-minutes, first config read to last | 30.5 (10:08:00–10:38:33); claim to release 31.2 min (10:07:52–10:39:06) |
| config | read at both ends, never set | TDP 65 W, 65 °C, 600 MHz at both ends of the session and of every pass |

## Departures (dated)

- **A1, Mon 2 Nov 2026, 10:19 PST, during pass 12910 and before any E129 power data was read** ([`E129.md`](../../../../tools/claims-v3/e129/E129.md) § Amendments, `7b0fa202`). Only the queue's log, the run log's heat counts and launch lines and the smoke gate's lines had been read; nothing had been collected. Pass 12910 began from a 47 °C die after the card had idled since 08:38 PST, and its launches needed up to 10 heats, so the registered budget would leave fewer than the six passes R1 needs. A1 added (1) one more pass by a second call if it fit (it did not: [`logs/extra-decision.txt`](logs/extra-decision.txt)) and (2) **R1p**, R1 pooled with E124's four passes on this card, scored by the new `pool_r1_e129.py`. E124's G_op (+0.060 ± 0.370 W) was known when A1 was written; E129's was not.
- **The passes took two to three times the registered estimate** (536–663 s against 175–290 s). Change 2 of the registration cut E78's pass to each format's zeros as anchors, so that six or more passes would fit. That also removed the hot runs: E124's pass ran nine random-anchor runs at 9–26 W over idle, which kept the die warm. E129's pass ran nothing above π's 10 W over idle, so E78's heater carried every launch from a die cooling toward its 47 °C idle: a median of 5, 8 and 5 heats a launch in the three passes (108, 134 and 111 heater launches; [`aifoundry1-c1/e129/p129*/marks.jsonl`](aifoundry1-c1/e129/)), up to 10, and two runs were skipped after 15. The registration expected 3 heats, E128's morning rate. The cut saved runs and cost heat. With E78's anchors kept, a pass would have been 12 runs longer (9 of them hot) and each run shorter; which is faster on a cool die was not tested. Recorded, not amended: the registered budget rule ran unchanged.

## How it ran

10:05:23–10:06:35 PST, before the commit, on the box with no device opened: Python 3.12.3; `check_e129.py` HARNESS OK (20 reused files and the 5 binaries, E124's `build/e109` among them); the preflight GO; every script parsed; the queue's budget rule on a 1 s stub; `V3_DRY` of the smoke and of pass 12910 (16 device calls in the pass: 14 runs and 2 burn-ins). `et-who`: no process held a device node or card lock. 10:07:21 the registration pushed. 10:07:52 the claim: the day's one card post, which read `<ai> **Claude says:** using aifoundry1 card 1 for 1 h, until ~09:10 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released` (E128's released clause), was rewritten to `<ai> **Claude says:** using aifoundry1 card 1 for 1 h, until ~11:10 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)` (`edit_replace.mjs` with `EXPECT_TEXT`, dry run, save, read back). 10:07:59 `session_e129.sh` started detached on the box (`setsid nohup`, T0 = the launch): `check_e129.py` (HARNESS OK); the preflight (GO); `et-who` (no holder); the opening config read; the smoke and its gate; `queue_e129.sh`; the closing config read at 10:38:33; `et-who` (no holder). The other lab user's idle logins were present throughout; no other user's process, device node or card lock was seen (E78's departure D1 for `aifoundry1-c*`).

Each pass ran E78's two burn-in runs of π, then 14 registered runs: π first and last, each format's zeros once in each of three segments, and E129's six arms dealt round-robin with seed `E129|aifoundry1-c1|<pass>`. Each run launched at a 58 °C die reading after a 59 °C preheat, with 2 s quiet and 4 s FMA runs on all 1,024 minions. Pass 12910 began from a 47 °C die, the others from 53 °C.

10:38:42 A1's extra pass was refused by its own rule. 10:39:06 the release: the post then read `…using aifoundry1 card 1 for 1 h, until ~11:10 PST [doc](…); using aifoundry2 for 3 h, until ~13:20 PST [doc](…); using aifoundry3 for 1 h, until ~11:25 PST [doc](…)` (two other lanes had added their cards), and it was rewritten to the two clauses still held, `<ai> **Claude says:** using aifoundry2 for 3 h, until ~13:20 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>); using aifoundry3 for 1 h, until ~11:25 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, and read back. 10:39–10:41 the data were collected to the Intel ([`collect_e129.sh`](../../../../tools/claims-v3/e129/collect_e129.sh)), then reduced and scored with [`pipeline_e129.sh`](../../../../tools/claims-v3/e129/pipeline_e129.sh) and [`pool_r1_e129.py`](../../../../tools/claims-v3/e129/pool_r1_e129.py). `reduce_e129.py` checks the 20 reused files' sha256 against the freeze before it reads anything.

## Device commands sent

Every command the run sent to card 1, classified from the source of its running build (firmware 1.2.0, **BL2 0.18.0**: the public et-platform 0.18.0 line `169a17566`–`da192816a`, read with `git show` in the lab's clone). E128's audit script, run unchanged because the command set is the same, gives output byte-identical to E128's ([`desk/dmcmd-e129.txt`](desk/dmcmd-e129.txt)): every function on every path is the same at both ends of the line. Q136(w)'s checker on every file the session runs read **GO with no WRITE allowed**, on the Intel and on the box before the first device opened ([`desk/preflight-e129.md`](desk/preflight-e129.md), [`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)). Its table is classified from BL2 0.22.0's source (`836a4ab`). For these nine commands it agrees with the 0.18.0 audit. **The run sent no WRITE.**

| # | sent by | command (id) | class (BL2 0.18.0 source) |
|---|---|---|---|
| 1 | `ettelem config` (session start and end, each block's start and end) | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25) | READ: copies the TDP from SP RAM |
| 2 | `ettelem config` | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` (21) | READ: copies the threshold from SP RAM |
| 3 | `ettelem config` | `DM_CMD_GET_MODULE_POWER_STATE` (23) | READ: copies the power state from SP RAM |
| 4 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_FREQUENCIES` (53) | READ: PLL register reads, an SP RAM copy |
| 5 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_VOLTAGE` (32) | READ: PVT voltage monitors and two PMIC voltage registers (I2C reads; allowed by the owner's rule of 2 Nov) |
| 6 | `ettelem sample` (the 10 Hz sampler, `lib.sh`'s 1 s die reads) | `DM_CMD_GET_MODULE_POWER` (33) | READ: copies the board power from SP RAM |
| 7 | `ettelem sample` | `DM_CMD_GET_SP_STATS` (60) | READ: copies the SP's statistics, no reset |
| 8 | `ettelem sample` | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | READ: PVT temperature sensors |
| 9 | `ettelem sample` | `DM_CMD_GET_MODULE_VOLTAGE` (31) | READ: nine PMIC voltage registers (I2C reads; allowed) |
| — | `sparsity_host` (E109's `build/e109`, E78's heater `build/sparsity`) | the Master Minion's device-ops: DMA writes and reads of device DRAM, kernel launches, an abort on a 6 s overrun | the workload, not a device-management command |
| — | `et-lab-manifest`, `et-holders`, `et-who` | sysfs and `fuser` reads | open no device node |

READ: the handler writes only its response, its log line and the SP's RAM copy of the value it read. **Not sent:** the statistics reset (`DM_CMD_SET_STATS_RUN_CONTROL`, 62; no `--reset-ms`), the SP log level (67), `sptrace`, the vendor tool `dev_mngt_service` (lib.sh's drain is refused in `block_e129.sh`; it was never needed), the firmware-revisions query (14), a residency read, any governor, TDP, threshold, clock or voltage set, any reset. Every telemetry call went through `tools/claims-v3/e128/ettelem_guard.sh`. The checker's one finding, `lib.sh:154`'s forwarded arguments that could carry `--reset-ms`, is waived on its line with the reason: `block_e129.sh:95` passes the file and the duration only, and the guard refuses `--reset-ms`.

## What this cannot say

- **Which per-row event and which per-cycle one.** One A row ends TenC's read-address walk and cuts int8's A path in the same arm (Q136(c) result 6). The per-cycle half does not separate TenC's reads as such, the TIMA controls and the core.
- **V1 assumes equal per-op work in the two formats at one row.** This session's e_op difference, priced at the one-row rate, is −0.04 ± 0.62 W: centred on zero, but as wide as the effect. The bench gives both formats the same cycles and the same loop.
- **Three passes.** t(0.975, 2) = 4.303. N1 sits near the V1 line, and more passes would narrow its interval, not necessarily move its verdict.
- **R1p pools two sessions.** E124's G_op was known when A1 registered the pool. Both sessions' G_op means agree (+0.060 and +0.058 W), and G differs by 0.15 W between them (0.548, 0.702), inside R10's band.
- **RTL, not silicon.** The arm's design and the bench's readings are core-et's later revision (Erbium); the silicon's 62.0 cycles agree with it.

## Files

`e129.json`, `runs.csv`, `reduce.txt`, `reduce.log` (the primary reduction); `scored.json`, `results.md`, `score.log` (`score_e129.py`; the set-aside rule chose the primary); `e129-relaxed.json`, `scored-relaxed.json`, `results-relaxed.md` and logs (the set-aside rule's reduction, always run, not needed); `e129-dipskept.json`, `e129-auto.json` with their `scored-*`, `results-*`, `runs-*`, `reduce-*` (the two arms); `r1p.json` (A1's pooled R1); `posthoc/` (post hoc arithmetic, deciding nothing); `desk/` (the device-command audit and the preflight's section); `aifoundry1-c1/e129/p1291[0-2]/` (every pass's raw data: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `tiles/`, `config_start.json`, `config_end.json`, `manifest.txt`, `binaries.sha256`, `code.sha256`, `gen.sha256`, `configs.json`, `plan.json`, `run.log`, `block.json`); `aifoundry1-c1/e129-smoke/p12901/`; `logs/` (the session, its two config reads with their times, the queue, the preflight, the box's desk checks and dry runs, `binaries.sha256`, `anchor-t0.txt`, A1's extra-pass decision). The registration and code are in [`tools/claims-v3/e129/`](../../../../tools/claims-v3/e129/README.md).

Rerun from the repo root: `bash tools/claims-v3/e129/pipeline_e129.sh <out dir> docs/reports/data/2026-11-02-e129-int8-noissue/aifoundry1-c1/e129/p1291[0-2]` (needs `uv` for numpy), then `python3 tools/claims-v3/e129/pool_r1_e129.py --primary <out dir>/e129.json --relaxed <out dir>/e129-relaxed.json --out <out dir>/r1p.json`. Post hoc: `python3 docs/reports/data/2026-11-02-e129-int8-noissue/posthoc/posthoc_e129.py`.

## Blog sentences, each with its baseline, its card and its source

*Any line about the RTL is about its later revision (Erbium, core-et), not the ET-SoC-1's own.*

- Give int8 a single row of A, so that it runs at exactly fp32's op rate, reads its accumulator memory at one address and stages almost no A data. Its extra cost on all-zero data with nothing issued then falls from 1.57 W to 0.87 ± 0.36 W, so roughly half goes with that per-row work and half with work done every clock cycle. [aifoundry1 card 1, 600 MHz; `scored.json` › `one_row`]
- The open RTL predicted that one-row arm's timing to the cycle: 62 cycles an op in both formats, the simulation's 54.25 plus the loop's 7.75. [aifoundry1 card 1; `scored.json` › `rules.R6_cycles`]
- Pooled over seven independent passes on one card, the "int8 just runs more operations" explanation is bounded: per-op work carries at most 0.21 W of int8 zeros' 0.6 W gap (+0.06 ± 0.16 W), under half of it. [aifoundry1 card 1, E124 and E129; `r1p.json`]
- Priced at the simulation's own fitted constants, with the accumulator read left on into the float runs as the RTL does, what int8 does every cycle with one A row comes to 0.07–0.14 W; the card measures 0.87 W, six to twelve times more. [aifoundry1 card 1; `scored.json` › `rules.V2_readings`]
- A measurement design note: cutting the hot reference runs out of a pass to fit more passes made each pass two to three times slower on a cool morning, because the heater then had to bring the die back to its launch temperature before every run. [aifoundry1 card 1; `aifoundry1-c1/e129/p129*/marks.jsonl`]
