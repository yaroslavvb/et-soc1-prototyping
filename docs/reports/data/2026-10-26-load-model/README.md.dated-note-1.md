# Dated note 1 beside README.md (Fri 6 Nov 2026, week 45): the joined whole-load model is retired

*Beside [`README.md`](README.md), which it edits nowhere; the model's files here (`frozen_predictions.json`, `scores.json`,
`refit_on_recount.json` and the rest) and its code (`tools/ettelem/load_model.py`, `predict_load.py`) stay as committed. Written by the
records round after Q147 (Q148(r)), desk only.*

**Retired, on the owner's word.** On Thu 5 Nov 2026, about 22:35 PST, answering the stock-take's open question whether to revive this
model (Q126(c)), the owner wrote *"Your choice, see what's relevant for the blog post."* The choice made: **retire it**, from that date
([`02-requests.md`](../../../findings/02-requests.md), Q147, item 8).

**Why.** The post this work serves asks how the kind of numbers in a matmul sets its power, its heat and its speed
([`02-requests.md`](../../../findings/02-requests.md), Q130). That question is served by the kernel power model (M10,
[`docs/reports/data/2026-11-04-q142m-m10/`](../2026-11-04-q142m-m10/README.md), blind on pool 8), the heat laws and the heat chain, and
the one-number matrices (E178, E180). A predictor of a whole workload's watts, clock and die temperature, which this model is, lies outside
it. Nothing replaces it, and no whole-load model is being built.

**What it keeps.** Its held-out scores stay as frozen and as the README gives them (lines 99-101): **E39**, the gemv sparsity ladder,
**1.10 W rms** over six independent predictions (bias −0.75 W; 2 of 3 slopes outside the measurement's 99% interval); **E37**, mmbench
fp32 from DRAM, **2.14 W rms** (bias +2.13 W, every card high); **E59**, sparse parity, **3.02 W rms** (bias −2.92 W, every size low).
Those, with every caveat beside them (the freeze is by commit order, not blind; three constants come from the held-out loads), remain the
record: [`05-claims.md`](../../../findings/05-claims.md), "Pricing a whole load".

**What would revive it.** A whole-workload question from the owner. Then a refit that carries M10's kernel term in place of the 21 Sep
flip prices, with the energy catalogue's memory and mesh energies ([`docs/energy-manual/`](../../../energy-manual/README.md)) and the
current leakage footing, scored held out on E39, E37 and E59 first, before any new load is predicted.

No number, verdict or frozen file changes, and no file under `tools/claims-v3/` reads this model.

SPDX-License-Identifier: Apache-2.0
