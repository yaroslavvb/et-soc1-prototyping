# E198's card-lane brief: what the lane that runs E198 on aifoundry1 card 1 does, sitting by sitting, and what it never does (Q191; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q191, lane `kit-e198`), beside [KIT.md](KIT.md). The registration is
[E198.md](E198.md) (its subtree `5434394b...`, list `SHA256SUMS-e198-registration` `f66bae0f...`, 14 entries). No card was claimed or
opened, no device command was sent, nothing was posted; the one look at aifoundry1 (22:05:49 PST) read et-who, uptime, bubblewrap and our
own folders, and opened nothing. No E198 datum exists. This brief changes no arm, value, order, window, threshold, stop, cap, rest, rule,
the reduction or the forecast (E193's protocol and E198's rules, both registered).*

*Changed before the land and before any datum (Mon 16 Nov 2026, PST; Q191 lane `fix-e198`, after `verify-e198`): the registration's
anchors (E198.md fixed before the land: the sealed card-1 forecast registered as its freeze line 2, the anchor spin2 decided at four
measured passes); rows 0, 1 and 2 of section 3 name the booking's release and the quiet hold's removal (the verifier's finding 5); step 9
refuses any further E198 sitting after a watch hit or a device process that did not finish (finding 3; section 4).*

## 1. What the day must carry (E198.md 12, CONTEXT 122)

- **The go:** the owner's standing words of Sun 15 Nov 2026 (10:05:42 "continue, all machines are up"; 10:22:36 "don't worry about
  discord post, just use the machines, nobody is using them"; 17:21:16 "Feel free to use more cards in parallel ..."), and "Try again"
  (at or before 21:28:59 PST). E198's items are its registered defaults. **The post: waived** (his words of 10:22:36), recorded as waived.
- **The card:** aifoundry1 card 1 at 600 MHz as found, reads only, `--device 1`, ET_DEVICES=1 for every device process, card 1's lock
  `/run/lock/etsoc-shire1.lock`. **Nothing on card 0**: no E198 process opens a card-0 node (the private /dev holds none) or card 0's lock.
- **The order on aifoundry1 card 1** (CONTEXT 122): the E191 repeat, then **E198 (A, then B)**, then E199, each after its 40-minute rest
  (wait for the rest, THEN book); one session of ours on aifoundry1 at a time (the booking key `aifoundry1` is the whole box).
- **The sealed card-1 forecast** (CONTEXT 122): the orchestrator writes each posted sha256 to `W/out/orch/sealed-card1.txt`. **E198's
  (sha256 `7de55c4f...`, posted 22:56:05 PST Sun 15 Nov 2026) was registered before the land as E198.md's freeze line 2**, which answers
  CONTEXT 122's wait (until 08:00 PST Mon 16 Nov 2026 at the latest) for it. A further one posted after the land goes into the dated
  note `tools/claims-v3/sealed-card1/e198-freeze-lines.md` (outside E198's pinned subtree), committed under the desk-commit rule BEFORE
  the card day; **step 2 and the history check accept its addition and refuse any later change to it** (KIT.md section 6). Its contents
  stay sealed: the lane reads, scores and quotes no number of it.
- **The landed anchors:** the registration (subtree `5434394b...`, 14 of 14 OK) and the kit (its list `SHA256SUMS-e198-kit` and step 2,
  `rb/s03_desk_e198.sh`, outside that list, at the sha256 the land dir's LAND.md gives), both ancestors of GitHub main; no
  `docs/reports/data/*e198*` path before sitting A, none but sitting A's own before sitting B.

## 2. THE WINDOW FROM G (E198.md 12)

G is **the card lane's booking of aifoundry1 for the sitting** (`bash W/book.sh take aifoundry1 <lane>`). Step 1
(`rb/s02_window_e198.sh <A|B> <day> <G HH:MM:SS>`) writes last start = G + 1:30 and last end = G + 3:30, **each rounded up to the whole
minute, both inside G's Pacific day** (G at 20:29:00 or earlier; a later G is refused, 16: the sitting waits for a later day and a new
booking). **One booking for both sittings:** sitting A's G is the booking; **sitting B's G is sitting A's session end + 40 minutes** (the
rest's opening), written in B's own RB_OUT. Sitting A's cap (60 card-minutes) must fit before its last end, B's (50) before B's.

## 3. The steps, in order, for EACH sitting (paths under `tools/claims-v3/e198/`), with THE ONE-LAB RULE and THE QUIET HOLD

Run from the lab clone on aifoundry2, ONE RB_OUT PER SITTING (a new directory outside the repo), one `RB_LOCK`, and `RB_GITLOCK` for
step 2. k6's drivers bound every remote call; **a printed login link stops the step (11)** and appends `<HH:MM:SS> aifoundry1 needs a
check` to `RB_LOCK`; nothing is retried until it is cleared.

| # | the step | what to do with its exit |
|---|---|---|
| — | the booking: `bash W/book.sh take aifoundry1 <lane>` (G); the quiet hold for the card day: `bash W/hold.sh add <lane>` | G is the window's start; book only after the 40-minute rest of the previous session of ours on aifoundry1 has opened |
| — | **THE ONE-LAB RULE: `bash W/onelab.sh desk <lane>`** (bounded waits; exit 3: call again) | **from here to step 2, every stop path runs `bash W/onelab.sh undesk <lane>`** |
| 0 | by hand: `uptime` on aifoundry2 (THE LOAD RULE), GitHub main read, the anchor lines of the land dirs' LAND.md | any line not as stated: undesk, release the booking (`bash W/book.sh release aifoundry1 <lane>`) and remove the quiet hold (`bash W/hold.sh remove <lane>`): no box step that day |
| 1 | `rb/s02_window_e198.sh <A\|B> <day> <G>` | 0; 16 (past G's day): undesk, release the booking (`book.sh release`) and remove the quiet hold (`hold.sh remove <lane>`): no sitting today |
| 2 | `rb/s03_desk_e198.sh` with `RB_GITLOCK`, **never inside the lab-git lock** | 0; anything else: undesk, release the booking (`book.sh release`) and remove the quiet hold (`hold.sh remove <lane>`): no box step that day |
| — | **`bash W/onelab.sh undesk <lane>`** right after step 2 | always, whatever step 2 read |
| 4 | `rb/s05_look_e198.sh` (both cards: et-who counts by card, ps, our sessions and jobs; the reboot gate) | 0 FREE; 17 HELD: `--wait` polls, at most 30 minutes in all (15: skip today); 16: the reboot gate (aifoundry1 booted after E82's firmware read): no sitting, report |
| 5 | `rb/s07_a1_sync_e198.sh` | 0 (HARNESS OK and TREE OK on the box: E198's root, the tree's E191 guard 6fd26f51..., the reader 8008f96f...); 10/16: no sitting until fixed |
| 6 | `rb/s08_a1_build_e198.sh start`, then `wait` while 17 | 0: X04-BUILT (THE KERNEL GATE on E193's .text fd720727..., the bodies, the host's refusals, the listing SAME x3); 16: once more if first of the day, after a second: NO-THIRD-BUILD, no sitting today |
| 7 | `rb/s09_a1_reads_e198.sh` (**THE REST RULE FIRST**, then the manifest, card 1's config through E191's guard with ET_DEVICES=1, et-who) | 0; **17: the rest has not opened: call again after it (no config read was made)**; 16: card 1's config or identity not as found: no sitting |
| 8 | `rb/s10_a1_dry_e198.sh start`, then `wait` | 0 (the session with DRY=1 on the box: the private /dev listed, both listings SAME) |
| 9 | `rb/s11_a1_session_e198.sh <A\|B>` | 0 launched; 10 refused (the rest, a session or job of ours, no dry pass or build today, the tree off its pins, the smoke gate failed today, an earlier E198 sitting with a watch hit or a device process that did not finish (no further sitting before a dated note), for B no sitting A or a crashed A); 16 IDENTITY-STOP (the reboot gate) |
| 10 | `rb/s20_wait_e198.sh <A\|B>` again while 17 (it finds the session by its real name, `session_e198.sh`) | 0 ended, manifest written; 16 a gate stop (collect it) or MAIN-CRASHED (collect, report, kill nothing); 14 RUN-GONE: read the box (read-only), report |
| — | **THE ONE-LAB RULE: `bash W/onelab.sh collect <lane>`** right before step 11 | **from here to the data commit's push, every stop path runs `bash W/onelab.sh uncollect <lane>`** |
| 11 | `rb/s22_collect_e198.sh <A\|B>` | 0 COLLECTED: the data directory `docs/reports/data/<day>-e198-x04-clock-sitting-<a\|b>-aifoundry1-c1/`, or for a gate stop `docs/reports/gate-stops/<day>-e198-x04-clock-sitting-<a\|b>-T<T0>-aifoundry1-c1/` |
| 12 | the README in [DATA-README-FORM-e198.md](DATA-README-FORM-e198.md)'s form, the public-text scan, the data commit through `W/commit_lab.sh` (new files only; the card lane's own data commit is allowed under its quiet hold), its push | then **`bash W/onelab.sh uncollect <lane>`** right after the push |
| 13 | after the data commit only, never on a gate stop's record: `rb/s24_reduce_e198.sh <A\|B>`; after both (or A alone): `rb/s24_reduce_e198.sh score <A's x04-e198-A.json> [<B's>]` | the registered reducer, E193's checker, then the transport scorer, each unchanged; the records lane commits their outputs |
| — | sitting B: its own RB_OUT, G = A's session end + 40 minutes, steps 1-13 again (step 6: `wait` only, the day's build) | the booking kept for B; released (`book.sh release`) and the quiet hold removed (`hold.sh remove <lane>`) after B's data commit's push, or on any stop path that ends the day |

**To stop a sitting by hand** (the operator's stop, a registered stop): touch the running runner call's stop file,
`build/e198/T<T0>/smoke/STOP` or `build/e198/T<T0>/x04/STOP` on aifoundry1 (`~/nekko`), and `build/e198/T<T0>/STOP` (the session then
starts nothing more). **Never kill a process**: the runner ends its own device process and stops its sampler with SIGTERM; never a reset,
never a driver reload, never a power cycle.

## 4. After a gate stop, a registered stop, a watch hit or a crash

- **A gate stop** (`GATE-STOP:`; session.rc 3; no main run: a holder on either card, the two-card box, the private /dev, identity (a) or
  (b), the warden, the operator's stop, the watch, the smoke gate) is **no sitting: no data** (E198.md 13). Step 11 collects it into its
  gate stop's record (never `docs/reports/data/`), committed with the gate-stop README, never reduced. The sitting is tried again with no
  amendment after a gate before the smoke once it clears (with the rest), and after the smoke gate **not the same day**, except after a
  watch hit (below).
- **A registered stop, the deadline or the cap** (`main run stopped: ...`; session.rc 1): the passes done stand and are reduced as they
  stand; prices with fewer than 4 measured passes are NOT DECIDED; the missing passes are never re-run without a dated amendment.
- **A watch hit** (`session/holderd/WATCH-STOP`): a process of the sitting held a node other than card 1's. The runner's stop files were
  touched; report it at once with the line; kill nothing; collect; no further E198 sitting before a dated note (step 9 refuses one, 10,
  whether the hit ended the smoke as a gate stop or came in the main run).
- **A crash** (`main run ended without a registered stop`; session.rc 4; step 10's MAIN-CRASHED): report it, kill nothing, collect it
  into the data directory; a dated note decides whether its passes are reduced; no further sitting before that note.
- **A device process that did not finish** (the runner's "tell the lab admin": an exit 1 or other unexpected status, killed by
  `timeout`; or three incomplete launches, or "device process not ended" in its logs): stop the day, keep the booking, report to the owner
  and the lab admin; a card reset is never E198's to make. Step 9 refuses any further E198 sitting (B after A included) until a dated
  note decides (10).

## 5. What the lane reports

The booking and G; the window; the one-lab spans (desk and collect, with their waits); the quiet hold's span; each step's exit; the
session's first card command, end and card-minutes; the identity lines (counts only, no login); the warden's summary (holder checks
served, nodes held, watch hits: none expected); the smoke gate's line; passes done; stops; the host's runtime lines dropped by the guard;
peaks (board, die) and 600 MHz samples; the closing config read; the data commit; every departure, dated; the interpreter
(`/usr/bin/python3` 3.12.3 on aifoundry2; aifoundry1's python3 3.12.3 for the box's scripts, read 22:05:49 PST Sun 15 Nov 2026).

SPDX-License-Identifier: Apache-2.0
