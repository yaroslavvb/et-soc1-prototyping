# mnistmlp: one pass over MNIST in int8 on an ET-SoC-1 card (E202's program)

**What it is.** A device kernel and its host that run an int8 multilayer perceptron, **784 -> 1792 -> 1792 -> 1792 ->
1792 -> 10** (ReLU, biases), over the 60,000-image MNIST training split on every working minion of a card, check every
label and checksum bit for bit against a numpy model of the kernel's integer arithmetic, and report the cycle counter's
seconds. It answers the owner's step 6, "one pass over MNIST in int8", from his private checkpoint of Wed 11 Nov 2026
(no number from it is in this folder), on his words of Sun 15 Nov 2026:
"Make sure to incorporate suggestions from Fable when planning experiments".
The design is E202's (Q193, lane mnist-design); this folder is its build (lane mnist-kernel), answered after its
verifier (lane verify-mnist) by lane fix-mnist. **It has not run on a card.** Nothing here is a registration or a
forecast; E202's registration freezes those.

*Labels used below: **desk check of code** (exact by construction), **measured on the desk** (a CPU run on the lab
box), **simulator** (sys_emu, the functional emulator: no timing, no cache model), **REPORTED** (from a committed lab
record).*

## The work

| layer | K as issued (real) | N as issued (real) | k tiles of 64 | 16-column blocks | multiply-adds issued per image |
|---|---|---|---|---|---|
| 1 | 832 (784: 48 zero columns) | 1,792 | 13 | 112 | 1,490,944 |
| 2-4 | 1,792 | 1,792 | 28 | 112 each | 3,211,264 each |
| 5 | 1,792 | 16 (10: 6 zero columns) | 28 | 1 | 28,672 |
| **all** | | | | **449 chunks** | **11,153,408** (11,056,640 real) |

*Desk check of code.* A group of 16 images is 10,892 TensorIMA8A32 operations (one per k tile per block); a pass is
3,750 groups, 40,845,000 operations.

- **Data-parallel by image group.** Hart 0 of each working minion takes one group of 16 images at a time through all
  five layers. A **shire-round** is the P working minions of a shire each with its own group; working shire number i
  takes rounds i, i + nshires, ... of the launch's ceil(groups / P) rounds.
- **Weights through a shared staging buffer.** The P minions of a shire walk the 449 weight chunks together (a chunk =
  one 16-column block of one layer, 13 or 28 B tiles of 1 KiB). Chunk u+1 is copied into staging buffer S[(u+1) & 1]
  while chunk u is computed from S[u & 1] (u counts chunks across rounds, so the buffers alternate although 449 is odd);
  each minion copies the tiles i with i mod P = its index, with TensorLoadL2Scp. A shire barrier ends every chunk.
- **Two staging sources** (`--stage`): `scp` (the default) copies each chunk from the shire that keeps it resident: at
  launch start every shire copies its share of the weights (chunk q in the (q mod nshires)-th shire, at most 360 tiles)
  from DRAM into its resident region, then a shire barrier and one chip barrier (`workloads/onchip`'s credit-release
  shape). `dram` copies every chunk from the packed weights in DRAM (the registered fallback: TensorLoadL2Scp from DRAM
  is proven on silicon in sparsity and sparse parity; from another shire's scratchpad it is in the PRM and the
  simulator but no lab run has used it on a card).
- **The tile loop** is sparse parity's streamed-A TensorIMA8A32 loop (its M1 order, exact on silicon) with UA = 1:
  A (uint8 activations, 16 images x 64) from the minion's own buffer into L1 scratchpad lines 0-15 / 16-31, B (int8
  weights) from the staging buffer into TenB paired with the next TensorIMA8A32, int32 accumulation in TenC, the last
  operation writing C to f0..f31.
- **Between layers** (hidden layers 1-4): y = sat_u8(((acc + Bp) * M) >> 32) with `fadd.pi`, `fmulh.pi` (the upper
  32 bits of the signed 64-bit product), `fsatu8.pi` (ReLU and clamp), `fpackrepb.pi` and one masked `for.pi` per image
  row that puts columns 8-15 beside columns 0-7. **Column blocks go in pairs:** an even block's 16 x 16 bytes wait in a
  512 B slot on the hart's stack (full-width `fsw.ps`); the odd block reads each image's slot back, puts its own 16
  bytes beside it (a masked `for.pi`), and writes the image's 32 bytes into the next layer's A tile with **one unmasked
  `fswg.ps`** (tile c / 4, bytes 32 ((c / 2) mod 2) .. +31 of the image's line; the shire's explicit address, as sparse
  parity's staging stores). Rows 14-15 are spilled to the hart's stack to free f28-f31 for Bp and M.
- **The output layer:** the C tile goes to the hart's stack (`fsw.ps`), scalar code adds B and takes the first index
  of the maximum (strict `>`, numpy's argmax rule), and the group's 64 B label line (16 labels, the group number, the
  epoch, the sum of the 160 logits mod 2^32) is written with plain stores, as every lab record is.
- **Hart 1 returns at once**, as in every lab tensor kernel.

**Two changes from the design (the reasons, for the verifier):**
1. The design wrote each image row's 16 output bytes with two masked `fswg.ps`. That cannot work: erratum 1.8 ignores
   the mask of contiguous L1-bypassing stores (the lab's `workloads/enercat/kernel/enercat_gs.c` header: "the mask of
   contiguous L1-bypassing stores is ignored"), and the simulator, which models stepping A0, ignores `fswg.ps`'s mask too
   (`insn_fswg_ps`: "fswg.ps with m0 not all 1s is UNDEFINED behavior", the whole 32 bytes stored). Each masked store
   would have written 32 bytes over the neighbouring column block.
2. This build's first version wrote each C tile with one TensorStore (16 B rows into the A tile). In the simulator it
   stopped at layer 2's first TensorLoad of those lines: sys_emu's memory checker (on by default in every host-run
   simulation: `SysEmuOptions` `memcheck = true`) reported "FATAL EMU: [Mem-Checker] (Coherency Read Hazard)" on every
   line of the buffer. A TensorStore goes through the shire cache's coalescing buffer, which needs a drain
   (`cache_ops_cb_drain`, an ESR write) before a TensorLoad may read the line; `workloads/sparsity`'s README already
   says so. No lab kernel has drained it on a card, so the build uses whole 32-byte `fswg.ps` stores instead, the path
   sparse parity's staging proved on silicon (`fswg.ps` into the scratchpad, then TensorLoad). The pairing costs about
   50 more instructions a chunk than one TensorStore, and puts 114,688 B of `fswg.ps` a group into the own scratchpad,
   the activation-store bytes the design counted.

## The scratchpad layout (every working shire; 64-byte lines)

| lines | KiB | what |
|---|---|---|
| 0 - 4,095 | 256 | unused: offset 0 faults; every lab buffer starts 256 KiB in |
| 4,096 - 9,855 | 360 | resident weight chunks kept by this shire (scp staging) |
| 9,856 - 10,751 | 56 | staging buffers S0 and S1 (one chunk of up to 28 tiles each) |
| 10,752 - 39,423 | 1,792 | 32 minions x (P, Q): 16 images x 1,792 bytes in A-tile layout |
| 39,424 - 40,959 | 96 | spare |

The host refuses a layout that does not fit the scratchpad the device reports, and scp staging when a shire would keep
more than 360 tiles (fewer than 31 working shires).

## Files

| file | what |
|---|---|
| `mnistmlp_args.h` | the kernel's arguments, chunk table, per-minion record and label line (shared by kernel and host) |
| `kernel/mnistmlp.c` | the device kernel (no floating point, no libc, none of the 13 trapping instructions) |
| `kernel/crt.S`, `kernel/sections.ld`, `kernel/CMakeLists.txt` | as `workloads/ledger/kernel` |
| `host/main.cpp` | the host: pins, packing, the host's own reference (`--ref`), the device session, every check, one JSON result to `--out` |
| `model/fetch_mnist.sh`, `model/MNIST-SHA256SUMS` | the data recipe: fetch the public files from two mirrors, accept each only by its sha256 |
| `model/train_int8.py` | the trained-weights recipe (numpy, fixed seed, post-training quantization as the kernel computes) |
| `model/mnist_model.py` | the bit-exact numpy model; the random-weights configuration; the expected outputs; `compare-ref`; `dump-tiles` |
| `model/selftest_model.py` | the model's self-tests |
| `model/PINS-SHA256SUMS` | the sha256 of every input file the host reads (MNIST, both weights files, the expected outputs) |
| `sysemu_check.sh` | the simulator checks S0a, S0b, S0c, S0r, S1, S2, S3, S3x and S1b, each counted by `tools/counter` |
| `counts_scale.py` | the counts per group and per launch from those runs, every counted hart's tensor operations against a derivation from the code, and each planned launch's exact accounting (shire-rounds, padding groups, the busiest shire) |

## Build

```bash
cmake -S workloads/mnistmlp -B build/mnistmlp -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice cmake --build build/mnistmlp -j4
build/mnistmlp/host/mnistmlp_host --selftest      # CPU only
```

Record a kernel by its `.text` hash (`objcopy -O binary -j .text`), not its ELF's: the boxes' RISC-V GCC builds carry
different version strings.

## Data, weights and expected outputs (never commit large data)

```bash
bash workloads/mnistmlp/model/fetch_mnist.sh DATA                  # FETCH-MNIST OK
python3 -I -B workloads/mnistmlp/model/mnist_model.py make-random --train-images DATA/train-images-idx3-ubyte --out FILES/mnist-int8-random.mlpw
python3 -I -B workloads/mnistmlp/model/mnist_model.py expect --weights FILES/mnist-int8-trained.mlpw \
    --images DATA/train-images-idx3-ubyte --true-labels DATA/train-labels-idx1-ubyte \
    --out-expect FILES/expect-trained-train.mlpe --out-logits FILES/logits-trained-train.mlpl
sha256sum -c --ignore-missing workloads/mnistmlp/model/PINS-SHA256SUMS   # in each folder that holds some of the files
```

- **Trained weights** (`mnist-int8-trained.mlpw`): `model/train_int8.py`, run once on the desk inside a CPU slot.
  Float training through a BLAS is not bit-reproducible across machines or thread counts, so the program pins the
  output by sha256 and never retrains on a card's box. The file is 11,182,400 bytes; it is not committed here (the
  registration decides: commit it compressed, or carry it with the kit, by its pin).
- **Random weights** (`mnist-int8-random.mlpw`): splitmix64 bytes per layer from seed 0xE202000000000000 + layer (1..5)
  over the real rows and columns, zeros in the padding. The network's biases are 0, so each hidden layer's stored Bp
  is the folded rounding offset alone, floor(2^31 / M) (1,243; 999; 982; 946), and the output layer's B is 0. Each
  hidden layer's multiplier is M = round(255 x 2^32 / p), rounded to nearest (Python's `round`), where p is the 99.9th
  percentile of the layer's positive accumulators over the first 10,000 training images by numpy's default (linear)
  `percentile` method; the file's bytes depend on both choices (a floor, or another percentile method, gives another
  file). Regenerated anywhere and checked by its pin; never committed.
- **Expected outputs** (`expect-<config>-<split>.mlpe`, `logits-<config>-<split>.mlpl`): the model's labels, group
  checksums and raw layer-5 C tiles; integer arithmetic, so identical on any machine; regenerated on the box and
  checked by their pins.

## Running

```bash
# the host's own reference of the kernel's arithmetic on the packed tiles, against the model (no device)
mnistmlp_host --ref --ref-groups 4 --images DATA/train-images-idx3-ubyte --split train \
    --weights FILES/mnist-int8-trained.mlpw --expect FILES/expect-trained-train.mlpe \
    --expect-logits FILES/logits-trained-train.mlpl --pins FILES/PINS-SHA256SUMS --ref-out ref.mlpr --out ref.json
# simulator, a small batch (dram staging, shire 0, 2 minions, 2 groups, every logit checked)
mnistmlp_host --sysemu --stage dram --shires 0x1 --per-shire 2 --groups 2 --debug-logits ... --out result.json
# card (a registered card day only): R passes, every minion; keep the kernel's own label lines for a verifier
mnistmlp_host --card --passes 96 ... --labels-out labels.bin --out result.json
```

`--passes R` launches R x 3,750 groups (R x 625 with `--split test`); `--groups N` a small batch. One launch per
process. The result is written to `--out` (the host's own file) and repeated on stdout: a runtime line can split a
host's stdout on a real box (E191's first session), so a kit reads the file. Exit 0 only when every check passes.
`--labels-out` writes the launch's label lines 0..groups-1 as the kernel wrote them (64 B each), so that a verifier
can compare the kernel's own labels with the model directly.

**Rounds and padding** (`counts_scale.py`, desk check of code). A launch of N groups at P minions a shire has
ceil(N / P) shire-rounds; working shire i takes rounds i, i + 32, ...; in the last round the minions past group N - 1
take **padding groups** (input group 0, a whole group's work, their slot's discard line). At P = 32 on 32 shires:

| launch | groups | shire-rounds | padding groups | rounds of the busiest shire (shires that take them) |
|---|---|---|---|---|
| `--passes 1` (train) | 3,750 | 118 | 26 | 4 (22) |
| `--passes 16` | 60,000 | 1,875 | 0 | 59 (19) |
| `--passes 96` | 360,000 | 11,250 | 0 | 352 (18) |
| `--split test --passes 1` | 625 | 20 | 15 | 1 (20) |

A launch's seconds follow the busiest shire; its operations follow the group slots (3,776 at `--passes 1`: 41,128,192
TensorIMA8A32 issued, 40,845,000 of them for real groups).

**The checks** (all must pass): every working minion's record (this epoch, magic, no error flag, `tensor_error` 0,
groups = its shire's rounds, ops = groups x 10,892, barriers = groups x 449); every label line 0..groups-1 written by
this launch with its own group number, its 16 labels and checksum equal to the expected file's for input group
G mod 3,750; every padding group's discard line; with `--debug-logits` every layer-5 C tile. The result also carries
`core_status` (every check but the debug logits) and `logits_status` (the debug logits alone, `NOT CHECKED` without
`--debug-logits`): the debug path's TensorStore writes 64 B rows from register pairs, a form no lab kernel has run on
silicon, so a kit can read a logits-only failure apart from the program's own checks. The host poisons the label
lines and records before the launch, so a skipped store is seen; it zeroes the chip barrier's counter before each
launch. Card etiquette as `workloads/ledger`: the device is held only between opening the runtime and tearing it down;
a deliberately slow model of the launch (700 cycles per operation, 1,500 per chunk, at 600 MHz) refuses a launch over
`--max-kernel-s` (default 6 s); the launch's timeout is min(8 s, 2 x model + 1.5 s, the time left in `--budget`); after
a timed-out launch the stream is aborted and nothing is read back.

## Hazards handled (each cost the lab time before)

- Errata 1.29: TOUCH_ALL after the last TensorWait 7 before vector code (type F); every vector register read 8 or more
  instructions after its write, or after a taken branch (types B and C); every `flw.ps` target touched by `fmv.x.w`
  and one more instruction before use (type A). The output epilogue's asm reads the f registers only and declares no
  f-register clobber, so the compiler saves no callee-saved f register in that function's prologue (which would read
  the tensor-written registers before the TOUCH_ALL). `sys_emu -vpurf_warn` (always on in `run_counted.sh`) checks
  types B and C, not F.
- Erratum 1.8 (above). Erratum 1.23: only hart 0 reads `hpmcounter3`, four back-to-back reads, late-carry corrected.
- Offset 0 of a scratchpad faults: every region starts 256 KiB in. TensorWait 7 before a TensorLoad overwrites L1
  scratchpad lines an FMA reads; every TensorLoadB is paired with an FMA; TensorWait 2/3 before anything uses a
  TensorLoadL2Scp's lines; a `fence` after each chunk's `fswg.ps` stores, before the barrier; no TensorStore into the
  scratchpad for data read back (the coalescing buffer, above); the debug logits' TensorStore goes to DRAM, read by the
  host after the launch, with TensorWait 8 before the f registers are written again.
- Never spin on a global atomic (the chip barrier is the credit-release shape); every barrier polls FCCNB with a limit,
  and a hart that gives up records the error and ends its launch. A launch that fails in a barrier may leave a fast
  local barrier's count or a credit behind; the host's checks catch the next launch's damage, and a kit treats any
  failed launch as the end of that arm.
- No floating point (the requantization is integer), so no divide, no `fsqrt` and no 64-bit conversion; no libc
  (`-fno-tree-loop-distribute-patterns`; a local popcount instead of libgcc's).

## What has been checked (Mon 16 Nov 2026; records in `docs/reports/data/2026-11-16-q193-mnistmlp/`)

- **Measured on the desk:** the data recipe (every file equal to its pin); the trained recipe (int8 as the kernel
  computes it: **98.49% on the test split**, 99.98% on the training split; the float network the same); both
  self-tests; the host's reference of the kernel's arithmetic equal to the numpy model on 4 groups in each of 4 cases
  (trained and random weights, both splits): every label, checksum and raw layer-5 C tile.
- **Simulator** (sys_emu inside the host, on aifoundry3's CPU): nine runs of the final kernel, every one as wanted:
  dram staging with 2 minions (1 and 2 rounds; trained and random weights; every layer-5 C tile checked in two of
  them), dram staging with all 32 minions of a shire (a card's shire-round), scp staging on 32 shires with 1 minion
  each (the resident copy, the chip barrier and every chunk copied from another shire's scratchpad, every C tile
  checked), and, after the verifier, **the padding path** (S3: dram, 2 minions, one padding group, every checker; S1b:
  scp staging on 32 shires with 2 minions each, the copies split between them, one padding group) and **the
  debug-logits gate's negative control** (S3x: only the logits disagree, so `core_status` PASS and `logits_status`
  FAIL).
- **Counted** (`tools/counter`): per group at 32 minions a shire, 492,883 instructions (the classes in the data
  folder), 10,892 TensorIMA8A32, 2 x 10,892 TensorLoads of 1 KiB from the own scratchpad, 13 input tiles, 3,584
  `fswg.ps` of 32 B; every counted hart's tensor operations equal to a derivation from the code (18 of 18 harts); a
  padding group's work counts equal to a real group's; and each planned launch counted exactly (`counts_scale.py`).

## What this build has not done, and the risks a registration should name

- **No card run.** Seconds, joules and the card's own behaviour are E202's card day's.
- **coop4** (the design's REPORTED arm with cooperative B loads) is **not built**.
- The resident copy's remote TensorLoadL2Scp is checked in the simulator only; `--stage dram` is the fallback. The
  scored configuration (scp staging at 32 x 32) has not run as a whole even in the simulator (too long there); S1
  (32 x 1) and S1b (32 x 2: the copies split between minions) are the closest.
- **UA = 1** (bit 21 of the TensorIMA8A32 word: uint8 activations) has not run on silicon in this lab: every lab int8
  run on a card used signed A and B. The vendor header names bit 21 `tenb_unsigned`; sys_emu decodes it as A unsigned
  (the simulator runs agree with the model only that way: the weights hold negative bytes), the vendor's own test
  kernels pass their unsigned-A flag in that place, and this kernel follows them. A different meaning on silicon would
  fail every smoke check of both weight configurations at once (no data, nothing wrong recorded). An exact fallback
  with UA = 0 exists on paper and is **not built**: the inputs and every activation byte XOR 0x80 (as signed bytes,
  u - 128), and each hidden and output layer's bias gains 128 x its column's weight sum.
- **The debug logits** (`--debug-logits`) use a TensorStore of 64 B rows from register pairs, a form no lab kernel has
  run on silicon (lab kernels ran 32 B rows); sys_emu agrees with the kernel. `core_status` reads apart from it.
- **The trained weights** exist only by their pin (`model/PINS-SHA256SUMS`) in the lanes' scratch folders, and a retrain
  cannot reproduce them bit for bit: every expected output and forecast rests on those copies until the registration
  gives the file a durable home.
- **The simulator's timing is not the card's:** the `sync` class and the poll loops' instructions follow the simulator;
  the stack and table traffic (about 434 KB a group of scalar and vector loads and stores to DRAM addresses) has no
  cache model there (a hart has 512 B of L1 in scratchpad mode, so most of it is likely shire-L2 traffic). With scp
  staging every working shire copies chunk q from the same keeping shire at about the same time, so the copies may
  not hide behind the tile loop. A launch's length is therefore known only from the card: a registration can set each
  arm's R from the smoke's measured pass, so that every launch lasts at least the meter's 0.5 s and ends inside the
  host's 8 s launch timeout and the 10 s process rule (the host's slow model refuses over `--max-kernel-s`).
