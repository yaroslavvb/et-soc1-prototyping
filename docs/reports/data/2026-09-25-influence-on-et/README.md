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
| Tensor-load bandwidth and pJ/B above idle, own scratchpad and DRAM, random data, both cards | `../2026-09-23-energy-manual/manual.json`: `catalogue.combined["tload/scp/random"]`, `["tload/dram/random"]`; `catalogue.cards.<card>.summary[...].bytes_per_s` |
| Board power at rest (aifoundry3 cool, aifoundry2 hot) | same file, `cards.idle`, `cards.launch` (temperatures) |
| Packed-integer vector instruction energy and rate (for the 1-bit SWAR estimate) | same file, `catalogue.combined["fxor.pi/random/h2"]` and three others; `catalogue.cards.<card>.summary["fxor.pi/random/h2"].ops_per_s` |
| Spread global atomics: rate and energy | same file, `sync.atomics.runs[label=spread]`, `reruns.hotline_nj_per_op.spread` |
| Matmul peak rates and board power, fp32/fp16/int8, aifoundry2 | `../2026-09-18-aifoundry2/results.json`: `results[*]`, `idle_w` |
| The batch-1 1024×4096 fp32 layer in the scratchpads (S1's anchor), aifoundry3, one run | `../2026-09-18-sparsity-aifoundry3/energy-b/results.json` (`gemv-skip-0`), `gemv-tree-dense.jsonl` |
| Chip-wide allreduce, 32 B, 1,024 minions, aifoundry2 | `../2026-09-18-nocbench-aifoundry2/xallreduce-c1.jsonl` |

Stated in the producer with a source rather than read: the usable scratchpad (32 × 2.25 MB, from the on-chip relay
report), the host launch (0.2–0.4 ms, sparse-compute report), PCIe and DRAM capacity (spec); the H100's datasheet
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
E_pass/Q (already in the server). The energy rule max(), not sum, is the one that reproduces the anchor: 71 µJ
modelled against 68 µJ measured above idle (the anchor is checked on its matrix bytes; its own layout splits rows
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
