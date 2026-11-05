# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 18:30 PST: E170's provenance in full, E170-W's registered line, and the day's post (E170's fix pass)

*This note sits beside [`README.md`](README.md), not inside it: the README stays as committed in `81178664` (17:36:18 PST). It records
what the verifier of the aifoundry1 scoring found in this README (Wed 4 Nov 2026, about 17:40–18:14 PST). Its verdict was "holds with
fixes". Several things hold:
- the box-side hashes equal git at the launch;
- the stops held, and every device command was a READ;
- the scorer of record, the C checks and the post hoc reader each re-make their committed output byte for byte (`score.txt` but for its
  output-path line);
- the order, the window, the post and the privacy hold.

Its items are a disclosure and a wording point. This is desk work: no verdict, number, band, prediction, rule or frozen file changes, no
device command is involved, and nothing in this note was registered. It answers the same items as the README: the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6, the Q139 critic's ranks 1 and 4, and
the Q138 critic's rank 5.*

## 1. Provenance: no verifier read the last two kit commits, and one of them edited kit files in place

The README's § Registered before any data lists amendment E170-A2 (`6147a9c7`, 16:08:53 PST) and the kit's corrections (`0e35ec58`,
16:09:38), "every commit before any E170 data, claim or launch". That holds. The launch was at 16:19:41, and no ref holds E170 data before
`81178664`. The README leaves three things unsaid.

- **No independent verifier read either commit before the launch.** The round's brief asked that E170 be "verified before it runs". Its
  desk verifier wrote its verdict at 15:47 PST, before both commits, which answer it. Before launching, the card lane read
  `box/launch_e170.sh`'s diff (`57e1c6c4` to `0e35ec58`) and A2's § A2-1.
- **`0e35ec58` edited four kit files in place**, where Q141's practice was new files only. The files are the kit's
  [`README.md`](../../../../tools/claims-v3/e170/README.md), `box/launch_e170.sh`, `harness-e170.json` (one line: the launcher's pin) and
  `selftest_kit_e170.py`. It also added five logs (`git show --name-status 0e35ec58`). All four edits came before any data. They add
  refusals to the launcher and change no measurement, rule, prediction or scorer:
  - exit 6 outside the round's window (a start after 18:15 PST, or a deadline after 19:00 PST);
  - exit 3 while a run queue or session of ours is alive;
  - the registered subset's 30-minute slot.

  The kit self-test gained six cases for them.
- **Every registration file, scorer, protocol and prediction is as registered.** `git log` on each path shows one commit each:
  - `b5ca3e78` (14:41:25): `E170.md`, `e170_common.py`, `predictions-e170.json` and `.txt`, and `make_predictions_e170.py`;
  - `574dc5b5` (14:48:30): `score_e170.py`;
  - `57e1c6c4` (15:13:43): `score_e170_a1.py`, the five protocols, `run_e170.py`, `queue_e170.py`, the guard, `check_e170.py` and
    `collect_e170.sh`.

  A1 and A2 are new files. The hashes the box recorded at the launch equal git at `efaaa726`, the lab's main at the launch (the verifier's
  check). `0e35ec58` is an ancestor of `efaaa726`. `check_e170.py --desk` reads HARNESS OK 107 at the desk now.

**The disclosure, as the records should state it:** *"E170 ran on a kit whose last two pre-launch commits had no independent verifier read:
A2 (`6147a9c7`), and the kit's corrections (`0e35ec58`), which edited four kit files in place before any data. The card lane read the
launch diff. Every registration file, scorer, protocol and prediction is as registered."*

## 2. E170-W's line: the registered rule applied, not the printed planning figure

The README's § Results quotes E170-W's line as [0.599, 1.040] W, the line the scorer of record applied (`score.txt`: `"range": [0.5988,
1.0398]`). [`E170.md`](../../../../tools/claims-v3/e170/E170.md) prints "0.602-1.045 W at n = 39" in its rules table and in § Precision,
before the data, and A2-1 quotes its upper end, 1.045 W. That figure is `make_predictions_e170.py`'s planning estimate, made at 4,000 draws
(line 93). The registered rule is E170.md's own definition of "Bootstrap": "the 2.5–97.5% range of the rms of n errors drawn with
replacement from the reference errors (20,000 draws, seeded 170)". `e170_common.BOOT_DRAWS` = 20000 carries it, and `score_e170.py` applies
it.

Re-computed at the desk with the committed `e170_common.boot_rms_range`, on the same reference (Q140(l)'s 42 end-to-end pinned board errors)
and seed 170, at n = 39:

| draws | line, W |
|---|---|
| 4,000 (planning: E170.md's printed figure) | [0.6021, 1.0448] |
| 20,000 (the registered rule, as applied) | [0.5988, 1.0398] |

The verdict is PASS under either: 0.7274 W.

**As the records should state it:** *"E170-W PASS: board rms 0.727 W over 39 tiles against the registered rule's line, [0.599, 1.040] W
(20,000 draws, seed 170). E170.md's printed 0.602–1.045 W is its 4,000-draw planning estimate of the same line."* E170.md prints no other
bootstrap line as a number: E170-F's and E170-H1's rows name only their reference errors.

## 3. The day's post, after this README's account

The README's § Card and post ends: *"... aifoundry2's kept word for word as the last one held, so no " — released" yet"*. That was true at
16:50:15. At 17:18:22 PST aifoundry2's lane appended " — released" to message `1567662592850399304`. Every word was kept, and it worked under
the Discord lock with `EXPECT_TEXT` and read the post back. The post now reads `<ai> **Claude says:** using aifoundry2 for 4.25 h, until
~18:26 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released`. The post's day, in full:
- 14:11:27: claimed with three clauses.
- 16:38:11: aifoundry3's clause dropped.
- 16:50:09–15: aifoundry1's clause dropped, by E170's lane.
- 17:18:22: " — released" appended.

## 4. How this note was checked

- The provenance: `git show --name-status 0e35ec58`, `git log` on each E170 kit path, `git merge-base --is-ancestor 0e35ec58 efaaa726`,
  and `check_e170.py --desk` (HARNESS OK 107).
- The line: a desk script that imports `e170_common` and calls `boot_rms_range` on `predictions-e170.json` › `reference` ›
  `pinned_board_w_err` at 4,000 and 20,000 draws (seconds, one core, nice 10).
- No file in this directory was edited or re-made. The scrub's `--check` reads 0 left on `logs/` and on the whole directory.

SPDX-License-Identifier: Apache-2.0
