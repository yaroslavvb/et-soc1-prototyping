# E178's bench counts: the RTL toggle bench on the one-number tiles

*Thu 5 Nov 2026 (week 45), PST, on the mini, desk only, for E178's registration (`../E178.md` section 4). No card was used.*

**What ran.** `rtl-sim/fma_toggle_v2` (core-et `b38a1a3`'s whole `vpu_top` under Verilator 5.052 with `-fno-dfg`), the
recorded Q141(t2) build on the mini, used read-only: `Vtb` sha256 `a740318ce8d8a097…`, `run_kinds.py` `fa8112e9ff953f71…`
and `accum.c` `dc47efbc32e3c45b…` (both equal to this repo's), `settle_count` `9da18b7582db59ba…`, the build's `maps/`.
`bench_e178.sh` is the exact sequence, through `run_remote --host mini` (section 28 of the round's brief: batch work leaves the
Intel).

| file | what | when (PST) |
|---|---|---|
| `counts-e178.json` | `run_kinds.py` unchanged over the 40 E178 tiles and each format's committed zeros tile, at its three launch points (1/6, 1/2, 5/6 of a 0.5 s launch at 600 MHz), 3 jobs | 20:21:50-20:27:28 |
| `vcd-signals-e178-1.json` | `../vcd_signals_e178.py`: per-signal toggles of one op, 14 points (int8 and fp32) | 20:21:03-20:21:50 |
| `vcd-signals-e178-2.json` | the same, 14 more points (the crossed pairs, fp16, more fp32) | 20:26:2x-20:27:14 |

**Checks.**
- `check_mismatch` is 0 at all 129 points: after every measured op the bench's accumulator words equal software's (accum.c)
  at every one of the 256 words. No count here comes from a run that failed the check (the bench README's rule).
- **The build check** (section 28: a count from the mini's build is checked against the Intel's before it is quoted): the
  mini's `zeros`, `ones` and `neg_ones` rows equal `docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json`'s (the Intel
  build, the counts M10 was fitted on) in every format, to the net: VPU `nets_map` 58,258 / 58,382 / 19,068 (zeros), 97,693.3 /
  97,876 / 30,940 (ones), 97,693.3 / 97,876 / 38,108 (neg_ones); unit `nets_map` likewise.
- `vcd_signals_e178.py` counts every value change of every VCD id (unsettled, unmerged, all names), so its totals are larger
  than `nets_map`'s; it is a reading of which signals move and how, for the flip model's structure, never a count M10 uses.

**What the signal-level reading shows** (E178.md section 3 builds on it): in a one-number tile no operand word moves (the A and
B words at every unit's inputs hold); what moves is the accumulator (its storage, its read and write data), a write-back bus that
is zero between k-passes (floats: `f8_txfma_res` / `f8_wdata` / `vpu_rf` `wr_data[0]`, copied into three bypass registers,
`vpu_rf.v:33-46`), TenB's bypass read data, zero once a k-group (int8: `ex_bypass_tenb_rf_rdata`, 256 x popcount of the B word
an op: 1,024 for 0x01010101, 8,192 for 0xFFFFFFFF), and the scratchpad's read data when A and B differ (62 A/B switches an op in
the floats, 32 in int8). For int8, the classifier files TenC (`.lane_tima.tenc_rf`) under `lane_operand_bus`, so M10's int8
`bus` term carries the accumulator's flips; `c_regfile` is 0 for int8 because that stage is the float RF only.
