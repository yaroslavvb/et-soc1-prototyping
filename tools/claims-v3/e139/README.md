# E139: E132 again with more passes - the memory path's encoded part, settled or not (Q137, aifoundry3 card 0, 600 MHz)

*Pre-registered Mon 2 Nov 2026 (week 45), about 15:40 PST, on the Intel, by the Q137 lane `a3-q137` (its E139 preparation). No card was
opened for this file. Frozen at the commit that adds it, before the day's card post names aifoundry3 for E139 and before its first
launch. Changes after that go in Amendments, dated, before the data they touch.*

*It answers the kinds page's [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 10, "The memory path"**: E132 ([its data README](../../../docs/reports/data/2026-11-02-e132-memory-split/README.md)) left two of its
six registered verdicts UNRESOLVED, R3 (the encoded part at the DDR die rail) and R4 (the encoded part on the board). E139 runs E132's
design again, unchanged, with more passes, to settle them. Asked in Q137 (the owner's words of Mon 2 Nov 2026, about 15:20 PST: the goal is
to predict the power and the heat of kinds of numeric computation as accurately as possible).*

## What it does to predicting power and heat

The power model prices a kernel's memory traffic by toggled bits on two paths (E110: a 64-bit path at 0.71 pJ a toggled bit, a 256-bit path
at 2.38 pJ, or 1.15 pJ with line edges), and E132 added where the line-to-line changes are paid (R2 EDGES, `R_4` +0.310 W on the board, off
every metered rail). What is still open is **one term**: whether the DRAM bus's *encoded* bits (after read DBI) cost power of their own,
apart from the raw bits the model already counts. E132 read the residual at +0.166 W [0.121, 0.210] where 448 encoded toggles a line move
(`E448`), and +0.118 W [-0.002, +0.237] where 56 move (`E56`). If R4 reads PAYS, the model gains an encoded-toggle term (about 0.26-0.36 pJ
an encoded toggle in E132's reading) and a DRAM-bound kernel's predicted power moves by up to about 0.17 W, the size of the error the model
carries today on those images; if NONE, the term is dropped and that error is explained elsewhere. R3 says whether the same term shows on
the DDR die rail, which decides whether the model can tie it to the memory shire's supply (a rail it can read on every run) or must keep it
as a board-only residual. **For heat**, the term enters only through board power: a 0.1-0.2 W change times the card's die rise per board
watt (M6's heat term, Q137(m)), so it changes no heat prediction measurably; E139 measures no heat term. Out-of-sample error before and
after: the data README states E132's and E139's encoded residuals against the frozen +0.185 W, and the model's residual on E132's E-family
images with and without the term.

## The design: E132's, unchanged

Every image, command, binary, item, contrast, gate, arm and rule is E132's ([its registration](../e132/README.md), § 1-4). Only these change,
each marked in the scripts:

| | E132 | E139 | why |
|---|---|---|---|
| passes | smoke 13201; 13210 (warm-up) - 13216 | **smoke 13901; 13910 (warm-up), 13911 - 13918** | more headline passes; the queue's deadline decides how many run |
| images | `build/e132-gen` | **`build/e139-gen`**: E132's images byte for byte, synced from `docs/reports/data/2026-11-02-e132-memory-split/gen`, checked against `gen.sha256` (identical to `e132/gen.sha256`; checked on the Intel, 0 mismatches) | reuse, no regeneration |
| data, logs | `e132/p<pass>`, `build/e132/` | `e139/p<pass>`, `build/e139/` | |
| die stop | 78 C (`runitems.py --max-c`, its default) | **70 C** (`MF_MAX_C=70`; the PMIC-field stop with it, 80 C, which is the minion shires' average again, E132 note) | margin (the brief's section 17); E132's die mean peaked at 61 C |
| board stop | none (E132's verification, fault 3) | **65 W on any telemetry sample's `board_w`**: [`watch_e139.py`](watch_e139.py) follows the pass's own telemetry file and writes the pass's `STOP` (runitems ends the pass, exit 8) and `build/e139-STOP` (no further pass); it opens no device | a registered board stop with margin; E132's heater bursts peaked at 53.60 W ([`watchtest.txt`](watchtest.txt): 53.6 W passes, 66.2 W stops) |
| budget | 40 card-minutes, queue deadline start + 36 min | **45 card-minutes** from the session-start config read to the session-end read; **queue deadline start + 42 min, never later than 21:40 PST**; first pass estimate 270 s | the lane's budget |
| start | no session after 15:00 PST | `session_e139.sh` refuses to start after **21:00 PST**; everything ends by 21:45 PST | Q137's gates |
| reduction | `reduce.sh` | [`reduce_e139.sh`](reduce_e139.sh): E132's `reduce_e132.py` and `predictions.json` **unchanged** (sha256 in [`predictions-e139.json`](predictions-e139.json)), `--warmup 13910` | the same estimator and constants |

**How many passes.** E132's passes took 258, 251, 247, 268, 255, 263 and 239 s, plus 15 s between passes, and its session spent 141 s
from the opening config read to the first pass (smoke and gate) ([`queue.out`](../../../docs/reports/data/2026-11-02-e132-memory-split/logs/queue.out)).
A pass starts only if it ends, at the longest pass so far, before start + 42 min (2,520 s): 141 + 8 x 284 = 2,413 s, and a ninth would end
near 2,700 s. **Expected: eight passes, 13910 - 13917 (the warm-up and seven headline passes), about 41 card-minutes with both config
reads;** 13918 runs only if the passes run short. If the session starts after 20:58 PST, the 21:40 cap cuts the queue sooner.

## How E139 joins E132 (decided before any E139 data)

- **The registered primary is E139's own headline passes alone** (13911 onward, the board meter's dips removed, leakage `auto`). E132's
  passes are not in it: E139 exists because E132 left R3 and R4 unresolved, and pooling the session that prompted the rerun into its own
  test is optional stopping.
- **The registered secondary is the pool**: E132's six headline passes (13211 - 13216) with E139's, the same reducer (`e139-pooled.json`).
- **The joint reading per rule:** **SETTLED** (the class) if the primary decides it; **SETTLED ONLY POOLED** if the primary is UNRESOLVED and
  the pool decides it, always stated with the optional-stopping caveat; **CONFLICT** if the primary and E132 read opposite decided classes;
  **OPEN** otherwise. The arms (leakage 0.2936 and 0.3803 W/C; dips kept) are reported, and a verdict that moves at an arm is named.

## The two rules it settles (E132's, restated exactly)

DDR die rail (`die_mv.ddr`, `GET_ASIC_VOLTAGE`'s PVT memory-shire reading): *moves* at a mean <= -0.30 mV with the 95 % interval below 0,
*still* with the interval inside +-0.30 mV. Board: *present* with the interval above 0 (the encoded residuals), *absent* inside +-0.10 W.

| rule | test | verdicts | E132 read | frozen prediction |
|---|---|---|---|---|
| **R3** the encoded part at the DDR die rail | classes of `wl_64z`, `eh_64z`, `el_64z`, `RE64` | UNRESOLVED if `wl_64z` does not move (the raw control); OTHER if `el_64z` moves; **ENCODED** if `RE64` moves and `el_64z` is still; RAW if `eh_64z`, `el_64z` and `RE64` are all still; else UNRESOLVED. PASS if ENCODED, FAIL if RAW or OTHER | UNRESOLVED: `el_64z` -0.09 mV [-0.31, +0.13], 0.01 mV past the still band; `RE64` -0.77 [-1.02, -0.52] moves | ENCODED (E132's) |
| **R4** the encoded part on the board | `E56`, `E448` | **PAYS** (both present), NONE (both absent), AT-HIGH-RAW-ONLY / AT-LOW-RAW-ONLY, else UNRESOLVED. PASS if PAYS | UNRESOLVED: `E56` +0.118 W [-0.002, +0.237]; `E448` +0.166 [0.121, 0.210] present | PAYS, +0.185 W each (E132's) |

**R1, R2, R5 and R6** are re-tested with E132's rules and constants unchanged and reported beside E132's verdicts (all four PASSED there);
a re-test that now fails is reported as failed, and fewer than three headline passes makes every verdict UNRESOLVED, as in E132.

## Precision, before the data

[`precision_e139.py`](precision_e139.py) ([`precision.txt`](precision.txt)) takes E132's six headline passes as the truth and its per-pass
scatter as the noise. Projected 95 % half-widths: `el_64z` 0.24 mV at n = 6, **0.20 at n = 7**, 0.18 at 8, 0.13 at 13; `E56` 0.129 W at n = 6,
**0.111 at 7**, 0.098 at 8, 0.070 at 13. The chance each rule resolves the way E132's means point: **E139 alone, n = 7: R3 ENCODED 54 %,
R4 PAYS 59 %** (n = 8: 65 %, 68 %); **pooled, n = 13: 91 %, 92 %**. Both hinge on one quantity each (`el_64z` still; `E56` present); the
others resolve in every draw. So E139 alone is near a coin flip on each, and the pool is likely to settle them if E132's means hold.
[`selftest_e139.sh`](selftest_e139.sh) ([`selftest.txt`](selftest.txt)) runs `reduce_e139.sh` on E132's committed passes in place of
E139's: it reproduces E132's six verdicts and every headline contrast exactly (SELFTEST PASS). Nothing there is a measurement.

**What I expect, frozen so it can be wrong:** `E56` near +0.12 W and `E448` near +0.17 W, `el_64z` near -0.1 mV and `RE64` near -0.77 mV;
R3 ENCODED and R4 PAYS, more likely SETTLED ONLY POOLED than SETTLED; R1, R2, R5 and R6 PASS.

## Device commands sent

*The owner's rule of Mon 2 Nov 2026: every device-management command a run's harness, sampler, host program and helpers send, classified
from the firmware source of the running build, READ or WRITE; read-only PMIC voltage reads are allowed; no governor move, no power cycle.*
The sending code is E132's, unchanged (`lib.sh`, `mf/block.sh`'s one sampler call, the `ettelem` at `build/ettelem/`) plus
`session_e139.sh`'s two config reads, so the list is E132's (its registration § 5, with its two notes): classified at et-platform `836a4ab`
(BL2 0.22.0), paths under `device-bootloaders/src/ServiceProcessorBL2/`.

| # | command | sent by | at `836a4ab` | class |
|---|---|---|---|---|
| 1 | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` | `ettelem config` (session start and end) | `services/thermal_pwr_mgmt.c:613`, copies SP RAM | **READ** |
| 2 | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` | `ettelem config` | `thermal_pwr_mgmt.c:665`, SP RAM | **READ** |
| 3 | `DM_CMD_GET_MODULE_POWER_STATE` | `ettelem config` | `thermal_pwr_mgmt.c:551`, SP RAM | **READ** |
| 4 | `DM_CMD_GET_ASIC_FREQUENCIES` | `ettelem config`; `ettelem sample` | `services/perf_mgmt.c:276` -> `driver/io_pll.c:932`, PLL reads | **READ** |
| 5 | `DM_CMD_GET_ASIC_VOLTAGE` | `ettelem config`; `ettelem sample` (the DDR die rail is this reply's PVT memory-shire reading, `thermal_pwr_mgmt.c:1172`) | `thermal_pwr_mgmt.c:1142` -> `driver/pmic_controller.c:1473`, `:254` `i2c_read`: PVT reads and two PMIC voltage-register reads | **READ**, PMIC voltage reads, allowed |
| 6 | `DM_CMD_GET_MODULE_POWER` | `ettelem sample`; `lib.sh` `drain_mgmt` only after a sampler fails twice | `thermal_pwr_mgmt.c:984`, SP RAM | **READ** |
| 7 | `DM_CMD_GET_SP_STATS` | `ettelem sample` | `services/performance.c:404` -> `thermal_pwr_mgmt.c:2780`, resets nothing | **READ** |
| 8 | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | `ettelem sample`; `lib.sh` `die_c` | `thermal_pwr_mgmt.c:732`, PVT reads | **READ** |
| 9 | `DM_CMD_GET_MODULE_VOLTAGE` | `ettelem sample` | `thermal_pwr_mgmt.c:1010` -> `pmic_controller.c:1473`, nine PMIC voltage-register reads | **READ**, PMIC voltage reads, allowed |

**Never sent:** `DM_CMD_SET_STATS_RUN_CONTROL` (the statistics reset: `mf/block.sh:71` calls `start_sampler "$OUT/telemetry.jsonl"
$((MAXS + 900))` and nothing else, and no E139 file names `--reset-ms`); `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`; any residency read; any
`DM_CMD_SET_*`; no governor, TDP, threshold or clock set; no reset, power cycle, PCIe, driver, firmware or OTA work. `watch_e139.py` reads
files only. The host program (`enercat_host`, E99's) opens the ops node only (`workloads/enercat/host/main.cpp:147`); its commands go to
the master minion's runtime. Helpers opening no device node: `et-who`, `flock`, `timeout`, `ps`, `who`.

**The preflight checker** (`tools/claims-v3/dmcmd_audit.py`, committed at `32e9c109`, sha256 `f29e91ca…`, table `50168632…`) on
`tools/claims-v3/e139/` with `lib.sh`, `mf/block.sh`, `runitems.py`, `text_hash.sh`, E110's `smoke_gate_e110.py`, `reduce_e110.py`,
`make_e110.py`, `e132/reduce_e132.py` and `dp/posthoc_dips.py` ([`dmcmd-audit.txt`](dmcmd-audit.txt)): the nine READs at 26 send sites,
PMIC access on `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE` only (reads); without an exception NO-GO (exit 3) on the conditional
`STATS_RESET` at `lib.sh:154` alone (`start_sampler` forwards `"$@"`); with the reviewed exception (the call above) **GO, 0 disallowed**.

**Residuals, as for every aifoundry3 lane.** aifoundry3 runs a non-public thermal build of BL2 0.22.0 first flashed on 7 October 2026, so
each class is `836a4ab`'s handler, which that build may not share (Q136(w); E130's A1); the classes rest on it and on the reads' unchanged
behaviour since 7 October. The `ettelem` at `build/ettelem/` on the box is built from lab commit `de262730`'s source, whose `config` and
`sample` are byte-identical to the reviewed one's (E132's correction C1). **Condition:** if the session-start config read or the smoke's
telemetry comes back in another form than E132's (an error, a missing field, `since_reset_ms` other than -1, TDP other than 0 W, a threshold
other than 65 C, a clock other than 600 MHz), the list may not describe what runs: NO-GO, the session stops there.

**Verdict before the first launch: GO**, on that condition.

## How to run it (aifoundry3, in `~/aifoundry`)

    # on the Intel, after this commit is on origin/main
    rsync -a --exclude __pycache__ tools/claims-v3/e139/ aifoundry3:aifoundry/tools/claims-v3/e139/
    rsync -a docs/reports/data/2026-11-02-e132-memory-split/gen/ aifoundry3:aifoundry/build/e139-gen/
    # on the box
    bash tools/claims-v3/e139/run_e139.sh setup     # images by hash, binary, harness hashes, stop files, dry run; no card
    # -> rewrite the day's post to add "using aifoundry3 for 1 h, until ~HH:MM PST"
    bash tools/claims-v3/e139/run_e139.sh go        # detached: config, smoke 13901, gate, passes, config (CARD RUN)
    bash tools/claims-v3/e139/run_e139.sh status
    # back on the Intel: copy build/claims-v3/aifoundry3/e139/p139* to <D>/passes/ and build/e139/ to <D>/logs/, then
    PY=<python3 with numpy> bash tools/claims-v3/e139/reduce_e139.sh docs/reports/data/2026-11-02-e139-memory-split-more-passes

## Files

`README.md` (this), `predictions-e139.json` (the freeze: passes, budget, stops, joining, rules, expectation, every hash),
`queue_e139.sh`, `session_e139.sh`, `run_e139.sh` (ports of E132's), `watch_e139.py` (the board stop) and `watchtest.txt`,
`reduce_e139.sh`, `selftest_e139.sh` and `selftest.txt`, `precision_e139.py` and `precision.txt`, `dmcmd-audit.txt`, `gen.sha256`.

## Amendments

*(none yet)*
