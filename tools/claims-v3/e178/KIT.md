# E178's run kit: the 40 one-number kinds on aifoundry3 card 0 at 600 MHz, a matrix of 4s against a matrix of 5s among them, every launch's C checked, and the scorer for every registered rule (Q146; kitted, not run)

*Thu 5 Nov 2026 (week 45), about 22:15-23:15 PST, on the Intel, desk only (Q146, lane `kit-e178`): no card was claimed, no device command
was sent, no lab box or mordast was reached, nothing was posted. New files only: the registration [`E178.md`](E178.md) (`48171930`, 20:51:01
PST), its dated note [A1](E178.md.dated-note-A1.md) (`f421c67a`, 22:12:30 PST) and every file their two hash lists name stay as committed
(76 of 76 and 27 of 27 OK after this commit). This is section 12's step 3, the kit and the scorer. No E178 datum exists: `git log --all`
shows no `docs/reports/data/*e178*`. It answers the owner's ask of Thu 5 Nov 2026, about 19:30 PST ("here's a matrix filled with one number,
and here's a matrix filled with another number, and they require different number of transistor flips, therefore they will use different
power, and I have a model which actually tracks it down"), for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6. Nothing here changes a rule,
a forecast, a threshold or a registered power figure.*

## Results first

- **The box kit, E171's form with the v3 drivers, for aifoundry3 card 0.** E78's runner and reduction run unchanged with E178's 40 kinds
  and its registered order installed; every launch goes through Q139(k)'s C-logging wrapper; E171's live stops (65 W, 70 C on
  `minshire[0]`) and in-run watcher; FULL (17810-17813, cap 60 card-minutes) and TWO (17810-17811, cap 32); the stop-path test 17802 and
  the smoke 17801 (E178.md section 7's ten items) gated as E171's.
- **The order is the registered one, three ways.** `e178_common.py` rebuilds each pass by the rule with its segments, and refuses unless it
  equals both `plan_e178.one_pass` and `plan-e178.json` run for run. In the dry pass, the order E78's runner recorded for every planned pass
  (`plan.json`) equals `plan-e178.json`.
- **The scorer** ([`score_e178.py`](score_e178.py)) reads every rule of section 5 and A1's E178-S-int8. It reports F's SIZE beside P's for
  H and U, and 127 - neg_ones beside S. It reads the owner's sentence only when A1-1's four rules read together.
  - **Its self-test, 16 of 16 PASS** ([`logs/selftest-score-e178.txt`](logs/selftest-score-e178.txt)). Fed A1's own draws, its
    interval, SIGN and SIZE functions give power-e178-a1.json's shares EXACTLY. That includes F's SIZE coverage: dF inside 0.9312 if F is
    right, 0.7933 if P is right, 0.3344 under no difference (A1-5).
  - On E171's committed anchors, its routes give E171's committed scale and C counts exactly.
  - Eight synthetic E178 sessions read as designed: P true reads POSITIVE with SIZE PASS on H-int8 and on S-int8, and the owner's sentence
    is measured. A truth of the operands' held 1-bits reads S-int8 NEGATIVE. With int8 flat, R-int8 FAILS and W-int8 FAILS HIGH. One C FAIL
    on int8 85 drops it from every set. One kept pass gives NOT SCORED. A lost run is handled. Card 1 uses its own forecasts. The C-session
    gate passes and refuses as it should.
- **The collection, end to end, 5 of 5 PASS** ([`logs/selftest-collect-e178.txt`](logs/selftest-collect-e178.txt)). `collect_e178.sh` ran
  `reduce_e178.py`'s primary and seven arms, and `score_e178.py` with every arm, on real card files: E171's four committed passes,
  relabelled by rule into E178's order. A plumbing test only; its verdicts are E171's tiles under E178's labels and are never quoted.
- **Device commands: `dmcmd_audit.py` GO, 32 send sites, 0 disallowed, every one READ** ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)).
  E153's one reviewed exception, `lib.sh:154`, is E171's: the statistics reset is never sent. Without it the audit reads NO-GO exactly
  there ([`logs/dmcmd-audit-noexcept.txt`](logs/dmcmd-audit-noexcept.txt)). The desk files send nothing (GO, 0 sites). The runbook's
  steps with k6's steps 5 and 9 read GO, 11 sites, all E128's guard lines.
- **The Intel dry pass, DRY-INTEL PASS** ([`logs/dry-intel.txt`](logs/dry-intel.txt)), 19 of 19 checks: every planned pass 78 launches
  through the wrapper, the smoke 10, unplanned passes refused, the queue's budget, deadline and plan rules, the session's three start gates,
  and no ssh, rsync or scp call (the stand-ins log and refuse).
- **The runbook (the k6 v3 drivers, sourced unchanged), desk test 17 of 17 PASS with a fake ssh and rsync**
  ([`logs/selftest-rb-e178.txt`](logs/selftest-rb-e178.txt)); its dry listing ([`logs/dry-listing-e178.txt`](logs/dry-listing-e178.txt))
  makes no network call.
- **Not in this kit:**
  - aifoundry1 card 1, the registered fallback (section 7, A1-7's footing), is not kitted. Its box kit is E172's form and needs its own port
    and readiness check. If aifoundry3 is held at the go, E178 waits; it is not run on card 1 from these files. The scorer already reads
    card 1's frozen P and F.
  - Dated note M1 (section 8, the mordast forecast's sha256) is not committed. Step 3 reports it, and without it that forecast is not
    scored. The kit does not need it to run.
  - The anatomy's extra readings (section 43, such as an idle read beside each pass) are not taken. They would need a dated amendment
    before any datum.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md and MAP.md, read Thu 5 Nov 2026 about 22:20-22:30 PST. Public rows read: H07, H15, H21, H24,
   H27, H28, L06, P05, P06, P08, P09, P11, P12; MAP rows 19, 41 and section 3. The row ids are opaque pointers into a private file.
2. **Used** (each piece unchanged, called or sourced by path, its sha256 in [`SHA256SUMS-e178-kit`](SHA256SUMS-e178-kit)), with the
   check against an earlier measurement where one exists:
   - **E171's kit** (Q142(k6), `tools/claims-v3/e171/`, `1b80da20` with its notes): the form of every box and desk file here (runner, block,
     queue, session, check, preflight, smoke gate, reducer, collector, harness and plan makers, dry pass, watcher test).
     - *Check:* E171's session on this card (5 Nov 2026, data `91f8ae40`) ran its 86-launch passes in 818-862 s. Scaled to E178's 78
       launches that is 740-780 s a pass, the registration's figure, on which the queue's first estimate (800 s) and the caps rest.
   - **E78's card code and reduction** (`run_e78.py`, `reduce_e78.py`, `e78_common.py`, `kinds.json`) and E163's 14 reused files and four
     box binaries: `make_harness_e178.py` refuses unless every value equals E163's and E171's harness.
   - **Q139(k)'s check of C** (`ccheck.py`, `sparsity_ccheck.sh`, the C-logging host) unchanged. The C-session rule is
     `ccsessions_p8.py` (Q142(k6), `a518aa11`), imported unchanged with E178's layout added in memory. E163's `c_status` comes from
     `score_p8_600.py`.
     - *Check:* both routes on E171's committed session: 5 of 5 listed sessions checked; every anchor and tie launch PASS (B1, B3).
   - **Q139(u)'s footing**: `reduce_footing.K_FROZEN['a3']` = 0.20563713796102187, which the collector reads and refuses on any other value.
     It is E178.md section 5's primary, with dips removed once (E82 A2).
   - **M10 and pool 8's frozen predictor** (`m10.json`, `predict_m10.d600`; `predict_pool8.scale` with pool 8's frozen anchor features):
     M10's term a, as E171's scorer reads it.
     - *Check:* on E171's committed reduction the route gives E171's committed s (1.006149) and its six ratios exactly (B2). The scored P
       equals `d600` on each kind's frozen features at three (s, rate) points to 4e-15 W (A2).
   - **The k6 runbook's v3 drivers** (`q141k-runbook/k6/rb_common.sh`; v3.1's `rb_run.py`, `nopath_q142s.py`, `ccdone_q142s.py`), sourced
     unchanged. k6's steps 5 and 9 are used unchanged. `rb/` holds E178's own steps 2, 3, 7, 8, 10, 11, 20 and 22 in their form.
   - **Q136(w)'s `dmcmd_audit.py` and table, and E128's `ettelem_guard.sh`**: the audits.
   - **E178's registration and A1** (`kinds-e178.json` and the tiles, `plan-e178.json`, `forecast-e178.json`, `power-e178.json`,
     `power_e178.py`, `power-e178-a1.json`): imported unchanged, each checked against the registration's hash lists first.
     - *Check:* the scorer's functions reproduce power-e178-a1.json's E178-S-int8 and E178-U shares and power-e178.json's E178-H-int8
       shares exactly on their own seeds (A3, A4). The tiles re-make byte for byte by rules R1-R4
       ([`logs/tiles-check-e178.txt`](logs/tiles-check-e178.txt), 40 kinds).
3. **Not used:**
   - E172's card-1 kit (`tools/claims-v3/e172/`): owed to a later port (the fallback card).
   - The energy manual's catalogue and `catfull`: not applicable here (the vector arm stays outside E178, A1-2).
   - Public sysemu: not applicable (E178.md section 9's reason).
   - E147-style trains: not applicable (they are a later registration's route for the float pairs).
   - M11's holds: not applicable (heat over minutes; E178 scores power).
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this kit. Dated note M1, when
   committed, adds only the one line the rule allows.
5. **Readiness:** this block is the kit's. A verifier checks it against INVENTORY.md and the cited commits.

## The scorer's readings, stated here before any datum (where section 5 and A1 leave a choice)

- **A kind's per-pass D** is the reduction's per-pass entry: the mean of its kept runs, as E78's reduction writes it.
  - A couple's per-pass x_p (E178-H-int8, -fp32, -fp16 and E178-U) is the mean, over the pass's segments in which both runs were kept, of
    D(5s) - D(4s) (U: D(ones) - D(uf)) in that segment, read from the primary's `runs.csv`. With every run kept this equals the per-pass
    difference (B4: to 4e-15 W on E171's data). A pass with no complete couple gives none.
  - E178-S-int8's x_p is D(85) - D(neg_ones) per kept pass (one run each).
  - The interval is t(0.975, n - 1) over the passes that give a value. Fewer than 2: NOT SCORED.
- **The scored forecasts**: P = the frozen P x s x (the kind's measured rate / E171's rate), and F likewise. That is M10's d600 at the
  session's s and rate, since d600 is linear in both (A2). s is M10's term a for floats and 1 for int8.
  - The scale may read only E78's random float anchors, fp32.randn and fp16.randn. Any other anchor refuses (5).
- **SIZE words.** FAIL HIGH means the forecast is above the measured interval: the model prices more than the card reads. FAIL LOW means
  it is below. This is E178.md section 5's own definition (W: "FAIL HIGH (M10 prices the flips higher than the card)") and E171's scorer's.
  Every SIZE verdict prints its direction in words.
  - A1-1's sentence "With SIZE FAIL LOW, the flips' sign holds and something takes part of it back" uses the word for the measurement's
    side. It names the case printed here as FAIL HIGH. A1's power tables name W's cases the same way.
  - So the two texts use opposite words for one case. No verdict or threshold depends on the word. A one-line dated note should settle
    it before any datum (open item 3 below).
- **E178-R-int8** at 13 kinds: the registered line, 0.56. At fewer kinds (E178-C left some out), the line is the 97.5% point of rho over
  20,000 shuffles of the measured D, from `random.Random(17805)` (power_e178's seed for the rule). At 4 kinds or fewer: NOT SCORED.
- **E178-W-int8**: the OLS slope of the measured D on (i)'s launch-mean flips, divided by the mean of the scored kinds' measured rates, with
  t(0.975, n - 2). The line is power-e178.json's P slope, 7.4796 fJ a flip. The scored P's own slope is printed beside it.
- **E178-E**: power_e178's groups and generator, `random.Random(17807)` for each group. Each member's se is its sd over passes / sqrt(n),
  plus the 0.041 W session term. PASS ("read equal") if the spread is at or below the 95% point.
- **Reported, never a verdict:** every pair of section 4 and the extremes against P and F; each kind's D, P, F, flips and rate; the floats'
  ranking and slope; 127 - neg_ones; the smoke's C per item (fp32.e178_uf's must read +0 throughout); whether each kept pass ran
  plan-e178.json's order; the scale anchors' C status; seven reduction arms (E171's).

## Card-minutes and the cap

| plan (`E178_PLAN`) | sequence | expected | cap (the budget rule) | the day's post says |
|---|---|---|---|---|
| **FULL** (default) | 17810, 17811, 17812, then 17813 if it fits | **about 51-54** | **60** (3,600 s from E178_T0, 60 s reserve) | `for 1.5 h` |
| TWO (the registered subset) | 17810, 17811 | about 27 | 32 (1,920 s) | `for 1 h` |

The queue's first estimate is 800 s a pass, then the longest measured. A pass in flight is never cut, and a fifth is never planned.
**TWO cannot answer E178-H-int8 (0.226), E178-S-int8 (0.244) or E178-U (0.093)** (A1-4). FULL gives 0.90 on H-int8 only with all four
passes kept.

## The order on aifoundry3

E178 runs alone on aifoundry3, starting with `et-who` clean; an idle login does not block (D1, the owner's ruling of 1 Nov 2026). Never
two of our sessions on one card. The day's one post follows the one-post rule.

## The box steps that wait for the approvals and his go

Run them from the lab clone after `git pull --ff-only`, each with this card day's `RB_OUT` and `RB_LOCK`. The k6 drivers bound every remote
call: a 15 s hard-killed probe, then 60 s for a read, 600 s for a copy. A printed login link stops the step (11) and appends
`<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`.

1. **His go and fresh network approvals** for aifoundry3, with the round's time gates. Then [`rb/s02_window_e178.sh`](rb/s02_window_e178.sh)
   `<day> <last start> <last end>`.
2. **The desk check**, [`rb/s03_desk_e178.sh`](rb/s03_desk_e178.sh): pull; HEAD descends from `f421c67a`; E178's paths clean; the three hash
   lists; the kit and harness rebuilt; the orders verified; HARNESS OK 80 without binaries. It reports dated note M1 present or absent, and
   any E178 data in any ref.
3. **The day's one post** in `#community-lab` (the card lane's, under the post's lock):
   `using aifoundry3 for 1.5 h, until ~HH:MM PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
4. **Look first:** `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` (k6's, unchanged).
5. **Sync:** [`rb/s07_a3_sync_e178.sh`](rb/s07_a3_sync_e178.sh), one rsync. It copies E178's directory, E78's six committed one-number tiles
   and the pinned watcher files; uncommitted changes refuse.
6. **The checks on the box:** [`rb/s08_a3_preflight_e178.sh`](rb/s08_a3_preflight_e178.sh): `HARNESS OK: 84 files` (E163's four binaries
   among them), the preflight GO, the items and orders verified. If a binary differs, stop: a dated amendment registers it first.
7. **Reads:** `../q141k-runbook/k6/s09_a3_reads_k6.sh` (k6's, unchanged): `et-lab-manifest`, the config through the guard (0 W / 65 C /
   600 MHz), et-who clean.
8. **A V3_DRY pass on the box:** [`rb/s10_a3_dry_e178.sh`](rb/s10_a3_dry_e178.sh) `start`, then `wait` while it says 17. That is 17810's 78
   launches, the smoke's 10, and the start gate refusing (8).
9. **The session:** [`rb/s11_a3_session_e178.sh`](rb/s11_a3_session_e178.sh) `FULL` (or `TWO`). It launches
   `E178_T0=$(date +%s) E178_PLAN=FULL E178_LATEST_START=<last start> E178_DEADLINE=<last end> setsid nohup bash tools/claims-v3/e178/session_e178.sh`
   detached. The session runs the check, the preflight, the stop-path test and the smoke with its gate before any pass.
10. **Wait:** [`rb/s20_wait_e178.sh`](rb/s20_wait_e178.sh), repeated while it says 17.
11. **Release, then collect:** the post's release. Then [`rb/s22_collect_e178.sh`](rb/s22_collect_e178.sh): the copies into
    `build/e178-raw`, `collect_e178.sh`, the C-session gate, E164's scrub check and the desk-path gate. The output is
    `build/e178-out/<day>-e178-one-number-aifoundry3/`, and the data directory is `docs/reports/data/<day>-e178-one-number-aifoundry3/`. The
    login scrub and the public-text scan come before its commit.

## Files, and what each builds on

| file | what | builds on |
|---|---|---|
| `e178_common.py` | the items (E78's 51 and the tie, plus the 34 new tiles), the registered order with segments, the smoke, the frozen checks | `e171_common.py`; `plan_e178.py` |
| `run_e178.py` | the runner: E78's unchanged, with E171's live stops and watcher | `run_e171.py` |
| `block_e178.sh`, `queue_e178.sh`, `session_e178.sh` | one pass, the plan's budget, the session | E171's three |
| `check_e178.py`, `preflight_e178.sh`, `smoke_gate_e178.py` | the harness check, the device-command preflight, the smoke gate | E171's three |
| `kit-e178.json`, `make_kit_e178.py` | section 7 in machine form; the new tiles' A and B sha256 | `make_plan_e171.py` |
| `harness-e178.json`, `make_harness_e178.py` | the sha256 of everything the box runs (84 with binaries) | `make_harness_e171.py`; E163's and E171's harness |
| `reduce_e178.py` | E78's reduction unchanged on E178's passes; the footing's options | `reduce_e171.py` |
| `collect_e178.sh` | the check of C, the primary and seven arms, the scorer, the copies | `collect_e171.sh` |
| `ccsessions_e178.py` | the C-session rule on E178's layout | `ccsessions_p8.py`, unchanged |
| `score_e178.py` | section 5's rules, A1's S-int8, F's SIZE, the reported readings | E171's scorer forms; `power_e178.py`; `c_status`; `predict_pool8.scale` |
| `selftest_score_e178.py` | the scorer's self-test (A1-A4, B1-B4, C1-C8) | A1's draws; E171's committed data |
| `selftest_collect_e178.py`, `desktest_ccheck_standin_e178.py` | the collection end to end on E171's relabelled session | E171's committed passes and check of C |
| `dry_intel_e178.sh` | the Intel dry pass with stand-in ssh, rsync and scp | `dry_intel_e171.sh` |
| `selftest_watcher_e178.py` | the watcher against run_hpl's race | `selftest_watcher_e171.py` |
| `rb/` | steps 2, 3, 7, 8, 10, 11, 20, 22, the dry listing, the desk test | the k6 runbook (v3 drivers) |
| `logs/` | every check above, and the four audits | |
| `SHA256SUMS-e178-kit` | the kit's files, its logs and the unchanged files it calls | |

## Open items (for the verifier, the readiness critic and the records)

1. A verifier of this commit, then a readiness critic. The critic quotes each rule's power at the kept n (A1-4). Card time only on his go.
2. Dated note M1 (the mordast forecast's sha256), before any E178 datum, or that forecast is not scored.
3. A one-line dated note on the SIZE words (above): E178.md section 5 and A1-1 use FAIL HIGH / FAIL LOW for opposite sides. The scorer
   follows E178.md's definition and prints the direction in words.
4. The card-1 fallback's box kit (E172's form), only if aifoundry3 is held on the day.
5. If the anatomy (section 43) needs readings E178 does not take, a dated amendment before any datum.

## Compute

All on the Intel through the round's local slot (`slot.sh`), one job at a time, at nice 10:
- the kit and harness makers, the item and order checks, the watcher test and the tile re-make (seconds each);
- the dry pass (about a minute, two runs, the second into `logs/` at 22:57:45-22:58:51 PST);
- the scorer's self-test (about 45 s, one core, two runs, the second at 22:59:01-22:59:51);
- the collection test (about 30 s, its reduction on one core and its stand-in check of C, four runs);
- the runbook's desk test (about 20 s, two runs) and its dry listing.

The four audits and sub-second reads ran outside the slot. No bench job, mini, lab box or card was used. The collection test wrote under
the lab clone's `build/`, which git ignores, and removed what it wrote.

SPDX-License-Identifier: Apache-2.0
