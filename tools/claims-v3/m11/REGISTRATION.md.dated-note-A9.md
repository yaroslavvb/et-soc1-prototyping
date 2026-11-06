# M11, dated amendment A9 (Fri 6 Nov 2026, before any E181 datum): A8-6 read by a reported arm, the chain run over the smoke and the measured pass together, beside the registered reading; no verdict, gate, stop, box file or card-minute changes

*Beside [`REGISTRATION.md`](REGISTRATION.md) (`3c31a91d`) and its amendments A1-A8; it edits none of them. Written on the Intel, desk only (no
card, no lab box, no device command), by the lane fix-e181 of E181's kit round, from about 03:10 PST Fri 6 Nov 2026 until its commit. E181 is
M11's session 2 on aifoundry3 card 0; it is kitted (`33cdccf6`), **not run: no M11 hold has run, and no E181 datum exists.** A9 answers the
kit verifier's major fault (A8-6, disclosed by A8 `80b92990` and named for the readiness critic): M11's readings run Q138(t)'s chain on the
measured pass alone, so the smoke's heat still leaving the die at H_E's anchor is not in the chain's input. It serves the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **items 9 and 8** (heat over minutes). It
governs E181 and every later M11 aifoundry3 session scored by M11's scorer v4 or later. Its evidence is [`a9_posthoc.py`](a9_posthoc.py),
committed with it: it reads committed files only, and every session it reads has been seen, so every figure below is post hoc. The arm
(A9-1) is the function `two_pass()` in that file, which the scorer v4 imports unchanged; it was written before the script's first run, and
nothing in it changed after.*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Fri 6 Nov 2026 about 03:10 PST: public rows H12, H14, H19
   and H25 (opaque pointers), as A8 read H12, H14 and H25.
2. **Used.**
   - **M11's registered reading** (`REGISTRATION.md` § 1, `3c31a91d`; `score_m11.py`, `03582d2f`, line 150; `score_m11_v2.py`'s staged reader,
     `ebdbb35c`; `score_m11_v3.py`, `33cdccf6`): Q138(t)'s chain as Q139(e) froze it (`docs/reports/data/2026-11-03-q139e-heat-end-to-end/
     predict_q139e.py`, `455c46c1`: `TAU` and `R3`, the inventory's H14), on `score_e144.a3_load([pass])`'s session
     (`docs/reports/data/2026-11-02-q138t-heat-model/score_e144.py`, `heat_q138t.py`, `fit_q138t.py`, `f5473428`), each hold read by
     `tools/claims-v3/e166/score_e166.py` (`f830b9e2`) unchanged. The arm reuses every one of these functions as committed.
   - **A8-6** (`REGISTRATION.md.dated-note-A8.md`, `80b92990`) and its estimate (`residue-a8.json` › `H_E_anchor_estimate`: the first hold's e
     carries about −(1 − g) × M6's residue at its anchor: −0.12 °C for E144, −0.28 / −0.25 / −0.31 °C for E154 / E166 / E176, −0.30 °C for
     E181), M6's step response behind it (the inventory's H12).
   - **The four committed aifoundry3 sessions with a smoke pass and then a fixed R0** (the ones A8 reads): E144 (`ca979517`, R0 8 min), E154
     (`d037d82a`), E166 (`179549ce`) and E176 (`5db7bcf7`), each R0 5 min (the inventory's H19 and H25). E176's measured pass holds no hold
     (G0 refused it): it gives the planned smoke's gap and R0 only.
   - *The same quantity at the same operating point, earlier:* A8-6's estimate of the first hold's part, against the registered chain's own
     account of it (A9-5): −0.02 / −0.13 / −0.12 °C on E144 / E154 / E166, about 0.2-0.5 of the estimate.
3. **Not used.**
   - An 8-minute R0 (A8-6's other route): it changes the box's runner, the cap (about 78-79 card-minutes) and the kit, all verified as they
     stand. The arm costs no card time and changes nothing on the box.
   - M6 as the arm's chain: an arm changes one thing (the chain's start), not the model; M6 stays A8's predictor of the residue.
   - The arm's start at the floor's equilibrium (every state at the board's excess over Pref in the smoke's first 3 s): a sensitivity, printed
     beside (A9-5), never the arm.
   - Anything of the NDA tier; Q124's counts.
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code. No NDA-tier check is used, so there is no sha256 line;
   no NDA-tier piece, name, verdict, ratio or figure is cited.

## A9-1. The arm (reported, never a verdict)

For every M11 aifoundry3 session that passed its start gate, and whose smoke pass's telemetry is collected, the scorer also reads the
session's five holds with **the registered chain run over the smoke pass and the measured pass together**:

- **the telemetry:** the smoke pass's `telemetry.jsonl.gz`, then the measured pass's (`heat_q138t.load_tel`, the 34 raw codes, as
  `score_e144.a3_load` reads one pass);
- **the grid:** the measured pass's own 0.2 s grid (`heat_q138t.grid` on its telemetry alone), extended back by whole 0.2 s steps to the
  smoke's first readable sample. So every grid point inside the measured pass, and every value the registered reading reads there (T, P,
  Pref, each hold's measured rise R), is the registered reading's own, bit for bit; the arm refuses if it is not. The gap between the passes
  is the straight line across it, as `heat_q138t.grid` fills any gap;
- **the input:** the board above the session's Pref (the median board W over R0's last 120 s, the measured pass's, unchanged);
- **the chain's start:** every state 0 at the first grid point (the card settled at its floor F0: A6-1, and A7-4's hour of rest);
- **the marks, records and anchors:** the measured pass's only (`score_e144.a3_session`, unchanged); each hold's anchor is the mean of T less
  the prediction over the 120 s before its anchor end, as registered; the plateau window, X1's completeness and every reader are the
  registered reading's;
- **refused** (the arm reads NOT SCORED, with its reason, and nothing else changes) when the smoke's telemetry is not there, or holds fewer
  than 10 readable samples, or when the gap from its last readable sample to the measured pass's first is not in (0, 600] s.

So **R is the registered R exactly, and the arm's e (e_2p) differs from the registered e only through the chain's prediction.** P_2p = R − e_2p.

## A9-2. What the arm reads

- **Per hold:** e_2p, and Δe = e_2p − e.
- **On the arm's points (P_2p, e_2p):** HM-E144 (|e_2p(H_E)| / R ≤ 1.5%), HM-HE (`he_departs_exact`) and HM-CAL (A3's `cal_by_name`, pooled
  as registered), computed by the registered decision code unchanged (`score_m11_v2.decide_card_kind`). Its other outputs on the arm are
  printed too, all under the arm's own heading.
- **Its lines staged** in A4-8's form, in the same lines file after the registered reading's three stages: the arm's A2 line (H_E and Z)
  before any later hold's e_2p is read, and its A4 line (L1 and S) before L2's.

## A9-3. What the arm never does

It is never a verdict, an entry (A2-3, A4-3) or what M11 carries; it changes no start gate, stop, rest rule, box file, design, power figure or
card-minute. M11's primary stays the registered reading, and every registered reading is the same with or without the arm (the scorer v4's
self-test checks this). A record quotes a reading on the arm only beside the registered one, labelled "reported (A9): the chain over the smoke
and the measured pass".

## A9-4. What each outcome means

- **Δe(H_E):** the registered chain's own account of the smoke's heat at H_E's anchor (A8-6's mechanism). Its sign is fixed by the mechanism
  (positive: the registered e(H_E) is pushed negative); its size on E181 is expected near E176's +0.147 °C (A9-5).
- **HM-E144 reads the same on both:** the smoke does not decide it. **It reads differently:** the records quote both, with A8-6 named; the
  registered reading still decides (A9-3), and the next M11 session's registration says whether the arm becomes its reading.
- **HM-CAL and HM-HE:** read the same way. A Δe of about +0.15 °C on H_E alone moves the H_E-Z pair line's gain by about 1.1% (0.15 °C over
  the cool plan's span of P, 14.52 − 0.69 °C; 1.4% for the warm pattern's) and its value at L1, S and L2 by about 0.10, 0.03 and 0.08 °C
  (0.15 × (P − P_Z) / (P_HE − P_Z) at the plan's P of 9.67, 3.46 and 8.35 °C, A1's table), against HM-CAL's τ of about 0.05 °C with three
  later holds. So HM-CAL is the reading the arm can move most.
- **Δe on Z, L1, S and L2:** expected under 0.001 °C (A9-5): the smoke's heat is gone from the chain by then. A larger Δe there means the
  arm's grid or input is wrong; the records say so.

## A9-5. The post hoc evidence (`a9_posthoc.py`; `a9-posthoc.json`, `a9-posthoc.txt`)

| session | R0 | gap between the passes (s) | first hold | its Δe (°C) | A8-6's estimate of its part (°C) | later holds' largest \|Δe\| (°C) | the first hold's offset from the other holds' line, registered → arm (°C) |
|---|---|---|---|---|---|---|---|
| E144 | 8 min | 14.1 | H_H | +0.021 | −0.119 | 0.000 (1 hold) | (too few others) |
| E154 | 5 min | 2.5 | H_M | +0.131 | −0.282 | 0.0001 | −0.089 → +0.050 (se 0.14, 4 others) |
| E166 | 5 min | 2.5 | K_S | +0.117 | −0.253 | 0.0001 | −0.129 → −0.012 (se 0.23, 3 others) |
| E176 (the planned smoke) | 5 min | 2.5 | (no hold: G0 refused) | the chain's prediction at R0's anchor rises by +0.147 | −0.31 | | |

- **By the chain's own account the part is about half of A8-6's estimate.** After a 5-minute R0, the registered chain carries 0.13-0.15 °C of
  the smoke at R0's anchor (M6 put 0.33-0.41 °C there), and almost all of it is gone by the first hold's plateau, so Δe ≈ that anchor part.
  After E144's 8 minutes it carries 0.02 °C.
- **The arm moves each first hold toward its session's other holds:** E154's from −0.089 to +0.050 °C off their line, E166's from −0.129 to
  −0.012 °C. Each offset is inside its prediction's standard error either way, so this supports the arm's size without resolving it.
- **Every grid point inside each measured pass is the registered reading's own** (`measured_points_identical` true in all four), and R reads
  the same to the bit.
- **The sensitivity:** the arm's start at the floor's equilibrium (the board 0.11-0.18 W under Pref in the smoke's first 3 s) moves each Δe by
  0.001-0.007 °C.
- **For E181**, which runs E176's smoke unchanged: Δe(H_E) is expected near +0.15 °C. HM-E144's line is 1.5% of R, about 0.21 °C for the cool
  pattern's H_E (R about 14 °C): the registered reading can carry about 0.15 °C of the smoke inside that line.

## A9-6. What it does to E181's kit

M11's scorer v4 (new files, committed after this amendment) reads the arm; E181's `score_e181_v2.sh` names the smoke pass (`p18101`) for the
measured pass (`p18120`). Nothing on the box changes: the box list, the runner, the session, the gates and the stops are the kit's as committed
(`33cdccf6`). About 75 card-minutes, as before.

## Files (`SHA256SUMS-a9`)

This amendment; [`a9_posthoc.py`](a9_posthoc.py) (numpy; `/usr/bin/python3 -B tools/claims-v3/m11/a9_posthoc.py . <out.json>` from the lab
clone's top, about 15 s; it imports `score_m11.py` unchanged for the registered reading's own modules); its output
[`a9-posthoc.json`](a9-posthoc.json) (with the sha256 of every file it read) and printout [`a9-posthoc.txt`](a9-posthoc.txt).

## Compute

The Intel, through the round's local slot, one job at a time: the development run (03:12:41-03:12:56 PST); a run in a scratch copy of the
tree with M11's scorer v4 drafted against `two_pass()` (03:19:23-03:20:51 PST: the arm's shift of H_E on E154's renamed pass, +0.131 °C, is
this file's +0.131 °C for E154's H_M, and R is the registered R in all five holds); then the committed run from the lab clone
(03:21:24-03:21:40 PST), its json byte for byte the development run's. No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0
