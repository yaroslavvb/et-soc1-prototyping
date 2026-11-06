# The governor's idle-reset dips as a counted session term (DT): registration (Q145(b), MAP step 1)

*Registered Fri 6 Nov 2026 (week 45), about 02:40 PST, on the Intel, desk only. No card, lab box or device was touched for it. It is
committed before its post hoc re-scores of E173-E175 (a separate data directory, committed after this file) and before any session it
governs. No run number is taken: the first blind test is "number to be assigned" (section 6). It answers the pool-8 card day critic's
rank 9 ("the governor's mid-burst dips as a session term, registered first") and MAP step 1 of the Q145 stock-take. E165's README
(line 60), E173's (lines 54, 75, 85) and E175's (lines 59, 108) call the dips "a session term no model of the bits predicts". This file
makes them a counted term.*

## Builds on

1. **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 02:10 PST. Public rows read: P01, P02, P03, P04, P08, L11, L22, H07,
   H08, H10, H19, H23, H24, H26, H28. The ids are opaque pointers into a private inventory.
2. **Used** (each piece, what is taken, its source):
   - **E170's dated note A2-2** (lab `6147a9c7`, Wed 4 Nov 16:08 PST; [`../e170/E170.md.dated-note-A2.md`](../e170/E170.md.dated-note-A2.md)
     § A2-2). Taken: the mechanism, named for E165's mid-burst dips: the once-a-second heartbeat landing in a gap between kernels. Also
     taken: that a fall inside the burst window lowers that burst's board too.
   - **E114 § 3** ([`2026-11-01-e114-card0-replicates/README.md`](../../../docs/reports/data/2026-11-01-e114-card0-replicates/README.md)
     § 3, `posthoc/lattice.txt`; `a4a4bf3e`, `d93f7a1c`). Taken: card 0's period (1000.0191 ms, residuals within 0.55 ms over 1,110
     beats), and that the climb waits for a heartbeat: the first 800 MHz reading comes 0.389 s after the first lattice point inside a
     kernel (median of 35 starts).
   - **E100**: its registration [`../e100/README.md`](../e100/README.md) (`5e12c4bd`) and its data
     [`2026-11-01-e100-idle-reset/`](../../../docs/reports/data/2026-11-01-e100-idle-reset/README.md) (`f9fe3f57`, corrections `9b93e3e9`).
     Taken:
     - the test: all five rules PASS; 39 of 39 heartbeats in a gap fell, 0 of 234 inside a kernel;
     - the zone: 2.0 ms where the host's mean gap is 1.29 ms, so the zone is the stamp gap plus 0.7 ms;
     - the band's construction: w from 1.3 to 2.5 ms, Poisson ends at the heartbeats exposed;
     - the fall's length: D4's median of 1.101 s;
     - the N arm, one kernel per process: 0 falls in 126 heartbeats inside kernels;
     - that the fitted periods are tie-breaks over about 0.01 ms (its README, under the rules' table).
   - **Q132(g)'s heartbeat lattice** ([`2026-11-01-q132-governor-desk/`](../../../docs/reports/data/2026-11-01-q132-governor-desk/README.md)
     § b; `ir-lattice.txt`, `ir-gaps.txt`, `13de3994`). Taken:
     - the per-session periods on the host clock: aifoundry2's E64 1000.0089, E69 1000.0088, E80 1000.0102, E83 1000.0098 and E87
       1000.0105 ms; card 0's E84 1000.0186 ms;
     - the climb from the first heartbeat inside a kernel, aifoundry2: the first 700 MHz reading at 0.09-0.14 s and the first 800 MHz
       reading at 0.29-0.32 s (medians, five sessions); card 0 (E84): 0.113 and 0.383 s;
     - a fall's length: 1.10 s at 600 MHz, 1.30 s to the first 800 MHz reading;
     - the count's form: 25 falls against 23.5 expected, a 2 ms zone over 11,781 boundaries.
   - **The public heartbeat and idle path, `aifoundry-org/et-platform` at `836a4ab60`** (the lab's clone `external/et-platform`). Taken:
     the chain of section 1, line by line:
     - `device-minion-runtime/src/MasterMinion/src/services/sp_iface.c:76-100` and `:1085`;
     - `.../workers/kw.c:1915-1930`, `:938`, `:1653`;
     - `device-bootloaders/src/ServiceProcessorBL2/rtos_task/command_dispatcher.c:476`;
     - `.../services/thermal_pwr_mgmt.c:3110-3124` and `:864-926`;
     - `.../rtos_task/dm_task.c:200-276`.
   - **M9's aifoundry2 relation** ([`2026-11-04-q140l-a2-session-terms/m9_a2.json`](../../../docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json)
     `relation`, sha256 `cc6fbccc4b63fa80…`, `5b98bd5c`). Taken: the board's levels L(f) = B(f) + c s(f) at 600, 700 and 800 MHz for a
     tile's D. That is how the dipped launches are carried into Bp. Nothing is refitted.
   - **The registered reduction** (`tools/claims-v3/kspeed/reduce_kspeed.py` `burst_extra`, sha256 `10fee8c1…`; `hpl/reduce_hpl.py`
     `run_metrics`, `e49b6c1b…`). Taken: a pass's clock and board are the sampler's means from 1.5 s after the process start to the
     work's end. That window is what a dip costs a pass.
   - **E58** (`docs/findings/05-claims.md` lines 770-773; `03-experiments.md` lines 2274-2280). Taken: the board reading is published
     one SP pass late (0.24 s, E64's pass; [`2026-10-23-e64-horace-power-limit/README.md`](../../../docs/reports/data/2026-10-23-e64-horace-power-limit/README.md)
     line 103).
   - **The check against an earlier measurement of the same quantity at the same operating point.** The quantity is the dip count:
     falls per session on aifoundry2 and card 0, at the 800 MHz cap, with the sparsity host's back-to-back launches. The earlier
     measurements are E100's and Q132(g)'s committed counts. The post hoc study committed after this file runs DT-N's own formula on
     two of them:
     - E100's committed session, arm by arm: A0, A5, A20, A100 and N. Each arm is set against E100's registered prediction and its
       observed falls.
     - Q132(g)'s statement: 25 falls against 23.5 expected.

     That is the form section 3 of the stock-take's rule asks for: "a dip count against E100's lattice and E170's note A2-2". The
     committed SP rings and launch records of E173 (`ed8b5761`, 167 ring files), E174 (`e5206b5b`, 128) and E175 (`9f13d7c3`, 128),
     read with [`../hpl/sptrace_full.py`](../hpl/sptrace_full.py) (sha256 `58dd8b04…`), are used **only** in that post hoc study. No
     parameter of this term is set from them.
3. **Not used:**
   - **The POWER_IDLE ring records as the phase's calibration.** Each one sits about ±19 ms (sd) from the lattice on the SP's own tick
     (E100: R 0.9926 over 193 records; Q132(g) item 1: p10-p90 residuals of −18 to +18 ms in four of six sessions, down to −78 ms in
     two), against zones 3-4 ms wide. Their tick must also be
     mapped to the host clock. They serve only as a check: the period on the SP tick, and a POWER_IDLE record behind each fall (the
     post hoc study). The falls themselves place the lattice to about ±1 ms (section 3).
   - **E85's statistics-reset trigger.** Superseded by E100's D5: no rise was seen with the reset.
   - **G4's fitted dip fraction, T_G** (`2026-11-04-q140m-m9` and G4's own files). It is a post hoc share fitted for the large-GEMM
     model, not a count per gap. G4 keeps it.
   - **`surface_hpl.py`'s governor filter** (tau 1.3 s, line 108). The term carries the dip on top of the model's predicted clock; it
     does not refit the governor model. The filter set from source is the meter note's (MAP row 16).
   - **P04, the SP PLL 4 bypass and relock on every frequency change.** Its stall is inside the sampled clock this term predicts, and
     is not modelled apart (MAP row 39).
   - **aifoundry3 and aifoundry1's card 1.** They run pinned at 600 MHz (TDP 0 W, or a clock that never leaves 600 MHz), so no fall
     can show there. The term is zero on those cards.
   - **E165's and E160's dipped passes** (pool 6 and 7 on aifoundry2). They set no parameter and are not re-scored here. Re-scoring
     them is owed to a records lane, if wanted.
4. **Tiers:** public only. Every piece is the lab's committed data or public code at a pinned commit.
5. **Readiness:** a verifier checks this block against the inventory and the cited commits, and checks this file against (4).

## 1. The mechanism and its timing

**The chain, in the public source at `836a4ab60`:**
1. The Master Minion arms a periodic heartbeat (`sp_iface.c:1085`, `SP_IFACE_MM_HEARTBEAT_INTERVAL(100)` software-timer ticks). Each
   one sends `event.state = KW_Get_Kernel_State()`, a snapshot of that instant (`sp_iface.c:76-100`).
2. The snapshot reads BUSY only if a kernel slot reads `KERNEL_STATE_IN_USE` (`kw.c:1915-1930`). A slot becomes IN_USE only after the
   launch's multicast is acknowledged (`:938`), and is freed at completion (`:1653`). Between two kernels the snapshot reads IDLE.
3. The SP passes the state on (`command_dispatcher.c:476`). On a busy-to-idle edge, `Thermal_Pwr_Mgmt_Update_MM_State` notifies
   POWER_IDLE at once, with no debounce (`thermal_pwr_mgmt.c:3110-3124`). That sets the 600 MHz boot point.
4. The power branch steps the clock only while the state is not idle, one point per SP pass (`:864-926`, called once per pass from
   `dm_task.c:267`).

**Timing, from the committed measurements** (the source fixes the order of events, not their times):
- **The period.** The source arms the heartbeat as 100 software-timer ticks (`sp_iface.c:1085`). How long a tick lasts depends on
  the PU timer's clock and on how often `SW_Timer_Processing` runs (`sw_timer.c:113-142`); `sw_timer.h:24-28` notes that its 1 MHz is
  the silicon timer clock and that other platforms differ. So the period in time is taken from the committed measurements, not read
  from the source.
  - On the host clock: 1000.0088-1000.0105 ms on aifoundry2 (Q132(g), five sessions; E100 1000.007, a tie-break) and
    1000.0186-1000.0191 ms on card 0 (E84, E114).
  - On the SP's own tick, the rings' POWER_IDLE records line up at 0.999994-1.000004 s (Q132(g) item 1; E100).
  - Between sessions the period moves by about 1-2 ppm. That is about ±2-4 ms over a 36-minute session, against zones 3-4 ms wide. So
    a session's period is re-fitted on its own falls (section 3), and the count alone (DT-N) needs no phase.
- **A fall** lasts one heartbeat plus a pass. The clock sits at 600 MHz from the heartbeat in the gap until the next heartbeat inside a
  kernel, one period P later, then waits for the next pass. So it sits at 600 MHz for P + c7 and at 700 MHz for c8 − c7, where c7 and
  c8 are the first 700 and 800 MHz readings after a heartbeat inside a kernel. On aifoundry2 that is 1.12 s and 0.19 s. Measured:
  E100's D4 median 1.101 s; Q132(g) 1.10 s and 1.30 s.
- **The climb at a process start** waits for the first heartbeat inside a kernel: E114 § 3 measured 0.389 s from it to the first
  800 MHz reading on card 0, and Q132(g) measured 0.29-0.32 s on aifoundry2. The first launch starts about 0.15 s after the process's
  own start stamp: the median is 146-148 ms in E173-E175's launch records. That is a structural read, not an outcome. So a normal climb
  ends by 0.15 + P/1000 + c8 ≈ 1.46 s on aifoundry2, before the reduction's window opens at 1.5 s. If the first heartbeat after the
  first launch lands in a gap, the state is already IDLE: nothing falls, but the climb waits one more period and ends inside the window.
  This is the **late climb**. The term predicts it with the same lattice.
- **Which gaps can show a fall.** A gap qualifies when all four of these hold:
  1. it lies inside one process (between two of its launches);
  2. its zone opens at least one period after the process's first launch. Before that the state is still IDLE, and a heartbeat in a
     gap delays the climb instead;
  3. the clock is above the boot point when it opens: the launch before it read at least 0.65 GHz on the kernel's own counters;
  4. it lies outside a low episode. After a fall the next heartbeat is one period later, and condition 3 excludes the episode's 600 MHz
     launches.

  The zone of gap i runs from the earlier launch's end stamp, less b, to the later launch's start stamp, plus a. The stamps are whole
  milliseconds, so each is read at its middle (+0.5 ms). a + b = 0.7 ms (E100), placed after the start stamp (a = 0.7 ms, b = 0),
  because the slot turns IN_USE only after the launch's multicast is acknowledged.
- **What a dip costs a pass.** The reduction's window runs from 1.5 s after the process start to its end (about 4.95 s in E173-E175's
  records). A fall inside it costs (f − 600)(P + c7) + (f − 700)⁺(c8 − c7) MHz·s, divided by the window. With f = 800 MHz that is
  about 50 MHz. The board falls with it, by L(f) − L(600) and L(f) − L(700) watts for the same times, shifted by the meter's one-pass
  lag.

## 2. The parameters, frozen (the constants at the top of [`dipterm.py`](dipterm.py))

| constant | value | source |
|---|---|---|
| `PERIOD_PRIOR_MS` aifoundry2 | 1000.0095 ms, sd 0.0015 ms (1.5 ppm) | Q132(g) `ir-lattice.txt`: E64, E69, E80, E83, E87 (1000.0088-1000.0105); E100 (1000.007, a tie-break) |
| `PERIOD_PRIOR_MS` card 0 | 1000.0190 ms, sd 0.0010 ms | Q132(g) E84 1000.0186; E114 `posthoc/lattice.txt` 1000.0191 |
| `CLIMB_S` aifoundry2 (c7, c8) | 0.12, 0.31 s | Q132(g) `ir-gaps.txt` B: first 700 / 800 readings from the first heartbeat inside a kernel |
| `CLIMB_S` card 0 | 0.11, 0.39 s | Q132(g) E84 (0.113 / 0.383 s); E114 `posthoc/lattice.txt` (0.389 s) |
| `A_MS`, `B_MS` (the zone) | 0.7, 0.0 ms after the start and before the end stamp | E100: a 2.0 ms zone at a 1.29 ms host gap; `kw.c:938` |
| `DELTA_BAND_MS` (DT-N's band) | 0.0-1.2 ms | E100's w of 1.3-2.5 ms |
| `SIGMA_Z_MS` | 0.3 ms | the whole-ms stamp's blur (uniform ±0.5 ms) |
| `FALL_GHZ`, `ABOVE_GHZ` | ≤ 0.62 after ≥ 0.65 GHz | Q132(g)'s kernel rule (0.55-0.62 after ≥ 0.79), widened to ≥ 0.65 for governed bursts |
| `BURST_FROM_S` | 1.5 s | `reduce_kspeed.py` `BURST_FROM_S` |
| `BOARD_LAG_S` | 0.24 s | E58, published one SP pass late; E64's pass 0.24 s |
| `OFF_LATTICE_MS` | 20 ms | about 6 sd of a lattice point extrapolated over a session |
| `MC_DRAWS`, `SEED` | 400, 145 | |
| `SENS_LINE`, `PPV_LINE` (DT-L) | 0.6, 0.5 | set from the self-test's synthetic sessions (section 5), before any re-score |

## 3. The term

**DT-N, the count (primary).** For one session, take the eligible gaps of section 1. Then

> **expected falls = (the sum of their stamp gaps + n × δ) / P0**, with δ = a + b = 0.7 ms central.

The band runs from the lower Poisson 2.5% point at δ = 0.0 ms to the upper 97.5% point at δ = 1.2 ms, the band E100's D1 registered.
The observed falls are the eligible gaps whose next launch reads ≤ 0.62 GHz (each episode counts once).
- **PASS:** the count lies in the band. The gaps alone set how many bursts dip.
- **FAIL low:** something else holds the state BUSY across gaps.
- **FAIL high:** the falls do not come from the gaps.

The count needs no phase. It is scored alone.

**The lattice's phase is an in-session calibration, registered as such** (like term a's session scale, read from the session's own
anchors).
- **Which bursts dip** is set by where a free-running one-second timer falls against each burst's gaps. That needs the lattice's phase
  to about a millisecond, and the period to about a ppm over a session.
- **Both are fitted on the session's own falls, sequentially.** Every burst is predicted from the falls of the bursts before it,
  never its own. The fit is a weighted least squares of the falls' zone centres on whole beats, each with sd √(w²/12 + 0.3²) ms, plus
  the card's period prior. A fall more than 20 ms from the lattice so far is reported as off the lattice and not used.
- **The session's first fall can never be predicted.** It is the calibration's first input. Bursts before it are predicted with the
  phase unknown.
- **No pass is set aside for having calibrated the lattice.** Every pass is scored with the prediction it had before it ran, so the
  calibration selects nothing on the outcome.

**The arms** (`dipterm.predict`). Each arm gives a pass's expected clock deficit and board deficit in its window, by Monte Carlo
(400 draws) over the lattice through the state machine of section 1. The same state machine also gives the late climbs.
- **none:** the model's clock alone, the session's own registered rule;
- **count:** the phase uniform for each burst and the period from the prior, so only the exposure carries information;
- **seq:** the in-session calibration, **the term's primary**;
- **oracle:** the lattice fitted on all of the session's falls. It is **post hoc by construction** and is never a prediction.

**DT-L, the calibration's predictions (secondary).** Take the eligible gaps of the bursts after the session's first fall. A gap is
predicted to fall when the seq arm gives it P ≥ 0.5.
- **PASS** if sensitivity ≥ 0.6 and positive predictive value ≥ 0.5.
- **NOT SCORED** with fewer than 3 later falls.

**The clock rules on the predicted clock.** A tile's predicted clock is its M10 clock, as the session's frozen predictor gives it, less
the mean over its counted passes of the seq arm's expected deficit. The session's own rule is then re-scored on its own line:
- **DT-F2:** aifoundry2's pinned clock (P8-A2-F2's and E175-A2-F2's lines);
- **DT-C0F:** card 0's pinned clock (P8-C0-F's line);
- **DT-G:** aifoundry2's governed clock (rms ≤ 4.0 MHz and |mean| ≤ 2.0 MHz).

Beside each, the same rule is reported with arm none (the committed verdict, reproduced to 0.001 or the scorer refuses) and arm count.

**DT-Bp, the dipped launches carried into the board.** A tile's predicted board is its M10 board less the mean of the seq arm's
expected board deficit. Each low segment costs L(f_ref) − L(600) or L(f_ref) − L(700) watts. L comes from M9's aifoundry2 relation
with c = c_zeros[t] + g·D for the tile's frozen M10 D (the session's level shift cancels). The result is scored on the session's own Bp
line (|mean| ≤ 0.5 W and rms ≤ 1.0 W). Card 0's board is not carried here, because its relation (E170's card term) is not imported.
That is owed.

**One approximation, stated.** A governed burst's deficit is taken against its predicted dither mean. The power arm's catch-up after a
dip is not modelled: after a dip the filtered power is lower and the clock may hold 800 MHz a little longer. So a governed burst's
deficit is over-stated by at most that catch-up.

**One-kernel sessions** (kit v4's default; section 46 item 5 of the round's brief). The option is committed after this file, as new
files in `tools/claims-v3/kitv4-onekernel/`. A burst run as one kernel has no gap inside it:
- the exposure is zero, so DT-N's band is [0, 0];
- the first heartbeat after the launch lies inside the kernel, unless it falls in the first 0.7 ms, so no climb is late;
- **DT-K:** any fall inside a one-kernel burst refutes the chain, in E100's D2 form.

## 4. The scorer, and what a session needs

[`score_dipterm.py`](score_dipterm.py) takes:
- the session directory (`launches.jsonl.gz`, the harness's per-launch records);
- the run's own registered `results.json` (its `run_rows`, its per-tile M10 predictions under `score.reported.tiles`, its rules' lines
  under `score.rules`);
- the card (`a2` or `c0`);
- the clock rule and its set;
- on aifoundry2, the board rule, the frozen predictions file (for each tile's M10 D) and `m9_a2.json`.

It refuses unless arm none reproduces the committed rule's rms and mean to 0.001 W or MHz. Its own self-test is
`python3 dipterm.py --selftest`, whose output is committed as [`selftest-dipterm.txt`](selftest-dipterm.txt).

## 5. Power and forecast (registered, information only)

The self-test's synthetic sessions (T4, T7) are built in E173's shape: 160 bursts of 16 launches of 0.366 s with 2.6-3.4 ms stamp gaps.
- **CHAIN:** falls from a lattice whose true period is 0.8 ppm off the prior, through the state machine.
- **RANDOM:** the same falls at random eligible gaps.

Results, 24 sessions of each:
- **DT-N** passes in 24 of 24 CHAIN sessions.
- **DT-L** passes in 19 of 24 CHAIN sessions (2 NOT SCORED) and 0 of 24 RANDOM sessions.
- **The window clock's rms per pass** (CHAIN): 10.27 MHz with no term, 10.14 MHz with the count alone, 6.29 MHz with the in-session
  calibration.

So the count alone cannot remove a clock rule's dip miss: it spreads the expected loss over every pass. Only the phase can say which
passes dipped, and the session's first fall always stays unpredicted.

**What I expect, frozen so it can be wrong:**
- On the next governed session that keeps the gaps, DT-N PASSES.
- DT-L PASSES, or is NOT SCORED if the session has fewer than four falls.
- DT-F2 (or DT-G) improves on the model alone by about a third of its dip-borne rms, but does not reach the residue without the dips:
  the first fall and the late climbs before it stay.

## 6. The first blind test

**The next governed session that keeps the gaps** (number to be assigned): an aifoundry2 replicate of E175's governed line (the
evening critic's ranks 5 and 8), or card 0's next governed session in E174's form. Its registration names this commit's
`dipterm.py` and `score_dipterm.py` by sha256 (`SHA256SUMS`) and scores:
- DT-N as primary;
- DT-L;
- DT-F2 or DT-C0F, and DT-G, on that session's own registered lines;
- DT-Bp on aifoundry2.

A session run in kit v4's one-kernel form scores DT-K and DT-N's zero exposure only. Nothing here asks for card time. That needs his
go, as always.

## 7. What this does not change

No committed registration, prediction, data file, scorer or hash list is edited. M10, M9, rule E and the frozen pool-8 and E175
predictions are unchanged. The re-scores of E173, E174 and E175 are post hoc, whatever is registered here, because their data existed
first. They are in `docs/reports/data/2026-11-06-q145b-dips-posthoc/`, committed after this file.

## Files

| file | what |
|---|---|
| `REGISTRATION.md` | this file |
| [`dipterm.py`](dipterm.py) | the term: the session's gaps, DT-N, the lattice, the state machine, the arms, DT-L, the board's levels, the self-test |
| [`score_dipterm.py`](score_dipterm.py) | the scorer for one governed session |
| [`selftest-dipterm.txt`](selftest-dipterm.txt) | `python3 -I -B dipterm.py --selftest` (T1-T7; the forecast of section 5) |
| [`SHA256SUMS`](SHA256SUMS) | the hash list of the four files above |

SPDX-License-Identifier: Apache-2.0
