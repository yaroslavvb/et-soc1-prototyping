# Dated note 4 beside REGISTRATION.md (Fri 6 Nov 2026, week 45): amendment A1, the fall rule set against the governor's own steps, before any session it governs

*This note sits beside [`REGISTRATION.md`](REGISTRATION.md) and its dated notes [1](REGISTRATION.md.dated-note-1.md),
[2](REGISTRATION.md.dated-note-2.md) and [3](REGISTRATION.md.dated-note-3.md), and edits none of them: `dipterm.py`,
`score_dipterm.py`, `score_dipterm_v2.py`, `score_dipterm_v3.py` and the hash lists `SHA256SUMS`, `SHA256SUMS-1` and
`SHA256SUMS-2` stay as committed (`7a099fb9`, `fe4fdf92`, `17c18e89`), byte for byte. It amends the registered rules for every
session scored after it. No session the term governs has run. Its time is its commit's, as dated note 3 asks of the records.
Desk only: no card, lab box or device was touched.*

**Why.** The registered fall rule (a launch at 0.62 GHz or less straight after one at 0.65 GHz or more, `dipterm.py` line 53)
was widened from Q132(g)'s rule (0.55-0.62 GHz after 0.79 GHz or more) so that a governed burst's dither counts. That also
counts the governor's own power and thermal steps to 600 MHz, and card 0's 300 MHz alarm state, as idle-reset falls. The
registration's Builds-on block promised a check of DT-N's formula against Q132(g)'s count, and the post hoc study did not run
it. Run post hoc by the lane's verifier, the registered rule reads 188 falls against 27.3 expected on Q132(g)'s six sessions,
and 5 of 6 FAIL; at Q132(g)'s own rule all six PASS. The registered calibration also takes the session's first fall with no
check at all. The check is re-run and committed in the post hoc study's dated note 1, after this note.

## Builds on

1. **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 03:50 PST. Public rows read: P01, P02, P03, P04, P08, L11,
   L22, H08, H10, H19, H23, H24, H26, H28. The ids are opaque pointers into a private inventory.
2. **Used** (each piece, what is taken, its source):
   - **Q132(g)'s kernel rule** ([`2026-11-01-q132-governor-desk/README.md`](../../../docs/reports/data/2026-11-01-q132-governor-desk/README.md),
     "What the data show"; `13de3994`). Taken: a fall lands at 0.55-0.62 GHz, straight after a launch at 0.79 GHz or more. Its
     own exclusions say why: E83's `BURST-06-fp32-randn_large-r1` was left out because "its kernel before ran at 0.63 GHz,
     inside the power arm's dither", and E84's two 300 MHz cases "are the alarm". Its count, 25 falls against 23.5 expected
     over 11,781 boundaries at 800 MHz, is the earlier measurement this rule is checked against (post hoc study, dated note 1).
   - **The public governor, `aifoundry-org/et-platform` at `836a4ab60`.** `thermal_pwr_mgmt.c:864-926`: the power and thermal
     arms move one operating point a pass; `:3110-3124`: POWER_IDLE sets the boot point at once on a busy-to-idle edge. Taken:
     straight after a launch at full clock, only the idle reset can reach the boot point within one gap of 1-3 ms.
   - **The SP ring's power-status record** (`device-api/include/management-api/device_mgmt_api_spec.h:280-283` at `836a4ab60`:
     throttle states 0 POWER_IDLE, 1 POWER_UP, 2 POWER_DOWN, 3 POWER_SAFE) **and its reader**
     [`../hpl/sptrace_full.py`](../hpl/sptrace_full.py) (sha256 `58dd8b04…`), with its target MHz and `since()`. Taken: a
     step to the boot point or lower for any reason but the idle reset shows as a record with a state other than 0 and a target
     of 620 MHz or less (a power step, a thermal step, or card 0's alarm at 300 MHz). A dump that does not reach back to the
     previous dump may have lost records: the ring holds about 63-72 entries, and a governed run can write more.
   - **Card 0's alarm** ([`docs/findings/14-card-behaviour.md`](../../../docs/findings/14-card-behaviour.md) lines 236-240 and
     464-468; E84). Taken: the alarm sets a 300 MHz safe state, so its launches read under 0.55 GHz.
   - **Card 0's climb, re-read** by [`climb_c0_a1.py`](climb_c0_a1.py) ([`climb-c0-a1.txt`](climb-c0-a1.txt)) from the committed
     10 Hz telemetry of E114 ([`2026-11-01-e114-card0-replicates/`](../../../docs/reports/data/2026-11-01-e114-card0-replicates/README.md),
     `a4a4bf3e`, corrections `d93f7a1c`) and E174 (`e5206b5b`). **The check against earlier measurements of the same
     quantity:** E114 alone gives c7 0.064 s and c8 0.265 s, E174 alone 0.062 and 0.312, pooled (8 falls that recover inside
     their process) 0.062 and 0.262. At a process start, E114's start table (`posthoc/lattice.txt` item 4) reads 0.389 s to the
     first 800 MHz reading over 35 starts, and Q132(g)'s E84 0.383 s: the registered 0.39 s. The same reading of aifoundry2's
     E100, E173 and E175 gives c7 0.101 and c8 0.301 s (54 falls), against the registered 0.12 and 0.31.
   - **aifoundry2's SP pass**: findings 14 line 794 (under the 10 Hz sampler a new `board_w` every 156 ms on aifoundry2, 263 ms on
     aifoundry3; E41); `docs/findings/05-claims.md` line 770 (E58: `board_avg_w` current, the rails one pass late) and line 773
     (aifoundry3's pass 0.255 s); `dm_task.c:222` and `:267` at `836a4ab60` (the average is refreshed and checked in the same
     pass). Taken: the sensitivity lag of A1-6. The pass is read again on E173-E175's own telemetry in the post hoc study's
     dated note 1.
   - **The registered term, scorer v2 and dated note 2's K_GC**, imported unchanged.
3. **Not used:**
   - **A POWER_IDLE record by each fall as its confirmation** (the verifier's first form). Two committed cases show why it
     cannot confirm every idle reset. An idle reset that comes while the power arm already holds 600 MHz writes no POWER_IDLE
     record: E175's `BURST-68` shows three POWER_DOWN records to 600 MHz and no POWER_IDLE before its end-of-process one,
     though its fall sits 0.17 ms from the lattice of the session's other three falls. And a fall whose low episode runs past
     the process end leaves one POWER_IDLE record, as a run with no fall does (E173's `BURST-91`, E174's `BURST-05` and
     `BURST-89`). A1-2 uses the absence of any other step in a complete dump instead.
   - **A time map from the SP's tick to the host clock.** The POWER_IDLE records place a lattice point to about ±12-14 ms (p10-p90;
     the post hoc study, result 5), against zones 3-4 ms wide.
   - **aifoundry2's climb, re-read.** Its registered values over-state a fall's 600 MHz part by about 0.02 s (1.12 against 1.10 s),
     and the pinned falls' costs matched to about 1 MHz (the post hoc study, result 4). It stays as registered.
   - **E165's and E160's sessions.** Still not re-scored; owed to a records lane, as registered.
4. **Tiers:** public only. Every piece is the lab's committed data or public code at a pinned commit.
5. **Readiness:** a verifier checks this block against the inventory and the cited commits, and this file against (4).

**This rule was chosen after looking.** The verifier's Q132(g) check and E173-E175's committed rings were read before it was
written, so on all of those sessions its readings are **post hoc**. Its first blind test is the next governed session.

## The amendment

**A1-1, the fall rule.** A **fall** is an eligible gap whose next launch reads **0.55-0.62 GHz** (the boot point). A gap is
**eligible** when all of these hold:
- it is structurally eligible as registered: inside one process, its zone opening at least one heartbeat period after the
  process's first launch, with a stamp gap of 0 ms or more;
- its process is in scope (A1-3);
- the launch before it read **0.79 GHz or more** (full clock), **or** it read 0.65 GHz or more and the process is **clear**
  (A1-2).

DT-N's expected count and band keep the registered formula over these gaps. A fall the registered rule counted and A1 does not is
reported with its reason. The registered rule also counted a fall at a gap that was not eligible (inside the process's first
heartbeat period, where no idle edge can fall); A1 counts falls at eligible gaps only.

**A1-2, a clear process, and the calibration's first fall.** A process is **clear** when its run's SP ring dump exists, reaches
back to the previous run's dump (its oldest entry is no newer than the previous dump's newest), holds power-status records, and
holds none, among its entries newer than the previous dump, with a throttle state other than 0 and a target of 620 MHz or less.
- **The calibration's first fall must lie in a clear process.** It is the one fall no lattice can check. A fall before it in a
  process that is not clear (counted by the full-clock path) is counted in DT-N and not used as the first input.
- Later falls are checked against the lattice so far at 20 ms, as registered, wherever they lie.

**A1-3, the scope.** DT-N and DT-L score the processes of the session's registered burst block(s) only ("BURST" in E173-E175's
form). A process that holds an **alarm step** (a launch under 0.55 GHz straight after one at 0.65 GHz or more, or a POWER_SAFE
record among its run's new entries) is out of scope: it is reported, never counted. So the count holds no governor or alarm step
to 600 MHz or below.

**A1-4, the Monte Carlo.** Each arm runs **8 batches of 500 draws** a process (seeds 145-152; 4,000 draws, against the
registered 400). A rule's figure is read on the pooled deficits. Its **Monte Carlo standard error** is the sd of the 8 batch
figures over √8, and is reported beside every figure. A verdict whose figure lies within two standard errors of its line is
reported as near the line.

**A1-5, card 0's climb.** After a fall, card 0's 600 MHz part lasts P + c7 and its 700 MHz part c8 − c7, with **c7 0.062 s and
c8 0.262 s** (pooled; Builds on, Used). At a process start card 0 keeps the registered 0.11 and 0.39 s. aifoundry2 is unchanged.
The term's state machine is otherwise the registered one (self-test T4: with the registered rule, climb, draws and seed it
reproduces `dipterm.predict` draw for draw).

**A1-6, the board's lag, a sensitivity.** Beside the registered 0.24 s, the seq arm's board deficit is also reported with the
meter lag at **0.17 s** (about one aifoundry2 SP pass under the 10 Hz sampler). This is the arm **seq-lag**: REPORTED, never a
verdict. The lag moves only a low segment that crosses the window's edges.

**Dated note 2's seq-gc** stays REPORTED and runs on A1's calibration.

## What a governed session scores from now on

Its registration names `score_dipterm_v4.py` and [`SHA256SUMS-4`](SHA256SUMS-4), and scores:
- **DT-N (A1)** as primary. DT-N is a **rate check**: it tests how many falls the gaps allow, not which bursts dip. Random
  placements of the same falls pass it too, and at 4-8 expected falls its band is wide (1-14 at E173's 7.0 expected).
- **DT-L (A1)**, which is what tests the phase.
- **DT-F2 or DT-C0F, DT-G and DT-Bp** on the seq arm, each with its Monte Carlo standard error.
- **seq-gc and seq-lag**, reported only.

A session in kit v4's one-kernel form scores DT-K and DT-N's zero exposure, as registered.

**What I expect, frozen so it can be wrong:** on the next governed session that keeps the gaps, A1's DT-N passes and holds no
fall from a process with a step to the boot point; DT-L passes, or is NOT SCORED with fewer than three later falls.

## What this changes, and what it does not

- No committed registration, data file, scorer or hash list is edited. M10, M9, rule E and every frozen prediction are unchanged.
- A1's rules replace the registered fall rule, scope, first calibration fall, draws and card 0's fall climb for every session
  scored after this note. The registered term and its arms stay committed and can still be run as they were.
- Re-scoring E173, E174 and E175 under A1 is post hoc. It is in the post hoc study's dated note 1, committed after this note. E174
  is in sample for A1-5, because its falls enter card 0's pooled climb.

## Files

| file | what |
|---|---|
| `REGISTRATION.md.dated-note-4.md` | this note, amendment A1 |
| [`dipterm_a1.py`](dipterm_a1.py) | A1's rules around the registered `dipterm.py` (imported unchanged): the ring's status, the fall rule, the scope, the calibration, the batched arms, DT-L; `--selftest` T1-T9 |
| [`score_dipterm_v4.py`](score_dipterm_v4.py) | the scorer v4: v2's tile means and reproduction check, on A1's rules, with each figure's Monte Carlo standard error; seq-gc and seq-lag reported |
| [`climb_c0_a1.py`](climb_c0_a1.py) | A1-5's reading of the committed falls' 10 Hz telemetry (card 0's E114 and E174; aifoundry2's E100, E173, E175 as a check) |
| [`climb-c0-a1.txt`](climb-c0-a1.txt) | its output: `python3 -I -B climb_c0_a1.py --lab <the lab tree>` |
| [`selftest-dipterm-a1.txt`](selftest-dipterm-a1.txt) | `python3 -I -B dipterm_a1.py --selftest` |
| [`SHA256SUMS-4`](SHA256SUMS-4) | the files above, plus every file `SHA256SUMS-2` lists and `SHA256SUMS-2` itself, all unchanged |

SPDX-License-Identifier: Apache-2.0
