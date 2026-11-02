# e136: a large GEMM on the ET-SoC-1, its power, clock, rate and die predicted first (Q137)

The registration is [`E136.md`](E136.md), with the classified list of every device command the run sends; the frozen numbers are `predictions-e136.json`
and `.txt`, written by `make_predictions_e136.py` from E107's, E119's, E126's, E95's, E101's, E111's and E133's committed records through E119's own
prediction module. It answers the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 1 ("a
large GEMM itself, which needs its own reuse per L2-sized block and its footprint, C included").

- [`rgm136/`](rgm136/README.md): the binary, E107's `rgm107` plus `SP_GEMM_LARGE` (the vendor's pattern as a large GEMM). Built on aifoundry2 into
  `build/e136` (`logs/build.txt`).
- [`desk/reuse_e136.py`](desk/reuse_e136.py): the GEMM's reuse per L2-sized block, its footprint, and where its missing lines are served (E105's L2 model, a
  tile-level L3), into `reuse_e136.txt` and `.json`.
- `make_protocol_e136.py`: `protocol.json`, `protocol-dry.json`, printed in `protocol.txt` (the order, the admission table, the smoke, the stops).
- `run_e136.py`: E119's `run_e119.py` imported and run unchanged, after a preflight that refuses the session unless the three binaries are the registered ones.
- `queue_e136.py`: E126's queue with E136's names.
- `reduce_e136.py`: E126's collect() and E119's clock_x, then the rules R0-R8 and the prediction errors. `selftest_e136.py` (`selftest.txt`).
- `dry-reduce.txt`: a toy-card dry session (blocks SMOKE, A, B) through `run_e136.py` and `reduce_e136.py`, no device. `logs/dmcmd-audit.txt`: Q136(w)'s checker on the run chain.
