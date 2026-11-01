# e107: where a large GEMM falls, by reuse and by the L3 (Q133)

The registration is [`E107.md`](E107.md); the frozen numbers are `predictions-e107.json` and `.txt`, written by `make_predictions_e107.py` from E105's and E101's committed aifoundry3 records. It answers the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 1, as of `1fe8377a18af`.

- `rgm107/`: the binary, E105's `rgm105` plus block repeats and a shared C. Built into `build/e107`.
- `e107_common.py`: the arms, the 75 items and the per-pass order.
- `run_e107.py`, `block_e107.sh`: E78's runner and E101's block, unchanged in what they do, with E107's items; `queue_e107.sh` runs the three passes detached with the deadline rule; `watch_e107.py` ends a pass at 80 W on three board samples.
- `reduce_e107.py` (`reduce_e78.py`, byte-identical, with E107's items), `rails_e107.py` (SRAM and NoC rails, DDR droop), `score_e107.py` (the rules into `scored.json` and `results.md`), `selftest_e107.py` (`selftest.txt`).
- `sim-check.txt`: what sys_emu could and could not check. `desk/`: the desk check of E105's and E101's rails that set R4c.
