# M11, dated amendment A6 (Thu 5 Nov 2026, about 23:15 PST, before any M11 hold): G0 referred to the card's own floor, so a warm room no longer refuses a settled card, and a cool-hour plan for the next session

*Beside [`REGISTRATION.md`](REGISTRATION.md) (`3c31a91d`) and its amendments A1-A5; it edits none of them. Written on the Intel, desk only
(no card, no lab box), by the lane heat-q145a of Q145(a), round A (the stock-take's step 4; the evening critic's rank 3). It answers the
kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **items 9 and 8** (heat over
minutes) and E176's G0 refusal ([E176's data README](../../../docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/README.md), `5db7bcf7`,
with its dated note 1, `127a4e85`). **No M11 hold has run**: E176 was refused at G0 and scored nothing, and no later session exists. This
amendment governs every M11 session on aifoundry3 registered or kitted after this commit. Its evidence is the post hoc floor study
[`docs/reports/data/2026-11-05-q145a-a3-idle-floor/`](../../../docs/reports/data/2026-11-05-q145a-a3-idle-floor/README.md), committed with it
(reads of committed files only).*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Thu 5 Nov 2026 about 22:20 PST: public rows H07, H08,
   H12, H14, H25 and L10 (opaque pointers), and the map's row 6.
2. **Used.**
   - **E89's 34 raw codes and E97's conversion** (`code_to_c`, as `tools/claims-v3/e176/smoke_gate_e176.py`, `03582d2f`, has it): every
     34-sensor floor here. *Check:* the five sessions whose sampler carried the codes (E89, E144, E154, E166, E176) read 0.77-1.20 °C above
     the firmware's whole degree at their first sample (mean 0.94), and E176's floor recomputes to its committed 53.202 °C.
   - **The committed floors:** the first sample of every committed aifoundry3 session, 22 Sep - 5 Nov 2026 (43 sessions, 415 distinct passes),
     E154's 50.982 °C, E166's 51.838 °C, E171's firmware 49 °C and E176's 53.202 °C among them; and the smoke residues at G0's window
     (R0's committed `room` mark less the session's first sample): E154 0.428, E166 0.087, E176 0.380 °C.
   - **E97's idle law** (`heat_q138t.py` line 167, `f5473428`) and **Q138(t)'s R** (`model-q138t.json` › `a3`, 0.8695 °C per board W): the
     loop gain at the floor, g = R × k(T) = 0.21-0.25 at 49-53 °C, which is the card's own share of a floor change. The footing law
     ([`FOOTING-LAW.md`](../footing-law/FOOTING-LAW.md) FL2, `c14e5f35`) keeps this law for the loop.
   - **M6's slowest pole** (`docs/reports/data/2026-11-02-q137m-model/m6.json` › `heat.step_response`, `6a713a9f`: τ 1,500 s, weight 0.010):
     what an earlier run leaves after a rest, about 0.05 °C at most at 40 minutes for a 25 °C plateau.
   - **The room proxies the lab recorded:** E97's host sensors (`room.txt`, `18e7683e`: the NVMe at 36.71 °C over R0) and E176's host
     windows (`room-rule/hostwin-base.out`, `5db7bcf7`: 38.85 °C, whole kelvins). *Check:* between them the floor moved 2.64 °C and the NVMe
     2.14 °C, 1.24 against the loop's predicted 1 / (1 − g) = 1.31.
   - **M11's exact planner** (`design_power_heat_v2.py` › `plan_exact`, `f49b7ddd`, the A1 plan): every hold's planned plateau and
     in-launch peak at a given room, and the registered envelope over G0's admitted rooms (the highest: H_E's cool pattern at 51.5 °C,
     peak 68.51 °C, plateau 66.10 °C; A1's table, `REGISTRATION.md.dated-note-1.md` lines 84-96).
   - **The registered gate and stops**, kept: G0 (`REGISTRATION.md` line 188; E176's kit README lines 79 and 95, `03582d2f`), the stops of
     REGISTRATION.md lines 207-212, the runbook's rest rule (`tools/claims-v3/q143k-runbook/s11_a3_session_q143k.sh` lines 32-42, `92a1b27f`:
     at least 40 minutes since our last session end on the card), and M11's scorer, which reads the kit's `start_gate` mark
     (`score_m11_v2.py` lines 338-340, `ebdbb35c`) and needs no change.
3. **Not used.**
   - An inlet thermometer: it waits on his word.
   - The host's NVMe composite as a gate: it reads whole kelvins, and the lab holds two readings of it; it is reported, never a gate.
     E176's lane's room rule (the NVMe at least 0.5 °C under a baseline) is superseded by this gate.
   - Raw codes for the kinds sessions (E171 and every kinds harness): their samplers carried none, so their floors are the firmware's whole
     degree plus 0.94 °C, labelled "est".
   - aifoundry2 (E177): not built; this amendment covers aifoundry3 only.
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code. No NDA-tier check is used, so there is no sha256
   line; no NDA-tier piece, name, verdict, ratio or figure is cited.

## What the floor is, and why G0 refused E176 (post hoc, from the floor study)

A die at rest sits where its idle draw's heat balances the room's: T = T_room + R × P_idle(T), and P_idle rises with T (the leakage law),
so a change of room moves the floor by 1 / (1 − g) of itself. Against the week's coolest raw-code floor (E144, Mon 2 Nov 22:37, 50.888 °C, 32 minutes after E141, so at most 0.07 °C of tail),
E176's 53.202 °C (Thu 5 Nov 17:21, 4 h 46 min after E171) was **+2.31 °C: +1.92 °C of room and +0.39 °C of the card's own leakage
answering it** (its board idle 0.45 W higher), with no tail left (M6's slowest pole: under 10⁻⁴ °C after that rest). E166's 51.838 °C was
+0.95 (+0.78 room, +0.17 the card's own), E89's 51.773 °C +0.89 (+0.78, +0.11). On these three, the card's own share reads 0.12-0.18 by
the board's measured idle draw, against the law's loop gain of 0.23-0.24 (the board's idle level also wanders about ±0.2 W between
sessions). **By the hour**, the settled November floors (rest at least an hour) read
firmware 48-49 °C before noon (est 48.9-49.9 °C, five sessions), 50.9-51.8 °C from noon to 17:00 (four) and 50.9-53.2 °C after 17:00
(three); in September and October some reached 53.9-55.9 °C (est). **So G0's fixed 53.0 °C line, read after the smoke's residue (up to
0.43 °C), refused a settled card for a warm room**: E176's floor alone was over it, and no rest could have passed it that evening.

## The amended gate, G0-A6 (replaces G0 for every M11 session on aifoundry3 kitted after this commit)

- **A6-1, the floor F0.** The 34-sensor mean over the first 3 s of the session's first sampled pass (the smoke's, before its first launch),
  read after the runbook's rest rule (at least 40 minutes since our last session end on the card, unchanged), and written to a `floor` mark
  with the firmware reading and the board W. **If F0 is above 53.9 °C, the session ends before the smoke's first launch** (exit 7, no
  hold), since R0 could not then pass.
- **A6-2, the gate after R0** (R0 unchanged: 5 minutes; its room the 34-sensor mean over its last 120 s): **holds run only if R0's room is
  at or under 53.9 °C, and R0's room less F0 is at or under 0.50 °C.** Else exit 7 and no hold, as G0. The `start_gate` mark records both
  readings, both lines and `passed`, which the scorer reads.
- **A6-3, H_E's pattern:** the cool pattern at a room at or under 51.5 °C (unchanged), the warm one in (51.5, 53.9] °C.
- **A6-4, unchanged:** every stop (no launch at a firmware reading ≥ 70 °C; a hold ends at ≥ 72 °C or ≥ 65 W; the pass ends at ≥ 74 °C),
  the plan, the holds and their order, every HM reading's definition, A1-A5's design and power, and the card-minute envelope (76).
- **A6-5, reported beside, never a gate:** the host's NVMe composite and coretemp at the session's start and end (read-only sysfs, as
  E176's lane read them); the room's drift over R0 (as registered); and the footing law's blind check
  ([`FOOTING-LAW.md`](../footing-law/FOOTING-LAW.md) FL5(c)): the session's rests after its holds pooled by E97's method (rule F, 20 s
  after each rest's start; 0.5 °C bins of the 34-sensor mean with at least 20 samples), its slope at 52-58 °C against FL1's and E97's law
  (0.280-0.351 W/°C), PASS within ±0.02 W/°C.

**Why these lines, mechanically.**
- **53.9 °C** is the warmest room on a 0.1 °C grid at which every planned in-launch peak and plateau of M11's exact planner stays at or
  under the registered envelope over G0's admitted rooms: H_E's warm pattern peaks at **68.44 °C** with a 65.97 °C plateau at 53.9 °C,
  against **68.51 / 66.10 °C** for its cool pattern at 51.5 °C; at 54.0 °C the peak would read 68.56 (crossing at 53.96 °C); every other
  hold peaks at or under 65.72 °C. So the registered margin, 3.49 °C under the 72 °C hold line, holds at every room A6 admits, and the
  plateau goes no further past E97's law's top (64.8 °C) than the registration already went.
- **0.50 °C** keeps G0's "settled": it refuses a card still carrying more than a smoke's heat (an earlier run, or a room that warmed during
  R0); the committed smoke residues at G0's window are 0.09-0.43 °C.
- **F0 is the room as the card itself sees it**, read on the 34 codes before any launch, with at most 0.05 °C left of any earlier run: a
  known start without an inlet thermometer.

**What G0-A6 would have done on the committed history** (post hoc, each settled floor + the largest committed residue, 0.43 °C): G0 as
registered passes 17 of 26 settled sessions since 22 Sep and 11 of 12 in November (E176's evening refused); G0-A6 passes 21 of 26 and 12 of
12 in November, E176 among them (R0's room 53.58 °C, residue 0.38 °C: PASS, the warm pattern, H_E's planned peak 68.07 °C). Five
September-October sessions with firmware floors of 53-55 °C are refused by both.

## The cool-hour plan for the next session (a plan, not a gate)

Launch M11's next aifoundry3 session **before 12:00 PST** where the day allows. Every settled November floor before noon read firmware
48-49 °C (est 48.9-49.9 °C), so G0-A6 passes with more than 3.5 °C to spare and the **cool pattern** runs: E144's own H_H, at the plan's
first room (51.2 °C), which HM-E144 reads best. An afternoon or evening launch is allowed under G0-A6 and will most likely run the warm
pattern.

## What M11's next session needs, and when it could pass

It is M11's first scored session (E176 scored nothing): a run number (the orchestrator's); a kit ported from E176's that carries A6
(`run_e176.py`'s `ROOM_MAX_C` and `WARM_HI` to 53.9, the `floor` mark, the residue test and the pre-smoke stop), with E176's dated note 2's
runbook fixes (step 11's rest rule must skip a V3_DRY session's "session end"; the scorer runs after the gates) and the two code-verifier
faults recorded; dmcmd_audit GO; a dry pass; a readiness critic; then his go for a card day and fresh lab approvals. About 75 card-minutes
and 1.75 h of wall time on aifoundry3. **On every committed November floor it would pass G0-A6, at any hour; launched before noon it would
also pass G0 as registered and run the cool pattern.**

SPDX-License-Identifier: Apache-2.0
