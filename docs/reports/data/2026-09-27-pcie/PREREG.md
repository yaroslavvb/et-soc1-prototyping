# PCIe link and launch path: predictions stated before the runs (2026-09-27, 14:19 PDT)

Written before any timed transfer or launch on any card. The only card facts known when writing: the negotiated
link on every card is 16.0 GT/s x8 (`et-lab-manifest` / sysfs `current_link_speed`, `current_link_width`, read at
14:13), the IOMMU is in translated mode (`DMA-FQ`) on all three hosts, and the runtime source
(external/et-platform, esperanto-tools-libs): the response receiver thread polls the completion queue, sleeping
**50 µs** between polls while commands are in flight and **500 µs** when none are (`ResponseReceiver.cpp`,
`kResponsePollingIntervalWithEventsOnFly`, `kResponsePollingIntervalNoEventsOnFly`); user memory is always staged
through a CMA bounce buffer (`MemcpyH2DAction.cpp`), and a barrier is a device-side flag
(`CMD_FLAGS_BARRIER_ENABLE`). The firmware has 4 DMA read and 4 DMA write channels, one per command
(`pcie_dma.h`, `dmaw.c`). aifoundry3's `libetrt.so` is a patched build and aifoundry1's a fork build, so their
receiver constants may differ: the latency predictions are for the stock constants.

## The tool, the schedule, the reduction

- `workloads/pciebench` (runtime API only): `--test info|bw|lat|launch|conc|hostcopy`, each process `timeout 10`
  with `--budget 8.5`, under the card's lock (`flock -n /run/lock/etsoc-shire<N>.lock`).
- **staged** = the API's normal path (the runtime's bounce copy + DMA); **dma** = the same DMA commands with the
  bounce copy replaced by a no-op through the API's `cmaCopyFunction` hook (the analogue of pinned memory).
- A **run** on a card = info, bw (4 KB-256 MB in x2 steps, both directions, staged and dma, interleaved), lat,
  launch, conc, and hostcopy (host only). **Five runs per card**, at least 10 minutes apart, the three cards
  interleaved: aifoundry2, aifoundry3, aifoundry1 card 1 (`ET_DEVICES=1`; card 0 is never opened).
- Units: sizes binary (1 MB = 2^20 B); bandwidth decimal (GB/s = 10^9 B/s), as the link figure is.
  Link figure: 16 GT/s x 8 lanes x 128/130 / 8 = **15.75 GB/s per direction**.
- A run's value for a cell = the median of its repeats. A card's value = the mean of its runs' values with a
  **99% t-interval** (n = 5: t = 4.604).
- **PASS** if the card's 99% interval lies inside the predicted range (for a direction: excludes 0 on the predicted
  side), **FAIL** if it lies entirely outside (or excludes 0 on the other side), otherwise **INCONCLUSIVE**.
  Each prediction is judged per card; a failed prediction is reported as failed and the page takes the measured value.

## Predictions

| ID | Quantity | Prediction | Why |
|---|---|---|---|
| P1 | H2D bandwidth, dma, 256 MB | **9.0-14.2 GB/s** (57-90% of 15.75; point guess 11.5) | Gen4 x8 with 128-256 B payloads leaves 83-91% after TLP overhead; device reads wait for completions; GPUs reach ~80% |
| P2 | D2H bandwidth, dma, 256 MB | **9.0-14.2 GB/s** (point guess 12) | same link; device writes are posted |
| P3 | D2H vs H2D, dma, 256 MB | **D2H > H2D** | posted writes against non-posted reads |
| P4 | staged / dma, 256 MB, each direction | **0.50-0.95** | the bounce copy (4 threads) overlaps the DMA of the previous chunk, but not fully |
| P5 | n1/2: the size where H2D dma bandwidth reaches half its 256 MB value | **128 KB-4 MB** | a fixed cost of 30-150 µs per transfer (issue, DMA set-up, the receiver's poll) times ~11 GB/s |
| P6 | round trip, 4 KB, staged, H2D (issue to event) | **60-700 µs** median | the wire time is 0.3 µs; the receiver's 50 µs / 500 µs polling and the thread wake-ups set it |
| P7 | round trip, 64 B vs 4 KB (staged H2D) | **differ by < 25 µs** | size-independent at this scale |
| P8 | empty kernel, 32 shires, launch to completion | **80-1,000 µs** median | the same polling, plus the firmware's dispatch to 32 shires and the gather of their completions |
| P9 | empty kernel, 32 shires, back-to-back (100 queued, per launch) | **5-300 µs**, and **below P8's value** | the barrier is on the device, so the host's polling drops out between queued launches |
| P10 | back-to-back per launch: 32 shires vs 1 | **32 > 1** | more shires to start and to gather |
| P11 | H2D + D2H at once (dma, two streams, 2 x 64 MB each) | aggregate **>= 1.5x** the faster single direction | the link is full duplex and reads and writes use separate DMA channels |
| P12 | two H2D streams at once (dma) | aggregate **<= 1.25x** one H2D stream | one stream already fills most of the link |
| P13 | the three cards, dma 256 MB, each direction | card values **within 10%** of their mean | same link and DMA engine; hosts, firmware and runtime builds differ |

Not predicted (reported as measured): the staged path's small-size behaviour, the idle-stream wait, the first launch
after loading, the pipelined 4 KB copies, the host memcpy bandwidth.
