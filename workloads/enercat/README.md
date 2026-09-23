# enercat: the energy catalogue

Every hart runs one kind of operation flat out until a cycle deadline and reports how many it completed,
while the host's power logger runs. Energy per operation is what is left over idle, divided by the rate.

| `--pattern` | What every hart does | Unit |
|---|---|---|
| `spin` | 8 independent `addi` | an awake core doing the least it can |
| `iadd`, `ixor`, `imul` | scalar integer, sources from the operand buffer | instruction |
| `fadd_s`, `fmul_s`, `fmadd_s` | scalar float | instruction |
| `fadd_ps`, `fmul_ps`, `fmadd_ps` | 8-lane vector float | instruction (8 lanes) |
| `iadd_pi`, `imul_pi` | 8-lane vector int32 | instruction (8 lanes) |
| `fexp_ps`, `frcp_ps` | transcendental unit | instruction (8 lanes) |
| `ld_l1`, `st_l1` | `flw.ps` / `fsw.ps` on a 256 B buffer that stays in the hart's L1 | byte |
| `st_stream` | `fsw.ps` streaming over a per-hart DRAM slice: the L1 write-back path | byte |
| `tstore`, `tload` | tensor store / load streaming over a per-hart slice; `--scp` puts the slice in the shire's own scratchpad | byte |

`--operands zeros|const|random` fills the 256 B source buffer every hart reads its operands from: all zeros,
1.0f everywhere, or floats in [0.5, 2). Sources are never overwritten and sinks never read, so the switching
a unit sees is "the next pair of operands", which is what a stream of real data looks like.

```bash
scripts/deploy-lab.sh aifoundry2 workloads/enercat
workloads/enercat/run_enercat.sh DATA 5              # 56 configurations, about 12 minutes of card time
python3 workloads/enercat/analyze_enercat.py DATA_A2 DATA_A3 --out enercat.json
```

`run_enercat.sh` brackets every burst with six seconds of idle; `analyze_enercat.py` subtracts the mean of the
two brackets and the extra leakage of a burst that ran warmer than them (the slope of the idle law from
`docs/findings/11-thermal-model.md`), and reports pJ per operation and per byte, raw and corrected, with the
die temperature. Results: `docs/energy-manual/` and `docs/reports/2026-09-23-energy-manual.html`.

Things that bit: `fdiv.ps` and `fsqrt.ps` trap (no hardware divide); a `double` anywhere in a kernel traps
too (64-bit integer-to-float conversion); the transcendental unit issues at a quarter of the rate and a
64-bit `mul` at an eighth, so their per-instruction cost is mostly the awake core amortised over a slow op.
