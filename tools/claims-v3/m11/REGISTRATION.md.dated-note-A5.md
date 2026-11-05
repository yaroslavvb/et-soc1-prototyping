# Dated amendment A5 beside REGISTRATION.md (Thu 5 Nov 2026; Q143(k)'s fix pass) - whether the sessions' pair lines agree, read beside each per-session calibration (A2's HM-CAL, A4's HM-CAL-I8), and the form an entry is stated in: "per session" only where the lines differ

*Rule fixed at 13:37 PST and written from about 13:43 PST on Thu 5 Nov 2026, on the Intel, desk only (no card, no device command, no lab
box, no post in the lab's channel, no Modal, no archive), and committed at the time git records. REGISTRATION.md, A1, A2, A3 and A4, with
every file of lab commits `3c31a91d` (07:41:57 PST), `f49b7ddd` (08:44:59), `d3d97fe2` (10:07:42), `ed24bc6e` (11:07:48) and `0b554d25`
(12:16:24), stay as committed. A5 answers the verifier of Q143(k) (Thu 5 Nov 2026, about 12:52-13:30 PST): its fault 1, major ("the entry
route cannot tell a per-session line from one common to both sessions, yet A4-3 says an entry means 'heat over minutes on aifoundry3 is set
per session'"), and its fault 6 ("A5 states whether such an entry stands"). It is committed before every output it governs: no M11 hold,
session or claim exists, and no file of E176 or E177 data is in any ref (`git log --all` on `docs/reports/data/*e176*` and `*e177*` at
13:36:54 PST, and again just before the commit). For the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8 (heat over minutes, the
heat path between sessions).*

The figures come from a new file, [`design_power_heat_a5.py`](design_power_heat_a5.py) → [`design-power-heat-a5.txt`](design-power-heat-a5.txt)
and [`.json`](design-power-heat-a5.json). It checks every file [`SHA256SUMS-a4`](SHA256SUMS-a4) (6) lists, then imports
`design_power_heat_a4.py` unchanged, which checks `SHA256SUMS-m11`, `-a1`, `-a2` and `-a3` and imports A3, A2, v2 and v1 unchanged. It draws
exactly v2's committed draws and calls A4's functions per draw in A4's order. Its "Checks" line reads five of five yes; among them,
**every one of the 110 cells of `design-power-heat-a4.json`, re-read here, equals the committed figures** (HM-LG, A1-4's path, A2-3's outcome
at the exact t point, HM-E144, HM-CAL-I8, N1-I8, E4′ and A4-3's outcome). [`SHA256SUMS-a5`](SHA256SUMS-a5) pins this commit's five other files
and `SHA256SUMS-a4`.

## A5-0. What governs, and the result first

- **REGISTRATION.md, as amended by A1-A5, governs.** A5 rewords what an entry of a per-session calibration means (A5-1), adds two reported
  readings (A5-2) and a form clause (A5-3), and states two readings of A4-3 that A4 left open (A5-4). It changes no rule, threshold, clause,
  verdict, adoption value, entry, hold, stop or card-minute figure of REGISTRATION.md or A1-A4, and nothing M11 carries.
- [`registration-a5.json`](registration-a5.json) is `registration-a4.json` with A5 applied. The amendments govern where they differ.
- **The result.** In § 0.1's case on the likeliest pattern (E154's line, then E166's), a calibration read from the session's own holds still
  enters in **81.0%** of draws (A2 21.6%, A4 59.4%), as A4 found. Under A5 M11 states that entry **"per session" in 66.4%** of draws (81.9% of
  the entries), and "common to the sessions, or not separated" in 14.6%. Where both sessions share one line (E154's line in both, a common
  gain of 2.35-4.52%, a common level, a kind effect on `int8.full` of ±0.15-0.30 °C, a common int8 level of 0.30 °C), the route still enters
  in up to 94.4% of draws. But M11 states "per session" in **at most 4.5%**: 0.2-4.5% in § 0.1's case and 0.9-1.6% with the premise holding.
  Under A2's and A4's tables as committed, every entry was stated per session. For E154's line in both sessions and the common gains, in
  § 0.1's case, that was 72.3-94.4% of draws; A4's route alone was 58.7-80.6%, the verifier's figures. With the premise holding, on the
  likeliest pattern, A2 enters in 97.1% and is stated per session in 97.0%.

## A5-1. What an entry means (replaces one row's meaning in A2's table and A4-3's)

An entry of a per-session calibration means only this: **the session's own pair line carries to its later holds, blind given the
watts, in that calibration's scope.** That is A2-3's "the calibration enters" (the pair H_E and Z read on L1, S and L2; A3-4's scope) and
A4-3's "HM-CAL-I8 enters" (the pair L1 and S read on L2; A4-2's scope). By itself an entry does not separate a line set per session from one
common to the sessions. **"Heat over minutes on aifoundry3 is set per session" is said only under A5-3's DIFFER.**

This replaces the meaning column of A2's table, row "BETTER, no clause met" ("Heat over minutes on this card kind is set per session, and
the calibration pair reads it"), and of A4-3's table, row "HM-CAL-I8 BETTER and it enters" ("Heat over minutes on aifoundry3 is set per
session, and the int8 holds' own pair reads it ..."). The verifier named A4's row. A2's row makes the same claim, and A2 also enters under
common lines: in 13.6-18.5% of draws under the common gains in § 0.1's case (A4's committed table), and in 5.2-36.8% in the common rows with
the premise holding (`design-power-heat-a5.txt` § 2). So A5 rewords both rows. What each row puts in M11 (its third column) is unchanged.

## A5-2. The agreement readings HM-CAL-AG and HM-I8-AG

- **What they read.** HM-CAL-AG reads the sessions HM-CAL reads, through their pair H_E and Z (A3-6's names; on aifoundry2 Z_m and G1E).
  HM-I8-AG reads the sessions HM-CAL-I8 reads, through their pair L1 and S (A4-1's names). Each reads only its pair's holds, never a later
  hold.
- **The statistic.** For the k read sessions, take the 2k pair points (P, e): **X²_AG = Σ (e − â − ĝ P)² / σ_c²**, where (â, ĝ) is the
  least-squares line through all 2k points. Each session's own line passes through its two points exactly, so X²_AG is the sessions' (a, g)
  differences weighed by their known covariance σ_c² (XᵀX)⁻¹. At k = 2 it is (Δa, Δg)ᵀ (C₁ + C₂)⁻¹ (Δa, Δg). The code checks the two forms
  agree, to 6e-14 relative, on 2,000 random pairs. Under one common line with independent noise σ_c it is χ² at **2(k − 1) degrees of
  freedom**.
- **The threshold.** σ_c as § 7 fixes it, at the power code's full precision (`design_power_heat.noise()`: 0.0884 °C on aifoundry3, 0.2296 °C
  on aifoundry2). The 95% point is **5.9915 at k = 2**, 9.4877 at k = 3, and 12.5916 at k = 4.
- **The verdicts.** **DIFFER** if X²_AG exceeds the point; **AGREE** otherwise (the lines' difference reads as noise); **NOT SCORED** if
  fewer than 2 sessions are read.
- **Reported:** X²_AG with its df and point, the verdict, each session's (a, g), and the pooled line (â, ĝ) with its covariance. Both
  readings are reported whenever their calibration reads two or more sessions, whether or not that calibration enters.
- **aifoundry2:** HM-CAL-AG is registered in form there (pair Z_m and G1E, σ_c 0.2296 °C). Its power is not computed here: E177 is not built,
  and the amendment its kit needs computes it before any E177 session.

## A5-3. The form clause: how an entry is stated

When a per-session calibration enters, M11 states its form from the **entering** calibration's own agreement reading (A2's from HM-CAL-AG,
A4's from HM-I8-AG):

| entering calibration's reading | M11 states |
|---|---|
| **DIFFER** | **per session**: the read sessions' pair lines differ, so heat over minutes on aifoundry3 is set per session for the holds in that calibration's scope, and each session's own pair reads it |
| **AGREE** | **common to the sessions, or not separated**: the sessions' pair lines read as one. The truth is a common line (for A4, a common int8 line or kind effect on E97's natural chain) or per-session lines this design cannot separate. M11 does not say heat over minutes is set per session. The pooled line (â, ĝ) with its covariance is reported as a candidate common term, never carried; a later registration tests it blind, on a session that needs no calibration holds for it |

- **One way only (§ 10).** The form clause never brings a term in, never takes one out, and never changes what M11 carries. The entry, its
  blind error RMS_c with its interval, its scope and its floor stand as A2 and A4 state them.
- **One session:** nothing enters, and both readings read NOT SCORED (reported).
- **A1-4's common terms** are unchanged. Where A1-4 carries a gain, a level or both, its statement is A1-4's own.

## A5-4. Two readings of A4-3 made explicit (the verifier's fault 6, and its fault 3's printed reasons)

- **Each entry counts its own reading's sessions.** A2-3's one-session clause reads HM-CAL's k, as `design_power_heat_a2.a2_entry` reads
  it. A4-3's E5 reads HM-CAL-I8's k. § 6's one-session rule and HM-LG's k govern A1-4's path.
  - **So an A4 entry (or an A2 entry) stands** when HM-LG counts one session but the entering reading reads two: for example, one session's
    H_E and Z not scored, so that HM-LG counts the other only, while HM-CAL-I8 reads both.
  - Its form is read by A5-3 like any other entry, so HM-I8-AG stands in for HM-AG's comparison there. The output labels such an entry
    "HM-LG read one session".
- **E3 is read over the sessions that scored H_E,** and it needs at least one. With none, HM-E144 reads NOT SCORED and E3 is not met. A4-3's
  outcome then reads "nothing from A4: HM-E144 NOT SCORED". Where HM-CAL-I8 reads NOT SCORED, the outcome reads "nothing from A4: HM-CAL-I8
  NOT SCORED". The scorer reads both before E4′; `score_m11.py` printed the wrong reason in these two cases (the verifier's fault 3). No
  decision changes: each was and is "nothing from A4".

## A5-5. Its rates at the registered design (v2's committed draws; `design-power-heat-a5.txt` §§ 2-5)

Two aifoundry3 sessions at v2's exact plan, 5,000 draws a cell, σ_c. Columns: a calibration from the session's own holds enters (A4's
figure, A2's plus A4's); A2's and A4's entries split by form; the share M11 states "per session", and that share of the entries; each
agreement reading's DIFFER share over all draws.

**§ 0.1's case: H_E read by the chain as E144's `H_H` was** (σ_c):

| truth (both sessions unless named) | enters | A2: per session / common | A4: per session / common | stated per session (of entries) | DIFFER: CAL-AG / I8-AG |
|---|---|---|---|---|---|
| none | 1.1 | 0.0 / 0.7 | 0.1 / 0.3 | 0.1 (7.4%) | 5.1 / 4.4 |
| gain 2.35% | 72.3 | 0.3 / 13.3 | 2.4 / 56.3 | 2.7 (3.8%) | 5.0 / 5.4 |
| gain 3.20% (the arm) | 87.3 | 0.6 / 17.2 | 3.1 / 66.4 | 3.7 (4.3%) | 5.4 / 4.7 |
| gain 4.52% | 94.4 | 0.6 / 17.9 | 3.9 / 72.0 | 4.5 (4.8%) | 4.8 / 5.3 |
| level 0.15 °C | 34.6 | 0.5 / 16.6 | 0.9 / 16.7 | 1.4 (4.0%) | 5.4 / 5.1 |
| level 0.27 °C | 13.7 | 0.8 / 9.3 | 0.1 / 3.4 | 1.0 (7.0%) | 7.0 / 5.0 |
| level 0.40 °C | 2.8 | 0.3 / 1.9 | 0.0 / 0.5 | 0.3 (12.3%) | 8.8 / 5.1 |
| E154's line in both | 81.5 | 0.0 / 0.8 | 3.5 / 77.1 | 3.5 (4.3%) | 6.0 / 4.6 |
| E166's line in both | 1.4 | 0.2 / 1.0 | 0.0 / 0.1 | 0.2 (17.1%) | 8.6 / 4.9 |
| **E154's line, then E166's** | **81.0** | **21.1 / 0.5** | **45.3 / 14.2** | **66.4 (81.9%)** | **98.9 / 79.5** |

- **The premise holding** (σ_c): on the likeliest pattern A2 enters in 97.1% and is stated per session in 97.0% (99.9% of entries). In the
  common rows a calibration enters in 5.2-38.9% and is stated per session in 0.9-1.6%.
- **The kind and format rows** (truth none, σ_c; the miss added to the named holds in both sessions; `design-power-heat-a5.txt` § 5):

| row | enters | stated per session (of entries) |
|---|---|---|
| `int8.full` +0.15 °C (L1 and L2) | 42.6 | 1.5 (3.6%) |
| `int8.full` +0.30 °C (L1 and L2) | 92.5 | 3.7 (4.0%) |
| `int8.full` −0.30 °C (L1 and L2) | 93.2 | 3.9 (4.1%) |
| every int8 hold +0.30 °C (a format level) | 89.1 | 3.6 (4.0%) |
| control (A4's committed 'none' cell) | 1.1 | 0.1 (7.4%) |

  The entries equal, within rounding, the verifier's rows (its A4 route 36.4 / 80.5 / 82.0 / 72.5%) plus A2's entries in the same draws
  (6.3 / 12.0 / 11.1 / 16.6%).
- **What the size and the power are.**
  - HM-I8-AG's size is 5% by construction under any common int8 line (χ² exact): it reads DIFFER in 4.3-5.4% of draws in every common row
    and every kind and format row.
  - HM-CAL-AG reads 4.8-8.8% there. In § 0.1's case the fp32 pair is not on the truth's line, and H_E's P differs between the two sessions
    (14.517 against 11.723 °C), so its points are not on one line exactly: 7.0-8.8% under the 0.27 and 0.40 °C levels and E166's line.
  - On the per-session pattern, HM-I8-AG reads DIFFER in 79.5% of all draws; its noncentrality at the plan is 9.39 (the noiseless pairs,
    `design-power-heat-a5.txt` § 1). HM-CAL-AG reads DIFFER in 98.9-99.9%.
- **At 1.5 σ** (thresholds fixed at σ_c), both readings' size grows to 24.8-31.1%, since they take σ_c as known. In § 0.1's case the common
  rows are then stated per session in 3.9-16.7% of draws. On the likeliest pattern a calibration enters in 60.0% and is stated per session in
  47.1% (78.4% of entries). With noise above σ_c, a "per session" statement is weaker evidence.
- **One session:** both readings read NOT SCORED in 100% of draws, and nothing enters. **Three sessions** (4 df): in § 0.1's case on the
  likeliest pattern a calibration enters in 79.9% and is stated per session in 65.3% (81.7% of entries). The common rows are stated per
  session in 0.0-4.6%.

## A5-6. How the rule was fixed (disclosed)

- **13:37 PST:** the whole rule, A5-1 to A5-5, was written in the fix lane's scratch, `a5-rule-fixed.txt`, before any A5 code existed. That
  was before any A5 output and before any E176 or E177 data. Nothing from any E171-E174 datum or any M11 hold was used: none of them was
  read. The verifier's rates under A4 (its rows above) were in view; A5's own rates were not.
- **13:40:11-13:40:12:** one 20-draw run, to check the code ran, written only to the scratch. Its figures are noise at 20 draws.
- **13:40:24-13:42:24:** the committed run.
- **No revision.** Nothing in the rule changed after any output.
- **What A5 is not.** It has no adoption rule: it is a form clause, not a route. Its size is fixed by construction under a common line with
  noise σ_c, and its power is printed whatever it reads.

## A5-7. What the scorer must do (§ 13 step 1, as amended by A1-A5)

- It prints HM-CAL-AG and HM-I8-AG for aifoundry3 as A5-2 says: X²_AG, df, point, verdict, each session's (a, g), the pooled line and its
  covariance.
- It states an entry's form by A5-3, beside A2-3's and A4-3's outcomes. It labels an entry made while HM-LG counted one session.
- It prints A4-3's two NOT SCORED reasons as A5-4 says.
- It checks `SHA256SUMS-a5` with the earlier lists before it reads anything.
- It counts A5's commit in the blind precedence: HM-CAL-AG, HM-I8-AG and the form clause are blind only if this commit precedes the first
  launch record of every M11 session they read.
- Its self-tests cover A5-2 on synthetic sessions:
  - one common line, which reads AGREE;
  - E154's line then E166's, which reads DIFFER;
  - one session, which reads NOT SCORED;
  - the two forms of X²_AG, which agree.

  They also cover A5-3's two forms on an A4 entry and on an A2 entry, and A5-4's two reasons.
- `score_m11.py` (lab `03582d2f`) stays as committed; `score_m11_v2.py`, a new file, does this.

## A5-8. What does not change, and precedence

- **Unchanged:** REGISTRATION.md and A1-A4 with every file of `3c31a91d`, `f49b7ddd`, `d3d97fe2`, `ed24bc6e` and `0b554d25`; every rule,
  threshold, clause, verdict, adoption value, entry, hold, stop and card-minute figure they state; HM-LG, HM-AG, HM-E144, HM-HE, S7-W, HM-CAL
  and HM-CAL-I8; A4's adoption (81.0% against its 80% bar), which A5 does not re-read; (c) HC1 and (d) I8P; M10, M9, Q138(t)'s chain,
  pool 8, and E171-E174's registrations.
- **The card time is unchanged:** aifoundry3, two sessions of 74.7 card-minutes on different days (cap 76 each), in § 5's order. A5 needs no
  new hold.
- **This commit:** this amendment; `registration-a5.json`; `design_power_heat_a5.py` with `design-power-heat-a5.txt` and `.json`; and
  `SHA256SUMS-a5`, which pins these five and `SHA256SUMS-a4`.

## What it does to predicting power and heat

Nothing is measured, and no frozen prediction changes. A4 gave M11 a blind per-session error for heat over minutes on int8 holds (0.095 °C
over the two L2 holds), whichever pair carries. But A4 would have called a line common to both sessions "per session" in most of the draws
where one was the truth.
- With A5 the same two sessions also say which it is. M11 states "per session" in 66.4% of the per-session pattern's draws, and in at most
  4.5% of the draws of any common line, kind or format effect.
- A common int8 line, where the sessions agree, is reported as a candidate. It is not carried: the next registration can test it blind on a
  session that needs no calibration holds.
- The blind error itself is unchanged.

## Compute

Desk only, on the Intel, at nice 10 through the round's local slot, one job at a time on one core:
- the 20-draw code check (13:40:11-13:40:12 PST), into the scratch;
- the committed run (13:40:24-13:42:24).

Outside the slot: an `ast` parse of the new file, the tables of this text read from the committed JSON, git and `shasum`. No lab box, no
remote host, no card.
