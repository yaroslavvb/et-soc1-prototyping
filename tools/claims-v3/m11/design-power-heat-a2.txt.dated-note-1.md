# Dated note 1 beside design-power-heat-a2.txt and .json (Thu 5 Nov 2026; Q142(a2)'s fix pass, amendment A3) - what A3's power file re-ran, the one figure the exact t point changes, the pair taken by position, and the rows A3 adds

*Written on Thu 5 Nov 2026, on the Intel, desk only. [`design-power-heat-a2.txt`](design-power-heat-a2.txt) and
[`.json`](design-power-heat-a2.json), the first output of [`design_power_heat_a2.py`](design_power_heat_a2.py) (lab `d3d97fe2`, 10:07:42
PST), stay as committed. Amendment A3 ([`REGISTRATION.md.dated-note-A3.md`](REGISTRATION.md.dated-note-A3.md)) governs. Its power file,
[`design_power_heat_a3.py`](design_power_heat_a3.py), re-runs every cell of this output on the same draws ([`design-power-heat-a3.txt`](design-power-heat-a3.txt)
and `.json`).*

- **Reproduced exactly.** All 74 cells of `design-power-heat-a2.json` were recomputed with `design_power_heat_a2`'s own functions on v2's
  committed draws. Each equals the committed cell (`design-power-heat-a3.txt` § 3). Every figure here stands, except as below.
- **Superseded: N2 at HM-HE's exact t point.** This output read HM-HE, which N2 reads, at a t point rounded to three decimals (4.303 at 2
  degrees of freedom). REGISTRATION.md § 3 registers the exact point, 4.30265.
  - At the exact point one cell changes: § 6, one aifoundry3 session under a 3.2% gain (the ×1.032 arm), N2 4.7% → 4.8%.
  - No other N2 figure, no entry share, no "BETTER with no clause met" share and no adoption value changes.
  - The same rounding in `design_power_heat.he_rates` moves one cell of `design-power-heat-v2.txt` § 5': a 0.15 °C level with a 0.3 °C miss
    on H_E, HM-HE departs 22.9% → 23.0% (A3-7 (c)).
- **The pair by position.** `session_cal` takes a session's first two scored holds as its calibration pair. Every simulated hold is scored
  here, so its figures stand: the pair by name gives the same reading on all 780,000 simulated sessions. A scorer must not reuse it: with
  H_E not scored it would pair Z with L1 and read a session that A2-1 reads NOT SCORED (A3-6).
- **Extended.**
  - § 5's premise table, by `design-power-heat-a3.txt` § 6 (A3-2): H_E read by the chain as E144's `H_H` was, under every truth; H_E −0.3
    and −0.5 °C; the fp32 pair ±0.15 °C.
  - HM-E144 beside HM-CAL in every aifoundry3 cell (§ 5; A3-5).
  - A1-4's BOTH-and-differ row, 98.4% at σ_c (§ 4; A3-7 (a)).
