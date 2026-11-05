# E175's run kit, dated note 1: dated note A2's M1 reading after the collector, and the step test's v2 (Q143(g) fix pass)

*Written Thu 5 Nov 2026 (week 45), from about 14:50 PST, on the Intel, desk only: no card claimed, no device command sent, no lab box reached,
nothing posted, nothing measured. [`README.md`](README.md) and every file of the kit (lab `16b3d6e3`) stay as committed, and no box step, stop,
gate, protocol or bound changes. It answers two items from Q143(g)'s verifier, on the kinds page's
[section 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
- fault 1, the reading of E175-A2-M1, registered in [dated note A2](E175.md.dated-note-A2.md) beside E175.md;
- its fourth item: the step test's cleanup and count reached beyond the test's own processes.*

## 1. After step 7 (collect): dated note A2's M1 reading

Box step 7 (`... collect`) is unchanged. After it, at the desk and before the public-text scan and the data commit, the scoring lane runs
[`m1_reading_e175.py`](m1_reading_e175.py) on the collector's `results.json`, as dated note A2 section A2-4 gives it. It writes
`m1-reading.json` and `m1-reading.txt` into the same data directory, and both are committed with the data. **Exit 2** means the results' M1, or
its clock beside, is not the registered engine's on the results' own tiles: the data commit then waits until that is understood. The records
state E175-A2-M1 as A2-3 says:
- the verdict as registered;
- Bg's and Bp's means beside it, and E175-A2-M1c;
- a resolved M1 with the session's board on its own side is the session's board level, not evidence on D.

## 2. The step test, v2

`selftest_steps_e175.sh` (`16b3d6e3`) cleaned up between cases with `pkill -f 'sleep 3651'` and counted leftovers with
`pgrep -f 'sleep 3651'`, on the whole machine. That is the q142kg test form. Run beside another agent's test of the same form, it could kill
that test's stand-in processes or fail on them. (The verifier found no other such process before its own re-run, and there is no risk to a
card or a box.)

[`selftest_steps_e175_v2.sh`](selftest_steps_e175_v2.sh) is v1 with one change:
- every hang of its stand-in ssh runs under the run's own name (`exec -a e175v2-standin-<tag> sleep 3651`; the tag comes from the clock and
  the test shell's pid), and `clean()` and `none_left()` match only that name;
- v1's machine-wide pattern no longer matches v2's stand-ins either;
- a new case V0 shows that pgrep finds exactly the stand-in's pid by that name, and that it is gone after its kill;
- before each cleanup, the stand-ins of the run still alive are counted and printed, as information.

Every other line, case and bound is v1's.

**Re-tested** ([`logs/selftest-steps-v2.txt`](logs/selftest-steps-v2.txt)): ALL PASS, 36 of 36. v1's 34 lines are identical, line for line,
and V0 adds 2. None of the run's stand-ins was alive when any step returned (`rb_run.py` kills each call's process group itself), so v1's
cleanup was only ever a safety net. v1 stays committed and is not run again. Any later re-run of the step test uses v2. Nothing is needed for
E175's session.

## 3. Files (this note's commit; their sha256 in [`SHA256SUMS-e175-a2`](SHA256SUMS-e175-a2), from the repo top)

| file | what |
|---|---|
| [`E175.md.dated-note-A2.md`](E175.md.dated-note-A2.md) | dated note A2: M1's power and its reading |
| [`m1_power_e175.py`](m1_power_e175.py) → [`m1-power-e175.txt`](m1-power-e175.txt), [`m1-power-e175.json`](m1-power-e175.json) | M1's, M1c's and the clock beside's outcome shares at the registration's truths (design only) |
| [`m1_reading_e175.py`](m1_reading_e175.py) | the desk step after the collector |
| [`selftest_m1_reading_e175.py`](selftest_m1_reading_e175.py) → [`selftest-m1-reading.txt`](selftest-m1-reading.txt) | its self-test, 13 of 13 |
| [`selftest_steps_e175_v2.sh`](selftest_steps_e175_v2.sh) → [`logs/selftest-steps-v2.txt`](logs/selftest-steps-v2.txt) | the step test, v2: 36 of 36 |
| [`logs/dmcmd-audit-a2.txt`](logs/dmcmd-audit-a2.txt) | dmcmd_audit on the four new code files: GO, 0 send sites |
| `README.md.dated-note-1.md` | this note |
| `../../../docs/reports/data/2026-11-05-q143g-e175-design/README.md.dated-note-1.md` | the design README's three corrections and the lane's process disclosures |

Each job ran as a short local job at nice 10, one at a time. No lab box was used.

SPDX-License-Identifier: Apache-2.0
