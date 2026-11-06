# The footing law, dated note 1: FL2's check and FL5's checks in one die coordinate, E178 named, card 1's earlier fits, E60's referral, and the record's wording (before any session it governs)

*Beside [`FOOTING-LAW.md`](FOOTING-LAW.md) (`c14e5f35`, committed 22:46:56 PST Thu 5 Nov 2026); it edits none of it and no file `c14e5f35`
committed (`SHA256SUMS` 7 of 7 still pass). Written Fri 6 Nov 2026 (week 45), from about 00:00 PST until its commit, on the Intel, desk
only (no card, no lab box, no device command), by the lane fix-heat-q145a of Q145(a), round A, from the faults an adversarial verifier
found in the heat lane (one major, seven minor). No card session has run since E176 (17:21-17:28 PST Thu 5 Nov), and no session
registered after `c14e5f35` exists, so nothing this note governs has data. **It changes no number of FL1, FL3, FL4 or FL6, no FL7
output and no committed verdict, frozen file or hash list.** It records FL2's self-check, read in one coordinate, as failing its
registered line (N1); fixes FL5(a) and FL5(c) to one coordinate before any data (N1); names E178 (N2) and card 1's earlier fits (N3);
rewords FL6 (N4) and the identification (N5) to the evidence; and states what FL7 can show (N6). Everything it adds is post hoc unless
named a rule.*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Thu 5 Nov 2026 about 23:55 PST to Fri 6 Nov about
   00:05: public rows L10, L20, H07, H08, H12, H14, H15, H24 and H25 (opaque pointers), and the map's rows 4 and 6.
2. **Used.**
   - **FL1's laws, method and bootstrap:** `footing_law.py` (`_quad`, `tables`, `raw_cycle`, the 2,000-draw bootstrap with seed 145),
     `footing-law.json`, `k-e171.json`, `k-e172.json` (`c14e5f35`), imported unchanged by [`footing_law_note1.py`](footing_law_note1.py).
   - **E97's rests,** `docs/reports/data/2026-11-01-e97-heat-low-power-steady/aifoundry3/e97/p9720/` (`18e7683e`): the 22,726 samples
     `rederive_e97.py` selects (the rests R0-R2 from 20 s after each start, 600 MHz, a clean 34-code record), read here per whole
     firmware degree by FL1's method. *Check:* on the 34 codes the same samples give E97's committed law to 1.2e-12
     (`docs/reports/data/2026-11-05-q145a-footing-law/e97-law.json`, `0f4204e9`).
   - **FL1's sources apart:** E44's three September cycles (`sep-p1p3.json`, `8fab3404`) and E71's six October cycles (`slopes.json`,
     `730cc8fc`), each alone by FL1's method: the quasi-static law's between-session spread on one sensor and one method.
   - **E44's card-1 items,** `docs/reports/data/2026-09-25-claims-v3/results/idle.json` (`921e3158`) › `items` IDLE-a, IDLE-c, IDLE-e
     for aifoundry1-c1 (reported there, not tested), with its September idle law (`constants.law`): the earlier fits of the three cycles
     card 1's law rests on (N3). *Check:* `docs/reports/data/2026-11-05-q145a-footing-law/fix-note1.json` › `A_card1_E44_items`.
   - **E78's switching power,** `docs/reports/data/2026-10-31-e78-kinds-energy-matrix/` (`410c56f6`), as E97's closure carries it
     (`e97.json` › `holds.holds.H1`-`H3` › `steady.S_E78_W`, `18e7683e`): Why 4's "what E78 measured" rests on it; FOOTING-LAW.md's
     block left it out.
   - **The reducers' die reading:** `tools/claims-v3/kinds/reduce_e78.py` line 120 and `run_e78.py` line 187 (`cfd94285`) read
     `temp_c.minshire[0]`, so FL3's T_mid and k_s are on FL1's coordinate.
   - **E178's registration and kit** (`48171930` `tools/claims-v3/e178/E178.md` section 5; `a4aafc6f` `KIT.md` line 70): N2.
   - **This study's committed outputs** (`0f4204e9`: `inrun.json`, `profile.json`, `law.json`, `sim.json`, `fl7/`), with the checks
     `fix_note1.py` adds beside them in the study's dated note 1 (N4-N6).
   - *The same quantity at the same operating point, earlier:* aifoundry3 at 600 MHz and 522-523 mV, 55-62 °C: E97's rests (1 Nov)
     against FL1 (E44, Sep; E71, Oct), in one coordinate: N1's table.
3. **Not used.**
   - The 34-sensor coordinate for FL1 or FL3: the reducers' launch and window readings are the firmware's (above), so FL1 and FL3 stay
     there.
   - A wider FL2 line chosen now: not registered, because it would be chosen after the matched difference was read; the
     between-session spread is reported beside it, never as a line.
   - An inlet thermometer: none exists (his answer of Thu 5 Nov 2026: *"We don't have a thermometer, so make do with what you can."*).
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code. No NDA-tier check is used, so there is no sha256
   line; no NDA-tier piece, name, verdict, ratio or figure is cited, and none of Q124's counts.

## N1. One die coordinate: FL2's check fails its line; FL5(a) and FL5(c) fixed before any data

**Two readings of one die.** FL1, the reducers' launch and window readings, FL3's T_mid and E71's method read the firmware's whole degree
(`temp_c.minshire[0]`). E97's law, the heat chain (Q138(t)) and M11's floors and rests read the 34-sensor mean of the raw codes. Over
E97's rests the 34-sensor mean reads **0.746-0.956 °C above the firmware by degree** (0.815 °C over the 22,726 samples; M11's A6 found
0.77-1.20 °C at five sessions' first samples). The laws rise about 0.012 W/°C per °C, so comparing them at the same number misplaces
them by about 0.01 W/°C. FOOTING-LAW.md's Builds on, Why 1 and FL2, and `footing_law.py selftest`'s criterion (3), did exactly that.

**FL2's check, read in one coordinate** (`footing_law_note1.py`, `footing-law-note1.json` items 1-4; post hoc: E97's rests were seen
before the rule). W/°C, at the firmware reading:

| °C | 55 | 56 | 57 | 58 | 59 | 60 | 61 | 62 |
|---|---|---|---|---|---|---|---|---|
| FL1, aifoundry3 | 0.3155 | 0.3273 | 0.3391 | 0.3509 | 0.3627 | 0.3745 | 0.3863 | 0.3981 |
| E97's rests on the firmware degree, FL1's method (its band, 52-66 °C), minus FL1 | +0.0092 | +0.0100 | +0.0107 | +0.0115 | +0.0123 | +0.0130 | +0.0138 | +0.0146 |
| the same over every degree with at least 100 samples (50-63 °C), minus FL1 | +0.0120 | +0.0110 | +0.0101 | +0.0091 | +0.0081 | +0.0072 | +0.0062 | +0.0053 |
| E97's committed law at T + the measured offset, minus FL1 | +0.0086 | +0.0091 | +0.0097 | +0.0102 | +0.0105 | +0.0118 | +0.0122 | +0.0127 |
| E97's committed law at the same number, minus FL1 (what the selftest read) | −0.0028 | −0.0023 | −0.0017 | −0.0012 | −0.0006 | −0.0001 | +0.0005 | +0.0010 |
| FL1's own sources apart: E71's six cycles alone minus E44's three alone | +0.0288 | +0.0234 | +0.0181 | +0.0127 | +0.0074 | +0.0020 | −0.0033 | −0.0086 |

- **FL2's registered self-check (the two laws within 0.01 W/°C over 55-62 °C) FAILS when read in one coordinate.** By FL1's own method,
  E97's rests sit 0.009-0.015 W/°C above FL1 and exceed the line at 57-62 °C; over every degree they sit 0.005-0.012 above it and
  exceed the line at 55-57 °C. The selftest's PASS line (`selftest-output.txt`: "worst 0.0028 W/C, line 0.01") compared across
  coordinates. Its criteria (1) and (2) stand as committed; criterion (3) is superseded by `footing_law_note1.py` item 4.
- **Post hoc, never a line** (item 4b): over 55-62 °C the matched difference is 0.012 W/°C rms by FL1's method (0.009 over every
  degree). That is smaller than the difference between FL1's own two seasons on one sensor and one method (E71 against E44: 0.016 rms,
  up to 0.029 at 55 °C, the two crossing near 60 °C), and larger than FL1's bootstrap over its nine cycles (±0.0044 at 58 °C). So
  E97's rests differ from FL1 by about what one season differs from another, and the reading stands as **one quasi-static law per card
  to within its season-to-season spread**, not "the same law within 0.0028 W/°C".
- **What does not change.** FL2's substance: the loop keeps E97's law in its own coordinate (g(T) as FL2 gives it, T the 34-sensor
  mean), and the footing keeps FL1 in the reducers' coordinate. No number of FL3 (k_s 0.36007 / 0.49300), FL7 or M11's A6 gate moves.
  Had the footing taken E97's rests on the firmware degree at E171's T_mid instead (0.3722 against 0.3601 W/°C), FL7's gain f would
  move by c1 × 0.0121 = 0.0015.
- **Withdrawn wording, with the corrected quote.** FOOTING-LAW.md's "within **0.0028 W/°C** of it over 55-62 °C (two sensors, two
  methods, one law)" (Builds on), "give the same to 0.0028 W/°C" (Why 1) and FL2's "the same law within 0.01 W/°C over 55-62 °C
  (checked by `footing_law.py selftest`; worst 0.0028)"; the study README's "two sensors, one law" and "the same law within 0.003 W/°C".
  They become: *"read in one die coordinate, E97's rests sit 0.005-0.015 W/°C above FL1 at 55-62 °C, about what FL1's own two seasons
  differ by (E44 to E71: 0.016 W/°C rms, up to 0.029); FL2's registered 0.01 line is exceeded over part of that range."*

**FL5(a), fixed before any data.** (a) k_s against FL1's bootstrap interval at T_mid, both on the firmware reading; and on aifoundry3
against E97's rests read on the firmware degree by FL1's method, at T_mid. *Post hoc, on the seen sessions* (`footing-law-note1.json`
item 6): E171's k_s 0.3601 lies inside FL1's [0.3567, 0.3638] and 0.0121 below E97's rests on the firmware degree (0.3722; the
registered form, E97's law at the same number, read 0.3593); E172's 0.4930 lies inside [0.4400, 0.5135].

**FL5(c), and M11's A6-5 with it, fixed before any data.** This replaces "its slope at T_mid lies within ±0.02 W/°C of k_c(T_mid)",
and A6-5's rests binned on the 34-sensor mean against FL1's 0.280-0.351 W/°C:
- **the reading:** the cooling's or the rests' samples (rule F: from 20 s after each cooling's or rest's start, 600 MHz), per whole
  firmware degree inside FL1's band for the card (aifoundry3 52-66 °C, card 1 56-70 °C), the degrees with at least 100 samples; a
  straight line through the per-degree mean board W, weighted by the samples;
- **the law's value:** the same line through FL1's quadratic, evaluated at the same degrees with the same weights, so the two are
  compared at matched temperatures and weights whatever the degrees' spread;
- **the verdict:** PASS if the two slopes differ by at most 0.02 W/°C, FAIL outside, NOT SCORED with fewer than 300 samples in the band
  (all as registered); still reported beside, never a gate of a verdict;
- **reported beside it, on the 34 codes:** the same samples in E97's 0.5 °C bins of the 34-sensor mean (at least 20 samples each), the
  same weighted line, against E97's law by the same estimator at the same bins and weights;
- **a dry run on E97's own rests** (seen data: a check of this specification, never a test of the law; item 5): firmware degrees 52-58,
  0.3196 W/°C against FL1's 0.3106 by the same estimator, +0.0090: PASS;
- **what a FAIL means, restated before any data:** at 52-55 °C FL1's own two seasons differ by 0.029-0.045 W/°C (item 3; 0.031 rms over
  52-58 °C), beyond the ±0.02 line. So a FAIL whose rests sit mostly there may be the law's season-to-season spread rather than a moved
  law. FOOTING-LAW.md's "FAIL, the card's law moved (or the reading's offset did)" gains that third reading, and a PASS shows one law
  to within the line.

## N2. E178 is the next 600 MHz kinds session on aifoundry3, and FL3 does not reach it

FOOTING-LAW.md's header says "the next one has no registration yet". It had one. E178 (one-number kinds on aifoundry3 card 0 at 600 MHz in
E171's form) was registered in `48171930` at 20:51:01 PST, 1 h 56 min before `c14e5f35`; its kit `a4aafc6f` (23:06:28) came after.
E178 reduces on Q139(u)'s footing (E178.md section 5: `reduce_e171.py --leak 0.20563713796102187 --no-refit --drop-dips`; KIT.md line 70:
its collector refuses any other value), and FL3 binds only sessions registered after `c14e5f35`. **So E178 keeps its registered footing
and carries no FL3 arm or companion.**

"What it answers, and the first blind tests" (FOOTING-LAW.md's last section) therefore reads:
- **the law:** M11's next aifoundry3 session (FL5(c) as N1 fixes it) or card 1's first cooling, unchanged;
- **the footing's consequences:** the first 600 MHz kinds session registered after `c14e5f35` that scores M1, A1 and KA (pool 8's day 2
  or pool 9).

E178 scores none of M1, A1 or KA: its rules read one-number differences, a ranking, a slope per flip and spreads (E178.md section 5). Its
owners, Q146's lanes, who alone write `tools/claims-v3/e178/`, may add FL3's arm and FL7's first-order companion by a dated amendment
before its data. E178 would then be FL3's first blind reading on aifoundry3, of the footing's effect on one-number differences only. To
first order that effect is a gain f = 1 − 0.1234 × (k_s − 0.2056) ≈ 0.98 on every D (Why 5), so about 2% of each measured int8
difference (about 0.004 W of the +0.186 W forecast for 5s against 4s); the session scale absorbs it on the floats.

## N3. Card 1's cycles were fitted before, as a residual

"Never fitted before" (`c14e5f35`'s subject; FOOTING-LAW.md's "no earlier dedicated fit exists (this is the first of E44's card-1
cycles)"; the study README's table) is wrong. E44's committed `results/idle.json` (`921e3158`, 26 Sep) fitted the same three cycles:
- **IDLE-a:** card 1's idle less aifoundry2's September idle law, a residual slope of 0.237 W/°C over 57-81 °C (0.2381 / 0.2378 / 0.2351
  per cycle; reported, not tested);
- **IDLE-c:** its metered rails at 75-80 °C, 0.767 W/°C, and the unsensed part at 74-88 °C, 0.162 W/°C;
- **IDLE-e:** its SRAM rail, 0.051 W/°C.

The record reads instead: *"card 1's first board-power slope at 58-62 °C stated as such; E44's IDLE-a fitted the same cycles as a residual
over aifoundry2's September law."*

**Check** (`fix-note1.json` › `A_card1_E44_items`): IDLE-a's per-bin residual over 58-62 °C, re-joined to that law (P = 12.635 + 23.257
e^((T − 80)/36) W), gives 0.5401 / 0.5209 / 0.5324 W/°C per cycle. FL1's per-cycle fits on the raw telemetry give 0.5495 / 0.5183 /
0.5313. The differences, −0.009 / +0.003 / +0.001, come from bin means against samples. The residual rebuilt from the raw telemetry
equals IDLE-a's per bin within 0.0005 W, so both rest on the same samples.

## N4. E60's 800 MHz referral, reworded

FL6 and Why 3 call E60's 0.442 W/°C "the right referral for its own use". The record reads instead: **kept unchanged in `surface_hpl.py`
because the governor model was fitted with it; by this study an in-run estimate whose relation to the quasi-static law is not identified
(N5), so the 800 MHz referral may be understated; a quasi-static cooling at 800 MHz needs a governor move, which waits on his word.**

*Post hoc and untested:* where the law is known, the same estimator from 0.8 s read 0.56 (E60, aifoundry3), 0.79 (E171) and 0.82 (E172)
of it. If that ratio carried to aifoundry2 at 800 MHz and 617 mV, the quasi-static slope there would be about 0.54-0.79 W/°C. That is
+0.35 to +1.2 W over E60's median window rise there (3.5 °C), the size of aifoundry2's pinned-board misses (E173's 1.094 W rms; E175's
+0.53 W level). It is an open question for aifoundry2's pinned-board level, not a finding.

## N5. What the estimators show, worded to the evidence

FOOTING-LAW.md's ground (3), "the two low slopes are shown here to be estimator dilution of that same law"; Why 2's Monte Carlo
"pattern"; and Why 3's "So the low in-run medians are the estimator, not a different leakage". With them goes the lane's "physically
identified" (its result) and "answered at the desk" (its hub line). They become: **the low slopes are consistent with the quasi-static
law, not measured in-run.** The evidence:
- **The rests' bracket holds the law.** OLS to reverse regression spans [0.206, 0.455] W/°C on aifoundry3 and [0.313, 0.512] on card 1;
  the law at the rests' temperatures reads 0.351-0.363 and 0.415-0.496. But the Monte Carlo with the law's slope matches the OLS
  (0.21-0.22 and 0.28-0.31), not the reverse regressions: it gives 0.53-0.65 and 0.55-0.70, against the observed 0.455 / 0.512. So the
  rests alone admit any slope in the bracket.
- **The in-run fits sit below the law; their ensemble moves with the start.** The per-run medians, dips removed, are E171 0.285 → 0.225 →
  0.177 and E172 0.403 → 0.374 → 0.302 from 0.8 / 1.5 / 2.0 s. Why 3 quoted the dips-kept series (0.290 → 0.233 → 0.183; 0.395 →
  0.377 → 0.303) beside the dips-removed own slopes. The ensemble of the same runs moves with the start: E171 0.441 → 0.378 → 0.305 from
  1.0 / 1.5 / 2.0 s; E60 on aifoundry3 0.425 → 0.450 → 0.541; E172 0.621 → 0.602 → 0.545. It straddles the law (0.36) on aifoundry3
  and sits above it (0.49) on card 1.
- **New, post hoc** (`fix-note1.json` › `C_inrun_model`): a model of the per-run estimator with only the whole-degree quantisation and the
  sensor noise (`sim_attenuation.py`'s), its rise and time constant fitted to each session's committed mean profile and its truth set to
  the law, reads **1.8-3.2 times below the observed medians on all three sessions where the law is known**. From 0.8 / 1.5 / 2.0 s it
  gives E171 0.142 / 0.093 / 0.065 against 0.285 / 0.225 / 0.177; E172 0.217 / 0.137 / 0.093 against 0.403 / 0.374 / 0.302; E60 on
  aifoundry3 0.111 / 0.056 / 0.031 against 0.203 / 0.124 / 0.096. It also falls faster with a later start than the data do. So
  quantisation dilution does not account for the in-run values, and the lane's Monte Carlo, run at assumed rises, overstated that
  account. Something else lifts the per-run fits: the reading lagging the hotter parts of the die, or power that drifts within a run,
  are candidates, and neither is measured.
- **The blind tests** are FL5(c) as N1 fixes it, and the first FL3-armed session (N2).

## N6. What FL7 can show

FL7's first-order companion is, to first order, the registered footing's errors times f. On E171's 64 tiles the companion's M10 rms is
0.1670 W against f × the registered 0.1664, M9's 0.2265 against 0.2323, the errors correlated 0.971. On E172 the figures are 0.1675
against 0.1683, M9 0.2182 against 0.2370, correlation 0.964 (`fix-note1.json` › `B_FL7`). So FL7 shows that a footing shared by the
model and the data leaves the verdicts in place; it does not test the law. The registered footing's 5 Nov caveat stands, and the
study's dated note 1 gives the corrected reading. The exact test stays "M10 on the law" (FL3), owed.

## N7. Times

FOOTING-LAW.md was written 22:20-22:46 PST and committed at 22:46:56 (its header says "about 22:20-22:55").

## Files (this note's hash list: `SHA256SUMS-note1`)

| file | what |
|---|---|
| `FOOTING-LAW.md.dated-note-1.md` | this note |
| [`footing_law_note1.py`](footing_law_note1.py) | items 1-6: E97's rests on the firmware degree, the offset, FL1's sources apart, FL2's line, FL5(c)'s dry run, FL5(a); `python3 -B tools/claims-v3/footing-law/footing_law_note1.py . <out.json>` from the lab clone's top |
| `footing-law-note1.json`, `footing-law-note1.txt` | its output and printout |

SPDX-License-Identifier: Apache-2.0
