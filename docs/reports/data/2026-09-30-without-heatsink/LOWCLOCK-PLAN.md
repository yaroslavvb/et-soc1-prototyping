# LC: the ET-SoC-1 at a low minion clock, heatsink on, then bare: a measurement plan (design only, not run)

> **Repository copy.** Copied unchanged below this note on 30 September 2026 (about 21:30 PDT) from the working file
> `~/claude/work/lowclock/plan.md` (md5 `fc7b9422dadfe78f7e1dae7eeb4701c4`), for the page "Feasibility of running the
> ET-SoC-1 without its heatsink", section 5. **It is a design: nothing in it has run, and every stage needs the owner's
> go-ahead and the lab lead's consent.** Where the text names working files, their repository counterparts are in this
> directory: `FW §n` → `LOWCLOCK-FIRMWARE.md` §n (condensed; same section numbers); [EM] and `model.md` →
> `lowclock_calc.py` / `.out` / `.json`; `~/claude/work/lowclock/imaging/` → `imaging_calc.py` / `.out` / `.json`;
> `lc_plan_calc.py` / `.out` are here as well. `~/claude/work/lowclock/fw/*_ffca4cbb4.*` are line-identical copies of
> `git -C external/et-platform show ffca4cbb4:<path>`. The md5 sums the text gives for `lc_plan_calc.py` and
> `lc_plan_calc.out` are those of the copies here.

Written 30 September 2026, 16:00-17:45 PDT, on aifoundry2, for the owner's question of that afternoon (~15:45 PDT): how
low can the minion clock go (100 MHz? 10 MHz?), what is the envelope, and can a card run about ten times slower
without its heatsink so that a thermal camera sees where the computation runs. Revised 20:50-21:20 PDT: the script is
renamed `lc_plan_calc.py` (the first name collided with the envelope model's `lowclock_calc.py`), and the envelope
model's predictions are registered beside this plan's (§4.5, item B-MODEL).

**Nothing here touched a card.** No `/dev/et*` node was opened, nothing ran on a card, and no clock, voltage, TDP or
power-management setting was changed. The only contact with a lab host was two read-only `ssh` looks at aifoundry3:
uptime, the clock guard's marker, `et-who`, the service list, and the driver's world-readable error counters.

**Every stage below runs only with the owner's go-ahead and the lab lead's consent** (§8). Stage B and the bare-card
step each need their own approval, given after the previous stage's report.

**Labels.** Every number carries one of these:

| Label | Meaning |
|---|---|
| [meas: path] | a measurement already in the repository |
| [src: file:line] | read from firmware or driver source. `BL2/` = `external/et-platform/device-bootloaders/src/ServiceProcessorBL2/` at `ffca4cbb4` (BL2 0.20.0, the 1.3.1 build that aifoundry2 and aifoundry3 run); copies are in `~/claude/work/lowclock/fw/*_ffca4cbb4.*` |
| [model: §X] | printed by `lc_plan_calc.py`, section X of `lc_plan_calc.out` (§F imports the set's `nohs_calc.py` and checks it still reproduces `nohs_calc.out`) |
| [EM] | the envelope model: `lowclock_calc.py` and its `lowclock_calc.json` (the model agent's, `~/claude/work/lowclock/model.md`), restated in this plan's terms by `lc_plan_calc.py` §K |
| [inf] | my reasoning: not measured, and not source text |
| [ext: ref] | an outside source (the page's [n], or `outside.md`'s On) |
| FW §n | the firmware notes `~/claude/work/lowclock/fw.md`, section n |
| ASSUMED | an assumed input, named where it is used |

**Files.**
- `lc_plan_calc.py` (md5 `0fdee447029666abfa3994dc4877b3b1`) and its printout `lc_plan_calc.out` (md5
  `de2d17f3ee0743fc87666e6f06326224`). They are in `~/claude/work/lowclock/plan/` and, identical and not committed, in
  `docs/reports/data/2026-09-30-without-heatsink/`, where the script finds the repository from its own path. The
  printout was made there.
- It reads committed data only: E44's cooling cycles, E51's raw telemetry, E46's unmetered fit, E20's switching
  powers, the `nohs_calc.py` model and (§K only) the envelope model's `lowclock_calc.json`. Run time is about 5 minutes
  (`nice -n 19`). Rebuild order in that directory: `imaging_calc.py`, then `lowclock_calc.py`, then `lc_plan_calc.py`.
- Its first version, under the envelope model's file name, is kept in `plan/superseded/`; it must not be copied into
  the repository, where it would overwrite the envelope model. Sections A-J of the two printouts are identical except
  that section D now prints its falls as positive numbers.

---

## 0. The plan in brief

1. **The card is aifoundry3's.** It is the only card on which a low clock holds and a single-card host keeps the
   stock tools off other cards. Its firmware path for the clock command runs at every boot. It is not the host this
   agent runs on. Every other card has a disqualifying reason (§3).

2. **Two stages, heatsink on.**
   - **Stage A** steps the minion clock 600 → 400/300/200/100 MHz and back, at the card's own voltages, on an idle die.
     It reads the board and rail power jump at each step, so the die temperature is fixed by construction.
   - **Stage B** holds 100 MHz and steps the minion voltage from 525 down to 400 mV and the SRAM from 700 to 660 mV.
     These are the firmware's lowest accepted values. Then it dwells 10 minutes at the lowest point.
   - Card time: about 34 and 18 minutes [model: §H]. Device processes are capped at 10 s each.

3. **The record already predicts most of the answer.** All of these are model numbers from measured data.
   - **The clock alone removes little.** The part of the idle power that depends on the clock is at most what does not
     follow temperature. On aifoundry3 that is ≤ 3.5 W on the minion rail and ≤ 0.8 W on the SRAM rail [model: §A].
     So 600 → 100 MHz should take 0.6-3.6 W off a 25.3 W idle board (5-95 %), and at most 4.1 W (16 %) [model: §D].
   - **Voltage does more.** aifoundry2's idle reset moves 800 → 600 MHz on an idle card (619 → 519 mV minion, 830 →
     704 mV SRAM). Its board step is 7.40 W (19 events) [meas, §B]. Read together with that bound, the leakage goes as
     V^2.26 to V^2.82 [model: §C]. Then 400 mV halves the minion leakage (×0.47-0.54), and 660 mV cuts the SRAM's by
     about 14 %.
   - **At the lowest settable point** (100 MHz, 400/660 mV) the idle board should read 18.7-19.8 W at 56 °C, 22-26 %
     below today's 600 MHz idle [model: §E].
   - **Bare, it still does not settle in still air** (0 % of draws). With a 1-2.5 m/s fan, about 20 % of draws settle
     [model: §F].
   - **With a 3-6 m/s blower, about 70 % settle, but only 44 % of power-ons stay below an 80 °C stop and end at or
     below 70 °C** [model: §F]. The settling shares are up from 0 %, 0 % and 4 % for the card as it is. (Revised 30
     September after review: the power-on model's blower now takes its board-to-air resistance from `nohs_calc.py`'s
     own formulas, 1.14-2.31 °C/W, instead of an assumed 0.5-1.5 °C/W, which had given 80 %.)
   - The board path (θ_JB, ASSUMED 1-3 °C/W in `nohs_calc.py`) sets the floor of every air-cooled θ_JA.
   - **The envelope model behind the page agrees on the step and the low point but not on the exponent** [model: §K].
     It predicts a 1.07-2.43 W clock step, 19.6-20.2 W at the low point and n = 1.92-2.35, against this plan's
     2.26-2.82. Stage B decides between them (§4.5).

4. **A hazard found while designing this.**
   - aifoundry3's governor is latched in a loop that runs for ever. At a clock that is not in the card's operating-point
     table, that loop logs one ERROR line per pass [src].
   - BL2 0.20.0 turns every ERROR line into a CRITICAL "SP Runtime Error" event to the host (`RT_ERROR_THRESHOLD 0`)
     [src]. The driver prints each event to the kernel log with no rate limit [src].
   - So setting 100 MHz on the card as it usually is could flood the host with hundreds of events a second [inf].
   - The plan avoids it:
     - start from a boot with no kernel since (S0);
     - turn active power management off first, which gates both governor triggers [src];
     - watch the driver's `SpCeEvent` counter as a stop rule (§2.2, §7).

5. **The voltage stage carries a host-level risk.** A voltage write that the regulator path refuses loops inside a
   critical section until the 10 s watchdog resets the SoC [src]. Whether this host survives a reset it did not ask for
   is not known. The PCIe retrain of 30 September hung aifoundry1 until someone power-cycled it on site. So Stage B
   needs someone reachable who can power-cycle aifoundry3, and nobody else working on that host (§7.4, §8).

6. **The bare step comes only after the measurement agrees with the model** (§9). It needs:
   - someone on site;
   - a lid thermocouple on an independent logger;
   - an automatic, latching power cut at 80 °C on that thermocouple;
   - a blower-class airflow;
   - a modelled success rate of at least 80 % with the measured law.

   On today's predictions no cooling class reaches 80 % (a blower 44 %, a fan 21 %), so the bare step goes ahead only if
   Stages A and B find a lower power law than predicted, or with stronger cooling than a 3-6 m/s blower.

7. **Below 100 MHz** (25 or 10 MHz) no command reaches. It would need a signed BL2 or JTAG [src: FW §2]. The model
   says it would gain almost nothing: the clock-dependent idle power left at 100 MHz is at most 1/6 of ≤ 3.5 W.

---

## 1. What the model needs, and the smallest experiment that gives it

The bare-package model (`nohs_calc.py`) decides whether a bare card settles. Its inputs:
- the card's idle board law P(T) at the operating point;
- the share of that power on the die;
- the slope dP/dT, which sets the runaway loop gain θ·dP/dT;
- the bare θ_JA.

The record has the law at 600 MHz only. At a lower clock and voltage, three unknowns decide the new law:

| Unknown | What it is | Why heatsink-on can measure it | Stage |
|---|---|---|---|
| **D**, per rail | the idle power that follows the minion clock (clock tree, shire-cache and mesh-stop clocking, the master minion's idle loop) | a clock step at a fixed die temperature changes only D | A |
| **n** | leakage's voltage exponent, P_leak ∝ V^n, for the minion and SRAM rails | a voltage step at 100 MHz, where D is at most 1/6 of its 600 MHz value, changes mostly leakage | B |
| **the low point's law and slope** | P(T) and dP/dT at 100 MHz, 400/660 mV | a 10-minute dwell at the low point cools the die by several degrees | B |

Out of scope:
- θ_JA bare cannot be measured with the heatsink on. Only the bare step measures it, protected by the power cut (§9).
- The camera and the image are planned separately (`~/claude/work/lowclock/imaging/`).

**Kept small:**
- one card (no second card qualifies, §3);
- 4 clock levels and 4 passes;
- one voltage ladder down and up;
- 17 voltage writes and about 51 clock writes in all [model: §H].
- The load item (A3) and the hot item (A4) are optional and can be dropped without losing a primary item.

---

## 2. Firmware facts the design rests on

### 2.1 The clock command (FW §1, §2)

- **The command.** `DM_CMD_SET_FREQUENCY` reprograms the step-clock PLL (SP PLL4) that every minion shire runs from.
  - It changes no voltage, and its only check is that the mode exists [src: `BL2/services/thermal_power_monitor.c:875-920`].
  - Below 300 MHz the table offers 100, 125, 150, 166, 175, 200, 225, 250 and 275 MHz [src: FW §2].
  - 100 MHz is mode 62, DCO 1100 MHz ÷ 11. 300 MHz is mode 66 (1200 ÷ 4) and reads back as exactly 300 [src:
    `BL2/driver/io_pll.c:912-934` `calculate_pll_freq`; FW `pll_modes.out`].
- **The stock CLI always re-locks the NoC PLL.** `dev_mngt_service -m DM_CMD_SET_FREQUENCY -f <minion>,<noc>` sends the
  NoC PLL first and then the minion PLL [src: `device-management-application/src/dev_mngt_service.cc:771-796,
  1706-1728`].
  - Each call therefore also re-locks the NoC PLL at 400 MHz: bypass to 100 MHz, reprogram, lock, un-bypass [src:
    `io_pll.c:707-745`].
  - aifoundry3's clock guard does exactly this at every boot (`-f 600,400`) [meas:
    `docs/reports/data/2026-09-25-aifoundry1/facts.md:205-213`]. The vendor's own test uses it too (FW §2).
  - If a PLL fails to lock, it is left bypassed at 100 MHz, and no code path hangs: lock waits are bounded at 10,000
    polls × 3 tries, with no critical section [src: `io_pll.c:413-434, 748-786`].
- **The clock reading is a register decode.** `mhz.minion` decodes PLL4's registers, so the true clock is checked by
  work rate: kernel cycles over wall time [src: FW §1]. `sparsity_host` prints this per launch as `ghz`
  [src: `workloads/sparsity/host/main.cpp:260`]. With its default small-integer inputs it also checks every result
  exactly (`ok`, `tensor_errors`) [src: same file, header].
- **The master minion's timers do not slow with the minion clock.** They run on the PU timer, which counts at about
  95 MHz: 100 ticks of 10^6 counts take 1.05 s on the card [meas: REV §1.4; inf: independent of the minion clock].
  - At 100 MHz its 10-tick (≈ 105 ms) wait for the compute minions to acknowledge a launch [src:
    `device-minion-runtime/src/MasterMinion/src/workers/kw.c:285-320`, `kw.h:41`] has to cover a handshake that is
    6 × slower. That margin is not established.
  - The probe (A1) tests it at each level before any pass uses the level.

### 2.2 The governor on aifoundry3, and the event flood (new)

- **Why the card holds whatever clock it is set to.** aifoundry3's clock guard sets a 0 W TDP and 600/400 MHz at every
  boot [meas: facts.md, above; and this boot's marker `/run/et-board-clock-guard.ok` = `… 600 400 0`, read 30 Sep 16:31].
  On 0.20.0 the first kernel after boot then sends the power task into a POWER_DOWN loop that never exits. Its exit
  needs an average under 1.05 × 0 W, or a clock of 300 MHz [src: `BL2/services/thermal_pwr_mgmt.c:2133-2256`; REV §4].
  Call this state **S1**; a boot with no kernel since is **S0**.
- **At an off-table clock the loop logs an ERROR on every pass.** Each pass calls `reduce_minion_operating_point()`.
  At 600 MHz (table point 0) the "previous" point is 600, so nothing is logged. At any clock not in the card's
  operating-point table the lookup fails and logs ERROR "Failed to find input frequency in vmin lut" [src:
  `thermal_pwr_mgmt.c:1899-1914`; `BL2/driver/flashfs.c:2389-2404`]. The loop has no delay. Each pass is an I2C read
  of the PMIC average [src: `thermal_pwr_mgmt.c:2219`; `BL2/driver/pmic_controller.c:2253-2257`], so a pass takes a few
  milliseconds [inf].
- **Every ERROR line becomes a host event.**
  - `Log_Write` counts every ERROR line, and once the count passes `RT_ERROR_THRESHOLD` it sends the host a CRITICAL
    `SP_RUNTIME_ERROR` event [src: `BL2/services/log.c:250-297, 419-440`]. The threshold is **0** [src:
    `BL2/include/config/mgmt_build_config.h:384`].
  - The driver prints each event with `dev_info`, about five lines, with no rate limit [src:
    `et-driver/et_event_handler.h:188-198`, `et_event_handler.c:703-707`].
  - So an off-table clock on an S1 card should send hundreds of events a second, for as long as the clock stays there
    [inf from source; never seen, because no clock off the table has been set on a lab card].
  - aifoundry2's kernel log of 28 September has an "SP Runtime Error … Runtime Error Count Beyond Threshold: 6" line
    [meas: `14-card-behaviour.md`, the hang section]. With a threshold of 0 that is the sixth ERROR line since boot,
    each sent as its own event [inf from the source above].
- **Turning active power management off silences it.** APM is a RAM flag, on at boot [src:
  `thermal_pwr_mgmt.c:1696-1700`]. Both governor triggers test it: the thermal one tests it for truth (`:668-670`), the
  power one for `== 1` (`:844-845`). APM off therefore starts no loop, and in S0 nothing runs at all [src]. The PMIC
  alarm path (75 W, or the PMIC's own temperature, which reads 0) does not test APM; it is not expected near idle
  [src: REV §6].
  - APM off does not stop a loop that is already running (S1) [src: REV §8].
  - The stock CLI sets it with `-m DM_CMD_SET_MODULE_ACTIVE_POWER_MANAGEMENT -p 0|1`. No command reads it back [src:
    `device_mgmt_api_spec.h`; `dev_mngt_service.cc:1575-1580`]. So it is verified by behaviour: with APM on, the first
    kernel after it would log the CRITICAL "Power throttle down event" line in the SP ring, and with APM off it does not
    [src: `thermal_pwr_mgmt.c:862-873`].
- **From S1 there is a one-event way out** [inf from source; not tried]. With APM off, setting 300 MHz makes the
  spinning loop log one ERROR and then exit, because 300 MHz is `SAFE_STATE_FREQUENCY`, one of its exit conditions
  [src: `BL2/include/thermal_pwr_mgmt.h:66`; `thermal_pwr_mgmt.c:2238-2246`]. After that no loop runs, and APM off
  keeps it so.
  - **There is a race** [src for each step; inf that the window can be hit]. The loop's
    `reduce_minion_operating_point()` reads the clock (600) at `thermal_pwr_mgmt.c:1901`. Its
    `set_minion_operating_point(600)` then compares that with the clock again at `:1788`, and acts only if they
    differ. The command's path (`thermal_power_monitor.c:875-920` → `Minion_Configure_Hpdpll`,
    `minion_configuration.c:674-722`) reprograms PLL4 and then updates the clock variable (`:722`). No lock is shared
    between the two tasks: `io_pll.c` `configure_sp_pll_4` (`:748`) takes none.
  - So if the command finishes between `:1901` and `:1788`, the loop sees 600 ≠ 300 and sets 600 MHz back, with the
    table's voltages (`:1801-1849`). The same window exists for any `SET_FREQUENCY` sent while a governor loop runs, on
    any 0.20.0 card: the governor's stale target overwrites the clock the command set.
  - Added 30 September, after review [src at et-platform HEAD `836a4ab`, `BL2/` paths; inf where marked]:
    - **The window is reachable.** The command runs in the host-command task (`SP_PC_VQueue_Task`,
      `rtos_task/command_dispatcher.c:78-83,150-153`, priority `VQUEUE_TASK_PRIORITY` 3) and the governor in `TT_TASK`
      (priority 2; `include/config/mgmt_build_config.h:422,429`; `services/thermal_pwr_mgmt.c:1651-1653`), so the
      command can preempt the governor's loop anywhere, and never the reverse.
    - **HEAD still has it.** `reduce_minion_operating_point_and_update_pwr_status` reads the clock at
      `thermal_pwr_mgmt.c:1890`, and `set_minion_operating_point_and_update_pwr_status` compares at `:1798`. The
      command's handler (`services/thermal_power_monitor.c:870-912`) now calls
      `Minion_Configure_Minion_Shire_PLL_no_mask` and takes no lock; the only mutex in `thermal_pwr_mgmt.c` guards
      `mm_state` (`:159-162`).
    - **It is wider than one comparison.** When the governor raises the clock it first changes the minion and SRAM
      voltages, a blocking regulator write (`Change_Minion_And_L2Cache_Modules_Voltage`, `:1813-1817`), and only then
      reprograms the PLL (`:1824`). A command that completes during the voltage change is overwritten too.
    - **A second variant** [inf, never seen]: if the command preempts the governor inside `configure_sp_pll_4`, two
      PLL4 programming sequences interleave, and the governor then records its own target, not the mode actually
      programmed.
  - The plan sees it in the read-back and retries once.
  - The preferred start is S0: the lab lead reboots aifoundry3 with the demo service stopped (§5.1).
- **The driver's counters are world-readable stop signals** [src: `et-driver/et_sysfs_err_stats.c:161-174`; meas: read
  on aifoundry3 30 Sep 16:33, all zero since the 15:07 boot].
  - The counters are `/sys/bus/pci/drivers/ET/0000:02:00.0/err_stats/{ce_count,uce_count}`: `SpCeEvent`, `SramCeEvent`,
    `SramUceEvent`, `SpWdogUceEvent`, `MinionHangUceEvent`, `DramUceEvent`.
  - `dmesg` is readable too (`kernel.dmesg_restrict` = 0 on aifoundry3) [meas].

### 2.3 The voltage command (FW §3)

- **Range.** `DM_CMD_SET_MODULE_VOLTAGE` (`-v MINION,<mV>` or `-v L2CACHE,<mV>`; 5 mV codes) accepts minion
  400-620 mV and SRAM 660-850 mV on 0.20.0 [src: `BL2/include/bl2_pmic_controller.h:170-221`; FW §3]. It does not
  write the flash (0.18.0 does, for the NoC) [src: FW §3; `14-card-behaviour.md`].
- **The endless retry.** Inside `portENTER_CRITICAL()`, a regulator write or read-back that fails retries for ever. It
  is not counted against the three retries, so the 10 s watchdog resets the SoC [src: `thermal_pwr_mgmt.c:3166-3215`,
  read-back loop `:402-424` with a 1 s timeout per try (`SET_VOLTAGE_TIMEOUT` 10^6 µs, `:362`); watchdog 10 s:
  `mgmt_build_config.h:421`].
  - An on-die (PVT) mismatch over 5 % instead returns an error after at most 3 tries [src: `:366-392`].
  - A whitelist inside the range is therefore the only guard against the first case.
- **Precedent for the floors.** The silicon idles at 400/660 mV: aifoundry1's card 0 (firmware 1.4.1, PMIC 1.6.1) holds
  `reg_mv` minion 400 and SRAM 660 at 300 MHz between kernels, for days [meas: `card0_guard.py`'s
  `guard.jsonl.gz` files, e.g. `2026-09-28-heat-placement/raw/aifoundry1-c1/hp/p5501/guard.jsonl.gz`].
  - Whether aifoundry3's PMIC firmware 1.5.0 accepts 400 mV is not established.
  - No voltage has yet been written on any lab card; NV's first write (E54) also waits for the owner.

### 2.4 What a reset does on aifoundry3

- A card reset (SP watchdog, management reset, sysfs per-card reset) brings BL2 back at its boot values:
  - 600/400 MHz;
  - the flash's voltages (525/700 mV here);
  - APM on;
  - **TDP 65 W**: the clock guard's 0 W is lost [src: FW §6; `14-card-behaviour.md`].
- The guard runs only at host boot. Until the lab lead re-runs it (`systemctl restart et-board-clock-guard`), the
  card's DVFS is live and may lift the clock above 600 MHz. The guard's own comment says this card is unreliable there
  [meas: facts.md:205-213].
- **A host reboot or power cycle restores everything**: BL2's boot values, then the guard. Every setting this plan
  makes lives in the card's RAM.

---

## 3. Which card

| Card (firmware) | Verdict | Why |
|---|---|---|
| **aifoundry3** (1.3.1: BL2 0.20.0, PMIC 1.5.0) | **use** | The latched governor cannot snap the clock back; in S0 with APM off, nothing governs at all (§2.2). Its exact `SET_FREQUENCY` path runs at every boot (the guard's `-f 600,400`), and the guard re-applies 600/400 MHz after any host reboot: a built-in restore on the worst exit path. It is a single-card host, so the stock CLI opens only this card. 0.20.0 range-checks voltages and does not write them to the flash. It idles cool (55-57 °C) [meas: `14-card-behaviour.md` card table]. The agent runs on aifoundry2, so a hang of aifoundry3 does not stop the session. **Against:** the event flood in S1 (§2.2); the lab's demo service launches on the card without taking the card lock, so the lab lead must stop it for the session [meas: `etsoc1-demo.service` running, read 30 Sep 16:31]; a reset loses the guard's TDP 0 (§2.4); its patched `libetrt.so` crashes about 1 host launch in 100 at 1.08 s, unless the program registers its log levels first (our workloads do) [meas: `14-card-behaviour.md`, Traps]. |
| aifoundry2 (1.3.1: BL2 0.20.0) | no | **Its governor is live, so a low clock does not hold.** The card idles above 65 °C inside the thermal loop [meas: E51, 8.65 of 9.23 days]. That loop logs an ERROR (a host event) every 0.4 s at an off-table clock, and sets 600 MHz again when the die cools to 65 °C [src: `thermal_pwr_mgmt.c:2289-2383`, `:1975-1979`]. A kernel at an off-table clock sends its POWER_UP loop into an endless ERROR-per-pass spin [src: `:2173-2236`]. APM off cannot stop a loop already running, so holding a clock needs a second governor setting (a raised threshold) [src: REV §8]. **It is also the host this agent, the checkout and `~/claude/work` live on**, and CI uses its card. |
| aifoundry1 card 1 (1.2.0: BL2 0.18.0) | no | **A two-card host**: the stock `dev_mngt_service` opens every card's management node whatever `-n` says, so every command would also open card 0, which is never to be touched [meas: `14-card-behaviour.md`, "Selecting one card"; `tools/claims-v3/nv/DESIGN.md` §2]. 0.18.0 has no voltage range check and writes every NoC voltage to the flash [src: FW §3]. Its governor's state is unknown (APM off or latched); if live, a "reduce" from 100 MHz would raise the clock to 300 MHz [src: FW §6]. **aifoundry1 is the host the PCIe retrain hung on 30 September**, and its disk is nearly full. |
| aifoundry1 card 0 (1.4.1: BL2 0.21.2) | excluded (the owner) | It overheats (a cooling fault): 115-117 °C on the host on 25 September, and its SP's statistics hold a 119 °C mean [meas: `14-card-behaviour.md`]. Same two-card host and retrain history. Its 0.21.x governor acts while a kernel runs and would log an error on every pass at an off-table clock [src: FW §6]. Its link flooded corrected errors until the 30 September power cycle. |

---

## 4. Theories and numeric predictions (to be frozen in `predictions.json` before the first write)

Reference: aifoundry3, idle, die at T_ref = 56 °C (its rest at 600 MHz), set-points 525/700/485 mV minion/SRAM/NoC
[meas: E44 `reg_mv`]. Its E44 laws at 56 °C give board 25.29 W (slope 0.328 W/°C), minion rail 7.68 W, SRAM 2.15 W,
NoC 2.40 W and unmetered 13.05 W [model: §A]. The delivery loss (unmetered W per rail W) is minion 0.181, SRAM 0.043,
NoC 0.294 [meas: E46 fit, `limits-of-observability.data.json` `power.fit`].

### 4.1 Stage A: the idle step at a lower clock, voltage fixed

**The bound.** Dynamic power does not follow die temperature. So the clock-dependent idle power D of a rail is at most
the part of its idle law that does not follow temperature, P_fix [inf]. P_fix depends on the leakage law's form; all
three forms fit the 54-84 °C span within 0.002 W rms of each other [model: §A]:

| aifoundry3 rail | exponential in T (the set's form) | Arrhenius | T²·Arrhenius (subthreshold) |
|---|---|---|---|
| minion P_fix (band within 10 % of the best rms) | 1.73 (1.23-2.24) W | 3.20 (2.84-3.53) W | 3.00 (2.61-3.35) W |
| SRAM P_fix | 0.29 (-0.01-0.29) W | 0.70 (0.63-0.76) W | 0.69 (0.55-0.75) W |

| Theory | Statement | Predicted board step, 600 → 100 MHz, at T_ref |
|---|---|---|
| **TH-C0** (null) | nothing at idle follows the clock | \|step\| ≤ 0.3 W at every level |
| **TH-CS** (the record) | step(f) = (1 − f/600)·[(1 + 0.181)·D_m + (1 + 0.043)·D_s], with 0 < D ≤ P_fix; the NoC rail does not move; unmetered moves by 0.181·ΔP_m + 0.043·ΔP_s | 0.3 < step ≤ 4.14 W. Joint draws (§4.3): **0.61 / 2.39 / 3.57 W** (5/50/95 %). Largest allowed by form: exponential 2.46, T²·Arrhenius 3.95, Arrhenius 4.14 W [model: §D] |
| **TH-CL** (rival) | more of the idle power follows the clock than any form of the idle law allows | step > 4.14 W |

Per level, TH-CS joint draws (5/50/95 %) [model: §D]:

| 600 → f | board | minion rail | SRAM rail | unmetered | NoC rail |
|---|---|---|---|---|---|
| 400 MHz | 0.25 / 0.96 / 1.43 W | 0.09 / 0.70 / 1.07 | 0.01 / 0.13 / 0.24 | 0.02 / 0.13 / 0.20 | 0 |
| 300 MHz | 0.37 / 1.43 / 2.14 | 0.14 / 1.05 / 1.60 | 0.02 / 0.20 / 0.36 | 0.03 / 0.20 / 0.30 | 0 |
| 200 MHz | 0.49 / 1.91 / 2.85 | 0.19 / 1.39 / 2.14 | 0.02 / 0.26 / 0.48 | 0.05 / 0.26 / 0.40 | 0 |
| 100 MHz | 0.61 / 2.39 / 3.57 | 0.24 / 1.74 / 2.67 | 0.03 / 0.33 / 0.60 | 0.06 / 0.33 / 0.50 | 0 |

Also registered under TH-CS:
- **A-LIN:** the step is linear in (600 − f).
- **A-T:** the 100 MHz step is the same at a 72 °C die as at 56 °C (dynamic power).
- **The slope dP/dT does not change with the clock at a fixed voltage** (0.328 W/°C at 56 °C) [model: §D].
- **The load item, TH-E1:** switching power scales as f at a fixed voltage. aifoundry3's random-normal matmul on 1,024
  minions adds 24.86 W at 600 MHz [meas: E20, `2026-09-22-dvfs-aifoundry2/dvfs.json` `cards.patterns`]. Predicted:
  12.43 W at 300 MHz and 4.14 W at 100 MHz; ones 9.68 → 4.84 → 1.61 W [model: §I].
- **The readings that answer "how cool".** With its heatsink, clock-only 100 MHz should settle the idle die at 47-49 °C
  (ambient 22-28 °C) if D is at the top of its band, against 56 °C now. A smaller D leaves it nearer 56 °C
  [model: §J].

### 4.2 Stage B: the minion and SRAM voltage at 100 MHz

**The record's exponent.** aifoundry2's idle reset (800 → 600 MHz on an idle card) moves the board by 7.40 W [meas:
§B]:
- median of 19 events, bootstrap 95 % 7.28-7.53 W;
- die 60-65 °C;
- on-die 619 → 519 mV minion and 830 → 704 mV SRAM;
- 0.3-1.1 s after the kernel ended, each event read from E51's raw 10 Hz telemetry.

Write the step as leakage (∝ V^n) plus dynamic power (∝ f·V²). Then each D on aifoundry2 fixes one n
[model: §C]:

| D_m on aifoundry2 at 600 MHz | 0 | 0.5 | 1.0 | 1.5 | 2.0 | 2.5 | 3.0 | 3.5 W |
|---|---|---|---|---|---|---|---|---|
| n that reproduces the 7.40 W step | 2.81 | 2.76 | 2.70 | 2.64 | 2.57 | 2.49 | 2.39 | 2.28 |

With aifoundry2's bound (D_m ≤ 3.40 W, the union of the forms), **n lies in [2.26, 2.82]**, central 2.55 [model: §C].
This is steeper than the FinFET textbook 1.5-2.4 (NV DESIGN.md §3) and than DIBL alone with N7's figures, 1.74
[ext: O11 via `outside.md`; model: §C]. One assumption: both rails share one n.

| Theory | Statement | Minion leakage factor, 525 → 400 mV |
|---|---|---|
| **TH-V0** (null) | the rail reading does not follow the set-point | n ≤ 0.5 |
| **TH-VD** (rival: textbook DIBL) | n in [1.4, 2.26) | ×0.540-0.683 [model: §C] |
| **TH-VS** (the record) | n in [2.26, 2.82] | **×0.465-0.540** (central ×0.500) [model: §C] |
| **TH-VX** (steeper) | n > 2.82 | below ×0.465 |

Predicted at 100 MHz and 56 °C, from the joint draws (5/50/95 %) [model: §E]:

| Set-points (minion/SRAM) | minion rail | SRAM rail | board |
|---|---|---|---|
| 525/700 (clock step only) | 5.01 / 5.94 / 7.45 W | | 21.7 / 22.9 / 24.7 W |
| 500/700 | 4.48 / 5.26 / 6.50 | | 21.1 / 22.1 / 23.6 |
| 475/700 | 3.98 / 4.63 / 5.64 | | 20.5 / 21.3 / 22.6 |
| 450/700 | 3.52 / 4.04 / 4.86 | | 19.9 / 20.7 / 21.7 |
| 425/700 | 3.08 / 3.50 / 4.15 | | 19.4 / 20.0 / 20.8 |
| 400/700 | 2.68 / 3.01 / 3.51 | 1.55 / 1.83 / 2.12 | 18.9 / 19.4 / 20.1 |
| 400/680 | | 1.44 / 1.70 / 1.97 | 18.8 / 19.3 / 19.9 |
| **400/660 (the lowest settable point)** | 2.68 / 3.01 / 3.51 | 1.34 / 1.57 / 1.82 | **18.7 / 19.2 / 19.8 W** (22-26 % below 25.29) |

- Under TH-VD (n = 1.8) the lowest point reads 20.26 W; under TH-V0, 23.18 W [model: §E].
- **C-METER** checks the meter itself. While only the minion set-point moves, the board should change by 1 + k_m =
  **1.181** W per W of minion rail. A meter that reported current × a fixed voltage would give 1.83-2.11 instead
  [model: §E]. The pass band is [0.9, 1.6], as in NV.
- **The dwell (B-DWELL).** Held at the lowest point with its heatsink, the idle die should settle at 45-48 °C (ambient
  22-28 °C), at a board of 17.2-17.6 W and a slope of 0.15-0.16 W/°C [model: §I]. For comparison, card 0 idles at
  300 MHz, 400/660 mV: 17.97 W at 62 °C, slope 0.207 W/°C [meas: `card0_guard.out`; a different card and firmware].

### 4.3 The cross-prediction that ties A to B (registered)

n is the process's, and D transfers between the two 1.3.1 cards by their switching scale [inf]. aifoundry3 switches
0.924 × aifoundry2 (E20) and 0.93-0.99 × (version 3) [meas: `11-thermal-model.md`; `16-dvfs-and-leakage.md`, "Not
established"]; the script draws 0.92-0.99, times (525/520)² for the voltage [inf]. So **the D_m that
Stage A measures on aifoundry3 predicts the n Stage B must find** [model: §C]:

| D_m measured (aifoundry3) | 0 | 0.5 | 1.0 | 1.5 | 2.0 | 2.5 | 3.0 | 3.5 W |
|---|---|---|---|---|---|---|---|---|
| n predicted for Stage B (±0.05; the item's tolerance is ±0.15) | 2.81 | 2.76 | 2.70 | 2.64 | 2.56 | 2.48 | 2.38 | 2.26 |

If it fails, either the leakage is not a single power law in V, or the two rails' exponents differ (B reports n_SRAM),
or the transfer between cards fails. The bare model then uses the measured n directly.

### 4.4 What the outcomes mean for a bare card (the reason to measure)

From `nohs_calc.py`'s model, imported and run with each scenario's law [model: §F]:

| Operating point (aifoundry3) | board at 56 °C | SoC at 56 °C | largest θ_JA for an idle equilibrium ≤ 70 °C (worst … best case) | still air (θ 4-12) | fan 1-2.5 m/s (θ 2-7) | blower 3-6 m/s (θ 1.8-3.0) |
|---|---|---|---|---|---|---|
| 600 MHz, 525/700 (as it is) | 25.29 W | 17.8-20.8 W | 1.52 … 2.14 °C/W | 0 % | 0 % (1 of 600) | 3 % |
| 100 MHz, 525/700 (clock only, D at its largest) | 21.15 | 14.2-17.2 | 1.76 … 2.54 | 0 % | 6 % | 29 % |
| 100 MHz, 400/660, central (D_m 2.09 W, n 2.42) | 19.18 | 12.5-15.5 | 2.08 … 3.07 | 0 % | 18 % | 64 % |
| 100 MHz, 400/660, small D and steep n | 19.44 | 12.7-15.7 | 2.08 … 3.07 | 0 % | 21 % | 65 % |
| 100 MHz, 400/660, rival n = 1.8 | 20.26 | 13.5-16.5 | 1.95 … 2.84 | 0 % | 13 % | 48 % |

The last three columns are the share of 600 Monte Carlo draws with a stable idle equilibrium at or below 70 °C.

Notes on the table [model: §F]:
- The blower's θ_JA comes from `nohs_calc.py`'s own convection formulas at an ASSUMED 3-6 m/s: 1.82 / 2.37 /
  3.03 °C/W. The board path, θ_JB ASSUMED 1-3 °C/W, keeps even strong airflow above about 1.8 °C/W.
- **Power-on**, with the central low point: a cold start idles at 600 MHz for the host boot (30-90 s, `nohs_calc.py`'s
  ASSUMED window) plus 20-60 s to set the low point, then the low point until 30 min. Over 300 draws:

  | Air | peak stays below 80 °C | ends at or below 70 °C | both |
  |---|---|---|---|
  | still | 0 % | 0 % | 0 % |
  | fan | 25 % | 22 % | 21 % |
  | blower | 54 % | 45 % | **44 %** |

  The blower's board-to-air resistance is drawn from the same formulas at 3-6 m/s, 1.14 / 1.61 / 2.31 °C/W (revised 30
  September; an assumed 0.5-1.5 °C/W had given 84 %, 82 % and 80 %).

**What this means:** the lowest settable point turns "never" into "about two times in three, with a blower" for a card
that has settled, but under half of cold power-ons get there below the stop. It is not "safe bare". Stages A and B replace the two biggest unknowns, D and n, with measurements. After them the bare question
rests on θ_JA alone (§9).

### 4.5 The envelope model's predictions, registered beside these

The page's low-clock section rests on a second model, the envelope model [EM] (`~/claude/work/lowclock/model.md`). It
fits one minion clock tree shared by the three cards and a leakage law G(V) = (V/V0)·e^(κ(V−V0)) to two anchors:
aifoundry2's idle at 800 and 600 MHz, and card 0's rails at 300 MHz, 399 mV. Its SRAM exponent is a wide prior held
only by the SRAM rail's part of the 800 MHz step (its 830 mV there is recorded in E51; added 30 September after review,
which moved the numbers below). Both models start from the same 600 MHz law (25.29 W at 56 °C). Restated in this plan's terms [model: §K]:

| Item | This plan | Envelope model [EM] | What the measurement decides |
|---|---|---|---|
| A-STEP, board, 600 → 100 MHz | 0.61 / 2.39 / 3.57 W | 1.07 / 1.86 / 2.43 W | Both lie inside TH-CS. A step above 2.43 W or below 1.07 W is outside the EM's 5-95 % band. |
| the same, 600 → 400 / 300 / 200 MHz | §4.1 | 0.43 / 0.74 / 0.97, 0.64 / 1.11 / 1.46, 0.86 / 1.49 / 1.95 W | |
| B-N, the minion exponent fitted over 525-400 mV | 2.26-2.82, central 2.55 | 1.92 / 2.15 / 2.35 (κ 2.00 / 2.49 / 2.93 per volt) | n below 2.26 favours the EM, above 2.35 this plan; 2.26-2.35 fits both |
| minion leakage factor, 525 → 400 mV | ×0.465-0.540 | ×0.527-0.592 | |
| B-NS, the SRAM exponent | equal to n (assumed) | 2.0 / 2.8 / 4.1 (a wide prior, held by the 800 MHz step) | a difference over 0.5 refutes this plan's shared n |
| B-LOW, 100 MHz, 400/660 mV, 56 °C | 18.7 / 19.2 / 19.8 W | 19.57 / 19.90 / 20.21 W | this plan inside the registered band [18.4, 20.1] W; the EM's top 5 % above it |
| board slope at that point, 56 °C | 0.215 W/°C (central, §F) | 0.224 W/°C | |

The EM's 56 °C values are interpolated from its 40 and 60 °C rows with its own median slopes [model: §K].

**Why they differ on n** [inf]:
- Both read aifoundry2's 800 → 600 MHz idle step: this plan 7.40 W from 19 idle-reset events, the EM 7.12 ± 0.72 W from
  the idle laws [model: §B; EM].
- This plan gives the SRAM rail the minion's exponent, so the minion rail must carry most of the step, and n comes out
  steep.
- The EM lets the SRAM exponent range more widely (its draws give the SRAM 0.7-1.6 W of the 800 MHz step), and it adds
  card 0's 300 MHz minion rail (a different card and firmware) as a second anchor. Both pull its n down; the two anchors
  also pull against each other (about 2.5 % of the EM's prior draws pass both).
- Stage B measures the two rails' exponents separately, so it decides between the models (item B-MODEL, §6). B-CP, the
  cross-prediction from A to B, belongs to this plan only.

**On the bare verdict the two agree.**
- At 100 MHz, 400/660 mV, still air settles in 0 % of draws in both.
- With a fan: 15 % settle below 85 °C [EM: `lowclock_calc.out` §F], against 18 % at or below 70 °C here [model: §F].
- With the heatsink, that point settles at a 47 °C die [EM], against 45-48 °C here (§4.2).

---

## 5. The measurement

### 5.1 Stage 0: read-only state and baseline (no write; about 20 minutes of wall time)

Before Stage 0:
- The lab lead stops `etsoc1-demo.service` on aifoundry3 for the session and says whether anything else launches
  there. The chatbot service, an LLM on `llama_cpp`, appears not to use the card [meas: the unit file]; the lab lead
  confirms.
- The owner announces "using aifoundry3" on the lab's Discord.

Then, from the checkout's twin on aifoundry3 (`~/nekko`), detached with `setsid nohup … < /dev/null &`, each device
process under `timeout -k 3 10` and the card lock:

1. **Host checks.** `et-who --check` (0 = free), `who`, `uptime`, `et-lab-manifest > manifest.txt`,
   `cat /run/et-board-clock-guard.ok` (this boot's id, `600 400 0`), the driver counters
   (`cat /sys/bus/pci/drivers/ET/0000:02:00.0/err_stats/{ce_count,uce_count}`), and
   `dmesg | grep -c 'Error Event Detected'`.
2. **Identity.** `dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000` must read release 1.3.1,
   BL2 0.20.0. Then `DM_CMD_GET_MODULE_UPTIME`.
3. **The operating-point table.** `DM_CMD_GET_VMIN_LUT` writes `dev0_vmin_lut.bin`; parse its 11 points [src:
   `service_processor_BL2_data.h:77-100`].
   - **Stop if 400, 300, 200 or 100 MHz is in the table.** The governor would then act on those points with their own
     voltages, and this design assumes they are off-table.
   - Record the boot point's voltages: the restore targets are the values read here, never assumed.
4. **Clocks, voltages, TDP, threshold.** `DM_CMD_GET_ASIC_FREQUENCIES` (600/400), `DM_CMD_GET_MODULE_VOLTAGE` (525/700/485
   expected), `DM_CMD_GET_ASIC_VOLTAGE`, `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (0), `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS`.
5. **The governor's state.** These decide **S0 or S1**:
   - `ettelem-dv2 residency 2 3 4 5 6` and `ettelem-dv2 uptime`: the DV2 build's read-only queries [meas:
     `tools/claims-v3/dv2/z2.sh`].
   - `ettelem sptrace sp0.bin`: a BAR read that adds no line [meas: REV §7.3].
   - At the boot's WARNING level, any CRITICAL "Power throttle down event" line in the SP ring means a kernel has run
     since boot (S1).
   - **The SP pass time is a second test.** Under a 10 Hz sampler aifoundry3's board value changes every 263 ms, against
     156-158 ms on the other cards [meas: E41]. The spinning power task is the proposed cause (REV §4).
   - Predicted [inf]:

     | State | board value changes every | "Power throttle down" line in the SP ring |
     |---|---|---|
     | S1 | ~263 ms | present |
     | S0 | ~160 ms | absent |

     If the two signs disagree, the state is unknown: stop and ask the lab lead for a reboot.
6. **Baseline.** Six 9-second `ettelem sample --every-ms 100` windows at 600 MHz: board, rails, die mean, `took_ms`.

**If S1:** ask the lab lead to reboot aifoundry3 with the demo stopped (preferred), or use the one-event way out with
the owner's OK (A0). If neither is approved, Stage A does not run.

### 5.2 Stage A: the minion clock, idle, heatsink on (34 minutes of card time [model: §H])

- **A0: quiet the governor.** Set APM off (`-m DM_CMD_SET_MODULE_ACTIVE_POWER_MANAGEMENT -p 0`).
  - **Only on S1:** then `-f 300,400`. Expect exactly one new `SpCeEvent`, the clock reading 300, a nonzero POWER_DOWN
    residency (the loop exited), and the board value changing every ~160 ms within a minute. Anything else: restore 600
    and stop.
  - Then one verification launch at 600 MHz:
    `sparsity_host --test fma --type fp32 --pattern none --shires 0xffffffff --per-shire 32 --seconds 1 --seed 1`
    (small-integer inputs, every result checked). Expect `ok`, `ghz` near 0.6, no new governor line in the SP ring, and
    unchanged counters.
- **A1: probe (the first write of each level).** Descend 600 → 400 → 300 → 200 → 100 MHz.
  - At each level: set, read back (`GET_ASIC_FREQUENCIES`: the level and NoC 400), one window, one verification launch
    (`ok`; `ghz`/f within ±3 % of the 600 MHz launch's ratio), one window.
  - The first level that fails ends the descent; the lowest level that passed becomes the floor for A2-A4. Then back to
    600.
  - Card time: 2.6 minutes.
- **A2: passes (the primary data).** Four passes. Each is nine segments, 600 | f₁ | 600 | f₂ | 600 | f₃ | 600 | f₄ | 600,
  with f₁-f₄ the four levels in the pass's row of a Latin square: (400, 300, 100, 200), (300, 200, 400, 100),
  (200, 100, 300, 400), (100, 400, 200, 300).
  - A segment is: set, read-back, two windows; 26 s, so a pass takes 3.9 minutes [model: §H].
  - No kernel runs in A2.
  - Every level is entered from 600 and left to 600, so each pass gives each level one down-step and one up-step.
- **A3: load (optional).** At 600, 300 and 100 MHz, three bracketed 2 s bursts of the random-normal matmul
  (`--values randn --seconds 2`, E42's heater command), each inside its own window, as E42 did. The quantity is
  switching power over the idle just before the burst.
- **A4: hot (optional).** At 600 MHz, launch the heater until the die mean reads 74 °C (aifoundry3 went 55 → 88 °C in
  150 two-second launches [meas: `14-card-behaviour.md`]). Idle; at the first reading of 72 °C on the way down, run
  600 | 100 | 600 | 100 | 600. Two such passes.
- **Restore.** `-f 600,400`, then a 600 MHz verification launch while APM is still off, then APM on (`-p 1`) (§7.2).
  In that order the launch does not start the governor's loop, so the card is left in S0 for Stage B.

**The step estimator.**
- Each step = board mean over the last 2.5 s of the window before the set − board mean over the first 2.5 s of the first
  window after it. Samples begin ≥ 0.3 s after the set call returns.
- Down-steps and up-steps are signed so that both estimate P(600) − P(f).
- The rails follow through the PMIC's running average (τ 1.01-1.06 s on aifoundry3, one SP pass late [meas: E58]).
  Rail steps are deconvolved with `tools/ettelem/deconv.py`'s aifoundry3 τ, or read from samples ≥ 4 s after the step;
  both are reported.
- **The gap bias.** Between the two windows (2-4 s) the die answers the power step through the fast thermal stages.
  The leakage follows, so every step reads 4.7-5.7 % large, in both directions alike [model: §J]. The reduction divides
  each step by (1 + that fraction at its measured gap) and reports the uncorrected value beside it.
- **The noise.** A same-temperature null step on aifoundry3's idle board has an SD of 35 mW; the minion rail's is 7 mW
  [meas noise, model: §G]. Eight steps (four passes) give an SE of 12 mW, so 37 mW is 3 SE. The narrowest decided band
  edge is 0.3 W.
- **The temperature** is the 34-sensor mean (whole degrees), recorded per window. Every quantity is a step at one
  temperature, so no correction to T_ref is needed beyond the gap bias. A2's die drifts from 56 °C toward the
  low-clock rest (47-49 °C, §4.1) within a pass, and each step is local.

### 5.3 Stage B: the voltages at 100 MHz (18 minutes of card time [model: §H]; separate approval)

Preconditions: Stage A ended with its restore verified and its report read by the owner; §8's people are reachable;
nobody else is on aifoundry3; no kernel has run since Stage A's restore (the demo stayed stopped), so the card is still
in S0 (checked as in §5.1). Then A0 again (APM off) and `-f 100,400`, and:

- **B0: the gentle first write.** At 100 MHz, write the minion set-point it already has (`-v MINION,525`, the value
  read in Stage 0). It exercises the full path: I2C write, PMIC read-back, PVT check. It changes nothing.
  - Read back: two module reads 1 s apart equal 525; the on-die reading within 5 %.
  - If this write resets the card, Stage B ends there.
- **B1: the minion ladder.** 525 → 500 → 475 → 450 → 425 → 400 → 425 → 450 → 475 → 500 → 525 mV.
  - Every level is a write, two read-backs and an on-die check, one window, one verification launch at 100 MHz (`ok`,
    `ghz` ≈ 0.1 × the 600 MHz ratio), and one window.
  - Down and up together cancel a linear drift.
- **B2: the SRAM ladder at minion 400 mV.** Write 700 (the value it has), then 680 → 660 → 680 → 700, the same way.
  - The driver's `SramCeEvent`/`SramUceEvent` counters are read after every SRAM level.
- **B3: the dwell.** Set minion 400 and SRAM 660 (the lowest point), then 10 minutes of windows back to back.
  - This gives the low point's board law and slope as the die cools toward its rest (45-48 °C, §4.2), and its settled
    temperature.
- **Restore,** voltage first and frequency last: SRAM to its Stage 0 value, minion to its Stage 0 value (each verified),
  then `-f 600,400`, then a 600 MHz verification launch with APM still off, then APM on.

### 5.4 The runner

A new experiment directory, `tools/claims-v3/lc/`, adapted from NV's (`tools/claims-v3/nv/`), keeping NV's safety
machinery:
- `dms()` under `timeout -k 3 10`;
- the state file;
- the restore guardian, which holds the card lock until it has restored;
- ALERT and STOP files;
- the trap on every catchable signal;
- detached runs;
- the uptime check that detects a reset;
- the `DRY` mode.

What is specific to LC:
- **A hard-coded whitelist in the only functions that write** (`lc_setclk`, `lc_setvolt`, `lc_setapm`):
  - clocks {600, 400, 300, 200, 100} minion with NoC 400 only;
  - minion {525, 500, 475, 450, 425, 400} mV;
  - SRAM {700, 680, 660} mV;
  - APM {0, 1};
  - no other module or command.

  Any other value is refused, as is any card other than aifoundry3's, any BL2 other than 0.20.0, and any start whose
  Stage 0 reads differ from 600/400 MHz and 525/700/485 mV.
- **The driver counters and `dmesg`'s event count, read before and after every write and every window.**
- **`predictions.json` and `PREDICTIONS.sha256`, frozen and committed before the first write.** Every real block refuses
  unless they check.
- **`reduce.py --self-test`** on synthetic passes that carry:
  - a planted D and n;
  - the gap bias;
  - an event flood;
  - a failed restore;
  - a reset.
- **Order:** `V3_DRY=1` first, then `et-who`, then A1 for real.

### 5.5 The commands

`D=/opt/et/bin/dev_mngt_service`. Every call is run as `flock -n /run/lock/etsoc-shire0.lock timeout -k 3 10 $D … -n 0`.

| Purpose | Command |
|---|---|
| identity, uptime | `-m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -u 5000`; `-m DM_CMD_GET_MODULE_UPTIME -u 5000` |
| table, clocks, voltages, TDP | `-m DM_CMD_GET_VMIN_LUT -u 5000` (writes `dev0_vmin_lut.bin`); `-m DM_CMD_GET_ASIC_FREQUENCIES -u 5000`; `-m DM_CMD_GET_MODULE_VOLTAGE -u 5000`; `-m DM_CMD_GET_ASIC_VOLTAGE -u 5000`; `-m DM_CMD_GET_MODULE_STATIC_TDP_LEVEL -u 5000` |
| drain a poisoned queue (after any failed call) | `-m DM_CMD_GET_MODULE_POWER -u 5000` [meas: `14-card-behaviour.md`, Traps] |
| APM off / on | `-m DM_CMD_SET_MODULE_ACTIVE_POWER_MANAGEMENT -p 0 -u 7000` / `-p 1` |
| clock | `-m DM_CMD_SET_FREQUENCY -f 100,400 -u 7000` (and 200, 300, 400; restore `-f 600,400`) |
| voltage | `-m DM_CMD_SET_MODULE_VOLTAGE -v MINION,500 -u 7000` (…); `-v L2CACHE,680 -u 7000` (…) |
| governor state (read-only) | `build/ettelem-dv2/ettelem residency 2 3 4 5 6`; `… uptime`; `build/ettelem/ettelem sptrace spN.bin` |
| telemetry window | `build/ettelem/ettelem sample --seconds 9 --every-ms 100` |
| verification launch | `build/sparsity/host/sparsity_host --test fma --type fp32 --pattern none --shires 0xffffffff --per-shire 32 --seconds 1 --seed 1` |
| heater / load (A3, A4) | the same with `--values randn --seconds 2` |
| counters | `cat /sys/bus/pci/drivers/ET/0000:02:00.0/err_stats/ce_count` (and `uce_count`); `dmesg \| grep -c 'Error Event Detected'` |

---

## 6. Statistics and decision rules (`predictions.json`)

The unit of replication is the pass (A2: four; A4: two). Stage B's ladder counts each level's down and up visit as
two. Per item:
- the mean over passes, with the hull of its 95 % t-interval and its 95 % percentile bootstrap (20,000 resamples, seed
  20261001) as the verdict interval;
- **PASS** if that interval lies inside the band, **FAIL** if wholly outside, **INSUFFICIENT** otherwise or with fewer
  than 3 valid passes;
- **NOT DECIDED** if a gating control failed.

A failed prediction is reported as failed.

**This is one card.** There is no second card to validate on (§3), so the verdicts are aifoundry3's.

| Item | Quantity | Bands (registered) | Gated by |
|---|---|---|---|
| **A-STEP** (primary) | board step 600 → 100 MHz, gap-corrected | TH-C0 [−0.3, 0.3] · TH-CS (0.3, 4.14] · TH-CL > 4.14 W; within TH-CS, which forms of the idle law allow it (exponential ≤ 2.46, T²·Arrhenius ≤ 3.95, Arrhenius ≤ 4.14 W) is reported | C-CLK, C-NOC |
| A-LIN | the four steps against (600 − f) | PASS if a line through 0 leaves rms ≤ max(0.05 W, 5 % of the 100 MHz step) | C-CLK |
| A-RAIL | minion and SRAM rail steps; unmetered step against 0.181·ΔP_m + 0.043·ΔP_s | reported; the unmetered check passes within ±0.15 W | C-CLK |
| A-T (A4) | 100 MHz step at 72 °C ÷ at 56 °C | PASS inside [0.9, 1.1] (TH-CS's temperature independence) | C-CLK |
| A-E (A3) | switching(f) ÷ switching(600) for f = 300, 100 | TH-E1: f/600 ± 10 % | C-CLK |
| **B-N** (primary) | the minion rail's exponent, from ln(P_m − D_m/6·(V/525)²) against ln(V/525) over six levels, D_m from A-STEP | TH-V0 ≤ 0.5 · TH-VD [1.4, 2.26) · TH-VS [2.26, 2.82] · TH-VX > 2.82 | C-METER, C-CLK, C-OK |
| B-CP | B-N against §4.3's n for A-STEP's measured D_m | PASS within ±0.15 | as B-N |
| B-MODEL | which model B-N and A-STEP favour (§4.5) | B-N < 2.26: the EM; 2.26-2.54: both; > 2.54: this plan. A-STEP inside [1.02, 2.43] W: both; outside: this plan only (if ≤ 4.14 W). Reported, with B-NS against each model's SRAM row | as B-N |
| B-NS | the SRAM rail's exponent (700/680/660) | reported against B-N (the shared-n assumption fails if they differ by > 0.5) | C-METER |
| **B-LOW** (primary for §9) | board at 100 MHz, 400/660 mV, at the B3 start temperature, corrected to 56 °C with B3's own slope | inside [18.4, 20.1] W (§4.2's 5-95 %, ± 0.3 W) | C-CLK, C-OK |
| B-SLOPE | board dP/dT at the low point over B3's cooling | reported against 0.15-0.22 W/°C (§4.2, §4.4) | — |

Controls:

| Control | Rule |
|---|---|
| **C-CLK** (gates everything) | every verification launch's `ghz`/f ratio within ±3 % of the 600 MHz launches'; `mhz.minion` = the level and `mhz.noc` = 400 in every window |
| C-NOC | NoC rail step \|Δ\| ≤ 0.1 W at every level (its clock and voltage do not change) |
| C-METER | board step ÷ minion rail step while only the minion set-point moves, in [0.9, 1.6] (true meter 1.181; current × fixed voltage 1.83-2.11 [model: §E]) |
| C-OK | every verification launch `ok`, `tensor_errors` 0 |
| C-QUIET | `SpCeEvent` rises by at most 1 in the whole session (the S1 way out), `SramCe/Uce`, `DramUce`, `SpWdogUce` and `MinionHangUce` not at all |
| C-RESTORE | every restore verified (§7.2) |

---

## 7. Stop rules, the restore, and every exit path

### 7.1 Stop rules (each ends in the restore of §7.2 unless it says otherwise)

| Event | Action |
|---|---|
| `SpCeEvent` rises by ≥ 2 (≥ 1 outside A0), or `dmesg` gains "Error Event Detected" lines | **set 600/400 at once** (600 MHz is on the table, so a running loop falls silent), then the restore; ALERT-LC-FLOOD; STOP |
| a verification launch not `ok`, `tensor_errors` > 0, or `ghz` outside ±3 % | restore; that level is the failing level (reported); the stage ends |
| a launch that `timeout` stops, or "kernel did not finish within 6 s" | wait for the board to return within 0.3 W of idle (up to three windows), then restore; ALERT-LC-MM if the next launch fails ("Couldn't use the HPSQ") |
| `MinionHangUceEvent` rises | restore (the SP still answers); ALERT-LC-MM: a management reset is the owner's and the lab lead's call, and the clock guard runs after it |
| a read-back ≠ the level, the on-die voltage > 5 % off, or `mhz` ≠ the level in a window | restore; ALERT-LC-SET; STOP |
| a voltage set that times out (the endless retry, §2.3) or the uptime going back | wait up to 60 s for answers; verify the boot values; ALERT-LC-RESET (the lab lead re-runs the clock guard before any kernel); STOP |
| `SramCeEvent`/`SramUceEvent`/`DramUceEvent` rises | restore (voltages up first); ALERT-LC-ECC; STOP |
| die mean ≥ 85 °C, any current reading ≥ 90 °C (A4), or board > 70 W (the PMIC alarm is set at 75 W [src: REV §6]; A4's heater at 74 °C is about 33 W idle + 25 W [model: §A; meas: E20]) | restore |
| another user's or process's hold on the card, `et-who --check` ≠ 0, a STOP file | restore; exit 3 (another user) or 0 (STOP) |
| a signal (HUP, INT, TERM, PIPE, USR1, USR2, ALRM) | the trap restores; signals are ignored while it runs |

### 7.2 The restore and its verification

Order: SRAM voltage → minion voltage (each to its Stage 0 value) → clock 600/400 → the 600 MHz verification launch →
APM on. Voltage goes up before frequency. APM comes back last, so no loop can start at an off-table clock, and the
verification launch, run with APM off, does not latch the governor.

The restore is **verified** when all of these hold:
- after a drain if any call failed, two module reads 1 s apart equal the Stage 0 values;
- the on-die voltages are within 5 %;
- `GET_ASIC_FREQUENCIES` reads 600/400 twice;
- one 600 MHz verification launch is `ok` with `ghz` at the baseline;
- the SP ring has no new governor ERROR;
- the counters are unchanged.

The restore is tried up to 5 times, waiting 20 s whenever the card does not answer. If it cannot be verified, the runner
writes ALERT-LC-RESTORE and the host's STOP.

### 7.3 Every exit path

| Exit | What restores | How it is known |
|---|---|---|
| normal end | the block's `finish` | `block.json` `restored: true` |
| a stop rule | `finish` | the ALERT file and `block.json` |
| a signal | the trap → `finish` | same |
| `kill -9`, the OOM killer, a crash of the block | the guardian (holds the card-lock descriptor; restores, verifies, then exits) | `block.json` `guardian: true` |
| `kill -9` of the whole process group | nothing until the next boot: the card keeps the low settings | the state file `LC-STATE.json` is dirty, so the next block refuses and alerts; a person restores with the commands of §5.5 |
| the host hangs, reboots or loses power | the card's boot: BL2's boot values (600/400, the flash voltages, APM on), then the clock guard (TDP 0, 600/400) | the guard's marker for the new boot |
| an SP watchdog reset (a failed voltage write) | BL2's boot values; TDP 65 W until the guard is re-run | the uptime; `SpWdogUceEvent`; ALERT-LC-RESET |
| an MM hang | the SP path still restores clock, voltages and APM; the MM stays hung | ALERT-LC-MM |
| the agent's `ssh` drops or its session ends | nothing needed: the block is detached and finishes alone | `block.json` |

### 7.4 Host-level risk, after 30 September

On 30 September a link retrain hung aifoundry1 until the lab was power-cycled. There was no panic record, no console
and nobody on site [meas: `14-card-behaviour.md`, retrain section]. What follows from that:

- **Stage A** has no known path to a link-level event. The clock code is bounded and runs no critical section, and the
  PCIe shire has its own PLL [src: §2.1]. Its worst known case is a hung master minion. On 28 September such a hang left
  the host up, and a management reset recovered it [meas]. Stage A needs the lab lead reachable, not on site.
- **Stage B** can cause an SP watchdog reset (§2.3). That resets the SoC under a live driver. The driver has an event for
  it (`SP_WATCHDOG_RESET_EVENT`) [src: `et_event_handler.c:709-712`], which suggests the platform expects the host to
  survive one [inf]. But this host's behaviour is not established.
  - So during Stage B, **someone who can power-cycle aifoundry3 is reachable and can be there within about 30 minutes;
    nobody else works on aifoundry3; the demo stays stopped.**
  - The session runs on aifoundry2 and the block is detached, so a hung aifoundry3 costs the lab time, not data.
  - Each voltage write is a separate step, so the first failure stops the stage.

---

## 8. Time and approvals

| Stage | Card time | Wall time (estimate) | Approves | Must be reachable |
|---|---|---|---|---|
| 0: read-only | 1.4 min [model: §H] | ~20 min | the owner (machine and card); the lab lead stops the demo | the lab lead (the demo) |
| **A**: clock and APM | 34 min [model: §H]; 22 min without the optional A3 and A4 | ~1-1.5 h | **the owner and the lab lead (Roman)**: a clock and power-management change on a shared card, a possible master-minion hang and reset | the lab lead, by message |
| **B**: voltages | 18 min [model: §H] | ~45 min | **the owner and the lab lead again, after Stage A's report** | someone able to power-cycle aifoundry3 within ~30 min |
| reduction and model re-run | none | ~1 h | — | — |
| **bare step** (§9) | ≤ 30 min powered | half a day, on site | **the owner and the lab lead (the hardware); the demo's owner if aifoundry3's card is used** | a person on site throughout |

Write counts [model: §H]: about 51 `SET_FREQUENCY` (each also re-locks the NoC PLL at 400 MHz through the stock CLI),
17 `SET_MODULE_VOLTAGE`, 2 `SET_MODULE_ACTIVE_POWER_MANAGEMENT`.

A minion-only setter would cut the 51 NoC re-locks to none: a 4-byte `DM_CMD_SET_FREQUENCY` with `pll_id` 1 from a new
`ettelem setclk`. It is optional, and it needs its own dry run and a byte-for-byte check against the stock CLI before
use.

---

## 9. The bare-card step (only after the model and the measurement agree)

### 9.1 The gate: all four must hold

| | Condition |
|---|---|
| **G1** | Stages A and B ran; every control passed; every restore verified; the card back at its pre-session idle (55-57 °C at 600 MHz). |
| **G2 (agreement)** | A-STEP not TH-CL, and B-N in TH-VS or TH-VD with B-CP holding. If they do not hold, `lc_plan_calc.py` is re-run with the measured D and n in place of the priors. Its predicted lowest-point board must then match B-LOW within ±0.5 W and B-SLOPE within ±0.05 W/°C, and that refit is registered before the bare step. Whatever B-MODEL finds, the envelope model (`lowclock_calc.py`) is re-run too, with the measured clock tree and exponents, so the page's numbers and the bare-step gate rest on the same law. |
| **G3 (odds)** | `lc_plan_calc.py` §F, re-run with the measured low-point law, gives ≥ 80 % of power-on draws that stay below the stop (80 °C) **and** settle at or below 70 °C, for the cooling class installed. Today's priors give 44 % for a 3-6 m/s blower, 21 % for a 1-2.5 m/s fan and 0 % in still air [model: §F]. |
| **G4 (safety)** | every precondition of §9.2 checked by the person on site, the power cut tested end to end. |

### 9.2 Preconditions

1. **Someone on site** for the whole powered time: the lab lead or a delegate who knows the rig. They must be able to
   cut power by hand and to see the thermocouple display.
2. **A thermocouple on the lid** and a logger independent of the card and its host.
   - Type K or T, 36-40 AWG, bead ≤ 0.25 mm, on the lid centre under Kapton tape with a dot of thermal paste.
   - Logged at ≥ 1 Hz.
   - With the heatsink off, the lid should read the die mean to within about 1 °C [inf]. θ_JC is ASSUMED 0.03-0.10 °C/W
     in `nohs_calc.py`, and only 8-13 % of the heat leaves through the lid top in still air [model: `nohs_calc.out` B].
3. **An automatic, latching power cut**, driven by the logger's alarm, independent of the host and the card.
   - **Recommended:** a relay or smart outlet on aifoundry3's mains, so card and host lose power together.
   - **Possible:** a relay on the card's 12 V. That needs a riser that isolates the slot's 12 V and feeds the card
     through its ATX AUX jumper [ext: card doc PDF p.5, power tree]. A cut there removes the device from under its
     driver, the same kind of event that hung aifoundry1 on 30 September, so expect the host to hang and plan to
     power-cycle it.
   - It fails safe: an open thermocouple cuts the power. Resetting it needs a hand.
   - It is tested before the card is powered: a heat gun on the thermocouple trips it on a dummy load (a lamp), and the
     action time is under 1 s.
4. **The stop temperature: 80 °C on the lid thermocouple.** That leaves 10 °C to the lab's 90 °C cap. The hottest
   sensor runs 2-4 °C above the mean [meas: REV §10, `tel.json` TEL-R].
   - Second, software line: a watcher on the host reads the die mean at 10 Hz. At 75 °C it stops any kernel, and if the
     die is still rising it shuts the host down.
5. **Cooling.**
   - A blower of the modelled class (≥ 3 m/s at the lid; G3 decides), powered independently of the card, aimed across
     the lid from the side so the camera's view stays open.
   - It runs before power-on and until the card is cold.
6. **The card.** Use the card measured in Stages A and B, with the same firmware; the idle law and scale are per card
   [meas: `11-thermal-model.md`]. A spare card would need Stages A and B first.
   - The lab lead removes the heatsink with the host off and unplugged, wearing an ESD strap, and cleans the lid with
     isopropanol.
   - A high-emissivity patch goes on for the camera (the plated lid's emissivity is ASSUMED 0.05-0.3 in `nohs_calc.py`
     B), leaving the thermocouple spot bare.
   - The heatsink, its clips and fresh thermal interface material are kept for the refit.
7. **The host**: dedicated (no other users, the demo stopped, the lab told).
   - For the session the lab lead sets the clock guard's `ET_MINION_FREQUENCY_MHZ=100` (an environment value of
     `et-board-clock-guard.service` [meas: facts.md:205-213]). The 600 MHz window then ends when the guard runs at
     boot.
   - The block's first action after boot is APM off. The guard sets TDP 0 and does not touch APM, so in S0 no loop runs
     until a kernel; our APM-off comes before any kernel.

### 9.3 Procedure

1. Arm the logger, start the blower and the camera's recording, then power on. Nobody touches the board while it is
   powered.
2. From power-on until the low point is set, the card idles at 600 MHz.
   - With the blower, the modelled peak over the whole power-on is 54 / 75 / runaway °C (5/50/95 %) [model: §F]. The
     runaway tail is what the cut is for.
   - With an ordinary fan the time to 90 °C at a 600 MHz idle is 73 / 127 / 284 s (5/50/95 %) [model:
     `nohs_calc.out` E, aifoundry3 fan idle].
3. When the host is up, the block runs:
   - S0 check;
   - APM off;
   - 100 MHz, if the guard has not already set it;
   - minion 525 → 450 → 400 and SRAM 700 → 660, each a whitelisted write with its read-back;
   - then telemetry windows back to back.
4. **The approach.** With a blower and the central law, the modelled stable equilibria lie at 46 / 57 / 70 °C
   (5/50/95 %), and the power-on draws read 52 / 73 / runaway °C at 30 minutes [model: §F]. Compare live against the
   model.
5. **If it settles at or below 70 °C**, the separately planned imaging run follows, for at most 30 minutes.
   - The workload adds at most the margin left: at the low point the random-normal matmul on all 1,024 minions adds
     about 2.4 W, 75 mW per shire [model: §I].
   - Its rise is about 2.4 W × θ_JA plus the leakage feedback; the imaging plan sizes the workload to the margin [inf].
6. **End: never restore 600 MHz on a bare card.** Stop the workload, shut the host down at the low point, keep the blower
   on until the lid is below 40 °C, then cut power.

### 9.4 Abort rules (any one)

| Rule | By |
|---|---|
| lid thermocouple ≥ 80 °C | the relay (automatic) |
| die mean ≥ 75 °C, or the lid ≥ 75 °C | the watcher stops the workload; if the die still rises, it shuts the host down |
| rise faster than 0.5 °C/s for 10 s above 60 °C (the adiabatic idle rate is 1.3-2.0 °C/s [model: `nohs_calc.out` E]) | the person on site cuts power |
| 10 min at the low point and still rising faster than 0.05 °C/s above 65 °C (no equilibrium within the margin) | the watcher shuts the host down |
| the thermocouple and the die mean disagree by > 5 °C, or a thermocouple fault | the person cuts power |
| smell, smoke, discolouration, or anything unexpected | the person cuts power |
| the host stops answering while the lid is rising | the person cuts power |

### 9.5 After

1. The lab lead refits the heatsink with fresh interface material and the original mounting.
2. With the host powered and the card at 600 MHz (the guard back to 600), the idle die must return to 55-57 °C (its
   pre-session rest [meas]) and the idle board to its E44 law within 0.5 W at that temperature. Otherwise the refit is
   redone before anyone uses the card.
3. The guard's `ET_MINION_FREQUENCY_MHZ` goes back to 600 and the demo restarts.

### 9.6 What to expect

On today's numbers the bare step fails G3 with every cooling class: a blower gives 44 % against an 80 % gate, a fan
21 % [model: §F].
The measurement moves this in either direction:
- **Above central:** n above 2.7 and D at the top of its band, or a lower floor than predicted, add margin.
- **Below central:** n below 2.3, as textbook DIBL, or a larger SoC share, removes it. The rival's blower rows are 48 %.

If G3 fails, the alternatives on the page keep their place:
- the heatsink-on camera views;
- the 34 on-die sensors as a shire-level map (the heat-placement study);
- a delidded die under an IR window (`imaging/`).

The low-clock work still delivers the floor: what the chip draws at its lowest settable point.

---

## 10. Not established, and limits of this plan

- **The event flood (§2.2) is read from source, never seen.** Neither is the S0/S1 pass-time signature, nor the
  300 MHz way out.
- Whether the minions, the shire DLL and the master minion run correctly at 100-275 MHz: no record of their use on a
  lab card. A1 and the verification launches test it.
- Whether aifoundry3's PMIC 1.5.0 accepts 400 mV minion and 660 mV SRAM (card 0's PMIC 1.6.1 does). Also whether the
  host survives an SP watchdog reset.
- The idle reset's 7.40 W step mixes three changes: clock, minion voltage and SRAM voltage. Section C separates them
  only with two assumptions: one shared n, and the P_fix bound with its three forms.
- θ_JB (1-3 °C/W) and every bare θ_JA are ASSUMED or modelled; only the bare step measures them.
- A WFI minion's residual clock power, the master minion's idle loop and the shire caches' clocking all land in D
  together. The experiment does not separate them.
- The blower's 3-6 m/s and the 30-90 s boot window are ASSUMED. The hosts' boot time is not recorded.
- One card only: the verdicts are aifoundry3's.
- The two models' n bands overlap only at 2.26-2.54, and both rest on the same 800 → 600 MHz idle step. Neither has a
  measured SRAM exponent; Stage B is the first.

## 11. What to copy and commit (the owner's call; nothing was committed)

- `lc_plan_calc.py` and `lc_plan_calc.out` are already in `docs/reports/data/2026-09-30-without-heatsink/` (not
  committed), beside the envelope model's `lowclock_calc.*`. Suggested README row: "`lc_plan_calc.py` / `.out`: the
  low-clock measurement plan's registered predictions for aifoundry3 (the idle step at 400-100 MHz, the leakage
  exponent from aifoundry2's idle reset, the lowest settable point, the bare card at that point by `nohs_calc.py`, the
  schedule) and, in section K, the envelope model's predictions restated in the plan's terms. Seed 20260930; about
  5 minutes; run after `lowclock_calc.py`." The exploration scripts in `~/claude/work/lowclock/plan/`
  (`explore_*.py`, `sens_form.py`) are superseded by `lc_plan_calc.py` and need not be kept.
- This plan → `tools/claims-v3/lc/DESIGN.md` when the runner is built. Its §4 tables become `predictions.json`,
  frozen with `freeze.sh --predictions` and recorded in `docs/findings/03-experiments.md` before the first write.
- New lessons for `docs/findings/14-card-behaviour.md`:
  - an off-table clock on a card whose governor loop runs floods the host with SP runtime-error events;
  - APM off gates both governor triggers;
  - the driver's world-readable `err_stats` counters make a stop signal;
  - `SET_FREQUENCY` and the governor's loop both reprogram PLL4 with no lock between them (§2.2), so a clock set while
    a loop runs can be undone. This is an upstream firmware report (et-platform), to be filed only with the owner's
    OK; it is from source reading, never seen on a card.
