# onchip: does shire-to-shire communication beat main memory?

A shire's own L2 scratchpad runs at about 2.5 TB/s and another shire's at about 1 TB/s, against 76 GB/s of
DRAM for the whole chip. This workload asks whether a computation can be arranged to collect that.

| Probe | What runs | What it answers |
|---|---|---|
| `--test probe [--method 0\|1] [--shift K]` | Every minion writes a 1 KB pattern into its own shire's scratchpad, by tensor store or by plain vector stores; a second launch has every minion read and check the block the shire `K` places away wrote | Can one shire read what another wrote, and by which write path |
| `--test relay --medium dram\|scp\|hop` | K stages over a slab per shire: each stage reads the previous stage's output, adds 1.0 to every element and writes its own. `dram` puts the intermediate in DRAM, `scp` in this shire's scratchpad, `hop` where the next shire will read it | Whether the hand-off beats main memory, and by how much |

Knobs for `relay`: `--stage-bytes` per shire per stage (256 KB + two buffers must fit the 2.5 MB scratchpad,
so at most 1 MB), `--stages`, `--work` (vector adds per element: the arithmetic-intensity knob), `--shires`,
`--hop-distance` (how many shire IDs back round the ring a stage reads from; shire IDs do not follow the mesh, so
this is not a count of mesh hops, and `onchip.json` records the mesh hops each offset spans).

```bash
scripts/deploy-lab.sh aifoundry2 workloads/onchip
workloads/onchip/run_onchip.sh DATA                 # 88 configurations, milliseconds of card time each
tools/ettelem/run_onchip_power.sh DATA 12           # board power, one burst per medium
python3 workloads/onchip/analyze_onchip.py DATA/sweep.jsonl DATA3/sweep.jsonl --power DATA --out onchip.json   # DATA3: the second card's sweep
```

Results and the full argument: `docs/findings/18-on-chip-relay.md` and
`docs/reports/2026-09-22-on-chip-relay.html`.

## Things it relies on, and things that bite

- **Scratchpad addressing** is the PRM's format 0: `0x80000000 + (shire << 23) + offset`, with `0x7F` meaning
  the local shire. **Offset 0 faults**, so the buffers start 256 KB in.
- **A tensor store bypasses the L1 and L2 caches**, which is what makes the hand-off safe: what one shire
  writes, another reads with no stale line possible. Inputs are plain vector loads from addresses the reading
  minion has never written, and a minion's chunk is sixty-four times its 512 B of L1, so nothing it touched
  two stages ago survives. Every run verifies its own output element by element rather than assuming this.
- **Each shire starts its slab filled with its own number**, so the final contents say which shire the data
  came from. With `--medium hop` shire 0 ends holding the value of the shire `stages` places back round the
  ring — that is how a run proves the data really moved.
- **Never spin on a global atomic in a barrier.** The chip barrier here is the credit-release shape
  `nocbench` measures at about 5,000 cycles: one atomic per shire, nobody polling. An earlier version had
  every shire's leader poll one counter, which starves that line's home shire of its own memory
  (`docs/findings/17-hot-line.md`) and hangs the barrier.
- **This core traps on 64-bit integer-to-float conversion**, so a `double` in a kernel checksum kills the
  launch. Sum bit patterns as integers.
