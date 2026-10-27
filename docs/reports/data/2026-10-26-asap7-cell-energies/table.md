| cell | what | input pin cap (fF) | leakage (pW) | internal E/transition, VDD+VSS (fJ) | internal E/transition, VDD only (fJ) | E/transition @0.7 V (fJ) | @0.517 V (fJ) |
|---|---|---|---:|---:|---:|---:|---:|
| INVx1 | inverter, minimum drive | A 0.620 | 51.2 | 0.0975 | 0.0487 | 0.5875 | 0.3205 |
| INVxp33 | inverter, 1/3 drive (the smallest) | A 0.276 | 17.1 | 0.0484 | 0.0243 | 0.5384 | 0.2937 |
| BUFx2 | buffer (two inverters) | A 0.534 | 136.4 | 0.5033 | 0.2517 | 0.9933 | 0.5418 |
| NAND2xp33 | 2-input NAND, 1/3 drive | A 0.337, B 0.347 | 30.4 | 0.0800 | 0.0398 | 0.5700 | 0.3109 |
| NOR2xp33 | 2-input NOR, 1/3 drive | A 0.339, B 0.349 | 27.4 | 0.0809 | 0.0407 | 0.5709 | 0.3114 |
| AOI21xp33 | AND-OR-invert 2+1, 1/3 drive | A1 0.402, A2 0.371, B 0.442 | 46.9 | 0.1704 | 0.0856 | 0.6604 | 0.3603 |
| OAI21xp33 | OR-AND-invert 2+1, 1/3 drive | A1 0.401, A2 0.424, B 0.413 | 51.1 | 0.1912 | 0.0952 | 0.6812 | 0.3716 |
| NAND2x1 | 2-input NAND | A 0.990, B 0.990 | 91.2 | 0.2232 | 0.1103 | 0.7132 | 0.3890 |
| NOR2x1 | 2-input NOR | A 1.001, B 1.017 | 82.1 | 0.2293 | 0.1166 | 0.7193 | 0.3924 |
| XOR2x1 | 2-input XOR | A 1.519, B 1.523 | 232.1 | 0.9763 | 0.4896 | 1.4663 | 0.7998 |
| XNOR2x1 | 2-input XNOR | A 1.520, B 1.516 | 232.3 | 0.9742 | 0.4858 | 1.4642 | 0.7987 |
| XOR2xp5 | 2-input XOR, half drive | A 0.982, B 0.981 | 134.2 | 0.6003 | 0.3008 | 1.0903 | 0.5947 |
| XNOR2xp5 | 2-input XNOR, half drive | A 0.969, B 0.967 | 137.0 | 0.5973 | 0.2980 | 1.0873 | 0.5931 |
| AOI21x1 | AND-OR-invert, 2+1 | A1 1.113, A2 0.963, B 1.134 | 127.0 | 0.4413 | 0.2214 | 0.9313 | 0.5080 |
| OAI21x1 | OR-AND-invert, 2+1 | A1 1.112, A2 0.952, B 1.251 | 140.1 | 0.4512 | 0.2252 | 0.9412 | 0.5134 |
| MAJIxp5 | majority gate, inverting (the 4:2 compressor's carry) | A 0.595, B 1.122, C 0.963 | 94.3 | 0.4219 | 0.2112 | 0.9119 | 0.4974 |
| MAJx2 | majority gate, non-inverting | A 0.598, B 1.128, C 0.959 | 196.6 | 1.2584 | 0.6292 | 1.7484 | 0.9537 |
| HAxp5 | half adder | A 0.981, B 0.914 | 137.0 | 0.3041 | 0.1517 | 0.7941 | 0.4332 |
| FAx1 | full adder (28-transistor mirror type) | A 1.827, B 1.997, CI 1.494 | 212.2 | 0.8503 | 0.4255 | 1.3403 | 0.7311 |
| DFFHQNx1 | D flip-flop, inverting output | CLK 0.475, D 0.559 | 229.7 | 1.1010 | 0.4965 | 1.5910 | 0.8679 |
| ICGx1 | integrated clock gate | CLK 2.191, ENA 0.427, SE 0.428 | 319.2 | 0.8090 | 0.6517 | 1.2990 | 0.7086 |
