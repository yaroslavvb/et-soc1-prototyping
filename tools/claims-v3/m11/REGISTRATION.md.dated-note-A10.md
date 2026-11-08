# M11, dated amendment A10 (Sat 7 Nov 2026, before any E185 datum): A9's arm, the chain over the smoke and the measured pass, becomes M11's registered reading from session 3 on, by a stated rule read on E181's committed score; the x1.032 arm stays reported

*Beside [`REGISTRATION.md`](REGISTRATION.md) (`3c31a91d`) and its amendments A1-A9; it edits none of them. Written on the Intel, desk only (no
card, no lab box, no device command), by the lane e185 of Q155, from about 20:20 PST Sat 7 Nov 2026 until its commit. A9
([`REGISTRATION.md.dated-note-A9.md`](REGISTRATION.md.dated-note-A9.md), `cd5bed77`) registered a REPORTED arm and said "the next M11 session's
registration says whether the arm becomes its reading" (A9-4). E181 (M11's session 2, data `d4e5119d`, fix `efdfe4f8`) read it blind, and
E181's data note 1 § 3 left the x1.032 arm's fate to "the dated amendment owed before session 3's first datum". This is that amendment. M11's
session 3 is E185 (the orchestrator's number); **it is registered after this commit, and no E185 datum exists** (`git log --all` on
`docs/reports/data/*e185*` and `tools/claims-v3/e185`, 20:23 PST: nothing committed; E185's registration files exist only in the lane's working tree). It serves the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **items 9 and 8** (heat over minutes).*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Sat 7 Nov 2026 at about 20:00 PST: public rows H12, H14,
   H19 and H25 (opaque pointers), as A9 read them.
2. **Used.**
   - **A9's rule text** (`cd5bed77`): A9-1's refusals and its identity of the grid and of R, A9-4's expectations ("its sign is fixed by the
     mechanism (positive)"; "Δe on Z, L1, S and L2: expected under 0.001 °C ... A larger Δe there means the arm's grid or input is wrong"),
     and A9-5's expectation for E181's smoke: the registered chain's own account of E176's planned smoke at R0's anchor,
     [`a9-posthoc.json`](a9-posthoc.json) › `sessions` › `E176` › `R0_anchor_window` › `pred_two_less_one_C`, **+0.147 °C**.
   - **E181's committed score** (`docs/reports/data/2026-11-06-e181-m11-session2-aifoundry3/scored-m11.json`, `d4e5119d`, checked against
     that directory's `SHA256SUMS`): `arm_A9` › `sessions` › `S2:p18120` (its `info` and per-hold `delta_e_C` and `R_C`) beside the
     registered `sessions` › `S2:p18120` › `holds`.
   - **E181's data note 1 § 3** (`efdfe4f8`): the x1.032 arm printed "retired" from one session is a candidate, not retired.
   - *The same quantity at the same operating point, earlier:* A9-5's post hoc shifts of each session's first hold by the arm, +0.131 °C
     (E154's H_M) and +0.117 °C (E166's K_S) after a 5-minute R0, +0.021 °C (E144's H_H) after an 8-minute one; E181's is +0.140 °C after
     a 5-minute R0, the same smoke as E176's.
3. **Not used.** Any verdict, rms or HM reading of E181 under either chain: E181's HM-CAL reads BETTER on the arm and NOT RESOLVED on the
   registered reading, and A10-R does not read it. Any E185 datum (none exists). Anything of the NDA tier.
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code. No NDA-tier check is used, so there is no sha256
   line; no NDA-tier piece, name, verdict, ratio or figure is cited.

## A10-1. The rule, A10-R (stated before it was run; E181's arm readings were committed and seen when it was written, disclosed)

A9's arm becomes M11's registered reading for every M11 aifoundry3 session read after this amendment, and the measured-pass-only reading
becomes a reported arm beside it, **if and only if E181's committed arm passes all four of these checks, each one stated in A9 before
E181's first datum**:

| check | what | from |
|---|---|---|
| V1 | the arm read SCORED on E181: the smoke's telemetry there with at least 10 readable samples, the gap between the passes in (0, 600] s | A9-1's refusals |
| V2 | every grid point inside the measured pass the registered reading's own, and R the registered R in every hold | A9-1 |
| V3 | Δe under 0.001 °C in size on every hold after the first, at the committed score's printed precision | A9-4 |
| V4 | Δe on the first hold positive (the mechanism's sign) and within a factor of two of A9-5's expectation: in [+0.074, +0.294] °C | A9-4, A9-5 |

If any one fails, the arm is retired (its grid or its input is wrong) and the registered reading stays. **The rule reads no verdict and no
miss of either chain**: it asks only whether the arm does what A9 said it would, and nothing else. Why adopt it when it passes: A8-6 showed
that the registered reading leaves out heat the session put into the die (the smoke's, still leaving at the first hold's anchor), and the
arm adds exactly that heat, from the committed telemetry, through the same frozen chain, with every other value the registered one.

## A10-2. Its reading on E181 ([`a10_fate.py`](a10_fate.py) → [`a10-fate.json`](a10-fate.json), [`a10-fate.txt`](a10-fate.txt))

| check | E181's committed value | result |
|---|---|---|
| V1 | the arm SCORED; 712 readable smoke samples; the gap 2.517 s | PASS |
| V2 | `measured_points_identical` true; R the registered R in 5 of 5 holds | PASS |
| V3 | Δe 0.000 °C on Z, L1, S and L2 (three decimals) | PASS |
| V4 | Δe(H_E) **+0.140 °C**, inside [+0.074, +0.294] °C (expected +0.147 °C) | PASS |

**A10-R reads ADOPTED.**

## A10-3. What changes from E185 on

- **M11's registered reading on aifoundry3 is A9's arm:** Q138(t)'s frozen chain (as Q139(e) froze it) run over the smoke pass and the
  measured pass together, exactly as A9-1 defines it, with the anchors, windows, Pref, R and every reader the registered ones. Each hold's
  P is R less the arm's e (A9-1's P_2p).
- **Every M11 reading that pools sessions** (HM-LG, HM-AG, S7-W, A1-4's path, A2-3 and A4-3 where their pairs exist, A5's agreement readings)
  reads each aifoundry3 session on this reading, **E181's among them** (its two-pass points, `scored-m11.json` › `arm_A9`). E181's own
  verdicts stay as its README records them: A9-3 governed E181, and A10 changes no E181 reading, verdict or record.
- **The measured-pass-only reading is printed beside**, labelled "reported (A10): the measured pass alone, the reading of E181 and before".
- **When A9-1 refuses on a session** (no smoke telemetry, fewer than 10 readable samples, or a gap outside (0, 600] s), that session is read
  on the measured-pass-only reading, and the record says so. It is not a refusal of the session.
- **No gate, stop, rest rule, design, power figure or card-minute of A1-A9 changes.** G0-A6 with A8-4 reads the residue at R0's window as
  before (the gate reads the die, not a chain), and R0 stays 5 minutes.

## A10-4. The x1.032 arm (E181's data note 1 § 3)

**It is not retired.** E181 read HM-LG at k = 1, and REGISTRATION.md § 6 makes a one-session reading a candidate. From E185 on it is read on
the adopted reading as a reported arm, as A1-4 has it, until HM-LG is read on two or more aifoundry3 sessions; A1-4 then decides its fate
as registered. E185's registration states its own arm B, aifoundry3's board gain fitted on aifoundry3's sessions before E181, beside it. The
x1.032 arm's gamma (both card kinds, M10's) is not refitted.

## A10-5. What does not change

REGISTRATION.md and A1-A9 as committed; every frozen file and hash list; E181's data, README, dated note and score; M11's scorers v1-v4
(E185's kit adds a v5 that reads A10). A record quotes a reading on the measured-pass-only reading only beside the adopted one, labelled.

## Files (`SHA256SUMS-a10`)

This amendment; [`a10_fate.py`](a10_fate.py) (standard library; `/usr/bin/python3 -B tools/claims-v3/m11/a10_fate.py . <out.json> <out.txt>`
from the lab clone's top, under a second); its output [`a10-fate.json`](a10-fate.json) (with the sha256 of the two files it read, each checked
against its committed list) and printout [`a10-fate.txt`](a10-fate.txt).

## Compute

The Intel, one job through the round's local slot (20:23:02-20:23:03 PST), after the rule was written into the script's docstring. No lab box, no
remote host, no card.

SPDX-License-Identifier: Apache-2.0
