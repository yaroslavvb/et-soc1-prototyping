# README.md, dated note 1 (Thu 12 Nov 2026, PST): two figures the README quotes, read again from this folder's files; nothing frozen changed

*Written by Q167's fix of its records, on two nits of its verifier (Thu 12 Nov 2026, about 21:56–22:51 PST), desk only: no card, no
lab box, no device command. [`README.md`](README.md) (`80eb3bdf`) and every frozen file here stay byte for byte as committed; this
note sits beside them and is pinned by `SHA256SUMS-note1`. Each figure below is re-read from this folder's own committed files. No
prediction, score, label or verdict changes.*

**1. E37 at its starting die** ("Results", the bullet that ends "reads +2.4 / +3.3 / +1.4% (post hoc), against
+3.4 / +3.7 / +1.3% as frozen"): [`posthoc-v2.json`](posthoc-v2.json), `e37_die_start.j_total_per_op_error_pct_given`, reads
+2.34996 (aifoundry2), +3.29001 (aifoundry3) and +1.39840 (aifoundry1 card 1): **+2.3 / +3.3 / +1.4%** at one decimal. The +2.4 came
from rounding 2.35 a second time. Post hoc, as the README labels it.

**2. The first model's joules a solve over idle, given its seconds** (the table "What this does to predicting power and heat", its
row "the same, J a solve over idle, given its seconds", where the first model's column reads "13-39% low"):
[`scores-v2.json`](scores-v2.json), the four E59 rows whose quantity is "J a solve over idle" with "seconds": "given", their
`v1_error_pct`, read −19.3 / −12.3 / −16.1 / −37.5%: **12–37% low**. The 13–39% is the first model's watts over idle (the same runs'
"W over idle, leak-corrected" rows, −23.0 / −13.4 / −19.6 / −38.8%), as the table's row above it says. v2's figures beside it stand.

SPDX-License-Identifier: Apache-2.0
