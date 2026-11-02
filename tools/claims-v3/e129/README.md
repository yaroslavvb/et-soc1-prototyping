# E129: int8 zeros' no-issue excess - one A row, and R1 with six or more passes (Q136, kinds page section 11 item 11)

The registration is [`E129.md`](E129.md); the frozen numbers are [`predictions-e129.json`](predictions-e129.json) (printed in `predictions-e129.txt`,
written by `make_predictions_e129.py` from E109's frozen file, E124's committed card-1 results and Q136(c)'s committed bench). It answers
[the kinds page's section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 11, and Q134's final critic, item 5.
E78's runner and reducer, E109's binary and statistics and E124's card-1 frame run unchanged; the files here are what the new arm, the shorter pass, the
six-pass R1 and the device-command care need.

| file | what |
|---|---|
| `e129_common.py` | the arms (E109's `m0`, `m0k8` and the new one-A-row `m0r1`), the six items, the 14-run pass order, the installers for `run_e78.py` and `reduce_e78.py` |
| `check_e129.py` | every reused file (and on the box every binary) byte-identical to `predictions-e129.json` › `harness`, or exit 9 |
| `preflight_e129.sh` | Q136(w)'s `dmcmd_audit.py` on every file the session runs, no WRITE allowed: GO or no device opens |
| `run_e129.py`, `block_e129.sh` | one pass as a lib.sh block (`run_e78.py` unchanged); telemetry only through `e128/ettelem_guard.sh`, the drain refused |
| `session_e129.sh`, `queue_e129.sh`, `smoke_gate_e129.py` | the card session on aifoundry1 card 1 (checks, config reads, smoke and its gate, passes 12910-12919 inside 35 card-minutes) |
| `reduce_e129.py` | `reduce_e78.py` unchanged with E129's items, card 1's config gate, its meter dips removed; `--relax-tie` is the registered set-aside rule |
| `score_e129.py` | R0-R3 (E109's formulas), Y1, Y2, V0-V2 (one A row), R6, R10, and the set-aside rule's choice of reduction |
| `pipeline_e129.sh` | on the Intel: the primary, the relaxed reduction, two arms, the scorer on each |
| `pool_r1_e129.py` | amendment A1: R1p, R1 pooled with E124's four passes on this card |
| `selftest_e129.py` | committed data through the code (`selftest.txt`): E124's numbers reproduced, the order, the reducer port, the rules |
| `collect_e129.sh` | the raw passes and the session's logs from aifoundry1 to the Intel's clone (rsync, read only on the box) |

Run the session from `~/nekko` on aifoundry1, after the claim: `E129_T0=$(date +%s) setsid nohup bash tools/claims-v3/e129/session_e129.sh > build/e129/session.out 2>&1 < /dev/null &`.
The data and results: [`docs/reports/data/2026-11-02-e129-int8-noissue/`](../../../docs/reports/data/2026-11-02-e129-int8-noissue/README.md).
