# E215's data README: the form each arm's card lane fills for its data commit (Q224, lane kit-e215; kitted, not run)

*Thu 19 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md); E213's form ([../e213/DATA-README-FORM-e213.md](../e213/DATA-README-FORM-e213.md),
landed 6efdb002, whose arm A and arm B READMEs followed it; arm B's with the A2 form's `fwgate/` folder), for E215's two data directories. This is the form of `README.md` in `docs/reports/data/<day>-e215-blind-matmul-aifoundry3/` (arm A) or
`docs/reports/data/<day>-e215-blind-matmul-aifoundry1-c1/` (arm B), written by that arm's card lane after step 12 (the collection) and before
the data commit, for a session in which at least one run started, in the lab's data-README form: **results first, then registered against
happened, then departures, each dated**. It is a form, not a result: every `<...>` is filled from the session's own files (`session/session.log`,
`session/queue.json`, `session/identity.json`, `data-e215.json`, `reduce-e215.txt`, the runbook's log, step 6n's report and judgement), and every
number carries its label. The README lies beside the data and is not in its `SHA256SUMS` (the collector made that list over the collected
files). A session in which no run started has no data directory: step 12 collects it into a gate stop's record, whose README has the shorter
form at the end of this file. The scorer runs after the data commit (step 13): its words are not in this README at the commit; a later lane adds
them in a dated note beside it. **The pooled rules** (HP1-HP5, E215.md 7) need both arms in one data file: the scores lane scores them once both
arms are committed; each arm's own step 13 prints them NO DATA. **Every verdict is per group and reported apart** (E215.md D1): the registered
group (families P, C, R: E215's answer) and the post hoc group (families L, S: "points chosen post hoc after the fit; forecasts frozen before any
E215 datum").*

**The rules for this file.** No number from the owner's private pages or his A100 report. No sealed forecast's number (a sealed sha256 only, as
`tools/claims-v3/sealed-e215/` registers it). No lab user's login (the collector's scrub masked ours; write `<login>`). No credential or access
path. Times Pacific. The interpreter named. A check not run is NOT RUN. His words quoted without links. **The forecasts are BLIND** (arm A:
MM1-v3.1's and MM1-v3's frozen at MM1-v3.1's land `2c971828`, `tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.csv` `f8fe39b4...`; arm B: this
registration's `forecast-e215b-v31.csv` `06541b49...`, `-v3.csv` `12a91f34...`, `-v2.csv` `0f1c6297...`, frozen with the registration's push;
'v3.1 with T7' REPORTED only); quote them only from their frozen files.

---

```
# E215 arm <A | B>, <day>, <aifoundry3 card 0 at its pinned 600 MHz | aifoundry1 card 1 at 600 MHz, ET_DEVICES=1, nothing on card 0 but the A2
form's one firmware read>: MM1-v3.1's blind matmul day (<60 points (32 registered, 28 post hoc) and 2 references | 30 points (18 registered, 12
post hoc) and 2 references>): <RAN FULL (the opening smoke, the stop-path test, <n> of <119 | 71> runs and the gemmLnc smoke) / RAN SHORT (<n> of
<119 | 71> runs: <why>) / STOPPED at <the stop> after <n> runs>

*<the day>, PST. E215, registered before any datum (<the registration's landed commit>: arm B's freeze line), kitted (<the kit's landed commit>),
verified (<lane, verdict>) and readiness-checked (<lane, verdict>); run on the owner's go (<his words and their times>). Arm <A | B>'s freeze line:
<arm A: MM1-v3.1's land 2c971828, committed 23:09:13 PST Wed 18 Nov 2026 | arm B: the registration commit <sha>, pushed <time>>; step 0 read it
on GitHub main (<the STEP0-E215 line>). <arm B: the firmware identity on this boot by the A2 form's step 4 (fwgate's look: <CONTINUITY | NEEDS-READ,
then one read EQUAL at <time>, the record in fwgate/>), its guard at step 9 "identity: ... ok".> rgm136 (E136's binary, unchanged) and rgm211
(E211's) built today on the box through their kernel gates (<the build record's two gate lines; arm B: both kernels at their whole ELF, and both
hosts and the device layer carrying ET_DEVICES>); every process gated by its loop's own ELF (THE IDENTITY GATE PER PROCESS, the four families).
Nothing was set on the card.*

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | <queue.json card_min> (planned <49.4 | 28.0>; no run after <60 | 42>, cap <70 | 48>); step 7's config read at <RB_OUT/e215-step7-<arm>.txt>, reported apart; <arm B: the A2 form's firmware read at <time>, reported apart> | measured (the session's clock) |
| the opening smoke, then the stop-path test | <arm A: s01 gemmL2x2x2 (rgm136: the session's gate), s02 gemmLn2x2x2 (rgm211's host and ELF), s04 gemmL2x2x2 (rgm211's host and ELF) / arm B: s11 gemmL2x4x4 fp32, s12 gemmL2x4x2 fp16, s13 gemmL2x4x1 int8 (rgm136: the session's gate), s15 gemmLn2x2x2 fp32 (rgm211's host and ELF: rgm211's ELF's first process on card 1)>, 2 s each: <each: its identity gate's words, rc, launches, the check, the walk (none / nm / mn; walk_ok on every launch, walk_launches_bad), the counter's mean cycles an op (R0's absolute band 200-4,000: in or out), the board's rise, the host's card>; the stop-path test <passed> | measured |
| THE FAMILY SMOKES (E215.md 3, each its own stop path) | <arm A: s02 'rgm211 gemmLn', s04 'rgm211 gemmL', s03 'rgm136 gemmLnc' (the gemmLnc block's, at place 112) / arm B: s15 'rgm211 gemmLn', s14 'rgm136 gemmLnc' (place 70)>: <each good / FAILED for its family alone: its words (the session log's "FAILED for its family alone" line; queue.json's families_dropped), and then its family's points not started (NO DATA) / a failure that was the session's: the stop's words> | measured |
| THE GEMMLNC BLOCK, LAST (E215.md 3) | <its smoke at its place after its own 10 s rest (its rest W, its rise), then its runs (<a026 a031 a024 a032, then reversed | b013 twice>): each started or not, and why; the board's peak in the block against the stop (<70 W x3 | 72 W x3>); a board stop there, if any, and the runs it cost> | measured |
| THE IDENTITY GATE PER PROCESS | <every process's gate words by its family ('rgm136 gemmL', 'rgm136 gemmLnc', 'rgm211 gemmLn', 'rgm211 gemmL'): "GATE OK: ..." for each, or the first GATE FAILED and where the session stopped> | measured (the gate's reading of the box's ELFs) |
| THE WALK CHECK | <every rgm211-host process ('rgm211 gemmLn': nm with the tag; 'rgm136 gemmLnc' and 'rgm211 gemmL': mn): walk_ok true on every launch and walk_launches_bad 0, or the first failure and THE KERNEL STOP it caused> | measured |
| runs: started, with counted launches, not started (why) | <n started> / <n with t_gemm> / <reduce-e215.txt's "not started" lines and runs without a counted launch> | measured |
| how the session ended | <"session end"; queue.json stop: none / the stop's words (a kernel stop names its run and family)>; runner.rc <0 / 8 HUNG / 1 a crash, its CRASH line> | measured |
| telemetry samples, and those at 600 MHz | <n> / <n at 600 MHz>; off the clock: <n> | measured |
| board power, peak; the shires' mean, peak; the latch (minshire[2]) at the start and its highest | <W>; <C>; <C> / <C> (the stops: <arm A: 70 W on 3 samples, 70 C | arm B: 72 W on 3 samples, 80 C>; the latch read as E206.md A1 item 1 and KIT.md 4.1 read it; the line 65 W; the planning peak <50.76 W at r01 | 58.35 W at r11>; the gemmLnc bounds REPORTED <62.92 W at a024 | 64.43 W at b013>) | measured |
| the opening and closing configuration reads | <config start>; <config end, or "not read: <why>"> | measured (READ) |
| the identity lines | <the config read's PCIe target, physical device ID, minion_mv (arm B: below 510, card 1)>; <the identity read's counts and the sampler's nodes>; <each smoke host's stderr targets and held nodes> | measured |
| per point: cycles an op (the wall: cycles_gemm / ops a minion a GEMM; the counter's mean: the host's cycles_per_op), seconds a GEMM, p_work, p_rest, the die at the start (each run, and the point's mean) | <the table from reduce-e215.txt> | measured (reduce_e215.py) |
| the never-run search repeated right before the first card command (step 6n; `neverrun-e215-card.txt`, `.json`; `judge-e215-card.txt`, `.json`; `labels-e215.json`) | <its NEVER-RUN-E215 line: n of n scored points never ran; ran before the freeze line, labelled: <none / the points>; ran after it (REPORTED, kept): <none / the points>; the scan's files read> | a desk read; the labels go to the scorer (`--labels`) at step 13; a point labelled 'ran before' gets the dated note |

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside
meter** (E184's arm S, the test of the meter itself, is pending). The watts carry that gain.

## Registered against happened

| registered (E215.md, plan-e215.json, KIT.md) | happened |
|---|---|
| <arm A: aifoundry3 card 0 at 600 MHz as found; the start config TDP 0 W / 65 C / 600 MHz | arm B: aifoundry1 card 1 at 600 MHz as found, ET_DEVICES=1, nothing on card 0; the start config TDP 65 W / 65 C / 600 MHz, minion_mv below 510> | <the config reads; the identity lines; the clock in every sample> |
| the freeze line on GitHub main before the booking (arm A MM1-v3.1's land; arm B the registration commit) and the sealed-forecast check (step 0) | <the STEP0-E215 line; any seal registered in tools/claims-v3/sealed-e215/ (its sha256 only; a later seal in a new note, its record line a comment)> |
| arm B only: the firmware identity on this boot (the A2 form's step 4 and its guard at step 9) | <fwgate's look; the one read's verdict and time, its folder in fwgate/; the evidence's reading ("one call on this boot, ended EQUAL"); the guard's identity line> |
| the rest: 40 minutes since our last session on the box (arm B: either card of aifoundry1, ours or the model session's) | <the box's last session before E215 and its end; step 7's and step 9's "rest:" lines> |
| the window: G = the booking; last start G + 1:30, last end G + 3:30 | <G; the window; the launch before the last start; the session's start and end inside it> |
| the never-run search right before the first card command | <step 6n's time and line; step 7 within 30 minutes of it> |
| the opening smoke (<s01 s02 s04 | s11 s12 s13 s15>; every family smoke with its own stop path), then the stop-path test; the order: <arm A: tie t01, pass 1 (80: tier 1 the registered points but gemmLnc, tier 2 family L, tier 3 family S's A B B A blocks), tie, pass 2 (tier 1 reversed, 28), tie, then the gemmLnc block (s03, 8 runs): 119 runs | arm B: tie t02, pass 1 (41), tie, pass 2 (tiers 1 and 2 reversed, 25), tie, then the gemmLnc block (s14, 2 runs): 71 runs> | <as run> |
| the identity gate per process (the four families); the walk check; the kernel stops for the rgm211-host families | <every gate OK, every walk OK, or the stop> |
| the stops and gates (KIT.md 4) | <any stop, gate wait or NO DATA run, and why> |
| reads only (dmcmd_audit_v2 GO); no SIGKILL; a plain timeout 10 on every device process | <the preflight's line; every process's rc; any HUNG line (then: reported and left)> |

## Departures (dated, before the results they touch)

- The go: <his words, as section 1 of CARD-LANE-BRIEF.md lists them>; G = the booking on its day; the post waived (his words, Sun 15 Nov 2026
  10:22:36 PST); the host's package counter not read; the desk aifoundry2 with `/usr/bin/python3` 3.12.3; the yvb3 session.
- The die line's hottest sensor read as E206.md's amendment A1 item 1 registers it and plan-e215.json adopts it (not a departure): the latch at
  <its start value> C.
- <any other: a step re-run, a wait, a sealed forecast registered before the day (its sha256 only, never its numbers), a point labelled 'ran
  before' by step 6n (the dated note's name), ...>

## Files

`session/` (the box's session directory, copied back exact and scrubbed), `data-e215.json` (the frozen scorer's input), `reduce-e215.txt` (the
reducer's table), `neverrun-e215-card.txt`, `neverrun-e215-card.json`, `judge-e215-card.txt`, `judge-e215-card.json` and `labels-e215.json`
(step 6n's report, judgement and labels, copied in by the collection), arm B's `fwgate/` (the A2 form's read folder and the evidence of the one
call, scrubbed, when step 4 read), `SHA256SUMS` (all of these). The scorer's outputs follow after the data commit (a later lane).
```

## The gate stop's record (no run started)

```
# E215 arm <A | B>, <day>: no run: <the gate's words> (a gate stop's record, never scored)

*<the day>, PST. The session <T0> on <aifoundry3 card 0 | aifoundry1 card 1> stopped at <the gate> before any run: no data (E215.md 7: a point
or case with no run is NO DATA). <What the session did: the first card command or none; the identity lines if read; the smoke processes if any
ran, with their identity gates and walks.> E215 may be tried again as CARD-LANE-BRIEF.md section 3 says.*

## What happened
<the session log's lines from "session start" to "session end"; runner.rc; the runbook's step 10 reading>

## Departures
<as above>
```

SPDX-License-Identifier: Apache-2.0
