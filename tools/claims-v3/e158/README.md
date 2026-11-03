# e158: a large GEMM's time per op as the L3's retention by reuse distance (Q139)

The registration is [`E158.md`](E158.md), with the classified list of every device command the run sends; the frozen numbers are `predictions-e158.json`
and `.txt`, written by `make_predictions_e158.py` from E146's frozen line prices (MAB), E119's c1 and E146's committed ladder, through `model_e158.py`. It
answers the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 1, and rank 7 of Q138's final
critic: E146 found a large GEMM's remaining time error in where its lines are served, and asked for an L3 retention curve by reuse distance.

- The binary is E136's [`rgm136`](../e136/rgm136/README.md), unchanged (`build/e136` on aifoundry2): every shape is an argument, `gemmL<MB>x<NB>x<KB>`.
- [`desk/reuse_e158.py`](desk/reuse_e158.py): every L2-missing line's exact LRU stack distance in the L3, operand and C tiles apart, from E136's L2 model and
  E146's L3 step order (imported unchanged; it reproduces E146's splits on E146's nine shapes before it writes), into `reuse_e158.txt` and `.json`.
- `model_e158.py`: MAB's form and frozen prices with the lines a retention curve leaves; the far-B share; the two fits (ISO, the registered primary, and LOGI).
- `make_protocol_e158.py`: `protocol.json`, `protocol-dry.json`, the two stop-path tests `protocol-stoptest-{board,die}.json` (and their dry twins), printed
  in `protocol.txt`.
- `run_e158.py`: E146's preflight (the three binaries are E136's registered ones) and E158's stop limits (board stop at most 85 W, admission limit at most
  82 W), then E119's `run_e119.py`, imported and run unchanged.
- `queue_e158.py`: E146's queue with its names changed and nothing else (the stop-path tests between the smoke and the session; the queue halts unless both
  stops fire on live samples).
- `reduce_e158.py`: E126's collect() and E119's clock_x, then the shares, the fits and the rules R0-R8. `selftest_e158.py` (`selftest.txt`).
- `logs/dry-queue.txt`, `dry-reduce.txt`: a toy-card dry run of the whole queue (smoke, both stop tests, the session) through `run_e158.py` and
  `reduce_e158.py`, no device. `logs/dmcmd-audit.txt`: Q136(w)'s checker on the run chain.
