# Influence functions on the ET-SoC-1: the numbers behind the page (25 September 2026)

Data for the exploratory report "Influence functions on the ET-SoC-1" (`docs/reports/2026-09-25-influence-on-et.html`,
built from `docs/reports/sources/influence-on-et.{body.html,script.js,meta.json}`; slug when published:
`et-soc1-influence-functions`). **Desk analysis: no card was run for it.** The question came from the author of the
influence-functions report (<https://spacesheep.dev/@yaroslavvb/influence-functions-hessians-sketching-weak-factoring>):
which steps of large-scale influence-function work could the ET-SoC-1 speed up, perhaps finding the most influential
training examples. The answer: none of the bill; two narrow research items (S1, a static shard scored from SRAM; S2, an
MNIST-sized pipeline on one chip) and one measurement (S3, gather/scatter rates). The page is meant for the
research/exploratory group of the set, next to the sparse-compute report it builds on.

| File | What it is |
|---|---|
| `make_analysis.py` | The producer. Reads the measured ET-SoC-1 numbers from this repository's data files (below), states every spec, published, owner and estimated constant with its source, evaluates the page's scoring model on the reference cases and writes `analysis.json`. Prints the anchor check and the reference cases. |
| `analysis.json` | Everything the page shows: `model` (the constants the explorer runs on, each with a kind `k` and a source `src`), `s1` (the shard cases, capacity, parity in Q), `duty` (idle against the pass, break-even arrival rates), `kills` (K1, K4, K5, K7), `s2` (the atlas scan), `dense` (dense gradient work, ET against H100), `pipeline` (the steps of the dot plot), `presets`, `topk_inserts`, and `kinds` (the tag legend). |

**Measured inputs read by the producer** (kind M, or D when the producer does arithmetic on them):

| Quantity | File and field |
|---|---|
| Tensor-load bandwidth and pJ/B above idle, own scratchpad and DRAM, random data, every card of the catalogue (three since 26 September) | `../2026-09-23-energy-manual/manual.json`: `catalogue.combined["tload/scp/random"]`, `["tload/dram/random"]`; `catalogue.cards.<card>.summary[...].bytes_per_s` |
| Board power at rest (aifoundry3 cool, aifoundry2 hot) | same file, `cards.idle`, `cards.launch` (temperatures) |
| Packed-integer vector instruction energy and rate (for the 1-bit SWAR estimate) | same file, `catalogue.combined["fxor.pi/random/h2"]` and three others; `catalogue.cards.<card>.summary["fxor.pi/random/h2"].ops_per_s` |
| Spread global atomics: rate and energy | same file, `sync.atomics.runs[label=spread]`, `reruns.hotline_nj_per_op.spread` |
| Matmul peak rates and board power, fp32/fp16/int8, aifoundry2; energy per op above the idle just before each workload | `../2026-09-18-aifoundry2/results.json`: `results[*]`; the idle before each workload from `power.csv` and `runs.jsonl` (`idle_before()` of `scripts/mmbench-report-data.py`: 30.61, 32.53, 33.83 W), not `idle_w` |
| Board power of the tensor unit on random operands, fp16 and fp32 (dense work, S2), aifoundry2 at 80 °C | `../2026-09-23-energy-manual/manual.json`: `tensor.rows[config=fp16_randn, fp32_randn]` (`idle_w` + `over_idle_w`) |
| S3: gathers, scatters, scatter-add and packed atomics, per element or update, both harts of 1,024 minions, three cards (E48) | same file, `gs.configs["gs/E/<op>/<table>/rand/<data>/h2/mff/n1024"]` (`elements_per_s`, `pj_per_element`), written as `model.et.gs` |
| The board meter's refresh per card and the rails' running average | same file, `v3.refresh_ms.<card>.sampler_10hz`, `catalogue.rail_filter.<card>.tau_s` (`model.et.meter`) |
| The batch-1 1024×4096 fp32 layer in the scratchpads (S1's anchor), aifoundry3, one run | `../2026-09-18-sparsity-aifoundry3/energy-b/results.json` (`gemv-skip-0`: joules per layer, and layers per second at 600 MHz for its time, 7.36 µs) |
| Chip-wide allreduce, 32 B, 1,024 minions, aifoundry2 | `../2026-09-18-nocbench-aifoundry2/xallreduce-c1.jsonl` |
| The host link, three cards (E50, 27 September): host to card at 256 MB with the DMA alone and as a program's staged copy, and an empty kernel on 32 shires launched and waited for (section 4, the first experiment's prerequisite); K1's 64 MB copy at the rates of the copy size nearest it (64 MiB); S2's host launch, and each launch queued back to back | `../2026-09-27-pcie/pcie.json`: `bw.<card>.h2d.{dma,staged}[largest].gbs.mean`, `launch.<card>.single_us["32"].mean` (`model.et.pcie`); `bw.<card>.h2d.{dma,staged}[64 MiB].gbs.mean` (`kills.k1.pcie_*`); `launch.<card>.{single_us,b2b_us}["32"].mean` (`model.et.launch_ms`) |
| Board power at rest of the card the model's idle range leaves out (aifoundry1-c1), for the explorer's note | `../2026-09-23-energy-manual/manual.json`: `v3.idle.bins.<card>.bins` (`model.et.idle_W_other`) |

Stated in the producer with a source rather than read: the usable scratchpad (32 × 2.25 MB, from the on-chip relay
report), the PCIe line rate and DRAM capacity (spec); the H100's datasheet
rates, the A100 energies per bit by level (Antepara et al., SC'25, via the memory-hierarchy report's notes) and every
H100 and host-CPU assumption (kind E); the author's 8B cost model and MNIST atlas costs (kind O, from his pages).

**The model** (the page's section 6 states it in words; `make_analysis.py` and the page script implement the same):
one pass of Q queries over N codes of k coordinates reads B = N·k·bytes and does 2QNk operations. ET: chips =
⌈B / 72 MB⌉ (SRAM) or ⌈B / 32 GB⌉ (DRAM); a minion's 3 KB L1 scratchpad cannot hold a query, so every minion also
re-reads the Q queries from SRAM once per tile of 16 codes it holds, B_q = 1,024·chips·⌈N/(1,024·chips·16)⌉·Q·k·bytes (E);
time = max(load, compute); energy above idle = max(bytes·pJ/B, ops·pJ/op). H100: L2 if B ≤ 37.5 MB (4.3 TB/s, 37.7
pJ/B), else HBM (3.0 TB/s, 105 pJ/B): the A100's per-level energies, not its whole path through L2 and L1 (50 and
155 pJ/B, recorded as `path` and not used); 80 GB per GPU, 60% of tensor peak, 1.3 µs launch, idle 60–90 W; 1-bit
work at an xor, a popc and an add per 32 bits, each at one fp32 lane-operation's energy at the TDP (1.75 pJ per bit).
Energy per query at arrival rate λ: ET = chips·P_idle/λ + E_above/Q (a dedicated card); H100 and host CPU =
E_pass/Q (already in the server). The energy rule max(), not sum, is the one that reproduces the anchor: 74 µJ
modelled against 68 µJ measured above idle (71 µJ on the two-card data of 25 September) (the anchor is checked on its matrix bytes; its own layout splits rows
across minions). `kills` holds the numbers the page quotes for K1, K4, K5 and K7, from the same model.

**Reproduce**

```bash
python3 docs/reports/data/2026-09-25-influence-on-et/make_analysis.py
python3 scripts/build-report.py influence-on-et docs/reports/data/2026-09-25-influence-on-et/analysis.json \
    docs/reports/2026-09-25-influence-on-et.html
```

The research notes and the two desk maps the page was distilled from, and the skeptical pass that ranked their
candidates, were working files of the session and are not committed; the page's section 6 lists the corrections that
pass made.

**Corrections folded in** (moved here from the page's section 6 on 27 September) from the two desk maps the page started
from: the atlas comparison is against its measured 0.231 s scan, not the 0.558 s gradient-pass primitive (so the ET is
slower, not 45–140× faster); the atlas uses tanh, so its hidden activations have no exact zeros, and its scan is
4.1×10¹² FLOP, not 4.2×10¹¹; the "one row costs a full 16-row op" figure was a measurement of masked rows, not of smaller
ops; the top-k state was over-sized for the SRAM; a ±1 energy lead compared energy above idle with board energy;
per-query shortlists are not resident; the 0.2–0.4 ms host launch was ignored in a latency claim; a posting-list rate was
halved. The rest of their arithmetic reproduced. A later check of the page charged the H100 the A100's per-level energies
only (the first draft's upper end used the whole path and gave a 7–13× lead), added the query tiles each minion re-reads,
re-priced the H100's 1-bit work per instruction rather than at its full power, and computed K1, K4, K5 and K7 from the
same model.

**27 September.** S3 was measured (E48: gathers, scatters, scatter-add and packed atomics on three cards, 26 September;
the energy manual's §4.4 and §6), so `model.et.gs` carries its rates and energies and the page's S3, K3, K6 and section 6
quote them. The review's TODO items for this page were applied at the same time: the dense energy and S2 use the tensor
unit's board power on random operands (CMP-1), the anchor's time is the energy run's own rate at 600 MHz (7.36 µs, 2.3
TB/s, CMP-2), "72 MB of on-chip SRAM" became the scratchpads' 72 MB usable of 80 MB (CMP-5), the per-op energies
subtract each workload's own idle (int8 0.39 pJ, fp16 1.41 pJ; CMP-6), and S1's L2 lead prints one decimal (CMP-7).
The measured inputs now come from the energy manual's three-card data, which moved the model's scratchpad energy from
4.21 to 4.43 pJ/B and the anchor's model to 9% above the measured 68 µJ.

**Later on 27 September.** The host link was timed on the three cards (E50, the PCIe page), so K1's copy over PCIe, the
pipeline's two link notes, section 4 and the first experiment's prerequisite use its rates (`model.et.pcie`; K1's 64 MB
takes 5.4 ms with the DMA alone and 8.4–12.0 ms as a program's staged copy at the rates measured for a 64 MiB copy,
where the Gen4 x8 line rate gave 4.1 ms; a first version applied the 256 MB copy's rate, 5.1 and 8.2–12.3 ms). S2's
host launch (`model.et.launch_ms`) is E50's too: 0.56–0.57 ms launched and waited for, 0.10 ms each queued back to
back, in place of the sparse-compute report's first figure, 0.2–0.4 ms on aifoundry3. The
idle-to-pass ratio (`duty.ratio_idle_to_active`) now takes the same card's idle on both sides (it had paired
aifoundry3's idle with aifoundry2's pass energy and back: 19,000–36,000, now 25,000–27,000). `experiment` holds the first
experiment's pass and kill rule, which the page's section 5 draws against `s1.hbm_case` and `s1.hbm_case_rows16`.
