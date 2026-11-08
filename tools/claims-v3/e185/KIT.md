# E185: M11's session 3 on aifoundry3 card 0 (600 MHz pinned), the run kit v5 - E181's kit ported to E185's six holds and E171's stops, with E182's runbook lessons, M11's scorer v5 and an exact copy-back

*Desk preparation, Sat 7 Nov 2026 (week 45), from about 20:42 PST, on the Intel: no card, no device command, no ssh to a lab box, no post in
the lab's channel, no Modal. Nothing here has touched a card. It kits [E185.md](E185.md) (`98fe28b7`), committed before it, under M11's
registration and A1-A10 (A10 `5e708747`). **No E185 datum exists.** Card time waits on the owner's word. For the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8 (heat over minutes).*

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| **DRY-INTEL**, in a tree built from step 7's sync list alone | **PASS, 8 of 8 sections** (A-G and S) | [`logs/dry-intel.txt`](logs/dry-intel.txt) |
| **the runbook's desk test**, stand-in ssh, rsync and pgrep | **SELFTEST-RB-E185 PASS**, 16 of 16 checks over 21 cases (A, K1-K2, P1, O, J1-J2, R1-R3, W1-W3, C1-C4, G1-G2, E1, Z), 97 s | [`rb/logs/selftest-rb.txt`](rb/logs/selftest-rb.txt) |
| **M11's scorer v5 self-test**, on E181's committed data | **14 of 14 PASS** | `../m11/selftest-score-m11-v5.txt` |
| **device commands**, the kit (through `preflight_e185.sh`) | **GO, 38 send sites, 0 disallowed**, the same commands and counts as E181's | [`logs/dmcmd-audit-kit.txt`](logs/dmcmd-audit-kit.txt) |
| **device commands**, the runbook as it runs | **GO, 11 send sites** with E128's guard, every one a READ; bare, NO-GO at exactly step 9's guard call | [`rb/logs/dmcmd-audit.txt`](rb/logs/dmcmd-audit.txt), [`rb/logs/dmcmd-audit-bare.txt`](rb/logs/dmcmd-audit-bare.txt) |
| **the dry listing** | every step exits 0, no ssh or rsync call, the look listed before the day's post | [`rb/logs/dry-listing.txt`](rb/logs/dry-listing.txt) |

**Every device command is a READ:** the two PMIC voltage-register reads the owner allowed on 2 November 2026, through E128's guard. There is
no statistics reset, no firmware-revisions query and no set of any kind (no governor, TDP, threshold or clock). No power cycle, and nothing
that risks one.

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Sat 7 Nov 2026 at about 20:00 PST: public rows H08, H14,
   H19, H24, H25 and H28 (opaque pointers).
2. **Used.**
   - **E181's kit** (`33cdccf6`, with its dated note 1 and runbook v2, `dc35a540`): `run_e181.py`, `block_e181.sh`, `session_e181.sh`,
     `smoke_gate_e181.py`, `preflight_e181.sh`, `collect_e181_v2.sh`, `dry_intel_e181.sh` and its runbook `rb/` (as note 1 runs it), ported
     (the tables below). Its smoke, R0, gates, watcher, C wrapper, sampler, guards, card lock and E97's toy card carry over unchanged.
   - **E182's v4 runbook lessons** (`e0d31903`, `22da6a7b`, with k6's job functions): detached box jobs (E181's runbook already runs its dry
     pass as one; kept), the ours_live and jobs_live refusals (kept, with E182's, E183's, E184's and E185's names), the look before the post
     (kept), every step 2 refusing without the day's window (added), T0-named files (E184's form, `571511d0`), and an exact copy-back (new).
   - **M11's scorer v4** (`dc35a540`), imported unchanged by the new [`../m11/score_m11_v5.py`](../m11/score_m11_v5.py).
   - **E185's registration** (`98fe28b7`): the design, the gains, the rules; `arms_e185.py`, imported unchanged by the scorer v5.
   - **E171's stops** (`4441083f`, E171.md line 95), as E185.md section 8 states them.
   - **E181's committed passes and logs** (`d4e5119d`): the stand-in box of the desk test, and the scorer v5's self-test.
   - *The same quantities, earlier:* the kit's device-command audit against E181's (the same commands and counts: GO 38); the dry pass's plan
     against E185.md's planner (101.0 minutes on the toy's clock against the plan's 100.73, a toy launch's 0.32 s added); the scorer v5's
     readings of E181 against its committed score (equal).
3. **Not used.** Any change to E181's committed files; aifoundry1 or aifoundry2; anything of the NDA tier.
4. **Tiers.** Public tier only. No NDA-tier check is used, so there is no sha256 line.

## The run kit (E181's, ported)

| file | from | what changed |
|---|---|---|
| [`run_e185.py`](run_e185.py) | `run_e181.py` | the six holds in the seed's order (R0 5, H_E 10, rest 8, L1 10, rest 8, L2 10, rest 8, H_E2 10, rest 8, S 10, rest 2, S2 10, rest 2 min); H_E2 runs H_E's pattern; **E171's stops: the hold's line fires at the firmware reading ≥ 70 °C, the 34-sensor mean ≥ 72 °C or the board ≥ 65 W, and the pass ends** (exit 6, nothing retried); a sixth stop test (the 34-sensor-mean line); passes 18501 and 18520; looser lines refused |
| [`block_e185.sh`](block_e185.sh) | `block_e181.sh` | E185's runner and names; exit 6 read as a stop line (block status "stop") |
| [`session_e185.sh`](session_e185.sh) | `session_e181.sh` | **T0-named files** (every file of the session's own in `build/e185/T<T0>/`, a dry session's in `T<T0>-dry/`; a T0 directory that exists refused; `LAST_T0`); **the manifest** (`T<T0>/MANIFEST.sha256`, the session's last act, over the T0 directory and both pass directories); the 105-card-minute budget; exit 6 named |
| [`smoke_gate_e185.py`](smoke_gate_e185.py) | `smoke_gate_e181.py` | the six holds; the six stop tests, all run and all passed |
| [`preflight_e185.sh`](preflight_e185.sh) | `preflight_e181.sh` | E185's files in E181's place |
| [`frozen-e185.sha256`](frozen-e185.sha256) | `frozen-e181.sha256` | 30: E185's five card files, E181's other 22 repo entries and its three box binaries unchanged |
| [`collect_e185.sh`](collect_e185.sh) | `collect_e181_v2.sh` | the T0 directory copied as `logs/`; **the exact copy-back** (every manifest line read back, and nothing else: `COPY-BACK EXACT`, else `DIFFERS`, `EXTRA`, `NO-MANIFEST` or `NO-T0`, exit 4); the host windows picked by T0; **one copy of each C log** (moved into `ccheck/`, E181's data note 1 section 6) |
| [`score_e185.sh`](score_e185.sh) | `score_e181_v2.sh` | M11's scorer v5 on E176, E181 (with its smoke) and E185 (with its smoke and host windows), `--e185` naming E185's pass |
| [`dry_intel_e185.sh`](dry_intel_e185.sh) | `dry_intel_e181.sh` | E185's checks, plus section S: a stricter 34-sensor-mean line ends H_E and the pass |
| [`rb/`](rb/) | `../e181/rb/` (note 1's steps) | every step ported; the changes below |

## The runbook (each step with this card day's `RB_OUT` outside the repo and `RB_LOCK`; exit codes are v3.1's)

| step | file | E185's change |
|---|---|---|
| 1, the window | `rb/s02_window_e185.sh <day> <last start> <last end>` | E185 fits with 105 minutes before the last end |
| 2, the desk check | `rb/s03_desk_e185.sh` | **refuses (10) without a window written today**; HEAD descends from `98fe28b7` and A10; M11's seventeen lists, the footing law's two, E185's registration, kit and runbook lists, the box list's 27 repo entries |
| 3, the look, FIRST | `rb/s05_look_e185.sh aifoundry3 [--wait]` | none (listed before the post) |
| 4, the day's post | (the card lane's, not scripted) | after the look |
| 5-7, sync, preflight, reads | `rb/s07_a3_sync_e185.sh`, `rb/s08_a3_preflight_e185.sh`, `rb/s09_a3_reads_e185.sh` | E185's names |
| 8, the dry pass | `rb/s10_a3_dry_e185.sh start`, then `wait` | one detached job (refused beside a session of ours); the dry session writes only `T<T0>-dry/` (checked, with its manifest) |
| 9, the host's start window | `rb/s12_a3_host_e185.sh start` | epoch-named on the box (`build/e185/host/start-<epoch>.out`) |
| 10, the launch | `rb/s11_a3_launch_e185.sh [--later-try] [--under-an-hour] [--after-noon]` | refused beside a dry job or a session of ours (the guard); **the rest rule reads every log of ours on the card**: `build/e17x` and `e18x/session.log`, E184's `session-*.log` and E185's `T*/session.log`, dry logs skipped; the session's T0 written for step 20 |
| 11, the wait | `rb/s20_wait_e185.sh` | the T0 directory's log; ended only when `MANIFEST.sha256` is written; a stop line named |
| 12, the host's end window | `rb/s12_a3_host_e185.sh end` | epoch-named |
| 13, the release | (not scripted) | |
| 14, the collection | `rb/s22_collect_e185.sh` | E185's lists first; the collector; **16 on any copy-back fault**; the session's gates and stops; the check of C; the launch gate; the scrub in every directory; the desk-path gate; then the score; data in `docs/reports/data/<day>-e185-m11-session3-aifoundry3/` |

A later session of ours on aifoundry3 the same day reads E185's end from `build/e185/T*/session.log` (a rest rule that reads only
`build/e185/session.log` would not see it: the brief must say so).

## Card-minutes, the order, the post (as E185.md section 8 registers them)

- **About 102 card-minutes, cap 105**, enforced from T0 by `session_e185.sh`; the measured pass's deadline T0 + 104 min. About 2.4 h of wall
  time on the box with its steps, then about 15 minutes of collection and score at the desk.
- **aifoundry3 card 0 alone**, never beside another session of ours; launched before 12:00 PST where the day allows (A7-4), at least an hour
  after our last session there (the gate: 40 minutes).
- **The day's one post:** `using aifoundry3 for 2.5 h, until ~HH:MM PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`,
  rewritten under the post's lock with EXPECT_TEXT, after the look; " — released" appended at the last release, every word kept.
- **Stops:** E171's, a stop ending the pass (firmware ≥ 70 °C, 34-sensor mean ≥ 72 °C, board ≥ 65 W); no launch at a firmware reading
  ≥ 70 °C; the session line 74 °C. The smoke tests each line on live samples; on E97's toy card the 34-sensor-mean line and the in-launch board
  line cannot fire (its newest sample carries no codes and its board never rises), so DRY-INTEL's section S tests the first on a toy that
  carries them.

## Open items (for the verifier, the readiness critic and the records)

1. The kit's box steps have run only against stand-ins: the first real sync, preflight and session are the card day's.
2. The collector's exact copy-back assumes the box's `sha256sum` and the desk's reading agree on every byte (they hash the same files);
   `telemetry.jsonl.raw` and `tiles/` are left out on both sides.
3. M11's registered readings at k = 2 (E181 and E185, on A10's reading) are computed by v5; E185.md section 7 forecasts HM-LG NOT SEPARATED in
   97-100% of draws.
4. The card lane's brief for the day (E185 with E183) is the critic's; this kit says only E185's own order and gates.

## Files (`SHA256SUMS-e185-kit`)

Every file of this directory but the registration's (which `SHA256SUMS-e185-registration` pins), and the runbook's own list; M11's scorer v5
has its own list (`../m11/SHA256SUMS-score-m11-v5`).

## Compute

The Intel, through the round's local slot, one job at a time. The committed runs (21:12:51-21:16:11 PST, one job): the scorer v5's self-test
(49 s), DRY-INTEL (50 s), the runbook's desk test (97 s), the dry listing and the audits (seconds). Before them, development runs of each into
the lane's scratch (the dry pass's first run found two faults of its own expectations and one of the session's manifest, fixed before the
committed run). No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0
