# E124: E109's int8-zeros test on a second card (Q134, kinds page section 11 item 11)

The registration is [`E124.md`](E124.md); the frozen numbers are [`predictions-e124.json`](predictions-e124.json) (printed in `predictions-e124.txt`,
written by `make_predictions_e124.py` from E109's frozen file and committed card-1 results). It answers
[the kinds page's section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 11's "a replicate that scores".
E109's code runs unchanged; the files here are what card 1 and the set-aside rule need.

| file | what |
|---|---|
| `check_e124.py` | every reused file (E109's, E78's, E93's tile, lib.sh) byte-identical to `predictions-e124.json` › `harness`, or exit 9 |
| `session_e124.sh`, `queue_e124.sh` | the card session on aifoundry1 card 1 (config reads under card 1's lock, E109's smoke and gate, passes 12410-12414 with the budget from the session's launch, amendment A1) |
| `reduce_e124.py` | `reduce_e78.py` unchanged with E109's items, card 1's config gate, its meter dips removed; `--relax-random` is the registered set-aside rule |
| `pipeline_e124.sh` | on the Intel: the primary, the relaxed reduction, two arms, `score_e109.py` with `predictions-e124.json`, `extras_e124.py` |
| `extras_e124.py` | which reduction carries the verdicts, rules Y1, Y2, Z, the reported readings, every quantity beside E109's |
| `selftest_e124.py` | E109's committed data through the pipeline (`selftest.txt`) |
| `collect_e124.sh` | the raw passes and the session's logs from aifoundry1 to the Intel's clone (rsync, read only on the box) |

Run the session from `~/nekko` on aifoundry1, after the claim: `E124_T0=$(date +%s) setsid nohup bash tools/claims-v3/e124/session_e124.sh > build/e124/session.out 2>&1 < /dev/null &`.
The data and results: [`docs/reports/data/2026-11-01-e124-int8-zeros-replicate/`](../../../docs/reports/data/2026-11-01-e124-int8-zeros-replicate/README.md).
