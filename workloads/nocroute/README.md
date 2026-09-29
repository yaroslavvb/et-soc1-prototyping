# nocroute: the mesh's stops and its routing order

The workload behind EXPERIMENT nocr ([`tools/claims-v3/nocr`](../../tools/claims-v3/nocr/README.md): hub rungs 31
and 32). Standalone, in the et-testdrive style of `workloads/memprobe` (runtime API and `et-common-libs` only); it
builds on each lab host against its own `/opt/et`:

```bash
cmake -S workloads/nocroute -B build/nocroute -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/nocroute -j4
```

(`tools/claims-v3/nocr/deploy.sh` does this on aifoundry1 and aifoundry3.) Run it only through the block, which
takes the card lock, checks `et-who` and wraps every run in `timeout 10`.

## Host: one plan, one line per launch

`nocroute_host [--sysemu] [--budget S] [--out-dir D] --plan PLAN` prints `NOCR {json}` per launch. Plan lines:

| Line | Launch |
|---|---|
| `mesh <name> <calls.bin> <caller_mask> <slot> <lead> <gap>` | R31: the callers take turns (caller k starts `lead + k * slot` cycles after its own kernel entry) running a list of u64 call entries, a multiple of 8 of them; results to `D/<name>.u32` (32 slots x n calls x {cycles, low 32 bits of a0}; the host fills it with 0xffffffff before each launch) |
| `fill <slice_bytes>` | every minion of every compute shire tensor-stores a fixed random 512 B pattern over its read slice of its own scratchpad |
| `read <label> <window> <slice_bytes> <src>dst,...>` | R32: the 32 minions of each dst shire stream 1 KB tensor loads (two in flight) from their slice of src's scratchpad for `window` cycles |
| `write <label> <window> <slice_bytes> <src>dst,...>` | R32w: the 32 minions of each src shire stream 512 B tensor stores into their slice of dst's scratchpad |

The host checks the whole plan before it opens the device, opens the ops node only (never the management node), and
stops launching past `--budget` (8 s on silicon). It registers libetrt's log levels first (the g3log race of
14-card-behaviour.md). A launch that has not finished after 6 s is aborted and its line says `"timed_out":true` (the
block then writes its HALT marker). A mesh caller is ok only if it answered, made every call, refused none and did
not overrun its slot.

## Kernel (`kernel/nocroute.c`, arguments in `nocroute_args.h`)

- **Call entries** (`kind | id << 8 | a << 16 | b << 24`, id 0xFF = the caller's own shire): `SC` =
  `syscall(SYSCALL_PMC_SC_SAMPLE, shire, bank, pmc)`, `MS` = `syscall(SYSCALL_PMC_MS_SAMPLE, ms, pmc, 0)`, `NOP` = the
  timer alone. What a call touches is the compiled firmware's code: `pmu.h`'s ESR pointers are not `volatile`, so
  the compiler merges the stop's and the start's read-modify-writes. In `MachineMinion.elf` (objdump; the same code
  in all three lab hosts' copies) pmc 0 is `ld ctl; sd ctl; ld counter; sd ctl` (2 loads, 2 stores), cache-bank pmc
  3 (`PMU_SC_ALL`) is `ld ctl; sd ctl | 0x20011` (1 load, 1 store), and pmc 7 matches no case and touches no ESR.
  The kernel refuses shire 33 and above 32, banks above 3, memory shires above 7 and any other pmc (it records
  0xffffffff and never makes that call).
- Each caller copies its list into its own scratchpad (2.25 MB in) during the lead-in and records its results there
  (2.3125 MB in), so no DRAM or L3 traffic happens during anyone's slot; the per-call timer is `hpmcounter3` with the
  late-carry correction (`fixcyc`), read around the `ecall` only (and at entry by hart 0 alone, after hart 1 has
  left: erratum 1.23). A caller whose program overruns its slot reports error 3 and the host marks it not ok. L1 is
  not coherent, so each caller's results must fill whole 64 B lines of the output: the kernel refuses (error 4, and
  writes nothing) a call count that is not a multiple of 8 or an output that is not 64 B-aligned; `nocr.py` pads
  every list with timed no-ops.
- **Scratchpad layout** per compute shire: 256 KB-1.25 MB the read slices (minion m at +m x 32 KB), 1.25-2.25 MB the
  write slices, 2.25-2.375 MB R31's list and results. Offset 0 is never used (it faults). Reads and writes refuse a
  partner that is not a compute shire (never 32, the master, whose scratchpad holds the firmware's buffers) or is
  the shire itself.
- The tensor load, store and wait encodings are enercat's (`workloads/enercat/kernel/enercat.c`), proven on all
  three cards; only hart 0 of a minion issues tensor ops.

## Mesh map and stream sets (`meshmap.py`)

marty1885's logical map (a copy of `workloads/nocbench/analyze.py`'s `MARTY` and `EMPTY`; `reduce.py` checks they are
equal), dimension-order routes on it, the packets of each flow (a read's requests dst -> src and replies src -> dst;
a write's stores src -> dst and acknowledgements dst -> src), weighted max-min link sharing (a control packet costs
c of the data it stands for; one network or separate request and reply networks), and R32's sets: `python3
meshmap.py` prints every set with the rho that each order, link capacity and c predicts, and checks every design
property: under the sharing order all of a family's replies cross its link and no two of its requests share one;
under the other order no two replies share a link and all requests cross the reversed link; no link carries a reply
of one flow and a request of another; distinct compute-shire endpoints; negative controls share nothing, replies or
requests, under either order.
