# E213's kit, as amended by A2 for ARM B: steps 4, 9 and 12's first half on aifoundry1 card 1 (Q219; written before any datum of arm B)

*Wed 18 Nov 2026 (week 47), PST, on aifoundry2, at the desk (Q219, lane `a2-e213`). The amendment is
[`E213.md.dated-amendment-A2.md`](E213.md.dated-amendment-A2.md); this file is its kit patch, new files only under `tools/claims-v3/e213-a2/`.
The kit (`tools/claims-v3/e213/`, `6efdb002`) and its CARD-LANE-BRIEF stay as committed and govern every other step. Arm A: no change.
**Fixed before the land** by Q219's `fix-a2e213` (Wed 18 Nov 2026, from 11:07 PST, before any datum of arm B), answering `verify-a2e213`'s
findings 1 and 2: the never-run scan's place beside the read (row 4) and the evidence of the one call (row 4, item 7e; row 12); section 5.*

## 1. What arm B's card lane runs in place of the kit's three rows

| row | the kit's (unchanged, still committed) | A2's (arm B only) |
|---|---|---|
| 4 | `bash tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh aifoundry1` | `bash tools/claims-v3/e213-a2/rb/s05_look_e213_a2.sh B` |
| 9 | `bash tools/claims-v3/e213/rb/s11_session_e213.sh B` | `bash tools/claims-v3/e213-a2/rb/s11_session_e213_a2.sh B` |
| 12, first half | `bash <W>/slot.sh bash tools/claims-v3/e213/rb/s23_data_e213.sh B` | `bash <W>/slot.sh bash tools/claims-v3/e213-a2/rb/s23_data_e213_a2.sh B` |

Every other row (B, 0, H, 1, 2, 3, 5, 6, 6n, 7, 8, 10, 11, 12's commit, 13, E), every span (THE ONE-LAB RULE's desk and collect, THE QUIET
HOLD), every bound and every stop path stay the kit's. Each A2 step refuses arm A (10) and a window written for another arm or runbook (10).

### Row 4 (A2): the look, and on NEEDS-READ the one firmware read

In this order, nothing synced or read before the gate above it passes:
1. the window (today, E213, arm B) and the last start;
2. **the pins at the desk**: `fwgate.py`, its six records and A2's helper committed, unmodified (`git status`) and at their sha256 in the lab
   clone (`rb/rb_e213_a2.sh`), else 16;
3. **the holder rule**: k6's own look with `--wait` (k6 reads no identity under `--wait`), unchanged: 0 FREE goes on; 17, 15, 11, 12, 13, 14 are
   this step's exits, as in the kit's row 4 (17: call this step again, bounded; 15: no session today); it writes `RB_OUT/box-login-aifoundry1.txt`;
4. **A2's box files into the box's tree** (nekko) by one `rsync -a -c -R -i` at their committed bytes, then `sha256sum -c` of the pinned list
   on the box: `A2-PINS OK 8 of 8`, else 16;
5. **fwgate's look** (`fwgate_e213a2.py look`, no device): CONTINUITY: no read; NEEDS-READ: item 6; anything else 16;
6. **on NEEDS-READ only, one box call** (600 s bound): THE REST RULE (a refusal: 10, nothing sent; wait in bounded chunks and run row 4 again);
   then `et-who --check` polled every 10 s for at most 400 s until both cards read free (still held: 17, nothing read; 15 once held 30 minutes in
   all, `RB_OUT/hold-a2-aifoundry1.since`); then **one** `fwgate_e213a2.py read` (`fwgate.py read --box aifoundry1 --card 1 --both-nodes-ok
   --out build/e213/fwgate-B-<day>`, ET_DEVICES removed): `A2-READ: EQUAL <record>` passes, **anything else 16 and arm B has no session on
   this boot**;
7. the read's folder (when the box holds one) **copied back** into `RB_OUT/e213-a2-fwgate-B/`, checked file by file against the box's sha256
   list (`RB_OUT/e213-a2-fwgate-B.sha256`), and **THE SCRUB CHECK** on it (`collect_e213.py scrub-check`, the box's home in every form read in
   the same call, `RB_OUT/box-home-B-a2.txt`): CLEAN, else 16;
   7e. **THE EVIDENCE OF THE ONE CALL** (fix-a2e213): in item 7's listing call, read only, `fwgate_e213a2.py evidence` under a plain
   `timeout 20` (no device, no fwgate call, nothing written) prints this boot's lines of fwgate's ledger and of the kit's attempt log, verbatim;
   the desk writes them into `RB_OUT/e213-a2-evidence-B/` (`fwgate-ledger-aifoundry1-c1-this-boot.jsonl`,
   `a2-fwgate-attempts-aifoundry1-c1-this-boot.jsonl`) with their list `RB_OUT/e213-a2-evidence-B.sha256`, and the reading ("one call on
   this boot, ended EQUAL"; "no call on this boot" on a day of continuity by the boot) into the runbook log (`A2-EVIDENCE-B:`) and the look
   file. **Never a gate:** a capture that fails says "evidence NOT CAPTURED by this call" there, keeps an earlier capture, and the step goes on;
8. `RB_OUT/e213-a2-look-B.txt`: `A2-LOOK-B: CONTINUITY: ...` or `A2-LOOK-B: EQUAL <record>; ...` (row 9 requires it from today).

**The read and the never-run scan** (fix-a2e213, verify-a2e213's finding 1): the read at item 6 is a card command for THE REST RULE alone
(the rule runs before it). For E213.md section 4's never-run scan ("right before their first card command") and step 7's 30-minute check of
step 6n's report, **the day's first card command stays step 7's config read**: step 6n still runs right before it, in the kit's order; the read
runs no GEMM and starts no point; the session's card time counts from the session's own first card command.

**Exits:** 0 pass; 10 refused (usage, arm A, the window, the rest not open before the read: nothing sent); 11 a login link; 12 no answer; 13 past
a bound (if it came during the read's call, the read's outcome is the box's: the kit's attempt log or fwgate's ledger then stops any later read on
this boot: row E); 14 a call failed; 15 held 30 minutes in all; **16 a gate says stop: row E, no session on this boot, tell the orchestrator,
never a second read**; 17 held: call row 4 again (nothing read). A call after an EQUAL read the same day reads CONTINUITY (this boot's EQUAL
record of today, read with `--extra`) and copies the folder back again: no second read. A second try the same day in a new RB_OUT (the kit's
section 3) runs row 4 again first, which then reads CONTINUITY.

### Row 9 (A2): the launch past fwgate's guard

The kit's `s11_session_e213.sh` line for line, but: arm B only; `RB_OUT/e213-a2-look-B.txt` from today required before anything reaches the box
(10); and in the one launch call, in place of k6's `rb_guard_text`, A2's guard: k6's two refusals verbatim (a dry pass of the runbook running, a
session of ours running), the pinned list `sha256sum -c` on the box, then `fwgate.py guard --box aifoundry1 --card 1 --extra
build/e213/fwgate-B-<day>`: `identity: ... ok` and `A2-GUARD: ...` go on to THE REST RULE, THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and
build and the launch, as the kit's; **IDENTITY-STOP: nothing launched, 16** (the step reads the guard's own words; row E; no session on this boot).
Like the kit's row 9 it never runs while THE QUIET DESK FLAG stands (its name holds `session_e213`).

### Row 12, first half (A2)

The kit's `s23_data_e213.sh B`, unchanged, as a child; then `data_e213a2.py add`: step 4's copy checked again against its list, copied into the
directory as `fwgate/`, scrubbed by the kit's own `collect_e213.py` functions (the record's ledger path's home -> `~`; nothing may be left),
checked (one fwgate read record, EQUAL, aifoundry1 card 1, its raw answer at the sha256 it names), then **step 4's evidence of the one call
beside it** (fix-a2e213: `RB_OUT/e213-a2-evidence-B/`, checked against its list, as `fwgate/fwgate-ledger-aifoundry1-c1-this-boot.jsonl` and
`fwgate/a2-fwgate-attempts-aifoundry1-c1-this-boot.jsonl`, through the same scrub: the ledger lines' record paths' home -> `~`; missing,
changed since step 4, not whole or not clean after the scrub: left out and said in the `A2-DATA ADDED` line, **never a refusal**), and the
directory's `SHA256SUMS` made again over every file in the kit's form and read back; then the desk-path gate and the history check again. Run
it right after row 11, **before the README**. Exits: the kit's step 12's, then 16 if A2's addition is refused (commit nothing). On a continuity
day nothing is added.

**The data README** (DATA-README-FORM-e213.md's form) adds, among the DATED DEPARTURES: "Amendment A2 (arm B only): card 1's firmware identity
shown on this boot by fwgate - its look NEEDS-READ, one read with `--both-nodes-ok` (the owner's word: his rulings of Sun 15 Nov 2026 15:07:01
and 15:09:49 PST), EQUAL to E82's read in all seven fields - and fwgate's guard at the launch; card 0's management node opened only within that
one call; the record in `fwgate/`, with this boot's fwgate ledger lines and the kit's attempt-log lines beside it" (or, if step 12 said so,
"the evidence of the one call left out: <its words>"). In "Device commands sent": the one `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` (READ,
`dmcmd_table_v2.json` id 14) with its time, rc and both locks, beside the session's own reads.

## 2. Files

| file | what |
|---|---|
| `E213.md.dated-amendment-A2.md` | the amendment (arm B only) |
| `KIT-A2.md` | this file |
| `fwgate_e213a2.py` | on the box: `look` and `read` around `fwgate.py`, the kit's attempt log `build/e213/a2-fwgate-attempts-aifoundry1-c1.jsonl`; `evidence` (fix-a2e213: read only, this boot's ledger and attempt-log lines); Python's own modules |
| `data_e213a2.py` | at the desk: row 12's addition, with step 4's evidence beside the record (imports the kit's `collect_e213.py`, unchanged) |
| `rb/rb_e213_a2.sh` | sources `tools/claims-v3/e213/rb/rb_e213.sh` unchanged; the pins, `e213a2_dir`, `e213a2_check_desk`, `e213a2_pins_box_text`, `e213a2_guard_text` |
| `rb/s05_look_e213_a2.sh`, `rb/s11_session_e213_a2.sh`, `rb/s23_data_e213_a2.sh` | rows 4, 9 and 12's first half (section 1) |
| `rb/list_steps_e213_a2.sh` | arm B's dry listing as amended |
| `desk/selftest_a2_e213.sh` | the desk test (section 3) |
| `logs/selftest-a2-e213.txt`, `logs/test-fwgate-a2.txt`, `logs/dmcmd-audit-a2.txt`, `logs/dry-listing-a2-B.txt`, `logs/e213-checks-a2.txt` | the final runs |
| `SHA256SUMS-e213-a2` | every file above but itself, from the lab's top |

**The pins** (`rb/rb_e213_a2.sh`, `e213a2_pins_text`): `fwgate.py` `4d529a57...` and its six records at their sha256 as landed in `d5beec9b`, and
`fwgate_e213a2.py` at its own. **On aifoundry1, A2 writes only:** `tools/claims-v3/fwgate/fwgate.py`, its six `records/*.json` and
`tools/claims-v3/e213-a2/fwgate_e213a2.py` in the box's tree, at their committed bytes; `build/e213/fwgate-B-<day>/` (the read's folder),
`build/e213/a2-fwgate-attempts-aifoundry1-c1.jsonl` and `build/e213/a2-pins.sha256`; and fwgate writes its own ledger
`.local/state/fwgate/aifoundry1-c1.jsonl` under the account's home (outside the tree). The evidence call (row 4, item 7e) reads that ledger and
the attempt log and writes nothing.

## 3. The desk tests (`desk/selftest_a2_e213.sh`)

The kit's runbook-test form: stand-ins for the remote shell and rsync, a stand-in aifoundry1 box per case (its own tree, lock folder, ledger and RB_OUT), k6's
bounded runner and the kit's own steps around A2's, the private PID namespace; fwgate's desk-test stand-ins as its README requires
(`FWGATE_DESK_TEST=1` and every stand-in: its own `tests/fwcli-standin` and `tests/etwho-standin`, a lock folder with both lock files, the ledger
under the stand-in box's home, `FWGATE_HOSTNAME`, `FWGATE_BOOT_EPOCH`, `FWGATE_BOOT_ID`); the stand-in CLI answers with E82's committed answer
(EQUAL), with card 0's PMIC (DIFFERENT) or without its success line (UNREADABLE); **the boxes boot after E82's read** (2026-11-17 16:46:32 PST)
but in the continuity case (2026-10-26 15:18:24 PDT); the box shell carries `ET_DEVICES=1`. Cases (31 checks): NE, NC, NL (EQUAL, again
CONTINUITY, the launch); CT (continuity, no read, the launch); DF, UR, CS, BL, BW, ML (DIFFERENT, UNREADABLE, a cut-off SENT, a busy lock, a busy
et-who, a missing lock file: each 16, a second row 4 16 with no second read, and row 9 with a forced look file IDENTITY-STOP with the stand-in
session not started); NG, SB, SD (the guard with no EQUAL of this boot, a stale EQUAL of an earlier boot, of an earlier day: IDENTITY-STOP); RS
(the rest rule before the read: 10 then EQUAL); BH (both cards held before the read: 17, nothing read, then EQUAL); PB, PD (the pins on the box
and at the desk); AA (arm A refused); DT (row 12's addition: added and read back; continuity adds nothing; a changed copy and another login's home
refused with SHA256SUMS untouched; a path not arm B's refused); DRY (the dry listing); Z (nothing left running). **fix-a2e213's 8 checks (the
evidence of the one call; 39 in all):** NE-EV (after NE: RB_OUT's capture holds this boot's ledger lines SENT and END EQUAL and attempt-log
lines ATTEMPT and END EQUAL, its list OK, "one call on this boot, ended EQUAL" in the runbook log and the look file); NC-EV (the same after
CONTINUITY); CT-EV (no line on a day of continuity by the boot); EV (the evidence call failing on the box, by a stand-in box `python3` that
refuses the `evidence` subcommand alone: step 4 still EQUAL, "evidence NOT CAPTURED" said, no capture made, step 9 launches: never a gate); EVX
(the helper alone on a copy of NE's files: this boot's lines only, another boot's left out, a line of another form named, a second SENT read
as "NOT one EQUAL call", another host refused with nothing printed, the files unchanged); DT f-h (row 12 with the capture: added beside the
record, the ledger lines' home masked as `~`, SHA256SUMS read back; changed since step 4: left out and said; another login's home in it: left
out by the scrub's check and said; the record committed in each). Run it only inside a sandbox with
no card node and an empty `/run/lock` (the round's nodev.sh), never while THE QUIET DESK FLAG stands: its launch cases start a stand-in script
named `session_e213.sh`.

## 4. Found while writing A2 (REPORTED, for the readiness lane and the orchestrator)

1. **The never-run scanner subtracts E213's card lanes by name**: `desk/neverrun_e213.py`'s `subtracted()` reads `W/out/card-e213a/` and
   `W/out/card-e213b/` (with the slash) and data folders whose name holds `-e213-`. A card lane named otherwise (for example `card-e213b2`) is
   read as a lane folder: its own RB_OUT (step 2's scorer self-tests write E213's points there) would read as hits at its step 6n, classed by
   the scanner's experiment map for `card-e213`: now that arm A's data is committed (`c69a12aa`), as aifoundry3 (another card for arm B:
   REPORTED, not counted; before that commit they would have read as no card named, COUNTED for card 1, so every arm B point would have read
   "ran after the freeze line (REPORTED, kept)"). Keeping arm B's RB_OUT and 6n folders under `W/out/card-e213b/` (the kit's go lines name
   `rb-e213b-2` for a second try) keeps that noise out. The scanner also reads lane folders whose names start `a1`, `a2` or `a3`.
2. **The quiet-desk flag and row 9**: `s11_session_e213_a2.sh` holds `session_e213` in its name, like the kit's row 9: the go lines keep the
   kit's rule (row 9 waits while the flag stands).
3. **(verify-a2e213's finding 3, for the readiness lane; added by fix-a2e213)** Any "17, nothing sent" at the one read ends arm B's day: that
   covers a missing lock file for either card (fwgate never makes one) and no `/usr/local/bin/et-who` (fwgate's fixed path; row 4's wait loop
   runs `et-who` from the box shell's PATH, as k6's holder rule does). With `--wait`, k6's look no longer prints the lock files. The readiness
   lane's read-only look adds `ls -l /run/lock/etsoc-shire0.lock /run/lock/etsoc-shire1.lock`, `command -v et-who`, `test -x
   /usr/local/bin/et-who` and `test -x /opt/et/bin/dev_mngt_service` (`tools/lab/README.md` documents both: the lock files made at every boot,
   et-who in /usr/local/bin on all three boxes).

## 5. Changes before the land (fix-a2e213, Wed 18 Nov 2026)

The amendment's A2-8 lists them: row 4's note on the never-run scan (finding 1); row 4's item 7e, the helper's `evidence` and row 12's addition
of the capture (finding 2); `rb/rb_e213_a2.sh`'s pin of the helper at its new sha256; the desk test's 8 new checks; the logs re-run. Every
other line of A2's kit is as `verify-a2e213` verified it. No box call is added; the read's box call is unchanged.

SPDX-License-Identifier: Apache-2.0
