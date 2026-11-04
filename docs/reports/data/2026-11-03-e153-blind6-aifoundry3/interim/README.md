# E153: the interim scoring before amendment A1 (disclosed after verification; not results)

*Committed Tue 3 Nov 2026, about 18:40 PST, by E153's fix pass, after an independent verifier found that A1's text misstated this look
(the data README's § Corrections after verification, C1). These four files are byte for byte what the lane's working copy held. They are
evidence of what was seen before A1 was written. They are not results, and no number here is quoted as one.*

**What was run.** Pass 15310, the session's first, ended at 16:35:07 PST. The lane copied it to the desk and ran the collector on it
alone: the C check, the registered reduction and its arms. With one kept pass the registered scorer scores nothing, and it printed no
verdict (16:39:47). The lane then took that reduction (`e153.json` of pass 15310), set its `passes` list to `[15310, 15310]`, and ran the
registered scorer on it with the C check. The scorer counted the pass twice, so each tile read one pass's value with n = 2. It printed
every rule's verdict:

| file | written | the scorer | what it shows |
|---|---|---|---|
| `scored-15310x2-pre-a1.json`, `results-15310x2-pre-a1.md` | 16:40:11 PST | as registered (`359c96b2`) | every verdict; KC FAIL, because `int8.b_line_zero_full` (skipped in 15310 by E78's runner) was counted as a C failure |
| `scored-15310x2-a1.json`, `results-15310x2-a1.md` | 16:41:35 PST | with A1's change | the same verdicts and numbers, KC PASS; the tile named in `c_not_measured` |

A1 was written at 16:41:53 and committed at 16:42:11 (`e6ca949d`). The times are the working files' modification times.

**What it changed.** Nothing in the final verdicts: the scorer as registered, run on the session's final reduction, gives the committed
`scored.json` and `results.md` exactly, bar A1's new, empty `c_not_measured` keys (`../corrections.txt` C1). The interim verdicts equal
the final ones for every rule except K1 and KC. K1 was NOT SCORED here, because its rules read the reduction's own per-tile count, which was
1; the other rules loop over the `passes` list.
