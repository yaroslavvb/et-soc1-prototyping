# Sparse parity: the Sutro challenge, the literature, and where 1,000 cores matter

Brief SP1, 28 September 2026: web and repository research, no card access. **M** measured on the lab cards (repository), **X** published by others, **E** estimated here.

## 1. The Sutro group's challenge

Two venues, both noiseless and small, both scoring energy or data movement rather than wall time.

- **[sparse-parity-challenge](https://github.com/cybertronai/sparse-parity-challenge)** (from [SutroYaro](https://github.com/cybertronai/SutroYaro), March 2026). A submission is `solve(x, y, n_bits, k_sparse)` in numpy. The inputs are ±1 and the label is the product of k secret bits. The configuration is n = 20, k = 3 (C = 1,140 subsets), with no noise. It must reach ≥95% over 3 seeds within 60 s, and it is ranked by DMD, "sum of sqrt(stack_distance) per element read" (moving to [ByteDMD](https://github.com/cybertronai/ByteDMD), ⌈√depth⌉ per byte). The leader is "Sequential Elimination" at DMD 19,153. GF(2) entries score 45,904 to 24.4M.
  - SutroYaro's 36 experiments ([DISCOVERIES.md](https://github.com/cybertronai/SutroYaro/blob/main/DISCOVERIES.md), [survey](https://github.com/cybertronai/SutroYaro/blob/main/survey.md)): GF(2) solves n=20/k=3 in 509 µs, SGD in 0.12 s, the Fourier test n=200/k=3 in 10.8 s; "Standard SGD breaks at n^k > 100,000 steps" (n=50/k=3 stuck at 54%), while GrokFast plus a curriculum solves n=50/k=5 in 77 ms.
  - Their O(n) "KM influence" solver queries labels of chosen inputs, which "a pure PAC learning setting with i.i.d. samples" does not allow ([exp_km](https://github.com/cybertronai/SutroYaro/blob/main/findings/exp_km.md)).
- **[sutro-problems/sparse-parity](https://github.com/cybertronai/sutro-problems/tree/main/sparse-parity)** (current). Each instance has n = 32, k = 5 and m = 18 noiseless strings. The solver outputs the 32-cell secret mask. Energy is the static read cost of a straight-line program (8-bit cells, v3 ISA, ≤2M lines) in the [simplified Dally model](https://github.com/cybertronai/simplified-dally-model): "every operand read of address a costs ⌈√a⌉". Records are kept at 20/40/60/80/100% recovery:

  | Recovery | Record cost | Method |
  |---|---|---|
  | 20% | 86,753 | packed static information set |
  | 40% | 141,218 | |
  | 60% | 149,665 | |
  | 80% | 182,744 | |
  | 100% | 392,666 | packed RREF + capture |

  The 100% baseline is a Gray walk of the 2^14 null space, costing 43.3M. The retired tiers ([legacy.md](https://github.com/cybertronai/sutro-problems/blob/main/sparse-parity/legacy.md)) were (n,k) = (3,2), (8,3), (12,3) with m = 8, and (32,5) with a test set. The [analysis page](https://cybertronai.github.io/sutro-problems/docs/spatial-model-analysis.html) measures 4.22% success per ISD restart at n=32 (theory 4.25%).

**Takeaway:** nothing in the Sutro tiers needs 1,000 cores. The ET case has to come from larger instances, noisy instances, or instances with few samples (§3).

## 2. Literature

**Definitions.** x is uniform on {±1}^n and y = χ_S(x) = ∏_{i∈S} x_i with |S| = k, flipped with probability η; noisy labels with a sparse secret give LSPN (learning sparse parities with noise). About log₂C(n,k) ≈ k log n samples suffice without noise, O(k log n/(1−2η)²) with it.

"Sparse LPN" in cryptography usually means something different: sparse *equations* (Alekhnovich 2003, [doi](https://doi.org/10.1109/sfcs.2003.1238204)). [Bangachev et al. 2024](https://arxiv.org/abs/2411.12512) prove n^{Ω(k/polylog)} bounds for that variant.

**Hardness.**
- SQ lower bound: "Ω(n^k) constant-noise queries are necessary, which is far greater than the statistical limit" ([Barak et al.](https://arxiv.org/abs/2207.08799), after [Kearns 1998](https://doi.org/10.1145/293347.293351) and [Blum et al. 1994](https://doi.org/10.1145/195058.195147)).
- Noisy sparse parity "even at a very small noise level … is believed to inherently require n^{Ω(k)} computational steps", first conjectured by Alekhnovich (quoted in Barak et al.).

**Algorithms.**
- **Noiseless, m ≥ n:** GF(2) Gaussian elimination costs ~½n³ bit-ops. [M4RI](https://doi.org/10.1145/1644001.1644010) gives O(n³/log n).
- **Noiseless, m ≈ k log n:**
  - Meet-in-the-middle takes Õ(C(n,k/2)) time and memory (Spielman, reported in [Klivans–Servedio 2004](https://doi.org/10.1007/978-3-540-27819-1_16)).
  - There is a time–sample dial (Buhrman–García-Soriano–Matsliah 2010; [Bhattacharyya–Gadekar–Rajgopal 2020](https://doi.org/10.1016/j.tcs.2020.08.025)).
  - Prange information-set decoding needs C(n,k)/C(m,k) expected restarts, each an m×m GF(2) solve. This case is syndrome decoding, so the GPU ISD work applies ([Esser–May–Zweydinger 2022](https://doi.org/10.1007/978-3-031-07082-2_16)).
- **Exhaustive correlation (Fourier) test:** C(n,k)·m pair-tests at any η < ½. It is the SQ-optimal baseline.
- **Grigorescu–Reyzin–Vempala 2011** ([doi](https://doi.org/10.1007/978-3-642-24412-4_32)): runs in n^{(1+(2η)²+o(1))k/2}·poly(1/(1−2η)), close to n^{k/2} when η is small.
- **Valiant's light bulb method:** [preliminary version](https://eccc.weizmann.ac.il/report/2012/006/), "< n^{.82k} poly(1/(1−2η))"; [J. ACM 2015](https://doi.org/10.1145/2728167), n^{0.80k}.
  - [Karppa–Kaski–Kohonen](https://arxiv.org/abs/1510.03895) (SODA 2016 / TALG 2018): Õ(n^{(ω+ε)k/3}·|1−2η|^{−8ω/9−4/3}) time with (2k+3)|1−2η|^{−4ω/9−2/3} log n samples.
  - Both need fast matrix multiplication, which "remains the only known tool to obtain truly subquadratic scaling for weak outliers" (Karppa et al.).
  - With ω = 3 the practical content is that **the correlation test is a matrix product**.
- **BKW** ([Blum–Kalai–Wasserman 2003](https://doi.org/10.1145/792538.792543)): 2^{O(n/log n)} for dense LPN; see also [Lyubashevsky 2005](https://doi.org/10.1007/11538462_32), [LPN Decoded 2017](https://doi.org/10.1007/978-3-319-63715-0_17) and Coded-BKW in "only 2^39 bits of memory" ([Wiggers–Samardjiska 2021](https://doi.org/10.1109/isit45174.2021.9518109)). None is sparse-specific.

**Neural networks.** These pay the n^{O(k)} search plus the network, so they test the energy of learning, not the fastest solve.
- [Barak et al. 2022](https://arxiv.org/abs/2207.08799): SGD learns in "approximately n^{O(k)} iterations", which "nearly matches SQ lower bounds". Experiments cover n ≤ 30, k ≤ 4 and n = 50, k = 3. The progress is hidden: a Fourier gap is amplified.
- [Edelman et al. 2023](https://arxiv.org/abs/2309.03800): "width plays the role of parallel search", and sparse initialization helps.
- [Kou, Chen, Gu, Kakade 2024](https://arxiv.org/abs/2404.12376): sign SGD reaches Õ(d^{k−1}) samples with 2^{Θ(k)} neurons, matching the SQ bound.

**Hardware.** Epistasis detection, the k-way SNP interaction search, is the same kernel on binary data.
- One Turing GPU evaluates 25.4×10¹² 3-way sets·samples/s on binary tensor cores ([Nobre et al. IPDPS 2020](https://doi.org/10.1109/ipdps47924.2020.00043)).
- "Fused XOR and population count as the highest throughput operations" reach 54.5×10¹² ([TPDS 2021](https://doi.org/10.1109/tpds.2021.3060322)).
- The 4-way version reaches 90.9×10¹² on one A100 and 835×10¹² on 8 ([ICPP 2022](https://doi.org/10.1145/3545008.3545066)), and up to 13×10¹⁵ on 32 A100s ([ICS 2025](https://doi.org/10.1145/3721145.3725769)).
- Gray-code exhaustive search over GF(2) has also been done on GPUs ([Bouillaguet et al. 2010](https://doi.org/10.1007/978-3-642-15031-9_14)).

## 3. Where parallel hardware matters

**Rates used** ([estimate_ops.py](estimate_ops.py)).
- Samples: m ≈ (√(2 ln C(n,k)) + 3)²/(1−2η)², so the true coefficient 1−2η clears the largest null correlation by 3σ (E).
- One CPU core: 5×10¹¹ pair-tests or bit-ops per second (AVX-512 xor plus popcount, optimistic; E).
- ET-SoC-1 tensor path: int8 at the measured 71.8 TOP/s, i.e. 3.6×10¹³ ±1 MACs per second (M, `docs/et-soc1-notes.md`), assumed reached by the split GEMM below (E).
- ET-SoC-1 vector path: the minion has no popcount instruction, so SWAR popcount gives about 10¹³ pair-tests per second (E, [chip.md](chip.md)). XOR streams run at about 1.2×10¹⁴ bit-ops per second when the matrix is L1-resident and about 7×10¹² when it streams from L2 (E).

**Split GEMM.** Write S = S₁∪S₂ and define A[i,S₁] = y_iχ_{S₁}(x_i) and B[i,S₂] = χ_{S₂}(x_i). Then (AᵀB)[S₁,S₂] = m × the empirical correlation of S₁∪S₂. Sort the rows by max S₁ and the columns by min S₂, and compute only the tiles where max < min; the overcount then tends to 1. Each minion generates its A and B tiles from the packed x.

| n | k | η | m | Algorithm | Ops | 1 CPU core | ET-SoC-1 (E) |
|---|---|---|---|---|---|---|---|
| 20 | 3 | 0 | 21 | GF(2) GE (Sutro challenge) | 4×10³ bit | µs | — |
| 32 | 5 | 0 | 18 | null-space walk / ISD (Sutro mask tier) | 5×10⁵ / 1.2×10⁵ bit | µs | — |
| 64 | 4 | 0.1 | 104 | correlation | 6.6×10⁷ pair | 0.1 ms | 2 µs |
| 128 | 6 | 0.2 | 261 | correlation | 1.4×10¹² | 2.8 s | 40 ms |
| 1024 | 4 | 0.3 | 626 | correlation | 2.9×10¹³ | 57 s | 0.8 s |
| 256 | 6 | 0.25 | 424 | correlation | 1.6×10¹⁴ | 5 min | 4.4 s |
| 128 | 8 | 0.2 | 305 | correlation | 4.4×10¹⁴ | 15 min | 12 s |
| 256 | 8 | 0.1 | 196 | correlation | 8×10¹⁶ | 45 h | 37 min |
| 128 | any | 0.15 | ≥128 | sample-then-GE, (1−η)^{−n} tries | 1.1×10¹⁵ bit | 38 min | 10–160 s |
| 256 | 12 | 0 | 90 | Prange ISD, 4.7×10⁵ restarts | 4.8×10¹¹ bit | 1 s | 4–70 ms |
| 512 | 16 | 0 | 150 | Prange ISD, 6.1×10⁸ restarts | 3.5×10¹⁵ bit | 2 h | 0.5–8 min |

**Formulations where the chip is visibly used:**

1. **Noisy correlation search** at n = 128–1024, k = 4–8, η = 0.2–0.3. It is compute-bound on the int8 tensor unit (the ±1 GEMM beats SWAR popcount by about 3.6×), and the operands are generated on the fly.
2. **Sample-starved noiseless ISD** at n = 256–512, with m 1.3–1.5× the information limit. The restarts are independent, and each m×n bit matrix (2–10 KB) is minion-local. The only communication is a "found" flag.
3. **Noiseless meet-in-the-middle.** At n=128, k=8 it needs C(128,4) = 1.07×10⁷ entries (about 85 MB), roughly the chip's 80 MB of scratchpad. It is a distributed hash join that exercises the SRAM and the mesh.

**Caveat.** A 16-core host divides the CPU column by about 16. On the tensor path the ET's lead over a whole host is then roughly 4–5× (E). The stronger claim is energy: 0.3 pJ per int8 MAC above idle (M).
