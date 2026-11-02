# E77 — the rail launched and read at one temperature, at two rail voltages (aifoundry2)

*Pre-registered Sun 1 Nov 2026 (week 44), PST, before the `#community-lab` claim and the first launch (Q133). Any
change after this commit goes under Amendments, dated, before the data it touches. Results go above the registration
when the run is done; nothing below is edited.*

*Corrected after an independent verification the same evening (Sun 1 Nov 2026, about 19:00 PST), at the desk: no
card touched, nothing set, nothing re-run. Wrong sentences in the Results are replaced in place, each marked;
[Corrections after verification](#corrections-after-verification-sun-1-nov-2026) lists F1–F6, and
[`corrections-check.txt`](corrections-check.txt) prints every new number from the committed files. No registered
number or verdict changed, and the registration below is untouched (one dated note is added after its Amendments). The
two major ones: the 22 `SP Runtime Error` events were caused by this run's own residency read of raw state 4, which is
no state on the card's 0.22.0 build (F1); and the registered conduction bound used the plan's literal square, which
departure 10 rejects: in the registered model's own total-current form the 99% upper edge is more than the whole
0.875 pJ row, so the regulators' share stays unresolved (F2).*

## Results (the run: Sun 1 Nov 2026, 17:26–17:59 PST; written 18:1x PST)

**The registered verdict is FAIL, and by the registration's own rule it is provisional.** On the central footing
R_eff = **0.62 mΩ, 99% interval [−0.49, +1.73] mΩ** over three passes: the interval contains 0, which is the registered
FAIL; the pooled fit's rms falls by 22.6%, short of the 30% a PASS would also have needed (`results.json`
`footings.drift_split.fit`). *(Reworded after verification, F4: the first version set the rms beside its bar as if it
decided the verdict.)* The other two footings fail too: uncorrected 0.33 [−3.86, +4.53] mΩ, board_only 0.67
[−0.13, +1.47] mΩ. **What the FAIL bounds.** By the frozen conversion, R_eff·(21/V_A)², the interval's upper edge is
2.84 W at a 21 W minion rail (518 mV), 72% of the published 0.188 × 21 W, 0.63 pJ of the 0.875 pJ row (`moves`; the
registered figure). That conversion is the plan's literal square, which departure 10 rejects: the registered model
charges the regulators R·I² in their whole current, so a 21 W step on arm A's 7.11 W idle rail adds
R·[((7.11 + 21)/V_A)² − (7.11/V_A)²], 1.68 times the literal amount. In that form the upper edge is **4.77 W, 1.06 pJ,
more than the whole 0.875 pJ row** ([`corrections-check.txt`](corrections-check.txt) C). **So this run does not bound
the regulators' share below the row: the FAIL leaves the split unresolved**, and the frozen FAIL reading, "the whole
0.875 pJ row is then logic in step with the rails", is not supported. *(Replaced after verification, F2: the first
version read the FAIL as the whole row being logic in step, with the conduction loss at most 0.63 pJ.)* And **all four
rung pairs missed the 5% matching (P2)**, so by the registered rule the f·V² transfer is reported as refuted on this card
and the verdict as provisional, pending a re-cut ladder. The secondaries agree: the published small-rail coefficients
0.35 [−0.25, +0.96] mΩ, the plan's literal square 0.71 [−0.82, +2.24] mΩ, both FAIL; leaving nothing out changes
nothing (no launch was flagged `below_floor`).

**P1 FAIL, P2 four of four mismatched — and what broke (post hoc).** At equal hart counts arm B's minion watts over
arm A's are **2.33** (544 harts) and **2.68** (288), against the frozen 1.913 ± 5%; at the designed pairs arm B reads
+22%, +30%, +39% and +79% more than arm A (`P1_ratio`, `P2_matching`). Post hoc, the per-hart transfer itself holds:
fitting each arm's rung means against harts, arm A is **21.05 mW per hart** (−0.34 W, rms 0.05 W; the ledger's law
was 22.31) and arm B **40.49 mW per hart** (+3.75 W, rms 0.08 W), a ratio of **1.924 against f·V² = 1.899** at the
measured 518 / 618 mV, 1.3% apart (`posthoc.json`); over the three passes the ratio's 99% interval is [1.81, 2.04],
which holds 1.899. What breaks the matching is an **offset in arm B: +4.09 W on the minion rail and +1.73 W on the SRAM
rail at every rung** (99% over passes [3.44, 4.75] W and [1.69, 1.78] W), the operating-point step
([`corrections-check.txt`](corrections-check.txt) D). *(Label and intervals added after verification, F4.)* On this
card the idle clock is 600 MHz in both arms (the ring: "New OP: Freq 600 MNN 520 (V) SRM 705 (V)" at idle, "Freq 700 MNN 570 SRM 735" and
"Freq 800 MNN 620 SRM 830" under load), so arm B's pre-launch idle sits at 600 MHz and its window at 800 MHz: its
deltas carry the static and clock power of the higher operating point with no work at all. E77-PLAN.md's matching
assumed each arm idles at its own clock, and this registration did not catch it.

**With that step fitted (post hoc, no verdict),** offrail = a_m·Δm + c_B·[arm B] + R_eff·Δ(I²) per pass gives
R_eff = **0.21 mΩ, 99% [−0.08, +0.50] mΩ**, rms better by 3.5%: still no conduction term. In the model's total-current
form its upper edge is **1.37 W at a 21 W rail step, 0.30 pJ of the 0.875 pJ row** (the literal conversion gives
0.82 W, 0.18 pJ). With the SRAM and NoC rails as regressors too, R_eff = 0.64 [−0.69, +1.98] mΩ, whose upper edge is
5.45 W, 1.21 pJ, more than the row. So the post hoc bound depends on the fit: only the tighter one bounds the share, at
about 0.3 pJ. *(Replaced after verification, F2 and F4: the first version gave only the tighter fit's literal
≤ 0.18 pJ.)* A pre-registered re-run would define arm B's reference at its own operating point (or fit the step) and
re-cut arm B's harts on the measured 40.5 mW per hart.

**S-T, the rail at the launch temperature (secondary, no verdict).** Arm A's top rung is E38's own configuration
(fp32 randn on 1,024 harts at 600 MHz), launched here at 54–55 °C with its drift measured in the same block. Its minion
rail is **4.645 pJ per multiply-add on every footing** (4.648 on drift_split), because this block's minion drift is
−0.001 ± 0.027 W/°C while the board's is 0.267 ± 0.098 W/°C, 76% of it off the three rails (`drift`, 43 body windows).
The ledger's footings put the minion row at 4.55 / 4.77 / 4.95 pJ; at E77's launch temperature the footing choice moves
it by 0.003 pJ, and the whole footing question sits in the off-rail row (0.97 pJ uncorrected, 0.56 on drift_split, 0.44
on board_only). The board is 5.69 pJ uncorrected, 5.16 with the registered 0.81 W/°C (this block's own board slope,
0.27 W/°C, is E66's idle 0.29). Caveats: a late window ([t1−1.5, t1]), the model's settling ratio (0.962; the 8 s rung
did not run), seven launches (`secondary_rail_at_launch_temperature`).

**The governor operation, as registered.** Originals 65 W / 65 °C by the two RAM GETs (17:27:01); TDP **65 → 0** at
17:35:34.974, read back 0 / 65 at 17:35:34.999; the pin held every arm-A launch at 600 MHz (the abort never fired);
**0 → 65** at 17:55:10.848, read back 65 / 65 at 17:55:10.871; the watchdog, armed at 17:35:34, read `release` and
exited at 17:55:15; the return burst stepped **600 → 700 → 800 MHz** and arm B's third pass then ran all 12 launches at
800 MHz; closing read 17:59:25: **65 W / 65 °C**, `low_power`, 600 MHz, module uptime 6 d 3 h 46 m (no reset).
**The ring criterion E72 left PARTIAL is met here.** Read with the lab's full ring reader
(`tools/claims-v3/hpl/sptrace_full.py`), the dump after the burst holds ten entries newer than the dump before it: the
previous residency read's two error lines (F1), then **two `Power throttle up` lines at 17:55:14.92 and 17:55:15.10 PST**
(`current pwr 30310`, then `32500`, against `tdp level: 65000`), 0.79 and 0.96 s into the burst's launch and 4.1 s after
the restore, each followed by its operating point (700, then 800 MHz), and 600 MHz again at 17:55:18.98, after the
launch ended. The SP clock is aligned to the residency reads' error lines, within 9 ms; the 10 Hz telemetry first reads
700 MHz at 17:55:14.98 and 800 MHz at 17:55:15.18 ([`corrections-check.txt`](corrections-check.txt) B). *(Replaced
after verification, F3: the first version called it partial, saying that dump held nothing newer than the one before;
the runner's live check, which passed, had counted all 12 throttle-up lines in the dump, stale ones included.)* Highest
board reading 70.7 W (a 768-hart heater launch), 58.05 W in a kept launch. **Host kernel log: 22 `SP Runtime Error`
events in the window, all caused by this run's own residency reads.** Each read of raw state 4, which is no state on the
card's 0.22.0 build, makes the service processor log two ERROR lines, and each ERROR line pushes one such event to the
host: two events 6–8 s after each of the 11 reads (the gate reads, the smoke and the nine in the session), none elsewhere
(`raw/kernel-events.txt`; F1). *(Replaced after verification, F1: the first version called them the known syndrome, two
per management burst.)* 32.44 card-minutes. The change record has the full log.

**What ran.** 67 of 72 launches (5 gates not reached: the preheat to 59 °C failed within 8 heater launches at the
start of four passes and once mid-pass; arm A's heater, 1,024 harts at 600 MHz, heats slowly), 66 kept (one arm-B
launch dropped by S1: its clock dipped after reaching 800 MHz); the 8 s settling rung's gate was not reached either.
The gate held the rails to S2's settling test with approaches of 10.2–11.7 s; the launch readings were **54.9 °C in
arm A (54–55) and 53.7 °C in arm B (53–54), a 1.2 °C gap** — above the 1 °C this registration said it would name.
Both arms also launched below the 55–58 °C that departure 3 registered: arm A at 54–55 °C (29 of 32 kept launches at
55 °C), arm B at 53–54 °C (11 of 34 at the 53 °C re-heat floor, none flagged `below_floor`)
([`corrections-check.txt`](corrections-check.txt) E). *(Added after verification, F5.)* In arm B the clock reached
800 MHz 0.34–1.26 s after each launch began, before the window.

**What it changes.** For the kinds page's § 11 item 13 and the Levels tab's stop 2: E77 ran. The regulators' half
stays open: no conduction term resolved, and this run does not bound the conduction share below the row (in the
registered model's total-current form the 99% upper edge is 1.06 pJ of the 0.875 pJ row; the frozen literal conversion
gives 0.63 pJ). Post hoc, with the operating-point step fitted, one fit bounds it at about 0.30 pJ and a fit that also
takes the SRAM and NoC rails does not bound it. Also post hoc, and the reason the registered P1 and P2 failed: the
minion rail's per-hart cost moves with f·V² from 600 to 800 MHz (1.924, 99% [1.81, 2.04], against 1.899), and the
800 MHz operating point costs **4.09 W (99% [3.44, 4.75]) on the minion rail and 1.73 W ([1.69, 1.78]) on the SRAM rail
before any work**. *(Replaced after verification, F2 and F4: the first version bounded the regulators at ≤ 0.63 pJ or
≤ 0.18 pJ and gave the post hoc numbers without their label or intervals.)* At a 54 °C launch the minion row does not
depend on the leakage footing. The kinds page's [§ 11 list](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
item 13 ("Not touched: E77 ... each a governor move, your OK for that exact operation"), and the Horace hub's Levels
tab, stop 2 ("the card"), whose Missing column reads: *the rail measured AT the launch temperature, rather than at the
launch window and corrected onto it (E77, reserved; the same run would split the 0.875 pJ regulator row, and it needs
a governor move under the field manual's gates)*. It was the hub's item 2 on 28 Oct. The design is
[`E77-PLAN.md`](../2026-10-27-q129-rail-ledger/E77-PLAN.md), written with Q129's
[rail ledger](../2026-10-27-q129-rail-ledger/README.md) on 27 Oct and reserved since. **The owner authorized this
governor move on Sun 1 Nov 2026** (about 12:30 PST), for E77 among three named runs, on the condition that the firmware
maintainer's posted guidelines be read first; they were read in full, and the change record
([`CHANGE-RECORD.md`](CHANGE-RECORD.md)) says what they set. The full read was the workflow's desk lane's: all 258 of
the maintainer's posts at 13:54–14:01 PST, and the field manual's four files at 12:30 PST. The run agent read that
lane's paraphrase, the manual's `AGENTS.md` and its change-record template, and last checked for newer posts at
16:04:26 PST, 82 minutes before the claim. *(Added after verification, F6.)*

## Corrections after verification (Sun 1 Nov 2026)

The workflow's independent verifier returned "holds with fixes": the governor move safe and honestly recorded, no
critical fault, and two major and four minor faults, all in the write-up. It reproduced `results.json` and
`posthoc.json` from the committed raw data. One read-only read of its own at 18:30:53 PST found the card at its
originals (TDP 65 W, threshold 65 °C, `low_power`, 600 MHz). Corrected at the desk the same evening: no card touched,
nothing set, nothing re-run. **Not changed:** every registered number and verdict; `results.json`, `reduce.txt`,
`posthoc.json`, `posthoc_e77.py` and `raw/`; the registration below and the tools under `tools/claims-v3/e77/`; the
change record's GO section. [`corrections-check.py`](corrections-check.py) recomputes every new number from the
committed files and prints it to [`corrections-check.txt`](corrections-check.txt) (sections A–E):
`/usr/bin/python3 docs/reports/data/2026-11-01-e77-rail-one-temperature/corrections-check.py`.

- **F1 (major): the residency reads were mislabelled, and they caused the 22 kernel events.**
  - *The labels.* After each pass the run read raw throttle states 2, 3 and 4 and labelled them POWER_UP, POWER_DOWN
    and THERMAL_DOWN. Those are the seven-state names of the 0.20.0 and 0.18.0 builds
    (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`). This card runs BL2 0.22.0
    ([Q130's governor finding](../2026-10-31-q130-governor-thermal-branch/README.md), item 7), whose enum is IDLE 0,
    UP 1, DOWN 2, SAFE 3, with 4 its UNKNOWN sentinel (et-platform `836a4ab`,
    `device-api/include/management-api/device_mgmt_api_spec.h:280-285`). So raw 2 is **POWER_DOWN**, raw 3 **POWER_SAFE**
    and raw 4 **no state**; POWER_UP (1) was never read. Raw 2 grew 7.03, 4.79 and 3.60 s over arm B's three passes,
    whose dumps hold throttle-down lines, and stayed flat under the pin; raw 3 read 0 at all 11 reads.
  - *The events.* A read of raw 4 takes `get_throttle_residency`'s default branch, which logs "Unexpected power
    throtlling state: 4" at ERROR (`services/thermal_pwr_mgmt.c:1477-1501`). The handler then logs "thermal pwr mgmt
    error: get_throttle_time()" at ERROR (`services/thermal_power_monitor.c:596-610`). Past the runtime-error threshold,
    every ERROR line pushes one `SP_RUNTIME_ERROR` event to the host (`services/log.c:371-389, 410-428`). The rings hold
    those two lines after every read they still cover, the smoke's ring included; the change record had said it held
    none. Aligned on them, the SP clock reproduces the read times within 9 ms. The kernel log's 22 events are two, 6–8 s
    after each of the 11 reads, and none elsewhere (A). The read itself is a RAM read and writes nothing; the error
    lines and the events are its only effect.
  - *Amendment A1* dropped states 5 and 6 for exactly this error logging, but kept 4, although the E69 rings it cites
    show state 4 erroring too (2 and 4 times, beside 5 and 6). Before any re-run, `run_e77.py`'s `queries()` drops raw 4
    (and reads 1 if POWER_UP is wanted).
  - *A lead, not a result.* At `836a4ab` POWER_SAFE is entered only from the PMIC interrupt callback, on an
    over-temperature or over-power cause (`thermal_pwr_mgmt.c:2317-2323`). Its time is added when an episode ends
    (`:2096-2114`), and nothing resets the counter. So raw 3's zero says, on the version-matched source, that no such
    episode has completed on this card since its service processor started on 26 Oct. That span includes E83's runs of
    31 Oct, whose board samples reached 88.9 W. This bears on [§ 11 item 14](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)
    (aifoundry2's over-power alarm). The running build's residual applies, and what the PMIC's threshold measures is
    not established here.
- **F2 (major): the conduction bound used the conversion departure 10 rejects.** The frozen report form,
  R_eff·(21/V_A)² (`predictions.json` `V_fit.report`, `reduce_e77.py` `moves`), is the plan's literal square. The frozen
  model charges the regulators R·I² in their whole current, so the loss a 21 W rail step adds is
  R·[((m₀ + 21)/V_A)² − (m₀/V_A)²]. Arm A's idle minion rail is m₀ = 7.11 W (32 kept launches, 7.01–7.15 W) at 518 mV:
  13.7 A, where departure 10 assumed 15–16 W and about 30 A. The increment is 1.68 times the literal form (C):

  | fit | R_eff, mΩ [99%] | upper edge, frozen literal form | upper edge, total-current increment |
  |---|---|---|---|
  | registered (drift_split; the verdict) | 0.62 [−0.49, +1.73] | 2.84 W, 0.63 pJ | **4.77 W, 1.06 pJ (121% of the row)** |
  | post hoc, arm-B offset | 0.21 [−0.08, +0.50] | 0.82 W, 0.18 pJ | **1.37 W, 0.30 pJ (35%)** |
  | post hoc, offset + SRAM and NoC | 0.64 [−0.69, +1.98] | 3.25 W, 0.72 pJ | **5.45 W, 1.21 pJ (138%)** |

  pJ = W × 0.875 / (0.188 × 21 W). The verdict, FAIL, is unchanged: it rests on the interval containing 0. The literal
  figure stays the registered one, labelled as such. But the registered interval does not bound the regulators' share
  below the 0.875 pJ row, so the FAIL leaves the split unresolved; the frozen reading that the whole row is logic in step
  is not supported by this run.
- **F3 (minor): the return burst's ring criterion is met.** The README called it PARTIAL, saying that the dump after
  the burst held nothing newer than the one before. Read with the full ring reader, it holds ten newer entries, among
  them two `Power throttle up` lines at 17:55:14.92 and 17:55:15.10 PST, 4.1 s after the restore and inside the burst
  (B). The change record's "12 lines" counted every throttle-up in the dump, stale ones included; so did the runner's
  live check (`run_e77.py` `queries()`). Before any re-run, the check counts only entries newer than the previous dump,
  by SP timestamp (`sptrace_full.since`).
- **F4 (minor): post hoc labels and intervals.** The statements that go outward now say "post hoc" and carry intervals
  with passes as the unit (D):
  - the per-hart ratio, 1.924 [1.81, 2.04], which holds f·V² = 1.899;
  - the operating-point step, 4.09 W [3.44, 4.75] on the minion rail and 1.73 W [1.69, 1.78] on the SRAM rail;
  - both post hoc fits are quoted (F2);
  - the verdict is FAIL because the interval contains 0, and the rms gain is reported beside it.
- **F5 (minor): the launch readings departed from departure 3.** It registered launch readings of 55–58 °C. Arm A
  launched at 54–55 °C, arm B at 53–54 °C, 11 of 34 at the 53 °C re-heat floor (E). "What ran" now says so.
- **F6 (minor): who read what, and when.**
  - The full read of the maintainer's posts and of the field manual's four files was the desk lane's.
  - The run agent read that lane's paraphrase (14:24 PST), the change-record template and the manual's `AGENTS.md`
    (its first 230 of 249 lines, 14:30 PST).
  - It last checked for newer posts at 16:04:26 PST: 82 minutes before the claim (17:26:15) and 91 before the set
    (17:35:34.974), not "just before the claim" as the change record planned.
  - `#community-lab`, read again at 17:25 and 18:07 PST, shows no post of his after 14:00 PST. The direct messages were
    not read again after 16:04:26.
  - On a re-run, the run agent reads all four manual files itself and re-checks both within minutes of the claim.

## The question

The rail ledger puts **0.875 pJ** of a 5.783 pJ random fp32 multiply-add on "the regulators' delivery loss plus logic
in step with the rails" — one coefficient, 0.188 × minion W on aifoundry2, that no committed data can split, because the
management struct carries each regulator's output power and no input-side power. A switching regulator's conduction
loss carries 1/V² at a given output power; logic in step with the rail does not. So the same minion-rail watts
delivered at two rail voltages separate them:

    offrail = a_m · minion + a_s · SRAM + a_n · NoC + R_eff · (minion / V_minion)²        (E77-PLAN.md)

(registered here with the conduction term in the total current, departure 10), with arm A at **600 MHz, about 516 mV** (the static TDP level at 0 pins the clock at the vmin-LUT floor, the write E72
made on this card on 27 Oct) and arm B at **800 MHz, about 618 mV** (the card's own governor, untouched), matched by
hart count on the ledger's measured 600 MHz minion-rail law (−0.446 W + 22.31 mW per hart) carried to 800 MHz by
f·V² = 1.913 per hart. Every launch passes one die gate, so both arms are launched and read at one temperature.

The same run also bears on the ledger's other open question: its three leakage footings differ by **0.23 pJ** on the
multiply-add (minion rail 4.55 / 4.77 / 4.95 pJ), and arm A's top rung is E38's own configuration (fp32 randn on 1,024
harts at 600 MHz) launched from a known reading with its own drift measured in the same block.

## Design

| rung | arm A: TDP 0, 600 MHz | predicted minion W | arm B: own governor, 800 MHz | predicted minion W | mismatch |
|---|---|---|---|---|---|
| 1 | 1,024 harts (32 per shire) | 22.40 | 544 (17 per shire) | 22.36 | −0.2% |
| 2 | 768 (24) | 16.69 | 416 (13) | 16.90 | +1.3% |
| 3 | 544 (17) | 11.69 | 288 (9) | 11.44 | −2.2% |
| 4 | 288 (9) | 5.98 | 160 (5) | 5.98 | −0.1% |

- **Workload:** `sparsity_host --test fma --type fp32 --values randn --shires 0xffffffff --per-shire N`, 4 s launches
  (`--seconds 4 --budget 5.5`), every one under `timeout 10` with `--stop-file`; aifoundry2's `build/sparsity_t2`.
- **Passes:** three per arm; a pass is three rounds, each round every rung once in a seeded shuffle
  (`random.Random("E77|<arm>|<pass>")`), so 12 launches a pass and 72 in all.
- **Order, one session holding the card lock throughout:** arm B passes 1–2 → the deadline watchdog → **TDP 65 → 0**,
  read back → arm A passes 1–3 → the settling rung → **TDP 0 → 65**, read back → the return burst → arm B pass 3 →
  closing reads. The gate reads come first, in their own short hold of the lock, then a smoke (the sampler and one 2 s
  launch of 160 harts at the card's own settings, no write), and the GO is committed before the session starts.
- **The gate, before every launch:** the arm's heater (2 s launches) until the die mean reads ≥ 59 °C; then idle until
  it reads ≤ 58 °C, at least 6 s after the last device process ended, **with the minion rail settled by S2's own test
  computed live** (|mean over [t−5, t−3] − mean over [t−2, t−0.3]| ≤ 0.15 W). A die that falls below 53 °C first is
  heated again (at most three times); after that the launch goes ahead at its reading, flagged `below_floor`. Arm A's
  heater is 1,024 harts (at 600 MHz, about 51 W, E72's own trace); arm B's is 768 harts.
- **The settling rung:** one 8 s launch of arm A's top rung, after arm A's passes.
- **The return burst:** one 4 s launch of arm B's top rung right after the restore; the clock must step up to 800 MHz
  and the ring dumped after it must hold a throttle-up line.
- **Telemetry:** 10 Hz, the **no-PMIC-read profile**: `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/`), which sends
  only the board power, the service processor's statistics (the rails and `sp.minion_mv`), the die sensors and the
  clocks; it drops `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE` (register reads in the PMIC at et-platform `836a4ab`) and
  has no statistics reset. E77's inputs are all still read.
- **The governor:** one field, `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL`, written only to the literal 0 and back to the
  literal 65 the gate read; the threshold is never written; every write is read back by the two RAM GETs; a deadline
  watchdog (E72's), armed before the first write, writes 65 back if the session has not released it within 75 min or
  by 18:55 PST.
- **Aborts:** any single board reading ≥ 85.0 W; a die mean ≥ 72 °C; the die high-water latch ≥ 80 °C; while the TDP is
  0, any clock other than 600 MHz during a measurement launch; a DM rc ≠ 0 or a read-back mismatch; a device process
  outliving its `timeout 10`. Any abort restores the governor in the session's `finally`. The desk draft's "a
  kernel-log line other than the known syndrome" is read before and after the session (read-only `dmesg`, E69's
  record) and reported, not used as a live abort.
- **Time:** at most 50 card-minutes (the runner cuts at 47, with per-phase cuts by whole rounds: arm B's first passes
  by 16 card-minutes, the move by 17, the restore by 36, arm B's third pass by 45; the restore and the return burst are
  never cut); no session starts after 18:00 PST; the runner stops at 18:55 PST.
- **Etiquette:** lab `AGENT.md` §§ 4–5; the card lock held for the whole session; before every launch another user's
  device process, a stale one of ours or the module's use count over its baseline ends the session; another logged-in
  user blocks unless every one of their sessions has been idle for 120 minutes or more (E111's amendment A1, the same
  rule, which fails closed).

## Where this registration departs from or adds to E77-PLAN.md (named before any data)

1. **72 launches, not "96".** The plan's table and text give 4 rungs × 2 arms × 3 passes, which is 24 rung-launches;
   its "96 launches, 6.4 card-minutes" multiplies by the 4 s. Here each rung runs three times per pass (72 launches),
   the most that fits the 50 card-minute budget with the gate below.
2. **The settling rung is 8 s, not 12 s.** One launch cannot outlive the lab's `timeout 10`; 8 s gives the rails 4 s
   after the 4 s window, more than six time constants.
3. **The gate waits for the rails, so the launch reading is 55–58 °C, not 58 °C.** On this card the die falls from
   59–60 °C to 58 °C within about 0.5 s of a heater ending (E72's own telemetry, 27 Oct), while the rails need about
   10 s to settle from a 2 s heater (τ ≈ 1.06 s). E60/E72's strict start launched about 0.5 s after the heater, which
   the ledger's S2 screen would reject. Here S2 is a launch condition instead, and every launch reading is recorded and
   used in the leakage correction. The arms' mean launch readings are reported; a gap above 1 °C is named.
4. **Arm B's heater is 768 harts.** At 800 MHz the full card reads 82–85 W with single readings to 88.88 W (E83),
   which would trip the 85 W single-reading abort.
5. **The no-PMIC-read telemetry profile** (above). The plan's inputs are unchanged.
6. **The return burst before arm B's third pass.** The plan's "arm B pass 3 doubles as the return check" would leave
   pass 3's first launch absorbing the 600 → 800 MHz step after the restore; the burst shows the stepping, and pass 3
   then runs from the card's own state.
7. **Identity by continuity.** The firmware revisions query is not sent (at `836a4ab` it writes the PMIC's
   firmware-management command register twice). The module uptime (service-processor RAM) must exceed the minutes since
   E69's revisions read on this card (27 Oct 2026, 13:56:26 PDT): no service-processor reset since, so that read still
   names the running image (release 1.4.0, BL1/BL2 0.22.0, PMIC 1.5.0, minions 0.25.1).
8. **Three thresholds the plan names without numbers:** the 1.91 ratio check gets a ±5% band (the plan's matching
   tolerance); "99% confidence over passes" is mean ± t(0.995, n−1) · SD/√n over the per-pass R_eff; if more than one
   pair misses the 5% matching, the verdict is reported as provisional (the plan re-cuts the ladder first, which this
   session cannot do).
9. **Secondary readouts, which carry no verdict:** the same fit with the SRAM and NoC coefficients held at the
   published aifoundry2 values (0.034, 0.291); the plan's literal square term (below); and S-T, the rail at the launch
   temperature: arm A rung 1's minion/board ratio and pJ per multiply-add on the three footings, against the ledger's
   0.787 / 0.825 / 0.856 and 4.55 / 4.77 / 4.95 pJ.
10. **The conduction term is written in the total current.** A regulator loses R·I² in its whole output current, and
    the fit is written in deltas over each launch's idle, where the minion rail already carries about 15–16 W (about
    30 A at 516 mV). The change in its conduction loss is R·[((m₀ + Δm)/V)² − (m₀/V₀)²], with m₀ the idle bracket's
    minion watts, V₀ its voltage and V the window's. The plan's R·(Δm/V)² leaves out the cross term 2·I₀·ΔI, which is
    larger than ΔI² at every rung here and differs between the arms through 1/V², so it would land partly in a_m and
    partly in R_eff. On the dry run's toy card, built with 1.2 mΩ, the total-current fit returned 1.16 mΩ and the
    literal one 4.0 mΩ. The verdict uses the total-current form; the literal form is reported beside it.

## Predictions (frozen in [`predictions.json`](../../../../tools/claims-v3/e77/predictions.json))

- **P1, the ratio at equal hart counts:** minion-rail watts, arm B over arm A, at 544 and at 288 harts: **1.913**
  (PASS within ±5% at both); also reported against (800/600)·(V_B/V_A)² from the measured voltages. A FAIL is reported
  first: the matching is then wrong.
- **P2, the matching:** each rung pair within 5% of each other in measured minion watts; the predicted values are the
  table's.
- **P3:** at matched rail watts, arm A's conduction loss exceeds arm B's by (V_B/V_A)² − 1 of the conduction part,
  **43.4%** at the nominal 516/618 mV, computed from the measured voltages.
- **V, the verdict (central footing):**
  - **PASS (the term exists):** R_eff's 99% interval over the three passes excludes 0, AND the pooled fit's rms is at
    least 30% below the same fit without the R_eff term. Reported: R_eff in mΩ, the conduction loss at a 21 W minion
    rail at arm A's measured voltage, its share of 0.188 × 21 W, and that share of the 0.875 pJ row in pJ.
  - **FAIL (it does not):** the interval contains 0: the whole 0.875 pJ is then logic in step with the rails, the
    conduction loss bounded above by the interval's upper edge. **A FAIL is a result.**
  - **Neither:** the interval excludes 0 but the rms improves by less than 30%: "resolved, not a material term".
- No size or sign of R_eff is predicted: the plan freezes the test, not the outcome.

## The pre-registered reading ([`reduce_e77.py`](../../../../tools/claims-v3/e77/reduce_e77.py))

Per launch (t0 = its first kernel record's start, t1 = its last record's end):
- **Windows:** idle [t0−2, t0−0.3] s; far [t0−5, t0−3]; **the window [t1−1.5, t1]**, the median of the 10 Hz board
  samples and of the raw rail readings (the plan's statistic); body [t0+1.5, t1−0.2] for the drift.
- **S1:** rc 0 and every record ok; enough samples in each window; arm A every sample at 600 MHz over [t0−2, t1]; arm B
  every window sample at 800 MHz and no sample under 800 after the first 800 one (a clock that moves is dropped, not
  corrected). **S2:** the settling test above, and an approach ≥ 6 s. **S3:** board samples more than 2 W under their
  window's median dropped (E62's meter dips), idle and window alike.
- **Deltas** over the launch's own idle: board, minion, SRAM, NoC; V = the window's median `sp.minion_mv`.
- **Settling:** each rail's window delta divided by its settling ratio from the 8 s rung (its delta over the 4 s
  window's position against its last 1.5 s, the later one taken back to the earlier temperature with the block's drift
  slope); the first-order filter's own ratio at τ 1.06 s if that rung is not kept (flagged).
- **Footings** (the ledger's three): uncorrected; **drift_split, the central one**: C = 0.81 W/°C × (T_window −
  T_launch) taken off the board and shared over the rails by this block's drift slopes (the rails deconvolved with
  `tools/ettelem/deconv.py`, body windows rising ≥ 1 °C; the ledger's aifoundry2 slopes if fewer than three launches
  qualify or the board slope is not 2 SE from 0), the rest on the off-rail remainder; board_only.
- **The fit:** offrail = a_m·Δm + a_s·ΔSRAM + a_n·ΔNoC + R_eff·[((m₀ + Δm)/V)² − (m₀/V₀)²] (departure 10); per
  pass k, the rung means of arm A pass k and arm B pass k (8 points), least squares, no intercept; R_eff per pass; the
  verdict as above. The pooled fit uses every rung mean. Sensitivities: the other two footings, `below_floor` launches
  left out, the two secondary fits.

## Gates

The ET-SoC-1 firmware field manual's gates, PASS / FAIL / UNKNOWN / N-A each with its evidence and time (UNKNOWN is
never PASS), are in [`CHANGE-RECORD.md`](CHANGE-RECORD.md), filled as the run goes and committed with its data. The
desk gates (rule 8 at the version-matched source, the envelope, recovery) are filled there before this commit; the
live gates (identity by continuity, the originals, the LUT floor, exclusivity) are filled at gate time and committed as
the GO before the first write.

## Files

| file | what |
|---|---|
| `tools/claims-v3/e77/run_e77.py` | the runner (`plan`, `gates`, `session`; `--dry` touches no device) |
| `tools/claims-v3/e77/protocol.json` | the design above, as the runner reads it |
| `tools/claims-v3/e77/predict_e77.py`, `predictions.json` | the frozen predictions and rules |
| `tools/claims-v3/e77/reduce_e77.py` | the reduction |
| `tools/claims-v3/e77/ettelem-e77/` | the no-PMIC-read telemetry tool and its build file |
| `tools/claims-v3/e77/e77.sh` | the stages on the box: build, look, kernlog (the host kernel log's ET error events, read-only, before and after; E69's record), gates, smoke, go, status, wait |
| `CHANGE-RECORD.md` | the field manual's record for this governor move |
| `raw/` | *(after the run)* the run directory: `gates.json`, `smoke/`, `session.json`, `launches.jsonl`, `gov.jsonl`, `passes.jsonl`, `queries.jsonl`, `marks.jsonl`, `end.json`, `tel/*.jsonl.gz` (10 Hz, no-PMIC-read), `sp/*.bin` (the rings), `watchdog.*`, `kernel-events.txt`; the box's tree path written `<tree>` |
| `results.json`, `reduce.txt` | *(after the run)* the registered reduction: `/usr/bin/python3 tools/claims-v3/e77/reduce_e77.py docs/reports/data/2026-11-01-e77-rail-one-temperature/raw --out .../results.json --text .../reduce.txt` |
| `posthoc_e77.py`, `posthoc.json` | *(after the run, post hoc)* each arm's minion-rail law against harts, the operating-point step, the fit with an arm-B offset |

## Results

*At the top (written after the run, Sun 1 Nov 2026, 18:1x PST); this line replaced "Pending".*

## Amendments

**A1, Sun 1 Nov 2026, 15:04 PST** (before the claim, the gate reads and any card access by E77): the throttle
residencies read after each pass are raw states **2–4** (POWER_UP, POWER_DOWN, THERMAL_DOWN), not 2–6. E69's own rings
on this card (`docs/reports/data/2026-10-27-e69-governor-knob/smoke2/sp/start.bin`, `end.bin`) show that every read
of states 5 and 6 makes the service processor log "Unexpected power throtlling state" and "thermal pwr mgmt error:
get_throttle_time()" — errors on the card for a read E77 does not need (POWER_SAFE and THERMAL_SAFE bear only on
E117's alarm). One argument list in `run_e77.py`'s `queries()`; nothing else changes.

**A2, Sun 1 Nov 2026, 16:09 PST** (before the claim, the gate reads and any card access by E77): **a GO interlock in
code.** The session no longer writes the TDP as soon as arm B's first two passes end: it waits for a file `GO` in its
run directory, which the operator creates only after the GO commit (the live gates filled in the change record) is
pushed. If `GO` has not appeared by the move cut (17 card-minutes), there is no move: arm A and arm B's third pass are
not run, the session closes with its reads, and nothing was written. This makes "the GO recorded in a commit before
the first write" a coded condition instead of an order of steps, and lets the session start straight after the smoke
while the GO commit is made during arm B's first passes (Q133's E111 holds aifoundry2 until close to the 18:00 PST
start limit). Dry-tested both ways (present: the full dry session; absent: no move, closing read 65 W / 65 °C).

*Note after verification, Sun 1 Nov 2026, about 19:00 PST (not an amendment: written after the data, it changes
nothing above):* A1's labels are the 0.20.0 build's. On the card's 0.22.0 build raw states 2–4 are POWER_DOWN,
POWER_SAFE and no state, and the E69 rings A1 cites show state 4 logging the same two errors as states 5 and 6. The
run's 11 reads of state 4 caused the window's 22 `SP Runtime Error` events. See
[Corrections after verification](#corrections-after-verification-sun-1-nov-2026), F1.
