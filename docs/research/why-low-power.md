# Why is the ET-SoC-1 low power? Sources and numbers

Notes behind `docs/reports/2026-09-21-why-low-power.html`. Measurements are from aifoundry2's card; the rest is
from the sources listed at the end.

## Esperanto's own argument (Hot Chips 33, August 2021; IEEE Micro, May/June 2022)

- The target: six chips on a 120 W OCP card, so under 20 W per chip, "about 0.4 V"; half of that for the
  thousand minions, "so only 10 mW per core".
- The equation on the slide: `Power = Cdynamic x Voltage^2 x Frequency + Leakage`.

| | Power per core | Frequency | Voltage | Cdynamic |
|---|---|---|---|---|
| Generic x86 server core (165 W for 24 cores) | 7 W | 3 GHz | 0.850 V | 2.2 nF |
| 10 mW ET-Minion core (about 10 W for 1K cores) | 0.01 W | 1 GHz | 0.425 V | 0.04 nF |
| Reduction needed | about 700x | 3x ("easy") | 4x ("hard": circuits, SRAM) | 58x ("very hard": architecture) |

- The voltage study (modelled, cores re-synthesised per voltage): one chip at the highest voltage 275 W; at
  0.75 V, "the nominal voltage in 7 nm", 164 W; 0.67 V gives 118 W; about 0.4 V gives 20 W; the best
  energy-efficiency point, 0.3 V, gives 8.5 W. Energy efficiency at 0.3 V is 20 times that at the highest
  voltage. "Esperanto's sweet spot ... between 300 and 500 mV."
- How the core was made to work there: an in-order pipeline with "very few gates per pipeline stage";
  libraries recharacterised at 0.4 V; the whole minion, L1 included, on one low-voltage plane; the integer
  pipeline sleeps during tensor instructions (up to 512 cycles each); eight minions share one instruction cache
  and can share one L2 load; the 1 MB SRAM banks run near nominal voltage for density; the mesh has its own
  low-voltage domain; LPDDR4x instead of HBM, with bandwidth scaled by using more chips.
- The chip: TSMC 7 nm, over 24 billion transistors, 570 mm2, 89 mask layers, 1,088 minions, 4 Maxions,
  256-bit LPDDR4x at 137 GB/s, operating range 300 MHz to 2 GHz, "peak of 128 Int8 GOPS per GHz" per minion.

## The A100, for comparison

- Datasheet: TSMC 7 nm, 54.2 billion transistors, 826 mm2, 400 W (SXM4); fp32 19.5 TFLOPS, TF32 156, fp16/bf16
  tensor cores 312, int8 624 TOPS; HBM2e at 1.6 to 2.0 TB/s.
- Horace He's measurement (the post this repo's Horace experiment reproduces): 8192^3 matmul, 257 TFLOPS on
  random data and 295 on zeros, with a 330 W power limit on his A100; 88 W idle.
- Core voltage is not published. Esperanto calls 0.75 V nominal for 7 nm; GPUs run above nominal at their
  top clock (1,410 MHz maximum graphics clock on an A100).

## What this card measures (2026-09-20/21, 0.52 V, 600 MHz, 80 C unless said)

- Idle 36.3 W at 80 C, 26.7 W at 62 C. Fitted: 11.5 W fixed + 24.5 W x exp((T - 80)/38) of leakage.
- fp32 TensorFMA on 1,024 minions, 9.18 TFLOPS: 38.3 W on zeros, 46.7 W on ones, 63.4 W on random normal.
- Per minion, above idle: 2 mW (zeros), 10 mW (ones), 26 mW (random fp32). Cdynamic = P/(V^2 f): 0.012, 0.064
  and 0.16 nF against the slide's 0.04 nF target.
- The 0.62 V / 800 MHz operating point (the governor's choice below 65 C): idle 35.0 W against 28.1 W at the
  same 65 C.

## Sources

- D. Ditzel et al., "Accelerating ML Recommendation with over a Thousand RISC-V/Tensor Processors on Esperanto's
  ET-SoC-1 Chip", Hot Chips 33, 2021: https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Esperanto.Dave_Ditzel.presentation.v1submitted.pdf
- D. Ditzel et al., same title, IEEE Micro 42(3), 2022: https://www.esperanto.ai/wp-content/uploads/2022/05/Dave-IEEE-Micro.pdf
- NVIDIA A100 datasheet: https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet.pdf
- H. He, "Strangely, Matrix Multiplications on GPUs Run Faster When Given 'Predictable' Data!", 2024:
  https://www.thonking.ai/p/strangely-matrix-multiplications
