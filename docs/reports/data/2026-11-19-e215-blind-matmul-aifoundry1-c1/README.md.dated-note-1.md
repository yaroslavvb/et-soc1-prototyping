# E215 arm B data, dated note 1 (post hoc): the arm A line of this directory's never-run report is not arm A's judgement; it reads E217's registration desk

*Thu 19 Nov 2026 (week 47), PST. Written by the fix lane `fix-e215d` (Q224) after the data verifier `verify-e215d`. The verifier read
HOLDS WITH FIXES: this directory's data commit `4f648f24` (committed 14:14:38 PST) and arm A's, `8355db15`, re-derive exactly from their raw
records, and its finding 3 (low, records) asked for this note. The note sits beside the README and is **post hoc**: it was written after the
data and after the frozen scorer's run (step 13). A later lane commits the scorer's outputs beside this directory. This note edits no
committed file and changes no datum, forecast, rule, label or verdict, and it does not re-run the scorer. Its counts are printed by
`posthoc_note1_e215b.py` in this directory, run under `/usr/bin/python3` 3.12.3 at the lab's `fd8b0ef4`. The script reads committed files only,
each checked first: this directory's and arm A's step-6n report, judgement and labels (against each directory's `SHA256SUMS`), E215's
never-run candidates (against `SHA256SUMS-e215-registration`), and E217's registration tree, `tools/claims-v3/e217/` (95 of 95 files against
`SHA256SUMS-e217-registration`). It uses the registered scanners' own reader and patterns, loaded at their pins (`neverrun_e215.py`
`9e68b001`, `neverrun_e213.py` `d603ff8b`). Its printout is `posthoc-note1-e215b.txt` and its JSON `posthoc-note1-e215b.json`, both listed in
`SHA256SUMS-note1`. The counts are **desk arithmetic on committed records**.*

## 1. The line, and what it is

`neverrun-e215-card.txt` is step 6n's report from this arm's day, the scan of 13:41:38-13:41:49 PST. Its first two rows read:

- "arm A (aifoundry3 card 0): 5 of 60 scored points never ran; dropped ['a001', ... 'a052', 'a055', 'a058', 'a060']; references ['r01', 'r02']"
- "arm B (aifoundry1 card 1): 4 of 30 scored points never ran; dropped ['b001', ... 'b026']; references ['r11', 'r12']"

The registered scanner's report (`tools/claims-v3/e215/desk/neverrun_e215.py report`) always prints a row for **both** arms. The card tool
(`desk/neverrun_card_e215.py`) then judges **only its own day's arm**: `judge-e215-card.*` and `labels-e215.json` here are arm B's. So the
arm A row is the scanner's reading of arm A's 60 points at 13:41, 43 minutes after arm A's session ended. That session on aifoundry3 card 0
ran from 12:05:55 to 12:58:41 PST, and its data commit `8355db15` came at 13:00:32. **No rule reads the arm A row.**

**Arm A's judgement is its own step 6n**, committed in [its directory](../2026-11-19-e215-blind-matmul-aifoundry3/). That scan ran at
12:05:06-12:05:17 PST, before arm A's first card command (12:05:55). It read "NEVER-RUN-E215 arm A: 60 of 60 scored points never ran on any
card ...; ran before the freeze line (MM1-v3.1's land 2c971828), labelled: none; ran after it (REPORTED, kept): none", and its labels are
empty. The same report printed arm B's row then as 30 of 30.

## 2. What made the arm A row read 55 points otherwise

Every one of the 55 is met by a file of **E217's registration tree**. E217 is the model session's next sweep; its registration was committed
as `78b690b5` at 13:14:57 PST. The round's data lane for E217 holds a copy of that tree, and the scanner reads that lane's folder like any card
or data lane of the round. Arm B's own judgement in this directory dates two of the copies, `configs-e217.json` and `scan-e217.json`, at
13:14:57 PST by their modification time. The fix lane compared the copy with the committed tree: 96 of 96 files byte-equal, none changed
after 13:41:38.

| family (scored points) | read otherwise at 13:41 | the E217 file that meets the family's reading | what that file holds for them |
|---|---|---|---|
| L (a001-a020, 20) | 20 | `desk/configs-e217.json` | E217's never-run index lists each point's configuration (its shape and its shire mask) on a row whose status is "PLANNED (E215 arm A, registered; not run at this index)" |
| P, C, R (a021-a052, 32) | 32 | `desk/configs-e217.json` and `desk/scan-e217.json` | the same PLANNED rows; and E217's own scan, an index of where each shape appears, which holds these 32 shapes only in its class SUBTRACTED (files of E215's own folders, which E217's scan set apart) |
| S (a053-a060, 8) | 3: a055 (pow2), a058 (lanes2), a060 (bf16trunc) | `desk/card-record-e217.txt` | E217's copy of the cards' committed power record. Its card-1 rows include E212's committed gemmL1x1x1 runs with the pow2, lanes2 and bf16trunc tiles, as the hosts' run strings |

- **Why the copy of E212's runs counts for family S and the runs themselves do not.** Family S's reading counts a GEMM run record of the kind
  only from an experiment outside MM1-v3.1's data. E212's own records sit inside MM1-v3.1's data. Their copy sits in a folder whose name
  carries E217, so the reading took it for a record from outside.
- **The other five S points still read never run** at 13:41: a053 (i8_den6), a054 (i8_den3), a056 (den21), a057 (i8_pm1) and a059 (fp16grid).
  No E217 file holds a run string of their kinds.
- **The 62 rows of E215 arm A in `configs-e217.json`** (60 points and the references r01 and r02) all read "PLANNED (E215 arm A, registered; not
  run at this index)".
- **Nothing else moved arm A's row between the two scans.** For each of arm A's 62 rows, the scan counts the files that hold the row's shape.
  From arm A's scan (12:05) to this arm's (13:41), that count rose by exactly the number of E217 registration files holding the shape: 62 of
  62 rows.

## 3. What does not change

- **Arm A's step 6n stands as committed in its directory:** 60 of 60 never ran, labels empty. Arm A's scorer input is unchanged.
- **This arm's step 6n stands as printed:** 4 of 30, the 26 "ran after" readings REPORTED and kept (the README's departure 13 says why), labels
  empty. Its scorer input is unchanged.
- **No point, case, rule, forecast or verdict of either arm changes.**
- **None of the three E217 files is a run of an E215 arm A configuration.** One is a list of planned rows, one is a scan's index of where
  shapes appear, and one is a copy of E212's committed card-1 runs at another shape, gemmL1x1x1.

## 4. The scanner

The registered scanner reads the round's data lanes, so it read E217's registration copy. The same kind of reading met E213 arm B's day: E214's
registration and kit copies (that directory's dated note 1). E215's registered scanner stays as registered: it is pinned.

A scanner taught to skip these copies is committed beside E215's notes: E215's dated note 2,
[`tools/claims-v3/e215-notes/E215.md.dated-note-2.md`](../../../../tools/claims-v3/e215-notes/E215.md.dated-note-2.md), for later kits.
It skips copies of registration and desk trees, never-run desk files, PLANNED rows and copied power records. On the folders as they stood at
15:20 PST, it read arm A 60 of 60 and arm B 30 of 30 never run, where the registered scanner read 5 and 4. Every difference is a file it skips.

## What this note changes

Nothing measured, forecast, registered or scored. It adds five new files:

- this note;
- the script `posthoc_note1_e215b.py`;
- its printout, `posthoc-note1-e215b.txt`;
- its JSON, `posthoc-note1-e215b.json`;
- `SHA256SUMS-note1`, which lists the other four, plus `README.md` and `SHA256SUMS` as the data commit holds them.

Every committed file stands as committed. To reproduce, run `/usr/bin/python3 -I -B posthoc_note1_e215b.py --json <a new path>` from this
directory. It prints `posthoc-note1-e215b.txt` byte for byte and uses Python's own modules only.

SPDX-License-Identifier: Apache-2.0
