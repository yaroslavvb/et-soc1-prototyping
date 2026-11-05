# E176 (Q143(k)): M11's heat-over-minutes holds on aifoundry3 card 0 - the run kit, from E166's

*Desk preparation, Thu 5 Nov 2026 (week 45), on the Intel: no card, no device command, no ssh to a lab box, no post in the lab's channel,
no Modal, no archive. Nothing here has touched a card. It is step 1 of [`../m11/REGISTRATION.md`](../m11/REGISTRATION.md) section 13 ("the
kits ... aifoundry3's from E166's ... each with dmcmd_audit GO, a dry pass on the Intel and the parent's stop tests in its smoke"), as
amended by A1-A4, for the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**items 9 and 8** (heat over minutes; the heat path between sessions). The owner's go of 5 Nov 2026 covers today's registered
experiments once kitted and passed by a readiness check; E176 runs **after pool 8's day (E171-E174) has left aifoundry3, never beside it**.*

## What is registered, and where

| commit | time (PST) | what |
|---|---|---|
| `3c31a91d` | 07:41:57 | M11's registration: the hold design (§ 5), the readings (§ 1, § 3), the rules (§ 6, § 7), the scorer's duties (§ 13) |
| `f49b7ddd` | 08:44:59 | A1: the BOTH path, HM-AG's BOTH form, H_E's plan on an exact grid (P 14.52 °C, peak 68.13 °C at 51.2 °C) |
| `d3d97fe2` | 10:07:42 | A2: HM-CAL, the in-session calibration on H_E and Z |
| `ed24bc6e` | 11:07:48 | A3: HM-CAL's premise and scope, HM-E144 beside it, the pair by name |
| `0b554d25` | 12:16:24 | A4: HM-CAL-I8, the int8 pair (L1, S) read on L2, with its entry route |
| this commit | | the run kit; M11's scorer [`../m11/score_m11.py`](../m11/score_m11.py) with its self-test; this README |

**No rule is added here.** The kit runs § 5's design, and the scorer applies the registered rules through the committed design code's own
functions.

## Results first

- **The scorer's self-test passes** ([`../m11/selftest-score-m11.txt`](../m11/selftest-score-m11.txt), `.json`; about 60 s):
  - all nine of M11's lists check (SHA256SUMS 58, -m11 6, -a1 9, -a2 7, -a3 7, -a4 6, and the three h2 lists 16, 129, 6);
  - M10's committed per-hold e for E154's five and E166's four fitted holds come back within 0.001 °C. R comes back within 0.001 °C for
    eight of the nine. For E154's `K_S`, § 1's window (R3: b = the last process's end) reads 11.785 °C, posthoc.json's convention window
    exactly; M10's 11.792 °C is E154's registered window, whose end moved −1.921 s. That hold is accepted by that recorded difference only;
  - 11 synthetic sessions with known answers, covering A1-4's paths and A2-A4's paths:
    - a common gain carried and the arm replaced;
    - a common level carried and the arm retired;
    - E154's line then E166's, where the sessions differ and A2's calibration enters;
    - § 0.1's case, where HM-E144 REPEATS and A4's calibration enters;
    - no effect, and one session;
    - H_E not scored, the pair reordered, L2 not scored, and L2 run before S ended (each NOT SCORED where registered);
    - a session HM-LG does not count;
  - one committed cell each of A2, A3 and A4, re-made exactly from v2's committed draws through the scorer's own decision code:
    - A2: HM-CAL 99.2 / 0.7 / 0.1, enters 97.1;
    - A3: § 0.1's case, BETTER 37.1, enters 21.6, REPEATS 94.1;
    - A4: I8 BETTER 89.5, enters 59.4, a per-session calibration 81.0;
  - the precedence check by git (a first launch now reads blind; one second before A4's commit reads post hoc).
- **The desk dry pass** ([`logs/dry.txt`](logs/dry.txt), 12:33 PST; `V3_DRY=1 E176_DESK=1` in a scratch copy of the committed tree with these
  files, E97's toy card, no device opened, no ssh):
  - the session script's gates, the hash check (26 repo files as listed; the three box binaries named as box-only), the preflight (GO), the
    smoke and its five stop tests, and the smoke gate. Four stop tests pass. The in-launch board test cannot trip on a toy card whose board
    never rises, so the dry smoke exits 1 and the gate reads NO-GO, as E154's and E166's dry passes did;
  - the gates refuse before any device: no gates set (exit 8), T0 + 76 minutes past the end gate (exit 8), `E176_DESK` without `V3_DRY` (exit 2);
  - the measured pass through the block, the full design: **73.5 minutes of plan**. H_E ran 80 launches at 7.56 s start to start; Z, L1, S
    and L2 ran 85 each. The order by first launch is H_E, Z, L1, S, L2: the pair first, and L1 and S ended before L2, as A2-7, A3-9 and A4-8
    require;
  - at a 53.4 °C room G0 ends the pass with **exit 7** and block status "gate", no hold run; at 52.5 °C H_E runs the warm pattern (2.60 s
    every 7.98 s, 75 launches);
  - a looser stop line (a 70 W hold line) and `E176_DRY_ROOM_C` without `--dry` are refused; the runner's `--list` checks the four E78 tiles
    against kinds.json (no problem).
- **Device commands** ([`dmcmd-audit.txt`](dmcmd-audit.txt), [`dmcmd-audit.md`](dmcmd-audit.md)): `dmcmd_audit.py` through `preflight_e176.sh`
  reads **GO, 38 send sites, 0 disallowed, no WRITE allowed**, with E144's table and E154's one reviewed exception (lib.sh:154, never
  called). Every command is a READ: the two PMIC voltage-register reads the owner allowed on 2 November 2026; no statistics reset, no
  firmware-revisions query, no set of any kind. Against the stock table with no exception
  ([`dmcmd-audit-bare.txt`](dmcmd-audit-bare.txt)) it reads NO-GO at exactly E154's and E166's two sites: command 74, which is UNCLASSIFIED
  there, and lib.sh:154.

## The run kit (E166's, ported)

| file | from E166's (`c75bc460`) | what changed |
|---|---|---|
| [`run_e176.py`](run_e176.py) | `run_e166.py` | § 5's design (R0 5, H_E 10, R1 6, Z 10, R2 2, L1 10, R3 6, S 10, R4 2, L2 10, R5 2.5 min); H_E is E144's H_H pattern (`--seconds 3.20` every 7.56 s at a room ≤ 51.5 °C, `--seconds 2.60` every 7.98 s in (51.5, 53.0] °C); the four items are E78's (`fp32.randn`, `fp32.zeros`, `int8.full`, `int8.neg_ones`), checked against kinds.json; no K_OL, room table or pool-6 tile; the smoke runs each hold once (H_E 11 s, two dispatches) with the five stop tests on H_E's tile; the dry-only room override `E176_DRY_ROOM_C` |
| [`block_e176.sh`](block_e176.sh) | `block_e166.sh` | the runner; `gen.sha256` over kinds.json and the four E78 tiles; `E176_DESK=1` (dry only) |
| [`session_e176.sh`](session_e176.sh) | `session_e166.sh` | E176's names; the 76-card-minute budget from T0 with no subset, as E166's; passes 17601 (smoke) and 17620 |
| [`smoke_gate_e176.py`](smoke_gate_e176.py) | `smoke_gate_e166.py` | the five holds (H_E with two launches); E166's checks unchanged |
| [`preflight_e176.sh`](preflight_e176.sh) | `preflight_e166.sh` | E176's session files in E166's list |
| [`frozen-e176.sha256`](frozen-e176.sha256) | `frozen-e166.sha256` | 29 files: E176's five card files, the reused chain, the four E78 tiles, the C-check files, the audit, the host source and the three box binaries; the 20 it shares with E166's list (the box binaries among them) are byte-identical to it |
| [`collect_e176.sh`](collect_e176.sh) | `collect_e166.sh` | E176's names; `ccheck/` emptied first (an earlier try's check is never read as this one's); M11's scorer, with any earlier M11 session's pass dir named after the data directory |

**Kept from E166, unchanged:** the stops, on live samples, tested in the smoke: no launch at a firmware reading ≥ 70 °C; a hold ends at any
sample ≥ 72 °C (firmware or the 34-sensor mean) or a board reading ≥ 65 W; the pass ends at ≥ 74 °C. Also kept:
- E97's guards: a stale sampler, another user on the card, a clock off 600 MHz in 5 samples, three failed launches;
- G0: R0's room ≤ 53.0 °C, else no hold, exit 7;
- the check of C on every launch (Q139(k)'s wrapper with the C-logging host);
- E89's 10 Hz 34-sensor sampler, and the card lock;
- `timeout 10` on every device process, and the two config reads through E128's guard.

The runner refuses a looser line. **H_E's planned in-launch peak** is 68.13 °C at a 51.2 °C room and 68.51 °C at 51.5 °C (A1-2; 34-sensor
mean), 3.5 °C or more under the hold line; every other hold peaks at or under 64.65 °C at 53.0 °C.

## Card-minutes, the order, and the box steps

- **Card-minutes: about 75** = 73.5 of plan + about 1.5 for the smoke and its stop tests, counted from the session-start config read to the
  session-end one, **inside the registered 76-card-minute cap**. The session enforces that cap: it starts only if T0 + 76 min is at or before
  the end gate, and its measured pass's deadline is T0 + 75 min. A hold does not start with less than its length + 30 s left, and R5 is cut
  at the deadline. **Disclosed:** the registration's 73.3 minutes of plan count whole dispatch cycles (79 of H_E's 7.56 s periods in a
  10-minute hold). The runner holds each hold 600 s as E166's did, so its plan reads 73.5 minutes and the session about 75, against the
  registered 74.7.
- **The order on aifoundry3:** after E171 (pool 8's aifoundry3 run) has ended and been collected, on a rested card (G0: the room ≤ 53.0 °C;
  the cool pattern ≤ 51.5 °C). After E171, rest at least about 40 minutes first (E154's room read 51.41 °C 41 minutes after E153). Never
  beside E171-E174 on this card, and never on their claims, locks, queues, build directories or post clauses. **The second session runs on
  another day** (§ 12).
- **The box steps** (wrapped by the bounded runbook, the next commit, `tools/claims-v3/q143k-runbook/`):
  1. the day's one post with this card's clause (section 15's rules);
  2. sync this kit and its unchanged reused files into `aifoundry3:aifoundry/` from the pushed commit;
  3. on the box: `sha256sum -c tools/claims-v3/e176/frozen-e176.sha256` (29, the binaries included), `bash
     tools/claims-v3/e176/preflight_e176.sh` (GO), `et-who`, `et-lab-manifest`, and `ettelem config` through the guard (TDP 0 W, threshold
     65 °C, 600 MHz);
  4. a dry pass on the box: `V3_DRY=1 E176_T0=… E176_LATEST_START=… E176_END_GATE=… bash tools/claims-v3/e176/session_e176.sh` (its dry smoke
     ends 1 on the toy card, as expected);
  5. the session, detached: `E176_T0=$(date +%s) E176_LATEST_START='…' E176_END_GATE='…' setsid nohup bash
     tools/claims-v3/e176/session_e176.sh > build/e176/session.out 2>&1 < /dev/null &` (the end gate leaves 76 minutes after T0);
  6. on the Intel: `bash tools/claims-v3/e176/collect_e176.sh docs/reports/data/<date>-e176-m11-holds-aifoundry3` (the check of C and M11's
     scorer).

  A later try after G0 stopped a session first moves the earlier smoke aside (`p17601` → `p17601.try1`), as E166's dated note says.

## What each rule answers, and with what power (registered; nothing is measured here)

**Today's one session (k = 1).** Nothing enters M11's primary (§ 6: one session). Every reading is reported, labelled "one session", as a
candidate for the next session:
- **HM-LG** at df (1, 3): GAIN 68.6% at a common 3.2% gain, LEVEL 65.2% at 0.27 °C, NOT SEPARATED 93.0% with no effect (A1-7).
- **HM-E144**: does H_E repeat E144's `H_H`, read by the chain to 1.5%? REPEATS in about 94% of draws if § 0.1's case holds, 0.0% on the
  likeliest pattern if A2's premise holds (A3-5). **This is the reading that says which pair carries heat over minutes on this card.**
- **HM-HE**: does H_E depart from the other holds' line (exact t, 4.30265 at 2 df)? It is weak in one session (A1-7: 21.5-23.3% for a
  0.3 °C hold-specific miss).
- **HM-CAL (A2)**: the H_E and Z line read on L1, S and L2, at τ = 0.0884 / √3 = 0.051 °C. BETTER in 92.0-99.7% under the committed
  patterns if the premise holds (A2-5); its calibrated rms near 0.097 °C.
- **HM-CAL-I8 (A4)**: the L1 and S line read on L2, at τ = 0.0884 °C. BETTER in 79.6% on the likeliest pattern under either premise, and in
  3.1% with no effect. Its calibrated L2 miss is near 0.076 °C, against 0.251 °C unscaled (A4-7).

**With the second session (k = 2, another day):**
- HM-LG reads GAIN at 88.5% (a common 3.2% gain) and LEVEL at 89.4% (0.27 °C); HM-AG and S7-W are read;
- § 6's entry rules carry a common term if the sessions share one;
- otherwise A2's calibration enters at 97.1% if the premise holds, or a per-session calibration (A2's or A4's) enters at **81.0%** in
  § 0.1's case. The blind per-session error is then about 0.104 °C (A2) or 0.095 °C over the two L2 holds (A4), against the chain unscaled's
  0.27-0.28 °C.

## E177 (aifoundry2): not built in this lane

M11's registration makes aifoundry2 optional and recommends no card time there: HM-LG-A2 reads 29% (two sessions), 51% with four.
`score_e167.read_hold` is tied to E167's own holds and frozen predictions, so E177 needs an aifoundry2 reader of its own. Its masked hold
(shires `0x11111111`) also needs the check of C to be shown to cover a masked launch, else Z_m and Z_m2 drop (§ 5). **Not done here.** M11's
scorer refuses an aifoundry2 pass (`--a2`). What remains for E177 is in the lane's result.

## What this does to predicting power and heat

Nothing yet: no frozen prediction changes, and no out-of-sample error moves until E176 runs. E176 then gives the first per-session reading
of heat over minutes on aifoundry3. HM-E144 says whether the chain reads H_E as it read E144's `H_H`. HM-CAL and HM-CAL-I8 each give a blind
error for the session's later holds, given the watts: if the premise holds, about 0.10 °C, against 0.27-0.28 °C for the chain unscaled. All
of it is "one session": nothing enters until the second session.

## Compute

The Intel, through the round's local slot, one job at a time on one core:
- the scorer's self-test, three runs (12:22:23-12:23:19, which found the E154 window difference; 12:24:20-12:25:19; and the committed run,
  12:25:33-12:26:34, byte-identical to the second);
- the kit's audits and the desk dry pass (12:33:28-12:33:52), in a 45 MB scratch mirror made by `git archive`.

No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0
