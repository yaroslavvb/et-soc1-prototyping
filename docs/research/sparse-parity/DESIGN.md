# Sparse parity on the ET-SoC-1: design of a scalable solver

Brief SP4, 28 September 2026. It builds on three briefs: [literature.md](literature.md) (SP1), [chip.md](chip.md) (SP2)
and the CPU prototypes in [`workloads/sparseparity/proto/`](../../../workloads/sparseparity/proto/RESULTS.md) (SP3).
This is a design only: nothing here has run on a card. Every number in §1.3, §2.7 and §3 comes from
[`design_model.py`](design_model.py) (`python3 docs/research/sparse-parity/design_model.py`, standard library plus
scipy). Labels: **M** measured in this repository, **D** derived here, **A** assumed, **P** predicted.

## Amendments (29 September 2026): where the critique and the reviews supersede this document

The adversarial critique of this design (SP5) and the two reviews of its first implementation (R1: the M1 kernel and
host; R2: the CPU side and the test plan) changed the points below. Where they conflict with the rest of this file,
they hold. [`workloads/sparseparity/README.md`](../../../workloads/sparseparity/README.md) documents the code that
implements them, and each finding's status.

- **Showcase at η = 0.4.** The flagship is L2 (512, 4, 0.4, 1,850); then (256, 5, 0.4, 1,925) and the hero L5
  (512, 5, 0.4, 2,151) as a two-stage screen; L1 (512, 4, 0.3, 448) for strong scaling; C0, C1 and B1 for bring-up.
  S2 (L3) is no longer the flagship.
- **The CPU baseline is the best CPU method, measured.** A tuned AVX-512 scan (`vexh`, 8 candidates per register) is
  2.4–4.4× faster on one core than SP3's scan that §3 uses; the CPU runs its own two-stage screen; B1 runs 8
  instances per register; the meet in the middle draws a random halving of the features. §3's "vs 16 threads"
  column and its CPU energies are superseded by the README's paired table.
- **CPU energy is assumed, not measured and not bounded.** The RAPL counter is root-only on the lab hosts and the
  board lifts both package limits to 4,095 W, so no package limit bounds it (R2). The README states it at an
  assumed 125–251 W.
- **The planner** balances modelled cycles (§2.2's max of op cycles and bytes over bandwidth, plus an epilogue per
  output tile and hart 1's generation per row tile) and deals blocks round-robin across the shires (§2.5's
  contiguous equal-op ranges gave 1.3–2.3× imbalance under the same model).
- **The harts.** Hart 1 generates each row tile in its own vector registers and stages it (fswg.ps into the
  scratchpad, or fswl.ps into DRAM lines held in L2); hart 0 issues only tensor ops and the epilogue. They signal
  through L2 lines with a pause between polls, and a hart that gives up writes an abort word (§2.4, §2.5).
- **X reaches the scratchpads through `TensorLoadL2Scp`**, never through plain stores that a TensorLoad reads.
- **No early exit inside the kernel in M1–M3** (§2.8): the host slices the work into launches.
- **Rows are the (k−1)-subsets of 0..n−2** (a row whose maximum is n−1 has no candidate), as `cpu/sp.h` counts them.
- **§4.1(6)'s three negative controls exist:** a dropped tile, a duplicated tile, and one tile's staircase shifted
  (the count holds, both checksums fail).
- **Ties are detected** without a top list: each hart's record flags a second candidate at its best c.
- **§4.4's limits in code:** the host refuses a launch modelled over 4 s (`--max-kernel-s`), launches only while
  the launch's timeout ends 9 s after the process started, and sizes the harts' poll limits inside that timeout.
- **§5's M1 exit criterion** (cycles per op within 10% of 270 and 280) is measured with `--timing-only`: with the
  epilogue, the tensor unit idles about 420 cycles per op at S = 3 (R1).
- [`design_model.py`](design_model.py) now also prints the two-stage screens at two m1 per showcase size, the card
  side of the paired table.
- **M4, after the first card runs (29 September).** M3 ran L1 and L2 on 1,024 minions in 0.204 s and 0.807 s,
  2.8x §3's prediction: `workloads/sparseparity/tools/cycle_model.py`, fitted to the card's per-hart records, puts
  it on hart 1's row generation (4.8x the assumed cost), a planner that undercosts narrow row tiles (the busiest
  minion 1.55x the mean) and a 1,606-cycle epilogue per output tile with the tensor unit idle. The code now has, as
  flags beside M1's path: the plan cut by the fitted model's cost (§2.5's balance, measured instead of assumed),
  incremental row generation from a slice-major copy of X (§2.4), the epilogue in pieces between the next tile's
  first S-1 ops (R1-7, which this document deferred), and optionally 3 A buffers with one TensorWait 7 per two ops.
  The model predicts L1 86 ms and L2 403 ms on 1,024 minions; the cooperative B loads that §2.2 counts on for large m
  are still not written, and the shire's L2 (2 KB per streamed op) bounds private loads at 72 ms / 300 ms. The
  workload README's "M4" sections hold the details and the card A/B (`card_run.sh m4`).
- **§4.4's 4 s rule while M4's constants are predictions** (review R3 of M4's code): the host's guard also takes the
  plan simulated with M1's fitted constants x1.15 (the launch if M4's changes gain nothing), unless the run passes
  `--trust-model`, which `card_run.sh m4` does only for the whole (256,5) after the same kernel ran its two halves
  within x1.3 of the model. The A/B also runs the hand-off probe with M4's generation first, M4's kernel on M1's
  fitted plan (the kernel's gain apart from the plan's balance), and the full oracle offline on its full-coverage
  M4 steps.
- **M5, the two-stage screen (§2.7), after M4's card A/B.** Keeping the secret with P(loss) < 1e-4 fixes τ₁ from
  its binomial tail, and at η = 0.4 with m1 ≤ 192 (A resident) τ₁ is −12: 83% of the candidates survive, so
  "m1 = 192 also keeps A resident" (§2.7) helps only at small η (S2, η = 0.2). At L1 (η = 0.3) m1 = 192 keeps 7.2e7. §2.7's
  L2 row (m1 = 832, τ₁ = 80) keeps the secret with 0.9989, not 1 − 1e-4. The card screens at L1 m1 = 320, τ₁ = 66
  (P(loss) 8.8e-5, 3.8e5 survivors) and at L2 and (256,5) m1 = 1,152, τ₁ = 106 (8.9e-5; 2.8e6 and 8.7e6), with
  A streamed, in variant b's kernel (the best of M4's A/B): each output tile's epilogue compares the tile with τ₁ in
  the vector unit (`fltm.pi` into mask registers) and logs survivors per minion, counted and flagged when a log is
  full; stage 2 runs on 6 host threads and re-derives every logged c₁. §2.7's survivor log is per minion as designed,
  sized at 1.5x its expected share + 10σ; an overflow fails the run instead of rescanning. The workload README's "M5"
  sections hold the details, the `sys_emu` evidence and `card_run.sh m5`.

## The design in one screen

- **Problem.** Noisy sparse parity (learning sparse parities with noise). The ranges are n = 256–1,024 features,
  k = 4–5 secret bits and label noise η = 0.2–0.4, with m set to SP3's 99% sample count. The noiseless problem is not
  a many-core problem: GF(2) elimination solves n = 512 in 1.3 ms on one core (M, SP3).
- **Where the chip's cores show.** A solve needs total work W = C(n,k)·m ≥ about 10¹² subset-samples. At that size a
  kernel runs 50 ms or longer, so launch costs under 1%, and one CPU core needs 5 s or more (§1.3).
- **Algorithm.** An exhaustive correlation scan written as an int8 matrix product on ±1 bytes, run on the tensor unit
  (the "T2 split"):
  - Rows are the label times the product over a (k−1)-subset. The minion that uses them generates them.
  - Columns are the n raw features, copied once into every shire's scratchpad.
  - Each k-subset is scored exactly once, in exact int32.
- **Parallel layout.**
  - The host cuts the row tiles, taken in colex order, into 1,024 contiguous ranges of equal cost.
  - There is no traffic between shires inside the loop, and each hart writes only its own lines.
  - The host merges 2,048 records of 64 B.
- **The binding constraint is shire bandwidth, not arithmetic.** An int8 op must bring in at most about 1.1 KB per
  minion to run at the measured 270–280 cycles. Two ways keep it there:
  - **m ≤ 192:** the row operand stays in the L1 scratchpad.
  - **Larger m:** 32 minions share the column loads through cooperative tensor loads (M4). Without them, the
    baseline is predicted at about 540 cycles per op (§2.2).
- **Two-stage screen.** The card scans the first m1 samples and logs the candidates above a threshold; the host
  rescores the survivors on all m. For SP3's S2 (512, 5, 0.2, 218) this keeps the row operand resident (m1 = 192)
  and loses the secret with probability below 10⁻⁴ (§2.7).
- **Proof of coverage.** Two closed-form checksums, Σc and Σc² over all C(n,k) candidates (Krawtchouk
  polynomials, §4.1), prove on every run that each candidate was scored once and correctly.
- **Flagship prediction (P).** S2 solves in **1.8–2.0 s** on the card:
  - One i7-11700K core running the same two-stage algorithm needs 4.0 min (SP3's fit), so the card is
    **120–130× one core**.
  - The whole 16-thread host would need an assumed ~28 s, so the card is about **15× the host**.
  - Energy per solve is 90–110 J on the card against an assumed ~4 kJ on the host.
- **Milestones.** M0 CPU reference → M1 one minion → M2 one shire → M3 all 32 shires → M4 tuned tensor path →
  M5 report page (§5).

## 1. The problem and its sizes

### 1.1 What is solved

- **Instance.** Samples x_i are uniform in {0,1}ⁿ. Each label is y_i = ⊕_{j∈S} x_ij ⊕ ν_i, with ν_i ~ Bernoulli(η)
  and |S| = k. Given m samples, the solver returns S; success means the exact S, and a tie counts as a failure.
- **Score.** Candidate T scores c(T) = Σ_i (−1)^(y_i ⊕ ⊕_{j∈T} x_ij) = m − 2·(disagreements).
- **Answer.** The argmax of c(T). Ties go to the smallest colex rank, so the card and the CPU give the same answer.
- **Sample count.** m is SP3's binomial model for 99% success, which landed within 0.63–1.37× of the 20-seed
  measurement at 85 points (M, SP3).
- **Generator.** Instances come from SP3's generator. Its C and Python versions produce bit-identical output (M),
  so every card run has a CPU twin.

### 1.2 Why noisy instances

**Without noise the problem is not a compute problem**:
- With m ≥ n samples, elimination takes milliseconds (M, SP3).
- With few samples, a meet-in-the-middle hash join works. At (512, 5, m = 45) it makes 2.2 × 10⁷ lookups into a
  130,816-entry table, about 0.1 s on one core (D).
- The Sutro tiers (n ≤ 32) take microseconds (SP1).

**With noise, exact matching fails.** The statistical-query lower bound is n^Ω(k) (SP1). SP3 found the plain
correlation scan the practical method: elimination on random subsets was 6–3,200× slower. That scan is a matrix
product, which is Valiant's observation at ω = 3 (SP1), and a matrix product is what the tensor unit does. The
problem's size is set by three numbers:
- n and k set the number of candidates, C(n,k).
- η sets m ≈ 2 ln C(n,k)/(1−2η)².
- A fourth dimension, the number of independent instances, is the batch mode (§2.9).

### 1.3 Where the 1,024 minions become visible

Only 32 of the 34 shires run kernels (the others are the firmware's master and a spare), so a kernel has
**1,024 minions**, 94% of the 1,088. Each cell below gives m99, then the card time (M3 baseline, 32 shires, launch
included; P), then one CPU core (M where SP3 timed it, otherwise SP3's per-subset fit). **Bold** marks a kernel of
50 ms to 8 s: long enough that the launch is under 1%, short enough for one process under the 10 s rule.

| n | k | η = 0.1 | η = 0.2 | η = 0.3 | η = 0.4 |
|---|---|---|---|---|---|
| 256 | 4 | 84: 1.5 ms / 0.14 s | 168: 2.0 ms / 0.16 s | 404: 5.6 ms / 0.30 s | 1,666: 20 ms / 0.57 s |
| 256 | 5 | **97: 52 ms / 6.8 s** | **195: 0.15 s / 9.8 s** | **466: 0.30 s / 15.4 s** | **1,925: 1.2 s / 29 s** |
| 512 | 4 | 93: 13 ms / 2.0 s | 187: 19 ms / 2.4 s | **448: 73 ms / 4.7 s** | **1,850: 0.30 s / 9.4 s** |
| 512 | 5 | **109: 1.3 s / 3.5 min** | **218: 4.3 s / 4.8 min** | 521: 9.7 s / 11 min | 2,151: 37 s / 19 min |
| 1,024 | 4 | **102: 0.17 s / 33 s** | **205: 0.63 s / 46 s** | **492: 1.3 s / 77 s** | **2,032: 5.0 s / 2.5 min** |
| 1,024 | 5 | 120: 36 s / 1.9 h | 240: 2.2 min / 2.6 h | 575: 4.9 min / 5.9 h | 2,373: 21 min / 10 h |

For k ≤ 3, and for n ≤ 128 at any k ≤ 5, every cell is under 40 ms on the card and under 1 s on one core, so the
launch dominates. The rule of thumb is **W = C(n,k)·m ≥ 10¹²**. Past about 8 s a solve is split into several
processes (§4.4).

### 1.4 The ladder

| ID | (n, k, η, m) | Work C(n,k)·m | Role | Card time, 32 shires (P, M3 / M4) | One core |
|---|---|---|---|---|---|
| C0 | (32, 3, 0.1, 128) | 6.3 × 10⁵ | exact check: every one of the 4,960 correlations dumped; `sys_emu`, then 1 minion | launch-bound | 4 µs |
| C1 | (128, 4, 0.2, 192) | 2.1 × 10⁹ | correctness on the card, 20 seeds, row operand resident | launch-bound | 11 ms |
| L1 | (512, 4, 0.3, 448) | 1.3 × 10¹² | **strong scaling from 1 to 32 shires** (2.3 s to 73 ms) | 73 / 40 ms | 4.7 s (M) |
| L2 | (512, 4, 0.4, 1,850) = SP3's S1 | 5.2 × 10¹² | strong scaling from 2 to 32 shires; energy burst | 301 / 164 ms | 9.4 s (M) |
| L3 | (512, 5, 0.2, 218) = S2 | 6.3 × 10¹³ | **flagship**: two-stage, m1 = 192; weak scaling in 1/32 slices per shire | 1.95 / 1.81 s | 4.0 min same algorithm (4.8 min, M, one stage) |
| L4 | (1,024, 4, 0.3, 492) | 2.2 × 10¹³ | n = 1,024 | 1.26 / 0.67 s | 77 s |
| L5 | (512, 5, 0.4, 2,151) = S3 | 6.2 × 10¹⁴ | time-sliced over 3–5 processes, with early exit | 37 / 20 s | 19 min (M, slice) |
| L6 | (1,024, 5, 0.4, 2,373) = S4 | 2.2 × 10¹⁶ | 1/256 slices only (about 5 s each), extrapolated | 21 / 11 min | 10.3 h (M, slice) |
| B1 | 1,024 × (64, 4, 0.1, 64) | 4.2 × 10¹⁰ | batch: one instance per minion, vector path; weak scaling 32 instances per shire; the M1–M2 bring-up vehicle | 6–12 ms | 0.51 s |

### 1.5 Not pursued now

- **Noiseless variants.** Elimination, meet-in-the-middle and information-set decoding are all host-fast at these
  sizes (§1.2).
- **Learning by SGD.** An MLP trained by SGD, as in the Sutro "energy of learning" framing, measures the cost of
  learning rather than of solving. The tensor unit could train one, as a later project.
- **Sub-cubic matrix multiplication** (Valiant, Karppa et al., SP1). It has no practical gain at these sizes; the
  GEMM here is its ω = 3 form.

## 2. The algorithm and how it maps onto the chip

**Choice of engine** (subset-samples per minion-cycle, D from SP2's per-op costs):

| Engine | Rate | Verdict |
|---|---|---|
| Scalar | No popcount instruction: libgcc's `__popcountdi2` needs a 1/8-rate `mul`, and a shift-add fold is about 17 ops, so about 20 instructions per 64 subset-samples: ~2.4 with both harts issuing | Out |
| Vector | 8 × 32-bit lanes: about 9 instructions per 256: ~21 with both harts issuing | Bring-up, batch mode and fallback (§2.9) |
| Tensor, int8 on ±1 bytes | 16,384 per op: ~61 at 270 cycles, ~30 at the bandwidth-bound 540 | **The engine** |
| Hybrid: tensor on hart 0, vector on hart 1 | Could add ~10 | Hart 1's scan also needs ~1.3 B per cycle of shire bandwidth. Both streaming variants already use the 4 B budget (§2.2); only the resident, cooperative regime (~1.1 B per cycle) leaves room. It is an M4 experiment. |

### 2.1 The scan as an int8 GEMM (the T2 split)

**Encoding.** Bit b becomes the int8 value +1 (`0x01`) or −1 (`0xFF`). Both operands are signed (UA = UB = 0 in
`TensorIMA8A32`; PRM:7677-7760). The int32 sums are exact, and padding samples are zero bytes, so they add nothing.

**Operands.** Write a candidate as T = R ∪ {j}, where R is a (k−1)-subset with largest element p < j. Define
u_R[i] = ỹ_i·∏_{r∈R} x̃_ir and v_j[i] = x̃_ij, where ˜ marks the ±1 value. Then c(T) = Σ_i u_R[i]·v_j[i] = (UᵀV)[R, j].

**Tiles.** Each op multiplies 16 rows by 16 columns over 64 samples:
- The 16 rows are consecutive (k−1)-subsets in colex order, which sorts by the largest element first.
- The 16 columns are the features 16J … 16J+15.
- A row tile whose smallest maximum is p visits the column tiles from ⌊(p+1)/16⌋ to n/16 − 1.
- The entries with j ≤ p_R are masked in the epilogue.
- A brute-force check at (32, 3), (48, 4), (64, 3) and (32, 5) found every k-subset covered exactly once, and tile
  counts equal to the model's (D).

**Work.** Including padding the samples up to a multiple of 64, the work is 1.06–1.09× C(n,k)·m at n = 512–1,024.
At the small correctness sizes it is 1.25–1.9×.

**Why not SP3's balanced split.** SP3's split takes a = ⌊k/2⌋ and has almost no redundancy (1.001×). T2 takes
b = 1, so the column operand is the data itself:
- n·m bytes, broadcast once and never regenerated.
- Only the row operand is generated, by the minion that consumes it.

The balanced split needs both operands generated, and needs the generated columns shared across a shire to be fast.
It returns in M4, once cooperative loads work.

### 2.2 The tensor op and the byte budget

Facts of the op:
- `TensorIMA8A32` computes C[16×16] int32 += A[16×64] × B[64×16].
- A comes from the L1 scratchpad: 48 lines, 3 KB.
- B comes from the L1 scratchpad or TenB.
- C stays in TenC and is copied to f0–f31 on the last op.

Only one C tile is live, so every op needs a 1 KB A slice and a 1 KB B slice. What the lab has measured on 1,024
minions at 600 MHz:

| Operand flow | Cycles per op | Source |
|---|---|---|
| A held in the L1 scratchpad, B streamed through TenB | **270.00** | M, E39 (`05-claims.md`:460) |
| A and B loaded every op from a small shared pool (mmbench) | **280.35** | M, E37 (:446) |
| A and B loaded every op from private tiles in the shire | **511.94** (4.00 B per minion-cycle) | M, E37 (:450) |

So **an op is compute-bound only if a minion's shire traffic per op stays under about 1.1 KB**. The design follows
from that:

| Regime | Traffic per op | Cycles per op (P) |
|---|---|---|
| **m ≤ 192** (S = ⌈m/64⌉ ≤ 3): A stays in the 48 lines for all the column tiles of a row tile | B (1 KB), plus the row tile's generation write and reload spread over its ops. At S = 3 the next A cannot be double-buffered, so the reload stalls about 37 cycles per op at L3. | private B: 330 (L3); cooperative B: 307 |
| **m > 192**: A and B both stream | 2 KB, plus about 120 B of generated rows | private: **~540** (bandwidth-bound) |
| **m > 192**, with the 32 minions of a shire loading the same B lines cooperatively | 1 KB + 32 B + 120 B | cooperative: **~295** (M4) |

Cooperative loads work as follows:
- `tensor_coop` (PRM 9.2.4, 9.3.1.1) makes TensorLoads of the same lines, issued by hart 0 of the minions in a group
  across the shire's neighbourhoods, into one L2 request.
- The group must issue identical loads, so the 32 minions of a shire walk the same (column tile, sample slice)
  sequence in lockstep, each with its own row tile.
- The host therefore groups 32 row tiles that share a first column tile into one shire step (§2.5).
- M2 also tries the cheaper middle case: the same column order on every minion without `tensor_coop`, which may get
  mmbench's hot-pool rate.

### 2.3 Data layout in each shire's scratchpad

Every region starts at offset 256 KB or later, since offset 0 faults (`14-card-behaviour.md`:402).

| Region | Contents | Size at L2 (n = 512, m = 1,856) | Written by | Read by |
|---|---|---|---|---|
| X_B | The features as B tiles, one 1 KB tile per (column tile J, sample slice s), in the 4-sample interleave TensorLoad expects. The host lays them out. | n·m_pad = 0.95 MB | the shire's 32 minions, a thirty-second each, copied from DRAM at kernel start, then an FLB barrier (233 cycles) | all 32 minions, through TensorLoad into TenB |
| A staging | One row tile per minion: 16·m_pad bytes, 64 B aligned | 32 × 29.7 KB = 0.95 MB | the owning minion, with L2-direct stores | the same minion's TensorLoad |
| DRAM, cached in L2 | Bit-packed X and y (116 KB), the binomial table, the plan (each minion's first rank, first subset and last tile) | — | the host | all |
| DRAM results | One 64 B record per hart; one survivor log per minion (8 B entries) | 128 KB plus the logs | each hart its own lines | the host |

- **Budget.** The scratchpad needs m_pad·(n + 512) ≤ 2.25 MB.
  - At n = 512 this allows m ≤ 2,304, so every ladder size fits (L5 uses 2.12 MB).
  - At n = 1,024 it allows m ≤ 1,536. L6 therefore shards the columns: the shires form 2–4 groups, each holding
    one column range, and every row tile is scanned against each range by one shire of that range's group.
- **Broadcast data.** Only X (1–2 MB) and the plan (8 KB) are broadcast. Copying X into 32 scratchpads reads
  32·n·m_pad bytes from DRAM: 0.4 ms at L2 (D), under 1% of any kernel of 50 ms or more.

### 2.4 The minion loop

In M3, hart 0 does everything. Hart 1 returns at entry, as in the `sparsity` kernel's tensor modes.

```
copy my 1/32 of X_B from DRAM into the shire scratchpad; FLB barrier
R = first row tile of my range;  generate A(R) into my staging area
for each row tile R in my range:
    if S <= 3: TensorLoad A(R) into L1Scp lines 0..16S-1          # resident: once per row tile
    for J in first_col_tile(R) .. n/16-1:
        for s in 0 .. S-1:
            if S > 3: TensorLoad A(R, s) into L1Scp buffer s%2    # double-buffered with the op before
            TensorLoad B(J, s) into TenB                          # cooperative in M4
            TensorIMA8A32(first = (s == 0), to_f_regs = (s == S-1))
        epilogue(R, J)       # runs while the next tile's first ops execute
        if J is the last column tile: generate A(R+1) as the loads of A(R) retire (single staging buffer)
write my 64 B record; flush my survivor log
```

- **Row generation.** Rows are built in the bit domain first: XOR the packed columns, reusing the products that
  colex neighbours share. Each 32 bits are then expanded to 32 ±1 bytes in about 7 vector ops: broadcast, per-lane
  shift, `fmul.pi` spread, `and`, `fmul.pi` by `0xFE`, `xor` `0x01`, store. This costs 2–5% of hart 0's issue slots
  at m > 192 and up to about 20% at m = 192, k = 5. It overlaps the asynchronous tensor ops.
- **Epilogue.** It runs once per output tile on hart 0, reading f0–f31 after `fmv.x.w x0, f0` (errata 1.29, type F).
  It:
  - masks the staircase entries;
  - adds Σc and Σc² into the hart's int64 accumulators (c² ≤ 4.7 × 10⁶ and a tile's Σc² < 2³¹, so int32 lanes
    suffice inside a tile);
  - compares c against τ_log (survivor log) and τ_acc (early exit), with one branch per tile on an OR of the masks;
  - updates the hart's best.

  That is about 110 instructions per tile. They must finish before the next tile's last op overwrites f0–f31, which
  is S × 270+ cycles away: easy for S ≥ 2 and tight at S = 1 (m ≤ 64).

### 2.5 Partition over shires, minions and harts

- **Unit of work: the row tile.** A tile is 16 consecutive (k−1)-subsets in colex order. Its cost is
  (n/16 − ⌊(p_min+1)/16⌋)·S ops. The cost is constant within each p, so its prefix sum has a closed form.
- **Minions.** The host planner cuts the sequence into 1,024 contiguous ranges of equal cost. Contiguity keeps colex
  neighbours on one minion, which makes generation incremental. The imbalance is at most one row tile (≤ 32·S ops,
  about 1 ms at S = 34), under 1% for kernels of 100 ms or more.
- **Shires.** Shire s takes the ranges of minions 32s … 32s+31, numbered as in `sgemm` (the popcount of the mask
  below the shire).
  - **Strong scaling:** the same plan cut for 1 … 32 shires.
  - **Weak scaling:** the first s/32 of the cost on s shires.
- **Cooperative variant (M4).** A shire step becomes 32 row tiles that share the first column tile ⌊(p_min+1)/16⌋.
  Even the first block (p < 16, k = 4) has about 35 row tiles (D). Partial groups are padded with masked
  dummy rows, and the host balances the steps across shires by cost.
- **Harts.**
  - Hart 0 does the tensor ops, the generation and the epilogue.
  - Hart 1 is idle in M3. In M4 it becomes the vector hybrid or the on-chip stage 2, if M2 shows spare shire
    bandwidth.
- **No shared-line writes.**
  - X_B is written once, in disjoint 1 KB tiles, before a barrier.
  - The A staging areas are private.
  - Each hart owns one 64 B record, and each minion owns its log.
  - Nothing a minion writes in the loop is read by another minion.

### 2.6 Reduction and output

Each hart's record holds:
- its best (c, row rank, j), plus a top-8;
- Σc and Σc² as int64;
- ops done, survivors logged and overflowed;
- `hpmcounter3` at entry and exit, corrected with `fixcyc()`.

The host reads 2,048 × 64 B, about 20 µs, and the logs. It merges them, takes the argmax, and checks both checksums
(§4.1). The on-chip TensorReduce (444 cycles per shire, 1,393 across the chip; M) is not needed. It is an option if
a later variant keeps many instances on the card.

### 2.7 The two-stage screen

The card scans only the first m1 samples and logs candidates with c₁ ≥ τ₁. The host rescores the survivors on all
m samples and takes the argmax. The secret is lost only when it falls under τ₁: whenever it survives, it is also
the best among the survivors on all m samples, since it was the best of all C(n,k). So success barely drops, and
the card's work shrinks by m1/m. m1 = 192 also keeps A resident. The table gives the card's stage 1 (P, M3 private /
M4 cooperative) against a single stage:

| Instance | m | m1 | τ₁ | P(secret kept) | E[survivors] | Stage 1 | One stage |
|---|---|---|---|---|---|---|---|
| L3 = S2 (512, 5, 0.2) | 218 | 192 | 70 | > 0.9999 | 6.9 × 10⁴ | 1.95 / 1.81 s | 4.32 / 2.37 s |
| (512, 4, 0.3) | 448 | 192 | 34 | 0.9996 | 2.4 × 10⁷ | 19 / 16 ms | 73 / 40 ms |
| L2 = S1 (512, 4, 0.4) | 1,850 | 832 | 80 | 0.9989 | 8.7 × 10⁶ | 135 / 74 ms | 301 / 164 ms |
| L5 = S3 (512, 5, 0.4) | 2,151 | 1,280 | 144 | 0.9993 | 9.1 × 10⁶ | 21.6 / 11.8 s | 36.7 / 20.1 s |
| L4 (1,024, 4, 0.3) | 492 | 256 | 58 | 0.9988 | 7.9 × 10⁶ | 0.63 / 0.34 s | 1.26 / 0.67 s |

- **Stage 2 on the host.** At most 10⁷ survivors times m subset-samples, plus an 80 MB readback: 10–30 ms (D).
- **Survivor logs.** Each is sized at 4× the minion's expected share. On overflow, that range is rescanned with a
  higher τ₁ and the run is flagged.
- **When.** S2 runs this way in M3, as the flagship; the other rows come in M4.
- **CPU comparisons use the same algorithm.** SP3's scan at 192 samples takes 4.0 min for S2, against 4.8 min for
  one stage at 218.

### 2.8 Early exit

- **Threshold.** A candidate is accepted when c ≥ τ_acc, where the union bound over all candidates caps a false
  accept at 10⁻³. At m99 the secret clears it with probability 0.93 (L1, L2, L4, L5; D). The expected scan
  fraction is then 0.54, since the secret sits at a uniform point of its minion's range. At η = 0 the rule is c = m.
- **M3: at the host.** A solve is a sequence of launches, each a slice of every minion's range lasting 50 ms or
  more, so launches cost at most 1%. The host stops when a record reports c ≥ τ_acc. This is the same slicing that
  the 10 s rule needs anyway.
- **M4: in the kernel.** The finder sets one flag line per shire, homed in different shires. Each minion reads its
  shire's line with an atomic read at the home at most once per 50 µs. That is not a spin; a spin on one global line
  stops its home shire (`17-hot-line.md`).
- **Reporting.** The primary metric is the full-scan time, which is deterministic. The distribution of early-exit
  times is secondary.

### 2.9 The vector path

The vector path serves four roles: bring-up in M1, the batch mode, the fallback, and the hart-1 hybrid.
- **The test.** A candidate scores popcount(P ⊕ x_j), where P = y ⊕ x_R, on packed bits. With no popcount
  instruction, a SWAR or carry-save count on 8 × 32-bit lanes takes about 9 instructions per 256 subset-samples. At
  m ≤ 64, four 64-bit candidates fit per register, at about 16 instructions per 256. The noiseless test is `fxor`
  followed by a `fsetm`/`maskpopc` zero check.
- **Rate.** The measured issue rate is 0.37–0.74 instructions per minion-cycle, which gives 0.6–1.3 × 10¹³
  subset-samples per second (P). That is 1.3–5× slower than the tensor path at L2–L4 (§3).
- **B1.** Each minion runs one (64, 4, 0.1, 64) instance, whose packed X is 512 B, one hart's L1. Both harts split
  the prefixes. The prediction is 6–12 ms for 1,024 instances, against 0.51 s on one core and about 60 ms on 16
  threads (A): 0.27–0.47 mJ per instance.

### 2.10 Traps that shape the code (from SP2)

- **Vector hazard (errata 1.29).** Put ≥ 8 instructions between a vector write and its read, and a `fmv.x.w x0, f0`
  after TenC reaches f0–f31. GCC inserts neither. Check with `sys_emu -vpurf_warn`, filtered to the kernel's PCs.
- **Missing arithmetic.** There is no `double`, no `fcvt.s.lu`, and no packed-unit integer divide in U-mode. Keep
  checksums as integers.
- **Memory visibility.** L1 is not coherent. Data that another agent's TensorLoad will read must go out with
  L2-direct or tensor stores.
- **Tensor ops** issue from hart 0 only.
- **`hpmcounter3`** reads 128 short; correct it with `fixcyc()`.
- **Synchronisation.** Never spin on a global atomic.

## 3. Predictions: one card, 600 MHz, 32 shires

| | One core | 16 threads (A) | Card, M3 (cycles/op, time) | Card, M4 | vs 1 core | vs 16 threads | Board W (M3 / M4) | J per solve | J over idle | 16 threads, J (A) |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 4.7 s (M) | 0.55 s | 542, 73 ms | 294, 40 ms | 64–118× | 7.6–14× | 51 / 56 | 3.7 / 2.3 | 1.1 / 0.8 | 83 |
| L2 = S1 | 9.4 s (M) | 1.1 s | 542, 301 ms | 294, 164 ms | 31–57× | 3.7–6.8× | 51 / 56 | 15 / 9.2 | 4.5 / 3.3 | 166 |
| L3 = S2, two-stage | 4.0 min | 28 s | 330, 1.95 s | 307, 1.81 s | 122–132× | 14–16× | 56 / 50 | 108 / 90 | 38 / 25 | 4,200 |
| L4 | 77 s | 9.0 s | 528, 1.26 s | 280, 0.67 s | 61–114× | 7–13× | 51 / 57 | 64 / 38 | 19 / 14 | 1,350 |
| L5 = S3 | 18.8 min (M) | 2.2 min | 549, 37 s | 301, 20 s | 31–56× | 3.6–6.6× | 51 / 56 | 1,870 / 1,120 | 549 / 399 | 20,000 |
| L6 = S4 | 10.3 h (M) | 73 min | 531, 21 min | 283, 11 min | 30–56× | 3.5–6.6× | 51 / 56 | 63 k / 37 k | 19 k / 13 k | 654 k |
| B1 (1,024 instances) | 0.51 s (M, per instance × 1,024) | 60 ms | vector path: 6–12 ms | | 43–82× | 5–10× | 40–45 | 0.28–0.48 (0.27–0.47 mJ per instance) | | 9 |

How the columns are built:
- **CPU.** One core is SP3's i7-11700K (AVX-512 `VPOPCNTQ`), measured where marked, otherwise its per-subset fit.
- **16 threads** is one core divided by an assumed 8.5 (range 7–10). Four threads measured 3.89×, and the host has
  8 cores with SMT.
- **CPU energy** assumes a 150 W package: the i7-11700K's PL1 is 125 W and PL2 251 W. It was not measured.
- **Card power.** Board power is aifoundry2's idle at 80 °C (35.9 W, M; aifoundry3 37.3 W; aifoundry1's card 1
  48.9 W, which adds 13 W × t) plus the dynamic terms:
  - 0.30 pJ per MAC (M, E38);
  - 3.7 pJ per tensor-loaded byte (D, fitted so that mmbench's int8 run reproduces its measured 27.9 W over idle);
  - 15 pJ per instruction (M range 8–20).

**What the table says.** The card beats one core by 30–130× and a whole 16-thread host by 3.5–16× (A). It is
10–47× cheaper in energy per solve than that host at its assumed power (A). The lead is largest where m is small and
the row operand stays resident (S2), and smallest at η = 0.4, where AVX-512 popcount is at its best (SP3's finding).

Strong scaling for the M3 baseline is linear by construction, apart from the fixed ~0.6–1 ms launch and copy-in:

| | 1 shire | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| L1 | 2.32 s | 1.16 s | 579 ms | 290 ms | 145 ms | 73 ms (efficiency 0.99) |
| L2 | 9.6 s | 4.8 s | 2.4 s | 1.2 s | 600 ms | 301 ms |
| L4 | 40 s | 20 s | 10 s | 5.0 s | 2.5 s | 1.26 s |

**Where the prediction can fail:**
- **Shire bandwidth under 32 private streams plus the generation stores.** It decides between 540 and 295 cycles
  per op, and M2 measures it.
- **Cooperative loads** have never been run in this repository.
- **The epilogue** is tight at S = 1.
- **The CPU columns** (16 threads and energy) are assumptions.

## 4. Verification and measurement plan

### 4.1 Correctness

1. **CPU oracle (M0).**
   - A numpy version of the T2 GEMM plus the planner, which gives the expected record of every hart for any plan.
   - For the large sizes, `spbits` extended to report per-range results.
2. **`sys_emu`.** C0 on 1 minion, then 1 shire, with `-mem_check -l1_scp_check -l2_scp_check` and `-vpurf_warn`.
3. **C0 on the card.** Dump all 4,960 correlations; they must match the CPU bit for bit.
4. **C1 and L1.** Every hart's record must equal the oracle's (best, top-8, Σc, Σc²), on 20 seeds.
5. **L2–L6.** Three checks:
   - **Two checksums over all C(n,k) candidates, both exact identities.** Write K_k(w) = Σ_t (−1)^t C(w,t) C(n−w,k−t)
     (the Krawtchouk polynomial), w_i for the weight of sample i, and d for Hamming distance. Then
     **Σ_T c(T) = Σ_i ỹ_i K_k(w_i)** and **Σ_T c(T)² = Σ_{i,i′} ỹ_i ỹ_i′ K_k(d(x_i, x_i′))**. The first costs O(m)
     on the host and the second O(m²n/64). Both were checked numerically against brute force at (12, 3, 20),
     (16, 4, 37) and (10, 5, 9).
   - The top list rescored on the host.
   - The secret recovered on at least 5 seeds per size.
6. **Negative controls (M1).** Three altered plans: one tile dropped, one duplicated, one staircase mask flipped.
   Both checksums must fail on each.

### 4.2 Performance

- **M1.** Cycles per op on one minion, resident and streamed. Cycles per 256 subset-samples on the vector path.
- **M2.** Run 1, 2, 4, 8, 16 and 32 minions in one shire to find where private streams reach 4 B per cycle. Compare
  three variants: private, same column order, and cooperative.
- **M3.**
  - Strong scaling: L1 at 1–32 shires, L2 at 2–32, L4 at 4–32.
  - Weak scaling: L3 in 1/32 slices per shire, and B1 with 32 instances per shire.
  - Two different shire masks per count. Placement should not matter, since no data crosses shires.
  - Five repeats per point, reporting the median and range.
- **Recorded with every run.** `hpmcounter3` per hart at entry and exit, host wall time from launch to wait, the
  copy-in and scan phases, ops done, `et-lab-manifest`, the clock from telemetry, and the code's sha256.

### 4.3 Energy, through the existing framework

- **Framework.** A new `tools/claims-v3/sp/` experiment (`block.sh`, `reduce.py`, and a README that fixes the rules
  before any data), run `V3_DRY=1` first, then `--smoke`, then for real.
- **Sampling.** `ettelem sample` at 10 Hz.
- **One burst:**
  1. An idle bracket.
  2. Back-to-back solves for about 7 s in one process: L1 about 90 times, L2 about 20, L3 3–4.
  3. An idle bracket.
- **Reading it.** The first 3 s of each burst are skipped: the rails lag with τ ≈ 1.2 s, and the board value
  refreshes every 133–224 ms. Every run launches at the registered die temperature (`heat_to` on a card with a free
  governor), and 600 MHz is checked in every sample.
- **Reported:** board W; W over the idle at that temperature; J per solve (mean power × solve time); J over idle.
  These are compared with the prediction registered beforehand: 51–56 W on aifoundry2's idle, 9–15 J per L2 solve.
- **M4 variant: 0/1 unsigned encoding** (UA = UB = 1, disagreements = |a| + |b| − 2⟨a,b⟩). It toggles fewer bits
  than ±1, and zero operands are gated per 32-bit word, so it may cut the MAC energy at the same speed.
- **CPU side.** Times on aifoundry1 at 1 and 4 threads; 8 and 16 threads need the owner's permission (the current
  cap is 4). Energy comes from RAPL if a user can read it; otherwise it stays marked as assumed.

### 4.4 Card etiquette, and sizing runs to fit it

- **Permission.** No card work without the owner's go-ahead and a named card.
  - aifoundry2 is off limits while its frozen validation runs.
  - aifoundry1's card 1 and aifoundry3 both hold 600 MHz. aifoundry3's demo can launch without the lock, so check
    `et-who` before and after.
- **Every process that opens the device:**
  - runs as `flock -n /run/lock/etsoc-shire<N>.lock timeout 10 …`, with the host's `--budget 8`;
  - holds kernels totalling at most 8 s;
  - releases the lock before the next process;
  - checks `et-who` before and after, and is stopped with a plain `kill` only.
- **Builds** go to `build/sparseparity-<tag>/`, never into `~/nekko` or a block's directory while a queue runs.
- **`sys_emu`** is heavy on the CPU: run it niced, with at most 2 shires, on a host that is not running a
  validation.

| Instance | Fits one process from | Otherwise |
|---|---|---|
| C0, C1, B1, L1 | 1 shire (L1: 2.3 s in M3) | — |
| L2 | 2 shires (4.8 s) | 1 shire as 2 slices |
| L3 | 8 shires (7.8 s in M3) | weak scaling; slices |
| L4 | 8 shires (5.0 s) | slices |
| L5 | never: 37 s in M3, 20 s in M4 | 5 or 3 processes with early exit |
| L6 | 1/256 slices (about 5 s each) | a full run is 11–21 min of card time: only if the owner asks |

## 5. Milestones

| | Deliverable | Exit criterion | Card time |
|---|---|---|---|
| **M0** CPU reference | T2 oracle; a C planner shared with the card host; both checksums; a `spbits screen` mode and per-range output; instance files; CPU baselines at 1 and 4 threads (8 and 16 with permission) | The oracle agrees with `spbits` on every ladder size it can run; the checksums match brute force; the planner's cuts are within one tile | 0 |
| **M1** one minion | `workloads/sparseparity/{kernel,host}` on the `sgemm`/`sparsity` template (shire mask and minions per shire, 64 B records per hart, `--sysemu`); the vector path on B1-type instances; tensor T2 on C0 and C1 | Bit-exact; cycles per op on one minion within 10% of 270 (resident) and 280 (streamed); the negative controls fail as they should | ~2 min |
| **M2** one shire | 32 minions: copy-in and barrier, the plan, per-hart records; the operand-flow variants | The bandwidth knee measured and set against §2.2; imbalance under 2%; an L1 slice exact | ~10 min |
| **M3** all shires | L1–L5 and B1; strong and weak scaling; S2 two-stage; early exit at the host; energy bursts on L2 and L3 | Efficiency ≥ 0.9 at 32 shires against 1 (L1); S2 solved in under 8 s in one process on every seed tried; a table of measured against predicted | ~30 min |
| **M4** tuned tensor path | Cooperative B loads; two-stage for L2 and L5; the balanced split for k = 5; ±1 against 0/1 energy; early exit in the kernel; the hart-1 hybrid if M2 shows headroom | ≤ 330 cycles per op (at least 85% of the measured int8 rate) on L2 and L4, or the measured limit documented | ~30 min |
| **M5** report page | A page in the repository's style, with data under `docs/reports/data/<date>-sparseparity-<host>/`; entries in 02, 03, 04, 05 and MIRROR.md; a private space first, with visibility the owner's decision | Builds cleanly and passes `check_page.sh` | 0 |

M1–M4 all run under §4.4. M3 and M4 go through `tools/claims-v3`.

## 6. Open questions

- **Cooperative loads.** Whether `tensor_coop` holds lockstep across 32 minions without hangs is unknown. Try it
  first in `sys_emu`, then on 1 neighbourhood, then on 1 shire.
- **Shire bandwidth with stores in flight.** The 4.00 B per cycle came from private streaming without concurrent
  stores. Generation stores add 5–10%.
- **B streamed from the scratchpad.** E39's 270 cycles had B hot. Distinct B tiles need 3.8 B per cycle, just under
  the private limit.
- **Card and publication.** Which card to use, and whether a page is published, are the owner's decisions.

## 7. Files

- **This file,** plus [`design_model.py`](design_model.py), which regenerates §1.3, §2.7 and §3.
- **The earlier briefs:** SP1's [literature.md](literature.md) and [estimate_ops.py](estimate_ops.py), SP2's
  [chip.md](chip.md), and SP3's [`workloads/sparseparity/proto/`](../../../workloads/sparseparity/proto/RESULTS.md).
- **Planned:** `workloads/sparseparity/{CMakeLists.txt,kernel/,host/,planner/,README.md,run_lab.sh}` and
  `tools/claims-v3/sp/`.
