# E223 session a2c0-S3's data README, dated note 1 (Sat 21 Nov 2026; after the data verifier): check W1's FAIL is a reading at T0's whole second, and by the box's own file times the claim came first; two wordings of note 7 corrected (post hoc)

*Written on aifoundry2 from about 07:07 PST on Sat 21 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab box, no device and no post. It was written by the lab's lane `fix-e223d` of round Q239, after this directory's data verifier, `verify-e223d`. The verifier's verdict was "HOLDS WITH FIXES" (its record, REPORTED: with its own code it re-derived E223's three committed aifoundry2 card 0 sessions, 280 of 280 runs, from their raw files: 92,787 of 92,787 leaves equal, 87,061 of them numeric and bit-equal, and 0 mismatches; the committed session files equal the box's own by sha256, 909 of 909). It found two low fixes, and neither changes a datum or a verdict. Its finding 1 applies here (section 1); its finding 2 is about the folders of sessions a2c0-S1 and a2c0-S2. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `7d540724`, 04:48:44 PST Sat 21 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check verdict or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E223.md`](../../../../tools/claims-v3/e223/E223.md) and its proposal copy of the kit's source), **measured** (the session's records), **desk check** (this lane's runs of the committed code on copies of the committed files, and its timing on this box), **post hoc** (file times read on the box after the session, which are not in this directory), and **REPORTED** (verify-e223d's record, not re-run here).*

## 1. Check W1 reads FAIL at T0's whole second; by the box's file times the claim came first (verify-e223d's finding 1; low)

**What README.md says** (note 7, line 15; row W on line 41 and the verdict on line 46 read the same check): W1 reads FAIL by 0.080 s. The session's T0 is a whole second, `1795262908` (04:08:28.000 PST), and the claim post #16.4's stamp is 04:08:28.080 PST, so "by the records the session began at most 0.08 s before its claim was posted, or up to 0.92 s after it (T0 is cut to the second)". Those bounds are right. W1's rule, in `window_e223.py` (line 92, with T0 taken from queue.json's `t0` at line 65), is that the claim post's time comes before T0 and before the first card command. At T0's resolution it cannot hold here, and **W1's FAIL stays the check's reading**: the committed `window-e223-a2c0-S3.json` and `.txt` and row W are unchanged.

**The sub-second reading (post hoc).** In the registered `src/start_mms.sh`, T0 is the clock read at line 29 (`NOW=$(date +%s)`; line 37 copies it, `T0=$NOW`). After it the script tests the window's end (lines 30-31), runs `mkdir -p run sessions` (line 32), opens `run/box.lock` on file descriptor 9 and takes it with `flock -n` (lines 33-34), checks for the build record (line 35), and at line 36 starts the harness check with its output redirected into `run/harness-$NOW.txt`, a new file named by T0. The shell makes that file before the harness program starts. On this box, in the kit's top folder, the files' birth times read here with `stat` (read only) after the session:

| file (the kit's top folder on aifoundry2) | made by | born (PST, Sat 21 Nov) | after the claim post #16.4 (04:08:28.080) |
|---|---|---|---|
| `run/harness-1795262908.txt` | `start_mms.sh` line 36 | 04:08:28.663 | 0.583 s |
| `sessions/1795262908-a2c0-S3/` | line 39 | 04:08:28.680 | 0.600 s |
| `sessions/1795262908-a2c0-S3/session.log` | the runner | 04:08:28.727 | 0.647 s |

A file's birth time is set by the file system when the file is made, and no system call changes it afterwards (unlike its modify time). The `run/` folder's modify time in the data lane's two listings of the kit's folder, made at 04:10:13 and 04:46:20 PST, is the same instant as the harness file's birth, to the nanosecond: making the harness file was the last change to the names in that folder. This lane timed the same shell steps on this box, in its own work folder (lines 29-36, with `/bin/true` in place of the harness program, since the redirect comes before it): from a clock read just before line 29's `date` to the new file's birth took at most 2.4 ms over 200 runs (mean 1.5 ms; desk check). verify-e223d's own timing, over 30 runs, gave a mean of 0.42 ms and at most 0.87 ms (REPORTED). So **T0's clock was read at about 04:08:28.66 PST, about 0.58 s after the claim post's stamp: the claim came before the session's start.** The claim's lead before the first card command (04:08:32.022 PST), 3.942 s, is unchanged.

**Its premises.**

- The Discussion server's stamps and this box's clock agree to well within 0.58 s. This box's clock is kept by NTP (chrony reported it 0.3 ms from NTP time when read at 07:01 PST; its offset at 04:08 was not read). The server's clock cannot be read from here.
- Lines 29-36 took less than 0.58 s that time. By the timings above they take a few milliseconds.

Without the second premise, the box's files alone put T0's clock reading between 04:08:28.000 and 04:08:28.663 PST. Without either, note 7's bounds stand. These file times are not in the committed records (a commit keeps no file times, and the kit's harness file was not copied), so this reading is post hoc, and it does not change W1.

**The same reading for the box's two earlier E223 sessions** (their W1 PASS as committed): a2c0-S1's harness file was born at 02:50:35.973 PST, 3.801 s after its claim #16.2 (02:50:32.172; W1's whole-second lead 2.828 s), and a2c0-S2's at 03:30:35.307 PST, 0.692 s after #16.3 (03:30:34.615; 0.385 s).

**Two wordings of note 7 do not hold.** README.md stays as committed; read these two places as corrected here.

1. "a departure of the session from its claim, REPORTED". W1's FAIL is the check's reading at T0's whole second, and the committed records leave the order undecided within that second (note 7's own bounds). By the box's file times (post hoc), the session started about 0.58 s after the claim was posted. It was not a departure of the session from its claim.
2. "the kit's start script had taken the box lock before T0 (session.log line 2: 'held since src/start_mms.sh took it (handed over)'), at a time the session's records do not give". By the registered code, the start script read T0's clock first (line 29) and took the box lock after it (lines 33-34), then handed the lock to the runner (session.log line 2). The session's records do not give the lock's time. By the code it came after T0's clock reading, and the box's file times put it before 04:08:28.663 PST, the harness file's birth.

**What stays as it was:** every other line of README.md, including note 7's bounds and its sentence on W2-W7, row W, the verdict line ("W FAIL: W1_claim_first"), `window-e223-a2c0-S3.json` and `.txt`, BLIND (note 1) and every datum. **For later registrations** (verify-e223d's suggestion, not applied to this one): W1 could decide at T0's resolution (FAIL only when the claim post's whole second is after T0's), or read the birth time of the kit's `run/harness-<T0>.txt`. This note leaves the check's rule as it is.

## 2. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B window_e223.py session meta-e223-a2c0-S3.json ../../../../tools/claims-v3/e223/proposal/src --out window.json --txt window.txt
```

`window.json` and `window.txt` equal `window-e223-a2c0-S3.json` and `.txt` byte for byte (W1 FAIL at T0's whole second), in a checkout of this directory's data commit, which is also GitHub main `7d540724` when this note was written. It needs `python3` to be `/usr/bin/python3` 3.12.3 (the JSON files name the interpreter and its version). The sub-second reading cannot be reproduced from the repository, since it reads file times on the box. In the kit's top folder there: `stat -c '%w %n' run/harness-1795262908.txt sessions/1795262908-a2c0-S3 sessions/1795262908-a2c0-S3/session.log`.

SPDX-License-Identifier: Apache-2.0
