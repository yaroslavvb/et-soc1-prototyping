# Amendments to the pre-registered plan

Each amendment is recorded before any data of the experiment it touches exists. The run code that implements the
plan is committed under `tools/claims-v3/` (one directory per experiment, with its `README.md` listing where the code
departs from PLAN3's command lines and why); every block records the sha256 of the code it ran (`code.sha256`).

**A1 (25 Sep 2026, before any V3-IDLE data).** IDLE-b ("every whole-degree bin inside -0.23 ± 0.3 W") leaves out
each cycle's first and last bin. The die temperature is read in whole degrees, so a cycle's edge bins average only
part of a degree and are biased by 0.1-0.3 W on aifoundry2 (the reviewer's simulation), which would fail the item
from rounding, not physics. `tools/claims-v3/idle/reduce.py`.

**Readings confirmed, not amendments** (the reviewers asked; the registered rules stand as the code implements them):
- a telemetry sample with no clock field is a gap, not a drop (V3-MEM); with fewer than three kept passes a card is
  undecided even after an every-pass failure (all experiments);
- band items pass only when the 99% interval excludes the null *and* the estimate lies in the band; a sign-only
  result counts as a failure (V3-CAT, V3-WIRE, V3-ABL);
- V3-X5 keeps its registered hot target on aifoundry3 (65 °C launch, 68 °C preheat) although it is probably out of
  reach there; the registered correction to the launch temperature applies, and the reached temperatures are reported;
- V3-RL's RL-g scratchpad parts pool the zeros and random passes as registered; their readings say so;
- the scratchpad bus-error probe (`LAT_SCPSELF`) is not run: it faults a shared card on purpose, and the claim it
  would test (hotline-relay-l2-52) stays labelled one card.
