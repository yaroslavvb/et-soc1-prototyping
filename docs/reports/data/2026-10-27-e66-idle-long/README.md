# E66 — IDLE-L on aifoundry2: the long cooling E44 never ran (Q128)

*Pre-registered Mon 26 Oct 2026 (week 44) 21:2x PDT on aifoundry2, **before the first E66 pass**; any change after
this commit goes in the Amendments section at the end, dated, before the data it touches. Request Q128(b).
The data land on this path in the morning, after the overnight run is reduced.*

**Deviation from the ask, stated plainly.** Q128(b) asked for E66 and E68 to be pre-registered in **one** commit
before E68's first launch. E68's registration went out alone in `b88c6bdc` and its first measured launch ran at
21:11:45 PDT; this file is a second commit, written before E66's first pass and before any E66 data exists, so
E66 is still registered ahead of its own measurement, but the single-commit instruction was not met.

## Why this pass

E44 ran V3-IDLE's nine short cycles on three cards on 25–26 Sep 2026 and left two of its items open, both for the
same reason: **the overnight IDLE-LONG passes were never scheduled.**

- **IDLE-L was INSUFFICIENT.** The fixed/leakage split of idle power — how much of the card's resting draw is a
  constant and how much is leakage that grows with temperature — has never been identified on this card. A short
  900 s cooling leaves the exponential's profile flat, so the fit is unidentified by construction.
- **IDLE-d stayed open.** aifoundry2 cooled only to 67–77 °C in 15 minutes, so the 73 °C rail split had a bin in
  two cycles of three.

**And the model needs it tonight.** E64's governor model regulates a ~1.3 s average of board power to 65 W and
trips at a 66 °C die reading, and the card idles near 51 °C. Everything the chain says about how much of that 65 W
budget is available for switching depends on how much of it leakage has already taken — over exactly the band
**51–67 °C**, which a 15-minute cooling on this card never reaches and a 90-minute cooling does. The idle law in
use, `12.6349 + 23.2568·e^((T−80)/36)` W (`2026-09-21-horace-aifoundry2/model.json`, 21 Sep), is the one the power
model assumes; nothing has tested its two terms separately on this card.

## Method

`tools/claims-v3/idle/block.sh <pass>`, unchanged, passes **11, 12, 13 …** (IDLE-LONG numbering): 2 s random-data
fp32 fma bursts on 1,024 minions, back to back under `hold10`, until the minion-shire reading reaches 88 °C or
150 bursts or 900 s; then **5,400 s with no launch**, `ettelem` at 10 Hz, board power, the three rails
(minion, SRAM, mesh), clock, on-die voltage and temperature. The block takes the card lock for the pass, polls
every 10 s for another user's device process or a rise in the `et_soc1` use count and aborts the cycle if it sees
one, and releases the lock between passes. About 93 card-minutes per pass.

The heater is the one E44 used on this card, and it is **not** held under 60 W: at 1,024 minions on random data it
asks for ~82 W and the governor regulates it to the 65 W board limit. That does not touch the measurement — rule A
drops every sample from 1 s before to 6 s after any launch, and the whole measured window is the cooling, with no
launch in it and idle power of 26–35 W.

**It stops by itself.** The runner starts a new pass only while the clock leaves room for it to finish, so the last
pass ends **no later than 06:30 PT** and the lock is released. The card claim in `#community-lab`
(message `1564491254660595715`, 21:09 PDT) covers the night and is released in the morning, after the reduction.

## Pre-registered analysis

`tools/claims-v3/idle/reduce.py --data <dir> --out verdicts.json`, unchanged, which carries IDLE-L's registered
rule for this card: `flip_thermal_model.py` step 2a exactly (no launch within 4.5 s, the first 20 s of the pass and
off-600 samples dropped), fitted per cycle, with the aifoundry2 bands **T_L in [30, 45] °C, A80 in [19, 29] W and
A80/T_L in [0.62, 0.68]**; the split counts as identified only if A80's interval is narrower than ±3 W. Bins are
whole degrees with n ≥ 20; intervals are two-sided 99 % t over cycles.

On top of it, the 51–67 °C reading Q128(b) asks for, computed from the same per-cycle fits:
P(T) = B + A80·e^((T−80)/T_L), leakage share = A80·e^((T−80)/T_L) / P(T).

## Predictions, frozen with this commit

- **L1 — the e-folding.** The fitted T_L lies in **[30, 45] °C** (the registered band), and its 99 % interval is
  narrower than ±8 °C — that is, the long cooling identifies what the short one could not. The published law's
  value is 36 °C. A T_L interval still wider than ±8 °C means 90 minutes is also not enough, and is reported as
  such rather than as a fit.
- **L2 — the split is identified.** A80's 99 % interval is narrower than **±3 W** (the registered threshold) and
  lies in **[19, 29] W**, with the fixed term B in **[9, 16] W** (the law's 12.63 W).
- **L3 — the fixed/leakage split over 51–67 °C.** Taking the law at face value, leakage is 10.40 W of 23.03 W at
  51 °C and 16.21 W of 28.84 W at 67 °C. So the registered prediction: the leakage share rises from
  **0.38–0.52 at 51 °C** to **0.49–0.63 at 67 °C**, and the rise across the band is **+0.06 to +0.16**. If the
  share at 51 °C is below 0.38 the card's resting draw is more fixed than the law says, and the switching budget
  under the governor's 65 W is correspondingly larger.
- **L4 — the floor is reached.** At least one cycle's cooling reaches **≤ 53 °C**, so the 51–67 °C band is
  measured rather than extrapolated. If the lowest bin is above 53 °C, L3 is reported as an extrapolation and
  scored UNDECIDED below the lowest bin reached.
- **L5 — IDLE-d closes.** With a 73 °C bin in at least 3 kept cycles, the four rail values (minion, SRAM, mesh,
  unsensed) each fall within **±0.2 W** of the 22 Sep split 11.05 / 2.00 / 3.64 / 15.10 W — the registered IDLE-d
  rule, which E44 could not score.

## Decision rules

Each prediction is scored PASS / FAIL / UNDECIDED against its own stated band, in the results section of this
README. UNDECIDED where an interval straddles a band edge, where fewer than 3 cycles are kept, or where the
temperature band was not reached (L4). A cycle whose `block.json` is not `ok` — an intrusion, three failed heater
bursts in a row, a sampler failure or a failed check — is dropped by `reduce.py` and named in `verdicts.json`
`passes`; it is never re-registered.

## Amendments

**A1, Mon 26 Oct 2026, 22:4x PDT (written during pass 11's cooling, which began at 22:37:37; before any E66
cooling data had been fitted, and before passes 12 and later).** The plateau this card reaches tonight is
**70 °C, not 88 °C**, and that changes how L2 must be read.

Pass 11 heated for 398 s and stopped on the registered 150-burst cap, not on the 88 °C target
(`marks.jsonl`: `heat_end die_c 70, reason "bursts", bursts 150`). Stopping on the cap *is* the registered
method; what is new is where the die stops climbing. E64 measured this card's governor tripping on a **66 °C**
die reading, so a 1,024-minion random-data heater cannot take it much past that — E44's 88 °C on 25 Sep is not
reproducible here tonight, and E64 saw the same ceiling ("a random-data heater cannot take this die past
~67 °C, because the two limits hold it there").

What it costs and what it does not:

- **L3 and L4 are unaffected, and in fact better served.** The cooling runs 5,400 s from 70 °C, so the whole
  **51–67 °C** band Q128(b) asks for is measured rather than extrapolated, and none of the 90 minutes is spent
  above it.
- **L1 (T_L) is unaffected in kind** — it is fitted over whatever range the cooling covers — though the range
  is now about 19 °C wide instead of 37, so its interval will be wider than a cooling from 88 °C would give.
- 🛑 **L2 (A80) becomes an extrapolation.** A80 is the law's amplitude *at 80 °C*, 10 °C above anything
  measured tonight. Its registered bands ([19, 29] W, identified only if the interval is narrower than ±3 W)
  therefore test an extrapolated parameter, and the result must say so. The directly measured equivalent — the
  leakage term at the top of the measured range — is reported beside it.

No rule, band or command changes; `e66_split.py` already fits whatever bins the cooling provides and reports
each cycle's lowest reading, which is what L4 scores.
