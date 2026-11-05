# Dated note 2 beside README.md, Wed 4 Nov 2026 (week 45), written by 23:11 PST: the chain's misses are a session level or a gain, not separated (post hoc; Q142's records)

*Written beside [`README.md`](README.md) and not inside it; the README and [dated note 1](README.md.dated-note.md) stay as committed. It
records a reading by Q142's round critic (Wed 4 Nov 2026, about 22:02–22:40 PST), re-derived here with new code,
[`posthoc_heat_level_gain.py`](posthoc_heat_level_gain.py), whose output is [`posthoc-heat-level-gain.txt`](posthoc-heat-level-gain.txt).
Post hoc: no rule registered it, and no verdict, number, band, prediction, rule or frozen file changes. Desk only. It answers the
same items as the README: the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)
items 9 and 8, and rank 3 of Q139's final critic.*

## What it corrects

The README reads the chain's misses as a gain: "So E154's gain deficit repeats in sign, about a third smaller", and "The heat model's
gain deficit is real and repeatable on this card". 03's E166 entry says "a gain deficit". Those words stay as written. Read them as
**a session level or a gain, not separated**: within this session the misses do not grow with the rise.

## Why: the misses given the watts, session by session

The input is `heldout-m10.json` › `heat_d_chain_gain.holds` in [`2026-11-04-q142m-m10/`](../2026-11-04-q142m-m10/README.md) (lab
`6829c9ba`, listed in that directory's `SHA256SUMS`). For each hold it gives the measured plateau rise R and the error e: measured
minus Q138(t)'s frozen chain, given the measured watts. A pure gain makes e grow with R through zero; a session level makes e flat
in R.

| Session (card) | Holds: R, e (°C) | e = a + g R, least squares | A level alone | A gain alone, through 0 |
|---|---|---|---|---|
| **E166** (aifoundry3) | K_L 4.41, +0.403; K_Q 6.66, +0.200; K_O_window 11.27, +0.242; K_S 12.73, +0.233 | a +0.395 °C, g −1.43% of R; residual 0.062 °C | +0.270 °C; residual **0.079 °C** | +2.50% of R; residual 0.155 °C |
| **E154** (aifoundry3, a day earlier) | K_L 4.02, +0.073; K_Q 5.67, +0.005; H_M 11.21, +0.352; K_O 11.55, +0.536; K_S 11.79, +0.418 | a −0.229 °C, g +5.72% of R; residual 0.076 °C | +0.277 °C; residual 0.204 °C | +3.45% of R; residual **0.110 °C** |
| **E144** (aifoundry3, 2 Nov) | H_L 4.25, −0.032; H_H 15.00, +0.015 | — (two holds) | −0.008 °C; residual 0.023 °C | +0.04% of R; residual 0.024 °C |

- **In E166 the misses are flat, or falling, in the rise:** a level alone fits them better than a gain alone (0.079 against
  0.155 °C). **In E154 they grow with it:** a gain alone fits better than a level alone (0.110 against 0.204 °C). E144 has no miss
  to split: its 15.00 °C rise was read to 0.1%.
- **Over the nine large rises** (fitted, R at least 10 °C, as M10's term (d) selects them), eight read 1.83–5.60% low given the
  watts, and E144's +0.10% (the output, section 1).
- So one gain averages two patterns. RK3-c registers the relative misses of large rises only, and no registered rule tests a
  level against a gain. With two to five holds a session, these are readings, not tests.

## What it does to predicting heat

Nothing frozen changes. M10 ([`2026-11-04-q142m-m10/`](../2026-11-04-q142m-m10/README.md); held out, not blind) already carries the
chain unscaled as its primary and the +3.2% gain as a reported arm, because the gain makes E144's rise 0.53 °C worse (its
registration's section 7, read by amendment A2). Held out, the nine large rises read 0.493 °C rms with the chain unscaled and
0.294 °C with the arm. The next heat registration should test a session level against a gain, with two or more rise levels in
each session and one hold like E144's, which the chain already reads well.
