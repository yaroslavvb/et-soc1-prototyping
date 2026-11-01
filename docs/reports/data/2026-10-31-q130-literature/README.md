# Q130(e) — the literature the blog post stands on, corrected

Desk lane `desk-lit`, Sat 31 Oct 2026 (week 44), **corrected the same day by `fix-desk-lit`** after the
lane's verifier found fourteen faults in the first pass. No card was touched for any of this, in either
pass: it is reading, fetching and arithmetic.

Every number is quoted with the sentence it comes from. Primary sources preferred: the author's own post,
the arXiv PDF (text extracted with `pdftotext -layout`, not a summary), the vendor's own API reference,
the slide deck that carries the table. Where only a secondary source exists it is marked. A handful of
figures are **derived here** from a published raw-data repository and are labelled as such; they are not
figures any paper states.

Lab-side numbers are cited **repo-relative** (`docs/findings/…`, `docs/reports/data/…`), with the line or
JSON key. The reductions and their scripts are beside this file.

---

## 0. What the first pass got wrong, and what changed

Results first, in the repo's style. Fourteen faults were raised; **thirteen are accepted and fixed here,
one is accepted as to wording and declined as to its proposed remedy, with the reason below.** One further
error, which the verifier did not catch, was found while fixing the others and is fixed too.

| # | Severity | What was wrong | What this file says instead |
|---|---|---|---|
| 1 | critical | **5.783 / 0.27 pJ per multiply-add were called "whole board"** and glossed "regulators, rails, clocks, leakage and all". They are **switching energy over idle** | "At the board, **over idle**" everywhere, the gloss deleted, and the whole-board pair (**11.579 / 6.139 pJ**) printed beside them. §6c |
| 2 | critical | The derived A100 **per-flipped-bit price (3,182 fJ)** was one slope fitted across a knee the same text said existed, with no interval and a wrong "flat to n = 8" | The **rising slope only**: **7.65 pJ ± 0.60 (fit), 5.4–9.9 pJ with the ±30% timing band**, knee at n = 4, flat beyond it within a newly computed noise control. §2, `a100-bitflips-v2.txt` |
| 3 | major | The headline band "×1.6–×1.9 of switching power" mixed **over-idle** ratios with **absolute-board** ratios | Both conventions printed per entry; the two entries that cannot be converted are labelled. §6a, `ratio-conventions.txt` |
| 4 | major | ×13.6 and ×21.4 were presented as two readings of one ratio, 57% apart, with no interval | One statement of the mechanism (**the quiet-data floor as a share**), then every ratio with its basis: ×8.6–13.6 in watts by session, ×14.7–32.9 per card in energy per MAC. §6a |
| 5 | major | Three "Dally 2022" transport constants are the **lab's own reconstruction**, not figures Dally states, and a derivation `(= 57.4 pJ / 64 b / 30 mm)` appears in no source | Dally's own stated figures separated from the reconstruction; the 57.4 derivation **withdrawn**; process and supply named. §3c |
| 6 | major | "HMMA is ~4× cheaper per MAC than an FMA", and 110/64 called "the instruction wrapper's share" | The slide's three rows as they stand, the 30 pJ overhead where it belongs, the MAC count named as **an assumption the slide does not make**, and the real amortisation factor. §3b |
| 7 | major | **8192³ attached to Horace He's 295/257 pair** — the post states no size for it | The size is dropped from that claim. §1 |
| 8 | major | The "1.8 mm vs 4.2 mm, 2.3× apart" caution **failed its own arithmetic** | Recomputed on the claims register's own per-bit·mm rates: **2.7 / 3.5 / 4.2 mm**, a 1.6× spread across three conventions. §6d |
| 9 | minor | Jarmusch's "57–60 W across precisions" was spliced onto Table VI's watts, which are a different experiment | Table VI and Table VIII in separate sentences. §5(8) |
| 10 | minor | "reproducing their 'almost 40%' from their own data" | "**lands between their stated 38% and 40%**", with the span named. §2 |
| 11 | minor | Three cited papers had no retained copy | All three PDFs retained in `src/` of the lane's handoff and every quoted figure re-checked locally. §5(6)(7)(8) |
| 12 | minor | E75's 274 fJ was quoted bare | Named as the **L2** coefficient with **[183, 366] fJ**, and L3/DRAM as bounds, not prices. §6d |
| 13 | minor | Mac home paths in the handoff | Every lab-side citation **repo-relative**. Throughout |
| 14 | minor | "An A100 pays 148 W no matter what the numbers are" | "**as little as** about 148 W, whatever the data" — a measured floor, not a decomposition. §6a |
| 15 | minor | "four numbers" in one place, "five numbers" in another | **four distinct values in five mentions**. §1 |
| — | new | **Chen 2025's NVINT4 0.34× / 0.38× were read as ratios against NVFP4.** Table 5 normalises the whole single-format group to **MXFP8 = 1×** | NVFP4 is 0.55× / 0.54× and NVINT4 0.34× / 0.38× **of MXFP8**; int4-against-fp4 is **0.62× energy**, which is the paper's own −38%. §5(7) |

**The one declined remedy (fault 1's second half).** The verifier asked for "drop the '17× below the bare
45 nm arithmetic' claim entirely". Declined, with the convention printed instead. Horowitz's 4.6 pJ is a
**dynamic (switching) energy** per operation from synthesised datapath blocks — his own figure caption says
*"Rough energy costs for various operations in 45nm 0.9V"* — with no idle and no leakage term in it. So the
like-for-like ET-SoC-1 side is the **over-idle** figure, not the whole-board one, and on that convention
0.27 pJ really is 17× below 4.6 pJ. What was wrong was calling 5.783 pJ "the whole board … leakage and
all". Both conventions are now printed together (§6c), with the explicit note that the claim **is true over
idle and false whole-board**, so a writer cannot pick one up without its basis. Everything else the
verifier raised is fixed as asked.

Also recorded: two of the first pass's own open issues are now **closed**, and one was wrong.
- Lucas & Juurlink's 155–257 W was re-fetched from the repository record and reads, in the authors' own
  abstract, *"the power consumption of one kernel varies between 155 and 257 Watt depending on the
  processed values"*. Closed as to the figure; the GPU and the kernel are still unnamed there, and the
  postprint PDF is behind a challenge page.
- Horowitz's **0.9 V is in the paper**: Figure 1.1.9's caption reads *"Rough energy costs for various
  operations in 45nm 0.9V."* The first pass's "no voltage on the face of it" was wrong. The figure's own
  word **"rough"** is worth carrying: there is no interval on any of its eleven values.

---

## 1. Horace He's original post

**Citation.** Horace He, "Strangely, Matrix Multiplications on GPUs Run Faster When Given 'Predictable'
Data! [short]", *thonking.ai*, **29 April 2024**. <https://www.thonking.ai/p/strangely-matrix-multiplications>
(comments: `/comments`). A blog post, not a paper; no DOI, not peer reviewed.

**Hardware.** An **NVIDIA A100**, the main test part: *"The A100 GPU I'm testing this on happens to have a
power limit of 330W"* (footnote 1), while the body says *"An Nvidia A100 GPU has a power limit of 400W"* —
the two are his unit's BIOS setting and the standard TDP. Idle: *"when the GPU is fully idle, nvidia-smi
tells me that it's only pulling 88W."* An **H100** appears in the marketing-vs-real section (1.830 GHz max
clock, 528 tensor cores, 1,024 FLOP per instruction → *"989 TFLOPS"* theoretical, 700 W limit); a **B100**
is named with no measurements.

**The numbers that are in his text** — **four distinct values in five mentions**, and the only ones
quotable (see §7):

| What | Value |
|---|---|
| cuBLAS via PyTorch, 8192 × 8192 × 8192 | *"CuBLAS: 258 Teraflops"* (83% utilisation) |
| CUTLASS profiler, its default integer-initialised inputs | *"CUTLASS: 288 Teraflops."* |
| the same CUTLASS kernel bound into Python, same inputs | *"CUTLASS: 257 Teraflops."* |
| zeros | *"benchmark(zero_inputs) # 295 Teraflops."* |
| random normal | *"benchmark(randn_inputs) # 257 Teraflops."* |

So **zeros against randn is 295 / 257 = ×1.148, a 14.8% gain** — and the whole 288-vs-258 "CUTLASS is
faster than cuBLAS" result dissolves once the inputs match.

🛑 **The size of the zeros/randn pair is not stated.** 8192³ is the dimension of the cuBLAS/CUTLASS
benchmark in the first half of the post. The `zero_inputs` / `randn_inputs` snippet that carries 295 and
257 uses a bare `N`. **Do not attach 8192³ to the 14.8%** — the post does not say, and the first pass of
this file did.

**The data kinds he compared.** Nine, listed in his text, with their per-kind TFLOPS **only in an
unlabelled image**: (1) randn, (2) checkerboard (normal with zeros in a checkerboard), (3) rand (uniform),
(4) sparse (normal, a random 75% masked), (5) ternary (1, −1, 0), (6) one bit (only the 4th bit set in
every value), (7) all pies (every value π), (8) twos (every value 2), (9) zeros. "All ones" appears in his
explanation but not in the list.

**His explanation.** The cause is *"dynamic/switching power in semiconductors!"*, because *"a small amount
of power is consumed whenever a transistor switches states."* Zeros win because they *"reduce the
'flipping' of enough transistors in the chip to stay under the power limit!"* He is careful about scope:
*"Remember that the switching power is coming from every transistor in the GPU, not just the ones holding
data!"* And the conclusion he draws for the H100: *"matmuls on the H100 are primarily not compute or
bandwidth limited, they are power limited."* He hedges his own evidence: *"It's hard for me to say for
sure, since I can't count how many times each individual transistor flips."*

**Two sweeps.** A power-limit sweep from 330 W down to 100 W (the minimum): the predictable/random gap
widens as the cap tightens, then **reverses at 100 W**. A clock-limit sweep at a 200 W cap: the gap closes,
because *"both using predictable and unpredictable inputs have identical performance, as both become
completely limited by our manual clock speed limit."* Values are in charts only.

**Follow-ups and corrections.**

- **His own update, labelled "(6/25)":** NVIDIA's MLPerf submission *"largely confirms the hypothesis in
  this blog post."* Checkable at the source. NVIDIA's own write-up says *"Tensor Core throughput is
  constrained by the power available to the GPU"*, and for the 512-GPU submission: *"we improved end-to-end
  performance by redirecting power from the L2 cache memory on each H100 GPU to the streaming
  multiprocessor (SM)"*, which *"resulted in higher GPU operating frequency within the same power budget
  and improved end-to-end performance by 4%."* ([NVIDIA developer blog, MLPerf Training
  v4.0](https://developer.nvidia.com/blog/nvidia-sets-new-generative-ai-performance-and-scale-records-in-mlperf-training-v4-0))
  **4% is the size of the effect NVIDIA bought by moving power between blocks of one chip.**
- **A correction he accepted, in the comments:** Uma Kelkar's point that the power cap *"also just directly
  throttles the clock speeds"* — he called it *"a good point"*, said it probably explains the **reversal at
  100 W**, and said he would add it to the article. (See §4: the cap does not only shave power, it is read
  by the clock controller.)
- **An explanation he rejected:** caching. He argued that `randn` doing worse than `rand` points at power,
  since both have unique elements.
- **Alternatives proposed and left open:** an off-centre logic threshold or a circuit in the multiplier
  path that favours a 0 or a 1 (Kelkar); Hamming distance — *"the larger the Hamming distance, larger is
  the switching power"* (The Microprocessor Guy); Gaussian beating uniform because more values sit near
  zero (nazago).
- **No published errata or follow-up post.** Searched; none found (§7).

---

## 2. Input-dependent power in GPUs — Gregersen, Patel, Choukse (2024)

**Citation.** Theo Gregersen (U. Washington), Pratyush Patel (U. Washington), Esha Choukse (Microsoft Azure
Research – Systems), "Input-Dependent Power Usage in GPUs", **arXiv:2409.18324v1, 26 Sep 2024**; presented
at the **SC'24 Sustainable Supercomputing workshop**. <https://arxiv.org/abs/2409.18324>. Code and data:
<https://github.com/theo-gregersen/input-dependent-power-sc24>.

**It does not cite Horace He.** Its predecessors are Lucas & Juurlink 2016 (ref. [38]), Bhalachandra et al.
2022 ([39]) and Pekhimenko et al. 2016 ([45]). Horace's post (April 2024) and this paper (September 2024)
are independent results.

**Setup.** NVIDIA **A100 PCIe** (300 W TDP) on an Azure VM; **NVIDIA CUTLASS** kernels; power from **DCGM**
every **100 ms**; **2048 × 2048** matrices — *"We selected 2048 as the largest power of two that did not
consistently throttle the A100 GPU"*; 98.5% average utilisation; C zeroed; A and B share the pattern, B
transposed; 10 seeds × 10,000 iterations (20,000 for FP16-T). Four datatypes: **FP32, FP16, FP16-T (tensor
cores), INT8**. Generalised on **H100 80GB HBM3** (700 W), **Quadro RTX 6000** (260 W, 512² because it
throttled at 2048²) and **V100-SXM2** (300 W).

**Headline.** *"these variations can change the GPU power usage during GEMM by almost 40%"* (abstract);
*"GEMM input patterns can change GPU power consumption by up to 38%"* (intro). **The abstract names no
datatype.**

**The four properties, and every takeaway as the paper words them:**

| # | Property | Finding (verbatim takeaway) |
|---|---|---|
| T1 | value distribution — σ | *"Input distribution standard deviation does not significantly impact power."* |
| T2 | value distribution — mean | *"Larger input value means can reduce power for FP datatypes."* |
| T3 | number of distinct values | *"Inputs from a small set of unique values decrease power consumption."* |
| T4 | bit similarity — random flips | *"Input data with highly similar bits uses less power."* |
| T5 | least significant bits randomised | *"As more least significant bits are randomized, power increases."* |
| T6 | most significant bits randomised | *"As more of the most significant bits are randomized, power increases."* |
| T7 | datatype | *"FP16-T is the most power hungry data type."* — and it *"is the default data type in AI applications"* |
| T8 | sorting into rows | *"Sorting input values can decrease power consumption."* |
| T9 | sorted **and aligned** (B transposed) | *"Aligning sorted values decreases power even more than just sorting."* |
| T10 | sorting into columns | *"Sorting values into columns can decrease power consumption."* |
| T11 | sorting within rows | *"Intra-row sorting can decrease power, but to a lesser extent than sorting fully."* |
| T12 | sparsity | *"Matrix sparsity decreases GEMM power."* |
| T13 | sparsity **after** sorting | *"Sparsity applied to sorted matrices can actually increase power consumption"* — it peaks *"around 30 − 40% sparsity"* for FP; the two do **not** compound |
| T14 | zeroing least significant bits | *"Zeroing least significant bits can reduce power."* |
| T15 | zeroing most significant bits | *"Zeroing most significant bits can reduce power."* |

**Runtime is flat.** *"the average iteration runtime (Figure 1) was consistent to a microsecond-level; this
is expected since each experiment uses the standard cutlass kernel."* At 2048² the A100 does not throttle,
so the whole effect shows up as **power, not speed** — the complement of Horace's result, where the cap
turned power into speed.

**Mechanism — hypothesis, not measurement.** *"we hypothesize that GPU power draw depends on inputs due to
changes in the number of bitflips during computation [45], or how many bits are set [38]."* And: *"running
a GEMM with zero matrices would incur no bitflips, and thus, it likely has lower power draw."* Their §F
finds *"correlation with higher bit alignment or lower Hamming weight and decreasing average GPU power
during GEMM. However, this is not an entirely consistent trend."* **No per-flipped-bit price is measured
anywhere in the paper.**

**Their own figures are images.** The per-experiment watts are not in the text, so **this lane reduced their
published DCGM traces** (`a100_expt_results/`, 9,629 files; `POWER` column, first 500 ms trimmed as the
paper does, 10 seeds pooled). Full table: `a100-watts.txt`; script `reduce_idp.py`, beside this file. The corners:

| A100 PCIe, 2048³ CUTLASS GEMM | FP32 | FP16 | FP16-T | INT8 |
|---|---|---|---|---|
| random normal (mean 0, σ = 2¹⁰) | **289.10** | 248.27 | **297.33** | 266.27 |
| one unique value | 225.76 | 221.15 | 215.50 | 228.09 |
| 512 unique values | 298.51 | 259.63 | 298.46 | 269.89 |
| fully sorted into rows | 250.72 | 212.10 | 228.00 | 241.36 |
| no bits flipped (one value, B another) | 213.33 | 215.15 | 206.48 | 222.73 |
| all 16 (8) bits flipped | 270.26 | 219.35 | 211.24 | 228.19 |
| all mantissa / LSBs zeroed | 270.24 | 196.81 | 184.07 | 171.90 |
| all exponent / MSBs zeroed | 224.58 | 195.34 | 182.33 | 177.68 |
| **100% sparse (all zeros)** | **196.13** | 197.64 | **183.77** | 178.59 |
| busiest cell measured | 298.78 | 289.26 | 299.04 | 269.89 |
| **span, quietest ÷ busiest** | −34.4% | −32.5% | **−39.0%** | −36.3% |

Idle on the same box: **48.56 W** (their `other_expt/idle.tsv`).

🛑 **How to word the −39.0%.** It is this lane's own max-minus-min across *all* FP16-T experiment families
(299.04 W from the `8-sort-rows` 0% cell against 182.33 W from `15-bits-most-zeros`), and the busiest of
those two cells carries only 6 samples per file. The paper never states that its 38–40% is that statistic,
nor that it is FP16-T. So: **the reduction lands between their stated 38% and 40%** (−38.7% against FP16-T's
own 180-sample baseline, −39.0% against the noisier cell). It does not "reproduce" a statistic the paper
claims. The number is robust; only the identification was overclaimed.

**Two things their data shows that the paper does not state.**

1. *(derived here)* **Holding** a 4 GB matrix of ones costs the same as holding one of zeros:
   **71.87 W vs 72.37 W** against 48.56 W idle (`other_expt/ones.tsv`, `zeros.tsv`; 65,536² int8 resident
   for 300 s). Value-dependence lives in **switching**, not in retention — a clean negative control.
2. *(derived here, **corrected**)* Their `other_expt/bit_flips/` is **a Hamming ladder** — 10,000 launches
   of a kernel that XORs every byte of a 16,384² int8 matrix with a mask of *n* set low bits. Reduced
   (`a100-bitflips-v2.txt`, script `reduce_bitflips_v2.py`):

   | n set mask bits | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
   |---|---|---|---|---|---|---|---|---|---|
   | W | 224.75 | 227.03 | 229.32 | 230.74 | 232.77 | 232.63 | 232.41 | 232.14 | 231.23 |
   | over n = 0 | +0.00 | +2.28 | +4.57 | +5.99 | +8.02 | +7.88 | +7.65 | +7.39 | +6.48 |

   **The noise control the first pass never computed.** `other_expt.cu` stores through an `int8_t*`
   (`A[offset] = A[offset] ^ mask`), so for n ≥ 8 the mask truncates to `0xFF` and the conditions
   **n = 8…32 are twenty-five runs of one identical workload**: mean **231.39 W**, spread **1.90 W**,
   **sd 0.490 W**. That is the only replication this dataset offers — there is exactly one trace per n —
   and it sets the scatter on every rung. (Within-trace sd is 0.18–0.26 W, which is *not* the unit of
   replication.)

   **So the ladder gives one price, not a blended slope.** The first four steps average **+2.00 W per bit
   position** (least squares over n = 0…4: **1.975 ± 0.155 W/bit**, the error from the control sd). Past
   n = 4 the steps are **−0.14, −0.22, −0.27, −0.91 W**: zero within the control's spread. At
   2.58 × 10¹¹ flips/s per bit position (trace-length timing), the rising slope is
   **≈ 7.65 pJ per flipped bit, ±0.60 pJ from the fit and 5.4–9.9 pJ once the ±30% timing band is
   carried**. 🛑 The first pass's **0.82 W/bit and ≈3.2 pJ/flip spanned the knee and are withdrawn**: they
   are the average of a real price and a zero.

   Two things this price is not. It is a **bandwidth-bound XOR**, so it prices a flip through the whole
   load–flip–store path in HBM2, not inside an arithmetic unit. And it **saturates at n ≈ 4 of 8**: n = 4
   sits +1.38 W (2.8 control sd) above the n ≥ 8 plateau, and the marginal flip past half a byte is free.

---

## 3. Per-format energy references

### 3a. Horowitz, ISSCC 2014

**Citation.** Mark Horowitz, "1.1 Computing's energy problem (and what we can do about it)", *2014 IEEE
International Solid-State Circuits Conference (ISSCC) Digest of Technical Papers*, 10 Feb 2014, pp. 10–14.
DOI 10.1109/ISSCC.2014.6757323. Copy read: <https://gwern.net/doc/cs/hardware/2014-horowitz-2.pdf>.

**The figure's own caption**, from the PDF text: *"Figure 1.1.9: Rough energy costs for various operations
in 45nm 0.9V."* So the **45 nm and the 0.9 V are the paper's own conditions**, and the word **"rough"** is
the paper's own too: there is no interval on any of the eleven values, and none should be invented.

**What the paper's own text says** (the table itself, Figure 1.1.9, is a raster image in every copy
reachable today — see §7):

- *"the programmable nature of a processor has high energy overhead, 70pJ/instruction, vs. a few pJ for an
  operation."*
- *"the energy cost of a DRAM access (1 to 2nJ) is a couple of orders-of-magnitude higher than the cost of
  an internal cache access or functional operation (10pJ)."*
- DRAM I/O *"not only takes over 20pJ/bit, but also require static termination power"*; even fixed,
  *"the energy cost of a DRAM access will still be large (10pJ/bit, 0.6nJ/8B)"*.
- *"a cache fetch is 20pJ"*; *"FP arithmetic takes around 1/10 the energy of a simple [instruction]"*.
- The efficiency target: *"1000 MOPS/mW = 1pJ/operation."*

**The table itself, verbatim, from Bill Dally's own slide that reproduces it** (see 3b) — the canonical
form everyone cites:

| Operation | Energy (pJ) | Area (µm²) |
|---|---|---|
| 8b Add | **0.03** | 36 |
| 16b Add | **0.05** | 67 |
| 32b Add | **0.1** | 137 |
| 16b FP Add | **0.4** | 1360 |
| 32b FP Add | **0.9** | 4184 |
| 8b Mult | **0.2** | 282 |
| 32b Mult | **3.1** | 3495 |
| 16b FP Mult | **1.1** | 1640 |
| 32b FP Mult | **3.7** | 7700 |
| 32b SRAM Read (8KB) | **5** | N/A |
| 32b DRAM Read | **640** | N/A |

Dally's slide states the provenance exactly: *"Energy numbers are from Mark Horowitz 'Computing's Energy
Problem (and what we can do about it)', ISSCC 2014"*, and separately *"Area numbers are from synthesized
result using Design Compiler under TSMC 45nm tech node. FP units used DesignWare Library."* So **the
energies are Horowitz's 45 nm figures; the areas are Dally's own synthesis** — do not attribute the areas
to Horowitz.

Independently confirmed verbatim in a third source that cites Horowitz for exactly these eleven values:
Luo & Sun, "Addition is All You Need for Energy-Efficient Language Models", arXiv:2410.00907v2, Table 1 —
*"Energy cost of various arithmetic operations cited from Horowitz (2014)"*, with 0.03 / 0.1 / 0.4 / 0.9 pJ
for addition (int8, int32, fp16, fp32) and 0.2 / 3.1 / 1.1 / 3.7 pJ for multiplication.

**Derived multiply-adds at 45 nm, 0.9 V** (arithmetic only, no operand transport, no fetch, no memory):
**fp32 MAC = 3.7 + 0.9 = 4.6 pJ · fp16 MAC = 1.1 + 0.4 = 1.5 pJ · int8×int8→int32 MAC = 0.2 + 0.1 =
0.3 pJ.** What is missing from this table and cannot be filled from it: **no fp8 row, no int4 row, no fp16
SRAM row**, and the DRAM row is a *32-bit* read.

### 3b. Dally 2018: what the amortisation slide does and does not say

**Source.** Bill Dally, "Scaling of Machine Learning", *Scaled ML*, 24 March 2018.
<https://www.matroid.com/wp-content/uploads/2024/11/bill-dally-ScaledML.pdf> (text extracted locally in the lane's handoff).

- **The memory hierarchy, per word:** LPDDR DRAM (GB) **640 pJ/word** → on-chip SRAM (MB) **50 pJ/word** →
  local SRAM (KB) **5 pJ/word**. Slide title: "The Importance of Staying Local".
- **"Specialized Instructions Amortize Overhead"**, verbatim and complete — three rows and two footnotes,
  nothing else:

  | Operation | Energy** | Overhead* |
  |---|---|---|
  | HFMA | 1.5 pJ | 2000% |
  | HDP4A | 6.0 pJ | 500% |
  | HMMA | 110 pJ | 27% |

  *\*Overhead is instruction fetch, decode, and operand fetch – 30pJ.* *\*\*Energy numbers from 45nm
  process.*

🛑 **Read it carefully; the first pass did not.** The Overhead column is the fixed **30 pJ as a percentage
of the Energy column** (30/1.5 = 2000%, 30/6.0 = 500%, 30/110 = 27%). So **110 pJ is HMMA's own arithmetic
energy, not its total**, and the total per instruction is 110 + 30 = **140 pJ**.

**The slide states no MAC count and no per-MAC figure anywhere.** Any per-MAC number is therefore an
assumption laid on top of it. On the first pass's own assumption of 64 MACs per HMMA:

| | arithmetic | + 30 pJ overhead | MACs | per MAC, total |
|---|---|---|---|---|
| HFMA | 1.5 pJ | 31.5 pJ | 1 | **31.5 pJ** |
| HDP4A | 6.0 pJ | 36.0 pJ | 4 | **9.0 pJ** |
| HMMA | 110 pJ | 140 pJ | 64 *(assumed)* | **2.19 pJ** |

So the amortisation against an FMA is **14.4×**, not ~4×; the ~4× figure is HMMA against **HDP4A**
(9.0 / 2.19 = 4.1), which is not what the first pass's sentence said. And 110/64 = 1.72 pJ is HMMA's
**arithmetic** per MAC — slightly *above* HFMA's 1.5 pJ of arithmetic, which is the real point: the whole
win is the fixed overhead spread thinner. The wrapper's own share is 30/64 = **0.47 pJ per MAC**. If HMMA
is instead read as Volta's 8×8×4 (256 MACs), the total per MAC is 0.55 pJ. **State the MAC count you
assume.**

### 3c. Dally 2022: his figures, and the lab's reconstruction, kept apart

**The article.** Bill Dally, "On the Model of Computation: Point", *Communications of the ACM* 65(9),
Sept 2022. **The figures Dally states**, as the lab's own page labels them (it prints "Dally 1.9 pJ,
0.4 ns", "Dally 58 pJ, 12.3 ns", "Dally 680 pJ, 354×" beside its own recomputations):

| Dally states | Value |
|---|---|
| 2 MB tile, core at centre, 64-bit access | **1.9 pJ, 0.4 ns** |
| 256 MB block (10 × 10 mm), 64-bit access | **58 pJ, 12.3 ns** |
| average random access, and its multiple | **≈680 pJ**, random ÷ local = **354×** |
| off-chip access, 64 bits, at 10 pJ/bit | **640 pJ** |
| the square-root rule | **4× the memory = 2× the energy and 2× the time** |

🛑 **The transport constants are the lab's reconstruction, not Dally's words.** The public page
[Dally's heuristics, rebuilt with calculators](https://spacesheep.dev/@yaroslavvb/dally-heuristics)
(7 Oct 2026) computes them from `e_w = α · ½ · c · (1 + f_rep) · V²` at **c = 0.2 fF/µm, V ≈ 0.75 V,
activity α ≈ 0.5, 5-nm-class** and prints its own output: **e_w = 30.9 fJ/bit·mm, v = 2.48 mm/ns,
L_seg = 49 µm**. Those are the numbers usually quoted as "30 fJ per bit per millimetre", "2.5 mm/ns" and
"repeaters every ~50 µm". They are a model's output reconciled against Dally's stated figures, and that is
how to cite them. The first pass's parenthetical derivation **"(= 57.4 pJ ÷ 64 b ÷ 30 mm = 29.9)"** appears
in no source read here and is **withdrawn**.

The rest of the page's reconstruction, same status:

| Reconstructed | Value | Condition |
|---|---|---|
| 8 KB (64 Kb) sub-array, 64-bit access | 0.64 pJ, 300 ps | ≈10 fJ/bit; two-thirds bitlines and sense amplifiers |
| wire capacitance | 0.2 fF/µm | an input, not an output; holds from the 0.5-µm generation to the 2020s |
| integer add at 5 nm | ≈10 fJ | vs 640 pJ off-chip = 64,000× |
| 16-bit MAC at 5 nm | ≈0.16 pJ | store-vs-recompute crossover at n ≈ 4,000 |
| distance equivalents | a sub-array read = 0.33 mm; an off-chip access = 333 mm; **an integer add = 5 µm** | at the reconstructed 30 fJ/bit·mm |

"An add is worth 5 µm of wire" remains the single most useful sentence in the literature for the blog —
**as a 5-nm-class, ≈0.75 V statement.** The ET-SoC-1's mesh rail is **0.485 V** on a 7-nm-class part, so
any millimetre converted at 30 fJ/bit·mm crosses both process and supply. §6d prices the same bit on the
lab's own measured rails as well.

---

## 4. The vendor documentation: the power cap *is* a clock controller

This is the link in Horace's chain that he and his commenters argued about, and both vendors document it.

**NVIDIA, NVML.** The authoritative wording is in the (now deprecated) throttle-reason group, carried
verbatim into DCGM's field constants:

- `DCGM_CLOCKS_THROTTLE_REASON_SW_POWER_CAP` / `nvmlClocksThrottleReasonSwPowerCap`:
  **"SW Power Scaling algorithm is reducing the clocks below requested clocks."**
  ([DCGM field constants](https://docs.nvidia.com/datacenter/dcgm/3.1/dcgm-api/dcgm-api-field-constants.html))
  The renamed constant, `nvmlClocksEventReasonSwPowerCap` (0x0000000000000004LL), words it as
  **"The clocks have been optimized to ensure not to exceed currently set power limits"**
  ([NVML R550 archive](https://docs.nvidia.com/deploy/archive/R550/nvml-api/group__nvmlClocksEventReasons.html)).
- `..._HW_SLOWDOWN` (0x…08LL): **"HW Slowdown (reducing the core clocks by a factor of 2 or more) is
  engaged"**, and *"This is an indicator of:"* **"temperature being too high"**, **"External Power Brake
  Assertion is triggered (e.g. by the system power supply)"**, **"Power draw is too high and Fast Trigger
  protection is reducing the clocks"**, *"May be also reported during PState or clock change"*.
- `..._HW_POWER_BRAKE` (0x…80LL): **"HW Power Brake Slowdown (reducing the core clocks by a factor of 2 or
  more) is engaged"**, indicating *"External Power Brake Assertion being triggered"*.
- `..._SW_THERMAL` (0x…20LL): **"SW Thermal Slowdown"** — clocks optimised so *"Current GPU temperature does
  not exceed GPU Max Operating Temperature"* and the same for memory.
- `..._HW_THERMAL`: **"HW Thermal Slowdown (reducing the core clocks by a factor of 2 or more) is
  engaged"**, indicating *"temperature being too high"*.
- `nvmlClocksEventReasonApplicationsClocksSetting` (0x…02LL): *"GPU clocks are limited by current setting
  of applications clocks"* — the reason a pinned clock removes the effect (Horace's second sweep).

So NVIDIA names **two different mechanisms**: a software scaling algorithm that *reduces the clock below
the requested clock* to respect the power limit, and a hardware trigger that *halves the clock or worse*.
Horace's data-dependent speed gap is the first; his reversal at 100 W is where the first runs out of room.

**AMD, ROCm / amd-smi.** On MI300 and newer the quantity exposed is time-in-violation, not a flag:
*"`PVIOL`, representing power violations, is the percentage of time the GPU throttled due to power
(wattage) limits."* and *"`TVIOL`, representing thermal violation, is the percentage of time the GPU
throttled due to temperature limits."* The field is `per_ppt_pwr` — *"Package Power Tracking — PVIOL; power
consumption exceeds limits"* — and `per_*` is *"Percentage of sampling period spent in violation (>0% =
throttled)"*. The mechanism is stated outright: **"Throttling directly reduces GPU clock speeds to stay
within power and thermal limits, which decreases performance."** and *"Higher violation percentages mean
more time throttled, which translates to more performance loss."* On Radeon/Navi and MI100/MI200 the older
`throttle_status` bitfield says only *whether* it is throttling; it reads N/A on MI300+.
([ROCm amd-smi, gpu violations](https://rocm.docs.amd.com/projects/amdsmi/en/latest/_sources/conceptual/gpu-violations.md))
Lowering the clock ceiling is documented as a power lever: *"Lowering the SCLK maximum reduces peak power
draw, which can reduce PVIOL percentage at the cost of peak compute throughput."* The C API for the limit
itself is `amdsmi_get_power_cap_info`.

**An independent replication of the data effect, from an HPC centre, in the course of a capping study.**
Ujeniya, Eitzinger, Hager, Wellein (NHR@FAU), "Architectural Trade-offs in the Energy-Efficient Era: A
Comparative Study of power-capping NVIDIA H100 and H200", arXiv:2604.11391v2, 15 Jul 2026: *"All
experiments use random data initialization to maximize power draw. Randomly initialized data causes more
dynamic power due to more frequent transistor switching; we experimented with different array
initialization techniques like constant and random data and found **up to 100 W difference in power
draw**."* Also useful for the blog's governor section: across caps from **200 W to 700 W** in 100 W steps,
*"the memory frequency remained strictly static: 1593 MHz for the H100 and 3201 MHz for the H200"* — **only
the SM clock moves**; base/boost SM clock 1665/1980 MHz on both; the most stable performance zones are
**400 W (H100)** and **500 W (H200)**, and *"Scaling the total power cap from 200 W to 400 W yields
substantial performance gains, whereas the 500 W to 700 W"* range does little. Within-GPU variance under
5%.

---

## 5. 2020–2026 on data-dependent power in tensor cores, systolic arrays and DNN accelerators

Nine in the window, best first, plus two foundational papers from 2016 that everything above cites.

**(1) Gregersen, Patel & Choukse 2024** — §2. *Measures:* A100/H100/V100/RTX6000 board power under 15 input
patterns × 4 datatypes. *Finds:* up to 38–40%; sorting, alignment, sparsity and bit similarity all cut
power; FP16-T is the hungriest format; **runtime flat** at a size that does not throttle.

**(2) Bhalachandra, Austin, Williams & Wright 2022** — "Understanding the Impact of Input Entropy on FPU,
CPU, and GPU Power", arXiv:2212.08805, 17 Dec 2022 (LBNL/NERSC). <https://arxiv.org/abs/2212.08805>.
*Measures:* 100 DGEMMs, 16384², NERSC Proxies + cuBLAS 11.7, on an A100 (Perlmutter, 400 W limit) and 64
cores of AMD Milan. *Finds, with the sentence:* *"The average power consumed by the random case (≈398 W) is
about 67% higher than the fixed case (≈239 W)"*, and *"the performance of the random case is nearly 4%
lower (18.6 TFLOPS vs. 19.4 TFLOPS)."* They attribute the gap to the datapath: *"We estimate (159 W /
19.4 TFLOP/s) an upper bound on FPU energy of about **8pJ/FLOP**"* on a 7 nm part. Mechanism, as a
hypothesis: *"Each of the 192 input bits to each of the 3456 FP64 FMAs has a chance of flipping from one
cycle to the next."* The structural finding is the one the blog needs: *"FPU energy is tied less to the
values of a matrix and more to **how those values change from one column/row to the next**"*, and *"power
consumption increases quickly once more than about 6% of the matrix is random"*; a constant checkerboard is
as expensive as a random one because striding sees high variability either way. The CPU effect is far
smaller — ≈188 W vs ≈158 W, **19%**, and *"less than 15 pJ/FLOP using vectorized FMA instructions."*
**The strongest prior art for Horace's result, 16 months earlier, with both the power number and the 4%
speed number.** 🛑 Its 398/239 is **absolute board power**; no idle is published anywhere on the record, so
it cannot be put in an over-idle band without an assumption (§6a).

**(3) Li, Li, Chuang, Lai & Chandra 2020** — "Improving Efficiency in Neural Network Accelerator Using
Operands Hamming Distance optimization", arXiv:2002.05293, 13 Feb 2020 (Arm).
<https://arxiv.org/abs/2002.05293>. *Measures:* post-layout simulation of a systolic datapath, **8-bit
activations, 4-bit weights, 32-bit partial sums**. *Finds:* *"on average 2.85× datapath energy reduction
and up to 8.51× datapath energy reduction for certain layers"* on MobileNetV2, with accuracy degradation
*"within 1%"*. Mechanism, named: the Hamming distance of the streamed operand matrices; *"HD(W) captures
the total bit flips of streaming W and NHD(W) represents the bit flip probability."* Two methods:
post-training reordering (channel clustering + output-channel ordering, no extra hardware) and
Hamming-distance-aware training. **The cleanest demonstration that operand *order*, with the same values
and the same results, is worth 2.85× of datapath energy.**

**(4) Peltekis, Filippas, Dimitrakopoulos & Nicopoulos 2023** — "Low-Power Data Streaming in Systolic
Arrays with Bus-Invert Coding and Zero-Value Clock Gating", **MOCAST 2023**,
DOI 10.1109/MOCAST57943.2023.10176467; arXiv:2304.12691. *Measures:* a 16×16 **Bfloat16** output-stationary
systolic array, *"driven by a commercial-grade 45-nm standard-cell library"*. *Finds:* *"The switching
activity is reduced by **29%**, on average, as compared to SAs with unencoded data values"*, *"total
dynamic power savings of **9.4%**"*, data streaming itself down *"by 1%-19%"*, and per-network *"an overall
power reduction of 9.4% for ResNet50 and 6.2% for MobileNet."* Why bus-invert works on bf16 specifically:
*"when the weights are represented as Bfloat16 numbers"* the exponent bits are *"highly concentrated, while
the mantissa"* bits are not — so only the high-activity segments are encoded. Zero-value clock gating
handles ReLU's zeros. **The paper to cite for "zero-skipping and re-coding, measured, in the same place the
ET-SoC-1 gates".**

**(5) Li, Tiwari & Orshansky 2021** — "Power-Based Attacks on Spatial DNN Accelerators", *ACM J. Emerg.
Technol. Comput. Syst.*, Aug 2021; arXiv:2108.12579. *Measures:* two weight-stationary systolic arrays
(3×1 and 3×3), **general 8-bit numbers**, on a SAKURA-G FPGA, with real power traces. *Finds:* a
conventional DPA recovers the weights from **20K power measurements** on the 1D array; the 2D array
survives **460K traces** but falls to a template DPA with **40K**. *Why it matters here:* the attack only
works because the power model is right — *"We investigate Hamming distance, Hamming weight, and bit-level
power models"*, and the successful model is *"based on the Hamming distance of the register holding the MAC
result"*. The 2D array is harder *"because the 2D array intrinsically entails multiple MACs simultaneously
dependent on the same input"*. **Independent, adversarial validation that a MAC's power is a
Hamming-distance function of its operands — and that operand sharing across a 2D array blurs it, which is
the lab's sub-additivity finding (E67/E70).**

**(6) Han, Chen, Lei, Altayo Gonzalez & Hemani 2026** — "'1'-bit Count-based Sorting Unit to Reduce Link
Power in DNN Accelerators", arXiv:2601.14087v1, 20 Jan 2026 (PDF retained in the lane's handoff).
*Measures:* **8-bit** fixed-point data over **128-bit** links in a 16-PE NoC accelerator, synthesised at
**22 nm, 500 MHz**, plus post-layout LeNet-5. *Finds:* accurate popcount ordering **20.42%** link
bit-transition reduction and *"ACC-PSU reduces link-related power by **18.27%**"*; the approximate
4-bucket version keeps **19.50%** of the BT reduction for **16.48%** link power and *"achieves up to 35.4%
area reduction"*; PE-level power 4.98% / 4.58%; the sorting unit's own overhead *"is only 1.43 mW compared
to ACC-PSU's 2.28 mW"*. Single-hop only. **The 2026 state of the art for "reorder the stream, pay fewer
flips" on the wires rather than in the ALU.**

**(7) Chen et al. 2025** — "INT v.s. FP: A Comprehensive Study of Fine-Grained Low-bit Quantization
Formats", arXiv:2510.25602v1, 29 Oct 2025 (PDF retained in the lane's handoff). *Measures:* MAC +
dequantiser + fp32 accumulator cost from *"cell factors from a TSMC FinFET standard-cell library"* (node not
stated), normalised; *"We model only combinational logic; we ignore sequential elements, placement and
routing, and interconnect."* *Finds:* *"Table 5 shows that MXINT8 and NVINT4 reduce energy by **37%** and
**38%**, respectively, compared with MXFP8 and NVFP4."*

🛑 **Read Table 5's baseline correctly.** The single-format group is normalised to **MXFP8 = 1×**
throughout: MXFP8 1× / 1×, **MXINT8 0.63× energy / 0.79× area**, **NVFP4 0.55× / 0.54×**, **NVINT4 0.34× /
0.38×**; the mixed group is normalised to MXFP8+NVFP4 = 1×, with MXINT8+NVINT4 at 0.75× / 0.66×. So
NVINT4's 0.34× is **against MXFP8, not against NVFP4** — int4-against-fp4 is 0.34/0.55 = **0.62× energy**
(and 0.38/0.54 = 0.70× area), which is exactly the paper's own −38%. The first pass printed "NVFP4 1×,
NVINT4 0.34×", which overstates the int4-over-fp4 saving by 1.8×. **No absolute pJ anywhere in the paper.**
*Use for:* the format axis below fp16, which Horowitz's 2014 table does not cover at all.

**(8) Jarmusch, Graddon & Chandrasekaran 2025** — "Dissecting the NVIDIA Blackwell Architecture with
Microbenchmarks", arXiv:2507.10789v2, 21 Jul 2025 (U. Delaware; PDF retained in the lane's handoff). Two separate experiments, and the first pass spliced them:

- **Table VI**, "Power Usage (Watts)/Performance per Watt with Data Formats on the Blackwell and Hopper
  architectures", per tensor-core format via `nvidia-smi`: on a **GeForce RTX 5080 (GB203)** FP4 e2m1
  **16.753 W**, FP6 e2m3 **39.383**, FP6 e3m2 **46.723**, FP8 e4m3 **46.661**, FP8 e5m2 **46.806 W**;
  on an **H100 PCIe (GH100)** FP8 e4m3 **55.823** and e5m2 **55.786 W** (FP4 and FP6 n/a). The caption
  promises a performance-per-watt column that the table does not carry.
- **Table VIII**, a *different* experiment — Transformer inference, *"Each inference was run a hundred
  times and the metrics were averaged"* — is where the summary sentence lives: *"Hopper maintained a
  57-60W consistent power usage across precisions, indicating a stable runtime efficiency"*, against
  Blackwell *"having a more pronounced reduction in power as precision decreases, with a from 58.8W to 45W
  in FP8"*.

*Use with care:* these are short-kernel and short-inference readings on a consumer part, no clocks, no
energy-per-op, and no stated method for Table VI (§7). The qualitative claim — **Blackwell's power tracks
the format, Hopper's does not** — is the quotable part, and the two tables must not share a sentence.

**(9) Ujeniya, Eitzinger, Hager & Wellein 2026** — §4. *Measures:* H100 vs H200 across power caps 200–700 W
with DGEMM and a bandwidth benchmark. *Finds:* up to **100 W** between constant and random initialisation;
memory clock fixed across every cap; the inverse relation between memory power draw and SM frequency when
throttling. 🛑 A watt **difference**, not a ratio: it has no quiet/busy pair and no idle, so it cannot enter
either band in §6a.

**Foundational (2016), cited by all of the above:**

**(F1) Lucas & Juurlink 2016** — "ALUPower: Data Dependent Power Consumption in GPUs", **MASCOTS 2016**,
pp. 95–104, DOI 10.1109/MASCOTS.2016.21. *Finds, in the authors' own abstract, re-fetched from the
repository record:* *"Using measurements from actual GPUs, we show that the processed data values influence
the energy consumption of GPUs significantly. For example, the power consumption of one kernel varies
between 155 and 257 Watt depending on the processed values. Existing architectural simulators are not able
to model the influence of the data values on power consumption."* A ×1.66 span of **absolute** board power;
**the GPU and the kernel are not named in the abstract, and no idle is published**, so this entry is
absolute-only (§6a). The postprint PDF sits behind a challenge page; the abstract is the authors' own text.

**(F2) Pekhimenko, Bolotin, Vijaykumar, Mutlu, Mowry & Keckler 2016** — "A Case for Toggle-Aware
Compression for GPU Systems", **HPCA 2016**, pp. 188–200. *Finds:* across *"242 GPU applications and six
different compression algorithms"*, *"The total bit toggle count can increase from 20% to 2.2×"* once data
is compressed — compression trades bandwidth for flips. Their Energy Control and Metadata Consolidation
*"almost completely eliminate the 2.2× increase in bit toggle count"* in the worst workload; total-system
energy **up to 8.9%, 2.1% on average** (that last pair from secondary indexing, not the paper's own page).
*This is the paper Gregersen et al. cite as ref. [45] for the bit-flip hypothesis.*

**Thin spots in the window.** No 2020–2026 paper measures a **per-flipped-bit price inside a tensor core**
on real silicon; no 2024–2026 paper applies **Gray coding to operands** (the only Gray-code hit is a
register-file addressing patent); zero-skipping power numbers in the window are **simulated or estimated**,
not measured on silicon (e.g. 46.6% PE dynamic power from zero-activation gating at 77.4% input sparsity,
PrimeTime PX, in a 2022 spiking-accelerator paper; 1.18–2.94× from weight gating on a 14 nm library in a
2025 Nature Sci. Rep. paper). **The ET-SoC-1 work (E60, E64–E68, E75, E78–E80) occupies exactly those three
gaps.**

---

## 6. How the literature compares with the ET-SoC-1 measurements

### 6a. The size of the data effect — and the two conventions it can be stated in

🛑 **A ratio of switching power over idle and a ratio of absolute board power are different numbers.** The
first pass put both in one band. Here every entry carries both where an idle figure exists, and says so
where it does not. Recomputed by `compare_conventions.py` → `ratio-conventions.txt`.

| System | What varied | over idle | absolute board | idle |
|---|---|---|---|---|
| **ET-SoC-1 fp32** | zeros → random normal (21 Sep session) | **×13.6** | ×1.66 | 36.29 W |
| **ET-SoC-1 fp32** | the same, on the E67-session anchors | **×8.6** | ×1.89 | 24.60 W |
| A100 PCIe FP32 | zeros → random normal | ×1.63 | ×1.47 | 48.56 W |
| A100 PCIe FP16 | zeros → random normal | ×1.34 | ×1.26 | 48.56 W |
| A100 PCIe FP16-T | zeros → random normal | ×1.84 | ×1.62 | 48.56 W |
| A100 PCIe INT8 | zeros → random normal | ×1.67 | ×1.49 | 48.56 W |
| A100 PCIe, 4 formats | quietest → busiest cell | **×1.64 – ×1.87** | ×1.48 – ×1.64 | 48.56 W |
| A100 (Perlmutter) | fixed → random, FP64 DGEMM | ×1.84 *at an assumed 50 W idle* | **×1.665** | not published |
| GPU unnamed (Lucas) | one kernel, values varied | **not convertible** | **×1.658** | not published |
| H100 / H200 (Ujeniya) | constant → random | a **+100 W difference**, no ratio | — | not published |

Sources: ET-SoC-1 `docs/findings/10-data-dependent-power.md` lines 27, 40, 42 (zeros 38.29 W, randn
63.40 W, idle 36.29 ± 0.06) and `docs/reports/data/2026-10-27-chain-closure/README.md`'s term table
(27.83 / 52.49 W over a 24.60 W idle); A100 derived here; the rest as cited in §5.

**So state the mechanism, not the ratio.** The convention-robust form is the **quiet-data floor as a share
of each machine's own busiest switching**:

| | quietest data costs | of a busiest-data switching budget of | share |
|---|---|---|---|
| A100 FP32 | 147.6 W | 240.5 W | **61%** |
| A100 FP16 | 149.1 W | 199.7 W | **75%** |
| A100 FP16-T | 135.2 W | 248.8 W | **54%** |
| A100 INT8 | 130.0 W | 217.7 W | **60%** |
| ET-SoC-1 fp32 (21 Sep) | 2.00 W | 27.11 W | **7%** |
| ET-SoC-1 fp32 (E67 session) | 3.23 W | 27.89 W | **12%** |
| ET-SoC-1 fp32, per MAC, E38's three cards | — | — | **3%, 4%, 7%** |

**The quietest data still costs an A100 54–75% of its busiest switching. On the ET-SoC-1 it costs 3–12%.**
That is the finding; the ratio is its reciprocal (×8.6–×32.9 against ×1.3–×1.8), and it is why the effect
is loud on one chip and faint on the other. The physics is identical; what differs is how much of each
chip's work depends on the numbers at all. 🛑 And say **"as little as about 148 W of its 240 W, whatever the
data"** — 147.6 W is the quietest run measured, a **floor**, not a demonstrated data-independent component.

*Dated note, Sun 1 Nov 2026, from the kinds page's verifier: 3–12% is the ET-SoC-1's resident loop, by September's protocol, not the chip. Zeros' watts read 13–14% of random's in the benchmark, 26–30% on the cold walks in fp32 and fp16, 61% in the one fp32 arm from DRAM ([E101](../2026-11-01-e101-real-matmul/README.md), [E105](../2026-11-01-e105-gemm-layout/README.md)). An A100's matmul streams, so this ratio does not separate the chip from the kernel.*

**One ratio, with its basis.** The first pass printed ×13.6 (switching power) and ×21.4 (energy per MAC) as
two readings of one quantity; they are 57% apart because they are different measurements:

- **×13.6** = 27.11 / 2.00 W, one session's pair at launch temperature
  (`docs/findings/10-data-dependent-power.md`). The same file states the same effect as *"Over the idle
  card the data decides a factor of 14–15 in energy per FLOP (0.22 against 2.95 pJ at 80 °C, 3.31 on the
  run average)"* (line 58) — ×13.4 to ×15.0, i.e. the same thing.
- **×8.6** on the E67 session's own anchors, the same card type at the same clock: the over-idle ratio
  moves with the idle basis.
- **×21.4** = 5.783 / 0.27 pJ per MAC, E38's **three-card means**
  (`docs/reports/data/2026-10-27-matmul-to-transistor/data.json`, `/permac/mean_randn_pJ`,
  `/permac/mean_zeros_pJ`). Per card (`/permac/e38_registered`): aifoundry2 5.920/0.4034 = **×14.7**,
  aifoundry3 5.369/0.1633 = **×32.9**, aifoundry1-c1 6.058/0.2512 = **×24.1**. Mean of the ratios ×23.9 —
  which is not the ratio of the means.
- The spread is entirely the **zeros denominator**, 0.163 to 0.403 pJ per MAC: a small difference of large
  numbers, with no published interval of its own.

**For the blog:** quote **"more than ten times, and up to thirty on the quietest card"** with the
convention named, or quote the floor shares above, which need no ratio at all. Do not print a bare ×13.6
or ×21.4 as *the* number.

### 6b. Speed

| System | Effect on speed | Source |
|---|---|---|
| **ET-SoC-1, burst** | zeros **×1.127–1.150** faster than random (measured, 4 comparators; ×1.147 predicted) | `docs/findings/05-claims.md`, the burst-gap row; `docs/findings/02-requests.md` Q128(f) |
| **ET-SoC-1, sustained** | **800 vs 600 MHz = ×1.333 (33%)**; random falls to the governor's floor, zeros does not. A *clamp*, not a ratio that scales with the cap | `docs/reports/data/2026-10-23-e64-horace-power-limit/results.md` |
| Horace He, A100 | zeros 295 vs randn 257 TFLOPS = **×1.148 (14.8%)**, size not stated | thonking.ai, 29 Apr 2024 |
| Bhalachandra, A100, 16384³ fp64 | random **4% slower** (18.6 vs 19.4 TFLOPS) at a 400 W cap | arXiv:2212.08805 |
| Gregersen, A100, 2048³ | **no speed effect** — *"consistent to a microsecond-level"*, size chosen not to throttle | arXiv:2409.18324 |

**The ET-SoC-1's burst number (×1.127–1.150) and Horace's ×1.148 agree inside the lab's own interval.** Two
chips, two vendors, the same number — the best sentence available for the blog's opening. The sustained 33%
is larger than anything in the literature **because the ET-SoC-1's governor has a discrete floor**: the
claims register calls it a clamp, not a test (any cap in a 14.56 W window returns exactly 800/600), and the
blog must say so.

### 6c. Energy per operation, across the formats — **and which convention each number is on**

🛑 **The correction that matters most in this file.** `docs/findings/05-claims.md` line 1094 reads "**At the
board, over idle**, per random fp32 multiply-add — **5.783 pJ**". It is **switching energy over the idle
card**, not a whole-board total, and the whole-board pair sits in the same JSON object. Both, with their
keys:

| ET-SoC-1 fp32, 600 MHz, 1,024 harts | random normal | zeros | ratio | key |
|---|---|---|---|---|
| **at the board, over idle** | **5.783 pJ** | **0.27 pJ** | ×21.4 | `/permac/mean_randn_pJ`, `/permac/mean_zeros_pJ` |
| **whole board**, idle included | **11.579 pJ** | **6.139 pJ** | ×1.89 | `/permac/budget_600_pJ/randn_board`, `/zeros_board` |

(both in `docs/reports/data/2026-10-27-matmul-to-transistor/data.json`; the whole-board pair is also printed
in `docs/reports/data/2026-10-27-chain-closure/README.md`'s term table.)

| Reference | fp32 MAC | fp16 MAC | int8 MAC | Conditions |
|---|---|---|---|---|
| Horowitz 2014 (via Dally's slide) | **4.6 pJ** (3.7 + 0.9) | **1.5 pJ** (1.1 + 0.4) | **0.3 pJ** (0.2 + 0.1) | 45 nm, 0.9 V, **arithmetic only**, "rough"; no transport, no fetch, no memory, no idle, no leakage |
| Dally 2018, HMMA | — | **2.19 pJ/MAC** incl. the 30 pJ overhead, **at an assumed 64 MACs** (1.72 pJ of arithmetic) | — | 45 nm; the slide states no MAC count (§3b) |
| Dally 2022, 16-bit MAC | — | **≈0.16 pJ** | — | 5-nm-class, ≈0.75 V, reconstruction |
| **ET-SoC-1, random** | **5.783 pJ** | — (E78/E80 fill this) | — | **at the board, OVER IDLE**; 7-nm class, 0.517 V minion rail, resident tiles |
| **ET-SoC-1, zeros** | **0.27 pJ** | — | — | same convention |
| **ET-SoC-1, random / zeros** | **11.579 / 6.139 pJ** | — | — | **whole board**, idle included — the other convention |
| A100 FP16-T, random / zeros | — | **3.98 / 2.46 pJ** *(derived, ±30%)* | — | whole board, 2048³ GEMM incl. memory traffic |
| A100 FP32 (CUDA cores), random / zeros | **40.72 / 27.63 pJ** *(derived, ±30%)* | — | — | whole board, SIMT not tensor core, incl. memory |
| Bhalachandra 2022 upper bound | **≈16 pJ/MAC** (8 pJ/FLOP) | — | — | A100 fp64, **FPU only**, from the 159 W random−fixed delta |

**Read it this way for the blog.** Horowitz's 45 nm fp32 multiply-add is **4.6 pJ of arithmetic alone**, and
his own caption calls it rough. The ET-SoC-1's **switching, over idle, for the whole board** — rails,
clocks, mesh, register files, operand delivery, not just the multiplier — is **5.783 pJ** for the same
operation on a process three generations newer: **×1.26**. Almost the whole twelve-year gain in the
multiplier went into paying for *everything around it*, which is Dally's thesis stated as a measurement.
And when the operands stop changing, that switching falls to **0.27 pJ — 17× below the bare 45 nm
arithmetic** — because the data-dependent part was never the multiplier, it was the bits arriving at it.

🛑 **Both of those sentences are on the over-idle convention, and only there.** On the whole-board
convention the same card pays **11.579 pJ** random and **6.139 pJ** on zeros, so **both** sit *above*
Horowitz's 4.6 pJ (×2.52 and ×1.33) and the "17× below" statement is false. Horowitz's figure is a dynamic
switching energy with no idle or leakage term, which is why over-idle is the like-for-like side — but the
convention has to travel with the number. **Never write "whole board … regulators, rails, clocks, leakage
and all" next to 5.783 pJ**: that is exactly what has been subtracted.

**Two further caveats the blog must carry.** The A100 per-MAC figures include a 2048³ GEMM's full memory
traffic while the ET-SoC-1's TensorFMA repeats on resident tiles, so the per-MAC columns are **not
like-for-like** — the honest cross-machine comparison is the *ratio between kinds*, which is
traffic-independent. And the A100 per-MAC numbers are this lane's derivation from trace length, ±30%
(§7).

### 6d. Per flipped bit

| Reference | Price of one flipped bit | What path |
|---|---|---|
| **ET-SoC-1, E60/E68** | **117.5 ± 2.8 fJ** at the registered leakage slope; **135.9 ± 2.7 fJ** at E66's measured slope; **quote 118–136 fJ**, upper end better supported | one input bit of an fp32 multiply-add, at the board |
| **ET-SoC-1, E75** | **L2: 0.274 pJ [0.183, 0.366]** per changed bit. 🛑 **L1 is 0.0492 pJ [0.0482, 0.0501]; L3 and DRAM are NOT RESOLVED — quote < 0.37 and < 0.42 pJ at 95%** | memory path, a changed bit, by level |
| Dally 2022 *(lab reconstruction)* | **30 fJ per bit·millimetre** | on-chip wire, 0.2 fF/µm, ≈0.75 V, activity 0.5, 5-nm class |
| **ET-SoC-1 mesh, finding 20 / E32** | **36.2 fJ per bit·mm** on the mesh rail (24.6 data + 11.7 fixed), **46.7 fJ per bit·mm** on board power | a random bit carried a millimetre, free links, 0.485 V |
| A100 *(derived here)* | **≈7.65 pJ ± 0.60 (fit), 5.4–9.9 pJ with timing**, rising slope only, saturating at n ≈ 4 of 8 | a bit XORed in an HBM2-resident int8 matrix: load, flip, store |
| Gregersen 2024 | none — a hypothesis, correlated with bit alignment and Hamming weight, *"not an entirely consistent trend"* | — |
| Li et al. 2020 | none absolute; **2.85× datapath energy** from reordering alone | 8b × 4b systolic datapath, post-layout |

Sources: `docs/findings/05-claims.md` — the "A flipped mantissa bit is a band, not a number" row, the "The
memory path per changed bit" row, and the 🛑 **"37 fJ per bit·mm is not one number — say which of these you
mean"** row (added 26 Oct 2026 for exactly this confusion).

**Nobody else has published a per-flipped-bit price for a multiply-add.** The task brief's "117 fJ (E60)" is
the registered-slope end; the lab's own record says to quote the band **118–136 fJ**.

🛑 **The millimetre conversion, recomputed.** The first pass claimed a "2.3× discrepancy" between the
published page *A bit flip in microns* (1.8 mm) and Dally's rate (4.2 mm), and its own arithmetic did not
work: 1.8 mm × 43.7 fJ/mm = 78.7 fJ, not 127 fJ. What is actually true:

- The page's **1.8 mm is E60's 116.7 fJ** charged at **66.4 fJ per mm on board power** (its own stated
  rate; it gives 2.0 mm for the A = π bit at 129.9 fJ). The "43.7 fJ/mm" quoted alongside is the **mesh**
  figure from the same page, not the rate behind the 1.8 mm.
- The claims register supersedes that pair: its stop-sign row says the number sometimes quoted as "43.7"
  is **43.5 fJ per bit per *hop*** (one hop = 3.72 mm — the fixed part of the cost), and the per-bit·mm
  figures are **36.2 fJ (mesh rail)** and **46.7 fJ (board)**.
- So for the band's mid-point, 127 fJ: **2.7 mm** on the lab's own board rate, **3.5 mm** on its mesh rail,
  **4.2 mm** at Dally's reconstructed 30 fJ/bit·mm (5-nm class, ≈0.75 V, against this part's 0.485 V mesh).

**A 1.6× spread across three conventions, not 2.3×, and no contradiction** — just three rails. Pick one,
name it, and say "per bit·mm" or "per bit per hop". *"One input bit of one multiply-add costs as much as
carrying that bit three to four millimetres across the die"* is defensible on any of them.

**One more corroboration worth the blog's space.** The A100's own Hamming ladder, reduced from the authors'
traces, **saturates at about half a byte**: +2.28, +4.57, +5.99, +8.02 W for 1–4 flipped bit positions,
then flat within a 0.49 W noise control out to 32. The lab found the same shape on the ET-SoC-1 (E70,
shared wires, carry-over 1.246 ± 0.014; E67, sub-additive at **16 of 16** grid cells, 16.185 W measured
against 18.372 W summed). Li/Tiwari/Orshansky 2021 found the same blurring in a 2D systolic array, where
many MACs share one operand. **Flips are not additive on any of the three machines** — three machines,
three methods, one law, and the most transferable finding in this file.

---

## 7. What could not be verified

1. **Horace He's per-distribution numbers.** The TFLOPS for the nine data kinds, and every value in his
   power-cap and clock-cap sweeps, are in unlabelled images. Only §1's table is in his text. Nothing
   quantitative can be quoted for checkerboard, ternary, one-bit, π, twos, uniform or 75%-sparse, and
   **no matrix size can be attached to the 295/257 pair**. A per-kind comparison against E64/E78 has to be
   the ET-SoC-1's own table with Horace's names, not his numbers.
2. **Horowitz Figure 1.1.9 itself.** The per-operation table is a raster image in both copies reachable
   today (gwern's PDF and the Semantic Scholar scan); `pdftotext` returns the body text and the caption but
   not the figure. The eleven values in §3a are therefore from Dally's own slide and from Luo & Sun's
   Table 1, which agree exactly and both cite Horowitz 2014. **The IEEE Xplore original
   (DOI 10.1109/ISSCC.2014.6757323) has not been read.** The caption's conditions (45 nm, 0.9 V, "rough")
   *are* from the paper.
3. **Horowitz's body text and his table disagree and must not be averaged.** The text says *"a cache fetch
   is 20pJ"* and a DRAM access is *"1 to 2nJ"*; the table says 32b SRAM read (8 KB) = 5 pJ and 32b DRAM
   read = 640 pJ. Different widths, different levels. Quote each with its condition. No SRAM row other
   than the 8 KB one is reproduced anywhere, and the table has no fp8, int4 or fp16-SRAM row at all —
   arXiv:2510.25602's normalised ratios are the only substitute and give no absolute pJ.
4. **The lab's own `dally-heuristics` page could not be read over the wire.** `WebFetch` of
   <https://spacesheep.dev/@yaroslavvb/dally-heuristics> returns a client-rendered shell with no figures.
   Every value in §3c came from the page's source in the project's private notes instead. If the blog cites
   the public page for a number, re-read it in a browser first. Related: §3c now separates **Dally's own
   stated figures** from **the lab's reconstruction**, and the first pass's derivation
   "(= 57.4 pJ ÷ 64 b ÷ 30 mm)" is withdrawn — it is in no source read here.
5. **Whether Dally's CACM article states the 30 fJ/bit·mm constant in those words is unverified.** The
   article itself was not read today (paywall); the constant as used here is the lab page's model output
   (30.9 fJ/bit·mm) reconciled against the figures the page attributes to him. Check the article before
   writing "Dally says 30 fJ per bit per millimetre".
6. **Pekhimenko et al.'s energy numbers** (up to 8.9%, 2.1% average). From secondary indexing; the HPCA PDF
   was not re-read. The 20%-to-2.2× toggle figure is the paper's own abstract and is solid.
7. **The Blackwell per-format watts.** arXiv:2507.10789's Table VI gives no method, no clocks and no energy
   per op, and its caption promises a performance-per-watt column that is absent. On a consumer RTX 5080,
   16.753 W for FP4 is far below any sustained tensor-core load — these are short-kernel averages. Quote
   the trend, not the watts, and keep Table VI and Table VIII apart (§5(8)).
8. **No arXiv precedent for Horace's exact result on Hopper.** A commenter (Aleksa Gordić) said a paper had
   described the phenomenon earlier on Hopper; searched twice, not found. The genuine earlier work is
   Bhalachandra 2022 on an A100 and Lucas & Juurlink 2016. Treated as unverified.
9. **The derived A100 figures are reductions of a third party's published traces, not measurements of this
   lane's.** The watts are solid: the authors' own `POWER` column, 10 seeds pooled, first 500 ms trimmed as
   they trim, and `cudaDeviceSynchronize()` is inside their iteration loop so trace length is compute time.
   The **per-MAC and per-flip conversions divide by a runtime inferred from trace length**, which includes
   `dcgmi dmon` pre- and post-roll: **±30%**, and they must not sit in a table beside measured ET-SoC-1
   values without that label. Sanity check: implied throughputs are 14.2 TFLOP/s fp32 (73% of the A100
   PCIe's 19.5 peak) and 149.4 TFLOP/s fp16-T (48% of 312), both plausible for CUTLASS at 2048³.
   The derived **int8** per-MAC (69.1 pJ at 7.7 TOP/s) is a slow SIMT path, **not** the int8 tensor-core
   path, and is not an int8 comparator at all.
10. **The A100 Hamming ladder has one trace per condition.** Its only replication is the accidental one
    (n = 8…32, the truncated mask): sd 0.490 W, spread 1.90 W. Every rung carries that scatter, and no
    pass of this reduction may use within-burst samples as the unit of replication.
11. **Lucas & Juurlink's 155–257 W** is now verified as the authors' own abstract text, but the **GPU, the
    kernel and the idle draw are not named there**, and the postprint PDF is behind a challenge page. It
    stays an absolute-board entry only.
12. **No measured per-flipped-bit price inside a tensor core** exists in the 2020–2026 literature, and no
    operand-level **Gray coding** paper exists in 2024–2026. Searched both; §5's "thin spots" records what
    was found instead. Worth re-running that search immediately before publication.
13. **The published page *A bit flip in microns* and the project hub's 20 Oct entry carry the superseded
    "43.7 fJ per mm / 66.4 fJ per mm" labels** that the claims register's 26 Oct stop-sign row was written
    to correct. §6d restates the arithmetic, but **the deployed page itself has not been corrected** —
    that is the owner's call, and the hub's log is append-only.

---

## References

1. He, Horace. "Strangely, Matrix Multiplications on GPUs Run Faster When Given 'Predictable' Data!
   [short]." *thonking.ai*, 29 Apr 2024. <https://www.thonking.ai/p/strangely-matrix-multiplications> ·
   comments <https://www.thonking.ai/p/strangely-matrix-multiplications/comments>
2. Gregersen, Theo, Pratyush Patel, and Esha Choukse. "Input-Dependent Power Usage in GPUs."
   arXiv:2409.18324v1, 26 Sep 2024; SC'24 Sustainable Supercomputing workshop.
   <https://arxiv.org/abs/2409.18324> · data <https://github.com/theo-gregersen/input-dependent-power-sc24>
3. Horowitz, Mark. "1.1 Computing's energy problem (and what we can do about it)." *ISSCC 2014 Digest of
   Technical Papers*, 10 Feb 2014, 10–14. DOI 10.1109/ISSCC.2014.6757323.
   Copy: <https://gwern.net/doc/cs/hardware/2014-horowitz-2.pdf>
4. Dally, Bill. "Scaling of Machine Learning." Scaled ML, 24 Mar 2018.
   <https://www.matroid.com/wp-content/uploads/2024/11/bill-dally-ScaledML.pdf>
5. Dally, Bill. "On the Model of Computation: Point." *Communications of the ACM* 65(9), Sept 2022.
   Rebuilt with calculators: <https://spacesheep.dev/@yaroslavvb/dally-heuristics>
6. Luo, Hongyin, and Wei Sun. "Addition is All You Need for Energy-Efficient Language Models."
   arXiv:2410.00907v2, Oct 2024. (Table 1 reproduces Horowitz 2014.)
7. NVIDIA. "Field Constants — DCGM API."
   <https://docs.nvidia.com/datacenter/dcgm/3.1/dcgm-api/dcgm-api-field-constants.html>
8. NVIDIA. "nvmlClocksEventReasons / nvmlClocksThrottleReasons — NVML API Reference (R550)."
   <https://docs.nvidia.com/deploy/archive/R550/nvml-api/group__nvmlClocksEventReasons.html>
9. AMD. "GPU violations — AMD SMI."
   <https://rocm.docs.amd.com/projects/amdsmi/en/latest/_sources/conceptual/gpu-violations.md>
10. NVIDIA. "NVIDIA Sets New Generative AI Performance and Scale Records in MLPerf Training v4.0."
    <https://developer.nvidia.com/blog/nvidia-sets-new-generative-ai-performance-and-scale-records-in-mlperf-training-v4-0>
11. Bhalachandra, Sridutt, Brian Austin, Samuel Williams, and Nicholas J. Wright. "Understanding the Impact
    of Input Entropy on FPU, CPU, and GPU Power." arXiv:2212.08805, 17 Dec 2022.
    <https://arxiv.org/abs/2212.08805>
12. Li, Meng, Yi Li, Pierce Chuang, Liangzhen Lai, and Vikas Chandra. "Improving Efficiency in Neural
    Network Accelerator Using Operands Hamming Distance optimization." arXiv:2002.05293, 13 Feb 2020.
    <https://arxiv.org/abs/2002.05293>
13. Peltekis, Christodoulos, Dionysios Filippas, Giorgos Dimitrakopoulos, and Chrysostomos Nicopoulos.
    "Low-Power Data Streaming in Systolic Arrays with Bus-Invert Coding and Zero-Value Clock Gating."
    MOCAST 2023. DOI 10.1109/MOCAST57943.2023.10176467; arXiv:2304.12691.
    <https://arxiv.org/abs/2304.12691>
14. Li, Ge, Mohit Tiwari, and Michael Orshansky. "Power-Based Attacks on Spatial DNN Accelerators."
    *ACM JETC*, Aug 2021; arXiv:2108.12579. <https://arxiv.org/abs/2108.12579>
15. Han, Ruixiao, Yuxuan Chen, Tianyu Lei, Jaime Altayo Gonzalez, and Ahmed Hemani. "'1'-bit Count-based
    Sorting Unit to Reduce Link Power in DNN Accelerators." arXiv:2601.14087v1, 20 Jan 2026.
    <https://arxiv.org/abs/2601.14087>
16. Chen, Mengzhao, et al. "INT v.s. FP: A Comprehensive Study of Fine-Grained Low-bit Quantization
    Formats." arXiv:2510.25602v1, 29 Oct 2025. <https://arxiv.org/abs/2510.25602>
17. Jarmusch, Aaron, Nathan Graddon, and Sunita Chandrasekaran. "Dissecting the NVIDIA Blackwell
    Architecture with Microbenchmarks." arXiv:2507.10789v2, 21 Jul 2025.
    <https://arxiv.org/abs/2507.10789>
18. Ujeniya, Aditya, Jan Eitzinger, Georg Hager, and Gerhard Wellein. "Architectural Trade-offs in the
    Energy-Efficient Era: A Comparative Study of power-capping NVIDIA H100 and H200." arXiv:2604.11391v2,
    15 Jul 2026. <https://arxiv.org/abs/2604.11391>
19. Lucas, Jan, and Ben Juurlink. "ALUPower: Data Dependent Power Consumption in GPUs." MASCOTS 2016,
    95–104. DOI 10.1109/MASCOTS.2016.21.
    <https://depositonce.tu-berlin.de/items/f6f95245-1fea-41d7-8a84-8f83c4d6a84a>
20. Pekhimenko, Gennady, Evgeny Bolotin, Nandita Vijaykumar, Onur Mutlu, Todd C. Mowry, and Stephen W.
    Keckler. "A Case for Toggle-Aware Compression for GPU Systems." HPCA 2016, 188–200.
    <https://research.nvidia.com/publication/2016-03_case-toggle-aware-compression-gpu-systems>
21. Singhania, Varsha, Shaizeen Aga, and Mohamed Assem Ibrahim. "FinGraV: Methodology for Fine-Grain GPU
    Power Visibility and Insights." arXiv:2412.12426v2, 28 Mar 2025. (Cites [2]; no data-value experiments
    of its own.)
22. Aga, Shaizeen, and Mohamed Assem Ibrahim. "CompPow: A Case for Component-level GPU Power Management."
    arXiv:2605.21847v1, 21 May 2026. (Cites [2]; component-level power, 10% energy / 5% performance.)

**Lab-side sources used for the comparisons** (all repo-relative, in this repository):
`docs/findings/10-data-dependent-power.md` (the ten-kind fp32 table: zeros 38.29, ternary 45.70, random
normal 63.40 W, idle 36.29 ± 0.06; line 58's "factor of 14–15 in energy per FLOP");
`docs/findings/05-claims.md` (line 1094 "At the board, over idle, per random fp32 multiply-add — 5.783 pJ";
the "A flipped mantissa bit is a band, not a number" row, 117.5 ± 2.8 / 135.9 ± 2.7 fJ, quote 118–136; the
burst-gap row, ×1.147 predicted against ×1.127–1.150 measured over four comparators; the sustained-gap
clamp row; the "memory path per changed bit" row, L1 0.0492 [0.0482, 0.0501] and L2 0.274 [0.183, 0.366] pJ
with L3 and DRAM unresolved; the "37 fJ per bit·mm is not one number" stop-sign row, mesh 36.2 / board 46.7
fJ per bit·mm and 43.5 fJ per bit per hop; E67's sub-additivity at 16 of 16 cells; E70's carry-over
1.246 ± 0.014); `docs/findings/02-requests.md` Q128(f);
`docs/reports/data/2026-10-23-e64-horace-power-limit/results.md` (sustained randn fp32 600 MHz / 54.4 W /
67.1 °C, fp16 600 MHz / 51.3 W, int8 763 MHz / 50.7 W; the cool-die ladder at 800 MHz);
`docs/reports/data/2026-10-27-matmul-to-transistor/data.json` (`/permac/mean_randn_pJ` 5.783,
`/permac/mean_zeros_pJ` 0.27, `/permac/budget_600_pJ/randn_board` 11.579, `/zeros_board` 6.139,
`/permac/e38_registered/<card>/{random,zeros}`, `/q129/kernels/e75_levels[1]/e_flip_pJ` 0.274);
`docs/reports/data/2026-10-27-chain-closure/README.md` (the term table: idle 24.60, zeros 27.83 W / 6.14 pJ,
random 52.49 W / 11.58 pJ).

---

## Files beside this one

| File | What |
|---|---|
| `a100-watts.txt` | every A100 experiment cell reduced to watts (first pass, unchanged — the watts were correct) |
| `a100-bitflips-v2.txt` | **corrected** Hamming ladder: the ladder, the identical-workload control, two slopes, the knee |
| `a100-permac.txt` | per-MAC conversions, ±30% (first pass, unchanged) |
| `ratio-conventions.txt` | **new**: every data-effect ratio in both conventions, the floor shares, and the per-MAC conventions reconciled |
| `reduce_idp.py` | the watts reduction (first pass) |
| `reduce_bitflips_v2.py` | **corrected** ladder reduction, with the control the first pass missed |
| `permac.py` | the per-MAC conversion (first pass) |
| `compare_conventions.py` | **new**: the convention table, every input annotated with its committed source |

To re-run the three A100 reductions, clone the authors' data repository
(<https://github.com/theo-gregersen/input-dependent-power-sc24>) into a directory of its own and pass the
path as an argument. Their traces are third-party data and are not vendored here; neither are the papers'
PDFs (retained only in the lane's own handoff).
