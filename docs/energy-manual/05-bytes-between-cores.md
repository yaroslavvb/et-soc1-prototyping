# 5. Bytes between cores and shires

Register file to register file over the tensor network (`TensorSend`/`TensorRecv`), 1 KB messages unless said otherwise, hart 0 of every minion sending and receiving in rings, at 600 MHz and 518 mV.

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2" and "a3" are aifoundry2 and aifoundry3, each as its own mean ± its pass-to-pass standard error. The rings were re-measured on 23 September with the manual's own sampler, 3 passes on each card, the die held warm on aifoundry2; the pair of 18 September runs, sampled without the die temperature, is not pooled and agrees to within 10%. **The s ↔ s+16 ring starves the service processor's own management path** — the sampler's latency triples and the board reading is held for seconds — so its aifoundry2 passes were dropped and that row is aifoundry3 only (its 18 September value on aifoundry2 was 14.7).

| Ring | What moves | pJ/B | per card | GB/s aggregate |
|---|---|---|---|---|
| pair | 1 KB messages between the two minions of each pair, inside a neighbourhood | **0.67** [0.61–0.73] | a2: 0.63 ± 0.02 · a3: 0.70 ± 0.02 | 2992 |
| neigh | 1 KB messages around rings of 8 (a neighbourhood) | **2.11** [1.86–2.25] | a2: 2.22 ± 0.03 · a3: 1.99 ± 0.07 | 1120 |
| shire | 1 KB messages around rings of 32 (a shire) | **2.08** [1.93–2.16] | a2: 2.05 ± 0.06 · a3: 2.12 ± 0.03 | 1120 |
| xshire1 | 1 KB messages from each minion to the same minion of the next shire ID | **14.92** [14.20–15.44] | a2: 15.40 ± 0.02 · a3: 14.44 ± 0.12 | 124 |
| xshire16 | 1 KB messages between shires s and s+16 | **13.27** [12.20–13.81] | a3: 13.27 ± 0.53 | 156 |
| xshire8 | 1 KB messages around rings of 4 shires, 8 IDs apart | **11.87** [10.55–12.79] | a2: 11.37 ± 0.72 · a3: 12.38 ± 0.14 | 150 |
| xshire2 | 1 KB messages around rings of 16 shires, 2 IDs apart | **17.77** [17.03–18.36] | a2: 18.32 ± 0.03 · a3: 17.22 ± 0.11 | 87 |
| xshire4 | 1 KB messages around rings of 8 shires, 4 IDs apart | **15.57** [14.46–16.22] | a2: 15.64 ± 0.59 · a3: 15.51 ± 0.17 | 91 |
| xshire6 | 1 KB messages around rings of 16 shires, 6 IDs apart | **16.75** [14.59–19.66] | a2: 17.98 ± 0.91 · a3: 15.51 ± 0.73 | 89 |
| shire-c4 | 128 B messages around rings of 32 (a shire) | **3.26** [2.52–3.63] | a2: 3.41 ± 0.15 · a3: 3.11 ± 0.31 | 553 |
| xshire1-c4 | 128 B messages from each minion to the same minion of the next shire ID | **18.92** [17.18–20.88] | a2: 19.80 ± 0.57 · a3: 18.04 ± 0.86 | 112 |

## Handing a slab to another shire through its scratchpad (E25)
 The relay was measured on 22 September and re-run three times on each card on 23 September (n = 8).

| Medium | pJ per byte (read + write) | per card | GB/s on the card |
|---|---|---|---|
| Write to DRAM, read back | **105.7** [99.5–111.0] | a2: 102.1 ± 1.3 · a3: 109.3 ± 1.5 | 50 |
| Write where the next shire reads it | **8.6** [7.8–9.2] | a2: 9.1 ± 0.1 · a3: 8.1 ± 0.1 | 594 |
| Keep it in this shire's scratchpad | **4.0** [3.9–4.2] | a2: 4.0 ± 0.1 · a3: 4.0 ± 0.0 | 1503 |

**What the tables say.**
- **Inside a neighbourhood a byte costs under a picojoule**; inside a shire about 2.1 pJ; across the mesh 12–18 pJ, roughly flat in distance. The step is leaving the shire, not the number of hops after that.
- Small messages cost more per byte (the 128 B rows): the per-message overhead is a few hundred cycles of the sending and receiving harts.
- **Handing a slab to the next shire through its scratchpad, 8.6 pJ/B for the write and the read together, costs 12× less than the DRAM round trip** and sits between the in-shire and cross-mesh tensor-network figures.
- The DRAM relay's bar is the widest of the three: its 4–5 W over idle rides on a DRAM path whose idle draw is not on any rail sensor, so the idle it is measured against is the board's, and the board's idle drifts.

Sources: `docs/reports/data/2026-09-18-nocbench-aifoundry2/energy-a/results.json`, `docs/reports/data/2026-09-18-nocbench-aifoundry2/energy-b/results.json`, `docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json`, `docs/reports/data/2026-09-23-energy-manual/reruns.json`.
