# Finding: why the ET-SoC-1 is low power, term by term

**Sources:** E15 (the ablations), E10 (the two operating points), E17 (leakage), R6 (Esperanto's argument),
R7 and R8 (the A100 numbers, **not measured here**). Published as A5.

An A100 draws 330–400 W under a matmul. This card draws 38–64 W, and Esperanto advertised the chip at under
20 W. Both are TSMC 7 nm. Esperanto's own explanation is one line,
`Power = C_dynamic × V² × f + Leakage`, with every term pushed down. Each term can be measured.

**Short answer:** it runs at 0.52 V and 600 MHz where a GPU runs near 0.85 V and 1,410 MHz — a factor of 6.3
in switching power for the same capacitance — whatever is not computing is gated off, and it does 28× fewer
FLOPs per second. It is **not** more efficient per FLOP at dense matmul. And the term Esperanto's slide leaves
without a number, leakage, is the largest single item on this card.

---

## Side by side

| | A100 (SXM4) | ET-SoC-1 card | Note |
|---|---|---|---|
| Process, transistors, die | 7 nm · 54.2 B · 826 mm² | 7 nm · >24 B · 570 mm² | same process generation |
| Dense matmul, measured | 257 TFLOPS at 330 W | 9.18 TFLOPS at 63.9 W | A100: R8's 8192³ run on random data. ET: fp32 `TensorFMA`, random data, 80 °C |
| Board energy per FLOP | **1.28 pJ** | **7.0 pJ** | the A100 is ~5× better at dense matmul |
| Idle | 88 W | 26.7 W at 62 °C, 36.3 W at 80 °C | |
| Power per transistor under load | 6.1 nW | 2.7 nW | |
| Power density under load | 0.40 W/mm² | 0.11 W/mm² | |
| Core voltage, clock | ~0.85 V *(assumed)* · 1,410 MHz | 0.52 V · 600 MHz | |
| V² × f, relative | 6.3× | 1× | switching power of the same capacitance |
| Memory | HBM2e, 1,555 GB/s | LPDDR4x, 137 GB/s | |

## Esperanto's equation, measured

Their Hot Chips slide contrasts a generic x86 server core (7 W, 3 GHz, 0.85 V, 2.2 nF) with the minion they
needed (0.01 W, 1 GHz, 0.425 V, 0.04 nF): 3× in frequency ("easy"), 4× in V² ("hard"), 58× in capacitance
("very hard"). Dividing a measured workload's power over idle by 1,024 minions, V² and f gives its effective
switched capacitance per minion:

| Workload on all 1,024 minions | Board W at 80 °C | Over idle | mW per minion | C_dyn per minion | pJ per unit of work |
|---|---|---|---|---|---|
| integer loop (4 adds + branch) | 37.79 | +1.46 | **1.4** | 0.009 nF | 8.1 per instruction |
| fp32 `TensorFMA`, zeros — fully gated | 38.23 | +1.91 | 1.9 | 0.012 nF | 0.42 per multiply-add |
| int8 `TensorFMA`, zeros | 38.90 | +2.57 | 2.5 | 0.016 nF | 0.08 |
| int8, ones | 40.62 | +4.22 | 4.1 | 0.026 nF | 0.13 |
| **int8, random** | 46.29 | +9.98 | **9.8** | 0.061 nF | **0.32** |
| fp32, ones | 46.87 | +10.56 | 10.3 | 0.064 nF | 2.30 |
| fp16, random | 61.10 | +24.78 | 24.2 | 0.151 nF | 2.70 |
| **fp32, random** | 63.93 | +27.63 | **27.0** | 0.168 nF | **6.02** |
| TensorLoad from L2 SRAM | 42.57 | +6.24 | 6.1 | 0.038 nF | 0.3 per bit |
| TensorLoad from LPDDR4x | 46.99 | +10.71 | 10.5 | 0.065 nF | 18 per bit |
| *Esperanto's design target* | | | *10* | *0.040 nF* | *at 1 GHz, 0.425 V* |

- **The capacitance target holds for the workloads the chip was designed around.** An integer loop switches
  0.009 nF per minion, a gated tensor op 0.012, int8 multiply-adds on random data 0.061. The slide's 0.04 nF
  sits in the middle of that range. Only fp32 on random data — which the chip was not designed around — reaches
  0.17 nF.
- **10 mW per core is about right for int8:** 4 mW on constant data, 10 mW on random data, even at this card's
  higher-than-intended voltage.
- **This card is not at the advertised operating point.** Its lowest is 0.52 V at 600 MHz. Esperanto's "about
  0.4 V, 20 W" is an operating point the firmware never offers.

## The ablations

**Activity: what is not computing costs almost nothing.** 1,024 minions spinning in an integer loop add 1.46 W
to an idle card, 1.4 mW per core. Esperanto's claim that RISC-V compatibility costs little is borne out: during
a tensor instruction the integer pipeline sleeps, and a fully gated `TensorFMA` costs 1.9 W for the whole chip.

**Power is linear in active cores:** 25.6 mW per minion at 256, 512 and 768 active, 27.0 at 1,024. Idle cores
cost nothing measurable — no cliff, no floor beyond the card's idle.

**Precision is the biggest lever inside the chip.** On random data an int8 multiply-add costs 0.32 pJ over
idle, fp16 2.70 pJ, fp32 6.02 pJ: a factor of **19** between the type the chip was built for and the one a GPU
benchmark uses. The int8 unit also runs 6.9× more multiply-adds per second.

**Voltage and clock behave as CV²f says.** From a cool die the governor runs kernels at 800 MHz / 0.62 V; past
65 °C it drops to 600 MHz / 0.52 V. The same kernels at nearly the same temperature (64–68 °C) draw, over idle:
zeros 3.9 against 1.9 W, ones 20.6 against 10.2 W, random fp32 about 52 against 26 W — **2.0× the switching
power for 1.33× the clock**, where V²f predicts 1.90×. Energy per operation rises 1.5× for 33% more speed.
Idle pays too: 35.0 W at 0.62 V against 28.1 W at 0.52 V, both at 65 °C.

**Leakage.** Idle board power follows 12.6 W + 23.3 W · e^((T−80)/36) from 64 to 88 °C, to 0.2 W. At 80 °C
that is 23 W of leakage in a 36 W idle. It is the term that keeps the measured card far from Esperanto's
headline, and a cooler die or the 0.4 V point would cut it on both counts.

**Memory.** Streaming from LPDDR4x at 75 GB/s adds 10.7 W: **18 pJ per bit** end to end (DRAM, PHY,
controller, mesh, cache fills). From the shire's own L2 SRAM at 2.4 TB/s, 6.2 W: **0.3 pJ per bit**, sixty
times cheaper.

## Putting the terms together

The A100 measured by R8 draws 330 W under load and 88 W idle, so ~242 W switches at ~0.85 V and 1,410 MHz:
237 nF of effective capacitance. This card's fp32 matmul switches 27.6 W at 0.52 V and 600 MHz: 172 nF.

| Term | A100 | ET-SoC-1 | Ratio |
|---|---|---|---|
| Switched capacitance | 237 nF | 172 nF | 1.4× |
| V² | 0.72 V² | 0.27 V² | 2.7× |
| Clock | 1,410 MHz | 600 MHz | 2.35× |
| **Switching power** | **242 W** | **27.6 W** | **8.8×** |
| Idle floor | 88 W | 36 W | 2.4× |
| FLOPs per second | 257 × 10¹² | 9.2 × 10¹² | 28× |
| Capacitance switched per FLOP | 1.3 pF | 11 pF | **0.12×** |
| Switching energy per FLOP | 0.94 pJ | 3.0 pJ | 0.31× |
| Board energy per FLOP | 1.28 pJ | 7.0 pJ | 0.18× |

**So: three parts operating point, one part doing less.** Against the A100 this chip switches a comparable
amount of capacitance per cycle, but at a third of the V² and 43% of the clock, and everything idle is gated
to nearly nothing. What it does not have is efficiency per FLOP on dense floating-point matmul: its
general-purpose vector units switch nine times more capacitance per FLOP than tensor cores do, and at
9 TFLOPS its idle floor is spread over very little work.

On the workload it *was* designed for — int8 with sparse memory access — the arithmetic is 19× cheaper and the
comparison would be far closer. **That comparison was not run.**

## Caveats that matter

- **No A100 was measured.** Every GPU number is from R7 (datasheet) or R8 (one person's measurement of one
  GPU at a 330 W limit).
- **The A100's core voltage is an assumption** (0.85 V). Over 0.75–0.95 V the V² ratio runs from 2.1× to 3.3×,
  so the 8.8× switching ratio is really 7–11×.
- **Everything here is board power**, including LPDDR4x, regulators (about 7 W of the 28 W under random data
  never reaches the die) and PCIe. Esperanto's 20 W is a chip figure.
- **The 800 MHz numbers come from seven short runs** in which the governor changed the clock within seconds
  (E10). They agree with V²f to 5%, but deserve the dedicated run that `tools/ettelem/run_vf_cold.sh` was
  written for and which has never been executed.
- **Desktop chassis.** The card idles at 62–80 °C; in server airflow it would run cooler and leak less.
