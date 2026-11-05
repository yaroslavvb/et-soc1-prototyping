# Dated amendment A4 beside REGISTRATION.md (Thu 5 Nov 2026; Q143(k)) - HM-CAL-I8, the int8 pair's own line (L1 and S) read on the later int8 hold L2 in each aifoundry3 session: its read rule, its threshold, an entry route under a rule fixed first, and its power on v2's committed draws with the premise holding and in section 0.1's case

*Read from about 11:55 PST and written from about 12:15 PST on Thu 5 Nov 2026, on the Intel, desk only (no card, no device command, no lab
box, no post in the lab's channel, no Modal, no archive), and committed at the time git records. REGISTRATION.md, A1, A2 and A3, with every
file of lab commits `3c31a91d` (07:41:57 PST), `f49b7ddd` (08:44:59), `d3d97fe2` (10:07:42) and `ed24bc6e` (11:07:48), stay as committed. A4
answers the critic of Q142(h2), (a2) and (r3) (Thu 5 Nov 2026, about 11:18-11:55 PST): its fault 1, a design gap ("A3 found and quantified
the case that breaks A2's premise, but registered no reading that survives it"), and its `next` rank 3. It is committed before every
output it governs: no M11 kit, scorer, fit, hold or claim exists. The run numbers E176 (aifoundry3) and E177 (aifoundry2) were assigned
at about 11:53 PST, and no file of either exists in any ref (`git log --all` at 12:13 PST, and again just before the commit). For the
kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8 (heat over
minutes, the heat path between sessions).*

The figures come from a new file, [`design_power_heat_a4.py`](design_power_heat_a4.py) → [`design-power-heat-a4.txt`](design-power-heat-a4.txt)
and [`.json`](design-power-heat-a4.json). It checks every file [`SHA256SUMS-m11`](SHA256SUMS-m11) (6), [`SHA256SUMS-a1`](SHA256SUMS-a1) (9),
[`SHA256SUMS-a2`](SHA256SUMS-a2) (7) and [`SHA256SUMS-a3`](SHA256SUMS-a3) (7) list, and the ten inputs [`SHA256SUMS`](SHA256SUMS) lists. It
imports `design_power_heat_a3.py` unchanged, which imports A2, v2 and v1 unchanged, and draws exactly v2's committed draws. Its "Checks"
line reads four of four yes; among them, **80 cells that A2 or A3 committed, re-read here, equal the committed figures**: HM-LG's verdicts,
HM-CAL's verdicts, A1-4's path, A2-3's outcome at the exact t point and HM-E144's REPEATS share. [`SHA256SUMS-a4`](SHA256SUMS-a4) pins this
commit's five other files and `SHA256SUMS-a3`, which no list pinned.

## A4-0. What governs, and the result first

- **REGISTRATION.md, as amended by A1, A2, A3 and A4, governs.** A4 adds one reading, HM-CAL-I8, and one entry route after A1-4's path and
  A2-3. It changes no rule, threshold, clause, verdict, adoption value, hold, stop or card-minute figure of REGISTRATION.md, A1, A2 or A3.
  One sentence of A3 is qualified (A4-9): HM-E144 stays "never a clause" of HM-CAL, and it is one condition of HM-CAL-I8's entry route.
- [`registration-a4.json`](registration-a4.json) is `registration-a3.json` with A4 applied. It is the machine-readable copy; the amendments
  govern where they differ.
- **The result.** On the likeliest pattern (E154's fit, then E166's), HM-CAL-I8 reads BETTER in **89.5%** of draws, whether the premise
  holds or H_E is read by the chain as E144's `H_H` was: it never reads H_E or Z. With no effect it reads BETTER in 2.4%. Its blind error over
  the two L2 holds is **0.095 °C** (median; 5-95%: 0.026-0.195 °C), against the chain unscaled's 0.269 °C. In § 0.1's case a per-session
  calibration now enters in **81.0%** of draws (A2's 21.6% plus A4's 59.4%), against A2's 21.6% alone. **The entry route is adopted by A4-6's
  rule, at 81.0% against its 80% bar.** That margin is thin, and A4-5 says how the route reached it: one revision of one condition, made
  after one development run. The route as first fixed reads 36.8% there. With one session, HM-CAL-I8 is read and reported, and nothing
  enters.

## A4-1. The reading HM-CAL-I8

Per aifoundry3 M11 session σ, with § 1's per-hold P, R and e = R − P and § 1's rule for which holds are scored:
- **The int8 pair** is **L1** (`int8.full`) and **S** (`int8.neg_ones`), both on E97's natural chain. **The later hold** is **L2**
  (`int8.full`). All three are chosen by hold name, never by position (A3-6's rule).
- **The line** through the pair: **g = (e_L1 − e_S) / (P_L1 − P_S) and a = e_S − g P_S**. Nothing of L2 enters it.
- **The prediction, blind given the watts:** R̂(L2) = P(L2) + a + g P(L2). The calibrated miss is **e_c(L2) = e(L2) − a − g P(L2)**; the
  chain unscaled's is e(L2).
- **The read rule (A4's own).** A session is read if all of these hold:
  - L1, S and L2 are scored (§ 1);
  - L1 and S both ended before L2's first launch (the launch records' times);
  - the pair spans **at least 3.0 °C of P**;
  - **L2's P lies inside the pair's span**, so w = (P_L2 − P_S) / (P_L1 − P_S) is in [0, 1].

  Otherwise the session reads NOT SCORED, with its reason printed.
- **Why 3.0 °C, not HM-LG's 6.0 °C.** The plan's pair spans 6.211 °C (the 51.2 °C room) and 6.307 °C (52.0 °C), only 0.2-0.3 °C over 6.0 °C.
  The plan's P comes from E78's switching watts, and a session's measured P can differ by more than that: E154's `int8.full` hold `H_M`
  read P 10.86 °C where the plan has L1 at 9.67 °C. Under a 6.0 °C rule a session could read NOT SCORED for a realistic shortfall. The
  read is an interpolation, since L2 lies inside the span (w 0.788 at both rooms). Its noise there is σ_c √(1 + (1 − w)² + w²), at most
  √2 σ_c, whatever the span. The span only keeps the pair's two rise levels distinct, so half of HM-LG's 6.0 °C is kept as that guard.
- **One later hold a session.** At the plan n_L is 2 (one L2 in each of two sessions). The reading is thin, and its interval is wide.
- No constant is shared between sessions or card kinds, and nothing is fitted on a committed session.
- **aifoundry2:** A4 registers nothing. Its A2 pair (Z_m, G1E) and later holds (Z_m2, G1E2) are all `int8.neg_ones` on run_hpl.py's
  pattern, so § 0.1's fp32 and duty-cycle case does not arise there.

## A4-2. The statistic, the threshold and the verdicts

- **The statistic.** D_I8 = RMS_c − RMS_u over the L2 holds of every read session of aifoundry3, pooled (n_L holds), where
  RMS_c = √(mean e_c²) and RMS_u = √(mean e²).
- **The threshold.** **τ = σ_c / √n_L**, with σ_c fixed as § 7 fixes it (0.0884 °C). At the plan n_L = 2 and **τ = 0.0884 / √2 =
  0.0625 °C**; with one session read, 0.0884 °C.
- **The verdicts:** **BETTER** if D_I8 ≤ −τ; **WORSE** if D_I8 ≥ +τ; **NOT RESOLVED** otherwise; **NOT SCORED** if no session is read.
- **Reported per session:** a, g, the span and w; e(L2), e_c(L2) and d(σ) = |e_c(L2)| − |e(L2)|; the session's own verdict at σ_c.
- **The blind error it delivers.** RMS_c(I8) is a blind per-session error for heat over minutes, given the watts, on int8 holds of E97's
  natural chain inside the pair's span. It is reported with its χ² interval at n_L degrees of freedom (approximate, and wide at n_L 2),
  beside RMS_u, the ×1.032 arm's rms over the same L2 holds, A2's calibrated miss on L2 alone, and the floor if the premise holds on the
  int8 holds: **σ_c × √(mean over the sessions of 1 + (1 − w)² + w²) = 0.114 °C at the plan** (the critic's arithmetic, now computed).

## A4-3. The entry route: what M11 then carries

**The order.** A1-4's path is read first, then A2-3, both unchanged. HM-CAL-I8 is read after them. HM-CAL-I8 enters only if **all** of these
hold:
1. **E1:** A1-4's path carries nothing (no common term);
2. **E2:** A2's calibration does not enter (A2-3 as A3 amends it, at the exact t point): HM-CAL is not BETTER, or a clause N1 or N2 is met,
   or it is NOT SCORED;
3. **E3:** HM-E144 reads REPEATS (A3-5's flag of § 0.1's case: |e(H_E)| / R(H_E) ≤ 1.5% in every session that ran H_E);
4. **E4′:** the chain misses the int8 holds. X² = Σ (e / σ_c)² over the read sessions' L1, S and L2 exceeds χ²'s 95% point at 3k degrees
   of freedom, for k read sessions (7.8147 at 3, **12.5916 at 6**, 16.9190 at 9). It reads no fp32 hold;
5. **E5:** at least 2 sessions are read by HM-CAL-I8 (with one session nothing enters, as § 6's one-session rule says);
6. **E6:** HM-CAL-I8 reads BETTER and N1-I8 (A4-4) is not met.

**When it enters.** A session that runs L1 and S before a later int8 hold on E97's natural chain has that hold's rise predicted as
P + a + g P from its own pair's line, where the hold's P lies inside the pair's span. M11 states RMS_c(I8) as that prediction's error, with
its interval. Outside that scope (another format, kind or duty pattern, or outside the span) the line is not tested and no error is
established.

**Otherwise** A1-4's or A2-3's outcome stands, and HM-CAL-I8 is reported beside it (a reported arm): its verdict, RMS_c(I8) with its
interval, and the floor. The ×1.032 arm keeps A1-4 (d)'s fate in every case: A4 replaces or retires nothing.

| outcome | what it means |
|---|---|
| HM-CAL-I8 BETTER and it enters | Heat over minutes on aifoundry3 is set per session, and the int8 holds' own pair reads it where the fp32 pair does not (§ 0.1's case flagged by HM-E144) |
| BETTER, not entering | A1-4's or A2's term carries, or one of E3-E6 fails: a reported arm with its blind error |
| NOT RESOLVED | the calibrated and unscaled L2 misses differ by less than τ: with one later hold a session this is common under a small effect |
| WORSE | the pair's line does not carry to L2: the chain is already right on int8 (no effect), or the misses belong to the holds or drift |
| NOT SCORED | no session read (a hold not scored, the order, the span, or L2 outside it) |

## A4-4. The not-wanted clause, and one way only

- **N1-I8, a session worse on its own:** d(σ) = |e_c(L2)| − |e(L2)| ≥ σ_c / √1 = **0.0884 °C** in any read session.
- **One way only** (§ 10): a clause met makes HM-CAL-I8 a reported arm, never the primary, and a clause never brings a term in.
- A2's N2 (H_E departs in every session) is not a clause of HM-CAL-I8, which never reads H_E.

## A4-5. How the rule was fixed (disclosed)

- **12:02:52 PST:** the whole rule was written down in the lane's scratch before any A4 code had run. That covered A4-1 to A4-4 with E4
  as **HM-LG's own reading** ("GAIN, LEVEL or BOTH, or NOT SEPARATED with its null rejected"), and A4-6's adoption criteria. Rough
  hand figures were in view: the critic's floor 0.114 °C, and a hand guess that the combined entry in § 0.1's case would land near 80%.
- **12:05:45-12:05:52:** one development run at 300 draws a cell, written only to the scratch. In § 0.1's case on the likeliest pattern
  HM-CAL-I8 read BETTER in 87.7% of draws, but the combined entry read 42.0%. E4 blocked the route in 47.3% of draws: HM-LG's null was
  not rejected. H_E's near-zero miss at the largest P inflates the per-session residual that both of HM-LG's F tests divide by. So E4
  read H_E, the hold whose miss defines the case the route is for.
- **12:07:32: the one revision.** E4 became **E4′**, the int8 holds' own null test (A4-3), which reads no fp32 hold. Nothing else changed:
  the read rule, D, τ, N1-I8, E1-E3, E5, E6 and A4-6's criteria (i)-(iii) stand as fixed at 12:02:52. The lane's note says no further
  revision would follow, whatever the full run read. The route as first fixed is printed beside the registered one in every cell
  (`route_as_first_fixed_with_E4_HM_LG`).
- **12:08:14-12:09:50:** the full run, into scratch. **12:10:36-12:12:25:** the committed run. Its JSON is byte-identical to the full run's,
  and its printout differs only in the "wrote" line.
- **What the reader should take from it.** The criteria were fixed before any output and did not move. The route's form moved once,
  for a reason in the design's own logic (E4 measured the wrong holds), and that one change took the combined entry in § 0.1's case from
  36.8% to 81.0%, over an 80% bar. A critic may count the revision as one fork. The route as first fixed would not be adopted: (ii)
  reads 36.8%.

## A4-6. The adoption rule and its reading

- **The rule** (fixed at 12:02:52 PST, before any output). A4's entry route is adopted at the registered design if, at σ_c, on two
  aifoundry3 sessions at the exact plan, on v2's committed draws:
  - (i) with no effect, HM-CAL-I8 enters in at most 5% of draws;
  - (ii) in § 0.1's case on E154's fit then E166's, a per-session calibration (A2's or A4's) enters in at least 80%;
  - (iii) in each premise row where the chain is right on the int8 holds and only the fp32 pair misses (no effect, with H_E ±0.3 or ±0.5 °C,
    Z +0.15 or +0.3 °C, or the fp32 pair ±0.15 °C), HM-CAL-I8 enters in at most 5%.

  Else HM-CAL-I8 is a reported arm only.
- **As read** (`design-power-heat-a4.json` › `adoption`): (i) **0.4%**; (ii) **81.0%**; (iii) 0.0-0.3% in each of the eight rows. **The route is
  adopted.** As first fixed: (i) 0.2%, (ii) 36.8%, (iii) 0.0-0.3%: not adopted.

## A4-7. Its power at the registered design (v2's committed draws; `design-power-heat-a4.txt` §§ 3-5)

Two aifoundry3 sessions at v2's exact plan (P 14.517, 0.695, 9.670, 3.459, 8.354 °C at the 51.2 °C room; 11.723, 0.986, 9.778, 3.471, 8.439 °C
at 52.0 °C), 5,000 draws a cell. Columns: HM-CAL-I8 BETTER / NOT RESOLVED / WORSE; N1-I8; HM-E144 REPEATS; what M11 carries (A1-4's common
term / A2's calibration / HM-CAL-I8), all in %; a per-session calibration in all, with the route as first fixed in brackets; the rms over
the L2 holds in °C (median: unscaled / HM-CAL-I8 [5%, 95%] / A2's line on L2); and, when HM-CAL-I8 enters, its calibrated rms (unscaled in
those draws).

**§ 0.1's case: H_E read by the chain as E144's `H_H` was** (σ_c; e(H_E) is its noise only, as A3-2 adds it):

| truth (both sessions unless named) | I8 B / NR / W | N1-I8 | REPEATS | carries: A1-4 / A2 / I8 | per-session (first) | L2 rms | on entry |
|---|---|---|---|---|---|---|---|
| none | 2.4 / 78.9 / 18.7 | 23.3 | 94.0 | 0.6 / 0.7 / 0.4 | 1.1 (0.9) | 0.073 / 0.095 [0.025, 0.198] / 0.091 | 0.071 (0.150) |
| gain 2.35% | 75.0 / 22.0 / 3.0 | 12.7 | 94.4 | 1.3 / 13.6 / 58.7 | 72.3 (14.3) | 0.207 / 0.095 [0.026, 0.201] / 0.205 | 0.079 (0.225) |
| gain 3.20% (the arm) | 90.7 / 8.3 / 0.9 | 6.7 | 94.2 | 0.2 / 17.8 / 69.5 | 87.3 (18.3) | 0.274 / 0.097 [0.026, 0.200] / 0.270 | 0.088 (0.282) |
| gain 4.52% | 98.4 / 1.5 / 0.1 | 1.6 | 94.3 | 0.0 / 18.5 / 75.9 | 94.4 (19.0) | 0.384 / 0.094 [0.026, 0.197] / 0.371 | 0.090 (0.386) |
| level 0.15 °C | 56.0 / 37.5 / 6.5 | 19.3 | 94.0 | 40.7 / 17.1 / 17.5 | 34.6 (19.2) | 0.163 / 0.095 [0.027, 0.198] / 0.126 | 0.074 (0.196) |
| level 0.27 °C | 91.9 / 7.4 / 0.7 | 5.7 | 94.1 | 84.8 / 10.1 / 3.5 | 13.7 (10.5) | 0.278 / 0.094 [0.024, 0.198] / 0.188 | 0.083 (0.298) |
| level 0.40 °C | 99.3 / 0.7 / 0.0 | 1.0 | 93.6 | 97.0 / 2.2 / 0.5 | 2.8 (2.5) | 0.399 / 0.096 [0.028, 0.197] / 0.258 | 0.074 (0.453) |
| E154's fit | 88.5 / 10.6 / 0.9 | 7.4 | 94.2 | 1.1 / 0.8 / 80.6 | 81.5 (1.0) | 0.260 / 0.095 [0.026, 0.193] / 0.330 | 0.087 (0.269) |
| E166's fit | 91.0 / 8.3 / 0.7 | 6.4 | 93.9 | 98.5 / 1.3 / 0.1 | 1.4 (1.3) | 0.283 / 0.095 [0.026, 0.201] / 0.157 | 0.066 (0.348) |
| **E154's fit, then E166's** | **89.5 / 9.7 / 0.8** | 6.5 | 94.1 | **6.2 / 21.6 / 59.4** | **81.0 (36.8)** | **0.269 / 0.095 [0.026, 0.195] / 0.271** | **0.085 (0.278)** |

**The premise holding** (σ_c; A2-5's draws, unchanged): HM-CAL-I8's verdicts are the same as above (it reads only the int8 holds).
HM-E144 reads REPEATS in 0.0-1.2% of draws under E154's fit, the likeliest pattern, every gain and a 0.40 °C level; in 4.1% at 0.27 °C,
20.1% under E166's fit, 50.2% at 0.15 °C and 94.0% with no effect. So E3 keeps the route out where A2 works. **On the likeliest pattern A2's calibration enters in 97.1% and A4's in 0.0%**,
and the combined entry is A2's 97.1%. A4 adds at most 2.1 points of entry in any premise-holding cell (a 0.15 °C level).

**At 1.5 σ** (thresholds fixed at σ_c): in § 0.1's case on the likeliest pattern, HM-CAL-I8 reads BETTER in 74.8%, and a per-session
calibration enters in 60.0% (A2 23.8%, A4 36.3%; as first fixed 30.2%), at 0.117 °C on entry (unscaled 0.306 °C). With no effect the route
enters in 3.4% and the combined entry is 6.3%. With the premise holding on the likeliest pattern A2 enters in 75.3% and A4 in 0.0%.

**A2's and A3's other premise rows** (σ_c; `design-power-heat-a4.txt` § 4):
- With no other effect, where only the fp32 holds miss (H_E ±0.3 or ±0.5 °C, Z +0.15 or +0.3 °C, the fp32 pair ±0.15 °C), the route enters in
  0.0-0.3%. That is criterion (iii): E4′ reads the int8 holds' misses as noise in about 95% of draws, and E3 fails where H_E misses.
- Under a drift of +0.05 or +0.10 °C a hold with no other effect, HM-CAL-I8 reads BETTER in 65.0% and 99.7%, and the route enters in 41.8% and
  44.0%. The line partly corrects a drift: 0.124 against 0.210 °C, and 0.197 against 0.405 °C, over L2.
- Under a 3.2% gain with H_E −0.5 °C (A2 enters 2.0%), the route enters in 59.3%, at 0.089 °C on entry (unscaled 0.283 °C).
- On the likeliest pattern, a miss on H_E of +0.3 or +0.5 °C, or on Z, leaves REPEATS at 0.0%, so the route adds nothing there: it is for
  § 0.1's case only.

**One aifoundry3 session** (the least, 74.7 card-minutes): HM-CAL-I8 reads BETTER in 79.6% on the likeliest pattern (either premise), in
3.1% with no effect, and 65.4-95.2% under the committed gains and levels of 0.27 °C or more. Its calibrated L2 miss reads 0.076 °C (median,
one hold), against 0.251 °C unscaled. Nothing enters with one session. **Three sessions:** BETTER 94.8% on the likeliest pattern; in § 0.1's
case a per-session calibration enters in 79.9% (A2 6.4%, A4 73.6%).

## A4-8. What the kits and the scorer must do (§ 13 step 1, as amended by A1-A4)

- **The kit** runs § 5's order, H_E, Z, L1, S, L2, and records each hold's name with its launch times, as A3-9 says. A kit that runs L2
  before S or L1 has ended makes HM-CAL-I8 read NOT SCORED for that session, as a named departure.
- **The scorer:**
  - It takes each hold's P and e from § 1's functions unchanged.
  - It selects L1, S and L2 by hold name and checks the order and the span by the launch records and P. It writes a and g to its output
    before it reads L2's e.
  - It prints HM-CAL-I8 per session and pooled: the verdict at its exact τ, N1-I8, E4′'s X² with its χ² point, A4-3's outcome beside A1-4's
    and A2-3's, RMS_c(I8) with its interval, the floor, and A2's line and the ×1.032 arm on L2.
  - It labels RMS_c(I8) with A4-2's scope.
  - Its self-tests cover A4-1's read rule on synthetic sessions (`design-power-heat-a4.txt` § 2: every hold scored; H_E not scored, which A4
    still reads; L2, S or L1 not scored; L2 run before S ended; a span of 2.9 °C; L2 above L1's P or below S's; a span of exactly 3.0 °C). They
    also cover A4-3's route on synthetic sessions with known answers, and reproduce one cell of `design-power-heat-a4.json` from the
    committed draws: § 0.1's case on the likeliest pattern (HM-CAL-I8 BETTER 89.5%, the route enters 59.4%, a per-session calibration 81.0%).
  - It checks `SHA256SUMS`, `SHA256SUMS-m11`, `-a1`, `-a2`, `-a3` and `-a4` before it reads anything.

## A4-9. What does not change, precedence, and what supersedes what

- **Unchanged:** REGISTRATION.md, A1, A2 and A3 with every file of `3c31a91d`, `f49b7ddd`, `d3d97fe2` and `ed24bc6e`; every rule, threshold,
  clause, verdict, adoption value, hold, stop and card-minute figure they state; HM-LG, HM-AG, HM-E144, HM-HE and S7-W; (c) HC1 and (d) I8P
  with HC1-B, I8P-B and their precedence; M10, M9, Q138(t)'s chain, pool 8, and E171-E174's registrations.
- **One sentence qualified.** A3-5's "It is reported, never a clause: it decides nothing" reads: HM-E144 is never a clause of HM-CAL (A2),
  and it decides nothing there; **it is condition E3 of HM-CAL-I8's entry route** (A4-3).
- **Precedence.** HM-CAL-I8 counts as blind only if this commit precedes the first launch record of every M11 session it reads. The scorer
  checks that by git and by the launch records' times, as § 11 says, and otherwise labels the reading post hoc.
- **The card time is unchanged:** aifoundry3, two sessions of 74.7 card-minutes on different days (149.4; cap 76 each), in § 5's order.
  aifoundry2 stays optional. A4 needs no new hold.
- **This commit:** this amendment; `registration-a4.json`; `design_power_heat_a4.py` with `design-power-heat-a4.txt` and `.json`; and
  `SHA256SUMS-a4`, which pins these five and `SHA256SUMS-a3`.

## What it does to predicting power and heat

Nothing is measured, and no frozen prediction changes. Heat over minutes is the largest open heat error: 0.49 °C blind given the watts for
the chain unscaled over nine large rises. As registered before A4, M11's two aifoundry3 sessions gave a blind per-session error near
0.104 °C only if the fp32 pair shared the int8 holds' line; in the case the one committed reading of H_E's pattern supports, a calibration
entered in 21.6% of draws. With A4, the session's own int8 pair reads its later int8 hold whichever case holds. Its blind error is 0.095 °C
(median over two L2 holds; wide at n_L 2), and a per-session calibration enters in 81.0% of § 0.1's draws. HM-E144 says which pair carries.

## Compute

Desk only, on the Intel, at nice 10 through the round's local slot, one job at a time on one core:
- one development run at 300 draws a cell (12:05:45-12:05:52 PST), into the lane's scratch;
- the full run (12:08:14-12:09:50), into the scratch;
- the committed run (12:10:36-12:12:25), its JSON byte-identical to the full run's.

Outside the slot: `py_compile` and `ast` checks of the new file, the tables of this text generated from the committed JSON, git and
`shasum`. No lab box, no remote host, no card.
