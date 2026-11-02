# e135: a GPU measured the same way, Horace He's kinds of numbers on a Modal A100-40GB

The registration is [`E135.md`](E135.md); the frozen numbers are `predictions-e135.json` and `.txt`, written by
`make_predictions_e135.py` from Q132(g)'s and E80's and E83's committed records. It answers item 2 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), "A GPU measured the same
way". The data and the results are in [`docs/reports/data/2026-11-02-e135-a100-kinds/`](../../../docs/reports/data/2026-11-02-e135-a100-kinds/).

- `e135_app.py`: the Modal app (pinned image, the NVML sampler, the kinds, the cells, Horace's protocol, the lower-cap
  arm with its restore, the plans for units A, B and the smoke S, the budget guard). `--mode dry` prints the plans and
  their cost and calls no GPU.
- `make_predictions_e135.py`: writes `predictions-e135.json` and `predictions-e135.txt`.
- `reduce_e135.py`: the reduction (windows, gaps, replicates, Horace's protocol, the lower cap) and the rules R1-R10.
  `selftest_e135.py` shows every rule holding and failing on made-up units (`selftest.txt`).
- `posthoc_e135.py`: the post-hoc views (no verdicts): the A100's cool-die ladder from the pre-boost readings, leakage
  at the cap, energy per multiply-add, and what the measured relation predicts at a 330 W limit. Sections 1-5 were
  committed with amendment A1, before the measured run; sections 6-7 after the data.

Rebuild the predictions and the selftest from this directory with Python 3 and no third-party modules:
`python3 make_predictions_e135.py && python3 selftest_e135.py > selftest.txt`. The app needs the Modal client
(1.5.5 here) and a Modal workspace; nothing in this directory holds a token.
