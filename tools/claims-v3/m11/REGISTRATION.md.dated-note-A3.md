# Dated amendment A3 beside REGISTRATION.md (Thu 5 Nov 2026; Q142(a2)'s fix pass) - HM-CAL's premise and scope after § 0.1's E144 reading (H_E read by the chain while the other holds miss), HM-E144 reported beside HM-CAL as that case's flag, the calibration pair chosen by hold name, HM-HE at its exact t point, and A2's wording; no rule, threshold, clause, adopted figure or card time changes

*Read from about 10:40 PST and written from about 11:05 PST on Thu 5 Nov 2026, on the Intel, desk only (no card, no device command, no lab
box, no post in the lab's channel, no Modal), and committed at the time git records. REGISTRATION.md, A1 and A2, with every file of lab
commits `3c31a91d` (07:41:57 PST), `f49b7ddd` (08:44:59) and `d3d97fe2` (10:07:42), stay as committed. This amendment answers an
adversarial read of `d3d97fe2` (about 10:11-10:40 PST; verdict: holds with fixes): one minor fault (F1, A3-1 to A3-5) and two nits on the
commit (F2, A3-6; F3, A3-7). Its fourth item concerns the lane's own report, not this text, and goes to the records. A3 is committed
before every output it governs: no M11 kit, scorer, fit, hold, run number or claim exists, and no data of pool 8's card day (E171-E174)
exists in any ref (`git log --all` at 10:43 PST, and again just before the commit). For the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
items 9 and 8 (heat over minutes, the heat path between sessions).*

The figures come from a new file, [`design_power_heat_a3.py`](design_power_heat_a3.py) → [`design-power-heat-a3.txt`](design-power-heat-a3.txt)
and [`.json`](design-power-heat-a3.json). It checks every file [`SHA256SUMS-m11`](SHA256SUMS-m11) (6), [`SHA256SUMS-a1`](SHA256SUMS-a1) (9)
and [`SHA256SUMS-a2`](SHA256SUMS-a2) (7) list, and the ten inputs [`SHA256SUMS`](SHA256SUMS) lists. It imports `design_power_heat_a2.py`
unchanged, which imports v2 and v1 unchanged, and re-runs every cell of `design-power-heat-a2.json` on v2's committed draws. Its "Checks"
line reads eight of eight yes; among them, all 74 cells, recomputed with A2's own functions, equal the committed ones. Beside the first
output, [`design-power-heat-a2.txt.dated-note-1.md`](design-power-heat-a2.txt.dated-note-1.md) says which of its figures A3's output
supersedes. [`SHA256SUMS-a3`](SHA256SUMS-a3) pins this commit's six other files and `SHA256SUMS-a2`, which no list pinned.

## A3-0. What governs

- REGISTRATION.md, as amended by A1, A2 and A3, governs. Where A3 and A2 differ, A3 governs: A3-3 (one sentence qualified), A3-4 (the
  scope of the calibrated error), A3-6 (the pair by name) and A3-7 (wording and a t point).
- [`registration-a3.json`](registration-a3.json) is `registration-a2.json` with A3 applied. It supersedes `registration-a2.json` as the
  machine-readable copy; the amendments govern where they differ.
- `design-power-heat-a3.txt` / `.json` supersede `design-power-heat-a2.txt` / `.json` for N2 at the exact t point (one cell, A3-7 (c)) and
  add the rows of A3-2 and A3-5. A2's other figures stand: A3's run reproduces each one.

## A3-1. What § 0.1 already showed about H_E (F1)

- **The committed reading.** § 0.1 records the frozen chain's misses on the 14 fitted holds of six sessions. Nine are large rises
  (R ≥ 10 °C). The chain read eight of them 1.83-5.60% low, and **E144's `H_H` (fp32 random, duty-cycled, R 15.00 °C) to +0.10%
  (e +0.015 °C)**. E144's other hold, `H_L` (int8 −1s, R 4.25 °C), read −0.032 °C. E144b's `G1`, the int8 −1s hold of E144's aifoundry2
  half, read 5.6% low (`heldout-m10.json` › `heat_d_chain_gain.holds`).
- **H_E is that pattern** (§ 5; A1-6.1: held 10 minutes, not 13). In the plan, H_E is the only duty-cycled hold and, with Z, one of the
  two fp32 holds. The later holds L1, S and L2 are int8 holds on E97's natural chain. So the calibration pair and the later holds differ in
  format, and H_E differs in duty pattern as well.
- **What that admits.** The committed record already holds a case A2's premise excludes: the chain reads H_E as it read E144's `H_H` (H_E's
  miss near zero) while the session's other holds keep their line. The pair's line then passes near zero at H_E's P, and it misses the
  later holds.
- **What A2 left out.** A2-0 did not name this reading. A2-5's premise table tested only H_E misses of +0.3 and +0.5 °C.

## A3-2. The premise table, extended (F1)

`design-power-heat-a3.txt` § 6. At the plan, σ_c, 5,000 draws a cell. Each failure is added after the draw to v2's committed draws for the
truth named, as A2-5's are. "H_E read by the chain" subtracts the truth's a + g P(H_E) from H_E's miss in each session, leaving its noise
only. Shares in %; rms medians over the later holds in °C.

| failure | with no other effect: HM-CAL; calibrated / unscaled | on E154's fit then E166's: BETTER, enters; calibrated / unscaled | HM-E144 REPEATS there |
|---|---|---|---|
| **H_E read by the chain as E144's `H_H` was** | NOT RESOLVED 72.2%; 0.104 / 0.083 (as with no failure) | **37.1%, 21.6%; 0.256 / 0.278** | **94.1%** |
| a miss specific to H_E, −0.3 °C | WORSE 93.5%; 0.199 / 0.083 | 85.5%, 70.1%; 0.198 / 0.278 | 15.4% |
| a miss specific to H_E, −0.5 °C | WORSE 99.8%; 0.303 / 0.083 | 8.9%, 6.3%; 0.303 / 0.278 | 11.0% |
| the fp32 pair (H_E and Z) +0.15 °C against the int8 later holds | WORSE 88.6%; 0.179 / 0.083 | 80.1%, 72.8%; 0.179 / 0.278 | 0.0% |
| the fp32 pair −0.15 °C | WORSE 87.9%; 0.179 / 0.083 | 92.8%, 77.3%; 0.178 / 0.278 | 0.4% |
| *A2-5's rows:* H_E +0.3 / +0.5 °C; Z +0.15 / +0.3 °C; a drift of +0.05 / +0.10 °C a hold | as A2-5 | as A2-5 | 0.0% in each |

**H_E read by the chain, under every truth** (`design-power-heat-a3.txt` § 6; N2 at the exact t point):

| truth (both sessions unless named) | HM-CAL BETTER / NOT RESOLVED / WORSE | N1 / N2 | the calibration enters / A1-4's common term | rms, median: unscaled / calibrated; when it enters: calibrated (unscaled in those draws) |
|---|---|---|---|---|
| none | 0.7 / 72.2 / 27.1 | 34.7 / 0.3 | 0.7 / 0.6 | 0.083 / 0.104; 0.058 (0.109) |
| gain 2.35% | 15.3 / 66.2 / 18.5 | 29.5 / 6.9 | 13.6 / 1.3 | 0.198 / 0.200; 0.152 (0.205) |
| gain 3.20% (the arm) | 20.1 / 62.5 / 17.4 | 29.8 / 15.5 | 17.8 / 0.2 | 0.259 / 0.256; 0.202 (0.260) |
| gain 4.52% | 25.7 / 60.5 / 13.8 | 26.1 / 39.0 | 18.5 / 0.0 | 0.356 / 0.347; 0.291 (0.353) |
| level 0.15 °C | 49.9 / 47.4 / 2.7 | 8.3 / 1.3 | 17.1 / 40.7 | 0.170 / 0.132; 0.124 (0.181) |
| level 0.27 °C | 93.2 / 6.7 / 0.1 | 1.3 / 4.7 | 10.1 / 84.8 | 0.282 / 0.184; 0.226 (0.291) |
| level 0.40 °C | 99.6 / 0.4 / 0.0 | 0.3 / 13.4 | 2.2 / 97.0 | 0.402 / 0.245; 0.338 (0.420) |
| E154's fit | 1.1 / 30.6 / 68.3 | 77.0 / 27.9 | 0.8 / 1.1 | 0.252 / 0.309; 0.222 (0.270) |
| E166's fit | 99.5 / 0.5 / 0.0 | 0.2 / 2.8 | 1.3 / 98.5 | 0.305 / 0.157; 0.091 (0.294) |
| **E154's fit, then E166's** | **37.1 / 53.1 / 9.9** | **60.0 / 11.5** | **21.6 / 6.2** | **0.278 / 0.256; 0.212 (0.282)** |

**Read plainly.**
- **The likeliest pattern.** If H_E is read by the chain as E144's `H_H` was while the sessions otherwise repeat E154 and then E166, the
  calibration enters in 21.6% of draws, about a fifth of A2-5's 97.1%. N1 is met in 60.0%. A1-4's path carries nothing in 93.8% of these
  draws (HM-LG reads NOT SEPARATED in 66.7%), so HM-CAL decides.
- **The rules hold.** The calibration enters only where it reads better than the chain unscaled on the same later holds (D ≤ −τ), so on
  entry it never reads worse: 0.212 °C against 0.282 °C in those draws.
- **The stated error flatters where entry is rare.** That error is read on the holds that let the calibration enter. With the premise holding
  on the likeliest pattern, entry is near certain and the two figures agree (0.103 °C on entry, 0.104 °C over every draw;
  `design-power-heat-a2.json`). In § 0.1's case they part: 0.212 °C on entry, 0.256 °C over every draw.
- **Other truths.** Under E154's fit alone, HM-CAL reads WORSE in 68.3% and the calibration enters in 0.8%. Under E166's fit or a level of
  0.27 °C or more, A1-4's common term carries in 84.8-98.5% of draws and stays M11's primary. Under a common gain it carries in 0.0-1.3%
  (HM-LG reads NOT SEPARATED in 98.4-100%: H_E's near-zero miss at the largest P flattens the slope), and the calibration enters in
  13.6-18.5%.
- **Negative and format-specific misses.** A negative H_E miss of 0.3 °C still leaves the calibration better than the chain on the likeliest
  pattern (it enters in 70.1%; calibrated 0.198 °C over every draw); one of 0.5 °C does not (6.3%). An offset of the fp32 pair against the
  int8 later holds of ±0.15 °C keeps entry at 72.8-77.3%, at 0.178-0.179 °C, which is 0.07 °C above the floor (0.112 °C).
- **HM-HE (N2) stays weak.** Across these rows it is met in 0.3-39.0% of draws (exact t), and in 11.5% in § 0.1's case on the likeliest
  pattern. HM-E144, which A3-5 puts beside HM-CAL, reads REPEATS in 93.6-94.4% of draws when H_E is read by the chain, under every truth.

## A3-3. "Whatever HM-AG reads", qualified (F1)

A2-5's sentence "So the same 149.4 card-minutes give a blind heat-over-minutes error near the noise floor (0.112 °C), whatever HM-AG reads"
reads: **if the premise holds** (each session's misses follow one line in P, the pair's included, plus independent noise), the same 149.4
card-minutes give a blind heat-over-minutes error near the noise floor (0.112 °C), whatever HM-AG reads. If H_E is read by the chain as
E144's `H_H` was, the calibration enters in about a fifth of draws on the likeliest pattern (21.6%), at about 0.21 °C (A3-2). Any record
that quotes A2's 97.1% and 0.104 °C quotes them with "if the premise holds".

## A3-4. What the calibrated error covers (F1)

A2-3's "The line covers holds whose P lies within the pair's span" reads: the line covers **int8 holds on E97's natural chain** (the later
holds' format and pattern: `int8.full` and `int8.neg_ones`) whose P lies within the pair's span (at the plan 0.7-14.5 °C at the 51.2 °C
room, 1.0-11.7 °C at 52.0 °C). RMS_c is established for those holds only. The pair is fp32 and H_E alone is duty-cycled, so a miss that
depends on the format or the pattern moves the line against the later holds (A3-2's fp32-pair rows). For a hold of another format, kind
or duty pattern, or outside the span, the line is not tested and no calibrated error is established.

## A3-5. HM-E144 beside HM-CAL: the flag of § 0.1's case (F1)

- **What is read.** § 3's HM-E144, unchanged: |e(H_E)| / R(H_E) ≤ 1.5% in every session that ran H_E reads REPEATS. The scorer prints it,
  per session and over the card kind, beside HM-CAL's verdict, RMS_u and A2-3's outcome. It is **reported, never a clause**: it decides
  nothing.
- **Its power for this case** (`design-power-heat-a3.txt` §§ 5-6): REPEATS in 93.6-94.4% of draws when H_E is read by the chain, under
  every truth; on the likeliest pattern 94.1%, against 0.0% when the premise holds there.
- **What else reads REPEATS** (the premise holding, the plan, σ_c):
  - no effect, 94.0% (H_E's miss is then noise too; the later holds read RMS_u 0.083 °C, near the noise);
  - a level of 0.15 °C, 50.2%; E166's fit in both sessions, 20.1%; a level of 0.27 °C, 4.1%;
  - a level of 0.40 °C, gains of 2.35% or more, E154's fit and the likeliest pattern, 0.0-1.2%.
- **How to read it beside HM-CAL.**
  - REPEATS, with the later holds missing by much more than the noise (RMS_u) and HM-CAL NOT RESOLVED, WORSE or N1 met: § 0.1's case. On
    the likeliest pattern with H_E read by the chain, REPEATS comes with NOT RESOLVED or WORSE in 58.8% of draws and N1 is met in 60.0%.
  - REPEATS with RMS_u near σ_c: no effect.
  - REPEATS with BETTER: § 0.1's case (35.3% of its draws on the likeliest pattern, 20.5% with the calibration entering), a small common
    level (0.15 °C: 40.9% of draws) or E166's own line (20.1%). This reading cannot tell them apart.
  - DOES NOT REPEAT: H_E misses as the session's line says, and A2-5's figures apply.
- **Why not a clause.** As a third not-wanted clause (N3), A3's run shows that HM-E144 REPEATS would:
  - fail A2-6's adoption criterion (ii) under E166's fit: 79.1%, against the 80% the rule asks;
  - halve the calibration's entry under a 0.15 °C level, where the premise holds: 36.8% → 18.1%;
  - in § 0.1's own case, cut entry from 21.6% to 1.1%, where on entry the calibration still reads better than the chain unscaled (0.212
    against 0.282 °C).

  This choice was made with those figures in view, and it changes no rule.
- **What the first session can show.** If M11's first aifoundry3 session reads REPEATS with large later misses, the pair's premise has
  failed in § 0.1's way. A later registration, written before the second session, may move the calibration pair to holds of the later holds'
  format and pattern. It would be written after the first session's data, and it would say so. A3 registers no such pair.

## A3-6. The calibration pair by hold name (F2)

- **By name.** A2-1's pair and later holds are fixed by name: H_E and Z, then L1, S and L2 on aifoundry3; Z_m and G1E, then Z_m2 and G1E2
  on aifoundry2. The scorer selects them by name from the session's hold records, never by position among the scored holds.
- **NOT SCORED cases.** A session whose pair hold is not scored reads NOT SCORED, with the hold named, whatever else scored. So does a
  session whose pair was not its first two holds by their launch records' times (A2-7's reordering).
- **Why it matters.** `design_power_heat_a2.session_cal` takes the first two *scored* holds. In the design every simulated hold is scored,
  so its figures stand: the pair by name gives the same reading on all 780,000 simulated sessions (`design-power-heat-a3.txt` § 3). On
  a measured session it can go wrong. With H_E not scored it pairs Z with L1 (a span of 8.97 °C) and reads S and L2, a session A2-1 reads
  NOT SCORED. With the pair run in the other order it reads the session as well (§ 2's synthetic sessions).
- **The rule for the scorer.** It never reuses `session_cal` for a measured session; `design_power_heat_a3.cal_by_name` is the reference.

## A3-7. Wording and precision (F3)

- **(a)** A2-3's "(98.5% of draws)" for the row "BOTH, and HM-AG's BOTH form says they differ" reads **98.4%**: on A1-4's path's own draws,
  HM-LG reads BOTH and the sessions differ in 98.4%. 98.5% is "the sessions differ" over every HM-LG verdict, as A1-4 (e) and A2-5 quote
  it (`design-power-heat-a3.txt` § 4; at 1.5 σ, 73.4% and 74.3%).
- **(b)** A2-3's row-by-row list gains two rows. In both, nothing enters by A1-4, so HM-CAL decides by A2-3. The general rule ("the
  calibration enters only where A1-4's path carries nothing"), `registration-a2.json`'s entry block and `design_power_heat_a2.a2_entry`
  already read them so.
  - BOTH, "share", one term passes, and refitted alone it fails its size, its interval or S7-W.
  - GAIN or LEVEL, "share", failing its size, its interval or S7-W.
- **(c) HM-HE's t point.** § 3 registers the 95% prediction interval with t at n_σ − 3 degrees of freedom: the exact 97.5% point,
  **4.30265 at 2** (`design_power_heat_v2.t95`, the same point A1-4's intervals use). `design_power_heat.he_rates` and
  `design_power_heat_a2` used a table rounded to three decimals (4.303 at 2). The scorer computes the exact point and prints it.
  - In A2's cells it changes one figure: one aifoundry3 session under a 3.2% gain, N2 4.7% → 4.8%.
  - In v2's one-session H_E table (`design-power-heat-v2.txt` § 5') it changes one: a 0.15 °C level with a 0.3 °C miss on H_E, HM-HE
    departs 22.9% → 23.0%.
  - No entry share, no BETTER-with-no-clause share and no adoption value changes (`design-power-heat-a3.txt` §§ 1 and 3).
- **(d)** `registration-a2.json` › `a_heat_over_minutes.entry.one_session` ran A1's sentence and A2's together. `registration-a3.json` gives
  them as two sentences.

## A3-8. The figures, as amended

- **A2-5's tables and A2-6's values stand**, re-run exactly; N2 as A3-7 (c) says. At the exact t point the adoption values read (i) 0.7%;
  (ii) 97.8%, 99.1% and 98.2%; (iii) 97.1%; (iv) 0.7%. A2 stays adopted.
- **The likeliest case, E154's fit then E166's:**
  - if the premise holds: BETTER 99.2%, the calibration enters 97.1%, 0.104 °C [0.058, 0.166] against 0.278 °C unscaled;
  - if H_E is read by the chain as E144's `H_H` was: BETTER 37.1%, enters 21.6%, at 0.212 °C on entry (0.256 °C over every draw);
  - HM-E144 tells the two apart: REPEATS in 94.1% of draws in the second case, 0.0% in the first.
- **The card time is unchanged:** aifoundry3, two sessions of 74.7 card-minutes on different days (149.4; cap 76 each), H_E then Z first.
  aifoundry2 stays optional.

## A3-9. What the kits and the scorer must do (A2-7, as amended)

- **The kit** runs H_E and then Z first, as A2-7 says, and records each hold's name with its launch times.
- **The scorer:**
  - It selects the pair and the later holds by hold name (A3-6), and checks the pair ran first by the launch records' times. Otherwise the
    session reads NOT SCORED, with the reason printed.
  - It reads HM-HE, and so N2, at the exact t point (A3-7 (c)), and prints the point.
  - It prints HM-E144 per session and over the card kind beside HM-CAL, RMS_u and A2-3's outcome, labelled as A3-5's flag.
  - It labels RMS_c with A3-4's scope: int8 holds on E97's natural chain, within the pair's span of P.
  - Its self-tests are A2-7's, plus these synthetic sessions:
    - H_E not scored, which reads NOT SCORED;
    - Z not scored, which reads NOT SCORED;
    - one later hold not scored, which reads with two;
    - the pair run in the other order, which reads NOT SCORED.

    It reproduces one cell of `design-power-heat-a3.json` from the committed draws: § 0.1's case on the likeliest pattern (BETTER 37.1%,
    enters 21.6%, HM-E144 REPEATS 94.1%).
  - It checks `SHA256SUMS`, `SHA256SUMS-m11`, `-a1`, `-a2` and `-a3` before it reads anything.

## A3-10. What does not change, precedence, and what supersedes what

- **Unchanged:**
  - REGISTRATION.md, A1 and A2, with every file of `3c31a91d`, `f49b7ddd` and `d3d97fe2`;
  - every rule, threshold, clause, verdict, adoption value, hold, stop and card-minute figure they state;
  - HM-LG, HM-AG, HM-E144 (now also printed beside HM-CAL), HM-HE (at its exact point) and S7-W;
  - (c) HC1 and (d) I8P, with HC1-B, I8P-B and their precedence;
  - M10, M9, Q138(t)'s chain, pool 8, and E171-E174's registrations.
- **Precedence.** A3 changes no statistic, threshold or clause of HM-CAL, so HM-CAL's precedence stays A2's: `d3d97fe2` must precede the
  first launch record of every M11 session it reads. The scorer also checks that this commit precedes them, because A3-5's flag and A3-6's
  pair rule are read from it. Otherwise it labels the reading post hoc.
- **This commit:** this amendment; `registration-a3.json`; `design_power_heat_a3.py` with `design-power-heat-a3.txt` and `.json`;
  `design-power-heat-a2.txt.dated-note-1.md`; and `SHA256SUMS-a3`, which pins these six and `SHA256SUMS-a2`.

## Compute

Desk only, on the Intel, at nice 10 through the round's local slot, one job at a time on one core:
- a development run of `design_power_heat_a3.py` at 300 draws a cell (10:51:16-10:51:26 PST);
- two short reads of HM-HE's statistic near the t point, which showed that the few draws moved by the exact point are ordinary draws, not a
  fault of the code;
- a full run (10:53:44-10:56:01), all of these into the lane's scratch;
- the committed run, whose time is in the commit message. Its JSON is byte-identical to the full run's, and its printout differs only in
  the "wrote" line.

Outside the slot: sub-second reads of committed JSON, git and `shasum`. No lab box, no remote host, no card.
