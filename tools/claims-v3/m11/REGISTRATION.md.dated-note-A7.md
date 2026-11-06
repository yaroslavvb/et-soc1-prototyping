# M11, dated amendment A7 (Fri 6 Nov 2026, before any M11 hold): A6 corrected. Its footing-law reading in one die coordinate, "settled" where A6 meant it, an hour's rest in the cool-hour plan, and what an earlier session can leave

*Beside [`REGISTRATION.md`](REGISTRATION.md) (`3c31a91d`) and its amendments A1-A6; it edits none of them. A6
([`REGISTRATION.md.dated-note-A6.md`](REGISTRATION.md.dated-note-A6.md), `95c75047`, committed 23:11:50 PST Thu 5 Nov 2026; its title's
"about 23:15 PST" overruns its own commit) governs every M11 session on aifoundry3 kitted after it. None has been kitted, and no M11 hold
has run. Written Fri 6 Nov 2026 (week 45), from about 00:00 PST until its commit, on the Intel, desk only (no card, no lab box), by the
lane fix-heat-q145a of Q145(a), round A, from an adversarial verifier's faults in A6. **It changes no gate line (G0-A6's 53.9 °C and
0.50 °C stand), stop, hold, plan pattern, HM reading, design or power.** It fixes one reported reading's coordinate (A7-1), narrows two
sentences to the evidence (A7-2, A7-3), asks the cool-hour plan for an hour's rest (A7-4) and gives the commit times (A7-5). The
history it reads is post hoc.*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Thu 5 Nov 2026 about 23:55 PST to Fri 6 Nov about
   00:05: public rows H07, H08, H12, H14, H25 and L10 (opaque pointers), and the map's row 6.
2. **Used.**
   - **The footing law's dated note 1** ([`FOOTING-LAW.md.dated-note-1.md`](../footing-law/FOOTING-LAW.md.dated-note-1.md) N1, with this
     amendment): FL5(c)'s reading in one coordinate, which A7-1 takes for A6-5.
   - **The floor study's committed tables** (`docs/reports/data/2026-11-05-q145a-a3-idle-floor/floors.json` and `floor_analysis.json`,
     `95c75047`): every November floor, its rest and both gates, read by that study's dated note 1 (`floor_note1.py`,
     `floor-note1.json`, committed with this amendment).
   - **M6's slowest pole** (`docs/reports/data/2026-11-02-q137m-model/m6.json`, `6a713a9f`: τ 1,500 s, weight 0.010), as A6 quotes it,
     set against the history (A7-3).
   - **E71's law** (the inventory's L10: E71's six October cycles with E44's three September ones, which the footing law's FL1 is built
     from, `c14e5f35`; E71's data `730cc8fc` and `8fab3404`). A6 checks this row but listed it neither as used nor as not used. Here it
     is the check of A6's loop gain at the floor: at the five raw-code floors, R × k by FL1 on the firmware reading (each floor less the
     study's mean offset, 0.94 °C) gives 0.223-0.246, against 0.228-0.253 by E97's law, the one A6 takes (`floor-note1.json` ›
     `loop_gain_at_raw_code_floors`; FL1's band starts at 52 °C, so floors below it are extrapolated by up to 2 °C). The card's own share
     of a floor change that A6 quotes holds by either law.
3. **Not used.** The host's NVMe composite as a gate, as in A6. An inlet thermometer, as in A6: none exists (his answer of Thu 5 Nov
   2026: *"We don't have a thermometer, so make do with what you can."*). aifoundry2 (E177): not built.
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code. No NDA-tier check is used, so there is no sha256
   line; no NDA-tier piece, name, verdict, ratio or figure is cited.

## A7-1. A6-5's footing-law check, in one die coordinate

A6-5 pooled the rests "by E97's method (… 0.5 °C bins of the 34-sensor mean with at least 20 samples), its slope at 52-58 °C against
FL1's and E97's law (0.280-0.351 W/°C)". FL1 is a law in the firmware's whole degree, and over E97's rests the 34-sensor mean reads
0.75-0.96 °C above that reading, so this compared two coordinates. **A6-5's check becomes FL5(c) as the footing law's dated note 1
(N1) fixes it.** The primary reads the rests per whole firmware degree inside FL1's band, against FL1 by the same estimator at the same
degrees and weights, PASS within ±0.02 W/°C. Beside it, the rests in E97's 0.5 °C bins of the 34-sensor mean are read against E97's
law by the same estimator. Both readings go in the session's scored output, and both are still reported, never a gate. A dry run on
E97's own rests (seen data) reads +0.009 W/°C: PASS. At 52-55 °C FL1's own two seasons differ by up to 0.045 W/°C, so a FAIL from rests
mostly there may be that spread rather than a moved law.

## A7-2. "Settled", where A6 meant it

A6's last paragraph says "On every committed November floor it would pass G0-A6, at any hour". That holds for the **settled** floors
only, rest at least an hour: 12 of 12 (`floor-note1.json` › `summary`). Of all 24 November floors, G0-A6 passes 22 and G0 as
registered 21. Two floors taken 40-41 minutes after our own sessions would be stopped by A6-1 before the smoke:
- Sun 1 Nov 00:35: firmware 54 °C, est 54.94 °C, rest 0.68 h;
- Mon 2 Nov 16:43: firmware 53 °C, est 53.94 °C, rest 0.66 h.

Both meet the runbook's 40-minute rest rule, which A6 keeps and A7 keeps: A6-1 stops such a card within seconds of the session's
start, before any launch. The sentence reads instead: *"On every settled (at least an hour's rest) committed November floor it would
pass G0-A6, at any hour; launched before noon it would also pass G0 as registered and run the cool pattern."*

## A7-3. What an earlier session can leave (post hoc)

A6 quotes M6's slowest pole twice: "about 0.05 °C at most at 40 minutes" (Builds on) and "with at most 0.05 °C left of any earlier run"
(why F0). The history disagrees for two of the fifteen sessions that followed a rest under 0.75 h and have a settled session (rest at
least 2 h) within 6 h of them (`floor-note1.json` › `excess_by_rest_bin`). They are the two floors of A7-2, at firmware 54 and 53 °C,
3-4 °C above the lowest such neighbour (51 and 49 °C); M6's pole leaves 0.050 °C at 40 minutes. The other thirteen read at most 1 °C
above, and so do the three sessions after 0.75-2 h of rest that have such a neighbour (whole degrees). The cause is not identified: a
slower or larger mode than M6's four poles, or something not in the committed records. So the 0.05 °C bound holds for a settled card,
not at the runbook's 40-minute rest, and F0 reads the room only on a settled card. On an unsettled one only A6-1's stop at 53.9 °C
guards the reading (A6-2's 0.50 °C line catches a card that warms during R0, not one still cooling from an earlier run), and a card that
is unsettled but under 53.9 °C would run with its floor raised by the tail. Hence A7-4.

## A7-4. The cool-hour plan asks for an hour's rest

The plan (a plan, not a gate) reads: launch M11's next aifoundry3 session **before 12:00 PST where the day allows, and at least an hour
after our last session on the card ended**. Every settled November floor came after 1.84 h or more of rest. The history holds three
sessions after 0.75-2 h of rest with a settled neighbour, none more than 1 °C above it, so an hour is the shortest rest the records
support, on thin evidence; more is better. The runbook's 40-minute rule stays the gate.

## A7-5. Times

A6 was committed at 23:11:50 PST Thu 5 Nov 2026; its title says "about 23:15". The floor study's README, committed with it, says it was
written "about 22:55-23:20".

## Files (`SHA256SUMS-a7`)

This amendment, and the floor study's dated note 1 with its script and output
(`docs/reports/data/2026-11-05-q145a-a3-idle-floor/README.md.dated-note-1.md`, `floor_note1.py`, `floor-note1.json`, `floor-note1.txt`).

SPDX-License-Identifier: Apache-2.0
