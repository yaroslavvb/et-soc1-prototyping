# Dated note on E164's kit README `README.md` (Wed 4 Nov 2026, week 45, PST, after Q141(b)'s verifier; before any E164 data and before the claim)

Written beside the README and not inside it. [`README.md`](README.md) (`ce10e301`) stays as committed, and so does every file the box
runs: `harness-e164.json` is unchanged and still passes (`check_e164.py --desk`: HARNESS OK, 103 files). No E164 data exists, and no card
has been claimed. This note changes two box steps, 5 (the launch) and 7 (the collector), each to a new file, and corrects one figure.
The registration's own amendment is [`E164.md.dated-note.md`](E164.md.dated-note.md) (E164-A1). The desk checks are
[`selftest_notes_e164.py`](selftest_notes_e164.py), output in [`logs/selftest-notes.txt`](logs/selftest-notes.txt) (§ 1, 4, 8-10). It
answers faults 1 and 4 of Q141(b)'s verifier, and the interpreters of its fault 6.

## 1. Launch with `box/launch_e164_a1.sh`, never `box/launch_e164.sh` (the verifier's fault 1)

**The fault.** The usage line of `box/launch_e164.sh`, which step 5 points to, was:

```
ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' -- '<YYYY-MM-DD HH:MM PST>' < tools/claims-v3/e164/box/launch_e164.sh
```

ssh joins its command words with single spaces and the box's shell splits them again. The script therefore gets `$1` = the date, `$2` =
the time and `$3` = `PST`, and `DL=${1:?…}` keeps only the date: that day's 00:00, already past. `date -d` accepts it, and
`session_e164.sh` only checks that `E164_DEADLINE` is set. The session would open card 1, run the stop-path test and the smoke (about
1-1.5 card-minutes), and then `queue_e164.sh` would stop before p16410 and run no pass. The desk reproduces it (§ 1, case A: the
session sees only the date and the queue ends "done, 0 passes").

**The fix** is a new file, [`box/launch_e164_a1.sh`](box/launch_e164_a1.sh). `launch_e164.sh` is not in `harness-e164.json`, so
nothing is re-pinned, and it stays as committed. **Never use it.**
- The deadline is **all the arguments joined by spaces**, so the old line and the new one both give the whole string (§ 1, cases B, C).
- **The new usage line** puts the quoting inside the remote command:

  ```
  ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '<YYYY-MM-DD HH:MM PST>'" < tools/claims-v3/e164/box/launch_e164_a1.sh
  ```

  With the registered subset chosen before the launch, it is `"E164_DROP_P2=1 bash -s -- '<…>'"` (§ 1, case D).
- **It refuses before anything is launched:**
  - exit 2: no deadline, or not a date;
  - exit 4: fewer than **1,930 s** left, the scoring minimum of two passes even at the queue's 900 s first-pass estimate (about 120 s
    for the opening reads, the stop-path test, the smoke and its gate, then two passes and one 10 s gap). It is checked again after
    the harness check (§ 1, cases E, F; a deadline 2,000 s away launches, case G);
  - exit 3: anything holding card 1's nodes or lock, ours or another user's; anything of ours on either card, a node, a lock or a
    device process; or `et-holders` unreadable (cases J, L, M, N). This comes before the session's opening config read touches the
    card;
  - exit 9: `check_e164.py` not HARNESS OK.
- It prints the parsed deadline, in the box's zone and in Pacific time, and the passes to expect by the queue's own rule ("4 of the 4
  planned" for a deadline an hour away).
- It records the holders at launch as counts, never names, in `build/e164/holders-at-launch.txt`: whether card 0 was in use (E164-A1-2;
  case K launches with another user on card 0 and records it).
- It masks et-who's logins in what it prints. It sends no device command (§ 10: `dmcmd_audit` GO, 0 send sites).

**The emulation.** The box's shell is emulated with the script fed through a pipe, as over ssh's channel, into a sandbox laid out like
`~/nekko`. It has shims for `sudo`/`et-holders`, `ps`, `setsid` and GNU `date`, and a stub session that runs the committed
`queue_e164.sh` on a stub block. Feeding the script from a seekable file instead lets the detached session's fork move bash's read
offset, and the script re-runs lines; ssh's pipe cannot do that.

**Step 5 now reads:** after the day's post carries the reservation, run `box/launch_e164_a1.sh` with the new usage line and the deadline
(the round's time gate less 10 minutes).

## 2. Collect with `collect_e164_a1.sh` (the verifier's fault 4)

**The hazard.** `session_e164.sh` appends et-who's output to `build/e164/session.log` at the session's start and end (its lines 60 and
87). A block that finds someone on card 1 logs `lib.sh`'s or `block_e164.sh`'s "others present: … holders=[login:pid]" line there too.
`pull_e164.sh` copies those logs to the Intel, and `collect_e164.sh` (line 105) copies every one into the data directory bound for the
public lab repo. An et-who holder line carries a login and a command line. E164-A1-2 shows that another user can be on card 0 during the
session. The lab's privacy table is not on the Intel.

**The fix** is a new collector, [`collect_e164_a1.sh`](collect_e164_a1.sh). It runs `collect_e164.sh` unchanged, with the same
arguments, then:
- [`scrub_etwho_e164.py`](scrub_etwho_e164.py) on `<out>/logs/` rewrites other accounts' logins to `<another-user>` and withholds their
  command lines. That covers et-who holder lines, others-present lists, `/home/<login>/` paths, and any other whole-word mention of a
  login seen there. The owner's lines are kept, and so is every line that names nobody;
- the scrub's `--check` must read OK, or the collector exits 7 and nothing may be committed;
- the scrub writes `logs/et-who-summary.txt`, every et-who reading counted by card, ours and another user's, with no names;
- [`rank1_e164.py`](rank1_e164.py) writes `rank1-e164.json` (E164-RANK1, E164-A1-3).

At the desk (§ 4), a fixture with another account on card 0, in both others-present forms and in a `/home` path, comes out with no trace
of it, the owner's lines byte for byte, and the summary right. `--check` refuses the unscrubbed fixture, and two logins in the session's
own paths are refused. **E157's committed logs come through byte-identical**: nobody else was on the box that day.

**Step 7 now reads:**

```
bash tools/claims-v3/e164/box/pull_e164.sh
PY=/usr/bin/python3 PYS=<python 3.12 or later> E164_DATE=<the day> \
  nice -n 10 bash tools/claims-v3/e164/collect_e164_a1.sh build/e164-raw [<E163's e163.json> [<its C-excluded tiles> [<E163's scored.json>]]]
```

The records lane still reads `logs/` by eye before the data commit, as a backstop. `box/look_e164.sh` (step 1) and
`box/check_box_e164.sh` (step 3) print et-who's lines to the operator's terminal: read them, and never copy a name.

## 3. The interpreters on the day (the verifier's fault 6)

`PY` runs the reduction, which needs numpy: `/usr/bin/python3` (3.9.6, numpy 1.26.4) on the Intel. `PYS` runs `score_e164.py` and
`pair_rank4_e164.py`, which need Python 3.12 or later, as E157's scorer ran: `/usr/local/bin/python3.12`, or the Intel's `python3`
(3.13.11). The freeze's own interpreters are in E164-A1-5.

## 4. The card-minutes, recounted

The README says "about 56-58". Recounted from E157's measured session on this card (§ 8):
- E157's first pass started at T0+58 s, and its passes took 665, 675, 658 and 674 s for 78 launches.
- Scaled to E164's 98 launches, that is 836, 848, 827 and 847 s.
- With three 10 s gaps and the queue's sleep after the last pass, the session ends about T0+3,455 s: **57.6 card-minutes** (56.7-58.2
  at the shortest and longest pass). That is inside the 65-minute cap.
- The fourth pass starts inside the queue's 3,840 s limit, and a fifth does not fit.

The day's post keeps `for 1.5 h`.

## 5. The box steps, as they now read

1. Look (`box/look_e164.sh`), unchanged.
2. Sync (`box/sync_e164.sh`), unchanged. It copies `tools/claims-v3/e164/` to the box, the new files included, except `dry/`. None of
   them is pinned or run by the session.
3. Check on the box (`box/check_box_e164.sh`), unchanged.
4. The claim, the day's one post, unchanged.
5. **Launch with `box/launch_e164_a1.sh`** (§ 1).
6. Wait (`box/wait_e164.sh`), unchanged; then the post's release edit.
7. **Pull, then `collect_e164_a1.sh`** (§ 2).

**New files, all desk-checked:** `box/launch_e164_a1.sh`, `collect_e164_a1.sh`, `scrub_etwho_e164.py`, `rank1_e164.py`,
`selftest_notes_e164.py` → `logs/selftest-notes.txt`, `E164.md.dated-note.md` and this note. No tracked file changed. The kit's 58
committed files are unchanged. Every hash list still passes: `blind7/SHA256SUMS` 91 OK, `frozen-sha256-e168.json` 9 of 9,
`frozen-sha256-e168-scorer.txt` 18 of 18 and predict_q140e's 26 input hashes (§ 9).

SPDX-License-Identifier: Apache-2.0
