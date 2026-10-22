# E62 — Spatial heat movies on the ET-SoC-1: pre-registration

*AI Foundry. Written Wed 21 Oct 2026 (week 43) on the Intel (`Intel-mbp`, Darwin 26.6.2, x86_64), in
`tools/claims-v3/hm/prereg`. Experiment **E62**, request **Q121**, card **aifoundry2**,
**version 2** — every blocker and major from the red-team pass applied; what changed and why is §11. This file is
the pre-registration that freezes the predictions and the decision rules before the first card run.
🛑 **`protocol.json` is not executable on its own**: it carries the sets, the launch counts, the executed phase
orders, the safety numbers and the runner's plumbing, but **§4 and §5 of this file are mandatory for the runner**.
Nothing in this design phase touched a card, a lab box, Discord or a deployed page.*

E62 absorbs E61's deferral: `tools/claims-v3/dtf/README.md` §10 says the constant-total-power spatial dipole is
*"deferred to E62"*, and that is exactly this.

---

## 1. The question

> "design a set of spatial heating experiments. I want to generate some videos of heat spreading in various
> patterns depending on how the compute is scheduled. Come up with some interesting ideas, maybe like corners or
> the center, and create a set of videos. Turn this into a set of videos and eventually produce a [spacesheep]
> page, which has these videos. Use the live stream to make this possible." — his words, Wed 21 Oct 2026

Stated as something a card run can answer:

**Does the back of aifoundry2's circuit board show *where* on the die the compute was scheduled, at constant total
power — and does it show it well enough to be a movie?**

The sharp physical fact that shapes every block (physics.md §0): at the dwell times that give any amplitude at
all, the board's blur is 29–49 mm FWHM, **1.3–2.2× the die's own 22 mm height**. So the back of the board cannot
show the *shape* of a hot region. It can only show **where one blob is**. Every spatial movie here is therefore a
**constant-total-power swap between equal-hart patterns**, cycled, rendered as a phase-averaged difference image —
and the one pattern-vs-idle block exists only to prove the rig, build the gain map and time the heat's arrival.

Three sub-questions the blocks are built around:

1. **Can a schedule move the heat at all, and to where?** E62-ORBIT (the hero), E62-WE42, E62-SWEEP.
2. **Is the camera watching the die, or the card's voltage regulators?** E62-NS42's 90° keystone, every block's
   monopole null, E62-ORBIT's four distinct lobes, E62-W8BE8B.
3. **What does this instrument say when there is nothing to see?** E62-NULLAA (instrumental null) and
   E62-NULLGEO (geometry null). These two are the reason the other numbers are worth having, so **E62-NULLAA now
   runs sixth of ten rather than last**: the σ it measures is the σ behind every error bar on the page, and in
   version 1 it ran after every block that quotes it.

---

## 2. The die, and the sets

The die frame is `placements.py`'s inference from the MARTY map (`workloads/nocbench/analyze.py`): die row
`r = map x` with **r0 the I/O + PCIe edge**, die col `c = map y + 1`. Rows r0–r5 are the short ~22.2 mm N–S axis
at 3.70 mm pitch; columns c1–c6 are the long ~25.7 mm W–E axis at 3.73 mm pitch, with a memory strip outside c1
and outside c6. Four cells hold no compute shire.

```
          c1     c2     c3     c4     c5     c6
   r0     S0     S8     S3    M/S  IO/PCIe IO/PCIe
   r1     S24    S16    S4     S12    S20    S28
   r2     S9     S1     S13    S21    S29    S5
   r3     S25    S17    S14    S22    S30    S6
   r4     S2     S10    S18    S26    S15    S7
   r5     S11    S19    S27   M/S     S23    S31
```

**Compute corners are S0, S11 and S31 only.** The fourth corner is IO/PCIe, so a true 2 × 2 NE corner block does
not exist and `B4NE` is the registered set pushed one row in (r1r2 × c5c6).

**Every mask, shire list, `rc` pair and centroid in `protocol.json` was derived by running `placements.py`, never
transcribed.** `validate_protocol.py` re-derives the map from the same source and asserts each one; its output is
`validate.out`. This matters: the panel that fed this synthesis contained nine hand-written shire lists that
disagreed with their own masks.

In the pictures below, `--` is a master/spare cell, `==` is IO/PCIe, and `.` is a compute shire this block does
not use. Centroids are in millimetres from the die centre; **x runs along the columns (W→E), y along the rows
(N→S, positive toward r5)**. A die bearing of 0° points toward c6 and 90° toward r0.

### 2.1 E62-ORBIT — four corners and the centre (the hero)

```
          c1   c2   c3   c4   c5   c6
   r0    NW   NW    .   --   ==   ==
   r1    NW   NW    .    .   NE   NE
   r2     .    .   C    C    NE   NE
   r3     .    .   C    C     .    .
   r4    SW   SW    .    .   SE   SE
   r5    SW   SW    .   --   SE   SE
```

| set | mask | shires | per-shire | harts | switched W | centroid (x, y) mm |
|---|---|---|---|---|---|---|
| `B4NW` | `0x01010101` | 4 | 32 | 128 | 5.2 | (−7.46, −7.40) |
| `B4NE` | `0x30100020` | 4 | 32 | 128 | 5.2 | (+7.46, −3.70) |
| `B4SE` | `0x80808080` | 4 | 32 | 128 | 5.2 | (+7.46, +7.40) |
| `B4SW` | `0x00080c04` | 4 | 32 | 128 | 5.2 | (−7.46, +7.40) |
| `B4C` | `0x00606000` | 4 | 32 | 128 | 5.2 | (+0.00, +0.00) |

Travel and die bearing: NW↔SE **21.02 mm at 135.2°** (the longest travel this die offers), NE↔SW 18.60 mm at
36.6°, NW↔NE 15.37 mm at 166.1°, SE↔SW 14.92 mm at 0.0°, NW↔SW 14.80 mm at 90.0°, NE↔SE 11.10 mm at 90.0°,
C↔NW 10.51 mm at 135.2°, C↔SW 10.51 mm at 224.8°, C↔SE 10.51 mm at 315.2°, C↔NE 8.33 mm at 26.4°.

🛑 **The two diagonals are 98.6° apart, not opposed.** 135.2° − 36.6° = 98.58°, re-derived in
`validate_protocol.py` from the die map: NW−SE is (−14.92, −14.80) mm and NE−SW is (+14.92, −11.10) mm. Two
diagonals of a quadrilateral are never opposed, and because the fourth corner is IO/PCIe these four arms are a
trapezoid, so the difference is 98.6° and not 90° either. Version 1's `protocol.json` asked the hero to show them
*opposed within 15°* — a geometry correct data could only fail, with the FAIL branch reading "the regulators, not
the die". The pass rule now reads **98.6 ± 12°**, and the validator recomputes every angle any pass rule quotes.

`B4NW` and `B4SE` are derived here from the MARTY map and are **not** registered groups; `B4NE`, `B4SW` and `B4C`
are. `B4C` sits exactly on the die centre (r 2.5, c 3.5).

🛑 **Declared departure, stated now rather than discovered later.** The five arms are *not* feature-matched, and
**the centre is the worst of them**:

| arm | `(mem_side, ns_edge, by_io, by_ms)` | differs from `B4C` by |
|---|---|---|
| `B4NW` | (1, 2, 0, 0) | 1 on mem_side, 2 on ns_edge |
| `B4NE` | (2, 0, 2, 0) | 2 on mem_side, 2 on by_io |
| `B4SE` | (1, 2, 0, 1) | 1, 2, 0, 1 |
| `B4SW` | (1, 2, 0, 0) | 1 on mem_side, 2 on ns_edge |
| **`B4C`** | **(0, 0, 0, 0)** | — |

All five arms are 4 shires × per-shire 32 = **128 harts**, and on this card power follows the hart count and not
the geometry (`INT16@32` vs `PER16@32` read −0.21 W at ~14 W, inside the ±0.5 W band hp's own README registered),
so the residual is small — but it is measured, not assumed: each phase's board power is logged at 10 Hz and
required within **±0.3 W** of the others, tightened from ±0.5 W. A power asymmetry appears as a **fixed-position
monopole**, never as a lobe that moves between four places, which is precisely what the block's pass rule tests.

🛑 **And the consequence for the centre, because his ask named it.** `B4C` is the most mismatched arm of the five,
and the centre's *confirmatory* statistic — the four `B4C`-minus-corner dipoles — is only **+61 to +77 mK**,
against the session's own price for an electrical half-die asymmetry of **~34 mK** (E61's 0.44 W). That is 44–56%
of the signal. So those dipoles are **quoted with that correction and never as a clean confirmation**, and if the
measured `B4C`-versus-corner board-power spread exceeds ±0.3 W the centre result is reported as **exploratory**
alongside the ring statistic rather than as the answer.

🛑 **Second declared consequence.** Because the true NE corner is IO/PCIe, the four corners form a **trapezoid**,
not a rectangle: the ring centroid is at (0.00, +0.93) mm while `B4C` is at (0.00, 0.00). So
**centre-minus-ring-mean carries a 0.925 mm dipole underneath a large radial residual** (blur-model radial
fraction 0.924), and the camera's own post-shutter drift is radial at ~140 mK over 20 s. That statistic is
**exploratory only** (§8). The centre's confirmatory form is the four clean dipoles `B4C` against each individual
corner, which are not radial.

The feature-matched inner-quadrant rectangle (r1r2/r3r4 × c1c2/c5c6, all four arms matched on all four features,
a perfect 14.92 × 7.40 mm rectangle) is the first thing to add in a second session: it would separate a
corner/edge effect from geometry. It is not in this budget, and the orientation fit does not need it (§7.7).

### 2.2 E62-WE42 and E62-WE17 — the registered west/east halves

```
          c1   c2   c3   c4   c5   c6
   r0     .    .    .   --   ==   ==
   r1    W    W    W    E    E    E
   r2    W    W    W    E    E    E
   r3    W    W    W    E    E    E
   r4    W    W    W    E    E    E
   r5     .    .    .   --    .    .
```

| set | mask | shires | per-shire | harts | switched W | centroid (x, y) mm |
|---|---|---|---|---|---|---|
| `W12` | `0x03076616` | 12 | 32 | 384 | 15.6 | (−5.59, +0.00) |
| `E12` | `0x747090e0` | 12 | 32 | 384 | 15.6 | (+5.59, +0.00) |

W↔E **11.19 mm at 180.0°** — exactly the hub's own named control, on the W–E axis the hub wrote it for. E61 ran
the N–S axis by accident.

🛑 **A correction to the readers' notes, found by running the code.** `physics.md:582` calls W12/E12 the pair that
"matches memory-side and IO-adjacency counts by construction". **It does not.** `placements.py` asserts that
balance only for the 8-shire mirror pairs. The measured features are `W12 (mem_side 4, ns_edge 0, by_io 0,
by_ms 0)` against `E12 (4, 0, 2, 2)`: E12 holds the shires beside the IO/PCIe and master/spare cells and W12 holds
none. E61's measured 0.44 W half-die electrical asymmetry (|t| = 9.55 on the board meter, priced at ~34 mK of
regulator signal, ~7% of this block's prediction) may therefore reappear here. It is **quoted as a correction, not
ignored**, and E62-W8BE8B is the arbiter.

### 2.3 E62-NS42 — the registered north/south halves, the keystone

```
          c1   c2   c3   c4   c5   c6
   r0     .    .    .   --   ==   ==
   r1    N    N    N    N    N    N
   r2    N    N    N    N    N    N
   r3    S    S    S    S    S    S
   r4    S    S    S    S    S    S
   r5     .    .    .   --    .    .
```

| set | mask | shires | per-shire | harts | switched W | centroid (x, y) mm |
|---|---|---|---|---|---|---|
| `N12` | `0x31313232` | 12 | 32 | 384 | 15.6 | (+0.00, −3.70) |
| `S12` | `0x4646c4c4` | 12 | 32 | 384 | 15.6 | (+0.00, +3.70) |

N↔S **7.40 mm at 90.0°**. The enabling identity, asserted in `placements.py` and re-derived in
`validate_protocol.py`: **`W12 ∪ E12 = N12 ∪ S12 = CORE24 = 0x7777f6f6`**, rows r1–r4, exactly four shires in
every column. So the union of loud shires, the card's total power, the regulator dissipation, the die temperature
and the clock are **identical** between E62-WE42 and E62-NS42, and the only thing that differs is the geometry.
That is what makes the 90° test a test rather than a comparison of two differently loaded runs.

### 2.4 E62-NULLGEO — the pair that must show nothing

```
          c1   c2   c3   c4   c5   c6
   r0     .    .    .   --   ==   ==
   r1    Q    P    Q    Q    P    Q
   r2    P    P    P    P    P    P
   r3    Q    Q    Q    Q    Q    Q
   r4    P    Q    P    P    Q    P
   r5     .    .    .   --    .    .
```

| set | mask | shires | per-shire | harts | switched W | centroid (x, y) mm |
|---|---|---|---|---|---|---|
| `NULLP12` | `0x243522a6` | 12 | 32 | 384 | 15.6 | (+0.00, +0.00) |
| `NULLQ12` | `0x5342d450` | 12 | 32 | 384 | 15.6 | (+0.00, +0.00) |

Constructed, not chosen. The point reflection `(r, c) → (5 − r, 7 − c)` partitions CORE24 into exactly **12
orbits**; taking one member of each gives a set P whose complement is **P rotated 180° about the die centre**.
Verified here: Q is P's exact image under that map, P ∪ Q = CORE24, the two centroids agree to 1e-9 mm, and both
arms carry `(mem_side 4, ns_edge 0, by_io 1, by_ms 1)` — matched on all four features placements.py records. The
pair is maximally interleaved, so it *looks* like it should show something.

**Why this is the only honest null available.** A point reflection preserves every **even** moment, so P and Q
have identical radial profiles and the camera's radial post-shutter drift cancels *by symmetry*, not by argument.
Its blur-model radial fraction is **0.000**. (For contrast, a spread-versus-clustered pair at a matched centroid —
tempting, and in one of the panel designs — comes out at 0.32 × the headline with 82% of it radial: it is not a
null, it is the camera's worst systematic wearing a null's clothes.)

### 2.5 E62-SWEEP — a 4 × 2 block sliding one column at a time

Phase *k* occupies **rows r1–r4 of columns c*k* and c*k*+1**, so consecutive phases overlap by one column:

```
   phase 1: r1-r4 x c1,c2      phase 4: r1-r4 x c4,c5
   phase 2: r1-r4 x c2,c3      phase 5: r1-r4 x c5,c6
   phase 3: r1-r4 x c3,c4   (= the registered CEN8)
```

| set | mask | shires | per-shire | harts | switched W | centroid (x, y) mm |
|---|---|---|---|---|---|---|
| `SCAN1` | `0x03030606` | 8 | 32 | 256 | 10.4 | (−7.46, +0.00) |
| `SCAN2` | `0x00076412` | 8 | 32 | 256 | 10.4 | (−3.73, +0.00) |
| `CEN8` | `0x04647010` | 8 | 32 | 256 | 10.4 | (+0.00, +0.00) |
| `SCAN4` | `0x64709000` | 8 | 32 | 256 | 10.4 | (+3.73, +0.00) |
| `SCAN5` | `0x701080e0` | 8 | 32 | 256 | 10.4 | (+7.46, +0.00) |

Verified: five phases of **exactly 8 shires**, mean die row **exactly 2.500** in all five, mean column
**1.5 / 2.5 / 3.5 / 4.5 / 5.5**, four perfectly even **3.730 mm** steps, every phase an **exact one-column
translate** of the one before, pure column axis. Two structural ties belong on the page and not only here: the
five phases' union is **exactly CORE24 = W12 ∪ E12**, and **phase 3 IS the registered `CEN8`**. The sweep is the
hub's 11 mm control taken apart into five steps.

Phase 3 sits exactly on the sweep's own centroid, so its **first moment** against the five-phase mean is **exactly
zero by construction**. 🛑 **Its image is not.** The mean of five translates of a pattern is a comb-smeared
pattern, not the pattern at the centre, so phase 3 minus the five-phase mean carries a real residual: in this
design's own Gaussian blur model, **+8 to +20 mK of centre-positive, wing-negative radial term** (+8 mK at
FWHM 47.1 mm, **+12 mK at the 17.0 s model FWHM of 39.2 mm**, +20 mK at E61's measured 30 mm). That is below the
registered 27 mK floor, so **the middle frame reads blank *within noise*** — which is the honest form of version
1's "predicted exactly zero", a claim nothing could falsify and one this file contradicted two sections later by
calling the same residual "77–85% radial". The statistic that *is* exactly zero is registered instead: the
matched-filter **position** sits at the sequence centroid. And the finding rests on the **monotone, evenly spaced
advance** of the five positions — the observable that distinguishes sliding from jumping — with the blank middle
frame as corroboration.

### 2.6 E62-W8BE8B — the one mirror pair the repo certifies as feature-matched

```
          c1   c2   c3   c4   c5   c6
   r0     .    .    .   --   ==   ==
   r1     .    .    .    .    .    .
   r2    W    W    W    E    E    E
   r3    W    W    W    E    E    E
   r4    W    W     .    .   E    E
   r5     .    .    .   --    .    .
```

| set | mask | shires | per-shire | harts | switched W | centroid (x, y) mm |
|---|---|---|---|---|---|---|
| `W8B` | `0x02026606` | 8 | 32 | 256 | 10.4 | (−6.06, +1.39) |
| `E8B` | `0x606080e0` | 8 | 32 | 256 | 10.4 | (+6.06, +1.39) |

W↔E **12.12 mm at 180.0°** — slightly *larger* than W12/E12's 11.19 mm. Both arms carry
`(mem_side 3, ns_edge 0, by_io 0, by_ms 0)`; `placements.py` asserts that equality for this pair and for N8b/S8b
alone. This is the arbiter of §2.2's correction and the sharpest available test of physics.md's open question 6.

### 2.7 E62-BLOOM and the calibration ladder

`UNI32 = 0xffffffff`, all 32 compute shires, per-shire 32 = 1,024 harts, **41.6 W switched** (measured board power
p50 65.6 W, p90 84.1 W against ~24 W idle). The ladder also uses `CEN8` (256 harts), `W12` (384), `INT16`
`0x6477f412` (512) and the three legs of the hart-matched triple: `B4C` at per-shire 32, `W8B` at per-shire 16 and
`INT16` at per-shire 8 — **128 harts each, across 4, 8 and 16 shires**.

`IDLE` is `0x00000000` with 0 harts and means *no launch; the card idles* — the heater rejects a zero mask
(`main.cpp:1010`), so the runner starts no process for an IDLE phase.

---

## 3. The blocks, in run order

Ten blocks, **63.52 min of card time** and a **74.27 min card-held span** against DECISIONS' 75 min, in **410
heater launches**, every one under `timeout 10` and every one carrying `--stop-file`.

🛑 **A phase is a launch COUNT, not a clock target.** The runner executes exactly *n* back-to-back launches and
switches at the last one's exit. `dwell_s = n × 8.5 s` is the **nominal** dwell and is what the predictions are
priced at; **the budget below is the worst case at 8.6 s**, the top of DECISIONS §3's 8.3–8.6 s range. Version 1
instead told the runner to "switch at the first launch boundary at or after the planned phase end" — and since
E61 measured 8.31–8.49 s, *the whole measured range is below 8.5 s*, so **every phase would have gained one
entire extra launch**: +95% at an 8.5 s phase, +46% at 17.0 s, +30% at 25.5 s, +17% at 42.5 s, 76–77 min of card
time and an 84–85 min held span, over the cap by 9 min. Worse, a 0.2 s difference between two arms' launch
durations could give one arm 6 launches and the other 5 — **unequal arm dwells, which make a monopole at the swap
frequency**, the single confound this whole design exists to avoid. A fixed count makes that impossible.

`cycles` is the **total** number of laps the runner executes; the first `warmup_cycles` laps are discarded, so
analysed laps = `cycles − warmup_cycles`.

| # | block | kind | phases | dwell (launches) | lap | cycles (analysed) | min | cum | switched W | steady die |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **E62-CAL** | calibration | 7 power rungs, 30 s idle, 8 arm rungs | 8.5 s (1) | 159.0 s | 1 (1) | 2.65 | 5.7 | 5.2–41.6 | 59.4 °C |
| 2 | **E62-ORBIT** | sequence | NW → NE → SE → SW → C | 25.5 s (3) | 129.0 s | 6 (5) | 12.90 | 19.1 | 5.2 | 54.5 °C |
| 3 | **E62-BLOOM** | bloom | UNI32 on, idle off | 42.5 (5) / 85 s | 128.0 s | 3 (3) | 6.40 | 26.7 | 41.6 (33% duty) | 60.4 °C |
| 4 | **E62-WE42** | swap | W12 ↔ E12 | 42.5 s (5) | 86.0 s | 5 (4) | 7.17 | 35.1 | 15.6 | 61.6 °C |
| 5 | **E62-NS42** | swap | N12 ↔ S12 | 42.5 s (5) | 86.0 s | 5 (4) | 7.17 | 42.8 | 15.6 | 61.6 °C |
| 6 | **E62-NULLAA** | control | W12 ↔ W12 (labelled A/B) | 42.5 s (5) | 86.0 s | 5 (4) | 7.17 | 50.5 | 15.6 | 61.6 °C |
| 7 | **E62-NULLGEO** | control | NULLP12 ↔ NULLQ12 | 42.5 s (5) | 86.0 s | 3 (2) | 4.30 | 55.3 | 15.6 | 61.6 °C |
| 8 | **E62-W8BE8B** | swap | W8B ↔ E8B | 42.5 s (5) | 86.0 s | 3 (2) | 4.30 | 60.1 | 10.4 | 58.1 °C |
| 9 | **E62-SWEEP** | sequence | SCAN1 → 2 → CEN8 → 4 → 5 | 17.0 s (2) | 86.0 s | 6 (5) | 8.60 | 69.2 | 10.4 | 58.1 °C |
| 10 | **E62-WE17** | swap | W12 ↔ E12 | 17.0 s (2) | 34.4 s | 5 (4) | 2.87 | 73.3 | 15.6 | 61.6 °C |

**The run order is the priority order, because the session ends the moment another user appears.** Each block is
independently analysable and, because the sign orders are balanced in quartets, an abort loses whole balanced
subsets rather than the block. **Three blocks moved** against version 1, and all three moves are the same
principle — *everything that underwrites another number runs before it*:

- **E62-NULLAA from tenth to sixth.** Its per-lap scatter is the σ behind every error bar and every SNR on the
  page, and in version 1 it ran after every block that quotes it; the storyboard's "publishable core" arrived at
  minute 44.7 with the σ behind every number on it still unmeasured. It also rises to **cycles 5** (four analysed
  laps, the quadratically balanced 8-phase order, a 27.0 mK bound instead of 38.2).
- **E62-W8BE8B from ninth to eighth**, ahead of the two blocks that only add to the story: it is the arbiter of
  the headline (§2.2).
- **E62-SWEEP and E62-WE17 to the tail**, because the sweep's one-column step is a 2.7σ result at the honest
  floor (§6.1) and E62-WE17 replicates masks already filmed.

The cumulative column says exactly what exists at every point:

- **after 19.1 min** — the power calibration and the hero movie. A page already exists.
- **after 26.7 min** — the establishing shot and the per-pixel gain map, which must come from *this* session
  because the camera may be moved before the next one.
- **after 42.8 min** — the registered 11 mm control and its 90° orientation partner.
- **after 50.5 min — the publishable core**: calibration, hero, bloom, control, keystone **and the measured σ**.
- **after 60.1 min** — the geometry null and the feature-matched arbiter: everything load-bearing is in.
- the last two blocks buy the wave movie with its ruler, and the transfer point.

**Slack: 0.73 min at an 8.6 s launch, 1.42 min at 8.5 s, 2.78 min at 8.3 s.** Version 1 had 7.51 min and it is
spent — on the worst-case launch budget, the 180 s pre-session idle, the cool-down allowance, E62-NULLAA's four
analysed laps and E62-BLOOM's thermal margin. The queue, in order, runs only if the realised launch comes in
short or a block ends early: (1) **E62-NULLGEO to cycles 5** (+2.87 min — four analysed laps and a 27.0 mK bound);
(2) `B4NW ↔ B4SE` at 42.5 s, 3 cycles (+4.30 min — 21.02 mm, the longest travel this die offers, predicted
≈ +290 mK, the strongest single spatial statement available); (3) E62-BLOOM to cycles 4 with a 127.5 s off-phase
(+4.97 min); (4) two more analysed laps on E62-ORBIT (+4.30 min); (5) the feature-matched inner-quadrant
rectangle of §2.1 (+7.17 min).

### Why the dwells are what they are

A dwell is built from back-to-back heater launches of about 8.3–8.6 s each (`--seconds 8 --budget 9.5` under
`timeout 10`; E61 measured 8.31–8.49 s with 8 ms gaps). **Every dwell here is a whole number of 8.5 s launches:**
8.5 / 17.0 / 25.5 / 42.5 s. The 42.5 s headline is five launches, which is **E61's own realised dwell per side**
— 5 × 8.34 s = 41.7 s, *not* the ~53 s its plan registered (`launch.md:278`). That turns every amplitude
prediction into a pure ratio to a measured anchor.

**The dwells are split by purpose, and the reason is the frame.** The difference image's two extrema sit about
2σ of the blur apart whatever the displacement, so the dwell sets how much of the picture fits. 🛑 **Two rows per
dwell, because the model and E61's own measurement disagree and the disagreement decides which blocks are
geometry-legible.** `physics.md:361` records that E61's measured 162 px profile separation implies
**FWHM 30–35 mm** — "i.e. the 10–20 s rows, not the 53 s row… Unresolved". The hub model says 47.1 mm at 42.5 s.
Columns are at the **nominal, planning-only** 0.156 mm/px of the planned 60 mm lens distance; no pixel or
millimetre figure here is published or read by a decision rule (§7.7).

| dwell | model FWHM | lobes apart | E61-measured FWHM | lobes apart | long axis (39.9 mm) | short axis (29.9 mm) |
|---|---|---|---|---|---|---|
| 8.5 s | 26.4 mm | 22.4 mm | — | — | fits | fits |
| 17.0 s | 39.2 mm | 33.3 mm | ~27 mm *(scaled)* | ~23 mm | fits | model clips, scaled fits |
| 25.5 s | 44.3 mm | 37.6 mm | ~31 mm *(scaled)* | ~26 mm | fits | model clips, scaled fits |
| 42.5 s | 47.1 mm | 39.9 mm | **30–35 mm** *(measured)* | **25–30 mm** | model fills | model clips, measured fits |

E61 measured at **one** dwell — its own realised 41.7 s — so only that row's measured figure is a measurement;
the two above it are that row scaled by the model's own dwell law (×0.69), marked *(scaled)* and never quoted as
data. The lobe separation is 0.848 × FWHM in every row, which is the 2σ relation the model gives.

**The dwell split assumes the model row**, and that is why 42.5 s is designated amplitude-only and 17.0–25.5 s
geometry. 🛑 **Registered now: E62-WE42's own difference image measures the FWHM, and the measured value — not the
assumed one — decides which blocks are admitted to the geometry fit.** If the board turns out to blur at 30 mm,
the 42.5 s blocks earn their geometry too instead of discarding it, and the split is retired as an amendment.

**The clipping rule is quantitative** (version 1's "any block whose lobes touch a frame edge is excluded from the
geometry fit" excluded, read literally, *all three inputs to the geometry fit*: the 17.0, 25.5 and 42.5 s blocks):

> A block is excluded from the geometry fit only if **more than 15% of the matched-filter template's energy falls
> outside the frame**, computed from the **measured** die footprint (E62-CAL's UNI32 monopole image) and the
> **measured** blur FWHM — never from the assumed lens distance or the modelled FWHM. The exclusion applies to
> **centroid estimators only**: the matched-filter peak and the registration translation are kept, with a
> clipping-aware template, because those are the estimators clipping does not bias.

The clipped-pixel fraction is recorded per block, and the geometric estimators chosen (§7.6) are the robust ones:
a direction, a matched-filter peak, and a registration translation — never a centroid of a clipped image and
never a lobe separation.

---

## 4. Timing, launching and the session

| | |
|---|---|
| Card | **aifoundry2 only**, as it is: no clock, voltage, TDP, firmware or driver change |
| Heater | `build/sparsity_t2/host/sparsity_host --test fma --type fp32 --pattern none --values randn --shires <MASK> --per-shire <N> --seconds 8 --budget 9.5 --seed 1 --kernel <abs path to build/sparsity_t2/kernel/sparsity.elf> --stop-file <STOP>` under `timeout 10 … < /dev/null` |
| Why `--budget 9.5` | `--budget` defaults to **8.0 s** counted from device open, so a bare `--seconds 8` is silently truncated and only stderr says so (`main.cpp:1007`). 9.5 s is inside `timeout 10`. |
| Why `sparsity_t2` | `lib.sh:35-43` selects it on this card and only on this card; `--kernel` is spelled out so a relocated binary can never load a different ELF |
| Card lock | `exec 9<>/run/lock/etsoc-shire0.lock; flock -n 9 \|\| exit 3` — **non-blocking**, held for the **card session** and **released before reduction**, never a wait loop. `wait_free()` exists and must not be used. |
| Between every pair of launches | the framework's own other-user checks: another logged-in user, any other user's device process by `ps comm`, and `lsmod` `et_soc1` use count against the baseline. Any hit → stop, **exit 3**, do not wait. |
| Telemetry | **one** `ettelem sample --every-ms 100 --reset-ms 1000` for the whole session, started with fds 8 and 9 closed, six start attempts (about one start in three fails right after a previous instance), stopped with **SIGTERM only**. Nothing else may open the management node while it runs: the die reading comes from the sampler's file. |
| Per launch | one line in `launches.jsonl`: `run`, `pattern`, `mask`, `per_shire`, `seconds`, `t_start_ms`, `t_end_ms`, `rc`, taken from `date +%s%3N` immediately around the `timeout 10` call |
| Camera | the phone's lossless `/stream.raw.z` (25 fps, 256 × 192, uint16 in 1/64 K), recorded **on aifoundry2** — the Intel cannot reach the phone's subnet. Preset stays `visualize` and auto-FFC stays on (DECISIONS §1), so the public live page is unchanged. |
| Raw frames | to a **non-synced** path on the box (`~/drive.unsynced/e62/<block>/`), never the Dropbox work tree; deleted after reduction, as E61 did with its 550 MB. Only reduced arrays, posters and mp4s reach the work tree. |
| 🛑 Before recording | **close the browser viewer tab.** `/` polls `/frame.raw` in a loop and holds `activeClients` above zero, which makes a sensitivity run abort or wait forever on its `allow_clients` gate. |
| Session shape | **180 s** idle before the first block, **30 s** between blocks, **60 s** idle after the last |
| 🛑 Why 180 s, and it is a **gate** | `camera.md` records that in the only capture on this rig "`ffcCountdown` read 0 for all 375 frames while the header said `auto_ffc=1`" and **no FFC fired**, concluding that "15 s was not enough to see a single FFC" and that "a longer capture (≥ 3 min) would show the FFC steps directly and settle it". **The FFC detection path has never been exercised on this camera**, and §7.2's two-way detection, bridging and drop window are applied to every one of the ten blocks. So: 180 s, camera.md's own figure, and **the run proceeds only if at least one FFC is detected by both routes (a P3FZ `seq` gap and a frame-mean step) and the two agree**; if none fires in 180 s, the FFC rhythm is recorded **on the page** as uncharacterised. This idle also carries tonight's drift, the zero-signal reference frame rendered at every movie's colour scale, and the baseline E62-CAL's session gate reads against. The post-idle is 60 s because the pre-idle now carries the reference frame. |
| Cool-down gate | **registered with a threshold and a budget**, not "holds bounded". It applies **only where the next block's dwell-weighted switched power exceeds the previous block's** — so three boundaries in this order (before E62-BLOOM, E62-WE42 and E62-WE17), and never between WE42 / NS42 / NULLAA / NULLGEO, which all sit at the same 61.6 °C steady state where cooling buys nothing. The 30 s gap **extends to at most 75 s** while the die, read from the sampler's own file, is above **59 °C**; then it proceeds and logs. Never an unbounded wait. **The whole allowance is counted in the card-held span**, and the die model says none of the three will actually hold: 54.5 °C after E62-ORBIT, ~56 °C after E62-BLOOM (whose lap *ends* in its 85 s idle), 58.1 °C after E62-SWEEP. Version 1's unbudgeted 5 × 180 s was 15.0 min against 7.51 min of slack. |
| Budget — **three caps, not one** | **card time ≤ 75 min** (63.52), **card-held ≤ 75 min** (74.27, including the idles and the cool-down allowance), **card session wall ≤ 100 min** (91.27: held + ~12 min setup + ~5 min for E62-CAL's go/no-go and any per-shire amendment). All gated at the **worst-case 8.6 s launch**. |
| 🛑 Reduction is **outside** the wall and outside the lock | The card lock and the `ettelem` sampler are **released**, and the Discord message edited to "released", **before reduction starts**. Reduction is roughly 4 GB of frames (~100k frames at 25 fps) through decompression, 1 s binning, per-lap per-pixel detrending, permutation nulls for ten blocks and five `ffmpeg` renders — comfortably half an hour. aifoundry2 is the box earmarked for Roman's firmware/overclocking work, so holding its card through that is a courtesy problem as well as a scheduling one. Version 1 registered "≤ 2 h wall **including** setup and reduction" with the lock "held for the whole session", which was at or over 120 min before anything went wrong. |
| Claim | one `#community-lab` message naming **aifoundry2** and the window, closed by **editing that same message** to add "released" and the artifact link. 🛑 **The message and the edit each open with a plain `<ai>` on the first line** — plain text on Discord, not the escaped GitHub form — and the post is **read back after sending**. A Discord post is chat, so the standing rule applies and a hook will block an untagged one. |
| 🛑 Never | reboot aifoundry2 or restart its networking — it is the dashboard collector **and the camera phone's only route to the internet**. Never reset the card, retrain its PCIe link, `kill -9` a sampler, change any camera setting, or average laps taken at different `--per-shire`. The full list is `protocol.json`'s `runner.forbidden`. |

---

## 5. Safety

| | registered value | why |
|---|---|---|
| `abs_stop_c` | **85 °C** die | the lab's 90 °C rule stands; 85 is this experiment's own stop, on **one** sample, sticky |
| `board_cap_w` | **95 W** | **deliberate, and it matters**: hp's default `cap_board_w` is **73 W** on 2 consecutive samples (`hplib.py:119`), and E62-CAL's full-card rung draws 65.6 W p50 / 84.1 W p90. A runner reusing hp's caps unchanged would be stopped by `CAP_W` at its own go/no-go gate. |
| `governor_c` | **65 °C** | aifoundry2's governor steps 800 → 700 → 600 MHz above this, and it moved inside 1.5 s of load in the dvfs2 log. Every block is designed to sit below it. |
| `max_steady_c` | **63 °C** | DECISIONS §2. The hottest block steadies at **61.6 °C**, 3.4 °C under the governor. |
| Stop plumbing | `--stop-file` on every launch | every launch carries `--stop-file`; the loop checks it between launches, so worst-case latency to stop is one launch (~0.5 s). A small reader of the sampler's output touches `STOP` on `temp_c.minshire[0] ≥ 85` or `board_w ≥ 95`. |
| Clock fallback | a flagged block **ends**, it is not rescaled | `mhz.minion` every 100 ms; any lap containing a sub-800 MHz sample is flagged. If two laps in a block are flagged the block **ends at the next lap boundary**, its realised lap count is recorded, and if budget remains it **restarts as a separate block id** at `--per-shire 28` (14.0 W → 60.5 °C) with its own full cycle count and its own sign order. 🛑 **Laps taken at different `--per-shire` are never averaged together**, and each amplitude is re-anchored per measured watt. Version 1 dropped `--per-shire` to 28 mid-block at the next lap boundary: harts stayed equal so the monopole stayed null, but the amplitude changed by 28/32 = 0.875 **part-way through a balanced 8-phase quartet**, so averaging with the registered signs mixed two measurements and splitting left two 2-lap halves on the weak 4-phase order. |
| 🛑 Power fallback, decided now — **three branches** | | DECISIONS fixes ≈1.3 W per shire, but the full-card heater reads **p50 65.6 W and p90 84.1 W** against a 23–25 W idle — 1.3 to 1.9 W per shire. E62-CAL measures it in the first 2.7 min, before any movie block. Each branch is a timestamped amendment recorded before any reduction, and **harts stay equal within every swap in all three**. |
| &nbsp;&nbsp;(1) **high, 384-hart arms** | `--per-shire 24` above 16.0 W | At 1.9 W/shire a 384-hart arm would draw 22.8 W and reach **66.5 °C**, over the governor. If E62-CAL's telemetry puts a 384-hart arm above **16.0 W** switched, every 384-hart block (WE42, NS42, NULLAA, NULLGEO, WE17) runs at `--per-shire 24` for **both** arms (288 harts, amplitudes × 0.75) and every amplitude is re-anchored per measured watt. |
| &nbsp;&nbsp;(2) **high, the full card** | `--per-shire 24` **and a 127.5 s off-phase** above 45 W | 🛑 **Version 1 had no branch for the 1,024-hart block at all** — its fallback covered 384-hart arms and said "the 256-hart blocks are unchanged", leaving E62-BLOOM, the only block that duty-cycles the whole card, in no branch. If the `UNI32` rung reads above **45 W** switched, E62-BLOOM runs at `--per-shire 24` (768 harts) **and** its off-phase lengthens from 85.0 s to 127.5 s. The duty-cycle model puts the on-phase peaks at **61.0 / 62.0 / 62.3 °C** there, against **63.7 / 64.0 / 64.0 °C** unchanged — i.e. unchanged it would be truncated by the per-cycle gate on two of three cycles. The gain map's SNR > 50 criterion still holds comfortably at 768 harts. The extra 2.1 min is paid by dropping E62-WE17, last in the order. |
| &nbsp;&nbsp;(3) **low** | drop E62-SWEEP below 12.0 W | `physics.md` measured 0.90 W/shire for E61's *enercat* arm against DECISIONS' 1.3 for this heater. If a 384-hart arm reads **below 12.0 W** switched, every amplitude falls ~25% and E62-SWEEP's one-column step drops under the measured floor: E62-SWEEP is dropped and its 8.6 min go to E62-NULLGEO (to cycles 5) and to the `B4NW ↔ B4SE` diagonal. A decision, not a disappointment. |
| Transient phases | ≤ 60 s each | two phases would steady above 63 °C if they ran forever — E62-CAL's 8.5 s `UNI32` rung and E62-BLOOM's 42.5 s on-phase (both 41.6 W, 79.3 °C steady). Both are inside DECISIONS' "the all-32 bloom is on for ≤ 60 s at a time" (measured 53 → 62 °C in 60 s), and `validate_protocol.py` asserts exactly that. |
| 🛑 `bloom_cycle_stop_c` | **64 °C**, per on-phase | A dwell-weighted mean cannot see a per-cycle peak, and E62-BLOOM is the only block that duty-cycles the full card. The runner reads the die before and during **every** on-phase and ends it early by touching the stop file at 64 °C, logging the truncated dwell. **64 °C, not 63**: `max_steady_c` 63 governs *steady* states and DECISIONS exempts the bloom explicitly ("≤ 60 s at a time"), the duty-cycle model puts the three on-phase peaks at **60.3 / 62.1 / 62.8 °C**, and a gate that fires on the design's own predicted outcome is a mis-set gate. 64 °C still leaves 1.0 °C under the governor's 65 °C step, which is the thing being protected: a step from 800 to 700 MHz inside an on-phase would silently change the power during **the one block that builds the per-pixel gain map applied to every other difference image**, and would void both the +2,500–4,000 mK prediction and the 4–14 s arrival measurement. |

Die temperature per block is `51 °C + 0.68 °C/W × (dwell-weighted mean switched watts)`, from aifoundry2's own
measured cooling line (51 °C at 23.2 W idle, 0.68 °C/W after the 9 Oct two-fan bracket). 🛑 **The validator no
longer gates only that mean.** It now **simulates the die phase by phase through the whole session** — every
launch, every idle, every gap — with a single time constant **τ = 143.2 s** fitted on DECISIONS' own measurement
(53 → 62 °C in 60 s at 41.6 W switched), and asserts that the simulated peak stays under the governor and that
every E62-BLOOM on-phase peak stays under the 64 °C gate. The simulated session peaks at **62.8 °C**, in
E62-BLOOM's third on-phase, 2.2 °C under the governor. It still separately checks every phase's transient against
the 60 s rule.

---

## 6. Predictions, frozen before the first card run

### 6.1 How every number was priced

Nothing is predicted in absolute millikelvin. Every amplitude is

> **A = 372.9 mK × (centroid travel / 10.012 mm) × (switched W / 14.40 W) × (transfer(dwell) / transfer(41.7 s))**

anchored on **E61's measured +372.9 ± 13.6 mK** (half-patch double difference, permutation p = 0.0007, monopole
−13.2 mK at p = 0.96) for a 10.012 mm N↔S swap at 14.40 W and a realised 41.7 s dwell. Centroid travel comes from
`placements.py`; switched power from DECISIONS' 1.3 W per shire at per-shire 32; the dwell factor from the hub's
transfer table read dwell-indexed and log-log interpolated:

| dwell | 8.5 s | 17.0 s | 25.5 s | 42.5 s | anchor 41.7 s |
|---|---|---|---|---|---|
| mK per W | 19.6 | 50.1 | 83.9 | 158.5 | 154.8 |
| relative to the anchor | 0.126 | 0.324 | 0.542 | **1.024** | 1.000 |

**This removes three uncertainties from every prediction at once**: the model's 1.5–2.3× optimism against E61, the
hub table's absolute scale, and its period-versus-dwell octave (a locally power-law table gives nearly the same
*dwell-to-dwell ratio* under either reading — dwell-indexed and period-indexed differ by under 10% across the
whole ladder here, far inside the per-lap scatter). **No number in this protocol depends on settling that octave**,
and E62 does not claim to settle it: it is a desk job, rerunning the model behind `thermal-camera-hub.md:338`.

**σ per analysed lap is pre-registered as `max(27 mK, 7% of the amplitude)`** — 🛑 **27 mK, not version 1's
15 mK.** The floor is E61's **own measured between-pass scatter**, 27 mK on 373 mK, used **additively**, and
version 1's 15 mK patch sat *below the very measurement it was derived from*. The multiplicative form alone is
worse still: 7% would give a 33 mK signal a 2.3 mK error, which is impossible when the stated limit is
5–8 mK/s of field drift. E61's **13.6 mK single-pass standard error** is quoted as the *optimistic bound*, never
as the expectation.

It is **not** a per-pixel photon-noise figure: at 25 fps with 1 s bins and a 4 × 4 bin the photon noise is ~2 mK
per displayed pixel, 100× below every signal here, and physics.md measured a hard spatially-correlated floor near
4 mK per frame that does not improve past about 8 × 8. **The limit is 5–8 mK/s of field drift, not photons.**

**What the correction costs, stated rather than discovered:** E62-SWEEP's one-column step falls from 4.8σ to
**2.7σ** over five laps (2.2 → **1.2 per lap**); the orbit's C-minus-corner dipoles — the *confirmatory* answer to
"corners or the centre?" — fall from 9.1 to **5.0–6.3** over five laps; both nulls' 2σ bounds widen from 21 mK to
**27.0 mK** (four analysed laps) and **38.2 mK** (two), so "under 5% of E62-WE42's prediction" becomes **5.8%**
and **8.3%**; and the storyboard's "10× margin in a single lap" KPI tile becomes **5.7× in a single lap, 12.7×
over five**. Nothing in the design changes because of this — but every number on the page does, and it is better
to find that here than in a reader's comment.

**E62-NULLAA measures the real σ and replaces this prior on the page — and it now runs sixth, before every block
whose published error bars and whose detectability depend on it.** It is reduced **twice**: over all four analysed
laps on the 8-phase order (the clean σ), and over its **first two analysed laps on the 4-phase order** — the exact
configuration of E62-NULLGEO and E62-W8BE8B — so the residual quadratic drift leak those two-lap blocks carry is
bounded by a *matched* null instead of argued away. That second reduction is free: it is an analysis choice, not
card time.

### 6.2 The registered numbers

Every σ column below is at the **registered 27 mK floor**, `max(27 mK, 7% × A)`. The analysed-lap count is in the
`laps` column, and `over all laps` is `A / (floor / √laps)`.

| block | statistic | predicted | × E61 | travel | laps | σ floor | σ per lap | over all laps | basis |
|---|---|---|---|---|---|---|---|---|---|
| **E62-WE42** | half-patch, W12 − E12 | **+462 mK** | 1.24 | 11.190 mm | 4 | 32.4 | **14.3** | 28.6 | the formula above at 15.6 W and 1.024 |
| **E62-NS42** | half-patch, N12 − S12 | **+306 mK** | 0.82 | 7.400 mm | 4 | 27.0 | 11.3 | 22.6 | same; **ratio to WE42 = 0.661 × r**, with the anisotropy `r` measured by E62-ORBIT — see below |
| **E62-WE17** | half-patch, same masks | **+146 mK** | 0.39 | 11.190 mm | 4 | 27.0 | 5.4 | 10.8 | **ratio to WE42 = 0.316**, local log-log transfer slope **1.257** |
| **E62-W8BE8B** | half-patch, W8B − E8B | **+334 mK** | 0.90 | 12.123 mm | 2 | 27.0 | 12.4 | 17.5 | **ratio to WE42 = 0.722**; reduced form **2.65 mK per W per mm**, identical to WE42's by construction — so the *measured* agreement is the test |
| **E62-ORBIT** | NW − SE | **+153 mK** | 0.41 | 21.015 mm | 5 | 27.0 | 5.7 | 12.7 | 5.2 W, 25.5 s; the longest travel on this die |
| | NE − SW | +136 mK | 0.36 | 18.596 mm | 5 | 27.0 | 5.0 | 11.2 | predicted at **36.6° ± 10°** from the measured W→E direction with **no free parameter** once WE42 and NS42 are in |
| | NW − NE | +112 mK | 0.30 | 15.372 mm | 5 | 27.0 | 4.2 | 9.3 | the W–E baseline for the anisotropy `r` |
| | SE − SW | +109 mK | 0.29 | 14.920 mm | 5 | 27.0 | 4.0 | 9.0 | |
| | NW − SW | +108 mK | 0.29 | 14.800 mm | 5 | 27.0 | 4.0 | 8.9 | the N–S baseline for the anisotropy `r` |
| | NE − SE | +81 mK | 0.22 | 11.100 mm | 5 | 27.0 | 3.0 | 6.7 | |
| | **C − NW / SE / SW** | **+77 mK** | 0.21 | 10.508 mm | 5 | 27.0 | 2.8 | 6.3 | **the centre's confirmatory form** — a dipole, not a ring. 🛑 Against a **~34 mK** electrical correction (§2.1): quoted with it, never as a clean confirmation |
| | C − NE | +61 mK | 0.16 | 8.327 mm | 5 | 27.0 | 2.2 | 5.0 | same correction |
| **E62-SWEEP** | one column step | **+32.5 mK** | 0.09 | 3.730 mm | 5 | 27.0 | **1.2** | **2.7** | 🛑 averaged only, and registered as a 2.7σ result — not a per-lap one |
| | phase 1 − phase 3 | +65 mK | 0.17 | 7.460 mm | 5 | 27.0 | 2.4 | 5.4 | |
| | phase 1 − phase 5 | **+130 mK** | 0.35 | 14.920 mm | 5 | 27.0 | 4.8 | 10.8 | visible per lap; must equal the sum of the four steps |
| | **phase 3 − five-phase mean** | **first moment exactly 0; image +8 to +20 mK** | 0.00 | 0.000 mm | 5 | 27.0 | — | — | §2.5: a centre-positive, wing-negative radial residual **below the floor**, so blank *within noise*. The zero that is exact is the matched-filter **position** |
| **E62-NULLGEO** | half-patch, P − Q | **0 mK** | 0.00 | 0.000 mm | 2 | 27.0 | — | 2σ bound **38.2 mK** (8.3% of WE42) | modelled residual from the arms' higher odd moments only: **0.0077 × WE42 = 3.5 mK**, far below the floor. Radial fraction 0.000 |
| **E62-NULLAA** | half-patch, A − B | **0 mK** | 0.00 | — | 4 | 27.0 | — | 2σ bound **27.0 mK** (5.8% of WE42) | zero by construction: the same mask in both arms, so the drive never changes. Both bounds are now `2 × 27 / √laps` from the same floor — version 1 gave these two identical configurations 21 and 25 mK |
| **E62-BLOOM** | frame mean, on − off | **+2,500 to +4,000 mK** zero-to-peak | — | monopole | 3 | — | — | — | physics.md's ALL32 row (2,651 mK at 40 s and 28.8 W, already × K = 0.674) carried to 41.6 W, lower end divided by the 572/373 gap between E61's undetrended and detrended arms |
| **E62-CAL** | board W vs harts | linear at **40.6 mW/hart** | — | — | 1 | — | — | — | 5.2 / 10.4 / 15.6 / 20.8 / 41.6 W above a 23–25 W idle; the three 128-hart legs within **±0.5 W** of each other, each statistic the **median of the 10 Hz samples in the last 4.0 s of a launch** |

🛑 **E62-NS42's amplitude ratio is conditional, and only its orthogonality is confirmatory.** The 0.661 =
7.400 / 11.190 mm identity is "pure geometry" **only if the board blurs the die's short axis as widely as its
long one**: the half-patch amplitude scales as `travel / σ_axis`, so an anisotropy `r` moves the predicted ratio
to **0.661 × r**. Nothing in the readers' notes measures `r` — physics.md's FWHM figures are all dwell-indexed and
isotropic — and a rectangular PCB with a heatsink bracket and edge connectors down one side is not obviously
isotropic. A ±12% pass band on an unmeasured quantity was the tightest unhedged criterion in version 1, gating the
block this design calls the keystone. **E62-ORBIT measures `r` for free and runs first**: the lobe widths along
its NW↔NE baseline (15.372 mm, the W–E family) and its NW↔SW baseline (14.800 mm, the N–S family) give it
directly. So the keystone is **90° ± 10°**, which is robust, and the ratio is **0.661 × r ± 0.08**, with 0.661
quoted only as the isotropic special case.

🛑 **E62-CAL's board-power statistic is a steady-window median, not a launch mean.** The ascending-then-descending
octet gives each of W12 / E12 / N12 / S12 one 8.5 s launch per appearance, and a single launch includes device
open, kernel load and the power ramp — which biases the mean and inflates the scatter on exactly the comparison
that prices the regulator confound for the headline. Registered: the **median of the 10 Hz board samples in the
last 4.0 s of each launch**, with the **within-arm scatter reported beside the between-arm difference**, so the
±0.5 W test has a stated power.

### 6.3 Arrival lag — the one calibration-free observable

Modelled as **431·√f degrees** (`notes-physics.md:87-89`), with the independent empirical analogue of 9.15 s into
aluminium and 13.59 s into ABS on the M5:

| drive | period | f | lag | in seconds |
|---|---|---|---|---|
| E62-ORBIT lap, E62-BLOOM cycle | 127.5 s | 0.00784 Hz | 38.2° | **13.5 s** |
| E62-WE42 / NS42 / NULLAA / NULLGEO / W8BE8B, E62-SWEEP lap | 85.0 s | 0.01176 Hz | 46.7° | **11.0 s** |
| E62-WE17 | 34.0 s | 0.02941 Hz | 73.9° | **7.0 s** |

Plus E62-BLOOM's direct step response, **4–14 s**. So the fit has **four points: three lock-in drive periods
(127.5 / 85.0 / 34.0 s) plus the bloom's step response**, and the three periods span **1.94× in √f** — √f runs
0.0886 → 0.1715 — not the "1.5×" version 1 wrote in two places. The lever arm is better than it was advertised,
but a frozen pre-registration should not misstate its own.
🛑 **Every lag is reported as an UPPER BOUND**, because the `visualize` preset's `TNR = 50` temporal filter smears
time and DECISIONS fixes the preset so the public live page stays as it is.

---

## 7. Analysis plan

Written before any data exists. Every step runs on the reduced cube; nothing is chosen after seeing a result.

**7.1 Raw counts, never CSV.** Work on `/stream.raw.z`'s uint16 plane × (1000/64) → millikelvin: linear,
offset-free under differencing. `/frame.csv` is never used for mK work — it bakes in an emissivity correction
(solved from the data as **ε = 0.960, reflected 25.0 °C**) that is non-linear in the raw count, and its quantiser
is 64.7 mK against the raw path's 62.5 mK. The `visualize` preset's real hardware step is **62.5 mK**, verified by
`raw % 4 == 0`; it dithers away under averaging (16 × 16 binning measured 5.0 mK including it).

**7.2 FFC bridging — the window comes from the camera's own measurement, not from a round number.** Auto-FFC
stays **on** (DECISIONS §1) and fires on a 0.25 °C focal-plane move, so it is *correlated with the load*. Detect
each event two ways — a gap in the P3FZ header's `seq`, and a step in the whole-frame mean. Then:

- **Drop 2 s before and at least 16 s after** every event — or until the frame-mean slope returns to within
  1 mK/s of the pre-event baseline, whichever is longer.
- **Estimate the bridging offset per pixel from windows *outside* that settle**: the 4 s before the event and the
  4 s after the drop ends.
- **Report the dropped fraction per block *and per arm*,** and publish the **per-block FFC-phase histogram** as a
  diagnostic: a load-correlated FFC distribution is itself a result.
- **If a block's dropped fraction exceeds 30%, that block's amplitude is reported as a bound, not a value.**

🛑 **Why, since version 1 said ±2 s.** The camera's own measured post-shutter drift is "median 23 mK at 5 s,
34 mK at 10 s, **~140 mK from 20 s on**; 95th pct ~400 mK — the corners warm against the centre, **~16 s
settling**" (`physics.md:473`). A ±2 s window is **8× shorter than that settle**, so ~14 s of a 140–400 mK
**radial** transient survived inside every arm — a third of a 42.5 s arm — and the per-pixel offset used to bridge
the step was fitted on the steepest 2 s of it. 140 mK is larger than every signal in this session except
E62-WE42 and E62-BLOOM, the surviving signature is radial, and because auto-FFC is load-correlated these
transients do **not** distribute randomly across arms — which is exactly what E62-ORBIT's centre statistic and
E62-SWEEP's phase 3 are most exposed to.

The **180 s** pre-session idle measures tonight's FFC rhythm before anything runs and gates the session on
detecting one (§4), and the balanced sign orders mean an FFC landing in one phase does not align with the arm
labels.

**7.3 Drift removal, in three layers, in this order.** (a) **Cold-anchor common-mode subtraction** from the
coldest quarter of pixels, per 1 s bin — the single most important step: on the M5 run, without it, 1 s boxcar
averaging turned half the keyboard negative by −600 mK from focal-plane wander. (b) A **per-pixel linear time
trend per analysed lap**, as E61 did. It provably attenuates a real step, so it is conservative, and the balanced
orders keep the attenuation from aligning with the arm labels. (c) The **difference between arms** itself, which
cancels a spatially uniform drift exactly.

**7.4 Phase-averaged differences.** 1 s temporal bins; a 4 × 4 spatial bin (0.6 mm — free against a 29–49 mm
blur); the first **15 s of every arm dropped** (E61's `w15` arm read *higher* than `w0`, 572 vs 455 mK
undetrended, exactly as a settling lag predicts) — except at the 17.0 s dwell, where there is no 15 s to drop and
the statistic is instead the **lock-in fundamental at the drive frequency** with the lag as its phase, converted
as `window statistic = (π/4) × fundamental amplitude`. **This switch is registered now, not chosen later.** Each
lap's phase mean minus that lap's own mean, then averaged over the analysed laps with the registered sign order.

**7.5 Gain map.** From E62-BLOOM: per-pixel ΔT over the on-phase, normalised to its median inside the die
footprint. This divides out both the per-pixel emissivity — **12.4% of pixels are shiny component tops that read
up to 4.2 °C cold and under-report ΔT** — and the board's own spreading, so the pattern movies compare like with
like. Accepted only if the per-pixel rise has signal-to-noise above 50 on at least 90% of die-footprint pixels.
Applied to every difference image before any statistic. It must come from this session: the camera may be moved
before the next one.

**7.6 The statistics.** The registered primary is **E61's permutation-calibrated half-patch double difference**
(`cam_reduce.py`) — one patch minus the other of the (arm-A mean − arm-B mean) image — with σ from **permuting the
arm labels inside each lap**, never from a frame-noise figure. Per block:

- **Monopole** — the card mean of the difference image, with its permutation p. The camera's own read of
  "ΔP_card = 0". E61's was −13.2 mK, p = 0.96.
- **Orthogonal-axis** — the gradient component perpendicular to a reference direction **the block does not itself
  set**. 🛑 Version 1 asked E62-WE42 for "the component on the orthogonal image axis |·| < 40 mK with p > 0.1"
  while that same block's `direction` field says it **defines** the image direction of the W→E axis: read that
  way the orthogonal component is zero by construction and the criterion tests nothing, and read as the sensor's
  own x/y axes it fails on a perfectly good result at an unmeasured camera roll near 45°. Registered instead: the
  reference is the **die frame fitted by E62-ORBIT**, which runs earlier, and failing that **E61's measured 173.8°
  gradient** on the same axis family. The 40 mK bound attaches to that reference. For E62-NS42 and E62-SWEEP the
  reference direction was already independent (E62-WE42's measured dipole), and there the clause stands as
  written. E61's own orthogonal component was −11.7 mK, p = 0.29.
- **Direction** — the gradient direction of the difference image, in degrees on the sensor.
- **Position** — the **matched-filter peak**: cross-correlate the difference image (or a phase-minus-lap-mean
  image) against the blur-model template for that dwell and take the peak. Chosen *because* it is robust to the
  wing clipping of §3; the centroid of a clipped image is not, and is reported only as exploratory.
- **Translation** — for the sweep, the registration shift between **pairwise** difference images of the same form.
  🛑 **The widest-separated pair, not consecutive ones**: (phase1 − phase2) against (phase4 − phase5), a
  three-column **11.19 mm** shift at the same noise. These **are** exact translates of one another under
  convolution, so the shift is PSF-independent and invariant to the ~11 s thermal lag. Phase-minus-lap-mean images
  are **not** translates and are not used for this.
- **Peak-to-peak / matched filter, not half-patch**, for any phase sitting on its own sequence centroid —
  E62-SWEEP's phase 3. The half-patch form is blind there by construction. **Registered now**, before any data, or
  it would look like a statistic chosen after the fact.
- 🛑 **No displacement is ever read from a lobe separation.** `cam_reduce.py`'s own
  `dipole_centroid_separation_px` tracks the *pattern's width*, not its displacement: on synthetic frames a 9 px
  move read 41.9 px and a static control read 36.1 px.
- Each arm's **board power** at 10 Hz from the block's own telemetry, reported beside the result. E61's 0.44 W
  half-die asymmetry is priced at **~34 mK** and quoted as a correction.
- Every realised dwell is read from `launches.jsonl`'s `t_start_ms` / `t_end_ms`, **never from the plan**, and the
  predicted transfer row is recomputed from the realised dwell before any decision rule is read. This is exactly
  how E61's registered "53 s" turned out to be 41.7 s.

**7.7 How the orientation is fitted.** Three unknowns — the camera's **roll** θ, its **handedness** (flip) k, and
**millimetres per pixel** s — against five independent measurements.

The model is a 2-D similarity with reflection:

> **p_image = s · R(θ) · M^k · p_die + t**,  with M = diag(1, −1) and k ∈ {0, 1}

fitted by least squares on E62-ORBIT's **four corner matched-filter positions**: 8 observations, 4 continuous
parameters (s, θ, t_x, t_y) with k chosen as whichever of the two gives the lower residual — **4 degrees of
freedom of residual**. A trapezoid is a perfectly good target for this: the fit needs the four die positions to be
non-degenerate, not to form a rectangle.

🛑 **What makes those four positions admissible, said here because §8 item 5 calls them exploratory.** They are
**matched-filter peaks, not centroids**, and the clipping rule of §3 excludes a block from the fit only if more
than 15% of the template's energy falls outside the frame — measured, not assumed. So the fit uses them, with a
clipping-aware template, while their **absolute image coordinates** remain exploratory (§8 item 5): what is
confirmatory is that the lobe sits at four mutually distinct positions and that their separations and bearings
come out right. Version 1's rule and version 1's fit could not both stand; now they do.

Then four pre-registered redundancy checks, each a falsifier:

1. **E62-WE42's dipole direction must equal the fitted image direction of the die's W→E axis** within 15°.
2. **E62-NS42's must be 90° ± 10° from it** — the keystone. Die rows and columns are orthogonal by construction,
   and orthogonality survives a rotation, a mirror **and a modest tilt**. **Landing within 30° of each other is
   geometrically impossible for the die.** 🛑 Version 1 justified this with "a camera projection is a rotation and
   possibly a mirror", which is true only of a *fronto-parallel* camera: a 30° tilt moves two orthogonal die axes
   to about **82°** apart. That still passes 90° ± 10°, so the test stands and only the stated reason was wrong —
   and the 30° falsifier has that much more margin than advertised. E62-NS42 is also E61's own axis, so it should
   come out near E61's measured 173.8° gradient with the same sign.
3. **E62-ORBIT's NE↔SW diagonal must land at 36.6° ± 10°** from the measured W→E direction, rotated toward the
   measured north. **Zero free parameters** once checks 1 and 2 are in; the *signed* prediction is what breaks the
   handedness.
4. **E62-SWEEP's step direction must be parallel to E62-WE42's** within 10°, and its five positions collinear and
   evenly spaced (5 points, 2 parameters, 3 df).

**Millimetres per pixel — the primary route is the orbit fit, and every route's precision is written down now.**
🛑 Version 1 made the *least* precise route primary. The predicted fractional error of each, computed at the
registered 27 mK floor from `σ_PSF / SNR` with the SNR integrated over the analysed laps:

| route | shift | amplitude | SNR over laps | σ_PSF | position error | fractional |
|---|---|---|---|---|---|---|
| **E62-ORBIT four-corner fit** (primary) | 14.92 mm baselines | 153 mK | 12.7 | 18.8 mm | 1.48 mm | **9.9%** |
| **E62-SWEEP widest pair**, (p1−p2) vs (p4−p5) (cross-check) | 11.19 mm | 98 mK | 8.1 | 16.6 mm | 2.06 mm | **18.4%** |
| E62-SWEEP consecutive pair, (p1−p2) vs (p2−p3) — **not used** | 3.73 mm | 32.5 mK | 2.7 | 16.6 mm | 6.19 mm | **166%** |

So the sweep's *consecutive* registration — version 1's primary — is useless at the honest floor: a 3.73 mm true
shift measured to ±6.2 mm, and still ~96% after averaging the three independent consecutive pairs. The
widest-separated pair costs nothing extra, has the same noise and a three-times-longer lever, and the orbit fit is
tighter again because it spans four corners. **Registered rule: the scale bar appears only if the
inverse-variance combination of the two kept routes lands inside 10%** (predicted **8.7%**). 🛑 **Until that
number exists there is no millimetre scale bar and no displacement in millimetres is published.** A wrong scale
bar is worse than none — and so is one with no stated precision, which is what the storyboard promised.

**7.8 The movie rendering.** Each 1 s bin minus the lap mean, gain-corrected, 4 × 4 binned, **RdBu_r symmetric
about 0 in mK** over a grey structural scene, with sub-3σ pixels left grey (σ from the same data). 256 × 192
upscaled ×3 with NEAREST to 768 × 576, `libx264 -pix_fmt yuv420p -crf 23 -preset slow -movflags +faststart`, a
`.jpg` poster written by the same script. A die-map inset in the same corner of every movie lighting the shires
that are running; real time and the speed-up burnt into the frame.

🛑 **The repeat count per movie is registered, because a lap does not have enough bins for the loop DECISIONS
asks for.** One 1 s bin per second of lap means `orbit` has 127 bins, `sweep` 85, `we42` 85, `nullgeo` 85 and
`we17` only **34** — 3.4–4.3 s of footage at 8–10 fps against DECISIONS §7's 10–20 s loops.

| movie | lap | bins | laps repeated | fps | loop |
|---|---|---|---|---|---|
| `orbit.mp4` | 127.5 s | 127 | 1 | 10 | 12.7 s |
| `sweep.mp4` | 85.0 s | 85 | 1 | 8 | 10.6 s |
| `we42.mp4` | 85.0 s | 85 | 1 | 8 | 10.6 s |
| `nullgeo.mp4` | 85.0 s | 85 | 1 | 8 | 10.6 s |
| `bloom.mp4` | 127.5 s | 127 | 1 | 10 | 12.7 s |
| (`we17`, if it is rendered at all) | 34.0 s | 34 | **3** | 10 | 10.2 s |

**A repeated lap has its boundary burnt into the frame** — a one-frame flash of the lap counter — so a reader sees
it is a repeat of a cyclic process and not extra data. The storyboard's durations are reconciled with this table.

---

## 8. What is exploratory

The whole camera result is **exploratory** in the lab's grading, as E61's was: the camera has never been
calibrated on this card, so there are **no absolute degrees and no mK/W**. Within that, these are exploratory even
relative to the rest:

1. **E62-ORBIT's centre phase against the four-corner mean.** Its contrast is radial (blur-model radial fraction
   **0.924**) and the camera's own post-shutter drift is radial at ~140 mK over 20 s — larger than the signal. The
   ring centroid is also 0.925 mm off `B4C`, so the statistic is a small dipole under a large radial residual.
   DECISIONS §4 allows a radial pattern only as a constant-power swap **labelled exploratory**, and it is. Its
   **confirmatory** replacement is the four clean dipoles `B4C` against each individual corner, +61 to +77 mK.
2. **E62-SWEEP's phase 3 as anything other than a zero crossing.** Its image residual against the five-phase mean
   is a predicted **+8 to +20 mK** centre-positive, wing-negative term, **77–85% radial** in the blur model and
   below the registered floor (§2.5). Its blankness is **corroboration** of a result that rests on the monotone,
   evenly spaced advance of the five positions — the heat slides, it does not jump — and is never reported as a
   radial finding, nor as "exactly zero", which nothing could falsify.
3. **Every absolute millikelvin and every millimetre**, until §7.7's registration produces mm/px *inside its
   registered 10% band*.
4. **Every arrival lag**, as an upper bound only (§6.3).
5. **The orbit's absolute image coordinates**, though **not** its four positions' separations and bearings, and
   **not** its role in the fit. §7.7 uses those four matched-filter peaks as the similarity fit's only data, and
   §3's quantitative clipping rule is what admits them: a matched-filter peak with a clipping-aware template is
   not biased by the wings leaving the frame, while a centroid of the same image is, and the 15% energy test is
   computed from the *measured* footprint and FWHM. What is confirmatory is that the lobe is at **four mutually
   distinct positions** and that their separations and bearings come out right.
6. **The on-die cross-check.** Stock firmware returns one spatially blind aggregate (`temp_c.minshire` = mean over
   34 shires plus peak-holds, whole degrees), so **the dipole cannot be checked on-die at all**. One weak
   registered check survives: the peak-hold spread should widen when half the die is loud against a whole-card
   loud run. The 35 Moortec sensors at 0.061 °C need a signed firmware image and are out of scope.

**Deliberately not filmed**, each for a measured reason: a single shire (3.72 mm against a 29–49 mm blur —
invisible by construction, and the job of the on-die sensors); a checkerboard (Δcentroid 1.2 mm, 0.11 × E61, a
near-pure monopole residual); perimeter ↔ interior (0.17 × E61 **and** degenerate with the radial drift — and its
real result already exists on-die, where E52 measured the perimeter taking **2.04×** as long as the interior, 5 of
5 blocks, so **cite it, do not refilm it**); `MEM8 ↔ EDGE8` (0.17 × E61 and not power-matched); spread versus
clustered at a matched centroid (0.32 × the headline with 82% of it radial — a false null); any dwell below 8.5 s
(the transfer collapses) or above 60 s (the blob overflows the frame and the die climbs into the governor); and
pattern-versus-idle for anything smaller than the whole die (a brightness movie, used once).

---

## 9. What would make the result say "regulators, not die"

A watt in the card's power stage reaches the back of the board **~10× better** than a watt in the die, and at high
card power the regulators shed ~9 W, so a change in *total* power modulates them in perfect phase with the work
and **lock-in cannot remove it**. Equal hart counts are the whole reason this design is a swap. Any one of these
turns the session's conclusion into a statement about the instrument:

1. **A non-null monopole on a constant-power swap** — |card mean of the difference| ≥ 25 mK with permutation
   p < 0.1. Two fixed sources make a level shift, not a contrast that changes sides with the mask.
2. **The lobe does not move in E62-WE42.** This is the hub's own mandatory control
   (`thermal-camera-hub.md:350`): move the work to the opposite half and the peak must move ~11 mm. If it does
   not, the camera is watching the power stages.
3. **E62-WE42 and E62-NS42 land within 30° of each other.** The die's rows and columns are orthogonal; a rotation
   and a mirror both preserve that. A non-orthogonal pair at identical power, identical shires and identical die
   temperature cannot be the die — it is the power stages, or a mask-to-position error in the code.
4. **E62-ORBIT's four corner phases collapse onto fewer than three distinct image positions.** Two fixed
   regulators cannot make four lobes in four places at constant total power. No two-arm dipole can make that
   argument; this is the strongest single statement in the set.
5. **E62-SWEEP's matched-filter position does not advance monotonically.** A fixed source cannot walk.
6. **E62-NULLGEO shows a dipole.** Then either the die map is wrong or the instrument is talking — and
   **E62-NULLAA separates the two**, because its zero does not depend on the die map being right at all.
7. **The amplitude tracks each arm's board power rather than its centroid travel.** Tested directly: E62-W8BE8B
   has the same predicted reduced amplitude (2.65 mK per W per mm) as E62-WE42 at a different power and a
   different travel, and is matched by construction on exactly the features that would cause an electrical
   asymmetry. If E61's 0.44 W survives on *that* pair, it is the card and every monopole in the session is priced
   at ~34 mK rather than zero.
8. **A bright spot appears in a frame corner and does not move with the mask.** At the planned 60 mm lens distance
   the 39.9 × 29.9 mm frame **excludes** the regulators, which sit 20–50 mm from the package centre — so the "two
   fixed hot spots never move" check **cannot be made directly**, and that limit is stated on the page rather than
   claimed as a control. 🛑 **That sentence rests on a lens distance this file itself calls "planned", so it is
   now measured before the hero runs**: E62-CAL's frame-extent check reads the die footprint's pixel extent, the
   clipped-pixel fraction and whether any regulator hot spot is in frame, off the same UNI32 monopole image, and
   compares them against §3's table. The camera is live and read-only, so it costs nothing. If the camera turns
   out to sit further out, the regulators enter a frame corner and are **masked before any statistic is
   computed**.

---

## 10. Files, and what is frozen

| file | what |
|---|---|
| `design/protocol.json` | the sets, the launch counts, the executed phase orders, the predictions with their anchors, the safety numbers, the `runner` plumbing, the three budgets and the slack queue. 🛑 **NOT executable on its own: §4 and §5 of this file are mandatory for the runner.** A runner handed version 1's `protocol.json` alone — the likely case, since that is what it claimed to be — would have fired **410 launches on a shared lab card with no stop file, no lock and no other-user check**, because none of those were in the file. They are now, as structured fields. |
| `design/PROTOCOL.md` | this pre-registration |
| `design/storyboard.md` | the page outline, with each movie's headline finding phrased as a prediction to be confirmed or replaced by the measured value |
| `design/validate_protocol.py` | re-derives the die map from `placements.py` and asserts every mask, shire list, `rc`, hart equality, power and budget; **re-derives every angle any pass rule quotes**; **rebuilds every executed sign order from the block's own `lap_phase_orders` and checks its moments**; **recomputes every predicted amplitude from the registered formula**; **simulates the die phase by phase through the whole session**; and gates **three** budgets at the worst-case 8.6 s launch |
| `design/validate.out` | that run's output — **exit 0** |
| `design/scratch/syn/derive.py` | the derivation and the amplitude/blur model that produced version 1 |
| `design/scratch/syn/pics.py` | the die pictures in §2 |
| `design/scratch/syn2/numbers.py` | every number version 2 changed: the angles, the sign-order moments, the budget at 8.3 / 8.5 / 8.6 s, the bloom's duty cycle, the SNRs at the 27 mK floor, phase 3's residual, the mm/px precisions and the lag table |
| `design/scratch/syn2/make_protocol.py`, `patch*.py` | the edits that produced version 2 of `protocol.json` |
| `design/scratch/syn2/protocol.v1.json` | version 1, kept so §11's diff can be checked |

**Frozen before the first measured pass**, as E60 and E61 did: this file, `protocol.json`, and a
`predictions.json` carrying every number in §6.2 and §6.3, committed into the lab repo at
`tools/claims-v3/e62/` and `docs/reports/data/2026-10-2x-e62/` with its manifest and `gen.sha256`. Later changes
are **amendments**, each with its timestamp and what had and had not been read at the time.

Still open after E62, and said so in advance: the period-versus-dwell octave (a desk job, and nothing here depends
on it); which board revision aifoundry2 carries and where its regulators sit; why the model runs 1.5–2.3× hot; and
the die-to-back coupling, which stays unmeasured until the on-die sensors and the camera run in the same block.

---

## 11. Changes after the red team

A red-team pass re-derived the die map independently from `placements.py` and re-ran `validate_protocol.py`
byte-identically against version 1's `validate.out`. **What it confirmed stands unchanged** and is worth saying,
because a revision is where good parts get lost: every mask matches its shire list and `rc`;
`W12|E12 = N12|S12 = CORE24 = 0x7777f6f6`; the W↔E and N↔S mirrors; `NULLQ12` is `NULLP12` rotated 180° with
identical centroids and identical `(mem_side, ns_edge, by_io, by_ms) = (4, 0, 1, 1)`; the five sweep phases as
exact one-column translates unioning to CORE24 with phase 3 = the registered `CEN8`; W8b/E8b matched on all five
features where W12/E12 are not, so **the `physics.md:582` correction in §2.2 is right**; E61's 10.012 mm anchor
travel; "22 of the 38 die edges straddle P and Q"; and the Sylvester moments as claimed. The constant-power-swap
doctrine, the two nulls, the regulator reasoning, the refusal to read a displacement off a lobe separation, and
the rule that the transfer row is recomputed from the *realised* dwell all survived attack. The cyclic-shift
sequence order is in fact **better** than version 1 claimed: it cancels *any* function of slot position within a
lap, not merely a linear drift, and that is now what §`conventions.sign_orders.sequence` says.

**Nine blockers and thirteen majors are applied. The eight minors are applied too.**

| # | sev | what was wrong | what changed |
|---|---|---|---|
| 1 | blocker | The dwell rule ("switch at the first launch boundary at or after the planned phase end") overran the 75 min cap by 9 min on the launch durations E61 **measured** — 8.31–8.49 s, the whole range *below* the nominal 8.5 — and could give one arm of a swap 6 launches and the other 5 | Phases are **launch counts**; the runner executes exactly *n* launches and switches at the last one's exit. Budget recomputed and **gated at the worst case 8.6 s**. §3, `conventions.dwell_rule`, `phases[].launches`, validator |
| 2 | blocker | `protocol.json` could not express the balanced phase orders the design rests on; a literal `[W12,E12] × cycles=5` run gives plain alternation, whose `Σs·t = −4` leaks 20–35% of E62-WE42's own prediction at the measured drift. "Applied to the ANALYSED phases" was also ambiguous between execution and analysis | Every block carries **`lap_phase_orders`**, the actual per-lap sequence the runner *executes*. The validator rebuilds the realised sign sequence and asserts it equals the registered Sylvester order and that its moments vanish. The ambiguous wording is gone |
| 3 | blocker | E62-ORBIT's pass rule demanded the two diagonals be **opposed within 15°** — geometrically impossible (the true angle is 98.58°), so correct data would have been published as "the regulators, not the die" | Pass rule reads **98.6 ± 12°**; `direction` no longer claims opposition; §2.1 states the trapezoid and the derivation. The validator **recomputes every angle any pass rule quotes** from the die map, and refuses the word in a pass rule |
| 4 | blocker | The "machine-readable protocol a runner executes literally" had no `--stop-file`, no lock, no other-user check, no sampler, no cool-down, no frames path, no forbidden list | `heater.args` carries `--stop-file`; new **`runner`** block with `lock`, `other_user_checks`, `telemetry`, `stop_watcher`, `frames_path`, `forbidden`; new `cooldown_gate`; and both §10 and the file's own `runner.executable_on_its_own: false` say in bold that **§4 and §5 are mandatory** |
| 5 | blocker | The session-abort gate ("of order 500 mK") named neither a window nor a reference, and its 8.5 s rung is shorter than the 4–14 s arrival it measures — two readings straddled the threshold | Rewritten: **the frame mean over the UNI32 rung plus the following 30 s IDLE, against the 180 s pre-session idle, stop below 300 mK**. Plus the **frame-extent check** nothing else performed, before the hero commits 12.9 min |
| 6 | blocker | The FFC exclusion window was ±2 s against the camera's own **~16 s** measured settle, leaving ~14 s of a 140–400 mK *radial*, load-correlated transient in every arm, with the bridging offset fitted inside it | §7.2: **drop ≥ 16 s** (or to a 1 mK/s slope), offsets from windows **outside** the settle, dropped fraction per block **and per arm**, an FFC-phase histogram as a published diagnostic, and **> 30% dropped ⇒ that block is a bound** |
| 7 | blocker | Cool-down gates were unbudgeted (5 × 180 s = 15.0 min against 7.51 min of slack) and had no entry threshold | `cooldown_gate` with **`enter_below_c` 59, gap 30 s extending to ≤ 75 s**, applied only where the next block's power *rises* — three boundaries, not five — **counted in the card-held span** and gated by the validator |
| 8 | blocker | The σ floor, `max(15 mK, 7%)`, was **below the 27 mK measurement it was derived from**, and E62-NULLAA, which measures the real one, ran **tenth of ten** | Floor is **`max(27 mK, 7%)`**; every SNR, both null bounds and the KPI margin restated (§6.1, §6.2); 13.6 mK quoted as the optimistic bound. **E62-NULLAA moves to sixth** and rises to four analysed laps, and is **reduced twice** so the two-lap blocks' quadratic leak gets a *matched* bound |
| 9 | blocker | No per-cycle die gate on the only block that duty-cycles the full card, and the power fallback covered 384-hart blocks only — the 1,024-hart block was in **no branch at all** | `safety.bloom_cycle_stop_c` **64 °C** per on-phase; `power_fallback` branch **(2)** for UNI32 above 45 W (`--per-shire 24` **and** a 127.5 s off-phase); and the validator now **simulates the duty cycle**, not a dwell-weighted mean |
| 10 | major | The three blocks that underwrite everything had 2 analysed laps and the 4-phase order, whose quadratic moment is 4 | **E62-NULLAA to cycles 5.** Its matched two-lap reduction bounds E62-NULLGEO's and E62-W8BE8B's leak for free; **E62-NULLGEO to cycles 5 is slack item #1** (see the budget note below) |
| 11 | major | `B4C`'s own feature mismatch was undeclared — and it is the most mismatched arm of the five | §2.1 carries the full table with **`B4C` = (0,0,0,0)**; the C-minus-corner dipoles are quoted **with the ~34 mK correction**; the per-phase band tightens to **±0.3 W**, and above that the centre result is exploratory |
| 12 | major | The clipping rule, read literally, excluded **every** input to the geometry fit | §3's rule is quantitative: **> 15% of template energy outside the frame**, from the *measured* footprint and FWHM, and **centroid estimators only**. §7.7 and §8 item 5 reconciled |
| 13 | major | mm/px was taken from the **least** precise route (166%), with no precision stated anywhere | §7.7 carries the precision of each route: **orbit fit primary (9.9%)**, sweep **widest** pair cross-check (18.4%), consecutive pairs dropped. **Scale bar only if the combination lands inside 10%** (predicted 8.7%) |
| 14 | major | E62-WE42's orthogonal-axis null was circular — the block *defines* the axis it was measured against | §7.6: the reference is **E62-ORBIT's fitted die frame**, or failing that **E61's 173.8°**; the 40 mK bound attaches to that |
| 15 | major | The "centroid meter" chart mixed three dwell families on one line — a 3.1× spread that is purely the dwell factor | `storyboard.md` §8 plots **amplitude / (W × mm × transfer(realised dwell))**, headline carries the dwell, "Six points" corrected to the nine travels |
| 16 | major | The hero's frozen caption promised a compass direction and a handedness the session solves **two blocks later** | Hero text is **orientation-free** ("round a closed loop, then the middle"); `direction` says "the sense set by the fitted handedness k"; the title's second clause too |
| 17 | major | 90 s of pre-session idle, when the camera's FFC path has **never** fired in any capture on this rig | **180 s**, camera.md's own figure, and a **gate**: one FFC detected by both routes, or the rhythm is published as uncharacterised |
| 18 | major | One 2 h wall "including setup and reduction", with the lock held through a half-hour reduction | **Three caps** — card time ≤ 75, card-held ≤ 75, card session wall ≤ 100 — and the **lock, sampler and Discord claim released before reduction**, which is outside the wall |
| 19 | major | E62-NS42's ±12% ratio band assumed an **unmeasured** isotropic blur | Keystone is the **90° ± 10°** orthogonality; the ratio is **0.661 × r**, with `r` measured for free by E62-ORBIT. §7.7 check 2's fronto-parallel justification corrected (a 30° tilt gives 82°) |
| 20 | major | E62-SWEEP's phase 3 was "predicted **exactly zero**", unfalsifiable and contradicted two sections later | §2.5 and §6.2: first moment exactly zero **by construction**, image residual **+8 to +20 mK** radial, **below the floor**, so blank *within noise*; the exact zero is the matched-filter **position**; the finding rests on the monotone advance |
| 21 | major | §3's dwell/blur table took the model over E61's own measurement, and that choice alone decided which blocks were geometry-legible | §3 now carries **both rows**, says the split assumes the model, and registers that **E62-WE42's measured FWHM decides** — so a 30 mm board earns the 42.5 s blocks' geometry instead of discarding it |
| 22 | major | The `mhz.minion` fallback changed `--per-shire` **mid-block**, cutting a balanced quartet across a 0.875× amplitude change | §5: a flagged block **ends** at the lap boundary and restarts as a **separate block id** at `--per-shire 28`. Laps at different `--per-shire` are never averaged |
| 23 | minor | The two nulls carried **21** and **25 mK** bounds for identical configurations | Both are now `2 × 27 / √laps` from the same floor: **38.2 mK** (2 laps) and **27.0 mK** (4), consistent across `predicted.what`, `pass_rule`, `predicted.bound_2sigma_mk` and §6.2, and **asserted by the validator** |
| 24 | minor | 0.156 mm/px, declared UNMEASURED, was read **inside a pass rule** | Every use is labelled **nominal, planning only, never published**; the pixel figure is **out of** E62-WE17's pass rule |
| 25 | minor | The lag fit's lever arm was quoted as **1.5×** in two places | **1.94×**, with the point count stated: three lock-in periods plus the bloom's step response |
| 26 | minor | The `#community-lab` claim was registered without the standing `<ai>` tag | §4's Claim row: the message **and** the "released" edit each open with a plain `<ai>` on the first line, and the post is read back after sending |
| 27 | minor | `validate_protocol.py` printed "ok" for an identity it did not test (a literal `True` at line 164) and omitted several checks it could make | The literal is replaced by the computed comparison. Added: the 2 h wall; `len(sign_order) == analysed × phases`; **every `predicted.mk` recomputed from the formula** and every travel re-derived from the die map; `order` compared as a **list**, not a set; the registered 2σ bounds; the launch counts; the die simulation; and the angles |
| 28 | minor | The ±0.5 W arm discrimination came from single launches **including the ramp** | §6.2: the **median of the 10 Hz samples in the last 4.0 s** of each launch, with the within-arm scatter reported beside the between-arm difference |
| 29 | minor | E62-WE17's movie could not reach the registered loop length from its own 34 bins | §7.8 carries a **repeat count per movie** with the lap boundary burnt into the frame, reconciled with the storyboard |
| 30 | minor | The dwell-multiple convention did not state its own IDLE exemption | `conventions.dwell_rule`: "IDLE phases launch nothing and are timed directly, so they are exempt"; `launches: 0` and `timed: true` on every such phase, asserted |

### The one place the fixes collided: the budget

The required fixes **add about 11 min of card-held time to a design that had 7.51 min of slack** and simultaneously
demand the 75 min cap hold. That is a real collision, so the trade is made here rather than discovered on the
night, and it follows the red team's own priority — *pay the controls before the extras*:

- **Paid in full:** the worst-case launch budget (+0.69), the 180 s pre-idle (+1.50), the cool-down allowance
  (+3.00, counted), E62-NULLAA's four analysed laps (+2.87), E62-BLOOM's thermal margin (the 64 °C per-cycle gate
  and the fallback branch, +0.00 at nominal power).
- **Trimmed to pay for them:** the post-session idle from 90 s to 60 s (−0.50), since the 180 s pre-idle now
  carries the reference frame.
- **Deferred, and registered as slack item #1:** **E62-NULLGEO to cycles 5** (+2.87). E62-NULLAA got the four
  laps first because its number *is* the σ on every error bar — the red team's own argument for the fix — and
  because its matched two-lap reduction bounds NULLGEO's residual leak for nothing. At two analysed laps NULLGEO
  still bounds the geometric systematic at 38.2 mK, 8.3% of the headline, and still supplies `nullgeo.mp4`.
- **Not done, and why:** E62-ORBIT was *not* shortened to a 17.0 s dwell, although that would have saved 4.30 min
  and made its four positions unclipped under §3's own model. At 17.0 s the C-minus-corner dipoles fall from
  61–77 mK to 36–46 mK, i.e. to about the size of the ~34 mK electrical correction they already carry — which
  would destroy the "corners **or the centre**" answer his ask named explicitly. The quantitative clipping rule
  (fix 12) buys the same geometry without that cost.

The result: **63.52 min of card time, a 74.27 min card-held span and a 91.27 min card session wall**, against 75 /
75 / 100, with **0.73 min of slack at an 8.6 s launch and 2.78 min at 8.3 s**. `validate.out` is that run.

### The red team's optional notes, and what was done with them

- **Promote the 42.5 s `B4NW ↔ B4SE` diagonal out of the slack** — it is now **slack item #2**, with its
  ≈ +290 mK prediction written down, ahead of the extra orbit laps. It is not committed because there is 0.73 min
  of slack, not 4.30.
- **Split E62-ORBIT's dwell** — declined, with the reason above.
- **A one-frame field-of-view check in the pre-session idle** — adopted, as E62-CAL's frame-extent check (fix 5),
  which is where the UNI32 monopole image already is.
- **Register what happens if E62-CAL finds power LOW** — adopted as `power_fallback` branch **(3)**: below 12.0 W
  on a 384-hart arm, E62-SWEEP is dropped and its minutes go to E62-NULLGEO and the diagonal.
