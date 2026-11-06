# Q145(a) anatomy tables (post hoc; written by `anatomy_q145a.py`, every figure from committed files)

Each TensorFMA table is one TensorFMA instruction on one minion (fp32 4,096 MACs, fp16 8,192, int8 16,384), at the measured rate of that session's kept passes; each vector table is one instruction of both harts' loop (8 lanes). Lines marked `+` add up to the board's window reading; lines marked `x` are cross-cuts (a split of lines above, not added). Charge is energy over the line's voltage; electrons are charge over e. Off-rail lines are counted at the card's nominal 12 V input.

## TensorFMA `fp32.zeros`, aifoundry3 (E171, 4 passes)

Board in the window 27.919 W (95% 0.034); 1.1172e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **24.99 nJ an op, 6.101 pJ a MAC** with rest included; 1.3e+10 electrons an op from the 12 V input; idle bracket at 58.83 C, window at 58.08 C. Sum of the `+` lines 27.919 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.991 | 11627.9 | 2.8388 | 46.53% | 12.000 | 6.05e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.298 | 7427.1 | 1.8133 | 29.72% | 0.522 | 8.88e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.227 | 1992.9 | 0.4865 | 7.97% | 0.698 | 1.78e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.590 | 2318.5 | 0.5660 | 9.28% | 0.484 | 2.99e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.680 | 1503.7 | 0.3671 | 6.02% | 0.522 | 1.80e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.075 | 67.0 | 0.0164 | 0.27% | 0.698 | 5.99e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.012 | -10.8 | -0.0026 | -0.04% | 0.484 | -1.39e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.225 | 201.2 | 0.0491 | 0.81% | 12.000 | 1.05e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.522 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.698 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.484 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.154 | -138.0 | -0.0337 | -0.55% | 12.000 | -7.18e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.304 | 271.8 | 0.0664 | 1.09% | 12.000 | 1.41e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.079 | -70.7 | -0.0172 | -0.28% | 12.000 | -3.67e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.83 C), by the card's idle law | 13.883 | 12426.5 | 3.0338 | 49.73% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.57-17.35 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.222 | 10939.8 | 2.6709 | 43.78% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.005 | 4.8 | 0.0012 | 0.02% | 12.000 | 2.52e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `anchor_pi`, aifoundry3 (E171, 4 passes)

Board in the window 36.472 W (95% 0.055); 1.1174e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **32.64 nJ an op, 7.969 pJ a MAC** with rest included; 1.7e+10 electrons an op from the 12 V input; idle bracket at 58.45 C, window at 58.98 C. Sum of the `+` lines 36.472 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.926 | 11567.5 | 2.8241 | 35.44% | 12.000 | 6.02e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.269 | 7400.2 | 1.8067 | 22.67% | 0.522 | 8.85e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.214 | 1981.0 | 0.4837 | 6.07% | 0.698 | 1.77e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.572 | 2301.9 | 0.5620 | 7.05% | 0.484 | 2.97e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.642 | 1469.8 | 0.3588 | 4.50% | 0.522 | 1.76e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.087 | 78.2 | 0.0191 | 0.24% | 0.698 | 6.99e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | 0.006 | 5.1 | 0.0012 | 0.02% | 0.484 | 6.58e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.276 | 246.8 | 0.0602 | 0.76% | 12.000 | 1.28e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 7.041 | 6301.4 | 1.5384 | 19.31% | 0.522 | 7.53e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.027 | 24.5 | 0.0060 | 0.08% | 0.698 | 2.19e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.041 | 36.8 | 0.0090 | 0.11% | 0.484 | 4.75e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 1.262 | 1129.7 | 0.2758 | 3.46% | 12.000 | 5.88e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.108 | 96.7 | 0.0236 | 0.30% | 12.000 | 5.03e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 1.590 | 1423.2 | 0.3475 | 4.36% | 12.000 | 7.40e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.288 | 1152.3 | 0.2813 | 3.53% | 12.000 | 5.99e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.052 | -46.7 | -0.0114 | -0.14% | 12.000 | -2.43e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.45 C), by the card's idle law | 13.739 | 12295.8 | 3.0019 | 37.67% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.45-17.17 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.241 | 10954.8 | 2.6745 | 33.56% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 8.3 | 0.0020 | 0.03% | 12.000 | 4.30e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.randn`, aifoundry3 (E171, 4 passes)

Board in the window 53.256 W (95% 0.028); 1.1171e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **47.67 nJ an op, 11.639 pJ a MAC** with rest included; 2.48e+10 electrons an op from the 12 V input; idle bracket at 58.88 C, window at 61.19 C. Sum of the `+` lines 53.256 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.976 | 11615.8 | 2.8359 | 24.37% | 12.000 | 6.04e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.286 | 7416.8 | 1.8107 | 15.56% | 0.521 | 8.89e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.229 | 1995.5 | 0.4872 | 4.19% | 0.698 | 1.78e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.594 | 2321.7 | 0.5668 | 4.87% | 0.484 | 2.99e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.699 | 1520.7 | 0.3713 | 3.19% | 0.521 | 1.82e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.072 | 64.3 | 0.0157 | 0.13% | 0.698 | 5.75e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.016 | -14.4 | -0.0035 | -0.03% | 0.484 | -1.85e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.242 | 216.9 | 0.0530 | 0.46% | 12.000 | 1.13e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 19.645 | 17585.2 | 4.2933 | 36.89% | 0.521 | 2.11e11 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.122 | 108.8 | 0.0266 | 0.23% | 0.698 | 9.73e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.191 | 171.2 | 0.0418 | 0.36% | 0.484 | 2.21e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 4.740 | 4242.6 | 1.0358 | 8.90% | 12.000 | 2.21e9 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.477 | 426.7 | 0.1042 | 0.90% | 12.000 | 2.22e8 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 3.923 | 3511.4 | 0.8573 | 7.37% | 12.000 | 1.83e9 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 3.617 | 3237.6 | 0.7904 | 6.79% | 12.000 | 1.68e9 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 1.059 | 948.2 | 0.2315 | 1.99% | 12.000 | 4.93e8 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.88 C), by the card's idle law | 13.903 | 12444.8 | 3.0383 | 26.11% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.59-17.38 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.182 | 10904.9 | 2.6623 | 22.87% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.020 | 17.6 | 0.0043 | 0.04% | 12.000 | 9.17e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.zeros`, aifoundry3 (E171, 4 passes)

Board in the window 27.898 W (95% 0.055); 1.1171e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **24.97 nJ an op, 3.049 pJ a MAC** with rest included; 1.3e+10 electrons an op from the 12 V input; idle bracket at 58.84 C, window at 58.08 C. Sum of the `+` lines 27.898 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.958 | 11599.6 | 1.4160 | 46.45% | 12.000 | 6.03e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.268 | 7401.6 | 0.9035 | 29.64% | 0.522 | 8.85e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.228 | 1994.2 | 0.2434 | 7.99% | 0.698 | 1.78e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.588 | 2316.9 | 0.2828 | 9.28% | 0.484 | 2.99e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.708 | 1528.9 | 0.1866 | 6.12% | 0.522 | 1.83e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.077 | 69.1 | 0.0084 | 0.28% | 0.698 | 6.18e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.009 | -8.1 | -9.917e-04 | -0.03% | 0.484 | -1.05e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.236 | 211.0 | 0.0258 | 0.84% | 12.000 | 1.10e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.522 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.698 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.484 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.156 | -139.6 | -0.0170 | -0.56% | 12.000 | -7.26e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.310 | 277.3 | 0.0338 | 1.11% | 12.000 | 1.44e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.074 | -66.2 | -0.0081 | -0.27% | 12.000 | -3.45e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.84 C), by the card's idle law | 13.890 | 12433.6 | 1.5178 | 49.79% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.57-17.36 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.153 | 10878.7 | 1.3280 | 43.56% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.005 | 4.8 | 5.906e-04 | 0.02% | 12.000 | 2.52e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.randn`, aifoundry3 (E171, 4 passes)

Board in the window 50.607 W (95% 0.061); 1.1175e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **45.29 nJ an op, 5.528 pJ a MAC** with rest included; 2.36e+10 electrons an op from the 12 V input; idle bracket at 58.77 C, window at 60.83 C. Sum of the `+` lines 50.607 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.993 | 11627.4 | 1.4194 | 25.67% | 12.000 | 6.05e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.259 | 7390.8 | 0.9022 | 16.32% | 0.521 | 8.85e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.229 | 1994.3 | 0.2434 | 4.40% | 0.698 | 1.78e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.591 | 2318.2 | 0.2830 | 5.12% | 0.484 | 2.99e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.708 | 1528.9 | 0.1866 | 3.38% | 0.521 | 1.83e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.077 | 69.0 | 0.0084 | 0.15% | 0.698 | 6.17e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.011 | -10.0 | -0.0012 | -0.02% | 0.484 | -1.29e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.197 | 176.4 | 0.0215 | 0.39% | 12.000 | 9.17e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 17.789 | 15919.4 | 1.9433 | 35.15% | 0.521 | 1.91e11 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.110 | 98.1 | 0.0120 | 0.22% | 0.698 | 8.77e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.169 | 151.5 | 0.0185 | 0.33% | 0.484 | 1.95e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 4.073 | 3645.1 | 0.4450 | 8.05% | 12.000 | 1.90e9 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.423 | 378.7 | 0.0462 | 0.84% | 12.000 | 1.97e8 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 3.583 | 3206.6 | 0.3914 | 7.08% | 12.000 | 1.67e9 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 3.274 | 2929.9 | 0.3577 | 6.47% | 12.000 | 1.52e9 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.687 | 614.9 | 0.0751 | 1.36% | 12.000 | 3.20e8 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.77 C), by the card's idle law | 13.864 | 12406.7 | 1.5145 | 27.40% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.55-17.33 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.207 | 10923.9 | 1.3335 | 24.12% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.018 | 15.9 | 0.0019 | 0.04% | 12.000 | 8.28e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.zeros`, aifoundry3 (E171, 4 passes)

Board in the window 28.508 W (95% 0.056); 1.9209e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **14.84 nJ an op, 0.906 pJ a MAC** with rest included; 7.72e+09 electrons an op from the 12 V input; idle bracket at 58.76 C, window at 58.30 C. Sum of the `+` lines 28.508 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.986 | 6760.6 | 0.4126 | 45.55% | 12.000 | 3.52e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.274 | 4307.2 | 0.2629 | 29.02% | 0.522 | 5.15e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.224 | 1158.0 | 0.0707 | 7.80% | 0.698 | 1.04e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.589 | 1348.1 | 0.0823 | 9.08% | 0.484 | 1.74e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.253 | 1172.9 | 0.0716 | 7.90% | 0.522 | 1.40e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.003 | 1.8 | 1.082e-04 | 0.01% | 0.698 | 1.59e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.010 | -5.2 | -3.146e-04 | -0.03% | 0.484 | -6.65e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.282 | 146.6 | 0.0089 | 0.99% | 12.000 | 7.62e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.522 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.698 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.484 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.093 | -48.5 | -0.0030 | -0.33% | 12.000 | -2.52e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.405 | 210.8 | 0.0129 | 1.42% | 12.000 | 1.10e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.123 | -64.3 | -0.0039 | -0.43% | 12.000 | -3.34e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.76 C), by the card's idle law | 13.857 | 7214.0 | 0.4403 | 48.61% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.55-17.32 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.216 | 6359.8 | 0.3882 | 42.85% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.006 | 2.9 | 1.793e-04 | 0.02% | 12.000 | 1.53e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.full`, aifoundry3 (E171, 4 passes)

Board in the window 35.764 W (95% 0.133); 1.9205e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **18.62 nJ an op, 1.137 pJ a MAC** with rest included; 9.69e+09 electrons an op from the 12 V input; idle bracket at 58.61 C, window at 58.94 C. Sum of the `+` lines 35.764 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.992 | 6765.0 | 0.4129 | 36.33% | 12.000 | 3.52e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.264 | 4303.1 | 0.2626 | 23.11% | 0.522 | 5.15e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.218 | 1154.9 | 0.0705 | 6.20% | 0.698 | 1.03e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.583 | 1345.0 | 0.0821 | 7.22% | 0.484 | 1.73e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.239 | 1166.0 | 0.0712 | 6.26% | 0.522 | 1.39e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.010 | 5.2 | 3.190e-04 | 0.03% | 0.698 | 4.67e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.004 | -2.0 | -1.250e-04 | -0.01% | 0.484 | -2.64e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.282 | 146.7 | 0.0090 | 0.79% | 12.000 | 7.63e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 5.953 | 3099.8 | 0.1892 | 16.65% | 0.522 | 3.71e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.033 | 17.3 | 0.0011 | 0.09% | 0.698 | 1.55e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.052 | 26.8 | 0.0016 | 0.14% | 0.484 | 3.46e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 1.073 | 558.8 | 0.0341 | 3.00% | 12.000 | 2.91e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.069 | 35.7 | 0.0022 | 0.19% | 12.000 | 1.86e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 1.499 | 780.3 | 0.0476 | 4.19% | 12.000 | 4.06e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.094 | 569.6 | 0.0348 | 3.06% | 12.000 | 2.96e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.144 | -74.8 | -0.0046 | -0.40% | 12.000 | -3.89e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.61 C), by the card's idle law | 13.800 | 7185.6 | 0.4386 | 38.59% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.50-17.25 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.257 | 6382.4 | 0.3896 | 34.27% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 4.6 | 2.823e-04 | 0.02% | 12.000 | 2.41e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.zeros`, aifoundry1-c1 (E172, 3 passes)

Board in the window 34.909 W (95% 0.111); 1.1172e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **31.25 nJ an op, 7.628 pJ a MAC** with rest included; 1.63e+10 electrons an op from the 12 V input; idle bracket at 58.56 C, window at 58.01 C. Sum of the `+` lines 34.909 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.270 | 14562.6 | 3.5553 | 46.61% | 12.000 | 7.57e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.787 | 9655.1 | 2.3572 | 30.90% | 0.499 | 1.21e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.367 | 2118.6 | 0.5172 | 6.78% | 0.751 | 1.76e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.835 | 3432.6 | 0.8380 | 10.99% | 0.486 | 4.41e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.573 | 1407.7 | 0.3437 | 4.51% | 0.499 | 1.76e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.067 | 59.7 | 0.0146 | 0.19% | 0.751 | 4.96e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.040 | -35.4 | -0.0087 | -0.11% | 0.486 | -4.55e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.221 | 198.2 | 0.0484 | 0.63% | 12.000 | 1.03e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.499 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.751 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.486 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.171 | -152.7 | -0.0373 | -0.49% | 12.000 | -7.94e7 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.189 | 168.9 | 0.0412 | 0.54% | 12.000 | 8.78e7 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.033 | 29.4 | 0.0072 | 0.09% | 12.000 | 1.53e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.56 C), by the card's idle law | 19.181 | 17168.8 | 4.1916 | 54.95% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 15.98-23.98 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.077 | 12600.1 | 3.0762 | 40.33% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.008 | 7.6 | 0.0018 | 0.02% | 12.000 | 3.94e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `anchor_pi`, aifoundry1-c1 (E172, 3 passes)

Board in the window 43.257 W (95% 0.142); 1.1175e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **38.71 nJ an op, 9.450 pJ a MAC** with rest included; 2.01e+10 electrons an op from the 12 V input; idle bracket at 58.45 C, window at 59.08 C. Sum of the `+` lines 43.257 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.207 | 14502.8 | 3.5407 | 37.47% | 12.000 | 7.54e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.658 | 9537.1 | 2.3284 | 24.64% | 0.499 | 1.19e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.356 | 2108.5 | 0.5148 | 5.45% | 0.751 | 1.75e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.813 | 3411.7 | 0.8329 | 8.81% | 0.486 | 4.38e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.674 | 1497.7 | 0.3656 | 3.87% | 0.499 | 1.87e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.080 | 71.7 | 0.0175 | 0.19% | 0.751 | 5.96e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.017 | -15.0 | -0.0037 | -0.04% | 0.486 | -1.93e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.273 | 244.3 | 0.0596 | 0.63% | 12.000 | 1.27e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 7.078 | 6333.4 | 1.5462 | 16.36% | 0.499 | 7.92e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.038 | 34.1 | 0.0083 | 0.09% | 0.751 | 2.83e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.093 | 83.5 | 0.0204 | 0.22% | 0.486 | 1.07e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.805 | 720.1 | 0.1758 | 1.86% | 12.000 | 3.75e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.199 | 178.0 | 0.0435 | 0.46% | 12.000 | 9.26e7 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.974 | 871.4 | 0.2127 | 2.25% | 12.000 | 4.53e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.763 | 682.7 | 0.1667 | 1.76% | 12.000 | 3.55e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.104 | 93.0 | 0.0227 | 0.24% | 12.000 | 4.84e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.45 C), by the card's idle law | 19.125 | 17113.9 | 4.1782 | 44.21% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 15.94-23.91 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 13.909 | 12446.3 | 3.0386 | 32.15% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.013 | 11.6 | 0.0028 | 0.03% | 12.000 | 6.05e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.randn`, aifoundry1-c1 (E172, 3 passes)

Board in the window 59.745 W (95% 0.232); 1.1172e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **53.48 nJ an op, 13.056 pJ a MAC** with rest included; 2.78e+10 electrons an op from the 12 V input; idle bracket at 58.83 C, window at 61.30 C. Sum of the `+` lines 59.745 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.305 | 14595.2 | 3.5633 | 27.29% | 12.000 | 7.59e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.774 | 9644.4 | 2.3546 | 18.03% | 0.498 | 1.21e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.372 | 2123.2 | 0.5184 | 3.97% | 0.751 | 1.76e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.847 | 3443.8 | 0.8408 | 6.44% | 0.486 | 4.42e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.630 | 1458.7 | 0.3561 | 2.73% | 0.498 | 1.83e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.057 | 51.0 | 0.0124 | 0.10% | 0.751 | 4.23e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.060 | -53.9 | -0.0132 | -0.10% | 0.486 | -6.92e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.202 | 181.2 | 0.0442 | 0.34% | 12.000 | 9.42e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 19.808 | 17730.9 | 4.3288 | 33.15% | 0.498 | 2.22e11 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.173 | 155.0 | 0.0378 | 0.29% | 0.751 | 1.29e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.357 | 319.8 | 0.0781 | 0.60% | 0.486 | 4.11e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 3.506 | 3138.3 | 0.7662 | 5.87% | 12.000 | 1.63e9 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.773 | 691.7 | 0.1689 | 1.29% | 12.000 | 3.60e8 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 2.376 | 2126.6 | 0.5192 | 3.98% | 12.000 | 1.11e9 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 2.191 | 1961.0 | 0.4788 | 3.67% | 12.000 | 1.02e9 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 1.333 | 1192.9 | 0.2912 | 2.23% | 12.000 | 6.20e8 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.83 C), by the card's idle law | 19.330 | 17302.7 | 4.2243 | 32.35% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.11-24.16 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 13.969 | 12503.9 | 3.0527 | 23.38% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.025 | 22.2 | 0.0054 | 0.04% | 12.000 | 1.15e7 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.zeros`, aifoundry1-c1 (E172, 3 passes)

Board in the window 34.856 W (95% 0.364); 1.1173e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **31.20 nJ an op, 3.808 pJ a MAC** with rest included; 1.62e+10 electrons an op from the 12 V input; idle bracket at 58.56 C, window at 57.90 C. Sum of the `+` lines 34.856 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.235 | 14531.0 | 1.7738 | 46.58% | 12.000 | 7.56e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.810 | 9675.4 | 1.1811 | 31.01% | 0.499 | 1.21e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.364 | 2116.0 | 0.2583 | 6.78% | 0.751 | 1.76e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.827 | 3425.1 | 0.4181 | 10.98% | 0.486 | 4.40e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.542 | 1380.0 | 0.1685 | 4.42% | 0.499 | 1.73e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.068 | 60.9 | 0.0074 | 0.20% | 0.751 | 5.06e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.038 | -34.3 | -0.0042 | -0.11% | 0.486 | -4.40e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.254 | 227.5 | 0.0278 | 0.73% | 12.000 | 1.18e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.499 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.751 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.486 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.206 | -184.7 | -0.0225 | -0.59% | 12.000 | -9.61e7 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.186 | 166.9 | 0.0204 | 0.54% | 12.000 | 8.68e7 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.068 | 60.5 | 0.0074 | 0.19% | 12.000 | 3.15e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.56 C), by the card's idle law | 19.181 | 17167.6 | 2.0956 | 55.03% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 15.98-23.98 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.056 | 12579.9 | 1.5356 | 40.32% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.008 | 7.6 | 9.218e-04 | 0.02% | 12.000 | 3.93e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.randn`, aifoundry1-c1 (E172, 3 passes)

Board in the window 57.153 W (95% 0.474); 1.1173e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **51.15 nJ an op, 6.244 pJ a MAC** with rest included; 2.66e+10 electrons an op from the 12 V input; idle bracket at 58.49 C, window at 60.88 C. Sum of the `+` lines 57.153 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.229 | 14525.2 | 1.7731 | 28.40% | 12.000 | 7.55e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.821 | 9685.2 | 1.1823 | 18.93% | 0.498 | 1.21e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.367 | 2118.4 | 0.2586 | 4.14% | 0.751 | 1.76e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.831 | 3428.9 | 0.4186 | 6.70% | 0.486 | 4.40e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.503 | 1345.5 | 0.1642 | 2.63% | 0.498 | 1.69e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.066 | 58.7 | 0.0072 | 0.11% | 0.751 | 4.88e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.046 | -41.4 | -0.0051 | -0.08% | 0.486 | -5.32e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.253 | 226.4 | 0.0276 | 0.44% | 12.000 | 1.18e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 17.876 | 15999.5 | 1.9531 | 31.28% | 0.498 | 2.01e11 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.134 | 119.9 | 0.0146 | 0.23% | 0.751 | 9.97e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.333 | 298.4 | 0.0364 | 0.58% | 0.486 | 3.83e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 3.036 | 2717.3 | 0.3317 | 5.31% | 12.000 | 1.41e9 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.751 | 671.9 | 0.0820 | 1.31% | 12.000 | 3.49e8 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 2.147 | 1921.5 | 0.2346 | 3.76% | 12.000 | 9.99e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.967 | 1760.8 | 0.2149 | 3.44% | 12.000 | 9.16e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 1.142 | 1022.1 | 0.1248 | 2.00% | 12.000 | 5.32e8 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.49 C), by the card's idle law | 19.146 | 17136.2 | 2.0918 | 33.50% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 15.95-23.93 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.102 | 12621.4 | 1.5407 | 24.67% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.023 | 20.3 | 0.0025 | 0.04% | 12.000 | 1.06e7 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.zeros`, aifoundry1-c1 (E172, 3 passes)

Board in the window 35.521 W (95% 0.251); 1.9197e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **18.50 nJ an op, 1.129 pJ a MAC** with rest included; 9.62e+09 electrons an op from the 12 V input; idle bracket at 58.76 C, window at 58.12 C. Sum of the `+` lines 35.521 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.246 | 8462.9 | 0.5165 | 45.74% | 12.000 | 4.40e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.828 | 5640.7 | 0.3443 | 30.48% | 0.499 | 7.06e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.371 | 1234.9 | 0.0754 | 6.67% | 0.751 | 1.03e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.842 | 2001.6 | 0.1222 | 10.82% | 0.486 | 2.57e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.300 | 1198.0 | 0.0731 | 6.47% | 0.499 | 1.50e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.005 | 2.4 | 1.445e-04 | 0.01% | 0.751 | 1.97e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.047 | -24.7 | -0.0015 | -0.13% | 0.486 | -3.17e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.176 | 91.7 | 0.0056 | 0.50% | 12.000 | 4.77e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.499 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.751 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.486 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.198 | -103.4 | -0.0063 | -0.56% | 12.000 | -5.38e7 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.228 | 118.6 | 0.0072 | 0.64% | 12.000 | 6.17e7 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.052 | -26.9 | -0.0016 | -0.15% | 12.000 | -1.40e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.76 C), by the card's idle law | 19.288 | 10047.8 | 0.6133 | 54.30% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.07-24.11 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 13.999 | 7292.3 | 0.4451 | 39.41% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 4.6 | 2.786e-04 | 0.02% | 12.000 | 2.37e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.full`, aifoundry1-c1 (E172, 3 passes)

Board in the window 42.599 W (95% 0.398); 1.9199e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **22.19 nJ an op, 1.354 pJ a MAC** with rest included; 1.15e+10 electrons an op from the 12 V input; idle bracket at 58.62 C, window at 59.13 C. Sum of the `+` lines 42.599 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.288 | 8483.9 | 0.5178 | 38.24% | 12.000 | 4.41e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.805 | 5627.8 | 0.3435 | 25.36% | 0.499 | 7.04e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.361 | 1229.6 | 0.0750 | 5.54% | 0.751 | 1.02e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.829 | 1994.6 | 0.1217 | 8.99% | 0.486 | 2.56e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.250 | 1172.0 | 0.0715 | 5.28% | 0.499 | 1.47e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.015 | 7.7 | 4.679e-04 | 0.03% | 0.751 | 6.37e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.010 | -5.2 | -3.176e-04 | -0.02% | 0.486 | -6.68e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.152 | 79.1 | 0.0048 | 0.36% | 12.000 | 4.11e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 5.884 | 3065.0 | 0.1871 | 13.81% | 0.499 | 3.83e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.034 | 17.6 | 0.0011 | 0.08% | 0.751 | 1.47e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.077 | 40.1 | 0.0024 | 0.18% | 0.486 | 5.15e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.756 | 393.6 | 0.0240 | 1.77% | 12.000 | 2.05e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.158 | 82.5 | 0.0050 | 0.37% | 12.000 | 4.29e7 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.871 | 453.8 | 0.0277 | 2.05% | 12.000 | 2.36e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.635 | 330.9 | 0.0202 | 1.49% | 12.000 | 1.72e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.036 | 18.9 | 0.0012 | 0.09% | 12.000 | 9.83e6 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.62 C), by the card's idle law | 19.217 | 10009.3 | 0.6109 | 45.11% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.01-24.02 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.066 | 7326.6 | 0.4472 | 33.02% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.013 | 6.6 | 4.006e-04 | 0.03% | 12.000 | 3.41e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.zeros`, aifoundry3 (E78, 6 passes)

Board in the window 27.900 W (95% 0.025); 1.1208e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **24.89 nJ an op, 6.077 pJ a MAC** with rest included; 1.29e+10 electrons an op from the 12 V input; idle bracket at 58.80 C, window at 58.06 C. Sum of the `+` lines 27.900 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.986 | 11586.4 | 2.8287 | 46.54% | 12.000 | 6.03e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.266 | 7375.4 | 1.8006 | 29.63% | 0.522 | 8.82e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.224 | 1984.3 | 0.4844 | 7.97% | 0.698 | 1.77e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.587 | 2308.2 | 0.5635 | 9.27% | 0.484 | 2.98e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.712 | 1527.6 | 0.3730 | 6.14% | 0.522 | 1.83e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.077 | 68.3 | 0.0167 | 0.27% | 0.698 | 6.11e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.013 | -12.0 | -0.0029 | -0.05% | 0.484 | -1.55e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.215 | 192.0 | 0.0469 | 0.77% | 12.000 | 9.99e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.522 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.698 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.484 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.154 | -137.0 | -0.0334 | -0.55% | 12.000 | -7.12e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.309 | 275.9 | 0.0673 | 1.11% | 12.000 | 1.43e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.094 | -83.8 | -0.0205 | -0.34% | 12.000 | -4.36e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.80 C), by the card's idle law | 13.875 | 12380.0 | 3.0225 | 49.73% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.56-17.34 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.188 | 10874.3 | 2.6549 | 43.68% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.005 | 4.8 | 0.0012 | 0.02% | 12.000 | 2.51e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.ones`, aifoundry3 (E78, 6 passes)

Board in the window 36.528 W (95% 0.023); 1.1208e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **32.59 nJ an op, 7.956 pJ a MAC** with rest included; 1.7e+10 electrons an op from the 12 V input; idle bracket at 58.90 C, window at 59.20 C. Sum of the `+` lines 36.528 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 13.013 | 11609.7 | 2.8344 | 35.62% | 12.000 | 6.04e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.232 | 7344.3 | 1.7930 | 22.54% | 0.522 | 8.78e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.225 | 1985.0 | 0.4846 | 6.09% | 0.698 | 1.77e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.586 | 2307.6 | 0.5634 | 7.08% | 0.484 | 2.98e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.777 | 1585.5 | 0.3871 | 4.87% | 0.522 | 1.90e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.076 | 68.0 | 0.0166 | 0.21% | 0.698 | 6.08e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.011 | -9.5 | -0.0023 | -0.03% | 0.484 | -1.23e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.195 | 173.7 | 0.0424 | 0.53% | 12.000 | 9.03e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 7.016 | 6259.6 | 1.5282 | 19.21% | 0.522 | 7.48e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.044 | 38.9 | 0.0095 | 0.12% | 0.698 | 3.48e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.070 | 62.3 | 0.0152 | 0.19% | 0.484 | 8.03e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 1.245 | 1110.5 | 0.2711 | 3.41% | 12.000 | 5.78e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.061 | 54.3 | 0.0133 | 0.17% | 12.000 | 2.83e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 1.614 | 1439.9 | 0.3515 | 4.42% | 12.000 | 7.49e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.292 | 1152.9 | 0.2815 | 3.54% | 12.000 | 6.00e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.175 | -155.7 | -0.0380 | -0.48% | 12.000 | -8.10e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.90 C), by the card's idle law | 13.912 | 12412.3 | 3.0304 | 38.09% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.59-17.39 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.143 | 10834.2 | 2.6451 | 33.24% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 8.3 | 0.0020 | 0.03% | 12.000 | 4.30e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.neg_ones`, aifoundry3 (E78, 6 passes)

Board in the window 36.485 W (95% 0.138); 1.1210e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **32.55 nJ an op, 7.946 pJ a MAC** with rest included; 1.69e+10 electrons an op from the 12 V input; idle bracket at 58.75 C, window at 59.08 C. Sum of the `+` lines 36.485 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.918 | 11523.4 | 2.8133 | 35.41% | 12.000 | 5.99e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.315 | 7417.3 | 1.8109 | 22.79% | 0.522 | 8.87e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.222 | 1981.9 | 0.4839 | 6.09% | 0.698 | 1.77e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.587 | 2307.3 | 0.5633 | 7.09% | 0.484 | 2.98e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.637 | 1460.4 | 0.3566 | 4.49% | 0.522 | 1.75e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.078 | 69.2 | 0.0169 | 0.21% | 0.698 | 6.19e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.014 | -12.3 | -0.0030 | -0.04% | 0.484 | -1.59e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.276 | 246.2 | 0.0601 | 0.76% | 12.000 | 1.28e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 7.020 | 6262.5 | 1.5289 | 19.24% | 0.522 | 7.49e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.044 | 39.1 | 0.0096 | 0.12% | 0.698 | 3.50e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.061 | 54.6 | 0.0133 | 0.17% | 0.484 | 7.04e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 1.273 | 1135.8 | 0.2773 | 3.49% | 12.000 | 5.91e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.069 | 61.3 | 0.0150 | 0.19% | 12.000 | 3.19e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 1.586 | 1414.8 | 0.3454 | 4.35% | 12.000 | 7.36e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.290 | 1151.1 | 0.2810 | 3.54% | 12.000 | 5.99e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.037 | -32.8 | -0.0080 | -0.10% | 12.000 | -1.71e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.75 C), by the card's idle law | 13.854 | 12359.0 | 3.0173 | 37.97% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.55-17.32 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.186 | 10870.9 | 2.6540 | 33.40% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 8.2 | 0.0020 | 0.03% | 12.000 | 4.29e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.pi`, aifoundry3 (E78, 6 passes)

Board in the window 36.559 W (95% 0.119); 1.1210e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **32.61 nJ an op, 7.962 pJ a MAC** with rest included; 1.7e+10 electrons an op from the 12 V input; idle bracket at 58.55 C, window at 59.16 C. Sum of the `+` lines 36.559 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.938 | 11541.5 | 2.8177 | 35.39% | 12.000 | 6.00e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.308 | 7411.2 | 1.8094 | 22.72% | 0.522 | 8.86e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.215 | 1976.3 | 0.4825 | 6.06% | 0.698 | 1.77e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.580 | 2301.7 | 0.5619 | 7.06% | 0.484 | 2.97e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.612 | 1437.7 | 0.3510 | 4.41% | 0.522 | 1.72e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.083 | 74.2 | 0.0181 | 0.23% | 0.698 | 6.63e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.009 | -7.7 | -0.0019 | -0.02% | 0.484 | -9.99e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.243 | 216.7 | 0.0529 | 0.66% | 12.000 | 1.13e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 7.126 | 6356.8 | 1.5520 | 19.49% | 0.522 | 7.60e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.044 | 39.3 | 0.0096 | 0.12% | 0.698 | 3.52e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.062 | 54.9 | 0.0134 | 0.17% | 0.484 | 7.08e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 1.232 | 1099.0 | 0.2683 | 3.37% | 12.000 | 5.72e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.125 | 111.6 | 0.0272 | 0.34% | 12.000 | 5.80e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 1.602 | 1429.4 | 0.3490 | 4.38% | 12.000 | 7.43e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.310 | 1168.3 | 0.2852 | 3.58% | 12.000 | 6.08e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.127 | -113.7 | -0.0278 | -0.35% | 12.000 | -5.91e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.55 C), by the card's idle law | 13.778 | 12290.4 | 3.0006 | 37.69% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.48-17.22 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.264 | 10940.3 | 2.6710 | 33.55% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 8.3 | 0.0020 | 0.03% | 12.000 | 4.31e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `anchor_pi`, aifoundry3 (E78, 6 passes)

Board in the window 36.422 W (95% 0.073); 1.1208e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **32.50 nJ an op, 7.933 pJ a MAC** with rest included; 1.69e+10 electrons an op from the 12 V input; idle bracket at 58.30 C, window at 58.81 C. Sum of the `+` lines 36.422 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.987 | 11586.8 | 2.8288 | 35.66% | 12.000 | 6.03e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.174 | 7292.5 | 1.7804 | 22.44% | 0.522 | 8.72e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.203 | 1965.8 | 0.4799 | 6.05% | 0.698 | 1.76e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.559 | 2283.1 | 0.5574 | 7.03% | 0.484 | 2.94e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.720 | 1534.3 | 0.3746 | 4.72% | 0.522 | 1.83e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.099 | 88.3 | 0.0215 | 0.27% | 0.698 | 7.89e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | 0.016 | 14.3 | 0.0035 | 0.04% | 0.484 | 1.85e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.204 | 182.3 | 0.0445 | 0.56% | 12.000 | 9.48e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 7.131 | 6362.2 | 1.5533 | 19.58% | 0.522 | 7.61e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.020 | 17.7 | 0.0043 | 0.05% | 0.698 | 1.58e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.031 | 27.5 | 0.0067 | 0.08% | 0.484 | 3.54e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 1.174 | 1047.5 | 0.2557 | 3.22% | 12.000 | 5.45e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.105 | 93.3 | 0.0228 | 0.29% | 12.000 | 4.85e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 1.621 | 1446.0 | 0.3530 | 4.45% | 12.000 | 7.52e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.301 | 1160.3 | 0.2833 | 3.57% | 12.000 | 6.04e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.242 | -216.1 | -0.0528 | -0.67% | 12.000 | -1.12e8 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.30 C), by the card's idle law | 13.682 | 12207.1 | 2.9802 | 37.57% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.40-17.10 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.241 | 10921.0 | 2.6663 | 33.61% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 8.2 | 0.0020 | 0.03% | 12.000 | 4.28e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.randn`, aifoundry3 (E78, 6 passes)

Board in the window 53.270 W (95% 0.035); 1.1208e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **47.53 nJ an op, 11.604 pJ a MAC** with rest included; 2.47e+10 electrons an op from the 12 V input; idle bracket at 58.81 C, window at 61.16 C. Sum of the `+` lines 53.270 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.952 | 11555.5 | 2.8212 | 24.31% | 12.000 | 6.01e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.298 | 7403.5 | 1.8075 | 15.58% | 0.521 | 8.87e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.228 | 1988.0 | 0.4854 | 4.18% | 0.698 | 1.78e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.591 | 2311.5 | 0.5643 | 4.86% | 0.484 | 2.98e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.680 | 1498.7 | 0.3659 | 3.15% | 0.521 | 1.80e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.071 | 63.7 | 0.0156 | 0.13% | 0.698 | 5.70e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.018 | -16.4 | -0.0040 | -0.03% | 0.484 | -2.12e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.248 | 220.9 | 0.0539 | 0.46% | 12.000 | 1.15e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 19.781 | 17648.8 | 4.3088 | 37.13% | 0.521 | 2.11e11 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.125 | 111.3 | 0.0272 | 0.23% | 0.698 | 9.95e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.194 | 173.3 | 0.0423 | 0.36% | 0.484 | 2.23e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 4.638 | 4137.7 | 1.0102 | 8.71% | 12.000 | 2.15e9 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.484 | 431.4 | 0.1053 | 0.91% | 12.000 | 2.24e8 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 3.944 | 3519.0 | 0.8591 | 7.40% | 12.000 | 1.83e9 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 3.642 | 3249.8 | 0.7934 | 6.84% | 12.000 | 1.69e9 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.941 | 839.6 | 0.2050 | 1.77% | 12.000 | 4.37e8 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.81 C), by the card's idle law | 13.876 | 12380.1 | 3.0225 | 26.05% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.56-17.34 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.193 | 10878.5 | 2.6559 | 22.89% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.020 | 17.6 | 0.0043 | 0.04% | 12.000 | 9.14e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.zeros`, aifoundry3 (E78, 6 passes)

Board in the window 27.866 W (95% 0.058); 1.1208e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **24.86 nJ an op, 3.035 pJ a MAC** with rest included; 1.29e+10 electrons an op from the 12 V input; idle bracket at 58.75 C, window at 57.94 C. Sum of the `+` lines 27.866 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.991 | 11591.2 | 1.4149 | 46.62% | 12.000 | 6.03e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.244 | 7355.4 | 0.8979 | 29.58% | 0.522 | 8.79e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.221 | 1981.7 | 0.2419 | 7.97% | 0.698 | 1.77e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.583 | 2304.7 | 0.2813 | 9.27% | 0.484 | 2.97e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.718 | 1533.2 | 0.1872 | 6.17% | 0.522 | 1.83e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.077 | 68.5 | 0.0084 | 0.28% | 0.698 | 6.12e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.016 | -14.6 | -0.0018 | -0.06% | 0.484 | -1.88e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.213 | 190.4 | 0.0232 | 0.77% | 12.000 | 9.90e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.522 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.698 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.484 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.166 | -147.8 | -0.0180 | -0.59% | 12.000 | -7.69e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.309 | 276.1 | 0.0337 | 1.11% | 12.000 | 1.44e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.096 | -85.7 | -0.0105 | -0.34% | 12.000 | -4.46e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.75 C), by the card's idle law | 13.854 | 12361.3 | 1.5090 | 49.72% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.55-17.32 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.185 | 10871.7 | 1.3271 | 43.73% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.005 | 4.8 | 5.873e-04 | 0.02% | 12.000 | 2.50e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.ones`, aifoundry3 (E78, 6 passes)

Board in the window 36.523 W (95% 0.042); 1.1210e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **32.58 nJ an op, 3.977 pJ a MAC** with rest included; 1.69e+10 electrons an op from the 12 V input; idle bracket at 58.77 C, window at 59.09 C. Sum of the `+` lines 36.523 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.969 | 11569.0 | 1.4122 | 35.51% | 12.000 | 6.02e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.306 | 7409.0 | 0.9044 | 22.74% | 0.522 | 8.86e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.223 | 1982.8 | 0.2420 | 6.09% | 0.698 | 1.77e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.585 | 2306.2 | 0.2815 | 7.08% | 0.484 | 2.97e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.649 | 1471.2 | 0.1796 | 4.52% | 0.522 | 1.76e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.071 | 63.1 | 0.0077 | 0.19% | 0.698 | 5.64e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.024 | -21.8 | -0.0027 | -0.07% | 0.484 | -2.82e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.237 | 211.7 | 0.0258 | 0.65% | 12.000 | 1.10e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 7.105 | 6337.7 | 0.7736 | 19.45% | 0.522 | 7.58e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.054 | 48.5 | 0.0059 | 0.15% | 0.698 | 4.34e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.081 | 71.9 | 0.0088 | 0.22% | 0.484 | 9.27e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 1.201 | 1071.7 | 0.1308 | 3.29% | 12.000 | 5.57e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.067 | 59.6 | 0.0073 | 0.18% | 12.000 | 3.10e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 1.606 | 1432.8 | 0.1749 | 4.40% | 12.000 | 7.45e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.312 | 1170.2 | 0.1428 | 3.59% | 12.000 | 6.09e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.167 | -149.3 | -0.0182 | -0.46% | 12.000 | -7.77e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.77 C), by the card's idle law | 13.861 | 12364.6 | 1.5093 | 37.95% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.55-17.33 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.222 | 10902.4 | 1.3309 | 33.46% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 8.3 | 0.0010 | 0.03% | 12.000 | 4.30e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.neg_ones`, aifoundry3 (E78, 6 passes)

Board in the window 36.513 W (95% 0.115); 1.1208e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **32.58 nJ an op, 3.977 pJ a MAC** with rest included; 1.69e+10 electrons an op from the 12 V input; idle bracket at 58.73 C, window at 59.18 C. Sum of the `+` lines 36.513 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.976 | 11577.0 | 1.4132 | 35.54% | 12.000 | 6.02e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.284 | 7391.2 | 0.9022 | 22.69% | 0.522 | 8.84e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.227 | 1986.7 | 0.2425 | 6.10% | 0.698 | 1.78e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.583 | 2304.1 | 0.2813 | 7.07% | 0.484 | 2.97e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.688 | 1506.4 | 0.1839 | 4.62% | 0.522 | 1.80e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.077 | 68.7 | 0.0084 | 0.21% | 0.698 | 6.14e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.010 | -8.7 | -0.0011 | -0.03% | 0.484 | -1.12e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.222 | 198.4 | 0.0242 | 0.61% | 12.000 | 1.03e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 6.996 | 6241.4 | 0.7619 | 19.16% | 0.522 | 7.46e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.043 | 38.5 | 0.0047 | 0.12% | 0.698 | 3.44e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.062 | 55.6 | 0.0068 | 0.17% | 0.484 | 7.17e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 1.273 | 1135.8 | 0.1386 | 3.49% | 12.000 | 5.91e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.091 | 81.0 | 0.0099 | 0.25% | 12.000 | 4.21e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 1.592 | 1420.6 | 0.1734 | 4.36% | 12.000 | 7.39e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.286 | 1147.6 | 0.1401 | 3.52% | 12.000 | 5.97e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.097 | -86.4 | -0.0105 | -0.27% | 12.000 | -4.49e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.73 C), by the card's idle law | 13.848 | 12355.0 | 1.5082 | 37.93% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.54-17.31 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.222 | 10904.0 | 1.3311 | 33.47% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 8.3 | 0.0010 | 0.03% | 12.000 | 4.30e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.randn`, aifoundry3 (E78, 6 passes)

Board in the window 50.596 W (95% 0.021); 1.1208e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **45.14 nJ an op, 5.510 pJ a MAC** with rest included; 2.35e+10 electrons an op from the 12 V input; idle bracket at 58.70 C, window at 60.80 C. Sum of the `+` lines 50.596 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.958 | 11560.7 | 1.4112 | 25.61% | 12.000 | 6.01e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.306 | 7411.0 | 0.9047 | 16.42% | 0.521 | 8.88e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.225 | 1985.1 | 0.2423 | 4.40% | 0.698 | 1.78e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.586 | 2307.3 | 0.2816 | 5.11% | 0.484 | 2.98e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.648 | 1470.1 | 0.1795 | 3.26% | 0.521 | 1.76e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.073 | 64.8 | 0.0079 | 0.14% | 0.698 | 5.80e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.020 | -18.0 | -0.0022 | -0.04% | 0.484 | -2.31e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.244 | 217.8 | 0.0266 | 0.48% | 12.000 | 1.13e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 17.761 | 15846.8 | 1.9344 | 35.10% | 0.521 | 1.90e11 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.110 | 98.5 | 0.0120 | 0.22% | 0.698 | 8.81e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.175 | 156.2 | 0.0191 | 0.35% | 0.484 | 2.01e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 4.098 | 3656.0 | 0.4463 | 8.10% | 12.000 | 1.90e9 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.432 | 385.1 | 0.0470 | 0.85% | 12.000 | 2.00e8 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 3.566 | 3181.7 | 0.3884 | 7.05% | 12.000 | 1.65e9 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 3.271 | 2918.2 | 0.3562 | 6.46% | 12.000 | 1.52e9 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.776 | 692.1 | 0.0845 | 1.53% | 12.000 | 3.60e8 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.70 C), by the card's idle law | 13.835 | 12343.7 | 1.5068 | 27.34% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.53-17.29 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.240 | 10920.4 | 1.3331 | 24.19% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.018 | 15.9 | 0.0019 | 0.04% | 12.000 | 8.25e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.zeros`, aifoundry3 (E78, 6 passes)

Board in the window 28.543 W (95% 0.024); 1.9255e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **14.82 nJ an op, 0.905 pJ a MAC** with rest included; 7.71e+09 electrons an op from the 12 V input; idle bracket at 58.74 C, window at 58.22 C. Sum of the `+` lines 28.543 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 13.015 | 6759.3 | 0.4126 | 45.60% | 12.000 | 3.52e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.221 | 4269.3 | 0.2606 | 28.80% | 0.522 | 5.10e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.222 | 1153.7 | 0.0704 | 7.78% | 0.698 | 1.03e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.585 | 1342.5 | 0.0819 | 9.06% | 0.484 | 1.73e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.327 | 1208.5 | 0.0738 | 8.15% | 0.522 | 1.45e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.006 | 3.1 | 1.887e-04 | 0.02% | 0.698 | 2.76e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.008 | -4.2 | -2.590e-04 | -0.03% | 0.484 | -5.47e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.284 | 147.3 | 0.0090 | 0.99% | 12.000 | 7.66e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.522 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.698 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.484 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.108 | -56.2 | -0.0034 | -0.38% | 12.000 | -2.92e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.419 | 217.6 | 0.0133 | 1.47% | 12.000 | 1.13e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.135 | -70.3 | -0.0043 | -0.47% | 12.000 | -3.66e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.74 C), by the card's idle law | 13.851 | 7193.3 | 0.4390 | 48.53% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.54-17.31 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.192 | 6331.4 | 0.3864 | 42.71% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.006 | 2.9 | 1.793e-04 | 0.02% | 12.000 | 1.53e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.ones`, aifoundry3 (E78, 6 passes)

Board in the window 30.246 W (95% 0.075); 1.9255e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **15.71 nJ an op, 0.959 pJ a MAC** with rest included; 8.17e+09 electrons an op from the 12 V input; idle bracket at 58.87 C, window at 59.00 C. Sum of the `+` lines 30.246 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 13.023 | 6763.3 | 0.4128 | 43.05% | 12.000 | 3.52e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.233 | 4275.7 | 0.2610 | 27.22% | 0.522 | 5.11e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.226 | 1156.1 | 0.0706 | 7.36% | 0.698 | 1.03e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.593 | 1346.5 | 0.0822 | 8.57% | 0.484 | 1.74e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.340 | 1215.4 | 0.0742 | 7.74% | 0.522 | 1.45e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 6.839e-04 | 0.4 | 2.168e-05 | 0.00% | 0.698 | 3.18e6 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.019 | -9.8 | -5.992e-04 | -0.06% | 0.484 | -1.27e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.267 | 138.6 | 0.0085 | 0.88% | 12.000 | 7.21e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 1.352 | 702.1 | 0.0429 | 4.47% | 0.522 | 8.40e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.012 | 6.2 | 3.813e-04 | 0.04% | 0.698 | 5.59e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.020 | 10.2 | 6.197e-04 | 0.06% | 0.484 | 1.31e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.173 | 89.6 | 0.0055 | 0.57% | 12.000 | 4.66e7 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.027 | 14.2 | 8.691e-04 | 0.09% | 12.000 | 7.41e6 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.669 | 347.4 | 0.0212 | 2.21% | 12.000 | 1.81e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.251 | 130.3 | 0.0080 | 0.83% | 12.000 | 6.78e7 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.230 | -119.2 | -0.0073 | -0.76% | 12.000 | -6.20e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.87 C), by the card's idle law | 13.899 | 7218.6 | 0.4406 | 45.95% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.58-17.37 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.175 | 6322.9 | 0.3859 | 40.25% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.006 | 3.3 | 2.014e-04 | 0.02% | 12.000 | 1.72e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.neg_ones`, aifoundry3 (E78, 6 passes)

Board in the window 30.280 W (95% 0.202); 1.9257e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **15.72 nJ an op, 0.960 pJ a MAC** with rest included; 8.18e+09 electrons an op from the 12 V input; idle bracket at 58.57 C, window at 58.81 C. Sum of the `+` lines 30.280 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 12.921 | 6710.0 | 0.4095 | 42.67% | 12.000 | 3.49e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.329 | 4325.1 | 0.2640 | 27.51% | 0.522 | 5.17e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.224 | 1155.0 | 0.0705 | 7.35% | 0.698 | 1.03e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.581 | 1340.5 | 0.0818 | 8.53% | 0.484 | 1.73e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.187 | 1135.9 | 0.0693 | 7.22% | 0.522 | 1.36e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.004 | 1.8 | 1.125e-04 | 0.01% | 0.698 | 1.65e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.007 | -3.5 | -2.159e-04 | -0.02% | 0.484 | -4.56e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.366 | 190.0 | 0.0116 | 1.21% | 12.000 | 9.88e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 1.445 | 750.6 | 0.0458 | 4.77% | 0.522 | 8.97e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.007 | 3.4 | 2.094e-04 | 0.02% | 0.698 | 3.07e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.010 | 5.2 | 3.164e-04 | 0.03% | 0.484 | 6.68e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.163 | 84.5 | 0.0052 | 0.54% | 12.000 | 4.39e7 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.050 | 25.8 | 0.0016 | 0.16% | 12.000 | 1.34e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.659 | 342.1 | 0.0209 | 2.18% | 12.000 | 1.78e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.265 | 137.5 | 0.0084 | 0.87% | 12.000 | 7.15e7 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.130 | -67.7 | -0.0041 | -0.43% | 12.000 | -3.52e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.57 C), by the card's idle law | 13.784 | 7157.9 | 0.4369 | 45.52% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.49-17.23 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.272 | 6372.7 | 0.3890 | 40.53% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.006 | 3.3 | 2.018e-04 | 0.02% | 12.000 | 1.72e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.full`, aifoundry3 (E78, 6 passes)

Board in the window 35.785 W (95% 0.046); 1.9257e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **18.58 nJ an op, 1.134 pJ a MAC** with rest included; 9.67e+09 electrons an op from the 12 V input; idle bracket at 58.57 C, window at 59.01 C. Sum of the `+` lines 35.785 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 13.013 | 6757.8 | 0.4125 | 36.36% | 12.000 | 3.51e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 8.209 | 4263.0 | 0.2602 | 22.94% | 0.522 | 5.10e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.220 | 1152.8 | 0.0704 | 6.20% | 0.698 | 1.03e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 2.579 | 1339.2 | 0.0817 | 7.21% | 0.484 | 1.73e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.314 | 1201.5 | 0.0733 | 6.47% | 0.522 | 1.44e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.007 | 3.8 | 2.331e-04 | 0.02% | 0.698 | 3.42e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.002 | -1.3 | -7.855e-05 | -0.01% | 0.484 | -1.66e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.276 | 143.2 | 0.0087 | 0.77% | 12.000 | 7.45e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 5.933 | 3081.0 | 0.1881 | 16.58% | 0.522 | 3.68e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.034 | 17.7 | 0.0011 | 0.10% | 0.698 | 1.59e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.053 | 27.5 | 0.0017 | 0.15% | 0.484 | 3.54e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 1.060 | 550.7 | 0.0336 | 2.96% | 12.000 | 2.86e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.089 | 46.3 | 0.0028 | 0.25% | 12.000 | 2.41e7 | modelled (the footing slope k = 0.2056 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 1.509 | 783.7 | 0.0478 | 4.22% | 12.000 | 4.08e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.091 | 566.4 | 0.0346 | 3.05% | 12.000 | 2.95e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.173 | -89.8 | -0.0055 | -0.48% | 12.000 | -4.67e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.57 C), by the card's idle law | 13.786 | 7159.0 | 0.4370 | 38.52% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 11.49-17.23 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 12.235 | 6353.9 | 0.3878 | 34.19% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 4.6 | 2.819e-04 | 0.02% | 12.000 | 2.40e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.zeros`, aifoundry1-c1 (E82, 7 passes)

Board in the window 34.928 W (95% 0.048); 1.1209e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **31.16 nJ an op, 7.608 pJ a MAC** with rest included; 1.62e+10 electrons an op from the 12 V input; idle bracket at 58.67 C, window at 58.00 C. Sum of the `+` lines 34.928 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.331 | 14569.9 | 3.5571 | 46.76% | 12.000 | 7.58e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.742 | 9583.8 | 2.3398 | 30.76% | 0.499 | 1.20e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.344 | 2091.7 | 0.5107 | 6.71% | 0.751 | 1.74e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.835 | 3421.1 | 0.8352 | 10.98% | 0.486 | 4.39e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.659 | 1480.3 | 0.3614 | 4.75% | 0.499 | 1.85e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.078 | 69.2 | 0.0169 | 0.22% | 0.751 | 5.75e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.033 | -29.2 | -0.0071 | -0.09% | 0.486 | -3.75e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.182 | 162.2 | 0.0396 | 0.52% | 12.000 | 8.44e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.499 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.751 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.486 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.210 | -187.7 | -0.0458 | -0.60% | 12.000 | -9.76e7 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.205 | 182.7 | 0.0446 | 0.59% | 12.000 | 9.50e7 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.023 | -20.4 | -0.0050 | -0.07% | 12.000 | -1.06e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.67 C), by the card's idle law | 19.243 | 17168.2 | 4.1915 | 55.09% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.04-24.05 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.009 | 12498.4 | 3.0514 | 40.11% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.008 | 7.6 | 0.0018 | 0.02% | 12.000 | 3.93e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.ones`, aifoundry1-c1 (E82, 7 passes)

Board in the window 43.287 W (95% 0.165); 1.1210e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **38.61 nJ an op, 9.427 pJ a MAC** with rest included; 2.01e+10 electrons an op from the 12 V input; idle bracket at 58.60 C, window at 59.36 C. Sum of the `+` lines 43.287 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.201 | 14452.0 | 3.5283 | 37.43% | 12.000 | 7.52e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.863 | 9690.3 | 2.3658 | 25.10% | 0.499 | 1.21e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.373 | 2116.6 | 0.5168 | 5.48% | 0.751 | 1.76e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.836 | 3421.9 | 0.8354 | 8.86% | 0.486 | 4.39e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.498 | 1336.0 | 0.3262 | 3.46% | 0.499 | 1.67e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.048 | 43.0 | 0.0105 | 0.11% | 0.751 | 3.58e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.042 | -37.4 | -0.0091 | -0.10% | 0.486 | -4.80e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.301 | 268.6 | 0.0656 | 0.70% | 12.000 | 1.40e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 6.949 | 6198.6 | 1.5133 | 16.05% | 0.499 | 7.75e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.071 | 63.1 | 0.0154 | 0.16% | 0.751 | 5.24e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.119 | 106.0 | 0.0259 | 0.27% | 0.486 | 1.36e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.832 | 742.2 | 0.1812 | 1.92% | 12.000 | 3.86e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.239 | 213.3 | 0.0521 | 0.55% | 12.000 | 1.11e8 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.943 | 841.3 | 0.2054 | 2.18% | 12.000 | 4.38e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.773 | 689.2 | 0.1683 | 1.78% | 12.000 | 3.58e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.190 | 169.5 | 0.0414 | 0.44% | 12.000 | 8.82e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.60 C), by the card's idle law | 19.205 | 17131.8 | 4.1826 | 44.37% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.00-24.01 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.068 | 12549.0 | 3.0637 | 32.50% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.013 | 11.6 | 0.0028 | 0.03% | 12.000 | 6.04e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.neg_ones`, aifoundry1-c1 (E82, 7 passes)

Board in the window 43.250 W (95% 0.215); 1.1211e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **38.58 nJ an op, 9.419 pJ a MAC** with rest included; 2.01e+10 electrons an op from the 12 V input; idle bracket at 58.54 C, window at 59.34 C. Sum of the `+` lines 43.250 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.230 | 14477.3 | 3.5345 | 37.53% | 12.000 | 7.53e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.738 | 9578.5 | 2.3385 | 24.83% | 0.499 | 1.20e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.359 | 2104.4 | 0.5138 | 5.45% | 0.751 | 1.75e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.823 | 3409.7 | 0.8325 | 8.84% | 0.486 | 4.38e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.648 | 1470.3 | 0.3589 | 3.81% | 0.499 | 1.84e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.063 | 56.4 | 0.0138 | 0.15% | 0.751 | 4.69e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.014 | -12.3 | -0.0030 | -0.03% | 0.486 | -1.59e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.289 | 258.0 | 0.0630 | 0.67% | 12.000 | 1.34e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 6.935 | 6185.5 | 1.5101 | 16.03% | 0.499 | 7.74e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.058 | 52.1 | 0.0127 | 0.14% | 0.751 | 4.33e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.095 | 85.0 | 0.0207 | 0.22% | 0.486 | 1.09e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.776 | 692.0 | 0.1689 | 1.79% | 12.000 | 3.60e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.248 | 221.6 | 0.0541 | 0.57% | 12.000 | 1.15e8 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.959 | 855.8 | 0.2089 | 2.22% | 12.000 | 4.45e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.760 | 677.6 | 0.1654 | 1.76% | 12.000 | 3.52e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.106 | 94.1 | 0.0230 | 0.24% | 12.000 | 4.90e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.54 C), by the card's idle law | 19.175 | 17103.5 | 4.1757 | 44.33% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 15.98-23.97 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 13.976 | 12466.5 | 3.0436 | 32.31% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.013 | 11.6 | 0.0028 | 0.03% | 12.000 | 6.03e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.pi`, aifoundry1-c1 (E82, 7 passes)

Board in the window 43.440 W (95% 0.160); 1.1209e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **38.76 nJ an op, 9.462 pJ a MAC** with rest included; 2.02e+10 electrons an op from the 12 V input; idle bracket at 58.74 C, window at 59.36 C. Sum of the `+` lines 43.440 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 17.379 | 15505.5 | 3.7855 | 40.01% | 12.000 | 8.06e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 9.733 | 8683.5 | 2.1200 | 22.41% | 0.499 | 1.09e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.364 | 2109.4 | 0.5150 | 5.44% | 0.751 | 1.75e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.843 | 3428.3 | 0.8370 | 8.85% | 0.486 | 4.40e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.677 | 2388.8 | 0.5832 | 6.16% | 0.499 | 2.99e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.043 | 38.6 | 0.0094 | 0.10% | 0.751 | 3.20e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.045 | -40.0 | -0.0098 | -0.10% | 0.486 | -5.13e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | -0.850 | -758.0 | -0.1851 | -1.96% | 12.000 | -3.94e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 7.090 | 6325.5 | 1.5443 | 16.32% | 0.499 | 7.91e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.083 | 73.6 | 0.0180 | 0.19% | 0.751 | 6.12e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.123 | 109.8 | 0.0268 | 0.28% | 0.486 | 1.41e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.804 | 717.5 | 0.1752 | 1.85% | 12.000 | 3.73e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.195 | 173.8 | 0.0424 | 0.45% | 12.000 | 9.04e7 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 1.082 | 965.4 | 0.2357 | 2.49% | 12.000 | 5.02e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.794 | 708.6 | 0.1730 | 1.83% | 12.000 | 3.69e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -1.127 | -1005.8 | -0.2456 | -2.60% | 12.000 | -5.23e8 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.74 C), by the card's idle law | 19.281 | 17202.5 | 4.1998 | 44.39% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.07-24.10 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.038 | 12524.2 | 3.0577 | 32.32% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.013 | 11.7 | 0.0029 | 0.03% | 12.000 | 6.08e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `anchor_pi`, aifoundry1-c1 (E82, 7 passes)

Board in the window 43.338 W (95% 0.090); 1.1209e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **38.66 nJ an op, 9.439 pJ a MAC** with rest included; 2.01e+10 electrons an op from the 12 V input; idle bracket at 58.44 C, window at 59.21 C. Sum of the `+` lines 43.338 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.194 | 14447.5 | 3.5272 | 37.37% | 12.000 | 7.51e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.743 | 9584.5 | 2.3400 | 24.79% | 0.499 | 1.20e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.356 | 2102.0 | 0.5132 | 5.44% | 0.751 | 1.75e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.854 | 3438.0 | 0.8394 | 8.89% | 0.486 | 4.42e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.584 | 1413.5 | 0.3451 | 3.66% | 0.499 | 1.77e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.074 | 66.0 | 0.0161 | 0.17% | 0.751 | 5.48e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.057 | -51.3 | -0.0125 | -0.13% | 0.486 | -6.59e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.285 | 254.4 | 0.0621 | 0.66% | 12.000 | 1.32e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 7.094 | 6328.5 | 1.5450 | 16.37% | 0.499 | 7.92e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.063 | 56.0 | 0.0137 | 0.14% | 0.751 | 4.65e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.101 | 89.8 | 0.0219 | 0.23% | 0.486 | 1.15e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.806 | 719.4 | 0.1756 | 1.86% | 12.000 | 3.74e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.242 | 215.6 | 0.0526 | 0.56% | 12.000 | 1.12e8 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.969 | 864.9 | 0.2112 | 2.24% | 12.000 | 4.50e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.779 | 695.3 | 0.1697 | 1.80% | 12.000 | 3.62e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.122 | 108.9 | 0.0266 | 0.28% | 12.000 | 5.66e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.44 C), by the card's idle law | 19.121 | 17059.0 | 4.1648 | 44.12% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 15.93-23.90 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.026 | 12513.0 | 3.0549 | 32.36% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.013 | 11.6 | 0.0028 | 0.03% | 12.000 | 6.05e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp32.randn`, aifoundry1-c1 (E82, 7 passes)

Board in the window 59.791 W (95% 0.053); 1.1209e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **53.34 nJ an op, 13.022 pJ a MAC** with rest included; 2.77e+10 electrons an op from the 12 V input; idle bracket at 58.85 C, window at 61.34 C. Sum of the `+` lines 59.791 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.284 | 14527.1 | 3.5466 | 27.24% | 12.000 | 7.56e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.813 | 9646.7 | 2.3551 | 18.09% | 0.498 | 1.21e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.369 | 2113.6 | 0.5160 | 3.96% | 0.751 | 1.76e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.845 | 3430.0 | 0.8374 | 6.43% | 0.486 | 4.41e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.637 | 1460.7 | 0.3566 | 2.74% | 0.498 | 1.83e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.050 | 44.3 | 0.0108 | 0.08% | 0.751 | 3.68e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.041 | -36.7 | -0.0090 | -0.07% | 0.486 | -4.72e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.248 | 221.4 | 0.0541 | 0.42% | 12.000 | 1.15e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 19.822 | 17682.9 | 4.3171 | 33.15% | 0.498 | 2.22e11 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.170 | 151.7 | 0.0370 | 0.28% | 0.751 | 1.26e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.342 | 304.9 | 0.0744 | 0.57% | 0.486 | 3.92e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 3.470 | 3095.6 | 0.7558 | 5.80% | 12.000 | 1.61e9 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.782 | 697.3 | 0.1702 | 1.31% | 12.000 | 3.63e8 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 2.373 | 2117.0 | 0.5168 | 3.97% | 12.000 | 1.10e9 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 2.187 | 1951.3 | 0.4764 | 3.66% | 12.000 | 1.01e9 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 1.345 | 1200.1 | 0.2930 | 2.25% | 12.000 | 6.24e8 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.85 C), by the card's idle law | 19.339 | 17252.7 | 4.2121 | 32.35% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.12-24.17 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 13.972 | 12464.6 | 3.0431 | 23.37% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.025 | 22.1 | 0.0054 | 0.04% | 12.000 | 1.15e7 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.zeros`, aifoundry1-c1 (E82, 7 passes)

Board in the window 34.963 W (95% 0.053); 1.1208e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **31.19 nJ an op, 3.808 pJ a MAC** with rest included; 1.62e+10 electrons an op from the 12 V input; idle bracket at 58.80 C, window at 57.98 C. Sum of the `+` lines 34.963 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.288 | 14531.9 | 1.7739 | 46.59% | 12.000 | 7.56e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.790 | 9626.5 | 1.1751 | 30.86% | 0.499 | 1.20e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.364 | 2109.2 | 0.2575 | 6.76% | 0.751 | 1.75e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.840 | 3426.1 | 0.4182 | 10.98% | 0.486 | 4.40e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.661 | 1482.1 | 0.1809 | 4.75% | 0.499 | 1.85e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.095 | 84.6 | 0.0103 | 0.27% | 0.751 | 7.03e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.032 | -29.0 | -0.0035 | -0.09% | 0.486 | -3.72e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.215 | 191.6 | 0.0234 | 0.61% | 12.000 | 9.97e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.499 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.751 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.486 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.257 | -229.7 | -0.0280 | -0.74% | 12.000 | -1.19e8 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.214 | 191.2 | 0.0233 | 0.61% | 12.000 | 9.95e7 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 4.144e-04 | 0.4 | 4.513e-05 | 0.00% | 12.000 | 1.92e5 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.80 C), by the card's idle law | 19.313 | 17231.0 | 2.1034 | 55.24% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.09-24.14 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 13.969 | 12462.7 | 1.5213 | 39.95% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.008 | 7.6 | 9.245e-04 | 0.02% | 12.000 | 3.94e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.ones`, aifoundry1-c1 (E82, 7 passes)

Board in the window 43.357 W (95% 0.134); 1.1210e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **38.68 nJ an op, 4.721 pJ a MAC** with rest included; 2.01e+10 electrons an op from the 12 V input; idle bracket at 58.87 C, window at 59.57 C. Sum of the `+` lines 43.357 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.258 | 14503.6 | 1.7705 | 37.50% | 12.000 | 7.54e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.884 | 9709.0 | 1.1852 | 25.10% | 0.499 | 1.21e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.376 | 2119.6 | 0.2587 | 5.48% | 0.751 | 1.76e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.850 | 3434.4 | 0.4192 | 8.88% | 0.486 | 4.41e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.580 | 1409.3 | 0.1720 | 3.64% | 0.499 | 1.76e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.127 | 113.0 | 0.0138 | 0.29% | 0.751 | 9.39e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.052 | -46.6 | -0.0057 | -0.12% | 0.486 | -5.98e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.196 | 175.0 | 0.0214 | 0.45% | 12.000 | 9.10e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 6.886 | 6143.0 | 0.7499 | 15.88% | 0.499 | 7.68e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | -0.005 | -4.3 | -5.232e-04 | -0.01% | 0.751 | -3.56e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.130 | 115.5 | 0.0141 | 0.30% | 0.486 | 1.48e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.909 | 811.2 | 0.0990 | 2.10% | 12.000 | 4.22e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.219 | 195.3 | 0.0238 | 0.50% | 12.000 | 1.02e8 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.947 | 844.5 | 0.1031 | 2.18% | 12.000 | 4.39e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.728 | 649.0 | 0.0792 | 1.68% | 12.000 | 3.38e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.159 | 141.6 | 0.0173 | 0.37% | 12.000 | 7.37e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.87 C), by the card's idle law | 19.350 | 17262.0 | 2.1072 | 44.63% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.13-24.19 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.017 | 12504.6 | 1.5264 | 32.33% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.013 | 11.6 | 0.0014 | 0.03% | 12.000 | 6.06e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.neg_ones`, aifoundry1-c1 (E82, 7 passes)

Board in the window 43.382 W (95% 0.088); 1.1210e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **38.70 nJ an op, 4.724 pJ a MAC** with rest included; 2.01e+10 electrons an op from the 12 V input; idle bracket at 58.84 C, window at 59.29 C. Sum of the `+` lines 43.382 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.239 | 14486.6 | 1.7684 | 37.43% | 12.000 | 7.53e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.863 | 9690.9 | 1.1830 | 25.04% | 0.499 | 1.21e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.390 | 2132.2 | 0.2603 | 5.51% | 0.751 | 1.77e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.849 | 3433.9 | 0.4192 | 8.87% | 0.486 | 4.41e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.600 | 1427.7 | 0.1743 | 3.69% | 0.499 | 1.79e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.043 | 38.0 | 0.0046 | 0.10% | 0.751 | 3.15e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.051 | -45.3 | -0.0055 | -0.12% | 0.486 | -5.82e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.296 | 264.2 | 0.0322 | 0.68% | 12.000 | 1.37e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 6.982 | 6228.6 | 0.7603 | 16.09% | 0.499 | 7.79e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.050 | 44.4 | 0.0054 | 0.11% | 0.751 | 3.69e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.124 | 110.9 | 0.0135 | 0.29% | 0.486 | 1.42e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.854 | 761.9 | 0.0930 | 1.97% | 12.000 | 3.96e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.142 | 126.2 | 0.0154 | 0.33% | 12.000 | 6.57e7 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.942 | 840.3 | 0.1026 | 2.17% | 12.000 | 4.37e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.766 | 683.2 | 0.0834 | 1.77% | 12.000 | 3.55e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.208 | 185.8 | 0.0227 | 0.48% | 12.000 | 9.66e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.84 C), by the card's idle law | 19.335 | 17248.3 | 2.1055 | 44.57% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.11-24.17 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.007 | 12495.3 | 1.5253 | 32.29% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.013 | 11.7 | 0.0014 | 0.03% | 12.000 | 6.06e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `fp16.randn`, aifoundry1-c1 (E82, 7 passes)

Board in the window 57.192 W (95% 0.111); 1.1207e9 ops/s measured (nominal 1.1253e9 from 546.001 cycles an op); **51.03 nJ an op, 6.229 pJ a MAC** with rest included; 2.65e+10 electrons an op from the 12 V input; idle bracket at 58.76 C, window at 60.91 C. Sum of the `+` lines 57.192 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.220 | 14472.3 | 1.7666 | 28.36% | 12.000 | 7.53e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.833 | 9665.8 | 1.1799 | 18.94% | 0.498 | 1.21e11 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.366 | 2111.1 | 0.2577 | 4.14% | 0.751 | 1.75e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.859 | 3443.3 | 0.4203 | 6.75% | 0.486 | 4.42e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 1.608 | 1434.6 | 0.1751 | 2.81% | 0.498 | 1.80e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.093 | 83.2 | 0.0102 | 0.16% | 0.751 | 6.92e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.053 | -47.4 | -0.0058 | -0.09% | 0.486 | -6.09e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.277 | 247.0 | 0.0302 | 0.48% | 12.000 | 1.28e8 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 17.956 | 16021.0 | 1.9557 | 31.40% | 0.498 | 2.01e11 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.107 | 95.5 | 0.0117 | 0.19% | 0.751 | 7.94e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.294 | 262.0 | 0.0320 | 0.51% | 0.486 | 3.36e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 2.960 | 2640.7 | 0.3223 | 5.17% | 12.000 | 1.37e9 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.674 | 601.0 | 0.0734 | 1.18% | 12.000 | 3.13e8 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 2.157 | 1924.2 | 0.2349 | 3.77% | 12.000 | 1.00e9 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 1.953 | 1742.3 | 0.2127 | 3.41% | 12.000 | 9.06e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 1.080 | 963.5 | 0.1176 | 1.89% | 12.000 | 5.01e8 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.76 C), by the card's idle law | 19.292 | 17213.2 | 2.1012 | 33.73% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.08-24.11 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 13.986 | 12479.3 | 1.5234 | 24.45% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.023 | 20.3 | 0.0025 | 0.04% | 12.000 | 1.05e7 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.zeros`, aifoundry1-c1 (E82, 7 passes)

Board in the window 35.550 W (95% 0.058); 1.9248e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **18.47 nJ an op, 1.127 pJ a MAC** with rest included; 9.61e+09 electrons an op from the 12 V input; idle bracket at 58.74 C, window at 58.17 C. Sum of the `+` lines 35.550 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.221 | 8427.2 | 0.5144 | 45.63% | 12.000 | 4.38e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.827 | 5624.7 | 0.3433 | 30.45% | 0.499 | 7.04e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.370 | 1231.2 | 0.0751 | 6.67% | 0.751 | 1.02e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.861 | 2005.8 | 0.1224 | 10.86% | 0.486 | 2.58e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.179 | 1132.2 | 0.0691 | 6.13% | 0.499 | 1.42e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.003 | 1.6 | 9.739e-05 | 0.01% | 0.751 | 1.33e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.050 | -26.0 | -0.0016 | -0.14% | 0.486 | -3.34e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.317 | 164.6 | 0.0100 | 0.89% | 12.000 | 8.56e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.499 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.751 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.000 | 0.0 | 0.0000 | 0.00% | 0.486 | 0 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | -0.177 | -91.9 | -0.0056 | -0.50% | 12.000 | -4.78e7 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.214 | 111.2 | 0.0068 | 0.60% | 12.000 | 5.79e7 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.103 | 53.4 | 0.0033 | 0.29% | 12.000 | 2.77e7 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.74 C), by the card's idle law | 19.279 | 10016.0 | 0.6113 | 54.23% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.07-24.10 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 13.999 | 7272.9 | 0.4439 | 39.38% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.009 | 4.6 | 2.783e-04 | 0.02% | 12.000 | 2.37e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.ones`, aifoundry1-c1 (E82, 7 passes)

Board in the window 37.285 W (95% 0.115); 1.9252e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **19.37 nJ an op, 1.182 pJ a MAC** with rest included; 1.01e+10 electrons an op from the 12 V input; idle bracket at 58.81 C, window at 58.85 C. Sum of the `+` lines 37.285 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.338 | 8486.6 | 0.5180 | 43.82% | 12.000 | 4.41e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.779 | 5598.8 | 0.3417 | 28.91% | 0.499 | 7.00e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.366 | 1229.2 | 0.0750 | 6.35% | 0.751 | 1.02e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.839 | 1993.9 | 0.1217 | 10.30% | 0.486 | 2.56e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.259 | 1173.4 | 0.0716 | 6.06% | 0.499 | 1.47e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.009 | 4.5 | 2.721e-04 | 0.02% | 0.751 | 3.71e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.028 | -14.6 | -8.903e-04 | -0.08% | 0.486 | -1.87e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.195 | 101.1 | 0.0062 | 0.52% | 12.000 | 5.26e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 1.299 | 674.5 | 0.0412 | 3.48% | 0.499 | 8.44e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.015 | 7.7 | 4.720e-04 | 0.04% | 0.751 | 6.43e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.031 | 15.9 | 9.730e-04 | 0.08% | 0.486 | 2.05e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.174 | 90.4 | 0.0055 | 0.47% | 12.000 | 4.70e7 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.011 | 5.8 | 3.549e-04 | 0.03% | 12.000 | 3.02e6 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.377 | 195.7 | 0.0119 | 1.01% | 12.000 | 1.02e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.147 | 76.4 | 0.0047 | 0.39% | 12.000 | 3.97e7 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.008 | -4.2 | -2.563e-04 | -0.02% | 12.000 | -2.18e6 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.81 C), by the card's idle law | 19.320 | 10035.2 | 0.6125 | 51.82% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.10-24.15 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 14.002 | 7273.1 | 0.4439 | 37.55% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.010 | 5.0 | 3.061e-04 | 0.03% | 12.000 | 2.61e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.neg_ones`, aifoundry1-c1 (E82, 7 passes)

Board in the window 37.480 W (95% 0.055); 1.9248e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **19.47 nJ an op, 1.189 pJ a MAC** with rest included; 1.01e+10 electrons an op from the 12 V input; idle bracket at 58.94 C, window at 59.00 C. Sum of the `+` lines 37.480 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.322 | 8479.8 | 0.5176 | 43.55% | 12.000 | 4.41e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.796 | 5608.9 | 0.3423 | 28.80% | 0.499 | 7.02e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.366 | 1229.0 | 0.0750 | 6.31% | 0.751 | 1.02e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.848 | 1999.4 | 0.1220 | 10.27% | 0.486 | 2.57e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.268 | 1178.2 | 0.0719 | 6.05% | 0.499 | 1.47e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.013 | 6.7 | 4.062e-04 | 0.03% | 0.751 | 5.53e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.028 | -14.7 | -8.955e-04 | -0.08% | 0.486 | -1.88e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.245 | 127.2 | 0.0078 | 0.65% | 12.000 | 6.62e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 1.461 | 759.0 | 0.0463 | 3.90% | 0.499 | 9.49e9 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.013 | 6.9 | 4.189e-04 | 0.04% | 0.751 | 5.70e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.032 | 16.7 | 0.0010 | 0.09% | 0.486 | 2.14e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.128 | 66.6 | 0.0041 | 0.34% | 12.000 | 3.46e7 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.018 | 9.3 | 5.679e-04 | 0.05% | 12.000 | 4.84e6 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.396 | 205.7 | 0.0126 | 1.06% | 12.000 | 1.07e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.163 | 84.7 | 0.0052 | 0.43% | 12.000 | 4.40e7 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | -0.023 | -11.9 | -7.249e-04 | -0.06% | 12.000 | -6.18e6 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.94 C), by the card's idle law | 19.389 | 10073.4 | 0.6148 | 51.73% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.16-24.24 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 13.942 | 7243.7 | 0.4421 | 37.20% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.010 | 5.1 | 3.094e-04 | 0.03% | 12.000 | 2.64e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## TensorFMA `int8.full`, aifoundry1-c1 (E82, 7 passes)

Board in the window 42.650 W (95% 0.157); 1.9248e9 ops/s measured (nominal 1.9321e9 from 318.0 cycles an op); **22.16 nJ an op, 1.352 pJ a MAC** with rest included; 1.15e+10 electrons an op from the 12 V input; idle bracket at 58.77 C, window at 59.21 C. Sum of the `+` lines 42.650 W.

| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.0 | 0.0000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw) | 16.285 | 8460.7 | 0.5164 | 38.18% | 12.000 | 4.40e9 | measured (board less the three rails, at rest) |
| + | at rest, the minion rail (the die's leakage and clocks at rest) | 10.796 | 5609.0 | 0.3423 | 25.31% | 0.499 | 7.02e10 | measured (that card's own regulator telemetry) |
| + | at rest, the sram rail (the die's leakage and clocks at rest) | 2.366 | 1229.2 | 0.0750 | 5.55% | 0.751 | 1.02e10 | measured (that card's own regulator telemetry) |
| + | at rest, the noc rail (the die's leakage and clocks at rest) | 3.842 | 1995.8 | 0.1218 | 9.01% | 0.486 | 2.56e10 | measured (that card's own regulator telemetry) |
| + | awake on zeros, the minion rail (the zeros anchor over rest) | 2.215 | 1150.8 | 0.0702 | 5.19% | 0.499 | 1.44e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the sram rail (the zeros anchor over rest) | 0.006 | 3.0 | 1.835e-04 | 0.01% | 0.751 | 2.50e7 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, the noc rail (the zeros anchor over rest) | -0.032 | -16.7 | -0.0010 | -0.08% | 0.486 | -2.14e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step) | 0.257 | 133.3 | 0.0081 | 0.60% | 12.000 | 6.93e7 | measured as a remainder (board less rails) |
| + | the data-dependent part (over the zeros anchor), the minion rail | 5.970 | 3101.7 | 0.1893 | 14.00% | 0.499 | 3.88e10 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the sram rail | 0.047 | 24.4 | 0.0015 | 0.11% | 0.751 | 2.03e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part (over the zeros anchor), the noc rail | 0.104 | 54.1 | 0.0033 | 0.24% | 0.486 | 6.94e8 | measured (minion: the registered reduction; SRAM and NoC: post hoc, raw) |
| + | the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step) | 0.657 | 341.4 | 0.0208 | 1.54% | 12.000 | 1.78e8 | measured as a remainder (board less rails) |
| + | the window's own heating: the leakage the die adds as it warms during the 2 s window | 0.138 | 71.7 | 0.0044 | 0.32% | 12.000 | 3.73e7 | modelled (the footing slope k = 0.3134 W/C times the window's measured rise) |
| x | the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest) | 0.880 | 457.0 | 0.0279 | 2.06% | 12.000 | 2.38e8 | modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points) |
| x | of which on the data-dependent watts | 0.657 | 341.2 | 0.0208 | 1.54% | 12.000 | 1.77e8 | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit's delivery loss (the books' named gap) | 0.034 | 17.6 | 0.0011 | 0.08% | 12.000 | 9.15e6 | measured less modelled |
| x | the die's leakage at rest, at the run's idle temperature (58.77 C), by the card's idle law | 19.297 | 10025.3 | 0.6119 | 45.24% | - | - | modelled (the lab's own fitted law, docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it) | 16.08-24.12 | | | | | | modelled (range) |
| x | the clock and always-on switching at rest, as the at-rest board less the law's leakage | 13.992 | 7269.4 | 0.4437 | 32.81% | - | - | measured less modelled |
| x | of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current | 0.013 | 6.6 | 4.006e-04 | 0.03% | 12.000 | 3.41e6 | modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## One-number pairs on the TensorFMA (a - b, the same pass, W; mean and 95% t half-width over passes)

| session | card | a - b | n | board D | minion rail | SRAM rail | NoC rail | off-rail | what |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| E78 | aifoundry3 | `fp32.pi` - `anchor_pi` | 6 | 0.108 ± 0.140 | -0.005 ± 0.086 | 0.024 ± 0.020 | 0.031 ± 0.031 | 0.058 ± 0.085 | the same bytes (0x40490FDB everywhere) from the file and the host's built-in: the resolution floor |
| E78 | aifoundry3 | `fp32.pi` - `fp32.ones` | 6 | 0.090 ± 0.114 | 0.110 ± 0.134 | 5.176e-04 ± 0.018 | -0.008 ± 0.021 | -0.013 ± 0.098 | pi against 1.0, both file tiles in the segments |
| E82 | aifoundry1-c1 | `fp32.pi` - `fp32.ones` | 7 | 0.129 ± 0.181 | 0.141 ± 0.172 | 0.012 ± 0.050 | 0.004 ± 0.044 | -0.028 ± 0.130 | pi against 1.0, both file tiles in the segments |
| E78 | aifoundry3 | `anchor_pi` - `fp32.ones` | 6 | -0.018 ± 0.116 | 0.115 ± 0.087 | -0.024 ± 0.016 | -0.039 ± 0.021 | -0.071 ± 0.129 | pi against 1.0, v = w |
| E78 | aifoundry3 | `fp32.ones` - `fp32.neg_ones` | 6 | -0.025 ± 0.154 | -0.004 ± 0.202 | -3.213e-04 ± 0.023 | 0.009 ± 0.027 | -0.029 ± 0.121 | 1.0 against -1.0 |
| E78 | aifoundry3 | `fp16.ones` - `fp16.neg_ones` | 6 | 0.067 ± 0.153 | 0.109 ± 0.140 | 0.011 ± 0.022 | 0.018 ± 0.035 | -0.072 ± 0.129 | fp16 1.0 against -1.0 |
| E78 | aifoundry3 | `int8.neg_ones` - `int8.ones` | 6 | 0.069 ± 0.116 | 0.093 ± 0.018 | -0.005 ± 0.016 | -0.010 ± 0.019 | -0.010 ± 0.116 | int8 -1 against 1 |
| E82 | aifoundry1-c1 | `fp32.pi` - `anchor_pi` | 7 | 0.036 ± 0.123 | -0.004 ± 0.162 | 0.020 ± 0.075 | 0.022 ± 0.030 | -0.002 ± 0.178 | the same bytes, file against built-in: the resolution floor |
| E82 | aifoundry1-c1 | `anchor_pi` - `fp32.ones` | 7 | 0.093 ± 0.133 | 0.145 ± 0.118 | -0.008 ± 0.038 | -0.018 ± 0.039 | -0.026 ± 0.109 | pi against 1.0, v = w |
| E82 | aifoundry1-c1 | `fp32.ones` - `fp32.neg_ones` | 7 | 0.106 ± 0.135 | 0.014 ± 0.149 | 0.012 ± 0.020 | 0.024 ± 0.042 | 0.056 ± 0.071 | 1.0 against -1.0 |
| E82 | aifoundry1-c1 | `fp16.ones` - `fp16.neg_ones` | 7 | -0.090 ± 0.091 | -0.096 ± 0.161 | -0.055 ± 0.180 | 0.005 ± 0.027 | 0.055 ± 0.140 | fp16 1.0 against -1.0 |
| E82 | aifoundry1-c1 | `int8.neg_ones` - `int8.ones` | 7 | 0.116 ± 0.119 | 0.162 ± 0.063 | -0.002 ± 0.013 | 0.001 ± 0.028 | -0.046 ± 0.084 | int8 -1 against 1 |

## Vector `fadd.pi/zeros/h2`, aifoundry3 (catalogue, 3 passes)

456.47e9 instructions/s (wall; 458.27e9 device), 0.3729 per hart-cycle; board 31.807 W = **69.7 pJ an instruction** with rest included, 12.78 pJ above rest; die 58.0 -> 58.4 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 12.869 | 28.19 | 3.524 | 40.46% | 12.000 | 1.47e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.177 | 17.91 | 2.239 | 25.71% | 0.523 | 2.14e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.248 | 4.92 | 0.616 | 7.07% | 0.698 | 4.40e7 | measured |
| + | at rest, the NoC rail | 2.543 | 5.57 | 0.696 | 7.99% | 0.484 | 7.18e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.136 | 0.30 | 0.037 | 0.43% | 12.000 | 1.55e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 4.772 | 10.45 | 1.307 | 15.00% | 0.523 | 1.25e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.113 | 0.25 | 0.031 | 0.36% | 0.698 | 2.22e6 | measured (raw) |
| + | above rest, the NoC rail | 0.026 | 0.06 | 0.007 | 0.08% | 0.484 | 7.42e5 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.923 | 2.02 | 0.253 | 2.90% | 12.000 | 1.05e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.876 | 1.92 | - | 2.75% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.047 | 0.10 | - | 0.15% | - | - | measured less modelled |
| x | the die's leakage at rest, at 58.0 C, by the card's idle law | 13.569 | 29.73 | - | 42.66% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.pi/const/h2`, aifoundry3 (catalogue, 3 passes)

456.53e9 instructions/s (wall; 458.29e9 device), 0.3730 per hart-cycle; board 31.880 W = **69.8 pJ an instruction** with rest included, 12.72 pJ above rest; die 58.0 -> 58.6 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 12.906 | 28.27 | 3.534 | 40.48% | 12.000 | 1.47e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.131 | 17.81 | 2.226 | 25.51% | 0.523 | 2.13e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.270 | 4.97 | 0.622 | 7.12% | 0.698 | 4.45e7 | measured |
| + | at rest, the NoC rail | 2.541 | 5.57 | 0.696 | 7.97% | 0.484 | 7.18e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.222 | 0.49 | 0.061 | 0.70% | 12.000 | 2.53e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 4.885 | 10.70 | 1.337 | 15.32% | 0.523 | 1.28e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.094 | 0.21 | 0.026 | 0.30% | 0.698 | 1.84e6 | measured (raw) |
| + | above rest, the NoC rail | 0.031 | 0.07 | 0.009 | 0.10% | 0.484 | 8.84e5 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.799 | 1.75 | 0.219 | 2.51% | 12.000 | 9.10e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.897 | 1.97 | - | 2.81% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.098 | -0.22 | - | -0.31% | - | - | measured less modelled |
| x | the die's leakage at rest, at 58.0 C, by the card's idle law | 13.557 | 29.70 | - | 42.53% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.pi/random/h2`, aifoundry3 (catalogue, 3 passes)

456.56e9 instructions/s (wall; 458.27e9 device), 0.3730 per hart-cycle; board 35.063 W = **76.8 pJ an instruction** with rest included, 19.73 pJ above rest; die 58.0 -> 58.7 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 12.846 | 28.14 | 3.517 | 36.64% | 12.000 | 1.46e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.197 | 17.95 | 2.244 | 23.38% | 0.523 | 2.14e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.246 | 4.92 | 0.615 | 6.41% | 0.698 | 4.40e7 | measured |
| + | at rest, the NoC rail | 2.536 | 5.55 | 0.694 | 7.23% | 0.484 | 7.16e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.233 | 0.51 | 0.064 | 0.66% | 12.000 | 2.65e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 7.419 | 16.25 | 2.031 | 21.16% | 0.523 | 1.94e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.126 | 0.28 | 0.035 | 0.36% | 0.698 | 2.47e6 | measured (raw) |
| + | above rest, the NoC rail | 0.049 | 0.11 | 0.014 | 0.14% | 0.484 | 1.40e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.412 | 3.09 | 0.386 | 4.03% | 12.000 | 1.61e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.363 | 2.98 | - | 3.89% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.049 | 0.11 | - | 0.14% | - | - | measured less modelled |
| x | the die's leakage at rest, at 58.0 C, by the card's idle law | 13.567 | 29.72 | - | 38.69% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.ps/zeros/h2`, aifoundry3 (catalogue, 3 passes)

456.65e9 instructions/s (wall; 458.36e9 device), 0.3730 per hart-cycle; board 36.174 W = **79.2 pJ an instruction** with rest included, 22.36 pJ above rest; die 57.7 -> 58.4 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 12.841 | 28.12 | 3.515 | 35.50% | 12.000 | 1.46e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.086 | 17.71 | 2.214 | 22.35% | 0.523 | 2.11e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.254 | 4.94 | 0.617 | 6.23% | 0.698 | 4.41e7 | measured |
| + | at rest, the NoC rail | 2.509 | 5.49 | 0.687 | 6.94% | 0.484 | 7.09e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.272 | 0.60 | 0.074 | 0.75% | 12.000 | 3.10e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 8.705 | 19.06 | 2.383 | 24.06% | 0.523 | 2.27e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.109 | 0.24 | 0.030 | 0.30% | 0.698 | 2.13e6 | measured (raw) |
| + | above rest, the NoC rail | 0.055 | 0.12 | 0.015 | 0.15% | 0.484 | 1.55e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.344 | 2.94 | 0.368 | 3.71% | 12.000 | 1.53e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.596 | 3.50 | - | 4.41% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.252 | -0.55 | - | -0.70% | - | - | measured less modelled |
| x | the die's leakage at rest, at 57.7 C, by the card's idle law | 13.444 | 29.44 | - | 37.16% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.ps/const/h2`, aifoundry3 (catalogue, 3 passes)

456.71e9 instructions/s (wall; 458.37e9 device), 0.3730 per hart-cycle; board 36.273 W = **79.4 pJ an instruction** with rest included, 22.80 pJ above rest; die 57.0 -> 57.9 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 13.003 | 28.47 | 3.559 | 35.85% | 12.000 | 1.48e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 7.877 | 17.25 | 2.156 | 21.72% | 0.523 | 2.06e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.194 | 4.80 | 0.601 | 6.05% | 0.698 | 4.30e7 | measured |
| + | at rest, the NoC rail | 2.471 | 5.41 | 0.676 | 6.81% | 0.484 | 6.98e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.313 | 0.69 | 0.086 | 0.86% | 12.000 | 3.57e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 8.844 | 19.36 | 2.421 | 24.38% | 0.523 | 2.31e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.146 | 0.32 | 0.040 | 0.40% | 0.698 | 2.85e6 | measured (raw) |
| + | above rest, the NoC rail | 0.057 | 0.12 | 0.016 | 0.16% | 0.484 | 1.61e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.368 | 3.00 | 0.374 | 3.77% | 12.000 | 1.56e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.624 | 3.56 | - | 4.48% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.256 | -0.56 | - | -0.70% | - | - | measured less modelled |
| x | the die's leakage at rest, at 57.0 C, by the card's idle law | 13.200 | 28.90 | - | 36.39% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.ps/random/h2`, aifoundry3 (catalogue, 3 passes)

456.68e9 instructions/s (wall; 458.44e9 device), 0.3731 per hart-cycle; board 45.265 W = **99.1 pJ an instruction** with rest included, 41.40 pJ above rest; die 58.0 -> 59.5 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 13.061 | 28.60 | 3.575 | 28.85% | 12.000 | 1.49e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.014 | 17.55 | 2.194 | 17.70% | 0.523 | 2.09e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.232 | 4.89 | 0.611 | 4.93% | 0.698 | 4.37e7 | measured |
| + | at rest, the NoC rail | 2.514 | 5.50 | 0.688 | 5.55% | 0.484 | 7.10e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.537 | 1.18 | 0.147 | 1.19% | 12.000 | 6.11e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 15.737 | 34.46 | 4.308 | 34.77% | 0.523 | 4.11e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.180 | 0.39 | 0.049 | 0.40% | 0.698 | 3.52e6 | measured (raw) |
| + | above rest, the NoC rail | 0.121 | 0.27 | 0.033 | 0.27% | 0.484 | 3.42e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 2.869 | 6.28 | 0.785 | 6.34% | 12.000 | 3.27e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 2.891 | 6.33 | - | 6.39% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.022 | -0.05 | - | -0.05% | - | - | measured less modelled |
| x | the die's leakage at rest, at 58.0 C, by the card's idle law | 13.572 | 29.72 | - | 29.98% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/zeros/h2`, aifoundry3 (catalogue, 3 passes)

445.95e9 instructions/s (wall; 447.57e9 device), 0.3642 per hart-cycle; board 38.185 W = **85.6 pJ an instruction** with rest included, 26.94 pJ above rest; die 57.7 -> 58.8 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 12.968 | 29.08 | 3.635 | 33.96% | 12.000 | 1.51e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.057 | 18.07 | 2.258 | 21.10% | 0.523 | 2.16e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.230 | 5.00 | 0.625 | 5.84% | 0.698 | 4.47e7 | measured |
| + | at rest, the NoC rail | 2.515 | 5.64 | 0.705 | 6.59% | 0.484 | 7.27e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.402 | 0.90 | 0.113 | 1.05% | 12.000 | 4.69e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 10.047 | 22.53 | 2.816 | 26.31% | 0.523 | 2.69e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.213 | 0.48 | 0.060 | 0.56% | 0.698 | 4.27e6 | measured (raw) |
| + | above rest, the NoC rail | 0.072 | 0.16 | 0.020 | 0.19% | 0.484 | 2.09e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.680 | 3.77 | 0.471 | 4.40% | 12.000 | 1.96e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.849 | 4.15 | - | 4.84% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.169 | -0.38 | - | -0.44% | - | - | measured less modelled |
| x | the die's leakage at rest, at 57.7 C, by the card's idle law | 13.457 | 30.18 | - | 35.24% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/const/h2`, aifoundry3 (catalogue, 3 passes)

445.72e9 instructions/s (wall; 447.48e9 device), 0.3642 per hart-cycle; board 38.329 W = **86.0 pJ an instruction** with rest included, 27.11 pJ above rest; die 58.0 -> 59.1 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 12.939 | 29.03 | 3.629 | 33.76% | 12.000 | 1.51e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.093 | 18.16 | 2.270 | 21.12% | 0.523 | 2.17e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.291 | 5.14 | 0.643 | 5.98% | 0.698 | 4.60e7 | measured |
| + | at rest, the NoC rail | 2.540 | 5.70 | 0.712 | 6.63% | 0.484 | 7.35e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.381 | 0.86 | 0.107 | 0.99% | 12.000 | 4.45e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 10.131 | 22.73 | 2.841 | 26.43% | 0.523 | 2.71e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.166 | 0.37 | 0.047 | 0.43% | 0.698 | 3.33e6 | measured (raw) |
| + | above rest, the NoC rail | 0.073 | 0.16 | 0.020 | 0.19% | 0.484 | 2.10e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.714 | 3.85 | 0.481 | 4.47% | 12.000 | 2.00e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.862 | 4.18 | - | 4.86% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.148 | -0.33 | - | -0.39% | - | - | measured less modelled |
| x | the die's leakage at rest, at 58.0 C, by the card's idle law | 13.575 | 30.46 | - | 35.42% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/random/h2`, aifoundry3 (catalogue, 3 passes)

446.66e9 instructions/s (wall; 448.34e9 device), 0.3649 per hart-cycle; board 51.919 W = **116.2 pJ an instruction** with rest included, 56.25 pJ above rest; die 58.3 -> 60.5 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 13.093 | 29.31 | 3.664 | 25.22% | 12.000 | 1.52e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.085 | 18.10 | 2.263 | 15.57% | 0.523 | 2.16e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.268 | 5.08 | 0.635 | 4.37% | 0.698 | 4.54e7 | measured |
| + | at rest, the NoC rail | 2.560 | 5.73 | 0.716 | 4.93% | 0.484 | 7.39e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.788 | 1.76 | 0.220 | 1.52% | 12.000 | 9.17e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 20.619 | 46.16 | 5.770 | 39.71% | 0.523 | 5.51e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.250 | 0.56 | 0.070 | 0.48% | 0.698 | 5.01e6 | measured (raw) |
| + | above rest, the NoC rail | 0.141 | 0.31 | 0.039 | 0.27% | 0.484 | 4.06e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 4.114 | 9.21 | 1.151 | 7.92% | 12.000 | 4.79e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 3.784 | 8.47 | - | 7.29% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.330 | 0.74 | - | 0.64% | - | - | measured less modelled |
| x | the die's leakage at rest, at 58.3 C, by the card's idle law | 13.692 | 30.65 | - | 26.37% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/random/h1`, aifoundry3 (catalogue, 3 passes)

355.80e9 instructions/s (wall; 357.20e9 device), 0.5814 per hart-cycle; board 44.758 W = **125.8 pJ an instruction** with rest included, 51.99 pJ above rest; die 57.9 -> 59.3 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 12.960 | 36.43 | 4.553 | 28.96% | 12.000 | 1.89e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.034 | 22.58 | 2.823 | 17.95% | 0.523 | 2.69e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.251 | 6.33 | 0.791 | 5.03% | 0.698 | 5.66e7 | measured |
| + | at rest, the NoC rail | 2.511 | 7.06 | 0.882 | 5.61% | 0.484 | 9.10e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.502 | 1.41 | 0.176 | 1.12% | 12.000 | 7.34e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 15.279 | 42.94 | 5.368 | 34.14% | 0.523 | 5.12e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.129 | 0.36 | 0.045 | 0.29% | 0.698 | 3.23e6 | measured (raw) |
| + | above rest, the NoC rail | 0.111 | 0.31 | 0.039 | 0.25% | 0.484 | 4.03e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 2.980 | 8.38 | 1.047 | 6.66% | 12.000 | 4.36e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 2.803 | 7.88 | - | 6.26% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.176 | 0.50 | - | 0.39% | - | - | measured less modelled |
| x | the die's leakage at rest, at 57.9 C, by the card's idle law | 13.531 | 38.03 | - | 30.23% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `nop/zeros/h2`, aifoundry3 (catalogue, 3 passes)

477.69e9 instructions/s (wall; 479.53e9 device), 0.3902 per hart-cycle; board 28.240 W = **59.1 pJ an instruction** with rest included, 5.23 pJ above rest; die 57.7 -> 57.7 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 12.848 | 26.90 | 3.362 | 45.50% | 12.000 | 1.40e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.083 | 16.92 | 2.115 | 28.62% | 0.523 | 2.02e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.278 | 4.77 | 0.596 | 8.07% | 0.698 | 4.26e7 | measured |
| + | at rest, the NoC rail | 2.535 | 5.31 | 0.663 | 8.98% | 0.484 | 6.84e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 2.007 | 4.20 | 0.525 | 7.11% | 0.523 | 5.02e7 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 7.517e-04 | 0.00 | 1.967e-04 | 0.00% | 0.698 | 1.41e4 | measured (raw) |
| + | above rest, the NoC rail | 5.067e-04 | 0.00 | 1.326e-04 | 0.00% | 0.484 | 1.37e4 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.487 | 1.02 | 0.128 | 1.73% | 12.000 | 5.31e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.363 | 0.76 | - | 1.29% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.124 | 0.26 | - | 0.44% | - | - | measured less modelled |
| x | the die's leakage at rest, at 57.7 C, by the card's idle law | 13.444 | 28.14 | - | 47.60% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fence/zeros/h2`, aifoundry3 (catalogue, 3 passes)

460.24e9 instructions/s (wall; 462.06e9 device), 0.3760 per hart-cycle; board 27.874 W = **60.6 pJ an instruction** with rest included, 4.35 pJ above rest; die 57.8 -> 58.0 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 12.843 | 27.91 | 3.488 | 46.08% | 12.000 | 1.45e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 8.104 | 17.61 | 2.201 | 29.07% | 0.523 | 2.10e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.305 | 5.01 | 0.626 | 8.27% | 0.698 | 4.48e7 | measured |
| + | at rest, the NoC rail | 2.541 | 5.52 | 0.690 | 9.11% | 0.484 | 7.12e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.078 | 0.17 | 0.021 | 0.28% | 12.000 | 8.82e4 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 1.646 | 3.58 | 0.447 | 5.91% | 0.523 | 4.27e7 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | -0.047 | -0.10 | -0.013 | -0.17% | 0.698 | -9.20e5 | measured (raw) |
| + | above rest, the NoC rail | -0.001 | -0.00 | -3.578e-04 | -0.00% | 0.484 | -3.69e4 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.405 | 0.88 | 0.110 | 1.45% | 12.000 | 4.58e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.296 | 0.64 | - | 1.06% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.110 | 0.24 | - | 0.39% | - | - | measured less modelled |
| x | the die's leakage at rest, at 57.8 C, by the card's idle law | 13.484 | 29.30 | - | 48.38% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.pi/zeros/h2`, aifoundry1-c1 (catalogue, 3 passes)

456.35e9 instructions/s (wall; 458.30e9 device), 0.3730 per hart-cycle; board 39.818 W = **87.3 pJ an instruction** with rest included, 12.53 pJ above rest; die 60.0 -> 60.5 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.344 | 35.81 | 4.477 | 41.05% | 12.000 | 1.86e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.146 | 24.42 | 3.053 | 27.99% | 0.499 | 3.05e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.411 | 5.28 | 0.660 | 6.06% | 0.751 | 4.39e7 | measured |
| + | at rest, the NoC rail | 3.997 | 8.76 | 1.095 | 10.04% | 0.486 | 1.12e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.203 | 0.44 | 0.056 | 0.51% | 12.000 | 2.31e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 4.909 | 10.76 | 1.345 | 12.33% | 0.499 | 1.35e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.129 | 0.28 | 0.035 | 0.32% | 0.751 | 2.35e6 | measured (raw) |
| + | above rest, the NoC rail | 0.051 | 0.11 | 0.014 | 0.13% | 0.486 | 1.43e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.628 | 1.38 | 0.172 | 1.58% | 12.000 | 7.16e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.582 | 1.27 | - | 1.46% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.046 | 0.10 | - | 0.12% | - | - | measured less modelled |
| x | the die's leakage at rest, at 60.0 C, by the card's idle law | 19.967 | 43.75 | - | 50.15% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.pi/const/h2`, aifoundry1-c1 (catalogue, 3 passes)

456.37e9 instructions/s (wall; 458.28e9 device), 0.3729 per hart-cycle; board 39.947 W = **87.5 pJ an instruction** with rest included, 12.59 pJ above rest; die 60.3 -> 60.9 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.356 | 35.84 | 4.480 | 40.94% | 12.000 | 1.86e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.188 | 24.52 | 3.064 | 28.01% | 0.499 | 3.07e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.428 | 5.32 | 0.665 | 6.08% | 0.751 | 4.42e7 | measured |
| + | at rest, the NoC rail | 4.031 | 8.83 | 1.104 | 10.09% | 0.486 | 1.13e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.201 | 0.44 | 0.055 | 0.50% | 12.000 | 2.29e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 5.011 | 10.98 | 1.373 | 12.54% | 0.499 | 1.37e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.118 | 0.26 | 0.032 | 0.30% | 0.751 | 2.15e6 | measured (raw) |
| + | above rest, the NoC rail | 0.040 | 0.09 | 0.011 | 0.10% | 0.486 | 1.11e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.574 | 1.26 | 0.157 | 1.44% | 12.000 | 6.55e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.584 | 1.28 | - | 1.46% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.010 | -0.02 | - | -0.02% | - | - | measured less modelled |
| x | the die's leakage at rest, at 60.3 C, by the card's idle law | 20.152 | 44.16 | - | 50.45% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.pi/random/h2`, aifoundry1-c1 (catalogue, 3 passes)

456.33e9 instructions/s (wall; 458.28e9 device), 0.3730 per hart-cycle; board 43.287 W = **94.9 pJ an instruction** with rest included, 19.19 pJ above rest; die 60.5 -> 61.4 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.372 | 35.88 | 4.485 | 37.82% | 12.000 | 1.87e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.319 | 24.80 | 3.100 | 26.15% | 0.499 | 3.10e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.434 | 5.33 | 0.667 | 5.62% | 0.751 | 4.43e7 | measured |
| + | at rest, the NoC rail | 4.039 | 8.85 | 1.106 | 9.33% | 0.486 | 1.14e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.363 | 0.80 | 0.100 | 0.84% | 12.000 | 4.14e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 7.656 | 16.78 | 2.097 | 17.69% | 0.499 | 2.10e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.136 | 0.30 | 0.037 | 0.31% | 0.751 | 2.47e6 | measured (raw) |
| + | above rest, the NoC rail | 0.094 | 0.20 | 0.026 | 0.22% | 0.486 | 2.63e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.873 | 1.91 | 0.239 | 2.02% | 12.000 | 9.95e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.875 | 1.92 | - | 2.02% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.002 | -0.00 | - | -0.00% | - | - | measured less modelled |
| x | the die's leakage at rest, at 60.5 C, by the card's idle law | 20.240 | 44.35 | - | 46.76% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.ps/zeros/h2`, aifoundry1-c1 (catalogue, 3 passes)

456.47e9 instructions/s (wall; 458.37e9 device), 0.3730 per hart-cycle; board 44.463 W = **97.4 pJ an instruction** with rest included, 22.35 pJ above rest; die 60.0 -> 61.0 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.327 | 35.77 | 4.471 | 36.72% | 12.000 | 1.86e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.151 | 24.43 | 3.054 | 25.08% | 0.499 | 3.06e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.421 | 5.30 | 0.663 | 5.45% | 0.751 | 4.41e7 | measured |
| + | at rest, the NoC rail | 3.985 | 8.73 | 1.091 | 8.96% | 0.486 | 1.12e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.375 | 0.82 | 0.103 | 0.84% | 12.000 | 4.27e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 8.937 | 19.58 | 2.447 | 20.10% | 0.499 | 2.45e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.155 | 0.34 | 0.042 | 0.35% | 0.751 | 2.82e6 | measured (raw) |
| + | above rest, the NoC rail | 0.110 | 0.24 | 0.030 | 0.25% | 0.486 | 3.10e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.001 | 2.19 | 0.274 | 2.25% | 12.000 | 1.14e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.019 | 2.23 | - | 2.29% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.018 | -0.04 | - | -0.04% | - | - | measured less modelled |
| x | the die's leakage at rest, at 60.0 C, by the card's idle law | 19.967 | 43.74 | - | 44.91% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.ps/const/h2`, aifoundry1-c1 (catalogue, 3 passes)

456.47e9 instructions/s (wall; 458.37e9 device), 0.3730 per hart-cycle; board 46.403 W = **101.7 pJ an instruction** with rest included, 22.76 pJ above rest; die 62.8 -> 63.9 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.647 | 36.47 | 4.559 | 35.88% | 12.000 | 1.90e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 12.022 | 26.34 | 3.292 | 25.91% | 0.499 | 3.29e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.554 | 5.60 | 0.699 | 5.50% | 0.751 | 4.65e7 | measured |
| + | at rest, the NoC rail | 4.365 | 9.56 | 1.195 | 9.41% | 0.486 | 1.23e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.427 | 0.94 | 0.117 | 0.92% | 12.000 | 4.87e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 9.116 | 19.97 | 2.496 | 19.64% | 0.499 | 2.50e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.147 | 0.32 | 0.040 | 0.32% | 0.751 | 2.67e6 | measured (raw) |
| + | above rest, the NoC rail | 0.106 | 0.23 | 0.029 | 0.23% | 0.486 | 2.99e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.018 | 2.23 | 0.279 | 2.19% | 12.000 | 1.16e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.033 | 2.26 | - | 2.23% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.014 | -0.03 | - | -0.03% | - | - | measured less modelled |
| x | the die's leakage at rest, at 62.8 C, by the card's idle law | 21.597 | 47.31 | - | 46.54% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.ps/random/h2`, aifoundry1-c1 (catalogue, 3 passes)

456.55e9 instructions/s (wall; 458.46e9 device), 0.3731 per hart-cycle; board 53.923 W = **118.1 pJ an instruction** with rest included, 40.64 pJ above rest; die 61.1 -> 63.0 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.737 | 36.66 | 4.582 | 31.04% | 12.000 | 1.91e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.328 | 24.81 | 3.102 | 21.01% | 0.499 | 3.10e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.447 | 5.36 | 0.670 | 4.54% | 0.751 | 4.45e7 | measured |
| + | at rest, the NoC rail | 4.095 | 8.97 | 1.121 | 7.59% | 0.486 | 1.15e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.762 | 1.67 | 0.209 | 1.41% | 12.000 | 8.68e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 16.370 | 35.86 | 4.482 | 30.36% | 0.499 | 4.48e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.214 | 0.47 | 0.058 | 0.40% | 0.751 | 3.89e6 | measured (raw) |
| + | above rest, the NoC rail | 0.259 | 0.57 | 0.071 | 0.48% | 0.486 | 7.29e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.710 | 3.75 | 0.468 | 3.17% | 12.000 | 1.95e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.841 | 4.03 | - | 3.41% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.131 | -0.29 | - | -0.24% | - | - | measured less modelled |
| x | the die's leakage at rest, at 61.1 C, by the card's idle law | 20.576 | 45.07 | - | 38.16% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/zeros/h2`, aifoundry1-c1 (catalogue, 3 passes)

445.53e9 instructions/s (wall; 447.43e9 device), 0.3641 per hart-cycle; board 46.297 W = **103.9 pJ an instruction** with rest included, 26.63 pJ above rest; die 60.3 -> 61.3 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.487 | 37.01 | 4.626 | 35.61% | 12.000 | 1.92e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.132 | 24.99 | 3.123 | 24.04% | 0.499 | 3.13e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.417 | 5.42 | 0.678 | 5.22% | 0.751 | 4.51e7 | measured |
| + | at rest, the NoC rail | 3.996 | 8.97 | 1.121 | 8.63% | 0.486 | 1.15e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.398 | 0.89 | 0.112 | 0.86% | 12.000 | 4.65e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 10.343 | 23.21 | 2.902 | 22.34% | 0.499 | 2.90e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.232 | 0.52 | 0.065 | 0.50% | 0.751 | 4.33e6 | measured (raw) |
| + | above rest, the NoC rail | 0.150 | 0.34 | 0.042 | 0.32% | 0.486 | 4.33e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.141 | 2.56 | 0.320 | 2.46% | 12.000 | 1.33e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.213 | 2.72 | - | 2.62% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.072 | -0.16 | - | -0.16% | - | - | measured less modelled |
| x | the die's leakage at rest, at 60.3 C, by the card's idle law | 20.116 | 45.15 | - | 43.45% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/const/h2`, aifoundry1-c1 (catalogue, 3 passes)

445.79e9 instructions/s (wall; 447.69e9 device), 0.3643 per hart-cycle; board 46.536 W = **104.4 pJ an instruction** with rest included, 26.75 pJ above rest; die 60.5 -> 61.6 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.008 | 35.91 | 4.489 | 34.40% | 12.000 | 1.87e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.195 | 25.11 | 3.139 | 24.06% | 0.499 | 3.14e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.439 | 5.47 | 0.684 | 5.24% | 0.751 | 4.55e7 | measured |
| + | at rest, the NoC rail | 4.542 | 10.19 | 1.274 | 9.76% | 0.486 | 1.31e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.429 | 0.96 | 0.120 | 0.92% | 12.000 | 5.01e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 10.493 | 23.54 | 2.942 | 22.55% | 0.499 | 2.94e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.216 | 0.48 | 0.061 | 0.46% | 0.751 | 4.03e6 | measured (raw) |
| + | above rest, the NoC rail | -0.394 | -0.88 | -0.110 | -0.85% | 0.486 | -1.13e7 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.608 | 3.61 | 0.451 | 3.46% | 12.000 | 1.88e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.108 | 2.49 | - | 2.38% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.500 | 1.12 | - | 1.07% | - | - | measured less modelled |
| x | the die's leakage at rest, at 60.5 C, by the card's idle law | 20.246 | 45.42 | - | 43.51% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/random/h2`, aifoundry1-c1 (catalogue, 3 passes)

446.68e9 instructions/s (wall; 448.64e9 device), 0.3651 per hart-cycle; board 60.210 W = **134.8 pJ an instruction** with rest included, 55.44 pJ above rest; die 61.3 -> 63.4 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.777 | 37.56 | 4.695 | 27.86% | 12.000 | 1.95e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.280 | 25.25 | 3.157 | 18.73% | 0.499 | 3.16e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.441 | 5.46 | 0.683 | 4.05% | 0.751 | 4.54e7 | measured |
| + | at rest, the NoC rail | 4.090 | 9.16 | 1.145 | 6.79% | 0.486 | 1.18e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.860 | 1.93 | 0.241 | 1.43% | 12.000 | 1.00e6 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 21.234 | 47.54 | 5.942 | 35.27% | 0.499 | 5.95e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.301 | 0.67 | 0.084 | 0.50% | 0.751 | 5.59e6 | measured (raw) |
| + | above rest, the NoC rail | 0.314 | 0.70 | 0.088 | 0.52% | 0.486 | 9.03e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 2.914 | 6.52 | 0.815 | 4.84% | 12.000 | 3.39e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 2.396 | 5.36 | - | 3.98% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.517 | 1.16 | - | 0.86% | - | - | measured less modelled |
| x | the die's leakage at rest, at 61.3 C, by the card's idle law | 20.678 | 46.29 | - | 34.34% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/random/h1`, aifoundry1-c1 (catalogue, 3 passes)

355.67e9 instructions/s (wall; 357.19e9 device), 0.5814 per hart-cycle; board 52.794 W = **148.4 pJ an instruction** with rest included, 50.05 pJ above rest; die 60.7 -> 62.4 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.612 | 46.71 | 5.838 | 31.47% | 12.000 | 2.43e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.226 | 31.56 | 3.945 | 21.26% | 0.499 | 3.95e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.438 | 6.86 | 0.857 | 4.62% | 0.751 | 5.70e7 | measured |
| + | at rest, the NoC rail | 4.040 | 11.36 | 1.420 | 7.65% | 0.486 | 1.46e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.677 | 1.90 | 0.238 | 1.28% | 12.000 | 9.91e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 15.923 | 44.77 | 5.596 | 30.16% | 0.499 | 5.60e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.187 | 0.52 | 0.066 | 0.35% | 0.751 | 4.36e6 | measured (raw) |
| + | above rest, the NoC rail | 0.240 | 0.67 | 0.084 | 0.45% | 0.486 | 8.67e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.450 | 4.08 | 0.510 | 2.75% | 12.000 | 2.12e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.777 | 5.00 | - | 3.37% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.327 | -0.92 | - | -0.62% | - | - | measured less modelled |
| x | the die's leakage at rest, at 60.7 C, by the card's idle law | 20.356 | 57.23 | - | 38.56% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `nop/zeros/h2`, aifoundry1-c1 (catalogue, 3 passes)

477.59e9 instructions/s (wall; 479.53e9 device), 0.3902 per hart-cycle; board 36.523 W = **76.5 pJ an instruction** with rest included, 4.93 pJ above rest; die 59.9 -> 60.5 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.316 | 34.16 | 4.270 | 44.67% | 12.000 | 1.78e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.168 | 23.38 | 2.923 | 30.58% | 0.499 | 2.92e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.437 | 5.10 | 0.638 | 6.67% | 0.751 | 4.24e7 | measured |
| + | at rest, the NoC rail | 4.023 | 8.42 | 1.053 | 11.02% | 0.486 | 1.08e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.227 | 0.47 | 0.059 | 0.62% | 12.000 | 2.47e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 2.084 | 4.36 | 0.545 | 5.71% | 0.499 | 5.46e7 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.041 | 0.09 | 0.011 | 0.11% | 0.751 | 7.08e5 | measured (raw) |
| + | above rest, the NoC rail | 0.006 | 0.01 | 0.002 | 0.02% | 0.486 | 1.72e5 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.223 | 0.47 | 0.058 | 0.61% | 12.000 | 2.43e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.236 | 0.49 | - | 0.65% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.013 | -0.03 | - | -0.04% | - | - | measured less modelled |
| x | the die's leakage at rest, at 59.9 C, by the card's idle law | 19.885 | 41.64 | - | 54.44% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fence/zeros/h2`, aifoundry1-c1 (catalogue, 3 passes)

460.21e9 instructions/s (wall; 462.13e9 device), 0.3761 per hart-cycle; board 37.758 W = **82.0 pJ an instruction** with rest included, 4.33 pJ above rest; die 63.0 -> 63.3 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 16.418 | 35.67 | 4.459 | 43.48% | 12.000 | 1.86e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 12.213 | 26.54 | 3.317 | 32.35% | 0.499 | 3.32e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.575 | 5.60 | 0.699 | 6.82% | 0.751 | 4.65e7 | measured |
| + | at rest, the NoC rail | 4.437 | 9.64 | 1.205 | 11.75% | 0.486 | 1.24e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.121 | 0.26 | 0.033 | 0.32% | 12.000 | 1.37e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 1.553 | 3.37 | 0.422 | 4.11% | 0.499 | 4.22e7 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.006 | 0.01 | 0.002 | 0.02% | 0.751 | 1.05e5 | measured (raw) |
| + | above rest, the NoC rail | -0.052 | -0.11 | -0.014 | -0.14% | 0.486 | -1.44e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.486 | 1.06 | 0.132 | 1.29% | 12.000 | 5.49e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.151 | 0.33 | - | 0.40% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.334 | 0.73 | - | 0.89% | - | - | measured less modelled |
| x | the die's leakage at rest, at 63.0 C, by the card's idle law | 21.726 | 47.21 | - | 57.54% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.pi/zeros/h2`, aifoundry2 (catalogue, 3 passes)

456.38e9 instructions/s (wall; 458.28e9 device), 0.3729 per hart-cycle; board 37.671 W = **82.5 pJ an instruction** with rest included, 12.73 pJ above rest; die 72.9 -> 73.5 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 14.792 | 32.41 | 4.051 | 39.27% | 12.000 | 1.69e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.098 | 24.32 | 3.040 | 29.46% | 0.518 | 2.93e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 1.987 | 4.35 | 0.544 | 5.28% | 0.700 | 3.88e7 | measured |
| + | at rest, the NoC rail | 3.631 | 7.96 | 0.995 | 9.64% | 0.485 | 1.02e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.354 | 0.78 | 0.097 | 0.94% | 12.000 | 4.04e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 4.797 | 10.51 | 1.314 | 12.73% | 0.518 | 1.27e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.129 | 0.28 | 0.035 | 0.34% | 0.700 | 2.51e6 | measured (raw) |
| + | above rest, the NoC rail | 0.041 | 0.09 | 0.011 | 0.11% | 0.485 | 1.15e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.841 | 1.84 | 0.230 | 2.23% | 12.000 | 9.59e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.918 | 2.01 | - | 2.44% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.076 | -0.17 | - | -0.20% | - | - | measured less modelled |
| x | the die's leakage at rest, at 72.9 C, by the card's idle law | 19.119 | 41.89 | - | 50.75% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.pi/const/h2`, aifoundry2 (catalogue, 3 passes)

456.53e9 instructions/s (wall; 458.29e9 device), 0.3730 per hart-cycle; board 37.652 W = **82.5 pJ an instruction** with rest included, 12.89 pJ above rest; die 72.9 -> 73.4 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 14.818 | 32.46 | 4.057 | 39.35% | 12.000 | 1.69e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.042 | 24.19 | 3.023 | 29.33% | 0.518 | 2.91e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.011 | 4.40 | 0.551 | 5.34% | 0.700 | 3.93e7 | measured |
| + | at rest, the NoC rail | 3.635 | 7.96 | 0.995 | 9.65% | 0.485 | 1.02e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.263 | 0.58 | 0.072 | 0.70% | 12.000 | 3.00e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 4.882 | 10.69 | 1.337 | 12.96% | 0.518 | 1.29e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.107 | 0.23 | 0.029 | 0.28% | 0.700 | 2.09e6 | measured (raw) |
| + | above rest, the NoC rail | 0.043 | 0.10 | 0.012 | 0.12% | 0.485 | 1.22e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.851 | 1.86 | 0.233 | 2.26% | 12.000 | 9.70e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.933 | 2.04 | - | 2.48% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.082 | -0.18 | - | -0.22% | - | - | measured less modelled |
| x | the die's leakage at rest, at 72.9 C, by the card's idle law | 19.115 | 41.87 | - | 50.77% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.pi/random/h2`, aifoundry2 (catalogue, 3 passes)

456.36e9 instructions/s (wall; 458.26e9 device), 0.3729 per hart-cycle; board 45.527 W = **99.8 pJ an instruction** with rest included, 20.58 pJ above rest; die 79.4 -> 80.2 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 15.482 | 33.92 | 4.241 | 34.01% | 12.000 | 1.76e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 13.270 | 29.08 | 3.635 | 29.15% | 0.518 | 3.50e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.467 | 5.41 | 0.676 | 5.42% | 0.700 | 4.82e7 | measured |
| + | at rest, the NoC rail | 4.386 | 9.61 | 1.201 | 9.63% | 0.485 | 1.24e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.532 | 1.17 | 0.146 | 1.17% | 12.000 | 6.06e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 7.584 | 16.62 | 2.077 | 16.66% | 0.518 | 2.00e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.160 | 0.35 | 0.044 | 0.35% | 0.700 | 3.13e6 | measured (raw) |
| + | above rest, the NoC rail | 0.091 | 0.20 | 0.025 | 0.20% | 0.485 | 2.57e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.554 | 3.41 | 0.426 | 3.41% | 12.000 | 1.77e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.457 | 3.19 | - | 3.20% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.097 | 0.21 | - | 0.21% | - | - | measured less modelled |
| x | the die's leakage at rest, at 79.4 C, by the card's idle law | 22.893 | 50.16 | - | 50.28% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.ps/zeros/h2`, aifoundry2 (catalogue, 3 passes)

456.43e9 instructions/s (wall; 458.33e9 device), 0.3730 per hart-cycle; board 41.823 W = **91.6 pJ an instruction** with rest included, 22.61 pJ above rest; die 71.7 -> 72.7 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 14.723 | 32.26 | 4.032 | 35.20% | 12.000 | 1.68e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 10.792 | 23.64 | 2.956 | 25.80% | 0.518 | 2.85e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 1.945 | 4.26 | 0.533 | 4.65% | 0.700 | 3.80e7 | measured |
| + | at rest, the NoC rail | 3.510 | 7.69 | 0.961 | 8.39% | 0.485 | 9.90e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.533 | 1.17 | 0.146 | 1.28% | 12.000 | 6.08e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 8.702 | 19.07 | 2.383 | 20.81% | 0.518 | 2.30e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.130 | 0.28 | 0.036 | 0.31% | 0.700 | 2.54e6 | measured (raw) |
| + | above rest, the NoC rail | 0.098 | 0.22 | 0.027 | 0.24% | 0.485 | 2.78e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.390 | 3.05 | 0.381 | 3.32% | 12.000 | 1.58e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.668 | 3.65 | - | 3.99% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.278 | -0.61 | - | -0.66% | - | - | measured less modelled |
| x | the die's leakage at rest, at 71.7 C, by the card's idle law | 18.485 | 40.50 | - | 44.20% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.ps/const/h2`, aifoundry2 (catalogue, 3 passes)

456.46e9 instructions/s (wall; 458.36e9 device), 0.3730 per hart-cycle; board 42.855 W = **93.9 pJ an instruction** with rest included, 23.10 pJ above rest; die 73.4 -> 74.4 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 15.009 | 32.88 | 4.110 | 35.02% | 12.000 | 1.71e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.085 | 24.28 | 3.036 | 25.87% | 0.518 | 2.93e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.009 | 4.40 | 0.550 | 4.69% | 0.700 | 3.92e7 | measured |
| + | at rest, the NoC rail | 3.658 | 8.01 | 1.002 | 8.54% | 0.485 | 1.03e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.550 | 1.20 | 0.151 | 1.28% | 12.000 | 6.26e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 8.911 | 19.52 | 2.440 | 20.79% | 0.518 | 2.35e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.164 | 0.36 | 0.045 | 0.38% | 0.700 | 3.21e6 | measured (raw) |
| + | above rest, the NoC rail | 0.111 | 0.24 | 0.030 | 0.26% | 0.485 | 3.13e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.357 | 2.97 | 0.372 | 3.17% | 12.000 | 1.55e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.712 | 3.75 | - | 4.00% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.355 | -0.78 | - | -0.83% | - | - | measured less modelled |
| x | the die's leakage at rest, at 73.4 C, by the card's idle law | 19.404 | 42.51 | - | 45.28% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fadd.ps/random/h2`, aifoundry2 (catalogue, 3 passes)

456.50e9 instructions/s (wall; 458.35e9 device), 0.3730 per hart-cycle; board 51.137 W = **112.0 pJ an instruction** with rest included, 41.38 pJ above rest; die 72.1 -> 74.1 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 15.019 | 32.90 | 4.112 | 29.37% | 12.000 | 1.71e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 10.721 | 23.49 | 2.936 | 20.96% | 0.518 | 2.83e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 1.935 | 4.24 | 0.530 | 3.78% | 0.700 | 3.78e7 | measured |
| + | at rest, the NoC rail | 3.529 | 7.73 | 0.966 | 6.90% | 0.485 | 9.95e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 1.045 | 2.29 | 0.286 | 2.04% | 12.000 | 1.19e6 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 15.802 | 34.62 | 4.327 | 30.90% | 0.518 | 4.17e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.221 | 0.48 | 0.061 | 0.43% | 0.700 | 4.32e6 | measured (raw) |
| + | above rest, the NoC rail | 0.189 | 0.41 | 0.052 | 0.37% | 0.485 | 5.33e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 2.676 | 5.86 | 0.733 | 5.23% | 12.000 | 3.05e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 3.032 | 6.64 | - | 5.93% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.355 | -0.78 | - | -0.69% | - | - | measured less modelled |
| x | the die's leakage at rest, at 72.1 C, by the card's idle law | 18.731 | 41.03 | - | 36.63% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/zeros/h2`, aifoundry2 (catalogue, 3 passes)

445.54e9 instructions/s (wall; 447.39e9 device), 0.3641 per hart-cycle; board 48.103 W = **108.0 pJ an instruction** with rest included, 27.69 pJ above rest; die 78.5 -> 79.7 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 15.483 | 34.75 | 4.344 | 32.19% | 12.000 | 1.81e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 12.830 | 28.80 | 3.600 | 26.67% | 0.518 | 3.47e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.395 | 5.38 | 0.672 | 4.98% | 0.700 | 4.79e7 | measured |
| + | at rest, the NoC rail | 4.257 | 9.55 | 1.194 | 8.85% | 0.485 | 1.23e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.800 | 1.80 | 0.224 | 1.66% | 12.000 | 9.34e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 10.236 | 22.97 | 2.872 | 21.28% | 0.518 | 2.77e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.246 | 0.55 | 0.069 | 0.51% | 0.700 | 4.93e6 | measured (raw) |
| + | above rest, the NoC rail | 0.133 | 0.30 | 0.037 | 0.28% | 0.485 | 3.83e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.723 | 3.87 | 0.483 | 3.58% | 12.000 | 2.01e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.970 | 4.42 | - | 4.10% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.247 | -0.55 | - | -0.51% | - | - | measured less modelled |
| x | the die's leakage at rest, at 78.5 C, by the card's idle law | 22.329 | 50.12 | - | 46.42% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/const/h2`, aifoundry2 (catalogue, 3 passes)

445.45e9 instructions/s (wall; 447.30e9 device), 0.3640 per hart-cycle; board 45.296 W = **101.7 pJ an instruction** with rest included, 27.84 pJ above rest; die 74.6 -> 75.5 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 15.018 | 33.71 | 4.214 | 33.15% | 12.000 | 1.75e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.454 | 25.71 | 3.214 | 25.29% | 0.518 | 3.10e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.110 | 4.74 | 0.592 | 4.66% | 0.700 | 4.22e7 | measured |
| + | at rest, the NoC rail | 3.772 | 8.47 | 1.059 | 8.33% | 0.485 | 1.09e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.539 | 1.21 | 0.151 | 1.19% | 12.000 | 6.29e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 10.129 | 22.74 | 2.842 | 22.36% | 0.518 | 2.74e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.205 | 0.46 | 0.058 | 0.45% | 0.700 | 4.10e6 | measured (raw) |
| + | above rest, the NoC rail | 0.116 | 0.26 | 0.033 | 0.26% | 0.485 | 3.36e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 1.953 | 4.38 | 0.548 | 4.31% | 12.000 | 2.28e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 1.944 | 4.36 | - | 4.29% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.009 | 0.02 | - | 0.02% | - | - | measured less modelled |
| x | the die's leakage at rest, at 74.6 C, by the card's idle law | 20.030 | 44.97 | - | 44.22% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/random/h2`, aifoundry2 (catalogue, 3 passes)

446.53e9 instructions/s (wall; 448.25e9 device), 0.3648 per hart-cycle; board 57.325 W = **128.4 pJ an instruction** with rest included, 55.59 pJ above rest; die 72.3 -> 74.6 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 15.026 | 33.65 | 4.206 | 26.21% | 12.000 | 1.75e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 10.741 | 24.05 | 3.007 | 18.74% | 0.518 | 2.90e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 1.948 | 4.36 | 0.545 | 3.40% | 0.700 | 3.89e7 | measured |
| + | at rest, the NoC rail | 3.558 | 7.97 | 0.996 | 6.21% | 0.485 | 1.03e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 1.229 | 2.75 | 0.344 | 2.14% | 12.000 | 1.43e6 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 20.541 | 46.00 | 5.750 | 35.83% | 0.518 | 5.54e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.301 | 0.67 | 0.084 | 0.53% | 0.700 | 6.01e6 | measured (raw) |
| + | above rest, the NoC rail | 0.225 | 0.50 | 0.063 | 0.39% | 0.485 | 6.48e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 3.756 | 8.41 | 1.051 | 6.55% | 12.000 | 4.37e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 3.935 | 8.81 | - | 6.86% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | -0.180 | -0.40 | - | -0.31% | - | - | measured less modelled |
| x | the die's leakage at rest, at 72.3 C, by the card's idle law | 18.839 | 42.19 | - | 32.86% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fmadd.ps/random/h1`, aifoundry2 (catalogue, 3 passes)

355.79e9 instructions/s (wall; 357.20e9 device), 0.5814 per hart-cycle; board 52.169 W = **146.6 pJ an instruction** with rest included, 52.72 pJ above rest; die 74.6 -> 76.3 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 15.126 | 42.51 | 5.314 | 28.99% | 12.000 | 2.21e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.429 | 32.12 | 4.015 | 21.91% | 0.518 | 3.87e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.105 | 5.92 | 0.740 | 4.03% | 0.700 | 5.28e7 | measured |
| + | at rest, the NoC rail | 3.768 | 10.59 | 1.324 | 7.22% | 0.485 | 1.36e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.985 | 2.77 | 0.346 | 1.89% | 12.000 | 1.44e6 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 15.398 | 43.28 | 5.410 | 29.51% | 0.518 | 5.21e8 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.184 | 0.52 | 0.065 | 0.35% | 0.700 | 4.61e6 | measured (raw) |
| + | above rest, the NoC rail | 0.202 | 0.57 | 0.071 | 0.39% | 0.485 | 7.32e6 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 2.972 | 8.35 | 1.044 | 5.70% | 12.000 | 4.34e6 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 2.958 | 8.31 | - | 5.67% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.014 | 0.04 | - | 0.03% | - | - | measured less modelled |
| x | the die's leakage at rest, at 74.6 C, by the card's idle law | 20.043 | 56.33 | - | 38.42% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `nop/zeros/h2`, aifoundry2 (catalogue, 3 passes)

477.64e9 instructions/s (wall; 479.53e9 device), 0.3902 per hart-cycle; board 33.920 W = **71.0 pJ an instruction** with rest included, 5.25 pJ above rest; die 72.3 -> 72.7 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 14.728 | 30.83 | 3.854 | 43.42% | 12.000 | 1.60e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 10.920 | 22.86 | 2.858 | 32.19% | 0.518 | 2.75e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 1.989 | 4.16 | 0.520 | 5.86% | 0.700 | 3.71e7 | measured |
| + | at rest, the NoC rail | 3.582 | 7.50 | 0.937 | 10.56% | 0.485 | 9.65e7 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.193 | 0.40 | 0.050 | 0.57% | 12.000 | 2.10e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 2.007 | 4.20 | 0.525 | 5.92% | 0.518 | 5.06e7 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | 0.015 | 0.03 | 0.004 | 0.04% | 0.700 | 2.79e5 | measured (raw) |
| + | above rest, the NoC rail | -0.003 | -0.01 | -6.606e-04 | -0.01% | 0.485 | -6.80e4 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.489 | 1.02 | 0.128 | 1.44% | 12.000 | 5.33e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.377 | 0.79 | - | 1.11% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.113 | 0.24 | - | 0.33% | - | - | measured less modelled |
| x | the die's leakage at rest, at 72.3 C, by the card's idle law | 18.816 | 39.39 | - | 55.47% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector `fence/zeros/h2`, aifoundry2 (catalogue, 3 passes)

460.17e9 instructions/s (wall; 462.09e9 device), 0.3761 per hart-cycle; board 34.691 W = **75.4 pJ an instruction** with rest included, 4.44 pJ above rest; die 74.7 -> 75.0 C.

| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |
|---|---|---:|---:|---:|---:|---:|---:|---|
| x | outside the card's measured envelope: the host's power supply and fans | - | - | - | - | - | - | not measured |
| x | the card's own fan | 0.000 | 0.00 | 0.000 | 0.00% | 12.000 | 0 | assumed none (recorded on aifoundry2 only) |
| + | at rest, off the three metered rails | 14.888 | 32.35 | 4.044 | 42.92% | 12.000 | 1.68e7 | measured (board less rails, at rest) |
| + | at rest, the minion rail | 11.583 | 25.17 | 3.146 | 33.39% | 0.518 | 3.03e8 | measured (that card's own regulator telemetry) |
| + | at rest, the SRAM rail | 2.165 | 4.71 | 0.588 | 6.24% | 0.700 | 4.20e7 | measured |
| + | at rest, the NoC rail | 3.825 | 8.31 | 1.039 | 11.03% | 0.485 | 1.07e8 | measured |
| + | the burst's own heating (the catalogue's leakage correction, 21 Sep law) | 0.186 | 0.40 | 0.051 | 0.54% | 12.000 | 2.10e5 | modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise) |
| + | above rest, the minion rail | 1.643 | 3.57 | 0.446 | 4.74% | 0.518 | 4.30e7 | measured (last 0.6 s, divided by 0.94 for the rail's filter) |
| + | above rest, the SRAM rail | -0.040 | -0.09 | -0.011 | -0.11% | 0.700 | -7.69e5 | measured (raw) |
| + | above rest, the NoC rail | -0.003 | -0.01 | -7.431e-04 | -0.01% | 0.485 | -7.65e4 | measured (raw) |
| + | above rest, off-rail (the delivery loss, and off-rail logic in step) | 0.443 | 0.96 | 0.120 | 1.28% | 12.000 | 5.00e5 | measured as a remainder (board over rest less the three rails) |
| x | the regulators' conversion loss above rest (cross-cut) | 0.307 | 0.67 | - | 0.88% | - | - | modelled (section 4.3's fit) |
| x | the off-rail remainder above rest less the fit (the named gap) | 0.136 | 0.30 | - | 0.39% | - | - | measured less modelled |
| x | the die's leakage at rest, at 74.7 C, by the card's idle law | 20.092 | 43.66 | - | 57.92% | - | - | modelled (docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)) |
| x | inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier) | - | - | - | - | - | - | pending |

## Vector pairs (pJ an instruction above rest; per card n 3; pooled card-blocked df 6)

| op | a - b | card | board | minion | SRAM | NoC | off-rail |
|---|---|---|---:|---:|---:|---:|---:|
| fadd.pi | const - zeros | aifoundry3 | -0.06 ± 0.73 | 0.25 ± 1.88 | -0.04 ± 0.31 | 0.01 ± 0.11 | -0.27 ± 2.56 |
| fadd.pi | random - zeros | aifoundry3 | 6.94 ± 0.68 | 5.80 ± 0.73 | 0.03 ± 0.08 | 0.05 ± 0.04 | 1.07 ± 1.17 |
| fadd.ps | const - zeros | aifoundry3 | 0.44 ± 2.05 | 0.30 ± 0.78 | 0.08 ± 0.34 | 0.00 ± 0.05 | 0.05 ± 2.32 |
| fadd.ps | random - zeros | aifoundry3 | 19.04 ± 2.10 | 15.40 ± 1.77 | 0.16 ± 0.31 | 0.14 ± 0.03 | 3.34 ± 2.87 |
| fmadd.ps | const - zeros | aifoundry3 | 0.17 ± 0.26 | 0.20 ± 1.26 | -0.11 ± 0.41 | 7.282e-04 ± 0.06 | 0.08 ± 1.75 |
| fmadd.ps | random - zeros | aifoundry3 | 29.31 ± 0.99 | 23.63 ± 1.90 | 0.08 ± 0.15 | 0.15 ± 0.15 | 5.44 ± 2.61 |
| fadd.pi | const - zeros | aifoundry1-c1 | 0.06 ± 0.77 | 0.22 ± 1.64 | -0.02 ± 0.09 | -0.02 ± 0.11 | -0.12 ± 2.38 |
| fadd.pi | random - zeros | aifoundry1-c1 | 6.67 ± 1.02 | 6.02 ± 0.73 | 0.01 ± 0.06 | 0.09 ± 0.09 | 0.54 ± 1.68 |
| fadd.ps | const - zeros | aifoundry1-c1 | 0.40 ± 0.98 | 0.39 ± 0.84 | -0.02 ± 0.14 | -0.01 ± 0.19 | 0.04 ± 2.11 |
| fadd.ps | random - zeros | aifoundry1-c1 | 18.28 ± 1.32 | 16.28 ± 0.75 | 0.13 ± 0.09 | 0.33 ± 0.12 | 1.55 ± 2.19 |
| fmadd.ps | const - zeros | aifoundry1-c1 | 0.11 ± 0.68 | 0.32 ± 0.81 | -0.04 ± 0.04 | -1.22 ± 5.10 | 1.05 ± 3.96 |
| fmadd.ps | random - zeros | aifoundry1-c1 | 28.80 ± 1.01 | 24.32 ± 1.20 | 0.15 ± 0.07 | 0.37 ± 0.18 | 3.96 ± 1.70 |
| fadd.pi | const - zeros | aifoundry2 | 0.16 ± 0.47 | 0.18 ± 1.67 | -0.05 ± 0.28 | 0.01 ± 0.16 | 0.02 ± 1.50 |
| fadd.pi | random - zeros | aifoundry2 | 7.85 ± 1.77 | 6.11 ± 0.87 | 0.07 ± 0.12 | 0.11 ± 0.17 | 1.56 ± 1.20 |
| fadd.ps | const - zeros | aifoundry2 | 0.49 ± 0.53 | 0.46 ± 1.15 | 0.08 ± 0.24 | 0.03 ± 0.13 | -0.07 ± 1.55 |
| fadd.ps | random - zeros | aifoundry2 | 18.77 ± 0.31 | 15.55 ± 1.54 | 0.20 ± 0.24 | 0.20 ± 0.10 | 2.82 ± 1.46 |
| fmadd.ps | const - zeros | aifoundry2 | 0.15 ± 1.91 | -0.24 ± 0.99 | -0.09 ± 0.43 | -0.04 ± 0.13 | 0.52 ± 0.48 |
| fmadd.ps | random - zeros | aifoundry2 | 27.90 ± 6.44 | 23.03 ± 0.70 | 0.12 ± 0.10 | 0.21 ± 0.17 | 4.54 ± 6.92 |
| fadd.pi | const - zeros | pooled | **0.05 ± 0.22** | **0.22 ± 0.57** | **-0.04 ± 0.08** | **-0.00 ± 0.04** | **-0.12 ± 0.72** |
| fadd.pi | random - zeros | pooled | **7.15 ± 0.41** | **5.98 ± 0.26** | **0.04 ± 0.03** | **0.08 ± 0.04** | **1.06 ± 0.45** |
| fadd.ps | const - zeros | pooled | **0.44 ± 0.44** | **0.38 ± 0.31** | **0.05 ± 0.08** | **0.01 ± 0.04** | **0.01 ± 0.66** |
| fadd.ps | random - zeros | pooled | **18.70 ± 0.47** | **15.74 ± 0.47** | **0.16 ± 0.08** | **0.22 ± 0.03** | **2.57 ± 0.74** |
| fmadd.ps | const - zeros | pooled | **0.15 ± 0.39** | **0.10 ± 0.34** | **-0.08 ± 0.11** | **-0.42 ± 0.97** | **0.55 ± 0.83** |
| fmadd.ps | random - zeros | pooled | **28.67 ± 1.25** | **23.66 ± 0.45** | **0.12 ± 0.04** | **0.24 ± 0.06** | **4.65 ± 1.44** |

