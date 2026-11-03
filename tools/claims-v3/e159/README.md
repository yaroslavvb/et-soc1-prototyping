# e159: a large GEMM's sustained power and governed clock, G3's blind test (Q139)

The registration is [`E159.md`](E159.md), with the classified list of every device command the run sends. The design and the frozen predictions are
Q139(q)'s, committed at `91def7c4` before this registration: [`predictions-e159.json`](../../../docs/reports/data/2026-11-03-q139q-gemm-g3/predictions-e159.json),
[`e159_g3.py`](../../../docs/reports/data/2026-11-03-q139q-gemm-g3/e159_g3.py) and [`g3_model.py`](../../../docs/reports/data/2026-11-03-q139q-gemm-g3/g3_model.py),
scored behind [`score_e159.py`](../../../docs/reports/data/2026-11-03-q139q-gemm-g3/score_e159.py)'s hash check. It answers rank 3 of Q138's final critic and the
kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 1 and 6.

- The binary is E136's [`rgm136`](../e136/rgm136/README.md), unchanged (`build/e136` on aifoundry2): every shape is an argument, `gemmL<MB>x<NB>x<KB>`.
- `make_protocol_e159.py`: `protocol.json`, `protocol-dry.json` and the two stop-path tests `protocol-stoptest-{board,die}.json` (and their dry twins), every
  hold read from the frozen design; printed in `protocol.txt`.
- `run_e159.py`: E146's preflight (the three binaries are E136's registered ones) and E158's stop limits (board stop at most 85 W, admission limit at most
  82 W), then E119's `run_e119.py`, imported and run unchanged.
- `queue_e159.py`: E158's queue (E146's) with its names changed and nothing else (the stop-path tests between the smoke and the session; the queue halts
  unless both stops fire on live samples).
- `reduce_e159.py`: the frozen scorer behind its hash check, per session, with cut holds left out; the attribution rule, R0 (the checks of C) and the safety
  record. `selftest_e159.py` (`selftest.txt`).
- `logs/dry-queue.txt`, `dry-reduce.txt`: a toy-card dry run of the whole queue (smoke, both stop tests, the session) through `run_e159.py` and
  `reduce_e159.py`, no device. `logs/dmcmd-audit.txt`: Q136(w)'s checker on the run chain (GO, 19 READ sites).
