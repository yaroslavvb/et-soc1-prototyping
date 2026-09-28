# Heat placement: which card can show a thermally triggered clock change, what to measure instead, and the safety limits

Research task 3 of the heat-placement workflow. Written 2026-09-27 from the repository alone. No card was touched.

## Citation key

| Tag | Meaning |
|---|---|
| `R/` | `/home/yaroslavvb/claude/et-soc1-pages`, branch `pages-v3b` at `305fe0d` |
| `V3/` | `R/docs/reports/data/2026-09-25-claims-v3/` (the version-3 three-card campaign, E35–E47) |
| `FW:` | The firmware source of the build that the 1.3.1 cards run: `git show cafe03fc3^:device-bootloaders/src/ServiceProcessorBL2/<file>` in `/home/yaroslavvb/claude/et-soc1-prototyping/external/et-platform`. `V3/firmware.md:15-17` maps the cards' release 1.3.1 (BL2 0.20.0) to `cafe03fc3^`. `FW:services/thermal_pwr_mgmt.c` is byte-identical to the `fw-may2024/` extract that `firmware.md` used (checked with `diff`) |
| `FWnow:` | The same tree at its checked-out HEAD `836a4ab` |
| `MAN/` | `/home/yaroslavvb/claude/et-soc1-prototyping/external/et-man/` |
| **[derived Dn]** | A number I computed from committed raw data. `derive_feasibility.py` (next to this file) reproduces every Dn, and its output is in `derive_feasibility.out` |
| **[inference]** | My reasoning, not a measurement or source text |

Firmware caveat: which exact commit the cards run is not established (`R/docs/findings/16-dvfs-and-leakage.md:215-219`). `cafe03fc3^` is the closest source for 1.3.1 (`V3/firmware.md:17`). **No source mapping exists in the repo for aifoundry1 card 1's release 1.2.0, or for card 0's 1.4.1.**

---

## 0. Answers in brief

1. **Average or one sensor? The average.** The thermal test compares the integer mean of the 34 minion-shire sensors with 65 °C. It never looks at a single sensor (§1). Two consequences for the owner's hypothesis:
   - A single hot shire moves the governor's reading by only 1/34 of its own rise.
   - From a cool start, the governor steps down only when the whole die has warmed.
2. **(a) Only aifoundry2 can show a thermally triggered step.** That step is 800 or 700 MHz down to 600 MHz, and back up while the reading hunts around 65–66 °C. It can happen only when aifoundry2's mean reading is ≤ 63–64 °C at launch.
   - That condition was met once: on the morning of 21 September, after an overnight idle to 62 °C (E10). It cannot be created on demand.
   - During the whole version-3 campaign, aifoundry2's mean never read below 65 °C in 336,070 samples, and its blocks started at 67–99 °C [derived D1, D2].
   - From a 62–63 °C start, the first down-step comes 0.9–1.5 s after launch for ones or random data, and 5.6–6.1 s after launch for zeros. All of this fits inside one ≤10 s process [derived D5].
   - aifoundry3 cannot step: it is pinned at 600 MHz by a TDP of 0 W.
   - aifoundry1 card 1 never left 600 MHz. That includes 11,446 samples in which both governor tests said "step up" [derived D1].
   - aifoundry1 card 0 is excluded.
3. **(b) Best proxy: the time for the mean reading to first read 66 °C from a fixed start**, measured on aifoundry3 and aifoundry1 card 1, whose idle dies sit below 65 °C.
   - This is the governor's own input crossing the governor's own threshold. So it answers "can the same computation run longer before the thermal test fires" directly.
   - The only thing missing on those cards is the clock response.
   - Add the peak-hold high after a statistics reset as the one spatial signal. It shows the hottest sensor's peak, but not which sensor it was.
   - The SP trace is not usable for this.
4. **(c) Safety.**
   - Cap the mean reading at 88–90 °C, and the peak-hold high at about 93 °C.
   - The firmware gives no protection above its 600 MHz floor on these cards. In the campaign, aifoundry2's mean read 103 °C (high 106) at 600 MHz with no reaction [derived D6]. The PMIC's 75 °C hardware alarm reads a register that is always 0 [derived D7].
   - Every device process must be ≤ 10 s. Chain 2 s heater launches as the V3-IDLE blocks did, with the card lock held, the intrusion checks on, and no configuration change.
   - aifoundry1 card 0 must hold no process and must stay at its idle while card 1 runs.

---

## 1. What the governor reads and does (facts every later section depends on)

**The thermal test uses the integer mean of 34 sensors.**
- `update_module_current_temperature()` calls `pvt_get_minion_avg_temperature()` and enters `THERMAL_DOWN` only when that value is `> sw_temperature_c` (`FW:services/thermal_pwr_mgmt.c:651-679`).
- The threshold is `TEMP_THRESHOLD_SW_MANAGED 65` (`FW:include/thermal_pwr_mgmt.h:46`). All three campaign cards report 65 °C (`V3/results/tel.json`, `.items[item=TEL-G].per_card.<card>.passes[].config.temp_threshold_c`).
- `pvt_get_minion_avg_temperature()` sums `sample.current` over `PVTC_MINION_SHIRE_NUM` = 34 shires and divides as integers (`FW:driver/pvt_controller.c:1279-1305`, `FW:include/bl2_pvt_controller.h:80`).
- Each shire's value is already truncated to whole °C by `/ 1000` in integer arithmetic (`FW:driver/pvt_controller.c:582`). See also `R/docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html:685`.
- The sensors are one per minion shire: 32 compute shires plus the master and spare shires (`MAN/ET Programmer's Reference Manual.pdf` p.17: "1 TS in each minion/IO Shire"; brief text §1).
- The host's `temp_c.minshire[0]` is this same mean (`R/docs/findings/14-card-behaviour.md:85`; `R/docs/findings/05-claims.md:36`).

*[inference]* The test fires when the sum of the 34 truncated readings reaches 34 × 66 = 2,244.
- A mean reading of 62 means the sum is 2,108–2,141, so reaching 66 needs 103–136 more sensor-degrees.
- One shire alone would have to warm by 103 °C or more. **With this rule, no single hot spot can trip the thermal step from a cool start.** The whole die has to warm.

**Thermal comes first, and at the floor it just holds.**
- The power branch runs only while the state is below `THERMAL_DOWN` (`FW:services/thermal_pwr_mgmt.c:845`).
- The thermal loop steps the operating point down while the mean is > 65 °C, and sleeps `DELTA_TEMP_UPDATE_PERIOD` = 1000 ms between steps (`FW:services/thermal_pwr_mgmt.c:2316-2360`; `FW:include/thermal_pwr_mgmt.h:87`).
- The lowest point seen on any card under load is 600 MHz. On aifoundry2, a die at 66 °C "stayed at 600 MHz for the last 4.5 s" (`R/docs/findings/16-dvfs-and-leakage.md:72-77`).
- With the governor at the floor, nothing else happens even very hot: aifoundry2 ran at 600 MHz with a 103 °C mean reading [derived D6].

**An idle master minion resets the clock to the boot point** (`FW:services/thermal_pwr_mgmt.c:2194`; `R/docs/findings/16-dvfs-and-leakage.md:63-65`). Each separate host process therefore starts again from 600 MHz, and the step-up comes 0.39–0.99 s after launch (`16-dvfs-and-leakage.md:88-92`).

**No hardware thermal trip is active.**
- The PMIC over-temperature alarm (set point `TEMP_THRESHOLD_HW_CATASTROPHIC 75`: `FW:include/bl2_pmic_controller.h:272`, `FW:driver/pmic_controller.c:490`) would force `THERMAL_SAFE`, which is 300 MHz (`FW:services/thermal_pwr_mgmt.c:2480-2486`; `SAFE_STATE_FREQUENCY 300U`, `FW:include/thermal_pwr_mgmt.h:66`).
- But the alarm watches the PMIC's own "System Temperature" register (`FW:driver/pmic_controller.c:1234-1236`, `PMIC_I2C_SYSTEM_TEMP_ADDRESS 0x6`). The firmware itself says: "PMIC is currently reporting system temperature as 0" (`FW:services/thermal_pwr_mgmt.c:2995`).
- On the cards, `sp.system_c` read `[0,0,0]` in all but 188–252 samples per card. In those few samples the middle field of the `[avg, min, max]` triple (the minimum; `R/tools/ettelem/ettelem.cpp:149-158`) read 65535, and the average and maximum read 0 [derived D7]. *[inference]* 65535 is probably the minimum's initial value just after a statistics reset.
- Cards ran at a 88–103 °C mean without dropping to 300 MHz [derived D3, D6]. The datasheet publishes no absolute maximum ratings or package thermal limits ("will be included in a future release": `MAN/ET Preliminary Datasheet Rev 1.0.pdf` p.31 §8.1, p.32 §9.1).

**The host cannot see temperature per shire.**
- The host gets the current mean, plus the lowest and highest values any sensor's hardware peak-hold captured since the last reset (`R/docs/findings/01-resources.md:216`).
- The per-shire print `MS %2d Temp [C]` exists twice, and neither copy is reachable. One is at DEBUG level in `pvt_print_min_shire_temperature_sampled_values` (`FW:driver/pvt_controller.c:1204`), reached only from `pvt_print_all` (`:1385-1390`). The other is at CRITICAL level in `pvt_get_and_print_minshire` (`:1410`), reached only from `pvt_get_and_print` (`:1578`). Neither entry point has a caller in the tree (checked with `git grep` at `cafe03fc3^`; brief §2).
- The peak-hold high runs 2–3 °C above the mean after each rise, on all three cards (`R/docs/findings/05-claims.md:39-40`; E41, `R/docs/findings/03-experiments.md:1238-1239`).
- `ettelem sample --reset-ms` resets it. It sends `DM_CMD_SET_STATS_RUN_CONTROL` with `STATS_CONTROL_RESET_COUNTER` (`R/tools/ettelem/ettelem.cpp:59-69`), which reaches `Thermal_Pwr_Mgmt_Init_OP_Stats()` → `pvt_hilo_reset()` (`FW:services/performance.c:578-580`, `FW:services/thermal_pwr_mgmt.c:2963-2986`). The reset windows worked in every aifoundry2 and aifoundry3 pass, and failed once on aifoundry1 card 1 (`R/docs/findings/03-experiments.md:1237-1238`).
- Exposing per-shire temperatures would take a reflash with a changed SP, which may need a signed image (brief `html:884`). That is out of scope under the lab rules (`R/AGENT.md:155`).

**The SP's own maximum-clock field.** `sp.minion_mhz[2]` is a since-boot maximum. `CALC_MIN_MAX(op_stats.minion.freq, …)` updates it every pass (`FW:services/thermal_pwr_mgmt.c:916`), and the stats reset does not clear it (no `freq` line in `Thermal_Pwr_Mgmt_Init_OP_Stats`, `FW:…:2963-2985`). It read 800 on aifoundry2 and 600 on aifoundry3 and aifoundry1 card 1 in every campaign sample [derived D1].

---

## 2. The four cards

| | aifoundry2 | aifoundry3 | aifoundry1 card 1 | aifoundry1 card 0 |
|---|---|---|---|---|
| Firmware | 1.3.1 | 1.3.1 | 1.2.0 | 1.4.1 |
| Governor config read on the card | TDP 65 W, 65 °C, `managed_power` | **TDP 0 W**, 65 °C, `max_power` | TDP 65 W, 65 °C, `managed_power` | 65 W (driver) |
| Sources for the config row | `tel.json` TEL-G `.per_card.aifoundry2.passes[].config` | same, `.aifoundry3` | same, `.aifoundry1-c1` | `14-card-behaviour.md:150-151` |
| Clock under load | 600/700/800 MHz; above 600 only from a cool die | 600 MHz always | 600 MHz always (below) | idles at 300 MHz (`low_power`) |
| Clock in version-3 telemetry [D1] | 600 in 336,070 of 336,070 samples | 600 in 397,813 of 397,813 | 600 in 359,657 of 359,657 | excluded |
| Die at block start, V3 [D2] | 67–99 °C | 52–67 °C | 55–69 °C | not run |
| Idle / cooling [D3] | 900 s after heating to 88 °C: 67–77 °C | 54–55 °C | 56–57 °C | — |
| Meter refresh | SP pass 133.2 ms | SP pass 224.1–224.5 ms | 134.8 ms | — |
| Sources for the meter row | `03-experiments.md:1232-1233` | same | same | — |
| Can a thermal DVFS step be shown? | **yes, only from a cool die** | **no** | **no, never boosted** | **must not be used** |

### 2.1 aifoundry2: the only card whose clock moves, and only from a cool die

- **Rule.** Above 65 °C a busy card sits at 600 MHz; below it, the clock steps up to 700 or 800 MHz (`R/AGENT.md:163-165`; `14-card-behaviour.md:27-46`). The operating points are 600 MHz at 516–518 mV, 700 at 568 and 800 at 618–620 (`14-card-behaviour.md:38-42`).
- **How E10's runs were cool.** "The card had idled overnight to 62 °C. This cannot be recreated on demand; the die needs hours to get below 65 °C" (`R/docs/findings/03-experiments.md:217-219`).
  - The runner then waited before each 7 s run until the mean read ≤ 63 °C. It took 0–62 s after the previous run (`R/tools/ettelem/run_horace_cold.sh:21-29`; `R/docs/reports/data/2026-09-21-horace-aifoundry2/cold1/starts.jsonl`, fields `start_temp` 62–63 and `waited_s` 0–62).
  - So once the die idles below 65 °C, getting back to the start temperature after a short run is quick.
  - The obstacle is the resting temperature, which depends on the room.
- **How often aifoundry2 is cool enough.**
  - 21 September: 62 °C after a night (E10).
  - 22 September: 73.0 °C after 20.6 hours idle, "in a warmer room" (`16-dvfs-and-leakage.md:134-139`).
  - 23 September: about 65 °C, when the clock lifted to 700–800 MHz in 5–25% of the samples of most bursts (`03-experiments.md:779-780`; `19-observability-and-the-unmetered.md:88-90`).
  - Over 26 sessions on five days it never ran above 600 MHz at a reading of 68 °C or more (`R/docs/reports/2026-09-22-dvfs-leakage.html:461`).
  - During the campaign, the lowest mean reading in 336,070 samples was 65 °C, and it never saw a busy sample at ≤ 65 °C [D1]. In 900 s of idle after heating it cooled only to 67–77 °C [D3]; see also `03-experiments.md:1343`.
  - The room also changes: the die once fell 12 °C under an unchanged workload (`14-card-behaviour.md:272-273`).
- **What a cool start looks like** (E10, 10 Hz, times from the runner's start mark, so they include host start-up) [D5]:

| Workload (1,024 minions, 7 s) | Start | Up to 800 MHz at | First down-step | Mean reading at the step | Board W at the step |
|---|---|---|---|---|---|
| random normal | 63 °C | 0.64, 1.13, 0.89 s | 0.94, 1.23, 1.09 s | 66, 67, 67 | 87.6, 53.7, 87.8 |
| ones | 63 °C | 0.66, 0.96 s | 1.26, 1.46 s | 66, 65 | 55.9, 55.6 |
| zeros | 62, 63 °C | 1.09, 0.53 s | 6.09, 5.63 s | 64, 65 | 39.0, 39.4 |

  - Time spent at 800 MHz over a whole run: zeros 5.1–5.9 s, ones 0.6–0.8 s, random data 0.1–0.3 s (`14-card-behaviour.md:48-54`).
  - The zeros steps happened at readings ≤ 65 °C. The DVFS finding counts steps like these as "unattributed": one looks like the boot-point reset, and the others are most likely thermal steps seen between samples (`16-dvfs-and-leakage.md:85`).
  - After the first step, the loop hunts around the 65/66 °C boundary: seven changes in 2.4 s in one run of ones (`16-dvfs-and-leakage.md:72-77`).
- **What this means for a placement experiment.**
  - The observable is the time from launch to the first 800 → 700 MHz step, inside one process of at most 9 s. The idle reset at every process boundary rules out chaining processes (§1).
  - To get a window of several seconds, the workload's power must be about that of zeros on the full chip (36–39 W board), or a partial-chip placement of random data at similar power [inference].
  - The attribution caveat above means each step must be checked against the mean reading (> 65 °C) at that moment.
- **Hazards.** A CI runner can take this card at any time (`14-card-behaviour.md:274-275`). The heat carried over from earlier runs contaminates later ones (`14-card-behaviour.md:116-132`).

### 2.2 aifoundry3: no DVFS step possible; the best card for thermal-only tests

- **Why no step.** A boot service (`et-board-clock-guard.service`) sets a TDP of 0 W and 600/400 MHz at every boot (`14-card-behaviour.md:166-178`). With TDP 0, the power test "> TDP" is always true and "< TDP" never is, so nothing can step the clock up (`14-card-behaviour.md:166-171`; the same logic in the cards' build: `V3/firmware.md:45-46`).
  - The clock read 600 MHz in all 397,813 campaign samples, and the SP's since-boot maximum is also 600 [D1].
  - Changing that setting is forbidden (`14-card-behaviour.md:211-213`; `R/AGENT.md:155`).
- **Why it still suits a thermal proxy.**
  - It idles at 55–57 °C since the host changes of 25 September (`V3/AMENDMENTS.md:857-859`), below the 65 °C threshold. So a rising mean crosses the governor's real threshold from below.
  - The all-chip heater (2 s random fp32 bursts) took it from 56–58 °C to above 65 °C in 21–35 s, and to 88–90 °C in 344–409 s (126–150 bursts).
  - It cooled back to 54–55 °C within 900 s. The heater drew up to 74.7 W [D3].
  - 407 heater processes of about 2.7 s each all exited 0 [D4].
- **Hazards.**
  - Its readings refresh about every 250 ms (`14-card-behaviour.md:91-96`).
  - A demo service can launch on the card without taking the card lock (`14-card-behaviour.md:274-276`).
  - Host binaries built before the log-level fix crash about 1 time in 100, 1.08 s after start (`14-card-behaviour.md:304-318`). A crashed heater launch must void that run's time-to-threshold.
  - Approaching a start temperature near its idle equilibrium is slow. A5 moved its launch targets to 57 °C after approaches took 225–364 s (`V3/AMENDMENTS.md:857-863`).

### 2.3 aifoundry1 card 1: cool, governor configured like aifoundry2's, but never boosts

- **The evidence** [D1]:
  - 11,446 campaign samples have a mean of 58–64 °C (thermal test off) and board power of 45–63 W. The card idles at 33–35 W (`14-card-behaviour.md:153`), so these samples are busy, and they are under the 65 W TDP, so the power test says "up". Every one of them is at 600 MHz.
  - The SP's since-boot maximum clock read 600 in all 359,657 samples. It never ran above 600 MHz since its SP last booted; the boot time is not recorded.
  - The DVFS page says the same: "aifoundry1's card 1 read 600 MHz in every sample of the three-card check" (`R/docs/reports/2026-09-22-dvfs-leakage.html:300`).
  - Its readout is the same as aifoundry2's (65 W, 65 °C, `managed_power`: `tel.json` TEL-G). **Why it does not step up is not established.** Candidates *[inference]*: its flashed VMIN table tops out at 600 MHz, or release 1.2.0's governor differs. No 1.2.0 source is mapped.
- **Why it still suits a thermal proxy.**
  - It idles below 65 °C: block starts 55–69 °C [D2], and 56–57 °C after 900 s of cooling [D3]; 57–62 °C in `14-card-behaviour.md:153`.
  - It heats fast. The all-chip heater crossed 65 °C 5.4 s after a 61 °C start, and reached 87 °C in 124–165 s (43–57 bursts), drawing up to 86.2 W [D3].
  - Its idle sits 10 W above the idle law, 42.71 W at 73 °C (`03-experiments.md:1344`).
  - The minion rail is 499 mV at 600 MHz, against 518 mV on aifoundry2 and 523 mV on aifoundry3 (`V3/results/idle.json` `.idle_clocks`).
- **Hazards.**
  - It shares a chassis and its air with card 0 (`R/tools/claims-v3/idle/block.sh:216`).
  - A GitHub Actions runner on aifoundry1 runs benchmarks as root (`R/tools/claims-v3/lib.sh:59-60`).
  - The host needs `V3_DEVICE=1`, `ET_DEVICES=1` and lock `etsoc-shire1` (`R/AGENT.md:216-217`; `lib.sh:22-28,183-186`).
  - `dev_mngt_service` opens every card on the host (`14-card-behaviour.md:208-209`). `lib.sh` defers its queue drain while another card's lock is held (`lib.sh:128-141`).

### 2.4 aifoundry1 card 0: excluded

- About ten minutes of smoke blocks took its die to 98–102 °C. Afterwards it read 115–117 °C with nothing running, drawing 66–71 W at 600 MHz, until its firmware dropped it to 300 MHz (`V3/AMENDMENTS.md:841-849`; `14-card-behaviour.md:197-204`).
- It is a cooling fault. The rule is no sustained work (`R/CLAUDE.md:53-54`; `R/docs/lab-access.md:7`).
- Its `low_power` idle is 300 MHz and 18.6–18.8 W (`14-card-behaviour.md:64-67`).

---

## 3. (a) Where a thermal step can be provoked and observed

**On aifoundry2 only, from a mean reading of about 62–63 °C at launch, within 1–6 s of launch.**
- The step is 800 → 700 → 600 MHz, and back up while the reading hunts at 65–66 °C.
- Seen in `mhz.minion` of the 10 Hz telemetry (the only reliable signal: `14-card-behaviour.md:87`), paired with the mean reading at each change.
- It needs a night of idle in a cool room, which cannot be scheduled (`03-experiments.md:217-219`). It did not happen once in the campaign [D1, D2].

**Proposed gate** *[inference]*.
- Before any aifoundry2 DVFS run, take a 1 s die reading (`die_c`, `lib.sh:103-104`) after at least several hours with nothing launched.
- If the reading is ≤ 62 °C, run the DVFS variant. If not, record that DVFS itself could not be shown and run only the proxy (§4) on aifoundry2 at a higher band.

**Within the 10 s rule.**
- One launch of at most 9 s under `timeout 10`, as E10 did with 7 s (`run_horace_cold.sh:30-32`), with the sampler running beside it.
- The window closes at the first step, which for moderate power comes after 5–6 s (zeros).

**Nowhere else.**
- aifoundry3's zero TDP pins it (§2.2), and changing that is forbidden.
- aifoundry1 card 1 never leaves 600 MHz for a reason that is not established (§2.3).
- aifoundry1 card 0 is unsafe (§2.4).
- A downward thermal step below 600 MHz has not been seen on any card (§1), so a hot card shows no step at all.

**Open question.** A 700 ↔ 800 MHz step at readings ≤ 65 °C (the zeros runs) can be the idle reset rather than the thermal branch (`16-dvfs-and-leakage.md:85`). An aifoundry2 run must therefore record, at every clock change, the mean reading and whether a kernel boundary fell within one SP pass.

---

## 4. (b) The best proxy, and whether it still answers the owner's question

### 4.1 Primary: the time for the governor's reading to reach 66 °C from a fixed start

- **What.**
  - Start from a fixed mean reading approached from above: the strict start's edge method, `03-experiments.md:30-44`, used at a start below 65 °C.
  - Run the same computation in placement A or placement B, as a chain of ≤ 10 s launches (`lib.sh:99-100`; the V3-IDLE heater loop, `idle/block.sh:170-192`).
  - Record, from the 10 Hz sampler's own output, the time at which `temp_c.minshire[0]` first reads 66.
- **Where.** On aifoundry3 and aifoundry1 card 1. They idle at 54–57 °C and reach 65 °C under load [D3], so the crossing is the exact event on which the governor's thermal test fires (§1).
- **Resolution.**
  - Step times are sharp to one SP pass: 133 ms on aifoundry2 and aifoundry1 card 1, 224 ms on aifoundry3 (`03-experiments.md:1232-1233`).
  - Fitting the heating power to the step times recovers the rise to about 0.03 °C (`14-card-behaviour.md:103-112`).
  - *[inference, using aifoundry2's fitted network: stages 1.5/4/60/150/400/2500 s, 1.47 °C/W total, `R/docs/findings/11-thermal-model.md` model table]*
    - A 16-shire random-data placement (13.6 W switching on 512 minions, `R/docs/findings/12-heat-management.md:26`) would need on the order of 1.5 minutes to add 8 °C, with the mean then rising by about 0.04 °C/s.
    - A 0.1 °C placement difference in the mean then shifts the crossing by about 2–3 s, which the timing resolves easily.
    - The limit is run-to-run scatter from the heatsink's hidden state. The same workload took 107 s against 162–167 s from the same start reading (`12-heat-management.md:52-55`). Placements must be interleaved in shuffled blocks from a fixed preheat history.
    - On the full chip, the model's 21 s for +8 °C matches aifoundry3's measured 21–35 s [D3].
- **Does it answer the question?** For "can the same computation run longer before the governor's thermal test fires", yes, exactly: same input, same threshold, same sensors.
  - What it cannot show on these two cards is the consequence. The clock stays at 600 MHz, where on a cool aifoundry2 the thermal step costs up to a quarter of throughput (800 → 600 MHz; `dvfs-leakage.html:419`).
  - Each card's heating rate differs from aifoundry2's at 800 MHz, where dynamic power is about 1.9× at the same work *[inference: (0.618/0.517)² × 800/600]*. The ranking of placements, not the seconds, is what transfers across cards.

### 4.2 Secondary: the peak-hold high after a statistics reset, the only spatial signal

- Start each run with `ettelem sample --reset-ms` (§1). `temp_c.minshire[2]` then reports the hottest sensor's peak during the run, which gives the excess of the hottest shire over the mean.
- Under uniform loads that excess is 2–3 °C (`05-claims.md:39-40`). *[inference]* A concentrated placement should raise it a lot while barely moving the mean.
- This is what a governor keyed to the maximum sensor would react to. So it is the counterfactual needed to explain why the mean rule makes placement matter less than the owner expects.
- It does not say which shire was hottest (brief `html:685`). Its E41 re-test failed its registered band (TEL-R, `03-experiments.md:1238-1239`), so treat it as a coarse signal.

### 4.3 Also usable

- **Steady mean at fixed power.** A placement that settles cooler gives a longer time to the threshold. It needs minutes, because the 400 s stage holds most of the resistance (`11-thermal-model.md`, model table), but chaining 2 s launches for up to 900 s has precedent (V3-IDLE: `idle/block.sh:59`, `03-experiments.md:1317-1347`).
- **aifoundry2 at a higher band.** When aifoundry2 is not cool: strict start at 80 °C, then the time for the mean to reach 88 °C per placement (E12's method as chained ≤ 10 s launches). This tests whether the placement ranking holds on a third card. It does not involve DVFS.
- **Not the SP trace.**
  - The trace is a 4 KB ring (`R/tools/ettelem/parse_sptrace_voltage.py:15`).
  - In the campaign's governor readouts, 44–48 of its roughly 60 lines were the host's own management requests [derived: `strings -n 8` over `V3/raw/<card>/tel/p<N>/gov/sp1.bin`].
  - It held no governor line on any card in 9 passes (`tel.json` TEL-G `down_lines` / `up_lines` = 0). The registered prediction of at least 5 throttle lines on aifoundry3 failed (`03-experiments.md:1239-1240`).

### 4.4 A caveat the theories should carry *[inference]*

The mean of a uniform grid of sensors (one per tile, `PRM p.17`) tracks the die's average temperature. With uniform heat removal into the heatsink, that average depends on total power, not on where the power is spent. So the thermal test is, to first order, blind to placement.

Placement can still move the mean through second-order effects:
- **Uneven cooling:** airflow direction across the heatsink, and where the heatsink spreads heat.
- **Neighbours:** the eight memory shires sit beyond the top and bottom rows of the latency map (brief `html:786`).
- **Leakage feedback:** a concentrated hot region leaks more, because leakage is exponential in temperature (`11-thermal-model.md`, power line). This favours spreading the load.

Board power must be recorded per run, and runs compared on switching power (`14-card-behaviour.md:235-240`).

**A balanced design from the latency map** (`R/workloads/nocbench/analyze.py:50-60`; the grid is inferred from latency, and which empty cell holds the master, spare, I/O or PCIe shire is not measured, brief `html:786`):
- The interior 4 × 4 holds exactly 16 compute shires: {1, 4, 10, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 26, 29, 30}, `--shires 0x6477f412`.
- The perimeter holds the other 16: {0, 2, 3, 5, 6, 7, 8, 9, 11, 19, 23, 24, 25, 27, 28, 31}, `--shires 0x9b880bed`.
- Each set is 512 minions. The heater takes `--shires MASK` (`R/workloads/sparsity/host/main.cpp:11`).
- Compute shires at the corners are S0 (0,0), S11 (5,0) and S31 (5,5). The centre 2 × 2 is S13, S14, S21 and S22.

---

## 5. (c) Safety limits

**Temperature caps. Enforce them in the script; the firmware will not.**
- **The firmware gives no protection above 600 MHz:**
  - aifoundry2's mean reached 103 °C (peak-hold 106 °C, 83.6 W) at 600 MHz in block `cat` p11 of the campaign (block 91 → 99 °C) [D6]. This is not written up anywhere in the findings.
  - aifoundry1 card 0 read 115–117 °C idle (A4).
  - The 75 °C PMIC alarm reads a register that stays at 0 (§1).
  - Board power reached 86.2 W on aifoundry1 card 1 with no response [D3]. So the PMIC's 75 W power alarm (`FW:include/bl2_pmic_controller.h:267`) did not act either. Why is not established.
  - No manufacturer limit is published (`MAN/…Datasheet` p.31–32).
- **Precedents in the repo:**
  - E12 stopped a run when the mean read 90 °C or the board reached 73 W. "90 °C is inside what this card had already seen (93 °C, 70 W in E7)" (`03-experiments.md:249-252`).
  - V3-IDLE heated to 88 °C (aifoundry2, aifoundry1 card 1) and 90 °C (aifoundry3) (`idle/block.sh:13-15,53-54`). At those caps the peak-hold high peaked at 90–93 °C [D3].
- **Proposed caps** *[inference, within those precedents]*:
  - Stop launching when the mean reads ≥ 88 °C, or the peak-hold high (reset at the run's start) reads ≥ 93 °C, whichever comes first.
  - For concentrated placements the high is the binding cap. The hottest shire can exceed the mean by more than the 2–3 °C seen under uniform loads, and the host has no other view of it.
  - The time-to-66 °C proxy never needs more than about 70 °C. Stopping each run a few degrees after the crossing keeps the whole experiment far below the caps and shortens cool-back.
  - Board-power cap: 73 W, as in E12. aifoundry1 card 1's all-chip heater exceeds it (86 W, [D3]), so use partial-chip placements only on that card.

**Process rules. All of them are already in the framework; use it, not ad-hoc scripts** (`R/AGENT.md:221-253`).
- **10 s per process.** Every device process goes under `hold10` = `timeout 10` (`R/CLAUDE.md:73`; `lib.sh:99-100`). Sustained heating means back-to-back 2 s heater launches, at most 150 bursts or 900 s (`idle/block.sh:59,66,186-187`), with the 10 Hz sampler held open for the cycle (`idle/block.sh:21-25`). Minutes-long single processes are forbidden: E47 was not run for that reason, and decision D1 kept the rule (`03-experiments.md:1422-1425`; `V3/README.md:20-22`).
- **Nobody else on the card.** `others_present` and `ours_running` at the start (`lib.sh:62-97`). The card lock is held for the block (`lib.sh:179-186`). Abort on another user or device process during heating or idle (`idle/block.sh:182-184,207-211`). Check `et-who` before and after (`R/CLAUDE.md:71-72`).
- **Sampler.** Stop it with SIGTERM only, and drain once on a failed start (`lib.sh:146-176`; `14-card-behaviour.md:281-287`). Never open a second management reader while the sampler runs; read the die from the sampler's output (`idle/block.sh:23-25`).
- **No configuration change.** No TDP change (this also rules out un-pinning aifoundry3), no change to the 65 °C threshold or the clocks, no card reset, no firmware or driver change (`R/AGENT.md:155`; `14-card-behaviour.md:211-216`). So the governor cannot be made to act on aifoundry3 or card 1, and per-shire temperatures cannot be exposed.
- **Before any real run:** `V3_DRY=1`, then `--smoke`, then the real run (`R/AGENT.md:234-242`). Do not rebuild a build directory that a running queue uses, and do not deploy to its host (`R/AGENT.md:192-204`).
- **Pre-register before data**, with at least three independent repeats per placement per card (`V3/README.md:15-18`; `R/AGENT.md:249-253`).
- **Budget three to eight times more wall-clock than card time** (`14-card-behaviour.md:131-132`).

**aifoundry1 card 0 while card 1 runs.**
- Card 0 must have no process and no lock holder for the whole block. `others_present` on a two-card host checks device-node holders and CI jobs (`lib.sh:65-78`).
- Card 1's heating warms the air card 0 breathes *[inference, from the shared chassis: `idle/block.sh:216`]*.
- Card 0's resting temperature at its 300 MHz idle is not recorded in the repo. Checking it would mean opening card 0's single-opener management node, even read-only for 1 s, which needs the owner's approval. Without that check, keep card 1's blocks short (a partial-chip heater, stop soon after 66 °C) and space them apart.
- If a CI job appears on either card (`Runner.Worker`), abort (`lib.sh:59-60`).

**Suggested card roles** *[inference]*.
- **Develop on aifoundry3.**
  - Its idle is below the threshold, and it cools from 90 °C to 54 °C within 900 s [D3].
  - No neighbour card; no DVFS confound.
  - Three full heat–cool cycles ran in one night, all 407 launches clean [D3, D4].
- **Test on aifoundry1 card 1**, which also idles below the threshold and differs in firmware and chassis.
- **aifoundry2 as a conditional third card:**
  - If the gate in §3 passes (≤ 62 °C at rest): the DVFS variant. That is the time at 800 MHz before the first thermal step per placement, plus the one on-card test of "average or one sensor": heat a few shires so that the peak-hold high exceeds 66 °C while the mean stays ≤ 64 °C; a clock that stays at 800 MHz confirms the mean rule.
  - Otherwise: the 80 → 88 °C band proxy.

---

## 6. Not established

- The exact governor build on the 1.3.1 cards (`16-dvfs-and-leakage.md:215-219`); any source for 1.2.0 (aifoundry1 card 1) or 1.4.1 (card 0).
- Why aifoundry1 card 1 never steps up (§2.3).
- The numeric value of `POWER_THROTTLE_STATE_THERMAL_IDLE` relative to `THERMAL_DOWN`: the enum is not in the tree at `cafe03fc3^` (git grep finds only its uses). It decides whether the cards' governor re-arms its thermal test after a thermal episode without an idle in between.
- Whether the PMIC's 75 W over-power alarm is armed on these cards (§5).
- Where on the die the master, spare, I/O and PCIe shires sit (brief `html:786`), and the physical orientation of the latency grid.
- aifoundry2's resting temperature on the day of the experiment. Only a card reading can tell.
