# E224 arm A's data README: the form the card lane fills for its data commit (Q237, lane kit-e224; kitted, not run)

*Fri 20 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md); E215's form ([../e215/DATA-README-FORM-e215.md](../e215/DATA-README-FORM-e215.md),
landed 8bde0182, whose arm B README followed it for aifoundry1 card 1) for E224 arm A's data directory. This is the form of `README.md` in
`docs/reports/data/<day>-e224-blind-matmul-aifoundry1-c1/`, written by the card lane (`card-e224a`) after step 12 (the collection) and before the data
commit, for a session in which at least one run started, in the lab's data-README form: **results first, then registered against happened, then
departures, each dated**. It is a form, not a result: every `<...>` is filled from the session's own files (`session/session.log`,
`session/queue.json`, `session/identity.json`, `data-e224a.json`, `reduce-e224a.txt`, the runbook's log, step 6n's report and judgement), and every
number carries its label. The README lies beside the data and is not in its `SHA256SUMS` (the collector made that list over the collected files).
A session in which no run started has no data directory: step 12 collects it into a gate stop's record, whose README has the shorter form at the
end of this file. The scorer runs after the data commit (step 13): its words are not in this README at the commit; a later lane adds them in a
dated note beside it.*

**The rules for this file.** No number from the owner's private pages or his A100 report. No sealed forecast's number (a sealed sha256 only, as
`tools/claims-v3/sealed-e224/` registers it). No lab user's login (the collector's scrub masked ours; write `<login>`). No credential or access
path. Times Pacific. The interpreter named. A check not run is NOT RUN. His words quoted without links. **The forecasts are BLIND**: every declared model's frozen by the registration commit (`tools/claims-v3/e224/forecast-e224.csv`, `forecast-e224.json`, `forecast-e224.txt`, each at its sha256 in `SHA256SUMS-e224-registration`; MM1-v3.2's land `4e386f75` the model's freeze line); quote them only from their frozen files.

---

```
# E224 arm A, <day>, aifoundry1 card 1 at 600 MHz as found: MM1-v3.3's blind day, arm A (64 points: D 30, P 16, L 18;
the tie t01 three times): <RAN FULL (the opening smoke s01, the stop-path test, <n> of 105 runs and the G block's smoke s03) / RAN SHORT (<n> of 105 runs: <why>) / STOPPED at <the stop> after <n> runs>

*<the day>, PST. E224, registered before any datum (<the registration's landed commit>: the freeze line of every composition's forecasts, the points, the
rules and the scorer), kitted (<the kit's landed commit>), verified (<lane, verdict>) and readiness-checked (<lane, verdict>); run on the owner's go
(<his words and their times>). The forecasts' freeze lines - OUT/reg-e224/FROZEN.txt (sha256 54277e52..., posted on the coordination thread at 15:45:40 PST Fri 20 Nov
2026) and the registration commit on GitHub main - came before the booking, with MM1-v3.2's land 4e386f75 (the models); step 0 read the
registration and the land (<the STEP0-E224 line>); THE PICK as the lab held it at the scorer's run (<E222's committed SEL, or NO PICK>). rgm136 (E136's binary, unchanged) and rgm211's host tree
(E211's) built today on the box: rgm136's ELF through THE KERNEL GATE and rgm211's tree through THE TREE GATE (<the build record's two gate lines>);
every process gated by its family's ELF - both families run rgm136's ELF ('rgm136 gemmL' on rgm136's host; 'rgm136 gemmLnc' on rgm211's host,
walk mn). Nothing was set on the card.*

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | <queue.json card_min> (planned: plan-e224.json > arms > A; no run starts after 60 minutes, cap 70); step 7's config read at <RB_OUT/e224a-step7-A.txt>, reported apart | measured (the session's clock) |
| the opening smoke, then the stop-path test | s01 gemmL2x2x2 fp32 (rgm136's host and ELF: the session's gate), 2 s: <its identity gate, the check of C, the counter's mean, the board's rise; the stop-path test's words> | measured |
| THE G BLOCK, LAST, AND ITS SMOKE s03 (E224.md 3, its own stop path) | <s03 gemmLnc2x1x37 fp32 (rgm211's host, rgm136's ELF; D1) at place 087 after its own rest: good / FAILED for its family alone (its words; queue.json's families_dropped; then the G block's 26 runs not started, NO DATA)>; then the G runs (the G block's points): each started or not, and why; the board's peak in the block against the 70 W x3 stop; a board stop there, if any, and the runs it cost | measured |
| THE IDENTITY GATE PER PROCESS | <every process's gate words by its family ('rgm136 gemmL', 'rgm136 gemmLnc'): "GATE OK: ..." for each, or the first GATE FAILED and where the session stopped> | measured (the gate's reading of the box's ELFs) |
| THE WALK CHECK | <every rgm211-host process ('rgm136 gemmLnc', walk mn): walk_ok true on every launch and walk_launches_bad 0, or the first failure and THE KERNEL STOP it caused> | measured |
| runs: started, with counted launches, not started (why) | <n started> / <n with t_gemm> / <reduce-e224a.txt's "not started" lines and runs without a counted launch> | measured |
| how the session ended | <"session end"; queue.json stop: none / the stop's words (a kernel stop names its run and family)>; runner.rc <0 / 8 HUNG / 1 a crash, its CRASH line> | measured |
| telemetry samples, and those at 600 MHz | <n> / <n at 600 MHz>; off the clock: <n> | measured |
| board power, peak; the shires' mean, peak; the latch (minshire[2]) at the start and its highest | <W>; <C>; <C> / <C> (arm A's stops: above 72 W on 3 samples in a row, the die 80 C; the die gate min(63, rest + 3) C; the drop line 69 W; the planning peaks PP32 from plan-e224.json) | measured |
| the opening and closing configuration reads | <config start>; <config end, or "not read: <why>"> | measured (READ) |
| the identity lines | <the config read's PCIe target and physical device ID>; <the identity read's counts and the sampler's nodes>; <each smoke host's stderr targets and held nodes> | measured |
| per point: cycles an op (the wall: cycles_gemm / ops a minion a GEMM; the counter's mean: the host's cycles_per_op), seconds a GEMM, p_work, p_rest, the die at the start (each run, and the point's mean) | <the table from reduce-e224a.txt> | measured (reduce_e224a.py) |
| the never-run search repeated right before the first card command (step 6n; `neverrun-e224-card.txt`, `.json`; `judge-e224-card.txt`, `.json`; `labels-e224.json`) | <its NEVER-RUN-E224 line: n of 84 registered points never ran; ran, labelled 'ran before' (E224.md 4): <none / the points, each file's date against the freeze line REPORTED>; the scan's files read> | a desk read; the labels go to the scorer |

## The meter's absolute scale (stated before the data)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside
meter** (E184's arm S, the test of the meter itself, is pending). The watts carry that gain.

## Registered against happened

| registered (E224.md, plan-e224.json, KIT.md) | happened |
|---|---|
| aifoundry1 card 1 at 600 MHz as found; the start config TDP 65 W / 65 C / 600 MHz, minion_mv below 510, /dev/et1_mgmt and physical ID 1; ET_DEVICES=1 on every device process; nothing on card 0 but A2's one READ | <the config reads; the identity lines; the clock in every sample> |
| the freeze lines on GitHub main before the booking (MM1-v3.2's land; the registration commit; the kit commit) and the sealed-forecast check (step 0) | <the STEP0-E224 line; any seal registered in tools/claims-v3/sealed-e224/ (its sha256 only; a later seal in a new note, its record line a comment)> |
| THE REST: 40 minutes since the last session on aifoundry1 (either card, ours or the model session's) and no write under the model session's ~/claude/work/ee-*/ there within the last 40 minutes | <the box's last session before E224 and its end; step 7's and step 9's "rest:" lines> |
| the window: G = the booking; last start G + 1:30, last end G + 3:30 | <G; the window; the launch before the last start; the session's start and end inside it> |
| the never-run search right before the first card command | <step 6n's time and line; step 7 within 30 minutes of it> |
| the opening smoke s01 (D1: gemmL2x2x2), then the stop-path test; the order: plan-e224.json > arms > A > runs (t01 at 001, 068 and 086; s03 at 087; the G block's 26 runs 088-113, last): 112 runs and 2 smoke processes | <what ran, in order; any run not started and why> |
| the identity gate per process (both families); the walk check; the kernel stops for the rgm211-host family | <every gate OK, every walk OK, or the stop> |
| the stops and gates (KIT.md 4) | <any stop, gate wait or NO DATA run, and why> |
| reads only (dmcmd_audit_v2 GO); no SIGKILL; a plain timeout 10 on every host (desk/timeouts-e224.json) | <the preflight's line; every process's rc; any HUNG line (then: reported and left)> |

## Departures (dated, before the results they touch)

- The go: <his words, as section 1 of CARD-LANE-BRIEF.md lists them>; G = the booking on its day; the post waived (his words, Sun 15 Nov 2026
  10:22:36 PST); the host's package counter not read; the desk aifoundry2 with `/usr/bin/python3` 3.12.3; the yvb3 session.
- The registration's D1 (each arm's smoke rows replaced by configurations under its drop line: arm A s01 gemmL2x2x2, s03
  gemmLnc2x1x37) is a registered item, not a departure of the day; say so.
- The die line's hottest sensor read as E213 and E215 arm A read it (not a departure): the latch at <its start value> C.
- <any other: a step re-run, a wait, a sealed forecast registered before the day (its sha256 only, never its numbers), a point labelled 'ran
  before' by step 6n (the dated note's name), ...>

## Files

`session/` (the box's session directory, copied back exact and scrubbed), `data-e224a.json` (the frozen scorer's input), `reduce-e224a.txt` (the
reducer's table), `neverrun-e224a-card.txt`, `neverrun-e224a-card.json`, `judge-e224a-card.txt`, `judge-e224a-card.json` and `labels-e224a.json`
(step 6n's report, judgement and labels, copied in by the collection), `SHA256SUMS` (all of these). The scorer's outputs follow after the data
commit (a later lane).
```

## The gate stop's record (no run started)

```
# E224, <day>: no run: <the gate's words> (a gate stop's record, never scored)

*<the day>, PST. The session <T0> on aifoundry1 card 1 stopped at <the gate> before any run: no data (E224.md 7: a point or case with no run is
NO DATA). <What the session did: the first card command or none; the identity lines if read; the smoke process if it ran, with its identity
gate.> E224 may be tried again as CARD-LANE-BRIEF.md section 3 says.*

## What happened
<the session log's lines from "session start" to "session end"; runner.rc; the runbook's step 10 reading>

## Departures
<as above>
```

SPDX-License-Identifier: Apache-2.0
