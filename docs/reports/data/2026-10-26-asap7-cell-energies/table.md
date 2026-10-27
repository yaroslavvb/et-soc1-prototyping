Internal energy is per OUTPUT TRANSITION, averaged over rise and fall
and over the arc's mutually exclusive `when` states, then over the
cell's arcs. **The headline convention is the VDD group alone**; the
summed column is VDD+VSS, what a power tool reports, and it
double-counts (part 2 settles it in SPICE). 10 ps input slew, 2.0 fF
output load, RVT TT 0.7 V 25 C.

| cell | what | input pin cap (fF) | leakage (pW) | when states | **internal E/transition, VDD only (fJ)** | summed reference, VDD+VSS (fJ) | **E/transition @0.7 V (fJ)** | **@0.517 V (fJ)** |
|---|---|---|---:|---:|---:|---:|---:|---:|
| INVx1 | inverter, minimum drive | A 0.620 | 51.2 | 1 | 0.0487 | 0.0975 | 0.5387 | 0.2939 |
| INVxp33 | inverter, 1/3 drive (the smallest) | A 0.276 | 17.1 | 1 | 0.0243 | 0.0484 | 0.5143 | 0.2806 |
| BUFx2 | buffer (two inverters) | A 0.534 | 136.4 | 1 | 0.2517 | 0.5033 | 0.7417 | 0.4046 |
| NAND2xp33 | 2-input NAND, 1/3 drive | A 0.337, B 0.347 | 30.4 | 1 | 0.0398 | 0.0800 | 0.5298 | 0.2890 |
| NOR2xp33 | 2-input NOR, 1/3 drive | A 0.339, B 0.349 | 27.4 | 1 | 0.0407 | 0.0809 | 0.5307 | 0.2895 |
| AOI21xp33 | AND-OR-invert 2+1, 1/3 drive | A1 0.402, A2 0.371, B 0.442 | 46.9 | 3 | 0.0539 | 0.1072 | 0.5439 | 0.2967 |
| OAI21xp33 | OR-AND-invert 2+1, 1/3 drive | A1 0.401, A2 0.424, B 0.413 | 51.1 | 3 | 0.0549 | 0.1097 | 0.5449 | 0.2972 |
| NAND2x1 | 2-input NAND | A 0.990, B 0.990 | 91.2 | 1 | 0.1103 | 0.2232 | 0.6003 | 0.3274 |
| NOR2x1 | 2-input NOR | A 1.001, B 1.017 | 82.1 | 1 | 0.1166 | 0.2293 | 0.6066 | 0.3309 |
| XOR2x1 | 2-input XOR | A 1.519, B 1.523 | 232.1 | 2 | 0.2448 | 0.4881 | 0.7348 | 0.4008 |
| XNOR2x1 | 2-input XNOR | A 1.520, B 1.516 | 232.3 | 2 | 0.2429 | 0.4871 | 0.7329 | 0.3998 |
| XOR2xp5 | 2-input XOR, half drive | A 0.982, B 0.981 | 134.2 | 2 | 0.1504 | 0.3001 | 0.6404 | 0.3493 |
| XNOR2xp5 | 2-input XNOR, half drive | A 0.969, B 0.967 | 137.0 | 2 | 0.1490 | 0.2987 | 0.6390 | 0.3486 |
| AOI21x1 | AND-OR-invert, 2+1 | A1 1.113, A2 0.963, B 1.134 | 127.0 | 3 | 0.1426 | 0.2834 | 0.6326 | 0.3451 |
| OAI21x1 | OR-AND-invert, 2+1 | A1 1.112, A2 0.952, B 1.251 | 140.1 | 3 | 0.1439 | 0.2889 | 0.6339 | 0.3458 |
| MAJIxp5 | majority gate, inverting (the 4:2 compressor's carry) | A 0.595, B 1.122, C 0.963 | 94.3 | 2 | 0.1056 | 0.2110 | 0.5956 | 0.3249 |
| MAJx2 | majority gate, non-inverting | A 0.598, B 1.128, C 0.959 | 196.6 | 2 | 0.3146 | 0.6292 | 0.8046 | 0.4389 |
| HAxp5 | half adder | A 0.981, B 0.914 | 137.0 | 2 | 0.1023 | 0.2052 | 0.5923 | 0.3231 |
| FAx1 | full adder (28-transistor mirror type) | A 1.827, B 1.997, CI 1.494 | 212.2 | 4 | 0.1421 | 0.2840 | 0.6321 | 0.3448 |
| DFFHQNx1 | D flip-flop, inverting output, minimum drive | CLK 0.475, D 0.559 | 229.7 | 1 | 0.4965 | 1.1010 | 0.9865 | 0.5381 |
| DFFHQx4 | D flip-flop, x4 drive (the only flop in the Q126(e) census) | CLK 0.476, D 0.559 | 485.5 | 1 | 0.9892 | 2.0865 | 1.4792 | 0.8069 |
| ICGx1 | integrated clock gate | CLK 2.191, ENA 0.427, SE 0.428 | 319.2 | 2 | 0.3258 | 0.4045 | 0.8158 | 0.4450 |

`E/transition` = internal (VDD only) + 1/2 C_load V^2 at 2.0 fF; the @0.517 V column scales the whole by (0.517/0.7)^2.
