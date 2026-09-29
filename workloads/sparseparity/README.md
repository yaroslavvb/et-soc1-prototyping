# sparseparity: noisy sparse parity on the ET-SoC-1

The design is [`docs/research/sparse-parity/DESIGN.md`](../../docs/research/sparse-parity/DESIGN.md) (SP4). Where the
adversarial critique (SP5) and the two reviews of this code (R1: the kernel and host; R2: the CPU side and the test
plan) disagree with it, they hold; DESIGN.md's "Amendments" lists the points. [`proto/`](proto/RESULTS.md) holds
SP3's CPU prototypes.

**State, 29 September 2026.** M0 (the CPU side) and M1's code (the kernel and its host program) exist and pass
every CPU and `sys_emu` test below. **Nothing here has run on a card yet**: the card steps are written out in
[`card_run.sh`](card_run.sh) and in "M1 on a card" and "M2 on a card" below, for the owner's session to run.

## Contents

| Path | What it is |
|---|---|
| `kernel/sparseparity.c`, `sparseparity_args.h` | The device kernel (U-mode RISC-V) and its argument, work-list and record layouts. `SPP_TENSOR`: the scan as an int8 ±1 GEMM on the tensor unit (hart 0: tensor ops and the epilogue; hart 1: row generation). `SPP_SCALAR`: bit-packed XOR and a software popcount, the card's own correctness reference. |
| `host/main.cpp` | `sparseparity_host`: generate or load an instance, plan, open the card (or `--sysemu`), launch, read back the per-hart records, check everything on the CPU, print one JSON line. |
| `host/spp_common.h` | The host's instance generator, colex ranks and tile geometry (the same as `cpu/sp.h`), the cost model and planner, the CPU oracle and the closed-form checksums. |
| `host/spp_selftest.cpp` | `spp_selftest`: the host model's CPU-only tests; also `--tie-instance`, `--bench-oracle`, `--plan`, `--hash`. |
| `sysemu_check.sh` | Every kernel path in `sys_emu` (27 cases), with the simulator's checkers on. |
| `card_run.sh` | The M1, probe and M2 card steps, one locked, `timeout 10` process each, stopping at the first unexpected result. `--dry` runs them without a device. |
| `cpu/sp.h` | Header-only C11/C++: the instance generator (bit-identical to `proto/spbits.c` and `proto/sp.py`), the ±1 and B-tile layouts, colex ranks and the T2 geometry, the closed forms, and the binary formats (work list, records, top lists, survivors). |
| `cpu/spref.c` | The reference solver in exactly the card's formulation: `gen`, `scan` (full, by work list, two-stage), `check`, `selftest`. |
| `cpu/spbase.c` | The CPU baselines: `vexh` (AVX-512, 8 candidates per register), `mitm` (bucketed meet in the middle with a random halving of the features), `batch` (B1, 8 instances per register). |
| `tools/planner.py` | `plan` (the work list, cut by modelled cycles and dealt round-robin across the shires, with host-side slices), `show`, `merge` (per-hart records → coverage, checksums, rescoring, ties), `closed`. |
| `tools/sptest.py`, `tools/spcore.py` | The CPU tests (102 checks; 110 with `--spbits`) and `sptest.py card` (a card's output against the reference, hart by hart); `spcore.py` is `sp.h` in Python. |
| `tools/bench_cpu.py`, `tools/table_cpu.py` | The CPU baseline ladder and its tables. |
| `cpu/data/2026-09-29-aifoundry3-r/` | The CPU baselines after the reviews (the table below). `cpu/data/2026-09-29-aifoundry3/` is the first run, superseded. |
| `data/2026-09-29-aifoundry3-sysemu/` | The `sys_emu` suite's results and the CPU test logs of the code as it stands. |

## Build

Everything builds on the lab host that will run it, against its own `/opt/et`, in a directory no `tools/claims-v3`
block uses (AGENT.md §7). Check `et-who` first and build only while nobody holds the card there. The host program has
its kernel's path compiled in.

| Host | Tree | Build | Notes |
|---|---|---|---|
| aifoundry3 | `~/nekko` (a copy, no git) | the commands below | card idle; `sys_emu` at `/opt/et/bin/sys_emu`; built and tested there on 29 September |
| aifoundry1 | `~/nekko` | the same | **card 1 only**: `card_run.sh` sets `ET_DEVICES=1` and `etsoc-shire1.lock`; `/home` is 99% full, so keep only this build |
| aifoundry2 | the git checkout, `~/claude/et-soc1-prototyping` | `cmake` and `make` as below, in the checkout | **not before the DV2 validation ends (about 17:00 PDT on 29 September)**: no builds, no `*_host` or `sys_emu` process until then |

From a clone (on aifoundry2 the checkout itself), copy the sources to aifoundry1 or aifoundry3 the way
`scripts/deploy-lab.sh` does, then build there:

```bash
tar --exclude=__pycache__ -czf - workloads/sparseparity docs/research/sparse-parity | ssh aifoundry3 'tar xzf - -C ~/nekko'
# on the host, in ~/nekko (or the checkout on aifoundry2):
cmake -S workloads/sparseparity -B build/sparseparity-f -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice -n 19 cmake --build build/sparseparity-f -j4           # kernel/sparseparity.elf, host/sparseparity_host, host/spp_selftest
make -C workloads/sparseparity/cpu O=$PWD/build/sparseparity-f-cpu   # spref, spbase (-march=native: AVX-512 VPOPCNTDQ)
build/sparseparity-f/host/spp_selftest                       # CPU only: SELFTEST PASS
/opt/et/bin/riscv64-unknown-elf-objcopy -O binary -j .text build/sparseparity-f/kernel/sparseparity.elf /dev/stdout | sha256sum
```

The last line is the kernel's identity: the three hosts' toolchains emit the same `.text` and differ only in
`.comment` (14-card-behaviour.md), so record and compare the `.text` hash, never the file's. The kernel tested here
has `.text` sha256 `68b3f273c18f0b8e94244dba3a588b73ba1115e9b8478b2ae3bd83f7a65a234e`, built on aifoundry3 and
again on aifoundry1 on 29 September; `card_run.sh` records it with every run. (R1 found that an earlier report quoted
a wrong hash, `76eb2d2f…`, for the previous kernel: its `.text`, extracted this way on three hosts, was
`d32d702ad0ffb4c4…`.)

## The milestones and how to run each

### M0: the CPU side (no card)

```bash
nice -n 19 python3 workloads/sparseparity/tools/sptest.py --bin build/sparseparity-f-cpu --threads 2   # 102 checks, ~15 s
#   (--spbits build/sparseparity-cpu/spbits adds 8: the generator against SP3's proto/spbits.c)
python3 workloads/sparseparity/tools/planner.py plan --n 512 --k 4 --m 1850 --topm 0 --out l2.bin     # L2 on 32 x 32 minions
build/sparseparity-f-cpu/spref scan n=512 k=4 eta=0.4 m=1850 seed=1 plan=l2.bin out=l2.ref threads=6
python3 workloads/sparseparity/tools/planner.py merge --plan l2.bin --out l2.ref --inst 512,4,0.4,1850,1
nice -n 19 python3 workloads/sparseparity/tools/bench_cpu.py --bin build/sparseparity-f-cpu --out DIR --maxt 6   # ~25 min, detached
python3 workloads/sparseparity/tools/table_cpu.py DIR
```

### `sys_emu`: every kernel path in the functional simulator (no card)

```bash
setsid nohup bash workloads/sparseparity/sysemu_check.sh --build build/sparseparity-f --cpu build/sparseparity-f-cpu \
    > build/sparseparity-f/sysemu.log 2>&1 < /dev/null &      # 27 cases, ~16 min; --quick: 4 cases
```

It refuses to run on aifoundry2 (the DV2 validation counts any `sys_emu` or `*_host` process as a foreign device
process) and while any `tools/claims-v3` queue runs. Every case passes `--sysemu`; the checkers are the runtime's
defaults (`mem_check`, `l1_scp_check`, `l2_scp_check`, `flb_check`, `tstore_check`) plus `-vpurf_warn`, counted at the
kernel's PCs (0x8005…). The cases are listed in "Tests" below. `sys_emu` checks correctness only, never speed, and
it cannot check errata 1.29 type F (its VPURF checker ignores tensor writes to the f registers; the kernel handles
it by construction: a `TOUCH_ALL` after every `TensorWait` that precedes a vector read).

### M1 on a card: one minion, then one shire's bring-up

**The card rules** (AGENT.md §5; 14-card-behaviour.md, "Traps"):
- only with the owner's go-ahead and a named card: aifoundry3's card (idle, but its demo can launch without the
  lock: check `et-who` before and after), or aifoundry1's card 1 (`ET_DEVICES=1`); aifoundry2 only after its DV2
  validation ends, and aifoundry1's card 0 never (it overheats);
- every device-opening process runs as `flock -n /run/lock/etsoc-shire<N>.lock timeout 10 …`, releases the lock
  before the next, and is stopped with a plain `kill`, never `kill -9`;
- save `et-lab-manifest` with the data; build into your own directory; never reset a card or change its settings.

`card_run.sh` does all of this per step: it waits for `et-who --check` to show a free card, runs each step as one
locked, `timeout 10` process with `--records-out`, compares the JSON with the step's expected result, stops at the
first surprise (resume with `--from STEP`), and after a step whose plan does not cover every candidate it re-runs the
full oracle offline on the saved records (`--verify-records`, no device). Look first, then run:

```bash
cd ~/nekko                                                    # aifoundry3 or aifoundry1 (the checkout on aifoundry2)
bash workloads/sparseparity/card_run.sh list                  # every step, its expectation and its modelled time
bash workloads/sparseparity/card_run.sh m1 --dry              # the same plans with --dry: no device, no lock
et-who                                                        # nobody on the card
bash workloads/sparseparity/card_run.sh m1                    # then: probe, then m2
```

The M1 steps (one process each; "model" is the kernel's modelled time at 600 MHz; each process also opens the
device, about 1 s, and is capped at 10 s):

| Step | What it runs | Expected | Model |
|---|---|---|---|
| `m1-c0-scalar` | C0 (32, 3, 0.1, 128), scalar path, 1 minion, every correlation dumped | PASS: the dump equals the CPU's 9,472 entries (4,960 candidates), both closed forms, the secret | 1 ms |
| `m1-c0-tensor` | C0, tensor path, 1 minion, dumped | PASS, the same | 0.1 ms |
| `m1-neg-drop`, `-dup`, `-mask` | the three negative controls (DESIGN §4.1(6)): a tile dropped, a tile scanned twice, one tile's staircase shifted | FAIL on the closed forms; the count holds for `mask`; records and launch clean | 0.1 ms |
| `m1-tie` | the tie instance (C0's shape, two candidates at c = m) | PASS with the answer reported not unique | 0.1 ms |
| `m1-c1-timing`, `m1-c1` | C1 (128, 4, 0.2, 192), 1 minion: A resident (S = 3) | TIMING: `kernel.cycles_per_op_busiest` against 270 (the M1 criterion, ±10%); then PASS with the closed forms | 0.14 s |
| `m1-l1-timing`, `m1-l1` | L1 (512, 4, 0.3, 448) slice 0 of 64, 1 minion: A streamed (S = 7) | TIMING against 280 (mmbench's loop, E37; this kernel waits for the previous FMA before reloading A, as the PRM requires, and `estCycles` assumes 350); PASS (oracle in-process, then offline) | 1.2 s |
| `m1-l2-timing`, `m1-l2` | L2 (512, 4, 0.4, 1,850) slice 0 of 200, 1 minion (S = 29) | TIMING against 280; PASS | 1.5 s |
| `m1-c1-32-seed1` … `seed20` | C1 on one shire's 32 minions, seeds 1–20 (DESIGN §4.1(4)) | PASS each (closed forms); `solved` on about 99% of seeds | 4 ms |

Then **the hand-off race probe** (`card_run.sh probe`; review R1, finding 3). Hart 1 publishes each staged row tile
with `fence; amoswapl.d` after global stores (`fswg.ps`) to its own shire's scratchpad, and whether that `fence`
waits for those stores' acknowledgements is not in the PRM; `sys_emu` cannot show a reordering. The probe gives each
of 32 minions 2,000 (or 200) consecutive one-column-tile row tiles, so hart 0 loads every A right after it is
published, and checks every minion with the full oracle, for each staging (scratchpad or DRAM, 1 or 2 buffers) and
both A paths:

| Step | What it runs | Expected | Model |
|---|---|---|---|
| `probe-l2-scp1`, `-dram1`, `-dram2` | L2's geometry (S = 29, A streamed), 32 minions × 2,000 narrow tiles | PASS, oracle exact on all 32 minions | 77 ms |
| `probe-l2-scp2` | the same with 16 minions (2 scratchpad buffers do not fit 32) | PASS | 77 ms |
| `probe-c1-scp2`, `-scp1`, `-dram2`, `-dram1` | C1's geometry (S = 3, A resident), 32 minions × 200 narrow tiles | PASS | 1 ms |

A MISMATCH in any probe is the race: stop, keep the records, and do not run the scratchpad staging at scale until it
is understood (DRAM staging publishes through the shire's own L2, a different path).

### M2 on a card: one shire (32 minions)

`card_run.sh m2`, after M1 and the probe pass. DESIGN §5's exit criteria: the bandwidth knee measured and set against
§2.2, the imbalance under 2%, an L1 run exact.

| Step | What it runs | Expected | Model |
|---|---|---|---|
| `m2-c1-32` | C1 on 32 minions | PASS (closed forms) | 4 ms |
| `m2-knee-p{1,2,4,8,16,32}-timing`, `m2-knee-p{…}` | L1 with P = 1 … 32 minions in one shire, the same work per minion (slice 0 of 64/P): private streams from 1 to 32 minions | TIMING: cycles per op against P (the knee, where 32 private streams reach 4 B per minion-cycle, predicted at 512); PASS | 1.2 s each |
| `m2-l1-full` | all of L1 on one shire | PASS with both closed forms; `cycles_max / cycles_median` is the imbalance (model 1.0001) | 2.3 s |
| `m2-l2-q0`, `-dram2`, `-dram1`, `-timing` | L2 slice 0 of 4 on one shire: staging in the scratchpad (1 buffer, what `auto` picks), in DRAM with 2 and 1 buffers, and without the epilogue | PASS (sampled oracle in-process, full oracle offline); TIMING | 2.4 s |
| `m2-f5-s0` | (256, 5, 0.4, 1,925) slice 0 of 16 | PASS | 2.3 s |
| `m2-l5-s0` | L5 (512, 5, 0.4, 2,151) slice 0 of 512 (the scratchpad layout ends at 2,432 KB) | PASS | 2.3 s |
| `m2-l2-q0-nowait` | L2's slice without the PRM's `TensorWait` before an A buffer is reloaded (`sys_emu` rejects it; silicon only) | PASS if the hardware tolerates it, checked in full offline; last, so a failure stops nothing else | 2.4 s |

A card run can also be checked hart by hart against the CPU reference, through M0's work list and output format
(what `sysemu_check.sh`'s `m0-*` cases do); the host process is the only one that touches the card:

```bash
python3 workloads/sparseparity/tools/planner.py plan --n 512 --k 4 --m 448 --shire-mask 0x1 --mps 32 --topm 0 --out $D/l1.wl
flock -n /run/lock/etsoc-shire0.lock timeout 10 build/sparseparity-f/host/sparseparity_host --n 512 --k 4 --eta 0.3 \
    --m 448 --seed 1 --plan $D/l1.wl --out $D/l1.card --records-out $D/l1.rec > $D/l1.json
python3 workloads/sparseparity/tools/sptest.py card --bin build/sparseparity-f-cpu --threads 4 --plan $D/l1.wl \
    --out $D/l1.card --inst 512,4,0.3,448,1                    # no device: spref on the same work list, field by field
```

M2 also calibrates the planner's constants: `CYC_EPI` from a step's normal and `--timing-only` cycles, and
`CYC_GEN_SLICE` from hart 0's wait cycles (`kernel.wait_cycles_max`) on the probe's narrow tiles; pass them to the
planner with `--model FILE.json`.

M3 (all 32 shires) is not scripted yet. Its sizes fit one process each: L2 on 32 shires is modelled at 0.30 s, L1
at 73 ms (`sparseparity_host --dry --shires 0xffffffff --per-shire 32 …`); L5 needs host-side slices (`--slice I/N`).

## How the kernel and the host work

**The formulation** (shared by the kernel, `cpu/sp.h` and `spref`). A candidate is T = R ∪ {j}: R a (k−1)-subset of
0..n−2 in colex order (row rank ρ), j > max(R). Its score is c(T) = Σᵢ ỹᵢ ∏_{t∈T} x̃ᵢₜ = m − 2·popcount(y ⊕ x_T), an
exact int32; bit 0 is +1 (`0x01`), bit 1 is −1 (`0xFF`), padding samples are 0. Row tiles are 16 consecutive rows,
column tiles 16 features; row tile t visits column tiles ⌊(p_min+1)/16⌋ … ⌈n/16⌉−1 and the staircase (j ≤ max(R))
and padding are masked; each output tile is S = ⌈m/64⌉ `TensorIMA8A32` ops. The answer is the largest c; a tie goes to
the smallest colex rank C(j,k) + ρ, and is reported as not unique. The two checksums Σc and Σc² (mod 2⁶⁴) over all
C(n,k) candidates have closed forms in the data alone (Krawtchouk polynomials), so a run that covers everything proves
each candidate was scored once and correctly.

**The kernel, per minion** (`SPP_TENSOR`):
- hart 0 copies its share of X (the B tiles) into its shire's scratchpad with `TensorLoadL2Scp`, meets the other
  minions at a fast local barrier, then issues only tensor ops: `TensorLoad` of A from the staging buffer, `TensorLoad`
  of B into TenB, `TensorIMA8A32`; and runs each output tile's epilogue (mask, Σc, Σc², lane maxima, and a scalar
  rescan of a tile that could hold a new best or a tie). It reads the scratchpad through the local alias 0x7F;
- hart 1 builds each row tile's A (16 rows × 64·S bytes) in its own vector registers and stages it with stores that
  bypass its L1: `fswg.ps` into the scratchpad (the shire's explicit address) or `fswl.ps` into DRAM lines held in L2;
- they signal through two L2 lines per minion (`amoswapl.d` / `amoorl.d`) with a multiply-chain pause between polls
  (erratum 1.28). A hart that gives up writes an abort word, so the other stops at once;
- every hart writes one 64 B record: best (c, rank) and a tie flag, Σc, Σc², candidates, ops, cycles
  (`hpmcounter3`, hart 0 only, erratum 1.23), wait, and a status with the launch's epoch.

**The host.** Staging `--stage auto` takes the scratchpad with 2 buffers per minion, else 1, else DRAM with 2. After
opening the device it reads the scratchpad size the device reports and refuses a layout past it (`TensorLoadL2Scp`
would wrap silently). **The 10 s rule:** it refuses a work list modelled over `--max-kernel-s` (4 s); it launches only
while the launch's timeout (min(8 s, 2 × the model + 1.5 s)) plus a readback still ends by `--budget` (9 s after the
process started); after a timed-out launch it aborts the stream and reads nothing back; the harts' poll limits are
sized so that they give up well inside the timeout. **Repeats** (`--reps`) are read back and checked after every
launch; a run that stops short fails.

**The value checks.** Every run: the records (epoch, errors), the count and ops against the plan, and the best
rescored on the CPU. Full coverage: both closed forms. The **oracle** rescores whole minions on the CPU and compares
each hart-0 record field by field: `--oracle on` every minion; `auto` every minion if that fits the process's time,
else a random sample (seeded by the epoch); `sample`; `off`, which a card run refuses unless the closed forms apply
and `--nowait-a` is off. `--records-out FILE` then `--verify-records FILE` (same arguments, no device) runs the full
oracle offline. `--out FILE` writes M0's output format for `sptest.py card`.

**The negative controls** (`--perturb`): `drop` (one tile fewer), `dup` (one tile twice), `mask` (one tile's
staircase shifted one column left in every row that allows it: the count holds, both checksums fail).

## The planner and its cost model

A row tile with n_out column tiles and S slices costs, in modelled cycles (`tools/planner.py tile_cycles` =
`host/spp_common.h tileCycles`):

    max( hart 0 = ops · c_op + n_out · CYC_EPI + (A resident ? 16·64·S / BW : 0),     ops = n_out · S
         hart 1 = S · CYC_GEN_SLICE,
         bytes / BW )                           bytes = B (1 KB per op) + A reads + the generated rows (S KB)

with c_op = 270 (A resident, S ≤ 3; M, E39) or 280.35 (streamed; M, E37), BW = 4 B per minion-cycle (M, E37),
CYC_EPI = 450 per output tile and CYC_GEN_SLICE = 800 per slice of a row tile (both assumed until M2). The planner
cuts the row tiles, in colex order, into blocks of equal modelled cost and deals block q to shire q mod nshires,
minion (q div nshires) mod 32, so every shire gets a like mix of wide and narrow tiles; `--slices N` cuts every
minion's work into N launches of equal cost (no early exit inside the kernel in M1–M3). On 32 × 32 minions the
modelled imbalance of `planner.py`'s plans is 1.0001–1.0017 at L1, L2, (256,5), L5 and L5's two-stage stage 1, and
every block is within 0.60–0.81 row tile of its share. The host's built-in plan (used unless `--plan FILE`) is the
same model and the same deal, with 4 blocks per minion: 1.0033 at L1 and L2.

## Tests

**CPU (`tools/sptest.py`: 110 checks with `--spbits`, all pass on aifoundry3 with the final code, 29 September;
~15 s at 2 threads):**
- **gen:** the C generator = the Python mirror = `proto/spbits gen` on 8 instances up to L5 (instance, ±1 layouts,
  B tiles); the generator is prefix-consistent (the two-stage screen's stage 1 is an ordinary instance).
- **closed:** the closed forms (Python and C) = brute force in C and Python on 7 small sizes up to k = 6; Python = C
  at L2, (256,5) and L5.
- **ref:** `spref selftest` on 13 sizes: closed forms = brute force = the bits path = the int8 tile path = 7 uneven
  ranges merged over 3 minions, best, top-8 and the tie flag included; every candidate scored once; the two-stage
  survivors = brute force's; the three negative controls fail (the mask control: the count holds and both checksums
  fail, on every size). C0's 4,960 correlations = Python brute force one by one; C1 int8 = bits.
- **plan:** nine plans from 1 minion to 32 × 32 (1–3 blocks per minion, 1–4 slices, one two-stage): `spref`'s
  per-range ops and candidates = the planner's; the slices cover every row tile once; both checksums = the closed
  forms; the merge = the full scan. Negative controls on 1,024-minion plans: a record's Σc off by 2, a best j off by
  2, a duplicated range, a dropped range, and a flagged tie (the answer must become not unique) are each caught.
- **planbig:** the showcase plans on 32 × 32 minions: coverage, cut error ≤ 1 tile, imbalance < 1.01.
- **base:** `vexh` = the reference (answer, ties, both checksums = closed forms) on 9 sizes; `mitm` with and without
  the halving finds the reference's answer; two-stage survivors and stage 2 = the reference; `batch` with 8
  instances per register and one per thread solves exactly what the reference solves (η = 0.1 and 0.3, with
  padding lanes).

**Host model (`spp_selftest`):** ranks, the J0 runs and sp.h's row count; both closed forms = brute force on 9
sizes up to k = 6; plans on 4 shire masks × 3 minion counts × 2 rounds: every tile once, candidates = C(n,k), the
plan-order oracle and the merged per-minion oracles = brute force (tie flag included); the tie rule within one and
across merged accumulators.

**`sys_emu` (`sysemu_check.sh`): 27 of 27 cases as expected, with the final binaries, on aifoundry3, 03:36–03:51
PDT on 29 September** ([`data/2026-09-29-aifoundry3-sysemu/`](data/2026-09-29-aifoundry3-sysemu/README.md)). Every case
had 0 VPURF warnings at the kernel's PCs and no FATAL, except `s4-nowait`, whose FATALs are all the L1 scratchpad
checker's. The dumps compare every raw 16 × 16 output tile with the CPU, masked entries included.

| case | what | expected | result |
|---|---|---|---|
| c0-scalar | C0, scalar path, 1 minion, dumped | PASS | PASS; closed forms ok/ok; oracle exact, all 1 minions; dump exact 9472 entries; solved True |
| c0-tensor | C0, tensor path (S = 2, A resident), 1 minion, dumped | PASS | PASS; closed forms ok/ok; oracle exact, all 1 minions; dump exact 9472 entries; solved True |
| s4-tensor | (48, 3, 0.1, 256): S = 4, A streamed | PASS | PASS; closed forms ok/ok; oracle exact, all 1 minions; dump exact 26880 entries; solved True |
| shire8-s5 | (64, 3, 0.2, 320), S = 5, 8 minions | PASS | PASS; closed forms ok/ok; oracle exact, all 8 minions; dump exact 58368 entries; solved True |
| c0-scalar-2h | C0 scalar, both harts | PASS | PASS; closed forms ok/ok; oracle exact, all 1 minions; dump exact 9472 entries; solved True |
| s4-nbuf1 | S = 4, 1 staging buffer | PASS | PASS; closed forms ok/ok; oracle exact, all 1 minions; dump exact 26880 entries; solved True |
| s4-dram | S = 4, staging in DRAM | PASS | PASS; closed forms ok/ok; oracle exact, all 1 minions; dump exact 26880 entries; solved True |
| s4-nowait | S = 4 with --nowait-a | REJECT | the L1 scratchpad checker stops the run (FATAL in L1-SCP-Checker), as the PRM predicts |
| k4-2shires | (40, 4, 0.1, 192), 2 shires x 2 minions (n not a multiple of 16) | PASS | PASS; closed forms ok/ok; oracle exact, all 4 minions; dump exact 225792 entries; solved True |
| k5 | (24, 5, 0.1, 128) | PASS | PASS; closed forms ok/ok; oracle exact, all 1 minions; dump exact 163840 entries; solved True |
| k2-m100 | (40, 2, 0.1, 100), m not a multiple of 64 | PASS | PASS; closed forms ok/ok; oracle exact, all 1 minions; dump exact 1536 entries; solved True |
| k1 | (20, 1, 0.1, 40) | PASS | PASS; closed forms ok/ok; oracle exact, all 1 minions; dump exact 512 entries; solved True |
| k4-scalar-2shires | (40, 4) scalar, both harts, 2 shires | PASS | PASS; closed forms ok/ok; oracle exact, all 4 minions; dump exact 225792 entries; solved True |
| s4-timing | S = 4, --timing-only | TIMING | TIMING |
| neg-drop | C0, one tile dropped | NEG | FAIL; closed forms MISMATCH/MISMATCH; oracle exact, all 1 minions |
| neg-dup | C0, one tile scanned twice | NEG | FAIL; closed forms MISMATCH/MISMATCH; oracle exact, all 1 minions |
| neg-mask | C0, one tile's staircase shifted | NEGM | FAIL; closed forms MISMATCH/MISMATCH; oracle MISMATCH 1 of all 1 minions |
| tie | the tie instance, 1 minion (tie inside one hart) | TIE | PASS; closed forms ok/ok; oracle exact, all 1 minions; unique False, harts at best 1, flagging 1 |
| tie-8 | the tie instance, 8 minions (the two tied candidates on two harts) | TIE | PASS; closed forms ok/ok; oracle exact, all 8 minions; unique False, harts at best 2, flagging 0 |
| tie-scalar | the tie instance, scalar path | TIE | PASS; closed forms ok/ok; oracle exact, all 1 minions; unique False, harts at best 1, flagging 1 |
| probe | --probe narrow:6 on 4 minions, --oracle on | PASS | PASS; oracle exact, all 4 minions; partial plan |
| reps2 | --reps 2, 2 minions, dumped | PASS | PASS; closed forms ok/ok; oracle exact, all 2 minions; dump exact 26880 entries; reps 2, consistent ok; solved True |
| abort | --poll-limit 2, 4 minions | ABORT | FAIL; closed forms MISMATCH/MISMATCH; oracle MISMATCH 4 of all 4 minions; records 8 bad; hart 0 gave up (`SPP_ERR_POLL`) and hart 1 stopped on its abort word (`SPP_ERR_ABORTED`); the launch completed |
| hi-auto | (512, 4, 0.4, 2304), 32 minions x 1 row tile (R1's wide plan): auto staging picks the scratchpad with 1 buffer, 2,560 KB exactly | PASS | PASS; oracle exact, all 32 minions; stage scp x 1, layout 2560 KB; partial plan |
| m0-c0 | M0 work list (planner.py, --topm 0), C0, 1 minion; sptest.py card vs spref | M0 | host PASS; `sptest.py card`: every hart's record = spref's, field by field (ALL PASS) |
| m0-s4-shire8 | M0 work list, (48, 3), 8 minions x 2 blocks | M0 | host PASS; `sptest.py card`: every hart's record = spref's, field by field (ALL PASS) |
| m0-k4-2shires | M0 work list, (40, 4), 2 shires x 2 minions | M0 | host PASS; `sptest.py card`: every hart's record = spref's, field by field (ALL PASS) |

## CPU baselines, and the card against the CPU's best method

**Setup.** aifoundry3's host, an i7-11700K (8 cores, 16 threads, AVX-512 VPOPCNTQ), 03:52–04:07 PDT on
29 September: niced to 19, at most 6 threads pinned one per physical core, no card opened (`et-who` empty before and
after every run). Every timed point is the median of 5 repetitions, with the range. 16 threads are extrapolated from
6, not measured (this work may use at most 6 threads there): the fast end linear to 8 cores, the slow end at the
measured 4 → 6 step efficiency (0.96–0.97); SMT adds nothing to this port-bound scan (0.94–1.09 on one core). The
data, the generated tables and the reasons are in [`cpu/data/2026-09-29-aifoundry3-r/`](cpu/data/2026-09-29-aifoundry3-r/README.md)
([`tables.md`](cpu/data/2026-09-29-aifoundry3-r/tables.md)).

**CPU energy is assumed, not measured, and not bounded.** The package's energy counter is root-only, `perf` power
events are off (`perf_event_paranoid` = 2), and the board has lifted both package power limits to 4,095 W
([`powercap.txt`](cpu/data/2026-09-29-aifoundry3-r/powercap.txt)), so the part's rated 125 W (PL1) and 251 W (PL2) bound
nothing. The energy column is P × t at an assumed 125–251 W. Measuring it needs the lab admin: read access to
`energy_uj`, or a wall meter.

**Every card method against the CPU's best method at its size.** The card's times are DESIGN.md's model
(`design_model.py`: M3 private loads / M4 cooperative loads, 32 shires, 600 MHz) and are **predictions (P): nothing
has run on a card**. A card two-stage row adds the host's stage 2 as the CPU measured it for that m1 and the
survivors' readback. P(ok) is the chance of returning the secret: m is SP3's 99% sample count, and a two-stage screen
also needs the secret to survive stage 1. The last column is the CPU's 16-thread time (slow end) over the card's.

| size | card method | card time, M3 / M4 (P) | card P(ok) | CPU's best method | CPU P(ok) | CPU 1T | CPU 6T (range) | CPU 16T extrapolated | CPU energy at 16T, assumed 125-251 W | CPU 16T / card M3 - M4 |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 (512,4,0.3,448) | one stage | 73 ms / 39.9 ms | 0.990 | mitm, expected over 10 seeds | 0.990 | 897 ms | 148 ms | 111 ms - 115 ms | 14.3-28.8 J | 1.57 - 2.87 |
| L2 (512,4,0.4,1850) | one stage | 301 ms / 164 ms | 0.990 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 2.53 s | 459 ms (455 ms-459 ms) | 344 ms - 347 ms | 43.4-87.1 J | 1.15 - 2.12 |
| L2 (512,4,0.4,1850) | two-stage m1 = 832, tau1 = 80 | 207 ms / 145 ms | 0.989 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 2.53 s | 459 ms (455 ms-459 ms) | 344 ms - 347 ms | 43.4-87.1 J | 1.68 - 2.39 |
| F5 (256,5,0.4,1925) | one stage | 1.16 s / 668 ms | 0.990 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 8.81 s | 1.58 s (1.57 s-1.63 s) | 1.19 s - 1.2 s | 150-301 J | 1.03 - 1.79 |
| F5 (256,5,0.4,1925) | two-stage m1 = 1024, tau1 = 104 | 656 ms / 399 ms | 0.989 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 8.81 s | 1.58 s (1.57 s-1.63 s) | 1.19 s - 1.2 s | 150-301 J | 1.83 - 3.00 |
| L5 (512,5,0.4,2151) | one stage | 36.7 s / 20.1 s | 0.990 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 4.49 min | 48.2 s (47.9 s-51.5 s) | 36.2 s - 36.5 s | 4.56e+03-9.16e+03 J | 1.00 - 1.81 |
| L5 (512,5,0.4,2151) | two-stage m1 = 1280, tau1 = 144 | 21.7 s / 11.9 s | 0.989 | vexh two-stage m1 = 1024, tau1 = 104 | 0.989 | 4.49 min | 48.2 s (47.9 s-51.5 s) | 36.2 s - 36.5 s | 4.56e+03-9.16e+03 J | 1.68 - 3.06 |
| B1 1,024 x (64,4,0.1,64) | vector path, one instance per minion | 6-12 ms (DESIGN.md) | ~0.99 | batch, 8 instances per register | ~0.99 | 56 ms | 10 ms (9.98 ms-10.2 ms) | 6.89 ms - 7.64 ms | 0.955-1.92 J | 0.64 - 1.27 |

**What the table says.**
- **At η = 0.4 the CPU's best method is its own two-stage screen**, at m1 = 1,024 for L2, (256,5) and L5: 1.5–1.8×
  faster than its one-stage scan (L2 459 ms against 699 ms on 6 threads; (256,5) 1.58 s against 2.63 s; L5 48 s
  against 85 s), with the secret kept with probability 0.9994. Against it, the card's predicted one-stage scan leads by
  1.0–2.1× and its two-stage screen by 1.7–3.1×, not DESIGN.md's 3.7–6.8× at L2 (which set the card against SP3's
  slower scan).
- **At L1 (η = 0.3) the meet in the middle with the random halving is the CPU's best in expectation**: 148 ms on 6
  threads (the mean over 10 seeds of each seed's expected time; all 10 solved, median wall 114 ms) against the
  AVX-512 scan's 180 ms. The card's predicted lead there is 1.6–2.9×.
- **B1: the card has no predicted lead.** 1,024 instances with 8 per register take 10.0 ms on 6 threads and 6.9–7.6 ms
  extrapolated to 16, against the card's predicted 6–12 ms (0.64–1.27×). The old one-instance-per-thread baseline
  took 46.6 ms.
- **The halving makes the meet in the middle 4–5× faster** (the r sweeps at seed 1: L1 0.21 s against 0.86 s, L2
  3.2 s against 14.9 s), and the refitted cost model picks r = 16, inside the flat optimum (r = 15–18). At η = 0.4 it
  is still 4.5–6× slower than the CPU's best (L2 2.9 s, (256,5) 8.6 s, L5 3.6 min in expectation on 6 threads). No seed
  of the 23 at L1, L2 and (256,5) had a secret that could not clear the acceptance threshold.
- **The scan itself is unchanged** from the first run (L1 180 ms, L2 699 ms, (256,5) 2.63 s, L5 85 s on 6 threads,
  within 3%), and its checksums still equal the closed forms at L1, L2 and (256,5); the reference through the
  planner's 1,024-minion L2 work list merges to the secret with both closed forms and all 8,192 reported candidates
  rescored.

## What the reviews found, and what changed

**R1 (the kernel and host).**

| # | Finding | Status |
|---|---|---|
| 1 | HIGH: large sliced runs had no value check | **Fixed.** A card run must run a value check: the closed forms, or the oracle. `--oracle auto` rescores every minion when that fits the process's time, else a random sample of minions (seeded by the epoch); `--oracle off` is refused on a card for partial coverage or `--nowait-a`; `--records-out` + `--verify-records` runs the full oracle offline, which `card_run.sh` does after every partial step. The host is built with `-mpopcnt` (the oracle runs 1.0e9 words/s at S = 29). |
| 2 | HIGH: the 10 s rule could be broken | **Fixed.** The host launches only if its whole timeout plus a readback ends by `--budget` (9 s from the process's start; at most 9.5 s); the timeout is min(8 s, 2 × the model + 1.5 s, the time left); `--max-kernel-s` defaults to 4 s; after a timed-out launch it aborts the stream and reads nothing back; every other wait is timed. |
| 3 | MEDIUM: the `fswg.ps` → `fence; amoswapl.d` hand-off is a silicon-only risk | **Applied as R1 proposed:** `--probe narrow:N` and `card_run.sh probe`, the first card work at scale: 32 minions consuming one-column-tile row tiles right after hart 1 publishes them, with the full oracle, for scratchpad and DRAM staging with 1 and 2 buffers, streamed and resident A. |
| 4 | MEDIUM: hart 0 read A through the shire's explicit address | **Fixed.** Hart 0 `TensorLoad`s A through the local alias 0x7F (`SPP_SCP_LOCAL`), the path of the measured own-scratchpad rate; hart 1 keeps the explicit address for its `fswg.ps`. `sys_emu` passes every scratchpad-staging case. |
| 5 | MEDIUM: `--stage auto` fell back to DRAM too early | **Fixed.** auto: the scratchpad with 2 buffers, else 1 buffer, else DRAM with 2. L2, (256,5) and L5 at 32 minions per shire now stage in the scratchpad with 1 buffer (2,112, 1,744 and 2,432 KB of 2,560). |
| 6 | MEDIUM: the planner ignored hart 1 | **Fixed** in both planners: a row tile costs max(hart 0, hart 1 = S × CYC_GEN_SLICE, bytes/BW), CYC_GEN_SLICE = 800 cycles per slice assumed until M2 measures it from hart 0's wait cycles on the probe's narrow tiles. |
| 7 | LOW: the epilogue runs with the tensor unit idle | **Not applied.** Issuing the next tile's first S−1 ops before the epilogue restructures the TenC / f-register hand-off that errata 1.29 type F constrains, which `sys_emu` cannot check; it belongs to M4's tuning, after silicon shows the cost. M1's cycles-per-op criterion is measured with `--timing-only` instead (DESIGN.md, Amendments). |
| 8 | LOW: an error exit was slower than the host's timeout | **Fixed.** A hart that gives up (poll limit or barrier) writes an abort word to its own sync line and the other hart stops at once (`SPP_ERR_ABORTED`); the poll limit is sized from the launch's timeout (under 0.4 of it at 600 MHz). `sys_emu` case `abort`. |
| 9 | LOW: the third negative control was missing | **Fixed.** `--perturb mask` (kernel flag `SPP_F_PERTURB_MASK`): one tile's staircase shifted one column left in every row that allows it; the count holds and both closed forms fail (`sys_emu` `neg-mask`; `spref selftest` on 13 sizes). |
| 10 | LOW: repeats were not checked | **Fixed.** Records are read back and checked after every launch (epoch, errors, and every minion's results equal to the first launch's); the JSON reports `reps_requested`, `reps_done`, `reps_consistent`, and a short run fails. `sys_emu` case `reps2`. |
| 11 | LOW: the scratchpad size was hard-coded | **Fixed.** After opening the device the host reads `DeviceProperties.l2scratchpadSize_` (MB, whole chip, over the compute shires) and refuses a layout past it; `--scp-kb` plans for a smaller one. The JSON reports `scp_kb_device`; the first card run shows the real value. |
| 12 | LOW: a wrong kernel hash was reported | **Fixed:** the method (`objcopy -O binary -j .text`) and the current hash are in "Build"; `card_run.sh` records it on every run. |
| 13 | INFO: `sys_emu` cannot check type F | Documented (kernel header, this README). |
| 14 | LOW: a tile index could overflow 32 bits | **Fixed.** The host refuses 2^32 row tiles or more (and a minion with that many). |

**R2 (the CPU side and the test plan).**

| # | Finding | Status |
|---|---|---|
| 1 | HIGH: the CPU energy "bound" was not a bound | **Fixed.** The powercap limits read 4,095 W (PL1 = PL2) on aifoundry3 (`powercap.txt` in the data), the energy counter is root-only and `perf_event_paranoid` is 2: CPU energy is stated as an estimate at an assumed 125–251 W, not a bound. Measuring it needs the lab admin: read access to `energy_uj`, or a wall meter. |
| 2 | HIGH: the showcase rows were not paired with the CPU's best method | **Fixed.** The CPU runs its own two-stage screens at (256,5) too, and the summary table pairs every card method (one stage, two-stage) with the CPU's best measured method at that size, with both sides' chance of success; `design_model.py` computes the card's side (including (256,5) two-stage). |
| 3 | MEDIUM: the B1 baseline was 4.5× too slow | **Fixed.** `spbase batch` runs 8 instances per 512-bit register (R2's prototype, generalised to any k ≤ 6); the old one-instance-per-thread is kept as `lanes=0`. Measured: 56 ms on 1 thread and 10.0 ms on 6 for 1,024 instances, 4.7× the old baseline; the card's predicted 6–12 ms no longer leads. |
| 4 | MEDIUM: the meet in the middle was under-tuned | **Fixed.** A random halving of the features per repetition (`split=1`, the default for k ≥ 4, k = 4 and 5); the verification cost refitted from the split r sweeps; every run reports `expected_s_full`, which charges the cap to a seed whose secret cannot clear the acceptance threshold. Measured: 4.1× (L1) and 4.7× (L2) faster than without the halving; at L1 it is now the CPU's best method in expectation. |
| 5 | LOW: the CPU two-stage used the card's m1 | **Fixed.** Each showcase size runs at two m1 (L2: 832 and 1,024; (256,5) and L5: 1,024 and 1,280) and the table takes the CPU's best: m1 = 1,024 at all three, 2–14% faster than the other. |
| 6 | LOW: the planner's balance at S ≤ 3 | **Fixed** with R1-6: the model has the per-output-tile epilogue (CYC_EPI) and the resident A load; the host's built-in plan uses the same model. |
| 7 | LOW: ties could not be detected with `--topm 0` | **Fixed.** Each hart's record flags a second candidate at its best c (the kernel, `spref`, the host's oracle; `SP_REC_TIE` in M0's format), and the merge counts two harts at the best as a tie. `sys_emu` cases `tie`, `tie-8`, `tie-scalar`; an `sptest` control. |
| 8 | LOW: single-shot measurements, reported as the minimum | **Fixed.** Five repetitions per timed point, reported as the median with the range. |
| 9 | LOW: two tile spaces | **Fixed.** The host uses `sp.h`'s geometry (rows = C(n−1, k−1)); an M0 work list with another tile count is refused. At n = 40 the closed forms now apply (`sys_emu` `k4-2shires`, `m0-k4-2shires`). |
| 10 | LOW: a negative control was missing in `spref` | **Fixed** (R1-9). |
| 11 | LOW: format limits were not guarded | **Fixed.** The planner and `spref` refuse a two-stage size whose rows (≥ 2^40) or m1 (> 4,095) do not fit a survivor entry; the host refuses ≥ 2^32 row tiles. |
| 12 | LOW: 16 threads are extrapolated | **Not applied**: this work may use at most 6 threads on aifoundry3. The extrapolation's error favours the CPU. |

**The critique (SP5).** (1) The AVX-512 scan and the bucketed meet in the middle are the baselines, tuned further per
R2, and the card is compared with the best CPU method. (2) The ladder is at η = 0.4 (C0, C1, B1 for bring-up); the
card's two-stage screen needs the survivor log, which is M3/M4 work, so the hero L5 two-stage is not yet runnable on
the card. (3) The planner balances modelled cycles and deals round-robin. (4) Hart 1 generates the rows, hart 0 only
issues tensor ops and the epilogue, and they signal through L2 lines. (5) X reaches each scratchpad through
`TensorLoadL2Scp`; A through `fswg.ps` or `fswl.ps`. (6) No early exit inside the kernel. (7) Superseded by R2-1:
the CPU's energy is assumed, not bounded.

## Formats (sp.h §6; `tools/spcore.py` reads and writes the same bytes)

- **Work list.** A 128 B header (n, k, m scanned, S, shires, minions per shire, slice i of N, two-stage τ₁, shire
  mask, totals), then 16 B per minion (first range, number of ranges, logical shire, minion in shire), then 64 B per
  range (row tiles [begin, end), ops, candidates, modelled cycles, the first row's subset, owner, block). A minion is
  logical, `shire_index·mps + minion`: `shire_index` is the rank of the physical shire among the mask's set bits.
- **Output.** A 64 B header, one 64 B record per hart (index minion·2 + hart), then each minion's top list in 16 B
  entries. A record holds magic, hart, flags (valid, has best, log overflow, error, tie), minion, best (c, ρ, j), ops,
  Σc, Σc² mod 2⁶⁴, candidates and cycles. Hart 0's record is the tensor ops and the epilogue; hart 1's is the row
  generation, with `ops` = row tiles generated.
- **Survivor entry** (two-stage): ρ in 40 bits | j in 12 bits | c₁ in 12 bits. The planner and `spref` refuse a
  two-stage size whose rows or m1 do not fit it.
- **The kernel's own record** (`SppRecord`, `sparseparity_args.h`) is the same information in the card's layout; the
  host converts it (`--out`).
