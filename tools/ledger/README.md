# tools/ledger: a load in, its joules out, by the energy manual's ledger

The calculator of the November checkpoint's plan, step 1 (Q166, Thu 12 Nov 2026).

**A new folder, on purpose.** The joined load model of 26 Oct (`tools/ettelem/load_model.py`, `predict_load.py`) is retired
by a dated note, and its files stay as committed. This folder revives it the way that note prescribes without editing a
committed file, beside `tools/ettelem/` rather than inside it. Nothing under `tools/claims-v3/` reads it.

The counter of step 2 and the programs of step 3 are other lanes' work, in folders of their own.

| file | what |
|---|---|
| `ledger_v2.py` | the model: `predict(load, frozen)` returns joules over idle and with the card at rest, split by term, each with a band |
| `freeze_ledger_v2.py` | writes `docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json`: the form and every constant, each with its committed source and label |
| `loads_ledger_v2.py` | the scored loads, described by their inputs and counts only, and their frozen predictions (`predictions-v2.json`) |
| `score_ledger_v2.py` | the frozen predictions against the committed measurements (`scores-v2.json`, `chart-data-v2.json`); it refuses to run if a frozen file changed |
| `posthoc_ledger_v2.py` | the dated corrections of Q166's fix lane, every one post hoc (`posthoc-v2.json`): the awake rule's effect on E37 and E101's DRAM arm, E136's L3 row, sparse parity's op cycles priced once, E37 at its starting die and its byte count |
| `chart_ledger_v2.py` | the one chart, forecast against measured (`chart-v2.html`, self-contained) |

**To price a new load**, write it as `loads_ledger_v2.py` writes E59: the card, clock and starting die temperature, its seconds,
its tensor ops by format and kind, its hart cycles by activity, its bytes by path with the data's set-bit and changed-bit shares,
and its mesh hops. Then call `ledger_v2.predict()`. A kind that is not in `frozen-v2.json` needs M10's features first.

The results and their labels are in [the data directory's README](../../docs/reports/data/2026-11-12-q166-ledger-v2/README.md).
Standard library only; run with `/usr/bin/python3 -I -B` (Python 3.9, as the committed outputs were written).

SPDX-License-Identifier: Apache-2.0
