# e119: what a clock gap buys in each of E107's arms, under aifoundry2's own governor (Q134)

The registration is [`E119.md`](E119.md); the frozen numbers are `predictions-e119.json` and `.txt`, written by `make_predictions_e119.py` from E107's,
E105's and E101's committed records. It answers part of the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
item 1 ("what a clock gap buys in each of E107's arms, on a governed card"), as of version `90e02fa93e9c`.

- The binary is E107's [`../e107/rgm107/`](../e107/rgm107/README.md), unchanged, built on aifoundry2 into `build/e119`:
  `cmake -S tools/claims-v3/e107/rgm107 -B build/e119 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/e119 -j2`.
- `make_protocol_e119.py`: writes `protocol.json` and `protocol-dry.json`, printed in `protocol.txt` (the order, the admission table, the smoke).
- `run_e119.py`: E105's `run_e105.py` imported and run unchanged, plus E111's idle-login rule, the residency read without raw state 4, and a cap that
  cuts the tail between runs.
- `queue_e119.py`: the detached queue, E105's with E119's names, E111's idle-login count and E119's smoke.
- `reduce_e119.py`: the reduction (E105's per-run code with E119's labels), X per arm and format, and the rules R0-R6. `selftest_e119.py` shows every
  rule failing on made-up rows (`selftest.txt`).
