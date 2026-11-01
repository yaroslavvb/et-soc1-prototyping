# E109: int8 zeros' extra 0.61 W (Q133, kinds page section 11 item 11)

The registration is [`E109.md`](E109.md); the frozen numbers are [`predictions-e109.json`](predictions-e109.json) (printed in `predictions-e109.txt`,
written by `make_predictions_e109.py`). It answers [the kinds page's section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
item 11, with an arm for item 15.

| file | what |
|---|---|
| `sp109/` | the binary: `workloads/sparsity` with `SpArgs.shape` and a `shape=` prefix on `--values` |
| `e109_common.py` | the items, the per-pass order, the installers for `run_e78.py` and `reduce_e78.py` |
| `run_e109.py`, `reduce_e109.py` | E78's runner and reducer, byte-identical, with E109's items installed |
| `block_e109.sh`, `queue_e109.sh` | one pass as a lib.sh block; the registered passes, detached on the box |
| `score_e109.py`, `selftest_e109.py` | the registered rules; synthetic data through them (`selftest.txt`) |
| `desk/` | the RTL bench for every arm (`bench_e109.sh`, `tb_patch_e109.py`, `bench_arms_e109.py`, `bench-arms.*`) and the sys_emu check |

Run the passes from the tree that holds `build/e109` (aifoundry3: `~/aifoundry`): `bash tools/claims-v3/e109/block_e109.sh 10901 --smoke`, then
`setsid nohup bash tools/claims-v3/e109/queue_e109.sh > build/e109/queue.out 2>&1 < /dev/null &`.
