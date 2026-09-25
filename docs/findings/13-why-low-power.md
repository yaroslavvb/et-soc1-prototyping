# Finding: why the ET-SoC-1 is low power, term by term

[← Findings index](README.md) · published as [Why is the ET-SoC-1 low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) (A5) ·
numbers and sources: [05-claims.md](05-claims.md)

**Sources:** E15 (the ablations), E10 (the 600 and 800 MHz operating points), E17 (leakage), R6 (Esperanto's
argument), R7 and R8 (the A100 numbers, **not measured here**).

An A100 draws 330–400 W under a matmul. This card draws 38–64 W, and Esperanto advertised the chip at under
20 W. Both are TSMC 7 nm. Esperanto's own explanation is one line,
`Power = C_dynamic × V² × f + Leakage`, with every term pushed down. Each term can be measured.

**Short answer:**

- It runs at 0.52 V and 600 MHz where a GPU runs near 0.85 V and 1,160–1,410 MHz: a factor of 5 to 6 in switching
  power for the same capacitance.
- Whatever is not computing is clock-gated: it stops switching but still leaks; nothing is power-gated
  ([16](16-dvfs-and-leakage.md)).
- It does 14 to 28 times fewer FLOPs per second (fp16 or fp32 here, against the A100's bf16).
- It is **not** more efficient per FLOP at dense matmul: 7.0 pJ per FLOP in fp32 and 3.3 pJ in fp16, against the
  A100's 1.28 in bf16, so the A100's tensor cores are 5.4× and 2.6× better. Only against the A100's fp32 CUDA-core
  datasheet figure (19.5 TFLOPS at 400 W) is this card better: about 2.9× on random data and 3.4× on the matmul
  benchmark's ±1/±2 operands ([matmul efficiency](https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency), R4),
  a comparison of this card's measurement with the A100's datasheet.
- Leakage, the term Esperanto's slide leaves without a number, is the largest single item on this card.

---

## Side by side

| | A100 (SXM4) | ET-SoC-1 card | Note |
|---|---|---|---|
| Process, transistors, die | 7 nm · 54.2 B · 826 mm² | 7 nm · >24 B · 570 mm² | same process generation |
| Dense matmul, measured | 257 TFLOPS at 330 W | 9.18 TFLOPS at 63.9 W | A100: R8's 8192³ run, **bf16** on tensor cores, random data. ET: fp32 `TensorFMA`, random data, 80 °C |
| Board energy per FLOP | **1.28 pJ** (bf16) | **7.0 pJ** (fp32) | the A100's tensor cores are 5.4× better |
| Board energy per FLOP, 16-bit inputs (fp16 here, bf16 on the A100) | 1.28 pJ | 3.3 pJ (fp16, 61.1 W at 18.4 TFLOPS, E15) | the closest like for like: the A100 is ~2.6× better |
| Board energy per FLOP, fp32 by datasheet | 20.5 pJ (19.5 TFLOPS at 400 W, CUDA cores) | 7.0 pJ | this card is ~2.9× better (3.4× in the matmul benchmark, R4) |
| Idle | 88 W | 26.7 W at 62 °C, 36.3 W at 80 °C | |
| Power per transistor under load | 6.1 nW | 2.7 nW | |
| Power density under load | 0.40 W/mm² | 0.11 W/mm² | board power over die area; both include memory and regulators |
| Core voltage, clock | ~0.85 V *(assumed)* · 1,160–1,410 MHz | 0.52 V · 600 MHz | 1,410 MHz is the A100's maximum boost; under R8's 330 W cap on random data it is lower: 257 of the 312 peak TFLOPS needs at least 1,160 MHz, and if the zero-data run (295 TFLOPS) held 1,410, the random run was near 1,230 |
| V² × f, relative | 5.2–6.3× | 1× | switching power of the same capacitance |
| Memory | HBM2, 1,555 GB/s (40 GB; the 80 GB HBM2e part is 1,935–2,039) | LPDDR4x, 137 GB/s | |

## Esperanto's equation, measured

Their Hot Chips slide contrasts a generic x86 server core (7 W, 3 GHz, 0.85 V, 2.2 nF) with the
[minion](README.md#terms) they needed (0.01 W, 1 GHz, 0.425 V, 0.04 nF): 3× in frequency ("easy"), 4× in V² ("hard"), 58× in capacitance
("very hard"). Dividing a measured workload's power over idle by 1,024 minions, V² and f gives its effective
switched capacitance per minion:

| Workload on all 1,024 minions | Board W at 80 °C | Over idle | mW per minion, over idle | C_dyn per minion | pJ per unit of work |
|---|---|---|---|---|---|
| integer loop (4 adds + branch) | 37.79 | +1.46 | **1.4** | 0.009 nF | 8.1 per instruction |
| fp32 `TensorFMA`, zeros — fully gated | 38.23 | +1.91 | 1.9 | 0.012 nF | 0.42 per multiply-add |
| int8 `TensorFMA`, zeros | 38.90 | +2.57 | 2.5 | 0.016 nF | 0.08 |
| int8, ones | 40.62 | +4.22 | 4.1 | 0.026 nF | 0.13 |
| **int8, random** | 46.29 | +9.98 | **9.7** | 0.061 nF | **0.32** |
| fp32, ones | 46.87 | +10.56 | 10.3 | 0.064 nF | 2.30 |
| fp16, random | 61.10 | +24.78 | 24.2 | 0.151 nF | 2.70 |
| **fp32, random** | 63.93 | +27.63 | **27.0** | 0.168 nF | **6.02** |
| TensorLoad from L2 SRAM | 42.57 | +6.24 | 6.1 | 0.038 nF | 0.3 per bit |
| TensorLoad from LPDDR4x | 46.99 | +10.71 | 10.5 | 0.065 nF | 18 per bit |
| *Esperanto's design target* | | | *10 (total)* | *0.040 nF* | *at 1 GHz, 0.425 V; by P/(V²f), 10 mW there is 0.055 nF, so the slide's 0.040 nF would leave about 3 mW for the leakage its equation includes* |

- **The capacitance target holds for the workloads the chip was designed around.** An integer loop switches
  0.009 nF per minion, a gated tensor op 0.012, int8 multiply-adds on random data 0.061. The slide's 0.04 nF
  sits in the middle of that range. Only fp32 on random data — which the chip was not designed around — reaches
  0.17 nF.
- **10 mW per core: the switching part fits for int8,** even at this card's higher voltage: 4 mW over idle on
  constant data and 10 mW on random data. But Esperanto's 10 mW was the whole budget, leakage included, and this
  card's minion rail alone reads 22 W under int8 random data at the end of a 7 s run (about 82 °C), 21.7 mW per
  minion. fp32 on random data switches 27 mW per core.
- **This card is not at the advertised operating point.** Its lowest operating point is 0.52 V at 600 MHz. Below
  65 °C die temperature and 65 W board power the firmware steps it up through 0.57 V at 700 MHz to 0.62 V at
  800 MHz ([16](16-dvfs-and-leakage.md)). Esperanto's "about 0.4 V, 20 W" is an operating point the firmware never
  offers.

## The ablations

**Activity: what is not computing costs almost nothing.** 1,024 minions spinning in an integer loop add 1.46 W
to an idle card, 1.4 mW per core (a four-add loop issuing about 0.3 instructions per cycle; the energy manual's
tighter `addi` loop draws 2.1 mW per minion on one hart and 3.4 mW on both). Esperanto's claim that RISC-V compatibility costs little is borne out: during
a tensor instruction the integer pipeline sleeps, and a fully gated `TensorFMA` costs 1.9 W for the whole chip.

**Power is close to linear in active cores:** 25.6 mW per minion at 256 and 512 active, 26.2 at 768 and 27.0 at
1,024: linear to within 5%; a line through zero fits 26.5 mW per minion. Idle cores cost nothing measurable — no
cliff, no floor beyond the card's idle.

**Precision is the biggest lever inside the chip.** On random data an int8 multiply-add costs 0.32 pJ over
idle, fp16 2.70 pJ, fp32 6.02 pJ: a factor of **19** between the type the chip was built for (int8) and fp32 (the A100
figure here is bf16; this card's fp16 multiply-add costs 2.70 pJ). The int8 unit also runs 6.9× more multiply-adds
per second.

**The two outer operating points differ as CV²f says.** From a cool die the governor runs kernels at 800 MHz /
0.62 V; past 65 °C (or 65 W at the board) it drops to 600 MHz / 0.52 V (700 MHz at 0.57 V lies between). The same kernels at nearly the
same temperature (63–68 °C) draw, over idle: zeros 4.5 against 1.9 W (the 600 MHz zeros figure is from the 80 °C
runs, since from a cool die zeros stayed at 800 MHz), ones 21.0 against 10.0 W, random fp32 about 53 against 27 W
(the 87.8 W peak at 800 MHz less the 35.0 W idle there). The 800 MHz figures are the highest readings before the
governor stepped down; random data held 800 MHz for at most 0.3 s. That is **2.1× (ones) and 2.0× (random) the
switching power for 1.33× the clock**, where V²f predicts 1.91×: within about 10%. `tools/ettelem/build_vf.py`
writes these values (`vf.json`) from the cool-start telemetry, with each window stated. Energy per operation rises
1.5–1.6× for 33% more speed. Idle pays too: 35.0 W at 0.62 V against 28.1 W at 0.52 V, both at 63–68 °C.

**Leakage.** Idle board power follows 12.6 W + 23.3 W · e^((T−80)/36) from 64 to 88 °C, to 0.2 W. At 80 °C
that is 23 W of leakage in a 36 W idle. It is the term that keeps the measured card far from Esperanto's
headline, and a cooler die or the 0.4 V point would cut it on both counts.

**Memory.** Streaming tensors from LPDDR4x at 75 GB/s adds 10.7 W: 142 pJ per byte (**18 pJ per bit**) end to
end (DRAM, PHY, controller, mesh, cache fills), on a buffer whose contents were never set. The energy manual's
levels probe (memhier's 1 KB tensor loads over a buffer likewise never written, pinned at 600 MHz on both cards)
gives 122 pJ/B, and tensor loads on known data give 91 (zeros) to 129 (random) pJ/B, 11–16 pJ per bit. The manual's
data file keeps this section's ablation figures as `memory_reads.recheck_600mhz`. Streaming from the shire's own L2
cache at 2.4 TB/s adds 6.2 W: 2.6 pJ per byte (**0.3 pJ per bit**), as the energy manual's L2 row (2.5 pJ/B)
confirms: about 55 times cheaper per byte than DRAM.

## Putting the terms together

The A100 measured by R8 draws 330 W under load and 88 W idle, so ~242 W switches at ~0.85 V and
1,160–1,410 MHz: 237–288 nF of effective capacitance. This card's fp32 matmul switches 27.6 W at 0.52 V and
600 MHz: 172 nF.

| Term | A100 (bf16) | ET-SoC-1 (fp32) | Ratio |
|---|---|---|---|
| Switched capacitance | 237–288 nF | 172 nF | 1.4–1.7× |
| V² | 0.72 V² | 0.27 V² | 2.7× |
| Clock | 1,160–1,410 MHz | 600 MHz | 1.9–2.35× |
| **Switching power** | **242 W** | **27.6 W** | **8.8×** |
| Idle floor | 88 W | 36 W | 2.4× |
| FLOPs per second | 257 × 10¹² | 9.2 × 10¹² | 28× |
| Capacitance switched per FLOP | 1.3 pF | 11 pF | **0.12×** |
| Switching energy per FLOP | 0.94 pJ | 3.0 pJ | 0.31× |
| Board energy per FLOP | 1.28 pJ | 7.0 pJ | 0.18× |

The per-FLOP rows do not depend on the A100's clock. At 16 bits the capacitance per FLOP is 5.0 pF against 1.3
(3.9×), not 11 against 1.3.

**So of the 8.8× lower switching power, most is the operating point:** 6.3× at the A100's maximum clock (2.7× from
V², 2.35× from the clock), about 5.2–5.5× at the 1,160–1,230 MHz its capped random-data run implies. The rest,
1.4–1.7×, is switching less capacitance per cycle. Against the A100 this chip switches a comparable amount of
capacitance per cycle, but at a third of the V² and under half the clock, and everything idle is clock-gated to
nearly no switching power. What it does not have is efficiency per FLOP on dense floating-point matmul: in fp32 it
switches about nine times more capacitance per FLOP than the A100's bf16 tensor cores (3.9× in fp16), and at
9 TFLOPS its idle floor is spread over very little work.

On the workload it *was* designed for — int8 with sparse memory access — the arithmetic is 19× cheaper and the
comparison would be far closer. **That comparison was not run.**

## Caveats that matter

- **No A100 was measured.** Every GPU number is from R7 (datasheet) or R8 (one person's measurement of one
  GPU at a 330 W limit), and R8's run is bf16 on tensor cores, not fp32.
- **The A100's core voltage is an assumption** (0.85 V). Over 0.75–0.95 V the V² ratio runs from 2.1× to 3.3×, so
  at the maximum clock the V²f factor is 4.9–7.9× instead of 6.3× and the capacitance ratio 1.1–1.8× instead of
  1.4×. The 8.8× switching-power ratio is measured (242 W against 27.6 W) and does not move; the capacitance per
  FLOP ratio moves from 0.12× to 0.09–0.15×. Nor is the A100's clock under the 330 W cap published: 1,410 MHz is an
  upper bound.
- **Everything here is board power**, including LPDDR4x, regulators (about 7 W of the 28 W under random data is
  on no rail sensor, some 4 W of it regulator delivery loss; see [19](19-observability-and-the-unmetered.md)) and
  PCIe. Esperanto's 20 W is a chip figure.
- **One card.** aifoundry3 switches about 8% less for the same work ([11](11-thermal-model.md)).
- **The 800 MHz numbers come from seven short runs** in which the governor changed the clock within seconds
  (E10). They agree with V²f to 5%, but deserve the dedicated run that `tools/ettelem/run_vf_cold.sh` was
  written for and which has never been executed.
- **Desktop chassis.** The card idles at 62–80 °C; in server airflow it would run cooler and leak less.

## Related

- [10-data-dependent-power.md](10-data-dependent-power.md) and [11-thermal-model.md](11-thermal-model.md): the flip
  model and the leakage law used above.
- [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md): the governor, its three operating points, and why only clock
  gating works.
- [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md): what the 7 W on no rail sensor is.
- The energy manual, [`docs/energy-manual/`](../energy-manual/README.md): per-event costs with bars on two cards.
