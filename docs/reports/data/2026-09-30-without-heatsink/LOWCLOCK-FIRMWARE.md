# ET-SoC-1 clocks and voltages: firmware facts for a low-clock run (condensed notes)

Condensed on 30 September 2026 (about 21:30 PDT) from the firmware notes written that afternoon on aifoundry2
(`~/claude/work/lowclock/fw.md`, read-only work: no card, no `/dev/et*` node, no clock, voltage, TDP or
power-management setting was touched). Sections keep the full notes' numbers, so the measurement plan's `FW §n`
(`LOWCLOCK-PLAN.md`) points here; sections 0, 2, 3, 6, 7 and 9 are as written, sections 1, 4, 5 and 8 are shortened.
The page "Feasibility of running the ET-SoC-1 without its heatsink" cites these notes as [R15].

Labels: **[src]** firmware or hardware source text, with file:line; **[meas]** a measurement already in the repository,
with its path; **[calc]** arithmetic printed by `pll_modes.py` here (its printout `pll_modes.out`; it finds
`external/et-platform` from its own path and reads each build with `git show`); **[inf]** reasoning, not source text and
not measured; **[ext]** an outside document (manual, errata, card doc) with its location.

## Citation key

| Tag | Meaning |
|---|---|
| `EP/` | `external/et-platform`, HEAD `836a4ab` (2026-07-17). For firmware purposes identical to `353f20e`, which the lab hosts' `/opt/et` is built from (review-governor.md, key `H:`) |
| `BL2/` | `EP/device-bootloaders/src/ServiceProcessorBL2/` |
| `@O` | BL2 0.18.0 = et-platform `da192816a` (release 1.2.0, aifoundry1 card 1). `@C` = 0.20.0 = `ffca4cbb4` (release 1.3.1, aifoundry2 and aifoundry3). `@N` = 0.21.0 = `50310b06b`, the closest public source to 1.4.1's BL2 0.21.2 (aifoundry1 card 0; 0.21.1/0.21.2 are not in the public history). Files are read with `git -C EP show <commit>:<path>` |
| `HAL/` | `EP/etsoc-hal/include/hwinc/` (PLL mode tables, ESR maps); `IPX/` = `EP/etsoc-hal/include/etsoc_hal/inc/` (Movellus IP-XACT register headers) |
| `DS` | `external/et-man/ET Preliminary Datasheet Rev 1.0.pdf` (Figure 5-1 on PDF page 22; text in `et-man/txt/`) |
| `PRM` | `external/et-man/txt/ET Programmer's Reference Manual.txt` (line numbers of the text extract) |
| `ERR` | `external/et-man/txt/ET-SoC Errata.txt` (line numbers of the text extract) |
| `CARD` | `external/et-man/txt/ET-PCIe-Dev-Card-V3.txt` and the PDF's page 10 (DIP switches) |
| `REV` | `docs/reports/data/2026-09-28-dvfs2-aifoundry2/plan/review-governor.md` (the governor, read exactly, by build) |

Which build runs where [meas: `docs/findings/14-card-behaviour.md:335`]: aifoundry2 and aifoundry3 = 1.3.1 (BL2 0.20.0,
PMIC 1.5.0, MM 0.23.0); aifoundry1 card 0 = 1.4.1 (BL2 0.21.2, PMIC 1.6.1, MM 0.24.0); aifoundry1 card 1 = 1.2.0 (BL2
0.18.0, PMIC 1.3.0, MM 0.22.0).

---

## 0. The answer in brief

1. **The minions do not use their own per-shire PLLs.** In every build (0.18.0, 0.20.0, 0.21.0, HEAD) BL2 boots all
   minion shires on the **step clock**, service-processor PLL4 (a Movellus HPDPLL), through each shire's clock mux, and
   switches the per-shire LVDPLLs off [src: `BL2/common/main.c:94,411-414` (`min_step_pll_mode = {34,…}`,
   `MINION_PLL_USE_STEP_CLOCK`), `BL2/include/minion_configuration.h:82` (`true`), `BL2/driver/minion_configuration.c:670-721`
   (`Minion_Configure_Hpdpll`: `configure_sp_pll_4`, mux → `SELECT_STEP_CLOCK`, `lvdpll_disable`)]. The governor also
   moves the clock by reprogramming PLL4 [src: `@C BL2/services/thermal_pwr_mgmt.c:1842-1849`; HEAD `:1749-1761`]. The
   vendor errata says why: the LVDPLL "is still not stable even with the workaround" [ext: ERR:3443,3479].
2. **The lowest minion clock the stock tools can set is 100 MHz.** `DM_CMD_SET_FREQUENCY` with `use_step_clock = 1`
   (which the stock `dev_mngt_service` always sends) accepts exactly the output frequencies of the HPDPLL mode table.
   With the cards' 100 MHz reference that table has 72 entries from **100 MHz** (mode 62: DCO 1100 MHz ÷ 11) up, including
   **100, 125, 150, 166, 175, 200, 225, 250, 275 MHz** below the governor's 300 MHz floor [src: `HAL/hpdpll_modes_config.h:637-767`;
   calc: `pll_modes.out` §1]. The command changes **no voltage** and has **no range check** beyond "the mode must exist";
   a request with no table entry (25 MHz, 10 MHz) is refused with -9008 and changes nothing [src:
   `BL2/services/thermal_power_monitor.c:775-800,870-920`]. The same list applies to the NoC PLL.
3. **25 MHz or 10 MHz needs new firmware (or a debugger), not a command.** The hardware post-dividers are 9 bits
   (HPDPLL, max 511) and 8 bits (LVDPLL, max 255), so 10–50 MHz fit the divider fields at the DCO frequencies the tables
   use [src: `IPX/mvls_tn7_hpdpll.ipxact.h:1198`, `IPX/mvls_tn7_lvdpll.ipxact.h:1197`; calc §4], but no mode table entry,
   DM command or BL2 path programs them, and the tables never use a divider above 11 [calc §4]. The only other sources
   into the minion shires are 100 MHz too: PLL4 bypass (step-clock mux falls back to `clk_100`) and the shire mux's
   reference position [ext: DS Figure 5-1; PRM:12268-12271]. Whether the DLL, the PLL post-divider at >100:1 and the
   shire logic behave below 100 MHz is **not established**.
4. **Voltages.** Minion, SRAM (L2/"SCW"), NoC, DDR, Maxion, PCIe-logic, PCIe, VDDQ and VDDQLP rails, set through the PMIC
   as 8-bit codes (250 mV + 5 mV·code for the core rails) [src: `BL2/include/bl2_pmic_controller.h:133-162`]. The lowest
   values the firmware accepts (0.20.0, 0.21.0, HEAD): **minion 400 mV, NoC 400 mV, SRAM 660 mV**, DDR 700, Maxion 600
   [src: `@C bl2_pmic_controller.h:170-248`, `pmic_controller.c:1409-1473`]. **0.18.0 has no range check at all.** The
   vendor's own lowest operating point is the safe state, 300 MHz at 400 mV minion and 660 mV SRAM (0.21.0+) [src:
   `BL2/include/thermal_pwr_mgmt.h:65-75`]; aifoundry1 card 0 idles near it (300 MHz, 398 mV, 18.8 W) [meas:
   `14-card-behaviour.md:148-150`]. No SRAM-retention floor is documented anywhere in the sources read.
5. **Frequency and voltage are coupled only inside the governor.** `SET_FREQUENCY` moves only the PLL, `SET_MODULE_VOLTAGE`
   only the regulator. The governor looks both up in the per-card flash VMIN table (0.20.0+) and needs an **exact** table
   frequency; a clock set to 100 MHz is off-table, so the governor cannot step it and, on the cards' 0.20.0, either
   leaves it or snaps it back to the boot point (600 MHz) at its next idle or thermal-loop exit (§6).
6. **No power gating is used.** BL2 initialises all 34 minion shires regardless of the fuse mask ("Workaround to get rid
   of a bug that causes huge excess current draw") [src: `BL2/driver/minion_configuration.c:585-587`, the same in all
   builds], writes none of the documented neighbourhood/minion power-control ESRs, and gates only debug clocks. An
   unused shire idles in WFI (clock-gated inside the core) and leaks: the idle minion rail is 11.05 W at 73 °C, about
   0.33 W per shire [meas: `16-dvfs-and-leakage.md` E19; calc §6].
7. **What keeps running regardless:** the SP (PLL0, 1000 MHz), the PCIe shire (505 MHz), the NoC (400 MHz), the memory
   shires and LPDDR4X (933 MHz, **power-down and self-refresh disabled**, auto-refresh on), the Maxion rail (600 mV,
   cores not booted in production BL2). At idle, the NoC rail plus everything off the three metered rails is
   18.74 W of 31.79 W (59 %) on aifoundry2 [meas: E19; calc §6]; a lower minion clock cannot touch that part.
8. **Watchdogs and timeouts are wall-clock, not minion-clock:** SP watchdog 10 s, MM-heartbeat watchdog 10 s, both on
   the SP's timer; the MM's own timeouts run on the PU timer. The master minion runs on the same step clock, so at
   100 MHz the runtime firmware itself runs 6× slower. The host runtime waits 24 h by default; the lab's 10 s device
   rule is the binding limit.

## 1. Every clock, how it is made, and who sets it (shortened)

- All SoC PLLs are Movellus digital PLLs: HPDPLLs (SP PLL0/1/2/4, PCIe, Maxion, memory shires) and one LVDPLL per minion
  shire [ext: ERR:3311-3337; DS Figure 5-1]. The lab cards run on the 100 MHz reference [inf: they report 600 MHz minion
  and 400 MHz NoC, the 100 MHz-reference boot modes 34 and 37].
- **Minion shires** (cores, L1 and the shire cache: "all the areas … except the NoC are actually using the same
  clock", ERR:1629-1630) run on the **step clock**, SP PLL4, through each shire's clock mux, at mode 34 = 600 MHz
  [src: `BL2/common/main.c:94,411-414`; `BL2/driver/minion_configuration.c:670-721`; PRM:12250]. The clock is
  configured with the remapped mask `0x1FFFFFFFF`, 33 virtual shires (32 compute and the master) [src:
  `BL2/common/main.c:288-291,411`]; only the initialisation (`enable_minion_shire`) forces `0x3FFFFFFFF`, all 34
  [src: `BL2/driver/minion_configuration.c:587`]. Which clock the spare shire runs on is not established (added 30
  September, after review). The per-shire LVDPLLs
  are switched off. The shire DLLs are locked once at boot on the 100 MHz reference
  [src: `EP/etsoc-hal/src/sp_minion_shire_pll_dll_config.c:6-20`].
- **NoC** 400 MHz (SP PLL2, mode 37), **memory shires / LPDDR4X** 933 MHz, **service processor** 1000 MHz (PLL0),
  **PCIe shire** 505 MHz ("anything beyond this cause intermittent hangs in PCIe DMA engine"), Maxion PLLs unused in the
  production BL2 [src: `main.c:91,326,383-398`; `BL2/driver/io_pll.c:41-56,1049-1079`; `BL2/driver/mem_controller.c:39-44`].
  `mtime` ticks at 10 MHz from the 100 MHz reference [ext: DS line 1325].
- **Readback trap.** `DM_CMD_GET_ASIC_FREQUENCIES` (`mhz.minion`) decodes PLL4's registers [src: `BL2/services/perf_mgmt.c:280-287`;
  `io_pll.c:907-930`]: it would not see a bypassed PLL4. Check the true clock by work rate (cycles against host time or `mtime`).
- **Every PLL4 change already passes through 100 MHz**: `configure_sp_pll_4()` bypasses PLL4 to `clk_100`, reprograms,
  waits for lock (≤ 10,000 polls × 3 tries) and un-bypasses [src: `io_pll.c:576-614,743-782`; PRM:12268-12271]. If
  programming fails three times PLL4 is left off and bypassed, so the minions stay at 100 MHz while the readback shows
  the requested mode [src: `io_pll.c:776-781`; inf for the readback].

## 2. Selectable minion and NoC frequencies, and what the DM command accepts

`DM_CMD_SET_FREQUENCY` (37) carries `{uint16 pll_freq (MHz), uint8 pll_id (0 = NoC, 1 = minion), uint8 use_step_clock}`
[src: `EP/device-api/include/management-api/device_mgmt_api_rpc_types.h:1019-1029`; `device_mgmt_api_spec.h:385-405`].
The handler [src: `BL2/services/thermal_power_monitor.c:870-920`; identical in @O, @C, @N and HEAD, checked by diff]:

1. if `pll_id == NoC` or `use_step_clock == 1`: find the **first** HPDPLL table entry whose input equals the strap's
   reference and whose output equals `pll_freq × 10^6` (`:775-800`); else the same in the LVDPLL table (`:821-846`);
2. no match → status `THERMAL_PWR_MGMT_HPDPLL_MODE_FIND_FAILED` (-9008) or `…LVDPLL…` (-9009) to the host, nothing
   changes [src: `EP/device-bootloaders/src/shared/common/include/bl_error_code.h:158-159`];
3. NoC → `configure_sp_pll_2(mode, NO_UPDATE)`; minion → `Minion_Configure_Minion_Shire_PLL_no_mask()`, i.e. PLL4 +
   mux to step + LVDPLLs off + the governor's frequency register updated (`minion_configuration.c:670-721,1187-1196`);
4. **no voltage change, no bounds check, no 25 MHz rounding** (the rounding is only in the governor's own setter).

The stock CLI `dev_mngt_service -m DM_CMD_SET_FREQUENCY -f <minion>,<noc>` sends NoC first, then minion, both with
`USE_STEP_CLOCK_TRUE`, and stops at the first failure [src: `EP/device-management-application/src/dev_mngt_service.cc:771-796`].
aifoundry3's boot service uses exactly this path (`-f 600,400`) [meas: `docs/reports/data/2026-09-25-aifoundry1/facts.md:209`],
so it works on 1.3.1. The vendor's own test sets minion/NoC to 400/200, 500/250, 600/300 MHz through it [src:
`EP/devicemanagement/tests/TestDevMgmtApiSyncCmds.cpp:1959-2040`].

**Accepted frequencies (100 MHz reference; HPDPLL table)** [src: `HAL/hpdpll_modes_config.h`; calc `pll_modes.out` §1]:
100, 125, 150, 166, 175, 200, 225, 250, 275, 300, 325, 333, 350, 375, 400, 425, 450, 475, 498, 500, 502, 505, 525,
550, 575, 600, 625, 650, 675, 700, 725, 750, 758, 775, 795, 800, 825 … 1050 (25 MHz steps, plus 933, 995, 1010, 1066),
1075 … 1475 (25 MHz steps), 1500, 2000, 4000 MHz. Modes 62–75 (100–350 MHz) came in with etsoc-hal 1.2.0 ("New HPDPLL
modes added", 2022-09-02) [src: `EP/etsoc-hal/CHANGELOG.md:65-69`]; BL2 0.18.0 builds against etsoc_hal 1.6.0 and
0.20.0/0.21.0 against 1.7.0 [src: `device-bootloaders/conanfile.py:52` at @O/@C/@N], and no later changelog entry
touches the tables, so **the lab's builds have the same list** [inf from the changelog; the pinned 1.6.0/1.7.0 packages
themselves are not in the tree].

**LVDPLL table (100 MHz reference):** 300–1400 MHz in 25 MHz steps, 45 modes [src: `HAL/lvdpll_modes_config.h:27-512`;
`HAL/lvdpll_defines.h:61-71,145-191`]. Reachable only with `use_step_clock = 0`, which the stock CLI never sends, onto a
PLL the errata calls unstable.

**The governor's range is separate:** the VMIN-table validator accepts minion points 300–800 MHz / 460–620 mV, SRAM
670–850 mV, NoC 300–500 MHz / 485–600 mV [src: `@C thermal_pwr_mgmt.c:70-133`; same in @N and HEAD]; an out-of-range
table turns active power management off at boot (0.20.0+: `@C :1703-1723`). 0.18.0 steps 50 MHz within 300–700 MHz
[src: `@O thermal_pwr_mgmt.h:56-58`].

**Below 100 MHz** [calc `pll_modes.out` §4]: 50 MHz would need a post-divider of 22–80 (HPDPLL) or 22–42 (LVDPLL), 25 MHz
43–160 / 43–84, 10 MHz 107–400 / 108–210, all within the 511 / 255 field limits; the extreme with the tables' lowest DCO
is ≈ 2.1 MHz (HPDPLL) and ≈ 4.2 MHz (LVDPLL). The PLLs also have a reference pre-divider (PRM: "bits 7:0"; IP-XACT: 9 bits for the HPDPLL,
8 for the LVDPLL) and an open-loop bypass mode [ext: PRM:13346-13378]. None of this is reachable without a modified BL2 image (signed and
flashed; not tested here) or JTAG/debugger access. `DM_CMD_MDI_*` (minion debug) is not a path either: its memory write
reaches only the host-managed DRAM, the user-mode kernel stack and the MM and CM trace buffers
[src: `@C BL2/services/minion_debug.c:134-158,698-710`], none of them a PLL register (checked 30 September, after review).
Whether the Movellus DCO locks with such dividers, and whether the shire DLL (locked at 100 MHz) tracks a slower clock,
is **not established**.

## 3. Voltage rails, regulators, the table, the floors, and the hazards

**Regulators** [ext: CARD "Key Voltage Regulators"]: minion and NoC share a TI TPSM831D31 (minion on a 3-phase output,
120 A max; NoC single phase, 40 A); SRAM ("SCW") on an LTM4680 (60 A). All rails are set by the SP through the PMIC over
I2C. The PMIC also has 17 per-group minion voltage registers (G1–G17) that the SP driver can write but never calls [src:
`BL2/driver/pmic_controller.c:1652-1760` (HEAD); `BL2/include/pmic_hal.h:175-178`; no caller in BL2].

**Encoding:** mV = base + multiplier·code: 250 + 5·code for minion, SRAM, NoC, DDR, Maxion; 250 + 10·code for VDDQ,
VDDQLP; PCIe-logic and PCIe use 600 base with other steps [src: `BL2/include/bl2_pmic_controller.h:133-162`]. Code 0 = 250 mV.

| Rail (firmware name) | Firmware accepts (0.20.0/0.21.0/HEAD) | 0.18.0 | Boot default if the flash table is unset | Set-point on the cards [meas] |
|---|---|---|---|---|
| MINION ("MNN") | 400–620 mV | no check | 500 mV | aifoundry2 520, aifoundry3 525, card 1 500 (600 MHz); card 0 ≈ 398 at 300 MHz |
| L2CACHE / SRAM ("SRM") | **660**–850 mV | no check | 750 mV | 705, 700, 750 |
| NOC | 400–600 mV | no check | 485 mV | 485 on all |
| DDR | 700–870 mV | no check | 800 mV | 800 |
| MAXION ("MXN") | 600–870 mV | no check | 850 mV | 600 |
| PCIE_LOGIC ("PCL") | 731.25–815 mV | no check | 775 mV | 775 |
| PCIE | 1400–1525 mV | no check | — | — |
| VDDQ / VDDQLP | 1000–1120 / 580–660 mV | no check | — | 1100 / 640 |

Sources: range checks `@C BL2/include/bl2_pmic_controller.h:170-248` and `@C BL2/driver/pmic_controller.c:1409-1473`
(`pmic_validate_voltage`, compiled out only in FAST_BOOT); @O's header has no `*_MIN_VAL_mV` [calc §5]; boot defaults
`@C BL2/include/thermal_pwr_mgmt.h:93-98`; set-points = `reg_mv` in the first sample of
`docs/reports/data/2026-09-25-claims-v3/raw/{aifoundry2,aifoundry3,aifoundry1-c1}/tel/p1/e10.jsonl.gz` [meas];
card 0 from `14-card-behaviour.md:148-150` [meas].

**The operating-point table** is the per-card flash "VMIN LUT": 11 points, each with minion, SRAM, NoC, PCIe-logic, DDR
and Maxion frequency/voltage pairs; point 0 is the boot point [src: `EP/device-bootloaders/src/shared/common/include/service_processor_BL2_data.h:77-100`;
`@C BL2/driver/flashfs.c:2159-2219`]. Measured on aifoundry2: 600/700/800 MHz at 0.517/0.568/0.618 V on-die
[meas: `docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json` `.operating_points`]. The full table of any lab card has
not been read; `DM_CMD_GET_VMIN_LUT` (73) is a read-only query that would give it (NV plans to read it). `DM_CMD_SET_VMIN_LUT`
(72) writes the flash (0.19.0+) [src: `@C flashfs.c:2087-2155`].

**Floors.**
- Firmware floors: above (0.20.0+). 0.18.0 has none; its governor's own clamps are minion 400–650, SRAM 650–1000 mV
  [src: `@O thermal_pwr_mgmt.h:61-66`].
- The vendor's lowest point: the safe state, 300 MHz with minion 0x1E = 400 mV and SRAM 0x52 = 660 mV (0.21.0, HEAD) [src:
  `@N thermal_pwr_mgmt.h:67-80`]. Both constants carry the comment "TODO: to be removed and replaced with vmin lut value"
  [src: HEAD `BL2/include/thermal_pwr_mgmt.h:67-75`], and `Minion_Get_Voltage_Given_Freq` returns them for a 300 MHz target
  [src: HEAD `BL2/driver/minion_configuration.c:1000-1002,1039-1041`]: a lookup, not a validated operating point [inf]. In **0.20.0 the safe SRAM value is 0x50 = 650 mV, below that build's own 660 mV check**
  [src: `@C thermal_pwr_mgmt.h:76` vs `@C bl2_pmic_controller.h:170`; fixed by `e024210bc` "Fix go to power safe state",
  2024-09-05]. It is latent on the cards: 0.20.0's safe path does not set voltages (`@C thermal_pwr_mgmt.c:2001-2060`),
  and the table path reaches 300 MHz only if the card's table contains it [inf]. If it were ever applied, the range
  error would enter the endless retry below.
- SRAM retention: no figure in the firmware, PRM, datasheet or errata text searched. The SRAM rail has the least room:
  from 700–705 mV today to the 660 mV floor is 40–45 mV [meas + src].
- Regulator limits: not stated in the sources; the encoding bottoms at 250 mV.

**Coupling in the governor.**
- 0.20.0: `set_minion_operating_point()` looks up minion and SRAM voltage for the target frequency in the table, sets
  minion then SRAM voltage, then PLL4, in both directions; returns at once if the target equals the current frequency
  [src: `@C thermal_pwr_mgmt.c:1781-1877`; "Set L2cache voltage, it is using same clock as minion" `:1821`]. An off-table
  frequency is an error (`flash_fs_get_minion_voltage_for_freq`) [src: `@C minion_configuration.c:1020-1070`].
- 0.21.0/HEAD: up = voltage first, down = frequency first [REV §3; src HEAD `thermal_pwr_mgmt.c:1700-1761,1805-1864`].
- 0.18.0: voltage = boot voltage ∓ 10 mV per 50 MHz, clamped [src: `@O minion_configuration.c:267,272,1030-1110`]. With card
  1's boot 500/750 mV this gives 440/690 mV at 300 MHz and 400/650 mV at 100 MHz [calc §6] — only if its governor acted;
  it does not (card 1's clock never left 600 MHz in 359,657 samples, REV §5).
- The governor refreshes its cached rail voltages from the PMIC every dm pass (`update_module_soc_power` →
  `get_module_voltage`) [src: `@C thermal_pwr_mgmt.c:782,975-1040`], so a voltage set by hand is seen within one pass
  (~133 ms) [inf].

**Hazards (voltage writes).**
1. **Endless retry → watchdog reset (0.20.0; likely 0.21.x).** `Thermal_Pwr_Mgmt_Set_Validate_Voltage` loops inside
   `portENTER_CRITICAL()` and decrements its 3 retries only on the on-die (PVT) check failure; a range error or a failed
   regulator write/read-back loops for ever, until the SP's 10 s watchdog resets the SoC [src: `@C thermal_pwr_mgmt.c:3166-3215`;
   fix `7c6049087`, 2024-10-10, after 0.21.0; `14-card-behaviour.md:249-253`]. `SET_MODULE_VOLTAGE` (35) goes straight
   into it for any rail [src: `@C thermal_power_monitor.c:299-321`]. Keep every value inside the table above.
2. **0.18.0 writes every NoC set to flash** as the boot voltage (erase + reprogram of the asset-config sector) [meas/src:
   `14-card-behaviour.md:241-248`; `tools/claims-v3/nv/DESIGN.md:43-58`]. Never set a voltage on card 1.
3. A reset clears aifoundry3's TDP-0/600 MHz clock guard until the lab admin re-runs it [`nv/DESIGN.md` §7].
4. `SET_FREQUENCY` does not touch voltage: raising the clock after a manual undervolt leaves the card undervolted.
   Order for a low point: frequency down first, then voltage; back up: voltage first, then frequency [inf].

## 4. Power gating, masks, and whether an unused shire leaks (shortened)

- **Firmware gates nothing** beyond debug clocks [src: `minion_configuration.c:353-358,611`; `BL2/driver/mem_controller.c:131`].
  The hardware documents per-neighbourhood power on/off and per-minion sleep [ext: PRM:15262-15277], and the errata says
  neighbourhoods "can be dynamically powered off (if the PCB design allows for this)" [ext: ERR:1614-1615], but the card
  feeds every minion from one regulator output [ext: CARD] and no firmware writes those controls.
- BL2 enables all 34 shires whatever the fuse mask says ("Workaround to get rid of a bug that causes huge excess current
  draw") [src: `minion_configuration.c:581-612`, the same in every build].
- **Unused shires leak**: the idle minion rail is 11.05 W at 73 °C on aifoundry2, about 0.33 W per shire
  [meas: `docs/findings/16-dvfs-and-leakage.md` E19; calc §6].

## 5. What must keep running, and what it costs (shortened)

The service processor (1000 MHz; its watchdog is 10 s, kicked every 8 s [src: `BL2/include/config/mgmt_build_config.h:414-417`]),
the PCIe shire and link (505 MHz; a link retrain hung aifoundry1's host on 30 September [meas: `docs/findings/14-card-behaviour.md`]),
the NoC (400 MHz), the memory shires and LPDDR4X (933 MHz, auto-refresh on, power-down and self-refresh disabled "for
performance reasons" [src: `EP/etsoc-hal/src/memshire_ddr_init_functions.c:5459-5475`]), the Maxion rail (600 mV, cores
not booted) and the master minion (shire 32, on the minion step clock). Idle board power splits as 11.05 W minion +
2.00 W SRAM + 3.64 W NoC + 15.10 W off the rails = 31.79 W at 73 °C [meas: E19]; the NoC rail and the off-rail part,
18.74 W (59 %), do not depend on the minion clock [calc §6]. aifoundry1 card 0 idling at 300 MHz / 398 mV draws
18.6–18.8 W [meas: `14-card-behaviour.md:148-150`].

## 6. What happens to a running card if the minion clock is set very low (100 MHz)

**Everything that runs on the minion clock slows together:** compute minions, their L1, the shire caches (L2/L3/SCP)
[ext: ERR:1629-1630; src `@C thermal_pwr_mgmt.c:1821`], and the master-minion runtime on shire 32 [src: `main.c:289-291`,
the step clock goes to all 33 virtual shires]. The NoC, DDR, PCIe and the SP do not [§1].

**Timers are wall-clock:**
- SP watchdog 10 s and the MM-heartbeat watchdog 10 s (`MM_HEARTBEAT_TIMEOUT_MSEC 10000`, one-shot FreeRTOS timer
  restarted by each heartbeat; expiry logs "MM Hung" and runs the MM error handler, a recoverable event) [src:
  `BL2/include/minion_configuration.h:43`; `minion_configuration.c:547-560,1892-1907`]. Both count SP time.
- The MM's heartbeat and its kernel timeouts run on the PU timer (`SW_TIMER_HW_COUNT_PER_SEC`, `PU_Timer_Init`) [src:
  `EP/device-minion-runtime/src/MasterMinion/include/services/sw_timer.h:24-28`; `…/src/services/sw_timer.c:202`]:
  heartbeat every 100 ticks (measured ≈ 1.05 s, REV §1.4), `KERNEL_LAUNCH_WAIT_TIMEOUT` 10 ticks, `KERNEL_CM_ABORT_WAIT_TIMEOUT`
  5, `CW_INIT_TIMEOUT` 5 [src: `…/include/workers/kw.h:41,46`; `…/include/workers/cw.h:36`]. If a tick is ≈ 10.5 ms (the
  measured heartbeat ÷ 100) these are ≈ 105 ms and ≈ 52 ms windows for minion-side handshakes that take 6× longer at
  100 MHz [inf; the margin at 100 MHz is not established].
- Host runtime: `waitForEvent`/`waitForStream` default to 24 h, `abortCommand` to 5 s [src:
  `EP/esperanto-tools-libs/include/runtime/IRuntime.h:283,294,353`]. The binding limit is the lab's own: never hold a device
  more than 10 s (`timeout 10`). A compute-bound kernel takes 6× longer at 100 MHz than at 600 MHz [inf].

**The governor, by build** (details and line numbers in REV §2–§5):
- **0.20.0, active (aifoundry2).** An off-table clock cannot be stepped: `increase`/`reduce` log ERROR "Failed to find
  input frequency in vmin lut" and keep the clock [src: `@C thermal_pwr_mgmt.c:1899-1954`; exact-match lookup
  `@C flashfs.c:2370-2404`]. Consequences [inf from source]:
  - on the next kernel (MM busy, power < TDP) the POWER_UP loop can never meet its exit (average > TDP, or clock = table
    maximum) and **spins for ever with no delay**, as aifoundry3's POWER_DOWN loop does — the governor is then dead until an
    SP reset and the clock stays at 100 MHz [src: `@C :2173-2256`];
  - but if the SP is in (or enters) the thermal loop, its exit at a mean ≤ 65 °C, and any serviced POWER_IDLE, run
    `go_to_idle_state()` = table point 0 = **600 MHz with its voltages** [src: `@C :1975-1979,2366-2369,2446-2449`].
    aifoundry2 idles at 66–80 °C in its chassis (REV §10), so it is usually already in that loop; a 100 MHz clock would
    cool it below 66 °C and the loop's exit would restore 600 MHz.
  - Turning active power management off (24) stops new triggers (`@C :670,844`) but not a loop already running. A clean
    hold needs the governor quiescent first (for example APM off plus a raised threshold so the loop exits once), then
    the clock set. All of these are governor settings: the owner's call.
- **0.20.0, latched (aifoundry3).** Its zero TDP has left the power task spinning and the state latched since boot; no
  governor path runs [REV §4; meas: 600 MHz at every temperature]. A `SET_FREQUENCY` there would simply stay until an SP
  reset or the next run of the lab's clock guard [inf]. It is also the card whose clock path is exercised at every boot.
- **0.21.0/HEAD (card 0's lineage, 0.21.2 not public).** Only while a kernel runs; at 100 MHz neither down-test fires
  (clock not above the table minimum) and the up request fails every pass with an ERROR line; a failed transition leaves
  the task's state unchanged, so if it was IDLE the busy→idle notification is ignored and 100 MHz persists [src HEAD:
  `thermal_pwr_mgmt.c:864-926,1929-1956,2244-2256,2286-2293,3110-3124`; inf]. Card 0 is off-limits (overheats).
- **0.18.0 (card 1).** Steps ±50 MHz clamped to 300–700: a "reduce" from 100 MHz would *raise* the clock to 300 MHz
  [src: `@O thermal_pwr_mgmt.c:1769-1811`]. Its governor has been inactive all along (REV §5).

**Clock changes during a kernel:** two relay launches returned wrong elements when the governor moved 800→600 MHz inside
the launch [meas: `16-dvfs-and-leakage.md:44`]. Change the clock only between kernels [inf].

## 7. Which lab builds differ

| Item | 0.18.0 (1.2.0, card 1) | 0.20.0 (1.3.1, aifoundry2/3) | 0.21.0 / HEAD (≈ 1.4.1, card 0) |
|---|---|---|---|
| Minion clock source at boot | step clock PLL4, 600 MHz | same | same |
| `SET_FREQUENCY` handler, `configure_sp_pll_4`, `Minion_Configure_Hpdpll`, `configure_pll` | identical (function hashes equal across all four commits, `git show` + `md5sum`) | same | same |
| PLL mode tables | etsoc_hal 1.6.0 | 1.7.0 | 1.7.0 (no table change after etsoc-hal 1.2.0 per its changelog, so the same 100 MHz floor [inf]) |
| Rail range checks | **none** | minion/NoC ≥ 400, SRAM ≥ 660 mV … | same |
| Voltage for a frequency | linear 10 mV / 50 MHz from boot point | VMIN table, exact frequency only | VMIN table |
| Governor steps | ±50 MHz, 300–700 | table points; loops (thermal 0.4 s, power no delay) | one point per pass; busy-only |
| Safe state | really sets 300 MHz | cosmetic (register only); SRAM 650 mV constant below its own floor | 300 MHz at 400/660 mV |
| NoC voltage set writes flash | **yes** | no | no |
| Voltage-set endless retry | range: no check; regulator failure: see REV | **yes** | 0.21.0 yes; fixed at `7c6049087` (whether 0.21.2 has it: unknown) |

## 8. What a measurement would need (shortened; the full design is `LOWCLOCK-PLAN.md`)

Read-only queries first (`GET_VMIN_LUT` 73, throttle residencies 29, frequencies 53, voltages 31); then, with the owner's
approval and on an idle aifoundry3 only, `SET_FREQUENCY -f 100,400`, optionally a minion voltage ≥ 400 mV and SRAM
≥ 660 mV (never outside the table of §3, never on card 1); verify the clock by work rate; restore voltage first, then
`-f 600,400`. Nothing here was run.

## 9. Not established

- Whether the minions, the DLL, and the MM runtime work correctly at 100–275 MHz (the modes exist; no record of their
  use on silicon; the vendor test only used minion ≥ 400 and NoC ≥ 200 MHz).
- Anything below 100 MHz: PLL lock with post-dividers > 11, DLL range, shire logic.
- Each card's full VMIN table, and why card 0 idles at 300 MHz / 398 mV when the public 0.21.0 validator rejects minion
  table voltages below 460 mV (0.21.2 may differ, or card 0 sits in the safe state).
- The regulators' own minimum output and any SRAM retention voltage.
- Whether the spare (34th) shire really stays on the reference clock, and its power.
- How much of the 15 W off-rail power is dissipated in the ET package rather than in DRAM chips and regulators.
