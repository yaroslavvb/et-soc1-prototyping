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

> **What this is.** E78's heat column resolved only the 19 kinds above about 12 W of switching power; every int8 kind
> and the low-power float kinds were extrapolated as *S × 0.118 °C/W*, and the thermal camera had not detected int8
> (E85). E89 reads the die's 34 minion-shire temperature sensors one by one, as raw 12-bit codes (0.061 °C a code;
> the governor sees only their whole-degree mean), and switches each low-power kind against its own type's zeros as a
> 60 s square wave, beside fp32 random data as the resolved reference. Two passes, four laps a kind, every number
> below with a 95% interval.

## Results

**All 16 blocks passed every gate and all 24 registered verdicts PASS (0 fail, 0 inconclusive)**
([`scored.json`](scored.json) `tally`; [`tables.txt`](tables.txt) T5, T7). 22,976 samples at 10 Hz carry all 34
sensors (100%), and the firmware's integer mean rebuilt from the 34 codes with the firmware's own integer arithmetic
equals the `minshire_avg` it reports in **98.1%** of them (`e89.json` `instrument`; E89-R0 PASS): these are the
governor's sensors, read before the firmware truncates them.

**1. Heat follows switching power below 12 W, with one coefficient for every kind.** Each kind against its own
zeros at 1/60 Hz, H = the die's temperature fundamental over the board's power fundamental
([`e89.json`](e89.json) `blocks.<block>.H_proj_ref_phase`, `.r_H`; [`tables.txt`](tables.txt) T1):

| kind (against) | E78 switching power | die swing at 1/60 Hz (°C) | H (°C per board W) | r = H / H_fp32-random [95%] | per minion-rail W, r (post hoc) |
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
die **4–11% more than fp32 random data**, and five of the seven intervals exclude 1. **Post hoc, that difference is
where the board's watts go, not how heat flows.** Per watt of the minion rail (the SP's running average, the same fit),
all eight kinds give 0.239–0.246 °C/W and r = 0.980–1.008. The minion rail carries 0.856–0.864 of the board's swing
for the int8 kinds and fp32 ones, 0.912 for int8 zeros against idle, and only 0.812 for fp32 random data
([`posthoc.txt`](posthoc.txt), POST HOC 2), which matches E78's rail-to-board ratios of 0.800–0.865 (E78 README,
Registered against what happened). In short, heat follows the die's own power exactly, and the board's power to within
11%, the spread of each kind's rail share.

**2. The heat cells E78 could not resolve, measured.** The die's rise over its type's zeros in E78's own 2 s window
([t0 + 1, t0 + 3) s after the switch), read on the 34-sensor mean ([`tables.txt`](tables.txt) T2, `step2_C`):

| kind | 2 s rise, measured (°C) | E78's extrapolation, D × 0.118 °C/W (°C) | 2 s rise per E78 W (°C/W) |
|---|---|---|---|
| int8 full | **0.863 ± 0.073** | 0.833 | 0.122 ± 0.010 |
| int8 gauss_q | **0.820 ± 0.151** | 0.779 | 0.124 ± 0.023 |
| int8 smallint | **0.725 ± 0.073** | 0.708 | 0.121 ± 0.012 |
| int8 sparse50 | **0.673 ± 0.078** | 0.645 | 0.123 ± 0.014 |
| int8 neg_ones | **0.222 ± 0.026** | 0.192 | 0.136 ± 0.016 |
| int8 zeros, over idle | **0.340 ± 0.006** | 0.307 (S × 0.118) | 0.130 ± 0.002 |
| fp32 ones | **1.059 ± 0.164** | 0.974 | 0.128 ± 0.020 |
| fp32 randn (reference) | 2.920 ± 0.194 | 2.918 | **0.118 ± 0.008** |

The fine reading reproduces E78's resolved coefficient on the reference exactly (0.1181 against 0.118 °C/W), and the
low-power kinds come out 0.121–0.136 °C/W, 2–15% above it, every ratio inside the registered [0.70, 1.43] (E89-R4 PASS
×7). So E78's extrapolation was right to within the rail-share spread of result 1: **random int8 warms the die about
0.86 °C in 2 s at 600 MHz, int8 −1 about 0.22 °C, int8's zeros about 0.34 °C over an idle card.** Over a 30 s half the
die swings 1.89 ± 0.11 °C on random int8 and 6.22 ± 0.04 °C on random fp32 (0.268 and 0.252 °C per E78 W; T2
`swing30`). None of this is a steady state (§ Joins and traps).

**3. The finest reading the card offers, with nothing set.** On this firmware, command 74 group 0 returns each
sensor's raw 12-bit code (amendment A1). At idle (pass 8910's bracket, a steady 51 °C card), each sensor's code had an
SD of **0.52 codes** (0.032 °C; 3 distinct codes a sensor) and the 34-sensor mean an SD of **0.0076 °C**, against a
resolution of 0.0018 °C ([`posthoc.txt`](posthoc.txt)). So the sensors are quiet: time-averaging one sensor dithers
by about one code, and averaging the 34 sensors gives the rest. On the firmware's whole-degree mean (E78's reading),
the same laps resolve the strong kinds but not int8 −1 (0.347 ± 0.418 °C) or int8 zeros (0.411 ± 0.207 °C) (T2). The
firmware's reported die temperature runs **about 1 °C below the sensors' mean** (median 0.96 and 1.04 °C in the two
passes), because the firmware truncates twice: each sensor to a whole degree, then the mean.

**4. The heat lands in the same places for every kind.** Each sensor's own H forms a pattern across the die
(0.153–0.227 °C/W on fp32 random data, sensor 0 coolest, sensor 30 warmest). The pattern of every other kind correlates
**0.996–1.000** with the reference's (T4). int8 and fp32 differ in how much heat they make, not where they make it.

**5. Speed.** As in E78, no kind changed the work per cycle: all 4,024 kernel records from the 282 launches ran at
546.0 (fp32) or 318.0 (int8) cycles per op (T7).

## What it changes

- **For the blog's kinds table, the heat column.** The 32 cells E78 extrapolated now rest on a measurement for the
  seven kinds E89 ran. All six int8 kinds (zeros against idle) and fp32 ones heat the die by the same degrees per
  watt of the die's own power as fp32 random data (±2%), and by 4–11% more per board watt. E78's *S × 0.118 °C/W* for
  a 2 s window holds to +2…+15%. The cells to quote, at 600 MHz on aifoundry3: random int8 **0.86 ± 0.07 °C** in 2 s
  (0.90 ± 0.03 °C swing at 1/60 Hz); int8 −1 **0.22 ± 0.03 °C**; int8 zeros over idle **0.34 ± 0.01 °C**; fp32 ones
  **1.06 ± 0.16 °C**. The remaining float kinds below 12 W (π, −1.0, sparse50/90 and the one-sided kinds in fp32 and
  fp16) are still extrapolations, now backed by a measured coefficient for both a float constant and every int8 kind.
- **Horace hub, Status item 7 ("heat below ~12 W of switching, every int8 kind")** is closed for int8 and the float
  constant: the die's sensors detect int8 at a 0.90 °C swing with a 3% interval, where E85's camera saw 64.5 ± 28.3 mK.
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
| every rule scored on the 34-sensor mean | 24 verdicts scored, 24 PASS; the sampler never fell back to `ettelem` (command 74 answered in every one of the 22,976 samples) |
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
  sustained window measured from the reference level, not from an idle gate, so their per-watt numbers are
  comparable between kinds, not with E78's ΔT/S column except as noted.
- **int8 zeros is measured against idle (S); the other int8 kinds against int8 zeros (D).** Their r compares heat per
  watt across both.
- **E85's sampler sent a statistics reset once a second; E89's sends none** (no `--reset-ms`; the sampler has no such
  option).

## Files

| file | what |
|---|---|
| `README.md` | this file |
| [`results.md`](results.md), [`scored.json`](scored.json), [`e89.json`](e89.json) | `reduce_e89.py`: every block, lap, step and swing; the rules and verdicts |
| [`tables_e89.py`](tables_e89.py), [`tables.txt`](tables.txt) | the README's tables, printed from `e89.json` (it changes nothing) |
| [`posthoc_e89.py`](posthoc_e89.py), [`posthoc.txt`](posthoc.txt) | post hoc and descriptive: per-sensor noise at idle, ranges, the firmware's truncation |
| [`manifest.json`](manifest.json) | every file's sha256, the registration commits, the claim |
| `ident/` | the session `ettelem config` reads, the probe and the 3 s re-run, the box's `et-lab-manifest` |
| `logs/` | the queue log, the setup's dry-run log, the harness hashes on the box |
| `aifoundry3/e89/p8910`, `p8911`, `aifoundry3/e89-smoke/p8901` | raw: `telemetry.jsonl.gz` (10 Hz, with the 34 codes), `runs.jsonl` (host launch records), `marks.jsonl` (gate, idle, blocks, halves, launches), `run.log`, `configs.json`, `config_start/end.json`, `block.json`, `sampler.json`, `manifest.txt`, `code.sha256`, `gen.sha256`, `tiles/` (every tile the host dumped) |
