# Heat per millimetre: required corrections

This list combines these sources:
- two independent re-analyses:
  - **[A]** a tail-window reduction (`verify-hpm/indep/`);
  - **[B]** an explicit filter model with Theil–Sen fits (`verify-hpm/methodB/`);
- three skeptics:
  - **[Art]** measurement artifacts;
  - **[Phys]** physics and interpretation;
  - **[Ari]** arithmetic, units and sources;
- my own cross-checks of `wire.json`, `report.json` and the local source texts: **[own]**, `verify-hpm/combine/checks.py`, `newhead.py` and `slowreads.py`.

Nothing was run on the cards.

**Verdict: publish after these corrections.** The measurements reproduce. Every number the page prints follows from `wire.json` with correct unit conversions. Three independent reductions agree with the pipeline to within 1–3% on the mesh-rail numbers and to within about 7% on board power; the board spread comes from the leakage treatment.

What fails is a set of sentences built on the numbers:
- **The 0.9 V comparison with Dally.** An inference is stated as fact, one "brackets" is false, and board power is scaled as if it were die capacitance.
- **The contention wording.** "A third" and "72% at five or six" are wrong, and the two sets are compared over different distance ranges.
- **"A one costs more than a flip".** This is a property of the fit, not an established fact.
- **"Where 40 nm wires were" and "the rest is the routers".**
- **The DRAM ratio and the fadd comparison.** Both mix meters.
- **"Linear" and "one extra hop".** Both are stated more generally than the data allow.
- **The explanation of the 256 B shortfall.**
- **"x and y within 2%".**

## Required corrections, most important first

### 1. Dally's number: its conditions and the 0.9 V comparison (lede, §1, KPI 4, §8 text and chart)

**Claims.**
- Lede: "Scaled to 0.9 V, the voltage behind the lineage of Dally's number, the measured data-dependent cost is 84–159 fJ per bit·mm, so the rule of thumb holds".
- §1: "Neither says at what voltage, in which process, or for what data … The lineage is traceable … 20–40 fJ in a "typical 16 nm"".
- §8: "105–159 fJ for the data-dependent part, which brackets Dally's 100 and Keckler's 121".

**What is wrong.**
- **The lineage is an inference.** SYNTHESIS.md §0, §2d and §4 say: "That is an inference; no source says so."
- **The same 2023 talk puts ~0.5 V beside the figure.** Slide 45 reads "V – Reduce V until it gets too slow (~0.5V)" / "C – Communication (100fJ/b-mm)", and slide 7 reads "~0.5V today". The page never mentions this reading. At ~0.5 V the mesh's data-dependent cost is 26–49 fJ, a quarter to a half of 100, which is in line with Dally's own later 20–40.
- **CACM 2020 does name a process.** "This communication costs 100fJ/bit-mm" is in the paragraph that begins "Accessing a small (8KByte) local memory in 14nm costs 50fJ/bit".
- **VLSI 2018 is misquoted.** The 20–40 sentence says "In present day chips". "Typical 16 nm" comes from another paragraph.
- **§8's "105–159 … brackets Dally's 100" is false**, since 105 > 100. The lede's 84–159 brackets 100 only by pairing the free-link mesh rail with the loaded board figure.
- **Board power should not be V²-scaled for a comparison with die-level wire figures.** It includes the regulator's loss: board watts are 1.2–1.4× mesh-rail watts, and the ratio rises with load.
- **On the mesh rail alone the 0.9 V data part is 84–105 fJ** (free links to loaded). That brackets 100 and is 0.7–0.9 of Keckler's 121.

**Evidence.**
- [Phys], [Ari].
- [own], checked against the local copies of the talks and papers:
  - `wire-research/lit/dally_aha2023.txt`, l.122 and l.712–715;
  - `dally_cacm2020.txt`, l.544–553;
  - `dally_vlsi2018.txt`, l.62–64.
- `report.json` × 3.4435:
  - free-link mesh rail: 83.6 (84.6 with item 2's d = 1–4);
  - loaded mesh rail: 105.3;
  - loaded board: 158.8.

**Replace.**

(a) The lede's last sentence:
```text
Dally states no voltage. Scaled to 0.9 V — the voltage of Keckler 2011's 40 nm wire figure, from which his number most likely descends (an inference; no source says so) — the mesh rail's data-dependent cost is <b id="l-09"></b>, so the rule of thumb holds, to within its own vagueness. Read instead at the "~0.5V" his 2023 talk sets beside it, the figure is two to four times what this mesh spends on the data.
```
In `script.js`, set `l-09` to `${f0(UN.random_bit_data.mean*s09)}–${f0(HN.random_bit_data.mean*s09)} fJ per bit·mm`. It renders "85–105", or "84–105" without item 2.

(b) KPI 4: give `k-09` the same expression. Sub-label: `per random bit·mm, mesh rail, free links to loaded; Dally ~100, Keckler 121`.

(c) §1, from "Neither says…" to "(VLSI Symposium 2018).":
```text
Neither gives a voltage or a data activity. CACM 2020 states it in a paragraph about 14 nm on-chip memory, and the 2023 talk's conclusion slide sets it beside "Reduce V until it gets too slow (~0.5V)" without saying it applies there. A wire's energy goes as CV², so the voltage alone moves the number by 3.4× between 0.9 V and 0.485 V, and "per bit" can mean per bit sent (random data flips half its bits) or per transition. The likeliest lineage — an inference; no source states it — runs through Keckler, Dally and colleagues (IEEE Micro 2011): 310 pJ for 256 random bits over 10 mm at 40 nm and 0.9 V, 121 fJ per bit·mm. Dally's own later numbers are 68 fJ at a projected 10 nm and 0.7 V, and 20–40 fJ/bit-mm "in present day chips" (VLSI Symposium 2018, a paper set in 16 nm).
```

(d) The first two sentences of §8 `comparetext`. These numbers assume item 2, and the template needs `UN` and `UB` added.
```text
At the voltage it runs at, the ET-SoC-1's mesh moves a random bit a millimetre for 25–33 fJ of data-dependent heat and 36–47 fJ in all on free links, and 31–46 and 50–73 fJ on the loaded mesh (mesh rail to board): in all, a third to three quarters of Dally's 100 taken literally. But 0.485 V is low: the same capacitance at 0.9 V would cost 3.44× more, 85–105 fJ per random bit·mm for the mesh rail's data-dependent part (free links to loaded), which brackets Dally's 100 and is 0.7–0.9 of Keckler's 121 (40 nm, 0.9 V). Board power would say up to 159, but it carries the regulator's loss, which is not switched capacitance on the die.
```

(e) §8 chart: drop the row "ET-SoC-1 board power data, scaled to 0.9 V", or relabel it `board power data × 3.44 (includes regulator loss; not a die figure)`.

### 2. Contention: wrong numbers and mismatched distance ranges (lede, §6, model table, §6 chart legend, build_wire_report.py)

**Claims.**
- Lede: "contention costs as much as a third more distance".
- §6: "(none at one hop, up to 72% of link-hops at five or six)"; "At one hop, where neither set shares, the two agree"; "flits held in router buffers and arbitrated rather than passing straight through".
- Free-link board figures: 44 fJ/mm; 107 and 55 fJ per bit per hop.

**What is wrong.**
- **"A third" matches no number on the page.** Loaded over free is 50/36 = 1.39 on the mesh rail and 73/44 = 1.67 on board power. The like-for-like per-hop totals over d = 1–4 give 1.45 and 1.66.
- **The sharing figures are wrong.** From the recorded target maps with XY routing, link sharing is 0/22/32/55/72% at d = 1/2/3/4/6 (78% at d = 6 with YX). The all-pairs set has no d = 5, and within the compared d = 1–4 the maximum is 55%.
- **At d = 1 the two sets do not fully agree on the mesh rail.** The data-dependent parts agree (+1.7%), but the loaded totals are +2.9% (random) and +5.3% (zeros). The pass-to-pass scatter is about 0.5%. The all-pairs one-hop map puts two readers on some targets. Board power agrees within 0–2%.
- **The distance ranges differ.** The free-link headline fits wsep over d = 1–5, but the loaded set is fitted over d = 1–4.
  - `analyze_wire.py` says the comparison is "over the same distances 1-4" and computes `wsep_d1_4`, but `build_wire_report.py` uses `wsep`.
  - On the mesh rail the difference is small: data 90.4 → 91.4, zeros 43.1 → 43.4.
  - On board power it matters: data 107 → 122, zeros 55 → 52, free-link total 43.8 → 46.7 fJ/mm. wsep's readers fall from 31 to 14 shires, and board power per rail watt rises with load, which is what depresses its d = 5 board point.
- **The mechanism is overstated.** Per-reader bandwidth is within 1–6% between the sets at each d = 1–4 (45.7/46.7, 41.4/41.9, 37.3/38.0, 32.8/34.8 GB/s), so flits are not held long. The link-disjoint set also has only straight paths, one reader per target and fewer readers.
- **The board contrast is inflated by about 10%.** Board watts per mesh-rail watt rise with load: 1.22–1.27 at wu d = 1–2 against 1.36–1.37 at d = 4–6.

**Evidence.**
- Sharing: all five analyses agree.
- d = 1: [A], [B], [Art], [own].
- Distance ranges: [Art], [Ari], [Phys], [own] (`combine/newhead.py`).
- Bandwidth: [Art], [Phys], [own].
- Board/rail ratio: [Art].

**Replace.**

(a) In `build_wire_report.py`, use `dj[key]["wsep_d1_4"]` for the uncontended headline and fix the comment "(wsep, d = 1-5)". In `script.js`, change the §6 legend's `dj.wsep` to `dj.wsep_d1_4`.

Expected results:
- mesh rail: 24.6 + 11.7 = 36.2 fJ/mm (91 and 43 fJ per bit per hop);
- board: 32.7 + 14.0 = 46.7 (122 and 52);
- the lede then renders "36 fJ … 25 of it … says 47 fJ", and KPI 2 renders "25 + 12 fJ".

If d = 1–5 is kept instead, state on the page: "free-link board figure 107 fJ per bit per hop over 1–5 hops, 122 over 1–4".

(b) Lede:
```text
On a busy mesh, where flows share links, the same bit costs <b id="l-load"></b>: <b>contention adds about 40% per millimetre on the mesh rail, and 55–65% on board power.</b>
```

(c) §6 `conttext`:
```text
In the all-pairs traffic of sections 4 and 5, flows share links more as the distance grows (none at one hop, 22–32% of link-hops at two and three, 55% at four, 72% at six). The second run added pairs chosen so that no two flows share a link and every scratchpad has one reader. At one hop, where neither set shares a link, the data-dependent parts agree within 2%, and the totals within 3% for random data and 5% for zeros on the mesh rail (the all-pairs one-hop map puts two readers on some targets). Beyond one hop the loaded mesh climbs faster: over the same one to four hops, 119 against 91 fJ per bit per hop for the data-dependent part and 76 against 43 for the rest, on the mesh rail. That is energy the loaded mesh spends beyond carrying the bits, most likely buffer writes and arbitration where flows meet; flits are not held long, since each reader's bandwidth is within 6% of what it gets on free links. It raises the data-independent part proportionally more (+76% against +30%). The link-disjoint set also has only straight paths, one reader per target and fewer readers at long distances (31 shires at one hop, 14 at five), but straight x-only flows that do share links (v1, one to three hops: 122–127 and 72 fJ) cost about as much as the loaded mesh, which points to sharing rather than turns. On board power the contrast is larger (122 against 186, 52 against 103) but noisier (96–146 over passes for the free-link data part), and about 10% of it is the regulator's loss growing with load.
```

### 3. "A one costs more than a flip" is a property of the fit, not an established fact (§5 title, KPI 3, lede, §3, §5)

**Claims.**
- Title: "A one costs more than a flip".
- KPI 3: "a carried 1 costs more than a transition".
- Lede: "A stream of all ones, which never flips, costs as much as random data."
- §5: "the frozen line — half ones, no transitions at all".

**What is wrong.**
- **The coefficients are solid; the ranking is not.** a = 98 and b = 129 fJ per hop on the mesh rail reproduce, but they do not show that a one costs more than a flip.
- **Ordinary logic gives this exact model.** Static logic whose output rests at 0 when no flit is present (a crossbar output with no grant, or data gated by valid) produces a = f·E_t and b = 2(1−f)·E_t, where f is the fraction of flits followed directly by another.
- **Under that reading, b > a is an artifact of the parameterization.**
  - The measured b/a gives f ≈ 0.6 (0.58–0.61 on both meters and both sets) and E_t ≈ 163 fJ per transition per hop. That is about 370 fF/mm, ordinary wire capacitance.
  - Each one is simply two ordinary transitions at the ends of a train, so b > a does not make a one costlier than a flip.
  - An all-ones stream's wires do flip, at the ends of each train.
- **The mechanism is open.** Precharged buffer read lines are the other candidate; dynamic logic is unlikely in a synthesized NetSpeed NoC. The data cannot pick between them.
- **"As much as random" holds per hop, not in total.** All-ones costs 5–9% more per hop than random data. At one hop it costs a third less in total (mesh rail 1.54 against 2.40 pJ/B, board 5.66 against 9.03), because it pays almost no exit step (item 6).

**Evidence.** [Phys] refutes the interpretation; its parity term comes out at −0.4 fJ with the rms unchanged. [own] computed f = 0.603, E_t = 163 fJ and the one-hop totals.

**Replace.**
- §5 title: `5. Ones cost energy, not just flips`.
- KPI 3 label: `Per one-bit vs per flit-to-flit difference, per mm`. Sub-label: `mesh rail, loaded mesh: fitted coefficients, not a physical ranking (§5)`.
- Lede, the two sentences that begin "And what costs is surprising":
```text
And <b>what costs is surprising</b>: not only bits that differ between consecutive flits, but the <em>ones</em> carried. A stream of all ones, which never changes from one flit to the next, costs as much per hop as random data (5–9% more), though at one hop it costs a third less in all.
```
- §3: replace "(so two consecutive flits differ in a bit with probability 2P(1−P), whichever flows interleave)" with `(so two consecutive data flits differ in a bit with probability 2P(1−P): a difference rate between flits, not necessarily the transition rate on the wires)`.
- §5: replace "no transitions at all" with `no differences between flits at all`.
- §5, the sentence `script.js` injects: `On the mesh rail, on the loaded mesh, the fit gives <b>26 fJ per mm</b> per flit-to-flit difference and <b>35</b> per one carried, the same within a few percent on both cards (…).`
- §5 mechanism, from "A cost per one-bit that does not need the bit to change" to "ones are not.":
```text
A cost per one-bit that does not need the bit to differ from the previous flit needs wires or nodes that rest at 0. The simplest case is ordinary logic whose output goes to 0 when no flit is present — a crossbar output with no grant, or data gated by valid. Then each one rises and falls at the ends of a train of flits, and a and b are the same energy per transition, split by how often flits come back to back: the fitted b/a puts that at about 60%, and a transition near 160 fJ per hop (370 fF/mm), ordinary wire capacitance. Precharged structures, such as buffer arrays with precharged read lines, would also do it. Either way it matters for anyone encoding data for this mesh: <b>zeros are cheap to move, ones are not</b>.
```
- Keep "The fit cannot say which circuit it is; …", and add after that clause: `slowing the flows at a fixed distance would.`
- The bus-inversion sentence is item 11.

### 4. §8 interpretation: "where 40 nm wires were" and "the rest is the routers"

**Claims.**
- "In capacitance per millimetre of mesh travel, routers included, this 7 nm chip is where 40 nm wires were; its advantage is almost all V²."
- "A bare 7 nm wire … 12–24 fJ … a third to a half of what the mesh measures: the rest is the routers' flops, buffers and crossbar, and the extra paid for ones."

**What is wrong.**
- **The mesh is not at Keckler's level.** At equal voltage the mesh rail's data part is 0.70 (free links) to 0.87 (loaded) of Keckler's figure, which is 35.1 fJ at 0.485 V.
- **Parity would be expected, not a finding.** Wire capacitance per mm hardly changes between nodes: Keckler 2011 says so, and Dally 2018 writes "about 200fF/mm and independent of scaling".
- **The page's own references disagree by 2×.** Its first-principles wire at 0.9 V is 41–81 fJ (`report.json` `first_principles.at_09`), half of Keckler's 121.
- **"A third to a half" fits only the loaded board number.** The 12–24 fJ bare wire is half to all of the free-link mesh-rail data cost (24.6). With that cost at the top of the bare-wire range, "the rest is the routers" does not follow.

**Evidence.** [Phys], [Ari], [own].

**Replace** both sentences with:
```text
At equal voltage the mesh rail's data-dependent cost per random bit·mm, routers included, is 0.7–0.9 of Keckler's 40 nm repeated-wire figure (35 fJ at 0.485 V). Wire capacitance per mm barely changes between process nodes (Dally 2018: "about 200fF/mm and independent of scaling"), so that is roughly what one would expect, and the mesh's advantage over the 0.9 V literature is mostly V². A plain repeated wire estimated from a predictive 7 nm kit (ASAP7) with Ho's repeater factors would cost 12–24 fJ per random bit·mm at 0.485 V (41–81 at 0.9 V, half of Keckler's figure, which therefore holds more than an ideal wire or counts differently). The free-link mesh-rail data cost, 25, is at the top of that range; these data cannot say how much the routers add.
```

### 5. §9: the DRAM and fadd comparisons mix meters

**Claims.**
- "the farthest on-chip hand-off is still 6–8× cheaper than going to DRAM";
- "each hop adds a third to a half of what reading the byte from the shire's own scratchpad costs";
- "a 32-bit operand crossing one hop costs 6.0–8.7 pJ, about one lane of … fadd.ps (5.3 pJ) … a floating-point add is worth roughly a hop".

**What is wrong.**
- **The reference costs are board power.** The DRAM (122 pJ/B), own-scratchpad (4.21 pJ/B) and fadd.ps (42.2 pJ) figures are leakage-corrected board power from the energy manual. The 8× end, the "a third" end and the 6.0 pJ end of each claim use the mesh rail.
- **The DRAM ratio, board to board:**
  - the ten hops alone are 7.81/1.39 = 5.6× cheaper;
  - the whole hand-off, including the far scratchpad read and leaving the shire, is 4.3× cheaper. The board line for wu at P = ½ gives 6.79 + 10 × 2.18 = 28.6 pJ/B, or 1.83 nJ per line.
- **The fadd comparison, board to board.** One hop for a 32-bit operand is 8.7 pJ, which is 1.65 fadd.ps lanes. An add is therefore worth about 0.6 hop, or 2.3 mm.
- **The ten hops are an extrapolation.** The data stop at d = 6, and on the loaded mesh the per-hop cost rises at d = 4.

**Evidence.** [Ari], [Phys], [Art], [own].

**Replace** from "A 64-byte line carried across the whole die" to the end of the paragraph with:
```text
A 64-byte line carried across the whole die — 10 hops, about 37 mm corner to corner, extrapolated from the 1–6 hops measured — costs 1.0–1.4 nJ in hops alone, against 7.8 nJ to read the same line from DRAM and 0.27 nJ from the shire's own scratchpad (the energy manual, board power). On the same meter the ten hops are 5.6× cheaper than the DRAM read, and the whole hand-off — the far scratchpad read and leaving the shire included, about 1.8 nJ per line — is about 4× cheaper. Each hop adds about half of what reading the byte from the shire's own scratchpad costs (2.17 against 4.21 pJ, board power). In Dally's currency — "an add is worth 10 µm of movement" — a 32-bit operand crossing one hop costs 8.7 pJ of board power (6.0 on the mesh rail alone), about 1.6 lanes of an eight-lane fadd.ps on random data (5.3 pJ, with its share of instruction issue), so on this chip a floating-point add is worth a little over half a hop — about 2 mm — of movement.
```

### 6. §4: "linear", "the same amount with every hop", "about one hop more", "all-ones near random"

**What is wrong.**
- **The d = 4 point sits above the line.** In the loaded sweep, d = 4 lies above the line through d = 1, 2, 3 and 6. v1 behaves the same way.

  | Pattern | Mesh rail | Board power |
  |---|---|---|
  | Random | +5.6% | +4.7% |
  | Zeros | +6.8% | +2.6% |
  | All ones | +14.8% | +12.0% |

  This coincides with shared link-hops rising from 32% to 55%. The link-disjoint set wsep is linear to 1–2%.
- **The exit step depends on meter and pattern.** Measured as line intercept minus the d = 0 value, in hops:
  - board, random: 1.1;
  - mesh rail, random: 0.55–0.7; random minus zeros: 0.7; zeros: 0.3–0.7, depending on the fit range;
  - wsep, mesh rail: about 1.1;
  - all ones: −0.1 to +0.1 on both meters.
- **All ones is not near random at short distance.** It is 36% below random at one hop. On the mesh rail it meets the random line by d = 4; on board power it is still 15% below at d = 6.

**Evidence.** [A], [B], [Art], [Phys], [Ari], [own] (`combine/checks.py`).

**Replace.** Heading: `4. Energy grows nearly linearly with distance`. Paragraph:
```text
On the mesh rail the data-dependent energy is zero at d = 0 (under 2% of its one-hop value: the shire's own scratchpad does not use the mesh) and grows by nearly the same amount with every hop out to 6. On this loaded mesh the step from three to four hops is larger — the four-hop point sits 3–7% above the straight line for random data and zeros, 12–15% for all ones — where the share of link-hops on shared links jumps from 32% to 55%; with link-disjoint flows (section 6) the growth is linear to 2%. Leaving the shire adds a step of its own (the mesh-stop crossings) whose size depends on the data and the meter: about one hop's worth for random data on board power, half to three quarters of a hop on the mesh rail in this sweep (about one with link-disjoint flows), and almost nothing for all-ones data. The lines fan out with the density of ones; the all-ones line (P = 1) starts a third below the random one at one hop and climbs 5–9% faster.
```

### 7. §7: the explanation for the 256-byte shortfall is contradicted

**Claim.** "about 60% do, which is what lines from the other in-flight load and from other flows slipping in between on the same lane would do".

**What is wrong.**
- **The fraction is the same at every distance.** On the mesh rail it is 0.52, 0.48 and 0.53 of the per-distance full-flip prediction at d = 1, 3 and 6, and 0.54 per hop. On board power it is 0.69 per hop. That holds at d = 1, where no link is shared, and at d = 6, where 72% of link-hops are.
- **Other flows would not give a constant fraction.** Their share rises from none to 72% over that range.
- **The other in-flight load is also unlikely.** In v1 its lines are identical to the first load's, so interleaving line by line would halve v1's random-data transition coefficient. Instead v1 and v2 agree: 95 against 98 fJ.
- **"About 60%" depends on the reference.** It is measured against the v1 board model line (0.58). Against the measured 16–128 B level it is 0.69 on board power and 0.54 on the mesh rail.
- **Most of the excess is paid on leaving the shire.** On the mesh rail it is 1.26 pJ/B at one hop, against 0.41 for each further hop.

**Evidence.** [Phys] (`perd_v1.py`), [Ari], [Art], [own].

**Replace** the last sentence of §7 with:
```text
The 256-byte pattern costs less than the model predicts if every bit flipped on every flit (dashed): its extra cost per hop is about two thirds of that on board power and about half on the mesh rail, the same at one hop, where no link is shared, as at six, where 72% are — so it is not other flows slipping in, and the other in-flight load is unlikely too (in v1 its lines are identical to the first load's, yet v1's transition cost equals v2's). Why is open; one possibility is that when all wires flip the same way together, the capacitance between neighbours is not charged. Most of the excess is paid on leaving the shire (1.26 pJ/B at one hop on the mesh rail, 0.41 per further hop).
```

### 8. §10: "x-only and y-only paths cost the same within 2%"

**What is wrong.**
- **The y value rests on one card.** The y value (128) comes from aifoundry3 alone, because all six aifoundry2 y-only 3-hop bursts were dropped.
- **Neither comparison is within 2%.**
  - The pooled difference is 2.4% (124.6 against 127.6).
  - The same-card difference on aifoundry3 is 4.4% (122.2 against 127.6), and 4.1% on board power.
- **aifoundry3's y-only 3-hop point is suspect.** Those bursts had occasional slow meter readings, up to 0.55 s. Their zeros point is high: 2.23 pJ/B, against 2.00 for x. Dropping these bursts gives y = 112, 10% below x.
- **Over one and two hops, y is below x on both cards.** x is 135 and 134, y is 121 and 118: 10–12% lower.
- **The axis sets also differ in load.** They have different reader counts and link sharing: x 56–69%, y 41–76% at d = 2–3.
- **The equal pitches rest on the geometry, not on these energies.**

**Evidence.** [A], [Art], [Phys], [Ari], [own].

**Replace** the first sentence of the "Router against wire" bullet with:
```text
Every hop is one router plus one pitch of link, and the x and y pitches are equal to within 1% on the die plot, so the experiment cannot split a hop's energy between the router's flops and crossbar and the wire itself. (The x-only and y-only sets agree only to about 10% — y is 10–12% below x over one and two hops on both cards, and 4% above over one to three hops on aifoundry3, the only card with a usable three-hop y point — and they differ in link sharing, so they do not test this.)
```

### 9. The board-power coefficients depend on the leakage treatment (§5 table, §6, §10)

**What is wrong.** The bars show the range over passes and cards, not the sensitivity to method.
- **The leakage correction moves the board coefficients.** Without it:
  - v2 board a is about 161 fJ ([A] 162, [B] 162, [Art] 160) against the reported 151;
  - v2 board b is 198–200 against 192;
  - on aifoundry2 alone, a is 171–172 and b 204–209;
  - v1 board a ranges from 137 to 162 across the reductions.
- **The pipeline's leak model over-corrects aifoundry3.** It uses 0.33 W/°C where idle regressions give 0.22–0.24. That changes the coefficients by 1% or less.
- **The mesh-rail coefficients are robust.** They agree within 3% across all three reductions.

**Replace.** Append to the §10 bullet "Board against rail":
```text
Board-power numbers also depend on the leakage correction — without it the board coefficients come out 4–7% higher in v2 (a 161 fJ against 151) and up to 16% for v1's a — and board power per mesh-rail watt rises with load (about 1.22 at light to 1.37 at heavy mesh load), so contrasts between light and heavy traffic are about 10% larger on board power than on the die. The mesh-rail coefficients agree within 3% across three independent reductions.
```

### 10. §10: "The meter can be starved"

**What is wrong.**
- **The ring numbers are wrong.** These data contain no ring bursts between shires s and s+16. The energy manual measured them at a median of 75–146 ms per reading, and the observability report gives "150 ms instead of 22", not 0.8–1.6 s.
- **0.8–1.6 s belongs only to aifoundry2's y-only 3-hop set.** Each burst had 2–3 readings, with medians of 0.80–1.59 s and a maximum of 1.62 s.
- **aifoundry3 also slowed, and its bursts were kept.** On the same traffic it had a normal median of 21–22 ms but occasional readings of 0.23–0.55 s. Those bursts carry item 8's y value.
- **Queue poisoning is not claimed on the page.** "A sampler killed mid-request poisons the queue" appears nowhere on the page and cannot be tested from these data, so no change is needed.

**Evidence.** [Art], [Ari], [Phys], [own] (`combine/slowreads.py`); `manual.json` `reruns.dropped`.

**Replace** the bullet with:
```text
<b>The meter can be starved.</b> On aifoundry2 the set of y-only pairs 3 hops apart slowed the service processor's management path so much (0.8–1.6 s per reading instead of 22 ms) that each burst had two or three readings; those six bursts are dropped. On aifoundry3 the same traffic delayed occasional readings to 0.2–0.55 s; those bursts were kept, and they give the only y-only three-hop point. Rings between shires s and s+16, measured for the energy manual and not part of this run, also starve it: about 150 ms per reading, with the board reading frozen for seconds.
```

### 11. §5: "an all-ones stream would travel almost free"

**What is wrong.**
- **Complementing all ones gives all zeros, which is not free.** All zeros still pays the data-independent part: 74 of 203 fJ per bit per hop on the loaded mesh rail, or 36%.
- **For random data the saving is about 1%.** Per-flit inversion of 512 bits moves the density of ones only from 0.50 to about 0.48.
- **Only software can choose the representation here.** The mesh is fixed hardware.

**Evidence.** [Phys], [own].

**Replace** the bus-inversion sentence with:
```text
Storing or sending ones-dense data complemented would make it cost what its complement costs: all-ones data would then cost what zeros cost, about a third of its present per-hop cost, since the data-independent part remains. For random data a per-flit inversion code would save about 1%. On this chip the mesh is fixed, so only software can choose the representation.
```

## Minor corrections

1. **§3.** "Each burst … bracketed by idle on both sides, corrected for the extra leakage" is true of board power only. Add: `The mesh rail is read over the burst's last 0.6 s against the idle before it, without a leakage correction (about 2%, roughly cancelling a 2.5% under-correction of the meter's 1 s filter).` Sources: [Art], [B].
2. **§2.** After "per mm of mesh travel, one router and one link per 3.72 mm", add: `— per mm of displacement; the metal actually routed can only be longer, so per mm of wire the cost would be lower.` Source: [Phys].
3. **§5.** Replace "to a few hundredths of a pJ/B" with `to 0.01 pJ/B per hop on the mesh rail and 0.04 on board power`. Source: [Ari].
4. **Hop range.** "3.64–3.76 mm" does not follow from the three readings in `pitch.json`, which give 3.637–3.735. Use `3.64–3.74` in `INPUTS.hop_mm.range`, §2, SYNTHESIS.md and the research README. The effect on the per-mm numbers is 0.3% or less. Source: [Ari].
5. **§7, the flit-width sentence.** Replace "if it were 32 or 16 bytes, the 16- and 32-byte patterns would flip…" with `with 32-byte flits the 32-byte pattern would flip on every flit, and with 16-byte flits the 16- and 32-byte patterns would too, on every or every other flit; neither costs more.` Source: [Phys].
6. **§10, "Fixed per-hop cost".** Replace "The data-dependent part is immune to this." with `Even if all of the one-hop zeros energy were cost per second, it would explain at most a quarter of the link-disjoint fixed part and a fifth of the loaded one. The data-dependent part is immune to per-second costs that do not depend on the data (P = ½ and P = 0 run at the same bandwidth); a per-cycle cost of ones held in the mesh would still look per-hop.` Sources: [Art], [Phys].
7. **§10, "Voltage scaling".** Add: `gate capacitance is somewhat lower near threshold, so constant-C scaling slightly understates the 0.9 V figure for full-swing links; low-swing links would make it overstate.` Source: [Phys].
8. **KPI 2 sub-label and model table.** Say that the loaded figures come from the ones/transition model fitted over 1–6 hops. The like-for-like wu d = 1–4 figure used in §6 is 32 + 21 = 53 fJ/mm on the mesh rail. Source: [A].
9. **No page change needed: card-to-card agreement is not an independent check on order effects.** Both cards ran the same shuffled order (seeds 11–13) at the same time, so only the three passes are independent. Per-burst residuals do not depend on the previous burst (|r| ≤ 0.18). Source: [Art].

## Repository and pipeline fixes (not page text)

1. **`research/lit/first-principles-estimate.md` is the wrong file.** It is OpenROAD's "Parasitics estimation" manual (`set_wire_rc`), but `research/README.md` describes it as the estimate. Replace it with the arithmetic of SYNTHESIS §1f, or delete it and point to `lit/wire_calc.py`. Source: [Phys], confirmed by [own].
2. **SYNTHESIS.md carries superseded numbers.** Its §0 and §2 give the E27 values: d = 8, q = 0.445, 35/26 fJ, "101–137 fJ at 0.9 V" and "the capacitance per mm of a repeated wire from 2003–2011". The page cites the file for its sources. Add a first line saying its measured numbers are superseded by the 24 September `wire.json` and `report.json`. Source: [Phys], confirmed by [own].
3. **`analyze_wire.py` mislabels the starved bursts.** It logs the six aifoundry2 bursts as "too few samples" because the sample-count check runs before the `took_ms` check. Check `took_ms` first, or label them "service processor starved". Sources: [B], [Art], [own].
4. **`analyze_wire.py`'s "over the same distances 1-4" comment conflicts with the headline's use of `wsep` (1–5).** Item 2(a) resolves this.
5. **`build_wire_report.py`'s "V^2 scaling of the mesh-rail numbers" comment conflicts with the page,** which also scales board power. Item 1 resolves this.

## Confirmed

- **The d = 0 null.** The mesh-rail data-dependent part is 0.01–0.03 pJ/B at d = 0, against 1.53–1.59 at d = 1: under 2%.
- **The mesh-rail model (C2).**
  - Coefficients: v2 a 97–99 and b 128–131 fJ; v1 95–98 and 129–131.
  - Fit rms: 0.005–0.009 pJ/B/hop on the mesh rail, 0.02–0.04 on board power.
  - Complement tests: 128–133 fJ for ¾ against ¼, and 128–129 for all ones against all zeros.
  - P and 1−P differ, and all ones costs 5–9% more per hop than random.
  - The frozen line sits on the model. Its residual is −0.01, and the wu-only fit predicts 1.097 against 1.089 measured. Its 244/512 ones were checked with a reimplementation of mt19937_64 (seed 1).
  - There is no parity or header term.
  - With the pipeline's leakage model, the board coefficients reproduce exactly (151/192).
- **The ones effect belongs to the mesh.**
  - It is on the mesh rail, grows with hops and is absent at d = 0.
  - Bandwidth is the same for every P at each d.
  - The SRAM rail is flat in d (6 fJ/bit/hop).
  - Prefill ends more than 5 s before each burst and never raises the mesh rail.
- **Contention on the mesh rail (C3).**
  - Data-dependent part: wsep 90.6/90.1 (91–92 by [B]) against wu 119 (119–122). Zeros: 43 (43–46) against 76 (75–77).
  - The gap survives a mesh-rail leakage correction (116–119 against 89).
  - Per-reader bandwidth and the number of readers do not explain it. A global per-time cost would steepen wsep instead.
- **Geometry.**
  - Pitches are 3.73 × 3.70 mm, and √(3.73 × 3.70) = 3.715.
  - The tiles are square within 1%: the pitch ratio is 1.008 in all three copies of the plot.
  - The shire grid spans 86% of the die width.
- **The §8 and KPI arithmetic.**
  - Every per-mm conversion checks, and (0.9/0.485)² = 3.4435.
  - The literature numbers check:
    - Keckler: 310 pJ/(256 b × 10 mm) = 121 fJ;
    - Yale Patt 75: 68 fJ;
    - CACM 2022: ~30;
    - VLSI 2018: 20–40.
  - The AHA 2023 slide 8 and CACM 2020 "100fJ/bit-mm" quotes are verbatim.
  - The first-principles wire is 11.8–23.5 fJ at 0.485 V.
- **Lanes (C6).**
  - Blocks of 16–128 B cost the same: 1.06–1.09 pJ/B/hop on the mesh rail and 1.46–1.54 on board power.
  - 256 B blocks cost +0.76 pJ/B/hop on board power (both cards) and +0.41 on the mesh rail.
  - The lane is chosen by PA[7:6] in the clean-room `shirecache_mesh_master.sv`.
  - `etsoc_shire_other_esr.h` lists 4 to_l3 masters and 4 L3 slaves per shire.
  - Bandwidth and readers are identical for every block size.
- **The §9 arithmetic.**
  - 1.50–2.17 pJ/B per hop;
  - 0.96–1.39 nJ for a line over 10 hops;
  - DRAM 7.81 nJ;
  - one fadd.ps lane 5.27 pJ;
  - a 32-bit operand over one hop 6.0–8.7 pJ;
  - 10 hops is the Manhattan diameter of the minion grid.
- **Starvation.** The aifoundry2 y-only 3-hop starvation is real. Every reduction drops those six bursts; [A]'s stricter rule also drops four aifoundry3 bursts (item 8).
- **Measurement hygiene.**
  - The clock was at 600 MHz (minion) and 400 MHz (NoC) in all 756 burst windows.
  - No heater ran.
  - Every burst lasted 3.21 s.
  - Independent mesh-rail reductions are within 2.5% of the pipeline, uniformly across hops.
  - There is no d-dependent bias from prefill, idle drift or the clock.

Files:
- my checks: `/tmp/claude-1019/-home-yaroslavvb-claude/ed6d06d5-de26-4323-94f1-0dc808eafbda/scratchpad/verify-hpm/combine/checks.py`, `newhead.py` and `slowreads.py`;
- upstream analyses in the same folder: `indep/`, `methodB/`, `artifacts/`, `physics/`, `arith/`.
