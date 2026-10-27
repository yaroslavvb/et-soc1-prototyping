# The glitch factor of the open TensorFMA32, measured (Q129)

**Request Q129(b). Tuesday 27 October 2026 (week 44), 14:27 – 15:10 PDT, on the lab's EDA host** —
CPU only, no card, no `/dev/et*`, under `nice -n 19` with at most four processes at once. Every
input and every tool is open; nothing here needs a card, a licence or a private file.
*Corrected the same evening after verification — nine fixes, no measured quantity changed; the
list is the last section of this file.*

**The glitch factor exists now.** [Q126(e)](../2026-10-26-open-netlist/POWER.md)'s second blocker
is cleared, and the number the record has been quoting from the tape-out flow alone —
*"the multiplier tree makes about 1.5 times as many toggles as at zero delay and spends about 1.4
times the energy"* — has an open-flow counterpart, on the detailed-routed netlist with extracted
parasitics:

| per random fp32 multiply-add | toggles, zero delay | toggles, timed | ×  | pJ (k = 1), zero | pJ, timed | × |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **the whole unit** | **4,132.5** | **6,494.8** | **1.572** | **1.5119** | **2.0121** | **1.331** |
| its signal half | 3,473.8 | 5,836.2 | 1.680 | 1.0149 | 1.5151 | 1.493 |
| its clock tree | 658.6 | 658.6 | **1.000** | 0.4970 | 0.4970 | **1.000** |
| the multiplier | 954.7 | 2,003.4 | 2.098 | 0.2535 | 0.4644 | 1.832 |
| **the Wallace tree** | **628.2** | **1,499.9** | **2.387** | **0.1392** | **0.3242** | **2.329** |
| &nbsp;&nbsp;`f1/wallace1` | 408.7 | 1,188.9 | 2.909 | 0.0885 | 0.2525 | 2.854 |
| &nbsp;&nbsp;`f2/wallace2` | 219.5 | 311.0 | 1.417 | 0.0508 | 0.0717 | 1.413 |
| Booth rows (`f1/ppg`) | 281.1 | 392.3 | 1.396 | 0.1049 | 0.1171 | 1.116 |
| product adder (`f2/prod_adder_64b`) | 45.4 | 111.2 | 2.450 | 0.0094 | 0.0230 | 2.453 |

6,265 of the 10,376 nets that move at all glitch; **not one net toggles fewer times with delays
than without**. The clock tree's ×1.000 is measured, not assumed, and is the cheapest sanity check
in the file.

**The band to quote beside ×1.572 is the cross-instrument one: ×1.55–1.76 in toggles and
×1.32–1.44 in energy.** The ×1.50–1.57 / ×1.29–1.33 above is one instrument over two netlists and
two SDF options — a hierarchy-and-options band, not an uncertainty — while the second instrument
in this very directory reads ×1.762 / ×1.444 (§ Sensitivities).

**And a second thing fell out that was not asked for: this run prices 100% of the extracted
capacitance.** It simulates `txfma_routed.v`, the post-route netlist, so every one of the 16,440
nets OpenRCX extracted is a net the simulation names — against 50.5%/56.3% in Q126(e) and
43.6%/51.8% in [Q129(a)](../2026-10-27-q129-routed-netlist/README.md). That is the "next best
hour" Q129(a) named, and it supersedes both of those partial-coverage deltas. (62.3% of those
farads belong to a net that toggles at all in a random multiply-add; the rest is idle wire.)

Two clauses that 100% needs. **682 of the 17,122 netlist net names (4.0%) have no extraction entry
at all** and are priced at zero; exactly one of them moves — `wallace_fC41_f2a_h[63]`, 16
transitions against a settled count of 0, so a pure glitch — and its omission can therefore only
*understate* the timed energy, by a nil amount. And the fractions it is compared against come from
a **different extraction**: the published 50.5% is 23,762 of 47,093 fF of *Steiner estimate*,
while this 100% is of the SPEF extraction's 38,850 fF at k = 1. One question, three denominators.
What is strictly true: no net this netlist contains is left unpriced for want of an extraction.

## What it does to Q128's waterfall

**Measured end to end, with no published term reused** — this run's own ½CV² on the routed
netlist at 100% extraction coverage, plus Q126(d)'s 0.1188 fJ of internal energy per signal
transition. This is the waterfall to use, and the only one of the three in this section that is
self-consistent:

| Miller k | switching, zero → timed | internal, zero → timed | bottom-up | unaccounted vs board | closure |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 1.2686 → 1.6929 | 0.4127 → 0.6933 | 1.681 → **2.386** | 4.102 → **3.397** | 29.1% → **41.3%** |
| **1** | **1.5119 → 2.0121** | **0.4127 → 0.6933** | **1.925 → 2.706** | 3.858 → **3.078** | 33.3% → **46.8%** |
| 2 | 1.7552 → 2.3313 | 0.4127 → 0.6933 | 2.168 → **3.025** | 3.615 → **2.758** | 37.5% → **52.3%** |

**So the glitch factor moves +0.781 pJ from "unaccounted" to "accounted"** (k = 1; band 41.3% at
k = 0 to 52.3% at k = 2) — the largest single step any of these open-flow measurements has made,
and in the opposite direction to Q129(a)'s wire correction, which moved 0.137 pJ the wrong way.
**Do not compose this with Q129(a)'s or `eda-cap`'s deltas**: this run re-prices the same
capacitance they re-priced, at 100% coverage, so it replaces them rather than adding to them.

That zero-delay bottom-up of 1.925 pJ lands within 1% of the published 1.947 — by two errors
cancelling, not by agreement: the published figure priced **half** the farads at a Steiner
estimate that Q129(a) showed to be **20% high**, and this one prices **all** of them at the
extraction.

**Bridges to the two published ledgers**, for following their numbers and nothing else. Each
applies this run's multipliers (signal capacitance ×1.4929, signal transitions ×1.6800, clock
carried through at ×1.000) to a switching total that came from a *different* simulation:

| per random multiply-add, pJ | (A) published | (B) + Q129(a)'s wire |
| --- | ---: | ---: |
| wire between the cells | 0.590 | 0.453 |
| switching, total | 1.516 → 2.019 | 1.379 → 1.877 |
| the cells' internal energy | 0.431 → 0.724 | 0.429 → 0.721 |
| bottom-up total | 1.947 → 2.743 | 1.810 → 2.598 |
| closure against the board | 33.7% → 47.4% | 31.3% → 44.9% |

⚠️ **(B) is internally inconsistent and the first version of this file made it the headline.** It
splits Q129(a)'s switching total with Q129(a)'s **26.7%** clock share, while this run measures
**32.88%** on the same routed netlist (k = 1, zero delay) — 23% relative, because Q129(a)
re-priced *pre*-CTS toggle counts (477 clock toggles per multiply-add) against post-route
capacitance while this run simulates the post-CTS netlist (658.6). Re-run (B) with 32.88% and it
reads **2.556 pJ and 44.2%**, not 2.598 and 44.9%. The three waterfalls agree to within 0.11 pJ
at k = 1, which is the size of the inconsistency; (C) above carries none of it.

## The Hamming ladder: the slope the project rests on carries ×1.28–1.38

The glitch factor is **strongly activity-dependent**, so one number for "the unit" would be
misleading on its own. Both ladder partners were run at h = 0, 1, 2, 4, 8 — ten more pairs — and
fitted the way E60's own reducer fits them, a line over h ≥ 1 with a free intercept against the
*designed* flip count:

| | unit's toggle factor, h = 0 → 8 | slope, switching | slope, + cells' internal | E60 at the board | share of the board |
| --- | ---: | ---: | ---: | ---: | ---: |
| `lq` (quiet, A = 1.0) | ×1.002 → ×1.232 | 35.10 ± 2.23 → **44.85 ± 2.30** fJ (×1.28) | 48.12 ± 3.23 → **63.67 ± 3.22** fJ (×1.32) | 116.7 fJ | 30.1 ± 1.9% → **38.4 ± 2.0%**; with internal 41.2 ± 2.8% → **54.6 ± 2.8%** |
| `lb` (busy, A = π) | ×1.003 → ×1.227 | 36.81 ± 3.27 → **49.18 ± 2.02** fJ (×1.34) | 51.56 ± 4.73 → **71.15 ± 2.92** fJ (×1.38) | 129.9 fJ | 28.3 ± 2.5% → **37.9 ± 1.6%**; with internal 39.7 ± 3.6% → **54.8 ± 2.2%** |

**± is the fit's own standard error at 1 σ, 2 degrees of freedom on a four-point fit** — 4–9% of
the slope. The ladder is markedly non-linear (POWER.md's own trap 3) and the residuals are large
and structured: `lq` h4 sits +15.1 fJ above the timed line and `lb` h4 −13.1 fJ below it, against
slopes of 45–49 fJ. The *ratio* is the sturdier half, but not sturdy either: leave one rung out
and it runs ×1.24–1.29 (`lq`) and ×1.31–1.55 (`lb`), the widest excursion being the window that
drops h = 8. **About 1.3, and about 38%, is what these four points support — not 1.278 and 38.4%.**

With the operands held still (`h0`) the factor is **×1.00**: the clock is 97.9% (`lq`) / 97.8%
(`lb`) of that rung *measured here* and does not glitch. (POWER.md's 97.6%/97.7% for the same
rungs is its own `keep`-netlist figure; the first version of this file quoted it as if it were
this run's.) It climbs ×1.06, ×1.09, ×1.15, ×1.23 through the ladder and reaches ×1.57 at `randn`.
The *marginal* cost of one more flipped bit — which is what
[POWER.md](../2026-10-26-open-netlist/POWER.md)'s "about **30%** of what the board pays for a
flipped operand bit on switching alone, and about **40%** with the cells' internal energy" is made
of — carries ×1.28 to ×1.38.

**So that claim becomes "about 38% on switching alone and about 55% with internal energy"**, each
good to about ±2 percentage points at 1 σ (30–47% at 95% with 2 dof). The lane's own arithmetic is
a bigger share of the board's per-flipped-bit price than the project has been saying, and glitches
are the whole of the difference — the conclusion survives the interval, the four-figure precision
does not.

(The zero-delay slopes above, 35.10 and 36.81 fJ, are this run's independent reproduction of
POWER.md's `mixed` figures of 34.8 and 38.3 fJ — within 1% and 4%, on a different netlist stage,
different capacitances and a different simulator.)

## Against the record, and against Q124

| | the tape-out flow (`tfma.glitch`) | this run, open flow |
| --- | ---: | ---: |
| Wallace tree, zero delay | 1,244 toggles/MAC | 628.2 |
| Wallace tree, timed | 1,871 | **1,499.9** |
| toggle factor | ×1.504 | **×2.387** |
| energy factor | ×1.4 | **×2.329** |

Two readings, and both matter.

- **The open tree glitches 1.59× as hard**, so the record's 1.5×/1.4× is *not* transferable to this
  netlist: in the tree it is ×2.39 and ×2.33.
- **But the two flows' timed tree counts are only 1.25× apart, where at zero delay they were
  1.98× apart** ([Q126(e)](../2026-10-26-open-netlist/POWER.md) § "The toggle comparison, at
  matched scope"). The open flow builds a tree that settles in fewer transitions and then glitches
  more, and counting the glitches brings the two within a quarter. That is the first time these two
  flows have agreed about the tree to better than a factor of two.
- **Q124's "glitches add about 40% to the tree's energy"** is the ×1.4 above. In the tree the
  measured factor is ×2.33, so applied to a tree figure that understates by 1.7×; at the **whole
  unit** the measured factor is ×1.33, so a page that applied ×1.4 to a unit-level number was about
  right for the wrong reason. The chip-diagram page's `tfma.flip.energy` note and
  [05-claims.md](../../../findings/05-claims.md)'s "×1.4 for glitches" both use it at tree scope.

## How it was measured, and why not with Icarus

The bench Q126(e) built is the right one — `tb_timed.v` replays the unit's recorded pins so a
plain-Verilog simulator can drive the netlist — and its SDF half still aborts. The diagnosis
Q126(e) asked for is in [`sdf_icarus_probe.txt`](sdf_icarus_probe.txt), in full. In short:

- **it is structural, not a size problem.** Twenty `(INTERCONNECT ...)` entries abort exactly as
  42,525 do, and all 16,480 cell blocks with none of them run to the end. Icarus's `intermodpath`
  wants a delay between two *module* ports and this netlist is flat.
- **`-gspecify` was not the only missing flag**: without `-ginterconnect` Icarus says so itself
  ("Did you run iverilog with '-ginterconnect'?") before asserting.
- **`$sdf_annotate(sdf)` with no scope annotates nothing at all** — it resolves instance names in
  the calling module, so every cell block reports "Unable to find `_08184_` in scope tbt". The fix
  is `$sdf_annotate(sdf, dut)`. The timed figure Q126(e) could not get would have been wrong even
  if the abort had not happened.
- **`(COND (~A1 & ~A2) ...)`, the form OpenSTA writes, is rejected** (46,066 of 51,626 conditional
  entries), and XOR2x2/XNOR2x2 have no unconditional `ifnone` path at all, so dropping the COND
  entries runs 1,390 cells in the middle of the tree at zero delay.

So the third route the request allowed was taken: **a small event-driven simulator over the
netlist**, [`tools/open-flow/txfma/gsim.py`](../../../../tools/open-flow/txfma/README.md). It is
short because this library is four Verilog primitives (`and`, `or`, `not`, `buf`) plus one
flip-flop and one latch, read straight out of ASAP7's own models; it carries SDF `IOPATH`,
`(COND ...)` and `INTERCONNECT` delays in integer femtoseconds, and uses an inertial delay model
(a transition still pending when its cause reverses is cancelled, so a pulse shorter than the
delay it would travel through is swallowed).

**The validation gate.** One engine runs both passes and `--sdf` is the only difference between
them. With no SDF the per-net toggle counts must reproduce Icarus's own zero-delay VCD exactly:

| netlist | gsim | Icarus | nets | nets differing | exact |
| --- | ---: | ---: | ---: | ---: | :---: |
| `mixed` | 2,115,833 | 2,115,833 | 9,841 / 9,841 | 0 | ✅ |
| `keep` | 2,337,966 | 2,337,966 | 11,118 / 11,118 | 0 | ✅ |

Net by net, not just in total ([`check_mixed.json`](check_mixed.json),
[`check_keep.json`](check_keep.json)). Two bugs were found by that gate and not by anything else:
input pins were being mapped to the wrong slot of a cell's model (the first run made the design
inert), and two flip-flops in series raced through a zero-delay clock tree of unequal depth, which
a proper non-blocking-assignment region fixed and which showed up as exactly 12 toggles on 6 nets
out of 2.1 million.

## Sensitivities, and a second instrument

| | unit, toggles / energy | tree, toggles / energy |
| --- | ---: | ---: |
| **full SDF, `mixed` — the number** | **×1.572 / ×1.331** | **×2.387 / ×2.329** |
| the same without interconnect delay | ×1.553 / ×1.318 | ×2.339 / ×2.282 |
| the same without `(COND ...)` paths | ×1.578 / ×1.333 | ×2.424 / ×2.364 |
| full SDF, the `keep` netlist | ×1.495 / ×1.287 | ×2.086 / ×2.070 |
| Icarus, cell delays only (an upper bound) | ×1.762 / ×1.444 | ×2.940 / ×2.871 |
| every zero-delay delta event (a convention) | ×1.808 / ×1.486 | ×2.659 / ×2.621 |

- **Interconnect delay adds only 1.2%** to the unit's toggle factor. The skew between two loads of
  one net is not what makes these glitches; the cells' own path imbalance is.
- **The hierarchy choice moves it 5%**, as it moves everything else in this flow: ×1.50–1.57 in
  toggles and ×1.29–1.33 in energy at the unit across the two netlists, ×2.09–2.39 / ×2.07–2.33 in
  the tree. **That is a hierarchy-and-options band, not an uncertainty** — the honest band is the
  **cross-instrument** one, ×1.55–1.76 in toggles and ×1.32–1.44 in energy, and the first version
  of this file quoted the narrow one as if it were the whole story.
- **The energy factor barely moves over the Miller band** (×1.334 / ×1.331 / ×1.328 at k = 0/1/2):
  a glitch is a count, not a capacitance.
- **The Icarus run, with every caveat in `sdf_icarus_probe.txt`, reads higher** — an independent
  instrument that brackets the answer from above. **The two instruments are not yet compared
  like-for-like, and the 13.5% between them is not attributed.** The nearest matched pair is gsim
  cells-only with COND *kept* (×1.553) against Icarus cells-only with COND *dropped* (×1.762). Of
  the three mechanisms the probe names, one cannot explain the gap: **gsim has no CLK→Q delay
  either** (`sdf_bind.iopath_missing` = 1,974 of 42,486 input pins), so simultaneous flip-flop
  launch is common to both and makes both *conservative*. What is left is Icarus running 1,390
  XOR2x2/XNOR2x2 at zero delay in the middle of the tree — gsim back-fills those pins from the
  conditional entries (`iopath_from_cond` = 2,780) — and its 10 ps delay grid against gsim's
  femtoseconds. No run here separates the two, and `--no-cond` would *not* reproduce Icarus's
  zeroed XOR paths, so the matched pass needs a change to `gsim.py`, not just a flag. Open.
- **Counting every zero-delay delta event gives ×1.808, MORE than the timed run's ×1.572.** So the
  glitch factor is not an artefact of counting every edge: a naive delta count overstates it, and
  inertial delay removes more pulses than the real delays create.

## Files

| File | What |
| --- | --- |
| `summary.txt` | every number above, generated |
| `summarize.py` | the generator, with the published constants it compares against |
| `glitch_mixed_full.json` | **the measurement**: per scope, toggles and ½CV² at Miller k = 0/1/2, plus the 25 nets that glitch most |
| `glitch_mixed_nointer.json`, `glitch_mixed_nocond.json` | the two SDF sensitivities |
| `glitch_keep_full.json` | the same on the hierarchy-kept netlist |
| `glitch_mixed_icarus.json` | the Icarus cell-delay-only pair, as an upper bound |
| `glitch_mixed_zerodelta.json` | zero-delay delta events against settled values, as a diagnostic |
| `glitch_mixed_l{q,b}_h{0,1,2,4,8}.json` | the ten Hamming-ladder rungs, both partners |
| `check_mixed.json`, `check_keep.json` | the validation gate, net by net |
| `toggles_mixed_zero.json.gz`, `toggles_mixed_timed.json.gz` | the per-net toggle tables both passes produced, 17,122 nets |
| `sdf_icarus_probe.txt` | why Icarus aborts, the slice table, and two SDF traps worth propagating |
| `versions.txt` | tools, inputs and their hashes |
| `stimulus/*.vec.gz` | **the eleven stimuli**, gzipped: `randn` and both ladders at h = 0, 1, 2, 4, 8. One line per 1 ns step; `gunzip` and pass to `gsim.py --vectors` |

**What is and is not here.** The stimulus is committed (above; `randn.vec` has the md5 in
`versions.txt`, 56f45fbf…). The two netlists and their SDFs are **not** — 3 to 21 MB each — and
nor are the ASAP7 models; they are identified by sha256 in `versions.txt` and regenerated by
[Q129(a)](../2026-10-27-q129-routed-netlist/README.md)'s `post_route.tcl`. So this directory
reproduces the *reduction* from committed inputs and the *simulation* only on a tree that has
those netlists. The commands are in
[`tools/open-flow/txfma/README.md`](../../../../tools/open-flow/txfma/README.md) § "The timed
pass". (The first version of this file, and commit `76fadaf4`'s message, said "the committed
`randn.vec`" when no `.vec` was committed at all.)

## Two checks on the timed run that the first version left unstated

- **The timed pass computes the same function as the zero-delay one, to 1 part in 900.** Its own
  settled count is 2,118,201 against the zero run's 2,115,833: **+0.112% over 32 nets** of 17,122.
  That is positive evidence worth stating, because the netlist misses its SDC by about 2×. Using
  the timed run's own settled as the denominator gives ×1.5699 at the whole design against the
  reported ×1.5716 — a 0.1% effect, and the published convention (the zero-delay pass is the
  denominator) is the one used.
- **4.6% of the "timed" netlist ran at zero delay in gsim too.** `sdf_bind.iopath_missing` = 1,974
  of 42,486 input-pin paths: essentially every flip-flop's and clock gate's CLK→Q, because the
  behavioural stand-in `asap7_seq_behav.v` carries no `specify` block. So gsim launches every
  flip-flop simultaneously and removes the launch skew that would deepen these glitches — ×1.572
  is conservative on that axis too. `sdf_icarus_probe.txt` faults Icarus for exactly this; it is
  only fair to fault the engine used for the measurement.

## What this does not settle

- **One tile per pattern, and no repeat**, so there is **no repeat-variance** interval on any
  ratio here. Eleven stimuli ran (`randn` and both ladders at h = 0, 1, 2, 4, 8) on one netlist
  pair, each once; the engine is deterministic, so a repeat would reproduce the number exactly and
  tell you nothing. What is missing is a second *tile* and a second *seed*. (The ladder *fits* do
  carry a regression interval, and it is printed with every slope above; the headline ratios carry
  no interval at all, only the cross-instrument spread.)
- **Of Q126(e)'s three reasons the bottom-up figure is a floor, this run retires the coverage
  one** — the routed netlist is what is simulated, so no extracted net goes unpriced. Q129(a)
  retired the *coupling/SPEF* one. The third stands untouched by both: the ledger covers one
  lane's arithmetic while the board also pays for the register-file read ports, the operand bus,
  the result path, pipeline registers and leakage.
- **These delays are not the card's.** The SDF is ASAP7 RVT TT at 0.700 V and 25 °C, while the
  energy is priced at the 0.517 V minion rail, where every delay would be longer and the glitches
  deeper. And the placed design misses its 1250 ps SDC by about 2× (`wns` −1,322 ps after
  extraction), so this is the glitch factor of a netlist that would run near 400 MHz.
- **Inertial delay with full pulse rejection is the conservative model.** A transport-delay model,
  or Verilog's pulse-control defaults with a shorter rejection limit, would report more glitches.
- **The internal-energy term is scaled, not measured.** Q126(d)'s 0.1188 fJ per transition is a
  census-weighted average over combinational cells and skips the flip-flops' and clock gates' own
  clock-pin energy; a glitch on a cell input costs internal energy whether or not the output moves,
  which this does not price at all.
- **ASAP7 is a predictive library**, not the process the ET-SoC-1 was built in. Every number here
  is what an open 7 nm kit makes of this RTL, and that is the point: it can be checked.

## What the first version of this directory got wrong

Written on first publication (commits `4a6a840a`, `76fadaf4`), corrected the same day after
verification. No measured quantity changed; every correction is to a headline, an interval or a
claim about what was committed.

| Claim, as first published | Corrected |
| --- | --- |
| headline waterfall **1.810 → 2.598 pJ, closure 31.3% → 44.9%, "+0.790 pJ"** | that is bridge **(B)**, the composition this result's own open issues told the integrator *not* to make, and it splits Q129(a)'s switching total with Q129(a)'s 26.7% clock share against this run's measured **32.88%**. The headline is now the measured-end-to-end **(C)**: **1.925 → 2.706 pJ, +0.781 pJ, closure 33.3% → 46.8%**. (B) with 32.88% reads 2.556 pJ / 44.2% |
| "the honest band … **×1.50–1.57** in toggles and ×1.29–1.33 in energy" | that is one instrument over two netlists; the second instrument in this directory reads **×1.762 / ×1.444**. The band to quote is the cross-instrument **×1.55–1.76 / ×1.32–1.44**, and the 13.5% between the nearest matched pair is **not attributed** — a like-for-like pass needs a change to `gsim.py`, not a flag |
| ladder slopes **35.10 → 44.85 fJ**, share **38.4%**, "no interval on any ratio" | the four-point fit yields a regression SE directly and it is **4–9%**: 35.10 ± 2.23 → 44.85 ± 2.30 fJ, share **38.4 ± 2.0%**. Say *about 38%* and *about 1.3*; leave one rung out and the ratio runs ×1.24–1.55 |
| "the clock is **97.6%** of that rung" (four places) | 97.6%/97.7% is POWER.md's `keep`-netlist figure. Measured here, on the routed `mixed` netlist: **97.9%** (`lq` h0) and **97.8%** (`lb` h0) |
| "its re-recording reproduces **the committed `randn.vec`** byte for byte" | the re-recording is byte-exact (md5 56f45fbf…) but **no `.vec` was committed**. All eleven now are, in `stimulus/`; the netlists and SDFs still are not, and § Files says so |
| "**100%** of the extracted capacitance" | exact, and now carries its two clauses: **682 netlist names (4.0%)** have no extraction entry (one moves, a pure glitch, so the omission understates), and the 50.5%/56.3% it is compared against are fractions of a *different* extraction |
| the settled divergence and gsim's own missing CLK→Q paths | not mentioned at all; both are now stated above, the first as positive evidence, the second as a reason ×1.572 is conservative |
| "this run retires the **second** of Q126(e)'s three floor-reasons" | Q129(a) retired the coupling/SPEF reason; this run retires the **coverage** one |
| undo note "about **1.5 GB**, including two 150–220 MB Icarus VCDs" | **1.1 GB apparent** (612 MB on disk; the filesystem compresses), and **four** files over 70 MB — 225, 174, 156 and 74 MB of VCD — plus four 54–68 MB `.vvp` images. The undo path itself was right |
