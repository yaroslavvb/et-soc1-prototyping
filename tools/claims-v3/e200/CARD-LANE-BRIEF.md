# E200's card lane brief: the two sittings on aifoundry2 card 0, run from aifoundry2 itself (Q192, lanes kit-e200 and fix-e200; kitted, fixed before the land, not run)

*Mon 16 Nov 2026 (week 46), PST, desk only, beside [KIT.md](KIT.md), in E197's brief's form (`tools/claims-v3/e197/CARD-LANE-BRIEF.md`)
with E194's lines for this box (`tools/claims-v3/e194/CARD-LANE-BRIEF.md` and its dated note 1: THE QUIET DESK FLAG, the box that is the
desk). **The card day:** Mon 16 Nov 2026 or a later day, after E194's session on this card (it ended Mon 16 Nov 2026 00:49:00 PST), each
sitting's G its card lane's booking of aifoundry2 that day. This is a desk statement for the card lane and the readiness check, never the
owner's go. Every step below is a committed script run from the lab clone's top, each as one plain call from a script file (no `bash -c`,
no background `&`), with k6's exit codes: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder
for 30 minutes; 16 a gate says stop; 17 call again. Paths are under `tools/claims-v3/e200/` unless named.*

## 1. What the go carries (E200.md 12: the owner's standing words, the registration's items as defaults)

- **G1.** E200 on aifoundry2 card 0 under its governor as found (800 MHz under load, 600 MHz at rest; TDP 65 W, threshold 65 C), reads
  only (dmcmd_audit_v2 GO: 12 send sites, every one a READ, fwgate's firmware query among them by the owner's rulings), nothing set; one
  session of ours on this card at a time.
- **G2. The two sittings (E197's, E200.md 5).** Sitting 1: blocks A, B, C, D; the full plan (about 46 card-minutes at the mean climb, cap
  50) unless the window cannot hold it, then the short plan (about 37, cap 40), decided by step 7 at the sitting's first card command and
  logged. Sitting 2: block E, the ext plan (about 28, cap 35), only after a sitting 1 that ran its smoke and at least one train block with
  no stop naming the card (the owner may withhold it). T15 may be cut by the cap at long climbs (E200.md 10): never a failed check.
- **G3. The 40-minute rests (E200.md 11):** before sitting 1's first card command after E194's session (or any later session of ours on
  this card); between sitting 1's end and sitting 2's first card command; after sitting 2, before the next session of ours here.
- **G4. One day or two.** Each sitting its own window (section 4), each inside one Pacific day.
- **G5. The post: none,** the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST: "don't worry about discord post, just use
  the machines, nobody is using them"), unless his go names one.
- **G6. The host's package counter: NOT READ** (no E200 file reads rapl, powercap or energy_uj).
- **The freeze line** is the model session's sealed aifoundry2 forecast, registered in E200.md 0 before the land: sha256
  `2eba6ef4b60241674628dde125273db4547b0ba17dd6d5a3e30935c7c6e89733`, posted as #2.5.1.2.3 at 01:28:51 PST Mon 16 Nov 2026; step 2 checks it and prints it (a later one only by a dated note beside
  E200.md, before the first datum); the forecast stays sealed: no forecast number and no score in any lab file. E200 publishes 800 MHz
  prices only.

## 2. Setup and the order of the steps

    W=<the round's workflow folder>; LAB=<the shared lab clone>; LANE=<the lane's name>
    mkdir $W/out/$LANE/rb-e200-1     (new and empty: E200's own); later $W/out/$LANE/rb-e200-2 for sitting 2
    for sitting N: export RB_OUT=$W/out/$LANE/rb-e200-N RB_LOCK=<the round's lock file of checks> RB_GITLOCK=$W/locks/lab-git.lock
                   RB_QUIET=$W/locks/quiet-desk-aifoundry2
    <GH> = the round's environment-only HTTPS rewrite for git reads (never a config file)
    NEVER set E200_DESKTEST, E200_READER_SHA256, E200_CAP_S, E200_DIE_MAX_S or E200_DIE_POLL_S: they are the desk tests' (the session's
    start line names DESKTEST when set, and the collection refuses such a session)

**THE ORDER: B, D+, 0, H, 1, 2, D-; Q (the quiet desk flag); 4 the look, 5 the sync, 6 the build, 8 the dry pass; then, once the rest
has opened, 7 the reads and 9 the launch, back to back; 10, C+, 11, Q-, 12, C-, 13.** Step 7's first command to the card (fwgate's one
firmware read when its look reads NEEDS-READ, else the config read) is the sitting's first card command (KIT.md 4): the cap counts from
it, and step 7 reads the rest on the box before it sends anything; step 9 refuses more than 120 s after it. Steps 0-6 and 8 send nothing
to the card (the look reads fwgate's records, et-who and ps; the sync copies files; the build runs the host only to refusals before the
device layer; the dry pass opens nothing).

| step | call | expected | any other exit |
|---|---|---|---|
| B | `bash $W/book.sh take aifoundry2 $LANE` (the day's first sitting) | BOOKED; G = this moment (its owner file's time) | busy: no step at all; stop |
| D+ | `bash $W/onelab.sh desk $LANE` (THE ONE-LAB RULE, before steps 0, H and 2) | ONELAB: in its desk span | 3: call again (each call waits at most 9 minutes) |
| 0 | `uptime` (the load at most 8); the go's anchor lines at LAB's HEAD; GitHub main read | as stated | no step that day: D-, E |
| H | `bash $W/hold.sh add $LANE`; `git -C $LAB status --porcelain --untracked-files=all` | 0 lines | D-, hold remove, release, stop |
| 1 | `bash rb/s02_window_e200.sh <N> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (G+1:30 and G+3:30, rounded up) | "fits now: E200 sitting N ..." | "fits now: nothing", or 10: D-, E |
| 2 | `env <GH> bash $W/slot.sh bash rb/s03_desk_e200.sh` (NEVER inside the lab-git lock) | "desk check for sitting N: ..." | 16 naming only "pull" while GitHub was silent: again; else D-, E |
| D- | `bash $W/onelab.sh undesk $LANE` (right after step 2, and on every stop path from D+ to here) | left its desk span | |
| Q | `bash rb/quiet_e200.sh raise $LANE` (LANE=card-e200: it writes `e200 card-e200 <time>`; never write the flag by hand: steps 4-11 refuse any other form, the round's `<lane> <time>` among them), then `bash rb/quiet_e200.sh count --wait` (THE P2 COUNT 0) | QUIET: raised; P2 0 | raise 10 (another lane's flag up): wait, never overwrite; count 16: wait (bounded) until 0 |
| 4 | `bash rb/s05_look_e200.sh` | 0 FREE; the identity CONTINUITY, or NEEDS-READ (step 7 reads the firmware once) | 17: again with --wait (30 minutes in all); 15: E; 16 (fwgate STOPPED or NO-RECORD): no sitting on this boot, report to the owner, E |
| 3 | the post: waived (G5) | | |
| 5 | `bash rb/s07_sync_e200.sh` | synced into E200's root (build/claims-v3/aifoundry2/e200 in the box tree) | 10: a session or job of ours: read why; 16: commit nothing, read why |
| 6 | `bash rb/s08_build_e200.sh start` (the day's first sitting), then `... wait` while 17 | "built today on aifoundry2: regfile (REGFILE-BUILT ...)" | 16: start once more (at most two starts a day; a third is NO-THIRD-BUILD: no sitting that day) |
| 8 | `bash rb/s10_dry_e200.sh start`, then `... wait` while 17 | "the dry pass ended rc 0: E200-DRY ... LISTING SAME ..." | 14: no sitting that day; read why |
| - | WAIT until 40 minutes after our previous session's end on this card (E194's 00:49:00 for sitting 1; sitting 2: sitting 1's "session end") | | |
| 7 | `bash rb/s09_reads_e200.sh <N>` (its reads wait up to 6 s for our device processes and our live collector's reader, lab-monitor) | "sitting N: rest: ...; the plan: full; the firmware identity: ...; the first card command stamped ...", then "aifoundry2 card 0: the firmware identity ...; config TDP 65 W / 65 C / 600 MHz at rest ...: run step 9 now" | 10 "REFUSED: <m> minutes since ...": wait, run it again (nothing was sent); 16 (fwgate's read not EQUAL, or the configuration not 65 W / 65 C / 600 MHz): no sitting, set nothing, report; 16 "no config read came back": once more after the look reads FREE; 17: look again with --wait, then step 7 again (the stamp stays) and step 9 at once, else a new RB_OUT (steps 1, 6's wait, 8, then 7 and 9) |
| 9 | `bash rb/s11_session_e200.sh <N>` AT ONCE | "E200 sitting N launched on aifoundry2 card 0 (T0 <T0>, plan <plan>) past fwgate's guard" | 16 "more than 120 s": no sitting on this RB_OUT today (a new try needs a new RB_OUT and step 7); 16 IDENTITY-STOP: no sitting on this boot, report; 10: read why, never go around it |
| 10 | `bash rb/s20_wait_e200.sh <N>` while 17 | 0 ended (with "STOPPED" when a registered stop ended it after its trains began) | 16 GATE-STOPPED: collect (step 11) as a gate stop's record; 16 CRASHED or HUNG: section 3; 14: wait once more, then read the box read-only |
| 4' | the look after: `bash rb/s05_look_e200.sh` once the session has ended | 0 FREE: nothing of ours holds the card | 17: read who holds it, read-only; a holder of ours after the session's end is a finding: write it up, kill nothing |
| C+ | `bash $W/onelab.sh collect $LANE` (before step 11) | in its collect span | 3: call again |
| 11 | `bash $W/slot.sh bash rb/s22_collect_e200.sh <N>` (at least 10 minutes before the last end) | "collected docs/reports/data/<day>-e200-regfile-sitting-<N>-aifoundry2 ..." or the gate stop's record | 16: commit nothing; read why; Q- and C- (E) |
| Q- | `bash rb/quiet_e200.sh lower $LANE` (after step 11's COPY-BACK EXACT, and on every stop path after Q) | QUIET: lowered | 10: the flag is not ours: leave it, read why |
| 12 | the README in DATA-README-FORM-e200.md's form; the public-text scan; `LAB_QUIET_HOLD_OWNER=$LANE bash $W/commit_lab.sh "<subject>" "<body>" <the data dir>` | "COMMIT_LAB: pushed <sha>" | 5 or 6: run it again |
| C- | `bash $W/onelab.sh uncollect $LANE` (after the push, and on every stop path from C+ to here) | | |
| 13 | `bash $W/slot.sh bash rb/s24_reduce_e200.sh <N>` (after the data commit only; never on a gate stop's record; after a crash only on a dated note) | "reduced after sitting N: regfile-e200-s1.json (sitting 2: regfile-e200.json, the pooled reduction) and checks-e200-N.json ..." | 10: the data is not committed; 16: reduce nothing, read why |
| E | on every stop path, after the last step that ran: D- if inside D+..D-; Q- if after Q and before Q-; C- if inside C+..C-; then `bash $W/hold.sh remove $LANE` after each sitting's data commit or its stop; `bash $W/book.sh release aifoundry2 $LANE` after the day's last sitting | | a flag left blocks the other lanes' commits, collections, desk spans and desk tests |

**Sitting 2 on the same day:** keep the booking; a new RB_OUT; then D+, 0, H, 1 (sitting 2's window: G = sitting 1's end + 40 minutes),
2, D-, Q, 4, 5, 6 (wait only), 8, WAIT until 40 minutes after sitting 1's end, 7, 9, 10, 4', C+, 11, Q-, 12, C-, 13 (the pooled
reduction), E. Step 7 refuses sitting 2 unless sitting 1's log on the box reads `SITTING-RESULT: smoke passed; train blocks complete
<k >= 1> ...; card stop none` and no crash; else sitting 2 needs a dated amendment.

## 3. Stop paths (each ends with E; nothing is ever killed)

- **Every stop path clears its flags first:** D- inside D+..D- (step 0 not as stated, H's status, step 1, step 2's 16); Q- after Q and
  before Q- (any stop from the look to the copy-back: the session itself is collected first when it ran); C- inside C+..C- (step 11's 16,
  COPY-BACK NOT EXACT, a gate at step 11, step 12 not pushed). A flag left behind blocks the other lanes.
- **Before the session** (B busy; step 0; H; step 1 "fits nothing"; step 2's 16; step 4's 15 or 16; steps 5, 6, 8: 16 or NO-THIRD-BUILD;
  step 7's 16): no sitting that day: no data, never a failed check.
- **THE REBOOT GATE stops** (step 4 or 7 or 9: fwgate's look STOPPED or NO-RECORD, its read DIFFERENT or UNREADABLE, its guard
  IDENTITY-STOP): no E200 sitting on this boot; nothing is retried (fwgate's ledger stops every later read, look and guard of this card
  for the boot); collect step 7's folder (`build/e200/first-s<n>-<FIRST>/` in the box tree) for the record and report to the owner.
- **A login link (11) at any step:** the line is appended to RB_LOCK, nothing is retried, and that day's box steps end until the check is
  cleared. A session already detached keeps running: wait and collect once the check is cleared, the same day.
- **A gate stop (GATE-STOPPED):** no block began: no train block, no data. Collected as a gate stop's record under docs/reports/gate-stops/,
  never reduced. After a holder, the lock or a refusal: try again once the gate has cleared, in a NEW RB_OUT with its own step 7 (the rest
  rule skips a session that opened no device). After a smoke failure (the runner's gate, or the kit's check with the smoke's clock) or THE
  DIE GATE: not the same day (step 9 refuses a smoke-failed day; steps 7 and 9 refuse a day whose E200 log holds the die gate's
  GATE-STOP, and that stop is counted by the rest rules).
- **A registered stop after the trains began** (a live stop with aifoundry2's lines, C3's clock, a holder between blocks, a failing device
  process, the cap, the deadline, the operator's stop): the trains done are reduced as they stand (E200.md 13); the missing trains are never
  re-run without a dated amendment. Sitting 2 follows only if the stop did not name the card.
- **A crash (CRASHED, the wrapper's exit 9):** report it at once, kill nothing, collect it, commit those records, stop the day; a dated note
  decides whether its trains are reduced; no sitting 2 before that note (steps 7 and 9 refuse).
- **A HUNG device process (departure D1: no KILL):** KILL NOTHING, reset nothing, no PMIC or power action; keep the booking, the hold, the
  quiet desk flag and the card lock as they are; write it up and escalate to the owner. The session ends by itself if the host ends.
- **A session that does not end, or a card that stops answering:** never kill a device process, never reset; keep the booking, the hold
  and the flag, write it up, escalate to the owner.
- **The operator's stop, by hand,** only if the owner asks or a reading calls for it: `touch
  ~/claude/et-soc1-prototyping/build/e200/T<T0>/run/STOP` from a script file (the launch in flight finishes; nothing is killed).

## 4. The window and the order on aifoundry2

From G (the card lane's booking of aifoundry2 for that sitting: `book.sh take` prints BOOKED, its owner file records the time): **last
start G+1:30, last end G+3:30, each rounded up to the whole minute, inside that Pacific day: G at 20:29:00 PST or earlier** (E200.md 12;
step 1 refuses a last end that is not the last start + 2:00). The start is the sitting's first card command (step 7), the end its
sampler's stop. Step 7 refuses after the last start; step 9 refuses unless the plan's cap from the first card command fits before the last
end; step 11 must start 10 minutes before the last end.

| | example (desk arithmetic from the registered figures) |
|---|---|
| sitting 1, booked at 06:10:20 | `rb/s02_window_e200.sh 1 <day> 07:41 09:41`; steps 2-8 about 15-25 minutes; step 7 no earlier than 40 minutes after E194's 00:49:00 (open from 01:29); the session about 47 minutes from step 7 (cap 50); collected and committed within about 30 minutes of its end |
| sitting 2, the same day | G = sitting 1's end + 40 minutes (its rest's opening), say 07:40 + 0:40 = 08:20: `rb/s02_window_e200.sh 2 <day> 09:50 11:50`; the session about 29 minutes from step 7 (cap 35) |

**The order:** E194's session first (done, 00:13-00:49 PST Mon 16 Nov 2026), then E200 sitting 1 at least 40 minutes after it, then
sitting 2; never two of ours on this card (book.sh key aifoundry2). E200's rest rule reads every session-log form of ours in every tree of
ours on this box (E194's and E190 arm A's among them); E200's own log is the kits' form, so later rest rules read it too.

## 5. Never

- Never kill a device process: no SIGKILL, no `timeout -k`, no `kill -9`; never reset the card; no power cycle, no PMIC write, no firmware
  change, no OTA, no driver reload (the field manual's gates bind them; none is E200's).
- Never set anything: no governor, TDP, threshold, clock, voltage or fan; no statistics reset (`--reset-ms`). The firmware-revisions query
  is a read (the owner's rulings of 15:07:01 and 15:09:49 PST, Sun 15 Nov 2026), sent only by fwgate's read, once a boot.
- Never send a card command for a sitting before its rest has opened (step 7 reads the rest first); never run step 9 more than 120 s after
  step 7.
- Never two sessions of ours on this card; never a session outside its window; never sitting 2 before a sitting 1 that qualifies.
- Never start, beside a sitting, a process of ours named like a device process or a session or queue script on this box: THE QUIET DESK
  FLAG is up from the look to the copy-back; the P2 count must read 0 at the look and at the launch.
- Never run step 2 inside the lab-git lock; never edit, pull or commit in LAB by hand; commits only through commit_lab.sh.
- Never edit a committed file of E200 or E197 (the registrations, the proposal's copy, the kits); a change is a dated amendment or kit note
  beside it, committed before the data it touches.
- Never put a forecast number or a score in a lab file; never a lab user's login, a credential or a private page's number.
- On this box E200 writes only its root (build/claims-v3/aifoundry2/e200 in the box tree), build/e200/ and the runbook's build/q141k/
  entries, fwgate's ledger (`~/.local/state/fwgate/aifoundry2-c0.jsonl`, by fwgate itself) and RB_OUT.

## 6. Gaps the go should know (none blocks; each is the kit's registered behaviour or a reading the desk cannot make)

1. **The host on this card:** the desk ran the real host only to its refusals and its table; its launches, its REGFILE lines and the
   runtime's teardown meet the card first in the smoke (C3 reads the smoke's own counts first).
2. **The governor's climb:** the desk's stand-in climbs inside each process; the card's climb is E190 arm A's measured 0.01-1.33 s; a
   climb past 1.5 s sets that process aside (never re-run); three processes in a row off 800 MHz end the sitting (C3).
3. **The session's median clock:** C1 sets aside every process of a session whose median clock is not 800 MHz; a whole sitting's trains
   fill it at 800 MHz, but a sitting cut very short (more idle than trains) reads 600 MHz and gives no datum (the real-path case RCM).
4. **Our own live collector** can hold the management node for a moment at the free checks (the wrapper re-reads up to 3 times for a
   reader of ours; run_session.sh's own check reads once: a collision there is a gate stop before the sampler, tried again in a new RB_OUT).
5. **fwgate's one read:** if its look reads NEEDS-READ (no committed record after this boot), step 7 reads the firmware once (a READ);
   anything but EQUAL stops E200 on this boot. If a later round adds `15cb0fcb`'s read to fwgate's records first, the look reads
   CONTINUITY and nothing is sent (step 2's harness check names the added record and passes; the sync carries it).
6. **The deadline's margin** at the card's real pace and **T15 at long climbs** (E200.md 10): estimates, not measured.

SPDX-License-Identifier: Apache-2.0
