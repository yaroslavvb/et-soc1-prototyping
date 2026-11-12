# E185: M11's session 3 on aifoundry3 card 0, heat over minutes, blind - the six holds complete and every stop clear; E185-BEST NOT SEPARATED (F, Rl), the board gain WORSE than the frozen chain, the rail chain BETTER than the board gain, E185-C NOT RESOLVED on F; nothing changes in M11

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**items 9 and 8, heat over minutes and the heat path between sessions**. E185 is M11's session 3 on aifoundry3 card 0, as
[`E185.md`](../../../../tools/claims-v3/e185/E185.md) registers it, with its dated amendment
[A1](../../../../tools/claims-v3/e185/E185.md.dated-note-A1.md) and its dated note
[M1](../../../../tools/claims-v3/e185/E185.md.dated-note-M1.md), under [M11's registration](../../../../tools/claims-v3/m11/REGISTRATION.md)
and its amendments A1-A10. [`KIT.md`](../../../../tools/claims-v3/e185/KIT.md) with its dated notes 1-4 and the day's
[brief](../../../../tools/claims-v3/e185/CARD-LANE-BRIEF.md) with its dated notes 1-2 kit and run it.*

*Day 2 ran on Thu 12 Nov 2026 (week 46), on the owner's go of Wed 11 Nov 2026 at about 21:24 PST, in his words: "approvals went through,
continue now". That was a fresh network approval for aifoundry3; one lasts about 12 h, so it lapses about 09:20 PST Thu 12 Nov. No approval
came on Tue 10 Nov, the day the plan first named, so day 2 did not run then. No brief or kit names that day, and nothing registered changed.
E185's step 1 wrote the window at 03:15:28 PST: day 2026-11-12, no session starts after 07:45 PST, and every run ends by 08:30 PST. It is one
window for E185 and then E183. The card was aifoundry3 card 0 at 600 MHz pinned: TDP 0 W, threshold 65 °C, max_power, 600 MHz and 523 mV,
read through E128's guard at step 9 and at the session's start and end. Nothing was set.*

*Registered before any E185 datum, one ancestry chain (git's times, PST): M11's A6 `95c75047` (Thu 5 Nov 23:11:50), A7 `65a93fbb` (Fri 6 Nov
00:28:50), A8 `80b92990` (01:40:25), A9 `cd5bed77` (03:22:30), A10 `5e708747` (Sat 7 Nov 20:25:30); E185's registration `98fe28b7`
(20:40:51), its kit `460c352f` (21:17:55), A1 `df4e6763` (22:27:33), kit note 1 `ad2ed873` (22:45:02); note M1 `2f6a4440` (Sun 8 Nov
05:14:15); kit note 2 and the brief `408a9a9e` (06:48:51); kit note 3 with the brief's note 1 `1e74546a` (08:37:53); kit note 4 with the
brief's note 2 `e8e9f4e1` (12:13:55), the commit the day-2 go names. The lab clone stood at `52e3f68a` (Mon 9 Nov 19:18:10) all day.*

*The runbook ran as kit note 4 orders it, never a v1 step 2, 10 or 14 and never step 2 v4, v3 or v2 alone.
- The claim lane ran the day-2 check v2 by hand (`check_day2_v2.py tree --pull`, 03:15:22-03:15:26, rc 0 at `52e3f68a`), step 1, and step 2
  v5 (03:15:28-03:15:40, rc 0, with note M1's list "21 of 21 at its pinned bytes"). It then ran the probe, and the look read FREE at 03:15:56
  (no holder, no device process of any user; idle logins only). The day's one post followed at 03:16:09.
- The card lane ran step 5, the sync (03:21:26-03:21:27, rc 0). Step 6, the preflight on the box (03:21:35-03:21:36), read the box list 30 of 30
  OK, the device-command audit GO with 38 send sites and 0 disallowed, and the runner's tile list with no problem.
- Step 7, the reads (03:21:39-03:21:40), found TDP 0 W, 65 °C and 600 MHz, and et-who clean. Step 8, the dry job, ran 03:21:44-03:22:25 and
  ended rc 0.
- Step 9, the host's start window, ran 03:22:48-03:24:49; then step 10 launched the first try.
- Load_guard read calm before each step 2.*

## Two tries: the first refused at its start gate, the later try ran

| | the first try | the later try (the session collected here) |
|---|---|---|
| launch (step 10, `rb/s11_a3_launch_e185_v2.sh`) | 03:24:55-03:25:01 PST, no flag. The rest gate read 5,822 minutes since E184 arm S's session end (Sun 8 Nov 02:22:24 PST); see the note below | 04:32:43-04:32:49 PST with `--later-try`, the kit's path after a start-gate refusal ([kit note 1](../../../../tools/claims-v3/e185/KIT.md.dated-note-1.md), "Major 1"). The rest gate read **61 minutes** since the first try's session end, so A7-4's hour held and `--under-an-hour` was not used. Step 9, the host's start window, ran again first (04:29:07-04:31:08), so the collector could pick one within its 30 minutes |
| T0 (session start) | 03:24:56 PST (`T1794482696`) | **04:32:44 PST** (`T1794486764`) |
| A6-1, the floor F0 (the 34-sensor mean over the smoke's first 3 s; at most 53.9 °C) | 51.77 °C (30 samples; firmware 51.0 °C, board 23.53 W): the smoke ran | **51.973 °C** (30 samples; firmware 51.0 °C, board 23.70 W): the smoke ran |
| the smoke and its six stop tests | GO (03:24:57-03:26:23) | **GO** (04:32:46-04:34:11) |
| G0-A6 with A8-4, the start gate after R0 | R0's room **52.794 °C**, which passes the 53.9 °C line. The residue, room less F0, was **1.024 °C**; less A8's frozen 0.414 °C that is **+0.610 °C**, over the 0.50 °C line. **REFUSED** at 03:31:27: no hold ran | R0's room **52.098 °C**; the residue **0.125 °C**; less 0.414 °C, **−0.289 °C**: **PASSED** at 04:39:16, and the design ran |
| session end | 03:31:32 PST (6.6 card-minutes from T0, no hold) | **06:15:21 PST** (102.6 card-minutes from T0) |

- **The first try is not a failed prediction, and it is not E185 data.**
  - A8-4's line refuses "a card that warms during R0 by more than 0.50 °C beyond the smoke's predicted heat"
    ([A8-4](../../../../tools/claims-v3/m11/REGISTRATION.md.dated-note-A8.md)).
  - A1-5 predicted E185's own smoke residue at about 0.53 °C, with a chance of about 1.4 × 10⁻⁴ that the line refuses a settled card. The
    first try read 1.024 °C. The later try, an hour on, read 0.125 °C.
  - Why the card warmed during that R0 (03:26:27-03:31:27 PST) is not known. The lane read the first try only through the runbook's own wait
    lines, and it made no read of the box outside the runbook.
  - The first try's files stay on aifoundry3, read-only, as the kit says. Step 10 moved its smoke aside as `e185-smoke/p18501.try1`, and the
    later block moved its measured pass aside as `e185/p18520.attempt-1794486851`; step 14 names both ("left on the box", below). Its T0
    directory `build/e185/T1794482696/` stays there too. A records round that wants them copies them by a read-only rsync of its own.
- **The rest gate did not see E186.** Step 10 v2's rest rule reads `build/e17x` and `e18[0-4]/session.log`, `build/e18x/session-*.log` and
  `build/e185/T*/session.log`. E186's session log is T0-named under `build/e186/T<T0>/session.log` (E186's `rb/s11_a3_session_e186.sh`), so
  E186's session on this card was invisible to it. That session ended Mon 9 Nov 2026 14:19:08 PST (its data README).
  - This is *post hoc* and changed nothing today: the true rest before the first try was about 3,666 minutes.
  - It is the same class as kit note 1's minor fault 6, which concerned E183's log. A later kit's rest rule should read E186's form.
- **The day's one post** is `#community-lab` message 1570396782918238239. The claim sent it at 03:16:09 PST: "using aifoundry3 for 2.5 h, until
  ~05:46 PST".
  - At 04:33:14 PST it was rewritten to "using aifoundry3 for 2.5 h, until ~07:02 PST": the same line, with the until re-estimated from the
    later try's launch, because the run would overrun its estimate by more than 15 minutes.
  - The rewrite was made under the post's lock with EXPECT_TEXT, after a dry run, and read back equal.
  - E183 follows on the same card, so the post keeps E185's clause until E183's look (the brief's section 4).

## The answer

Blind: A10 (`5e708747`) and E185's registration (`98fe28b7`) are ancestors of HEAD, and both precede the measured pass's first launch
record (`scored-m11.json` › `E185` › `precedence`, `blind` true). Every reading below is on **A10's reading** (the chain over the smoke and
the measured pass), with the frozen two-pass gains G_B 1.02678 and G_Rl 1.19380, as registered. The stated reading's arm is set beside each
rule, labelled. It is the one-pass reading with the one-pass gains (1.02350, 1.18978), `E185` › `one_pass_reported`, and decides nothing
(A1-1). τ = σ_c / √n = 0.0884 / √6 = **0.0361 °C**; six holds were scored by all three arms.

| rule | reading (A10's, registered) | verdict | the stated reading's arm, reported (A1-1) |
|---|---|---|---|
| **E185-RF**, the rail chain against the frozen chain | D = rms(e_Rl) − rms(e_F) = 0.2158 − 0.2146 = **+0.0013 °C** | **NOT RESOLVED** | D −0.0217 (0.2010 − 0.2226): NOT RESOLVED |
| **E185-BF**, the board gain against the frozen chain | D = 0.2578 − 0.2146 = **+0.0432 °C** (≥ +τ) | **WORSE** | D +0.0627 (0.2853 − 0.2226): WORSE |
| **E185-RB**, the rail chain against the board gain | D = 0.2158 − 0.2578 = **−0.0420 °C** (≤ −τ) | **BETTER** | D −0.0843 (0.2010 − 0.2853): BETTER |
| **E185-BEST** | rms F **0.2146**, B **0.2578**, Rl **0.2158 °C** | **NOT SEPARATED (F, Rl)** | F 0.2226, B 0.2853, Rl 0.2010: NOT SEPARATED (F, Rl) |
| **E185-C on F**, the frozen chain's cool-down shape: **its line governs** (A1-2) | n_c 4 (H_E, L1, L2, H_E2); d̄ **+0.0063 °C**, 95% t interval **[−0.2387, +0.2513]** | **NOT RESOLVED**: nothing follows | d̄ +0.0053 [−0.2370, +0.2477]: NOT RESOLVED |
| E185-C on B, reported, decides nothing (A1-2) | d̄ +0.2503 [−0.0014, +0.5021]; A1-2's offset d_B − d_F at the frozen forecasts: +0.320 (H_E, H_E2), +0.241 (L1, L2) | NOT RESOLVED | d̄ +0.2195 [−0.0287, +0.4677] |
| E185-C on Rl, reported, decides nothing (A1-2) | d̄ +0.1756 [−0.1303, +0.4816]; A1-2's offset d_Rl − d_F: −0.071 (H_E), +0.403 (L1), +0.408 (L2), −0.056 (H_E2) | NOT RESOLVED | d̄ +0.1434 [−0.1631, +0.4500] |

**What M11 carries on aifoundry3** (E185.md section 6's table, one way only): E185-BEST reads NOT SEPARATED, so **nothing changes**. The
frozen chain stays M11's primary, and B and Rl stay reported arms for the next session. E185-C on F reads NOT RESOLVED, so nothing follows
from the cool-down. The board gain reads WORSE than the frozen chain (E185-BF) on this first blind session; B never entered, so the rule
that would make an entered arm a reported arm does not apply.

**Each hold** (A10's reading; e = R − P, °C; the 34-sensor die's plateau mean over [b − 300 s, b) less its mean over the 120 s before the
anchor end; the cool-down window [b + 120 s, b + 360 s); every hold complete by E166's X1 and scored, with its rail readings):

| hold | item | R | e_F | e_B | e_Rl | cool-down miss F / B / Rl | rail share |
|---|---|---|---|---|---|---|---|
| H_E | fp32.randn (the warm pattern) | 11.1224 | +0.0632 | −0.2329 | +0.0652 | +0.2720 / +0.2259 / +0.2245 | 0.8325 |
| L1 | int8.full | 10.5009 | +0.2638 | −0.0103 | −0.1998 | +0.2741 / +0.2360 / +0.1953 | 0.8749 |
| L2 | int8.full | 10.4266 | +0.1962 | −0.0777 | −0.2651 | +0.0330 / −0.0029 / −0.0464 | 0.8743 |
| H_E2 | fp32.randn (the warm pattern) | 10.6302 | −0.2075 | −0.4977 | −0.1807 | −0.2382 / −0.2762 / −0.2513 | 0.8330 |
| S | int8.neg_ones | 4.1902 | +0.0301 | −0.0813 | −0.3121 | (120 s rest) | 0.9041 |
| S2 | int8.neg_ones | 2.4615 | +0.3466 | +0.2900 | +0.1869 | (120 s rest) | 0.9058 |

Each arm's mean miss by kind, reported (°C): H, F −0.0721, B −0.3653, Rl −0.0578; L, F +0.2300, B −0.0440, Rl −0.2325; S, F +0.1884, B
+0.1044, Rl −0.0626. *Post hoc, deciding nothing:* the board gain over-predicts both duty-cycled fp32 holds (−0.23 and −0.50 °C), as it did
E181's H_E. The rail chain over-predicts L1, L2 and S (−0.20, −0.27 and −0.31 °C) and reads both fp32 holds within 0.19 °C. The frozen chain
runs warm on L1, L2 and S2 (+0.26, +0.20 and +0.35 °C) and reads H_E and S within 0.07 °C.

**M11's own registered readings**, at k = 2 (E181 and E185, on A10's reading; M11's decision code counts H_E, L1, S and L2 of E185, A1-4):

| reading | the scorer's figures | verdict |
|---|---|---|
| **HM-LG** at df (2, 5), n 9 | F_slope 0.1805, F_level 1.4339, against F's point 5.7861; the null F 2.5646 against 5.1922 | **NOT SEPARATED**; A1-4: "nothing: NOT SEPARATED", the ×1.032 arm retired |
| **HM-AG** | F_level 0.6035, F_gain 0.1978, F_both 0.4788, against F's points 6.6079 and 5.7861 | (a reading of the two sessions' agreement) |
| **HM-E144** on H_E | \|e(H_E)\| / R = 0.0632 / 11.1224 = **0.57%**, inside 1.5% in both sessions | **REPEATS**; the same ratio on H_E2, reported: **1.95%** |
| **HM-HE** | e(H_E) inside the 95% prediction interval (t at 2 df, 4.303) in both sessions | does not depart (N2 false) |
| **HM-CAL** and **HM-CAL-I8**, pooled | the scorer prints BETTER for both under `A10` › `readings` | **E181's alone, never E185's** (A1-3): E185 has no Z, and its L1 and L2 run before S, so neither pair reads E185 (`per_session` › `S3:p18520`: "its pair was not run first"); E181's own registered HM-CAL verdict stays NOT RESOLVED |
| **what M11 carries** | "nothing: the chain unscaled stays M11's primary" | nothing enters |
| **FL5(c)**, reported, never a gate | the rests after the holds (15,529 samples at degrees 52-59): **0.3220 W/°C** against FL1's **0.3139**, **+0.0081**; on the 34 codes −0.0009; the degrees 52-58 +0.0113 | **PASS** (within ±0.02 W/°C) |
| **A9's arm**, reported | Δe(H_E) **+0.221 °C** (the chain over the smoke and the measured pass against the measured pass alone); L1, S and L2 0.000 °C; the gap between the passes 2.564 s | never a verdict |
| **A6-5, the host's own sensors**, reported | the NVMe composite 36.85 → 37.85 °C (whole kelvins), the coretemp 2-9 mean 31.865 → 31.625 °C, at step 9's window (04:29:08-04:31:08) and step 12's (06:15:34-06:17:34) | never a gate |
| **the check of C** | `CCHECK-DONE … 6206 launches, PASS 6206, ROUNDING 0, UNMODELLED 0, FAIL 0, all_pass True` (fp32 1,082, int8 5,124); `COUNT-OK p18520: 6134 checked launches in 476 processes`; `COUNT-OK p18501: 72 checked launches in 9 processes` | 6,206 of 6,206 computed correctly |

Sources: [`scored-m11.json`](scored-m11.json) and [`scored-m11.md`](scored-m11.md) (M11's scorer v5, run by step 14 v2 after every gate),
[`scored-m11-lines.jsonl`](scored-m11-lines.jsonl), the measured pass's [`aifoundry3/e185/p18520/marks.jsonl`](aifoundry3/e185/p18520/marks.jsonl)
(kinds `room`, `start_gate`, `hold`, `rest`), the smoke's [`aifoundry3/e185-smoke/p18501/marks.jsonl`](aifoundry3/e185-smoke/p18501/marks.jsonl)
(kinds `floor`, `stoptest`), [`ccheck/ccheck-all.json`](ccheck/ccheck-all.json) and [`ccheck/ccheck.txt`](ccheck/ccheck.txt),
[`logs/host-start.out`](logs/host-start.out) and [`logs/host-end.out`](logs/host-end.out).

## The readings, labelled

Everything in this table was measured on the card in this session, except the rows marked **post hoc**: those were read afterwards and
decide nothing.

| what | reading | source |
|---|---|---|
| card-minutes | **102.6** of the 105 cap, from the config read at the session's start (04:32:45 PST) to the one at its end (06:15:21 PST). The first try added 6.6 card-minutes with no hold (03:24:56-03:31:32), so the card carried E185 for 109.2 minutes today | `logs/config-session-start.json.time`, `logs/config-session-end.json.time`, `logs/session.log` |
| the room and the pattern | R0's room **52.098 °C** (firmware 51.0 °C), above A6-3's 51.5 °C: H_E and H_E2 ran the **warm pattern** (2.60 s every 7.98 s) | `aifoundry3/e185/p18520/marks.jsonl` (kind `room`, `he_seconds` 2.6) |
| the timeline of pass 18520 | R0 04:34:16-04:39:16 (300 s); H_E 04:39:16-04:49:16 (75 launches); R1 8 min; L1 04:57:16-05:07:16 (82); R2 8 min; L2 05:15:16-05:25:16 (81); R3 8 min; H_E2 05:33:16-05:43:16 (75); R4 8 min; S 05:51:16-06:01:16 (81); R5 2 min; S2 06:03:16-06:13:16 (82); R6 2 min, to 06:15:16. Each hold ended on time (`why_end` "time"); none was gated or stopped; 476 launches, every one rc 0 | `aifoundry3/e185/p18520/marks.jsonl`, `run.log` |
| the six stop tests (the smoke) | the gate line at 1 °C: 0 launches; the hold die, hold 34-sensor-mean and hold board lines: each hold ended with 0 launches; the in-launch board line at 28.37 W ended the launch in flight (board read 50.52 W); the session line at 1 °C ended the block with exit 6 (die 54 °C, 34-sensor mean 54.50 °C, board 24.76 W) | `logs/smoke-gate.json` (GO, no problems); `aifoundry3/e185-smoke/p18501/marks.jsonl` (kind `stoptest`, all_pass true) |
| peaks, pass 18520 (board W / firmware °C / 34-sensor mean °C) | H_E **55.26 / 65 / 65.736**; L1 37.18 / 62 / 63.251; L2 37.27 / 62 / 63.256; H_E2 55.08 / 64 / 65.244; S 29.58 / 56 / 56.555; S2 29.64 / 56 / 56.895. The stops are no launch at a firmware reading of 70 °C or more, and a hold and the pass end at a firmware 70 °C, a 34-sensor mean of 72 °C or a board of 65 W. None was reached: the closest were the firmware's 5 °C under its line, the board's 9.7 W under its line and the 34-sensor mean's 6.3 °C under its line | `aifoundry3/e185/p18520/telemetry.jsonl.gz` |
| peaks, the smoke | board 51.68 W, firmware 57 °C, 34-sensor mean 58.18 °C | `aifoundry3/e185-smoke/p18501/telemetry.jsonl.gz` |
| clock and statistics | 600 MHz in 61,510 of 61,510 samples (842 + 60,668); `since_reset_ms` −1 in every sample (no statistics reset); the service processor's running board maximum 68.9 W, unchanged (set before today) | the two `telemetry.jsonl.gz` |
| config at both ends | TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV at the session's start and end | `logs/config-session-start.json`, `logs/config-session-end.json` |
| the plan's forecast at the room, **post hoc** beside the rules | the registered forecasts (E185.md section 5) are from planned watts at the plan's rooms; at 52.5 °C, the nearest warm room, P_F for H_E 11.808 and for H_E2 11.332 °C. The measured rises were 11.122 and 10.630. The rules read each arm on the session's measured watts, so a forecast that missed because the watts moved decides nothing | `tools/claims-v3/e185/design-e185.json` |
| the rest before the later try | 61 minutes since the first try's session end (03:31:32 PST), by step 10 v2's rest rule | step 10 v2's output (the lane's runbook log) |

## Who checked it

Before step 14, step 2 v5 ran again (06:17:40-06:17:52 PST, rc 0 at `52e3f68a`). It ran under one hold of the lab-git lock, and step 14 ran
right after it under the same hold, so no pull or commit could fall between them. Step 14 v2 (06:17:52-06:19:19) then ran its gates in order,
each passing:
- the eight lists as committed;
- the collector v2: COPY-BACK EXACT, 41 files. It named the earlier try's directories as "left on the box (not this session's manifest; an
  earlier try's, not copied): e185-smoke/p18501.try1 e185/p18520.attempt-1794486851", and it picked the host windows by T0;
- the session's own gates: "GATES-PASSED: the smoke's floor mark True; p18520's start gate True";
- the session log's own stops: none before the measured pass;
- the check of C, finished: `ccdone: 1 of 1 C checks finished`;
- the launch gate: `cclaunch: 2 pass(es) with a C log read against their marks; 0 problem(s): OK`;
- the login scrub in every directory (SCRUB-ALL CLEAN, 8 directories and 4 `.gz` files) and the desk-path gate (47 files, 0 hits);
- then M11's scorer v5 (`score rc=0`), and the desk-path gate on its files (0 hits).

No data verifier has read this directory yet: the day's verifier for E185 follows its data commit. october-forecast-model's reported arm
(note M1) is read only after this commit, through the day-2 check v2's gate. Its outputs and exit status go into a dated note beside this
README, never here (the brief's dated notes 1 and 2).

## Privacy and the public-text scan (before the commit)

- **Logins.** Step 14 v2's own gate ran E164's `scrub_etwho_e164.py --check` through `rb/scrub_all_e185.py` in every directory of this one.
  The scrub is unchanged and rewrites nothing; `--owner` is the box login of this repository's owner. Each `.gz` was unpacked outside the
  repository first. The result was CLEAN.
  - The lane re-read the final bytes the same way: E164's `--check` in all 15 directories of this one and of a scratch tree holding the text
    inside its 4 `.gz` files, every one rc 0. It found 0 of `run_e78`'s "another user on this card" lines and 0 of `lib.sh`'s "others
    present" lines.
  - The session log's et-who readings say "No process holds an ET-SoC-1 device node or card lock".
  - Other accounts' idle terminals on the box are named in no file. An idle login does not block, by the owner's ruling of 1 November 2026.
- **The public-text scan** used `tools/timeline/sanitize_extracts.py`'s fixed list, plus the private-network, Mac-home, scratch and e-mail
  patterns. It read every text file and the text inside every `.gz` of step 14's collection: 46 text files and 4 `.gz` files, 26,777
  matches.
  - 26,774 are the owner's own box home path, and 2 are the configs' tree key that names it. E166's, E176's and E181's committed data carry
    the same reviewed class.
  - The last one is the scan's private-network port pattern. It matched a telemetry counter value inside
    `aifoundry3/e185/p18520/telemetry.jsonl.gz`: the field `cmd_mismatch` reading 8792 in one sample, a command-mismatch count, not a network
    address. Reviewed, it is a false positive, as E181's README read the same field. The file is kept as collected.
  - This README and `SHA256SUMS` were scanned on their own afterwards.
  - The lab's private name table is absent on the Intel, so names were checked against the fixed list only. That is a stated coverage limit.

## Files

All files of step 14 v2's collection and score are here as step 14 left them, plus this README and [`SHA256SUMS`](SHA256SUMS), which pins
every file but this README and itself.

| path | what |
|---|---|
| `aifoundry3/e185-smoke/p18501/` | the later try's smoke as the box wrote it: `block.json`, `configs.json`, `marks.jsonl` (with A6-1's `floor` mark and the `stoptest` mark), `runs.jsonl`, `run.log`, `telemetry.jsonl.gz`, the config reads at both ends, the `STOP` and `HOLDSTOP` files of its stop tests, the binary, code and generator hashes, `manifest.txt`, the sampler's files |
| `aifoundry3/e185/p18520/` | the measured pass: R0, the start gate and the six holds (`marks.jsonl`, `runs.jsonl`, `run.log`, `telemetry.jsonl.gz`, `block.json`, the config reads, the hashes, the sampler's files) |
| `ccheck/` | the check of C: `ccheck-all.json`, `ccheck.txt` and the two passes' C logs as `.gz` (`c-log-p18501.jsonl.gz`, `c-log-p18520.jsonl.gz`) |
| `logs/` | the session's own T0 directory (`T1794486764`) as copied back: `session.log`, `smoke-gate.json`, `dmcmd-preflight.txt` (the box's device-command audit, GO), the config reads with their times and stderr, `MANIFEST.sha256` (the session's last act), `T0`; and `host-start.out` and `host-end.out` (steps 9 and 12) |
| `scored-m11.json`, `scored-m11.md`, `scored-m11-lines.jsonl` | M11's scorer v5's output, written after every gate: A10's reading with E176 (refused, excluded), E181 and E185, E185's rules and the stated reading's arm, A9's arm, A6-5's host readings and FL5(c) |

## What it does to predicting power and heat

- **Heat over minutes on aifoundry3, blind:** these are the first blind readings of the three arms, read on the measured watts over six 10-minute
  holds at a 52.10 °C room. The frozen chain missed by **0.2146 °C rms**, the rail-driven chain by **0.2158 °C** and the plain board gain by
  **0.2578 °C**.
  - The rail chain and the frozen chain cannot be told apart (NOT SEPARATED (F, Rl), D +0.0013 °C against τ 0.0361).
  - The board gain is worse than the frozen chain (D +0.0432 °C), and the rail chain is better than the board gain (D −0.0420 °C).
  - E181's held-out ranking (Rl 0.198, B 0.231, F 0.296 °C) did not carry: the frozen chain read E185 better than it read E181 (0.21 against
    0.30 °C). The board gain's one number over-predicts the duty-cycled fp32 holds (H_E2 −0.50 °C).
  - Nothing changes in M11: the chain unscaled stays the primary.
- **The cool-down shape** after the four big holds: d̄ +0.006 °C on F, with a wide 95% interval (−0.24, +0.25) from n = 4.
  - The window misses moved with their holds: H_E +0.27, L1 +0.27, L2 +0.03 and H_E2 −0.24 °C on F.
  - E185-C's power at σ_c was registered as weak, and NOT RESOLVED is what it read.
- **The start gate's residue line** refused the first try at a residue of 1.024 °C, against A1-5's prediction of about 0.53 °C. An hour later the
  same line passed at 0.125 °C. Why the card warmed during the first R0 is open.
- **The power side** is unchanged: no power figure is read or scored here. The holds' boards (H_E 55.3 W peak, 36.5 W mean) drive the chain
  as measured.

SPDX-License-Identifier: Apache-2.0
