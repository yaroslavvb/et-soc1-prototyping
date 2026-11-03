# e146: a large GEMM's time per op with C's stores as a term, and what the stores cost in power (Q138)

The registration is [`E146.md`](E146.md), with the classified list of every device command the run sends; the frozen numbers are `predictions-e146.json`
and `.txt`, written by `make_predictions_e146.py` from E119's and E136's committed records (and E136's frozen power, governor and heat laws) through E136's
own prediction module. It answers the rest of the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
item 1: E136's time per op came out 7-13% faster than its law, and only C's store cadence, priced post hoc, explained part of it.

- The binary is E136's [`rgm136`](../e136/rgm136/README.md), unchanged (`build/e136` on aifoundry2): every shape is an argument, `gemmL<MB>x<NB>x<KB>`.
- [`desk/reuse_e146.py`](desk/reuse_e146.py): each shape's missing lines by operand (A, B) and place (L2, L3, fresh), and where C's stores land, from E136's
  L2 and L3 models, into `reuse_e146.txt` and `.json`.
- `make_protocol_e146.py`: `protocol.json`, `protocol-dry.json`, the two stop-path tests `protocol-stoptest-{board,die}.json` (and their dry twins), printed
  in `protocol.txt`.
- `run_e146.py`: E119's `run_e119.py` imported and run unchanged, after a preflight that refuses the session unless the three binaries are E136's registered
  ones and the protocol's stops are named by the keys run_hpl.py's watcher reads.
- `queue_e146.py`: E136's queue with E146's names, and the stop-path tests between the smoke and the session (the queue halts unless both stops fire on
  live samples).
- `reduce_e146.py`: E126's collect() and E119's clock_x, then the rules R0-R8 and the prediction errors per model. `selftest_e146.py` (`selftest.txt`).
- `logs/dry-queue.txt`, `dry-reduce.txt`: a toy-card dry run of the whole queue (smoke, both stop tests, the session) through `run_e146.py` and
  `reduce_e146.py`, no device. `logs/dmcmd-audit.txt`: Q136(w)'s checker on the run chain.
