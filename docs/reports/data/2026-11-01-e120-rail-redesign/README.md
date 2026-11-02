# E120 — E77 redesigned: the rail launched and read at one temperature, at two rail voltages, with the operating-point step fitted (aifoundry2)

*Pre-registered Sun 1 Nov 2026 (week 44), PST, before the `#community-lab` claim and the first launch (Q134). Any
change after this commit goes under Amendments, dated, before the data it touches. Results go above the registration
when the run is done; nothing below is edited.*

## Results (the run: Sun 1 Nov 2026, 20:49–21:20 PST; written 21:2x PST)

**The registered verdict is FAIL, narrowly, and the bound is new: the regulators' conduction share of the 0.875 pJ row
is at most 0.69 pJ.** On the central footing R_eff = **0.55 mΩ, 99% [−0.06, +1.16] mΩ** over five passes (per pass 0.61,
0.30, 0.30, 1.02, 0.51): the interval contains 0, by 0.06 mΩ, which is the registered FAIL; the pooled rms falls by 2.9%
(`results.json` `footings.drift_split.fit`). **B: BOUNDED BELOW THE ROW.** At the interval's upper edge a 21 W
minion-rail step on arm A's measured idle rail (6.75 W at 518 mV) adds **3.12 W** of conduction loss in the registered
model's total-current form, **0.69 pJ of the 0.875 pJ row** (0.42 pJ by the literal conversion); at the mean, 1.48 W,
0.33 pJ (`results.json` `B`). So at 99% at least 0.18 pJ of the row is not regulator conduction. E77's registered form
gave an upper edge of 1.06 pJ, above the row. **C1 FAILS:** E77's post hoc bound, 0.496 mΩ (0.30 pJ), does not hold on
fresh data; E120's upper edge is 1.16 mΩ, because its five passes spread six times wider (SD 0.30 mΩ) than E77's three
did in the same form (0.05). In this form the linear "logic in step" coefficient comes out near zero (a_m −0.064 to
+0.042 per W, mean −0.001) and the arm-B offset at +0.63 W (0.26–0.93): the fit trades a_m against R_eff, which is
what widens the passes.

**The rest of the registration passes.**
- **T1, the per-hart transfer: PASS.** Arm B's cost per hart over arm A's, divided by (800/600)·(V_B/V_A)² from the
  measured voltages, is **0.979, 99% [0.906, 1.053]** over five passes (ratios 1.86, 1.92, 1.75, 1.90, 1.88 against
  1.90; `T1`, `lines_per_pass`). E77's post hoc finding, now registered: the minion rail's per-hart cost moves with f·V².
- **S1 and S2, the operating-point step: PASS.** With no work, the 800 MHz operating point costs **4.26 W on the minion
  rail, 99% [3.82, 4.70]**, and **1.76 W on the SRAM rail, [1.70, 1.81]** (E77's post hoc 4.09 [3.44, 4.75] and 1.73
  [1.69, 1.78]; `S1`, `S2`).
- **P2, the matching: PASS.** The re-cut ladder matched every pair within 2.4% (−2.4, +1.7, −2.2, +0.2%), where E77's
  missed by 22–79%.
- **G, one temperature: PASS.** Arm A launched at 52.03 °C (52–53) and arm B at 51.95 °C (51–52), 0.08 °C apart (E77:
  1.2 °C).
- **RING: PASS.** The return burst stepped 600 → 700 → 800 MHz, and the ring dumped after it holds 2 throttle-ups newer
  than the dump before it.
- **K: PASS.** 0 kernel error events in the window (`raw/kernel-events.txt`; E77's held 22).

**The secondaries (no verdict).** The uncorrected footing gives 0.89 mΩ [0.41, 1.37], an interval that excludes 0 with
an rms gain of 8.5% ("resolved, not material"); board_only 0.53 [−0.14, 1.19]; the published small-rail coefficients
held 0.55 [−0.05, 1.14]; SRAM and NoC free 0.53 [−0.19, 1.25]; E77's registered form (no offset) 0.37 [−0.32, 1.06];
launches flagged `below_floor` left out 0.44 [−0.06, 0.94]; and the floor-referenced form, which spends one arm-B point a
pass on the reference, −0.02 [−1.45, 1.41]. Every upper edge lies between 0.56 and 0.85 pJ, below the row.

**Post hoc (labelled; no verdict; `posthoc_e120.py` → `posthoc.txt`).** All five per-pass values are positive (a
one-sided sign test gives p = 0.031), and the same five passes at 95% give [0.18, 0.91] mΩ. The widest pass, 3, holds
the one launch of either run that reached 800 MHz late: 1.84 s after it began (E77's latest was 1.26 s). The service
processor's rails are the PMIC's running average (τ about 1.06 s) and the board reading is not, so that launch read its
minion rail low in the window (17.2 W against its twin's 19.3 W) and its off-rail high. Leaving it out gives 0.60 mΩ
[0.06, 1.14] at 99% (NEITHER), with the upper edge unchanged at 0.68 pJ. So a conduction term of about 0.5–0.6 mΩ,
about 0.3 pJ of the row, is probably there; it is not resolved at the registered 99%, and by the plan's rms test it is
not material in any form.

**The governor operation, as registered** ([`CHANGE-RECORD.md`](CHANGE-RECORD.md) has the full log). Originals 65 W /
65 °C by the two RAM GETs (20:49:33); TDP **65 → 0** at 20:55:16.593, read back 0 / 65 at .616, the watchdog armed first;
arm A's 40 launches all read 600 MHz (the abort never fired); **0 → 65** at 21:11:41.131, read back 65 / 65 at .155; the
watchdog read `release` and exited at 21:11:41; the return burst above; closing read 21:19:48: **65 W / 65 °C**,
`low_power`, 600 MHz, module uptime 6 d 7 h 6 m (no reset); an independent read at 21:20:22 agreed. Highest board
reading 69.59 W (an arm-B heater), 50.6 W in a kept launch, die mean at most 59 °C. 30.29 card-minutes in the session,
about 31 with the gate reads, the smoke and the closing read.

**What ran.** 79 of 80 launches (the first gate, from a 46 °C die at the session's start, was not reached in 8 heater
launches), 78 kept (one arm-B launch dropped by S1: its clock moved after reaching 800 MHz), 3 flagged `below_floor`:
the gate's code launches when the rails settle even if the die has just dipped under the floor, and those three read
51 °C (the registration's wording, "heated again first", describes the case where it dips before the rails settle).
The 8 s settling rung ran this time (settling ratios minion 0.959, SRAM 0.965, NoC 0.965). The block's drift: board
0.351 W/°C, minion −0.020, SRAM 0.022, NoC 0.026, so 92% of the board's drift is off the three rails. Arm A's idle minion
rail read 6.75 W at a 52 °C launch (E77: 7.11 W at 55 °C). By amendment A1, no residency was read.

**What it changes.** The regulator split that E77 left open is now bounded by a registered run: the regulators'
conduction share of the rail ledger's 0.875 pJ row is **at most 0.69 pJ at 99%** in the registered model's total-current
form, about 0.33 pJ at the point estimate, and not resolved from zero at 99% (post hoc, probably there at about 0.3 pJ).
E77's post hoc 0.30 pJ bound does not replicate as a bound. The operating-point step (4.26 W minion, 1.76 W SRAM before
any work) and the f·V² per-hart transfer are now registered results on this card. This bears on the Horace hub's Levels
tab, stop 2 ("the card", its Missing column), its Next item 10 ("E77's regulator split"), and the final critic's item 13
(Q130(q)); the kinds page's [§ 11 list](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)
has no entry of its own for it at `fdcbcba2f34d` (see "What this answers").

## What this answers

**E77 ran on this card at 17:26–17:59 PST today and failed provisionally** ([E77's README](../2026-11-01-e77-rail-one-temperature/README.md),
results and corrections F1–F6). Its registered fit found no regulator conduction term (R_eff 0.62 mΩ, 99% [−0.49,
+1.73]) and did not bound the regulators' share of the rail ledger's 0.875 pJ row: the 99% upper edge is 1.06 pJ in the
registered model's total-current form. What broke it was found post hoc: on aifoundry2 the card idles at 600 MHz in both
arms, so arm B's deltas over its own pre-launch idle carry the 800 MHz operating point's step, +4.09 W on the minion
rail (99% [3.44, 4.75]) and +1.73 W on the SRAM rail ([1.69, 1.78]), with no work at all. With that step fitted (post
hoc), R_eff was 0.21 mΩ [−0.08, +0.50], an upper edge of 0.30 pJ, and the per-hart cost moved with f·V² (1.924
[1.81, 2.04] against 1.899). **E120 is the re-run E77's open issues ask for**, pre-registered on fresh data: arm B
referenced at its own operating point (the step fitted in the verdict, and measured on a floor rung), the ladder re-cut on
the measured costs, the residency reads and ring check fixed, the bound in the total-current form, and a gate both arms
reach.

**Where it sits.** The owner's ask of Sun 1 Nov 2026, about 19:05 PST, to confirm results while the cards are
available (Q134), with E120 named as E77 redesigned; the governor move is covered by his OK of about 12:30 PST the same
day for E77's operation, TDP 65 → 0 → 65 W on aifoundry2, under the lab's firmware field manual's gates and the firmware
maintainer's posted guidelines, read first. The regulator split is the Horace hub's Levels tab, stop 2 ("the card"),
Missing column, and its Next item 10 ("E77's regulator split"), and the final critic's item 13 (Q130(q): "not touched
until Sunday: E77"). The kinds page's [§ 11 list](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)
carries no entry of its own for it at `fdcbcba2f34d` (E77 is not yet folded into the page; its § 11 item 10 names a
separate regulators' share, the memory path's). *For the records lane:* E77's README calls the "Not touched: E77" entry
"the kinds page's § 11 list, item 13"; that entry is the final critic's item 13, and the page's item 13 is zeros'
transport.

## The question

The rail ledger puts **0.875 pJ** of a 5.783 pJ random fp32 multiply-add on "the regulators' delivery loss plus logic
in step with the rails" — one coefficient, 0.188 × minion W on aifoundry2. A switching regulator's conduction loss is
R·I² in its whole output current, so at a given output power it carries 1/V²; logic in step with the rail does not. The
same minion-rail watts delivered at two rail voltages separate them:

    offrail = a_m · Δm + c_B · [arm B] + R_eff · [((m₀ + Δm) / V)² − (m₀ / V₀)²]

with arm A at **600 MHz, about 518 mV** (the static TDP level at 0 pins the clock at the vmin-LUT floor; E72 and E77 made
this write on this card) and arm B at **800 MHz, about 618 mV** (the card's own governor, untouched). Δm is the minion
rail's rise over each launch's own pre-launch idle, m₀ and V₀ that idle's watts and voltage, V the window's. **c_B is
new:** it is the off-rail part of the 800 MHz operating point's step that a_m does not carry, the term E77's post hoc
fit added. Every launch passes one die gate, so both arms are launched and read at one temperature.

## What E120 changes from E77 (named before any data)

1. **Arm B referenced at its own operating point.** The verdict fit carries c_B (E77's post hoc form, registered). As a
   secondary, arm B's deltas are also taken over its own **floor rung** (32 harts, one per shire, at 800 MHz in the same
   pass), which measures the step instead of fitting it.
2. **The ladder re-cut on E77's measured costs** (`posthoc.json`: arm A −0.343 W + 21.05 mW per hart over the 600 MHz
   idle; arm B +3.752 W + 40.49 mW per hart over the same idle). The arms are matched on the minion rail's watts over the
   common idle, that is on the total minion-rail power in the window, which sets the regulator's current at each arm's
   voltage: arm A 992 / 736 / 512 / 256 harts, arm B 416 / 288 / 160 / 32 (predicted mismatches +0.3 / +1.7 / −2.0 /
   0.0%). E77-PLAN.md's per-hart f·V² transfer with no step (E77's 1,024/768/544/288 against 544/416/288/160) mismatched
   by 22–79%.
3. **The residency reads ask raw throttle states 1–3 only**: POWER_UP, POWER_DOWN and POWER_SAFE on this card's BL2
   0.22.0 (et-platform `836a4ab`, `device_mgmt_api_spec.h:280-285`). Raw 4 is no state there, and each read of it logged
   two service-processor errors and pushed two `SP Runtime Error` events to the host: all 22 of E77's (its F1). E119's
   session read states 1–3 only on this card tonight.
4. **The ring check counts only entries newer than the previous dump**, by service-processor timestamp
   (`tools/claims-v3/hpl/sptrace_full.py` `since`). E77's live check counted every throttle-up in the dump, stale ones
   included (its F3).
5. **The bound in the registered model's total-current form,** at arm A's measured idle minion rail (E77: 7.11 W at
   518 mV, where its departure 10 had assumed 15–16 W), with the literal R·(21/V_A)² beside it (E77's F2).
6. **The manual and the maintainer read by the run agent itself:** the field manual's four files in full (`AGENTS.md`,
   `docs/hosts-and-recovery.md`, `docs/runbook.md`, `templates/change-record.md`), about 20:29 PST; the maintainer's
   posts since 14:17 PST in `#community-lab` and in the owner's direct messages, read-only and masked, 20:30:50 PST
   (none), and again within minutes of the claim (the change record's live gates).
7. **A gate both arms reach.** E77's preheat to 59 °C sat at arm A's heater's plateau (about 58–59 °C at 600 MHz): arm A
   took 5.7 heater launches a launch, five gates and the settling rung were never reached, and the arms launched at 54.9
   and 53.7 °C, 1.2 °C apart. Here: heat until the die mean reads **≥ 56 °C**, then idle until it reads **≤ 55 °C**, at
   least 6 s after the last device process, with the minion rail settled by S2's test computed live; a die that falls
   below **52 °C** first is heated again (at most three times), then the launch goes ahead at its reading, flagged
   `below_floor`. E77's telemetry shows both arms falling to 53–55 °C during the rails' ~10 s settling.
8. **Five passes per arm of two rounds** (8 launches a pass, 80 in all) instead of three passes of three rounds (72).
   The unit of replication stays the pass. With five passes the 99% interval's multiplier is t(0.995, 4) = 4.604, against
   9.925 with three; E77's per-pass R_eff in the offset form had an SD of 0.05 mΩ (0.180 / 0.182 / 0.268), so the
   expected half-width is about 0.13 mΩ.
9. **E77's own binaries, by hash:** the heater and kernel (`build/sparsity_t2`, sha256 `7adadf4f1ce331cc…` and
   `990807f483cd57aa…`) and the no-PMIC-read telemetry tool `ettelem-e77` (`21e7bf77e631eb7e…`), as E77's
   `session.json` records them. The runner refuses to start if any differs. No telemetry voltage-register read, no
   firmware-revisions query, no statistics reset.
10. **The order:** B1 B2 | set TDP 0 | A1–A5, the 8 s settling rung | restore TDP 65 | the return burst | B3 B4 B5. Arm
    B's passes bracket arm A's in time; pass k of arm A pairs with pass k of arm B.
11. **Time:** no session starts after 22:30 PST; the runner stops at 23:25 PST, so that the restore and the closing read
    end by 23:30; at most 50 card-minutes in all (the session cuts at 46: arm B's first passes by 11 card-minutes, the
    move by 12, the restore by 33, arm B's last passes by 45; the restore and the return burst are never cut).

## Design

| rung | arm A: TDP 0, 600 MHz | predicted minion W over idle | arm B: own governor, 800 MHz | predicted minion W over idle | mismatch |
|---|---|---|---|---|---|
| 1 | 992 harts (31 per shire) | 20.54 | 416 (13 per shire) | 20.60 | +0.3% |
| 2 | 736 (23) | 15.15 | 288 (9) | 15.41 | +1.7% |
| 3 | 512 (16) | 10.43 | 160 (5) | 10.23 | −2.0% |
| 4 | 256 (8) | 5.05 | 32 (1): arm B's floor rung | 5.05 | 0.0% |

- **Workload:** `sparsity_host --test fma --type fp32 --values randn --shires 0xffffffff --per-shire N`, 4 s launches
  (`--seconds 4 --budget 5.5`), every one under `timeout 10` with `--stop-file`; aifoundry2's `build/sparsity_t2`.
- **Passes:** five per arm; a pass is two rounds, each round every rung once in a seeded shuffle
  (`random.Random("E120|<arm>|<pass>")`), so 8 launches a pass and 80 in all.
- **One session holding the card lock throughout**, after the gate reads (their own short hold) and a smoke (the sampler
  and one 2 s launch of 160 harts at the card's own settings, no write). The GO is committed before the first write: the
  session writes nothing until a file `GO` exists in its run directory (E77's amendment A2, kept), created after the GO
  commit is pushed; without it by 12 card-minutes there is no move.
- **The gate, before every launch:** above (change 7). Arm A's heater is 1,024 harts at 600 MHz (about 51 W); arm B's is
  768 harts at 800 MHz (E77's: its highest reading, 70.7 W, was this heater).
- **The settling rung:** one 8 s launch of arm A's top rung (992 harts) after arm A's passes, at the same gate.
- **The return burst:** one 4 s launch of arm B's top rung (416 harts) right after the restore; the clock must step up to
  800 MHz and the ring dumped after it must hold a throttle-up entry newer than the dump before it.
- **Telemetry:** 10 Hz, the **no-PMIC-read profile** (E77's `ettelem-e77`): the board power, the service processor's
  statistics (the rails and `sp.minion_mv`), the die sensors and the clocks.
- **The governor:** one field, `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL`, written only to the literal 0 and back to the
  literal 65 the gate read; the threshold is never written; every write is read back by the two RAM GETs; a deadline
  watchdog (E72's), armed before the first write, writes 65 back if the session has not released it within 75 min or by
  23:25 PST.
- **Aborts:** any single board reading ≥ 85.0 W; a die mean ≥ 72 °C; the die high-water latch ≥ 80 °C; while the TDP is
  0, any clock other than 600 MHz during a measurement launch; a DM rc ≠ 0 or a read-back mismatch; a device process
  outliving its `timeout 10`. Any abort restores the governor in the session's `finally`. The host kernel log is read
  before and after (read-only `dmesg`) and reported, not used as a live abort.
- **Etiquette:** lab `AGENT.md` §§ 4–5; before every launch another user's device process, a stale one of ours or the
  module's use count over its baseline ends the session. Another logged-in user blocks unless every one of their sessions
  has been idle 120 minutes or more (E111's amendment A1, in the runner, which fails closed); an idle login present is
  recorded as a dated departure under the owner's ruling of 1 Nov 2026 that an idle login does not block.

## Predictions (frozen in [`predictions.json`](../../../../tools/claims-v3/e120/predictions.json))

- **V, the verdict** (central footing, drift_split): per pass k, the 8 rung means of arm A pass k and arm B pass k, least
  squares in the form above (3 coefficients). **PASS** (the term exists): R_eff's 99% interval over the passes excludes 0
  AND the pooled fit's rms is at least 30% below the same fit without R_eff. **NEITHER**: the interval excludes 0 but the
  rms improves by less than 30% ("resolved, not a material term"). **FAIL**: the interval contains 0. E77's rules,
  unchanged. No size or sign of R_eff is predicted.
- **B, the bound:** the 21 W rail step's conduction loss at the interval's upper edge, in the total-current form at arm
  A's measured idle rail m₀ and window voltage, as pJ of the 0.875 pJ row (pJ = W × 0.875 / (0.188 × 21)): **BOUNDED
  BELOW THE ROW** if under 0.875 pJ, else not. The literal form beside it.
- **C1, E77's post hoc bound on fresh data:** PASS if E120's 99% upper edge is at or under 0.496 mΩ.
- **T1, the per-hart transfer:** per pass, each arm's line of rung-mean Δm against harts; slope B / slope A over
  (800/600)·(V_B/V_A)² from the pass's measured voltages; PASS if the 99% interval over passes contains 1 and the mean is
  within 5% of 1.
- **S1, the operating-point step on the minion rail** (arm B's intercept minus arm A's): PASS if the mean over passes
  lies in E77's post hoc 99% interval [3.44, 4.75] W. **S2, on the SRAM rail** (arm B's mean ΔSRAM minus arm A's): PASS if
  in [1.69, 1.78] W.
- **P2, the matching:** PASS if all four rung pairs are within 5% in measured minion watts over idle. The offset form
  compares the arms' lines and needs their ranges to overlap, not exact pairs, so a miss is reported and does not make
  the verdict provisional.
- **G, one temperature:** PASS if the arms' mean launch readings differ by at most 1 °C.
- **RING, the return check:** PASS if the burst reaches 800 MHz and its ring holds at least one fresh throttle-up.
- **K, the kernel log:** 0 `SP Runtime Error` events expected between the gate reads and the closing read (no raw-4
  reads); any event is reported and looked for in the rings.

## The pre-registered reading ([`reduce_e120.py`](../../../../tools/claims-v3/e120/reduce_e120.py))

- **Per launch, E77's reading unchanged** (its `reduce_e77.py`, copied verbatim): t0 = the first kernel record's start,
  t1 = the last record's end; windows idle [t0−2, t0−0.3] s, far [t0−5, t0−3], **the window [t1−1.5, t1]** (the median of
  the 10 Hz board samples and of the raw rail readings), body [t0+1.5, t1−0.2]; S1 (rc 0, every record ok, enough samples,
  arm A at 600 MHz throughout, arm B at 800 MHz in the window and never under it after its first 800 sample), S2 (the
  rail settled within 0.15 W, approach ≥ 6 s), S3 (board samples more than 2 W under their window's median dropped);
  deltas over the launch's own idle; the settling ratio from the 8 s rung, else the first-order model at τ 1.06 s
  (flagged); the footings uncorrected, **drift_split (central)**, board_only.
- **The fit:** V above, per pass and pooled; B, C1, T1, S1, S2, P2 and G as frozen. **Secondaries, no verdict:** the
  floor-referenced fit (arm B's deltas over its 32-hart floor rung in the same pass, arm A's over its idle, no offset; the
  conduction regressor between the floor's and the rung's total currents); the offset form with the published SRAM and
  NoC coefficients held (0.034, 0.291); with SRAM and NoC free; E77's registered form (no offset); the other two
  footings; launches flagged `below_floor` left out.

## Gates

The firmware field manual's gates, PASS / FAIL / UNKNOWN / N-A each with its evidence and time (UNKNOWN is never PASS),
are in [`CHANGE-RECORD.md`](CHANGE-RECORD.md), filled as the run goes and committed with its data. The desk gates (rule
8 at the version-matched source, the envelope, recovery) are filled there before this commit; the live gates (identity
by continuity, the originals, the LUT floor, exclusivity, the maintainer's newest posts) are filled at gate time and
committed as the GO before the first write.

## Files

| file | what |
|---|---|
| `tools/claims-v3/e120/run_e120.py` | the runner (`plan`, `gates`, `smoke`, `session`; `--dry` touches no device), E77's `run_e77.py` with the changes above |
| `tools/claims-v3/e120/protocol.json` | the design above, as the runner reads it |
| `tools/claims-v3/e120/predict_e120.py`, `predictions.json` | the frozen predictions and rules, from E77's committed `posthoc.json` |
| `tools/claims-v3/e120/reduce_e120.py` | the reduction |
| `tools/claims-v3/e120/e120.sh` | the stages on the box: hashes, look, kernlog, gates, smoke, go, status, wait |
| `tools/claims-v3/e120/crosscheck_e77.py`, `crosscheck_e77.txt` | the new fit code on E77's raw data against E77's committed numbers |
| `tools/claims-v3/e120/dry-reduce.txt` | the reduction of the dry session on the toy card |
| `CHANGE-RECORD.md` | the field manual's record for this governor move |
| `raw/` | *(after the run)* the run directory, as E77's |
| `results.json`, `reduce.txt` | *(after the run)* the registered reduction: `/usr/bin/python3 tools/claims-v3/e120/reduce_e120.py docs/reports/data/2026-11-01-e120-rail-redesign/raw --out .../results.json --text .../reduce.txt` |

**Dry run** (before this commit, no device): the gate reads, the smoke and a short session (three passes per arm of one
round) on the runner's toy card, which carries E77's measured per-hart costs and operating-point step and a 0.25 mΩ
conduction term: gates GO-able, smoke PASS, session exit 0 with the restore read back, the return burst stepping to
800 MHz, closing read 65 W / 65 °C; `reduce_e120.py` ran end to end on its output (`dry-reduce.txt`). Its numbers are
the toy's, not a prediction, and its drift_split rows are not physical: the toy's die tracks board power with a 1 s
node, so its block board slope reads 0.073 W/°C and E77's footing code (kept verbatim) divides by it. **The new fit code
is checked against E77 instead:** run on E77's committed raw data with E77's hart counts, `reduce_e120.py` reproduces
E77's post hoc offset fit pass by pass (0.180 / 0.182 / 0.268 mΩ, 99% [−0.076, +0.496]), the total-current bound
(1.37 W, 0.30 pJ; 0.18 pJ literal), E77's registered interval ([−0.487, +1.731]), the per-hart ratio (1.924) and the
two steps (4.09 W, 1.73 W): `crosscheck_e77.py` prints every comparison to `crosscheck_e77.txt` (all match).

## Amendments

**A1, Sun 1 Nov 2026, 20:52 PST** (after the gate reads and the smoke, while arm B's first pass runs; before the first
write and before any end-of-pass query): **E120 reads no throttle residency.** E77's `ettelem-e77`, which E120 must use
by hash (change 9), accepts raw states 2–6 only and checks every argument before it opens the management node: given
raw state 1 it refuses the whole call (rc 2), so states 2 and 3 are not read either, and nothing is sent to the card.
The gate reads at 20:49:02 PST returned an empty residency with rc 2, which is how this was found. Change 3's "raw
states 1–3" therefore reads none. No registered rule uses the residencies, the running session's protocol is not changed
(it was loaded at 20:49:31 PST), and the post-pass queries keep their ring dumps and governor reads. What it costs: no
new POWER_DOWN or POWER_SAFE reading (E77's lead for § 11 item 14 gets none from E120). What it gains: K now has no
residency read of any state as a possible cause of a kernel event. A re-run that wants POWER_UP needs a tool that
accepts raw 1 (E119's session read 1–3 on this card tonight with its own build).
