# The load ledger v2: its form, its constants and its predictions, frozen before any score (Q166, step 1)

*Thu 12 Nov 2026 (week 46), PST, desk only: no card, no lab box, no device command. Written by Q166's calc-a lane.*

This file freezes [`frozen-v2.json`](frozen-v2.json) (the form and every constant, each with its committed source and
its label) and [`predictions-v2.json`](predictions-v2.json) (every load's prediction, from `frozen-v2.json` and the
loads' inputs only). Their sha256 are in [`SHA256SUMS-freeze`](SHA256SUMS-freeze). They are committed before
`tools/ledger/score_ledger_v2.py` exists and before any measured watt or joule of a scored load is read by code.

**Held out, not blind.** The three held-out loads (E39, E37 and E59) were measured on 26 and 29 September; their
measured values were known before this freeze (the November checkpoint page quotes E59's and E37's, and v1's
committed scores carry all three). Two rules were set during the desk build after arithmetic that put v2 beside E101's
`mmp64` arm, which is the benchmark streaming from DRAM: a hart's time is priced once (`awake_rule`), and E136's
cooperative loads move 384 B per minion-op beyond the L2, not 2 KB (`E136.md`'s own count). No constant was fitted to
any of the seven loads.

**What v2 is.** The joined load model of 26 Oct (`tools/ettelem/load_model.py`), revived by its retirement note's
recipe ([`../2026-10-26-load-model/README.md.dated-note-1.md`](../2026-10-26-load-model/README.md.dated-note-1.md)):
- M10's kernel term in place of the 21 Sep flip prices, leave-one-kind-out;
- the energy catalogue's memory and mesh prices, with the set-bit form that E101 found;
- the footing law per card, with E66's idle split outside its band.

Its code is [`tools/ledger/ledger_v2.py`](../../../../tools/ledger/ledger_v2.py),
[`freeze_ledger_v2.py`](../../../../tools/ledger/freeze_ledger_v2.py) and
[`loads_ledger_v2.py`](../../../../tools/ledger/loads_ledger_v2.py).

Re-run, from the top of the tree:

```
python3 -I -B tools/ledger/freeze_ledger_v2.py      # writes frozen-v2.json (its frozen_pst line changes; nothing else)
python3 -I -B tools/ledger/loads_ledger_v2.py       # writes predictions-v2.json from it
```

SPDX-License-Identifier: Apache-2.0
