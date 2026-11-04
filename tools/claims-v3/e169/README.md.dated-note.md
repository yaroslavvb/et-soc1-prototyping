# Dated note on E169's kit README (Wed 4 Nov 2026, week 45, Q141(s)'s fix pass, after the lane's verifier)

*This note is written beside [`README.md`](README.md), not inside it. The README stays as committed in `6a3929ec`. Where the two
differ, this note holds. It is written before any E169 data or claim, and it answers faults 2, 3, 4 and 6 of the lane's verifier. It
changes no rule, prediction or code. The registration's own clarifications (a negative step, a pass split across sessions, B7's
convention, the tree checked) are in [`REGISTRATION-A2.md.dated-note-2.md`](REGISTRATION-A2.md.dated-note-2.md).
[`selftest_notes_e169.py`](selftest_notes_e169.py) → [`selftest-notes.txt`](selftest-notes.txt) checks every claim here.*

## Box step 2 (the tree): also check the zero tiles

After `shasum -a 256 -c frozen-sha256-e169.txt`, run this in `tools/claims-v3/e169`:

```
shasum -a 256 -c frozen-sha256-e169-tiles.txt          # 3 OK
```

- **What the tiles are.** Every cell, the smoke and both stop tests read one of three tiles,
  `tools/claims-v3/kinds/tiles/{fp32,fp16,int8}/zeros.bin`. Each is 2,048 bytes, every byte zero, unchanged since `654ee2ce` (31 Oct
  2026).
- **Why they need the check.** Neither the 54-file list nor E146's preflight pinned them. R0's check of C could not catch a changed
  tile, because the host's reference reads the same tile.
- **On a mismatch,** the box steps stop and the queue does not start (selftest-notes.txt § 4).

## Box step 4 (the dry pass on the box): its own directory and slot file

**What went wrong.** Step 4 named neither a run directory nor a slot file. Suppose a dry pass wrote into `build/e169/runs`. Its
`smoke/`, `stoptest-*/` and `s1/` would each hold a session, so the real queue's runner would refuse each one (exit 2, "already holds a
session"). The queue's smoke check would then read the dry records left there and halt the queue on their cycles: the toy card's 546
per op against the frozen 1,596.6-1,700.5. No session would run, and the slot would be lost (selftest-notes.txt § 3).

**Step 4 now reads**, from the top of the lab checkout on aifoundry2. Run it as one script file through `ssh … 'bash -s' < file`,
never inside `bash -c`:

```
mkdir -p build/e169
now=$(date +%s)
printf 'SLOT E169: start %s (dry pass on the box) end %s (one hour later) \n' "$now" "$((now + 3600))" > ~/claude/work/q141-a2-e169-dry-slot.txt
nice -n 10 python3 -B tools/claims-v3/e169/queue_e169.py --dry --slots ~/claude/work/q141-a2-e169-dry-slot.txt --runs build/e169/dry \
  --protocol tools/claims-v3/e169/protocol-dry.json --stoptest-board tools/claims-v3/e169/protocol-stoptest-board-dry.json \
  --stoptest-die tools/claims-v3/e169/protocol-stoptest-die-dry.json > build/e169/dry.out 2>&1 < /dev/null
nice -n 10 python3 -B tools/claims-v3/e169/score_e169.py build/e169/dry/s[1-6] --out build/e169/dry-results.json > build/e169/dry-score.txt
test ! -e build/e169/runs && echo "the real run directory is empty"
```

- **It passes when:**
  - the queue exits 0, and `build/e169/dry/queue.jsonl` shows the smoke check and both stop-path checks with `bad` null, `s1_end` rc 0
    and `queue_end`, over 50 runs;
  - the scorer exits 0, with every verdict labelled DRY;
  - `build/e169/runs` does not exist, so step 5's queue starts in an empty directory.
- **Its slot line** needs the space after the end time: the queue's slot pattern ends `end (\d+) `.
- **`mkdir -p build/e169`** also makes the directory that step 5's `> build/e169/queue.out` writes into. Bash opens that file before the
  queue starts, so without the directory the queue would not start.
- **When to run it.** It takes about 5 minutes. Run it before the day's first card session on aifoundry2, or between two of them,
  never while one runs. It uses little CPU, but it is still load on the host during a measurement.
- **The dry records stay** in `build/e169/dry` and are never collected: step 7 copies `build/e169/runs` only.
- **Rehearsed on the Intel** in an archive copy of the tree, exactly as written above, with `~/claude/work` standing in a scratch
  directory: [`logs/dry-box-step4.txt`](logs/dry-box-step4.txt).

## Box step 7 (collect and score): every session directory

**What went wrong.** Step 7 scored `<dir>/s1` only. If another user's login ends a session, the queue resumes as `s2` (up to `s6`), and
those runs would be left out.

**Step 7 now reads:**

```
python3 -B tools/claims-v3/e169/score_e169.py docs/reports/data/<date>-e169-stride-shapes/aifoundry2/s[1-6] \
  --out docs/reports/data/<date>-e169-stride-shapes/results.json > docs/reports/data/<date>-e169-stride-shapes/score.txt
```

- **The glob** expands to every session directory the queue wrote, in order. It never matches `smoke/`, `stoptest-board/`,
  `stoptest-die/` or a session moved aside as `s<k>.refused<n>`.
- **A split pass counts.** A pass whose two bursts fall in two sessions still counts (note 2, item 2), and the run's README names each
  one. A negative step reads as note 2, item 1 says.
- **What to collect.** Copy `build/e169/runs` only, never `build/e169/dry`.
- **Checked:** the scorer on E158's session cut in two gives E158's committed numbers and verdicts (selftest-notes.txt § 2).

## The self-test's count

`README.md`, and its own dated note, say "22 made-up truths read as built (42 checks in all)". Those 22 are checks.

- **Part 3** of [`selftest.txt`](selftest.txt) makes **22 checks on 17 made-up reductions** (calls of `score()`). SM's truth carries 4
  checks, ISO's 3 (the floor's among them), and every other truth 1.
- **Parts 1 and 2** make 20 more, on E158's committed data, so **42 in all**.
- **How to cite it.** Records say "42 checks, 22 of them on 17 made-up truths" (selftest-notes.txt § 6). The lane's verifier counted
  18; it took the floor's check, which reads ISO's reduction, as a case of its own. Commit `18aaca80`'s message says 23, and it stays
  as pushed.

## What this fix pass adds (all new files; no tracked file is edited)

| file | what |
|---|---|
| [`REGISTRATION-A2.md.dated-note-2.md`](REGISTRATION-A2.md.dated-note-2.md) | the registration's dated note 2: a negative step, a split pass, B7's convention, the tree checked, the first note's time |
| this note | box steps 2, 4 and 7, and the count |
| [`frozen-sha256-e169-tiles.txt`](frozen-sha256-e169-tiles.txt) | the three zero tiles' sha256, checked in box step 2 |
| [`selftest_notes_e169.py`](selftest_notes_e169.py) → [`selftest-notes.txt`](selftest-notes.txt) | the notes' self-test, desk only (it refuses a host with an ET-SoC-1 device node) |
| [`logs/dry-box-step4.txt`](logs/dry-box-step4.txt) | step 4 rehearsed on the Intel |
