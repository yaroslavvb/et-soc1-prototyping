# sparseparity: noisy sparse parity on the ET-SoC-1

The design is [`docs/research/sparse-parity/DESIGN.md`](../../docs/research/sparse-parity/DESIGN.md) (SP4). Where the
adversarial critique (SP5) and the two reviews of this code (R1: the kernel and host; R2: the CPU side and the test
plan) disagree with it, they hold; DESIGN.md's "Amendments" lists the points. [`proto/`](proto/RESULTS.md) holds
SP3's CPU prototypes.

**State, 29 September 2026.** M1, the hand-off probe, M2 and first all-shire runs (M3) ran on aifoundry3's card
from 04:15 PDT, every step as expected ([`data/2026-09-29-aifoundry3-card/`](data/2026-09-29-aifoundry3-card/README.md)):
L1 and L2 solved on 1,024 minions in 0.204 s and 0.807 s with exact checksums, about 5x one CPU core and level with
6 tuned AVX-512 threads. [`tools/cycle_model.py`](tools/cycle_model.py) fits a two-hart cycle model to those records
(rms 1.8% of a minion's cycles) and says why: hart 1's row generation costs 4.8x what the planner assumed, the
planner undercosts narrow row tiles 6.7x (the busiest minion 1.55x the mean), and each output tile's epilogue takes
1,606 cycles with the tensor unit idle. **M4's code** (below, "M4: what changed") answers the three: incremental row
generation, the epilogue in pieces between the next tile's ops, and a planner balanced by the fitted model, plus 3 A
buffers as an option; M1's kernel and planner stay one flag away (`--variant m1`) on the same build. A review of
M4's code (R3, below) found no correctness bug; its findings on the time budget and the card's coverage are applied
(the host's guard no longer trusts M4's predicted constants alone; `card_run.sh m4` gains the race probe with M4's
generation, a plan-balance control, a speed gate and offline full-oracle checks), and it found a stall in the
pipeline model past 1e10 cycles, now fixed. `card_run.sh m4` ran on aifoundry3's card at 08:17-08:45 PDT
([`data/2026-09-29-aifoundry3-card-m4/`](data/2026-09-29-aifoundry3-card-m4/README.md)): variant b (the fitted plan
and the incremental generation, M1's epilogue) is the best, L1 0.130 s, L2 0.429 s, (256,5) 2.55 s in two halves;
the epilogue in pieces was slower on silicon than its model. **M5's code** ("M5: the two-stage screen") puts the
screen's stage 1 in variant b's epilogue (a survivor log per minion, counted and flagged when full) and stage 2 on
the host; at η = 0.4 A cannot stay resident (m1 ≤ 192 keeps 83% of the candidates at P(loss) < 1e-4), so it screens
at m1 = 320 (L1) and 1,152 (L2, (256,5)). It passes every CPU test and 83 `sys_emu` cases (survivor logs equal to
`spref`'s byte for byte); **it has not run on a card**: `card_run.sh m5` predicts L1 0.10-0.12 s, L2 0.26 s and
(256,5) 1.22-1.33 s, 1.3-1.9x the CPU's own two-stage screen at the same P(loss). A review of M5 and of the board
energy tooling (R4, below) found no card-safety blocker; its findings are applied: the energy headline is the SP's
board average with the leakage law on the measured die temperature (±3%, tested on a second, adversarial test card
as well as the plumbing one), the card-against-CPU energy ratio is stated for the card's board alone and with the
host's package added, `combine` refuses anything but one solve's slices; the host poisons the survivor logs before
each launch, and two controls show on the card that the checks catch a missed survivor (`--perturb tau`) and a log
that never reached DRAM (`--perturb lostlog`); S2 is provisional until the offline full oracle. **Both card runs
(`card_run.sh m5`, `energy.sh`) use `build/sparseparity-t`** ("Build"; kernel `.text` `3e14be32…`, M5's, unchanged).

## Contents

| Path | What it is |
|---|---|
| `kernel/sparseparity.c`, `sparseparity_args.h` | The device kernel (U-mode RISC-V) and its argument, work-list and record layouts. `SPP_TENSOR`: the scan as an int8 ±1 GEMM on the tensor unit (hart 0: tensor ops and the epilogue; hart 1: row generation). `SPP_SCALAR`: bit-packed XOR and a software popcount, the card's own correctness reference. |
| `host/main.cpp` | `sparseparity_host`: generate or load an instance, plan, open the card (or `--sysemu`), launch, read back the per-hart records, check everything on the CPU, print one JSON line. |
| `host/spp_common.h` | The host's instance generator, colex ranks and tile geometry (the same as `cpu/sp.h`), the cost model and planner, the CPU oracle and the closed-form checksums. |
| `host/spp_selftest.cpp` | `spp_selftest`: the host model's CPU-only tests; also `--tie-instance`, `--bench-oracle`, `--plan`, `--hash`. |
| `sysemu_check.sh` | Every kernel path in `sys_emu` (85 cases: M4's kernel by default, M1's with `--variant m1`, and M5's two-stage screen, `ts-*`, whose survivor logs are compared byte for byte with `spref`'s, with its four controls), with the simulator's checkers on; `--only REGEX` runs a subset. |
| `card_run.sh` | The M1, probe, M2, M4 and M5 card steps (`m1`, `probe`, `m2`, `m4`, `m4gen`, `m5`), one locked, `timeout 10` process each, stopping at the first unexpected result; each step's launch time over its model; the M4 stage's speed gate and offline full-oracle checks; M5's two-stage fields, its controls, provisional S2 and the survivor logs' packing. `--dry` runs them without a device. |
| `energy.sh`, `tools/energy_reduce.py`, `tools/energy_stub.py` | Board energy per solve on one card: idle, one host process of back-to-back solves, idle, under `ettelem` at 10 Hz; the reduction (J per solve over idle from the SP's board average, the catalogue's method beside it, the rails, the host's share, the CPU ratios; `combine` for one solve's slices); the test doubles for `--dry`, a plumbing card and an adversarial one. "Energy per solve (`energy.sh`)" below. |
| `tools/cycle_model.py` | The two-hart cycle model fitted to the card's records (`check`, `fit`, `validate`, `explain`, `whatif`), the host's model of a launch (`host`, `table`: the same numbers `sparseparity_host --dry` and `spp_selftest --pipe-table` print), and the M4 steps' predictions (`m4`). |
| `cpu/sp.h` | Header-only C11/C++: the instance generator (bit-identical to `proto/spbits.c` and `proto/sp.py`), the ±1 and B-tile layouts, colex ranks and the T2 geometry, the closed forms, and the binary formats (work list, records, top lists, survivors). |
| `cpu/spref.c` | The reference solver in exactly the card's formulation: `gen`, `scan` (full, by work list, two-stage), `check`, `selftest`. |
| `cpu/spbase.c` | The CPU baselines: `vexh` (AVX-512, 8 candidates per register), `mitm` (bucketed meet in the middle with a random halving of the features), `batch` (B1, 8 instances per register). |
| `tools/planner.py` | `plan` (the work list, cut by modelled cycles, by default the fitted pipeline's (`--cost fit`; `--cost m1` is M1's model), and dealt round-robin across the shires, with host-side slices), `show`, `merge` (per-hart records → coverage, checksums, rescoring, ties), `closed`. |
| `tools/sptest.py`, `tools/spcore.py` | The CPU tests (107 checks; 115 with `--spbits`) and `sptest.py card` (a card's output against the reference, hart by hart); `spcore.py` is `sp.h` in Python. |
| `tools/bench_cpu.py`, `tools/table_cpu.py` | The CPU baseline ladder and its tables. |
| `cpu/data/2026-09-29-aifoundry3-r/` | The CPU baselines after the reviews (the table below). `cpu/data/2026-09-29-aifoundry3/` is the first run, superseded. |
| `data/2026-09-29-aifoundry3-sysemu-m5/` | M5: the `sys_emu` suite (83 cases), the CPU tests, the stage-2 benchmark, `card_run.sh m5 --dry`, the offline-verify test and the CPU's two-stage screens at P(loss) < 1e-4. `-sysemu-r4/`: M5 after R4's fixes (`build/sparseparity-t`). `-energy-dry/`: `energy.sh --dry` on both test cards. `-sysemu-m4r/`: M4 after R3 (`-sysemu/`: M1's code; `-sysemu-m4/`: M4 before R3's fixes). |

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
`.comment` (14-card-behaviour.md), so record and compare the `.text` hash, never the file's. The M1 kernel that ran
M1-M3 has `.text` sha256 `68b3f273c18f0b8e94244dba3a588b73ba1115e9b8478b2ae3bd83f7a65a234e` (`build/sparseparity-f`,
commit `92b168f`'s sources); `card_run.sh` records the hash with every run.

**M4's sources build into a new directory**, `build/sparseparity-h` (`-g` holds the same sources before R3's
fixes), so that `build/sparseparity-f` keeps M1's binaries: the kernel's CMake step is `BUILD_ALWAYS`, so rebuilding
`-f` after copying these sources over would turn it into M4's kernel. Its host runs M1's kernel and planner with
`--variant m1`, so `card_run.sh m4` compares both on one build. The M4 kernel's `.text` sha256 is
`4c2e7bdeb1b4e614109eca32fce8506291ff4ef49ac513237d84f5b57484015f`: R3's changes to the kernel are comments, so it is
the `.text` the review tested (`-g`); the host and the scripts changed.

```bash
cmake -S workloads/sparseparity -B build/sparseparity-h -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev   # from a tree's root
nice -n 19 cmake --build build/sparseparity-h -j4
make -C workloads/sparseparity/cpu O=$PWD/build/sparseparity-h-cpu
build/sparseparity-h/host/spp_selftest                       # CPU only: SELFTEST PASS (includes the model's cross-check)
```

On aifoundry3, where `~/nekko/workloads/sparseparity` holds M1's sources (`build/sparseparity-f`'s), the tree is a copy
in its own directory, and `card_run.sh` runs from that copy (`--build` and `--out` are absolute, or relative to the
copy's root):

```bash
tar --exclude=__pycache__ -czf - workloads/sparseparity docs/research/sparse-parity | \
    ssh aifoundry3 'mkdir -p ~/nekko/build/sparseparity-h-src && tar xzf - -C ~/nekko/build/sparseparity-h-src'
cd ~/nekko/build/sparseparity-h-src                          # on aifoundry3, while et-who shows the card free
cmake -S workloads/sparseparity -B ../sparseparity-h -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice -n 19 cmake --build ../sparseparity-h -j4
make -C workloads/sparseparity/cpu O=$HOME/nekko/build/sparseparity-h-cpu
../sparseparity-h/host/spp_selftest
```

(R1 found that an earlier report quoted a wrong hash, `76eb2d2f…`, for the previous kernel: its `.text`, extracted
this way on three hosts, was `d32d702ad0ffb4c4…`.)

**M5's sources build into `build/sparseparity-s`** (and `-s-cpu`; `-h` and `-i` keep M4's kernel). Its kernel's
`.text` sha256 is `3e14be325df307751f424372d0a1dccad244b3ffe0e46e43d82baefb300cb820` (aifoundry3, 29 September
10:04 PDT); without `--m1` it runs M4's paths (the screen is a flag, and the host sets it only for a two-stage run).
The tree also holds the energy change ("Energy per solve"): this host opens the ops node only.

```bash
tar --exclude=__pycache__ -czf - workloads/sparseparity docs/research/sparse-parity | \
    ssh aifoundry3 'mkdir -p ~/nekko/build/sparseparity-s-src && tar xzf - -C ~/nekko/build/sparseparity-s-src'
cd ~/nekko/build/sparseparity-s-src                          # on aifoundry3, while et-who shows the card free
cmake -S workloads/sparseparity -B ../sparseparity-s -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice -n 19 cmake --build ../sparseparity-s -j6
make -C workloads/sparseparity/cpu O=$HOME/nekko/build/sparseparity-s-cpu
../sparseparity-s/host/spp_selftest                          # SELFTEST PASS (with M5's checks)
```

**R4's fixes build into `build/sparseparity-t`** (and `-t-cpu`; sources in `~/nekko/build/sparseparity-t-src`,
aifoundry3, 29 September 11:08 PDT). They change the host and the scripts only: the kernel's `.text` sha256 is
`3e14be325df307751f424372d0a1dccad244b3ffe0e46e43d82baefb300cb820`, M5's, and `spp_selftest` passes. Both card
runs use it: `card_run.sh m5 --build ../sparseparity-t` and `energy.sh --build ../sparseparity-t`.

```bash
tar --exclude=__pycache__ -czf - workloads/sparseparity docs/research/sparse-parity | \
    ssh aifoundry3 'mkdir -p ~/nekko/build/sparseparity-t-src && tar xzf - -C ~/nekko/build/sparseparity-t-src'
cd ~/nekko/build/sparseparity-t-src                          # on aifoundry3, while et-who shows the card free
cmake -S workloads/sparseparity -B ../sparseparity-t -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice -n 19 cmake --build ../sparseparity-t -j6
make -C workloads/sparseparity/cpu O=$HOME/nekko/build/sparseparity-t-cpu
../sparseparity-t/host/spp_selftest                          # SELFTEST PASS
/opt/et/bin/riscv64-unknown-elf-objcopy -O binary -j .text ../sparseparity-t/kernel/sparseparity.elf /dev/stdout | sha256sum   # 3e14be32…
```

## The milestones and how to run each

### M0: the CPU side (no card)

```bash
nice -n 19 python3 workloads/sparseparity/tools/sptest.py --bin build/sparseparity-f-cpu --threads 2   # 107 checks, ~16 s
#   (--spbits build/sparseparity-cpu/spbits adds 8: the generator against SP3's proto/spbits.c)
python3 workloads/sparseparity/tools/planner.py plan --n 512 --k 4 --m 1850 --topm 0 --out l2.bin     # L2 on 32 x 32 minions
build/sparseparity-f-cpu/spref scan n=512 k=4 eta=0.4 m=1850 seed=1 plan=l2.bin out=l2.ref threads=6
python3 workloads/sparseparity/tools/planner.py merge --plan l2.bin --out l2.ref --inst 512,4,0.4,1850,1
nice -n 19 python3 workloads/sparseparity/tools/bench_cpu.py --bin build/sparseparity-f-cpu --out DIR --maxt 6   # ~25 min, detached
python3 workloads/sparseparity/tools/table_cpu.py DIR
```

### `sys_emu`: every kernel path in the functional simulator (no card)

```bash
setsid nohup bash workloads/sparseparity/sysemu_check.sh --build build/sparseparity-h --cpu build/sparseparity-h-cpu \
    > build/sparseparity-h/sysemu.log 2>&1 < /dev/null &      # 66 cases, ~45 min; --quick: 4 cases
```

It refuses to run on aifoundry2 (the DV2 validation counts any `sys_emu` or `*_host` process as a foreign device
process) and while any `tools/claims-v3` queue runs, and before each case it waits while `et-who --check` shows the
host's card held. Every case passes `--sysemu`; the checkers are the runtime's
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

M3 (all 32 shires) ran by hand on 29 September (`data/2026-09-29-aifoundry3-card/runs/m3-manual-0420`): L1 0.204 s
and L2 0.807 s on 1,024 minions, where M1's model had said 73 ms and 0.30 s. `card_run.sh m4` below includes M3's two
runs as its `m1` configuration.

### M4: what changed (the kernel, the host and the planner)

`tools/cycle_model.py` (`explain`) splits M3's gap to 270 cycles per op (5.7x at L1, 5.4x at L2) into the planner's
imbalance (1.52 / 1.48), hart 0's overhead per op (2.65 / 2.61: the epilogue, issue slots shared with hart 1, waiting for
rows) and the op itself (378 cycles, not 270). M4 implements the changes its `whatif` ranked highest that `sys_emu` can
check; each is a kernel flag or a host option, so M1 stays available on the same build (`--variant m1`) for an A/B.

| Change (the analysis' letter) | How | Switch (default) | Model: L1 / L2 on 1,024 minions |
|---|---|---|---|
| — M1 as run (M3) | | `--variant m1` | 207 ms / 835 ms (measured 204 / 807) |
| A: the plan balanced by the fitted model | the host's built-in plan and `planner.py` cut the row tiles by the fitted two-hart pipeline's period for the kernel that runs (`spp_common.h` `pipeTileCost` = `cycle_model.py` `steady_cost`, cross-checked to 0.1% by `spp_selftest`); host-side slices likewise (`--slice-cost`) | `--cost fit` (m1 with `--variant m1`) | 134 / 545 ms |
| B: incremental row generation | hart 1 reads X slice-major (`xt`, a new argument): per slice, one prefix word y ^ x_r1 ^ .. per run of rows that share it (r0 varies fastest in colex order) and one word per row, 16 consecutive words (2-3 lines), instead of 16 x (k-1) dependent loads through a pointer table on the stack; the expansion, the staged stores and the hand-off are M1's | `SPP_F_GEN_INC`, `--gen inc` | 113 / 427 ms (with A) |
| C: the epilogue hidden behind the next tile's ops | an output tile's last op writes f0..f31, the next tile's first S-1 ops accumulate in TenC, so the epilogue runs in 8 pieces between those ops and is complete before the next last op; it spills 8 registers (256 B) instead of 16 (512 B, all of hart 0's L1); a tile that could hold a new best is rescanned at the end of the row tile (deferred: the rescans are a superset of M1's, the records identical) | `SPP_F_EPI_HIDE`, `--epi hide` | 110 / 520 ms (with A) |
| B + C + A | | `--variant m4` (the default) | **86 / 403 ms** (2.4x / 2.1x) |
| D: 3 A buffers | op i reads L1 scratchpad buffer i % 3; ops in pairs, one TensorWait 7 per pair instead of one per op (the PRM's rule holds: no load overwrites a buffer an unwaited FMA reads; `sys_emu`'s L1 scratchpad checker enforces it); streamed A only | `SPP_F_ABUF3`, `--abuf 3` | 78 / 362 ms (with B + C + A; op 378 -> 300 assumed) |

Errata 1.29 by construction, as M1: TOUCH_ALL after the TensorWait 7 that follows every op writing f0..f31 (type F,
which `sys_emu` cannot see); inside the pieces, types A to C as in M1's reduction, and every piece ends with a taken
branch. Two traps the new code met in `sys_emu` and handles: **each hart's U-mode stack is 4,160 B**
(`KERNEL_UMODE_STACK_SIZE`, hart 1's directly below hart 0's; the memory checker stopped a first build whose hart 0
used 4.2 KB): the per-hart paths are `noinline`, and hart 0's deepest chain is 2.9 KB, hart 1's 2.7 KB (M1: 2.4 KB);
and **a function whose asm clobbers the f registers saves and restores the callee-saved ones** (`fsw`/`flw` of f8,
f9, f18..f27), so its next call reads registers the last one loaded (type A): the kernel does a TOUCH_ALL before
every such call (`CALL_GUARD`), and every function that carries a partial epilogue in registers is always inlined.

**Not done.** 2 staging buffers at L2 (the model's best L2 case, 301-337 ms) need 3.0 MB of scratchpad against 2.5 MB:
22 minions per shire fit, but lose 31% of the tensor units, which the model says gains nothing; the two-stage screen
is M5 (below), in M1's epilogue, at m1 = 320 and 1,152. E (both harts generate) is at most 1.06x (one issue slot). R1-7's earlier
release of the staging buffer conflicts with the deferred rescans, which reread A from it.

**The model's uncertainty.** M1's kernel is fitted (M3's busiest minion +1.4% / +3.6%; held out +5.0% / +7.5%). M4's
numbers are predictions: B assumes the staged stores cost what they did (x0.57-0.72 on generation; x0.27 if they do
not block), C assumes the epilogue still costs 1,606 cycles per output tile (the smaller spill may cut it), D assumes
300 cycles per op. **The host's guard** (`guard_s`, refused over `--max-kernel-s`, 4 s) is the largest of: the model
x1.3 once an M4 change is on (x1.15 for M1's kernel; `est_s`); M1's own model of the plan (`model_m1_s`, whatever cost
cut the plan: R3-5); the plan's own cost summed (`model_plan_s`); and, while an M4 change runs on predicted constants
(no `--pipe-set`), the same plan simulated with M1's fitted constants x1.15 (`model_fallback_s`: the launch if the M4
changes gain nothing; R3-1). `--trust-model` drops that last term; `card_run.sh m4` passes it on one step only, the
whole (256,5), after the same kernel ran the instance's two halves within x1.3 of their model. `--pipe-set K=V,..`
overrides the constants without a rebuild once the card has measured them (`cycle_model.py fit` refits them from the
records). The model's event loop stalled past about 1e10 cycles (a double's step exceeds its epsilon; R3 found it
through its own check, finding 8): a run now ends at its end time, and a model that stops before its last row tile
throws.

### M4 on a card: the A/B

`card_run.sh m4` needs the M4 build (default `--build build/sparseparity-h`) and checks that its host knows
`--variant` and `--trust-model`. Configurations: `m1` = `--variant m1` (M1 exactly, kernel and planner); `a` = M1's
kernel with the fitted plan; `b`, `c` = `a` plus the incremental generation or the epilogue in pieces alone; `m4` =
the default; `m4d` = `m4` with 3 A buffers; `m4a` = M4's kernel on `a`'s plan (`--pipe-set` with M1's fitted
generation constants and `HIDDEN=0`: it changes only the plan and the model; R3-2). A sliced step cuts its slice by
M1's cost (`--slice-cost m1`), so its configurations scan the same tiles. Every step is one locked, `timeout 10`
process with `--records-out`; a partial one is checked offline in full right after it, and the full-coverage M4 steps
(`m4-32s-{l1,l2}-{m4,m4d}`, `m4-32s-f5-m4`) once more at the end of the stage, with the full oracle (R3-4: the closed
forms do not check the lane maxima, the best or the tie flag that the new pieces compute; about 9 minutes of one CPU
thread, no device). The model column is `cycle_model.py m4`, which `sparseparity_host --dry` reproduces to the
millisecond (`card_run.sh m4 --dry` prints the model, the fallback and the guard). The largest guard is M1's
`m4-1s-l2-n-m1` (model 2.71 s, guard 3.12 s); `m4-32s-f5-m4`'s is 2.93 s with `--trust-model`, and would be 4.21 s
(its plan at M1's fitted speed, 3.66 s, x1.15) without it.

**The speed gate** (R3-1). Every step's line shows its launch time over its model (`x1.07 of model`, and `SLOW` past
x1.3, x1.15 for M1's kernel: information, not a stop). `m4-32s-f5-m4` runs only if `m4-32s-f5-h0-m4` and
`m4-32s-f5-h1-m4` ran within x1.3 of their model in the same `--out` directory; otherwise the script skips it, says
why, and goes on (`DONE m4: ... skipped (gates): m4-32s-f5-m4`). To resume after a stop, pass the same `--out` so the
gates are kept.

On aifoundry3 (the tree and the build as in "Build"):

```bash
cd ~/nekko/build/sparseparity-h-src
bash workloads/sparseparity/card_run.sh m4 --dry --build ../sparseparity-h --out ../sparseparity-h-dry-m4   # no device
et-who                                            # nobody on the card
bash workloads/sparseparity/card_run.sh m4 --build ../sparseparity-h --out ../sparseparity-card/aifoundry3-m4-$(date +%H%M)
bash workloads/sparseparity/card_run.sh m4gen --build ../sparseparity-h --out ../sparseparity-card/aifoundry3-m4gen-$(date +%H%M)
                                                  # optional: the generation probe (9 processes, timing only)
```

`m4` is 42 processes, each at most 10 s (about 4-6 minutes of card time with the in-process checks), then the offline
full oracle (about 9 minutes, no device, no lock).

First, **the race probe with M4's generation** (R3-3): the probe stage ran only M1's generation, the incremental one
stores faster after the same `fence; amoswapl.d`, and no other step here stages in DRAM (`fswl.ps`). Each checks
every minion with the full oracle in-process, like `card_run.sh probe`:

| Step | Geometry | Staging | Model |
|---|---|---|---|
| `m4-probe-l2-scp1` | L2 (S = 29, A streamed), 32 minions x 2,000 one-column tiles | scratchpad, 1 buffer | 0.29 s |
| `m4-probe-l2-dram1`, `-dram2` | the same | DRAM, 1 and 2 buffers | 0.49 / 0.45 s |
| `m4-probe-l2-scp1-abuf3` | the same, 3 A buffers | scratchpad, 1 buffer | 0.28 s |
| `m4-probe-c1-scp1`, `-dram1` | C1 (S = 3, A resident), 32 minions x 200 | scratchpad / DRAM, 1 buffer | 5 / 7 ms |

Then the A/B (model times):

| Step | Instance, minions | Tiles | m1 | a | b | c | m4 | m4d |
|---|---|---|---|---|---|---|---|---|
| `m4-1s-l1-w-*` | L1, one shire (32) | widest third (`--slice 0/3`) | 1.12 s | 1.11 s | | | 0.69 s | 0.59 s |
| `m4-1s-l1-n-*` | L1, one shire | narrowest third (`2/3`) | 2.48 s | 1.92 s | | | 1.25 s | 1.20 s |
| `m4-1s-l2-w-*` | L2, one shire | widest eighth (`0/8`) | 1.50 s | 1.48 s | | | 1.18 s | 1.01 s |
| `m4-1s-l2-n-*` | L2, one shire | narrowest sixteenth (`15/16`) | 2.71 s | 2.52 s | | | 1.66 s | 1.59 s |
| `m4-32s-l1-*` | L1, 32 shires (1,024) | all (closed forms) | 207 ms | 134 ms | 113 ms | 110 ms | 86 ms | 78 ms |
| `m4-32s-l2-*` | L2, 32 shires | all | 835 ms | 545 ms | 427 ms | 520 ms | 403 ms | 362 ms |
| `m4-32s-l2-m4a` | L2, 32 shires | all; M4's kernel on `a`'s plan | | | | | 545 ms (the host's model: M1's constants); 414 ms at M4's predicted speed (max/mean 1.032) | |
| `m4-32s-f5-h0-*` | (256,5,0.4,1925), 32 shires | first half (`0/2`) | 1.30 s | | | | 0.83 s (a gate) | 0.76 s |
| `m4-32s-f5-h1-*` | (256,5), 32 shires | second half (`1/2`) | 2.55 s | | | | 1.41 s (a gate) | 1.34 s |
| `m4-32s-f5-m4` | (256,5), 32 shires | all (closed forms; M1 whole is 4.4 s, over the limit); `--trust-model`, gated | | | | | 2.25 s | |

Every step expects PASS: the closed forms on the whole-instance steps, the in-process oracle on a sample and the
full oracle offline on the slices and on the five full-coverage M4 steps. What to read: `kernel.cycles_max` (the
launch), `cycles_max / cycles_median` (the balance: A should bring it from 1.55 to about 1.00), `wait_cycles_max`
(hart 0 starved of rows: B's effect) and `cycles_per_op_busiest`. Each plan is cut by its own configuration's
constants, and M4's are predictions: if they are off, `m4` against `a` mixes the kernel's gain with the plan's
imbalance. At L2 the M4-cut plan run at M1's constants models 563 ms at max/mean 1.035 (`a`'s own plan: 545 ms,
1.002), and `a`'s plan run at M4's constants 414 ms at 1.032 (`m4`'s own: 403 ms, 1.004); at L1 all four are within
1.006 (R3's own computation, with other assumptions, found up to 1.16 and 1.11 at L2). `m4a` against `a` is the kernel
alone on one plan; refit (`cycle_model.py fit` on the new records) before reading balance off `m4`. Against the CPU's
best (L1 148 ms, L2 459 ms on 6 threads), `m4` at 86 / 403 ms would be 1.7x / 1.1x.

**If `m4d` alone mismatches** (R3-6): with 3 A buffers an output tile's last op (DST = 1) at an even index is followed
by the next tile's first op (MUL = 1) with no TensorWait 7 between them. The PRM needs none between tensor ops, but
M1 never issued that sequence on silicon; the first thing to try is a `t_wait(7)` after every last op
(`kernel/sparseparity.c`, `tile_abuf3`).

**`card_run.sh m4gen`** is the measurement the analysis asked for: 32 minions x 400 one-column-tile row tiles, timing
only, so the pipeline runs at hart 1's pace, at k = 4 (S = 7, 29) and k = 5 (S = 31), with M1's generation, the
incremental one, and the incremental one with `--gen-probe nostore` (the same expansion, stored with plain `fsw.ps`
into a 256 B buffer in hart 1's L1 instead of the staging buffer: hart 0 then multiplies stale rows, so timing only).
Cycles per row tile = `kernel.cycles_max` / 400; the model says 34k / 21k at L1 and 138k / 86k at L2 (M1 / inc) and
cannot say what `nostore` gives: the difference is the staged stores' cost, which decides where B lands. A caveat
(R3-9): the 256 B buffer is 4 of the 8 L1 lines hart 1 has in scratchpad mode, shared with the slice-major X lines and
the stack, so its dirty write-backs may count as generation time, and incremental minus `nostore` can understate the
staged stores' cost.

### Energy per solve (`energy.sh`)

Board energy per solve of variant b on one card, with the energy catalogue's discipline (`tools/claims-v3/lib.sh`:
the card lock for the whole run, the sampler started with retries and stopped with SIGTERM only, every device
process under `timeout 10`) and its method beside a better headline. **It has not run on a card.** R4 (below) found
no card-safety blocker in it; its findings are applied.

**The host change it needs.** `sparseparity_host` opened the card's management node as well as its ops node
(`createPcieDeviceLayer(true, true)`), and the driver lets one process hold the management node
(`et-driver/et-soc1-pcie.c`: `EBUSY`), which `ettelem` holds while it samples: the build that ran M4
(`build/sparseparity-h`) cannot run under the sampler. The host now opens the ops node only, as `pciebench`'s host
does (the device properties come through it: `DevicePcie.cpp:365-368`; `sgemm`'s host still opens both). Its JSON
line carries `launch_epoch_ms` (the first launch's start and the last completed launch's end, Unix ms) and
`host_cpu_s` (the process's CPU time, every thread, `getrusage`: over that burst and over the whole process).
`energy.sh` refuses a host binary without `launch_epoch_ms`. **The build is `build/sparseparity-t`** (M5's sources
with R4's fixes: kernel `.text` `3e14be32…`, "Build"), whose kernel without `--m1` runs variant b's paths; the steps
`m5-l1-b` and `m5-l2-b` of `card_run.sh m5` rerun variant b on it against 29 September's 0.130 and 0.429 s. The build
that R4 checked, `build/sparseparity-i` (the kernel that ran M4, `4c2e7bde…`, and the ops-node host without
`host_cpu_s`), also runs: `energy.sh` then bounds the host's share by the whole process's CPU time.

**One run** is one preset: `l1`, `l2`, `f5h0` or `f5h1` (the two halves of (256,5) as `data/2026-09-29-aifoundry3-card-m4/f5-b`
ran them, `--slice I/2 --slice-cost m1`), all `--variant m1 --cost fit --gen inc` on 32 x 32 minions. The script
plans with the host's `--dry` (no device, niced) how many launches fill `--target-s` (6 s) and still start under the
host's own budget rule (a launch needs a timeout of at least max(1, 1.25 x guard + 0.5) s, whole seconds of the time
left before 9 s less 0.5 s); waits for `et-who --check` and no other user's device process; takes the card lock on
fd 9 for the whole run; starts `ettelem sample --every-ms 100` (10 Hz, as `lib.sh` and the catalogue: `board_w` is
held for one SP pass, which a 20 Hz sampler only lengthens, 0.255 to 0.296 s, E58); idles 8 s; runs ONE `timeout 10`
host process with `--reps R --oracle sample` (every launch read back and checked against the first), its CPU time
taken by bash's `times`; idles 10 s; stops the sampler; releases the lock; reduces. About 30 s per run: the lock
about 27 s, the card's ops node at most 10 s. It refuses aifoundry2 (the DV2 validation treats a sampler or a
`*_host` process as foreign) unless `SPP_ALLOW_AIFOUNDRY2=1`; there only the stubs' `--dry` runs.

| Preset | Launches | Burst | Launch (29 Sep) |
|---|---|---|---|
| `l1` | 44 | 5.9 s | 0.130 s |
| `l2` | 14 | 6.1 s | 0.429 s |
| `f5h0` | 6 | 5.8 s | 0.958 s |
| `f5h1` | 3 | 4.8 s (its guard leaves the host no fourth start) | 1.589 s |

These are the first card runs with `--reps` > 1 (every earlier card JSON has one launch), and L1's 44 launches at
7.3 per second are the densest stream of short kernels yet (aifoundry2's Master Minion hang came in such a stream,
cause not established): run a 3-launch smoke run and `l2` before `l1`. Each launch keeps its own timeout, and the
host checks every one.

**The reduction** (`tools/energy_reduce.py DIR`, no device). The burst [lo, hi] is the host's `launch_epoch_ms`.
- **The headline, J per solve over idle: the SP's board average** (`sp.board_avg_w`, the PMIC's own running average
  of its input power; unit gain, 1.00-1.01 against first-order-filtered `board_w` on E58's bursts, R4) integrated over
  [lo - 1, hi + 6] above the before bracket, less the leakage's rise: the catalogue's law (23.257/36 e^((T-80)/36)
  W/°C) times the measured die temperature over the before bracket's, sample by sample. The average does not alias
  the gaps between launches, and a unit-gain filter keeps the energy it delays. **Claimed: ±3%** (the die
  temperature reads whole degrees; the law is aifoundry2's, and aifoundry3's own idle curve is 0.26-0.30 W/°C at
  55-57 °C against its 0.33, `2026-09-22-horace-aifoundry3/leakage_crosscard.json`).
- **The board total per solve, idle included** (the before bracket's idle over the burst, the leakage's rise, the
  headline): ±2%.
- **Cross-checks.** The catalogue's method (`analyze_catalogue.py`'s windows and law on the point-sampled `board_w`,
  so the numbers sit beside the catalogue's): ±3% plus one pass of the step per busy reading at idle more or fewer
  than expected (the busy passes x the gaps' share), and one more; one such reading moves a run by 1/N of its step,
  N the busy passes (4-6% here), which is why it is no longer the headline. The ramp baseline (the SP average above
  a straight line from the before bracket to a late bracket [hi + 6, hi + 8]; no temperature, no law): it misses the
  fast thermal stages (`docs/findings/11-thermal-model.md`: 1.5 s and 4 s, 0.16 °C/W, which heat the die within the
  burst and let it cool within seconds of its end) and reads about 4% high on the adversarial test card. The
  uncorrected value (all of the leakage's rise).
- **The rails** (minion, SRAM, NoC: the PMIC's running averages, tau ~1.05 s, E58) over the ramp baseline, since no
  law is known per rail: upper bounds, -2% to +7%; unmetered = the headline minus the rails, ±15% (a small difference
  of larger numbers).
- **The host's share.** The card does not solve alone: the host drives it (the runtime polls the device, E50) and its
  package idles meanwhile. Its package energy is root-only on aifoundry3 (below), so it is bounded: an assumed idle of
  10-20 W over the burst plus 10-38.5 W per busy core-second (38.5 = the CPU side's own 251 W spread over its 6
  busy cores), the busy core-seconds the host's `host_cpu_s.burst`.
- Also: mean board watts, solves per second (wall and kernel), die temperature before, busy and after, the clock in
  every busy sample, the sampler's latency; flags for a moved clock, a starved sampler, short windows, a host short of
  its reps, a foreign device process, and the catalogue method off the headline by more than both claims.

**`combine`** adds the slices of one solve (`combine DIR DIR --label NAME`: the halves of (256,5)) and refuses
(exit 2) unless the parts are one instance (its hash), one variant and one kernel, and their slices are I/N for one N
with every I in 0..N-1 exactly once: a rerun of a half is not a third part. Name the parts explicitly (the commands
below give each run its own directory), never with a glob.

**The CPU side.** The CPU's energy per solve is its measured 6-thread time x an assumed 125-251 W, idle included:
aifoundry3's package energy counter is root-only (`/sys/class/powercap/intel-rapl:0/energy_uj` 0400 root;
`/dev/cpu/*/msr` 0600 root; `perf_event_paranoid` 2; the only sudo rule is `et-holders`; checked 29 September, and
`energy.sh` records it with every run). Its time is its fastest method that keeps the secret with P(loss) ≤ 1e-4,
since the card's one-stage scan loses nothing: L1 the meet in the middle, 0.148 s (expected over 10 seeds; the
two-stage screen at 8.8e-5 takes 0.166 s); L2 the two-stage screen at m1 1,152, 0.508 s (P(loss) 8.9e-5; the earlier
0.459 s at m1 1,024 loses the secret with 6.2e-4); (256,5) the same, 1.769 s (8.9e-5; 1.58 s at 6.2e-4). The reducer
states two ratios: the CPU over **the card's board alone** (the host not counted) and over **the card's board plus the
host's package** (the bounds above). An M5 run's energy (not measured here) must add stage 2 on 6 host threads the
same way (`two_stage.stage2_s` x 6 busy cores).

**Dry tests** (`--dry`: `tools/energy_stub.py` stands in for the host and the sampler, in real time; no device, no
lock). `--stub-card base` simulates a card with the reducer's own laws (the same leakage law, unit-gain first-order
filters with the tau it assumes, one slow thermal stage, the launch edges the host's): a **plumbing test**, not a
test of the method. `--stub-card alt` breaks each of those: another leakage law (aifoundry3's idle curve, 0.27 W/°C
at 56 °C), `11-thermal-model.md`'s thermal chain, the board average with gain 1.01 and tau 0.8 s, the rails with
tau 1.3 s, `board_w` one SP pass late, other rail shares, the die idling at 55.7 °C instead of 55.3 °C (the whole-degree
rounding the other way), and the card's power starting 5 ms after the host's launch mark and ending 3 ms before its
end mark (the truth's burst is the card's own). The reducer's TRUTH check holds each value to its claim above.
Nine runs on aifoundry3 (29 September, 11:14-11:17 PDT, `--real-plan`: the real host's `--dry` plan with
`build/sparseparity-t`; `data/2026-09-29-aifoundry3-energy-dry/`), every preset on both cards and L1 on the alt card
at 20 Hz, every one TRUTH PASS; error against the injected energy, %:

| Run | Headline (±3) | Total (±2) | Catalogue (at idle / busy readings, expected) | Ramp | Rails: minion, SRAM, NoC (-2..+7) | Unmetered (±15) | Edges, ms |
|---|---|---|---|---|---|---|---|
| l1 base | -2.83 | -0.76 | -6.70 (2/19, 0.6) | -0.11 | -0.22, +0.52, -0.49 | -10.9 | -0.5 / -0.6 |
| l2 base | -1.77 | -0.49 | +0.58 (0/19, 0.2) | -0.08 | -0.18, +0.59, -0.50 | -6.8 | -0.1 / -0.8 |
| f5h0 base | -2.15 | -0.63 | +0.03 (0/20, 0.1) | +0.03 | -0.08, +0.60, -0.38 | -8.6 | -0.2 / -0.4 |
| f5h1 base | -2.74 | -0.78 | +0.14 (0/15, 0.0) | +0.06 | -0.05, +0.44, -0.24 | -11.0 | -0.7 / -0.3 |
| l1 alt | +0.95 | +1.05 | -0.66 (2/21, 0.6) | +4.39 | +1.32, +5.80, +1.90 | -2.0 | -5.6 / +3.0 |
| l2 alt | +0.56 | +0.79 | -2.47 (1/22, 0.2) | +4.32 | +1.34, +5.88, +1.92 | -3.7 | -5.3 / +3.0 |
| f5h0 alt | +0.89 | +0.91 | +0.87 (0/20, 0.1) | +4.49 | +1.39, +5.91, +2.05 | -2.5 | -5.2 / +2.5 |
| f5h1 alt | +1.47 | +1.18 | +0.34 (0/17, 0.0) | +4.63 | +1.28, +5.65, +1.86 | +0.3 | -5.7 / +2.7 |
| l1 alt, 20 Hz | +0.94 | +1.05 | -7.92 (3/18, 0.5) | +4.32 | +1.33, +5.86, +1.95 | -2.1 | -5.4 / +2.1 |

The headline's error follows the whole-degree rounding of the die temperature (low when the idle die sits at
55.3 °C, high at 55.7 °C); the catalogue's follows its readings at idle (-6.7% and -7.9% with 2 and 3 of them against
0.5-0.6 expected); the ramp is exact on the base card and 4.3-4.6% high on the alt one (the fast thermal stages).
`combine` of the two halves gave (256,5) 38.0 J (base) and 39.3 J (alt) over idle, 100.6 / 100.5 J with the idle,
and refused f5h1 twice, f5h1 twice with l1, and one half alone (exit 2). A host that stops short of its `--reps`
is flagged, not failed; a host binary without `launch_epoch_ms` is refused before anything runs; on aifoundry2 a
non-dry or `--real-plan` run is refused.

**On aifoundry3** (the build as in "Build"; `et-who` first; about 30 s each, with a pause between; one start time
`S` names the session's directories, so that `combine` gets exactly the two halves):

```bash
cd ~/nekko/build/sparseparity-t-src
S=$(date +%H%M); E=workloads/sparseparity/energy.sh; B="--build ../sparseparity-t"; D=../sparseparity-energy/aifoundry3
bash $E l2 --dry --real-plan $B --out $D-$S-dry-l2          # no device: the real host's plan, the stubs
bash $E l2 --reps 3 $B --out $D-$S-smoke-l2                 # the first multi-launch card run: 3 launches
bash $E l2   $B --out $D-$S-l2
bash $E l1   $B --out $D-$S-l1
bash $E f5h0 $B --out $D-$S-f5h0
bash $E f5h1 $B --out $D-$S-f5h1
~/nekko/.venv/bin/python3 workloads/sparseparity/tools/energy_reduce.py combine $D-$S-f5h0 $D-$S-f5h1 --label "(256,5)" --json $D-$S-f5.json
```

**Expected** (a prediction, not a measurement): each run `DONE <preset>: ok`, the host `PASS` with every launch
done (l1 44, l2 14, f5h0 6, f5h1 3; the smoke run 3) and solved (the halves: f5h0 finds the secret, f5h1 does not
hold it). aifoundry3 idles at about 24-26 W at 55-60 °C; its full-rate int8 matmul adds 26.3 W (E37), and this
kernel keeps the tensor unit busy about 35-45% of the time (318 of 730-910 cycles per op) while hart 1 generates
rows, so about +12-20 W and 36-46 W of board power in the burst. Over idle, J per solve: L1 1.3-2.9 (about 2), L2
4.5-9 (about 7), `f5h0` 10-20 (about 15), (256,5) whole 26-55 (about 36); the board total with the idle about 5.5,
18 and 100 J; 7.3-7.5, 2.3 and 1.0 solves per second (L1, L2, `f5h0`); the die 1-3 °C above its idle; the minion rail
most of it, unmetered about a sixth; the catalogue method within its claim of the headline. The host: its CPU time
over the burst is measured for the first time (the runtime's idle poll is every 500 µs, E50: between 0.1 and 1 core
busy), so its share is 1.5-8 J per solve at L1, 5-25 J at L2 and 28-150 J for (256,5). Against the CPU's best at
P(loss) ≤ 1e-4 (L1 18.5-37 J, L2 63.5-128 J, (256,5) 221-444 J, all assumed): the card's board alone about 3-8x (L1,
L2) and 2-5x ((256,5)) in the card's favour; with the host's package added, about 1.3-6x (L1, L2) and 0.8-3.8x
((256,5)): at the pessimistic end (a host core busy through the burst at 38.5 W, a 20 W idle) the whole (256,5)
solve is level. The CPU's side and the host's share are assumed; measuring them needs the lab admin: read access to
`energy_uj`, or a wall meter.

### M5: the two-stage screen (stage 1 on the card, stage 2 on the host)

DESIGN.md §2.7: the card scores every candidate on the first m1 samples and logs those with c1 ≥ τ1; the host
rescores the survivors on all m samples. The secret is lost only when its own c1 falls under τ1, since whenever it
survives it is also the best survivor on all m. **It has not run on a card**: `card_run.sh m5` is the step for the
owner's session ("M5 on a card"). The kernel, the host and the scripts are new; everything else is M4's.

**Why not m1 ≤ 192 (A resident).** Keeping the secret with P(loss) < 1e-4 fixes τ1 from its binomial tail (its
disagreements are Bin(m1, η); `design_model.py screen_at`, the host's `screenKept`), and at η = 0.4 and m1 = 192 that
τ1 is −12: 83% of L2's 2.8e9 candidates and of (256,5)'s 8.8e9 survive, more than a one-stage scan costs. At L1
(η = 0.3) m1 = 192 needs τ1 = 28 and keeps 7.2e7 (580 MB of log). The resident regime also buys less than it seemed:
at S ≤ 3 the epilogue (1,606 cycles per output tile, M3's fit) outweighs the ops (3 × 256), so the fitted model puts
L1's scan at m1 = 192 only 30% under m1 = 320. The exact tails at P(loss) < 1e-4, with the fitted model of variant
b's scan at m1 on 1,024 minions (the screen's own cost not included):

| Instance | m1 = 192 (S1 = 3) | m1 = 320 (5) | m1 = 1,024 (16) | m1 = 1,152 (18) | m1 = 1,280 (20) |
|---|---|---|---|---|---|
| L1 (512,4,0.3,448) | τ1 28, 7.2e7 survivors, 65 ms | **τ1 66, 3.8e5, 93 ms** | | | |
| L2 (512,4,0.4,1850) | τ1 −12, 2.3e9 | τ1 −2, 1.6e9 | τ1 88, 9.2e6, 202 ms | **τ1 106, 2.8e6, 222 ms** | τ1 124, 8.2e5, 243 ms |
| (256,5,0.4,1925) | τ1 −12, 7.3e9 | τ1 −2, 5.0e9 | τ1 88, 2.9e7, 1.00 s | **τ1 106, 8.7e6, 1.10 s** | τ1 124, 2.6e6, 1.21 s |

The scan plus the log's readback plus stage 2 is least at the bold points: L1 m1 = 320, τ1 = 66 (P(loss) 8.8e-5);
L2 and (256,5) m1 = 1,152, τ1 = 106 (8.9e-5). The rule is one-sided, c1 ≥ τ1, as `spref`'s and `spbase`'s screens
are: the secret's c is positive at η < 0.5, and |c1| ≥ τ1 would double the survivors for nothing. `card_run.sh m5`
keeps one resident step, L1 at m1 = 192 with τ1 = 40 (P(loss) 1.8e-3, 6.7e6 survivors), to measure that regime.

**The kernel** (`SPP_F_SCREEN`; M1's epilogue, as in variant b = `--variant m1 --cost fit --gen inc`; the kernel and
the host refuse the screen with `--epi hide` or `--abuf 3`). Each output tile's epilogue, after the staircase mask
(a masked entry is 0, and τ1 ≥ 1), compares the tile with τ1 in the vector unit: the reduction already spills rows
8-15 (f16..f31), which frees f16 for τ1 − 1 broadcast; `fltm.pi md, f16, fr` sets lane l of mask md when entry l of
register r is ≥ τ1, seven registers into m1..m7, and one `mova.x.m` reads them all (m0, the active mask, stays 0xFF):
32 compares and 6 moves per tile. Rows 0-7 are stored beside the spill only when one of their masks is set (their
reduction overwrites them); rows 8-15 are in the spill already. A tile with a survivor goes through plain C that logs
each set bit as `cpu/sp.h`'s entry (row | j << 40 | c1 << 52) in (row, column) order into the minion's log. Every
found entry is counted and summed into the minion's `SppSurvHdr` (found, stored, the capacity, the sums of the packed
entries and of c1, the tiles with a hit, the epoch, an overflow flag); an entry is stored while the log has room, so
a full log is counted, flagged and fails the run, never silent. Errata 1.29: f16 is written by `fbcx.ps` (type B)
and read after a taken branch; f0..f15 after `mask_tile`'s taken branch or `TOUCH_ALL`; the reloaded rows after an
`fmv.x.w` each and a taken branch, as in `reduce_tile`; the mask registers are outside the VPURF erratum, and
`mova.x.m` is its own dependency resolver. Hart 0's stack: 2.4 KB on the screen's path (4,160 B allowed). The
screen's cost is assumed (A) until a card measures it: 100 cycles per output tile, 200 more when rows 0-7 hold a
survivor, 60 per survivor, added to the fitted model's epilogue (`E_OUT`) in the plan's costs and every model (139
cycles per tile at L2's m1 = 1,152, against a tile's 18 × 378 + 1,606).

**The host** (`--m1 M1 --tau1 T`): the card's instance is the first m1 samples of the m-sample one (the generator is
prefix-consistent: `spp_selftest` checks the prefix against the instance generated with m1), so every stage-1 check
is M1's on m1 samples: the count, both closed forms (they apply with m1), the best rescored, the oracle. Each
minion's log holds 1.5 × its expected share (its candidates × the null tail) + 10σ + 256 entries (`--surv-cap N`,
`--surv-factor F`): the CPU's screens counted within 0.3% of the expectation at L2 and (256,5). After the last
launch the host reads the headers and the whole log area in one copy (a copy per minion would cost 0.1-0.4 ms each,
E50), timed. **Before every launch it fills the whole log area with all-ones** (R4), outside the timed launch (about
21 ms for (256,5)'s 108 MB at aifoundry3's 5.2 GB/s staged rate, E50; `two_stage.poison_s`, and the budget rule
counts it): an entry the kernel did not write reads as row 2^40 - 1, j 4095, c1 -1, which fails the entry checks,
stage 2 and the oracle, so a log line that never reached DRAM cannot pass as an identical entry an earlier launch or
process left there (the entries carry no epoch, and the header sums come from registers; `sys_emu` starts its DRAM at
0xDEADBEEF, a card at whatever the last process left). The logs may take 512 MB on a card (3 GB in `sys_emu`), and
the host allocates its copy after `--dry`'s return. Then, before the sampled oracle (which fills the time left):
- **headers**: this launch's epoch, the capacity the host set, stored = min(found, cap), the overflow flag; **counts
  per minion**: found within 8σ of its expected share (and the total within 5% once 1e5 are expected); **entries**:
  c1 ≥ τ1, each in its minion's blocks and in their order, and (nothing overflowed) their sums equal the header's;
- **stage 2** (`--stage2-threads`, default 6): every stored entry rescored on all m samples (the row's prefix
  y ^ x_r1 ^ .. cached and r0 advanced in place: 23 ns per survivor on one aifoundry3 thread at L2, 7.6 ns on six),
  and **each logged c1 re-derived on the first m1 samples**, so every value the card logged is checked, and an
  invalid entry (a row past the last, j ≤ max(R)) is caught; the answer is the best on all m, a tie flagged;
- **the oracle's survivors**: on the minions the oracle rescores (all with `--oracle on`, a sample under `auto`), the
  CPU's list of c1 ≥ τ1 in the kernel's order equals the log entry by entry, with the found count and both sums.

The JSON line's `result` is stage 1's (the best on the first m1 samples); `two_stage` has the plan (m1, τ1, P(kept),
the expected survivors, the logs' size, the model), found and stored, overflowed minions, `found_over_expected`,
`minion_z_max`, the readback's and stage 2's times, stage 2's answer, `solved`, `secret_survived`, and `solve_s` =
the launch + the readback + stage 2 (`model_solve_s` its model); `checks` adds `survivors`, `survivors_oracle` and
`stage2`. `--records-out FILE` also writes `FILE.surv` (the headers and the stored entries), which `--verify-records`
reads for the full oracle offline; `--surv-out FILE` writes every stored entry in `spref log=`'s order. Offline, a
flipped c1 bit in one entry fails three ways (the minion's sums, its oracle list, stage 2) and a lowered found count
fails the header check and the oracle (`data/2026-09-29-aifoundry3-sysemu-m5/verify-test.txt`).

**Two controls** (R4): `--perturb tau` gives the kernel τ1 + 2 (the next c1 of the same parity) while the host checks
τ1, so the kernel misses every survivor at τ1 and τ1 + 1; every stage-1 check, the entries (each c1 ≥ τ1 + 2 ≥ τ1)
and stage 2 still pass, and only the survivor oracle (and, with enough survivors, the counts) can see it: it must say
MISMATCH. On the minions the sampled oracle skips, the checks are self-consistency and the counts (8σ per minion, 5%
in total), which miss a small loss, so a whole-instance S2 on a card is provisional until the full oracle offline
passes. `--perturb lostlog` has the kernel log into a spare area while the host poisons and reads back the usual one,
as if no log line reached DRAM: the entries, their oracle and stage 2 must fail.

### M5 on a card

`card_run.sh m5` needs R4's M5 build (default `--build build/sparseparity-t`; it refuses a host without
`--perturb tau|lostlog`, which also means without the logs' poisoning). Every step is one locked, `timeout 10` process with
`--records-out`; the four whole-instance two-stage steps also get the full oracle offline at the end of the stage
(every minion's survivor list; about 1 min at L1 and L2, 3 min at (256,5), no device): their S2 is printed
PROVISIONAL at the step and confirmed (or the stage stops) at the end. Then each `<step>.rec.surv` (20-70 MB, about
150 MB per session) is gzipped beside its sha256 and its 64 KB of headers alone (`.rec.surv.hdr.gz`, a few KB):
commit those two, never the logs (`gunzip -k` one before another `--verify-records`). "Model" is the host's `model_solve_s` (`card_run.sh m5 --dry` prints it): stage 1's kernel (variant b's
fitted model with the screen's assumed cost) + the log's readback + stage 2 on 6 threads. Variant b ran L1, L2 and
(256,5) at x1.15, x1.00 and x1.10 of its fitted model on 29 September.

| Step | What it runs | Expect | Model |
|---|---|---|---|
| `m5-1s-small` | (128,4,0.4,1850), m1 1,152, τ1 60, one shire, the full oracle in-process (every minion's survivors) | S2 | 70 ms |
| `m5-ovf` | L1 slice 0/16 on one shire, m1 320, τ1 66, `--surv-cap 8`: every log too small | OVF | 0.16 s |
| `m5-negmask` | C1 (128,4,0.2,192), m1 128, τ1 24, one shire: the mask control | NEGM | 15 ms |
| `m5-negtau` | `m5-1s-small` with `--perturb tau`: the kernel screens at τ1 + 2 = 62, the host checks 60 | NEGT | 70 ms |
| `m5-lostlog` | `m5-1s-small` with `--perturb lostlog`: the kernel logs into a spare area, the host reads the poisoned one | LOST | 70 ms |
| `m5-l1-b` | L1 one stage, variant b (this session's reference; 0.130 s on 29 September) | PASS | 113 ms |
| `m5-l1-s320` | L1, m1 320, τ1 66 (P(loss) 8.8e-5, 3.8e5 survivors, 8 MB of logs) | S2 | 101 ms |
| `m5-l1-res192` | L1, m1 192, τ1 40: A resident (P(loss) 1.8e-3, 6.7e6 survivors, 85 MB) | S2 | 127 ms |
| `m5-l2-b` | L2 one stage, variant b (0.429 s on 29 September) | PASS | 427 ms |
| `m5-l2-s1152` | L2, m1 1,152, τ1 106 (P(loss) 8.9e-5, 2.8e6 survivors, 38 MB) | S2 | 262 ms |
| `m5-f5-s1152` | (256,5), m1 1,152, τ1 106 (8.9e-5, 8.7e6 survivors, 108 MB), whole, one process (guard 2.17 s) | S2 | 1.22 s |

S2 = PASS (the survivors, their oracle and stage 2 exact) and stage 2's answer the secret, unique; OVF = every log
overflows: flagged, the run fails, and every other check passes (the stored prefixes equal the oracle's); NEGM as in
M1; NEGT = FAIL with the survivor oracle MISMATCH on every minion, the survivors `ok` or `COUNT` (the per-minion and
total counts: 12% fewer at τ1 + 2 here), and the records, count, closed forms, oracle and stage 2 exact; LOST = FAIL
with the survivors, their oracle and stage 2 MISMATCH (every entry the poison), everything else exact. Each line shows the launch over its stage-1 model and the two-stage fields: found (and over the expectation),
overflow, the readback, stage 2, `solve_s` against `model_solve_s`, the answer.

```bash
cd ~/nekko/build/sparseparity-t-src        # aifoundry3: these sources, built into ../sparseparity-t ("Build")
bash workloads/sparseparity/card_run.sh m5 --dry --build ../sparseparity-t --out ../sparseparity-t-dry-m5   # no device
et-who                                      # nobody on the card
bash workloads/sparseparity/card_run.sh m5 --build ../sparseparity-t --out ../sparseparity-card/aifoundry3-m5-$(date +%H%M)
```

Eleven processes, each at most 10 s (about 1-2 minutes of card time), then about 6 minutes of offline oracle.

**Expected, against the CPU's two-stage screen at the same P(loss).** The card: the model, and in brackets the model
with stage 1 at variant b's measured ratio. The CPU: `spbase vexh` with m1 and τ1, stage 2 on m (6 threads pinned to
cores 0-5, aifoundry3, 29 September 10:03 PDT, median of 5, stage 2 once; `data/2026-09-29-aifoundry3-sysemu-m5/cpu2s.jsonl`).

| Instance | card two-stage (P) | card one stage b (measured) | CPU two-stage, P(loss) < 1e-4 | CPU / card |
|---|---|---|---|---|
| L1 (512,4,0.3,448) | 0.101 s (0.115 s) at m1 320 | 0.130 s | 0.166 s at m1 320 (0.165 + 0.001); the CPU's best is the meet in the middle, 0.148 s expected | 1.3-1.5x vs MITM |
| L2 (512,4,0.4,1850) | 0.262 s at m1 1,152 | 0.429 s | **0.508 s** at m1 1,152 (0.488 + 0.020); 0.524 at 1,280; 0.551 at 1,024/88 | **1.9x** |
| (256,5,0.4,1925) | 1.22 s (1.33 s) at m1 1,152 | 2.55 s (two halves) | **1.769 s** at m1 1,152 (1.694 + 0.075); 1.854 at 1,280; 1.932 at 1,024/88 | **1.3-1.45x** |

The CPU's earlier two-stage figures (L2 0.459 s, (256,5) 1.58 s) were at m1 = 1,024, τ1 = 104, which loses the secret
with P = 6.2e-4; rerun in this session they took 0.450 and 1.573 s. At P(loss) < 1e-4 the CPU's best screen is
m1 = 1,152 as well, 11-13% slower. The card's side is a prediction: stage 1 carries the screen's assumed cost and
variant b's fitted constants, and `m5-l1-b` and `m5-l2-b` rerun the one-stage reference in the same session.

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

**M4's kernel** (`--variant m4`, the default; "M4: what changed" above): hart 1 builds rows from the slice-major copy
of X (`xt`) one run of shared prefix at a time; hart 0 runs each output tile's epilogue in 8 pieces between the next
tile's first S-1 ops, spills 8 registers, and rescans possible bests at the end of the row tile; with `--abuf 3`,
streamed A rotates through 3 L1 buffers with one TensorWait 7 per pair of ops. The records, the checks and the
formats are M1's.

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

That was M1's cost, and M3 showed it wrong where it matters: a one-column-tile row tile costs 37k cycles, not 5.6k,
and a 32-column one 157k, not 117k, so the busiest minion drew 2,703 row tiles to the median's 1,176 and ran 1.55x
the mean. **M4's default cost (`--cost fit`, both planners)** is the fitted pipeline's period for a long run of
identical row tiles with that many column tiles (`cycle_model.py` `steady_cost`, ported to `spp_common.h`
`pipeSteady`), for the kernel that runs (M1's or M4's constants), its staging (buffers, scratchpad or DRAM) and the
shire's L2 demand M3 measured (U = 0.58 at 32 minions per shire); the deal is unchanged. Simulated minion by minion,
the fitted plan runs L1 at max/mean 1.002-1.006 with either kernel (M1's plan: 1.55); `spp_selftest` checks it.
`--cost m1` (and `--variant m1`) restores M1's plans; `planner.py plan --cost m1` likewise. The host's `model_s` is
now the fitted model's time for the kernel that runs (every minion's row tiles simulated in order), whatever cost
cut the plan; `model_m1_s` is M1's model of the same plan (always M1's cost: R3-5), `model_plan_s` the plan's own
cost summed on its busiest minion, `model_fallback_s` the plan at M1's fitted constants (an M4 kernel only) and
`guard_s` what the 4 s rule is checked against ("The model's uncertainty" above). Host-side slices (`--slice I/N`)
are positional: slice i is equal-cost block i of N even when an earlier block is empty (one row tile costing more
than a slice's share; R3-7), in `spp_common.h` `sliceRange` and `cycle_model.py` `slice_range` alike.

## Tests

**CPU (`tools/sptest.py`: 110 checks with `--spbits`, all pass on aifoundry3 with M1's code, 29 September;
~15 s at 2 threads; with M4's code, 107 of 107 without `--spbits` on aifoundry3, 29 September, 05:33 PDT, and again
after R3's fixes, 07:13 PDT):**
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
- **planbig:** the showcase plans on 32 × 32 minions: coverage, cut error ≤ 1 tile, imbalance < 1.01; under M1's
  cost and (M4) the fitted pipeline's (L1 1.0010, L2 1.0016, (256,5) and L5 1.0001). The **plan** group's planner now
  cuts by the fitted cost by default: the same checks pass.
- **base:** `vexh` = the reference (answer, ties, both checksums = closed forms) on 9 sizes; `mitm` with and without
  the halving finds the reference's answer; two-stage survivors and stage 2 = the reference; `batch` with 8
  instances per register and one per thread solves exactly what the reference solves (η = 0.1 and 0.3, with
  padding lanes).

**Host model (`spp_selftest`):** ranks, the J0 runs and sp.h's row count; both closed forms = brute force on 9
sizes up to k = 6; plans on 4 shire masks × 3 minion counts × 2 rounds: every tile once, candidates = C(n,k), the
plan-order oracle and the merged per-minion oracles = brute force (tie flag included); the tie rule within one and
across merged accumulators. M4: the same plan checks with the fitted cost; the C++ pipeline model = `cycle_model.py
table` on 10 entries (L1, L2 and C1; M1's kernel, M4's, and 3 A buffers) to 0.1%; at L1 on 32 × 32 minions,
simulated, M1's plan runs 207.0 ms at max/mean 1.549 (M3 measured 204 ms, 1.56-1.63 max/median) and the fitted plan
134.0 ms at 1.002 with M1's kernel, 83.7 ms at 1.003 with M4's. R3: host-side slices are positional (each slice is
equal-cost block i, for N from 2 to 4x the row tiles, where empty blocks keep their place), with M1's and the
fitted cost. All pass on aifoundry3 with M4's code after R3's fixes.

**R3's own checks, rerun on the fixed sources** (CPU only; the programs and logs are in
[`data/2026-09-29-aifoundry3-sysemu-m4r/checks/`](data/2026-09-29-aifoundry3-sysemu-m4r/README.md)): coverage, with
the host's new `sliceRange` (1,158,066 plans and the L geometries on 32 x 32 and 1 x 32 minions, sliced 1-16: every
tile once, candidates = C(n,k); the incremental generation = `rowBits` on every tile start): COVERAGE PASS; the model
over 153,600 configurations: none stops early (887 did before the fix, all past 1.1e10 cycles); the hart-0 schedules
against the PRM's wait rules: 5,390 pass (the kernel's code is unchanged). `card_run.sh m4`'s gate, speed ratio and
deferred offline oracle, run against a test double of the host (no device, no lock): a slow gate skips the whole
(256,5) and the run ends DONE; a disagreeing offline oracle stops it; a resume keeps the gates only in the same
`--out`.

**M5 after R4's fixes, 29 September on aifoundry3** (`build/sparseparity-t`, kernel `.text` `3e14be32…`, the same
as M5's; [`data/2026-09-29-aifoundry3-sysemu-r4/`](data/2026-09-29-aifoundry3-sysemu-r4/README.md)): the host now
poisons the logs before each launch, allocates its copy after `--dry`, reports `host_cpu_s` and has the two controls.
`sysemu_check.sh --only '^(ts-|c0-tensor$|reps2$|neg-mask$|s4-tensor-m1$)'`, **23 of 23 as expected** (11:08–11:21
PDT): the 17 two-stage cases, the survivors again equal to `spref`'s byte for byte (989, 7,881, 624, 4,018, 138, 19,960
entries) with the poisoned log area; `ts-negtau` (FAIL: 462 found against the oracle's 624, `survivors_oracle`
MISMATCH on its minion, the survivors' own checks, both closed forms, the oracle and stage 2 exact: without the
oracle only the count, 5.7σ low here, under the 8σ flag, would have hinted at it) and `ts-lostlog` (FAIL: the entries
MISMATCH, stage 2 624 bad entries, each `0xffffffffffffffff`, the survivor oracle MISMATCH, stage 1 exact); and four
of M4's cases on the same host (`c0-tensor`, `reps2`, `neg-mask`, `s4-tensor-m1`). 0 VPURF warnings at the kernel's
PCs and no FATAL. `spp_selftest` SELFTEST PASS; `tools/sptest.py`: 107 of 107; `card_run.sh m5 --dry`: 11 steps, none
refused; `--records-out` then `--verify-records` on a two-stage `sys_emu` run (2 minions, 624 survivors): PASS in-process and
offline; after `card_run.sh`'s packing (the gzipped log, its headers alone, its sha256) the gunzipped copy matches its
sha256, the headers file is its first 64 KB, and the offline oracle passes again; one flipped c1 bit fails the
entries, the survivor oracle and stage 2 (`verify-test.txt`).

**M5 (the two-stage screen), 29 September on aifoundry3** (`build/sparseparity-s`, kernel `.text` `3e14be32…`;
[`data/2026-09-29-aifoundry3-sysemu-m5/`](data/2026-09-29-aifoundry3-sysemu-m5/README.md)): `sysemu_check.sh`, **83 of
83 cases as expected** (09:14–10:02 PDT): the 66 below, unchanged, and 17 two-stage cases (`ts-*`, the last rows of the
table), all with 0 VPURF warnings at the kernel's PCs and no FATAL; the two-stage cases rerun on the final host
(which adds the per-minion count check), 17 of 17 again. In every full-coverage `ts-*` case the host's `--surv-out`
file equals `spref scan m1= tau1= log=`'s byte for byte, and every case's in-process oracle equals the card's log entry
by entry on every minion. `spp_selftest` (SELFTEST PASS) adds: the m1-prefix of 6 instances = the instance generated
with m1; the plan-order survivor oracle, merged over two plans, = brute force's survivor set; stage 2 over those
survivors = brute force's best, and it flags corrupted entries; the screen's probabilities = `design_model.py`'s.
`tools/sptest.py`: 107 of 107.

**`sys_emu` (`sysemu_check.sh`), M4's code after R3's fixes: 66 of 66 cases as expected, on aifoundry3, 07:33–08:11
PDT on 29 September** (`build/sparseparity-h`, kernel `.text` `4c2e7bde…`;
[`data/2026-09-29-aifoundry3-sysemu-m4r/`](data/2026-09-29-aifoundry3-sysemu-m4r/README.md)). The first 52 gave the
same results before the fixes (05:36–06:06 PDT, `build/sparseparity-g`, the same `.text`;
[`data/2026-09-29-aifoundry3-sysemu-m4/`](data/2026-09-29-aifoundry3-sysemu-m4/README.md)). The 27 cases below now run
M4's kernel (the host's default) and give the results listed; the 25 cases after them add M1's kernel on the same build,
each M4 change alone, 3 A buffers, a tie with A streamed, the generation probe, and the L geometries; the last 14 are
R3's (k = 6 and k = 2 on the new paths, the mask control streamed and with 3 A buffers, S = 40, DRAM staging with 3 A
buffers and with 1 buffer, a tie across 8 minions) and the race probe on DRAM staging. Every case had 0 VPURF warnings
at the kernel's PCs and no FATAL, except `s4-nowait`, whose FATALs are all the L1 scratchpad checker's. The dumps
compare every raw 16 × 16 output tile with the CPU, masked entries included.

M1's code passed the first 27 the same way (03:36–03:51 PDT,
[`data/2026-09-29-aifoundry3-sysemu/`](data/2026-09-29-aifoundry3-sysemu/README.md)).

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
| c0-tensor-m1, s4-tensor-m1, s4-nbuf1-m1, s4-dram-m1, k4-2shires-m1 | M1's kernel on the M4 build (`--variant m1`): C0, S = 4 (2 and 1 buffers, DRAM), (40, 4) on 2 shires | PASS | PASS each; closed forms ok/ok; dump exact (9,472 / 26,880 / 225,792 entries) |
| neg-mask-m1 | M1's kernel, the mask control | NEGM | FAIL; closed forms MISMATCH/MISMATCH; oracle MISMATCH |
| c0-gen-only, s4-gen-only | the incremental generation alone (`--variant m1 --gen inc`) | PASS | PASS; closed forms ok/ok; dump exact |
| c0-epi-only, s4-epi-only | the epilogue in pieces alone (`--variant m1 --epi hide`) | PASS | PASS; closed forms ok/ok; dump exact |
| c0-dram | C0, M4, staging in DRAM | PASS | PASS; dump exact 9,472 entries |
| s4-abuf3, s4-abuf3-nbuf1, s5-abuf3-8 | 3 A buffers (S = 4, 1 and 2 staging buffers; (64, 3, 0.2, 320) S = 5 on 8 minions) | PASS | PASS each; closed forms ok/ok; dump exact (26,880 / 26,880 / 58,368); the L1 scratchpad checker silent |
| tie-str, tie-str-m1, tie-abuf3 | the tie instance at m = 256 (A streamed): M4, M1, 3 A buffers on 2 minions | TIE | PASS; unique False (the deferred rescans flag the tie as M1's immediate ones do) |
| gen-nostore | `--timing-only --gen-probe nostore`, S = 4, 2 minions | TIMING | TIMING |
| l1geo-scp, l1geo-dram, l1geo-abuf3, l1geo-m1 | L1's geometry (512, 4, 0.3, 448), S = 7: 7 row tiles on 3 minions (`plan_lgeo.txt`: the first two, with many prefix runs; two with a prefix change inside the tile; the last three, one column tile, the very last padded), M4 in the scratchpad (2 buffers) and in DRAM, 3 A buffers, and M1 | PASS | PASS each; oracle exact on all 3 minions; dump exact 32,512 entries |
| l2geo-scp1, l2geo-dram, l2geo-abuf3 | L2's geometry (512, 4, 0.4, 1850), S = 29, the same tiles: scratchpad with 1 buffer, DRAM, 3 A buffers | PASS | PASS each; oracle exact; dump exact 32,512 entries |
| k6-res, k6-str, k6-str-abuf3 | (20, 6, 0.1, m = 64 / 256): k = 6 fills the incremental generation's prefix array; A resident, streamed on 3 minions, 3 A buffers | PASS | PASS each; closed forms ok/ok; dump exact 234,240 entries |
| k2-str | (40, 2, 0.1, 300) on 2 minions: k = 2 with A streamed | PASS | PASS; closed forms ok/ok; dump exact 1,536 entries |
| negmask-str, negmask-abuf3 | the mask control at S = 4 (A streamed), with 2 and 3 A buffers | NEGM | FAIL; closed forms MISMATCH/MISMATCH; oracle MISMATCH |
| abuf3-dram, s4-dram1 | S = 4 on 2 minions: 3 A buffers with DRAM staging; DRAM staging with 1 buffer | PASS | PASS each; closed forms ok/ok; dump exact 26,880 entries |
| timing-abuf3, timing-res | `--timing-only` with 3 A buffers (S = 4, 2 minions) and resident (C0) | TIMING | TIMING |
| s40-m4, s40-abuf3 | (64, 3, 0.1, 2560): S = 40, the largest m, on 4 minions, oracle on every minion; 2 and 3 A buffers | PASS | PASS each; closed forms ok/ok; dump exact 58,368 entries |
| tie-str-8 | the m = 256 tie instance on 8 minions (the two tied candidates on two harts, A streamed) | TIE | PASS; unique False |
| probe-dram1 | `--probe narrow:6` on 4 minions, S = 4, M4's generation, DRAM staging with 1 buffer, `--oracle on` | PASS | PASS; oracle exact, all 4 minions |
| ts-c0-res | M5, variant b: C0 at m 128, m1 64 (S1 = 1, A resident), τ1 8, dumped | TS | PASS; closed forms ok/ok; dump exact; 989 survivors = `spref`'s; stage 2 solved |
| ts-res3-2shires | (40, 4, 0.1, 384), m1 192 (S1 = 3), τ1 20, 2 shires x 2 minions, dumped | TS | PASS; 7,881 survivors = `spref`'s; oracle's survivors exact on 4 minions |
| ts-s4-str, -nbuf1, -dram1, -m1gen, ts-reps2 | (48, 3, 0.1, 512), m1 256 (S1 = 4, A streamed), τ1 30: 2 and 1 staging buffers, DRAM with 1 buffer on 2 minions, M1's generation, 2 reps | TS | PASS each; 624 survivors = `spref`'s |
| ts-k5, ts-k2-m100, ts-k1 | k = 5 (m1 128), k = 2 (m1 100: not a multiple of 64), k = 1 (m1 40) | TS | PASS; 4,018 and 138 survivors = `spref`'s; k = 1 (`spref` needs k ≥ 2): 6, the oracle's |
| ts-dense8 | (64, 3, 0.2, 640), m1 320, τ1 1 on 8 minions: about half the candidates survive (every register, lane and mask) | TS | PASS; 19,960 survivors = `spref`'s |
| ts-l1geo, ts-l2geo, ts-f5geo | the L1, L2 and (256,5) geometries at m1 320, 1,152, 1,152 (τ1 30, 60, 60), 7 row tiles on 3 minions | TS | PASS; 1,581, 1,329 and 389 survivors, the oracle's on every minion; L1, L2 dumps exact |
| ts-tie | the tie instance, m1 64, τ1 8 | TSTIE | PASS; stage 2's answer not unique |
| ts-ovf | C0 two-stage with `--surv-cap 16` | TSOVF | FAIL: survivors OVERFLOW (found 989, stored 16); the stored prefix = the oracle's; closed forms, oracle, records ok |
| ts-negmask | the mask control, m1 256 | NEGM | FAIL: both closed forms and the oracle |
| ts-negtau | R4: `--perturb tau` on (48, 3, 0.1, 512), m1 256: the kernel screens at τ1 + 2 = 32 | TSNEGT | FAIL: 462 found against 624; the survivor oracle MISMATCH; closed forms, oracle, the entries' own checks and stage 2 exact |
| ts-lostlog | R4: `--perturb lostlog`, the same instance: the kernel logs into a spare area | TSLOST | FAIL: the entries, stage 2 (624 poisoned entries) and the survivor oracle MISMATCH; stage 1 exact |

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
| 7 | LOW: the epilogue runs with the tensor unit idle | **Applied in M4** (`SPP_F_EPI_HIDE`, the default; M1's order with `--epi m1`), after M3 measured 1,606 cycles per output tile: the next tile's first S−1 ops (DST = 0, TenC only) run while the epilogue does, in pieces, and type F is handled by construction (TOUCH_ALL after the TensorWait 7 that follows each DST = 1 op). Rescans are deferred to the end of the row tile, which rules out releasing the staging buffer earlier. |
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

**R3 (M4's kernel, host and planner, 29 September).** No correctness bug: the review rebuilt the sources, passed the
52 `sys_emu` cases and 13 of its own, and checked the tile walk, the incremental generation, 1.16M plans, the hart-0
schedules against the PRM's wait rules (5,390, 5 mutations caught), the disassembly and the stack. Its findings are
about the time budget, what the A/B can tell apart and the card's coverage.

| # | Finding | Status |
|---|---|---|
| 1 | MEDIUM: `m4-32s-f5-m4` passed the 4 s guard (2.93 s) only on M4's predicted constants; at M1's fitted speed its plan models 3.66 s (4.21 s with x1.15), and nothing compared a launch with its model | **Fixed, both ways R3 proposed.** The host's guard also takes the plan simulated with M1's fitted constants x1.15 while an M4 change runs on predicted constants (`model_fallback_s`; R3's alternative), and `--trust-model` drops that term. The verdict compares every launch with its model (R3's first proposal), as a gate rather than a stop, so that a slow M4 elsewhere does not end the A/B: `m4-32s-f5-m4` (with `--trust-model`) runs only after `m4-32s-f5-h0-m4` and `-h1-m4` ran within x1.3 of their model, else it is skipped with the reason; other steps print `SLOW`. Every other M4 step's guard stays under 4 s (largest 3.12 s). |
| 2 | LOW-MEDIUM: each configuration's plan is cut by its own predicted constants, so `m4` vs `a` mixes the kernel's gain with plan imbalance | **Applied:** `m4-32s-l2-m4a`, M4's kernel on the plan cut by M1's fitted constants (`--pipe-set HIDDEN=0,G_TILE=2081,G_SLICE=2108,G_K=570.3`); the README says to refit before reading balance off `m4`. |
| 3 | LOW: the race probe ran only M1's generation; DRAM staging (`fswl.ps`) with the incremental one runs nowhere in stage `m4` | **Applied:** six `m4-probe-*` steps open stage `m4` (L2 scratchpad 1 buffer, DRAM 1 and 2 buffers, 3 A buffers; C1 scratchpad and DRAM), full oracle in-process. `sys_emu` case `probe-dram1`. |
| 4 | LOW: the full-coverage M4 steps are checked by the closed forms and a sampled oracle only; the lane maxima, best and tie flag come from the new pieces | **Applied:** `card_run.sh m4` runs `--verify-records` (the full oracle, no device) on `m4-32s-{l1,l2}-{m4,m4d}` and `m4-32s-f5-m4` at the end of the stage, and stops if one disagrees. |
| 5 | LOW: under `--cost fit`, `model_m1_s` was the plan's fitted cost, not M1's model | **Fixed:** `model_m1_s` is always M1's model; `model_plan_s` is the plan's own cost (both still in the guard). |
| 6 | LOW: with 3 A buffers a last op (DST = 1) can be followed by the next tile's first op with no TensorWait 7, a sequence M1 never issued on silicon | Documented (the kernel's `tile_abuf3` and "M4 on a card"): if `m4d` alone mismatches, try `t_wait(7)` after every last op. |
| 7 | NIT: `sliceRange` indexed only non-empty blocks, so an empty block renumbered the later slices | **Fixed:** slices are positional (`spp_common.h` `cutBlocks` / `sliceRange`, `cycle_model.py` alike); `spp_selftest` checks N up to 4x the row tiles; R3's coverage program passes with the new `sliceRange` (1,158,066 plans). |
| 8 | NIT: `pipeSimMinion` did not check that it reached the last row tile | **Fixed, and it found a bug:** with the check, 887 of R3's 153,600 configurations stopped early, all runs past 1.1e10 cycles (18 s), where a double's step exceeds the loop's epsilon and the event loop stalled (a model that understated the time). A run now ends at its end time (C++ and Python alike), 0 of 153,600 stop early, and a model that stops early throws. Nothing under 4 s was affected: the models of every step here are unchanged. |
| 9 | NIT: `nostore`'s 256 B buffer is half of hart 1's L1 lines | Documented next to `m4gen` and in the kernel: incremental minus `nostore` can understate the staged stores' cost. |
| 10 | NIT: hart 1's constants in f8-f11 and f13 are live across C code undeclared | Documented at `gen_consts` (what the generators may call; reload after anything that uses FP). |

**R4 (the board-energy tooling E and M5's two-stage screen S, 29 September).** No card-safety blocker: the review
rebuilt S (the same `.text`, `3e14be32…`), passed its 17 `ts-*` cases in `sys_emu` and `spp_selftest` on both
builds, ran two energy dry runs with the real host's plan, checked the SP's board average for unit gain on E58's
aifoundry3 bursts (1.00-1.01), the card etiquette, the ops-node-only host, the screen's maths, the kernel's compares,
indexing and erratum sequences, the survivor logs' layout and epochs, and stage 2. Its findings are about what the
measurements can claim, the reducer's and the host's robustness, and the tests' coverage; all but one (outside this
directory) are applied, in `build/sparseparity-t`.

| # | Finding | Status |
|---|---|---|
| 1 | MEDIUM: the "3-7x in the card's favour" set the card's board alone against the CPU's whole package; the host that drives the card (and, for M5, stage 2 on 6 threads) was not counted | **Fixed.** The host reports its CPU time over the burst (`host_cpu_s`, getrusage) and `energy.sh` measures the whole process's (bash `times`); the reducer bounds the host's package (10-20 W idle over the burst + 10-38.5 W per busy core-second, assumed: RAPL is root-only) and states two ratios, the card's board alone (labelled so) and the card's board plus the host's package. The README's expectation is restated both ways (at the pessimistic end the whole (256,5) is level); an M5 energy must add stage 2's threads the same way. |
| 2 | LOW-MEDIUM: `combine` summed whatever it was given (`f5h1 f5h1 l1` printed a "(256,5)" solve) and the README's glob picked up reruns | **Fixed.** `combine` refuses (exit 2) unless the parts are one instance (hash), variant and kernel and their slices are exactly 0..N-1 of one N, once each; dry and card runs cannot mix. The README names each run's directory from one start time. Tested: the valid pair, and three refusals. |
| 3 | LOW-MEDIUM: the catalogue method's single-run aliasing (±5-6%) was as wide as the TRUTH tolerance, so TRUTH PASS could not tell a -5.8% error from a correct reducer | **Fixed, and it found more.** The headline is the SP's board average (no aliasing). A second test card (finding 10) showed that its ramp baseline, which the dry runs had validated, reads 4.3-4.6% high when the die has fast thermal stages (`11-thermal-model.md`): the headline now corrects the leakage with the catalogue's law on the measured die temperature (-2.8% to +1.5% on both cards; claimed ±3%). Every TRUTH tolerance is now the claim: headline ±3%, total ±2%, catalogue 3% + one pass per reading at idle beyond the expected number and one more, rails -2..+7%, unmetered ±15%, edges 10 ms. |
| 4 | LOW-MEDIUM: the survivor log was never cleared and its entries carry no epoch: stale identical entries in DRAM (a rerun, `--from`) would pass every check, and `sys_emu` (0xDEADBEEF) cannot show it | **Fixed as proposed, per launch:** the host fills the whole log area with all-ones before every launch (outside the timed launch; the budget rule counts it); an unwritten entry fails the entries, stage 2 and the oracle. `--perturb lostlog` (the kernel logs elsewhere) shows it: `sys_emu` `ts-lostlog` and card step `m5-lostlog`. |
| 5 | LOW: nothing on the card showed that the survivor checks catch a missed survivor (`m5-negmask` does not change the survivor set); off the sampled minions the checks are self-consistency and counts | **Fixed as proposed:** `--perturb tau` (the kernel gets τ1 + 2, the host checks τ1) in `sys_emu` (`ts-negtau`) and on the card (`m5-negtau`, full oracle in-process): the survivor oracle must say MISMATCH. A whole-instance S2 on 1,024 minions is printed PROVISIONAL until the full oracle offline passes at the end of the stage. |
| 6 | LOW: the energy runs are the first card runs with `--reps` > 1; L1 is 44 launches at 7.3 per second, and aifoundry2's Master Minion hang came in a stream of short kernels | **Applied:** the commands run a 3-launch smoke run (`l2 --reps 3`) and `l2` (14) before `l1`; `energy.sh` says so. |
| 7 | LOW: `energy.sh` did not refuse aifoundry2, and `--dry --real-plan` ran the real host without `nice` | **Fixed:** refused on aifoundry2 (non-dry or `--real-plan`) unless `SPP_ALLOW_AIFOUNDRY2=1`; the plan step and the reduction run at `nice -n 19`. |
| 8 | LOW, lab-wide: `ps` truncates `sparseparity_host` to `sparseparity_ho`, which `tools/claims-v3/lib.sh:57`, `dv2/z2.sh:37` and `dv2lib.sh`'s `DEV_COMM` (`_host$`) never match | **Not applied here** (outside this directory; `energy.sh` already matches `^sparseparity_ho`): for the owner's session, add `^sparseparity_ho` to those patterns. The card lock and `et-who`'s node holders still protect the card. |
| 9 | LOW: the CPU baselines in the reducer (0.459 s, 1.58 s) were the two-stage screens at P(loss) 6.2e-4 | **Fixed:** the reducer lists each CPU method with its P(loss) and takes the fastest at ≤ 1e-4: L1 0.148 s (the meet in the middle), L2 0.508 s, (256,5) 1.769 s (the screens at m1 1,152). |
| 10 | LOW: the dry TRUTH check was circular (the stub's leakage law, filters, tau and launch edges were the reducer's own); the stub's SP pass was 0.25 s; 20 Hz only lengthens the pass | **Fixed:** the base card is called a plumbing test; `--stub-card alt` breaks each assumption (another leakage law, `11-thermal-model.md`'s thermal chain, the board average's gain 1.01 and tau 0.8 s, the rails' tau 1.3 s, `board_w` a pass late, the die idling on the other side of a half degree, the card's edges 5 / 3 ms inside the host's marks); the SP pass is E58's (0.255 s at 10 Hz, 0.296 s at 20 Hz); `energy.sh` samples at 10 Hz. |
| 11 | LOW: the host allocated its survivor copy before `--dry`'s return (up to 3 GiB zero-filled by a dry plan), and allowed 3 GB of logs on a card | **Fixed:** allocated after the return; at most 512 MB on a card (the largest step takes 108 MB), 3 GB in `sys_emu`. |
| 12 | LOW: each `FILE.surv` holds every stored entry (about 150 MB per m5 session) | **Fixed:** `card_run.sh` gzips each after the offline oracle and writes its sha256 and its headers alone (`.surv.hdr.gz`), which are what gets committed. |
| 13 | NITS: E's report said every other workload's host opens the ops node only (`sgemm`'s opens both); the SP pass was given as 0.25 s; the host's stop message said 1.25 guard + 1.0 s for a rule of + 0.5 s | **Fixed** (the README names `pciebench`; 0.296 s at 20 Hz, 0.255 s at 10 Hz; the message states the rule). |

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
