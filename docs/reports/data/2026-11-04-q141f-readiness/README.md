# The card half's readiness: Q141(f)'s verdict, card plan and go checklist (dated report, Wed 4 Nov 2026, week 45)

*Written by Q141(r), the records round, from the result of Q141(f), the readiness critic (about 12:20–13:10 PST on Wed 4 Nov
2026), and from Q141(k)'s runbook. New files only: nothing registered, frozen or measured changes, and no card result is in it.
Q141(f) worked at the desk only: no card claimed, no device command sent, no ssh to a lab box, no Discord, no Modal and no archive,
and it committed, deployed and posted nothing. It answers Q140's final critic's `card_half` list and its `desk_next` 1–8 (is each
of E163–E169 ready to claim?), under the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) items 6 (a power model across kinds),
8 and 9 (heat over minutes) and 1 (where a large GEMM falls). Scrubbed for this public repository: the session's own files and
locks are named by what they are, not by their paths.*

**What it does to predicting power and heat.** It changes no frozen prediction, band, rule, stop or verdict, and every hash list
passes as the critic re-hashed it. It makes no new blind test scorable by itself. It confirms, by re-derivation rather than by the
lanes' word, that seven blind tests of power and heat can be scored once the card half runs: rank 1 (M9 against M6 on pool 7's 48
priority-1 kinds) on both 600 MHz cards, with the 4.5 s heat, rank 4's paired-anchor card scale, the card term 0.9616 and rank 14's
C-checked re-runs (E163, E164); rank 2, M9's aifoundry2 part in governed bursts, recomputed per tile from the session's anchors and
die starts (E165); rank 3, heat over minutes from the bits on both kinds of card (E166, E167); G4's first blind test (E168); and
the 8 MB index's step by a registered rule (E169). **Before**, the blind record is Q139's: a new kind's 600 MHz power to 0.24–0.32 W
rms per card; the 4.5 s rise to 0.10–0.18 °C; a 10-minute plateau to 0.37 °C rms on aifoundry3; governed bursts to 6.7 MHz and
1.4 W; a governed large GEMM to 8.7 MHz, 1.9 W and 1.0 °C. **After:** what E163–E169 measure. The registered forecasts stand: with
M1 forecast NOT RESOLVED, E163-RANK1 and E164-RANK1 read FAIL, the likeliest misses in classes S, E and L; rank 2's governed-clock
lines hold in 35% of draws. The plan's correction below changes when those numbers arrive, not what they test.

## The verdict: all seven ready to claim

Only the box steps remain, after the owner's go and fresh lab approvals: the approvals, the day's post, the tree sync, the
preflights, the firmware and et-who reads, a dry pass on the box, and the smoke.

| Run | Card | Registered (PST, Wed 4 Nov) | What it tests | Card-minutes (cap) | Stops |
|---|---|---|---|---|---|
| E163 | aifoundry3 card 0, 600 MHz pinned; TDP 0 / 65 °C as read, nothing set | `64dff136` 09:33:22 (E163.md alone, first), `442474d5` 09:38:32 (the freeze), `1c47ce62` 09:52:17 (the kit), `f13e0b39` 10:49:52 (A1 and the README's dated note) | rank 1 as E163-RANK1: M1 = M9 − M6 by paired bootstrap, U1, B1/B2, C1 at least 42 of 48, P1–P3, H1–H4 under M7's heat law, R1/R2, M2 and M3; rank 4's reference half; rank 14's re-runs (K14/K14' in pass, KE/KE' on E151's six in blocks 16350–16352); Q141(t)'s 27-point arm, reported only | FULL about 56–59 (70: 4,200 s with a 60 s reserve; three kinds passes and the E151 block); TWO about 31–33 (38); SHORT about 25–27 (30) | 65 W / 70 °C; E151's block 45 W / 68 °C |
| E164 | aifoundry1 card 1, 600 MHz; its lock etsoc-shire1, never card 0, one session of ours on the box | `4286f0a8` 09:18:57 (E164.md, rank 7's pick), `f4e75c95` 09:41:51 (the freeze, the scorer, E157 reproduced), `ce10e301` 10:05:44 (the kit), `45aeda12` 11:41:49 (E164-A1, `launch_e164_a1.sh`, `collect_e164_a1.sh`, the scrub) | rank 1 as E164-RANK1 (new in A1-3, E163-RANK1's conjunction exactly); X1/X2 (the card term 0.9616 with E163's reduction); RK4 (rank 4's paired-anchor scale); K7C/K7D/K7W/K7/K7' on 8 pool-6 tiles; PCa; P1–P3, B1/B2, C1, U1, H1–H4, R1/R2 | about 57.6 (65): four 96-run passes | 66 W / 72 °C |
| E165 | aifoundry2 card 0 under its own governor (65 W / 65 °C as read, BL2 0.22.0) | `3ef06839` 09:36:11 (E165.md, the per-tile primary, the note beside pool 7's predictions), `a5c56d17` 09:37:49 (the scorer, E160 self-test), `e3c4eafc` 09:43:55 (the kit, A1), `fe6f4862` 10:43:24 (the domain screen, 57 of 57), `a509ff8b` 10:54:04 (A2: the bounded collector) | rank 2: M9's aifoundry2 part recomputed per tile through `predict_m9_a2.burst` from the session's zeros anchors and each tile's measured die starts; the governed clock at most 4 MHz rms, its mean within ±2 MHz; the governed and pinned board means within ±0.5 W, the pinned rms at most 1.0 W; each resolved better than M7 as frozen (95% paired bootstrap, 20,000 draws, seed 1651) | about 36 (40, in a 45-minute slot); subset, passes 1–2: 22.7 + about 1 (25) | board above 85 W on 3 live samples; die 76 °C; the 82 W admission |
| E166 | aifoundry3 card 0 | `2b450e66` 09:16:36 (E166.md, SL's rule), `f830b9e2` 09:31:08 (the scorers, self-tests), `c75bc460` 09:41:09 (the kit, 30 pinned files), `ae39563c` 11:24:33 (dated note 2) | rank 3: RK3-a on at least 3 of 4 holds (K_S 14.78, K_Q 6.10, K_L 3.53, K_O's window 11.16 °C at a 51.2 °C room); RK3-c (does E154's 3.1–4.6% gain deficit repeat); G_A and SL on the 25-minute K_OL; the G0 room gate (53.0 °C); X1 | about 74.4 (76); no subset | Q138(t)'s |
| E167 | aifoundry2 card 0 under its own governor | `7ba987b3` 09:16:50 (E167.md), `f830b9e2` 09:31:08 (the scorer), `4f4e7620` 09:59:53 (the kit, 43 pinned files), `48994187` 11:24:19 (X2, the latch check, the bounded collector) | RK3-b on G1Q in the 800 MHz regime (within 1.0 °C, its trajectory at most 1.0 °C rms); RK3-c in X2's form (NOT SCORED when G1Q is gated or excluded); G2Q's trip plateau and trip clock (685.6 MHz primary); E2, reported, with E165's anchors | 35–39 (40); about 66–75 minutes of wall time | above 80 W on 3 samples; 72 °C; a static admission |
| E168 | aifoundry2 card 0 under its own governor | Q140(q)'s `49575094` / `e39d06da` / `1bfaa4e4`; A2 (E168) `226249e1` 09:18:35; the kit `a0310012` 09:38:43; the note `d86cafa6` 09:40:30; the fix `983e9499` 10:31:55 | G4 blind under A7: within 15 MHz / 2 W / 1 °C on at least 8 of 9 holds, the int8 increments within ±1.328 W, G3 as frozen and E136's law beside; A2's start dependence (cold minus warm int8 zeros window board: G4 +1.334 W, G3 +0.641, none 0, an absolute-die law −1.01 to −1.15 W) | about 42 (35 without A2; 53 if every cold gate waits its 360 s); cap 58, binding in flight, at most 63 in all in a 66-minute slot | board above 85 W on 3; 76 °C; 82 W |
| E169 | aifoundry2 card 0 under its own governor | A2 (E169) `217c94a2` 09:22:23; the scorer `18aaca80` 09:33:28; the kit `6a3929ec` 09:46:17; the note `2bf8f092` 09:47:26; the fix `5c9a62f1` 10:44:17 (note 2) | the step T800(P)/T800(N) at P1/N1 and P3/N3 against SM's +37.06% / +30.97% and ISO's and STRICT's 0.0%; zones ±3 points, the 95% t interval floored at σ0 0.336%; seven verdicts, a negative step UNRESOLVED; B7 expected to FAIL; a zeros burst's power reported | about 11–16 (20; at most 25 in a slot of about 45 minutes) | board above 60 W on 3; 76 °C; 82 W |

Every registration is the first commit in its directory and names its frozen hashes, and every Q141 commit descends from all 14 of
Q140's frozen commits: pool 7 `75802201` and `3c9bb2ba`; M9 `1f244140` and `8dfafae3`; M9's aifoundry2 part `5b98bd5c`, `245caffe`
and `5c98c0c5`; the heat replicates `11174d20`, `c9aaf179`, `a4fe976d` and `ac06c9be`; G4 and the stride term `49575094`,
`e39d06da` and `1bfaa4e4`. Every device command the seven kits send is READ in the firmware table it is audited under, and none
sends the statistics reset.

### What the critic checked itself

- **Hashes.** `blind7/SHA256SUMS` 91 of 91; `frozen-sha256-e168.json` 9 of 9; `frozen-sha256-e168-scorer.txt` 18 of 18;
  `predict_q140e.py`'s FROZEN list 26 of 26. Each run's own list too: E163's harness 138 plus 4 box-only; E164's 103 plus 4; E165's
  7, 3, 8, 5 and 4; E166's 27 plus 3, and its fix list 10; E167's 40 plus 3, and its X2 list 15; E169's 54 and its tiles' 3. No two
  kits that share a box pin different bytes for one path.
- **Git.** 33 Q141 lab commits, `0830f65b` at 09:11:50 to `c31e7ae3` at 12:16:56 PST, in a linear history, each descending from
  all 14 frozen commits; all 346 path entries are additions and none modifies a file; no E163–E169 data existed in any ref or on
  the desk's disk, and the public main was `c31e7ae3`.
- **Six scorer self-tests**, re-run on the parents' committed data, each reproducing its committed output: E168's byte for byte;
  E169's and its kit's byte for byte; E167's X2 JSON byte for byte; E166's parent check JSON byte for byte; E163's parent, 9,853
  fields with 0 differing; Q141(t)'s A1 byte for byte. And the own checks of the fix passes no verifier had read: E165's path
  check; E169's notes; E164's notes, 53 of 53 without `--freeze`; E163's hash part.
- **Two dry passes on the desk**, each equal to its committed log: E163 (DRY-INTEL PASS, 45 s) and E164 (rc 0, 2 min 39 s).
- **Every kit's command audit** (`dmcmd_audit.py`), re-run as documented: GO at 32 / 32 / 19 / 38 / 35 / 19 / 19 send sites for
  E163 / E164 / E165 / E166 / E167 / E168 / E169. All 12 distinct commands sent are READ in the table each is audited under
  (GET_ASIC_PVT_SAMPLES under E144's table, as for E154). The only WRITE is the conditional statistics-reset forward at
  `lib.sh:154`, excepted for E163, E164 and E166 for reasons confirmed in the code: those kits never pass it.

## The card plan

Three cards in parallel, serial on each; aifoundry1's card 0 is not in this plan (see "After the critic" below), there is one
session of ours on aifoundry1, and no box dry pass runs during a session on its own box. Times are minutes from his go, T, with the
approvals done.

| When | aifoundry3 card 0 | aifoundry1 card 1 | aifoundry2 card 0 |
|---|---|---|---|
| T+0–10 | the desk checks, a probe of each box, the look-first reads, and the day's one post rewritten once with three clauses ("using aifoundry3 for 3 h", "using aifoundry1 card 1 for 1.5 h", "using aifoundry2 for 4 h", each with its "until ~HH:MM PST") | | |
| from T+10 | T+10–20 the sync (E163 and E166 in one rsync), the preflights, the firmware and et-who reads and both dry passes; **E166** T+20–95 (74.4 card-minutes of 76, no subset; G0 needs the room at or under 53.0 °C); **E163** FULL T+97–156 (56–59 of 70); release about T+158 | T+10–15 the sync and the check on the box; **E164** T+20–78 (57.6 of 65, four 96-run passes); release about T+80 | T+10–17 the tree and the preflights; T+17–27 the four box dry passes, two at a time (E165 stopped after its smoke and stop tests, E167, E168, E169); **E165** T+28–65 (about 36 of 40, in a 45-minute slot); the latch check; **E167** T+68–140 (35–39 of 40 card-minutes, 66–75 minutes of wall time); **E168** T+142–190 (about 42, 53 at every cold gate's bound; cap 58, at most 63 in a 66-minute slot); **E169** T+193–208 (11–16, cap 20, at most 25); release about T+210–230 |
| card-minutes | 131–134 (caps 146) | about 58 (cap 65) | 123–148 (caps 173) |

**In all**, about 312–340 card-minutes (caps 384). **The last release comes about 3.5–4 h after his go, not 3–3.5 h** as Q140's
final critic planned (F5 below). Collection and scoring follow on the desk machine, about 1–1.5 h at `nice -n 10` with at most 2
jobs; E164 is collected after E163. **The window it needs:** the full plan needs the last end at least about 4 h 15 min after his
go and the last start at least 3 h 30 min after it. **Subsets if the day is short:** (a) about 1.5 h: E163 (FULL, or TWO) on
aifoundry3 instead of E166, plus E164 and E165, which gives rank 1 on both 600 MHz cards, rank 4's pair and rank 2; (b) about
2.75 h: everything but E168 and E169; (c) about 3.5–4 h: all seven. E166 has no subset; if G0 refuses it, E163 runs first and E166
needs at least 40 minutes of rest after it. Nothing in the plan sets a governor, TDP, threshold or clock, sends a PMIC command
beyond the voltage reads, or writes anything; every aifoundry2 stop is at most 85 W on live samples and is tested in each smoke.

## The go checklist

| # | Step | Who | Minutes |
|---|---|---|---|
| 1 | Approve the Tailscale checks for aifoundry1, aifoundry2 and aifoundry3, one link per box. The session first probes each box (a 15 s hard-killed `ssh -o BatchMode=yes -o ConnectTimeout=10 <box> true`) and hands him every link it prints. Each approval lasts about 12 h. | him | 3–5 |
| 2 | Say go, with the window: the last start of a card session and the last end. The full plan needs the last end at least about 4 h 15 min after his go; subset (b) about 3 h, subset (a) about 1 h 45 min. | him | 1 |
| 3 | The desk check: `git pull --ff-only` in the lab clone; HEAD descends from `c31e7ae3`; `git status --short tools/claims-v3` prints nothing. Re-run the four hash lists: blind7 91, `frozen-sha256-e168.json` 9, the scorer list 18, `predict_q140e` 26. | session | 2 |
| 4 | From here on, every remote call goes in a script file: a 15 s hard-killed probe first, then the call under a timeout (60 s for reads, 600 s for copies). If a login link prints, kill the call, append `<HH:MM:SS> <host> needs a check` to the session's Tailscale lock file, and retry every 3 min for up to 45 min. Detached runs keep going meanwhile. | session | 0 (a rule) |
| 5 | Look first on all three boxes, read-only: et-who, who, uptime; on aifoundry1, `box/look_e164.sh` (card 1's own lines, and nothing of ours on card 0). A holder of a device node or lock blocks: wait in bounded polls of at most 30 min in all, else skip that card. An idle login does not block. | session | 3 |
| 6 | The day's one post in `#community-lab`, under the session's Discord lock: find today's post (`delete_msg.mjs --plan --days 1`); if there is none, `post.mjs`, else `edit_replace.mjs` with `EXPECT_TEXT`. The text is the clauses still held, plus "using aifoundry3 for 3 h, until ~HH:MM PST [doc]; using aifoundry1 card 1 for 1.5 h, until ~HH:MM PST [doc]; using aifoundry2 for 4 h, until ~HH:MM PST [doc]". Read it back; record the message id and the text before and after. If a run will overrun by more than 15 min, rewrite its clause's "for N h, until". | session | 4 |
| 7 | aifoundry3, the sync: one `rsync -a -c -R --exclude __pycache__ -e 'ssh -o BatchMode=yes -o ConnectTimeout=10'` of E163's step-4 paths (`e163/`, `kinds/blind7/`, `kinds/blind5/`, `kinds/e130/`, `e152/`, `e151/`, `ccheck/`, `dmcmd_audit.py`, `dmcmd_table.json`) and `tools/claims-v3/e166/` to aifoundry3's binaries tree. | session | 2 |
| 8 | aifoundry3, the preflight: blind7 `sha256sum -c` (91); `check_e163.py` HARNESS OK 142; `preflight_e163.sh` GO; `e163_common.py --verify`; `sha256sum -c frozen-e166.sha256` (30); `preflight_e166.sh` GO. If any binary differs, stop that run: a dated amendment comes first. | session | 3 |
| 9 | aifoundry3, the firmware and et-who reads: `et-lab-manifest`, kept (the non-public thermal build since 7 Oct); `ettelem config` through the guard (TDP 0 W, 65 °C, 600 MHz); et-who clean. | session | 2 |
| 10 | aifoundry3, the dry passes: the `V3_DRY` `session_e166.sh` (no `E166_DESK`); `V3_DRY` `block_e163.sh` 16310, 16350 and 16301 `--smoke`; the start gate's exit 8. | session | 3 |
| 11 | aifoundry3, E166: launch it detached with `E166_T0`, `E166_LATEST_START` and `E166_END_GATE` (at least T0 + 76 min). The smoke and its five stop tests run first. If G0 exits 7 (the room above 53.0 °C), launch E163 instead. | session | 1, then about 75 |
| 12 | aifoundry1 card 1: `box/sync_e164.sh`; `box/check_box_e164.sh` (the harness with the binaries, 107; preflight GO; tiles; blind7 91; the dry pass 16410, 16401 and 16402; et-who); `uptime -s` before 31 Oct 13:45:24 PDT. | session | 4 |
| 13 | aifoundry1 card 1, E164: `ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '<the round's last end less 10 min, YYYY-MM-DD HH:MM PST>'" < tools/claims-v3/e164/box/launch_e164_a1.sh`. Never `box/launch_e164.sh`. Its refusals (exits 2, 3, 4, 9) open nothing. The stop-path test and the smoke run first. | session | 1, then about 58 |
| 14 | aifoundry2, the tree and the preflights: `git pull --ff-only`; `git merge-base --is-ancestor c31e7ae3 HEAD`; `git status --porcelain -- tools/claims-v3` empty. `e165_common.py` (61); blind7 91; the binaries `eae32a15` / `990807f4` / `77a46171`; `run_e167.sh check` and `sha256sum -c frozen-e167-x2.sha256`; E168's binaries `76475508` / `aace138c` / `77a46171` and `run_e168.py --list`; E169's `shasum -c` 54 and 3, `score_e169.py check` and `selftest_kit_e169.py`; `et-lab-manifest` (BL2 0.22.0); et-who, who, uptime. | session | 5 |
| 15 | aifoundry2, the four dry passes, all before E165's session and never during one, two at a time: E165's queue `--dry` (stopped after the smoke and the stop tests, about 1 min); `run_e167.sh dry` (about 7); E168's into `build/e168/dry` (about 3); E169's step 4 into `build/e169/dry` with its own slot file (about 5). | session | 9 (16 if serial) |
| 16 | aifoundry2, E165: the slot file (45 min) and the detached queue, `--cap 40`. The smoke, the DMA rule and both stop-path tests run first; the queue halts with QUEUE-HALT if any fails. | session | 1, then about 37 |
| 17 | aifoundry2, E167, after E165's `queue_end`: `latch_check_e167.py --history` on the box's history file for the UTC day (GO under 72 °C; on NO-GO, skip E167 and go on to E168). `run_e167.sh config start`; `run_e167.sh go <smoke-not-before> <smoke-latest> <no-start-after> <cutoff>` (HH:MM); the GO marker. | session | 3, then about 66–75 of wall time |
| 18 | aifoundry2, E168: the slot (66 min) and the detached queue, `--runs build/e168/runs`. The smoke and both stop tests run first; its first cold gate waits at most 360 s for 46 °C. | session | 2, then about 42–53 |
| 19 | aifoundry2, E169: `build/e169/runs` must not exist; then the slot (about 45 min) and the queue, `--runs build/e169/runs`. | session | 2, then about 11–16 |
| 20 | Wait in bounded remote calls (a timeout of 540 s inside a script, repeated), never a long local sleep. Read each smoke gate's verdict before counting a session as started. | session | ongoing |
| 21 | Releases: rewrite the day's post at each card's last end. aifoundry1 at about T+80 and aifoundry3 at about T+158 each drop their clause; aifoundry2 at about T+210–230 appends " — released" if its clause is the last one held, every word kept. | session | 2 each |
| 22 | Collect and score at the desk (it needs the desk's lab clone), at `nice -n 10` with at most 2 jobs, bounded copies only. E163: `collect_e163.sh` with `arm27-aifoundry3.json`. E166: `collect_e166.sh`. E164, after E163: `collect_e164_a1.sh` with `E164_S_RECOUNT` and E163's files. E165: `collect_e165_bounded.sh`, then write its `results.json` `score.anchors` to a file. E167: `collect_e167_bounded.sh`, then `score_e167_x2.py --e165-anchors`. E168: the copy, gzip and scrub, then `reduce_e168.py --anchors`. E169: `build/e169/runs` only, then `score_e169.py s[1-6]`. Then `score_rank4.py --a3 --c1 --pair` E163/E164 and `score_s7arm_a1.py --a3 --c1`. Before any data commit, scrub every `logs/` of other logins (`scrub_etwho_e164.py --check`, or read by eye) and run the public-text scan. | session | 60–90 |

E164's collect line in full, with Q141(t)'s card-1 arm (F2): `PY=/usr/bin/python3 PYS=<python 3.12+> E164_DATE=<day>
E164_S_RECOUNT=docs/reports/data/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry1c1.json nice -n 10 bash
tools/claims-v3/e164/collect_e164_a1.sh build/e164-raw <E163's e163.json> <its C-excluded tiles> <E163's scored.json>`. Without
`E164_S_RECOUNT` the card-1 arm is skipped silently.

## The critic's faults, F1–F9

None blocks a blind score. Each is answered by the checklist above, by Q141(k)'s runbook or by these records; no kit file changed.

| | Kind | Runs | The fault | How it is answered |
|---|---|---|---|---|
| F1 | minor, operational | E163, E164, E166, E168, E169 | The box steps' remote calls from the desk carry BatchMode and ConnectTimeout but no overall bound and no 15 s probe, so a Tailscale check link would hold the call, where the session's rule is to kill it at once. Only E165's `collect_e165_bounded.sh`, E167's `collect_e167_bounded.sh` and `collect_e166.sh`'s timeouts of 300 s and 120 s are bounded. Evidence: `e163/README.md.dated-note.md` steps 4, 10 and 11; `e164/box/sync_e164.sh:9-10` and `box/pull_e164.sh:10-12`; `e166/README.md` box step 2 (no command at all); `e168/README.md` step 8 and `e169/README.md` step 7 (copies in prose). | the checklist wraps every remote call in a probe and a timeout (step 4), and Q141(k)'s runbook does so in code |
| F2 | minor, a reported arm silently lost | E164, Q141(t) | E164's corrected collect command (its `README.md.dated-note.md` section 2, step 7) does not set `E164_S_RECOUNT`, and `collect_e164.sh:89` passes `--s-recount` only when that variable names an existing file, so Q141(t)'s card-1 arm (`arm27-aifoundry1c1.json`) would be skipped without an error. Q141(t)'s route names the variable but calls `collect_e164.sh`, not `collect_e164_a1.sh`. | the checklist's collect line sets it, and the full command is above |
| F3 | minor, privacy | E163, E166 | `session_e163.sh:50,75` and `session_e166.sh:35` append raw et-who output to `build/e16x/session.log`, and `collect_e163.sh:113` and `collect_e166.sh:15` copy those logs into the data directory bound for this repository unscrubbed (the class of E164's verifier's fault 4, fixed for E164 only, by `scrub_etwho_e164.py`). On these one-card boxes a holder at the start stops the session, so the exposure is a holder at the end. E168's README already asks for a scrub of end reasons; the aifoundry2 queues log counts only. | before each data commit, the scrub's `--check` (or a read of `logs/` by eye) and the public-text scan |
| F4 | minor, a missing command | E166 | Its README's box step 2 says only "Sync the committed tools/claims-v3/e166/ (and the unchanged reused files)". By `git log`, the 22 frozen-e166 files outside `e166/` last changed before E154 ran (the newest `4946a992`, Tue 3 Nov 05:46), and the 9 paths E166 shares with E163's harness carry identical pins, so one rsync of `tools/claims-v3/e166/` with E163's step-4 paths leaves `sha256sum -c frozen-e166.sha256` passing (27 plus 3 box-only). | that rsync, checklist step 7 |
| F5 | minor, the plan | Q140's final critic's card plan, the lanes' order notes | aifoundry2's wall time was undercounted. E167 holds the card about 66–75 minutes, not its 35–39 card-minutes: E98's two 15-minute no-launch rests (`e167/README.md` lines 70-73; E161 was claimed at 16:24:16 and released about 17:30 PST). And the four aifoundry2 box dry passes must precede E165's session and never run during one: E165 about 1 or 13 min, E167 about 7, E168 about 3, E169 about 5 (`e165/README.md` step 6; `e168/README.md` step 6; `e169/README.md.dated-note.md` step 4). So the last release comes about 3.5–4 h after his go, not 3–3.5 h. | the card plan above; these records quote it |
| F6 | nit, a collector's exit status | E163, E166 | `collect_e163.sh` exits 0 when `score_e163.py` fails (it prints "score_e163 failed", and `results.md` is absent); `collect_e166.sh` prints "score rc=" and also exits 0. The class of E165's A2-8, but both select passes by exact name (`p163[1-5][0-9]` with `block.json` ok, and `p16620`), so E165's `s1.out` trap does not apply. | the operator reads "results.md written" or "score rc=0" |
| F7 | nit, a carried hazard | E164 | `README.md` step 5 still names `box/launch_e164.sh`, which would run 0 passes; only the dated note points to `box/launch_e164_a1.sh`, and the broken script stays in the tree. | the checklist (step 13) and the records name `launch_e164_a1.sh` and its usage line |
| F8 | nit, disclosure | E167 | The session's brief lists aifoundry2's 82 W run-time admission; E167 keeps E161's static desk admission (M8's 95% peaks 53.33 / 68.15 W; X2's note says so), and its live stops (72 °C; over 80 W on 3 samples) are stricter than 76 °C / 85 W. | no change needed; the records say "a static admission" |
| F9 | a correction of two lanes' open issues | Q141(h), Q141(o) | They say E165 must still emit its zeros anchors for E167's E2 arm and E168's `--anchors` arm. It already does: `score_e165.py` puts them in `results.json` at `score.anchors`, in `session_delta`'s form `{type: [{burst_w, burst_mhz, die_start}]}`, and the session delta at `score.anchor_delta` (`score_e165.py:518, 526-527`); E167's loader takes either form. | the step is writing that object to a file (checklist step 22), not a new tool |

The critic also read, and re-ran where they end in a few minutes, the fix passes no verifier had read (`f13e0b39`, `45aeda12`,
`a509ff8b`, `48994187`, `ae39563c`, `983e9499`, `5c9a62f1` and `c31e7ae3`; `983e9499`'s floor and cap tests it only read): each
reproduced its committed output, and it found no fault beyond F1–F9. E164-RANK1, added by amendment before any data, is
E163-RANK1's conjunction exactly.

## Q141(k), the bounded runbook (after the critic, its `desk_next` 1)

[`tools/claims-v3/q141k-runbook/`](../../../../tools/claims-v3/q141k-runbook/README.md): one script per box step of the go
checklist above, with its exact commands, taken from the kits' dated notes and never from their superseded README lines
(`launch_e164_a1.sh`; E164's collect line with `E164_S_RECOUNT`; aifoundry3's one rsync for E163 and E166; E165's `score.anchors`
written to a file for E167's E2 arm and E168's `--anchors` arm; bounded copies of E168's and E169's runs). Each script first runs
a 15 s hard-killed probe, then makes its call under a timeout (60 s for reads, 600 s for copies; a detached launch returns at
once); a printed login link kills the call, is logged as `<HH:MM:SS> <host> needs a check` to the lock file it is given, and exits
with its own code; nothing prompts, and every command is logged with its exit status. The scripts call only the kits' own audited
scripts, so no new device command appears.

- **v1**, `e962227a` (14:08:36 PST). The card half has run its steps since 14:18 PST on all three boxes, and E170's box kit
  (`57e1c6c4`) sources its `rb_common.sh`. Its verifier read it as holding with five faults and four nits. Read as corrected:
  `dmcmd_audit` reads GO only with E128's guard scanned beside the runbook (one call site, `s09_a3_reads.sh:21`, a READ); there were
  four desk-test runs, not five; and its README's line "each launch refuses otherwise" was not true for E163.
- **v2**, `16771f36` (15:34:42 PST), new files beside v1, which stays byte for byte because live lanes run it
  ([`v2/README.md`](../../../../tools/claims-v3/q141k-runbook/v2/README.md),
  [the dated note](../../../../tools/claims-v3/q141k-runbook/README.md.dated-note.md)): (1) s13 reads the box for the runbook's own
  dry job, a session of ours and s12's clean check before E164's launch; (2) a lost dry job exits 14, not 17 on every call; (3) a
  plain E166 retry over an earlier smoke is refused; (4) E167's collection probes all three boxes, and the lock line names the box
  the link came from; (5) aifoundry2's BL2 0.22.0 is gated by host-boot continuity from E69's firmware read of 27 Oct 13:56:26 PDT,
  else exit 16; and the nits: s09 waits for a session of ours, E163's plan must end by the last end, and box state counts only when
  written that day. Its checks: the desk test 324 of 324, with v1 run beside v2 to reproduce each fault; the dry listing 50 of 50
  steps with no ssh; `dmcmd_audit` GO with E128's guard (11 send sites, all the guard's, every command READ); the public-text scan
  clean; its step 3 passing when run for real.
- **For the card day:** E167's collection should run with v2's `s22_collect.sh e167` (fault 4); every other remaining step may stay
  on v1.

## After the critic (dated, Wed 4 Nov 2026)

- **His go came at about 13:55 PST:** *"go, feel free to use all four cards because they're not being used right now."* Then
  *"There was a problem with card 0, but that's been fixed."* So aifoundry1's card 0, left out since E84's over-power alarm, is back
  in use by his word; E170, pool 7 on that card, was registered and kitted beside the plan by Q141(w) (`b5ca3e78`, `574dc5b5`,
  `57e1c6c4`), to run after E164 has ended, never beside it.
- **The window** the session set and told him: no card session starts after 18:15 PST, and every run ends by 19:00 PST. The full
  plan fits it.
- **The card half started at 14:11 PST** (the claim, 14:11:27): the day's one post in `#community-lab`, message
  `1567662592850399304`, holds aifoundry3 for 3 h (until about 17:11 PST), aifoundry1, both cards, for 3 h (until about 17:11) and
  aifoundry2 for 4.25 h (until about 18:26). Its results follow, in the runs' own data READMEs and the records of the card half's
  integration; none is in this report.

## Sources

- Q141(f)'s result: its verdict, `card_half`, `card_plan`, `go_checklist`, `faults_found`, `records_for_r`, `desk_next` and
  `prediction_effect`, transcribed here and scrubbed; its own logs and scripts stayed in the session's scratch.
- Each run's registration and kit, named in the verdict's table by commit; each kit's README and its dated notes in
  `tools/claims-v3/e163/` to `tools/claims-v3/e169/`.
- Q141(k): `e962227a` and `16771f36`, and `tools/claims-v3/q141k-runbook/v2/logs/` (the desk test, the dry listing, the audits and
  the public-text scan).
- The records: [`02-requests.md`](../../../findings/02-requests.md), Q141; [`03-experiments.md`](../../../findings/03-experiments.md),
  "Q141's lanes, beside the register"; [`04-artifacts.md`](../../../findings/04-artifacts.md), Q141;
  [`05-claims.md`](../../../findings/05-claims.md), "Q141".
