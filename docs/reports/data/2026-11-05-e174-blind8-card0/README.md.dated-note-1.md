# E174's data README, dated note 1: the checks of C as committed and how to re-score from them, the evidence for D1's two checks and its note's true writing time, and how far the login scrub reached (after the data; no number, rule or verdict changes)

*Written Thu 5 Nov 2026 (week 45), about 15:20-15:40 PST, on the Intel, desk only, by the fix pass of the pool-8 card day's aifoundry1 lane,
after that lane's data verifier (Thu 5 Nov 2026, about 13:50-15:03 PST: the data holds, with four minor faults to fix). [`README.md`](README.md)
(lab `e5206b5b`) stays as committed; this note sits beside it. Everything here is **post hoc**. **No number, rule, line or verdict in the README
changes**, and no data file is touched. The evidence is [`posthoc-note1-e174.txt`](posthoc-note1-e174.txt), written by
[`posthoc_note1_e174.py`](posthoc_note1_e174.py) (both beside this note; § numbers below are that output's). The run answers item 6 of the kinds
page's section 11 ([horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)), as
the README says. The kit-side half of these corrections is [`E174.md.dated-note-4.md`](../../../../tools/claims-v3/e174/E174.md.dated-note-4.md).*

## 1. The checks of C: what the collector wrote and what was committed (the verifier's fault 4)

- [`collect_e174.sh`](../../../../tools/claims-v3/e174/collect_e174.sh) checks C per session into the pulled copy's `cc/`: a
  `ccheck-<session>.json` and its log `ccheck-<session>.txt` for stoptest-board, smoke and s1 (stoptest-die carries no C log). It copies the three
  `.json` files into this directory, scores from them, and then `gzip -n -k`s them, which leaves both forms in the directory.
- Each check was committed in one form only:
  - `ccheck-s1.json.gz` (50,784 bytes), with the 2,196,385-byte `ccheck-s1.json` left out;
  - `ccheck-smoke.json` and `ccheck-stoptest-board.json` as plain files, with their `.gz` copies left out.
- The collector never copies the three logs `ccheck-<session>.txt` into this directory. They stay in the pulled copy on the Intel, outside the
  repo.
- The committed files are the ones scored (§ 4):
  - `ccheck-s1.json.gz`, gunzipped, hashes to `b113f2ee…`, the sha256 that [`results.json`](results.json) › `ccheck_files` records;
  - the two plain files hash to their records, `8658143f…` and `81b66a2e…`;
  - `gzip -n -c` of the pulled copy's `ccheck-s1.json` reproduces the committed `.gz` byte for byte.
- The README's Files table lists these three files correctly, but the README never said they had been trimmed. No figure is affected.

## 2. How to re-score from this directory (this replaces the README's second command; the verifier's fault 4)

The README's "How to reproduce" says to gunzip each session's `c-log.jsonl.gz`, `launches.jsonl.gz` and `tel/*.jsonl.gz` first. That step is not
needed: the scorer reads those files gzipped (`p8gov.py` and `score_e165.py` open `.gz` files). The one file it cannot read gzipped is the check of C
over s1, because `score_e165.load_ccheck` opens it as plain JSON. Unpack that file under its own name: the C-log coverage refusal looks for each
check by the name `ccheck-<session>.json`.

```bash
# from the lab clone; <new dir> is any empty directory
gzip -dc docs/reports/data/2026-11-05-e174-blind8-card0/ccheck-s1.json.gz > <new dir>/ccheck-s1.json
python3 -B tools/claims-v3/e174/score_e174.py docs/reports/data/2026-11-05-e174-blind8-card0/aifoundry1-c0/s1 \
  --ccheck <new dir>/ccheck-s1.json docs/reports/data/2026-11-05-e174-blind8-card0/ccheck-smoke.json \
           docs/reports/data/2026-11-05-e174-blind8-card0/ccheck-stoptest-board.json \
  --out <new dir>/results.json > <new dir>/score.txt
```

- **Tested** (§ 5): this command was run at HEAD `d34f2be6`, in the run of 15:26:45-15:28:18 PST that wrote the post hoc output (and once
  before, 15:20:55-15:22:26, with the same result), over a `git archive` of this directory, with the collector's
  python (3.9.6, with numpy). It read the 128 `.gz` session files as committed and wrote `results.json` and `score.txt` byte for byte equal to the
  committed ones (sha256 `d6d3cddf…` and `79e10227…`), in 79 s.
- **The checks' order** is the collector's (`ls ccheck-*.json`); `results.json` › `ccheck_files` keeps it.
- **The data verifier's own replay**, at HEAD `9b084c66`, matched `results.json` in every value and `score.txt` on all 21 lines.
- The README's first command, `collect_e174.sh` over the pulled copy, stands as written.

## 3. D1: its note's writing time, and the evidence for its two checks (the verifier's faults 1 and 2)

- **The writing time.** [`E174.md.dated-note-3.md`](../../../../tools/claims-v3/e174/E174.md.dated-note-3.md) (committed, never edited) says
  "Written … about 12:42-12:50 PST". It was written by 12:42:29 PST: lab `0a14c7bb` was committed at 12:42:29 and pushed at 12:42:32 (§ 1). It
  came after the box's 12:40:13 read that it reports. The order the README states holds: the note, then the copy (12:43:00-02), then the launch
  (12:44:42-48). The lab's main was `0a14c7bb` at both the copy and the launch, with no commit between (§ 1).
- **The check whose output was not kept.** Note 3 says each of the 18 files was "checked first on the Intel at its frozen sha256 (18 of 18 at
  12:41 PST, none with an uncommitted change)". That check's output was not kept. Four other records stand for it:
  - **at 12:43:00, just before the copy:** `git status --short` over the 18 paths in the lab clone printed nothing (§ 2);
  - **from git:** each of the 18 blobs at `0a14c7bb`, as at `c8064454` and at HEAD, equals its frozen sha256, and no commit has touched any of the
    32 frozen files since `c8064454` (§ 3: 32 of 32);
  - **on the box, after the copy:** the same v3 box check read all 32 frozen files and the 64 tiles: `64 tiles; frozen inputs, Q139(k)'s files and
    tiles: OK`, then `BOX-CHECK-CLEAN`. The box job ran 12:43:10-12:43:29, and the step's clean mark was written at 12:44:22 (§ 2). The
    README's "12:43:09-12:44:22" spans the step, from its start to the wait's return;
  - **the data verifier's re-derivation:** it worked the same out from git on its own and found 32 of 32.
- **What D1 copied** (§ 3):
  - Of `frozen-sha256-e174.json`'s 32 files, 12 are in note 1's sync list, including all 8 of `run_e174.py`'s `BOX_FROZEN`. The other 20 are
    outside the sync.
  - Of those 20, the box's 12:40:13 read named 18 absent. These are exactly the 18 that D1 copied.
  - The other 2 (`e170/harness-e170.json` and `e170/score_e170.py`, E170's kit files) were already on the box at their frozen sha256, from an
    earlier sync.
  - This is the kit defect that [`E174.md.dated-note-4.md`](../../../../tools/claims-v3/e174/E174.md.dated-note-4.md) records.

## 4. How far the login scrub reached (the verifier's fault 2, and one more case of it)

- **What the README says.** Its sentence reads: "The collector's scrub (`scrub_etwho_e164.py` over this whole directory with the owner's login: 0
  files rewritten) and its `--check` leave no other account's login in any file (0 left)".
- **What the scrub actually read.** `scrub_etwho_e164.py` reads only the files directly in the directory it is given (`files_in`: `os.listdir`,
  files only; § 6). At the collection, the only files directly in this directory were the three `ccheck-*.json`, because the scrub runs before
  the score and before the README is written. It did not read `logs/` or `aifoundry1-c0/`. Its "0 et-who reading(s) summarised"
  ([`logs/scrub.txt`](logs/scrub.txt)) shows the same.
- **What stands for "in any file".** For the subdirectories, two other reads support it:
  - the data verifier's independent scan of all 780 files that the lane's three commits added: no login but the owner's box login;
  - this pass's run of the scrub's own `--check` in every directory of this directory as committed (§ 6): 15 directories, 0 left (138 `.gz`
    unpacked, the 135 tiles left out), with every box home path the owner's (5,283).
- **The same reads cover E172's and E170's directories**, also 0 left (§ 6). E174's collector is a port of E170's, and E172's collector scrubs
  `logs/` only; see E172's [dated note 1](../2026-11-05-e172-blind8-card1/README.md.dated-note-1.md).
- **The result.** No other account's login is in any file here. The gap is in the collector, not in the data, and dated note 4 lists it for the
  kit's v4.

## 5. What the records take from this note

- D1's note 3 is dated "written by 12:42:29 PST (committed 12:42:29, pushed 12:42:32)".
- For its two checks with no saved output, the records cite the 12:43:00 clean read, the second box check (12:43:10-29) and the git
  re-derivation (§ 3 above; `posthoc-note1-e174.txt` §§ 1-3).
- The trim of the checks of C is named (§ 1), and the reproduce step without the gunzip (§ 2).
- "Leave no other account's login in any file" rests on the whole-directory reads of § 4, not on the collector's scrub alone.

SPDX-License-Identifier: Apache-2.0
