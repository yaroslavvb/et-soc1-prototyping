# Dated note 1 beside E176's kit README (Thu 5 Nov 2026, about 12:50 PST, before any E176 data): which of the v3 drivers' safeguards apply

*Written beside [`README.md`](README.md) (lab `03582d2f`), not inside it; that file stays as committed. Desk only: no card, no device
command, no lab box, no post. No rule, stop, file of the kit or card-minute figure changes. The round's brief asked for each M11 kit to carry
"the v3 drivers' safety (watcher_q142s, the cc_gate, the desk-path gate, v3.1's steps ported, ours_live naming E176 and E177)". This note
says where each one is for E176.*

| safeguard | for E176 | where |
|---|---|---|
| **watcher_q142s** (`../hpl/watcher_q142s.py`, run_hpl.py's dated amendment) | **does not apply** | The race it fixes is run_hpl.py's: its watcher follows each run's new telemetry file, and a `follow()` between the path read and the file read can leave the stops reading an earlier run's file (E165's `telemetry_stale` end; `../hpl/run_hpl.py.dated-note-2.md` § 1). E176 does not run on run_hpl.py. Its runner is E166's over E97's card class, and `RealCard.latest()` (`../e97/run_e97b.py:71-72`, through `../e89/run_e89.py:60-74`'s `last_sample`) re-opens the one sampler file of the pass (`--tel-live`, started once per block by `block_e176.sh`) and reads its newest line each time. No file switch happens inside a pass, and a sampler older than 3 s ends the pass (E97's guard, `--stale-s 3.0`). An aifoundry2 run on run_hpl.py (E177, if kitted) installs watcher_q142s, as v3.1's README says. |
| **the cc_gate** | applies | `../q143k-runbook/s22_collect_q143k.sh`: v3.1's `ccdone_q142s.py` on `ccheck/ccheck-all.json`. The file must be there, hold ccheck.py's summary, and have been written since the step began, else 14. `collect_e176.sh` also empties its `ccheck/` first. The desk test covers it in C1, C2 and C5. |
| **the desk-path gate** | applies | the same step's `rb_nopath` (v3.1's `nopath_q142s.py`) over the data directory, else 16. The desk test covers it in C6. |
| **v3.1's steps ported** | applies | `../q143k-runbook/` (lab `92a1b27f`), steps 2-11, 20 and 22, from k6's and v3.1's, with the probe, the bounds, the login-link stop and its lock line. The desk test passes 20 of 20, and the dry listing makes no call. |
| **ours_live naming E176 and E177** | applies | `../q143k-runbook/rb_common.sh`: E176's session, block and runner; E177's queue, runner and session; and k6's E171-E174 names. The desk test covers it in O1, 10 of 10. |
| **dmcmd_audit GO** | applies | the kit, GO with 38 send sites ([`dmcmd-audit.txt`](dmcmd-audit.txt)); the runbook, GO with 11 send sites with E128's guard beside it (`../q143k-runbook/logs/dmcmd-audit.txt`) |

**The box steps of `README.md` map to the runbook's:**
- 1, the post: step 6, not scripted;
- 2, the sync: step 7;
- 3, the checks and reads: steps 8 and 9;
- 4, the dry pass: step 10;
- 5, the session: step 11;
- 6, the collection: step 22;
- with step 5's look first, and step 20's bounded waits.

SPDX-License-Identifier: Apache-2.0
