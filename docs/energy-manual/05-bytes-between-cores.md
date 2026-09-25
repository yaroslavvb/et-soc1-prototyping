# 5. Bytes between cores and shires

Register file to register file over the tensor network (`TensorSend`/`TensorRecv`), 1 KB messages unless said otherwise, hart 0 of every minion sending and receiving in rings, at 600 MHz and 518 mV. Shire IDs do not follow the mesh, so each ring between shires is given with its mean distance in mesh hops, the Manhattan distance between shire s and shire s + k averaged over all 32 compute shires on the shire map of [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication) (checked against latency on aifoundry2).

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2" and "a3" are aifoundry2 and aifoundry3, each as its own mean ± its pass-to-pass standard error. The rings were re-measured on 23 September with the manual's own sampler, three passes on each card, the die held warm on aifoundry2. The pair of 18 September runs on aifoundry2, sampled without the die temperature and so without a leakage correction, is not pooled; against aifoundry2's own new passes the values On-chip communication publishes from it read −1% to +22% (median +10%). **On aifoundry2 the s ↔ s+16 ring starves the service processor's own management path** — the sampler's latency rises from 22 ms to 76–146 ms and the board reading takes a new value about twice a second instead of six times — so its aifoundry2 passes were dropped and that row is aifoundry3 only, where the sampler stays at 22 ms (On-chip communication gives 14.3 pJ/B for it on aifoundry2 on 18 September).

| Ring | What moves | Mesh hops, mean (range) | pJ/B | per card | GB/s aggregate |
|---|---|---|---|---|---|
| pair | 1 KB messages between the two minions of each pair, inside a neighbourhood | 0 | **0.67** [0.61–0.73] | a2: 0.63 ± 0.02 · a3: 0.70 ± 0.02 | 2,992 |
| neigh | 1 KB messages around rings of 8 (a neighbourhood) | 0 | **2.11** [1.86–2.25] | a2: 2.22 ± 0.03 · a3: 1.99 ± 0.07 | 1,120 |
| shire | 1 KB messages around rings of 32 (a shire) | 0 | **2.08** [1.93–2.16] | a2: 2.05 ± 0.06 · a3: 2.12 ± 0.03 | 1,120 |
| xshire8 | 1 KB messages around rings of 4 shires, 8 IDs apart | 1.6 (1–7) | **11.87** [10.55–12.79] | a2: 11.37 ± 0.72 · a3: 12.38 ± 0.14 | 150 |
| xshire16 | 1 KB messages between shires s and s+16 | 2.1 (1–6) | **13.27** [12.20–13.81] | a3: 13.27 ± 0.53 | 156 |
| xshire1 | 1 KB messages from each minion to the same minion of the next shire ID | 3.5 (1–10) | **14.92** [14.20–15.44] | a2: 15.40 ± 0.02 · a3: 14.44 ± 0.12 | 124 |
| xshire4 | 1 KB messages around rings of 8 shires, 4 IDs apart | 3.7 (1–8) | **15.57** [14.46–16.22] | a2: 15.64 ± 0.59 · a3: 15.51 ± 0.17 | 91 |
| xshire2 | 1 KB messages around rings of 16 shires, 2 IDs apart | 4.5 (2–7) | **17.77** [17.03–18.36] | a2: 18.32 ± 0.03 · a3: 17.22 ± 0.11 | 87 |
| xshire6 | 1 KB messages around rings of 16 shires, 6 IDs apart | 4.7 (3–8) | **16.75** [14.59–19.66] | a2: 17.98 ± 0.91 · a3: 15.51 ± 0.73 | 89 |
| shire-c4 | 128 B messages around rings of 32 (a shire) | 0 | **3.26** [2.52–3.63] | a2: 3.41 ± 0.15 · a3: 3.11 ± 0.31 | 553 |
| xshire1-c4 | 128 B messages from each minion to the same minion of the next shire ID | 3.5 (1–10) | **18.92** [17.18–20.88] | a2: 19.80 ± 0.57 · a3: 18.04 ± 0.86 | 112 |

## Handing a slab to the next shire through its scratchpad (E25)
The relay was measured on 22 September on aifoundry2 and re-run on 23 September, three warm passes on aifoundry2 and four on aifoundry3 (n = 8). A stage reads a slab, adds 1 and writes it where the next stage reads it; the next shire is shire s − 1 by ID, 3.5 (1–10) mesh hops away.

| Medium | pJ per byte (read + write) | per card | GB/s on the card |
|---|---|---|---|
| Write to DRAM, read back | **105.7** [99.5–111.0] | a2: 102.1 ± 1.3 · a3: 109.3 ± 1.5 | 50 |
| Write where the next shire reads it | **8.6** [7.8–9.2] | a2: 9.1 ± 0.1 · a3: 8.1 ± 0.1 | 594 |
| Keep it in this shire's scratchpad | **4.0** [3.9–4.2] | a2: 4.0 ± 0.1 · a3: 4.0 ± 0.01 | 1,503 |

**What the tables say.**
- **Between the two minions of a pair a byte costs under a picojoule** (0.67 pJ); around a neighbourhood or a shire about 2.1 pJ; across the mesh 12–18 pJ. A straight line through the 1 KB rings between shires against their mean distances (the five both cards measured, 1.6–4.7 hops) gives 7.6 pJ to leave the shire plus 2.3 pJ per mesh hop on aifoundry2 and 10.2 plus 1.3 on aifoundry3; [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) measures 1.5 pJ/B per hop on the mesh rail and 2.2 on board power directly. **Leaving the shire is the biggest single step ([4.3](04a-fine-grain.md)'s wire fit shows it on both cards), but the hops after it are not free.**
- Small messages cost more per byte in the 128 B rows, a difference resolved so far only on aifoundry2's shire ring; the per-message overhead is 40–224 cycles of the sending and receiving harts ([On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication), one session on aifoundry2).
- **Handing a slab to the next shire through its scratchpad costs 11.3× less than the DRAM round trip on aifoundry2 and 13.5× less on aifoundry3** (9.1 and 8.1 pJ/B for the write and the read together), and sits between the in-shire and cross-mesh tensor-network figures.
- The three relay bars are ±4–8%: the hop relay's is mostly the difference between the cards, and the others are a 4–5 W signal over a board idle that drifts, the DRAM relay's power also riding on a path with no rail sensor.

Sources: `docs/reports/data/2026-09-18-nocbench-aifoundry2/energy-a/results.json`, `docs/reports/data/2026-09-18-nocbench-aifoundry2/energy-b/results.json`, `docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json`, `docs/reports/data/2026-09-23-energy-manual/reruns.json`; mesh hops from [marty1885](https://github.com/marty1885/etTopoScan)'s shire map as `workloads/nocbench/analyze.py` holds it.
