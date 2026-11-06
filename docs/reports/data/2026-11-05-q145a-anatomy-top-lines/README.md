# Q145(a), post hoc: the anatomy's measured top lines - every place the energy of one TensorFMA step and one vector add goes, as far as each card's own meters reach

**Post hoc throughout.** Thu 5 Nov 2026 (week 45), about 22:20-23:30 PST, on the Intel, desk only: no card claimed, no
device command sent, no lab box reached, nothing posted, nothing deployed. Every number is read from data committed before
this lane started, or from a public source at a pinned commit; nothing here is a prediction, a fit that enters a model or a
verdict, and nothing is blind.

## Builds on (the stock-take rule of 5 Nov 2026)

- **Checked:** the prior-work inventory, read Thu 5 Nov 2026 about 22:20-22:35 PST; its public rows L03, L06, L07, L11, L14,
  L22, H05, H07, H19, H24, H27, P03, P06, P07, P11, P16 and P18 (ids in a private inventory: opaque pointers here). The map's
  steps 6 and 5 and its rows 7, 5, 41, 16, 29 and 30 set this lane's scope.
- **Used**, each with what is taken and how it was checked:
  - **E171** (aifoundry3, pool 8, lab `91f8ae40`) and **E172** (aifoundry1 card 1, `b3255af1`): the registered reduction's board
    and minion-rail values per run, the run windows, the kept passes and the committed telemetry. Check: re-computed here from
    the committed telemetry with `reduce_e78.py`'s windows (`cfd94285`), they equal the committed per-pass D, S, Drail and Srail
    to 1e-11 W (`anatomy.txt`, VALIDATION).
  - **E78** (aifoundry3, `410c56f6`) and **E82** (card 1, `0a041356`), on **Q139(u)'s footing** (`f47669d1`,
    `2026-11-03-q139u-footing/reduced/e78-footing.json`, `e82-footing.json`, `footing.json`): the one-number kinds `ones`,
    `neg_ones`, `pi` in each format. Check: the re-computation equals the footing reductions' per-pass values to 1e-11 W.
  - **The energy manual** (`docs/energy-manual/`, 26-27 Sep): the per-card idle laws of `01-at-rest.md` (`0cfc742d`) for the
    leakage line, checked against each session's own idle before its fp32 random runs (aifoundry3 26.09 W read at 58.88 C, 26.20 W
    by its law; card 1 33.30 W read at 58.83 C, 33.43 W by its law); the awake core of `02-awake.md` (a nop or a fence, 4.4-5.1 pJ an issue slot); the catalogue
    (`2026-09-23-energy-manual/catalogue.json`, `f1461a68`) for the vector rows by rail, checked: its combined `fmadd.ps` random
    row re-reads 55.76 pJ, `03-instructions.md`'s 55.8; section 4.3's per-card delivery-loss fit (`unmetered_fit.json`,
    `tools/ettelem/fit_unmetered.py`) for the regulators' line, with its rail-scale caveat.
  - **Q129's rail ledger** (`2026-10-27-q129-rail-ledger/`, `b8b8691c`): the footing caveats and aifoundry2's short form below;
    check: this lane's SRAM and NoC lines for a random fp32 MAC (0.068 pJ together on aifoundry3, 0.116 pJ on card 1) sit inside
    Q129's bound (at most 0.13 pJ together, 2.2% of the board).
  - **Q136(b)'s off-rail row** (`2026-11-02-q136b-rail-row/`, `bba190bb`): the delivery-loss coefficient's band (E77 and E120
    combined, 0.175 [0.151, 0.199] W per minion W on aifoundry2, against the published 0.188) and the unsettled conduction share.
  - **E71** (`2026-10-27-e71-idle-slope-aifoundry3/slopes.json`, `730cc8fc`): aifoundry3's dedicated idle slope at 58-62 C,
    0.3803 W/C (re-read here as the median of its six cycles, 0.38027), as the check on the law's slope at 58.9 C (0.386 W/C).
    **E97** (`9b93e3e9`): 0.40 W/C at 62.4 C from its rests, cited beside it.
  - **E58's measured meter filter** (findings 05, 03): the rails' time constants, among them card 1's 0.54 s SRAM rail, for a
    sensitivity arm (`sram_tau054` in `anatomy.json`: the SRAM lines move by 0.02 W at most).
  - **E178** (`48171930`) and its dated note **A1** (`f421c67a`): the one-number kinds' framing, and A1-2's withdrawal of the
    vector-add "null" (quoted, not changed). Nothing is written under `tools/claims-v3/e178/`.
  - **The fan records**: `docs/findings/14-card-behaviour.md` (`5c5e35f5`; aifoundry2's card is passive, 9 Oct) and the 6 Oct
    fan-fix report (`591a23c2`).
  - **Public sources at pinned commits:** aifoundry-org/et-man `5fe80a3` (`ET-PCIe-Dev-Card-V3.pdf`: the TPSM831D31 minion and
    NoC regulator, the LTM4680 SRAM regulator, the 1 mOhm kelvin resistor and the LTC4218 on the 12 V input, no fan in the
    card's features); aifoundry-org/et-boards `e5e0cf2` (the PMIC firmware: one fixed current gain for every board, `adc.h:27`;
    the 1.0 s average, `power_manager_event.c:30`; the MAX6660 fan regulator read only in a test path, `IoTask.c:1171-1177`);
    aifoundry-org/et-platform `836a4ab60` (`test-compute-kernels/src/vpu_txfma_power_virus/kernel.h`); openhwfoundation/core-et
    `b38a1a3` (`dv/tests/minion_core/c_asm_tests/power_vpu/ps/kernel.h`); Ditzel, RISC-V Summit, Dec 2022, slides 14-15 (a
    public anchor only); Ditzel, IEEE Micro 42(3), 2022 (the rail domains: the ET-Minion and its L1 on one low-voltage plane).
  - **The lab's own workload code:** `workloads/enercat` (`gen_ops.py` `4845a60e`; `kernel/enercat.c` VMABLOCK and
    `host/main.cpp` `sources()`, `2be3f07e`) for the random rotation's operand flips.
- **Not used:**
  - the September 21 flip model's per-flip energies (energy manual 3.2's "per flip" table): superseded, the bench it was fitted on
    was miscompiled (Q132(b));
  - M10, M9 and every frozen predictor: this is a measured ledger, no model enters;
  - E173, E174 and E175 (800 MHz, governed, with the governor's dips): another operating point;
  - Q126(c)'s joined load model and the September structured matrices: not applicable to one operation;
  - the transistor ledger and waterfall (Q128, Q129's stop 9): their rebuild on the fixed bench is owed since 1 Nov, and the split
    inside the logic is left as one pending line here;
  - E64's fitted meter filter and the PMIC's alarm path: not applicable at 600 MHz pinned;
  - E77's and E120's rails at one temperature: used only through Q136(b)'s re-cut.
- **Tiers:** public only. Every figure is the lab's committed data or a public source at a pinned commit. No NDA-tier check is
  cited (none was made for these lines); the split inside the switching rails is one pending line with no number.

## Results first

### One fp32 TensorFMA step on random data, aifoundry3 (E171, 4 passes, 600 MHz, 521.6 mV), every line

One step is one TensorFMA instruction on one minion: a 16 x 16 x 16 tile, 4,096 multiply-adds, 546.001 cycles. The rate is
the measured one, **1.1171e9 steps a second** over all 1,024 minions (the launch records prorated over the 2 s window; the
cycle count alone gives 1.1253e9, the difference being the launch gaps). The first table's lines add up to what the board's own
meter reads in the window, exactly; the second table splits some of them another way. Charge is a line's energy
over its rail's voltage, and electrons are charge over e; the off-rail lines are counted at the card's nominal 12 V input.

| where the energy goes | W | nJ per op | pJ per MAC | share of the board | volts | electrons per op | label |
|---|---:|---:|---:|---:|---:|---:|---|
| At rest, off the three metered rails: DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw | 12.976 | 11.616 | 2.836 | 24.4% | 12.000 | 6.04e+09 | measured: the board less the three rails, 1 s before each run |
| At rest, the minion rail: the 1,024 minions' leakage and idle clocks | 8.286 ± 0.035 | 7.417 | 1.811 | 15.6% | 0.521 | 8.89e+10 | measured: the minion regulator's own telemetry |
| At rest, the SRAM rail: the shires' SRAM banks at rest | 2.229 ± 0.012 | 1.995 | 0.487 | 4.2% | 0.698 | 1.78e+10 | measured: the SRAM regulator's telemetry |
| At rest, the NoC rail: the mesh at rest | 2.594 ± 0.003 | 2.322 | 0.567 | 4.9% | 0.484 | 2.99e+10 | measured: the NoC regulator's telemetry |
| Awake on zeros, the minion rail: issuing TensorFMA, the tensor state machines, the scratchpad reads of zero words, the awake core's clocks | 1.699 | 1.521 | 0.371 | 3.2% | 0.521 | 1.82e+10 | measured (the registered reduction's Srail less Drail) |
| Awake on zeros, the SRAM and NoC rails | 0.056 | 0.050 | 0.012 | 0.1% | 0.698 | 3.90e+08 | measured, post hoc, raw |
| Awake on zeros, off-rail: the regulators' loss on those watts, and off-rail logic in step | 0.242 | 0.217 | 0.053 | 0.5% | 12.000 | 1.13e+08 | measured as a remainder |
| The data-dependent part, the minion rail: the lanes' multiplier and adder trees, the accumulator, the operand and result buses, the lane clocks that run once a word is nonzero, the scratchpad's data bits | 19.645 ± 0.154 | 17.585 | 4.293 | 36.9% | 0.521 | 2.11e+11 | measured (the registered reduction's Drail) |
| The data-dependent part, the SRAM and NoC rails | 0.313 | 0.280 | 0.068 | 0.6% | 0.698 | 3.18e+09 | measured, post hoc, raw: about the size of their own window heating |
| The data-dependent part, off-rail: mostly the regulators' loss on the extra minion-rail watts | 4.740 | 4.243 | 1.036 | 8.9% | 12.000 | 2.21e+09 | measured as a remainder |
| The window's own heating: leakage added as the die warms 2.3 C above its idle bracket during the 2 s window | 0.477 ± 0.012 | 0.427 | 0.104 | 0.9% | 12.000 | 2.22e+08 | modelled: the footing slope 0.2056 W/C times the measured rise |
| **The board, as its own meter reads it in the window** | **53.256 ± 0.028** | **47.672** | **11.639** | 100% | 12 (input) | 2.48e+10 | measured |

| cross-cut (a split of the lines above, not added) | W | nJ per op | share | label |
|---|---:|---:|---:|---|
| The regulators' conversion loss on the op's watts above rest (section 4.3's fit: 0.181 x minion + 0.043 x SRAM + 0.294 x NoC) | 3.923 | 3.511 | 7.4% | modelled from the lab's fit; each 1% of rail-meter scale moves it about 1.2 points |
| of which on the data-dependent watts | 3.617 | 3.238 | 6.8% | modelled |
| The off-rail watts above rest that the fit does not explain: the books' named gap | 1.059 | 0.948 | 2.0% | measured less modelled |
| The die's leakage at rest, at 58.88 C, by aifoundry3's idle law (12.3 W + 25.0 W e^((T-80)/36)) | 13.903 | 12.445 | 26.1% | modelled (the lab's own fit; the idle data do not pin the e-folding) |
| the same leakage at an e-folding of 30 or 45 C | 11.59-17.38 | 10.37-15.56 | 22-33% | modelled range |
| The clocks and always-on switching at rest (the at-rest board less that leakage) | 12.182 | 10.905 | 22.9% | measured less modelled |
| The board meter's own 1 mOhm sense resistor | 0.020 | 0.018 | 0.0% | modelled from the public schematic |
| Inside the switching rails: the per-electron ledger (transistor gate charge, wires, internal and short-circuit energy, glitches, the lane's clock tree) | - | - | - | pending (Q144, the NDA tier); no number beyond the rails' measured totals |

**Outside the card's measured envelope, and not in the sum:** the host's power supply (converting wall power to the card's 12 V)
and the host's fans, which cool the card. Neither is measured, and no public source gives a figure for these hosts, so the
ledger names them and gives no number. **The card's own fan: none.** aifoundry2's card is recorded passive (on site, 9 Oct
2026: since then a two-fan bracket on the host's headers blows across its heatsink; before it, a 120 mm fan clipped under the
card); the V3 card's public documentation lists no fan; its MAX6660 fan-speed regulator is read only by a PMIC test path.
aifoundry3's and aifoundry1's cooling is not recorded. So no fan draws from the card's metered 12 V, and every line above is on
the card.

**In plain words.** Half of what the card draws while it does one random fp32 tile step (49%) would be drawn with nothing
running: a quarter off the die's metered rails (memory, PCIe, I/O, clocks, the regulators' own draw) and a quarter on the die's
rails at rest, mostly leakage by the card's idle law. The step itself adds 51%: 37% is the minion rail's data-dependent switching,
the place where the numbers matter; 9% is off the rails, mostly the regulators turning 12 V into half a volt for those extra
watts (7% by the lab's fit); 0.6% is the SRAM and NoC rails; 4% is the awake but idle-on-zeros
core; and 1% is leakage the die adds as it warms during the 2 s window. Per multiply-add that is 11.6 pJ in all, 4.3 pJ of it
the lanes' own switching. At half a volt that switching is 2.1e11 electrons a step, 5.1e7 a multiply-add; the whole board draws
only 2.5e10 electrons a step from its 12 V input, because a regulator trades voltage for current (energy, not charge, carries
across it).

### The same step on zeros, on one number, and in fp16 and int8, on both 600 MHz cards (short form, nJ per op)

The full tables, every line with its watts, share, volts and electrons, are in [`anatomy-tables.md`](anatomy-tables.md).
`anchor_pi` is the host's built-in tile, 3.14159274f (0x40490FDB) in every element of A and B: a one-number fp32 tile. The
E78 and E82 rows are the one-number kinds of 31 Oct on Q139(u)'s footing.

| op (session) | card | board nJ/op (pJ/MAC) | at rest | awake on zeros | data, minion rail | data, SRAM + NoC | data, off-rail | window heating | regulators (fit) | named gap |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `fp32.zeros` (E171) | aifoundry3 | 24.99 (6.101) | 23.37 (94%) | 1.76 (7%) | 0.00 (0%) | 0.00 | 0.00 (0%) | -0.14 | 0.27 | -0.07 |
| `anchor_pi` (E171) | aifoundry3 | 32.64 (7.969) | 23.25 (71%) | 1.80 (6%) | 6.30 (19%) | 0.06 | 1.13 (3%) | 0.10 | 1.42 | -0.05 |
| `fp32.randn` (E171) | aifoundry3 | 47.67 (11.639) | 23.35 (49%) | 1.79 (4%) | 17.59 (37%) | 0.28 | 4.24 (9%) | 0.43 | 3.51 | 0.95 |
| `fp16.zeros` (E171) | aifoundry3 | 24.97 (3.049) | 23.31 (93%) | 1.80 (7%) | 0.00 (0%) | 0.00 | 0.00 (0%) | -0.14 | 0.28 | -0.07 |
| `fp16.randn` (E171) | aifoundry3 | 45.29 (5.528) | 23.33 (52%) | 1.76 (4%) | 15.92 (35%) | 0.25 | 3.65 (8%) | 0.38 | 3.21 | 0.61 |
| `int8.zeros` (E171) | aifoundry3 | 14.84 (0.906) | 13.57 (91%) | 1.32 (9%) | 0.00 (0%) | 0.00 | 0.00 (0%) | -0.05 | 0.21 | -0.06 |
| `int8.full` (E171) | aifoundry3 | 18.62 (1.137) | 13.57 (73%) | 1.32 (7%) | 3.10 (17%) | 0.04 | 0.56 (3%) | 0.04 | 0.78 | -0.07 |
| `fp32.zeros` (E172) | aifoundry1-c1 | 31.25 (7.628) | 29.77 (95%) | 1.63 (5%) | 0.00 (0%) | 0.00 | 0.00 (0%) | -0.15 | 0.17 | 0.03 |
| `anchor_pi` (E172) | aifoundry1-c1 | 38.71 (9.450) | 29.56 (76%) | 1.80 (5%) | 6.33 (16%) | 0.12 | 0.72 (2%) | 0.18 | 0.87 | 0.09 |
| `fp32.randn` (E172) | aifoundry1-c1 | 53.48 (13.056) | 29.81 (56%) | 1.64 (3%) | 17.73 (33%) | 0.47 | 3.14 (6%) | 0.69 | 2.13 | 1.19 |
| `fp16.zeros` (E172) | aifoundry1-c1 | 31.20 (3.808) | 29.75 (95%) | 1.63 (5%) | 0.00 (0%) | 0.00 | 0.00 (0%) | -0.18 | 0.17 | 0.06 |
| `fp16.randn` (E172) | aifoundry1-c1 | 51.15 (6.244) | 29.76 (58%) | 1.59 (3%) | 16.00 (31%) | 0.42 | 2.72 (5%) | 0.67 | 1.92 | 1.02 |
| `int8.zeros` (E172) | aifoundry1-c1 | 18.50 (1.129) | 17.34 (94%) | 1.27 (7%) | 0.00 (0%) | 0.00 | 0.00 (0%) | -0.10 | 0.12 | -0.03 |
| `int8.full` (E172) | aifoundry1-c1 | 22.19 (1.354) | 17.34 (78%) | 1.25 (6%) | 3.06 (14%) | 0.06 | 0.39 (2%) | 0.08 | 0.45 | 0.02 |
| `fp32.ones` (E78) | aifoundry3 | 32.59 (7.956) | 23.25 (71%) | 1.82 (6%) | 6.26 (19%) | 0.10 | 1.11 (3%) | 0.05 | 1.44 | -0.16 |
| `fp32.neg_ones` (E78) | aifoundry3 | 32.55 (7.946) | 23.23 (71%) | 1.76 (5%) | 6.26 (19%) | 0.09 | 1.14 (3%) | 0.06 | 1.41 | -0.03 |
| `fp32.pi` (E78) | aifoundry3 | 32.61 (7.962) | 23.23 (71%) | 1.72 (5%) | 6.36 (19%) | 0.09 | 1.10 (3%) | 0.11 | 1.43 | -0.11 |
| `fp16.ones` (E78) | aifoundry3 | 32.58 (3.977) | 23.27 (71%) | 1.72 (5%) | 6.34 (19%) | 0.12 | 1.07 (3%) | 0.06 | 1.43 | -0.15 |
| `fp16.neg_ones` (E78) | aifoundry3 | 32.58 (3.977) | 23.26 (71%) | 1.76 (5%) | 6.24 (19%) | 0.09 | 1.14 (3%) | 0.08 | 1.42 | -0.09 |
| `int8.ones` (E78) | aifoundry3 | 15.71 (0.959) | 13.54 (86%) | 1.34 (9%) | 0.70 (4%) | 0.02 | 0.09 (1%) | 0.01 | 0.35 | -0.12 |
| `int8.neg_ones` (E78) | aifoundry3 | 15.72 (0.960) | 13.53 (86%) | 1.32 (8%) | 0.75 (5%) | 0.01 | 0.08 (1%) | 0.03 | 0.34 | -0.07 |
| `fp32.ones` (E82) | aifoundry1-c1 | 38.61 (9.427) | 29.68 (77%) | 1.61 (4%) | 6.20 (16%) | 0.17 | 0.74 (2%) | 0.21 | 0.84 | 0.17 |
| `fp32.neg_ones` (E82) | aifoundry1-c1 | 38.58 (9.419) | 29.57 (77%) | 1.77 (5%) | 6.19 (16%) | 0.14 | 0.69 (2%) | 0.22 | 0.86 | 0.09 |
| `fp32.pi` (E82) | aifoundry1-c1 | 38.76 (9.462) | 29.73 (77%) | 1.63 (4%) | 6.33 (16%) | 0.18 | 0.72 (2%) | 0.17 | 0.97 | -1.01 |
| `fp16.ones` (E82) | aifoundry1-c1 | 38.68 (4.721) | 29.77 (77%) | 1.65 (4%) | 6.14 (16%) | 0.11 | 0.81 (2%) | 0.20 | 0.84 | 0.14 |
| `fp16.neg_ones` (E82) | aifoundry1-c1 | 38.70 (4.724) | 29.74 (77%) | 1.68 (4%) | 6.23 (16%) | 0.16 | 0.76 (2%) | 0.13 | 0.84 | 0.19 |
| `int8.ones` (E82) | aifoundry1-c1 | 19.37 (1.182) | 17.31 (89%) | 1.26 (7%) | 0.67 (3%) | 0.02 | 0.09 (0%) | 0.01 | 0.20 | -0.00 |
| `int8.neg_ones` (E82) | aifoundry1-c1 | 19.47 (1.189) | 17.32 (89%) | 1.30 (7%) | 0.76 (4%) | 0.02 | 0.07 (0%) | 0.01 | 0.21 | -0.01 |

- **The minion rail carries 79-85% of the data-dependent watts on aifoundry3 (median 82%) and 81-94% on card 1 (median 85%)**,
  over every pool-8 item with D above 2 W (63 a card; `anatomy.json` `extras.rail_share`): the upper bound for any model of the
  minion's logic on that card. The stock-take's "81-86%" is close; fp32 random on aifoundry3 sits near the bottom, at 79.5%.
- **Compared after each card's own V squared** (minion 521.6 mV on aifoundry3, 499 mV on card 1): card 1's data-dependent
  minion-rail energy per step is 1.100 / 1.104 / 1.100 / 1.082 times aifoundry3's for pi, fp32, fp16 and int8 random (raw, before
  V squared: 0.99-1.01), and its data-dependent off-rail line is 0.64-0.75 times aifoundry3's (card 1's delivery-loss coefficient
  is 0.102, aifoundry3's 0.181). Whether card 1's 10% is the rail meter's gain, the silicon or an on-die voltage reading is not
  separable on these data (the public PMIC firmware applies one fixed current gain to every board's 12 V meter, and the rails are
  each regulator's own telemetry, no better calibrated).
- **aifoundry2 in short form** (no 600 MHz pool-8 session; from committed rows of 26 Sep, launched at about 80 C): fp32 random
  5.920 pJ a MAC above idle at the board, 13.84 loaded (energy manual 3.2); on Q129's uncorrected footing, board 6.421 pJ, minion
  rail 4.881, SRAM 0.070, NoC 0.086 and off-rail 1.384 pJ a MAC, of which the delivery-loss fit takes 0.944
  (`2026-10-27-q129-rail-ledger/reduce.txt` line 12). The vector rows below include aifoundry2 in full.
- **One item's rest and awake split is unusable:** `fp32.pi` on card 1 (E82) has one pass whose 1 s idle bracket caught a minion-rail
  transient (that line's spread across passes is 2.9 W against 0.16 W for `fp32.ones`), so its rest and awake minion lines trade
  about 0.9 W and its named gap reads -1.01 nJ. Their sum, the board and the data line are unaffected.
- **No DRAM line above rest:** a resident TensorFMA tile is TensorLoaded once a launch and re-read from the scratchpad (on the
  minion rail, IEEE Micro's rail domains), so no byte crosses the mesh or reaches DRAM in steady state. The NoC line above zeros is
  0.04-0.36 W, the size of its own window heating; a byte that did cross would cost 1.27-1.50 pJ a hop on the mesh rail (energy
  manual `04a-fine-grain.md`, "The mesh rail alone"). The DDR rail's voltage monitor droops 0.33 mV on aifoundry3 and 1.99 mV on card 1 under fp32 random, but the
  energy manual already shows that monitor drooping on non-DRAM loads (2.0 mV for scratchpad traffic), so it is no DRAM reading.

### One vector instruction on zeros, the constant 1.0f and random data, three cards (catalogue, 26 Sep; pJ an instruction)

Both harts of all 1,024 minions run the instruction flat out, eight-instruction blocks rotating sources f0-f7 (the catalogue's
"constant" is 1.0f, 0x3F800000, in every source word). The rate is instructions retired over the burst's wall time, the
catalogue's own pj_per_op convention (0.4% above the device-time rate). The burst's heating line is the catalogue's own leakage
correction (the 21 Sep law's slope times the burst's measured rise).

| instruction | card | board pJ (rest included) | at rest | burst heating | above rest, minion rail | above rest, SRAM + NoC | above rest, off-rail | regulators (fit) | named gap | issue per hart-cycle |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `fadd.pi/zeros/h2` | aifoundry3 | 69.7 | 56.6 | 0.30 | 10.45 | 0.31 | 2.02 | 1.92 | 0.10 | 0.3729 |
| `fadd.pi/const/h2` | aifoundry3 | 69.8 | 56.6 | 0.49 | 10.70 | 0.27 | 1.75 | 1.97 | -0.22 | 0.3730 |
| `fadd.pi/random/h2` | aifoundry3 | 76.8 | 56.6 | 0.51 | 16.25 | 0.38 | 3.09 | 2.98 | 0.11 | 0.3730 |
| `fadd.ps/zeros/h2` | aifoundry3 | 79.2 | 56.3 | 0.60 | 19.06 | 0.36 | 2.94 | 3.50 | -0.55 | 0.3730 |
| `fadd.ps/const/h2` | aifoundry3 | 79.4 | 55.9 | 0.69 | 19.36 | 0.44 | 3.00 | 3.56 | -0.56 | 0.3730 |
| `fadd.ps/random/h2` | aifoundry3 | 99.1 | 56.5 | 1.18 | 34.46 | 0.66 | 6.28 | 6.33 | -0.05 | 0.3731 |
| `fmadd.ps/zeros/h2` | aifoundry3 | 85.6 | 57.8 | 0.90 | 22.53 | 0.64 | 3.77 | 4.15 | -0.38 | 0.3642 |
| `fmadd.ps/const/h2` | aifoundry3 | 86.0 | 58.0 | 0.86 | 22.73 | 0.53 | 3.85 | 4.18 | -0.33 | 0.3642 |
| `fmadd.ps/random/h2` | aifoundry3 | 116.2 | 58.2 | 1.76 | 46.16 | 0.88 | 9.21 | 8.47 | 0.74 | 0.3649 |
| `nop/zeros/h2` (the issue floor) | aifoundry3 | 59.1 | 53.9 | 0.00 | 4.20 | 0.00 | 1.02 | 0.76 | 0.26 | 0.3902 |
| `fadd.pi/zeros/h2` | aifoundry1-c1 | 87.3 | 74.3 | 0.44 | 10.76 | 0.39 | 1.38 | 1.27 | 0.10 | 0.3730 |
| `fadd.pi/const/h2` | aifoundry1-c1 | 87.5 | 74.5 | 0.44 | 10.98 | 0.35 | 1.26 | 1.28 | -0.02 | 0.3729 |
| `fadd.pi/random/h2` | aifoundry1-c1 | 94.9 | 74.9 | 0.80 | 16.78 | 0.50 | 1.91 | 1.92 | -0.00 | 0.3730 |
| `fadd.ps/zeros/h2` | aifoundry1-c1 | 97.4 | 74.2 | 0.82 | 19.58 | 0.58 | 2.19 | 2.23 | -0.04 | 0.3730 |
| `fadd.ps/const/h2` | aifoundry1-c1 | 101.7 | 78.0 | 0.94 | 19.97 | 0.55 | 2.23 | 2.26 | -0.03 | 0.3730 |
| `fadd.ps/random/h2` | aifoundry1-c1 | 118.1 | 75.8 | 1.67 | 35.86 | 1.04 | 3.75 | 4.03 | -0.29 | 0.3731 |
| `fmadd.ps/zeros/h2` | aifoundry1-c1 | 103.9 | 76.4 | 0.89 | 23.21 | 0.86 | 2.56 | 2.72 | -0.16 | 0.3641 |
| `fmadd.ps/const/h2` | aifoundry1-c1 | 104.4 | 76.7 | 0.96 | 23.54 | -0.40 | 3.61 | 2.49 | 1.12 | 0.3643 |
| `fmadd.ps/random/h2` | aifoundry1-c1 | 134.8 | 77.4 | 1.93 | 47.54 | 1.38 | 6.52 | 5.36 | 1.16 | 0.3651 |
| `nop/zeros/h2` | aifoundry1-c1 | 76.5 | 71.1 | 0.47 | 4.36 | 0.10 | 0.47 | 0.49 | -0.03 | 0.3902 |
| `fadd.pi/zeros/h2` | aifoundry2 | 82.5 | 69.0 | 0.78 | 10.51 | 0.37 | 1.84 | 2.01 | -0.17 | 0.3729 |
| `fadd.pi/const/h2` | aifoundry2 | 82.5 | 69.0 | 0.58 | 10.69 | 0.33 | 1.86 | 2.04 | -0.18 | 0.3730 |
| `fadd.pi/random/h2` | aifoundry2 | 99.8 | 78.0 | 1.17 | 16.62 | 0.55 | 3.41 | 3.19 | 0.21 | 0.3729 |
| `fadd.ps/zeros/h2` | aifoundry2 | 91.6 | 67.9 | 1.17 | 19.07 | 0.50 | 3.05 | 3.65 | -0.61 | 0.3730 |
| `fadd.ps/const/h2` | aifoundry2 | 93.9 | 69.6 | 1.20 | 19.52 | 0.60 | 2.97 | 3.75 | -0.78 | 0.3730 |
| `fadd.ps/random/h2` | aifoundry2 | 112.0 | 68.4 | 2.29 | 34.62 | 0.90 | 5.86 | 6.64 | -0.78 | 0.3730 |
| `fmadd.ps/zeros/h2` | aifoundry2 | 108.0 | 78.5 | 1.80 | 22.97 | 0.85 | 3.87 | 4.42 | -0.55 | 0.3641 |
| `fmadd.ps/const/h2` | aifoundry2 | 101.7 | 72.6 | 1.21 | 22.74 | 0.72 | 4.38 | 4.36 | 0.02 | 0.3640 |
| `fmadd.ps/random/h2` | aifoundry2 | 128.4 | 70.0 | 2.75 | 46.00 | 1.18 | 8.41 | 8.81 | -0.40 | 0.3648 |
| `nop/zeros/h2` | aifoundry2 | 71.0 | 65.4 | 0.40 | 4.20 | 0.03 | 1.02 | 0.79 | 0.24 | 0.3902 |

- **What an 8-lane add on zeros is made of** (aifoundry3): of `fadd.ps` zeros' 22.36 pJ above rest, 4.3-5.2 pJ is what a
  `fence` or a `nop` costs an issue slot (the awake core: fetch, decode, issue), so about 17 pJ is the vector unit working on zeros
  (register-file reads and the write-back of eight lanes, the FMA pipeline's control and clocks); `fadd.pi`'s integer short pipe
  takes 12.78 pJ in all. Random operands add 19.0 pJ to `fadd.ps` (2.4 pJ a lane) and 29.3 pJ to `fmadd.ps` (3.7 pJ a lane).
- **At rest the vector rows dwarf the work:** an instruction's share of the card's rest is 54-79 pJ, more than these three
  instructions' own 12-56 pJ above rest, because 2,048 harts retire 4.5e11 instructions a second against 25-36 W of rest.
- Card 1 against aifoundry3 after V squared, `fmadd.ps` random's minion rail: 1.131 (raw 1.030); `fadd.pi` random 1.134.

### Which lines differ between one-number fills, and how finely the data resolve them

Paired within each pass (the same session, the same footing), mean and 95% t half-width over passes, W; full table in
`anatomy-tables.md`.

| card (session, passes) | a - b | board D | minion rail | SRAM rail | NoC rail | off-rail |
|---|---|---:|---:|---:|---:|---:|
| aifoundry3 (E78, 6) | int8 -1 - int8 1 | +0.069 ± 0.116 | **+0.093 ± 0.018** | -0.005 ± 0.016 | -0.010 ± 0.019 | -0.010 ± 0.116 |
| card 1 (E82, 7) | int8 -1 - int8 1 | +0.116 ± 0.119 | **+0.162 ± 0.063** | -0.002 ± 0.013 | +0.001 ± 0.028 | -0.046 ± 0.084 |
| aifoundry3 (E78, 6) | fp32 pi - fp32 1.0 (both file tiles) | +0.090 ± 0.114 | +0.110 ± 0.134 | +0.001 ± 0.018 | -0.008 ± 0.021 | -0.013 ± 0.098 |
| card 1 (E82, 7) | fp32 pi - fp32 1.0 (both file tiles) | +0.129 ± 0.181 | +0.141 ± 0.172 | +0.012 ± 0.050 | +0.004 ± 0.044 | -0.028 ± 0.130 |
| aifoundry3 (E78, 6) | fp32 1.0 - fp32 -1.0 | -0.025 ± 0.154 | -0.004 ± 0.202 | -0.000 ± 0.023 | +0.009 ± 0.027 | -0.029 ± 0.121 |
| card 1 (E82, 7) | fp32 1.0 - fp32 -1.0 | +0.106 ± 0.135 | +0.014 ± 0.149 | +0.012 ± 0.020 | +0.024 ± 0.042 | +0.056 ± 0.071 |
| aifoundry3 (E78, 6) | fp16 1.0 - fp16 -1.0 | +0.067 ± 0.153 | +0.109 ± 0.140 | +0.011 ± 0.022 | +0.018 ± 0.035 | -0.072 ± 0.129 |
| card 1 (E82, 7) | fp16 1.0 - fp16 -1.0 | -0.090 ± 0.091 | -0.096 ± 0.161 | -0.055 ± 0.180 | +0.005 ± 0.027 | +0.055 ± 0.140 |
| aifoundry3 (E78, 6) | the same pi bytes, file - built-in (the floor) | +0.108 ± 0.140 | -0.005 ± 0.086 | +0.024 ± 0.020 | +0.031 ± 0.031 | +0.058 ± 0.085 |
| card 1 (E82, 7) | the same pi bytes, file - built-in (the floor) | +0.036 ± 0.123 | -0.004 ± 0.162 | +0.020 ± 0.075 | +0.022 ± 0.030 | -0.002 ± 0.178 |

- **On the TensorFMA, the only line that differs between committed one-number fills is the minion rail's data-dependent line:**
  int8 -1 against int8 1 reads +0.093 ± 0.018 W on aifoundry3 and +0.162 ± 0.063 W on card 1, resolved on both cards, while the
  board's own D cannot resolve it (±0.12 W): the off-rail remainder carries about ±0.1 W of noise a pass that the minion rail does
  not. (E178's registered bridge pair, int8 -1 against 1, is forecast at +0.110 W at the board; this reading of E78 and E82 is post
  hoc, of other sessions, and tests nothing of E178.) fp32 pi against 1.0 reads +0.11 / +0.14 W on the minion rail, the same sign
  on both cards, but not resolved for the two file tiles; against the built-in pi, which runs first and last in every pass, it reads
  +0.115 ± 0.087 / +0.145 ± 0.118 W, and that pass position also moves the SRAM and NoC rails by 0.02-0.04 W, so it is not
  counted. 1.0 against -1.0 reads zero in fp32 and fp16 within ±0.14-0.20 W, as E178's flip model ranks them (level: the sign
  bit never changes, and (-1)(-1) walks the accumulator as 1 x 1 does).
- **The SRAM and NoC rails resolve no data difference:** ±0.02-0.04 W, and the byte-twin pair (the same pi bytes from a file and
  from the host) reads +0.02-0.03 W on them: their floor is pass position and window heating, not data.
- **The lines at rest and awake cannot differ by construction** (each run's rest is read before it; the zeros anchor is shared),
  and the regulators' line and the window's heating move with the minion line (x0.181 and about 0.02 W per watt on aifoundry3).
- **On the vector unit, nothing resolves per card.** Constant (1.0f) against zeros, per card (3 passes): `fadd.pi` -0.06 / +0.06 /
  +0.16 pJ, `fadd.ps` +0.44 / +0.40 / +0.49 pJ, `fmadd.ps` +0.17 / +0.11 / +0.15 pJ at the board (aifoundry3 / card 1 /
  aifoundry2), each within ±0.3-2.1 pJ. Pooled over the three cards (card-blocked, df 6): `fadd.ps` +0.44 ± 0.44 pJ at the board and
  +0.38 ± 0.31 pJ on the minion rail, two of fifteen pooled line tests that clear zero (the board by 0.001 pJ), about what
  chance gives at 95% over fifteen correlated tests, so it is suggestive at best; `fmadd.ps`
  +0.15 ± 0.39 and `fadd.pi` +0.05 ± 0.22 pJ. That fits E178's dated note A1-2 (the float write-back returns to zero between
  results, so a result of 2.0, one 1-bit a lane, pays a small popcount term), which withdrew the reading of these rows as a "null";
  at this resolution the catalogue's rows cannot measure a 4s-against-5s term (one more 1-bit a lane). The vector arm's later
  registration owns that.

### Closing the books, and where each line ends up as heat

- **The books close by construction:** in every ledger the added lines sum to the board's own window reading (gap below 1e-13 W),
  because each run's reading splits exactly into its idle bracket, its switching over that bracket and the window's heating, and
  each part splits into three measured rails and a remainder. **The named gap is inside the remainder:** the off-rail watts above
  rest less the regulators' fitted delivery loss, **+0.95 nJ a step (2.0% of the board) for fp32 random on aifoundry3 and +1.19 nJ
  (2.2%) on card 1**; within ±0.2 nJ of zero for zeros, one-number and int8 steps (but for the one item flagged above); -0.8 to +1.2 pJ an
  instruction (under 1% of the board) on the vector rows. Its likely parts, none separable on these data: the off-rail domains' own heating (Q129 put a third
  to three quarters of the board's within-run rise off the three rails), the 19% of the board's leakage correction the registered
  reduction leaves off the minion rail, the SRAM and NoC rails' raw window heating, and the fit's own scale (Q136(b): the
  coefficient is 0.15-0.20, not 0.181 exactly).
- **What the books cannot split:** the 13.0 W (aifoundry3) and 16.3 W (card 1) off the rails at rest, among DRAM refresh, the DDR
  PHY, PCIe, the IO shire, the Maxion cores, PLLs and the regulators' own draw (the energy manual's section 4.3, "what the fit cannot
  say"); and the at-rest rails between leakage and clocks, because the idle data do not pin the leakage's e-folding (30-45 C puts
  aifoundry3's leakage at rest at 11.6-17.4 W, more than the three rails' 13.1 W at its upper end, so part of the temperature-
  dependent watts sits off the rails: the energy manual's slopes put about a sixth there).
- **Leakage, which law:** the level at rest uses each card's idle law from the energy manual (aifoundry3 12.3 W + 25.0 W
  e^((T-80)/36), card 1 14.1 W + 34.8 W e^((T-80)/36), aifoundry2 12.6 W + 23.3 W e^((T-80)/36)). The temperature slope at 58.9 C is
  0.386 W/C by aifoundry3's law, 0.3803 W/C by E71's dedicated idle cycles at 58-62 C and 0.40 W/C by E97's rests at 62.4 C;
  card 1's law gives 0.537 W/C. The window's heating line uses Q139(u)'s footing slopes (0.2056 W/C aifoundry3, 0.3134 W/C card 1),
  which are the registered reduction's correction, not a measured leakage: at E71's slope the line would be 1.85 times larger on
  aifoundry3 (0.88 W against 0.48 W for fp32 random), moving 0.4 W from the switching lines to it, with the books still closed.
  One law per card and operating point is a parallel desk lane's work (the stock-take's step 3), not this one's: it registered
  its footing law in `tools/claims-v3/footing-law/FOOTING-LAW.md` (lab `c14e5f35`, 22:46:56 PST, after these numbers were
  computed), with each session's slope at its own temperature, E171 0.3601 and E172 0.4930 W/C. At those slopes the window's
  heating line for fp32 random would be 0.84 W on aifoundry3 and 1.22 W on card 1 (1.75 and 1.57 times the footing's), taken
  from the switching lines with the books still closed; nothing here is re-run on it.
- **Where each line ends up as heat:** the three metered rails' watts (at rest, awake and data) are dissipated in the die: 34.8 W
  of 53.3 W (65%) for fp32 random on aifoundry3 and 39.0 W of 59.7 W (65%) on card 1, with most of the window's 0.5-0.8 W
  leakage rise beside them. The off-rail watts (about 34%) heat partly the die's unmetered domains (the IO shire, the PCIe and
  DDR PHYs, the Maxion cores), partly the card: the regulator modules (their conversion loss above rest, 3.9 W, 7.4%, on aifoundry3; 2.4 W, 4.0%, on card 1, plus an
  unmeasured fixed draw), the DRAM packages, the hot-swap FET and its 1 mOhm sense resistor (0.02 W) and the PMIC and other chips.
  No committed data splits the off-rail heat between the die and the board. The host's supply loss and its fans, outside the
  card's meter, heat the host. All of it ends as heat in the room: none is stored, apart from the die's and heatsink's warming
  during the window.
- **A public anchor, not an input:** Esperanto's measured split for its own DLRM FP16 runs (RISC-V Summit 2022, slides 14-15): a
  21-25 W card with a 13.5-16 W SoC, of which a thousand 600 MHz minions draw 6 W, 128 MB of SRAM 2.8 W and the NoC 1.8 W. Its
  workload, card and die temperature differ from these, so only its proportions are comparable, and they differ (minions 57% of the
  three rails there; 63% at rest here).

### The vector arm's public facts

In [`NOTE-2026-11-05-fmadd-ps-public-facts.md`](NOTE-2026-11-05-fmadd-ps-public-facts.md), a dated note of public facts only:
Esperanto's public TXFMA power virus flips 334 (hart 0) and 348 (hart 1) operand-port bits an instruction as each hart alternates
its two triples, or 318-352 if the two harts' instructions alternate one for one at the unit, against 286.7 expected for the lab's
random rotation and 0 for its constant column; the lab's random `fmadd.ps` costs 55.76 pJ at the board and 46.57 pJ on the minion
rail above rest (46.38 pJ at the device-time rate), at 0.730 issues per minion-cycle.

## How the lines were measured

- **Per run** (`anatomy_q145a.py`, pure Python, committed files only): E82 amendment A2's board-meter dip rule applied once to the
  pass's telemetry (as the registered primary and Q139(u)'s footing do), then `reduce_e78.py`'s windows: the board over
  [t0+1, t0+3) s, the idle bracket over [t0-1.2, t0-0.2) s, the die reading `minshire[0]` over both, and each rail deconvolved
  for its first-order lag (tau 0.95 s, delay 0.2 s). The board and the minion rail then take the footing's leakage correction
  exactly as the reduction does (k on the board, 0.81 k on the minion rail); the SRAM and NoC rails are raw, and their
  per-pass zeros-anchor interpolation is the reduction's own. Per (pass, item) the mean over kept runs, over passes the mean and
  a 95% t interval.
- **Lines:** at rest = the idle bracket (board; each rail's deconvolved bracket; off-rail = board less the three); awake = the
  zeros anchor over rest (S - D for the board, Srail - Drail and the like for each rail); data = D over the zeros anchor; the
  window's heating = k (T_window - T_idle bracket). For every run, board = rest + S + heating exactly. Energy per op = watts over
  the measured rate (work done in the window from the launch records, prorated); per MAC = per op over 4,096 / 8,192 / 16,384.
- **Vector rows:** the catalogue's own reduction (board over the busy window, idle the mean of the brackets either side, the
  rails over the burst's last 0.6 s divided by 0.94 for their filter, the leakage correction by the 21 Sep law), split the same way;
  energy per instruction = watts times wall seconds over instructions (the catalogue's pj_per_op).
- **Charge and electrons:** energy over the line's voltage (each rail's own die voltage monitor in the window: minion 521.6 /
  499 mV, SRAM 698 / 751 mV, NoC 484 / 486 mV on aifoundry3 / card 1; the energy manual's 518 / 523 / 499 mV (aifoundry2 /
  aifoundry3 / card 1) for the catalogue's minion rail; aifoundry2's SRAM and NoC at their 700 / 485 mV set points); off-rail lines at the nominal 12 V input; e =
  1.602176634e-19 C.

## Files

- `anatomy_q145a.py` - the script (pure Python; it reads the committed data and the public sources in `external/`).
- `anatomy.json` - every number: per session and item, per pass; every ledger with its lines and cross-cuts; the one-number and
  vector pairs; the card ratios; the virus flips with the operand words parsed; the inputs' sha256.
- `anatomy.txt` - the same as text, with the validation block first. `anatomy-tables.md` - every ledger as a table.
- `NOTE-2026-11-05-fmadd-ps-public-facts.md` - the vector arm's public facts.
- `SHA256SUMS` - this directory's files.

Re-make, from the top of the repository, after cloning github.com/aifoundry-org/et-platform at `836a4ab60` and
github.com/openhwfoundation/core-et at `b38a1a3` into `external/` (as the RTL bench does):

```
python3 -I docs/reports/data/2026-11-05-q145a-anatomy-top-lines/anatomy_q145a.py --repo . \
  --out docs/reports/data/2026-11-05-q145a-anatomy-top-lines/anatomy.json \
  --txt docs/reports/data/2026-11-05-q145a-anatomy-top-lines/anatomy.txt \
  --md docs/reports/data/2026-11-05-q145a-anatomy-top-lines/anatomy-tables.md
shasum -a 256 -c docs/reports/data/2026-11-05-q145a-anatomy-top-lines/SHA256SUMS
```

About 5 s on one core. *Compute for this lane:* slot jobs on the Intel, one at a time, at nice 10, one core each (the script,
its summaries and checks, each under 10 s); no bench, no mini, no lab box.
