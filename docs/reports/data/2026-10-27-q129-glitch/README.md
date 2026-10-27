# The glitch factor of the open TensorFMA32, measured (Q129)

**Request Q129(b). Tuesday 27 October 2026 (week 44), 14:27 – 15:10 PDT, on the lab's EDA host** —
CPU only, no card, no `/dev/et*`, under `nice -n 19` with at most four processes at once. Every
input and every tool is open; nothing here needs a card, a licence or a private file.

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

**And a second thing fell out that was not asked for: this run prices 100% of the extracted
capacitance.** It simulates `txfma_routed.v`, the post-route netlist, so every one of the 16,440
nets OpenRCX extracted is a net the simulation names — against 50.5%/56.3% in Q126(e) and
43.6%/51.8% in [Q129(a)](../2026-10-27-q129-routed-netlist/README.md). That is the "next best
hour" Q129(a) named, and it supersedes both of those partial-coverage deltas. (62.3% of those
farads belong to a net that toggles at all in a random multiply-add; the rest is idle wire.)

## What it does to Q128's waterfall

Applied to the ledger the way the measurement is scoped — the clock tree carried through
unchanged at ×1.000, the signal capacitance at ×1.4929, the signal transition count (which is what
the cells' internal energy is priced per) at ×1.6800:

| per random multiply-add, pJ | published | + Q129(a)'s wire | **+ glitches** |
| --- | ---: | ---: | ---: |
| wire between the cells | 0.590 | 0.453 | 0.453 |
| switching, total | 1.516 | 1.379 | **1.877** |
| the cells' internal energy | 0.431 | 0.429 | **0.721** |
| **bottom-up total** | 1.947 | 1.810 | **2.598** |
| unaccounted against the board's 5.783 | 3.836 | 3.975 | **3.185** |
| unaccounted against the minion rail's 4.337 | 2.390 | 2.529 | **1.739** |
| closure against the board | 33.7% | 31.3% | **44.9%** |

**So the glitch factor moves 0.790 pJ from "unaccounted" to "accounted"** — the largest single
step any of these open-flow measurements has made, and in the opposite direction to Q129(a)'s
wire correction, which moved 0.137 pJ the wrong way. On the published ledger without that wire
correction the same multipliers give 1.947 → 2.743 pJ and a closure of 47.4%.

**Measured end to end instead, with no published term reused** (this run's own ½CV² at 100%
capacitance coverage, plus Q126(d)'s 0.1188 fJ of internal energy per signal transition):

| Miller k | switching, zero → timed | internal, zero → timed | bottom-up | unaccounted | closure |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 1.2686 → 1.6929 | 0.4127 → 0.6933 | 1.681 → **2.386** | 4.102 → **3.397** | 29.1% → **41.3%** |
| **1** | **1.5119 → 2.0121** | **0.4127 → 0.6933** | 1.925 → **2.706** | 3.858 → **3.078** | 33.3% → **46.8%** |
| 2 | 1.7552 → 2.3313 | 0.4127 → 0.6933 | 2.168 → **3.025** | 3.615 → **2.758** | 37.5% → **52.3%** |

That zero-delay bottom-up of 1.925 pJ lands within 1% of the published 1.947 — by two errors
cancelling, not by agreement: the published figure priced **half** the farads at a Steiner
estimate that Q129(a) showed to be **20% high**, and this one prices **all** of them at the
extraction.

## The Hamming ladder: the slope the project rests on carries ×1.28–1.38

The glitch factor is **strongly activity-dependent**, so one number for "the unit" would be
misleading on its own. Both ladder partners were run at h = 0, 1, 2, 4, 8 — ten more pairs — and
fitted the way E60's own reducer fits them, a line over h ≥ 1 with a free intercept against the
*designed* flip count:

| | unit's toggle factor, h = 0 → 8 | slope, switching | slope, + cells' internal | E60 at the board | share of the board |
| --- | ---: | ---: | ---: | ---: | ---: |
| `lq` (quiet, A = 1.0) | ×1.002 → ×1.232 | 35.10 → **44.85** fJ (**×1.278**) | 48.12 → **63.67** fJ (×1.323) | 116.7 fJ | 30.1% → **38.4%**; with internal 41.2% → **54.6%** |
| `lb` (busy, A = π) | ×1.003 → ×1.227 | 36.81 → **49.18** fJ (**×1.336**) | 51.56 → **71.15** fJ (×1.380) | 129.9 fJ | 28.3% → **37.9%**; with internal 39.7% → **54.8%** |

With the operands held still (`h0`) the factor is **×1.00**: the clock is 97.6% of that rung and
the clock does not glitch. It climbs ×1.06, ×1.09, ×1.15, ×1.23 through the ladder and reaches
×1.57 at `randn`. The *marginal* cost of one more flipped bit — which is what
[POWER.md](../2026-10-26-open-netlist/POWER.md)'s "about **30%** of what the board pays for a
flipped operand bit on switching alone, and about **40%** with the cells' internal energy" is made
of — carries ×1.28 to ×1.38.

**So that claim becomes "about 38% on switching alone and about 55% with internal energy".** The
lane's own arithmetic is a bigger share of the board's per-flipped-bit price than the project has
been saying, and glitches are the whole of the difference.

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
- **The hierarchy choice moves it 5%**, as it moves everything else in this flow. The honest band
  across the two netlists is **×1.50–1.57 in toggles and ×1.29–1.33 in energy at the unit**, and
  **×2.09–2.39 / ×2.07–2.33 in the tree**.
- **The energy factor barely moves over the Miller band** (×1.334 / ×1.331 / ×1.328 at k = 0/1/2):
  a glitch is a count, not a capacitance.
- **The Icarus run, with every caveat in `sdf_icarus_probe.txt`, reads higher** — zero-delay XORs,
  simultaneous flip-flops and a 10 ps delay grid all manufacture glitches. It is an independent
  instrument and it brackets the answer from above.
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

Reproduce it with the commands in
[`tools/open-flow/txfma/README.md`](../../../../tools/open-flow/txfma/README.md) § "The timed pass".

## What this does not settle

- **One tile per pattern, and no repeat**, so there is no interval on any ratio here. Eleven
  stimuli ran (`randn` and both ladders at h = 0, 1, 2, 4, 8) on one netlist pair, each once; the
  engine is deterministic, so a repeat would reproduce the number exactly and tell you nothing.
  What is missing is a second *tile* and a second *seed*.
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
