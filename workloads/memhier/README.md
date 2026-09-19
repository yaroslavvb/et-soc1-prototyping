# memhier: measure the ET-SoC-1 memory hierarchy

Latency, bandwidth, capacity and energy per byte for each level of the memory hierarchy, measured on a
lab card. The results and the comparison with a modeled A100 are in
`docs/reports/2026-09-18-et-soc1-memory-hierarchy.html`.

The structure is the same as `workloads/sgemm`: the runtime API plus a minimal kernel, with no gp-sdk. It
builds against the lab machines' older `/opt/et`.

| Probe | What runs | What it measures |
|---|---|---|
| `--test chase --where dram` | One hart follows a random pointer chain (`p = *p`) over a working set from 256 B to 256 MB, each node on its own 64 B line | Load-to-use latency of L1, L2, L3 and DRAM, and the capacity where each step happens |
| `--test chase --where scp --scp-shire local\|all\|K` | The same chase over a chain written into a shire's L2 scratchpad | Scratchpad latency, locally and to every other shire (network-on-chip distance) |
| `--test stream --where dram --bytes-per-minion B` | Hart 0 of all 1024 minions streams 1 KB TensorLoads, which bypass the L1, from private slices; the per-shire total picks the level | L2 (8K), L3 (24K) and DRAM (256K) bandwidth |
| `--test stream --where scp-local\|scp-remote` | The same, from the shire's own scratchpad or one `--scp-shift` shires away | Scratchpad bandwidth, local and remote |
| `--test l1` | Both harts of every minion re-read a private 256 B buffer with 32 B vector loads | L1 hit bandwidth |
| `--test spin` | Both harts run an integer loop that touches no data | Power of busy cores, the baseline for L1 energy |

Things this relies on, from the PRM and the firmware in `/opt/et` (et-platform `353f20e`):
- Before every launch the firmware puts the L1 in **scratchpad mode** (PRM table 8.4). Each hart then has
  2 sets x 4 ways x 64 B = **512 B** of data cache, and sets 0-11 become the 3 KB scratchpad that only tensor
  loads use. Kernels cannot switch back to 4 KB shared mode from U-mode.
- Each shire's 4 MB of SRAM is split into 512 KB of L2, a 1 MB L3 slice and a 2.5 MB scratchpad. `DM_CMD_GET_SHIRE_CACHE_CONFIG`
  reports the chip totals as 16 MB, 32 MB and 80 MB.
- Scratchpad addresses use Format 0: `0x80000000 + (shire << 23) + offset`, where shire `0x7F` means the
  local shire (PRM 15.3). The firmware only uses the master shire's scratchpad (`system/layout.h`).

## Run

Build on the lab machine:

```bash
scripts/deploy-lab.sh aifoundry2 workloads/memhier
```

Latency sweeps hold the card for about 3-6 s each, and their outputs are checked: the chase's final pointer
must equal a host-side walk of the same chain.

```bash
ssh aifoundry2 'cd ~/nekko/build/memhier && timeout 10 host/memhier_host --test chase > chase-dram.jsonl'
ssh aifoundry2 'cd ~/nekko/build/memhier && timeout 10 host/memhier_host --test chase --where scp --scp-shire all --sizes 64K'
```

For bandwidth and energy, quit `et-powertop` first, because the power logger needs the management node.
Each configuration runs in its own `timeout 10` process.

```bash
ssh aifoundry2 'cd ~/nekko && python3 workloads/memhier/run_energy.py --host-bin build/memhier/host/memhier_host --out build/memhier-energy'
```

In the simulator, add `--sysemu --shires 0x1` to any command. That checks the kernels run correctly. The
simulator's timing is meaningless.

## Lab etiquette

The card is shared. Check `uptime`, `who` and `ps` first. Every command here holds the device for under 10 s
(`--budget 8` stops launching after 8 s), and builds use `nice -j4`.
