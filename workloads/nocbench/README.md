# nocbench: on-chip communication on ET-SoC-1

Latency, bandwidth and energy of the ways ET-SoC-1 cores talk to each other, measured on a lab card. The
results, the shire layout, and the comparison with GPUs are in
`docs/reports/2026-09-18-et-soc1-on-chip-communication.html`.

GPUs connect their SMs through L2. ET-SoC-1 has direct paths. Hart 0 of any minion can send up to 127 × 32 B
(about 4 KB, cycling through its 32 vector registers) straight into another minion's registers with
`TensorSend`/`TensorRecv`. The receiver
can add, max or min what arrives into what it holds. Hardware trees do reductions and broadcasts, and credit
counters and barrier counters let cores wait on each other without polling memory. The 32 compute shires, with
the master, spare, I/O and PCIe shires, form a 6x6 grid on the mesh (8x6 stops with the memory shires down two sides).

The structure is the same as `workloads/memhier`: the runtime API plus a minimal kernel, with no gp-sdk. It
builds against the lab machines' older `/opt/et`.

| Probe | What runs | What it measures |
|---|---|---|
| `--test pairs --pairs 0.0-0.1,0.0-5.0` | Minion pairs bounce `--counts` registers back and forth with TensorSend/TensorRecv (one pair at a time, with a chip-wide barrier between them) | Round-trip time by distance: same neighbourhood, same shire, k mesh hops |
| `--test pairs --mode stream` | The first minion of each pair only sends; the second only receives | Time per message, and one link's bandwidth |
| `--test pairs --funct iadd\|imax\|fadd` | The receiver combines instead of overwriting | Cost of the combine in the channel |
| `--test pairs --mode fcc\|flag` | Credit round trips (a store to the partner shire's CREDINC register, a blocking FCC read), or flag round trips through global atomics on DRAM lines | Hardware credits, and the GPU way of signalling between cores through L3 |
| `--test matrix [--mode ...] [--minion M]` | Every pair of the 32 shires, minion M of each | The shire-to-shire latency matrix, which checks the 6x6 layout |
| `--test intra --shire S` | Every pair of the 32 minions inside one shire | Which pairs use the neighbourhood's fast local network |
| `--test shift --rings pair\|neigh\|shire\|xshire:K` | Every minion sends to the next one in its ring and receives from the previous one, all at once | Aggregate bandwidth, and energy per byte by distance (`run_energy.py`) |
| `--test allreduce --levels 1,...,10` | TensorReduce up the hardware tree, then TensorBroadcast down, over 2 to 1024 minions | Allreduce latency against the number of cores |
| `--test barrier --scope shire\|chip` | Fast-local-barrier counters plus credits, and a chip-wide version with one global atomic per shire | Barrier latency |
| `--test hotline --home S\|own\|scp:S\|scplocal:S\|dramlocal:S\|scpstream:S\|dramstream:S` | Many-to-one contention on one global atomic word, homed in a chosen shire. Reports each shire's share of a common, barrier-aligned window. `scplocal`/`dramlocal`/`scpstream`/`dramstream` make the host shire do ordinary local memory work instead of joining, which is what actually starves. `--pace` slows the remote side | Who the shire cache serves |
| `--test spin` | Hart 0 of every minion runs an integer loop | Power of busy cores that move no data |

Things this relies on (PRM chapters 7, 9.4, 10 and 11, checked in `sw-sysemu/insns/tensors.cpp`):
- Only hart 0 of a minion may issue TensorSend, TensorRecv, TensorReduce and TensorBroadcast. The target is a
  minion ID, `shire * 32 + minion`, and the partner is hart `2 * ID`. Both sides must name each other and use
  the same COUNT, otherwise they wait forever.
- A receiver announces itself with a "ready" message before the sender transmits. Each minion has **one**
  peer-to-peer ready bit, not one per partner (`partner_ready_peer` in core-et `dcache_reduce.v`). If two partners'
  readies overlap, one is lost and both of them stall for good. So a minion may change partners only across a barrier.
  Tree operations keep one bit per level and are safe. The simulator tracks partners separately and never shows this.
- A pending transfer stalls every instruction that touches a vector register on that core. `TensorWait 9`
  waits for all of them.
- The tree operations pair minion `m` with `m +/- 2^h` at level `h`. Levels 0-2 stay inside a
  neighbourhood (8 minions), levels 3-4 inside a shire, and levels 5-9 cross shires. Level 10 would reach
  the master shire, so the host refuses it.
- Reading a register a tensor operation wrote needs an `fmv.x.w x0, fN` first (errata 1.29 type F).
- Credits go to thread 0 of the minions in a mask through the `CREDINC0/1` registers of the target shire
  (user-mode ESRs). The firmware empties the credit counters and clears the barrier counters around every
  launch, so a finished kernel must leave no credit in flight.

Every schedule is checked on the host before launch. Each rendezvous needs a partner that names it back, rings
alternate send-first and receive-first, and on silicon no minion may change partners without a barrier. Pairs run one
per round with a chip-wide barrier in between, unless `--concurrent` is given and no minion has two partners. Credit
waits that cross shires poll `fccnb` and give up after `--poll-limit` reads instead of blocking. A TensorSend or
credit wait that nobody answers stalls the hart for good, the firmware's abort cannot free it, and on a shared card
that means asking the lab admin for a power cycle.

## Run

Build on the lab machine:

```bash
scripts/deploy-lab.sh aifoundry2 workloads/nocbench
```

`run_lab.sh` runs the latency, size, collective and barrier probes. Each is its own `timeout 10` process
with `--budget 8`. Before each one the script waits until no other process holds the card. It also logs the
minion clock and board power, because the DVFS governor moves the clock between 600 and 800 MHz (three points: 600, 700, 800), and time
spent on the mesh is fixed in ns rather than in cycles.

```bash
ssh aifoundry2 'cd ~/nekko && bash workloads/nocbench/run_lab.sh build/nocbench/host/nocbench_host build/nocbench-data'
ssh aifoundry2 'cd ~/nekko && python3 workloads/nocbench/run_energy.py --host-bin build/nocbench/host/nocbench_host --out build/nocbench-data/energy-a'
```

Quit `et-powertop` before either one, because both read `/dev/et0_mgmt`, which allows only one opener. The report
averages two energy runs, `energy-a` and `energy-b`. The second used `--only` to run the configurations in reverse order.
Then copy the data back and summarize it:

```bash
python3 workloads/nocbench/analyze.py docs/reports/data/2026-09-18-nocbench-aifoundry2 --memhier docs/reports/data/2026-09-18-memhier-aifoundry2 --search
```

In the simulator, add `--sysemu` to any `nocbench_host` command with small `--iters`. That checks that the
schedules and the data movement are right. The simulator's timing means nothing.

## Lab etiquette

The card is shared. Check `uptime`, `who` and `ps` first. Every command here holds the device for under 10 s,
and builds use `nice -j4`.
