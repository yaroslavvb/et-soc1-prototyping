# The open TensorFMA32, detailed-routed: SPEF with coupling, and the wire half re-priced (Q129)

**Request Q129(a). Tuesday 27 October 2026 (week 44), 13:54 – 14:14 PDT, on aifoundry1** — CPU
only, no card, no `/dev/et*`, under `nice -n 19` in a container capped at 8 of 16 cores. Every
input and every tool is open; nothing here needs a card, a licence or a private file.

**Detailed routing closes.** The first of [Q126(e)](../2026-10-26-open-netlist/POWER.md)'s two
blockers is cleared: the current OpenROAD in the ORFS container routes this design to **zero DRC
violations** in 193 s, where the 2022 conda build stopped with `DRT-0255` on the top-level port
nets in all ten configurations tried. OpenRCX then extracted **251,162 coupling capacitors** on
the `mixed` netlist, the SPEF is written and read back, and an SDF is waiting on aifoundry1 for
the glitch bench.

**And the headline is a correction, not a confirmation.** The published pages say the
global-route Steiner estimate "has no coupling term, so it is a lower bound on the wire half of
each net". It is not. The ORFS asap7 platform's `setRC.tcl` gives the estimator **0.1658 fF per
micron** for a signal wire, which is a layer's *total* capacitance at nominal spacing — the
neighbour coupling is already bundled into it and grounded. Against the extraction the estimate
comes out **20% high**, not low:

| the whole design's capacitance, fF | `mixed` | `keep` |
| --- | ---: | ---: |
| pin capacitance, from ASAP7's liberty (**unchanged by routing**) | 26,844.3 | 33,469.6 |
| wire, global-route Steiner estimate | **14,427.4** | **15,532.8** |
| wire, extracted to ground | 5,028.1 | 5,344.1 |
| wire, extracted coupling (each capacitor once) | 3,495.8 | 3,633.1 |
| **wire, extracted, Miller k = 1** (each coupling cap charged to **both** its nets) | **12,005.8** | **12,605.2** |
| extracted (k = 1) ÷ Steiner | **0.832** | **0.812** |
| coupling as a share of the extracted wire capacitance | **41.0%** | 40.5% |

**Where the 20% comes from, measured.** The detailed router used **82,358 µm** of wire and
166,805 vias on `mixed`. That carries 0.1035 fF/µm of physical capacitance, or 0.1458 fF/µm as
each driver sees it at k = 1. The Steiner estimate instead assumes **87,642 µm — 1.064× the
routed length — at 1.137× the extracted fF/µm**, and 1.064 × 1.137 = 1.210, against the measured
ratio of 1.202. So it is about a third topology and two thirds the unit capacitance, and neither
is a coupling term that was missing.

## The Miller factor, stated

A coupling capacitor between nets A and B costs nothing when they move together, C·V when one
moves past a still neighbour, and 2C·V when they move oppositely. Everything here is reported at
three factors, and **k = 1 — the quiet-neighbour convention — is the row to quote**:

| | what it means |
| --- | --- |
| **k = 0** | coupling dropped entirely: every neighbour moves in step. A floor, and the closest thing to a genuinely coupling-free number |
| **k = 1** | each net pays C·V for each of its own toggles, past a neighbour assumed still. The design's energy per period then carries ½C·V²·(n_A + n_B), which is why each coupling capacitor is charged to **both** its nets |
| **k = 2** | every neighbour switches the other way. The worst case |

🛑 **Two SPEF facts that a naive reading gets wrong, both asserted in `caps_*.json`:**

1. OpenRCX writes `*DESIGN_FLOW "NAME_SCOPE LOCAL" "PIN_CAP NONE"`. **There are no pin
   capacitances in the SPEF at all** — no `*L` field on any `*CONN` line (`conn_L_fields: 0`).
   `power.py --spef` prices `½CV²` against the `*D_NET` header, so run that way it would price
   the wire half and silently drop the **26,844 fF** pin half, which is two thirds of this
   design's capacitance. The pin column here comes from OpenSTA's own `net … pin_cap` table, as
   Q126(e)'s `--netcap` path did.
2. OpenRCX writes **each coupling capacitor twice**, once under each of its two nets:
   502,324 two-node `*CAP` entries for the 251,162 capacitors it reports extracting
   (`entries_per_distinct_cap: 2.0`, measured, not assumed). `spef_caps.py` de-duplicates on the
   node pair before summing; without that step the coupling total comes out exactly 2× too
   large. The check `sum(*D_NET) = sum(ground) + sum(coupling written under each net)` holds to
   8 × 10⁻⁸ relative.

## Energy per random fp32 multiply-add

One lane, one TensorFMA32 op (512 micro-ops, 547 cycles), ASAP7 RVT TT liberty, **priced at
0.517 V**, switching only. Same stimulus, same SAIFs, same reader as Q126(e) — **only the
capacitance changed**.

| `mixed` netlist, `randn` | total pJ | wire between cells | pin (in-cell + gates) | clock pJ | clock share | farads priced |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| global-route Steiner, this run | 1.3276 | **0.4675** | 0.8601 | 0.3413 | 25.7% | 51.8% |
| extracted, k = 0 | 1.0247 | 0.1646 | 0.8601 | 0.2725 | 26.6% | 51.7% |
| **extracted, k = 1** | **1.2321** | **0.3719** | 0.8601 | 0.2998 | 24.3% | 51.8% |
| extracted, k = 2 | 1.4394 | 0.5793 | 0.8601 | 0.3271 | 22.7% | 51.9% |
| *the published figure, 2022 OpenROAD* | *1.468* | — | — | — | *32.0%* | *56.3%* |

| `keep` netlist, `randn` | total pJ | wire between cells | pin | clock pJ | clock share | farads priced |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| global-route Steiner, this run | 1.3009 | **0.4238** | 0.8772 | 0.3684 | 28.3% | 43.6% |
| extracted, k = 0 | 1.0276 | 0.1504 | 0.8772 | 0.2930 | 28.5% | 43.6% |
| **extracted, k = 1** | **1.2024** | **0.3252** | 0.8772 | 0.3215 | 26.7% | 43.7% |
| extracted, k = 2 | 1.3772 | 0.5001 | 0.8772 | 0.3500 | 25.4% | 43.7% |
| *the published figure, 2022 OpenROAD* | *1.516* | *0.590* | *0.926* | *0.496* | *32.7%* | *50.5%* |

**The wire-between-cells energy, before and after: 0.4675 → 0.3719 pJ on `mixed` (×0.796) and
0.4238 → 0.3252 pJ on `keep` (×0.768)** at k = 1, with ×0.355 and ×1.18 at k = 0 and k = 2.

Two things in those tables are **tool differences, not routing results**, and they have to be
kept apart from the before/after:

- **this run's own Steiner estimate is lower than the published one** (0.4238 against 0.590 pJ on
  the same `keep` netlist, ×0.718). Current OpenROAD's `repair_design` and CTS build a different
  design from the 2022 build's: 20,656 placed instances against the netlist's 19,822, 20,570
  extracted nets against 20,383. Nothing was done to make them agree, and the published absolute
  is not reproduced;
- **the priced share of the farads got worse, not better**: 43.6% on `keep` against the published
  50.5%, because the current flow creates *more* nets after the point the netlist was simulated.
  Q126(e)'s first caveat — half the capacitance unpriced — stands and is slightly larger here.

So the **ratios** within one run are the transferable result, exactly as POWER.md argued. Every
before/after number on this page is a within-run ratio.

## The clock tree, extracted

| clock nets only, fF | `mixed` | `keep` |
| --- | ---: | ---: |
| pin capacitance (liberty) | 1,443.9 | 1,554.6 |
| wire, Steiner estimate | 733.8 | 815.6 |
| wire, extracted to ground | 282.8 | 313.1 |
| wire, extracted coupling at k = 1 (both sides) | 175.2 | 188.2 |
| **total, Steiner → extracted k = 1** | 2,177.7 → **1,901.9** | 2,370.2 → **2,055.9** |
| the subset that **toggles** at `randn` (POWER.md's **1,846 fF** row) | 1,275.9 → **1,121.0** | 1,377.5 → **1,202.3** |

POWER.md's 1,846 fF is the kept netlist's toggling clock capacitance under the 2022 flow. The
current flow puts it at 1,377.5 fF before routing and **1,202.3 fF extracted at k = 1** — so the
clock tree is *smaller* than the published figure on both counts, and its share of a random
multiply-add falls from 32.7% to 26.7%. The ±20% flip-flop-choice sensitivity the census page
records (`DFFHQx4` forbidden moves sequential area 20%) is larger than this whole move, and
still undecided by any RTL fact.

## The Hamming ladder: does the slope move?

Fitted the way E60's own reducer fits it — OLS over h = 1, 2, 4, 8 with a free intercept, against
the **designed** flip count. fJ per designed flipped bit:

| | `mixed` Steiner | `mixed` k = 1 | `keep` Steiner | `keep` k = 1 | published (2022) | E60 at the board |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lq`, quiet partner A = 1.0 | 34.96 | **33.09** | 28.63 | **27.01** | 34.8 (`mixed`) / 32.9 (`keep`) | **116.7 ± 0.6** |
| `lb`, busy partner A = π | 37.72 | **35.56** | 33.07 | **31.31** | 38.3 (`mixed`) / 38.5 (`keep`) | **129.9 ± 0.5** |

**Detailed routing moves the ladder's slope by 5–6%** — down, on all four ladders. The Miller
factor brackets the k = 1 slope by −16 to −23% at k = 0 and +16 to +23% at k = 2, which is the
honest error bar on this row and is larger than the move itself. On `mixed` the k = 1 slopes land within 5% and 7% of the published ones. So the central
claim Q126(e) rested on the ladder — the arithmetic inside one lane is about 30% of what the
board pays per flipped operand bit on switching alone — survives the extraction unchanged. That
is the one result here that confirms rather than corrects.

## What it does to Q128's waterfall

**(A) the published ledger, with only the between-cell wire re-priced**, by the within-run
extracted ÷ Steiner ratio measured on the same (kept) netlist. The pin half is untouched because
pin capacitance is the liberty's and routing does not change it, so
[the ledger](../2026-10-27-transistor-ledger/)'s transistor-gate and wire-inside-the-cell rows
stand as measured:

| pJ per random fp32 multiply-add | published | k = 0 | **k = 1** | k = 2 |
| --- | ---: | ---: | ---: | ---: |
| transistor gates | 0.306 | 0.306 | 0.306 | 0.306 |
| wire inside the cells | 0.620 | 0.620 | 0.620 | 0.620 |
| **wire between the cells** | **0.590** | 0.209 | **0.453** | 0.696 |
| switching total | 1.516 | 1.135 | **1.379** | 1.622 |
| the cells' own internal energy | 0.431 | 0.431 | 0.431 | 0.431 |
| **bottom-up total** | **1.947** | 1.566 | **1.810** | 2.053 |
| **unaccounted against the board's 5.783** | **3.836** | 4.217 | **3.973** | 3.730 |
| unaccounted against the rail's 4.337 | 2.390 | 2.771 | **2.527** | 2.284 |

🛑 **Closing this blocker widens the gap by 0.137 pJ**, it does not narrow it. 0.137 pJ moves
*out* of "accounted" and back into "unaccounted", and the k = 0 … k = 2 band says the honest
uncertainty on that row is **0.21 – 0.70 pJ**, with 0.45 pJ the figure to quote. Bottom-up
closure against the board goes from 33.7% to **31.3%**.

**(B) the same quantity re-measured end to end on the current tool**, kept netlist, routed. The
pin half's internal split is *not* re-measured here — it is carried at the ledger's own measured
share, 33.0% of the pin energy on transistor gates — because that split needs the DEF × fin-count
join of [`fanout2.py`](../2026-10-27-transistor-ledger/), which this request did not re-run:

| pJ per random multiply-add | Steiner | k = 0 | **k = 1** | k = 2 |
| --- | ---: | ---: | ---: | ---: |
| transistor gates *(scaled, not re-measured)* | 0.290 | 0.290 | 0.290 | 0.290 |
| wire inside the cells *(scaled, not re-measured)* | 0.587 | 0.587 | 0.587 | 0.587 |
| wire between the cells *(measured)* | 0.424 | 0.150 | **0.325** | 0.500 |
| switching total *(measured)* | 1.301 | 1.028 | **1.202** | 1.377 |
| the cells' own internal energy | 0.429 | 0.429 | 0.429 | 0.429 |
| bottom-up total | 1.730 | 1.457 | **1.632** | 1.807 |
| closure against the board | 29.9% | 25.2% | **28.2%** | 31.2% |

Read (A) for what Q128's page should say and (B) for what the whole flow says on a current tool.
They differ by the tool, not by the routing.

### What this changes in Q128 §5 and the Horace Hub's Levels tab

- **"no detailed route / SPEF / coupling"** — **done**, both netlists, 0 DRC violations, coupling
  extracted, and the answer is the opposite sign to the one the entry assumed.
- **"the between-cell wire has no coupling term, so the Steiner estimate is a lower bound"** —
  **wrong and retired.** The estimate is 17–20% *above* the extraction at k = 1. Of Q126(e)'s
  three reasons the bottom-up figure is a floor, this one was never a floor; the other two —
  half the capacitance unpriced, and the ledger covering one lane's arithmetic — are untouched
  and are now carrying the whole claim.
- **"the routed wires"** (Levels tab, Missing) — **done** for the open netlist. 82,358 µm on
  `mixed`, 88,248 µm on `keep`, per-net capacitance committed.
- **the glitch factor** — **unblocked, not measured.** An SDF annotated with the extracted
  parasitics now exists for both netlists (paths and hashes in `versions.txt`). Whether Icarus
  can annotate it is the next step and belongs to the glitch bench, not here.
- **half the capacitance unpriced** — **worse**, 43.6% priced against 50.5%. The way to fix it is
  to re-simulate the *post-route* netlist (`txfma_routed.v`, which has the CTS and
  `repair_design` cells in it) rather than the pre-placement one. That is a bench change, not a
  capacitance change, and it is the single largest remaining item in this part of the chain.

## What ran, and what did not

| Step | State |
| --- | --- |
| Floorplan, pin placement, global placement, `repair_design`, detailed placement | done, both netlists |
| Clock-tree synthesis, propagated clock | done (332 clock nets `mixed`, 350 `keep`) |
| Global route, Steiner parasitics **written as a SPEF** (`estimate_parasitics -spef_file`) | done |
| **Detailed route (TritonRoute)** | **done, 0 violations, 193 s each, `route.drc` empty** |
| **OpenRCX extraction, coupling threshold 0.02 fF, SPEF** | **done, 251,162 / 273,581 coupling caps** |
| SPEF read back; timing, skew and OpenROAD's own `report_power` under it | done |
| **SDF at the TT corner, with the extracted parasitics** | **done, 14.8 MB / 20.9 MB, on aifoundry1** |
| Re-pricing all 13 patterns on both netlists at k = 0, 1, 2 | done, 104 priced runs |
| **Timing closure against the 1250 ps SDC** | **still not met: wns −1,322 ps (`mixed`) / −1,354 ps (`keep`) after extraction** |
| Re-synthesis, re-simulation | **not run on purpose** — Q126(e)'s own netlists and SAIFs, unchanged |
| SDF **annotation** and the glitch ratio | **not attempted here** — the file is handed on |

**Why the port nets route now.** No floorplan change was needed, and the second fix POWER.md
proposed — an I/O ring instead of bare die-edge slots — was not used. The configuration is row 10
of that table exactly (utilisation 30%, pins M4/M5, GRT M2–M7 / clock M4–M7, DRT M2–M9) and the
current router's pin access simply handles the die-edge ports. Both netlists routed, so this is
not the `mixed` netlist's smaller boundary doing the work either.

**End to end, in one tool, not reusing the 2022 placement.** The floorplan, placement, CTS and
global route were all re-run in the current OpenROAD. That is deliberate: a 2022 DEF read into a
current router would mix two tools in one number, and the before/after here has to be measured in
one. The cost is that this run's absolutes do not reproduce the published ones (above). To make
the "before" the right comparator, the whole pre-DRT flow was run a **second** time with
`STOP_AFTER=grt` to dump the Steiner estimate as a SPEF; it reproduced the routing run's
placement **byte for byte** (`txfma_placed.def` md5 `1f8b9d2e6052094760b023e384bfba73` in both),
so the Steiner row and the extracted row describe the same placed design.

**Departures from the plan, dated 27 Oct 2026.**

- The task named the `mixed` netlist. **Both** were routed, because the Q128 ledger's own numbers
  are on `keep` and re-pricing them needs `keep`'s own ratio. `mixed` is still the comparator.
- `docker` on aifoundry1 is not usable by the login (not in the `docker` group), so the container
  ran as root per the lab's root rule, with `--user 1009:1009` so every output file belongs to
  the ordinary account. **Nothing was configured**: no group edit, no package, no daemon change.
  The one persistent effect is the pulled image, and the undo line is
  `docker rmi openroad/orfs:26Q4-229-g64939f371` (1.55 GB in `/var/lib/docker`, which has 111 GB
  free).
- The first routing run died **after** writing the SPEF, on `sta::cmd_corner_name` — an OpenSTA
  accessor that current builds have renamed. The route was not repeated: `post_route.tcl` reads
  the saved routed DEF and the SPEF back and derives the SDF, the net-cap table and the reports
  from them in seconds. `pnr_route.tcl` now tries `sta::cmd_analysis_corner` first.

## Caveats that do not go away

- **0.517 V against a 0.7 V liberty.** Energies are ½CV² at the minion rail because capacitance
  is geometry and very nearly voltage-independent. The **delays**, and therefore the SDF, are
  ASAP7 TT at **0.700 V, 25 °C** (the SDF's own `(VOLTAGE 0.700::0.700)`), and are not
  transferable to 0.517 V. Same caveat as POWER.md's, unchanged.
- **The design still misses its clock.** wns −1,322 ps (`mixed`) and −1,354 ps (`keep`) against
  a 1250 ps period after extraction, so this netlist would run near 400 MHz. The CTS answer being priced is an answer to
  a constraint the design misses by about 2×.
- **ASAP7 is not the process the chip was built in.** Ratios, not absolutes.
- **77 coupling pairs (of 251,162) have one side this script could not resolve to a net** —
  0.03%, almost certainly coupling to a power net, and they are dropped.

## Files

| File | What |
| --- | --- |
| `caps_spef_{mixed,keep}.json` | the extraction's totals: ground, coupling (once and both-sides), pin, the `*D_NET` cross-check, and the entry counts that prove the 2× duplication |
| `caps_gr_{mixed,keep}.json` | the same for the global-route Steiner SPEF (coupling 0 by construction) |
| `net_caps_spef_{mixed,keep}.txt.gz` | **the per-net capacitance table**: `net ground_F coupling_F pinload_F` for all 16,440 / 20,570 nets |
| `net_caps_gr_{mixed,keep}.txt.gz` | the same from the Steiner estimate, for the before/after join |
| `txfma_mixed_coupled.spef.gz` | the `mixed` netlist's full OpenRCX SPEF with coupling, 7.9 MB gzipped (27.5 MB raw). The `keep` SPEF is 31.6 MB raw / 8.5 MB gzipped and was left on aifoundry1; its sha256 is in `versions.txt` |
| `reprice-{mixed,keep}/reprice_<pattern>.json` | 13 patterns × 2 netlists, each priced at Steiner / k = 0 / k = 1 / k = 2, with the wire and pin halves separate and the per-block breakdown |
| `summary.txt`, `summarize.py` | every table above, rebuilt from the JSONs: `python3 -I summarize.py` |
| `route/route_{mixed,keep}.log.gz` | the routing logs, including the DRT iteration-by-iteration violation counts and the per-layer wire length |
| `route/post_{mixed,keep}.log.gz`, `route/route_mixed_gr.log.gz` | the post-route pass and the Steiner-only re-run |
| `route/timing_*.rpt`, `route/skew_*.rpt`, `route/power_default_*.rpt`, `route/drc_bytes.txt` | reports under the extraction; `drc_bytes.txt` records both `route.drc` files as 0 bytes |
| `versions.txt` | the image digest, the binary sha256, the platform file hashes, the netlist and SAIF hashes, and the paths and hashes of the SDFs left on aifoundry1 |

## How to re-run it

```
SQ=$HOME/scratch-q129-route            # netlists in $SQ/in, from synth.sh
bash tools/open-flow/txfma/route_docker.sh -mixed           # route + extract + SPEF (~4 min)
TCL=/flow/post_route.tcl PNROUT=/sq/work/pnr-route-mixed \
  DEF=/sq/work/pnr-route-mixed/txfma_routed.def \
  SPEF=/sq/work/pnr-route-mixed/txfma_coupled.spef \
  bash tools/open-flow/txfma/route_docker.sh -mixed-post    # SDF + net-cap table (seconds)
python3 -I tools/open-flow/txfma/spef_caps.py $SQ/work/pnr-route-mixed/txfma_coupled.spef \
  --table caps_spef_mixed.txt --summary caps_spef_mixed.json \
  --pin-from $SQ/work/pnr-route-mixed/net_cap_spef.txt
python3 -I tools/open-flow/txfma/reprice.py --saif …/randn_o1.saif --saif-base …/randn_o0.saif \
  --muladds 512 --vdd 0.517 --cell-energies asap7-cell-energies.json \
  --caps gr=caps_gr_mixed.txt:0 --caps spef_k1=caps_spef_mixed.txt:1 --out reprice_randn.json
```

`STOP_AFTER=grt` stops before the detailed route and writes the Steiner estimate alone. The flow
and its traps: [`tools/open-flow/txfma/`](../../../../tools/open-flow/txfma/).
