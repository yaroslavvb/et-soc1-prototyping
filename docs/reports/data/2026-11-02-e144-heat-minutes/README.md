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

*Corrected after verification (a dated note, Tue 3 Nov 2026, about 00:20 PST; desk only: no card opened, no device command, nothing
re-run).*
- *An independent verifier re-ran the frozen scorer on the committed pass, which gave `scored.json` byte for byte, and re-ran the
  device-command audit, which gave the same printout. It also checked the frozen inputs, the order of events, the stops and their
  margins, the card and the day's post.*
- *It found one major fault and five minor ones. None changes a measured number, a rule, a prediction or a registered verdict, and none
  is a disallowed command.*
- *Each is corrected by a dated note beside the text it concerns, with that text left as it was, and set out in full in
  [§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026) at the end. The numbers they quote are printed by
  [`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt).*
- ***The major one, C1:** E144 sent ten kinds of device-management command, not nine. lib.sh's `die_c` ran `ettelem sample` at both ends
  of each block, which adds `GET_MODULE_VOLTAGE` (nine PMIC voltage-register reads a sample). All ten kinds are READs. Two of them make
  PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows. No write was sent.*

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

*Dated note, 3 Nov (C2): more exactly, the frozen chain was fitted on E89's two passes and E97's session, and its leave-one-hold-out
score was inside E97's session. A chain of its form fitted on E89's square waves alone had one session-out score, on E97: 0.46–1.50 °C
rms (the table's first row; Q138(t)'s C2). E144 is the frozen chain's first score on a session it never saw. "In plain words" above has
the same slip: it says the chain had been checked only inside the one session it was fitted on.*

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
  - *Dated note, 3 Nov (C3): these errors come from one blind session (2 Nov), as point readings. The scorer gives (a) and (b) no
    interval. The 0.3–0.8 °C is how far the plateau moved within E97's one session, cause not established, not a move between sessions.
    This session showed no move of that size (given the board trace, the die stayed within 0.04–0.18 °C rms of the chain), and there is
    no inlet reading. So the error between sessions is not yet measured below that scale. Until more sessions run, the scale to quote is
    E97's within-session moves and the 0.46–1.50 °C of the one session-out design (E89 → E97). And "from the planned work alone", here
    and in "In plain words", also takes the die's measured starting temperature (each hold's own rest) and the realized launch pattern
    (A1.2).*
- **The planned-power route works on a new day.** E78's per-kind switching watts × the launch pattern, closed through the leakage
  law, puts both plateaus within 0.15 °C. M6's long-hold rule has no leakage loop and misses them by 23–28%, close to the 29–33% by
  which it missed E97's. The measured board rise over the planned switching watts shows where the gap comes from:
  - H_H: 17.29 W against E78's 26.701 W × 0.4563 = 12.18 W;
  - H_L: 5.35 W against 4.176 W × 0.9655 = 4.03 W.

  That is 25–30% of the board's rise. It is the temperature-dependent power of E97's idle law, mostly the leakage the warming die
  draws, which the closed loop carries and M6 leaves out.
- **Item 8 gets a second-session plateau on this card**, through the chain: fp32 random reads 0.868 °C per board W against the frozen
  0.8695 (E97: 0.877–0.921). The int8-full replicate of E97's H1 was not in the subset and stays open.
  - *Dated note, 3 Nov (C4): the line above is corrected in three ways.*
    - *The like for like is one hold, E97's H3: fp32 random, duty-cycled (share 0.560). It read 0.877 °C per board W (0.8767 in
      `e97.json`), against H_H's 0.8675 (share 0.456). That is −1.0%, or −1.1% against the rounded 0.877, at rest dies of 50.63 and
      51.22 °C. "0.877–0.921" spans three kinds.*
    - *It is consistent with no drift of the heat path between 1 and 2 Nov. It cannot separate room from path, because there is no
      inlet thermometer. The operating points also differ: H3 sat at 70.4 °C, approached from above; H_H at 66.2 °C, from rest.*
    - *What the kinds page's items still need. Item 8 is "The heat path drifts between sessions": an inlet thermometer, a probe at
      23 Oct's idle die and more than one warm probe. Item 9 is "A steady state for heat": a hold steady by the registered test (E144
      registered no steadiness test), a replicate of each hold (E97's int8 full and fp32 ones have none) and the inlet. Random fp32 at
      full duty still has no plateau below aifoundry3's stop. What E144 adds to item 9 is the chain tested on one blind session, and a
      second-session plateau for fp32 random on this card.*
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

*Dated note, 3 Nov (C6): slips in time and text, and two things done or present that no record stated. None moves a number or a
verdict (`corrections-numbers.txt` § C6).*
- ***(a) The time left.** The registration says the gates left "under 60 card-minutes", and so did the lane's first result. From the
  claim (22:36:26) to the 23:50 end gate was 73.6 minutes, and `run.log` read "70.4 min left" at the pass's start (to the runner's 23:49
  deadline). The subset still follows: the full design's 75.9 minutes did not fit, and Q138(t)'s rule takes the subset whenever the
  gates leave under 80 card-minutes. This README's own wording, "no room for the full 75.9-minute design", was right.*
- ***(b) When the registration and N1 were written.***
  - *The registration's "about 22:40" is wrong: its commit is 22:35:10, pushed 22:35:14.*
  - *N1's "about 22:46" is wrong too: its commit is 22:44:43, pushed 22:44:48 by the Intel clone's origin/main reflog. The table's
    22:44:49 is a second late.*
  - *N1 came after the smoke's first launch (22:37:20) and 6 minutes into pass 14420 (its block began 22:38:30), during R0 and before
    H_H's first launch (22:46:34). The registration's line 3 says nothing below it changes after the first launch, so N1 departs from
    that line in form.*
  - *N1 changes no rule, band or prediction. Its numbers are the frozen subset's (`predictions-e144.json` › `aifoundry3.subset`: H_L
    0.7858 °C per board W, 0.409 °C carried in, and 0.8608 / 0.7858 = 1.095).*
  - *Pass 14420's `code.sha256` pins the registration README at its `13799873` text (`fcd51917…`), before N1.*
- ***(c) The claim's clause.** The registered order of work names `until ~23:50 PST`; the claim said `until ~23:40 PST` (§ Card and
  post). The session ended at 23:23:39, inside both.*
- ***(d) An interim look.** At 23:09 PST, while H_L ran, the lane copied the live pass's files from the box (no device access) to its
  scratch, cut them at R1's end and scored H_H with the frozen `score_e144.py`. Every arm of that H_H score is identical to
  `scored.json`'s. Nothing registered changed afterwards: the registration's last change is N1, and the scorer's sha256 matches the
  registration. The reducer and collector added at `ca979517` run the frozen scorer unchanged. No record stated the look until now.*
- ***(e) Other users' logins.** No record of the session says whether other users were logged in on aifoundry3. `block_e144.sh`'s
  other-user test, E97's, looks at other users' device processes and the card's holders, not at logins. It logged nothing: there is no
  "others present" line in `run.log`, `logs/smoke.log` or `logs/queue.log`. A read-only `who` count by the verifier at 23:47 PST, after
  the session, found three logins of other users; aifoundry3 has carried idle tmux logins of other lab users since 26 Oct. Under E60's
  D1, which the block cites, an idle login does not block. No login is named in any file.*

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

**Dated note, 3 Nov (C1): one sender is missing from the list above, lib.sh's `die_c`.**
- `block_begin` (lib.sh:188) and `block_end` (:196) call `die_c` (:103), which runs `$ETTELEM sample --seconds 1 --every-ms 500` under
  `timeout 20`. `block_e144.sh` sources lib.sh (:15) and then sets `ETTELEM` to E128's guard (:16), so the calls took the guard's
  sample path (`ettelem_guard.sh:19-31`).
- The binary is the box's `build/ettelem/ettelem` (`16037641…`, `logs/sha256-setup.txt`), built from lab `de262730`'s source. Its
  `sample()` is the reviewed source's, byte for byte ([`docs/findings/14-card-behaviour.md`](../../../findings/14-card-behaviour.md),
  E132 C1 and E134 C6; `corrections-numbers.txt` § C1).
- They ran under the card lock at both ends of smoke 14401 (22:37:01, 22:38:18) and of pass 14420 (22:38:30, 23:23:39): four calls of
  about two samples each. `block.json` › `die_c_start`/`die_c_end` read 50/51 and 51/52, so each call ran.
- Each sample sends `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE` and
  `GET_ASIC_FREQUENCIES` (`tools/ettelem/ettelem.cpp:165-167`). It resets nothing without `--reset-ms` (:149, :172), which the guard
  refuses.

The kind the table lacks:

| command | sent by | class | source (et-platform 836a4ab) |
|---|---|---|---|
| `DM_CMD_GET_MODULE_VOLTAGE` (31) | lib.sh's `die_c` (`ettelem sample` through E128's guard), at each block's start and end | READ (nine PMIC voltage-register reads per sample, I2C reads with no write; allowed by the owner's rule of 2 Nov 2026) | thermal_power_monitor.c:243 → thermal_pwr_mgmt.c:1010-1140 (nine `pmic_get_voltage` calls) → pmic_controller.c:1473-1500 → `get_pmic_reg` :254-300 (Q136(w)'s table, `tools/claims-v3/dmcmd_table.json`) |

`die_c` is also a sender of five rows above: `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`
and `GET_ASIC_FREQUENCIES`. The committed audit lists all six at lib.sh:103 (`tools/claims-v3/e144/dmcmd-audit.txt` lines 8-13) and
read GO, so the checker saw them; only the README's list left them out.
- **Corrected count: ten kinds of command, every one a READ.** Two of them make PMIC voltage-register reads: `GET_ASIC_VOLTAGE` (two
  a call) and `GET_MODULE_VOLTAGE` (nine). The owner's rule of 2 November 2026 allows both.
- E128's guard carried the config reads and these samples, not "config only" (the table's first row).
- No class, verdict or number changes, and no write was sent.

**Dated note, 3 Nov (C5): command 74's residual, exactly.** The held source has two forms, both of 7 Oct 2026:
- **The first** serves group 0 (`PVT_SAMPLE_GROUP_MINSHIRE_TS`) through `pvt_get_min_shire_ts_sample`, which converts the codes to whole
  degrees. It serves group 6 through `pvt_hilo_reset`, a write.
- **The same day's amendment** serves raw codes on a new group 7 (`PVT_SAMPLE_GROUP_TS_RAW`) through `pvt_get_ts_raw_data`. That makes
  the same `sdif_data` and `smpl_hilo` reads, unconverted, and writes nothing. It no longer serves group 6.
- **The running build** returns raw codes on group 0 (`logs/probe.out`: codes 1914–1956 at a 50 °C firmware reading). So its group-0
  path matches neither held form. It differs in more than "the conversion" (above).

The committed data check the only write either held form has, the latch reset (`corrections-numbers.txt` § C5):
- The 34 high latches read the same at E89's probe of 31 Oct, 19:02:49 PDT
  ([`ident/probe2.out`](../2026-10-31-e89-heat-low-power/ident/probe2.out)), as in every hi/lo tick of smoke 14401 (16 ticks) and pass
  14420 (542).
- No low latch rose between ticks.
- A reset sets each latch to the current code, which would drop the high latches and lift the low ones.

So no latch reset ran on this card through more than 200,000 group-0 reads: E89's 22,976, E97's 150,295 and E144's 27,816. That covers
command 74's group 6, and also the statistics reset, whose handler resets the latches too (performance.c:575 →
`Thermal_Pwr_Mgmt_Init_OP_Stats`, thermal_pwr_mgmt.c:2828).

At 836a4ab, `pvt_get_min_shire_ts_sample` is pvt_controller.c:645-657, not 651-665 as the table says; `pvt_get_ts_data` is :618-643. The
class stays READ, with this residual. The integration lane that folds E144's entry into `tools/claims-v3/dmcmd_table.json` carries the
same residual.

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
- *Dated note, 3 Nov (C6): two more, set out in § Registered against what happened, (b) and (d). Note N1 was appended after the first
  launch, which the registration's line 3 rules out in form, though N1 changes no rule. An interim score of H_H was read at 23:09,
  during H_L. Neither changed anything registered.*

## Files

| file | what |
|---|---|
| `scored.json` | the frozen scorer's output: `score_e144.py a3 aifoundry3/e144/p14420` (Q138(t) at A1, unchanged) |
| `e144.json` | from `reduce_e144.py`. Per hold: launches, dispatch records, share, gates, stops. Also the rest die before each hold, the sampler's health, the peaks, the clock, the config reads, the smoke's stop tests and, reported only, the model's own (c) readings and the subset's plan numbers beside the measured rises |
| `aifoundry3/e144/p14420/` | the measured pass: `telemetry.jsonl.gz` (10 Hz, 34 raw codes a line), `marks.jsonl`, `runs.jsonl` (one record a dispatch), `run.log`, `configs.json`, `config_start.json`/`config_end.json`, `block.json`, `manifest.txt`, `code.sha256`, `gen.sha256` |
| `aifoundry3/e144-smoke/p14401/` | the smoke plan and the five stop tests. Its `STOP` and `HOLDSTOP` files are the tests' own |
| `logs/` | the box's setup checks (`sha256-setup.txt`, `dmcmd-preflight.txt`, `dry-subset.log`), `probe.out`, `smoke.log`, `queue.log`, and the session's config reads (`config-session-start.json`, `config-session-end.json`) |
| [`tools/claims-v3/e144/`](../../../../tools/claims-v3/e144/README.md) | the registration and its scripts: runner, block, session, queue, preflight, audit table, collect, reduce |

*Added after verification (Tue 3 Nov 2026):* [`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt),
every number the corrections quote, read from committed files. Run it from the lab repo's root, with `--et-platform <clone>` for the PVT
functions' line numbers at 836a4ab. Nothing listed above changed.

Reproduce from the lab repo's root with `python3 tools/claims-v3/e144/reduce_e144.py docs/reports/data/2026-11-02-e144-heat-minutes`.
It needs numpy, for the scorer.

## Corrections after verification (Tue 3 Nov 2026)

An independent verifier (Q138's, about 23:30–23:54 PST on 2 Nov) re-ran the frozen scorer on the committed pass and got `scored.json`
byte for byte. It re-ran the device-command audit and got the committed printout. It checked the frozen inputs by sha256 and git
ancestry, the order of events by the clone's reflog, the stops and margins on the raw samples, and the card (read-only) and the day's
post. Its verdict: the result holds, with six faults to fix, one major. None is a measured number, a rule, a prediction or a
registered verdict, and none is a disallowed command. They are corrected here, desk only, at about 00:20 PST on 3 Nov, by the dated
notes above, in this README and the registration's, and by this section. No existing line was edited. Every number quoted is printed
by `corrections-numbers.py` → `corrections-numbers.txt`.

- **C1 (major): the device-command list left out lib.sh's `die_c`.**
  - `block_begin` and `block_end` call it at both ends of each block, and it runs `ettelem sample` through E128's guard.
  - That sends `GET_MODULE_VOLTAGE`, nine PMIC voltage-register reads a sample, and five GETs already listed.
  - E144 therefore sent ten kinds of command, not nine, every one a READ. Two of them make PMIC voltage-register reads, which the
    owner's rule of 2 November 2026 allows.
  - The committed audit always listed these sends (lib.sh:103) and read GO.
  - See the note in § Device commands sent, and the registration's.
- **C2 (minor): the "before".** The registration's "What it does to predicting heat" repeats two framings that Q138(t)'s C1 and C2
  withdrew before the claim:
  - "M6's plateau-only rule used as a trajectory read 1.5–11.6 °C": no model made that rule.
  - "measured only within one session": a chain of the same form, fitted on E89 alone, read E97 session-out at 0.46–1.50 °C.
  - This README's "In plain words" and § What it does to predicting power and heat have a smaller form of the second. The before/after
    table was right.
- **C3 (minor): one session.** E144's errors are one blind session's point readings, with no interval. The 0.3–0.8 °C is E97's
  within-session plateau moves, not a session-to-session move. The error between sessions is not measured below that scale. Arm (b)'s
  "planned work alone" also takes the measured starting die, and the fp32 hold was duty-cycled (3.20 s every 7.56 s, share 0.456).
- **C4 (minor): items 8 and 9.**
  - Item 8's like for like is E97's H3 alone: 0.8767 against H_H's 0.8675 °C per board W, −1.0%. That is consistent with no drift
    between 1 and 2 Nov, but it cannot separate room from path.
  - Both items' named needs stay open: the inlet thermometer, the warm probes, a hold steady by the registered test, and the
    replicates.
- **C5 (minor): command 74's residual.**
  - The held source's raw-code form serves group 7, so the running build's group-0 raw path matches neither held form.
  - The latches show no reset through more than 200,000 group-0 reads since 31 Oct.
  - `pvt_get_min_shire_ts_sample` is pvt_controller.c:645-657 at 836a4ab.
- **C6 (minor): times and text.**
  - The gates left 73.6 card-minutes, not "under 60", and the subset still follows.
  - The registration was written by 22:35:10, not "about 22:40". N1 was written by 22:44:43, not "about 22:46", after the first
    launch.
  - The claim said "~23:40", not "~23:50".
  - An interim H_H score was read at 23:09.
  - Other users' logins went unrecorded.

**Unchanged:** the registration's text (`tools/claims-v3/e144/`, `13799873`, with N1 at `8d396e2c`; only dated notes added),
`scored.json`, `e144.json`, every raw pass and log, every script, and every registered verdict:
- H_H: (a) PASS, (b) PASS, (c) per board W PASS;
- H_L: (a) PASS, (b) PASS, (c) t63 PASS, (c) per board W INCONCLUSIVE;
- the linearity H_H/H_L INCONCLUSIVE.

**What the corrections do to predicting power and heat.** No scored number moves. The term tested is still Q138(t)'s five-stage heat
chain on aifoundry3, from board watts to the die (0.8695 °C per board W), closed through E97's idle law and fed by E78's switching watts
× the launch pattern.

| | before E144 (corrected) | after: one blind session, 2 Nov |
|---|---|---|
| the die given the board trace (a) | inside E97, leave one hold out: 0.47–0.66 °C rms. Session-out, the chain's form fitted on E89 alone: 0.46–1.50 °C. M6 as frozen, in sample: 0.31–0.91 °C | 0.18 °C (fp32 random, duty-cycled) and 0.04 °C (int8 −1s) rms |
| the plateau from planned power (b) | the chain 0.33–1.04 °C low on E97, in sample; M6 29–33% low | −0.15 and +0.01 °C; M6 28% and 23% low |

What changes is how far the "after" reaches:
- It is one session, in a stable room, with no interval.
- Between sessions the scale is still E97's within-session 0.3–0.8 °C and the one session-out design's 0.46–1.50 °C.
- Power is not measured here. E78's switching watts reproducing the plateau is indirect support only.
- The command record is now complete: ten kinds of read, two with PMIC voltage-register reads, no write.
