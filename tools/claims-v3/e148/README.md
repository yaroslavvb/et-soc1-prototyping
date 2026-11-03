# E148: int8's no-issue excess - two A rows turn TenC's read-address walk on while int8's A staging falls (Q138, aifoundry1 card 1)

Mon 2 Nov 2026 (week 45), Q138, lane a1c1-e148-int8-excess. **Registered before the claim and the first launch.** It answers
[section 11 of the kinds page](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 11, int8's no-issue
excess**: with nothing issued, int8's loop costs 2.11 W over idle against fp32's 0.38 W on aifoundry3 (E109), and **N = 1.57 ± 0.21 W** more than
fp32's on this card (E124's Y1; E129 1.566 ± 0.125). It builds on [Q136(c)](../../../docs/reports/data/2026-11-02-q136c-tima-bench/README.md)
(the TIMA bench: int8's loop differs from fp32's in **TenC's reads** (16 a cycle), **the TIMA controls** (about 107 register bits clocked a
working cycle), **TenTMP's staging** and **the scratchpad's 64-bit A reads**), on [E129](../../../docs/reports/data/2026-11-02-e129-int8-noissue/README.md)
(this card, this morning: one A row removes **0.70 ± 0.42 W** of N, V1 INCONCLUSIVE, with the reading of that part as "TenC's read-address walk
or int8's A path" left open) and on [E124](../../../docs/reports/data/2026-11-01-e124-int8-zeros-replicate/README.md) (this card: the frame, the
per-read ceilings). The run is [E142](../../../docs/reports/data/2026-11-02-e142-blind5-card1/README.md)'s successor on this card (E142 ended
21:35:48 PST).

## The question, and the one arm that answers it

E129's one A row cut two things at once: TenC's read-address walk (4,096 reads an op at a new address at sixteen rows, none at one) and int8's
A path (TenTMP's staging, the 64-bit A reads, 64 an op at sixteen rows, 8 at one). **Two A rows separate them.** The bench
([`desk/bench-e148.json`](desk/bench-e148.json), Q136(c)'s binary run by [`desk/bench_e148.py`](desk/bench_e148.py); its m0 and m0r1 streams are
identical to Q136(c)'s committed `counts.json`) says, per op on one minion with the row mask 0x0000:

| an op, nothing issued | `m0` int8 (16 rows) | `m0r1` int8 (1 row) | **`m0r2` int8 (2 rows)** | `m0r2` fp32 (2 rows) |
|---|---:|---:|---:|---:|
| bench cycles (card: + 7.75, E109's rule) | 310.25 → 318 | 54.25 → 62 | **86.25 → 94** | 88.25 → **96** |
| TenC reads; **at a new address** | 5,092; 4,096 | 996; **0** | 1,508; **512** | 0 (1,540 in the card's order, all at one address) |
| TenTMP writes = 64-bit A reads | 64 | 8 | **8** | 0 |
| TenA writes | 192 | 8 | 24 | 32 |
| TIMA control bits clocked (int8 enables) | 33,167 | 5,775 | 9,199 | 0 |
| TenB writes (B, both formats) | 256 | 256 | 256 | 256 |

A second, chip-wide, at the predicted rates (1,024 minions × 600 MHz × E129's one-row duty 0.9954 / the cycles), int8 − fp32 in the card's order
([`predictions-e148.json`](predictions-e148.json) › `bench_per_s_card_order`):

| a second | 16 rows | 1 row | **2 rows** | 2 rows against 1 |
|---|---:|---:|---:|---:|
| TenC reads at a new address (the walk) | 7.88 × 10¹² | 0 | **3.33 × 10¹²** | **+42% of 16 rows'** |
| 64-bit A reads into TenTMP (the A path) | 1.23 × 10¹¹ | 7.89 × 10¹⁰ | **5.21 × 10¹⁰** | **−61% of (16 − 1)** |
| TIMA control bits clocked | 6.38 × 10¹³ | 5.70 × 10¹³ | 5.99 × 10¹³ | +5.1% of 1 row's |

**So with two A rows the walk turns on (42% of its sixteen-row rate) while the A path FALLS below one row's.** The op rates of the two formats
stay within 2.1% (94 against 96 cycles), so the per-op work that cancels at one row nearly cancels here too.

**N2 = S(`m0r2.int8.zeros`) − S(`m0r2.fp32.zeros`)**, and the registered statistic **D21 = N2 − N1**, paired inside each pass beside N and N1.

## The frozen readings of D21 (`predictions-e148.json` › `readings`, printed in [`predictions-e148.txt`](predictions-e148.txt))

Each reading puts E129's measured part where it says it goes, scaled by the bench's counts a second; the 95% range comes from E129's own 95%
interval of N − N1 (0.280–1.122 W) or of N1 (0.508–1.223 W). Nothing is fitted to E148's data.

| reading | what it says | D21 = N2 − N1, W | 95% range |
|---|---|---:|---|
| **W** the walk | all of E129's N − N1 is TenC's read-address walk: × (walk at 2 rows)/(walk at 16) = 0.4225 | **+0.296** | +0.118 to +0.474 |
| **T** the A path | all of it is TenTMP's staging, its 64-bit A reads: × (2 − 1)/(16 − 1) = −0.6069 | **−0.425** | −0.681 to −0.170 |
| **C** per cycle | none of N is per-row; N1 is per-cycle work, scaled by the TIMA controls' clocked bits: N1 × 0.0506 | **+0.044** | +0.026 to +0.062 |
| reported: TenA's writes | excluded beforehand by Q136(c)'s fp32-level bound (all of fp32's events at one price buy int8 at most 0.14 W on card 1) | +0.136 | +0.054 to +0.218 |
| reported: the bench at its constants | M2, M4, I3 at card 1's scale; card order / from reset | +0.011 to +0.023 | — |

The three registered ranges do not overlap: W's lower end (0.118) lies above C's upper end (0.062), and T is negative.

## Rules (frozen in `predictions-e148.json` › `rules`; scored by [`score_e148.py`](score_e148.py))

Every statistic is computed per kept pass, paired inside the pass, then its mean and 95% t interval over passes. S is over the run's idle bracket
(E78's reduction, E129's primary: leakage 0.2414 W/°C, card 1's launch-gap dips removed).

| rule | statistic | line | verdicts |
|---|---|---|---|
| **W1** (primary) | D21 = N2 − N1 | each reading X ∈ {W, T, C}: CONSISTENT if D21's 95% interval overlaps X's frozen range, else EXCLUDED | **WALK** (W only) / **A-PATH** (T only) / **PER-CYCLE** (C only) / NONE / INCONCLUSIVE (naming the consistent set) |
| W2 | D21 | 95% lower bound > 0 | RISES (the A path is excluded as the sole per-row carrier) / NOT-RISES |
| R6 | median cycles per op, six arms | \|measured − predicted\| ≤ 2.0: m0 544 / 318, m0r1 62 / 62, **m0r2 96 / 94 (new)** | PASS / FAIL per arm |
| Y1 | N | PASS if lower ≥ 0.84 W; FAIL if upper < 0.84 W (E124's line) | PASS / FAIL / INCONCLUSIVE |
| V1 | N1 against N/2 (E129's rule, this session) | PER-ROW if N1's upper < N/2; PER-CYCLE if lower ≥ N/2 | PER-ROW / PER-CYCLE / INCONCLUSIVE |
| V1p | N1 − N/2 per pass, pooled with E129's three passes (known when this was written) | PER-ROW if upper < 0; PER-CYCLE if lower ≥ 0; ≥ 6 passes in all | as V1, or NOT-SCORED |
| T1 | N and N1 against E129's 1.566 and 0.865 W | \|difference\| ≤ 0.5 W | PASS / FAIL per cell; labels, removes nothing |

**At least 3 kept passes** for every rule (E109's minimum), else NOT-SCORED. **The set-aside rule** (`set_aside_rule`): the primary reduction
(E78's pass gates as they apply to E129's pass) carries every verdict if it keeps at least 3 passes; if it keeps fewer, the relaxed reduction
(`reduce_e148.py --relax-tie`, π's drift gate lifted) carries them if it keeps more, labelled; the relaxed one is always reported; no pass is added
after any reduction is read, and none is chosen after the fact.

**Reported with no verdict:** N − N1; each format's S(m0r2) − S(m0r1); **the two-term solve** per pass (N − N1 = p_w·walk₁₆ + p_t·ΔT₁₆₋₁ and
D21 = p_w·walk₂ + p_t·ΔT₂₋₁, giving p_w in fJ a TenC read at a new address and p_t in pJ a 64-bit A read; at W's point it returns E129's post hoc
89 fJ, [`selftest.txt`](selftest.txt) C); **N2's out-of-sample prediction** by each reading (this session's N1 + the reading's D21) against N2 measured;
every arm's D, S, rate and cycles; the leakage-`auto` and dips-kept arms.

**Expectations, not lines:** R6 PASS ×6 (E129 matched the bench to the cycle at one row; two rows are a new schedule test), Y1 PASS, T1 PASS.
W1 has no single expectation: E129's post hoc arithmetic put the walk as the likelier per-row carrier (the A path would need 5.7 pJ a 64-bit read,
far above the 0.61 pJ fp32's own level allows a scratchpad read on this card), which predicts WALK; Q136(c)'s TIMA controls at the cards' issue
price predict PER-CYCLE. With E129's per-pass spread of N1 (0.144 W), 3–4 passes give D21 a 95% half-width of roughly 0.25–0.45 W, so
INCONCLUSIVE between W and C is a likely outcome; T would be excluded by a D21 above about −0.17 + that half-width.

## What is reused unchanged, and what changes

E129's harness, every change marked E148 in each file: E78's runner `run_e78.py`, `e78_common.py`, reducer `reduce_e78.py`, `kinds.json` and its
fp32 and int8 zeros tiles; `lib.sh`; E109's binary `sp109/` (built on aifoundry1 into `build/e109` for E124, run by E129); E128's telemetry
allow-list `e128/ettelem_guard.sh`; Q136(w)'s checker `dmcmd_audit.py` and its table. Their sha256 (E129's 20 files, unchanged since E129's
freeze, and the 5 box binaries) are frozen in `predictions-e148.json` › `harness` and checked by [`check_e148.py`](check_e148.py) before any
device opens and before any reduction.

1. **The arm.** E129's `m0k8` is replaced by **`m0r2`**: two A rows, K = 16, mask 0x0000 ([`e148_common.py`](e148_common.py) › `ARMS`). The six
   items: `m0`, `m0r1` and `m0r2` on each format's zeros. **The pass is E129's**: π burn-ins ×2, π first and last, each format's zeros once in each
   of three segments, the six arms dealt round-robin with seed `E148|aifoundry1-c1|<pass>`: 14 runs. Launch at 58 °C after a 59 °C preheat, 2 s quiet,
   4 s runs on all 1,024 minions (E78's frame). The errata note (workloads/sparsity README) puts TensorFMA16A32/32 with B in the L1 scratchpad at
   risk only with **4** A rows; two rows with B in the scratchpad are outside it, as E129's one row was; nothing issues, so power is low.
2. **Live-sample stops** (E142's, copied into [`run_e148.py`](run_e148.py), which ran on this card at 20:50–21:36 PST today): the newest line of
   the running sampler's file is read before every launch and every 0.1 s while waiting, and by an in-run watcher every 0.1 s that writes the STOP
   file the host program checks before every launch; **board_w ≥ 66 W** or **any minion-shire reading ≥ 72 °C** ends the pass (E142's; E129's
   session peaked at 59.38 W and 60 °C), plus run_e78's die cap `--max-c 72` (E129's was 78). **The stop path is tested before the smoke**
   (`block_e148.sh 14802 --stoptest`, no launch: the die stop at 1.0 °C, the board stop at 1.0 W, and the watcher at 1.0 W must each end with exit 6
   and a STOP line read from a live sample); anything else and no smoke or pass runs.
3. **Passes and the budget.** Passes **14810–14819** in order, smoke **14801**, stop test **14802**. **At most 40 card-minutes**, counted from the
   session's first config read to its last: [`queue_e148.sh`](queue_e148.sh) starts a pass only if now + projected ≤ T0 + 2,400 − 150 s and its end
   is before **23:45 PST**; projected is 600 s (E129's passes took 536–663 s) until a pass ends, then the longest measured. **No session starts after
   23:00 PST** ([`session_e148.sh`](session_e148.sh) refuses); every run ends by 23:50 PST.
4. **The scorer** ([`score_e148.py`](score_e148.py)) and the predictions ([`make_predictions_e148.py`](make_predictions_e148.py)) are new;
   [`selftest.txt`](selftest.txt): A, the bench's m0/m0r1 counts identical to Q136(c)'s; B, the scorer on E129's reduction with synthetic m0r2 items at
   each reading's point returns that reading's verdict (WALK, A-PATH, PER-CYCLE); C, the two-term solve at W's point gives 88.9 fJ (E129's post hoc
   89). The reducer ([`reduce_e148.py`](reduce_e148.py), E129's wrapper) ran mechanically on a renamed copy of E129's pass 12910 at the desk.

## Device commands sent

Every command the run sends to card 1, classified from the source of its running build: release 1.4.0, **BL2 0.22.0**, et-platform **`836a4ab`**
(the version-matched revision of Q136(w)'s table and E129's dated note C1; E142's audit of the same command set, today). Q136(w)'s checker on
every file the session runs reads **GO: 32 send sites, 0 disallowed, no WRITE allowed** ([`dmcmd-audit.txt`](dmcmd-audit.txt), from
[`preflight_e148.sh`](preflight_e148.sh)); the session runs it again on the box and opens no device unless it reads GO.

| # | sent by | command (id) | class (BL2 0.22.0, `836a4ab`) |
|---|---|---|---|
| 1 | `ettelem config` (session start and end, each block's start and end) | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25) | READ: `thermal_power_monitor.c:339` → `thermal_pwr_mgmt.c:613`, a copy from SP RAM |
| 2 | `ettelem config` | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` (21) | READ: `:438` → `:665`, SP RAM |
| 3 | `ettelem config` | `DM_CMD_GET_MODULE_POWER_STATE` (23) | READ: `:48` → `:551`, SP RAM |
| 4 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_FREQUENCIES` (53) | READ: `performance.c:41` → `io_pll.c:907-960`, PLL register reads |
| 5 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_VOLTAGE` (32) | READ: `thermal_pwr_mgmt.c:1142`, PVT reads and two `pmic_get_voltage` I2C register reads (allowed, the owner's rule of 2 Nov) |
| 6 | `ettelem sample` (the 10 Hz sampler; `lib.sh`'s 1 s die reads) | `DM_CMD_GET_MODULE_POWER` (33) | READ: `:984`, SP RAM |
| 7 | `ettelem sample` | `DM_CMD_GET_SP_STATS` (60) | READ: `performance.c:404` → `thermal_pwr_mgmt.c:2780`, SP RAM, no reset |
| 8 | `ettelem sample` | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | READ: `:732`, PVT sensor reads |
| 9 | `ettelem sample` | `DM_CMD_GET_MODULE_VOLTAGE` (31) | READ: `:1010`, nine `pmic_get_voltage` register reads (allowed) |
| — | `lib.sh:154` forwarded arguments (a possible `--reset-ms` = `SET_STATS_RUN_CONTROL`, 62) | WRITE, conditional: **never sent** (the reviewed exception: `block_e148.sh:104` passes the file and the duration only; the guard refuses `--reset-ms`) |
| — | `lib.sh` `drain_mgmt` (`dev_mngt_service`) | **never sent**: replaced by a refusal in `block_e148.sh` |
| — | `sparsity_host` (E109's `build/e109`; E78's heater `build/sparsity`) | the Master Minion's device-ops: DMA, kernel launches, an abort on a 6 s overrun: the workload, not a device-management command |
| — | `et-lab-manifest`, `et-holders`, `et-who` | sysfs and `fuser` reads; open no device node |

**The run sends no WRITE.** Not sent: the statistics reset, the SP log level (67), `sptrace`, `dev_mngt_service`, the firmware-revisions query
(14), a residency read, any governor, TDP, threshold, clock or voltage set, any reset.

## Protocol

1. **Desk, before this commit:** the bench run and its identity check; `make_predictions_e148.py`; `selftest_e148.py` (PASS); the preflight (GO);
   `bash -n` of every script; the reducer's mechanical run. **On the box, before the claim:** the files synced into `~/nekko`, `check_e148.py`,
   `preflight_e148.sh` GO, `bash -n`, a stub run of `queue_e148.sh`, `V3_DRY=1` of the stop test, the smoke and pass 14810.
2. This registration committed and pushed; then the claim, by rewriting the day's one card post in `#community-lab` (message
   `1566837317765963987`) to the clauses held now plus `using aifoundry1 card 1 for 1 h, until ~HH:MM PST [doc](…)`, under the discord lock with
   `EXPECT_TEXT`; never while another of our clauses holds aifoundry1.
3. [`session_e148.sh`](session_e148.sh), detached on aifoundry1 (`setsid nohup`, `E148_T0` = the launch): the 23:00 gate; `check_e148.py`; the
   preflight; `et-who`; the opening `ettelem config` under card 1's lock (`ET_DEVICES=1`, `timeout 10`, through the guard); the stop test (14802)
   and its gate; the smoke (14801: seven items, 2 s runs, no preheat) and its gate ([`smoke_gate_e148.py`](smoke_gate_e148.py), E109's rule); the
   queue; the closing config read; `et-who`.
4. The release by rewriting the day's post; the data collected to the Intel ([`collect_e148.sh`](collect_e148.sh)), reduced and scored with
   [`pipeline_e148.sh`](pipeline_e148.sh), data in `docs/reports/data/2026-11-02-e148-int8-excess/`.

**Stops:** `build/e148/STOP`; the live board and die stops above; another user's device process, a device node or this card's lock held by anyone
else (exit 3, no retry; another user's idle login does not block, D1 for `aifoundry1-c*`); a failed pass. **No power cycle and nothing that risks
one:** nothing issues in the arms, no random anchor runs, E78's heater (2 s fp32 random launches, about 59 W at the board in E129) is the hottest run.
**Nothing is set.**

## What a result does to predicting power and heat

The term under test is int8's no-issue excess, the part of an int8 matmul's power that is there whatever the data and whether or not anything
issues: 1.57 W on this card at sixteen rows. A power model must say how it scales with the shape of the op. **WALK** makes it a price per TenC read
at a new address (about 89 fJ, the two-term solve), so it scales with the number of distinct C rows an op walks a second: a model can then predict
int8's floor for any shape from the bench's walk count. **PER-CYCLE** makes it a constant per int8 working cycle (about 0.87 W at the one-row rate),
whatever the shape. **A-PATH** makes it a price per 64-bit A read. Before E148, the per-row/per-cycle split of N is INCONCLUSIVE (E129 V1) and no
model term carries it; the out-of-sample test here is N2, a shape no model was fitted on, predicted by each reading before the run (N1 + D21) and
scored against the card. Heat follows power through the card's die rise per board watt (M7's H2, 0.1151 °C/W on card 1); at these 1–2 W
differences that is 0.1–0.2 °C, below what the 4.5 s readout resolves, so E148 scores power only.

## Amendments

None yet. Any departure is a dated amendment written before the data it touches.
