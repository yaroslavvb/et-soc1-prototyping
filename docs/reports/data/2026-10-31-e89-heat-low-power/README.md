# E89 — heat below 12 W of switching, measured on the die's 34 sensors one by one (Q130, aifoundry3, 2026-10-31)

*Pre-registered in [`tools/claims-v3/e89/E89.md`](../../../../tools/claims-v3/e89/E89.md) with
[`predictions-e89.json`](../../../../tools/claims-v3/e89/predictions-e89.json), committed as **`850421ec`** and pushed at
**18:58:18 PDT**, 39 s before the card was claimed in `#community-lab` (18:58:57 PDT, message `1566270291833790485`)
and 50 s before the first device access (a read-only `ettelem config`, 18:59:08). Amendments A1 and A2 (plumbing:
raw sensor codes, the sampler's reply matching) were committed as **`ac95a217`** at **19:03:20**, after the probe and
the smoke and before the measured passes. Card runs **18:59:08–19:42:12 PDT** on **aifoundry3 card 0 only**: the
probe, the smoke (18:59:51–19:00:36), a 3 s sampler check (19:02:49), passes **8910** (19:03:29–19:22:39) and
**8911** (19:22:40–19:41:50), and a closing read-only `ettelem config`. 600 MHz, 521–523 mV throughout, pinned by
the card's boot-time TDP 0; nothing was set, and no statistics reset was sent. **Released at 19:42:31 PDT** by an edit
of the same post, read back as `<ai> Claude says: using aifoundry3 for 1 h, until ~20:00 PDT doc — released
(edited)`: the claim was held 43.6 minutes, inside the 45 budgeted.*

*Corrected after verification, Sat 31 Oct 2026, at the desk, with no card touched and nothing re-run (§ [Corrections
after verification](#corrections-after-verification), C1–C9): E89 measured six of E78's 16 int8 kinds, not every one,
so Horace hub Status item 7 is narrowed, not closed; its 2 s rises are over each type's zeros, where E78's heat cells
are over idle, and result 2 now gives derived over-idle values beside them; the per-minion-rail result is post hoc; the
camera side-by-side is dropped; and the pass-level verdicts (23 PASS, 1 INCONCLUSIVE), the trend model's effect on the
intervals, the 2 s step's dependence on the cycle and the second idle bracket are stated. No number in `e89.json`,
`scored.json`, `results.md`, `tables.txt` or `posthoc.txt` changed, no registered verdict changed, and no frozen input
changed.*

> **What this is.** E78's heat column resolved only the 19 kinds above about 12 W of switching power; the other 32,
> every int8 kind among them, were extrapolated as *S × 0.118 °C/W*, and the thermal camera had not detected int8
> (E85). E89 reads the die's 34 minion-shire temperature sensors one by one, as raw 12-bit codes (0.061 °C a code;
> the governor sees only their whole-degree mean), and switches seven of those 32 kinds (six of E78's 16 int8 kinds and
> fp32 ones) each against its own type's zeros (int8 zeros against idle) as a 60 s square wave, beside fp32 random data
> as the resolved reference. Two passes, four laps a kind, every number below with a 95% interval; the registered
> intervals take the lap as the unit, and the pass-level verdicts are in § The tables.

## Results

**All 16 blocks passed every gate and all 24 registered verdicts PASS (0 fail, 0 inconclusive)**
([`scored.json`](scored.json) `tally`; [`tables.txt`](tables.txt) T5, T7), as registered, with the lap as the unit;
with the pass as the unit, 23 PASS and 1 INCONCLUSIVE (E89-R4 for int8 −1; § The tables, D7). 22,976 samples at
10 Hz carry all 34 sensors (100%), and the firmware's integer mean rebuilt from the 34 codes with the firmware's own
integer arithmetic equals the `minshire_avg` it reports in **98.1%** of them (`e89.json` `instrument`; E89-R0 PASS):
these are the governor's sensors, read before the firmware truncates them.

**1. Heat follows switching power below 12 W: each of the seven kinds lies inside the registered band, 4–11% above
the reference per board watt.** Each kind against its own zeros at 1/60 Hz, H = the die's temperature fundamental
over the board's power fundamental ([`e89.json`](e89.json) `blocks.<block>.H_proj_ref_phase`, `.r_H`;
[`tables.txt`](tables.txt) T1):

| kind (against) | E78 switching power | temperature fundamental at 1/60 Hz, amplitude (°C) | H (°C per board W) | r = H / H_fp32-random [95%] | per minion-rail W, r (post hoc) |
|---|---|---|---|---|---|
| int8 full, random (int8 zeros) | D 7.056 W | 0.899 ± 0.026 | 0.2077 ± 0.0042 | **1.050** [1.019, 1.080] | 0.992 [0.979, 1.005] |
| int8 gauss_q (int8 zeros) | D 6.598 W | 0.837 ± 0.015 | 0.2060 ± 0.0092 | **1.041** [0.989, 1.092] | 0.988 [0.963, 1.012] |
| int8 smallint (int8 zeros) | D 6.003 W | 0.776 ± 0.021 | 0.2095 ± 0.0069 | **1.059** [1.017, 1.100] | 1.002 [0.997, 1.008] |
| int8 sparse50 (int8 zeros) | D 5.463 W | 0.718 ± 0.024 | 0.2107 ± 0.0028 | **1.065** [1.038, 1.091] | 1.008 [0.984, 1.033] |
| int8 neg_ones, −1 (int8 zeros) | D 1.628 W | 0.232 ± 0.011 | 0.2064 ± 0.0147 | **1.043** [0.965, 1.120] | 0.980 [0.963, 0.996] |
| int8 zeros (idle) | S 2.605 W | 0.360 ± 0.008 | 0.2202 ± 0.0082 | **1.113** [1.065, 1.160] | 0.991 [0.958, 1.024] |
| fp32 ones, 1.0 (fp32 zeros) | D 8.257 W | 1.071 ± 0.023 | 0.2104 ± 0.0046 | **1.063** [1.031, 1.095] | 1.003 [0.987, 1.018] |
| **fp32 randn, the reference** (fp32 zeros) | D 24.725 W | 3.032 ± 0.056 | **0.1979 ± 0.0041** | 1 | 1 |

Every low-power r lies inside the registered [0.80, 1.25] at 95% (E89-R2 PASS ×7), and the reference's 0.1979 °C/W sits
inside the heat model's band (predicted 0.188; E89-R3 PASS). Measured per board watt, the low-power kinds heat the
die **4–11% more than fp32 random data**. Five of the seven intervals exclude 1 under the registered model (the lap as
the unit, a quadratic trend); with the pass as the unit three do, and with a linear or a cubic trend none do, though
every point estimate stays above 1 (1.02–1.12; § The tables, C5). **Post hoc and descriptive, the difference tracks
where the board's watts go.** Per watt of the minion rail (the SP's running average, the same fit), all eight kinds
give 0.239–0.246 °C/W and r = 0.980–1.008; int8 −1's 0.980 [0.963, 0.996] still excludes 1, and these intervals take
the reference as a fixed number. The minion rail carries 0.856–0.864 of the board's swing for the int8 kinds and fp32
ones, 0.912 for int8 zeros against idle, and only 0.812 for fp32 random data ([`posthoc.txt`](posthoc.txt), POST HOC 2),
which matches E78's rail-to-board ratios of 0.800–0.865 (E78 README, Registered against what happened). The SRAM and
NoC rails carry 0.022–0.026 of the swing; the rest (0.164 for fp32 random data, 0.111–0.122 for the int8 kinds and
fp32 ones, 0.062 for int8 zeros) is outside the metered rails, most likely regulator loss, which E89 did not measure
(C8). In short: per board watt, every kind measured is inside the registered band and 4–11% above fp32 random data;
post hoc, per watt of the minion rail, within about 2% of it.

**2. E78's 2 s window, measured on seven of the kinds it could not resolve.** The die's rise over each kind's own
reference (its type's zeros; idle for int8 zeros) in E78's own 2 s window ([t0 + 1, t0 + 3) s after the switch), read
on the 34-sensor mean ([`tables.txt`](tables.txt) T2, `step2_C`). E78's heat cells are rises over idle (ΔT from the
58 °C launch reading, 0.118 °C per W of S), so the last two columns put each rise on that footing, derived
([`corrections-check.txt`](corrections-check.txt) [C2]):

| kind | measured over | 2 s rise, measured (°C) | E78's 0.118 °C/W × this step's watts (°C) | 2 s rise per E78 W (°C/W) | 2 s rise over idle, derived (°C) | E78's over-idle extrapolation, S × 0.118 (°C) |
|---|---|---|---|---|---|---|
| int8 full | int8 zeros | **0.863 ± 0.073** | 0.833 (D) | 0.122 ± 0.010 | 1.20 ± 0.07 | 1.14 |
| int8 gauss_q | int8 zeros | **0.820 ± 0.151** | 0.779 (D) | 0.124 ± 0.023 | 1.16 ± 0.15 | 1.08 |
| int8 smallint | int8 zeros | **0.725 ± 0.073** | 0.708 (D) | 0.121 ± 0.012 | 1.06 ± 0.07 | 1.02 |
| int8 sparse50 | int8 zeros | **0.673 ± 0.078** | 0.645 (D) | 0.123 ± 0.014 | 1.01 ± 0.08 | 0.95 |
| int8 neg_ones | int8 zeros | **0.222 ± 0.026** | 0.192 (D) | 0.136 ± 0.016 | 0.56 ± 0.03 | 0.49 |
| int8 zeros | idle | **0.340 ± 0.006** | 0.307 (S) | 0.130 ± 0.002 | 0.340 ± 0.006 (measured) | 0.31 |
| fp32 ones | fp32 zeros | **1.059 ± 0.164** | 0.974 (D) | 0.128 ± 0.020 | 1.29–1.32 | 1.21 |
| fp32 randn (reference) | fp32 zeros | 2.920 ± 0.194 | 2.918 (D) | **0.118 ± 0.008** | 3.15–3.18 | 3.15 (E78 measured 3.16 ± 0.08) |

*Derived over idle:* an int8 kind's rise over int8 zeros plus int8 zeros' rise over idle, assuming 2 s responses add
(± the two intervals in quadrature); a fp32 kind's rise over fp32 zeros plus fp32 zeros' rise over idle, which E89 did
not measure, taken as E78's S for fp32 zeros (1.986 W) × 0.118–0.130 °C/W (the reference's and int8 zeros' measured
2 s coefficients). The reference's derived 3.15–3.18 °C matches E78's measured 3.16 ± 0.08 °C.

The fine reading agrees with E78's resolved coefficient on the reference within about 4% (0.1181 against 0.118 °C/W:
0.1138 from the steps after the 20 s lead-in, 0.1224 from those after a 30 s reference half; C6). The low-power kinds
come out 0.121–0.136 °C/W, 2–15% above it, every ratio inside the registered [0.70, 1.43] (E89-R4 PASS ×7; with the
pass as the unit, int8 −1's is INCONCLUSIVE, C5). So each kind's own step is 2–15% larger than E78's coefficient
predicts for it; against the over-idle cells E78 published (*S × 0.118*), the derived over-idle rises come out
4.5–14% higher. **At 600 MHz, in 2 s, random int8 warms the die about 0.86 °C over int8 zeros and int8 −1 about
0.22 °C over int8 zeros; int8's zeros warm it about 0.34 °C over an idle card. Over idle, random int8 comes to about
1.20 °C (derived).** Each 2 s rise also depends on what came before it: in seven of the eight blocks, in both passes,
the step after a 30 s reference half is 7–21% larger than the step after the lead-in, so a different protocol could
move a rise by about ±10% beyond its quoted interval (C6). Over a 30 s half the die rises 1.89 ± 0.11 °C
over int8 zeros on random int8 and 6.22 ± 0.04 °C over fp32 zeros on random fp32 (0.268 and 0.252 °C per E78 W; T2
`swing30`). None of this is a steady state (§ Joins and traps).

**3. The finest reading the card offers, with nothing set.** On this firmware build, command 74 group 0 returns each
sensor's raw 12-bit code (amendment A1), converted here with the firmware's own formula (one set of constants for
every sensor, no per-sensor calibration). At idle (pass 8910's bracket, a steady 51 °C card), each sensor's code had an
SD of **0.52 codes** (0.032 °C; 3 distinct codes a sensor) and the 34-sensor mean an SD of **0.0076 °C**, against a
step of 0.0018 °C ([`posthoc.txt`](posthoc.txt)). Pass 8911's bracket is not a noise figure: it began 13.8 s after
8910's last block (fp32 random data) ended, and the die cooled 0.79 °C over its 15 s, so its raw SD is 0.23 °C; about a
straight line it is 0.0081 °C, with 0.53 codes a sensor, as quiet as 8910's (0.0050 °C and 0.52 codes about a line;
C7). So the sensors are quiet: time-averaging one sensor dithers by about one code, and averaging the 34 sensors gives
the rest. On the firmware's whole-degree mean (E78's reading), the same laps resolve the strong kinds but not int8 −1
(0.347 ± 0.418 °C) or int8 zeros (0.411 ± 0.207 °C) (T2). The firmware's reported die temperature runs **about 1 °C
below the mean of the same sensors' readings** (median 0.96 and 1.04 °C in the two passes), because the firmware
truncates twice: each sensor to a whole degree, then the mean. Neither is a calibrated die temperature.

**4. With every shire loaded alike, every kind gives the same per-sensor pattern.** Each sensor's own H forms a
pattern across the die (0.153–0.227 °C/W on fp32 random data, sensor 0 coolest, sensor 30 warmest). The pattern of
every other kind correlates **0.996–1.000** with the reference's (T4). Every launch ran on all 32 shires and 1,024
minions (shire mask 0xffffffff in all 4,306 launch records; C8), so the pattern is set by the die's geometry by
design: E89 cannot say whether a kind run on part of the die would put its heat elsewhere.

**5. Speed.** As in E78, no kind changed the work per cycle: all 4,024 kernel records from the 282 launches ran at
546.0 (fp32) or 318.0 (int8) cycles per op (T7).

## What it changes

- **For the blog's kinds table, the heat column.** Seven of the 32 cells E78 extrapolated now rest on a measurement:
  six of E78's 16 int8 kinds (full, gauss_q, smallint, sparse50, −1 and zeros, the last against idle) and fp32 ones.
  Per board watt they heat the die 1.04–1.11 times as much as fp32 random data, inside the registered [0.80, 1.25]
  (E89-R2 PASS ×7); post hoc, per watt of the minion rail, 0.98–1.01 times. E78's coefficient (0.118 °C per W in a
  2 s window), applied to each kind's own step, holds to +2…+15% (E89-R4 PASS ×7); against E78's over-idle cells
  (*S × 0.118*), the derived over-idle rises come out 4.5–14% higher. The cells to quote, at 600 MHz on aifoundry3, each
  a 2 s rise: random int8 **0.86 ± 0.07 °C over int8 zeros** (about 1.20 ± 0.07 °C over idle, derived); int8 −1
  **0.22 ± 0.03 °C over int8 zeros** (about 0.56 ± 0.03 °C over idle, derived); int8 zeros **0.34 ± 0.01 °C over
  idle**; fp32 ones **1.06 ± 0.16 °C over fp32 zeros** (about 1.3 °C over idle, derived). Each carries a protocol
  dependence of up to about ±10% beyond its interval (C6). Beside them, random int8's temperature fundamental at
  1/60 Hz has an amplitude of 0.90 ± 0.03 °C. Still *S × 0.118* extrapolations, now backed by a coefficient measured on
  six int8 kinds and one float constant: the other ten int8 kinds (ones, sparse90, ternary, highbit, sorted, pos,
  wsparse50, wsparse90, a_full_b_zeros, a_zeros_b_full) and fifteen float kinds (fp32 π, −1.0, sparse50, sparse90,
  zeros and its two one-sided kinds; fp16 1.0, −1.0, sparse90, wsparse50, wsparse90, zeros and its two one-sided
  kinds). On E89's six int8 kinds the 2 s coefficient is 0.121–0.136 °C/W, which would put the ten unmeasured int8
  kinds 2–15% above their *S × 0.118* values (C1).
- **Horace hub, Status item 7 ("heat below ~12 W of switching, every int8 kind")** is narrowed, not closed: six of
  E78's 16 int8 kinds and one float constant are measured, and the other ten int8 kinds and fifteen float kinds stay
  extrapolations. The die's sensors detect every kind E89 ran (E89-R1 PASS ×8, also with the pass as the unit). E85's
  camera did not detect int8, but under other conditions (aifoundry2, 192 minions at 800 MHz, a 2.45 W step at
  0.05 Hz, the back of the board seen by a camera), so its 64.5 ± 28.3 mK and E89's 0.90 °C amplitude are not
  comparable (C4).
- **E78's correction C1** ("a measured heat cell for those 32 kinds needs a card run … a finer reading"): done for
  seven of them.
- **For the instrument.** The governor's 34 sensors can be read one by one on aifoundry3, 0.061 °C a code, at 10 Hz,
  with nothing set: `tools/claims-v3/e89/pvt_sample.py`. It replaces `ettelem sample` wherever die temperature
  matters, on this firmware.

## The tables

Full tables, printed from `e89.json` by [`tables_e89.py`](tables_e89.py): [`tables.txt`](tables.txt) (T1 the lock-in,
T2 the 2 s step, the 30 s swing and the whole-degree reading, T3 per pass, T4 per sensor, T5 the verdicts, T6 the
instrument, T7 the gates). The registered intervals use the lap as the unit (4 laps a kind, t(0.975, 3)), as E85 did;
with the pass as the unit (E78's convention, n = 2, t(0.975, 1) = 12.706) the two passes agree to within 0.0002–0.0057
°C/W on every block:

| block | H pass 8910 (°C/W) | H pass 8911 (°C/W) | mean ± 95% over the two passes |
|---|---|---|---|
| int8 full | 0.2083 | 0.2071 | 0.2077 ± 0.0078 |
| int8 gauss_q | 0.2085 | 0.2034 | 0.2060 ± 0.0328 |
| int8 smallint | 0.2073 | 0.2117 | 0.2095 ± 0.0281 |
| int8 sparse50 | 0.2108 | 0.2106 | 0.2107 ± 0.0012 |
| int8 neg_ones | 0.2035 | 0.2092 | 0.2064 ± 0.0364 |
| int8 zeros (over idle) | 0.2198 | 0.2206 | 0.2202 ± 0.0052 |
| fp32 ones | 0.2113 | 0.2094 | 0.2104 ± 0.0122 |
| fp32 randn (reference) | 0.1976 | 0.1982 | 0.1979 ± 0.0037 |

Scored with the pass as the unit, the brief's unit of replication (D7), **23 rules pass and 1 is inconclusive**:
E89-R4 for int8 −1, 1.153 [0.380, 1.925]. R0, R1 ×8, R2 ×7 (the widest, int8 −1's, [0.858, 1.228]; three of the
seven exclude 1), R3 and R4's other six pass ([`corrections-check.txt`](corrections-check.txt) [C5]). The r intervals
also rest on the registered quadratic trend: re-run with a linear or a cubic trend and nothing else changed, r stays
1.015–1.117, but the intervals widen 1.8–6.3×, none of the seven excludes 1, and int8 zeros' R2 would read
INCONCLUSIVE ([0.784, 1.341] linear, [0.937, 1.297] cubic) [C5].

The per-block die mean ran 55.9–58.4 °C on the low-power blocks and 62.7 °C on the reference (post hoc, `posthoc.txt`);
the die read 52.4–68.1 °C over both passes (the 34-sensor mean), board power 23.3–56.4 W.

## Registered against what happened

| registered ([`E89.md`](../../../../tools/claims-v3/e89/E89.md), [`predictions-e89.json`](../../../../tools/claims-v3/e89/predictions-e89.json)) | happened |
|---|---|
| registration, predictions, code and desk checks on origin/main before the claim and any device access | `850421ec`, pushed 18:58:18 PDT; claim 18:58:57; first device-opening command 18:59:08 |
| the harness copied into the aifoundry3 binaries tree (`~/aifoundry`) | rsync 18:56 and again after each commit; every harness file's sha256 on the box at the start of the queue is in [`logs/box-harness.sha256`](logs/box-harness.sha256) |
| `run_e89.sh setup`, opening no device node | 18:56:26–18:56:32: lib.sh identical to E78's freeze (`033d0776…`), 51 tiles verified, the binary's four strings present, numpy 1.26.4, `dry rc=0`, 37 device launches printed in the dry pass (one a non-idle half) ([`logs/e89-dry.log`](logs/e89-dry.log)) |
| the probe: three read-only sampler ticks, command 74 answers 34 sensors? | 18:59:08: one tick (the first tick took 1.0 s; A2), command 74 status 0 with 34 values, **raw codes** 1,928–1,969 (A1) ([`ident/probe.out`](ident/probe.out)) |
| the smoke: i8full, 10 s halves, one cycle | 18:59:51–19:00:36, block ok, cycles per op 318.0 on every record; telemetry at 1 Hz (A2); the firmware's integer mean rebuilt from the codes equals `minshire_avg` in 43 of 43 samples |
| passes 8910 and 8911 inside 42 queue-minutes and before 21:40 | queue 19:03:28 – 19:41:50; 8910 19:03:29–19:22:39 (19.2 min), 8911 19:22:40–19:41:50 (19.2 min) |
| the start gate (≤ 62 °C, ≤ 60 s) and a 15 s idle bracket | 8910 began at a 51 °C reading, 8911 at 59 °C: both gates passed at once |
| per-block gates (600 MHz, 515–530 mV, launches, cycles per op, ≥ 5 samples/s) | all 16 blocks passed: 600 MHz in every sample, 521–523 mV, 1,400 samples a block (10 Hz), 282 launches with no failure, every one of the 4,024 kernel records' cycles per op within 0.5% ([`tables.txt`](tables.txt) T7); no block dropped |
| every rule scored on the 34-sensor mean | 24 verdicts scored, 24 PASS with the lap as the unit (with the pass as the unit, 23 PASS and 1 INCONCLUSIVE, D7); the sampler never fell back to `ettelem` (command 74 answered in every one of the 22,976 samples) |
| nothing set; two read-only session `ettelem config` reads | 18:59:08 and 19:42:12: TDP 0, 65 °C, 600 MHz, 523 and 522 mV ([`ident/config_session_start.json`](ident/config_session_start.json), [`ident/config_session_end.json`](ident/config_session_end.json)); each pass also read it at its start and end (`config_start.json`, `config_end.json`) |

## Departures (dated)

- **D1 — the brief's design, not the registration's (decided 18:20–18:55, before the claim; E89.md "Design").** The
  brief asked for 3–5 minute sustained windows per kind from a die-temperature gate. E89 runs each kind as a 60 s
  square wave against its own zeros (2 cycles a block, 4 laps a kind over two passes), because on the lab's heat
  model no window inside 45 card-minutes reaches a steady state, a gated window's rise is dominated by the die's
  relaxation from its preheat, and a zeros/kind chain carries the previous segments' heat into the next
  ([`desk/`](../../../../tools/claims-v3/e89/desk/)). The idle bracket and the start gate of E78's frame are kept at the
  head of each pass. One float kind below 12 W (fp32 ones) is measured, not several.
- **D2 — amendments A1 and A2 (19:03, after the probe and the smoke, before the passes; `ac95a217`).** Raw codes
  instead of whole degrees, converted with the firmware's formula; the sampler matches replies on the tag. Neither
  changes a prediction, a rule or a band.
- **D3 — a 3 s sampler run outside the registered stages (19:02:49).** To check A2's fix, `pvt_sample.py` ran for 3 s
  under the card lock and `timeout 10` ([`ident/probe2.out`](ident/probe2.out)). Read only, like the probe.
- **D4 — card time, inside the budget (stated, not a departure).** The claim was held from 18:58:57 to 19:42:31
  (43.6 min) against the brief's 45 card-minutes; the first device access was at 18:59:08 and the last at 19:42:12,
  and the two passes took 38.4 min. The claim's own estimate ("for 1 h, until ~20:00 PDT") held.
- **D5 — device processes not under `timeout 10` (inherited from E78, its D4).** Every launch, the probe and every
  `ettelem config` read ran under `timeout 10`. lib.sh's `die_c` in `block_begin` and `block_end` runs
  `ettelem sample --seconds 1` under `timeout 20`, and the sampler runs for the whole pass by design, stopped by
  SIGTERM (lib.sh's `stop_sampler`).
- **D6 — idle logins (E78's D1).** Other lab users kept idle logins on aifoundry3 (12 `who` lines at 18:56); none held
  the card, a device node or the card lock (`et-who` empty at 18:56, 18:59, 19:03 and 19:42:12).
- **D7 — the lap, not the pass, as the unit of the registered intervals (decided at registration, `850421ec`, before
  the claim; named as a departure after verification).** The brief makes the independent pass the unit of
  replication. E89.md made the lap (two per pass) the unit, as E85 did, and reported the pass-level spread beside it.
  With the pass as the unit, 23 of the 24 rules pass and E89-R4 for int8 −1 is INCONCLUSIVE (§ The tables, C5).

## How it ran

On the Intel: origin/main contained `850421ec` and then `ac95a217`; `rsync -a --exclude __pycache__
tools/claims-v3/e89/ aifoundry3:aifoundry/tools/claims-v3/e89/` (`tools/claims-v3/kinds/` was already there from E78,
its tiles and `e78_common.py` unchanged). On aifoundry3, from `~/aifoundry`, each step in a script file run by
`ssh -o BatchMode=yes aifoundry3 'bash -s' < file`:

```bash
bash tools/claims-v3/e89/run_e89.sh setup        # 18:56:26, no device access
# 18:58:57  the #community-lab claim (one line)
flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null   # 18:59:08, read only
bash tools/claims-v3/e89/run_e89.sh probe        # 18:59:08, three sampler ticks under the lock
bash tools/claims-v3/e89/run_e89.sh smoke 8901   # 18:59:51-19:00:36
# 19:02:49  pvt_sample.py --seconds 3 under the lock (A2's check, D3); 19:03:20 ac95a217 pushed
bash tools/claims-v3/e89/run_e89.sh go 8910 2    # 19:03:28, detached; queue done 19:41:50
flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null   # 19:42:12, read only
```

Waits were bounded remote loops of at most 540 s, reading only the queue log and the run logs; nothing was reduced
before the queue ended. The raw passes, the smoke, the logs and the reads were copied to the Intel at the box's
relative layout (`aifoundry3/e89/p8910`, …) and the registered reducer ran there from the repository root:
`nice -n 10 python3 tools/claims-v3/e89/reduce_e89.py docs/reports/data/2026-10-31-e89-heat-low-power/aifoundry3/e89/p8910 docs/reports/data/2026-10-31-e89-heat-low-power/aifoundry3/e89/p8911 --out docs/reports/data/2026-10-31-e89-heat-low-power`.

## Joins and traps

- **The per-sensor codes are this firmware's.** Command 74 exists only on the thermal build flashed on 7 Oct, and
  its group 0 returned whole degrees then and raw codes now. Another card, or this one re-flashed, may answer
  differently or not at all; the sampler records whatever comes back, and A1's integer check (the firmware's own mean
  rebuilt from the codes) is the test that they are the governor's sensors.
- **Group 6 of command 74 resets the sensors' latches.** It is a write; `pvt_sample.py` refuses it.
- **H is per watt of the board's own fundamental at 1/60 Hz,** not a steady-state resistance. The steady rise per watt
  is larger (the heat model puts it at 1.47 °C/W, 2.07 with E78's leakage slope as feedback, with stages of 400 and
  2,500 s; `predictions-e89.json` `model.H_dc_C_per_W`), and nothing here measures it.
- **The 2 s step (step2) and the 30 s swing (swing30)** come from the same square waves; they are E78's window and a
  sustained window measured from the reference level (the type's zeros; idle for int8 zeros), not from an idle gate.
  Their per-watt numbers are comparable between kinds and with E78's coefficient; their absolute values are rises over
  the type's zeros, not E78's over-idle ΔT cells (result 2 gives derived over-idle values, C2). The step also depends
  on the half before it (C6).
- **Command 74 group 0 was sent after the probe showed its behaviour had changed** (raw codes, not the whole degrees
  of 7 Oct; the sampler's group map came from that build). It is a read: across both passes the sensors' 460 latch
  reads never moved backwards (highest code 2,543, 87.5 °C), the firmware's min/max holds stayed at 48 and 87 °C, and
  no sample carried a fault bit (C9).
- **int8 zeros is measured against idle (S); the other int8 kinds against int8 zeros (D).** Their r compares heat per
  watt across both.
- **E85's sampler sent a statistics reset once a second; E89's sends none** (no `--reset-ms`; the sampler has no such
  option).

## Corrections after verification

*Sat 31 Oct 2026, after the Q130 workflow's verifier checked this directory.* It re-ran the registered reducer on the
committed raw passes (`e89.json` and `scored.json` reproduce to about 1e-14), wrote an independent lock-in that
reproduces H, r, the minion-rail r and the rail shares, confirmed the timeline, the hashes and that nothing was set or
reset, and found four major and four minor faults in how the results were stated. Each is corrected in place above;
this list says what changed and why. No number in `e89.json`, `scored.json`, `results.md`, `tables.txt` or
`posthoc.txt` changed, no registered verdict changed, and no frozen input changed (their sha256 are in
[`manifest.json`](manifest.json) › `inputs_frozen`). Every figure below is printed from the committed files by
[`corrections-check.py`](corrections-check.py), whose output is [`corrections-check.txt`](corrections-check.txt) (its
section in brackets); it gives the same output on Python 3.9 with numpy 1.26 and Python 3.15 with numpy 2.5. The data
commit's subject (`1bef3fc0`, "every int8 kind …") stays as it is; C1 corrects it.

- **C1 (major) — six of E78's 16 int8 kinds, not every one.** The data commit's subject and the result handed on
  with it said "every int8 kind", § What it changes said "all six int8 kinds", and both closed Horace hub Status item 7
  for int8. E89 ran full, gauss_q, smallint, sparse50, −1 and zeros; ones, sparse90, ternary, highbit, sorted, pos,
  wsparse50, wsparse90, a_full_b_zeros and a_zeros_b_full were not run [C1]. Of E78's 32 kinds at or below 12 W of S,
  E89 measured 7; 25 stay *S × 0.118* extrapolations (10 int8, 15 fp32 and fp16), now resting on a coefficient
  measured on six int8 kinds and one float constant [C1]. Item 7 is narrowed, not closed.
- **C2 (major) — over the type's zeros, not over idle.** E89's 2 s rises are over each kind's own reference (its
  type's zeros; idle only for int8 zeros). E78's heat cells and its published extrapolations are over idle: ΔT from
  the 58 °C launch reading, 0.118 °C per W of S, "random int8 would warm about 1.1 °C" (E78 README, result 4). Result
  2's column "E78's extrapolation, D × 0.118" held numbers E78 never published (0.833, 0.192 and 0.974 °C for int8
  full, −1 and fp32 ones); it is now "E78's 0.118 °C/W × this step's watts", and two columns add E78's own
  *S × 0.118* and a derived rise over idle [C2]:
  - an int8 kind: its rise over int8 zeros plus int8 zeros' measured rise over idle, assuming 2 s responses add (±
    in quadrature): random int8 1.20 ± 0.07 °C against E78's 1.14, int8 −1 0.56 ± 0.03 °C against 0.49;
  - a fp32 kind: its rise over fp32 zeros plus fp32 zeros' rise over idle, which E89 did not measure, taken as E78's
    S (1.986 W) × 0.118–0.130 °C/W: fp32 ones 1.29–1.32 °C against 1.21; the reference 3.15–3.18 °C against E78's
    measured 3.16 ± 0.08 °C.

  On the seven low-power kinds the derived over-idle rises are 4.5–13.9% above *S × 0.118* [C2]. "E78's
  S × 0.118 °C/W … holds to +2…+15%" described the coefficient on each kind's own step (0.121–0.136 against
  0.118 °C/W, +2.3% to +15.3%); it now says so. Every 2 s rise in result 2 and § What it changes now names what it is
  over.
- **C3 (major) — the minion-rail result is post hoc.** The registered measure is per board watt: r = 1.041–1.113, five
  of the seven intervals excluding 1 (E89-R2). Per watt of the minion rail (r = 0.980–1.008) is post hoc and
  descriptive, with intervals that take the reference as a fixed number ([`posthoc.txt`](posthoc.txt), POST HOC 2), and
  even there int8 −1's 0.980 [0.963, 0.996] excludes 1 [C3]. Result 1 said "heat follows the die's own power exactly";
  it now leads with the registered result, labels the rail result post hoc and drops "exactly". The minion rail is
  not all of the die's power: the SRAM and NoC rails carry 0.022–0.026 of the board's swing [C8].
- **C4 (major) — the camera comparison was not like for like.** § What it changes set E89's 0.90 °C beside E85's
  64.5 ± 28.3 mK. They differ in card (aifoundry3 against aifoundry2), geometry and clock (1,024 minions at 600 MHz
  against 192 at 800 MHz), frequency (1/60 against 0.05 Hz, 3.00×), drive (a 4.33 W against a 1.53 W board
  fundamental, 2.82×) and what is measured (the on-die sensors against the back of the board seen by a camera) [C4].
  The side-by-side is dropped, and the differences are stated where E85 is named. 0.90 °C is the amplitude of the
  die's 1/60 Hz component, not a peak-to-peak swing; result 1's column is renamed.
- **C5 — the unit of replication, and the trend model.** The registration made the lap the unit (n = 4, t = 3.182);
  the brief makes the independent pass the unit. With the pass as the unit (n = 2, t = 12.706), 23 rules pass and 1 is
  inconclusive, E89-R4 for int8 −1 (1.153 [0.380, 1.925]); R2's widest interval is int8 −1's [0.858, 1.228], and three
  of the seven r intervals exclude 1 [C5]. It is named as departure D7. The tight r intervals also rest on the
  registered quadratic trend: with a linear or a cubic trend and nothing else changed, r is 1.015–1.117, the intervals
  widen 1.8–6.3×, none excludes 1, and int8 zeros' R2 would read INCONCLUSIVE [C5]. "Five of the seven intervals
  exclude 1" now carries that qualifier.
- **C6 — the 2 s step depends on the cycle.** In seven of the eight blocks, in both passes, the step after a 30 s
  reference half (cycle 1) is larger than the step after the 20 s lead-in (cycle 0), by 7–21%; int8 zeros against idle
  shows none [C6]. The reference's coefficient is 0.1138 °C/W from cycle 0 and 0.1224 from cycle 1, and 0.1181 is their
  mean: it agrees with E78's 0.118 within about 4% (−3.5% and +3.7%), not "exactly" [C6]. A likely cause is the
  straight-line baseline over-extrapolating the die's cooling after a hot half (not tested here). Every absolute 2 s
  rise carries a protocol dependence of this size beyond its interval.
- **C7 — the second idle bracket.** Result 3's noise figures come from pass 8910's bracket. Pass 8911's began 13.8 s
  after 8910's last block (fp32 random data) ended, and the die cooled 0.79 °C over its 15 s: its raw SD is 0.23 °C, and
  about a straight line 0.0081 °C (0.53 codes a sensor), as quiet as 8910's 0.0050 °C (0.52 codes) [C7]. Result 3 now
  says so.
- **C8 — wording, here and in the blog material handed on with this result.** (a) Result 3 called 0.0018 °C the
  34-sensor mean's resolution, and the blog material said it "resolves about 0.002 °C": that is its step; its noise at
  idle is 0.005–0.008 °C a sample [C7, C8]. (b) The blog material said the finer thermometer was "already on the
  chip": command 74 exists only on the thermal firmware build flashed on 7 Oct (§ Joins and traps), so the fine
  reading is that build's, not every card's. (c) The codes are converted with one formula for every sensor
  (G/H/CAL5 = 57400/249400/4096, no per-sensor calibration), so the firmware's die reading runs about 1 °C below the
  mean of the same sensors' readings, not below a "true" die temperature, as the blog material had it [C8]. (d)
  Result 4 said int8 and fp32 "differ in how much heat they make, not where they make it". Every launch ran on all 32
  shires (shire mask 0xffffffff in 4,306 of 4,306 launch records), so the per-sensor pattern cannot show where a kind
  puts its heat, only that with every shire loaded alike every kind gives the same pattern [C8]. (e) Result 1 said
  the per-board-watt difference "is where the board's watts go, not how heat flows", and the blog material that more
  of fp32 random's power "is lost before it reaches the die". Both are post hoc: the SRAM and NoC rails carry
  0.022–0.026 of the board's swing, and the swing outside the three metered rails is 0.164 for fp32 random data,
  0.111–0.122 for the int8 kinds and fp32 ones and 0.062 for int8 zeros, most likely regulator loss, which E89 did not
  measure [C8].
- **C9 — disclosed: command 74 group 0 after its behaviour changed.** The sampler's group map came from the 7 Oct
  build; the probe showed group 0 now returns raw codes, and the run kept sending it. It is a read: the sensors' 460
  latch reads never moved backwards (highest code 2,543, 87.5 °C), the firmware's min/max holds stayed at 48 and 87 °C,
  and no sample carried a fault bit [C9].

## Files

| file | what |
|---|---|
| `README.md` | this file |
| [`results.md`](results.md), [`scored.json`](scored.json), [`e89.json`](e89.json) | `reduce_e89.py`: every block, lap, step and swing; the rules and verdicts |
| [`tables_e89.py`](tables_e89.py), [`tables.txt`](tables.txt) | the README's tables, printed from `e89.json` (it changes nothing) |
| [`posthoc_e89.py`](posthoc_e89.py), [`posthoc.txt`](posthoc.txt) | post hoc and descriptive: per-sensor noise at idle, ranges, the firmware's truncation |
| [`corrections-check.py`](corrections-check.py), [`corrections-check.txt`](corrections-check.txt) | every number in § Corrections after verification, printed from the committed files; it re-runs the registered reducer with only its trend order changed, into a temporary directory, and changes nothing |
| [`manifest.json`](manifest.json) | every file's sha256, the registration commits, the claim |
| `ident/` | the session `ettelem config` reads, the probe and the 3 s re-run, the box's `et-lab-manifest` |
| `logs/` | the queue log, the setup's dry-run log, the harness hashes on the box |
| `aifoundry3/e89/p8910`, `p8911`, `aifoundry3/e89-smoke/p8901` | raw: `telemetry.jsonl.gz` (10 Hz, with the 34 codes), `runs.jsonl` (host launch records), `marks.jsonl` (gate, idle, blocks, halves, launches), `run.log`, `configs.json`, `config_start/end.json`, `block.json`, `sampler.json`, `manifest.txt`, `code.sha256`, `gen.sha256`, `tiles/` (every tile the host dumped) |
