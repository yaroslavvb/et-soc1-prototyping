# ET-SoC-1 findings: start here

> **Revised only in part for version 3.** The pages were revised under the version-3 standard on 25 September
> (`0399048`: 57 claims dropped or weakened, one-card results labelled) and carry the three-card check's results
> since 26 September. Here, 02, 03 (E35–E49), 04, 05's "Version 3: the three-card check" and 20-heat-per-mm.md have
> them; the other topic files and the findings in brief were corrected on 25 and 26 September but not rewritten for
> three cards. Where a page and these files differ, the page holds: each claim's outcome is in
> [`results/pagemap.md`](../reports/data/2026-09-25-claims-v3/results/pagemap.md), and the known differences are in
> [`../reports/TODO.md`](../reports/TODO.md), part B.

Everything measured on AI Foundry's ET-SoC-1 cards between 18 and 24 September 2026 (`aifoundry2`; `aifoundry3`
for the 18 September sparsity runs, the cross-card sessions E20–E21, and repeats of E22–E27, E29, E31 and E32), and
in the three-card check of 25–26 September (E35–E48, adding aifoundry1's card 1),
written so that **you never have to open the HTML reports or the raw data to get an answer** — though every
number says where to find both.

The published reports are indexed on the public hub,
[Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#reports);
[04-artifacts.md](04-artifacts.md) maps each one to its sources and its space.

The question the work converged on: **what does a workload's data do to a chip's power and temperature, and
can you predict it before running?** New to the chip's vocabulary (minion, hart, shire, scratchpad, SP, PMIC)?
Read [Terms](#terms) first.

---

## The findings in brief

1. **The effect.** The same matrix multiply — same clock, same instruction count, same 9.18 TFLOPS — draws
   **38 W on matrices of zeros, 47 W on ones and 63 W on random values**. The only thing that differs is the
   numbers in the operands. → [10-data-dependent-power.md](10-data-dependent-power.md)
2. **The explanation.** Simulating the chip's own multiply-add RTL on the operands the card ran gives four
   counts per operation. A zero operand is gated and costs nothing; a constant clocks registers but toggles no
   data; random values toggle 87 million nets. Four fitted energies turn those counts into watts to
   **0.50 W rms** when each pattern is left out of the fit, and 14 structured matrices priced from their tiles
   before they ran came within 0.92 W rms. → [11-thermal-model.md](11-thermal-model.md)
3. **The consequence.** Leakage is 20–29 W (23 W in the best fit) of the 36 W an idle card draws at 80 °C and grows 0.65 W per °C there, which
   closes a feedback loop with gain 0.95. Sustained switching above **about 3 W** has no equilibrium on this
   card in 21 September's room (less on a warmer day): random data drives the die from 80 to 90 °C in
   **20 seconds**, ones in **two minutes**, zeros never. → [12-heat-management.md](12-heat-management.md)
4. **The governor.** The firmware's DVFS loop reads a power *sensor* rather than estimating power from
   activity counters, and its temperature test has no dead band, so from a cool die it hunts across the 65 °C
   threshold, changing clock seven times in 2.4 seconds. The per-minion sleep controls in the open (Erbium) RTL
   are tied off; only clock gating works. (The loop was read in the et-platform source at `353f20e`; the cards'
   own trace strings match an older build.) → [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md)
5. **The comparison.** Against an A100 this chip switches a similar capacitance per cycle, but at a third of
   the V² and about half the clock, and clock-gates everything idle (it stops switching but still leaks). It is
   **not** more efficient per FLOP at dense matmul: 7.0 pJ in fp32 and 3.3 pJ in fp16, against 1.28 for the
   A100 at 16 bits, its format not stated ([R8](01-resources.md)). (Dated note, 2 November 2026: measured on two A100s
   at 400 W, random normal bf16 costs 1.49–1.51 pJ per FLOP of board power at its own clock, in an 8192³ GEMM; E135.) Only against the A100's fp32 CUDA-core datasheet figure is it better: about 2.9× on random data,
   3.4× on the matmul benchmark's ±1/±2 operands.
   → [13-why-low-power.md](13-why-low-power.md)
6. **It transfers to another card.** Re-run on aifoundry3 — different silicon, a launch temperature 25 °C
   lower — the model applied unchanged is off by 1.4 W, and it overestimates every pattern, by 3–10% (8% by least
   squares), not scatter. **One scale factor of 0.92 brings it to 0.2 W rms**, and calibrating that factor on the
   random-normal runs alone predicts the other seven patterns to 0.27 W rms (0.36 in the median over the eight
   patterns, 0.93 at worst, calibrated on zeros). The leakage law extrapolated 7–14 °C below its fitted range lands
   within 0.73 W (the mean of four temperature bins). → [11-thermal-model.md](11-thermal-model.md), "Does it transfer to another card?"
7. **The gotcha if you use these machines.** aifoundry3's firmware reports a TDP of **0 W** (a boot service sets
   it at every boot), which makes the governor's step-up test unreachable and holds the card at 600 MHz for as long
   as it stays at zero. The driver reports the nameplate 65 W on every machine, so nothing on the host notices.
   aifoundry1's two cards work since 25 September 2026, on two more firmware releases; its card 0 overheated under
   load until its fan was replaced on 2 October 2026, and is back in service. aifoundry2's card is back in service
   since 9 October 2026, cooled by a two-fan 92 mm bracket in the slot beside it (idle 51 °C, 23 W); it was out of
   service from 7 to 9 October and from 2 to 6 October, when the cooling at the card fell short and it heated at idle
   until it dropped off the PCIe bus. → [14-card-behaviour.md](14-card-behaviour.md)
8. **The sharpest edge on the chip.** One contended global atomic is shared out fairly, to within half a percent,
   and takes the entire memory path of the shire that hosts it to **zero** — 384 operations, then nothing, for as
   long as the hammering lasts. It takes 21–24 remote requesters (20 leave the host at 98.9%, 24 stop it), under one shire's worth. The vendor's errata
   describe it; they say the configuration bit that looks like the fix does not help when the host and the mesh
   want the same address, and the case measured here (different addresses) was not tested.
   → [17-hot-line.md](17-hot-line.md)
9. **The biggest win available.** A chain of stages that hands its intermediate to the next shire's scratchpad
   (in ID order, 3.5 mesh hops away on average) instead of DRAM runs **12.3× faster at a twelfth of the energy per
   byte** (the three routes draw within about a watt of each other); keeping it in the shire's own scratchpad is 30.7×. The catch is a sharp one: below
   the 32 MB L3 the cache already does the job and you gain nothing. → [18-on-chip-relay.md](18-on-chip-relay.md)
10. **What the bars say.** Re-running every table on three cards (26 September) puts a bar on every entry: ±7% in
   the median for the catalogue (±6% over two cards on 23 September), most of it the difference between the cards
   (in the median entry aifoundry3 is 0.972 of aifoundry2 and aifoundry1's card 1 0.962); ±17% on the hot line, where
   a 1.2 W signal (1.19 W pooled) rides on a drifting 30 W idle; ±13–15% on the relay, mostly aifoundry1's card 1
   reading 17–21% above the other two. Two traps
   found on the way: aifoundry2's governor lifts the clock mid-burst below 68 °C, and rings between shires s and
   s+16 starve the service processor that reads the meter. → [../energy-manual/09-method.md](../energy-manual/09-method.md)
11. **What the meters miss.** Half of idle is on no rail sensor, as is about a sixth of what an arithmetic workload
   adds and 60–75% of what DRAM traffic adds (70% of a DRAM read). Fitted over 392 configuration means per
   card on three cards (26 September), the part above idle is 19%, 18% and 10% delivery loss on the minion rail
   (aifoundry2, aifoundry3, aifoundry1's card 1), 29%, 29% and 20% on the mesh, 73, 73 and 82 pJ per DRAM byte
   off-rail and an SRAM term that differs by card (3–4% on the first two, 54% on the third), to 0.31–0.48 W rms
   (1.0–1.2 W on the DRAM configurations); the idle 12–18 W is not split (`tools/ettelem/fit_unmetered.py` writes the
   fit; the two-card fit of 23 September gave 18–20%, 5%, 26–29% and about 70 pJ/B). And the memory shires' Moortec
   voltage monitor droops
   0.87 mV per off-rail DRAM watt, a DRAM meter that was in every telemetry file all along (traffic with no DRAM
   access moves it too, by up to about 2 mV).
   → [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md)
12. **What a millimetre of mesh costs.** At the mesh's 0.485 V a random bit costs 36 fJ per mm on the mesh rail with
   free links (25 of it data-dependent) and 50 on a loaded mesh; board power says 47 and 73. Ones carried cost
   energy, not just bits that change between flits, and sharing a link adds 40–45% on the mesh rail and 55–65% on
   board power. Scaled to 0.9 V the data part is 85–105 fJ, bracketing Dally's "~100 fJ/b-mm".
   → [20-heat-per-mm.md](20-heat-per-mm.md)
13. **The caveat that matters most.** The temperature half of the model was only held out properly after the
   fact, when the fit was challenged. On the later runs of the same session, which it was not fitted to, the
   time-to-90 °C error is 9% in the median and 23% at worst. In a separate session that afternoon, with new matrices, it is 7% in
   the median but 65% at worst: the DFT pair, whose power the flip model got 2.8 W low. It also runs 3–5 °C hot at
   ten minutes. → [11-thermal-model.md](11-thermal-model.md), section "How well it predicts"
14. **Three cards, pre-registered.** Every claim the pages make was listed and given a verdict (1,372), and those
   that needed new data got a prediction and a decision rule before any run and were re-tested on aifoundry2,
   aifoundry3 and aifoundry1's card 1 (25–26 September, E35–E46). The
   pages now say what the three cards showed, name the card where a result rests on one, and correct the claims whose
   test failed (among them the cycle counter's short window, the rails' reset, aifoundry3's 224 ms service-processor
   pass and the factor between cards). Cycle counts and rates agree across the cards; energies differ by a few
   percent (the full catalogue: aifoundry3 0.976 and aifoundry1's card 1 0.967 of aifoundry2).
   → [03-experiments.md](03-experiments.md), "Version 3 of the claims check"; [05-claims.md](05-claims.md),
   "Version 3: the three-card check"
15. **Gathers and scatters.** On each of the three cards a word gather runs at 452 G elements/s from L1 (12.8 pJ
   each), 27 G/s from L2 or the own scratchpad (about 360 pJ) and 1.2 G/s from DRAM (9.8 nJ, the DRAM's 76 GB/s of
   whole lines); a scatter keeps pace from L1 and falls to 0.42 G/s from DRAM. All 159 verify launches per card were
   exact. On the pages since 27 September: the energy manual (§3.1, §4.3, §4.4, §6), memory hierarchy ("Irregular
   access"), influence functions (S3) and the hub's chart of events. → [03-experiments.md](03-experiments.md), E48
16. **The host link.** Through the runtime, the PCIe Gen4 x8 link moves 12.46–12.60 GB/s from host to card and
   10.41–10.54 GB/s back by DMA alone on each of the three cards (79–80% and 66–67% of its 15.75 GB/s); a program's
   staged copies get 5.20–7.79 GB/s, set by each host's memcpy. An empty kernel costs the card about 104 µs queued,
   but 556–566 µs launched and waited for, most of it the runtime's 500 µs idle poll; two host-to-card DMA commands
   of one stream at once move half as much as one (E55, item 20, found where). → [03-experiments.md](03-experiments.md), E50;
   [05-claims.md](05-claims.md), "The host link"
17. **The governor the cards run, and what it compares** (development, 28 September, and a frozen validation on the
   same card, 28–29 September). The source compares the whole-degree mean of the 34 minion-shire sensors, never the
   hottest one, and the cards' build runs a blocking thermal loop of about 0.405 s steps that acts on an idle card too
   and climbs to 800 MHz in one call. On aifoundry2 every step that fitted a rule fitted the mean: in the development
   night's 12 runs and the validation's 17 the clock held 800 MHz for over a second after the hottest sensor read 67 °C
   or more, and none of the validation's 9 runs that tell the rules apart stepped with the hottest sensor. Placed on the
   perimeter, 192 minions held 800 MHz longer than in the interior in every block: 1.4 and at least 1.8 times in
   development, 1.16–1.52 times in the validation's 4. The validation's verdicts: no dead band (TH3), the Master Minion's
   heartbeat sets the latencies (TH4) and the residency counter adds whole episodes (TH8) survived; "an idle exit is
   followed at once by the idle reset" (TH7) fell, once in 52; the mean against the hottest sensor (TH1), the build (TH2)
   and placement (Q2) are untested: 7 of 9 separating runs fitted the mean where the rule asks for 80%, and 4 blocks of
   the 6 needed, since the card idled at 71–76 °C for most of the 20 hours and its heating sessions could run only in
   an evening cool spell. aifoundry3's
   governor is latched by its zero TDP, aifoundry1's card 1's never raises the clock, and nothing on those three cards
   limits the die's temperature (a 90–103 °C mean on aifoundry2, 26 September). aifoundry2's Master Minion hung in
   development (28 September, 02:50 PDT); the management reset restored it at 08:32, and the validation's three heating
   sessions ran without a hang.
   → [03-experiments.md](03-experiments.md), E51; [14-card-behaviour.md](14-card-behaviour.md)
18. **Where the work sits changed the time to the thermal trip on aifoundry3; on card 1, short bursts PASS and the
   primary sustained test is INSUFFICIENT** (development on aifoundry3, 27 September; frozen validation on
   aifoundry1's card 1, 27–28 September). The same 512 minions on the 16 perimeter shires took 1.62
   [1.51–1.73] times as long as on the 16 interior shires to bring the mean from 61 to 66 °C on aifoundry3, in 9 of 9
   blocks, at equal power; spread over all 32 shires (16 minions each) they took about 1.4 times as long. Half power
   (256 minions) never reached 66 °C there. On card 1 the frozen prediction held in short bursts (one 7 s launch from
   64 °C: 2.04 [1.73–2.42] times as long, 5 of 5 blocks, PLACE-tS PASS) and the primary sustained test was
   INSUFFICIENT (PLACE-t: 7 of its 10 runs, 10 of all 15 Tier L runs, did not reach 66 °C within the 150 s cap; the two
   blocks that decided went the predicted way). By the frozen table no theory survived on card 1 and none was refuted.
   → [03-experiments.md](03-experiments.md), E52; [`reports/data/2026-09-28-heat-placement/`](../reports/data/2026-09-28-heat-placement/README.md)
19. **Heat changed neither the results nor the work per cycle, and the hottest sensor stays close to the mean**
   (E53, 28 September, pre-registered on aifoundry3 and aifoundry1's card 1: 20 of 21 verdicts PASS). The hottest of the
   34 minion-shire sensors ran 1–3 °C above their mean (at most +4), even with the whole load on one shire, so where the
   0.20.0 `mean > 65` rule acts it fires at a hottest sensor of 67–69 °C; every documented hard limit elsewhere (Intel,
   AMD RX 5700, IBM POWER9, Jetson) acts on the hottest sensor or core. 663 exact-checked launches up to an 81 °C mean
   computed nothing wrong, cycles per operation stayed within 0.05% of rest (aifoundry3; card 1 never passed a 76 °C
   mean), the DRAM refresh period did not change, and each card's September idle law still held. On the 0.20.0 and
   0.18.0 builds nothing limits the die once the clock is at 600 MHz. → [03-experiments.md](03-experiments.md), E53;
   [05-claims.md](05-claims.md), "The effect of overheating"; [`reports/data/2026-09-28-overheating/`](../reports/data/2026-09-28-overheating/README.md)
20. **Two DMA commands collide only inside one stream, and a host write lands in the L3** (E55, 28–29 September,
   pre-registered: development on aifoundry1's card 1, validation on aifoundry3 and, as a third card, aifoundry2). Two
   host-to-card commands in flight in one stream move 0.488 [0.486, 0.491] of one at 2 × 64 MB on aifoundry3 (0.496 on
   aifoundry2, 0.493 on card 1), a rate ratio of 0.484 over 1–64 MB; one command in each of two streams moves 1.012
   [1.000, 1.025] of one (1.014 on aifoundry2). T35-S survived; a shared read engine, the IOMMU, a fixed cost per
   overlap, a slow onset and a loss per element were refuted on all three cards. After a staged host copy 99.5% of a
   4 MB buffer's lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on card 1), whether the L3 held them
   before or not, and no value read was wrong: a host write goes through its line's L3 home, which allocates it (T34-A). → [03-experiments.md](03-experiments.md), E55; [`reports/data/2026-09-29-pcie2/`](../reports/data/2026-09-29-pcie2/README.md)
21. **Read replies cross the mesh y first, write requests x first** (E56, the same cards and plan). Sets of 1 KB
   tensor-load streams that share one directed link only under y first fell to 0.54–0.77 of their bandwidth alone and
   those that share one only under x first held at 1.00; tensor stores showed the mirror (0.52–0.76 against 0.99–1.00),
   the same on all three cards to 0.003. A reply retraces its request's route, and a shared link saturates near
   92 GB/s. An ESR call costs 1,556.9 + 35.9 cycles per mesh hop on aifoundry3 and 1,556.8 + 35.9 on aifoundry2, with
   rms errors of 4.7 and 4.5 cycles against the frozen limit of 4, so the placements were not decided on either; on
   card 1 the master shire placed at (0,3), the firmware map's cell.
   → [03-experiments.md](03-experiments.md), E56; [`reports/data/2026-09-29-nocr/`](../reports/data/2026-09-29-nocr/README.md)
22. **The DRAM map mostly holds, the L2 keeps TensorLoad lines, and the 128 B cap is unexplained** (E57, the same
   cards and plan). The L50 map's bank and row split held in 15 of 15 conditions on aifoundry3 and card 1 (a row that
   also differs in any of PA[6–12] reads as a row hit, 20 cycles faster) and in 14 of 15 on aifoundry2, where two lines
   that differ only in PA[17], a column bit in the map, read as a row conflict; PA[6–9] set the refresh phase on
   aifoundry3 and aifoundry2, so the refresh domain is the controller there (not established on card 1). A second
   TensorLoad of the same 1 KB takes 199 cycles, an L2 hit, on all three cards. No registered theory of the shire's
   128 B per cycle TensorLoad cap survives. Stride-256 scratchpad loads get 0.665 of stride 64's bandwidth and, on
   aifoundry3, cost +41.9 (zeros) and +49.9 (random) pJ per 64 B more, which the waiting minions' awake time explains;
   on aifoundry2 the excess was not resolved (+31 to +36, intervals that include 0). → [03-experiments.md](03-experiments.md), E57; [`reports/data/2026-09-29-memp2/`](../reports/data/2026-09-29-memp2/README.md)
23. **The rails are a first-order average of about one second, published one SP pass late** (E58, the same cards and
   plan). On aifoundry3 τ is 1.06 s on the minion rail, 1.01 s on SRAM and 1.04 s on the mesh rail, and the PMIC's board
   average 1.05 s with no lag; aifoundry1's card 1's SRAM rail averages over 0.54 s, its other rails 1.08 s. E27's
   1.15–1.22 s had folded the pass into τ. The published rails understate a 2 s burst by 19–22% (all but card 1's SRAM
   rail) and the board average by 16–17%; undone with each card's τ (`tools/ettelem/deconv.py`), the bursts' energy
   comes back within 0.3% of the step and their plateau within 1.1% on aifoundry3. → [03-experiments.md](03-experiments.md),
   E58; [`reports/data/2026-09-29-tau-aifoundry3/`](../reports/data/2026-09-29-tau-aifoundry3/README.md)
24. **A sparse parity solver on the card's 1,024 minions is 1.1–1.6× six tuned CPU threads** (E59, 29 September,
   aifoundry3; an engineering benchmark, not pre-registered). Noisy sparse parity, as an int8 tensor GEMM checked by
   two closed-form checksums: L1 (512, 4, 0.3, 448) in 0.131 s, L2 (512, 4, 0.4, 1,850) in 0.323 s, (256, 5, 0.4,
   1,925) in 1.52 s; 7.8–12× one core. Board energy per solve with the idle, measured on the one-stage scan: 5.0, 16.6
   and 89 J; the board alone, 2.5–7.7× below the CPU's assumed package energy at 125–251 W (1.6–6.1× with the host
   that drives the card). → [03-experiments.md](03-experiments.md), E59;
   [`workloads/sparseparity/`](../../workloads/sparseparity/README.md)

25. **Every bit position of an fp32 operand has its own price, and the mantissa is two regimes** (E65,
   26 October, pre-registered, aifoundry3). Flipping one B bit against a constant partner costs **83 fJ at bit 6
   and 1,008 fJ at bit 22, a 12.2× span**: bits 0–9 sit flat at 83–136 fJ, then the price climbs to the top of the
   mantissa, while the exponent averages 174 fJ and the sign bit 123 — so the registered guess that the exponent
   would be dearest fails both halves. The case the chip diagram models — b bit 11 against a = π — is **745 ± 56 fJ
   at the board**, about four times the gate-level multiplier price, and a busy partner costs 1.6–4.7× a quiet one.
   An idle-bracketed hart ladder reads **−0.51 ± 0.03 W + 27.1 mW per hart** on random data and **+0.013 ± 0.016 W
   + 2.08 mW per hart** on zeros: E62's 5.80 W fixed cost scales to 3.12 W here and **is not there** — its slope
   lands and its offset was E62's own baseline. → [03-experiments.md](03-experiments.md), E65;
   [05-claims.md](05-claims.md); [`reports/data/2026-10-26-e65-bit-prices-hart-ladder/`](../reports/data/2026-10-26-e65-bit-prices-hart-ladder/README.md)
26. **The toggle count under the flip model is a count of names under one Verilator, not of wires** (26 October,
   simulated, no card). The bench's **21,331 toggles per random fp32 multiply-add** re-runs as 21,379 on the lab
   host's Verilator 5.042 and **7,014** under 5.052 on the same tiles; one traced run carries both counters at once
   and its coverage says 21,297 where its own waveform holds 7,233 — 2.94× apart inside a single simulation, and
   only in two modules. Merging each name with its ancestor scope gives **1,301 physical nets**, a floor, so the
   number under every fitted femtojoule is **8–16× too large**. Independently, the same RTL synthesised and placed
   on an open 7 nm flow gives **3,299** physical nets and **38.5 fJ per flipped operand bit** against the card's
   measured 129.9 — about 30% of the board price on switching alone. Refitting the watts on the smaller counts
   costs accuracy (leave-one-out 0.46 → 0.70 W) and moves the model's standing over-prediction barely at all
   (0.832 → 0.854 of measured, 25 of 26 residuals still one sign), so the missing term is not a counting
   artefact. → [05-claims.md](05-claims.md); [`reports/data/2026-10-26-toggle-recount/`](../reports/data/2026-10-26-toggle-recount/README.md),
   [`2026-10-26-open-netlist/`](../reports/data/2026-10-26-open-netlist/README.md),
   [`2026-10-26-load-model/`](../reports/data/2026-10-26-load-model/README.md)

27. **Four fifths of a random multiply-add's energy is now accounted for bottom up, and the biggest row added
   over-prices** (Q129, 27–28 October, seven card experiments on aifoundry2 and aifoundry3 plus desk work). Routing
   the open netlist, pricing the farads the ledger had left out, measuring the glitch factor and counting one lane's
   transport takes the bottom-up total from **1.946 pJ to 3.966–4.190 pJ** and the remainder from **3.837 pJ to
   0.718–0.941 pJ** against the board's 5.783 pJ in the resident loop; the minion rail is now **measured at 4.774 pJ** [4.549–4.951]
   rather than scaled. 🛑 **Two closures against the board are published and a summary must say which it means:**
   the bottom-up rows alone are **68.6–72.4%** (against 33.7% on 27 October, the comparison that is like for like),
   and **83.7–87.6%** once the measured board-to-rail step's regulator row is counted — which is a named account,
   not a bottom-up term. 🛑 And the closure's upper half rests on a register-file **model** the card's own
   measurement contradicts: one lane's transport model costs 0.654 pJ per multiply-add in the zeros stimulus where
   the **whole board** costs 0.27 pJ over idle, so a true accounting sits **below** the bottom of every range here.
   Three things also stopped being inferences: the governor's cap and threshold were **moved** (the sustained clamp
   is the thermal threshold — 763.4 MHz with 11 thermal steps at 65 °C against 800.0 and none at 70 °C), the price
   list's 2× over-count of a random word is **shared wires, not interaction** (+3.860 ± 0.052 W between two layouts
   at the same Hamming weight), and the thirteen trapping instructions have **no energy at all**, because each ends
   its hart's kernel. → [03-experiments.md](03-experiments.md), E69–E76; [05-claims.md](05-claims.md), "Q129";
   [14-card-behaviour.md](14-card-behaviour.md), "The governor's two knobs";
   [`reports/data/2026-10-28-q129-waterfall/`](../reports/data/2026-10-28-q129-waterfall/README.md)

28. **The kind of number sets a matmul's power and heat at a fixed clock, and its speed only through the governor**
   (Q130, 31 October: fourteen card experiments on all four cards, plus desk work). All 51
   kinds of numbers in three formats — zeros, constants, random at three scales, sparse by element and by word, small
   integers, truncated mantissas, powers of two, sign patterns, sorted streams, weight-like distributions — were
   measured at a pinned 600 MHz: random data costs **5.816 / 2.625 / 0.306 pJ per multiply-add over idle** in fp32 /
   fp16 / int8 in the resident loop (a matmul that streams costs more, E101 below), every kind runs at the same cycles per op, and a second card ranks the kinds the same way (Spearman
   0.995–1.000) at about one card scale. One operand all zero costs 2.5–3.5% of random in the floats, a constant about
   a third, a bf16-truncated mantissa 73%, and magnitude nothing; and because the zero gate tests a whole 32-bit word,
   **a zero is worth most in fp32 and least in int8** (half the elements zero: 0.30× / 0.60× / 0.77× of random power).
   Under aifoundry2's own governor the same kinds set the speed through their power: on a cool die only the power test
   acts (random fp32 712 MHz against 800 for sparse or small-integer data), in sustained work only the thermal test
   (random 604 against sparse90's 800 MHz), int8 barely throttles, and one power-to-clock relation gives 33 kinds'
   clocks from their measured power to 7.5–7.9 MHz rms (8.4–10.6 MHz over the kinds whose clock is free to move, post
   hoc). The afternoon and evening rounds added: on aifoundry1's card 0 fp32 random data trips the PMIC's 75 W
   over-power alarm, so zeros run 1.67× faster sustained there (E84); in three windows of GPT-2 small, real fp32 and
   fp16 tensors cost 97–99.6% of random data's switching over each format's zeros and run at its speed, while real int8
   saves 11–22% (2–4% of the whole board) (E86, E87); a random positive fp32 multiply-add splits 37 / 40 / 23% into the
   clocked lane, the multiplier and the result path (E88); low-power kinds heat the die per board watt within 4–11% of
   random fp32 (E89); and a random sign costs about 5 W, 8–16× what its sign bits cost (E90). 🛑 Both frozen
   explanation models failed parts of their scoring and are reported as failing; the whole-degree die reading resolves
   heat only above about 12 W of switching (E89 read seven of the 32 low-power kinds on the sensors' raw codes); and the
   RTL toggle counts are provisional, because neither bench computes a·b+c on a multiply-add. **Q132 (1 November)
   narrowed most of what that left open.** Every per-kind number above is the resident loop's: in the matmul benchmark
   random fp32 costs 7.69 pJ per multiply-add and int8 slows ×1.17 and ×1.32, and in one port of the vendor's GEMM pattern, whose packed
   tiles miss the L2 on most lines, fp32's clocks part ×1.06 and ×1.27 but the rate ×1.03 and ×1.09 (E101); pack B by column in a repeated block and the fixed term goes, the rate follows the clock and the gap comes back, ×1.24 in an fp32 burst and ×1.32 sustained in fp16, while a walk over fresh blocks buys ×1.06 of rate for ×1.33 of clock; nothing places a large GEMM (E105). With sums read back as held, alternating between adding and subtracting costs fp32 4.4 W on one card, a steady subtract nothing measurable, and fp16's sums walk (E92, E104); of a random sign's ~5 W, tiles that hold keep 0.19–0.45 in fp16 and about 0.35–0.56 in fp32, a bracket, not a number (E106). The zero gate compares raw bits, at
   power resolution on one card (E93). Real tiles sit on their live share in fp32 and fp16, "within 2% of random" fails as a
   rule, and int8's bits and gate are not separated (E95, E96). All 32 low-power kinds now rest on the fine reading on one
   card, and a hold settles at about 0.9 °C per board W, not a steady state (E97). The idle reset is a once-a-second check
   reading idle between two kernels, tested from outside on one card and one kind (E100). And the RTL bench's fault was
   Verilator's optimiser, fixed by `-fno-dfg`; its model reads this kernel to 0.10–0.39 W rms per format and set, not the chip
   (Q132(b), E103). **Q133 (1 November) took the Esperanto side of what Q132 left.** Reuse is the variable for a walk over fresh
   blocks, and with the walk's operands inside the L3, DRAM sets about two thirds of its extra time over a warm block in fp32
   and fp16 (E107; a large GEMM is still not placed). In fp32 most of a random sign's rest goes with the accumulators holding
   different values (E108). int8 zeros' extra 0.61 W is not per-op work and not the lanes: with nothing issued, int8's loop
   costs 1.7 W more than fp32's (E109, labelled, not scored). The DRAM read path pays for raw bit flips at 64 and 256 bits
   only (E110). aifoundry2's die settles at about 0.67 °C per board watt, though not steady by the registered test (E111).
   E91's GPT-2 tiles and E88's split repeat on second cards (E112, E116); card 0's fp16 and int8 sustained cells were
   re-run on the same card, three runs each (E114: fp16 ×1.23; int8's 1% is the clock); and the bit price follows the
   voltage on card 0 too (E118, a governor move). The A side's form (E113), int8 at gate level
   (Q133(a)) and the power model's blind pool (Q133(b), E115: 0.29 W rms over 16 float tiles, a marginal fail) narrow the
   rest. **Q134 (the evening of 1 November) confirmed what it could while the cards were free.** Under aifoundry2's own
   governor a third more clock buys ×1.32 in a reused block and ×1.065 cold, by E107's reuse law at both clocks, and ×1.13 in
   the walk the L3 serves, in every format (E119). E93's zero gate (E121) and E108's fp32 location of a sign's rest (E122)
   hold on aifoundry3; E113's A side holds on aifoundry1's card 1, where a few low A bits cost nearly what B pays (E125); and
   E109's int8-zeros test scores there: the extra is per-time, the lanes oppose it, and it is not per-op work at its
   reading's price (E124). Every † row of the kinds table now has a measured spread (E123). aifoundry2's service processor
   has not entered POWER_SAFE since 26 October, read from its own counter with card 0's alarm as an exact control (Q134(a)).
   E77 left the regulators' share of the 0.875 pJ row unbounded, and its redesign bounds it at 0.69 pJ, loosely (E120).
   **Q136 (2 November) ran under the owner's three rules of that morning**: no power cycle and nothing that risks one,
   read-only PMIC voltage reads allowed, and every command classified READ or WRITE from the firmware source before the
   first launch; none of its nine card runs sent a WRITE. A third more clock buys ×1.13 in E107's `c4s`, ×1.067 in `c8` and
   ×1.052 in `c16s`, so all ten arms are measured, and a governed sustained gap did not replicate between two sessions while
   what the clock buys did (E126). The float B-lane gate's miss is the gate's own, mostly each lane's gate flipping (E127).
   fp16's sign rest goes with the accumulators differing on E108's design, and the moving-sum ratio holds 1.55× pooled over
   ten passes (E128; the inverse-variance arm, 1.710 ± 0.024, leaves it open). One A row cuts int8 zeros' no-issue excess
   from 1.57 to 0.87 W, and per-op work is below half the gap (R1p, registered after E124's passes were known; E129; the
   bench leaves TenC's read port and the TIMA controls, Q136(c)). The int8 multiplier does not Booth-recode A, against
   frozen netlist predictions (E130, Q136(a)). E95's real tiles carry to a second card verdict for verdict (E131). A memory
   channel pays +0.31 W for changes between its lines, off every metered rail (E132). aifoundry2's heat coefficient
   replicates at 0.65–0.70 °C per board W (E133: by R1 for fp32 random, inconclusive for int8 −1s). An A bit's price
   depends on its base word (E134). At the desk the off-rail row stands at 0.75–1.05 pJ (Q136(b)), and the write audit
   classifies all 92 management commands from source, with a checker every runner calls (Q136(w)). **E135 (2 November)
   measured a GPU the same way.** On two A100s rented on Modal, at their 400 W limit, Horace He's kinds in bf16 at 8192³
   show the ET-SoC-1's burst mechanism: random data sits on the power cap at 1267–1277 MHz while zeros run the full 1410
   MHz, so zeros run ×1.108 faster sustained and ×1.097 in a 3 s burst, and the speed follows the clock to 0.34%; the
   lower cap could not be set there, and his own loop reads a smaller gap (R10 fails). **Q137 (2 November) set prediction
   as the goal**, the owner's words: to predict the power and heat of numeric work as accurately as possible. A real
   4,096³ fp32 GEMM (192 MB with C) ran on aifoundry2 at 3.86 TFLOPS with no zeros-against-random speed gap, its burst
   power predicted to 3.4 W rms and its die to 0.8 °C, its time per op 7–13% slow (E136). fp16's sign rest goes with the
   accumulators differing on the matched design too, and almost none with the sums changing (E137). int8's B bits fit
   neither netlist group on the rail and need a price per position (E138). The memory path's encoded part pays, about
   0.46 pJ an encoded toggle, and moves the DDR die rail (E139). The model M6, frozen with a heat term and tested on 25
   tiles nobody fitted (Q137(m), E140), predicts the die's rise to about 0.2 °C, and power to about 0.4 W rms, biased high,
   with too few tiles inside its intervals (19 of 25) and no better than M5. **Q138 (the evening of 2 November) set out to settle
   the power model's open questions.** M7, refitted on every public kinds row and frozen first, met a fifth blind pool, 30 new
   kinds and 6 anchors, on three cards: the die's rise over a 4.5 s run is predicted to 0.13 °C rms on aifoundry3 and 0.14–0.17 °C
   on aifoundry1's card 1, and power to 0.15–0.36 W rms by card and format, its error bars holding by being wider rather than its
   errors smaller, with no gain over M6 shown on card 1 (E141, E142); under aifoundry2's governor it predicts a burst's clock to
   about 7 MHz where the governor acts (E143). Heat over minutes was predicted blind to 0.04–0.18 °C rms on aifoundry3 and
   0.37–0.76 °C under aifoundry2's governor (Q138(t), E144, E144b). A large GEMM's C stores cost no time where C stays in the L3,
   and its die held to about 1 °C rms in bursts but ran 3.6–4.6 °C over the frozen law, sustained, on a shape never run (E146);
   int8's B side on a second card matches the first, its structural verdict still open (E145); every open single-bit position is
   priced (E147); and on an A100 and an A10G under their caps power follows the operand bits as on the ET-SoC-1, in kind, the
   model's pairing excepted (E149, E150). **Q139 (3 November) worked down Q138's final critic's list.** Every 600 MHz row was put
   on one reduction footing first (Q139(u)), and M8, refitted on it and frozen, met a sixth blind pool of 50 tiles, 44 of them new
   kinds and 12 cut from two public models, on three cards, with every launch's result checked bit for bit (Q139(k)): a new kind's
   power is predicted to 0.10–0.39 W rms by card and format, unbiased on the floats but no better than M7 or M6, and the die's
   rise over a 4.5 s run to 0.10–0.18 °C (E153, E157); under aifoundry2's governor its bands hold at the last pool's size (E160).
   Heat over ten minutes was predicted from the bits alone to 0.37 °C rms on aifoundry3 and within about 1 °C on governed
   aifoundry2, one session each (Q139(e), E154, E161). A governed large GEMM's sustained clock, board and die came within 8.7 MHz,
   1.9 W and 1.0 °C blind, the clock about five times closer than the old law, though every per-hold rule failed (Q139(q), E159),
   and past 32 MB the L3 keeps about half of a returning B panel (E158). int8's B side is Booth-recoded (E151); the float gate's
   cost is one constant per flip within about ±10% (E152); int8's floor by shape follows address-bit toggles (E155); the memory
   path's encoded term carries to a second card (E156); and on an A100 what costs is A's rows one apart, not neighbours along K
   (E162). A card nobody has measured still needs a measured reference (E153, E157). *Corrected by Q140(c) (Wed 4 Nov 2026,
   post hoc): the 4.5 s figure is a skill on the floats, int8's rises being whole-degree readings; and the two cards' heat
   over ten minutes is not like for like: aifoundry3's chain ran on the session's realized dispatch records, its 0.37 °C
   with a 95% interval on the sigma of 0.22–1.06 °C, while aifoundry2's −0.90 °C assumed continuous work (−0.39 °C at the
   kernel duty).* **Q140 (the night of 4 November) froze Q139's final critic's list for the cards, at the desk only;**
   no card ran. The critic's four desk checks were re-derived (Q140(c)): the board's exponent n = 2.28 doubles the
   governed clock's error on the session run after it was committed, so it fits a session offset. On aifoundry2 three
   session terms, the die at a burst's start, the session's zeros level and the cap's plateau, carry leave one session
   out (Q140(l)): held out the governed clock goes 6.25 → 5.00 MHz and the boards 1.62 → 0.89 W and 1.52 → 0.75 W rms,
   the terms chosen on the same folds (with the choice nested, 5.1–6.9 MHz and 0.88–0.93 W). M9's 600 MHz part, frozen
   first, counts int8's radix-4 Booth partial products and takes int8's out-of-kind error from 0.25–0.26 W to 0.18 W,
   while no float term helps (Q140(m)); post hoc, the bench's three-point launch average over-counts a high single
   bit by up to about 1 W. A seventh blind pool, 61 tiles by an independent designer (Q140(b)), is committed with M9's,
   M8's, M7's and M6's predictions on three cards and rank 4's paired-anchor rule (Q140(x)). The heat replicates are
   frozen on one duty convention (Q140(e)); G4, a governed large GEMM's sustained path, keeps the zeros level and the
   governor's process-boundary dip and rejects a start-die term, its held-out board 1.89 → 1.33 W (about 1.47 W with
   the choice nested) *(dated, Wed 4 Nov 2026, after Q140(r)'s verifier: with the selection nested and the span fraction
   applied as frozen; 1.42 W with the selection nested alone)*, while a block-stride term from the L3's public set mapping
   fails (Q140(q)). Every figure is out
   of kind, held out or post hoc: the card half (E163–E169) scores them blind and waits on the owner's word. **Q141 (4 November, by day) wrote and verified the card half at the desk:** every run's registration, scorer and kit, E163–E169, committed before any data (Q141(a)–(t)); its critic found all seven ready, the last release about 3.5–4 h after the owner's go (Q141(f), [the readiness report](../reports/data/2026-11-04-q141f-readiness/README.md)), and a bounded runbook holds the box steps (Q141(k)). After his go the card half started at 14:11 PST; its results follow. *(Dated, Wed 4 Nov 2026, the card half's records, Q141(i): it ran to 17:18 PST, E163–E170 on four cards. M9, blind on pool 7, reads new kinds with the lowest rms of the four models on both 600 MHz cards (0.278 and 0.273 W over 48) and on card 0's governed bursts (0.727 W), but rank 1's rule fails on both 600 MHz cards, the floats carrying a session-wide excess; rank 2 fails on resolution only, rank 3 is not answered and rank 4 passes; G4 holds a large GEMM's board and die and misses one shape's clock; a power-of-two stride steps 0.81–0.88 of the L3 set map's step. → [05-claims.md](05-claims.md), "Q141, the card half".)* *(Dated, Wed 4 Nov 2026, Q142's records: M10, M9's forms refitted on 959 rows with each session's own random anchors setting a float scale and the single high bits counted at 9–243 launch points, reads the floats to 0.185 W rms held out, not blind, and pool 7's 48 kinds to 0.205 and 0.187 W, where M9 read 0.278 and 0.273 W blind; heat over minutes keeps Q138(t)'s chain unscaled, its gain a reported arm, and post hoc its misses are a session level or a gain, not separated; a safer runbook, v3.1, waits for the next card day (Q142(m), Q142(s)). → [05-claims.md](05-claims.md), "Q142".)* *(Dated, Thu 5 Nov 2026, Q142's pool-8 records and Q142(v2) and Q142(h)'s: blind pool 8, drawn by an independent designer, has M9's and M10's predictions on four cards frozen before any claim, with M10 carried to aifoundry2 and card 0 by a rule registered first; its card day, E171–E174, is registered and kitted, its code read and fixed at the desk (the v3 drivers), and waits on the owner's word; M11's heat registration, heat over minutes as a session level against a gain on two aifoundry3 sessions, is registered, design only. Nothing of pool 8 is measured. → [05-claims.md](05-claims.md), "Q142, pool 8" and "Q142(v2) and Q142(h)".)* *(Dated, Thu 5 Nov 2026, Q143(r)'s records: pool 8's card day ran on the owner's go. M10 reads new kinds blind to 0.180 and 0.185 W rms at 600 MHz on aifoundry3 and card 1 (M9 0.245 and 0.266 W), its lead over M9 and its float scale holding on the registered footing only; in governed bursts aifoundry2's pinned board reads 1.094 W and card 0's board 0.689 W. aifoundry2's governed clock is blind at 4.49 MHz rms, its held-out level, above rank 2's 4.0 MHz line (E175); M11's first heat-over-minutes session was refused at its start gate, nothing scored (E176); card 1's session heat scale reads BETTER and its paired int8 term NOT RESOLVED, reported only. → [05-claims.md](05-claims.md), "Q142(h2) and Q142(a2)", "Q142, pool 8's card day" and "Q143".)* *(Dated, Fri 6 Nov 2026, Q148(r)'s records: no card ran. The one-number matrices are registered and kitted, not run: int8 5s against 4s on the TensorFMA is forecast at +0.186 W, the floats below resolution (E178), and on the vector unit 5 + 5 against 4 + 4 at +0.165 W, one more 1-bit in the result, with a 21-number ladder (E180); adding is not null. Post hoc, the anatomy of one fp32 TensorFMA step on aifoundry3 is 47.67 nJ, 11.64 pJ a MAC, its minion rail's data-dependent switching 36.9% of the board and the only line that resolves a one-number pair; the split inside the logic waits for october-forecast-model. One leakage law per card is registered; the governor's dips are a counted, registered term, post hoc better on two sessions and worse on E175; a per-position single-bit term does not enter; M10's lead over M9 survives one footing (post hoc). M11's second session (E181) is READY. → [05-claims.md](05-claims.md), "Q145, Q146 and Q147".)* →
   [03-experiments.md](03-experiments.md), E78–E181; [05-claims.md](05-claims.md), "Q130", "Q130 additions", "Q132",
   "Q133", "Q134", "Q136", "E135", "Q137", "Q138", "Q139", "Q140" and "Q141" (with "Q141, the card half"), then "Q142", "Q142, pool 8" and "Q142(v2) and Q142(h)", then "Q142(h2) and Q142(a2)", "Q142, pool 8's card day" and "Q143", then "Q145, Q146 and Q147";
   [`reports/data/2026-10-31-e78-kinds-energy-matrix/`](../reports/data/2026-10-31-e78-kinds-energy-matrix/README.md),
   [`2026-10-31-e80-kinds-speed/`](../reports/data/2026-10-31-e80-kinds-speed/README.md)

## Terms

The chip in brief. The ET-SoC-1 is Esperanto's RISC-V accelerator, now open-sourced by AI Foundry. Its compute
cores are **minions**: small in-order RISC-V cores, each with two hardware threads (**harts**), an 8-lane fp32 vector
unit and a tensor unit whose matrix multiply-accumulate instruction is **TensorFMA** (one fp32 op multiplies 16×16×16
tiles: 4,096 multiply-adds). Only hart 0 issues tensor operations (hart 1 may only prefetch into the L2 scratchpad).
Eight minions form a **neighbourhood** and 32 a **shire**. Each shire has 4 MB of SRAM, which these cards' firmware
splits into a 512 KB L2 cache, a 1 MB slice of the chip-wide 32 MB L3 and a 2.5 MB **scratchpad**: software-managed
memory that any shire can address. Each minion also sets aside 3 KB of its 4 KB L1 data cache as an **L1
scratchpad** for tensor operands. The chip has 34 minion shires (1,088 minions): 32 run kernels (1,024 minions), the
master shire runs firmware and one is spare. With the I/O and PCIe shires they form a 6×6 grid on a mesh
network-on-chip (**NoC**, 400 MHz); eight memory shires with the LPDDR4X controllers (32 GB) sit along two sides,
making 8×6 mesh stops. A **hop** is one step between neighbouring stops, about 3.72 mm. A **flit** is the unit the
mesh moves as a whole. The **service processor (SP)** is the on-die management core: its firmware reads the sensors,
runs the clock and voltage governor (600, 700 or 800 MHz; the table of operating points is the VMIN LUT) and answers
the host's management commands. The **PMIC** is the board's power-management controller: it meters the 12 V input
and three regulators (the minion, SRAM and NoC rails). Moortec **PVT** monitors measure temperature and voltage on
the die. Kernels run in user mode (U-mode) and firmware in machine mode (M-mode). The four Maxions are larger
out-of-order RISC-V cores on their own 0.6 V rail. aifoundry2 and aifoundry3 (**a2**, **a3**) are the lab machines
that hold the two cards measured. The Horace experiment is named after Horace He's post showing that GPU matrix
multiplies run faster on predictable data.

The same glossary is on the hub, [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#terms).

## Where to look, by what you came for

| You want to… | Read |
|---|---|
| Quote a number and know it is right | [05-claims.md](05-claims.md) — every value, its kind (measured / simulated / fitted / predicted / derived / read from source / external / **assumed**), and the file and field that hold the evidence |
| Predict the heat of your own kernel | [12-heat-management.md](12-heat-management.md), then `tools/ettelem/predict_heat.py` |
| Predict a whole load's watts, clock, die temperature and energy per unit of work | [12-heat-management.md](12-heat-management.md) § "Pricing a whole load, not just a tile", then `tools/ettelem/predict_load.py`; what it got right and wrong on four loads it had never seen is [2026-10-26-load-model](../reports/data/2026-10-26-load-model/README.md) |
| Measure power on one of these cards | [14-card-behaviour.md](14-card-behaviour.md) — the protocol, the telemetry fields, and the traps |
| Understand the model or improve it | [11-thermal-model.md](11-thermal-model.md) |
| Argue about efficiency against a GPU | [13-why-low-power.md](13-why-low-power.md), and read its caveats first |
| Know what the card's instruments can and cannot see | [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md) and the hub's [ladder](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#ladder); [15-earlier-findings.md](15-earlier-findings.md) for the first survey |
| Share a counter, lock or flag between shires | [17-hot-line.md](17-hot-line.md) — one hot line stops the shire that hosts it |
| Make a multi-pass computation faster than main memory | [18-on-chip-relay.md](18-on-chip-relay.md) — hand each stage to the next shire's scratchpad |
| **Look up what anything costs in joules** | [../energy-manual/](../energy-manual/README.md) — the energy manual: at rest, awake, every instruction, per byte, wires, lines, rows, leakage, rails, between shires, synchronisation, composition; every entry with a confidence bar from repeated passes, on three cards since 26 September |
| Know what moving data across the chip costs per millimetre, or compare with Dally's rule of thumb | [20-heat-per-mm.md](20-heat-per-mm.md) — per bit per mm, per flip against per one, free against shared links |
| Know what the meters miss, and what would let them see more | [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md) — the power meter chain, the unmetered remainder attributed, the DDR-rail droop meter, the meter starved by s ↔ s+16 rings, the improvement ladder |
| Pick a machine, or compare two cards | [14-card-behaviour.md](14-card-behaviour.md) — the three machines side by side, and why aifoundry3 is slow |
| Understand the clock/voltage governor, or why the card leaks so much | [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) |
| Re-run an experiment | [03-experiments.md](03-experiments.md) — command, protocol, raw data path, caveats, and the report it fed |
| Find the published version | [04-artifacts.md](04-artifacts.md) — reports, spaces and their visibility, GIFs, tools, commits |
| Know what was re-checked, what reproduced and what did not | [04-artifacts.md](04-artifacts.md), "The 25 September validation", and its record in [../reports/data/2026-09-24-report-review/](../reports/data/2026-09-24-report-review/README.md); for the three-card check, each page claim with its outcome in [`results/pagemap.md`](../reports/data/2026-09-25-claims-v3/results/pagemap.md) |
| Know why a question was or was not answered | [02-requests.md](02-requests.md) |
| Check a source | [01-resources.md](01-resources.md) — what each is authoritative for, and what it is not |

## How provenance works here

Four kinds of thing have IDs, and every claim cites them:

| Prefix | Meaning | File |
|---|---|---|
| **R1–R14** | Resources that existed before any measurement: manuals, RTL, firmware source, prior reports, external papers, expert accounts, and the lab machines | [01-resources.md](01-resources.md) |
| **Q1–Q148** | Requests from the repo owner, and what each produced | [02-requests.md](02-requests.md) |
| **E1–E181** | Experiments: what ran, when, on what, with which command, producing which raw files (E33–E34 are the 18 September memory-hierarchy and on-chip communication sessions, registered later; E35–E47 the version-3 three-card check of 25–26 September; E48 the gathers and scatters on the same three cards; E49 the runtime's log-level race, 25–26 September; E50 the host link on the three cards, 27 September; E51 DV2 on aifoundry2, development on 28 September and a frozen validation on 28–29 September; E52 the heat placement, 27–28 September, development and a frozen validation; E53 the overheating experiments, 28 September, pre-registered; E54 NV, the mesh rail's voltage step, predictions frozen, not run; E55–E58 the major pass's pcie2, nocr, memp2 and tau, 28–29 September, developed on aifoundry1's card 1 and validated on aifoundry3 (E55–E57 also on aifoundry2 as a third card); E59 the sparse parity solver on aifoundry3, 29 September, an engineering benchmark; E60–E64 the October campaign — the bit-flip ladder, the deterministic transistor flips, the heat movies, the camera half of the ladder and Horace's power limit; E65 every bit position, the flow-M case and the hart ladder, 26 October; E66–E76 the rest of the October campaign (Q128–Q129: aifoundry2's idle slope, the A side, the stage map, the governor moved, the saturation ladder, aifoundry3's idle slope, 600 MHz, the camera's heat path, the register file, the memory path, the trapping instructions); E77 the rail at one temperature, reserved by Q129 and registered and run on 1 November under Q133's governor moves (recorded by Q134's records after its verification, beside E120, its redesign); E78–E91 Q130's, 31 October — the kinds energy matrix, the fp16 and int8 bit prices and the DRAM pattern on aifoundry3, the kinds' speed under aifoundry2's own governor (E80, E83), the matrix on aifoundry1's card 1 (E82), a speed replicate on aifoundry1's card 0 (E84), the camera per kind (E85), and the evening round: the real GPT-2 tiles' energy (E86) and speed (E87), the result path's share (E88), heat below 12 W (E89), sign patterns and tile spread (E90), and the real tiles on aifoundry1's card 1 (E91, not scored); E92–E106 Q132's, 1 November — signs and C read back, the zero gate, tile spread, more real tensors, heat below 12 W, the drift, the DRAM mechanism, the idle reset, a matmul that streams and its layout, balanced bit prices, the model's blind test and held signs; E107–E118 Q133's, 1 November — a large GEMM's placement, a sign's rest located, int8 zeros, the memory path's width, a steady coefficient on aifoundry2, replicates on aifoundry1's two cards and aifoundry3, the A side's form, the power model's blind pool, and E72 on card 0 by a governor move (E118); E117 was not run; E119–E125 Q134's, the evening of 1 November — what a clock gap buys in seven of E107's arms on aifoundry2, E77 redesigned by a governor move (E120), E93's zero gate, E108's sign designs and E94's † rows on aifoundry3, and E109's int8 zeros and E113's A side on aifoundry1's card 1; E126–E134 Q136's, 2 November, under the owner's three rules on device commands — E107's last three arms and a governed replicate, and E111's heat holds again, on aifoundry2; the float B-lane gate, which int8 multiplier, the memory path's split and more single-bit prices on aifoundry3; fp16's sign rest, int8's no-issue excess with one A row and E95's real tiles on aifoundry1's card 1; E135, 2 November, at the owner's OK: a GPU measured the same way, Horace He's kinds on two A100s rented on Modal, with no lab card; E136–E140 Q137's, 2 November, run so that power and heat can be predicted — a large GEMM predicted first on aifoundry2, fp16's sign rest on aifoundry1's card 1, int8's B side on the rail, the memory path's split again and the blind test of the model M6 on aifoundry3; E141–E150 Q138's, the evening of 2 November, run to settle the power model's open questions — blind pool 5 scored by the model M7 on aifoundry3, aifoundry1's card 1 and under aifoundry2's own governor, heat over minutes on aifoundry3 and aifoundry2 (E144, E144b), int8's B side on aifoundry1's card 1, a large GEMM's C stores on aifoundry2, single-bit prices at item 15's open positions on aifoundry3, int8's no-issue excess with two A rows on card 1, and the model checked on A100s and A10Gs rented on Modal, with no lab card; E151–E162 Q139's, 3 November, run on Q138's final critic's open list — int8's B side with its rail filter, the float gate's dose ladder, blind pool 6 scored by the model M8 and heat over minutes from the bits on aifoundry3, int8's no-issue floor by shape, the memory path's encoded term on two new images and blind pool 6 on aifoundry1's card 1, the L3's retention, a large GEMM's sustained power and clock predicted blind, blind pool 6 in bursts and heat over minutes from the bits under aifoundry2's own governor, and which operand pairing a GPU pays for, on A100s rented on Modal; E163–E169 are reserved for Q140's card half, 4 November — blind pool 7 on aifoundry3, aifoundry1's card 1 and in aifoundry2's bursts, the heat replicates on aifoundry3 and aifoundry2, and a large GEMM's sustained holds and the stride shapes on aifoundry2 — each frozen at the desk, none run; *dated, Wed 4 Nov 2026, the card half's records: they ran that afternoon on the owner's go, with E170, pool 7 on aifoundry1's card 0 in governed bursts, beside them*; *dated, Thu 5 Nov 2026, Q142(v2) and Q142(h)'s records: E171–E174 are registered for Q142's pool-8 card day, 5 November — blind pool 8 at 600 MHz on aifoundry3 and aifoundry1's card 1, in bursts under aifoundry2's own governor, and in governed bursts on aifoundry1's card 0 after card 1 — each frozen, registered and kitted at the desk, none run*; *dated, Thu 5 Nov 2026, Q143(r)'s records: E171–E174 ran that day on the owner's go; E175, aifoundry2's governed line, and E176, M11's first heat-over-minutes session on aifoundry3, refused at its start gate with nothing scored, ran that evening; E177 is reserved, not built, not run; E178 is Q146's, being registered, not run*; *dated, Fri 6 Nov 2026, Q148(r)'s records: E178 is registered, amended by A1 and A2 and kitted, not run; E179, the public power viruses on a card, is assigned, not registered, not built, not run; E180, the one-number vector add, is registered, amended by A1 and kitted, not run; E181, M11's second heat-over-minutes session on aifoundry3, is kitted and read READY, not run*) | [03-experiments.md](03-experiments.md) |
| **A1–A25** | Artifacts published: reports, spaces, GIFs, tools, commits (A9 and A10 are unused; A20 the session timeline; A21 the sparse parity page; A22 the heatsink study; A23 the transistor-heat timeline; A24 the matmul-to-transistor chain; A25 the kinds-of-numbers page) | [04-artifacts.md](04-artifacts.md) |

**To trace a claim** — say someone tells you "the ET-SoC-1 runs at 0.52 V":

1. Look it up in [05-claims.md](05-claims.md). It is there as 516–518 mV, kind `M` (measured), source **E9**.
2. [03-experiments.md](03-experiments.md), entry **E9**, says it ran on 2026-09-21 06:55–07:52 with `run_horace_strict.sh`, and points at
   `docs/reports/data/2026-09-21-horace-aifoundry2/strict/telemetry.jsonl.gz`.
3. That file has a `die_mv.minion` field in every one of ~35,000 samples. Check it yourself.

The same path works in reverse for anything **not** measured. The A100's 0.85 V core voltage is kind `A` —
an assumption — and [13-why-low-power.md](13-why-low-power.md) states how much the conclusion moves over the
plausible range. Esperanto's 20 W headline is kind `X` from R6 and is **modelled, not measured**.

## Reproducing

Raw data for the main body of work is `docs/reports/data/2026-09-21-horace-aifoundry2/` (7 MB: every kernel
launch, every run's start record, 10 Hz telemetry compacted, the exact operand tiles the card ran, the RTL
activity counts, the model, and the predictions with their timestamps).

```
tools/ettelem/finish_horace.sh     # no card needed: re-runs the Horace line (E9–E17 and the E20 transfer):
                                   # its analyses, the model, the held-out validations, the GIFs,
                                   # and the Horace and why-low-power pages
```

Every other experiment gives its own command in [03-experiments.md](03-experiments.md). Re-running on a card
needs aifoundry2's card (back in service since 9 October 2026 with a two-fan bracket at the card, so it now runs much
cooler than when these runs were made: compare with care), the build in `build/`, and an idle machine;
see [14-card-behaviour.md](14-card-behaviour.md)
for the traps and [AGENT.md](../../AGENT.md) §5 for the etiquette.

## What is *not* established

Stated in full in [05-claims.md](05-claims.md), last section. The big ones:

- **One GPU model, measured once.** Until 2 November 2026 every A100 number was from published sources: the datasheet (R7), the Ampere
  whitepaper, the sourced notes in `docs/reports/sources/` (`2026-09-18-a100-memory-hierarchy.md`,
  `2026-09-18-gpu-on-chip-communication.md`), and one blog post (R8). E135 then measured two A100-SXM4-40GB boards
  on Modal, at their default 400 W limit, in one session: no lower cap (the container refused it), no H100, square
  operands only, and no large GEMM on this chip to set beside them.
- **This chip at 0.4 V was never exercised.** The firmware offers 600–800 MHz at 0.52–0.62 V and nothing
  lower, so Esperanto's headline operating point is out of reach here.
- **Nothing that needs modified firmware** was done: the images are signed and no key is available, so
  per-event PMU counters on silicon, SRAM ECC counts and the debug fabric remain untested.
- **Which firmware the cards run.** Their trace strings match a service-processor build older than the
  et-platform source read here (R3).
- **The thermal resistance is this card in this desktop chassis**, not a property of the chip.
- **aifoundry1 contributed no measurements before 25 September 2026** (its cards could not be opened; card 1
  ran the version-3 campaign, E35–E46, and E48). aifoundry3 repeated the strict protocol (E20), the hot-line sweeps
  (E22–E23), the scratchpad probe and relay sweep (E24–E25), the catalogue (E26–E27), the reruns (E29) and the wire
  runs (E31–E32), but its thermal network was never characterised, so do not apply aifoundry2's 1.47 °C/W to it.
- **The model's slow thermal stages are not identified.** They move a lot between fits; do not quote them as
  physics.
