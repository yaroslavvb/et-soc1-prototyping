# sparsity: what ET-SoC-1 does with zeros

Probes of the chip's sparsity hooks, measured on a lab card: tensor-unit zero-skipping, masked TensorLoads, a
batch-1 sparse layer, and work items of very different lengths. The results, and the scenarios where the chip
could beat an A100, are in `docs/reports/2026-09-18-et-soc1-sparsity.html`.

The structure is the same as `workloads/memhier`: the runtime API plus a minimal kernel, with no gp-sdk. It
builds against the lab machines' older `/opt/et`.

| Probe | What runs | What it measures |
|---|---|---|
| `--test fma --type fp32\|fp16\|int8 --pattern elem\|col\|row\|pair\|none --sweep 0,0.5,1` | Hart 0 of each minion repeats one 16x16 TensorFMA with A and B in the L1 scratchpad, with a chosen fraction of A zero | Whether zeros save cycles (`--b-sparsity`, `--row-mask`, `--b-stream` vary B and the tensor_mask) |
| `--test tload --where dram\|l2\|scp --masks 0xFFFF,0xFF,0x1` | 16-line TensorLoads under a fixed tensor_mask. The DRAM buffers add up to more than the 32 MB L3 (64 MB for a lone minion) | Whether masked-off lines cost time or bandwidth |
| `--test gemv --gemv dense\|masked\|skip [--gemv-tree] --sweep 0,0.9,0.99` | y = W x, 1024 x 4096 fp32, W in each shire's scratchpad, all 1024 minions | Batch-1 layer latency against activation sparsity: each 16-output block's slowest minion, from the barrier that starts the layer |
| `--test diverge --variant static\|refill\|scalar --alpha A` | Items that need k FMA iterations, k from a Pareto distribution, on 8 SIMD lanes per hart | Lane efficiency and throughput against the tail of k |
| `--test spin` | Integer loop on hart 0 | Power baseline |

Every result is checked on the host. Inputs are small integers, so fp32, fp16 and int8 results are exact (fp32 and
fp16 while the sums stay below 2^24; longer runs are marked `unchecked`).

Things this relies on:
- TensorFMA and TensorLoad encodings follow PRM 9.4. Only hart 0 of a minion may issue tensor ops. After a tensor op
  writes the vector registers, an `fmv.x.w x0, fN` must come before other reads (errata 1.29 type F). A vector
  register must not be read within 8 instructions of a packed or FP write unless a taken branch comes between
  (types B and C). The simulator's `-vpurf_warn` checks this; `-vpurf_check` aborts on the firmware's own code, so it
  cannot be used with a full boot.
- TensorFMA16A32/32 with A of 4 rows (TENB=0) or 1-4 rows (TENB=1) hit errata type D. The layer uses 1-row A with B in
  the L1 scratchpad, which is safe.
- `--gemv-tree` sums partial rows with TensorReduce (levels 0-3, inside a shire). Without it every minion writes its
  partial row and the host adds them. A TensorStore to the scratchpad followed by a TensorLoad from another minion is
  not safe without draining the shire cache's coalescing buffers (the simulator's memory checker flags it), so the
  kernel does not do that.
- The layer's barrier polls its credit counter and gives up after 2^26 reads, so a minion that never arrives fails the
  run instead of stalling the shared card.

## Run

Build on the lab machine:

```bash
scripts/deploy-lab.sh aifoundry3 workloads/sparsity
```

`run_lab.sh` runs the cycle-count sweeps (groups `fma tload gemv diverge`, or name some of them after the output directory). Each command is its own `timeout 10`
process with `--budget 8`, and the script waits until no other process holds the card. It also logs the minion clock
and board power.

```bash
ssh aifoundry3 'cd ~/nekko && bash workloads/sparsity/run_lab.sh build/sparsity/host/sparsity_host build/sparsity-data'
ssh aifoundry3 'cd ~/nekko && python3 workloads/sparsity/run_energy.py --host-bin build/sparsity/host/sparsity_host --out build/sparsity-data/energy-a'
```

Quit `et-powertop` first, because both read `/dev/et0_mgmt`, which allows only one opener. The report averages two
energy runs; the second (`energy-b`) used `--only` to run the configurations in reverse order. Copy the data back and
summarize it:

```bash
python3 workloads/sparsity/analyze.py docs/reports/data/2026-09-18-sparsity-aifoundry3 --embed docs/reports/2026-09-18-et-soc1-sparsity.html
```

In the simulator, add `--sysemu` to any `sparsity_host` command. That checks the kernels and the data; the
simulator's timing means nothing.

## Lab etiquette

The card is shared. Check `uptime`, `who` and `ps` first. Every command here holds the device for under 10 s, and
builds use `nice -j4`.
