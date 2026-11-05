# Dated amendment A2 beside REGISTRATION.md (Thu 5 Nov 2026; Q142(a2)) - an in-session calibration reading of heat over minutes, HM-CAL: each session's own level and gain fitted on its first two holds (H_E and Z), its later holds scored blind against the chain unscaled; the fit, the statistic, the threshold and what each outcome means; its place beside A1-4's path; its power on v2's committed draws (adopted at the registered design, card time unchanged)

*Read from about 09:35 PST and written from about 09:56 PST on Thu 5 Nov 2026, on the Intel, desk only (no card, no device command, no lab
box, no post in the lab's channel, no Modal), and committed at the time git records. REGISTRATION.md and every file of lab commit `3c31a91d`
(07:41:57 PST), and amendment A1 with every file of `f49b7ddd` (08:44:59 PST), stay as committed. This amendment answers the critic of
Q142(v2), (r2) and (h) (Thu 5 Nov 2026, about 08:52-09:35 PST): its `next` rank 3 and its fault 3, a design gap: as registered, M11's holds
would most likely carry no heat-over-minutes term (A1-4 (e): nothing in 98.7% of draws if the two sessions repeat E154's pattern and then
E166's). It is committed before every output it governs: no M11 kit, scorer, fit, hold, run number or claim exists, and no data of pool 8's
card day (E171-E174) exists in any ref (`git log --all` at 09:57 PST, and again just before the commit). It changes no form, statistic,
set, seed, design, stop or card-minute figure that REGISTRATION.md and A1 state, and no verdict, carried term or arm's fate of their path.
It adds one reading beside them, and one entry route where their path carries nothing. It changes nothing of (c) HC1 or (d) I8P. For the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
items 9 and 8 (heat over minutes, the heat path between sessions).*

The power is computed by a new file, [`design_power_heat_a2.py`](design_power_heat_a2.py) →
[`design-power-heat-a2.txt`](design-power-heat-a2.txt) and [`.json`](design-power-heat-a2.json). It checks every file
[`SHA256SUMS-m11`](SHA256SUMS-m11) (6) and [`SHA256SUMS-a1`](SHA256SUMS-a1) (9) list, and the ten inputs [`SHA256SUMS`](SHA256SUMS) lists. It
imports `design_power_heat_v2.py` unchanged, which imports `design_power_heat.py` unchanged, and draws exactly v2's committed draws. Its
"Checks" line reads seven of seven yes. On every cell of a committed truth, HM-LG's verdict shares equal the committed tables: one, two and
three aifoundry3 sessions (v2), and aifoundry2's designs (v1). On the plan, A1-4's whole path (`design_power_heat_v2.decide`) equals
`design-power-heat-v2.json` › `path` share for share. [`SHA256SUMS-a2`](SHA256SUMS-a2) pins this amendment's five files and the two lists
the code checks first.

## A2-0. Why, and what was already seen (post hoc, disclosed)

- **The gap.** A1-4 (e): if the two aifoundry3 sessions repeat the committed pattern (E154's fit in one, E166's in the other), HM-LG reads
  BOTH in 98.6% of draws, HM-AG's BOTH form says the sessions differ in 98.2%, and M11 carries nothing in 98.7%. § 6's row for that case
  says "the next registration reads the term from each session itself (a calibration hold first)". So the 149.4 card-minutes, as
  registered, would most likely buy only "the sessions differ", and no blind error for heat over minutes. A2 reads that per-session term
  now, from holds the plan already has. H_E and Z already run first in every session (§ 5), so A2 needs no new hold.
- **Seen before writing** (post hoc; A2's own code, `design-power-heat-a2.txt` § 2). HM-CAL's arithmetic was applied to the two committed
  aifoundry3 sessions that have four or more fitted holds (`heldout-m10.json` › `heat_d_chain_gain.holds`, in run order):
  - **E166:** its first pair (K_S, K_Q; P 12.49 and 6.46 °C, a span of 6.03 °C) gives a +0.165 °C and g +0.55%. Its two later holds read
    0.332 °C rms unscaled and 0.153 °C calibrated, d −0.179 °C.
  - **E154:** its first pair (H_M, K_S) spans 0.52 °C, so the rule cannot read it.
  - **Every pair spanning 6 °C or more** in either session lowers the rms of that session's other holds: 6 of 6 pairs, by 0.112-0.260 °C.

  These sessions ran other kinds in another order. They enter no rule, constant or verdict here. They are why a two-term line was expected
  to carry within a session.
- **Development runs.** Before this text was written, the power code ran twice at 500 draws a cell (the first 500 of the committed draws)
  and once in full, all three into the lane's scratch. The form, the threshold and the clauses were fixed from the design's logic (A2-1 to
  A2-4). The adoption rule's levels (A2-6) are the conventional 5% and 80%, chosen with the development figures in view, and not tuned to
  them.

## A2-1. The reading HM-CAL: the fit

Per M11 hold session σ on a card kind, with § 1's per-hold P, R and e = R − P and § 1's rule for which holds are scored:
- **The calibration pair** is the session's first two holds by § 5's order: on aifoundry3 **H_E, then Z**; on aifoundry2 Z_m, then G1E.
  **The later holds** are the session's other scored holds: on aifoundry3 **L1, S and L2**; on aifoundry2 Z_m2 and G1E2.
- **The fit** is the two-term line through the pair (1 = H_E, 2 = Z): **g_σ = (e₁ − e₂) / (P₁ − P₂) and a_σ = e₂ − g_σ P₂**. With two holds
  this is the least-squares fit of § 2's BOTH form. It needs no choice between a level and a gain, and it fits both committed patterns (E154's
  growing misses and E166's flat ones).
- **The prediction, blind given the watts.** Each later hold h is predicted as **R̂(h) = P(h) + a_σ + g_σ P(h)**: the chain on the hold's
  measured board, plus the session's own line. Its calibrated miss is **e_c(h) = e(h) − a_σ − g_σ P(h)**; the chain unscaled's miss is e(h).
  Nothing of a later hold enters the line.
- **A session is read** if both pair holds are scored, they span at least **6.0 °C of P** (HM-LG's span), and at least **2** later holds
  are scored. Otherwise it reads NOT SCORED, with its reason. At the plan the pair spans 13.82 °C (the 51.2 °C room) and 10.74 °C (52.0 °C).
- No constant is shared between sessions or card kinds, and nothing is fitted on a committed session.

## A2-2. The statistic, the threshold and the verdicts

- **The statistic.** D = RMS_c − RMS_u over the scored later holds of every read session of the card kind, pooled (n_L holds), where
  RMS_c = √(mean e_c²) and RMS_u = √(mean e²).
- **The threshold.** **τ = σ_c / √n_L**, with σ_c fixed as § 7 fixes it: 0.0884 °C on aifoundry3, 0.2296 °C on aifoundry2. At the plan,
  n_L = 6 and τ = 0.0361 °C.
- **The verdicts**, on **HM-CAL-A3** (the primary) and **HM-CAL-A2** (registered beside it, with its own low power):
  - **BETTER** if D ≤ −τ;
  - **WORSE** if D ≥ +τ;
  - **NOT RESOLVED** otherwise;
  - **NOT SCORED** if no session is read.
- **Reported per session:** a_σ and g_σ; rms_u(σ), rms_c(σ) and d(σ) = rms_c − rms_u; and the session's own verdict at σ_c / √n_σ.
- **The blind error it delivers.** RMS_c is M11's blind per-session error for heat over minutes, given the watts. It is reported with its χ²
  interval at n_L degrees of freedom (approximate: one session's later holds share their line's noise), beside RMS_u, the ×1.032 arm's rms
  over the same holds, and **the floor the premise implies**: σ_c × √(mean over the later holds of 1 + (1 − w)² + w²), with
  w = (P − P_Z) / (P_HE − P_Z), the pair's own noise carried to each later hold. The floor is 0.112 °C at the plan.

## A2-3. What each outcome means, and what M11 then carries

**The order.** A1-4's path is read first, unchanged: HM-LG, HM-AG and S7-W over all of each session's scored holds, the pair included.
HM-CAL is read after it, on the later holds only. If A1-4's path carries a common term, that term stays M11's primary: it needs no
calibration pair, and when the sessions share a form it reads the same later holds better than the calibration does. A2-5's figures: refitted
on the other session it reads 0.077-0.092 °C, against the calibration's 0.104-0.105 °C. **The calibration enters only where A1-4's path carries
nothing.**

| HM-CAL | what it means | what M11 carries for heat over minutes on that card kind |
|---|---|---|
| **BETTER**, no clause met (A2-4) | The session's own line, read from its first two holds, predicts its later holds better than the chain unscaled does, blind given the watts. Heat over minutes on this card kind is set per session, and the calibration pair reads it. | If A1-4's path carries nothing: **the calibration enters** (below). If A1-4 carries a common term: that term, with the calibration a reported arm and both blind errors reported. |
| **BETTER**, a clause met | Better pooled, but one session is worse on its own (N1), or H_E departs in every session (N2): the line does not carry in every session. | The calibration is a reported arm (§ 10's one way only); otherwise A1-4's outcome. |
| **NOT RESOLVED** | The calibrated and unscaled misses differ by less than τ. | A1-4's outcome; RMS_c is reported. |
| **WORSE** | The first holds' misses do not carry to the later holds. Either the chain is already right (HM-LG's null not rejected), so calibrating only adds the pair's own noise; or the misses belong to the holds (their kind or duty pattern) or drift through the session (HM-LG's null rejected, or HM-HE departing). A2-5's premise table shows both cases. | A1-4's outcome; RMS_c is reported. |
| **NOT SCORED** | No session could be read (a pair hold not scored, its span under 6 °C, or fewer than 2 later holds). | A1-4's outcome. |

**When the calibration enters.** A session that runs the pair first, H_E then Z in § 5's pattern, has each later hold's rise predicted as
P + a_σ + g_σ P, from its own pair's line. A session that does not run the pair keeps A1-4's outcome: the chain unscaled, when nothing
enters. M11 states RMS_c as that prediction's error. The line covers holds whose P lies within the pair's span (at the plan 0.7-14.5 °C
at the 51.2 °C room, 1.0-11.7 °C at 52.0 °C); outside it the line extrapolates, and no error is established there.

**A1-4's BOTH path, row by row:**
- BOTH, HM-AG's BOTH form says "share", and both terms pass: both enter (A1-4 (c) 3). HM-CAL is reported beside, with the carried term's
  own error over the later holds (refitted on the other sessions, S7-W's fit).
- BOTH, "share", and one term passes: that term, refitted alone, enters by its own row (A1-4 (c) 4). HM-CAL is reported beside.
- BOTH, "share", and neither term passes, or S7-W is met: nothing enters by A1-4, so HM-CAL decides by this section.
- **BOTH, and HM-AG's BOTH form says "they differ"**, the likeliest case if the sessions repeat E154 and then E166 (98.5% of draws):
  nothing enters by A1-4. § 6's "the next registration reads the term from each session itself (a calibration hold first)" is HM-CAL,
  read now on the holds already planned. BETTER with no clause met: the calibration enters.
- GAIN or LEVEL with "they differ", NOT SEPARATED (either null reading) and NOT SCORED: nothing enters by A1-4, so HM-CAL decides.
  Where HM-LG's in-sample null is not rejected and HM-CAL reads BETTER, the blind reading decides.
- **One session (k = 1):** nothing enters, as § 6's one-session rule says. HM-CAL and RMS_c are reported, labelled "one session", as a
  candidate for the next session.

**The ×1.032 arm** keeps A1-4 (d)'s fate in every case: A2 replaces or retires nothing. Its rms over the same later holds is reported
beside HM-CAL.

## A2-4. The not-wanted clauses, and the reported arms

- **N1, a session worse on its own:** d(σ) ≥ σ_c / √n_σ in any read session (0.051 °C for three later holds).
- **N2, H_E departs in every session** that ran H_E (§ 3's HM-HE, § 7's second clause): the misses belong to the hold. N2 is read on
  aifoundry3 only, because aifoundry2's plan has no H_E.
- **One way only** (§ 10): a clause met makes the calibration a reported arm, never the primary, and a clause never brings a term in.
- **The reported arms** use the same pair, the same later holds and the same τ, and never decide anything:
  - the pair's **gain** alone, Σ e P / Σ P² over H_E and Z (§ 6's GAIN form on the pair);
  - the pair's **level** alone, the mean e (§ 6's LEVEL form on the pair);
  - **H_E's gain** alone, e(H_E) / P(H_E): one calibration hold.

## A2-5. Its power at the registered design (v2's committed draws)

At the plan: two aifoundry3 sessions on v2's exact plan (P 14.517, 0.695, 9.670, 3.459, 8.354 °C at the 51.2 °C room; 11.723, 0.986, 9.778,
3.471, 8.439 °C at 52.0 °C), σ_c 0.0884 °C, 5,000 draws a cell (`design-power-heat-a2.txt` § 3; `.json` › `plan` › `0.0884`):

| truth (both sessions unless named) | HM-CAL BETTER / NOT RESOLVED / WORSE (%) | with A2, M11 carries: the calibration / A1-4's common term (%) | rms over the later holds, median (°C): chain unscaled / calibrated [5%, 95%] / the ×1.032 arm |
|---|---|---|---|
| none | 0.7 / 72.2 / 27.1 | 0.7 / 0.6 | 0.083 / 0.104 [0.056, 0.166] / 0.258 |
| gain 2.35% | 89.7 / 9.6 / 0.7 | 26.2 / 67.3 | 0.198 / 0.104 / 0.105 |
| gain 3.20% (the arm) | 98.5 / 1.5 / 0.1 | 11.7 / 87.6 | 0.259 / 0.105 / 0.084 |
| gain 4.52% | 100 / 0 / 0 | 7.0 / 92.9 | 0.356 / 0.104 / 0.130 |
| level 0.15 °C | 76.6 / 21.4 / 2.0 | 36.8 / 43.1 | 0.170 / 0.104 / 0.143 |
| level 0.27 °C | 99.5 / 0.5 / 0 | 11.4 / 88.0 | 0.282 / 0.104 / 0.125 |
| level 0.40 °C | 100 / 0 / 0 | 6.3 / 93.7 | 0.402 / 0.105 / 0.202 |
| E154's fit | 98.6 / 1.3 / 0.1 | 5.2 / 94.8 | 0.252 / 0.104 / 0.116 |
| E166's fit | 99.7 / 0.2 / 0 | 6.3 / 93.6 | 0.305 / 0.104 / 0.162 |
| **E154's fit, then E166's** | **99.2 / 0.7 / 0.1** | **97.1 / 1.3** | **0.278 / 0.104 [0.058, 0.166] / 0.141** |

- **The likeliest case, E154's fit then E166's.** A1-4's path carries nothing in 98.7% of draws (the sessions differ in 98.5%). HM-CAL
  reads BETTER in 98.0% of all draws together with that, and the calibration enters in 97.1%. The blind per-session error is then
  0.104 °C, median (5-95%: 0.058-0.166 °C), against the chain unscaled's 0.278 °C and the arm's 0.141 °C. One session's own calibrated rms
  has a median of 0.097 °C (0.037-0.183). So the same 149.4 card-minutes give a blind heat-over-minutes error near the noise floor
  (0.112 °C), whatever HM-AG reads.
- **At 1.5 σ** (thresholds fixed at σ_c, as A1-5 reads S7-W): with no effect HM-CAL reads BETTER in 3.1% of draws and the calibration enters
  in 2.9%. On E154's fit then E166's, BETTER 91.5% and enters 75.3%, with 0.158 °C calibrated against 0.294 °C unscaled.
- **One session** (the least, 74.7 card-minutes): BETTER in 92.0-99.7% under the committed patterns and under gains of 3.2% or more and
  levels of 0.27 °C or more, and in 1.5% with no effect; the calibrated rms reads 0.096-0.097 °C (median). Nothing enters with one
  session. **Three sessions:** BETTER in 99.6-100% under the committed patterns, and 0.4% with no effect.
- **The arms** (`design-power-heat-a2.txt` § 4):
  - The pair's gain and H_E's gain read best under a pure gain (0.096 °C) and worst under a level or E166's fit (0.118-0.216 °C).
  - The pair's level reads best under a level (0.100-0.102 °C) and worse under a gain or E154's fit (0.119-0.189 °C).
  - The two-term line reads 0.104-0.105 °C under every truth. It is the primary because it need not know the form.
- **The clauses at the plan:** N1 is met in 0.4-1.2% of draws under the committed patterns, and N2 in 0.3-0.4%.

**When the premise fails** (`design-power-heat-a2.txt` § 5: a miss added after the draw, in every session, to v2's committed draws for the
truth named; rms medians, °C):

| failure | with no other effect: HM-CAL; calibrated / unscaled | on E154's fit then E166's: BETTER, enters; calibrated / unscaled |
|---|---|---|
| a miss specific to H_E, +0.3 °C | WORSE 94.0%; 0.198 / 0.083 | 72.6%, 57.4%; 0.198 / 0.278 |
| a miss specific to H_E, +0.5 °C | WORSE 99.8%; 0.302 / 0.083 | 22.0%, 9.9%; 0.303 / 0.278 |
| a miss specific to Z, +0.15 °C | WORSE 58.5%; 0.128 / 0.083 | 95.5%, 91.7%; 0.128 / 0.278 |
| a miss specific to Z, +0.3 °C | WORSE 91.8%; 0.186 / 0.083 | 78.7%, 66.3%; 0.186 / 0.278 |
| a level drifting +0.05 °C a hold | BETTER 23.8%; 0.165 / 0.175 | 100%, 92.2%; 0.164 / 0.414 |
| a level drifting +0.10 °C a hold | BETTER 52.7%; 0.283 / 0.322 | 100%, 54.4%; 0.281 / 0.560 |

- **Read plainly.** When the premise fails, RMS_c sits well above the 0.112 °C floor (0.128-0.303 °C), and A2-2 reports the two side by side.
- A miss specific to H_E of 0.3 °C or more makes the calibration a poor predictor. With no other effect HM-CAL then reads WORSE. With the
  committed pattern it reads BETTER less often (72.6%, 22.0%).
- HM-HE (N2) catches little of it: it is met in 6.1-26.2% of those draws, as § 4 and A1-7 found one session's HM-HE weak.
- Under a drift, BETTER is true but partial: the calibrated holds stay 0.05-0.17 °C above the floor.

**aifoundry2** (registered beside, reported; `design-power-heat-a2.txt` § 7, v1's committed draws, σ_c 0.2296 °C). Two masked sessions read
BETTER in 60.2% at a 4.52% gain, 59.0% at a 0.40 °C level and 40.3% on E154's fit then E166's, and in 1.4% with no effect. Calibrated they
read 0.295-0.300 °C, against 0.37-0.45 °C unscaled. Four sessions read 72.1%, 72.1% and 47.5%. So, as for HM-LG-A2, **no aifoundry2 card
time is recommended for it.**

## A2-6. Adoption, and the card time

- **The rule** (fixed before the committed output): A2 is adopted at the registered design if, at σ_c, on two aifoundry3 sessions at the
  exact plan:
  - (i) HM-CAL-A3 reads BETTER in at most 5% of draws with no effect;
  - (ii) it reads BETTER with no clause met in at least 80% under each committed pattern: E154's fit, E166's fit, and E154's then E166's;
  - (iii) on E154's fit then E166's, the calibration enters in at least 80%;
  - (iv) with no effect, it enters in at most 5%.
- **As read** (`design-power-heat-a2.json` › `adoption`): (i) 0.7%; (ii) 97.8%, 99.1% and 98.2%; (iii) 97.1%; (iv) 0.7%. **A2 is
  adopted.**
- **The card time is unchanged.** aifoundry3: two sessions of 74.7 card-minutes on different days (149.4; cap 76 each). The holds and their
  order are § 5's and A1-2's, with H_E first and then Z, which form the pair. A2 needs no more card time. aifoundry2 stays optional, as
  registered. The least is one session, 74.7 card-minutes: HM-CAL is read and reported there, and nothing enters.

## A2-7. What the kits and the scorer must do (§ 13 step 1, as amended)

- **The kit** runs H_E and then Z first, as § 5 orders them. A kit that reorders them makes HM-CAL read NOT SCORED for that session; the
  reordering is a named departure.
- **The scorer:**
  - It takes each hold's P and e from § 1's functions unchanged (`score_e166.read_one` / `arm_a_error` on aifoundry3, `score_e167.read_hold`
    on aifoundry2).
  - It fits each session's line on its pair only, and writes a_σ and g_σ to its output before it reads any later hold's e.
  - It prints the per-session and pooled readings, the clauses, RMS_c with its interval, the floor, the arms, and A2-3's outcome beside
    A1-4's.
  - Its self-tests cover A2-3's table on synthetic sessions. They reproduce one cell of `design-power-heat-a2.json` (HM-CAL's shares on
    E154's fit then E166's at σ_c) from the committed draws.
  - It checks `SHA256SUMS`, `SHA256SUMS-m11`, `SHA256SUMS-a1` and `SHA256SUMS-a2` before it reads anything.

## A2-8. What does not change, precedence, and what supersedes what

- **Unchanged:** REGISTRATION.md, A1 and every file of `3c31a91d` and `f49b7ddd`; HM-LG, HM-AG, HM-E144, HM-HE and S7-W; § 6's and A1-4's
  tables, verdicts and the arm's fate (A2 adds a reading beside them, and an entry route where they carry nothing); the holds, the stops and
  the card-minutes; (c) HC1 and (d) I8P, with their blind readings HC1-B and I8P-B and their precedence; M10, M9, Q138(t)'s chain, pool 8,
  and E171-E174's registrations.
- **Precedence.** HM-CAL counts as blind only if this commit precedes the first launch record of every M11 session it reads. The scorer
  checks that by git and by the launch records' times, as § 11 says; otherwise it labels the reading post hoc.
- [`registration-a2.json`](registration-a2.json) is `registration-a1.json` with A2 applied. It is the machine-readable copy; REGISTRATION.md,
  A1 and this amendment govern where they differ.
- [`SHA256SUMS-a2`](SHA256SUMS-a2) pins this amendment, `registration-a2.json`, `design_power_heat_a2.py` and its two outputs, plus
  `SHA256SUMS-m11` and `SHA256SUMS-a1`, which no list pinned.

## Compute

Desk only, on the Intel, at nice 10 through the round's local slot, one job at a time on one core: two development runs of
`design_power_heat_a2.py` at 500 draws a cell (09:47:27-09:47:47 and 09:50:03-09:50:24 PST) and a full run (09:52:45-09:54:19), all written
only to the lane's scratch. The committed run's time is in the commit message; its JSON is byte-identical to the full scratch run's, and its
printout differs only in the "wrote" line. Outside the slot: sub-second reads of committed JSON, git and `shasum`. No lab box, no remote
host, no card.
