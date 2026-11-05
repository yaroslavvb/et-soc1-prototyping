# Pool 8's P8 scorer at 600 MHz, dated note 1: `score_p8_600_v2.py` beside it, the pooled KA read for the registered pair only, each scale anchor's C status with an arm beside, and the exit codes as the code has them

*Written Thu 5 Nov 2026 (week 45), PST, on the Intel, in Q142(k6)'s fix pass (lane `fix-desk-q142k6-kits`), desk only: no card claimed,
no device command sent, no lab box reached. New files only: [`README.md`](README.md), `score_p8_600.py` and every file of `a518aa11` stay
as committed, and `SHA256SUMS` (5) still passes. This note follows the registrations' dated notes,
[`../e171/E171.md.dated-note-1.md`](../e171/E171.md.dated-note-1.md) and [`../e172/E172.md.dated-note-1.md`](../e172/E172.md.dated-note-1.md)
(`2502ba81`, 05:38:09 PST, committed before this code and before any data), which say what N1 and N2 below register and why. They answer
faults 1-3 of the kit's verifier (`verify-desk-q142k6-kits`, Thu 5 Nov 2026), for item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

## What it does to predicting power and heat

No number, line or verdict of M10 or M9 changes. It closes two ways a blind pool-8 figure could be misread. The pooled check of term a
(P8-KA over both 600 MHz cards) can no longer be read from one session counted twice, or from a file relabelled as the other card's. And a
session's float scale s, which sets every float primary on that card, now comes with each of its anchors' C status, plus an arm that
leaves out any anchor whose C is not all PASS. So a scale set by a miscomputed anchor would be visible beside the registered verdicts.

## The files

| file | what |
|---|---|
| `score_p8_600_v2.py` | imports the committed scorer, unchanged, and adds two commands (below); it does no scoring of its own |
| `selftest_score_p8_600_v2.py` → `selftest-score-p8-600-v2.json`, `.txt` | the self-test, V0-V3, all PASS (run 05:46:00-05:47:38 PST, one slot job; the files are the test's own output, never edited) |
| `SHA256SUMS-v2` | the four files above |

**`ka-pooled <E171 scored.json> <E172 scored.json> [--scale-c <E171 scale-c.json> <E172 scale-c.json>] [--json out]`** (N1). It refuses,
with exit 6 and nothing written, unless: the first file is run E171 on aifoundry3 and the second run E172 on aifoundry1c1; each names its
card's frozen predictions file with the freeze's sha256; each was scored by the committed scorer, whose file still has its committed
sha256; each passed the C gate; the two are different files with different contents; and each file's rows are its own card's (every row's
a-priori D is its rate times that card's frozen per-op coefficient within 1e-9 W, and both check anchors have a row). Then it calls the
committed `ka_pooled` on the two files. With `--scale-c`, the arm's pooled reading is reported beside, never the verdict.

**`scale-c --run E171|E172 --scored <scored.json> --reduction <primary> --raw <raw copy> --ccheck <check of C> [--json] [--md] [--work]`**
(N2). It first checks that the scored file is this run's: on this reduction, these predictions, by the committed scorer, C-gated, with the
P8-KC block this check of C gives and the scale the frozen `scale` gives on this reduction. If not, exit 6. It then writes each anchor's C
status by P8-KC's own rule (E163's `c_status`, the committed scorer's copy). These are pool 8's four float scale anchors and M10's own
list, E78's `fp32.randn` and `fp16.randn` among them, with E78's footing items beside: `fp32.zeros`, `fp16.zeros`, `int8.zeros`, `int8.full`
and the tie. If an anchor that entered s is not all PASS, it also writes the arm `c_clean_scale`: the frozen `scale` on a copy of the
primary reduction without those anchors' items, and every rule scored on it by the committed `score_reduction`. Its last line is the
`SCALE-C` summary the runbook prints.

## The exit codes (the verifier's fault 3)

The committed scorer's docstring says "9 when a frozen input differs", and [`README.md`](README.md)'s "How it scores" step 1 says "anything
else exits 9". As the code has them: **0** scored; **4** a listed session without a finished check of C; **5** the scale read an anchor it
must not; **9** this card's predictions file or `intervals-pool8.json` is not the freeze's; **1** one of the predictor's own hash lists,
or POOL8-SHA256SUMS's 209, differs. The last is the predictor's stop, `POOL8-A2 STOPPED` or `POOL8 STOPPED`, raised as SystemExit.
Nothing is written in any refusal. v2 keeps these codes and adds **6**, an identity check failed. It also uses 9 when the committed
scorer's file is not its committed one.

## The self-test, V0-V3: all PASS

| part | what | result |
|---|---|---|
| V0 | the inputs | the committed scorer's sha256 `cd5b602484d7…` equals its `SHA256SUMS` line; v2's list of E78's items equals `e78_common.py`'s `ANCHORS` and `TIE`; the predictor's lists pass |
| V1 | N1 on a synthetic session per card: the committed self-test's builder, with E78's items added to every pass's runs and C logs, scored by the committed scorer's command line as the collectors call it | the right pair reads PASS, n 4, the same verdict, n and rows as the committed `ka_pooled`. **Refused, exit 6, nothing written:** E171 twice; E172 twice; the pair swapped; E171's file relabelled as E172's, with run, card, predictions path and sha256 changed (caught by its rows: the cards' per-op coefficients differ by about 4%); a predictions sha256 that is not the freeze's; a scorer sha256 that is not the committed one; a file with no `c_sessions`; a missing file; `--scale-c` with its two files swapped. `--scale-c` in order: the beside reading equals the registered one when neither session has an arm |
| V2 | N2 on synthetic sessions whose six anchors in s sit at known ratios (1.000-1.010, so the primary's s is their median, 1.005) | (a) every anchor C all PASS, both cards: six anchors in s, each all PASS, the arm is the primary. (b) one of pool 8's scale anchors judged FAIL on every launch, both cards: the scored file's P8-KC reads FAIL, as registered; the anchor is named; the arm's s is 1.006, the median of the other five ratios computed in the test, against the primary's 1.005. (c) E78's `fp32.randn` judged FAIL: the scored file's P8-KC reads PASS (it covers pool 8's tiles only); scale-c names the anchor, and the arm without it reads s 1.006. (d) every anchor in s judged FAIL: the arm's s is 1, its KA NOT SCORED, and 5 rules read differently. (e) `fp32.zeros` judged FAIL: named as a footing item, no arm. (f) **refused, exit 6, nothing written:** the other card's scored file; a reduction other than the one scored (one tile's D moved by 1 mW); another session's check of C; a scored file without `c_sessions`; the other run named. Exit 9 for predictions that are not the freeze's; the predictor's own stop propagates, and nothing is written. (g) `ka-pooled --scale-c` with (b)'s arm on E171: the registered reading is the committed one's (PASS, n 4), and the beside reading's E171 rows are the arm's KA rows |
| V3 | real data: the same C-status reading on E163's and E164's committed sessions (committed reductions, raw passes and checks of C) | **E163** (kept passes 16310-16312): `fp32.randn` 90 launches, `fp16.randn` 90, pool 7's four random anchors 30 each, `fp32.zeros`, `fp16.zeros`, `int8.zeros`, `int8.full` 90 each, the tie 60. **E164** (16410-16413): `fp32.randn` 120, `fp16.randn` 110, pool 6's two random anchors 40 each, pool 7's four 40, 30, 40 and 40, the zeros 110, 110 and 120, `int8.full` 120, the tie 80. Every one is C all PASS. E78's items had been judged inside each check's summary (E163: 4,062 launches, all PASS; E164: 3,896, all PASS), but no record gave their C status item by item: E163's committed `c_status` covers its 77 pool tiles (pool 7's anchors among them), and P8-KC covers pool 8's |

## Compute

The Intel, through the round's local slot, one job at a time at nice 10: two runs of the self-test. The first, 05:43:21-05:45:05 PST,
failed one case of its own design: "another session's reduction" passed (b)'s reduction, which the deterministic builder makes
byte-identical to the base session's, so v2 rightly read it as the same reduction. The case now moves one tile's D by 1 mW; nothing in v2
changed. The second, 05:46:00-05:47:38, is the committed one. A syntax check ran inside each job. No lab box, no mini job, no card.

SPDX-License-Identifier: Apache-2.0
