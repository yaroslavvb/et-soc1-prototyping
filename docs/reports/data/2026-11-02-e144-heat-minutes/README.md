# E144: heat over minutes on aifoundry3 card 0 - run blind on a new day, Q138(t)'s frozen step response follows the die through two 13-minute holds to 0.18 and 0.04 °C rms and predicts both plateaus from planned power to within 0.15 °C (every registered (a) and (b) verdict PASS; (c) PASS or, as note N1 expected, INCONCLUSIVE); M6 reads the same plateaus 23-28% low

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
item **9**, the heat over minutes (the die's step response, with one long-hold session per card until now), and item **8**, a plateau's
second session on a card. Also step (2) of "After Q137, the next steps in order". Mon 2 Nov 2026 (week 45), Q138.
- **Model:** Q138(t)'s frozen chain, [`docs/reports/data/2026-11-02-q138t-heat-model/`](../2026-11-02-q138t-heat-model/README.md) with
  amendment A1 at `c2f9920d` (20:32:38 PST), scored by its own `score_e144.py`, unchanged.
- **Pre-registered** in `13799873` (pushed 22:35:14 PST), before the claim (22:36:26) and before any device access (22:36:51):
  [`tools/claims-v3/e144/README.md`](../../../../tools/claims-v3/e144/README.md). Its note N1 (`8d396e2c`, 22:44:49) came before
  any hold's data.
- **Card:** aifoundry3 card 0, 600 MHz in all 27,065 samples. `ettelem config` was read at the session's start (22:36:51), at both ends
  of the smoke and the pass, and at the session's end (23:23:39). Every read gave TDP 0 W, threshold 65 °C, max_power, 600 MHz,
  523 mV. Nothing was set.
- **Every device-management command sent was a read**, nine kinds. One kind, `GET_ASIC_VOLTAGE`, includes PMIC voltage-register reads,
  which the owner's rule of 2 November 2026 allows. Command 74 group 0, the per-sensor reading, was classified READ from the held
  patch source before the first launch (§ Device commands sent).
- **Card session** 22:36:51–23:23:39 PST, **46.8 card-minutes**, inside 80: the probe, the smoke with its five stop tests, and one
  measured pass, 14420.
- **The registered subset.** The round's gates left no room for the full 75.9-minute design.*

**In plain words.** Q138(t) froze a model of how this chip's die warms over minutes. It is a chain of five heat stores between the
board's watts and the die, closed through the leakage that rises as the die warms. Before E144 it had been checked only inside the one
session it was fitted on. E144 ran it blind on a new day, from the card's own rest:
- **13 minutes of fp32 random numbers, duty-cycled (H_H).** Given the board's watts, the model follows the die to **0.18 °C rms**.
  From the planned work alone (E78's switching watts × when the launches ran), it puts the plateau **0.15 °C** too high, and every
  checkpoint from one minute on within 0.32 °C.
- **13 minutes of int8 −1s (H_L).** The die follows to **0.04 °C rms**, and the planned-work plateau is off by **0.01 °C**. That holds
  although this hold started on the first hold's cooling tail.
- **The previous model, M6,** reads the same two plateaus **4.2 and 1.0 °C low** (28% and 23%), because it has no leakage loop.

## Results

**Verdicts, Q138(t)'s frozen rules applied by its scorer** (`scored.json` › `verdicts`):

| hold | (a) heat model alone | (b) full chain from planned power | (c) per board W | (c) t63 | (c) linearity H_H/H_L |
|---|---|---|---|---|---|
| **H_H** fp32 random, 3.20 s every 7.56 s | **PASS** | **PASS** | **PASS** | not registered (duty-cycled) | **INCONCLUSIVE**: 1.091 (the model's own reading 1.105, note N1) |
| **H_L** int8 −1s, back to back | **PASS** | **PASS** | **INCONCLUSIVE**: 0.795 (the model's own reading 0.793, note N1) | **PASS** | |

**The numbers** (`scored.json` › `holds`; the model's own (c) readings are `e144.json` › `reported_model_reading`):

| hold | rest die before it (34-sensor mean, last 120 s) | (a) rms / plateau error / max abs | cool-down rms | M6 (a) rms / plateau | (b) plateau rise, measured vs predicted | (b) worst checkpoint from 60 s | M6 (b) plateau | (c) per board W, last 300 s [interval] |
|---|---|---|---|---|---|---|---|---|
| **H_H** (share 0.4563, A1's 0.4571) | 51.220 °C (firmware 50.0) | **0.182** / **+0.015** / 0.72 °C | **0.062 °C** over R1's 540 s (PASS ≤ 0.60) | 0.650 / −0.223 °C | **14.997 vs 15.148 °C (−0.150)** | −0.317 °C | 10.779 °C (+4.219) | **0.8675** [0.854, 0.881]; the model's own 0.876 |
| **H_L** (share 0.9655) | 51.646 °C (firmware 50.92) | **0.037** / **−0.032** / 0.16 °C | 0.118 °C over R2's 120 s (PASS) | 0.372 / +0.198 °C | **4.254 vs 4.242 °C (+0.012)** | +0.054 °C | 3.274 °C (+0.980) | 0.7952 [0.599, 0.991]; the model's own 0.793 |

- **(b)'s trajectory, measured vs predicted rise over the rest, in °C.** H_H's prediction sits 0.2–0.3 °C high from 1 to 3 minutes and
  then closes:

  | hold | 10 s | 30 s | 60 s | 2 min | 3 min | 5 min | 7.5 min | 10 min | end |
  |---|---|---|---|---|---|---|---|---|---|
  | H_H | 3.07 vs 3.03 | 4.75 vs 4.83 | 6.58 vs 6.81 | 9.32 vs 9.61 | 11.11 vs 11.43 | 13.26 vs 13.51 | 14.46 vs 14.66 | 15.02 vs 15.15 | 15.08 vs 15.23 |
  | H_L | 0.77 vs 0.76 | 1.31 vs 1.33 | 1.94 vs 1.94 | 2.82 vs 2.78 | 3.35 vs 3.30 | 3.88 vs 3.87 | 4.17 vs 4.14 | 4.24 vs 4.24 | 4.31 vs 4.30 |

- **The frozen subset's plan numbers** (`predictions-e144.json` › `aifoundry3.subset`, written for a 50.6 °C rest), read beside
  (b) and reported only:
  - H_H: 15.006 °C against a measured 14.997 (−0.01). Its checkpoints are within 0.26 °C.
  - H_L: 4.209 °C against a measured 4.254 (+0.05). Its checkpoints are within 0.06 °C.
  - The scorer's own `b_plan_f5473428` reading compares against the full design's holds, H_H 14.71 and H_L 4.61 °C from a fresh rest.
    It reads PASS for both (+0.29, −0.36 °C), but for the subset the subset's numbers above are the like-for-like ones.
- **(c) t63 on H_L:** 107.8 s against the closed loop's 110.4 s, a ratio of 0.977 (PASS; the model's own reading on this session is
  111.4 s). H_H is duty-cycled, so it has no registered t63.
- **(c) per board W, as note N1 expected:**
  - H_H reads 0.8675 against the frozen R of 0.8695 (PASS).
  - H_L reads 0.795, under the 0.80 PASS edge. H_L started on H_H's tail, and the model's own reading of this session is 0.793. It is
    INCONCLUSIVE, not a miss.
  - The linearity is INCONCLUSIVE for the same reason: 1.091 measured against the model's own 1.105.
- **Not tested:** the registered replicate of E97's H1 (int8 full at 600 s over 0.898). It belongs to the full design, which did not run.

**The card's conduct** (`e144.json` › `pass`):
- **Sampler:** 27,065 lines over 2,706 s, every one with 34 sensors and status 0. No gap over 0.5 s, nothing on stderr.
- **Peaks:**
  - firmware die reading 67 °C (the launch gate is 70);
  - 34-sensor mean 68.14 °C (the hold line is 72);
  - board 56.69 W (the line is 65).
- **No stop fired:** no watcher mark, no gated launch, no decision, every launch's exit code 0.
- **H_H:** 103 launches, 824 dispatch records, 546.0 cycles per op.
- **H_L:** 105 launches, 1,659 records, 318.0 cycles per op. Every record ok.

## What it does to predicting power and heat

**The term tested.** Q138(t)'s time-resolved heat path on aifoundry3 is a five-stage Foster chain from board watts to the die. Its
total R is 0.8695 °C per board W. About 13% of the rise arrives in 2 s, 56% in a minute and 95% in five, and the open-loop t63 is
79 s. For arm (b) the chain is closed through E97's idle law (leakage) and fed by E78's switching watts × the launch pattern.

Before E144 the chain was measured only inside E97's session. E144 is its first score on a different day, from that day's own rest,
with nothing refitted.

| | before E144 (Q138(t): `cv-q138t.json`, `amendment-a1.json` › `A1_7_before_after`, README C2) | after: E144, blind (`scored.json`) |
|---|---|---|
| heat model alone, the die over a long hold (arm a) | leave one E97 hold out: **0.47–0.66 °C rms**, plateau −0.40 to +0.82 °C. Trained on E89 alone and scored on E97: 0.46–1.50 °C rms | **0.18 °C (H_H) and 0.04 °C (H_L) rms**; plateaus +0.02 and −0.03 °C |
| full chain from planned power (arm b) | E97's plateaus read 0.33–1.04 °C low, in sample | **plateaus −0.15 °C (H_H) and +0.01 °C (H_L)**; worst checkpoint 0.32 °C |
| cool-down after a hold | leave-one-out 0.12–0.33 °C rms | 0.06 °C (H_H, 540 s), 0.12 °C (H_L, 120 s) |
| per board W over the last 300 s (arm c) | E97: 0.877–0.921; the chain 0.870 | 0.868 (H_H) |
| **M6 as frozen**, the comparison arm | (a) 0.31–0.91 °C, in sample; (b) E97's plateaus 29–33% low | (a) 0.65 and 0.37 °C rms; **(b) plateaus 4.22 °C (28%) and 0.98 °C (23%) low** |

**For prediction, this means:**
- **Heat over minutes on aifoundry3 is now predicted blind to a few tenths of a degree**, over the whole trajectory and not only its end.
  Given the board trace, the error is 0.04–0.18 °C rms. From the planned work alone, the plateau is within 0.15 °C and the trajectory
  within 0.32 °C.
  - That is below the 0.3–0.8 °C the plateau moved within E97's single session, which Q138(t) set as every band's floor.
  - It is below the chain's own within-session leave-one-out error.
  - This session's room, with a rest die of 51.2–51.6 °C, did not move the plateau by anything near that.
- **The planned-power route works on a new day.** E78's per-kind switching watts × the launch pattern, closed through the leakage
  law, puts both plateaus within 0.15 °C. M6's long-hold rule has no leakage loop and misses them by 23–28%, close to the 29–33% by
  which it missed E97's. The measured board rise over the planned switching watts shows where the gap comes from:
  - H_H: 17.29 W against E78's 26.701 W × 0.4563 = 12.18 W;
  - H_L: 5.35 W against 4.176 W × 0.9655 = 4.03 W.

  That is 25–30% of the board's rise. It is the temperature-dependent power of E97's idle law, mostly the leakage the warming die
  draws, which the closed loop carries and M6 leaves out.
- **Item 8 gets a second-session plateau on this card**, through the chain: fp32 random reads 0.868 °C per board W against the frozen
  0.8695 (E97: 0.877–0.921). The int8-full replicate of E97's H1 was not in the subset and stays open.
- **Power is not tested here.** The holds use E78's frozen switching watts as inputs to arm (b). That they reproduce the die's
  plateau to 0.15 °C is indirect support that those watts, × the recorded duty, are right on this card, at 0.4563 and 0.9655 of the time.

## Registered against what happened

| registered ([`tools/claims-v3/e144/README.md`](../../../../tools/claims-v3/e144/README.md)) | what happened |
|---|---|
| Pre-registration committed and pushed before the claim, with Q138(t)'s A1 commit on origin first | `13799873` was pushed 22:35:14 PST. `c2f9920d` (20:32:38) is its ancestor, and Q138(t)'s directory did not change after it. The claim was saved 22:36:26. The first device access, the session-start config read, was 22:36:51 |
| Note N1 written before any hold's data | `8d396e2c` was pushed 22:44:49. H_H's first launch was 22:46:34 |
| The registered subset, since the gates leave no room for the full 75.9-minute design | It ran as registered: R0 480 s (from 22:38:34), H_H 780 s (from 22:46:34), R1 540 s, H_L 780 s (from 23:08:34), R2 120 s. The pass ended 23:23:34 |
| H_H at 3.20 s every 7.56 s if the rest die before it is ≤ 51.5 °C | The rest die over R0's last 120 s read **51.22 °C** (firmware 50.0 °C), so H_H ran as planned. H_H' did not run. The realized share was 0.4563 at a 7.56 s period |
| The rest die recorded before each hold | H_H 51.220 °C (firmware 50.0); H_L 51.646 °C (firmware 50.92), as `rest_die` marks |
| Stops on live samples, every path tested in the smoke | **All five stop tests passed** in smoke 14401 (block 22:37:01–22:38:18). The sample-to-reaction latencies were 0.012–0.084 s:<br>- the gate at 1 °C gave 0 launches;<br>- the hold's die line at 1 °C ended the hold with 0 launches, and so did its board line at 1 W;<br>- with a board line 4 W over the idle, the watcher read 49.44 W 0.28 s into the launch, and the launch ended at 0.75 s with 2 dispatch records (a full one is about 3.7 s and 8 records);<br>- the session line at 1 °C gave exit 6.<br>In the measured pass no line was reached |
| The probe: command 74 group 0 must return raw codes | Three ticks at 22:36:51: status 0, 34 sensors, codes 1914–1956 at a 50 °C firmware reading (`logs/probe.out`) |
| Scored with `score_e144.py a3 <pass dir>`, no refit, no tuning | `tools/claims-v3/e144/reduce_e144.py` runs it unchanged into `scored.json`, and writes `e144.json` with the conduct, the subset's plan numbers and the model's own (c) readings, which are reported only |

## Device commands sent

The list and its classes were registered before the first launch (`tools/claims-v3/e144/README.md`, "Device commands sent").
`tools/claims-v3/dmcmd_audit.py`, run through `preflight_e144.sh`, reads:
- on the box, before any device opened (`logs/dmcmd-preflight.txt`): **GO**, 38 send sites, 0 disallowed, no WRITE allowed;
- against Q136(w)'s stock table with no exception (`tools/claims-v3/e144/dmcmd-audit-bare.txt`): NO-GO at exactly two sites. One is
  command 74, which is UNCLASSIFIED there. The other is lib.sh:154, start_sampler, which is never called.

| command | sent by | class | source (et-platform 836a4ab unless stated) |
|---|---|---|---|
| `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL`, `…_TEMPERATURE_THRESHOLDS`, `…_POWER_STATE` | `ettelem config` through E128's guard (config only): session start, both ends of the smoke and the pass, session end | READ | thermal_power_monitor.c:339/438/48 → thermal_pwr_mgmt.c:613-617/665-669/551-555, RAM |
| `DM_CMD_GET_ASIC_FREQUENCIES` (53) | `ettelem config`; `pvt_sample.py` at 10 Hz | READ | performance.c:41 → perf_mgmt.c:276 → io_pll.c:907-960, PLL register reads |
| `DM_CMD_GET_ASIC_VOLTAGE` (32) | `ettelem config`; `pvt_sample.py` | READ (two PMIC voltage-register reads, allowed by the owner's rule of 2 Nov 2026) | thermal_power_monitor.c:192 → thermal_pwr_mgmt.c:1142-1222 → pmic_get_voltage |
| `DM_CMD_GET_MODULE_POWER` (33) | `pvt_sample.py` | READ | thermal_power_monitor.c:142 → thermal_pwr_mgmt.c:984-988, the SP's RAM copy |
| `DM_CMD_GET_SP_STATS` (60) | `pvt_sample.py` | READ | performance.c:404-466 → thermal_pwr_mgmt.c:2780-2784, RAM, resets nothing |
| `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | `pvt_sample.py` | READ | thermal_power_monitor.c:545 → thermal_pwr_mgmt.c:732-773 → pvt_controller.c:618-643, 659-664 |
| **`DM_CMD_GET_ASIC_PVT_SAMPLES` (74), group 0 only** | `pvt_sample.py` at 10 Hz (27,816 ticks in the smoke and the pass), and its three-tick probe | **READ, classified by E144 from the held patch source** | the maintainer's command-74 patch of 7 Oct 2026 (held by the lab, not public): group 0 → the stock `pvt_get_min_shire_ts_sample` (pvt_controller.c:651-665) → `pvt_get_ts_data` (:618-643), two register reads per sensor, no write |
| not sent | — | — | `DM_CMD_SET_STATS_RUN_CONTROL` (no `--reset-ms`; the guard refuses it), command 74's group 6 (the latch reset, a WRITE; the sampler refuses every group but 0 and 4), the firmware-revisions query, any residency read, any `DM_CMD_SET_*`, any governor, TDP, threshold or clock set, any reset, power cycle, PCIe, driver, firmware or OTA work, and `dev_mngt_service` (lib.sh's drain is replaced by a refusal) |

**Command 74 group 0's residual.** The running build is not hashed. Since 31 Oct its group 0 returns raw 12-bit codes, where the held
patch converts them to whole degrees, so the classification rests on the nearest held source with a known divergence. That is the
standard Q136(w)'s table applies to every aifoundry3 command. Both held forms of that read path read the same two PVT registers
(`sdif_data`, `smpl_hilo`) per sensor and write none.

## Card and post

- **Card:** aifoundry3 card 0 is free. `et-who` at 23:23:39 read "No process holds an ET-SoC-1 device node or card lock", and no
  E144 process is left. The session-end config is identical to the session-start read. Nothing was set.
- **Post:** the day's one `#community-lab` post (message `1566837317765963987`) was rewritten under the Discord lock with EXPECT_TEXT,
  dry run first, then saved and read back:
  - **The claim** was saved 22:36:26 PST. It appended `; using aifoundry3 for 1 h, until ~23:40 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`
    to the clauses then held (aifoundry2 until ~23:30, aifoundry1 card 1 until ~23:11).
  - **The release** was saved 23:27:07 PST, after the data commit `ca979517` (23:26:39). By then the post named aifoundry3 alone,
    because the other two clauses had been dropped at their releases. So ` — released` was appended with every word kept:
    `<ai> **Claude says:** using aifoundry3 for 1 h, until ~23:40 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released`.

## Departures

- **D1, the subset** (registered before the claim, not a departure from the registration): the full 75.9-minute design did not
  run, so H_M and its replicate rule were not tested.
- **D2, H_L's cool-down** covers R2's 120 s, not 540 s, because the subset's last rest is 2 minutes. It is reported as the scorer
  reads it (0.118 °C rms).
- Nothing else departed from the registration.

## Files

| file | what |
|---|---|
| `scored.json` | the frozen scorer's output: `score_e144.py a3 aifoundry3/e144/p14420` (Q138(t) at A1, unchanged) |
| `e144.json` | from `reduce_e144.py`. Per hold: launches, dispatch records, share, gates, stops. Also the rest die before each hold, the sampler's health, the peaks, the clock, the config reads, the smoke's stop tests and, reported only, the model's own (c) readings and the subset's plan numbers beside the measured rises |
| `aifoundry3/e144/p14420/` | the measured pass: `telemetry.jsonl.gz` (10 Hz, 34 raw codes a line), `marks.jsonl`, `runs.jsonl` (one record a dispatch), `run.log`, `configs.json`, `config_start.json`/`config_end.json`, `block.json`, `manifest.txt`, `code.sha256`, `gen.sha256` |
| `aifoundry3/e144-smoke/p14401/` | the smoke plan and the five stop tests. Its `STOP` and `HOLDSTOP` files are the tests' own |
| `logs/` | the box's setup checks (`sha256-setup.txt`, `dmcmd-preflight.txt`, `dry-subset.log`), `probe.out`, `smoke.log`, `queue.log`, and the session's config reads (`config-session-start.json`, `config-session-end.json`) |
| [`tools/claims-v3/e144/`](../../../../tools/claims-v3/e144/README.md) | the registration and its scripts: runner, block, session, queue, preflight, audit table, collect, reduce |

Reproduce from the lab repo's root with `python3 tools/claims-v3/e144/reduce_e144.py docs/reports/data/2026-11-02-e144-heat-minutes`.
It needs numpy, for the scorer.
