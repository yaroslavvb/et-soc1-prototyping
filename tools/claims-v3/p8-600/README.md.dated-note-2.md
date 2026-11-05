# p8-600, dated note 2: score_p8_600_v3.py's ka-pooled supersedes v2's; what the identity checks establish; a self-test whose output re-makes byte for byte (Q142(v2) fix pass)

*Written Thu 5 Nov 2026 (week 45), about 08:30 PST, on the Intel, desk only, after the code it describes was committed (lab `e2b48f5a`,
08:27:12 PST) and before any E171 or E172 data. It sits beside [`README.md`](README.md) (`a518aa11`) and its
[dated note 1](README.md.dated-note-1.md) (`86d10a75`), which stay as committed. Registered by dated notes 2 beside
[`../e171/E171.md`](../e171/E171.md.dated-note-2.md) and [`../e172/E172.md`](../e172/E172.md.dated-note-2.md) (`c9a3e40a`, 08:23:02 PST, committed
before the code). It answers the first verifier of v2 (`verify-q142v2-code`, Thu 5 Nov 2026: faults 1, 2 and 6) and serves item 6 of the kinds
page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

## What the card day runs

| reading | command | status |
|---|---|---|
| every registered verdict of a session | `score_p8_600.py score` (`a518aa11`), through each run's collector | unchanged |
| the scale anchors' C status, the c_clean_scale arm beside | `score_p8_600_v2.py scale-c` (`86d10a75`) | unchanged |
| P8-KA pooled, the registered reading | **`score_p8_600_v3.py ka-pooled <E171 scored.json> <E172 scored.json> --scale-c <both scale-c.json>`** | **new: supersedes v2's ka-pooled** |

Step 22 v3 (`../q141k-runbook/k6/s22_collect_k6_v3.sh`) calls each in its place. Neither the committed scorer's `ka-pooled` nor v2's is the
registered pooled reading from now on.

## What v3 changes, and why

- **Fewer than 2 kept passes (the verifier's fault 1).** The committed scorer writes such a session with its mark `"<k> kept passes, fewer
  than 2"`, every verdict NOT SCORED and no rows. v2's check 6 counted rows and refused the pair (6); step 22 v2 then stopped with 16. v3's
  check 6 accepts the committed scorer's own NOT SCORED session (the mark with k equal to its kept passes and k < 2, no rows, no rule but
  P8-KC, no verdict but NOT SCORED) and refuses any other form of the mark. The pooled reading is then NOT SCORED, as E171.md and E172.md
  register it ("2 check anchors, fewer than 4"; with both sessions short, 0).
- **One session counted twice (the verifier's fault 2).** v3's check 7 refuses two files that carry the same measured D to the bit on at
  least 3, and at least half, of the pool-8 tiles both measured with a non-zero D. Genuine sessions share none (E163 and E164: 0 of 65).
- **The wording, as the records quote it from now on.** Note 1's line 14 ("can no longer be read from one session counted twice") says more
  than v2 did. v3 refuses, with exit 6 and nothing written: one file twice; a byte copy; the pair swapped; a relabelled file; another
  scorer or predictions file; no C gate; a NOT SCORED mark the committed scorer never writes; two files with the same measured D. It cannot
  tell a copy whose numbers differ from the original's (for example one session's raw copy re-reduced with the other card's footing); the
  runbook's fixed per-box routes keep the pair right.

## The self-test: `selftest_score_p8_600_v3.py`, W0-W6 PASS

Its output, `selftest-score-p8-600-v3.json` and `.txt`, re-makes byte for byte on any machine and in any temporary directory: two runs from
temporary directories of very different lengths (07:59 and 08:01 PST) and the committed one (08:08) are identical, and none holds a home or
temporary path. That answers the verifier's fault 6 for v3: v2's self-test cut its lines to 150 characters before masking (its lines 218 and
423), so a long temporary path could escape the mask, and it hashed synthetic files that embed the temporary path. v3's masks before any cut
and reports every sha256 of a file it wrote as the sha256 of that file's masked bytes. **v2's own self-test is quoted as: "V0-V3 PASS on
re-run; 269 of 272 leaves equal, the other 3 hashes of synthetic files that embed the temporary directory".**

| part | what it shows |
|---|---|
| W0 | the committed scorer and v2 as their lists name them; a wrong v2 line exits 9; the scorer's NOT SCORED mark is the form v3 reads; the predictor's lists 16 and 9 |
| W1 | the genuine pair: v3 = v2 = the committed `ka_pooled`, PASS, n 4, the rows equal |
| W2 | one kept pass: v2 refuses (6), as the verifier found; v3 NOT SCORED n 2 (E171 short), n 2 (E172 short), n 0 (both), each equal to the committed reading; with `--scale-c`, the arm beside NOT SCORED n 2 |
| W3 | six NOT SCORED marks the committed scorer never writes, each refused (6, nothing written) |
| W4 | E171's measurements laid out as E172's raw copy and scored `--run E172`: v2 PASS, n 4; v3 refused (6): 62 of 62 shared non-zero D identical |
| W5 | v2's refusals carried by v3 (nine, each 6), and the positive control with `--scale-c` in order (PASS, beside PASS, n 4) |
| W6 | E163's and E164's committed reductions: 65 tiles with a non-zero D in both, 0 bit-identical (only the three zeros items, exactly 0 W, coincide); E163 against itself refused |

Run end to end through step 22 v3 in a sandbox with the real scorer, gate and v2 scale-c (10 of 10 cases as expected; not committed): one
kept pass reads NOT SCORED with `ka-pooled.json` written; the relabelled copy stops with 16.

`SHA256SUMS-v3` lists v3, its self-test and the self-test's output (4); step 3b (`../q141k-runbook/k6/s03b_lists_k6.sh`) checks it at the go
beside the 22 lists. Exit codes: 0 written; 6 an identity check failed; 9 the committed scorer, v2 or a predictions or intervals file is not its
committed file; 1 the predictor's own stop; 2 usage. Nothing is written on a refusal.

SPDX-License-Identifier: Apache-2.0
