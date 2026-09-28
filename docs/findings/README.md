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
   A100 in bf16. Only against the A100's fp32 CUDA-core datasheet figure is it better: about 2.9× on random data,
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
   aifoundry1's two cards work since 25 September 2026, on two more firmware releases, and its card 0 overheats
   under load. → [14-card-behaviour.md](14-card-behaviour.md)
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
   at once move half as much as one, for reasons not established. → [03-experiments.md](03-experiments.md), E50;
   [05-claims.md](05-claims.md), "The host link"
17. **The governor the cards run, and what it compares** (development, 28 September; not validated). The cards run
   an older governor than the source first read: on aifoundry2 a thermal episode is a blocking loop of about 0.405 s
   steps that acts on an idle card too, and a climb goes to 800 MHz in one call. It compares the whole-degree mean of
   the 34 minion-shire sensors, not the hottest one: the clock held 800 MHz for over a second after the hottest sensor
   read 67 °C in 12 of 12 runs. Placing 192 minions on the perimeter held 800 MHz 1.4 and at least 1.8 times as long
   as in the interior (two blocks). aifoundry3's governor is latched by its zero TDP, aifoundry1's card 1's never
   raises the clock, and nothing on those three cards limits the die's temperature (a 90–103 °C mean on aifoundry2,
   26 September). aifoundry2's Master Minion hung that night; the management reset restored it at 08:32 the same
   morning (the sysfs per-card reset had not).
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
| **Q1–Q61** | Requests from the repo owner, and what each produced | [02-requests.md](02-requests.md) |
| **E1–E53** | Experiments: what ran, when, on what, with which command, producing which raw files (E33–E34 are the 18 September memory-hierarchy and on-chip communication sessions, registered later; E35–E47 the version-3 three-card check of 25–26 September; E48 the gathers and scatters on the same three cards; E49 the runtime's log-level race, 25–26 September; E50 the host link on the three cards, 27 September; E51 the DV2 development night on aifoundry2, 28 September, development only; E52 the heat placement, 27–28 September, development and a frozen validation; E53 the overheating experiments, 28 September, pre-registered) | [03-experiments.md](03-experiments.md) |
| **A1–A19** | Artifacts published: reports, spaces, GIFs, tools, commits (A9 and A10 are unused) | [04-artifacts.md](04-artifacts.md) |

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
needs `aifoundry2`, the build in `build/`, and an idle machine; see [14-card-behaviour.md](14-card-behaviour.md)
for the traps and [AGENT.md](../../AGENT.md) §5 for the etiquette.

## What is *not* established

Stated in full in [05-claims.md](05-claims.md), last section. The big ones:

- **No GPU was measured.** Every A100 number is from published sources: the datasheet (R7), the Ampere
  whitepaper, the sourced notes in `docs/reports/sources/` (`2026-09-18-a100-memory-hierarchy.md`,
  `2026-09-18-gpu-on-chip-communication.md`), and one blog post (R8).
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
