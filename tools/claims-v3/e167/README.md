# E167 (Q141(h)): the heat replicate on aifoundry2 card 0 under its own governor - the run kit, ready for the card day

*Desk preparation, Wed 4 Nov 2026 (week 45), on the Intel: no card, no device command, no ssh to a lab box, no Discord, no Modal, no
archive. The card session needs the owner's go and fresh approvals; nothing here has touched a card. It answers Q139's final critic
**rank 3** ("Heat over minutes from the bits, a second session per card"), as Q140's final critic left it (`card_half[4]`, `desk_next` 3
and 7); on the kinds page, [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **items 9, 8
and 6**.*

## What is registered, and where

| commit | time (PST) | what |
|---|---|---|
| `7ba987b3` | 09:16:50 | **the registration** [`E167.md`](E167.md), [`e167-registration.json`](e167-registration.json), before any E167 data |
| `f830b9e2` | 09:31:08 | the scorer [`score_e167.py`](score_e167.py) and its self-test ([`logs/selftest-e167.txt`](logs/selftest-e167.txt), `.json`); the dated note [`E167.md.dated-note.md`](E167.md.dated-note.md) (the header's writing time; G1's reason stated against RA1.2's readout edge, 49.38 °C) |
| this commit | | the run kit, its hash list, the device-command audit, the desk dry queues, and this README |

It descends from Q140(e)'s frozen predictions and rules (registration `11174d20`, frozen `c9aaf179`, RA1 `a4fe976d`, `ac06c9be`), M9's
aifoundry2 part (`5b98bd5c`, `245caffe`, `5c98c0c5`) and E161 (`ddbd15b1`, `0158efd6`, corrections `d0704105` and `77d8b89b`, the dated note
`57304c1e`). **Nothing new is predicted.** E167.md adds **G1**, G1Q's start gate (its REST waits up to 240 s for a 49 °C die, and the hold
runs only if the REST's anchor reads 49.0 °C or less, else exit 6: G1Q NOT RUN, RK3-b not scored, G2Q still runs), and **E2**, a reported
arm with the day's zeros-anchor offset from E165 through `predict_m9_a2.session_delta`, beside D4's fallback (the primary).

## The scorer's self-test (before any E167 data)

`score_e167.py --self-test` (`/usr/bin/python3` 3.9.6, numpy 1.26.4, about 20 s): **every check passes.**
- On E161's committed data the scorer gives back Q140(e)'s `posthoc.json` E161 figures **exactly**: G1Q d 0.9696, anchor 47.0 °C /
  22.124 W, rise 15.935 °C, the primary **+0.636 °C at 0.504 °C rms** (RK3-b PASS, "not resolved by the readout": at −0.5 °C it reads
  +1.336 °C), arm A +0.372 °C (+2.33%, RK3-c outside); G2Q d 0.9702, the primary's trip clock **−4.0 MHz**, arm A −1.16%; and the M8 at d
  and M8 continuous arms with every checkpoint. RA1.3's referred arm gives back corrections.json C3 (G1Q −0.012 °C, G2Q +4.1 MHz). E161's
  registered reducer, run beside on the same data, gives back `results.json`'s six verdicts.
- Its arms at E161's anchors equal `predictions-q140e.json` › `E167.at_E161_anchor` and C3's `at_E161_anchor` byte for byte (eight of eight).
- A session whose G1Q stopped at the gate (E161's REST, no hold, exit 6) reads RK3-b "not scored: the start gate" and still scores G2Q
  (−4.0 MHz); RA1.2's regime rule reads PASS at 47.0 and 49.0 °C and "not scored" at 49.4, 49.6 and 50.5 °C (at the rest-board law, RA1.2's
  readout edge is **49.38 °C**: the gate at 49.0 sits under it); E2 with no anchors is the primary exactly, and anchors 1.0 W over the zeros
  level move the level by β × 1.0 W at every clock.

## The run kit (E161's, ported)

| file | from E161's | what changed |
|---|---|---|
| [`make_protocols_e167.py`](make_protocols_e167.py), `protocol-*.json` (seven, each with a `-dry` twin) | `make_protocols_e161.py`, E161's protocols | made from E161's committed protocols: every block, tool, stop and cap equal to E161's except G1Q's REST start (cool, 49 °C, 240 s; was 99 °C, 5 s), G1Q's cap 21 (was 17) and the added `e167_gate`; G1Q's HOLD block unchanged (93 × 8 s behind E98's 57 °C gate) |
| [`run_e167.py`](run_e167.py) | `run_e161.py` | G1Q's gate before the HOLD block (the anchor read as `reduce_e161.rest_reading` reads it; exit 6); a dry-only line (`E167_DRY_GATE_C`, refused without `--dry`); E167's names. The audited chain's hashes, the pool-6 tile check, the C log, the binaries' pins and the stops' refusal are E161's |
| [`queue_e167.py`](queue_e167.py) | `queue_e161.py` | exit 6 from G1Q: recorded as the gate, END skipped, the queue goes on to the rest and G2Q; G1Q's plan 19.6 card-minutes; no camera read under `--dry`; the go gate's marker `tools/claims-v3/e167/CLAIMED`; E161's rules otherwise |
| [`make_schedule_e167.py`](make_schedule_e167.py), [`run_e167.sh`](run_e167.sh) | E161's | E167's names; `run_e167.sh go` takes all four gates (smoke not before, smoke latest, no start after, cutoff), none defaulted; `check` runs the hash list |
| [`unitcheck_e167.py`](unitcheck_e167.py), [`collect_e167.sh`](collect_e167.sh) | E161's | E167's names (the runs directory `build/e167/runs`) |
| [`frozen-e167.sha256`](frozen-e167.sha256) | (new; E161 had none) | 43 files: E167's queue files and protocols, the audited chain, the tiles and inputs it checks, the C-check files, the audit, the host and kernel sources, and the three box binaries as E160/E161 pinned them |

**The stops** (E161's, stricter than section 26's general aifoundry2 stops): a hold ends at a die reading ≥ 72 °C (the shires' mean or the
hottest sensor, one live sample) or over 80 W on 3 consecutive live samples; tested on live samples by STOPTEST-DIE (30 °C) and
STOPTEST-BOARD (30 W). The 82 W admission: M8's 95% peaks 53.33 W (G1Q) and 68.15 W (G2Q), both admitted.

**Device commands** ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)): `dmcmd_audit.py` over E167's files, E144b's chain, the C-check
files and the host and kernel sources, Q136(w)'s table, E161's two reviewed exceptions (run_hpl.py:622's residency read, answered unsent; the
unit check's stand-in): **GO, 35 send sites, 0 disallowed, no allow-list** - every command a READ, the two PMIC voltage-register reads the
owner's allowed reads, no statistics reset. Without the exceptions: NO-GO on exactly those two lines. The unit check passes; the host source
names no device-management command; and G1Q's gate reads the anchor exactly as E161's reducer does (47.000000 °C / 22.123595 W from 1,199
lines on E161's G1Q, 47.000000 / 22.185613 on G2Q, equal to `reduce_e161.rest_reading`).

**The desk dry queues** ([`logs/dry-queue.txt`](logs/dry-queue.txt), 09:51-09:58 PST; `run_e167.sh dry` in a scratch copy of the committed
tree with these files, run_hpl's toy card, no device opened, no ssh, no network):
- **A, the registered gate:** SMOKE (sound), both stop tests (the die stop 54 ms after the first live line over 30 °C, the board stop 1 ms
  after the third line over 30 W, inside the launch), G1Q's REST read 51.0 °C on the toy card, so **G1Q stopped at the gate (exit 6)**, END
  was skipped, the queue rested and ran G2Q and END2, and ended "done";
- **B, the dry-only line at 60 °C:** G1Q's hold path ran, then END, G2Q and END2, "done";
- `E167_DRY_GATE_C` without `--dry` is refused before any device; the seven protocols list as registered;
- the scorer on B's collected layout ([`logs/dry-reduce.txt`](logs/dry-reduce.txt)) parses it (the toy card's numbers mean nothing).

## On the card day

**Card-minutes:** E161 used **35.07 of 40**; G1Q's REST wait can add up to 4, so at most about 39.1 of the **40-minute cap**, counted per step
by the queue. **The registered subset** (if the clock leaves no room for G2Q): SMOKE, the stop tests, G1Q and END. **The order on
aifoundry2: after E165** (its zeros anchors give E2's arm the day's offset; pass them to the scorer as `--e165-anchors`), then E167, then
E168. E98's 15-minute no-launch rests are inside the queue. About 70-75 minutes of wall time (E161's).

**The box steps that wait for the approvals** (nothing else is left):
1. The day's one `#community-lab` post with this card's clause (`using aifoundry2 for 1.5 h, until ~HH:MM PST [doc](<…>)`; section 15's
   rules).
2. On aifoundry2, in `~/claude/et-soc1-prototyping`: `git pull --ff-only` (the kit is on `origin/main`), then `bash
   tools/claims-v3/e167/run_e167.sh check` (the binaries, `frozen-e167.sha256`, `et-who`, the idle-login rule, the plans) and `… config
   start` (65 W / 65 °C as read; nothing set).
3. A dry pass on the box: `bash tools/claims-v3/e167/run_e167.sh dry`.
4. The queue: `bash tools/claims-v3/e167/run_e167.sh go <smoke-not-before> <smoke-latest> <no-start-after> <cutoff>` (in a script file run
   by `ssh aifoundry2 'bash -s'`), then the go: touch `build/e167/runs/GO` over ssh after the post names the card, or commit the marker
   `tools/claims-v3/e167/CLAIMED` on the Intel (the queue reads it from `origin/main` over https, so the go does not depend on reaching the box later).
5. After it, on the Intel: `bash tools/claims-v3/e167/collect_e167.sh <data dir> <from> <to>`, `ccheck.py check` on each step's C log, then
   `/usr/bin/python3 tools/claims-v3/e167/score_e167.py <data dir> [--e165-anchors <file>] --json <data dir>/scored.json`.

## What this does to predicting power and heat

Nothing yet: no frozen prediction changes, and no out-of-sample error moves until E167 runs. E167 then gives the first blind score, on
the governed card, of Q140(e)'s duty convention and M9's in-work level (T2 through its relation, one die law): G1Q's plateau and trajectory
where the bits set the die (RK3-b), the chain's gain given the watts on both large rises (RK3-c), and G2Q's sustained trip clock from the
bits. Before (as registered): E161 G1Q −0.90 °C (1.04 °C rms), G2Q's clock +12.6 MHz; post hoc on Q140(e)'s convention, in sample for the duty
and for the choice of option, G1Q +0.64 °C (0.50 °C rms) and G2Q −4.0 MHz.
