# E64 data: Horace — power limit (Q123, Fri 23 Oct 2026, aifoundry2)

Which of the governor's two limits, the 65 W power test or the 65 °C thermal test, sets the Horace matmul's speed on
aifoundry2's card, and when. Pre-registered in [`tools/claims-v3/hpl/`](../../../../tools/claims-v3/hpl/README.md)
(`2b951fca`, before the first card access; amendments A0 `4b2b1401`, A1 `69380c49`, A2 `1a899d8f`). The page:
[Power, then heat: what limits the ET-SoC-1's matmul speed](https://spacesheep.dev/@yaroslavvb/et-soc1-power-limit).

Three card sessions, all on aifoundry2 with nothing set on the card (TDP 65 W and threshold 65 °C read back after
every run):

| Session | When (PDT) | What |
|---|---|---|
| `smoke2/` | 20:31:56–20:32:23 | the smoke: four 2 s launches (fp32, fp16, int8 random, fp32 zeros); not analysed. (`smoke`, 20:31:29, ended before any launch: amendment A0) |
| `s1/` | 20:37:01–21:08:43 | the registered session: LAD (20 runs), MIN (6), HOT (8), SUS (9) |
| `s2/` | 21:09:24–21:11:11 | HOT2 (4 runs, amendment A2) |

| Path | What |
|---|---|
| `s*/session.json`, `end.json`, `run.log`, `manifest.txt` | the protocol as run, the code's sha256 (runner, heater, kernel, ettelem), the git head, the stop reason, `et-lab-manifest` |
| `s*/runs.jsonl` | one line per run: its gate (the die reading it launched at), its launch processes, the management queries after it (config, residencies) |
| `s*/launches.jsonl` | every device process: the command, its timing and its `SPARSITY` lines (per ~0.5 s launch: cycles, wall time, the kernel's own clock) |
| `s*/tel/<run>.jsonl` | the sampler, 10 Hz, from the gate to the end of the idle tail (no `--reset-ms`) |
| `s*/sp/<run>.bin` | the service processor's 4 KB trace ring, dumped after each run: read it with `tools/claims-v3/hpl/sptrace_full.py` |
| `s*/marks.jsonl`, `queries.jsonl` | the runner's marks; the start and end queries |
| `results.json`, `reduce.txt`, `results.md` | `reduce_hpl.py s1 s2`: per-run metrics, every governor entry placed on the host clock, the four registered rules |
| `figures.json`, `surface.txt`, `page_text.json` | `surface_hpl.py` (powers per clock, the governor model, the cap table, the thermal line, the surface) and `page_text_hpl.py` |

Rebuild (any machine with Python 3; no third-party modules):

```bash
cd docs/reports/data/2026-10-23-e64-horace-power-limit    # the telemetry is gzipped; the reducer reads .gz
python3 ../../../../tools/claims-v3/hpl/reduce_hpl.py s1 s2 --out results.json > reduce.txt
python3 ../../../../tools/claims-v3/hpl/surface_hpl.py results.json --out figures.json > surface.txt
python3 ../../../../tools/claims-v3/hpl/summary_hpl.py --results results.json --figures figures.json > results.md
python3 ../../../../tools/claims-v3/hpl/page_text_hpl.py --results results.json --figures figures.json --out page_text.json
python3 ../../../../tools/claims-v3/hpl/build_page_hpl.py --results results.json --figures figures.json --text page_text.json \
    --out ../../2026-10-23-horace-power-limit/index.html
```

## Results

### The registered rules

| Rule | Verdict | Counts |
|---|---|---|
| R1 | **PASS** | {"population": 10, "with_power_down_first": 10, "die_le_65_at_first_step": 10} |
| R2 | **PASS** | {"population": 10, "with_power_down": 0} |
| R3 | **PASS** | {"a_population": 4, "a_held_600_until_65": 4, "b_population_reaching_66": 4, "b_thermal_not_power": 4, "a_excluded_not_hot_at_start": ["HOT2-00-fp32-ones-hot66-r1", "HOT2-01-fp32-zeros-hot66-r1", "HOT2-00-fp32-ones-hot66-r2", "HOT2-01-fp32-zeros-hot66-r2"]} |
| R4 | **PASS** | {"randn_thermal_share_ge_0.6": true, "zeros_at_800_ge_0.9": true, "randn_sampler_only_hot_share_ge_0.6": true} |

### The cool-die ladder (LAD, MIN): each run's power at 800 MHz and its clock after the start ramp

| operands | minions | runs | W at 800 MHz | mean MHz after 1.5 s | TFLOPS, whole run | power steps down | first step |
|---|---|---|---|---|---|---|---|
| zeros | 1024 | 2 | 35.0 | 800 | 12.11 | 0 | None |
| sparse75 | 1024 | 2 | 40.2 | 800 | 11.94 | 0 | None |
| ones | 1024 | 2 | 50.2 | 800 | 11.98 | 0 | None |
| randn | 512 | 2 | 55.8 | 800 | 5.89 | 0 | None |
| signs | 1024 | 2 | 60.0 | 800 | 11.86 | 0 | None |
| pow2 | 1024 | 2 | 62.5 | 800 | 12.03 | 0 | None |
| randn | 640 | 2 | 62.5 | 800 | 7.37 | 0 | None |
| a_randn_b_ones | 1024 | 2 | 65.5 | 785 | 11.80 | 6 | power_down |
| randn | 768 | 2 | 69.1 | 774 | 8.61 | 13 | power_down |
| a_ones_b_randn | 1024 | 2 | 72.7 | 741 | 11.21 | 18 | power_down |
| mant | 1024 | 2 | 78.0 | 725 | 10.75 | 20 | power_down |
| uniform | 1024 | 2 | 79.2 | 711 | 10.86 | 21 | power_down |
| randn | 1024 | 2 | 82.2 | 710 | 10.61 | 20 | power_down |

### Hot starts (HOT, HOT2)

| run | die at launch | mean MHz | thermal steps | power steps | first step |
|---|---|---|---|---|---|
| HOT-01-fp32-ones-edge63-r1 | 63 | 771 | 8 | 0 | thermal_down |
| HOT-03-fp32-zeros-edge63-r1 | 63 | 800 | 5 | 0 | None |
| HOT-00-fp32-ones-edge67-r1 | 66 | 688 | 10 | 0 | thermal_down |
| HOT-02-fp32-zeros-edge67-r1 | 66 | 796 | 7 | 0 | thermal_down |
| HOT-02-fp32-zeros-edge67-r2 | 66 | 739 | 6 | 0 | thermal_down |
| HOT-01-fp32-ones-edge63-r2 | 64 | 704 | 10 | 0 | thermal_down |
| HOT-03-fp32-zeros-edge63-r2 | 63 | 800 | 4 | 0 | None |
| HOT-00-fp32-ones-edge67-r2 | 66 | 635 | 11 | 0 | thermal_down |
| HOT2-00-fp32-ones-hot66-r1 | 65 | 784 | 9 | 0 | thermal_down |
| HOT2-01-fp32-zeros-hot66-r1 | 65 | 800 | 8 | 0 | None |
| HOT2-00-fp32-ones-hot66-r2 | 65 | 741 | 10 | 0 | thermal_down |
| HOT2-01-fp32-zeros-hot66-r2 | 65 | 800 | 6 | 0 | None |

### Sustained (SUS): the last 40 s of about 80 s

| type | operands | rate at 800 MHz | cool die, first 8 s | sustained (kernel) | sustained (wall) | MHz | die °C | board W | at 800 | thermal | power | ramp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp16 | ones | 24.6 | 24.6 | 22.3 | 21.7 | 737 | 65.4 | 49.3 | 0.48 | 0.52 | 0.00 | 0.00 |
| fp16 | randn | 24.6 | 22.0 | 18.4 | 17.8 | 600 | 66.1 | 51.3 | 0.00 | 1.00 | 0.00 | 0.00 |
| fp16 | zeros | 24.6 | 24.6 | 24.4 | 23.7 | 794 | 59.0 | 36.1 | 0.97 | 0.00 | 0.00 | 0.03 |
| fp32 | ones | 12.3 | 12.3 | 11.1 | 10.8 | 738 | 65.4 | 49.4 | 0.48 | 0.52 | 0.00 | 0.00 |
| fp32 | randn | 12.3 | 10.7 | 9.2 | 8.9 | 600 | 67.1 | 54.4 | 0.00 | 1.00 | 0.00 | 0.00 |
| fp32 | zeros | 12.3 | 12.3 | 12.3 | 12.0 | 800 | 59.0 | 36.4 | 1.00 | 0.00 | 0.00 | 0.00 |
| int8 | ones | 84.4 | 84.4 | 84.3 | 81.7 | 800 | 61.7 | 41.8 | 1.00 | 0.00 | 0.00 | 0.00 |
| int8 | randn | 84.4 | 84.4 | 79.5 | 77.1 | 763 | 65.3 | 50.7 | 0.66 | 0.34 | 0.00 | 0.00 |
| int8 | zeros | 84.4 | 84.4 | 84.3 | 82.2 | 800 | 59.0 | 37.6 | 1.00 | 0.00 | 0.00 | 0.00 |

### The model (descriptive)

- Power per clock, referred to a 58 °C die: busy offsets {"600": 25.5, "700": 28.2, "800": 33.6} W plus each run's switching term × (V/0.517)²·f/600; rms 0.82 W over 103 points.
- The governor: a first-order average of the board's power, time constant 1.3 s, compared with the level once per 0.24 s pass, one point up or down; mean clock after the ramp reproduced to 3.3 MHz rms over 26 cool-die runs.
- The thermal line over the SUS runs' last 40 s: die = 41.88 + 0.4696 °C per W of board power; it reads 65.5 °C at 50.3 W.

**The cap table** (the model on each measured kind's own powers, cool die, mean MHz):

| type | operands | 35 W | 45 W | 55 W | 65 W | 75 W | 85 W |
|---|---|---|---|---|---|---|---|
| fp16 | zeros | 779 | 800 | 800 | 800 | 800 | 800 |
| fp16 | ones | 609 | 724 | 800 | 800 | 800 | 800 |
| fp16 | randn | 600 | 600 | 655 | 715 | 773 | 800 |
| fp32 | zeros | 776 | 800 | 800 | 800 | 800 | 800 |
| fp32 | sparse75 | 697 | 800 | 800 | 800 | 800 | 800 |
| fp32 | ones | 600 | 718 | 800 | 800 | 800 | 800 |
| fp32 | signs | 600 | 664 | 752 | 800 | 800 | 800 |
| fp32 | pow2 | 600 | 652 | 736 | 800 | 800 | 800 |
| fp32 | a_randn_b_ones | 600 | 633 | 712 | 791 | 800 | 800 |
| fp32 | a_ones_b_randn | 600 | 600 | 682 | 752 | 800 | 800 |
| fp32 | mant | 600 | 600 | 661 | 721 | 779 | 800 |
| fp32 | uniform | 600 | 600 | 652 | 712 | 773 | 800 |
| fp32 | randn | 600 | 600 | 636 | 700 | 755 | 800 |
| int8 | zeros | 758 | 800 | 800 | 800 | 800 | 800 |
| int8 | ones | 748 | 800 | 800 | 800 | 800 | 800 |
| int8 | randn | 609 | 733 | 800 | 800 | 800 | 800 |
