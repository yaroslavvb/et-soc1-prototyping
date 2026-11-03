# e149: the GPU sanity check of the ET-SoC-1 power model, on Modal A100-40GB boards under the cap

The registration is [`E149.md`](E149.md). It answers the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6 ("a power model
across kinds") on a GPU, and the under-the-cap part of item 2 ("a GPU measured the same way") that E135 left. The data
and results are in [`docs/reports/data/2026-11-02-e149-gpu-model-check/`](../../../docs/reports/data/2026-11-02-e149-gpu-model-check/).

- `e149_app.py`: the Modal app (E135's pinned image and NVML sampler; the 92 stage-1 kinds and 21 stage-2 kinds and
  their seeded generators; the operand-bit features; the reference-bracketed windows, the heat holds, the plans for
  units A, B and the smoke S; the budget guard). `--mode dry` prints the plans and their cost and calls no GPU.
- `analyze_e149.py`: `reduce` (windows -> watts over zeros per kind, validity from the clock and the clock-event
  reasons), `fit` (the six registered models, nested leave-one-kind-out, the lag scan, the two-pole heat model, the
  leakage slope, the frozen bands, stage 1's rules) -> `model-e149.json`, `predict` (stage 2's kinds from the frozen
  file), `score` (the blind power and heat rules). Needs numpy.
- `selftest_e149.py`: synthetic logs in the harness's format through the whole chain (`selftest.txt`).

Run the selftest from this directory: `python selftest_e149.py <scratch dir> > selftest.txt` (Python 3 with numpy and the
Modal client installed, for the app's kind tables; it calls nothing remote). Nothing in this directory holds a token.
