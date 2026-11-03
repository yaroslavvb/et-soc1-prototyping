# e162: which operand pairing a GPU pays for, row against K, on Modal A100-40GB and L40S boards under the cap

The registration is [`E162.md`](E162.md). It answers the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 2 ("a GPU measured
the same way") in the form Q138's final critic ranked 9th: which operand pairing an A100 pays for, and a later generation
with headroom under its cap. The data and results are in
[`docs/reports/data/2026-11-03-e162-gpu-row-k/`](../../../docs/reports/data/2026-11-03-e162-gpu-row-k/).

- `e162_app.py`: the Modal app, E149's harness with the changes its docstring lists: E162's row-against-K kinds and
  held-out kinds, E149's kinds under E149's seeds, the row-lag features, two GPU types with a board guard, the L40S smoke,
  stage-1 and stage-2 plans. `python -c "import e162_app; e162_app.dry_report()"` prints the plans and their cost and
  calls nothing remote.
- `analyze_e162.py`: `reduce` (E149's reduction, with the validity clock as a parameter), `choose` (the L40S smoke's
  size rule), `freezeA` / `freezeL` (the ridge row+K form RK with its scan and fully nested error, G1's form and the
  comparisons, the pairing rules, the frozen predictions), `score` (BEAT, STABLE, the heat cells, the secondary arms).
  It imports `tools/gpu/e149/analyze_e149.py` and reads E149's frozen files unchanged. Needs numpy.
- `selftest_e162.py`: the reduction against E149's committed logs, and the RK procedure and the rules on synthetic
  features (`selftest.txt`). Run from this directory: `python selftest_e162.py > selftest.txt`.

Nothing in this directory holds a token; Modal's client reads its own from the machine's profile.
