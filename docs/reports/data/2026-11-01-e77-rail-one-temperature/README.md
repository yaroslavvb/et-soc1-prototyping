# E77 — the rail launched and read at one temperature, at two rail voltages (aifoundry2)

*Pre-registered Sun 1 Nov 2026 (week 44), PST, before the `#community-lab` claim and the first launch (Q133). Any
change after this commit goes under Amendments, dated, before the data it touches. Results go above the registration
when the run is done; nothing below is edited.*

**What it answers.** The kinds page's [§ 11 list](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
item 13 ("Not touched: E77 ... each a governor move, your OK for that exact operation"), and the Horace hub's Levels
tab, stop 2 ("the card"), whose Missing column reads: *the rail measured AT the launch temperature, rather than at the
launch window and corrected onto it (E77, reserved; the same run would split the 0.875 pJ regulator row, and it needs
a governor move under the field manual's gates)*. It was the hub's item 2 on 28 Oct. The design is
[`E77-PLAN.md`](../2026-10-27-q129-rail-ledger/E77-PLAN.md), written with Q129's
[rail ledger](../2026-10-27-q129-rail-ledger/README.md) on 27 Oct and reserved since. **The owner authorized this
governor move on Sun 1 Nov 2026** (about 12:30 PST), for E77 among three named runs, on the condition that the firmware
maintainer's posted guidelines be read first; they were read in full, and the change record
([`CHANGE-RECORD.md`](CHANGE-RECORD.md)) says what they set.

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

## Results

*Pending: the run follows Q133's E111 on aifoundry2.*

## Amendments

**A1, Sun 1 Nov 2026, 15:1x PST** (before the claim, the gate reads and any card access by E77): the throttle
residencies read after each pass are raw states **2–4** (POWER_UP, POWER_DOWN, THERMAL_DOWN), not 2–6. E69's own rings
on this card (`docs/reports/data/2026-10-27-e69-governor-knob/smoke2/sp/start.bin`, `end.bin`) show that every read
of states 5 and 6 makes the service processor log "Unexpected power throtlling state" and "thermal pwr mgmt error:
get_throttle_time()" — errors on the card for a read E77 does not need (POWER_SAFE and THERMAL_SAFE bear only on
E117's alarm). One argument list in `run_e77.py`'s `queries()`; nothing else changes.
