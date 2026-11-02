# e126: E119's harness on E107's last three arms, and E119's sustained pairs again, under aifoundry2's own governor (Q136)

The registration is [`E126.md`](E126.md), with the classified list of every device command the run sends ("Device commands sent"); the frozen numbers
are `predictions-e126.json` and `.txt`, written by `make_predictions_e126.py` from E107's and E119's committed records through E119's own prediction
module. It answers part of the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 1
("the clock gap in E107's other three arms (c4s, c8 and c16s)", and the replicate of E119's governed clocks Q134's critic asked for), as of version
`fbb682f9393b`.

- The binaries are E119's, unchanged and not rebuilt: `build/e119/host/sparsity_host`, `build/e119/kernel/sparsity.elf` (E107's
  [`../e107/rgm107/`](../e107/rgm107/README.md), built by E119) and the sampler `build/ettelem-hpl/ettelem` (`../dv2/ettelem-dv2/`).
- `make_protocol_e126.py`: writes `protocol.json` and `protocol-dry.json`, printed in `protocol.txt` (the order, the admission table, the smoke, the
  session stops: 80 °C, 93 W on three samples).
- `run_e126.py`: E119's `run_e119.py` imported and run unchanged, after a preflight that refuses the session unless the three binaries are
  byte-identical to E119's.
- `queue_e126.py`: E119's `queue_e119.py` with three names changed (the slot's name, the runner, the default protocol).
- `reduce_e126.py`: the reduction (E119's per-run loop with E126's labels, E119's `clock_x`), X per arm and format, the rules R0-R8, the safety
  record. `selftest_e126.py` shows every rule failing on made-up rows and the preflight refusing (`selftest.txt`).
- `dry-reduce.txt`: the toy card's dry session through `run_e126.py` and `reduce_e126.py` (no device); `dry-queue.txt`: the queue's dry run.
