# Q145(a): one leakage law per card and operating point, shared by the power model's footing and the heat chain's loop (registration)

*Thu 5 Nov 2026 (week 45), written about 22:20-22:55 PST on the Intel, desk only (no card, no lab box, no device command), by the lane
heat-q145a of Q145(a), round A (MAP step 3). It answers the card day critic's rank 5 ("a footing rule, registered before pool 8's day 2
or pool 9 ... with the slope fitted jointly with the scale") and the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **item 6** (the power model) with
**items 8 and 9** (heat). It is committed **before any new card data**: no card session has run since E176 (17:21-17:28 PST), and the
next one has no registration yet. It changes no committed verdict, frozen file or hash list.*

**What was read before this was written, disclosed.** E171's dated note 1 (the eight footings' verdicts), E172's README lines 95-97 (its
five), Q139(u)'s README, and the post hoc re-derivations of this lane (below, "Why"). The rule is chosen on three grounds, none of them a
model's error: (1) the request itself, that the footing and the loop use one law; (2) E97's steady heat balance, which only the
quasi-static law closes; (3) the two low slopes are shown here to be estimator dilution of that same law. The post hoc scores under the
rule (FL7) are computed only after this commit.

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Thu 5 Nov 2026 about 22:20 PST: public rows L10, L20,
   H08, H12, H14, H15, H24 and H25 (opaque pointers), and the map's rows 4 and 6.
2. **Used.**
   - **E44's dedicated idle cycles** (25-26 Sep 2026), `921e3158`, `docs/reports/data/2026-09-25-claims-v3/raw/{aifoundry3,aifoundry1-c1}/idle/p1-p3/`
     (telemetry and the `cool_start` mark): three of aifoundry3's nine cycles, and the whole of card 1's law. *Check:* aifoundry3's
     per-degree tables re-read from the raw telemetry equal `sep-p1p3.json`'s exactly (`selftest-output.txt`).
   - **E71's six cycles** (27 Oct), `730cc8fc` `docs/reports/data/2026-10-27-e71-idle-slope-aifoundry3/slopes.json` and `8fab3404`
     `sep-p1p3.json`: per-degree dwell and mean board W. *Check:* all 162 committed per-cycle band fits of E44, E66 and E71 are reproduced
     from these tables by weighted least squares (worst 7.3e-15 W/°C), so the law rests on the same numbers as 0.3803 and 0.2936.
   - **E66's 18 cycles** (aifoundry2's idle, 26-27 Oct), as E71's re-fit tables `aifoundry2-58-62.json` (`730cc8fc`): aifoundry2's idle law.
   - **E97's pooled idle law**, `18e7683e` `e97.json` › `holds.idle_law_pooled`, as `docs/reports/data/2026-11-02-q138t-heat-model/heat_q138t.py`
     (`f5473428`) line 167 carries it: the law the heat chain closes through. *Check:* aifoundry3's nine-cycle law lies within
     **0.0028 W/°C** of it over 55-62 °C (two sensors, two methods, one law).
   - **Q138(t)'s chain**, `model-q138t.json` (`f5473428`) › `a3`, R = 0.8695 °C per board W: the loop gain g(T) = R × k(T).
   - **Q139(u)'s footing** (`d4c36bfe` FOOTING-RULE.md, `f47669d1` footing.json, `ca7dee2a` README C4): its F2 (E82 A2's dip rule) and
     F3 (each experiment's registered reducer with `--leak k --no-refit`) are kept unchanged; its F1 slope is replaced (FL3). *Check:* F1
     re-derived by independent code from the 123 committed passes gives 0.20564 / 0.31341 W/°C exactly, with reverse regressions 0.455 /
     0.512 (its C4 bound).
   - **E60's in-run slopes** (`dfee3d7a`, `docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt` lines 1, 11 and 19, and its telemetry):
     re-derived exactly (0.2026 / 0.4420 / 0.3273 W/°C over 149 / 179 / 229 runs). aifoundry2's 0.442 at 800 MHz and 617.4 mV stays in
     `tools/claims-v3/hpl/surface_hpl.py` (`4a58ed79`) line 40 as the check at that point (FL6).
   - **E171's and E172's arms** (`91f8ae40` scored.json with `d34f2be6` dated note 1; `b3255af1` scored.json and README lines 95-97):
     every rule already scored under each footing; used here for the scale's dependence on k (FL4) and as the record of what each footing
     gives. They are not re-scored, except under this rule, post hoc (FL7).
   - **M6's 4.5 s heat law** (`6a713a9f` m6.json; 0.118 °C per board W over a kinds window): the gain c1 that ties k to the session scale.
   - **The registered reducers**, unchanged: `tools/claims-v3/e171/reduce_e171.py` (`1b80da20`), `tools/claims-v3/e172/reduce_e172.py`
     (`14fcb30d`), `tools/claims-v3/kinds/reduce_e78.py` (`cfd94285`); and the scorer `tools/claims-v3/p8-600/score_p8_600.py` (`a518aa11`).
   - *The same quantity at the same operating point, earlier:* aifoundry3 at 600 MHz and 522 mV, 58-62 °C: E44's 0.3799 (Sep) and E71's
     0.3803 (Oct) per-cycle medians, and E97's law (0.3498 at 58 °C, 0.3992 at 62); this law reads 0.3509 and 0.3981. Card 1 at 600 MHz and
     499 mV: no earlier dedicated fit exists (this is the first of E44's card-1 cycles); Q139(u)'s 0.3134 and its reverse bound 0.512
     bracket this law at card 1's rest temperatures, 55-59 °C (0.415-0.496). aifoundry2 at its 600 MHz idle and 519 mV: E66's 0.2936 (51-58
     °C) and E71's re-fit 0.3452 (58-62) reproduced. aifoundry2 at 800 MHz and 617 mV: E60's 0.442, re-derived, the check (FL6).
3. **Not used.**
   - Q139(u)'s frozen slopes (0.2056 aifoundry3, 0.3134 card 1) as the footing of sessions registered after this commit: superseded by FL3.
     They stay the registered primary of every committed session that registered them (E140-E172), whose verdicts stand as registered.
   - The in-run slopes (E60's and E78's `--leak auto`, a session's own: 0.203, 0.285, 0.290, 0.403) as a law: they are per-run fits on a
     whole-degree reading, diluted and dependent on where the trace starts (Why, 3). Reported only.
   - The in-pass rests as a law (Q139(u)'s F1; E171's own 0.127, E172's 0.242): diluted (Why, 2). Reported only.
   - The September idle law (`2026-09-21-horace-aifoundry2/model.json`): superseded for both cards by E66 and E71 (E71's README).
   - One law in T and V: not identifiable from public data. Each card has one idle voltage; across cards the process spread dominates
     (card 1, at the lowest voltage, 499 mV, leaks most); aifoundry2's second voltage (617 mV, 800 MHz) has only an in-run slope. A
     dedicated cooling at 800 MHz needs the governor held there, which is a governor move: owed, on his word.
   - Card 0 (aifoundry1 card 0): no dedicated idle cycle has run there; M10's term e (its die-start footing) stays; owed.
   - aifoundry2's burst reduction (kspeed; Q139(u)'s F4: board W as sampled, no leakage term) and its governor model: not changed.
   - E73's heat-path poles and the camera runs (E62, E63): not applicable to a slope of board power on the die reading.
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code. No NDA-tier check is used, so there is no sha256
   line; no NDA-tier piece, name, verdict, ratio or figure is cited, and none of Q124's counts.

## Why one law, and which (post hoc reads of committed data; the evidence for the choice)

All of it is in this lane's post hoc data directory (`docs/reports/data/2026-11-05-q145a-footing-law/`, committed after this file), from
code that imports nothing of the lab's. The die reading is the firmware's whole degree (`temp_c.minshire[0]`) unless named.

1. **The quasi-static law is one law across methods and sensors.** A dedicated idle cycle heats the die, stops every launch, and fits board
   W against the reading over a cooling of minutes: the package cools as a whole, so the reading tracks the temperature the leakage sees,
   at a fixed clock and voltage. Pooled over aifoundry3's nine cycles (E44, E71) its slope is 0.3155 W/°C at 55 °C, 0.3509 at 58, 0.3745
   at 60 and 0.3981 at 62 (bootstrap over cycles at 58 °C: [0.3463, 0.3552]); E97's pooled rests (the 34-sensor mean, 1 Nov) give the same
   to 0.0028 W/°C. It rises about 0.012 W/°C per °C, as leakage's exponential does.
2. **The in-pass rests read the same law through a noisy thermometer.** Q139(u)'s rests are 1 s brackets before each launch; the launch
   gate puts every one within 0.5 °C of the target, so within a pass they spread only 0.33 °C (aifoundry3) and 0.36 °C (card 1), while the
   1 s mean of a whole-degree reading moves in 0.1 °C steps. The reading's error is a large part of that spread (within-pass R² 0.45 on
   aifoundry3), and ordinary least squares on an error-laden x is diluted. The reverse regression bounds it from above (0.455 / 0.512), and
   the law at the rests' temperatures sits inside the bracket on both cards (aifoundry3 0.351-0.363 at 58-59 °C, in [0.206, 0.455]; card 1
   0.415-0.496 at 55-59 °C, in [0.313, 0.512]). A Monte Carlo of the estimator with the true slope set to the law (0.36 / 0.49) and a
   reading noise that reproduces the observed 0.27-0.31 °C spread gives OLS 0.21-0.22 (true 0.36) and 0.28-0.31 (true 0.49), under
   reverse regressions of 0.53-0.70: the pattern of Q139(u)'s 0.2056 / 0.3134 under 0.455 / 0.512. As its C4 said: one frozen number per
   card, not a measured leakage.
3. **The in-run slopes are diluted too, and are not stationary.** E60's and a session's `--leak auto` fit one line per ~4 s run, while
   the reading climbs about 1.5 °C: one or two whole-degree steps, so each run's fit sees two or three distinct readings. Started later in
   the run, the same fits fall: aifoundry3 (E60) 0.203 → 0.124 → 0.096 W/°C from 0.8 / 1.5 / 2.0 s; E171 0.290 → 0.233 → 0.183; E172
   0.395 → 0.377 → 0.303; aifoundry2 at 800 MHz 0.442 → 0.400 → 0.340; card 0 0.327 → 0.271 → 0.226. The ensemble of the same runs,
   averaged over hundreds of launches before the line is drawn (so the whole degrees average out), climbs 0.30-0.54 W per degree of
   reading over 1-4 s on aifoundry3 (E171, E60) and 0.54-0.62 on card 1 (E172): at or above the law (0.36 / 0.49 at 58.8 °C). The
   Monte Carlo with the law's slope and that rise gives per-run medians of 0.29-0.59 of the truth. So the low in-run medians are the
   estimator, not a different leakage. E60's 0.442 on aifoundry2 is the same estimator at 800 MHz and 617 mV: in the direction leakage's
   rise with voltage predicts (an estimate from textbook device physics, not a measurement: subthreshold current through drain-induced
   barrier lowering, and gate tunnelling, grow by roughly 1.5-1.8x for +98 mV), but by a
   method that reads aifoundry3 at about 0.56 of its law, so it is not a voltage coefficient and not a law; it is the right referral for
   its own use (surface_hpl.py refers each burst sample within a burst, the same in-run method at the same point).
4. **Only the quasi-static law closes the steady heat balance.** E97's three holds closed on E78's switching power within about 2% with
   that law's leakage part: (board rise − leakage) / (S × compute share) = 0.990, 0.991, 1.001. With a constant 0.2056 W/°C the same holds
   read 1.149, 1.169, 1.232; with E171's own 0.285, 1.048, 1.064, 1.127; with E60's 0.203, 1.152, 1.173, 1.236. Switching power cannot be
   15-23% above what E78 measured in the same kinds, so the leakage of this card at 51-70 °C is the law's, and the footing's 0.2056 is not
   a leakage.
5. **The footing's slope and the session scale are one degree of freedom on the floats.** Across E171's committed arms the float scale
   follows s(k) = 1.0321 (1 − 0.1234 k) (k 0 to 0.3803 W/°C, five arms); on E172 s(k) = 1.0452 (1 − 0.1133 k). The factor is the 4.5 s heat
   law (about 0.12 °C per board W): the window's rise is about 0.12 °C per watt of the run, so a change of k is a gain on every float D,
   and the session's float scale absorbs it. A session's own kinds cannot fit k beside s; only int8 (which takes no session scale), the
   pass gates and second-order terms see k.

## The rule

- **FL1. The law.** For each card at its idle operating point, k_c(T) = 2 q0 T + q1 with q from [`footing-law.json`](footing-law.json),
  built by [`footing_law.py`](footing_law.py) `build` from the committed cycles above (the firmware's whole-degree reading):
  - aifoundry3, 600 MHz, 522-523 mV: q = (0.0058999, −0.3334632, 25.42157), degrees 52-66, nine cycles; k = 0.3509 at 58 °C, 0.3627 at 59;
  - aifoundry1 card 1, 600 MHz, 499 mV: q = (0.0101684, −0.7038227, 39.70767), degrees 56-70, three cycles (one session, 25-26 Sep);
    k = 0.4757 at 58 °C, 0.4961 at 59 (bootstrap [0.4122, 0.4999] at 58: three cycles);
  - aifoundry2, its 600 MHz idle, 519 mV: q = (0.0058041, −0.3351545, 25.18637), degrees 49-62, 18 cycles; k = 0.3381 at 58 °C.
- **FL2. The heat chain's loop** on aifoundry3 closes through E97's law, unchanged; FL1's aifoundry3 law is the same law within 0.01 W/°C
  over 55-62 °C (checked by `footing_law.py selftest`; worst 0.0028), so the loop and the footing share one law. The loop gain stays
  g(T) = 0.8695 × (2 × 0.0061754 T − 0.36659): 0.272 at 55 °C, 0.304 at 58, 0.347 at 62, 0.390 at 66. A chain built later for card 1 or
  aifoundry2 closes through that card's FL1 law.
- **FL3. The power model's footing** (aifoundry3 and card 1, kinds sessions at 600 MHz): a session's slope is k_s = k_c(T_mid), T_mid the
  median over the session's runs that pass every per-run gate of (launch reading + window reading) / 2 (`footing_law.py k <law> <card>
  <runs.csv>`; both columns are independent of k), passed to the session's registered reducer as `--leak k_s --no-refit`, with Q139(u)'s
  F2 (A2's dips removed on both 600 MHz cards) and every other part of the registered reduction unchanged. **One footing for training
  rows and tests alike** (Q139(u)'s principle): FL3 becomes a session's primary only for a model fitted on rows re-reduced by FL3 (each
  training experiment at its own T_mid, through Q139(u)'s `reduce_footing.reduce` route, then the model's form refitted: owed to a later
  lane, "M10 on the law"). Until that refit exists, **every 600 MHz kinds session registered after this commit reports FL3 as a
  registered arm** beside its primary (the frozen model's own footing), with FL7's first-order one-footing companion, both frozen in its
  registration before its data; after it, the session names FL3 primary and Q139(u)'s frozen slope is the arm.
- **FL4. The session scale, jointly.** Term a's float scale s is read on the session's own random anchors after FL3, as registered. Neither
  k nor an intercept is fitted on the session: on the floats k and s are one degree of freedom (Why, 5), so the pair is fitted jointly in
  the only form the session identifies, s at the law's k.
- **FL5. The checks at the session's temperature** (reported beside, never a gate of a verdict):
  - (a) k_s against FL1's bootstrap interval at T_mid, and against E97's law at T_mid (aifoundry3);
  - (b) the session's ensemble in-run slope: the mean board-power and reading profile of every gated run, its straight line over [1, 4] s;
  - (c) **the blind check of the law:** a no-launch cooling of at least 420 s from at least 62 °C (E71's form), or rests of minutes after
    holds (M11's), read by E71's method (or E97's on the 34 raw codes); PASS if its slope at T_mid lies within ±0.02 W/°C of k_c(T_mid)
    (E71's between-cycle sd is 0.0036 W/°C; the nine cycles' interval at 58 °C is ±0.0045; the line also allows E44-to-E71's 0.013 at
    58 °C), FAIL outside, NOT SCORED with fewer than 300 samples in the band.
- **FL6. Where it does not apply.** aifoundry2's governed bursts keep their reduction and their governor model; E60's 0.442 W/°C at 800
  MHz and 617 mV stays in surface_hpl.py as the referral and the check at that point (a 600 MHz law there would understate it). Card 0
  keeps M10's term e. No committed verdict, frozen file or hash list changes.
- **FL7. The post hoc study, after this commit (new files, labelled post hoc; it decides nothing).** E171 and E172 re-reduced at FL3's
  k_s (E171: T_mid 58.775 °C, k_s 0.36007; E172: T_mid 58.85 °C, k_s 0.49300; `k-e171.json`, `k-e172.json`) by their registered reducers
  and scored by the registered scorer with that reduction as the primary: M1, M1f, A1, KA, P8-KA pooled, B1, B2, P1-P3, LG and G. Because
  M10 and M9 were fitted on Q139(u)'s footing, that arm mixes the footing with a train/test footing mismatch; a first-order one-footing
  companion (every unscaled prediction multiplied by 1 − c1 Δk, c1 from Why 5) is reported beside it, and the exact one (M10's rows
  re-reduced by FL3 and refitted) is owed to a later lane. The chain's loop gain under FL2.

## What it answers, and the first blind tests

- **The law, blind:** FL5(c) on **M11's next session on aifoundry3** (E176's successor; its run number is the orchestrator's): its rests
  after holds are quasi-static coolings read on the 34 raw codes, and FL1 / E97 predict their pooled slope at 52-58 °C (0.28-0.35 W/°C)
  within ±0.02 W/°C. On card 1, the first test is a 420 s cooling after the last pass of its next kinds session (about 7 card-minutes):
  card 1's first dedicated cooling since 26 Sep.
- **The footing's consequences, blind:** the next 600 MHz kinds session on aifoundry3 or card 1 (pool 8's day 2 or pool 9, not yet
  registered), with FL3's arm and its first-order companion frozen in that session's registration (FL3), or with FL3 primary if "M10 on
  the law" is fitted first: does M10's lead over M9 (M1) and term a's carry (A1, KA) hold when the footing is the leakage law rather than
  the diluted rests? If they hold, they were never the footing's; if they fail, the registered-footing reading of 5 Nov was.
- **What each outcome of FL5(c) means:** PASS, the reduction and the loop rest on one measured law on that card; FAIL, the card's law moved
  (or the reading's offset did) and FL1 is re-built from the new cooling by a dated amendment before the next session.

SPDX-License-Identifier: Apache-2.0
