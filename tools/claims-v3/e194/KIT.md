# E194's run kit: the blind day's runner on aifoundry2's own card 0, orchestrated from aifoundry2 itself; E191's kit ported back to a card on the orchestrating box, with THE CLOCK RULE live, the host's line read whole, the holder re-read for our own live collector, THE QUIET DESK FLAG and the box-tree gate (Q183; kitted, verified and fixed before the land, not run)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q183, lane `kit-e194`). **Written after E194's registration** ([`E194.md`](E194.md),
its list `SHA256SUMS-e194-registration` sha256 `788af7da...`, 17 entries; its bytes frozen in the local commit `0d8e3de0` at 11:08:30 PST,
landing with its dated note 1 before this kit) **and before any
E194 datum.** It carries out the registration's steps and registers kit mechanics and gates made stricter for safety, each named in section
4; **nothing here changes a forecast, a band, a rule, a threshold, K, the order, the plan, the card time, the cap, a registered stop line or
the scorer.** No card was claimed or opened (aifoundry2 has a card: every desk test that ran a host, a runner, a stand-in session or a
stand-in box ran in the round's sandbox, with no /dev/et* and an empty /run/lock; the one real built host that was run to its device open,
the parser test's P7, ran with /sys hidden too), no device command was sent, no other lab box was reached, nothing was posted. New files
only, all under `tools/claims-v3/e194/`. This is the kit E194.md 17 asks for: **E191's kit (`eb1ac923`, with both of its verifiers' fixes)
ported back to a card on the orchestrating box** in E190 arm A's form (that card day's steps ran on this very card from this box, Fri 13
Nov 2026), every E191 and E189 file unchanged beside it. **Fixed after its verifier, the same day and before any E194 datum** (lane
`fix-e194`, from 14:09 PST): verify-e194's medium finding, its two minor findings and its five nits are answered in section 11, each kit
mechanics or a gate made stricter; the registration's 18 files are unchanged, and its dated note 1 (`E194.md.dated-note-1.md`, with
`SHA256SUMS-e194-note1`) lands with them.*

**THE REBOOT GATE IS CLOSED TODAY (section 8, item 1; the card-lane brief, section 1).** aifoundry2 booted 2026-11-13 16:53:28 PST, after E69's
firmware read of record (2026-10-27 13:56:26 PDT); k6's guard refuses every launch on it (IDENTITY-STOP) and the look reads 16. The kit keeps
that gate as it is; E194's session needs the owner's ruling on the firmware identity across that reboot before any card time.

## Results first (desk checks of code; nothing is measured)

Every test below ran on aifoundry2 (Linux, /usr/bin/python3 3.12.3, g++-13 13.3.0, bubblewrap 0.9.0), on Sun 15 Nov 2026 between 14:27 and
14:54 PST (re-run by fix-e194 from the fixed files; kit-e194's first runs were 12:38-13:09 PST), from the files as committed here, each that
runs a host, the runner or a stand-in session inside the sandbox (W/nodev.sh, under the round's slot.sh); every log was made by that run
(section 10 names what earlier runs of the same tests caught, section 11 what the verifier found).

| check | result | log |
|---|---|---|
| **the runner's desk test** (`selftest_run_e194.py`, --dry sessions with `fake_card_e194.py`'s doubles; the doubles' clock 600 MHz at rest and 800 MHz in a burst after a climb): E191's cases on E194's runner with this card's numbers (the stop lines, the die gate at 57 C and a die below 46 C labelled, the cap, the end bound, the gates, SHORT and FAILED RUN, the refusals with `--climb-s` among them, the identity gate both ways I1-I10, the BOUND B1-B2 with card 0's lock held, the sampler's freshness F1-F7, et-who unreadable W1-W4, the early stop Q1-Q5, the dry check's refusals for this box D1), **THE CLOCK RULE** C1-C4 (a pass at 700 MHz after its climb set aside; a second stops the session; a late climb; bursts shorter than the window flagged, never set aside), aifoundry2's own lines C5 (the latch at 80 C), **THE HOST'S LINE** H1-H2 (split by a runtime line in every ledger host, reassembled, recorded), **THE HOLDER RE-READ** T1-T2, and END TO END from a stand-in box tree through COPY-BACK EXACT, THE BOX-TREE GATE, the unchanged reducer (its clock line on every pass, the governor's climb inside its busy window, read by THE CLOCK RULE as E194.md 8.2 and the scorer read it; no other hard line) and the frozen scorer (its clock rule), R2E/R3E and the cut-tail control, BT (the box-tree gate refusing a desk path and a scratch root); fix-e194: H2-H4 (a split by a line no lab box printed, by the line "42" a number-continuing reader would merge into width, by a lone "}": that pass reads 'none', a FAILED RUN, never a wrong value; the other passes PASS), F8 (six sampler lines of other shapes inside pass 1: the reader thread lives on, no restart, no pass flagged, six passes) | **SELFTEST-RUN-E194 75 of 75 PASS** | [`logs/selftest-run-e194.txt`](logs/selftest-run-e194.txt) |
| **the REAL path** (`desk/realpath_e194.py`, `desk/realpath_e194.sh`): run_e194.py WITHOUT --dry under the hostname aifoundry2 (a private UTS namespace) and a private PID namespace, E194's REAL guard, the real `timeout 10`, the real ps, et-who on PATH, stand-in reader (named `ettelem`), hosts, lock and nodes; RP1 the whole path through the box check, the lock, the identity gate (a) and (b), the stop-path test (four lines, the clock rule read), the smoke and six passes, each with THE CLOCK RULE ok at the REGISTERED 1.5 s climb; RP2-RP25 each gate and stop on that path (E191's cases with this card's forms: a second card's config, sampler, holder and host refused; the guard refusing ET_DEVICES=0, =1 and V3_DEVICE=1 and passing unset; fix-e194: the box check refusing a session with ET_DEVICES=0 or V3_DEVICE=1 in the runner's own environment, no patched module); RC1-RC3 THE CLOCK RULE (set aside; a second off-clock pass stops; a late climb); RH1-RH2 THE HOST'S LINE split in the smoke and a pass (fix-e194: RH2's span no lab box printed reads 'none', a FAILED RUN, the raw bytes kept); **RH3 THE REAL BYTES: the smoke's host replays E191's committed smoke stdout from aifoundry1's card verbatim (1a4bc1e3, at its SHA256SUMS sha256, the line split by "Opening device 1"): status PASS read, the span dropped and recorded, the stdout kept byte for byte, six passes**; RT1-RT3 THE HOLDER RE-READ (a stray reader at the first read; a stand-in `ettelem` of ours ending 1.5 s in; a reader that stays: refused); RW1 the wrong box (hostname aifoundry1) | **REALPATH-E194 35 of 35 PASS** | [`logs/realpath-e194.txt`](logs/realpath-e194.txt) |
| **the dry-vs-real audit** (`desk/dryaudit_e194.py`): every line of run_e194.py that reads the dry flag, what the real path does there, and the desk cases that ran it, each PASS in its committed log | **DRY-AUDIT-E194 21 of 21 COVERED** | [`logs/dry-audit-e194.txt`](logs/dry-audit-e194.txt) |
| **THE KERNEL GATE on this box's REAL build** (`desk/realbuild_e194.sh`): build_e194.sh with NO stand-in (this box's /opt/et, riscv gcc "() 15.1.0", real cmake and objcopy, the real pins) in a stand-in tree under the hostname aifoundry2: both programs BUILT through the gate by the '() 15.1.0' pin, the records carrying the gate's line, the box and the ET_DEVICES reading "not a gate" (K1); HARNESS OK with the built kernels (K2); E191's attacks K3-K7 and K10 as expected (aifoundry3's .comment and a debug byte OK by the loadable identity; a .rodata, .text and entry change and five header fields refused); sparse parity's sections, program headers and symbols equal E189's committed records (K8); the pins as built (K9) | **REALBUILD-E194 10 of 10 PASS** | [`logs/realbuild-e194.txt`](logs/realbuild-e194.txt) |
| **THE HOST'S LINE on the REAL bytes** (`desk/parser_e194.py`): E191's committed aifoundry1 smoke stdout (1a4bc1e3): E191's last_json read {} (the defect reproduced), host_json the host's object (PASS, 2,048 of 2,048, one launch), the one span "Opening device 1" dropped (P1); E189's committed smoke and pass lines read whole (P3, P4); this card's 87 committed host stdouts (E190 arm A, ET_DEVICES unset): no runtime line in any (P5); this box's runtime libraries carry no "Opening device" string (P6); **the real ledger host built here, run to its device open in the sandbox with /sys hidden: its head printed, the open failed, no runtime line on its stdout, with ET_DEVICES unset and with ET_DEVICES=0** (P7); a runtime line at every one of 178 token boundaries of a committed host line, two and three at once, a decoy: the object every time (P8); cut lines and spans inside strings: 'none', never a guess (P9); **fix-e194, host_result (the runner's reading):** every committed real host line (E191's split smoke, E189's 7 smoke stdouts and 24 pass files) read against its own command line, and 'none' against another configuration's, 80 of 80 (P10); **a foreign line at every position strictly inside two committed host lines (1,483 positions), eleven kinds (the digit, dot, e and E lines, a lone "}", an unknown word line, "Opening device 0 extra", the known "Opening device 0"): 16,313 insertions, never a different object; the known runtime line read exactly at every position between tokens past the host's key** (P11); a stale object 'none', a '{' that begins a line inside the host's line, two complete lines (P12); the config read split and merged, step 7's `--config-line` (P13) | **PARSER-E194 13 of 13 PASS** | [`logs/parser-e194.txt`](logs/parser-e194.txt) |
| **the identity gate both ways on committed forms** (`desk/identity_e194.py`): this card's committed config reads pass (E190 arm A, both ends); a second card's (E190 arm B, E191's stop record, both ends) refused naming /dev/et1_mgmt and ID 1; a missing node's forms (no block, the guard's refusal, a failed open) and minion_mv 0 or 619 refused; another box's card 0 passes the card test (stated: the box check tells boxes apart); 87 of this card's host blocks right, 87 of a second card's wrong; et-who's and the sampler's forms both ways; only a stray reader of ours reads transient | **IDENTITY-E194 7 of 7 PASS** | [`logs/identity-e194.txt`](logs/identity-e194.txt) |
| **the rest rule** (`rb/selftest_rest_e194.sh`): E190 arm A's committed log on this card at its box path (30 minutes REFUSED, 41 rest 41; its dry session not counted), E194's own form (real, dry, cut, stopped before its first card command, stopped at the identity gate), another tree, a symlinked tree read once, the lab clone, lib.sh's aifoundry2 block trees, energy.sh's form, none; fix-e194: the older claims-v3 run logs (E146's runs/<x>/run.log, E77's run/run.log) by their last write, their dry one not counted (RA11); and **this box's real trees, read-only now: E190 arm A's end, Fri 13 Nov 2026 16:24:57 PST** | **SELFTEST-REST-E194 11 of 11 PASS** | [`logs/selftest-rest-e194.txt`](logs/selftest-rest-e194.txt) |
| **THE QUIET DESK FLAG** (`rb/selftest_quiet_e194.sh`): raise, check and lower by the card lane, never over another lane's flag; every step from the look to the collection refusing (10) with the flag down before any box call, and going past it with the flag up; THE P2 COUNT in a private PID namespace (a ledger_host, sys_emu and session_e194.sh of ours counted; an ettelem that ends read again to 0; a grep, a `bash -c` string and a --dry run not counted) | **SELFTEST-QUIET-E194 6 of 6 PASS** | [`logs/selftest-quiet-e194.txt`](logs/selftest-quiet-e194.txt) |
| **step 10's two readings** (`rb/selftest_wait_e194.py`): the gate-stop pattern, read from s20's own text, against a whole E194 session (dry, and the real path's RP1), every gate-stop sentence of the runner, the real path's gate-stop lines, E189's and E190 arm A's committed real sessions (no hit) and E191's committed stop record (a hit); E194's clock, reassembly and re-read lines read as no gate stop; the BOUND line; the session found by its own script in a private PID namespace | **SELFTEST-WAIT-E194 7 of 7 PASS** | [`logs/selftest-wait-e194.txt`](logs/selftest-wait-e194.txt) |
| **the runbook** (`rb/selftest_rb_e194.sh` under `rb/selftest_rb_e194_ns.sh`: a private PID namespace, a fake ssh and rsync serving a stand-in aifoundry2 whose box tree is a git clone of the scratch repository, the scratch repository with its own upstream; RB_LOCK a scratch COPY of the round's lock file, the file itself never written): A, K, W1-W3, G, N, P1-P4, H1-H4, LK-LK3, S0, S, X, U, T, L1-L3, R0, R, D, RS, IS, QP, LA (the REAL session_e194.sh stopping at its box check), WT1-WT3, fix-e194's WT4-WT5 (runner.rc 1 with no gate line: 16; runner.rc not written: 14), C (the runner's exit status reported), SC0-SC3, C2, Z, listed in its header | **SELFTEST-RB-E194 24 of 24 PASS** | [`logs/selftest-rb-e194.txt`](logs/selftest-rb-e194.txt) |
| the dry listing, every step with stand-ins | **13 steps, 0 exiting non-zero, 0 box calls beyond aifoundry2** (24 calls printed, each to aifoundry2); the runbook's command lines pass `desk/drylisting_check_e194.py` (2 device-opening lines, each after an unset of ET_DEVICES and V3_DEVICE). Its desk calls read "run on the Intel": k6's library's wording (unchanged, as in E191's listing), from when the desk was the Intel; the desk here is aifoundry2 itself | [`logs/dry-listing-e194.txt`](logs/dry-listing-e194.txt) |
| `dmcmd_audit` on the session's files (`preflight_e194.sh`) | **GO, 16 send sites, 0 disallowed, every one a READ**, no allow-list, no exception; the guard's reader resolved to its reviewed variant (`build/ettelem-hpl` = ettelem-dv2) | [`logs/dmcmd-audit-e194.txt`](logs/dmcmd-audit-e194.txt) |
| the quick set (`desk/checks_e194.sh`; fix-e194: the never-run check with both of E191's folders left out, and `never-ran-same`: step 2 leaves out the same folders) | **CHECKS-E194 21 of 21 PASS** | [`logs/checks-e194.txt`](logs/checks-e194.txt) |

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** E194.md 15's and 16's rows as they read them; the stock-take's inventory was not read again for this kit. Newer pieces are cited
   by commit: E194's registration (`0d8e3de0`, local, its subtree `5f98fca0`); E191's kit (`eb1ac923`) and its stop record (`1a4bc1e3`); E190's
   kit, note 1 (`bff31df2`) and note 2 (the `_v3` steps) and its card day (`a6fafba4`: arm A on this card); E189's kit (`b42dc95c`) and data
   (`fa9098c4`); E183's kit note 5 (the desk-path gate on this desk); E192's data note 1 (`4e964246`: step 7 after the rest).
2. **Used** (each unchanged, called or read by path; sha256 in [`SHA256SUMS-e194-kit`](SHA256SUMS-e194-kit) or the lists step 2 pins): E191's kit
   (its runner's, modules', doubles', collector's, runbook's and desk tests' form; THE KERNEL GATE and its pins, made on this box); E190's kit
   and notes (arm A's steps on this card: the box tree, the reader `build/ettelem-hpl/ettelem` at `77a46171...`, ET_DEVICES unset, ssh to
   this box, the quiet desk, step 10 v3's pattern); E189's host check, its frozen lines, plan, stand-in cmake and desk mock; k6's runbook
   library (`rb_common.sh`, v3.1's `rb_run.py` and `nopath_q142s.py`), its guard's firmware-read-of-record rule unchanged; `dmcmd_audit.py` and
   its table; energy.sh's reducer and stub, unchanged. *Check against an earlier measurement of the same quantity:* the rest rule's test reads
   E190 arm A's committed session log at its box path and this box's real trees; the parser test reads the committed host stdouts of three
   boxes; the identity test the committed config and host blocks of two cards; step 10's test the committed real sessions.
3. **Not used:** any card; any E194 datum (none exists); any E189 or E191 measured number for any forecast, band, rule, threshold, K, order,
   plan or cap; the counters arm (dropped, section 5); the host's package counter unless his go allows it; nothing of the private tier.
4. **Tiers:** public pieces only.
5. **Readiness:** this kit gates nothing by itself: a verifier checks it, a readiness critic gates the card, and the reboot gate needs the
   owner's ruling first.

## 1. What changes from E191's kit, item by item

| what | E191's kit (aifoundry1 card 1, from aifoundry2) | here (aifoundry2 card 0, from aifoundry2 itself) |
|---|---|---|
| the card | card 1, ET_DEVICES=1 and V3_DEVICE=1 for every device process; card 1's lock | card 0, the box's only card; **ET_DEVICES and V3_DEVICE UNSET** for every device process (E190 arm A's form: this box's device layer carries no ET_DEVICES, and its guard refused any setting); `/run/lock/etsoc-shire0.lock` |
| the reader | `build/ettelem/ettelem` at `8008f96f...` (card 1's) | `build/ettelem-hpl/ettelem` at `77a46171...` (E136's, E146's, E169's and E190 arm A's on this card), through E194's guard: aifoundry2 only, ET_DEVICES and V3_DEVICE unset only (exit 97 before the device opens: realpath RP8, RW1) |
| the box and its tree | aifoundry1, `~/nekko`, one rsync of the harness | aifoundry2, `~/claude/et-soc1-prototyping` (k6's rb_tree; a git checkout): **step 5 is "the tree"**: it waits for (or pulls, ff-only) the kit commit there, E194's paths clean, HARNESS OK, nothing copied (E190 arm A's step 5) |
| the box calls | ssh to aifoundry1 | ssh to aifoundry2 itself, k6's drivers unchanged (E190 arm A's day reached this box the same way: E190's KIT.md, "reached by ssh to itself"); the dry listing names aifoundry2 alone |
| the identity gate | /dev/et1_mgmt, ID 1, 450 < minion_mv < 510 (card 1 499, card 0 519) | /dev/et0_mgmt, ID 0 alone; minion_mv a number strictly between 450 and 600 (a sanity bound on a one-card box: this card read 519; a failed read 0 and the 800 MHz point refused); every holder or node of another card refused, every form a missing node prints refused (identity test I1-I7) |
| the build gate | the ET_DEVICES reading a refusal on aifoundry1 | the reading **recorded, never a gate** (E190 arm A's build here); the runner's box check needs the record made on aifoundry2 |
| the stop lines | E189's 65 W / 70 C, and the per-sample clock line (600 MHz) | E189's 65 W / 70 C first, **aifoundry2's own kept beside them** (board above 85 W on 3 samples in a row; minshire[0] or the latch minshire[2] at or above 80 C); the per-sample clock line is gone (it would trip in every pass at 800 MHz under load and 600 at rest) |
| the clock | 600 MHz on every sample in a pass | **THE CLOCK RULE, live** (E194.md 11): after each pass, the live samples from its burst's first launch's start + 1.5 s to its last launch's end must read 800 MHz; the first pass off it SET ASIDE, a second stops the session; a window with no live sample flagged; the stop-path test reads the rule on live samples |
| the die gate | 60 C, below 52 C labelled | **57 C**, below 46 C labelled (E194.md 11) |
| the host's line | `last_json`: the last line beginning `{` (E191's stop record: a runtime line split it) | **`host_result`** (fix-e194; `host_json`'s reassembly, verified): the last object with the host's key read from the whole stdout around whole known runtime lines only, no foreign newline inside it, checked against its own command line (E191's kit note 2's checks), else 'none'; the raw stdout kept (`host-stdout.txt`) |
| the holder rule at the start | read once | **re-read with the lock held** while every reason is a stray reader of ours (our live collector's `ettelem temp`), at most 3 times 2 s apart; any other reason refuses at once |
| the quiet desk | none (another box) | **THE QUIET DESK FLAG** (`rb/quiet_e194.sh`, RB_QUIET): raised before the look, lowered after the copy-back; every step 4-11 refuses without it; THE P2 COUNT before the look and in step 9's launch call |
| step 7 | k6's reads, before the rest rule | **the rest rule first, then the reads** (E192's note 1 lesson); a settle (6 s at most) for our live collector before the lock |
| the collection | the scrub, then k6's desk-path gate | **THE BOX-TREE GATE first** (every path under the home in the session's files inside the box tree; no scratch root: E183's note 5 lesson for a desk that is the box), then the scrub and k6's gate |
| the rest rule | aifoundry1's trees, either card | this box's trees (the box tree, ~/nekko, ~/aifoundry, the lab clone), E190 arm A's form among them, lib.sh's aifoundry2 block trees, and (fix-e194) the older claims-v3 run logs by their last write |
| the look and the launch | aifoundry1 booted before E82's firmware read | aifoundry2's rule, k6's unchanged: **booted before E69's firmware read of record (2026-10-27 13:56:26 PDT): CLOSED today** (section 8, item 1) |

## 2. Card-minutes and the cap (registered; unchanged)

About 95 card-minutes (12 + 6 + 50 + 6 + 20 = 94), **cap 110**: no pass starts after 108 card-minutes from the first card command, and the
session's last card command ends by 110 (E189's end bound, unchanged). The counters arm's 6 card-minutes go unused (section 5).

## 3. The box steps (on aifoundry2; the card lane's brief is [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md))

E194 runs alone on aifoundry2's card (the booking key `aifoundry2`), never beside another session of ours there. Run from the lab clone,
each step with this day's `RB_OUT` (outside the repo, E194's own), the one `RB_LOCK`, `RB_QUIET` (the quiet desk flag) and, for step 2,
`RB_GITLOCK`. Exit codes are k6's: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after
30 minutes; 16 a gate says stop; 17 call again.

| box step | file | what |
|---|---|---|
| 0 | (by hand) | the booking; THE LOAD RULE; `check_day2_v2.py tree --pull` under the lab-git lock; E194's anchor lines; THE QUIET HOLD |
| 1, the window | [`rb/s02_window_e194.sh`](rb/s02_window_e194.sh) `<day> <last start> <last end>` | FIRST; today's day only; G+1:30 / G+3:30 rounded up |
| 2, the desk check | [`rb/s03_desk_e194.sh`](rb/s03_desk_e194.sh) (outside the kit list; its sha256 in the anchor lines) | the window; the pull under the lab-git lock; ancestry; the history check; every list at its pins (17; the registration's dated note 1's 1; 11; 3; 10; 55; 165; 17, 6; 86; the kit's); E194.md and E189.md at their bytes; the harness; PLANS SAME; both self-checks; the registration's checks; NEVER RAN with E189's and both of E191's data folders left out (fix-e194); no E194 data in any ref; the preflight; the desk tests' logs |
| Q, the quiet desk | [`rb/quiet_e194.sh`](rb/quiet_e194.sh) `raise <lane>`, `count --wait` | the flag up right before the look; THE P2 COUNT 0 |
| 4, the look, FIRST on the box | [`rb/s05_look_e194.sh`](rb/s05_look_e194.sh) `[--wait]` | the identity by continuity (E69's read: CLOSED today), et-who as counts, ps, our sessions and jobs, the P2 count; FREE only with nothing on the card; our login to RB_OUT |
| 3, the post | none | the owner's standing waiver |
| 5, the tree | [`rb/s07_tree_e194.sh`](rb/s07_tree_e194.sh) `[pull]` | the box read first; the box tree holds the kit commit (ff-only pull), E194's paths clean, HARNESS OK there; nothing copied |
| 6, the build | [`rb/s08_build_e194.sh`](rb/s08_build_e194.sh) `start`, then `wait` while 17 | the detached job a2-build-e194: both programs, the kernels through THE KERNEL GATE, the hosts by behaviour, the ET_DEVICES reading recorded; the records (box aifoundry2), the harness, the preflight and both self-checks read on the box; NO-THIRD-BUILD |
| 7, the reads | [`rb/s09_reads_e194.sh`](rb/s09_reads_e194.sh) | THE REST RULE first; a settle for our live collector; card 0's config through the guard (ET_DEVICES unset, card 0's lock, stderr and stdout kept, its object read by `e194_common.py --config-line`: /dev/et0_mgmt, ID 0, minion_mv between 450 and 600, TDP 65 W / 65 C / 600 MHz); the card free; "no config read came back": one re-run after the look reads FREE again |
| 8, the dry pass | [`rb/s10_dry_e194.sh`](rb/s10_dry_e194.sh) `start`, then `wait` | the runner on the box with its doubles (the clock among them), the identity gate and the dry check in it |
| 9, the session | [`rb/s11_session_e194.sh`](rb/s11_session_e194.sh) `FULL [--rapl-allowed]` | k6's guard (no session of ours, the identity by continuity: CLOSED today), THE REST RULE, today's dry pass and build, THE P2 COUNT, then session_e194.sh detached with ET_DEVICES unset |
| 10, the wait | [`rb/s20_wait_e194.sh`](rb/s20_wait_e194.sh), while 17 | the session by its own script; GATE-STOPPED and BOUND-SEEN (16); each pass's reading and clock in words; THE EARLY STOP ends it gracefully (0); **the runner's exit status** once it has ended (fix-e194): runner.rc not 0 with no gate line, 16 ("the runner exited <rc>"); not written, 14 |
| 11, the collection | [`rb/s22_collect_e194.sh`](rb/s22_collect_e194.sh) | one read-only copy back, COPY-BACK EXACT, THE BOX-TREE GATE, the data directory `docs/reports/data/<day>-e194-blind-day-aifoundry2/`, the reducer (unchanged), the scrub, SHA256SUMS and FILES.txt, k6's desk-path gate, the history check, the runner's exit status reported; then the flag lowered |
| 12, the data commit | (the card lane's) | the README from [`rb/data-readme-form-e194.md`](rb/data-readme-form-e194.md), checked by [`rb/readme_check_e194.py`](rb/readme_check_e194.py), the public-text scan, commit_lab.sh |
| 13, the scorer, after the data commit | [`rb/s24_score_e194.sh`](rb/s24_score_e194.sh) | `score_e194.py` (registered, unchanged) on the committed data; RB_OUT/scores-e194.json; read the words |

## 4. The readings stated here before any E194 datum (each kit mechanics, or a stop or gate made stricter for safety, named so)

- **The card's selection (kit mechanics, E190 arm A's).** ET_DEVICES and V3_DEVICE unset for every device process; the guard refuses any
  setting of either before the device opens, and any box but aifoundry2; the box check refuses a session whose own environment carries
  either (fix-e194: it reads the runner's environment, as this line always said).
- **The identity bounds (a gate made stricter for safety).** /dev/et0_mgmt and device ID 0 alone on every identity line of the start config
  read; minion_mv a number strictly between 450 and 600; et-who's lines of ours on card 0 only with one on /dev/et0_mgmt; the sampler holding
  /dev/et0_mgmt and no other card's node; another login's holder line anywhere refuses the identity read.
- **The holder rule (E191's, for one card; stricter).** Before the first card command and before each pass: another login's line anywhere,
  a line of ours on any other card's node or lock, ours on /dev/et0_ops while no host of ours runs, ours on /dev/et0_mgmt while no sampler of
  ours runs, another user's device process, a device process of ours but the session's own sampler.
- **THE HOLDER RE-READ (kit mechanics).** Before the first card command only, with card 0's lock held: when every reason is a stray reader
  of ours (a device process of ours besides the sampler, or a line of ours on /dev/et0_mgmt), the rule is read again up to 3 times 2 s apart
  and the first card command comes only after a clear read; our live collector reads the card for a moment once a second only while
  `et-who --check` finds nothing held, and the lock is held by then (et-who counts a lock our own script holds). Any other reason refuses at
  once; before a pass the rule is read once, as E191's.
- **THE CLOCK RULE, live (registered, E194.md 11; its reading here, kit mechanics).** lo and hi are the host's own launch_epoch_ms (the first
  launch's start and the last launch's end, as the reducer reads them); the window is [lo + 1.5 s, hi]; only live samples count; a pass off
  it is SET ASIDE with the words "the clock: n of m live samples ... read [...] MHz, not 800", a second such pass stops the session ("a
  second pass off 800 MHz after its climb"); a window with no live sample is flagged ("the clock: no live sample ..."), never set aside; the
  idle samples (600 MHz) are not read. The stop-path test reads the rule on the last 3 s of live samples and fails if it reads none.
- **aifoundry2's stop lines (registered, E194.md 11; kit mechanics).** Board strictly above 85 W on 3 samples in a row (a sample with no
  board reading starts the count again); minshire[0] or the latch minshire[2] at or above 80 C; E189's lines are read first and bind first;
  minshire[2] is never read against 70 C. The stop-path test trips each of the four lines with a test threshold.
- **THE HOST'S LINE (kit mechanics; E191's stop record's lesson; verified by fix-e194).** Every host's and the reader's JSON object is read
  from the whole stdout by `e194_common.host_result`: the LAST object that begins with the host's own key (`{"ledger"`, `{"workload"`,
  `{"tdp_w"`), reassembled by `host_json`'s scanner, whose foreign spans (from a character the grammar cannot take to the end of its line)
  are dropped and recorded in run.json / smoke.json `host_line`. It reads 'none' ({}: a FAILED RUN or a failed gate, never a guess) when a
  later object with the host's key cannot be read (never an earlier one in its place), when a raw newline lies inside the object read (a
  foreign line merged into a value: a line that begins with a digit, '.', 'e' or 'E' after a number), when a dropped span is not a whole
  known runtime line ("Opening device <n>", aifoundry1's), when a span falls inside a string or the object never closes, and when the
  object fails its command line's checks (E191's kit note 2's `ledger_checks` and `spp_checks`, ported unchanged: the head fields equal the
  command's, the tail typed, one wall time and two span ends per launch, sparse parity's reps_requested the command's). The raw stdout is
  kept as host-stdout.txt; host-raw.json and host.json hold the object as read. On this box's runtime no runtime line is expected (parser
  test P5-P7).
- **THE RUNNER'S EXIT STATUS (kit mechanics, fix-e194).** session_e194.sh writes runner.rc after the runner exits; step 10 waits for it (at
  most 10 s) once the session has ended and stops with 16 when it is not 0 and no gate line was written (a crash after the gate: its
  finally block writes "session end" and the manifest all the same), 14 when it is not written; step 11 reports it and the README names it.
- **The rest rule's older forms (kit mechanics, fix-e194).** This card's older claims-v3 run logs (build/eNNN/runs/<x>/run.log,
  build/eNNN/run/run.log) are read by their last write beside the kits' session logs.
- **THE QUIET DESK FLAG (registered, E194.md 13; its form here, kit mechanics).** A file outside the repo (RB_QUIET) holding "e194 <lane>
  <time>"; raised before the look and lowered after the copy-back by the card lane; never overwritten or removed when another lane's; every
  step from the look to the collection refuses without it; THE P2 COUNT (device-named processes and session or queue scripts of ours on
  this box) before the look and in step 9's own launch call, read again up to 5 times 2 s apart.
- **THE BOX-TREE GATE (a gate made stricter for safety).** Before the collector writes anything: every place this account's home is written
  in the session's files begins a path inside the box tree (read lexically) or is the home itself, and no file holds a session scratch root;
  else nothing is written (exit 3).
- **Step 7 after the rest (kit mechanics).** The same rest rule step 9 reads, before step 7's config read.
- **The reboot gate (k6's, unchanged; stated).** k6's `rb_guard_text` and the look refuse a launch on aifoundry2 booted after E69's firmware
  read of record; the kit neither loosens nor works around it (section 8, item 1).
- **Everything else is E191's kit section 4, unchanged:** the 30 s bound (the queue stops, nothing killed, the lock kept while that host
  lives), the sampler's freshness and a live sample, the per-pass sampler flag, et-who unreadable, the early stop and an early stop at the
  gate, our device processes by comm and executable, the box check reading the kernels, the kernel gate and its identity's second form,
  ours_live by each process's own script, the pass's reading in words, FILES.txt, the README form and check, the cap and the end bound, one
  sampler, the build's re-run (at most two starts a Pacific day), the package counter only with `--rapl-allowed`.

## 5. The counters arm: DROPPED

E194.md 7: E189's kit dropped it (its KIT.md section 5), so E194 does not run it; the session logs "the counters arm: DROPPED" and its 6
card-minutes go unused; its frozen expectations stay in `forecast-e194.json`, unused. A registered option taken as registered.

## 6. Files (all new, under tools/claims-v3/e194/)

| file | what | builds on |
|---|---|---|
| `e194_common.py` | the card (ET_DEVICES unset, shire0 lock, the reader's pin, the config line), the commands, the smoke, THE ADAPTER, the reading in words, THE STOP LINES (E189's and aifoundry2's), THE CLOCK RULE (`clock_pass`), THE HOST'S LINE (`host_json`) | E191's `e191_common.py` |
| `e194_ident.py` | the identity gate (a) and (b), the sampler's nodes, the holder rule's lines (with the stray-reader reading), the host watch | E191's `e191_ident.py` |
| `run_e194.py`, `session_e194.sh` | the session runner and its detached wrapper | E191's runner |
| `ettelem_guard_e194.sh` | the only way to the reader: config and sample, aifoundry2 and ET_DEVICES / V3_DEVICE unset only | E190's guard (arm A) |
| `build_e194.sh`, `etdevices_e194.sh` | the box build (THE KERNEL GATE) and its ET_DEVICES reading (recorded) | E191's build |
| `check_e194.py`, `harness-e194.json` | the 42 files the box runs or reads; PLANS SAME; THE KERNEL GATE and its pins (E191's) | E191's harness |
| `preflight_e194.sh` | dmcmd_audit on the session's files | E191's preflight |
| `fake_card_e194.py` | the doubles: card 0's identity and a second card's and a missing node's forms; the clock with its climb; split host lines; a committed stdout replayed verbatim (RH3); the stray reader | E191's doubles |
| `collect_e194.py` | COPY-BACK EXACT, THE BOX-TREE GATE, the data directory, the reducer (unchanged), the scrub, SHA256SUMS, FILES.txt | E191's collector; E183's note 5 |
| `selftest_run_e194.py` | the runner's desk test | E191's |
| `desk/realpath_e194.py`, `desk/realpath_e194.sh` | the real-path desk test and its namespaces | E191's |
| `desk/dryaudit_e194.py` | the dry-vs-real audit | E191's |
| `desk/realbuild_e194.sh` | THE KERNEL GATE on this box's real build | E191's |
| `desk/parser_e194.py` | THE HOST'S LINE on the committed real bytes and this box's runtime | CONTEXT section 116's lesson |
| `desk/identity_e194.py` | the identity gate both ways on committed forms | the task's lesson |
| `desk/drylisting_check_e194.py`, `desk/checks_e194.sh` | the runbook's command lines; the quick set | E191's |
| `rb/rb_e194.sh` | what every step sources (k6's library unchanged; E194's ours_live and P2 count, the registration by content, the window, the lab-git lock, the quiet desk) | E191's `rb_e191.sh` |
| `rb/s02`, `rb/s03` (step 2, outside the list), `rb/s05`, `rb/s07` (the tree), `rb/s08`, `rb/s09`, `rb/s10`, `rb/s11`, `rb/s20`, `rb/s22`, `rb/s24`, `rb/quiet_e194.sh` | the runbook's steps and THE QUIET DESK FLAG | E191's steps; E190 arm A's step 5 |
| `rb/rest_rule_e194.sh`, `rb/check_history_e194.py` | the rest rule and the history check | E191's |
| `rb/list_steps_e194.sh` | the dry listing | E191's |
| `rb/selftest_rb_e194.sh`, `rb/selftest_rb_e194_ns.sh`, `rb/selftest_rest_e194.sh`, `rb/selftest_wait_e194.py`, `rb/selftest_quiet_e194.sh`, `rb/fake_cmake_e194.sh` | the runbook's desk tests and the stand-in cmake | E191's |
| `rb/data-readme-form-e194.md`, `rb/readme_check_e194.py` | the data README's form and its check | E191's |
| `CARD-LANE-BRIEF.md` | the card lane's brief | E191's |
| `logs/` | every check above | |
| `SHA256SUMS-e194-kit` | every kit file but itself and step 2, the logs, and the unchanged files the kit calls | |

## 7. Device commands

`dmcmd_audit.py` on the session's file set (`preflight_e194.sh`): **GO, 16 send sites, 0 disallowed, every one a READ**, with no allow-list
and no exception: `ettelem config` (TDP level, temperature thresholds, power state, the ASIC's frequencies and voltage) and `ettelem sample`
(module power, SP statistics, temperature, the ASIC's and the module's voltage, frequencies), through E194's guard, which refuses
`--reset-ms` and every other word, any box but aifoundry2 and any ET_DEVICES or V3_DEVICE setting, before the device opens. The 16 sites are
the guard's 11 (config 5, sample 6) and the runner's recorded config command line (5); the reader resolves to its reviewed variant
(`build/ettelem-hpl` = ettelem-dv2). The two hosts open card 0's ops node only. No set, no reset, no statistics reset, no firmware query of
any kind, no power cycle.

## 8. What the desk cannot show (for the verifier and the readiness critic)

1. **THE REBOOT GATE IS CLOSED (blocking).** aifoundry2 booted 2026-11-13 16:53:28 PST, after E69's firmware read of record (2026-10-27
   13:56:26 PDT). k6's guard (`rb_guard_text`, the go checklist's "fault 12") refuses every launch on it (IDENTITY-STOP, step 9's 16; the
   runbook test's IS) and the look reads 16 (LK3). This box's firmware build is carried by uptime continuity only; the firmware-revisions
   query is forbidden (it writes the PMIC's firmware-management register); the config read's identity block carries the node, the device ID
   and the TDP but no firmware build (E190 arm A's committed config-start.err), and this boot's kernel log carries the driver's probe and the
   PCI device but no firmware build (a desk read, Sun 15 Nov 2026). No kit file loosens the gate: the owner's ruling (a dated amendment
   before step 4) is needed before E194's session.
2. **The two programs' first build on this box's card day** is step 6 there; the real-build test showed the gate passes this box's toolchain
   and that the hosts' behaviour reads OK in the sandbox; the hosts have never opened this card (E190 arm A ran rgm136's host here).
3. **The ledger host's and sparse parity's host's identity block on this card** has not been read: rgm136's host printed `/dev/et0_ops`, ID 0
   in every committed process here (identity test I5); a host whose block cannot be read fails the smoke gate (a safe failure).
4. **The runner has run only with its doubles and stand-ins** (the desk, and step 8 on the day): the live reader, card 0's lock, et-who and
   the real hosts meet it first in the session; our live collector's read in flight has been met only by stand-ins (realpath RT1-RT3).
5. **THE CLOCK RULE has met only the doubles' clock.** E190 arm A's committed telemetry (the registration's climb read: 0.014-1.325 s) is
   the evidence for the 1.5 s allowance; whether a governor step inside a burst occurs on these loads at a 57 C gate is what the session reads.
6. **Other users' device processes:** a positive count cannot be made on the desk without a second login (the dry audit states it).
7. **The collection** has run on stand-in sessions (the runbook test's gate-stopped one; the doubles' passes from a stand-in box tree), not on
   a card's.
8. **Card time waits on his go** (`CARD-LANE-BRIEF.md`) and on the reboot gate's ruling, never beside another session of ours on this card.
9. **No relaunch rule** (verify-e194's information 10; unchanged here): E194.md 11.1 forbids a re-run around a gate stop, so a gate stop
   before any pass datum ends the day (our live collector's single-open moment at the start config read, or a smoke kit defect). The
   precedents for a dated relaunch rule are E191's A1 and E192's G4; the owner's reboot-gate ruling could carry one.
10. **A third E191 data folder** (fix-e194): step 2 leaves out E191's two registered folders by their exact paths; a third, if ever
    registered, is read and step 2 refuses (16, NAMED BEFORE) until a dated note names it (E194.md.dated-note-1.md 3).

## 9. Labels

Every figure quoted from E194.md and its files (the forecasts, K, the order, the caps, the stops, the clock rule, the die gate) is
**registered**. The desk tests' results are **desk checks of code**, not measurements; the end-to-end joules and the scorer's words come
from the doubles (energy_stub.py's alt card). The committed records the kit reads (the session logs at their box paths, the identity blocks,
the hosts' stdout bytes, this box's boot time and kernel log) are **desk reads of committed records** or of this box's files. Nothing here is
measured, blind or held out, and no E194 datum exists.

## 10. What the desk tests caught in this lane, each fixed before this commit (stated, not hidden)

Every log above is from the last run of its test, made after the fixes below and from the files as committed. None of them changed
run_e194.py, the guard, the modules' gates or any registered number.

| test | what its first run showed | the fix |
|---|---|---|
| real path RC1 | the clock double read 600 MHz between a burst's planned end and the host's end mark, so a pass read off the clock | the double's burst holds 800 MHz to the host's end (`END_GRACE_S` 0.05 s; injections keyed to bursts) |
| real path RT2 | a finished stand-in reader left a zombie that ps still counted | the test reaps its stand-in in a thread |
| runner R6 | a 58 C die held 1 s did not hold the gate long enough to skip a pass | held 6 s from the first pass's first launch |
| runner E2E, R2E, R3E | the unchanged reducer wrote "minion clock in busy samples: [600, 800] MHz (the governor moved it)" and ok false on every 800 MHz pass (the climb lies inside its busy window); the test required ok true | the test reads the reducer as `score_e194.py` and E194.md 8.2 do (that line read by THE CLOCK RULE, every other hard line standing); CARD-LANE-BRIEF.md step 11 tells the card lane to expect the line |
| runner BT, real path | the logs printed the desk's scratch root | masked as `<scratch>`; BT's scratch-root text names no real uid |
| runbook P1, P2-P4, S | step 2 read the runbook test's own log while that run was still writing it; the build case counted k6's doubled output lines | the stand-in kit carries that log's stand-in line; distinct lines counted |
| step 10's N1 | its step-9 stand-in was run under E191's file name, so it never started and the case passed vacuously | run under E194's step 9 name; the case now also fails if any stand-in fails to start |
| real path (new case RH3) | CONTEXT section 116's lesson asks for the REAL bytes through the real path, not only stand-in JSON | RH3 replays E191's committed split stdout through run_e194.py without --dry |
| identity I2, I4; parser P5; the dry listing's check | test inputs (499 mV lies inside this card's sanity band; E189 kept no config stderr; P5's 'check' records; the dry job's own grep words) | the expectations and inputs corrected |

## 11. fix-e194: E194's verifier's findings, answered before the land (Sun 15 Nov 2026, Q183, lane `fix-e194`)

`verify-e194` (13:17-13:58 PST) read the registration and this kit as they stood in their local commits (`0d8e3de0`, `e86fa432`): one
medium finding, two minor, five nits and three for information. Each finding but the three for information is answered here, before any
E194 datum, as kit mechanics or a gate made stricter for safety. **Nothing here changes a forecast, a band, a rule, a threshold, K, the
order, the plan, the card time, the cap, a registered stop line or the scorer**, and the registration's 18 files are unchanged byte for
byte. The kit's files are new files under `tools/claims-v3/e194/`, as before; the logs above are the fixed files' own.

| finding | what the verifier found | the fix (file) | its desk test |
|---|---|---|---|
| 1, medium | E191's second session (E191.md A1) writes to `...-aifoundry1-c1-s2/`, which step 2's never-run command did not leave out: once that data landed, step 2 would read NAMED BEFORE and refuse (16) on E194's day; and E194.md's sentences on E191 would no longer describe the record if that data landed before the registration | step 2 and the quick set leave out both of E191's folders (`rb/s03_desk_e194.sh`, `desk/checks_e194.sh`: E194.md 17 item 7's "E191's left out" read as both, in the registration's dated note 1); the quick set checks that the two commands leave out the same folders; step 2 pins the note's list (1 entry); the registration's commit body names the note | CHECKS-E194 `never-ran`, `never-ran-same`; the lane's stand-in check (a copy of E189's sparse-parity host.json under the `-s2` name: NAMED BEFORE without the new exclude, NEVER RAN with it); step 2 run for real at GitHub main with both commits local |
| 2, minor | `host_json` merged a line beginning with a digit, '.', 'e' or 'E' into the head's last number (width 32 read as 3242), read an all-digit line as 'whole line', closed the object early on a lone '}' line, and read an earlier object when the last could not be read; nothing checked the object against its command line | `e194_common.host_result` (section 4's THE HOST'S LINE), used for the smoke, every pass and the config read (`run_e194.py`); `ledger_checks`, `spp_checks`, `parse_size` ported unchanged from `e191_common_v2.py` (2d0fe517); the doubles print the real host's head fields, and split it where aifoundry1's runtime did (`fake_card_e194.py`) | PARSER-E194 P10 (every committed real host line read against its own command line; against another configuration's, 'none'), P11 (a foreign line at every position inside two committed host lines, eleven kinds: never a different object), P12 (the stale object), P13 (the config read); the runner's H2-H4; the real path's RH2; the common module's self-check |
| 3, minor | a runner exception after the gate read as an ordinary end: the finally block writes "session end" and the manifest, step 10 exited 0 | step 10 reads runner.rc once the session has ended: not 0 with no gate line, 16; not written in 10 s, 14 (`rb/s20_wait_e194.sh`); step 11 reports it (`rb/s22_collect_e194.sh`); the README form's "What ran" names it and its checker requires it (`rb/data-readme-form-e194.md`, `rb/readme_check_e194.py`) | the runbook's WT4 (runner.rc 1: 16), WT5 (none: 14), WT2 (0: 0), C (reported); the README checker's self-test |
| 4, nit | the rest rule did not read this card's older claims-v3 run logs (`runs/<x>/run.log`, `run/run.log`) | read by their last write (`rb/rest_rule_e194.sh`) | the rest test's RA11; RA10 still reads E190 arm A's end on this box's real trees |
| 5, nit | the box check's ET_DEVICES clause could never fire: it read the environment `device_env()` had already cleaned | it reads the runner's own environment (`run_e194.py`) | the real path's RP8: ET_DEVICES=0 and V3_DEVICE=1 in the runner's environment, no patched module: 16, nothing started |
| 6, nit | step 7 took the config line as the last line beginning '{' | step 7 keeps the read's stdout on the box and reads it with `e194_common.py --config-line` (host_result) (`rb/s09_reads_e194.sh`) | PARSER-E194 P13; the runbook's R and R0 |
| 7, nit | a sampler line whose temp_c or minshire was not an object or a list raised in the reader thread, which then ended silently | `die_of`, `latch_of`, `sample_live` and THE STOP LINES read any shape as no reading (`e194_common.py`); the reader catches, counts and names any error, and a t_ms that is not a number is not live (`run_e194.py`; queue.json `sampler_lines_unreadable`) | the runner's F8 (six lines of other shapes inside pass 1: no restart, no flag, six passes); the common module's self-check |
| 8, nit | the brief named RB_QUIET only as "the round's quiet-desk flag file" | `RB_QUIET=W/locks/quiet-desk-aifoundry2` named (`CARD-LANE-BRIEF.md`) | (text) |
| 9-11, information | the reboot gate closed; no relaunch rule; today's idle die below the forecast band | unchanged: section 8, items 1 and 9; the forecast is registered | |

## Compute

On aifoundry2 through the round's local slots (`slot.sh`, nice 10), one job at a time, each that runs a host, the runner, a stand-in session
or a stand-in box inside the sandbox (W/nodev.sh; the real-path, the runbook, the quiet-desk and step 10's tests in private PID namespaces,
the real-path and real-build tests under a private hostname): the runner's test (about 20 minutes, the registered idles in its end-to-end
cases), the real-path test (about 5 minutes), the real-build test (real cmake builds of both programs against /opt/et, about a minute), the
runbook test (real g++-13 builds of both hosts), the rest rule's, quiet desk's and step 10's tests, the parser and identity tests, the dry
listing, the quick set. No other box, no card.

SPDX-License-Identifier: Apache-2.0
