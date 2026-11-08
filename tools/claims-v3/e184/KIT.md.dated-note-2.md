# E184's kit, dated note 2 (Sat 7 Nov 2026, week 45, written from 18:24 PST by the clock): the verifier's faults in A2 and kit note 1 fixed in new files before any datum - the governing reading at the top level of the scores, A2-4's filter on E184-C, a missing config read replaced by runbook step 7's read (step 7 v2, run again after the session; step 11 v2), and the kit's records

*Written on the Intel in Q154 (lane `fix-e184n`), desk only: no card claimed, no device command sent, no lab box, mini or network reached
(every ssh and rsync of the tests below is a stand-in that serves a local directory), nothing posted or deployed. New files only: the kit
(`65f844be`), kit note 1 (`eab0c70e`) and every file their hash lists name stay as committed (registration 11 of 11, kit 44 of 44, A2 6 of
6, kit note 1 45 of 45 OK). It follows dated amendment A3 ([`E184.md.dated-note-A3.md`](E184.md.dated-note-A3.md), committed alone just
before it: `3b48cf7b`, 18:10:08 PST), whose A3-3 and A3-4 its code implements. **No box file changes:** the harness's 59 files
(`harness-e184-v2.json`) are kit note 1's, byte for byte. No E184 datum exists: `git log --all` shows no `docs/reports/data/*e184*`.*

## Results first

The verifier of A2 and kit note 1 held both "with fixes": 5 minor faults and nits (a)-(i), no major or critical fault.

| the verifier's fault | the fix | file | its test |
|---|---|---|---|
| 1: the md showed the registered R and interval beside a verdict another reading governed | E184-L and E184-P carry `governing_rule`, `governing_R`, `governing_ci95` at the top level; the registered statistic is labelled (`registered_R`, `registered_ci95`, `registered_verdict`); no bare `R` or `ci95`; the md prints the governing interval on the verdict's line | `score_e184_v3.py` | self-test v3 **F1** (V7: P's null-corrected METER EXCLUDED read on the governing interval, 1.01168 [0.911224, 1.11214], beside the registered 1.21894 [1.17545, 1.26244]) and **F1b** (+40 mW at E178's 0.29: METER NOT EXCLUDED on the governing interval, where the registered one alone, [0.523, 0.603], would read EXCLUDED) |
| 2: E184-C kept levels with fewer than 4 quads | A3-4: A2-4's filter on E184-C's fit, its reference reading and the reported registered statistic | `score_e184_v3.py` | **F2** (15 levels cut to 2 quads: NOT SCORED on 9, where v2 scored 24), **F2b** (3 levels cut to 3: scored on 21, the 3 named) |
| 3: a missing config read voided a whole arm | A3-3: a missing read (its attempt recorded, its file empty) replaced by step 7's read, as a departure; a moved read still fatal | `reduce_e184_v3.py`, `rb/s09_reads_e184_v2.sh`, `rb/s22_collect_e184_v2.sh`, `collect_e184_v2.sh` | **G0-G11** (12 gate cases), runbook desk test v2 **R1-R5** (step 7 v2 on a stand-in box) and **C2, C2n** (the real collector), interpreter check v3 |
| 4: the smoke's 16-shire check still censors E184-P's high side | A3-1: accepted, the band kept, no box file | (A3) | `power-e184-a3.json` > K |
| 5: "the powers stand" overstated | A3-2: the registered statistic's powers stand; the governing reading's are A2-2's (0.953, 0.952) | (A3) | `power-e184-a3.json` > R |
| nits (a)-(i) | (a) section 3's table looks first; (c) the runbook audit v2 adds `look_e172.sh`; (e) the collector keeps each arm's T0; (b), (d), (f) stated; (g)-(i) in A3-5 | section 4 | `logs/dmcmd-audit-rb-v2.txt` |

**Every other reading is v2's.** v2's fifteen synthetic cases (V1-V13 of arm S, B1-B2 of arm B, with v2's seeds and options) read the same
verdicts, meters and session gates under v3 as under v2 (self-test v3, Q). **Device commands:** the runbook v2 **GO, 23 send sites**, the same 23
as kit note 1's runbook audit (every one a READ but v1's reviewed exception: E184's guard forwards a reset the runbook never passes), with
`look_e172.sh` now scanned (nit c: no send site); kit note 2's desk files **GO, 0 send sites** ([`logs/dmcmd-audit-rb-v2.txt`](logs/dmcmd-audit-rb-v2.txt), [`logs/dmcmd-audit-desk-v3.txt`](logs/dmcmd-audit-desk-v3.txt)). Step 7 v2
sends the same config read as v1, through the same guard; it adds one file write on the box (its read, as JSON) and nothing else.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sat 7 Nov 2026 at 18:08 PST (rows L06, L08, L11, H27, P03; A3's block). The ids are
   opaque pointers into a private inventory.
2. **Used** (each unchanged, called, imported or sourced by path; their sha256 in [`SHA256SUMS-e184-kit-note2`](SHA256SUMS-e184-kit-note2) or
   in kit note 1's list):
   - **Kit note 1's files** (`eab0c70e`): `reduce_e184_v2.py`'s reduction (called unchanged by v3), `score_e184_v2.py`'s readings (called
     unchanged by v3), `collect_e184.sh`, `rb/s03_desk_e184.sh`, `rb/s09_reads_e184.sh`, `rb/s22_collect_e184.sh`, `rb/list_steps_e184.sh`,
     `rb/selftest_rb_e184.sh` and `audit_rb_e184.sh`, each v-next file being its predecessor with the stated changes (counted, exact
     replacements; each file's header lists them). *Check:* the Q cases (v2's verdicts re-read under v3) and v1's runbook cases re-run in the
     runbook's desk test v2.
   - **k6's runbook drivers** (`tools/claims-v3/q141k-runbook/k6/rb_common.sh`, sourced unchanged through `rb/rb_e184.sh`; its prelude's
     `ours_live` and `hold_read`). *Check:* E171 ran them on 5 Nov, and E178, E180 and E181 on 6 Nov.
   - **A3** (`3b48cf7b`) for the rules A3-3 and A3-4.
3. **Not used:** a v3 session that retries its config reads (the verifier's other option for fault 3: a box-file change, with the harness and
   every test re-made, for a case step 7's read now covers at the desk); a wider smoke band (A3-1).
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this note.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

## 1. The scorer v3 (faults 1 and 2)

`score_e184_v3.py` runs v2's scorer (`score_e184_v2.score_s` and `score_b`, imported unchanged: the session gate, v1's readers on the kept
passes, A2-1 to A2-4) and changes two things.

- **The governing reading at the top level (fault 1).** For E184-L and E184-P, `verdict` is A2-2's governing verdict (as in v2), and beside
  it now stand `governing_rule` ("the registered R", or "the null-corrected R (the own null reads OFFSET)"), `governing_R` and
  `governing_ci95`; E184-P's `meter` is read on `governing_ci95`'s lower end (as v2 read it; `meter_read_on` says so). The registered
  statistic is kept, labelled: `registered_R`, `registered_ci95`, `registered_verdict`; the null-corrected one as `null_corrected_R` and
  `null_corrected_ci95`. The bare `R` and `ci95` v1 and v2 wrote (always the registered statistic's) are not written. In the md the
  verdict's line carries the governing interval, and a line of its own, "registered R (reported, A2-2)", carries the registered one with
  its own verdict. On V7's session (+25 mW in every B block): E184-P reads **LINEAR, METER EXCLUDED, governing R 1.01168 [0.911224, 1.11214]**
  by the null-corrected R; the registered R, 1.21894 [1.17545, 1.26244], is printed beside it as reading HIGH.
- **A2-4's filter on E184-C (fault 2, A3-4).** A scan level besides the reference with fewer than 4 kept quads is left out of A2-1's fit, of
  the reference reading's median and of the reported registered statistic (whose fit keeps the reference level only with 4 or more); only the
  levels kept count toward the 10; `levels_left_out` names the others with their counts. With no level left out, every number is v2's.

## 2. The reducer v3 and the collector v2 (fault 3; A3-3)

- **`reduce_e184_v3.py`** calls v2's reduction unchanged (the pass gate, A2-5) and replaces the session gate's config part by A3-3's
  rule: a session read is **missing** when its attempt was recorded (`config-<arm>-t<T0>-<edge>.json.time`, the session's `date -Iseconds`
  after every attempt) and its file is absent, empty or holds no JSON object; a missing start read is replaced by the newest step-7 read
  (`config-<arm>-step7-<epoch>.json` in the copied logs) in the 90 minutes before T0, a missing end read by the oldest in the 30 minutes
  after its attempt; the replacement is checked as the session's own read would be, and named in `session.departures` (`config_from`
  says where each edge's read came from). A moved read, a dry read in a real session's file, a missing read with no attempt recorded or no
  step-7 read in its window, and a replacement not as registered all leave the arm NOT SCORED. Every step-7 read found is listed, and one
  taken after a present end read is reported (`reported_step7_after_end`), never gated. Times are the box's (the epoch in each step-7
  file's name; T0; the `.time` files), and the files print them in UTC.
- **`collect_e184_v2.sh`** is v1's collector with `reduce_e184_v3.py` and `score_e184_v3.py` (`reduced-e184{s,b}-v3.json`,
  `scored-e184-v3.{json,md}`, the success line "scored-e184-v3.md written"), and the verifier's nit (e) fixed: an arm collected with its T0
  keeps it in `<out>/t0-<arm>.txt`, and is reduced with it again when the other arm's step 11 runs.

## 3. The runbook as it now runs (it governs E184's steps; nit a)

Kit note 1 section 3's table, with these steps in v2 and the look before the post (nit a, as the dry listing and the card lane's brief for
E182 and E184 order it). Every other step, file and rule is kit note 1's.

| KIT.md box step | file |
|---|---|
| 1, his go and the window | `rb/s02_window_e184.sh <day> <last start> <last end>` (one `RB_OUT` per arm) |
| 2, the desk check | **`rb/s03_desk_e184_v2.sh`**: v1's checks with **six** hash lists and their counts pinned: 11, 44, A2's 6, kit note 1's 45, A3's 3 and this note's 20 |
| 4, look first | `q141k-runbook/k6/s05_look_k6.sh aifoundry3` or `aifoundry1` (k6's, unchanged; on aifoundry1 E172's look) |
| 3, then the day's one post | the card lane's, under the post's lock, only after the look reads the card free |
| 5, the sync | `rb/s07_sync_e184.sh S` or `B` |
| 6, the build and the box checks | `rb/s08_build_e184.sh S|B start`, then `... wait` (repeat while 17) |
| 7, the reads | **`rb/s09_reads_e184_v2.sh S|B`**: v1's reads, and the config read kept on the box as step 7's read (A3-3) |
| 8, the V3_DRY pass on the box | `rb/s10_dry_e184.sh S|B start`, then `... wait` |
| 9, the session | `rb/s11_session_e184.sh S|B` |
| 10, the wait | `rb/s20_wait_e184.sh S|B` (repeat while 17) |
| **10b, step 7 again** | **`rb/s09_reads_e184_v2.sh S|B after`**, right after step 10 exits 0 and before the release, every time (a few seconds, READ only). It refuses (10) beside a session of ours or unless this T0's log on the box ends "session end (T0 <T0>)": then run step 10 again first. A 16 (the config is not as registered) or a 17 (et-who not clean) comes after the read is kept on the box: it is recorded in the runbook's log and does not stop the release, and the reducer refuses a read not as registered as a replacement. |
| 11, release, then collect | the post's release; then **`rb/s22_collect_e184_v2.sh S|B`** (the copy-back of kit note 1, which brings step 7's reads with the session's own files, then `collect_e184_v2.sh`); then the data directory `docs/reports/data/<day>-e184-sensor-validation/` and a data verifier |

**What the card lane and the data verifier read.** `scored-e184-v3.md` and `.json` govern; `scored-e184-v2.*` is not written by step 11 v2.
E184-L's and E184-P's verdicts are quoted with `governing_R` and `governing_ci95`, and the registered R as reported. A session gate that
holds with a departure (A3-3) is named in the data README with the step-7 read it used. If step 11 v1 was run by mistake, step 11 v2 can be
run after it on the same copy.

## 4. The kit's records (the verifier's nits)

- (a) Kit note 1 section 3's table listed the post (3) before the look (4). The table above looks first; nothing else changes.
- (b) Kit note 1's Builds-on called k6's `s09_a3_reads_k6.sh` "called unchanged". The runbook runs E184's own port, `rb/s09_reads_e184.sh`
  (now v2), made from k6's file; k6's file is not called. Its `s05_look_k6.sh` is called unchanged.
- (c) `audit_rb_e184.sh` left out `tools/claims-v3/e172/box/look_e172.sh`, which k6's look sends to aifoundry1. `audit_rb_e184_v2.sh` adds
  it: it runs uptime, et-who, who, df, sha256sum and pgrep, and the audit finds no device-command send in it (GO, above).
- (d) `rb/s07_sync_e184.sh` has no `ours_live` refusal: it relies on the look (step 4) having run first, whose holder rule refuses beside a
  session of ours. Kept: an rsync of about a hundred files is light, and the order rule (the look first; one session of ours per box, the
  Q153 critic's shared-box order, which E182's kit note 2 carries in its card lane's brief) covers it.
- (e) Fixed in `collect_e184_v2.sh` (section 2).
- (f) **A2-5 governs the reducer only.** The box's calibration (`run_e184_v2.calibrate`, v1's reader) reads pass 18413's quads and pass
  18412's A blocks without it, so an uncaught dip (about 5% of quads at A2-5's rate) can move one base point by up to about 0.17 W and the
  calibration's M_op or M_s by one shire, about 0.34 W of zeros base (E180's zeros, 10.77 W over idle at 32 shires,
  `inputs-e184.json` > `e180_anchor`). Stated, not fixed: the calibration is a box file. Its `cal.json` is copied back with the pass, and part
  P's zeros base is reported against its 30.132 W target (`E184-P.reported_base_w`, `reported_target_w`), so a shifted operating point is
  seen in the data.
- (g)-(i) A3-5: E184-C's critical values (the registered statistic's 2.874 on 20,000 draws, reported only; A2-1's 3.004 stands, null rate
  0.047); the base model's 7 refreshes a block against E180's 8.18; A2's and kit note 1's header times.
- This lane's own header times: A3 says "written from 18:07 PST by the clock" (committed 18:10:08); this note "written from 18:24 PST by
  the clock" (its commit time is git's).

## 5. The checks (each run by this lane; the logs are this commit's)

| check | result | log |
|---|---|---|
| the scorer's self-test v3 | **SELFTEST-SCORE-E184-V3 32 of 32** (Q V1-V13, B1-B2; F1, F1b, F2, F2b; G0-G11; ID) | `logs/selftest-score-e184-v3.txt` |
| the runbook's desk test v2 | **SELFTEST-RB-E184-V2 PASS, 34 of 34** (v1's 27 with the v2 steps, R1-R5, C2, C2n) | `logs/selftest-rb-e184-v2.txt` |
| the runbook's dry listing v2 | 24 steps (v1's 22 and the two `after` reads), 0 exit non-zero, no ssh or rsync | `logs/dry-listing-e184-v2.txt` |
| the interpreter check v3 | **INTERP-E184-V3 SAME** (3.9 and 3.13, with A3-3's replacement and A2-5's rule exercised) | `logs/interp-check-e184-v3.txt` |
| dmcmd_audit | runbook v2 GO, 23 sites; desk v3 GO, 0 sites | `logs/dmcmd-audit-{rb-v2,desk-v3}.txt` |
| the hash lists, the harness, no E184 data | registration 11 of 11, kit 44 of 44, A2 6 of 6, kit note 1 45 of 45, A3 3 of 3 OK; the box list CHECK PASS, 59 files, kit note 1's; `power-e184-a3.json` re-made IDENTICAL; no committed E184 file changed; no commit names `docs/reports/data/*e184*`; this note's own list, 20 of 20 OK, checked after it was made and before the commit | `logs/reruns-note2.txt` |

## 6. Kit note 2's files (their sha256 in [`SHA256SUMS-e184-kit-note2`](SHA256SUMS-e184-kit-note2), 20)

| file | what | from |
|---|---|---|
| `KIT.md.dated-note-2.md` | this note | |
| `score_e184_v3.py` | the governing reading at the top level; A2-4's filter on E184-C | `score_e184_v2.py`, imported |
| `reduce_e184_v3.py` | A3-3's session gate | `reduce_e184_v2.py`, imported |
| `collect_e184_v2.sh` | the desk collector with v3's readers; each arm's T0 kept | `collect_e184.sh` |
| `selftest_score_e184_v3.py` | the scorer's and the gate's self-test | `selftest_score_e184_v2.py` |
| `interp_check_e184_v3.sh` | 3.9 against 3.13 | `interp_check_e184_v2.sh` |
| `audit_rb_e184_v2.sh`, `audit_desk_e184_v3.sh` | the device-command audits | v1's, v2's |
| `rb/s03_desk_e184_v2.sh` | step 2 v2: six lists pinned | `rb/s03_desk_e184.sh` |
| `rb/s09_reads_e184_v2.sh` | step 7 v2: the read kept on the box; `after` | `rb/s09_reads_e184.sh` |
| `rb/s22_collect_e184_v2.sh` | step 11 v2: `collect_e184_v2.sh` | `rb/s22_collect_e184.sh` |
| `rb/list_steps_e184_v2.sh`, `rb/selftest_rb_e184_v2.sh` | the dry listing and the runbook's desk test | v1's |
| `logs/` (7 files) | the checks above | |

## 7. Open items (for the verifier, the readiness critic and the records)

1. **No verifier has read A3 or this note.** Card time only on his go and fresh approvals.
2. **The box build is still new:** both arms' patched hosts compile first at step 6 (kit note 1's open item 2).
3. **Arm B's identity:** aifoundry1 must not have rebooted since E82's firmware read (31 Oct 2026, 13:45:24 PDT), or IDENTITY STOP and no
   firmware query (kit note 1).
4. **Stated limits:** A3-1's censoring of E184-P's high side above a gain of about 1.6; nit (f)'s one-shire calibration effect; the rail
   witness rarely separates the meter from the power (A2-3).

## Compute

All on the Intel, desk only, through the round's local slot (`slot.sh`), one job at a time at nice 10, one core: A3's figures (about 20 s
each under 3.9 and 3.13), the scorer's self-test v3 (about 4 minutes), the runbook's desk test v2, the dry listing, the audits and the
interpreter check (one job). No lab box, card, mini or network call.

SPDX-License-Identifier: Apache-2.0
