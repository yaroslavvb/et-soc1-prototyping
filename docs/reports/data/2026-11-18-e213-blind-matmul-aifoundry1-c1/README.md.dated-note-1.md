# E213 arm B data, dated note 1 (post hoc): the never-run judgement holds 126 counted hits in 12 files, where the README's results row says 112

*Wed 18 Nov 2026 (week 47), PST. Written by the fix lane `fix-e213bd` (Q219) after the data verifier `verify-e213bd`. The verifier read
HOLDS WITH FIXES: this directory's data commit `b0c727c5` (committed 15:49:38 PST) re-derives exactly from its raw records, and one low
wording point needed a fix. This note sits beside the README and is **post hoc**: it was written after the data and after the frozen scorer's
run (step 13). A later lane commits the scorer's outputs beside this directory. This note edits no committed file and changes no datum,
forecast, rule, label or verdict, and it does not re-run the scorer. The counts below are printed by `posthoc_note1_e213b.py` in this
directory, run under `/usr/bin/python3` 3.12.3. It reads this directory's committed `judge-e213-card.json`, `judge-e213-card.txt` and
`labels-e213.json` (each checked against `SHA256SUMS` first) and `README.md`. Its printout is `posthoc-note1-e213b.txt` and its JSON is
`posthoc-note1-e213b.json`, both listed in `SHA256SUMS-note1`. The counts are **desk arithmetic on committed records**.*

## 1. The README's figure and what the judgement holds

The README's results row for step 6n (the never-run search, repeated right before the day's first card command) ends: "the judgement's
named hits by lane folder: {"data-e214": 112} (departure 6)". That 112 is the number of file names printed in **the judgement's text form**,
`judge-e213-card.txt`. The registered scanner (`tools/claims-v3/e213/desk/neverrun_card_e213.py`, its `j["files"][:6]`) prints at most the
first six counted files of each point there, and the README counted those names. **The judgement itself**, `judge-e213-card.json`, lists
every counted file of every point:

- **126 counted hits in 12 distinct files.** A hit is one of the 40 judged points together with one counted file that names its shape. All
  12 files are in `data-e214`, the round's lane folder for E214's data lane.
- **110 hits are dated 13:42:16 PST** Wed 18 Nov 2026. They come from the 8 files of E214's registration tree in that folder: `E214.md`;
  the desk files `configs-e214.json`, `neverrun-e214.json` and `scan-e214.json`; and the proposal's `arms.json` and its card-1 schedules
  `a1c1-S1`, `a1c1-S3` and `a1c1-S4`. 13:42:16 PST is the time of E214's registration commit, `95eb8069`.
- **16 hits are dated 06:29:02 PST.** They come from the 4 files of E214's kit as copied from aifoundry1 (departure 6): `arms.json` and
  the card-1 schedules `a1c1-S1`, `a1c1-S3` and `a1c1-S4`.
- **Why the text form shows fewer.** Eight points have more than six counted files: k01-k04, k20 and k21 have 8 each, and k22 and k23 have
  7 each. So the text form leaves out 14 names. Its 112 names are 110 dated 13:42:16 and 2 dated 06:29:02. For all 40 points, the text form
  names the JSON's first six counted files (or all of them, where there are six or fewer) in the JSON's order.

So the row's figure should read: the judgement's **counted hits by lane folder: {"data-e214": 126}**. That is 126 hits in 12 files: 110
dated 13:42:16 PST and 16 dated 06:29:02 PST. The text form names 112 of them, at most six a point.

| file in the lane folder `data-e214` (`work/...`) | dated (PST, its modification time) | class | points it names |
|---|---|---|---|
| `src/arms.json` | 06:29:02 | no card named | 8 |
| `src/sched/a1c1-S1.json` | 06:29:02 | aifoundry1 card 1 | 2 |
| `src/sched/a1c1-S3.json` | 06:29:02 | aifoundry1 card 1 | 4 |
| `src/sched/a1c1-S4.json` | 06:29:02 | aifoundry1 card 1 | 2 |
| `reg-tree/tools/claims-v3/e214/E214.md` | 13:42:16 | no card named | 6 |
| `reg-tree/tools/claims-v3/e214/desk/configs-e214.json` | 13:42:16 | no card named | 40 |
| `reg-tree/tools/claims-v3/e214/desk/neverrun-e214.json` | 13:42:16 | no card named | 8 |
| `reg-tree/tools/claims-v3/e214/desk/scan-e214.json` | 13:42:16 | no card named | 40 |
| `reg-tree/tools/claims-v3/e214/proposal/src/arms.json` | 13:42:16 | no card named | 8 |
| `reg-tree/tools/claims-v3/e214/proposal/src/sched/a1c1-S1.json` | 13:42:16 | aifoundry1 card 1 | 2 |
| `reg-tree/tools/claims-v3/e214/proposal/src/sched/a1c1-S3.json` | 13:42:16 | aifoundry1 card 1 | 4 |
| `reg-tree/tools/claims-v3/e214/proposal/src/sched/a1c1-S4.json` | 13:42:16 | aifoundry1 card 1 | 2 |
| **12 files** | 110 hits at 13:42:16, 16 at 06:29:02 | 110 no card named, 16 aifoundry1 card 1 | **126 hits** |

## 2. What does not change

- **Every hit is dated after arm B's freeze line,** the registration commit `291c8201` (04:18:23 PST), and none is marked before it. All 12
  files are E214's registration and kit files, which name arm B's shapes among the planned arms of the model session's third sweep. None is
  a run record: no E214 session ran before arm B released the box, as departure 6 says.
- **Step 6n's line stands as printed:** "0 of 40 scored points never ran on aifoundry1 card 1 ...; ran before the freeze line ...,
  labelled: none; ran after it (REPORTED, kept): k01 ... k40".
- **The labels stay empty.** `labels-e213.json` equals the judgement's labels, which are empty, and every point stays in every rule. The
  scorer's input and its verdicts are unchanged.
- **Departure 6 stands.** It gives no count.

## 3. The verifier's other findings: nothing to change in this directory

- **The board stop in run 079 (k37; medium, registered).** It is the trade that Amendment A3 registered. The runs done stand as registered,
  and k38 and k39 have NO DATA. After the data commit, the round's orchestrator accepted the short day as registered: no amendment and no
  rerun of the gemmLnc block.
- **MM1-v3's gemmLnc energy (medium, a model finding).** This is the work of MM1-v3.1's declared gemmLnc census energy item (`7375bc9c`).
  Arm B's scores stand as registered.
- **H2 NOT DECIDED (low).** It reads as registered. The frozen scorer's words go beside this directory with its outputs.
- **The scorer's outputs (info).** They reproduce byte for byte from this directory's committed data, and a later lane commits them as
  they are.

## What this note changes

Nothing measured, forecast, registered or scored. It adds five new files:

- this note;
- the script `posthoc_note1_e213b.py`;
- its printout, `posthoc-note1-e213b.txt`;
- its JSON, `posthoc-note1-e213b.json`;
- `SHA256SUMS-note1`, which lists the other four, plus `README.md` and `SHA256SUMS` as the data commit holds them.

Every committed file stands as committed. To reproduce, run `/usr/bin/python3 -I -B posthoc_note1_e213b.py --json <a new path>` from
this directory. It prints `posthoc-note1-e213b.txt` byte for byte and uses Python's own modules only.

SPDX-License-Identifier: Apache-2.0
