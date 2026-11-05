# Dated note 1 beside the q143k runbook's README (Thu 5 Nov 2026; Q143(k)'s fix pass): step 22 v2 collects E176, with a gate that requires the measured pass's C log and counts the checked launches against the marks

*Written on the Intel from about 14:35 PST on Thu 5 Nov 2026, desk only, before any E176 data: no E176 or E177 datum is in any ref. No card,
no device command, no lab box, no post. [`README.md`](README.md) and every file of lab `92a1b27f` stay as committed. This note answers the
verifier of Q143(k) (Thu 5 Nov 2026, about 12:52-13:30 PST), its fault 2: "step 22's cc_gate passes when the measured pass carries no C
log". For the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8.*

## What was wrong

`../e176/collect_e176.sh` skips a pass whose `c-log.jsonl` is empty or missing, and checks the rest. Step 22's `cc_gate` (v3.1's
`ccdone_q142s.py`) reads only whether the check's `--out` file finished. The verifier showed it end to end on a stand-in box: with the
smoke's C log there and the measured pass p17620's missing, the check read the smoke's 48 launches, ccdone passed, the scorer read rc 0, and
step 22 printed "E176 collected and scored". No measured hold's C was checked, against the README's "every launch was checked for C to the
end" and E176's dated note 1's "the cc_gate applies". The kg runbook's list of sessions that must carry a C log was not ported.

## What replaces it: step 22 v2

**Step 22 is now [`s22_collect_q143k_v2.sh`](s22_collect_q143k_v2.sh).** Never `s22_collect_q143k.sh`. It is v1 with four changes:
1. **First, before any box call,** it checks the v2 files as committed: `../m11/SHA256SUMS-score-m11-v2` (M11's scorer v2, lab `ebdbb35c`)
   and [`SHA256SUMS-q143k-v2`](SHA256SUMS-q143k-v2). A file that differs stops the step (16), and nothing is collected.
2. **The collector is [`../e176/collect_e176_v2.sh`](../e176/collect_e176_v2.sh):** v1 with M11's scorer v2 (`score_m11_v2.py`, with
   its lines file `scored-m11-lines.jsonl`), and a line naming each pass whose C log is absent or empty.
3. **After v3.1's cc_gate, the launch gate [`cclaunch_q143k.py`](cclaunch_q143k.py)** (standard library; it reads, and writes nothing):
   - p17620 is required. Its marks must be there and show a launch (else NO-LAUNCH: no hold ran, so nothing is scored), and its C log must
     have been collected (else MISSING-CLOG);
   - p17601's marks must be there, because the session runs the smoke before the measured pass. It is required whenever its marks show a
     launch;
   - for each required pass, the check's rows for its log must equal, process by process, the `records` each launch mark holds
     (`run_e176.py` writes `records=len(recs)`, the C records it logged). No row may fall outside every mark's window (else COUNT-SHORT,
     COUNT-OVER, ORPHAN or COUNT-UNREAD). A C FAIL in a matched row is not stopped here: it reaches the registered C rule.
   Any of these stops the step (14).
4. **"E176 collected and scored" only after both gates,** the login scrub check and the desk-path gate.

The rule holds on the lab's committed sessions of the same runner. On E166's (4 Nov) it reads 493 processes and 6,644 checked launches for
the measured pass, and 6 and 48 for the smoke. On E154's (3 Nov) it reads 474 and 6,288, and 7 and 58. Every process's records equal its
rows.

## Results

- **The desk test, [`logs/selftest-v2.txt`](logs/selftest-v2.txt): 24 of 24 PASS** (73 s;
  [`selftest_runbook_q143k_v2.sh`](selftest_runbook_q143k_v2.sh), with the data maker
  [`selftest_data_q143k.py`](selftest_data_q143k.py)). No lab box is reached: stand-in `ssh` and `rsync` serve a stand-in box.
  - **V1:** v1's own desk test, re-run unchanged: 20 of 20.
  - **A2:** the dry listing with step 22 v2: every step exits 0, with no ssh or rsync call.
  - **C1-C7:** v1's collection cases, ported to v2 (good 0; check crashed 14; failed copy 14; scorer not rc 0 14; stale check 14; desk
    path 16; stand-in without `RB_DESKTEST=1` 10).
  - **C8-C16, the new ones:**
    - C8, the measured pass with no C log while the smoke's is checked (the verifier's M1): 14, MISSING-CLOG p17620;
    - C9, a short check (one launch of the last process missing): 14, COUNT-SHORT;
    - C10, the smoke's launches with no C log: 14;
    - C11, the smoke with no launch and no C log: 0, NOT-REQUIRED;
    - C12, an orphan checked launch: 14;
    - C13, a measured pass that ran no launch: 14, NO-LAUNCH;
    - C14, an empty measured C log: 14;
    - C15, a launch mark without records: 14, COUNT-UNREAD;
    - C16, a v2 file that differs from its list: 16, before any box call.
  - **U1-U4:** the gate on E166's and E154's committed sessions renamed to E176's passes (0 and 0, with the counts above), and E166's
    without the measured C log, or one launch short (4 and 4).
  - **E1-E2, the real collector v2 end to end** (`ccheck.py` and `score_m11_v2.py` as committed). These run in a scratch tree of `tools/`,
    `workloads/` and `rtl-sim/fma_toggle_v2/` made by `git archive HEAD`, whose `docs/reports/data/*` are read-only links to the lab
    clone's, with ccheck's cache in the scratch. The stand-in box holds E154's committed passes, the measured pass's holds renamed to M11's.
    - E1, with both C logs: the check reads 6,346 launches, all PASS. The scorer reads rc 0, both passes read COUNT-OK, and the desk-path
      gate finds no path in the real scorer's outputs. The step says "E176 collected and scored", and the lines file holds stages 1, 2 and 3;
    - E2, with the measured pass's C log absent on the box: 14, MISSING-CLOG p17620. v1's step said "collected and scored" here.
- **The dry listing, [`logs/dry-listing-v2.txt`](logs/dry-listing-v2.txt)** ([`list_steps_q143k_v2.sh`](list_steps_q143k_v2.sh)): 12 step
  calls in order, each exit 0. It ran in the lab clone with logging stand-ins first on PATH, which saw no call.
- **Device commands** ([`logs/dmcmd-audit-v2.txt`](logs/dmcmd-audit-v2.txt)): `dmcmd_audit.py` on v1's steps, the v2 files and
  `collect_e176_v2.sh`, with E128's guard beside them, reads **GO, 11 send sites, 0 disallowed**, as v1's audit did. Without the guard
  ([`logs/dmcmd-audit-v2-bare.txt`](logs/dmcmd-audit-v2-bare.txt)) it reads NO-GO at exactly step 9's guard call, as v1's does. The v2 files
  alone send nothing (GO, 0 send sites).

## The steps on the day, as amended

The README's table stands, with row 22 replaced:

| step | file | what |
|---|---|---|
| 22 | `s22_collect_q143k_v2.sh [<earlier M11 pass dir> ...]` | the v2 lists checked; `collect_e176_v2.sh`; `cc_gate` (v3.1's `ccdone_q142s.py`); the launch gate (`cclaunch_q143k.py`); the login scrub check; the desk-path gate; "E176 collected and scored" |

- **At the go:** step 3 (`s03_desk_q143k.sh`) checks v1's lists only. Also run `shasum -a 256 -c` on
  `tools/claims-v3/m11/SHA256SUMS-score-m11-v2` and `tools/claims-v3/q143k-runbook/SHA256SUMS-q143k-v2`. Step 22 v2 checks both again
  before it collects.
- **E176's box step 6** (`../e176/README.md`, "on the Intel: `bash tools/claims-v3/e176/collect_e176.sh …`") is step 22 v2. The collector
  is never run alone: the step reads its rsync lines, the scorer's rc, the check's end and the launch gate.
- **Exit codes** are v1's.

## Files (new; [`SHA256SUMS-q143k-v2`](SHA256SUMS-q143k-v2) pins them)

- `s22_collect_q143k_v2.sh`, `cclaunch_q143k.py`, `list_steps_q143k_v2.sh`, `selftest_runbook_q143k_v2.sh`, `selftest_data_q143k.py`;
- `logs/selftest-v2.txt`, `logs/dry-listing-v2.txt`, `logs/dmcmd-audit-v2.txt`, `logs/dmcmd-audit-v2-bare.txt`;
- this note;
- `../e176/collect_e176_v2.sh` and `../e176/README.md.dated-note-2.md`;
- the list also pins `SHA256SUMS-q143k` (v1's), `../e176/kit-e176.sha256` and `../m11/SHA256SUMS-score-m11-v2`.

## What it does to predicting power and heat

Nothing to any number. A session scored by step 22 v2 is known to have computed every measured launch correctly, so M11's first
per-session reading of heat over minutes rests only on checked holds.

## Compute

The Intel, at nice 10 through the round's local slot, one job at a time:
- a quick run of the gate on the two committed sessions (14:38:53-14:38:57);
- the desk test, four runs, each 24 cases:
  - 14:44:14-14:45:19: E1 and E2 failed, because the scratch tree lacked `rtl-sim/fma_toggle_v2/`, where ccheck's engine source and one of
    M11's pins are;
  - 14:46:07-14:47:50 and 14:48:47-14:50:19: 24 of 24;
  - after the public-text scan read a variable name in `selftest_data_q143k.py` as its account word (renamed `bld`; nothing else
    changed), the committed run, 14:53:27-14:54:40: 24 of 24;
- the dry listing and the audits, in the same job as each of the last two runs. The dry listing's one hit of that class, step 8's runner
  option naming its tree, is v1's reviewed class, line for line as in `logs/dry-listing.txt`.

`ccheck.py` ran with `--jobs 2` inside the end-to-end cases; nothing else ran on more than one core. No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0
