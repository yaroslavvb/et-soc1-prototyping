# The q142kg runbook, dated note 3: E173's departure D1 made a rule for a later collection (E175), before any E175 data (the E173 card lane's fix pass)

*Written Thu 5 Nov 2026 (week 45), about 14:35 PST, on the Intel, desk only, after E173's data commit (`ed8b5761`, 12:47:48 PST) and its
README fix (`571d0482`, 12:51:14 PST), and before any E175 data exists in any ref (`git log --all`: no `*e175-governed*` data directory, read
at this commit). It sits beside [`README.md`](README.md) (`5a2a9ba0`), [dated note 1](README.md.dated-note-1.md) (`34436d68`) and
[dated note 2](README.md.dated-note-2.md) (`6f4b48e4`), which stay as committed. It answers fault 2 of the verifier of E173's card lane
(`verify-card-a2-e173`, Thu 5 Nov 2026): "D1's remedy was chosen after the stop and is registered nowhere, and E175's new kit repeats E173's
route". The complaint it fixes is E173's departure D1, in [E173's data README](../../../docs/reports/data/2026-11-05-e173-blind8-aifoundry2/README.md)
§ "Registered against what happened", with its [dated note 1](../../../docs/reports/data/2026-11-05-e173-blind8-aifoundry2/README.md.dated-note-1.md).
It serves item 6 of the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

## Why a rule is needed

At 12:30:54 PST E173's collection stopped with 16 at v3.1's desk-path gate. The gate's own remedy reads "commit nothing; fix the route,
remove the outputs, collect again", but collecting again through the committed driver writes the same lines:

- `box/step_e173_v3.sh` line 24 hands the collector a raw copy under the day's directory outside the repo (`RAW=$RB_OUT/e173-raw`);
- the collector tees the C-log list with that copy's absolute paths into `$RAW/logs/cclist.txt` (`collect_e173_bounded.sh` line 86) and
  copies `logs/` into the data dir (line 96).

E173's lane replaced the `RB_OUT` prefix by `<RB_OUT>` in that one file and re-ran the two gates: a remedy chosen after the stop. E175's kit
(`16b3d6e3`) repeats the route line for line (`box/step_e175_v3.sh` line 187, `RAW=$RB_OUT/e175-raw`; `collect_e175_bounded.sh` lines 86
and 96), so its collection will stop at the same gate. This note registers that remedy, and nothing else, as the rule for it, before the data.
E174 is not affected: its driver hands its collector the relative `build/e174-raw` (`box/step_e174_v3.sh` lines 36-37), its list holds
relative paths, and its collection passed the desk-path gate at 13:18:58 PST.

## The rule

**It applies only when all of these hold:**
- a collect step of a v3 kg-form driver that hands its collector a raw copy under `$RB_OUT` stopped with 16 at the desk-path gate, and that
  stop is the step's last line in `$RB_OUT/runbook.log`;
- every hit the gate reads is in the data dir's `logs/cclist.txt`;
- every occurrence of `$RB_OUT` there is the prefix of a `REQUIRED` line's path, and the file holds only the list's own lines
  (`REQUIRED <session> <path>` and its `cclist:` summary);
- the data dir is not committed.

**What it does**, as [`d1mask_q142kg.sh`](d1mask_q142kg.sh) (with [`d1mask_q142kg.py`](d1mask_q142kg.py), which does the reads and the one
write), run from the top of the lab clone with the collect step's own `RB_OUT` and `RB_LOCK`:

```
bash tools/claims-v3/q142kg-runbook/d1mask_q142kg.sh E175 docs/reports/data/<day>-e175-governed-aifoundry2 aifoundry2
```

1. It reads the collect step's start, its probe line, from the runbook log. That time is the C-log gate's `--since`, as the step's own
   `t_cc` was.
2. It reads the desk-path gate again and checks that every hit is inside the rule.
3. It replaces that prefix by `<RB_OUT>`, the runbook's display form (`rb_disp`), in `logs/cclist.txt` only. The bytes as collected are kept
   in `<RB_OUT>/<run>-d1/cclist.txt.as-collected`. A manifest of the data dir before and after shows that no other file changed.
4. It re-runs the step's two gates through this runbook's own functions (`rb_common_v3.sh`):
   - the C-log gate: `cclist_q142kg_v3.py` on the data dir's runs, then v3.1's `ccdone_q142s.py` with that `--since`;
   - the desk-path gate over the whole data dir.

It prints and logs both sha256s of the list (as collected, and after) and exits 0 when both gates read clean.

**When it refuses or stops, `logs/cclist.txt` is left as collected (the rule writes no other file in the data dir):**
- **10, the rule does not apply:** a dry listing; the data dir or its list not there; the list committed; the collect step's last stop is
  not the desk-path gate's, or the step ran again after it; nothing to mask.
- **16, a hit outside the rule:** a hit in another file; a MISSING or UNREAD file; an absolute path not under `RB_OUT`; a line the list never
  prints.
- **After the mask, any failure puts back the bytes as collected:** another file changed; the C-log gate stopped (14); the desk-path gate
  stopped (16).

Then the gate's own remedy holds: commit nothing, fix the route, remove the outputs, collect again.

**What it never does.** It makes no remote call and sends nothing to a card. It touches no other file, and never a committed one: a
correction to committed data is a dated note beside it. **Nothing scored can change.** The collector scored the data dir's runs and checks of
C before the gate ran, and the rule writes none of them: it reads them only to hash them and to re-run the gates. `logs/cclist.txt` is the
collector's log of the list; the gate derives the list again from the data dir's runs.

## Who uses it

- **E175** (aifoundry2's governed line, Q143(g), kit `16b3d6e3`): if `box/step_e175_v3.sh collect` stops with 16 at the desk-path gate, run
  the line above with the same `RB_OUT` and `RB_LOCK`. On exit 0, record it in E175's data README as a departure under this note, with the
  two sha256s and the time. Then the login scrubs, the public-text scan and the commit. Any other stop takes the gate's own remedy. No other
  remedy is chosen after the stop.
- **E173** is collected and committed (`ed8b5761`). Its D1 (12:30:54-12:40:12 PST) was this rule applied by hand before it was written down;
  the desk test below replays it. The rule never runs on E173's committed files.
- **E174** never meets the rule (above).
- **A later port of a kg-form kit** should hand its collector a raw copy under the clone's `build/`, as E174's driver does, so the gate never
  stops on the list. No driver is changed here, so E175's kit stays as committed (its harness of 103 files and its frozen list of 33).

## Its desk test

[`selftest_d1mask_q142kg.sh`](selftest_d1mask_q142kg.sh) writes [`logs/selftest-d1mask.txt`](logs/selftest-d1mask.txt): **13 of 13 PASS**,
with 0 calls to the stand-in `ssh` and `rsync`.

**P1 replays E173's D1.** Its input is E173's data dir as committed at `571d0482`, read through `git archive` (never the work tree, so a
later note beside its README changes nothing), set back to its file set at 12:30:54 PST: 425 files, the count the gate read then.
- The gate reads 4 HIT lines, all in `logs/cclist.txt`, from 3 occurrences of `RB_OUT`.
- The rule's list equals the committed `logs/cclist.txt` byte for byte (sha256 `5273aabd…`), and of the 425 files only that one changed.
- The C-log gate reads 3 required (v2 3, v1 3), with 3 of 3 checks finished and all PASS. The desk-path gate reads 425 files, CLEAN.

**R1-R10 and U1 are the refusals and stops above.** In each the list is unchanged or put back. **U2** is the `--since` of E173's own re-gate:
the probe line's 12:17:15 PST reads 1793909835.

## Device commands

`dmcmd_audit.py` with no allow-list, over the three files and every file they source or call: **GO, 0 send sites**
([`logs/dmcmd-audit-d1mask.txt`](logs/dmcmd-audit-d1mask.txt)).

## Hashes

[`SHA256SUMS-d1mask`](SHA256SUMS-d1mask) lists the three files, this note and the two logs (check it from the top of the clone with
`shasum -a 256 -c`).

SPDX-License-Identifier: Apache-2.0
