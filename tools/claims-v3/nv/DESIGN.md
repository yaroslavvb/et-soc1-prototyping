# NV: does the mesh's cost per bit·hop follow its supply voltage?

Written 2026-09-28, before any card run, and revised the same day after two reviews (safety R1, science R2; §10). The
owner asked on 28 September to validate Q63's explanation, that the mesh's low cost per bit·mm is mostly its 0.485 V
supply. The method is the owner's:

- The theories and their numeric predictions come first, in `predictions.json`. That file is fixed by its SHA-256
  (`PREDICTIONS.sha256`, `freeze.sh --predictions`) and committed before the first card write. Every real block refuses
  unless it checks.
- Iteration happens only on a development card (aifoundry3).
- The validation's remaining values are then frozen (`PREREG.md` with its SHA-256, and `LOCK.sha256` over the runner)
  and validated on a different card: aifoundry2, once DV2's validation there has ended.
- The summary says which theories survived.

Nothing here has touched a card. `README.md` says how to run it.

## 1. The question

The heat-per-mm page measures the mesh's data cost at 90–105 fJ per random bit per hop on the mesh rail (E42,
`wsep` link-disjoint pairs, d = 1–4), about 25 fJ per bit·mm. Q63 (`docs/findings/02-requests.md`,
`20-heat-per-mm.md`) explained the gap to Dally's ~100 fJ per bit·mm as "mostly voltage". A full-swing wire's energy
per transition is C·V². At 0.485 V it costs (0.485/0.9)² = 0.29 of what it costs at the literature's 0.9 V. That is
an inference from scaling rules. NV tests it by changing only the thing the explanation names: the mesh (NoC) rail's
supply.

## 2. What changes and what is held

| | Value | How it is enforced |
|---|---|---|
| **Changed:** NoC rail set-point | 485, 540 and 600 mV only | `nv_set` in `block.sh` refuses anything else (a hard-coded `case`, then nv.json `allowed_mv`, then an exact `NOC,<mV>` argument check). `nvlib.py` refuses any level outside 485–600 mV. |
| Held: NoC clock | 400 MHz | The set writes only the regulator register (U1, `pmic_controller.c`). `mhz.noc` is read in every sample, and a window off 400 MHz aborts the pass. That value is the PLL's configured divider (`calculate_pll_freq`), not a measured clock, so **C-BW** (§5) checks the clock and the routing by the work done: bytes per launch at each level against 485 mV. |
| Held: minion clock | 600 MHz | aifoundry3 is pinned. aifoundry2's governor lifts the clock off 600 MHz on a die below ~68 °C, so there E42's heater holds the die at ≥ 69 °C (below). `analyze_wire.bursts()` drops any burst with a sample off 600 MHz, and the idle quantities use only samples at 600 MHz. |
| Held: traffic | E42's eight `wsep` configurations: P = 0 and ½, d = 1, 2, 3, 4, link-disjoint `--pairs` | The arguments are copied from `tools/claims-v3/wire/configs.json`, byte for byte. |
| Held: fill, burst and meter | `tstore_uniq` fill; a 3 s burst of 8 launches of 0.4005 s; the mesh rail over the burst's last 0.6 s ÷ 0.94 against the idle in [lo−2.5, lo−0.3] s | `analyze_wire.bursts()`, unchanged |
| Held: heat (aifoundry2) | E42's: heat to 76 °C under the lock before the first set, then one 2 s heater launch before any idle window or configuration whose die reads below 69 °C | The heater is aifoundry2's (`lib.sh` `HEATER`); each launch is marked in `marks.jsonl`, so `analyze_wire` keeps it out of every idle bracket. aifoundry3 runs no heater. |
| Not touched | the minion, SRAM and other rails; TDP; firmware; the VMIN table and the flash | Only `DM_CMD_SET_MODULE_VOLTAGE NOC` is issued, and only on BL2 0.19.0 or later (below). `DM_CMD_SET_VMIN_LUT` is never used. The VMIN table is read before the first set, after it, and at the end. |

The midpoint, 540 mV, gives three points for the exponent. It is also a gentler first write: the probe sets 540
before 600.

**The firmware and the flash.** On BL2 0.18.0 (release `da192816a`, 2024-03-27), `pwr_svc_set_module_voltage` calls
`flash_fs_set_vmin_lut_boot_voltages()` for `MODULE_NOC`. That function erases and reprograms the 4 KB asset-config
sector (the part number and the VMIN table), and the boot code (`main.c`) takes the NoC rail's boot voltage from it.
The write came in with `5f5c37abf` (2024-03-20) and was removed by `dd8927ce5` (2024-04-05). BL2 0.20.0 (`ffca4cbb4`)
does not write the flash. On 0.18.0 every NV set would therefore become the card's boot voltage. A kill, a crash or a
power loss before the restore would leave the card booting at 540 or 600 mV, and a reset during the erase could
corrupt the sector. The flash write's status also overwrites the set's own status, so a failed on-die check would
reach the host as "succeeded". NV therefore:

- never sets a rail on BL2 below 0.19.0. `nv_set` refuses it hard-coded, and nv.json `min_bl2` again. The BL2 version
  comes from the identity call's "BL2 Firmware versions" line, and a card below it gets NV's STOP;
- no longer uses aifoundry1's card 1 (BL2 0.18.0; E42 read 1.2.0 / 0.18.0 on 25 September). aifoundry2 (1.3.1, BL2
  0.20.0, the same build as aifoundry3) is the validation card, after DV2's validation there has ended;
- reads the VMIN table (`GET_VMIN_LUT`) before the first set, right after it, and at the end. A change raises
  `ALERT-NV-FLASH`. A change after the first set stops the block before any other set.

**The firmware's limits.** On BL2 0.20.0 the set command's range check (`pmic_set_voltage`: 400–600 mV inclusive, so
600 mV is its top code 0x46) returns its error into `Thermal_Pwr_Mgmt_Set_Validate_Voltage`'s retry loop. That loop
counts its retries down only on the on-die (PVT) failure branch. A range error, or a regulator write or read-back that
fails, therefore loops inside a critical section until the watchdog resets the SoC. The value is never refused (U1;
the fix, `7c6049087` of 2024-10-10, is later than the lab's builds). BL2 0.18.0 has no range check. **The whitelist
is the only guard on either build.** The "485–600" in `20-heat-per-mm.md` §"Tests" is the range the VMIN table must
stay inside (`VMIN_LUT_NOC_MIN_VAL_mV` is 485), not the command's range. That line needs correcting by its owner.

**One card per host.** The stock `dev_mngt_service` opens every card's management node (`DevicePcie.cpp`), whatever
`-n` says. `DeviceManagement::getInstance` starts a reply reader on each. On aifoundry1 every call would open card 0,
which is never to be touched, and would depend on its single-opener node being free. NV runs only on a host with
exactly one `/dev/et*_mgmt`: a listing of `/dev`, which opens no node. It also refuses any `V3_DEVICE`. Driving a card
of a two-card host would need a client that opens only that card, for example `setvolt`, `getvolt` and `fwrev`
subcommands in `tools/ettelem` run under `ET_DEVICES`. That is not built.

## 3. Theories and predictions

Write each quantity as Q(V) = Q(485)·(V/485)^n. The prediction is the exponent n. The ratio to 485 mV is 1.1134^n at
540 mV and 1.2371^n at 600 mV. The base values are E42's medians over six passes, recomputed from the raw data with
`analyze_wire.bursts()` (mesh rail, `wsep` d = 1–4, fJ/bit/hop):

| Card | Data part D | Zeros part Z | Idle rail I |
|---|---|---|---|
| aifoundry3 (development) | 90.45 (per-pass CV 2.2%) | 42.6 (2.0%) | 2.47 W at 57 °C |
| aifoundry2 (validation) | 89.48 (3.1%) | 43.87 (3.1%) | about 4.1 W at 75 °C, with the heater |

**The data part, D.** D is the random-bit slope minus the zeros slope: the cost of the bits toggling.

| Theory | Mechanism | n | ×540 | ×600 | aifoundry3 D at 540 / 600 | aifoundry2 D at 540 / 600 |
|---|---|---|---|---|---|---|
| **TH-V2** (Q63 as stated) | Full-swing links and repeaters, E = α·C·V². The per-bit·mm cost at 600 mV would be 37 fJ, against 24 at 485. | 2 | 1.240 | 1.530 | 112.1 / 138.4 | 110.9 / 136.9 |
| **TH-V1** | Low-swing or regulated-swing links: E = C·V_swing·V, with V_swing held by a reference, so the cost goes as V. Also a partly regulated mix at its low end. | 1 | 1.113 | 1.237 | 100.7 / 111.9 | 99.6 / 110.7 |
| **TH-0** (null) | The data cost does not follow this rail: the links run from another supply, or the meter does not see them. | 0 | 1 | 1 | 90.5 / 90.5 | 89.5 / 89.5 |
| TH-X | Faster than V²: more glitching as delays change, or a meter artefact. No mechanism is expected. | > 2.5 | | | | |

**Short-circuit current** would push n slightly above 2, still inside TH-V2's band. It is the usual reason energy
rises faster than V². With the N7-class low-V_t cells likely here (V_t ≈ 0.2–0.3 V), V − 2V_t is near zero at 485 mV
and reaches about 0.2 V at 600 mV, so it is small but not ruled out.

**Burst heating adds a little leakage inside D and Z.** In E42 on aifoundry3 the die warmed by 1.07–1.96 °C during
random-data bursts and by 0.21–0.83 °C during zeros bursts. At the rail's ~0.08 W/°C that is about +2.0 fJ in T's
slope and −0.6 fJ in Z's, about 3% of D at 485 mV. Its exponent is about 2.4 against D's 2, so it biases n_D by about
+0.01–0.02 and changes no verdict. `reduce.py` reports the burst heating (T_burst − T_idle) per level.

**The zeros part, Z: TH-DI.** Z is the per-hop cost that does not depend on the data: clock gating, flops, the
router's control and the header. It is CMOS dynamic energy on the same rail, so it also goes as V², n = 2. Predicted
Z: aifoundry3 52.8 at 540 mV and 65.2 at 600 mV; aifoundry2 54.4 and 67.1. The same four bands as D apply: TH-DI
passes in the V² band, and TH-DI-V1, TH-DI-0 and TH-DI-X are its rivals.

**The idle rail, I: TH-LEAK.** The rail's idle power is the clock tree's dynamic power (C·V²·f, n = 2) plus leakage.

- Leakage power is V·I_sub, with I_sub ∝ exp(η·V/(m·V_T)). Its exponent is n_leak = 1 + η·V/(m·V_T).
- The full range: DIBL η of 0.03–0.15 V/V, a slope factor m of 1.1–1.5, V_T = 28.4 mV at about 57 °C (V ≈ 0.54 V)
  give n_leak in [1.4, 3.6]. FinFET values (η 0.03–0.08, m 1.05–1.2) give about 1.5–2.4.
- Gate leakage would be steeper and junction leakage flatter; both are small.
- The rival TH-I-V1 (a constant current, n ≈ 1) sits close to the low end of that range. Low-DIBL leakage and a
  constant current cannot be told apart at NV's resolution.
- **So the decided contrast is whether the idle rail follows the rail at all.**
  - TH-LEAK: n_I in [1.0, 3.5], so the current rises with the voltage.
  - TH-I-0: n ≤ 0.5, so the reading does not follow the rail.
  - Where the interval sits against 1.25 (constant-current-like below, leakage-like above) is reported as
    descriptive.
- Predicted on aifoundry3: 2.75–3.60 W at 540 mV and 3.06–5.20 W at 600 mV (3.20 and 4.12 W at a central n = 2.4).
  On aifoundry2: 4.56–5.97 and 5.07–8.63 W (5.31 and 6.83 W).
- **Temperature.** The idle rail is mostly leakage. E44's cooling curves give d ln I/dT = 2.7–2.9 %/°C on all three
  cards (0.028/°C registered; `predictions.json`). A 1 °C difference between a level's idle window and the 485 mV
  window therefore moves n_I by about 0.13, and the six orders do not balance carry-over: 600 mV is never preceded by
  600, so warmth left by a 600 mV segment lands only on 485 and 540.
- **NV-I is therefore decided on I_tc:** each level's idle rail corrected to the pass's 485 mV idle die temperature
  with that coefficient. The uncorrected exponent is reported as a sensitivity result. The end-of-pass 485 mV window,
  against the pass's 485 mV segment, is a drift diagnostic.

**Q63's per-hop against per-mm test is not registered.** No route that the existing kernels can make crosses a
memory-shire column (U2 §3):

- The memory shires fill the west and east edge columns.
- All 32 addressable shires are minion tiles inside the 6 × 6 block.
- Dimension-ordered routes stay inside the rectangle their two ends span.
- Every hop is one tile pitch of 3.70–3.73 mm. x and y differ by 0.8%, below NV's resolution of about 3%.

Separating per hop from per mm needs new kernels and the floorplan.

**What each outcome would mean for Q63:**

- TH-V2 passes: the explanation's voltage dependence holds over 485–600 mV. This is a local exponent over ×1.24 in
  voltage. Q63's scaling to 0.9 V is ×1.86, an extrapolation, and a V² result does not by itself mean full-swing
  links: charge-sharing low-swing links also scale as V².
- TH-V1 passes: only a V¹ part holds, so the links are low-swing or regulated. The page's "×3.44 to 0.9 V" would then
  overstate the voltage effect (×1.86).
- TH-0 passes: the explanation fails.

## 4. Measurement

**A pass.** One pass is one block, `block.sh <pass>`, and takes about 6.6 min (plus heating on aifoundry2):

1. **Gate.** The pass does not start if any of these is present:
   - the host has other than one card, or `V3_DEVICE` is set;
   - `PREDICTIONS.sha256` does not check;
   - on aifoundry2, `build/claims-v3/aifoundry2/nv/CARD-RELEASED` is missing;
   - another claims-v3 queue or block runs on the host (DV2's, say);
   - STOP files, unresolved `ALERT-NV-*.json`, or a dirty state file;
   - other users or device processes (`lib.sh`), our own device processes, or `et-who --check` ≠ 0.
2. **Card lock.** Then `flock -n` on the card lock, held until the block exits, and by the guardian after it (§7).
3. **Checks, one `dev_mngt_service` call each:**
   - identity: the firmware release must be the card's (1.3.1 on both), and BL2 must be 0.19.0 or later;
   - the card's uptime (a reset is detected against it at the end);
   - temperature: the minion-shire mean ≤ 85 °C, and every current reading < 90 °C;
   - the rail must read the base, 485 mV, the on-die monitor must be within 5%, and the NoC clock must read 400 MHz;
   - the VMIN table.
4. **Heating** on aifoundry2 (§2), under the lock.
5. **Three segments,** one per level, in the pass's order. Each segment:
   - **The step:** set, read back through the regulator (`GET_MODULE_VOLTAGE` must equal the level), and through the
     on-die monitor (`GET_ASIC_VOLTAGE` within 5%, the firmware's own tolerance). After the first set off the base,
     the VMIN table is read again.
   - **A settle** of 6 s.
   - **An idle window.**
   - **The eight configurations,** shuffled per segment (seed 7100 + 100·pass + segment). Each configuration is a fill
     (≤ 2 tries: a failed fill would leave the previous image, the cause of E42's aifoundry3 pass-4 anomaly), 1.5 s,
     then a sampler window holding the burst, then 1 s.
6. **The restore:** set 485 and verify it (§7), then 6 s and a last idle window. That window must show `reg_mv.noc` =
   485, the on-die median within 10 mV of its expected value, and 400 MHz in the telemetry. The uptime and the VMIN
   table are then read again.

**Voltage order.** The six orders of the three levels are nv.json `orders`. Pass p runs order (p − first pass) mod 6,
so six passes contain each order once. Each level then takes each position twice, and a linear drift within a pass
(heat, the SP's averages) cancels in the mean exponent. Every pass contains every level, so the comparison is paired
within the pass. This counterbalances across passes rather than within one (ABBA), which keeps the voltage writes to
three per pass: each write is a risk (§7). Carry-over is not balanced (§3); the idle rail is corrected for it.

**A spare validation pass** takes the order of the earliest regular pass whose `block.json` status is not ok and that
no ok spare has replaced. It needs no result, only the run's status, so the orders stay balanced whatever failed.
`reduce.py` reports the order balance of the valid passes.

**Sampler windows, not a block-long sampler.** Each window is one `ettelem sample --seconds 9` under
`timeout -k 3 10`:

- The etiquette caps every device process at 10 s.
- The management node has a single opener, and the set needs it between segments.

Inside a window:

- The burst starts ≥ 2.8 s after the sampler's first line and ≥ 5.0 s after the fill ends, and never later than 5.0 s
  after the sampler's launch. Otherwise the window is "late" and the configuration is repeated.
- That leaves `analyze_wire.bursts()` its brackets: before-idle ≥ 2.8 s, rail-idle [lo−2.5, lo−0.3] s, and ≥ 1.3 s
  after.
- The burst is E42's, so the rail's filter (τ ≈ 1.2 s) and the ÷0.94 hold unchanged.
- A sampler that gives no line in 2 s is stopped with SIGTERM and retried (up to 5 starts, with a drain at the third).
  "One start in three fails" is a known trap.
- Only good windows reach `telemetry.jsonl`, `runs.jsonl` and `windows.jsonl`. The others go to `*-rejected.jsonl`,
  so two attempts never merge into one burst.

**The temperature rule reads current values.** The DM call's "MINSHIRE High" and "IOSHIRE High", and the telemetry's
`minshire[2]` and `ioshire[2]`, are the PVT's latched HILO watermarks, not readings. E42 on aifoundry2 read a
minion-shire high of 93, 93, 95, 81, 91 and 106 °C, constant through each pass. The 90 °C rule is therefore applied
to the current readings (the minion-shire mean, the IO shire's current reading, the PMIC's), and to a watermark only
if it rises during the block to 90 °C or more: then some sensor reached it.

**The lock is held for the whole pass,** about 7 min. This is the framework's block convention, and here also a safety
property: nobody else runs on the card while its rail is stepped. Every device process inside the pass is still capped
at 10 s.

**NV's own queue.** `run-queue.sh`, not `tools/claims-v3/queue.sh`, runs the passes. On a multi-card host
`queue.sh`'s cooling wait samples the card with the sampler, without the card lock, under `timeout 20` and before its
checks. The NV runner opens no device. `block.sh` checks the temperature under the lock and exits 3 (retried in 10
min) when the die is too warm.

**Departures from E42:**

- a sampler per window instead of per block;
- 8 configurations instead of 28;
- NV's own checks on each window (§5, §7);
- the heater's checks read the die through `dev_mngt_service` under the lock, not through a separate sampler.

## 5. Statistics and decision rules

What decides is in `predictions.json` (the bands, the E42 references, the controls' rules, the pass-count rule). It is
fixed before the first card write, and development may change nothing in it. Development may change only nv.json's
timing, limits, heater and burst-drop fields. Any change is recorded in `PREREG.md` §3.

**Per burst.** `analyze_wire.bursts()` computes each burst, then NV drops it if any of these holds:

- `reg_mv.noc` ≠ the level in any sample of the burst or its rail-idle bracket;
- the median `die_mv.noc` is more than 10 mV off the level × (the pass's own on-die reading at 485 mV) / 485. A card
  whose monitor reads 2% low at every level thus keeps its bursts, as it would under the firmware's 5%;
- any `mhz.noc` sample is not 400 MHz;
- it has fewer than 7 launches;
- a rail spike: the max − min of the rail in the last 0.6 s exceeds 2.0 W. Normal bursts reach at most 0.47 W at
  485 mV; E42's aifoundry1-c1 pass 6 had 7.0 and 7.3 W.

**Per pass and level:**

- Z and T are the least-squares slopes of the rail's pJ per byte against d, in fJ per bit per hop (×125), for P = 0
  and P = ½ respectively.
- All three levels of a pass are fitted on the hops every level kept. At least 3 of the 4 hops are needed.
- D = T − Z.
- I is the mean rail in the segment's idle window after its first 3 s, over samples at 600 MHz. I_tc is the same,
  each sample corrected to the pass's 485 mV idle die temperature by exp(−0.028·(T − T_ref)).

**Per pass and quantity** (D, Z, T, I_tc; I reported): n_p is the least-squares slope of ln Q on ln(V/485) over the
pass's three levels.

**A pass is valid** when all of these hold:

- block status ok;
- the restore verified;
- D, Z, I and I_tc present and > 0 at every level;
- ≥ 75% of its bursts kept.

**Across passes** (the pass is the unit of replication):

- Compute the mean, the 95% t-interval (df = n − 1) and the 95% percentile bootstrap over passes (20,000 resamples,
  seed 20260928).
- The **verdict interval is the hull of the two**: the bootstrap is anti-conservative with six passes, and the hull
  is never narrower than either.

| Band | Exponent |
|---|---|
| TH-0 | (−∞, 0.5] |
| TH-V1 | [0.5, 1.5] |
| TH-V2 | [1.5, 2.5] |
| TH-X | [2.5, ∞) |
| TH-LEAK | [1.0, 3.5] |

The boundaries are the midpoints between the predicted integers. TH-LEAK's lower edge is the constant current's n = 1
(§3).

- **PASS:** the verdict interval lies inside the band.
- **FAIL:** it lies wholly outside.
- **INSUFFICIENT:** anything else, and every theory item when fewer than 3 (development) or 5 (validation) passes are
  valid.
- **NOT DECIDED:** a gating control did not pass (the table below). The verdict it would have had is reported beside it.

| Item | Quantity | Theories | Gated by |
|---|---|---|---|
| **NV-D** (primary) | D | TH-V2, TH-V1, TH-0, TH-X | C-METER, C-BW |
| NV-Z | Z | TH-DI, TH-DI-V1, TH-DI-0, TH-DI-X | C-METER, C-BW |
| NV-I | I_tc | TH-LEAK, TH-I-0 (the 1.25 split is descriptive) | C-METER |
| NV-T (reported) | T, the random bit in all | the V2, V1 and 0 bands | C-METER, C-BW |
| **R1** (validation only) | n_D, validation against development | PASS when the 95% Welch interval of the difference lies inside ±tol; FAIL when wholly outside | nD, sdD, nDev and tol frozen in `prereg.json` |

**The controls:**

- **C-N:** valid passes ≥ the minimum.
- **C-RESTORE:** every pass restored and verified.
- **C-REPRO:** the median D at 485 mV within ±10% of E42's median for the card. It checks the new windowing and
  gates any absolute fJ figure and the Q63 line, not the theories, whose test is a paired ratio.
- **C-METER, the rail meter's formula.** The PMIC reads v_out, a_out and w_out separately (`pmic_controller.c`), but
  the SP forwards only w_out, so the host cannot recompute V·I. If w_out were a fixed voltage times the current, every
  exponent would drop by exactly 1. A true V² would then pass TH-V1. C-REPRO cannot see this (it runs at 485 mV, where
  every formula agrees), and neither can the TH-LEAK band. So:
  - per pass, compute the least-squares slope of the 12 V board idle power on the rail idle power across the three
    levels. Take both from the idle window and the eight pre-burst brackets, at 600 MHz. Correct the board to the
    pass's 485 mV idle die temperature with `analyze_wire`'s leakage law, and the rail with the 0.028/°C coefficient;
  - a true meter gives 1/efficiency: predicted 1.1–1.5, and the E42 burst fits give 1.29 on aifoundry3. A fixed-voltage
    meter gives about 2.1–2.8;
  - PASS when the verdict interval lies inside [0.9, 1.8]. A pass counts only if its corrected rail idle rose by
    ≥ 0.25 W from 485 to 600 mV;
  - if most passes' rail did not rise, C-METER is NOT APPLICABLE: the reading does not follow the rail, and only the
    zero theories (TH-0, TH-DI-0, TH-I-0) are decided.
  - The two cards run the same firmware; C-METER is decided on each.
- **C-BW:** for each configuration, bytes per launch at 540 and 600 mV within ±0.5% of the same pass's 485 mV value.
  E42's bytes per burst vary about 0.01% between passes (aifoundry3 hop 1: 4.6362–4.6367e12), so this directly shows
  whether the voltage changed the clock or the routing. It also matters for Z: the rail's excess is nearly constant
  across d (1.07–1.26 W) while the bytes fall from 4.64 to 2.01 TB, so Z is mostly power per unit time divided by
  throughput.
- **C-DROPS:** bursts dropped, by cause.

**Reported, not decided:**

- the exponents using the on-die voltages instead of the set-points;
- the board-power slopes and their exponents (they carry the regulator's loss);
- the die temperature per level, and the burst heating;
- the SRAM and minion rails' idle and burst excess per level, and their 600/485 ratios. They should not move with the
  NoC level; if they do, the power domains are coupled;
- the uncorrected n_I and the end-of-pass drift;
- the ratios to 485 mV with their intervals;
- the order balance of the valid passes.

**Summary.** `reduce.py` prints which theories survived and one line on Q63. The line is printed only when C-N,
C-RESTORE, C-REPRO, C-METER and C-BW all PASS, and otherwise says which did not. It gives the exponent's interval and
the implied factor to 0.9 V (1.856^n over the interval), labelled as an extrapolation, and says that V² does not by
itself mean full-swing links.

## 6. Sample size and duration

Per-pass spreads in E42 (mesh rail, `wsep` d = 1–4, recomputed with `analyze_wire.bursts()`):

| Card | Data part D | Zeros Z | Random bit T |
|---|---|---|---|
| aifoundry3 | 2.2% | 2.0% | 1.2% |
| aifoundry2 | 3.1% | 3.1% | 1.5% |

- **The exponent's spread per pass.** The per-pass exponent's SD is CV/√Σ(x − x̄)², with x = ln(V/485) for the three
  levels; √Σ = 0.1505. This gives 0.146 at aifoundry3's 2.2% and 0.206 at aifoundry2's 3.1%.
- **E42's spread is not a conservative bound.** NV's per-level estimate uses the same eight bursts that E42 used per
  pass, and the per-window samplers add noise.
- **The decision rules' error rates** (`reduce.py --monte-carlo`, 1,000 replicates; per-level noise on D, and a second
  variant that adds E42's per-burst residuals to each hop point through the slope fit):

  | Per-level CV | P(TH-V2 PASS), n = 2 | n = 1.8 | n = 1.7 | P(false PASS), n = 1.5 |
  |---|---|---|---|---|
  | 2.2% | 1.00 (1.00 with bursts) | 0.98 (0.89) | 0.78 (0.59) | V2 0.03, V1 0.02 |
  | 3.1% | 0.99 (0.97) | 0.82 (0.72) | 0.50 (0.38) | 0.02, 0.03 |
  | 5% | 0.69 (0.62) | 0.42 (0.40) | 0.22 (0.20) | 0.03, 0.03 |

  At n = 1 TH-V1 passes with probability 1.00, 0.99 and 0.68 at the three CVs. With the minimum of 5 passes and CV
  2.2%: 1.00, 0.93 and 0.61. The earlier text's "> 0.999 at n = 2" and "0.99 at n = 1.8" were too optimistic.
- **The validation's pass count N is registered now as a rule, not a number:** the smallest N with
  t(0.975, N−1)·SD_dev/√N ≤ 0.25, at least 6 and at most 12. SD_dev is the development per-pass SD of n_D. SD_dev of
  0.10–0.20 gives N = 6, 0.25 gives 7, 0.30 gives 9 and 0.35 gives 11. Above about 0.39 more than 12 would be needed:
  the design is then revisited by an amendment before any validation pass. `freeze.sh` checks `prereg.json`'s
  `val_passes` against the rule.
- **The plan:** N validation passes (101 to 100 + N), plus 2 spares that run only while fewer than N ended ok. For
  development, 6 passes (the minimum is 3).
- **The self-test** (`reduce.py --self-test`) runs the whole pipeline on synthetic pass directories. These carry:
  - per-level noise (2%) and per-burst noise (0.5%);
  - E42's bytes, falling with d;
  - E42's intercepts;
  - a die that drifts per segment, warms with the level and during bursts;
  - an idle rail that follows the die by the registered coefficient;
  - a board meter with the leakage law and an efficiency of 0.8.

  It recovers planted exponents of 2, 1 and 0 within 0.02. It checks:
  - that a fixed-voltage meter fails C-METER (ratio 2.57) and leaves the items NOT DECIDED, with their raw verdict
    dropping from V2 to V1;
  - that 2% fewer bytes at 600 mV fail C-BW;
  - that 3 °C of carry-over at 600 mV leaves n_I_tc at 2.39 against an uncorrected 2.76;
  - a failed restore, a spike and a set-point mismatch;
  - R1 against a wrong development value;
  - a failed pass whose spare, chosen by `nvlib.py`'s own rule, keeps the orders balanced.

**Duration** (from the timing in nv.json):

| Step | Time |
|---|---|
| One configuration | ≈ 13.2 s |
| One segment | ≈ 124 s |
| One pass | ≈ 6.6 min, with the lock held throughout (plus heating on aifoundry2) |
| Development on aifoundry3 | a probe (≈ 1 min), a smoke (≈ 2 min) and 6 passes (≈ 42 min with the queue's gaps): **about 45–50 min** |
| Validation on aifoundry2 | a probe (≈ 1 min) and N passes of ≈ 7–9 min: **about 50 min to 2 h** for N = 6–12, plus the spares |

## 7. Safety and abort rules

**Before the lock.** The block refuses to start (exit 2 unless said otherwise) in any of these cases:

- a host with other than one card, or `V3_DEVICE` set;
- `PREDICTIONS.sha256` missing or not checking;
- the wrong card for the pass: development passes 1–99 only on aifoundry3, validation passes 101–199 only on
  aifoundry2 and only with its release file; nothing ever on aifoundry1 (either card);
- a validation pass whose `LOCK.sha256` or `PREREG.sha256` does not check;
- another claims-v3 queue or block on the host (exit 3);
- a STOP file: the host's `build/claims-v3/STOP` or NV's `build/claims-v3/<card>/nv/STOP` (exit 0);
- any `ALERT-NV-*.json` (a person must look first; exit 1);
- a dirty state file, which also writes `ALERT-NV-STATE` and the host's STOP (exit 1);
- other users or device processes (`lib.sh`), our own device processes, or `et-who --check` ≠ 0 (exit 3).

**Before the first set.** No set is issued unless all of these hold:

- the firmware release is the card's and BL2 is 0.19.0 or later (else NV's STOP; exit 2);
- the uptime reads;
- the minion-shire mean is ≤ 85 °C and every current reading < 90 °C (else exit 3: the queue retries in 10 min);
- the rail reads 485 mV. At any other value the block issues nothing and restores nothing, and raises
  `ALERT-NV-STATE`;
- the on-die monitor is within 5%;
- the NoC clock is 400 MHz;
- the VMIN table reads.

**Every device process** runs under `timeout -k 3 10`: each `dev_mngt_service` call (with `-u 5000`, and `-u 7000` for
the set), each fill, each burst, each heater launch and each sampler window. The `-k 3` kills a process that ignores
SIGTERM (stuck in an ioctl, say). A sampler that has to be killed is followed by a drain.

**Mid-pass aborts.** Every one ends in the restore:

| Event | What happens |
|---|---|
| A set or read-back fails; the on-die monitor is off by > 5%; the set times out (the firmware's endless retry, §2) | Restore, then `ALERT-NV-SET` and the host's STOP |
| The VMIN table changed after the first set | Restore, then `ALERT-NV-FLASH` and the host's STOP |
| A window shows `reg_mv.noc` ≠ the level, the on-die median off its expected value by > 10 mV, or `mhz.noc` ≠ 400 | Restore, then `ALERT-NV-STATE` and STOP |
| A burst's rail current over 35 A in three samples of one window (the phase is rated 40 A) | Restore; the pass fails, with no alert and no host STOP. A second such abort on the card sets NV's STOP. At 600 mV normal `wsep` peaks project to about 21–25 A (E42's `wsep` bursts: about 8 W at 485 mV on aifoundry2). E42's aifoundry1-c1 pass-6 spikes, 14.8 W for one or two samples at 485 mV, would project to about 38 A: one such spike does not trip the rule, and a trip costs only the pass. |
| A burst that `timeout` had to stop (rc 124 or 137): a kernel may still run | Up to three idle windows until the rail is back within 0.3 W of the segment's idle, then the restore; the pass fails, no alert |
| A window with a minion-shire mean ≥ 85 °C | Restore; the pass fails; a second on the card sets NV's STOP |
| A current reading ≥ 90 °C, or a watermark that rises to ≥ 90 °C during the block | Restore, then NV's STOP |
| The device layer names another card's node ("PCIe target") | Restore, then NV's STOP |
| A STOP file, another user's device process, a sampler that stays dead or overruns, or two configurations in a row that fail | Restore, then the block fails (exit 1, or 3 for another user) |
| A signal: HUP, INT, TERM, PIPE, USR1, USR2 or ALRM | The trap restores. All of them are ignored while the restore runs, and a second signal cannot re-enter it. |
| kill -9, the OOM killer, a crash | The guardian (below) restores |

**The restore.** It reads the rail and sets 485 until the rail is verified, up to 5 times, waiting 20 s whenever the
card does not answer. That covers the time a watchdog reset takes to bring the card back at its boot value. **Verified**
means all of these:

- a drain (`GET_MODULE_POWER`) first, if any earlier call in the block returned non-zero. Every `dev_mngt_service`
  process starts at tag 0 and matches replies by tag alone, so a late reply to a killed call could otherwise be read;
- two fresh module reads, 1 s apart, both reading 485;
- the on-die monitor within 5% of 485: an independent path, and 540 mV is 11% away.

If the restore cannot be verified, the block writes `ALERT-NV-RESTORE.json` in `build/claims-v3/`, in the NV directory
and in the pass. It also sets the host's `build/claims-v3/STOP`, which stops every queue on the host at its next
block. `block.json` then says `"restored": false`.

**The guardian.** Just before the first set, the block starts a restore guardian. It is a subshell that ignores every
catchable signal and holds the card lock's descriptor too. It polls the block's process (by PID and start time). If
the block dies without finishing and the state file is dirty, the guardian:

1. waits (up to 20 s) for the block's device processes to end;
2. runs the same verified restore, writing `ALERT-NV-RESTORE` if it cannot;
3. writes `block.json`;
4. exits, and only then is the card lock released.

The block's own finish stops the guardian after its restore. A `kill -9` of the whole process group would still defeat
it.

**Detached runs.** Every block, the probe and the smoke included, runs under `setsid nohup … > log 2>&1 < /dev/null`
(README). An ssh drop can then deliver no signal at all.

**A reset.** The uptime is read before the first set and again at the end of any block that made a set. If it went
back, the block writes `ALERT-NV-RESET`. The alert says that a reset clears et-board-clock-guard's TDP 0 and 600 MHz
pin on aifoundry3, so the lab admin must re-run the clock guard before anyone measures on that card. The rail itself
comes back at its boot value, which on BL2 ≥ 0.19 is the flash's 485 mV.

**The state file.** `build/claims-v3/<card>/nv/NV-STATE.json` turns "dirty" before every set and "clean" only when a
restore is verified.

## 8. Plan

1. **Fix the predictions.** Run `freeze.sh --predictions`, commit `predictions.json` and `PREDICTIONS.sha256`, and
   record the SHA-256 in `docs/findings/03-experiments.md`. This comes before any card write, and every real block
   refuses until it is done.
2. **Tell the lab admin** before the first write: the probe may reset the card (§2, the endless retry), and a reset
   loses aifoundry3's clock guard.
3. **Read-only probes** (the main session runs them, `README.md` §1): the firmware and BL2, the uptime, the rail at
   485, the VMIN table's boot value, an idle baseline, and the SP trace's boot line, on aifoundry3. On aifoundry2 the
   same probes run after DV2 ends.
4. **Development on aifoundry3:**
   - `block.sh 1 --probe`, detached: the first write. 540 mV, then 600 mV, with idle windows, then the restore.
   - Then read the SP trace for "Unable to validate", and the probe's steps.
   - `block.sh 1 --smoke`, detached: 485 and 600 mV with two configurations each.
   - `run-queue.sh` runs passes 1–6.
   - `reduce.py --card aifoundry3` gives the development results.
   - Change timing, limits, heater or drop thresholds here only (never `predictions.json`), and rerun development
     passes after any change.
5. **Freeze** (after DV2's validation on aifoundry2 has ended and the owner has released the card):
   - Complete `PREREG.md` (every TBD) and `prereg.json`: nD, sdD and nDev from development; tol; and val_passes = N,
     the rule's.
   - `freeze.sh --binaries <aifoundry2's hashes>`.
   - Commit, recording the PREREG hash in `docs/findings/03-experiments.md`.
   - Run `freeze.sh --check` on aifoundry2.
6. **Validation on aifoundry2:**
   - A person writes `build/claims-v3/aifoundry2/nv/CARD-RELEASED`.
   - The read-only probes (step 3).
   - `block.sh 101 --probe`: the steps only. It records no power, so nothing registered is seen before the freeze. It
     applies the windows' exact on-die rule, so a card the passes would reject is found here.
   - `run-queue.sh` runs passes 101 to 100 + N and the spares.
   - `reduce.py --card aifoundry2 --dev-ref tools/claims-v3/nv/prereg.json` gives the summary.

## 9. Risks

- **The firmware's endless retry** (§2; read from source, not tested). A regulator write or read-back that fails, or an
  out-of-range value, loops until the 10 s watchdog resets the SoC. The whitelist keeps every code in range, and
  `dev_mngt_service` returns after `timeout 10`.
  - After a reset the card comes back at its boot value (485 mV from the flash on BL2 ≥ 0.19). NV restores, verifies
    and raises `ALERT-NV-SET` and `ALERT-NV-RESET`.
  - A reset changes other users' conditions: on aifoundry3 it clears et-board-clock-guard's TDP 0 and 600 MHz pin.
    The lab admin is told before the probe and after any reset.
  - Whether the card comes back unaided is not known; a card that does not answer is the lab admin's.
  - The boot line `Overriding NOC -> … (0x2F)` in the SP trace would show that the read-back returns the bare code.
    The trace buffer is 8 KB and wraps within minutes of management traffic, so the line is visible only shortly
    after a boot. The probe's 540-first step is the check otherwise.
- **aifoundry2's heater.** On 28 September a heater launch 0.6 s after the previous one coincided with a Master Minion
  hang there (`14-card-behaviour.md`). The cause is not established. NV spaces heater launches by ≥ 2 s and never
  launches while another kernel runs.
- **A kill -9 of the whole process group**, a host crash or a power loss mid-pass leaves the rail at 540 or 600 mV
  until the next reset or boot. On BL2 ≥ 0.19 the boot value stays 485 mV, since the flash is not written. The state
  file makes the next NV block refuse and alert.
- **The rail's power reading at a new voltage** is now a registered control (C-METER, §5), not an assumption.
- **aifoundry2 runs hot.** E42 there ran at a 72–90 °C mean with the heater. At 600 mV the mesh adds about 2–4 W.
  - A window with a mean ≥ 85 °C fails its pass, and a second such window stops NV on the card.
  - If that happens in the validation, heat_c (76) may be lowered in development. The governor needs only ≥ 69 °C.

## 10. The reviews (28 September) and what changed

**R1 (safety).**

| Finding | What changed |
|---|---|
| B1: BL2 0.18.0 writes every NoC set to flash | Hard-coded BL2 ≥ 0.19.0 refusal in `nv_set`, plus nv.json `min_bl2`; aifoundry1's card 1 refused; validation moved to aifoundry2; the VMIN table read before, after the first set and at the end (`ALERT-NV-FLASH`) |
| B2: `dev_mngt_service` opens card 0 on aifoundry1 | NV runs only on single-card hosts; the multi-card lock code is removed |
| M1: one "485" read taken as the restore | The verified restore: a drain after any failed call, two reads 1 s apart, and the on-die monitor |
| M2: kill -9 leaves the rail stepped and frees the lock | The guardian |
| M3: a second HUP kills the restore | Every catchable signal trapped; ignored in `finish`, with a re-entry guard; every block detached with `setsid nohup` |
| M4: `queue.sh` samples the card without the lock | NV's own `run-queue.sh`, which opens no device |
| M5: a reset is not handled | The uptime before and after (`ALERT-NV-RESET`, the clock guard named); the range-check wording corrected; the lab admin told before the probe |
| L1–L4 | `timeout -k 3 10` everywhere; L2 moot (no other locks); the PCIe target checked; a burst stopped by `timeout` waits for an idle rail before the restore's set |

**R2 (science).**

| Finding | What changed |
|---|---|
| 1: the meter's formula is unchecked | C-METER, gating NV-D, NV-Z and NV-I |
| 2: the NoC clock check is a register | C-BW |
| 3: NV-I and temperature | I_tc with the E44 coefficient (0.028/°C; the review's 1/29–1/34 used a slope at ~62 °C over the level at 57 °C); TH-LEAK's band [1.0, 3.5]; the 1.25 split descriptive; the end-window drift |
| 4: predictions not fixed | `predictions.json` and `PREDICTIONS.sha256`, checked by every real block and by the freeze |
| 5: the sample size overstated | The Monte Carlo (§6) and the pass-count rule |
| 6: the on-die tolerance | Relative to the pass's own 485 mV reading; the validation probe applies the windows' rule |
| 7: spares break the balance | A spare takes the earliest failed pass's order |
| 8: the self-test checks only plumbing | A realistic synthetic model, meter, bandwidth, temperature and spare scenarios, and `--monte-carlo` |
| 9–14 | Burst heating reported and stated (§3); common hops per pass; Q ≤ 0 invalidates a pass; R1 by a Welch interval; the Q63 line gated and labelled; the short-circuit wording |
| 15: current headroom | A current abort drops the pass and restores, with no host STOP; a repeat stops NV on the card |

**Found while fixing them.** The "High" temperatures are latched watermarks (§4). The old "every reading < 90 °C" rule
would have refused or aborted every aifoundry2 pass, since E42 read a latched 93–106 °C there.
