# Dated note 1 beside design-power-heat.txt (Thu 5 Nov 2026; Q142(h)'s fix pass) - kept as committed; the figures design-power-heat-v2.txt supersedes, and why

*`design_power_heat.py`, `design-power-heat.txt` and `design-power-heat.json` (lab commit `3c31a91d`, 07:41:57 PST) stay as committed:
this printout is the first output, kept. The faults the lane's verifier found in its code, and one this fix pass found, are fixed in a
new file, [`design_power_heat_v2.py`](design_power_heat_v2.py). Its output, [`design-power-heat-v2.txt`](design-power-heat-v2.txt) and
[`.json`](design-power-heat-v2.json), supersedes the figures below. Amendment A1 ([`REGISTRATION.md.dated-note-1.md`](REGISTRATION.md.dated-note-1.md))
says what each change does to the registration. v2 checks this file's code and JSON against `SHA256SUMS-m11` before it imports the code,
unchanged.*

## Superseded

- **§ 2, H_E's rows.** Q138(t)'s `closed_loop` rounds each piece of a schedule to its 0.2 s grid:
  - H_E's cool pattern, 3.456 s on and 4.104 s off, ran as 3.4 and 4.2 s: a modelled share of 0.4474 against the recorded 0.4571,
    −2.1%;
  - the warm pattern, 2.965 and 5.015 s, ran as 3.0 and 5.0 s: 0.375 against 0.3716, +0.9%.

  On an exact grid (v2 § 2': 0.008 s cool, 0.005 s warm, the marks on the same grid), over the registered window [b − 300 s, b):

  | room | H_E's P | H_E's peak | Z's P |
  |---|---|---|---|
  | 51.2 °C | 14.205 → **14.517** °C | 67.79 → **68.13** °C | 0.731 → 0.695 °C |
  | 51.5 °C (not printed here) | 14.268 → 14.582 | 68.17 → **68.51** | 0.721 → 0.684 |
  | 52.0 °C | 11.856 → **11.723** | 66.27 → 66.15 | 0.974 → 0.986 |

  L1, S and L2 move by at most 0.002 °C. Over describe's window, which this file used and which includes the last off-gap, H_E reads
  0.012-0.021 °C higher (14.538 °C at 51.2 °C).
- **§ 3, aifoundry3's tables** (A3 x2, x1, x3). Their P comes from the plan, and v2 runs the same draws at the exact plan. The two-session
  table moves by at most 0.8 points in any cell: GAIN 88.2 → 88.5% at a 3.2% gain, LEVEL 89.3 → 89.4% at 0.27 °C, NOT SEPARATED 93.1%
  unchanged with no effect. The one- and three-session tables move by at most 1.8 points: one session 67.1 → 68.6% and 64.6 → 65.2%.
- **§ 4, S7-W's rates at 1.5 σ.** This code compared each held-out session's change with the simulated noise over √n_σ. REGISTRATION.md
  § 7 fixes the threshold at σ_c = 0.0884 °C. At the registered threshold, a gain or a level fitted on no effect reads "worse" in
  21.8% and 21.3% of the same draws on this plan (21.9% and 21.3% at the exact plan), not 11.3% and 10.8%. The rates at σ are the
  registered ones, and v2 reproduces them exactly.
- **§ 4b, HM-AG.** This file computes the gain and level forms only. v2 adds BOTH's form, F(2(k − 1), n − 2k), on the same draws. It
  sees the difference between E154's fit and E166's in 98.0% of draws on this plan (98.2% at the exact plan), so § 4's "with two
  sessions HM-AG rarely sees a difference that HM-LG reads as BOTH" is superseded (A1-4).
- **§ 5, H_E's readings.** H_E's P comes from the plan; each rate moves by at most 1.8 points, for example HM-E144 inside under a
  0.27 °C level 27.3 → 29.1%.

## Unchanged, and reproduced by v2

- § 1, the noise: aifoundry3 0.0884 °C over 11 residuals (6 degrees of freedom), aifoundry2 0.2296 °C, the readout floor 0.3019 °C.
- § 2's 0.2 s plan at 49.5, 51.2, 52.0 and 53.0 °C, byte for byte.
- § 3's aifoundry2 tables: they do not use the aifoundry3 plan, and v2 does not re-run them.
- § 4's rates at σ, exactly, on this plan.
- § 4b's gain and level shares, exactly, on this plan.
- § 6, the precision for terms (c) and (d).
