# ET-SoC-1 findings: start here

Everything measured on AI Foundry's ET-SoC-1 cards (`aifoundry2`, and `aifoundry3` for the cross-card work)
between 19 and 24 September 2026, written so
that **you never have to open the HTML reports or the raw data to get an answer** — though every number says
where to find both.

The question the work converged on: **what does a workload's data do to a chip's power and temperature, and
can you predict it before running?**

---

## If you have five minutes

1. **The effect.** The same matrix multiply — same clock, same instruction count, same 9.18 TFLOPS — draws
   **38 W on matrices of zeros, 47 W on ones and 63 W on random values**. The only thing that differs is the
   numbers in the operands. → [10-data-dependent-power.md](10-data-dependent-power.md)
2. **The explanation.** Simulating the chip's own multiply-add RTL on the operands the card ran gives four
   counts per operation. A zero operand is gated and costs nothing; a constant clocks registers but toggles no
   data; random values toggle 87 million nets. Four fitted energies turn those counts into watts to
   **±0.5 W** out of sample. → [11-thermal-model.md](11-thermal-model.md)
3. **The consequence.** Leakage is 23 of the 36 W an idle card draws at 80 °C and grows 0.65 W per °C, which
   closes a feedback loop with gain 0.95. Sustained switching above **about 3 W** has no equilibrium on this
   card: random data drives the die from 80 to 90 °C in **20 seconds**, ones in **two minutes**, zeros never.
   → [12-heat-management.md](12-heat-management.md)
4. **The governor.** The firmware's DVFS loop reads a power *sensor* rather than estimating power from
   activity counters, and its ±5% guardband macros are defined but never used — so it hunts, changing clock
   seven times in a 7-second run. Its leakage-suppression transistors exist in the RTL and are tied off.
   → [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md)
5. **The comparison.** Against an A100 this chip switches a similar capacitance per cycle, but at a third of
   the V² and 43% of the clock, and gates everything idle. It is **not** more efficient per FLOP at dense
   matmul: 7.0 pJ against 1.28. → [13-why-low-power.md](13-why-low-power.md)
6. **It transfers to another card.** Re-run on aifoundry3 — different silicon, a launch temperature 25 °C
   lower — the model applied unchanged is off by 1.4 W, and the error is a flat 8%, not scatter. **One scale
   factor of 0.92 brings it to 0.2 W rms**, and calibrating that factor on a single random-data run predicts
   the other seven patterns to 0.27 W. The leakage law extrapolated 25 °C below its fitted range lands within
   0.73 W. → [11-thermal-model.md](11-thermal-model.md), "Does it transfer to another card?"
7. **The gotcha if you use these machines.** aifoundry3's firmware reports a TDP of **0 W**, which makes the
   governor's step-up test unreachable and pins the card at 600 MHz for life. The driver reports the nameplate
   65 W on every machine, so nothing on the host notices. aifoundry1's two cards cannot be opened at all.
   → [14-card-behaviour.md](14-card-behaviour.md)
8. **The sharpest edge on the chip.** One contended global atomic is shared out perfectly fairly, and takes
   the entire memory path of the shire that hosts it to **zero** — 384 operations, then nothing, for as long
   as the hammering lasts. It takes 24 remote requesters, under one shire's worth, and the vendor's errata
   describe it and say the configuration bit that looks like the fix does not work.
   → [17-hot-line.md](17-hot-line.md)
9. **The biggest win available.** A chain of stages that hands its intermediate to a neighbouring shire's
   scratchpad instead of DRAM runs **12.3× faster at a twelfth of the energy per byte, on the same watts**;
   keeping it in the shire's own scratchpad is 30.7×. The catch is a sharp one: below the 32 MB L3 the cache
   already does the job and you gain nothing. → [18-on-chip-relay.md](18-on-chip-relay.md)
10. **What the bars say.** Re-running every table and repeating it on the second card puts a bar on every
   entry: ±6% in the median for the catalogue, mostly the 5% between the cards; ±17% on the hot line and
   ±5% on the DRAM relay, where a 1–5 W signal rides on a drifting 30 W idle. Two traps found on the way:
   aifoundry2's governor lifts the clock mid-burst below 68 °C, and rings between shires s and s+16 starve the
   service processor that reads the meter. → [../energy-manual/09-method.md](../energy-manual/09-method.md)
11. **What the meters miss.** Half of idle and a fifth of any workload is on no rail sensor. Fitted over 390
   bursts, that remainder is 18–20% delivery loss on the minion rail, 5% on SRAM, 26–29% on the mesh and
   about 70 pJ per DRAM byte off-rail, to 0.3 W; and the memory shires' Moortec voltage monitor droops
   0.84 mV per off-rail DRAM watt, a DRAM meter that was in every telemetry file all along.
   → [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md)
12. **What a millimetre of mesh costs.** At the mesh's 0.485 V a random bit costs 36 fJ per mm on the mesh rail with
   free links (25 of it data-dependent) and 50 on a loaded mesh; board power says 47 and 73. Ones carried cost
   energy, not just bits that change between flits, and sharing a link adds 40–45%. Scaled to 0.9 V the data part is
   85–105 fJ, bracketing Dally's "~100 fJ/b-mm". → [20-heat-per-mm.md](20-heat-per-mm.md)
13. **The caveat that matters most.** The temperature half of the model was only held out properly after the
   fact, when the fit was challenged. On runs it was not fitted to, the time-to-90 °C error is 9% in the
   median and 23% at worst out to a few minutes, and it runs 3–5 °C hot at ten minutes. → [11-thermal-model.md](11-thermal-model.md), section "How well it predicts"

## Where to look, by what you came for

| You want to… | Read |
|---|---|
| Quote a number and know it is right | [05-claims.md](05-claims.md) — every value, its kind (measured / simulated / fitted / predicted / external / **assumed**), and the file and field that hold the evidence |
| Predict the heat of your own kernel | [12-heat-management.md](12-heat-management.md), then `tools/ettelem/predict_heat.py` |
| Measure power on one of these cards | [14-card-behaviour.md](14-card-behaviour.md) — the protocol, the telemetry fields, and the traps |
| Understand the model or improve it | [11-thermal-model.md](11-thermal-model.md) |
| Argue about efficiency against a GPU | [13-why-low-power.md](13-why-low-power.md), and read its caveats first |
| Know what the card's instruments can and cannot see | [15-earlier-findings.md](15-earlier-findings.md) |
| Share a counter, lock or flag between shires | [17-hot-line.md](17-hot-line.md) — one hot line stops the shire that hosts it |
| Make a multi-pass computation faster than main memory | [18-on-chip-relay.md](18-on-chip-relay.md) — hand each stage to a neighbouring shire |
| **Look up what anything costs in joules** | [../energy-manual/](../energy-manual/README.md) — the energy manual: at rest, awake, every instruction, per byte, wires, lines, rows, leakage, rails, between shires, synchronisation, composition; every entry with a confidence bar from repeated passes on two cards |
| Know what moving data across the chip costs per millimetre, or compare with Dally's rule of thumb | [20-heat-per-mm.md](20-heat-per-mm.md) — per bit per mm, per flip against per one, free against shared links |
| Know what the meters miss, and what would let them see more | [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md) — the power meter chain, the unmetered remainder attributed, the DDR-rail droop meter, the meter starved by s ↔ s+16 rings, the improvement ladder |
| Pick a machine, or compare two cards | [14-card-behaviour.md](14-card-behaviour.md) — the three machines side by side, and why aifoundry3 is slow |
| Understand the clock/voltage governor, or why the card leaks so much | [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) |
| Re-run an experiment | [03-experiments.md](03-experiments.md) — command, protocol, raw data path, caveats |
| Find the published version | [04-artifacts.md](04-artifacts.md) — reports, spaces, GIFs, commits |
| Know why a question was or was not answered | [02-requests.md](02-requests.md) |
| Check a source | [01-resources.md](01-resources.md) — what each is authoritative for, and what it is not |

## How provenance works here

Four kinds of thing have IDs, and every claim cites them:

| Prefix | Meaning | File |
|---|---|---|
| **R1–R14** | Resources that existed before any measurement: manuals, RTL, firmware source, prior reports, external papers, expert accounts, and the lab machines | [01-resources.md](01-resources.md) |
| **Q1–Q42** | Requests from the repo owner, in order, and what each produced | [02-requests.md](02-requests.md) |
| **E1–E32** | Experiments: what ran, when, on what, with which command, producing which raw files | [03-experiments.md](03-experiments.md) |
| **A1–A18** | Artifacts published: reports, spaces, GIFs, tools, commits | [04-artifacts.md](04-artifacts.md) |

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
tools/ettelem/finish_horace.sh     # no card needed: re-runs every analysis, the model,
                                   # the held-out validations, the GIFs and both reports
```

Re-running on a card needs `aifoundry2`, the build in `build/`, and an idle machine; see
[03-experiments.md](03-experiments.md) for the commands and
[14-card-behaviour.md](14-card-behaviour.md) for the etiquette and the traps.

## What is *not* established

Stated in full in [05-claims.md](05-claims.md), last section. The big ones:

- **No GPU was measured.** Every A100 number is from a datasheet or one public blog post.
- **This chip at 0.4 V was never exercised.** The firmware offers 600–800 MHz at 0.52–0.62 V and nothing
  lower, so Esperanto's headline operating point is out of reach here.
- **Nothing that needs modified firmware** was done: the images are signed and no key is available, so
  per-event PMU counters on silicon, SRAM ECC counts and the debug fabric remain untested.
- **The thermal resistance is this card in this desktop chassis**, not a property of the chip.
- **aifoundry1 contributed no measurements**, and aifoundry3 contributed only the cross-card session: its
  thermal network was never characterised, so do not apply aifoundry2's 1.47 °C/W to it.
- **The model's slow thermal stages are not identified.** They move a lot between fits; do not quote them as
  physics.
