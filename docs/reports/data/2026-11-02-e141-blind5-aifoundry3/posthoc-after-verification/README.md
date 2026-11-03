# E141, post hoc after verification: the registered pool read on M7's training footing

*Written Mon 2 Nov 2026, about 23:10 PST, after E141's data and after an independent verifier's read. **Post hoc: never a verdict.**
E141's registered verdicts are those of the primary, in [`../scored.json`](../scored.json) and [`../results.md`](../results.md), and they
stand. Desk only: no card, no device command. The why is correction C1 of the
[data README](../README.md#corrections-after-verification-mon-2-nov-2026).*

**What these files are.** E141's frozen reducer, [`tools/claims-v3/e141/reduce_e141.py`](../../../../../tools/claims-v3/e141/reduce_e141.py)
(E78's `reduce_e78.py` unchanged, E78's gates), run over the same four committed passes as the primary (`../aifoundry3/e141/p14110`–`p14113`),
with the leakage slope fixed (`--no-refit`) at three readings of the footing M7's 247 aifoundry3 float training rows were reduced on:

- **0.2104 W/°C**, their sessions' slopes averaged over rows (the verifier's value);
- **0.2163**, weighted by each row's D;
- **0.2217**, weighted by D², the weighting a common scale error carries.

Each slope is read twice: once with the board meter's dips kept (as in the registered primary and in 154 of those rows), and once with
them removed (E82 A2's definition, as in the other 93 rows: E121–E123 and E127). Each reduction is scored **alone** by the frozen scorer,
[`tools/claims-v3/e141/score_e141.py`](../../../../../tools/claims-v3/e141/score_e141.py), as the dips-removed arm was. How the three slopes
come from the rows is printed by [`../corrections-numbers.py`](../corrections-numbers.py) (§ C1) into
[`../corrections-numbers.txt`](../corrections-numbers.txt).

| footing | P1 fp32 rms | P2 fp16 rms | P3 int8 rms | B1 floats bias | B2 int8 bias | C1 |
|---|---|---|---|---|---|---|
| **registered primary** (auto 0.2634, dips kept) | 0.325 PASS | **0.317 FAIL** | 0.356 PASS | **−0.230 FAIL HIGH** | −0.110 PASS | 28/30 |
| 0.2104, dips kept | 0.266 PASS | 0.243 PASS | 0.344 PASS | −0.107 PASS | −0.082 PASS | 30/30 |
| 0.2163, dips kept | 0.271 PASS | 0.249 FAIL | 0.345 PASS | −0.121 FAIL HIGH | −0.085 PASS | 30/30 |
| 0.2217, dips kept | 0.275 PASS | 0.255 FAIL | 0.346 PASS | −0.133 FAIL HIGH | −0.088 PASS | 30/30 |
| 0.2104, dips removed | 0.145 PASS | 0.147 PASS | 0.337 PASS | +0.001 PASS | −0.086 PASS | 30/30 |
| 0.2163, dips removed | 0.144 PASS | 0.145 PASS | 0.338 PASS | −0.013 PASS | −0.090 PASS | 30/30 |
| 0.2217, dips removed | 0.145 PASS | 0.145 PASS | 0.339 PASS | −0.026 PASS | −0.093 PASS | 30/30 |

The lines are the registered ones: P2 at most 0.247 W, B1 inside [−0.117, +0.085] W. Heat (H1–H4) reads the same at every footing:
0.128 / 0.129 / 0.135 °C with the dips kept, 0.087 / 0.126 / 0.129 °C with them removed, 30 of 30 inside. M1 and M2 stay NOT RESOLVED
everywhere. With the dips kept the reducer sets 14110 aside, as the primary does; with them removed it keeps all four passes.

**Files.** `run_posthoc.sh` (the commands); for each `<tag>` in `leak0.2104`, `leak0.2163`, `leak0.2217`, `nodips-leak0.2104`,
`nodips-leak0.2163`, `nodips-leak0.2217`: `e141-<tag>.json` and `runs-<tag>.csv` (the reduction), `reduce-<tag>.txt|log`,
`scored-<tag>.json`, `results-<tag>.md` and `score-<tag>.log` (the score; each results file's header gives its slope and passes).
`e141-leak0.2104.json` is byte-identical to the verifier's own reduction at that slope.

```bash
PY=/usr/bin/python3 nice -n 10 bash docs/reports/data/2026-11-02-e141-blind5-aifoundry3/posthoc-after-verification/run_posthoc.sh
```
