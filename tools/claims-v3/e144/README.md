# E144 (Q138): heat over minutes on aifoundry3 card 0, scored blind against Q138(t)'s frozen step response (pre-registration)

*Written Mon 2 Nov 2026, about 22:40 PST, before E144's claim and before any E144 device access. Nothing below changes after the
first launch. A departure is a dated amendment written before the data it touches.*

*Dated note, Tue 3 Nov 2026, about 00:20 PST, after verification (desk only: no card, no device command, nothing re-run). The notes
marked "Dated note, 3 Nov" below were added then, and the text as registered is unedited. Pass 14420's `code.sha256` pins this file at
its registration text (`fcd51917…`, commit `13799873`). Note N1 (`8d396e2c`) and these notes came after it, and
`git show 13799873:tools/claims-v3/e144/README.md` gives the pinned text. Four slips here are corrected in the data README,
[§ Registered against what happened](../../../docs/reports/data/2026-11-02-e144-heat-minutes/README.md#registered-against-what-happened)
(C6): this header's "about 22:40" (the commit is 22:35:10), N1's "about 22:46" (22:44:43), § Design's "under 60 card-minutes" (73.6
from the claim to the 23:50 gate) and the order of work's "~23:50" (the claim said "~23:40").*

**What it answers.** The kinds page's section 11, items **9** (heat over minutes: the die's step response, one long-hold session per
card) and **8** (a plateau's second session on a card), [§ 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
and step (2) of "After Q137, the next steps in order".

**What it does to predicting heat.** It scores the frozen time-resolved heat term, a five-stage Foster chain from board watts to
the die (aifoundry3: R 0.8695 °C/W, t63 79 s), on a session the chain never saw:
- **arm (a)**, the heat model alone on the measured board trace;
- **arm (b)**, the full chain from the planned power: E78's S × the launch pattern, closed through E97's idle law;
- **arm (c)**, its plateaus and time constants.

Before E144 the out-of-sample error was measured only within one session (E97, leave one hold out): 0.47–0.66 °C rms. M6's
plateau-only rule used as a trajectory read 1.5–11.6 °C. E144 gives the first session-out score on long holds on this card.

*Dated note, 3 Nov (C2 of the data README): the two sentences above repeat framings that Q138(t)'s corrections C1 and C2 withdrew
before E144's claim ([Q138(t)'s README](../../../docs/reports/data/2026-11-02-q138t-heat-model/README.md), § Corrections after
verification).*
- ***C1:** the 1.5–11.6 °C arm was an instantaneous 0.9 × ΔP rule that no model made, M6 included. M6 as frozen is a four-pole step
  response. Given the board trace it read E97's holds to 0.31–0.91 °C rms, and from the planned power it read their plateaus 29–33%
  low, both in sample.*
- ***C2:** the 0.47–0.66 °C is leave one hold out inside E97's session. A session-out score did exist: the chain's form, fitted on
  E89's square waves alone (31 Oct), read E97 (1 Nov) at 0.46–1.50 °C rms. The frozen chain was fitted on E89's and E97's sessions,
  and E144 is its first score on a session it never saw.*
- *No rule, band or prediction changes.*

## Frozen inputs (not changed by E144)

Q138(t)'s directory `docs/reports/data/2026-11-02-q138t-heat-model/` as committed **with amendment A1 at `c2f9920d`** (20:32:38 PST).
`c2f9920d` is an ancestor of `origin/main`, and nothing in that directory changed after it (checked at 22:35 PST). sha256:

| file | sha256 |
|---|---|
| `predictions-e144.json` | `ae840f84bd36e80f822981913b3d44f314248669f56ff96dc2c2b61ced0a92d0` |
| `model-q138t.json` | `268b47fd580b330738eb3e1c83ea392f3784aae348a658e7335b734a1168e8fa` |
| `amendment-a1.json` | `a147f40c5225e6d213f6f907dae652961f2b7ae784fe56747dbf6d22b5726240` |
| `score_e144.py` | `0569c49474da4058de4ad14c13d1081fa50ba2e7dd705d4a564835d94c2e1494` |
| `heat_q138t.py` / `fit_q138t.py` / `predict_e144.py` | `9dbb288f…` / `0f21f77c…` / `313c6840…` |

The harness reused unchanged: `tools/claims-v3/e97/run_e97b.py` (`b62d8225…`), `e97_common.py` (`4277cf89…`, with E97's own
check of the files it reuses), `tools/claims-v3/e89/pvt_sample.py` (`c4e4aed5…`), `run_e89.py` (`32ca337d…`), `tools/claims-v3/lib.sh`
(`033d0776…`, the same on aifoundry3), `tools/claims-v3/e128/ettelem_guard.sh` (`c2c4ab76…`).

## Design: the registered subset, because of the gates

The previous aifoundry3 lane (E141) released the card at 22:10 PST. The round's gates are no new card session after 23:00 PST and
every run ended by 23:50 PST. That leaves under 60 card-minutes, so **Q138(t)'s full 75.9-minute design cannot run**. E144 runs
**the registered subset** Q138(t) names (`predictions-e144.json` › `aifoundry3.subset`, at A1's launch pattern
`amendment-a1.json` › `A1_1_launch_pattern.subset`), 44.9 card-minutes:

| step | min | kind | launch pattern | frozen (b) plateau rise | frozen (b) at 60 s / 2 min / 5 min / 10 min |
|---|---|---|---|---|---|
| R0 | 8 | rest | — | — | — |
| **H_H** | 13 | fp32 random | `--seconds 3.20` once every 7.56 s from its first launch (A1.1; share 0.4571) | **15.01 °C** (A1: 15.005), peak 67.6 °C abs at a 50.6 °C rest | 6.80 / 9.56 / 13.41 / 15.00 (A1: 6.77 / 9.53 / 13.39 / 15.03) |
| R1 | 9 | rest | — | — | — |
| **H_L** | 13 | int8 −1s | E97's natural chain (back-to-back 6.8 s launches, share 0.966) | **4.21 °C** over a rest still carrying H_H's tail | 1.95 / 2.78 / 3.84 / 4.21 |
| R2 | 2 | rest | — | — | — |

- **H_H in a warm room** (`aifoundry3.H_H_warm_room`, A1.1): the rest die before H_H is the 34-sensor mean over the last 120 s of R0.
  At most 51.5 °C, H_H runs as above. Above 51.5 and up to 53.0 °C, H_H' runs (`--seconds 2.60` every 7.98 s, share 0.3716).
  Above 53.0 °C there is no H_H: its 13 minutes are a rest, and only H_L is scored.
- **Recorded before each hold:** the rest die, as a `rest_die` mark (34-sensor mean and firmware reading, last 120 s).
- **What the subset cannot test:** H_M (int8 full), so (c)'s replicate rule against E97's H1 (item 8's second session at
  0.898 °C per board W) is not run. H_L's plateau sits on H_H's tail (the frozen subset numbers include it).

## Rules (Q138(t)'s, frozen; E144 adds none)

Scored with `python3 docs/reports/data/2026-11-02-q138t-heat-model/score_e144.py a3 <pass dir>`, no refit, no tuning:

- **(a)** heat model alone, the chain on the measured board trace, anchored on each hold's own pre-hold rest. PASS: rms ≤ 0.80 °C
  and |plateau error| ≤ 1.00 °C. FAIL: rms > 1.60 or |plateau| > 2.00. Else INCONCLUSIVE. The cool-down rms over 540 s after each
  hold is reported, with PASS ≤ 0.60 °C (R1 is 540 s; R2 is only 120 s, so H_L's cool-down is short).
- **(b)** the full chain from planned power, at the realized launch pattern from the measured rest die (A1.2). PASS: every
  checkpoint from 60 s to the end within ±1.30 °C, and the plateau rise within ±1.30 °C. FAIL: plateau outside ±2.60 °C. The
  `f5473428` plan reading is reported beside it.
- **(c)** per board W over each hold's last 300 s: PASS inside [0.80, 0.94], FAIL wholly outside [0.74, 1.00]. Linearity H_H/H_L
  inside [0.92, 1.08] PASS, outside [0.85, 1.15] FAIL. t63 for the full-duty hold (H_L) within 0.75–1.33× of the closed loop's
  t63 PASS, outside 0.5–2× FAIL.
- **M6 as frozen** (A1.6) is reported beside each arm, with no verdict of its own.

**Note N1, a reading of the frozen numbers.** Written Mon 2 Nov 2026 about 22:46 PST, during R0, before any hold's data. It changes no
rule or band. In the subset, H_L starts 9 minutes after H_H, on H_H's tail (carried in: 0.409 °C, `aifoundry3.subset.holds[H_L]`). So
the frozen model itself reads H_L's rise per board W as 0.786. That is under (c)'s PASS edge of 0.80 and inside its FAIL interval
[0.74, 1.00]. It reads the linearity H_H/H_L as 0.8608 / 0.7858 = 1.095, outside PASS [0.92, 1.08] and inside [0.85, 1.15].
- In the subset, an INCONCLUSIVE on those two (c) readings is what a correct model gives.
- E144 reports them as the scorer reads them, beside the model's own values.
- Arms (a) and (b) carry the tail in the prediction, so they are the subset's tests.

## Stops (Q138(t)'s `rules.stops`), on live samples, tested in the smoke

- No launch starts at a firmware die reading (minshire[0]) ≥ **70 °C**.
- A hold ends at any sample ≥ **72 °C** or a board reading ≥ **65 W**.
- The pass ends at ≥ **74 °C**.
- The 34-sensor mean is held to the 72 and 74 °C lines too, which is stricter, never looser.
- E97's own guards stay: a stale or absent sampler, another user on the card, a clock off 600 MHz in 5 samples, three failed
  launches.

**Live samples, never a file written at pass end (E139's lesson).** `run_e144.py`'s watcher thread reads each new line of the
sampler's live file (10 Hz) while launches run. At a hold line it writes the hold's stop file, and `sparsity_host --stop-file`
checks that file before each 0.49 s dispatch (`workloads/sparsity/host/main.cpp:574`), so the launch in flight ends.

The smoke (block 14401) tests each path on the card, with a line the idle card already meets:
- the launch gate at 1 °C: no launch;
- the hold's die line at 1 °C, then its board line at 1 W: the hold ends with no launch;
- a board line 4 W over the idle: the launch in flight is cut short;
- the session line at 1 °C: exit 6.

A failed stop test is NO-GO for the measured pass.

## Device commands sent

Classified from the firmware source with `tools/claims-v3/dmcmd_audit.py`, through `preflight_e144.sh`:
- **GO**: 38 send sites, 0 disallowed, no WRITE allowed. One reviewed exception, E141's lib.sh:154 (start_sampler is never called).
- **Bare, against Q136(w)'s stock table, no exception:** NO-GO at exactly two sites:
  - command 74, UNCLASSIFIED there;
  - lib.sh:154.
- E144's table, `dmcmd_table_e144.json` (written by `make_table_e144.py`), changes that one entry only.

| command | sent by | class | source |
|---|---|---|---|
| `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL`, `…_TEMPERATURE_THRESHOLDS`, `…_POWER_STATE` | `ettelem config` via E128's guard (config only): session start and end, each block's start and end | READ | thermal_power_monitor.c:339/438/48 → thermal_pwr_mgmt.c:613-617/665-669/551-555 at 836a4ab, RAM |
| `DM_CMD_GET_ASIC_FREQUENCIES` (53) | `ettelem config`; `pvt_sample.py` at 10 Hz | READ | performance.c:41 → perf_mgmt.c:276 → io_pll.c:907-960, PLL register reads |
| `DM_CMD_GET_ASIC_VOLTAGE` (32) | `ettelem config`; `pvt_sample.py` | READ (two PMIC voltage-register reads, allowed by the owner's rule of 2 Nov) | thermal_power_monitor.c:192 → thermal_pwr_mgmt.c:1142-1222 → pmic_get_voltage |
| `DM_CMD_GET_MODULE_POWER` (33) | `pvt_sample.py` | READ | thermal_power_monitor.c:142 → thermal_pwr_mgmt.c:984-988, the SP's RAM copy |
| `DM_CMD_GET_SP_STATS` (60) | `pvt_sample.py` | READ | performance.c:404-466 → thermal_pwr_mgmt.c:2780-2784, RAM, resets nothing |
| `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | `pvt_sample.py` | READ | thermal_power_monitor.c:545 → thermal_pwr_mgmt.c:732-773 → pvt_controller.c:618-643, 659-664, PVT register reads |
| **`DM_CMD_GET_ASIC_PVT_SAMPLES` (74), group 0 only** | `pvt_sample.py` at 10 Hz and its 3-tick probe | **READ, from the held patch source** (below) | the maintainer's command-74 patch of 7 Oct 2026 (held by the lab, not public): `pwr_svc_get_asic_pvt_samples`, group 0 → `pvt_get_min_shire_ts_sample(idx)` = public pvt_controller.c:651-665 → `pvt_get_ts_data` :618-643 |
| not sent | — | — | `DM_CMD_SET_STATS_RUN_CONTROL` (no `--reset-ms`; the guard refuses it), command 74's group 6 (the latch reset, a WRITE: the sampler refuses every group but 0 and 4), the firmware-revisions query, any residency read, any `DM_CMD_SET_*`, any governor/TDP/threshold/clock set, any reset, power cycle, PCIe, driver, firmware or OTA work, `dev_mngt_service` (lib.sh's drain is replaced by a refusal) |

**Command 74 group 0, classified against aifoundry3's non-public thermal build.** Q136(w) left it UNCLASSIFIED because its source
is not public. The lab holds the maintainer's patch that added it (7 Oct 2026).

What the held source shows:
- The handler serves group 0 (`PVT_SAMPLE_GROUP_MINSHIRE_TS`) by calling the stock `pvt_get_min_shire_ts_sample` for each sensor.
- That function makes two register reads per sensor (`ts_individual[].sdif_data` and `.smpl_hilo`) and writes nothing.
- The reply is built in a static RAM buffer.
- This is the same register path the already-classified READ `GET_MODULE_CURRENT_TEMPERATURE` uses.
- The patch's only writing form is group 6, `pvt_hilo_reset`.

**Residual.** The running build is not hashed. It differs from the held patch in at least one respect: since 31 Oct its group 0
returns raw 12-bit codes, where the held patch converts them to whole degrees. So the classification rests on the nearest held source
with a known divergence. That is the standard Q136(w)'s table applies to every aifoundry3 command. Both held forms of that read path,
the converted read and a raw-code variant of the same function, read the same two registers and write none. The empirical record
agrees but does not replace the source: E89 sent group 0 in 22,976 samples and E97 in 150,295, with no fault.

**No statistics reset** and **no PMIC write**. The compute launches (`sparsity_host`) use the ops queue, not management commands.

**Dated note, 3 Nov (C1 of the data README): one sender is missing above, lib.sh's `die_c`.**
- lib.sh's `block_begin` (lib.sh:188) and `block_end` (:196) call `die_c` (:103). It runs `$ETTELEM sample --seconds 1 --every-ms 500`
  under `timeout 20`.
- `block_e144.sh` sources lib.sh (:15) and then sets `ETTELEM` to E128's guard (:16). So these calls took the guard's sample path
  (`ettelem_guard.sh:19-31`) to the box's `ettelem`.
- They ran under the card lock at both ends of smoke 14401 and of pass 14420: four calls of about two samples each (`block.json` ›
  `die_c_start`/`die_c_end`: 50/51 and 51/52).
- Each sample sends six GETs (`tools/ettelem/ettelem.cpp:165-167`). It resets nothing without `--reset-ms` (:149, :172), which the guard
  refuses.

One of the six is a kind the table above lacks:

| command | sent by | class | source (et-platform 836a4ab) |
|---|---|---|---|
| `DM_CMD_GET_MODULE_VOLTAGE` (31) | lib.sh's `die_c`: `ettelem sample` through E128's guard, at each block's start and end | READ (nine PMIC voltage-register reads per sample, I2C reads with no write; allowed by the owner's rule of 2 Nov 2026) | thermal_power_monitor.c:243 → thermal_pwr_mgmt.c:1010-1140 (nine `pmic_get_voltage` calls) → pmic_controller.c:1473-1500 → `get_pmic_reg` :254-300 (Q136(w)'s table) |

The other five (`GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_ASIC_FREQUENCIES`) are in
the table already, from the sampler and `ettelem config`. The committed audit lists all six at lib.sh:103 (`dmcmd-audit.txt` lines
8-13) and reads GO.
- **So E144 sent ten kinds of command, every one a READ.** Two of them, `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE`, make PMIC
  voltage-register reads.
- E128's guard carried the config reads and these samples, not "config only".
- No class changes, and no write was sent.

**Dated note, 3 Nov (C5 of the data README): command 74's residual, exactly.** The held source has two forms, both of 7 Oct 2026:
- **The first:** group 0 goes to `pvt_get_min_shire_ts_sample`, which converts the codes to whole degrees, and group 6 goes to
  `pvt_hilo_reset`, a write.
- **The same day's amendment:** raw codes are served on a new group 7 (`PVT_SAMPLE_GROUP_TS_RAW`, through `pvt_get_ts_raw_data`). It makes
  the same `sdif_data` and `smpl_hilo` reads, unconverted, and writes nothing. Group 6 is no longer served.

The running build returns raw codes on group 0, so its group-0 path matches neither held form. It differs in more than "the
conversion" (above).

The committed data check the only write either form has, the latch reset:
- The 34 high latches read the same at E89's probe of 31 Oct (19:02:49 PDT) as in every hi/lo tick of smoke 14401 (16) and pass 14420
  (542).
- No low latch rose between ticks.
- A reset sets each latch to the current code: the high latches would drop and the low ones rise.

So no latch reset ran on this card through more than 200,000 group-0 reads (E89's 22,976, E97's 150,295 and E144's 27,816). That rules
out both paths: command 74's group 6, and the statistics reset, whose handler resets the latches too (performance.c:575 →
thermal_pwr_mgmt.c:2828). At 836a4ab, `pvt_get_min_shire_ts_sample` is pvt_controller.c:645-657, not 651-665. The class stays READ, with
this residual.

## Order of work

1. This directory committed and pushed, then the day's one `#community-lab` post rewritten under the Discord lock with
   EXPECT_TEXT, adding the clause `using aifoundry3 for 1 h, until ~23:50 PST`.
2. On the box: `session_e144.sh setup` (no device access: sha256, tiles, preflight, dry run).
3. Then `probe`: the session-start config read, then three sampler ticks. Raw codes must come back, else NO-GO.
4. Then `smoke`: the smoke plan plus the stop tests. All must pass.
5. Then `go`: pass 14420, the subset, detached, deadline 23:49 PST, then the session-end config read.
6. Collect, reduce with `score_e144.py a3`, and write the data README, results first, in
   `docs/reports/data/2026-11-02-e144-heat-minutes/`. Push, then drop this lane's clause from the post.

## Files

| file | what |
|---|---|
| `run_e144.py` | the runner (E97's `run_e97b.py` imported unchanged; E144's plan, A1's duty cycle, the stops and the watcher, `rest_die` marks, smoke and stop tests) |
| `block_e144.sh` | one pass as a lib.sh block (`block_e97.sh` ported: E128's guard, the drain refused) |
| `session_e144.sh`, `queue_e144.sh` | the stages on the box, and the detached measured pass |
| `preflight_e144.sh`, `make_table_e144.py`, `dmcmd_table_e144.json` | the device-command preflight and E144's audit table |
| `dmcmd-audit.txt`, `dmcmd-audit-bare.txt` | the preflight's printout (GO) and the stock table's (NO-GO at command 74 and lib.sh:154) |
| `dry-subset.txt` | the desk's dry run of the subset (V3_DRY) |
