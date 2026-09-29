# Sparse parity on aifoundry3's card: M1, the hand-off probe, M2 and a first all-shire run (29 September 2026, 04:15-04:30 PDT)

Kernel `.text` sha256 `68b3f273…` (`build/sparseparity-f`, commit `92b168f`'s sources). Every process held the card
lock, ran under `timeout 10` and checked `et-who` first. Logs: `sparseparity-m1.log`, `sparseparity-probe.log`,
`sparseparity-m2.log`; per-step JSON and records in `runs/`.

- **M1 (one minion; `card_run.sh m1`), every step as expected:** C0 scalar and tensor exact against the CPU (all 4,960
  correlations), the three negative controls caught (both checksums fail), the tie instance flagged, C1 on 32
  minions for seeds 1-20 solved with exact checksums. One minion at the L1/L2 geometry: 411-470 cycles per tensor op
  (the design's target 270-330).
- **Probe (`card_run.sh probe`):** narrow tiles on scratchpad and DRAM staging, 1 and 2 buffers: every result exact
  (no hand-off race seen); narrow tiles are bound by hart 1's row generation (hart 0 waits ~85% of its cycles).
- **M2 (one shire; `card_run.sh m2`):** cycles per op 428 (1 minion), 432, 443, 451, 462, 503 (32 minions): the
  shire's bandwidth is not the limit at this size. Full L1 on one shire: solved, closed-form checksums exact, 6.37 s
  (model 2.3 s; slowest minion 1.58x the median). L2, (256,5) and L5 slices exact at 616-934 cycles per op.
  `--nowait-a` (skipping the wait the manual requires) gave a wrong result: the wait is needed.
- **M3, first all-shire runs (`runs/m3-manual-*`; 32 shires x 32 minions = 1,024 minions):**

  | Instance | Candidates | Card launch | Result | CPU 1 core | CPU 6 threads, best |
  |---|---|---|---|---|---|
  | L1 (512, 4, 0.3, 448) | 2.83e9 | 0.204 s | secret found, unique; checksums exact; oracle exact on 17 sampled minions | 1.06 s | 0.18 s (vexh), 0.148 s expected (MITM) |
  | L2 (512, 4, 0.4, 1850) | 2.83e9 | 0.807 s | secret found, unique; checksums exact; oracle exact on 8 sampled minions | 3.95 s | 0.693 s one-stage, 0.459 s two-stage |

  The busiest minion ran at 1,564-1,644 cycles per op (6x the target) and the slowest minion took 1.56-1.63x the
  median: hart 1's row generation starves hart 0, and the planner's generation cost (800 cycles per slice, assumed)
  is low. So the card is ~5x one CPU core and on par with 6 tuned AVX-512 threads so far; the tensor path has ~5x
  headroom (M4).
