# Dated amendment A1 beside REGISTRATION.md (Thu 5 Nov 2026; Q142(h)'s fix pass) - the BOTH path and the x1.032 arm in full, HM-AG's BOTH form and S7-W with both terms computed, I8P's not-wanted clause named for the test it computes, H_E's plan on an exact grid, S7-W's 1.5 sigma rates at the registered threshold, and what was already known disclosed

*Read from about 08:15 PST and written from about 08:25 PST on Thu 5 Nov 2026, on the Intel, desk only (no card, no device command, no lab box, no post in the lab's
channel, no Modal), and committed at the time git records. REGISTRATION.md, `registration.json`, `design_power_heat.py`,
`design-power-heat.txt` and `.json`, [`SHA256SUMS`](SHA256SUMS) (58) and [`SHA256SUMS-m11`](SHA256SUMS-m11) (6), all of lab commit
`3c31a91d` (07:41:57 PST), stay as committed. This amendment answers the lane's verifier, an adversarial read of `3c31a91d` (about
07:45-08:15 PST): four minor faults and a nit (A1-1 to A1-4, A1-6), plus one fault this fix pass found in the power code (A1-5). It
is committed before every output it governs: no M11 kit, scorer, fit, hold, run number or claim exists, and no data of pool 8's card
day (E171-E174) exists in any ref (`git log --all`, 08:23 PST). It changes no form, statistic, set, seed, design, stop, card-minute
figure or entry size that REGISTRATION.md states. It states in full what REGISTRATION.md left open or ambiguous (A1-4: the BOTH row's t
points, a term that passes alone, the arm's fate in every case). It names one clause for the test it computes (A1-3). It restates the
figures that a coarse grid and a mis-set threshold moved (A1-2, A1-5). And it discloses what was known (A1-1). For the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
items 9 and 8 (heat over minutes, the heat path between sessions) and item 6 (the power model).*

The power code's faults are fixed in a new file, [`design_power_heat_v2.py`](design_power_heat_v2.py) →
[`design-power-heat-v2.txt`](design-power-heat-v2.txt) and [`.json`](design-power-heat-v2.json). It checks `design_power_heat.py`
and its committed output against `SHA256SUMS-m11` and its ten inputs against `SHA256SUMS`, imports the committed code unchanged, and
reproduces what it does not change: the noise, the 0.2 s plan at all four committed rooms byte for byte, S7-W's committed gain and
level rates at σ, and HM-AG's committed gain and level shares (its "Checks" line: six of six). Beside the first output,
[`design-power-heat.txt.dated-note-1.md`](design-power-heat.txt.dated-note-1.md) says which of its figures v2 supersedes.

## A1-0. What governs

- **REGISTRATION.md governs `registration.json`** wherever they differ (A1-4 names the two places).
  [`registration-a1.json`](registration-a1.json) is `registration.json` with this amendment applied, and supersedes it as the
  machine-readable copy.
- **`design-power-heat-v2.txt` / `.json` supersede `design-power-heat.txt` / `.json`** for the plan's H_E rows and the figures that
  follow from them (A1-2), S7-W's rates (A1-5), and HM-AG's comment (A1-4). The committed output's other figures stand (the noise, the
  aifoundry2 tables, the precision), and v2 reproduces each one it re-runs.
- **Precedence of the blind readings.** This amendment changes no statistic, set, seed or verdict of HC1-B or I8P-B (§§ 8-9), so their
  precedence stays `3c31a91d`'s (§ 11). A1-3 changes no computed test, only a clause's name and what it implies. That clause is judged on
  M11's refit of the committed pairs, which has not run. A1-4 governs HM-LG on M11's own hold sessions, none of which has run.

## A1-1. What was already known (fault 1)

The verifier found two more things already in `heldout-m10.json`, which § 0.7 says this lane read. Neither is a registered result.
`design-power-heat-v2.txt` § 7 re-reads them from the committed file.
- **HC1's bias clause passes on committed rows.** Card 1's held-out 4.5 s heat bias is +0.0071 °C without the session scale and
  −0.0026 °C with it (`heat_c1` › `base_refit_loko` and `with_session_heat_scale_loko` › `aifoundry1-c1`; rms 0.2855 → 0.1731 °C).
  The sign changes and the size falls, so "does not change sign and grow in size" passes. With § 0.4's pooled clause, **two of HC1's
  three entry clauses are known to pass**.
  - Unknown: the two-thirds clause. `heat_c1` holds no per-session d; 14 of card 1's 16 sessions have at least 10 heat rows (448
    rows).
  - Also unknown: HC1-B.
- **I8P's k is previewed by M10's own int8 session scales.** The ratio, card-1 session over its aifoundry3 pair, of M10's int8 term-a
  scales (`power.int8.session_scales_term_a_all_rows`; each session's median over its int8 anchors, all rows):

  | pair | ratio | anchors |
  |---|---|---|
  | E82 / E78 | 0.9960 | 1, 1 |
  | E91 / E86 | 0.9867 | 1, 1 |
  | E131 / E95 | 0.9901 | 1, 1 |
  | E93 / E121 | 1.0059 | 1, 1 |
  | E108 / E122 | 0.9967 | 1, 1 |
  | E94 / E123 | 1.0086 | 1, 1 |
  | E142 / E141 | 0.9989 | 1, 1 |
  | E157 / E153 | 0.9966 | 2, 2 |
  | E164 / E163 | 0.9756 | 4, 3 |

  The range is 0.9756-1.0086 and the median 0.9966. E164 / E163's 0.9756 is § 0.5's RK4 figure, 0.974. These ratios are not k: k
  takes each anchor's measured over predicted D and each fold's D̂ (§ 9). For the seven single-anchor pairs, though, they are close
  to it.
- **The precedence line** "no candidate term below has been computed on any committed row" (top of REGISTRATION.md) reads: **no M11 fit
  code exists and no M11 term has been fitted**. M10's committed outputs already show HC1's pooled and bias clauses and this preview of
  I8P's k.
- **Known when A1-3's reading was chosen:** this preview (the verifier's, re-read here). Under it, a location reading of I8P's clause
  would likely be met (median 0.9966). The spread test that A1-3 keeps cannot be read from it: it needs each anchor's own se.

## A1-2. H_E's plan on an exact grid (fault 2)

**What was wrong.** `design_power_heat.plan_a3` fed H_E's recorded pattern to Q138(t)'s `closed_loop`, which rounds each piece of a
schedule to its 0.2 s grid (`m = int(round(d / dt))`):
- the cool pattern, 3.456 s on and 4.104 s off, became 3.4 and 4.2 s: a modelled share of 0.4474 against the recorded 0.4571, **−2.1%**;
- the warm pattern above 51.5 °C, 2.965 and 5.015 s, became 3.0 and 5.0 s: 0.3750 against 0.3716, **+0.9%**.

E97's natural chain (5.6 s on, 0.2 s off) and the rests are whole on that grid, so only H_E moved, plus the tail H_E carries into Z.

**The corrected plan** (`design-power-heat-v2.txt` § 2'). Every piece is a whole number of steps: 0.008 s for the cool pattern and
0.005 s for the warm one. The code stops if a piece is not whole. The hold marks are on the same grid. P is read over the registered
window, [b − 300 s, b), with b the end of the hold's last process (§ 1). Describe's window, which the committed plan used, ends at the
hold's last piece and so includes H_E's last off-gap (4.1 s cool, 5.0 s warm); it reads H_E 0.012-0.021 °C higher (0.021 °C at 51.2 °C),
and every other hold within 0.001 °C.

| room | H_E's P (0.2 s grid) | H_E's in-launch peak, 34-sensor mean (0.2 s grid) | Z's P (0.2 s grid) |
|---|---|---|---|
| 49.5 °C (cool) | 14.161 (13.856) °C | 66.02 (65.69) °C | 0.751 (0.784) |
| **51.2 °C (cool; the plan's first room)** | **14.517 (14.205)** | **68.13 (67.79)** | 0.695 (0.731) |
| **51.5 °C (cool; the hottest room it admits)** | 14.582 (14.268) | **68.51 (68.17)** | 0.684 (0.721) |
| **52.0 °C (warm; the plan's second room)** | **11.723 (11.856)** | 66.15 (66.27) | 0.986 (0.974) |
| 53.0 °C (warm; G0's limit) | 11.895 (12.032) | 67.35 (67.47) | 0.964 (0.951) |

- **The plan's P per session** is therefore 14.52 / 0.69 / 9.67 / 3.46 / 8.35 °C at 51.2 °C and 11.72 / 0.99 / 9.78 / 3.47 / 8.44 °C at
  52.0 °C, against § 4's 14.21 / 0.73 / 9.67 / 3.46 / 8.36 and 11.86 / 0.97 / 9.78 / 3.47 / 8.44. L1, S and L2 move by at most 0.002 °C.
- **Stops.** The highest planned in-launch peak at any admitted room is **H_E's 68.51 °C at 51.5 °C**: 3.49 °C under the 72 °C hold
  line. The firmware reads about 1 °C under the 34-sensor mean (E144: 68.14 °C mean, firmware 67 °C), so H_E sits about 2.5 °C under
  the 70 °C launch gate. Every other hold peaks at or under 64.65 °C, at 53.0 °C. E144 measured 68.14 °C at a 51.22 °C rest; this
  plan gives 68.13 °C at 51.2 °C, so § 5's "3.8 °C under the hold line" (from E144's measured peak) holds at 51.2 °C, and at 51.5 °C the
  margin is 3.5 °C.
- **Card-minutes:** 73.28-73.30 of plan plus the 1.4 smoke, 74.68-74.70. The registered **74.7 a session (cap 76) stands**.
- **The kit.** Any plan the kit prints at R0's room, for the gate and the stop margins, uses `design_power_heat_v2.plan_exact`, or
  another grid on which every piece of the dispatch's recorded on-time and off-time is whole. A plan on Q138(t)'s 0.2 s grid states its
  H_E share error (−2.1% cool, +0.9% warm) beside it. The scorer reads P from the measured board trace (§ 1), so this concerns the plan
  only.
- **The power at the exact plan** (v2 § 3', on the committed draws, so only P differs). § 4's two-session table moves by at most 0.8
  points in any cell. The one- and three-session figures and H_E's readings move by at most 1.8 points. A1-7 quotes the figures.

## A1-3. I8P's not-wanted clause: named for the test it computes (fault 3)

§§ 9-10 and `registration.json` say I8P is not wanted if "the pairs' k agree with 1 within the anchors' own errors (the sd of k over
the pairs no larger than the sd that drawing each anchor's D as D + se × N(0, 1), 2,000 draws, seed 142, gives), so M10's constant card
term suffices". The test in parentheses asks whether k varies across the pairs more than the anchors' noise. The words ask whether k is
near 1. The conclusion follows from neither alone: a k steady at 0.974 meets the test but not the words.

**Read here, the clause keeps the test exactly as registered and takes the name and the consequence that test supports:**
- **"k varies across the pairs no more than the anchors' own errors give":** the sd of k over the nine pairs (each pair's k in its own
  fold, as § 9 computes it) is no larger than the sd of k that drawing each anchor's D as D + se × N(0, 1) gives (2,000 draws, seed
  142).
- **Met:** a per-session k is not wanted, because a constant card term would do as well. I8P is then a reported arm (§ 10's one way
  only).
- The constant that would do, **0.9616 × the median k over the pairs**, is reported beside it with its 95% interval (a bootstrap over
  the pairs, 2,000 draws, seed 142). M11 never carries it, since no entry rule here registers it; it is a candidate for the next
  registration.
- **Reported beside, never a clause:** |median k − 1| against that interval. If the interval excludes 1, the constant would differ
  from M10's card term.

**Why this reading.** It is the test `3c31a91d` registered in numbers. It is also M10's own form for a session scale's first not-wanted
clause (`section7-m10.json` › `c1` › `clause_1_scales_within_the_window_rises_own_noise`). The location reading was not chosen: it
would also be met by a k that tracks a real session-to-session change around 1, the case this term exists for. A1-1 says what was
known when this was chosen.

## A1-4. The BOTH path and the x1.032 arm in full; HM-AG's BOTH form computed (fault 4)

**(a) The two copies.** REGISTRATION.md governs where `registration.json` differs. The verifier found two places:
- the arm under NOT SEPARATED and LEVEL (the JSON keeps it "reported");
- HM-AG's BOTH form (the JSON gives only F(k − 1, n − 2k)).

`registration-a1.json` carries REGISTRATION.md's reading, as amended here.

**(b) HM-AG's three forms**, read when HM-LG gives GAIN, LEVEL or BOTH and k ≥ 2, each against the sessions' own per-session fits,
with s² = RSS_BOTH / (n − 2k) (§ 3):
- GAIN: one gain e = γP over all the holds, against F(k − 1, n − 2k);
- LEVEL: one level e = ā, against F(k − 1, n − 2k);
- BOTH: one two-term model e = ā + γP, [(RSS_one − RSS_BOTH) / (2(k − 1))] / s² against **F(2(k − 1), n − 2k)**.

"They share one" if the test does not reject at 5%.

**(c) § 6's BOTH row, in full** (HM-LG reads BOTH and HM-AG's BOTH form reads "share"):
1. e = ā_c + γ_c P is fitted by least squares over the card kind's scored M11 holds, **each 95% interval at t(n − 2)**.
2. Each term passes on its own: γ_c if |γ_c| ≥ 0.010 and its interval excludes 0; ā_c if |ā_c| ≥ 0.10 °C and its interval excludes 0.
3. **Both pass:** both enter at their jointly fitted values, unless S7-W with the two-term form carried is met. S7-W then holds each
   session out and refits the form on the others. If it is met, nothing enters and the pair is a reported arm.
4. **One passes:** that term is **refitted alone** (the GAIN or LEVEL row's constant). It enters only by that row's rule: its size, its
   interval at t(n − 1), and S7-W with it alone. A jointly fitted value is never carried alone.
5. **Neither passes:** nothing enters.

**(d) The x1.032 arm on aifoundry3, in every case.** REGISTRATION.md § 6 says the arm is replaced only by a γ_c that M11 carries, and
retired on LEVEL or a clean NOT SEPARATED. Both sentences stand; this table extends them:

| HM-LG-A3 | what M11 carries | the arm |
|---|---|---|
| GAIN | γ_c | **replaced** by M11's γ_c |
| GAIN | nothing (the sessions differ, its size or interval, S7-W) | stays a reported arm |
| LEVEL | anything | **retired** |
| BOTH | γ_c, with ā_c or alone by (c) 4 | **replaced** by M11's carried form |
| BOTH | otherwise | stays a reported arm: the slope test rejected, so a gain is present |
| NOT SEPARATED, the null not rejected | nothing | **retired** |
| NOT SEPARATED, the null rejected ("they differ from zero, the form unresolved") | nothing | stays a reported arm |
| NOT SCORED | nothing | stays a reported arm |

With one session (k = 1) the table is the same, except that nothing enters (§ 6), so the arm is never replaced.

**(e) What the new forms do at the plan** (v2 §§ 4', 4b', 4c; two aifoundry3 sessions, the exact plan, the committed draws; % of
5,000):

| truth, the same in both sessions unless named | HM-AG says they differ: gain / level / **both** form | S7-W met, both carried | M11 carries on aifoundry3 | the arm |
|---|---|---|---|---|
| none | 5.4 / 5.1 / **5.3** | 26.7 | nothing 99.4 (NOT SEPARATED 93.1) | retired 93.8 |
| gain 3.20% (the arm) | 4.5 / 5.7 / **4.9** | 0.1 | γ_c 87.5 | replaced 87.5 |
| level 0.27 °C | 7.0 / 5.0 / **4.6** | 0.1 | ā_c 86.4 | retired 89.4 |
| E154's fit (−0.229 °C + 5.72%) | 6.7 / 6.9 / **4.9** | 0.0 | both 80.0, γ_c alone 14.7 | replaced 94.8 |
| E166's fit (+0.395 °C − 1.43%) | 9.7 / 4.8 / **4.4** | 0.0 | both 28.3, ā_c alone 65.3 | retired 65.6, replaced 28.3 |
| **E154's fit, then E166's** | 13.7 / 35.8 / **98.2** | 49.3 | **nothing 98.7 (the sessions differ 98.5)** | reported 98.7 |

- **This corrects § 4's** "With two sessions HM-AG rarely sees a difference that HM-LG reads as BOTH (98.6%)". The gain and level forms
  rarely see it, but BOTH's own form sees it in 98.2% of draws (77.8% at 1.5 σ). So if M11's two sessions repeat the committed pattern,
  HM-LG reads BOTH (98.6%), and **M11 most likely carries nothing on aifoundry3**. The chain unscaled then stays M11's primary, the arm
  stays reported, and the next registration reads the term from each session itself, after a calibration hold, as § 6's "they differ"
  row says.
- **HM-AG's matched false rates** (each form's test when the sessions share that form, or nothing) are 4.5-5.8% (gain), 4.8-5.7%
  (level) and 4.4-5.3% (both): the 5% each test allows.
- **S7-W with both carried** reads "worse" in 26.7% of draws with no effect: a two-term form fitted on one session of five holds is
  noisy. HM-LG then reads NOT SEPARATED in 93.1% of draws, so it rarely matters; on the path it stops 0.1%. Under either session's real
  two-term truth it reads 0.0%.
- The path's HM-LG verdicts are the power table's on the same draws (v2's "Checks" line).

## A1-5. S7-W's 1.5 σ rates at the registered threshold (found by this fix pass)

§ 7 registers S7-W's threshold as σ_c / √n_σ, **σ_c fixed at 0.0884 °C on aifoundry3**. `design_power_heat.s7w_rates` divided its
simulated noise instead, so its 1.5 σ rates are for a looser threshold than the registered one. § 4's "11.3% and 10.8% at 1.5 σ" (a
gain or a level fitted on no effect) read **21.9% and 21.3%** at the registered threshold: 21.8% and 21.3% on the 0.2 s plan, the
same draws. With both carried the figure is 42.5%.

At σ the committed rates reproduce exactly (11.6% and 10.9% on the 0.2 s plan; 11.7% and 10.9% at the exact plan). So the rule
stays as registered; only the 1.5 σ rates quoted for it change. Read plainly: if the true noise is 1.5 σ, S7-W calls a no-effect term
harmful about one time in five.

## A1-6. Wording and precision (the nit)

1. **H_E is E144's H_H pattern held 10 minutes**; E144 held 13. H_E's plateau window is its 300-600 s, not E144's 480-780 s. § 5's "so
   it repeats the one hold the chain read to 0.1%" reads: so it repeats, from the room, **the pattern** of the one hold the chain read
   to 0.1%, over a 10-minute hold. HM-E144's line, |e/R| ≤ 1.5%, is read on that shorter hold. Its planned P is A1-2's.
2. **§ 4's HM-AG false rates.** "4.6-8.9% say they differ when the sessions share one form" mixed in mismatched pairings: the 8.9% was
   the gain test under a level truth. The matched rates read 4.6-5.7% (gain) and 4.8-5.7% (level) on the committed plan, and A1-4 (e)'s
   at the exact plan.
3. **`SHA256SUMS` pins the 58 committed files this registration reads as inputs**, not every file it names. It names four more:
   - `docs/reports/data/2026-11-02-q138m-model/fit_m7.py`, pinned by M10's `SHA256SUMS` and `POOL8-SHA256SUMS`;
   - `tools/claims-v3/kspeed/run_kspeed.py` (E80's, in § 5's aifoundry2 harness), `tools/claims-v3/dmcmd_audit.py` and
     `tools/claims-v3/e144/README.md` (A1.1's patterns), pinned by no list at `3c31a91d`.

   [`SHA256SUMS-a1`](SHA256SUMS-a1) pins those three, unchanged since `3c31a91d` (git log), with this amendment's own new files. The
   verifier named three of the four files; this pass's own check of every file name in REGISTRATION.md found `run_kspeed.py`.
4. **HC1-B's 0.082 °C and I8P-B's 0.021 W** scale M10's pooled intervals to one session's tiles. One session's effect scales with its
   own |h₁ − 1|, or |k − 1|. Card 1's 16 session heat scales ran 0.629-1.101: eight read 0.96-1.06 and the other eight 0.63-0.87 or
   1.09-1.10 (v2 § 6). The nine pairs' preview ratios run 0.976-1.009. So "M10's held-out effect, −0.112 °C, would read BETTER" (§ 8) is
   the average over card 1's sessions, not a forecast for E172. If E172's h₁ reads near 1, HC1-B reads NOT RESOLVED even with the term
   right.
5. **Not this commit's text but the lane's result:** "E144/E154/E166, 5 degrees of freedom" is 6 (E144 1, E154 3, E166 2), and "abar_c
   ≥ 0.10 C" is |ā_c| ≥ 0.10 °C, as § 6 says.

## A1-7. The figures, as amended

- **HM-LG-A3 at the plan** (two sessions, σ 0.0884 °C, v2 § 3'), GAIN / LEVEL / BOTH / NOT SEPARATED in %:

  | truth | at σ | at 1.5 σ |
  |---|---|---|
  | none | 1.8 / 1.9 / 3.2 / **93.1** | 2.0 / 1.7 / 3.1 / **93.1** |
  | gain 2.35% | **68.9** / 0.3 / 4.3 / 26.4 | **35.4** / 1.2 / 3.7 / 59.7 |
  | gain 3.20% (the arm) | **88.5** / 0.1 / 5.2 / 6.2 | **58.8** / 0.8 / 4.4 / 36.0 |
  | gain 4.52% | **95.4** / 0 / 4.5 / 0.2 | **86.2** / 0.1 / 4.6 / 9.1 |
  | level 0.15 °C | 1.0 / **45.0** / 3.8 / 50.2 | 1.5 / **20.8** / 3.6 / 74.0 |
  | level 0.27 °C | 0 / **89.4** / 4.9 / 5.7 | 0.8 / **60.2** / 4.4 / 34.6 |
  | level 0.40 °C | 0 / **95.1** / 4.8 / 0.1 | 0.1 / **87.9** / 4.8 / 7.2 |
  | E154's fit | 14.7 / 0 / **85.3** / 0 | 48.3 / 0 / **50.3** / 1.5 |
  | E166's fit | 0 / 65.6 / **34.4** / 0 | 0 / 76.0 / **16.9** / 7.1 |
  | E154's fit, then E166's | 1.3 / 0 / **98.6** / 0.1 | 15.4 / 1.5 / **75.1** / 8.0 |

- **One session:** GAIN 68.6% at 3.2%, LEVEL 65.2% at 0.27 °C, NOT SEPARATED 93.0% with no effect. **Three sessions:** 94.5% and 94.5%.
- **H_E** (one session at 51.2 °C, v2 § 5'): with no effect HM-E144 reads inside ±1.5% in 98.9% of draws and HM-HE departs 4.9%. A
  3.2% gain puts H_E inside 0.2% of the time, a 0.27 °C level 29.1%, a 0.15 °C level 78.1%. A hold-specific miss of 0.3 °C makes HM-HE
  depart 21.5-23.3% of the time, and 0.5 °C 44.8-46.5%.
- **What M11 would carry** (A1-4 (e)): γ_c in 87.5% of draws at a common 3.2% gain, ā_c in 86.4% at a common 0.27 °C level. Nothing
  enters in 98.7% if the sessions repeat E154 then E166.
- **Unchanged:** the noise (aifoundry3 σ_c 0.0884 °C over 11 residuals with 6 degrees of freedom; aifoundry2 0.2296 °C; the readout
  floor 0.3019 °C); every aifoundry2 figure of § 4 (those designs do not use the aifoundry3 plan); the precision of § 8 and § 9; the
  card time of § 12.

## A1-8. What supersedes what, and the order

1. **This commit:** this amendment; `registration-a1.json`; `design_power_heat_v2.py` with `design-power-heat-v2.txt` and `.json`;
   `design-power-heat.txt.dated-note-1.md`; and `SHA256SUMS-a1`.
2. **These stay as committed:** REGISTRATION.md, `registration.json`, `design_power_heat.py`, `design-power-heat.txt` / `.json`,
   `SHA256SUMS` and `SHA256SUMS-m11`.
3. **The M11 scorer and kits** (§ 13 step 1) implement REGISTRATION.md as amended here. They check `SHA256SUMS`, `SHA256SUMS-m11` and
   `SHA256SUMS-a1` before they read anything, and their self-tests cover A1-4's path on synthetic sessions.

## Compute

Desk only, on the Intel, at nice 10 through the round's local slot, one job at a time, each on one core:
- one development run of v2 at 200 draws a cell (08:31:18-08:31:50 PST), written only to the lane's scratch;
- the first full run (08:33:19-08:34:42), and a re-run into scratch (08:36:34-08:37:55) that gave the same bytes;
- the committed run (08:42:41-08:44:10). It followed a change that renamed one variable and split each printed line that began with a
  newline escape, so that no word reads to the public-text scan as a login or a process name. Its printout and JSON are byte-identical
  to the first run's.

Outside the slot: the facts checks of this amendment's and the dated note's figures against both committed JSON outputs (165 and 18,
all equal), the generator of
`registration-a1.json`, git, `shasum` and sub-second reads of committed JSON. No lab box, no remote host, no card.
