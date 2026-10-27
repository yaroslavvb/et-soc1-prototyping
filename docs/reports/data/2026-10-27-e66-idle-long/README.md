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

**A2, Mon 26 Oct 2026, 23:1x PDT — the record of a pass this session ended. Written before any pass after 11.**

🛑 **Pass 11 was cut short at 23:09:57 PDT by this session**, 32 minutes into its 90-minute cooling. A review of
E68 had asked whether the night's remaining card time could be re-tasked (A3 below); the signal sent to the
overnight driver — meant to stop it *after* pass 11 — reached the whole job, because a non-interactive bash
passes a fatal signal on to the foreground process group it is waiting on. The block got no chance to finish:
`p11/` has **no `block.json`**, its `telemetry.jsonl` was never gzipped and `marks.jsonl` carries no `abort`
mark, so **the registered reduction drops p11 as a non-ok pass**. It is not re-registered, and no verdict below
rests on it.

What it still holds, and why its profile is quoted in A3: p11's cooling ran **1,940 s from 22:37:37, 70 °C down
to 49 °C** — and on this card that is the *whole* informative part of a cooling. The die passes 51 °C at
t+207 s and is at its floor by t+278 s. The raw pass stays on the box at
`build/claims-v3/aifoundry2/idle/p11/` (ungzipped telemetry, 16 MB) as the measurement A3 is argued from; it is
not published as a kept pass and it is not scored.

**A3, Mon 26 Oct 2026, 23:2x PDT — the cooling drops from 5,400 s to 900 s, and the night runs many cycles
instead of four. Written before the first pass it touches (pass 12), and before any data from it exists.**

*Why.* The registered 5,400 s cooling spends **94 % of its card time at the floor**, and buys nothing over the
registered **900 s** short cooling on this card. Measured on p11's own telemetry (A2), seconds of idle samples
per whole degree over the cooling:

| die °C | 69 | 68 | 67 | 66 | 65 | 64 | 63 | 62 | 61 | 60 | 59 | 58 | 57 | 56 | 55 | 54 | 53 | 52 | 51 | 50 | 49 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| seconds | 0.7 | 1.2 | 2.0 | 3.2 | 4.1 | 5.5 | 6.3 | 7.2 | 7.8 | 9.1 | 10.0 | 11.2 | 13.4 | 13.9 | 16.9 | 22.4 | 31.8 | 41.3 | 73.9 | 1343 | 218 |

**280.0 s** of the cooling lie in the registered **51–67 °C** band, **55.2 s** of them above 59 °C — and
**every one of those seconds falls in the first 300 s.** A 300 s cooling and a 5,400 s cooling collect
identical in-band data; the remaining 5,100 s are the die resting at 49–50 °C.

So the Q128(b) band is served by *repetition*, not by length. With a **900 s** cooling — the length this
tool's own short cycle uses, so `reduce.py`'s items 0, a–f and k (which read each cycle's first 900 s) see a
complete cooling, and item L (which reads a long cycle whole) sees the same 900 s:

| | registered (5,400 s) | A3 (900 s) |
|---|---:|---:|
| cycle length | ~99 min | ~24 min |
| cycles before 06:30 | 4 | ~17 |
| seconds in 51–67 °C | 1,120 | ~4,760 |
| seconds above 59 °C | 221 | ~938 |
| cycles for the 99 % t-interval | 4 (3 dof, t = 5.84) | ~17 (16 dof, t = 2.92) |

The interval-width thresholds L1 and L2 are scored against (±8 °C on T_L, ±3 W on A80) are **between-cycle**
intervals, so the cycle count is what decides whether they can be met at all; four cycles halve nothing. This
amendment roughly halves the t multiplier before any gain from the extra in-band samples.

*What changes, exactly.* `tools/claims-v3/idle/block.sh` gains one **default-preserving** knob, in the manner of
the two E68 added to `hl/block.sh`: `IDLE_COOL_S` overrides the long variant's cooling length, and the long
variant's pass range widens from 11–19 to 11–49 so the extra cycles have numbers. With `IDLE_COOL_S` unset,
every pass 11–19 behaves exactly as before; nothing E44 ran changes. The driver becomes
`~/q128b/run_e66b.sh`, the same loop with `IDLE_COOL_S=900` and a pass budget of 1,500 s.

*What does not change.* The heater, the 88 °C target and 150-burst cap, the 10 Hz sampler, the intrusion poll,
the card lock, the registered reduction (`reduce.py`, unchanged), every band and threshold in L1–L5, and the
06:30 PT stop. The cooling length is the one parameter touched, and it is set to the value this tool already
uses for its short cycle.

*What it costs.* The long dwell at the floor is gone from every cycle after 11 (about 300 s per cycle at
49–50 °C remains, and ~17 cycles give more floor samples in total than four long ones did). L5 (IDLE-d, a
73 °C bin) was already out of reach tonight at a 70 °C plateau (A1) and stays so.

🛑 *And it corrects A1's wording.* A1 said the 5,400 s cooling meant *"the whole 51–67 °C band Q128(b) asks
for is measured rather than extrapolated"*. On the profile above that was true only of **51–58 °C**: a
single cycle spends 225 s there but just **55 s** above 59 °C, and 1.2 s at 65 °C, so four cycles would have
given about three and a half minutes in the band's upper half and nothing above 69 °C. Scored on four long
cycles, L3's top end would have been a claim resting on seconds. It is A3's ~17 cycles, not A1's length,
that make the band measured: ~16 minutes above 59 °C instead of ~3.7. Where the morning's fit still rests
on thin bins at the top, say so with the per-degree sample counts beside it.

**A4, Mon 26 Oct 2026, 23:2x PDT — the night runs from pass 13, not pass 12, and the driver now sets `USER`.
Written before pass 13's cooling data was read.**

A3 says it is written "before the first pass it touches (pass 12)". Pass 12 did start under A3, at 23:14:32,
and was **aborted at 23:16:16, 104 s in, still in its heat phase with no cooling data**. Its directory
`build/claims-v3/aifoundry2/idle/p12/` has no `block.json`, so both reducers drop it exactly as they drop p11.
**The night's measured passes are p13 upward.**

*Why it was aborted.* The driver's log filled with `lib.sh: line 64: USER: unbound variable`. `tmux
new-session` starts its pane with no `USER` in the environment, and both `lib.sh`'s `others_present` and
`block.sh`'s `other_logins` read `"$USER"` under `set -u`. The fault is inside a `$( )`, so only the subshell
dies and the pass runs on — but the variable reads empty, and the **"another user is logged in" guard silently
passes every time**. For a seven-hour unattended run on a shared lab card that is not acceptable, so the pass
was stopped while it had produced nothing, `USER` and `LOGNAME` were exported in `run_e66b.sh`, and the run
restarted at pass 13 at 23:16:24. The log has carried no such line since.

This is the same fault that killed E68's `p1.attempt-1793074293` at 21:11:22 (E68 amendment A7, item 4). The
device-level guards — `scan_procs`, the `et_soc1` use count, and the card lock — were never affected by it;
only the logged-in-user check was.

*Nothing else changes.* Same cooling length, same heater, same bands, same reduction, same 06:30 PT stop.

## How to reduce this in the morning

The pass set tonight is **p13 upward** (A2: p11 and p12 were aborted and carry no `block.json`, so both
reducers drop them; p1–p3 are E44's short cycles of 25 Sep and are used only where a short cycle counts).

```bash
cd ~/claude/et-soc1-prototyping
# 1. IDLE-L and IDLE-d, the registered scoring E44 left INSUFFICIENT
python3 tools/claims-v3/idle/reduce.py --data build/claims-v3 \
        --out docs/reports/data/2026-10-27-e66-idle-long/verdicts.json
# 2. L1-L4, including the 51-67 C fixed/leakage share Q128(b) asked for
python3 tools/claims-v3/idle/e66_split.py --data build/claims-v3/aifoundry2/idle \
        --out docs/reports/data/2026-10-27-e66-idle-long/e66-split.json
# 3. this card's idle leakage slope, the number E68's correction needs
python3 tools/claims-v3/idle/idle_slope.py
```

Then write the Results section into this README, and **re-run E68 with the measured slope as a labelled
sensitivity, never as a replacement for its registered scoring**:

```bash
python3 tools/claims-v3/sm/reduce_sm.py --data build/claims-v3/aifoundry2/sm --gen build/sm-gen \
        --pred docs/reports/data/2026-10-27-e68-stage-map/predictions.json \
        --leak <the 51-58 C slope> --out <a sensitivity path, not verdicts.json>
```

**Two cycles already agree on that slope**: p11 reads 0.2960 W/°C over 51–58 °C (rms 0.116 W, 2,248 samples)
and p13 reads 0.2946 (rms 0.116, 638 samples). E68's published prices already carry both ends of the band
(amendment A7), so this re-run confirms rather than changes them.
