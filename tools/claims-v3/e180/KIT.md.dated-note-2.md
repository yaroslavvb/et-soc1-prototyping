# E180's kit, dated note 2: the kit verifier's faults fixed before any E180 datum - A1-7's disassembly walk read at the desk on the box's own listing with A1-7's words binding, the build record and that listing collected, an unreadable pass set aside without losing the others, A1-5's band test and the per-kind marks named, and the runbook's two v3 steps (Q146(g); new files only; no box file changes)

*Fri 6 Nov 2026 (week 45), written about 05:40-06:45 PST on the Intel, desk only (Q146(g), lane `kitfix-e180`): no card was claimed, no
device command was sent, no lab box was reached, nothing was posted. It sits beside [KIT.md](KIT.md) (the kit, `c92f627b`) and
[KIT.md.dated-note-1.md](KIT.md.dated-note-1.md) (kit v2, `90a1312f`, 03:54:42 PST), which stay as committed, as does every file of the
four earlier hash lists (71, 55, 41 and 90 OK). It answers the adversarial verifier of the registration's dated note A1 and of kit v2
(`kitv-e180`, about 04:55-05:30 PST today: holds with fixes, 1 major, 4 minor, 5 nits), fault by fault. It is committed before any E180
datum: `git log --all` shows no `docs/reports/data/*e180*`.*

*No box file changes. The box's sync, harness (`harness-e180-v2.json`, 61 files), build, dry pass and session are kit note 1's, exactly as
the verifier and the readiness critic read them. Every change is a desk file the Intel runs: the walk v2, the build record's reader, the
reduction v3, the scorer v3, the collector v3, and runbook steps 2 and 11, v3. No registered rule, threshold, plan, order or forecast
changes. Where kit note 1's code departed from A1's words (A1-7, A1-5), this note says which reading binds.*

## In short

- **Fault 1 (major) is fixed at the desk.** The compiler lays the generated cases out in reverse mode order. In the committed listing
  all 43 consecutive pairs of the 44 vector modes found sit at decreasing addresses, and every pair of consecutive ids (40 of 40) sits
  exactly 104 instructions apart. So on the box kernel 262's zeroing block sits about 110 instructions before 261's loop, and v1's walk,
  which wants exactly one block in the 400 instructions before the loop, could never read 261: A1-7 was inert. [`check_elf_e180_v2.py`](check_elf_e180_v2.py) takes the case's **own** block: the nearest one before the
  loop's head with no unconditional jump and no backward branch between them. On listings built from the committed real listing it reads
  261 and 262 PASS in both orders, where v1 reads one of them UNREAD (**35 of 35**). It runs at step 22 v3, on the box's own listing,
  which step 22 now copies back. The box's v1 line from step 6 is kept beside and never read for a verdict.
- **Fault 2: A1-7's words bind.** The walk reads writes only (a store or a read of f8-f15 is not a write). A zeroing block inside the loop
  reads FAIL (v1 read it UNREAD, which failed open). E61's "any f-register instruction in the loop" becomes a remark.
- **Fault 3:** step 22 v3 copies `build/e180-kernel-dis.txt` and `build/enercat-e180/BUILD-E180.json` back. The data's `logs/` then holds
  the listing (byte for byte, with its sha256), the kernel's and the host's sha256, and the desk walk's lines.
- **Fault 4:** [`reduce_e180_v3.py`](reduce_e180_v3.py) sets an unreadable pass aside with its reason and reduces the rest. For every
  input v2 reduces, v3's output is v2's plus one record. The box side stays fail-closed (recorded).
- **Faults 5 and 6:** A1-5's "inside" is read as "meets", the scorer's own test and the more cautious reading. Every accumulating kind's
  reported reading carries its walk mark.
- **Nits 7-10** are recorded (section 5), with one new runbook rule: no relaunch without a dated departure (section 6).
- **The checks:**
  - the walk's test **35 of 35**;
  - the reduction, scorer and collection test **14 of 14**;
  - the runbook's v3 desk test **18 of 18**, and its dry listing 0 failing steps;
  - every earlier test re-run identical to its committed log, the dry pass DRY-INTEL-V2 (24 of 24) among them;
  - `dmcmd_audit` GO for the new desk files (0 send sites), and for the runbook as it now runs (11 sites, every one READ, all E128's
    guard's).
- **Card-minutes, the plan, the stops and every box file are unchanged** (FULL about 43, cap 50).

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md and MAP.md section 3, read Fri 6 Nov 2026 about 05:50-06:00 PST. Public rows read: L06,
   L21, H24, H27, H28; MAP rows 5 and 41. The row ids are opaque pointers into a private file.
2. **Used** (each unchanged, imported, called or read by path; sha256 in [`SHA256SUMS-e180-kit-note2`](SHA256SUMS-e180-kit-note2)):
   - **E180's kit v2** (`90a1312f`), file by file where v3 replaces it (`collect_e180_v2.sh`, `rb/s22_collect_e180_v2.sh`,
     `rb/s03_desk_e180_v2.sh`, `rb/list_steps_e180_v2.sh`, `rb/selftest_rb_e180_v2.sh`'s form), and its walk
     [`check_elf_e180.py`](check_elf_e180.py), imported unchanged by the walk v2: its parse, register names and body search, and E61's
     loop walk for the control, mode 160.
   - **The registration's dated note A1** (`879197e3`): rule A1-7 (section 7) and rule A1-5 (section 5), whose words this note reads.
   - **The committed real listing** (`docs/reports/data/2026-10-21-dtf/proof/enercat-df-aifoundry2.dis.txt`, `7eb1ec79`, E61's V3-DTF
     proof; L21): the tests' input, with mode 160's whole case as the compiler laid it out and the generated cases' reverse mode order.
     *Check against the same reading on the same listing:* the walk v2 finds mode 160's loop once (64 ops, 72 instructions), as v1 and
     E61's check did, and reads 261 and 262 absent (UNREAD), as v1 does.
   - **The kit verifier's adversarial forms** (its scratch `adv_elf.py` and `layout_order.py`, not committed): the two-mode listing in
     both orders, the zeroing block inside the loop, a store, a reload and a read between or in the loop, the block twice, and the layout
     count. The new self-test re-makes them from the committed listing alone.
   - **The catalogue's reduction** (`workloads/enercat/analyze_catalogue.py`, `bursts_of`; L06): the fields it reads, which reduce v3's
     scan checks; **the sampler's sample form** (`tools/ettelem/ettelem.cpp` lines 165-200; H28): a failed request leaves its field out of
     the line. **The reductions v1 and v2** (`reduce_e180.py`, `reduce_e180_v2.py`) and **the scorers v1 and v2** (`score_e180.py`,
     `score_e180_v2.py`), imported unchanged; v1's synthetic sessions (`selftest_score_e180.py`).
   - **The k6 runbook's v3 drivers** (`q141k-runbook/k6/rb_common.sh`, `9a2630ff`) through `rb/rb_e180.sh`, unchanged; E178's tree-wide
     login scrub (`tools/claims-v3/e178/scrub_tree_e178.py`, `763307e7`) and the desk-path gate (`q141k-runbook/v3.1/nopath_q142s.py`),
     unchanged (H24's card day is where the E174 class was found).
   - *Check against an earlier measurement of the same quantity:* none applies. Nothing here measures or forecasts a quantity.
3. **Not used:**
   - A walk v2 run on the box (an s08 v3): it would change the harness and the sync (a harness v3, a sync v3, a new readiness read: the
     E174 class) for a reading that needs only the listing, which is a file.
   - E61's own check (`tools/claims-v3/dtf/check_elf.py`, L21): checked; its loop walk reaches this note only through v1, for the control.
   - The build's cmake log (`build/enercat-e180-cmake.log`): not collected. It can carry the box tree's absolute paths, and nothing reads
     it.
   - Box-file fixes for nits 7-9 (D1's login source, a quieter holder check between runs, the reader's pin): owed to a later kit
     (section 5).
4. **Tiers:** every file of this note is public tier and cites public pieces only. No NDA-tier check enters it. The logins, uids, owners,
   groups and pids in the tests are made up.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

## 1. A1-7's walk, v2, read at the desk on the box's own listing (faults 1, major, and 2)

**The fault.** `check_elf_e180.py` line 110 keeps the zeroing blocks (`fxor.pi f8..f15, f0, f0`) that lie in the 400 instructions before
the loop and below its head, and lines 111-112 read UNREAD unless exactly one is found. Modes 261 and 262 carry the same block. In the
committed listing the generated cases sit in reverse mode order, consecutive ids exactly 104 instructions apart, so on the box 262's case
will sit just before 261's, if the box's build lays them out as the committed one does. Then step 6 v2 prints 261 UNREAD ("the zeroing block found 2 time(s)") and 262 PASS, E180-A is always scored
"walk not verified", and A1-7's FAIL can never fire. The kit's test built each mode in a listing of its own, so it never met the case.

**The fix, new files, no box file changed:**
- [`check_elf_e180_v2.py`](check_elf_e180_v2.py): the case's own zeroing block is the nearest complete block before the loop's head,
  with no unconditional jump (`j`, `jr`, `ret`, `tail`, a `jal` or `jalr` without a link) and no backward branch between them, looked
  for at most 400 instructions back. Another case's block lies behind that case's own loop and exit `j`, so it is never taken.
- [`rb/s22_collect_e180_v3.sh`](rb/s22_collect_e180_v3.sh) copies the box's listing back (section 2), and
  [`collect_e180_v3.sh`](collect_e180_v3.sh) runs the walk v2 on it into `logs/elfcheck-e180-v2.txt`, the reading A1-7 scores.
  The box's own line, `logs/elfcheck-e180.txt` (v1's walk at step 6 v2), comes back with the logs as before. The scorer keeps it beside
  and never reads it for a verdict.

**The readings: A1-7's words bind** (`E180.md.dated-note-A1.md` section 7). They replace kit note 1 section 5's definitions:
- **FAIL:** the body is found once and, on the sums' path from the end of the case's own zeroing block to the loop's backward branch,
  there is a write to f8-f15 by an instruction other than the 64 body ops, or a call. Or the zeroing block lies inside the loop. A1-7's
  "a write to f8-f15 other than its own block's, a call" is read over that whole path, as kit note 1's walk read it for writes. (The
  verifier found its reload case, a write between the block and the loop, correctly FAIL.) A call is now read on the path too: it can
  overwrite f10-f15, which the calling convention does not save. A write is an f-register destination: a store's register is read, not
  written, and so is every source operand.
- **UNREAD:** first A1-7's own two, no listing ("no objdump": the file absent or holding no instruction) or the body not found once. Then
  two cases where the listing does not show what A1-7's words presuppose, so no FAIL can be read:
  - the loop's backward branch not within 30 instructions of the body (E61's reading);
  - no zeroing block of the case's own before a loop that reads clean. That is the walker's limit, not the kernel's: an asm volatile
    block is never deleted.

  Each scores as A1-7's UNREAD does: as registered, labelled "walk not verified". Neither can hide a FAIL that the listing shows. Every
  reason inside the loop is read first, and a zeroing block inside the loop reads FAIL.
- **PASS:** otherwise.
- **Remarks, never reasons:** other f-register instructions in the loop (E61's rule, which v1 read as FAIL), stores of f8-f15 on the path,
  and earlier zeroing blocks in the same case (the nearest is the sums' start).

**The test** ([`selftest_elf_e180_v2.py`](selftest_elf_e180_v2.py), [`logs/selftest-elf-e180-v2.txt`](logs/selftest-elf-e180-v2.txt):
**35 of 35**). The input is the committed real listing, followed by generated cases made from mode 160's whole real case (104
instructions: the saves of fs0 and fs1, `mov.m.x`, load_vsrc, `cycles()`, the 64-op loop, the restores and the exit `j`), each with its
body rewritten to 261's or 262's form and the zeroing block where their source puts it. v1's reading on the same listing is asserted beside
each case:

| case | walk v2 (A1-7) | v1, kept beside |
|---|---|---|
| F0 the real listing alone | 261, 262 UNREAD (absent); control 160 PASS | the same |
| **F1 262 then 261, adjacent (the box's order)** | **261 PASS, 262 PASS** | **261 UNREAD**, 262 PASS (the fault) |
| F2 261 then 262 | both PASS | 262 UNREAD |
| F3 the two more than 400 instructions apart | both PASS | both PASS |
| **F4 261's zeroing block inside the loop** | **FAIL** | UNREAD (fail-open) |
| F5 a store `fsw fs0,44(sp)` between the block and the loop | PASS, with a remark | FAIL |
| F6 a reload `flw fs0,44(sp)` there (a write) | FAIL | FAIL |
| F7 a read `fmv.x.w a1,fs1` in the loop | PASS, with E61's remark | FAIL |
| F8 the zeroing block twice in the case | PASS (the nearest) | UNREAD |
| F9, F10 a write to f9 in the loop; to f10 between | FAIL | FAIL |
| F11, F12 a call in the loop; between the block and the loop | FAIL | FAIL; PASS |
| F13 262 then 261, 261's own block missing | 261 UNREAD (262's block not taken), 262 PASS | 261 FAIL (262's loop read as writes) |
| F14 the body twice; F15 the loop's branch missing | UNREAD | UNREAD |
| F16 a trailing rounding mode (`,dyn`) | PASS | PASS |
| F17 no listing; F18 an empty one | 261, 262 UNREAD, exit 0 | (not run) |

On F1, v2's line for 261 reads "the case's own zeroing block 56 bytes before the body, outside the loop, 8 instructions between".

**What step 6 v2 prints on the box from now on.** Its line is v1's. On the box's layout it is expected to read one of 261 and 262 UNREAD.
That is the fault this note fixes, not a reason to stop: the build step never gated on the walk, and this line is not A1-7's reading. A
FAIL there is not A1-7's reading either (v1 reads stores and reads as writes). A1-7 is read once, at step 22 v3.

## 2. The build record and the listing, collected (fault 3)

- **Step 22 v3's third copy** brings `build/enercat-e180/BUILD-E180.json` and `build/e180-kernel-dis.txt` back into
  `build/e180-raw/build-record/`, after v2's two copies. Earlier copies there are removed first, so a listing the box did not write this
  time is never read from an older copy. The listing is not asked for when the box's walk line, copied back with the logs, says step 6
  found no objdump or no kernel (then step 6 never wrote it), or when that line is absent (step 6's walk never ran). A copy that exits
  non-zero stops the step (14): call it again.
- [`build_record_e180.py`](build_record_e180.py) writes `logs/build-e180.json` and `logs/e180-kernel-dis.txt`:
  - BUILD-E180.json's binaries' sha256 (the kernel's among them), the appended modes' sha256 and the build time, unchanged;
  - the listing's own record: its sha256, bytes, lines and instruction count, or "absent";
  - the listing itself, byte for byte. `check_elf_e180_v2.py` reads it there, and anyone can re-read A1-7 from the data.
- **A departure from the verifier's literal fix:** BUILD-E180.json is not copied into `logs/` as it stands. Its `toolchain_listing` is
  `ls -l /opt/et/bin | head -3; cat /opt/et/VERSION`, cut to its last 400 characters. Owner and group columns (and a symlink's target)
  can name a lab account, in a form the tree scrub does not read. So every `ls -l` line's owner, group and target is withheld, any line
  that is not an `ls -l` entry, a total or a bare version string is withheld whole (the cut can leave a partial first line), and the
  sha256 of the listing as recorded is kept. The raw copy stays in `build/e180-raw/`, which is never committed.
- **Which kernel ran.** The kernel's sha256 is BUILD-E180.json's. `check_e180_v2.py harness --binaries` compares the built binaries against
  it before every session, and step 6 v2 made the listing from that ELF in the same job.
- The cmake log is not collected (Builds on, Not used).

## 3. The reduction, v3: one unreadable pass is set aside, never the whole session (fault 4)

**The fault.** `reduce_e180.py` and `reduce_e180_v2.py` parse every pass directory before their set-aside rule. So one unreadable file
loses every pass's score: a gzip that ends early, a partial line, or a sample the sampler printed without a field because that request
failed (`ettelem.cpp` prints only the fields whose request succeeded).

**The fix,** [`reduce_e180_v3.py`](reduce_e180_v3.py): v1's per-pass reduction (`reduce_e180.reduce_pass`) and v2's per-burst readings
(`reduce_e180_v2.extras`), imported unchanged, run one pass at a time, as v1's and v2's mains run them, with three changes:
- when v1's reduction of a pass raises, that pass is set aside as `unreadable: <reason>`, and its record holds no D and no runs. The
  reason names the file and its first bad line, from a scan of what `bursts_of` reads: every `{` line is JSON; a sample's `t_ms`,
  `board_w`, `temp_c.minshire[0]`, `mhz.minion` and the three rails' first values are numbers; a run's fields are there. When the scan
  names nothing, the reason is the exception itself;
- when v2's readings of a kept pass raise, the pass stays kept with v1's D unchanged and every burst listed in `v2_unread`;
- a data directory that is not there gives no pass, never an error.

For every input v2 reduces without an error, v3's output is v2's, field for field, plus one `v3` record naming what it set aside. So the
registered rules read exactly what v1 and v2 give them.

**The box side stays fail-closed, as recorded.** On the box, `check_e180_v2.py block` still crashes on such a sample. The block then
reads fail and the queue stops after that pass, never retried. The passes before it are kept and scored at the desk. The verifier's scan
found 0 such lines in 3,607,077 committed samples (1,053 telemetry files).

## 4. A1-5's band test, and A1-7's per-kind marks (faults 5 and 6)

- **A1-5: "meets" binds,** registered here before any datum. A1-5 says a SIZE FAIL "with the measured interval inside the band" is read
  "not separated from the harts' start offset". The scorer has tested "meets" since kit note 1 (`score_e180_v2.py` line 147: the
  interval overlaps the band). That is the more cautious reading: it reads a SIZE FAIL as "outside P's offset band" only when the whole
  interval lies outside the band (+0.752 to +4.261 W), and as "not separated" whenever any part of it lies inside. It is a reported
  reading only: E180-A's SIGN is the verdict.
  [`score_e180_v3.py`](score_e180_v3.py) names the test in its output (`a1_5_band_test`). Kit note 1 section 2's "meets" was right and
  is now the stated rule.
- **A1-7's marks per kind:** the scorer v3 marks every fadd.ps.acc kind's reported reading with 261's walk label, and every fadd.pi.acc
  kind's with 262's ("the sums do not walk as registered" on a FAIL), as A1 section 7 says, beside v2's one summary line.
- **The scorer v3 is v2's** (imported and run unchanged) with these two additions and A1-7 read from the desk walk. On v2's own self-test
  sessions, 11 sessions under 5 walk readings, it equals v2 in every rule record, every reported arm and the owner's sentence (55 of 55).

## 5. Recorded, not changed: nits 7, 8 and 9 (box files; the planned day never meets them)

- **Nit 7, D1 with `USER` unset:** `others_d1_e180.sh` reads `awk -v me="$USER"` inside a command substitution, so with `USER` unset it
  reads "no one" (fails open). The planned route always sets `USER`. Step 11 v2 launches the session over ssh, `setsid nohup` inherits
  the login's environment, and the runner's check before every run inherits the session's. E171's and E178's D1 share the line. A later
  kit uses `me=$(id -un)`, as `rb_prelude`'s `hold_read` does.
- **Nit 8, the per-run holder check's sudo calls:** about 290 `sudo -n /usr/local/sbin/et-holders` calls in a FULL session, so sudo
  writes roughly 600-900 journal lines, about one call every 8 s for 45 min. The live collector stopped running et-who every second for
  exactly this. Each call reads only, and kit note 1 disclosed the count. Each adds about 0.3-1 s to a run, so the sixth pass still needs
  passes of 463 s or less (the readiness critic's estimate stands). A later kit keeps et-holders at the block and reads `ps` and
  `/proc/locks` between runs.
- **Nit 9, the reader's pin:** `harness-e180-v2.json` does not pin `build/ettelem/ettelem`, the reader E128's guard execs; block v2 checks
  only that it is executable. E178's and E181's harnesses pin it at one sha256, and on the planned day their sessions run first on the
  same box and check it there. A later kit pins it.
- **Fault 4's box side:** section 3.

## 6. The runbook as it now runs (KIT.md's box steps)

E180 runs by this table. It is kit note 1 section 6 with steps 2 and 11 replaced. Every box step is note 1's, unchanged.

| KIT.md box step | file | changed here |
|---|---|---|
| 1, the window | `rb/s02_window_e180.sh` | no |
| 2, the desk check | **[`rb/s03_desk_e180_v3.sh`](rb/s03_desk_e180_v3.sh)** | five hash lists, each with its count: 71, 55, 41, 90 and this note's 96 |
| 3, the post | (the card lane's) | no |
| 4, the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | no |
| 5, the sync | `rb/s07_a3_sync_e180_v2.sh` | no (note 1's: every harness file; this note adds none) |
| 6, the build and the checks on the box | `rb/s08_a3_build_e180_v2.sh` | no. Its walk line is v1's, kept beside: one of 261 and 262 is expected UNREAD there (section 1) |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | no |
| 8, the V3_DRY pass on the box | `rb/s10_a3_dry_e180_v2.sh` | no |
| 9, the session | `rb/s11_a3_session_e180_v2.sh` | no (needs the two v2 jobs ended rc 0 today) |
| 10, the wait | `rb/s20_wait_e180_v2.sh` | no |
| 11, release, then collect | **[`rb/s22_collect_e180_v3.sh`](rb/s22_collect_e180_v3.sh)** | the build record and the listing copied back; [`collect_e180_v3.sh`](collect_e180_v3.sh): the walk v2, reduce v3, score v3 |

- **A relaunch on the same day (nit 10, the operator's).** lib.sh's `block_begin` exits 0, "already done", for any pass directory that
  holds a `block.json`, a pass D1 stopped among them. A second launch would then skip those passes, take a skip's few seconds as the
  queue's first measured estimate, and keep passes from two sessions. So **no second launch of E180's session on a day without a dated
  departure written first.** The departure says either that the earlier pass directories were moved aside first (`p<P>` to
  `p<P>.attempt-<epoch>`, the block's own form for an earlier attempt, which every reduction skips), making it a fresh session, or that
  they stay, naming the two sessions the kept passes come from.
- [`rb/list_steps_e180_v3.sh`](rb/list_steps_e180_v3.sh) is the dry listing of this table
  ([`logs/dry-listing-e180-v3.txt`](logs/dry-listing-e180-v3.txt): 0 steps fail, no network call).
- [`rb/selftest_rb_e180_v3.sh`](rb/selftest_rb_e180_v3.sh) is the desk test of the two v3 steps, with stand-in ssh and rsync and a
  stand-in box ([`logs/selftest-rb-e180-v3.txt`](logs/selftest-rb-e180-v3.txt), **18 of 18**):
  - **A:** the dry listing;
  - **C1:** a good collection, the build record and the listing back, three copies;
  - **B1, B2:** the walk line saying no objdump, or absent: the listing not asked for, BUILD-E180.json alone back;
  - **B3, B4:** BUILD-E180.json, or the listing step 6 wrote, missing on the box: 14, the collector not called;
  - **C5-C7, P1, P2, D1:** v2's cases on v3;
  - **E1:** the real collector on the stand-in box. Its listing has 262's case before 261's, its own v1 line reads 261 UNREAD, and its
    BUILD-E180.json names a made-up toolchain owner. The desk walk reads 261 and 262 PASS, the box's line is kept beside, and the owner
    is in no output file.

## 7. The checks after the fix ([`logs/reruns-note2.txt`](logs/reruns-note2.txt))

| check | result |
|---|---|
| the four earlier hash lists: the registration's, the kit's, A1's, kit note 1's | 71, 55, 41, 90 OK |
| the plan and the forecasts `--check`; `make_harness_e180_v2.py --check`; `check_e180_v2.py harness` | CHECK PASS; CHECK PASS; HARNESS OK, 86 files (v2), identical to its log |
| v1's walk test, `selftest_elf_e180.py` | 9 of 9, identical to its log |
| **the walk v2's test, `selftest_elf_e180_v2.py`** | **35 of 35** ([`logs/selftest-elf-e180-v2.txt`](logs/selftest-elf-e180-v2.txt)) |
| v1's scorer self-test; v2's | 12 of 12; 7 of 7, each identical to its log |
| **the v3 reduction, scorer and collection test, `selftest_score_e180_v3.py`** | **14 of 14** ([`logs/selftest-score-e180-v3.txt`](logs/selftest-score-e180-v3.txt)) |
| D1's desk test | 13 of 13, identical to its log |
| the dry pass on the Intel, `dry_intel_e180_v2.sh` (the box files, unchanged) | DRY-INTEL-V2 PASS, 24 of 24, identical to its log |
| the runbook's v2 desk test; its dry listing | 26 of 26; 0 steps fail (only the scratch repository's file count and the listing's "minutes from now" differ: environment counts) |
| **the runbook's v3 desk test; the v3 dry listing** | **18 of 18; 0 steps fail, no network call** ([`logs/selftest-rb-e180-v3.txt`](logs/selftest-rb-e180-v3.txt), [`logs/dry-listing-e180-v3.txt`](logs/dry-listing-e180-v3.txt)) |
| `dmcmd_audit`: the v2 session's files (`preflight_e180_v2.sh`); the same without E153's exception; the v2 runbook steps with k6's 5 and 9; the v2 and A1 desk files | GO, 32 sites; NO-GO only at lib.sh:154 (the statistics reset, never sent); GO, 11 sites; GO, 0 sites: each byte for byte with its log |
| **`dmcmd_audit`: note 2's desk files; the runbook as it now runs** (note 2's v3 steps, note 1's v2 box steps, k6's 5 and 9, E128's guard) | **GO, 0 send sites; GO, 11 send sites, every one READ, all E128's guard's: the same 11 as v2's** ([`logs/dmcmd-audit-desk-v3.txt`](logs/dmcmd-audit-desk-v3.txt), [`logs/dmcmd-audit-rb-v3.txt`](logs/dmcmd-audit-rb-v3.txt)) |

None of the new files sends a device command. None names the firmware-revisions query, `--reset-ms`, a SET or a residency read. The walk
v2 reads a file, and the collector, reduction and scorer read the copied session; none opens a device or reaches a box. Only step 22 v3's
copies reach the box, by rsync, read-only.

## 8. Labels

- **Registered** (before any E180 datum): every rule, threshold, plan and forecast of E180.md (`4dc5035f`) and of dated note A1
  (`879197e3`), unchanged. This note registers no new rule. It binds A1-7's words over kit note 1's definitions (section 1) and A1-5's
  "inside" read as "meets" (section 4), each before any datum.
- No E180 datum exists, so nothing here is blind, held out or post hoc for E180. The layout count (43 of 43 pairs in reverse order, 40 of
  40 consecutive ids 104 instructions apart: the verifier's) is a post hoc read of a committed listing. The tests' outputs are plumbing on synthetic or committed inputs; none is a forecast or a verdict.

## 9. Files, the hash list, compute; what remains open

- **New files (19, and the hash list):**
  - this note;
  - the desk files `check_elf_e180_v2.py`, `build_record_e180.py`, `reduce_e180_v3.py`, `score_e180_v3.py`, `collect_e180_v3.sh`;
  - the runbook steps `rb/s03_desk_e180_v3.sh`, `rb/s22_collect_e180_v3.sh`, `rb/list_steps_e180_v3.sh`;
  - the tests `selftest_elf_e180_v2.py`, `selftest_score_e180_v3.py`, `rb/selftest_rb_e180_v3.sh`;
  - the logs `logs/selftest-elf-e180-v2.txt`, `logs/selftest-score-e180-v3.txt`, `logs/selftest-rb-e180-v3.txt`,
    `logs/dry-listing-e180-v3.txt`, `logs/dmcmd-audit-desk-v3.txt`, `logs/dmcmd-audit-rb-v3.txt`, `logs/reruns-note2.txt`.
- **[`SHA256SUMS-e180-kit-note2`](SHA256SUMS-e180-kit-note2), 96 entries:** these 19 and the 77 committed files they import, call,
  replace, read or cite, each unchanged. Box step 2 v3 checks it. Check it from the repository's root:
  `shasum -a 256 -c tools/claims-v3/e180/SHA256SUMS-e180-kit-note2`.
- **Compute:** every check ran here through the round's local slot (`slot.sh`), one job at a time at nice 10 and one core, 05:51-06:20
  PST (the times are in `logs/reruns-note2.txt`). No bench, mini, lab box or card was used. The tests ran in this lane's own clone and
  scratch, never in the lab clone, and their trees were removed by literal path.
- **Open, for the records and the card day:**
  1. E180 runs by section 6 of this note: box step 2 is `s03_desk_e180_v3.sh` and step 11 is `s22_collect_e180_v3.sh`. The card lane's
     brief should point here, not at KIT.md or note 1's section 6 alone.
  2. The build has still never been compiled on a box. Step 6 v2 is its first compile and the walk's first meeting with the box's own
     listing (KIT.md open item 2, unchanged). If the box's layout differs from the committed listing's, A1-7 reads what the listing
     shows, by section 1's words.
  3. No verifier has read this note. It changes no box file, so one can read it while E181 or E178 holds the card.
  4. Nits 7-9 wait for a later kit (section 5). The card-1 fallback runbook (note 1's open item 3) and the october-forecast-model freeze
     (E180.md section 8) are unchanged.

SPDX-License-Identifier: Apache-2.0
