# E184 arm S's README, dated note 2 (Sun 8 Nov 2026; kit note 4's step 11 v4): the gate-stopped session's own files collected from aifoundry3, COPY-BACK EXACT against the box's own listing; its end config read, seen for the first time, reads TDP 0 W / 65 °C / 600 MHz as registered; the session gate does not hold, every arm S rule NOT SCORED: A3-1 stands, arm S not run

*Written on the Intel from about 05:13 PST on Sun 8 Nov 2026, after the collection below. One copy from aifoundry3 and one read of our own
files there; no device command, no card session, no card claimed: **0 card-minutes**. [`README-arm-s.md`](README-arm-s.md),
[`SHA256SUMS-arm-s`](SHA256SUMS-arm-s) (lab `f8d94224`, 02:36:34 PST), [dated note 1](README-arm-s.md.dated-note-1.md) and its list
(`9a8b9d3e`, 03:43:07 PST), and every file of arm B (`8bf74b26`, 00:43:41 PST) stay as committed. **New files only**, under names that do not
collide with arm B's. **No number, rule, verdict or gate reading changes, and nothing is scored: E184 arm S was not run (A3-1).** It closes
README-arm-s.md's "Still on aifoundry3" list and dated note 1's section 3. For the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6, as the README.*

## Results first

| what | reading |
|---|---|
| collected | the session's **12 own files** (its T0 log and `.out`, both session config reads with `.time` and `.err`, the preflight, step 7's two reads, the dry pass's log) into [`raw/aifoundry3/logs/`](raw/aifoundry3/logs/), and the two pass directories its log names, `e184-smoke` and `e184-stoptest` (20 files, the same bytes as `f8d94224`'s copy) |
| from where | aifoundry3, our own tree's `build/e184/` (its 13 operand images left out, as step 11 v4 is written) and `build/claims-v3/aifoundry3/`; the box holds no `e184` pass directory |
| how | kit note 4 ([`KIT.md.dated-note-4.md`](../../../../tools/claims-v3/e184/KIT.md.dated-note-4.md), `8092c27a`, 03:37:08 PST): step 2 v4, then step 11 v4 `rb/s22_collect_e184_v4.sh S`, as committed, with the card day's arm-S runbook output directory (its window written 00:01:55 PST: day 2026-11-08, last start 05:30, last end 07:45) |
| when (the Intel's clock, PST) | step 2 v4 05:04:02-05:04:16 (rc 0); a probe 05:04:54; **step 11 v4 05:05:00-05:05:18, rc 0**: its probe 05:05:01, the session's files copied 05:05:01 (0.4 s), the pass directories 05:05:02 (0.4 s), the collector 05:05:02-05:05:17, the desk-path and login gates 05:05:18; the box's read listing 05:06:24 (the box's clock) |
| the copy | **COPY-BACK EXACT**: the box's own sha256 of every file the step copied ([`copyback-box-list-arm-s.txt`](copyback-box-list-arm-s.txt)) equals the files here, 12 of 12 and 20 of 20, the same names both ways, the same whole-second times and sizes; no other file was on the box's side and none was copied |
| the end config read | `{"tdp_w":0,"temp_threshold_c":65,"power_state":0,"power_state_name":"max_power","minion_mhz":600,"minion_mv":523}` at 02:22:24 PST: **TDP 0 W, 65 °C, 600 MHz, as registered** (not MOVED); byte for byte the start read and step 7's reads before and after |
| the collector (reduce v4 with A4, score v3, unchanged) | the session gate **does not hold**, two reasons: the session log has no "smoke gate passed" line, and the smoke, checked again at the desk, reads `SMOKE NO-GO: m16 n19 read 0.358 W, outside -0.15-0.30`; **E184-C, -J, -L, -N and -P NOT SCORED** |
| arm B | its section of the both-arm scored files equals its committed one; the collector re-made `reduced-e184b-v4.json` byte for byte; its 80 files untouched (80 of 80 OK) |

## 1. What was collected, from where, and when

The session is arm S's of Sun 8 Nov 2026 on aifoundry3 card 0, T0 1794133299 (02:21:39 PST), stopped by its smoke gate at 02:22:24 (A3-1;
README-arm-s.md). Step 11 v3 had stopped at its first copy at 02:26:36, so its own files had stayed on the box. Kit note 4's step 11 v4
copies the box's `build/e184/` first and checks this T0's log there. The log holds `smoke gate failed (stop test rc 0, smoke rc 0, gate 1): no
pass runs`, so the step copied `e184-smoke` and `e184-stoptest` and no `e184`. It then ran the collector, the desk-path gate (112 files read,
0 hits) and the login check (89 files in 17 directories, 0 left). It said: "a gate-stopped session: by A3-1 no rule of arm S has a reading".

**The box's times.** Each file's time on aifoundry3, as the box's listing reads it and as rsync kept it (PST):

| file | box time | what it holds |
|---|---|---|
| `config-S-step7-1794133226.json` | 02:20:26 | box step 7's config read, before the session |
| `session-S-dry-t1794133234.log` | 02:20:34 | the dry pass's start-gate log: `no new card session after 2026-11-08 01:20:00 PST: no device opened` (the dry job's refusal test, as registered) |
| `session-S-t1794133299.out` | 02:21:39 | the session's stdout: empty (0 bytes) |
| `dmcmd-preflight-S-t1794133299.txt` | 02:21:39 | the session's own device-command audit: GO, 32 send sites, 0 disallowed, no allow-list (its one conditional statistics-reset site excepted, as registered: arm S never forwards a `--reset-ms`) |
| `config-S-t1794133299-start.json`, `.time`, `.err` | 02:21:39 | the session's start read (`.time` 2026-11-08T02:21:39-08:00; `.err` the device layer's stderr, 3,181 bytes) |
| `config-S-t1794133299-end.json`, `.time`, `.err` | 02:22:24 | **the session's end read** (`.time` 2026-11-08T02:22:24-08:00; `.err` as at the start but for the thread id) |
| `session-S-t1794133299.log` | 02:22:24 | the session's log, 1,747 bytes: its start line, HARNESS OK 61, the preflight's GO, et-who's "No process holds an ET-SoC-1 device node or card lock.", both config reads, the stop-path test and the smoke, the gate's NO-GO, the gate-stop line and `session end (T0 1794133299)` |
| `config-S-step7-1794133494.json` | 02:24:54 | step 10b's read, after the session's end line |

Those lines were known before today only from the runbook's printed output (README-arm-s.md, box step 10). They are now in the data,
the same words.

**The git times** (PST, Sun 8 Nov 2026): arm B's data `8bf74b26` 00:43:41; arm S not run `f8d94224` 02:36:34; kit note 4 `8092c27a` 03:37:08;
dated notes 1 `9a8b9d3e` 03:43:07. The lab's HEAD at step 2 v4 was `d5eb87b5` (04:56:09) = origin/main. This note's own commit time is git's.

## 2. The session's end config read, seen for the first time

`config-S-t1794133299-end.json`: `{"tdp_w":0,"temp_threshold_c":65,"power_state":0,"power_state_name":"max_power","minion_mhz":600,
"minion_mv":523}`, read at 02:22:24 PST through E128's guard. **TDP 0 W, threshold 65 °C, 600 MHz: as registered** (E184.md; A3-3 with A4
reads it "complete", from the session's own read). It is not MOVED. All four config files of the session share one sha256 (`6933cf9f…`): the
start read (02:21:39), the end read, and step 7's reads at 02:20:26 and 02:24:54. **Nothing was set.**

## 3. COPY-BACK EXACT, and the checks the commit was made under

Step 11 v4 checks rsync's status and this T0's log, not the copy against its source. So right after it, one more call read aifoundry3: a
probe, then one bounded 60 s READ through the kit's own runner (`rb_run.py`, class read). It listed the sha256 of every file of our tree's
`build/e184/` without its operand images, those files' times and sizes, and the sha256 of every file of the two pass directories. It also
noted whether `e184` exists. It wrote, moved and deleted nothing, and sent no device command. Its output, unchanged, is
[`copyback-box-list-arm-s.txt`](copyback-box-list-arm-s.txt).

[`check_note2_e184.py`](check_note2_e184.py) re-makes these checks from the committed files alone. Its output is
[`check-note2-e184.txt`](check-note2-e184.txt): **CHECK-NOTE2-E184 PASS, 0 failed**.
1. **COPY-BACK EXACT.** `raw/aifoundry3/logs/` holds exactly the box's 12 files and `raw/aifoundry3/e184-smoke`, `e184-stoptest` the box's
   20, each with the box's sha256. No file is on one side only. There is no `e184` on the box or here, and no link or other non-regular
   entry. The session's files are there by name: the T0 log and `.out`; both config reads with `.time` and `.err`; the preflight; step 7's
   two reads; one dry log. Nothing else is there. At the desk, before the commit, the times and sizes matched too, 12 of 12 (git keeps no file
   times). The collector's copy matched the step's copy (32 files).
2. **The collector re-made** from the committed files. `reduce_e184_v4.py` on `raw/` for arm S (T0 from `t0-S.txt`) and for arm B (T0 from
   `t0-B.txt`), then `score_e184_v3.py`, all unchanged. The reductions equal `reduced-e184s-v4.json` and arm B's committed
   `reduced-e184b-v4.json`, byte for byte; the scored pair equals `scored-e184-v3-arms-bs.json` and `.md`.
3. **Arm B's section** of the both-arm files: `scored-e184-v3-arms-bs.json`'s `arm_B` equals arm B's committed `scored-e184-v3.json`'s,
   and so do its other top-level keys (`t_crit_a2`, `what`). The `.md`'s header and "Arm B" section equal arm B's committed
   `scored-e184-v3.md`'s.
4. **Arm S:** the gate and the two config reads as above; every rule NOT SCORED.
5. **The readers `f8d94224` committed,** re-run on the smoke, give their committed outputs byte for byte: `check_e184_v2.py smoke`
   (`smoke-gate-desk-arm-s.txt`) and `posthoc_arms_e184.py` (`posthoc-arms-e184.json`).
6. **The lists:** `SHA256SUMS-arm-b` 80 of 80, `SHA256SUMS-arm-s` 23 of 23, `SHA256SUMS-note1` 4 of 4.

**The four checks the commit was made under** (the kit verifier's fault on kit note 4, Sun 8 Nov 2026: the step writes arm S's files
beside arm B's in one output directory, and two of them keep arm B's committed names with other bytes):
1. `git status --porcelain` on this directory listed only new (`??`) entries before the commit: 21 files, none modified.
2. `SHA256SUMS-arm-b` read 80 of 80 and `SHA256SUMS-arm-s` 23 of 23.
3. The renamed file's `arm_B` equals arm B's committed `scored-e184-v3.json`'s `arm_B`.
4. `reduced-e184b-v4.json` as the collector re-made it is `cmp`-equal to arm B's committed one.

Each new path was given to the commit by name, never the directory. The two both-arm scored files carry new names,
`scored-e184-v3-arms-bs.json` and `.md`. Arm B's `scored-e184-v3.json` and `.md` stay as committed; their `arm_S` reads `null` and "NOT
SCORED (no reduced file)".

**Before step 11 v4,** the Intel's own build state was checked equal to the committed files (the verifier's limit on a merge into the local
tree). The 02:26 partial copy's `e184-smoke` and `e184-stoptest` equalled `f8d94224`'s `raw/aifoundry3/`, and its `logs/` was empty. The
output directory's arm B files (`reduced-e184b-v4.json`, `scored-e184-v3.json` and `.md`, `t0-B.txt`, `raw/aifoundry1-c1/`) equalled
`8bf74b26`'s. Step 2 v4 ran under the lab clone's commit lock, and each box call came after a clock check: the box step started by 07:15 PST
and ended long before the window's 07:45.

## 4. What the collector reads, and what stands

- **The session gate** (`reduced-e184s-v4.json` > `session`): `gate_ok` false, with two reasons. The log has no "smoke gate passed" line,
  and the smoke, checked again at the desk, reads NO-GO. Without these files, the verifier's desk check (dated note 1, section 3) had
  given four: no session log, the desk smoke's NO-GO, and no start and no end config read. With the session's own files in the data, the
  log's missing "smoke gate passed" line and the desk smoke's NO-GO remain. `log_session_end` true, `departures` none.
- **A3-1 stands: E184 arm S not run.** E184-N, E184-L, E184-P, E184-J and E184-C have no reading. They are never a verdict, and their
  registered forecasts stay untested (N NULL, L LINEAR, P LINEAR and METER EXCLUDED, J and C NONE SEEN; the governing LINEAR powers 0.953
  and 0.952).
- **The A2-5 readings stay post hoc.** The reducer applies A2-5's refresh rule (registered for the reducer). So the quads in
  `reduced-e184s-v4.json` read the smoke as dated note 1 does: the 16-shire n = 19 quad +0.1847 W, 1.18 of its step; the n = 121 quad
  +0.9629 W; the null -0.0051 W; every minion +8.5874 W. They are no rule's reading and decide nothing. The registered gate read the
  smoke with v1's reader: NO-GO.
- **The box:** nothing on aifoundry3 was written, moved or deleted by this collection. Step 11 v4 is one probe and two rsync pulls (no
  `--delete`, no `--remove-source-files`). This lane added two probes and the read listing. `e184-smoke/p18401` and `e184-stoptest/p18402`
  stay there; any later arm S session needs them moved aside first, by a dated note (README-arm-s.md; kit note 4 section 1).

## Files (new; their sha256 in [`SHA256SUMS-note2`](SHA256SUMS-note2), 20)

| file | what |
|---|---|
| `raw/aifoundry3/logs/` (12 files) | the session's own files, as the box wrote them (section 1's table) |
| `reduced-e184s-v4.json` | the collector's arm S reduction (`reduce_e184_v4.py` with A4): the session gate does not hold |
| `t0-S.txt` | the T0 the collector kept for arm S, 1794133299 |
| `scored-e184-v3-arms-bs.json`, `scored-e184-v3-arms-bs.md` | `score_e184_v3.py` on both arms, renamed: arm S NOT SCORED; arm B's section equal to arm B's committed pair |
| `copyback-box-list-arm-s.txt` | aifoundry3's read listing of what step 11 v4 copied |
| `check_note2_e184.py`, `check-note2-e184.txt` | section 3's checks, re-made from the committed files, and their output |
| `README-arm-s.md.dated-note-2.md` | this note |
| `SHA256SUMS-note2` | the sha256 of the 20 files above |

Re-make from the top of the repository (the same bytes under `/usr/bin/python3` 3.9, about 16 s on one core):

```
D=docs/reports/data/2026-11-08-e184-sensor-validation
/usr/bin/python3 -B $D/check_note2_e184.py $D | cmp - $D/check-note2-e184.txt
(cd $D && shasum -a 256 -c SHA256SUMS-note2)
```

## Privacy and the public-text scan (before the commit)

Step 11 v4's own login gate (`scrub_tree_e178.py --check`, the box login of this repository's owner as the owner) read the output: 0 left.
Before the commit, the same check ran again over this whole directory, and E164's `scrub_etwho_e164.py --check` ran in every directory of it
and of a scratch copy of the text inside its `.gz` files. The search for the others-present and another-user stop lines ran too. Then came
the runbook's desk-path gate (`nopath_q142s.py`), and the public-text scan of every new file and of the commit message. That scan is
`tools/timeline/sanitize_extracts.py`'s fixed list plus the private-network, Mac-home, scratch and e-mail patterns, and a wider class list.
The session log's paths name the owner's own box account, as every arm's run logs here do; no other account's login appears.

## Labels

- **Registered, blind:** the smoke gate's bands and its NO-GO, with A3-1's reporting words; every rule and forecast of arm S, untested; the
  registered config (TDP 0 W, 65 °C, 600 MHz) that the end read is checked against.
- **Measured, reported:** the session's own files: the config reads, the preflight, the log's lines and the files' times.
- **Post hoc** (deciding nothing): the A2-5 readings in `reduced-e184s-v4.json`, as dated note 1.
- **Desk checks of code, not measurements:** COPY-BACK EXACT, the re-made collector, arm B's equality and the readers' re-runs.

## What remains

A data verifier of this commit; the records round (02-05, the kinds page, one Horace Hub entry). Arm S is **not** re-run today (A3-1). A re-run
on another day needs dated notes first and then the owner's go: A2-5 in the box's smoke gate or the dip risk accepted at 0.35-0.8%; that
day's `p18401` and `p18402` moved aside on the box; and a window that fits 8,100 s.

SPDX-License-Identifier: Apache-2.0
