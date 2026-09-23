# 5. Bytes between cores and shires

Register file to register file over the tensor network (`TensorSend`/`TensorRecv`), 1 KB messages unless said otherwise, hart 0 of every minion sending and receiving in rings, at 600 MHz and 518 mV. Two independent runs averaged; ± is half their difference.

| Ring | What moves | pJ/B | GB/s aggregate |
|---|---|---|---|
| pair | 1 KB messages between the two minions of each pair, inside a neighbourhood | **0.80** ± 0.04 | 2992 |
| neigh | 1 KB messages around rings of 8 (a neighbourhood) | **2.31** ± 0.14 | 1120 |
| shire | 1 KB messages around rings of 32 (a shire) | **2.34** ± 0.06 | 1120 |
| xshire1 | 1 KB messages from each minion to the same minion of the next shire ID | **15.84** ± 0.81 | 124 |
| xshire16 | 1 KB messages between shires s and s+16 | **14.65** ± 1.09 | 156 |
| xshire8 | 1 KB messages around rings of 4 shires, 8 IDs apart | **13.86** ± 0.11 | 150 |
| xshire2 | 1 KB messages around rings of 16 shires, 2 IDs apart | **18.92** ± 0.05 | 87 |
| xshire4 | 1 KB messages around rings of 8 shires, 4 IDs apart | **17.57** ± 0.33 | 91 |
| xshire6 | 1 KB messages around rings of 16 shires, 6 IDs apart | **20.35** ± 1.27 | 89 |
| shire-c4 | 128 B messages around rings of 32 (a shire) | **4.00** ± 0.31 | 553 |
| xshire1-c4 | 128 B messages from each minion to the same minion of the next shire ID | **21.71** ± 1.11 | 112 |

## Handing a slab to another shire through its scratchpad (E25)

| Medium | pJ per byte (read + write) | GB/s on the card |
|---|---|---|
| Write to DRAM, read back | 104.8 | 50 |
| Write where the next shire reads it | **8.9** | 594 |
| Keep it in this shire's scratchpad | 4.2 | 1503 |

**What the tables say.**
- **Inside a neighbourhood a byte costs under a picojoule**; inside a shire about 2.3 pJ; across the mesh 14–22 pJ, roughly flat in distance. The step is leaving the shire, not the number of hops after that.
- Small messages cost more per byte (the 128 B rows): the per-message overhead is a few hundred cycles of the sending and receiving harts.
- **Handing a slab to the next shire through its scratchpad, 8.9 pJ/B for the write and the read together, is a twelfth of the energy of the DRAM round trip** and sits between the in-shire and cross-mesh tensor-network figures.

Sources: `docs/reports/data/2026-09-18-nocbench-aifoundry2/energy-a/results.json`, `docs/reports/data/2026-09-18-nocbench-aifoundry2/energy-b/results.json`, `docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json`.
