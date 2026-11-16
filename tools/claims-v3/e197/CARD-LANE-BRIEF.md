# E197's card lane brief: the two sittings on aifoundry3 card 0, run from aifoundry2 (Q185, lane kit-e197; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, desk only, beside [KIT.md](KIT.md), in E193's brief's form (`tools/claims-v3/e193/CARD-LANE-BRIEF.md`);
fixed before the land by Q191's lane `fix-e197` (verify-e197's F2 and F3: step 9's 120 s bound, with KIT.md 4's table and gap 3 below;
the ONE-LAB flags cleared on every stop path). **The card day:** Mon 16 Nov 2026 or a later day, each sitting's G its card lane's
booking of aifoundry3 that day.
This is a desk statement for the card lane and the readiness check, never the owner's go. Every step below is a committed script run
from the lab clone's top, each as one plain call from a script file (no `bash -c`, no background `&`), with k6's exit codes: 0 done; 10
refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes; 16 a gate says stop; 17 call
again. Paths are under `tools/claims-v3/e197/` unless named.*

## 1. What the go must carry (E197.md 12)

- **G1.** E197 on aifoundry3 card 0, at 600 MHz as found, reads only (dmcmd_audit GO: 11 send sites, every one a READ), nothing set;
  one session of ours on aifoundry3 at a time.
- **G2. The two sittings.** Sitting 1: blocks A, B, C, D; the full plan (about 45 card-minutes, cap 50) unless the window cannot hold
  it, then the short plan (about 36, cap 40), decided by step 7 at the sitting's first card command and logged. Sitting 2: block E, the
  ext plan (about 28 card-minutes, cap 35), only after a sitting 1 that ran its smoke and at least one train block with no stop naming
  the card (E197.md 6: the lab's choice; the owner can withhold it). About 73 card-minutes in all, at most 85.
- **G3. The 40-minute rests:** before sitting 1's first card command after any earlier session of ours on aifoundry3 (the round's order
  there is E195, E196, then E197: each 40 minutes after the last); between sitting 1's end and sitting 2's first card command; after
  sitting 2, before the next session of ours there.
- **G4. One day or two.** Each sitting its own window (below), each inside one Pacific day; both on one day when the day holds them with
  the rest between, else sitting 2 on a later day (its own window; its build started again that day).
- **G5. The post route:** the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST: "don't worry about discord post, just
  use the machines, nobody is using them"), unless his go names a post.
- **G6. The host's package counter: NOT READ.** No E197 file has a step or option that reads it (no rapl, powercap or energy_uj in any
  file under tools/claims-v3/e197).
- The freeze line is in E197.md (section 0, `e8e1746e...`); the forecast stays sealed: no forecast number and no score in any lab file.

## 2. Setup and the order of the steps

    W=<the round's workflow folder>; LAB=<the shared lab clone>; LANE=<the lane's name>
    mkdir $W/out/$LANE/rb-e197-1     (new and empty: E197's own); later $W/out/$LANE/rb-e197-2 for sitting 2
    for sitting N: export RB_OUT=$W/out/$LANE/rb-e197-N RB_LOCK=<the round's lock file of checks> RB_GITLOCK=<the lab-git lock>
    <GH> = the round's environment-only HTTPS rewrite for git reads (never a config file)

**THE ORDER: 5 the sync, 6 the build, 8 the dry pass; then, once the rest has opened, 7 the reads and 9 the launch, back to back.** Step
7's config read is the sitting's first card command (KIT.md 4): the cap counts from it, and its wrapper reads the rest on the box
before it sends anything; step 9 refuses more than 120 s after it. Steps 0-6 and 8 send nothing to the card (the look reads
et-who and ps; the sync copies files; the build runs the host only to refusals before the device layer; the dry pass opens nothing).

| step | call | expected | any other exit |
|---|---|---|---|
| B | `bash $W/book.sh take aifoundry3 $LANE` (the day's first sitting) | BOOKED; G = this moment | busy: no ssh to aifoundry3 at all; stop |
| D+ | `bash $W/onelab.sh desk $LANE` (THE ONE-LAB RULE, before steps 0, H and 2) | ONELAB: in its desk span | 3: call again (each call waits at most 9 minutes) |
| 0 | `uptime` (the load at most 8); the go's anchor lines at LAB's HEAD | as stated | no box step that day: E |
| H | `bash $W/hold.sh add $LANE`; `git -C $LAB status --porcelain --untracked-files=all` | 0 lines | hold remove, release, stop |
| 1 | `bash rb/s02_window_e197.sh <N> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` | "fits now: E197 sitting N ..." | "fits now: nothing": E |
| 2 | `env <GH> bash $W/slot.sh bash rb/s03_desk_e197.sh` (NEVER inside the lab-git lock) | "desk check for sitting N: ..." | 16 naming only "pull" while GitHub was silent: again; else E |
| D- | `bash $W/onelab.sh undesk $LANE` | left its desk span | |
| 4 | `bash ../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | 0 FREE | 17: again with --wait (30 minutes in all); 15: E |
| 3 | the post: waived (G5) unless the go names one | | |
| 5 | `bash rb/s07_a3_sync_e197.sh` | synced | 10: a session or job of ours on the box: read why; 16: commit nothing, read why |
| 6 | `bash rb/s08_a3_build_e197.sh start` (the day's first sitting), then `... wait` while 17 | "built today on aifoundry3: regfile (REGFILE-BUILT ...)" | 16: start once more (at most two starts a day; a third is NO-THIRD-BUILD: no sitting that day) |
| 8 | `bash rb/s10_a3_dry_e197.sh start`, then `... wait` while 17 | "the dry pass ended rc 0: E197-DRY ... LISTING SAME ..." | 14: no sitting that day; read why |
| - | WAIT until 40 minutes after our previous session's end on aifoundry3 (sitting 2: sitting 1's "session end") | | |
| 7 | `bash rb/s09_a3_reads_e197.sh <N>` | "sitting N: rest: ...; the plan: full; the first card command stamped ..." then k6's 0 | 10 "REFUSED: <m> minutes since ...": wait, run it again (nothing was sent); 16: no sitting that day, set nothing; 17: look again with --wait; then step 7 again (the stamp stays) and step 9 at once if the stamp is under about 90 s old, else a new RB_OUT (steps 1, 6's wait, 8, then 7 and 9) |
| 9 | `bash rb/s11_a3_session_e197.sh <N>` AT ONCE | "E197 sitting N launched on aifoundry3 (T0 <T0>, plan <plan>)" | 16 "more than 120 s": no sitting on this RB_OUT today (a new try needs a new RB_OUT and step 7); 10: read why, never go around it |
| 10 | `bash rb/s20_wait_e197.sh <N>` while 17 | 0 ended (with "STOPPED" when a registered stop ended it after its trains began) | 16 GATE-STOPPED: collect (step 11) as a gate stop's record; 16 CRASHED or HUNG: section 3; 14: wait once more, then read the box read-only |
| 4' | the look after (E197.md 18.2: "before and after"): `bash ../q141k-runbook/k6/s05_look_k6.sh aifoundry3` once the session has ended | 0 FREE: nothing of ours holds the card | 17: read who holds it, read-only; a holder of ours after the session's end is a finding: write it up, kill nothing |
| C+ | `bash $W/onelab.sh collect $LANE` (before step 11) | in its collect span | 3: call again |
| 11 | `bash $W/slot.sh bash rb/s22_collect_e197.sh <N>` (at least 10 minutes before the last end) | "collected docs/reports/data/<day>-e197-regfile-sitting-<N>-aifoundry3: ..." or the gate stop's record | 16: commit nothing; read why |
| 12 | the README in DATA-README-FORM-e197.md's form; the public-text scan; `LAB_QUIET_HOLD_OWNER=$LANE bash $W/commit_lab.sh "<subject>" "<body>" <the data dir>` | "COMMIT_LAB: pushed <sha>" | 5 or 6: run it again |
| C- | `bash $W/onelab.sh uncollect $LANE` (after the push) | | |
| 13 | `bash $W/slot.sh bash rb/s24_reduce_e197.sh <N>` (after the data commit only; never on a gate stop's record; after a crash only on a dated note) | "reduced after sitting N: regfile-e197-s1.json (sitting 2: regfile-e197.json, the pooled reduction) and checks-e197-N.json ..." | 10: the data is not committed; 16: reduce nothing, read why |
| E | on a stop inside a ONE-LAB span, first: `bash $W/onelab.sh undesk $LANE` after D+ and before D- (steps 0, H, 1, 2), `bash $W/onelab.sh uncollect $LANE` after C+ and before C- (step 11's 16, COPY-BACK NOT EXACT, step 12 not pushed); then `bash $W/hold.sh remove $LANE` after each sitting's data commit or its stop; `bash $W/book.sh release aifoundry3 $LANE` after the day's last sitting | | on every stop path, after the last step that ran (onelab.sh's rule: a flag left blocks the other lanes' commits, collections and desk spans) |

**Sitting 2 on the same day:** keep the booking; a new RB_OUT; then D+, 0, H, 1 (sitting 2's window), 2, D-, 4, 5, 6 (wait only), 8,
WAIT until 40 minutes after sitting 1's end, 7, 9, 10, 4', C+, 11, 12, C-, 13 (the pooled reduction), E. Step 7 refuses sitting 2 unless
sitting 1's log on the box reads `SITTING-RESULT: smoke passed; train blocks complete <k >= 1> ...; card stop none` and no crash; else
sitting 2 needs a dated amendment (E197.md 6).

## 3. Stop paths (each ends with E; nothing is ever killed)

- **Every stop path clears its ONE-LAB flag first** (onelab.sh's header): a stop after D+ and before D- (step 0 not as stated, H's
  status, step 1 "fits nothing", step 2's 16) runs `bash $W/onelab.sh undesk $LANE`; a stop after C+ and before C- (step 11's 16,
  COPY-BACK NOT EXACT, a gate at step 11, step 12 not pushed) runs `bash $W/onelab.sh uncollect $LANE`; then E. A flag left behind
  blocks the other lanes' commits (commit-ok), collections and desk spans.
- **Before the session** (B busy; step 0 not as stated; H's status; step 1 "fits nothing"; step 2's 16; step 4's 15; steps 5, 6, 8: 16
  or NO-THIRD-BUILD; step 7's 16): no sitting that day: no data, never a failed check.
- **A login link (11) at any step:** the line is appended to RB_LOCK, nothing is retried, and that day's box steps end until the check is
  cleared. A session already detached keeps running: wait and collect once the check is cleared, the same day.
- **A gate stop (GATE-STOPPED):** no block began: no sitting, no data. Collected as a gate stop's record under docs/reports/gate-stops/
  (never under docs/reports/data/), never reduced. After a holder, the lock or a refusal: try again once the gate has cleared, in a NEW
  RB_OUT with its own step 7 (the first card command of the new try; the rest rule skips a session that opened no device). After a smoke
  failure (the runner's gate or the kit's check): not the same day (step 9 refuses).
- **A registered stop after the trains began** (a live stop, a holder between blocks, a failing device process, the cap, the deadline,
  the operator's stop): the trains done are reduced as they stand (E197.md 11); step 10 reads 0 with "STOPPED"; the missing trains are
  never re-run without a dated amendment. Sitting 2 follows only if the stop did not name the card.
- **A crash (CRASHED: "the trains ended without a registered stop", the wrapper's exit 9):** report it at once, kill nothing, collect it
  (its data directory, when a block began), commit those records, stop the day; a dated note decides whether its trains are reduced, and
  no sitting 2 runs before that note (steps 7 and 9 refuse).
- **A HUNG device process (departure D1: no KILL):** a host still running after its timeout's TERM; the kit's watch has written STOP and
  a HUNG line. KILL NOTHING, reset nothing, no PMIC or power action; keep the booking, the hold and the card lock as they are (the lock
  stays with the process's own descriptor); write it up and escalate to the owner. The session ends by itself if the host ends.
- **A session that does not end, or a card that stops answering:** never kill a device process, never reset; keep the booking and the
  hold, write it up, escalate to the owner.
- **The operator's stop, by hand,** only if the owner asks or a reading calls for it: `ssh -o BatchMode=yes aifoundry3 touch
  aifoundry/build/e197/T<T0>/run/STOP` (the launch in flight finishes; nothing is killed).
- **After the session:** COPY-BACK NOT EXACT or a gate at step 11 means commit nothing and `onelab.sh uncollect` (above); collect again only once the cause is known, into
  a new RB_OUT/e197-raw (move the partial one aside), the same day.

## 4. The windows and the order on aifoundry3

From G (his go's moment, or under his standing go the card lane's booking of aifoundry3 for that sitting): **last start G+1:30, last end
G+3:00**, where the start is the sitting's first card command (step 7) and the end its sampler's stop, inside one Pacific day. Step 1
records it, one window a sitting; step 7 refuses after the last start; step 9 refuses unless the plan's cap from the first card command
fits before the last end; step 11 must start 10 minutes before the last end; step 10 reads only a T0 written today.

| | example (desk arithmetic from the registered figures) |
|---|---|
| sitting 1, G 09:00 | `rb/s02_window_e197.sh 1 <day> 10:30 12:00`; the box steps about 15-25 minutes (the first build on the box longer), then the rest; launch by 10:30 at the latest; the session about 47 minutes from step 7 (cap 50); collected and committed within about 30 minutes of its end |
| sitting 2, the same day | its own G (a booking kept from sitting 1: G at sitting 1's end, say 10:20): `rb/s02_window_e197.sh 2 <day> 11:50 13:20`; step 7 no earlier than 40 minutes after sitting 1's "session end"; the session about 29 minutes from step 7 (cap 35) |
| a later day | each sitting its own go and window; sitting 2's build started again that day |

The order: after the sessions of ours queued before E197 on aifoundry3 (E195, then E196: the round's order), each 40 minutes after the
last; never two of ours there at once (book.sh key aifoundry3). E197's rest rule reads every session-log form of ours on the box, theirs
included; E197's own log is the kits' form, so their rest rules read it too.

## 5. Never

- Never kill a device process: no SIGKILL, no `timeout -k`, no `kill -9`; never reset the card; no power cycle, no PMIC or firmware
  action, no driver reload (the field manual's gates).
- Never set anything: no governor, TDP, threshold, clock, voltage or fan; no statistics reset (`--reset-ms`); never the
  firmware-revisions query.
- Never send a card command for a sitting before its rest has opened (step 7's wrapper reads the rest first); never run step 9 more
  than 120 s after step 7.
- Never two sessions of ours on aifoundry3; never a session outside its window; never sitting 2 before a sitting 1 that qualifies.
- Never run step 2 inside the lab-git lock; never edit, pull or commit in LAB by hand; commits only through commit_lab.sh.
- Never edit a committed file of E197 (the registration, the proposal's copy, the kit); a change is a dated amendment or kit note
  beside it, committed before the data it touches.
- Never put a forecast number or a score in a lab file; never a lab user's login, a credential or a private page's number.
- Never touch aifoundry2's /dev/et* or /run/lock/etsoc-shire*.lock; on aifoundry3 E197 writes only its root
  (build/claims-v3/aifoundry3/e197), build/e197/ and the runbook's build/q141k/ entries.

## 6. Gaps the go should know (none blocks; each is the kit's registered behaviour or a reading the desk cannot make)

1. **The host on the card:** the desk ran the real host only to its refusals and its table; its launches, its REGFILE lines and the
   runtime's teardown meet the card first in the smoke.
2. **The host-output parser** (KIT.md 8): the registered runner drops a REGFILE line a runtime print splits or glues a fragment to;
   aifoundry3's runtime printed no byte on a host's stdout in any committed output, and the E197 host writes each line in one write of
   at most 4,096 B after the device is open, so no amendment is proposed. If it ever happened, the smoke gate stops the sitting before any
   train (no data), or a train loses that one process (two in a row stop the sitting): never a wrong datum.
3. **The deadline's margin** (KIT.md 4, its table; desk arithmetic): step 9 and the wrapper refuse more than 120 s after step 7's
   stamp (600 s until `fix-e197`, verify-e197's F2), so the gap to the sampler's start stays at about 125 s or less. At the planned
   5.7 s a train process every plan is whole at any such gap. Slower processes lose block D's last trains by the runner's own rule,
   the block ending with its anchors, reduced as it stands: the full plan T15 from 5.9 s (from a gap of about 120 s; at any gap at
   6.2 s, with T12 too from about 120 s); the short plan T12 from 5.8 s (T13 too at 6.2 s and about 120 s); sitting 2 is whole up to
   6.2 s. At the old 600 s bound the full plan lost T13, T12 and T15 even at 5.5 s, and sitting 2 lost every train. Run step 9 at once.
4. **Our own live collector on aifoundry3** reads the card's temperature once a second (about 4 ms on the single-open management node,
   only while et-who finds no holder). Step 7's config read or the session's sampler start can meet it (about 0.4-0.5 % an open, by
   E192's readiness estimate; not measured): step 7 would read "no config read came back" (16: no sitting that day; run it again only
   after reading why); the sampler would write nothing, and the runner's first reading stops the smoke (exit 4: a gate stop, tried again
   in a new RB_OUT).
5. **The box's sampler and holder check** (build/ettelem/ettelem behind E128's guard, et-who) meet the session first on the day; step 7
   reads the config through the same guard just before.
6. **The signal read on aifoundry3's build** (build_e197.sh, SIGNAL-READ) is reported, never a gate: a host that ignores TERM is the
   hang watch's (section 3).

SPDX-License-Identifier: Apache-2.0
