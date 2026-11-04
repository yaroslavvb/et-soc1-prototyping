# E164's run kit: blind pool 7 on aifoundry1 card 1, ported from E157's, checked at the desk, ready for the box steps after the approvals (Q141(b))

*Wed 4 Nov 2026 (week 45), PST, on the Intel, Q141(b) (the card half's desk preparation). Desk only: no card claimed, no device command
sent, no lab box reached, nothing measured. It answers **item 6 of the kinds page's section 11**
([§ 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)) and Q140's final critic's
`card_half[1]` (E164) with `desk_next` items 1 (the registration) and 7 (the kit), for the Q139 critic's ranks 1, 4, 7 and the card-1
half of rank 14. The rules are registered in [`E164.md`](E164.md) (lab **`4286f0a8`**, 09:18:57 PST); the reference errors, the
machine freeze and the scorer, self-tested, in **`f4e75c95`** (09:41:51 PST); this kit in the commit that adds this README.*

## What it does to predicting power and heat

Nothing yet: it makes E164 runnable. E164 then gives **M9's first blind score on the second 600 MHz card** (power at 600 MHz on 61
new tiles, with M8, M7 and M6 beside it on the same tiles, and the die's rise over 4.5 s), the **card term on pool 7** with E163, rank
4's **paired-anchor card scale** on the E163 / E164 pair, and **card 1's day-to-day floor** (rank 7) under any M9 gain there. The
error before, nothing of it blind for M9: M9 nested on card 1's rows 0.211 / 0.178 / 0.185 W rms (fp32 / fp16 / int8); M8 blind on
pool 6 there (E157) 0.386 / 0.098 / 0.327 W, M6 0.283 W over 30 kinds; heat 0.12-0.18 °C. No frozen prediction changes here.

## Ready, and what waits

| step | state |
|---|---|
| registration, rules, sets, stops, plan | **committed** (`4286f0a8`), descending from pool 7 `75802201` / `3c9bb2ba` and M9 `1f244140` / `8dfafae3` (and every other frozen commit of the card half) |
| M9's card-1 reference errors | **committed** (`f4e75c95`): `ref_errors_e164.py` re-ran Q140(m)'s `fit_m9.run_family` unchanged; all 855 rows equal `rows-m9.json`'s committed errors (worst 0 W), card-1 pools 171 / 145 / 84 rows at 0.2112 / 0.1783 / 0.1847 W |
| the scorer, self-tested on E157 | **committed** (`f4e75c95`): `score_e164.py` run in E157's own registration reproduces all 25 of E157's registered verdicts and every one of 8,297 (8,960 with E153's reduction) numbers of `scored.json` and `scored-e153.json`, and both results pages byte for byte ([`selftest-e157-repro.txt`](selftest-e157-repro.txt); Python 3.12 or later, as E157's scorer ran) |
| E164's own rules on simulated sessions | **committed**: [`selftest-sim.txt`](selftest-sim.txt) (K7 removes a 2% session gain, passes with one tile moved 0.3 W and fails with two; U1 catches an M6-right world 20 times in 20; the C paths; X1 / X2) |
| rank 4's pair score | **committed**: [`pair_rank4_e164.py`](pair_rank4_e164.py) runs Q140(x)'s `score_rank4.py` unchanged (pinned); its self-test reproduces `selftest-rank4.txt` byte for byte and reads E164's layout ([`selftest-rank4-pair.txt`](selftest-rank4-pair.txt)) |
| the run kit, ported from E157's | **this commit**: every file the box runs pinned in [`harness-e164.json`](harness-e164.json) (E78's 15 card-code files equal to E157's pins, E164's 10 card files, 78 pool files with 72 tiles, E157's four binary pins) |
| device commands | **GO**: 32 send sites, 0 disallowed, with the one reviewed exception (`lib.sh:154`, the forwarded `--reset-ms` E164 never passes) ([`dmcmd-audit.txt`](dmcmd-audit.txt)); NO-GO without it, as E157's ([`dmcmd-audit-noexcept.txt`](dmcmd-audit-noexcept.txt)); the desk files and the box-step scripts: GO, no send site ([`dmcmd-audit-desk.txt`](dmcmd-audit-desk.txt), [`dmcmd-audit-box-steps.txt`](dmcmd-audit-box-steps.txt)) |
| the dry pass on the Intel | **done** ([`dry/`](dry/)): see below |
| a verifier over the registration, scorer and kit | **owed** (Q140 critic's `desk_next` 8) |
| E163's registration and scorer (the pair's other half) | Q141(a)'s, at the same time; RK4 and X1 / X2 are scored only with E163's committed files |
| everything on the box | **waits for the approvals and his go** (below) |

## Card-minutes and the cap

**Expected about 56-58 card-minutes; the cap is 65** (the critic's: about 54-57 for 89-93 runs; E164's passes have 96, since pool 6's
three random anchors run again for rank 7's scale). From `E164_T0`, the session's first device access: the stop-path test and the
smoke about 1.5 min, then **four passes of about 827-848 s** (E157's passes on this card took 658-675 s for 78 launches; 98 launches
scale to 827-848 s) with 10 s between. The queue starts a pass only if its projected end (900 s until the first pass ends, then the
longest measured) is inside **3,840 s** of `E164_T0` and before `E164_DEADLINE`; a fifth pass does not fit, and a pass in flight is
never cut. **The registered subset**: the four priority-2 tests dropped before the session (`E164_DROP_P2=1`, 92 runs a pass, about
2 minutes less over four passes); below that, two kept passes are the scoring minimum. The day's one post carries `using aifoundry1
card 1 for 1.5 h, until ~HH:MM PST`.

## The order on the box

E164 is the only run on aifoundry1 card 1 in the card half, and runs in parallel with aifoundry3 (E166, then E163) and aifoundry2
(E165, E167, E168, E169). **aifoundry1 card 0 is never used**, and **never two of our sessions on aifoundry1**: `session_e164.sh`
refuses (exit 3) if any device process of ours runs or any node or lock is held by us on either card before it opens anything. Rank
4 and X1 / X2 are scored after both E163 and E164 have committed their data.

## Box steps, after the approvals and his go

Each is a script in [`box/`](box/), run from the Intel's lab tree (`ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' <
<script>` for the box ones). If an approval link appears, stop and follow the round's brief; never wait on it.

1. **Look, read only** ([`box/look_e164.sh`](box/look_e164.sh)): the host's boot time against E82's firmware read (the build's
   read-only identity: it must precede 2026-10-31 13:45:24 PDT), `et-who` (card 1's own lines decide; read it, never copy a name),
   the login count, `/home`'s room, the four binaries against E157's pins, the card locks, our own processes (none), python.
2. **Sync** ([`box/sync_e164.sh`](box/sync_e164.sh), on the Intel): `tools/claims-v3/e164/` and pool 7 into `~/nekko`; pool 6 and
   Q139(k)'s `ccheck/` are there from E157 and are checked by sha256, not overwritten. No compiled source changes, so **nothing is
   rebuilt**: the C-logging host must be present as E157 ran it (`build/ccheck/b/host/sparsity_host` `4f0956ce…`). If any binary is
   missing or differs, stop: a rebuild with `build_host_ccheck.sh` (a fresh `build/ccheck`, `-j4`) needs a dated amendment re-pinning
   it before the claim.
3. **Check on the box** ([`box/check_box_e164.sh`](box/check_box_e164.sh)): `check_e164.py` HARNESS OK with the binaries;
   `preflight_e164.sh` GO; the 72 tiles; pool 7's SHA256SUMS 91 OK; the dry pass of a pass (rc 0), the smoke (rc 0) and the stop-path
   test (rc 1, as a dry run must end).
4. **The claim**: the day's one post in `#community-lab`, rewritten by the round's rules (the clause above, beside any other card
   held).
5. **Launch** ([`box/launch_e164.sh`](box/launch_e164.sh)) with the deadline (the round's time gate less 10 minutes) as its argument:
   it detaches `session_e164.sh` (`setsid nohup`), which runs `check_e164.py`, the preflight, the identity and holder checks, the
   opening config read, the stop-path test, the smoke and its gate, the queue and the closing config read.
6. **Wait** ([`box/wait_e164.sh`](box/wait_e164.sh)), bounded at 540 s a call, repeated; then the post's release edit.
7. **Pull and collect on the Intel** ([`box/pull_e164.sh`](box/pull_e164.sh), then `PY=<python with numpy> PYS=<python 3.12+>
   E164_DATE=<the day> nice -n 10 bash tools/claims-v3/e164/collect_e164.sh build/e164-raw [<E163's e163.json> [<its C-excluded
   tiles> [<E163's scored.json>]]]`): the primary reduction and the arms, every launch's C checked at the desk, `score_e164.py`, and
   rank 4's pair when E163's files are given. The data directory is `docs/reports/data/<the day>-e164-blind7-card1/`.

## The dry pass on the Intel

[`drypass_intel_e164.sh`](drypass_intel_e164.sh), run as `bash tools/claims-v3/e164/drypass_intel_e164.sh <scratch dir>`: a copy of
the tree laid out like `~/nekko`, labelled stub binaries that refuse to run, a `hostname` shim answering the box's name so lib.sh
selects `aifoundry1-c1`, and GNU date. No device opened, no ssh. Results ([`dry/drypass-summary.txt`](dry/drypass-summary.txt), every
scratch path replaced by a placeholder): `check_e164.py --desk` HARNESS OK on 103 files; the tiles OK; the preflight GO; **a pass of
96 runs** ([`dry/plan-16410.json`](dry/plan-16410.json): segments 31 / 31 / 32, E78's six anchors and pool 7's two int8 random
anchors three times each, 98 device calls printed with the two burn-in runs) rc 0; the smoke rc 0; the stop-path test rc 1 (its
stops need live samples); the priority-2 switch gives **92 runs** with no priority-2 test ([`dry/plan-16411-dropp2.json`](dry/plan-16411-dropp2.json));
card 0 and a missing `V3_DEVICE` refused (rc 2); the queue and the session refuse without `E164_DEADLINE`; the queue on a stub block
stops on its budget, on a past deadline and on a STOP file, and runs five passes when they fit; and the whole session dry ran the
check, the preflight, both tests, the gate (FAIL: no live records, as expected) and five dry passes of 96 runs
([`dry/session.log`](dry/session.log), [`dry/queue-lines.txt`](dry/queue-lines.txt)).

## Files

| file | runs where | what |
|---|---|---|
| [`E164.md`](E164.md), [`pick7_e164.py`](pick7_e164.py) → `pick7-e164.json`, `.txt` | desk | the registration; rank 7's mechanical pick (`4286f0a8`) |
| [`ref_errors_e164.py`](ref_errors_e164.py) → `ref-errors-m9.json`; [`make_predictions_e164.py`](make_predictions_e164.py) → `predictions-e164.json`, `planned-intervals.txt` | desk | M9's card-1 reference errors; the machine registration and the precision before data (`f4e75c95`) |
| [`score_e164.py`](score_e164.py), [`selftest_score_e164.py`](selftest_score_e164.py) → `selftest-e157-repro.txt`, [`selftest_e164.py`](selftest_e164.py) → `selftest-sim.txt`, [`pair_rank4_e164.py`](pair_rank4_e164.py) → `selftest-rank4-pair.txt` | desk | the scorer and its two self-tests; rank 4's pair score (`f4e75c95`) |
| [`e164_common.py`](e164_common.py), [`run_e164.py`](run_e164.py), [`block_e164.sh`](block_e164.sh), [`queue_e164.sh`](queue_e164.sh), [`session_e164.sh`](session_e164.sh), [`check_e164.py`](check_e164.py), [`preflight_e164.sh`](preflight_e164.sh), [`smoke_gate_e164.py`](smoke_gate_e164.py) | the box | the session, ported from E157's with each change marked `E164` in the file |
| [`reduce_e164.py`](reduce_e164.py), [`collect_e164.sh`](collect_e164.sh) | desk | E78's reduction unchanged, and the collector |
| [`make_harness_e164.py`](make_harness_e164.py) → [`harness-e164.json`](harness-e164.json) | desk | the hashes the box checks |
| [`drypass_intel_e164.sh`](drypass_intel_e164.sh), [`dry/`](dry/) | desk | the Intel dry pass and its outputs |
| [`box/`](box/) | the box and the Intel | the box steps above |
| `dmcmd-audit*.txt` | | the device-command audits |

**The Intel's batch guard.** The desk runs here (the reference errors, the self-tests, the dry pass) were single-core and short, at
`nice -n 10`; when the Intel's guard reported this session's processes already at four cores (another lane's bench), they ran under
its stated exception for work that needs this Mac's own files, since this round reaches no lab box.

## What this cannot say

The kit is ported and dry-run, not run: nothing here has opened card 1. The box steps re-read what the desk cannot: the binaries,
the build's identity, the holders and the host's room. Rank 14's card-1 half stays open (dropped by name in `E164.md`: E155's masked,
shaped launches cannot be C-checked with what exists). Rank 7 needs a second new card-1 session after this one.

SPDX-License-Identifier: Apache-2.0
