# M11, dated amendment A8 (Fri 6 Nov 2026, before any M11 hold): the smoke's residue at G0-A6's window predicted at 0.41 °C, 0.09 °C under A6-2's 0.50 °C line, so that line is referred to the predicted residue

*Beside [`REGISTRATION.md`](REGISTRATION.md) (`3c31a91d`) and its amendments A1-A7; it edits none of them. Written on the Intel, desk only (no
card, no lab box, no device command), by the lane kit-e181 of E181's kit round, from about 01:20 PST Fri 6 Nov 2026 until its commit. E181 is
M11's session 2 on aifoundry3 card 0 (the orchestrator's number); it is M11's first scored session, since E176 was refused at G0 and scored
nothing ([E176's data README](../../../docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/README.md), `5db7bcf7`). **No M11 hold has run,
and no E181 datum exists.** A8 answers round A's critic (its `m11_session2` item 3: "a prediction of this smoke's residue at R0's window
(M6's step response on the planned smoke) ... if the prediction sits within about 0.1 C of it, a dated amendment before any hold (a longer R0,
or the line referred to the predicted residue)") for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **items 9 and 8** (heat over minutes). It
governs E181 and every later M11 session on aifoundry3 kitted after this commit. Its evidence is [`residue_a8.py`](residue_a8.py), committed
with it, which reads committed files only; its output is [`residue-a8.json`](residue-a8.json) and [`residue-a8.txt`](residue-a8.txt) (the run of
01:36:03-01:36:08 PST, re-run byte for byte). Every session it reads has been seen, so every figure below is post hoc, except the rule (A8-3)
and the amended test (A8-4), which are registered here before any datum they govern.*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Fri 6 Nov 2026 about 01:30 PST: public rows H07, H08, H12,
   H14, H25 and L10 (opaque pointers), and the map's row 6 (aifoundry3's idle floor), as A6 and A7 read them.
2. **Used.**
   - **M6's step response** (the inventory's H12; `docs/reports/data/2026-11-02-q137m-model/m6.json` › `heat`, `6a713a9f`): F(t) = 1 − Σ wᵢ
     e^(−t/τᵢ), τ = 1.005, 15.98, 138.2 and 1,500 s, w = 0.148, 0.010, 0.832 and 0.010, and aifoundry3's steady 0.9 °C per board W, frozen;
     driven by a measured board trace, open loop, as Q138(t)'s arm A drives its chain.
   - **The four committed sessions with a smoke pass and then a fixed R0**, each read from its own committed telemetry (34 raw codes, E97's
     `code_to_c`) and marks: E144 (`ca979517`, R0 8 min), E154 (`d037d82a`), E166 (`179549ce`) and E176 (`5db7bcf7`), each R0 5 min (the
     inventory's H08 and H25).
   - **A6's definitions**, unchanged (`95c75047`): F0 = the 34-sensor mean over the first 3 s of the smoke pass's samples (A6-1); R0's room =
     the 34-sensor mean over R0's last 120 s; the residue = R0's room less F0 (A6-2). A7 (`65a93fbb`), unchanged.
   - **E176's smoke and timeline:** `tools/claims-v3/e176/run_e176.py` (`03582d2f`) `DESIGNS["smoke"]`, `stoptests()` and its hold rule ("a
     hold does not start with less than its length + 30 s left"); E176's committed session log (`5db7bcf7`: T0 17:21:15 PST, the measured
     pass's R0 79.251 s later, its deadline T0 + 4,500 s). E181's kit runs this smoke unchanged, so E176's committed trace is the planned smoke's.
   - **E97's idle law** (`heat_q138t.py` line 167, `f5473428`; the inventory's H08) and **Q138(t)'s R** (`model-q138t.json` › `a3`, 0.8695 °C per
     board W, `f5473428`; H14): the floor dependence of the R0 part (A8-1) and the loop gain g = R k(F0) (A8-6).
   - *The same quantity at the same operating point, earlier:* the floor study's committed residues (`95c75047`,
     `docs/reports/data/2026-11-05-q145a-a3-idle-floor/floor_analysis.json` › `smoke_residues_c`: E154 0.428, E166 0.087, E176 0.380 °C, each
     against the session's first sample). With A6-1's 3 s F0 the script reads 0.422, 0.085 and 0.383 °C (the first sample and the 3 s mean
     differ by 0.002-0.006 °C). E176's own residue, the same smoke on the same card, reads 0.383 °C against M6's 0.414 °C.
3. **Not used.**
   - E89 and E97 as checks: E97's R0 is slope-ended 2.3 h after its smoke, and E89's measured pass holds no rest marks, so neither has A6-2's
     window after a smoke.
   - Q138(t)'s chain as the predictor: it reads only the measured pass, so it does not see the smoke (A8-6). M6's step response is the critic's
     named predictor.
   - E144's longer windows (6-8 minutes) in the rule: every session is read at the 300 s window, the one A6-2 reads; E144's are reported (A8-2).
   - An inlet thermometer: none exists (his answer of Thu 5 Nov 2026: *"We don't have a thermometer, so make do with what you can."*). The
     host's NVMe composite: whole kelvins (A6).
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code. No NDA-tier check is used, so there is no sha256 line;
   no NDA-tier piece, name, verdict, ratio or figure is cited.

## A8-1. The prediction (post hoc reads; frozen here)

M6's step response on the planned smoke (E176's committed smoke pass and R0; the input is the board's excess over P0, the board's mean over
F0's 3 s), read over R0's last 120 s: **the predicted residue is 0.414 °C** (`residue-a8.json` › `E181.predicted_residue_C`, 0.41436). Of it, 0.237 °C is the
smoke pass's own heat and 0.177 °C the R0 part, the board's leakage excess while the die cools. **That is 0.086 °C under A6-2's 0.50 °C line:
within about 0.1 °C of it, so this amendment is written.**

| F0 (°C) | 49.4 (a settled morning floor, est) | 51.5 | 53.2 (E176's) | 53.9 (A6-1's top) |
|---|---|---|---|---|
| predicted residue, the R0 part scaled by E97's k(F0) (°C) | 0.386 | 0.402 | 0.414 | 0.420 |

## A8-2. The prediction checked on the committed sessions (post hoc)

| session | R0 | F0 (°C) | measured residue at the 300 s window (°C) | M6 (°C) | miss (°C) |
|---|---|---|---|---|---|
| E144, Mon 2 Nov 22:37 | 8 min | 50.884 | 0.168 | 0.266 | −0.098 |
| E154, Tue 3 Nov 17:53 | 5 min | 50.987 | 0.422 | 0.366 | +0.057 |
| E166, Wed 4 Nov 14:20 | 5 min | 51.839 | 0.085 | 0.332 | −0.247 |
| E176, Thu 5 Nov 17:21 | 5 min | 53.199 | 0.383 | 0.414 | −0.031 |

- **The misses** (measured less predicted): mean −0.080 °C, sd 0.128 °C, rms 0.137 °C (n 4). So E181's reading is expected near **0.33 °C,
  with an sd of 0.13 °C** (0.414 + −0.080).
- **They are the room, not the smoke:** E144's 8-minute R0 shows it. Its residue rose while M6's fell: 0.168, 0.187, 0.271 and 0.336 °C at
  the 300, 360, 420 and 480 s windows, against M6's 0.266, 0.204, 0.171 and 0.154 (misses −0.098, −0.017, +0.099, +0.181 °C). Over minutes the
  room moves the residue by ±0.2 °C, in both directions (E166 −0.25 °C).

## A8-3. The rule between the two remedies (A8-R, registered before any datum)

**A8 takes the remedy with the smaller chance of refusing a settled card**, estimated from the committed misses at the 300 s window alone, as a
normal with their mean and sd: P = 1 − Φ((line − predicted residue − mean) / sd). Within 0.5 percentage points it takes (a), which changes no gate.
The empirical count of misses over each margin is printed beside. Why this criterion: A6-2's line is a "settled" check, not a stop. A refusal
costs the session (75 card-minutes of plan and the day's window). A card it wrongly passes is guarded by every stop, by A6-1 and by the room
line, all unchanged (A8-5). And by A7-3 the line cannot catch an earlier run's tail anyway, since a card still cooling reads a smaller residue.

| remedy | what it is | predicted residue (°C) | its line | P(refusing a settled card) | committed misses over the margin |
|---|---|---|---|---|---|
| none (A6 as registered) | R0 5 min | 0.414 | residue ≤ 0.50 | 9.8% | 0 of 4 |
| (a) a longer R0 | **6 min**: the longest whole minute that leaves L2's start 60 s or more inside run_e176.py's hold rule on E176's committed timeline (70.7 s spare; 7 min leaves 10.7 s, 8 min −49.3 s); R5 falls from 150 s to 101 s (the deadline's cut); every other rest and hold unchanged | 0.314 (0.317 with the board's excess held) | residue ≤ 0.50 | 1.9% (2.0%) | 0 of 4 |
| (b) the line referred to the predicted residue | R0 5 min | 0.414 | residue − 0.414 ≤ 0.50 | 3 × 10⁻⁶ | 0 of 4 |

**A8-R reads (b).**

## A8-4. The amended residue test (replaces A6-2's second clause for E181 and every M11 aifoundry3 session kitted after this commit)

- **Holds run only if R0's room is at or under 53.9 °C (A6-2's first clause, unchanged), and R0's room less F0 less 0.414 °C is at or under
  0.50 °C.** Equivalently, the residue is at or under 0.914 °C. Else exit 7 and no hold, as G0.
- **0.414 °C is frozen here:** the prediction of A8-1 at E176's own floor. It is the same for every session, not re-predicted on the box from the
  session's own trace. The floor dependence (0.386-0.420 °C) is under 0.03 °C, beside the 0.50 °C line.
- **What the line now refuses:** a card that warms during R0 by more than 0.50 °C beyond the smoke's predicted heat, about 5 °C an hour. The
  committed misses reach +0.18 °C (E144 at 8 minutes). This is the purpose A6 gave the line ("a room that warmed during R0"). Its size, 0.50 °C,
  is unchanged; it is now measured from F0 plus the smoke's predicted residue rather than from F0.
- **The `start_gate` mark records it all:** the room and its 53.9 °C line, F0 (from the smoke pass's `floor` mark), the residue, the frozen
  0.414 °C, the residue less it, the 0.50 °C line, and `passed`. M11's scorer reads `passed`, as A6 says.

## A8-5. What does not change

A6-1 (F0, its `floor` mark and the stop before the smoke's first launch above 53.9 °C); A6-2's first clause (R0's room at most 53.9 °C);
A6-3 (H_E's cool pattern at a room at or under 51.5 °C, the warm one in (51.5, 53.9]); A6-4 (every stop: no launch at a firmware reading of
70 °C or more, a hold ends at 72 °C or 65 W, the pass at 74 °C; the plan, the holds and their order, R0's 5 minutes, every HM reading's
definition, A1-A5's design and power, the 76-card-minute envelope); A6-5 with A7-1 (FL5(c) in both coordinates, reported, never a gate);
A7-4 (the cool-hour plan: before 12:00 PST, and at least an hour after our last session on the card; the runbook's 40-minute rule is the
gate). The card-minutes stay about 75.

## A8-6. Disclosed, not resolved here: the chain does not see the smoke's residue at H_E's anchor (an estimate)

M11's readings (REGISTRATION.md § 1) run Q138(t)'s chain on **the measured pass alone** (`score_m11.py` line 150: `SE.a3_load([pass_dir])`).
The smoke is the pass before it, so its heat is not in the chain's input. The chain's anchor over R0's last 120 s absorbs the smoke's residue as
an offset. By H_E's plateau window that residue has decayed (M6: to about 0.01 °C), and the chain sees only the share its leakage carries, g =
R k(F0) ≈ 0.21-0.25. So H_E's miss e carries about **−(1 − g) × the residue at its anchor** (`residue-a8.json` › `H_E_anchor_estimate`; an
estimate, not verified on committed holds):

| session | R0 | M6's residue at the first hold's anchor (°C) | estimated part of that hold's e (°C) |
|---|---|---|---|
| E144 (H_H, the hold HM-E144 compares with) | 8 min | 0.154 | −0.12 |
| E154 / E166 / E176 | 5 min | 0.366 / 0.332 / 0.414 | −0.28 / −0.25 / −0.31 |
| E181 as kitted | 5 min | 0.386 (at a 49.4 °C floor) | −0.30 |
| E181 with remedy (a) | 6 min | about 0.29 | −0.23 |

- **It bears on HM-E144** (|e| / R ≤ 1.5%, about 0.21 °C at H_E's 14 °C): E181's H_E would carry about 0.18 °C more of it than E144's H_H did.
  It also bears on HM-CAL, whose pair line runs through H_E, and on HM-HE.
- **Which way:** it pushes H_E's e negative; it does not move Z, L1, S or L2, whose rests run inside the measured pass.
- **Why A8 does not resolve it:** A8-R's criterion is the false refusal it was written for, and remedy (a) would remove only about a quarter of
  this. Two routes would remove it, each a further amendment before any hold, and each the owner's or the registration's call:
  - the chain read over the smoke and the measured pass together (a change to § 1's reading);
  - an 8-minute R0, as E144 had, with the cap raised to about 78-79 card-minutes (run_e176.py's hold rule: L2 starts 49 s too late on E176's
    timeline at the 76-minute cap).

  **It is named for the readiness critic.**

## Files (`SHA256SUMS-a8`)

This amendment; [`residue_a8.py`](residue_a8.py) (standard library; `python3 -B tools/claims-v3/m11/residue_a8.py . <out.json>` from the lab
clone's top, about 5 s); its output [`residue-a8.json`](residue-a8.json) (with the sha256 of every file it read) and printout
[`residue-a8.txt`](residue-a8.txt).

## Compute

The Intel, one job through the round's local slot (01:36:03-01:36:08 PST, then a re-run, byte for byte), after scratch development runs of a
few seconds each. No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0
