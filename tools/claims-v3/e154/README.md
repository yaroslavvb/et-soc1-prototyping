# E154 (Q139): heat over minutes predicted end to end from the bits, on aifoundry3 card 0 - Q139(e)'s frozen holds scored on the card (pre-registration)

*Pre-registration, Tue 3 Nov 2026 (week 45), written on the Intel about 17:30-18:00 PST, before any E154 data, before the claim of aifoundry3
and before the first launch. Nothing below changes after the first launch; a departure is a dated amendment written before the data it
touches. On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**items 9** (a steady state for heat), **8** (the heat path between sessions) and **6** (the power model). It answers **rank 4 of Q138's final
critic**: "Heat over minutes predicted end to end from the computation's description ... The bits-to-M7-power-to-chain path for a new kind has
never been scored", the aifoundry3 half ("a 76-minute window on aifoundry3, which also fits the int8-full replicate of E97's H1"). E161 is the
aifoundry2 half. The owner's mandate is his words of 2 November 2026, about 18:40 PST ("settle any unanswered questions regarding horace's power
model"), with his goal of the same day: "to be able to predict the power requirement and heat generation of various kinds of numeric
computations as accurately as possible".*

## What it does to predicting power and heat

**The term tested** is the whole path from a computation's description to its die over minutes on a pinned card: the tile's bits, then M8's
switching power over idle (Q139(m), as Q139(x) computed it for this card), then Q138(t)'s frozen chain from switching watts to the die,
closed through E97's idle-leakage law. Nothing in that path has seen these four kinds run.

**The out-of-sample error before** (committed data only):
- given the measured board watts, the chain reads a 13-minute hold to 0.04-0.18 °C rms on this card (E144, blind, 2 Nov; plateaus +0.015 /
  −0.032 °C);
- from E78's measured watts for the same kinds (not the bits), E144's plateaus −0.15 / +0.01 °C;
- from the bits, only over a 4.5 s run: 0.10-0.13 °C rms (E153, M8 on pool 6, today) and 0.13-0.17 °C (M7, pool 5);
- **from the bits over minutes: never scored.** Q139(e)'s expected 95% sizes on this card: 0.60-0.69 °C for the float holds and
  0.94-1.45 °C for the int8 holds (its bands), against the critic's 0.35 °C scale (Q139(e)'s D4).

**After:** E154 measures each of the four pool-6 holds' plateau and trajectory against the frozen numbers below. The session figure, the rms of
the four plateau errors from the bits (arm E), is the first out-of-sample error of heat over minutes predicted from a computation's
description on this card; E − A per hold splits each error into the power path's part and the heat path's. A reported arm runs the same chain
on the same tiles' S as E153 measured them this afternoon (4.5 s runs), so M8's power error (M8 reads these four 0.04-0.44 W off E153's
measurement) can be followed into the die over minutes.

## The predictions, frozen elsewhere

**Every number E154 scores was frozen before this was written.** E154 adds no prediction and no fit.

| what | file | sha256 | frozen in |
|---|---|---|---|
| Q139(e)'s composition, E154's design, holds, bands and rules | [`predict_q139e.py`](../../../docs/reports/data/2026-11-03-q139e-heat-end-to-end/predict_q139e.py), [`predictions-q139e.json`](../../../docs/reports/data/2026-11-03-q139e-heat-end-to-end/predictions-q139e.json) | `0dad4370…`, `60424edb…` | `455c46c1` (06:00:48 PST) |
| its amendment A1 (corrections after verification, before E154/E161; no rule changed; K_S's plan reading +11.72 °C, K_Q's +6.09 °C on the registered machinery) | [`amendment-a1.json`](../../../docs/reports/data/2026-11-03-q139e-heat-end-to-end/amendment-a1.json) | `1e2b7abf…` | `e224a3f8` (06:51:54 PST) |
| Q138(t)'s chain, its code and its scorer | `model-q138t.json`, `heat_q138t.py`, `fit_q138t.py`, `score_e144.py`, `predictions-e144.json`, `amendment-a1.json` in [`../../../docs/reports/data/2026-11-02-q138t-heat-model/`](../../../docs/reports/data/2026-11-02-q138t-heat-model/README.md) | `268b47fd…`, `9dbb288f…`, `0f21f77c…`, `0569c494…`, `ae840f84…`, `a147f40c…` | `c2f9920d` (2 Nov) |
| M8 and its pool-6 predictions for aifoundry3 (M7's and M6's beside) | `m8.json`, [`../kinds/blind6/predictions-blind6-aifoundry3.json`](../kinds/blind6/predictions-blind6-aifoundry3.json) | `8c23aba2…`, `97247642…` | `122da8b6`, `d98d2e34` |
| blind pool 6's manifest and tiles; Q139(k)'s C check | [`../kinds/blind6/blind6.json`](../kinds/blind6/blind6.json); [`../ccheck/`](../ccheck/README.md) (`sparsity_ccheck.sh`, `ccheck.py`) | `4c4cee7b…`; `d00158d4…`, `2f806fe6…` | `d98d2e34`, `4946a992` |

`git merge-base --is-ancestor` holds for `455c46c1`, `e224a3f8`, `d98d2e34`, `4946a992`, `122da8b6` and `c2f9920d` against `origin/main`
(checked 17:46 PST), so the predictions precede this registration, the claim and the first launch. [`score_e154.py`](score_e154.py) checks the
sha256 of thirteen frozen inputs (with E153's `e153.json` for the reported arm) before it scores anything and imports `score_e144.py`
unchanged.

**The plan** (`predictions-q139e.json` › `aifoundry3.design`; numbers at a 51.2 °C room; K_S and K_Q as amendment A1's table reads them on the
registered machinery, the others as frozen):

| step | min | kind | power from the bits (S over idle, W): M8 / M7 / M6 | launch pattern | plateau rise (°C), over the carried-in tail | band 95% / FAIL beyond (°C) |
|---|---|---|---|---|---|---|
| R0 | 5 | rest (the room: the 34-sensor mean over its last 120 s) | | | | |
| **H_M** | 11 | `int8.full` (E78's tile; E97's H1 again) | 9.648 (E78, measured) | E97's natural chain | 11.02 (the replicate rule, not end to end) | 0.36 (tight reading); (b) ±1.30 |
| R1 | 3.5 | rest | | | | |
| **K_S** | 10 | `fp32.real_smol_softmax_v_causal` | 15.674 / 15.606 / 15.528 | 7 dispatches (`--seconds 3.20`) once every **4.37 s** (room ≤ 51.5 °C) or 4.97 s (51.5-53.0 °C); above 53.0 °C a rest | **11.72** (tail 3.21) | 0.599 / 1.30 |
| R2 | 3.5 | rest | | | | |
| **K_Q** | 10 | `int8.real_qwen_w8a8_v` | 9.241 / 9.239 / 9.250 | natural chain | **6.09** (tail 4.44) | 0.941 / 1.882 |
| R3 | 3.5 | rest | | | | |
| **K_L** | 10 | `int8.b_line_zero_ff` | 5.935 / 6.250 / 6.649 | natural chain | **3.54** (tail 3.06) | 1.446 / 2.892 |
| R4 | 3.5 | rest | | | | |
| **K_O** | 10 | `fp32.a_onebit_b5_third` | 11.427 / 11.373 / 11.317 | natural chain | **11.21** (tail 1.88) | 0.688 / 1.376 |
| R5 | 2.5 | rest | | | | |

The full design is 72.5 minutes; **the registered subset** (Q139(e)'s `aifoundry3.subset`) is R0, H_M, R1, K_S, R2 and K_Q, 43.0 minutes.

## What runs

**The harness is E144's** (Q139(e): "E144's runner (tools/claims-v3/e144/run_e144.py, E97's harness, --values file: tiles)"):
- [`run_e154.py`](run_e154.py) is `run_e144.py` with five marked changes: Q139(e)'s design (full or subset; rests are fixed lengths); the hold
  items (E78's `int8.full` from `kinds.json`; pool 6's four hold candidates from `blind6.json`, each checked against blind6.json's sha256 of
  the whole, of A and of B before any launch); K_S's duty from its first launch, its period set by the room rule at R0's end (a `room` mark);
  the smoke; and the stop tests on K_S's tile. It imports E97's `run_e97b.py` unchanged (its card classes, readers and guards).
- [`block_e154.sh`](block_e154.sh) is `block_e144.sh` with the runner, the C-check wrapper and the card check changed (E144's other changes kept:
  E128's guard for the two config reads, lib.sh's drain refused, E89's per-sensor sampler `pvt_sample.py` at 10 Hz).
- **The C check on every launch** (Q139(k); departure D1): `--sparsity tools/claims-v3/ccheck/sparsity_ccheck.sh` runs the C-logging host
  `build/ccheck/b/host/sparsity_host` (`99ed75fb…`, built on aifoundry3 at 06:40 PST today, the host E153 ran) with E78's kernel
  `build/sparsity/kernel/sparsity.elf` (`d521e432…`, byte-identical to the ELF the plain host E144 ran loads from `~/nekko`), with
  `--c-log <pass>/c-log.jsonl --c-poison`. So the device code is E144's; the host is E153's.
- [`session_e154.sh`](session_e154.sh), detached on the box, runs everything in order: the gates; `sha256sum -c`
  [`frozen-e154.sha256`](frozen-e154.sha256) (31 files: every reused file, E154's card files, `kinds.json`, `blind6.json`, the five tiles, the
  host, the kernel, the wrapper and `ettelem`; else exit 9, no device opened); the device-command preflight
  [`preflight_e154.sh`](preflight_e154.sh) (else exit 3); `et-who`; the session-start config read; **the smoke and the five stop tests** (block
  15401); the gate [`smoke_gate_e154.py`](smoke_gate_e154.py); **the measured pass** (block 15420) only if the gate passes; the session-end
  config read; `et-who`.

**The smoke** (block 15401, `run_e154.py --smoke --stoptest`): R0 8 s, then each of the five tiles once (H_M 5 s, K_S 9 s at 4.37 s, K_Q,
K_L, K_O 5 s each) with 2 s rests, R5 3 s; then E144's five stop-path tests on live samples on K_S's tile: the launch gate at 1 °C (no launch);
the hold's die line at 1 °C, then its board line at 1 W (the hold ends with no launch); a board line 4 W over the idle (the launch in flight
ends early); the session line at 1 °C (exit 6, read as passed). About 1.5 minutes. **The gate** passes only if: block.json ok; all five stop
tests passed; each of the five holds ran on time with launch records (K_S two), every record ok, no tensor error, 1,024 minions; a sound C log
(every host record naming the host and kernel above by sha256, at least one C record for every launch record, each poisoned, no mask, no stream,
1,024 participants); the 34 raw codes in at least 90% of the telemetry lines, their mean (E97's conversion) in [35, 75] °C and within 3 °C of
the firmware's `minshire[0]` (E144's probe: command 74 group 0 must return raw codes); 600 MHz in every line; and both config reads TDP 0 W,
threshold 65 °C, 600 MHz. A failed gate is NO-GO for the measured pass.

**The measured pass** (block 15420): Q139(e)'s design as above. The rest die before each hold is recorded (E144's `rest_die` mark: the 34-sensor
mean and the firmware reading over the last 120 s), and the room before K_S (the `room` mark at R0's end).

**Budget and gates** (section 23 of the round's brief: no new card session after 21:00 PST, every run ends by 22:00 PST; the task: "at most
76 card-minutes inside the gates, else Q139(e)'s registered subset"):
- the session starts no later than 21:00 PST (else exit 8, no device opened);
- the **full design** if the session's anchor T0 is at or before 20:40 PST, with a budget of 76 card-minutes from T0; else the **registered
  subset** with a budget of 47 (departure D3);
- the measured pass's deadline is min(T0 + budget − 60 s, 21:58 PST). The runner starts no hold with less than its length + 30 s left
  (E144's rule) and cuts a rest at the deadline, so a late session loses its last hold, never overruns. Card-minutes are counted from the
  session-start config read to the session-end one.
- Expected: the smoke block about 1.5 minutes, the pass's own overheads about 0.3 minutes, the plan 72.5: about 74.5 card-minutes for the
  full design.

## Registered rules ([`score_e154.py`](score_e154.py))

Q139(e)'s E154 rules (`predictions-q139e.json` › `rules` › `E154 (aifoundry3 card 0, 600 MHz, nothing set)`), applied as written:

- **Arm E, end to end from the bits (the primary, per pool-6 hold):** Q138(t)'s frozen chain closed through E97's idle law, from R0's measured
  rest die (34-sensor mean, last 120 s of R0), on the session's realized dispatch records (`runs.jsonl`), each on at the item's frozen S
  (`S_table_W`: M8's S for the pool-6 items) - `score_e144.py`'s arm (b) machinery (A1.2) with its S78 table extended by `S_table_W`, nothing
  else changed. Plateau = the mean rise over the hold's last 300 s over the chain's carried-in base (the anchor window: the last 120 s of the
  rest before the hold, read the same way in the measurement and the prediction: `score_e144.traj`). The trajectory = the checkpoints from 60 s
  to the end (5 s means; one cycle on K_S): 60, 120, 180, 300, 450 (and 600 where the hold is longer) and "end".
  - **PASS:** |plateau error| ≤ band_95_C **and** the checkpoints' rms ≤ band_95_C.
  - **FAIL:** |plateau error| > fail_beyond_C.
  - **Otherwise INCONCLUSIVE.**
  - band_95_C / fail_beyond_C: K_S 0.599 / 1.30, K_Q 0.941 / 1.882, K_L 1.446 / 2.892, K_O 0.688 / 1.376 °C (the frozen session table).
- **Arm A, given watts (the registered comparison arm, beside each hold):** `score_e144.py`'s arm (a) unchanged, the chain on the measured board
  trace: PASS rms ≤ 0.80 °C and |plateau error| ≤ 1.00 °C; FAIL rms > 1.60 or |plateau error| > 2.00; else INCONCLUSIVE. **E − A** on the
  plateau is the power path's share of the error.
- **M7 and M6:** their S (`aifoundry3.power_arms`), through the same chain on the same records, reported with their plateau errors and the
  verdict the same rule would give (no verdict of their own).
- **H_M (E97 H1's replicate, not end to end):** Q138(t)'s (b) from E78's S (PASS every checkpoint from 60 s and the plateau within ±1.30 °C;
  FAIL the plateau outside ±2.60) and (c) replicate: the rise per board W at 570-630 s over E97's H1 0.898, PASS inside [0.94, 1.06], FAIL
  outside [0.88, 1.12], as `score_e144.py` reads them. band_95_C 0.361 °C reported as the tight reading.
- **The session figure:** the rms of the pool-6 holds' arm E plateau errors (4 in the full design, 2 in the subset) is this card's
  out-of-sample error of heat over minutes from the bits, reported with M7's, M6's and arm A's.
- **Arm E153, measured watts for the same kinds (reported, registered here before the data):** the four tiles' S as E153 measured them on this
  card today (`e153.json` › `items` › `S` › `mean`, Q139(u)'s footing, committed `8e18eb67` at 17:25:43 PST, before this registration: K_S
  15.298, K_Q 9.043, K_L 6.378, K_O 11.463 W, against M8's 15.674, 9.241, 5.935, 11.427) through the same chain on the same records, as E144's
  (b) read E78's watts. E − E153 on the plateau is M8's power error at work over minutes; E153 − A is the chain's error from steady watts. No
  verdict of its own.
- **Reported beside, never a verdict:** the plan readings (the measured rise against the frozen session table, and against amendment A1's arm-E
  table for K_S and K_Q), the rest die before each hold, the realized share and period, the carried-in tail, each hold's peak die and board,
  M6's frozen step response on the measured trace (`a_M6`), (c)'s per board W for every hold, and the C check per step.
- **The check of C** (Q139(k)), at the desk on the Intel after collection, never on the box: `ccheck.py check` on the smoke's and the pass's
  `c-log.jsonl` (`--jobs 6`). It is a validity label, not a heat rule: a hold whose every launch reads PASS is "C verified"; otherwise its
  verdicts stand as scored and the data README names the launches whose C was not verified.
- If the room rule makes K_S a rest (room above 53.0 °C), K_S is NOT RUN and not scored, and the session figure has three holds. If the
  runner drops a hold at the deadline, it is NOT RUN, named, and the session figure is over the holds that ran.

**The scorer's self-test** (`score_e154.py --self-test`, 17:48 PST, [`logs/selftest.txt`](logs/selftest.txt)): a synthetic pass made by the
frozen model itself at the plan's pattern (amendment A1's `plan_records`) gives back A1's arm-E numbers at a 51.2 °C room (K_S 11.722 °C over
a 3.211 °C tail, K_Q 6.091 over 4.440, K_L 3.544, K_O 11.203; within 0.002 °C of the frozen table for H_M, K_L and K_O) and reads PASS on every
arm; a die offset of +0.3 °C over each hold's last 300 s reads PASS everywhere, +3.0 °C FAIL everywhere, +1.0 and +1.6 °C as the rule says
hold by hold; a warm room (52.0 °C, 4.97 s) reads PASS; ten edge cases of the verdict function read as registered.

**The dry run** on aifoundry3 (17:50 PST, `V3_DRY=1`, E97's toy card, no device opened, [`logs/dry.txt`](logs/dry.txt)): the hash check and
the preflight pass on the box; the full design runs every step (H_M 93 launches, K_S 137 at 4.37 s start to start, K_Q, K_L, K_O 85 each; 72.5
minutes of plan); the smoke runs each tile once through the wrapper, and the stop tests read as on E144's toy card (the in-launch board test
cannot trip on a toy card whose board never rises, so the dry smoke exits 1 there, as E144's would).

## Stops (Q139(e)'s for E154: Q138(t)'s, unchanged), on live samples, tested in the smoke

- No launch starts at a firmware die reading (`minshire[0]`) ≥ **70 °C**.
- A hold ends at any live sample ≥ **72 °C** (the firmware reading or the 34-sensor mean) or a board reading ≥ **65 W**.
- The pass ends at ≥ **74 °C**.
- E97's guards stay: a stale or absent sampler, another user on the card, a clock off 600 MHz in 5 samples, three failed launches.
- `run_e154.py` refuses any line looser than these.

`run_e154.py`'s watcher thread reads each new line of the sampler's live file (10 Hz) while launches run. At a hold line it writes the hold's
stop file, and the host's `--stop-file` check before each 0.49 s dispatch ends the launch in flight. The smoke tests each path on the card with a
line the idle card already meets (above). Every planned in-launch peak is at or under 67.5 °C (34-sensor mean) at its room: amendment A1 puts
K_S's at 67.40 °C (51.5 °C room, 4.37 s) and 67.35 °C (53.0 °C, 4.97 s), 4.6 °C under the hold line. The hottest tile's board: E153 read
K_S's tile at 41.20 W in its 4.5 s runs from a 58 °C die (`e153.json` › `items` › `p80`), and the leakage law adds about 2 W at K_S's 66-67 °C,
so about 43 W, 22 W under 65 W. Nothing here drives the card toward a PMIC over-power or over-temperature reset: aifoundry3's highest board
reading was 54.26 W in E153's session and 56.69 W in E144's duty-cycled fp32 random hold (pass 14420's telemetry).

## Departures from Q139(e)'s plan, dated, before any data (Tue 3 Nov 2026, 17:30-18:00 PST)

- **D1, the host is the C-logging host** (as E161's D1 on aifoundry2). Q139(e) named E144's runner, whose host is the plain
  `build/sparsity/host/sparsity_host`. E154 runs every launch through Q139(k)'s wrapper and the C-logging host, so every pool-6 launch's C is
  checked (section 22: "so every pool-6 launch is checked"; critic rank 14). The kernel is byte-identical. The C log adds one 1 MiB write
  before and one 1 MiB read after each dispatch, outside its window: E153 read a median 3 ms between dispatches and a duty of 0.9932 against
  E141's 0.9963 on this card (about 0.3%), and the wrapper's two sha256 sums add about 10-20 ms to each process's start. Arm E is computed on
  the realized dispatch records, so the share that ran is the share scored.
- **D2, the probe is folded into the smoke gate.** E144 read three sampler ticks (`pvt_sample.py --probe`) before its smoke to see that command
  74 group 0 answers raw codes. E154's gate reads the same thing from the smoke's own telemetry (the 34 codes, their mean against `minshire[0]`),
  so no separate device step runs. It saves about 20 s of the 76 minutes.
- **D3, the subset's budget is 47 card-minutes, not 45**, and only if the session starts after 20:40 PST. The frozen subset is 43.0 minutes of
  plan, and the smoke with its stop tests and the blocks' own reads take about 1.8 minutes; at 45 the runner's own rule (no hold starts with less
  than its length + 30 s left) would drop K_Q, one of the subset's two pool-6 holds. The full design stays inside 76.
- **D4, an unreadable room.** Q139(e)'s K_S rule reads the room from R0's last 120 s. If fewer than half the samples are there, K_S runs the
  warm-room period, 4.97 s (the lower peak). The rule leaves this case open.
- **D5, "S78 extended by S_table_W".** Arm E adds `S_table_W`'s four pool-6 entries to `score_e144.py`'s S78 table; `int8.full` keeps E78's own
  value (9.648347 W) rather than `S_table_W`'s rounded 9.6483, so H_M's (b) is Q138(t)'s exactly. The difference moves no prediction by more
  than 0.0002 °C.
- **D6, the stop tests run on K_S's tile** (E144 ran them on `fp32.randn`), so the smoke opens no tile outside the design.
- **D7, the checkpoints and their rms** are defined above where Q139(e)'s text leaves them open: the frozen `rise_C_by_s` keys from 60 s to the
  end that fall inside the hold (`score_e144.traj`'s, as `verdict_b` selects them), the rms over all of them with equal weight.

## Device commands sent

*His rules of Mon 2 Nov 2026 (only read-only PMIC voltage reads plus the statistics reset; every command listed and classified before a
launch), kept in Q139: every device-management command the harness, sampler, host program and helpers send, classified from the firmware source
of the running build by Q136(w)'s table with E144's one change (command 74 group 0 classified READ from the held patch source, E144's README).
`tools/claims-v3/dmcmd_audit.py` through [`preflight_e154.sh`](preflight_e154.sh) on every file the session runs or sources reads **GO: 38 send
sites, 0 disallowed, no WRITE allowed**, with one reviewed exception, E141's and E144's lib.sh:154 (start_sampler is never called; the guard
refuses `--reset-ms`) ([`dmcmd-audit.txt`](dmcmd-audit.txt), also GO on the box at 17:50 PST). Against Q136(w)'s stock table with no exception it
reads NO-GO at exactly two sites, command 74 (UNCLASSIFIED there) and lib.sh:154 ([`dmcmd-audit-bare.txt`](dmcmd-audit-bare.txt)), as E144's
did. No statistics reset is sent.*

| command | sent by | class | source (et-platform `836a4ab`) |
|---|---|---|---|
| `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25), `…_TEMPERATURE_THRESHOLDS` (21), `…_POWER_STATE` (23) | `ettelem config` through E128's guard: the session's start and end, each block's start and end | READ | thermal_power_monitor.c:339/438/48 → thermal_pwr_mgmt.c:613-617/665-669/551-555, RAM copies |
| `DM_CMD_GET_ASIC_FREQUENCIES` (53) | `ettelem config`; `pvt_sample.py` at 10 Hz; lib.sh's `die_c` | READ | performance.c:41 → perf_mgmt.c:276 → io_pll.c:907-960, PLL register reads |
| `DM_CMD_GET_ASIC_VOLTAGE` (32) | `ettelem config`; `pvt_sample.py`; `die_c` | READ (two PMIC voltage-register reads; allowed by the owner's rule of 2 Nov 2026) | thermal_power_monitor.c:192 → thermal_pwr_mgmt.c:1142-1222 → pmic_get_voltage → pmic_controller.c:1473-1500 |
| `DM_CMD_GET_MODULE_POWER` (33) | `pvt_sample.py`; `die_c` | READ | thermal_power_monitor.c:142 → thermal_pwr_mgmt.c:984-988, RAM |
| `DM_CMD_GET_SP_STATS` (60) | `pvt_sample.py`; `die_c` | READ | performance.c:404-466 → thermal_pwr_mgmt.c:2780-2784, RAM, resets nothing |
| `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | `pvt_sample.py`; `die_c` | READ | thermal_power_monitor.c:545 → thermal_pwr_mgmt.c:732-773 → pvt_controller.c, PVT register reads |
| `DM_CMD_GET_MODULE_VOLTAGE` (31) | lib.sh's `die_c` (`ettelem sample --seconds 1 --every-ms 500` through E128's guard, each block's start and end: E144's C1) | READ (nine PMIC voltage-register reads; allowed) | thermal_power_monitor.c:243 → thermal_pwr_mgmt.c:1010-1140 → pmic_get_voltage |
| **`DM_CMD_GET_ASIC_PVT_SAMPLES` (74), group 0 only** | `pvt_sample.py` at 10 Hz | **READ, from the held patch source** (E144's classification and residual, unchanged: two register reads per sensor, no write; the sampler refuses every group but 0 and 4) | the maintainer's command-74 patch of 7 Oct 2026 (held by the lab, not public) → public pvt_controller.c:645-657 → `pvt_get_ts_data` |
| `sparsity_ccheck.sh` → `build/ccheck/b/host/sparsity_host` (the C-logging host, E78's kernel) | every launch | no device-management command: the ops node only (code load, the tiles' DMA, launches; the C log's two extra transfers are runtime DMA, `dev.put`/`dev.get`; Q139(k)'s audit of the patch: GO, 0 send sites) | — |
| `et-who`, `et-holders`, `et-lab-manifest`, `uptime`, `who`, `ps`, `flock`, `sha256sum` | the session and the blocks | none: no management node opened | — |
| **not sent** | — | — | `DM_CMD_SET_STATS_RUN_CONTROL` (no `--reset-ms`; the guard refuses it), command 74's group 6 (the latch reset), the firmware-revisions query, any residency read, any `DM_CMD_SET_*`, any governor/TDP/threshold/clock set, any reset, power cycle, PCIe, driver, firmware or OTA work, `dev_mngt_service` (lib.sh's drain is replaced by a refusal) |

## The day's one post

Before the session, this card's clause goes into the day's one `#community-lab` post, `1567332504330051616` (section 15 and 23: every change
rewrites it with `edit_replace.mjs` and `EXPECT_TEXT`, under the discord lock): `using aifoundry3 for 1.5 h, until ~HH:MM PST
[doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, the other clauses kept word for word. At the release the clause is
dropped (or, if it is the last card held, ` — released` is appended, every word kept). Mon 2 Nov's post is never edited.

## What this cannot say

- One session, one card, one evening. The plateau moves 0.3-0.8 °C between sessions on this card with nothing changed (E97, item 8), the room's
  only proxy is the rest die, and there is no inlet thermometer.
- The 10-minute holds read 92-95% of their fixed points: the plateau is the same window in prediction and score, so it is like for like, not a
  steady state. K_S and K_Q start on tails of 3.2 and 4.4 °C, which no earlier session has scored.
- The bands are 1.7-4.1 times the critic's 0.35 °C (Q139(e)'s D4), so a hold's verdict cannot separate M8 from M7 or M6; the informative figures
  are the plateau errors themselves, E − A and the session rms.

## How to run it (for this lane)

At the desk: `/usr/bin/python3 tools/claims-v3/e154/score_e154.py --self-test`, `bash tools/claims-v3/e154/preflight_e154.sh`. Copy
`tools/claims-v3/e154/` to `aifoundry3:aifoundry/tools/claims-v3/e154/`. On aifoundry3, from `~/aifoundry`, after the claim:
`E154_T0=$(date +%s) setsid nohup bash tools/claims-v3/e154/session_e154.sh > build/e154/session.out 2>&1 < /dev/null &` (in a script file run by
`ssh aifoundry3 'bash -s'`). After it: [`collect_e154.sh`](collect_e154.sh) on the Intel (rsync, the C check, the scorer). Data:
`docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/`.

## Files

| file | what |
|---|---|
| `README.md` | this registration |
| `run_e154.py` | the runner (`run_e144.py` with Q139(e)'s design, the pool-6 items, K_S's room rule, the smoke, the stop tests on K_S's tile) |
| `block_e154.sh` | one pass as a lib.sh block (`block_e144.sh` with the runner, the C-check wrapper and the card check) |
| `session_e154.sh` | the detached session on the box (gates, hashes, preflight, config reads, smoke and stop tests, gate, measured pass) |
| `smoke_gate_e154.py` | the smoke's gate |
| `preflight_e154.sh`, `dmcmd-audit.txt`, `dmcmd-audit-bare.txt`, `dmcmd-audit.md` | the device-command preflight and its printouts |
| `frozen-e154.sha256` | the 31 files the session checks before any device opens |
| `score_e154.py` | the scorer (13 frozen inputs' hashes; arm E, arm A, M7, M6, E153's measured S, H_M's rules, the session figure) and its self-test |
| `collect_e154.sh` | brings the session's data and logs to the Intel, runs the C check and the scorer |
| `logs/` | the self-test, the dry run |

## The session script's dry run

**The session script's dry run** (17:50 PST, `V3_DRY=1 bash session_e154.sh`): the gates chose the full design, the hash check and the
preflight passed, the dry smoke exited 1 (the toy card's board never rises, so the in-launch stop test cannot trip), the gate read NO-GO, and
no measured pass started: the NO-GO path ends the session after its closing config read. The gate's readers were also run on E144's and E153's
real smoke directories on the box: E144's 751 telemetry lines all carry the 34 raw codes (mean 50.9-55.8 °C, within 3 °C of `minshire[0]`, 600
MHz) and its config reads pass; E153's C log gives 10 host records naming this host and kernel and 60 C records for 60 launch records.
